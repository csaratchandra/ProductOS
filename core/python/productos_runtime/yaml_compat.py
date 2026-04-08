from __future__ import annotations

import ast
from typing import Any

try:  # pragma: no cover - exercised implicitly when PyYAML is available
    import yaml as _yaml
except ImportError:  # pragma: no cover - exercised in slimmer runtime environments
    _yaml = None


def _read_text(stream_or_text: Any) -> str:
    if hasattr(stream_or_text, "read"):
        return stream_or_text.read()
    return str(stream_or_text)


def _parse_scalar(raw_value: str) -> Any:
    value = raw_value.strip()
    if not value:
        return ""
    if value in {"null", "Null", "NULL"}:
        return None
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value.startswith(("'", '"')) and value.endswith(("'", '"')):
        return ast.literal_eval(value)
    return value


def safe_load(stream_or_text: Any) -> Any:
    if _yaml is not None:
        return _yaml.safe_load(stream_or_text)

    text = _read_text(stream_or_text)
    if not text.strip():
        return None

    data: dict[str, Any] = {}
    current_key: str | None = None
    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line.startswith("  - "):
            if current_key is None:
                raise ValueError("Encountered list item before any manifest key.")
            data.setdefault(current_key, []).append(_parse_scalar(raw_line[4:]))
            continue
        if ":" not in raw_line:
            raise ValueError(f"Unsupported YAML line: {raw_line}")
        key, raw_value = raw_line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if value:
            data[key] = _parse_scalar(value)
            current_key = None
        else:
            data[key] = []
            current_key = key
    return data


def _format_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def safe_dump(data: Any, stream: Any, *, sort_keys: bool = False) -> None:
    if _yaml is not None:
        _yaml.safe_dump(data, stream, sort_keys=sort_keys)
        return

    if not isinstance(data, dict):
        raise TypeError("yaml_compat.safe_dump expects a dictionary payload.")

    items = data.items()
    if sort_keys:
        items = sorted(items)

    lines: list[str] = []
    for key, value in items:
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {_format_scalar(item)}")
        else:
            lines.append(f"{key}: {_format_scalar(value)}")
    stream.write("\n".join(lines) + "\n")
