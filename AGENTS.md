# AGENTS.md — the protocol

You are the agent running this repository. A person has asked you to put something in front of a synthetic
buyer panel. Follow this literally.

**Read `docs/rules.md` before your first dispatch.** Four of its rules are absolute. They are the difference
between a reading someone can act on and confident nonsense that reads exactly the same.

---

## 0 · Pick the instrument

| They gave you | Instrument | File |
|---|---|---|
| something to judge | `panel` | `instruments/panel.md` |
| nothing — they want to hear a buyer talk | `interview` | `instruments/interview.md` |
| a plan | `pre-mortem` | `instruments/pre-mortem.md` |

If they asked you to **rate copy, brand, voice, or how differentiated something is**, do not do it. That
shape fails by construction (`docs/rules.md` §2). Reframe it to `packaging-choice` or
`ad-and-page-resonance`, run that, and tell them you switched and why in one sentence.

For `panel`, pick the scenario and read its file:

`concept-screening` · `offer-pricing` · `feature-prioritisation` · `ad-and-page-resonance` · `packaging-choice`

---

## 1 · Gather context, in this order, and stop when you have enough

1. What the user pointed you at — a directory, a file, a URL. Always first.
2. Real human language: call transcripts, support threads, sales notes, customer emails, reviews. This is
   the tier that changes the output. Look for it before anything else in the repo.
3. Positioning material: ICP notes, a deck, a pricing page, an about page.
4. The website, if that is all there is.

Then place the run on the fidelity ladder and **say where it landed, in the output, every time**:

| What you found | Label |
|---|---|
| a URL and nothing else | `hypothesis — thin` |
| positioning notes, a deck, an ICP | `hypothesis — grounded` |
| transcripts, emails, tickets — real human sentences | `evidence-anchored` |

**If you found nothing usable, stop.** Do not invent personas to have something to show. Say plainly that
there is not enough here to build a panel worth reading, and offer the two things that help: run an ICP
exercise first, or talk to an actual buyer.

---

## 2 · Build the panel

`docs/generator.md` has the method. Short version: extract personas as **roles in a buying decision** — who
benefits, who pays, who blocks, who the incumbent serves, who already left — not demographics. Ground each
in at least one verbatim line from the source where a real-language source exists; a persona with no
verbatim anchor is marked `hypothesis` and says so in every output it appears in.

Compose 3–5 for this run: **at least one skeptic, at least two distinct roles.** Write them to
`personas/<slug>.md`. They are yours to keep and edit; the repo does not own them.

---

## 3 · Dispatch — one persona, one process

```
python3 bin/synth-panel detect     # once: find your agent CLI, write its entrypoint file
python3 bin/synth-panel doctor     # once: prove the dispatch command actually works
```

Then assemble one self-contained prompt per persona from `prompts/worker.md` and dispatch them **all at
once, each in its own subprocess**, via `synthpanel/dispatch.py`.

**Do not role-play the personas yourself.** Not in sequence, not in sections, not "as if" isolated. One
model playing five people in one context produces five voices that cannot genuinely disagree, and their
agreement means nothing. This is the one claim the repo makes about itself. It is structural, and you
cannot restore it with a prompt.

---

## 4 · Rate — only if you can, only what is validated

If `[embedding]` is configured in `config.toml`, pipe each worker's `axes` object to `ssr/rate.py` with the
scenario's anchor file. If it is not configured, **skip this step and run qualitatively** — verdicts,
objections, the disagreement map and the stopped-at line all survive. You lose ranking, not insight.

Before you use an anchor file, check its state in `docs/anchors.md`. Some ship validated, one ships
templated and must be filled from the stimulus, and two scenarios ship with none at all. Never author a
quick anchor set to fill a gap — see the two-run gate.

When `rate.py` returns `"bimodal": true`, `expected` is `null` on purpose. Report the two modes in words.

---

## 5 · Report

Build the disagreement map first. It is the output, not a section of it.

Every report opens with a state line, and it is not optional:

```
Panel: 4 personas · fidelity: hypothesis — grounded · rating: SSR (concept-screening, validated anchors)
Panel: 3 personas · fidelity: evidence-anchored · rating: qualitative (no embedding provider configured)
```

Then: verdict spread · distributions where you have them · the strongest disagreement, named by role pair ·
objections verbatim · what nobody said out loud.

**Ranks and spreads only. Never a headline percentage.** "68% would buy" is the failure mode, not the
feature — the evidence behind this method is on ranking, not levels.

End with something they can do this week. A panel that terminates in a list of observations wasted
everyone's compute.
