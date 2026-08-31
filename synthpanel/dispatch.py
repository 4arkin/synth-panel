"""One persona, one process.

This is the load-bearing part of the repo. The common approach to an "AI focus
group" is one model role-playing five people inside one context; those five
cannot genuinely disagree, and their agreement is an artifact of sharing a
context. Here each persona is a separate subprocess with a separate working
directory, so it cannot see the stimulus's other readers, the repo, or the
orchestrator's reasoning. Agreement across them is evidence.

Isolation this module provides:
  - separate OS process per persona
  - separate empty working directory per persona (no project files in scope)
  - no shared state; the only input is the prompt written to stdin

Isolation it does NOT provide: user-level agent configuration (a global
CLAUDE.md, AGENTS.md or equivalent in the user's home directory) is still read
by the CLI. Said plainly in docs/rules.md rather than papered over.
"""
import json
import re
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


class DispatchError(RuntimeError):
    pass


def run_one(command, prompt, timeout=420):
    """Run a single persona. Never raises for the persona's own failure."""
    if not command:
        raise DispatchError(
            "No dispatch command configured. Run `synth-panel detect`, or set "
            "[dispatch].command in config.toml.")
    started = time.time()
    with tempfile.TemporaryDirectory(prefix="synth-panel-") as workdir:
        try:
            proc = subprocess.run(
                list(command),
                input=prompt,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=workdir,
            )
            return {
                "ok": proc.returncode == 0,
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "seconds": round(time.time() - started, 1),
            }
        except subprocess.TimeoutExpired:
            return {
                "ok": False,
                "returncode": None,
                "stdout": "",
                "stderr": "timed out after {}s".format(timeout),
                "seconds": round(time.time() - started, 1),
            }
        except FileNotFoundError as exc:
            raise DispatchError(
                "Dispatch command not found: {}. Run `synth-panel detect`.".format(command[0])
            ) from exc


def run_all(command, prompts, max_parallel=5, timeout=420):
    """Dispatch every persona at once. `prompts` is {label: prompt}.

    Order of completion is irrelevant and deliberately not reported — nothing
    downstream may depend on which persona answered first.
    """
    results = {}
    with ThreadPoolExecutor(max_workers=max(1, int(max_parallel))) as pool:
        futures = {
            pool.submit(run_one, command, prompt, timeout): label
            for label, prompt in prompts.items()
        }
        for future in futures:
            label = futures[future]
            results[label] = future.result()
    return results


def extract_json(text):
    """The last fenced JSON object in a worker's output, or None.

    Agent CLIs wrap answers in prose and sometimes in several code blocks. The
    contract says the answer is the last one, so a worker that thinks out loud
    first still parses.
    """
    if not text:
        return None
    matches = FENCE.findall(text)
    if not matches:
        matches = re.findall(r"(\{.*\})", text, re.DOTALL)
    for candidate in reversed(matches):
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    return None
