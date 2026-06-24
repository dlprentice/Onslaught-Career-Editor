#!/usr/bin/env python3
"""Tests for the MeshPart/CMC existing-function signature probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_meshpart_cmc_existing_signature_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
TAGS_HEADER = "address\tname\ttags\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)
VTABLE_HEADER = (
    "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\t"
    "containing_entry\tcontaining_name\tstatus\n"
)
STRING_HEADER = "input_addr\tmode\tptr_raw\ttarget_addr\tcstring\n"


def strip0x(address: str) -> str:
    return address[2:] if address.startswith("0x") else address


def write_fixture(root: Path, *, stale: bool = False, missing_string: bool = False) -> dict[str, Path]:
    dry = root / "meshpart_cmc_existing_signature_dry.log"
    apply = root / "meshpart_cmc_existing_signature_apply.log"
    metadata = root / "metadata_after.tsv"
    tags = root / "tags_after.tsv"
    xrefs = root / "xrefs_after.tsv"
    instructions = root / "instructions_after.tsv"
    vtables = root / "vtable_slots_after.tsv"
    decompile = root / "decompile_after"
    decompile.mkdir()

    count = len(probe.TARGETS)
    dry.write_text(f"--- SUMMARY ---\ntargets={count} changed_or_would_change={count} failed=0 dry=true\n", encoding="utf-8")
    apply.write_text(f"--- SUMMARY ---\ntargets={count} changed_or_would_change={count} failed=0 dry=false\n", encoding="utf-8")

    metadata_lines: list[str] = []
    tag_lines: list[str] = []
    for address, spec in probe.TARGETS.items():
        name = str(spec["name"])
        signature = str(spec["signature"])
        if stale and address == "0x00495960":
            signature = "void * __thiscall CMCComponent__ScalarDeletingDestructor(void * this, int param_2)"
        comment = " ".join(str(token) for token in spec["commentTokens"])
        if stale and address == "0x004957d0":
            comment += " runtime behavior proven"
        metadata_lines.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        tag_lines.append(f"{address}\t{name}\t{';'.join(sorted(probe.COMMON_TAGS | set(spec['tags'])))}\tOK\n")
        (decompile / f"{address[2:]}_{name}.c").write_text(
            f"{name}\n{signature}\nreturn;\n{' '.join(str(token) for token in spec['decompileTokens'])}\n",
            encoding="utf-8",
        )

    metadata.write_text(METADATA_HEADER + "".join(metadata_lines), encoding="utf-8")
    tags.write_text(TAGS_HEADER + "".join(tag_lines), encoding="utf-8")
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
    vtables.write_text(
        VTABLE_HEADER
        + "".join(
            f"{strip0x(vtable)}\t{slot}\t{strip0x(slot_addr)}\t{pointer}\t{strip0x(pointer)}\t{strip0x(pointer)}\t"
            f"{probe.TARGETS[pointer]['name']}\t{strip0x(pointer)}\t{probe.TARGETS[pointer]['name']}\tOK\n"
            for vtable, slot, slot_addr, pointer in probe.VTABLE_EVIDENCE
        ),
        encoding="utf-8",
    )
    for filename, expected in probe.STRING_EVIDENCE:
        value = "" if missing_string and filename == "string_0062dd88.tsv" else expected
        (root / filename).write_text(STRING_HEADER + f"00000000\tdirect\t\t00000000\t{value}\n", encoding="utf-8")

    return {
        "root": root,
        "dry": dry,
        "apply": apply,
        "metadata": metadata,
        "tags": tags,
        "xrefs": xrefs,
        "instructions": instructions,
        "vtables": vtables,
        "decompile": decompile,
    }


class MeshPartCmcExistingSignatureProbeTests(unittest.TestCase):
    def test_passes_for_saved_signature_tranche(self) -> None:
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
                vtable_path=paths["vtables"],
                decompile_dir=paths["decompile"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], 12)
        self.assertEqual(report["summary"]["xrefEvidenceHits"], len(probe.XREF_EVIDENCE))
        self.assertEqual(report["summary"]["instructionEvidenceHits"], len(probe.INSTRUCTION_EVIDENCE))
        self.assertEqual(report["summary"]["vtableEvidenceHits"], len(probe.VTABLE_EVIDENCE))
        self.assertEqual(report["summary"]["stringEvidenceHits"], len(probe.STRING_EVIDENCE))

    def test_fails_for_stale_signature_overclaim_or_missing_string(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale=True, missing_string=True)
            report = probe.build_report(
                root=paths["root"],
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                tags_path=paths["tags"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
                vtable_path=paths["vtables"],
                decompile_dir=paths["decompile"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("signature mismatch" in failure or "stale signature token" in failure for failure in report["failures"]))
        self.assertTrue(any("overclaim" in failure for failure in report["failures"]))
        self.assertTrue(any("string evidence mismatch" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
