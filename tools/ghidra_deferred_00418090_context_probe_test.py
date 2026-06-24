#!/usr/bin/env python3
"""Tests for the deferred 0x00418090 Ghidra context probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_deferred_00418090_context_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
TABLE_HEADER = "slot\tentry_addr\tptr\tptr_name\tptr_signature\n"
TYPE_HEADER = "vtable\tcol_ptr_slot\tcol_addr\tsignature\toffset\tcd_offset\ttype_desc\tclass_desc\traw_type_name\tdemangled_type_name\n"


def write_fixture(root: Path, *, remove_boundary: bool = False) -> dict[str, Path]:
    comments_dry = root / "comments_dry.log"
    comments_apply = root / "comments_apply.log"
    metadata = root / "metadata_readback.tsv"
    xrefs = root / "xrefs_readback.tsv"
    table = root / "table_005d9000_96.tsv"
    type_names = root / "vtable_type_names.tsv"
    type_names_9080 = root / "vtable_type_names_9080.tsv"
    data_xrefs = root / "data_xrefs.tsv"
    decompile = root / "decompile_readback"
    decompile.mkdir()

    address = "0x00418090"
    name = "FindAnimationIndex__Wrapper_00418090"
    comment = (
        "Opening-animation state callback candidate. Evidence: state field +0x254, timer field +0x25c, "
        "s_opening_00623ba4, FindAnimationIndex call, animation start vcall +0xf0, and DATA xref from mixed table slot 0x005d9080. "
        "Owner/table boundary, exact source identity, signature/types, tags, and runtime behavior remain provisional."
    )
    if remove_boundary:
        comment = comment.replace("runtime behavior remain provisional", "runtime behavior proven")

    comments_dry.write_text("Mode: dry\nDRY: 0x00418090 FindAnimationIndex__Wrapper_00418090\n--- SUMMARY ---\napplied=0 skipped=1 missing=0 bad=0\n", encoding="utf-8")
    comments_apply.write_text("Mode: apply\nOK: 0x00418090 FindAnimationIndex__Wrapper_00418090\n--- SUMMARY ---\napplied=1 skipped=0 missing=0 bad=0\n", encoding="utf-8")
    metadata.write_text(
        METADATA_HEADER + f"{address}\t{name}\tint __fastcall {name}(void * param_1)\t{comment}\tOK\n",
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        INDEX_HEADER + f"{address}\t{name}\tint __fastcall {name}(void * param_1)\tOK\n",
        encoding="utf-8",
    )
    (decompile / f"{address[2:]}_{name}.c").write_text(
        "s_opening_00623ba4 FindAnimationIndex + 0x254 + 0x25c + 0xf0",
        encoding="utf-8",
    )
    xrefs.write_text(
        XREF_HEADER + "00418090\tFindAnimationIndex__Wrapper_00418090\t005d9080\t<none>\t<no_function>\tDATA\n",
        encoding="utf-8",
    )
    table.write_text(
        TABLE_HEADER
        + "31\t005d907c\t004014c0\tCFrontEndPage__ActiveNotification_NoOp\tvoid __stdcall CFrontEndPage__ActiveNotification_NoOp(void * this, int from_page)\n"
        + "32\t005d9080\t00418090\tFindAnimationIndex__Wrapper_00418090\tint __fastcall FindAnimationIndex__Wrapper_00418090(void * param_1)\n"
        + "34\t005d9088\t3d23d70a\t<none>\t<none>\n"
        + "35\t005d908c\t39a3d70a\t<none>\t<none>\n"
        + "37\t005d9094\t00401be0\tVFuncSlot_00_00401be0\tvoid __thiscall VFuncSlot_00_00401be0(void * this, int param_1, void * param_2)\n"
        + "68\t005d9110\t00418430\tCByteSprite__scalar_deleting_dtor\tundefined CByteSprite__scalar_deleting_dtor(void)\n",
        encoding="utf-8",
    )
    type_names.write_text(
        TYPE_HEADER
        + "005d9094\t005d9090\t0060ca90\t0x00000000\t8\t0\t0x00623be0\t0x0060cb00\t.?AVCBuildingNamedMesh@@\tCBuildingNamedMesh\n",
        encoding="utf-8",
    )
    type_names_9080.write_text(
        TYPE_HEADER
        + "005d9080\t005d907c\t004014c0\t0x900004c2\t-1869574000\t-1869574000\t0x90909090\t0x8564418b\t\t\n",
        encoding="utf-8",
    )
    data_xrefs.write_text(
        XREF_HEADER
        + "005d9088\t<no_function>\t004fe92e\t004fe710\tCWarspite__Init\tREAD\n"
        + "005d9094\t<no_function>\t004bf3e9\t004bf090\tOID__CreateObject\tDATA\n",
        encoding="utf-8",
    )

    return {
        "comments_dry": comments_dry,
        "comments_apply": comments_apply,
        "metadata": metadata,
        "decompile_index": decompile / "index.tsv",
        "decompile_dir": decompile,
        "xrefs": xrefs,
        "table": table,
        "type_names": type_names,
        "type_names_9080": type_names_9080,
        "data_xrefs": data_xrefs,
    }


class GhidraDeferred00418090ContextProbeTests(unittest.TestCase):
    def test_passes_for_conservative_opening_animation_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                comments_dry_log_path=paths["comments_dry"],
                comments_apply_log_path=paths["comments_apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                table_path=paths["table"],
                type_names_path=paths["type_names"],
                type_names_9080_path=paths["type_names_9080"],
                data_xrefs_path=paths["data_xrefs"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["candidateClassification"], "deferred-opening-animation-context-commented-owner-unproven")
        self.assertTrue(report["readback"]["commentBoundaryPresent"])
        self.assertTrue(report["tableContext"]["mixedRegionPresent"])

    def test_fails_when_comment_overclaims_runtime_behavior(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), remove_boundary=True)
            report = probe.build_report(
                comments_dry_log_path=paths["comments_dry"],
                comments_apply_log_path=paths["comments_apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                table_path=paths["table"],
                type_names_path=paths["type_names"],
                type_names_9080_path=paths["type_names_9080"],
                data_xrefs_path=paths["data_xrefs"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("boundary" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
