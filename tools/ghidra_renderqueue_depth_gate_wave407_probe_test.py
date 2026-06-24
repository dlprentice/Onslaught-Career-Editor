#!/usr/bin/env python3
"""Self-tests for the Wave407 render-queue depth gate probe."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import ghidra_renderqueue_depth_gate_wave407_probe as probe


class RenderQueueDepthGateWave407ProbeTests(unittest.TestCase):
    def test_accepts_expected_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "subagents" / "ghidra-static-reaudit" / "wave407-cvbuftexture-depth-queue" / "current"
            decomp = base / "decompile_after"
            decomp.mkdir(parents=True)

            (base / "metadata_before.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x00477b70\tCVBufTexture__QueueRenderIfDepthInRange\t"
                "void __thiscall CVBufTexture__QueueRenderIfDepthInRange(void * this, void * param_1, void * param_2, float param_3)\t\tOK\n",
                encoding="utf-8",
            )
            (base / "metadata_after.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x00477b70\tCRenderQueue__InsertIfDepthBelowIndexedLimit\t"
                "void __thiscall CRenderQueue__InsertIfDepthBelowIndexedLimit(void * this, void * item, float depth)\t"
                "Name/signature correction: render-queue depth-gated insert helper reached from CVBufTexture__RenderDynamicUnitPass. "
                "The caller sets ECX to global render queue &DAT_009c7550, pushes item and computed depth, and the target returns with RET 0x8. "
                "Body skips when DAT_0089d680 is set, compares depth against an indexed CRenderQueue limit at this+0x5bc*8+0x8, "
                "then calls CRenderQueue__InsertSortedByDepth(this,item,depth). Static retail evidence only; exact CRenderQueue layout, "
                "DAT_0089d680 semantics, runtime LOD/render behavior, and rebuild parity remain unproven.\tOK\n",
                encoding="utf-8",
            )
            (base / "tags_after.tsv").write_text(
                "address\tname\ttags\tstatus\n"
                "00477b70\tCRenderQueue__InsertIfDepthBelowIndexedLimit\tcomment-hardened;dynamic-unit-render;"
                "name-corrected;owner-corrected;render-queue;renderqueue-depth-gate-wave407;retail-binary-evidence;"
                "signature-hardened;static-reaudit\tOK\n",
                encoding="utf-8",
            )
            (base / "xrefs_after.tsv").write_text(
                "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
                "00477b70\tCRenderQueue__InsertIfDepthBelowIndexedLimit\t00477250\t00476fe0\t"
                "CVBufTexture__RenderDynamicUnitPass\tUNCONDITIONAL_CALL\n",
                encoding="utf-8",
            )
            (base / "instructions_after.tsv").write_text(
                "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
                "0x00477b70\t0x00477b70\tTARGET\t0\t0x00477b70\t0x00477b70\tCRenderQueue__InsertIfDepthBelowIndexedLimit\tMOV\tAL, [0x0089d680]\ta0 80 d6 89 00\tFALL_THROUGH\n"
                "0x00477b70\t0x00477b70\tAFTER\t3\t0x00477b79\t0x00477b70\tCRenderQueue__InsertIfDepthBelowIndexedLimit\tMOV\tEAX, dword ptr [ECX + 0x5bc]\t8b 81 bc 05 00 00\tFALL_THROUGH\n"
                "0x00477b70\t0x00477b70\tAFTER\t5\t0x00477b83\t0x00477b70\tCRenderQueue__InsertIfDepthBelowIndexedLimit\tFCOMP\tfloat ptr [ESP + 0x8]\td8 5c 24 08\tFALL_THROUGH\n"
                "0x00477b70\t0x00477b70\tAFTER\t13\t0x00477b98\t0x00477b70\tCRenderQueue__InsertIfDepthBelowIndexedLimit\tCALL\t0x005526c0\te8 23 ab 0d 00\tUNCONDITIONAL_CALL\n"
                "0x00477b70\t0x00477b70\tAFTER\t14\t0x00477b9d\t0x00477b70\tCRenderQueue__InsertIfDepthBelowIndexedLimit\tRET\t0x8\tc2 08 00\tTERMINATOR\n",
                encoding="utf-8",
            )
            (base / "callsite_instructions_after.tsv").write_text(
                "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
                "0x00477250\t0x00477250\tBEFORE\t-4\t0x00477246\t0x00476fe0\tCVBufTexture__RenderDynamicUnitPass\tPUSH\tECX\t51\tFALL_THROUGH\n"
                "0x00477250\t0x00477250\tBEFORE\t-3\t0x00477247\t0x00476fe0\tCVBufTexture__RenderDynamicUnitPass\tMOV\tECX, 0x9c7550\tb9 50 75 9c 00\tFALL_THROUGH\n"
                "0x00477250\t0x00477250\tBEFORE\t-2\t0x0047724c\t0x00476fe0\tCVBufTexture__RenderDynamicUnitPass\tFSTP\tfloat ptr [ESP]\td9 1c 24\tFALL_THROUGH\n"
                "0x00477250\t0x00477250\tBEFORE\t-1\t0x0047724f\t0x00476fe0\tCVBufTexture__RenderDynamicUnitPass\tPUSH\tESI\t56\tFALL_THROUGH\n"
                "0x00477250\t0x00477250\tTARGET\t0\t0x00477250\t0x00476fe0\tCVBufTexture__RenderDynamicUnitPass\tCALL\t0x00477b70\te8 1b 09 00 00\tUNCONDITIONAL_CALL\n",
                encoding="utf-8",
            )
            (decomp / "00477b70_CRenderQueue__InsertIfDepthBelowIndexedLimit.c").write_text(
                "void __thiscall CRenderQueue__InsertIfDepthBelowIndexedLimit(void *this,void *item,float depth) {\n"
                "  if ((DAT_0089d680 == '\\0') && (depth < *(float *)((int)this + *(int *)((int)this + 0x5bc) * 8 + 8))) {\n"
                "    CRenderQueue__InsertSortedByDepth(this,item,depth);\n"
                "  }\n"
                "}\n",
                encoding="utf-8",
            )
            (base / "apply_renderqueue_depth_gate_wave407_dry.log").write_text(
                "SUMMARY updated=0 skipped=1 renamed=0 would_rename=1 missing=0 bad=0\nREPORT: Save succeeded\n",
                encoding="utf-8",
            )
            (base / "apply_renderqueue_depth_gate_wave407_apply.log").write_text(
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
                            "commentlessFunctionCount": 4468,
                            "undefinedSignatureCount": 1909,
                            "paramSignatureCount": 1856,
                        },
                        "priorityQueues": {"commentlessHighSignal": [{"address": "0x00477cb0"}]},
                    }
                ),
                encoding="utf-8",
            )
            note = root / "release" / "readiness" / "ghidra_renderqueue_depth_gate_wave407_2026-05-14.md"
            note.parent.mkdir(parents=True)
            note.write_text(
                "0x00477b70 CVBufTexture__QueueRenderIfDepthInRange CRenderQueue__InsertIfDepthBelowIndexedLimit "
                "void __thiscall CRenderQueue__InsertIfDepthBelowIndexedLimit(void * this, void * item, float depth) "
                "CVBufTexture__RenderDynamicUnitPass ECX to global render queue &DAT_009c7550 RET 0x8 "
                "DAT_0089d680 CRenderQueue__InsertSortedByDepth does not prove exact CRenderQueue layout "
                "does not prove DAT_0089d680 semantics does not prove runtime LOD/render behavior "
                "does not prove rebuild parity\n",
                encoding="utf-8",
            )

            result = probe.validate(root=root, base=base)
            self.assertEqual([], result.failures)

    def test_rejects_stale_owner_and_extra_param_signature(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "subagents" / "ghidra-static-reaudit" / "wave407-cvbuftexture-depth-queue" / "current"
            base.mkdir(parents=True)
            (base / "metadata_after.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x00477b70\tCVBufTexture__QueueRenderIfDepthInRange\t"
                "void __thiscall CVBufTexture__QueueRenderIfDepthInRange(void * this, void * param_1, void * param_2, float param_3)\t\tOK\n",
                encoding="utf-8",
            )
            result = probe.validate(root=root, base=base)
            self.assertTrue(any("CRenderQueue__InsertIfDepthBelowIndexedLimit" in failure for failure in result.failures))

    def test_rejects_runtime_overclaim_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "subagents" / "ghidra-static-reaudit" / "wave407-cvbuftexture-depth-queue" / "current"
            base.mkdir(parents=True)
            note = root / "release" / "readiness" / "ghidra_renderqueue_depth_gate_wave407_2026-05-14.md"
            note.parent.mkdir(parents=True)
            note.write_text("runtime LOD/render behavior proven\n", encoding="utf-8")
            result = probe.validate(root=root, base=base)
            self.assertTrue(any("overclaim" in failure for failure in result.failures))


if __name__ == "__main__":
    unittest.main()
