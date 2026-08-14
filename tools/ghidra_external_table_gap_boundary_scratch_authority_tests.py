#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import tempfile
import unittest
import sys
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ghidra_external_table_gap_boundary_scratch_authority as authority


class ExternalTableGapBoundaryScratchAuthorityTests(unittest.TestCase):
    def test_preserved_formal_campaign_reproduces_semantically(self) -> None:
        if not authority.LANE.is_dir():
            self.skipTest("ignored saved scratch evidence is absent")
        self.assertEqual(
            authority.verify_campaign(),
            {
                "targets": 79,
                "bodyBytes": 9234,
                "externalInstructions": 3319,
                "ghidraBodyInstructions": 3318,
                "rankCounts": {"P0": 12, "P1": 20, "P2": 47},
                "preFunctions": 8201,
                "postFunctions": 8280,
                "preInstructions": 550982,
                "postInstructions": 550991,
                "instructionDelta": 9,
                "preReferences": 234537,
                "postReferences": 234495,
                "referenceDelta": -42,
                "preservedPreFunctionRows": 8201,
                "replicas": 2,
                "adverseControls": 2,
                "externalPathPreflights": 2,
                "actualProjectTrees": 2,
                "readonlyRestoreProofs": 1,
                "reusedExactPositiveReplicas": 2,
            },
        )

    def test_missing_saved_evidence_is_a_clean_skip(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            case = self.__class__(
                "test_preserved_formal_campaign_reproduces_semantically"
            )
            result = unittest.TestResult()
            with mock.patch.object(authority, "LANE", Path(temporary) / "absent"):
                case.run(result)
        self.assertEqual(1, len(result.skipped))
        self.assertEqual([], result.errors)
        self.assertEqual([], result.failures)

    def test_explicit_verify_still_requires_saved_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            missing = Path(temporary) / "missing.ready.json"
            with mock.patch.object(authority, "READY", missing):
                with self.assertRaisesRegex(authority.AuthorityError, "invalid JSON"):
                    authority.verify()

    def test_full_pre_row_gate_checks_every_field(self) -> None:
        header = "address\tname\tsignature\n"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            before = root / "before.tsv"
            after = root / "after.tsv"
            before.write_text(header + "0x1\tname\tvoid f(void)\n", encoding="utf-8")
            after.write_text(header + "0x1\tname\tint f(void)\n", encoding="utf-8")
            with (
                mock.patch.object(authority, "PRE_FUNCTIONS", 1),
                mock.patch.object(authority, "POST_FUNCTIONS", 1),
            ):
                with self.assertRaisesRegex(authority.AuthorityError, "full PRE row drift"):
                    authority.verify_full_pre_rows_equal(before, after, "fixture")

    def test_receipt_paths_are_repository_relative_posix(self) -> None:
        authority.verify_portable_path("local-lab/run/output.tsv", "local-lab/run/output.tsv", "fixture")
        for value in ("C:/absolute/output.tsv", "local-lab\\run\\output.tsv", "/root/output.tsv"):
            with self.assertRaises(authority.AuthorityError):
                authority.verify_portable_path(value, value, "fixture")

    def test_program_parser_rejects_duplicate_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "program.tsv"
            path.write_text("metric\tvalue\nfunctions\t8201\nfunctions\t8280\n", encoding="utf-8")
            with self.assertRaisesRegex(authority.AuthorityError, "bad program row"):
                authority.program_rows(path)

    def test_exact_stamp_rejects_one_byte_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "artifact.bin"
            path.write_bytes(b"exact")
            expected = (path.stat().st_size, authority.sha256_file(path))
            authority.verify_stamp(path, expected, "fixture")
            path.write_bytes(b"drift")
            with self.assertRaisesRegex(authority.AuthorityError, "SHA-256 drift"):
                authority.verify_stamp(path, expected, "fixture")

    def test_actual_project_tree_rehash_rejects_byte_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            gpr = root / "BEA.gpr"
            db = root / "BEA.rep/idata/00/~00000000.db/db.18612.gbf"
            db.parent.mkdir(parents=True)
            gpr.write_bytes(b"")
            db.write_bytes(b"db")
            rows = [
                ("BEA.gpr", 0, authority.sha256_file(gpr)),
                (
                    "BEA.rep/idata/00/~00000000.db/db.18612.gbf",
                    2,
                    authority.sha256_file(db),
                ),
            ]
            digest = authority.hashlib.sha256()
            for relative, size, file_hash in rows:
                digest.update(
                    f"{file_hash}\t{size}\t{relative}\n".encode("utf-8")
                )
            with (
                mock.patch.object(authority, "BASE_PROJECT", (2, 2)),
                mock.patch.object(authority, "DB_18612", rows[1][1:]),
                mock.patch.object(
                    authority, "CANONICAL_PROJECT_SHA256", digest.hexdigest()
                ),
            ):
                authority.verify_actual_project_tree(root, "fixture")
                db.write_bytes(b"dB")
                with self.assertRaisesRegex(
                    authority.AuthorityError, "actual canonical inventory mismatch"
                ):
                    authority.verify_actual_project_tree(root, "fixture")

    def test_restore_probe_binds_log_markers_and_safe_command(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            retained = root / "BEA-open-probe-fixture"
            retained.mkdir()
            receipt = root / "base-restore-v2.ready.json"
            log = root / "base-restore-v2.ready.open-probe.log"
            console = root / "base-restore-v2.console.log"
            sentinel = (
                "GHIDRA_PROJECT_OPEN_PROBE_OK program=BEA.exe "
                f"md5={authority.PROGRAM_MD5} "
                f"sha256={authority.PROGRAM_SHA256} functions=8425"
            )
            log.write_text(
                "INFO  REPORT: Processing read-only project file: /BEA.exe\n"
                + sentinel
                + "\n",
                encoding="utf-8",
            )
            console.write_text("project=BEA ReadOnlyOpen=PASS\n", encoding="utf-8")
            argv = [
                "analyzeHeadless.bat",
                str(retained),
                "BEA",
                "-process",
                "BEA.exe",
                "-readOnly",
                "-noanalysis",
                "-postScript",
                "GhidraProjectOpenProbe.java",
            ]
            opened = {
                "opened": True,
                "contentStable": True,
                "exitCode": 0,
                "observedFunctionCount": 8425,
                "observedProgramSha256": authority.PROGRAM_SHA256,
                "commandArgv": argv,
                "probeLog": {
                    "path": log.name,
                    "bytes": log.stat().st_size,
                    "sha256": authority.sha256_file(log),
                },
            }
            restore = {"readonlyOpen": opened}
            authority.verify_readonly_restore(restore, retained, receipt)

            opened["commandArgv"] = argv + ["-commit"]
            with self.assertRaisesRegex(authority.AuthorityError, "forbids -commit"):
                authority.verify_readonly_restore(restore, retained, receipt)
            opened["commandArgv"] = argv

            log.write_text(log.read_text(encoding="utf-8") + "ERROR injected\n")
            opened["probeLog"]["bytes"] = log.stat().st_size
            opened["probeLog"]["sha256"] = authority.sha256_file(log)
            with self.assertRaisesRegex(authority.AuthorityError, "error marker"):
                authority.verify_readonly_restore(restore, retained, receipt)

            log.write_text(
                "INFO  REPORT: Processing read-only project file: /BEA.exe\n",
                encoding="utf-8",
            )
            opened["probeLog"]["bytes"] = log.stat().st_size
            opened["probeLog"]["sha256"] = authority.sha256_file(log)
            with self.assertRaisesRegex(authority.AuthorityError, "success sentinel"):
                authority.verify_readonly_restore(restore, retained, receipt)

            opened["probeLog"]["sha256"] = "0" * 64
            with self.assertRaisesRegex(authority.AuthorityError, "SHA-256 drift"):
                authority.verify_readonly_restore(restore, retained, receipt)

    def test_payload_keeps_live_and_tracked_mutation_unauthorized(self) -> None:
        with (
            mock.patch.object(authority, "verify_campaign", return_value={"targets": 79}),
            mock.patch.object(authority, "artifact_tree", return_value={"fileCount": 1}),
            mock.patch.object(
                authority,
                "stamp",
                return_value={"path": "fixture", "bytes": 1, "sha256": "0" * 64},
            ),
        ):
            payload = authority.build_payload("2026-08-14T00:00:00Z")
        self.assertEqual(payload["verdict"], "SCRATCH_READY_LIVE_FORBIDDEN")
        self.assertIs(payload["liveMutationAuthorized"], False)
        self.assertIs(payload["trackedGhidraMutationAuthorized"], False)

    def test_authority_pins_exact_db_18612_and_project_inventory(self) -> None:
        self.assertEqual(
            authority.DB_18612,
            (
                68321280,
                "424775377ea0f40d9e429c9219b9310d427760acc40548dbc588ca285f932f7b",
            ),
        )
        self.assertEqual(
            authority.CANONICAL_PROJECT_SHA256,
            "91776fb4a67579950afc4fb3b48ea8a866733628aecfdae7a2cb918c615fe211",
        )


if __name__ == "__main__":
    unittest.main()
