#!/usr/bin/env python3
"""Tests for the CAtmospheric signature-hardening tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_atmospheric_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"


def write_fixture(root: Path, *, stale_signature: bool = False, overclaim: bool = False) -> dict[str, Path]:
    signature_dry = root / "signature_dry.log"
    signature_apply = root / "signature_apply.log"
    comments_dry = root / "comments_dry.log"
    comments_apply = root / "comments_apply.log"
    metadata = root / "metadata_readback.tsv"
    decompile = root / "decompile_readback"
    xrefs = root / "xrefs.tsv"
    decompile.mkdir()

    signature_dry.write_text(
        "Mode: dry\n"
        "DRY: 0x004046d0 CAtmospheric__Constructor -> void * __thiscall CAtmospheric__Constructor(void * this, float param_1)\n"
        "DRY: 0x00404920 CAtmospheric__Link -> void __fastcall CAtmospheric__Link(void * this)\n"
        "DRY: 0x00404960 CAtmospheric__Unlink -> void __fastcall CAtmospheric__Unlink(void * this)\n"
        "--- SUMMARY ---\nupdated=0 skipped=3 missing=0 bad=0\n",
        encoding="utf-8",
    )
    signature_apply.write_text(
        "Mode: apply\n"
        "OK: 0x004046d0 CAtmospheric__Constructor -> void * __thiscall CAtmospheric__Constructor(void * this, float param_1)\n"
        "OK: 0x00404920 CAtmospheric__Link -> void __fastcall CAtmospheric__Link(void * this)\n"
        "OK: 0x00404960 CAtmospheric__Unlink -> void __fastcall CAtmospheric__Unlink(void * this)\n"
        "--- SUMMARY ---\nupdated=3 skipped=0 missing=0 bad=0\n",
        encoding="utf-8",
    )
    comments_dry.write_text("--- SUMMARY ---\napplied=0 skipped=3 missing=0 bad=0\n", encoding="utf-8")
    comments_apply.write_text("--- SUMMARY ---\napplied=3 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    comments = {
        "0x004046d0": "Signature hardening for CAtmospheric constructor. Decompile evidence: returns object pointer, stores float param_1, schedules event. Type layout, exact source identity, and runtime behavior remain unproven.",
        "0x00404920": "Signature hardening for CAtmospheric link helper. Decompile evidence: object pointer parameter, tail insertion into global atmospheric list. Type layout, exact source identity, and runtime behavior remain unproven.",
        "0x00404960": "Signature hardening for CAtmospheric unlink helper. Decompile evidence: object pointer parameter, removal from global atmospheric list. Type layout, exact source identity, and runtime behavior remain unproven.",
    }
    if overclaim:
        comments["0x00404920"] = comments["0x00404920"].replace(
            "runtime behavior remain unproven", "runtime behavior proven"
        )

    signatures = {
        "0x004046d0": "void * __thiscall CAtmospheric__Constructor(void * this, float param_1)",
        "0x00404920": "void __fastcall CAtmospheric__Link(void * this)",
        "0x00404960": "void __fastcall CAtmospheric__Unlink(void * this)",
    }
    if stale_signature:
        signatures["0x004046d0"] = "undefined CAtmospheric__Constructor(void)"

    names = {
        "0x004046d0": "CAtmospheric__Constructor",
        "0x00404920": "CAtmospheric__Link",
        "0x00404960": "CAtmospheric__Unlink",
    }

    metadata.write_text(
        METADATA_HEADER
        + "".join(f"{addr}\t{names[addr]}\t{signatures[addr]}\t{comments[addr]}\tOK\n" for addr in names),
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        INDEX_HEADER + "".join(f"{addr}\t{names[addr]}\t{signatures[addr]}\tOK\n" for addr in names),
        encoding="utf-8",
    )
    for addr, name in names.items():
        (decompile / f"{addr[2:]}_{name}.c").write_text(
            f"{name} {signatures[addr]} global atmospheric list object pointer param_2",
            encoding="utf-8",
        )
    xrefs.write_text(
        XREF_HEADER
        + "".join(f"{addr[2:]}\t{names[addr]}\t00401000\t00401000\tCaller\tUNCONDITIONAL_CALL\n" for addr in names),
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
    }


class AtmosphericSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_hardened_signatures_with_caveats(self) -> None:
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
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["signatureHardenedTargets"], 3)
        self.assertEqual(report["summary"]["staleUndefinedSignatures"], 0)
        self.assertEqual(report["summary"]["supersededTargets"], 1)

    def test_fails_for_stale_signature_or_runtime_overclaim(self) -> None:
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
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("stale undefined signature" in failure for failure in report["failures"]))
        self.assertTrue(any("runtime/source overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
