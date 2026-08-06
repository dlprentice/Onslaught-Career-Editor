#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused attacks for :mod:`re_global_init515_campaign_lineage`."""

from __future__ import annotations

import csv
import importlib.util
import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/re_global_init515_campaign_lineage.py"
SPEC = importlib.util.spec_from_file_location("re_global_init515_campaign_lineage", TOOL)
assert SPEC is not None and SPEC.loader is not None
lineage = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(lineage)
FORMAL = ROOT / "local-lab/formal-global-init515-proof-20260803-v4"
CAMPAIGN = ROOT / "local-lab/re-campaign/campaign-2026-08-02-observed40-generation-5-v5-carried-r3-invariant-bound"
BUNDLE = ROOT / "local-lab/global-init515-campaign-lineage-v1-ready"


def generic_tsv(rows: list[dict[str, str]]) -> bytes:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def synthetic_bundle(root: Path, *, owner: bytes | None = None, ready: bytes | None = None) -> Path:
    bundle = root / "bundle"
    (bundle / "inputs").mkdir(parents=True)
    for name in lineage.INPUT_NAMES:
        (bundle / name).write_bytes(b"")
    for name in lineage.OUTPUT_NAMES:
        (bundle / name).write_bytes(b"")
    (bundle / "lineage-owner.py").write_bytes(TOOL.read_bytes() if owner is None else owner)
    (bundle / "READY.json").write_bytes(lineage.canonical_json({}) if ready is None else ready)
    return bundle


