#!/usr/bin/env python3
"""Focused tests for level-854 fire/input-to-weapon-handoff proof semantics."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import build_winui_original_binary_level854_fire_handoff_bundle as builder
import winui_safe_copy_online_level854_fire_handoff_check as checker


class Level854FireHandoffCheckerTests(unittest.TestCase):
    def test_detects_retryable_foreground_abort_artifact(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            path = Path(tmp) / "live-safe-copy-runtime-smoke.json"
            path.write_text(
                json.dumps(
                    {
                        "schemaVersion": "winui-safe-copy-live-runtime-smoke.v1",
                        "input": [
                            {
                                "status": "failed",
                                "stderr": builder.FOREGROUND_CHANGED_TOKEN,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            self.assertTrue(builder.runtime_artifact_has_foreground_abort(path))

    def test_live_bundle_retries_foreground_abort_before_promotion(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            artifact_root = Path(tmp) / "level854-fire-handoff-live-fixture"
            output_path = Path(tmp) / "level854-fire-handoff-proof.json"

            def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                current_root = Path(command[command.index("--artifact-root") + 1])
                current_root.mkdir(parents=True, exist_ok=True)
                if fake_run.call_count == 0:
                    (current_root / "live-safe-copy-runtime-smoke.json").write_text(
                        json.dumps({"input": [{"status": "failed", "stderr": builder.FOREGROUND_CHANGED_TOKEN}]}),
                        encoding="utf-8",
                    )
                    fake_run.call_count += 1
                    return subprocess.CompletedProcess(command, 2, stdout="", stderr="")
                (current_root / "live-safe-copy-runtime-smoke.json").write_text(
                    json.dumps({"input": [{"status": "sent"}]}),
                    encoding="utf-8",
                )
                fake_run.call_count += 1
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            fake_run.call_count = 0  # type: ignore[attr-defined]
            with (
                mock.patch.object(builder.subprocess, "run", side_effect=fake_run) as run_mock,
                mock.patch.object(builder, "build_bundle_from_runtime", return_value={"runtimeEvidence": {}}),
            ):
                bundle = builder.build_live_bundle(artifact_root, output_path, exe_override=Path("BEA.exe"))
            self.assertEqual(run_mock.call_count, 2)
            self.assertEqual(bundle["runtimeEvidence"]["liveSmokeAttemptCount"], 2)
            self.assertTrue(bundle["runtimeEvidence"]["liveSmokeRetriedAfterForegroundAbort"])

    def test_live_bundle_retries_basic_handoff_pointer_chain_miss_before_promotion(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            artifact_root = Path(tmp) / "level854-fire-handoff-live-fixture"
            output_path = Path(tmp) / "level854-fire-handoff-proof.json"

            def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                current_root = Path(command[command.index("--artifact-root") + 1])
                current_root.mkdir(parents=True, exist_ok=True)
                (current_root / "live-safe-copy-runtime-smoke.json").write_text(
                    json.dumps({"input": [{"status": "sent"}]}),
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

            build_results = [
                builder.Level854FireHandoffBuildError(builder.POINTER_CHAIN_MISSING_TOKEN),
                {"runtimeEvidence": {}},
            ]
            with (
                mock.patch.object(builder.subprocess, "run", side_effect=fake_run) as run_mock,
                mock.patch.object(builder, "runtime_artifact_has_basic_fire_handoff", return_value=True),
                mock.patch.object(builder, "build_bundle_from_runtime", side_effect=build_results),
            ):
                bundle = builder.build_live_bundle(artifact_root, output_path, exe_override=Path("BEA.exe"))

            self.assertEqual(run_mock.call_count, 2)
            self.assertEqual(bundle["runtimeEvidence"]["liveSmokeAttemptCount"], 2)
            self.assertFalse(bundle["runtimeEvidence"]["liveSmokeRetriedAfterForegroundAbort"])
            self.assertTrue(bundle["runtimeEvidence"]["liveSmokeRetriedAfterPointerChainMiss"])

    def test_live_bundle_does_not_retry_non_foreground_failure(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            artifact_root = Path(tmp) / "level854-fire-handoff-live-fixture"
            output_path = Path(tmp) / "level854-fire-handoff-proof.json"

            def fake_run(command: list[str], **_: object) -> subprocess.CompletedProcess[str]:
                current_root = Path(command[command.index("--artifact-root") + 1])
                current_root.mkdir(parents=True, exist_ok=True)
                (current_root / "live-safe-copy-runtime-smoke.json").write_text(
                    json.dumps({"input": [{"status": "failed", "stderr": "different failure"}]}),
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(command, 2, stdout="", stderr="")

            with mock.patch.object(builder.subprocess, "run", side_effect=fake_run) as run_mock:
                with self.assertRaises(builder.Level854FireHandoffBuildError):
                    builder.build_live_bundle(artifact_root, output_path, exe_override=Path("BEA.exe"))
            self.assertEqual(run_mock.call_count, 1)

    def test_accepts_button19_same_window_fire_handoff(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            path = checker.make_fixture(Path(tmp))
            summary = checker.validate_bundle(path, allow_fixture=True)
            self.assertEqual(summary["button18DispatchCount"], 0)
            self.assertGreater(summary["button19DispatchCount"], 0)
            self.assertGreater(summary["sameWindowInputFireHandoffWindowCount"], 0)
            self.assertGreater(summary["sameWindowFireBurstPointerChainWindowCount"], 0)
            self.assertIn("04990000", summary["fireBurstPointerChainContexts"])
            self.assertFalse(summary["baseOnlineMultiplayerReady"])

    def test_parse_cdb_log_accepts_checksum_warning_split_render_printf(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            log_path = Path(tmp) / "windbg.log"
            hook_lines = [
                f"FIRE_HANDOFF_HOOK_TARGET name={target['name']} address={target['address']} category={target['category']}"
                for target in builder.TARGETS
            ]
            log_path.write_text(
                "\n".join(
                    hook_lines
                    + [
                        "FIRE_HANDOFF_HIT name=CGame__Render this=*** WARNING: Unable to verify checksum for BEA.exe",
                        "008a9a98 players=2 level=854 horizSplit=1 p0=0467c090 p1=04693890 cam0=04111111 cam1=04222222 world=00855090",
                    ]
                )
                + "\n",
                encoding="utf-8",
            )

            parsed = builder.parse_cdb_log(log_path)

            self.assertEqual(parsed["render"]["this"], "008a9a98")
            self.assertEqual(parsed["render"]["players"], 2)
            self.assertEqual(parsed["render"]["level"], 854)

    def test_rejects_missing_button19_dispatch(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            with self.assertRaises(builder.Level854FireHandoffBuildError):
                checker.make_fixture(Path(tmp), no_button19=True)

    def test_rejects_button18_overclaim(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            with self.assertRaises(builder.Level854FireHandoffBuildError):
                checker.make_fixture(Path(tmp), button18_dispatch=True)

    def test_rejects_input_without_direct_fire_or_burst_handoff(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        for kwargs in ({"no_direct_fire": True}, {"no_burst": True}):
            with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
                with self.assertRaises(builder.Level854FireHandoffBuildError):
                    checker.make_fixture(Path(tmp), **kwargs)

    def test_rejects_direct_fire_and_burst_without_pointer_correlation(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            with self.assertRaises(builder.Level854FireHandoffBuildError):
                checker.make_fixture(Path(tmp), mismatched_burst_context=True)

    def test_records_pointer_correlation_without_event_order_as_non_promoted(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            path = checker.make_fixture(Path(tmp), unordered_fire_burst_events=True)
            summary = checker.validate_bundle(path, allow_fixture=True)
            self.assertGreater(summary["sameWindowFireBurstPointerChainWindowCount"], 0)
            self.assertEqual(summary["sameWindowOrderedFireBurstPointerChainWindowCount"], 0)
            self.assertFalse(summary["sameWindowOrderedFireBurstPointerChainObserved"])

    def test_rejects_wait_window_button_dispatch(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            with self.assertRaises(builder.Level854FireHandoffBuildError):
                checker.make_fixture(Path(tmp), wait_window_button=True)

    def test_rejects_external_cdb_log_and_wrong_command_file(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        for kwargs in ({"external_cdb_log": True}, {"wrong_command_file": True}):
            with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
                with self.assertRaises(builder.Level854FireHandoffBuildError):
                    checker.make_fixture(Path(tmp), **kwargs)

    def test_rejects_background_window_message_input(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            path = checker.make_fixture(Path(tmp), background_window_messages=True)
            with self.assertRaises(checker.Level854FireHandoffError):
                checker.validate_bundle(path, allow_fixture=True)

    def test_rejects_online_or_round_projectile_overclaims(self) -> None:
        builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
        for section, key in (
            ("nonClaims", "baseOnlineMultiplayerReady"),
            ("nonClaims", "nativeBeaNetcodeProof"),
            ("nonClaims", "roundProjectileCausalityProof"),
            ("slotBoundary", "activeP3P4OriginalBinaryGameplayProof"),
        ):
            with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
                path = checker.make_fixture(Path(tmp))
                payload = json.loads(path.read_text(encoding="utf-8"))
                payload[section][key] = True
                path.write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaises(checker.Level854FireHandoffError):
                    checker.validate_bundle(path, allow_fixture=True)

    def test_rejects_public_text_overclaim_tokens(self) -> None:
        good_text = " ".join(checker.PUBLIC_REQUIRED_FALSE_TOKENS)
        checker.require_public_claim_tokens(good_text, "fixture")
        with self.assertRaises(checker.Level854FireHandoffError):
            checker.require_public_claim_tokens(
                good_text + " button18RuntimeDispatchObserved=true",
                "fixture",
            )

    def test_rejects_raw_runtime_identity_in_public_json(self) -> None:
        checker.require_public_json_release_boundary(
            {
                "runtimeEvidence": {
                    "p1p2PointersDistinct": True,
                    "exactPidCdbObserverProven": True,
                },
                "releaseBoundary": {
                    "rawRuntimePointerPublishedInPublicDocs": False,
                    "rawRuntimePidPublishedInPublicDocs": False,
                },
            }
        )
        with self.assertRaises(checker.Level854FireHandoffError):
            checker.require_public_json_release_boundary(
                {
                    "runtimeEvidence": {
                        "p1Pointer": "0430aff0",
                        "p1p2PointersDistinct": True,
                    }
                }
            )

    def test_rejects_private_level854_fire_tools_in_public_allowlist(self) -> None:
        classification = "\n".join(
            list(checker.PUBLIC_RELEASE_ALLOW_ROWS) + list(checker.PRIVATE_RELEASE_DENY_ROWS)
        )
        public_allowlist = "\n".join(
            list(checker.PUBLIC_RELEASE_ALLOW_ROWS)
            + ["tools/winui_safe_copy_online_level854_fire_handoff_check.py\tR4_DENY"]
        )
        private_inventory = "\n".join(checker.PRIVATE_RELEASE_DENY_ROWS)
        release_profile = "\n".join(row.split("\t", 1)[0] for row in checker.PRIVATE_RELEASE_DENY_ROWS)
        with self.assertRaises(checker.Level854FireHandoffError):
            checker.require_release_boundaries(
                classification,
                public_allowlist,
                private_inventory,
                release_profile,
            )


if __name__ == "__main__":
    unittest.main()
