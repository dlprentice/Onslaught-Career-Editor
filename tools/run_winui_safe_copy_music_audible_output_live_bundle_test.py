#!/usr/bin/env python3
"""Tests for the private music audible-output live-bundle executor."""

from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import tempfile
import unittest
from unittest import mock
from pathlib import Path

import run_winui_safe_copy_music_audible_output_live_bundle as live_bundle
import winui_safe_copy_music_audible_output_materializer_test as materializer_fixtures
import winui_safe_copy_music_timestamped_cdb_log_producer as timestamp_producer


EXPECTED_AUDIO_CAPTURE_STARTUP_MARGIN_MS = 15000


def cdb_live_payload(
    *,
    cleanup_status: str = "stopped",
    launch_process_id: int = 2468,
    target_process_id: int = 2468,
    cdb_process_id: int = 1234,
    cleanup_cdb_process_id: int | None = 1234,
) -> dict[str, object]:
    cleanup: dict[str, object] = {"status": cleanup_status}
    if cleanup_cdb_process_id is not None:
        cleanup["cdbProcessId"] = cleanup_cdb_process_id
    return {
        "schemaVersion": "winui-safe-copy-live-runtime-smoke.v1",
        "launch": {"processId": launch_process_id},
        "cdbObserver": {
            "enabled": True,
            "result": {"status": "attached", "targetProcessId": target_process_id, "cdbProcessId": cdb_process_id},
            "cleanup": cleanup,
        },
    }


