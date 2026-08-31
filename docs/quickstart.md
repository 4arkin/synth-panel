# Quickstart

Three commands, then you are running panels. Nothing to install — it is Python 3 and your own agent CLI.

```
python3 bin/synth-panel detect     # find your agent CLI, write its entrypoint file
python3 bin/synth-panel doctor     # prove the dispatch actually works, once
python3 bin/synth-panel personas --examples
```

## Do you need an API key?

**No.** Not to run this.

Personas run through the agent CLI you are already logged into, so there is no account and no key involved
in the part that matters. Interviews, pre-mortems and panels all run as-is, and you get verdicts,
objections, the disagreement map and the line each persona stopped reading at.

**One optional feature needs one.** Turning a persona's written answer into a 1–5 distribution — the SSR
rating in `docs/reference-statements.md` — requires an embedding model, which is an HTTP call somewhere. That is the
only external dependency in the repo, and it buys you ranking, not insight.

| You have | What runs |
|---|---|
| an agent CLI | everything except distributions |
| an agent CLI + an embedding provider | the above, plus ranked distributions on the scenarios that ship with reference statements |

Any OpenAI-compatible `/embeddings` endpoint works; nothing is hard-coded to a vendor. A local Ollama
satisfies it with no key and no bill. Configure it in `config.toml` under `[embedding]` and leave it empty
if you do not want it. `doctor` tells you which mode you are in, and every run states its mode in its first
line.

## Your first real run

The panel this repo ships in `examples/personas/` is a **worked example** — somebody else's buyers. Running
your work past it will produce four articulate, confident opinions about a business that is not yours.
Look at the shape, then build your own:

```
you: read ./research/ and build me a panel, then run a concept screen on these three ideas
```

Your agent reads `AGENTS.md`, sweeps whatever context it can find, writes personas into `personas/`, and
dispatches them. Point it at real human language — call transcripts, support threads, sales notes — and the
run is labelled `evidence-anchored` instead of `hypothesis`. That label is the difference between a reading
worth acting on and a well-written guess, and it appears in every output.

## Doing it by hand

```
python3 bin/synth-panel panel --scenario offer-pricing --stimulus ./offer.md --size 4
python3 bin/synth-panel rate runs/<timestamp>          # only if you configured an embedding provider
```

`--dry-run` prints the assembled prompts and dispatches nothing, which is the fastest way to see exactly
what each persona will and will not be able to see.
