#!/usr/bin/env python3
"""Tests for the BattleEngine D0-tail saved-Ghidra tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_battleengine_d0_tail_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)

TARGET_FIXTURES = {
    "0x0040d0f0": (
        "CWeaponStatement__UsesBallisticArcNoLocks",
        "int __thiscall CWeaponStatement__UsesBallisticArcNoLocks(void * weaponStatement)",
        "Owner/name correction for a weapon-definition ballistic gate: checks gravity and +0x50/+0x6c lock-style fields. This is not runtime weapon-fire or stealth proof.",
        "CWeaponStatement__UsesBallisticArcNoLocks + 0x3c + 0x50 + 0x6c",
    ),
    "0x0040d470": (
        "CLine__ctor_fromEndpoints",
        "void __thiscall CLine__ctor_fromEndpoints(void * this, void * startPoint, void * endPoint)",
        "Owner/name correction: constructor writes the CGeneralVolume base vtable, copies two 16-byte endpoint/vector blocks, then writes the CLine vtable. Runtime collision behavior remain unproven.",
        "CLine__ctor_fromEndpoints PTR_VFuncSlot_00_00426340_005d8bfc",
    ),
    "0x0040da30": (
        "CBattleEngine__BuildInterpolatedWorldTransform",
        "void * __thiscall CBattleEngine__BuildInterpolatedWorldTransform(void * this, void * outWorldTransform, void * unusedContext)",
        "Owner/name correction from the target-marker caller: builds an interpolated BattleEngine world transform into the output buffer. Static render-path evidence only; runtime render behavior remain unproven.",
        "CBattleEngine__BuildInterpolatedWorldTransform Vec3__SubtractToOut CSquadNormal__BuildOrientationMatrixFromEuler CMCBuggy__MultiplyMat34Basis",
    ),
    "0x0040dc90": (
        "CBattleEngine__CountFlag9CBySelectionMode",
        "int __thiscall CBattleEngine__CountFlag9CBySelectionMode(void * this)",
        "Owner/name correction: if +0x260 == 3, tail-calls LinkedObjectList__CountFlag9C on +0x57c; otherwise counts +0x578. This is not objective completion runtime proof.",
        "CBattleEngine__CountFlag9CBySelectionMode LinkedObjectList__CountFlag9C LinkedObjectList__CountFlag9C_IncludingExtra + 0x260 + 0x57c + 0x578",
    ),
    "0x0040dcb0": (
        "CBattleEngine__SetFlag58CEnabled",
        "void __thiscall CBattleEngine__SetFlag58CEnabled(void * this)",
        "Owner correction for a tiny BattleEngine setter: writes 1 to +0x58c, adjacent to the +0x260/+0x58c transition-selection context. Runtime behavior remain unproven.",
        "CBattleEngine__SetFlag58CEnabled + 0x58c = 1",
    ),
    "0x0040dce0": (
        "CBattleEngine__HostileEnvironment",
        "void __thiscall CBattleEngine__HostileEnvironment(void * this)",
        "Source bridge for CBattleEngine::HostileEnvironment: emits hud_hostile_environment/log context after the mLastTimeInHostileEnviroment throttle and updates the timestamp. Static evidence only; not runtime HUD audio proof.",
        "CBattleEngine__HostileEnvironment CBattleEngine__FindSoundEventByNameIfEnabled CMonitor__PlayRandomSampleFromChain CConsole__Printf + 0x510 DAT_00672fd0",
    ),
}


def write_fixture(root: Path, *, overclaim: bool = False, stale_signature: bool = False) -> dict[str, Path]:
    signature_dry = root / "signature_dry.log"
    signature_apply = root / "signature_apply.log"
    metadata = root / "metadata_readback.tsv"
    decompile = root / "decompile_readback"
    xrefs = root / "xrefs_readback.tsv"
    instructions = root / "instructions_readback.tsv"
    vtables = root / "vtable_types_pre.tsv"
    decompile.mkdir()

    signature_dry.write_text("--- SUMMARY ---\nupdated=0 skipped=6 missing=0 bad=0\n", encoding="utf-8")
    signature_apply.write_text("--- SUMMARY ---\nupdated=6 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    metadata_rows = []
    index_rows = []
    for address, (name, signature, comment, decompile_tokens) in TARGET_FIXTURES.items():
        if stale_signature and address == "0x0040dc90":
            signature = "undefined CBattleEngine__CountFlag9CBySelectionMode(void)"
        if overclaim and address == "0x0040dce0":
            comment = comment.replace("Static evidence only", "runtime behavior proven")
        metadata_rows.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        index_rows.append(f"{address}\t{name}\t{signature}\tOK\n")
        (decompile / f"{address[2:]}_{name}.c").write_text(decompile_tokens, encoding="utf-8")

    metadata.write_text(METADATA_HEADER + "".join(metadata_rows), encoding="utf-8")
    (decompile / "index.tsv").write_text(INDEX_HEADER + "".join(index_rows), encoding="utf-8")
    xrefs.write_text(
        XREF_HEADER
        + "0040d0f0\tCWeaponStatement__UsesBallisticArcNoLocks\t005096c1\t005096a0\tCUnit__ComputeMinBallisticTravelDistance\tUNCONDITIONAL_CALL\n"
        + "0040d0f0\tCWeaponStatement__UsesBallisticArcNoLocks\t005099c1\t005099a0\tCUnit__ComputeMaxBallisticTravelDistance\tUNCONDITIONAL_CALL\n"
        + "0040d0f0\tCWeaponStatement__UsesBallisticArcNoLocks\t00507dd4\t00507ab0\tOID__CanFireAtTarget_BallisticArcA\tUNCONDITIONAL_CALL\n"
        + "0040d0f0\tCWeaponStatement__UsesBallisticArcNoLocks\t0050919a\t00509140\tOID__UpdateAimTransformAndAttachTargetReader\tUNCONDITIONAL_CALL\n"
        + "0040da30\tCBattleEngine__BuildInterpolatedWorldTransform\t004843d3\t00484340\tCExplosionInitThing__RenderTargetMarkers3D\tUNCONDITIONAL_CALL\n"
        + "0040dc90\tCBattleEngine__CountFlag9CBySelectionMode\t00485d60\t00485d50\tCExplosionInitThing__RenderObjectiveStatusPanel\tUNCONDITIONAL_CALL\n"
        + "0040dce0\tCBattleEngine__HostileEnvironment\t00411611\t00411500\tCMonitor__ApplyHostileEnvironmentPenalty\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x0040d0f0\t0x0040d0f0\tTARGET\t0\t0x0040d0f0\t0x0040d0f0\tCWeaponStatement__UsesBallisticArcNoLocks\tFLD\tfloat ptr [ECX + 0x3c]\td9 41 3c\tFALL_THROUGH\n"
        + "0x0040d0f0\t0x0040d0f0\tAFTER\t1\t0x0040d104\t0x0040d0f0\tCWeaponStatement__UsesBallisticArcNoLocks\tJNZ\t0x0040d11a\t75 14\tCONDITIONAL_JUMP\n"
        + "0x0040d0f0\t0x0040d0f0\tAFTER\t2\t0x0040d119\t0x0040d0f0\tCWeaponStatement__UsesBallisticArcNoLocks\tRET\t\tc3\tTERMINATOR\n"
        + "0x0040d470\t0x0040d470\tTARGET\t0\t0x0040d482\t0x0040d470\tCLine__ctor_fromEndpoints\tMOV\tdword ptr [EAX], 0x5d892c\tc7 00 2c 89 5d 00\tFALL_THROUGH\n"
        + "0x0040d470\t0x0040d470\tAFTER\t1\t0x0040d4bd\t0x0040d470\tCLine__ctor_fromEndpoints\tMOV\tdword ptr [EAX], 0x5d8bfc\tc7 00 fc 8b 5d 00\tFALL_THROUGH\n"
        + "0x0040d470\t0x0040d470\tAFTER\t2\t0x0040d4c6\t0x0040d470\tCLine__ctor_fromEndpoints\tRET\t0x8\tc2 08 00\tTERMINATOR\n"
        + "0x0040da30\t0x0040da30\tTARGET\t0\t0x0040da30\t0x0040da30\tCBattleEngine__BuildInterpolatedWorldTransform\tSUB\tESP, 0x138\t81 ec 38 01 00 00\tFALL_THROUGH\n"
        + "0x0040da30\t0x0040da30\tAFTER\t1\t0x0040da4a\t0x0040da30\tCBattleEngine__BuildInterpolatedWorldTransform\tFLD\tfloat ptr [ESI + 0x1c]\td9 46 1c\tFALL_THROUGH\n"
        + "0x0040da30\t0x0040da30\tAFTER\t2\t0x0040da4d\t0x0040da30\tCBattleEngine__BuildInterpolatedWorldTransform\tFSUB\tfloat ptr [ESI + 0x8c]\td8 a6 8c 00 00 00\tFALL_THROUGH\n"
        + "0x0040dc90\t0x0040dc90\tTARGET\t0\t0x0040dc90\t0x0040dc90\tCBattleEngine__CountFlag9CBySelectionMode\tCMP\tdword ptr [ECX + 0x260], 0x3\t83 b9 60 02 00 00 03\tFALL_THROUGH\n"
        + "0x0040dc90\t0x0040dc90\tAFTER\t1\t0x0040dc9f\t0x0040dc90\tCBattleEngine__CountFlag9CBySelectionMode\tJMP\t0x004129a0\te9 fc 4c 00 00\tCALL_TERMINATOR\n"
        + "0x0040dc90\t0x0040dc90\tAFTER\t2\t0x0040dcaa\t0x0040dc90\tCBattleEngine__CountFlag9CBySelectionMode\tJMP\t0x00414b70\te9 c1 6e 00 00\tCALL_TERMINATOR\n"
        + "0x0040dcb0\t0x0040dcb0\tTARGET\t0\t0x0040dcb0\t0x0040dcb0\tCBattleEngine__SetFlag58CEnabled\tMOV\tdword ptr [ECX + 0x58c], 0x1\tc7 81 8c 05 00 00 01 00 00 00\tFALL_THROUGH\n"
        + "0x0040dcb0\t0x0040dcb0\tAFTER\t1\t0x0040dcba\t0x0040dcb0\tCBattleEngine__SetFlag58CEnabled\tRET\t\tc3\tTERMINATOR\n"
        + "0x0040dce0\t0x0040dce0\tTARGET\t0\t0x0040dce0\t0x0040dce0\tCBattleEngine__HostileEnvironment\tFLD\tfloat ptr [0x00672fd0]\td9 05 d0 2f 67 00\tFALL_THROUGH\n"
        + "0x0040dce0\t0x0040dce0\tAFTER\t1\t0x0040dd25\t0x0040dce0\tCBattleEngine__HostileEnvironment\tCALL\t0x004e1910\te8 e6 3b 0d 00\tUNCONDITIONAL_CALL\n"
        + "0x0040dce0\t0x0040dce0\tAFTER\t2\t0x0040dd53\t0x0040dce0\tCBattleEngine__HostileEnvironment\tCALL\t0x004e1940\te8 e8 3b 0d 00\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    vtables.write_text(
        "vtable\tcol_ptr_slot\tcol_addr\tsignature\toffset\tcd_offset\ttype_desc\tclass_desc\traw_type_name\tdemangled_type_name\n"
        "005d892c\t005d8928\t0060c658\t0x00000000\t0\t0\t0x00622f10\t0x0060c648\t.?AVCGeneralVolume@@\tCGeneralVolume\n"
        "005d8bfc\t005d8bf8\t0060c740\t0x00000000\t0\t0\t0x006232a8\t0x0060c730\t.?AVCLine@@\tCLine\n",
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
        "vtables": vtables,
    }


class BattleEngineD0TailSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_corrected_names_signatures_comments_and_evidence(self) -> None:
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
                vtables_path=paths["vtables"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], 6)
        self.assertEqual(report["summary"]["correctedNames"], 5)
        self.assertEqual(report["summary"]["hardenedSignatures"], 6)

    def test_fails_for_stale_signature_or_runtime_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), overclaim=True, stale_signature=True)
            report = probe.build_report(
                signature_dry_log_path=paths["signature_dry"],
                signature_apply_log_path=paths["signature_apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
                vtables_path=paths["vtables"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("signature tokens missing" in failure for failure in report["failures"]))
        self.assertTrue(any("runtime/source overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
