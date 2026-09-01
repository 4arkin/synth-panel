# Reference statements. Read this before you edit one.

A reference set is five statements per axis, one per point of a 1 to 5 scale. The rater embeds a
persona's free-text answer and compares it against all five. The similarities become a probability
distribution.

Reference-statement design is the most fragile part of this method. A set that looks correct will score
skeptics as enthusiasts, and nothing in the output will look wrong.

## What happened when this repo tested its own reference statements

They did not clear the gate. Ten runs, on material that the statements were not written for, through
this repo's own `tools/validate.py`:

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

**No configuration ever cleared the gate twice.**

Three things were tried and none of them fixed it:

- **One concept at a time instead of several.** This mattered. It moved the floor from +0.14 to +0.54,
  and the first four runs broke this repo's own instruction.
- **A panel of plausible buyers only, without outsiders.** It scored *worse*.
- **Statements written for the specific stimulus instead of generic ones.** This is the principled fix.
  The cleanest test of it returned +0.47 and +0.31, which is lower than the generic set's best.

**One confound is honestly untested.** The referee is the second model whose reading the rater is scored
against. It ran on the same small model as the personas throughout. A referee that reads stance poorly
puts a ceiling on any correlation measurable against it, and that ceiling looks exactly like this.
Nobody ran the gate with a stronger referee.

**So every set in this repo ships `unchecked`, and `rate` refuses to run on one.** The sets are still
here and they are a reasonable start. They are not evidence, and this repo will not emit a distribution
on the strength of them.

`synth-panel references` writes a set in your own stimulus's vocabulary. That is what the wording law
asks for, and no shipped file can do it for material that it never saw. It did not clear the gate here
either. It is the better-principled start, not a fix.

To run the gate on **your** stimulus is a real thing that you can do. It is the only thing that makes a
number here mean something:

```
python3 tools/validate.py --scenario <scenario> --stimulus <your file>
```

## How much of this was examined

Be suspicious of anything here that sounds like proof.

The sets below were examined once, on one author's own material, by a **model referee**. The referee got
the same five reference statements and named the one that the speaker was closest to. That catches a
rater that is badly broken. It is not validation:

- **No human ever graded any of it.** There is no paired human data anywhere in this repo.
- **It was one author's stimulus**, in one industry. Yours is different.
- **The samples were small enough to flip.** One set scored 0.53 on one run and 0.70 on the next, with
  nothing changed between them. That is the honest measure of what a single number here is worth.

So no set is marked "validated" anywhere in this repo, because none of them are. They are marked
**checked** or **unchecked**. The only thing that upgrades one is you, running the gate below on your own
material.

What *is* solid is the failure that the test caught. See *The wording law*. A rater that scores skeptics
as enthusiasts is visible from a mile away, even through a crude test, and that is the finding worth
having.

## The wording law

> All five reference statements for an axis must use the **same register** and the **same topic
> vocabulary** as the responses that they rate. Only the **stance** can change between scale points.

This is not a style preference. The first implementation used generic stance statements and scored
*backwards*. The more skeptical the sentence, the higher it rated. Its clearest failure:

> *"I am skeptical about the feasibility of installation and integrated components within a month without
> past evidence."* rated **4.64 / 5**, which means "I am confident this is achievable."

Cosine similarity matched the *topic*, which was feasibility, installation and one month. It was blind to
the *polarity*. Reference statements 4 and 5 shared the response's vocabulary. Reference statements 1 and
2 did not. Every on-topic sentence drifted high, whatever it said.

A rewrite fixed it. All five statements shared the topic vocabulary and differed only in stance. That
rewrite is the entire method.

## Elicit one answer per axis, never one blob

Collect one free-text answer per axis. Each answer must answer only its own question. A single blended
answer, rated against four different reference sets, leaks general positivity across all four.

## The gate. Run it on your own material.

Before you trust a distribution from a reference set, examine it. The bar is a rank correlation of 0.70
or more against a reference-grounded referee, on **two independent runs**. Two, because one is not
evidence.

```
python3 tools/validate.py --scenario <scenario> --stimulus ./your-stimulus.md
```

It elicits answers through the real pipeline, with the same personas, the same worker prompts and the
same subprocess dispatch that a panel uses. Then it scores each answer twice and reports the rank
correlation, pooled and per axis. The referee gets **the same five reference statements** and names the
one that the speaker is closest to. A generic "1 = negative, 5 = positive" referee is wrong. It
understates rho by about 0.3, and it has no meaning for an axis such as *"how far would you read"*.

The referee is not ground truth. It is a model that reads the same text, and it reads polarity correctly
where the embedding does not. That is enough to catch a broken rater and nothing more. It cannot tell you
that the scores are right, only that they are not obviously backwards.

Clear two runs, set `reference_state` to `"checked"` in the scenario file, and rating turns on.

## What ships, and in what state

| Scenario | Axes | State |
|---|---|---|
| `concept-screening` | `jtbd_fit`, `would_pay` | **unchecked** · failed the gate here, cleared 1 of 6 runs · generic wording |
| `ad-and-page-resonance` | `would_keep_reading`, `would_act` | **unchecked** · never tested on foreign material |
| `offer-pricing` | `dream_outcome`, `believability`, `time_tolerance`, `effort_acceptance` | **templated, unchecked once filled** · see below |
| `feature-prioritisation` | none | none · prose only |
| `packaging-choice` | none | none · prose only |

Nothing ships `checked`. `rate` refuses an unchecked set and tells you how to change that.

### Why offer-pricing is templated and the others are not

The wording law cuts both ways. Generic axes such as *would you pay* can be written once and reused,
because their natural vocabulary is the same for every stimulus. Offer axes cannot. A reference statement
for *is this outcome what you want* has to name the outcome, and the outcome is different for every
offer.

So the offer set that was examined carried its original stimulus's words at all five scale points. That
is the law working correctly, and it means that the wording does not transfer.
`reference-statements/offer-pricing.json` ships with those stimulus-bound fragments replaced by
`{{outcome}}` and `{{timeline}}`. Fill them from your offer, in your offer's own words, identically
across all five statements of an axis.

**Once you fill it, nobody examined it, including us.** Whatever the original wording scored belongs to
the original wording. Run the gate on your filled set before you trust a distribution from it.

## Bimodality. When the mean is not a reading.

Take a response in a concession shape, such as *"yes, I want that, **but** the framing is vocabulary"*.
Its first clause matches the top reference statement. Its second clause matches the bottom one. The
distribution splits, the middle hollows out, and the expected value lands where nobody stood. One measured example:
`[0.28, 0.01, 0.00, 0.39, 0.32] → 3.47`, from a persona who both wanted the outcome and rejected how it
was described.

`rate.py` detects this and returns `expected: null` plus the two modes. Report the two modes in words. Do
not average them, and do not quietly fall back to `mean_do_not_report`. That field is in the output for
debugging, and its name is the instruction.

On one live run, 6 of 20 axis-cells split this way, and 5 of the 6 were the same axis. That axis asks
whether someone wants an outcome. Asking that question reliably produces "yes, but". Expect it.

## Axes with no reference statements

Several axes ship deliberately unrated: `would_switch`, `would_trust`, `would_pay_at_price`, and
everything in the two qualitative scenarios. The tool collects them as free text.

Free text is not a lesser output. The objection that nobody says out loud is the most valuable thing that
this tool produces, and it was never going to be a number. If you want one of these rated, write the
reference statements and clear the gate yourself. Do not invent a set to make the table look complete.
