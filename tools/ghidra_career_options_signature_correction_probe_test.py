#!/usr/bin/env python3
"""Self-tests for the Career/options Ghidra correction probe."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_career_options_signature_correction_probe.py"


def load_module():
    spec = importlib.util.spec_from_file_location("probe", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CareerOptionsSignatureCorrectionProbeTests(unittest.TestCase):
    def write_fixture(self, root: Path, *, stale: bool = False) -> dict[str, Path]:
        decompile_dir = root / "decompile_final"
        decompile_dir.mkdir(parents=True)
        dry = root / "signature_correction_dry.log"
        apply = root / "signature_correction_apply.log"
        metadata = root / "metadata_final.tsv"
        index = decompile_dir / "index.tsv"
        xrefs = root / "xrefs_final.tsv"
        instructions = root / "instructions_final.tsv"

        dry.write_text("updated=0 skipped=3 renamed=0 missing=0 bad=0\n", encoding="utf-8")
        apply.write_text("updated=3 skipped=0 renamed=2 missing=0 bad=0\n", encoding="utf-8")

        name_20cd0 = "CCareer__GetSlotRecordPtr" if stale else "D3DDeviceProfileTable__GetAdapterRecord"
        metadata.write_text(
            "\n".join(
                [
                    "address\tname\tsignature\tcomment\tstatus",
                    "0x0041bd00\tCCareer__Update\tvoid __fastcall CCareer__Update(void * this)\tSource-parity career end-level update copies END_LEVEL_DATA slots, updates kills/ranking/complete state, sets mCareerInProgress, recalculates links, updates goodies; runtime save behavior remains unproven.\tOK",
                    f"0x00420cd0\t{name_20cd0}\tvoid * __thiscall {name_20cd0}(void * this, int adapterIndex)\tName correction: not a CCareer helper; indexes DAT_00855bb0 display/profile table base using 0x516c stride and active-adapter fallback at +0x32e40; table layout and runtime display behavior remain unproven.\tOK",
                    "0x00420d10\tD3DDeviceProfile__PackDeviceIndexKey\tvoid __thiscall D3DDeviceProfile__PackDeviceIndexKey(void * this, void * modeRecord)\tName correction: not a CCareer helper; packs a display mode/profile record into the persisted g_D3DDeviceIndex-style key at the this output pointer using low 16 bits, 0x7fff shifted mode bits, and high-bit format marker for 0x14/0x15/0x16; runtime display behavior remains unproven.\tOK",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        index.write_text(
            "\n".join(
                [
                    "address\tname\tsignature\tstatus",
                    "0x0041bd00\tCCareer__Update\tvoid __fastcall CCareer__Update(void * this)\tOK",
                    f"0x00420cd0\t{name_20cd0}\tvoid * __thiscall {name_20cd0}(void * this, int adapterIndex)\tOK",
                    "0x00420d10\tD3DDeviceProfile__PackDeviceIndexKey\tvoid __thiscall D3DDeviceProfile__PackDeviceIndexKey(void * this, void * modeRecord)\tOK",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (decompile_dir / "0041bd00_CCareer__Update.c").write_text(
            "void __fastcall CCareer__Update(void *this) { CCareer__UpdateThingsKilled(this); CCareer__ReCalcLinks(); CCareer__UpdateGoodieStates(this); }\n",
            encoding="utf-8",
        )
        (decompile_dir / f"00420cd0_{name_20cd0}.c").write_text(
            "void * __thiscall D3DDeviceProfileTable__GetAdapterRecord(void *this,int adapterIndex) { return (void *)((int)this + adapterIndex * 0x516c + 4); }\n",
            encoding="utf-8",
        )
        (decompile_dir / "00420d10_D3DDeviceProfile__PackDeviceIndexKey.c").write_text(
            "void __thiscall D3DDeviceProfile__PackDeviceIndexKey(void *this, void *modeRecord) { int format = *(int *)((int)modeRecord + 8); if ((format == 0x16) || (format == 0x15) || (format == 0x14)) { *(uint *)this = 0x80000000; } *(uint *)this |= (*(uint *)modeRecord & 0xffff) | ((*(uint *)((int)modeRecord + 4) & 0x7fff) << 0x10); }\n",
            encoding="utf-8",
        )
        xrefs.write_text(
            "\n".join(
                [
                    "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type",
                    "0041bd00\tCCareer__Update\t00466315\t004662a0\tCFrontEnd__Init\tUNCONDITIONAL_CALL",
                    "00420cd0\tD3DDeviceProfileTable__GetAdapterRecord\t00420b41\t00420b10\tOptionsTail_Write\tUNCONDITIONAL_CALL",
                    "00420d10\tD3DDeviceProfile__PackDeviceIndexKey\t00420b76\t00420b10\tOptionsTail_Write\tUNCONDITIONAL_CALL",
                    "00420d10\tD3DDeviceProfile__PackDeviceIndexKey\t00420dd5\t00420d70\tOptionsTail_Read\tUNCONDITIONAL_CALL",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        instructions.write_text(
            "\n".join(
                [
                    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type",
                    "0x0041bd00\t0x0041bd00\tTARGET\t0\t0x0041bd00\t0x0041bd00\tCCareer__Update\tMOV\tEAX, [0x00672e1c]\ta1 1c 2e 67 00\tFALL_THROUGH",
                    "0x00420cd0\t0x00420cd0\tAFTER\t1\t0x00420cd0\t0x00420cd0\tD3DDeviceProfileTable__GetAdapterRecord\tIMUL\tadapterIndex, 0x516c\t00\tFALL_THROUGH",
                    "0x00420d10\t0x00420d10\tAFTER\t1\t0x00420d10\t0x00420d10\tD3DDeviceProfile__PackDeviceIndexKey\tAND\t0x7fff\t00\tFALL_THROUGH",
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
        }

    def test_accepts_corrected_readback(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_fixture(Path(tmp))
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["renamedTargets"], 2)

    def test_rejects_stale_career_owner_for_options_helper(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_fixture(Path(tmp), stale=True)
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("0x00420cd0" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
