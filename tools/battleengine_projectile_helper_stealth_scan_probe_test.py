#!/usr/bin/env python3
"""Tests for the BattleEngine projectile helper stealth scan probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import battleengine_projectile_helper_stealth_scan_probe as probe


INDEX = (
    "address\tname\tsignature\tstatus\n"
    "0x00406560\tCBattleEngine__UpdateAutoTargetSetAndFireProjectiles\t"
    "void __fastcall CBattleEngine__UpdateAutoTargetSetAndFireProjectiles(int param_1)\tOK\n"
)


def write_fixture(root: Path, body: str) -> Path:
    decompile_dir = root / "decompile"
    decompile_dir.mkdir(parents=True, exist_ok=True)
    (decompile_dir / "index.tsv").write_text(INDEX, encoding="utf-8")
    (decompile_dir / "00406560_CBattleEngine__UpdateAutoTargetSetAndFireProjectiles.c").write_text(
        body,
        encoding="utf-8",
    )
    return decompile_dir


def write_source_fixture(root: Path) -> Path:
    source = root / "BattleEngine.cpp"
    source.write_text(
        """
        void CBattleEngine::WeaponFired()
        {
          BOOL fired=mWalkerPart->WeaponFired();
          fired|=mJetPart->WeaponFired();
          if (fired)
            mStealth=0.0f;
        }
        """,
        encoding="utf-8",
    )
    return source


class BattleEngineProjectileHelperStealthScanProbeTests(unittest.TestCase):
    def test_passes_when_projectile_helper_has_no_stealth_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            decompile_dir = write_fixture(
                root,
                """
                void __fastcall CBattleEngine__UpdateAutoTargetSetAndFireProjectiles(int param_1) {
                  CBattleEngine__GetIndexedEntry(*(void **)(param_1 + 0x57c));
                  CBattleEngine__IsIndexedEntryUsable(*(void **)(param_1 + 0x57c));
                  CGeneralVolume__ResolveCurrentOrFallbackEntry(*(void **)(param_1 + 0x578));
                  CBattleEngine__IsResolvedEntryUsable(*(void **)(param_1 + 0x578));
                  CBattleEngine__CalcUnitOverCrossHair((void *)param_1, 0, 0, 0);
                  CBattleEngine__IsWeaponModeCompatibleWithMountState((void *)param_1, 0, 0);
                  CBattleEngine__DoesTargetMaskMatchProfileByDistance(0, 0, 0);
                  CBattleEngine__SelectNearestForwardTargetFromGlobalSet();
                  CBattleEngine__AddProjectile(0, 0.0f, 0);
                  CSPtrSet__Remove((undefined4 *)(param_1 + 0x294), 0);
                  CBattleEngine__GetProfileField9CByDistance(0);
                  fVar11 = (float10)_DAT_005d85fc;
                  dVar13 = dVar13 * (double)(float)(fVar1 - fVar12 * fVar11);
                }
                """,
            )
            source = write_source_fixture(root)

            report = probe.build_report(decompile_dir, source)

            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["stealthWriteTokenHits"], {})
            self.assertEqual(report["helperClassification"], "projectile-targeting-helper-no-stealth-reset-observed")

    def test_fails_if_stealth_write_token_is_observed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            decompile_dir = write_fixture(
                root,
                """
                void __fastcall CBattleEngine__UpdateAutoTargetSetAndFireProjectiles(int param_1) {
                  CBattleEngine__GetIndexedEntry(*(void **)(param_1 + 0x57c));
                  CBattleEngine__IsIndexedEntryUsable(*(void **)(param_1 + 0x57c));
                  CGeneralVolume__ResolveCurrentOrFallbackEntry(*(void **)(param_1 + 0x578));
                  CBattleEngine__IsResolvedEntryUsable(*(void **)(param_1 + 0x578));
                  CBattleEngine__CalcUnitOverCrossHair((void *)param_1, 0, 0, 0);
                  CBattleEngine__IsWeaponModeCompatibleWithMountState((void *)param_1, 0, 0);
                  CBattleEngine__DoesTargetMaskMatchProfileByDistance(0, 0, 0);
                  CBattleEngine__SelectNearestForwardTargetFromGlobalSet();
                  CBattleEngine__AddProjectile(0, 0.0f, 0);
                  CSPtrSet__Remove((undefined4 *)(param_1 + 0x294), 0);
                  *(undefined4 *)(param_1 + 0x5d8) = 0;
                }
                """,
            )
            source = write_source_fixture(root)

            report = probe.build_report(decompile_dir, source)

            self.assertEqual(report["status"], "FAIL")
            self.assertIn("*(undefined4 *)(param_1 + 0x5d8) = 0", report["stealthWriteTokenHits"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
