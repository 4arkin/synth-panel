"""Read and validate persona files.

A persona file is a heading, a block of `key: value` lines, and optional prose
below. Deliberately not YAML or JSON: these are files a user edits by hand, often
mid-run, and a missing quote should never cost them the panel.
"""
import glob
import os

from . import config

FIELDS = ("name", "cluster", "role_and_context", "current_situation",
          "current_alternative", "objection_pattern", "skepticism", "signature_phrase")
OPTIONAL = ("grounding", "source")
SKEPTIC_AT = 7


def parse(path):
    persona = {"slug": os.path.splitext(os.path.basename(path))[0], "path": path}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if line.startswith("#") or line.startswith("##"):
                continue
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            key = key.strip()
            if key in FIELDS or key in OPTIONAL:
                persona[key] = value.strip()
    persona.setdefault("grounding", "hypothesis")
    persona.setdefault("source", "none — hypothesis")
    try:
        persona["skepticism"] = int(str(persona.get("skepticism", "5")).split("/")[0])
    except ValueError:
        persona["skepticism"] = 5
    persona["is_skeptic"] = persona["skepticism"] >= SKEPTIC_AT
    persona["missing"] = [f for f in FIELDS if not persona.get(f)]
    return persona


def load_dir(directory):
    return [parse(p) for p in sorted(glob.glob(os.path.join(directory, "*.md")))]


def pool_dir(root=config.ROOT, use_examples=False):
    """The user's own personas, or the worked example when they have none yet."""
    own = os.path.join(root, "personas")
    if not use_examples and glob.glob(os.path.join(own, "*.md")):
        return own, False
    return os.path.join(root, "examples", "personas"), True


def fidelity(personas):
    """Where this panel sits on the ladder. The weakest persona sets the label."""
    if not personas:
        return "no panel"
    if all(p.get("grounding") == "evidence-anchored" for p in personas):
        return "evidence-anchored"
    if any(p.get("grounding") == "evidence-anchored" for p in personas):
        return "hypothesis — grounded, partly evidence-anchored"
    return "hypothesis"
