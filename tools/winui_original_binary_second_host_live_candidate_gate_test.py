#!/usr/bin/env python3
"""Tests for explicit second-host live/candidate gate wrappers."""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import winui_original_binary_second_host_live_candidate_gate as gate
import winui_safe_copy_online_second_host_command_source_check as command_source
import winui_safe_copy_online_second_host_runtime_causality_check as runtime_causality


class SecondHostLiveCandidateGateTests(unittest.TestCase):
    def test_missing_command_source_env_fails_closed(self) -> None:
        with self.assertRaises(gate.LiveCandidateGateError) as caught:
            gate.validate_command_source_live_candidate(env={})

        message = str(caught.exception)
        self.assertIn(gate.COMMAND_SOURCE_ENV, message)
        self.assertIn("required", message)

    def test_missing_runtime_causality_env_fails_closed(self) -> None:
        with self.assertRaises(gate.LiveCandidateGateError) as caught:
            gate.validate_runtime_causality_candidate(env={})

        message = str(caught.exception)
        self.assertIn(gate.RUNTIME_CAUSALITY_ENV, message)
        self.assertIn("required", message)

    def test_command_source_fixture_is_rejected_as_live_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fixture_path = command_source.make_bundle_fixture(
                Path(tmp),
                include_security_hardening=True,
                security_hardening_evidence_mode="live-server-client-transcript",
                source_safety_evidence_mode="local-preflight-computed",
                listener_evidence_mode="live-server-socket-receipt",
            )

            with self.assertRaises(gate.LiveCandidateGateError):
                gate.validate_command_source_live_candidate(path=fixture_path)

    def test_nested_validator_error_redacts_absolute_candidate_paths(self) -> None:
        private_path = Path(r"C:\Users\david\private-proof-root\candidate.json")
        leaked_path = Path(r"C:\Users\david\private-proof-root\missing-private-lan-proof.json")
        with mock.patch.object(
            gate.command_source,
            "validate_bundle",
            side_effect=RuntimeError(f"referenced private LAN proof is missing: {leaked_path}"),
        ):
            with self.assertRaises(gate.LiveCandidateGateError) as caught:
                gate.validate_command_source_live_candidate(path=private_path)

        message = str(caught.exception)
        self.assertNotIn(str(private_path), message)
        self.assertNotIn(str(leaked_path), message)
        self.assertNotIn(r"C:\Users\david", message)
        self.assertIn("<redacted-private-path>", message)

    def test_runtime_self_test_candidate_is_rejected_as_runtime_candidate(self) -> None:
        runtime_causality.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=runtime_causality.PRIVATE_PROOF_ROOT) as tmp:
            fixture_path = runtime_causality.write_file_backed_self_test_candidate(Path(tmp))

            with self.assertRaises(gate.LiveCandidateGateError):
                gate.validate_runtime_causality_candidate(path=fixture_path)

    def test_host_join_candidate_requires_matching_command_and_invitation_hashes(self) -> None:
        command_summary = {
            "acceptedLiveSecondHostCommandSourceProof": True,
            "acceptedSecondHostCommandRequestPayloadSha256": "a" * 64,
            "secondHostInvitationLifecycleSha256": "b" * 64,
            "baseOnlineMultiplayerReady": False,
            "hostHelperInputSent": False,
            "gameInputSentBySecondHostClient": False,
        }
        runtime_summary = {
            "acceptedLiveSecondHostRuntimeDeliveryProof": True,
            "runtimeInputDerivedFromSecondHostCommandSource": True,
            "runtimeDrivenBySecondHostCommandSource": True,
            "rawArtifactReceiptsRecomputed": True,
            "acceptedSecondHostCommandRequestPayloadSha256": "c" * 64,
            "secondHostInvitationLifecycleSha256": "b" * 64,
            "hostJoinControlsMayBeEnabled": False,
            "baseOnlineMultiplayerReady": False,
        }

        with (
            mock.patch.object(gate, "validate_command_source_live_candidate", return_value=command_summary),
            mock.patch.object(gate, "validate_runtime_causality_candidate", return_value=runtime_summary),
            self.assertRaises(gate.LiveCandidateGateError),
        ):
            gate.validate_host_join_candidate(command_path=Path("command.json"), runtime_path=Path("runtime.json"))

    def test_host_join_candidate_accepts_matching_private_candidate_summaries_without_enabling_host_join(self) -> None:
        command_summary = {
            "acceptedLiveSecondHostCommandSourceProof": True,
            "acceptedSecondHostCommandRequestPayloadSha256": "a" * 64,
            "secondHostInvitationLifecycleSha256": "b" * 64,
            "baseOnlineMultiplayerReady": False,
            "hostHelperInputSent": False,
            "gameInputSentBySecondHostClient": False,
        }
        runtime_summary = {
            "acceptedLiveSecondHostRuntimeDeliveryProof": True,
            "runtimeInputDerivedFromSecondHostCommandSource": True,
            "runtimeDrivenBySecondHostCommandSource": True,
            "rawArtifactReceiptsRecomputed": True,
            "acceptedSecondHostCommandRequestPayloadSha256": "a" * 64,
            "secondHostInvitationLifecycleSha256": "b" * 64,
            "hostJoinControlsMayBeEnabled": False,
            "baseOnlineMultiplayerReady": False,
        }

        with (
            mock.patch.object(gate, "validate_command_source_live_candidate", return_value=command_summary),
            mock.patch.object(gate, "validate_runtime_causality_candidate", return_value=runtime_summary),
        ):
            summary = gate.validate_host_join_candidate(command_path=Path("command.json"), runtime_path=Path("runtime.json"))

        self.assertTrue(summary["acceptedLiveSecondHostCommandSourceProof"])
        self.assertTrue(summary["acceptedLiveSecondHostRuntimeDeliveryProof"])
        self.assertTrue(summary["candidateAcceptedLiveSecondHostCommandSourceProof"])
        self.assertTrue(summary["candidateAcceptedLiveSecondHostRuntimeDeliveryProof"])
        self.assertTrue(summary["hostJoinPromotionGateRequired"])
        self.assertFalse(summary["hostJoinControlsMayBeEnabled"])
        self.assertFalse(summary["baseOnlineMultiplayerReady"])
        self.assertFalse(summary["playerReadyOnlineMultiplayer"])
        self.assertEqual(summary["gateScope"], "private-candidate-validation-not-host-join-enablement")

    def test_public_claim_boundary_rejects_true_live_booleans_in_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "public-doc.md"
            path.write_text(
                "Online play is not available in this release. "
                "private-candidate-validation-not-host-join-enablement "
                "Host/Join remains disabled. "
                "hostJoinControlsMayBeEnabled=false "
                "baseOnlineMultiplayerReady=false "
                "acceptedLiveSecondHostCommandSourceProof=true\n",
                encoding="utf-8",
            )

            with self.assertRaises(gate.LiveCandidateGateError) as caught:
                gate.validate_public_claim_boundary([path])

        self.assertIn("must not publish online proof/readiness as true", str(caught.exception))

    def test_public_claim_boundary_rejects_json_style_true_live_booleans_in_docs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "public-doc.md"
            path.write_text(
                "Online play is not available in this release. "
                "private-candidate-validation-not-host-join-enablement "
                "Host/Join remains disabled. "
                "hostJoinControlsMayBeEnabled=false "
                "baseOnlineMultiplayerReady=false "
                '"acceptedLiveSecondHostRuntimeCausalityProof": true\n',
                encoding="utf-8",
            )

            with self.assertRaises(gate.LiveCandidateGateError) as caught:
                gate.validate_public_claim_boundary([path])

        self.assertIn("must not publish online proof/readiness as true", str(caught.exception))

    def test_public_claim_boundary_rejects_true_online_readiness_booleans_in_docs(self) -> None:
        fields = (
            "hostJoinControlsMayBeEnabled",
            "baseOnlineMultiplayerReady",
            "multiHostLanPlayProof",
            "multiHostLanProof",
            "playerReadyOnlineMultiplayer",
            "publicMatchmakingProof",
            "nativeBeaNetcodeProof",
            "secondPhysicalHostProof",
            "activeP3P4OriginalBinaryGameplayProof",
        )
        for field in fields:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "public-doc.md"
                path.write_text(
                    "Online play is not available in this release. "
                    "private-candidate-validation-not-host-join-enablement "
                    "Host/Join remains disabled. "
                    "hostJoinControlsMayBeEnabled=false "
                    "baseOnlineMultiplayerReady=false "
                    f'"{field}": true\n',
                    encoding="utf-8",
                )

                with self.assertRaises(gate.LiveCandidateGateError) as caught:
                    gate.validate_public_claim_boundary([path])

                self.assertIn("must not publish online proof/readiness as true", str(caught.exception))

    def test_public_claim_boundary_rejects_prose_host_join_ready_even_when_other_doc_has_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            good_path = Path(tmp) / "good-boundary.md"
            ambiguous_path = Path(tmp) / "ambiguous-ready.md"
            good_path.write_text(
                "Online play is not available in this release. "
                "private-candidate-validation-not-host-join-enablement "
                "Host/Join remains disabled. "
                "hostJoinControlsMayBeEnabled=false "
                "baseOnlineMultiplayerReady=false\n",
                encoding="utf-8",
            )
            ambiguous_path.write_text(
                "The next build is Host/Join ready and ready to host online sessions. "
                "The app is player-ready online multiplayer.\n",
                encoding="utf-8",
            )

            with self.assertRaises(gate.LiveCandidateGateError) as caught:
                gate.validate_public_claim_boundary([good_path, ambiguous_path])

        self.assertIn("must not publish Host/Join readiness prose", str(caught.exception))

    def test_public_claim_boundary_accepts_release_unavailable_tokens(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "public-doc.md"
            path.write_text(
                "Online play is not available in this release. "
                "private-candidate-validation-not-host-join-enablement "
                "Host/Join remains disabled. "
                "hostJoinControlsMayBeEnabled=false "
                "baseOnlineMultiplayerReady=false "
                "acceptedLiveSecondHostCommandSourceProof=false "
                "acceptedLiveSecondHostRuntimeDeliveryProof=false "
                "This is not second-host LAN proof, public matchmaking, native BEA netcode, or player-ready online multiplayer. "
                "This does not prove player-ready online multiplayer.\n",
                encoding="utf-8",
            )

            summary = gate.validate_public_claim_boundary([path])

        self.assertEqual(summary["gateScope"], "public-doc-candidate-claim-boundary")
        self.assertEqual(summary["checkedFileCount"], 1)

    def test_public_claim_boundary_default_discovers_readiness_and_lore_docs(self) -> None:
        paths = gate.discover_public_claim_boundary_docs()

        self.assertIn(
            gate.ROOT / "release" / "readiness" / "winui_original_binary_second_host_runtime_causality_raw_material_plan_2026-06-22.md",
            paths,
        )
        self.assertIn(gate.ROOT / "lore-book" / "CURRENT_CAPABILITIES.md", paths)


if __name__ == "__main__":
    unittest.main(verbosity=2)
