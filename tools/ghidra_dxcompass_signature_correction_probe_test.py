#!/usr/bin/env python3
"""Self-tests for the DXCompass signature correction probe."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_dxcompass_signature_correction_probe.py"


def load_module():
    spec = importlib.util.spec_from_file_location("probe", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class DXCompassSignatureCorrectionProbeTests(unittest.TestCase):
    def write_fixture(
        self,
        root: Path,
        *,
        stale_signature: bool = False,
        bad_queue_counts: bool = False,
        missing_xref: bool = False,
    ) -> dict[str, Path]:
        probe = load_module()
        decompile_dir = root / "decompile_final"
        decompile_dir.mkdir(parents=True)
        metadata = root / "metadata_final.tsv"
        index = decompile_dir / "index.tsv"
        xrefs = root / "xrefs_final.tsv"
        instructions = root / "instructions_final.tsv"
        queue = root / "static-reaudit-queue.json"

        metadata_rows = []
        index_rows = []
        for address, expected in probe.TARGETS.items():
            signature = expected["signature"]
            if stale_signature and address == "0x00427210":
                signature = "undefined CDXCompass__Render(void)"
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
        xref_lines = []
        for address, expected in probe.TARGETS.items():
            if missing_xref and address == "0x0053c1d0":
                continue
            xref_lines.append(f"{address}\t{expected['name']}\t0x0053c0f3\t0x0053be40\tCDXCompass__Init\tUNCONDITIONAL_CALL")
        xrefs.write_text(
            "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
            + "\n".join(xref_lines)
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
                    "totalFunctions": 5884,
                    "qualitySignals": {
                        "commentlessFunctionCount": 5134 if bad_queue_counts else 5133,
                        "undefinedSignatureCount": 1998 if bad_queue_counts else 1997,
                        "paramSignatureCount": 2307 if bad_queue_counts else 2306,
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
            "queue_json_path": queue,
        }

    def test_accepts_dxcompass_signature_wave(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_fixture(Path(tmp))
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["targetCount"], 8)
        self.assertEqual(report["queueUndefinedSignatures"], 1997)
        self.assertEqual(report["queueParamSignatures"], 2306)

    def test_rejects_stale_render_signature_and_missing_xref(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_fixture(Path(tmp), stale_signature=True, missing_xref=True)
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("signature mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("has no xref rows" in failure for failure in report["failures"]))

    def test_rejects_queue_count_regression(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.write_fixture(Path(tmp), bad_queue_counts=True)
            report = probe.build_report(**paths)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("undefinedSignatureCount" in failure for failure in report["failures"]))
        self.assertTrue(any("paramSignatureCount" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
