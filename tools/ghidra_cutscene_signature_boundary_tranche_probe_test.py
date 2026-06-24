#!/usr/bin/env python3
"""Tests for the CCutscene Ghidra signature/boundary tranche probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_cutscene_signature_boundary_tranche_probe as probe


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
    dry = root / "cutscene_dry.log"
    apply = root / "cutscene_apply.log"
    metadata = root / "metadata_final.tsv"
    tags = root / "tags_final.tsv"
    xrefs = root / "xrefs_final.tsv"
    vtable_slots = root / "vtable_slots_final.tsv"
    instructions = root / "instructions_final.tsv"
    decompile = root / "decompile_final"
    decompile.mkdir()

    dry.write_text("--- SUMMARY ---\ntargets=14 changed_or_would_change=14 failed=0 dry=true\n", encoding="utf-8")
    apply.write_text("--- SUMMARY ---\ntargets=14 changed_or_would_change=14 failed=0 dry=false\n", encoding="utf-8")

    metadata_lines = []
    tag_lines = []
    for address, spec in probe.TARGETS.items():
        name = str(spec["name"])
        signature = str(spec["signature"])
        if stale and address in {"0x0043e8e0", "0x0043eab0"}:
            name = "CCutscene__scalar_deleting_dtor_0043e8e0" if address == "0x0043e8e0" else "CCutscene__VFunc_09_0043eab0"
            signature = "undefined " + name + "(void)"
        comment = " ".join(spec["commentTokens"]) + " runtime behavior remains unproven"
        if overclaim and address == "0x0043f690":
            comment += " runtime behavior proven"
        metadata_lines.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        tag_lines.append(f"{address}\t{name}\t{';'.join(probe.COMMON_TAGS + spec['tags'])}\tOK\n")
        (decompile / f"{address[2:]}_{name}.c").write_text(
            f"{name}\n{signature}\n{' '.join(spec['decompileTokens'])}\n",
            encoding="utf-8",
        )

    metadata.write_text(METADATA_HEADER + "".join(metadata_lines), encoding="utf-8")
    tags.write_text(TAGS_HEADER + "".join(tag_lines), encoding="utf-8")
    xrefs.write_text(
        XREF_HEADER
        + "0043ea90\tCCutscene__scalar_deleting_dtor\t005dad8c\t<none>\t<no_function>\tDATA\n"
        + "0043eca0\tCCutscene__ClearAnimationsAndStop\t005dad90\t<none>\t<no_function>\tDATA\n"
        + "0043eab0\tCCutscene__Init\t005dadac\t<none>\t<no_function>\tDATA\n"
        + "0043f510\tCCutscene__InitAnimations\t005dae10\t<none>\t<no_function>\tDATA\n"
        + "0043f420\tCCutscene__Stop\t005dae88\t<none>\t<no_function>\tDATA\n"
        + "0043fcb0\tCCutscene__EventDispatchUpdate\t005dad88\t<none>\t<no_function>\tDATA\n",
        encoding="utf-8",
    )
    vtable_slots.write_text(
        VTABLE_HEADER
        + "005dad88\t0\t005dad88\t0x0043fcb0\t0043fcb0\t0043fcb0\tCCutscene__EventDispatchUpdate\t0043fcb0\tCCutscene__EventDispatchUpdate\tOK\n"
        + "005dad88\t1\t005dad8c\t0x0043ea90\t0043ea90\t0043ea90\tCCutscene__scalar_deleting_dtor\t0043ea90\tCCutscene__scalar_deleting_dtor\tOK\n"
        + "005dad88\t2\t005dad90\t0x0043eca0\t0043eca0\t0043eca0\tCCutscene__ClearAnimationsAndStop\t0043eca0\tCCutscene__ClearAnimationsAndStop\tOK\n"
        + "005dad88\t9\t005dadac\t0x0043eab0\t0043eab0\t0043eab0\tCCutscene__Init\t0043eab0\tCCutscene__Init\tOK\n"
        + "005dae00\t4\t005dae10\t0x0043f510\t0043f510\t0043f510\tCCutscene__InitAnimations\t0043f510\tCCutscene__InitAnimations\tOK\n"
        + "005dae80\t2\t005dae88\t0x0043f420\t0043f420\t0043f420\tCCutscene__Stop\t0043f420\tCCutscene__Stop\tOK\n",
        encoding="utf-8",
    )
    instructions.write_text(
        INSTRUCTION_HEADER
        + "0x0043eab0\t0x0043eab0\tAFTER\t198\t0x0043ec98\t0x0043eab0\tCCutscene__Init\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x0043ed20\t0x0043ed20\tAFTER\t16\t0x0043ed54\t0x0043ed20\tCCutsceneAnimNode__DestroyRecursive\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        + "0x0043fcb0\t0x0043fcb0\tAFTER\t7\t0x0043fcca\t0x0043fcb0\tCCutscene__EventDispatchUpdate\tRET\t0x4\tc2 04 00\tTERMINATOR\n",
        encoding="utf-8",
    )

    return {
        "dry": dry,
        "apply": apply,
        "metadata": metadata,
        "tags": tags,
        "xrefs": xrefs,
        "vtable_slots": vtable_slots,
        "instructions": instructions,
        "decompile": decompile,
    }


class CutsceneSignatureBoundaryTrancheProbeTests(unittest.TestCase):
    def test_passes_for_saved_cutscene_tranche(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                tags_path=paths["tags"],
                xrefs_path=paths["xrefs"],
                vtable_slots_path=paths["vtable_slots"],
                instructions_path=paths["instructions"],
                decompile_dir=paths["decompile"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], 14)
        self.assertEqual(report["summary"]["vtableEvidenceHits"], 6)
        self.assertEqual(report["summary"]["commentOverclaims"], 0)

    def test_fails_for_stale_names_or_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale=True, overclaim=True)
            report = probe.build_report(
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                tags_path=paths["tags"],
                xrefs_path=paths["xrefs"],
                vtable_slots_path=paths["vtable_slots"],
                instructions_path=paths["instructions"],
                decompile_dir=paths["decompile"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("name" in failure for failure in report["failures"]))
        self.assertTrue(any("overclaim" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
