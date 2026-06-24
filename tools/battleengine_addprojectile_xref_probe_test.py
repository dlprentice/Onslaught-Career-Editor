#!/usr/bin/env python3
"""Tests for the BattleEngine AddProjectile xref probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import battleengine_addprojectile_xref_probe as probe


XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"


def write_xrefs(root: Path, rows: str) -> Path:
    path = root / "addprojectile_xrefs.tsv"
    path.write_text(XREF_HEADER + rows, encoding="utf-8")
    return path


class BattleEngineAddProjectileXrefProbeTests(unittest.TestCase):
    def test_passes_when_all_addprojectile_xrefs_are_from_projectile_helper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            xrefs = write_xrefs(
                Path(tmp),
                "\n".join(
                    [
                        "00406fc0\tCBattleEngine__AddProjectile\t004068d9\t00406560\tCBattleEngine__UpdateAutoTargetSetAndFireProjectiles\tUNCONDITIONAL_CALL",
                        "00406fc0\tCBattleEngine__AddProjectile\t00406a51\t00406560\tCBattleEngine__UpdateAutoTargetSetAndFireProjectiles\tUNCONDITIONAL_CALL",
                        "00406fc0\tCBattleEngine__AddProjectile\t00406aae\t00406560\tCBattleEngine__UpdateAutoTargetSetAndFireProjectiles\tUNCONDITIONAL_CALL",
                        "00406fc0\tCBattleEngine__AddProjectile\t00406d06\t00406560\tCBattleEngine__UpdateAutoTargetSetAndFireProjectiles\tUNCONDITIONAL_CALL",
                    ]
                )
                + "\n",
            )

            report = probe.build_report(xrefs)

            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["callerClassification"], "addprojectile-xrefs-confined-to-projectile-helper")
            self.assertEqual(report["xrefRowCount"], 4)
            self.assertEqual(report["unexpectedCallerRows"], [])

    def test_fails_when_addprojectile_has_unexpected_non_helper_caller(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            xrefs = write_xrefs(
                Path(tmp),
                "\n".join(
                    [
                        "00406fc0\tCBattleEngine__AddProjectile\t004068d9\t00406560\tCBattleEngine__UpdateAutoTargetSetAndFireProjectiles\tUNCONDITIONAL_CALL",
                        "00406fc0\tCBattleEngine__AddProjectile\t00409999\t00409000\tCBattleEngine__PossibleWeaponFireWrapper\tUNCONDITIONAL_CALL",
                    ]
                )
                + "\n",
            )

            report = probe.build_report(xrefs)

            self.assertEqual(report["status"], "FAIL")
            self.assertEqual(len(report["unexpectedCallerRows"]), 1)
            self.assertIn("unexpected AddProjectile caller", report["failures"][0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
