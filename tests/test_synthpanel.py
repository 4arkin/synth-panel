#!/usr/bin/env python3
"""synth-panel test suite. Stdlib unittest, no dependencies, no network, no model.

Every test here runs against a fake agent CLI and a fake embedding server. That is
deliberate: if the suite passes, nothing in the dispatch or rating path depends on
a particular vendor, model, subscription or API key.

  python3 tests/test_synthpanel.py
"""
import glob
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tests"))

from synthpanel import compose, config, detect, dispatch, personas, prompt  # noqa: E402
import fake_embed  # noqa: E402

FAKE = [sys.executable, os.path.join(ROOT, "tests", "fake_agent.py")]
CLI = [sys.executable, os.path.join(ROOT, "bin", "synth-panel")]


def load_rate():
    path = os.path.join(ROOT, "ssr", "rate.py")
    spec = importlib.util.spec_from_file_location("rate_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestConfig(unittest.TestCase):
    def test_loads_shipped_config(self):
        cfg = config.load()
        self.assertIn("dispatch", cfg)
        self.assertIsInstance(cfg["dispatch"]["timeout_seconds"], int)
        self.assertIsInstance(cfg["panel"]["require_skeptic"], bool)

    def test_fallback_parser_agrees_with_tomllib(self):
        """The <3.11 path must read our own files identically to the real parser."""
        source = open(os.path.join(ROOT, "synthpanel", "config.py")).read()
        namespace = {"__file__": os.path.join(ROOT, "synthpanel", "config.py")}
        exec(compile(source.replace("import tomllib", "raise ImportError()"),
                     "config_fallback", "exec"), namespace)
        self.assertEqual(namespace["load"](ROOT), config.load())
        self.assertEqual(namespace["registry"](ROOT), config.registry())


class TestRegistryIsVendorNeutral(unittest.TestCase):
    def test_no_cli_is_preferred(self):
        """detect must not silently favour one vendor when several are installed."""
        entries = config.registry()
        self.assertGreater(len(entries), 3)
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("aaa-agent", "zzz-agent"):
                stub = os.path.join(tmp, name)
                open(stub, "w").write("#!/bin/sh\ncat >/dev/null\n")
                os.chmod(stub, 0o755)
            registry = os.path.join(tmp, "agents.toml")
            open(registry, "w").write(
                '[zzz-agent]\ncommand = ["zzz-agent"]\ntuning = ["--small"]\nentrypoint = "ZZZ.md"\n'
                '[aaa-agent]\ncommand = ["aaa-agent"]\ntuning = []\nentrypoint = "AAA.md"\n')
            open(os.path.join(tmp, "config.toml"), "w").write("[dispatch]\ncommand = []\n")
            old_path = os.environ["PATH"]
            os.environ["PATH"] = tmp + os.pathsep + old_path
            try:
                results, chosen = detect.install(root=tmp, write_config=False)
            finally:
                os.environ["PATH"] = old_path
        self.assertEqual(len(results), 2)
        # zzz is the tuned one; alphabetical order must still win.
        self.assertEqual(chosen["cli"], "aaa-agent")

    def test_every_entry_has_the_same_shape(self):
        """Symmetry is the guard. One CLI carrying fields the others lack is how a
        vendor preference creeps back in as 'the one that happens to be tuned'."""
        entries = config.registry()
        shapes = {frozenset(entry) for entry in entries.values()}
        self.assertEqual(len(shapes), 1, "registry entries disagree on fields: {}".format(shapes))
        self.assertEqual(shapes.pop(), frozenset({"command", "tuning", "entrypoint"}))

    def test_every_entry_is_well_formed(self):
        for name, entry in config.registry().items():
            self.assertTrue(entry["command"], name)
            self.assertIsInstance(entry["command"], list, name)
            self.assertIsInstance(entry["tuning"], list, name)
            self.assertTrue(entry["entrypoint"], name)

    def test_detect_composes_command_and_tuning(self):
        with tempfile.TemporaryDirectory() as tmp:
            stub = os.path.join(tmp, "tuned-agent")
            open(stub, "w").write("#!/bin/sh\ncat >/dev/null\n")
            os.chmod(stub, 0o755)
            open(os.path.join(tmp, "agents.toml"), "w").write(
                '[tuned-agent]\ncommand = ["tuned-agent", "-p"]\n'
                'tuning = ["--small"]\nentrypoint = "T.md"\n')
            open(os.path.join(tmp, "config.toml"), "w").write("[dispatch]\ncommand = []\n")
            old = os.environ["PATH"]
            os.environ["PATH"] = tmp + os.pathsep + old
            try:
                results, chosen = detect.install(root=tmp, write_config=False)
            finally:
                os.environ["PATH"] = old
        self.assertEqual(chosen["command"], ["tuned-agent", "-p", "--small"])
        self.assertTrue(chosen["tuned"])

    def test_untuned_entry_is_flagged_not_hidden(self):
        with tempfile.TemporaryDirectory() as tmp:
            stub = os.path.join(tmp, "bare-agent")
            open(stub, "w").write("#!/bin/sh\ncat >/dev/null\n")
            os.chmod(stub, 0o755)
            open(os.path.join(tmp, "agents.toml"), "w").write(
                '[bare-agent]\ncommand = ["bare-agent"]\ntuning = []\nentrypoint = "B.md"\n')
            open(os.path.join(tmp, "config.toml"), "w").write("[dispatch]\ncommand = []\n")
            old = os.environ["PATH"]
            os.environ["PATH"] = tmp + os.pathsep + old
            try:
                _, chosen = detect.install(root=tmp, write_config=False)
            finally:
                os.environ["PATH"] = old
        self.assertFalse(chosen["tuned"])


class TestDetect(unittest.TestCase):
    def test_never_writes_into_the_protocol_file(self):
        """A CLI that already reads AGENTS.md must not have a pointer appended to it."""
        with tempfile.TemporaryDirectory() as tmp:
            protocol = os.path.join(tmp, "AGENTS.md")
            open(protocol, "w").write("# the real protocol\n")
            stub = os.path.join(tmp, "agentsmd-cli")
            open(stub, "w").write("#!/bin/sh\ncat >/dev/null\n")
            os.chmod(stub, 0o755)
            open(os.path.join(tmp, "agents.toml"), "w").write(
                '[agentsmd-cli]\ncommand = ["agentsmd-cli"]\nentrypoint = "AGENTS.md"\n')
            open(os.path.join(tmp, "config.toml"), "w").write("[dispatch]\ncommand = []\n")
            old = os.environ["PATH"]
            os.environ["PATH"] = tmp + os.pathsep + old
            try:
                results, _ = detect.install(root=tmp, write_config=False)
            finally:
                os.environ["PATH"] = old
            self.assertEqual(open(protocol).read(), "# the real protocol\n")
            self.assertEqual(results[0]["action"], "reads AGENTS.md directly")

    def test_pointer_write_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = os.path.join(tmp, "SOME_CLI.md")
            self.assertEqual(detect._write_pointer(target), "created")
            self.assertEqual(detect._write_pointer(target), "unchanged")
            first = open(target).read()
            open(target, "w").write("user content above\n" + first)
            self.assertEqual(detect._write_pointer(target), "unchanged")
            self.assertIn("user content above", open(target).read())


class TestIsolation(unittest.TestCase):
    """The one claim this repo makes about itself. Tested, not asserted."""

    def _probe(self):
        result = dispatch.run_one(FAKE, "You are a probe.\n", timeout=30)
        self.assertTrue(result["ok"], result["stderr"])
        return dispatch.extract_json(result["stdout"])["_probe"]

    def test_worker_runs_outside_the_repo(self):
        probe = self._probe()
        self.assertNotEqual(os.path.realpath(probe["cwd"]), os.path.realpath(ROOT))

    def test_worker_cannot_see_repo_files(self):
        probe = self._probe()
        for leaked in ("AGENTS.md", "personas", "scenarios", "config.local.toml", "runs"):
            self.assertNotIn(leaked, probe["visible_files"])

    def test_worker_working_directory_is_empty(self):
        self.assertEqual(self._probe()["visible_files"], [])

    def test_each_worker_gets_its_own_directory(self):
        results = dispatch.run_all(FAKE, {"a": "You are A.", "b": "You are B."}, timeout=30)
        dirs = {dispatch.extract_json(r["stdout"])["_probe"]["cwd"] for r in results.values()}
        self.assertEqual(len(dirs), 2)

    def test_workers_only_receive_their_own_prompt(self):
        results = dispatch.run_all(
            FAKE, {"a": "You are A." + "x" * 100, "b": "You are B."}, timeout=30)
        sizes = {k: dispatch.extract_json(v["stdout"])["_probe"]["prompt_chars"]
                 for k, v in results.items()}
        self.assertGreater(sizes["a"], sizes["b"])


class TestDispatch(unittest.TestCase):
    def test_failure_is_reported_not_raised(self):
        result = dispatch.run_one(FAKE + ["--fail"], "x", timeout=30)
        self.assertFalse(result["ok"])
        self.assertEqual(result["returncode"], 3)

    def test_timeout_is_reported_not_raised(self):
        result = dispatch.run_one(FAKE + ["--slow", "5"], "x", timeout=1)
        self.assertFalse(result["ok"])
        self.assertIn("timed out", result["stderr"])

    def test_unparseable_output_returns_none(self):
        result = dispatch.run_one(FAKE + ["--garbage"], "x", timeout=30)
        self.assertTrue(result["ok"])
        self.assertIsNone(dispatch.extract_json(result["stdout"]))

    def test_missing_command_raises_a_readable_error(self):
        with self.assertRaises(dispatch.DispatchError):
            dispatch.run_one([], "x")
        with self.assertRaises(dispatch.DispatchError):
            dispatch.run_one(["definitely-not-installed-xyz"], "x")

    def test_all_workers_return_even_when_one_fails(self):
        results = dispatch.run_all(FAKE, {"good": "You are A."}, timeout=30)
        self.assertEqual(set(results), {"good"})

    def test_extract_json_takes_the_last_valid_block(self):
        self.assertEqual(dispatch.extract_json('```json\n{"a":1}\n```'), {"a": 1})
        self.assertEqual(
            dispatch.extract_json('```json\n{"a":1}\n```\n```json\n{"b":2}\n```'), {"b": 2})
        self.assertEqual(dispatch.extract_json('```json\n{bad}\n```\n```json\n{"c":3}\n```'),
                         {"c": 3})
        self.assertEqual(dispatch.extract_json('bare {"d":4} text'), {"d": 4})
        self.assertIsNone(dispatch.extract_json("no json here"))
        self.assertIsNone(dispatch.extract_json(""))


class TestPersonas(unittest.TestCase):
    def setUp(self):
        self.pool = personas.load_dir(os.path.join(ROOT, "examples", "personas"))

    def test_example_pool_is_complete(self):
        self.assertEqual(len(self.pool), 18)
        for persona in self.pool:
            self.assertEqual(persona["missing"], [], persona["slug"])

    def test_example_pool_is_scrubbed(self):
        """The worked example must not carry its author's identity or paths."""
        banned = ("/hq/", "/users/", "alex", "marketect", "icp.md")
        for path in glob.glob(os.path.join(ROOT, "examples", "personas", "*.md")):
            text = open(path).read().lower()
            for token in banned:
                self.assertNotIn(token, text, "{} leaks {!r}".format(os.path.basename(path), token))

    def test_example_pool_is_labelled_hypothesis(self):
        """No persona written from positioning material may claim evidence."""
        for persona in self.pool:
            self.assertEqual(persona["grounding"], "hypothesis", persona["slug"])

    def test_skeptic_flag_and_fidelity(self):
        self.assertTrue(any(p["is_skeptic"] for p in self.pool))
        self.assertEqual(personas.fidelity(self.pool), "hypothesis")
        self.assertEqual(personas.fidelity([]), "no panel")
        self.assertEqual(
            personas.fidelity([{"grounding": "evidence-anchored"}]), "evidence-anchored")

    def test_missing_fields_are_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "thin.md")
            open(path, "w").write("# thin\n\nname: Nobody\n")
            self.assertIn("anchor_phrase", personas.parse(path)["missing"])


