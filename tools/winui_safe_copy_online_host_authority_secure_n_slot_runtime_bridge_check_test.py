#!/usr/bin/env python3
"""Tests for the secure N-slot host-authority runtime bridge checker."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import build_winui_original_binary_host_authority_n_slot_session_security_smoke_bundle as security_builder
import winui_safe_copy_online_host_authority_n_slot_runtime_bridge_check as runtime_bridge
import winui_safe_copy_online_host_authority_secure_n_slot_runtime_bridge_check as checker


class SecureNSlotRuntimeBridgeCheckerTests(unittest.TestCase):
    def test_links_session_security_to_runtime_bridge_without_new_runtime_claim(self) -> None:
        root = runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as tmp:
            work = Path(tmp)
            session_path = work / "session" / "host-authority-n-slot-session-security-smoke-proof.json"
            security_builder.build_bundle(session_path)
            bridge_path = runtime_bridge.make_live_bridge_fixture(work / "bridge")
            proof_path = work / "secure-n-slot-runtime-bridge-proof.json"

            built = checker.make_secure_bridge_proof(session_path, bridge_path, proof_path)
            summary = checker.validate_secure_bridge_proof(proof_path)

            self.assertEqual(built["schemaVersion"], checker.EXPECTED_SCHEMA)
            self.assertEqual(summary["securityProofScope"], checker.EXPECTED_SECURITY_SCOPE)
            self.assertTrue(summary["secureSessionAcceptedRelayFeedsRuntimeBridge"])
            self.assertTrue(summary["runtimeCompatibleP1P2RelayHashMatched"])
            self.assertEqual(summary["acceptedOriginalBinaryGameplaySlots"], ["P1", "P2"])
            self.assertEqual(summary["metadataOnlySlots"], ["P3", "P4"])
            self.assertEqual(summary["rejectedGameplayRouteSlots"], ["P3", "P4"])
            self.assertEqual(summary["secureSessionAcceptedCommandCount"], 2)
            self.assertEqual(summary["sourceRuntimeBridgeDeliveredOriginalBinaryCommandCount"], 2)
            self.assertEqual(summary["wrapperNewBeaLaunchCount"], 0)
            self.assertEqual(summary["wrapperCdbAttachCount"], 0)
            self.assertFalse(summary["multiHostLanProof"])
            self.assertFalse(summary["publicMatchmakingProof"])
            self.assertFalse(summary["nativeBeaNetcodeProof"])
            self.assertFalse(summary["activeP3P4OriginalBinaryGameplayProof"])

    def test_rejects_runtime_bridge_relay_hash_mismatch(self) -> None:
        root = runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as tmp:
            work = Path(tmp)
            session_path = work / "session" / "host-authority-n-slot-session-security-smoke-proof.json"
            security_builder.build_bundle(session_path)
            bridge_path = runtime_bridge.make_live_bridge_fixture(work / "bridge")
            proof_path = Path(bridge_path)
            bridge = checker.read_json(proof_path)
            bridge["execution"]["runtimeCompatibleP1P2RelayHash"] = "0" * 64
            checker.write_json(proof_path, bridge)

            with self.assertRaises(checker.SecureNSlotRuntimeBridgeProofError):
                checker.make_secure_bridge_proof(session_path, proof_path, work / "secure-n-slot-runtime-bridge-proof.json")

    def test_rejects_session_security_overclaim_or_tamper(self) -> None:
        root = runtime_bridge.movement_bridge.executor.PRIVATE_PROOF_ROOT
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=root) as tmp:
            work = Path(tmp)
            session_path = work / "session" / "host-authority-n-slot-session-security-smoke-proof.json"
            security_builder.build_bundle(session_path)
            session = checker.read_json(session_path)
            session["transport"]["multiHostLanClaim"] = True
            checker.write_json(session_path, session)
            bridge_path = runtime_bridge.make_live_bridge_fixture(work / "bridge")

            with self.assertRaises(checker.SecureNSlotRuntimeBridgeProofError):
                checker.make_secure_bridge_proof(session_path, bridge_path, work / "secure-n-slot-runtime-bridge-proof.json")


if __name__ == "__main__":
    unittest.main(verbosity=2)
