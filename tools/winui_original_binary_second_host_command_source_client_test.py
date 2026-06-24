#!/usr/bin/env python3
"""Tests for the second-host command-source client helper."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import winui_original_binary_second_host_command_source_client as client
import winui_safe_copy_online_second_host_command_source_check as checker


class SecondHostCommandSourceClientTests(unittest.TestCase):
    def test_identity_preflight_hashes_source_roots_without_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copied = root / "client-copied-profile"
            installed = root / "client-installed-game"
            (copied / "data").mkdir(parents=True)
            installed.mkdir()
            (copied / "BEA.exe").write_bytes(b"client copied exe")
            (copied / "data" / "base_res_PC.aya").write_bytes(b"client copied resource")
            (installed / "BEA.exe").write_bytes(b"client installed exe")

            summary = client.build_identity_preflight_summary(
                client_copied_profile_root=copied,
                client_installed_game_root=installed,
            )
            serialized = json.dumps(summary, sort_keys=True)

            self.assertEqual(summary["schemaVersion"], "winui-original-binary-second-host-client-preflight.v1")
            self.assertEqual(summary["scope"], "second-host-client-identity-source-safety-preflight-not-command-source-proof")
            self.assertTrue(checker.is_hex64(str(summary["clientIdentityFingerprint"])))
            self.assertIn(str(summary["clientIdentityFingerprint"]), str(summary["copyForServerArgument"]))
            self.assertNotIn("--client-runtime-host-kind", str(summary["copyForClientRuntimeHostKindArgument"]))
            self.assertIn("omit", str(summary["copyForClientRuntimeHostKindArgument"]).lower())
            self.assertIn("attempt-only", str(summary["copyForClientRuntimeHostKindArgument"]).lower())
            self.assertEqual(summary["clientSourceSafety"]["sourceEvidenceMode"], "local-preflight-computed")
            self.assertEqual(summary["clientSourceSafety"]["copiedProfileFileCount"], 2)
            self.assertEqual(summary["clientSourceSafety"]["installedGameFileCount"], 1)
            self.assertFalse(summary["privateProofCreated"])
            self.assertFalse(summary["gameInputSent"])
            self.assertFalse(summary["baseOnlineMultiplayerReady"])
            self.assertFalse(summary["acceptedLiveSecondHostCommandSourceProof"])
            self.assertFalse(summary["acceptedLiveSecondHostRuntimeDeliveryProof"])
            self.assertNotIn(str(copied), serialized)
            self.assertNotIn(str(installed), serialized)

    def test_identity_preflight_rejects_partial_root_inputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(Exception):
                client.build_identity_preflight_summary(client_copied_profile_root=Path(tmp))

    def test_manual_vm_runtime_kind_remains_operator_supplied(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            copied = root / "client-copied-profile"
            installed = root / "client-installed-game"
            (copied / "data").mkdir(parents=True)
            installed.mkdir()
            (copied / "BEA.exe").write_bytes(b"client copied exe")
            (copied / "data" / "base_res_PC.aya").write_bytes(b"client copied resource")
            (installed / "BEA.exe").write_bytes(b"client installed exe")

            summary = client.build_identity_preflight_summary(
                client_copied_profile_root=copied,
                client_installed_game_root=installed,
                client_runtime_host_kind="vm-guest",
            )

            self.assertEqual(summary["machineIdentity"]["runtimeHostKind"], "vm-guest")
            self.assertEqual(summary["machineIdentity"]["runtimeHostKindSource"], "operator-supplied-runtime-host-kind")


if __name__ == "__main__":
    unittest.main(verbosity=2)