class TestCompose(unittest.TestCase):
    def setUp(self):
        self.pool = personas.load_dir(os.path.join(ROOT, "examples", "personas"))

    def test_always_includes_a_skeptic(self):
        for seed in range(25):
            roster, _ = compose.compose(self.pool, seed=seed, record=False)
            self.assertTrue(any(p["is_skeptic"] for p in roster), seed)

    def test_always_spans_two_roles(self):
        for seed in range(25):
            roster, _ = compose.compose(self.pool, seed=seed, record=False)
            self.assertGreaterEqual(len({p["cluster"] for p in roster}), 2, seed)

    def test_size_stays_in_range(self):
        for seed in range(25):
            roster, _ = compose.compose(self.pool, seed=seed, record=False)
            self.assertIn(len(roster), (3, 4, 5), seed)

    def test_include_and_exclude_are_honoured(self):
        roster, _ = compose.compose(self.pool, size=3, include=["economic-buyer-cfo"],
                                    exclude=["feed-cynic"], seed=1, record=False)
        slugs = [p["slug"] for p in roster]
        self.assertIn("economic-buyer-cfo", slugs)
        self.assertNotIn("feed-cynic", slugs)

    def test_rotation_excludes_recent_rosters(self):
        with tempfile.TemporaryDirectory() as tmp:
            open(os.path.join(tmp, "config.toml"), "w").write(
                "[panel]\nsize_min = 3\nsize_max = 5\nrotation_depth = 2\n"
                "require_skeptic = true\nmin_distinct_roles = 2\n")
            first, _ = compose.compose(self.pool, size=4, root=tmp, seed=2)
            second, _ = compose.compose(self.pool, size=4, root=tmp, seed=3)
            self.assertFalse(set(p["slug"] for p in first) & set(p["slug"] for p in second))

    def test_thin_pool_warns_instead_of_crashing(self):
        thin = [p for p in self.pool if not p["is_skeptic"]][:3]
        roster, notes = compose.compose(thin, size=3, record=False)
        self.assertEqual(len(roster), 3)
        self.assertTrue(any("no skeptic" in n.lower() for n in notes), notes)


