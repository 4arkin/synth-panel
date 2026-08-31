"""Self-install: find the agent CLIs on PATH and write the file each one reads.

Every agent CLI bootstraps from a different filename. Rather than ask the user
which one they have, look, then write a small pointer into each — so whichever
agent they open the repo with finds AGENTS.md on its own.
"""
import os
import shutil

from . import config

BEGIN = "<!-- BEGIN synth-panel -->"
END = "<!-- END synth-panel -->"

POINTER = """{begin}
# synth-panel

This repository is a synthetic buyer panel. Before doing anything a user asks of
it, read `AGENTS.md` in the repository root and follow it literally. The four
rules in `docs/rules.md` are absolute — they are the difference between a useful
reading and confident nonsense.
{end}"""


def available(root=config.ROOT):
    """Registry entries whose executable is on PATH."""
    found = {}
    for name, entry in config.registry(root).items():
        command = entry.get("command") or []
        if command and shutil.which(command[0]):
            found[name] = entry
    return found


def _write_pointer(path):
    block = POINTER.format(begin=BEGIN, end=END)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(block + "\n")
        return "created"
    with open(path, encoding="utf-8") as fh:
        existing = fh.read()
    if BEGIN in existing and END in existing:
        head, rest = existing.split(BEGIN, 1)
        _, tail = rest.split(END, 1)
        updated = head + block + tail
        if updated == existing:
            return "unchanged"
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(updated)
        return "updated"
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("\n" + block + "\n")
    return "appended"


def install(root=config.ROOT, write_config=True):
    """Write each found CLI's entrypoint file and record a dispatch command.

    Returns (results, chosen) where chosen is the CLI written into
    config.local.toml, or None when nothing was found.
    """
    found = available(root)
    results = []
    for name, entry in sorted(found.items()):
        entrypoint = entry.get("entrypoint")
        action = _write_pointer(os.path.join(root, entrypoint)) if entrypoint else "skipped"
        results.append({
            "cli": name,
            "entrypoint": entrypoint,
            "action": action,
            "verified": bool(entry.get("verified")),
            "command": entry.get("command", []),
        })

    chosen = None
    for candidate in results:  # prefer a CLI whose invocation this project has run
        if candidate["verified"]:
            chosen = candidate
            break
    if chosen is None and results:
        chosen = results[0]

    if chosen and write_config:
        _write_dispatch(root, chosen["command"])
    return results, chosen


def _write_dispatch(root, command):
    """Record the dispatch command in config.local.toml, leaving config.toml alone."""
    path = os.path.join(root, "config.local.toml")
    rendered = "[dispatch]\ncommand = [{}]\n".format(
        ", ".join('"{}"'.format(part) for part in command))
    existing = ""
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            existing = fh.read()
    if "[dispatch]" in existing:
        # Replace only the dispatch section; anything else the user wrote survives.
        lines, out, skipping = existing.splitlines(), [], False
        for line in lines:
            if line.strip() == "[dispatch]":
                skipping = True
                continue
            if skipping and line.strip().startswith("["):
                skipping = False
            if skipping and line.strip().startswith("command"):
                continue
            out.append(line)
        existing = "\n".join(out).strip() + "\n"
    with open(path, "w", encoding="utf-8") as fh:
        fh.write((existing + "\n" if existing.strip() else "") + rendered)
