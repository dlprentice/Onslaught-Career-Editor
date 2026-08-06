#!/usr/bin/env python3
"""Focused fail-closed tests for the one-shot live Ghidra owner."""

from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import ghidra_global_init515_live_promotion as live


class FakeProcess:
    def __init__(self, output: bytes, waits: list[object]) -> None:
        self.stdout = io.BytesIO(output)
        self._waits = list(waits)
        self.killed = False

    def wait(self, timeout: int) -> int:
        value = self._waits.pop(0)
        if isinstance(value, BaseException):
            raise value
        return int(value)

    def kill(self) -> None:
        self.killed = True


def fake_authority(root: Path) -> live.Authority:
    files = {}
    for name in (
        "formal", "manifest", "base-functions", "base-program", "pre-symbols",
        "post-functions", "post-program", "post-symbols", "envelope", "inventory",
        "symbols", "formal-owner", "lineage-owner", "campaign-owner", "python",
        "headless", "java",
    ):
        path = root / name
        path.write_bytes(name.encode())
        files[name] = path
    return live.Authority(
        formal_ready=files["formal"],
        manifest=files["manifest"],
        base_functions=files["base-functions"],
        base_program=files["base-program"],
        reference_pre_symbols=files["pre-symbols"],
        reference_post_functions=files["post-functions"],
        reference_post_program=files["post-program"],
        reference_post_symbols=files["post-symbols"],
        envelope_tool=files["envelope"],
        inventory_tool=files["inventory"],
        symbol_tool=files["symbols"],
        formal_owner=files["formal-owner"],
        lineage_owner=files["lineage-owner"],
        campaign_owner=files["campaign-owner"],
        python=files["python"],
        headless=files["headless"],
        java=files["java"],
    )


