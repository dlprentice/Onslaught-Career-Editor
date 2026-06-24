#!/usr/bin/env python3
"""Self-tests for the cockpit/volume/UnitAI correction probe."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_cockpit_volume_unitai_signature_correction_probe.py"


def load_module():
    spec = importlib.util.spec_from_file_location("probe", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CockpitVolumeUnitAiSignatureCorrectionProbeTests(unittest.TestCase):
    def write_fixture(
        self,
        root: Path,
        *,
        stale_final_name: bool = False,
        stale_final_signature: bool = False,
        bad_queue_metric: bool = False,
    ) -> dict[str, Path]:
        probe = load_module()
        decompile_dir = root / "decompile_final"
        decompile_dir.mkdir(parents=True)
        before = root / "metadata_before.tsv"
        metadata = root / "metadata_final.tsv"
        index = decompile_dir / "index.tsv"
        xrefs = root / "xrefs_final.tsv"
        instructions = root / "instructions_final.tsv"
        queue = root / "static-reaudit-queue.json"

        before_rows = []
        final_rows = []
        index_rows = []
        for address, expected in probe.TARGETS.items():
            before_rows.append((address, expected["before_name"], expected["before_signature"], "", "OK"))
            name = expected["name"]
            signature = expected["signature"]
            if stale_final_name and address == "0x00425760":
                name = expected["before_name"]
            if stale_final_signature and address == "0x004244b0":
                signature = expected["before_signature"]
            comment = "; ".join(expected["comment"])
            final_rows.append((address, name, signature, comment, "OK"))
            index_rows.append((address, name, signature, "OK"))
            (decompile_dir / f"{address[2:]}_{name}.c").write_text(
                f"/* {comment} */\n{signature} {{}}\n",
                encoding="utf-8",
            )

        before.write_text(
            "address\tname\tsignature\tcomment\tstatus\n"
            + "\n".join("\t".join(row) for row in before_rows)
            + "\n",
            encoding="utf-8",
        )
        metadata.write_text(
            "address\tname\tsignature\tcomment\tstatus\n"
            + "\n".join("\t".join(row) for row in final_rows)
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
                f"{address}\t{expected['name']}\t0x004055dc\t0x00404dd0\tCBattleEngine__Init\tUNCONDITIONAL_CALL"
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
        queue.write_text(
            json.dumps(
                {
                    "status": "PASS",
                    "totalFunctions": 5876,
                    "qualitySignals": {
                        "commentlessFunctionCount": 5153 if bad_queue_metric else 5152,
                        "undefinedSignatureCount": 2013,
                        "paramSignatureCount": 2310,
                    },
                }
            ),
            encoding="utf-8",
        )
        return {
            "metadata_before_path": before,
            "metadata_final_path": metadata,
            "decompile_index_path": index,
            "decompile_dir": decompile_dir,
            "xrefs_path": xrefs,
            "instructions_path": instructions,
            "queue_json_path": queue,
        }

    def test_accepts_wave321_readback(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_fixture(Path(tmp))
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["signatureCorrectedTargets"], 9)
        self.assertEqual(report["renamedTargets"], 2)
        self.assertEqual(report["queueCommentlessFunctions"], 5152)
        self.assertEqual(report["queueParamSignatures"], 2310)

    def test_rejects_stale_final_name_and_signature(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_fixture(Path(tmp), stale_final_name=True, stale_final_signature=True)
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("CCockpit__ctor signature" in failure for failure in report["failures"]))
        self.assertTrue(any("Mat34__OrthonormalizeAxes final name" in failure for failure in report["failures"]))

    def test_rejects_queue_metric_drift(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_fixture(Path(tmp), bad_queue_metric=True)
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("commentlessFunctionCount" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
