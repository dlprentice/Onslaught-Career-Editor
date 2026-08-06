#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Prospectively prove the listing-admissible 515 of a frozen 520 boundary set.

The historical artifact names call this cohort CRT.  This owner makes no such
semantic claim: it proves only exact manifest-bound function envelopes and
kinds.  Five entries whose current Ghidra instruction listing disagrees with
independent decoding are quarantined for a separate listing-repair proof.  This
owner consumes the authoritative 98-entry instrument proof, mutates only new
disposable clones, and may authorize only the exact 515-entry boundary apply in
the maintainer project through a separate live mutation owner.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Mapping, Sequence


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import ghidra_function_envelope_proof as envelope  # noqa: E402
import ghidra_function_batch_proof as pilot  # noqa: E402
import re_crt_function_strata as strata  # noqa: E402


SCHEMA = "bea.re.ghidra-global-init-admissible515-proof.v1"
STATUS = "READY"
VERDICT = "SURVIVED"
SOURCE_FULL_COUNT = 520
ADMISSIBLE_COUNT = 515
TARGET_COUNT = ADMISSIBLE_COUNT
EXPECTED_AFTER_COUNT = envelope.BASE_FUNCTION_COUNT + ADMISSIBLE_COUNT
EXPECTED_DEFAULT_SYMBOL_DELTA = 2
SYMBOLLESS_ENTRIES = {"0x00460050", "0x00564fd6"}
LISTING_QUARANTINE_ENTRIES = {
    "0x00422370",
    "0x0044aea0",
    "0x00457f80",
    "0x0047bb20",
    "0x00551d90",
}
BASE_OUTSIDE_SYMBOL_COUNT = 86091
BASE_OUTSIDE_SYMBOL_SHA256 = "149b88937826f6a8146eaf24f773fd9bad325b0eacbac576c2a32d4e300649da"

PILOT_READY_SHA256 = "c734b6c09c4adce6780ae5402c30a882935933c249a43cda7c2df26766b07b7d"
PILOT_OWNER_SHA256 = "f76a3e74bd618ef824b0185ce7bebf7476387381e8ace991af72c38560741afa"
FORMAL_READY_SHA256 = "35f8f0a2777c6676e5d8f3313b19ebfe1cdc5c76fd3fff6698619b343e543efd"
STRATA_READY_SHA256 = "b69a04144a4c5af8e18d275742c47bdf733104bd3a652911f46199bff4372d04"
FULL_MANIFEST_SHA256 = "d22c9600f93e84dd203f73ced840d57892cf1d63d5d8209e161ea2ac85c20463"
ADMISSIBLE_MANIFEST_SHA256 = "d9b919ee08d9d8becaa10ce2e248c604730fc7cbb97989da1e8e4d632d4e1abd"
QUARANTINE_MANIFEST_SHA256 = "8128ffc1244cc2f0a8fcb15261359006a505b71c8fca9e9d910139c9669bea17"
ENVELOPE_HELPER_SHA256 = "e20d619c39dd0f2037523b4577860b6640ed76b0be058472834a587192b305e8"
STRATA_HELPER_SHA256 = "620d2e09b2d73273ed4815e6dd1d6c0b7c54a3f824aa1b93bd69520119802ab7"
RTTI_HELPER_SHA256 = "90071f2536e6f511d647b47fda7d323110374fd6c57b15e5360adaa0fd717d1d"
TARGET_SYMBOL_TOOL_SHA256 = "6ea0e6ce2669dd9cb325a052df70cd2f84cd5ebc1319cf5ba8c089691d660327"

LATE_POISON_ENTRY = "0x0055b0b0"
LATE_POISON_TARGET = "0x00518bf0"
LATE_POISON_PATTERN = (
    r"THUNK_KIND_MISMATCH entry=0x0055b0b0 expected=true actual=false"
)
REPROBE_PATTERN = r"probe/apply requires a missing target: 0x00402080"

CLAIM_BOUNDARY = (
    "This proves only the exact natural Ghidra envelopes and manifest-bound function kinds for the 515 listing-admissible entries of a frozen 520-entry Aquila boundary set on two disposable clone pairs.",
    "The five exact quarantined entries remain an explicit instruction-listing repair frontier and are not authorized by this READY.",
    "The historical CRT artifact name and manifest lane labels are not semantic verdicts, and this boundary proof does not authorize treating any manifest entry as library code or excluding it from product-code accounting.",
    "Campaign residual, question, contract, and promotion-lane columns are frozen historical manifest metadata; a separate live owner must rebind every entry to the then-authoritative campaign generation before mutation.",
    "The exact 515-entry boundary apply may proceed only through a separate live owner that first reproduces this READY and the maintainer project's exact preimage.",
    "No semantic names, signatures, behavior contracts, library exclusion, or rebuild parity claim follows from boundary creation.",
    "The checked semantic boundary is the full-function inventory, exact 515 target-symbol rows, and an all-symbol digest outside the target set; every possible internal Ghidra database record is not claimed unchanged.",
    "This READY is unsigned machine-local evidence for a trusted quiescent host, not hostile-actor-resistant proof or proof of historical wall-clock ordering.",
)


ProofError = envelope.ProofError


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProofError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def default_paths(repo: Path) -> dict[str, Path]:
    base = pilot.default_paths(repo)
    pilot_root = repo / "local-lab/formal-crt98-pilot-20260803-v3"
    return {
        **base,
        "pilotProofRoot": pilot_root,
        "pilotReady": pilot_root / "proof.ready.json",
        "pilotOwner": pilot_root / "tools/ghidra_function_batch_proof.py",
        "formalReady": repo / "local-lab/formal-function-envelope-canary-20260803-v3/proof.ready.json",
        "fullManifest": repo / "local-lab/crt520-function-strata-20260803-v2-ready/crt520-full.tsv",
    }


def manifest_rows(path: Path) -> list[dict[str, str]]:
    return pilot.manifest_rows(path, expected_hash=ADMISSIBLE_MANIFEST_SHA256)


def validate_full_manifest(path: Path) -> list[dict[str, str]]:
    rows = pilot.manifest_rows(path, expected_hash=FULL_MANIFEST_SHA256)
    require(len(rows) == SOURCE_FULL_COUNT, "full manifest count differs")
    require([row["entry"] for row in rows] == sorted(row["entry"] for row in rows), "full manifest entries are not sorted")
    require(len({row["entry"] for row in rows}) == SOURCE_FULL_COUNT, "full manifest entry is duplicated")
    require(sum(int(row["expectedBodyBytes"]) for row in rows) == 58157, "full manifest body bytes differ")
    require(sum(int(row["expectedInstructionCount"]) for row in rows) == 10782, "full manifest instruction count differs")
    require(
        [row["entry"] for row in rows if row["expectedIsThunk"] == "true"]
        == ["0x00518be0", "0x0052ff20"],
        "full manifest true-thunk set differs",
    )
    forbidden = sorted({
        entry
        for row in rows
        for entry in row["forbiddenEntries"].split(";")
        if entry
    })
    require(forbidden == [
        "0x00441664", "0x0044967d", "0x00449696", "0x004bc21f",
        "0x004bc22a", "0x004f5f3c", "0x0054284c",
    ], "full manifest forbidden-entry set differs")
    terminal_counts = {
        "RET_TERMINATED": 0,
        "ECX_LOAD_TAIL_JUMP": 0,
        "DIRECT_JMP_THUNK": 0,
    }
    for row in rows:
        lane = row["promotionLane"]
        if "DIRECT_JMP_THUNK" in lane:
            terminal_counts["DIRECT_JMP_THUNK"] += 1
        elif "ECX_LOAD_TAIL_JUMP" in lane:
            terminal_counts["ECX_LOAD_TAIL_JUMP"] += 1
        else:
            require("RET_TERMINATED" in lane, f"unknown full-manifest lane: {lane}")
            terminal_counts["RET_TERMINATED"] += 1
    require(terminal_counts == {
        "RET_TERMINATED": 453,
        "ECX_LOAD_TAIL_JUMP": 65,
        "DIRECT_JMP_THUNK": 2,
    }, "full manifest terminal-kind counts differ")
    require(sum(row["entry"] == LATE_POISON_ENTRY for row in rows) == 1, "late poison entry is absent")
    return rows


