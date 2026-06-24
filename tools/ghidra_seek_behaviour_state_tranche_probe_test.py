#!/usr/bin/env python3
"""Self-test for ghidra_seek_behaviour_state_tranche_probe."""

from __future__ import annotations

import csv
import tempfile
import unittest
from pathlib import Path

import ghidra_seek_behaviour_state_tranche_probe as probe


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


class SeekBehaviourStateProbeTests(unittest.TestCase):
    def test_norm_addr_pads_and_prefixes(self) -> None:
        self.assertEqual(probe.norm_addr("43e2b0"), "0x0043e2b0")
        self.assertEqual(probe.norm_addr("0x005DAC58"), "0x005dac58")

    def test_run_check_accepts_minimal_valid_exports(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            metadata_rows = []
            tag_rows = []
            for address, spec in probe.TARGETS.items():
                metadata_rows.append(
                    {
                        "address": address,
                        "name": str(spec["name"]),
                        "signature": " ".join(spec["signature"]),  # type: ignore[arg-type]
                        "comment": " ".join(spec["comment"]),  # type: ignore[arg-type]
                        "status": "OK",
                    }
                )
                tag_rows.append(
                    {
                        "address": address[2:],
                        "name": str(spec["name"]),
                        "tags": ",".join(spec["tags"]),  # type: ignore[arg-type]
                        "status": "OK",
                    }
                )
                (base / "decompile" / f"{address[2:]}_{spec['name']}.c").parent.mkdir(parents=True, exist_ok=True)
                (base / "decompile" / f"{address[2:]}_{spec['name']}.c").write_text("ok\n", encoding="utf-8")

            xref_rows = [
                {
                    "target_addr": target,
                    "target_name": "",
                    "from_addr": from_addr,
                    "from_function_addr": "",
                    "from_function": "",
                    "ref_type": "DATA",
                }
                for target, from_addr in probe.EXPECTED_XREFS
            ]
            vtable_rows = [
                {
                    "vtable": vtable,
                    "slot_index": "0",
                    "slot_addr": "",
                    "pointer_raw": "",
                    "pointer_addr": "",
                    "function_entry": "",
                    "function_name": name,
                    "containing_entry": "",
                    "containing_name": "",
                    "status": "OK",
                }
                for vtable, name in probe.EXPECTED_VTABLE_SLOT0
            ]

            write_tsv(base / "metadata.tsv", metadata_rows, ["address", "name", "signature", "comment", "status"])
            write_tsv(base / "tags.tsv", tag_rows, ["address", "name", "tags", "status"])
            write_tsv(
                base / "xrefs.tsv",
                xref_rows,
                ["target_addr", "target_name", "from_addr", "from_function_addr", "from_function", "ref_type"],
            )
            write_tsv(
                base / "vtable_slots.tsv",
                vtable_rows,
                [
                    "vtable",
                    "slot_index",
                    "slot_addr",
                    "pointer_raw",
                    "pointer_addr",
                    "function_entry",
                    "function_name",
                    "containing_entry",
                    "containing_name",
                    "status",
                ],
            )

            failures, summary = probe.run_check(base)
            self.assertEqual([], failures)
            self.assertEqual("PASS", summary["status"])


if __name__ == "__main__":
    unittest.main()
