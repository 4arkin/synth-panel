# Scenario · ad-and-page-resonance

**Instrument:** panel · **Input:** headlines, ad copy, or a page.
**Rating:** SSR on two axes, free text on the third.

## Ask each persona, one answer per question

| Axis | The question, put in the second person | Rated |
|---|---|---|
| `would_keep_reading` | How far would you read before stopping? | SSR |
| `would_act` | Would you click, reply, or message the author? | SSR |
| `would_trust` | Would you believe this enough to act on it? | free text |

**Always also ask, unrated:** *"Quote the exact line where you stopped, or would have."*

That line is the highest-value thing this scenario produces. A distribution tells you the copy underperforms;
the stopped-at line tells you which sentence did it.

## Anchors

`anchors/anchors-ad-and-page-resonance.json`. Validated at +0.70 / +0.74 across two runs — passing, and the
least stable of the sets that passed. Treat its distributions as coarser than the concept-screening ones.

## Return

Variants ranked · the stopped-at line per persona, verbatim · what they thought was being sold.

## Machine-readable

The orchestrator reads this block. The prose above is for you.

```json
{
 "scenario": "ad-and-page-resonance",
 "instrument": "panel",
 "anchors": "anchors-ad-and-page-resonance.json",
 "anchor_state": "validated",
 "per_item": "variant",
 "verdicts": [
  "would act",
  "would keep reading",
  "would scroll past"
 ],
 "axes": [
  {
   "key": "would_keep_reading",
   "question": "How far would you read before stopping?",
   "rated": true
  },
  {
   "key": "would_act",
   "question": "Would you click, reply, or message the author?",
   "rated": true
  },
  {
   "key": "would_trust",
   "question": "Would you believe this enough to act on it?",
   "rated": false
  },
  {
   "key": "stopped_at",
   "question": "Quote the exact line where you stopped, or would have.",
   "rated": false
  }
 ]
}
```
