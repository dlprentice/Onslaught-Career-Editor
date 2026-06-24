#!/usr/bin/env python3
"""Tests for the vector/geometry signature tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_vector_geometry_signature_tranche_probe as probe


TARGET_ROWS = {
    "0x0040d120": {
        "name": "Vec3__SubtractToOut",
        "signature": "void __thiscall Vec3__SubtractToOut(void * this, void * outVec, void * rhs)",
        "comment": "Signature hardening: Vec3 subtract helper reads ECX as lhs, stack arg1 as outVec, stack arg2 as rhs, writes three output lanes, and returns with ret 0x8. Not concrete Vec3 layout, exact source identity, runtime behavior, tags, locals, or rebuild parity proof.",
        "decompile": "Vec3__SubtractToOut this outVec rhs",
        "ret": "0x8",
    },
    "0x0040d150": {
        "name": "Vec3__ScaleToOut",
        "signature": "void __thiscall Vec3__ScaleToOut(void * this, void * outVec, float scale)",
        "comment": "Signature hardening: Vec3 scale helper reads ECX as input vector, stack arg1 as outVec, stack arg2 as scale, writes three output lanes, and returns with ret 0x8. Not concrete Vec3 layout, exact source identity, runtime behavior, tags, locals, or rebuild parity proof.",
        "decompile": "Vec3__ScaleToOut this outVec scale",
        "ret": "0x8",
    },
    "0x0040d180": {
        "name": "Vec3__Dot",
        "signature": "double __thiscall Vec3__Dot(void * this, void * rhs)",
        "comment": "Signature hardening: Vec3 dot helper reads ECX as lhs and stack arg1 as rhs, multiplies the three vector lanes into an FPU return, and returns with ret 0x4. Not concrete Vec3 layout, exact source identity, runtime behavior, tags, locals, or rebuild parity proof.",
        "decompile": "Vec3__Dot this rhs",
        "ret": "0x4",
    },
    "0x0040d1a0": {
        "name": "Vec3__ElevationOrZero",
        "signature": "double __fastcall Vec3__ElevationOrZero(void * vec)",
        "comment": "Owner/name correction: vector-angle helper computes vector length, guards near-zero input, divides z over length, and calls OID__AcosWrapper/CRT acos context. Source uses FVector::Elevation in auto-aim/camera orientation flows, but exact source identity, concrete Vec3 layout, runtime behavior, tags, locals, and rebuild parity remain unproven.",
        "decompile": "Vec3__ElevationOrZero vec SQRT OID__AcosWrapper",
        "ret": "",
    },
    "0x0040d1f0": {
        "name": "Mat34__SetFromEulerAngles",
        "signature": "void __thiscall Mat34__SetFromEulerAngles(void * this, float angle0, float angle1, float angle2)",
        "comment": "Owner/name correction: matrix builder evaluates cos/sin for three stack float angles, writes row/basis floats through matrix offsets +0x0..+0x28, and returns with ret 0xc. Broad xrefs keep exact source identity, angle order, concrete Mat34 layout, runtime behavior, tags, locals, and rebuild parity unproven.",
        "decompile": "Mat34__SetFromEulerAngles angle0 angle1 angle2 fcos fsin",
        "ret": "0xc",
    },
    "0x0040d2c0": {
        "name": "Mat34__TransformVec3ByBasisToOut",
        "signature": "void __thiscall Mat34__TransformVec3ByBasisToOut(void * this, void * outVec, void * vec)",
        "comment": "Owner/name correction: basis-transform helper multiplies a vector by three matrix/basis rows at offsets +0x0/+0x10/+0x20, writes outVec lanes, and returns with ret 0x8. It does not prove translation, concrete Mat34/Vec3 layouts, exact source identity, runtime behavior, tags, locals, or rebuild parity.",
        "decompile": "Mat34__TransformVec3ByBasisToOut outVec vec",
        "ret": "0x8",
    },
}


def write_fixture(root: Path, *, stale: bool = False, overclaim: bool = False) -> dict[str, Path]:
    dry = root / "signature_dry.log"
    apply = root / "signature_apply.log"
    metadata = root / "metadata_final.tsv"
    decompile = root / "decompile_final"
    xrefs = root / "xrefs_final.tsv"
    instructions = root / "instructions_final.tsv"
    decompile.mkdir()

    dry.write_text("--- SUMMARY ---\nupdated=0 skipped=6 missing=0 bad=0\n", encoding="utf-8")
    apply.write_text("--- SUMMARY ---\nupdated=6 skipped=0 missing=0 bad=0\n", encoding="utf-8")

    rows = {address: dict(row) for address, row in TARGET_ROWS.items()}
    if stale:
        rows["0x0040d1a0"]["name"] = "CMonitor__ComputeVectorLengthOrZero"
        rows["0x0040d2c0"]["signature"] = (
            "void __thiscall CSquadNormal__TransformVec3ByOrientationMatrix"
            "(void * this, void * param_1, void * param_2, void * param_3)"
        )
    if overclaim:
        rows["0x0040d1f0"]["comment"] += " Runtime behavior proven."

    metadata.write_text(
        "address\tname\tsignature\tcomment\tstatus\n"
        + "".join(
            f"{address}\t{row['name']}\t{row['signature']}\t{row['comment']}\tOK\n"
            for address, row in rows.items()
        ),
        encoding="utf-8",
    )
    (decompile / "index.tsv").write_text(
        "address\tname\tsignature\tstatus\n"
        + "".join(f"{address}\t{row['name']}\t{row['signature']}\tOK\n" for address, row in rows.items()),
        encoding="utf-8",
    )
    for address, row in rows.items():
        text = f"{row['signature']} {row['decompile']}"
        if stale and address == "0x0040d2c0":
            text += " param_1 param_2 param_3 CSquadNormal__TransformVec3ByOrientationMatrix"
        (decompile / f"{address[2:]}_{row['name']}.c").write_text(text, encoding="utf-8")

    xrefs.write_text(
        "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
        + "".join(
            f"{address[2:]}\t{row['name']}\t00401000\t00401000\tCaller\tUNCONDITIONAL_CALL\n"
            for address, row in rows.items()
        ),
        encoding="utf-8",
    )
    instructions.write_text(
        "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
        + "".join(
            f"{address}\t{address}\tAFTER\t1\t{address}\t{address}\t{row['name']}\tRET\t{row['ret']}\t\tTERMINATOR\n"
            for address, row in rows.items()
        ),
        encoding="utf-8",
    )
    return {
        "dry": dry,
        "apply": apply,
        "metadata": metadata,
        "decompile_index": decompile / "index.tsv",
        "decompile_dir": decompile,
        "xrefs": xrefs,
        "instructions": instructions,
    }


class VectorGeometrySignatureTrancheProbeTests(unittest.TestCase):
    def test_passes_for_hardened_vector_geometry_tranche(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], 6)
        self.assertEqual(report["summary"]["renamedTargets"], 3)
        self.assertEqual(report["summary"]["signatureHardenedTargets"], 6)
        self.assertEqual(report["summary"]["paramSignatureHits"], 0)

    def test_fails_for_stale_name_signature_or_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale=True, overclaim=True)
            report = probe.build_report(
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                decompile_index_path=paths["decompile_index"],
                decompile_dir=paths["decompile_dir"],
                xrefs_path=paths["xrefs"],
                instructions_path=paths["instructions"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("name/status mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("signature tokens missing" in failure for failure in report["failures"]))
        self.assertTrue(any("stale token" in failure for failure in report["failures"]))
        self.assertTrue(any("overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
