#!/usr/bin/env python3
"""Tests for the BattleEngineData owner-correction probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_battleengine_data_owner_correction_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"


def write_fixture(root: Path, *, omit_load_token: bool = False) -> dict[str, Path]:
    rename_dry = root / "rename_dry.log"
    rename_apply = root / "rename_apply.log"
    comments_dry = root / "comments_dry.log"
    comments_apply = root / "comments_apply.log"
    metadata = root / "metadata_after.tsv"
    xrefs = root / "xrefs_after.tsv"

    renames = [
        ("0x0040f590", "CBattleEngineDataManager__Init", "CBattleEngineData__Initialise"),
        ("0x0040f890", "CBattleEngineDataManager__Clear", "CBattleEngineData__Shutdown"),
        ("0x0040f980", "CBattleEngineDataManager__Load", "CBattleEngineData__LoadFromMemBuffer"),
    ]

    rename_dry.write_text(
        "\n".join(["Mode: args (dry)"] + [f"DRY: {addr} {old} -> {new}" for addr, old, new in renames] + [
            "--- SUMMARY ---",
            "applied=0 skipped=3 missing=0 bad=0",
        ])
        + "\n",
        encoding="utf-8",
    )
    rename_apply.write_text(
        "\n".join(["Mode: args (apply)"] + [f"OK: {addr} {old} -> {new}" for addr, old, new in renames] + [
            "--- SUMMARY ---",
            "applied=3 skipped=0 missing=0 bad=0",
        ])
        + "\n",
        encoding="utf-8",
    )
    comments_dry.write_text(
        "\n".join(["Mode: dry"] + [f"DRY: {addr} {new}" for addr, _, new in renames] + [
            "--- SUMMARY ---",
            "applied=0 skipped=3 missing=0 bad=0",
        ])
        + "\n",
        encoding="utf-8",
    )
    comments_apply.write_text(
        "\n".join(["Mode: apply"] + [f"OK: {addr} {new}" for addr, _, new in renames] + [
            "--- SUMMARY ---",
            "applied=3 skipped=0 missing=0 bad=0",
        ])
        + "\n",
        encoding="utf-8",
    )

    load_note = "CBattleEngineData::Load(CMEMBUFFER&)"
    if omit_load_token:
        load_note = "generic loader"

    rows = [
        (
            "0x0040f590",
            "CBattleEngineData__Initialise",
            "void __fastcall CBattleEngineData__Initialise(undefined4 *param_1)",
            "Source-aligned CBattleEngineData::Initialise default-data setup; writes Standard, Vulcan Cannon 1, Pulse Cannon Pod, Missile Pod, Animated Explosion Emitter 2, cockpit2.msh, store defaults, and stealth zero. signature and parameter names deferred.",
        ),
        (
            "0x0040f890",
            "CBattleEngineData__Shutdown",
            "void __fastcall CBattleEngineData__Shutdown(int param_1)",
            "Source-aligned CBattleEngineData::Shutdown cleanup; frees mConfigurationName, mJetWeapons, mWalkerWeapons, mExplosion, mAugWeapon, mPrimaryWeapon, and mCockpit. signature and parameter names deferred.",
        ),
        (
            "0x0040f980",
            "CBattleEngineData__LoadFromMemBuffer",
            "void __fastcall CBattleEngineData__LoadFromMemBuffer(undefined4 *param_1)",
            f"Source-aligned {load_note}; calls CBattleEngineData__Shutdown first, reads versioned fields through DXMemBuffer__ReadBytes, appends walker/jet weapon names, and applies version fallback defaults. signature and parameter names deferred.",
        ),
    ]
    metadata.write_text(METADATA_HEADER + "".join("\t".join(row) + "\tOK\n" for row in rows), encoding="utf-8")
    xrefs.write_text(
        "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
        "0040f590\tCBattleEngineData__Initialise\t00510927\t00510800\tCWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData\tUNCONDITIONAL_CALL\n"
        "0040f890\tCBattleEngineData__Shutdown\t0040f98a\t0040f980\tCBattleEngineData__LoadFromMemBuffer\tUNCONDITIONAL_CALL\n"
        "0040f980\tCBattleEngineData__LoadFromMemBuffer\t00510a21\t00510800\tCWorldPhysicsManager__ReloadDefaultPhysicsAndBattleEngineData\tUNCONDITIONAL_CALL\n",
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


class GhidraBattleEngineDataOwnerCorrectionProbeTests(unittest.TestCase):
    def test_passes_for_clean_owner_correction(self) -> None:
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
        self.assertEqual(report["candidateClassification"], "battleengine-data-owner-names-corrected")
        self.assertTrue(report["readback"]["allNamesAndCommentsPresent"])
        self.assertTrue(report["xrefs"]["loadCallsShutdown"])

    def test_fails_when_load_comment_loses_mem_buffer_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), omit_load_token=True)
            report = probe.build_report(
                rename_dry_log_path=paths["rename_dry"],
                rename_apply_log_path=paths["rename_apply"],
                comments_dry_log_path=paths["comments_dry"],
                comments_apply_log_path=paths["comments_apply"],
                metadata_path=paths["metadata"],
                xrefs_path=paths["xrefs"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("0x0040f980" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
