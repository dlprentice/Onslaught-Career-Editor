#!/usr/bin/env python3
"""Tests for the CDebris Ghidra signature/boundary tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_debris_signature_boundary_tranche_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
TAGS_HEADER = "address\tname\ttags\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
VTABLE_HEADER = (
    "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\t"
    "containing_entry\tcontaining_name\tstatus\n"
)
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)


def write_fixture(root: Path, *, stale: bool = False, overclaim: bool = False) -> dict[str, Path]:
    dry = root / "debris_dry.log"
    apply = root / "debris_apply.log"
    metadata = root / "metadata_final.tsv"
    tags = root / "tags_final.tsv"
    xrefs = root / "xrefs_final.tsv"
    vtable_slots = root / "vtable_slots_final.tsv"
    instructions = root / "instructions_final.tsv"
    string_path = root / "string_006283e0.tsv"
    decompile = root / "decompile_final"
    decompile.mkdir()

    dry.write_text("--- SUMMARY ---\ntargets=7 changed_or_would_change=7 failed=0 dry=true\n", encoding="utf-8")
    apply.write_text("--- SUMMARY ---\ntargets=7 changed_or_would_change=7 failed=0 dry=false\n", encoding="utf-8")

    metadata_lines = []
    tag_lines = []
    for address, spec in probe.TARGETS.items():
        name = str(spec["name"])
        signature = str(spec["signature"])
        if stale and address == "0x00441320":
            name = "CDebris__ctor_like_00441320"
            signature = "void __fastcall CDebris__ctor_like_00441320(void * param_1)"
        comment = " ".join(str(token) for token in spec["commentTokens"])
        if overclaim and address == "0x004413a0":
            comment += " runtime behavior proven"
        metadata_lines.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        tag_lines.append(f"{address}\t{name}\t{';'.join(sorted(probe.COMMON_TAGS | set(spec['tags'])))}\tOK\n")
        (decompile / f"{address[2:]}_{name}.c").write_text(
            f"{name}\n{signature}\n{' '.join(str(token) for token in spec['decompileTokens'])}\n",
            encoding="utf-8",
        )

    metadata.write_text(METADATA_HEADER + "".join(metadata_lines), encoding="utf-8")
    tags.write_text(TAGS_HEADER + "".join(tag_lines), encoding="utf-8")
    xrefs.write_text(
        XREF_HEADER
        + "004411a0\tCDebris__Init\t005daf34\t<none>\t<no_function>\tDATA\n"
        + "00441320\tCDebris__dtor_base\t00441383\t00441380\tCDebris__scalar_deleting_dtor\tUNCONDITIONAL_CALL\n"
        + "00441380\tCDebris__scalar_deleting_dtor\t005daf14\t<none>\t<no_function>\tDATA\n",
        encoding="utf-8",
    )
    vtable_slots.write_text(
        VTABLE_HEADER
        + "005daf10\t1\t005daf14\t0x00441380\t00441380\t00441380\tCDebris__scalar_deleting_dtor\t00441380\tCDebris__scalar_deleting_dtor\tOK\n"
        + "005daf10\t7\t005daf2c\t0x00441360\t00441360\t00441360\tCDebris__GetClassName\t00441360\tCDebris__GetClassName\tOK\n"
        + "005daf10\t8\t005daf30\t0x00441370\t00441370\t00441370\tCDebris__GetClassId\t00441370\tCDebris__GetClassId\tOK\n"
        + "005daf10\t9\t005daf34\t0x004411a0\t004411a0\t004411a0\tCDebris__Init\t004411a0\tCDebris__Init\tOK\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x004411a0\t0x004411a0\tAFTER\t80\t0x00441310\t0x004411a0\tCDebris__Init\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x00441380\t0x00441380\tAFTER\t10\t0x0044139d\t0x00441380\tCDebris__scalar_deleting_dtor\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x004413a0\t0x004413a0\tAFTER\t44\t0x00441416\t0x004413a0\tCDebris__Render\tRET\t0x4\tc2 04 00\tTERMINATOR\n",
        encoding="utf-8",
    )
    string_path.write_text("input_addr\tmode\tptr_raw\ttarget_addr\tcstring\n006283e0\tdirect\t\t006283e0\tCDebris\n", encoding="utf-8")

    return {
        "root": root,
        "dry": dry,
        "apply": apply,
        "metadata": metadata,
        "tags": tags,
        "xrefs": xrefs,
        "vtable_slots": vtable_slots,
        "instructions": instructions,
        "decompile": decompile,
        "string": string_path,
    }


class DebrisSignatureBoundaryTrancheProbeTests(unittest.TestCase):
    def test_passes_for_saved_debris_tranche(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                root=paths["root"],
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                tags_path=paths["tags"],
                xrefs_path=paths["xrefs"],
                vtable_slots_path=paths["vtable_slots"],
                instructions_path=paths["instructions"],
                decompile_dir=paths["decompile"],
                string_path=paths["string"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], 7)
        self.assertEqual(report["summary"]["vtableEvidenceHits"], 4)
        self.assertEqual(report["summary"]["commentOverclaims"], 0)

    def test_fails_for_stale_name_or_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale=True, overclaim=True)
            report = probe.build_report(
                root=paths["root"],
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                tags_path=paths["tags"],
                xrefs_path=paths["xrefs"],
                vtable_slots_path=paths["vtable_slots"],
                instructions_path=paths["instructions"],
                decompile_dir=paths["decompile"],
                string_path=paths["string"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("name" in failure or "stale" in failure for failure in report["failures"]))
        self.assertTrue(any("overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
