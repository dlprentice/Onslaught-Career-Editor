#!/usr/bin/env python3
"""Tests for the linked-list / monitor Ghidra signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_linked_monitor_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
VTABLE_HEADER = "vtable\tcol_ptr_slot\tcol_addr\tsignature\toffset\tcd_offset\ttype_desc\tclass_desc\traw_type_name\tdemangled_type_name\n"


def write_fixture(root: Path, *, stale_name: bool = False, stale_param: bool = False, overclaim: bool = False) -> dict[str, Path]:
    dry = root / "signature_dry.log"
    apply = root / "signature_apply.log"
    metadata = root / "metadata_final.tsv"
    decompile = root / "decompile_final"
    xrefs = root / "xrefs_final.tsv"
    instructions = root / "instructions_full.tsv"
    vtables = root / "vtable_types.tsv"
    decompile.mkdir()

    dry.write_text("--- SUMMARY ---\nupdated=0 skipped=6 missing=0 bad=0\n", encoding="utf-8")
    apply.write_text("--- SUMMARY ---\nupdated=6 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    names = {
        "0x00409760": "LinkedPtrCursor__MoveFirstAndGet",
        "0x00409780": "LinkedPtrCursor__MoveNextAndGet",
        "0x004097a0": "CUnit__PushTransformHistoryAndSetCurrent",
        "0x00409880": "CMonitor__GetLastValidRangeStep100",
        "0x004098e0": "CLine__ctor_copy",
        "0x00409950": "CMonitor__UpdateSoundEventPlaybackForReader",
    }
    if stale_name:
        names["0x004098e0"] = "CGeneralVolume__ctor_like_004098e0"

    signatures = {
        "0x00409760": "void * __fastcall LinkedPtrCursor__MoveFirstAndGet(void * cursor)",
        "0x00409780": "void * __fastcall LinkedPtrCursor__MoveNextAndGet(void * cursor)",
        "0x004097a0": "void __thiscall CUnit__PushTransformHistoryAndSetCurrent(void * this, void * transform)",
        "0x00409880": "int __fastcall CMonitor__GetLastValidRangeStep100(void * monitor)",
        "0x004098e0": "void __thiscall CLine__ctor_copy(void * this, void * sourceLine)",
        "0x00409950": "void __fastcall CMonitor__UpdateSoundEventPlaybackForReader(void * monitor)",
    }
    if stale_param:
        signatures["0x004097a0"] = "void __thiscall CUnit__PushTransformHistoryAndSetCurrent(void * this, void * param_1, void * param_2)"

    comments = {
        "0x00409760": "Signature hardening: iterator/cursor First helper reads list +0x4, stores current node, and returns the item pointer. Exact list layout and runtime behavior remain unproven.",
        "0x00409780": "Signature hardening: iterator/cursor Next helper advances current node and returns the item pointer. Exact list layout and runtime behavior remain unproven.",
        "0x004097a0": "Signature hardening: ret 0x4 shows one transform pointer; body pushes current/old transform history and updates +0xac timestamp. Exact CUnit layout and runtime behavior remain unproven.",
        "0x00409880": "Signature hardening: monitor range-step helper scans five 100-step slots from monitor +0xa4 and returns last nonnegative slot. Exact layout and runtime behavior remain unproven.",
        "0x004098e0": "Owner correction: body installs CGeneralVolume base vtable and CLine vtable while copying three 16-byte rows from sourceLine. Exact constructor identity and layout remain unproven.",
        "0x00409950": "Signature hardening: monitor sound-event helper updates engine/health/energy/lock/walk sound chains and active-reader state. Runtime audio behavior remains unproven.",
    }
    if overclaim:
        comments["0x00409950"] += " Runtime audio behavior proven."

    metadata.write_text(
        METADATA_HEADER + "".join(f"{addr}\t{names[addr]}\t{signatures[addr]}\t{comments[addr]}\tOK\n" for addr in names),
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        INDEX_HEADER + "".join(f"{addr}\t{names[addr]}\t{signatures[addr]}\tOK\n" for addr in names),
        encoding="utf-8",
    )
    decompile_tokens = {
        "0x00409760": "cursor +0x4 return (void *)0x0",
        "0x00409780": "cursor +0x4 return (void *)0x0",
        "0x004097a0": "transform +0x40 +0x80 +0xac DAT_00672fd0",
        "0x00409880": "monitor +0xa4 100 500",
        "0x004098e0": "sourceLine PTR_LAB_005d892c PTR_VFuncSlot_00_00426340_005d8bfc",
        "0x00409950": "monitor CMonitor__HasAnySoundEventForReaderChain CGenericActiveReader__SetReader +0x5c4 +0x5e8 +0x5d0",
    }
    for addr, name in names.items():
        (decompile / f"{addr[2:]}_{name}.c").write_text(
            f"{name} {signatures[addr]} {decompile_tokens[addr]}",
            encoding="utf-8",
        )
    xrefs.write_text(
        XREF_HEADER
        + "00409760\tLinkedPtrCursor__MoveFirstAndGet\t004081ef\t004081c0\tCMonitor__Process\tUNCONDITIONAL_CALL\n"
        + "00409780\tLinkedPtrCursor__MoveNextAndGet\t00408214\t004081c0\tCMonitor__Process\tUNCONDITIONAL_CALL\n"
        + "004097a0\tCUnit__PushTransformHistoryAndSetCurrent\t00408418\t004081c0\tCMonitor__Process\tUNCONDITIONAL_CALL\n"
        + "00409880\tCMonitor__GetLastValidRangeStep100\t00408a49\t004081c0\tCMonitor__Process\tUNCONDITIONAL_CALL\n"
        + "004098e0\tCLine__ctor_copy\t00409544\t004081c0\tCMonitor__Process\tUNCONDITIONAL_CALL\n"
        + "00409950\tCMonitor__UpdateSoundEventPlaybackForReader\t0040963e\t004081c0\tCMonitor__Process\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x00409760\t0x00409760\tAFTER\t7\t0x0040976d\t0x00409760\tLinkedPtrCursor__MoveFirstAndGet\tRET\t\tc3\tTERMINATOR\n"
        + "0x00409780\t0x00409780\tAFTER\t7\t0x0040978d\t0x00409780\tLinkedPtrCursor__MoveNextAndGet\tRET\t\tc3\tTERMINATOR\n"
        + "0x004097a0\t0x004097a0\tAFTER\t76\t0x0040981c\t0x004097a0\tCUnit__PushTransformHistoryAndSetCurrent\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x00409880\t0x00409880\tAFTER\t16\t0x004098a2\t0x00409880\tCMonitor__GetLastValidRangeStep100\tRET\t\tc3\tTERMINATOR\n"
        + "0x004098e0\t0x004098e0\tAFTER\t58\t0x0040994c\t0x004098e0\tCLine__ctor_copy\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x00409950\t0x00409950\tAFTER\t640\t0x00409dd3\t0x00409950\tCMonitor__UpdateSoundEventPlaybackForReader\tRET\t\tc3\tTERMINATOR\n",
        encoding="utf-8",
    )
    vtables.write_text(
        VTABLE_HEADER
        + "005d892c\t005d8928\t0060c658\t0x00000000\t0\t0\t0x00622f10\t0x0060c648\t.?AVCGeneralVolume@@\tCGeneralVolume\n"
        + "005d8bfc\t005d8bf8\t0060c740\t0x00000000\t0\t0\t0x006232a8\t0x0060c730\t.?AVCLine@@\tCLine\n",
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
        "vtables": vtables,
    }


class LinkedMonitorSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_corrected_linked_monitor_targets(self) -> None:
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
                vtable_types_path=paths["vtables"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], 6)
        self.assertEqual(report["summary"]["renamedTargets"], 1)
        self.assertEqual(report["summary"]["paramSignatureHits"], 0)
        self.assertGreaterEqual(report["summary"]["retEvidenceHits"], 6)

    def test_fails_for_stale_name_param_signature_or_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale_name=True, stale_param=True, overclaim=True)
            report = probe.build_report(
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
                vtable_types_path=paths["vtables"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("stale name" in failure for failure in report["failures"]))
        self.assertTrue(any("param_N signature remains" in failure for failure in report["failures"]))
        self.assertTrue(any("runtime/source overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
