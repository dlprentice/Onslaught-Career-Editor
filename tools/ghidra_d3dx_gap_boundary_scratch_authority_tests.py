#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "local-lab/d3dx-gap-two-boundary-scratch-20260814-v1"
RECEIPT = PACKAGE / "scratch-authority.ready.json"
PACKAGED_TOOL = PACKAGE / "tools/ghidra_d3dx_gap_boundary_scratch_authority.py"

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ghidra_d3dx_gap_boundary_scratch_authority as authority


class D3dxGapBoundaryScratchAuthorityTests(unittest.TestCase):
    def test_frozen_contract_constants(self) -> None:
        self.assertEqual(authority.MANIFEST_SHA256, "2d8f16415206538d0377fafe70c210bf8de65b442e2162ad5f5909d01c21fefd")
        self.assertEqual(authority.MUTATOR_SHA256, "8767c361207de1718c3d3742fa43f76e9d897772ecd6a8123116299277a3f710")
        self.assertEqual(authority.PRE_FUNCTIONS_SHA256, "c3942b9e340cef71b731290b845843697af5c53204449c51949b779e896272d6")
        self.assertEqual(authority.POST_FUNCTIONS_SHA256, "1a269f886c7cc7c11c854aa1219b81384102a530550277e88b83e9b3c043916d")
        self.assertEqual(set(authority.TARGETS), {"0x00595fc9", "0x00596028"})

    def test_saved_campaign_verifies_through_packaged_owner(self) -> None:
        if not RECEIPT.is_file():
            self.skipTest("ignored saved D3DX scratch evidence is absent")
        completed = subprocess.run(
            [
                sys.executable,
                "-I",
                "-B",
                str(PACKAGED_TOOL),
                "verify",
                "--package-root",
                str(PACKAGE),
                "--receipt",
                str(RECEIPT),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("D3DX_GAP_TWO_SCRATCH_AUTHORITY_VERIFIED", completed.stdout)
        value = json.loads(RECEIPT.read_text(encoding="utf-8"))
        self.assertEqual(value["verdict"], "SCRATCH_READY_LIVE_FORBIDDEN")
        self.assertEqual(value["policy"], "LIVE_FORBIDDEN")
        self.assertEqual(value["proof"]["unchangedPreRowsExact"], 8280)
        self.assertEqual(value["post"]["newDefaultFunctions"], 2)

    def test_every_boundary_result_column_is_semantically_checked(self) -> None:
        fields, rows = authority.read_tsv(
            PACKAGE / "runs/replica-a-readback/boundaries.tsv"
        ) if PACKAGE.is_dir() else (
            authority.BOUNDARY_FIELDS,
            [
                {
                    "candidateId": "D3DX-GAP-002",
                    "cohort": "D3DX_GAP_TWO",
                    "entry": "0x00595fc9",
                    "status": "verified",
                    "name": "FUN_00595fc9",
                    "nameSource": "DEFAULT",
                    "expectedRanges": "0x00595fc9-0x00596028",
                    "actualRanges": "0x00595fc9-0x00596028",
                    "expectedBodyBytes": "95",
                    "actualBodyBytes": "95",
                    "expectedRangeSha256": authority.TARGETS["0x00595fc9"]["rangeSha256"],
                    "actualRangeSha256": authority.TARGETS["0x00595fc9"]["rangeSha256"],
                    "expectedBodyBytesSha256": authority.TARGETS["0x00595fc9"]["bodySha256"],
                    "actualBodyBytesSha256": authority.TARGETS["0x00595fc9"]["bodySha256"],
                    "externalInstructionCount": "35",
                    "actualGhidraInstructionCount": "35",
                },
                {
                    "candidateId": "D3DX-GAP-003",
                    "cohort": "D3DX_GAP_TWO",
                    "entry": "0x00596028",
                    "status": "verified",
                    "name": "FUN_00596028",
                    "nameSource": "DEFAULT",
                    "expectedRanges": "0x00596028-0x005960c1",
                    "actualRanges": "0x00596028-0x005960c1",
                    "expectedBodyBytes": "153",
                    "actualBodyBytes": "153",
                    "expectedRangeSha256": authority.TARGETS["0x00596028"]["rangeSha256"],
                    "actualRangeSha256": authority.TARGETS["0x00596028"]["rangeSha256"],
                    "expectedBodyBytesSha256": authority.TARGETS["0x00596028"]["bodySha256"],
                    "actualBodyBytesSha256": authority.TARGETS["0x00596028"]["bodySha256"],
                    "externalInstructionCount": "57",
                    "actualGhidraInstructionCount": "57",
                },
            ],
        )
        self.assertEqual(fields, authority.BOUNDARY_FIELDS)
        authority.validate_boundary_rows(rows, "verified")
        for field in fields:
            changed = copy.deepcopy(rows)
            changed[0][field] = "tampered"
            with self.subTest(field=field):
                with self.assertRaises(authority.AuthorityError):
                    authority.validate_boundary_rows(changed, "verified")

    def test_receipt_rejects_count_path_and_policy_drift(self) -> None:
        if not PACKAGE.is_dir():
            self.skipTest("ignored saved D3DX scratch evidence is absent")
        path = PACKAGE / "runs/replica-a-apply/boundaries.ready.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        expected = "local-lab/d3dx-gap-two-boundary-scratch-20260814-v1/runs/replica-a-apply/boundaries.tsv"
        authority.validate_receipt(value, "apply", expected)
        for key, changed_value in (
            ("counts", {**value["counts"], "referencesAfter": 234494}),
            ("output", {**value["output"], "path": "C:/escape.tsv"}),
            ("namesAuthorized", True),
            ("metadataAuthorized", True),
        ):
            changed = copy.deepcopy(value)
            changed[key] = changed_value
            with self.subTest(key=key):
                with self.assertRaises(authority.AuthorityError):
                    authority.validate_receipt(changed, "apply", expected)

    def test_topology_rejects_an_unexpected_run(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            runs = root / "runs"
            projects = root / "projects"
            runs.mkdir()
            projects.mkdir()
            for name, files in authority.EXPECTED_RUN_FILES.items():
                folder = runs / name
                folder.mkdir()
                for filename in files:
                    (folder / filename).write_bytes(b"")
            for name in authority.EXPECTED_PROJECTS:
                (projects / name).mkdir()
            authority.verify_topology(root)
            (runs / "unexpected").mkdir()
            with self.assertRaisesRegex(authority.AuthorityError, "run directory census"):
                authority.verify_topology(root)

    def test_artifact_tree_rejects_python_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cache = root / "__pycache__"
            cache.mkdir()
            (cache / "owner.pyc").write_bytes(b"cache")
            with self.assertRaisesRegex(authority.AuthorityError, "Python cache"):
                authority.artifact_tree(root, root / "receipt.json")


if __name__ == "__main__":
    unittest.main()
