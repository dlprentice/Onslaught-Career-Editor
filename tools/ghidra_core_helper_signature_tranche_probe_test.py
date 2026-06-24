#!/usr/bin/env python3
"""Tests for the core-helper signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_core_helper_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


TARGETS = {
    "0x00402000": (
        "CUnitAI__SetStateTimestampCCToNow",
        "void __fastcall CUnitAI__SetStateTimestampCCToNow(void * this)",
        "Signature hardening for timestamp setter. Decompile evidence stores DAT_00672fd0 into this+0xcc. Not concrete CUnitAI layout or runtime proof.",
    ),
    "0x00402010": (
        "CUnit__ResetFieldD0ToGlobalThreshold",
        "void __fastcall CUnit__ResetFieldD0ToGlobalThreshold(void * this)",
        "Signature hardening for CUnit threshold reset. Decompile evidence stores DAT_00672fd0 into this+0xd0. Not concrete CUnit layout proof.",
    ),
    "0x00402020": (
        "CGeneralVolume__ResetCooldownTimestamp",
        "void __fastcall CGeneralVolume__ResetCooldownTimestamp(void * this)",
        "Signature hardening for GeneralVolume timestamp reset. Decompile evidence stores DAT_00672fd0 into this+0xd4. Not exact source identity proof.",
    ),
    "0x00402220": (
        "CAirGuide__ShutdownAndUnlink",
        "void __fastcall CAirGuide__ShutdownAndUnlink(void * this)",
        "Signature hardening for AirGuide unlink/shutdown helper. Decompile evidence removes this+0x2c from a CSPtrSet when linked, then calls CMonitor__Shutdown. Not exact class layout proof.",
    ),
    "0x004026b0": (
        "Vec3__Magnitude",
        "double __fastcall Vec3__Magnitude(void * this)",
        "Signature hardening for Vec3 magnitude. Decompile evidence computes sqrt(x*x+y*y+z*z) from this, this+4, and this+8. Not concrete FVector layout proof.",
    ),
    "0x00403690": (
        "CUnit__ReleaseAllAttachedParticleNodes",
        "bool __fastcall CUnit__ReleaseAllAttachedParticleNodes(void * this)",
        "Signature hardening for CUnit attached-particle cleanup. Decompile evidence returns 0/1 after child-unit and linked-particle release loops. Not runtime side-effect completeness proof.",
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

    signature_dry.write_text("--- SUMMARY ---\nupdated=0 skipped=6 missing=0 bad=0\n", encoding="utf-8")
    signature_apply.write_text("--- SUMMARY ---\nupdated=6 skipped=0 missing=0 bad=0\n", encoding="utf-8")
    comments_dry.write_text("--- SUMMARY ---\napplied=0 skipped=6 missing=0 bad=0\n", encoding="utf-8")
    comments_apply.write_text("--- SUMMARY ---\napplied=6 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    rows = []
    index_rows = []
    for address, (name, signature, comment) in TARGETS.items():
        if stale_signature and address == "0x00402000":
            signature = "void __fastcall CUnitAI__SetStateTimestampCCToNow(int param_1)"
        if overclaim and address == "0x00403690":
            comment = comment.replace("Not runtime side-effect completeness proof", "Runtime behavior proven")
        rows.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        index_rows.append(f"{address}\t{name}\t{signature}\tOK\n")
        (decompile / f"{address[2:]}_{name}.c").write_text(
            f"{name} {signature} DAT_00672fd0 + 0xcc + 0xd0 + 0xd4 + 8 + 4 CMonitor__Shutdown "
            "CSPtrSet__Remove SQRT CUnit__ReleaseChildUnits CParticleManager__RemoveFromGlobalList "
            "return true return false",
            encoding="utf-8",
        )

    metadata.write_text(METADATA_HEADER + "".join(rows), encoding="utf-8")
    (decompile / "index.tsv").write_text(INDEX_HEADER + "".join(index_rows), encoding="utf-8")
    xrefs.write_text(
        XREF_HEADER
        + "00402000\tCUnitAI__SetStateTimestampCCToNow\t00403733\t00403730\tCExplosionInitThing__UpdateAndTriggerDeferredStart\tUNCONDITIONAL_CALL\n"
        + "004026b0\tVec3__Magnitude\t00406d71\t00406d50\tVec3__NormalizeInPlace\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x00402000\t0x00402000\tTARGET\t0\t0x00402000\t0x00402000\tCUnitAI__SetStateTimestampCCToNow\tMOV\tEAX, [0x00672fd0]\ta1 d0 2f 67 00\tFALL_THROUGH\n"
        + "0x00402000\t0x00402000\tTARGET\t1\t0x00402005\t0x00402000\tCUnitAI__SetStateTimestampCCToNow\tMOV\tdword ptr [ECX + 0xcc], EAX\t89 81 cc 00 00 00\tFALL_THROUGH\n"
        + "0x00402010\t0x00402010\tTARGET\t0\t0x00402010\t0x00402010\tCUnit__ResetFieldD0ToGlobalThreshold\tMOV\tEAX, [0x00672fd0]\ta1 d0 2f 67 00\tFALL_THROUGH\n"
        + "0x00402010\t0x00402010\tTARGET\t1\t0x00402015\t0x00402010\tCUnit__ResetFieldD0ToGlobalThreshold\tMOV\tdword ptr [ECX + 0xd0], EAX\t89 81 d0 00 00 00\tFALL_THROUGH\n"
        + "0x00402020\t0x00402020\tTARGET\t0\t0x00402020\t0x00402020\tCGeneralVolume__ResetCooldownTimestamp\tMOV\tEAX, [0x00672fd0]\ta1 d0 2f 67 00\tFALL_THROUGH\n"
        + "0x00402020\t0x00402020\tTARGET\t1\t0x00402025\t0x00402020\tCGeneralVolume__ResetCooldownTimestamp\tMOV\tdword ptr [ECX + 0xd4], EAX\t89 81 d4 00 00 00\tFALL_THROUGH\n"
        + "0x00402220\t0x00402220\tTARGET\t0\t0x0040223d\t0x00402220\tCAirGuide__ShutdownAndUnlink\tMOV\tEAX, dword ptr [ESI + 0x2c]\t8b 46 2c\tFALL_THROUGH\n"
        + "0x00402220\t0x00402220\tAFTER\t1\t0x00402259\t0x00402220\tCAirGuide__ShutdownAndUnlink\tCALL\t0x004e5bd0\te8 00 00 00 00\tUNCONDITIONAL_CALL\n"
        + "0x00402220\t0x00402220\tAFTER\t2\t0x00402268\t0x00402220\tCAirGuide__ShutdownAndUnlink\tCALL\t0x004bac40\te8 00 00 00 00\tUNCONDITIONAL_CALL\n"
        + "0x004026b0\t0x004026b0\tTARGET\t0\t0x004026b3\t0x004026b0\tVec3__Magnitude\tFLD\tfloat ptr [ECX + 0x8]\td9 41 08\tFALL_THROUGH\n"
        + "0x004026b0\t0x004026b0\tAFTER\t1\t0x004026ca\t0x004026b0\tVec3__Magnitude\tCALL\tSQRT\te8 00 00 00 00\tUNCONDITIONAL_CALL\n"
        + "0x00403690\t0x00403690\tTARGET\t0\t0x00403691\t0x00403690\tCUnit__ReleaseAllAttachedParticleNodes\tCALL\tCUnit__MarkDestroyedAndCleanupLinks\te8 00 00 00 00\tUNCONDITIONAL_CALL\n"
        + "0x00403690\t0x00403690\tAFTER\t1\t0x004036a2\t0x00403690\tCUnit__ReleaseAllAttachedParticleNodes\tCALL\t0x004fcfe0\te8 00 00 00 00\tUNCONDITIONAL_CALL\n"
        + "0x00403690\t0x00403690\tAFTER\t2\t0x004036cf\t0x00403690\tCUnit__ReleaseAllAttachedParticleNodes\tCALL\t0x004cb050\te8 00 00 00 00\tUNCONDITIONAL_CALL\n"
        + "0x00403690\t0x00403690\tAFTER\t3\t0x00403720\t0x00403690\tCUnit__ReleaseAllAttachedParticleNodes\tMOV\tEAX, 0x1\tb8 01 00 00 00\tFALL_THROUGH\n",
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


class CoreHelperSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_hardened_core_helper_signatures(self) -> None:
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
        self.assertEqual(report["summary"]["signatureHardenedTargets"], 6)
        self.assertEqual(report["summary"]["xrefRows"], 2)

    def test_fails_for_stale_signature_or_public_overclaim(self) -> None:
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
        self.assertTrue(any("signature tokens missing" in failure for failure in report["failures"]))
        self.assertTrue(any("runtime/source overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
