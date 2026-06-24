#!/usr/bin/env python3
"""Tests for the Wave369 feature/monitor boundary probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_feature_monitor_boundary_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
TAGS_HEADER = "address\tname\ttags\tstatus\n"
VTABLE_HEADER = "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\tcontaining_entry\tcontaining_name\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)
STRING_HEADER = "input_addr\tmode\tptr_raw\ttarget_addr\tcstring\n"


def strip0x(address: str) -> str:
    return address[2:] if address.startswith("0x") else address


def write_fixture(root: Path, *, stale: bool = False) -> dict[str, Path]:
    dry = root / "feature_monitor_boundary_dry.log"
    apply = root / "feature_monitor_boundary_apply.log"
    metadata = root / "metadata_after.tsv"
    tags = root / "tags_after.tsv"
    vtable = root / "vtable_slots_after.tsv"
    xrefs = root / "xrefs_after.tsv"
    instructions = root / "instructions_after.tsv"

    count = len(probe.TARGETS)
    dry.write_text(f"--- SUMMARY ---\ntargets={count} changed_or_would_change={count} failed=0 dry=true\n", encoding="utf-8")
    apply.write_text(f"--- SUMMARY ---\ntargets={count} changed_or_would_change={count} failed=0 dry=false\n", encoding="utf-8")

    metadata_lines: list[str] = []
    tag_lines: list[str] = []
    for address, spec in probe.TARGETS.items():
        name = str(spec["name"])
        signature = str(spec["signature"])
        comment = " ".join(str(token) for token in spec["commentTokens"])
        if stale and address == "0x0044e640":
            signature = signature.replace("void * this", "void * param_1")
        if stale and address == "0x0044e4e0":
            comment += " runtime behavior proven"
        metadata_lines.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        tag_lines.append(f"{address}\t{name}\t{';'.join(sorted(probe.COMMON_TAGS | set(spec['tags'])))}\tOK\n")

    metadata.write_text(METADATA_HEADER + "".join(metadata_lines), encoding="utf-8")
    tags.write_text(TAGS_HEADER + "".join(tag_lines), encoding="utf-8")
    vtable.write_text(
        VTABLE_HEADER
        + "".join(
            f"{strip0x(vtable_addr)}\t{slot}\t{strip0x(slot_addr)}\t0x{strip0x(pointer)}\t{strip0x(pointer)}\t"
            f"{strip0x(pointer)}\t{probe.TARGETS[pointer]['name']}\t{strip0x(pointer)}\t{probe.TARGETS[pointer]['name']}\tOK\n"
            for vtable_addr, slot, slot_addr, pointer in probe.VTABLE_EVIDENCE
        ),
        encoding="utf-8",
    )
    xrefs.write_text(
        XREF_HEADER
        + "".join(
            f"{strip0x(target)}\t{probe.TARGETS[target]['name']}\t{strip0x(source)}\t<none>\t<no_function>\t{ref_type}\n"
            for target, source, ref_type in probe.XREF_EVIDENCE
        ),
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "".join(
            f"{target}\t{target}\tAFTER\t1\t{addr}\t{target}\t{probe.TARGETS[target]['name']}\t"
            f"{mnemonic}\t{operands}\t00\tFALL_THROUGH\n"
            for target, addr, mnemonic, operands in probe.INSTRUCTION_EVIDENCE
        ),
        encoding="utf-8",
    )
    for filename, expected in probe.STRING_EVIDENCE:
        value = "" if stale and "00628e4c" in filename else expected
        (root / filename).write_text(STRING_HEADER + f"00000000\tdirect\t\t00000000\t{value}\n", encoding="utf-8")

    return {
        "root": root,
        "dry": dry,
        "apply": apply,
        "metadata": metadata,
        "tags": tags,
        "vtable": vtable,
        "xrefs": xrefs,
        "instructions": instructions,
    }


class FeatureMonitorBoundaryProbeTests(unittest.TestCase):
    def test_passes_for_saved_boundary_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                root=paths["root"],
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                tags_path=paths["tags"],
                vtable_path=paths["vtable"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], len(probe.TARGETS))
        self.assertEqual(report["summary"]["vtableEvidenceHits"], len(probe.VTABLE_EVIDENCE))
        self.assertEqual(report["summary"]["xrefEvidenceHits"], len(probe.XREF_EVIDENCE))
        self.assertEqual(report["summary"]["instructionEvidenceHits"], len(probe.INSTRUCTION_EVIDENCE))
        self.assertEqual(report["summary"]["stringEvidenceHits"], len(probe.STRING_EVIDENCE))

    def test_fails_for_stale_signature_overclaim_or_missing_string(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale=True)
            report = probe.build_report(
                root=paths["root"],
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                tags_path=paths["tags"],
                vtable_path=paths["vtable"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("signature mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("overclaim" in failure for failure in report["failures"]))
        self.assertTrue(any("string evidence mismatch" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
