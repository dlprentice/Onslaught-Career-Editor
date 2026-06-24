#!/usr/bin/env python3
"""Tests for the BattleEngine weapon slot-0 function recovery probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import battleengine_weapon_slot0_function_recovery_probe as probe


CREATE_HEADER = "address\tstatus\tname\tsignature\tnote\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
FUNCTIONS_HEADER = "address\tname\tsignature\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\t"
    "function_name\tmnemonic\toperands\tbytes\tflow_type\n"
)


def write_fixture(root: Path, *, omit_apply: bool = False) -> dict[str, Path]:
    dry = root / "create_dry.tsv"
    apply = root / "create_apply.tsv"
    decompile = root / "index.tsv"
    functions = root / "functions_all_after.tsv"
    xrefs = root / "xrefs_after.tsv"
    instructions = root / "instructions_after.tsv"

    dry.write_text(
        CREATE_HEADER
        + "00506930\twould_create\t\t\t"
        "dry-run would disassemble+create and name CWeapon__VFunc_00_00506930\n",
        encoding="utf-8",
    )
    if not omit_apply:
        apply.write_text(
            CREATE_HEADER
            + "00506930\tcreated\tCWeapon__VFunc_00_00506930\t"
            "undefined CWeapon__VFunc_00_00506930(void)\t"
            "disassemble+create succeeded; renamed\n",
            encoding="utf-8",
        )
    decompile.write_text(
        INDEX_HEADER
        + "0x00506930\tCWeapon__VFunc_00_00506930\t"
        "undefined CWeapon__VFunc_00_00506930(void)\tOK\n"
        + "0x005069f0\tCEngine__SpawnProjectileBurstFromCurrentPreset\t"
        "undefined CEngine__SpawnProjectileBurstFromCurrentPreset(void)\tOK\n"
        + "0x005078b0\tCEngine__GetListEntryIdByIndex\t"
        "int CEngine__GetListEntryIdByIndex(void * this, int param_1)\tOK\n",
        encoding="utf-8",
    )
    functions.write_text(
        FUNCTIONS_HEADER
        + "0x00506930\tCWeapon__VFunc_00_00506930\tundefined CWeapon__VFunc_00_00506930(void)\n"
        + "0x005069f0\tCEngine__SpawnProjectileBurstFromCurrentPreset\t"
        "undefined CEngine__SpawnProjectileBurstFromCurrentPreset(void)\n",
        encoding="utf-8",
    )
    xrefs.write_text(
        XREF_HEADER
        + "00506930\tCWeapon__VFunc_00_00506930\t005dfc94\t<none>\t<no_function>\tDATA\n"
        + "005069f0\tCEngine__SpawnProjectileBurstFromCurrentPreset\t005069b6\t00506930\t"
        "CWeapon__VFunc_00_00506930\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x00506930\t0x00506930\tTARGET\t0\t0x00506930\t0x00506930\t"
        "CWeapon__VFunc_00_00506930\tMOV\tEAX, dword ptr [ESP + 0x4]\t8b 44 24 04\tFALL_THROUGH\n"
        + "0x00506930\t0x00506930\tAFTER\t1\t0x00506934\t0x00506930\t"
        "CWeapon__VFunc_00_00506930\tPUSH\tEBX\t53\tFALL_THROUGH\n"
        + "0x005069f0\t0x005069f0\tTARGET\t0\t0x005069f0\t0x005069f0\t"
        "CEngine__SpawnProjectileBurstFromCurrentPreset\tMOV\tEAX, FS:[0x0]\t64 a1 00 00 00 00\tFALL_THROUGH\n",
        encoding="utf-8",
    )
    return {
        "dry": dry,
        "apply": apply,
        "decompile": decompile,
        "functions": functions,
        "xrefs": xrefs,
        "instructions": instructions,
    }


class BattleEngineWeaponSlot0FunctionRecoveryProbeTests(unittest.TestCase):
    def test_passes_for_dry_apply_and_readback_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))

            report = probe.build_report(
                dry_path=paths["dry"],
                apply_path=paths["apply"],
                decompile_index_path=paths["decompile"],
                functions_all_path=paths["functions"],
                xrefs_after_path=paths["xrefs"],
                instructions_after_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["candidateClassification"], "slot0-function-boundary-recovered")
        self.assertEqual(report["functionName"], "CWeapon__VFunc_00_00506930")
        self.assertEqual(report["createDryStatus"], "would_create")
        self.assertEqual(report["createApplyStatus"], "created")
        self.assertTrue(report["readback"]["decompileOk"])
        self.assertTrue(report["readback"]["presentInAllFunctions"])
        self.assertTrue(report["readback"]["innerCallOwnedByRecoveredFunction"])
        self.assertEqual(report["legacyWeakNameCount"], 0)

    def test_fails_when_apply_readback_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), omit_apply=True)

            report = probe.build_report(
                dry_path=paths["dry"],
                apply_path=paths["apply"],
                decompile_index_path=paths["decompile"],
                functions_all_path=paths["functions"],
                xrefs_after_path=paths["xrefs"],
                instructions_after_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("missing apply result" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
