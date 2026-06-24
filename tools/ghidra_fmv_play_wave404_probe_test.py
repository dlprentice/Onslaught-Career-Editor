#!/usr/bin/env python3
"""Self-tests for the Wave404 FMV console command probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_fmv_play_wave404_probe as probe


class FmvPlayWave404ProbeTests(unittest.TestCase):
    def test_accepts_expected_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "subagents" / "ghidra-static-reaudit" / "fmv-play-wave404" / "current"
            decomp = base / "decompile_after"
            decomp.mkdir(parents=True)

            (base / "metadata_after.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x004655d0\tcon_fmv_play\tvoid __cdecl con_fmv_play(char * command_line)\t"
                "Console command handler for fmv_play <filename>. Validates that the command line is longer than the 9-byte prefix, "
                "mirrors DAT_006630cc into DAT_0089d69c, enters controller non-interactive mode, invokes the frontend video object "
                "at 0x0089d690 through vtable slot +0x2c with command_line+9 and flags 0,0,0,0,1, then leaves non-interactive mode. "
                "On short input it prints the syntax string through CConsole__AddString. Static retail evidence only; exact frontend "
                "video object type/layout, runtime playback behavior, and rebuild parity remain unproven.\tOK\n",
                encoding="utf-8",
            )
            (decomp / "004655d0_con_fmv_play.c").write_text(
                "void __cdecl con_fmv_play(char * command_line) {\n"
                "  if (9 < strlen(command_line)) {\n"
                "    DAT_0089d69c = DAT_006630cc != 0;\n"
                "    CController__SetNonInteractiveSection(true);\n"
                "    (**(code **)(DAT_0089d690 + 0x2c))(command_line + 9,0,0,0,0,1);\n"
                "    CController__SetNonInteractiveSection(false);\n"
                "  } else CConsole__AddString(&DAT_00663498,s_Syntax___fmv_play_<filename>_00629abc);\n"
                "}\n",
                encoding="utf-8",
            )
            (base / "xrefs_after.tsv").write_text(
                "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
                "004655d0\tcon_fmv_play\t004656b5\t<none>\t<no_function>\tDATA\n",
                encoding="utf-8",
            )
            (base / "tags_after.tsv").write_text(
                "address\tname\ttags\tstatus\n"
                "004655d0\tcon_fmv_play\tcomment-hardened;console-command;fmv;fmv-play-wave404;"
                "frontend-video;retail-binary-evidence;signature-corrected;static-reaudit\tOK\n",
                encoding="utf-8",
            )
            (base / "instructions_after.tsv").write_text(
                "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
                "0x004655d0\t0x004655d0\tAFTER\t9\t0x004655e2\t0x004655d0\tcon_fmv_play\tCMP\tECX, 0x9\t83 f9 09\tFALL_THROUGH\n"
                "0x004655d0\t0x004655d0\tAFTER\t15\t0x004655f4\t0x004655d0\tcon_fmv_play\tMOV\t[0x0089d69c], EAX\ta3 9c d6 89 00\tFALL_THROUGH\n"
                "0x004655d0\t0x004655d0\tAFTER\t16\t0x004655f9\t0x004655d0\tcon_fmv_play\tCALL\t0x0042d7d0\te8 d2 81 fc ff\tUNCONDITIONAL_CALL\n"
                "0x004655d0\t0x004655d0\tAFTER\t17\t0x004655fe\t0x004655d0\tcon_fmv_play\tMOV\tEAX, [0x0089d690]\ta1 90 d6 89 00\tFALL_THROUGH\n"
                "0x004655d0\t0x004655d0\tAFTER\t19\t0x00465606\t0x004655d0\tcon_fmv_play\tADD\tESI, 0x9\t83 c6 09\tFALL_THROUGH\n"
                "0x004655d0\t0x004655d0\tAFTER\t27\t0x00465619\t0x004655d0\tcon_fmv_play\tCALL\tdword ptr [EAX + 0x2c]\tff 50 2c\tCOMPUTED_CALL\n"
                "0x004655d0\t0x004655d0\tAFTER\t29\t0x0046561e\t0x004655d0\tcon_fmv_play\tCALL\t0x0042d7d0\te8 ad 81 fc ff\tUNCONDITIONAL_CALL\n"
                "0x004655d0\t0x004655d0\tAFTER\t34\t0x00465629\t0x004655d0\tcon_fmv_play\tPUSH\t0x629abc\t68 bc 9a 62 00\tFALL_THROUGH\n",
                encoding="utf-8",
            )
            (base / "apply_fmv_play_wave404_dry.log").write_text(
                "SUMMARY updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0\n",
                encoding="utf-8",
            )
            (base / "apply_fmv_play_wave404_apply.log").write_text(
                "SUMMARY updated=1 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0\nREPORT: Save succeeded\n",
                encoding="utf-8",
            )
            note = root / "release" / "readiness" / "ghidra_fmv_play_wave404_2026-05-14.md"
            note.parent.mkdir(parents=True)
            note.write_text(
                "0x004655d0 con_fmv_play void __cdecl con_fmv_play(char * command_line) "
                "fmv_play <filename> command table DATA xref 0x004656b5 DAT_006630cc DAT_0089d69c 0x0089d690 "
                "CController__SetNonInteractiveSection CConsole__AddString does not prove runtime playback behavior "
                "does not prove exact frontend video object type/layout does not prove rebuild parity\n",
                encoding="utf-8",
            )

            result = probe.validate(root=root, base=base)
            self.assertEqual([], result.failures)

    def test_rejects_stale_void_pointer_signature(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "subagents" / "ghidra-static-reaudit" / "fmv-play-wave404" / "current"
            base.mkdir(parents=True)
            (base / "metadata_after.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x004655d0\tcon_fmv_play\tvoid __cdecl con_fmv_play(void * param_1)\t\tOK\n",
                encoding="utf-8",
            )
            result = probe.validate(root=root, base=base)
            self.assertTrue(any("char * command_line" in failure for failure in result.failures))

    def test_rejects_runtime_overclaim_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "subagents" / "ghidra-static-reaudit" / "fmv-play-wave404" / "current"
            base.mkdir(parents=True)
            note = root / "release" / "readiness" / "ghidra_fmv_play_wave404_2026-05-14.md"
            note.parent.mkdir(parents=True)
            note.write_text("runtime playback behavior proven\n", encoding="utf-8")
            result = probe.validate(root=root, base=base)
            self.assertTrue(any("overclaim" in failure for failure in result.failures))


if __name__ == "__main__":
    unittest.main()
