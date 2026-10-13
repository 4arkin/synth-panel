# Scenario · offer-pricing

**Instrument:** panel · **Input:** an offer, optionally several framings of the same offer.
**Use it when:** you want to know which part of an offer stops the deal.
**Scoring:** four axes have a templated reference set, the fifth is free text.

## Ask each persona, one answer per question

| Axis | The question, put in the second person | Reference set |
|---|---|---|
| `dream_outcome` | Is the promised outcome something you actually want? | template — **read the note** |
| `believability` | Do you believe it can be delivered as described? | template |
| `time_tolerance` | Does the timeline work for you? | template |
| `effort_acceptance` | Is what it asks of you beyond money acceptable? | template |
| `would_pay_at_price` | Would you pay this price for this? | free text |

## Note · the concession shape

`dream_outcome` reliably provokes *"yes, I want that, **but** …"*. Read both halves. "Wants the outcome,
rejects the framing" is the finding, and it is more useful than a yes or a no.

When scoring is on, the affirmative clause matches the top reference statement and the concession matches
the bottom one, so the distribution splits with a hollow middle. `ssr/rate.py` detects this, returns
`expected: null` and reports the two modes. **Report both modes in words** and never average them. On a
live run, 5 of 6 split cells were this axis.

## To score this scenario

`reference-statements/offer-pricing.json` is a **template**. Fill `{{outcome}}` and `{{timeline}}` from the
offer's own words, in the same register at all five scale points, or let `synth-panel references` write
the set from your offer. Then clear the gate in `docs/reference-statements.md`.

## Return

Framings ranked by pick count from a choice round · the axis that stops the deal · where stance flips as
price moves · the objection nobody said.

## Machine-readable

The orchestrator reads this block. The prose above is for you.

```json
{
 "scenario": "offer-pricing",
 "instrument": "panel",
 "reference_statements": "offer-pricing.json",
 "reference_state": "templated",
 "per_item": "framing",
 "verdicts": [
  "yes",
  "partial",
  "no"
 ],
 "axes": [
  {
   "key": "dream_outcome",
   "question": "Is the promised outcome something you actually want?",
   "rated": true
  },
  {
   "key": "believability",
   "question": "Do you believe it can be delivered as described?",
   "rated": true
  },
  {
   "key": "time_tolerance",
   "question": "Does the timeline work for you?",
   "rated": true
  },
  {
   "key": "effort_acceptance",
   "question": "Is what it asks of you beyond money acceptable?",
   "rated": true
  },
  {
   "key": "would_pay_at_price",
   "question": "Would you pay this price for this?",
   "rated": false
  }
 ]
}
```
