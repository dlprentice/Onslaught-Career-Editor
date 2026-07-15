#!/usr/bin/env python3
"""Synthetic tests for the receipt-bound walker trajectory measurement adapter."""

from __future__ import annotations

import hashlib
import importlib.util
import inspect
import json
import stat
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


TOOLS = Path(__file__).resolve().parent
MODULE_PATH = TOOLS / "run_battleengine_walker_trajectory_measurement.py"


def load_module():
    spec = importlib.util.spec_from_file_location("walker_measurement", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class FakeNative:
    def __init__(self, snapshot):
        self.snapshot = snapshot
        self.open_access = None
        self.closed = False
        self.read_result = b"ABCD"
        self.send_results = [1, 1]
        self.foreground = snapshot.window_handle

    def open_process(self, pid, access):
        self.open_access = access
        return 99

    def close_handle(self, handle):
        self.closed = True

    def read_process_memory(self, handle, address, size):
        return self.read_result[:size]

    def current_identity(self, handle, expected):
        return self.snapshot

    def foreground_window(self):
        return self.foreground

    def force_foreground(self, hwnd):
        self.foreground = hwnd
        return True

    def send_scan_code(self, scan_code, key_up):
        return self.send_results.pop(0)


class FakeClock:
    frequency = 10_000_000

    def __init__(self):
        self.tick = 0

    def now(self):
        value = self.tick
        self.tick += 1
        return value

    def wait_until(self, target):
        self.tick = max(self.tick, target)
        return self.tick


class MeasurementTests(unittest.TestCase):
    def setUp(self):
        self.m = load_module()

    def receipt(self, root: Path):
        exe = root / "profile" / "BEA.exe"
        manifest = root / "profile" / "profile-manifest.json"
        exe.parent.mkdir(parents=True)
        exe.write_bytes(b"copied-bea")
        manifest.write_text("{}", encoding="utf-8")
        payload = {
            "schemaVersion": "runtime-process-receipt.v1",
            "runId": "aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee",
            "process": {
                "id": 4242,
                "startedAtUtc": "2026-07-13T12:00:00.0000000Z",
                "executable": {
                    "path": str(exe.resolve()),
                    "sha256": hashlib.sha256(exe.read_bytes()).hexdigest(),
                    "size": exe.stat().st_size,
                },
                "workingDirectory": str(exe.parent.resolve()),
                "launchArguments": ["-skipfmv", "-level", "850", "-configuration", "2"],
            },
            "profileManifest": {
                "path": str(manifest.resolve()),
                "sha256": hashlib.sha256(manifest.read_bytes()).hexdigest(),
                "size": manifest.stat().st_size,
            },
            "window": {"hwndHex": "0x1234"},
            "module": {
                "path": str(exe.resolve()),
                "baseAddressHex": "0x10000000",
                "size": 0x260000,
            },
            "sourceExecutableSha256": hashlib.sha256(exe.read_bytes()).hexdigest(),
            "copiedExecutableSha256": hashlib.sha256(exe.read_bytes()).hexdigest(),
            "commandTemplateSha256": "0" * 64,
            "generatedCommandSha256": "0" * 64,
        }
        path = root / "runtime-process-receipt.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return path, digest

    def test_receipt_parsing_is_exact_and_module_base_drives_sampler(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, digest = self.receipt(Path(tmp))
            value = self.m.load_receipt(path, digest)
        self.assertEqual(0x10000000, value.module_base)
        self.assertEqual(("-skipfmv", "-level", "850", "-configuration", "2"), value.launch_arguments)
        self.assertEqual(value.process_id, value.window_process_id)

    def test_frozen_deadline_algebra_and_full_attempt_refusal(self):
        self.assertEqual(600, self.m.AGGREGATE_DEADLINE_SECONDS)
        self.assertEqual(150, self.m.PREBUILD_SAFETY_BOUND_SECONDS)
        self.assertEqual(215, self.m.COMPLETE_ATTEMPT_BUDGET_SECONDS)
        self.assertEqual(20, self.m.CLEANUP_RESERVE_SECONDS)
        self.assertEqual(580, self.m.DECLARED_MAXIMUM_SECONDS)
        with self.assertRaisesRegex(self.m.AttemptDeadlineExceeded, "full 215-second"):
            self.m.require_full_attempt_budget(214.999, attempt=2)

    def test_readiness_requires_three_consecutive_valid_polls_and_resets(self):
        ready = self.m.sampler.ReadinessProbe(850, 2, 1, self.m.sampler.WALKER_STATE_RAW,
                                               self.m.sampler.NEUTRAL_CONTROL_RAW)
        sequence = iter((
            ready,
            self.m.sampler.RuntimeNotReady(hop="p1"),
            ready,
            self.m.sampler.RuntimeNotReady(field="horizontalSplit"),
            ready, ready, ready,
        ))
        polls = []
        def probe():
            value = next(sequence)
            polls.append(value)
            if isinstance(value, BaseException):
                raise value
            return value
        guard = SimpleNamespace(
            revalidate_receipt=lambda: True, foreground_matches=lambda: True
        )
        result = self.m.wait_for_runtime_readiness(
            probe, guard, deadline_check=lambda: None, sleep=lambda _seconds: None
        )
        self.assertEqual(7, len(polls))
        self.assertEqual(3, result["consecutiveValidPolls"])
        self.assertEqual(1, result["horizontalSplit"])
        self.assertNotIn("path", json.dumps(result).lower())
        self.assertNotIn("0x", json.dumps(result))

    def test_not_ready_poll_is_revalidated_after_probe_before_retry(self):
        checks = []
        guard = SimpleNamespace(
            revalidate_receipt=lambda: checks.append("receipt") or len(checks) < 2,
            foreground_matches=lambda: checks.append("foreground") or True,
        )
        with self.assertRaisesRegex(self.m.sampler.AttemptError, "receipt or foreground"):
            self.m.wait_for_runtime_readiness(
                lambda: (_ for _ in ()).throw(self.m.sampler.RuntimeNotReady(hop="p0")),
                guard, deadline_check=lambda: None, sleep=lambda _seconds: None,
            )
        self.assertEqual(["receipt", "foreground", "receipt"], checks)

    def test_readiness_expiry_one_poll_short_and_fatal_defects(self):
        ready = self.m.sampler.ReadinessProbe(850, 2, 1, self.m.sampler.WALKER_STATE_RAW,
                                               self.m.sampler.NEUTRAL_CONTROL_RAW)
        with self.assertRaisesRegex(self.m.AttemptDeadlineExceeded, "readiness"):
            self.m.wait_for_runtime_readiness(
                lambda: ready,
                SimpleNamespace(revalidate_receipt=lambda: True, foreground_matches=lambda: True),
                deadline_check=lambda: None,
                sleep=lambda _seconds: None,
                max_polls=2,
            )
        with self.assertRaisesRegex(
            self.m.AttemptDeadlineExceeded, "last nullHop=p0"
        ):
            self.m.wait_for_runtime_readiness(
                lambda: (_ for _ in ()).throw(self.m.sampler.RuntimeNotReady(hop="p0")),
                SimpleNamespace(revalidate_receipt=lambda: True, foreground_matches=lambda: True),
                deadline_check=lambda: None, sleep=lambda _seconds: None, max_polls=1,
            )
        for defect in (
            self.m.sampler.SampleError("short read"),
            self.m.sampler.SampleError("torn runtime sample"),
        ):
            with self.subTest(defect=str(defect)), self.assertRaises(type(defect)):
                self.m.wait_for_runtime_readiness(
                    lambda d=defect: (_ for _ in ()).throw(d),
                    SimpleNamespace(revalidate_receipt=lambda: True, foreground_matches=lambda: True),
                    deadline_check=lambda: None, sleep=lambda _seconds: None,
                )

    def test_no_q_down_before_readiness(self):
        source = inspect.getsource(self.m.collect_trace)
        self.assertLess(source.index("wait_for_runtime_readiness("), source.index("origin = clock.now()"))

    def test_receipt_byte_drift_and_stale_output_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, digest = self.receipt(root)
            path.write_text(path.read_text(encoding="utf-8") + " ", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "receipt SHA-256"):
                self.m.load_receipt(path, digest)
            stale = root / "walker-trajectory-raw.json"
            stale.write_text("{}", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "already exists"):
                self.m.require_absent_outputs([stale])

    def test_observer_opens_only_query_limited_and_vm_read(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, digest = self.receipt(Path(tmp))
            receipt = self.m.load_receipt(path, digest)
            native = FakeNative(receipt)
            reader = self.m.ReceiptPinnedReader(receipt, native)
            reader.open()
            reader.close()
        self.assertEqual(
            self.m.PROCESS_QUERY_LIMITED_INFORMATION | self.m.PROCESS_VM_READ,
            native.open_access,
        )
        self.assertEqual(0, native.open_access & self.m.FORBIDDEN_PROCESS_RIGHTS)
        self.assertTrue(native.closed)

    def test_rpm_short_read_and_closed_handle_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, digest = self.receipt(Path(tmp))
            receipt = self.m.load_receipt(path, digest)
            native = FakeNative(receipt)
            reader = self.m.ReceiptPinnedReader(receipt, native)
            with self.assertRaisesRegex(RuntimeError, "not open"):
                reader.read(receipt.module_base, 4)
            reader.open()
            native.read_result = b"X"
            with self.assertRaisesRegex(RuntimeError, "short ReadProcessMemory"):
                reader.read(receipt.module_base, 4)

    def test_guard_detects_identity_and_foreground_drift_but_makes_bounded_nonclaim(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, digest = self.receipt(Path(tmp))
            receipt = self.m.load_receipt(path, digest)
            native = FakeNative(receipt)
            guard = self.m.ReceiptRuntimeGuard(receipt, path, digest, native, 99, Path(tmp))
            self.assertTrue(guard.revalidate_receipt())
            self.assertTrue(guard.foreground_matches())
            self.assertFalse(guard.interference_detected())
            self.assertIn("does not detect arbitrary human or controller input", guard.interference_nonclaim)
            native.foreground = 0x9999
            self.assertFalse(guard.foreground_matches())
            native.snapshot = self.m.sampler.replace_receipt(receipt, module_base=receipt.module_base + 0x1000)
            self.assertFalse(guard.revalidate_receipt())

    def test_guard_detects_process_creation_time_drift(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, digest = self.receipt(Path(tmp))
            receipt = self.m.load_receipt(path, digest)
            native = FakeNative(receipt)
            guard = self.m.ReceiptRuntimeGuard(receipt, path, digest, native, 99, Path(tmp))
            native.snapshot = self.m.sampler.replace_receipt(
                receipt, started_at_utc="2026-07-13T12:00:01.0000000Z"
            )
            self.assertFalse(guard.revalidate_receipt())

    def test_q_input_sends_exact_scan_code_once_each_and_confirms_finally_up(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, digest = self.receipt(Path(tmp))
            receipt = self.m.load_receipt(path, digest)
            native = FakeNative(receipt)
            value = self.m.ScanCodeQInput(native, receipt.window_handle)
            self.assertTrue(value.key_down())
            self.assertTrue(value.key_up())
            self.assertEqual([(0x10, False), (0x10, True)], value.events)
            with self.assertRaisesRegex(RuntimeError, "exactly one"):
                value.key_up()

    def test_q_up_is_attempted_after_sampling_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, digest = self.receipt(Path(tmp))
            receipt = self.m.load_receipt(path, digest)
            native = FakeNative(receipt)
            q_input = self.m.ScanCodeQInput(native, receipt.window_handle)
            guard = self.m.ReceiptRuntimeGuard(receipt, path, digest, native, 99, Path(tmp))
            with self.assertRaisesRegex(RuntimeError, "sample failed"):
                self.m.sampler.execute_owned_q_window(
                    guard, q_input, FakeClock().now,
                    [lambda: (_ for _ in ()).throw(RuntimeError("sample failed"))],
                )
            self.assertEqual([(0x10, False), (0x10, True)], q_input.events)
            self.assertTrue(q_input.up_confirmed)

    def test_deadline_overrun_during_hold_still_confirms_q_up(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, digest = self.receipt(Path(tmp))
            receipt = self.m.load_receipt(path, digest)
            native = FakeNative(receipt)
            q_input = self.m.ScanCodeQInput(native, receipt.window_handle)
            guard = self.m.ReceiptRuntimeGuard(receipt, path, digest, native, 99, Path(tmp))
            checks = iter((None, None, self.m.AttemptDeadlineExceeded("hold deadline")))
            def deadline_check():
                value = next(checks, None)
                if value:
                    raise value
            with self.assertRaisesRegex(self.m.AttemptDeadlineExceeded, "hold deadline"):
                self.m.execute_deadlined_q_batches(
                    guard, q_input, FakeClock().now,
                    [lambda: "batch-1", lambda: "batch-2"], deadline_check,
                )
            self.assertTrue(q_input.up_confirmed)
            self.assertEqual([(0x10, False), (0x10, True)], q_input.events)

    def test_mid_batch_foreground_drift_discards_window_and_confirms_q_up(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, digest = self.receipt(Path(tmp))
            receipt = self.m.load_receipt(path, digest)
            native = FakeNative(receipt)
            q_input = self.m.ScanCodeQInput(native, receipt.window_handle)
            guard = self.m.ReceiptRuntimeGuard(receipt, path, digest, native, 99, Path(tmp))
            def contaminated_batch():
                native.foreground = 0x9999
                return "must-not-be-promoted"
            with self.assertRaisesRegex(self.m.sampler.AttemptError, "foreground"):
                self.m.execute_deadlined_q_batches(
                    guard, q_input, FakeClock().now, [contaminated_batch], lambda: None
                )
            self.assertTrue(q_input.up_confirmed)
            self.assertEqual([(0x10, False), (0x10, True)], q_input.events)

    def test_lexical_reparse_route_is_rejected_before_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real = root / "real"
            real.mkdir()
            link = root / "link"
            try:
                link.symlink_to(real, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")
            path, digest = self.receipt(link)
            with self.assertRaisesRegex(ValueError, "reparse"):
                self.m.load_receipt(path, digest, authorized_private_root=root)

    def test_live_observer_cli_rejects_reparse_routed_paths_before_native_backend(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            authorized = root / "authorized"
            authorized.mkdir()
            real = authorized / "real"
            real.mkdir()
            link = authorized / "evidence"
            try:
                link.symlink_to(real, target_is_directory=True)
            except OSError as exc:
                self.skipTest(f"symlink creation unavailable: {exc}")
            receipt, digest = self.receipt(link)
            args = self.m.build_parser().parse_args([
                "observe-one", "--attempt", "1", "--receipt", str(receipt),
                "--expected-receipt-sha256", digest,
                "--raw-output", str(link / "walker-trajectory-raw.json"),
                "--metrics-output", str(link / "walker-trajectory-metrics.json"),
                "--status-output", str(link / "observer-status.json"),
                "--authorized-private-root", str(authorized),
            ])
            with self.assertRaisesRegex(ValueError, "reparse"):
                self.m.run_observer(args)

    def test_junction_reparse_attribute_is_detected_without_following(self):
        target = Path("C:/private/junction")
        original = self.m.os.lstat
        def fake_lstat(path):
            if Path(path) == target:
                return SimpleNamespace(st_file_attributes=0x400, st_mode=stat.S_IFDIR)
            return original(path)
        with patch.object(self.m.os, "lstat", side_effect=fake_lstat):
            self.assertTrue(self.m._path_is_reparse(target))

    def test_integrated_sampler_acceptance_is_private_and_provisional_until_cleanup(self):
        trace = self.m.sampler.synthetic_attempt_trace(attempt=1)
        trace.integrity.cleanup_confirmed = False
        metrics = self.m.analyze_provisional_trace(trace)
        self.assertTrue(metrics.accepted)
        payload = self.m._metrics_payload(metrics)
        self.assertEqual("battleengine-walker-trajectory-private-metrics.v1", payload["schemaVersion"])
        self.assertEqual(
            "CWalker::Forward -> CWalker::Move scalar response",
            payload["calibrationTarget"]["sourceNamedPath"],
        )
        self.assertIn("First Flight parity", payload["calibrationTarget"]["nonclaim"])
        self.assertFalse(payload["publicProjectionWritten"])
        trace.samples["baseline"][-1] = self.m.sampler.replace_sample(
            trace.samples["baseline"][-1], position=(100.0, 0.0, 0.0)
        )
        with self.assertRaises(self.m.sampler.AttemptError):
            self.m.analyze_provisional_trace(trace)

    def test_energy_measure_analyzes_jet_hold_drain(self):
        trace = self.m.sampler.synthetic_attempt_trace(
            attempt=1, vehicle=self.m.sampler.VEHICLE_JET
        )
        metrics = self.m.analyze_provisional_trace(
            trace,
            measure=self.m.sampler.MEASURE_ENERGY,
            vehicle=self.m.sampler.VEHICLE_JET,
        )
        self.assertTrue(metrics.accepted)
        self.assertLess(metrics.steady_rate_per_sec, 0.0)
        payload = self.m._metrics_payload(
            metrics, measure=self.m.sampler.MEASURE_ENERGY
        )
        self.assertEqual(
            "battleengine-energy-rate-private-metrics.v1", payload["schemaVersion"]
        )
        self.assertEqual(self.m.sampler.MEASURE_ENERGY, payload["measure"])

    def test_energy_measure_requires_jet_vehicle(self):
        with self.assertRaisesRegex(ValueError, "requires jet"):
            self.m.validate_measure_vehicle(
                self.m.sampler.MEASURE_ENERGY, self.m.sampler.VEHICLE_WALKER
            )
        self.m.validate_measure_vehicle(
            self.m.sampler.MEASURE_ENERGY, self.m.sampler.VEHICLE_JET
        )

    def test_turn_and_strafe_require_walker_vehicle(self):
        with self.assertRaisesRegex(ValueError, "requires walker"):
            self.m.validate_measure_vehicle(
                self.m.sampler.MEASURE_TURN, self.m.sampler.VEHICLE_JET
            )
        with self.assertRaisesRegex(ValueError, "requires walker"):
            self.m.validate_measure_vehicle(
                self.m.sampler.MEASURE_STRAFE, self.m.sampler.VEHICLE_JET
            )
        self.m.validate_measure_vehicle(
            self.m.sampler.MEASURE_TURN, self.m.sampler.VEHICLE_WALKER
        )
        self.m.validate_measure_vehicle(
            self.m.sampler.MEASURE_STRAFE, self.m.sampler.VEHICLE_WALKER
        )

    def test_forward_and_transform_accept_current_vehicles(self):
        self.m.validate_measure_vehicle(
            self.m.sampler.MEASURE_FORWARD, self.m.sampler.VEHICLE_WALKER
        )
        self.m.validate_measure_vehicle(
            self.m.sampler.MEASURE_FORWARD, self.m.sampler.VEHICLE_JET
        )
        self.m.validate_measure_vehicle(
            self.m.sampler.MEASURE_TRANSFORM, self.m.sampler.VEHICLE_WALKER
        )

    def test_source_has_no_outer_hard_timeout_for_lifecycle_owner(self):
        source = self.m.MODULE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("timeout=ATTEMPT_DEADLINE_SECONDS", source)
        invoke_source = inspect.getsource(self.m._invoke_smoke)
        monitor_source = inspect.getsource(self.m._communicate_with_phase_deadlines)
        self.assertIn("subprocess.Popen", invoke_source)
        self.assertIn("_communicate_with_phase_deadlines", invoke_source)
        self.assertIn("_write_cooperative_stop_request", monitor_source)
        self.assertIn("COMPLETE_ATTEMPT_BUDGET_SECONDS", monitor_source)
        self.assertIn("PROFILE_PREPARATION_BOUND_SECONDS", monitor_source)
        self.assertIn("LAUNCH_RECEIPT_FOCUS_BOUND_SECONDS", monitor_source)
        self.assertNotIn("PROFILE_PREPARATION_BUDGET_SECONDS", source)
        self.assertNotIn("LAUNCH_IDENTITY_BUDGET_SECONDS", source)
        self.assertEqual(120, self.m.PROFILE_PREPARATION_BOUND_SECONDS)
        self.assertEqual(30, self.m.LAUNCH_RECEIPT_FOCUS_BOUND_SECONDS)
        self.assertNotIn(".kill(", invoke_source)
        self.assertNotIn(".terminate(", invoke_source)
        for option in (
            "--walker-prebuilt-runner-dll",
            "--expected-walker-prebuilt-runner-sha256",
            "--walker-prebuild-receipt",
            "--expected-walker-prebuild-receipt-sha256",
        ):
            self.assertIn(option, invoke_source)

    def test_outer_monitor_signals_in_progress_profile_launch_and_fixed_attempt_bounds(self):
        class BlockingProcess:
            def __init__(self, module, clock, increment, stop_path):
                self.module = module
                self.clock = clock
                self.increment = increment
                self.stop_path = stop_path

            def communicate(self, timeout):
                if self.stop_path.is_file():
                    return "closed-out", ""
                self.clock[0] += self.increment
                raise self.module.subprocess.TimeoutExpired(["synthetic"], timeout)

        cases = (
            ("profile", self.m.PROFILE_PREPARATION_BOUND_SECONDS),
            ("launch", self.m.LAUNCH_RECEIPT_FOCUS_BOUND_SECONDS),
            ("attempt", self.m.COMPLETE_ATTEMPT_BUDGET_SECONDS),
        )
        for phase, limit in cases:
            with self.subTest(phase=phase), tempfile.TemporaryDirectory() as tmp:
                evidence = Path(tmp)
                if phase != "attempt":
                    (evidence / f"walker-phase-{phase}-started.marker").write_text(
                        "started", encoding="ascii"
                    )
                stop_path = evidence / "stop.request"
                clock = [0.0]
                process = BlockingProcess(self.m, clock, float(limit), stop_path)
                stdout, stderr, reason = self.m._communicate_with_phase_deadlines(
                    process, evidence, stop_path,
                    aggregate_remaining_seconds=500.0,
                    monotonic=lambda: clock[0],
                )
                self.assertEqual(("closed-out", ""), (stdout, stderr))
                self.assertIsNotNone(reason)
                self.assertIn(phase, reason)
                self.assertEqual(reason + "\n", stop_path.read_text(encoding="ascii"))

    def test_win32_backend_declares_pointer_safe_signatures_without_remote_dereference(self):
        source = self.m.MODULE_PATH.read_text(encoding="utf-8")
        for function in (
            "OpenProcess", "ReadProcessMemory", "CreateToolhelp32Snapshot",
            "Module32FirstW", "QueryFullProcessImageNameW", "GetProcessTimes",
            "GetWindowThreadProcessId", "SendInput", "NtQueryInformationProcess",
        ):
            self.assertIn(f"{function}.argtypes", source)
        self.assertNotIn("row.modBaseAddr.contents", source)

    def closeout(self, root: Path, attempt: int, *, accepted=True, zero=True, q_up=True,
                 handle=True, stopped=True, source=True, copy=True):
        receipt = root / f"attempt-{attempt:02d}" / "evidence" / "runtime-process-receipt.json"
        receipt.parent.mkdir(parents=True)
        receipt.write_text(f"receipt-{attempt}", encoding="utf-8")
        base = attempt * 100
        return {
            "attempt": attempt,
            "accepted": accepted,
            "receiptPath": str(receipt),
            "receiptSha256": hashlib.sha256(receipt.read_bytes()).hexdigest(),
            "qUpConfirmed": q_up,
            "observerHandleClosed": handle,
            "managedProcessStopped": stopped,
            "ownedProcessCount": 0 if zero else 1,
            "sourceUnchanged": source,
            "copyUnchanged": copy,
            "publicProjectionWritten": False,
            "phaseTimestamps": {
                name: base + index + 1 for index, name in enumerate((
                    "profilePreparationStartedTimestamp", "profilePreparationCompletedTimestamp",
                    "launchStartedTimestamp", "receiptValidatedTimestamp", "focusAcquiredTimestamp",
                    "adapterStartedTimestamp", "cleanupStartedTimestamp", "closeoutWrittenTimestamp",
                ))
            },
            "cleanup": {"observerQUp": q_up, "backupQUp": False,
                        "phaseJobsClosed": True},
        }

    def prebuild_receipt(self, root: Path):
        runner = root / "runner"
        runner.mkdir(parents=True)
        files = {
            "sourcePath": runner / "Program.cs",
            "projectPath": runner / "LiveSafeCopySmoke.csproj",
            "dllPath": runner / "LiveSafeCopySmoke.dll",
            "runtimeConfigPath": runner / "LiveSafeCopySmoke.runtimeconfig.json",
            "depsPath": runner / "LiveSafeCopySmoke.deps.json",
        }
        for key, path in files.items():
            path.write_text(key, encoding="utf-8")
        receipt_path = root / "runner-build-receipt.json"
        receipt_path.write_text("build-receipt", encoding="utf-8")
        row = {
            "passed": True, "exitCode": 0, "timedOut": False,
            "totalElapsedSeconds": 5.0,
            "sdkIdentity": {"hostPath": str(self.m.MODULE_PATH), "version": "10.0.0",
                            "hostSha256": hashlib.sha256(self.m.MODULE_PATH.read_bytes()).hexdigest()},
            "compilerOwnedProcessCount": 0,
            "compilerCleanup": {"cleanupConfirmed": True, "capturedDescendants": [],
                                "ownedProcessCount": 0, "residue": [],
                                "ownershipMode": "windows-job-object-before-resume",
                                "jobAssignedBeforeResume": True, "jobClosed": True,
                                "jobAccountingBeforeCleanup": {
                                    "totalProcesses": 1, "activeProcesses": 0,
                                },
                                "jobAccountingAfterCleanup": {
                                    "totalProcesses": 1, "activeProcesses": 0,
                                }},
            "buildInvocationCount": 1,
            "buildProcessId": 7001,
            "command": ["dotnet", "build", "--no-restore", "--nologo"],
            "phaseTimestampsUtc": {
                "generationStarted": "2026-07-13T00:00:00Z",
                "generationCompleted": "2026-07-13T00:00:01Z",
                "buildStarted": "2026-07-13T00:00:02Z",
                "buildCompleted": "2026-07-13T00:00:03Z",
                "compilerCleanupCompleted": "2026-07-13T00:00:04Z",
            },
            "dependencyInputs": [{"path": str(self.m.MODULE_PATH),
                                  "sha256": hashlib.sha256(self.m.MODULE_PATH.read_bytes()).hexdigest()}],
            "receiptPath": str(receipt_path),
            "receiptSha256": hashlib.sha256(receipt_path.read_bytes()).hexdigest(),
        }
        row["compilerCleanup"]["capturedDescendants"] = [{
            "processId": 7001, "parentProcessId": 1, "startedAtUtc": "s1",
            "executablePath": "C:/dotnet.exe", "role": "buildRoot",
        }]
        for key, path in files.items():
            row[key] = str(path)
            row[key.replace("Path", "Sha256")] = hashlib.sha256(path.read_bytes()).hexdigest()
        output_root = files["dllPath"].parent
        row["runnerOutputFiles"] = [
            {"relativePath": path.relative_to(output_root).as_posix(),
             "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
            for path in sorted(output_root.iterdir()) if path.is_file()
        ]
        return row

    def run_pair(self, root: Path, invoke, *, monotonic=None):
        kwargs = {}
        if monotonic is not None:
            kwargs["monotonic"] = monotonic
        return self.m.run_two_attempts(
            root,
            lambda attempt, profile, evidence, _runner, _remaining: invoke(
                attempt, profile, evidence
            ),
            authorized_private_root=root.parent,
            prebuild=self.prebuild_receipt,
            **kwargs,
        )

    def test_two_attempts_use_fresh_distinct_roots_and_zero_between(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "private"
            calls = []
            def invoke(attempt, profile_root, evidence_root):
                calls.append((attempt, profile_root, evidence_root))
                return self.closeout(root, attempt)
            result = self.run_pair(root, invoke)
        self.assertEqual([1, 2], [row[0] for row in calls])
        self.assertNotEqual(calls[0][1], calls[1][1])
        self.assertNotEqual(calls[0][2], calls[1][2])
        self.assertEqual(2, len(result["attempts"]))
        self.assertFalse(result["publicProjectionWritten"])

    def test_one_prebuild_precedes_attempt_roots_and_same_dll_is_rehashed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pair"
            events = []
            def prebuild(pair_root):
                events.append(("build", pair_root))
                return self.prebuild_receipt(pair_root)
            def invoke(attempt, profile_root, evidence_root, runner, remaining):
                events.append(("execute", attempt, runner["dllSha256"]))
                return self.closeout(root, attempt)
            result = self.m.run_two_attempts(
                root, invoke, authorized_private_root=root.parent, prebuild=prebuild,
                monotonic=iter((0.0, 1.0, 2.0, 3.0, 4.0, 5.0)).__next__,
            )
        self.assertEqual(["build", "execute", "execute"], [row[0] for row in events])
        self.assertEqual(events[1][2], events[2][2])
        self.assertNotEqual(
            result["attempts"][0]["phaseTimestamps"],
            result["attempts"][1]["phaseTimestamps"],
        )
        self.assertTrue(result["pairEligible"])

    def test_prebuild_failure_or_hash_drift_creates_no_attempt(self):
        for mode in ("failure", "dll-drift", "runtimeconfig-drift", "deps-drift"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "pair"
                calls = []
                def prebuild(pair_root):
                    row = self.prebuild_receipt(pair_root)
                    row["passed"] = mode != "failure"
                    if mode.endswith("drift"):
                        key = {
                            "dll-drift": "dllSha256",
                            "runtimeconfig-drift": "runtimeConfigSha256",
                            "deps-drift": "depsSha256",
                        }[mode]
                        row[key] = "0" * 64
                    return row
                with self.assertRaises(RuntimeError):
                    self.m.run_two_attempts(
                        root, lambda *args: calls.append(args), authorized_private_root=root.parent,
                        prebuild=prebuild,
                    )
                self.assertEqual([], calls)
                self.assertFalse((root / "attempt-01").exists())

    def test_one_valid_one_invalid_withholds_projection_and_never_runs_third(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "private"
            calls = []
            def invoke(attempt, profile_root, evidence_root):
                calls.append(attempt)
                return self.closeout(root, attempt, accepted=attempt == 1)
            result = self.run_pair(root, invoke)
        self.assertEqual([1, 2], calls)
        self.assertFalse(result["pairEligible"])
        self.assertFalse(result["publicProjectionWritten"])

    def test_invalid_attempt_one_suppresses_attempt_two(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pair"
            calls = []
            def invoke(attempt, profile_root, evidence_root):
                calls.append(attempt)
                # Simulate live profile tree that must be stripped after closeout.
                bulky = root / f"attempt-{attempt:02d}" / "profile-app-config" / "x"
                bulky.mkdir(parents=True)
                (bulky / "BEA.exe").write_bytes(b"game")
                return self.closeout(root, attempt, accepted=False)
            result = self.run_pair(root, invoke)
        self.assertEqual([1], calls)
        self.assertFalse(result["pairEligible"])
        self.assertFalse((root / "attempt-01" / "profile-app-config").exists())
        self.assertIn("labHygiene", result)

    def test_cleanup_failure_prevents_attempt_two(self):
        for field in ("qUpConfirmed", "observerHandleClosed", "managedProcessStopped",
                      "ownedProcessCount", "sourceUnchanged", "copyUnchanged"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "private"
                calls = []
                def invoke(attempt, profile_root, evidence_root):
                    calls.append(attempt)
                    kwargs = {
                        "q_up": field != "qUpConfirmed",
                        "handle": field != "observerHandleClosed",
                        "stopped": field != "managedProcessStopped",
                        "zero": field != "ownedProcessCount",
                        "source": field != "sourceUnchanged",
                        "copy": field != "copyUnchanged",
                    }
                    return self.closeout(root, attempt, **kwargs)
                with self.assertRaisesRegex(RuntimeError, "cleanup gate"):
                    self.run_pair(root, invoke)
                self.assertEqual([1], calls)

    def test_observer_false_backup_true_allows_clean_failed_closeout(self):
        """Backup Q-up is enough cleanup when the observer failed mid-window.

        Attempt two still does not run after a failed attempt one (pair needs two
        accepts), but closeout must not raise so the private evidence pair ends cleanly.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pair"
            calls = []
            def invoke(attempt, profile_root, evidence_root):
                calls.append(attempt)
                row = self.closeout(root, attempt, accepted=False, q_up=False)
                row["qUpConfirmed"] = True
                row["cleanup"] = {"observerQUp": False, "backupQUp": True,
                                  "phaseJobsClosed": True}
                return row
            result = self.run_pair(root, invoke)
        self.assertEqual([1], calls)
        self.assertFalse(result["pairEligible"])

    def test_remaining_budget_refuses_attempt_two_after_clean_attempt_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pair"
            calls = []
            clock = iter((0.0, 1.0, 2.0, 3.0, 386.0)).__next__
            def invoke(attempt, profile_root, evidence_root):
                calls.append(attempt)
                return self.closeout(root, attempt)
            with self.assertRaisesRegex(self.m.AttemptDeadlineExceeded, "full 215-second"):
                self.run_pair(root, invoke, monotonic=clock)
        self.assertEqual([1], calls)

    def test_receipt_reuse_deadline_and_public_output_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "private"
            first = None
            def invoke(attempt, profile_root, evidence_root):
                nonlocal first
                row = self.closeout(root, attempt)
                if first is None:
                    first = row
                else:
                    Path(row["receiptPath"]).write_bytes(Path(first["receiptPath"]).read_bytes())
                    row["receiptSha256"] = first["receiptSha256"]
                return row
            with self.assertRaisesRegex(RuntimeError, "fresh receipt"):
                self.run_pair(root, invoke)

            def timed_out(attempt, profile_root, evidence_root):
                raise self.m.AttemptDeadlineExceeded("observer deadline")
            with self.assertRaisesRegex(self.m.AttemptDeadlineExceeded, "observer deadline"):
                self.run_pair(Path(tmp) / "other", timed_out)

            def leaked(attempt, profile_root, evidence_root):
                row = self.closeout(Path(tmp) / "leak", attempt)
                row["publicProjectionWritten"] = True
                return row
            with self.assertRaisesRegex(RuntimeError, "public projection"):
                self.run_pair(Path(tmp) / "leak", leaked)


if __name__ == "__main__":
    unittest.main()
