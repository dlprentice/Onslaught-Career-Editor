#!/usr/bin/env python3
"""Tests for the Wave385 CGame/CDXGame Ghidra probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_game_dxgame_wave385_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
TAGS_HEADER = "address\tname\ttags\tstatus\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)
VTABLE_TYPE_HEADER = "vtable\tcol_ptr_slot\tcol_addr\tsignature\toffset\tcd_offset\ttype_desc\tclass_desc\traw_type_name\tdemangled_type_name\n"
VTABLE_SLOT_HEADER = "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\tcontaining_entry\tcontaining_name\tstatus\n"


def write_fixture(root: Path, *, stale: bool = False) -> dict[str, Path]:
    dry = root / "game_dxgame_wave385_dry.log"
    apply = root / "game_dxgame_wave385_apply.log"
    metadata = root / "metadata_after.tsv"
    tags = root / "tags_after.tsv"
    instructions = root / "instructions_after.tsv"
    decompile = root / "decompile_after"
    vtable_types = root / "vtable_type_names_after.tsv"
    secondary_vtable_types = root / "secondary_vtable_type_names_after.tsv"
    vtable_slots = root / "vtable_slots_after.tsv"
    secondary_vtable_slots = root / "secondary_vtable_slots_after.tsv"
    bink_boundary = root / "bink_deferred_boundary_after.tsv"
    decompile.mkdir()

    dry.write_text("SUMMARY: updated=0 skipped=7 renamed=0 would_rename=7 missing=0 bad=0\n", encoding="utf-8")
    apply.write_text(
        f"SUMMARY: updated={len(probe.TARGETS)} skipped=0 renamed=7 would_rename=0 missing=0 bad=0\n"
        "REPORT: Save succeeded\n",
        encoding="utf-8",
    )

    metadata_lines: list[str] = []
    tag_lines: list[str] = []
    for address, spec in probe.TARGETS.items():
        name = str(spec["name"])
        signature = str(spec["signature"])
        comment = " ".join(str(token) for token in spec["commentTokens"])
        if stale and address == "0x0046c210":
            name = "IController__ctor_like_0046c210"
            comment += " runtime proof"
        metadata_lines.append(f"{address}\t{name}\t{signature}\t{comment}\tOK\n")
        tag_lines.append(f"{address}\t{name}\t{';'.join(sorted(probe.COMMON_TAGS | set(spec['tags'])))}\tOK\n")
        decompile_text = f"{name}\n{signature}\n{' '.join(str(token) for token in spec['decompileTokens'])}\n"
        if stale and address == "0x00541f10":
            decompile_text += "CFrontEndVideo__CFrontEndVideo\n"
        (decompile / f"{address[2:]}_{name}.c").write_text(decompile_text, encoding="utf-8")

    metadata.write_text(METADATA_HEADER + "".join(metadata_lines), encoding="utf-8")
    tags.write_text(TAGS_HEADER + "".join(tag_lines), encoding="utf-8")
    instructions.write_text(
        INSTRUCTION_HEADER
        + "".join(
            f"{target}\t{target}\tTARGET\t0\t{instruction}\t{target}\t{probe.TARGETS[target]['name']}\t"
            f"{mnemonic}\t{operands}\t{bytes_}\tFALL_THROUGH\n"
            for target, instruction, mnemonic, operands, bytes_ in probe.INSTRUCTION_EVIDENCE
        ),
        encoding="utf-8",
    )

    first_types = {k: v for k, v in probe.VTABLE_TYPES.items() if k in {"0x005dbbb4", "0x005d9388", "0x005e5078"}}
    second_types = {k: v for k, v in probe.VTABLE_TYPES.items() if k not in first_types}
    vtable_types.write_text(
        VTABLE_TYPE_HEADER
        + "".join(f"{vtable[2:]}\t00000000\t00000000\t0x0\t0\t0\t0x0\t0x0\t\t{name}\n" for vtable, name in first_types.items()),
        encoding="utf-8",
    )
    secondary_vtable_types.write_text(
        VTABLE_TYPE_HEADER
        + "".join(f"{vtable[2:]}\t00000000\t00000000\t0x0\t0\t0\t0x0\t0x0\t\t{name}\n" for vtable, name in second_types.items()),
        encoding="utf-8",
    )
    vtable_slots.write_text(
        VTABLE_SLOT_HEADER
        + "005dbbb4\t1\t005dbbb8\t0x0046c2b0\t0046c2b0\t0046c2b0\tCGame__scalar_deleting_dtor\t0046c2b0\tCGame__scalar_deleting_dtor\tOK\n",
        encoding="utf-8",
    )
    secondary_vtable_slots.write_text(
        VTABLE_SLOT_HEADER
        + "005e509c\t1\t005e50a0\t0x00541f30\t00541f30\t00541f30\tCDXGame__scalar_deleting_dtor\t00541f30\tCDXGame__scalar_deleting_dtor\tOK\n",
        encoding="utf-8",
    )
    bink_boundary.write_text(METADATA_HEADER + "0x00541140\t<none>\t<none>\t\tMISSING\n", encoding="utf-8")
    return {
        "root": root,
        "dry": dry,
        "apply": apply,
        "metadata": metadata,
        "tags": tags,
        "instructions": instructions,
        "decompile": decompile,
        "vtable_types": vtable_types,
        "secondary_vtable_types": secondary_vtable_types,
        "vtable_slots": vtable_slots,
        "secondary_vtable_slots": secondary_vtable_slots,
        "bink_boundary": bink_boundary,
    }


class GameDxGameWave385ProbeTests(unittest.TestCase):
    def test_passes_for_owner_and_vtable_corrections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                root=paths["root"],
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                tags_path=paths["tags"],
                instructions_path=paths["instructions"],
                decompile_dir=paths["decompile"],
                vtable_type_path=paths["vtable_types"],
                secondary_vtable_type_path=paths["secondary_vtable_types"],
                vtable_slots_path=paths["vtable_slots"],
                secondary_vtable_slots_path=paths["secondary_vtable_slots"],
                bink_boundary_metadata_path=paths["bink_boundary"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["summary"]["targets"], len(probe.TARGETS))
        self.assertEqual(report["summary"]["instructionEvidenceHits"], len(probe.INSTRUCTION_EVIDENCE))
        self.assertEqual(report["summary"]["vtableTypeHits"], len(probe.VTABLE_TYPES))
        self.assertEqual(report["summary"]["vtableSlotHits"], len(probe.VTABLE_SLOT_EVIDENCE))

    def test_fails_for_stale_names_overclaim_or_repaired_deferred_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), stale=True)
            paths["bink_boundary"].write_text(
                METADATA_HEADER + "0x00541140\tCBinkOpenThread__DeferredSlot\tvoid f(void)\t\tOK\n",
                encoding="utf-8",
            )
            report = probe.build_report(
                root=paths["root"],
                dry_log_path=paths["dry"],
                apply_log_path=paths["apply"],
                metadata_path=paths["metadata"],
                tags_path=paths["tags"],
                instructions_path=paths["instructions"],
                decompile_dir=paths["decompile"],
                vtable_type_path=paths["vtable_types"],
                secondary_vtable_type_path=paths["secondary_vtable_types"],
                vtable_slots_path=paths["vtable_slots"],
                secondary_vtable_slots_path=paths["secondary_vtable_slots"],
                bink_boundary_metadata_path=paths["bink_boundary"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("name mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("comment overclaim" in failure for failure in report["failures"]))
        self.assertTrue(any("stale decompile name" in failure for failure in report["failures"]))
        self.assertTrue(any("deferred boundary unexpectedly present" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
