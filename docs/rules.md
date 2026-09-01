# The rules

Four of them are absolute. Each one, broken, makes output that looks more confident and is less true.
That is the only failure mode that costs the reader anything.

## 1 · Never ask a persona for a number

Personas answer in prose. `ssr/rate.py` turns prose into a distribution.

If you ask a model for "4 out of 5", the scores compress and hug the midpoint. We measured this on this
project's own prompts, across 96 direct integer scores. A `5` never appeared once. 85% of the scores were
2 or 3. A third of the persona-axis cells returned the *identical* integer across eight independent
samples. Under SSR, the spread inside a persona rose on every axis. One axis rose by a factor of 7.8.

## 2 · Never rate a property of the artifact

Rate the respondent, not the thing. *Would you pay, would you keep reading, would you pick this one.*
Those all work. *Is this differentiated, is this clear, does this sound like a real person.* Those all
fail.

One small internal test examined nine axes. Every axis that asks about the *respondent* tracked a
referee's reading. Every axis that asks about the *artifact* did not. `self_recognition`, which asks
whether something sounds like a real person, came out **actively inverted**. The rater scored it
backwards.

That test was crude and small. It is not evidence that the working axes are accurate. It is only evidence
that the failing ones fail, which is the direction that matters here.

The cause is structural. The artifact's own vocabulary dominates a critique of that artifact, so the
speaker's stance becomes a rounding error in the embedding. It is not a wording problem, and better
reference statements cannot fix it.

**If the user asks for an artifact rating, change the question to behavior and tell them that you did.**
"Rate my copy" becomes `packaging-choice` or `ad-and-page-resonance`. A good refusal is why the rest is
believable.

## 3 · Never emit an absolute number to the user

Report ranks, spreads, distributions and disagreement. Never "68% would buy".

The *published* evidence belongs to somebody else, it is properly peer-reviewed, and it is the reason
this method is here at all. It is on **ranking recovery**: about 90% of human test-retest reliability
across 57 concept surveys and 9,300 human responses (arXiv:2510.08338, PyMC Labs and Colgate-Palmolive).
That is consumer purchase intent. It is not evidence that a level transfers to a population. It is also
not evidence about B2B, where nobody calibrated any of this against real humans.

Nothing measured *inside this repo* reaches that standard, and no human graded any of it.

## 4 · Never invent a persona

If you cannot find material to ground a persona, say so and label the run `hypothesis — thin`. A thin run
with an honest label is useful. A confident fake one is worse than nothing, because the reader cannot see
the difference from the inside.

If there is no usable context at all, do not guess. Say so, and offer the two things that help: run an
ICP exercise first, or talk to a real human.

---

## Two more, which are engineering rather than method

**Dispatch. Never act as the personas yourself.** Every persona runs as its own subprocess with its own
empty working directory. One model that acts as five people in one context cannot disagree with itself in
any way that means anything, and no prompt fixes that. `synthpanel/dispatch.py` owns this.

**State the mode, every time.** State whether SSR ran or the panel was qualitative. State whether the
reference set was checked, filled in but unchecked, or absent. State where each persona sits on the
fidelity ladder. The label is part of the output, not a footnote to it.

## What isolation does not cover

Each subprocess gets a clean working directory, so no project file leaks in. It does **not** escape
user-level agent configuration. A global `CLAUDE.md`, `AGENTS.md` or equivalent in the user's home
directory is still read by the CLI, and every persona shares whatever it says. If your global
configuration holds opinions, your panel inherits them.

And the larger one, which no amount of isolation touches: every persona runs on the same base model. If
that model holds a wrong belief about your buyers, you get five *correlated* errors that look exactly
like consensus. Independence is not accuracy.
