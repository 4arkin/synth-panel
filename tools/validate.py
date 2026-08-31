#!/usr/bin/env python3
"""Check a set of reference statements before you trust a distribution from it.

    python3 tools/validate.py --scenario concept-screening --stimulus ./concepts.md

WHAT IT DOES. Elicits free-text answers through the real pipeline — the same
personas, the same worker prompts, the same subprocess dispatch a panel uses —
then scores every answer twice:

    SSR      the rater under test: embed the answer, compare against the five
             references, take the expected value
    referee  a second model shown THE SAME FIVE REFERENCE STATEMENTS, asked which
             one the speaker is closest to

and reports the rank correlation between them, pooled and per axis.

WHAT IT DOES NOT DO. It cannot tell you the scores are right. The referee is a
model reading the same text, and it reads polarity correctly where an embedding
does not — that is enough to catch a rater that scores skeptics as enthusiasts,
which is the failure this method actually has. Certifying accuracy would need
paired human data, and there is none here.

THE GATE. Rank correlation >= 0.70, on two independent runs. Two, because at
these sample sizes one run is not evidence: a set has scored 0.53 on one run and
0.70 on the next with nothing changed between them. `--runs 2` is the default and
lowering it defeats the purpose.

Per-axis numbers are the real diagnostic. An axis near zero or negative is asking
about the ARTIFACT rather than the respondent, and no rewording fixes that — see
docs/reference-statements.md.
"""
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from synthpanel import compose, config, dispatch, generate, personas, prompt  # noqa: E402

GATE = 0.70

REFEREE = """You are matching a quoted answer to whichever of five reference statements is closest in meaning.

The question the speaker was asked:
{question}

What the speaker actually said:
"{answer}"

The five reference statements:
{options}

Which single reference statement is closest to what the speaker expressed? Judge the
speaker's STANCE, not the topic — an answer can be about the same subject as a statement
while taking the opposite position on it.

Reply with nothing but one integer, 1 to 5, in a fenced json block: {{"choice": <integer>}}"""


