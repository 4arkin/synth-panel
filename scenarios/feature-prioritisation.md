# Scenario · feature-prioritisation

**Instrument:** panel · **Input:** a feature list.
**Use it when:** you want to know what to build next, and what to cut.
**Scoring:** none. Verdict counts and free text.

## Ask each persona, one answer per question, one feature at a time

| Axis | The question, put in the second person |
|---|---|
| `would_use` | Would you use this, in a normal week? Describe the week. |
| `would_pay_more` | Would you pay more to have it? |
| `would_miss_it` | Would you notice if it disappeared tomorrow? |

## What this scenario is for

The output that matters is **the features personas rank oppositely.** A roadmap argument lives in the
split, not in the average. A choice round on the full list gives you the order (`AGENTS.md` step 4), and
the prose from the per-feature runs gives you the reason.

## Return

Per-persona ordering · the features with opposite orderings across personas, named by role pair ·
the feature everyone was indifferent to, which is the one to cut.

To add scoring to this scenario, write reference statements and clear the gate in
`docs/reference-statements.md`.

## Machine-readable

The orchestrator reads this block. The prose above is for you.

```json
{
 "scenario": "feature-prioritisation",
 "instrument": "panel",
 "reference_statements": null,
 "reference_state": "none",
 "per_item": "feature",
 "verdicts": [
  "would use",
  "indifferent",
  "would not use"
 ],
 "axes": [
  {
   "key": "would_use",
   "question": "Would you use this, in a normal week? Describe the week.",
   "rated": false
  },
  {
   "key": "would_pay_more",
   "question": "Would you pay more to have it?",
   "rated": false
  },
  {
   "key": "would_miss_it",
   "question": "Would you notice if it disappeared tomorrow?",
   "rated": false
  }
 ]
}
```
