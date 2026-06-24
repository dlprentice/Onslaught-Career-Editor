#!/usr/bin/env python3
"""Tests for the vector/math signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_vector_math_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


TARGETS = {
    "0x00401b50": (
        "CMCMine__ComputeClampedScaleFactor",
        "double __fastcall CMCMine__ComputeClampedScaleFactor(void * this)",
        "Signature hardening for mine scale helper. Instruction/decompile evidence uses ECX as object pointer, calls vfunc +0x60, reads +0xd8, and clamps the FPU result. Not exact class layout, source identity, or runtime proof.",
    ),
    "0x00401ec0": (
        "Vec3__SetXYZ",
        "void __thiscall Vec3__SetXYZ(void * this, float x, float y, float z)",
        "Signature hardening for Vec3 setter. Instruction evidence writes three stack float/dword values into ECX vector slots and returns with ret 0xc. Not concrete FVector structure proof.",
    ),
    "0x00401ee0": (
        "Vec3__Add",
        "void __thiscall Vec3__Add(void * this, void * outVec, void * rhs)",
        "Signature hardening for Vec3 add. Instruction evidence reads ECX as lhs, stack arg1 as output vector, stack arg2 as rhs, and returns with ret 0x8. Not exact source identity proof.",
    ),
    "0x00401f10": (
        "Mat34__SetRows",
        "void __thiscall Mat34__SetRows(void * this, void * row0, void * row1, void * row2)",
        "Signature hardening for Mat34 row setter. Instruction evidence copies three four-dword row arguments into ECX matrix slots and returns with ret 0xc. Not concrete matrix layout proof.",
    ),
    "0x00401fa0": (
        "HeightDelta__Below025_D0",
        "bool __fastcall HeightDelta__Below025_D0(void * this)",
        "Signature hardening for height-delta predicate. Instruction evidence reads ECX+0xd0, compares against threshold constant, and returns 1 or 0. Not exact owner/source/runtime proof.",
    ),
    "0x00401fd0": (
        "HeightDelta__Below015_D4",
        "bool __fastcall HeightDelta__Below015_D4(void * this)",
        "Signature hardening for height-delta predicate. Instruction evidence reads ECX+0xd4, compares against threshold constant, and returns 1 or 0. Not exact owner/source/runtime proof.",
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
        if stale_signature and address == "0x00401ec0":
            signature = "int Vec3__SetXYZ(void)"
        if overclaim and address == "0x00401fa0":
            comment = comment.replace("Not exact owner/source/runtime proof", "Runtime behavior proven")
        rows.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        index_rows.append(f"{address}\t{name}\t{signature}\tOK\n")
        (decompile / f"{address[2:]}_{name}.c").write_text(
            f"{name} {signature} vfunc +0x60 +0xd8 ret 0xc ret 0x8 ECX+0xd0 ECX+0xd4",
            encoding="utf-8",
        )

    metadata.write_text(METADATA_HEADER + "".join(rows), encoding="utf-8")
    (decompile / "index.tsv").write_text(INDEX_HEADER + "".join(index_rows), encoding="utf-8")
    xrefs.write_text(
        XREF_HEADER
        + "00401ec0\tVec3__SetXYZ\t004a6fff\t004a5b70\tCMesh__Load\tUNCONDITIONAL_CALL\n"
        + "00401ee0\tVec3__Add\t004cdbad\t004cd890\tCUnit__ProjectMotion\tUNCONDITIONAL_CALL\n"
        + "00401f10\tMat34__SetRows\t0041ad8d\t0041ad30\tCInterpolatedCamera__ctor\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x00401b50\t0x00401b50\tTARGET\t0\t0x00401b52\t0x00401b50\tCMCMine__ComputeClampedScaleFactor\tMOV\tESI, ECX\t8b f1\tFALL_THROUGH\n"
        + "0x00401b50\t0x00401b50\tAFTER\t1\t0x00401b56\t0x00401b50\tCMCMine__ComputeClampedScaleFactor\tCALL\tdword ptr [EAX + 0x60]\tff 50 60\tCOMPUTED_CALL\n"
        + "0x00401b50\t0x00401b50\tAFTER\t2\t0x00401b6c\t0x00401b50\tCMCMine__ComputeClampedScaleFactor\tFSUB\tfloat ptr [ESI + 0xd8]\td8 a6 d8 00 00 00\tFALL_THROUGH\n"
        + "0x00401ec0\t0x00401ec0\tTARGET\t0\t0x00401ec0\t0x00401ec0\tVec3__SetXYZ\tMOV\tEDX, dword ptr [ESP + 0x8]\t8b 54 24 08\tFALL_THROUGH\n"
        + "0x00401ec0\t0x00401ec0\tAFTER\t1\t0x00401ec6\t0x00401ec0\tVec3__SetXYZ\tMOV\tECX, dword ptr [ESP + 0x4]\t8b 4c 24 04\tFALL_THROUGH\n"
        + "0x00401ec0\t0x00401ec0\tAFTER\t1\t0x00401eca\t0x00401ec0\tVec3__SetXYZ\tMOV\tdword ptr [EAX], ECX\t89 08\tFALL_THROUGH\n"
        + "0x00401ec0\t0x00401ec0\tAFTER\t1\t0x00401ecc\t0x00401ec0\tVec3__SetXYZ\tMOV\tECX, dword ptr [ESP + 0xc]\t8b 4c 24 0c\tFALL_THROUGH\n"
        + "0x00401ec0\t0x00401ec0\tAFTER\t2\t0x00401ed6\t0x00401ec0\tVec3__SetXYZ\tRET\t0xc\tc2 0c 00\tTERMINATOR\n"
        + "0x00401ee0\t0x00401ee0\tTARGET\t0\t0x00401ee0\t0x00401ee0\tVec3__Add\tMOV\tEAX, dword ptr [ESP + 0x8]\t8b 44 24 08\tFALL_THROUGH\n"
        + "0x00401ee0\t0x00401ee0\tAFTER\t1\t0x00401ef4\t0x00401ee0\tVec3__Add\tMOV\tEAX, dword ptr [ESP + 0x4]\t8b 44 24 04\tFALL_THROUGH\n"
        + "0x00401ee0\t0x00401ee0\tAFTER\t2\t0x00401f00\t0x00401ee0\tVec3__Add\tRET\t0x8\tc2 08 00\tTERMINATOR\n"
        + "0x00401f10\t0x00401f10\tTARGET\t0\t0x00401f13\t0x00401f10\tMat34__SetRows\tMOV\tECX, dword ptr [ESP + 0x8]\t8b 4c 24 08\tFALL_THROUGH\n"
        + "0x00401f10\t0x00401f10\tAFTER\t1\t0x00401f2f\t0x00401f10\tMat34__SetRows\tMOV\tECX, dword ptr [ESP + 0xc]\t8b 4c 24 0c\tFALL_THROUGH\n"
        + "0x00401f10\t0x00401f10\tAFTER\t1\t0x00401f4c\t0x00401f10\tMat34__SetRows\tMOV\tECX, dword ptr [ESP + 0x10]\t8b 4c 24 10\tFALL_THROUGH\n"
        + "0x00401f10\t0x00401f10\tAFTER\t1\t0x00401f6a\t0x00401f10\tMat34__SetRows\tRET\t0xc\tc2 0c 00\tTERMINATOR\n"
        + "0x00401fa0\t0x00401fa0\tTARGET\t0\t0x00401fa6\t0x00401fa0\tHeightDelta__Below025_D0\tFSUB\tfloat ptr [ECX + 0xd0]\td8 a1 d0 00 00 00\tFALL_THROUGH\n"
        + "0x00401fa0\t0x00401fa0\tAFTER\t1\t0x00401fb9\t0x00401fa0\tHeightDelta__Below025_D0\tMOV\tEAX, 0x1\tb8 01 00 00 00\tFALL_THROUGH\n"
        + "0x00401fd0\t0x00401fd0\tTARGET\t0\t0x00401fd6\t0x00401fd0\tHeightDelta__Below015_D4\tFSUB\tfloat ptr [ECX + 0xd4]\td8 a1 d4 00 00 00\tFALL_THROUGH\n"
        + "0x00401fd0\t0x00401fd0\tAFTER\t1\t0x00401fe9\t0x00401fd0\tHeightDelta__Below015_D4\tMOV\tEAX, 0x1\tb8 01 00 00 00\tFALL_THROUGH\n",
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


class VectorMathSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_hardened_vector_math_signatures(self) -> None:
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
        self.assertEqual(report["summary"]["xrefRows"], 3)

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
