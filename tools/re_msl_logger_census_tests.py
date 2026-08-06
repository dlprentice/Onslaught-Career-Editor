#!/usr/bin/env python3
"""Focused parser, identity, join, and optional publication tests."""

from __future__ import annotations

import csv
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import warnings


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/re_msl_logger_census.py"
SPEC = importlib.util.spec_from_file_location("re_msl_logger_census", TOOL)
assert SPEC is not None and SPEC.loader is not None
census = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = census
SPEC.loader.exec_module(census)
EVIDENCE_VALUE = os.environ.get("BEA_MSL_LOGGER_EVIDENCE_REPO", str(ROOT))
EVIDENCE_ROOT = Path(EVIDENCE_VALUE).resolve()
BUNDLE_VALUE = os.environ.get("BEA_MSL_LOGGER_CENSUS_BUNDLE", "")
LOCAL_BUNDLE = ROOT / "local-lab/msl-logger-census-2026-08-03-v2-ready"
BUNDLE = Path(BUNDLE_VALUE).absolute() if BUNDLE_VALUE else (LOCAL_BUNDLE if LOCAL_BUNDLE.is_dir() else None)


def registry_rows() -> list[dict[str, object]]:
    return [
        {"index": 0, "name": "Print", "handler": 0x00537AD0},
        {"index": 1, "name": "Pause", "handler": 0x00537C70},
        {"index": 2, "name": "SetHealth", "handler": 0x00535C10},
    ]


def synthetic_bundle(root: Path, *, owner: bytes | None = None, ready: bytes | None = None) -> Path:
    root.mkdir(parents=True)
    bundle = root / "bundle"
    bundle.mkdir()
    for name in census.OUTPUTS:
        (bundle / name).write_bytes(b"")
    (bundle / "msl-logger-census-owner.py").write_bytes(TOOL.read_bytes() if owner is None else owner)
    (bundle / "READY.json").write_bytes(census.canonical_json({}) if ready is None else ready)
    return bundle


class LexerTests(unittest.TestCase):
    def registry(self) -> dict[str, dict[str, object]]:
        return {str(row["name"]): row for row in registry_rows()}

    def test_comments_and_string_contents_are_not_calls(self) -> None:
        text = r'''
// Print("comment");
/* Pause(99); Print("block"); */
init()
{
    Print("literal Pause(1) // still a string");
    Pause(1.0);
}
event("game playing")
{
    Print(value);
}
died()
{
    SetHealth(0.0);
}
'''
        calls = census.parse_file_calls(text, "Level100/probe.msl", self.registry())
        self.assertEqual(["Print", "Pause", "Print", "SetHealth"], [row["nativeName"] for row in calls])
        self.assertEqual(
            [("init", "init"), ("init", "init"), ("event", "game playing"), ("actor-handler", "died")],
            [(row["scopeKind"], row["scopeName"]) for row in calls],
        )

    def test_numeric_operator_adjacency_does_not_swallow_nested_native(self) -> None:
        calls = census.parse_file_calls("init(){ Print(1+Pause(2)); }", "Level100/a.msl", self.registry())
        self.assertEqual(["Print", "Pause"], [row["nativeName"] for row in calls])
        self.assertEqual("1+Pause(2)", calls[0]["argumentText"])
        self.assertEqual("2", calls[1]["argumentText"])

    def test_expression_text_is_exact_after_edge_trim_only(self) -> None:
        calls = census.parse_file_calls("init(){ Print(  value + GetX(foo)  ); }", "Level100/a.msl", self.registry())
        self.assertEqual("value + GetX(foo)", calls[0]["argumentText"])
        self.assertEqual(census.sha256_bytes(b"value + GetX(foo)"), calls[0]["argumentSha256"])
        self.assertEqual(len(b"value + GetX(foo)"), calls[0]["argumentBytes"])

    def test_escaped_quote_does_not_end_string(self) -> None:
        calls = census.parse_file_calls('init(){ Print("one \\\"quoted\\\" Pause(9)"); }', "Level001/a.msl", self.registry())
        self.assertEqual(1, len(calls))
        self.assertEqual('"one \\\"quoted\\\" Pause(9)"', calls[0]["literalValueJson"])

    def test_unterminated_constructs_refuse(self) -> None:
        for source, message in (("/* nope", "block comment"), ('Print("nope)', "string literal"), ("init(){", "opening brace")):
            with self.subTest(source=source), self.assertRaisesRegex(census.CensusError, message):
                census.discover_scopes(census.lex_msl(source))


