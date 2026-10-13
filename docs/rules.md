# The rules

Four of them are absolute. Each one protects the same thing: a report that is as true as it sounds.

## 1 · Never ask a persona for a number

Personas answer in prose. Picks and verdicts rank the options. When scoring is on, `ssr/rate.py` turns
the prose into a distribution.

If you ask a model for "4 out of 5", the scores crowd the middle of the scale. We measured this on this
project's own prompts, across 96 direct integer scores. A `5` never appeared once. 85% of the scores were
2 or 3. A third of the persona-axis cells returned the *identical* integer across eight independent
samples. Under SSR, the spread inside a persona rose on every axis. One axis rose by a factor of 7.8.

## 2 · Never rate a property of the artifact

Rate the respondent, not the thing. *Would you pay, would you keep reading, would you pick this one.*
Those all work. *Is this differentiated, is this clear, does this sound like a real person.* Those all
fail.

An internal test examined nine axes. Every axis that asks about the *respondent* tracked a referee's
reading. Every axis that asks about the *artifact* did not. `self_recognition`, which asks whether
something sounds like a real person, came out **inverted**. The rater scored it backwards.

The cause is structural. The artifact's own vocabulary dominates a critique of that artifact, so the
speaker's stance becomes a rounding error in the embedding. Better reference statements cannot fix it.

**If the user asks for an artifact rating, change the question to behavior and tell them that you did.**
"Rate my copy" becomes `packaging-choice` or `ad-and-page-resonance`. The user gets the same judgment
through a question that a buyer can answer.

## 3 · Never emit an absolute number to the user

Report ranks, counts, spreads and disagreement. Never "68% would buy".

The published evidence for this method is on **ranking**: about 90% of human test-retest reliability
across 57 product surveys and 9,300 human responses (arXiv:2510.08338, PyMC Labs and Colgate-Palmolive).
So the tool reports an order and the reasons behind it.

## 4 · Never invent a persona

Build every persona from context: the user's project, a URL, the user's own answers, or real buyer
sentences. Label the run with its level: `hypothesis — thin`, `hypothesis — grounded` or
`evidence-anchored`. The label tells the reader what the panel stands on.

If you have no context at all, ask the user the questions in `AGENTS.md` step 2 before you build
anything.

---

## Two more, which are engineering rules

**Dispatch. Never act as the personas yourself.** Every persona runs as its own subprocess with its own
empty working directory. One model that acts as five people in one context cannot disagree with itself,
and no prompt fixes that. `synthpanel/dispatch.py` owns this.

**State the mode, every time.** State where the run sits on the fidelity ladder. State whether the run
was qualitative or scored. The label is part of the output.

## What the personas share

Each subprocess gets a clean working directory, so no project file leaks in. User-level agent
configuration is the exception. The CLI still reads a global `CLAUDE.md`, `AGENTS.md` or equivalent in
the user's home directory, and every persona shares what it says. If your global configuration holds
opinions, your panel inherits them. If your CLI has a flag that ignores user configuration, add it to
`[dispatch].command`.

The personas also share one base model. Real buyer sentences in the persona files are what make each
persona its own person, and a split between personas is the strongest signal in a report.
