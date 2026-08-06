#!/usr/bin/env python3
"""Focused tests for the disposable Ghidra body-envelope proof owner."""

from __future__ import annotations

import csv
import copy
import json
import os
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path

try:
    import ghidra_function_envelope_proof as proof
except ModuleNotFoundError:  # supports ``python -m unittest`` from repository root
    from tools import ghidra_function_envelope_proof as proof


CANARY = (
    proof.MANIFEST_HEADER + "\n"
    "0x00542710\t0x00542710-0x0054271a;0x00542720-0x00542736\t32\t"
    "f0f8f544b4fc3bdad54cb818a519db949906caf2b798bf0a5cdee84f96f1f2b3\t"
    "cdc88702c69f4171d35d7aa3d4283ef7f788c74dfe7873783496e7e3572f7356\t9\t"
    "false\t\t0x00542720\t"
    "TEXT_RESIDUAL:74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750:0x00542710-0x0054271A;"
    "TEXT_RESIDUAL:74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750:0x00542720-0x00542736\t"
    "Q-7761c6831ebefdbc;Q-e5cfa080a5190045\t"
    "C-115326b7fef5eebd;C-23cfea59e0f92403\tPROSPECTIVE_TWO_RANGE_CANARY\n"
)
POISON = (
    proof.MANIFEST_HEADER + "\n"
    "0x00542710\t0x00542710-0x0054271a\t10\t"
    "af92ff770e2f90f116c2e63ad59a3ae8234a67e42dda2974b734e2e27aaa4d07\t"
    "74fe35a3b08bbfcb8f47c3b11d839c8b8af7c7283b1122b816f3387e2232e19a\t2\t"
    "false\t\t0x00542720\t"
    "TEXT_RESIDUAL:74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750:0x00542710-0x0054271A\t"
    "Q-7761c6831ebefdbc\tC-115326b7fef5eebd\tREFUTED_ONE_RANGE_POISON\n"
)


class EnvelopeProofTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_inputs(self) -> tuple[Path, Path]:
        canary = self.root / "canary.tsv"
        poison = self.root / "poison.tsv"
        canary.write_text(CANARY, encoding="utf-8", newline="")
        poison.write_text(POISON, encoding="utf-8", newline="")
        return canary, poison

    def test_exact_v3_canary_and_poison_hashes(self) -> None:
        canary, poison = self.write_inputs()
        self.assertEqual(proof.sha256_file(canary), proof.CANARY_MANIFEST_SHA256)
        self.assertEqual(proof.sha256_file(poison), proof.POISON_MANIFEST_SHA256)
        proof.validate_canary_inputs(canary, poison)
        _, rows = proof.parse_manifest(canary)
        self.assertEqual(rows[0][6:9], ["false", "", proof.FORBIDDEN_TAIL_ENTRY])

    def test_control_manifests_are_canonical_and_distinct(self) -> None:
        canary, poison = self.write_inputs()
        controls = proof.build_control_manifests(canary, poison)
        self.assertEqual(set(controls), {
            "wrong-header.tsv", "trailing-blank.tsv", "instruction-coverage.tsv",
            "pairwise-body-conflict.tsv", "forbidden-target-conflict.tsv",
            "wrong-thunk-kind.tsv",
        })
        self.assertEqual(len({proof.sha256_bytes(value) for value in controls.values()}), 6)
        instruction = controls["instruction-coverage.tsv"].decode().splitlines()[1].split("\t")
        self.assertEqual(instruction[1:6], [
            "0x00542710-0x00542711", "1",
            proof.canonical_range_digest([(0x00542710, 0x00542711)]),
            proof.sha256_bytes(b"\xb9"), "1",
        ])
        self.assertEqual(instruction[6:9], ["false", "", ""])
        wrong_kind = controls["wrong-thunk-kind.tsv"].decode().splitlines()[1].split("\t")
        self.assertEqual(wrong_kind[6:9], ["true", proof.FORBIDDEN_TAIL_ENTRY, proof.FORBIDDEN_TAIL_ENTRY])
        with self.assertRaises(proof.ProofError):
            bad = self.root / "trailing.tsv"
            bad.write_bytes(controls["trailing-blank.tsv"])
            proof.parse_manifest(bad)

    def test_instruction_coverage_control_has_one_stable_rejection_class(self) -> None:
        java = Path(proof.__file__).with_name("CreateFunctionsFromBoundaryManifest.java")
        self.assertEqual(proof.sha256_file(java), proof.EXPECTED_TOOL_SHA256["envelope"])
        source = java.read_text(encoding="utf-8")
        self.assertIn(
            '"INSTRUCTION_COVERAGE_MISMATCH: instruction crosses expected body at "',
            source,
        )
        self.assertIn('"INSTRUCTION_COVERAGE_MISMATCH at "', source)

    def test_java_ready_requires_provisional_v3_transaction_semantics(self) -> None:
        tool = self.root / "tool.java"
        manifest = self.root / "manifest.tsv"
        output = self.root / "output.tsv"
        tool.write_bytes(b"tool")
        manifest.write_text(CANARY, encoding="utf-8", newline="")
        output.write_bytes(b"output")
        common = {
            "schemaVersion": proof.JAVA_READY_SCHEMA,
            "program": {
                "name": proof.PROGRAM_NAME,
                "executableMd5": proof.PROGRAM_MD5,
                "executableSha256": proof.PROGRAM_SHA256,
                "imageBase": proof.IMAGE_BASE,
                "language": proof.LANGUAGE,
                "compilerSpec": proof.COMPILER_SPEC,
            },
            "tool": proof.external_stamp(tool),
            "manifest": {**proof.external_stamp(manifest), "expectedCount": 1},
            "output": proof.external_stamp(output),
            "namesAuthorized": False,
            "functionKindsBoundByManifest": True,
            "loadedOrTransientEnvelopesVerified": True,
        }
        for mode, flags, before in (
            ("probe", (False, True, False, False, True), proof.BASE_FUNCTION_COUNT),
            ("apply", (True, False, False, False, True), proof.BASE_FUNCTION_COUNT),
            ("readback", (False, False, False, True, False), proof.BASE_FUNCTION_COUNT + 1),
        ):
            ready = self.root / f"{mode}.json"
            commit, rollback, transaction, loaded, reopen = flags
            payload = {
                **common,
                "mode": mode,
                "counts": {
                    "targets": 1,
                    "functionsBefore": before,
                    "functionsTransient": proof.BASE_FUNCTION_COUNT + 1,
                    "functionManagerViewAfterNestedTransaction": proof.BASE_FUNCTION_COUNT + 1,
                    "instructionsBefore": proof.BASE_INSTRUCTION_COUNT,
                    "instructionsAfter": proof.BASE_INSTRUCTION_COUNT,
                },
                "commitRequested": commit,
                "rollbackRequested": rollback,
                "transactionEndReturnedCommitted": transaction,
                "loadedStateVerified": loaded,
                "reopenVerificationRequired": reopen,
            }
            ready.write_text(json.dumps(payload), encoding="utf-8")
            proof.validate_java_ready(ready, output, mode=mode, tool=tool, manifest=manifest)
            payload["transactionEndReturnedCommitted"] = True
            ready.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(proof.ProofError):
                proof.validate_java_ready(ready, output, mode=mode, tool=tool, manifest=manifest)

    @staticmethod
    def write_function_tsv(path: Path, rows: list[dict[str, str]]) -> None:
        fields = [
            "address", "name", "nameSource", "sigSource", "bodyBytes", "bodyMin",
            "bodyMax", "bodyRanges", "bodyDigest", "instrCount", "isThunk",
            "thunkTarget", "isExternal", "marker",
        ]
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    @staticmethod
    def write_program_tsv(path: Path, functions: int) -> None:
        path.write_text(
            "metric\tvalue\nfunctions\t" + str(functions) + "\ninstructions\t549864\nmemorySha256\tstable\n",
            encoding="utf-8",
            newline="",
        )

    def test_applied_inventory_allows_only_exact_ordinary_canary(self) -> None:
        base_functions = self.root / "before.tsv"
        after_functions = self.root / "after.tsv"
        base_program = self.root / "before-program.tsv"
        after_program = self.root / "after-program.tsv"
        existing = {
            "address": "0x00401000", "name": "Existing", "nameSource": "USER_DEFINED",
            "sigSource": "USER_DEFINED", "bodyBytes": "2", "bodyMin": "0x00401000",
            "bodyMax": "0x00401001", "bodyRanges": "1", "bodyDigest": "existing",
            "instrCount": "1", "isThunk": "false", "thunkTarget": "",
            "isExternal": "false", "marker": "unchanged",
        }
        created = {
            "address": proof.TARGET_ENTRY, "name": "FUN_00542710", "nameSource": "DEFAULT",
            "sigSource": "DEFAULT", "bodyBytes": proof.CANARY_BODY_BYTES,
            "bodyMin": proof.TARGET_ENTRY, "bodyMax": "0x00542735", "bodyRanges": "2",
            "bodyDigest": proof.CANARY_RANGE_DIGEST, "instrCount": proof.CANARY_INSTRUCTIONS,
            "isThunk": "false", "thunkTarget": "", "isExternal": "false", "marker": "created",
        }
        self.write_function_tsv(base_functions, [existing])
        self.write_function_tsv(after_functions, [existing, created])
        self.write_program_tsv(base_program, proof.BASE_FUNCTION_COUNT)
        self.write_program_tsv(after_program, proof.BASE_FUNCTION_COUNT + 1)
        self.assertEqual(
            proof.validate_applied_inventory(base_functions, base_program, after_functions, after_program),
            created,
        )
        bad = dict(created, isThunk="true", thunkTarget="0x00542720")
        self.write_function_tsv(after_functions, [existing, bad])
        with self.assertRaises(proof.ProofError):
            proof.validate_applied_inventory(base_functions, base_program, after_functions, after_program)

    def test_receipt_failure_watcher_creates_exact_poison_only_after_staging(self) -> None:
        output = self.root / "envelopes.tsv"
        error: list[BaseException] = []
        thread = threading.Thread(
            target=lambda: self._capture(error, lambda: proof.publish_receipt_failure_poison(output, timeout_seconds=1.0))
        )
        thread.start()
        partial = self.root / ".envelopes.tsv.partial-test"
        partial.write_bytes(b"staged")
        thread.join(2)
        self.assertFalse(thread.is_alive())
        self.assertEqual(error, [])
        self.assertEqual(output.read_bytes(), b"RECEIPT_PUBLICATION_RACE_POISON\n")

    @staticmethod
    def _capture(errors: list[BaseException], callback) -> None:
        try:
            callback()
        except BaseException as exc:
            errors.append(exc)

    def test_artifact_manifest_detects_unmanifested_file(self) -> None:
        (self.root / "a.txt").write_text("a", encoding="utf-8")
        ready = {
            "artifacts": {
                "canonicalization": "sorted relative path with exact bytes and SHA-256; READY excluded",
                "count": 1,
                "items": proof.artifact_items(self.root),
            }
        }
        proof.verify_artifact_items(self.root, ready)
        (self.root / "unexpected.txt").write_text("x", encoding="utf-8")
        with self.assertRaises(proof.ProofError):
            proof.verify_artifact_items(self.root, ready)

    def test_write_new_refuses_overwrite(self) -> None:
        target = self.root / "receipt.json"
        proof.write_new(target, b"one")
        with self.assertRaises(proof.ProofError):
            proof.write_new(target, b"two")
        self.assertEqual(target.read_bytes(), b"one")

    @staticmethod
    def valid_ready_shape() -> dict:
        stamp = {"path": "inputs/x", "bytes": 1, "sha256": "0" * 64}
        source_inputs = {
            name: {"source": {"path": "C:/source", "bytes": 1, "sha256": "0" * 64}, "snapshot": dict(stamp)}
            for name in (
                "observed40.ready.json", "canary-refutation.ready.json", "boundary520.ready.json",
                "canary-two-range.tsv", "poison-one-range.tsv", "base-functions.tsv", "base-program.tsv",
            )
        }
        tools = {
            role: {"source": {"path": "C:/source", "bytes": 1, "sha256": "0" * 64}, "snapshot": dict(stamp)}
            for role in (*proof.EXPECTED_TOOL_SHA256, "runner")
        }
        external = {"path": "C:/external", "bytes": 1, "sha256": "0" * 64}
        distribution = {
            "root": "C:/distribution", "fileCount": 1, "totalBytes": 1,
            "fileSetSha256": "0" * 64, "manifest": dict(stamp),
        }
        replicas = []
        for replica_id in ("replica-a", "replica-b"):
            replicas.append({
                "id": replica_id,
                "controlProject": f"C:/{replica_id}-control",
                "applyProject": f"C:/{replica_id}-apply",
                "runs": [dict(stamp) for _ in range(24)],
                "probeOutput": dict(stamp), "applyOutput": dict(stamp),
                "readbackOutput": dict(stamp), "afterFunctions": dict(stamp),
                "afterProgram": dict(stamp), "createdRow": {},
                "controlProjectFileSetSha256": "0" * 64,
                "applyProjectFileSetSha256": "0" * 64,
            })
        return {
            "schema": proof.SCHEMA,
            "status": "READY",
            "verdict": "SURVIVED",
            "program": proof.expected_ready_program(),
            "sourceAuthority": {
                "projectRoot": "C:/source-project",
                "projectFileCount": proof.BASE_PROJECT_FILE_COUNT,
                "projectTotalBytes": proof.BASE_PROJECT_TOTAL_BYTES,
                "projectFileSetSha256": proof.BASE_PROJECT_FILE_SET_SHA256,
                "inputs": source_inputs,
                "sourceBeforeRun": dict(stamp), "sourceAfterRun": dict(stamp),
            },
            "tools": tools,
            "toolchain": {
                "analyzeHeadless": dict(external), "applicationProperties": dict(external),
                "java": dict(external), "python": dict(external),
                "ghidraDistribution": dict(distribution), "jdkDistribution": dict(distribution),
                "pythonDistribution": dict(distribution),
            },
            "manifest": proof.expected_ready_manifest(),
            "replicas": replicas,
            "checks": proof.expected_ready_checks(),
            "claimBoundary": list(proof.CLAIM_BOUNDARY),
            "artifacts": {
                "canonicalization": "sorted relative path with exact bytes and SHA-256; READY excluded",
                "count": 0, "items": [],
            },
        }

    def test_ready_semantics_reject_claim_only_mutations(self) -> None:
        ready = self.valid_ready_shape()
        proof.validate_ready_semantic_shape(ready)
        mutations = [
            ("program sha", lambda value: value["program"].__setitem__("sha256", "f" * 64)),
            ("thunk claim", lambda value: value["manifest"].__setitem__("expectedIsThunk", True)),
            ("kind claim", lambda value: value["checks"].__setitem__("functionKind", "thunk")),
            ("created entry", lambda value: value["checks"].__setitem__("onlyCreatedEntry", "0xdeadbeef")),
            ("extra key", lambda value: value.__setitem__("unverifiedClaim", True)),
        ]
        for label, mutate in mutations:
            with self.subTest(label=label):
                candidate = copy.deepcopy(ready)
                mutate(candidate)
                with self.assertRaises(proof.ProofError):
                    proof.validate_ready_semantic_shape(candidate)

    def test_ready_project_paths_are_derived_not_free_authority(self) -> None:
        proof_root = self.root / "local-lab" / "formal-proof"
        source_project = self.root / "observed40-project"
        ready = self.valid_ready_shape()
        ready["sourceAuthority"]["projectRoot"] = str(source_project.resolve())
        for replica in ready["replicas"]:
            replica_id = replica["id"]
            replica["controlProject"] = str((proof_root / "projects" / f"{replica_id}-control").resolve())
            replica["applyProject"] = str((proof_root / "projects" / f"{replica_id}-apply").resolve())
        proof.validate_derived_project_paths(ready, proof_root, source_project)

        mutations = [
            ("source", lambda value: value["sourceAuthority"].__setitem__("projectRoot", "C:/substituted-source")),
            ("control", lambda value: value["replicas"][0].__setitem__("controlProject", "C:/substituted-control")),
            ("apply", lambda value: value["replicas"][1].__setitem__("applyProject", "C:/substituted-apply")),
        ]
        for label, mutate in mutations:
            with self.subTest(label=label):
                candidate = copy.deepcopy(ready)
                mutate(candidate)
                with self.assertRaises(proof.ProofError):
                    proof.validate_derived_project_paths(candidate, proof_root, source_project)

    def test_producer_rejects_nonderived_source_selection_before_publication(self) -> None:
        expected = self.root / "expected-authority.json"
        selected = proof.require_derived_selection(None, expected, "authority")
        self.assertEqual(selected, proof.lexical_absolute(expected))
        self.assertEqual(
            proof.require_derived_selection(expected, expected, "authority"),
            proof.lexical_absolute(expected),
        )
        with self.assertRaises(proof.ProofError):
            proof.require_derived_selection(self.root / "same-bytes-elsewhere.json", expected, "authority")

    def test_receipt_order_rejects_duplicates(self) -> None:
        ids = ["one", "two"]
        stamps = [
            {"path": "runs/one/run.json", "bytes": 1, "sha256": "0" * 64},
            {"path": "runs/two/run.json", "bytes": 1, "sha256": "1" * 64},
        ]
        proof.require_receipt_stamp_order(stamps, ids, "test")
        with self.assertRaises(proof.ProofError):
            proof.require_receipt_stamp_order([stamps[0], stamps[0]], ids, "test")

    def test_rejection_cannot_survive_a_nonzero_process_exit(self) -> None:
        run_root = self.root / "runs" / "failed-control"
        run_root.mkdir(parents=True)
        with self.assertRaises(proof.ProofError):
            proof.require_rejection(
                proof_root=self.root,
                result={"id": "failed-control", "exitCode": 1},
                output=run_root / "envelopes.tsv",
                ready=run_root / "envelopes.ready.json",
                text="REPORT SCRIPT ERROR\nmanifest sha256 mismatch\n",
                expected_pattern=r"manifest sha256 mismatch",
            )
        self.assertFalse((run_root / "run.json").exists())

    def test_frozen_stamp_rejects_ads_backslash_and_nonmember(self) -> None:
        artifact = self.root / "artifact.txt"
        artifact.write_text("artifact", encoding="utf-8")
        value = proof.stamp(artifact, self.root)
        for unsafe in ("artifact.txt:stream", "nested\\artifact.txt"):
            candidate = dict(value, path=unsafe)
            with self.assertRaises(proof.ProofError):
                proof.validate_frozen_stamp(self.root, candidate, "unsafe")
        other = self.root / "other.txt"
        other.write_text("other", encoding="utf-8")
        ready = {
            "artifacts": {
                "items": [value], "count": 1,
                "canonicalization": "sorted relative path with exact bytes and SHA-256; READY excluded",
            }
        }
        (self.root / "proof.ready.json").write_text(json.dumps(ready), encoding="utf-8")
        with self.assertRaises(proof.ProofError):
            proof.validate_frozen_stamp(self.root, proof.stamp(other, self.root), "nonmember")

    def test_reparse_ancestor_is_rejected_when_supported(self) -> None:
        real = self.root / "real"
        real.mkdir()
        (real / "child.txt").write_text("x", encoding="utf-8")
        link = self.root / "link"
        try:
            os.symlink(real, link, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"directory symlink unavailable: {exc}")
        with self.assertRaises(proof.ProofError):
            proof.require_plain_file(link / "child.txt", "linked file")
        with self.assertRaises(proof.ProofError):
            proof.write_new(link / "new.txt", b"no")

    @unittest.skipUnless(os.name == "nt", "Windows Job Object test")
    def test_timeout_kills_descendant_and_cancels_callback(self) -> None:
        runs = self.root / "runs"
        work = self.root / "work"
        runs.mkdir()
        work.mkdir()
        orphan_marker = self.root / "orphan.txt"
        callback_marker = self.root / "callback.txt"
        grandchild = (
            "import time,pathlib;time.sleep(1);"
            f"pathlib.Path({str(orphan_marker)!r}).write_text('orphan')"
        )
        parent = (
            "import subprocess,sys,time;"
            f"subprocess.Popen([sys.executable,'-c',{grandchild!r}]);time.sleep(20)"
        )
        callback_stopped = threading.Event()

        def callback(stop: threading.Event) -> None:
            while not stop.wait(0.01):
                pass
            callback_stopped.set()
            time.sleep(1)
            if not stop.is_set():
                callback_marker.write_text("late", encoding="utf-8")

        with self.assertRaisesRegex(proof.ProofError, "timed out"):
            proof.run_process(
                proof_root=self.root, run_id="timeout-job",
                argv=[sys.executable, "-c", parent], cwd=work,
                environment=dict(os.environ), timeout_seconds=0.3,
                during_run=callback,
            )
        self.assertTrue(callback_stopped.is_set())
        time.sleep(1.2)
        self.assertFalse(orphan_marker.exists())
        self.assertFalse(callback_marker.exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
