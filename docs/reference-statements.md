# Reference statements — read this before editing one

An reference set is five statements per axis, one per point of a 1–5 scale. A persona's free-text answer is
embedded and compared against all five; the similarities become a probability distribution.

Reference-statement design is the single most fragile part of this method. A plausible-looking reference set will silently
score skeptics as enthusiasts, and nothing in the output will look wrong.

## What happened when this repo tested its own reference statements

They did not clear the gate. Six runs, on material they were not written for, using this repo's own
`tools/validate.py`:

| stimulus | panel | pooled |
|---|---|---|
| three concepts at once | mixed | +0.14 |
| three concepts at once | mixed | +0.62 |
| three concepts at once | buyer roles only | +0.16 |
| three concepts at once | buyer roles only | +0.23 |
| **one concept** | mixed | **+0.71** |
| **one concept** | mixed | +0.54 |
| one concept, statements written FOR it | mixed | +0.36 · one axis unmeasurable |
| one concept, statements written FOR it | mixed | +0.72 · one axis unmeasurable |
| a concept the panel splits on, statements written for it | buyer roles | +0.47 |
| a concept the panel splits on, statements written for it | buyer roles | +0.31 |

Ten runs. **No configuration has ever cleared the gate twice.**

Things that were tried and did not fix it: asking about one concept at a time rather than several (this
mattered — it moved the floor from +0.14 to +0.54, and the first four runs were breaking this repo's own
instruction); restricting the panel to plausible buyers rather than including outsiders (it scored
*worse*); and writing the statements for the specific stimulus instead of shipping generic ones (the
principled fix, and the cleanest test of it came back +0.47 and +0.31 — lower than the generic set's best).

**One confound is honestly untested.** The referee — the second model whose reading the rater is scored
against — ran on the same small model as the personas throughout. A referee that reads stance poorly puts
a ceiling on any correlation measurable against it, and that ceiling would look exactly like this. Nobody
has run the gate with a stronger referee.

**So every set in this repo ships `unchecked`, and `rate` refuses to run on one.** The sets are still here
and they are a reasonable starting point. They are not evidence, and this repo will not emit a
distribution on the strength of them.

`synth-panel references` writes a set in your own stimulus's vocabulary, which is what the wording law
asks for and what no shipped file can do for material it has never seen. It did not clear the gate here
either. It is the better-principled starting point, not a fix.

Validating them on **your** stimulus is a real thing you can do, and it is the only thing that would make
a number here mean something:

```
python3 tools/validate.py --scenario <scenario> --stimulus <your file>
```

Clear two runs, flip `reference_state` to `"checked"` in the scenario file, and rating turns on.

## How much any of this was checked

Be suspicious of anything here that sounds like proof.

The reference sets below were checked once, on one author's own material, by a **model referee** — a second
model given the same five reference statements and asked which one the speaker was closest to. That catches a rater
that is badly broken. It is not validation:

- **No human ever graded any of it.** There is no paired human data anywhere in this repo.
- **It was one author's stimulus**, in one industry. Yours is different.
- **The samples were small enough to flip.** One set scored 0.53 on one run and 0.70 on the next, with
  nothing changed between them. That is the honest measure of how much a single number here is worth.

So the sets are not marked "validated" anywhere in this repo, because they are not. They are marked
**checked** or **unchecked**, and the only thing that would upgrade one is you running the gate below on
your own material.

What *is* solid is the failure it caught — see *The boundary*, further down. A rater that scores skeptics
as enthusiasts is visible from a mile away even through a crude test, and that is the finding worth having.

## The wording law

> Every one of the five reference statements for an axis must be written in the **same register** and carry the **same
> topic vocabulary** as the responses being rated. Only the **stance** may vary between scale points.

This is not a style preference. The first implementation used generic stance statements and scored
*backwards* — the more skeptical the sentence, the higher it rated. Its clearest failure:

> *"I am skeptical about the feasibility of installation and integrated components within a month without
> past evidence."* → rated **4.64 / 5**, i.e. "I am confident this is achievable."

Cosine similarity matched the *topic* — feasibility, installation, one month — and was blind to the
*polarity*. Reference statements 4 and 5 shared the response's vocabulary; reference statements 1 and 2 did not. Every on-topic
sentence drifted high regardless of what it actually said.

Rewriting the reference statements so all five shared the topic vocabulary and differed only in stance fixed it. That
rewrite is the entire method.

## Elicit one answer per axis, never one blob

One free-text answer per axis, each answering only its own question. A single blended answer rated against
four different reference sets leaks general positivity across all four.

## The gate — run it on your own material

Before you trust a distribution from an reference set, check it: rank correlation ≥ 0.70 against an
reference-grounded referee, on **two independent runs**. Two, because one is not evidence — see above.

```
python3 tools/validate.py --scenario <scenario> --stimulus ./your-stimulus.md
```

It elicits answers through the real pipeline — same personas, same worker prompts, same subprocess
dispatch a panel uses — then scores each answer twice and reports the rank correlation, pooled and per
axis. The referee is given **the same five anchors** and asked which one the speaker is closest to. A generic "1 = negative, 5 = positive" referee is wrong and understates rho by
roughly 0.3 — it has no meaning for an axis like *"how far would you read"*.

The referee is not ground truth. It is a model reading the same text, which reads polarity correctly where
the embedding does not. That is enough to catch a broken rater and nothing more. It cannot tell you the
scores are right, only that they are not obviously backwards.

## What ships, and in what state

| Scenario | Axes | State |
|---|---|---|
| `concept-screening` | `jtbd_fit`, `would_pay` | **unchecked** · failed the gate here, 1 of 6 runs · wording is generic |
| `ad-and-page-resonance` | `would_keep_reading`, `would_act` | **unchecked** · never tested on foreign material |
| `offer-pricing` | `dream_outcome`, `believability`, `time_tolerance`, `effort_acceptance` | **templated, unchecked once filled** — see below |
| `feature-prioritisation` | — | none · prose only |
| `packaging-choice` | — | none · prose only |

Nothing ships `checked`. `rate` refuses on an unchecked set and tells you how to change that.

### Why offer-pricing is templated and the others are not

The wording law cuts both ways. Generic axes like *would you pay* can be written once and reused, because
their natural vocabulary is the same for every stimulus. Offer axes cannot — a reference statement for *is this outcome
what you want* has to name the outcome, and the outcome is different for every offer.

So the offer set that was checked carried its original stimulus's words at all five scale points. That is
the law working correctly, and it means the wording does not transfer. `reference-statements/offer-pricing.json`
ships with those stimulus-bound fragments replaced by `{{outcome}}` and `{{timeline}}`, to be filled from
your offer in your offer's own words, identically across all five statements of an axis.

**Once you fill it, nobody has checked it — including us.** Whatever the original wording scored belongs to
the original wording. Run the gate on your filled set before you trust a distribution from it.

## Bimodality — when the mean is not a reading

A response in a concession shape — *"yes, I want that, **but** the framing is vocabulary"* — matches the
top reference statement with its first clause and the bottom reference statement with its second. The distribution splits, the middle
hollows out, and the expected value lands somewhere nobody stood. One measured example:
`[0.28, 0.01, 0.00, 0.39, 0.32] → 3.47`, from a persona who both wanted the outcome and rejected how it
was described.

`rate.py` detects this and returns `expected: null` plus the two modes. Report the two modes in words.
Do not average them, and do not quietly fall back to `mean_do_not_report` — it is in the output for
debugging, and its name is the instruction.

On one live run, 6 of 20 axis-cells split this way and 5 of the 6 were the same axis: the one that asks
whether someone wants an outcome. Asking that question reliably produces "yes, but". Expect it.

## Axes with no reference statements

Several axes ship deliberately unrated — `would_switch`, `would_trust`, `would_pay_at_price`,
and everything in the two qualitative scenarios. They are collected as free text.

Free text is not a lesser output. The objection nobody says out loud is the most valuable thing this tool
produces, and it was never going to be a number. If you want one of these rated, author the reference statements and
clear the gate yourself. Do not invent a set to make the table look complete.
