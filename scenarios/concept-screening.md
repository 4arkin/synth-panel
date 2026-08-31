# Scenario · concept-screening

**Instrument:** panel · **Input:** 2–8 concepts · **Rating:** SSR on two axes, free text on the third.

This is the case the published method validated (arXiv:2510.08338): recovering the *ranking* of
concepts, not their absolute appeal. Read the output as an ordering.

## Ask each persona, one answer per question

| Axis | The question, put in the second person | Rated |
|---|---|---|
| `jtbd_fit` | Does this map to a job you are actively trying to do? | SSR |
| `would_pay` | Would you exchange money for this at the implied tier? | SSR |
| `would_switch` | Would you drop what you use today for it? What would you have to stop doing? | free text |

Ask about **one concept at a time**. A persona rating three concepts in one answer produces one blended
response, and the ranking you came for disappears into it.

## Return

- Concepts ranked, per persona and pooled.
- The strongest objection to each concept, verbatim.
- The concept with the **widest disagreement** across personas — this is usually the most useful line in
  the output, because it is where a real decision is hiding.
- `would_switch` answers unrated: what they would have to give up is the sentence that predicts adoption.

## Anchors

`anchors/anchors-concept-screening.json`. `jtbd_fit` and `would_pay` are generic — they name no specific
product, so they carry over to your concepts unchanged. They have been checked once against a model
referee, on somebody else's material; read `docs/anchors.md` on what that is and is not worth.
`would_switch` has no anchor set at all; do not invent one to make the output look complete.

## Machine-readable

The orchestrator reads this block. The prose above is for you.

```json
{
 "scenario": "concept-screening",
 "instrument": "panel",
 "anchors": "anchors-concept-screening.json",
 "anchor_state": "checked",
 "per_item": "concept",
 "verdicts": [
  "would use it",
  "curious",
  "not for me"
 ],
 "axes": [
  {
   "key": "jtbd_fit",
   "question": "Does this map to a job you are actively trying to do?",
   "rated": true
  },
  {
   "key": "would_pay",
   "question": "Would you exchange money for this at the implied tier?",
   "rated": true
  },
  {
   "key": "would_switch",
   "question": "Would you drop what you use today for it, and what would you have to stop doing?",
   "rated": false
  }
 ]
}
```
