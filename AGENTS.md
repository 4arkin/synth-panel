# AGENTS.md · the protocol

You are the agent that runs this repository. A person builds a product and wants to test something on a
synthetic buyer panel: an idea, a feature list, a price, a page, a message, a plan. This document tells
you how to build their buyers, run the panel and report. Obey it literally.

**Move fast.** The user's first report must arrive in minutes. Use the context that you already have
about what they build. Ask only for what you cannot find.

**Use plain words.** Assume that the user has no marketing background. Say "the person who pays", not
"economic buyer". Say "what you showed the panel", not "stimulus". If you must use a label from this
repo, explain it in half a sentence the first time.

**Read `docs/rules.md` before your first dispatch.** Four of its rules are absolute.

---

## 0 · Set up, once

If the user gave you this repository as a link, clone it. Put it beside their project, or inside it with
the folder added to their `.gitignore`. Then run, from the clone:

```
python3 bin/synth-panel detect     # find the agent CLI, write its entrypoint file
python3 bin/synth-panel doctor     # prove that the dispatch command works
```

`doctor` must print `PASS`. If it fails, it prints what to change in `config.local.toml`.

The context for the panel is **the user's project**, not this repository. The personas that you build go
into `personas/` in the clone, and they stay there for every later run.

---

## 1 · Pick the instrument

| They gave you | Instrument | File |
|---|---|---|
| something to judge | `panel` | `instruments/panel.md` |
| nothing, and they want to hear a buyer talk | `interview` | `instruments/interview.md` |
| a plan | `pre-mortem` | `instruments/pre-mortem.md` |

For `panel`, pick the scenario and read its file.

| They want to know | Scenario |
|---|---|
| which idea to build | `concept-screening` |
| what to build next from a backlog | `feature-prioritisation` |
| if an offer and its price work | `offer-pricing` |
| if a page, an ad, an email or a headline works | `ad-and-page-resonance` |
| which name, tagline, plan or positioning to use | `packaging-choice` |

If they asked you to **rate copy, brand, voice, or how differentiated something is**, change the question
(`docs/rules.md` §2). Run `packaging-choice` or `ad-and-page-resonance`, and tell them in one sentence
that you changed it and why.

If they did not say what to test, pick the most useful first run from what the project has. A landing
page gets `ad-and-page-resonance`. A backlog or a roadmap file gets `feature-prioritisation`. A project
with neither gets an `interview`.

---

## 2 · Collect context. Stop when you have enough.

Read in this order.

1. What the user pointed you at: a directory, a file, a URL.
2. The user's project: the README, the landing page and its copy, the pricing, the docs, the store
   listing, the roadmap or the issue tracker, and what you already know from this session.
3. Real human language, wherever it is: call transcripts, support threads, sales notes, customer emails,
   reviews. This tier changes the output most.
4. The public website, if that is all there is.

You have enough when you can name **who benefits, who pays, what they use today, and why they would say
no**. An answer that the project implies counts. Then build the panel. Do not ask the user for things
that the project already told you.

### Ask only for what is missing

If you can infer the answer, go on, and put the open questions at the end of the report. Stop and ask
only when you cannot name who the buyer is. Use the questions that you need from this list, in these
plain words:

1. What does it do, in one sentence, and for whom?
2. Who pays for it? Is that the same person who uses it?
3. What do those people use today instead? A spreadsheet or "nothing" is a valid answer.
4. What does it cost, or what do you plan to charge?
5. Who can say no, and what is their reason? For a company: a boss, a co-founder, finance, IT. For a
   consumer: a partner, a habit, a free alternative.
6. Did a real person say anything about it yet? Paste any message, review, reply or rejection, word for
   word.

Their answers are context. Build the panel from them.

To make the panel sharper, collect real buyer language. Ask the user to paste reviews of the product
that their buyers use today, forum threads about the problem, or replies to their outreach. If you can
browse and the user agrees, collect that public language yourself. Quote it word for word and record
where it came from.

### Label the run

**State the label in the output, every time.**

| What you built from | Label |
|---|---|
| a URL and nothing else | `hypothesis — thin` |
| the user's project, their answers, positioning notes, a deck | `hypothesis — grounded` |
| transcripts, emails, tickets, reviews, real human sentences | `evidence-anchored` |

The state line that `panel` prints shows `hypothesis` or `evidence-anchored`, from the `grounding` field
of the persona files. In your report, write the full label from this table.

A persona comes from context, always. If you have no project, no URL and no answers, ask the six
questions before you do anything else.

---

## 3 · Build the panel

`docs/generator.md` has the method. The short version: extract personas as **roles in a buying
decision**. Find who benefits, who pays, who blocks, who the current solution serves, and who already
left. Do not use demographics.

- **A consumer product** has the same roles in fewer people. The user and the payer are often one
  person. The blockers are the habit, the free alternative, and the partner who sees the bank statement.
- **A B2B product** has a buying committee. From the champion, derive who signs, who must change their
  workflow, whose budget shrinks, and who recommended the current solution.

Use the roles that the context supports. A product with no customers yet has nobody who already left,
so leave that role out.

Ground each persona in at least one verbatim line from a buyer, where a real-language source exists. The
product's own copy is not buyer language. A persona with no buyer line is marked `hypothesis`.

