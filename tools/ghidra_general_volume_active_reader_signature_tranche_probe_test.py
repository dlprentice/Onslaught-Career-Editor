#!/usr/bin/env python3
"""Tests for the GeneralVolume active-reader signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_general_volume_active_reader_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"


def write_fixture(root: Path, *, stale_param: bool = False, overclaim: bool = False) -> dict[str, Path]:
    dry = root / "signature_dry.log"
    apply = root / "signature_apply.log"
    metadata = root / "metadata_final.tsv"
    decompile = root / "decompile_final"
    xrefs = root / "xrefs_final.tsv"
    instructions = root / "instructions_final.tsv"
    decompile.mkdir()

    dry.write_text("--- SUMMARY ---\nupdated=0 skipped=2 missing=0 bad=0\n", encoding="utf-8")
    apply.write_text("--- SUMMARY ---\nupdated=2 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    names = {
        "0x00402020": "CGeneralVolume__ResetCooldownTimestamp",
        "0x0040c720": "CGeneralVolume__ResetAndSetActiveReader",
    }
    signatures = {
        "0x00402020": "void __thiscall CGeneralVolume__ResetCooldownTimestamp(void * this, void * activeReaderTarget)",
        "0x0040c720": "void __thiscall CGeneralVolume__ResetAndSetActiveReader(void * this, void * activeReaderTarget)",
    }
    if stale_param:
        signatures["0x0040c720"] = "void __thiscall CGeneralVolume__ResetAndSetActiveReader(void * this, int param_1, void * param_2)"

    comments = {
        "0x00402020": "Signature correction: instruction evidence shows ret 0x4 and one activeReaderTarget stack argument; body ignores the argument and stores DAT_00672fd0 into this+0xd4. Runtime behavior remain unproven.",
        "0x0040c720": "Signature correction: ret 0x4 shows one activeReaderTarget stack argument; body swaps reader state, binds this+0x264 through CGenericActiveReader__SetReader, then calls CGeneralVolume__ResetCooldownTimestamp with the same target. Runtime behavior remain unproven.",
    }
    if overclaim:
        comments["0x0040c720"] += " Runtime behavior proven."

    metadata.write_text(
        METADATA_HEADER + "".join(f"{addr}\t{names[addr]}\t{signatures[addr]}\t{comments[addr]}\tOK\n" for addr in names),
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        INDEX_HEADER + "".join(f"{addr}\t{names[addr]}\t{signatures[addr]}\tOK\n" for addr in names),
        encoding="utf-8",
    )
    decompile_tokens = {
        "0x00402020": "activeReaderTarget DAT_00672fd0 this + 0xd4",
        "0x0040c720": "activeReaderTarget CBattleEngine__SwapPrimarySecondaryPartReadersForState this + 0x264 CGenericActiveReader__SetReader CGeneralVolume__ResetCooldownTimestamp",
    }
    for addr, name in names.items():
        (decompile / f"{addr[2:]}_{name}.c").write_text(
            f"{name} {signatures[addr]} {decompile_tokens[addr]}",
            encoding="utf-8",
        )
    xrefs.write_text(
        XREF_HEADER
        + "00402020\tCGeneralVolume__ResetCooldownTimestamp\t0040c73c\t0040c720\tCGeneralVolume__ResetAndSetActiveReader\tUNCONDITIONAL_CALL\n"
        + "0040c720\tCGeneralVolume__ResetAndSetActiveReader\t005d8adc\t<none>\t<no_function>\tDATA\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x00402020\t0x00402020\tAFTER\t2\t0x0040202b\t0x00402020\tCGeneralVolume__ResetCooldownTimestamp\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x0040c720\t0x0040c720\tAFTER\t13\t0x0040c743\t0x0040c720\tCGeneralVolume__ResetAndSetActiveReader\tRET\t0x4\tc2 04 00\tTERMINATOR\n",
        encoding="utf-8",
    )
    return {
        "dry": dry,
        "apply": apply,
        "metadata": metadata,
        "decompile_index": decompile / "index.tsv",
        "decompile_dir": decompile,
        "xrefs": xrefs,
        "instructions": instructions,
    }


class GeneralVolumeActiveReaderSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_corrected_active_reader_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], 2)
        self.assertEqual(report["summary"]["paramSignatureHits"], 0)
        self.assertEqual(report["summary"]["commentOverclaims"], 0)
        self.assertEqual(report["summary"]["retEvidenceHits"], 2)

    def test_fails_for_stale_param_signature_or_runtime_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale_param=True, overclaim=True)
            report = probe.build_report(
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("param_N signature remains" in failure for failure in report["failures"]))
        self.assertTrue(any("runtime/source overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
