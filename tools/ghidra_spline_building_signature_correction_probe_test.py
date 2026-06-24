#!/usr/bin/env python3
"""Tests for the CBSpline/Building Ghidra signature correction proof parser."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_spline_building_signature_correction_probe as probe


HEADER = "address\tname\tsignature\tcomment\tstatus\n"


def metadata_text(stale: bool = False) -> str:
    rows = []
    for address, target in probe.TARGETS.items():
        name = target["name"]
        signature = " ".join(str(token) for token in target["signature"])
        if stale and address == "0x004176c0":
            signature = "void __thiscall CThing__InitRenderThingFromInitMeshName(void * this, int param_1, int param_2)"
        comment = " ".join(str(token) for token in target["comment"])
        rows.append(f"{address}\t{name}\t{signature}\t{comment}\tOK")
    return HEADER + "\n".join(rows) + "\n"


def index_text() -> str:
    lines = ["address\tname\tsignature\tstatus"]
    for address, target in probe.TARGETS.items():
        lines.append(f"{address}\t{target['name']}\t{' '.join(str(token) for token in target['signature'])}\tOK")
    return "\n".join(lines) + "\n"


def write_fixture(root: Path, stale: bool = False) -> dict[str, Path]:
    decompile_dir = root / "decompile"
    decompile_dir.mkdir()
    (root / "dry.log").write_text("updated=0 skipped=9 renamed=0 missing=0 bad=0\n", encoding="utf-8")
    (root / "apply.log").write_text("updated=9 skipped=0 renamed=4 missing=0 bad=0\n", encoding="utf-8")
    (root / "metadata.tsv").write_text(metadata_text(stale=stale), encoding="utf-8")
    (decompile_dir / "index.tsv").write_text(index_text(), encoding="utf-8")
    (root / "xrefs.tsv").write_text(
        "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
        + "\n".join(f"{address[2:]}\t{target['name']}\t00400000\t00400000\tcaller\tUNCONDITIONAL_CALL" for address, target in probe.TARGETS.items())
        + "\n",
        encoding="utf-8",
    )
    (root / "instructions.tsv").write_text(
        "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
        + "\n".join(f"{address}\t{address}\tTARGET\t0\t{address}\t{address}\t{target['name']}\tRET\t0x4\tc2 04 00\tTERMINATOR" for address, target in probe.TARGETS.items())
        + "\n",
        encoding="utf-8",
    )
    for address, target in probe.TARGETS.items():
        body = " ".join(str(token) for token in target["decompile"])
        (decompile_dir / f"{address[2:]}_{target['name']}.c").write_text(body, encoding="utf-8")
    return {
        "dry_log_path": root / "dry.log",
        "apply_log_path": root / "apply.log",
        "metadata_path": root / "metadata.tsv",
        "decompile_index_path": decompile_dir / "index.tsv",
        "decompile_dir": decompile_dir,
        "xrefs_path": root / "xrefs.tsv",
        "instructions_path": root / "instructions.tsv",
    }


class SplineBuildingSignatureCorrectionProbeTests(unittest.TestCase):
    def test_passes_for_corrected_tranche(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["targets"], 9)
        self.assertEqual(report["renamed"], 4)

    def test_fails_for_stale_param_signature(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale=True)
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "FAIL")
        self.assertGreater(report["staleParamSignatureHits"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
