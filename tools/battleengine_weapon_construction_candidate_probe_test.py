#!/usr/bin/env python3
"""Tests for the BattleEngine weapon construction candidate probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import battleengine_weapon_construction_candidate_probe as probe


INDEX_TEXT = """address\tname\tsignature\tstatus
0x0050f6d0\tCWorldPhysicsManager__CreateWeaponByIndex\tundefined CWorldPhysicsManager__CreateWeaponByIndex(void)\tOK
0x00505e00\tCEquipment__ctor_like_00505e00\tint __thiscall CEquipment__ctor_like_00505e00(void * this, void * param_1, int param_2, int param_3)\tOK
0x00506930\t<none>\t<none>\tMISSING
"""

CREATE_WEAPON_TEXT = """
pvVar3 = (void *)OID__AllocObject(0xb0,0x3d,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_0063d798,0xc4);
iVar4 = CEquipment__ctor_like_00505e00(pvVar3,pvVar2,param_2,unaff_EDI);
"""

CTOR_TEXT = """
*(undefined ***)this = &PTR_LAB_005dfc94;
*(void **)((int)this + 0xa4) = param_1;
"""

VTABLE_TEXT = """slot\tentry_addr\tptr\tptr_name\tptr_signature
0\t005dfc94\t00506930\t<none>\t<none>
1\t005dfc98\t00505f70\tCWeapon__VFunc_01_00505f70\tvoid * __thiscall CWeapon__VFunc_01_00505f70(void * this, void * param_1, int param_2)
2\t005dfc9c\t004bacb0\tCMonitor__Shutdown_Core\tvoid __fastcall CMonitor__Shutdown_Core(void * this)
"""

BODY_DISASM_TEXT = """address\tbytes\tmnemonic\toperands
00506a1f\tE8 BC 58 F0 FF\tCALL\t0x0040c2e0
00506aae\tE8 ED 8C 00 00\tCALL\t0x0050f7a0
005074d3\tE8 D8 35 FD FF\tCALL\t0x004daab0
005074c9\tE8 92 FB EF FF\tCALL\t0x00407060
00507871\tE8 CA 4A F0 FF\tCALL\t0x0040c340
"""


def write_fixture(root: Path, *, missing_projectile_call: bool = False) -> dict[str, Path]:
    paths = {
        "index": root / "index.tsv",
        "create_weapon": root / "create_weapon.c",
        "ctor": root / "ctor.c",
        "vtable": root / "vtable.tsv",
        "body": root / "body.tsv",
    }
    paths["index"].write_text(INDEX_TEXT, encoding="utf-8")
    paths["create_weapon"].write_text(CREATE_WEAPON_TEXT, encoding="utf-8")
    paths["ctor"].write_text(CTOR_TEXT, encoding="utf-8")
    paths["vtable"].write_text(VTABLE_TEXT, encoding="utf-8")
    body_text = BODY_DISASM_TEXT.replace("00506aae\tE8 ED 8C 00 00\tCALL\t0x0050f7a0\n", "")
    paths["body"].write_text(body_text if missing_projectile_call else BODY_DISASM_TEXT, encoding="utf-8")
    return paths


class BattleEngineWeaponConstructionCandidateProbeTests(unittest.TestCase):
    def test_passes_for_construction_vtable_slot0_projectile_body_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))

            report = probe.build_report(
                index_path=paths["index"],
                create_weapon_path=paths["create_weapon"],
                ctor_path=paths["ctor"],
                vtable_path=paths["vtable"],
                slot0_body_path=paths["body"],
            )

            self.assertEqual(report["status"], "PASS")
            self.assertEqual(
                report["candidateClassification"],
                "construction-vtable-slot0-projectile-body-candidate",
            )
            self.assertEqual(report["vtable"]["slot0Ptr"], "0x00506930")
            self.assertIn("0x0050f7a0", report["slot0BodyCallTargets"])
            self.assertEqual(report["unexpectedStealthResetTokens"], [])

    def test_fails_when_projectile_creation_call_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), missing_projectile_call=True)

            report = probe.build_report(
                index_path=paths["index"],
                create_weapon_path=paths["create_weapon"],
                ctor_path=paths["ctor"],
                vtable_path=paths["vtable"],
                slot0_body_path=paths["body"],
            )

            self.assertEqual(report["status"], "FAIL")
            self.assertTrue(any("missing slot0 body call target" in item for item in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
