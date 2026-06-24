#!/usr/bin/env python3
"""Self-tests for the Wave405 CGame::DrawGameStuff probe."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import ghidra_cgame_draw_game_stuff_wave405_probe as probe


class CGameDrawGameStuffWave405ProbeTests(unittest.TestCase):
    def test_accepts_expected_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "subagents" / "ghidra-static-reaudit" / "frontend-cheatchecks-wave405" / "current"
            decomp = base / "decompile_after"
            caller_decomp = base / "caller_decompile_after"
            decomp.mkdir(parents=True)
            caller_decomp.mkdir(parents=True)

            (base / "metadata_before.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x004714c0\tFrontendUpdate_CheatChecks\tundefined FrontendUpdate_CheatChecks(void)\t\tOK\n",
                encoding="utf-8",
            )
            (base / "metadata_after.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x004714c0\tCGame__DrawGameStuff\tvoid __thiscall CGame__DrawGameStuff(void * this)\t"
                "Name/signature correction: source-parity CGame::DrawGameStuff pass called by CDXEngine__PostRender after "
                "CGame__DrawDebugStuff with ECX=&DAT_008a9a98. Retail body handles the PC screenshot/selection key branch, "
                "periodic FPS trace/status-buffer text, developer/game status overlays, encoded frontend cheat text rendering "
                "through Frontend__XorWideTextBlock100BytesToScratch, console status-history rendering, and game-over/objective "
                "overlays. Static retail/source-alignment evidence only; exact CGame layout, input-key semantics, runtime overlay "
                "behavior, and rebuild parity remain unproven.\tOK\n",
                encoding="utf-8",
            )
            (base / "tags_after.tsv").write_text(
                "address\tname\ttags\tstatus\n"
                "004714c0\tCGame__DrawGameStuff\tcgame-draw-game-stuff-wave405;comment-hardened;debug-overlay;game;"
                "game-over;name-corrected;retail-binary-evidence;signature-hardened;source-parity;static-reaudit;"
                "status-overlay\tOK\n",
                encoding="utf-8",
            )
            (base / "xrefs_after.tsv").write_text(
                "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
                "004714c0\tCGame__DrawGameStuff\t0053ef9b\t0053ecc0\tCDXEngine__PostRender\tUNCONDITIONAL_CALL\n",
                encoding="utf-8",
            )
            (decomp / "004714c0_CGame__DrawGameStuff.c").write_text(
                "void __thiscall CGame__DrawGameStuff(void *this) {\n"
                "  if ((g_bDevModeEnabled == 0) && (g_bAllCheatsEnabled == 0)) PlatformInput__ConsumeKeyOnce(0x42);\n"
                "  CEngine__GrabScreenshot(&DAT_00855bb0);\n"
                "  PCPlatform__GetFPS(&DAT_0088a0a8);\n"
                "  CConsole__AppendToStatusBufferV(&DAT_0066ffc8, s_World);\n"
                "  Frontend__XorWideTextBlock100BytesToScratch((short *)&DAT_00679f38, (short *)&PTR_DAT_0062baac);\n"
                "  CConsole__RenderStatusHistoryOverlay(&DAT_0066f580);\n"
                "  CText__GetStringById(&g_Text, 0x88b6ab);\n"
                "}\n",
                encoding="utf-8",
            )
            (caller_decomp / "0053ecc0_CDXEngine__PostRender.c").write_text(
                "CGame__DrawDebugStuff(&DAT_008a9a98);\nCGame__DrawGameStuff(&DAT_008a9a98);\n",
                encoding="utf-8",
            )
            (base / "instructions_after.tsv").write_text(
                "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
                "0x004714c0\t0x004714c0\tAFTER\t10\t0x004714d9\t0x004714c0\tCGame__DrawGameStuff\tMOV\tEDI, ECX\t8b f9\tFALL_THROUGH\n"
                "0x004714c0\t0x004714c0\tAFTER\t118\t0x00471655\t0x004714c0\tCGame__DrawGameStuff\tCALL\t0x00472240\te8 e6 0b 00 00\tUNCONDITIONAL_CALL\n"
                "0x004714c0\t0x004714c0\tAFTER\t228\t0x004717e7\t0x004714c0\tCGame__DrawGameStuff\tCALL\t0x00472270\te8 84 0a 00 00\tUNCONDITIONAL_CALL\n"
                "0x004714c0\t0x004714c0\tAFTER\t245\t0x0047182c\t0x004714c0\tCGame__DrawGameStuff\tCALL\t0x004419e0\te8 af 01 fd ff\tUNCONDITIONAL_CALL\n",
                encoding="utf-8",
            )
            (base / "caller_instructions_after.tsv").write_text(
                "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
                "0x0053ef9b\t0x0053ef9b\tBEFORE\t-1\t0x0053ef96\t0x0053ecc0\tCDXEngine__PostRender\tMOV\tECX, 0x8a9a98\tb9 98 9a 8a 00\tFALL_THROUGH\n"
                "0x0053ef9b\t0x0053ef9b\tTARGET\t0\t0x0053ef9b\t0x0053ecc0\tCDXEngine__PostRender\tCALL\t0x004714c0\te8 20 25 f3 ff\tUNCONDITIONAL_CALL\n",
                encoding="utf-8",
            )
            (base / "apply_cgame_draw_game_stuff_wave405_dry.log").write_text(
                "SUMMARY updated=0 skipped=1 renamed=0 would_rename=1 missing=0 bad=0\nREPORT: Save succeeded\n",
                encoding="utf-8",
            )
            (base / "apply_cgame_draw_game_stuff_wave405_apply.log").write_text(
                "SUMMARY updated=1 skipped=0 renamed=1 would_rename=0 missing=0 bad=0\nREPORT: Save succeeded\n",
                encoding="utf-8",
            )
            queue = root / "subagents" / "ghidra-static-reaudit" / "queue" / "current"
            queue.mkdir(parents=True)
            (queue / "static-reaudit-queue.json").write_text(
                json.dumps(
                    {
                        "totalFunctions": 6028,
                        "qualitySignals": {
                            "commentlessFunctionCount": 4470,
                            "undefinedSignatureCount": 1909,
                        },
                        "priorityQueues": {"commentlessHighSignal": [{"address": "0x004725d0"}]},
                    }
                ),
                encoding="utf-8",
            )
            note = root / "release" / "readiness" / "ghidra_cgame_draw_game_stuff_wave405_2026-05-14.md"
            note.parent.mkdir(parents=True)
            note.write_text(
                "0x004714c0 FrontendUpdate_CheatChecks CGame__DrawGameStuff "
                "void __thiscall CGame__DrawGameStuff(void * this) Stuart source CGame::DrawGameStuff "
                "CDXEngine__PostRender 0x0053ef9b DAT_008a9a98 CGame__DrawDebugStuff "
                "Frontend__XorWideTextBlock100BytesToScratch CConsole__RenderStatusHistoryOverlay "
                "does not prove exact CGame layout does not prove runtime overlay behavior does not prove rebuild parity\n",
                encoding="utf-8",
            )

            result = probe.validate(root=root, base=base)
            self.assertEqual([], result.failures)

    def test_rejects_stale_function_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "subagents" / "ghidra-static-reaudit" / "frontend-cheatchecks-wave405" / "current"
            base.mkdir(parents=True)
            (base / "metadata_after.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x004714c0\tFrontendUpdate_CheatChecks\tundefined FrontendUpdate_CheatChecks(void)\t\tOK\n",
                encoding="utf-8",
            )
            result = probe.validate(root=root, base=base)
            self.assertTrue(any("CGame__DrawGameStuff" in failure for failure in result.failures))

    def test_rejects_runtime_overclaim_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "subagents" / "ghidra-static-reaudit" / "frontend-cheatchecks-wave405" / "current"
            base.mkdir(parents=True)
            note = root / "release" / "readiness" / "ghidra_cgame_draw_game_stuff_wave405_2026-05-14.md"
            note.parent.mkdir(parents=True)
            note.write_text("runtime overlay behavior proven\n", encoding="utf-8")
            result = probe.validate(root=root, base=base)
            self.assertTrue(any("overclaim" in failure for failure in result.failures))


if __name__ == "__main__":
    unittest.main()
