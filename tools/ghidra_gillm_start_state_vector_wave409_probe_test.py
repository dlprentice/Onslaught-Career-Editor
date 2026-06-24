#!/usr/bin/env python3
"""Self-tests for the Wave409 CGillM state-vector correction probe."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import ghidra_gillm_start_state_vector_wave409_probe as probe


class GillMStartStateVectorWave409ProbeTests(unittest.TestCase):
    def test_accepts_expected_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "subagents" / "ghidra-static-reaudit" / "wave409_explosion_start_state1_motion" / "current"
            decomp = base / "decompile_after"
            decomp.mkdir(parents=True)

            (base / "metadata_before.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x0047a160\tCExplosionInitThing__StartState1WithStoredMotionVector\t"
                "void __fastcall CExplosionInitThing__StartState1WithStoredMotionVector(void * param_1)\t\tOK\n",
                encoding="utf-8",
            )
            (base / "metadata_after.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x0047a160\tCGillM__StartState1WithStoredMotionVector\t"
                "void __thiscall CGillM__StartState1WithStoredMotionVector(void * this)\t"
                "Wave409 owner/signature correction from the older CExplosionInitThing label: CGillM RTTI vtable 0x005e0b30 slot 100 points here. The body skips when state field +0x244 is already 1 or 2, copies the stored four-dword motion vector at +0x278 into a virtual dispatch at vtable +0xf4 with a zero flag, then sets +0x244 to 1. Static retail evidence only; exact source virtual name, concrete CGillM layout, runtime movement behavior, and rebuild parity remain unproven.\tOK\n",
                encoding="utf-8",
            )
            (base / "tags_after.tsv").write_text(
                "address\tname\ttags\tstatus\n"
                "0047a160\tCGillM__StartState1WithStoredMotionVector\tcgillm;comment-hardened;"
                "gillm-start-state-vector-wave409;motion-vector;owner-corrected;retail-binary-evidence;"
                "signature-hardened;state-transition;static-reaudit;vtable-slot\tOK\n",
                encoding="utf-8",
            )
            (base / "xrefs_after.tsv").write_text(
                "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
                "0047a160\tCGillM__StartState1WithStoredMotionVector\t005e0cc0\t<none>\t<no_function>\tDATA\n",
                encoding="utf-8",
            )
            (base / "cgillm_vtable_slots_after.tsv").write_text(
                "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\tcontaining_entry\tcontaining_name\tstatus\n"
                "005e0b30\t66\t005e0c38\t0x00479d10\t00479d10\t00479d10\tCGillM__UpdateGroundedVerticalDrift\t00479d10\tCGillM__UpdateGroundedVerticalDrift\tOK\n"
                "005e0b30\t100\t005e0cc0\t0x0047a160\t0047a160\t0047a160\tCGillM__StartState1WithStoredMotionVector\t0047a160\tCGillM__StartState1WithStoredMotionVector\tOK\n"
                "005e0b30\t117\t005e0d04\t0x00479a50\t00479a50\t00479a50\tCGillM__InitLegMotion\t00479a50\tCGillM__InitLegMotion\tOK\n"
                "005e0b30\t118\t005e0d08\t0x00479b60\t00479b60\t00479b60\tCGillM__InitGillMAIComponent\t00479b60\tCGillM__InitGillMAIComponent\tOK\n"
                "005e0b30\t119\t005e0d0c\t0x00479cb0\t00479cb0\t00479cb0\tCGillM__InitTerrainGuideComponent\t00479cb0\tCGillM__InitTerrainGuideComponent\tOK\n",
                encoding="utf-8",
            )
            (base / "instructions_after.tsv").write_text(
                "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
                "0x0047a160\t0x0047a160\tAFTER\t1\t0x0047a161\t0x0047a160\tCGillM__StartState1WithStoredMotionVector\tMOV\tESI, ECX\t8b f1\tFALL_THROUGH\n"
                "0x0047a160\t0x0047a160\tAFTER\t4\t0x0047a16a\t0x0047a160\tCGillM__StartState1WithStoredMotionVector\tCMP\tEAX, 0x1\t83 f8 01\tFALL_THROUGH\n"
                "0x0047a160\t0x0047a160\tAFTER\t6\t0x0047a16f\t0x0047a160\tCGillM__StartState1WithStoredMotionVector\tCMP\tEAX, 0x2\t83 f8 02\tFALL_THROUGH\n"
                "0x0047a160\t0x0047a160\tAFTER\t8\t0x0047a174\t0x0047a160\tCGillM__StartState1WithStoredMotionVector\tPUSH\t0x0\t6a 00\tFALL_THROUGH\n"
                "0x0047a160\t0x0047a160\tAFTER\t9\t0x0047a176\t0x0047a160\tCGillM__StartState1WithStoredMotionVector\tLEA\tECX, [ESI + 0x278]\t8d 8e 78 02 00 00\tFALL_THROUGH\n"
                "0x0047a160\t0x0047a160\tAFTER\t22\t0x0047a19b\t0x0047a160\tCGillM__StartState1WithStoredMotionVector\tCALL\tdword ptr [EAX + 0xf4]\tff 90 f4 00 00 00\tCOMPUTED_CALL\n"
                "0x0047a160\t0x0047a160\tAFTER\t23\t0x0047a1a1\t0x0047a160\tCGillM__StartState1WithStoredMotionVector\tMOV\tdword ptr [ESI + 0x244], 0x1\tc7 86 44 02 00 00 01 00 00 00\tFALL_THROUGH\n",
                encoding="utf-8",
            )
            (decomp / "0047a160_CGillM__StartState1WithStoredMotionVector.c").write_text(
                "void __thiscall CGillM__StartState1WithStoredMotionVector(void *this) {\n"
                "  if (*(int *)((int)this + 0x244) != 1 && *(int *)((int)this + 0x244) != 2) {\n"
                "    (*(code **)(*(int *)this + 0xf4))(*(undefined4 *)((int)this + 0x278),0);\n"
                "    *(undefined4 *)((int)this + 0x244) = 1;\n"
                "  }\n"
                "}\n",
                encoding="utf-8",
            )
            (base / "apply_gillm_start_state_vector_wave409_dry.log").write_text(
                "SUMMARY updated=0 skipped=1 renamed=0 would_rename=1 missing=0 bad=0\nREPORT: Save succeeded\n",
                encoding="utf-8",
            )
            (base / "apply_gillm_start_state_vector_wave409_apply.log").write_text(
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
                            "commentlessFunctionCount": 4466,
                            "undefinedSignatureCount": 1909,
                            "paramSignatureCount": 1854,
                        },
                    }
                ),
                encoding="utf-8",
            )
            note = root / "release" / "readiness" / "ghidra_gillm_start_state_vector_wave409_2026-05-14.md"
            note.parent.mkdir(parents=True)
            note.write_text(
                "0x0047a160 CGillM__StartState1WithStoredMotionVector "
                "CGillM RTTI vtable 0x005e0b30 slot 100 0x005e0cc0 "
                "older CExplosionInitThing label vtable +0xf4 +0x244 +0x278 "
                "does not prove exact source virtual name does not prove concrete CGillM layout "
                "does not prove runtime movement behavior does not prove rebuild parity\n",
                encoding="utf-8",
            )

            result = probe.validate(root=root, base=base)
            self.assertEqual([], result.failures)

    def test_rejects_old_owner_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "subagents" / "ghidra-static-reaudit" / "wave409_explosion_start_state1_motion" / "current"
            base.mkdir(parents=True)
            (base / "metadata_after.tsv").write_text(
                "address\tname\tsignature\tcomment\tstatus\n"
                "0x0047a160\tCExplosionInitThing__StartState1WithStoredMotionVector\t"
                "void __fastcall CExplosionInitThing__StartState1WithStoredMotionVector(void * param_1)\t\tOK\n",
                encoding="utf-8",
            )
            result = probe.validate(root=root, base=base)
            self.assertTrue(any("CGillM__StartState1WithStoredMotionVector" in failure for failure in result.failures))

    def test_rejects_runtime_overclaim_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = root / "subagents" / "ghidra-static-reaudit" / "wave409_explosion_start_state1_motion" / "current"
            base.mkdir(parents=True)
            note = root / "release" / "readiness" / "ghidra_gillm_start_state_vector_wave409_2026-05-14.md"
            note.parent.mkdir(parents=True)
            note.write_text("runtime movement behavior proven\n", encoding="utf-8")
            result = probe.validate(root=root, base=base)
            self.assertTrue(any("overclaim" in failure for failure in result.failures))


if __name__ == "__main__":
    unittest.main()
