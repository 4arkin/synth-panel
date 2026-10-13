# synth-panel

**A synthetic buyer panel that argues with your work before the market does.**

You build an app or a SaaS. You do not have the audience to test every idea, feature and message on real
people. synth-panel gives your AI agent a panel of *your* buyers, and you test anything on them in
minutes:

- an idea, before you build it
- a feature backlog, to decide what comes next
- a price or an offer
- a landing page, an ad, an email, any message
- a name, a tagline, a pricing plan
- a launch plan, before you launch
- the same product in two markets, side by side

It works for consumer apps and for B2B buying committees. You get a ranking, the reasons behind it, and
the objection that nobody says to your face.

**The method is published and measured against people.** In a study by PyMC Labs and Colgate-Palmolive,
synthetic respondents reached about 90% of human test-retest reliability, across 57 product surveys and
9,300 human responses ([arXiv:2510.08338](https://arxiv.org/abs/2510.08338)). synth-panel uses that
elicitation method on your buyers. It runs each persona as a separate, isolated AI instance, so five
personas give you five independent readings.

You need no API key, no account and no marketing background.

> **AI agents:** read [`AGENTS.md`](AGENTS.md). It is the complete protocol.

---

## Start with one message

Open the project that you are building. Tell your AI agent:

```
Clone https://github.com/4arkin/synth-panel and read its AGENTS.md.
Then build a buyer panel for this project and test my landing page on it.
```

Your agent clones the repo, learns what you build from your own project, builds your buyer personas, runs
each one in its own process, and gives you the report. In a trial on a new app project, a fresh agent
went from this message to a finished panel run in under three minutes.

Then continue. Test the price. Rank the backlog. Interview a buyer. The panel is saved, and it rotates
between runs, so a revised draft meets fresh readers.

**Requirements:** Python 3 and an agent CLI. The repo is tested end to end on Claude Code. It ships
dispatch settings for Codex, Gemini CLI, Cursor Agent, opencode, Amp and Crush, and `doctor` confirms
yours in one command. Any other CLI that takes a prompt and prints an answer works with one line of
configuration.

Manual commands are in [`docs/quickstart.md`](docs/quickstart.md).

---

## What to ask

| You want to know | Tell your agent | You get |
|---|---|---|
| Which idea do I build? | `run a concept screen on these three ideas: …` | the ideas ranked, the strongest objection to each, and the idea that splits the panel |
| What do I build next? | `prioritise this backlog: …` | the features that buyers rank in opposite order, and the feature that nobody would miss |
| Does my offer and price work? | `test this offer and price: …` | the part that stops the deal: the outcome, the belief, the timeline, the effort or the price |
| Does my landing page work? | `run my landing page past the panel` | the exact line where each buyer stopped reading, and what each one thought you sell |
| Which name, tagline or plan? | `which of these would the panel pick: …` | a count of picks, and what each buyer thought it was for |
| How do my buyers talk? | `interview a buyer about how they handle <problem> today` | their own words, what they use today, and who else decides |
| What will stop my launch? | `pre-mortem this plan: …` | the causes of failure, ranked by how many personas named each one independently, and a to-do |
| How does it land in another market? | `run the same panel for buyers in Germany and in the US` | the same roles in each market, and where their answers differ |

A **panel** judges something that you show it. An **interview** takes nothing from you and returns the
buyer's vocabulary, which is the input your landing page needs. A **pre-mortem** takes a plan and tells
you how it failed.

---

## What comes back

This is a real run. Three product ideas went in front of four personas from the worked example in
`examples/personas/`: a bootstrapped founder, a head of marketing, a CFO and a marketing manager. Every
quote is a persona's own words.

```
Panel: 4 personas · fidelity: hypothesis — grounded · rating: qualitative

THE ANSWER
1. Exit interview   3 of 4 picks   automatic email interview with every customer who cancels, $29/mo
2. Call-to-copy     1 of 4 picks   landing page written from your sales-call recordings, $49/mo
3. Launch plan      0 of 4 picks   launch checklist and content calendar from your changelog, $19/mo

THE SPLIT
Everyone inside a company that already has customers picked the exit interview.
The bootstrapped founder rejected it and picked call-to-copy.
  CFO:      "a customer who leaves is a loss I can already see on a ledger, and I'd rather
             know why than guess."
  Founder:  "I don't have enough cancellations for a monthly digest to say anything I could
             act on."

THE OBJECTIONS
  Exit interview · head of marketing: "Ex-customers rarely answer surveys, so I have no idea
    how much of a digest I'd actually get back."
  Call-to-copy · founder: "I don't have a stack of recorded sales calls, so there's nothing
    for it to pull phrases from yet."
  Launch plan · marketing manager: "The calendar comes from a changelog, which says what we
    built but not why a buyer would care, so I'd be rewriting every post anyway."

WHAT NOBODY SAID OUT LOUD
  Marketing manager: "Couldn't a founder just read the cancel emails herself in ten minutes
    a week and skip paying for this?"

DO THIS WEEK
1. Build the exit interview first, and sell it to companies that already have churn.
2. Put the response rate on the page. It is the first question from the person who has to
   defend the purchase.
3. Make the digest show what the cancellations cost. The CFO: "Curious only if it prices
   churn. Otherwise it's a newsletter."
```

Each persona answered in about 20 seconds, on a small model.

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
[`docs/generator.md`](docs/generator.md).

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
[`docs/reference-statements.md`](docs/reference-statements.md).

---

## Where it came from

I built this inside my own marketing brain, to judge offers and content before I publish. It killed three
of my own ideas.

It is one piece of a larger setup. The pieces work alone, so this one is public.

Built by [Alex Charkin](https://alexcharkin.com). MIT licensed - fork it, tune it, ship it.
