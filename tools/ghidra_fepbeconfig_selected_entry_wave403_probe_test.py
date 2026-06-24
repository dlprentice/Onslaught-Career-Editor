#!/usr/bin/env python3
"""Self-tests for the Wave403 FEPBEConfig selected-entry probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_fepbeconfig_selected_entry_wave403_probe as probe


class FepBeConfigSelectedEntryWave403ProbeTests(unittest.TestCase):
    def test_accepts_expected_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "subagents" / "ghidra-static-reaudit" / "fepbeconfig-selected-entry-wave403" / "current"
            decomp = base / "decompile_after"
            caller = base / "caller_decompile_before"
            decomp.mkdir(parents=True)
            caller.mkdir(parents=True)
            (base / "metadata_after.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x00451a40\tFEPBEConfig__FindSelectedEntryByGlobalId\t"
                "int * __fastcall FEPBEConfig__FindSelectedEntryByGlobalId(void * list_state)\t"
                "Owner correction from CUnitAI to FEPBEConfig selected-entry list helper. "
                "Callers pass 0x0089da14, the body seeds the iterator cursor at +0x28 from list head +0x20, "
                "walks link nodes through +0x4, and returns the first entry whose leading id matches DAT_0089d94c. "
                "Runtime frontend behavior, exact source identity, concrete list-state/entry layout, and rebuild parity remain unproven.\tOK\n",
                encoding="utf-8",
            )
            (decomp / "00451a40_FEPBEConfig__FindSelectedEntryByGlobalId.c").write_text(
                "int * __fastcall FEPBEConfig__FindSelectedEntryByGlobalId(void * list_state) {\n"
                "  /* DAT_0089d94c */\n"
                "  /* list_state + 0x20 */\n"
                "  /* list_state + 0x28 */\n"
                "  return 0;\n"
                "}\n",
                encoding="utf-8",
            )
            (base / "xrefs_after.tsv").write_text(
                "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
                "00451a40\tFEPBEConfig__FindSelectedEntryByGlobalId\t00450da1\t004505b0\tCFEPBEConfig__Render\tUNCONDITIONAL_CALL\n"
                "00451a40\tFEPBEConfig__FindSelectedEntryByGlobalId\t0045139b\t004505b0\tCFEPBEConfig__Render\tUNCONDITIONAL_CALL\n"
                "00451a40\tFEPBEConfig__FindSelectedEntryByGlobalId\t00451638\t004505b0\tCFEPBEConfig__Render\tUNCONDITIONAL_CALL\n",
                encoding="utf-8",
            )
            (base / "tags_after.tsv").write_text(
                "address\tname\ttags\tstatus\n"
                "00451a40\tFEPBEConfig__FindSelectedEntryByGlobalId\t"
                "comment-hardened;fepbeconfig;fepbeconfig-selected-entry-wave403;global-selector;list-lookup;"
                "owner-corrected;retail-binary-evidence;signature-corrected;static-reaudit\tOK\n",
                encoding="utf-8",
            )
            (base / "instructions_after.tsv").write_text(
                "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
                "0x00451a40\t0x00451a40\tTARGET\t0\t0x00451a40\t0x00451a40\tFEPBEConfig__FindSelectedEntryByGlobalId\tMOV\tEAX, dword ptr [ECX + 0x20]\t8b 41 20\tFALL_THROUGH\n"
                "0x00451a40\t0x00451a40\tAFTER\t10\t0x00451a55\t0x00451a40\tFEPBEConfig__FindSelectedEntryByGlobalId\tMOV\tEDX, dword ptr [0x0089d94c]\t8b 15 4c d9 89 00\tFALL_THROUGH\n"
                "0x00451a40\t0x00451a40\tAFTER\t15\t0x00451a64\t0x00451a40\tFEPBEConfig__FindSelectedEntryByGlobalId\tMOV\tEAX, dword ptr [EAX + 0x4]\t8b 40 04\tFALL_THROUGH\n"
                "0x00451a40\t0x00451a40\tAFTER\t24\t0x00451a7b\t0x00451a40\tFEPBEConfig__FindSelectedEntryByGlobalId\tRET\t\tc3\tTERMINATOR\n",
                encoding="utf-8",
            )
            (caller / "004505b0_CFEPBEConfig__Render.c").write_text(
                "/* name: CFEPBEConfig__Render */\n"
                "piVar5 = FEPBEConfig__FindSelectedEntryByGlobalId(&DAT_0089da14);\n",
                encoding="utf-8",
            )
            (base / "apply_fepbeconfig_selected_entry_wave403_dry.log").write_text(
                "SUMMARY updated=0 skipped=1 created=0 would_create=0 renamed=0 would_rename=1 missing=0 bad=0\n",
                encoding="utf-8",
            )
            (base / "apply_fepbeconfig_selected_entry_wave403_apply.log").write_text(
                "SUMMARY updated=1 skipped=0 created=0 would_create=0 renamed=1 would_rename=0 missing=0 bad=0\nREPORT: Save succeeded\n",
                encoding="utf-8",
            )
            note = root / "release" / "readiness" / "ghidra_fepbeconfig_selected_entry_wave403_2026-05-14.md"
            note.parent.mkdir(parents=True)
            note.write_text(
                "0x00451a40 FEPBEConfig__FindSelectedEntryByGlobalId CFEPBEConfig__Render "
                "0x0089da14 DAT_0089d94c CUnitAI owner label superseded "
                "FEPBEConfig source file is present only as page-shell evidence in the current Stuart source snapshot "
                "does not prove runtime frontend behavior does not prove exact source identity does not prove rebuild parity\n",
                encoding="utf-8",
            )

            result = probe.validate(root=root, base=base)
            self.assertEqual([], result.failures)

    def test_rejects_stale_cunitai_owner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "subagents" / "ghidra-static-reaudit" / "fepbeconfig-selected-entry-wave403" / "current"
            base.mkdir(parents=True)
            (base / "metadata_after.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x00451a40\tCUnitAI__FindLinkedNodeByGlobalId\tint * __fastcall CUnitAI__FindLinkedNodeByGlobalId(int param_1)\t\tOK\n",
                encoding="utf-8",
            )
            result = probe.validate(root=root, base=base)
            self.assertTrue(any("FEPBEConfig__FindSelectedEntryByGlobalId" in failure for failure in result.failures))

    def test_rejects_runtime_overclaim_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "subagents" / "ghidra-static-reaudit" / "fepbeconfig-selected-entry-wave403" / "current"
            base.mkdir(parents=True)
            note = root / "release" / "readiness" / "ghidra_fepbeconfig_selected_entry_wave403_2026-05-14.md"
            note.parent.mkdir(parents=True)
            note.write_text("runtime frontend behavior proven\n", encoding="utf-8")
            result = probe.validate(root=root, base=base)
            self.assertTrue(any("overclaim" in failure for failure in result.failures))


if __name__ == "__main__":
    unittest.main()
