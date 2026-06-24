#!/usr/bin/env python3
"""Tests for the N-slot host-authority session-security smoke checker."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import winui_safe_copy_online_host_authority_n_slot_session_security_smoke_check as checker
import build_winui_original_binary_host_authority_n_slot_session_security_smoke_bundle as builder


class HostAuthorityNSlotSessionSecuritySmokeCheckerTests(unittest.TestCase):
    def test_builder_output_validates_strict_session_security_without_runtime_overclaim(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "host-authority-n-slot-session-security-smoke-proof.json"

            build_summary = builder.build_bundle(bundle)
            summary = checker.validate_bundle(bundle)

            self.assertEqual(build_summary["summary"]["schemaVersion"], checker.EXPECTED_SCHEMA)
            self.assertEqual(summary["acceptedOriginalBinaryGameplayCommandCount"], 2)
            self.assertEqual(summary["rejectedSecurityCaseCount"], len(checker.EXPECTED_SECURITY_REJECTION_REASONS))
            self.assertTrue(summary["sessionScopedMacCoverageProof"])
            self.assertTrue(summary["maxJsonLineBytesEnforced"])
            self.assertTrue(summary["unknownFieldRejectionProof"])
            self.assertTrue(summary["strictMessageSchemaProof"])
            self.assertEqual(summary["newBeaLaunchCount"], 0)
            self.assertEqual(summary["cdbAttachCount"], 0)
            self.assertEqual(summary["nPlayerOriginalBinaryRuntimeProof"], 0)
            self.assertFalse(summary["activeP3P4OriginalBinaryGameplayProof"])

    def test_rejects_recomputed_tampered_relay_plan_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "host-authority-n-slot-session-security-smoke-proof.json"
            builder.build_bundle(bundle)
            data = checker.read_json(bundle)

            plan = data["hostAuthorityNSlotScheduler"]["relayPlan"]
            plan[0]["mappedInputSequence"] = "down:X,wait:500,up:X"
            data["hostAuthorityNSlotScheduler"]["relayPlanSha256"] = checker.sha256_payload(plan)
            checker.write_json(bundle, data)

            with self.assertRaises(checker.HostAuthorityNSlotSessionSecuritySmokeProofError):
                checker.validate_bundle(bundle)

    def test_rejects_tampered_security_case_identity(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "host-authority-n-slot-session-security-smoke-proof.json"
            builder.build_bundle(bundle)
            data = checker.read_json(bundle)

            first_case = data["sessionSecurityTestMatrix"]["rejectedSecurityCases"][0]
            first_case["caseId"] = "slot-rate-limit-renamed-but-still-rejected"
            checker.write_json(bundle, data)

            with self.assertRaises(checker.HostAuthorityNSlotSessionSecuritySmokeProofError):
                checker.validate_bundle(bundle)

    def test_rejects_tampered_security_case_response_type(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "host-authority-n-slot-session-security-smoke-proof.json"
            builder.build_bundle(bundle)
            data = checker.read_json(bundle)

            first_case = data["sessionSecurityTestMatrix"]["rejectedSecurityCases"][0]
            first_case["responseType"] = "session_rejected"
            checker.write_json(bundle, data)

            with self.assertRaises(checker.HostAuthorityNSlotSessionSecuritySmokeProofError):
                checker.validate_bundle(bundle)

    def test_authorization_describes_canonical_signed_message_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "host-authority-n-slot-session-security-smoke-proof.json"
            builder.build_bundle(bundle)
            data = checker.read_json(bundle)
            authorization = data["authorization"]

            self.assertEqual(authorization["sessionScopedMacCoverageMode"], "canonical-json-message-excluding-mac")
            self.assertEqual(authorization["sessionScopedMacExcludedFields"], ["mac"])
            self.assertEqual(authorization["sessionHelloMacFields"], checker.EXPECTED_SESSION_HELLO_MAC_FIELDS)
            self.assertEqual(authorization["commandMacFields"], checker.EXPECTED_COMMAND_MAC_FIELDS)
            self.assertNotIn("payload", authorization["commandMacFields"])
            self.assertIn("clientSlot", authorization["commandMacFields"])
            sensitivity = data["sessionSecurityTestMatrix"]["macFieldSensitivityCases"]
            self.assertEqual(set(sensitivity["session_hello"]), set(checker.EXPECTED_SESSION_HELLO_MAC_FIELDS))
            self.assertEqual(set(sensitivity["command"]), set(checker.EXPECTED_COMMAND_MAC_FIELDS))
            self.assertTrue(all(sensitivity["session_hello"].values()))
            self.assertTrue(all(sensitivity["command"].values()))

    def test_raw_json_line_size_guard_is_exercised(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "host-authority-n-slot-session-security-smoke-proof.json"
            builder.build_bundle(bundle)
            data = checker.read_json(bundle)

            oversized = next(
                row
                for row in data["sessionSecurityTestMatrix"]["rejectedSecurityCases"]
                if row["reason"] == "oversized-message"
            )

            self.assertEqual(oversized["jsonLineByteMode"], "raw-line-before-json-parse")
            self.assertGreater(oversized["rawJsonLineBytes"], checker.EXPECTED_MAX_MESSAGE_BYTES)
            self.assertTrue(data["sessionSecurityTestMatrix"]["proofFlags"]["rawJsonLineByteLimitRejected"])

    def test_rejects_runtime_and_online_overclaims(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "host-authority-n-slot-session-security-smoke-proof.json"
            builder.build_bundle(bundle)
            data = checker.read_json(bundle)

            data["transport"]["multiHostLanClaim"] = True
            checker.write_json(bundle, data)

            with self.assertRaises(checker.HostAuthorityNSlotSessionSecuritySmokeProofError):
                checker.validate_bundle(bundle)


if __name__ == "__main__":
    unittest.main(verbosity=2)
