#!/usr/bin/env python3
"""Tests for the early-queue Ghidra signature/comment correction probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_early_queue_signature_correction_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def signature_for(target: dict[str, object]) -> str:
    return " ".join(str(token) for token in target["signature"])


def write_fixture(root: Path, *, stale_signature: bool = False, duplicate_particle_name: bool = False) -> dict[str, Path]:
    dry_log = root / "signature_correction_dry.log"
    apply_log = root / "signature_correction_apply.log"
    metadata = root / "metadata_final.tsv"
    decompile = root / "decompile_final"
    xrefs = root / "xrefs_final.tsv"
    instructions = root / "instructions_final.tsv"
    decompile.mkdir()

    target_count = len(probe.TARGETS)
    dry_log.write_text(
        f"Mode: dry\n--- SUMMARY ---\nupdated=0 skipped={target_count} renamed=0 missing=0 bad=0\n",
        encoding="utf-8",
    )
    apply_log.write_text(
        f"Mode: apply\n--- SUMMARY ---\nupdated={target_count} skipped=0 renamed=1 missing=0 bad=0\n",
        encoding="utf-8",
    )

    metadata_rows = []
    index_rows = []
    xref_rows = [XREF_HEADER]
    instruction_rows = [INSTRUCTION_HEADER]
    for index, (address, target) in enumerate(probe.TARGETS.items()):
        name = str(target["name"])
        if duplicate_particle_name and address == "0x00405d80":
            name = "CParticleManager__RemoveFromGlobalList"
        signature = signature_for(target)
        if stale_signature and address == "0x00406da0":
            signature = "int CBattleEngine__SelectNearestForwardTargetFromGlobalSet(void)"
        comment = " ".join(str(token) for token in target["comment"])
        metadata_rows.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        index_rows.append(f"{address}\t{name}\t{signature}\tOK\n")
        (decompile / f"{address[2:]}_{name}.c").write_text(
            f"{name} {signature} " + " ".join(str(token) for token in target["decompile"]),
            encoding="utf-8",
        )
        xref_rows.append(f"{address[2:]}\t{name}\t0040{index:04x}\t0040{index:04x}\tCaller\tUNCONDITIONAL_CALL\n")
        instruction_rows.append(
            f"{address}\t{address}\tAFTER\t{index}\t{target['instruction'][0]}\t{address}\t{name}\t"
            f"{target['instruction'][1]}\t{target['instruction'][2] if len(target['instruction']) > 2 else ''}\t\tTERMINATOR\n"
        )

    metadata.write_text(METADATA_HEADER + "".join(metadata_rows), encoding="utf-8")
    (decompile / "index.tsv").write_text(INDEX_HEADER + "".join(index_rows), encoding="utf-8")
    xrefs.write_text("".join(xref_rows), encoding="utf-8")
    instructions.write_text("".join(instruction_rows), encoding="utf-8")
    return {
        "dry_log": dry_log,
        "apply_log": apply_log,
        "metadata": metadata,
        "decompile_index": decompile / "index.tsv",
        "decompile_dir": decompile,
        "xrefs": xrefs,
        "instructions": instructions,
    }


class EarlyQueueSignatureCorrectionProbeTests(unittest.TestCase):
    def test_passes_for_corrected_tranche(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                dry_log_path=paths["dry_log"],
                apply_log_path=paths["apply_log"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], len(probe.TARGETS))
        self.assertEqual(report["summary"]["renamedTargets"], 1)
        self.assertEqual(report["summary"]["weaponFiredStealthStatus"], "unresolved")

    def test_fails_for_stale_signature_or_duplicate_particle_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale_signature=True, duplicate_particle_name=True)
            report = probe.build_report(
                dry_log_path=paths["dry_log"],
                apply_log_path=paths["apply_log"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("signature token missing" in failure for failure in report["failures"]))
        self.assertTrue(any("share the same function name" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
