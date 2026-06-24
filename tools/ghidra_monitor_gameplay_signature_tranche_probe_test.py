#!/usr/bin/env python3
"""Tests for the monitor/gameplay Ghidra signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_monitor_gameplay_signature_tranche_probe as probe


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

    dry.write_text("--- SUMMARY ---\nupdated=0 skipped=6 missing=0 bad=0\n", encoding="utf-8")
    apply.write_text("--- SUMMARY ---\nupdated=6 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    names = {
        "0x00407940": "CGeneralVolume__RandomizeOffsets4B8_4C0",
        "0x00407a50": "CMonitor__UpdateCameraVectorsAndInput",
        "0x004080f0": "CGame__IsWalkerGroundedOrCollision",
        "0x00408120": "CUnitAI__IsState2AndBelowHeightDeltaThreshold_00408120",
        "0x00408150": "CUnit__ProcessStateSwapAndDeathChecks",
        "0x004081c0": "CMonitor__Process",
    }
    signatures = {
        "0x00407940": "void __thiscall CGeneralVolume__RandomizeOffsets4B8_4C0(void * this, float offsetRange)",
        "0x00407a50": "void __fastcall CMonitor__UpdateCameraVectorsAndInput(void * monitor)",
        "0x004080f0": "bool __fastcall CGame__IsWalkerGroundedOrCollision(void * battleEngine)",
        "0x00408120": "bool __fastcall CUnitAI__IsState2AndBelowHeightDeltaThreshold_00408120(void * unitAi)",
        "0x00408150": "void __fastcall CUnit__ProcessStateSwapAndDeathChecks(void * unit)",
        "0x004081c0": "void __fastcall CMonitor__Process(void * monitor)",
    }
    if stale_param:
        signatures["0x00407940"] = "void __thiscall CGeneralVolume__RandomizeOffsets4B8_4C0(void * this, int param_1, float param_2)"

    comments = {
        "0x00407940": "Signature hardening: ret 0x4 shows one offsetRange argument; body randomizes +0x4b8/+0x4bc/+0x4c0 offsets and resets +0x4c4. Exact volume layout and runtime behavior remain unproven.",
        "0x00407a50": "Signature hardening: monitor camera/input update copies +0x114 angles, uses grounded/height checks, mouse-look, orientation setup, and offset decay. Exact owner/layout and runtime behavior remain unproven.",
        "0x004080f0": "Signature hardening: bool grounded/collision predicate checks mode +0x260 and collision vcall or height delta. Exact source identity and runtime behavior remain unproven.",
        "0x00408120": "Signature hardening: bool state/timestamp predicate checks mode +0x260 and now-minus +0xcc threshold. Exact CUnitAI layout and runtime behavior remain unproven.",
        "0x00408150": "Signature hardening: unit state/death helper swaps part readers, checks death flag +0x2c&4, dispatches pickup/death paths, and resets +0xd0. Runtime behavior remain unproven.",
        "0x004081c0": "Signature hardening: large monitor process body covers active-reader expiry, tracked-list update, 0x5d8/0x5dc interpolation, vibration, cloak/fade timer decay, actor move, CMonitor__UpdateCameraVectorsAndInput, and target effects. Cloak activation/fire behavior and rebuild parity remain unproven.",
    }
    if overclaim:
        comments["0x004081c0"] += " Runtime cloak activation proven."

    metadata.write_text(
        METADATA_HEADER + "".join(f"{addr}\t{names[addr]}\t{signatures[addr]}\t{comments[addr]}\tOK\n" for addr in names),
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        INDEX_HEADER + "".join(f"{addr}\t{names[addr]}\t{signatures[addr]}\tOK\n" for addr in names),
        encoding="utf-8",
    )
    decompile_tokens = {
        "0x00407940": "offsetRange Random__NextLCGAbs +0x4b8 +0x4bc +0x4c0 +0x4c4 CGeneralVolume__InitRandomizedVelocityOffsets",
        "0x00407a50": "monitor CGame__UpdateMouseLookAngles CSquadNormal__BuildOrientationMatrixFromEuler HeightDelta__Below015_D4 +0x114 +0x590",
        "0x004080f0": "battleEngine HeightDelta__Below015_D4 +0x260 return true return false",
        "0x00408120": "unitAi DAT_00672fd0 +0xcc +0x260 return true return false",
        "0x00408150": "unit CBattleEngine__SwapPrimarySecondaryPartReadersForState CGeneralVolume__SpawnPickupAndDispatch CUnit__ResetFieldD0ToGlobalThreshold +0x2c",
        "0x004081c0": "monitor CMonitor__UpdateCameraVectorsAndInput CActor__Move CBattleEngine__UpdateAutoAim +0x5d8 +0x5dc +0x4ac +0xfc",
    }
    for addr, name in names.items():
        (decompile / f"{addr[2:]}_{name}.c").write_text(
            f"{name} {signatures[addr]} {decompile_tokens[addr]}",
            encoding="utf-8",
        )
    xrefs.write_text(
        XREF_HEADER
        + "00407940\tCGeneralVolume__RandomizeOffsets4B8_4C0\t0040c355\t0040c340\tCEngine__RandomizeBurstOffsetsAndAccumulateRange\tUNCONDITIONAL_CALL\n"
        + "00407a50\tCMonitor__UpdateCameraVectorsAndInput\t004095d1\t004081c0\tCMonitor__Process\tUNCONDITIONAL_CALL\n"
        + "004080f0\tCGame__IsWalkerGroundedOrCollision\t0046eb8d\t0046e910\tCGame__Update\tUNCONDITIONAL_CALL\n"
        + "00408120\tCUnitAI__IsState2AndBelowHeightDeltaThreshold_00408120\t00413760\t00413760\tCMonitor__ProcessTrackingAndSurfaceAlignment\tUNCONDITIONAL_CALL\n"
        + "00408150\tCUnit__ProcessStateSwapAndDeathChecks\t005d8ad8\t<none>\t<no_function>\tDATA\n"
        + "004081c0\tCMonitor__Process\t005d8acc\t<none>\t<no_function>\tDATA\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x00407940\t0x00407940\tAFTER\t96\t0x00407a40\t0x00407940\tCGeneralVolume__RandomizeOffsets4B8_4C0\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x00407a50\t0x00407a50\tAFTER\t96\t0x004080ee\t0x00407a50\tCMonitor__UpdateCameraVectorsAndInput\tRET\t\tc3\tTERMINATOR\n"
        + "0x004080f0\t0x004080f0\tAFTER\t20\t0x0040811f\t0x004080f0\tCGame__IsWalkerGroundedOrCollision\tRET\t\tc3\tTERMINATOR\n"
        + "0x00408120\t0x00408120\tAFTER\t16\t0x0040814f\t0x00408120\tCUnitAI__IsState2AndBelowHeightDeltaThreshold_00408120\tRET\t\tc3\tTERMINATOR\n"
        + "0x00408150\t0x00408150\tAFTER\t24\t0x004081b0\t0x00408150\tCUnit__ProcessStateSwapAndDeathChecks\tRET\t\tc3\tTERMINATOR\n",
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


class MonitorGameplaySignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_corrected_monitor_gameplay_targets(self) -> None:
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
        self.assertEqual(report["summary"]["targets"], 6)
        self.assertEqual(report["summary"]["paramSignatureHits"], 0)
        self.assertEqual(report["summary"]["commentOverclaims"], 0)
        self.assertGreaterEqual(report["summary"]["retEvidenceHits"], 4)

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