class CanonicalOutputTests(unittest.TestCase):
    def test_tsv_and_json_canonical_forms(self) -> None:
        self.assertEqual(b"a\tb\nx\ty\n", census.render_tsv(("a", "b"), [{"a": "x", "b": "y"}]))
        self.assertEqual(b'{\n  "a": 1,\n  "z": 2\n}\n', census.canonical_json({"z": 2, "a": 1}))

    def test_level_key_is_case_insensitive_and_fixed_width(self) -> None:
        self.assertEqual("003", census.level_key("level003/a.msl"))
        self.assertEqual("611", census.level_key("Level611/a.msl"))
        self.assertEqual("ROOT", census.level_key("level3/a.msl"))

    def test_structural_attacks_need_no_local_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            owner_attack = synthetic_bundle(
                root / "owner",
                owner=TOOL.read_bytes() + b"# self-restamped mutation\n",
            )
            with self.assertRaisesRegex(census.CensusError, "frozen owner differs"):
                census.verify_bundle(owner_attack, TOOL)

            directory_attack = synthetic_bundle(root / "directory")
            (directory_attack / "undeclared").mkdir()
            with self.assertRaisesRegex(census.CensusError, "bundle members differ"):
                census.validate_bundle_tree(directory_attack)

            canonical_attack = synthetic_bundle(root / "canonical", ready=b"{}")
            with self.assertRaisesRegex(census.CensusError, "not canonical JSON"):
                census.verify_bundle(canonical_attack, TOOL)

    @unittest.skipUnless(os.name == "nt" and hasattr(Path, "is_junction"), "Windows junctions unavailable")
    def test_cli_rejects_root_junction_before_resolution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = synthetic_bundle(root / "target")
            junction = root / "bundle-junction"
            created = subprocess.run(
                ["cmd.exe", "/d", "/c", "mklink", "/J", str(junction), str(target)],
                capture_output=True, text=True, check=False,
            )
            if created.returncode != 0 or not junction.is_junction():
                self.skipTest(f"cannot create a test junction: {created.stderr.strip()}")
            try:
                result = subprocess.run(
                    [sys.executable, "-B", str(TOOL), "verify", "--bundle", str(junction)],
                    capture_output=True, text=True, check=False,
                )
                self.assertEqual(2, result.returncode)
                self.assertIn("reparse point", result.stderr)
            finally:
                os.rmdir(junction)

    def test_build_verifies_staging_before_publication(self) -> None:
        outputs = {name: name.encode("ascii") for name in census.OUTPUTS if name != "msl-logger-census-owner.py"}
        summary = {"schema": census.SCHEMA, "counts": {"corpusFiles": 0}, "inputs": {}}
        original_write = Path.write_bytes

        def poisoned_write(path: Path, data: bytes) -> int:
            if path.name == "native-summary.tsv":
                data += b"poison"
            return original_write(path, data)

        with tempfile.TemporaryDirectory() as temporary:
            out = Path(temporary) / "published"
            with (
                mock.patch.object(census, "analyze", return_value=(outputs, summary)),
                mock.patch.object(Path, "write_bytes", poisoned_write),
                self.assertRaisesRegex(census.CensusError, "published output differs"),
            ):
                census.build_bundle(out, TOOL)
            self.assertFalse(out.exists())
            self.assertEqual([], list(out.parent.glob(f".{out.name}-*")))


