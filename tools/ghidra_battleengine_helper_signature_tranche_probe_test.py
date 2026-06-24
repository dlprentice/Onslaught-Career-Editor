#!/usr/bin/env python3
"""Tests for the BattleEngine helper signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_battleengine_helper_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"


TARGET_ROWS = {
    "0x00405a40": {
        "name": "CBattleEngine__dtor_base",
        "signature": "void __fastcall CBattleEngine__dtor_base(void * this)",
        "comment": "BattleEngine destructor-base cleanup evidence. Frees owned cockpit/reader/projectile sets including tracked projectile set +0x294 before calling the CUnit base destructor. Not exact source identity, concrete layout, runtime behavior proof, or weapon-fired stealth reset proof.",
        "decompile": "CBattleEngine__dtor_base CSPtrSet__Clear CUnit__scalar_deleting_dtor_004f84e0 0x294",
    },
    "0x00405f60": {
        "name": "CBattleEngine__scalar_deleting_dtor",
        "signature": "void * __thiscall CBattleEngine__scalar_deleting_dtor(void * this, byte flags)",
        "comment": "BattleEngine scalar-deleting destructor wrapper evidence. Calls CBattleEngine__dtor_base, checks delete flag bit 0, optionally frees this, and returns this. Not exact source identity, concrete layout, runtime behavior proof, or weapon-fired stealth reset proof.",
        "decompile": "CBattleEngine__scalar_deleting_dtor CBattleEngine__dtor_base OID__FreeObject return this",
    },
    "0x00405f80": {
        "name": "CBattleEngine__VFunc_02_00405f80",
        "signature": "void __fastcall CBattleEngine__VFunc_02_00405f80(void * this)",
        "comment": "BattleEngine finalization-vfunc evidence. Clears the +0x250 linked set, dispatches vibration through the controller when present, finalizes linked unit state at +0x5f8, then calls the CUnit vfunc-02 path. Not exact source identity, concrete layout, runtime behavior proof, or weapon-fired stealth reset proof.",
        "decompile": "CBattleEngine__VFunc_02_00405f80 CGame__DispatchVibrationWithCareerGate CUnit__FinalizeLinkedUnitStateAndClear VFuncSlot_02_004f95d0",
    },
    "0x004063a0": {
        "name": "CBattleEngine__GetFloatAt0x118_AsDouble",
        "signature": "double __fastcall CBattleEngine__GetFloatAt0x118_AsDouble(void * this)",
        "comment": "BattleEngine field +0x118 float accessor evidence. Returns the +0x118 float widened to double. Field semantics, concrete layout, runtime behavior proof, and weapon-fired stealth reset proof remain unproven.",
        "decompile": "CBattleEngine__GetFloatAt0x118_AsDouble 0x118",
    },
    "0x004063b0": {
        "name": "CBattleEngine__UpdateWeaponEffect",
        "signature": "void __fastcall CBattleEngine__UpdateWeaponEffect(void * this)",
        "comment": "BattleEngine weapon/effect object helper evidence. Allocates a 0x20 object from BattleEngine.cpp line 0x1f5, fills squared range/timing-style fields, and hands it to a nested manager vcall. Not exact source identity, concrete layout, runtime behavior proof, or weapon-fired stealth reset proof.",
        "decompile": "CBattleEngine__UpdateWeaponEffect OID__AllocObject 0x1f5 PTR_VFuncSlot_00_00426340_005d88cc",
    },
    "0x00406460": {
        "name": "CBattleEngine__SwapPrimarySecondaryPartReadersForState",
        "signature": "void __fastcall CBattleEngine__SwapPrimarySecondaryPartReadersForState(void * this)",
        "comment": "BattleEngine primary/secondary reader swap evidence. Branches on state +0x260 and gate +0x5f0, swaps +0x5ec with +0x30, parks/restores +0x70 through +0x5f4, and refreshes mech/influence-map state. Not exact source identity, concrete layout, runtime behavior proof, or weapon-fired stealth reset proof.",
        "decompile": "CBattleEngine__SwapPrimarySecondaryPartReadersForState CMCMech__Reset CInfluenceMap__SetTrackedThingAndClearCachedObject 0x5ec",
    },
    "0x00406560": {
        "name": "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
        "signature": "void __fastcall CBattleEngine__UpdateAutoTargetSetAndFireProjectiles(void * this)",
        "comment": "BattleEngine tracked-target projectile helper evidence. Maintains tracked-target set +0x294, filters candidate targets, resolves profile/range context, and calls CBattleEngine__AddProjectile. This does not prove exact CBattleEngine::WeaponFired identity or weapon-fired stealth reset behavior.",
        "decompile": "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles CBattleEngine__AddProjectile CBattleEngine__IsWeaponModeCompatibleWithMountState CSPtrSet__First",
    },
    "0x00406fc0": {
        "name": "CBattleEngine__AddProjectile",
        "signature": "void __thiscall CBattleEngine__AddProjectile(void * this, void * target, float lifetime, int modeFlag)",
        "comment": "BattleEngine tracked projectile insertion evidence. Skips flagged targets, checks tracked projectile set +0x294 for a duplicate target, allocates a 0x14 active-reader entry from BattleEngine.cpp line 0x332, stores expiry/modeFlag, and appends it. Not exact source identity, concrete layout, runtime behavior proof, or weapon-fired stealth reset proof.",
        "decompile": "CBattleEngine__AddProjectile CGenericActiveReader__SetReader OID__AllocObject 0x332 CSPtrSet__AddToTail",
    },
}


def write_fixture(root: Path, *, stale_signature: bool = False, overclaim: bool = False) -> dict[str, Path]:
    rename_dry = root / "rename_dry.log"
    rename_apply = root / "rename_apply.log"
    signature_dry = root / "signature_dry.log"
    signature_apply = root / "signature_apply.log"
    comments_dry = root / "comments_dry.log"
    comments_apply = root / "comments_apply.log"
    metadata = root / "metadata_readback.tsv"
    decompile = root / "decompile_readback"
    xrefs = root / "xrefs_readback.tsv"
    instructions = root / "instructions_readback.tsv"
    decompile.mkdir()

    rename_dry.write_text(
        "Mode: args (dry)\n"
        "DRY: 0x00405a40 CBattleEngine__scalar_deleting_dtor_00405a40 -> CBattleEngine__dtor_base\n"
        "DRY: 0x00405f60 CBattleEngine__VFunc_01_00405f60 -> CBattleEngine__scalar_deleting_dtor\n"
        "--- SUMMARY ---\napplied=0 skipped=2 missing=0 bad=0\n",
        encoding="utf-8",
    )
    rename_apply.write_text(
        "Mode: args (apply)\n"
        "OK: 0x00405a40 CBattleEngine__scalar_deleting_dtor_00405a40 -> CBattleEngine__dtor_base\n"
        "OK: 0x00405f60 CBattleEngine__VFunc_01_00405f60 -> CBattleEngine__scalar_deleting_dtor\n"
        "--- SUMMARY ---\napplied=2 skipped=0 missing=0 bad=0\n",
        encoding="utf-8",
    )
    signature_dry.write_text(
        "Mode: dry\n"
        + "".join(f"DRY: {addr} {row['name']} -> {row['signature']}\n" for addr, row in TARGET_ROWS.items())
        + "--- SUMMARY ---\nupdated=0 skipped=8 missing=0 bad=0\n",
        encoding="utf-8",
    )
    signature_apply.write_text(
        "Mode: apply\n"
        + "".join(f"OK: {addr} {row['name']} -> {row['signature']}\n" for addr, row in TARGET_ROWS.items())
        + "--- SUMMARY ---\nupdated=8 skipped=0 missing=0 bad=0\n",
        encoding="utf-8",
    )
    comments_dry.write_text("--- SUMMARY ---\napplied=0 skipped=8 missing=0 bad=0\n", encoding="utf-8")
    comments_apply.write_text("--- SUMMARY ---\napplied=8 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    rows = {addr: dict(row) for addr, row in TARGET_ROWS.items()}
    if stale_signature:
        rows["0x004063b0"]["signature"] = "undefined CBattleEngine__UpdateWeaponEffect(void)"
    if overclaim:
        rows["0x00406560"]["comment"] = rows["0x00406560"]["comment"].replace(
            "This does not prove exact", "This proves exact"
        )

    metadata.write_text(
        METADATA_HEADER
        + "".join(
            f"{addr}\t{row['name']}\t{row['signature']}\t{row['comment']}\tOK\n"
            for addr, row in rows.items()
        ),
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        INDEX_HEADER
        + "".join(f"{addr}\t{row['name']}\t{row['signature']}\tOK\n" for addr, row in rows.items()),
        encoding="utf-8",
    )
    for addr, row in rows.items():
        (decompile / f"{addr[2:]}_{row['name']}.c").write_text(
            f"{row['signature']} {row['decompile']} {row['name']}",
            encoding="utf-8",
        )
    xrefs.write_text(
        XREF_HEADER
        + "".join(f"{addr[2:]}\t{row['name']}\t00401000\t00401000\tCaller\tUNCONDITIONAL_CALL\n" for addr, row in rows.items())
        + "00406fc0\tCBattleEngine__AddProjectile\t004068d9\t00406560\tCBattleEngine__UpdateAutoTargetSetAndFireProjectiles\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    instructions.write_text(
        "target_addr\tfunction_addr\tposition\tindex\taddress\tinstruction_function_addr\tinstruction_function\tmnemonic\toperands\tbytes\tflow_type\n"
        + "".join(
            f"{addr}\t{addr}\tAFTER\t1\t{addr}\t{addr}\t{row['name']}\tCALL\t0x00549220\t\tUNCONDITIONAL_CALL\n"
            for addr, row in rows.items()
        )
        + "0x00406460\t0x00406460\tAFTER\t2\t0x004064d0\t0x00406460\tCBattleEngine__SwapPrimarySecondaryPartReadersForState\tMOV\t[EAX + 0x5ec]\t\tFALL_THROUGH\n"
        + "0x00406560\t0x00406560\tAFTER\t2\t0x004068d9\t0x00406560\tCBattleEngine__UpdateAutoTargetSetAndFireProjectiles\tCALL\t0x00406fc0\t\tUNCONDITIONAL_CALL\n"
        + "0x00406fc0\t0x00406fc0\tAFTER\t2\t0x0040704f\t0x00406fc0\tCBattleEngine__AddProjectile\tCALL\t0x004021a0\t\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    return {
        "rename_dry": rename_dry,
        "rename_apply": rename_apply,
        "signature_dry": signature_dry,
        "signature_apply": signature_apply,
        "comments_dry": comments_dry,
        "comments_apply": comments_apply,
        "metadata": metadata,
        "decompile_index": decompile / "index.tsv",
        "decompile_dir": decompile,
        "xrefs": xrefs,
        "instructions": instructions,
    }


class BattleEngineHelperSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_hardened_battleengine_helper_tranche(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                rename_dry_log_path=paths["rename_dry"],
                rename_apply_log_path=paths["rename_apply"],
                signature_dry_log_path=paths["signature_dry"],
                signature_apply_log_path=paths["signature_apply"],
                comments_dry_log_path=paths["comments_dry"],
                comments_apply_log_path=paths["comments_apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["renamedTargets"], 2)
        self.assertEqual(report["summary"]["signatureHardenedTargets"], 8)
        self.assertEqual(report["summary"]["weaponFiredStealthStatus"], "unresolved")

    def test_fails_for_stale_signature_or_weapon_fire_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale_signature=True, overclaim=True)
            report = probe.build_report(
                rename_dry_log_path=paths["rename_dry"],
                rename_apply_log_path=paths["rename_apply"],
                signature_dry_log_path=paths["signature_dry"],
                signature_apply_log_path=paths["signature_apply"],
                comments_dry_log_path=paths["comments_dry"],
                comments_apply_log_path=paths["comments_apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("signature tokens missing" in failure for failure in report["failures"]))
        self.assertTrue(any("overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
