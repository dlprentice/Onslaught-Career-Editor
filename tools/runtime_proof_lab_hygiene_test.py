#!/usr/bin/env python3
"""Unit tests for runtime proof lab hygiene (no live BEA)."""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest


TOOLS = Path(__file__).resolve().parent
MODULE_PATH = TOOLS / "runtime_proof_lab_hygiene.py"


def load_module():
    spec = importlib.util.spec_from_file_location("runtime_proof_lab_hygiene", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class RuntimeProofLabHygieneTests(unittest.TestCase):
    def setUp(self) -> None:
        self.m = load_module()

    def test_strip_removes_profile_and_runner_junk_keeps_compact_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            auth = Path(tmp) / "auth"
            pair = auth / "pair"
            attempt = pair / "attempt-01"
            evidence = attempt / "evidence"
            profile = attempt / "profile-app-config" / "OnslaughtCareerEditor" / "GameProfiles" / "x"
            runner_bin = pair / "runner" / "bin" / "Release"
            runner_obj = pair / "runner" / "obj"
            evidence.mkdir(parents=True)
            profile.mkdir(parents=True)
            runner_bin.mkdir(parents=True)
            runner_obj.mkdir(parents=True)
            (profile / "BEA.exe").write_bytes(b"fake-game" * 1000)
            (profile / "data" / "big.bin").parent.mkdir(parents=True, exist_ok=True)
            (profile / "data" / "big.bin").write_bytes(b"\0" * 10_000)
            raw = evidence / "walker-trajectory-raw.json"
            metrics = evidence / "walker-trajectory-metrics.json"
            status = evidence / "observer-status.json"
            closeout = evidence / "walker-trajectory-attempt-closeout.json"
            for path, payload in (
                (raw, {"samples": {}}),
                (metrics, {"accepted": True}),
                (status, {"failure": ""}),
                (closeout, {"attempt": 1}),
            ):
                path.write_text(json.dumps(payload), encoding="utf-8")
            (runner_bin / "LiveSafeCopySmoke.dll").write_bytes(b"dll")
            (runner_obj / "cache").write_text("x", encoding="utf-8")

            result = self.m.strip_pair_private_root(
                pair, authorized_private_root=auth
            )

            self.assertFalse((attempt / "profile-app-config").exists())
            self.assertFalse((pair / "runner" / "bin").exists())
            self.assertFalse((pair / "runner" / "obj").exists())
            self.assertTrue(raw.is_file())
            self.assertTrue(metrics.is_file())
            self.assertTrue(status.is_file())
            self.assertTrue(closeout.is_file())
            self.assertTrue(result["attempts"])
            self.assertTrue(result["attempts"][0]["removed"])
            self.assertIn("walker-trajectory-raw.json", result["attempts"][0]["compactEvidenceNames"])
            self.assertFalse(result["attempts"][0]["profileAppConfigPresentAfter"])

    def test_strip_refuses_path_outside_authorized_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            auth = Path(tmp) / "auth"
            auth.mkdir()
            outside = Path(tmp) / "outside" / "attempt-01"
            outside.mkdir(parents=True)
            with self.assertRaisesRegex(ValueError, "escaped"):
                self.m.strip_bulky_attempt_tree(
                    outside, authorized_private_root=auth
                )

    def test_durable_lab_reuse_copies_under_authorized_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            auth = Path(tmp) / "auth"
            base = auth / "lab-base"
            dest = auth / "pair" / "attempt-01" / "profile-app-config"
            base.mkdir(parents=True)
            (base / "BEA.exe").write_bytes(b"lab-copy")
            (base / "defaultoptions.bea").write_text("opts", encoding="utf-8")
            receipt = self.m.materialize_from_durable_lab_base(
                dest, base, authorized_private_root=auth
            )
            self.assertTrue((dest / "BEA.exe").is_file())
            self.assertEqual((dest / "BEA.exe").read_bytes(), b"lab-copy")
            self.assertEqual(receipt["fileCount"], 2)
            with self.assertRaisesRegex(ValueError, "already exists"):
                self.m.materialize_from_durable_lab_base(
                    dest, base, authorized_private_root=auth
                )

    def test_compact_evidence_marker_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            auth = Path(tmp) / "auth"
            auth.mkdir()
            good = auth / "metrics.json"
            # wrong name
            good.write_text("{}", encoding="utf-8")
            self.assertFalse(self.m.compact_evidence_present([good]))
            marked = auth / "walker-trajectory-metrics.json"
            marked.write_text("{}", encoding="utf-8")
            self.assertTrue(self.m.compact_evidence_present([marked]))


if __name__ == "__main__":
    unittest.main()
