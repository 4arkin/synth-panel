"""Compose a panel for one run.

Two constraints do the work, and both exist to protect disagreement:

  at least one skeptic     — a panel that cannot say no has told you nothing when
                             it says yes
  at least two clusters    — five people in the same seat give you one opinion in
                             five voices

Rotation is the third: a persona used in the last runs sits out the next one, so
re-running on a revised draft does not just replay the same reaction back at you.
"""
import json
import os
import random

from . import config, personas as personas_mod

STATE = os.path.join("runs", "rotation.json")


def _load_state(root):
    path = os.path.join(root, STATE)
    if not os.path.exists(path):
        return []
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return []


def _save_state(root, rosters, depth):
    path = os.path.join(root, STATE)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(rosters[-max(depth, 1) * 2:], fh, indent=1)


def compose(pool, size=None, include=(), exclude=(), root=config.ROOT, seed=None,
            record=True):
    """Return (roster, notes). Never raises for a thin pool — it degrades and says so."""
    cfg = config.load(root).get("panel", {})
    rng = random.Random(seed)
    notes = []

    pool = [p for p in pool if p["slug"] not in exclude]
    forced = [p for p in pool if p["slug"] in include]
    unknown = set(include) - {p["slug"] for p in pool}
    if unknown:
        notes.append("not in pool, ignored: {}".format(", ".join(sorted(unknown))))

    if size is None:
        size = rng.choices([3, 4, 5], weights=[20, 50, 30])[0]
    size = max(1, min(int(size), len(pool)))

    recent = set()
    for roster in _load_state(root)[-int(cfg.get("rotation_depth", 2)):]:
        recent.update(roster)

    candidates = [p for p in pool if p not in forced and p["slug"] not in recent]
    if len(candidates) + len(forced) < size:
        notes.append("rotation relaxed — pool too small to exclude recent picks")
        candidates = [p for p in pool if p not in forced]

    roster = list(forced[:size])
    rng.shuffle(candidates)
    for persona in candidates:
        if len(roster) >= size:
            break
        roster.append(persona)

    # Repair the two constraints, in order of how much they cost you if broken.
    if cfg.get("require_skeptic", True) and roster and not any(p["is_skeptic"] for p in roster):
        swap = next((p for p in candidates if p["is_skeptic"] and p not in roster), None)
        if swap:
            drop = next((p for p in reversed(roster) if p not in forced), roster[-1])
            roster[roster.index(drop)] = swap
            notes.append("swapped in a skeptic — a panel that cannot say no proves nothing")
        else:
            notes.append("WARNING: no skeptic in the pool. Read every yes in this run as unearned.")

    min_roles = int(cfg.get("min_distinct_roles", 2))
    if len({p.get("cluster", "?") for p in roster}) < min_roles and len(roster) >= min_roles:
        have = {p.get("cluster", "?") for p in roster}
        swap = next((p for p in candidates if p.get("cluster") not in have and p not in roster), None)
        if swap:
            drop = next((p for p in reversed(roster) if p not in forced), roster[-1])
            roster[roster.index(drop)] = swap
            notes.append("swapped for a second role — one seat gives you one opinion in several voices")
        else:
            notes.append("WARNING: every persona sits in the same role. Their agreement is not evidence.")

    if record and roster:
        rosters = _load_state(root)
        rosters.append([p["slug"] for p in roster])
        _save_state(root, rosters, int(cfg.get("rotation_depth", 2)))
    return roster, notes
