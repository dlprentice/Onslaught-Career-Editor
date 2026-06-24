#!/usr/bin/env python3
"""Tests for the Wave469 vector helper metadata probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_vector_tail_wave469_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
TAGS_HEADER = "address\tname\ttags\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def write_fixture(root: Path, stale: bool = False) -> None:
    (root / "post-decomp").mkdir(parents=True)
    (root / "dry.log").write_text(
        "SUMMARY updated=0 skipped=2 created=0 would_create=0 renamed=0 would_rename=1 missing=0 bad=0\n"
        "REPORT: Save succeeded\n",
        encoding="utf-8",
    )
    (root / "apply.log").write_text(
        "SUMMARY updated=2 skipped=0 created=0 would_create=0 renamed=1 would_rename=0 missing=0 bad=0\n"
        "REPORT: Save succeeded\n",
        encoding="utf-8",
    )
    (root / "verify_dry.log").write_text(
        "SUMMARY updated=0 skipped=2 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0\n"
        "REPORT: Save succeeded\n",
        encoding="utf-8",
    )

    metadata_rows = []
    tag_rows = []
    xref_rows = []
    instruction_rows = []
    for address, expected in probe.TARGETS.items():
        name = str(expected["name"])
        signature = str(expected["signature"])
        comment = " ".join(str(token) for token in expected["commentTokens"])
        tags = ";".join(str(tag) for tag in expected["tags"])
        decompile = "\n".join(str(token) for token in expected["decompileTokens"])
        if stale and address == "0x004c7900":
            name = "CRocket__NormalizeVec3InPlace"
            comment += " runtime behavior proven"
            tags = tags.replace("owner-corrected", "")
            decompile = "missing expected normalize tokens"
        metadata_rows.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        tag_rows.append(f"{address}\t{name}\t{tags}\tOK\n")
        (root / "post-decomp" / f"{address[2:]}_{name}.c").write_text(decompile, encoding="utf-8")

    for target, from_addr, from_function in probe.EXPECTED_XREF_EDGES:
        if stale and target == "0x004c7d90" and from_function == "CDXImposter__BuildQuadGeometry":
            continue
        xref_rows.append(f"{target}\t{probe.TARGETS[target]['name']}\t{from_addr}\t0x00400000\t{from_function}\tUNCONDITIONAL_CALL\n")

    instructions = list(probe.EXPECTED_INSTRUCTIONS)
    if stale:
        instructions = instructions[:-1]
    for target, instruction_addr, mnemonic, operands, bytes_ in instructions:
        instruction_rows.append(
            f"{target}\t{target}\tTARGET\t0\t{instruction_addr}\t{target}\t{probe.TARGETS[target]['name']}\t"
            f"{mnemonic}\t{operands}\t{bytes_}\tFALL_THROUGH\n"
        )

    (root / "post_metadata.tsv").write_text(METADATA_HEADER + "".join(metadata_rows), encoding="utf-8")
    (root / "post_tags.tsv").write_text(TAGS_HEADER + "".join(tag_rows), encoding="utf-8")
    (root / "post_xrefs.tsv").write_text(XREF_HEADER + "".join(xref_rows), encoding="utf-8")
    (root / "post_instructions.tsv").write_text(INSTRUCTION_HEADER + "".join(instruction_rows), encoding="utf-8")


class VectorTailWave469ProbeTests(unittest.TestCase):
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
        self.assertTrue(any("expected name" in failure for failure in failures))
        self.assertTrue(any("overclaim" in failure for failure in failures))
        self.assertTrue(any("missing tag" in failure for failure in failures))
        self.assertTrue(any("missing xref edge" in failure for failure in failures))
        self.assertTrue(any("missing instruction evidence" in failure for failure in failures))


if __name__ == "__main__":
    unittest.main(verbosity=2)
