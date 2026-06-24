#!/usr/bin/env python3
"""Tests for the WalkerPart/Monitor/GeneralVolume dash-surface correction probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_walker_dash_surface_signature_correction_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def signature_for(target: dict[str, object]) -> str:
    return " ".join(str(token) for token in target["signature"])


def write_fixture(root: Path, *, stale_param: bool = False, overclaim: bool = False) -> dict[str, Path]:
    correction_dry = root / "correction_dry.log"
    correction_apply = root / "correction_apply.log"
    metadata = root / "metadata_final.tsv"
    decompile = root / "decompile_final"
    xrefs = root / "xrefs_final.tsv"
    instructions = root / "instructions_final.tsv"
    decompile.mkdir()

    target_count = len(probe.TARGETS)
    renamed_count = sum(1 for target in probe.TARGETS.values() if target.get("renamedByCorrection"))
    correction_dry.write_text(f"--- SUMMARY ---\nupdated=0 skipped={target_count} renamed=0 missing=0 bad=0\n", encoding="utf-8")
    correction_apply.write_text(
        f"--- SUMMARY ---\nupdated={target_count} skipped=0 renamed={renamed_count} missing=0 bad=0\n",
        encoding="utf-8",
    )

    metadata_rows = []
    index_rows = []
    xref_rows = [XREF_HEADER]
    instruction_rows = [INSTRUCTION_HEADER]
    for index, (address, target) in enumerate(probe.TARGETS.items()):
        signature = signature_for(target)
        if stale_param and address == "0x00412d80":
            signature = "void __thiscall CBattleEngineWalkerPart__Forward(void * this, int param_1, float param_2)"
        comment = " ".join(str(token) for token in target["comment"])
        if overclaim and address == "0x00413b90":
            comment += " runtime behavior proven"
        metadata_rows.append(f"{address}\t{target['name']}\t{signature}\t{comment}\tOK\n")
        index_rows.append(f"{address}\t{target['name']}\t{signature}\tOK\n")
        (decompile / f"{address[2:]}_{target['name']}.c").write_text(
            f"{target['name']} {signature} " + " ".join(str(token) for token in target["decompile"]),
            encoding="utf-8",
        )
        for xref in target["xrefs"]:
            xref_rows.append(
                f"{address[2:]}\t{target['name']}\t0040{index:04x}\t0040{index:04x}\t{xref}\tUNCONDITIONAL_CALL\n"
            )
        ret = str(target.get("ret", ""))
        if ret:
            instruction_rows.append(
                f"{address}\t{address}\tAFTER\t{index}\t{address}\t{address}\t{target['name']}\tRET\t{ret}\tc2 04 00\tTERMINATOR\n"
            )

    metadata.write_text(METADATA_HEADER + "".join(metadata_rows), encoding="utf-8")
    (decompile / "index.tsv").write_text(INDEX_HEADER + "".join(index_rows), encoding="utf-8")
    xrefs.write_text("".join(xref_rows), encoding="utf-8")
    instructions.write_text("".join(instruction_rows), encoding="utf-8")
    return {
        "correction_dry": correction_dry,
        "correction_apply": correction_apply,
        "metadata": metadata,
        "decompile_index": decompile / "index.tsv",
        "decompile_dir": decompile,
        "xrefs": xrefs,
        "instructions": instructions,
    }


class WalkerDashSurfaceCorrectionProbeTests(unittest.TestCase):
    def test_passes_for_corrected_tranche(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                correction_dry_log_path=paths["correction_dry"],
                correction_apply_log_path=paths["correction_apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )
        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], len(probe.TARGETS))
        self.assertEqual(report["summary"]["staleNameHits"], 0)
        self.assertEqual(report["summary"]["paramSignatureHits"], 0)
        self.assertEqual(report["summary"]["commentOverclaims"], 0)

    def test_fails_for_stale_signature_or_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale_param=True, overclaim=True)
            report = probe.build_report(
                correction_dry_log_path=paths["correction_dry"],
                correction_apply_log_path=paths["correction_apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("forbidden signature token" in failure for failure in report["failures"]))
        self.assertTrue(any("overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
