#!/usr/bin/env python3
"""Tests for the destructable-controller tail Ghidra signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_destructable_controller_tail_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
TAGS_HEADER = "address\tname\ttags\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def write_fixture(root: Path, *, stale: bool = False, overclaim: bool = False) -> dict[str, Path]:
    dry = root / "destructable_controller_tail_dry.log"
    apply = root / "destructable_controller_tail_apply.log"
    metadata = root / "metadata_final.tsv"
    tags = root / "tags_final.tsv"
    xrefs = root / "xrefs_final.tsv"
    instructions = root / "instructions_final.tsv"
    callsites = root / "callsite_instructions_final.tsv"
    decompile = root / "decompile_final"
    caller_decompile = root / "caller_decompile_final"
    decompile.mkdir()
    caller_decompile.mkdir()

    dry.write_text("--- SUMMARY ---\ntargets=8 changed_or_would_change=8 failed=0 dry=true\n", encoding="utf-8")
    apply.write_text("--- SUMMARY ---\ntargets=8 changed_or_would_change=8 failed=0 dry=false\n", encoding="utf-8")

    metadata_lines = []
    tag_lines = []
    xref_lines = []
    instruction_lines = []
    for address, spec in probe.TARGETS.items():
        name = str(spec["name"])
        signature = str(spec["signature"])
        if stale and address == "0x00444660":
            signature = "undefined CDestructableSegmentsController__Init(void)"
        comment = " ".join(str(token) for token in spec["commentTokens"])
        if overclaim and address == "0x00444c10":
            comment += " runtime behavior proven"
        metadata_lines.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        tag_lines.append(f"{address}\t{name}\t{';'.join(sorted(probe.COMMON_TAGS | set(spec['tags'])))}\tOK\n")
        xref_lines.append(f"{address[2:]}\t{name}\t00400000\t00400000\tCaller\tUNCONDITIONAL_CALL\n")
        operand = probe.RET_EVIDENCE[address]
        instruction_lines.append(
            f"{address}\t{address}\tAFTER\t1\t{address}\t{address}\t{name}\tRET\t{operand}\tc2\tTERMINATOR\n"
        )
        (decompile / f"{address[2:]}_{name}.c").write_text(
            f"{name}\n{signature}\n{' '.join(str(token) for token in spec['decompileTokens'])}\n",
            encoding="utf-8",
        )

    metadata.write_text(METADATA_HEADER + "".join(metadata_lines), encoding="utf-8")
    tags.write_text(TAGS_HEADER + "".join(tag_lines), encoding="utf-8")
    xrefs.write_text(XREF_HEADER + "".join(xref_lines), encoding="utf-8")
    instructions.write_text(INSTRUCTION_HEADER + "".join(instruction_lines), encoding="utf-8")
    callsites.write_text(
        INSTRUCTION_HEADER
        + "".join(
            f"{target}\t{target}\tTARGET\t0\t{target}\t00400000\tCaller\t{mnemonic}\t{operand}\te8\tUNCONDITIONAL_CALL\n"
            for target, mnemonic, operand in probe.CALLSITE_EVIDENCE
        ),
        encoding="utf-8",
    )
    (caller_decompile / "callers.c").write_text(
        "CUnit__Init "
        "CDestructableSegmentsController__Init "
        "CDestructableSegmentsController__ProcessNode "
        "CDestructableSegmentsController__CreateSegment "
        "CDestructableSegmentsController__FindSegmentByName\n",
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
        "caller_decompile": caller_decompile,
    }


class DestructableControllerTailSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_saved_destructable_controller_tail_tranche(self) -> None:
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
                callsite_instructions_path=paths["callsites"],
                decompile_dir=paths["decompile"],
                caller_decompile_dir=paths["caller_decompile"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], 8)
        self.assertEqual(report["summary"]["retEvidenceHits"], 8)
        self.assertEqual(report["summary"]["callsiteEvidenceHits"], 10)
        self.assertEqual(report["summary"]["commentOverclaims"], 0)

    def test_fails_for_stale_signature_or_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale=True, overclaim=True)
            report = probe.build_report(
                root=paths["root"],
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                tags_path=paths["tags"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
                callsite_instructions_path=paths["callsites"],
                decompile_dir=paths["decompile"],
                caller_decompile_dir=paths["caller_decompile"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("signature mismatch" in failure or "stale" in failure for failure in report["failures"]))
        self.assertTrue(any("overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
