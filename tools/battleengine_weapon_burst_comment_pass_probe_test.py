#!/usr/bin/env python3
"""Tests for the BattleEngine weapon/burst comment-pass probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import battleengine_weapon_burst_comment_pass_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"


def write_fixture(root: Path, *, omit_inner_token: bool = False) -> dict[str, Path]:
    dry_log = root / "comments_dry.log"
    apply_log = root / "comments_apply.log"
    metadata = root / "metadata.tsv"

    dry_log.write_text(
        "\n".join(
            [
                "Mode: dry",
                "DRY: 0x00506930 CWeapon__HandleFireBurstEvent",
                "DRY: 0x00505f70 CWeapon__scalar_deleting_dtor",
                "DRY: 0x005069f0 CEngine__SpawnProjectileBurstFromCurrentPreset",
                "DRY: 0x00506010 CGeneralVolume__SpawnBurstFromPresetWithFallback",
                "--- SUMMARY ---",
                "applied=0 skipped=4 missing=0 bad=0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    apply_log.write_text(
        "\n".join(
            [
                "Mode: apply",
                "OK: 0x00506930 CWeapon__HandleFireBurstEvent",
                "OK: 0x00505f70 CWeapon__scalar_deleting_dtor",
                "OK: 0x005069f0 CEngine__SpawnProjectileBurstFromCurrentPreset",
                "OK: 0x00506010 CGeneralVolume__SpawnBurstFromPresetWithFallback",
                "--- SUMMARY ---",
                "applied=4 skipped=0 missing=0 bad=0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    inner_comment = (
        "Inner projectile-burst body reached from CWeapon__HandleFireBurstEvent. "
        "Creates projectiles from the current preset and keeps source CWeapon::Fire and runtime stealth behavior unproven."
    )
    if omit_inner_token:
        inner_comment = "Inner projectile-burst body reached from CWeapon__HandleFireBurstEvent."

    rows = [
        (
            "0x00506930",
            "CWeapon__HandleFireBurstEvent",
            "undefined CWeapon__HandleFireBurstEvent(void)",
            "Weapon table event handler for burst event 0x1389. Not source CWeapon::Fire proof or runtime stealth proof.",
        ),
        (
            "0x00505f70",
            "CWeapon__scalar_deleting_dtor",
            "void * __thiscall CWeapon__scalar_deleting_dtor(void * this, int flags)",
            "Scalar deleting destructor shape with detach/shutdown and conditional free.",
        ),
        (
            "0x005069f0",
            "CEngine__SpawnProjectileBurstFromCurrentPreset",
            "int __fastcall CEngine__SpawnProjectileBurstFromCurrentPreset(void * param_1)",
            inner_comment,
        ),
        (
            "0x00506010",
            "CGeneralVolume__SpawnBurstFromPresetWithFallback",
            "int __fastcall CGeneralVolume__SpawnBurstFromPresetWithFallback(void * param_1)",
            "Shared preset fallback dispatcher with UnitAI/Sentinel/CGeneralVolume callers; provisional owner/name.",
        ),
    ]
    metadata.write_text(
        METADATA_HEADER + "".join("\t".join(row) + "\tOK\n" for row in rows),
        encoding="utf-8",
    )
    return {"dry_log": dry_log, "apply_log": apply_log, "metadata": metadata}


class BattleEngineWeaponBurstCommentPassProbeTests(unittest.TestCase):
    def test_passes_for_clean_logs_and_comment_readback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                dry_log_path=paths["dry_log"],
                apply_log_path=paths["apply_log"],
                metadata_path=paths["metadata"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["candidateClassification"], "weapon-burst-cluster-comments-applied")
        self.assertTrue(report["readback"]["allCommentsPresent"])

    def test_fails_when_inner_comment_loses_source_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), omit_inner_token=True)
            report = probe.build_report(
                dry_log_path=paths["dry_log"],
                apply_log_path=paths["apply_log"],
                metadata_path=paths["metadata"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("0x005069f0" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
