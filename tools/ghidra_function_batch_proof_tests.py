#!/usr/bin/env python3
"""Focused tests for the prospective CRT98 scratch-proof owner."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import ghidra_function_batch_proof as proof


def fixture_row(
    entry: str,
    *,
    lane: str = "CRT520_STRATIFIED_PILOT_RET_TERMINATED",
    is_thunk: str = "false",
    thunk_target: str = "",
) -> dict[str, str]:
    return {
        "entry": entry,
        "expectedRanges": f"{entry}-0x{int(entry, 16) + 1:08x}",
        "expectedBodyBytes": "1",
        "expectedRangeDigest": "1" * 64,
        "expectedBodyBytesSha256": "2" * 64,
        "expectedInstructionCount": "1",
        "expectedIsThunk": is_thunk,
        "expectedThunkTarget": thunk_target,
        "forbiddenEntries": "",
        "residualEntityKeys": f"R-{entry}",
        "questionIds": f"Q-{entry}",
        "contractIds": f"C-{entry}",
        "promotionLane": lane,
    }


def parse_manifest_bytes(data: bytes) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(data.decode("utf-8")), delimiter="\t")
    return [dict(row) for row in reader]


class BatchProofTests(unittest.TestCase):
    def test_created_names_follow_ghidra_thunk_aliasing(self) -> None:
        ordinary = fixture_row("0x00404ce0")
        thunk = fixture_row(
            "0x00518be0",
            lane="CRT520_STRATIFIED_PILOT_DIRECT_JMP_THUNK",
            is_thunk="true",
            thunk_target="0x00518bf0",
        )
        base = {
            "0x00518bf0": {
                "name": "CCredits__BuildDefaultEntries",
                "sigSource": "USER_DEFINED",
            }
        }
        self.assertEqual("FUN_00404ce0", proof.expected_created_name(ordinary, base))
        self.assertEqual("DEFAULT", proof.expected_created_sig_source(ordinary, base))
        self.assertEqual(
            "CCredits__BuildDefaultEntries",
            proof.expected_created_name(thunk, base),
        )
        self.assertEqual("USER_DEFINED", proof.expected_created_sig_source(thunk, base))
        with self.assertRaises(proof.ProofError):
            proof.expected_created_name(thunk, {})
        with self.assertRaises(proof.ProofError):
            proof.expected_created_sig_source(thunk, {})

    def test_pilot_and_full_rows_allow_only_the_expected_lane_translation(self) -> None:
        pilot = fixture_row("0x00402080")
        full = dict(
            pilot,
            promotionLane="CRT520_FULL_SCRATCH_RET_TERMINATED",
        )
        proof.validate_pilot_row_lineage(pilot, full)

        for field, value in (
            ("questionIds", "Q-swapped"),
            ("expectedInstructionCount", "2"),
            ("promotionLane", "CRT520_FULL_SCRATCH_DIRECT_JMP_THUNK"),
        ):
            poisoned = dict(full, **{field: value})
            with self.subTest(field=field), self.assertRaises(proof.ProofError):
                proof.validate_pilot_row_lineage(pilot, poisoned)

    def test_targeted_controls_are_canonical_and_change_only_preregistered_claims(self) -> None:
        rows = [
            fixture_row(
                "0x00518be0",
                lane="CRT520_STRATIFIED_PILOT_DIRECT_JMP_THUNK",
                is_thunk="true",
                thunk_target="0x00518bf0",
            ),
            fixture_row("0x00453090"),
            fixture_row("0x004f5f30"),
            fixture_row("0x00402080"),
        ]
        controls = proof.control_manifests(rows)
        self.assertEqual(
            set(controls),
            {
                "wrong-thunk-kind.tsv",
                "wrong-thunk-target.tsv",
                "side-tail-as-thunk.tsv",
                "truncated-internal-loop.tsv",
                "lineage-swap.tsv",
            },
        )
        self.assertEqual(5, len({proof.sha256_bytes(value) for value in controls.values()}))

        wrong_kind = parse_manifest_bytes(controls["wrong-thunk-kind.tsv"])[0]
        self.assertEqual(("false", ""), (wrong_kind["expectedIsThunk"], wrong_kind["expectedThunkTarget"]))
        wrong_target = parse_manifest_bytes(controls["wrong-thunk-target.tsv"])[0]
        self.assertEqual("0x0052ff30", wrong_target["expectedThunkTarget"])
        side_tail = parse_manifest_bytes(controls["side-tail-as-thunk.tsv"])[0]
        self.assertEqual(("true", "0x004530a0"), (side_tail["expectedIsThunk"], side_tail["expectedThunkTarget"]))
        truncated = parse_manifest_bytes(controls["truncated-internal-loop.tsv"])[0]
        self.assertEqual(
            ("0x004f5f30-0x004f5f4f", "31", "11"),
            (truncated["expectedRanges"], truncated["expectedBodyBytes"], truncated["expectedInstructionCount"]),
        )
        swapped = parse_manifest_bytes(controls["lineage-swap.tsv"])
        self.assertEqual(rows[1]["questionIds"], swapped[0]["questionIds"])
        self.assertEqual(rows[1]["contractIds"], swapped[0]["contractIds"])

    def test_batch_java_ready_binds_exact_98_target_transaction_counts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            tool = root / "tool.java"
            manifest = root / "manifest.tsv"
            output = root / "output.tsv"
            tool.write_bytes(b"tool")
            manifest.write_bytes(b"manifest")
            output.write_bytes(b"output")
            common = {
                "schemaVersion": proof.envelope.JAVA_READY_SCHEMA,
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
                    "expectedCount": proof.PILOT_COUNT,
                },
                "output": proof.envelope.external_stamp(output),
                "namesAuthorized": False,
                "functionKindsBoundByManifest": True,
                "loadedOrTransientEnvelopesVerified": True,
            }
            for mode, flags, before in (
                ("probe", (False, True, False, False, True), proof.envelope.BASE_FUNCTION_COUNT),
                ("apply", (True, False, False, False, True), proof.envelope.BASE_FUNCTION_COUNT),
                ("readback", (False, False, False, True, False), proof.EXPECTED_AFTER_COUNT),
            ):
                commit, rollback, transaction, loaded, reopen = flags
                payload = {
                    **common,
                    "mode": mode,
                    "counts": {
                        "targets": proof.PILOT_COUNT,
                        "functionsBefore": before,
                        "functionsTransient": before if mode == "readback" else proof.EXPECTED_AFTER_COUNT,
                        "functionManagerViewAfterNestedTransaction": before if mode == "readback" else proof.EXPECTED_AFTER_COUNT,
                        "instructionsBefore": proof.envelope.BASE_INSTRUCTION_COUNT,
                        "instructionsAfter": proof.envelope.BASE_INSTRUCTION_COUNT,
                    },
                    "commitRequested": commit,
                    "rollbackRequested": rollback,
                    "transactionEndReturnedCommitted": transaction,
                    "loadedStateVerified": loaded,
                    "reopenVerificationRequired": reopen,
                }
                ready = root / f"{mode}.json"
                ready.write_text(json.dumps(payload), encoding="utf-8")
                proof.validate_java_ready(
                    ready,
                    output,
                    mode=mode,
                    tool=tool,
                    manifest=manifest,
                    count=proof.PILOT_COUNT,
                )
                payload["namesAuthorized"] = True
                ready.write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaises(proof.ProofError):
                    proof.validate_java_ready(
                        ready,
                        output,
                        mode=mode,
                        tool=tool,
                        manifest=manifest,
                        count=proof.PILOT_COUNT,
                    )

    def test_real_frozen_manifests_preserve_all_98_rows_when_present(self) -> None:
        repo = Path(proof.__file__).resolve().parents[1]
        paths = proof.default_paths(repo)
        if not paths["pilotManifest"].is_file() or not paths["fullManifest"].is_file():
            self.skipTest("maintainer-local CRT v2 bundle is absent")
        rows = proof.validate_manifest_lineage(paths["pilotManifest"], paths["fullManifest"])
        self.assertEqual(proof.PILOT_COUNT, len(rows))
        self.assertTrue(
            {f"0x{entry:08x}" for entry in proof.strata.GRAPH_AWARE_MINIMUM}
            .issubset({row["entry"] for row in rows})
        )
        controls = proof.control_manifests(rows)
        proof.validate_lineage_poison(controls["lineage-swap.tsv"], paths["fullManifest"])

    def test_expected_replica_run_order_is_exact_when_bound_inputs_are_present(self) -> None:
        repo = Path(proof.__file__).resolve().parents[1]
        paths = proof.default_paths(repo)
        if not paths["pilotManifest"].is_file() or not paths["baseFunctions"].is_file():
            self.skipTest("maintainer-local CRT proof inputs are absent")
        rows = proof.validate_manifest_lineage(paths["pilotManifest"], paths["fullManifest"])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            control_paths: dict[str, Path] = {}
            for name, content in proof.control_manifests(rows).items():
                path = root / name
                path.write_bytes(content)
                control_paths[name] = path
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
                "pilot": paths["pilotManifest"],
                "controls": control_paths,
                "base_functions": paths["baseFunctions"],
            }
            first = proof.expected_replica_run_specs(
                replica_id="replica-a", run_controls=True, **common
            )
            second = proof.expected_replica_run_specs(
                replica_id="replica-b", run_controls=False, **common
            )
        self.assertEqual(21, len(first))
        self.assertEqual(11, len(second))
        self.assertEqual(
            [
                "replica-a-copy-control", "replica-a-copy-apply",
                "replica-a-control-baseline",
                "replica-a-control-wrong-thunk-kind", "replica-a-control-wrong-thunk-kind-reopened",
                "replica-a-control-wrong-thunk-target", "replica-a-control-wrong-thunk-target-reopened",
                "replica-a-control-side-tail-as-thunk", "replica-a-control-side-tail-as-thunk-reopened",
                "replica-a-control-truncated-internal-loop", "replica-a-control-truncated-internal-loop-reopened",
                "replica-a-probe", "replica-a-probe-reopened", "replica-a-apply-baseline",
                "replica-a-apply", "replica-a-readback", "replica-a-apply-reopened",
                "replica-a-inventory-diff", "replica-a-reprobe-applied",
                "replica-a-reprobe-applied-reopened", "replica-a-target-symbols",
            ],
            [spec["id"] for spec in first],
        )
        self.assertEqual(
            [
                "replica-b-copy-control", "replica-b-copy-apply",
                "replica-b-control-baseline", "replica-b-probe",
                "replica-b-probe-reopened", "replica-b-apply-baseline",
                "replica-b-apply", "replica-b-readback",
                "replica-b-apply-reopened", "replica-b-inventory-diff",
                "replica-b-target-symbols",
            ],
            [spec["id"] for spec in second],
        )

    def test_real_target_symbol_preimage_and_postimage_when_present(self) -> None:
        repo = Path(proof.__file__).resolve().parents[1]
        diagnostic = repo / "local-lab/crt98-symbol-diagnostic-20260803"
        paths = proof.default_paths(repo)
        manifest = paths["pilotManifest"]
        required = [
            diagnostic / "base-hardened-v2.tsv",
            diagnostic / "base-hardened-v2.ready.json",
            diagnostic / "after-hardened-v2.tsv",
            diagnostic / "after-hardened-v2.ready.json",
            manifest,
            paths["targetSymbolTool"],
            paths["baseFunctions"],
        ]
        if not all(path.is_file() for path in required):
            self.skipTest("maintainer-local target-symbol diagnostic is absent")
        summary = proof.validate_base_target_symbols(
            required[0], required[1], tool=paths["targetSymbolTool"], manifest=manifest,
        )
        _, base_rows = proof.envelope.function_rows(paths["baseFunctions"])
        proof.validate_applied_target_symbols(
            required[2], required[3], tool=paths["targetSymbolTool"], manifest=manifest,
            base_rows=base_rows, base_summary=summary,
        )
        self.assertEqual(86507, summary["outsideTargetSymbols"])
        self.assertEqual(
            "2782e5081330d0a4b1b5b87a1ad3c0323a2de4b4c86d03ebf1111c36b49722fe",
            summary["outsideTargetSymbolsSha256"],
        )

        poisoned = json.loads(required[3].read_text(encoding="utf-8"))
        poisoned["outsideTargetSymbolsSha256"] = "0" * 64
        with tempfile.TemporaryDirectory() as temporary:
            poisoned_ready = Path(temporary) / "poisoned.ready.json"
            poisoned_ready.write_text(
                json.dumps(poisoned, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(proof.ProofError, "outside the target set changed"):
                proof.validate_applied_target_symbols(
                    required[2], poisoned_ready,
                    tool=paths["targetSymbolTool"], manifest=manifest,
                    base_rows=base_rows, base_summary=summary,
                )

    def test_real_v2_inventory_requires_exact_default_symbol_delta_when_present(self) -> None:
        repo = Path(proof.__file__).resolve().parents[1]
        paths = proof.default_paths(repo)
        root = repo / "local-lab/formal-crt98-pilot-20260803-v2"
        after_functions = root / "runs/replica-a-apply-reopened/functions.tsv"
        after_program = root / "runs/replica-a-apply-reopened/program.tsv"
        manifest = root / "inputs/pilot98.tsv"
        required = [
            paths["baseFunctions"], paths["baseProgram"],
            after_functions, after_program, manifest,
        ]
        if not all(path.is_file() for path in required):
            self.skipTest("maintainer-local v2 applied inventory is absent")
        created = proof.validate_applied_inventory(*required)
        self.assertEqual(proof.PILOT_COUNT, len(created))

        rows = after_program.read_text(encoding="utf-8").splitlines()
        poisoned_rows = []
        for row in rows:
            fields = row.split("\t")
            if fields[0] == "symbolsDefaultOther":
                fields[1] = str(int(fields[1]) + 1)
            poisoned_rows.append("\t".join(fields))
        with tempfile.TemporaryDirectory() as temporary:
            poisoned_program = Path(temporary) / "program.tsv"
            poisoned_program.write_text("\n".join(poisoned_rows) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(proof.ProofError, "exact function/default-symbol counts"):
                proof.validate_applied_inventory(
                    paths["baseFunctions"], paths["baseProgram"],
                    after_functions, poisoned_program, manifest,
                )

    def test_candidate_and_ready_names_are_excluded_only_at_their_own_stage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "evidence.bin").write_bytes(b"evidence")
            items = proof.envelope.artifact_items(root)
            ready = {
                "artifacts": {
                    "canonicalization": "sorted relative path with exact bytes and SHA-256; READY excluded",
                    "count": len(items),
                    "items": items,
                }
            }
            candidate = root / "proof.candidate.json"
            candidate.write_text("{}\n", encoding="utf-8")
            proof.verify_artifact_items_for_ready(root, ready, candidate.name)
            candidate.rename(root / "proof.ready.json")
            proof.verify_artifact_items_for_ready(root, ready, "proof.ready.json")
            (root / "unexpected.bin").write_bytes(b"unexpected")
            with self.assertRaisesRegex(proof.ProofError, "artifact set differs"):
                proof.verify_artifact_items_for_ready(root, ready, "proof.ready.json")


if __name__ == "__main__":
    unittest.main(verbosity=2)
