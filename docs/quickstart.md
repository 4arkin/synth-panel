# Quickstart

Three commands, and then you run panels. There is nothing to install. You need Python 3 and your own
agent CLI.

```
python3 bin/synth-panel detect     # find your agent CLI, write its entrypoint file
python3 bin/synth-panel doctor     # prove that the dispatch works, once
python3 bin/synth-panel personas --examples
```

## Do you need an API key?

**No.** Not to run this.

Personas run through the agent CLI that you already use, so no account and no key is involved in the part
that matters. Interviews, pre-mortems and panels all run as they are. You get verdicts, objections, the
disagreement map, and the line where each persona stopped to read.

**One optional feature needs a key.** The rater turns a persona's written answer into a 1 to 5
distribution. To do that it needs an embedding model, which is an HTTP call to somewhere. See
`docs/reference-statements.md`. That call is the only external dependency in the repo, and it buys you
ranking, not insight.

| You have | What runs |
|---|---|
| an agent CLI | everything except distributions |
| an agent CLI and an embedding provider | the above, plus distributions on a reference set that you checked yourself |

Any OpenAI-compatible `/embeddings` endpoint works. Nothing is hard-coded to a vendor. A local runner
satisfies it with no key and no bill. Configure it in `config.toml` under `[embedding]`, and leave it
empty if you do not want it. `doctor` tells you which mode you are in, and every run states its mode in
the first line.

**Distributions also need a checked reference set, and this repo ships none.** Every set here failed the
repo's own gate, so `rate` refuses them. To turn rating on, clear the gate on your own material. The
procedure is in `docs/reference-statements.md`.

## Your first real run

The panel in `examples/personas/` is a **worked example**. Those are somebody else's buyers. If you put your
work in front of them, you get four articulate, confident opinions about a business that is not yours.
Look at the shape, then build your own.

```
you: read ./research/ and build me a panel, then run a concept screen on these three ideas
```

Your agent reads `AGENTS.md`, sweeps whatever context it can find, writes personas into `personas/`, and
dispatches them. Point it at real human language, such as call transcripts, support threads and sales
notes. Then the run gets the label `evidence-anchored` instead of `hypothesis`. That label is the
difference between a reading worth acting on and a well-written guess, and it appears in every output.

## To do it by hand

```
python3 bin/synth-panel panel --scenario offer-pricing --stimulus ./offer.md --size 4
python3 bin/synth-panel rate runs/<timestamp>          # only with an embedding provider and a checked set
```

`--dry-run` prints the assembled prompts and dispatches nothing. It is the fastest way to see exactly
what each persona can and cannot see.
