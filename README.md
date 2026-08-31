# synth-panel

**A synthetic buyer panel that argues with your work before the market does.**

> The public README is written and waiting on a copy pass; it ships verbatim in place of this note.
> Meanwhile the repo is complete and runs: start at [`docs/quickstart.md`](docs/quickstart.md).

**No API key needed.** Personas run through the agent CLI you are already logged into. One optional
feature — turning their answers into 1–5 distributions — needs an embedding provider, and without it you
still get verdicts, objections and the disagreement map. Details in
[`docs/quickstart.md`](docs/quickstart.md).

- [`AGENTS.md`](AGENTS.md) — the protocol your agent follows
- [`docs/rules.md`](docs/rules.md) — four rules that are absolute
- [`docs/reference-statements.md`](docs/reference-statements.md) — read before editing an reference set

Method: **arXiv:2510.08338** (PyMC Labs and Colgate-Palmolive) for turning free text into ratings ·
**arXiv:2406.20094** (Tencent AI Lab) for how personas are constructed. MIT licensed.
