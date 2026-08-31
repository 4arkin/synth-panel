#!/usr/bin/env python3
"""SSR rater — free text -> Likert distribution. Stdlib only.

Usage:
  echo '{"perceived_likelihood": "I am skeptical this ships in a month."}' \
    | python3 rate.py anchors-offers.json

Reads one JSON object of {axis: free-text} on stdin, writes
{axis: {pmf, expected, bimodal, modes}} on stdout.

WHY EMBEDDING AND NOT A NUMBER: asking an LLM persona for a 1-5 integer produces compressed,
midpoint-regressing distributions (arXiv:2510.08338). Measured on this skill's own prompt:
85% of scores were 2 or 3, a 5 never appeared once, and 4 of 12 persona-axis cells returned the
IDENTICAL integer across 8 independent samples.

NO VENDOR IS THE DEFAULT. There is no fallback endpoint: if you do not name one, this
refuses to guess. Any OpenAI-compatible /embeddings endpoint works, including a local one.
  SSR_EMBED_ENDPOINT  required — e.g. http://localhost:11434/v1/embeddings
  SSR_EMBED_MODEL     required — e.g. nomic-embed-text
  SSR_EMBED_KEY_ENV   optional — the NAME of the env var holding a key, if the endpoint
                      needs one at all. A local endpoint needs none.

BIMODALITY. A response in a concession shape ("yes I want this, BUT the framing is vocabulary")
puts mass at both ends and the mean lands in the middle, describing a position nobody held.
Measured 2026-08-18: 6 of 20 axis-cells split this way on the first live run. When that happens
`expected` is null and the two modes are reported instead. The mean of a bimodal PMF is not a reading.
"""
import os, sys, json, math, urllib.error, urllib.request

class EmbeddingError(RuntimeError):
    """The provider failed. Never a reason to guess a number instead."""


TAU = 0.5   # softmax temperature over z-scored similarities
TAIL = 0.25  # min mass at BOTH ends before a distribution counts as bimodal
MID = 0.20  # max mass in the middle for the same

ENDPOINT = os.environ.get("SSR_EMBED_ENDPOINT", "")
MODEL = os.environ.get("SSR_EMBED_MODEL", "")
KEY_ENV = os.environ.get("SSR_EMBED_KEY_ENV", "")


def embed(texts, model=MODEL, endpoint=ENDPOINT):
    if not endpoint or not model:
        raise EmbeddingError(
            "No embedding provider named. Set SSR_EMBED_ENDPOINT and SSR_EMBED_MODEL, or "
            "[embedding] in config.toml. There is no default on purpose — this repo does "
            "not pick a vendor for you.")
    headers = {"Content-Type": "application/json"}
    key = os.environ.get(KEY_ENV) if KEY_ENV else None
    if key:
        headers["Authorization"] = "Bearer " + key
    req = urllib.request.Request(
        endpoint,
        data=json.dumps({"model": model, "input": texts}).encode(),
        headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            d = json.load(r)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise EmbeddingError(
            "Embedding provider returned HTTP {} from {}.\n{}\n"
            "Nothing is broken in the panel itself — rerun without rating, or fix the "
            "provider. The qualitative output is most of the value.".format(
                exc.code, endpoint, detail)) from None
    except urllib.error.URLError as exc:
        raise EmbeddingError(
            "Could not reach the embedding provider at {} ({}).".format(endpoint, exc.reason)
        ) from None
    return [e["embedding"] for e in sorted(d["data"], key=lambda x: x["index"])]

def cos(a, b):
    return sum(x*y for x, y in zip(a, b)) / (
        math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(y*y for y in b)))

def pmf(sims, tau=TAU):
    m = sum(sims)/len(sims)
    var = sum((s-m)**2 for s in sims)/len(sims)
    sd = math.sqrt(var) or 1e-9
    e = [math.exp(((s-m)/sd)/tau) for s in sims]
    t = sum(e)
    return [x/t for x in e]

def bimodal(p):
    """True when mass sits at both ends with a hollow middle. Returns (flag, modes)."""
    low, high, mid = p[0] + p[1], p[3] + p[4], p[2]
    if min(low, high) >= TAIL and mid <= MID:
        return True, [1 + p.index(max(p[:2])), 4 + p[3:].index(max(p[3:]))]
    return False, []

def rate(responses, anchors):
    axes = [a for a in responses if a in anchors]
    flat, idx = [], {}
    for ax in axes:
        for i, s in enumerate(anchors[ax]):
            idx[(ax, i)] = len(flat); flat.append(s)
    vecs = embed(flat + [responses[ax] for ax in axes])
    av, rv = vecs[:len(flat)], vecs[len(flat):]
    out = {}
    for ax, v in zip(axes, rv):
        sims = [cos(v, av[idx[(ax, i)]]) for i in range(5)]
        p = pmf(sims)
        split, modes = bimodal(p)
        mean = round(sum((i+1)*x for i, x in enumerate(p)), 2)
        out[ax] = {"pmf": [round(x, 4) for x in p],
                   "expected": None if split else mean,
                   "bimodal": split,
                   "modes": modes}
        if split:
            # Kept for inspection only. Reporting it as a reading is the failure this flag exists to stop.
            out[ax]["mean_do_not_report"] = mean
    return out

if __name__ == "__main__":
    anchors = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), sys.argv[1])))
    try:
        json.dump(rate(json.load(sys.stdin), anchors), sys.stdout, indent=1)
    except EmbeddingError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
    print()
