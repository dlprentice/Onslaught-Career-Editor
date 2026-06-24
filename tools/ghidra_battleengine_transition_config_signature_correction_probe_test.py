#!/usr/bin/env python3
"""Tests for the BattleEngine transition/config Ghidra correction probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_battleengine_transition_config_signature_correction_probe as probe


TARGET_ROWS = {
    "0x0040eeb0": {
        "name": "CBattleEngine__FinishedPlayingCurrentAnimation",
        "signature": "int __thiscall CBattleEngine__FinishedPlayingCurrentAnimation(void * this)",
        "comment": (
            "CBattleEngine::FinishedPlayingCurrentAnimation source-parity correction: checks the current "
            "render animation against flytowalk/walktofly transition mode indices and switches to walk/fly "
            "animation when a transition finishes. Corrects the prior CUnit owner label; runtime animation "
            "behavior and concrete CBattleEngine layout remain unproven."
        ),
        "decompile": "CBattleEngine__FinishedPlayingCurrentAnimation this flytowalk walktofly PlayAnimationByNameIfPresent",
    },
    "0x0040ef20": {
        "name": "CBattleEngine__GroundParticleEffect",
        "signature": "void __thiscall CBattleEngine__GroundParticleEffect(void * this)",
        "comment": (
            "CBattleEngine::GroundParticleEffect source-parity correction: samples water/terrain height, "
            "spawns the land or water ground-effect particle when altitude is below the source threshold, "
            "and positions the particle from this+0x1c..0x28. Corrects the prior CMonitor helper/effect "
            "label; runtime particle behavior and concrete CBattleEngine layout remain unproven."
        ),
        "decompile": "CBattleEngine__GroundParticleEffect this CStaticShadows__SampleShadowHeightBilinear CParticleManager__CreateEffect 0x1c 0x24",
    },
    "0x0040f110": {
        "name": "CEngine__ClampBurstStartTimeFloorNow",
        "signature": "void __thiscall CEngine__ClampBurstStartTimeFloorNow(void * this)",
        "comment": (
            "Signature/comment hardening: clamps the burst/progress timestamp field at this+0x60c up to "
            "the current event-time global when the stored value plus the small floor constant is behind "
            "now. Exact owner field layout and runtime burst behavior remain unproven."
        ),
        "decompile": "CEngine__ClampBurstStartTimeFloorNow this 0x60c 005d85bc 00672fd0",
    },
    "0x0040f2f0": {
        "name": "BattleEngineConfigurations__GetConfiguration",
        "signature": "void * __cdecl BattleEngineConfigurations__GetConfiguration(int configurationId)",
        "comment": (
            "UBattleEngineConfigurations::GetConfiguration source-parity correction: bounds-checks "
            "configurationId against the global configuration count, selects a name from the global name "
            "table, asks UBattleEngineDataManager for that configuration, and falls back to index 0. "
            "Corrects the prior CBattleEngine weapon-profile label; concrete CBattleEngineData layout "
            "and runtime configuration coverage remain unproven."
        ),
        "decompile": "BattleEngineConfigurations__GetConfiguration configurationId 00660250 00660200 006602a0 0xa8",
    },
}


def write_fixture(root: Path, *, stale: bool = False, overclaim: bool = False) -> dict[str, Path]:
    signature_dry = root / "signature_dry.log"
    signature_apply = root / "signature_apply.log"
    metadata = root / "metadata_final.tsv"
    decompile = root / "decompile_final"
    xrefs = root / "xrefs_final.tsv"
    instructions = root / "instructions_final.tsv"
    decompile.mkdir()

    signature_dry.write_text("--- SUMMARY ---\nupdated=0 skipped=4 missing=0 bad=0\n", encoding="utf-8")
    signature_apply.write_text("--- SUMMARY ---\nupdated=4 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    rows = {address: dict(row) for address, row in TARGET_ROWS.items()}
    if stale:
        rows["0x0040eeb0"]["name"] = "CUnit__FinishedPlayingCurrentAnimation"
        rows["0x0040ef20"]["name"] = "CMonitor__SpawnGroundOrAirImpactEffect"
        rows["0x0040f2f0"]["name"] = "CBattleEngine__GetWeaponProfileByIndex"
        rows["0x0040f110"]["signature"] = "void __fastcall CEngine__ClampBurstStartTimeFloorNow(int param_1)"
    if overclaim:
        rows["0x0040ef20"]["comment"] += " This proves runtime particle behavior."

    metadata.write_text(
        "address\tname\tsignature\tcomment\tstatus\n"
        + "".join(
            f"{address}\t{row['name']}\t{row['signature']}\t{row['comment']}\tOK\n"
            for address, row in rows.items()
        ),
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        "address\tname\tsignature\tstatus\n"
        + "".join(f"{address}\t{row['name']}\t{row['signature']}\tOK\n" for address, row in rows.items()),
        encoding="utf-8",
    )
    for address, row in rows.items():
        text = f"{row['signature']} {row['decompile']}"
        if stale:
            text += " CUnit__FinishedPlayingCurrentAnimation CMonitor__SpawnGroundOrAirImpactEffect CBattleEngine__GetWeaponProfileByIndex param_1"
        (decompile / f"{address[2:]}_{row['name']}.c").write_text(text, encoding="utf-8")
    xrefs.write_text(
        "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
        + "".join(f"{address[2:]}\t{row['name']}\t00401000\t00401000\tCaller\tDATA\n" for address, row in rows.items()),
        encoding="utf-8",
    )
    instructions.write_text(
        "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
        + "".join(
            f"{address}\t{address}\tAFTER\t1\t{address}\t{address}\t{row['name']}\tRET\t\tc3\tTERMINATOR\n"
            for address, row in rows.items()
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


class BattleEngineTransitionConfigSignatureCorrectionProbeTests(unittest.TestCase):
    def test_passes_for_corrected_transition_config_tranche(self) -> None:
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
        self.assertEqual(report["summary"]["correctedTargets"], 4)
        self.assertEqual(report["summary"]["staleTokenHits"], 0)

    def test_fails_for_stale_names_signatures_or_overclaims(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale=True, overclaim=True)
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
        self.assertTrue(any("name mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("signature tokens missing" in failure for failure in report["failures"]))
        self.assertTrue(any("stale token" in failure for failure in report["failures"]))
        self.assertTrue(any("overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
