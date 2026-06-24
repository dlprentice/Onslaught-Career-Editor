#!/usr/bin/env python3
"""Self-tests for the Career save helper signature tranche probe."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_career_save_helper_signature_tranche_probe.py"


def load_module():
    spec = importlib.util.spec_from_file_location("probe", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CareerSaveHelperSignatureTrancheProbeTests(unittest.TestCase):
    def write_fixture(
        self,
        root: Path,
        *,
        missing_comment: bool = False,
        missing_tag: bool = False,
        missing_xref: bool = False,
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
        queue = root / "static-reaudit-queue.json"

        metadata_rows = []
        index_rows = []
        tag_rows = []
        for address, expected in probe.TARGETS.items():
            comment = "; ".join(expected["comment"])
            if missing_comment and address == "0x0041bdf0":
                comment = "stale god mode note"
            metadata_rows.append((address, expected["name"], expected["signature"], comment, "OK"))
            index_rows.append((address, expected["name"], expected["signature"], "OK"))
            final_tags = list(expected["tags"])
            if missing_tag and address == "0x004213c0":
                final_tags = [tag for tag in final_tags if tag != "save-format"]
            tag_rows.append((address, expected["name"], ";".join(final_tags), "OK"))
            (decompile_dir / f"{address[2:]}_{expected['name']}.c").write_text(
                f"/* {comment} */\n{expected['signature']} {{}}\n",
                encoding="utf-8",
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
        xref_rows = list(probe.EXPECTED_XREFS)
        if missing_xref:
            xref_rows = [row for row in xref_rows if row[0] != "0x004213c0"]
        xrefs.write_text(
            "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
            + "\n".join(
                f"{target}\t{probe.TARGETS[target]['name']}\t0x0041bd12\t0x0041bd00\t{caller}\tUNCONDITIONAL_CALL"
                for target, caller in xref_rows
            )
            + "\n",
            encoding="utf-8",
        )
        instructions.write_text(
            "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
            + "\n".join(
                f"{address}\t{address}\tTARGET\t0\t{address}\t{address}\t{expected['name']}\tRET\t\tc3\tTERMINATOR"
                for address, expected in probe.TARGETS.items()
            )
            + "\n",
            encoding="utf-8",
        )
        tags.write_text(
            "address\tname\ttags\tstatus\n" + "\n".join("\t".join(row) for row in tag_rows) + "\n",
            encoding="utf-8",
        )
        queue.write_text(
            json.dumps(
                {
                    "status": "PASS",
                    "totalFunctions": 5884,
                    "qualitySignals": {
                        "commentlessFunctionCount": 5067 if bad_queue else 5066,
                        "undefinedSignatureCount": 1989 if bad_queue else 1988,
                        "paramSignatureCount": 2269,
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
            "queue_json_path": queue,
        }

    def test_accepts_career_save_helper_signature_wave(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**self.write_fixture(Path(tmp)))
        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["targetCount"], 21)
        self.assertEqual(report["queueCommentlessFunctions"], 5066)
        self.assertEqual(report["queueUndefinedSignatures"], 1988)

    def test_rejects_missing_comment_and_tag(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**self.write_fixture(Path(tmp), missing_comment=True, missing_tag=True))
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("comment token missing" in failure for failure in report["failures"]))
        self.assertTrue(any("tag missing" in failure for failure in report["failures"]))

    def test_rejects_missing_xref_and_queue_regression(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**self.write_fixture(Path(tmp), missing_xref=True, bad_queue=True))
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("expected xref missing" in failure for failure in report["failures"]))
        self.assertTrue(any("queue" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
