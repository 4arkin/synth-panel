# Scenario · packaging-choice

**Instrument:** panel · **Input:** competing packages, names, or positioning variants.
**Rating:** none — qualitative only in this version.

## Ask each persona, one answer per question

| Axis | The question, put in the second person |
|---|---|
| `would_pick` | Which of these would you choose — and would you choose any of them? |
| `would_shortlist` | Would this survive to a shortlist you would show someone else? |

**Always also ask, unrated — this is the drift note:** *"What did you think this was for?"*

Their answer is what your packaging actually communicates, as opposed to what it says.

## No anchors ship for this scenario

`would_pick` is a forced choice between options, not a position on a 1–5 scale, so SSR has nothing to
rate — the answer is a name, and the ranking comes from counting names. `would_shortlist` has no validated
anchor set. Report the count and the split.

## Why this scenario exists

It absorbs the request this tool refuses. "Rate my copy / brand / voice" asks the method to score a
property of the artifact, which it cannot do — measured: *differentiation* +0.08, *voice-fit* −0.13,
*self-recognition* −0.63, actively inverted. Reframed as "which would you pick, and what did you think it
was for", the same judgement comes back through behaviour, where the method works. Redirect here and say
you did.

## Return

Forced ranking with counts · the drift note per persona, verbatim · the variant that splits the panel.

## Machine-readable

The orchestrator reads this block. The prose above is for you.

```json
{
 "scenario": "packaging-choice",
 "instrument": "panel",
 "anchors": null,
 "anchor_state": "none",
 "per_item": "option",
 "verdicts": [
  "would pick this",
  "would shortlist",
  "would pick none"
 ],
 "axes": [
  {
   "key": "would_pick",
   "question": "Which of these would you choose \u2014 and would you choose any of them?",
   "rated": false
  },
  {
   "key": "would_shortlist",
   "question": "Would this survive to a shortlist you would show someone else?",
   "rated": false
  },
  {
   "key": "drift_note",
   "question": "What did you think this was for?",
   "rated": false
  }
 ]
}
```
