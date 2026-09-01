# synth-panel

**A synthetic buyer panel that argues with your work before the market does.**

Install it in your coding agent. The agent reads what it can find about your business. It builds a panel
of buyer personas from *your* context. Then it puts your positioning, offers, drafts or product ideas in
front of them.

The tool ranks your options and finds the objection that nobody said out loud.
**It cannot tell you what the market will do.** Read *Honest limits* before you invest any time.

---

## Start here

### Level 1. "Just show me."

```
you: run a synth panel on my landing page
```

That is the whole procedure. Your agent reads the repo and finds the context that it can. Then it builds
a panel and runs it. You need no API key, no configuration file and no account. If the agent cannot find
enough context to build real personas, it tells you. It does not invent them.

Manual commands are in [`docs/quickstart.md`](docs/quickstart.md).

### Level 2. "Ground it in my actual buyers."

Give the agent real material: call transcripts, support threads, customer emails and sales notes.

```
you: build the panel from ./research/ then run a concept screen on these three ideas
```

The tool labels a persona built from a real human sentence `evidence-anchored`. It labels every other
persona `hypothesis`. The label is in every output, so you always know which kind you have.

### Level 3. "Tune it."

Plain files control every part of the judgment. You can edit all of them.

| File | What it controls |
|---|---|
| `personas/*.md` | who is on the panel |
| `reference-statements/<scenario>.json` | how free text becomes a rating |
| `scenarios/*.md` | the questions, and which axes get a rating |

**Before you edit a reference-statement file, read
[`docs/reference-statements.md`](docs/reference-statements.md).** Reference-statement design is the most
fragile part of the method. A set that looks correct can score skeptics as enthusiasts. The repo has a
gate that finds this. Use it.

---

## For the agent that reads this

An agent usually runs this tool. If you are that agent, read these three files in this order and obey
them literally.

1. `AGENTS.md`. The protocol. It tells you what to collect, in what order, and what to do when the
   context is thin.
2. `scenarios/<scenario>.md`. The questions for the run that the user asked for.
3. `docs/rules.md`. The constraints that you must not break.

Four rules are absolute. If you break one, the tool makes confident nonsense.

- **Never ask a persona for a number.** Personas answer in prose. `ssr/rate.py` turns prose into a
  distribution. If you ask a model for "4 out of 5", the scores compress toward the midpoint. We measured
  this. See *Method*.
- **Never rate a property of the artifact.** This method cannot rate "is this differentiated, clear or
  well-written". It returns inverted results. Rate the respondent: *would you pick this, would you keep
  reading, would you pay.* If the user asks for an artifact property, change the question to a stance
  question. Then tell the user that you changed it.
- **Never emit an absolute number to the user.** Report ranks, spreads and disagreement. "68% would buy"
  is the failure mode, not the feature.
- **Never invent a persona.** If you cannot find material to ground a persona, tell the user. Label
  the run `hypothesis — thin`. A thin run with an honest label is useful. A confident fake run is worse
  than no run.

If you find no usable context, do not guess. Tell the user. Then give the two options that help: do an
ICP exercise first, or talk to a real buyer.

---

## Three instruments

| | What you give it | What comes back |
|---|---|---|
| **panel** | a stimulus | verdict spread, distributions where they exist, the disagreement map, objections |
| **interview** | nothing | one persona, deep. Their language, what they use today, the workflow they must break |
| **pre-mortem** | a plan | the ways it dies, ranked by how many personas name the same cause |

People underuse **interview**. It takes no stimulus. You do not test your work. You collect the buyer's
own vocabulary, and that vocabulary is the input your positioning needs.

**Only `panel` rates anything.** The other two instruments return language and ranked causes. They have
no rating machinery and no rating risk.

---

## Five scenarios

`concept-screening` · `offer-pricing` · `feature-prioritisation` · `ad-and-page-resonance` ·
`packaging-choice`

Each scenario defines its own questions and rated axes. A persona can answer every rated question in the
first person, about themselves. This constraint is structural, not stylistic. See *The boundary*.

---

## Method

Ratings use **Semantic Similarity Rating (SSR)**. The persona writes a free-text answer. The rater embeds
that answer and compares it against five reference statements. The result is a probability distribution
on a 1 to 5 scale.