class ExactIdentityTests(unittest.TestCase):
    def test_same_count_source_drift_is_refused(self) -> None:
        census.validate_corpus_pin(census.EXPECTED_CORPUS_MANIFEST_SHA256, census.EXPECTED_CORPUS_FILES)
        poisoned = "0" + census.EXPECTED_CORPUS_MANIFEST_SHA256[1:]
        with self.assertRaisesRegex(census.CensusError, "manifest pin"):
            census.validate_corpus_pin(poisoned, census.EXPECTED_CORPUS_FILES)

    def test_same_count_compiled_drift_is_refused(self) -> None:
        identity = {
            "archiveCount": census.EXPECTED_RESOURCE_ARCHIVES,
            "resourceManifestSha256": census.EXPECTED_RESOURCE_MANIFEST_SHA256,
            "worldChunkCount": census.EXPECTED_COMPILED_WORLDS,
            "compiledCallCount": census.EXPECTED_COMPILED_CALLS,
            "compiledUsedNatives": census.EXPECTED_COMPILED_NATIVES,
            "compiledProfileSha256": census.EXPECTED_COMPILED_PROFILE_SHA256,
        }
        census.validate_compiled_pins(identity)
        identity["resourceManifestSha256"] = "f" * 64
        with self.assertRaisesRegex(census.CensusError, "resource manifest pin"):
            census.validate_compiled_pins(identity)

    def _coverage_fixture(self, root: Path) -> None:
        files: dict[str, dict[str, object]] = {}
        summary = {
            "denominators": {"coverageIndexCount": 72, "coverageSetSha256": "fixture"},
            "inputs": {"specimen": {"sha256": census.EXPECTED_SPECIMEN_SHA256}},
            "sources": [{"receipt": {"targetSha256": "ab" * 32}}],
        }
        for name in census.COVERAGE_FILES:
            path = root / name
            path.write_bytes(census.canonical_json(summary) if name == "ledger-summary.json" else b"fixture\n")
            files[name] = {"path": name, "bytes": path.stat().st_size, "sha256": census.sha256_file(path)}
        (root / "ledger.ready.json").write_bytes(census.canonical_json({"schema": census.COVERAGE_READY_SCHEMA, "files": files}))

    def test_self_restamped_coverage_fixture_still_fails_canonical_pin(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); self._coverage_fixture(root)
            self.assertEqual(7, census.coverage_identity(root, enforce_pins=False)["publishedFiles"])
            with self.assertRaisesRegex(census.CensusError, "READY pin"):
                census.coverage_identity(root, enforce_pins=True)

    def test_coverage_ready_requires_exact_file_set_and_portable_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary); self._coverage_fixture(root)
            ready_path = root / "ledger.ready.json"
            ready = json.loads(ready_path.read_text())
            ready["files"]["extra.tsv"] = {"path": "extra.tsv", "bytes": 0, "sha256": census.sha256_bytes(b"")}
            ready_path.write_bytes(census.canonical_json(ready))
            with self.assertRaisesRegex(census.CensusError, "exact seven-file"):
                census.coverage_identity(root, enforce_pins=False)


class RankTests(unittest.TestCase):
    def test_unrunnable_source_directory_cannot_receive_any_rank(self) -> None:
        def row(key: str, runnable: bool, stock: int, init: int, stimulus: int, frontier: int) -> dict[str, object]:
            return {
                "levelKey": key, "runnableArchive": str(runnable),
                "stockEarlyExpressionPrintCount": stock, "stockEarlyLiteralPrintCount": 0,
                "initExpressionPrintCount": init, "stimulusExpressionPrintCount": stimulus,
                "stimulusLiteralPrintCount": 0, "compiledFrontierNativeCount": frontier,
                "compiledFrontierCallCount": frontier, "stockObservabilityRank": 0,
                "authoredStimulusRank": 0, "nativeCoverageRank": 0,
            }
        rows = [row("001", True, 1, 1, 1, 1), row("999", False, 999, 999, 999, 999)]
        census._assign_ranks(rows)
        self.assertEqual((1, 1, 1), (rows[0]["stockObservabilityRank"], rows[0]["authoredStimulusRank"], rows[0]["nativeCoverageRank"]))
        self.assertEqual((0, 0, 0), (rows[1]["stockObservabilityRank"], rows[1]["authoredStimulusRank"], rows[1]["nativeCoverageRank"]))

    def test_presence_class_names_do_not_conflate_source_and_compiled(self) -> None:
        self.assertEqual("SOURCE_PRESENT_UNOBSERVED", census.classify_presence(True, False, "SOURCE"))
        self.assertEqual("COMPILED_ABSENT_OBSERVED", census.classify_presence(False, True, "COMPILED"))


