#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for the 31-function text-gap live authority."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

try:
    import tools.ghidra_text_gap_boundary_live_authority as authority
except ModuleNotFoundError:  # direct execution from tools/
    import ghidra_text_gap_boundary_live_authority as authority


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SHARED = Path.home() / "source/Onslaught-Career-Editor"
EVIDENCE_REPO = Path(os.environ.get(
    "BEA_TEXT_GAP_LIVE_EVIDENCE_REPO",
    DEFAULT_SHARED if DEFAULT_SHARED.is_dir() else ROOT,
))
LIVE_LANE = Path(os.environ.get(
    "BEA_TEXT_GAP_LIVE_LANE",
    EVIDENCE_REPO / authority.LIVE_LANE_REL,
))
SCRATCH_REPO = Path(os.environ.get("BEA_TEXT_GAP_SCRATCH_REPO", EVIDENCE_REPO))
LIVE_PROJECT = Path(os.environ.get(
    "BEA_LIVE_GHIDRA_PROJECT", Path.home() / "Ghidra/Projects"
))
PRE_BACKUP = Path(os.environ.get(
    "BEA_TEXT_GAP_PRE_BACKUP",
    r"D:\BEA-Ghidra-Backups\2026-08-14-text-gap-boundaries-pre-live",
))
POST_BACKUP = Path(os.environ.get(
    "BEA_TEXT_GAP_POST_BACKUP",
    r"D:\BEA-Ghidra-Backups\2026-08-14-text-gap-boundaries-post-live",
))
SAVED_RECEIPT = ROOT / (
    "local-lab/ghidra-text-gap-boundary-live-authority-20260814-v2/"
    "live-promotion.ready.json"
)


