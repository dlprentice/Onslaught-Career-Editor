#!/usr/bin/env python3
"""Tests for the CAtmospheric behavior signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_atmospheric_behavior_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"


def write_fixture(root: Path, *, stale_signature: bool = False, overclaim: bool = False) -> dict[str, Path]:
    signature_dry = root / "signature_dry.log"
    signature_apply = root / "signature_apply.log"
    comments_dry = root / "comments_dry.log"
    comments_apply = root / "comments_apply.log"
    metadata = root / "metadata_readback.tsv"
    decompile = root / "decompile_readback"
    xrefs = root / "xrefs.tsv"
    instructions = root / "instructions_readback.tsv"
    decompile.mkdir()

    signature_dry.write_text(
        "Mode: dry\n"
        "DRY: 0x00404210 CAtmospheric__Process -> void __fastcall CAtmospheric__Process(void * this)\n"
        "DRY: 0x00404790 CAtmospheric__UpdateBlendState -> void __fastcall CAtmospheric__UpdateBlendState(void * this)\n"
        "DRY: 0x00404860 CAtmospheric__ConfigureTrail -> bool __thiscall CAtmospheric__ConfigureTrail(void * this, int samplerIndex, int resetBlendPosition, int blendMode)\n"
        "DRY: 0x004048c0 CAtmospheric__GetInterpolatedBlendValue -> double __fastcall CAtmospheric__GetInterpolatedBlendValue(void * this)\n"
        "--- SUMMARY ---\nupdated=0 skipped=4 missing=0 bad=0\n",
        encoding="utf-8",
    )
    signature_apply.write_text(
        "Mode: apply\n"
        "OK: 0x00404210 CAtmospheric__Process -> void __fastcall CAtmospheric__Process(void * this)\n"
        "OK: 0x00404790 CAtmospheric__UpdateBlendState -> void __fastcall CAtmospheric__UpdateBlendState(void * this)\n"
        "OK: 0x00404860 CAtmospheric__ConfigureTrail -> bool __thiscall CAtmospheric__ConfigureTrail(void * this, int samplerIndex, int resetBlendPosition, int blendMode)\n"
        "OK: 0x004048c0 CAtmospheric__GetInterpolatedBlendValue -> double __fastcall CAtmospheric__GetInterpolatedBlendValue(void * this)\n"
        "--- SUMMARY ---\nupdated=4 skipped=0 missing=0 bad=0\n",
        encoding="utf-8",
    )
    comments_dry.write_text("--- SUMMARY ---\napplied=0 skipped=4 missing=0 bad=0\n", encoding="utf-8")
    comments_apply.write_text("--- SUMMARY ---\napplied=4 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    comments = {
        "0x00404210": "Atmospheric process/update loop evidence. Snapshots prior pose/orientation, retargets a peer atmospheric, updates orientation/motion, writes map-who position, and schedules event 3000. Not concrete layout, exact source identity, or runtime behavior proof.",
        "0x00404790": "Atmospheric blend-state update evidence. Advances current/previous blend scalar, wraps/clamps state, and may resample fallback velocity through the sampler helper. Not concrete layout, exact source identity, or runtime behavior proof.",
        "0x00404860": "Atmospheric trail configuration evidence. Updates sampler index/mode fields, optionally resets blend progress, samples fallback velocity, and returns true with ret 0xc. Not concrete layout, exact source identity, or runtime behavior proof.",
        "0x004048c0": "Atmospheric interpolated blend accessor evidence. Returns current blend or frame-interpolated previous/current blend using global frame factor. Not concrete layout, exact source identity, or runtime behavior proof.",
    }
    if overclaim:
        comments["0x004048c0"] = comments["0x004048c0"].replace(
            "runtime behavior proof", "runtime behavior proven"
        )

    signatures = {
        "0x00404210": "void __fastcall CAtmospheric__Process(void * this)",
        "0x00404790": "void __fastcall CAtmospheric__UpdateBlendState(void * this)",
        "0x00404860": "bool __thiscall CAtmospheric__ConfigureTrail(void * this, int samplerIndex, int resetBlendPosition, int blendMode)",
        "0x004048c0": "double __fastcall CAtmospheric__GetInterpolatedBlendValue(void * this)",
    }
    if stale_signature:
        signatures["0x00404790"] = "void __fastcall CAtmospheric__UpdateBlendState(int param_1)"

    names = {
        "0x00404210": "CAtmospheric__Process",
        "0x00404790": "CAtmospheric__UpdateBlendState",
        "0x00404860": "CAtmospheric__ConfigureTrail",
        "0x004048c0": "CAtmospheric__GetInterpolatedBlendValue",
    }

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
        "0x00404210": "CMapWhoEntry__UpdatePosition CEventManager__AddEvent_AtTime 3000",
        "0x00404790": "CAtmospheric__GetSamplerValueOrDefault 0x3f800000",
        "0x00404860": "CAtmospheric__GetSamplerValueOrDefault return true",
        "0x004048c0": "DAT_008a9e44",
    }
    for addr, name in names.items():
        (decompile / f"{addr[2:]}_{name}.c").write_text(
            f"{name} {signatures[addr]} {decompile_tokens[addr]} atmospheric blend sampler map-who event 3000 frame-interpolated",
            encoding="utf-8",
        )
    xrefs.write_text(
        XREF_HEADER
        + "".join(f"{addr[2:]}\t{names[addr]}\t00401000\t00401000\tCaller\tUNCONDITIONAL_CALL\n" for addr in names),
        encoding="utf-8",
    )
    instructions.write_text(
        "target_addr\tfunction_addr\tposition\tindex\taddress\tinstruction_function_addr\tinstruction_function\tmnemonic\toperands\tbytes\tflow_type\n"
        "0x00404210\t0x00404210\tAFTER\t1\t0x004045bc\t0x00404210\tCAtmospheric__Process\tCALL\t0x0044b370\t\tUNCONDITIONAL_CALL\n"
        "0x00404790\t0x00404790\tAFTER\t1\t0x0040485d\t0x00404790\tCAtmospheric__UpdateBlendState\tRET\t\tc3\tTERMINATOR\n"
        "0x00404860\t0x00404860\tAFTER\t1\t0x004048b7\t0x00404860\tCAtmospheric__ConfigureTrail\tRET\t0xc\tc2 0c 00\tTERMINATOR\n"
        "0x004048c0\t0x004048c0\tAFTER\t1\t0x004048d7\t0x004048c0\tCAtmospheric__GetInterpolatedBlendValue\tFMUL\tfloat ptr [0x008a9e44]\t\tFALL_THROUGH\n",
        encoding="utf-8",
    )
    return {
        "signature_dry": signature_dry,
        "signature_apply": signature_apply,
        "comments_dry": comments_dry,
        "comments_apply": comments_apply,
        "metadata": metadata,
        "decompile_index": decompile / "index.tsv",
        "decompile_dir": decompile,
        "xrefs": xrefs,
        "instructions": instructions,
    }


class AtmosphericBehaviorSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_hardened_behavior_signatures_with_caveats(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                signature_dry_log_path=paths["signature_dry"],
                signature_apply_log_path=paths["signature_apply"],
                comments_dry_log_path=paths["comments_dry"],
                comments_apply_log_path=paths["comments_apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["signatureHardenedTargets"], 4)
        self.assertEqual(report["summary"]["instructionRows"], 4)

    def test_fails_for_stale_signature_or_runtime_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale_signature=True, overclaim=True)
            report = probe.build_report(
                signature_dry_log_path=paths["signature_dry"],
                signature_apply_log_path=paths["signature_apply"],
                comments_dry_log_path=paths["comments_dry"],
                comments_apply_log_path=paths["comments_apply"],
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
