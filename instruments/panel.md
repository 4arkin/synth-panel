# Instrument · panel

**Give it:** a stimulus. **Personas:** 3–5, each in its own process. **Rates:** yes, on stance axes only.

The only instrument that scores anything, which is why it carries all of the method's risk and all of its
caveats. Pick a scenario from `scenarios/` — the scenario decides the questions and which axes are rated.

## Procedure

1. Compose the panel (`docs/generator.md`). 3–5 personas, at least one skeptic, at least two distinct roles
   in the buying decision.
2. Assemble one self-contained prompt per persona from `prompts/worker.md`.
3. Dispatch them **all at once, each in its own process**. Never role-play them yourself in one context —
   that is the thing this repo exists to not do, and it is not recoverable by prompting.
4. Rate the SSR axes if an embedding provider is configured. If not, skip and say so.
5. Build the disagreement map before you write a summary. It is the output, not a section of it.

## Return

Verdict spread · distributions where rated · the disagreement map · objections, verbatim.

## Read it as a ranking

The evidence behind this method is ranking recovery, not level accuracy. "Concept B beat concept A across
four of five personas" is supported. "68% would buy" is not, and emitting it is the failure mode.
