#!/usr/bin/env python3
"""Focused tests for the prospective admissible-515 Ghidra proof owner."""

from __future__ import annotations

import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import ghidra_global_init_full520_proof as proof


class Admissible515ProofTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repo = Path(proof.__file__).resolve().parents[1]
        self.paths = proof.default_paths(self.repo)
        if not self.paths["fullManifest"].is_file():
            self.skipTest("maintainer-local full520 manifest is absent")
        self.full_rows = proof.validate_full_manifest(self.paths["fullManifest"])
        self.rows, self.quarantine = proof.partition_full_manifest(self.full_rows)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.manifest = Path(self.temporary.name) / "admissible515.tsv"
        self.manifest.write_bytes(proof.render_manifest(self.rows))
        proof.validate_admissible_manifest(self.manifest)

    def test_full_manifest_partitions_into_exact_admissible_and_quarantine_sets(self) -> None:
        summary = proof.expected_manifest_summary(self.rows, self.quarantine)
        self.assertEqual(515, summary["count"])
        self.assertEqual(57182, summary["bodyBytes"])
        self.assertEqual(10602, summary["instructions"])
        self.assertEqual(
            {"RET_TERMINATED": 448, "ECX_LOAD_TAIL_JUMP": 65, "DIRECT_JMP_THUNK": 2},
            summary["terminalKinds"],
        )
        self.assertEqual(
            ["0x00460050", "0x00564fd6"],
            summary["symbolPreimage"]["symbolLessEntries"],
        )
        self.assertEqual(sorted(proof.LISTING_QUARANTINE_ENTRIES), summary["listingQuarantine"]["entries"])
        self.assertEqual(520, summary["sourceBoundarySet"]["count"])

    def test_late_poison_changes_only_admissible_row_513_thunk_claim(self) -> None:
        content = proof.late_poison_manifest(self.rows)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "poison.tsv"
            path.write_bytes(content)
            poisoned = proof.pilot.manifest_rows(path)
        changes = []
        for index, (before, after) in enumerate(zip(self.rows, poisoned, strict=True)):
            for key in before:
                if before[key] != after[key]:
                    changes.append((index, before["entry"], key, before[key], after[key]))
        self.assertEqual([
            (512, "0x0055b0b0", "expectedIsThunk", "false", "true"),
            (512, "0x0055b0b0", "expectedThunkTarget", "", "0x00518bf0"),
        ], changes)

    def test_real_admissible_symbol_preimage_and_synthetic_postimage(self) -> None:
        diagnostic = self.repo / "local-lab/global-init515-symbol-diagnostic-20260803"
        diagnostic_manifest = diagnostic / "admissible515.tsv"
        base_output = diagnostic / "base515.tsv"
        base_ready = diagnostic / "base515.ready.json"
        required = [
            diagnostic_manifest, base_output, base_ready,
            self.paths["targetSymbolTool"], self.paths["baseFunctions"],
        ]
        if not all(path.is_file() for path in required):
            self.skipTest("maintainer-local admissible515 symbol diagnostic is absent")
        self.assertEqual(self.manifest.read_bytes(), diagnostic_manifest.read_bytes())
        summary = proof.validate_base_target_symbols(
            base_output,
            base_ready,
            tool=self.paths["targetSymbolTool"],
            manifest=diagnostic_manifest,
        )
        self.assertEqual({
            "outsideTargetSymbols": proof.BASE_OUTSIDE_SYMBOL_COUNT,
            "outsideTargetSymbolsSha256": proof.BASE_OUTSIDE_SYMBOL_SHA256,
        }, summary)
        _, base_rows = proof.envelope.function_rows(self.paths["baseFunctions"])

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "symbols.tsv"
            with output.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(
                    stream,
                    fieldnames=proof.pilot.TARGET_SYMBOL_HEADER,
                    delimiter="\t",
                    lineterminator="\n",
                )
                writer.writeheader()
                for target in self.rows:
                    entry = target["entry"]
                    name = proof.pilot.expected_created_name(target, base_rows)
                    writer.writerow({
                        "entry": entry,
                        "symbolCount": "1",
                        "name": name,
                        "fqname": name,
                        "namespace": "Global",
                        "type": "Function",
                        "source": "DEFAULT",
                        "primary": "true",
                        "dynamic": "false",
                        "external": "false",
                        "pinned": "false",
                    })
            ready = root / "symbols.ready.json"
            payload = {
                "schemaVersion": proof.pilot.TARGET_SYMBOL_SCHEMA,
                "program": proof.envelope.expected_ready_program(),
                "tool": proof.envelope.external_stamp(self.paths["targetSymbolTool"]),
                "manifest": {
                    **proof.envelope.external_stamp(self.manifest),
                    "expectedCount": proof.TARGET_COUNT,
                },
                "output": proof.envelope.external_stamp(output),
                "counts": {
                    "targets": proof.ADMISSIBLE_COUNT,
                    "targetSymbols": proof.ADMISSIBLE_COUNT,
                    "zeroSymbols": 0,
                    "dynamicDefaultLabels": 0,
                    "nonDynamicDefaultFunctions": proof.ADMISSIBLE_COUNT,
                    "outsideTargetSymbols": proof.BASE_OUTSIDE_SYMBOL_COUNT,
                },
                "outsideTargetSymbolsSha256": proof.BASE_OUTSIDE_SYMBOL_SHA256,
            }
            ready.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            proof.validate_applied_target_symbols(
                output,
                ready,
                tool=self.paths["targetSymbolTool"],
                manifest=self.manifest,
                base_rows=base_rows,
                base_summary=summary,
            )
            payload["outsideTargetSymbolsSha256"] = "0" * 64
            ready.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(proof.ProofError, "outside the admissible target set changed"):
                proof.validate_applied_target_symbols(
                    output,
                    ready,
                    tool=self.paths["targetSymbolTool"],
                    manifest=self.manifest,
                    base_rows=base_rows,
                    base_summary=summary,
                )

    def test_synthetic_admissible_inventory_requires_exact_plus_two_symbol_delta(self) -> None:
        base_functions = self.paths["baseFunctions"]
        base_program = self.paths["baseProgram"]
        if not base_functions.is_file() or not base_program.is_file():
            self.skipTest("maintainer-local base inventory is absent")
        header, base_rows = proof.envelope.function_rows(base_functions)
        after = dict(base_rows)
        for target in self.rows:
            entry = target["entry"]
            _, end = target["expectedRanges"].split("-", 1)
            after[entry] = {
                key: value for key, value in {
                    "address": entry,
                    "name": proof.pilot.expected_created_name(target, base_rows),
                    "nameSource": "DEFAULT",
                    "sigSource": proof.pilot.expected_created_sig_source(target, base_rows),
                    "bodyBytes": target["expectedBodyBytes"],
                    "bodyMin": entry,
                    "bodyMax": f"0x{int(end, 16) - 1:08x}",
                    "bodyRanges": "1",
                    "bodyDigest": target["expectedRangeDigest"],
                    "instrCount": target["expectedInstructionCount"],
                    "isThunk": target["expectedIsThunk"],
                    "thunkTarget": target["expectedThunkTarget"],
                    "isExternal": "false",
                }.items()
            }
            for key in header:
                after[entry].setdefault(key, "")
        metrics = proof.envelope.program_metrics(base_program)
        metrics["functions"] = str(proof.EXPECTED_AFTER_COUNT)
        metrics["symbolsDefaultOther"] = str(int(metrics["symbolsDefaultOther"]) + 2)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            after_functions = root / "functions.tsv"
            with after_functions.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=header, delimiter="\t", lineterminator="\n")
                writer.writeheader()
                for entry in sorted(after):
                    writer.writerow(after[entry])
            after_program = root / "program.tsv"
            with after_program.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=("metric", "value"), delimiter="\t", lineterminator="\n")
                writer.writeheader()
                for key, value in metrics.items():
                    writer.writerow({"metric": key, "value": value})
            created = proof.validate_applied_inventory(
                base_functions, base_program, after_functions, after_program,
                self.manifest,
            )
            self.assertEqual(proof.ADMISSIBLE_COUNT, len(created))
            metrics["symbolsDefaultOther"] = str(int(metrics["symbolsDefaultOther"]) + 1)
            with after_program.open("w", encoding="utf-8", newline="") as stream:
                writer = csv.DictWriter(stream, fieldnames=("metric", "value"), delimiter="\t", lineterminator="\n")
                writer.writeheader()
                for key, value in metrics.items():
                    writer.writerow({"metric": key, "value": value})
            with self.assertRaisesRegex(proof.ProofError, "exact function/default-symbol counts"):
                proof.validate_applied_inventory(
                    base_functions, base_program, after_functions, after_program,
                    self.manifest,
                )

    def test_readback_java_ready_requires_admissible515_postimage_count(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tool = root / "tool.java"
            manifest = root / "manifest.tsv"
            output = root / "output.tsv"
            ready = root / "output.ready.json"
            tool.write_text("tool\n", encoding="utf-8")
            manifest.write_text("manifest\n", encoding="utf-8")
            output.write_text("output\n", encoding="utf-8")
            payload = {
                "schemaVersion": proof.envelope.JAVA_READY_SCHEMA,
                "mode": "readback",
                "program": {
                    "name": proof.envelope.PROGRAM_NAME,
                    "executableMd5": proof.envelope.PROGRAM_MD5,
                    "executableSha256": proof.envelope.PROGRAM_SHA256,
                    "imageBase": proof.envelope.IMAGE_BASE,
                    "language": proof.envelope.LANGUAGE,
                    "compilerSpec": proof.envelope.COMPILER_SPEC,
                },
                "tool": proof.envelope.external_stamp(tool),
                "manifest": {
                    **proof.envelope.external_stamp(manifest),
                    "expectedCount": proof.TARGET_COUNT,
                },
                "output": proof.envelope.external_stamp(output),
                "counts": {
                    "targets": proof.TARGET_COUNT,
                    "functionsBefore": proof.EXPECTED_AFTER_COUNT,
                    "functionsTransient": proof.EXPECTED_AFTER_COUNT,
                    "functionManagerViewAfterNestedTransaction": proof.EXPECTED_AFTER_COUNT,
                    "instructionsBefore": proof.envelope.BASE_INSTRUCTION_COUNT,
                    "instructionsAfter": proof.envelope.BASE_INSTRUCTION_COUNT,
                },
                "commitRequested": False,
                "rollbackRequested": False,
                "transactionEndReturnedCommitted": False,
                "loadedStateVerified": True,
                "reopenVerificationRequired": False,
                "namesAuthorized": False,
                "functionKindsBoundByManifest": True,
                "loadedOrTransientEnvelopesVerified": True,
            }
            ready.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            self.assertEqual(
                payload,
                proof.validate_java_ready(
                    ready,
                    output,
                    mode="readback",
                    tool=tool,
                    manifest=manifest,
                    count=proof.TARGET_COUNT,
                ),
            )

            payload["counts"]["functionsBefore"] = proof.pilot.EXPECTED_AFTER_COUNT
            payload["counts"]["functionsTransient"] = proof.pilot.EXPECTED_AFTER_COUNT
            payload["counts"]["functionManagerViewAfterNestedTransaction"] = proof.pilot.EXPECTED_AFTER_COUNT
            ready.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(proof.ProofError, "Java READY counts differ for readback"):
                proof.validate_java_ready(
                    ready,
                    output,
                    mode="readback",
                    tool=tool,
                    manifest=manifest,
                    count=proof.TARGET_COUNT,
                )

    def test_frozen_owner_imports_in_isolated_mode_with_rtti_dependency(self) -> None:
        sources = (
            Path(proof.__file__),
            Path(proof.envelope.__file__),
            Path(proof.pilot.__file__),
            Path(proof.strata.__file__),
            self.repo / "tools/re_rtti_vtables.py",
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tools = root / "tools"
            tools.mkdir()
            for source in sources:
                shutil.copyfile(source, tools / source.name)
            command = [
                sys.executable,
                "-I",
                "-B",
                str(tools / Path(proof.__file__).name),
                "--help",
            ]
            result = subprocess.run(
                command,
                cwd=root,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="strict",
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("listing-admissible 515", result.stdout)

            (tools / "re_rtti_vtables.py").unlink()
            missing = subprocess.run(
                command,
                cwd=root,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="strict",
                check=False,
            )
            self.assertNotEqual(0, missing.returncode)
            self.assertIn("re_rtti_vtables", missing.stderr)

    def test_expected_replica_run_order_and_cardinality(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tools = {
                "backup": root / "backup.py",
                "inventory": root / "inventory.java",
                "envelope": root / "envelope.java",
                "diff": root / "diff.py",
                "symbols": root / "symbols.java",
            }
            common = {
                "proof_root": root,
                "headless": root / "analyzeHeadless.bat",
                "python": root / "python.exe",
                "source_project": root / "source-project",
                "tools": tools,
                "manifest": self.manifest,
                "poison": self.manifest,
                "base_functions": self.paths["baseFunctions"],
            }
            first = proof.expected_replica_run_specs(
                replica_id="replica-a", late_control=True, **common,
            )
            second = proof.expected_replica_run_specs(
                replica_id="replica-b", late_control=False, **common,
            )
        self.assertEqual(15, len(first))
        self.assertEqual(11, len(second))
        self.assertEqual("replica-a-late-poison", first[3]["id"])
        self.assertEqual("replica-a-target-symbols", first[-1]["id"])
        self.assertEqual("replica-b-target-symbols", second[-1]["id"])

    def test_parent_pilot_authority_is_exact(self) -> None:
        required = [self.paths["pilotReady"], self.paths["pilotOwner"]]
        if not all(path.is_file() for path in required):
            self.skipTest("authoritative pilot proof is absent")
        self.assertEqual(proof.PILOT_READY_SHA256, proof.envelope.sha256_file(required[0]))
        self.assertEqual(proof.PILOT_OWNER_SHA256, proof.envelope.sha256_file(required[1]))
        result = proof.expected_parent_verifier_result(self.paths)
        self.assertTrue(result["full520ScratchAuthorized"])
        self.assertFalse(result["livePromotionAuthorized"])

    def test_parent_verifier_receipt_uses_a_noncolliding_observation_key(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_id = "parent-pilot-frozen-verify"
            (root / "runs" / run_id).mkdir(parents=True)
            expected = proof.expected_parent_verifier_result(self.paths)
            text = json.dumps(expected, indent=2, sort_keys=True) + "\n"
            process_result = {"id": run_id, "exitCode": 0}
            with mock.patch.object(
                proof.envelope,
                "run_process",
                return_value=(process_result, text),
            ):
                result = proof.run_parent_verifier(
                    proof_root=root,
                    run_id=run_id,
                    python=Path(sys.executable),
                    paths=self.paths,
                    cwd=root,
                    environment={},
                )
            self.assertEqual(expected, result["observations"]["verifierResult"])
            self.assertNotIn("result", result["observations"])
            receipt = json.loads((root / "runs" / run_id / "run.json").read_text(encoding="utf-8"))
            self.assertEqual(result["observations"], receipt["observations"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
