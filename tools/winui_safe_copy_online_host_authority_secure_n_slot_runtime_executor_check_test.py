#!/usr/bin/env python3
"""Tests for the secure N-slot host-authority live runtime executor checker."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

import winui_safe_copy_online_host_authority_secure_n_slot_runtime_executor_check as checker


class SecureNSlotRuntimeExecutorCheckerTests(unittest.TestCase):
    def test_default_validator_rejects_fixture_receipt(self) -> None:
        root = checker.runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as tmp:
            proof_path = checker.make_fixture(Path(tmp))

            with self.assertRaises(checker.SecureNSlotRuntimeExecutorProofError):
                checker.validate_secure_runtime_executor_proof(proof_path)

    def test_self_test_path_accepts_secure_session_derived_runtime_executor_fixture(self) -> None:
        root = checker.runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as tmp:
            proof_path = checker.make_fixture(Path(tmp))
            summary = checker.validate_secure_runtime_executor_proof(proof_path, allow_fixture=True)

            self.assertEqual(summary["schemaVersion"], checker.EXPECTED_SCHEMA)
            self.assertEqual(summary["receiptMode"], "self-test-fixture")
            self.assertEqual(summary["securityProofScope"], checker.security.EXPECTED_SECURITY_SCOPE)
            self.assertEqual(summary["acceptedOriginalBinaryGameplaySlots"], ["P1", "P2"])
            self.assertEqual(summary["metadataOnlySlots"], ["P3", "P4"])
            self.assertEqual(summary["rejectedGameplayRouteSlots"], ["P3", "P4"])
            self.assertEqual(summary["secureSessionAcceptedCommandCount"], 2)
            self.assertEqual(summary["secureSessionMetadataRejectionCount"], 2)
            self.assertEqual(
                summary["secureSessionSecurityRejectionCount"],
                len(checker.security.EXPECTED_SECURITY_REJECTION_CASES),
            )
            self.assertEqual(summary["deliveredOriginalBinaryCommandCount"], 2)
            self.assertTrue(summary["hostHelperInputSent"])
            self.assertFalse(summary["gameInputSentByNSlotScheduler"])
            self.assertEqual(summary["newBeaLaunchCount"], 1)
            self.assertEqual(summary["cdbAttachCount"], 1)
            self.assertEqual(summary["nPlayerOriginalBinaryRuntimeProof"], 0)
            self.assertFalse(summary["activeP3P4OriginalBinaryGameplayProof"])

    def test_rejects_runtime_sequence_not_derived_from_secure_session(self) -> None:
        root = checker.runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as tmp:
            proof_path = checker.make_fixture(Path(tmp))
            proof = checker.read_json(proof_path)
            runtime_path = checker.resolve_path(proof_path, str(proof["liveRuntimeArtifact"]))
            runtime = checker.read_json(runtime_path)
            runtime["inputCdbWindows"][1]["sequence"] = "down:O,wait:500,up:O"
            checker.write_json(runtime_path, runtime)

            with self.assertRaises(checker.SecureNSlotRuntimeExecutorProofError):
                checker.validate_secure_runtime_executor_proof(proof_path, allow_fixture=True)

    def test_rejects_p3p4_runtime_overclaim(self) -> None:
        root = checker.runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as tmp:
            proof_path = checker.make_fixture(Path(tmp))
            proof = checker.read_json(proof_path)
            proof["execution"]["nPlayerOriginalBinaryRuntimeProof"] = 4
            proof["execution"]["activeP3P4OriginalBinaryGameplayProof"] = True
            checker.write_json(proof_path, proof)

            with self.assertRaises(checker.SecureNSlotRuntimeExecutorProofError):
                checker.validate_secure_runtime_executor_proof(proof_path, allow_fixture=True)

    def test_retries_first_wait_render_warmup_miss_before_accepting_live_proof(self) -> None:
        root = checker.runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as tmp:
            tmp_root = Path(tmp)
            session_path = tmp_root / "session-security-proof.json"
            checker.security_builder.build_bundle(session_path)
            exe_path = tmp_root / "BEA.exe"
            exe_path.write_bytes(b"fixture")
            artifact_root = tmp_root / "live"

            run_roots: list[Path] = []
            make_receipts: list[dict[str, object]] = []
            original_run_live_smoke_process = checker.runtime_bridge.movement_bridge.executor.run_live_smoke_process
            original_make_secure_runtime_executor_proof = checker.make_secure_runtime_executor_proof
            original_warmup_check = checker.runtime_artifact_has_first_wait_render_warmup_miss
            original_process_check = checker.runtime_bridge.movement_bridge.executor.require_no_bea_or_cdb_processes

            def fake_run_live_smoke_process(command: list[str]) -> subprocess.CompletedProcess[str]:
                current_root = Path(command[command.index("--artifact-root") + 1])
                current_root.mkdir(parents=True, exist_ok=True)
                (current_root / "live-safe-copy-runtime-smoke.json").write_text("{}", encoding="utf-8")
                run_roots.append(current_root)
                return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

            def fake_make_secure_runtime_executor_proof(
                session_path_arg: Path,
                runtime_path: Path,
                output_path: Path,
                *,
                execution_receipt: dict[str, object],
                allow_fixture_receipt: bool = False,
            ) -> dict[str, object]:
                del session_path_arg, runtime_path, output_path, allow_fixture_receipt
                make_receipts.append(execution_receipt)
                if len(make_receipts) == 1:
                    self.assertEqual(execution_receipt["liveExecutorAttemptCount"], 1)
                    self.assertFalse(execution_receipt["liveExecutorRetriedAfterFirstWaitRenderWarmupMiss"])
                    raise checker.runtime_bridge.movement_bridge.movement.MovementStateDeltaError(
                        "wait window 1 had no render movement samples"
                    )
                self.assertEqual(execution_receipt["liveExecutorAttemptCount"], 2)
                self.assertTrue(execution_receipt["liveExecutorRetriedAfterFirstWaitRenderWarmupMiss"])
                return {"artifact": str(artifact_root / "retry-2" / "secure-n-slot-runtime-executor-proof.json")}

            try:
                checker.runtime_bridge.movement_bridge.executor.run_live_smoke_process = fake_run_live_smoke_process
                checker.make_secure_runtime_executor_proof = fake_make_secure_runtime_executor_proof
                checker.runtime_artifact_has_first_wait_render_warmup_miss = lambda runtime_path: True
                checker.runtime_bridge.movement_bridge.executor.require_no_bea_or_cdb_processes = lambda reason: None

                summary = checker.build_live_secure_runtime_executor(
                    session_path,
                    artifact_root,
                    exe_override=exe_path,
                )
            finally:
                checker.runtime_bridge.movement_bridge.executor.run_live_smoke_process = original_run_live_smoke_process
                checker.make_secure_runtime_executor_proof = original_make_secure_runtime_executor_proof
                checker.runtime_artifact_has_first_wait_render_warmup_miss = original_warmup_check
                checker.runtime_bridge.movement_bridge.executor.require_no_bea_or_cdb_processes = original_process_check

            self.assertEqual(len(run_roots), 2)
            self.assertEqual(run_roots[0], artifact_root)
            self.assertEqual(run_roots[1], artifact_root / "retry-2")
            self.assertEqual(summary["artifact"], str(artifact_root / "retry-2" / "secure-n-slot-runtime-executor-proof.json"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
