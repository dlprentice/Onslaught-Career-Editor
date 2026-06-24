#!/usr/bin/env python3
"""Self-tests for the fatal/controller signature tranche probe."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_fatal_controller_signature_tranche_probe.py"


def load_module():
    spec = importlib.util.spec_from_file_location("probe", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FatalControllerSignatureTrancheProbeTests(unittest.TestCase):
    def write_fixture(
        self,
        root: Path,
        *,
        stale_owner_name: bool = False,
        missing_comment_token: bool = False,
        bad_apply_summary: bool = False,
        bad_queue: bool = False,
    ) -> dict[str, Path]:
        probe = load_module()
        decompile_dir = root / "decompile_final"
        decompile_dir.mkdir(parents=True)
        metadata = root / "metadata_final.tsv"
        index = decompile_dir / "index.tsv"
        xrefs = root / "xrefs_final.tsv"
        instructions = root / "instructions_final.tsv"
        tags = root / "tags_final.tsv"
        dry_log = root / "dry.log"
        apply_log = root / "apply.log"
        queue = root / "static-reaudit-queue.json"

        metadata_rows = []
        index_rows = []
        tag_rows = []
        xref_rows = []
        instruction_rows = []
        for address, expected in probe.TARGETS.items():
            name = expected["name"]
            if stale_owner_name and address == "0x0042e750":
                name = "CGame__DispatchVibrationWithCareerGate"
            signature = " ".join(expected["signature"])
            comment_tokens = list(expected["comment"])
            if missing_comment_token and address == "0x0042d7d0":
                comment_tokens = comment_tokens[:-1]
            comment = "; ".join(comment_tokens)
            metadata_rows.append((address, name, signature, comment, "OK"))
            index_rows.append((address, name, signature, "OK"))
            tag_rows.append((address, name, ";".join(expected["tags"]), "OK"))
            (decompile_dir / f"{address[2:]}_{name}.c").write_text(
                " ".join(expected["decompile"]) + "\n" + signature + " {}\n",
                encoding="utf-8",
            )
            xref_rows.append((address, name, "0x005e0000", "<none>", "<no_function>", "UNCONDITIONAL_CALL"))
            instruction_rows.append(
                (
                    address,
                    address,
                    "TARGET",
                    "0",
                    expected["instruction"][0],
                    address,
                    name,
                    expected["instruction"][1],
                    " ".join(expected["instruction"][2:]),
                    "90",
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

        dry = dict(probe.EXPECTED_DRY)
        apply = dict(probe.EXPECTED_APPLY)
        if bad_apply_summary:
            apply["renamed"] -= 1
        dry_log.write_text(
            "SUMMARY: " + " ".join(f"{key}={value}" for key, value in dry.items()) + "\n",
            encoding="utf-8",
        )
        apply_log.write_text(
            "SUMMARY: " + " ".join(f"{key}={value}" for key, value in apply.items()) + "\n",
            encoding="utf-8",
        )

        expected_queue = dict(probe.EXPECTED_QUEUE)
        if bad_queue:
            expected_queue["paramSignatureCount"] += 1
        queue.write_text(json.dumps({"status": "PASS", "qualitySignals": expected_queue}), encoding="utf-8")

        return {
            "dry_log_path": dry_log,
            "apply_log_path": apply_log,
            "metadata_path": metadata,
            "decompile_index_path": index,
            "decompile_dir": decompile_dir,
            "xrefs_path": xrefs,
            "instructions_path": instructions,
            "tags_path": tags,
            "queue_json_path": queue,
        }

    def test_accepts_expected_tranche(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**self.write_fixture(Path(tmp)))
        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["targetCount"], 7)
        self.assertEqual(report["renamedTargetCount"], 4)
        self.assertEqual(report["sourceParityTargetCount"], 2)

    def test_rejects_stale_owner_and_missing_comment_token(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(
                **self.write_fixture(Path(tmp), stale_owner_name=True, missing_comment_token=True)
            )
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("metadata name" in failure for failure in report["failures"]))
        self.assertTrue(any("comment missing token" in failure for failure in report["failures"]))

    def test_rejects_apply_summary_and_queue_regression(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**self.write_fixture(Path(tmp), bad_apply_summary=True, bad_queue=True))
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("apply summary mismatch" in failure for failure in report["failures"]))
        self.assertTrue(any("paramSignatureCount" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
