#!/usr/bin/env python3
"""Tests for the cockpit/compass Ghidra signature correction probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_cockpit_compass_signature_correction_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
VTABLE_HEADER = "vtable\tcol_ptr_slot\tcol_addr\tsignature\toffset\tcd_offset\ttype_desc\tclass_desc\traw_type_name\tdemangled_type_name\n"


def write_fixture(root: Path, *, stale_name: bool = False, overclaim: bool = False) -> dict[str, Path]:
    dry = root / "correction_dry.log"
    apply = root / "correction_apply.log"
    metadata = root / "metadata_final.tsv"
    decompile = root / "decompile_final"
    xrefs = root / "xrefs_final.tsv"
    instructions = root / "instructions_final.tsv"
    vtables = root / "vtable_types.tsv"
    decompile.mkdir()

    dry.write_text("--- SUMMARY ---\nupdated=0 skipped=6 missing=0 bad=0\n", encoding="utf-8")
    apply.write_text("--- SUMMARY ---\nupdated=6 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    names = {
        "0x00405970": "CDXCockpit__scalar_deleting_dtor",
        "0x00405990": "CDXCockpit__dtor_base_thunk",
        "0x00406040": "CDXCompass__GetTrackedPositionX",
        "0x0040c630": "CDXCompass__GetTrackedPositionY",
        "0x00424710": "CCockpit__scalar_deleting_dtor",
        "0x00424730": "CCockpit__dtor_base",
    }
    if stale_name:
        names["0x00405970"] = "CDXCockpit__VFunc_01_00405970"

    signatures = {
        "0x00405970": "void * __thiscall CDXCockpit__scalar_deleting_dtor(void * this, byte flags)",
        "0x00405990": "void __fastcall CDXCockpit__dtor_base_thunk(void * this)",
        "0x00406040": "double __fastcall CDXCompass__GetTrackedPositionX(void * context)",
        "0x0040c630": "double __fastcall CDXCompass__GetTrackedPositionY(void * context)",
        "0x00424710": "void * __thiscall CCockpit__scalar_deleting_dtor(void * this, byte flags)",
        "0x00424730": "void __fastcall CCockpit__dtor_base(void * this)",
    }

    comments = {
        addr: "Signature correction with proof boundary. Exact source identity, concrete layout, tags, locals, and runtime behavior remain unproven."
        for addr in names
    }
    comments["0x00405970"] += " This is a scalar-deleting destructor that calls CDXCockpit__dtor_base_thunk and optionally calls OID__FreeObject."
    comments["0x00405990"] += " This is a jump thunk to CCockpit__dtor_base."
    comments["0x00406040"] += " Reads tracked pointer +0x4b0 and X field +0x1c; return precision remain unproven."
    comments["0x0040c630"] += " Reads tracked pointer +0x4b0 and Y field +0x20; return precision remain unproven."
    comments["0x00424710"] += " This is a scalar-deleting destructor that calls CCockpit__dtor_base and optionally calls OID__FreeObject."
    comments["0x00424730"] += " Resets CCockpit vtable slots 0x005d9524 and 0x005d94ac, then calls CMonitor__Shutdown."
    if overclaim:
        comments["0x00406040"] += " Runtime behavior proven."

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
        evidence_tokens = {
            "0x00405970": "CDXCockpit__dtor_base_thunk OID__FreeObject return this",
            "0x00405990": "CCockpit__dtor_base",
            "0x00406040": "0x4b0 0x1c",
            "0x0040c630": "0x4b0 0x20",
            "0x00424710": "CCockpit__dtor_base OID__FreeObject return this",
            "0x00424730": "PTR_LAB_005d9524 PTR_LAB_005d94ac CMonitor__Shutdown",
        }[addr]
        (decompile / f"{addr[2:]}_{name}.c").write_text(
            f"{name} {signatures[addr]} {evidence_tokens}",
            encoding="utf-8",
        )
    xrefs.write_text(
        XREF_HEADER
        + "".join(f"{addr[2:]}\t{names[addr]}\t00401000\t00401000\tCaller\tUNCONDITIONAL_CALL\n" for addr in names),
        encoding="utf-8",
    )
    instructions.write_text(
        "target_addr\tinstruction_addr\tfunction_name\tmnemonic\toperands\n"
        "0x00405970\t0x0040598d\tCDXCockpit__scalar_deleting_dtor\tRET\t0x4\n"
        "0x00424710\t0x0042472d\tCCockpit__scalar_deleting_dtor\tRET\t0x4\n",
        encoding="utf-8",
    )
    vtables.write_text(
        VTABLE_HEADER
        + "005d88b0\t005d88ac\t0060c628\t0x00000000\t0\t0\t0x00623000\t0x0060c618\t.?AVCDXCockpit@@\tCDXCockpit\n"
        "005d9524\t005d9520\t0060d048\t0x00000000\t0\t0\t0x00622fe8\t0x0060d038\t.?AVCCockpit@@\tCCockpit\n",
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


class CockpitCompassSignatureCorrectionProbeTests(unittest.TestCase):
    def test_passes_for_corrected_cockpit_compass_targets(self) -> None:
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
        self.assertEqual(report["summary"]["staleNameHits"], 0)
        self.assertEqual(report["summary"]["paramSignatureHits"], 0)

    def test_fails_for_stale_name_or_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale_name=True, overclaim=True)
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
        self.assertTrue(any("name/status mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("runtime/source overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
