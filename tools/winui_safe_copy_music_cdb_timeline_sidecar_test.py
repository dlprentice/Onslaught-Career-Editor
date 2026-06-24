#!/usr/bin/env python3
"""Tests for music CDB decode timeline sidecar materialization."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import winui_safe_copy_music_audible_output_materializer_test as fixtures
import winui_safe_copy_music_cdb_timeline_sidecar as timeline


class MusicCdbTimelineSidecarTests(unittest.TestCase):
    def test_builds_timeline_bound_to_live_raw_and_timestamped_cdb_logs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            raw_log = root / "clean" / "windbg.log"
            timestamped_log = root / "clean" / "windbg.timestamped.log"
            raw_log.parent.mkdir(parents=True, exist_ok=True)
            raw_log.write_text(fixtures.untimestamped_log_text(), encoding="utf-8")
            timestamped_log.write_text(fixtures.log_text(), encoding="utf-8")
            live = fixtures.write_json(
                root / "clean" / "live.json",
                fixtures.live_payload(raw_log, role="cleanBaseline", staged=False),
            )
            output = root / "clean" / "timeline.json"

            sidecar = timeline.build_sidecar(
                live_path=live,
                timestamped_cdb_log=timestamped_log,
                output=output,
                role="cleanBaseline",
            )

            self.assertEqual("winui-safe-copy-music-cdb-decode-timeline.v1", sidecar["schemaVersion"])
            self.assertEqual("cleanBaseline", sidecar["role"])
            self.assertEqual("timestamped-cdb-log", sidecar["timestampSource"])
            self.assertTrue(sidecar["cdbLogTimestamped"])
            self.assertEqual(fixtures.sha256_file(live), sidecar["liveArtifactSha256"])
            self.assertEqual(fixtures.sha256_file(raw_log), sidecar["rawCdbLogSha256"])
            self.assertEqual(fixtures.sha256_file(timestamped_log), sidecar["timestampedCdbLogSha256"])
            self.assertEqual(sidecar["timestampedCdbLogSha256"], sidecar["cdbLogSha256"])
            self.assertTrue(output.is_file())

    def test_rejects_timestamped_log_without_cdb_event_timestamps(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            raw_log = root / "clean" / "windbg.log"
            timestamped_log = root / "clean" / "windbg.timestamped.log"
            raw_log.parent.mkdir(parents=True, exist_ok=True)
            raw_log.write_text(fixtures.untimestamped_log_text(), encoding="utf-8")
            timestamped_log.write_text(fixtures.untimestamped_log_text(), encoding="utf-8")
            live = fixtures.write_json(
                root / "clean" / "live.json",
                fixtures.live_payload(raw_log, role="cleanBaseline", staged=False),
            )

            with self.assertRaises(timeline.TimelineSidecarError):
                timeline.build_sidecar(
                    live_path=live,
                    timestamped_cdb_log=timestamped_log,
                    output=root / "clean" / "timeline.json",
                    role="cleanBaseline",
                )

    def test_cli_without_required_paths_reports_missing_live_argument(self) -> None:
        result = subprocess.run(
            [sys.executable, str(Path(timeline.__file__))],
            capture_output=True,
            check=False,
            text=True,
        )

        self.assertEqual(2, result.returncode)
        self.assertIn("Provide --live or --self-test.", result.stdout)
        self.assertNotIn("Is a directory", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
