#!/usr/bin/env python3
"""Tests for the BattleEngine weapon event-handler rename probe."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import battleengine_weapon_event_handler_rename_probe as probe


INDEX_HEADER = "address\tname\tsignature\tstatus\n"
TABLE_HEADER = "slot\tentry_addr\tptr\tptr_name\tptr_signature\n"


def write_fixture(root: Path, *, omit_event_token: bool = False) -> dict[str, Path]:
    dry_log = root / "rename_dry.log"
    apply_log = root / "rename_apply.log"
    index = root / "index.tsv"
    table = root / "table.tsv"
    event_decompile = root / "00506930_CWeapon__HandleFireBurstEvent.c"
    dtor_decompile = root / "00505f70_CWeapon__scalar_deleting_dtor.c"

    dry_log.write_text(
        "\n".join(
            [
                "DRY: 0x00506930 CWeapon__VFunc_00_00506930 -> CWeapon__HandleFireBurstEvent",
                "DRY: 0x00505f70 CWeapon__VFunc_01_00505f70 -> CWeapon__scalar_deleting_dtor",
                "--- SUMMARY ---",
                "applied=0 skipped=2 missing=0 bad=0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    apply_log.write_text(
        "\n".join(
            [
                "OK: 0x00506930 CWeapon__VFunc_00_00506930 -> CWeapon__HandleFireBurstEvent",
                "OK: 0x00505f70 CWeapon__VFunc_01_00505f70 -> CWeapon__scalar_deleting_dtor",
                "--- SUMMARY ---",
                "applied=2 skipped=0 missing=0 bad=0",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    index.write_text(
        INDEX_HEADER
        + "0x00506930\tCWeapon__HandleFireBurstEvent\tundefined CWeapon__HandleFireBurstEvent(void)\tOK\n"
        + "0x00505f70\tCWeapon__scalar_deleting_dtor\tvoid * __thiscall CWeapon__scalar_deleting_dtor(void * this, void * param_1, int param_2)\tOK\n",
        encoding="utf-8",
    )
    table.write_text(
        TABLE_HEADER
        + "0\t005dfc94\t00506930\tCWeapon__HandleFireBurstEvent\tundefined CWeapon__HandleFireBurstEvent(void)\n"
        + "1\t005dfc98\t00505f70\tCWeapon__scalar_deleting_dtor\tvoid * __thiscall CWeapon__scalar_deleting_dtor(void * this, void * param_1, int param_2)\n"
        + "4\t005dfca4\t38d1b717\t<none>\t<none>\n",
        encoding="utf-8",
    )
    event_tokens = ["CEventManager__AddEvent_AtTime", "CEngine__SpawnProjectileBurstFromCurrentPreset"]
    if not omit_event_token:
        event_tokens.append("0x1389")
    event_decompile.write_text("\n".join(event_tokens) + "\n", encoding="utf-8")
    dtor_decompile.write_text(
        "CWeapon__DetachFromSetAndShutdownMonitor(this);\nOID__FreeObject(this);\n",
        encoding="utf-8",
    )
    return {
        "dry_log": dry_log,
        "apply_log": apply_log,
        "index": index,
        "table": table,
        "event_decompile": event_decompile,
        "dtor_decompile": dtor_decompile,
    }


class BattleEngineWeaponEventHandlerRenameProbeTests(unittest.TestCase):
    def test_passes_for_rename_readback_and_behavior_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp))
            report = probe.build_report(
                dry_log_path=paths["dry_log"],
                apply_log_path=paths["apply_log"],
                decompile_index_path=paths["index"],
                pointer_table_path=paths["table"],
                event_decompile_path=paths["event_decompile"],
                dtor_decompile_path=paths["dtor_decompile"],
            )

        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertEqual(report["candidateClassification"], "weapon-event-handler-and-dtor-renamed")
        self.assertTrue(report["readback"]["eventHandlerRenamed"])
        self.assertTrue(report["readback"]["scalarDtorRenamed"])
        self.assertTrue(report["evidence"]["eventSchedulesBurst"])
        self.assertTrue(report["evidence"]["dtorIsScalarDeleting"])

    def test_fails_when_event_handler_token_is_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            paths = write_fixture(Path(tmp), omit_event_token=True)
            report = probe.build_report(
                dry_log_path=paths["dry_log"],
                apply_log_path=paths["apply_log"],
                decompile_index_path=paths["index"],
                pointer_table_path=paths["table"],
                event_decompile_path=paths["event_decompile"],
                dtor_decompile_path=paths["dtor_decompile"],
            )

        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("event handler decompile" in failure for failure in report["failures"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