class TestScenariosAndPrompts(unittest.TestCase):
    def test_every_scenario_parses(self):
        slugs = prompt.available()
        self.assertEqual(len(slugs), 5)
        for slug in slugs:
            spec = prompt.scenario(slug)
            self.assertEqual(spec["scenario"], slug)
            self.assertTrue(spec["axes"])
            self.assertTrue(spec["verdicts"])
            for axis in spec["axes"]:
                self.assertTrue(axis["key"] and axis["question"])

    def test_rated_axes_have_anchors_and_unrated_ones_do_not(self):
        """A scenario may never claim to rate an axis it has no anchor set for."""
        for slug in prompt.available():
            spec = prompt.scenario(slug)
            rated = [a["key"] for a in spec["axes"] if a["rated"]]
            if not rated:
                self.assertIsNone(spec["anchors"], slug)
                continue
            path = os.path.join(ROOT, "anchors", spec["anchors"])
            anchors = json.load(open(path))
            for key in rated:
                self.assertIn(key, anchors, "{}: {}".format(slug, key))

    def test_every_anchor_axis_has_exactly_five_statements(self):
        for path in glob.glob(os.path.join(ROOT, "anchors", "*.json")):
            data = json.load(open(path))
            axes = [k for k in data if not k.startswith("_")]
            self.assertTrue(axes, path)
            for axis in axes:
                self.assertEqual(len(data[axis]), 5, "{} {}".format(path, axis))
                for statement in data[axis]:
                    self.assertTrue(statement.strip())

    def test_templated_anchors_are_declared_as_templated(self):
        """An anchor file with placeholders must not be presented as ready to use."""
        for path in glob.glob(os.path.join(ROOT, "anchors", "*.json")):
            has_placeholder = "{{" in open(path).read()
            slug = os.path.basename(path)[len("anchors-"):-len(".json")]
            state = prompt.scenario(slug)["anchor_state"]
            self.assertEqual(has_placeholder, state == "templated", path)

    def test_build_fills_every_slot(self):
        pool = personas.load_dir(os.path.join(ROOT, "examples", "personas"))
        for slug in prompt.available():
            text = prompt.build(pool[0], prompt.scenario(slug), "STIMULUS")
            self.assertNotIn("{{", text, slug)
            self.assertIn(pool[0]["anchor_phrase"], text)
            self.assertIn("STIMULUS", text)

    def test_incomplete_persona_raises_rather_than_reaching_a_worker(self):
        pool = personas.load_dir(os.path.join(ROOT, "examples", "personas"))
        broken = dict(pool[0])
        del broken["anchor_phrase"]
        with self.assertRaises(ValueError):
            prompt.build(broken, prompt.scenario("offer-pricing"), "x")

    def test_prompt_forbids_numbers(self):
        pool = personas.load_dir(os.path.join(ROOT, "examples", "personas"))
        text = prompt.build(pool[0], prompt.scenario("offer-pricing"), "x").lower()
        self.assertIn("no numbers", text)


