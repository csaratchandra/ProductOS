"""ProductOS V13 Code Analysis: Structural code repository analysis with AST parsing and git history intelligence."""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .llm import LLMProvider, default_provider


CODE_UNDERSTANDING_SCHEMA = "code_understanding.schema.json"

ROOT = Path(__file__).resolve().parents[3]


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def analyze_code_repository(
    repo_path: Path,
    *,
    llm: LLMProvider | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    """Analyze a code repository and produce code_understanding.json.

    Performs:
    - Module/directory structure extraction
    - API endpoint detection (Flask/FastAPI route decorators, OpenAPI specs)
    - Feature flag detection
    - Git history analysis (change velocity, staleness)
    - Dependency graph inference
    """
    provider = llm or default_provider()
    generated_at = generated_at or _now_iso()

    module_graph = _extract_module_graph(repo_path)
    api_surface = _extract_api_surface(repo_path)
    feature_flags = _extract_feature_flags(repo_path)
    change_velocity = _analyze_git_history(repo_path)

    evidence_confidence = _compute_evidence_confidence(module_graph, api_surface, feature_flags)

    return {
        "schema_version": "1.0.0",
        "code_understanding_id": f"cu_{repo_path.name}_{generated_at[:10]}",
        "source_repo_path": str(repo_path.resolve()),
        "workspace_id": "",
        "title": f"Code Understanding: {repo_path.name}",
        "module_graph": module_graph,
        "api_surface": api_surface,
        "feature_flags": feature_flags,
        "change_velocity": change_velocity,
        "evidence_confidence": evidence_confidence,
        "generated_at": generated_at,
    }


def _extract_module_graph(repo_path: Path) -> list[dict[str, Any]]:
    """Extract module/directory structure from the repo."""
    modules: list[dict[str, Any]] = []
    python_dirs = set()

    for f in sorted(repo_path.rglob("*.py")):
        if ".git" in f.parts or "__pycache__" in f.parts:
            continue
        rel = f.relative_to(repo_path)
        module_name = rel.stem
        module_path = str(rel)

        imports = _extract_python_imports(f)
        parent_dir = rel.parent.as_posix()
        python_dirs.add(parent_dir)

        modules.append({
            "module_name": module_name,
            "module_path": module_path,
            "purpose": _infer_module_purpose(module_name, module_path, imports),
            "dependencies": [imp for imp in imports if not imp.startswith("_")],
            "change_frequency": "moderate",
            "confidence": "observed",
            "last_modified": _now_iso(),
        })

    if not modules:
        modules.append({
            "module_name": repo_path.name,
            "module_path": ".",
            "purpose": f"Root directory of {repo_path.name}",
            "dependencies": [],
            "change_frequency": "moderate",
            "confidence": "inferred",
            "last_modified": _now_iso(),
        })
    return modules


def _extract_python_imports(filepath: Path) -> list[str]:
    """Extract import statements from a Python file."""
    imports: list[str] = []
    try:
        text = filepath.read_text(encoding="utf-8", errors="ignore")
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("import "):
                parts = line[7:].split()
                if parts:
                    imports.append(parts[0].split(".")[0])
            elif line.startswith("from "):
                parts = line[5:].split()
                if len(parts) >= 1:
                    imports.append(parts[0].split(".")[0])
    except Exception:
        pass
    return imports


def _infer_module_purpose(module_name: str, module_path: str, imports: list[str]) -> str:
    """Infer the purpose of a module from its name, path, and imports."""
    name_lower = module_name.lower()

    purpose_map = {
        "test": "Test suite",
        "__init__": "Package initialization and re-exports",
        "schema": "Data schema definitions",
        "model": "Data models",
        "view": "View/presentation logic",
        "controller": "Request handling and control flow",
        "route": "API route definitions",
        "util": "Utility and helper functions",
        "config": "Configuration management",
        "cli": "Command-line interface",
        "adapter": "External system adapter",
        "service": "Business logic service layer",
        "middleware": "HTTP middleware layer",
    }

    for key, purpose in purpose_map.items():
        if key in name_lower:
            return purpose

    if "api" in name_lower or "route" in name_lower:
        return "API endpoint definitions"
    if "db" in name_lower or "store" in name_lower:
        return "Data storage and retrieval"
    if "convert" in name_lower or "transform" in name_lower:
        return "Data transformation layer"

    return f"Module: {module_name}"


def _extract_api_surface(repo_path: Path) -> list[dict[str, Any]]:
    """Extract API endpoints from Flask/FastAPI route decorators and OpenAPI specs."""
    endpoints: list[dict[str, Any]] = []
    http_methods = {"get", "post", "put", "patch", "delete", "head", "options"}
    route_pattern = re.compile(
        r'@(?:app|router|blueprint|api)\.(route|get|post|put|patch|delete)\(\s*["\']([^"\']+)["\']',
        re.IGNORECASE,
    )
    openapi_path_pattern = re.compile(r'"(/?\w+(?:/\{\w+\})*)"\s*:\s*\{')
    openapi_method_pattern = re.compile(r'"(get|post|put|patch|delete|head|options)"\s*:')

    for f in sorted(repo_path.rglob("*")):
        if ".git" in f.parts or "__pycache__" in f.parts:
            continue
        if not f.is_file():
            continue
        suffix = f.suffix.lower()
        if suffix not in {".py", ".yaml", ".yml", ".json"}:
            continue

        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        if suffix == ".py":
            for match in route_pattern.finditer(text):
                method = match.group(1).lower()
                path = match.group(2)
                if method in http_methods:
                    endpoints.append({
                        "method": method.upper(),
                        "path": path,
                        "inferred_feature": _infer_feature_from_route(path, f),
                        "auth_scope": "unknown",
                        "linked_personas": [],
                        "confidence": "observed",
                    })
                elif method == "route":
                    endpoints.append({
                        "method": "GET",
                        "path": path,
                        "inferred_feature": _infer_feature_from_route(path, f),
                        "auth_scope": "unknown",
                        "linked_personas": [],
                        "confidence": "observed",
                    })

        if suffix in {".yaml", ".yml", ".json"}:
            paths = openapi_path_pattern.findall(text)
            methods = openapi_method_pattern.findall(text)
            if paths:
                for path in paths:
                    for m in methods:
                        endpoints.append({
                            "method": m.upper(),
                            "path": path,
                            "inferred_feature": _infer_feature_from_route(path, f),
                            "auth_scope": "unknown",
                            "linked_personas": [],
                            "confidence": "observed" if methods else "inferred",
                        })

    return endpoints


def _infer_feature_from_route(path: str, source_file: Path) -> str:
    """Infer what feature an API route belongs to based on path and file location."""
    parts = [p for p in path.split("/") if p and not p.startswith("{")]
    if parts:
        return parts[0].replace("-", "_").replace("_", " ").title()
    return source_file.stem.replace("_", " ").title()


def _extract_feature_flags(repo_path: Path) -> list[dict[str, Any]]:
    """Detect feature flags in the codebase."""
    flags: list[dict[str, Any]] = []
    flag_patterns = [
        re.compile(r'feature_flags?\s*\[?\s*["\'](\w+)["\']'),
        re.compile(r'is_feature_enabled\s*\(\s*["\'](\w+)["\']'),
        re.compile(r'FLAG_(\w+)'),
        re.compile(r'feature_flag\s*=\s*["\'](\w+)["\']'),
    ]

    seen_flags: set[str] = set()
    for f in sorted(repo_path.rglob("*.py")):
        if ".git" in f.parts or "__pycache__" in f.parts:
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        for pattern in flag_patterns:
            for match in pattern.finditer(text):
                flag_name = match.group(1)
                if flag_name not in seen_flags:
                    seen_flags.add(flag_name)
                    flags.append({
                        "flag_name": flag_name,
                        "location": str(f.relative_to(repo_path)),
                        "inferred_feature": _slug_to_title(flag_name),
                        "active_state": "unknown",
                        "confidence": "inferred",
                    })

    return flags


def _slug_to_title(slug: str) -> str:
    return slug.replace("_", " ").replace("-", " ").title()


def _analyze_git_history(repo_path: Path) -> dict[str, Any]:
    """Analyze git history to determine change velocity per module."""
    module_velocity: list[dict[str, Any]] = []

    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--since=6 months ago", "--format=format: %H"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        total_commits_6mo = len([l for l in result.stdout.splitlines() if l.strip()])

        log_output = subprocess.run(
            ["git", "log", "--oneline", "--since=6 months ago", "--name-only", "--format=format:COMMIT"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=60,
        )

        file_commit_counts: dict[str, int] = {}
        current_commit_files: set[str] = set()
        for line in log_output.stdout.splitlines():
            line = line.strip()
            if line == "COMMIT":
                for f in current_commit_files:
                    file_commit_counts[f] = file_commit_counts.get(f, 0) + 1
                current_commit_files = set()
            elif line:
                current_commit_files.add(line)

        for f in sorted(repo_path.rglob("*.py")):
            if ".git" in f.parts or "__pycache__" in f.parts:
                continue
            rel = str(f.relative_to(repo_path))
            commits = file_commit_counts.get(rel, 0)
            commits_per_month = round(commits / 6, 1) if total_commits_6mo > 0 else 0

            if commits_per_month >= 5:
                staleness = "active"
            elif commits_per_month >= 1:
                staleness = "normal"
            elif commits_per_month > 0:
                staleness = "stale"
            else:
                staleness = "archived"

            module_velocity.append({
                "module_name": f.stem,
                "commits_per_month": commits_per_month,
                "active_contributors": max(1, commits_per_month // 2),
                "staleness_score": staleness,
                "last_modified": _now_iso(),
            })

    except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
        pass

    if not module_velocity:
        module_velocity.append({
            "module_name": repo_path.name,
            "commits_per_month": 0,
            "active_contributors": 0,
            "staleness_score": "archived",
            "last_modified": _now_iso(),
        })

    return {
        "module_velocity": module_velocity,
        "overall_summary": f"Analyzed {len(module_velocity)} modules across {repo_path.name}",
    }


def _compute_evidence_confidence(
    module_graph: list[dict[str, Any]],
    api_surface: list[dict[str, Any]],
    feature_flags: list[dict[str, Any]],
) -> dict[str, Any]:
    observed = sum(1 for m in module_graph if m.get("confidence") == "observed")
    inferred = sum(1 for m in module_graph if m.get("confidence") == "inferred") + len(api_surface) + len(feature_flags)
    uncertain = sum(1 for m in module_graph if m.get("confidence") == "uncertain")
    return {
        "summary": f"Code analysis: {observed} observed modules, {inferred} inferred items, {uncertain} uncertain",
        "observed_count": observed,
        "inferred_count": inferred,
        "uncertain_count": uncertain,
    }
