#!/usr/bin/env python3
"""Self-tests for the CollisionSeekingRound boundary/signature probe."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_collision_seeking_round_boundary_signature_probe.py"


def load_module():
    spec = importlib.util.spec_from_file_location("probe", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CollisionSeekingRoundBoundarySignatureProbeTests(unittest.TestCase):
    def write_fixture(
        self,
        root: Path,
        *,
        stale_signature: bool = False,
        missing_created: bool = False,
        bad_queue_total: bool = False,
    ) -> dict[str, Path]:
        probe = load_module()
        decompile_dir = root / "decompile_final"
        decompile_dir.mkdir(parents=True)
        metadata = root / "metadata_final.tsv"
        index = decompile_dir / "index.tsv"
        xrefs = root / "xrefs_final.tsv"
        instructions = root / "instructions_final.tsv"
        create_apply = root / "function_create_apply.tsv"
        queue = root / "static-reaudit-queue.json"

        metadata_rows = []
        index_rows = []
        for address, expected in probe.TARGETS.items():
            signature = expected["signature"]
            if stale_signature and address == "0x00425a10":
                signature = "int __stdcall CCollisionSeekingInfantryBloke__VFunc_08_00425a10(int param_1)"
            comment = "; ".join(expected["comment"])
            metadata_rows.append((address, expected["name"], signature, comment, "OK"))
            index_rows.append((address, expected["name"], signature, "OK"))
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
                f"{address}\t{expected['name']}\t0x005d9608\t<none>\t<no_function>\tDATA"
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
        created_rows = []
        for address, expected in probe.TARGETS.items():
            if not expected.get("created"):
                continue
            if missing_created and address == "0x00426a20":
                continue
            created_rows.append((address, "created", expected["name"], expected["signature"], "disassemble+create succeeded; renamed"))
        create_apply.write_text(
            "address\tstatus\tname\tsignature\tnote\n"
            + "\n".join("\t".join(row) for row in created_rows)
            + "\n",
            encoding="utf-8",
        )
        queue.write_text(
            json.dumps(
                {
                    "status": "PASS",
                    "totalFunctions": 5883 if bad_queue_total else 5884,
                    "qualitySignals": {
                        "commentlessFunctionCount": 5141,
                        "undefinedSignatureCount": 1997,
                        "paramSignatureCount": 2307,
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
            "create_apply_path": create_apply,
            "queue_json_path": queue,
        }

    def test_accepts_recovered_collision_seeking_wave(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_fixture(Path(tmp))
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["targetCount"], 19)
        self.assertEqual(report["createdBoundaryReadBackTargets"], 8)
        self.assertEqual(report["queueTotalFunctions"], 5884)

    def test_rejects_stale_signature_and_missing_created_boundary(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_fixture(Path(tmp), stale_signature=True, missing_created=True)
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("signature mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("created target read-back missing" in failure for failure in report["failures"]))

    def test_rejects_queue_total_regression(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_fixture(Path(tmp), bad_queue_total=True)
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("totalFunctions" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