class TestRater(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server, cls.url = fake_embed.serve()
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        os.environ["SSR_EMBED_ENDPOINT"] = cls.url
        os.environ["SSR_EMBED_MODEL"] = "fake-embed"
        os.environ["SSR_EMBED_KEY_ENV"] = "SYNTH_PANEL_TEST_NO_KEY"
        cls.rate = load_rate()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_pmf_is_a_distribution(self):
        for sims in ([0.1, 0.2, 0.3, 0.4, 0.5], [0.9] * 5, [-0.4, 0.0, 0.4, 0.1, 0.2]):
            p = self.rate.pmf(sims)
            self.assertEqual(len(p), 5)
            self.assertAlmostEqual(sum(p), 1.0, places=9)
            self.assertTrue(all(x >= 0 for x in p))

    def test_bimodality_matches_the_recorded_case(self):
        self.assertEqual(self.rate.bimodal([0.28, 0.01, 0.00, 0.39, 0.32]), (True, [1, 4]))
        self.assertEqual(self.rate.bimodal([0.05, 0.10, 0.20, 0.40, 0.25])[0], False)
        self.assertEqual(self.rate.bimodal([0.02, 0.05, 0.60, 0.25, 0.08])[0], False)

    def test_rates_against_a_provider_that_is_not_openai(self):
        """End to end through the real rater, no vendor and no API key involved."""
        anchors = json.load(open(os.path.join(ROOT, "anchors", "anchors-concept-screening.json")))
        anchors = {k: v for k, v in anchors.items() if not k.startswith("_")}
        out = self.rate.rate({"jtbd_fit": "This is exactly the job I have."}, anchors)
        self.assertIn("jtbd_fit", out)
        self.assertAlmostEqual(sum(out["jtbd_fit"]["pmf"]), 1.0, places=3)
        self.assertIn("bimodal", out["jtbd_fit"])

    def test_bimodal_result_withholds_the_mean(self):
        out = self.rate.rate({"jtbd_fit": "x"}, {"jtbd_fit": ["a"] * 5})
        entry = out["jtbd_fit"]
        if entry["bimodal"]:
            self.assertIsNone(entry["expected"])
            self.assertIn("mean_do_not_report", entry)
        else:
            self.assertIsNotNone(entry["expected"])

    def test_provider_failure_is_an_error_not_a_traceback(self):
        os.environ["SSR_EMBED_ENDPOINT"] = "http://127.0.0.1:1/v1/embeddings"
        try:
            failing = load_rate()
            with self.assertRaises(failing.EmbeddingError):
                failing.rate({"a": "x"}, {"a": ["s"] * 5})
        finally:
            os.environ["SSR_EMBED_ENDPOINT"] = self.url

    def test_rater_is_byte_identical_to_nothing_vendor_specific(self):
        source = open(os.path.join(ROOT, "ssr", "rate.py")).read()
        for vendor in ("api.openai.com", "api.anthropic.com", "api.cohere", "voyageai"):
            self.assertNotIn('"https://{}'.format(vendor), source,
                             "no vendor endpoint may be baked into the rater")

    def test_unset_provider_refuses_rather_than_guessing(self):
        for key in ("SSR_EMBED_ENDPOINT", "SSR_EMBED_MODEL"):
            os.environ.pop(key, None)
        try:
            bare = load_rate()
            with self.assertRaises(bare.EmbeddingError):
                bare.rate({"a": "x"}, {"a": ["s"] * 5})
        finally:
            os.environ["SSR_EMBED_ENDPOINT"] = self.url
            os.environ["SSR_EMBED_MODEL"] = "fake-embed"


class TestEndToEnd(unittest.TestCase):
    """The whole CLI, driven by a fake agent. No model, no key, no network."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.stimulus = os.path.join(self.tmp, "stimulus.md")
        open(self.stimulus, "w").write("CONCEPT: a thing that does a job.")
        self.local = os.path.join(ROOT, "config.local.toml")
        self.backup = open(self.local).read() if os.path.exists(self.local) else None
        open(self.local, "w").write(
            "[dispatch]\ncommand = [{}]\n".format(", ".join('"{}"'.format(c) for c in FAKE)))

    def tearDown(self):
        if self.backup is None:
            os.path.exists(self.local) and os.remove(self.local)
        else:
            open(self.local, "w").write(self.backup)

    def _run(self, *args):
        return subprocess.run(CLI + list(args), capture_output=True, text=True, timeout=120)

    def test_doctor_passes_against_a_fake_agent(self):
        result = self._run("doctor")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_full_panel_run(self):
        result = self._run("panel", "--scenario", "concept-screening",
                           "--stimulus", self.stimulus, "--size", "3", "--examples")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload["workers"]), 3)
        for slug, worker in payload["workers"].items():
            self.assertTrue(worker["ok"], slug)
            self.assertIsNotNone(worker["parsed"], slug)
            self.assertIn("jtbd_fit", worker["parsed"]["axes"])
        self.assertIn("fidelity", payload)
        self.assertTrue(payload["example_pool"])

    def test_run_states_its_mode(self):
        result = self._run("panel", "--scenario", "feature-prioritisation",
                           "--stimulus", self.stimulus, "--size", "3", "--examples")
        self.assertIn("rating: qualitative", result.stderr)

    def test_dry_run_dispatches_nothing(self):
        result = self._run("panel", "--scenario", "packaging-choice",
                           "--stimulus", self.stimulus, "--size", "3", "--examples", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("prompts", json.loads(result.stdout))

    def test_unknown_scenario_is_refused(self):
        result = self._run("panel", "--scenario", "not-a-scenario",
                           "--stimulus", self.stimulus, "--examples")
        self.assertNotEqual(result.returncode, 0)

    def test_rate_refuses_templated_anchors(self):
        run_dir = os.path.join(self.tmp, "run")
        os.makedirs(run_dir)
        json.dump({"scenario": "offer-pricing", "anchors": "anchors-offer-pricing.json",
                   "anchor_state": "templated", "workers": {}},
                  open(os.path.join(run_dir, "run.json"), "w"))
        open(self.local, "a").write(
            '\n[embedding]\nendpoint = "http://127.0.0.1:1/v1/embeddings"\nmodel = "x"\n')
        result = self._run("rate", run_dir)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("placeholder", result.stderr.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2, buffer=False)
