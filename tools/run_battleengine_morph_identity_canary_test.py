#!/usr/bin/env python3
"""Focused tests for the authority-gated morph identity matrix executor."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import battleengine_morph_identity_authority as authority_control
import run_battleengine_morph_identity_canary as runner


NOW = "2026-07-12T20:00:00Z"
LATER = "2026-07-12T21:00:00Z"
COMMAND_SHA256 = "c" * 64


def authority(proof_root: Path) -> dict[str, object]:
    return {
        "schemaVersion": runner.AUTHORITY_SCHEMA,
        "actionFamily": runner.ACTION_FAMILY,
        "issuedAtUtc": NOW,
        "expiresAtUtc": LATER,
        "proofRoot": str(proof_root),
        "allowedActions": list(runner.REQUIRED_ALLOWED_ACTIONS),
        "forbiddenActions": list(runner.REQUIRED_FORBIDDEN_ACTIONS),
        "maxSpendUsd": 0,
        "validationGates": list(runner.REQUIRED_VALIDATION_GATES),
        "cleanup": runner.REQUIRED_CLEANUP,
        "rollback": runner.REQUIRED_ROLLBACK,
    }


def leases(owner: str = "task4-test") -> dict[str, object]:
    return {
        "schemaVersion": runner.LEASE_SCHEMA,
        "actionFamily": runner.ACTION_FAMILY,
        "issuedAtUtc": NOW,
        "expiresAtUtc": LATER,
        "owner": owner,
        "leases": [
            {
                "resource": resource,
                "owner": owner,
                "exclusive": True,
                "acquiredAtUtc": NOW,
                "expiresAtUtc": LATER,
            }
            for resource in runner.REQUIRED_RESOURCES
        ],
    }


def public_run(role: str, receipt_sha256: str, raw_capture_sha256: str) -> dict[str, object]:
    events = [] if role == "noInputControl" else list(runner.canary.EXPECTED_EVENTS)
    return {
        "role": role,
        "receiptSha256": receipt_sha256,
        "rawCaptureSha256": raw_capture_sha256,
        "events": events,
        "cleanup": {
            "keysReleased": True,
            "cdbDetached": True,
            "managedProcessStopped": True,
            "ownedProcessCount": 0,
        },
    }


class FakeHarness:
    def __init__(
        self,
        *,
        fail_role: str | None = None,
        reuse_receipt: bool = False,
        reuse_process: bool = False,
        reuse_run_id: bool = False,
        reuse_copy: bool = False,
        after_call=None,
    ) -> None:
        self.fail_role = fail_role
        self.reuse_receipt = reuse_receipt
        self.reuse_process = reuse_process
        self.reuse_run_id = reuse_run_id
        self.reuse_copy = reuse_copy
        self.after_call = after_call
        self.calls: list[tuple[str, Path, tuple[str, ...]]] = []

    def __call__(self, role: str, role_root: Path, command: tuple[str, ...]) -> runner.HarnessResult:
        self.calls.append((role, role_root, command))
        if role == self.fail_role:
            return runner.HarnessResult(
                2,
                role_root / "missing.json",
                role_root / "missing.log",
                role_root / "missing-receipt.json",
            )
        role_root.mkdir(parents=True, exist_ok=False)
        receipt_number = 1 if self.reuse_receipt else len(self.calls)
        process_number = 9001 if self.reuse_process or self.reuse_receipt else 9000 + len(self.calls)
        process_started = (
            "2026-07-12T20:00:01.0000000Z"
            if self.reuse_process or self.reuse_receipt
            else f"2026-07-12T20:00:0{receipt_number}.0000000Z"
        )
        copy_root = role_root.parent / "shared-copy" if self.reuse_copy else role_root / "GameProfiles" / role
        copy_root.mkdir(parents=True, exist_ok=True)
        process_executable = copy_root / "BEA.exe"
        process_executable.write_bytes(role.encode("ascii"))
        manifest_path = copy_root / "onslaught-profile-manifest.json"
        manifest_path.write_text("{}", encoding="utf-8")
        receipt_path = role_root / "runtime-process-receipt.json"
        receipt_path.write_text(
            json.dumps({
                "schemaVersion": "runtime-process-receipt.v1",
                "runId": "reused-run" if self.reuse_run_id else f"run-{receipt_number}",
                "process": {
                    "id": process_number,
                    "startedAtUtc": process_started,
                    "executable": {
                        "path": str(process_executable),
                        "sha256": hashlib.sha256(process_executable.read_bytes()).hexdigest(),
                        "size": process_executable.stat().st_size,
                    },
                    "workingDirectory": str(copy_root),
                    "launchArguments": ["-skipfmv", "-level", "850", "-configuration", "2"],
                },
                "profileManifest": {
                    "path": str(manifest_path),
                    "sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
                    "size": manifest_path.stat().st_size,
                },
                "window": {"hwndHex": f"0x{receipt_number:x}"},
                "module": {
                    "path": str(process_executable),
                    "baseAddressHex": "0x400000",
                    "size": runner.canary.CANONICAL_SIZE,
                },
                "sourceExecutableSha256": runner.canary.CANONICAL_SHA256,
                "copiedExecutableSha256": runner.canary.CANONICAL_SHA256,
                "commandTemplateSha256": runner.canary.TEMPLATE_SHA256,
                "generatedCommandSha256": COMMAND_SHA256,
            }),
            encoding="utf-8",
        )
        receipt_digest = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
        artifact_path = role_root / "battleengine-morph-identity-canary-private-run.json"
        artifact_path.write_text(
            json.dumps({
                "schema": "winui-original-binary-battleengine-morph-identity-canary-private-run.v1",
                "executablePath": str(process_executable),
                "templatePath": str(runner.canary.DEFAULT_TEMPLATE),
                "commandPath": str(role_root / "cdb" / "battleengine-morph-identity-canary.cdb.txt"),
                "receiptSha256": receipt_digest,
                "commandSha256": COMMAND_SHA256,
                "templateSha256": runner.canary.TEMPLATE_SHA256,
                "executableSha256": runner.canary.CANONICAL_SHA256,
                "fingerprints": [],
                "sourceUnchanged": True,
                "copyUnchanged": True,
                "cleanup": {
                    "keysReleased": True,
                    "cdbDetached": True,
                    "managedProcessStopped": True,
                    "ownedProcessCount": 0,
                },
            }),
            encoding="utf-8",
        )
        log_path = role_root / "cdb" / "windbg.log"
        log_path.parent.mkdir(exist_ok=True)
        log_path.write_text(
            f"MORPH_CANARY_BEGIN\nMORPH_CANARY_READY\nROLE={role}\n",
            encoding="utf-8",
        )
        if self.after_call is not None:
            self.after_call(role, len(self.calls))
        return runner.HarnessResult(0, artifact_path, log_path, receipt_path)


class MatrixExecutorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="morph-matrix-test-")
        self.root = Path(self.temp.name)
        self.private_parent = self.root / "local-proofs"
        self.private_parent.mkdir()
        self.proof_root = self.private_parent / "battleengine-morph-identity-canary-matrix"
        self.control_root = self.private_parent / "battleengine-morph-identity-canary-control-test"
        self.control_root.mkdir()
        self.authority_path = self.control_root / "authority.json"
        self.leases_path = self.control_root / "leases.json"
        self.source_root = self.root / "source"
        self.source_root.mkdir()
        (self.source_root / "BEA.exe").write_bytes(b"fixture")
        self.exe_override = self.source_root / "BEA.exe.original.backup"
        self.exe_override.write_bytes(b"fixture")
        self.write_controls()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_controls(
        self,
        authority_payload: dict[str, object] | None = None,
        lease_payload: dict[str, object] | None = None,
    ) -> None:
        self.authority_path.write_text(
            json.dumps(authority_payload or authority(self.proof_root)),
            encoding="utf-8",
        )
        self.leases_path.write_text(
            json.dumps(lease_payload or leases()),
            encoding="utf-8",
        )

    def preflight(self, source_root: Path, exe_override: Path) -> runner.RuntimePreflight:
        return runner.RuntimePreflight(
            source_root=source_root.resolve(),
            exe_override=exe_override.resolve(),
            executable_sha256=runner.canary.CANONICAL_SHA256,
            command_sha256=COMMAND_SHA256,
            template_sha256=runner.canary.TEMPLATE_SHA256,
        )

    def executor(
        self,
        harness: FakeHarness,
        *,
        materialize_run=None,
        materialize_matrix=None,
        validate_public=None,
        now=None,
    ):
        calls: list[tuple[bytes, bytes, str]] = []

        def materializer(artifact: bytes, log: bytes, role: str):
            calls.append((artifact, log, role))
            payload = json.loads(artifact.decode("utf-8"))
            return public_run(
                role,
                payload["receiptSha256"],
                hashlib.sha256(log).hexdigest(),
            )

        def matrix_materializer(runs):
            return {"schema": runner.canary.PUBLIC_SCHEMA, "runs": list(runs)}

        return runner.MatrixExecutor(
            harness=harness,
            materialize_run=materialize_run or materializer,
            materialize_matrix=materialize_matrix or matrix_materializer,
            validate_public=validate_public or (lambda _: None),
            runtime_preflight=self.preflight,
            private_parent=self.private_parent,
            now=now or (lambda: runner.parse_utc(NOW, "test now")),
        ), calls

    def run_live(self, executor: runner.MatrixExecutor):
        return executor.run_live(
            self.proof_root,
            self.authority_path,
            self.leases_path,
            runner.LIVE_ARM_PHRASE,
            self.source_root,
            self.exe_override,
        )

    def test_dry_run_is_complete_fixed_and_never_calls_harness(self) -> None:
        harness = FakeHarness()
        executor, _ = self.executor(harness)
        plan = executor.dry_run(
            self.proof_root,
            self.authority_path,
            self.leases_path,
            self.source_root,
            self.exe_override,
        )
        self.assertEqual(list(runner.RUN_ROLES), [row.role for row in plan.runs])
        self.assertEqual([], harness.calls)
        self.assertFalse(self.proof_root.exists())
        self.assertEqual(["no-input-control", "positive-transform", "positive-repeat"],
                         [row.root.name for row in plan.runs])
        for index, row in enumerate(plan.runs):
            self.assertEqual(("-skipfmv", "-level", "850", "-configuration", "2"), row.launch_arguments)
            self.assertEqual(() if index == 0 else ("tap:Q",), row.input_sequences)
            self.assertEqual(COMMAND_SHA256, row.command_sha256)
            self.assertIn("--canary-authority-file", row.command)
            self.assertIn("--expected-canary-authority-sha256", row.command)
            self.assertIn("--canary-leases-file", row.command)
            self.assertIn("--expected-canary-leases-sha256", row.command)

    def test_dry_run_requires_both_runtime_inputs_and_private_control_files(self) -> None:
        executor, _ = self.executor(FakeHarness())
        with self.assertRaises(runner.CanaryError):
            executor.dry_run(
                self.proof_root,
                self.authority_path,
                self.leases_path,
                None,
                None,
            )
        nested = self.root / "nested" / "local-proofs" / "battleengine-morph-identity-canary-run"
        with self.assertRaises(runner.CanaryError):
            executor.dry_run(
                nested,
                self.authority_path,
                self.leases_path,
                self.source_root,
                self.exe_override,
            )

    def test_symlinked_private_parent_is_rejected_before_resolution(self) -> None:
        target = self.root / "private-proof-target"
        target.mkdir()
        linked_parent = self.root / "linked-local-proofs"
        try:
            linked_parent.symlink_to(target, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"directory symlinks are unavailable: {exc}")
        with self.assertRaisesRegex(authority_control.AuthorityError, "reparse or symlink"):
            authority_control.validate_private_proof_root(
                linked_parent / "battleengine-morph-identity-canary-matrix",
                private_parent=linked_parent,
                require_exists=False,
            )

    def test_real_dry_run_preflight_rejects_noncanonical_executables(self) -> None:
        executor = runner.MatrixExecutor(
            harness=FakeHarness(),
            materialize_run=lambda *_: {},
            materialize_matrix=lambda _: {},
            validate_public=lambda _: None,
            private_parent=self.private_parent,
            now=lambda: runner.parse_utc(NOW, "test now"),
        )
        with self.assertRaisesRegex(runner.CanaryError, "canonical"):
            executor.dry_run(
                self.proof_root,
                self.authority_path,
                self.leases_path,
                self.source_root,
                self.exe_override,
            )

    def test_control_sets_are_order_independent_but_duplicates_and_drift_fail(self) -> None:
        reordered_authority = authority(self.proof_root)
        reordered_authority["allowedActions"] = list(reversed(reordered_authority["allowedActions"]))
        reordered_leases = leases()
        reordered_leases["leases"] = list(reversed(reordered_leases["leases"]))
        self.write_controls(reordered_authority, reordered_leases)
        executor, _ = self.executor(FakeHarness())
        executor.dry_run(
            self.proof_root,
            self.authority_path,
            self.leases_path,
            self.source_root,
            self.exe_override,
        )
        duplicated = authority(self.proof_root)
        duplicated["allowedActions"][0] = duplicated["allowedActions"][1]
        self.write_controls(duplicated, leases())
        with self.assertRaises(runner.CanaryError):
            executor.dry_run(
                self.proof_root,
                self.authority_path,
                self.leases_path,
                self.source_root,
                self.exe_override,
            )

    def test_control_files_require_the_exact_separate_directory_layout(self) -> None:
        wrong_root = self.private_parent / "misc-controls"
        wrong_root.mkdir()
        wrong_authority = wrong_root / "authority.json"
        wrong_leases = wrong_root / "leases.json"
        wrong_authority.write_text(self.authority_path.read_text(encoding="utf-8"), encoding="utf-8")
        wrong_leases.write_text(self.leases_path.read_text(encoding="utf-8"), encoding="utf-8")
        executor, _ = self.executor(FakeHarness())
        with self.assertRaisesRegex(runner.CanaryError, "control-directory layout"):
            executor.dry_run(
                self.proof_root,
                wrong_authority,
                wrong_leases,
                self.source_root,
                self.exe_override,
            )

    def test_live_requires_exact_arm_and_invokes_each_role_once(self) -> None:
        harness = FakeHarness()
        executor, materialize_calls = self.executor(harness)
        with self.assertRaises(runner.CanaryError):
            executor.run_live(
                self.proof_root,
                self.authority_path,
                self.leases_path,
                "wrong",
                self.source_root,
                self.exe_override,
            )
        result = self.run_live(executor)
        self.assertEqual(list(runner.RUN_ROLES), [call[0] for call in harness.calls])
        self.assertEqual(3, len(materialize_calls))
        self.assertTrue(result.private_manifest.is_file())
        self.assertTrue(result.sanitized_summary.is_file())

    def test_first_harness_or_semantic_failure_stops_before_next_role(self) -> None:
        harness = FakeHarness(fail_role="positiveTransform")
        executor, calls = self.executor(harness)
        with self.assertRaises(runner.CanaryError):
            self.run_live(executor)
        self.assertEqual(["noInputControl", "positiveTransform"], [call[0] for call in harness.calls])
        self.assertEqual(1, len(calls))

        import shutil
        shutil.rmtree(self.proof_root)
        harness = FakeHarness()

        def reject_control(*args):
            raise ValueError("control event")

        executor, _ = self.executor(harness, materialize_run=reject_control)
        with self.assertRaises(runner.CanaryError):
            self.run_live(executor)
        self.assertEqual(["noInputControl"], [call[0] for call in harness.calls])
        self.assertFalse((self.proof_root / runner.SANITIZED_SUMMARY_NAME).exists())

    def test_authority_is_reloaded_and_expiration_or_drift_stops_next_role(self) -> None:
        def expire_after_control(role: str, call_count: int) -> None:
            if call_count == 1:
                expired = leases()
                expired["expiresAtUtc"] = NOW
                for row in expired["leases"]:
                    row["expiresAtUtc"] = NOW
                self.write_controls(lease_payload=expired)

        harness = FakeHarness(after_call=expire_after_control)
        executor, _ = self.executor(harness)
        with self.assertRaises(runner.CanaryError):
            self.run_live(executor)
        self.assertEqual(["noInputControl"], [call[0] for call in harness.calls])

    def test_reused_receipt_process_run_or_copy_identity_is_rejected(self) -> None:
        variants = (
            (FakeHarness(reuse_receipt=True), 2),
            (FakeHarness(reuse_process=True), 2),
            (FakeHarness(reuse_run_id=True), 2),
            (FakeHarness(reuse_copy=True), 1),
        )
        for harness, expected_calls in variants:
            executor, _ = self.executor(harness)
            with self.subTest(harness=harness), self.assertRaises(runner.CanaryError):
                self.run_live(executor)
            self.assertEqual(expected_calls, len(harness.calls))
            self.assertLess(len(harness.calls), len(runner.RUN_ROLES))
            if self.proof_root.exists():
                import shutil
                shutil.rmtree(self.proof_root)

    def test_hash_drift_during_materialization_fails_before_next_role(self) -> None:
        harness = FakeHarness()

        def drifting_materializer(artifact: bytes, log: bytes, role: str):
            log_path = harness.calls[-1][1] / "cdb" / "windbg.log"
            log_path.write_text(log_path.read_text(encoding="utf-8") + "DRIFT\n", encoding="utf-8")
            payload = json.loads(artifact.decode("utf-8"))
            return public_run(role, payload["receiptSha256"], hashlib.sha256(log).hexdigest())

        executor, _ = self.executor(harness, materialize_run=drifting_materializer)
        with self.assertRaises(runner.CanaryError):
            self.run_live(executor)
        self.assertEqual(["noInputControl"], [call[0] for call in harness.calls])

    def test_executor_rejects_public_path_leak_even_if_injected_validator_accepts(self) -> None:
        harness = FakeHarness()

        def leaking_matrix(runs):
            return {
                "schema": runner.canary.PUBLIC_SCHEMA,
                "runs": list(runs),
                "artifactPath": str(self.proof_root / "private.json"),
            }

        executor, _ = self.executor(
            harness,
            materialize_matrix=leaking_matrix,
            validate_public=lambda _: None,
        )
        with self.assertRaises(runner.CanaryError):
            self.run_live(executor)
        self.assertFalse((self.proof_root / runner.SANITIZED_SUMMARY_NAME).exists())

    def test_real_harness_cannot_be_combined_with_injected_acceptance_interfaces(self) -> None:
        with self.assertRaises(runner.CanaryError):
            runner.MatrixExecutor(validate_public=lambda _: None)

    def test_control_json_rejects_duplicate_keys(self) -> None:
        self.authority_path.write_text(
            '{"schemaVersion":"one","schemaVersion":"two"}',
            encoding="utf-8",
        )
        with self.assertRaises(authority_control.AuthorityError):
            authority_control.load_control_records(
                self.authority_path,
                self.leases_path,
                self.proof_root,
                runner.parse_utc(NOW, "now"),
                private_parent=self.private_parent,
                proof_root_exists=False,
            )

    def test_summary_is_not_published_when_manifest_publish_fails(self) -> None:
        executor, _ = self.executor(FakeHarness())
        original_replace = runner.os.replace

        def fail_manifest(source, target):
            if Path(target).name == runner.PRIVATE_MANIFEST_NAME:
                raise OSError("injected manifest publish failure")
            return original_replace(source, target)

        with mock.patch.object(runner.os, "replace", side_effect=fail_manifest):
            with self.assertRaises(runner.CanaryError):
                self.run_live(executor)
        self.assertFalse((self.proof_root / runner.SANITIZED_SUMMARY_NAME).exists())

    def test_default_harness_marks_parent_interrupt_invalid_after_child_cleanup(self) -> None:
        process = mock.Mock()
        process.wait.side_effect = [KeyboardInterrupt(), 0]
        with mock.patch.object(runner.subprocess, "Popen", return_value=process) as popen:
            result = runner._default_harness(
                "noInputControl",
                self.proof_root / "no-input-control",
                ("py", "-3", "fake-harness.py"),
            )
        self.assertEqual(130, result.exit_code)
        self.assertEqual(2, process.wait.call_count)
        self.assertEqual(
            getattr(runner.subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
            popen.call_args.kwargs["creationflags"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
