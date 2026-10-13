# Scenario · ad-and-page-resonance

**Instrument:** panel · **Input:** headlines, ad copy, or a page.
**Use it when:** you want to know if a page, an ad or a headline holds a buyer's attention.
**Scoring:** two axes have a reference set, the third is free text.

## Ask each persona, one answer per question

| Axis | The question, put in the second person | Reference set |
|---|---|---|
| `would_keep_reading` | How far would you read before stopping? | yes |
| `would_act` | Would you click, reply, or message the author? | yes |
| `would_trust` | Would you believe this enough to act on it? | free text |

**Always also ask, unrated:** *"Quote the exact line where you stopped, or would have."*

That line is the highest-value thing this scenario produces. A verdict tells you the copy underperforms;
the stopped-at line tells you which sentence did it.

For several variants, run one variant per run with the same roster, and add one choice round on all of
them for the order (`AGENTS.md` step 4).

## Reference statements

`reference-statements/ad-and-page-resonance.json`. Generic wording, so it carries over to your page
unchanged. To score with it, clear the gate in `docs/reference-statements.md` on your own material.

## Return

Variants ranked by pick count · the stopped-at line per persona, verbatim · what they thought was being
sold.

## Machine-readable

The orchestrator reads this block. The prose above is for you.

```json
{
 "scenario": "ad-and-page-resonance",
 "instrument": "panel",
 "reference_statements": "ad-and-page-resonance.json",
 "reference_state": "unchecked",
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
