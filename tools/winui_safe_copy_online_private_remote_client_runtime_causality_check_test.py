#!/usr/bin/env python3
"""Tests for private remote-client to runtime-executor causality proof validation."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import build_winui_original_binary_private_remote_client_runtime_causality_bundle as builder
import winui_safe_copy_online_host_authority_runtime_executor_check as executor_check
import winui_safe_copy_online_private_remote_client_runtime_causality_check as checker


class PrivateRemoteClientRuntimeCausalityCheckTests(unittest.TestCase):
    def test_accepts_private_remote_client_runtime_causality_fixture(self) -> None:
        with tempfile.TemporaryDirectory(dir=executor_check.PRIVATE_PROOF_ROOT) as raw_tmp:
            tmp = Path(raw_tmp)
            executor_path = executor_check.make_executor_fixture(tmp / "executor-source")
            output_path = tmp / "wrapper" / "private-remote-client-runtime-causality-proof.json"

            build_summary = builder.build_bundle_from_executor(
                executor_path,
                output_path,
                allow_fixture_executor=True,
            )
            check_summary = checker.validate_bundle(output_path, allow_fixture=True)

            self.assertTrue(build_summary["privateRemoteClientRuntimeCausalityProven"])
            self.assertTrue(check_summary["privateRemoteClientRuntimeCausalityProven"])
            self.assertEqual(check_summary["remoteClientAcceptedCommandId"], "private-remote-client-p2-forward-0001")
            self.assertEqual(check_summary["acceptedOriginalBinaryGameplaySlots"], ["P1", "P2"])
            self.assertEqual(check_summary["metadataOnlySlots"], ["P3", "P4"])
            self.assertEqual(check_summary["newBeaLaunchCount"], 1)
            self.assertEqual(check_summary["cdbAttachCount"], 1)
            self.assertEqual(check_summary["deliveredOriginalBinaryCommandCount"], 2)
            self.assertFalse(check_summary["baseOnlineMultiplayerReady"])
            self.assertFalse(check_summary["multiHostLanProof"])
            self.assertFalse(check_summary["nativeBeaNetcodeProof"])

    def test_rejects_remote_client_hash_mismatch(self) -> None:
        with tempfile.TemporaryDirectory(dir=executor_check.PRIVATE_PROOF_ROOT) as raw_tmp:
            tmp = Path(raw_tmp)
            executor_path = executor_check.make_executor_fixture(tmp / "executor-source")
            output_path = tmp / "wrapper" / "private-remote-client-runtime-causality-proof.json"
            builder.build_bundle_from_executor(executor_path, output_path, allow_fixture_executor=True)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            payload["sourceArtifacts"]["privateRemoteClientProofSha256"] = "0" * 64
            output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

            with self.assertRaises(checker.PrivateRemoteClientRuntimeCausalityError):
                checker.validate_bundle(output_path, allow_fixture=True)

    def test_rejects_online_overclaim(self) -> None:
        with tempfile.TemporaryDirectory(dir=executor_check.PRIVATE_PROOF_ROOT) as raw_tmp:
            tmp = Path(raw_tmp)
            executor_path = executor_check.make_executor_fixture(tmp / "executor-source")
            output_path = tmp / "wrapper" / "private-remote-client-runtime-causality-proof.json"
            builder.build_bundle_from_executor(executor_path, output_path, allow_fixture_executor=True)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            payload["nonClaims"]["baseOnlineMultiplayerReady"] = True
            output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

            with self.assertRaises(checker.PrivateRemoteClientRuntimeCausalityError):
                checker.validate_bundle(output_path, allow_fixture=True)

    def test_rejects_absolute_source_artifact_path(self) -> None:
        with tempfile.TemporaryDirectory(dir=executor_check.PRIVATE_PROOF_ROOT) as raw_tmp:
            tmp = Path(raw_tmp)
            executor_path = executor_check.make_executor_fixture(tmp / "executor-source")
            output_path = tmp / "wrapper" / "private-remote-client-runtime-causality-proof.json"
            builder.build_bundle_from_executor(executor_path, output_path, allow_fixture_executor=True)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            raw_remote_path = Path(payload["sourceArtifacts"]["privateRemoteClientProof"])
            if not raw_remote_path.is_absolute():
                raw_remote_path = output_path.parent / raw_remote_path
            payload["sourceArtifacts"]["privateRemoteClientProof"] = str(raw_remote_path.resolve())
            output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

            with self.assertRaises(checker.PrivateRemoteClientRuntimeCausalityError):
                checker.validate_bundle(output_path, allow_fixture=True)


if __name__ == "__main__":
    unittest.main()
