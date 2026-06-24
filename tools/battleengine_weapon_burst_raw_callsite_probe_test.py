#!/usr/bin/env python3
"""Tests for the BattleEngine raw burst-callsite probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import battleengine_weapon_burst_raw_callsite_probe as probe


HEADER = "\t".join(
    [
        "target_raw",
        "target_addr",
        "role",
        "ordinal",
        "instruction_addr",
        "function_entry",
        "function_name",
        "mnemonic",
        "operands",
        "bytes",
        "flow_type",
    ]
)


def row(
    target: str,
    role: str,
    ordinal: int,
    addr: str,
    mnemonic: str,
    operands: str = "",
    function_entry: str = "<none>",
    function_name: str = "<no_function>",
) -> str:
    return "\t".join(
        [
            target,
            target,
            role,
            str(ordinal),
            addr,
            function_entry,
            function_name,
            mnemonic,
            operands,
            "",
            "UNCONDITIONAL_CALL" if mnemonic == "CALL" else "FALL_THROUGH",
        ]
    )


def write_sample(path: Path, *, weapon_named: bool = False) -> None:
    rows = [
        HEADER,
        row("0x0044e093", "BEFORE", -4, "0x0044e088", "CALL", "0x00509f70"),
        row("0x0044e093", "TARGET", 0, "0x0044e093", "CALL", "0x00506010"),
        row("0x0044e093", "AFTER", 6, "0x0044e0a7", "MOV", "dword ptr [ESI + 0x1a4], EAX"),
        row("0x0044e093", "AFTER", 18, "0x0044e0c6", "CMP", "EAX, 0x18"),
        row("0x0044e093", "AFTER", 20, "0x0044e0cb", "CMP", "EAX, 0x1b"),
        row("0x004f4bd6", "BEFORE", -15, "0x004f4bab", "FSQRT"),
        row("0x004f4bd6", "BEFORE", -9, "0x004f4bbb", "FCOMPP"),
        row("0x004f4bd6", "BEFORE", -8, "0x004f4bb1", "FSUB", "float ptr [0x005d8cc0]"),
        row("0x004f4bd6", "BEFORE", -5, "0x004f4bc9", "CALL", "0x00492020"),
        row(
            "0x004f4bd6",
            "TARGET",
            0,
            "0x004f4bd6",
            "CALL",
            "0x00506010",
            "0x00400000" if weapon_named else "<none>",
            "CBattleEngine__WeaponFired" if weapon_named else "<no_function>",
        ),
        row("0x004f4bd6", "AFTER", 2, "0x004f4bdd", "MOV", "ESI, dword ptr [EDI + 0x70]"),
        row("0x004f4bd6", "AFTER", 10, "0x004f4c01", "CALL", "0x0050ff10"),
        row("0x004f4bd6", "AFTER", 16, "0x004f4c19", "CALL", "0x0048dcf0"),
    ]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


class BattleEngineWeaponBurstRawCallsiteProbeTests(unittest.TestCase):
    def test_passes_for_current_unowned_raw_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "instructions.tsv"
            write_sample(path)

            report = probe.build_report(instructions_path=path)

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["candidateClassification"], "raw-callsites-unowned-shared-context")
        self.assertEqual(report["targetCallsiteCount"], 2)
        self.assertEqual(report["ownedFunctionRows"], 0)

    def test_fails_on_weapon_named_owner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "instructions.tsv"
            write_sample(path, weapon_named=True)

            report = probe.build_report(instructions_path=path)

        self.assertEqual(report["status"], "FAIL")
        self.assertGreater(len(report["weaponNamedRows"]), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
