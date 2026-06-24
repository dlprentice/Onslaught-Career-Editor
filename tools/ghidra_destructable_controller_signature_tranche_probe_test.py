#!/usr/bin/env python3
"""Tests for the destructable-controller Ghidra signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_destructable_controller_signature_tranche_probe as probe


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
    dry = root / "destructable_controller_dry.log"
    apply = root / "destructable_controller_apply.log"
    metadata = root / "metadata_final.tsv"
    tags = root / "tags_final.tsv"
    xrefs = root / "xrefs_final.tsv"
    vtable_slots = root / "vtable_slots_final.tsv"
    instructions = root / "instructions_final.tsv"
    decompile = root / "decompile_final"
    caller_decompile = root / "caller_decompile_final"
    decompile.mkdir()
    caller_decompile.mkdir()

    dry.write_text("--- SUMMARY ---\ntargets=18 changed_or_would_change=18 failed=0 dry=true\n", encoding="utf-8")
    apply.write_text("--- SUMMARY ---\ntargets=18 changed_or_would_change=18 failed=0 dry=false\n", encoding="utf-8")

    metadata_lines = []
    tag_lines = []
    xref_lines = []
    for address, spec in probe.TARGETS.items():
        name = str(spec["name"])
        signature = str(spec["signature"])
        if stale and address == "0x004433f0":
            name = "CDestructableSegmentsController__AreCoreChildrenDestroyed"
            signature = "int __fastcall CDestructableSegmentsController__AreCoreChildrenDestroyed(int param_1)"
        comment = " ".join(str(token) for token in spec["commentTokens"])
        if overclaim and address == "0x004443f0":
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
        + "005db06c\t1\t005db070\t0x004434d0\t004434d0\t004434d0\tCDestroyableCoreSegment__scalar_deleting_dtor\t004434d0\tCDestroyableCoreSegment__scalar_deleting_dtor\tOK\n"
        + "005db06c\t3\t005db078\t0x004435f0\t004435f0\t004435f0\tCDestroyableCoreSegment__VFunc_03_ApplyDamage\t004435f0\tCDestroyableCoreSegment__VFunc_03_ApplyDamage\tOK\n"
        + "005db148\t3\t005db154\t0x00443780\t00443780\t00443780\tCDestroyableSwapSegment__VFunc_03_ApplyDamage\t00443780\tCDestroyableSwapSegment__VFunc_03_ApplyDamage\tOK\n"
        + "005db148\t8\t005db168\t0x00443810\t00443810\t00443810\tCDestroyableSwapSegment__VFunc_08_HandleSegmentBreak\t00443810\tCDestroyableSwapSegment__VFunc_08_HandleSegmentBreak\tOK\n"
        + "005db0e0\t8\t005db100\t0x004439c0\t004439c0\t004439c0\tCDestroyableSegment__SharedVFunc_08_HandleChildBreak\t004439c0\tCDestroyableSegment__SharedVFunc_08_HandleChildBreak\tOK\n"
        + "005db114\t8\t005db134\t0x004439c0\t004439c0\t004439c0\tCDestroyableSegment__SharedVFunc_08_HandleChildBreak\t004439c0\tCDestroyableSegment__SharedVFunc_08_HandleChildBreak\tOK\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x00443480\t0x00443480\tAFTER\t1\t0x004434b9\t0x00443480\tCDestroyableCoreSegment__Init\tRET\t0x14\tc2 14 00\tTERMINATOR\n"
        + "0x004434d0\t0x004434d0\tAFTER\t1\t0x004434ed\t0x004434d0\tCDestroyableCoreSegment__scalar_deleting_dtor\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x00443780\t0x00443780\tAFTER\t1\t0x0044380b\t0x00443780\tCDestroyableSwapSegment__VFunc_03_ApplyDamage\tRET\t0x8\tc2 08 00\tTERMINATOR\n"
        + "0x00444030\t0x00444030\tAFTER\t1\t0x00444155\t0x00444030\tCDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold\tRET\t0xc\tc2 0c 00\tTERMINATOR\n"
        + "0x004442d0\t0x004442d0\tAFTER\t1\t0x004442ef\t0x004442d0\tCDestructableSegmentsController__GetSegmentLastDamageTimeByIndex\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x00444300\t0x00444300\tAFTER\t1\t0x0044431f\t0x00444300\tCDestructableSegmentsController__GetSegmentLastDamageAmountByIndex\tRET\t0x4\tc2 04 00\tTERMINATOR\n",
        encoding="utf-8",
    )
    (caller_decompile / "callers.c").write_text(
        "CDestructableSegmentsController__CreateSegment "
        "CDestructableSegmentsController__ProcessNode "
        "CDestroyableCoreSegment__Init\n",
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


class DestructableControllerSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_saved_destructable_controller_tranche(self) -> None:
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
        self.assertEqual(report["summary"]["targets"], 18)
        self.assertEqual(report["summary"]["vtableEvidenceHits"], 6)
        self.assertEqual(report["summary"]["retEvidenceHits"], 6)
        self.assertEqual(report["summary"]["commentOverclaims"], 0)

    def test_fails_for_stale_owner_or_overclaim(self) -> None:
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
