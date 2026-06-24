#!/usr/bin/env python3
"""Tests for the early-function Ghidra comment/signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_early_comment_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def write_fixture(root: Path, *, stale_signature: bool = False, overclaim: bool = False) -> dict[str, Path]:
    dry = root / "signature_dry.log"
    apply = root / "signature_apply.log"
    metadata = root / "metadata_final.tsv"
    decompile = root / "decompile_final"
    xrefs = root / "xrefs_final.tsv"
    instructions = root / "instructions_final.tsv"
    decompile.mkdir()

    dry.write_text("--- SUMMARY ---\nupdated=0 skipped=8 missing=0 bad=0\n", encoding="utf-8")
    apply.write_text("--- SUMMARY ---\nupdated=8 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    signatures = {
        "0x00401000": "void __thiscall CGenericActiveReader__SetReader(void * this, void * readerCell)",
        "0x00401040": "void __thiscall CMonitor__AddDeletionEvent(void * this, void * readerCell)",
        "0x004011b0": "void __stdcall vector_constructor_iterator_nothrow(void * base, int elemSize, int count, void * ctorFn)",
        "0x004014c0": "void __thiscall CFrontEndPage__ActiveNotification_NoOp(void * this, int fromPage)",
        "0x00403650": "void __thiscall CMeshRenderer__CopyBasisAndRefreshTime(void * this, void * srcBasis)",
        "0x00403f40": "void __fastcall CResourceDescriptor__ctor(void * this)",
        "0x00403f80": "void __fastcall CResourceDescriptor__dtor(void * this)",
        "0x004048f0": "int __cdecl CMesh__IsValidProfileIndex_1to10(int profileIndex)",
    }
    if stale_signature:
        signatures["0x004014c0"] = "void __stdcall CFrontEndPage__ActiveNotification_NoOp(void * this, int from_page)"
        signatures["0x00403650"] = "void __thiscall CMeshRenderer__CopyBasisAndRefreshTime(void * this, void * srcBasis, void * dst_basis)"

    comments = {
        "0x00401000": "Signature/comment hardening: rebinds a reader cell, removes the old reader through CSPtrSet__Remove, then registers the new reader with CMonitor__AddDeletionEvent. Exact runtime behavior remain unproven.",
        "0x00401040": "Signature/comment hardening: ensures a deletion-event set at +0x4 via CSptrSet__Init and appends readerCell with CSPtrSet__AddToHead. Exact runtime behavior remain unproven.",
        "0x004011b0": "Signature/comment hardening: CRT vector-constructor helper loops count elements, advances by elemSize, performs a computed call to ctorFn, and returns with ret 0x10. Exact runtime behavior remain unproven.",
        "0x004014c0": "Signature/comment hardening: frontend page active-notification no-op is a ret 0x4 thiscall-style vtable target. Exact runtime behavior remain unproven.",
        "0x00403650": "Signature/comment hardening: copies srcBasis into this as destination and refreshes +0xac from DAT_00672fd0 unless sentinel is present. Exact runtime behavior remain unproven.",
        "0x00403f40": "Signature/comment hardening: zeros descriptor byte slots and fields through +0x400, +0x414, and +0x418. Exact runtime behavior remain unproven.",
        "0x00403f80": "Signature/comment hardening: frees descriptor child pointers from +0x414/+0x418 with OID__FreeObject. Exact runtime behavior remain unproven.",
        "0x004048f0": "Signature/comment hardening: profileIndex returns true for 1..10 and is called from CMesh__Load. Exact runtime behavior remain unproven.",
    }
    if overclaim:
        comments["0x004048f0"] += " Runtime behavior proven."

    metadata.write_text(
        METADATA_HEADER
        + "".join(
            f"{addr}\t{probe.TARGETS[addr]['name']}\t{signatures[addr]}\t{comments[addr]}\tOK\n"
            for addr in probe.TARGETS
        ),
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        INDEX_HEADER
        + "".join(
            f"{addr}\t{probe.TARGETS[addr]['name']}\t{signatures[addr]}\tOK\n"
            for addr in probe.TARGETS
        ),
        encoding="utf-8",
    )

    decompile_tokens = {
        "0x00401000": "readerCell CSPtrSet__Remove CMonitor__AddDeletionEvent",
        "0x00401040": "readerCell OID__AllocObject CSPtrSet__Init CSPtrSet__AddToHead",
        "0x004011b0": "base elemSize count ctorFn",
        "0x004014c0": "fromPage",
        "0x00403650": "srcBasis +0xac DAT_00672fd0",
        "0x00403f40": "+0x400 +0x414 +0x418",
        "0x00403f80": "+0x414 +0x418 OID__FreeObject",
        "0x004048f0": "profileIndex 0xb",
    }
    for addr, expected in probe.TARGETS.items():
        (decompile / f"{addr[2:]}_{expected['name']}.c").write_text(
            f"{expected['name']} {signatures[addr]} {decompile_tokens[addr]}",
            encoding="utf-8",
        )

    xrefs.write_text(
        XREF_HEADER
        + "00401000\tCGenericActiveReader__SetReader\t0044b738\t0044b640\tCEventManager__Flush\tUNCONDITIONAL_CALL\n"
        + "00401000\tCGenericActiveReader__SetReader\t00405012\t00404dd0\tCBattleEngine__Init\tUNCONDITIONAL_CALL\n"
        + "00401000\tCGenericActiveReader__SetReader\t005073ab\t005069f0\tProjectileBurst__SpawnFromCurrentPreset\tUNCONDITIONAL_CALL\n"
        + "00401040\tCMonitor__AddDeletionEvent\t0040102a\t00401000\tCGenericActiveReader__SetReader\tUNCONDITIONAL_CALL\n"
        + "00401040\tCMonitor__AddDeletionEvent\t00538a85\t00538960\tCScriptEventNB__RegisterEventListener\tUNCONDITIONAL_CALL\n"
        + "004011b0\tvector_constructor_iterator_nothrow\t004a63de\t004a5b70\tCMesh__Load\tUNCONDITIONAL_CALL\n"
        + "004011b0\tvector_constructor_iterator_nothrow\t004b2dc7\t004b27a0\tCMeshPart__LoadFromStream\tUNCONDITIONAL_CALL\n"
        + "004011b0\tvector_constructor_iterator_nothrow\t0054a91f\t00549570\tCMeshRenderer__RenderMeshCore\tUNCONDITIONAL_CALL\n"
        + "004014c0\tCFrontEndPage__ActiveNotification_NoOp\t005df1f0\t<none>\t<no_function>\tDATA\n"
        + "00403650\tCMeshRenderer__CopyBasisAndRefreshTime\t004b656c\t004b6350\tCMeshRenderer__RenderMesh\tUNCONDITIONAL_CALL\n"
        + "00403650\tCMeshRenderer__CopyBasisAndRefreshTime\t0040ed6f\t0040ebf0\tCMonitor__UpdateTrackedList_620\tUNCONDITIONAL_CALL\n"
        + "00403f40\tCResourceDescriptor__ctor\t00515f68\t00515f60\tCResourceDescriptorTable__ctor\tDATA\n"
        + "00403f40\tCResourceDescriptor__ctor\t00405145\t00404dd0\tCBattleEngine__Init\tDATA\n"
        + "00403f40\tCResourceDescriptor__ctor\t004f8765\t004f86d0\tCUnit__Init\tDATA\n"
        + "00403f80\tCResourceDescriptor__dtor\t00403ff0\t00403ff0\tCDXLandscape__DestroyResourceDescriptorArray_Thunk\tDATA\n"
        + "00403f80\tCResourceDescriptor__dtor\t00515f63\t00515f60\tCResourceDescriptorTable__ctor\tDATA\n"
        + "00403f80\tCResourceDescriptor__dtor\t004f8760\t004f86d0\tCUnit__Init\tDATA\n"
        + "004048f0\tCMesh__IsValidProfileIndex_1to10\t004a87ed\t004a5b70\tCMesh__Load\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x00401000\t0x00401000\tAFTER\t23\t0x00401031\t0x00401000\tCGenericActiveReader__SetReader\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x00401040\t0x00401040\tAFTER\t38\t0x004010bb\t0x00401040\tCMonitor__AddDeletionEvent\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x004011b0\t0x004011b0\tAFTER\t20\t0x004011d7\t0x004011b0\tvector_constructor_iterator_nothrow\tRET\t0x10\tc2 10 00\tTERMINATOR\n"
        + "0x004014c0\t0x004014c0\tTARGET\t0\t0x004014c0\t0x004014c0\tCFrontEndPage__ActiveNotification_NoOp\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x00403650\t0x00403650\tAFTER\t17\t0x00403687\t0x00403650\tCMeshRenderer__CopyBasisAndRefreshTime\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x00403f40\t0x00403f40\tAFTER\t11\t0x00403f76\t0x00403f40\tCResourceDescriptor__ctor\tRET\t\tc3\tTERMINATOR\n"
        + "0x00403f80\t0x00403f80\tAFTER\t29\t0x00403fe1\t0x00403f80\tCResourceDescriptor__dtor\tRET\t\tc3\tTERMINATOR\n"
        + "0x004048f0\t0x004048f0\tAFTER\t6\t0x00404902\t0x004048f0\tCMesh__IsValidProfileIndex_1to10\tRET\t\tc3\tTERMINATOR\n",
        encoding="utf-8",
    )
    return {
        "dry": dry,
        "apply": apply,
        "metadata": metadata,
        "decompile_index": decompile / "index.tsv",
        "decompile_dir": decompile,
        "xrefs": xrefs,
        "instructions": instructions,
    }


class EarlyCommentSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_hardened_tranche(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], 8)
        self.assertEqual(report["summary"]["staleSignatureHits"], 0)
        self.assertEqual(report["summary"]["commentOverclaims"], 0)
        self.assertEqual(report["summary"]["retEvidenceHits"], 8)
        self.assertEqual(report["summary"]["xrefEvidenceHits"], 8)

    def test_fails_for_stale_signature_or_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale_signature=True, overclaim=True)
            report = probe.build_report(
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("forbidden signature token remains" in failure for failure in report["failures"]))
        self.assertTrue(any("runtime/source overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
