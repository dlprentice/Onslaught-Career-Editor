#!/usr/bin/env python3
"""Tests for the Wave378 frontend localization/text Ghidra probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_frontend_localization_wave378_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
TAGS_HEADER = "address\tname\ttags\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def strip0x(address: str) -> str:
    return address[2:] if address.startswith("0x") else address


def write_fixture(root: Path, *, stale: bool = False) -> dict[str, Path]:
    dry = root / "frontend_localization_wave378_dry.log"
    apply = root / "frontend_localization_wave378_apply.log"
    metadata = root / "metadata_after.tsv"
    tags = root / "tags_after.tsv"
    xrefs = root / "xrefs_after.tsv"
    instructions = root / "instructions_after.tsv"
    callsites = root / "callsite_instructions.tsv"
    decompile = root / "decompile_after"
    decompile.mkdir()

    count = len(probe.TARGETS)
    dry.write_text(
        "SUMMARY: updated=0 skipped=7 renamed=0 would_rename=5 missing=0 bad=0\n",
        encoding="utf-8",
    )
    apply.write_text(
        f"SUMMARY: updated={count} skipped=0 renamed=5 would_rename=0 missing=0 bad=0\nREPORT: Save succeeded\n",
        encoding="utf-8",
    )

    metadata_lines: list[str] = []
    tag_lines: list[str] = []
    for address, spec in probe.TARGETS.items():
        name = str(spec["name"])
        signature = str(spec["signature"])
        comment = " ".join(str(token) for token in spec["commentTokens"])
        if stale and address == "0x0046a1f0":
            name = "CUnitAI__GetStringByResolvedTextIdAfter"
        if stale and address == "0x0046b1e0":
            signature = "void __cdecl CFEPSaveGame__GetAsciiFallbackTextByToken(int param_1)"
        if stale and address == "0x0046a210":
            comment += " runtime proof"
        metadata_lines.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        tag_lines.append(f"{address}\t{name}\t{';'.join(sorted(probe.COMMON_TAGS | set(spec['tags'])))}\tOK\n")
        (decompile / f"{address[2:]}_{name}.c").write_text(
            f"{name}\n{signature}\n{' '.join(str(token) for token in spec['decompileTokens'])}\n",
            encoding="utf-8",
        )

    metadata.write_text(METADATA_HEADER + "".join(metadata_lines), encoding="utf-8")
    tags.write_text(TAGS_HEADER + "".join(tag_lines), encoding="utf-8")
    xrefs.write_text(
        XREF_HEADER
        + "".join(
            f"{strip0x(target)}\t{probe.TARGETS[target]['name']}\t{strip0x(source)}\t<none>\t{caller}\t{ref_type}\n"
            for target, source, caller, ref_type in probe.XREF_EVIDENCE
        ),
        encoding="utf-8",
    )
    instruction_lines = [
        (
            f"{target}\t{target}\tTARGET\t0\t{instruction_addr}\t{target}\t{probe.TARGETS[target]['name']}\t"
            f"{mnemonic}\t{operands}\t{bytes_}\tFALL_THROUGH\n"
        )
        for target, instruction_addr, mnemonic, operands, bytes_ in probe.INSTRUCTION_EVIDENCE
    ]
    if stale:
        instruction_lines = [line for line in instruction_lines if "0046a210" not in line]
    instructions.write_text(INSTRUCTION_HEADER + "".join(instruction_lines), encoding="utf-8")
    callsites.write_text(
        INSTRUCTION_HEADER
        + "".join(
            f"{target}\t{target}\tTARGET\t0\t{instruction_addr}\t<none>\t<no_function>\t{mnemonic}\t"
            f"{operands}\t{bytes_}\tFALL_THROUGH\n"
            for target, instruction_addr, mnemonic, operands, bytes_ in probe.CALLSITE_EVIDENCE
        ),
        encoding="utf-8",
    )
    return {
        "root": root,
        "dry": dry,
        "apply": apply,
        "metadata": metadata,
        "tags": tags,
        "xrefs": xrefs,
        "instructions": instructions,
        "callsites": callsites,
        "decompile": decompile,
    }


class FrontendLocalizationWave378ProbeTests(unittest.TestCase):
    def test_passes_for_saved_frontend_localization_tranche(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                root=paths["root"],
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                tags_path=paths["tags"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
                callsites_path=paths["callsites"],
                decompile_dir=paths["decompile"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], len(probe.TARGETS))
        self.assertEqual(report["summary"]["xrefEvidenceHits"], len(probe.XREF_EVIDENCE))
        self.assertEqual(report["summary"]["instructionEvidenceHits"], len(probe.INSTRUCTION_EVIDENCE))
        self.assertEqual(report["summary"]["callsiteEvidenceHits"], len(probe.CALLSITE_EVIDENCE))

    def test_fails_for_stale_owner_signature_overclaim_or_missing_color_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale=True)
            report = probe.build_report(
                root=paths["root"],
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                tags_path=paths["tags"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
                callsites_path=paths["callsites"],
                decompile_dir=paths["decompile"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("name mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("signature mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("overclaim" in failure for failure in report["failures"]))
        self.assertTrue(any("missing instruction evidence" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
