#!/usr/bin/env python3
"""Tests for the Atmospherics lifecycle signature/comment tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_atmospherics_lifecycle_signature_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def write_fixture(root: Path, *, stale_signature: bool = False, overclaim: bool = False) -> dict[str, Path]:
    dry = root / "signature_dry.log"
    apply = root / "signature_apply.log"
    metadata = root / "metadata_final.tsv"
    decompile = root / "decompile_final"
    xrefs = root / "xrefs_final.tsv"
    instructions = root / "instructions_final.tsv"
    decompile.mkdir()

    dry.write_text("--- SUMMARY ---\nupdated=0 skipped=8 missing=0 bad=0\n", encoding="utf-8")
    apply.write_text("--- SUMMARY ---\nupdated=8 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    signatures = {
        "0x004046d0": "void * __thiscall CAtmospheric__Constructor(void * this, void * ownerThing)",
        "0x00404a00": "void __cdecl Atmospherics__Init(void)",
        "0x00404b90": "void __cdecl Atmospherics__ResetAndUpdate(void)",
        "0x00404bd0": "void __cdecl Atmospherics__UpdateAll(void)",
        "0x00404bf0": "void __cdecl Atmospherics__RenderAll(void)",
        "0x00404c10": "void __cdecl Atmospherics__Shutdown(void)",
        "0x00404c90": "void __cdecl Atmospherics__NotifyAll(int eventCode)",
        "0x004f44a0": "void __thiscall CThing__AddTrail(void * this, int samplerIndex, int resetBlendPosition, int blendMode)",
    }
    if stale_signature:
        signatures["0x004046d0"] = "void * __thiscall CAtmospheric__Constructor(void * this, float param_1)"
        signatures["0x004f44a0"] = "undefined CThing__AddTrail(void)"

    comments = {
        "0x004046d0": "Signature/comment correction for CAtmospheric constructor. Corrects the prior float parameter: CThing__AddTrail passes the owning thing pointer, the constructor stores that dword at +0x20, behavior helpers later use +0x20 as the sampler/owner pointer, and event 3000 is scheduled. Concrete layout, exact source identity, and runtime behavior remain unproven.",
        "0x00404a00": "Signature/comment hardening for global Atmospherics init. Evidence zeroes wind/density globals, loads the snow layer texture, allocates profile/cloud objects, and registers the ListAtmospherics command plus atm_* console variables. Concrete global layout, exact source identity, and runtime behavior remain unproven.",
        "0x00404b90": "Signature/comment hardening for global Atmospherics reset/update. Evidence clears the prevailing wind vector globals and walks the atmospheric list at DAT_006601a8, dispatching the +0xc virtual slot. Concrete vtable names, list layout, and runtime behavior remain unproven.",
        "0x00404bd0": "Signature/comment hardening for global Atmospherics update-all helper. Evidence walks the atmospheric list at DAT_006601a8 and dispatches each entry's +0x8 virtual slot. Concrete vtable names, list layout, and runtime behavior remain unproven.",
        "0x00404bf0": "Signature/comment hardening for global Atmospherics render-all helper. Evidence walks the atmospheric list at DAT_006601a8 and dispatches each entry's +0x4 virtual slot. Concrete vtable names, list layout, and runtime behavior remain unproven.",
        "0x00404c10": "Signature/comment hardening for global Atmospherics shutdown. Evidence releases the cached snow texture handle, walks DAT_006601a8, dispatches the +0x10 virtual slot, unlinks entries, and frees objects. Concrete ownership/layout and runtime behavior remain unproven.",
        "0x00404c90": "Signature/comment hardening for global Atmospherics notify helper. Evidence walks DAT_006601a8 and dispatches the +0x14 virtual slot with eventCode. Concrete event semantics, vtable names, list layout, and runtime behavior remain unproven.",
        "0x004f44a0": "Signature/comment correction for CThing trail setup. Evidence checks this+0x6c, allocates a 0x24-byte CAtmospheric when missing, passes this to CAtmospheric__Constructor, stores the result back at +0x6c, then calls CAtmospheric__ConfigureTrail with samplerIndex/resetBlendPosition/blendMode; ret 0xc confirms three stack arguments. Concrete CThing layout and runtime trail behavior remain unproven.",
    }
    if overclaim:
        comments["0x00404c90"] += " Runtime behavior proven."

    metadata.write_text(
        METADATA_HEADER
        + "".join(
            f"{addr}\t{probe.TARGETS[addr]['name']}\t{signatures[addr]}\t{comments[addr]}\tOK\n"
            for addr in probe.TARGETS
        ),
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        INDEX_HEADER
        + "".join(
            f"{addr}\t{probe.TARGETS[addr]['name']}\t{signatures[addr]}\tOK\n"
            for addr in probe.TARGETS
        ),
        encoding="utf-8",
    )

    decompile_tokens = {
        "0x004046d0": "ownerThing + 0x20 CEventManager__AddEvent_AtTime 3000",
        "0x00404a00": "CTexture__FindTexture SnowLayer CAtmosphericsProfile__ctor CConsole__RegisterVariable",
        "0x00404b90": "DAT_00660198 DAT_006601a8 + 0xc",
        "0x00404bd0": "DAT_006601a8 + 8",
        "0x00404bf0": "DAT_006601a8 + 4",
        "0x00404c10": "CHud__DecrementCounter9C DAT_006601ac OID__FreeObject + 0x10",
        "0x00404c90": "eventCode DAT_006601a8 + 0x14",
        "0x004f44a0": "samplerIndex resetBlendPosition blendMode CAtmospheric__Constructor CAtmospheric__ConfigureTrail",
    }
    for addr, expected in probe.TARGETS.items():
        (decompile / f"{addr[2:]}_{expected['name']}.c").write_text(
            f"{expected['name']} {signatures[addr]} {decompile_tokens[addr]}",
            encoding="utf-8",
        )

    xrefs.write_text(
        XREF_HEADER
        + "004046d0\tCAtmospheric__Constructor\t004f44eb\t004f44a0\tCThing__AddTrail\tUNCONDITIONAL_CALL\n"
        + "00404a00\tAtmospherics__Init\t0046d072\t0046d040\tCGame__PostLoadProcess\tUNCONDITIONAL_CALL\n"
        + "00404b90\tAtmospherics__ResetAndUpdate\t0046d077\t0046d040\tCGame__PostLoadProcess\tUNCONDITIONAL_CALL\n"
        + "00404bd0\tAtmospherics__UpdateAll\t0053e8d2\t0053e2e0\tCDXEngine__Render\tUNCONDITIONAL_CALL\n"
        + "00404bf0\tAtmospherics__RenderAll\t0046ebd3\t0046e910\tCGame__Update\tUNCONDITIONAL_CALL\n"
        + "00404c10\tAtmospherics__Shutdown\t0046cc4d\t0046ca70\tCGame__ShutdownRestartLoop\tUNCONDITIONAL_CALL\n"
        + "00404c10\tAtmospherics__Shutdown\t0046e1d0\t0046dc30\tCGame__RestartLoopRunLevel\tUNCONDITIONAL_CALL\n"
        + "00404c90\tAtmospherics__NotifyAll\t0044a364\t0044a2d0\tCDXEngine__UpdateAtmosphericsAndLightMatrices\tUNCONDITIONAL_CALL\n"
        + "004f44a0\tCThing__AddTrail\t005d853c\t<none>\t<no_function>\tDATA\n"
        + "004f44a0\tCThing__AddTrail\t00489185\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x004046d0\t0x004046d0\tAFTER\t36\t0x0040474a\t0x004046d0\tCAtmospheric__Constructor\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x00404b90\t0x00404b90\tAFTER\t16\t0x00404bc3\t0x00404b90\tAtmospherics__ResetAndUpdate\tRET\t\tc3\tTERMINATOR\n"
        + "0x00404bd0\t0x00404bd0\tAFTER\t10\t0x00404bea\t0x00404bd0\tAtmospherics__UpdateAll\tRET\t\tc3\tTERMINATOR\n"
        + "0x00404bf0\t0x00404bf0\tAFTER\t10\t0x00404c0a\t0x00404bf0\tAtmospherics__RenderAll\tRET\t\tc3\tTERMINATOR\n"
        + "0x00404c10\t0x00404c10\tAFTER\t55\t0x00404c88\t0x00404c10\tAtmospherics__Shutdown\tRET\t\tc3\tTERMINATOR\n"
        + "0x00404c90\t0x00404c90\tAFTER\t15\t0x00404cb1\t0x00404c90\tAtmospherics__NotifyAll\tRET\t\tc3\tTERMINATOR\n"
        + "0x004f44a0\t0x004f44a0\tAFTER\t40\t0x004f4525\t0x004f44a0\tCThing__AddTrail\tRET\t0xc\tc2 0c 00\tTERMINATOR\n",
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


class AtmosphericsLifecycleSignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_corrected_lifecycle_tranche(self) -> None:
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
        self.assertEqual(report["summary"]["targets"], 8)
        self.assertEqual(report["summary"]["staleSignatureHits"], 0)
        self.assertEqual(report["summary"]["commentOverclaims"], 0)
        self.assertEqual(report["summary"]["xrefEvidenceHits"], 8)

    def test_fails_for_stale_signature_or_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale_signature=True, overclaim=True)
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
        self.assertTrue(any("forbidden signature token remains" in failure for failure in report["failures"]))
        self.assertTrue(any("runtime/source overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
