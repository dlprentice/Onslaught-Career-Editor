#!/usr/bin/env python3
"""Tests for the deferred 0x00410c50 Ghidra correction probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_deferred_00410c50_correction_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
XREFS_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"


def write_fixture(root: Path, *, overclaim_source_identity: bool = False) -> dict[str, Path]:
    rename_dry = root / "rename_dry.log"
    rename_apply = root / "rename_apply.log"
    comments_dry = root / "comments_dry.log"
    comments_apply = root / "comments_apply.log"
    metadata = root / "metadata_after.tsv"
    xrefs = root / "xrefs_after.tsv"

    old_name = "OID_Unk_005078f0__Wrapper_00410c50"
    new_name = "CMonitor__UpdateMovementTransitionAndEffects"
    address = "0x00410c50"

    rename_dry.write_text(
        "\n".join(
            [
                "Mode: args (dry)",
                f"DRY: {address} {old_name} -> {new_name}",
                "--- SUMMARY ---",
                "applied=0 skipped=1 missing=0 bad=0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    rename_apply.write_text(
        "\n".join(
            [
                "Mode: args (apply)",
                f"OK: {address} {old_name} -> {new_name}",
                "--- SUMMARY ---",
                "applied=1 skipped=0 missing=0 bad=0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    comments_dry.write_text(
        "\n".join(
            [
                "Mode: dry",
                f"DRY: {address} {new_name}",
                "--- SUMMARY ---",
                "applied=0 skipped=1 missing=0 bad=0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    comments_apply.write_text(
        "\n".join(
            [
                "Mode: apply",
                f"OK: {address} {new_name}",
                "--- SUMMARY ---",
                "applied=1 skipped=0 missing=0 bad=0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    boundary = "No dedicated Monitor source file is present in references/Onslaught; signature and parameter names deferred."
    if overclaim_source_identity:
        boundary = "Source-exact Monitor method identity is now proven."

    comment = (
        "Source-aligned owner/behavior correction without source-exact Monitor method identity. "
        "Evidence: only checked caller is CMonitor__Process; body updates tracked render pairs, "
        "movement/terrain integration, transition timers, impact effects, and hostile-environment penalty "
        "through CMonitor__UpdateTrackedRenderPair, CMonitor__IntegrateMovementAgainstTerrain, "
        "CMonitor__ComputeTerrainVelocityScalar, CMonitor__SpawnGroundOrAirImpactEffect, and "
        f"CMonitor__ApplyHostileEnvironmentPenalty. {boundary}"
    )
    metadata.write_text(
        METADATA_HEADER
        + "\t".join(
            [
                address,
                new_name,
                "void __fastcall CMonitor__UpdateMovementTransitionAndEffects(void * param_1)",
                comment,
                "OK",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    xrefs.write_text(
        XREFS_HEADER
        + "00410c50\tCMonitor__UpdateMovementTransitionAndEffects\t00408d61\t004081c0\tCMonitor__Process\tUNCONDITIONAL_CALL\n"
        + "005078f0\tCMonitor__UpdateTrackedRenderPair\t00410c81\t00410c50\tCMonitor__UpdateMovementTransitionAndEffects\tUNCONDITIONAL_CALL\n"
        + "00411630\tCMonitor__IntegrateMovementAgainstTerrain\t00410e08\t00410c50\tCMonitor__UpdateMovementTransitionAndEffects\tUNCONDITIONAL_CALL\n"
        + "00411aa0\tCMonitor__ComputeTerrainVelocityScalar\t00411068\t00410c50\tCMonitor__UpdateMovementTransitionAndEffects\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )

    return {
        "rename_dry": rename_dry,
        "rename_apply": rename_apply,
        "comments_dry": comments_dry,
        "comments_apply": comments_apply,
        "metadata": metadata,
        "xrefs": xrefs,
    }


class GhidraDeferred00410c50CorrectionProbeTests(unittest.TestCase):
    def test_passes_for_conservative_monitor_behavior_correction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                rename_dry_log_path=paths["rename_dry"],
                rename_apply_log_path=paths["rename_apply"],
                comments_dry_log_path=paths["comments_dry"],
                comments_apply_log_path=paths["comments_apply"],
                metadata_path=paths["metadata"],
                xrefs_path=paths["xrefs"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["candidateClassification"], "deferred-monitor-body-renamed-commented-signature-deferred")
        self.assertTrue(report["readback"]["nameAndCommentPresent"])
        self.assertTrue(report["xrefs"]["processCallsTarget"])
        self.assertTrue(report["xrefs"]["targetCallsMovementHelpers"])

    def test_fails_when_comment_overclaims_source_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), overclaim_source_identity=True)
            report = probe.build_report(
                rename_dry_log_path=paths["rename_dry"],
                rename_apply_log_path=paths["rename_apply"],
                comments_dry_log_path=paths["comments_dry"],
                comments_apply_log_path=paths["comments_apply"],
                metadata_path=paths["metadata"],
                xrefs_path=paths["xrefs"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("source boundary" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
