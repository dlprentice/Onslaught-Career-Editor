#!/usr/bin/env python3
"""Regression tests for the pinned campaign evidence-register exporter."""

from __future__ import annotations

import csv
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import re_evidence_register_export as exporter


FUNCTION_COLUMNS = (
    "entityKey",
    "entryVa",
    "currentName",
    "semanticGrade",
    "resolutionState",
    "campaignState",
    "evidenceStates",
)


def write_fixture(root: Path, *, reducer: dict | None = None) -> tuple[str, str]:
    root.mkdir()
    with open(root / "campaign-functions.tsv", "w", encoding="utf-8", newline="") as handle:
        handle.write("# bea.re.campaign.v5\n")
        writer = csv.DictWriter(
            handle, fieldnames=FUNCTION_COLUMNS, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerow(
            {
                "entityKey": "CODE:test:VA=0x00401000:RANGES=" + "a" * 64,
                "entryVa": "0x00401000",
                "currentName": "Example",
                "semanticGrade": "OPAQUE",
                "resolutionState": "OPEN_JOIN",
                "campaignState": "OPEN",
                "evidenceStates": "BASELINE_STATIC",
            }
        )
    reducer_id = "b" * 64
    receipt = {
        "schema": "bea.re.campaign.v5",
        "reducer": reducer if reducer is not None else {"id": reducer_id},
        "generatedAtUtc": "2026-08-08T12:34:56+00:00",
        "generation": 11,
        "advance": {"branchId": "incident-20260806-recovery-v1"},
    }
    ready = root / "campaign.ready.json"
    ready.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return hashlib.sha256(ready.read_bytes()).hexdigest(), str(receipt["reducer"]["id"])


class EvidenceRegisterExportTests(unittest.TestCase):
    def test_direct_mode_requires_every_authority_selector(self) -> None:
        self.assertEqual(10, exporter.main([]))

    def test_weak_reducer_is_refused_before_rows_publish(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "campaign"
            ready_sha, reducer_id = write_fixture(
                root, reducer={"id": "c" * 64, "note": "weak candidate reducer"}
            )
            with self.assertRaisesRegex(exporter.ExportError, "frozen full replay refused"):
                exporter.build(
                    root,
                    expected_ready_sha256=ready_sha,
                    expected_reducer_id=reducer_id,
                )

    def test_ready_self_identity_lie_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "campaign"
            ready_sha, reducer_id = write_fixture(root)
            ready = root / "campaign.ready.json"
            receipt = json.loads(ready.read_text(encoding="utf-8"))
            receipt["readySha256"] = "0" * 64
            ready.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
            actual = hashlib.sha256(ready.read_bytes()).hexdigest()
            with self.assertRaisesRegex(exporter.ExportError, "self-identity"):
                exporter.build(
                    root,
                    expected_ready_sha256=actual,
                    expected_reducer_id=reducer_id,
                )

    def test_publish_and_check_are_deterministic_for_one_ready(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "campaign"
            out = Path(td) / "register.tsv"
            ready_sha, reducer_id = write_fixture(root)
            argv = [
                "--campaign",
                str(root),
                "--out",
                str(out),
                "--expected-ready-sha256",
                ready_sha,
                "--expected-reducer-id",
                reducer_id,
            ]
            with patch.object(exporter, "verify_full_replay"):
                self.assertEqual(0, exporter.main(argv))
                first = out.read_bytes()
                self.assertEqual(0, exporter.main([*argv, "--check"]))
                self.assertEqual(first, out.read_bytes())
                text = first.decode("utf-8")
                self.assertIn("# bea.re.evidence-register.v2", text)
                self.assertIn("# generatedAtUtc: 2026-08-08T12:34:56+00:00", text)
                self.assertIn(f"# readySha256: {ready_sha}", text)
                self.assertIn(f"# reducerId: {reducer_id}", text)
                out.write_text(text.replace("Example", "Stale"), encoding="utf-8")
                self.assertEqual(10, exporter.main([*argv, "--check"]))

    def test_header_only_check_is_portable_and_detects_stale_authority(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            register = root / "register.tsv"
            state = root / "developer_state.json"
            authority = {
                "campaignPath": "local-lab/not-present-in-a-fresh-clone",
                "evidenceRegisterPath": str(register),
                "generation": 11,
                "readySha256": "a" * 64,
                "reducerId": "b" * 64,
                "lineageId": "incident-20260806-recovery-v1",
            }
            state.write_text(
                json.dumps({"current_re_authority": authority}), encoding="utf-8"
            )
            register.write_text(
                "\n".join(
                    (
                        "# bea.re.evidence-register.v2",
                        "# generatedAtUtc: 2026-08-08T12:34:56+00:00",
                        "# generation: 11",
                        f"# readySha256: {'a' * 64}",
                        f"# reducerId: {'b' * 64}",
                        "# lineageId: incident-20260806-recovery-v1",
                        "# authorityClass: FULL_CAMPAIGN_REPLAY_AUTHORITY",
                        "entryVa\tname",
                    )
                )
                + "\n",
                encoding="utf-8",
            )
            self.assertEqual(
                0, exporter.main(["--state", str(state), "--check-header-only"])
            )
            authority["readySha256"] = "c" * 64
            state.write_text(
                json.dumps({"current_re_authority": authority}), encoding="utf-8"
            )
            self.assertEqual(
                10, exporter.main(["--state", str(state), "--check-header-only"])
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
