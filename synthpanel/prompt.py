"""Assemble one self-contained worker prompt per persona.

Self-contained is the point. The subprocess sees this string and nothing else —
not the repo, not the scenario file, not the other personas, not the
orchestrator's reasoning. Anything the persona needs has to be in here.
"""
import json
import os
import re

from . import config

SLOT = re.compile(r"\{\{(\w+)\}\}")


def scenario(slug, root=config.ROOT):
    """The machine-readable block at the foot of a scenario file."""
    path = os.path.join(root, "scenarios", "{}.md".format(slug))
    if not os.path.exists(path):
        raise FileNotFoundError(
            "No scenario '{}'. Available: {}".format(slug, ", ".join(available(root))))
    with open(path, encoding="utf-8") as fh:
        blocks = re.findall(r"```json\s*(\{.*?\})\s*```", fh.read(), re.DOTALL)
    if not blocks:
        raise ValueError("{} has no machine-readable block".format(path))
    return json.loads(blocks[-1])


def available(root=config.ROOT):
    directory = os.path.join(root, "scenarios")
    return sorted(os.path.splitext(f)[0] for f in os.listdir(directory) if f.endswith(".md"))


def template(root=config.ROOT):
    with open(os.path.join(root, "prompts", "worker.md"), encoding="utf-8") as fh:
        return fh.read().split("\n---\n", 1)[1].lstrip()


def build(persona, spec, stimulus, root=config.ROOT):
    """One persona + one scenario + one stimulus -> one prompt. Raises on an unfilled slot."""
    questions = "\n".join(
        "{}. {} — {}".format(i + 1, axis["key"], axis["question"])
        for i, axis in enumerate(spec["axes"]))
    axes_keys = ", ".join('"{}": "<prose>"'.format(a["key"]) for a in spec["axes"])

    filled = template(root)
    values = dict(persona)
    values.update({
        "stimulus": stimulus,
        "questions": questions,
        "axes_keys": axes_keys,
        "verdict_enum": " | ".join(spec["verdicts"]),
    })
    for key, value in values.items():
        filled = filled.replace("{{%s}}" % key, str(value))

    leftover = sorted(set(SLOT.findall(filled)))
    if leftover:
        raise ValueError(
            "persona '{}' is missing: {}. An unfilled slot reaching a worker is a bug, "
            "not a default.".format(persona.get("slug", "?"), ", ".join(leftover)))
    return filled


def build_all(roster, spec, stimulus, root=config.ROOT):
    return {p["slug"]: build(p, spec, stimulus, root) for p in roster}
