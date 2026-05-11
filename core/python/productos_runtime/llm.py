"""ProductOS LLM abstraction layer.

Supports multiple backends with automatic fallback:
1. Ollama (local, no API key)
2. OpenAI-compatible endpoints (optional)
3. Deterministic / synthetic (fallback when no LLM available)

All providers expose a unified `generate_structured(prompt, schema)` interface
that returns a JSON object validated against the given JSON schema.
"""

from __future__ import annotations

import json
import os
import urllib.request
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class LLMProvider(ABC):
    """Abstract base for LLM providers."""

    @abstractmethod
    def generate_structured(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a JSON object matching the provided schema."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if this provider is ready to serve requests."""


class DeterministicProvider(LLMProvider):
    """Fallback provider that generates synthetic but schema-valid JSON.

    Uses rule-based population with realistic defaults. Suitable for
    demos, testing, and offline operation. Not intended for production
    qualitative synthesis — but guarantees schema compliance.
    """

    def is_available(self) -> bool:
        return True

    def generate_structured(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Return a synthetic object matching the schema."""
        return _synthesize_from_schema(schema)


class OllamaProvider(LLMProvider):
    """Local Ollama provider. No API key required."""

    DEFAULT_URL = "http://localhost:11434"
    DEFAULT_MODEL = "llama3.2"

    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = base_url or os.environ.get("OLLAMA_HOST", self.DEFAULT_URL)
        self.model = model or os.environ.get("OLLAMA_MODEL", self.DEFAULT_MODEL)

    def is_available(self) -> bool:
        try:
            req = urllib.request.Request(
                f"{self.base_url}/api/tags",
                method="GET",
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                return resp.status == 200
        except Exception:
            return False

    def generate_structured(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = (
            "You are a structured data generator. Respond ONLY with valid JSON "
            "matching the provided schema. Do not include markdown formatting, "
            "explanations, or code fences."
        )
        full_prompt = (
            f"{system_prompt}\n\nSchema:\n{json.dumps(schema, indent=2)}\n\n"
            f"Instructions:\n{prompt}\n\nReturn valid JSON only."
        )
        payload = json.dumps(
            {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False,
                "format": "json",
            }
        ).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = json.loads(resp.read().decode("utf-8"))

        text = raw.get("response", "")
        # Strip markdown fences if present
        text = text.strip()
        if text.startswith("```"):
            lines = text.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            text = "\n".join(lines).strip()
        return json.loads(text)


class OpenAIProvider(LLMProvider):
    """OpenAI-compatible API provider (optional)."""

    DEFAULT_URL = "https://api.openai.com/v1/chat/completions"
    DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(self, api_key: str | None = None, base_url: str | None = None, model: str | None = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = base_url or self.DEFAULT_URL
        self.model = model or self.DEFAULT_MODEL

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate_structured(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        system_prompt = (
            "You are a structured data generator. Respond ONLY with valid JSON "
            "matching the provided schema. Do not include markdown formatting, "
            "explanations, or code fences."
        )
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Schema:\n{json.dumps(schema, indent=2)}\n\nInstructions:\n{prompt}"},
                ],
                "temperature": 0.2,
                "response_format": {"type": "json_object"},
            }
        ).encode("utf-8")

        req = urllib.request.Request(
            self.base_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = json.loads(resp.read().decode("utf-8"))

        text = raw["choices"][0]["message"]["content"]
        return json.loads(text)


def default_provider() -> LLMProvider:
    """Return the best available provider, falling back to deterministic."""
    for provider in (OllamaProvider(), OpenAIProvider(), DeterministicProvider()):
        if provider.is_available():
            return provider
    return DeterministicProvider()


# ---------------------------------------------------------------------------
# Deterministic schema synthesizer
# ---------------------------------------------------------------------------

def _synthesize_from_schema(schema: Dict[str, Any]) -> Any:
    """Recursively synthesize data matching a JSON schema fragment."""
    stype = schema.get("type")
    if stype == "object":
        obj: Dict[str, Any] = {}
        props = schema.get("properties", {})
        required = set(schema.get("required", []))
        for key, subschema in props.items():
            if key in required or subschema.get("type") != "object":
                val = _synthesize_from_schema(subschema)
                if val is not None:
                    obj[key] = val
        return obj
    if stype == "array":
        items = schema.get("items", {})
        min_items = schema.get("minItems", 0)
        arr: List[Any] = []
        for _ in range(max(min_items, 1)):
            arr.append(_synthesize_from_schema(items))
        return arr
    if stype == "string":
        enum = schema.get("enum")
        if enum:
            return enum[0]
        const = schema.get("const")
        if const is not None:
            return const
        default = schema.get("default")
        if default is not None:
            return default
        fmt = schema.get("format", "")
        if "date-time" in fmt:
            from datetime import datetime, timezone
            return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        min_len = schema.get("minLength", 0)
        return " " * max(min_len, 5)
    if stype == "integer":
        minimum = schema.get("minimum", 0)
        maximum = schema.get("maximum", 100)
        return max(minimum, min(maximum, minimum + 1))
    if stype == "number":
        return 0.0
    if stype == "boolean":
        return schema.get("default", False)
    # Fallback for anyOf / oneOf / $ref
    any_of = schema.get("anyOf") or schema.get("oneOf")
    if any_of:
        return _synthesize_from_schema(any_of[0])
    ref = schema.get("$ref")
    if ref and ref.startswith("#"):
        # Local ref within same schema — caller must resolve; here we return empty dict
        return {}
    return None
