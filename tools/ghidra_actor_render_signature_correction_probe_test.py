#!/usr/bin/env python3
"""Tests for the CActor render signature/name correction probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_actor_render_signature_correction_probe as probe


TARGET_ROWS = {
    "0x00401b50": {
        "name": "CActor__GetFractionTime",
        "signature": "float __thiscall CActor__GetFractionTime(void * this)",
        "comment": (
            "CActor::GetFractionTime source-parity correction: calls virtual GetMoveMultiplier (+0x60), "
            "uses EVENT_MANAGER/GAME timing globals and this+0xd8 mLastMoveTime-style field, then clamps "
            "the interpolation fraction. Corrects a prior CMCMine scale-helper label; not a concrete CActor "
            "layout or runtime render proof."
        ),
        "decompile": "CActor__GetFractionTime GetMoveMultiplier this + 0xd8 005d8568 005d856c",
    },
    "0x00401be0": {
        "name": "CActor__GetRenderPos",
        "signature": "void __thiscall CActor__GetRenderPos(void * this, void * outRenderPos)",
        "comment": (
            "CActor::GetRenderPos source-parity correction: writes a hidden-return FVector from old/current "
            "position interpolation using the frame render fraction. Subclass vtable xrefs inherit this base "
            "render-position slot; not a concrete FVector layout or runtime render proof."
        ),
        "decompile": "CActor__GetRenderPos outRenderPos 0x14 0x84 0x18 0x88 0x1c 0x8c",
    },
    "0x00401c50": {
        "name": "CActor__GetRenderOrientation",
        "signature": "void __thiscall CActor__GetRenderOrientation(void * this, void * outRenderOrientation)",
        "comment": (
            "CActor::GetRenderOrientation source-parity correction: writes a hidden-return FMatrix from "
            "old/current orientation interpolation using the GetFractionTime-like clamp path and row-copy "
            "helpers. Subclass vtable xrefs inherit this base render-orientation slot; not a concrete FMatrix "
            "layout or runtime render proof."
        ),
        "decompile": "CActor__GetRenderOrientation outRenderOrientation Vec3__SetXYZ Mat34__SetRows 0x94 0xa4 0xb4",
    },
}


def write_fixture(root: Path, *, stale: bool = False, overclaim: bool = False) -> dict[str, Path]:
    rename_dry = root / "rename_dry.log"
    rename_apply = root / "rename_apply.log"
    signature_dry = root / "signature_dry.log"
    signature_apply = root / "signature_apply.log"
    comments_dry = root / "comments_dry.log"
    comments_apply = root / "comments_apply.log"
    metadata = root / "metadata_final.tsv"
    decompile = root / "decompile_final"
    xrefs = root / "xrefs_final.tsv"
    instructions = root / "instructions_final.tsv"
    decompile.mkdir()

    rename_dry.write_text("--- SUMMARY ---\napplied=0 skipped=3 missing=0 bad=0\n", encoding="utf-8")
    rename_apply.write_text("--- SUMMARY ---\napplied=3 skipped=0 missing=0 bad=0\n", encoding="utf-8")
    signature_dry.write_text("--- SUMMARY ---\nupdated=0 skipped=3 missing=0 bad=0\n", encoding="utf-8")
    signature_apply.write_text("--- SUMMARY ---\nupdated=3 skipped=0 missing=0 bad=0\n", encoding="utf-8")
    comments_dry.write_text("--- SUMMARY ---\napplied=0 skipped=3 missing=0 bad=0\n", encoding="utf-8")
    comments_apply.write_text("--- SUMMARY ---\napplied=3 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    rows = {address: dict(row) for address, row in TARGET_ROWS.items()}
    if stale:
        rows["0x00401b50"]["name"] = "CMCMine__ComputeClampedScaleFactor"
        rows["0x00401be0"]["name"] = "VFuncSlot_00_00401be0"
        rows["0x00401c50"]["signature"] = (
            "void __thiscall VFuncSlot_01_00401c50(void * this, int param_1, void * param_2)"
        )
    if overclaim:
        rows["0x00401c50"]["comment"] += " This proves runtime render behavior."

    metadata.write_text(
        "address\tname\tsignature\tcomment\tstatus\n"
        + "".join(
            f"{address}\t{row['name']}\t{row['signature']}\t{row['comment']}\tOK\n"
            for address, row in rows.items()
        ),
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        "address\tname\tsignature\tstatus\n"
        + "".join(f"{address}\t{row['name']}\t{row['signature']}\tOK\n" for address, row in rows.items()),
        encoding="utf-8",
    )
    for address, row in rows.items():
        text = f"{row['signature']} {row['decompile']}"
        if stale:
            text += " CMCMine__ComputeClampedScaleFactor VFuncSlot_00_00401be0 param_1"
        (decompile / f"{address[2:]}_{row['name']}.c").write_text(text, encoding="utf-8")
    xrefs.write_text(
        "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
        + "".join(f"{address[2:]}\t{row['name']}\t00401000\t00401000\tCaller\tDATA\n" for address, row in rows.items()),
        encoding="utf-8",
    )
    instructions.write_text(
        "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
        + "".join(
            f"{address}\t{address}\tAFTER\t1\t{address}\t{address}\t{row['name']}\tRET\t0x4\t\tTERMINATOR\n"
            for address, row in rows.items()
        ),
        encoding="utf-8",
    )
    return {
        "rename_dry": rename_dry,
        "rename_apply": rename_apply,
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


class ActorRenderSignatureCorrectionProbeTests(unittest.TestCase):
    def test_passes_for_corrected_actor_render_tranche(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                rename_dry_log_path=paths["rename_dry"],
                rename_apply_log_path=paths["rename_apply"],
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
        self.assertEqual(report["summary"]["renamedTargets"], 3)
        self.assertEqual(report["summary"]["signatureHardenedTargets"], 3)
        self.assertEqual(report["summary"]["staleTokenHits"], 0)

    def test_fails_for_stale_names_signatures_or_overclaims(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale=True, overclaim=True)
            report = probe.build_report(
                rename_dry_log_path=paths["rename_dry"],
                rename_apply_log_path=paths["rename_apply"],
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
        self.assertTrue(any("name mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("signature tokens missing" in failure for failure in report["failures"]))
        self.assertTrue(any("stale token" in failure for failure in report["failures"]))
        self.assertTrue(any("overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
