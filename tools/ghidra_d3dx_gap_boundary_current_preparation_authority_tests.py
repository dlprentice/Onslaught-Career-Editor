#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Focused tests for the db.18617 two-function D3DX preparation authority."""

from __future__ import annotations

import copy
import hashlib
import os
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

import ghidra_d3dx_gap_boundary_current_preparation_authority as authority


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / f"local-lab/{authority.PACKAGE_NAME}"
DEFAULT_SCRATCH = ROOT / f"local-lab/{authority.SCRATCH_PACKAGE_NAME}"
if not DEFAULT_SCRATCH.is_dir():
    DEFAULT_SCRATCH = (
        ROOT.parent
        / "Onslaught-Career-Editor"
        / f"local-lab/{authority.SCRATCH_PACKAGE_NAME}"
    )
SCRATCH = Path(os.environ.get("BEA_D3DX_SCRATCH_PACKAGE", DEFAULT_SCRATCH))
RECEIPT = PACKAGE / "preparation-authority.ready.json"


class PureContractTests(unittest.TestCase):
    def test_exact_pre_post_contract(self) -> None:
        self.assertEqual(authority.POLICY, "PREPARATION_ONLY")
        self.assertEqual(
            (authority.PRE_FUNCTIONS, authority.POST_FUNCTIONS), (8327, 8329)
        )
        self.assertEqual((authority.PRE_RANGES, authority.POST_RANGES), (8457, 8459))
        self.assertEqual(
            (authority.PRE_OWNED, authority.POST_OWNED), (1_811_443, 1_811_691)
        )
        self.assertEqual(authority.POST_OWNED - authority.PRE_OWNED, 248)
        self.assertEqual(
            (authority.PRE_INSTRUCTIONS, authority.POST_INSTRUCTIONS),
            (551_143, 551_143),
        )
        self.assertEqual(
            (authority.PRE_REFERENCES, authority.POST_REFERENCES),
            (234_478, 234_478),
        )
        self.assertAlmostEqual(
            100.0 * authority.POST_OWNED / authority.TEXT_BYTES,
            93.9129663986166,
            places=12,
        )

    def test_two_target_contract_closes_exact_bytes_and_instructions(self) -> None:
        self.assertEqual(set(authority.TARGETS), {"0x00595fc9", "0x00596028"})
        self.assertEqual(
            sum(int(value["bytes"]) for value in authority.TARGETS.values()), 248
        )
        self.assertEqual(
            sum(int(value["instructions"]) for value in authority.TARGETS.values()),
            92,
        )
        for address, target in authority.TARGETS.items():
            start, end = target["range"].split("-")
            self.assertEqual(start, address)
            self.assertEqual(int(end, 16) - int(start, 16), int(target["bytes"]))
            self.assertRegex(target["rangeSha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(target["bodySha256"], r"^[0-9a-f]{64}$")
            self.assertEqual(target["name"], f"FUN_{address[2:]}")

    def test_repo_manifest_and_mutator_are_exact(self) -> None:
        for relative, expected in (
            (authority.MANIFEST_REL, authority.MANIFEST_STAMP),
            ("tools/GhidraApplyD3dxGapBoundariesV2.java", authority.MUTATOR_STAMP),
        ):
            path = ROOT / relative
            self.assertEqual(
                (path.stat().st_size, authority.sha256_file(path)),
                expected,
                relative,
            )

    def test_project_digest_is_ordered_and_unambiguous(self) -> None:
        value = {
            "files": [
                {"relative_path": "a", "size": 1, "sha256": "1" * 64},
                {"relative_path": "b", "size": 2, "sha256": "2" * 64},
            ]
        }
        raw = ("1" * 64 + "\t1\ta\n" + "2" * 64 + "\t2\tb\n").encode()
        self.assertEqual(authority.project_digest(value), hashlib.sha256(raw).hexdigest())
        value["files"].reverse()
        with self.assertRaisesRegex(authority.AuthorityError, "ordered"):
            authority.project_digest(value)

    def test_recorded_path_binding_rejects_role_substitution(self) -> None:
        expected = ROOT / "reverse-engineering/ghidra"
        authority.require_recorded_path(str(expected), expected, "fixture")
        with self.assertRaisesRegex(authority.AuthorityError, "recorded root"):
            authority.require_recorded_path(
                str(ROOT / "local-lab/other-project"), expected, "fixture"
            )

    def test_containment_path_is_taken_from_the_exact_log_argument(self) -> None:
        expected = Path.home() / (
            "AppData/Local/Temp/bea-d3dx-containment-20260814/escaped-ready.json"
        )
        text = f"Execute script: Tool.java 'inside.tsv' '{expected}' 'apply'"
        self.assertEqual(
            authority.recorded_escape_path(text, "escaped-ready.json"), expected
        )
        with self.assertRaisesRegex(authority.AuthorityError, "recorded containment"):
            authority.recorded_escape_path(text, "escaped-boundaries.tsv")

    def test_artifact_tree_excludes_receipt_and_rejects_python_cache(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            payload = root / "payload.txt"
            payload.write_text("payload\n", encoding="utf-8")
            receipt = root / "receipt.json"
            receipt.write_text("{}\n", encoding="utf-8")
            tree = authority.artifact_tree(root, receipt)
            self.assertEqual(tree["files"], 1)
            self.assertEqual(tree["bytes"], payload.stat().st_size)
            cache = root / "__pycache__"
            cache.mkdir()
            (cache / "poison.pyc").write_bytes(b"poison")
            with self.assertRaisesRegex(authority.AuthorityError, "Python cache"):
                authority.artifact_tree(root, receipt)


RETAINED_AVAILABLE = PACKAGE.is_dir() and SCRATCH.is_dir()


@unittest.skipUnless(RETAINED_AVAILABLE, "retained D3DX preparation evidence unavailable")
class RetainedEvidenceTests(unittest.TestCase):
    def test_every_boundary_column_is_fail_closed(self) -> None:
        fields, original = authority.read_tsv(
            PACKAGE / "runs/replica-a-apply/boundaries.tsv"
        )
        self.assertEqual(fields, authority.BOUNDARY_FIELDS)
        authority.validate_boundary_rows(original, "created")
        for field in fields:
            with self.subTest(field=field):
                rows = copy.deepcopy(original)
                rows[0][field] = rows[0][field] + "__DRIFT"
                with self.assertRaises(authority.AuthorityError):
                    authority.validate_boundary_rows(rows, "created")

    def test_all_six_physical_projects_are_exactly_pinned(self) -> None:
        result, artifacts, _ceremony_repo = authority.verify_projects(
            PACKAGE, ROOT, Path.home() / "Ghidra/Projects"
        )
        self.assertEqual(
            result["pre"]["canonicalInventorySha256"], authority.PRE_PROJECT_SHA256
        )
        self.assertEqual(set(result["postReplicas"]), {"a", "b"})
        self.assertEqual(set(result["controlProjects"]), set(authority.CONTROL_PROJECT_SHA256))
        self.assertEqual(len(artifacts), 6)

    def test_controls_restore_exact_pre_semantics(self) -> None:
        artifacts = authority.verify_controls(PACKAGE)
        self.assertGreater(len(artifacts), 0)
        for run in (
            "failure-after-one-readback",
            "failure-post-inner-readback",
            "containment-output-readback",
            "containment-ready-readback",
        ):
            self.assertEqual(
                authority.sha256_file(PACKAGE / f"runs/{run}/functions.tsv"),
                authority.PRE_FUNCTIONS_STAMP[1],
            )

    def test_historical_scratch_tree_is_preserved_exactly(self) -> None:
        result = authority.verify_scratch(PACKAGE, SCRATCH)
        self.assertEqual(result["tree"]["sha256"], authority.SCRATCH_TREE_SHA256)
        self.assertEqual(result["verification"], "EXACT_SEALED_TREE_REHASH")
        self.assertEqual(
            result["currentRootReplay"],
            "INTENTIONALLY_SUPERSEDED_BY_DB18617_REPLICAS",
        )

    @unittest.skipUnless(RECEIPT.is_file(), "preparation receipt is not sealed yet")
    def test_saved_preparation_authority_replays(self) -> None:
        result = authority.verify(
            PACKAGE,
            RECEIPT,
            ROOT,
            Path.home() / "Ghidra/Projects",
            SCRATCH,
        )
        self.assertEqual(result["verdict"], "PREPARATION_READY_LIVE_FORBIDDEN")
        self.assertEqual(result["post"]["functions"], 8329)
        self.assertEqual(result["proof"]["postInnerCompensationControls"], 1)
        self.assertIs(result["mutationAuthorized"], False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
