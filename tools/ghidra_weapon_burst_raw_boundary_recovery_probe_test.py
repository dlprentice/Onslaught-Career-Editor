#!/usr/bin/env python3
"""Tests for the weapon-burst raw caller-boundary recovery probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import ghidra_weapon_burst_raw_boundary_recovery_probe as probe


METADATA_HEADER = "address\tname\tsignature\tcomment\tstatus\n"
INDEX_HEADER = "address\tname\tsignature\tstatus\n"
XREF_HEADER = "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
INSTRUCTION_HEADER = (
    "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\t"
    "mnemonic\toperands\tbytes\tflow_type\n"
)
CREATE_HEADER = "address\tstatus\tname\tsignature\tnote\n"


def write_fixture(root: Path, *, stale_boundary_name: bool = False) -> None:
    decompile = root / "decompile"
    decompile.mkdir()

    target_comment = (
        "Owner-neutral correction. Static Ghidra evidence only; raw caller-boundary recovery now "
        "resolves the prior unowned calls at 0x0044e093 and 0x004f4bd6. Proof-boundary: exact "
        "source identity, weapon_fire_breaks_stealth, runtime stealth behavior, tags/locals/types, "
        "and concrete layout remain unproven."
    )
    current_comment = (
        "Owner-neutral correction. Static Ghidra evidence only; raw percent-bucket fallback "
        "callsites are now bounded at ProjectileBurstCallerBoundary_0044e020 and "
        "ProjectileBurstCallerBoundary_004f4920. Proof-boundary: exact CWeapon::Fire, "
        "CBattleEngine::WeaponFired, weapon_fire_breaks_stealth, and runtime stealth behavior "
        "remain unproven."
    )

    metadata_lines = [
        METADATA_HEADER,
        f"{probe.TARGET_ADDRESS}\t{probe.TARGET_NAME}\tint __fastcall {probe.TARGET_NAME}(void *)\t{target_comment}\tOK\n",
        f"{probe.CURRENT_PRESET_ADDRESS}\t{probe.CURRENT_PRESET_NAME}\tint __fastcall {probe.CURRENT_PRESET_NAME}(void *)\t{current_comment}\tOK\n",
    ]
    index_lines = [INDEX_HEADER]
    xref_lines = [XREF_HEADER]
    instruction_lines = [INSTRUCTION_HEADER]
    create_dry_lines = [CREATE_HEADER]
    create_apply_lines = [CREATE_HEADER]

    for boundary in probe.BOUNDARIES:
        name = boundary["name"]
        if stale_boundary_name and boundary["address"] == "0x0044e020":
            name = "FUN_0044e020"
        address = boundary["address"]
        callsite = boundary["callsite"]
        comment = (
            f"Recovered owner-neutral projectile-burst raw caller boundary. Contains raw callsite "
            f"{callsite} into {probe.TARGET_NAME} and nearby {boundary['context']} context. "
            "Proof-boundary: exact owner/source identity, weapon_fire_breaks_stealth, runtime "
            "behavior, tags/locals/types, and concrete layout remain unproven."
        )
        metadata_lines.append(f"{address}\t{name}\tundefined {name}(void)\t{comment}\tOK\n")
        index_lines.append(f"{address}\t{name}\tundefined {name}(void)\tOK\n")
        decompile.joinpath(f"{address[2:]}_{name}.c").write_text(
            f"/* name: {name} */\nvoid {name}(void) {{ {probe.TARGET_NAME}(); }}\n",
            encoding="utf-8",
        )
        xref_lines.append(
            f"{probe.TARGET_ADDRESS[2:]}\t{probe.TARGET_NAME}\t{callsite[2:]}\t{address[2:]}\t{name}\tUNCONDITIONAL_CALL\n"
        )
        instruction_lines.append(
            f"{callsite}\t{callsite}\tTARGET\t0\t{callsite}\t{address}\t{name}\tCALL\t{probe.TARGET_ADDRESS}\te8 00 00 00 00\tUNCONDITIONAL_CALL\n"
        )
        create_dry_lines.append(
            f"{address[2:]}\twould_create\t\t\tdry-run would disassemble+create and name {boundary['name']}\n"
        )
        create_apply_lines.append(
            f"{address[2:]}\tcreated\t{name}\tundefined {name}(void)\tdisassemble+create succeeded; renamed\n"
        )

    root.joinpath("metadata.tsv").write_text("".join(metadata_lines), encoding="utf-8")
    root.joinpath("index.tsv").write_text("".join(index_lines), encoding="utf-8")
    root.joinpath("xrefs.tsv").write_text("".join(xref_lines), encoding="utf-8")
    root.joinpath("instructions.tsv").write_text("".join(instruction_lines), encoding="utf-8")
    root.joinpath("create_dry.tsv").write_text("".join(create_dry_lines), encoding="utf-8")
    root.joinpath("create_apply.tsv").write_text("".join(create_apply_lines), encoding="utf-8")


class GhidraWeaponBurstRawBoundaryRecoveryProbeTests(unittest.TestCase):
    def test_accepts_recovered_boundaries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root)

            report = probe.build_report(
                create_dry_path=root / "create_dry.tsv",
                create_apply_path=root / "create_apply.tsv",
                metadata_path=root / "metadata.tsv",
                decompile_index_path=root / "index.tsv",
                decompile_dir=root / "decompile",
                xrefs_path=root / "xrefs.tsv",
                instructions_path=root / "instructions.tsv",
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(len(report["recoveredBoundaries"]), 2)
        self.assertEqual(report["weaponFireBreaksStealthStatus"], "unresolved")

    def test_fails_on_stale_generic_boundary_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_fixture(root, stale_boundary_name=True)

            report = probe.build_report(
                create_dry_path=root / "create_dry.tsv",
                create_apply_path=root / "create_apply.tsv",
                metadata_path=root / "metadata.tsv",
                decompile_index_path=root / "index.tsv",
                decompile_dir=root / "decompile",
                xrefs_path=root / "xrefs.tsv",
                instructions_path=root / "instructions.tsv",
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("0x0044e020" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
