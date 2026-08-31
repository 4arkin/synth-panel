# Scenario · feature-prioritisation

**Instrument:** panel · **Input:** a feature list. **Rating:** none — qualitative only in this version.

## Ask each persona, one answer per question, one feature at a time

| Axis | The question, put in the second person |
|---|---|
| `would_use` | Would you use this, in a normal week? Describe the week. |
| `would_pay_more` | Would you pay more to have it? |
| `would_miss_it` | Would you notice if it disappeared tomorrow? |

## No anchors ship for this scenario

There is no anchor set for these axes, so nothing here is scored and no distribution is reported. That is a stated limit, not a defect — a made-up anchor set produces a confident number with
no evidence behind it, which is worse than a ranked list of prose.

You still get the output that matters: **the features personas rank oppositely.** A roadmap argument lives
in the split, not in the average.

## Return

Per-persona ordering · the features with opposite orderings across personas, named by role pair ·
the feature everyone was indifferent to, which is the one to cut.

To score this scenario, author anchors and clear the two-run gate in `ssr/validate.md` first.

## Machine-readable

The orchestrator reads this block. The prose above is for you.

```json
{
 "scenario": "feature-prioritisation",
 "instrument": "panel",
 "anchors": null,
 "anchor_state": "none",
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
