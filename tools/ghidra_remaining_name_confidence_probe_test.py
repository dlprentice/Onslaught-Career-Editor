#!/usr/bin/env python3
"""Tests for the remaining Ghidra name-confidence classifier."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_remaining_name_confidence_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def write_minimal_exports(root: Path, *, omit_unitai_caller_pointer: bool = False) -> None:
    decompile = root / "decompile"
    caller_decompile = root / "caller_decompile"
    decompile.mkdir()
    caller_decompile.mkdir()

    metadata_rows: list[str] = []
    index_rows: list[str] = []
    xref_rows: list[str] = []
    instruction_rows: list[str] = []
    caller_context_rows: list[str] = []

    for address, rule in probe.RULES.items():
        metadata_rows.append(
            f"{address}\t{rule['currentName']}\tvoid __fastcall {rule['currentName']}(void * param_1)\t"
            "Proof-boundary comment only: names, signatures, owners, and runtime behavior remain provisional.\tOK\n"
        )
        index_rows.append(
            f"{address}\t{rule['currentName']}\tvoid __fastcall {rule['currentName']}(void * param_1)\tOK\n"
        )
        (decompile / f"{address[2:]}_{rule['currentName']}.c").write_text(
            " ".join(rule["tokens"]), encoding="utf-8"
        )
        xref_rows.append(
            f"{address[2:]}\t{rule['currentName']}\t{rule['expectedFromAddr'][2:]}\t"
            f"{rule['expectedFromFunctionAddr']}\t{rule['expectedXrefFunction']}\t{rule['expectedRefType']}\n"
        )
        instruction_rows.append(
            f"{address}\t{address}\tTARGET\t0\t{address}\t{address}\t{rule['currentName']}\t"
            f"CALL\t{address}\t00\tUNCONDITIONAL_CALL\n"
        )

    for token in probe.RULES["0x00402dd0"]["callerContextTokens"]:
        caller_context_rows.append(
            "0x004478a3\t0x004478a3\tAFTER\t1\t0x004478a3\t<none>\t<no_function>\t"
            f"CALL\t{token}\t00\tUNCONDITIONAL_CALL\n"
        )
    caller_context_rows.append(
        "0x005d9080\t0x005d9080\tMISSING\t0\t<none>\t<none>\t<no_instruction>\t\t\t\t\n"
    )

    unitai_caller = (
        "CUnitAI_Unk_0044c720__Wrapper_0040dda0(*(void **)(param_1 + 0x50)); "
        "DAT_00672fd0 - *(float *)(*(int *)(param_1 + 0x50) + 0x2e8);"
    )
    if omit_unitai_caller_pointer:
        unitai_caller = "CUnitAI_Unk_0044c720__Wrapper_0040dda0(param_1);"

    (caller_decompile / "00485d50_CExplosionInitThing__RenderObjectiveStatusPanel.c").write_text(
        unitai_caller, encoding="utf-8"
    )
    (caller_decompile / "0044c720_CSquadNormal__GetCellValueAtWorldXY.c").write_text(
        "int CSquadNormal__GetCellValueAtWorldXY(void * this, int x, int y);", encoding="utf-8"
    )

    (root / "metadata.tsv").write_text(METADATA_HEADER + "".join(metadata_rows), encoding="utf-8")
    (decompile / "index.tsv").write_text(INDEX_HEADER + "".join(index_rows), encoding="utf-8")
    (root / "xrefs.tsv").write_text(XREF_HEADER + "".join(xref_rows), encoding="utf-8")
    (root / "instructions.tsv").write_text(INSTRUCTION_HEADER + "".join(instruction_rows), encoding="utf-8")
    (root / "caller_context_instructions.tsv").write_text(
        INSTRUCTION_HEADER + "".join(caller_context_rows), encoding="utf-8"
    )
    (caller_decompile / "index.tsv").write_text(
        INDEX_HEADER
        + "0x00485d50\tCExplosionInitThing__RenderObjectiveStatusPanel\tvoid __fastcall CExplosionInitThing__RenderObjectiveStatusPanel(int param_1)\tOK\n"
        + "0x0044c720\tCSquadNormal__GetCellValueAtWorldXY\tint __thiscall CSquadNormal__GetCellValueAtWorldXY(void * this, int param_1, int param_2)\tOK\n",
        encoding="utf-8",
    )


class GhidraRemainingNameConfidenceProbeTests(unittest.TestCase):
    def test_classifies_remaining_name_confidence_targets_from_caller_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_exports(root)

            report = probe.build_report(
                metadata_path=root / "metadata.tsv",
                decompile_index_path=root / "decompile" / "index.tsv",
                decompile_dir=root / "decompile",
                xrefs_path=root / "xrefs.tsv",
                instructions_path=root / "instructions.tsv",
                caller_context_instructions_path=root / "caller_context_instructions.tsv",
                caller_index_path=root / "caller_decompile" / "index.tsv",
                caller_decompile_dir=root / "caller_decompile",
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["targetCount"], 3)
        self.assertEqual(report["actionCounts"]["renameCandidate"], 1)
        self.assertEqual(report["actionCounts"]["deferRawCallerBoundary"], 1)
        self.assertEqual(report["actionCounts"]["deferTableOwner"], 1)

    def test_fails_when_unitai_caller_no_longer_passes_owned_actor_pointer(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_exports(root, omit_unitai_caller_pointer=True)

            report = probe.build_report(
                metadata_path=root / "metadata.tsv",
                decompile_index_path=root / "decompile" / "index.tsv",
                decompile_dir=root / "decompile",
                xrefs_path=root / "xrefs.tsv",
                instructions_path=root / "instructions.tsv",
                caller_context_instructions_path=root / "caller_context_instructions.tsv",
                caller_index_path=root / "caller_decompile" / "index.tsv",
                caller_decompile_dir=root / "caller_decompile",
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("0x0040dda0" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
