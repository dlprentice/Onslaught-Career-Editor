#!/usr/bin/env python3
"""Focused poison tests for the CRT text-residual boundary owner."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL_PATH = ROOT / "tools" / "re_text_residual_boundary.py"
SPEC = importlib.util.spec_from_file_location("re_text_residual_boundary", TOOL_PATH)
assert SPEC is not None and SPEC.loader is not None
boundary = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(boundary)
BUNDLE_ENV = os.environ.get("BEA_BOUNDARY_BUNDLE", "")
BUNDLE = Path(BUNDLE_ENV).resolve() if BUNDLE_ENV else None


class TsvParserTests(unittest.TestCase):
    def test_canonical_tsv_bytes_pin_column_order_and_final_lf(self) -> None:
        self.assertEqual(
            b"left\tright\nA\tB\n",
            boundary.render_tsv(("left", "right"), [{"left": "A", "right": "B"}]),
        )

    def test_schema_comment_is_not_mistaken_for_the_header(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "campaign.tsv"
            path.write_text(
                "# bea.re.campaign.v5\nleft\tright\nA\tB\n",
                encoding="utf-8",
            )

            self.assertEqual(
                [{"left": "A", "right": "B"}],
                boundary.read_tsv(
                    path,
                    "fixture",
                    leading_comment="# bea.re.campaign.v5",
                ),
            )

    def test_unexpected_comment_row_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "poisoned.tsv"
            path.write_text(
                "left\tright\nA\tB\n#POISONED_ROW_IGNORED\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(boundary.BoundaryError, "unexpected comment row"):
                boundary.read_tsv(path, "fixture")

    def test_extra_column_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "malformed.tsv"
            path.write_text("left\tright\nA\tB\tC\n", encoding="utf-8")

            with self.assertRaisesRegex(boundary.BoundaryError, "malformed row"):
                boundary.read_tsv(path, "fixture")


class CoverageLineageTests(unittest.TestCase):
    def setUp(self) -> None:
        lab = ROOT / "local-lab"
        lab.mkdir(exist_ok=True)
        self.root = Path(tempfile.mkdtemp(prefix="boundary-unit-", dir=lab))
        self.summary = self.root / "ledger-summary.json"
        self.unmapped = self.root / "ledger-unmapped.tsv"
        self.summary.write_text('{"fixture": true}\n', encoding="utf-8")
        self.unmapped.write_text("start\tend\n0x1\t0x2\n", encoding="utf-8")
        files = {
            "ledger-summary.json": boundary.stamp(self.summary),
            "ledger-unmapped.tsv": boundary.stamp(self.unmapped),
        }
        self.ready_path = self.root / "ledger.ready.json"
        self.ready_path.write_text(
            json.dumps(
                {
                    "schema": "bea.re.coverage-ledger-ready.v1",
                    "files": files,
                }
            )
            + "\n",
            encoding="utf-8",
        )
        self.body_ranges = {"bytes": 17, "sha256": "a" * 64}
        self.cohort = {
            "inputs": {
                "ledgerReady": boundary.stamp(self.ready_path),
                "ledgerSummary": files["ledger-summary.json"],
                "ledgerUnmapped": files["ledger-unmapped.tsv"],
                "bodyRanges": self.body_ranges,
            }
        }
        self.snapshot = {
            "files": copy.deepcopy(files),
            "parityGraph": {"bodyRanges": copy.deepcopy(self.body_ranges)},
        }

    def tearDown(self) -> None:
        shutil.rmtree(self.root)

    def test_underlying_ready_file_graph_is_accepted(self) -> None:
        result = boundary.validate_coverage_lineage(self.cohort, self.snapshot)

        self.assertEqual(boundary.stamp(self.ready_path), result["ready"])
        self.assertEqual(
            self.snapshot["files"]["ledger-summary.json"]["sha256"],
            result["fileSet"]["ledger-summary.json"]["sha256"],
        )

    def test_same_file_set_with_one_different_hash_is_refused(self) -> None:
        poisoned = copy.deepcopy(self.snapshot)
        poisoned["files"]["ledger-summary.json"]["sha256"] = "b" * 64

        with self.assertRaisesRegex(boundary.BoundaryError, "differ at ledger-summary"):
            boundary.validate_coverage_lineage(self.cohort, poisoned)

    def test_body_range_graph_mismatch_is_refused(self) -> None:
        poisoned = copy.deepcopy(self.snapshot)
        poisoned["parityGraph"]["bodyRanges"]["bytes"] += 1

        with self.assertRaisesRegex(boundary.BoundaryError, "body ranges"):
            boundary.validate_coverage_lineage(self.cohort, poisoned)


class CampaignSupersessionTests(unittest.TestCase):
    def test_old_code_candidate_va_is_canonicalized(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT / "local-lab") as temporary:
            campaign = Path(temporary)
            comment = "# bea.re.campaign.v5\n"
            fixtures = {
                "campaign-residuals.tsv": "startVa\tendVa\n",
                "campaign-questions.tsv": "entityKey\n",
                "campaign-contracts.tsv": "entityKey\n",
                "campaign-functions.tsv": "entryVa\n",
                "campaign-supersessions.tsv": (
                    "oldEntityKey\n"
                    "CODE_CANDIDATE:specimen:VA=0X00542710\n"
                ),
            }
            for name, body in fixtures.items():
                (campaign / name).write_text(comment + body, encoding="utf-8")

            indices = boundary.campaign_indices(campaign)

            self.assertEqual({"0x00542710"}, indices["supersededOldVas"])

@unittest.skipUnless(BUNDLE is not None and BUNDLE.is_dir(), "no boundary bundle requested")
class BoundaryBundlePoisonTests(unittest.TestCase):
    def setUp(self) -> None:
        assert BUNDLE is not None
        lab = ROOT / "local-lab"
        self.temporary = Path(tempfile.mkdtemp(prefix="boundary-poison-", dir=lab))
        self.bundle = self.temporary / "bundle"
        shutil.copytree(BUNDLE, self.bundle)

    def tearDown(self) -> None:
        shutil.rmtree(self.temporary)

    def read_ready(self) -> dict:
        return json.loads(
            (self.bundle / "boundary-targets.ready.json").read_text(encoding="utf-8")
        )

    def write_ready(self, ready: dict) -> None:
        (self.bundle / "boundary-targets.ready.json").write_text(
            json.dumps(ready, indent=2) + "\n",
            encoding="utf-8",
        )

    def test_frozen_owner_replays_from_its_bundle_directory(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                "-I",
                "-B",
                str((self.bundle / "boundary-owner.py").resolve()),
                "verify",
                "--bundle",
                str(self.bundle.resolve()),
            ],
            cwd=self.bundle,
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stderr or completed.stdout)
        self.assertIn("TEXT_RESIDUAL_BOUNDARY_VERIFIED", completed.stdout)

    def test_policy_and_claim_poison_is_refused(self) -> None:
        ready = self.read_ready()
        ready["selection"]["semanticNamesAuthorized"] = True
        ready["selection"]["batchAuthorized"] = True
        ready["claimBoundary"] = ["LIVE PROMOTION AUTHORIZED"]
        self.write_ready(ready)

        with self.assertRaisesRegex(boundary.BoundaryError, "selection policy drift"):
            boundary.verify_bundle(self.bundle)

    def test_source_envelope_poison_is_refused(self) -> None:
        ready = self.read_ready()
        ready["sourceCampaign"]["generation"] = 99
        ready["sourceCampaign"]["reducerId"] = "0" * 64
        self.write_ready(ready)

        with self.assertRaisesRegex(boundary.BoundaryError, "source campaign envelope"):
            boundary.verify_bundle(self.bundle)

    def test_self_restamped_hidden_comment_row_is_refused(self) -> None:
        manifest = self.bundle / "boundary-targets.tsv"
        with manifest.open("a", encoding="utf-8", newline="") as stream:
            stream.write("#POISONED_ROW_IGNORED_BY_VERIFIER\n")
        ready = self.read_ready()
        ready["outputs"]["boundary-targets.tsv"] = boundary.stamp(
            manifest,
            root=self.bundle,
        )
        self.write_ready(ready)

        with self.assertRaisesRegex(boundary.BoundaryError, "boundary manifest bytes"):
            boundary.verify_bundle(self.bundle)

    def test_self_restamped_trailing_blank_line_is_refused(self) -> None:
        manifest = self.bundle / "boundary-targets.tsv"
        manifest.write_bytes(manifest.read_bytes() + b"\n")
        ready = self.read_ready()
        ready["outputs"]["boundary-targets.tsv"] = boundary.stamp(
            manifest,
            root=self.bundle,
        )
        self.write_ready(ready)

        with self.assertRaisesRegex(boundary.BoundaryError, "boundary manifest bytes"):
            boundary.verify_bundle(self.bundle)

    def test_self_restamped_reordered_columns_are_refused(self) -> None:
        manifest = self.bundle / "boundary-targets.tsv"
        lines = manifest.read_text(encoding="utf-8").splitlines()
        header = lines[0].split("\t")
        header[0], header[1] = header[1], header[0]
        lines[0] = "\t".join(header)
        manifest.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="")
        ready = self.read_ready()
        ready["outputs"]["boundary-targets.tsv"] = boundary.stamp(
            manifest,
            root=self.bundle,
        )
        self.write_ready(ready)

        with self.assertRaisesRegex(boundary.BoundaryError, "boundary manifest bytes"):
            boundary.verify_bundle(self.bundle)

    def test_unmanifested_file_is_refused(self) -> None:
        (self.bundle / "unexpected.bin").write_bytes(b"poison")

        with self.assertRaisesRegex(boundary.BoundaryError, "unmanifested or missing"):
            boundary.verify_bundle(self.bundle)

if __name__ == "__main__":
    unittest.main(verbosity=2)
