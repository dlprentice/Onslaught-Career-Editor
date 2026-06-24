#!/usr/bin/env python3
"""Self-tests for the Carrier/Carver Ghidra boundary/signature correction probe."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_carrier_carver_boundary_signature_correction_probe.py"

FINAL_ROWS = [
    ("0x00421a80", "CCarrier__Init", "void __thiscall CCarrier__Init(void * this, void * init)"),
    ("0x00421b80", "CCarrierAI__scalar_deleting_dtor", "void * __thiscall CCarrierAI__scalar_deleting_dtor(void * this, byte flags)"),
    ("0x00421ba0", "CCarrierAI__dtor_base", "void __fastcall CCarrierAI__dtor_base(void * this)"),
    ("0x00421c40", "CUnit__ApplyFlag4DampingAndScaleSpeed", "void __fastcall CUnit__ApplyFlag4DampingAndScaleSpeed(void * this)"),
    ("0x00422440", "CCarver__Init", "void __thiscall CCarver__Init(void * this, void * init)"),
    ("0x00422560", "CCarverAI__scalar_deleting_dtor", "void * __thiscall CCarverAI__scalar_deleting_dtor(void * this, byte flags)"),
    ("0x00422580", "CCarverAI__dtor_base", "void __fastcall CCarverAI__dtor_base(void * this)"),
    ("0x00422620", "CCarver__UpdateMotionAndWingPose", "void __fastcall CCarver__UpdateMotionAndWingPose(void * this)"),
    ("0x00422760", "CCarverAI__OpenWings", "void __fastcall CCarverAI__OpenWings(void * this)"),
    ("0x004227a0", "CCarverAI__CloseWings", "void __fastcall CCarverAI__CloseWings(void * this)"),
    ("0x004227e0", "CCarverAI__OnHit", "void __thiscall CCarverAI__OnHit(void * this, void * otherThing, void * collisionReport)"),
    ("0x00422820", "CCarverAI__Fire", "int __fastcall CCarverAI__Fire(void * this)"),
    ("0x00422930", "CCarverAI__SetLastAttackTime", "void __fastcall CCarverAI__SetLastAttackTime(void * this)"),
    ("0x00422940", "CCarverAI__IsRecentlyAttacked", "int __fastcall CCarverAI__IsRecentlyAttacked(void * this)"),
    ("0x00422970", "CCarverAI__CanStartAttack", "int __fastcall CCarverAI__CanStartAttack(void * this)"),
    ("0x004229b0", "CarverAimGlobals__ResetVector", "void __cdecl CarverAimGlobals__ResetVector(void)"),
    ("0x004229d0", "CarverAimGlobals__InitMatrix", "void __cdecl CarverAimGlobals__InitMatrix(void)"),
    ("0x00422aa0", "CCarverAI__RefreshTargetReaderAndScheduleMove", "void __thiscall CCarverAI__RefreshTargetReaderAndScheduleMove(void * this, void * event)"),
    ("0x00422b90", "CCarverAI__UpdateAttackAndReschedule", "void __thiscall CCarverAI__UpdateAttackAndReschedule(void * this, void * event)"),
    ("0x00422db0", "CCarverAI__CheckNearbyEnemies", "void __fastcall CCarverAI__CheckNearbyEnemies(void * this)"),
    ("0x00422f90", "CCarverGuide__ctor", "void * __thiscall CCarverGuide__ctor(void * this, void * guideTarget)"),
    ("0x00422fb0", "CCarverGuide__scalar_deleting_dtor", "void * __thiscall CCarverGuide__scalar_deleting_dtor(void * this, byte flags)"),
    ("0x00422fd0", "CCarverGuide__dtor_base", "void __fastcall CCarverGuide__dtor_base(void * this)"),
    ("0x00423490", "CCarverGuide__HandleEvent", "void __thiscall CCarverGuide__HandleEvent(void * this, void * event)"),
]

AFTER_CREATE_NAMES = {
    "0x00421a80": "CCarrier__Init",
    "0x00421b80": "CCarrierAI__VFunc_01_00421b80",
    "0x00421ba0": "CUnitAI__ctor_like_00421ba0",
    "0x00421c40": "CUnit__ApplyFlag4DampingAndScaleSpeed_00421c40",
    "0x00422440": "CCarver__Init_candidate",
    "0x00422560": "CCarverAI__ScalarDeletingDestructor",
    "0x00422580": "CCarverAI__Destructor",
    "0x00422620": "CCarver__Process_candidate",
    "0x00422760": "CCarverAI__OpenWings",
    "0x004227a0": "CCarverAI__CloseWings",
    "0x004227e0": "CCarverAI__OnHit",
    "0x00422820": "CCarverAI__Fire",
    "0x00422930": "CCarverAI__SetLastAttackTime",
    "0x00422940": "CCarverAI__IsRecentlyAttacked",
    "0x00422970": "CCarverAI__CanAttack_candidate",
    "0x004229b0": "CCarverAimGlobals__Reset_candidate",
    "0x004229d0": "CCarverAimGlobals__InitMatrix_candidate",
    "0x00422aa0": "CCarverAI__Event3000Candidate",
    "0x00422b90": "CCarverAI__UpdateAttackCandidate",
    "0x00422db0": "CCarverAI__CheckNearbyEnemies",
    "0x00422f90": "CCarverGuide__Constructor",
    "0x00422fb0": "CCarverGuide__ScalarDeletingDestructor",
    "0x00422fd0": "CCarverGuide__Destructor",
    "0x00423490": "CCarverGuide__HandleEvent_candidate",
}

CREATED_BOUNDARY_NAMES = {
    "0x00422440": "CCarver__Init_candidate",
    "0x00422620": "CCarver__Process_candidate",
    "0x00422970": "CCarverAI__CanAttack_candidate",
    "0x004229b0": "CCarverAimGlobals__Reset_candidate",
    "0x004229d0": "CCarverAimGlobals__InitMatrix_candidate",
    "0x00422aa0": "CCarverAI__Event3000Candidate",
    "0x00422b90": "CCarverAI__UpdateAttackCandidate",
    "0x00423490": "CCarverGuide__HandleEvent_candidate",
}


def load_module():
    spec = importlib.util.spec_from_file_location("probe", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CarrierCarverBoundarySignatureCorrectionProbeTests(unittest.TestCase):
    def write_fixture(
        self,
        root: Path,
        *,
        stale_final_name: bool = False,
        omit_created_boundary: bool = False,
    ) -> dict[str, Path]:
        decompile_dir = root / "decompile_final"
        decompile_dir.mkdir(parents=True)
        created = root / "create_missing_boundaries_apply.tsv"
        after_create = root / "metadata_after_create.tsv"
        metadata = root / "metadata_final.tsv"
        index = decompile_dir / "index.tsv"
        xrefs = root / "xrefs_final.tsv"
        instructions = root / "instructions_final.tsv"
        queue = root / "static-reaudit-queue.json"
        baseline = root / "static-reaudit-baseline.json"

        created_items = list(CREATED_BOUNDARY_NAMES.items())
        if omit_created_boundary:
            created_items = created_items[:-1]
        created.write_text(
            "address\tstatus\tname\tsignature\tnote\n"
            + "\n".join(
                f"{address[2:]}\tcreated\t{name}\tundefined {name}(void)\tdisassemble+create succeeded; renamed"
                for address, name in created_items
            )
            + "\n",
            encoding="utf-8",
        )

        after_rows = []
        final_rows = []
        index_rows = []
        probe = load_module()
        for address, name, signature in FINAL_ROWS:
            after_name = AFTER_CREATE_NAMES[address]
            after_rows.append((address, after_name, f"undefined {after_name}(void)", "", "OK"))
            final_name = "CCarver__Init_candidate" if stale_final_name and address == "0x00422440" else name
            comment = "; ".join(probe.TARGETS[address]["comment"])
            final_rows.append((address, final_name, signature.replace(name, final_name), comment, "OK"))
            index_rows.append((address, final_name, signature.replace(name, final_name), "OK"))
            (decompile_dir / f"{address[2:]}_{final_name}.c").write_text(
                f"/* {comment} */\n{signature.replace(name, final_name)} {{}}\n",
                encoding="utf-8",
            )

        after_create.write_text(
            "address\tname\tsignature\tcomment\tstatus\n"
            + "\n".join("\t".join(row) for row in after_rows)
            + "\n",
            encoding="utf-8",
        )
        metadata.write_text(
            "address\tname\tsignature\tcomment\tstatus\n"
            + "\n".join("\t".join(row) for row in final_rows)
            + "\n",
            encoding="utf-8",
        )
        index.write_text(
            "address\tname\tsignature\tstatus\n"
            + "\n".join("\t".join(row) for row in index_rows)
            + "\n",
            encoding="utf-8",
        )
        xrefs.write_text(
            "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
            + "\n".join(
                f"{address[2:]}\t{name}\t005e0000\t<none>\t<no_function>\tDATA"
                for i in range(2)
                for address, name, _signature in FINAL_ROWS
            )
            + "\n",
            encoding="utf-8",
        )
        instructions.write_text(
            "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
            + "\n".join(
                f"{address}\t{address}\tTARGET\t{i}\t{address}\t{address}\t{name}\tMOV\tEAX, EAX\t00\tFALL_THROUGH"
                for i in range(81)
                for address, name, _signature in FINAL_ROWS
            )
            + "\n",
            encoding="utf-8",
        )
        queue.write_text(
            json.dumps(
                {
                    "status": "PASS",
                    "totalFunctions": 5876,
                    "qualitySignals": {
                        "commentlessFunctionCount": 5193,
                        "undefinedSignatureCount": 2032,
                        "paramSignatureCount": 2330,
                        "uncertainOwnerNameCount": 0,
                        "helperAddressNameCount": 0,
                        "wrapperAddressNameCount": 0,
                    },
                }
            ),
            encoding="utf-8",
        )
        baseline.write_text(
            json.dumps(
                {
                    "status": "PASS",
                    "totalFunctions": 5876,
                    "qualitySignals": {
                        "undefinedSignatureCount": 2032,
                        "paramSignatureCount": 2330,
                        "uncertainOwnerNameCount": 0,
                        "helperAddressNameCount": 0,
                        "wrapperAddressNameCount": 0,
                    },
                }
            ),
            encoding="utf-8",
        )
        return {
            "created_boundaries_path": created,
            "metadata_after_create_path": after_create,
            "metadata_final_path": metadata,
            "decompile_index_path": index,
            "decompile_dir": decompile_dir,
            "xrefs_path": xrefs,
            "instructions_path": instructions,
            "queue_json_path": queue,
            "baseline_json_path": baseline,
        }

    def test_accepts_carrier_carver_boundary_signature_readback(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_fixture(Path(tmp))
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["createdBoundaryCount"], 8)
        self.assertEqual(report["signatureCorrectedTargets"], 24)
        self.assertEqual(report["renamedTargets"], 16)
        self.assertEqual(report["instructionRows"], 1944)

    def test_rejects_stale_candidate_final_name(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_fixture(Path(tmp), stale_final_name=True)
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("CCarver__Init_candidate" in failure for failure in report["failures"]))

    def test_rejects_missing_created_boundary(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_fixture(Path(tmp), omit_created_boundary=True)
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("created boundary count" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