@unittest.skipUnless(
    (EVIDENCE_ROOT / "local-lab/safe-copy-bea-pristine/data/MissionScripts").is_dir(),
    "local retail-derived corpus is intentionally untracked",
)
class FrozenCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        old = os.environ.get("BEA_MSL_LOGGER_EVIDENCE_REPO")
        os.environ["BEA_MSL_LOGGER_EVIDENCE_REPO"] = str(EVIDENCE_ROOT)
        try:
            cls.inputs = census.canonical_inputs(ROOT)
            cls.outputs, cls.summary = census.analyze(cls.inputs, enforce_pins=True)
        finally:
            if old is None: os.environ.pop("BEA_MSL_LOGGER_EVIDENCE_REPO", None)
            else: os.environ["BEA_MSL_LOGGER_EVIDENCE_REPO"] = old

    def test_exact_source_compiled_runtime_counts(self) -> None:
        counts = self.summary["counts"]
        expected = {
            "corpusFiles": 733, "levelDirectories": 76, "runnableLevelDirectories": 66,
            "unrunnableLevelDirectories": 10, "resourceArchives": 301,
            "compiledWorldChunks": 115, "nativeRegistryRows": 144,
            "sourceNativeCalls": 9382, "compiledNativeCalls": 9236,
            "sourcePresentNatives": 110, "sourceAbsentNatives": 34,
            "compiledPresentNatives": 108, "compiledAbsentNatives": 36,
            "printSourceCalls": 726, "printCompiledCalls": 783,
            "printFiles": 207, "printLevelDirectories": 62,
            "literalPrintCalls": 580, "expressionPrintCalls": 146,
            "initPrintCalls": 145, "eventPrintCalls": 521,
            "actorHandlerPrintCalls": 60, "topLevelPrintCalls": 0,
        }
        for key, value in expected.items():
            with self.subTest(key=key): self.assertEqual(value, counts[key])
        self.assertEqual(["SetSegmentHealth", "SetAllSegmentsHealth"], counts["sourceOnlyNatives"])
        self.assertEqual(
            {"COMPILED_ABSENT_OBSERVED": 1, "COMPILED_ABSENT_UNOBSERVED": 35, "COMPILED_PRESENT_OBSERVED": 63, "COMPILED_PRESENT_UNOBSERVED": 45},
            counts["compiledPresenceCoverageClasses"],
        )

    def test_resource_join_excludes_exact_ten_nonrunnable_source_levels(self) -> None:
        rows = list(csv.DictReader(io.StringIO(self.outputs["level-summary.tsv"].decode()), delimiter="\t"))
        missing = {row["levelKey"] for row in rows if row["levelKey"] != "ROOT" and row["runnableArchive"] == "False"}
        self.assertEqual({"003", "004", "010", "020", "021", "022", "530", "888", "956", "958"}, missing)
        for row in rows:
            if row["runnableArchive"] == "False":
                self.assertEqual(("0", "0", "0"), (row["stockObservabilityRank"], row["authoredStimulusRank"], row["nativeCoverageRank"]))

    def test_source_expression_text_is_published_not_only_hashed(self) -> None:
        rows = list(csv.DictReader(io.StringIO(self.outputs["print-calls.tsv"].decode()), delimiter="\t"))
        expressions = [row for row in rows if row["argumentKind"] == "expression"]
        self.assertEqual(146, len(expressions))
        self.assertTrue(all(row["argumentText"] for row in expressions))
        for row in expressions[:20]:
            encoded = row["argumentText"].encode()
            self.assertEqual(str(len(encoded)), row["argumentBytes"])
            self.assertEqual(census.sha256_bytes(encoded), row["argumentSha256"])

    def test_static_dispatch_and_console_hypothesis_are_exactly_scoped(self) -> None:
        dispatch = json.loads(self.outputs["print-dispatch-static.json"])
        self.assertEqual([1, 2, 3, 4, 5, 6], [row["typeId"] for row in dispatch["types"]])
        self.assertEqual("STATIC_EXACT_BYTES", dispatch["evidenceGrade"])
        callers = list(csv.DictReader(io.StringIO(self.outputs["console-printf-mapped-callers.tsv"].decode()), delimiter="\t"))
        self.assertEqual(175, len(callers))
        self.assertEqual(377, sum(int(row["callSiteCount"]) for row in callers))
        callsites = list(csv.DictReader(io.StringIO(self.outputs["console-printf-callsites.tsv"].decode()), delimiter="\t"))
        self.assertEqual(380, len(callsites))
        partitions = {}
        for row in callsites:
            key = (row["receiverChannel"], row["mappingState"])
            partitions[key] = partitions.get(key, 0) + 1
        self.assertEqual(
            {
                ("DORMANT_LOGGER_RECEIVER", "GHIDRA_MAPPED"): 250,
                ("DORMANT_LOGGER_RECEIVER", "GHIDRA_UNMAPPED"): 3,
                ("SETUPHISTORY_RECEIVER", "GHIDRA_MAPPED"): 127,
            },
            partitions,
        )
        unmapped = {row["callSiteVa"]: row for row in callsites if row["mappingState"] == "GHIDRA_UNMAPPED"}
        self.assertEqual({"0x004f22fa", "0x005351f0", "0x00536ba9"}, set(unmapped))
        self.assertEqual("ERROR: Can't open text file %s", unmapped["0x004f22fa"]["formatString"])
        self.assertEqual("FATAL ERROR: Called PlayAnimWait on the non base script object", unmapped["0x005351f0"]["formatString"])
        self.assertEqual("Can't find particle effect %s", unmapped["0x00536ba9"]["formatString"])
        static = self.summary["inputs"]["staticLoggerEvidence"]
        self.assertEqual("PRISTINE_REL32_RECEIVER_CENSUS_WITH_GHIDRA_MAPPING", static["claimClass"])
        self.assertEqual((380, 377, 3, 253, 127), (
            static["rawRel32CallSiteCount"], static["ghidraMappedCallSiteCount"],
            static["ghidraUnmappedCallSiteCount"], static["dormantLoggerReceiverCallSiteCount"],
            static["setupHistoryReceiverCallSiteCount"],
        ))

    def test_console_raw_denominator_and_receiver_poisons_refuse(self) -> None:
        image = bytearray(self.inputs.specimen.read_bytes())
        body_rows = list(census._tsv_reader(self.inputs.parity_ready.parent / "after-body-ranges.tsv"))
        missing_call = bytearray(image)
        missing_call[census._pe_offset(missing_call, 0x004F22FA)] = 0x90
        with self.assertRaisesRegex(census.CensusError, "raw CConsole__Printf rel32 call count"):
            census.console_callsite_census(bytes(missing_call), body_rows)
        wrong_receiver = bytearray(image)
        receiver_immediate = census._pe_offset(wrong_receiver, 0x004F22F6)
        wrong_receiver[receiver_immediate] ^= 0x01
        with self.assertRaisesRegex(census.CensusError, "unknown receiver"):
            census.console_callsite_census(bytes(wrong_receiver), body_rows)

    def test_three_ranks_have_distinct_exact_leaders(self) -> None:
        rows = list(csv.DictReader(io.StringIO(self.outputs["level-summary.tsv"].decode()), delimiter="\t"))
        by_stock = {row["stockObservabilityRank"]: row["levelKey"] for row in rows}
        by_stimulus = {row["authoredStimulusRank"]: row["levelKey"] for row in rows}
        by_native = {row["nativeCoverageRank"]: row["levelKey"] for row in rows}
        self.assertEqual(("500", "742", "521"), (by_stock["1"], by_stimulus["1"], by_native["1"]))

    def test_compiled_profile_matches_existing_probe_author_owner(self) -> None:
        probe = sys.modules.get("probe_author")
        self.assertIsNotNone(probe)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ResourceWarning)
            independent = probe.build_call_profile(
                EVIDENCE_ROOT / "local-lab/safe-copy-bea-pristine/data/Resources",
                lab=EVIDENCE_ROOT / "local-lab",
            )
        rows = list(csv.DictReader(io.StringIO(self.outputs["compiled-native-profile.tsv"].decode()), delimiter="\t"))
        by_index = {int(row["index"]): row for row in independent["by_name"].values()}
        disagreements = []
        for row in rows:
            index = int(row["nativeIndex"])
            expected = by_index.get(index, {"calls": 0, "profiles": {}})
            if int(row["compiledCallCount"]) != expected["calls"] or json.loads(row["callProfilesJson"]) != expected["profiles"]:
                disagreements.append(index)
        self.assertEqual([], disagreements)
        self.assertEqual((301, 115, 108), (independent["archives"], independent["world_chunks"], independent["natives_called"]))


@unittest.skipUnless(BUNDLE is not None, "set BEA_MSL_LOGGER_CENSUS_BUNDLE for publication poisons")
class PublishedBundleTests(unittest.TestCase):
    def test_frozen_owner_verifies_bundle(self) -> None:
        assert BUNDLE is not None
        census.verify_bundle(BUNDLE, TOOL)

    def test_output_and_ready_tamper_fail(self) -> None:
        assert BUNDLE is not None
        for member, mutation in (
            ("native-summary.tsv", lambda data: data + b"\n"),
            ("READY.json", lambda data: data.replace(b'"status": "READY"', b'"status": "SURVIVED"')),
        ):
            with self.subTest(member=member), tempfile.TemporaryDirectory() as temporary:
                copy = Path(temporary) / "bundle"; shutil.copytree(BUNDLE, copy)
                path = copy / member; path.write_bytes(mutation(path.read_bytes()))
                with self.assertRaises(census.CensusError): census.verify_bundle(copy, TOOL)


if __name__ == "__main__":
    unittest.main(verbosity=2)
