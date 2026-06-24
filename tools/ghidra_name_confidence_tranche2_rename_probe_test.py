#!/usr/bin/env python3
"""Tests for the second Ghidra name-confidence rename-candidate correction probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_name_confidence_tranche2_rename_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"


def write_fixture(root: Path, *, omit_boundary_token: bool = False) -> dict[str, Path]:
    rename_dry = root / "rename_dry.log"
    rename_apply = root / "rename_apply.log"
    comments_dry = root / "comment_dry.log"
    comments_apply = root / "comment_apply.log"
    metadata = root / "metadata_after.tsv"
    xrefs = root / "xrefs_after.tsv"
    decompile = root / "decompile_after"
    decompile.mkdir()

    renames = [
        (
            "0x00414b30",
            "CVBufTexture_Unk_0050a290__Wrapper_00414b30",
            "TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit",
        ),
        (
            "0x00505c30",
            "stricmp__Wrapper_00505c30",
            "NamedEntryList__FindNearestChildByNameAndPosition",
        ),
    ]

    rename_dry.write_text(
        "\n".join(["Mode: args (dry)"] + [f"DRY: {addr} {old} -> {new}" for addr, old, new in renames] + [
            "--- SUMMARY ---",
            "applied=0 skipped=2 missing=0 bad=0",
        ])
        + "\n",
        encoding="utf-8",
    )
    rename_apply.write_text(
        "\n".join(["Mode: args (apply)"] + [f"OK: {addr} {old} -> {new}" for addr, old, new in renames] + [
            "--- SUMMARY ---",
            "applied=2 skipped=0 missing=0 bad=0",
        ])
        + "\n",
        encoding="utf-8",
    )
    comments_dry.write_text(
        "\n".join(["Mode: dry"] + [f"DRY: {addr} {new}" for addr, _, new in renames] + [
            "--- SUMMARY ---",
            "applied=0 skipped=2 missing=0 bad=0",
        ])
        + "\n",
        encoding="utf-8",
    )
    comments_apply.write_text(
        "\n".join(["Mode: apply"] + [f"OK: {addr} {new}" for addr, _, new in renames] + [
            "--- SUMMARY ---",
            "applied=2 skipped=0 missing=0 bad=0",
        ])
        + "\n",
        encoding="utf-8",
    )

    runtime_boundary = "runtime behavior remain deferred"
    if omit_boundary_token:
        runtime_boundary = "runtime behavior proven"

    metadata.write_text(
        METADATA_HEADER
        + "0x00414b30\tTargetSet__AnyUnitTargetTimeoutBeforeProfileLimit\tint __fastcall TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit(void * param_1)\t"
        + f"Behavior-backed rename from weak CVBufTexture wrapper. Evidence: scans a linked target/unit set, calls CUnit__IsTargetTimeoutBeforeProfileLimit on each entry, and is called by CBattleEngine__UpdateAutoTargetSetAndFireProjectiles. Exact source identity, signature, types, and {runtime_boundary}.\tOK\n"
        + "0x00505c30\tNamedEntryList__FindNearestChildByNameAndPosition\tint __cdecl NamedEntryList__FindNearestChildByNameAndPosition(void * param_1, void * param_2)\t"
        + "Behavior-backed rename from weak stricmp wrapper. Evidence: finds a named entry by case-insensitive string compare, then returns the nearest child point by squared 3D distance. Owner/type/source identity and runtime behavior remain deferred.\tOK\n",
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        INDEX_HEADER
        + "0x00414b30\tTargetSet__AnyUnitTargetTimeoutBeforeProfileLimit\tint __fastcall TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit(void * param_1)\tOK\n"
        + "0x00505c30\tNamedEntryList__FindNearestChildByNameAndPosition\tint __cdecl NamedEntryList__FindNearestChildByNameAndPosition(void * param_1, void * param_2)\tOK\n",
        encoding="utf-8",
    )
    (decompile / "00414b30_TargetSet__AnyUnitTargetTimeoutBeforeProfileLimit.c").write_text(
        "iVar2 = CUnit__IsTargetTimeoutBeforeProfileLimit(iVar2); if (iVar2 != 0) { return 1; }",
        encoding="utf-8",
    )
    (decompile / "00505c30_NamedEntryList__FindNearestChildByNameAndPosition.c").write_text(
        "iVar6 = stricmp(*(char **)(iVar7 + 4),param_1); DAT_00854fc8 = DAT_00854fc0; fVar4 = 0x4b18967f; fVar5 = *(float *)(iVar8 + 0x24);",
        encoding="utf-8",
    )
    xrefs.write_text(
        XREF_HEADER
        + "00414b30\tTargetSet__AnyUnitTargetTimeoutBeforeProfileLimit\t0040657e\t00406560\tCBattleEngine__UpdateAutoTargetSetAndFireProjectiles\tUNCONDITIONAL_CALL\n"
        + "00414b30\tTargetSet__AnyUnitTargetTimeoutBeforeProfileLimit\t0040658b\t00406560\tCBattleEngine__UpdateAutoTargetSetAndFireProjectiles\tUNCONDITIONAL_CALL\n"
        + "00505c30\tNamedEntryList__FindNearestChildByNameAndPosition\t00537d8c\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n"
        + "00505c30\tNamedEntryList__FindNearestChildByNameAndPosition\t00537e6b\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )

    return {
        "rename_dry": rename_dry,
        "rename_apply": rename_apply,
        "comments_dry": comments_dry,
        "comments_apply": comments_apply,
        "metadata": metadata,
        "decompile_index": decompile / "index.tsv",
        "decompile_dir": decompile,
        "xrefs": xrefs,
    }


class GhidraNameConfidenceTranche2RenameProbeTests(unittest.TestCase):
    def test_passes_for_clean_rename_comment_and_context_readback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                rename_dry_log_path=paths["rename_dry"],
                rename_apply_log_path=paths["rename_apply"],
                comments_dry_log_path=paths["comments_dry"],
                comments_apply_log_path=paths["comments_apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["candidateClassification"], "tranche2-rename-candidates-renamed-commented")
        self.assertTrue(report["readback"]["allNamesCommentsAndContextPresent"])

    def test_fails_when_comment_loses_runtime_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), omit_boundary_token=True)
            report = probe.build_report(
                rename_dry_log_path=paths["rename_dry"],
                rename_apply_log_path=paths["rename_apply"],
                comments_dry_log_path=paths["comments_dry"],
                comments_apply_log_path=paths["comments_apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("0x00414b30" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
