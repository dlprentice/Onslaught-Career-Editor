#!/usr/bin/env python3
"""Tests for the destructable-segment Ghidra signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_destructable_segment_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
TAGS_HEADER = "address\tname\ttags\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
VTABLE_HEADER = (
    "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\t"
    "containing_entry\tcontaining_name\tstatus\n"
)
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def write_fixture(root: Path, *, stale: bool = False, overclaim: bool = False) -> dict[str, Path]:
    dry = root / "destructable_segment_dry.log"
    apply = root / "destructable_segment_apply.log"
    metadata = root / "metadata_final.tsv"
    tags = root / "tags_final.tsv"
    xrefs = root / "xrefs_final.tsv"
    vtable_slots = root / "vtable_slots_final.tsv"
    instructions = root / "instructions_final.tsv"
    decompile = root / "decompile_final"
    caller_decompile = root / "caller_decompile_final"
    decompile.mkdir()
    caller_decompile.mkdir()

    dry.write_text("--- SUMMARY ---\ntargets=12 changed_or_would_change=12 failed=0 dry=true\n", encoding="utf-8")
    apply.write_text("--- SUMMARY ---\ntargets=12 changed_or_would_change=12 failed=0 dry=false\n", encoding="utf-8")

    metadata_lines = []
    tag_lines = []
    xref_lines = []
    for address, spec in probe.TARGETS.items():
        name = str(spec["name"])
        signature = str(spec["signature"])
        if stale and address == "0x00442660":
            name = "CDestroyableSegment__ctor_like_00442660"
            signature = "void __fastcall CDestroyableSegment__ctor_like_00442660(void * param_1)"
        comment = " ".join(str(token) for token in spec["commentTokens"])
        if overclaim and address == "0x00442f60":
            comment += " runtime behavior proven"
        metadata_lines.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        tag_lines.append(f"{address}\t{name}\t{';'.join(sorted(probe.COMMON_TAGS | set(spec['tags'])))}\tOK\n")
        xref_lines.append(f"{address[2:]}\t{name}\t00400000\t00400000\tCaller\tUNCONDITIONAL_CALL\n")
        (decompile / f"{address[2:]}_{name}.c").write_text(
            f"{name}\n{signature}\n{' '.join(str(token) for token in spec['decompileTokens'])}\n",
            encoding="utf-8",
        )

    metadata.write_text(METADATA_HEADER + "".join(metadata_lines), encoding="utf-8")
    tags.write_text(TAGS_HEADER + "".join(tag_lines), encoding="utf-8")
    xrefs.write_text(XREF_HEADER + "".join(xref_lines), encoding="utf-8")
    vtable_slots.write_text(
        VTABLE_HEADER
        + "005db02c\t1\t005db030\t0x00442640\t00442640\t00442640\tCDestroyableSegment__scalar_deleting_dtor\t00442640\tCDestroyableSegment__scalar_deleting_dtor\tOK\n"
        + "005db02c\t8\t005db04c\t0x00442b20\t00442b20\t00442b20\tCDestroyableSegment__VFunc_08_HandleSegmentBreak\t00442b20\tCDestroyableSegment__VFunc_08_HandleSegmentBreak\tOK\n"
        + "005db02c\t10\t005db054\t0x00442f60\t00442f60\t00442f60\tCDestroyableSegment__VFunc_10_SpawnRubbleEffects\t00442f60\tCDestroyableSegment__VFunc_10_SpawnRubbleEffects\tOK\n"
        + "005db06c\t10\t005db094\t0x00442f60\t00442f60\t00442f60\tCDestroyableSegment__VFunc_10_SpawnRubbleEffects\t00442f60\tCDestroyableSegment__VFunc_10_SpawnRubbleEffects\tOK\n"
        + "005db114\t10\t005db13c\t0x00442f60\t00442f60\t00442f60\tCDestroyableSegment__VFunc_10_SpawnRubbleEffects\t00442f60\tCDestroyableSegment__VFunc_10_SpawnRubbleEffects\tOK\n"
        + "005db148\t10\t005db170\t0x00442f60\t00442f60\t00442f60\tCDestroyableSegment__VFunc_10_SpawnRubbleEffects\t00442f60\tCDestroyableSegment__VFunc_10_SpawnRubbleEffects\tOK\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x004425a0\t0x004425a0\tAFTER\t42\t0x00442638\t0x004425a0\tCDestructableSegment__Init\tRET\t0x10\tc2 10 00\tTERMINATOR\n"
        + "0x00442640\t0x00442640\tAFTER\t10\t0x0044265d\t0x00442640\tCDestroyableSegment__scalar_deleting_dtor\tRET\t0x4\tc2 04 00\tTERMINATOR\n",
        encoding="utf-8",
    )
    (caller_decompile / "callers.c").write_text(
        "CDestructableSegmentsController__CreateSegment CDestructableSegmentsController__ProcessNode "
        "CDestructableSegment__RegisterChild\n",
        encoding="utf-8",
    )

    return {
        "root": root,
        "dry": dry,
        "apply": apply,
        "metadata": metadata,
        "tags": tags,
        "xrefs": xrefs,
        "vtable_slots": vtable_slots,
        "instructions": instructions,
        "decompile": decompile,
        "caller_decompile": caller_decompile,
    }


class DestructableSegmentSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_saved_destructable_segment_tranche(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                root=paths["root"],
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                tags_path=paths["tags"],
                xrefs_path=paths["xrefs"],
                vtable_slots_path=paths["vtable_slots"],
                instructions_path=paths["instructions"],
                decompile_dir=paths["decompile"],
                caller_decompile_dir=paths["caller_decompile"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], 12)
        self.assertEqual(report["summary"]["vtableEvidenceHits"], 6)
        self.assertEqual(report["summary"]["commentOverclaims"], 0)

    def test_fails_for_stale_name_or_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale=True, overclaim=True)
            report = probe.build_report(
                root=paths["root"],
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                tags_path=paths["tags"],
                xrefs_path=paths["xrefs"],
                vtable_slots_path=paths["vtable_slots"],
                instructions_path=paths["instructions"],
                decompile_dir=paths["decompile"],
                caller_decompile_dir=paths["caller_decompile"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("stale" in failure or "name" in failure for failure in report["failures"]))
        self.assertTrue(any("overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
