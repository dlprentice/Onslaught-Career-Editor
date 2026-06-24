#!/usr/bin/env python3
"""Tests for the Wave370 frontend/control-binding signature probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_frontend_controls_signature_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
TAGS_HEADER = "address\tname\ttags\tstatus\n"
VTABLE_HEADER = "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\tcontaining_entry\tcontaining_name\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def strip0x(address: str) -> str:
    return address[2:] if address.startswith("0x") else address


def write_fixture(root: Path, *, stale: bool = False) -> dict[str, Path]:
    dry = root / "frontend_controls_signature_dry.log"
    apply = root / "frontend_controls_signature_apply.log"
    metadata = root / "metadata_after.tsv"
    tags = root / "tags_after.tsv"
    vtable = root / "vtable_slots_after.tsv"
    xrefs = root / "xrefs_after.tsv"
    instructions = root / "instructions_after.tsv"
    controlsui_instructions = root / "controlsui_instructions_after.tsv"

    count = len(probe.TARGETS)
    dry.write_text(f"--- SUMMARY ---\ntargets={count} changed_or_would_change={count} failed=0 dry=true\n", encoding="utf-8")
    apply.write_text(f"--- SUMMARY ---\ntargets={count} changed_or_would_change={count} failed=0 dry=false\n", encoding="utf-8")

    metadata_lines: list[str] = []
    tag_lines: list[str] = []
    for address, spec in probe.TARGETS.items():
        name = str(spec["name"])
        signature = str(spec["signature"])
        comment = " ".join(str(token) for token in spec["commentTokens"])
        if stale and address == "0x00455010":
            signature = signature.replace("columnIndex", "param_2")
        if stale and address == "0x00453ac0":
            name = "CControllerDefinition__VFunc_01_00453ac0"
        if stale and address == "0x00456080":
            comment += " runtime behavior proven"
        metadata_lines.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        tag_lines.append(f"{address}\t{name}\t{';'.join(sorted(probe.COMMON_TAGS | set(spec['tags'])))}\tOK\n")

    metadata.write_text(METADATA_HEADER + "".join(metadata_lines), encoding="utf-8")
    tags.write_text(TAGS_HEADER + "".join(tag_lines), encoding="utf-8")
    vtable.write_text(
        VTABLE_HEADER
        + "".join(
            f"{strip0x(vtable_addr)}\t{slot}\t{strip0x(slot_addr)}\t0x{strip0x(pointer)}\t{strip0x(pointer)}\t"
            f"{strip0x(pointer)}\t{name}\t{strip0x(pointer)}\t{name}\tOK\n"
            for vtable_addr, slot, slot_addr, pointer, name in probe.VTABLE_EVIDENCE
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

    instruction_lines = []
    controlsui_lines = []
    for target, instruction_addr, mnemonic, operands in probe.INSTRUCTION_EVIDENCE:
        line = (
            f"{target}\t{target}\tAFTER\t1\t{instruction_addr}\t{target}\t{probe.TARGETS[target]['name']}\t"
            f"{mnemonic}\t{operands}\t00\tFALL_THROUGH\n"
        )
        if target in {"0x00455010", "0x00456080"}:
            controlsui_lines.append(line)
        else:
            instruction_lines.append(line)
    if stale:
        controlsui_lines = [line for line in controlsui_lines if "00455d98" not in line]
    instructions.write_text(INSTRUCTION_HEADER + "".join(instruction_lines), encoding="utf-8")
    controlsui_instructions.write_text(INSTRUCTION_HEADER + "".join(controlsui_lines), encoding="utf-8")

    return {
        "root": root,
        "dry": dry,
        "apply": apply,
        "metadata": metadata,
        "tags": tags,
        "vtable": vtable,
        "xrefs": xrefs,
        "instructions": instructions,
        "controlsui_instructions": controlsui_instructions,
    }


class FrontendControlsSignatureProbeTests(unittest.TestCase):
    def test_passes_for_saved_frontend_controls_signature_tranche(self) -> None:
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
                controlsui_instructions_path=paths["controlsui_instructions"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], len(probe.TARGETS))
        self.assertEqual(report["summary"]["vtableEvidenceHits"], len(probe.VTABLE_EVIDENCE))
        self.assertEqual(report["summary"]["xrefEvidenceHits"], len(probe.XREF_EVIDENCE))
        self.assertEqual(report["summary"]["instructionEvidenceHits"], len(probe.INSTRUCTION_EVIDENCE))

    def test_fails_for_stale_owner_signature_overclaim_or_missing_instruction(self) -> None:
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
                controlsui_instructions_path=paths["controlsui_instructions"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("name mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("signature mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("overclaim" in failure for failure in report["failures"]))
        self.assertTrue(any("missing instruction evidence" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
