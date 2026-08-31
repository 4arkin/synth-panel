"""Config loading. Stdlib only.

Uses `tomllib` (Python 3.11+) when present. Older interpreters fall back to a
minimal reader that covers this project's own schema — sections, strings,
integers, booleans and arrays of strings. It is deliberately not a general TOML
parser; it exists so `python3` means `python3` and not `python3.11+`.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:  # Python 3.11+
    import tomllib

    def _parse(text):
        return tomllib.loads(text)
except ImportError:  # pragma: no cover - exercised only on <3.11
    def _parse(text):
        data, section = {}, None
        for raw in text.splitlines():
            line = raw.split("#", 1)[0].strip() if not raw.strip().startswith("#") else ""
            if not line:
                continue
            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1].strip()
                data[section] = {}
                continue
            if "=" not in line:
                continue
            key, value = (p.strip() for p in line.split("=", 1))
            target = data if section is None else data[section]
            target[key] = _value(value)
        return data

    def _value(v):
        if v.startswith("[") and v.endswith("]"):
            inner = v[1:-1].strip()
            if not inner:
                return []
            return [_value(p.strip()) for p in re.split(r",(?![^\[]*\])", inner) if p.strip()]
        if v.lower() in ("true", "false"):
            return v.lower() == "true"
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            return v[1:-1]
        try:
            return int(v)
        except ValueError:
            return v


def _read(path):
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        return _parse(fh.read())


def _merge(base, overlay):
    out = dict(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


def load(root=ROOT):
    """config.toml, overlaid by config.local.toml when it exists."""
    return _merge(_read(os.path.join(root, "config.toml")),
                  _read(os.path.join(root, "config.local.toml")))


def registry(root=ROOT):
    """The known-agent-CLI registry from agents.toml."""
    return _read(os.path.join(root, "agents.toml"))
