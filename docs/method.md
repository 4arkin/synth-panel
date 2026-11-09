# The method

Why the panel works, how to ground it in real buyer language, which files to tune, and how optional scoring works.

---

## Why the panel works

**It stands on published research.** The study is *LLMs Reproduce Human Purchase Intent via Semantic
Similarity Elicitation of Likert Ratings* ([arXiv:2510.08338](https://arxiv.org/abs/2510.08338)). Its
method collects answers in free text, never as a number, and scores the text afterwards. A model that you
ask for "4 out of 5" crowds the middle of the scale: in 96 direct integer scores on this repo's own
prompts, a `5` never appeared once, and 85% of the scores were 2 or 3. Every panel here collects answers
in free text, and the scoring step is included as an option.

**Each persona is isolated.** Each one runs in its own process, with its own empty working directory. It
cannot see the other personas, your repo, or the agent's reasoning. Most "AI focus groups" use one model
to act as five people in one conversation, and those five cannot disagree. Here they can, so their
agreement is evidence.

**The personas are your buyers.** The agent builds them from your product as roles in a buying decision:
who benefits, who pays, who blocks, who the current solution serves, and who already left. From the one
person that it finds clearly, it derives the rest of the room. Both operations come from *Scaling
Synthetic Data Creation with 1,000,000,000 Personas* ([arXiv:2406.20094](https://arxiv.org/abs/2406.20094),
Tencent AI Lab). See
[`docs/generator.md`](generator.md).

**Every question is about the buyer.** *Would you pick this, would you keep reading, would you pay.* A
persona answers those in the first person, in its own voice. If you ask "is my copy clear", the agent
asks "which one would you pick, and what did you think it was for", and you get the same judgment through
behavior.

**The report is the disagreement.** Options are ranked by how many personas picked each one. The report
names the strongest disagreement by role, quotes every objection word for word, and ends with what to do
this week.

---

## Make it sharper with real buyer language

The agent starts from what your project already says. Real buyer sentences make the panel sharper, and
every report states its level in the first line.

| The panel is built from | Label on the report |
|---|---|
| a URL | `hypothesis — thin` |
| your project, your answers to the agent's questions, a pitch deck, a pricing page | `hypothesis — grounded` |
| things that real people said: call transcripts, support tickets, emails, reviews | `evidence-anchored` |

**No customers yet?** Paste reviews of the product that your buyers use today, forum threads about the
problem, the replies to your cold emails, or the message where someone told you no. One real sentence per
persona moves that persona to `evidence-anchored`.

The personas go into `personas/` as plain files. They are yours. Read them, correct them, and keep them
for the next run.

---

## Tune it

Plain files control every part of the judgment. You can edit all of them.

| File | What it controls |
|---|---|
| `personas/*.md` | who is on the panel |
| `scenarios/*.md` | the questions for each kind of run |
| `instruments/*.md` | the procedure for panel, interview and pre-mortem |
| `prompts/worker.md` | what each persona sees |
| `config.toml` | the agent CLI, the panel size, the rotation between runs |

`examples/personas/` holds a complete worked panel of 18 personas, so that you can see the shape of a
good one.

---

## Scores

Every panel reports picks, verdicts and words. A panel can also turn each written answer into a 1 to 5
distribution with Semantic Similarity Rating (SSR), the scoring step from arXiv:2510.08338.

Scoring is opt-in. You write a reference set in the vocabulary of your own material and pass it through
a gate:

```
python3 bin/synth-panel references --scenario concept-screening --stimulus ./ideas.md
python3 tools/validate.py --scenario concept-screening --stimulus ./ideas.md
```

When the set passes two runs, scoring turns on for that material. You need an embedding endpoint in
`config.toml`. A local one works and needs no key. See
[`docs/reference-statements.md`](reference-statements.md).
