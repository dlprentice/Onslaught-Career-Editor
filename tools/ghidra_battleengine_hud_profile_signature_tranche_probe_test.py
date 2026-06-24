#!/usr/bin/env python3
"""Tests for the BattleEngine HUD/profile Ghidra signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_battleengine_hud_profile_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def write_fixture(root: Path, *, stale_name: bool = False, overclaim: bool = False) -> dict[str, Path]:
    signature_dry = root / "signature_dry.log"
    signature_apply = root / "signature_apply.log"
    metadata = root / "metadata_readback.tsv"
    decompile = root / "decompile_readback"
    xrefs = root / "xrefs_readback.tsv"
    instructions = root / "instructions_readback.tsv"
    decompile.mkdir()

    signature_dry.write_text("--- SUMMARY ---\nupdated=0 skipped=6 missing=0 bad=0\n", encoding="utf-8")
    signature_apply.write_text("--- SUMMARY ---\nupdated=6 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    rows = []
    index_rows = []
    for address, expected in probe.TARGETS.items():
        name = expected["name"]
        if stale_name and address == "0x0040c650":
            name = expected["previous"]
        signature = " ".join(expected["signatureTokens"])
        comment = " ".join(expected["commentTokens"])
        if overclaim and address == "0x0040c4a0":
            comment += " runtime weapon charge proven"
        rows.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        index_rows.append(f"{address}\t{name}\t{signature}\tOK\n")
        (decompile / f"{address[2:]}_{name}.c").write_text(
            f"{name} {' '.join(expected['decompileTokens'])}",
            encoding="utf-8",
        )

    metadata.write_text(METADATA_HEADER + "".join(rows), encoding="utf-8")
    (decompile / "index.tsv").write_text(INDEX_HEADER + "".join(index_rows), encoding="utf-8")
    xrefs.write_text(
        XREF_HEADER
        + "0040c480\tCBattleEngine__IsWeaponOverheated\t0048695e\t00486940\tCExplosionInitThing__RenderObjectiveSlotFillPanel\tUNCONDITIONAL_CALL\n"
        + "0040c4a0\tCBattleEngine__GetWeaponCharge\t00485b34\t004858d0\tCExplosionInitThing__RenderObjectiveProgressGaugeAndHeadingNeedle\tUNCONDITIONAL_CALL\n"
        + "0040c550\tCBattleEngine__GetWeaponName\t00486069\t00485d50\tCExplosionInitThing__RenderObjectiveStatusPanel\tUNCONDITIONAL_CALL\n"
        + "0040c570\tCBattleEngine__GetWeaponPhysicsName\t005356bd\t00535670\tIScript__GetThingName\tUNCONDITIONAL_CALL\n"
        + "0040c590\tCBattleEngine__GetWeaponIconName\t00485ed9\t00485d50\tCExplosionInitThing__RenderObjectiveStatusPanel\tUNCONDITIONAL_CALL\n"
        + "0040c650\tCBattleEngine__UpdateConfiguration\t00404f7e\t00404dd0\tCBattleEngine__Init\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "".join(
            f"{address}\t{address}\tTARGET\t0\t{address}\t{address}\t{expected['name']}\tMOV\tECX, dword ptr [ECX + 0x578]\t8b 89 78 05 00 00\tFALL_THROUGH\n"
            for address, expected in probe.TARGETS.items()
        )
        + "0x0040c4a0\t0x0040c4a0\tAFTER\t1\t0x0040c51b\t0x0040c4a0\tCBattleEngine__GetWeaponCharge\tRET\t\tc3\tTERMINATOR\n",
        encoding="utf-8",
    )
    return {
        "signature_dry": signature_dry,
        "signature_apply": signature_apply,
        "metadata": metadata,
        "decompile_index": decompile / "index.tsv",
        "decompile_dir": decompile,
        "xrefs": xrefs,
        "instructions": instructions,
    }


class BattleEngineHudProfileSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_corrected_hud_profile_signatures(self) -> None:
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
        self.assertEqual(report["summary"]["renamedTargets"], 6)

    def test_fails_for_stale_name_or_runtime_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale_name=True, overclaim=True)
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
        self.assertTrue(any("metadata name/status mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("runtime/source overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
