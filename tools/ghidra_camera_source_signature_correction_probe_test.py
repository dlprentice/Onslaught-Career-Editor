#!/usr/bin/env python3
"""Self-tests for the Camera source/signature Ghidra correction probe."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_camera_source_signature_correction_probe.py"


def load_module():
    spec = importlib.util.spec_from_file_location("probe", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CameraSourceSignatureCorrectionProbeTests(unittest.TestCase):
    def write_fixture(self, root: Path, *, stale_viewpoint_name: bool = False, stale_controllable_signature: bool = False) -> dict[str, Path]:
        decompile_dir = root / "decompile_final"
        decompile_dir.mkdir(parents=True)
        dry = root / "signature_correction_dry.log"
        apply = root / "signature_correction_apply.log"
        metadata = root / "metadata_final.tsv"
        index = decompile_dir / "index.tsv"
        xrefs = root / "xrefs_final.tsv"
        instructions = root / "instructions_final.tsv"
        callsites = root / "callsites_instructions_before.tsv"

        dry.write_text("updated=0 skipped=9 renamed=0 missing=0 bad=0\n", encoding="utf-8")
        apply.write_text("updated=9 skipped=0 renamed=1 missing=0 bad=0\n", encoding="utf-8")

        viewpoint_name = "CViewPointCamera__ctor_like_00419e00" if stale_viewpoint_name else "CViewPointCamera__ctor"
        controllable_signature = (
            "undefined CControllableCamera__ctor(void)"
            if stale_controllable_signature
            else "void * __thiscall CControllableCamera__ctor(void * this, float posX, float posY, float posZ, float posW, float orientation00, float orientation01, float orientation02, float orientation03, float orientation10, float orientation11, float orientation12, float orientation13, float orientation20, float orientation21, float orientation22, float orientation23)"
        )

        rows = [
            ("0x00418ef0", "CThing3rdPersonCamera__ctor", "void * __thiscall CThing3rdPersonCamera__ctor(void * this, void * forThing)", "Source-parity Camera.cpp constructor: active reader plus CBSpline control points from GetRadius; static source/decompile/xref evidence only; runtime camera behavior remains unproven."),
            ("0x00419120", "CThing3rdPersonCamera__scalar_deleting_dtor", "void * __thiscall CThing3rdPersonCamera__scalar_deleting_dtor(void * this, byte flags)", "MSVC scalar deleting destructor wrapper for CThing3rdPersonCamera; source/decompile/vtable evidence only; concrete layouts remain unproven."),
            ("0x00419140", "CThing3rdPersonCamera__dtor", "void __fastcall CThing3rdPersonCamera__dtor(void * this)", "Source-parity destructor releases mCurve and active-reader link; static source/decompile evidence only; runtime behavior remains unproven."),
            ("0x004198d0", "CPanCamera__ctor", "void * __thiscall CPanCamera__ctor(void * this, void * forThing, void * curve, float length)", "Source-parity CPanCamera constructor stores tracked thing/curve/start-time/length and seeds current/old camera state; static source/decompile/xref evidence only; runtime pan-camera behavior remains unproven."),
            ("0x00419a40", "CPanCamera__scalar_deleting_dtor", "void * __thiscall CPanCamera__scalar_deleting_dtor(void * this, byte flags)", "MSVC scalar deleting destructor wrapper for CPanCamera; vtable/decompile evidence only; concrete layouts remain unproven."),
            ("0x00419a60", "CPanCamera__dtor", "void __fastcall CPanCamera__dtor(void * this)", "Source-parity CPanCamera destructor deletes owned curve and unregisters active-reader link; static evidence only; runtime behavior remains unproven."),
            ("0x00419b00", "CPanCamera__Update", "void __fastcall CPanCamera__Update(void * this)", "Source-parity CPanCamera update samples CBSpline by event-manager time and schedules UPDATE_CAMERA; static evidence only; runtime behavior remains unproven."),
            ("0x00419e00", viewpoint_name, f"void * __thiscall {viewpoint_name}(void * this, void * point, float * rotateSpeed, float * startDistance, float * endDistance, float * timeBetweenDistance)", "Name/signature correction: source-aligned CViewPointCamera constructor copies look-at point, distance/rotation references, default orientation, and cached old values; static source/decompile/callsite evidence only; runtime death-camera behavior remains unproven."),
            ("0x0041a740", "CControllableCamera__ctor", controllable_signature, "Signature hardening: source-aligned CControllableCamera constructor takes FVector pos and FMatrix orientation by value, seeds current/old/temp camera state, and stores frame-count snapshot; static source/decompile/callsite evidence only; runtime free-camera behavior remains unproven."),
        ]
        metadata.write_text(
            "address\tname\tsignature\tcomment\tstatus\n"
            + "\n".join("\t".join(row + ("OK",)) for row in rows)
            + "\n",
            encoding="utf-8",
        )
        index.write_text(
            "address\tname\tsignature\tstatus\n"
            + "\n".join(f"{address}\t{name}\t{signature}\tOK" for address, name, signature, _comment in rows)
            + "\n",
            encoding="utf-8",
        )

        for address, name, signature, _comment in rows:
            body = f"/* signature: {signature} */\nvoid sample_{address[2:]}() {{}}\n"
            if address == "0x00418ef0":
                body += "CBSpline(points); GetRadius();\n"
            elif address == "0x00419120":
                body += "CThing3rdPersonCamera__dtor(this); OID__FreeObject(this);\n"
            elif address == "0x00419140":
                body += "CSPtrSet__Remove(activeReaderOwner, this);\n"
            elif address == "0x004198d0":
                body += "DAT_00672fd0; CPanCamera__Update(this);\n"
            elif address == "0x00419a40":
                body += "CPanCamera__dtor(this); OID__FreeObject(this);\n"
            elif address == "0x00419a60":
                body += "CSPtrSet__Remove(activeReaderOwner, this); CMonitor__Shutdown(this);\n"
            elif address == "0x00419b00":
                body += "CBSpline__GetPoint(); CEventManager__AddEvent_TimeFromNow(&EVENT_MANAGER);\n"
            elif address == "0x00419e00":
                body += "CViewPointCamera__ctor copies point and float references; DAT_00660588;\n"
            elif address == "0x0041a740":
                body += "CControllableCamera__ctor copies posX orientation00 orientation23 DAT_006605c8;\n"
            (decompile_dir / f"{address[2:]}_{name}.c").write_text(body, encoding="utf-8")

        xrefs.write_text(
            "\n".join(
                [
                    "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type",
                    "00418ef0\tCThing3rdPersonCamera__ctor\t004d2a12\t004d29c0\tCPlayer__Goto3rdPersonView\tUNCONDITIONAL_CALL",
                    "00419120\tCThing3rdPersonCamera__scalar_deleting_dtor\t005d9250\t<none>\t<no_function>\tDATA",
                    "00419140\tCThing3rdPersonCamera__dtor\t00419123\t00419120\tCThing3rdPersonCamera__scalar_deleting_dtor\tUNCONDITIONAL_CALL",
                    "004198d0\tCPanCamera__ctor\t004d2f66\t004d2c10\tCPlayer__GotoPanView\tUNCONDITIONAL_CALL",
                    "00419a40\tCPanCamera__scalar_deleting_dtor\t005d92c8\t<none>\t<no_function>\tDATA",
                    "00419a60\tCPanCamera__dtor\t00419a43\t00419a40\tCPanCamera__scalar_deleting_dtor\tUNCONDITIONAL_CALL",
                    "00419b00\tCPanCamera__Update\t004199d5\t004198d0\tCPanCamera__ctor\tUNCONDITIONAL_CALL",
                    f"00419e00\t{viewpoint_name}\t0046f662\t0046f550\tCGame__DeclarePlayerDead\tUNCONDITIONAL_CALL",
                    "0041a740\tCControllableCamera__ctor\t00470557\t00470430\tCGame__ToggleFreeCameraOn\tUNCONDITIONAL_CALL",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        instructions.write_text(
            "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
            + "\n".join(
                f"{address}\t{address}\tTARGET\t0\t{address}\t{address}\t{name}\tMOV\tEAX, EAX\t00\tFALL_THROUGH"
                for address, name, _signature, _comment in rows
            )
            + "\n",
            encoding="utf-8",
        )
        callsites.write_text(
            "\n".join(
                [
                    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type",
                    "0x0046f662\t0x0046f662\tTARGET\t0\t0x0046f662\t0x0046f550\tCGame__DeclarePlayerDead\tCALL\t0x00419e00\te8 99 a7 fa ff\tUNCONDITIONAL_CALL",
                    "0x00470557\t0x00470557\tBEFORE\t-10\t0x0047053a\t0x00470430\tCGame__ToggleFreeCameraOn\tSUB\tESP, 0x10\t83 ec 10\tFALL_THROUGH",
                    "0x00470557\t0x00470557\tTARGET\t0\t0x00470557\t0x00470430\tCGame__ToggleFreeCameraOn\tCALL\t0x0041a740\te8 e4 a1 fa ff\tUNCONDITIONAL_CALL",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return {
            "dry_log_path": dry,
            "apply_log_path": apply,
            "metadata_path": metadata,
            "decompile_index_path": index,
            "decompile_dir": decompile_dir,
            "xrefs_path": xrefs,
            "instructions_path": instructions,
            "callsites_path": callsites,
        }

    def test_accepts_camera_source_signature_readback(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_fixture(Path(tmp))
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["renamedTargets"], 1)

    def test_rejects_stale_viewpoint_constructor_like_name(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_fixture(Path(tmp), stale_viewpoint_name=True)
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("CViewPointCamera__ctor_like_00419e00" in failure for failure in report["failures"]))

    def test_rejects_undefined_controllable_ctor_signature(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_fixture(Path(tmp), stale_controllable_signature=True)
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("undefined CControllableCamera__ctor(void)" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
