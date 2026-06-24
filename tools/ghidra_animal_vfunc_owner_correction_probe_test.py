#!/usr/bin/env python3
"""Tests for the CAnimal vfunc owner/name correction probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_animal_vfunc_owner_correction_probe as probe


TARGET_ROWS = {
    "0x00403d30": (
        "CAnimal__Init",
        "void __thiscall CAnimal__Init(void * this, void * init)",
        "CAnimal init correction vtable slot 9 bird_msh CComplexThing__Init event 3000",
        "CAnimal__Init CComplexThing__Init bird_msh CEventManager__AddEvent_AtTime 3000",
    ),
    "0x00404010": (
        "CAnimal__dtor_base",
        "void __fastcall CAnimal__dtor_base(void * this)",
        "CAnimal destructor-base correction vtable 0x005d8698 linked list DAT_00660130 CComplexThing__dtor_base",
        "CAnimal__dtor_base PTR_LAB_005d8698 DAT_00660130 CComplexThing__dtor_base",
    ),
    "0x004041f0": (
        "CAnimal__scalar_deleting_dtor",
        "void * __thiscall CAnimal__scalar_deleting_dtor(void * this, byte flags)",
        "CAnimal scalar-deleting destructor calls CAnimal__dtor_base flags&1 optionally frees this",
        "CAnimal__scalar_deleting_dtor CAnimal__dtor_base OID__FreeObject",
    ),
}


def write_fixture(root: Path, *, stale: bool = False) -> dict[str, Path]:
    apply_dry = root / "apply_dry.log"
    apply = root / "apply.log"
    metadata = root / "metadata_final.tsv"
    decompile = root / "decompile_final"
    xrefs = root / "xrefs_final.tsv"
    instructions = root / "instructions_final.tsv"
    vtable_types = root / "vtable_types.tsv"
    decompile.mkdir()

    apply_dry.write_text("--- SUMMARY ---\nupdated=0 skipped=3 missing=0 bad=0\n", encoding="utf-8")
    apply.write_text("--- SUMMARY ---\nupdated=3 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    rows = dict(TARGET_ROWS)
    if stale:
        rows["0x00404010"] = (
            "CAtmospheric__Destructor",
            "void __fastcall CAtmospheric__Destructor(void * this)",
            "Signature hardening for CAtmospheric destructor",
            "CAtmospheric__Destructor CComplexThing__dtor_base",
        )
        rows["0x004041f0"] = (
            "CAnimal__VFunc_01_004041f0",
            "void * __thiscall CAnimal__VFunc_01_004041f0(void * this, void * param_1, int param_2)",
            "",
            "CAnimal__VFunc_01_004041f0 CAtmospheric__Destructor param_1 param_2",
        )

    metadata.write_text(
        "address\tname\tsignature\tcomment\tstatus\n"
        + "".join(
            f"{address}\t{name}\t{signature}\t{comment}\tOK\n"
            for address, (name, signature, comment, _decompile) in rows.items()
        ),
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        "address\tname\tsignature\tstatus\n"
        + "".join(f"{address}\t{name}\t{signature}\tOK\n" for address, (name, signature, _comment, _decompile) in rows.items()),
        encoding="utf-8",
    )
    for address, (name, signature, _comment, decompile_text) in rows.items():
        (decompile / f"{address[2:]}_{name}.c").write_text(signature + " " + decompile_text, encoding="utf-8")

    xrefs.write_text(
        "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
        "00403d30\tCAnimal__Init\t005d86bc\t<none>\t<no_function>\tDATA\n"
        "004041f0\tCAnimal__scalar_deleting_dtor\t005d869c\t<none>\t<no_function>\tDATA\n",
        encoding="utf-8",
    )
    instructions.write_text(
        "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
        "0x00403d30\t0x00403d30\tAFTER\t148\t0x00403f3b\t0x00403d30\tCAnimal__Init\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        "0x004041f0\t0x004041f0\tAFTER\t10\t0x0040420d\t0x004041f0\tCAnimal__scalar_deleting_dtor\tRET\t0x4\tc2 04 00\tTERMINATOR\n",
        encoding="utf-8",
    )
    vtable_types.write_text(
        "vtable\tcol_ptr_slot\tcol_addr\tsignature\toffset\tcd_offset\ttype_desc\tclass_desc\traw_type_name\tdemangled_type_name\n"
        "005d8698\t005d8694\t0060c370\t0x00000000\t0\t0\t0x00622d58\t0x0060c360\t.?AVCAnimal@@\tCAnimal\n",
        encoding="utf-8",
    )
    return {
        "apply_dry": apply_dry,
        "apply": apply,
        "metadata": metadata,
        "decompile_index": decompile / "index.tsv",
        "decompile_dir": decompile,
        "xrefs": xrefs,
        "instructions": instructions,
        "vtable_types": vtable_types,
    }


class AnimalVfuncOwnerCorrectionProbeTests(unittest.TestCase):
    def test_passes_for_corrected_animal_tranche(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                apply_dry_log_path=paths["apply_dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
                vtable_types_path=paths["vtable_types"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], 3)
        self.assertEqual(report["summary"]["staleNameTokenHits"], 0)

    def test_fails_for_stale_atmospheric_and_generic_vfunc_names(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale=True)
            report = probe.build_report(
                apply_dry_log_path=paths["apply_dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
                vtable_types_path=paths["vtable_types"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("name mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("stale name/signature token" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
