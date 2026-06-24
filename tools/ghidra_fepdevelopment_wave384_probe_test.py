#!/usr/bin/env python3
"""Tests for the Wave384 CFEPDevelopment Ghidra probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_fepdevelopment_wave384_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
TAGS_HEADER = "address\tname\ttags\tstatus\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def write_fixture(root: Path, *, stale: bool = False) -> dict[str, Path]:
    dry = root / "fepdevelopment_wave384_dry.log"
    apply = root / "fepdevelopment_wave384_apply.log"
    metadata = root / "metadata_after.tsv"
    tags = root / "tags_after.tsv"
    instructions = root / "instructions_after.tsv"
    callsites = root / "callsite_instructions_wave384.tsv"
    decompile = root / "decompile_after"
    decompile.mkdir()

    dry.write_text(
        "SUMMARY: updated=0 skipped=8 created=0 would_create=1 boundary_moved=0 "
        "would_boundary_move=1 renamed=0 would_rename=0 missing=0 bad=0\n",
        encoding="utf-8",
    )
    apply.write_text(
        f"SUMMARY: updated={len(probe.TARGETS)} skipped=0 created=1 would_create=0 boundary_moved=1 "
        "would_boundary_move=0 renamed=0 would_rename=0 missing=0 bad=0\n"
        "REPORT: Save succeeded\n",
        encoding="utf-8",
    )

    metadata_lines: list[str] = [
        "0x00458100\t<none>\t<none>\t\tMISSING\n"
    ]
    tag_lines: list[str] = []
    for address, spec in probe.TARGETS.items():
        signature = str(spec["signature"])
        comment = " ".join(str(token) for token in spec["commentTokens"])
        if stale and address == "0x00458ce0":
            signature = "void __fastcall CFEPDevelopment__ResolveActiveStorageDevice(void * this, int force_refresh)"
            comment += " runtime proof"
        metadata_lines.append(f"{address}\t{spec['name']}\t{signature}\t{comment}\tOK\n")
        tag_lines.append(f"{address}\t{spec['name']}\t{';'.join(sorted(probe.COMMON_TAGS | set(spec['tags'])))}\tOK\n")
        decompile_text = f"{spec['name']}\n{signature}\n{' '.join(str(token) for token in spec['decompileTokens'])}\n"
        if stale and address == "0x00458090":
            decompile_text += "unaff_EBP\n"
        (decompile / f"{address[2:]}_{spec['name']}.c").write_text(decompile_text, encoding="utf-8")

    metadata.write_text(METADATA_HEADER + "".join(metadata_lines), encoding="utf-8")
    tags.write_text(TAGS_HEADER + "".join(tag_lines), encoding="utf-8")
    instructions.write_text(
        INSTRUCTION_HEADER
        + "".join(
            f"{target}\t{target}\tTARGET\t0\t{instruction}\t{target}\t{probe.TARGETS[target]['name']}\t"
            f"{mnemonic}\t{operands}\t{bytes_}\tFALL_THROUGH\n"
            for target, instruction, mnemonic, operands, bytes_ in probe.INSTRUCTION_EVIDENCE
        ),
        encoding="utf-8",
    )
    callsites.write_text(
        INSTRUCTION_HEADER
        + "".join(
            f"{target}\t{target}\tTARGET\t0\t{target}\t<none>\t<no_function>\t{mnemonic}\t{operands}\t00\tFALL_THROUGH\n"
            for target, mnemonic, operands in probe.CALLSITE_EVIDENCE
        ),
        encoding="utf-8",
    )
    return {
        "root": root,
        "dry": dry,
        "apply": apply,
        "metadata": metadata,
        "tags": tags,
        "instructions": instructions,
        "callsites": callsites,
        "decompile": decompile,
    }


class FepDevelopmentWave384ProbeTests(unittest.TestCase):
    def test_passes_for_boundary_and_signature_corrections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                root=paths["root"],
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                tags_path=paths["tags"],
                instructions_path=paths["instructions"],
                callsite_instructions_path=paths["callsites"],
                decompile_dir=paths["decompile"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], len(probe.TARGETS))
        self.assertEqual(report["summary"]["instructionEvidenceHits"], len(probe.INSTRUCTION_EVIDENCE))
        self.assertEqual(report["summary"]["callsiteEvidenceHits"], len(probe.CALLSITE_EVIDENCE))

    def test_fails_for_stale_boundary_signature_or_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale=True)
            # Simulate the old bad partial boundary still being present.
            metadata_text = paths["metadata"].read_text(encoding="utf-8")
            paths["metadata"].write_text(
                metadata_text.replace("0x00458100\t<none>\t<none>\t\tMISSING", "0x00458100\tCFEPDevelopment__EnumerateWorldFiles\tbool CFEPDevelopment__EnumerateWorldFiles(void)\t\tOK"),
                encoding="utf-8",
            )
            report = probe.build_report(
                root=paths["root"],
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                tags_path=paths["tags"],
                instructions_path=paths["instructions"],
                callsite_instructions_path=paths["callsites"],
                decompile_dir=paths["decompile"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("boundary guard failed" in failure for failure in report["failures"]))
        self.assertTrue(any("signature mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("comment overclaim" in failure for failure in report["failures"]))
        self.assertTrue(any("stale decompile token" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