def partition_full_manifest(
    rows: Sequence[Mapping[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    admissible = [dict(row) for row in rows if row["entry"] not in LISTING_QUARANTINE_ENTRIES]
    quarantine = [dict(row) for row in rows if row["entry"] in LISTING_QUARANTINE_ENTRIES]
    require(len(admissible) == ADMISSIBLE_COUNT, "listing-admissible manifest count differs")
    require(len(quarantine) == len(LISTING_QUARANTINE_ENTRIES) == 5, "listing quarantine count differs")
    require({row["entry"] for row in quarantine} == LISTING_QUARANTINE_ENTRIES, "listing quarantine entries differ")
    require(
        [row["entry"] for row in admissible] + [row["entry"] for row in quarantine]
        != [row["entry"] for row in rows],
        "partition unexpectedly preserves concatenated source order",
    )
    require(
        {row["entry"] for row in admissible}.isdisjoint(LISTING_QUARANTINE_ENTRIES),
        "listing quarantine leaked into admissible manifest",
    )
    require(
        {row["entry"] for row in admissible} | {row["entry"] for row in quarantine}
        == {row["entry"] for row in rows},
        "full manifest partition is not exhaustive",
    )
    require(sha256_bytes(render_manifest(admissible)) == ADMISSIBLE_MANIFEST_SHA256, "admissible manifest hash differs")
    require(sha256_bytes(render_manifest(quarantine)) == QUARANTINE_MANIFEST_SHA256, "quarantine manifest hash differs")
    require(sum(int(row["expectedBodyBytes"]) for row in admissible) == 57182, "admissible body bytes differ")
    require(sum(int(row["expectedInstructionCount"]) for row in admissible) == 10602, "admissible instruction count differs")
    return admissible, quarantine


def validate_admissible_manifest(path: Path) -> list[dict[str, str]]:
    rows = manifest_rows(path)
    require(len(rows) == ADMISSIBLE_COUNT, "admissible manifest count differs")
    require([row["entry"] for row in rows] == sorted(row["entry"] for row in rows), "admissible entries are not sorted")
    require(len({row["entry"] for row in rows}) == ADMISSIBLE_COUNT, "admissible entry is duplicated")
    require(not ({row["entry"] for row in rows} & LISTING_QUARANTINE_ENTRIES), "admissible manifest contains a quarantine entry")
    require(sum(int(row["expectedBodyBytes"]) for row in rows) == 57182, "admissible body bytes differ")
    require(sum(int(row["expectedInstructionCount"]) for row in rows) == 10602, "admissible instruction count differs")
    require(sum(row["entry"] == LATE_POISON_ENTRY for row in rows) == 1, "admissible late poison entry is absent")
    return rows


def render_manifest(rows: Sequence[Mapping[str, str]]) -> bytes:
    return pilot.render_manifest(rows)


def late_poison_manifest(rows: Sequence[Mapping[str, str]]) -> bytes:
    poisoned = [dict(row) for row in rows]
    index = next(i for i, row in enumerate(poisoned) if row["entry"] == LATE_POISON_ENTRY)
    require(index == 512, "late poison is not admissible row 513")
    require(poisoned[index]["expectedIsThunk"] == "false", "late poison preimage kind differs")
    require(poisoned[index]["expectedThunkTarget"] == "", "late poison preimage target differs")
    poisoned[index]["expectedIsThunk"] = "true"
    poisoned[index]["expectedThunkTarget"] = LATE_POISON_TARGET
    content = render_manifest(poisoned)
    require(content != render_manifest(rows), "late poison did not change the manifest")
    return content


def expected_manifest_summary(
    rows: Sequence[Mapping[str, str]],
    quarantine: Sequence[Mapping[str, str]],
) -> dict[str, object]:
    return {
        "count": ADMISSIBLE_COUNT,
        "sha256": ADMISSIBLE_MANIFEST_SHA256,
        "entries": [row["entry"] for row in rows],
        "bodyBytes": 57182,
        "instructions": 10602,
        "terminalKinds": {
            "RET_TERMINATED": 448,
            "ECX_LOAD_TAIL_JUMP": 65,
            "DIRECT_JMP_THUNK": 2,
        },
        "trueThunks": ["0x00518be0", "0x0052ff20"],
        "forbiddenEntries": sorted({
            entry for row in rows for entry in row["forbiddenEntries"].split(";") if entry
        }),
        "symbolPreimage": {
            "dynamicDefaultLabels": 513,
            "symbolLessEntries": sorted(SYMBOLLESS_ENTRIES),
            "outsideTargetSymbols": BASE_OUTSIDE_SYMBOL_COUNT,
            "outsideTargetSymbolsSha256": BASE_OUTSIDE_SYMBOL_SHA256,
        },
        "sourceBoundarySet": {
            "count": SOURCE_FULL_COUNT,
            "sha256": FULL_MANIFEST_SHA256,
        },
        "listingQuarantine": {
            "count": 5,
            "sha256": QUARANTINE_MANIFEST_SHA256,
            "entries": [row["entry"] for row in quarantine],
            "bodyBytes": 975,
            "instructions": 180,
            "authorization": "SEPARATE_LISTING_REPAIR_PROOF_REQUIRED",
        },
    }


def validate_base_target_symbols(
    output: Path,
    ready_path: Path,
    *,
    tool: Path,
    manifest: Path,
) -> dict[str, object]:
    ready = pilot.validate_target_symbol_ready(
        ready_path, output, tool=tool, manifest=manifest, count=TARGET_COUNT,
    )
    rows = pilot.target_symbol_rows(output)
    targets = manifest_rows(manifest)
    require(len(rows) == len(targets) == TARGET_COUNT, "base target-symbol row count differs")
    for row, target in zip(rows, targets, strict=True):
        entry = target["entry"]
        absent = entry in SYMBOLLESS_ENTRIES
        expected = {
            "entry": entry,
            "symbolCount": "0" if absent else "1",
            "name": "" if absent else f"LAB_{entry[2:]}",
            "fqname": "" if absent else f"LAB_{entry[2:]}",
            "namespace": "" if absent else "Global",
            "type": "" if absent else "Label",
            "source": "" if absent else "DEFAULT",
            "primary": "" if absent else "true",
            "dynamic": "" if absent else "true",
            "external": "" if absent else "false",
            "pinned": "" if absent else "false",
        }
        require(row == expected, f"base target-symbol row differs: {entry}")
    require(ready["counts"] == {
        "targets": TARGET_COUNT,
        "targetSymbols": 513,
        "zeroSymbols": 2,
        "dynamicDefaultLabels": 513,
        "nonDynamicDefaultFunctions": 0,
        "outsideTargetSymbols": BASE_OUTSIDE_SYMBOL_COUNT,
    }, "base target-symbol counts differ")
    require(
        ready["outsideTargetSymbolsSha256"] == BASE_OUTSIDE_SYMBOL_SHA256,
        "base outside-target symbol digest differs",
    )
    return {
        "outsideTargetSymbols": BASE_OUTSIDE_SYMBOL_COUNT,
        "outsideTargetSymbolsSha256": BASE_OUTSIDE_SYMBOL_SHA256,
    }


def validate_applied_target_symbols(
    output: Path,
    ready_path: Path,
    *,
    tool: Path,
    manifest: Path,
    base_rows: Mapping[str, Mapping[str, str]],
    base_summary: Mapping[str, object],
) -> None:
    ready = pilot.validate_target_symbol_ready(
        ready_path, output, tool=tool, manifest=manifest, count=TARGET_COUNT,
    )
    rows = pilot.target_symbol_rows(output)
    targets = manifest_rows(manifest)
    require(len(rows) == len(targets) == TARGET_COUNT, "applied target-symbol row count differs")
    for row, target in zip(rows, targets, strict=True):
        entry = target["entry"]
        name = pilot.expected_created_name(target, base_rows)
        require(row == {
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
        }, f"applied target-symbol row differs: {entry}")
    require(ready["counts"] == {
        "targets": TARGET_COUNT,
        "targetSymbols": TARGET_COUNT,
        "zeroSymbols": 0,
        "dynamicDefaultLabels": 0,
        "nonDynamicDefaultFunctions": TARGET_COUNT,
        "outsideTargetSymbols": base_summary["outsideTargetSymbols"],
    }, "applied target-symbol counts differ")
    require(
        ready["outsideTargetSymbolsSha256"] == base_summary["outsideTargetSymbolsSha256"],
        "a symbol outside the admissible target set changed",
    )


def validate_applied_inventory(
    base_functions: Path,
    base_program: Path,
    after_functions: Path,
    after_program: Path,
    manifest: Path,
) -> dict[str, dict[str, str]]:
    before_header, before = envelope.function_rows(base_functions)
    after_header, after = envelope.function_rows(after_functions)
    targets = manifest_rows(manifest)
    target_by_entry = {row["entry"]: row for row in targets}
    require(before_header == after_header, "function inventory header changed")
    require(sorted(set(after) - set(before)) == sorted(target_by_entry), "created function set differs")
    require(not (set(before) - set(after)), "a preexisting function was destroyed")
    for entry, row in before.items():
        require(after.get(entry) == row, f"preexisting function row changed: {entry}")
    forbidden = {
        entry for target in targets for entry in target["forbiddenEntries"].split(";") if entry
    }
    require(not forbidden.intersection(after), "a forbidden internal branch became a function")
    for entry, target in target_by_entry.items():
        row = after[entry]
        ranges = target["expectedRanges"].split(";")
        require(len(ranges) == 1, f"admissible target unexpectedly has multiple ranges: {entry}")
        start, end = ranges[0].split("-", 1)
        expected = {
            "address": entry,
            "name": pilot.expected_created_name(target, before),
            "nameSource": "DEFAULT",
            "sigSource": pilot.expected_created_sig_source(target, before),
            "bodyBytes": target["expectedBodyBytes"],
            "bodyMin": entry,
            "bodyMax": f"0x{int(end, 16) - 1:08x}",
            "bodyRanges": "1",
            "bodyDigest": target["expectedRangeDigest"],
            "instrCount": target["expectedInstructionCount"],
            "isThunk": target["expectedIsThunk"],
            "thunkTarget": target["expectedThunkTarget"],
            "isExternal": "false",
        }
        require(start == entry, f"full range does not start at entry: {entry}")
        for field, value in expected.items():
            require(row.get(field) == value, f"created row {entry} {field} differs")
    before_metrics = envelope.program_metrics(base_program)
    after_metrics = envelope.program_metrics(after_program)
    expected_metrics = dict(before_metrics)
    expected_metrics["functions"] = str(EXPECTED_AFTER_COUNT)
    require("symbolsDefaultOther" in before_metrics, "base program lacks default-symbol count")
    expected_metrics["symbolsDefaultOther"] = str(
        int(before_metrics["symbolsDefaultOther"]) + EXPECTED_DEFAULT_SYMBOL_DELTA
    )
    require(
        after_metrics == expected_metrics,
        "program metrics changed outside exact function/default-symbol counts",
    )
    return {entry: after[entry] for entry in sorted(target_by_entry)}


def validate_output(
    path: Path,
    manifest: Path,
    *,
    mode: str,
    base_rows: Mapping[str, Mapping[str, str]],
) -> list[dict[str, str]]:
    return pilot.validate_output(
        path, manifest, mode=mode, count=TARGET_COUNT, base_rows=base_rows,
    )


def validate_inventory_diff_payload(path: Path, expected_entries: Sequence[str]) -> dict[str, object]:
    payload = envelope.read_json(path, "admissible515 inventory diff")
    require(set(payload) == {
        "beforeFile", "afterFile", "counts", "dangerous", "created",
        "destroyed", "changesByField",
    }, "diff payload shape differs")
    counts = payload.get("counts", {})
    require(counts.get("before") == envelope.BASE_FUNCTION_COUNT, "diff before count differs")
    require(counts.get("after") == EXPECTED_AFTER_COUNT, "diff after count differs")
    require(counts.get("created") == TARGET_COUNT and counts.get("destroyed") == 0, "diff created/destroyed differs")
    for key in (
        "boundsChanged", "callingConvChanged", "instrCountChanged", "namesChanged",
        "noReturnChanged", "paramCountChanged", "returnTypeChanged", "sigSourceChanged",
        "signaturesChanged", "thunkFlagChanged",
    ):
        require(counts.get(key) == 0, f"diff reports {key}")
    require(all(value in (0, [], {}) for value in payload.get("dangerous", {}).values()), "diff reports dangerous changes")
    require(
        [row.get("address") for row in payload.get("created", [])] == list(expected_entries),
        "diff created entry list differs",
    )
    require(payload.get("destroyed") == [], "diff destroyed rows differ")
    require(all(value == [] for value in payload.get("changesByField", {}).values()), "diff field-change rows differ")
    return payload


def compare_to_base(
    functions: Path,
    program: Path,
    base_functions: Path,
    base_program: Path,
    label: str,
) -> None:
    envelope.compare_inventory_to_base(
        functions, program, base_functions, base_program, label,
    )


def validate_java_ready(
    ready_path: Path,
    output_path: Path,
    *,
    mode: str,
    tool: Path,
    manifest: Path,
    count: int,
) -> dict:
    """Validate the Java envelope against this owner's 515-function state."""
    ready = envelope.read_json(ready_path, "admissible515 Java READY")
    require(
        ready.get("schemaVersion") == envelope.JAVA_READY_SCHEMA
        and ready.get("mode") == mode,
        "Java READY schema/mode differs",
    )
    require(ready.get("program") == {
        "name": envelope.PROGRAM_NAME,
        "executableMd5": envelope.PROGRAM_MD5,
        "executableSha256": envelope.PROGRAM_SHA256,
        "imageBase": envelope.IMAGE_BASE,
        "language": envelope.LANGUAGE,
        "compilerSpec": envelope.COMPILER_SPEC,
    }, "Java READY program identity differs")
    require(ready.get("tool") == envelope.external_stamp(tool), "Java READY tool binding differs")
    expected_manifest = envelope.external_stamp(manifest)
    expected_manifest["expectedCount"] = count
    require(ready.get("manifest") == expected_manifest, "Java READY manifest binding differs")
    require(ready.get("output") == envelope.external_stamp(output_path), "Java READY output binding differs")
    before = EXPECTED_AFTER_COUNT if mode == "readback" else envelope.BASE_FUNCTION_COUNT
    expected_counts = {
        "targets": count,
        "functionsBefore": before,
        "functionsTransient": before if mode == "readback" else before + count,
        "functionManagerViewAfterNestedTransaction": before if mode == "readback" else before + count,
        "instructionsBefore": envelope.BASE_INSTRUCTION_COUNT,
        "instructionsAfter": envelope.BASE_INSTRUCTION_COUNT,
    }
    require(ready.get("counts") == expected_counts, f"Java READY counts differ for {mode}")
    expected_flags = {
        "probe": (False, True, False, False, True),
        "apply": (True, False, False, False, True),
        "readback": (False, False, False, True, False),
    }[mode]
    actual_flags = (
        ready.get("commitRequested"),
        ready.get("rollbackRequested"),
        ready.get("transactionEndReturnedCommitted"),
        ready.get("loadedStateVerified"),
        ready.get("reopenVerificationRequired"),
    )
    require(actual_flags == expected_flags, f"Java READY transaction flags differ for {mode}")
    require(ready.get("namesAuthorized") is False, "Java READY authorizes names")
    require(ready.get("functionKindsBoundByManifest") is True, "Java READY lost function-kind binding")
    require(
        ready.get("loadedOrTransientEnvelopesVerified") is True,
        "Java READY lost envelope verification",
    )
    return ready


def run_valid_envelope(
    *,
    proof_root: Path,
    run_id: str,
    headless: Path,
    project: Path,
    tool: Path,
    manifest: Path,
    mode: str,
    cwd: Path,
    environment: dict[str, str],
    base_rows: Mapping[str, Mapping[str, str]],
) -> tuple[dict[str, object], Path, list[dict[str, str]]]:
    result, output, ready, text = envelope.run_envelope(
        proof_root=proof_root,
        run_id=run_id,
        headless=headless,
        project_root=project,
        tool=tool,
        manifest=manifest,
        expected_count=TARGET_COUNT,
        mode=mode,
        cwd=cwd,
        environment=environment,
    )
    require(
        result["exitCode"] == 0 and f"FUNCTION_ENVELOPE_OK mode={mode}" in text,
        f"{run_id} failed",
    )
    envelope.require_clean_success_log(text, run_id)
    rows = validate_output(output, manifest, mode=mode, base_rows=base_rows)
    java_ready = validate_java_ready(
        ready, output, mode=mode, tool=tool, manifest=manifest, count=TARGET_COUNT,
    )
    receipt = envelope.finish_run(
        proof_root,
        result,
        output=envelope.stamp(output, proof_root),
        ready=envelope.stamp(ready, proof_root),
        rowsSha256=sha256_bytes(canonical_json(rows)),
        javaReady=java_ready,
    )
    return receipt, output, rows


def run_late_poison(
    *,
    proof_root: Path,
    run_id: str,
    headless: Path,
    project: Path,
    tool: Path,
    manifest: Path,
    cwd: Path,
    environment: dict[str, str],
) -> dict[str, object]:
    result, output, ready, text = envelope.run_envelope(
        proof_root=proof_root,
        run_id=run_id,
        headless=headless,
        project_root=project,
        tool=tool,
        manifest=manifest,
        expected_count=TARGET_COUNT,
        mode="probe",
        cwd=cwd,
        environment=environment,
    )
    return envelope.require_rejection(
        proof_root=proof_root,
        result=result,
        output=output,
        ready=ready,
        text=text,
        expected_pattern=LATE_POISON_PATTERN,
        mutation_tainted=True,
    )


def run_inventory_diff(
    *,
    proof_root: Path,
    run_id: str,
    python: Path,
    tool: Path,
    before: Path,
    after: Path,
    manifest: Path,
    cwd: Path,
    environment: dict[str, str],
) -> dict[str, object]:
    run_root = proof_root / "runs" / run_id
    output = run_root / "inventory-diff.json"
    result, text = envelope.run_process(
        proof_root=proof_root,
        run_id=run_id,
        argv=envelope.diff_argv(python, tool, before, after, output),
        cwd=cwd,
        environment=environment,
    )
    payload = validate_inventory_diff_payload(
        output, [row["entry"] for row in manifest_rows(manifest)],
    )
    require(result["exitCode"] == 0, "inventory diff process failed")
    return envelope.finish_run(
        proof_root,
        result,
        diff=envelope.stamp(output, proof_root),
        stdoutSha256=sha256_bytes(text.encode("utf-8")),
        payloadSha256=sha256_bytes(canonical_json(payload)),
    )


def expected_parent_verifier_result(paths: Mapping[str, Path]) -> dict[str, object]:
    return {
        "schema": pilot.SCHEMA,
        "verdict": pilot.VERDICT,
        "ready": str(paths["pilotReady"].resolve()),
        "readySha256": PILOT_READY_SHA256,
        "replicas": 2,
        "retainedProjectsReopenedReadOnly": 5,
        "pilotTargets": pilot.PILOT_COUNT,
        "publicationStatus": "READY",
        "full520ScratchAuthorized": True,
        "livePromotionAuthorized": False,
    }


def parent_verifier_argv(python: Path, paths: Mapping[str, Path]) -> list[str]:
    return [
        str(python.resolve()), "-I", "-B", str(paths["pilotOwner"].resolve()),
        "--verify-ready", str(paths["pilotReady"].resolve()),
    ]


def run_parent_verifier(
    *,
    proof_root: Path,
    run_id: str,
    python: Path,
    paths: Mapping[str, Path],
    cwd: Path,
    environment: dict[str, str],
) -> dict[str, object]:
    result, text = envelope.run_process(
        proof_root=proof_root,
        run_id=run_id,
        argv=parent_verifier_argv(python, paths),
        cwd=cwd,
        environment=environment,
        timeout_seconds=900,
    )
    require(result["exitCode"] == 0, "parent pilot frozen verifier failed")
    require(text.endswith("\n") and text.count("\n") > 1, "parent verifier output is malformed")
    try:
        observed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProofError("parent verifier output is not JSON") from exc
    expected = expected_parent_verifier_result(paths)
    require(observed == expected, "parent verifier result differs")
    return envelope.finish_run(
        proof_root,
        result,
        verifierResult=observed,
        stdoutSha256=sha256_bytes(text.encode("utf-8")),
    )


def run_replica(
    *,
    proof_root: Path,
    replica: str,
    run_late_control: bool,
    headless: Path,
    python: Path,
    source_project: Path,
    tools: Mapping[str, Path],
    manifest: Path,
    poison: Path,
    base_functions: Path,
    base_program: Path,
    base_symbol_summary: Mapping[str, object],
    cwd: Path,
    environment: dict[str, str],
) -> dict[str, object]:
    control_project = proof_root / "projects" / f"{replica}-control"
    apply_project = proof_root / "projects" / f"{replica}-apply"
    runs: list[dict[str, object]] = []
    _, base_rows = envelope.function_rows(base_functions)

    runs.append(envelope.invoke_backup_copy(
        proof_root=proof_root,
        run_id=f"{replica}-copy-control",
        python=python,
        backup_tool=tools["backup"],
        source=source_project,
        destination=control_project,
        cwd=cwd,
        environment=environment,
    ))
    runs.append(envelope.invoke_backup_copy(
        proof_root=proof_root,
        run_id=f"{replica}-copy-apply",
        python=python,
        backup_tool=tools["backup"],
        source=source_project,
        destination=apply_project,
        cwd=cwd,
        environment=environment,
    ))

    baseline, functions, program = envelope.run_inventory(
        proof_root=proof_root,
        run_id=f"{replica}-control-baseline",
        headless=headless,
        project_root=control_project,
        inventory_tool=tools["inventory"],
        cwd=cwd,
        environment=environment,
    )
    compare_to_base(functions, program, base_functions, base_program, f"{replica} control baseline")
    runs.append(baseline)

    if run_late_control:
        runs.append(run_late_poison(
            proof_root=proof_root,
            run_id=f"{replica}-late-poison",
            headless=headless,
            project=control_project,
            tool=tools["envelope"],
            manifest=poison,
            cwd=cwd,
            environment=environment,
        ))
        reopened, functions, program = envelope.run_inventory(
            proof_root=proof_root,
            run_id=f"{replica}-late-poison-reopened",
            headless=headless,
            project_root=control_project,
            inventory_tool=tools["inventory"],
            cwd=cwd,
            environment=environment,
        )
        compare_to_base(functions, program, base_functions, base_program, f"{replica} late-poison rollback")
        runs.append(reopened)

    probe, probe_output, probe_rows = run_valid_envelope(
        proof_root=proof_root,
        run_id=f"{replica}-probe",
        headless=headless,
        project=control_project,
        tool=tools["envelope"],
        manifest=manifest,
        mode="probe",
        cwd=cwd,
        environment=environment,
        base_rows=base_rows,
    )
    runs.append(probe)
    reopened, functions, program = envelope.run_inventory(
        proof_root=proof_root,
        run_id=f"{replica}-probe-reopened",
        headless=headless,
        project_root=control_project,
        inventory_tool=tools["inventory"],
        cwd=cwd,
        environment=environment,
    )
    compare_to_base(functions, program, base_functions, base_program, f"{replica} probe rollback")
    runs.append(reopened)

    apply_baseline, functions, program = envelope.run_inventory(
        proof_root=proof_root,
        run_id=f"{replica}-apply-baseline",
        headless=headless,
        project_root=apply_project,
        inventory_tool=tools["inventory"],
        cwd=cwd,
        environment=environment,
    )
    compare_to_base(functions, program, base_functions, base_program, f"{replica} apply baseline")
    runs.append(apply_baseline)

    apply, apply_output, apply_rows = run_valid_envelope(
        proof_root=proof_root,
        run_id=f"{replica}-apply",
        headless=headless,
        project=apply_project,
        tool=tools["envelope"],
        manifest=manifest,
        mode="apply",
        cwd=cwd,
        environment=environment,
        base_rows=base_rows,
    )
    runs.append(apply)
    readback, readback_output, readback_rows = run_valid_envelope(
        proof_root=proof_root,
        run_id=f"{replica}-readback",
        headless=headless,
        project=apply_project,
        tool=tools["envelope"],
        manifest=manifest,
        mode="readback",
        cwd=cwd,
        environment=environment,
        base_rows=base_rows,
    )
    runs.append(readback)
    require(
        [{k: v for k, v in row.items() if k not in {"status", "note"}} for row in apply_rows]
        == [{k: v for k, v in row.items() if k not in {"status", "note"}} for row in readback_rows],
        f"{replica} apply/readback rows differ",
    )

    after, after_functions, after_program = envelope.run_inventory(
        proof_root=proof_root,
        run_id=f"{replica}-apply-reopened",
        headless=headless,
        project_root=apply_project,
        inventory_tool=tools["inventory"],
        cwd=cwd,
        environment=environment,
    )
    created = validate_applied_inventory(
        base_functions, base_program, after_functions, after_program, manifest,
    )
    runs.append(after)
    runs.append(run_inventory_diff(
        proof_root=proof_root,
        run_id=f"{replica}-inventory-diff",
        python=python,
        tool=tools["diff"],
        before=base_functions,
        after=after_functions,
        manifest=manifest,
        cwd=cwd,
        environment=environment,
    ))

    if run_late_control:
        result, output, java_ready, text = envelope.run_envelope(
            proof_root=proof_root,
            run_id=f"{replica}-reprobe-applied",
            headless=headless,
            project_root=apply_project,
            tool=tools["envelope"],
            manifest=manifest,
            expected_count=TARGET_COUNT,
            mode="probe",
            cwd=cwd,
            environment=environment,
        )
        runs.append(envelope.require_rejection(
            proof_root=proof_root,
            result=result,
            output=output,
            ready=java_ready,
            text=text,
            expected_pattern=REPROBE_PATTERN,
            mutation_tainted=False,
        ))
        post, post_functions, post_program = envelope.run_inventory(
            proof_root=proof_root,
            run_id=f"{replica}-reprobe-applied-reopened",
            headless=headless,
            project_root=apply_project,
            inventory_tool=tools["inventory"],
            cwd=cwd,
            environment=environment,
        )
        require(post_functions.read_bytes() == after_functions.read_bytes(), "reprobe changed applied functions")
        require(post_program.read_bytes() == after_program.read_bytes(), "reprobe changed applied program")
        runs.append(post)

    symbol_run, symbol_output, symbol_ready = pilot.run_target_symbol_inventory(
        proof_root=proof_root,
        run_id=f"{replica}-target-symbols",
        headless=headless,
        project=apply_project,
        tool=tools["symbols"],
        manifest=manifest,
        count=TARGET_COUNT,
        cwd=cwd,
        environment=environment,
    )
    validate_applied_target_symbols(
        symbol_output,
        symbol_ready,
        tool=tools["symbols"],
        manifest=manifest,
        base_rows=base_rows,
        base_summary=base_symbol_summary,
    )
    runs.append(symbol_run)

    expected_runs = 15 if run_late_control else 11
    require(len(runs) == expected_runs, f"{replica} run count differs")
    return {
        "id": replica,
        "controlProject": str(control_project.resolve()),
        "applyProject": str(apply_project.resolve()),
        "lateControlRun": run_late_control,
        "runs": [run["receipt"] for run in runs],
        "probeOutput": envelope.stamp(probe_output, proof_root),
        "applyOutput": envelope.stamp(apply_output, proof_root),
        "readbackOutput": envelope.stamp(readback_output, proof_root),
        "afterFunctions": envelope.stamp(after_functions, proof_root),
        "afterProgram": envelope.stamp(after_program, proof_root),
        "targetSymbols": envelope.stamp(symbol_output, proof_root),
        "targetSymbolsReady": envelope.stamp(symbol_ready, proof_root),
        "outsideTargetSymbolsSha256": base_symbol_summary["outsideTargetSymbolsSha256"],
        "createdRowsSha256": sha256_bytes(canonical_json(created)),
        "createdEntries": sorted(created),
        "controlProjectFileSetSha256": envelope.rows_digest(envelope.project_rows(control_project)),
        "applyProjectFileSetSha256": envelope.rows_digest(envelope.project_rows(apply_project)),
    }


def expected_checks() -> dict[str, object]:
    return {
        "parentPilotFrozenVerifierSurvived": True,
        "replicationCount": 2,
        "admissibleTargets": ADMISSIBLE_COUNT,
        "quarantinedListingTargets": 5,
        "freshControlClones": 2,
        "freshApplyClones": 2,
        "lateAdmissibleRow513PoisonRejectedAndRolledBack": True,
        "admissibleProbeRollbackReopenedExact": True,
        "applyPersistedOnlyOnApplyClones": True,
        "separateProcessReadbackExact": True,
        "preexistingFunctionRowsUnchanged": True,
        "createdFunctionCount": TARGET_COUNT,
        "exactTargetSymbolPreimageAndPostimage": True,
        "outsideTargetSymbolDigestUnchanged": True,
        "defaultSymbolCountDelta": EXPECTED_DEFAULT_SYMBOL_DELTA,
        "replicasSemanticallyEquivalent": True,
        "reprobeAppliedCloneRejectedWithoutChange": True,
        "sourceProjectUnchanged": True,
        "semanticPromotionAuthorized": False,
        "libraryExclusionAuthorized": False,
        "rebuildParityAuthorized": False,
        "maintainerProjectOpened": False,
    }


def source_stamp(source: Path, snapshot: Path, proof_root: Path) -> dict[str, object]:
    return {
        "source": envelope.external_stamp(source),
        "snapshot": envelope.stamp(snapshot, proof_root),
    }


def snapshot_exact(
    source: Path,
    destination: Path,
    expected_hash: str,
    proof_root: Path,
) -> dict[str, object]:
    envelope.snapshot_file(source, destination, expected_hash=expected_hash)
    return source_stamp(source, destination, proof_root)


def run_proof(args: argparse.Namespace) -> dict[str, object]:
    repo = envelope.require_plain_directory(Path(args.repo_root), "repository root")
    require((repo / "README.MD").is_file() and (repo / "tools").is_dir(), "not the Onslaught repository")
    require(
        Path(__file__).resolve() == (repo / "tools" / Path(__file__).name).resolve(),
        "run only the landed full-boundary owner",
    )
    require(envelope.sha256_file(Path(envelope.__file__)) == ENVELOPE_HELPER_SHA256, "envelope helper hash differs")
    require(envelope.sha256_file(Path(pilot.__file__)) == PILOT_OWNER_SHA256, "pilot helper hash differs")
    require(envelope.sha256_file(Path(strata.__file__)) == STRATA_HELPER_SHA256, "strata helper hash differs")
    require(
        envelope.sha256_file(repo / "tools/re_rtti_vtables.py") == RTTI_HELPER_SHA256,
        "RTTI helper hash differs",
    )
    paths = default_paths(repo)
    proof_root = envelope.lexical_absolute(Path(args.proof_root))
    local_lab = envelope.require_plain_directory(repo / "local-lab", "repository local-lab")
    require(proof_root.parent.resolve() == local_lab.resolve(), "proof root must be one direct local-lab child")
    require(not proof_root.exists(), "proof root already exists")

    source_project = envelope.require_plain_directory(paths["sourceProject"], "source project")
    source_rows_before = envelope.validate_source_project(source_project)
    pilot_ready_source = envelope.require_plain_file(
        paths["pilotReady"], "pilot proof READY", expected_hash=PILOT_READY_SHA256,
    )
    pilot_owner_source = envelope.require_plain_file(
        paths["pilotOwner"], "pilot frozen owner", expected_hash=PILOT_OWNER_SHA256,
    )
    formal_ready_source = envelope.require_plain_file(
        paths["formalReady"], "formal envelope READY", expected_hash=FORMAL_READY_SHA256,
    )
    bundle_source = envelope.require_plain_directory(paths["strataBundle"], "strata bundle")
    require(envelope.sha256_file(bundle_source / "READY.json") == STRATA_READY_SHA256, "strata READY hash differs")
    strata.verify_bundle(repo, formal_ready_source, bundle_source)
    full_rows = validate_full_manifest(paths["fullManifest"])
    admissible_rows, quarantine_rows = partition_full_manifest(full_rows)
    base_functions_source = envelope.require_plain_file(
        paths["baseFunctions"], "base functions", expected_hash=envelope.BASE_FUNCTIONS_SHA256,
    )
    base_program_source = envelope.require_plain_file(
        paths["baseProgram"], "base program", expected_hash=envelope.BASE_PROGRAM_SHA256,
    )
    envelope.validate_base_inventory(base_functions_source, base_program_source)

    envelope.ensure_plain_directory(proof_root, "proof root")
    for name in ("inputs", "inputs/toolchain", "tools", "runs", "projects", "work"):
        envelope.ensure_plain_directory(proof_root / name, f"proof {name}")

    input_specs = {
        "pilot98-proof.ready.json": (pilot_ready_source, PILOT_READY_SHA256),
        "pilot98-frozen-owner.py": (pilot_owner_source, PILOT_OWNER_SHA256),
        "formal-envelope-proof.ready.json": (formal_ready_source, FORMAL_READY_SHA256),
        "strata.READY.json": (bundle_source / "READY.json", STRATA_READY_SHA256),
        "source-full520.tsv": (paths["fullManifest"], FULL_MANIFEST_SHA256),
        "base-functions.tsv": (base_functions_source, envelope.BASE_FUNCTIONS_SHA256),
        "base-program.tsv": (base_program_source, envelope.BASE_PROGRAM_SHA256),
    }
    input_graph: dict[str, object] = {}
    for name, (source, digest) in input_specs.items():
        destination = proof_root / "inputs" / name
        input_graph[name] = snapshot_exact(source, destination, digest, proof_root)

    manifest = proof_root / "inputs/admissible515.tsv"
    quarantine = proof_root / "inputs/listing-quarantine5.tsv"
    envelope.write_new(manifest, render_manifest(admissible_rows))
    envelope.write_new(quarantine, render_manifest(quarantine_rows))
    validate_admissible_manifest(manifest)
    require(envelope.sha256_file(quarantine) == QUARANTINE_MANIFEST_SHA256, "written quarantine hash differs")
    base_functions = proof_root / "inputs/base-functions.tsv"
    base_program = proof_root / "inputs/base-program.tsv"
    poison = proof_root / "inputs/admissible515-late-row513-poison.tsv"
    envelope.write_new(poison, late_poison_manifest(admissible_rows))

    tools: dict[str, Path] = {}
    tool_graph: dict[str, object] = {}
    for role, name in envelope.EXPECTED_TOOL_NAMES.items():
        source = repo / "tools" / name
        destination = proof_root / "tools" / name
        tool_graph[role] = snapshot_exact(
            source, destination, envelope.EXPECTED_TOOL_SHA256[role], proof_root,
        )
        tools[role] = destination
    extra_tool_specs = (
        ("envelopeHelper", Path(envelope.__file__).resolve(), ENVELOPE_HELPER_SHA256),
        ("pilotHelper", Path(pilot.__file__).resolve(), PILOT_OWNER_SHA256),
        ("strataHelper", Path(strata.__file__).resolve(), STRATA_HELPER_SHA256),
        ("rttiHelper", repo / "tools/re_rtti_vtables.py", RTTI_HELPER_SHA256),
        ("targetSymbolInventory", paths["targetSymbolTool"], TARGET_SYMBOL_TOOL_SHA256),
        ("runner", Path(__file__).resolve(), envelope.sha256_file(Path(__file__))),
    )
    for role, source, digest in extra_tool_specs:
        destination = proof_root / "tools" / source.name
        tool_graph[role] = snapshot_exact(source, destination, digest, proof_root)
        if role == "targetSymbolInventory":
            tools["symbols"] = destination

    toolchain_source = envelope.require_plain_directory(paths["toolchain"], "toolchain manifest source")
    distribution_specs = {
        "ghidra": ("ghidra-files.tsv", envelope.GHIDRA_DISTRIBUTION),
        "jdk": ("jdk-files.tsv", envelope.JDK_DISTRIBUTION),
        "python": ("python-files.tsv", envelope.PYTHON_DISTRIBUTION),
    }
    distribution_manifests: dict[str, Path] = {}
    for label, (name, spec) in distribution_specs.items():
        source = envelope.require_plain_file(
            toolchain_source / name,
            f"{label} distribution manifest",
            expected_hash=spec[2],
        )
        destination = proof_root / "inputs/toolchain" / name
        envelope.snapshot_file(source, destination, expected_hash=spec[2])
        distribution_manifests[label] = destination

    headless, properties, java, python = envelope.validate_external_toolchain(
        Path(args.analyze_headless or paths["headless"]),
        Path(args.java or paths["java"]),
    )
    toolchain: dict[str, object] = {
        "analyzeHeadless": envelope.external_stamp(headless),
        "applicationProperties": envelope.external_stamp(properties),
        "java": envelope.external_stamp(java),
        "python": envelope.external_stamp(python),
    }
    for label, root, spec in (
        ("ghidra", headless.parent.parent, envelope.GHIDRA_DISTRIBUTION),
        ("jdk", java.parent.parent, envelope.JDK_DISTRIBUTION),
        ("python", python.parent, envelope.PYTHON_DISTRIBUTION),
    ):
        record = envelope.verify_distribution(root, distribution_manifests[label], spec, label)
        record["manifest"] = envelope.stamp(distribution_manifests[label], proof_root)
        toolchain[f"{label}Distribution"] = record

    environment = envelope.sanitized_environment(proof_root, java)
    cwd = proof_root / "work"
    parent_run = run_parent_verifier(
        proof_root=proof_root,
        run_id="parent-pilot-frozen-verify",
        python=python,
        paths=paths,
        cwd=cwd,
        environment=environment,
    )

    before_run, before_functions, before_program = envelope.run_inventory(
        proof_root=proof_root,
        run_id="source-before",
        headless=headless,
        project_root=source_project,
        inventory_tool=tools["inventory"],
        cwd=cwd,
        environment=environment,
    )
    compare_to_base(before_functions, before_program, base_functions, base_program, "source before")
    before_symbol_run, before_symbols, before_symbols_ready = pilot.run_target_symbol_inventory(
        proof_root=proof_root,
        run_id="source-target-symbols-before",
        headless=headless,
        project=source_project,
        tool=tools["symbols"],
        manifest=manifest,
        count=TARGET_COUNT,
        cwd=cwd,
        environment=environment,
    )
    base_symbol_summary = validate_base_target_symbols(
        before_symbols,
        before_symbols_ready,
        tool=tools["symbols"],
        manifest=manifest,
    )

    replicas = [
        run_replica(
            proof_root=proof_root,
            replica="replica-a",
            run_late_control=True,
            headless=headless,
            python=python,
            source_project=source_project,
            tools=tools,
            manifest=manifest,
            poison=poison,
            base_functions=base_functions,
            base_program=base_program,
            base_symbol_summary=base_symbol_summary,
            cwd=cwd,
            environment=environment,
        ),
        run_replica(
            proof_root=proof_root,
            replica="replica-b",
            run_late_control=False,
            headless=headless,
            python=python,
            source_project=source_project,
            tools=tools,
            manifest=manifest,
            poison=poison,
            base_functions=base_functions,
            base_program=base_program,
            base_symbol_summary=base_symbol_summary,
            cwd=cwd,
            environment=environment,
        ),
    ]
    for key in (
        "probeOutput", "applyOutput", "readbackOutput", "afterFunctions",
        "afterProgram", "targetSymbols",
    ):
        first = envelope.validate_frozen_stamp(proof_root, replicas[0][key], f"first {key}")
        second = envelope.validate_frozen_stamp(proof_root, replicas[1][key], f"second {key}")
        require(first.read_bytes() == second.read_bytes(), f"replicas differ at {key}")
    require(replicas[0]["createdRowsSha256"] == replicas[1]["createdRowsSha256"], "replica created rows differ")

    after_run, after_functions, after_program = envelope.run_inventory(
        proof_root=proof_root,
        run_id="source-after",
        headless=headless,
        project_root=source_project,
        inventory_tool=tools["inventory"],
        cwd=cwd,
        environment=environment,
    )
    compare_to_base(after_functions, after_program, base_functions, base_program, "source after")
    after_symbol_run, after_symbols, after_symbols_ready = pilot.run_target_symbol_inventory(
        proof_root=proof_root,
        run_id="source-target-symbols-after",
        headless=headless,
        project=source_project,
        tool=tools["symbols"],
        manifest=manifest,
        count=TARGET_COUNT,
        cwd=cwd,
        environment=environment,
    )
    require(
        validate_base_target_symbols(
            after_symbols, after_symbols_ready,
            tool=tools["symbols"], manifest=manifest,
        ) == base_symbol_summary,
        "source target-symbol summary changed",
    )
    require(before_symbols.read_bytes() == after_symbols.read_bytes(), "source target-symbol rows changed")
    require(envelope.validate_source_project(source_project) == source_rows_before, "source project raw files changed")

    for label, graph in [*input_graph.items(), *tool_graph.items()]:
        source = envelope.resolve_external_stamp(graph["source"], f"post-run {label} source")
        snapshot = envelope.validate_frozen_stamp(proof_root, graph["snapshot"], f"post-run {label} snapshot")
        require(source.read_bytes() == snapshot.read_bytes(), f"post-run {label} source differs from snapshot")
    current_headless, current_properties, current_java, current_python = envelope.validate_external_toolchain(
        headless, java,
    )
    require(
        envelope.external_stamp(current_headless) == toolchain["analyzeHeadless"]
        and envelope.external_stamp(current_properties) == toolchain["applicationProperties"]
        and envelope.external_stamp(current_java) == toolchain["java"]
        and envelope.external_stamp(current_python) == toolchain["python"],
        "external toolchain changed during proof",
    )
    for label, root, spec, key, manifest_name in (
        ("Ghidra", headless.parent.parent, envelope.GHIDRA_DISTRIBUTION, "ghidraDistribution", "ghidra-files.tsv"),
        ("JDK", java.parent.parent, envelope.JDK_DISTRIBUTION, "jdkDistribution", "jdk-files.tsv"),
        ("Python", python.parent, envelope.PYTHON_DISTRIBUTION, "pythonDistribution", "python-files.tsv"),
    ):
        envelope.require_plain_file(
            toolchain_source / manifest_name,
            f"post-run {label} distribution authority",
            expected_hash=spec[2],
        )
        current = envelope.verify_distribution(root, distribution_manifests[label.lower()], spec, label)
        for field in ("root", "fileCount", "totalBytes", "fileSetSha256"):
            require(current[field] == toolchain[key][field], f"{label} distribution changed during proof")

    ready: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "verdict": VERDICT,
        "program": envelope.expected_ready_program(),
        "parentPilot": {
            "readySha256": PILOT_READY_SHA256,
            "frozenOwnerSha256": PILOT_OWNER_SHA256,
            "verifierRun": parent_run["receipt"],
            "verifierResult": expected_parent_verifier_result(paths),
        },
        "sourceAuthority": {
            "projectRoot": str(source_project.resolve()),
            "projectFileCount": envelope.BASE_PROJECT_FILE_COUNT,
            "projectTotalBytes": envelope.BASE_PROJECT_TOTAL_BYTES,
            "projectFileSetSha256": envelope.BASE_PROJECT_FILE_SET_SHA256,
            "sourceBeforeRun": before_run["receipt"],
            "sourceAfterRun": after_run["receipt"],
            "targetSymbolsBeforeRun": before_symbol_run["receipt"],
            "targetSymbolsAfterRun": after_symbol_run["receipt"],
            "targetSymbolsBefore": envelope.stamp(before_symbols, proof_root),
            "targetSymbolsAfter": envelope.stamp(after_symbols, proof_root),
            "targetSymbolSummary": base_symbol_summary,
        },
        "inputs": input_graph,
        "latePoison": envelope.stamp(poison, proof_root),
        "tools": tool_graph,
        "toolchain": toolchain,
        "manifest": expected_manifest_summary(admissible_rows, quarantine_rows),
        "replicas": replicas,
        "checks": expected_checks(),
        "claimBoundary": list(CLAIM_BOUNDARY),
    }
    items = envelope.artifact_items(proof_root)
    ready["artifacts"] = {
        "canonicalization": "sorted relative path with exact bytes and SHA-256; READY excluded",
        "count": len(items),
        "items": items,
    }
    validate_ready_shape(ready)
    candidate_path = proof_root / "proof.candidate.json"
    ready_path = proof_root / "proof.ready.json"
    envelope.write_json_new(candidate_path, ready)
    frozen_runner = proof_root / "tools" / Path(__file__).name
    verification_process = subprocess.run(
        [str(python), "-I", "-B", str(frozen_runner), "--verify-ready", str(candidate_path)],
        cwd=cwd,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="strict",
        check=False,
    )
    require(
        verification_process.returncode == 0,
        f"frozen candidate verifier failed: {verification_process.stderr.strip()}",
    )
    require(verification_process.stderr == "", "frozen candidate verifier emitted stderr")
    verification = json.loads(verification_process.stdout)
    require(verification == {
        "schema": SCHEMA,
        "verdict": VERDICT,
        "ready": str(candidate_path),
        "readySha256": envelope.sha256_file(candidate_path),
        "replicas": 2,
        "retainedProjectsReopenedReadOnly": 5,
        "admissibleTargets": ADMISSIBLE_COUNT,
        "quarantinedListingTargets": 5,
        "publicationStatus": "CANDIDATE",
        "separateLiveBoundaryOwnerEligible": False,
        "semanticPromotionAuthorized": False,
    }, "frozen candidate verifier result differs")
    candidate_sha256 = envelope.sha256_file(candidate_path)
    pilot.verify_artifact_items_for_ready(proof_root, ready, candidate_path.name)
    require(not ready_path.exists(), "proof READY appeared before publication")
    os.rename(candidate_path, ready_path)
    return {
        "ready": str(ready_path),
        "readySha256": candidate_sha256,
        "verdict": VERDICT,
        "admissibleTargets": ADMISSIBLE_COUNT,
        "quarantinedListingTargets": 5,
        "separateLiveBoundaryOwnerEligible": True,
        "semanticPromotionAuthorized": False,
        "frozenVerifierSurvived": True,
        "frozenVerifierStdoutSha256": sha256_bytes(verification_process.stdout.encode("utf-8")),
        "verifiedCandidatePublishedAtomically": True,
    }


def validate_ready_shape(ready: Mapping[str, object]) -> None:
    require(set(ready) == {
        "schema", "status", "verdict", "program", "parentPilot",
        "sourceAuthority", "inputs", "latePoison", "tools", "toolchain",
        "manifest", "replicas", "checks", "claimBoundary", "artifacts",
    }, "READY top-level shape differs")
    require(
        ready.get("schema") == SCHEMA
        and ready.get("status") == STATUS
        and ready.get("verdict") == VERDICT,
        "READY identity differs",
    )
    require(ready.get("program") == envelope.expected_ready_program(), "READY program differs")
    require(ready.get("checks") == expected_checks(), "READY checks differ")
    require(ready.get("claimBoundary") == list(CLAIM_BOUNDARY), "READY claim boundary differs")

    parent = ready.get("parentPilot")
    require(isinstance(parent, dict) and set(parent) == {
        "readySha256", "frozenOwnerSha256", "verifierRun", "verifierResult",
    }, "READY parent-pilot shape differs")
    require(
        parent.get("readySha256") == PILOT_READY_SHA256
        and parent.get("frozenOwnerSha256") == PILOT_OWNER_SHA256
        and isinstance(parent.get("verifierRun"), dict)
        and isinstance(parent.get("verifierResult"), dict),
        "READY parent-pilot values differ",
    )

    source = ready.get("sourceAuthority")
    require(isinstance(source, dict) and set(source) == {
        "projectRoot", "projectFileCount", "projectTotalBytes", "projectFileSetSha256",
        "sourceBeforeRun", "sourceAfterRun", "targetSymbolsBeforeRun",
        "targetSymbolsAfterRun", "targetSymbolsBefore", "targetSymbolsAfter",
        "targetSymbolSummary",
    }, "READY source authority shape differs")
    require(
        source.get("projectFileCount") == envelope.BASE_PROJECT_FILE_COUNT
        and source.get("projectTotalBytes") == envelope.BASE_PROJECT_TOTAL_BYTES
        and source.get("projectFileSetSha256") == envelope.BASE_PROJECT_FILE_SET_SHA256
        and isinstance(source.get("projectRoot"), str),
        "READY source authority values differ",
    )
    require(source.get("targetSymbolSummary") == {
        "outsideTargetSymbols": BASE_OUTSIDE_SYMBOL_COUNT,
        "outsideTargetSymbolsSha256": BASE_OUTSIDE_SYMBOL_SHA256,
    }, "READY source target-symbol summary differs")

    inputs = ready.get("inputs")
    require(isinstance(inputs, dict) and set(inputs) == {
        "pilot98-proof.ready.json", "pilot98-frozen-owner.py",
        "formal-envelope-proof.ready.json", "strata.READY.json", "source-full520.tsv",
        "base-functions.tsv", "base-program.tsv",
    }, "READY input graph differs")
    require(
        all(isinstance(record, dict) and set(record) == {"source", "snapshot"} for record in inputs.values()),
        "READY input record shape differs",
    )
    poison = ready.get("latePoison")
    require(
        isinstance(poison, dict)
        and poison.get("path") == "inputs/admissible515-late-row513-poison.tsv",
        "READY late poison differs",
    )

    tools = ready.get("tools")
    require(isinstance(tools, dict) and set(tools) == {
        *envelope.EXPECTED_TOOL_NAMES,
        "envelopeHelper", "pilotHelper", "strataHelper", "rttiHelper",
        "targetSymbolInventory", "runner",
    }, "READY tool graph differs")
    require(
        all(isinstance(record, dict) and set(record) == {"source", "snapshot"} for record in tools.values()),
        "READY tool record shape differs",
    )
    toolchain = ready.get("toolchain")
    require(isinstance(toolchain, dict) and set(toolchain) == {
        "analyzeHeadless", "applicationProperties", "java", "python",
        "ghidraDistribution", "jdkDistribution", "pythonDistribution",
    }, "READY toolchain shape differs")
    for key in ("analyzeHeadless", "applicationProperties", "java", "python"):
        require(
            isinstance(toolchain[key], dict)
            and set(toolchain[key]) == {"path", "bytes", "sha256"},
            f"READY {key} stamp shape differs",
        )
    for key in ("ghidraDistribution", "jdkDistribution", "pythonDistribution"):
        require(
            isinstance(toolchain[key], dict)
            and set(toolchain[key]) == {
                "root", "fileCount", "totalBytes", "fileSetSha256", "manifest",
            },
            f"READY {key} shape differs",
        )

    manifest = ready.get("manifest")
    require(isinstance(manifest, dict), "READY manifest is absent")
    require(set(manifest) == {
        "count", "sha256", "entries", "bodyBytes", "instructions",
        "terminalKinds", "trueThunks", "forbiddenEntries", "symbolPreimage",
        "sourceBoundarySet", "listingQuarantine",
    }, "READY manifest shape differs")
    require(
        manifest.get("count") == ADMISSIBLE_COUNT
        and manifest.get("sha256") == ADMISSIBLE_MANIFEST_SHA256
        and manifest.get("sourceBoundarySet") == {
            "count": SOURCE_FULL_COUNT,
            "sha256": FULL_MANIFEST_SHA256,
        }
        and manifest.get("listingQuarantine") == {
            "count": 5,
            "sha256": QUARANTINE_MANIFEST_SHA256,
            "entries": sorted(LISTING_QUARANTINE_ENTRIES),
            "bodyBytes": 975,
            "instructions": 180,
            "authorization": "SEPARATE_LISTING_REPAIR_PROOF_REQUIRED",
        },
        "READY admissible manifest identity differs",
    )

    replicas = ready.get("replicas")
    require(
        isinstance(replicas, list)
        and [row.get("id") for row in replicas] == ["replica-a", "replica-b"],
        "READY replicas differ",
    )
    require([row.get("lateControlRun") for row in replicas] == [True, False], "READY control allocation differs")
    require([len(row.get("runs", [])) for row in replicas] == [15, 11], "READY run cardinalities differ")
    replica_keys = {
        "id", "controlProject", "applyProject", "lateControlRun", "runs",
        "probeOutput", "applyOutput", "readbackOutput", "afterFunctions",
        "afterProgram", "targetSymbols", "targetSymbolsReady",
        "outsideTargetSymbolsSha256", "createdRowsSha256", "createdEntries",
        "controlProjectFileSetSha256", "applyProjectFileSetSha256",
    }
    for replica in replicas:
        require(set(replica) == replica_keys, f"READY {replica.get('id')} shape differs")
        require(
            isinstance(replica.get("createdEntries"), list)
            and len(replica["createdEntries"]) == TARGET_COUNT
            and replica["createdEntries"] == sorted(replica["createdEntries"]),
            f"READY {replica.get('id')} created entries differ",
        )
        for key in (
            "createdRowsSha256", "controlProjectFileSetSha256",
            "applyProjectFileSetSha256", "outsideTargetSymbolsSha256",
        ):
            require(
                isinstance(replica.get(key), str)
                and re.fullmatch(r"[0-9a-f]{64}", replica[key]) is not None,
                f"READY {replica.get('id')} {key} differs",
            )
    artifacts = ready.get("artifacts")
    require(
        isinstance(artifacts, dict)
        and set(artifacts) == {"canonicalization", "count", "items"},
        "READY artifact shape differs",
    )


def expected_replica_run_specs(
    *,
    proof_root: Path,
    replica_id: str,
    late_control: bool,
    headless: Path,
    python: Path,
    source_project: Path,
    tools: Mapping[str, Path],
    manifest: Path,
    poison: Path,
    base_functions: Path,
) -> list[dict[str, object]]:
    control_project = proof_root / "projects" / f"{replica_id}-control"
    apply_project = proof_root / "projects" / f"{replica_id}-apply"
    specs: list[dict[str, object]] = []

    def add(run_id: str, argv: list[str], verdict: str, kind: str, **metadata: object) -> None:
        specs.append({"id": run_id, "argv": argv, "verdict": verdict, "kind": kind, **metadata})

    add(
        f"{replica_id}-copy-control",
        envelope.backup_argv(python, tools["backup"], source_project, control_project),
        "SURVIVED", "backup", destination=control_project,
    )
    add(
        f"{replica_id}-copy-apply",
        envelope.backup_argv(python, tools["backup"], source_project, apply_project),
        "SURVIVED", "backup", destination=apply_project,
    )

    def inventory(
        run_id: str,
        project: Path,
        *,
        applied: bool = False,
        final_raw: str | None = None,
    ) -> None:
        root = proof_root / "runs" / run_id
        add(
            run_id,
            envelope.inventory_argv(
                headless, project, tools["inventory"],
                root / "functions.tsv", root / "program.tsv",
            ),
            "SURVIVED", "inventory", applied=applied, finalRaw=final_raw,
        )

    def envelope_run(
        run_id: str,
        project: Path,
        target_manifest: Path,
        mode: str,
        verdict: str,
        *,
        pattern: str | None = None,
        tainted: bool | None = None,
    ) -> None:
        root = proof_root / "runs" / run_id
        add(
            run_id,
            envelope.envelope_argv(
                headless, project, tools["envelope"], target_manifest,
                envelope.sha256_file(target_manifest), TARGET_COUNT,
                root / "envelopes.tsv", root / "envelopes.ready.json", mode,
            ),
            verdict,
            "envelope",
            manifest=target_manifest,
            mode=mode,
            pattern=pattern,
            tainted=tainted,
        )

    inventory(f"{replica_id}-control-baseline", control_project)
    if late_control:
        envelope_run(
            f"{replica_id}-late-poison", control_project, poison, "probe", "REFUTED",
            pattern=LATE_POISON_PATTERN, tainted=True,
        )
        inventory(f"{replica_id}-late-poison-reopened", control_project)
    envelope_run(f"{replica_id}-probe", control_project, manifest, "probe", "SURVIVED")
    inventory(f"{replica_id}-probe-reopened", control_project, final_raw="control")
    inventory(f"{replica_id}-apply-baseline", apply_project)
    envelope_run(f"{replica_id}-apply", apply_project, manifest, "apply", "SURVIVED")
    envelope_run(f"{replica_id}-readback", apply_project, manifest, "readback", "SURVIVED")
    inventory(
        f"{replica_id}-apply-reopened",
        apply_project,
        applied=True,
        final_raw=None if late_control else "apply",
    )
    diff_id = f"{replica_id}-inventory-diff"
    diff_root = proof_root / "runs" / diff_id
    add(
        diff_id,
        envelope.diff_argv(
            python,
            tools["diff"],
            base_functions,
            proof_root / "runs" / f"{replica_id}-apply-reopened" / "functions.tsv",
            diff_root / "inventory-diff.json",
        ),
        "SURVIVED", "diff",
    )
    if late_control:
        envelope_run(
            f"{replica_id}-reprobe-applied", apply_project, manifest, "probe", "REFUTED",
            pattern=REPROBE_PATTERN, tainted=False,
        )
        inventory(
            f"{replica_id}-reprobe-applied-reopened",
            apply_project,
            applied=True,
            final_raw="apply",
        )
    symbol_id = f"{replica_id}-target-symbols"
    symbol_root = proof_root / "runs" / symbol_id
    add(
        symbol_id,
        pilot.target_symbol_argv(
            headless, apply_project, tools["symbols"], manifest, TARGET_COUNT,
            symbol_root / "target-symbols.tsv",
            symbol_root / "target-symbols.ready.json",
        ),
        "SURVIVED", "symbols",
    )
    require(len(specs) == (15 if late_control else 11), f"internal {replica_id} run-spec count differs")
    return specs


def verify_parent_receipt(
    *,
    proof_root: Path,
    ready: Mapping[str, object],
    python: Path,
    java: Path,
    paths: Mapping[str, Path],
) -> None:
    stamp = ready["parentPilot"]["verifierRun"]
    run_id = "parent-pilot-frozen-verify"
    receipt = envelope.verify_run_receipt(
        proof_root,
        stamp,
        "parent pilot verifier",
        expected_id=run_id,
        expected_argv=parent_verifier_argv(python, paths),
        expected_cwd=proof_root / "work",
        expected_environment=envelope.expected_sanitized_environment(proof_root, java),
        expected_verdict="SURVIVED",
    )
    require(receipt["log"]["path"] == f"runs/{run_id}/headless.log", "parent verifier log path differs")
    log = envelope.validate_frozen_stamp(proof_root, receipt["log"], "parent verifier log")
    expected = expected_parent_verifier_result(paths)
    require(receipt["observations"] == {
        "verifierResult": expected,
        "stdoutSha256": sha256_bytes(log.read_bytes()),
    }, "parent verifier observations differ")
    require(ready["parentPilot"]["verifierResult"] == expected, "READY parent verifier result differs")


def verify_source_inventory_receipt(
    *,
    proof_root: Path,
    ready: Mapping[str, object],
    receipt_name: str,
    run_id: str,
    headless: Path,
    java: Path,
    source_project: Path,
    inventory_tool: Path,
    base_functions: Path,
    base_program: Path,
) -> None:
    run_root = proof_root / "runs" / run_id
    stamp = ready["sourceAuthority"][receipt_name]
    receipt = envelope.verify_run_receipt(
        proof_root,
        stamp,
        receipt_name,
        expected_id=run_id,
        expected_argv=envelope.inventory_argv(
            headless, source_project, inventory_tool,
            run_root / "functions.tsv", run_root / "program.tsv",
        ),
        expected_cwd=proof_root / "work",
        expected_environment=envelope.expected_sanitized_environment(proof_root, java),
        expected_verdict="SURVIVED",
    )
    functions = run_root / "functions.tsv"
    program = run_root / "program.tsv"
    require(receipt["observations"] == {
        "functionCount": envelope.BASE_FUNCTION_COUNT,
        "instructionCount": envelope.BASE_INSTRUCTION_COUNT,
        "functions": envelope.stamp(functions, proof_root),
        "program": envelope.stamp(program, proof_root),
        "projectFileSetSha256": envelope.BASE_PROJECT_FILE_SET_SHA256,
    }, f"{run_id} observations differ")
    compare_to_base(functions, program, base_functions, base_program, run_id)


def verify_source_symbol_receipt(
    *,
    proof_root: Path,
    ready: Mapping[str, object],
    receipt_name: str,
    output_name: str,
    run_id: str,
    headless: Path,
    java: Path,
    source_project: Path,
    symbol_tool: Path,
    manifest: Path,
) -> dict[str, object]:
    run_root = proof_root / "runs" / run_id
    output = run_root / "target-symbols.tsv"
    java_ready_path = run_root / "target-symbols.ready.json"
    receipt = envelope.verify_run_receipt(
        proof_root,
        ready["sourceAuthority"][receipt_name],
        receipt_name,
        expected_id=run_id,
        expected_argv=pilot.target_symbol_argv(
            headless, source_project, symbol_tool, manifest, TARGET_COUNT,
            output, java_ready_path,
        ),
        expected_cwd=proof_root / "work",
        expected_environment=envelope.expected_sanitized_environment(proof_root, java),
        expected_verdict="SURVIVED",
    )
    java_ready = pilot.validate_target_symbol_ready(
        java_ready_path, output, tool=symbol_tool, manifest=manifest, count=TARGET_COUNT,
    )
    require(receipt["observations"] == {
        "output": envelope.stamp(output, proof_root),
        "ready": envelope.stamp(java_ready_path, proof_root),
        "javaReady": java_ready,
        "projectFileSetSha256": envelope.BASE_PROJECT_FILE_SET_SHA256,
    }, f"{run_id} observations differ")
    require(
        ready["sourceAuthority"][output_name] == envelope.stamp(output, proof_root),
        f"{output_name} stamp differs",
    )
    return validate_base_target_symbols(
        output, java_ready_path, tool=symbol_tool, manifest=manifest,
    )


def verify_recorded_replica(
    *,
    proof_root: Path,
    replica: Mapping[str, object],
    headless: Path,
    java: Path,
    python: Path,
    source_project: Path,
    tools: Mapping[str, Path],
    manifest: Path,
    poison: Path,
    base_functions: Path,
    base_program: Path,
    base_rows: Mapping[str, Mapping[str, str]],
    base_symbol_summary: Mapping[str, object],
    full_rows: Sequence[Mapping[str, str]],
) -> None:
    replica_id = str(replica["id"])
    late_control = bool(replica["lateControlRun"])
    control_project = proof_root / "projects" / f"{replica_id}-control"
    apply_project = proof_root / "projects" / f"{replica_id}-apply"
    require(replica["controlProject"] == str(control_project.resolve()), f"{replica_id} control path differs")
    require(replica["applyProject"] == str(apply_project.resolve()), f"{replica_id} apply path differs")
    require(replica["createdEntries"] == [row["entry"] for row in full_rows], f"{replica_id} created entries differ")

    evidence_paths = {
        "probeOutput": f"runs/{replica_id}-probe/envelopes.tsv",
        "applyOutput": f"runs/{replica_id}-apply/envelopes.tsv",
        "readbackOutput": f"runs/{replica_id}-readback/envelopes.tsv",
        "afterFunctions": f"runs/{replica_id}-apply-reopened/functions.tsv",
        "afterProgram": f"runs/{replica_id}-apply-reopened/program.tsv",
        "targetSymbols": f"runs/{replica_id}-target-symbols/target-symbols.tsv",
        "targetSymbolsReady": f"runs/{replica_id}-target-symbols/target-symbols.ready.json",
    }
    for key, expected_path in evidence_paths.items():
        value = replica[key]
        require(isinstance(value, dict) and value.get("path") == expected_path, f"{replica_id} {key} path differs")
        envelope.validate_frozen_stamp(proof_root, value, f"{replica_id} {key}")

    specs = expected_replica_run_specs(
        proof_root=proof_root,
        replica_id=replica_id,
        late_control=late_control,
        headless=headless,
        python=python,
        source_project=source_project,
        tools=tools,
        manifest=manifest,
        poison=poison,
        base_functions=base_functions,
    )
    receipts = envelope.require_receipt_stamp_order(
        replica["runs"], [str(spec["id"]) for spec in specs], replica_id,
    )
    expected_environment = envelope.expected_sanitized_environment(proof_root, java)
    for index, (receipt_stamp, spec) in enumerate(zip(receipts, specs, strict=True)):
        run_id = str(spec["id"])
        receipt = envelope.verify_run_receipt(
            proof_root,
            receipt_stamp,
            f"{replica_id} run {index}",
            expected_id=run_id,
            expected_argv=spec["argv"],
            expected_cwd=proof_root / "work",
            expected_environment=expected_environment,
            expected_verdict=str(spec["verdict"]),
        )
        require(receipt["log"]["path"] == f"runs/{run_id}/headless.log", f"{run_id} log path differs")
        observations = receipt["observations"]
        kind = spec["kind"]
        run_root = proof_root / "runs" / run_id
        if kind == "backup":
            require(set(observations) == {
                "sourceProjectFileSetSha256", "destinationProjectFileSetSha256", "backupManifest",
            }, f"{run_id} backup observations differ")
            require(
                observations["sourceProjectFileSetSha256"] == envelope.BASE_PROJECT_FILE_SET_SHA256
                and observations["destinationProjectFileSetSha256"] == envelope.BASE_PROJECT_FILE_SET_SHA256,
                f"{run_id} backup project digest differs",
            )
            destination = Path(spec["destination"])
            require(
                observations["backupManifest"].get("path")
                == envelope.stamp(destination / "backup_manifest.json", proof_root)["path"],
                f"{run_id} backup manifest path differs",
            )
            envelope.validate_frozen_stamp(
                proof_root, observations["backupManifest"], f"{run_id} backup manifest",
            )
        elif kind == "inventory":
            functions = run_root / "functions.tsv"
            program = run_root / "program.tsv"
            require(set(observations) == {
                "functionCount", "instructionCount", "functions", "program", "projectFileSetSha256",
            }, f"{run_id} inventory observations differ")
            require(observations["functions"] == envelope.stamp(functions, proof_root), f"{run_id} functions stamp differs")
            require(observations["program"] == envelope.stamp(program, proof_root), f"{run_id} program stamp differs")
            applied = bool(spec["applied"])
            require(observations["instructionCount"] == envelope.BASE_INSTRUCTION_COUNT, f"{run_id} instruction count differs")
            require(
                observations["functionCount"] == (EXPECTED_AFTER_COUNT if applied else envelope.BASE_FUNCTION_COUNT),
                f"{run_id} function count differs",
            )
            raw_digest = observations["projectFileSetSha256"]
            require(isinstance(raw_digest, str) and re.fullmatch(r"[0-9a-f]{64}", raw_digest) is not None, f"{run_id} raw digest differs")
            if spec["finalRaw"] == "control":
                require(raw_digest == replica["controlProjectFileSetSha256"], f"{run_id} final control digest differs")
            elif spec["finalRaw"] == "apply":
                require(raw_digest == replica["applyProjectFileSetSha256"], f"{run_id} final apply digest differs")
            if applied:
                validate_applied_inventory(base_functions, base_program, functions, program, manifest)
            else:
                compare_to_base(functions, program, base_functions, base_program, run_id)
        elif kind == "envelope" and spec["verdict"] == "SURVIVED":
            require(set(observations) == {"output", "ready", "rowsSha256", "javaReady"}, f"{run_id} envelope observations differ")
            output = run_root / "envelopes.tsv"
            java_ready_path = run_root / "envelopes.ready.json"
            rows = validate_output(output, Path(spec["manifest"]), mode=str(spec["mode"]), base_rows=base_rows)
            java_ready = validate_java_ready(
                java_ready_path, output, mode=str(spec["mode"]),
                tool=tools["envelope"], manifest=Path(spec["manifest"]), count=TARGET_COUNT,
            )
            require(observations == {
                "output": envelope.stamp(output, proof_root),
                "ready": envelope.stamp(java_ready_path, proof_root),
                "rowsSha256": sha256_bytes(canonical_json(rows)),
                "javaReady": java_ready,
            }, f"{run_id} envelope observation values differ")
        elif kind == "envelope":
            require(observations == {
                "expectedPattern": spec["pattern"],
                "scriptErrorCount": 1,
                "mutationTainted": spec["tainted"],
                "outputPublished": False,
                "readyPublished": False,
            }, f"{run_id} rejection observations differ")
            require(not (run_root / "envelopes.tsv").exists(), f"{run_id} rejection published output")
            require(not (run_root / "envelopes.ready.json").exists(), f"{run_id} rejection published READY")
        elif kind == "diff":
            require(set(observations) == {"diff", "stdoutSha256", "payloadSha256"}, f"{run_id} diff observations differ")
            diff = run_root / "inventory-diff.json"
            log = envelope.validate_frozen_stamp(proof_root, receipt["log"], f"{run_id} log")
            payload = validate_inventory_diff_payload(diff, [row["entry"] for row in full_rows])
            require(observations == {
                "diff": envelope.stamp(diff, proof_root),
                "stdoutSha256": sha256_bytes(log.read_bytes()),
                "payloadSha256": sha256_bytes(canonical_json(payload)),
            }, f"{run_id} diff observation values differ")
            require(payload["beforeFile"] == str(base_functions.resolve()), f"{run_id} diff before path differs")
            require(
                payload["afterFile"]
                == str((proof_root / "runs" / f"{replica_id}-apply-reopened" / "functions.tsv").resolve()),
                f"{run_id} diff after path differs",
            )
        elif kind == "symbols":
            output = run_root / "target-symbols.tsv"
            java_ready_path = run_root / "target-symbols.ready.json"
            java_ready = pilot.validate_target_symbol_ready(
                java_ready_path, output,
                tool=tools["symbols"], manifest=manifest, count=TARGET_COUNT,
            )
            validate_applied_target_symbols(
                output, java_ready_path,
                tool=tools["symbols"], manifest=manifest,
                base_rows=base_rows, base_summary=base_symbol_summary,
            )
            require(observations == {
                "output": envelope.stamp(output, proof_root),
                "ready": envelope.stamp(java_ready_path, proof_root),
                "javaReady": java_ready,
                "projectFileSetSha256": replica["applyProjectFileSetSha256"],
            }, f"{run_id} target-symbol observations differ")
        else:
            raise ProofError(f"unsupported run kind: {run_id} {kind}")

    after_functions = envelope.validate_frozen_stamp(proof_root, replica["afterFunctions"], f"{replica_id} after functions")
    after_program = envelope.validate_frozen_stamp(proof_root, replica["afterProgram"], f"{replica_id} after program")
    created = validate_applied_inventory(base_functions, base_program, after_functions, after_program, manifest)
    require(replica["createdEntries"] == sorted(created), f"{replica_id} created set differs")
    require(replica["createdRowsSha256"] == sha256_bytes(canonical_json(created)), f"{replica_id} created rows differ")
    validate_applied_target_symbols(
        envelope.validate_frozen_stamp(proof_root, replica["targetSymbols"], f"{replica_id} target symbols"),
        envelope.validate_frozen_stamp(proof_root, replica["targetSymbolsReady"], f"{replica_id} target-symbol READY"),
        tool=tools["symbols"], manifest=manifest,
        base_rows=base_rows, base_summary=base_symbol_summary,
    )
    require(
        replica["outsideTargetSymbolsSha256"] == BASE_OUTSIDE_SYMBOL_SHA256,
        f"{replica_id} outside-target symbol digest differs",
    )


def verify_control_logs(proof_root: Path) -> None:
    root = proof_root / "runs/replica-a-late-poison"
    require(not (root / "envelopes.tsv").exists(), "late poison published output")
    require(not (root / "envelopes.ready.json").exists(), "late poison published READY")
    text = (root / "headless.log").read_text(encoding="utf-8")
    require(text.count("REPORT SCRIPT ERROR") == 1, "late poison script-error count differs")
    require(re.search(LATE_POISON_PATTERN, text) is not None, "late poison rejection differs")
    require("FUNCTION_ENVELOPE_MUTATION_TAINTED" in text, "late poison lacks transaction taint")
    require("FUNCTION_ENVELOPE_OK" not in text, "late poison emitted success")

    root = proof_root / "runs/replica-a-reprobe-applied"
    require(not (root / "envelopes.tsv").exists(), "reprobe published output")
    require(not (root / "envelopes.ready.json").exists(), "reprobe published READY")
    text = (root / "headless.log").read_text(encoding="utf-8")
    require(text.count("REPORT SCRIPT ERROR") == 1, "reprobe script-error count differs")
    require(REPROBE_PATTERN in text, "reprobe rejection differs")
    require("FUNCTION_ENVELOPE_MUTATION_TAINTED" not in text, "reprobe was transaction-tainted")
    require("FUNCTION_ENVELOPE_OK" not in text, "reprobe emitted success")


def live_reverify(
    *,
    proof_root: Path,
    ready: Mapping[str, object],
    paths: Mapping[str, Path],
    headless: Path,
    java: Path,
    python: Path,
    inventory_tool: Path,
    symbol_tool: Path,
    manifest: Path,
    base_functions: Path,
    base_program: Path,
    base_rows: Mapping[str, Mapping[str, str]],
    base_symbol_summary: Mapping[str, object],
) -> None:
    source = envelope.require_plain_directory(Path(ready["sourceAuthority"]["projectRoot"]), "source project")
    projects: list[tuple[str, Path, Path, Path, str, bool]] = [(
        "source-current",
        source,
        base_functions,
        base_program,
        envelope.BASE_PROJECT_FILE_SET_SHA256,
        False,
    )]
    for replica in ready["replicas"]:
        replica_id = replica["id"]
        projects.append((
            f"{replica_id}-control-current",
            envelope.require_plain_directory(proof_root / "projects" / f"{replica_id}-control", "retained control"),
            base_functions,
            base_program,
            replica["controlProjectFileSetSha256"],
            False,
        ))
        projects.append((
            f"{replica_id}-apply-current",
            envelope.require_plain_directory(proof_root / "projects" / f"{replica_id}-apply", "retained apply"),
            envelope.validate_frozen_stamp(proof_root, replica["afterFunctions"], "recorded functions"),
            envelope.validate_frozen_stamp(proof_root, replica["afterProgram"], "recorded program"),
            replica["applyProjectFileSetSha256"],
            True,
        ))
    with tempfile.TemporaryDirectory(prefix="bea-global-init515-ready-verify-") as temporary:
        verification = Path(temporary)
        envelope.ensure_plain_directory(verification / "runs", "verification runs")
        envelope.ensure_plain_directory(verification / "work", "verification work")
        environment = envelope.sanitized_environment(verification, java)
        run_parent_verifier(
            proof_root=verification,
            run_id="fresh-parent-pilot-verify",
            python=python,
            paths=paths,
            cwd=verification / "work",
            environment=environment,
        )
        for run_id, project, expected_functions, expected_program, raw_digest, applied in projects:
            before = envelope.project_rows(project)
            require(envelope.rows_digest(before) == raw_digest, f"retained {run_id} raw project differs")
            _, functions, program = envelope.run_inventory(
                proof_root=verification,
                run_id=run_id,
                headless=headless,
                project_root=project,
                inventory_tool=inventory_tool,
                cwd=verification / "work",
                environment=environment,
            )
            require(functions.read_bytes() == expected_functions.read_bytes(), f"retained {run_id} functions differ")
            require(program.read_bytes() == expected_program.read_bytes(), f"retained {run_id} program differs")
            require(envelope.project_rows(project) == before, f"retained {run_id} changed during readback")
            if run_id == "source-current" or applied:
                _, symbols, symbols_ready = pilot.run_target_symbol_inventory(
                    proof_root=verification,
                    run_id=f"{run_id}-target-symbols",
                    headless=headless,
                    project=project,
                    tool=symbol_tool,
                    manifest=manifest,
                    count=TARGET_COUNT,
                    cwd=verification / "work",
                    environment=environment,
                )
                if run_id == "source-current":
                    require(
                        validate_base_target_symbols(
                            symbols, symbols_ready, tool=symbol_tool, manifest=manifest,
                        ) == base_symbol_summary,
                        "retained source target-symbol summary differs",
                    )
                else:
                    validate_applied_target_symbols(
                        symbols, symbols_ready,
                        tool=symbol_tool, manifest=manifest,
                        base_rows=base_rows, base_summary=base_symbol_summary,
                    )


def verify_ready(ready_path: Path) -> dict[str, object]:
    ready_path = envelope.require_plain_file(ready_path, "proof READY")
    require(
        ready_path.name in {"proof.candidate.json", "proof.ready.json"},
        "proof READY filename differs",
    )
    proof_root = ready_path.parent.resolve()
    ready = envelope.read_json(ready_path, "proof READY")
    validate_ready_shape(ready)
    pilot.verify_artifact_items_for_ready(proof_root, ready, ready_path.name)
    require(proof_root.parent.name == "local-lab", "proof READY must remain one direct local-lab child")
    repo = envelope.require_plain_directory(proof_root.parent.parent, "proof repository")
    require((repo / "README.MD").is_file() and (repo / "tools").is_dir(), "proof parent is not Onslaught Toolkit")
    paths = default_paths(repo)

    input_sources = {
        "pilot98-proof.ready.json": (paths["pilotReady"], PILOT_READY_SHA256),
        "pilot98-frozen-owner.py": (paths["pilotOwner"], PILOT_OWNER_SHA256),
        "formal-envelope-proof.ready.json": (paths["formalReady"], FORMAL_READY_SHA256),
        "strata.READY.json": (paths["strataBundle"] / "READY.json", STRATA_READY_SHA256),
        "source-full520.tsv": (paths["fullManifest"], FULL_MANIFEST_SHA256),
        "base-functions.tsv": (paths["baseFunctions"], envelope.BASE_FUNCTIONS_SHA256),
        "base-program.tsv": (paths["baseProgram"], envelope.BASE_PROGRAM_SHA256),
    }
    for name, (source, expected_hash) in input_sources.items():
        record = ready["inputs"][name]
        require(record["source"] == envelope.external_stamp(source), f"{name} provenance source differs")
        require(record["snapshot"].get("path") == f"inputs/{name}", f"{name} snapshot path differs")
        snapshot = envelope.validate_frozen_stamp(proof_root, record["snapshot"], f"frozen {name}")
        require(envelope.sha256_file(snapshot) == expected_hash, f"{name} snapshot hash differs")

    strata.verify_bundle(repo, paths["formalReady"], paths["strataBundle"])
    source_manifest = proof_root / "inputs/source-full520.tsv"
    full_rows = validate_full_manifest(source_manifest)
    admissible_rows, quarantine_rows = partition_full_manifest(full_rows)
    manifest = envelope.require_plain_file(proof_root / "inputs/admissible515.tsv", "admissible manifest")
    quarantine = envelope.require_plain_file(proof_root / "inputs/listing-quarantine5.tsv", "listing quarantine")
    require(manifest.read_bytes() == render_manifest(admissible_rows), "admissible manifest bytes differ")
    require(quarantine.read_bytes() == render_manifest(quarantine_rows), "listing quarantine bytes differ")
    validate_admissible_manifest(manifest)
    require(
        ready["manifest"] == expected_manifest_summary(admissible_rows, quarantine_rows),
        "READY manifest values differ",
    )
    poison = envelope.validate_frozen_stamp(proof_root, ready["latePoison"], "late poison")
    require(poison.read_bytes() == late_poison_manifest(admissible_rows), "late poison bytes differ")
    base_functions = proof_root / "inputs/base-functions.tsv"
    base_program = proof_root / "inputs/base-program.tsv"
    envelope.validate_base_inventory(base_functions, base_program)
    _, base_rows = envelope.function_rows(base_functions)

    tools: dict[str, Path] = {}
    for role, digest in envelope.EXPECTED_TOOL_SHA256.items():
        record = ready["tools"][role]
        source = repo / "tools" / envelope.EXPECTED_TOOL_NAMES[role]
        require(record["source"] == envelope.external_stamp(source), f"{role} tool source differs")
        snapshot = envelope.validate_frozen_stamp(proof_root, record["snapshot"], f"frozen {role}")
        require(envelope.sha256_file(snapshot) == digest, f"frozen {role} hash differs")
        tools[role] = snapshot
    extra_tools = {
        "envelopeHelper": (repo / "tools/ghidra_function_envelope_proof.py", ENVELOPE_HELPER_SHA256),
        "pilotHelper": (repo / "tools/ghidra_function_batch_proof.py", PILOT_OWNER_SHA256),
        "strataHelper": (repo / "tools/re_crt_function_strata.py", STRATA_HELPER_SHA256),
        "rttiHelper": (repo / "tools/re_rtti_vtables.py", RTTI_HELPER_SHA256),
        "targetSymbolInventory": (paths["targetSymbolTool"], TARGET_SYMBOL_TOOL_SHA256),
        "runner": (repo / "tools" / Path(__file__).name, envelope.sha256_file(Path(__file__))),
    }
    for role, (source, expected_hash) in extra_tools.items():
        record = ready["tools"][role]
        require(record["source"] == envelope.external_stamp(source), f"{role} source differs")
        snapshot = envelope.validate_frozen_stamp(proof_root, record["snapshot"], f"frozen {role}")
        require(envelope.sha256_file(snapshot) == expected_hash, f"frozen {role} hash differs")
        if role == "targetSymbolInventory":
            tools["symbols"] = snapshot
    runner = envelope.validate_frozen_stamp(proof_root, ready["tools"]["runner"]["snapshot"], "frozen runner")
    require(runner.read_bytes() == Path(__file__).read_bytes(), "invoke verifier with the exact frozen owner")

    toolchain = ready["toolchain"]
    headless = envelope.resolve_external_stamp(
        toolchain["analyzeHeadless"], "analyzeHeadless", expected_hash=envelope.ANALYZE_HEADLESS_SHA256,
    )
    properties = envelope.resolve_external_stamp(
        toolchain["applicationProperties"], "Ghidra properties", expected_hash=envelope.GHIDRA_APPLICATION_PROPERTIES_SHA256,
    )
    java = envelope.resolve_external_stamp(
        toolchain["java"], "Java", expected_hash=envelope.HOST_JAVA_SHA256,
    )
    python = envelope.resolve_external_stamp(
        toolchain["python"], "Python", expected_hash=envelope.PYTHON_SHA256,
    )
    require(properties == headless.parent.parent / "Ghidra/application.properties", "Ghidra roots differ")
    for label, root, spec, key, manifest_name in (
        ("Ghidra", headless.parent.parent, envelope.GHIDRA_DISTRIBUTION, "ghidraDistribution", "ghidra-files.tsv"),
        ("JDK", java.parent.parent, envelope.JDK_DISTRIBUTION, "jdkDistribution", "jdk-files.tsv"),
        ("Python", python.parent, envelope.PYTHON_DISTRIBUTION, "pythonDistribution", "python-files.tsv"),
    ):
        record = toolchain[key]
        distribution_manifest = envelope.validate_frozen_stamp(
            proof_root, record["manifest"], f"{label} distribution manifest",
        )
        require(distribution_manifest.name == manifest_name, f"{label} distribution manifest name differs")
        current = envelope.verify_distribution(root, distribution_manifest, spec, label)
        for field in ("root", "fileCount", "totalBytes", "fileSetSha256"):
            require(record[field] == current[field], f"{label} distribution differs")

    verify_parent_receipt(
        proof_root=proof_root, ready=ready, python=python, java=java, paths=paths,
    )
    source_project = envelope.require_plain_directory(paths["sourceProject"], "derived source project")
    require(ready["sourceAuthority"]["projectRoot"] == str(source_project.resolve()), "source project path differs")
    require(
        envelope.rows_digest(envelope.validate_source_project(source_project))
        == ready["sourceAuthority"]["projectFileSetSha256"],
        "source project identity differs",
    )
    for receipt_name, run_id in (("sourceBeforeRun", "source-before"), ("sourceAfterRun", "source-after")):
        verify_source_inventory_receipt(
            proof_root=proof_root,
            ready=ready,
            receipt_name=receipt_name,
            run_id=run_id,
            headless=headless,
            java=java,
            source_project=source_project,
            inventory_tool=tools["inventory"],
            base_functions=base_functions,
            base_program=base_program,
        )
    before_symbol_summary = verify_source_symbol_receipt(
        proof_root=proof_root,
        ready=ready,
        receipt_name="targetSymbolsBeforeRun",
        output_name="targetSymbolsBefore",
        run_id="source-target-symbols-before",
        headless=headless,
        java=java,
        source_project=source_project,
        symbol_tool=tools["symbols"],
        manifest=manifest,
    )
    after_symbol_summary = verify_source_symbol_receipt(
        proof_root=proof_root,
        ready=ready,
        receipt_name="targetSymbolsAfterRun",
        output_name="targetSymbolsAfter",
        run_id="source-target-symbols-after",
        headless=headless,
        java=java,
        source_project=source_project,
        symbol_tool=tools["symbols"],
        manifest=manifest,
    )
    require(
        before_symbol_summary == after_symbol_summary == ready["sourceAuthority"]["targetSymbolSummary"],
        "source target-symbol summaries differ",
    )
    require(
        envelope.validate_frozen_stamp(
            proof_root, ready["sourceAuthority"]["targetSymbolsBefore"], "source symbols before",
        ).read_bytes()
        == envelope.validate_frozen_stamp(
            proof_root, ready["sourceAuthority"]["targetSymbolsAfter"], "source symbols after",
        ).read_bytes(),
        "source target-symbol rows differ",
    )

    for replica in ready["replicas"]:
        verify_recorded_replica(
            proof_root=proof_root,
            replica=replica,
            headless=headless,
            java=java,
            python=python,
            source_project=source_project,
            tools=tools,
            manifest=manifest,
            poison=poison,
            base_functions=base_functions,
            base_program=base_program,
            base_rows=base_rows,
            base_symbol_summary=before_symbol_summary,
            full_rows=admissible_rows,
        )
    verify_control_logs(proof_root)
    first, second = ready["replicas"]
    for key in (
        "probeOutput", "applyOutput", "readbackOutput", "afterFunctions",
        "afterProgram", "targetSymbols",
    ):
        left = envelope.validate_frozen_stamp(proof_root, first[key], f"first {key}")
        right = envelope.validate_frozen_stamp(proof_root, second[key], f"second {key}")
        require(left.read_bytes() == right.read_bytes(), f"replicas differ at {key}")

    live_reverify(
        proof_root=proof_root,
        ready=ready,
        paths=paths,
        headless=headless,
        java=java,
        python=python,
        inventory_tool=tools["inventory"],
        symbol_tool=tools["symbols"],
        manifest=manifest,
        base_functions=base_functions,
        base_program=base_program,
        base_rows=base_rows,
        base_symbol_summary=before_symbol_summary,
    )
    pilot.verify_artifact_items_for_ready(proof_root, ready, ready_path.name)
    published = ready_path.name == "proof.ready.json"
    return {
        "schema": SCHEMA,
        "verdict": VERDICT,
        "ready": str(ready_path),
        "readySha256": envelope.sha256_file(ready_path),
        "replicas": 2,
        "retainedProjectsReopenedReadOnly": 5,
        "admissibleTargets": ADMISSIBLE_COUNT,
        "quarantinedListingTargets": 5,
        "publicationStatus": "READY" if published else "CANDIDATE",
        "separateLiveBoundaryOwnerEligible": published,
        "semanticPromotionAuthorized": False,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-ready", type=Path)
    parser.add_argument("--proof-root", type=Path)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--analyze-headless", type=Path)
    parser.add_argument("--java", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.verify_ready is not None:
            require(args.proof_root is None, "--verify-ready and --proof-root are mutually exclusive")
            result = verify_ready(args.verify_ready)
        else:
            require(args.proof_root is not None, "--proof-root is required")
            result = run_proof(args)
    except (ProofError, strata.StrataError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"UNSCORED: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
