#!/usr/bin/env python3
"""Tests for the Ghidra vector math rename probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_vector_math_rename_probe as probe


INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"


def write_fixture(root: Path, *, omit_normalize_token: bool = False) -> dict[str, Path]:
    dry_log = root / "rename_dry.log"
    apply_log = root / "rename_apply.log"
    decompile_dir = root / "decompile_after"
    decompile_dir.mkdir()
    xrefs = root / "xrefs_after.tsv"

    dry_log.write_text(
        "\n".join(
            [
                "DRY: 0x004026b0 SQRT__Wrapper_004026b0 -> Vec3__Magnitude",
                "DRY: 0x00406d50 SQRT__Wrapper_00406d50 -> Vec3__NormalizeInPlace",
                "--- SUMMARY ---",
                "applied=0 skipped=2 missing=0 bad=0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    apply_log.write_text(
        "\n".join(
            [
                "OK: 0x004026b0 SQRT__Wrapper_004026b0 -> Vec3__Magnitude",
                "OK: 0x00406d50 SQRT__Wrapper_00406d50 -> Vec3__NormalizeInPlace",
                "--- SUMMARY ---",
                "applied=2 skipped=0 missing=0 bad=0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (decompile_dir / "index.tsv").write_text(
        INDEX_HEADER
        + "0x004026b0\tVec3__Magnitude\tdouble __fastcall Vec3__Magnitude(void * param_1)\tOK\n"
        + "0x00406d50\tVec3__NormalizeInPlace\tvoid __fastcall Vec3__NormalizeInPlace(void * param_1)\tOK\n",
        encoding="utf-8",
    )
    (decompile_dir / "004026b0_Vec3__Magnitude.c").write_text(
        "return (double)SQRT(*(float *)((int)param_1 + 8) + *(float *)((int)param_1 + 4) + *(float *)param_1);",
        encoding="utf-8",
    )
    normalize_text = "fVar1 = SQRT(*(float *)((int)param_1 + 8));\nfVar1 = _DAT_005d8568 / fVar1;\n"
    if omit_normalize_token:
        normalize_text = "fVar1 = SQRT(*(float *)param_1);\n"
    (decompile_dir / "00406d50_Vec3__NormalizeInPlace.c").write_text(normalize_text, encoding="utf-8")
    xrefs.write_text(
        XREF_HEADER
        + "004026b0\tVec3__Magnitude\t0040b750\t0040b6d0\tCBattleEngine__HandleAutoAim\tUNCONDITIONAL_CALL\n"
        + "00406d50\tVec3__NormalizeInPlace\t00407e00\t00407a50\tCMonitor__UpdateCameraVectorsAndInput\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    return {
        "dry_log": dry_log,
        "apply_log": apply_log,
        "decompile_index": decompile_dir / "index.tsv",
        "decompile_dir": decompile_dir,
        "xrefs": xrefs,
    }


class GhidraVectorMathRenameProbeTests(unittest.TestCase):
    def test_passes_for_clean_logs_and_readback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                dry_log_path=paths["dry_log"],
                apply_log_path=paths["apply_log"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["candidateClassification"], "vector-math-helpers-renamed")
        self.assertTrue(report["readback"]["magnitudeRenamed"])
        self.assertTrue(report["readback"]["normalizeInPlaceRenamed"])
        self.assertTrue(report["evidence"]["magnitudeShapePresent"])
        self.assertTrue(report["evidence"]["normalizeInPlaceShapePresent"])

    def test_fails_when_normalize_shape_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), omit_normalize_token=True)
            report = probe.build_report(
                dry_log_path=paths["dry_log"],
                apply_log_path=paths["apply_log"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("normalize" in failure.lower() for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
