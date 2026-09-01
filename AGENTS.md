# AGENTS.md · the protocol

You are the agent that runs this repository. A person asked you to put something in front of a synthetic
buyer panel. Obey this document literally.

**Read `docs/rules.md` before your first dispatch.** Four of its rules are absolute. They are the
difference between a reading that someone can act on and confident nonsense that reads the same way.

---

## 0 · Pick the instrument

| They gave you | Instrument | File |
|---|---|---|
| something to judge | `panel` | `instruments/panel.md` |
| nothing, and they want to hear a buyer talk | `interview` | `instruments/interview.md` |
| a plan | `pre-mortem` | `instruments/pre-mortem.md` |

If they asked you to **rate copy, brand, voice, or how differentiated something is**, do not do it. That
shape fails by construction (`docs/rules.md` §2). Change the question to `packaging-choice` or
`ad-and-page-resonance`, run that, and tell them in one sentence that you changed it and why.

For `panel`, pick the scenario and read its file:

`concept-screening` · `offer-pricing` · `feature-prioritisation` · `ad-and-page-resonance` ·
`packaging-choice`

---

## 1 · Collect context in this order. Stop when you have enough.

1. What the user pointed you at: a directory, a file, a URL. Always first.
2. Real human language: call transcripts, support threads, sales notes, customer emails, reviews. This
   tier changes the output. Look for it before anything else in the repo.
3. Positioning material: ICP notes, a deck, a pricing page, an about page.
4. The website, if that is all there is.

Then put the run on the fidelity ladder. **State where it landed, in the output, every time.**

| What you found | Label |
|---|---|
| a URL and nothing else | `hypothesis — thin` |
| positioning notes, a deck, an ICP | `hypothesis — grounded` |
| transcripts, emails, tickets, real human sentences | `evidence-anchored` |

**If you found nothing usable, stop.** Do not invent personas to have something to show. Say plainly that
there is not enough material here for a panel worth reading. Then offer the two things that help: run an
ICP exercise first, or talk to a real buyer.

---

## 2 · Build the panel

`docs/generator.md` has the method. The short version: extract personas as **roles in a buying decision**.
Find who benefits, who pays, who blocks, who the incumbent serves, and who already left. Do not use
demographics.

Ground each persona in at least one verbatim line from the source, where a real-language source exists. A
persona with no verbatim line is marked `hypothesis` and says so in every output that it appears in.

Compose 3 to 5 personas for this run. Include **at least one skeptic and at least two distinct roles**.
Write them to `personas/<slug>.md`. They belong to the user, who can keep them and edit them. The repo
does not own them.

---

## 3 · Dispatch. One persona, one process.

```
python3 bin/synth-panel detect     # once: find your agent CLI, write its entrypoint file
python3 bin/synth-panel doctor     # once: prove that the dispatch command works
```

Then assemble one self-contained prompt per persona from `prompts/worker.md`. Dispatch them **all at the
same time, each in its own subprocess**, through `synthpanel/dispatch.py`.

**Do not act as the personas yourself.** Not in sequence, not in sections, and not "as if" isolated. One
model that acts as five people in one context makes five voices that cannot genuinely disagree, and their
agreement means nothing. This is the one claim that the repo makes about itself. It is structural, and no
prompt can restore it.

---

## 4 · Rate, only if you can, and only what has a reference set

If `[embedding]` is configured in `config.toml`, pipe each worker's `axes` object to `ssr/rate.py` with
the scenario's reference-statement file. If it is not configured, **skip this step and run
qualitatively**. Verdicts, objections, the disagreement map and the stopped-reading line all survive. You
lose ranking, not insight.

Before you use a reference-statement file, examine its state in `docs/reference-statements.md`. Read what
"checked" means there, because it is weaker than it sounds. Never write a quick reference set to fill a
gap.

**Every reference set in this repo ships `unchecked`, and `rate` refuses to run on one.** That is not an
oversight. The sets were tested here and they failed. If the user wants distributions, point them at
`tools/validate.py` to clear the gate on their own material first. A panel without distributions is the
normal case, not a degraded one.

**Never describe a rating in this repo as validated.** No human graded anything here.

When `rate.py` returns `"bimodal": true`, `expected` is `null` on purpose. Report the two modes in words.

---

## 5 · Report

Build the disagreement map first. It is the output, not a section of it.

Every report opens with a state line. The state line is not optional.

```
Panel: 4 personas · fidelity: hypothesis — grounded · rating: SSR (concept-screening, checked reference statements)
Panel: 3 personas · fidelity: evidence-anchored · rating: qualitative (no embedding provider configured)
```

Then give the verdict spread and the distributions where you have them. Name the strongest disagreement
by role pair. Quote the objections verbatim. End with what nobody said out loud.

**Ranks and spreads only. Never a headline percentage.** "68% would buy" is the failure mode, not the
feature. The evidence behind this method is on ranking, not on levels.

End with something that the user can do this week. A panel that ends in a list of observations wasted
everyone's compute.