The method is published, not invented: **arXiv:2510.08338**, PyMC Labs and Colgate-Palmolive, October
2025. Across 57 concept surveys and 9,300 human responses, it recovered concept-ranking signal at about
90% of human test-retest reliability.

**Why not ask for a number?** Because it does not work. We measured 96 direct integer scores on this
codebase's own prompts. A `5` never appeared once. 85% of the scores were 2 or 3. A third of the
persona-axis cells returned the *identical* integer across eight independent samples.

### Independence is structural

Each persona runs in **its own process**, with its own empty working directory. The personas cannot see
each other. Most "AI focus groups" use one model to act as five people in one context. Those five cannot
disagree, and their agreement means nothing. Here, agreement is evidence.

### The boundary

SSR rates **first-person stance**. It does not rate **artifact properties**.

One small internal test examined nine axes. Every axis that asks about the *respondent* tracked a
referee's reading. Every axis that asks about the *artifact* did not. `self_recognition`, which asks
whether something sounds like a real person, came out **actively inverted**. The rater scored it
backwards.

That test was small and crude. It is not evidence that the working axes are accurate. It is only evidence
that the failing ones fail, and that is the direction that matters here.

The cause is structural. The artifact's own vocabulary dominates a critique of that artifact, so the
speaker's stance becomes a rounding error in the embedding. Better wording cannot fix it. This is why the
tool refuses "rate my copy" and changes the question to "which one would you pick".

---

## Requirements

**To run it:** an agent CLI that you already use. You need no API key, no account and no service.

**To get distributions:** an embedding provider, configured in `config.toml`. Any OpenAI-compatible
`/embeddings` endpoint works. Nothing is hard-coded to a vendor, and a local runner needs no key and
sends no bill.

**Distributions are off by default, and that is the honest state.** Every reference set in this repo
ships `unchecked`, because the sets failed this repo's own gate. `rate` refuses an unchecked set. To turn
rating on, clear the gate on your own material with `tools/validate.py`. See
[`docs/reference-statements.md`](docs/reference-statements.md).

**The tool runs without an embedding provider.** You get verdicts, objections, the stopped-reading line
and the disagreement map. You lose ranking, not insight. Every run states its mode in the first line.

---

## What it will not do

The refusals are why you can trust the rest.

- **No absolute numbers.** You get ranks and spreads only.
- **No artifact-property ratings.** See *The boundary*.
- **No fabricated personas.** The tool labels thin context. It does not invent the missing material.
- **No distributions from an unchecked reference set.** `rate` stops and prints the gate command.
- **No claim that it replaces real customer conversations.** Read *Honest limits*. This is the most
  important refusal.

---

## Honest limits

Read this section before you act on anything the tool tells you.

**Isolation fixes conformity. It does not create accuracy.** Every persona runs on the same base model.
If that model holds a wrong belief about your buyers, you get five *correlated* errors. The five errors
look exactly like consensus, and the tool cannot detect this.

**Isolation is also not total.** Each subprocess gets a clean working directory, so no project file leaks
in. It does not escape user-level agent configuration. A global `CLAUDE.md` or `AGENTS.md` in your home
directory is still read, and every persona shares whatever it says.

**This tool has no ground truth.** The published validation covers consumer purchase intent. Nobody
calibrated this against real humans in B2B, and we did not either. No human graded anything in this repo.

**You ground the panel. The tool cannot do it for you.** A panel built from real transcripts is much
better than a panel built from a homepage. The tool cannot manufacture validity. It can only state how
much it has, and the fidelity label does that.

**The ceiling, stated plainly:** the tool ranks your concepts and finds the objection that you otherwise
pay a lot of money to hear. **It can never hand you a letter of intent.** Validation runs on behavioral
currency, which means someone spends time, reputation or money. Synthetic panels are attitudinal by
construction. Use this tool to decide what to take to real buyers. Do not take them your worst three
ideas.

---

## Where it came from

I built this inside my own marketing brain, to judge offers and content before I publish. It killed three
of my own ideas.

It is one piece of a larger setup. The pieces work alone, so this one is public.

Built by [Alex Charkin](https://alexcharkin.com). MIT licensed - fork it, tune it, ship it.
