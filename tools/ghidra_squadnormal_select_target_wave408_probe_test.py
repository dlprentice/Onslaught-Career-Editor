#!/usr/bin/env python3
"""Self-tests for the Wave408 SquadNormal select-target probe."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import ghidra_squadnormal_select_target_wave408_probe as probe


class SquadNormalSelectTargetWave408ProbeTests(unittest.TestCase):
    def test_accepts_expected_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "subagents" / "ghidra-static-reaudit" / "wave408_squadnormal_select_target" / "current"
            decomp = base / "decompile_after"
            decomp.mkdir(parents=True)

            (base / "metadata_before.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x00477cb0\tCSquadNormal__SelectBestEngagementTarget\t"
                "int * __stdcall CSquadNormal__SelectBestEngagementTarget(void * param_1)\t\tOK\n",
                encoding="utf-8",
            )
            (base / "metadata_after.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x00477cb0\tCSquadNormal__SelectBestEngagementTarget\t"
                "void * __stdcall CSquadNormal__SelectBestEngagementTarget(void * squad)\t"
                "Signature/comment hardening: CSquadNormal target-selection/scoring helper. Fresh retail read-back shows one stack argument (RET 0x4), no ECX thiscall setup, squad state at +0x7c selecting global candidate lists DAT_00855090/DAT_008550b0/DAT_008550c0, virtual position/support-object reads at vtable +0x120/+0x124, per-candidate flag/range/faction/support checks, scoring against config weights at squad+0xa0 offsets 0x158/0x164/0x168/0x16c/0x170/0x174/0x178/0x17c, support/escort helpers, and fallback through candidate+0x148. Static retail evidence only; exact CSquadNormal/source identity, candidate struct layout, global list semantics, runtime AI behavior, and rebuild parity remain unproven.\tOK\n",
                encoding="utf-8",
            )
            (base / "tags_after.tsv").write_text(
                "address\tname\ttags\tstatus\n"
                "00477cb0\tCSquadNormal__SelectBestEngagementTarget\tai-target-selection;comment-hardened;"
                "name-confirmed;retail-binary-evidence;signature-hardened;squad-normal;"
                "squadnormal-select-target-wave408;static-reaudit\tOK\n",
                encoding="utf-8",
            )
            (base / "xrefs_after.tsv").write_text(
                "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
                "00477cb0\tCSquadNormal__SelectBestEngagementTarget\t004e815a\t004e8100\t"
                "CSquadNormal__ScheduleTargetReaderRefresh\tUNCONDITIONAL_CALL\n"
                "00477cb0\tCSquadNormal__SelectBestEngagementTarget\t004ea584\t<none>\t"
                "<no_function>\tUNCONDITIONAL_CALL\n",
                encoding="utf-8",
            )
            (base / "instructions_after.tsv").write_text(
                "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
                "0x00477cb0\t0x00477cb0\tAFTER\t6\t0x00477cbb\t0x00477cb0\tCSquadNormal__SelectBestEngagementTarget\tMOV\tESI, 0x855090\tbe 90 50 85 00\tFALL_THROUGH\n"
                "0x00477cb0\t0x00477cb0\tAFTER\t10\t0x00477cc8\t0x00477cb0\tCSquadNormal__SelectBestEngagementTarget\tMOV\tESI, 0x8550b0\tbe b0 50 85 00\tFALL_THROUGH\n"
                "0x00477cb0\t0x00477cb0\tAFTER\t14\t0x00477cd3\t0x00477cb0\tCSquadNormal__SelectBestEngagementTarget\tMOV\tESI, 0x8550c0\tbe c0 50 85 00\tFALL_THROUGH\n"
                "0x00477cb0\t0x00477cb0\tAFTER\t22\t0x00477cf0\t0x00477cb0\tCSquadNormal__SelectBestEngagementTarget\tCALL\tdword ptr [EAX + 0x120]\tff 90 20 01 00 00\tCOMPUTED_CALL\n"
                "0x00477cb0\t0x00477cb0\tAFTER\t25\t0x00477cfb\t0x00477cb0\tCSquadNormal__SelectBestEngagementTarget\tCALL\tdword ptr [EDX + 0x124]\tff 92 24 01 00 00\tCOMPUTED_CALL\n"
                "0x00477cb0\t0x00477cb0\tAFTER\t108\t0x00477e03\t0x00477cb0\tCSquadNormal__SelectBestEngagementTarget\tCALL\t0x004e6680\te8 78 e8 06 00\tUNCONDITIONAL_CALL\n"
                "0x00477cb0\t0x00477cb0\tAFTER\t113\t0x00477e15\t0x00477cb0\tCSquadNormal__SelectBestEngagementTarget\tCALL\t0x004fb3d0\te8 b6 35 08 00\tUNCONDITIONAL_CALL\n"
                "0x00477cb0\t0x00477cb0\tAFTER\t166\t0x00477ec9\t0x00477cb0\tCSquadNormal__SelectBestEngagementTarget\tCALL\t0x004fb840\te8 72 39 08 00\tUNCONDITIONAL_CALL\n"
                "0x00477cb0\t0x00477cb0\tAFTER\t260\t0x00477fe4\t0x00477cb0\tCSquadNormal__SelectBestEngagementTarget\tMOV\tEAX, dword ptr [EDI + 0x148]\t8b 87 48 01 00 00\tFALL_THROUGH\n"
                "0x00477cb0\t0x00477cb0\tAFTER\t269\t0x00477ff7\t0x00477cb0\tCSquadNormal__SelectBestEngagementTarget\tRET\t0x4\tc2 04 00\tTERMINATOR\n",
                encoding="utf-8",
            )
            (decomp / "00477cb0_CSquadNormal__SelectBestEngagementTarget.c").write_text(
                "void * CSquadNormal__SelectBestEngagementTarget(void *squad) {\n"
                "  DAT_00855090; DAT_008550b0; DAT_008550c0;\n"
                "  CSquadNormal__IsFactionCompatible();\n"
                "  CSquadNormal__IsValidLinkedSupportForTarget();\n"
                "  CSquadNormal__SelectBestSupportOrEscort();\n"
                "  CSquadNormal__GetSupportMinEngageDistance();\n"
                "  CSquadNormal__GetSupportMaxEngageDistance();\n"
                "  return *(void **)((int)candidate + 0x148);\n"
                "}\n",
                encoding="utf-8",
            )
            (base / "apply_squadnormal_select_target_wave408_dry.log").write_text(
                "SUMMARY updated=0 skipped=1 would_update=1 missing=0 bad=0\nREPORT: Save succeeded\n",
                encoding="utf-8",
            )
            (base / "apply_squadnormal_select_target_wave408_apply.log").write_text(
                "SUMMARY updated=1 skipped=0 would_update=0 missing=0 bad=0\nREPORT: Save succeeded\n",
                encoding="utf-8",
            )
            queue = root / "subagents" / "ghidra-static-reaudit" / "queue" / "current"
            queue.mkdir(parents=True)
            (queue / "static-reaudit-queue.json").write_text(
                json.dumps(
                    {
                        "totalFunctions": 6028,
                        "qualitySignals": {
                            "commentlessFunctionCount": 4467,
                            "undefinedSignatureCount": 1909,
                            "paramSignatureCount": 1855,
                        },
                    }
                ),
                encoding="utf-8",
            )
            note = root / "release" / "readiness" / "ghidra_squadnormal_select_target_wave408_2026-05-14.md"
            note.parent.mkdir(parents=True)
            note.write_text(
                "0x00477cb0 CSquadNormal__SelectBestEngagementTarget "
                "void * __stdcall CSquadNormal__SelectBestEngagementTarget(void * squad) "
                "RET 0x4 DAT_00855090 DAT_008550b0 DAT_008550c0 "
                "CSquadNormal__ScheduleTargetReaderRefresh 0x004ea584 no-function callsite "
                "does not prove exact CSquadNormal/source identity does not prove candidate struct layout "
                "does not prove global list semantics does not prove runtime AI behavior does not prove rebuild parity\n",
                encoding="utf-8",
            )

            result = probe.validate(root=root, base=base)
            self.assertEqual([], result.failures)

    def test_rejects_param_signature_debt(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "subagents" / "ghidra-static-reaudit" / "wave408_squadnormal_select_target" / "current"
            base.mkdir(parents=True)
            (base / "metadata_after.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x00477cb0\tCSquadNormal__SelectBestEngagementTarget\t"
                "int * __stdcall CSquadNormal__SelectBestEngagementTarget(void * param_1)\t\tOK\n",
                encoding="utf-8",
            )
            result = probe.validate(root=root, base=base)
            self.assertTrue(any("void * squad" in failure for failure in result.failures))

    def test_rejects_runtime_overclaim_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "subagents" / "ghidra-static-reaudit" / "wave408_squadnormal_select_target" / "current"
            base.mkdir(parents=True)
            note = root / "release" / "readiness" / "ghidra_squadnormal_select_target_wave408_2026-05-14.md"
            note.parent.mkdir(parents=True)
            note.write_text("runtime AI behavior proven\n", encoding="utf-8")
            result = probe.validate(root=root, base=base)
            self.assertTrue(any("overclaim" in failure for failure in result.failures))


if __name__ == "__main__":
    unittest.main()
