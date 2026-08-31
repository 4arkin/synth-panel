# Scenario · offer-pricing

**Instrument:** panel · **Input:** an offer, optionally several framings of the same offer.
**Rating:** SSR on four axes once anchors are filled, free text on the fifth.

## Ask each persona, one answer per question

| Axis | The question, put in the second person | Rated |
|---|---|---|
| `dream_outcome` | Is the promised outcome something you actually want? | SSR — **read the warning** |
| `believability` | Do you believe it can be delivered as described? | SSR |
| `time_tolerance` | Does the timeline work for you? | SSR |
| `effort_acceptance` | Is what it asks of you beyond money acceptable? | SSR |
| `would_pay_at_price` | Would you pay this price for this? | free text |

## Warning · the concession shape

`dream_outcome` reliably provokes *"yes, I want that, **but** …"*. The affirmative clause matches the top
anchor, the concession matches the bottom one, and the distribution splits with a hollow middle. Its mean
then describes a position nobody held. `ssr/rate.py` detects this, returns `expected: null` and reports the
two modes instead. **When it fires, report both modes in words** — "wants the outcome, rejects the framing"
— and never average them. Measured on a live run: 5 of 6 split cells were this axis.

## Before you rate anything

`anchors/anchors-offer-pricing.json` is **templated**. Fill `{{outcome}}` and `{{timeline}}` from the offer's
own words, in the same register at all five scale points. Anchors whose positive end echoes the offer's
vocabulary while the negative end does not will score skeptics as enthusiasts — measured, not theoretical.
A filled set is derived, not validated. Say so in the output.

## Return

Framings ranked · the axis that kills it · where stance flips as price moves · the objection nobody said.
