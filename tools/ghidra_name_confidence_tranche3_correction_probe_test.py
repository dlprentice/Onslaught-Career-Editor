#!/usr/bin/env python3
"""Tests for the third Ghidra name-confidence correction probe."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import ghidra_name_confidence_tranche3_correction_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def write_fixture(root: Path, *, overclaim_signature: bool = False) -> dict[str, Path]:
    rename_map = root / "rename_map_tranche3_corrections.txt"
    comments = root / "comments_after_rename.tsv"
    metadata = root / "metadata_readback.tsv"
    xrefs = root / "xrefs_readback.tsv"
    instructions = root / "instructions_readback.tsv"
    queue = root / "static-reaudit-queue.json"
    decompile = root / "decompile_readback"
    decompile.mkdir()

    renames = [
        (
            "0x0050b010",
            "CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk",
            "CWorld__AddUnitToOccupancyGridAndRebuildShadows",
        ),
        ("0x0050b020", "CWorld__RemoveUnitFromOccupancyGrid_Thunk", "CWorld__RemoveUnitFromOccupancyGrid"),
        ("0x0053f7d0", "CDXBitmapFont__InitNamedFontSlot", "StringScratch__CopyRotating4K"),
        ("0x0055e412", "CDXTexture__LoadPathFallbackNoFlags_Thunk", "CDXTexture__LoadFromPathWithFallbackExtensions"),
        ("0x0055e45f", "CRT__OpenFileByModeString_AutoUnlock", "CRT__OpenFileByModeString"),
        ("0x0056d21c", "CRT__IsDigitCharTypeMask_Thunk", "CRT__IsCharTypeMaskOrLeadByte_0056d22d"),
    ]

    rename_map.write_text("".join(f"{address} {name}\n" for address, name, _ in renames), encoding="utf-8")
    comments.write_text(
        "address\tname\tcomment\n"
        + "".join(
            f"{address}\t{name}\tProof boundary 2026-05-09 Wave 259: {token}; exact source identity, tags, types, and runtime behavior remain open.\n"
            for address, name, token in renames
        ),
        encoding="utf-8",
    )

    signature_note = "Current saved signature still needs review"
    if overclaim_signature:
        signature_note = "Current saved signature is final"

    metadata.write_text(
        METADATA_HEADER
        + "0x0050b010\tCWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk\tvoid __stdcall CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk(void * param_1)\tProof boundary 2026-05-09 Wave 259: thin wrapper into CWorld__AddUnitToOccupancyGridAndRebuildShadows. Name is behavior-backed; signature, exact source identity, tags, types, and runtime behavior remain open.\tOK\n"
        + "0x0050b020\tCWorld__RemoveUnitFromOccupancyGrid_Thunk\tvoid __stdcall CWorld__RemoveUnitFromOccupancyGrid_Thunk(void * param_1)\tProof boundary 2026-05-09 Wave 259: thin wrapper into CWorld__RemoveUnitFromOccupancyGrid. Name is behavior-backed; signature, exact source identity, tags, types, and runtime behavior remain open.\tOK\n"
        + "0x0053f7d0\tCDXBitmapFont__InitNamedFontSlot\tvoid __thiscall CDXBitmapFont__InitNamedFontSlot(void * this, void * param_1, void * param_2, int param_3, int param_4)\tProof boundary 2026-05-09 Wave 259: called by PCPlatform__LoadFonts for bitmap-font slot setup, copies a temporary string into the object and initializes fields including +0x54, +0x58, +0x15c, and +0x170. CDXBitmapFont ownership is behavior-backed but exact source identity, signature, tags, types, and runtime behavior remain open.\tOK\n"
        + "0x0055e412\tCDXTexture__LoadPathFallbackNoFlags_Thunk\tvoid __cdecl CDXTexture__LoadPathFallbackNoFlags_Thunk(int param_1, int param_2)\tProof boundary 2026-05-09 Wave 259: forwards to CDXTexture__LoadFromPathWithFallbackExtensions with stack-local option context and fixed no-flags behavior. Name is behavior-backed; signature, exact source identity, tags, types, and runtime behavior remain open.\tOK\n"
        + "0x0055e45f\tCRT__OpenFileByModeString_AutoUnlock\tint __cdecl CRT__OpenFileByModeString_AutoUnlock(int param_1, int param_2, int param_3)\tProof boundary 2026-05-09 Wave 259: acquires a CRT file-stream slot, calls CRT__OpenFileByModeString, and unlocks through the routed unlock helper before returning. Name is behavior-backed; signature, exact source identity, tags, types, and runtime behavior remain open.\tOK\n"
        + f"0x0056d21c\tCRT__IsDigitCharTypeMask_Thunk\tvoid __cdecl CRT__IsDigitCharTypeMask_Thunk(int param_1)\tProof boundary 2026-05-09 Wave 259: pushes ctype digit mask 4, calls CRT__IsCharTypeMaskOrLeadByte_0056d22d, adjusts the stack, and returns with the callee result preserved in EAX. {signature_note}; exact source identity, tags, types, and runtime behavior remain open.\tOK\n",
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        INDEX_HEADER + "".join(
            f"{address}\t{name}\tvoid __cdecl {name}(int param_1)\tOK\n" for address, name, _ in renames
        ),
        encoding="utf-8",
    )
    (decompile / "0050b010_CWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk.c").write_text(
        "CWorld__AddUnitToOccupancyGridAndRebuildShadows(param_1);", encoding="utf-8"
    )
    (decompile / "0050b020_CWorld__RemoveUnitFromOccupancyGrid_Thunk.c").write_text(
        "CWorld__RemoveUnitFromOccupancyGrid(param_1);", encoding="utf-8"
    )
    (decompile / "0053f7d0_CDXBitmapFont__InitNamedFontSlot.c").write_text(
        "StringScratch__CopyRotating4K(param_1); *(int *)((int)this + 0x54)=0; *(int *)((int)this + 0x58)=0; *(undefined4 *)((int)this + 0x170)=0; *(undefined1 *)((int)this + 0x15c)=1;",
        encoding="utf-8",
    )
    (decompile / "0055e412_CDXTexture__LoadPathFallbackNoFlags_Thunk.c").write_text(
        "CDXTexture__LoadFromPathWithFallbackExtensions(param_1,(void *)param_2,(int)&stack0x0000000c,0);",
        encoding="utf-8",
    )
    (decompile / "0055e45f_CRT__OpenFileByModeString_AutoUnlock.c").write_text(
        "CRT__AcquireFileStreamSlot(); CRT__OpenFileByModeString(param_1,(void *)param_2,param_3,pvVar1); CRT__UnlockRouteByAddress((uint)pvVar1);",
        encoding="utf-8",
    )
    (decompile / "0056d21c_CRT__IsDigitCharTypeMask_Thunk.c").write_text(
        "CRT__IsCharTypeMaskOrLeadByte_0056d22d(param_1,0,4);",
        encoding="utf-8",
    )
    xrefs.write_text(
        XREF_HEADER
        + "0050b010\tCWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk\t00447ade\t00447ac0\tCUnitAI__PlayWingFoldedAnimationAndSetState3\tUNCONDITIONAL_CALL\n"
        + "0050b010\tCWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk\t0044cb44\t0044ca30\tCFeature__VFunc_09_0044ca30\tUNCONDITIONAL_CALL\n"
        + "0050b010\tCWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk\t0050494c\t005047e0\tCWarspiteDome__Init\tUNCONDITIONAL_CALL\n"
        + "0050b010\tCWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk\t0041b32c\t0041b1a0\tCCannon__Init\tUNCONDITIONAL_CALL\n"
        + "0050b010\tCWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk\t004bbd94\t004bbcd0\tCNamedMesh__VFunc_09_004bbcd0\tUNCONDITIONAL_CALL\n"
        + "0050b010\tCWorld__AddUnitToOccupancyGridAndRebuildShadows_Thunk\t004dfa94\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n"
        + "0050b020\tCWorld__RemoveUnitFromOccupancyGrid_Thunk\t0041b459\t0041b450\tCCannon__Destructor\tUNCONDITIONAL_CALL\n"
        + "0050b020\tCWorld__RemoveUnitFromOccupancyGrid_Thunk\t004bc059\t004bc050\tCNamedMesh__VFunc_02_004bc050\tUNCONDITIONAL_CALL\n"
        + "0050b020\tCWorld__RemoveUnitFromOccupancyGrid_Thunk\t00447109\t00447100\tCDropship__VFunc_02_00447100\tUNCONDITIONAL_CALL\n"
        + "0050b020\tCWorld__RemoveUnitFromOccupancyGrid_Thunk\t0044cbf4\t0044cbe0\tCFeature__VFunc_02_0044cbe0\tUNCONDITIONAL_CALL\n"
        + "0053f7d0\tCDXBitmapFont__InitNamedFontSlot\t005156d0\t005155e0\tPCPlatform__LoadFonts\tUNCONDITIONAL_CALL\n"
        + "0055e412\tCDXTexture__LoadPathFallbackNoFlags_Thunk\t0042d05a\t0042cfa0\tFatalError__ExitProcess\tUNCONDITIONAL_CALL\n"
        + "0055e45f\tCRT__OpenFileByModeString_AutoUnlock\t0055e49a\t0055e490\tfopen\tUNCONDITIONAL_CALL\n"
        + "0056d21c\tCRT__IsDigitCharTypeMask_Thunk\t00568df1\t00568dc6\tCRT__ParseCommandLineToken\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x0056d21c\t0x0056d21c\tAFTER\t3\t0x0056d224\t0x0056d21c\tCRT__IsDigitCharTypeMask_Thunk\tCALL\t0x0056d22d\te8 04 00 00 00\tUNCONDITIONAL_CALL\n"
        + "0x0056d21c\t0x0056d21c\tAFTER\t4\t0x0056d229\t0x0056d21c\tCRT__IsDigitCharTypeMask_Thunk\tADD\tESP, 0xc\t83 c4 0c\tFALL_THROUGH\n"
        + "0x0056d21c\t0x0056d21c\tAFTER\t5\t0x0056d22c\t0x0056d21c\tCRT__IsDigitCharTypeMask_Thunk\tRET\t\tc3\tTERMINATOR\n",
        encoding="utf-8",
    )
    queue.write_text(
        json.dumps(
            {
                "status": "PASS",
                "totalFunctions": 5863,
                "qualitySignals": {
                    "commentlessFunctionCount": 5495,
                    "undefinedSignatureCount": 2087,
                    "paramSignatureCount": 2563,
                    "uncertainOwnerNameCount": 9,
                    "helperAddressNameCount": 0,
                    "wrapperAddressNameCount": 16,
                },
            }
        ),
        encoding="utf-8",
    )

    return {
        "rename_map": rename_map,
        "comments": comments,
        "metadata": metadata,
        "decompile_index": decompile / "index.tsv",
        "decompile_dir": decompile,
        "xrefs": xrefs,
        "instructions": instructions,
        "queue": queue,
    }


class GhidraNameConfidenceTranche3CorrectionProbeTests(unittest.TestCase):
    def test_passes_for_clean_saved_correction_readback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                rename_map_path=paths["rename_map"],
                comments_path=paths["comments"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
                queue_report_path=paths["queue"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["candidateClassification"], "tranche3-corrections-renamed-commented")
        self.assertTrue(report["readback"]["allNamesCommentsAndContextPresent"])
        self.assertEqual(report["queue"]["qualitySignals"]["commentlessFunctionCount"], 5495)

    def test_fails_when_digit_wrapper_comment_overclaims_signature(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), overclaim_signature=True)
            report = probe.build_report(
                rename_map_path=paths["rename_map"],
                comments_path=paths["comments"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
                queue_report_path=paths["queue"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("0x0056d21c" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
