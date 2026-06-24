#!/usr/bin/env python3
"""Tests for the destructable bridge Ghidra signature/boundary tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_destructable_bridge_signature_boundary_tranche_probe as probe


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


def write_fixture(root: Path, *, stale: bool = False, missing_vtable: bool = False) -> dict[str, Path]:
    dry = root / "destructable_bridge_dry.log"
    apply = root / "destructable_bridge_apply.log"
    metadata = root / "metadata_final.tsv"
    tags = root / "tags_final.tsv"
    xrefs = root / "xrefs_final.tsv"
    instructions = root / "instructions_final.tsv"
    vtables = root / "vtable_slots_final.tsv"
    decompile = root / "decompile_final"
    decompile.mkdir()

    dry.write_text("--- SUMMARY ---\ntargets=5 changed_or_would_change=5 failed=0 dry=true\n", encoding="utf-8")
    apply.write_text("--- SUMMARY ---\ntargets=5 changed_or_would_change=5 failed=0 dry=false\n", encoding="utf-8")

    metadata_lines = []
    tag_lines = []
    for address, spec in probe.TARGETS.items():
        name = str(spec["name"])
        signature = str(spec["signature"])
        if stale and address == "0x00444940":
            signature = "undefined CDestroyableSegmentComponent__scalar_deleting_dtor(void)"
        comment = " ".join(str(token) for token in spec["commentTokens"])
        if stale and address == "0x00444be0":
            comment += " runtime destruction behavior proven"
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
            f"{target[2:]}\t{probe.TARGETS[target]['name']}\t{source[2:]}\t00400000\tCaller\t{ref_type}\n"
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
    vtable_rows = "" if missing_vtable else "".join(
        f"{vtable[2:]}\t{slot}\t{slot_addr[2:]}\t{pointer}\t{pointer_addr[2:]}\t{pointer_addr[2:]}\t"
        f"{probe.TARGETS[pointer_addr]['name']}\t{pointer_addr[2:]}\t{probe.TARGETS[pointer_addr]['name']}\tOK\n"
        for vtable, slot, slot_addr, pointer, pointer_addr in probe.VTABLE_EVIDENCE
    )
    vtables.write_text(VTABLE_HEADER + vtable_rows, encoding="utf-8")

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


class DestructableBridgeSignatureBoundaryTrancheProbeTests(unittest.TestCase):
    def test_passes_for_saved_destructable_bridge_tranche(self) -> None:
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
        self.assertEqual(report["summary"]["targets"], 5)
        self.assertEqual(report["summary"]["xrefEvidenceHits"], 7)
        self.assertEqual(report["summary"]["instructionEvidenceHits"], 8)
        self.assertEqual(report["summary"]["vtableEvidenceHits"], 4)

    def test_fails_for_stale_metadata_or_missing_vtable_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale=True, missing_vtable=True)
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
        self.assertTrue(any("signature mismatch" in failure or "stale" in failure for failure in report["failures"]))
        self.assertTrue(any("overclaim" in failure for failure in report["failures"]))
        self.assertTrue(any("vtable evidence" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
