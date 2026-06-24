#!/usr/bin/env python3
"""Tests for the Wave387 geometry/collision Ghidra probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_geometry_collision_wave387_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
TAGS_HEADER = "address\tname\ttags\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def write_fixture(root: Path, *, stale: bool = False) -> dict[str, Path]:
    decompile_dir = root / "decompile_after"
    decompile_dir.mkdir(parents=True)
    dry = root / "geometry_collision_wave387_dry.log"
    apply = root / "geometry_collision_wave387_apply.log"
    metadata = root / "metadata_after.tsv"
    tags = root / "tags_after.tsv"
    xrefs = root / "xrefs_after.tsv"
    instructions = root / "instructions_after.tsv"

    dry.write_text("SUMMARY: updated=0 skipped=4 missing=0 bad=0\n", encoding="utf-8")
    apply.write_text(
        "OK: 0x00479020 CMeshCollisionVolume__IsDirectionInsideTrianglePrism -> int __cdecl CMeshCollisionVolume__IsDirectionInsideTrianglePrism(void * vertex0, void * vertex1, void * vertex2, void * vertex3, void * direction)\n"
        "SUMMARY: updated=4 skipped=0 missing=0 bad=0\n"
        "REPORT: Save succeeded\n",
        encoding="utf-8",
    )

    metadata_lines: list[str] = []
    tag_lines: list[str] = []
    xref_lines: list[str] = []
    instruction_lines: list[str] = []

    for address, expected in probe.TARGETS.items():
        name = str(expected["name"])
        signature = str(expected["signature"])
        comment = " ".join(str(token) for token in expected["commentTokens"])
        if stale and address == "0x00479770":
            signature = "double __cdecl Geometry__DistanceOutsideAabb(void * param_1, void * param_2)"
            comment += " runtime collision behavior proven"
        metadata_lines.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")

        target_tags = list(expected["tags"])
        if stale and address == "0x00479200":
            target_tags = [tag for tag in target_tags if tag != "closest-point"]
        tag_lines.append(f"{address}\t{name}\t{';'.join(target_tags)}\tOK\n")

        decompile_text = "\n".join(str(token) for token in expected["decompileTokens"])
        (decompile_dir / f"{address[2:]}_{name}.c").write_text(decompile_text, encoding="utf-8")

        caller = str(expected["caller"])
        if stale and address == "0x00479630":
            caller = "WrongCaller"
        xref_lines.append(f"{address}\t{name}\t0x00600000\t0x00478510\t{caller}\tUNCONDITIONAL_CALL\n")

    instruction_source = probe.INSTRUCTION_EVIDENCE
    if stale:
        instruction_source = instruction_source[:-1]
    for target, instruction, mnemonic, operands, bytes_ in instruction_source:
        instruction_lines.append(
            f"{target}\t{target}\tTARGET\t0\t{instruction}\t{target}\t{probe.TARGETS[target]['name']}\t"
            f"{mnemonic}\t{operands}\t{bytes_}\tFALL_THROUGH\n"
        )

    metadata.write_text(METADATA_HEADER + "".join(metadata_lines), encoding="utf-8")
    tags.write_text(TAGS_HEADER + "".join(tag_lines), encoding="utf-8")
    xrefs.write_text(XREF_HEADER + "".join(xref_lines), encoding="utf-8")
    instructions.write_text(INSTRUCTION_HEADER + "".join(instruction_lines), encoding="utf-8")

    return {
        "dry_log_path": dry,
        "apply_log_path": apply,
        "metadata_path": metadata,
        "decompile_dir": decompile_dir,
        "xrefs_path": xrefs,
        "instructions_path": instructions,
        "tags_path": tags,
    }


class GeometryCollisionWave387ProbeTests(unittest.TestCase):
    def test_passes_for_expected_wave387_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**write_fixture(Path(tmp)))
        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["targetCount"], 4)
        self.assertEqual(report["instructionEvidenceHits"], len(probe.INSTRUCTION_EVIDENCE))

    def test_fails_for_stale_signature_missing_tag_bad_caller_and_instruction_gap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**write_fixture(Path(tmp), stale=True))
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("signature mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("comment overclaim" in failure for failure in report["failures"]))
        self.assertTrue(any("missing tag" in failure for failure in report["failures"]))
        self.assertTrue(any("caller mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("missing instruction evidence" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
