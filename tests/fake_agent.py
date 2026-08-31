#!/usr/bin/env python3
"""A fake agent CLI. Reads a prompt on stdin, writes an answer on stdout.

This is the whole contract the dispatcher depends on, which is the point: the
test suite drives synth-panel with something that is not a language model at all.
If the tests pass against this, nothing in the dispatch path is tied to a vendor,
a model, or a subscription.

It also reports what it can see from inside its own process, which is how the
isolation claim gets tested rather than asserted.

  --fail       exit non-zero, to exercise the failure path
  --garbage    emit no JSON, to exercise the unparseable path
  --slow N     sleep N seconds, to exercise the timeout path
"""
import json
import os
import sys
import time

argv = sys.argv[1:]
if "--fail" in argv:
    sys.stderr.write("fake agent failing on purpose\n")
    sys.exit(3)
if "--slow" in argv:
    time.sleep(float(argv[argv.index("--slow") + 1]))

prompt = sys.stdin.read()

if '{"ok": true}' in prompt:
    # The `doctor` probe asks for exactly this. A real agent would comply; so does this.
    print("```json")
    print(json.dumps({"ok": True}))
    print("```")
    sys.exit(0)

if "--garbage" in argv:
    print("I am prose and I contain no JSON object whatsoever.")
    sys.exit(0)

# Everything the persona can actually reach from inside its own process.
answer = {
    "verdict": "partial",
    "axes": {},
    "reaction": "This is a fixed answer from a fake agent.",
    "friction": "none, this is a test double",
    "unsaid": "nothing",
    "headline": "fake agent answer",
    "_probe": {
        "cwd": os.getcwd(),
        "visible_files": sorted(os.listdir(".")),
        "prompt_chars": len(prompt),
        "saw_persona_name": "You are " in prompt,
    },
}
# Echo back whichever axis keys the prompt asked for, so prompt assembly is testable.
for line in prompt.splitlines():
    line = line.strip()
    if line[:1].isdigit() and " — " in line:
        key = line.split(".", 1)[1].split(" — ")[0].strip()
        answer["axes"][key] = "prose answer for {}".format(key)

print("Some preamble the agent felt like writing first.")
print("```json")
print(json.dumps(answer, indent=1))
print("```")
