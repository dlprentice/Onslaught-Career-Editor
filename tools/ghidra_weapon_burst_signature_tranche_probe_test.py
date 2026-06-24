#!/usr/bin/env python3
"""Tests for the weapon/burst signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_weapon_burst_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


TARGETS = {
    "0x00506930": (
        "CWeapon__HandleFireBurstEvent",
        "void __thiscall CWeapon__HandleFireBurstEvent(void * this, void * eventRecord)",
        "Signature hardening for weapon burst event handler. Instruction evidence reads event id 0x1389 from the event/context pointer, calls the current-preset projectile-burst body, and schedules a follow-up event. This is not exact source CWeapon::Fire or CBattleEngine::WeaponFired identity, and not runtime stealth proof.",
    ),
    "0x00505f70": (
        "CWeapon__scalar_deleting_dtor",
        "void * __thiscall CWeapon__scalar_deleting_dtor(void * this, byte flags)",
        "Signature hardening for CWeapon scalar deleting destructor. Instruction evidence calls CWeapon__DetachFromSetAndShutdownMonitor, tests flags bit 0, conditionally frees this, and returns this. Destructor evidence only; not weapon-fire or stealth behavior proof.",
    ),
    "0x005069f0": (
        "CEngine__SpawnProjectileBurstFromCurrentPreset",
        "int __fastcall CEngine__SpawnProjectileBurstFromCurrentPreset(void * param_1)",
        "Deferral note for the current-preset projectile-burst body. It is reached from the weapon burst event handler and CGeneralVolume fallback dispatcher, creates projectiles from the current preset, and still has provisional owner/name and param_N signature debt. Source weapon-fire and runtime stealth behavior remain unproven.",
    ),
    "0x00506010": (
        "CGeneralVolume__SpawnBurstFromPresetWithFallback",
        "int __fastcall CGeneralVolume__SpawnBurstFromPresetWithFallback(void * param_1)",
        "Deferral note for the shared preset fallback dispatcher. Direct callers include UnitAI, Sentinel, CEngine wrapper, and CGeneralVolume paths; it reaches the current-preset projectile-burst body and keeps provisional owner/name and param_N signature debt. Not source weapon-fire identity.",
    ),
}


def write_fixture(root: Path, *, stale_signature: bool = False, overclaim: bool = False) -> dict[str, Path]:
    signature_dry = root / "signature_dry.log"
    signature_apply = root / "signature_apply.log"
    comments_dry = root / "comments_dry.log"
    comments_apply = root / "comments_apply.log"
    metadata = root / "metadata_readback.tsv"
    decompile = root / "decompile_readback"
    xrefs = root / "xrefs.tsv"
    instructions = root / "instructions.tsv"
    decompile.mkdir()

    signature_dry.write_text("--- SUMMARY ---\nupdated=0 skipped=2 missing=0 bad=0\n", encoding="utf-8")
    signature_apply.write_text("--- SUMMARY ---\nupdated=2 skipped=0 missing=0 bad=0\n", encoding="utf-8")
    comments_dry.write_text("--- SUMMARY ---\napplied=0 skipped=4 missing=0 bad=0\n", encoding="utf-8")
    comments_apply.write_text("--- SUMMARY ---\napplied=4 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    rows = []
    index_rows = []
    for address, (name, signature, comment) in TARGETS.items():
        if stale_signature and address == "0x00506930":
            signature = "undefined CWeapon__HandleFireBurstEvent(void)"
        if overclaim and address == "0x00505f70":
            comment = comment.replace("Destructor evidence only", "Runtime behavior proven")
        rows.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        index_rows.append(f"{address}\t{name}\t{signature}\tOK\n")
        (decompile / f"{address[2:]}_{name}.c").write_text(
            f"{name} {signature} CEventManager__AddEvent_AtTime "
            "CEngine__SpawnProjectileBurstFromCurrentPreset CGeneralVolume__SpawnBurstFromPresetWithFallback "
            "CWeapon__DetachFromSetAndShutdownMonitor OID__FreeObject CWorldPhysicsManager__CreateProjectile",
            encoding="utf-8",
        )

    metadata.write_text(METADATA_HEADER + "".join(rows), encoding="utf-8")
    (decompile / "index.tsv").write_text(INDEX_HEADER + "".join(index_rows), encoding="utf-8")
    xrefs.write_text(
        XREF_HEADER
        + "00506930\tCWeapon__HandleFireBurstEvent\t005dfc94\t<none>\t<no_function>\tDATA\n"
        + "00505f70\tCWeapon__scalar_deleting_dtor\t005dfc98\t<none>\t<no_function>\tDATA\n"
        + "005069f0\tCEngine__SpawnProjectileBurstFromCurrentPreset\t005069b6\t00506930\tCWeapon__HandleFireBurstEvent\tUNCONDITIONAL_CALL\n"
        + "00506010\tCGeneralVolume__SpawnBurstFromPresetWithFallback\t004fc0b7\t004fc080\tCUnitAI__TrySpawnOrFinalizeAttachedUnit\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x00506930\t0x00506930\tTARGET\t0\t0x00506930\t0x00506930\tCWeapon__HandleFireBurstEvent\tMOV\tEAX, dword ptr [ESP + 0x4]\t8b 44 24 04\tFALL_THROUGH\n"
        + "0x00506930\t0x00506930\tAFTER\t1\t0x00506937\t0x00506930\tCWeapon__HandleFireBurstEvent\tCMP\tword ptr [EAX + 0x4], 0x1389\t66 81 78 04 89 13\tFALL_THROUGH\n"
        + "0x00506930\t0x00506930\tAFTER\t2\t0x005069b6\t0x00506930\tCWeapon__HandleFireBurstEvent\tCALL\t0x005069f0\te8 35 00 00 00\tUNCONDITIONAL_CALL\n"
        + "0x00506930\t0x00506930\tAFTER\t3\t0x005069ed\t0x00506930\tCWeapon__HandleFireBurstEvent\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x00505f70\t0x00505f70\tTARGET\t0\t0x00505f73\t0x00505f70\tCWeapon__scalar_deleting_dtor\tCALL\t0x00505f90\te8 18 00 00 00\tUNCONDITIONAL_CALL\n"
        + "0x00505f70\t0x00505f70\tAFTER\t1\t0x00505f78\t0x00505f70\tCWeapon__scalar_deleting_dtor\tTEST\tbyte ptr [ESP + 0x8], 0x1\tf6 44 24 08 01\tFALL_THROUGH\n"
        + "0x00505f70\t0x00505f70\tAFTER\t2\t0x00505f85\t0x00505f70\tCWeapon__scalar_deleting_dtor\tCALL\t0x00549220\te8 96 32 04 00\tUNCONDITIONAL_CALL\n"
        + "0x00505f70\t0x00505f70\tAFTER\t3\t0x00505f8d\t0x00505f70\tCWeapon__scalar_deleting_dtor\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x005069f0\t0x005069f0\tTARGET\t0\t0x00506a96\t0x005069f0\tCEngine__SpawnProjectileBurstFromCurrentPreset\tCALL\t0x004e1940\te8 a5 ae fd ff\tUNCONDITIONAL_CALL\n"
        + "0x00506010\t0x00506010\tTARGET\t0\t0x00506017\t0x00506010\tCGeneralVolume__SpawnBurstFromPresetWithFallback\tMOV\tEAX, 0x51eb851f\tb8 1f 85 eb 51\tFALL_THROUGH\n"
        + "0x00506010\t0x00506010\tAFTER\t1\t0x00506052\t0x00506010\tCGeneralVolume__SpawnBurstFromPresetWithFallback\tCALL\t0x00406d20\te8 c9 0c f0 ff\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    return {
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


class WeaponBurstSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_hardened_signatures_and_provisional_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
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
        self.assertEqual(report["summary"]["signatureHardenedTargets"], 2)
        self.assertEqual(report["summary"]["provisionalTargets"], 2)

    def test_fails_for_stale_hardened_signature_or_public_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale_signature=True, overclaim=True)
            report = probe.build_report(
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
        self.assertTrue(any("stale undefined signature" in failure for failure in report["failures"]))
        self.assertTrue(any("runtime/source overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
