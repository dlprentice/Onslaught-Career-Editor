#!/usr/bin/env python3
"""Tests for the CMCMech/CRadar signature-hardening tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_mech_radar_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


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
        "Mode: dry\n"
        "DRY: 0x00405a10 CMCMech__Destructor -> void __fastcall CMCMech__Destructor(void * this)\n"
        "DRY: 0x00405a20 CRadarWarningReceiver__scalar_deleting_dtor -> void * __thiscall CRadarWarningReceiver__scalar_deleting_dtor(void * this, byte flags)\n"
        "--- SUMMARY ---\nupdated=0 skipped=2 missing=0 bad=0\n",
        encoding="utf-8",
    )
    signature_apply.write_text(
        "Mode: apply\n"
        "OK: 0x00405a10 CMCMech__Destructor -> void __fastcall CMCMech__Destructor(void * this)\n"
        "OK: 0x00405a20 CRadarWarningReceiver__scalar_deleting_dtor -> void * __thiscall CRadarWarningReceiver__scalar_deleting_dtor(void * this, byte flags)\n"
        "--- SUMMARY ---\nupdated=2 skipped=0 missing=0 bad=0\n",
        encoding="utf-8",
    )
    comments_dry.write_text("--- SUMMARY ---\napplied=0 skipped=2 missing=0 bad=0\n", encoding="utf-8")
    comments_apply.write_text("--- SUMMARY ---\napplied=2 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    comments = {
        "0x00405a10": "Signature hardening for CMCMech destructor thunk. Decompile evidence: retail entry jumps to the destructor body, which resets vtable state, unlinks from the global mech list, frees mesh/resource arrays, and calls the motion-controller base cleanup. Concrete class layout, exact source identity, and runtime behavior remain unproven.",
        "0x00405a20": "Signature hardening for CRadarWarningReceiver scalar deleting destructor. Decompile evidence: ECX object pointer, byte deletion flag, underlying destructor call, optional CDXMemoryManager__Free, and this-pointer return. Concrete class layout, exact source identity, and runtime behavior remain unproven.",
    }
    if overclaim:
        comments["0x00405a20"] = comments["0x00405a20"].replace(
            "runtime behavior remain unproven", "runtime behavior proven"
        )

    signatures = {
        "0x00405a10": "void __fastcall CMCMech__Destructor(void * this)",
        "0x00405a20": "void * __thiscall CRadarWarningReceiver__scalar_deleting_dtor(void * this, byte flags)",
    }
    if stale_signature:
        signatures["0x00405a10"] = "undefined CMCMech__Destructor(void)"

    names = {
        "0x00405a10": "CMCMech__Destructor",
        "0x00405a20": "CRadarWarningReceiver__scalar_deleting_dtor",
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
            f"{name} {signatures[addr]} CDXMemoryManager__Free global mech list destructor",
            encoding="utf-8",
        )
    xrefs.write_text(
        XREF_HEADER
        + "00405a10\tCMCMech__Destructor\t00479b43\t00479b40\tVFuncSlot_01_00479b40\tUNCONDITIONAL_CALL\n"
        + "00405a20\tCRadarWarningReceiver__scalar_deleting_dtor\t005d8814\t<none>\t<no_function>\tDATA\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x00405a10\t0x00405a10\tTARGET\t0\t0x00405a10\t0x00405a10\tCMCMech__Destructor\tJMP\t0x00498530\te9 1b 2b 09 00\tUNCONDITIONAL_JUMP\n"
        + "0x00405a20\t0x00405a20\tTARGET\t0\t0x00405a20\t0x00405a20\tCRadarWarningReceiver__scalar_deleting_dtor\tPUSH\tESI\t56\tFALL_THROUGH\n"
        + "0x00405a20\t0x00405a20\tAFTER\t10\t0x00405a3d\t0x00405a20\tCRadarWarningReceiver__scalar_deleting_dtor\tRET\t0x4\tc2 04 00\tTERMINATOR\n",
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


class MechRadarSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_hardened_signatures_with_boundaries(self) -> None:
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
        self.assertEqual(report["summary"]["signatureHardenedTargets"], 2)
        self.assertEqual(report["summary"]["staleUndefinedSignatures"], 0)

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
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("stale undefined signature" in failure for failure in report["failures"]))
        self.assertTrue(any("runtime/source overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
