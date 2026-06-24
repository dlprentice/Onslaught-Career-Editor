#!/usr/bin/env python3
"""Tests for the Wave471 CPlayer snapshot metadata probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_cplayer_snapshot_wave471_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
TAGS_HEADER = "address\tname\ttags\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
DISASM_HEADER = "address\tbytes\tmnemonic\toperands\n"


def write_fixture(root: Path, stale: bool = False) -> None:
    (root / "post-decomp").mkdir(parents=True)
    (root / "dry.log").write_text(
        "SUMMARY updated=0 skipped=4 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0\n"
        "REPORT: Save succeeded\n",
        encoding="utf-8",
    )
    (root / "apply.log").write_text(
        "SUMMARY updated=4 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0\n"
        "REPORT: Save succeeded\n",
        encoding="utf-8",
    )
    (root / "verify_dry.log").write_text(
        "SUMMARY updated=0 skipped=4 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0\n"
        "REPORT: Save succeeded\n",
        encoding="utf-8",
    )

    metadata_rows = []
    tag_rows = []
    xref_rows = []
    disasm_rows = []
    for address, expected in probe.TARGETS.items():
        name = str(expected["name"])
        signature = str(expected["signature"])
        comment = " ".join(str(token) for token in expected["commentTokens"])
        tags = ";".join(str(tag) for tag in expected["tags"])
        decompile = "\n".join(str(token) for token in expected["decompileTokens"])
        if stale and address == "0x004d2a70":
            signature = "void __thiscall CPlayer__GetCurrentViewPoint(void * this, int param_1, void * param_2)"
            comment += " runtime camera behavior proven"
            tags = tags.replace("snapshot", "")
            decompile = "missing expected output tokens"
        metadata_rows.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        tag_rows.append(f"{address}\t{name}\t{tags}\tOK\n")
        (root / "post-decomp" / f"{address[2:]}_{name}.c").write_text(decompile, encoding="utf-8")

    for target, from_addr, from_function in probe.EXPECTED_XREF_EDGES:
        if stale and target == "0x004d2b40":
            continue
        xref_rows.append(f"{target}\t{probe.TARGETS[target]['name']}\t{from_addr}\t0x00400000\t{from_function}\tUNCONDITIONAL_CALL\n")

    returns = list(probe.EXPECTED_RETURNS)
    if stale:
        returns = returns[:-1]
    for address, mnemonic, operands, bytes_ in returns:
        disasm_rows.append(f"{address}\t{bytes_}\t{mnemonic}\t{operands}\n")

    (root / "post_metadata.tsv").write_text(METADATA_HEADER + "".join(metadata_rows), encoding="utf-8")
    (root / "post_tags.tsv").write_text(TAGS_HEADER + "".join(tag_rows), encoding="utf-8")
    (root / "post_xrefs.tsv").write_text(XREF_HEADER + "".join(xref_rows), encoding="utf-8")
    (root / "post_disasm_range.tsv").write_text(DISASM_HEADER + "".join(disasm_rows), encoding="utf-8")


class CPlayerSnapshotWave471ProbeTests(unittest.TestCase):
    def test_passes_for_expected_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)
            status, failures = probe.run_checks(root)
        self.assertEqual(status, "PASS", failures)

    def test_fails_for_stale_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root, stale=True)
            status, failures = probe.run_checks(root)
        self.assertEqual(status, "FAIL")
        self.assertTrue(any("expected signature" in failure for failure in failures))
        self.assertTrue(any("overclaim" in failure for failure in failures))
        self.assertTrue(any("missing tag" in failure for failure in failures))
        self.assertTrue(any("missing xref edge" in failure for failure in failures))
        self.assertTrue(any("missing return evidence" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main(verbosity=2)
