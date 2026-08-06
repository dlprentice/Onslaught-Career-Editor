#!/usr/bin/env python3
"""Focused falsifiers for the disposable Ghidra promotion proof owner."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import ghidra_promotion_scratch_proof as proof


class GhidraPromotionScratchProofTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "nt", "NTFS junction behavior is Windows-specific")
    def test_project_inventory_rejects_a_directory_junction(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            outside = root / "outside-store"
            project.mkdir()
            outside.mkdir()
            (project / "BEA.gpr").write_bytes(b"")
            (outside / "payload.gbf").write_bytes(b"external")
            junction = project / "BEA.rep"
            completed = proof.subprocess.run(
                [
                    str(proof.WINDOWS_SYSTEM_ROOT / "System32" / "cmd.exe"),
                    "/d",
                    "/c",
                    "mklink",
                    "/J",
                    str(junction),
                    str(outside),
                ],
                capture_output=True,
                text=True,
                check=False,
                creationflags=proof.CREATE_NO_WINDOW,
            )
            if completed.returncode != 0:
                self.skipTest(f"junction creation unavailable: {completed.stderr}")
            try:
                with self.assertRaisesRegex(proof.ProofError, "junction|reparse"):
                    proof.project_rows_from_disk(project, "BEA")
            finally:
                os.rmdir(junction)

    def test_project_inventory_rejects_a_hardlinked_store_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            project = root / "project"
            store = project / "BEA.rep"
            project.mkdir()
            store.mkdir()
            (project / "BEA.gpr").write_bytes(b"")
            outside = root / "outside.gbf"
            outside.write_bytes(b"external")
            os.link(outside, store / "payload.gbf")
            with self.assertRaisesRegex(proof.ProofError, "hardlinked"):
                proof.project_rows_from_disk(project, "BEA")

    def test_retained_inventory_recheck_rejects_readonly_project_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tool = root / "ExportFullFunctionInventory.java"
            tool.write_bytes(b"tool")
            projects = {}
            for role in ("main", "poison"):
                project = root / f"{role}-project"
                (project / "BEA.rep").mkdir(parents=True)
                (project / "BEA.gpr").write_bytes(b"")
                (project / "BEA.rep" / "db.gbf").write_bytes(role.encode())
                expected = root / "runs" / f"{role}-after"
                expected.mkdir(parents=True)
                (expected / "functions.tsv").write_bytes(f"{role}-functions".encode())
                (expected / "program.tsv").write_bytes(f"{role}-program".encode())
                projects[role] = project
            backup = root / "backup-project"
            (backup / "BEA.rep").mkdir(parents=True)
            (backup / "BEA.gpr").write_bytes(b"")
            (backup / "BEA.rep" / "db.gbf").write_bytes(b"backup")
            baseline = root / "runs" / "main-baseline"
            baseline.mkdir(parents=True)
            (baseline / "functions.tsv").write_bytes(b"backup-functions")
            (baseline / "program.tsv").write_bytes(b"backup-program")

            def mutate_project(**kwargs):
                project = kwargs["project_root"]
                (project / "BEA.rep" / "db.gbf").write_bytes(b"mutated")
                expected = (
                    baseline
                    if project == backup
                    else root / "runs" / f"{'main' if project == projects['main'] else 'poison'}-after"
                )
                return {}, expected / "functions.tsv", expected / "program.tsv"

            with (
                mock.patch.object(proof, "prepare_sanitized_environment", return_value={}),
                mock.patch.object(proof, "run_inventory", side_effect=mutate_project),
            ):
                with self.assertRaisesRegex(
                    proof.ProofError, "changed during read-only verification"
                ):
                    proof.reverify_retained_project_inventories(
                        proof_root=root,
                        headless=root / "analyzeHeadless.bat",
                        java=Path(sys.executable),
                        inventory_tool=tool,
                        backup_project=backup,
                        main_project=projects["main"],
                        poison_project=projects["poison"],
                    )

    def test_retained_inventory_recheck_rejects_semantic_replacement(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tool = root / "ExportFullFunctionInventory.java"
            tool.write_bytes(b"tool")
            projects = {}
            for role in ("main", "poison"):
                project = root / f"{role}-project"
                (project / "BEA.rep").mkdir(parents=True)
                (project / "BEA.gpr").write_bytes(b"")
                (project / "BEA.rep" / "db.gbf").write_bytes(role.encode())
                expected = root / "runs" / f"{role}-after"
                expected.mkdir(parents=True)
                (expected / "functions.tsv").write_bytes(f"{role}-functions".encode())
                (expected / "program.tsv").write_bytes(f"{role}-program".encode())
                projects[role] = project
            backup = root / "backup-project"
            (backup / "BEA.rep").mkdir(parents=True)
            (backup / "BEA.gpr").write_bytes(b"")
            (backup / "BEA.rep" / "db.gbf").write_bytes(b"backup")
            baseline = root / "runs" / "main-baseline"
            baseline.mkdir(parents=True)
            (baseline / "functions.tsv").write_bytes(b"backup-functions")
            (baseline / "program.tsv").write_bytes(b"backup-program")
            observed = root / "observed"
            observed.mkdir()
            (observed / "functions.tsv").write_bytes(b"replacement-functions")
            (observed / "program.tsv").write_bytes(b"replacement-program")

            with (
                mock.patch.object(proof, "prepare_sanitized_environment", return_value={}),
                mock.patch.object(
                    proof,
                    "run_inventory",
                    return_value=(
                        {}, observed / "functions.tsv", observed / "program.tsv"
                    ),
                ),
            ):
                with self.assertRaisesRegex(
                    proof.ProofError, "does not match its recorded inventory"
                ):
                    proof.reverify_retained_project_inventories(
                        proof_root=root,
                        headless=root / "analyzeHeadless.bat",
                        java=Path(sys.executable),
                        inventory_tool=tool,
                        backup_project=backup,
                        main_project=projects["main"],
                        poison_project=projects["poison"],
                    )

    def test_trusted_tool_role_rejects_arbitrary_bytes(self) -> None:
        canonical = Path(proof.__file__).parent / proof.TRUSTED_TOOL_NAMES["promotion"]
        self.assertEqual(
            canonical.resolve(), proof.require_trusted_tool_source("promotion", canonical)
        )
        with tempfile.TemporaryDirectory() as temporary:
            fake = Path(temporary) / proof.TRUSTED_TOOL_NAMES["promotion"]
            fake.write_bytes(b"arbitrary reviewed-looking tool")
            with self.assertRaisesRegex(proof.ProofError, "trusted canonical tool"):
                proof.require_trusted_tool_source("promotion", fake)

    def test_python_stamp_rejects_a_receipt_selected_executable(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            fake = Path(temporary) / "python.exe"
            fake.write_bytes(b"fake executable")
            with self.assertRaisesRegex(proof.ProofError, "trusted executable"):
                proof._verify_python_stamp(proof.external_stamp(fake))

    def test_authorized_pilot_inputs_reject_any_authority_edge_change(self) -> None:
        target = b"0x00401000\n"
        ready = b'{"verdict":"READY"}\n'
        target_sha = proof.sha256_bytes(target)
        ready_sha = proof.sha256_bytes(ready)
        with (
            mock.patch.object(proof, "BOUNDARY_TARGET_SHA256", target_sha),
            mock.patch.object(proof, "BOUNDARY_TARGET_READY_SHA256", ready_sha),
            mock.patch.object(proof, "BOUNDARY_TARGET_COUNT", 1),
        ):
            proof.require_authorized_pilot_inputs(
                target_content=target,
                ready_content=ready,
                requested_sha256=target_sha,
                requested_count=1,
            )
            mutations = (
                {"target_content": target + b"0x00402000\n"},
                {"ready_content": ready + b" "},
                {"requested_sha256": "0" * 64},
                {"requested_count": 2},
            )
            baseline = {
                "target_content": target,
                "ready_content": ready,
                "requested_sha256": target_sha,
                "requested_count": 1,
            }
            for mutation in mutations:
                with self.subTest(mutation=next(iter(mutation))):
                    with self.assertRaisesRegex(proof.ProofError, "authorized observed40"):
                        proof.require_authorized_pilot_inputs(
                            **{**baseline, **mutation}
                        )

    def test_source_campaign_ready_requires_the_external_authority_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            ready = Path(temporary) / "campaign.ready.json"
            ready.write_bytes(b"authority")
            with mock.patch.object(
                proof,
                "BOUNDARY_SOURCE_CAMPAIGN_READY_SHA256",
                proof.sha256_file(ready),
            ):
                proof.require_authorized_source_campaign_ready(ready)
                ready.write_bytes(b"self-consistent forgery")
                with self.assertRaisesRegex(proof.ProofError, "authorized observed40"):
                    proof.require_authorized_source_campaign_ready(ready)

    def test_distribution_receipt_rejects_manifest_disk_divergence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            proof_root = Path(temporary) / "proof"
            distribution = Path(temporary) / "distribution"
            manifest = proof_root / "inputs" / "toolchain" / "test-files.tsv"
            distribution.mkdir()
            (distribution / "runtime.bin").write_bytes(b"exact runtime")
            rows = proof.distribution_rows(distribution)
            proof.write_distribution_manifest(manifest, rows)
            spec = proof.distribution_receipt(
                root=distribution,
                manifest_path=manifest,
                proof_root=proof_root,
                rows=rows,
            )
            kwargs = {
                "proof_root": proof_root,
                "spec": spec,
                "expected_root": distribution,
                "expected_manifest_relative": "inputs/toolchain/test-files.tsv",
                "label": "test",
                "expected_count": len(rows),
                "expected_total_bytes": sum(row[1] for row in rows),
                "expected_sha256": proof.canonical_rows_sha(rows),
            }
            proof._verify_distribution_receipt(**kwargs)
            (distribution / "runtime.bin").write_bytes(b"changed runtime")
            with self.assertRaisesRegex(proof.ProofError, "fingerprint|no longer"):
                proof._verify_distribution_receipt(**kwargs)

    def test_sanitized_environment_drops_python_and_java_injection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            hostile = {
                "PYTHONPATH": str(root / "attacker"),
                "_JAVA_OPTIONS": "-javaagent:attacker.jar",
                "JAVA_TOOL_OPTIONS": "-javaagent:attacker.jar",
                "JDK_JAVA_OPTIONS": "-javaagent:attacker.jar",
                "GHIDRA_JAVA_OPTIONS": "-javaagent:attacker.jar",
                "GHIDRA_HEADLESS_JAVA_OPTIONS": "-javaagent:attacker.jar",
                "SystemRoot": str(root / "fake-windows"),
                "WINDIR": str(root / "fake-windows"),
            }
            with mock.patch.dict(os.environ, hostile, clear=False):
                environment = proof.expected_sanitized_environment(
                    root, Path(sys.executable)
                )
            for key in set(hostile) - {"SystemRoot", "WINDIR"}:
                self.assertNotIn(key, environment)
            self.assertEqual(
                str((root / "runtime-home" / "profile").resolve()),
                environment["USERPROFILE"],
            )
            self.assertEqual("1", environment["PYTHONNOUSERSITE"])
            self.assertEqual("1", environment["NoDefaultCurrentDirectoryInExePath"])
            self.assertEqual(
                str(proof.WINDOWS_SYSTEM_ROOT.resolve()), environment["SystemRoot"]
            )

    def test_copy_manifest_requires_a_stable_exact_source(self) -> None:
        row = {
            "relative_path": "BEA.gpr",
            "size": 0,
            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        }
        section = {
            "fileCount": 1,
            "files": [row],
            "projectName": "BEA",
            "structurallyComplete": True,
            "totalBytes": 0,
        }
        comparison = {
            "extra": [],
            "extraCount": 0,
            "hashDiffCount": 0,
            "hashDifferences": [],
            "matches": True,
            "missing": [],
            "missingCount": 0,
            "sizeDiffCount": 0,
            "sizeDifferences": [],
        }
        document = {
            "copyComparison": comparison,
            "createdAtUtc": "2026-08-02T20:42:19Z",
            "destination": section,
            "readonlyOpen": None,
            "schemaVersion": proof.BACKUP_SCHEMA,
            "source": section,
            "sourceStable": True,
        }
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "backup_manifest.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            self.assertEqual(([('BEA.gpr', 0, row['sha256'])],) * 2, proof.validate_copy_manifest(path))

            for field in ("sourceStable", "copyComparison", "source"):
                with self.subTest(field=field):
                    changed = json.loads(json.dumps(document))
                    if field == "sourceStable":
                        changed[field] = False
                    elif field == "copyComparison":
                        changed[field]["matches"] = False
                    else:
                        changed[field]["files"][0]["sha256"] = "0" * 64
                    path.write_text(json.dumps(changed), encoding="utf-8")
                    with self.assertRaises(proof.ProofError):
                        proof.validate_copy_manifest(path)

    def test_inspection_manifest_is_bound_to_its_exact_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            expected_root = root / "main-project"
            wrong_root = root / "poison-project"
            expected_root.mkdir()
            wrong_root.mkdir()
            document = {
                "createdAtUtc": "2026-08-02T20:42:19Z",
                "manifest": {
                    "fileCount": 1,
                    "files": [
                        {
                            "relative_path": "BEA.gpr",
                            "size": 0,
                            "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                        }
                    ],
                    "projectName": "BEA",
                    "root": str(wrong_root.resolve()),
                    "structurallyComplete": True,
                    "totalBytes": 0,
                },
                "schemaVersion": proof.BACKUP_SCHEMA,
            }
            path = root / "manifest.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            with self.assertRaisesRegex(proof.ProofError, "wrong project root"):
                proof.manifest_rows(path, expected_root=expected_root)

    def test_program_inventory_rejects_duplicate_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "program.tsv"
            path.write_text(
                "metric\tvalue\ninstructions\t1\ninstructions\t2\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(proof.ProofError, "duplicate metrics"):
                proof.program_map(path)

    def test_external_toolchain_rejects_an_arbitrary_launcher(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            launcher = Path(temporary) / "analyzeHeadless.bat"
            launcher.write_text("not ghidra", encoding="utf-8")
            with self.assertRaisesRegex(
                proof.ProofError, "unavailable|unsupported|not a regular file"
            ):
                proof.require_expected_external_toolchain(launcher)

    def test_headless_batch_launch_disables_cmd_autorun_and_rejects_metacharacters(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            headless = Path(temporary) / "analyzeHeadless.bat"
            headless.write_bytes(b"launcher")
            argv = proof.windows_batch_argv(headless, ["project", "BEA", "-readOnly"])
            self.assertEqual(
                ["/d", "/s", "/c"], [value.lower() for value in argv[1:4]]
            )
            self.assertTrue(argv[4].startswith("call "))
            self.assertIn(str(headless.resolve()), argv[4])
            with self.assertRaisesRegex(proof.ProofError, "unsafe for cmd.exe"):
                proof.windows_batch_argv(headless, ["project&attacker"])

    def test_campaign_authority_rejects_a_self_consistent_unknown_reducer(self) -> None:
        campaign_ready = {
            "reducer": {
                "schema": proof.CAMPAIGN_REDUCER_SCHEMA,
                "id": "0" * 64,
                "entry": proof.CAMPAIGN_REDUCER_ENTRY,
                "files": [
                    {
                        "role": "campaign",
                        "path": proof.CAMPAIGN_REDUCER_ENTRY,
                        "bytes": 0,
                        "sha256": "0" * 64,
                    }
                ],
            }
        }
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(proof.ProofError, "identity is unsupported"):
                proof._validate_campaign_reducer_copy(
                    Path(temporary), campaign_ready
                )

    def test_tsv_reader_ignores_campaign_schema_preamble(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "questions.tsv"
            path.write_text(
                "# bea.re.campaign.v5\nquestionId\tstate\nQ-1\tOPEN\n",
                encoding="utf-8",
            )

            self.assertEqual(
                [{"questionId": "Q-1", "state": "OPEN"}], proof.read_tsv(path)
            )

    def test_negative_control_cannot_survive_a_nonzero_process_exit(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "runs" / "guard-outside-text").mkdir(parents=True)
            project_root = root / "project"
            project_root.mkdir()
            (project_root / "BEA.gpr").write_bytes(b"")
            (project_root / "BEA.rep").mkdir()
            tool = root / "CreateFunctionsFromAddressList.java"
            target = root / "targets.txt"
            headless = root / "analyzeHeadless.bat"
            tool.write_bytes(b"tool")
            target.write_bytes(b"0x00401000\n")
            headless.write_bytes(b"launcher")
            tool_stamp = proof.stamp(tool, root)
            target_stamp = proof.stamp(target, root)
            expected_error = "Address outside executable .text"
            text = "\n".join(
                (
                    f"FUNCTION_PROMOTION_TOOL_OK path={tool.resolve()} "
                    f"bytes={tool_stamp['bytes']} sha256={tool_stamp['sha256']}",
                    f"Opening existing project: {project_root.resolve() / 'BEA'}",
                    f"SCRIPT: {tool.resolve()} (HeadlessAnalyzer)",
                    "REPORT SCRIPT ERROR",
                    expected_error,
                )
            )
            result = {
                "id": "guard-outside-text",
                "argv": ["analyzeHeadless"],
                "exitCode": 99,
            }

            with mock.patch.object(proof, "run_process", return_value=(result, text)):
                with self.assertRaisesRegex(proof.ProofError, "exited 99"):
                    proof.run_promotion(
                        proof_root=root,
                        run_id="guard-outside-text",
                        headless=headless,
                        project_root=project_root,
                        project_name="BEA",
                        tool=tool,
                        tool_stamp=tool_stamp,
                        target_path=target,
                        target_stamp=target_stamp,
                        target_count=1,
                        semantic_target_sha256=proof.semantic_target_sha(
                            ["0x00401000"]
                        ),
                        mode="dry",
                        expected_sha256=proof.PROGRAM_SHA256,
                        cwd=root,
                        environment={},
                        expected_error=expected_error,
                    )

    def test_ready_is_bound_to_the_executed_tool_target_output_and_instruction_count(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tool = root / "CreateFunctionsFromAddressList.java"
            target = root / "targets.txt"
            output = root / "dry.tsv"
            ready_path = root / "dry.ready.json"
            tool.write_bytes(b"tool")
            target.write_bytes(b"0x00401000\n")
            output.write_bytes(b"address\tstatus\n0x00401000\twould_create\n")
            tool_stamp = proof.stamp(tool, root)
            target_stamp = proof.stamp(target, root)
            output_stamp = proof.stamp(output, root)
            semantic_sha = proof.semantic_target_sha(["0x00401000"])
            ready = {
                "schemaVersion": proof.READY_SCHEMA,
                "mode": "dry",
                "tool": {
                    "path": str(tool.resolve()),
                    "bytes": tool_stamp["bytes"],
                    "sha256": tool_stamp["sha256"],
                },
                "program": {
                    "name": proof.PROGRAM_NAME,
                    "executableMd5": proof.PROGRAM_MD5,
                    "executableSha256": proof.PROGRAM_SHA256,
                    "imageBase": proof.IMAGE_BASE,
                    "language": proof.LANGUAGE,
                    "compilerSpec": proof.COMPILER_SPEC,
                },
                "input": {
                    "path": str(target.resolve()),
                    "bytes": target_stamp["bytes"],
                    "sha256": target_stamp["sha256"],
                    "expectedCount": 1,
                    "semanticTargetSetSha256": semantic_sha,
                },
                "output": {
                    "path": str(output.resolve()),
                    "bytes": output_stamp["bytes"],
                    "sha256": output_stamp["sha256"],
                },
                "counts": {
                    "targets": 1,
                    "wouldCreate": 1,
                    "created": 0,
                    "alreadyExists": 0,
                    "verified": 0,
                    "programInstructionsBefore": 100,
                    "programInstructionsAfter": 100,
                },
                "namesAuthorized": False,
                "mutationCommitted": False,
                "allTargetsVerified": False,
            }
            ready_path.write_text(json.dumps(ready), encoding="utf-8")
            proof.validate_ready(
                ready_path=ready_path,
                mode="dry",
                target_path=target,
                target_stamp=target_stamp,
                target_count=1,
                semantic_target_sha256=semantic_sha,
                tool=tool,
                tool_stamp=tool_stamp,
                output_path=output,
                proof_root=root,
            )

            for mutation in ("tool", "instructions", "output"):
                with self.subTest(mutation=mutation):
                    changed = json.loads(json.dumps(ready))
                    if mutation == "tool":
                        changed["tool"]["sha256"] = "0" * 64
                    elif mutation == "instructions":
                        changed["counts"]["programInstructionsAfter"] = 101
                    else:
                        changed["output"]["sha256"] = "0" * 64
                    ready_path.write_text(json.dumps(changed), encoding="utf-8")
                    with self.assertRaisesRegex(proof.ProofError, "READY"):
                        proof.validate_ready(
                            ready_path=ready_path,
                            mode="dry",
                            target_path=target,
                            target_stamp=target_stamp,
                            target_count=1,
                            semantic_target_sha256=semantic_sha,
                            tool=tool,
                            tool_stamp=tool_stamp,
                            output_path=output,
                            proof_root=root,
                        )

    def test_tool_sentinel_must_match_exact_snapshot_bytes_and_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tool = root / "tool.java"
            tool.write_bytes(b"exact")
            tool_stamp = proof.stamp(tool, root)
            clean = (
                f"INVENTORY_TOOL_OK path={tool.resolve()} bytes={tool_stamp['bytes']} "
                f"sha256={tool_stamp['sha256']}\n"
            )
            proof.require_tool_sentinel(
                clean, prefix="INVENTORY_TOOL_OK", tool=tool, tool_stamp=tool_stamp
            )
            with self.assertRaisesRegex(proof.ProofError, "tool identity"):
                proof.require_tool_sentinel(
                    clean.replace(str(tool_stamp["sha256"]), "0" * 64),
                    prefix="INVENTORY_TOOL_OK",
                    tool=tool,
                    tool_stamp=tool_stamp,
                )

    def test_artifact_set_excludes_mutable_projects_and_its_own_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "tools").mkdir()
            (root / "main-project").mkdir()
            (root / "poison-project").mkdir()
            (root / "tools" / "tool.java").write_bytes(b"tool")
            (root / "main-project" / "db.gbf").write_bytes(b"large")
            (root / "poison-project" / "db.gbf").write_bytes(b"large")
            (root / "proof.ready.json").write_bytes(b"self")

            artifact_set = proof.artifact_set(root)

            self.assertEqual(1, artifact_set["count"])
            self.assertEqual("tools/tool.java", artifact_set["items"][0]["path"])

    def test_atomic_new_publication_refuses_an_existing_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "receipt.json"
            proof.write_new(path, b"first")
            with self.assertRaisesRegex(proof.ProofError, "refusing to overwrite"):
                proof.write_new(path, b"second")
            self.assertEqual(b"first", path.read_bytes())

    def test_ready_verifier_rejects_metadata_only_project_receipts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "runs" / "one").mkdir(parents=True)
            projects = {}
            for role, name in (("mainScratch", "main-project"), ("poisonControl", "poison-project")):
                project_root = root / name
                (project_root / "BEA.rep" / "idata").mkdir(parents=True)
                (project_root / "BEA.gpr").write_bytes(b"")
                (project_root / "BEA.rep" / "idata" / "db.gbf").write_bytes(role.encode())
                rows = proof.project_rows_from_disk(project_root, "BEA")
                manifest_path = root / "runs" / f"{name}-manifest.json"
                manifest_path.write_text(
                    json.dumps(
                        {
                            "schemaVersion": proof.BACKUP_SCHEMA,
                            "manifest": {
                                "root": str(project_root.resolve()),
                                "projectName": "BEA",
                                "fileCount": len(rows),
                                "totalBytes": sum(row[1] for row in rows),
                                "structurallyComplete": True,
                                "files": [
                                    {"relative_path": path, "size": size, "sha256": sha}
                                    for path, size, sha in rows
                                ],
                            },
                        }
                    ),
                    encoding="utf-8",
                )
                manifest_spec = proof.stamp(manifest_path, root)
                projects[role] = {
                    "root": str(project_root.resolve()),
                    (
                        "postverificationManifest"
                        if role == "mainScratch"
                        else "postManifest"
                    ): manifest_spec,
                    "finalFileSetSha256": proof.canonical_rows_sha(rows),
                }
            run_path = root / "runs" / "one" / "run.json"
            run_path.write_text(
                json.dumps({"verdict": "SURVIVED", "argv": ["tool", "arg"]}),
                encoding="utf-8",
            )
            receipt = {
                "schema": proof.SCHEMA,
                "verdict": "SURVIVED",
                "projects": projects,
                "runs": [proof.stamp(run_path, root)],
            }
            receipt["artifacts"] = proof.artifact_set(root)
            ready = root / "proof.ready.json"
            ready.write_text(json.dumps(receipt), encoding="utf-8")

            with self.assertRaisesRegex(
                proof.ProofError, "schema/verdict is unsupported"
            ):
                proof.verify_ready_receipt(ready)


if __name__ == "__main__":
    raise SystemExit(0 if unittest.main(verbosity=2, exit=False).result.wasSuccessful() else 1)