class PureContractTests(unittest.TestCase):
    def test_project_digest_is_relative_path_ordered(self) -> None:
        value = {
            "files": [
                {"relative_path": "a", "size": 1, "sha256": "1" * 64},
                {"relative_path": "b", "size": 2, "sha256": "2" * 64},
            ]
        }
        raw = (
            f"{'1' * 64}\t1\ta\n"
            f"{'2' * 64}\t2\tb\n"
        ).encode("utf-8")
        self.assertEqual(authority.project_digest(value), hashlib.sha256(raw).hexdigest())
        with self.assertRaisesRegex(authority.AuthorityError, "relative-path ordered"):
            authority.project_digest({"files": list(reversed(value["files"]))})

    def test_target_row_supports_noncontiguous_body_sets(self) -> None:
        target = {
            "retailEntry": "0x00000010",
            "retailBodyRangesHalfOpen": "0x00000010-0x00000012;0x00000020-0x00000023",
            "bodyBytes": "5",
            "bodyRangeSha256": "range-hash",
            "instructionCount": "3",
        }
        row = {
            "address": "0x00000010",
            "name": "FUN_00000010",
            "nameSource": "DEFAULT",
            "bodyBytes": "5",
            "bodyMin": "0x00000010",
            "bodyMax": "0x00000022",
            "bodyRanges": "2",
            "bodyDigest": "range-hash",
            "instrCount": "3",
        }
        authority.validate_target_row(row, target)
        row["bodyMax"] = "0x00000023"
        with self.assertRaisesRegex(authority.AuthorityError, "body max"):
            authority.validate_target_row(row, target)

    def test_raw_function_comparison_checks_pre_rows_byte_for_byte(self) -> None:
        fields = (
            "address\tname\tnameSource\tbodyBytes\tbodyMin\tbodyMax\t"
            "bodyRanges\tbodyDigest\tinstrCount\n"
        )
        target = {
            "retailEntry": "0x00000020",
            "retailBodyRangesHalfOpen": "0x00000020-0x00000021",
            "bodyBytes": "1",
            "bodyRangeSha256": "target-range",
            "instructionCount": "1",
        }
        stable = "0x00000010\tStable\tUSER_DEFINED\t1\t0x00000010\t0x00000010\t1\tstable\t1\n"
        changed = "0x00000010\tChanged\tUSER_DEFINED\t1\t0x00000010\t0x00000010\t1\tstable\t1\n"
        added = "0x00000020\tFUN_00000020\tDEFAULT\t1\t0x00000020\t0x00000020\t1\ttarget-range\t1\n"
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            pre = root / "pre.tsv"
            post = root / "post.tsv"
            scratch_post = root / "scratch.tsv"
            pre.write_bytes((fields + stable).encode("utf-8"))
            post.write_bytes((fields + changed + added).encode("utf-8"))
            scratch_post.write_bytes((fields + stable + added).encode("utf-8"))
            with (
                mock.patch.object(authority, "PRE_FUNCTIONS", 1),
                mock.patch.object(authority, "POST_FUNCTIONS", 2),
            ):
                with self.assertRaisesRegex(authority.AuthorityError, "PRE row changed"):
                    authority.validate_function_delta(
                        pre, post, scratch_post, [target]
                    )

    def test_live_log_gate_requires_exactly_one_save(self) -> None:
        prefix = "TEXT_GAP_BOUNDARIES_OK mode=apply\nProcessing project file: /BEA.exe\n"
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "ghidra.log"
            path.write_text(
                prefix + "Save succeeded for processed file: /BEA.exe\n",
                encoding="utf-8",
            )
            self.assertEqual(
                authority.validate_run_log(path, "apply", live=True)["successfulSaves"],
                1,
            )
            path.write_text(
                prefix + "Save succeeded for processed file: /BEA.exe\n" * 2,
                encoding="utf-8",
            )
            with self.assertRaisesRegex(authority.AuthorityError, "writable/save"):
                authority.validate_run_log(path, "apply", live=True)

    def test_aggregate_payload_rejects_machine_paths(self) -> None:
        authority.ensure_portable({"path": "local-lab/evidence/receipt.json"})
        for value in (
            r"C:\Users\david\evidence.json",
            r"local-lab\evidence.json",
            "/tmp/evidence.json",
        ):
            with self.assertRaises(authority.AuthorityError):
                authority.ensure_portable({"path": value})

    def test_receipt_write_is_create_new(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "ready.json"
            authority.atomic_new_json(path, {"ok": True})
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"ok": True})
            with self.assertRaisesRegex(authority.AuthorityError, "refusing to overwrite"):
                authority.atomic_new_json(path, {"ok": False})

    def test_output_can_live_in_authority_repo_outside_evidence_lanes(self) -> None:
        config = authority.Config(
            ROOT,
            ROOT / authority.LIVE_LANE_REL,
            ROOT,
            ROOT / "fixture-live-project",
            ROOT / "fixture-pre-backup",
            ROOT / "fixture-post-backup",
            ROOT / "local-lab/fixture-live-authority/ready.json",
        )
        authority.validate_output(config, sealing=True)


RETAINED_AVAILABLE = all(path.exists() for path in (
    EVIDENCE_REPO / authority.MANIFEST_REL,
    LIVE_LANE / "runs/live-readback/functions.tsv",
    SCRATCH_REPO / authority.SCRATCH_RECEIPT_REL,
    LIVE_PROJECT / "BEA.gpr",
    PRE_BACKUP / "backup_manifest.json",
    POST_BACKUP / "backup_manifest.json",
    SAVED_RECEIPT,
))


@unittest.skipUnless(RETAINED_AVAILABLE, "retained text-gap live authority evidence is unavailable")
class RetainedEvidenceTests(unittest.TestCase):
    def test_saved_receipt_reproduces_without_opening_ghidra(self) -> None:
        config = authority.Config(
            EVIDENCE_REPO,
            LIVE_LANE,
            SCRATCH_REPO,
            LIVE_PROJECT,
            PRE_BACKUP,
            POST_BACKUP,
            SAVED_RECEIPT,
        )
        authority.verify(config)


if __name__ == "__main__":
    unittest.main(verbosity=2)
