# The rules

Four of them are absolute. They are absolute because each one, broken, produces output that looks more
confident and is less true — which is the only failure mode that actually costs the reader anything.

## 1 · Never ask a persona for a number

Personas answer in prose. `ssr/rate.py` turns prose into a distribution.

Asking a model for "4 out of 5" produces compressed, midpoint-hugging scores. Measured on this project's
own prompts, across 96 direct integer scores: a `5` never appeared once, 85% of scores were 2 or 3, and a
third of persona-axis cells returned the *identical* integer across eight independent samples. Under SSR,
within-persona spread rose on every axis — one of them by a factor of 7.8.

## 2 · Never rate a property of the artifact

Rate the respondent, not the thing. *Would you pay, would you keep reading, would you pick this one* — all
work. *Is this differentiated, is this clear, does this sound like a real person* — all fail.

Checked across nine axes in one small internal test. Every axis asking about the *respondent* tracked a
referee's reading. Every axis asking about the *artifact* did not, and `self_recognition` — "does this
sound like a real person" — came out **actively inverted**: the rater scored it backwards.

That test was crude and small, and it is not evidence that the working axes are accurate. It is only
evidence that the failing ones fail, which is the direction that matters here.

The cause is structural. A critique of an artifact is dominated by the artifact's own vocabulary, so the
speaker's stance becomes a rounding error in the embedding. It is not a wording problem and cannot be
fixed by writing better anchors.

**If the user asks for an artifact rating, reframe it to behaviour and tell them you did.** "Rate my copy"
becomes `packaging-choice` or `ad-and-page-resonance`. Refusing well is why the rest is believable.

## 3 · Never emit an absolute number to the user

Ranks, spreads, distributions and disagreement. Never "68% would buy".

The *published* evidence — which is somebody else's, properly peer-reviewed, and the reason this method is
here at all — is on **ranking recovery**: roughly 90% of human test–retest reliability across 57 concept
surveys and 9,300 human responses (arXiv:2510.08338, PyMC Labs and Colgate-Palmolive). That is consumer
purchase intent. It is not evidence that a level transfers to a population, and it is not evidence about
B2B, where nobody has calibrated any of this against real humans.

Nothing measured *inside this repo* rises to that standard, and none of it was graded by a human.

## 4 · Never fabricate a persona

If you cannot find material to ground one, say so and label the run `hypothesis — thin`. A thin run,
honestly labelled, is useful. A confident fake one is worse than nothing, because the reader cannot tell
the difference from the inside.

If there is no usable context at all, do not guess. Say so, and offer the two things that actually help:
run an ICP exercise first, or talk to a real human.

---

## Two more, which are engineering rather than method

**Dispatch, never role-play.** Every persona runs as its own subprocess with its own empty working
directory. One model playing five people in one context cannot disagree with itself in any way that means
anything, and no prompt fixes that. `synthpanel/dispatch.py` owns this.

**State the mode, every time.** Whether SSR ran or the panel was qualitative; whether the anchor set was
checked, filled-in but unchecked, or absent; where each persona sits on the fidelity ladder. The label is part of the
output, not a footnote to it.

## What isolation does not cover

Each subprocess gets a clean working directory, so no project file leaks in. It does **not** escape
user-level agent configuration — a global `CLAUDE.md`, `AGENTS.md` or equivalent in the user's home
directory is still read by the CLI, and personas will share whatever it says. If your global config has
opinions, your panel inherits them.

And the larger one, which no amount of isolation touches: every persona runs on the same base model. If
that model holds a wrong belief about your buyers, you get five *correlated* errors that look exactly like
consensus. Independence is not accuracy.
