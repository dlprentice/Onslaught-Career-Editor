#!/usr/bin/env python3
"""Tests for the CBSpline/CByteSprite signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_spline_bytesprite_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


TARGETS = {
    "0x00405d80": (
        "CParticleManager__RemoveFromGlobalList",
        "undefined CParticleManager__RemoveFromGlobalList(void)",
        "Deferral note for CParticleManager thunk. Instruction evidence shows a jump thunk to 0x004cb050; exact thunk/target signature, source identity, and runtime behavior remain unproven.",
    ),
    "0x00416d10": (
        "CBSpline__ctor",
        "void * __thiscall CBSpline__ctor(void * this, void * controlPoints, int order)",
        "Signature hardening for CBSpline constructor. Decompile evidence stores control points and order, sets the CBSpline vtable, allocates the knot vector, and initializes clamped knots. Concrete class layout and runtime behavior remain unproven.",
    ),
    "0x00416da0": (
        "CBSpline__dtor",
        "void * __thiscall CBSpline__dtor(void * this, byte flags)",
        "Signature hardening for CBSpline destructor/deleting-destructor shape. Decompile evidence frees the knot vector, frees linked control points, clears the set, optionally frees this, and returns this. Exact source identity and runtime behavior remain unproven.",
    ),
    "0x004183d0": (
        "CByteSprite__dtor_base",
        "undefined CByteSprite__dtor_base(void)",
        "Deferral note for CByteSprite__dtor_base. Current body resets vtable-like fields and calls the actor base cleanup/constructor-like helper; current name and exact source identity remain unresolved.",
    ),
    "0x00418430": (
        "CByteSprite__scalar_deleting_dtor",
        "void * __thiscall CByteSprite__scalar_deleting_dtor(void * this, byte flags)",
        "Signature hardening for CByteSprite scalar deleting destructor. Decompile evidence calls CByteSprite__dtor_base, conditionally frees this when flags bit 0 is set, and returns this. Runtime behavior remain unproven.",
    ),
    "0x00418480": (
        "CByteSprite__Free",
        "void __fastcall CByteSprite__Free(void * this)",
        "Signature hardening for CByteSprite free helper. Decompile evidence frees sprite data and frame-offset storage when present and clears both fields. Runtime behavior remain unproven.",
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

    signature_dry.write_text(
        "--- SUMMARY ---\nupdated=0 skipped=4 missing=0 bad=0\n",
        encoding="utf-8",
    )
    signature_apply.write_text(
        "--- SUMMARY ---\nupdated=4 skipped=0 missing=0 bad=0\n",
        encoding="utf-8",
    )
    comments_dry.write_text("--- SUMMARY ---\napplied=0 skipped=6 missing=0 bad=0\n", encoding="utf-8")
    comments_apply.write_text("--- SUMMARY ---\napplied=6 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    rows = []
    index_rows = []
    for address, (name, signature, comment) in TARGETS.items():
        if stale_signature and address == "0x00416d10":
            signature = "undefined CBSpline__ctor(void)"
        if overclaim and address == "0x00418430":
            comment = comment.replace("Runtime behavior remain unproven", "Runtime behavior proven")
        rows.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        index_rows.append(f"{address}\t{name}\t{signature}\tOK\n")
        (decompile / f"{address[2:]}_{name}.c").write_text(
            f"{name} {signature} OID__AllocObject OID__FreeObject "
            "CActor__ctor_like_004013d0 CByteSprite__dtor_base knot vector byte flags jump thunk sprite data",
            encoding="utf-8",
        )

    metadata.write_text(METADATA_HEADER + "".join(rows), encoding="utf-8")
    (decompile / "index.tsv").write_text(INDEX_HEADER + "".join(index_rows), encoding="utf-8")
    xrefs.write_text(
        XREF_HEADER
        + "".join(
            f"{address}\t{name}\t00400000\t00400000\tCaller_{name}\tUNCONDITIONAL_CALL\n"
            for address, (name, _, _) in TARGETS.items()
        ),
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x00405d80\t0x00405d80\tTARGET\t0\t0x00405d80\t0x00405d80\tCParticleManager__RemoveFromGlobalList\tJMP\t0x004cb050\te9 cb 52 0c 00\tUNCONDITIONAL_JUMP\n"
        + "0x00416d10\t0x00416d10\tTARGET\t0\t0x00416d10\t0x00416d10\tCBSpline__ctor\tCALL\t0x005490e0\te8 00 00 00 00\tUNCONDITIONAL_CALL\n"
        + "0x00416da0\t0x00416da0\tTARGET\t0\t0x00416da0\t0x00416da0\tCBSpline__dtor\tCALL\t0x00549220\te8 00 00 00 00\tUNCONDITIONAL_CALL\n"
        + "0x004183d0\t0x004183d0\tTARGET\t0\t0x004183d0\t0x004183d0\tCByteSprite__dtor_base\tJMP\t0x004013d0\te9 00 00 00 00\tCALL_TERMINATOR\n"
        + "0x00418430\t0x00418430\tTARGET\t0\t0x00418430\t0x00418430\tCByteSprite__scalar_deleting_dtor\tCALL\t0x004183d0\te8 00 00 00 00\tUNCONDITIONAL_CALL\n"
        + "0x00418430\t0x00418430\tAFTER\t1\t0x00418445\t0x00418430\tCByteSprite__scalar_deleting_dtor\tCALL\t0x00549220\te8 00 00 00 00\tUNCONDITIONAL_CALL\n"
        + "0x00418480\t0x00418480\tTARGET\t0\t0x00418480\t0x00418480\tCByteSprite__Free\tCALL\t0x00549220\te8 00 00 00 00\tUNCONDITIONAL_CALL\n",
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


class SplineByteSpriteSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_hardened_signatures_and_deferred_boundaries(self) -> None:
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
        self.assertEqual(report["summary"]["signatureHardenedTargets"], 4)
        self.assertEqual(report["summary"]["deferredTargets"], 2)

    def test_fails_for_stale_hardened_signature_or_public_overclaim(self) -> None:
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
        self.assertTrue(any("stale undefined signature" in failure for failure in report["failures"]))
        self.assertTrue(any("runtime/source overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
