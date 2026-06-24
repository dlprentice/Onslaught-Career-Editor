#!/usr/bin/env python3
"""Tests for the weapon/burst provisional-name review probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_weapon_burst_provisional_review_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def write_fixture(
    root: Path,
    *,
    stale_name: bool = False,
    stale_signature: bool = False,
    overclaim: bool = False,
) -> dict[str, Path]:
    signature_dry = root / "signature_dry.log"
    signature_apply = root / "signature_apply.log"
    metadata = root / "metadata_readback.tsv"
    decompile = root / "decompile_readback"
    xrefs = root / "xrefs_readback.tsv"
    instructions = root / "instructions_readback.tsv"
    caller_metadata = root / "caller_metadata.tsv"
    raw_xrefs = root / "raw_xref_instructions.tsv"
    decompile.mkdir()

    signature_dry.write_text("--- SUMMARY ---\nupdated=0 skipped=2 missing=0 bad=0\n", encoding="utf-8")
    signature_apply.write_text("--- SUMMARY ---\nupdated=2 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    current_name = "ProjectileBurst__SpawnFromCurrentPreset"
    fallback_name = "ProjectileBurst__SpawnFromPercentBucketFallback"
    if stale_name:
        current_name = "CEngine__SpawnProjectileBurstFromCurrentPreset"
    current_sig = f"int __fastcall {current_name}(void * burstContext)"
    fallback_sig = f"int __fastcall {fallback_name}(void * burstContext)"
    if stale_signature:
        fallback_sig = f"int __fastcall {fallback_name}(void * param_1)"

    current_comment = (
        "Owner-neutral correction for the current-preset projectile-burst body. It creates "
        "projectile/effect objects from burstContext +0xa0 and is reached from the weapon "
        "event handler plus the percent-bucket fallback helper. Static Ghidra evidence only; "
        "exact CWeapon::Fire, CBattleEngine::WeaponFired, runtime stealth behavior, and raw "
        "caller boundaries remain unproven."
    )
    fallback_comment = (
        "Owner-neutral correction for the shared percent-bucket fallback dispatcher. It selects "
        "a preset from burstContext +0xa4 bucket data, updates cooldown/progress fields, calls "
        "ProjectileBurst__SpawnFromCurrentPreset, and may reschedule event 0x1389. Static Ghidra "
        "evidence only; exact source identity, runtime stealth behavior, and raw caller boundaries "
        "remain unproven."
    )
    if overclaim:
        fallback_comment = fallback_comment.replace("runtime stealth behavior", "runtime stealth behavior proven")

    metadata.write_text(
        METADATA_HEADER
        + f"0x005069f0\t{current_name}\t{current_sig}\t{current_comment}\tOK\n"
        + f"0x00506010\t{fallback_name}\t{fallback_sig}\t{fallback_comment}\tOK\n",
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        INDEX_HEADER
        + f"0x005069f0\t{current_name}\t{current_sig}\tOK\n"
        + f"0x00506010\t{fallback_name}\t{fallback_sig}\tOK\n",
        encoding="utf-8",
    )
    (decompile / f"005069f0_{current_name}.c").write_text(
        "ProjectileBurst__SpawnFromCurrentPreset "
        "CWorldPhysicsManager__CreateProjectile "
        "CEngine__SetProjectileTargetReader "
        "CBattleEngine__RandomizeBurstOffsetsAndAccumulateRange",
        encoding="utf-8",
    )
    (decompile / f"00506010_{fallback_name}.c").write_text(
        "ProjectileBurst__SpawnFromPercentBucketFallback "
        "ProjectileBurst__SpawnFromCurrentPreset "
        "CEventManager__AddEvent_AtTime 0x1389 "
        "+ 0xa4 + 0x60 + 0x68 + 0xa0",
        encoding="utf-8",
    )
    xrefs.write_text(
        XREF_HEADER
        + "005069f0\tProjectileBurst__SpawnFromCurrentPreset\t00506143\t00506010\tProjectileBurst__SpawnFromPercentBucketFallback\tUNCONDITIONAL_CALL\n"
        + "005069f0\tProjectileBurst__SpawnFromCurrentPreset\t005069b6\t00506930\tCWeapon__HandleFireBurstEvent\tUNCONDITIONAL_CALL\n"
        + "00506010\tProjectileBurst__SpawnFromPercentBucketFallback\t004fc0b7\t004fc080\tCUnitAI__TrySpawnOrFinalizeAttachedUnit\tUNCONDITIONAL_CALL\n"
        + "00506010\tProjectileBurst__SpawnFromPercentBucketFallback\t004ded11\t004decc0\tCSentinel__UpdateFlamethrowers\tUNCONDITIONAL_CALL\n"
        + "00506010\tProjectileBurst__SpawnFromPercentBucketFallback\t00411e0f\t00411bf0\tCGeneralVolume__DispatchMode3BurstProgressAndSpawn\tUNCONDITIONAL_CALL\n"
        + "00506010\tProjectileBurst__SpawnFromPercentBucketFallback\t00413d5f\t00413cf0\tCGeneralVolume__UpdateCurrentEntryProgressAndRefresh\tUNCONDITIONAL_CALL\n"
        + "00506010\tProjectileBurst__SpawnFromPercentBucketFallback\t00411be4\t00411b90\tCGeneralVolume__DispatchSelectedBurstPreset\tUNCONDITIONAL_CALL\n"
        + "00506010\tProjectileBurst__SpawnFromPercentBucketFallback\t0044e093\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n"
        + "00506010\tProjectileBurst__SpawnFromPercentBucketFallback\t004f4bd6\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x005069f0\t0x005069f0\tAFTER\t1\t0x00506a96\t0x005069f0\tProjectileBurst__SpawnFromCurrentPreset\tCALL\t0x004e1940\te8\tUNCONDITIONAL_CALL\n"
        + "0x005069f0\t0x005069f0\tAFTER\t2\t0x00506ccc\t0x005069f0\tProjectileBurst__SpawnFromCurrentPreset\tCALL\t0x004062d0\te8\tUNCONDITIONAL_CALL\n"
        + "0x005069f0\t0x005069f0\tAFTER\t3\t0x0050787f\t0x005069f0\tProjectileBurst__SpawnFromCurrentPreset\tRET\t\tc3\tTERMINATOR\n"
        + "0x00506010\t0x00506010\tTARGET\t0\t0x00506010\t0x00506010\tProjectileBurst__SpawnFromPercentBucketFallback\tSUB\tESP, 0x8\t83 ec 08\tFALL_THROUGH\n"
        + "0x00506010\t0x00506010\tAFTER\t1\t0x00506143\t0x00506010\tProjectileBurst__SpawnFromPercentBucketFallback\tCALL\t0x005069f0\te8\tUNCONDITIONAL_CALL\n"
        + "0x00506010\t0x00506010\tAFTER\t2\t0x005061e8\t0x00506010\tProjectileBurst__SpawnFromPercentBucketFallback\tRET\t\tc3\tTERMINATOR\n",
        encoding="utf-8",
    )
    caller_metadata.write_text(
        METADATA_HEADER
        + "0x004fc080\tCUnitAI__TrySpawnOrFinalizeAttachedUnit\tint __fastcall CUnitAI__TrySpawnOrFinalizeAttachedUnit(void * param_1)\t\tOK\n"
        + "0x004decc0\tCSentinel__UpdateFlamethrowers\tundefined CSentinel__UpdateFlamethrowers(void)\t\tOK\n"
        + "0x00411bf0\tCGeneralVolume__DispatchMode3BurstProgressAndSpawn\tvoid __fastcall CGeneralVolume__DispatchMode3BurstProgressAndSpawn(void * param_1)\t\tOK\n"
        + "0x00413cf0\tCGeneralVolume__UpdateCurrentEntryProgressAndRefresh\tvoid __fastcall CGeneralVolume__UpdateCurrentEntryProgressAndRefresh(int param_1)\t\tOK\n"
        + "0x00411b90\tCGeneralVolume__DispatchSelectedBurstPreset\tvoid __fastcall CGeneralVolume__DispatchSelectedBurstPreset(void * param_1)\t\tOK\n"
        + "0x0044e093\t<none>\t<none>\t\tMISSING\n"
        + "0x004f4bd6\t<none>\t<none>\t\tMISSING\n",
        encoding="utf-8",
    )
    raw_xrefs.write_text(
        INSTRUCTION_HEADER
        + "0x0044e093\t0x0044e093\tTARGET\t0\t0x0044e093\t<none>\t<no_function>\tCALL\t0x00506010\te8\tUNCONDITIONAL_CALL\n"
        + "0x004f4bd6\t0x004f4bd6\tTARGET\t0\t0x004f4bd6\t<none>\t<no_function>\tCALL\t0x00506010\te8\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    return {
        "signature_dry": signature_dry,
        "signature_apply": signature_apply,
        "metadata": metadata,
        "decompile_index": decompile / "index.tsv",
        "decompile_dir": decompile,
        "xrefs": xrefs,
        "instructions": instructions,
        "caller_metadata": caller_metadata,
        "raw_xrefs": raw_xrefs,
    }


class WeaponBurstProvisionalReviewProbeTests(unittest.TestCase):
    def test_passes_for_owner_neutral_names_and_bounded_claims(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                signature_dry_log_path=paths["signature_dry"],
                signature_apply_log_path=paths["signature_apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
                caller_metadata_path=paths["caller_metadata"],
                raw_xref_instructions_path=paths["raw_xrefs"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], 2)
        self.assertEqual(report["summary"]["renamedTargets"], 2)
        self.assertEqual(report["summary"]["hardenedSignatures"], 2)
        self.assertEqual(report["summary"]["rawCallsitesWithoutFunctions"], 2)

    def test_fails_for_stale_owner_signature_or_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale_name=True, stale_signature=True, overclaim=True)
            report = probe.build_report(
                signature_dry_log_path=paths["signature_dry"],
                signature_apply_log_path=paths["signature_apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
                caller_metadata_path=paths["caller_metadata"],
                raw_xref_instructions_path=paths["raw_xrefs"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("metadata name/status mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("signature tokens missing" in failure for failure in report["failures"]))
        self.assertTrue(any("runtime/source overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
