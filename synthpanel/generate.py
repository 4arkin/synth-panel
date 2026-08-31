"""Generate reference statements for a stimulus.

The shipped sets are written for somebody else's material and were measured
failing to transfer. This writes a set in YOUR stimulus's vocabulary instead,
which is what the wording law actually asks for.

A generated set is UNCHECKED like any other. Generating it well and checking it
are different jobs, and only `tools/validate.py` does the second one.
"""
import datetime
import hashlib
import json
import os
import re

from . import config, dispatch

CACHE = os.path.join("reference-statements", "generated")
TEMPLATE = os.path.join("prompts", "reference-statements.md")


def fingerprint(scenario, stimulus):
    """Same scenario + same stimulus = same set, so validation is not re-paid."""
    digest = hashlib.sha256((scenario + "\0" + stimulus.strip()).encode()).hexdigest()
    return "{}-{}".format(scenario, digest[:12])


def cache_path(scenario, stimulus, root=config.ROOT):
    return os.path.join(root, CACHE, fingerprint(scenario, stimulus) + ".json")


def _template(root):
    with open(os.path.join(root, TEMPLATE), encoding="utf-8") as fh:
        return fh.read().split("\n---\n", 1)[1].lstrip()


def check_shape(statements):
    """Reject a set that cannot work before it costs anyone a validation run."""
    problems = []
    if not isinstance(statements, list) or len(statements) != 5:
        return ["not five statements"]
    if any(not isinstance(s, str) or not s.strip() for s in statements):
        return ["one or more statements are empty"]
    lengths = [len(s.split()) for s in statements]
    # The measured failure is a negative end that is shorter and vaguer than the
    # positive end, which makes every on-topic answer drift high.
    if max(lengths) > 2.5 * min(lengths):
        problems.append(
            "lopsided: {} words at the shortest, {} at the longest. All five must "
            "carry the same weight or skeptics score as enthusiasts".format(
                min(lengths), max(lengths)))
    if len({s.strip().lower() for s in statements}) < 5:
        problems.append("two statements are identical")
    return problems


def build_prompts(spec, stimulus, root=config.ROOT):
    template = _template(root)
    prompts = {}
    for axis in spec["axes"]:
        if not axis["rated"]:
            continue
        prompts[axis["key"]] = (template
                                .replace("{{stimulus}}", stimulus)
                                .replace("{{question}}", axis["question"]))
    return prompts


def generate(spec, stimulus, root=config.ROOT):
    """Returns (references, report). Never writes a set that fails its shape check."""
    cfg = config.load(root)
    prompts = build_prompts(spec, stimulus, root)
    if not prompts:
        return None, ["scenario '{}' rates nothing".format(spec["scenario"])]

    results = dispatch.run_all(
        cfg["dispatch"]["command"], prompts,
        max_parallel=cfg["dispatch"].get("max_parallel", 5),
        timeout=cfg["dispatch"].get("timeout_seconds", 420),
        prompt_via=cfg["dispatch"].get("prompt_via", "stdin"))

    references, report = {}, []
    for axis, result in sorted(results.items()):
        parsed = dispatch.extract_json(result["stdout"]) or {}
        statements = parsed.get("statements")
        problems = check_shape(statements)
        if problems:
            report.append("{}: {}".format(axis, "; ".join(problems)))
            continue
        references[axis] = [s.strip() for s in statements]
        report.append("{}: written around {!r}".format(
            axis, (parsed.get("shared_vocabulary") or "")[:60]))
    return (references or None), report


def save(scenario, stimulus, references, root=config.ROOT):
    path = cache_path(scenario, stimulus, root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = dict(references)
    payload["_provenance"] = (
        "GENERATED for one specific stimulus, and UNCHECKED. Written in that stimulus's own "
        "vocabulary, which is what the wording law asks for and what the shipped sets could not "
        "do for material they were not written for. Generating a set and checking one are "
        "different jobs: run tools/validate.py on it before any distribution from it means "
        "anything. Regenerated automatically if the stimulus changes.")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, indent=1, ensure_ascii=False) + "\n")
    return path


def load(scenario, stimulus, root=config.ROOT):
    path = cache_path(scenario, stimulus, root)
    if not os.path.exists(path):
        return None, path
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    return {k: v for k, v in data.items() if not k.startswith("_")}, path


def checked(scenario, stimulus, root=config.ROOT):
    """The gate result this set recorded about itself, or None.

    Written by tools/validate.py, never by hand and never by the thing being
    measured. A set is scorable only if this says two runs cleared the gate.
    """
    path = cache_path(scenario, stimulus, root)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh).get("_checked")


def record_gate(scenario, stimulus, rhos, gate, root=config.ROOT):
    """Stamp a set with what the gate measured. Passing needs two clear runs."""
    path = cache_path(scenario, stimulus, root)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    clean = [r for r in rhos if r is not None and r >= gate]
    data["_checked"] = {
        "passed": len(clean) >= 2 and len(clean) == len(rhos),
        "runs": [None if r is None else round(r, 3) for r in rhos],
        "gate": gate,
        "checked_at": datetime.date.today().isoformat(),
    }
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
    return data["_checked"]
