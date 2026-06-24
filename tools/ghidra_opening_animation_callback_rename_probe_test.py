#!/usr/bin/env python3
"""Tests for the 0x00418090 opening-animation callback rename probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_opening_animation_callback_rename_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
TABLE_HEADER = "slot\tentry_addr\tptr\tptr_name\tptr_signature\n"
TYPE_HEADER = "vtable\tcol_ptr_slot\tcol_addr\tsignature\toffset\tcd_offset\ttype_desc\tclass_desc\traw_type_name\tdemangled_type_name\n"


def write_fixture(root: Path, *, overclaim_owner: bool = False, include_target_in_ccockpit_table: bool = False) -> dict[str, Path]:
    rename_dry = root / "rename_dry.log"
    rename_apply = root / "rename_apply.log"
    comments_dry = root / "comments_dry.log"
    comments_apply = root / "comments_apply.log"
    metadata = root / "metadata_readback.tsv"
    decompile = root / "decompile_readback"
    xrefs = root / "xrefs_readback.tsv"
    mixed_table = root / "table_005d8f80_160.tsv"
    unresolved_types = root / "vtable_type_names.tsv"
    cockpit_types = root / "ccockpit_vtable_type_names.tsv"
    cockpit_table_a = root / "table_005d94ac_64.tsv"
    cockpit_table_b = root / "table_005d9524_40.tsv"
    decompile.mkdir()

    comment = (
        "Opening-animation state callback semantic rename. Evidence: state field +0x254, timer field +0x25c, "
        "s_opening_00623ba4, FindAnimationIndex call, animation start vcall +0xf0, and DATA xref from mixed table slot 0x005d9080. "
        "The 0x005d9080 table owner remains unresolved; resolved CCockpit RTTI vtables were checked separately and do not prove this slot. "
        "Exact owner, source identity, signature/types, tags, and runtime behavior remain unproven."
    )
    if overclaim_owner:
        comment = comment.replace("The 0x005d9080 table owner remains unresolved", "The 0x005d9080 table owner is proven")

    rename_dry.write_text(
        "Mode: args (dry)\nDRY: 0x00418090 FindAnimationIndex__Wrapper_00418090 -> OpeningAnimationStateCallback__StartOpeningIfPending\n--- SUMMARY ---\napplied=0 skipped=1 missing=0 bad=0\n",
        encoding="utf-8",
    )
    rename_apply.write_text(
        "Mode: args (apply)\nOK: 0x00418090 FindAnimationIndex__Wrapper_00418090 -> OpeningAnimationStateCallback__StartOpeningIfPending\n--- SUMMARY ---\napplied=1 skipped=0 missing=0 bad=0\n",
        encoding="utf-8",
    )
    comments_dry.write_text(
        "Mode: dry\nDRY: 0x00418090 OpeningAnimationStateCallback__StartOpeningIfPending\n--- SUMMARY ---\napplied=0 skipped=1 missing=0 bad=0\n",
        encoding="utf-8",
    )
    comments_apply.write_text(
        "Mode: apply\nOK: 0x00418090 OpeningAnimationStateCallback__StartOpeningIfPending\n--- SUMMARY ---\napplied=1 skipped=0 missing=0 bad=0\n",
        encoding="utf-8",
    )
    metadata.write_text(
        METADATA_HEADER
        + "0x00418090\tOpeningAnimationStateCallback__StartOpeningIfPending\tint __fastcall OpeningAnimationStateCallback__StartOpeningIfPending(void * param_1)\t"
        + comment
        + "\tOK\n",
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        INDEX_HEADER
        + "0x00418090\tOpeningAnimationStateCallback__StartOpeningIfPending\tint __fastcall OpeningAnimationStateCallback__StartOpeningIfPending(void * param_1)\tOK\n",
        encoding="utf-8",
    )
    (decompile / "00418090_OpeningAnimationStateCallback__StartOpeningIfPending.c").write_text(
        "OpeningAnimationStateCallback__StartOpeningIfPending s_opening_00623ba4 FindAnimationIndex + 0x254 + 0x25c + 0xf0",
        encoding="utf-8",
    )
    xrefs.write_text(
        XREF_HEADER
        + "00418090\tOpeningAnimationStateCallback__StartOpeningIfPending\t005d9080\t<none>\t<no_function>\tDATA\n",
        encoding="utf-8",
    )
    mixed_table.write_text(
        TABLE_HEADER
        + "8\t005d8fa0\t00418120\tCCockpit__AdvanceOpenCloseAnimationState\tint __fastcall CCockpit__AdvanceOpenCloseAnimationState(void * param_1)\n"
        + "31\t005d907c\t004014c0\tCFrontEndPage__ActiveNotification_NoOp\tvoid __stdcall CFrontEndPage__ActiveNotification_NoOp(void * this, int from_page)\n"
        + "32\t005d9080\t00418090\tOpeningAnimationStateCallback__StartOpeningIfPending\tint __fastcall OpeningAnimationStateCallback__StartOpeningIfPending(void * param_1)\n"
        + "34\t005d9088\t3d23d70a\t<none>\t<none>\n"
        + "35\t005d908c\t39a3d70a\t<none>\t<none>\n"
        + "100\t005d9110\t00418430\tCByteSprite__scalar_deleting_dtor\tundefined CByteSprite__scalar_deleting_dtor(void)\n",
        encoding="utf-8",
    )
    unresolved_types.write_text(
        TYPE_HEADER + "005d9080\t005d907c\t004014c0\t0x900004c2\t-1869574000\t-1869574000\t0x90909090\t0x8564418b\t\t\n",
        encoding="utf-8",
    )
    cockpit_types.write_text(
        TYPE_HEADER
        + "005d94ac\t005d94a8\t0060d008\t0x00000000\t8\t0\t0x00622fe8\t0x0060d038\t.?AVCCockpit@@\tCCockpit\n"
        + "005d9524\t005d9520\t0060d048\t0x00000000\t0\t0\t0x00622fe8\t0x0060d038\t.?AVCCockpit@@\tCCockpit\n",
        encoding="utf-8",
    )
    cockpit_ptr = "00418090" if include_target_in_ccockpit_table else "00424710"
    cockpit_ptr_name = "OpeningAnimationStateCallback__StartOpeningIfPending" if include_target_in_ccockpit_table else "CCockpit__VFunc_01_00424710"
    cockpit_table_a.write_text(
        TABLE_HEADER + f"31\t005d9528\t{cockpit_ptr}\t{cockpit_ptr_name}\t<none>\n",
        encoding="utf-8",
    )
    cockpit_table_b.write_text(
        TABLE_HEADER + "1\t005d9528\t00424710\tCCockpit__VFunc_01_00424710\t<none>\n",
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
        "mixed_table": mixed_table,
        "unresolved_types": unresolved_types,
        "cockpit_types": cockpit_types,
        "cockpit_table_a": cockpit_table_a,
        "cockpit_table_b": cockpit_table_b,
    }


class OpeningAnimationCallbackRenameProbeTests(unittest.TestCase):
    def test_passes_for_conservative_semantic_rename(self) -> None:
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
                mixed_table_path=paths["mixed_table"],
                unresolved_type_names_path=paths["unresolved_types"],
                cockpit_type_names_path=paths["cockpit_types"],
                cockpit_table_a_path=paths["cockpit_table_a"],
                cockpit_table_b_path=paths["cockpit_table_b"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["target"]["name"], "OpeningAnimationStateCallback__StartOpeningIfPending")
        self.assertTrue(report["tableContext"]["mixedSlotPresent"])
        self.assertTrue(report["cockpitBoundary"]["resolvedCockpitTypesPresent"])
        self.assertTrue(report["cockpitBoundary"]["targetAbsentFromResolvedCockpitTables"])

    def test_fails_if_comment_claims_owner_or_cockpit_table_contains_target(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), overclaim_owner=True, include_target_in_ccockpit_table=True)
            report = probe.build_report(
                rename_dry_log_path=paths["rename_dry"],
                rename_apply_log_path=paths["rename_apply"],
                comments_dry_log_path=paths["comments_dry"],
                comments_apply_log_path=paths["comments_apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                mixed_table_path=paths["mixed_table"],
                unresolved_type_names_path=paths["unresolved_types"],
                cockpit_type_names_path=paths["cockpit_types"],
                cockpit_table_a_path=paths["cockpit_table_a"],
                cockpit_table_b_path=paths["cockpit_table_b"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("owner boundary" in failure for failure in report["failures"]))
        self.assertTrue(any("CCockpit table" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
