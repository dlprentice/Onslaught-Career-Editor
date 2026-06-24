#!/usr/bin/env python3
"""Self-tests for the explosion-value Ghidra tranche probe."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_explosion_value_tranche_probe.py"


def load_module():
    spec = importlib.util.spec_from_file_location("probe", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ExplosionValueTrancheProbeTests(unittest.TestCase):
    def write_fixture(
        self,
        root: Path,
        *,
        stale_name: bool = False,
        missing_comment: bool = False,
        missing_tag: bool = False,
        missing_xref: bool = False,
        missing_slot: bool = False,
    ) -> dict[str, Path]:
        probe = load_module()
        decompile_dir = root / "decompile_final"
        decompile_dir.mkdir(parents=True)
        metadata = root / "metadata_final.tsv"
        index = decompile_dir / "index.tsv"
        xrefs = root / "xrefs_final.tsv"
        instructions = root / "instructions_final.tsv"
        tags = root / "tags_final.tsv"
        vtable_slots = root / "vtable_slots_final.tsv"

        metadata_rows = []
        index_rows = []
        tag_rows = []
        instruction_rows = []
        for idx, (address, expected) in enumerate(probe.TARGETS.items()):
            name = expected["name"]
            if stale_name and idx == 0:
                name = probe.STALE_NAMES[0]
            signature = " ".join(expected["signature"])
            comment = "; ".join(expected["comment"])
            if missing_comment and idx == 1:
                comment = "short stale note"
            final_tags = list(expected["tags"])
            if missing_tag and idx == 2:
                final_tags = [tag for tag in final_tags if tag != "explosion-value-tranche"]
            metadata_rows.append((address, name, signature, comment, "OK"))
            index_rows.append((address, name, signature, "OK"))
            tag_rows.append((address, name, ";".join(final_tags), "OK"))
            (decompile_dir / f"{address[2:]}_{name}.c").write_text(
                f"/* {comment} */\n{signature} {{}}\n",
                encoding="utf-8",
            )
            instruction_rows.append(
                f"{address}\t{address}\tTARGET\t0\t{address}\t{address}\t{name}\tRET\t\tc3\tTERMINATOR"
            )

        metadata.write_text(
            "address\tname\tsignature\tcomment\tstatus\n"
            + "\n".join("\t".join(row) for row in metadata_rows)
            + "\n",
            encoding="utf-8",
        )
        index.write_text(
            "address\tname\tsignature\tstatus\n" + "\n".join("\t".join(row) for row in index_rows) + "\n",
            encoding="utf-8",
        )
        xref_pairs = list(probe.EXPECTED_XREFS)
        if missing_xref:
            xref_pairs = xref_pairs[1:]
        xrefs.write_text(
            "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
            + "\n".join(
                f"{target}\t{probe.TARGETS[target]['name']}\t{from_addr}\t<none>\t<no_function>\tDATA"
                for target, from_addr in xref_pairs
            )
            + "\n",
            encoding="utf-8",
        )
        instructions.write_text(
            "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
            + "\n".join(instruction_rows)
            + "\n",
            encoding="utf-8",
        )
        tags.write_text(
            "address\tname\ttags\tstatus\n" + "\n".join("\t".join(row) for row in tag_rows) + "\n",
            encoding="utf-8",
        )
        slot_rows = list(probe.EXPECTED_VTABLE_SLOTS)
        if missing_slot:
            slot_rows = slot_rows[1:]
        vtable_slots.write_text(
            "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\tcontaining_entry\tcontaining_name\tstatus\n"
            + "\n".join(
                f"{vtable}\t{slot}\t{vtable}\t0x00000000\t0x00000000\t0x00000000\t{name}\t0x00000000\t{name}\tOK"
                for vtable, slot, name in slot_rows
            )
            + "\n",
            encoding="utf-8",
        )
        return {
            "metadata_final_path": metadata,
            "decompile_index_path": index,
            "decompile_dir": decompile_dir,
            "xrefs_path": xrefs,
            "instructions_path": instructions,
            "tags_path": tags,
            "vtable_slots_path": vtable_slots,
        }

    def test_accepts_explosion_value_fixture(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**self.write_fixture(Path(tmp)))
        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["targetCount"], len(probe.TARGETS))
        self.assertEqual(report["vtableSlotChecks"], len(probe.EXPECTED_VTABLE_SLOTS))

    def test_rejects_stale_name_and_missing_comment_tag(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(
                **self.write_fixture(Path(tmp), stale_name=True, missing_comment=True, missing_tag=True)
            )
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("stale name" in failure or "name mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("comment token missing" in failure for failure in report["failures"]))
        self.assertTrue(any("tag missing" in failure for failure in report["failures"]))

    def test_rejects_missing_xref_and_vtable_slot(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**self.write_fixture(Path(tmp), missing_xref=True, missing_slot=True))
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("expected xref missing" in failure for failure in report["failures"]))
        self.assertTrue(any("vtable slot missing" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
