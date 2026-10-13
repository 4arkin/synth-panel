# Scoring. Reference statements and the gate.

Scoring is optional. A panel is complete without it: verdict counts, objections and the disagreement map
come from every run. Scoring adds a 1 to 5 distribution for each written answer, with Semantic Similarity
Rating (SSR) from arXiv:2510.08338.

A reference set is five statements per axis, one for each point of the scale. The rater embeds a
persona's free-text answer and compares it against all five. The similarities become a probability
distribution.

## Turn scoring on

1. Put an embedding endpoint in `config.toml` under `[embedding]`. Any OpenAI-compatible `/embeddings`
   endpoint works. A local runner needs no key.
2. Write a reference set in the vocabulary of your own material:

   ```
   python3 bin/synth-panel references --scenario <scenario> --stimulus ./your-file.md
   ```

3. Run the gate:

   ```
   python3 tools/validate.py --scenario <scenario> --stimulus ./your-file.md
   ```

The gate runs twice. When both runs pass, it records the result in the set. From then on, `panel` prints
`SSR` in its state line for that material, and `rate` scores the run:

```
python3 bin/synth-panel rate runs/<timestamp>
```

Sets are stored by scenario and material in `reference-statements/generated/`. If you change the
material, you write and check a new set.

To use a shipped generic set, run the gate on it with your material. When two runs pass, set
`reference_state` to `"checked"` in the scenario file.

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
rewrite is the entire method, and `references` applies it to your material. It also rejects a set whose
negative end is shorter than its positive end, because that shape causes the same failure.

## Elicit one answer per axis, never one blob

Collect one free-text answer per axis. Each answer must answer only its own question. A single blended
answer, rated against four different reference sets, leaks general positivity across all four.

For the same reason, show a persona one item per run. One reply about three ideas blends the three.

## The gate

The bar is a rank correlation of 0.70 or more against a referee, on **two independent runs**. One run is
not enough at these sample sizes. The same set scored 0.53 on one run and 0.70 on the next, with no
change between them.

```
python3 tools/validate.py --scenario <scenario> --stimulus ./your-file.md
```

The gate elicits answers through the real pipeline, with the same personas, the same worker prompts and
the same subprocess dispatch that a panel uses. Then it scores each answer twice and reports the rank
correlation, pooled and per axis.

- **SSR** embeds the answer and compares it against the five reference statements.
- **The referee** is a model that gets the same five reference statements and names the one that the
  speaker is closest to.

The referee reads polarity correctly where an embedding can miss it. A set that passes the gate is
`checked`: it agrees with a model referee on your material, and it does not score skeptics as
enthusiasts. Use the word `checked` when you report a distribution.

An axis that every persona answers in the same way has no order to correlate. The gate reports that axis
as `UNDEFINED` and leaves it out of the pooled figure. Run the gate on material that your panel splits
on.

By default, the referee runs on the same command as the personas. To run it on a stronger model:

```
python3 tools/validate.py --scenario <scenario> --stimulus ./your-file.md \
    --referee-command "<your CLI> <flags for a larger model>"
```

## What ships, and in what state

| Scenario | Axes with a reference set | State |
|---|---|---|
| `concept-screening` | `jtbd_fit`, `would_pay` | `unchecked` · generic wording, a starting set |
| `ad-and-page-resonance` | `would_keep_reading`, `would_act` | `unchecked` · generic wording, a starting set |
| `offer-pricing` | `dream_outcome`, `believability`, `time_tolerance`, `effort_acceptance` | `templated` · fill it, or generate a set |
| `feature-prioritisation` | none | free text and verdict counts |
| `packaging-choice` | none | a forced choice, ranked by pick count |

A set becomes `checked` on your installation, with your material. `rate` runs on a checked set and prints
the gate command for any other.

### Why offer-pricing is a template

Generic axes such as *would you pay* can be written once and reused, because their natural vocabulary is
the same for every offer. Offer axes cannot. A reference statement for *is this outcome what you want*
has to name the outcome, and the outcome is different for every offer.

`reference-statements/offer-pricing.json` ships with `{{outcome}}` and `{{timeline}}` placeholders. Fill
them from your offer, in your offer's own words, identically across all five statements of an axis. Or
let `references` write the full set for you. Then run the gate.

## Bimodality. When the mean is not a reading.

Take a response in a concession shape, such as *"yes, I want that, **but** the framing is vocabulary"*.
Its first clause matches the top reference statement. Its second clause matches the bottom one. The
distribution splits, the middle hollows out, and the expected value lands where nobody stood. One
measured example: `[0.28, 0.01, 0.00, 0.39, 0.32] → 3.47`, from a persona who both wanted the outcome and
rejected how it was described.

`rate.py` detects this and returns `expected: null` plus the two modes. Report the two modes in words. Do
not average them. The field `mean_do_not_report` is in the output for debugging, and its name is the
instruction.

On one live run, 6 of 20 axis-cells split this way, and 5 of the 6 were the same axis. That axis asks
whether someone wants an outcome. That question reliably produces "yes, but". Expect it.

## Axes with no reference statements

Several axes are free text by design: `would_switch`, `would_trust`, `would_pay_at_price`, and everything
in the two qualitative scenarios.

Free text is the primary output. The objection that nobody says out loud is the most valuable thing that
this tool produces, and it is a sentence. To score one of these axes, write the reference statements and
clear the gate.
