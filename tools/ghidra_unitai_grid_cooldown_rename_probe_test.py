#!/usr/bin/env python3
"""Tests for the CUnitAI grid-cooldown Ghidra rename read-back probe."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import ghidra_unitai_grid_cooldown_rename_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def write_minimal_readback(root: Path, *, stale_name: bool = False) -> None:
    decompile = root / "decompile"
    caller_decompile = root / "caller_decompile"
    decompile.mkdir()
    caller_decompile.mkdir()

    name = probe.NEW_NAME
    if stale_name:
        name = probe.OLD_NAME

    signature = f"void __fastcall {name}(void * param_1)"
    comment = (
        "CUnitAI grid cooldown refresh. Caller evidence uses param_1+0x50 and +0x2e8. "
        "Proof-boundary: signature, tags, exact source identity, and runtime behavior remain provisional."
    )
    (root / "metadata.tsv").write_text(
        METADATA_HEADER + f"{probe.ADDRESS}\t{name}\t{signature}\t{comment}\tOK\n",
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        INDEX_HEADER + f"{probe.ADDRESS}\t{name}\t{signature}\tOK\n",
        encoding="utf-8",
    )
    (decompile / f"{probe.ADDRESS[2:]}_{name}.c").write_text(
        " ".join([name, *probe.DECOMPILE_TOKENS]), encoding="utf-8"
    )
    (root / "xrefs.tsv").write_text(
        XREF_HEADER
        + f"{probe.ADDRESS[2:]}\t{name}\t004862af\t00485d50\tCExplosionInitThing__RenderObjectiveStatusPanel\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    (root / "instructions.tsv").write_text(
        INSTRUCTION_HEADER
        + f"{probe.ADDRESS}\t{probe.ADDRESS}\tTARGET\t0\t{probe.ADDRESS}\t{probe.ADDRESS}\t{name}\tCALL\t{name}\t00\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    (caller_decompile / "index.tsv").write_text(
        INDEX_HEADER
        + "0x00485d50\tCExplosionInitThing__RenderObjectiveStatusPanel\tvoid __fastcall CExplosionInitThing__RenderObjectiveStatusPanel(int param_1)\tOK\n",
        encoding="utf-8",
    )
    (caller_decompile / "00485d50_CExplosionInitThing__RenderObjectiveStatusPanel.c").write_text(
        f"{name}(*(void **)(param_1 + 0x50)); "
        "DAT_00672fd0 - *(float *)(*(int *)(param_1 + 0x50) + 0x2e8);",
        encoding="utf-8",
    )
    (root / "queue.json").write_text(
        json.dumps(
            {
                "status": "PASS",
                "qualitySignals": {
                    "uncertainOwnerNameCount": 1,
                    "wrapperAddressNameCount": 2,
                    "helperAddressNameCount": 0,
                },
            }
        ),
        encoding="utf-8",
    )


class GhidraUnitaiGridCooldownRenameProbeTests(unittest.TestCase):
    def test_accepts_saved_unitai_grid_cooldown_rename(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_readback(root)

            report = probe.build_report(
                metadata_path=root / "metadata.tsv",
                decompile_index_path=root / "decompile" / "index.tsv",
                decompile_dir=root / "decompile",
                xrefs_path=root / "xrefs.tsv",
                instructions_path=root / "instructions.tsv",
                caller_index_path=root / "caller_decompile" / "index.tsv",
                caller_decompile_dir=root / "caller_decompile",
                queue_report_path=root / "queue.json",
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["newName"], probe.NEW_NAME)
        self.assertEqual(report["queueSignals"]["wrapperAddressNameCount"], 2)
        self.assertEqual(report["queueSignals"]["uncertainOwnerNameCount"], 1)

    def test_fails_when_stale_name_survives(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_readback(root, stale_name=True)

            report = probe.build_report(
                metadata_path=root / "metadata.tsv",
                decompile_index_path=root / "decompile" / "index.tsv",
                decompile_dir=root / "decompile",
                xrefs_path=root / "xrefs.tsv",
                instructions_path=root / "instructions.tsv",
                caller_index_path=root / "caller_decompile" / "index.tsv",
                caller_decompile_dir=root / "caller_decompile",
                queue_report_path=root / "queue.json",
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any(probe.ADDRESS in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
