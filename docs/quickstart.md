# Quickstart

There is nothing to install. You need Python 3 and your own agent CLI.

## The short way: one message to your agent

Open the project that you are building, and tell your AI agent:

```
Clone https://github.com/4arkin/synth-panel and read its AGENTS.md.
Then build a buyer panel for this project and test my landing page on it.
```

The agent clones the repo, sets it up, reads what you build from your project, writes your buyer personas
into `personas/`, and runs them. It asks you a question only when the project does not answer it.

Then ask for the next run in plain words:

```
prioritise this backlog on the panel: …
```

```
add the support tickets in ./tickets/ to the panel, then run a concept screen on these three ideas: …
```

## The setup, by hand

```
git clone https://github.com/4arkin/synth-panel
cd synth-panel
python3 bin/synth-panel detect     # find your agent CLI, write its entrypoint file
python3 bin/synth-panel doctor     # prove that the dispatch works, once
```

`doctor` sends one probe through your agent CLI and prints `PASS`. After that, you run panels.

## Do you need an API key?

**No.** Personas run through the agent CLI that you already use. Panels, interviews and pre-mortems all
run as they are. You get the ranking, the verdicts, the objections, the disagreement map, and the line
where each persona stopped reading.

A panel of five personas is five calls to your agent CLI. On a subscription, those calls use your normal
allowance. `detect` pins a small model where `agents.toml` names one for your CLI, because a persona
does not need a large model.

**One optional feature uses an embedding model.** Scoring turns a persona's written answer into a 1 to 5
distribution. Any OpenAI-compatible `/embeddings` endpoint works, and a local runner needs no key.
Configure it in `config.toml` under `[embedding]`. The procedure is in `docs/reference-statements.md`.

| You have | What runs |
|---|---|
| an agent CLI | panels, interviews, pre-mortems, ranking by picks and verdicts |
| an agent CLI, an embedding endpoint and a reference set that passed the gate on your material | the above, plus 1 to 5 distributions |

`doctor` tells you which mode you are in, and every run states its mode in the first line.

## Your first real run

`examples/personas/` holds a complete worked panel: 18 personas built for one consulting business. Use it
to see the shape of a good persona file.

```
python3 bin/synth-panel personas --examples
```

Then build your own. A panel judges your work as the people in it, so those people must be your buyers.
Point the agent at real human language, such as call transcripts, support threads, sales notes and
reviews. The run then gets the label `evidence-anchored` in place of `hypothesis`, and the label appears
in the first line of every report.

No customers yet? Paste reviews of the product that your buyers use today, forum threads about the
problem, or the replies to your cold emails. Those are real buyer sentences too.

## To do it by hand

```
python3 bin/synth-panel panel --scenario offer-pricing --stimulus ./offer.md --size 4
```

The scenarios are `concept-screening`, `offer-pricing`, `feature-prioritisation`,
`ad-and-page-resonance` and `packaging-choice`. Each run writes the answers of every persona to
`runs/<timestamp>/`.

To compare several ideas, keep the roster the same in every run. One run per idea gives you the reasons.
One choice round on all ideas gives you the order:

```
python3 bin/synth-panel panel --scenario concept-screening --stimulus ./idea-a.md --size 4
python3 bin/synth-panel panel --scenario concept-screening --stimulus ./idea-b.md --size 4 \
    --include <slug> --include <slug> --include <slug> --include <slug>
python3 bin/synth-panel panel --scenario packaging-choice --stimulus ./all-ideas.md --size 4 \
    --include <slug> --include <slug> --include <slug> --include <slug>
```

`--dry-run` prints the assembled prompts and dispatches nothing. It is the fastest way to see exactly
what each persona can and cannot see.