Build a pool of 6 to 9 personas where the context supports it. Four is enough to start. The pool needs
**at least two skeptics and at least three distinct roles**. Write each one to `personas/<slug>.md` in
the shape that `docs/generator.md` gives, and read that shape before you write. The pool belongs to the
user, who can read it and correct it.

Each run draws 3 to 5 personas from the pool, with at least one skeptic and at least two roles, and
rotates them, so that a revised draft meets fresh readers.

Show the user the pool in one line per persona: the name, the role in the decision, and what makes that
persona say no. Then dispatch. Do not wait for approval unless the user asked to review the panel first.

### Markets and segments

If the user wants to compare markets or segments, build the same roles one time for each market. Give
each persona that market's situation, current alternative and objections. Use slugs such as `de-payer`
and `us-payer`. Run the same material one time for each market, and pick that market's personas with
`--include`. Report the answers side by side, role against role.

---

## 4 · Dispatch. One persona, one process.

```
python3 bin/synth-panel panel --scenario <scenario> --stimulus <file> --size 4
```

Write what the user wants judged into a text file, and pass it as `--stimulus`. For a page in HTML or in
component code, write the text that a visitor sees, in reading order. `panel` composes the roster,
assembles one self-contained prompt per persona from `prompts/worker.md`, and dispatches them **all at
the same time, each in its own subprocess**. The answers go to `runs/<timestamp>/`.

Without `--size`, `panel` draws 3 to 5 personas. Add `--include <slug>` for a persona that this material
needs: the person who pays, when the material names a price. Add `--dry-run` to read the assembled
prompts before you dispatch. Do that for the first run of a new pool.

For an interview or a pre-mortem, assemble the prompts from the instrument file and `prompts/worker.md`,
and dispatch them with `python3 bin/synth-panel run <prompts.json>`.

### Several items: a choice round and the depth runs

If the user gave you several ideas, features or variants, do two kinds of run with **the same roster**.

1. **The choice round gives the order.** Put all items in one file, labelled `OPTION A`, `OPTION B` and
   so on. Run `--scenario packaging-choice` on it. Each persona picks one item, or none.
2. **The depth runs give the reasons.** Run the scenario that the user needs one time for each item, one
   item per file. One persona that answers about three ideas in one reply blends them.

Take the roster from the first run and pin it on the others with `--include <slug>` for each persona and
`--size <n>`. Start the runs at the same time. Different rosters cannot be compared.

For more than five items, run the choice round first. Then do the depth runs for the top three items and
for any item that split the panel.

**Do not act as the personas yourself.** Not in sequence, not in sections, and not "as if" isolated. One
model that acts as five people in one context makes five voices that cannot disagree. Isolation is what
makes the panel's agreement count, and only a separate process gives it.

---

## 5 · Report

Build the disagreement map first. It is the output, not a section of it.

Write the report in this order. Keep it short enough to read in two minutes.

**1. The state line.**

```
Panel: 4 personas · fidelity: hypothesis — grounded · rating: qualitative
```

Add one plain sentence that says what the panel was built from.

**2. The answer.** If the user gave you several items, rank them by pick count from the choice round.
Break a tie with the verdict counts from the depth runs: more top verdicts first, then fewer bottom
verdicts. If the items are still level, report a tie. Show the counts for each item, for example
`Idea B: 3 of 4 picks · 3 curious · 1 not for me`. For one item, give the verdict count and the one-line
position of each persona.

**3. The split.** Name the strongest disagreement by role pair, for example "the person who pays wants
it, the person who must use it does not". Give each side's reason in that persona's own words.

**4. The objections.** Quote them word for word, with the persona's role. For a page, an ad or a message,
quote the exact line where each persona stopped. Lead with the objections that the persona file did not
contain. Those are the panel's own findings. An objection that repeats the persona's `objection_pattern`
confirms what you already wrote, so give it one line.

**5. What nobody said out loud.** Each persona returned an `unsaid` field. Report the one that matters
most.

**6. Do this week.** Give at most three actions. Make each one specific to what the panel said: the line
to rewrite, the feature to cut, the idea to build, the price to change.

**7. The next run.** Offer one, in one line. After a page test, offer to test the revised page. After a
concept screen, offer a pre-mortem on the winner. If the panel has no real buyer language yet, offer an
interview instead.

**8. Open questions.** If you built the panel on an answer that you inferred, list the questions here,
at most three. The user's answers make the next panel sharper.

**Report ranks, counts and words.** A count is "3 of 4". Do not convert a count into a percentage of a
market. The evidence behind this method is on ranking.

The full answers of every persona are in `runs/<timestamp>/`. Offer them if the user wants more.

---

## 6 · Scoring, when the user asks for it

Every run is complete without scoring. Scoring adds a 1 to 5 distribution for each written answer.

`panel` prints the rating mode in its state line. If that line says `SSR`, run
`python3 bin/synth-panel rate runs/<timestamp>`. If it says `qualitative`, report as in step 5.

To turn scoring on, follow `docs/reference-statements.md`: write a reference set for the user's material
with `python3 bin/synth-panel references`, and pass it through the gate in `tools/validate.py`. Use only
a set that passed the gate. Name a set by its state, `checked` or `unchecked`. Never ask a persona for a
number in place of scoring.

When `rate` returns `"bimodal": true`, `expected` is `null` on purpose. Report the two modes in words.
