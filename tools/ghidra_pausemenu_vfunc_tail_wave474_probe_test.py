#!/usr/bin/env python3
"""Tests for ghidra_pausemenu_vfunc_tail_wave474_probe.py."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_pausemenu_vfunc_tail_wave474_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class PauseMenuVfuncTailWave474ProbeTests(unittest.TestCase):
    def test_parse_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dry.log"
            write(
                path,
                "REPORT: Save succeeded\n"
                "updated=0 skipped=3 created=0 would_create=0 renamed=0 "
                "would_rename=3 missing=0 bad=0\n",
            )
            self.assertEqual(probe.parse_summary(path), probe.EXPECTED_DRY)

    def test_fixture_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for name, summary in (
                ("dry.log", "updated=0 skipped=3 created=0 would_create=0 renamed=0 would_rename=3"),
                ("apply.log", "updated=3 skipped=0 created=0 would_create=0 renamed=3 would_rename=0"),
                ("verify_dry.log", "updated=0 skipped=3 created=0 would_create=0 renamed=0 would_rename=0"),
            ):
                write(
                    base / name,
                    "REPORT: Save succeeded\n"
                    f"{summary} missing=0 bad=0\n",
                )

            write(
                base / "post_metadata.tsv",
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x004d15d0\tCPauseMenu__VFunc_03_HandleMenuControlInput\t"
                "void __thiscall CPauseMenu__VFunc_03_HandleMenuControlInput(void * this, void * control_context, int button_id, int button_context)\t"
                "Wave474 timestamp at this+0x2c this+0x14/this+0x24 button 0x33 button 0x2e RET 0x0c runtime UI behavior\tOK\n"
                "0x004d1730\tCSimpleGameMenu__scalar_deleting_dtor\t"
                "void * __thiscall CSimpleGameMenu__scalar_deleting_dtor(void * this, int flags)\t"
                "Wave474 scalar-deleting destructor wrapper CSimpleGameMenu__dtor_base flags bit 0 RET 0x4 runtime UI behavior\tOK\n"
                "0x004d1750\tCSimpleGameMenu__dtor_base\t"
                "void __fastcall CSimpleGameMenu__dtor_base(void * simple_game_menu)\t"
                "Wave474 destructor body shared no-op vtable +0x3c CMenuItemRange CMonitor runtime UI behavior\tOK\n",
            )
            write(
                base / "post_tags.tsv",
                "address\tname\ttags\n"
                "0x004d15d0\tCPauseMenu__VFunc_03_HandleMenuControlInput\t"
                "static-reaudit;pausemenu-vfunc-tail-wave474;retail-binary-evidence;pause-menu;control-input;vtable-slot;"
                "name-corrected;signature-corrected;comment-hardened\n"
                "0x004d1730\tCSimpleGameMenu__scalar_deleting_dtor\t"
                "static-reaudit;pausemenu-vfunc-tail-wave474;retail-binary-evidence;simple-game-menu;destructor;"
                "name-corrected;signature-corrected;comment-hardened\n"
                "0x004d1750\tCSimpleGameMenu__dtor_base\t"
                "static-reaudit;pausemenu-vfunc-tail-wave474;retail-binary-evidence;simple-game-menu;destructor;"
                "name-corrected;signature-corrected;comment-hardened\n",
            )
            write(
                base / "post_xrefs.tsv",
                "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
                "004d15d0\tCPauseMenu__VFunc_03_HandleMenuControlInput\t005de708\t<none>\t<no_function>\tDATA\n"
                "004d1730\tCSimpleGameMenu__scalar_deleting_dtor\t005de720\t<none>\t<no_function>\tDATA\n"
                "004d1750\tCSimpleGameMenu__dtor_base\t004d1733\t004d1730\tCSimpleGameMenu__scalar_deleting_dtor\tUNCONDITIONAL_CALL\n",
            )
            write(
                base / "post_disasm_004d15d0.tsv",
                "address\tbytes\tmnemonic\toperands\n"
                "004d1647\t\tRET\t0xc\n"
                "004d1665\t\tCALL\t0x004d0810\n"
                "004d166e\t\tRET\t0xc\n"
                "004d1676\t\tJLE\t0x004d16f6\n"
                "004d16f3\t\tRET\t0xc\n",
            )
            write(
                base / "post_disasm_004d1730_1750.tsv",
                "address\tbytes\tmnemonic\toperands\n"
                "004d1733\t\tCALL\t0x004d1750\n"
                "004d1738\t\tTEST\tbyte ptr [ESP + 0x8], 0x1\n"
                "004d174d\t\tRET\t0x4\n"
                "004d176f\t\tMOV\tdword ptr [EBX], 0x5de71c\n"
                "004d179c\t\tCALL\t0x0044b1d0\n"
                "004d17ef\t\tCALL\t0x004bac40\n"
                "004d1805\t\tRET\t\n",
            )
            write(
                base / "post-decomp" / "004d15d0_CPauseMenu__VFunc_03_HandleMenuControlInput.c",
                "CPauseMenu__VFunc_03_HandleMenuControlInput button_id CPauseMenu__ButtonPressed "
                "CPauseMenu__ResumeGameAndPersistOptions Controls__FindFirstFreeBindingSlot CMenuItemRange__ResetIterator",
            )
            write(
                base / "post-decomp" / "004d1730_CSimpleGameMenu__scalar_deleting_dtor.c",
                "CSimpleGameMenu__scalar_deleting_dtor CSimpleGameMenu__dtor_base flags CDXMemoryManager__Free",
            )
            write(
                base / "post-decomp" / "004d1750_CSimpleGameMenu__dtor_base.c",
                "CSimpleGameMenu__dtor_base CGenericActiveReader__dtor CSPtrSet__Clear "
                "CMenuItemRange__Destructor CMonitor__Shutdown",
            )

            self.assertEqual(probe.run(base), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