@unittest.skipUnless(FORMAL.is_dir() and CAMPAIGN.is_dir(), "local formal/campaign evidence is absent")
class GlobalInit515CampaignLineageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inputs = lineage.load_external_inputs(FORMAL, CAMPAIGN)

    def test_real_lineage_is_exact_and_separates_the_two_range_digests(self) -> None:
        rendered, summary = lineage.derive(dict(self.inputs))
        self.assertEqual(515, summary["rows"])
        self.assertEqual(57_182, summary["bodyBytes"])
        self.assertEqual(10_602, summary["instructions"])
        self.assertEqual(lineage.EXPECTED_LINEAGE_BYTES, len(rendered))
        self.assertEqual(lineage.EXPECTED_LINEAGE_SHA256, lineage.sha256_bytes(rendered))
        rows = lineage.parse_tsv(rendered, "lineage")
        first = rows[0]
        self.assertNotEqual(first["expectedRangeDigest"], first["expectedBodyRangeSetSha256"])
        self.assertTrue(first["expectedNewEntityKey"].endswith(first["expectedBodyRangeSetSha256"]))
        self.assertFalse(first["expectedNewEntityKey"].endswith(first["expectedRangeDigest"]))

    def test_frozen_input_mutation_fails_closed(self) -> None:
        inputs = dict(self.inputs)
        inputs["inputs/admissible515.tsv"] += b"mutation"
        with self.assertRaisesRegex(lineage.LineageError, "admissible515 input differs"):
            lineage.validate_input_receipts(inputs)

    def test_semantic_attacks_fail_after_hash_gate_is_separately_bypassed(self) -> None:
        attacks: list[tuple[str, str]] = []

        manifest = lineage.parse_tsv(self.inputs["inputs/admissible515.tsv"], "manifest")
        manifest[0]["questionIds"], manifest[1]["questionIds"] = manifest[1]["questionIds"], manifest[0]["questionIds"]
        attacks.append(("inputs/admissible515.tsv", generic_tsv(manifest)))

        questions = lineage.parse_tsv(self.inputs["inputs/generation5-campaign-questions.tsv"], "questions")
        target_question = lineage.parse_tsv(self.inputs["inputs/admissible515.tsv"], "manifest")[0]["questionIds"]
        next(row for row in questions if row["questionId"] == target_question)["state"] = "CLOSED_SURVIVED"
        attacks.append(("inputs/generation5-campaign-questions.tsv", generic_tsv(questions)))

        supersessions = lineage.parse_tsv(self.inputs["inputs/generation5-campaign-supersessions.tsv"], "supersessions")
        residual = lineage.parse_tsv(self.inputs["inputs/admissible515.tsv"], "manifest")[0]["residualEntityKeys"]
        forged = dict(supersessions[0])
        forged["supersessionId"] = "S-0000000000000000"
        forged["oldEntityKey"] = residual
        supersessions.append(forged)
        attacks.append(("inputs/generation5-campaign-supersessions.tsv", generic_tsv(supersessions)))

        admissible = lineage.parse_tsv(self.inputs["inputs/admissible515.tsv"], "manifest")
        quarantine = lineage.parse_tsv(self.inputs["inputs/listing-quarantine5.tsv"], "quarantine")
        admissible[0] = dict(quarantine[0])
        admissible.sort(key=lambda row: int(row["entry"], 16))
        attacks.append(("inputs/admissible515.tsv", generic_tsv(admissible)))

        for name, poisoned in attacks:
            with self.subTest(name=name):
                inputs = dict(self.inputs)
                inputs[name] = poisoned
                with (
                    mock.patch.object(lineage, "validate_input_receipts", return_value=({}, {})),
                    self.assertRaises(lineage.LineageError),
                ):
                    lineage.derive_rows(inputs)

    def test_structural_attacks_need_no_local_rederivation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            owner_attack = synthetic_bundle(root / "owner", owner=TOOL.read_bytes() + b"# mutation\n")
            with self.assertRaisesRegex(lineage.LineageError, "frozen owner differs"):
                lineage.verify(owner_attack)
            directory_attack = synthetic_bundle(root / "directory")
            (directory_attack / "extra").mkdir()
            with self.assertRaisesRegex(lineage.LineageError, "bundle members differ"):
                lineage.validate_bundle_tree(directory_attack)
            input_attack = synthetic_bundle(root / "input")
            (input_attack / "inputs/extra").write_bytes(b"")
            with self.assertRaisesRegex(lineage.LineageError, "bundle input members differ"):
                lineage.validate_bundle_tree(input_attack)
            canonical_attack = synthetic_bundle(root / "canonical", ready=b"{}")
            with self.assertRaisesRegex(lineage.LineageError, "not canonical JSON"):
                lineage.verify(canonical_attack)

    @unittest.skipUnless(os.name == "nt" and hasattr(Path, "is_junction"), "Windows junctions unavailable")
    def test_bundle_rejects_terminal_root_junction(self) -> None:
        import subprocess

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = synthetic_bundle(root / "target")
            junction = root / "junction"
            made = subprocess.run(["cmd.exe", "/d", "/c", "mklink", "/J", str(junction), str(target)], capture_output=True, text=True, check=False)
            if made.returncode != 0 or not junction.is_junction():
                self.skipTest("could not create junction")
            try:
                with self.assertRaisesRegex(lineage.LineageError, "reparse point"):
                    lineage.validate_bundle_tree(junction)
            finally:
                os.rmdir(junction)

    def test_build_verifies_before_atomic_publication(self) -> None:
        inputs = {name: name.encode("ascii") for name in lineage.INPUT_NAMES}
        outputs = {name: name.encode("ascii") for name in lineage.OUTPUT_NAMES}
        outputs["lineage-owner.py"] = TOOL.read_bytes()
        summary = {"rows": 0}
        original_write = Path.write_bytes

        def poisoned_write(path: Path, data: bytes) -> int:
            if path.name == "lineage515.tsv":
                data += b"poison"
            return original_write(path, data)

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out = root / "published"
            with (
                mock.patch.object(lineage, "load_external_inputs", return_value=inputs),
                mock.patch.object(lineage, "output_bytes", return_value=(outputs, summary)),
                mock.patch.object(Path, "write_bytes", poisoned_write),
                self.assertRaisesRegex(lineage.LineageError, "derived output differs"),
            ):
                lineage.build(root / "formal", root / "campaign", out)
            self.assertFalse(out.exists())
            self.assertEqual([], list(root.glob(".published-*")))

    def test_frozen_ready_replays_when_present(self) -> None:
        if not BUNDLE.is_dir():
            self.skipTest("local READY evidence is absent")
        result = lineage.verify(BUNDLE)
        self.assertEqual(lineage.STATUS, result["status"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
