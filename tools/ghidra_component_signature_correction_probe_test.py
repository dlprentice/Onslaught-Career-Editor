#!/usr/bin/env python3
"""Self-tests for the Component signature correction probe."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_component_signature_correction_probe.py"


def load_module():
    spec = importlib.util.spec_from_file_location("probe", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ComponentSignatureCorrectionProbeTests(unittest.TestCase):
    def write_fixture(
        self,
        root: Path,
        *,
        stale_signature: bool = False,
        missing_tag: bool = False,
        missing_vtable_type: bool = False,
        bad_queue_counts: bool = False,
    ) -> dict[str, Path]:
        probe = load_module()
        decompile_dir = root / "decompile_final"
        decompile_dir.mkdir(parents=True)
        metadata = root / "metadata_final.tsv"
        index = decompile_dir / "index.tsv"
        xrefs = root / "xrefs_final.tsv"
        instructions = root / "instructions_final.tsv"
        tags = root / "tags_final.tsv"
        vtables = root / "vtable_type_names.tsv"
        queue = root / "static-reaudit-queue.json"

        metadata_rows = []
        index_rows = []
        tag_rows = []
        for address, expected in probe.TARGETS.items():
            signature = expected["signature"]
            if stale_signature and address == "0x00427f90":
                signature = "void * __thiscall CComponentBomberAI__VFunc_01_00427f90(void * this, void * param_1, int param_2)"
            comment = "; ".join(expected["comment"])
            metadata_rows.append((address, expected["name"], signature, comment, "OK"))
            index_rows.append((address, expected["name"], signature, "OK"))
            final_tags = list(expected["tags"])
            if missing_tag and address == "0x00428070":
                final_tags = [tag for tag in final_tags if tag != "owner-corrected"]
            tag_rows.append((address, expected["name"], ";".join(final_tags), "OK"))
            (decompile_dir / f"{address[2:]}_{expected['name']}.c").write_text(
                f"/* {comment} */\n{signature} {{}}\n",
                encoding="utf-8",
            )

        metadata.write_text(
            "address\tname\tsignature\tcomment\tstatus\n"
            + "\n".join("\t".join(row) for row in metadata_rows)
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
                f"{address}\t{expected['name']}\t0x005d96b8\t<none>\t<no_function>\tDATA"
                for address, expected in probe.TARGETS.items()
            )
            + "\n",
            encoding="utf-8",
        )
        instructions.write_text(
            "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
            + "\n".join(
                f"{address}\t{address}\tTARGET\t0\t{address}\t{address}\t{expected['name']}\tCALL\t0x00400000\t00\tUNCONDITIONAL_CALL"
                for address, expected in probe.TARGETS.items()
            )
            + "\n",
            encoding="utf-8",
        )
        tags.write_text(
            "address\tname\ttags\tstatus\n" + "\n".join("\t".join(row) for row in tag_rows) + "\n",
            encoding="utf-8",
        )
        vtable_rows = [
            ("005d96b4", "CComponentBomberAI"),
            ("005d9680", "CFenrirMainGunAI"),
            ("005d8e08", "CRepairPadAI"),
            ("005d9654", "CComponentGuide"),
            ("005d8d1c", "CUnitAI"),
        ]
        if missing_vtable_type:
            vtable_rows = [row for row in vtable_rows if row[1] != "CFenrirMainGunAI"]
        vtables.write_text(
            "vtable\tcol_ptr_slot\tcol_addr\tsignature\toffset\tcd_offset\ttype_desc\tclass_desc\traw_type_name\tdemangled_type_name\n"
            + "\n".join(
                f"{addr}\t005d0000\t00600000\t0x00000000\t0\t0\t0x00600000\t0x00600000\t.?AV{name}@@\t{name}"
                for addr, name in vtable_rows
            )
            + "\n",
            encoding="utf-8",
        )
        queue.write_text(
            json.dumps(
                {
                    "status": "PASS",
                    "totalFunctions": 5884,
                    "qualitySignals": {
                        "commentlessFunctionCount": 5124 if bad_queue_counts else 5123,
                        "undefinedSignatureCount": 1995 if bad_queue_counts else 1994,
                        "paramSignatureCount": 2300 if bad_queue_counts else 2299,
                    },
                }
            ),
            encoding="utf-8",
        )
        return {
            "metadata_final_path": metadata,
            "decompile_index_path": index,
            "decompile_dir": decompile_dir,
            "xrefs_path": xrefs,
            "instructions_path": instructions,
            "tags_path": tags,
            "vtable_types_path": vtables,
            "queue_json_path": queue,
        }

    def test_accepts_component_signature_wave(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**self.write_fixture(Path(tmp)))
        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["targetCount"], 10)
        self.assertEqual(report["queueUndefinedSignatures"], 1994)
        self.assertEqual(report["queueParamSignatures"], 2299)

    def test_rejects_stale_destructor_signature_and_missing_tag(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**self.write_fixture(Path(tmp), stale_signature=True, missing_tag=True))
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("signature mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("tag missing" in failure for failure in report["failures"]))

    def test_rejects_missing_vtable_type_and_queue_regression(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**self.write_fixture(Path(tmp), missing_vtable_type=True, bad_queue_counts=True))
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("vtable type missing" in failure for failure in report["failures"]))
        self.assertTrue(any("paramSignatureCount" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
