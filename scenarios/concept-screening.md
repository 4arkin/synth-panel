# Scenario · concept-screening

**Instrument:** panel · **Input:** 2–8 concepts.
**Use it when:** you have several ideas and want to know which one to build.
**Scoring:** two axes have a reference set, the third is free text.

This is the case the published method validated (arXiv:2510.08338): recovering the *ranking* of
concepts, not their absolute appeal. Read the output as an ordering.

## Ask each persona, one answer per question

| Axis | The question, put in the second person | Reference set |
|---|---|---|
| `jtbd_fit` | Does this map to a job you are actively trying to do? | yes |
| `would_pay` | Would you exchange money for this at the implied tier? | yes |
| `would_switch` | Would you drop what you use today for it? What would you have to stop doing? | free text |

Ask about **one concept at a time**: one run per concept, with the same roster. A persona that answers
about three concepts in one reply produces one blended response. For the order, add one choice round:
all concepts in one `packaging-choice` run, where each persona picks one or none (`AGENTS.md` step 4).

## Return

- Concepts ranked by pick count from the choice round, with the verdict count for each.
- The strongest objection to each concept, verbatim.
- The concept with the **widest disagreement** across personas — this is usually the most useful line in
  the output, because it is where a real decision is hiding.
- `would_switch` answers unrated: what they would have to give up is the sentence that predicts adoption.

## Reference statements

`reference-statements/concept-screening.json`. `jtbd_fit` and `would_pay` are generic — they name no specific
product, so they carry over to your concepts unchanged. To score with them, clear the gate in
`docs/reference-statements.md` on your own material. `would_switch` is free text by design.

## Machine-readable

The orchestrator reads this block. The prose above is for you.

```json
{
 "scenario": "concept-screening",
 "instrument": "panel",
 "reference_statements": "concept-screening.json",
 "reference_state": "unchecked",
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
