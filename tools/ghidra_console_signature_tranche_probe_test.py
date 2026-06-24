#!/usr/bin/env python3
"""Self-tests for the Console signature tranche probe."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "ghidra_console_signature_tranche_probe.py"


def load_module():
    spec = importlib.util.spec_from_file_location("probe", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ConsoleSignatureTrancheProbeTests(unittest.TestCase):
    def write_fixture(
        self,
        root: Path,
        *,
        stale_vfunc_name: bool = False,
        missing_tag: bool = False,
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
        queue = root / "static-reaudit-queue.json"

        metadata_rows = []
        index_rows = []
        tag_rows = []
        xref_rows = []
        instruction_rows = []
        for address, expected in probe.TARGETS.items():
            name = expected["name"]
            if stale_vfunc_name and address == "0x0042c440":
                name = "VFuncSlot_05_0042c440"
            signature = expected["signature"]
            comment = "; ".join(expected["comment"])
            metadata_rows.append((address, name, signature, comment, "OK"))
            index_rows.append((address, name, signature, "OK"))
            target_tags = expected["tags"]
            if missing_tag and address == "0x00429bc0":
                target_tags = target_tags[:-1]
            tag_rows.append((address, name, ";".join(target_tags), "OK"))
            (decompile_dir / f"{address[2:]}_{name}.c").write_text(
                f"/* {comment} */\n{signature} {{}}\n",
                encoding="utf-8",
            )
            xref_rows.append((address, name, "0x005e0000", "<none>", "<no_function>", "UNCONDITIONAL_CALL"))
            instruction_rows.append((address, address, "TARGET", "0", address, address, name, "MOV", "EAX, EAX", "90", "FALL_THROUGH"))

        for index_extra in range(7):
            xref_rows.append(
                (
                    "0x0042c440",
                    probe.TARGETS["0x0042c440"]["name"],
                    f"0x005d97{index_extra:02x}",
                    "<none>",
                    "<no_function>",
                    "DATA",
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
        expected_queue = dict(probe.EXPECTED_QUEUE)
        if bad_queue_counts:
            expected_queue["commentlessFunctionCount"] += 1
        queue.write_text(json.dumps({"status": "PASS", "qualitySignals": expected_queue}), encoding="utf-8")
        return {
            "metadata_final_path": metadata,
            "decompile_index_path": index,
            "decompile_dir": decompile_dir,
            "xrefs_path": xrefs,
            "instructions_path": instructions,
            "tags_path": tags,
            "queue_json_path": queue,
        }

    def test_accepts_console_signature_tranche(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**self.write_fixture(Path(tmp)))
        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["targetCount"], 16)
        self.assertEqual(report["renamedTargetCount"], 1)
        self.assertEqual(report["undefinedFixedTargetCount"], 4)

    def test_rejects_stale_vfunc_name_and_missing_tag(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**self.write_fixture(Path(tmp), stale_vfunc_name=True, missing_tag=True))
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("generic VFuncSlot" in failure for failure in report["failures"]))
        self.assertTrue(any("missing tag" in failure for failure in report["failures"]))

    def test_rejects_queue_regression(self) -> None:
        probe = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            report = probe.build_report(**self.write_fixture(Path(tmp), bad_queue_counts=True))
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("commentlessFunctionCount" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
