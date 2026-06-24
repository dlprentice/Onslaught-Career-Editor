#!/usr/bin/env python3
"""Tests for the BattleEngine cloak/HUD/interpolation Ghidra tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_battleengine_cloak_hud_interpolation_signature_tranche_probe as probe


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

    target_count = len(probe.TARGETS)
    signature_dry.write_text(f"--- SUMMARY ---\nupdated=0 skipped={target_count} missing=0 bad=0\n", encoding="utf-8")
    signature_apply.write_text(f"--- SUMMARY ---\nupdated={target_count} skipped=0 missing=0 bad=0\n", encoding="utf-8")

    rows = []
    index_rows = []
    for address, expected in probe.TARGETS.items():
        name = expected["name"]
        if stale_name and address == "0x0040d4d0":
            name = expected["previous"]
        signature = " ".join(expected["signatureTokens"])
        comment = " ".join(expected["commentTokens"])
        if overclaim and address == "0x0040d4d0":
            comment += " runtime cloak activation proven"
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
        + "0040d4d0\tCBattleEngine__HandleCloak\t004d32e2\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n"
        + "0040d5b0\tCLockInfo__GetLockPercentage\t00486fd5\t00486e00\tCExplosionInitThing__RenderWorldTargetSprites\tUNCONDITIONAL_CALL\n"
        + "0040d5f0\tCBattleEngine__PlayHudSampleByName\t0040a4a7\t00409f70\tCBattleEngine__ChangeWeapon\tUNCONDITIONAL_CALL\n"
        + "0040d660\tCBattleEngine__GetInterpolatedEulerOrientation\t00484ccb\t00484c50\tCExplosionInitThing__RenderTacticalRadarContacts\tUNCONDITIONAL_CALL\n"
        + "0040d660\tCBattleEngine__GetInterpolatedEulerOrientation\t004273bf\t00427210\tCDXCompass__Render\tUNCONDITIONAL_CALL\n"
        + "0040d7c0\tCBattleEngine__GetInterpolatedAutoAimPos\t00484458\t00484340\tCExplosionInitThing__RenderTargetMarkers3D\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "".join(
            f"{address}\t{address}\tTARGET\t0\t{address}\t{address}\t{expected['name']}\tMOV\tECX, dword ptr [ECX + 0x574]\t8b 89 74 05 00 00\tFALL_THROUGH\n"
            for address, expected in probe.TARGETS.items()
        ),
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


class BattleEngineCloakHudInterpolationSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_corrected_signatures(self) -> None:
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
        self.assertEqual(report["summary"]["targets"], len(probe.TARGETS))
        self.assertEqual(report["summary"]["renamedTargets"], len(probe.TARGETS))

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