def ranks(values):
    """Fractional ranks, so ties are handled. Referee scores are integers 1-5 and
    tie constantly; ranking them by position would invent an ordering that is not
    in the data and inflate the correlation."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    out = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        shared = (i + j) / 2.0
        for k in range(i, j + 1):
            out[order[k]] = shared
        i = j + 1
    return out


def spearman(a, b):
    """Pearson correlation of fractional ranks — Spearman, tie-correct."""
    if len(a) < 3:
        return None
    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return num / den if den else None


def load_rater(cfg):
    embedding = cfg.get("embedding", {})
    if not (embedding.get("endpoint") and embedding.get("model")):
        sys.exit("No embedding provider in config.toml. The rater under test needs one;\n"
                 "there is nothing to validate without it.")
    os.environ.setdefault("SSR_EMBED_ENDPOINT", embedding["endpoint"])
    os.environ.setdefault("SSR_EMBED_MODEL", embedding["model"])
    os.environ.setdefault("SSR_EMBED_KEY_ENV", embedding.get("api_key_env") or "")
    sys.path.insert(0, os.path.join(config.ROOT, "ssr"))
    import importlib
    return importlib.import_module("rate")


def elicit(cfg, roster, spec, stimulus, reps):
    """Run the real pipeline. Returns [(axis, prose)] across personas and reps."""
    jobs = {}
    for rep in range(reps):
        for persona in roster:
            jobs["{}#{}".format(persona["slug"], rep)] = prompt.build(persona, spec, stimulus)
    results = dispatch.run_all(
        cfg["dispatch"]["command"], jobs,
        max_parallel=cfg["dispatch"].get("max_parallel", 5),
        timeout=cfg["dispatch"].get("timeout_seconds", 420),
        prompt_via=cfg["dispatch"].get("prompt_via", "stdin"))
    cells, dropped = [], 0
    for label, result in results.items():
        parsed = dispatch.extract_json(result["stdout"])
        axes = (parsed or {}).get("axes") or {}
        if not axes:
            dropped += 1
            continue
        for axis, prose in axes.items():
            if isinstance(prose, str) and prose.strip():
                cells.append((axis, prose))
    return cells, dropped


def referee(cfg, cells, references, questions):
    """Score the same answers with a model shown the same five reference statements."""
    jobs = {}
    for index, (axis, prose) in enumerate(cells):
        options = "\n".join("{}. {}".format(i + 1, s) for i, s in enumerate(references[axis]))
        jobs[str(index)] = REFEREE.format(
            question=questions.get(axis, axis), answer=prose.replace('"', "'"),
            options=options)
    results = dispatch.run_all(
        cfg["dispatch"]["command"], jobs,
        max_parallel=cfg["dispatch"].get("max_parallel", 5),
        timeout=cfg["dispatch"].get("timeout_seconds", 420),
        prompt_via=cfg["dispatch"].get("prompt_via", "stdin"))
    scores = {}
    for label, result in results.items():
        parsed = dispatch.extract_json(result["stdout"]) or {}
        choice = parsed.get("choice")
        if isinstance(choice, int) and 1 <= choice <= 5:
            scores[int(label)] = choice
    return scores


def one_run(cfg, rater, roster, spec, stimulus, references, questions, reps):
    cells, dropped = elicit(cfg, roster, spec, stimulus, reps)
    cells = [(axis, prose) for axis, prose in cells if axis in references]
    if not cells:
        return None, "no ratable answers came back"

    # Batch across axes: rate() takes one answer per axis, so a call can carry one
    # cell from each axis at once. Every call re-embeds the reference statements, so grouping
    # cuts the embedding bill by roughly the number of axes.
    buckets = {}
    for index, (axis, prose) in enumerate(cells):
        buckets.setdefault(axis, []).append((index, prose))
    ssr = {}
    for position in range(max(len(v) for v in buckets.values())):
        batch = {axis: rows[position][1] for axis, rows in buckets.items()
                 if position < len(rows)}
        try:
            rated = rater.rate(batch, references)
        except rater.EmbeddingError as exc:
            return None, str(exc)
        for axis, result in rated.items():
            index = buckets[axis][position][0]
            # Expected value straight off the pmf: a bimodal cell returns
            # expected=None by design, and dropping it here would bias the sample
            # toward the answers that happened to be single-stance.
            ssr[index] = sum((k + 1) * p for k, p in enumerate(result["pmf"]))

    ref = referee(cfg, cells, references, questions)
    paired = sorted(set(ssr) & set(ref))
    if len(paired) < 3:
        return None, "only {} cells scored by both raters".format(len(paired))

    per_axis = {}
    for axis in sorted({cells[i][0] for i in paired}):
        idx = [i for i in paired if cells[i][0] == axis]
        per_axis[axis] = (spearman([ssr[i] for i in idx], [ref[i] for i in idx]), len(idx))
    measurable = [i for i in paired if per_axis[cells[i][0]][0] is not None]
    pooled = spearman([ssr[i] for i in measurable], [ref[i] for i in measurable])
    undefined = sorted(a for a, (rho, _) in per_axis.items() if rho is None)
    return {"pooled": pooled, "per_axis": per_axis, "n": len(measurable),
            "undefined": undefined, "dropped": dropped}, None


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--scenario", required=True)
    parser.add_argument("--stimulus", required=True)
    parser.add_argument("--reps", type=int, default=4, help="answers per persona per run")
    parser.add_argument("--size", type=int, default=3, help="personas per run")
    parser.add_argument("--runs", type=int, default=2, help="independent runs; 2 is the gate")
    parser.add_argument("--examples", action="store_true",
                        help="validate against the worked example pool")
    parser.add_argument("--cluster", action="append",
                        help="restrict the panel to these persona clusters (repeatable). "
                             "A rated scenario needs plausible respondents: asking an "
                             "outsider persona whether something maps to a job they are "
                             "doing produces a critique of the artifact, which this "
                             "method cannot rate.")
    parser.add_argument("--yes", action="store_true", help="skip the cost confirmation")
    args = parser.parse_args()

    cfg = config.load()
    if not cfg["dispatch"]["command"]:
        sys.exit("No dispatch command. Run `synth-panel detect` first.")
    spec = prompt.scenario(args.scenario)
    if not spec["reference_statements"]:
        sys.exit("Scenario '{}' ships no reference statements — it is qualitative by design, and\n"
                 "there is nothing here to validate.".format(args.scenario))

    stimulus_text = open(args.stimulus, encoding="utf-8").read().strip()
    generated, generated_path = generate.load(args.scenario, stimulus_text)
    if generated:
        references = generated
        source = os.path.relpath(generated_path, config.ROOT) + "  (written for this stimulus)"
    else:
        reference_path = os.path.join(config.ROOT, "reference-statements",
                                      spec["reference_statements"])
        raw = open(reference_path, encoding="utf-8").read()
        if "{{" in raw:
            sys.exit("{} still has unfilled placeholders, and no set has been written for\n"
                     "this stimulus. Write one first:\n\n"
                     "  python3 bin/synth-panel references --scenario {} --stimulus {}".format(
                         spec["reference_statements"], args.scenario, args.stimulus))
        references = {k: v for k, v in json.loads(raw).items() if not k.startswith("_")}
        source = "reference-statements/" + spec["reference_statements"] + "  (shipped, generic)"
    questions = {a["key"]: a["question"] for a in spec["axes"]}

    directory, is_example = personas.pool_dir(use_examples=args.examples)
    pool = personas.load_dir(directory)
    if args.cluster:
        wanted = {c.lower() for c in args.cluster}
        pool = [p for p in pool if (p.get("cluster") or "").lower() in wanted]
    if not pool:
        sys.exit("No personas. Build them first, or pass --examples.")
    if args.size > len(pool):
        sys.exit("Only {} personas match; --size {} cannot be drawn.".format(len(pool), args.size))

    stimulus = stimulus_text

    workers = args.size * args.reps
    calls = (workers + workers * len(references)) * args.runs
    print("scenario   : {} · axes {}".format(args.scenario, ", ".join(sorted(references))))
    print("testing    : {}".format(source))
    print("personas   : {} from {}{}".format(
        args.size, os.path.relpath(directory, config.ROOT),
        "  (a worked example, not your buyers)" if is_example else ""))
    print("plan       : {} runs x ({} answers + {} referee calls)".format(
        args.runs, workers, workers * len(references)))
    print("dispatches : ~{} agent calls (subscription usage, or credits if your CLI".format(calls))
    print("             is on API billing), plus a few cents of embeddings")
    if args.runs < 2:
        print("\nWARNING: one run is not evidence. A set has scored 0.53 and then 0.70")
        print("with nothing changed. --runs 2 is the gate for a reason.")
    if not args.yes:
        try:
            if input("\nproceed? [y/N] ").strip().lower() not in ("y", "yes"):
                sys.exit("stopped.")
        except EOFError:
            sys.exit("\nstopped (no tty — pass --yes to run unattended).")

    rater = load_rater(cfg)
    outcomes = []
    for run_index in range(args.runs):
        roster, _ = compose.compose(pool, size=args.size, record=False, seed=run_index)
        print("\nrun {} · {}".format(run_index + 1, ", ".join(p["slug"] for p in roster)))
        result, error = one_run(cfg, rater, roster, spec, stimulus, references, questions, args.reps)
        if error:
            print("  failed: {}".format(error))
            outcomes.append(None)
            continue
        outcomes.append(result)
        print("  pooled rho {:+.2f}  (n={}{})".format(
            result["pooled"], result["n"],
            ", {} answers unparsed".format(result["dropped"]) if result["dropped"] else ""))
        for axis, (rho, n) in sorted(result["per_axis"].items(),
                                     key=lambda kv: -(kv[1][0] if kv[1][0] is not None else -9)):
            if rho is None:
                print("    {:<24} UNDEFINED (n={}) <- every persona answered the same way, so "
                      "there is\n{:<28}nothing to correlate. This axis was not measured; the "
                      "panel\n{:<28}has no disagreement on it for this stimulus.".format(
                          axis, n, "", ""))
                continue
            note = ""
            if rho < 0.3:
                note = "  <- asks about the artifact, not the respondent?"
            print("    {:<24} {:+.2f}  (n={}){}".format(axis, rho, n, note))

    rhos = [o["pooled"] if o else None for o in outcomes]
    if generated:
        stamp = generate.record_gate(args.scenario, stimulus, rhos, GATE)
        if stamp:
            print("\nrecorded in {}".format(os.path.relpath(generated_path, config.ROOT)))

    stalled = sorted({a for o in outcomes if o for a in o.get("undefined", [])})
    if stalled:
        print("\nNOT MEASURED: {}. Every persona gave the same answer, so there was no".format(
            ", ".join(stalled)))
        print("ordering to check. That is a fact about your panel and this stimulus, not")
        print("about the reference statements — validate on something your personas would")
        print("genuinely split on, or the gate is measuring half an instrument.")

    passing = [o for o in outcomes if o and o["pooled"] is not None and o["pooled"] >= GATE]
    print("\n" + "=" * 62)
    if len(passing) == args.runs and args.runs >= 2:
        print("PASS — {} of {} runs cleared {:.2f}.".format(len(passing), args.runs, GATE))
        print("These references are checked against a model referee on this stimulus.")
        print("No human graded them. Say that when you report a distribution.")
    else:
        print("NOT PASSED — {} of {} runs cleared {:.2f}.".format(
            len(passing), args.runs, GATE))
        print("Do not ship distributions from this set. Either rework the references")
        print("(docs/reference-statements.md, the wording law) or drop the axis to free text.")
        print("An axis that fails on every rewording is asking about the artifact.")
    return 0 if len(passing) == args.runs and args.runs >= 2 else 1


if __name__ == "__main__":
    sys.exit(main())
