#!/usr/bin/env python3
"""Tests for the Wave386 diagnostic/fatal/console Ghidra probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_diagnostic_console_wave386_probe as probe


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
    dry = root / "diagnostic_console_wave386_dry.log"
    apply = root / "diagnostic_console_wave386_apply.log"
    metadata = root / "metadata_after.tsv"
    tags = root / "tags_after.tsv"
    xrefs = root / "xrefs_after.tsv"
    instructions = root / "instructions_after.tsv"

    dry.write_text(
        "SUMMARY: updated=0 skipped=5 renamed=0 varargs=0 noreturn=0 missing=0 bad=0\n",
        encoding="utf-8",
    )
    apply.write_text(
        "OK: 0x00441740 CConsole__Printf -> void __cdecl CConsole__Printf(void * console, char * format, ...) varArgs=true noReturn=false\n"
        "OK: 0x0042cfa0 FatalError__ExitProcess -> void __cdecl FatalError__ExitProcess(char * message, int code) varArgs=false noReturn=true\n"
        "SUMMARY: updated=5 skipped=0 renamed=0 varargs=2 noreturn=1 missing=0 bad=0\n"
        "REPORT: Save succeeded\n",
        encoding="utf-8",
    )

    metadata_lines: list[str] = []
    tag_lines: list[str] = []
    xref_lines: list[str] = []
    for address, expected in probe.TARGETS.items():
        name = str(expected["name"])
        signature = str(expected["signature"])
        comment = " ".join(str(token) for token in expected["commentTokens"])
        if stale and address == "0x00441740":
            signature = "void __cdecl CConsole__Printf(void * console, char * format)"
            comment += " runtime behavior proven"
        metadata_lines.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")

        target_tags = list(expected["tags"])
        if stale and address == "0x0042cfa0":
            target_tags = [tag for tag in target_tags if tag != "no-return"]
        tag_lines.append(f"{address}\t{name}\t{';'.join(target_tags)}\tOK\n")

        decompile_text = "\n".join(str(token) for token in expected["decompileTokens"])
        (decompile_dir / f"{address[2:]}_{name}.c").write_text(decompile_text, encoding="utf-8")

        xref_count = int(expected["minXrefs"])
        if stale and address == "0x0040c640":
            xref_count -= 1
        for idx in range(xref_count):
            xref_lines.append(f"{address}\t{name}\t0x0060{idx:04x}\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n")

    instruction_lines = [
        f"{target}\t{target}\tTARGET\t0\t{instruction}\t{target}\t{probe.TARGETS[target]['name']}\t"
        f"{mnemonic}\t{operands}\t{bytes_}\tFALL_THROUGH\n"
        for target, instruction, mnemonic, operands, bytes_ in probe.INSTRUCTION_EVIDENCE
    ]

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


class DiagnosticConsoleWave386ProbeTests(unittest.TestCase):
    def test_passes_for_expected_wave386_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**write_fixture(Path(tmp)))
        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["targetCount"], 5)
        self.assertEqual(report["instructionEvidenceHits"], len(probe.INSTRUCTION_EVIDENCE))

    def test_fails_for_stale_signature_overclaim_missing_tag_and_xrefs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**write_fixture(Path(tmp), stale=True))
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("signature mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("comment overclaim" in failure for failure in report["failures"]))
        self.assertTrue(any("missing tag" in failure for failure in report["failures"]))
        self.assertTrue(any("xref count too low" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