class LiveOwnerTests(unittest.TestCase):
    def test_parser_exposes_only_three_fixed_commands(self) -> None:
        parser = live.build_parser()
        action = next(action for action in parser._actions if action.dest == "command")
        self.assertEqual({"prepare", "promote", "recover-status"}, set(action.choices))
        for command in action.choices:
            self.assertEqual([], action.choices[command]._actions[1:])
        with self.assertRaises(SystemExit):
            parser.parse_args(["promote", "--project", "elsewhere"])

    def test_live_target_and_mutation_argv_are_not_user_selectable(self) -> None:
        self.assertEqual(Path(r"C:\Users\david\Ghidra\Projects"), live.LIVE_PROJECT_ROOT)
        self.assertEqual(515, live.TARGET_COUNT)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            authority = fake_authority(root)
            output = root / "output.tsv"
            ready = root / "ready.json"
            argv = live.envelope.envelope_argv(
                authority.headless,
                live.LIVE_PROJECT_ROOT,
                authority.envelope_tool,
                authority.manifest,
                live.MANIFEST_SHA256,
                live.TARGET_COUNT,
                output,
                ready,
                "apply",
            )
        joined = " ".join(argv)
        self.assertNotIn("-readOnly", joined)
        self.assertIn(str(live.LIVE_PROJECT_ROOT), joined)
        self.assertIn(" apply", joined)

    def test_exact_file_rejects_one_byte_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "fixed.bin"
            path.write_bytes(b"fixed")
            good = live.sha256_file(path)
            self.assertEqual(path.resolve(), live.exact_file(path, good, "fixed"))
            path.write_bytes(b"fixee")
            with self.assertRaisesRegex(live.LivePromotionError, "SHA-256 differs"):
                live.exact_file(path, good, "fixed")

    def test_project_snapshot_rejects_hardlinked_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "BEA.gpr").write_bytes(b"")
            rep = root / "BEA.rep"
            rep.mkdir()
            first = rep / "first.bin"
            second = rep / "second.bin"
            first.write_bytes(b"payload")
            os.link(first, second)
            with self.assertRaisesRegex(live.LivePromotionError, "hardlinked"):
                live.project_snapshot(root)

    def test_quiescence_refuses_java_and_native_lock_before_file_probe(self) -> None:
        with patch.object(
            live, "running_java_processes", return_value=[{"pid": 7, "name": "java.exe"}]
        ), self.assertRaisesRegex(live.LivePromotionError, "Java/Ghidra"):
            live.assert_quiescent(Path("unused"))

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "BEA.lock").write_bytes(b"lock")
            with patch.object(live, "running_java_processes", return_value=[]), self.assertRaisesRegex(
                live.LivePromotionError, "native Ghidra project lock"
            ):
                live.assert_quiescent(root)

    def test_contained_runner_precreates_and_preserves_log(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "work").mkdir()
            observed = []

            def spawn(argv: list[str], cwd: Path, environment: dict[str, str]):
                observed.append((root / "runs/test/headless.partial.log").is_file())
                return FakeProcess(b"partial output\n", [0]), 41

            closed = []
            result, text = live.run_contained(
                session_root=root,
                run_id="test",
                argv=["tool", "arg"],
                cwd=root / "work",
                environment={"SAFE": "1"},
                timeout_seconds=5,
                spawn=spawn,
                close_handle=closed.append,
            )

            self.assertEqual([True], observed)
            self.assertEqual([41], closed)
            self.assertEqual("COMPLETED", result["status"])
            self.assertEqual("partial output\n", text)
            self.assertTrue((root / "runs/test/run.json").is_file())
            self.assertTrue((root / "runs/test/headless.partial.log").is_file())

    def test_timeout_preserves_partial_log_and_closes_job(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "work").mkdir()
            timeout = subprocess.TimeoutExpired(["tool"], 1)
            process = FakeProcess(b"before timeout\n", [timeout, -1])
            closed = []
            result, text = live.run_contained(
                session_root=root,
                run_id="timeout",
                argv=["tool"],
                cwd=root / "work",
                environment={},
                timeout_seconds=1,
                spawn=lambda *_: (process, 99),
                close_handle=closed.append,
            )
            self.assertEqual("TIMED_OUT", result["status"])
            self.assertEqual([99], closed)
            self.assertIn("before timeout", text)
            self.assertTrue((root / "runs/timeout/run.json").is_file())

    def test_apply_intent_precedes_one_runner_call_and_forbids_retry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "work").mkdir()
            calls = []

            def runner(**kwargs):
                calls.append(kwargs)
                self.assertTrue((root / "attempt.started.json").is_file())
                return {"status": "COMPLETED", "exitCode": 0}, "ok"

            intent, _process, _text = live.execute_apply_once(
                promotion_root=root,
                attempt={"schema": live.ATTEMPT_SCHEMA},
                argv=["fixed-mutator"],
                cwd=root / "work",
                environment={},
                runner=runner,
                quiescence=lambda: {},
            )
            self.assertTrue(intent.is_file())
            self.assertEqual(1, len(calls))
            with self.assertRaisesRegex(live.LivePromotionError, "retry is forbidden"):
                live.execute_apply_once(
                    promotion_root=root,
                    attempt={"schema": live.ATTEMPT_SCHEMA},
                    argv=["fixed-mutator"],
                    cwd=root / "work",
                    environment={},
                    runner=runner,
                    quiescence=lambda: {},
                )
            self.assertEqual(1, len(calls))

    def test_classification_is_exact_pre_post_or_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            authority = fake_authority(root)
            functions = root / "functions.tsv"
            program = root / "program.tsv"
            symbols = root / "symbols.tsv"
            symbols_ready = root / "symbols.ready.json"
            functions.write_bytes(b"pre-functions")
            program.write_bytes(b"pre-program")
            symbols.write_bytes(b"pre-symbols")
            symbols_ready.write_text("{}")

            no_op = patch.multiple(
                live.formal,
                compare_to_base=lambda *args, **kwargs: None,
                validate_base_target_symbols=lambda *args, **kwargs: {},
                validate_applied_inventory=lambda *args, **kwargs: {},
                validate_applied_target_symbols=lambda *args, **kwargs: None,
            )
            with (
                no_op,
                patch.object(live.envelope, "function_rows", return_value=([], {})),
                patch.object(live, "BASE_FUNCTIONS_SHA256", live.sha256_file(functions)),
                patch.object(live, "BASE_PROGRAM_SHA256", live.sha256_file(program)),
                patch.object(live, "PRE_SYMBOLS_SHA256", live.sha256_file(symbols)),
            ):
                pre = live.classify_exports(
                    authority=authority,
                    functions=functions,
                    program=program,
                    symbols=symbols,
                    symbols_ready=symbols_ready,
                    raw_stable=True,
                )
                unstable = live.classify_exports(
                    authority=authority,
                    functions=functions,
                    program=program,
                    symbols=symbols,
                    symbols_ready=symbols_ready,
                    raw_stable=False,
                )
            self.assertEqual(live.ProjectState.PRE, pre["state"])
            self.assertEqual(live.ProjectState.UNKNOWN, unstable["state"])

            functions.write_bytes(b"post-functions")
            program.write_bytes(b"post-program")
            symbols.write_bytes(b"post-symbols")
            with (
                patch.multiple(
                    live.formal,
                    compare_to_base=lambda *args, **kwargs: None,
                    validate_base_target_symbols=lambda *args, **kwargs: {},
                    validate_applied_inventory=lambda *args, **kwargs: {},
                    validate_applied_target_symbols=lambda *args, **kwargs: None,
                ),
                patch.object(live.envelope, "function_rows", return_value=([], {})),
                patch.object(live, "POST_FUNCTIONS_SHA256", live.sha256_file(functions)),
                patch.object(live, "POST_PROGRAM_SHA256", live.sha256_file(program)),
                patch.object(live, "POST_SYMBOLS_SHA256", live.sha256_file(symbols)),
            ):
                post = live.classify_exports(
                    authority=authority,
                    functions=functions,
                    program=program,
                    symbols=symbols,
                    symbols_ready=symbols_ready,
                    raw_stable=True,
                )
            self.assertEqual(live.ProjectState.POST, post["state"])

    def test_existing_promotion_root_blocks_before_any_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            owner = Path(temporary)
            (owner / "promotion").mkdir()
            with self.assertRaisesRegex(live.LivePromotionError, "already exists"):
                live.promote(owner_root=owner)

    def test_verify_prepared_binds_backup_source_to_live_preimage(self) -> None:
        def snapshot(tag: str, root: Path) -> dict[str, object]:
            return {
                "root": str(root.resolve()),
                "fileCount": 1,
                "totalBytes": 1,
                "fileSetSha256": tag * 64,
                "files": [{"path": "BEA.gpr", "bytes": 1, "sha256": tag * 64}],
            }

        with tempfile.TemporaryDirectory() as temporary:
            owner = Path(temporary)
            authority = fake_authority(owner)
            live_preimage = snapshot("a", live.LIVE_PROJECT_ROOT)
            prepared = {
                "schema": live.PREPARED_SCHEMA,
                "status": "READY",
                "preparedAtUtc": "2026-08-03T12:00:00Z",
                "owner": {
                    "path": str(Path(live.__file__).resolve()),
                    "sha256": live.sha256_file(Path(live.__file__).resolve()),
                },
                "mutex": {"name": live.MUTEX_NAME, "abandoned": False},
                "authority": live.authority_summary(authority),
                "reproductions": {
                    "formal": {
                        "run": {},
                        "result": {
                            "verdict": "SURVIVED",
                            "admissibleTargets": live.TARGET_COUNT,
                            "publicationStatus": "READY",
                        },
                    },
                    "lineage": {
                        "run": {},
                        "result": {
                            "status": "READY",
                            "summary": {"rows": live.TARGET_COUNT},
                        },
                    },
                    "campaign": {
                        "run": {},
                        "result": {
                            "generation": 5,
                            "counts": {"functions": 7595, "residuals": 6618},
                        },
                    },
                },
                "livePreimage": live_preimage,
                "firstQuiescence": {
                    "checkedAtUtc": "2026-08-03T11:59:00Z",
                    "javaProcesses": [],
                    "nativeLockAbsent": True,
                    "exclusiveFilesProbed": 1,
                    "projectFileSetSha256": "a" * 64,
                },
                "finalQuiescence": {
                    "checkedAtUtc": "2026-08-03T12:01:00Z",
                    "javaProcesses": [],
                    "nativeLockAbsent": True,
                    "exclusiveFilesProbed": 1,
                    "projectFileSetSha256": "a" * 64,
                },
                "initialObservation": {},
                "finalObservation": {},
                "preBackup": {
                    "expectedState": "PRE",
                    "sourceSnapshot": snapshot("b", live.LIVE_PROJECT_ROOT),
                    "backupRoot": str((owner / "backup").resolve()),
                    "restoreRoot": str((owner / "restore").resolve()),
                },
            }
            (owner / "prepared.ready.json").write_text(
                json.dumps(prepared), encoding="utf-8"
            )
            with (
                patch.object(live, "validate_process_receipt", return_value={}),
                patch.object(
                    live,
                    "validate_observation_receipt",
                    return_value={"rawAfter": live_preimage},
                ),
                self.assertRaisesRegex(
                    live.LivePromotionError, "source snapshot differs"
                ),
            ):
                live.verify_prepared(owner, authority)

    def test_post_state_with_partial_protocol_cannot_publish(self) -> None:
        backup = {"expectedState": live.ProjectState.POST}
        self.assertTrue(
            live.publication_authorized(
                live.ProjectState.POST, {"status": "COMPLETE"}, backup
            )
        )
        self.assertFalse(
            live.publication_authorized(
                live.ProjectState.POST, {"status": "PARTIAL"}, backup
            )
        )
        self.assertFalse(
            live.publication_authorized(
                live.ProjectState.POST, {"status": "COMPLETE"}, None
            )
        )
        self.assertFalse(
            live.publication_authorized(
                live.ProjectState.UNKNOWN, {"status": "COMPLETE"}, backup
            )
        )

    def test_lineage_verifier_count_is_read_from_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            authority = fake_authority(root)
            payloads = {
                "authority-formal": {
                    "verdict": "SURVIVED",
                    "admissibleTargets": live.TARGET_COUNT,
                    "publicationStatus": "READY",
                },
                "authority-lineage": {
                    "status": "READY",
                    "summary": {"rows": live.TARGET_COUNT},
                },
                "authority-campaign": {
                    "generation": 5,
                    "counts": {"functions": 7595, "residuals": 6618},
                },
            }

            def runner(**kwargs):
                run_id = kwargs["run_id"]
                result = {
                    "status": "COMPLETED",
                    "exitCode": 0,
                    "readerError": None,
                    "receipt": {"path": f"{run_id}.json", "sha256": run_id},
                }
                if run_id == "authority-campaign":
                    return (
                        result,
                        f"CAMPAIGN_VERIFIED {payloads[run_id]['counts']!r} "
                        f"{live.CAMPAIGN_ROOT}\n",
                    )
                return result, json.dumps(payloads[run_id])

            with patch.object(live, "run_contained", side_effect=runner):
                result = live.verify_authority_reproductions(root, authority, {}, root)

            self.assertEqual(set(payloads), {f"authority-{key}" for key in result})
            self.assertEqual(
                live.TARGET_COUNT,
                result["lineage"]["result"]["summary"]["rows"],
            )

    def test_campaign_authority_rejects_self_attested_json(self) -> None:
        payload = {"generation": 5, "counts": {"functions": 7595, "residuals": 6618}}
        with self.assertRaisesRegex(
            live.LivePromotionError, "exact campaign verification line"
        ):
            live.parse_campaign_output(json.dumps(payload), "campaign verifier")

    def test_recover_status_records_unknown_when_authority_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            owner = Path(temporary)
            (owner / "prepared.ready.json").write_text("{}", encoding="utf-8")
            lease = live.MutexLease("test-mutex", False)
            with (
                patch.object(
                    live,
                    "acquire_mutex",
                    return_value=contextlib.nullcontext(lease),
                ),
                patch.object(
                    live,
                    "load_authority",
                    side_effect=live.LivePromotionError("project is busy"),
                ),
            ):
                result = live.recover_status(owner_root=owner)

            self.assertEqual(live.ProjectState.UNKNOWN, result["state"])
            self.assertEqual("project is busy", result["busyOrObservationError"])
            self.assertEqual(0, result["mutationSpawns"])
            self.assertFalse(result["automaticRestorePerformed"])
            self.assertTrue(Path(result["ready"]).is_file())

    def test_recover_status_records_unknown_when_prepared_ready_is_absent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            owner = Path(temporary)
            authority = fake_authority(owner)
            lease = live.MutexLease("test-mutex", False)
            with (
                patch.object(
                    live,
                    "acquire_mutex",
                    return_value=contextlib.nullcontext(lease),
                ),
                patch.object(live, "load_authority", return_value=authority),
            ):
                result = live.recover_status(owner_root=owner)

            self.assertEqual(live.ProjectState.UNKNOWN, result["state"])
            self.assertIn("prepared READY", result["busyOrObservationError"])
            self.assertTrue(Path(result["ready"]).is_file())

    def test_recover_status_downgrades_semantic_pre_when_raw_preimage_differs(self) -> None:
        def snapshot(tag: str) -> dict[str, object]:
            return {
                "fileCount": 1,
                "totalBytes": 1,
                "fileSetSha256": tag * 64,
                "files": [{"path": "BEA.gpr", "bytes": 1, "sha256": tag * 64}],
            }

        with tempfile.TemporaryDirectory() as temporary:
            owner = Path(temporary)
            authority = fake_authority(owner)
            lease = live.MutexLease("test-mutex", False)
            observation = {
                "classification": {"state": live.ProjectState.PRE, "reasons": []},
                "rawAfter": snapshot("b"),
                "receipt": {"path": "observation.json", "bytes": 1, "sha256": "c" * 64},
            }
            with (
                patch.object(
                    live,
                    "acquire_mutex",
                    return_value=contextlib.nullcontext(lease),
                ),
                patch.object(live, "load_authority", return_value=authority),
                patch.object(
                    live,
                    "verify_prepared",
                    return_value={"livePreimage": snapshot("a")},
                ),
                patch.object(live, "environment_for", return_value=({}, owner)),
                patch.object(live, "assert_quiescent", return_value={}),
                patch.object(live, "observe_project", return_value=observation),
            ):
                result = live.recover_status(owner_root=owner)

            self.assertEqual(live.ProjectState.UNKNOWN, result["state"])
            self.assertIn("differ from prepared preimage", result["busyOrObservationError"])
            self.assertIsNone(result["backupStatus"])

    def test_recover_status_never_accepts_a_stale_post_backup(self) -> None:
        def snapshot(tag: str) -> dict[str, object]:
            return {
                "fileCount": 1,
                "totalBytes": 1,
                "fileSetSha256": tag * 64,
                "files": [{"path": "BEA.gpr", "bytes": 1, "sha256": tag * 64}],
            }

        with tempfile.TemporaryDirectory() as temporary:
            owner = Path(temporary)
            (owner / "promotion/backups/post-live").mkdir(parents=True)
            (owner / "promotion/backups/post-live-restore-drill").mkdir(parents=True)
            authority = fake_authority(owner)
            lease = live.MutexLease("test-mutex", False)
            observations = [
                {
                    "classification": {"state": live.ProjectState.POST, "reasons": []},
                    "rawAfter": snapshot("b"),
                    "receipt": {"path": "live.json", "bytes": 1, "sha256": "d" * 64},
                },
                {
                    "classification": {"state": live.ProjectState.POST, "reasons": []},
                    "rawAfter": snapshot("c"),
                    "receipt": {"path": "backup.json", "bytes": 1, "sha256": "e" * 64},
                },
            ]
            with (
                patch.object(
                    live,
                    "acquire_mutex",
                    return_value=contextlib.nullcontext(lease),
                ),
                patch.object(live, "load_authority", return_value=authority),
                patch.object(live, "verify_prepared", return_value={}),
                patch.object(live, "environment_for", return_value=({}, owner)),
                patch.object(live, "assert_quiescent", return_value={}),
                patch.object(live, "observe_project", side_effect=observations),
            ):
                result = live.recover_status(owner_root=owner)

            self.assertEqual(live.ProjectState.POST, result["state"])
            self.assertIsNone(result["backupStatus"])
            self.assertIn("backup bytes differ", result["backupError"])


if __name__ == "__main__":
    raise SystemExit(0 if unittest.main(verbosity=2, exit=False).result.wasSuccessful() else 1)