class MusicAudibleOutputLiveBundleExecutorTests(unittest.TestCase):
    def test_live_smoke_commands_are_role_specific_and_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_root = root / "source"
            source_root.mkdir()
            layout = live_bundle.build_layout(root / "bundle")

            clean = live_bundle.live_smoke_command(layout, "cleanBaseline", source_root=source_root)
            staged = live_bundle.live_smoke_command(layout, "stagedPositive", source_root=source_root)
            mute = live_bundle.live_smoke_command(layout, "muteControl", source_root=source_root)

            clean_text = " ".join(clean)
            staged_text = " ".join(staged)
            mute_text = " ".join(mute)
            self.assertIn("--enable-cdb-observer", clean)
            self.assertIn("--enable-cdb-observer", staged)
            self.assertNotIn("--enable-cdb-observer", mute)
            self.assertIn("--cdb-attach-phase", clean)
            self.assertIn("--cdb-attach-phase", staged)
            self.assertNotIn("--cdb-attach-phase", mute)
            self.assertIn("--stage-music-replacement", staged)
            self.assertIn("--music-swap-preset-id use-bea02-for-bea04", staged_text)
            self.assertIn("--launch-nomusic", mute)
            self.assertIn("ALLOW EXTERNAL LIVE SMOKE ARTIFACT ROOT", clean_text)
            self.assertIn("ATTACH CDB TO SAFE COPY BEA", clean_text)
            self.assertNotIn("--stage-music-replacement", clean)
            self.assertNotIn("--launch-nomusic", clean)
            self.assertNotIn("--launch-nosound", clean)
            self.assertNotIn("--launch-nosound", staged)
            self.assertIn(str(source_root), clean_text)
            self.assertIn(str(layout.stage("cleanBaseline").live_root), clean_text)

            def option_value(command: list[str], option: str) -> str:
                return command[command.index(option) + 1]

            self.assertEqual("0", option_value(clean, "--post-window-delay-seconds"))
            self.assertEqual("0", option_value(staged, "--post-window-delay-seconds"))
            self.assertEqual("2", option_value(mute, "--post-window-delay-seconds"))
            self.assertEqual("after-launch", option_value(clean, "--cdb-attach-phase"))
            self.assertEqual("after-launch", option_value(staged, "--cdb-attach-phase"))

    def test_child_environment_is_sanitized_for_live_tools(self) -> None:
        sentinel_key = "ONSLAUGHT_TEST_SECRET_TOKEN"
        previous = os.environ.get(sentinel_key)
        os.environ[sentinel_key] = "must-not-leak"
        try:
            child_env = live_bundle.sanitized_child_env()
        finally:
            if previous is None:
                os.environ.pop(sentinel_key, None)
            else:
                os.environ[sentinel_key] = previous

        self.assertNotIn(sentinel_key, child_env)
        self.assertEqual(child_env["DOTNET_CLI_TELEMETRY_OPTOUT"], "1")
        self.assertEqual(child_env["PYTHONIOENCODING"], "utf-8")
        self.assertIn("PATH", child_env)

    def test_child_environment_preserves_windows_loader_keys_case_insensitively(self) -> None:
        child_env = live_bundle.sanitized_child_env()
        lower_keys = {key.lower(): key for key in child_env}

        self.assertIn("systemroot", lower_keys)
        self.assertIn("comspec", lower_keys)
        self.assertTrue(child_env[lower_keys["systemroot"]])
        self.assertTrue(child_env[lower_keys["comspec"]])

    def test_ambient_census_window_includes_audio_startup_margin(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = live_bundle.build_layout(Path(temp_dir) / "bundle")
            observed: dict[str, int] = {}

            def fake_ambient_census_command(stage: live_bundle.StagePaths, *, observe_ms: int) -> list[str]:
                observed["observe_ms"] = observe_ms
                return ["py", "-3", "fake-census.py"]

            with (
                mock.patch.object(live_bundle, "ambient_census_command", side_effect=fake_ambient_census_command),
                mock.patch.object(live_bundle, "start_command", return_value=(object(), object(), object())),
                mock.patch.object(live_bundle, "run_command"),
                mock.patch.object(live_bundle, "wait_process"),
                mock.patch.object(live_bundle.time, "sleep"),
            ):
                live_bundle.run_ambient_stage(
                    layout,
                    source_root=Path(temp_dir) / "source",
                    audio_duration_ms=30000,
                    log_root=Path(temp_dir) / "logs",
                )

            self.assertGreaterEqual(
                observed["observe_ms"],
                30000 + EXPECTED_AUDIO_CAPTURE_STARTUP_MARGIN_MS,
            )

    def test_live_audio_stage_waits_for_audio_startup_margin_before_launch(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = live_bundle.build_layout(Path(temp_dir) / "bundle")
            calls: list[str] = []

            def fake_start_command(*args: object, **kwargs: object) -> tuple[object, object, object]:
                calls.append("start-audio")
                return object(), object(), object()

            def fake_run_command(command: list[str], *args: object, label: str, **kwargs: object) -> subprocess.CompletedProcess[str]:
                calls.append(label)
                return subprocess.CompletedProcess(command, 0, "{}", "")

            def fake_sleep(seconds: float) -> None:
                calls.append(f"sleep:{seconds}")

            with (
                mock.patch.object(live_bundle, "start_command", side_effect=fake_start_command),
                mock.patch.object(live_bundle, "run_command", side_effect=fake_run_command),
                mock.patch.object(live_bundle, "wait_process"),
                mock.patch.object(live_bundle, "validate_live_stage_cdb_cleanup"),
                mock.patch.object(live_bundle, "ensure_no_bea_or_cdb_processes"),
                mock.patch.object(live_bundle, "CdbLogTailer"),
                mock.patch.object(live_bundle.time, "sleep", side_effect=fake_sleep),
            ):
                live_bundle.run_live_audio_stage(
                    layout,
                    "stagedPositive",
                    source_root=Path(temp_dir) / "source",
                    audio_duration_ms=30000,
                    live_timeout_seconds=24,
                    log_root=Path(temp_dir) / "logs",
                )

            self.assertEqual(calls[0], "start-audio")
            self.assertEqual(calls[1], f"sleep:{EXPECTED_AUDIO_CAPTURE_STARTUP_MARGIN_MS / 1000.0}")
            self.assertEqual(calls[2], "stagedPositive-live")

    def test_timestamp_ledger_from_observed_log_feeds_timestamp_producer(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            raw_log = root / "clean" / "windbg.log"
            raw_log.parent.mkdir()
            raw_log.write_text(materializer_fixtures.untimestamped_log_text(), encoding="utf-8")
            observed_at = dt.datetime(2026, 6, 24, 12, 0, 0, tzinfo=dt.timezone.utc)

            ledger_path = root / "clean" / "timestamp-observations.json"
            live_bundle.write_observation_ledger(
                raw_cdb_log=raw_log,
                output=ledger_path,
                role="cleanBaseline",
                observed_at_start=observed_at,
            )

            timestamped_log = root / "out" / "clean" / "windbg.timestamped.log"
            receipt = root / "out" / "clean" / "timestamped-cdb-log-receipt.json"
            payload = timestamp_producer.build_timestamped_log_from_paths(
                raw_cdb_log=raw_log,
                observation_ledger=ledger_path,
                timestamped_log_output=timestamped_log,
                receipt_output=receipt,
                allowed_output_root=root / "out",
                role="cleanBaseline",
            )

            self.assertTrue(payload["cdbLogTimestamped"])
            self.assertEqual(payload["timestampedLineCount"], len(raw_log.read_text(encoding="utf-8").splitlines()))
            ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
            self.assertEqual(ledger["timestampSource"], "trusted-tail-wrapper-observation-ledger")
            self.assertEqual(ledger["role"], "cleanBaseline")

    def test_materializer_command_uses_all_private_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            layout = live_bundle.build_layout(Path(temp_dir) / "bundle")
            command = live_bundle.materializer_command(layout)
            joined = " ".join(command)
            for token in (
                "--clean-live",
                "--staged-live",
                "--mute-live",
                "--clean-timeline",
                "--staged-timeline",
                "--clean-source-music-safety",
                "--mute-source-music-safety",
                "--ambient-census",
                "--ambient-audio",
                "--clean-audio",
                "--staged-audio",
                "--mute-audio",
                "--capture-source-correlation",
                "--output",
            ):
                self.assertIn(token, command)
            self.assertIn(str(layout.final_proof), joined)

    def test_unsafe_cdb_cleanup_status_is_rejected_before_materialization(self) -> None:
        for status in ("still-running", "failed", "not-started"):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as temp_dir:
                stage = live_bundle.StagePaths(role="cleanBaseline", root=Path(temp_dir) / "clean")
                stage.live_root.mkdir(parents=True)
                stage.live_json.write_text(
                    json.dumps(cdb_live_payload(cleanup_status=status)),
                    encoding="utf-8",
                )

                with self.assertRaises(live_bundle.LiveBundleError) as caught:
                    live_bundle.validate_live_stage_cdb_cleanup(stage)

                self.assertIn(status, str(caught.exception))

    def test_cdb_cleanup_stopped_or_already_exited_is_accepted(self) -> None:
        for status in ("stopped", "already-exited"):
            with self.subTest(status=status), tempfile.TemporaryDirectory() as temp_dir:
                stage = live_bundle.StagePaths(role="stagedPositive", root=Path(temp_dir) / "staged")
                stage.live_root.mkdir(parents=True)
                stage.live_json.write_text(
                    json.dumps(cdb_live_payload(cleanup_status=status)),
                    encoding="utf-8",
                )

                live_bundle.validate_live_stage_cdb_cleanup(stage)

    def test_cdb_cleanup_requires_matching_positive_cdb_process_id(self) -> None:
        cases = (
            ({"status": "attached"}, {"status": "stopped"}),
            ({"status": "attached", "cdbProcessId": 0}, {"status": "stopped", "cdbProcessId": 0}),
            ({"status": "attached", "cdbProcessId": 1234}, {"status": "stopped", "cdbProcessId": 5678}),
        )
        for result, cleanup in cases:
            with self.subTest(result=result, cleanup=cleanup), tempfile.TemporaryDirectory() as temp_dir:
                stage = live_bundle.StagePaths(role="cleanBaseline", root=Path(temp_dir) / "clean")
                stage.live_root.mkdir(parents=True)
                payload = cdb_live_payload()
                payload["cdbObserver"]["result"] = result
                payload["cdbObserver"]["cleanup"] = cleanup
                stage.live_json.write_text(json.dumps(payload), encoding="utf-8")

                with self.assertRaises(live_bundle.LiveBundleError):
                    live_bundle.validate_live_stage_cdb_cleanup(stage)

    def test_cdb_cleanup_requires_live_target_pid_to_match_launched_safe_copy_pid(self) -> None:
        cases = (
            cdb_live_payload(launch_process_id=0, target_process_id=2468),
            cdb_live_payload(launch_process_id=2468, target_process_id=0),
            cdb_live_payload(launch_process_id=2468, target_process_id=1357),
            cdb_live_payload(launch_process_id=2468, target_process_id=2468, cleanup_cdb_process_id=None),
        )
        for payload in cases:
            with self.subTest(payload=payload), tempfile.TemporaryDirectory() as temp_dir:
                stage = live_bundle.StagePaths(role="cleanBaseline", root=Path(temp_dir) / "clean")
                stage.live_root.mkdir(parents=True)
                stage.live_json.write_text(json.dumps(payload), encoding="utf-8")

                with self.assertRaises(live_bundle.LiveBundleError):
                    live_bundle.validate_live_stage_cdb_cleanup(stage)

    def test_live_stage_checks_process_census_before_timestamping_after_cdb_cleanup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_root = root / "source"
            source_root.mkdir()
            layout = live_bundle.build_layout(root / "bundle")
            stage = layout.stage("cleanBaseline")
            events: list[str] = []

            class FakeTailer:
                def start(self) -> None:
                    events.append("tail-start")

                def stop_and_write(self, output: Path) -> dict[str, object]:
                    events.append("tail-stop")
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_text("{}", encoding="utf-8")
                    return {}

            def fake_run_command(command: list[str], *, log_root: Path, label: str, timeout_seconds: int | None = None) -> subprocess.CompletedProcess[str]:
                events.append(label)
                if label == "cleanBaseline-live":
                    stage.live_root.mkdir(parents=True, exist_ok=True)
                    stage.live_json.write_text(json.dumps(cdb_live_payload()), encoding="utf-8")
                return subprocess.CompletedProcess(command, 0, "{}", "")

            with (
                mock.patch.object(live_bundle, "start_command", return_value=(object(), object(), object())),
                mock.patch.object(live_bundle, "wait_process"),
                mock.patch.object(live_bundle, "CdbLogTailer", return_value=FakeTailer()),
                mock.patch.object(live_bundle, "run_command", side_effect=fake_run_command),
                mock.patch.object(live_bundle, "ensure_no_bea_or_cdb_processes", side_effect=lambda: events.append("process-census")),
            ):
                live_bundle.run_live_audio_stage(
                    layout,
                    "cleanBaseline",
                    source_root=source_root,
                    audio_duration_ms=5000,
                    live_timeout_seconds=5,
                    log_root=root / "logs",
                )

            self.assertLess(events.index("cleanBaseline-live"), events.index("process-census"))
            self.assertLess(events.index("process-census"), events.index("cleanBaseline-timestamped-cdb"))

    def test_live_stage_waits_for_audio_process_when_cdb_tailer_stop_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_root = root / "source"
            source_root.mkdir()
            layout = live_bundle.build_layout(root / "bundle")
            events: list[str] = []

            class FailingTailer:
                def start(self) -> None:
                    events.append("tail-start")

                def stop_and_write(self, output: Path) -> dict[str, object]:
                    events.append("tail-stop")
                    raise live_bundle.LiveBundleError("tailer failed")

            with (
                mock.patch.object(live_bundle, "start_command", return_value=(object(), object(), object())),
                mock.patch.object(live_bundle, "wait_process", side_effect=lambda *args, **kwargs: events.append("audio-wait")),
                mock.patch.object(live_bundle, "CdbLogTailer", return_value=FailingTailer()),
                mock.patch.object(live_bundle, "run_command", return_value=subprocess.CompletedProcess([], 0, "{}", "")),
            ):
                with self.assertRaises(live_bundle.LiveBundleError):
                    live_bundle.run_live_audio_stage(
                        layout,
                        "cleanBaseline",
                        source_root=source_root,
                        audio_duration_ms=5000,
                        live_timeout_seconds=5,
                        log_root=root / "logs",
                    )

            self.assertIn("tail-stop", events)
            self.assertIn("audio-wait", events)

    def test_run_live_bundle_checks_no_bea_or_cdb_before_and_after_success(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_root = root / "source"
            source_root.mkdir()
            layout = live_bundle.build_layout(root / "bundle")
            process_checks: list[str] = []

            def record_process_check() -> None:
                process_checks.append("checked")

            with (
                mock.patch.object(live_bundle, "ensure_no_bea_or_cdb_processes", side_effect=record_process_check),
                mock.patch.object(live_bundle, "run_ambient_stage"),
                mock.patch.object(live_bundle, "run_live_audio_stage"),
                mock.patch.object(live_bundle, "materialize_attempt", return_value={"runtimeAudibleOutputProof": True}),
            ):
                receipt = live_bundle.run_live_bundle(
                    layout=layout,
                    source_root=source_root,
                    audio_duration_ms=5000,
                    live_timeout_seconds=5,
                )

            self.assertEqual(receipt["status"], "accepted")
            self.assertEqual(process_checks, ["checked", "checked"])

    def test_run_live_bundle_records_final_process_check_error_after_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_root = root / "source"
            source_root.mkdir()
            layout = live_bundle.build_layout(root / "bundle")
            process_checks: list[str] = []

            def process_check() -> None:
                process_checks.append("checked")
                if len(process_checks) == 2:
                    raise live_bundle.LiveBundleError("Refusing live bundle attempt while BEA/CDB processes exist: C:\\secret\\BEA.exe")

            with (
                mock.patch.object(live_bundle, "ensure_no_bea_or_cdb_processes", side_effect=process_check),
                mock.patch.object(live_bundle, "run_ambient_stage"),
                mock.patch.object(live_bundle, "run_live_audio_stage"),
                mock.patch.object(live_bundle, "materialize_attempt", side_effect=live_bundle.LiveBundleError("materializer failed")),
            ):
                with self.assertRaises(live_bundle.LiveBundleError):
                    live_bundle.run_live_bundle(
                        layout=layout,
                        source_root=source_root,
                        audio_duration_ms=5000,
                        live_timeout_seconds=5,
                    )

            receipt = json.loads(layout.receipt.read_text(encoding="utf-8"))
            self.assertEqual(receipt["status"], "failed")
            self.assertEqual(receipt["error"], "materializer failed")
            self.assertIn("finalProcessCheckError", receipt)
            self.assertNotIn("C:\\secret", receipt["finalProcessCheckError"])

    def test_run_live_bundle_checks_no_bea_or_cdb_after_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_root = root / "source"
            source_root.mkdir()
            layout = live_bundle.build_layout(root / "bundle")
            process_checks: list[str] = []

            def record_process_check() -> None:
                process_checks.append("checked")

            with (
                mock.patch.object(live_bundle, "ensure_no_bea_or_cdb_processes", side_effect=record_process_check),
                mock.patch.object(live_bundle, "run_ambient_stage"),
                mock.patch.object(live_bundle, "run_live_audio_stage"),
                mock.patch.object(live_bundle, "materialize_attempt", side_effect=live_bundle.LiveBundleError("materializer failed")),
            ):
                with self.assertRaises(live_bundle.LiveBundleError):
                    live_bundle.run_live_bundle(
                        layout=layout,
                        source_root=source_root,
                        audio_duration_ms=5000,
                        live_timeout_seconds=5,
                    )

            self.assertEqual(process_checks, ["checked", "checked"])

    def test_self_test_passes_without_live_processes(self) -> None:
        live_bundle.self_test()


if __name__ == "__main__":
    unittest.main()
