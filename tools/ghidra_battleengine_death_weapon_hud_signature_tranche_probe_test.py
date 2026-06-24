#!/usr/bin/env python3
"""Tests for the BattleEngine death/weapon HUD Ghidra signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_battleengine_death_weapon_hud_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def write_fixture(root: Path, *, stale_owner: bool = False, overclaim: bool = False) -> dict[str, Path]:
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
        if stale_owner and address == "0x0040c3a0":
            name = expected["previous"]
        signature = " ".join(expected["signatureTokens"])
        comment = " ".join(expected["commentTokens"])
        if overclaim and address == "0x0040c3c0":
            comment += " runtime HUD behavior proven"
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
        + "0040bfd0\tCBattleEngine__StartDieProcess\t005d8a8c\t<none>\t<no_function>\tDATA\n"
        + "0040c2e0\tCBattleEngine__CanSpawnBurstForResolvedEntry\t00506a1f\t005069f0\tCEngine__SpawnProjectileBurstFromCurrentPreset\tUNCONDITIONAL_CALL\n"
        + "0040c340\tCBattleEngine__RandomizeBurstOffsetsAndAccumulateRange\t00507871\t005069f0\tCEngine__SpawnProjectileBurstFromCurrentPreset\tUNCONDITIONAL_CALL\n"
        + "0040c3a0\tCBattleEngine__IsEnergyWeapon\t00486af5\t00486940\tCExplosionInitThing__RenderObjectiveSlotFillPanel\tUNCONDITIONAL_CALL\n"
        + "0040c3c0\tCBattleEngine__GetWeaponAmmoPercentage\t00486a89\t00486940\tCExplosionInitThing__RenderObjectiveSlotFillPanel\tUNCONDITIONAL_CALL\n"
        + "0040c460\tCBattleEngine__GetWeaponAmmoCount\t00486d56\t00486940\tCExplosionInitThing__RenderObjectiveSlotFillPanel\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "".join(
            f"{address}\t{address}\tTARGET\t0\t{address}\t{address}\t{expected['name']}\tMOV\tECX, ESI\t8b ce\tFALL_THROUGH\n"
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


class BattleEngineDeathWeaponHudSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_renamed_signatures_and_comments(self) -> None:
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
        self.assertEqual(report["summary"]["renamedTargets"], 5)

    def test_fails_for_stale_owner_or_runtime_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale_owner=True, overclaim=True)
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
