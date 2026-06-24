#!/usr/bin/env python3
"""Tests for the early-helper Ghidra signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_early_helper_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = "target_addr\tinstruction_addr\tfunction_name\tmnemonic\toperands\n"


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
        "0x004062d0": "CSquadNormal__BuildOrientationMatrixFromEuler",
        "0x00406d50": "Vec3__NormalizeInPlace",
        "0x00407060": "CEngine__MoveBurstReaderToCooldownSet",
        "0x00407140": "CMonitor__RemoveActiveReaderById",
        "0x00407310": "CBattleEngine__IsCurrentResolvedEntry",
        "0x00407540": "CGame__UpdateMouseLookAngles",
    }
    signatures = {
        "0x004062d0": "void __thiscall CSquadNormal__BuildOrientationMatrixFromEuler(void * this, float angle0, float angle1, float angle2)",
        "0x00406d50": "void __fastcall Vec3__NormalizeInPlace(void * vec)",
        "0x00407060": "void __thiscall CEngine__MoveBurstReaderToCooldownSet(void * this, int readerId)",
        "0x00407140": "void __thiscall CMonitor__RemoveActiveReaderById(void * this, int readerId)",
        "0x00407310": "bool __thiscall CBattleEngine__IsCurrentResolvedEntry(void * this, void * expectedEntry)",
        "0x00407540": "void __fastcall CGame__UpdateMouseLookAngles(void * battleEngine)",
    }
    if stale_param:
        signatures["0x00407060"] = "void __thiscall CEngine__MoveBurstReaderToCooldownSet(void * this, int param_1, int param_2)"

    comments = {
        "0x004062d0": "Signature hardening: ret 0xc and FPU trig writes matrix rows through this/outMatrix offsets through +0x28. Wide xrefs make exact source identity and owner layout remain unproven.",
        "0x00406d50": "Signature hardening: normalizes a Vec3 in place across +0x0/+0x4/+0x8, with zero-length guard. Runtime behavior remain unproven.",
        "0x00407060": "Signature hardening: ret 0x4 shows one stack readerId; body moves an active set +0x294 entry into cooldown set +0x2a4 or frees a duplicate. Exact reader layout remain unproven.",
        "0x00407140": "Signature hardening: ret 0x4 shows one stack readerId; body removes a cooldown set +0x2a4 entry then calls CGenericActiveReader__dtor and OID__FreeObject. Runtime behavior remain unproven.",
        "0x00407310": "Signature hardening: ret 0x4 shows one expectedEntry argument; body checks current resolved entry through +0x57c or +0x578. Exact entry type remain unproven.",
        "0x00407540": "Signature hardening for historical behavior label: mouse-look path uses g_MouseSensitivity and recentering but exact owner and runtime behavior remain unproven.",
    }
    if overclaim:
        comments["0x00407540"] += " Runtime behavior proven."

    metadata.write_text(
        METADATA_HEADER
        + "".join(f"{addr}\t{names[addr]}\t{signatures[addr]}\t{comments[addr]}\tOK\n" for addr in names),
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        INDEX_HEADER + "".join(f"{addr}\t{names[addr]}\t{signatures[addr]}\tOK\n" for addr in names),
        encoding="utf-8",
    )
    decompile_tokens = {
        "0x004062d0": "this angle0 angle1 angle2 fcos fsin + 0x28",
        "0x00406d50": "vec SQRT _DAT_005d8568 + 8",
        "0x00407060": "readerId CSPtrSet__Remove CSPtrSet__AddToHead CGenericActiveReader__dtor OID__FreeObject",
        "0x00407140": "readerId CSPtrSet__Remove CGenericActiveReader__dtor OID__FreeObject",
        "0x00407310": "expectedEntry CBattleEngine__GetIndexedEntry CGeneralVolume__ResolveCurrentOrFallbackEntry",
        "0x00407540": "battleEngine g_MouseSensitivity PLATFORM__GetWindowWidth CSquadNormal__BuildOrientationMatrixFromEuler Vec3__NormalizeInPlace",
    }
    for addr, name in names.items():
        (decompile / f"{addr[2:]}_{name}.c").write_text(
            f"{name} {signatures[addr]} {decompile_tokens[addr]}",
            encoding="utf-8",
        )
    xrefs.write_text(
        XREF_HEADER
        + "004062d0\tCSquadNormal__BuildOrientationMatrixFromEuler\t004076e2\t00407540\tCGame__UpdateMouseLookAngles\tUNCONDITIONAL_CALL\n"
        + "00406d50\tVec3__NormalizeInPlace\t004078b3\t00407540\tCGame__UpdateMouseLookAngles\tUNCONDITIONAL_CALL\n"
        + "00407060\tCEngine__MoveBurstReaderToCooldownSet\t005074c9\t005069f0\tCEngine__SpawnProjectileBurstFromCurrentPreset\tUNCONDITIONAL_CALL\n"
        + "00407140\tCMonitor__RemoveActiveReaderById\t004dab6b\t004dab50\tCRound__RemoveActiveReaderById\tUNCONDITIONAL_CALL\n"
        + "00407310\tCBattleEngine__IsCurrentResolvedEntry\t005074bb\t005069f0\tCEngine__SpawnProjectileBurstFromCurrentPreset\tUNCONDITIONAL_CALL\n"
        + "00407540\tCGame__UpdateMouseLookAngles\t0046e650\t0046e460\tCGame__Render\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x004062d0\t0x0040638e\tCSquadNormal__BuildOrientationMatrixFromEuler\tRET\t0xc\n"
        + "0x00407060\t0x0040713c\tCEngine__MoveBurstReaderToCooldownSet\tRET\t0x4\n"
        + "0x00407140\t0x004071a6\tCMonitor__RemoveActiveReaderById\tRET\t0x4\n"
        + "0x00407310\t0x00407345\tCBattleEngine__IsCurrentResolvedEntry\tRET\t0x4\n",
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


class EarlyHelperSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_corrected_early_helper_targets(self) -> None:
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

    def test_fails_for_stale_param_signature_or_overclaim(self) -> None:
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
