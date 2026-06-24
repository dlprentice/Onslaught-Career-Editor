#!/usr/bin/env python3
"""Tests for the music timestamped CDB log producer."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from typing import Any

import winui_safe_copy_music_audible_output_materializer_test as fixtures
import winui_safe_copy_music_cdb_timeline_sidecar as timeline
import winui_safe_copy_music_timestamped_cdb_log_producer as producer


def write_json(path: Path, payload: dict[str, Any]) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def line_hash(line: str) -> str:
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def observation_ledger(raw_log: Path, *, role: str = "cleanBaseline") -> dict[str, Any]:
    lines = raw_log.read_text(encoding="utf-8").splitlines()
    base = dt.datetime(2026, 6, 24, 1, 2, 3, tzinfo=dt.timezone.utc)
    return {
        "schemaVersion": "winui-safe-copy-timestamped-cdb-log-observations.v1",
        "role": role,
        "timestampSource": "trusted-tail-wrapper-observation-ledger",
        "rawCdbLogSha256": producer.sha256_file(raw_log),
        "observations": [
            {
                "lineIndex": index,
                "lineSha256": line_hash(line),
                "observedAtUtc": (base + dt.timedelta(milliseconds=index * 100)).isoformat(timespec="milliseconds").replace("+00:00", "Z"),
            }
            for index, line in enumerate(lines)
        ],
    }


class MusicTimestampedCdbLogProducerTests(unittest.TestCase):
    def test_builds_timestamped_log_from_observation_ledger_and_timeline_accepts_it(self) -> None:
        with tempfile.TemporaryDirectory(prefix="timestamped-cdb-log-") as temp_dir:
            root = Path(temp_dir)
            raw_log = root / "clean" / "windbg.log"
            raw_log.parent.mkdir(parents=True)
            raw_log.write_text(fixtures.untimestamped_log_text(), encoding="utf-8")
            live = write_json(root / "clean" / "live.json", fixtures.live_payload(raw_log, role="cleanBaseline", staged=False))
            ledger = write_json(root / "clean" / "timestamp-ledger.json", observation_ledger(raw_log))
            timestamped_log = root / "out" / "clean" / "windbg.timestamped.log"
            receipt = root / "out" / "clean" / "timestamped-cdb-log-receipt.json"

            summary = producer.build_timestamped_log_from_paths(
                raw_cdb_log=raw_log,
                observation_ledger=ledger,
                timestamped_log_output=timestamped_log,
                receipt_output=receipt,
                allowed_output_root=root / "out",
                role="cleanBaseline",
            )

            self.assertTrue(timestamped_log.is_file())
            self.assertTrue(receipt.is_file())
            self.assertEqual("winui-safe-copy-timestamped-cdb-log.v1", summary["schemaVersion"])
            self.assertEqual("cleanBaseline", summary["role"])
            self.assertEqual(producer.sha256_file(raw_log), summary["rawCdbLogSha256"])
            self.assertEqual(producer.sha256_file(timestamped_log), summary["timestampedCdbLogSha256"])
            self.assertTrue(summary["cdbLogTimestamped"])
            self.assertFalse(summary["runtimeAudibleOutputProof"])

            sidecar = timeline.build_sidecar(
                live_path=live,
                timestamped_cdb_log=timestamped_log,
                output=root / "out" / "clean" / "timeline.json",
                role="cleanBaseline",
            )
            self.assertEqual(summary["timestampedCdbLogSha256"], sidecar["timestampedCdbLogSha256"])

    def test_rejects_ledger_bound_to_different_raw_log_hash(self) -> None:
        with tempfile.TemporaryDirectory(prefix="timestamped-cdb-log-") as temp_dir:
            root = Path(temp_dir)
            raw_log = root / "clean" / "windbg.log"
            raw_log.parent.mkdir(parents=True)
            raw_log.write_text(fixtures.untimestamped_log_text(), encoding="utf-8")
            ledger_payload = observation_ledger(raw_log)
            ledger_payload["rawCdbLogSha256"] = "0" * 64
            ledger = write_json(root / "clean" / "timestamp-ledger.json", ledger_payload)

            with self.assertRaises(producer.TimestampedCdbLogProducerError):
                producer.build_timestamped_log_from_paths(
                    raw_cdb_log=raw_log,
                    observation_ledger=ledger,
                    timestamped_log_output=root / "out" / "clean" / "windbg.timestamped.log",
                    receipt_output=root / "out" / "clean" / "receipt.json",
                    allowed_output_root=root / "out",
                    role="cleanBaseline",
                )

    def test_rejects_missing_required_observed_row(self) -> None:
        with tempfile.TemporaryDirectory(prefix="timestamped-cdb-log-") as temp_dir:
            root = Path(temp_dir)
            raw_log = root / "clean" / "windbg.log"
            raw_log.parent.mkdir(parents=True)
            raw_log.write_text(fixtures.untimestamped_log_text(), encoding="utf-8")
            ledger_payload = observation_ledger(raw_log)
            ledger_payload["observations"] = ledger_payload["observations"][:-1]
            ledger = write_json(root / "clean" / "timestamp-ledger.json", ledger_payload)

            with self.assertRaises(producer.TimestampedCdbLogProducerError):
                producer.build_timestamped_log_from_paths(
                    raw_cdb_log=raw_log,
                    observation_ledger=ledger,
                    timestamped_log_output=root / "out" / "clean" / "windbg.timestamped.log",
                    receipt_output=root / "out" / "clean" / "receipt.json",
                    allowed_output_root=root / "out",
                    role="cleanBaseline",
                )

    def test_rejects_output_outside_allowed_root(self) -> None:
        with tempfile.TemporaryDirectory(prefix="timestamped-cdb-log-") as temp_dir:
            root = Path(temp_dir)
            raw_log = root / "clean" / "windbg.log"
            raw_log.parent.mkdir(parents=True)
            raw_log.write_text(fixtures.untimestamped_log_text(), encoding="utf-8")
            ledger = write_json(root / "clean" / "timestamp-ledger.json", observation_ledger(raw_log))

            with self.assertRaises(producer.TimestampedCdbLogProducerError):
                producer.build_timestamped_log_from_paths(
                    raw_cdb_log=raw_log,
                    observation_ledger=ledger,
                    timestamped_log_output=root / "escaped.timestamped.log",
                    receipt_output=root / "out" / "clean" / "receipt.json",
                    allowed_output_root=root / "out",
                    role="cleanBaseline",
                )

    def test_rejects_overwriting_raw_log_even_with_overwrite_enabled(self) -> None:
        with tempfile.TemporaryDirectory(prefix="timestamped-cdb-log-") as temp_dir:
            root = Path(temp_dir)
            raw_log = root / "out" / "clean" / "windbg.log"
            raw_log.parent.mkdir(parents=True)
            raw_log.write_text(fixtures.untimestamped_log_text(), encoding="utf-8")
            ledger = write_json(root / "out" / "clean" / "timestamp-ledger.json", observation_ledger(raw_log))

            with self.assertRaises(producer.TimestampedCdbLogProducerError):
                producer.build_timestamped_log_from_paths(
                    raw_cdb_log=raw_log,
                    observation_ledger=ledger,
                    timestamped_log_output=raw_log,
                    receipt_output=root / "out" / "clean" / "receipt.json",
                    allowed_output_root=root / "out",
                    role="cleanBaseline",
                    allow_overwrite=True,
                )

    def test_rejects_raw_log_that_is_already_timestamped(self) -> None:
        with tempfile.TemporaryDirectory(prefix="timestamped-cdb-log-") as temp_dir:
            root = Path(temp_dir)
            raw_log = root / "clean" / "windbg.log"
            raw_log.parent.mkdir(parents=True)
            raw_log.write_text(fixtures.log_text(), encoding="utf-8")
            ledger = write_json(root / "clean" / "timestamp-ledger.json", observation_ledger(raw_log))

            with self.assertRaises(producer.TimestampedCdbLogProducerError):
                producer.build_timestamped_log_from_paths(
                    raw_cdb_log=raw_log,
                    observation_ledger=ledger,
                    timestamped_log_output=root / "out" / "clean" / "windbg.timestamped.log",
                    receipt_output=root / "out" / "clean" / "receipt.json",
                    allowed_output_root=root / "out",
                    role="cleanBaseline",
                )

    def test_self_test_passes(self) -> None:
        producer.self_test()

    def test_producer_stays_offline_and_does_not_spawn_processes(self) -> None:
        source = Path(producer.__file__).read_text(encoding="utf-8")

        self.assertNotIn("import subprocess", source)
        self.assertNotIn("subprocess.", source)
        self.assertNotIn("Popen(", source)
        self.assertNotIn("CreateProcess", source)
        self.assertNotIn("Get-Process", source)
        self.assertNotIn("Stop-Process", source)
        self.assertNotIn("BEA.exe", source)
        self.assertNotIn("cdb.exe", source)


if __name__ == "__main__":
    unittest.main()
