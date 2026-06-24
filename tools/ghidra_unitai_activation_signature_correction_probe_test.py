#!/usr/bin/env python3
"""Self-tests for the UnitAI activation signature correction probe."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_unitai_activation_signature_correction_probe.py"


def load_module():
    spec = importlib.util.spec_from_file_location("probe", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class UnitAiActivationSignatureCorrectionProbeTests(unittest.TestCase):
    def write_fixture(
        self,
        root: Path,
        *,
        stale_boundary: bool = False,
        bad_owner_name: bool = False,
        missing_component_vtable: bool = False,
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
        xref_rows = []
        instruction_rows = []
        for address, expected in probe.TARGETS.items():
            name = expected["name"]
            if bad_owner_name and address == "0x00428cb0":
                name = "CExplosionInitThing__TriggerHitAnimationAndSetFlag"
            signature = expected["signature"]
            comment = "; ".join(expected["comment"])
            metadata_rows.append((address, name, signature, comment, "OK"))
            index_rows.append((address, name, signature, "OK"))
            tag_rows.append((address, name, ";".join(expected["tags"]), "OK"))
            body = f"/* {comment} */\n{signature} {{}}\n"
            if stale_boundary and address == "0x00429270":
                body += "unaff_ESI = 0; unaff_EDI = 0;\n"
            else:
                body += "turnContext;\n" if address == "0x00429270" else ""
            (decompile_dir / f"{address[2:]}_{name}.c").write_text(body, encoding="utf-8")
            xref_rows.append((address, name, "0x005e0000", "<none>", "<no_function>", "DATA"))
            instruction_rows.append((address, address, "TARGET", "0", address, address, name, "MOV", "EAX, EAX", "90", "FALL_THROUGH"))

        xref_rows.extend(
            [
                ("0x00428e80", probe.TARGETS["0x00428e80"]["name"], "0x005d96c4", "<none>", "<no_function>", "DATA"),
                ("0x00428e80", probe.TARGETS["0x00428e80"]["name"], "0x005d9690", "<none>", "<no_function>", "DATA"),
            ]
        )
        instruction_rows.append(
            (
                "0x00429270",
                "0x00429270",
                "AFTER",
                "8",
                "0x00429280",
                "0x00429280" if stale_boundary else "0x00429270",
                probe.TARGETS["0x00429270"]["name"],
                "TEST",
                "ECX, ECX",
                "85 c9",
                "FALL_THROUGH",
            )
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
            + "\n".join("\t".join(row) for row in xref_rows)
            + "\n",
            encoding="utf-8",
        )
        instructions.write_text(
            "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
            + "\n".join("\t".join(row) for row in instruction_rows)
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
        ]
        if missing_component_vtable:
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
                        "commentlessFunctionCount": 5124 if bad_queue_counts else 5111,
                        "undefinedSignatureCount": 1995 if bad_queue_counts else 1993,
                        "paramSignatureCount": 2300 if bad_queue_counts else 2283,
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

    def test_accepts_unitai_activation_wave(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**self.write_fixture(Path(tmp)))
        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["targetCount"], 12)
        self.assertEqual(report["ownerOrBoundaryTargetCount"], 3)
        self.assertEqual(report["queueUndefinedSignatures"], 1993)

    def test_rejects_stale_boundary_and_owner_name(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**self.write_fixture(Path(tmp), stale_boundary=True, bad_owner_name=True))
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("unaff register" in failure for failure in report["failures"]))
        self.assertTrue(any("name mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("0x00429280 instruction" in failure for failure in report["failures"]))

    def test_rejects_missing_component_rtti_and_queue_regression(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(
                **self.write_fixture(Path(tmp), missing_component_vtable=True, bad_queue_counts=True)
            )
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("vtable type missing" in failure for failure in report["failures"]))
        self.assertTrue(any("paramSignatureCount" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
