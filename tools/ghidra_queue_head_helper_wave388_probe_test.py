#!/usr/bin/env python3
"""Tests for the Wave388 queue-head helper Ghidra probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_queue_head_helper_wave388_probe as probe


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
    dry = root / "queue_head_helper_wave388_dry.log"
    apply = root / "queue_head_helper_wave388_apply.log"
    metadata = root / "metadata_after.tsv"
    tags = root / "tags_after.tsv"
    xrefs = root / "xrefs_after.tsv"
    instructions = root / "instructions_after.tsv"
    callsites = root / "callsite_instructions.tsv"

    dry.write_text("SUMMARY: updated=0 skipped=5 renamed=0 would_rename=0 missing=0 bad=0\n", encoding="utf-8")
    apply.write_text(
        "OK: 0x0040d320 Mat34__MultiplyBasisToOut -> void * __thiscall Mat34__MultiplyBasisToOut(void * this, void * out_basis, void * rhs_basis)\n"
        "SUMMARY: updated=5 skipped=0 renamed=0 would_rename=0 missing=0 bad=0\n"
        "REPORT: Save succeeded\n",
        encoding="utf-8",
    )

    metadata_lines: list[str] = []
    tag_lines: list[str] = []
    xref_lines: list[str] = []
    instruction_lines: list[str] = []
    callsite_lines: list[str] = []

    for address, expected in probe.TARGETS.items():
        name = str(expected["name"])
        signature = str(expected["signature"])
        comment = " ".join(str(token) for token in expected["commentTokens"])
        if stale and address == "0x0040d320":
            name = "CMCBuggy__MultiplyMat34Basis"
            signature = "void __thiscall CMCBuggy__MultiplyMat34Basis(void * this, void * out_basis, void * lhs_basis, void * rhs_basis)"
            comment += " runtime behavior proven"
        metadata_lines.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")

        target_tags = list(expected["tags"])
        if stale and address == "0x0041ad10":
            target_tags = [tag for tag in target_tags if tag != "owner-corrected"]
        tag_lines.append(f"{address}\t{name}\t{';'.join(target_tags)}\tOK\n")

        decompile_text = "\n".join(str(token) for token in expected["decompileTokens"])
        if stale and address == "0x004098c0":
            decompile_text = "missing dispatch token"
        (decompile_dir / f"{address[2:]}_{name}.c").write_text(decompile_text, encoding="utf-8")

        for idx, token in enumerate(expected["xrefTokens"]):
            from_function = str(token)
            ref_type = "UNCONDITIONAL_CALL"
            if token == "DATA":
                from_function = "<no_function>"
                ref_type = "DATA"
            if stale and address == "0x00414010" and idx == 0:
                from_function = "WrongCaller"
            xref_lines.append(f"{address}\t{name}\t0x006000{idx:02x}\t0x00400000\t{from_function}\t{ref_type}\n")

    instruction_source = probe.INSTRUCTION_EVIDENCE
    callsite_source = probe.CALLSITE_EVIDENCE
    if stale:
        instruction_source = instruction_source[:-1]
        callsite_source = callsite_source[:-1]
    for target, instruction, mnemonic, operands, bytes_ in instruction_source:
        instruction_lines.append(
            f"{target}\t{target}\tTARGET\t0\t{instruction}\t{target}\t{probe.TARGETS[target]['name']}\t"
            f"{mnemonic}\t{operands}\t{bytes_}\tFALL_THROUGH\n"
        )
    for target, instruction, mnemonic, operands in callsite_source:
        callsite_lines.append(
            f"{target}\t{target}\tTARGET\t0\t{instruction}\t{target}\tCaller\t"
            f"{mnemonic}\t{operands}\t00\tFALL_THROUGH\n"
        )

    metadata.write_text(METADATA_HEADER + "".join(metadata_lines), encoding="utf-8")
    tags.write_text(TAGS_HEADER + "".join(tag_lines), encoding="utf-8")
    xrefs.write_text(XREF_HEADER + "".join(xref_lines), encoding="utf-8")
    instructions.write_text(INSTRUCTION_HEADER + "".join(instruction_lines), encoding="utf-8")
    callsites.write_text(INSTRUCTION_HEADER + "".join(callsite_lines), encoding="utf-8")

    return {
        "dry_log_path": dry,
        "apply_log_path": apply,
        "metadata_path": metadata,
        "decompile_dir": decompile_dir,
        "xrefs_path": xrefs,
        "instructions_path": instructions,
        "callsites_path": callsites,
        "tags_path": tags,
    }


class QueueHeadHelperWave388ProbeTests(unittest.TestCase):
    def test_passes_for_expected_wave388_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**write_fixture(Path(tmp)))
        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["targetCount"], 5)
        self.assertEqual(report["instructionEvidenceHits"], len(probe.INSTRUCTION_EVIDENCE))
        self.assertEqual(report["callsiteEvidenceHits"], len(probe.CALLSITE_EVIDENCE))

    def test_fails_for_stale_name_signature_tag_xref_and_instruction_gaps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**write_fixture(Path(tmp), stale=True))
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("name mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("signature mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("comment overclaim" in failure for failure in report["failures"]))
        self.assertTrue(any("missing tag" in failure for failure in report["failures"]))
        self.assertTrue(any("missing xref token" in failure for failure in report["failures"]))
        self.assertTrue(any("missing instruction evidence" in failure for failure in report["failures"]))
        self.assertTrue(any("missing callsite evidence" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
