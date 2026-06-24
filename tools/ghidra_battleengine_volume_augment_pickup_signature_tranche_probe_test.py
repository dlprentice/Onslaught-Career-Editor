#!/usr/bin/env python3
"""Tests for the BattleEngine volume/augment/pickup signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_battleengine_volume_augment_pickup_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def write_fixture(root: Path, *, stale_signature: bool = False, overclaim: bool = False) -> dict[str, Path]:
    signature_dry = root / "signature_dry.log"
    signature_apply = root / "signature_apply.log"
    metadata = root / "metadata_readback.tsv"
    decompile = root / "decompile_readback"
    xrefs = root / "xrefs_readback.tsv"
    instructions = root / "instructions_readback.tsv"
    decompile.mkdir()

    signature_dry.write_text("--- SUMMARY ---\nupdated=0 skipped=6 missing=0 bad=0\n", encoding="utf-8")
    signature_apply.write_text("--- SUMMARY ---\nupdated=6 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    metadata_rows = []
    index_rows = []
    xref_rows = []
    instruction_rows = []
    for index, (address, expected) in enumerate(probe.TARGETS.items()):
        signature = " ".join(expected["signatureTokens"])
        if stale_signature and address == "0x0040de40":
            signature = signature.replace("void * this", "void * param_1")
        comment = " ".join(expected["commentTokens"])
        if overclaim and address == "0x0040dfb0":
            comment += " runtime behavior proven"

        metadata_rows.append(f"{address}\t{expected['name']}\t{signature}\t{comment}\tOK\n")
        index_rows.append(f"{address}\t{expected['name']}\t{signature}\tOK\n")
        (decompile / f"{probe.normalize_address(address)[2:]}_{expected['name']}.c").write_text(
            " ".join(expected["decompileTokens"]),
            encoding="utf-8",
        )
        xref_rows.append(
            f"{address}\t{expected['name']}\t{0x400000 + index:x}\t00400000\t"
            f"{' '.join(expected['xrefTokens'])}\tUNCONDITIONAL_CALL\n"
        )
        instruction_rows.append(
            f"{address}\t{address}\tTARGET\t0\t{address}\t{address}\t{expected['name']}\t"
            f"CALL\t{' '.join(expected['instructionTokens'])}\te8\tUNCONDITIONAL_CALL\n"
        )

    metadata.write_text(METADATA_HEADER + "".join(metadata_rows), encoding="utf-8")
    (decompile / "index.tsv").write_text(INDEX_HEADER + "".join(index_rows), encoding="utf-8")
    xrefs.write_text(XREF_HEADER + "".join(xref_rows), encoding="utf-8")
    instructions.write_text(INSTRUCTION_HEADER + "".join(instruction_rows), encoding="utf-8")

    return {
        "signature_dry": signature_dry,
        "signature_apply": signature_apply,
        "metadata": metadata,
        "decompile_index": decompile / "index.tsv",
        "decompile_dir": decompile,
        "xrefs": xrefs,
        "instructions": instructions,
    }


class BattleEngineVolumeAugmentPickupSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_expected_saved_signatures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                signature_dry_log_path=paths["signature_dry"],
                signature_apply_log_path=paths["signature_apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], 6)
        self.assertEqual(report["summary"]["correctedNames"], 4)
        self.assertEqual(report["summary"]["hardenedSignatures"], 6)

    def test_fails_for_stale_signature_or_runtime_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale_signature=True, overclaim=True)
            report = probe.build_report(
                signature_dry_log_path=paths["signature_dry"],
                signature_apply_log_path=paths["signature_apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("signature tokens missing" in failure for failure in report["failures"]))
        self.assertTrue(any("runtime/source overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
