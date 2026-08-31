# Anchors — read this before editing one

An anchor set is five statements per axis, one per point of a 1–5 scale. A persona's free-text answer is
embedded and compared against all five; the similarities become a probability distribution.

Anchor design is the single most fragile part of this method. A plausible-looking anchor set will silently
score skeptics as enthusiasts, and nothing in the output will look wrong.

## The anchor law

> Every one of the five anchors for an axis must be written in the **same register** and carry the **same
> topic vocabulary** as the responses being rated. Only the **stance** may vary between scale points.

This was measured, not asserted. The first implementation used generic stance statements and
**anti-correlated with direct scoring at rho −0.69**. Its clearest failure:

> *"I am skeptical about the feasibility of installation and integrated components within a month without
> past evidence."* → rated **4.64 / 5**, i.e. "I am confident this is achievable."

Cosine similarity matched the *topic* — feasibility, installation, one month — and was blind to the
*polarity*. Anchors 4 and 5 shared the response's vocabulary; anchors 1 and 2 did not. Every on-topic
sentence drifted high regardless of what it actually said.

Rewriting the anchors so all five shared the topic vocabulary and differed only in stance moved the same
harness from **+0.43 to +0.73**. That rewrite is the entire fix.

## Elicit one answer per axis, never one blob

One free-text answer per axis, each answering only its own question. A single blended answer rated against
four different anchor sets leaks general positivity across all four.

## The two-run gate

**No anchor set ships unvalidated, and one passing run is not evidence.**

Rho ≥ 0.70 against an anchor-grounded referee, on **two independent runs**. This is not caution for its own
sake: one set scored 0.53 on one run and 0.70 on the next, identically configured. At the sample sizes
involved, the estimate is noisy enough to flip a gate decision on its own.

Method in `ssr/validate.md`. The referee must be given **the same five anchors** and asked which one the
speaker is closest to. A generic "1 = negative, 5 = positive" referee is wrong and understates rho by
roughly 0.3 — it has no meaning for an axis like *"how far would you read"*.

The referee is not ground truth. It is a model reading the same text, which reads polarity correctly where
the embedding does not. That is enough to catch a broken rater. It cannot certify accuracy against humans.

## What ships, and in what state

| Scenario | Axes | State |
|---|---|---|
| `concept-screening` | `jtbd_fit`, `would_pay` | **validated**, +0.86 · generic wording, transfers unchanged |
| `ad-and-page-resonance` | `would_keep_reading`, `would_act` | **validated**, +0.70 / +0.74 · generic wording, transfers unchanged |
| `offer-pricing` | `dream_outcome`, `believability`, `time_tolerance`, `effort_acceptance` | **templated** — see below |
| `feature-prioritisation` | — | none · qualitative |
| `packaging-choice` | — | none · qualitative |

### Why offer-pricing is templated and the others are not

The anchor law cuts both ways. Generic axes like *would you pay* can be written once and reused, because
their natural vocabulary is the same for every stimulus. Offer axes cannot — an anchor for *is this outcome
what you want* has to name the outcome, and the outcome is different for every offer.

So the validated offer set carried its original stimulus's words at all five scale points. That is the law
working correctly, and it means the wording does not transfer. `anchors/anchors-offer-pricing.json` ships
with those stimulus-bound fragments replaced by `{{outcome}}` and `{{timeline}}`, to be filled from your
offer in your offer's own words, identically across all five statements of an axis.

**A filled template is derived, not validated.** The +0.73 belongs to the original wording. Run
`ssr/validate.md` against your filled set before you trust a distribution from it, and until you have,
label the run's ratings as derived.

## Bimodality — when the mean is not a reading

A response in a concession shape — *"yes, I want that, **but** the framing is vocabulary"* — matches the
top anchor with its first clause and the bottom anchor with its second. The distribution splits, the middle
hollows out, and the expected value lands somewhere nobody stood. One measured example:
`[0.28, 0.01, 0.00, 0.39, 0.32] → 3.47`, from a persona who both wanted the outcome and rejected how it
was described.

`rate.py` detects this and returns `expected: null` plus the two modes. Report the two modes in words.
Do not average them, and do not quietly fall back to `mean_do_not_report` — it is in the output for
debugging, and its name is the instruction.

On a live run, 6 of 20 axis-cells split this way and 5 of the 6 were the same axis: the one that asks
whether someone wants an outcome. Asking that question reliably produces "yes, but". Expect it.

## Axes with no anchors

Several axes ship deliberately unrated — `would_switch`, `would_trust`, `would_pay_at_price`,
and everything in the two qualitative scenarios. They are collected as free text.

Free text is not a lesser output. The objection nobody says out loud is the most valuable thing this tool
produces, and it was never going to be a number. If you want one of these rated, author the anchors and
clear the two-run gate. Do not invent a set to make the table look complete.
