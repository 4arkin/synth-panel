# Instrument · panel

**Give it:** a stimulus — the thing you want judged. **Personas:** 3–5, each in its own process.
**Returns:** a ranking, a split, and the objections.

Pick a scenario from `scenarios/` — the scenario decides the questions and the verdicts.

## Procedure

1. Compose the panel (`docs/generator.md`). 3–5 personas, at least one skeptic, at least two distinct roles
   in the buying decision.
2. Assemble one self-contained prompt per persona from `prompts/worker.md`.
3. Dispatch them **all at once, each in its own process**. Never role-play them yourself in one context —
   that is the thing this repo exists to not do, and it is not recoverable by prompting.
4. Several items: one choice round on all of them for the order, then one run per item for the
   reasons, all with the same roster (`AGENTS.md` step 4).
5. Score the rated axes only when the state line says `SSR`. Otherwise go on.
6. Build the disagreement map before you write a summary. It is the output, not a section of it.

## Return

The ranking by pick count and verdict count · the disagreement map · objections, verbatim ·
distributions where scored.

## Read it as a ranking

The evidence behind this method is ranking recovery, not level accuracy. "Concept B beat concept A across
four of five personas" is supported. "68% would buy" is not, so the report never says it.
