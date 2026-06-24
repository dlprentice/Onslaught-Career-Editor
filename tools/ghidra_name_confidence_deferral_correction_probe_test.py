#!/usr/bin/env python3
"""Tests for the Ghidra name-confidence deferral correction probe."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import ghidra_name_confidence_deferral_correction_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def write_minimal_readback(root: Path, *, stale_name: bool = False) -> None:
    decompile = root / "decompile"
    decompile.mkdir()
    metadata_rows = []
    index_rows = []
    xref_rows = []
    instruction_rows = []
    for address, rule in probe.RULES.items():
        name = "CCockpit_Unk_00411e70__Wrapper_00412830" if stale_name and address == "0x00412830" else rule["newName"]
        signature = (
            f"undefined {name}(void)"
            if address in probe.CREATED_FUNCTIONS
            else f"void __thiscall {name}(void * this, void * param_1, void * param_2)"
        )
        comment = "Proof-boundary: signature/types/source identity/runtime behavior remain provisional."
        if address == "0x00412830":
            comment = "Corrected from the stale CCockpit wrapper owner. " + comment
        metadata_rows.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        index_rows.append(f"{address}\t{name}\t{signature}\tOK\n")
        (decompile / f"{address[2:]}_{name}.c").write_text(" ".join(rule["tokens"]), encoding="utf-8")
        for xref in rule["expectedXrefs"]:
            xref_rows.append(
                f"{address[2:]}\t{name}\t{xref['from_addr']}\t{xref['from_function_addr']}\t{xref['from_function']}\t{xref['ref_type']}\n"
            )
        instruction_rows.append(
            f"{address}\t{address}\tTARGET\t0\t{address}\t{address}\t{name}\tNOP\t\t90\tFALL_THROUGH\n"
        )

    (root / "metadata.tsv").write_text(METADATA_HEADER + "".join(metadata_rows), encoding="utf-8")
    (decompile / "index.tsv").write_text(INDEX_HEADER + "".join(index_rows), encoding="utf-8")
    (root / "xrefs.tsv").write_text(XREF_HEADER + "".join(xref_rows), encoding="utf-8")
    (root / "instructions.tsv").write_text(INSTRUCTION_HEADER + "".join(instruction_rows), encoding="utf-8")
    (root / "create_dry.tsv").write_text(
        "address\tstatus\tname\tsignature\tnote\n"
        "0040dc30\twould_create\t\t\tdry-run would disassemble+create and name CExplosionInitThing__EnableVolumeEntryGroupsByName\n"
        "0040dc60\twould_create\t\t\tdry-run would disassemble+create and name CExplosionInitThing__DisableVolumeEntryGroupsByNameAndReselect\n",
        encoding="utf-8",
    )
    (root / "create_apply.tsv").write_text(
        "address\tstatus\tname\tsignature\tnote\n"
        "0040dc30\tcreated\tCExplosionInitThing__EnableVolumeEntryGroupsByName\tundefined CExplosionInitThing__EnableVolumeEntryGroupsByName(void)\tdisassemble+create succeeded; renamed\n"
        "0040dc60\tcreated\tCExplosionInitThing__DisableVolumeEntryGroupsByNameAndReselect\tundefined CExplosionInitThing__DisableVolumeEntryGroupsByNameAndReselect(void)\tdisassemble+create succeeded; renamed\n",
        encoding="utf-8",
    )
    (root / "queue.json").write_text(
        json.dumps(
            {
                "status": "PASS",
                "totalFunctions": 5865,
                "qualitySignals": {
                    "commentlessFunctionCount": 5495,
                    "undefinedSignatureCount": 2089,
                    "paramSignatureCount": 2563,
                    "uncertainOwnerNameCount": 3,
                    "helperAddressNameCount": 0,
                    "wrapperAddressNameCount": 4,
                },
                "priorityQueues": {
                    "nameConfidence": [
                        {"address": "0x00402dd0", "name": "CHeightField_Unk_0047eb80__Wrapper_00402dd0"},
                        {"address": "0x0040dda0", "name": "CUnitAI_Unk_0044c720__Wrapper_0040dda0"},
                        {"address": "0x00413660", "name": "CGeneralVolume_Unk_00409e60__Wrapper_00413660"},
                        {"address": "0x00418090", "name": "FindAnimationIndex__Wrapper_00418090"},
                    ]
                },
            }
        ),
        encoding="utf-8",
    )


class GhidraNameConfidenceDeferralCorrectionProbeTests(unittest.TestCase):
    def test_accepts_boundary_and_owner_correction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_readback(root)

            report = probe.build_report(
                metadata_path=root / "metadata.tsv",
                decompile_index_path=root / "decompile" / "index.tsv",
                decompile_dir=root / "decompile",
                xrefs_path=root / "xrefs.tsv",
                instructions_path=root / "instructions.tsv",
                create_dry_path=root / "create_dry.tsv",
                create_apply_path=root / "create_apply.tsv",
                queue_path=root / "queue.json",
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["createdFunctionCount"], 2)
        self.assertEqual(report["correctedRenameCount"], 1)
        self.assertEqual(report["queue"]["qualitySignals"]["wrapperAddressNameCount"], 4)

    def test_fails_when_stale_cockpit_owner_survives(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_readback(root, stale_name=True)

            report = probe.build_report(
                metadata_path=root / "metadata.tsv",
                decompile_index_path=root / "decompile" / "index.tsv",
                decompile_dir=root / "decompile",
                xrefs_path=root / "xrefs.tsv",
                instructions_path=root / "instructions.tsv",
                create_dry_path=root / "create_dry.tsv",
                create_apply_path=root / "create_apply.tsv",
                queue_path=root / "queue.json",
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("0x00412830" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
