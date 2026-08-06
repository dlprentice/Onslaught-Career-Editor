#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Prospectively prove a manifest of Ghidra function envelopes on scratch clones.

This owner consumes the independently verified ordinary two-range canary and
the frozen CRT strata bundle.  It never opens the maintainer project.  Pilot
survival may authorize only a subsequent full-520 scratch proof.
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
from typing import Iterable, Mapping, Sequence


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import ghidra_function_envelope_proof as envelope  # noqa: E402
import re_crt_function_strata as strata  # noqa: E402


SCHEMA = "bea.re.ghidra-function-batch-proof.v1"
STATUS = "READY"
VERDICT = "SURVIVED"
PILOT_COUNT = 98
PILOT_READY_SHA256 = "b69a04144a4c5af8e18d275742c47bdf733104bd3a652911f46199bff4372d04"
PILOT_MANIFEST_SHA256 = "edb85843ea8d95be94963495eede7246184b399b2eb6a5ba438a22e7ddb7f091"
FULL_MANIFEST_SHA256 = "d22c9600f93e84dd203f73ced840d57892cf1d63d5d8209e161ea2ac85c20463"
FORMAL_READY_SHA256 = "35f8f0a2777c6676e5d8f3313b19ebfe1cdc5c76fd3fff6698619b343e543efd"
ENVELOPE_HELPER_SHA256 = "e20d619c39dd0f2037523b4577860b6640ed76b0be058472834a587192b305e8"
RTTI_HELPER_SHA256 = "90071f2536e6f511d647b47fda7d323110374fd6c57b15e5360adaa0fd717d1d"
TARGET_SYMBOL_TOOL_SHA256 = "6ea0e6ce2669dd9cb325a052df70cd2f84cd5ebc1319cf5ba8c089691d660327"
TARGET_SYMBOL_SCHEMA = "bea.re.ghidra-target-symbol-inventory.v1"
SYMBOLLESS_PILOT_ENTRY = "0x00564fd6"
EXPECTED_DEFAULT_SYMBOL_DELTA = 1
EXPECTED_AFTER_COUNT = envelope.BASE_FUNCTION_COUNT + PILOT_COUNT

OUTPUT_HEADER = (
    "entry", "status", "name", "nameSource", "expectedRanges", "actualRanges",
    "expectedBodyBytes", "actualBodyBytes", "expectedRangeDigest", "actualRangeDigest",
    "expectedBodyBytesSha256", "actualBodyBytesSha256", "expectedInstructionCount",
    "actualInstructionCount", "expectedIsThunk", "actualIsThunk", "expectedThunkTarget",
    "actualThunkTarget", "forbiddenEntries", "residualEntityKeys", "questionIds",
    "contractIds", "promotionLane", "note",
)

TARGET_SYMBOL_HEADER = (
    "entry", "symbolCount", "name", "fqname", "namespace", "type", "source",
    "primary", "dynamic", "external", "pinned",
)

CLAIM_BOUNDARY = (
    "This proves only the exact natural Ghidra envelopes and manifest-bound function kinds for the frozen 98-entry CRT pilot on two disposable clone pairs.",
    "Pilot survival authorizes freezing and running the full-520 manifest on fresh scratch clones; it does not authorize the full manifest by inference.",
    "No live maintainer-project mutation, semantic names, signatures, behavior contracts, or rebuild parity claim follows from this pilot.",
    "The 520 boundary and the v2 strata bundle remain batch/live blocked until a separate full-520 proof survives.",
    "The exported full-function inventory, exact target-symbol rows, and all-symbol digest outside the target set are the checked semantic boundary; this is not a claim that every possible internal Ghidra database record is unchanged.",
    "This READY is unsigned machine-local evidence for a trusted quiescent host, not hostile-actor-resistant proof or proof of historical wall-clock ordering.",
)

CONTROL_SPECIFICATIONS = (
    ("wrong-thunk-kind", r"THUNK_KIND_MISMATCH entry=0x00518be0 expected=false actual=true"),
    ("wrong-thunk-target", r"THUNK_TARGET_MISMATCH entry=0x00518be0 expected=0x0052ff30 actual=0x00518bf0"),
    ("side-tail-as-thunk", r"THUNK_KIND_MISMATCH entry=0x00453090 expected=true actual=false"),
    ("truncated-internal-loop", r"BODY_ENVELOPE_MISMATCH entry=0x004f5f30"),
)
REPROBE_PATTERN = r"probe/apply requires a missing target: 0x00402080"


ProofError = envelope.ProofError


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProofError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def manifest_rows(path: Path, *, expected_hash: str | None = None) -> list[dict[str, str]]:
    header, rows = envelope.parse_manifest(path, expected_hash=expected_hash)
    return [dict(zip(header, row, strict=True)) for row in rows]


def render_manifest(rows: Iterable[Mapping[str, str]]) -> bytes:
    columns = envelope.MANIFEST_HEADER.split("\t")
    output = io.StringIO(newline="")
    writer = csv.DictWriter(
        output, fieldnames=columns, delimiter="\t", lineterminator="\n",
        extrasaction="raise",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow({column: row[column] for column in columns})
    return output.getvalue().encode("utf-8")


def default_paths(repo: Path) -> dict[str, Path]:
    formal = repo / "local-lab/formal-function-envelope-canary-20260803-v3"
    bundle = repo / "local-lab/crt520-function-strata-20260803-v2-ready"
    base = envelope.default_paths(repo)
    return {
        "sourceProject": base["source_project"],
        "baseFunctions": formal / "inputs/base-functions.tsv",
        "baseProgram": formal / "inputs/base-program.tsv",
        "formalReady": formal / "proof.ready.json",
        "strataBundle": bundle,
        "pilotManifest": bundle / "crt520-stratified-pilot.tsv",
        "fullManifest": bundle / "crt520-full.tsv",
        "toolchain": base["toolchain"],
        "headless": base["headless"],
        "java": base["java"],
        "targetSymbolTool": repo / "tools/ExportTargetSymbolInventory.java",
    }


def validate_pilot_row_lineage(
    pilot_row: Mapping[str, str],
    full_row: Mapping[str, str],
) -> None:
    columns = envelope.MANIFEST_HEADER.split("\t")
    require(set(pilot_row) == set(columns), "pilot manifest columns differ")
    require(set(full_row) == set(columns), "full520 manifest columns differ")
    entry = pilot_row["entry"]
    require(full_row["entry"] == entry, f"pilot/full entry differs at {entry}")
    for field in columns:
        if field != "promotionLane":
            require(
                pilot_row[field] == full_row[field],
                f"pilot row lineage differs from full520 at {entry}: {field}",
            )
    pilot_prefix = "CRT520_STRATIFIED_PILOT_"
    full_prefix = "CRT520_FULL_SCRATCH_"
    pilot_lane = pilot_row["promotionLane"]
    full_lane = full_row["promotionLane"]
    require(pilot_lane.startswith(pilot_prefix), f"pilot lane differs at {entry}")
    require(full_lane.startswith(full_prefix), f"full520 lane differs at {entry}")
    require(
        pilot_lane.removeprefix(pilot_prefix) == full_lane.removeprefix(full_prefix),
        f"pilot/full promotion class differs at {entry}",
    )


def validate_manifest_lineage(
    pilot: Path,
    full: Path,
    *,
    pilot_hash: str = PILOT_MANIFEST_SHA256,
    full_hash: str = FULL_MANIFEST_SHA256,
) -> list[dict[str, str]]:
    pilot_rows = manifest_rows(pilot, expected_hash=pilot_hash)
    full_rows = manifest_rows(full, expected_hash=full_hash)
    require(len(pilot_rows) == PILOT_COUNT and len(full_rows) == strata.EXPECTED_FULL_COUNT, "pilot/full row count differs")
    pilot_entries = [row["entry"] for row in pilot_rows]
    full_entries = [row["entry"] for row in full_rows]
    require(pilot_entries == sorted(pilot_entries) and len(set(pilot_entries)) == PILOT_COUNT, "pilot entries are not unique/sorted")
    require(full_entries == sorted(full_entries) and len(set(full_entries)) == strata.EXPECTED_FULL_COUNT, "full entries are not unique/sorted")
    full_by_entry = {row["entry"]: row for row in full_rows}
    for row in pilot_rows:
        full_row = full_by_entry.get(row["entry"])
        require(full_row is not None, f"pilot entry is absent from full520: {row['entry']}")
        validate_pilot_row_lineage(row, full_row)
        require(row["residualEntityKeys"] and row["questionIds"] and row["contractIds"], f"empty lineage at {row['entry']}")
    require({row["entry"] for row in pilot_rows}.issuperset({f"0x{entry:08x}" for entry in strata.GRAPH_AWARE_MINIMUM}), "pilot omits graph-aware minimum")
    require(SYMBOLLESS_PILOT_ENTRY in pilot_entries, "pilot omits the preregistered symbol-less direct-call closure")
    return pilot_rows


def control_manifests(rows: Sequence[Mapping[str, str]]) -> dict[str, bytes]:
    by_entry = {row["entry"]: dict(row) for row in rows}

    def changed(entry: str, **updates: str) -> dict[str, str]:
        require(entry in by_entry, f"control source is absent: {entry}")
        row = dict(by_entry[entry])
        row.update(updates)
        return row

    wrong_kind = changed(
        "0x00518be0", expectedIsThunk="false", expectedThunkTarget="",
        promotionLane="CRT98_CONTROL_WRONG_THUNK_KIND",
    )
    wrong_target = changed(
        "0x00518be0", expectedThunkTarget="0x0052ff30",
        promotionLane="CRT98_CONTROL_WRONG_THUNK_TARGET",
    )
    side_as_thunk = changed(
        "0x00453090", expectedIsThunk="true", expectedThunkTarget="0x004530a0",
        promotionLane="CRT98_CONTROL_SIDE_TAIL_AS_THUNK",
    )
    truncated = changed(
        "0x004f5f30",
        expectedRanges="0x004f5f30-0x004f5f4f",
        expectedBodyBytes="31",
        expectedRangeDigest="561bc914e052f8140d40c08d09c3565678957aaac1df7d8ffbe4488786b7eb22",
        expectedBodyBytesSha256="95081e615c602e2b2a9eae7091b9498c880b3b5618189bd7c157e8c5f3ecc557",
        expectedInstructionCount="11",
        promotionLane="CRT98_CONTROL_TRUNCATED_INTERNAL_LOOP",
    )
    lineage = [dict(row) for row in rows]
    lineage[0]["questionIds"], lineage[1]["questionIds"] = lineage[1]["questionIds"], lineage[0]["questionIds"]
    lineage[0]["contractIds"], lineage[1]["contractIds"] = lineage[1]["contractIds"], lineage[0]["contractIds"]
    return {
        "wrong-thunk-kind.tsv": render_manifest([wrong_kind]),
        "wrong-thunk-target.tsv": render_manifest([wrong_target]),
        "side-tail-as-thunk.tsv": render_manifest([side_as_thunk]),
        "truncated-internal-loop.tsv": render_manifest([truncated]),
        "lineage-swap.tsv": render_manifest(lineage),
    }


def validate_lineage_poison(poison: bytes, full: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="bea-crt-lineage-poison-") as temporary:
        path = Path(temporary) / "poison.tsv"
        path.write_bytes(poison)
        try:
            validate_manifest_lineage(
                path, full, pilot_hash=sha256_bytes(poison), full_hash=FULL_MANIFEST_SHA256
            )
        except ProofError:
            return
    raise ProofError("lineage-swap poison survived the outer provenance validator")


def validate_java_ready(
    ready_path: Path,
    output_path: Path,
    *,
    mode: str,
    tool: Path,
    manifest: Path,
    count: int,
) -> dict:
    ready = envelope.read_json(ready_path, "batch Java READY")
    require(ready.get("schemaVersion") == envelope.JAVA_READY_SCHEMA and ready.get("mode") == mode, "Java READY schema/mode differs")
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
        ready.get("commitRequested"), ready.get("rollbackRequested"),
        ready.get("transactionEndReturnedCommitted"), ready.get("loadedStateVerified"),
        ready.get("reopenVerificationRequired"),
    )
    require(actual_flags == expected_flags, f"Java READY transaction flags differ for {mode}")
    require(ready.get("namesAuthorized") is False, "Java READY authorizes names")
    require(ready.get("functionKindsBoundByManifest") is True, "Java READY lost function-kind binding")
    require(ready.get("loadedOrTransientEnvelopesVerified") is True, "Java READY lost envelope verification")
    return ready


def output_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        require(tuple(reader.fieldnames or ()) == OUTPUT_HEADER, f"output header differs: {path}")
        rows = [dict(row) for row in reader]
    require(all(None not in row and all(value is not None for value in row.values()) for row in rows), f"shifted output row: {path}")
    return rows


def expected_created_name(
    target: Mapping[str, str],
    base_rows: Mapping[str, Mapping[str, str]],
) -> str:
    entry = target["entry"]
    if target["expectedIsThunk"] != "true":
        return f"FUN_{entry[2:]}"
    destination = target["expectedThunkTarget"]
    require(destination != "", f"thunk target is empty at {entry}")
    require(destination in base_rows, f"thunk target is absent from base inventory at {entry}: {destination}")
    name = base_rows[destination].get("name", "")
    require(name != "", f"thunk target name is empty at {entry}: {destination}")
    return name


def expected_created_sig_source(
    target: Mapping[str, str],
    base_rows: Mapping[str, Mapping[str, str]],
) -> str:
    if target["expectedIsThunk"] != "true":
        return "DEFAULT"
    destination = target["expectedThunkTarget"]
    require(destination in base_rows, f"thunk target is absent from base inventory: {destination}")
    source = base_rows[destination].get("sigSource", "")
    require(source != "", f"thunk target signature source is empty: {destination}")
    return source


def target_symbol_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        require(tuple(reader.fieldnames or ()) == TARGET_SYMBOL_HEADER, f"target-symbol header differs: {path}")
        rows = [dict(row) for row in reader]
    require(
        all(None not in row and all(value is not None for value in row.values()) for row in rows),
        f"shifted target-symbol row: {path}",
    )
    return rows


def target_symbol_argv(
    headless: Path,
    project: Path,
    tool: Path,
    manifest: Path,
    count: int,
    output: Path,
    ready: Path,
) -> list[str]:
    return envelope.windows_batch_argv(headless, [
        str(project.resolve()), envelope.PROJECT_NAME,
        "-process", envelope.PROGRAM_NAME, "-readOnly", "-noanalysis",
        "-scriptPath", str(tool.parent.resolve()), "-postScript", tool.name,
        str(manifest.resolve()), envelope.sha256_file(manifest), str(count),
        str(output.resolve()), str(ready.resolve()),
    ])


def validate_target_symbol_ready(
    ready_path: Path,
    output: Path,
    *,
    tool: Path,
    manifest: Path,
    count: int,
) -> dict[str, object]:
    ready = envelope.read_json(ready_path, "target-symbol READY")
    require(set(ready) == {
        "schemaVersion", "program", "tool", "manifest", "output", "counts",
        "outsideTargetSymbolsSha256",
    }, "target-symbol READY shape differs")
    require(ready["schemaVersion"] == TARGET_SYMBOL_SCHEMA, "target-symbol schema differs")
    require(ready["program"] == envelope.expected_ready_program(), "target-symbol program differs")
    require(ready["tool"] == envelope.external_stamp(tool), "target-symbol tool binding differs")
    require(ready["manifest"] == {
        **envelope.external_stamp(manifest), "expectedCount": count,
    }, "target-symbol manifest binding differs")
    require(ready["output"] == envelope.external_stamp(output), "target-symbol output binding differs")
    counts = ready["counts"]
    require(isinstance(counts, dict) and set(counts) == {
        "targets", "targetSymbols", "zeroSymbols", "dynamicDefaultLabels",
        "nonDynamicDefaultFunctions", "outsideTargetSymbols",
    }, "target-symbol counts differ")
    require(counts["targets"] == count, "target-symbol target count differs")
    require(
        isinstance(counts["outsideTargetSymbols"], int) and counts["outsideTargetSymbols"] > 0,
        "outside-target symbol count is invalid",
    )
    digest = ready["outsideTargetSymbolsSha256"]
    require(isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest) is not None, "outside-target symbol digest is malformed")
    return ready


def validate_base_target_symbols(
    output: Path,
    ready_path: Path,
    *,
    tool: Path,
    manifest: Path,
    count: int = PILOT_COUNT,
) -> dict[str, object]:
    ready = validate_target_symbol_ready(
        ready_path, output, tool=tool, manifest=manifest, count=count,
    )
    rows = target_symbol_rows(output)
    targets = manifest_rows(manifest)
    require(len(rows) == count == len(targets), "base target-symbol row count differs")
    for row, target in zip(rows, targets, strict=True):
        entry = target["entry"]
        expected = {
            "entry": entry,
            "symbolCount": "0" if entry == SYMBOLLESS_PILOT_ENTRY else "1",
            "name": "" if entry == SYMBOLLESS_PILOT_ENTRY else f"LAB_{entry[2:]}",
            "fqname": "" if entry == SYMBOLLESS_PILOT_ENTRY else f"LAB_{entry[2:]}",
            "namespace": "" if entry == SYMBOLLESS_PILOT_ENTRY else "Global",
            "type": "" if entry == SYMBOLLESS_PILOT_ENTRY else "Label",
            "source": "" if entry == SYMBOLLESS_PILOT_ENTRY else "DEFAULT",
            "primary": "" if entry == SYMBOLLESS_PILOT_ENTRY else "true",
            "dynamic": "" if entry == SYMBOLLESS_PILOT_ENTRY else "true",
            "external": "" if entry == SYMBOLLESS_PILOT_ENTRY else "false",
            "pinned": "" if entry == SYMBOLLESS_PILOT_ENTRY else "false",
        }
        require(row == expected, f"base target-symbol row differs: {entry}")
    require(ready["counts"] == {
        "targets": count,
        "targetSymbols": count - 1,
        "zeroSymbols": 1,
        "dynamicDefaultLabels": count - 1,
        "nonDynamicDefaultFunctions": 0,
        "outsideTargetSymbols": ready["counts"]["outsideTargetSymbols"],
    }, "base target-symbol counts differ")
    return {
        "outsideTargetSymbols": ready["counts"]["outsideTargetSymbols"],
        "outsideTargetSymbolsSha256": ready["outsideTargetSymbolsSha256"],
    }


def validate_applied_target_symbols(
    output: Path,
    ready_path: Path,
    *,
    tool: Path,
    manifest: Path,
    base_rows: Mapping[str, Mapping[str, str]],
    base_summary: Mapping[str, object],
    count: int = PILOT_COUNT,
) -> None:
    ready = validate_target_symbol_ready(
        ready_path, output, tool=tool, manifest=manifest, count=count,
    )
    rows = target_symbol_rows(output)
    targets = manifest_rows(manifest)
    require(len(rows) == count == len(targets), "applied target-symbol row count differs")
    for row, target in zip(rows, targets, strict=True):
        entry = target["entry"]
        name = expected_created_name(target, base_rows)
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
        "targets": count,
        "targetSymbols": count,
        "zeroSymbols": 0,
        "dynamicDefaultLabels": 0,
        "nonDynamicDefaultFunctions": count,
        "outsideTargetSymbols": base_summary["outsideTargetSymbols"],
    }, "applied target-symbol counts differ")
    require(
        ready["outsideTargetSymbolsSha256"] == base_summary["outsideTargetSymbolsSha256"],
        "a symbol outside the target set changed",
    )


def run_target_symbol_inventory(
    *,
    proof_root: Path,
    run_id: str,
    headless: Path,
    project: Path,
    tool: Path,
    manifest: Path,
    count: int,
    cwd: Path,
    environment: dict[str, str],
) -> tuple[dict[str, object], Path, Path]:
    run_root = proof_root / "runs" / run_id
    output = run_root / "target-symbols.tsv"
    ready = run_root / "target-symbols.ready.json"
    before = envelope.project_rows(project)
    result, text = envelope.run_process(
        proof_root=proof_root,
        run_id=run_id,
        argv=target_symbol_argv(headless, project, tool, manifest, count, output, ready),
        cwd=cwd,
        environment=environment,
    )
    require(envelope.project_rows(project) == before, f"{run_id} changed a read-only project")
    require(result["exitCode"] == 0 and output.is_file() and ready.is_file(), f"{run_id} target-symbol invocation failed")
    envelope.require_clean_success_log(text, run_id)
    envelope.require_log_identity(text, "TARGET_SYMBOL_TOOL_OK", tool)
    match = re.search(
        r"TARGET_SYMBOL_INVENTORY_OK targets=(\d+) targetSymbols=(\d+) "
        r"outsideTargetSymbols=(\d+) outsideTargetSymbolsSha256=([0-9a-f]{64})",
        text,
    )
    require(match is not None and int(match.group(1)) == count, f"{run_id} lacks target-symbol sentinel")
    java_ready = validate_target_symbol_ready(
        ready, output, tool=tool, manifest=manifest, count=count,
    )
    require(
        int(match.group(2)) == java_ready["counts"]["targetSymbols"]
        and int(match.group(3)) == java_ready["counts"]["outsideTargetSymbols"]
        and match.group(4) == java_ready["outsideTargetSymbolsSha256"],
        f"{run_id} target-symbol sentinel differs from READY",
    )
    result = envelope.finish_run(
        proof_root,
        result,
        output=envelope.stamp(output, proof_root),
        ready=envelope.stamp(ready, proof_root),
        javaReady=java_ready,
        projectFileSetSha256=envelope.rows_digest(before),
    )
    return result, output, ready


def validate_output(
    path: Path,
    manifest: Path,
    *,
    mode: str,
    count: int,
    base_rows: Mapping[str, Mapping[str, str]],
) -> list[dict[str, str]]:
    observed = output_rows(path)
    expected = manifest_rows(manifest)
    require(len(observed) == count == len(expected), f"output row count differs for {mode}")
    status = {"probe": "probed_rollback_requested", "apply": "created_commit_requested", "readback": "verified"}[mode]
    note = {
        "probe": "natural Ghidra body inference matched; outer GhidraScript finalization is pending",
        "apply": "natural Ghidra body inference matched; outer GhidraScript finalization is pending",
        "readback": "exact envelope readback",
    }[mode]
    for row, target in zip(observed, expected, strict=True):
        entry = target["entry"]
        checks = {
            "entry": entry,
            "status": status,
            "name": expected_created_name(target, base_rows),
            "nameSource": "DEFAULT",
            "expectedRanges": target["expectedRanges"],
            "actualRanges": target["expectedRanges"],
            "expectedBodyBytes": target["expectedBodyBytes"],
            "actualBodyBytes": target["expectedBodyBytes"],
            "expectedRangeDigest": target["expectedRangeDigest"],
            "actualRangeDigest": target["expectedRangeDigest"],
            "expectedBodyBytesSha256": target["expectedBodyBytesSha256"],
            "actualBodyBytesSha256": target["expectedBodyBytesSha256"],
            "expectedInstructionCount": target["expectedInstructionCount"],
            "actualInstructionCount": target["expectedInstructionCount"],
            "expectedIsThunk": target["expectedIsThunk"],
            "actualIsThunk": target["expectedIsThunk"],
            "expectedThunkTarget": target["expectedThunkTarget"],
            "actualThunkTarget": target["expectedThunkTarget"],
            "forbiddenEntries": target["forbiddenEntries"],
            "residualEntityKeys": target["residualEntityKeys"],
            "questionIds": target["questionIds"],
            "contractIds": target["contractIds"],
            "promotionLane": target["promotionLane"],
            "note": note,
        }
        for field, value in checks.items():
            require(row.get(field) == value, f"{mode} output {entry} {field} differs: {row.get(field)!r}")
    return observed


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
        require(len(ranges) == 1, f"batch target unexpectedly has multiple ranges: {entry}")
        start, end = ranges[0].split("-", 1)
        require(start == entry, f"batch range does not start at entry: {entry}")
        expected = {
            "address": entry,
            "name": expected_created_name(target, before),
            "nameSource": "DEFAULT",
            "sigSource": expected_created_sig_source(target, before),
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


def run_inventory_diff(
    *, proof_root: Path, run_id: str, python: Path, tool: Path,
    before: Path, after: Path, manifest: Path, cwd: Path, environment: dict[str, str],
) -> dict:
    run_root = proof_root / "runs" / run_id
    output = run_root / "inventory-diff.json"
    argv = envelope.diff_argv(python, tool, before, after, output)
    result, text = envelope.run_process(
        proof_root=proof_root, run_id=run_id, argv=argv, cwd=cwd,
        environment=environment,
    )
    payload = validate_inventory_diff_payload(
        output, [row["entry"] for row in manifest_rows(manifest)]
    )
    counts = payload.get("counts", {})
    require(result["exitCode"] == 0, "inventory diff process failed")
    require(counts.get("before") == envelope.BASE_FUNCTION_COUNT, "diff before count differs")
    require(counts.get("after") == EXPECTED_AFTER_COUNT, "diff after count differs")
    require(counts.get("created") == PILOT_COUNT and counts.get("destroyed") == 0, "diff created/destroyed differs")
    for key in (
        "boundsChanged", "callingConvChanged", "instrCountChanged", "namesChanged",
        "noReturnChanged", "paramCountChanged", "returnTypeChanged", "sigSourceChanged",
        "signaturesChanged", "thunkFlagChanged",
    ):
        require(counts.get(key) == 0, f"diff reports {key}")
    require(all(value in (0, [], {}) for value in payload.get("dangerous", {}).values()), "diff reports dangerous changes")
    return envelope.finish_run(
        proof_root, result, diff=envelope.stamp(output, proof_root),
        stdoutSha256=sha256_bytes(text.encode("utf-8")),
    )


def validate_inventory_diff_payload(
    path: Path,
    expected_entries: Sequence[str],
) -> dict[str, object]:
    payload = envelope.read_json(path, "batch inventory diff")
    require(set(payload) == {
        "beforeFile", "afterFile", "counts", "dangerous", "created",
        "destroyed", "changesByField",
    }, "diff payload shape differs")
    counts = payload.get("counts", {})
    require(counts.get("before") == envelope.BASE_FUNCTION_COUNT, "diff before count differs")
    require(counts.get("after") == EXPECTED_AFTER_COUNT, "diff after count differs")
    require(counts.get("created") == PILOT_COUNT and counts.get("destroyed") == 0, "diff created/destroyed differs")
    for key in (
        "boundsChanged", "callingConvChanged", "instrCountChanged", "namesChanged",
        "noReturnChanged", "paramCountChanged", "returnTypeChanged", "sigSourceChanged",
        "signaturesChanged", "thunkFlagChanged",
    ):
        require(counts.get(key) == 0, f"diff reports {key}")
    require(all(value in (0, [], {}) for value in payload.get("dangerous", {}).values()), "diff reports dangerous changes")
    require(
        [row.get("address") for row in payload.get("created", [])]
        == list(expected_entries),
        "diff created entry list differs",
    )
    require(payload.get("destroyed") == [], "diff destroyed rows differ")
    require(all(value == [] for value in payload.get("changesByField", {}).values()), "diff field-change rows differ")
    return payload


def run_valid_envelope(
    *, proof_root: Path, run_id: str, headless: Path, project: Path,
    tool: Path, manifest: Path, mode: str, cwd: Path,
    environment: dict[str, str], base_rows: Mapping[str, Mapping[str, str]],
) -> tuple[dict, Path, list[dict[str, str]]]:
    result, output, ready, text = envelope.run_envelope(
        proof_root=proof_root, run_id=run_id, headless=headless,
        project_root=project, tool=tool, manifest=manifest,
        expected_count=PILOT_COUNT, mode=mode, cwd=cwd,
        environment=environment,
    )
    require(result["exitCode"] == 0 and f"FUNCTION_ENVELOPE_OK mode={mode}" in text, f"{run_id} failed")
    envelope.require_clean_success_log(text, run_id)
    rows = validate_output(
        output, manifest, mode=mode, count=PILOT_COUNT, base_rows=base_rows
    )
    java = validate_java_ready(ready, output, mode=mode, tool=tool, manifest=manifest, count=PILOT_COUNT)
    receipt = envelope.finish_run(
        proof_root, result, output=envelope.stamp(output, proof_root),
        ready=envelope.stamp(ready, proof_root), rowsSha256=sha256_bytes(canonical_json(rows)),
        javaReady=java,
    )
    return receipt, output, rows


def run_poison(
    *, proof_root: Path, run_id: str, headless: Path, project: Path,
    tool: Path, manifest: Path, pattern: str, cwd: Path,
    environment: dict[str, str],
) -> dict:
    result, output, ready, text = envelope.run_envelope(
        proof_root=proof_root, run_id=run_id, headless=headless,
        project_root=project, tool=tool, manifest=manifest,
        expected_count=1, mode="probe", cwd=cwd, environment=environment,
    )
    return envelope.require_rejection(
        proof_root=proof_root, result=result, output=output, ready=ready,
        text=text, expected_pattern=pattern, mutation_tainted=True,
    )


def compare_to_base(functions: Path, program: Path, base_functions: Path, base_program: Path, label: str) -> None:
    envelope.compare_inventory_to_base(functions, program, base_functions, base_program, label)


def run_replica(
    *, proof_root: Path, replica: str, run_controls: bool,
    headless: Path, python: Path, source_project: Path, tools: dict[str, Path],
    pilot: Path, controls: dict[str, Path], base_functions: Path,
    base_program: Path, base_symbol_summary: Mapping[str, object],
    cwd: Path, environment: dict[str, str],
) -> dict:
    control_project = proof_root / "projects" / f"{replica}-control"
    apply_project = proof_root / "projects" / f"{replica}-apply"
    runs: list[dict] = []
    _, base_rows = envelope.function_rows(base_functions)
    runs.append(envelope.invoke_backup_copy(
        proof_root=proof_root, run_id=f"{replica}-copy-control", python=python,
        backup_tool=tools["backup"], source=source_project, destination=control_project,
        cwd=cwd, environment=environment,
    ))
    runs.append(envelope.invoke_backup_copy(
        proof_root=proof_root, run_id=f"{replica}-copy-apply", python=python,
        backup_tool=tools["backup"], source=source_project, destination=apply_project,
        cwd=cwd, environment=environment,
    ))

    baseline, functions, program = envelope.run_inventory(
        proof_root=proof_root, run_id=f"{replica}-control-baseline", headless=headless,
        project_root=control_project, inventory_tool=tools["inventory"], cwd=cwd,
        environment=environment,
    )
    compare_to_base(functions, program, base_functions, base_program, f"{replica} control baseline")
    runs.append(baseline)

    if run_controls:
        for name, pattern in CONTROL_SPECIFICATIONS:
            runs.append(run_poison(
                proof_root=proof_root, run_id=f"{replica}-control-{name}",
                headless=headless, project=control_project, tool=tools["envelope"],
                manifest=controls[f"{name}.tsv"], pattern=pattern, cwd=cwd,
                environment=environment,
            ))
            reopened, reopened_functions, reopened_program = envelope.run_inventory(
                proof_root=proof_root, run_id=f"{replica}-control-{name}-reopened",
                headless=headless, project_root=control_project,
                inventory_tool=tools["inventory"], cwd=cwd, environment=environment,
            )
            compare_to_base(reopened_functions, reopened_program, base_functions, base_program, f"{replica} {name} rollback")
            runs.append(reopened)

    probe, probe_output, probe_rows = run_valid_envelope(
        proof_root=proof_root, run_id=f"{replica}-probe", headless=headless,
        project=control_project, tool=tools["envelope"], manifest=pilot,
        mode="probe", cwd=cwd, environment=environment, base_rows=base_rows,
    )
    runs.append(probe)
    reopened, reopened_functions, reopened_program = envelope.run_inventory(
        proof_root=proof_root, run_id=f"{replica}-probe-reopened", headless=headless,
        project_root=control_project, inventory_tool=tools["inventory"], cwd=cwd,
        environment=environment,
    )
    compare_to_base(reopened_functions, reopened_program, base_functions, base_program, f"{replica} probe rollback")
    runs.append(reopened)

    apply_baseline, apply_functions, apply_program = envelope.run_inventory(
        proof_root=proof_root, run_id=f"{replica}-apply-baseline", headless=headless,
        project_root=apply_project, inventory_tool=tools["inventory"], cwd=cwd,
        environment=environment,
    )
    compare_to_base(apply_functions, apply_program, base_functions, base_program, f"{replica} apply baseline")
    runs.append(apply_baseline)
    apply, apply_output, apply_rows = run_valid_envelope(
        proof_root=proof_root, run_id=f"{replica}-apply", headless=headless,
        project=apply_project, tool=tools["envelope"], manifest=pilot,
        mode="apply", cwd=cwd, environment=environment, base_rows=base_rows,
    )
    runs.append(apply)
    readback, readback_output, readback_rows = run_valid_envelope(
        proof_root=proof_root, run_id=f"{replica}-readback", headless=headless,
        project=apply_project, tool=tools["envelope"], manifest=pilot,
        mode="readback", cwd=cwd, environment=environment, base_rows=base_rows,
    )
    runs.append(readback)
    require(
        [{k: v for k, v in row.items() if k not in {"status", "note"}} for row in apply_rows]
        == [{k: v for k, v in row.items() if k not in {"status", "note"}} for row in readback_rows],
        f"{replica} apply/readback rows differ",
    )
    after, after_functions, after_program = envelope.run_inventory(
        proof_root=proof_root, run_id=f"{replica}-apply-reopened", headless=headless,
        project_root=apply_project, inventory_tool=tools["inventory"], cwd=cwd,
        environment=environment,
    )
    created = validate_applied_inventory(
        base_functions, base_program, after_functions, after_program, pilot
    )
    runs.append(after)
    runs.append(run_inventory_diff(
        proof_root=proof_root, run_id=f"{replica}-inventory-diff", python=python,
        tool=tools["diff"], before=base_functions, after=after_functions,
        manifest=pilot, cwd=cwd, environment=environment,
    ))

    if run_controls:
        result, output, java_ready, text = envelope.run_envelope(
            proof_root=proof_root, run_id=f"{replica}-reprobe-applied",
            headless=headless, project_root=apply_project, tool=tools["envelope"],
            manifest=pilot, expected_count=PILOT_COUNT, mode="probe", cwd=cwd,
            environment=environment,
        )
        runs.append(envelope.require_rejection(
            proof_root=proof_root, result=result, output=output, ready=java_ready,
            text=text,
            expected_pattern=REPROBE_PATTERN,
            mutation_tainted=False,
        ))
        post, post_functions, post_program = envelope.run_inventory(
            proof_root=proof_root, run_id=f"{replica}-reprobe-applied-reopened",
            headless=headless, project_root=apply_project,
            inventory_tool=tools["inventory"], cwd=cwd, environment=environment,
        )
        require(post_functions.read_bytes() == after_functions.read_bytes(), "reprobe changed applied functions")
        require(post_program.read_bytes() == after_program.read_bytes(), "reprobe changed applied program")
        runs.append(post)

    symbol_run, symbol_output, symbol_ready = run_target_symbol_inventory(
        proof_root=proof_root, run_id=f"{replica}-target-symbols",
        headless=headless, project=apply_project, tool=tools["symbols"],
        manifest=pilot, count=PILOT_COUNT, cwd=cwd, environment=environment,
    )
    validate_applied_target_symbols(
        symbol_output, symbol_ready, tool=tools["symbols"], manifest=pilot,
        base_rows=base_rows, base_summary=base_symbol_summary,
    )
    runs.append(symbol_run)

    return {
        "id": replica,
        "controlProject": str(control_project.resolve()),
        "applyProject": str(apply_project.resolve()),
        "controlsRun": run_controls,
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


def source_stamp(source: Path, snapshot: Path, proof_root: Path) -> dict[str, object]:
    return {
        "source": envelope.external_stamp(source),
        "snapshot": envelope.stamp(snapshot, proof_root),
    }


def snapshot_exact(source: Path, destination: Path, expected_hash: str, proof_root: Path) -> dict[str, object]:
    envelope.snapshot_file(source, destination, expected_hash=expected_hash)
    return source_stamp(source, destination, proof_root)


def expected_checks() -> dict[str, object]:
    return {
        "replicationCount": 2,
        "pilotTargets": PILOT_COUNT,
        "freshControlClones": 2,
        "freshApplyClones": 2,
        "pilotProbeRollbackReopenedExact": True,
        "targetedKindTargetAndLoopPoisonsRejected": True,
        "lineageSwapRejectedBeforeGhidra": True,
        "applyPersistedOnlyOnApplyClones": True,
        "separateProcessReadbackExact": True,
        "preexistingFunctionRowsUnchanged": True,
        "createdFunctionCount": PILOT_COUNT,
        "exactTargetSymbolPreimageAndPostimage": True,
        "outsideTargetSymbolDigestUnchanged": True,
        "defaultSymbolCountDelta": EXPECTED_DEFAULT_SYMBOL_DELTA,
        "replicasSemanticallyEquivalent": True,
        "reprobeAppliedCloneRejectedWithoutChange": True,
        "sourceProjectUnchanged": True,
        "full520ScratchAuthorized": True,
        "livePromotionAuthorized": False,
        "maintainerProjectOpened": False,
    }


def expected_manifest_summary(rows: Sequence[Mapping[str, str]]) -> dict[str, object]:
    require(len(rows) == PILOT_COUNT, "pilot manifest summary row count differs")
    return {
        "count": PILOT_COUNT,
        "sha256": PILOT_MANIFEST_SHA256,
        "full520Sha256": FULL_MANIFEST_SHA256,
        "entries": [row["entry"] for row in rows],
        "bodyBytes": sum(int(row["expectedBodyBytes"]) for row in rows),
        "instructions": sum(int(row["expectedInstructionCount"]) for row in rows),
        "trueThunks": [row["entry"] for row in rows if row["expectedIsThunk"] == "true"],
        "forbiddenEntries": sorted({
            entry for row in rows for entry in row["forbiddenEntries"].split(";") if entry
        }),
    }


def verify_artifact_items_for_ready(
    proof_root: Path,
    ready: Mapping[str, object],
    ready_name: str,
) -> None:
    artifacts = ready.get("artifacts")
    require(
        isinstance(artifacts, dict)
        and artifacts.get("canonicalization")
        == "sorted relative path with exact bytes and SHA-256; READY excluded",
        "READY artifact boundary is malformed",
    )
    actual = envelope.artifact_items(proof_root, ready_name=ready_name)
    require(
        artifacts.get("items") == actual and artifacts.get("count") == len(actual),
        "READY artifact set differs from current proof tree",
    )


def expected_replica_run_specs(
    *,
    proof_root: Path,
    replica_id: str,
    run_controls: bool,
    headless: Path,
    python: Path,
    source_project: Path,
    tools: Mapping[str, Path],
    pilot: Path,
    controls: Mapping[str, Path],
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
        manifest: Path,
        count: int,
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
                headless, project, tools["envelope"], manifest,
                envelope.sha256_file(manifest), count,
                root / "envelopes.tsv", root / "envelopes.ready.json", mode,
            ),
            verdict,
            "envelope",
            manifest=manifest,
            count=count,
            mode=mode,
            pattern=pattern,
            tainted=tainted,
        )

    inventory(f"{replica_id}-control-baseline", control_project)
    if run_controls:
        for name, pattern in CONTROL_SPECIFICATIONS:
            run_id = f"{replica_id}-control-{name}"
            envelope_run(
                run_id, control_project, controls[f"{name}.tsv"], 1,
                "probe", "REFUTED", pattern=pattern, tainted=True,
            )
            inventory(f"{run_id}-reopened", control_project)
    envelope_run(f"{replica_id}-probe", control_project, pilot, PILOT_COUNT, "probe", "SURVIVED")
    inventory(f"{replica_id}-probe-reopened", control_project, final_raw="control")
    inventory(f"{replica_id}-apply-baseline", apply_project)
    envelope_run(f"{replica_id}-apply", apply_project, pilot, PILOT_COUNT, "apply", "SURVIVED")
    envelope_run(f"{replica_id}-readback", apply_project, pilot, PILOT_COUNT, "readback", "SURVIVED")
    inventory(
        f"{replica_id}-apply-reopened", apply_project, applied=True,
        final_raw=None if run_controls else "apply",
    )
    diff_id = f"{replica_id}-inventory-diff"
    diff_root = proof_root / "runs" / diff_id
    add(
        diff_id,
        envelope.diff_argv(
            python, tools["diff"], base_functions,
            proof_root / "runs" / f"{replica_id}-apply-reopened" / "functions.tsv",
            diff_root / "inventory-diff.json",
        ),
        "SURVIVED", "diff",
    )
    if run_controls:
        envelope_run(
            f"{replica_id}-reprobe-applied", apply_project, pilot, PILOT_COUNT,
            "probe", "REFUTED", pattern=REPROBE_PATTERN, tainted=False,
        )
        inventory(
            f"{replica_id}-reprobe-applied-reopened", apply_project,
            applied=True, final_raw="apply",
        )
    symbol_id = f"{replica_id}-target-symbols"
    symbol_root = proof_root / "runs" / symbol_id
    add(
        symbol_id,
        target_symbol_argv(
            headless, apply_project, tools["symbols"], pilot, PILOT_COUNT,
            symbol_root / "target-symbols.tsv",
            symbol_root / "target-symbols.ready.json",
        ),
        "SURVIVED", "symbols", applied=True,
    )
    expected_count = 21 if run_controls else 11
    require(len(specs) == expected_count, f"internal {replica_id} run-spec count differs")
    return specs


def run_proof(args: argparse.Namespace) -> dict[str, object]:
    repo = envelope.require_plain_directory(Path(args.repo_root), "repository root")
    require((repo / "README.MD").is_file() and (repo / "tools").is_dir(), "not the Onslaught repository")
    require(Path(__file__).resolve() == (repo / "tools" / Path(__file__).name).resolve(), "run only the landed batch owner")
    require(envelope.sha256_file(Path(envelope.__file__)) == ENVELOPE_HELPER_SHA256, "envelope helper hash differs")
    paths = default_paths(repo)
    proof_root = envelope.lexical_absolute(Path(args.proof_root))
    local_lab = envelope.require_plain_directory(repo / "local-lab", "repository local-lab")
    require(proof_root.parent.resolve() == local_lab.resolve(), "proof root must be one direct local-lab child")
    require(not proof_root.exists(), "proof root already exists")

    source_project = envelope.require_plain_directory(paths["sourceProject"], "source project")
    source_rows_before = envelope.validate_source_project(source_project)
    base_functions_source = envelope.require_plain_file(
        paths["baseFunctions"], "base functions", expected_hash=envelope.BASE_FUNCTIONS_SHA256
    )
    base_program_source = envelope.require_plain_file(
        paths["baseProgram"], "base program", expected_hash=envelope.BASE_PROGRAM_SHA256
    )
    formal_ready_source = envelope.require_plain_file(
        paths["formalReady"], "formal READY", expected_hash=FORMAL_READY_SHA256
    )
    bundle_source = envelope.require_plain_directory(paths["strataBundle"], "strata bundle")
    require(envelope.sha256_file(bundle_source / "READY.json") == PILOT_READY_SHA256, "strata READY hash differs")
    strata.verify_bundle(repo, formal_ready_source, bundle_source)
    pilot_rows = validate_manifest_lineage(paths["pilotManifest"], paths["fullManifest"])
    envelope.validate_base_inventory(base_functions_source, base_program_source)
    controls_content = control_manifests(pilot_rows)
    validate_lineage_poison(controls_content["lineage-swap.tsv"], paths["fullManifest"])

    envelope.ensure_plain_directory(proof_root, "proof root")
    for name in ("inputs", "inputs/controls", "inputs/toolchain", "tools", "runs", "projects", "work"):
        envelope.ensure_plain_directory(proof_root / name, f"proof {name}")

    input_specs = {
        "formal-proof.ready.json": (formal_ready_source, FORMAL_READY_SHA256),
        "strata.READY.json": (bundle_source / "READY.json", PILOT_READY_SHA256),
        "pilot98.tsv": (paths["pilotManifest"], PILOT_MANIFEST_SHA256),
        "full520.tsv": (paths["fullManifest"], FULL_MANIFEST_SHA256),
        "strata-owner.py": (bundle_source / strata.OWNER_NAME, envelope.sha256_file(bundle_source / strata.OWNER_NAME)),
        "base-functions.tsv": (base_functions_source, envelope.BASE_FUNCTIONS_SHA256),
        "base-program.tsv": (base_program_source, envelope.BASE_PROGRAM_SHA256),
    }
    input_graph: dict[str, object] = {}
    for name, (source, digest) in input_specs.items():
        destination = proof_root / "inputs" / name
        input_graph[name] = snapshot_exact(source, destination, digest, proof_root)
    pilot = proof_root / "inputs/pilot98.tsv"
    full = proof_root / "inputs/full520.tsv"
    base_functions = proof_root / "inputs/base-functions.tsv"
    base_program = proof_root / "inputs/base-program.tsv"

    tools: dict[str, Path] = {}
    tool_graph: dict[str, object] = {}
    for role, name in envelope.EXPECTED_TOOL_NAMES.items():
        source = repo / "tools" / name
        destination = proof_root / "tools" / name
        tool_graph[role] = snapshot_exact(
            source, destination, envelope.EXPECTED_TOOL_SHA256[role], proof_root
        )
        tools[role] = destination
    for role, source, digest in (
        ("envelopeHelper", Path(envelope.__file__).resolve(), ENVELOPE_HELPER_SHA256),
        ("strataHelper", Path(strata.__file__).resolve(), envelope.sha256_file(Path(strata.__file__))),
        ("rttiHelper", repo / "tools/re_rtti_vtables.py", RTTI_HELPER_SHA256),
        ("targetSymbolInventory", paths["targetSymbolTool"], TARGET_SYMBOL_TOOL_SHA256),
        ("runner", Path(__file__).resolve(), envelope.sha256_file(Path(__file__))),
    ):
        destination = proof_root / "tools" / source.name
        tool_graph[role] = snapshot_exact(source, destination, digest, proof_root)
        if role == "targetSymbolInventory":
            tools["symbols"] = destination

    control_paths: dict[str, Path] = {}
    for name, content in controls_content.items():
        path = proof_root / "inputs/controls" / name
        envelope.write_new(path, content)
        control_paths[name] = path

    toolchain_source = envelope.require_plain_directory(paths["toolchain"], "toolchain manifest source")
    distribution_specs = {
        "ghidra": ("ghidra-files.tsv", envelope.GHIDRA_DISTRIBUTION),
        "jdk": ("jdk-files.tsv", envelope.JDK_DISTRIBUTION),
        "python": ("python-files.tsv", envelope.PYTHON_DISTRIBUTION),
    }
    distribution_manifests: dict[str, Path] = {}
    for label, (name, spec) in distribution_specs.items():
        source = envelope.require_plain_file(toolchain_source / name, f"{label} distribution manifest", expected_hash=spec[2])
        destination = proof_root / "inputs/toolchain" / name
        envelope.snapshot_file(source, destination, expected_hash=spec[2])
        distribution_manifests[label] = destination

    headless, properties, java, python = envelope.validate_external_toolchain(
        Path(args.analyze_headless or paths["headless"]), Path(args.java or paths["java"])
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
    before_run, before_functions, before_program = envelope.run_inventory(
        proof_root=proof_root, run_id="source-before", headless=headless,
        project_root=source_project, inventory_tool=tools["inventory"], cwd=cwd,
        environment=environment,
    )
    compare_to_base(before_functions, before_program, base_functions, base_program, "source before")
    before_symbol_run, before_symbols, before_symbols_ready = run_target_symbol_inventory(
        proof_root=proof_root, run_id="source-target-symbols-before",
        headless=headless, project=source_project, tool=tools["symbols"],
        manifest=pilot, count=PILOT_COUNT, cwd=cwd, environment=environment,
    )
    base_symbol_summary = validate_base_target_symbols(
        before_symbols, before_symbols_ready, tool=tools["symbols"], manifest=pilot,
    )

    replicas = [
        run_replica(
            proof_root=proof_root, replica="replica-a", run_controls=True,
            headless=headless, python=python, source_project=source_project,
            tools=tools, pilot=pilot, controls=control_paths,
            base_functions=base_functions, base_program=base_program,
            base_symbol_summary=base_symbol_summary, cwd=cwd,
            environment=environment,
        ),
        run_replica(
            proof_root=proof_root, replica="replica-b", run_controls=False,
            headless=headless, python=python, source_project=source_project,
            tools=tools, pilot=pilot, controls=control_paths,
            base_functions=base_functions, base_program=base_program,
            base_symbol_summary=base_symbol_summary, cwd=cwd,
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
    require(
        replicas[0]["outsideTargetSymbolsSha256"]
        == replicas[1]["outsideTargetSymbolsSha256"]
        == base_symbol_summary["outsideTargetSymbolsSha256"],
        "replica outside-target symbol digests differ",
    )

    after_run, after_functions, after_program = envelope.run_inventory(
        proof_root=proof_root, run_id="source-after", headless=headless,
        project_root=source_project, inventory_tool=tools["inventory"], cwd=cwd,
        environment=environment,
    )
    compare_to_base(after_functions, after_program, base_functions, base_program, "source after")
    after_symbol_run, after_symbols, after_symbols_ready = run_target_symbol_inventory(
        proof_root=proof_root, run_id="source-target-symbols-after",
        headless=headless, project=source_project, tool=tools["symbols"],
        manifest=pilot, count=PILOT_COUNT, cwd=cwd, environment=environment,
    )
    require(
        validate_base_target_symbols(
            after_symbols, after_symbols_ready, tool=tools["symbols"], manifest=pilot,
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
        headless, java
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
        "tools": tool_graph,
        "toolchain": toolchain,
        "manifest": expected_manifest_summary(pilot_rows),
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
    candidate_verification_process = subprocess.run(
        [
            str(python), "-I", "-B", str(frozen_runner),
            "--verify-ready", str(candidate_path),
        ],
        cwd=proof_root / "work",
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
        candidate_verification_process.returncode == 0,
        f"frozen candidate verifier failed: {candidate_verification_process.stderr.strip()}",
    )
    require(candidate_verification_process.stderr == "", "frozen candidate verifier emitted stderr")
    candidate_verification = json.loads(candidate_verification_process.stdout)
    require(candidate_verification == {
        "schema": SCHEMA,
        "verdict": VERDICT,
        "ready": str(candidate_path),
        "readySha256": envelope.sha256_file(candidate_path),
        "replicas": 2,
        "retainedProjectsReopenedReadOnly": 5,
        "pilotTargets": PILOT_COUNT,
        "publicationStatus": "CANDIDATE",
        "full520ScratchAuthorized": False,
        "livePromotionAuthorized": False,
    }, "frozen candidate verifier result differs")

    candidate_sha256 = envelope.sha256_file(candidate_path)
    verify_artifact_items_for_ready(proof_root, ready, candidate_path.name)
    require(not ready_path.exists(), "proof READY appeared before publication")
    os.rename(candidate_path, ready_path)
    return {
        "ready": str(ready_path),
        "readySha256": candidate_sha256,
        "verdict": VERDICT,
        "pilotTargets": PILOT_COUNT,
        "full520ScratchAuthorized": True,
        "livePromotionAuthorized": False,
        "frozenVerifierSurvived": True,
        "frozenVerifierStdoutSha256": sha256_bytes(
            candidate_verification_process.stdout.encode("utf-8")
        ),
        "verifiedCandidatePublishedAtomically": True,
    }


def validate_ready_shape(ready: dict[str, object]) -> None:
    require(set(ready) == {
        "schema", "status", "verdict", "program", "sourceAuthority", "inputs",
        "tools", "toolchain", "manifest", "replicas", "checks", "claimBoundary",
        "artifacts",
    }, "READY top-level shape differs")
    require(ready.get("schema") == SCHEMA and ready.get("status") == STATUS and ready.get("verdict") == VERDICT, "READY identity differs")
    require(ready.get("program") == envelope.expected_ready_program(), "READY program differs")
    require(ready.get("checks") == expected_checks(), "READY checks differ")
    require(ready.get("claimBoundary") == list(CLAIM_BOUNDARY), "READY claim boundary differs")
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
    summary = source.get("targetSymbolSummary")
    require(
        isinstance(summary, dict)
        and set(summary) == {"outsideTargetSymbols", "outsideTargetSymbolsSha256"}
        and isinstance(summary.get("outsideTargetSymbols"), int)
        and summary["outsideTargetSymbols"] > 0
        and isinstance(summary.get("outsideTargetSymbolsSha256"), str)
        and re.fullmatch(r"[0-9a-f]{64}", summary["outsideTargetSymbolsSha256"]) is not None,
        "READY source target-symbol summary differs",
    )
    inputs = ready.get("inputs")
    require(isinstance(inputs, dict) and set(inputs) == {
        "formal-proof.ready.json", "strata.READY.json", "pilot98.tsv", "full520.tsv",
        "strata-owner.py", "base-functions.tsv", "base-program.tsv",
    }, "READY input graph differs")
    require(all(isinstance(record, dict) and set(record) == {"source", "snapshot"} for record in inputs.values()), "READY input record shape differs")
    tools = ready.get("tools")
    require(isinstance(tools, dict) and set(tools) == {
        *envelope.EXPECTED_TOOL_NAMES, "envelopeHelper", "strataHelper", "rttiHelper",
        "targetSymbolInventory", "runner",
    }, "READY tool graph differs")
    require(all(isinstance(record, dict) and set(record) == {"source", "snapshot"} for record in tools.values()), "READY tool record shape differs")
    toolchain = ready.get("toolchain")
    require(isinstance(toolchain, dict) and set(toolchain) == {
        "analyzeHeadless", "applicationProperties", "java", "python",
        "ghidraDistribution", "jdkDistribution", "pythonDistribution",
    }, "READY toolchain shape differs")
    for key in ("analyzeHeadless", "applicationProperties", "java", "python"):
        require(isinstance(toolchain[key], dict) and set(toolchain[key]) == {"path", "bytes", "sha256"}, f"READY {key} stamp shape differs")
    for key in ("ghidraDistribution", "jdkDistribution", "pythonDistribution"):
        require(isinstance(toolchain[key], dict) and set(toolchain[key]) == {
            "root", "fileCount", "totalBytes", "fileSetSha256", "manifest",
        }, f"READY {key} shape differs")
    manifest = ready.get("manifest")
    require(isinstance(manifest, dict), "READY manifest is absent")
    require(set(manifest) == {
        "count", "sha256", "full520Sha256", "entries", "bodyBytes",
        "instructions", "trueThunks", "forbiddenEntries",
    }, "READY manifest shape differs")
    require(manifest.get("count") == PILOT_COUNT and manifest.get("sha256") == PILOT_MANIFEST_SHA256, "READY pilot identity differs")
    require(manifest.get("full520Sha256") == FULL_MANIFEST_SHA256, "READY full520 identity differs")
    replicas = ready.get("replicas")
    require(isinstance(replicas, list) and [row.get("id") for row in replicas] == ["replica-a", "replica-b"], "READY replicas differ")
    require([row.get("controlsRun") for row in replicas] == [True, False], "READY control allocation differs")
    require([len(row.get("runs", [])) for row in replicas] == [21, 11], "READY run cardinalities differ")
    replica_keys = {
        "id", "controlProject", "applyProject", "controlsRun", "runs",
        "probeOutput", "applyOutput", "readbackOutput", "afterFunctions",
        "afterProgram", "targetSymbols", "targetSymbolsReady",
        "outsideTargetSymbolsSha256", "createdRowsSha256", "createdEntries",
        "controlProjectFileSetSha256", "applyProjectFileSetSha256",
    }
    for replica in replicas:
        require(set(replica) == replica_keys, f"READY {replica.get('id')} shape differs")
        require(
            isinstance(replica.get("createdEntries"), list)
            and len(replica["createdEntries"]) == PILOT_COUNT
            and replica["createdEntries"] == sorted(replica["createdEntries"]),
            f"READY {replica.get('id')} created entries differ",
        )
        for key in (
            "createdRowsSha256", "controlProjectFileSetSha256",
            "applyProjectFileSetSha256", "outsideTargetSymbolsSha256",
        ):
            require(isinstance(replica.get(key), str) and re.fullmatch(r"[0-9a-f]{64}", replica[key]) is not None, f"READY {replica.get('id')} {key} differs")
    artifacts = ready.get("artifacts")
    require(isinstance(artifacts, dict) and set(artifacts) == {"canonicalization", "count", "items"}, "READY artifact shape differs")


def verify_recorded_replica(
    *,
    proof_root: Path,
    replica: dict[str, object],
    headless: Path,
    java: Path,
    python: Path,
    source_project: Path,
    tools: Mapping[str, Path],
    pilot: Path,
    controls: Mapping[str, Path],
    base_functions: Path,
    base_program: Path,
    base_rows: Mapping[str, Mapping[str, str]],
    base_symbol_summary: Mapping[str, object],
    pilot_rows: Sequence[Mapping[str, str]],
) -> None:
    replica_id = str(replica["id"])
    run_controls = bool(replica["controlsRun"])
    control_project = proof_root / "projects" / f"{replica_id}-control"
    apply_project = proof_root / "projects" / f"{replica_id}-apply"
    require(replica["controlProject"] == str(control_project.resolve()), f"{replica_id} control project path differs")
    require(replica["applyProject"] == str(apply_project.resolve()), f"{replica_id} apply project path differs")
    require(replica["createdEntries"] == [row["entry"] for row in pilot_rows], f"{replica_id} created entries differ")

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
        proof_root=proof_root, replica_id=replica_id, run_controls=run_controls,
        headless=headless, python=python, source_project=source_project,
        tools=tools, pilot=pilot, controls=controls, base_functions=base_functions,
    )
    receipts = envelope.require_receipt_stamp_order(
        replica["runs"], [str(spec["id"]) for spec in specs], replica_id
    )
    expected_environment = envelope.expected_sanitized_environment(proof_root, java)
    for index, (receipt_stamp, spec) in enumerate(zip(receipts, specs, strict=True)):
        run_id = str(spec["id"])
        receipt = envelope.verify_run_receipt(
            proof_root, receipt_stamp, f"{replica_id} run {index}",
            expected_id=run_id, expected_argv=spec["argv"],
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
                f"{run_id} backup project digests differ",
            )
            destination = Path(spec["destination"])
            manifest_stamp = observations["backupManifest"]
            require(isinstance(manifest_stamp, dict) and manifest_stamp.get("path") == envelope.stamp(destination / "backup_manifest.json", proof_root)["path"], f"{run_id} backup manifest path differs")
            envelope.validate_frozen_stamp(proof_root, manifest_stamp, f"{run_id} backup manifest")
        elif kind == "inventory":
            require(set(observations) == {
                "functionCount", "instructionCount", "functions", "program", "projectFileSetSha256",
            }, f"{run_id} inventory observations differ")
            functions = run_root / "functions.tsv"
            program = run_root / "program.tsv"
            require(observations["functions"] == envelope.stamp(functions, proof_root), f"{run_id} functions stamp differs")
            require(observations["program"] == envelope.stamp(program, proof_root), f"{run_id} program stamp differs")
            applied = bool(spec["applied"])
            require(observations["instructionCount"] == envelope.BASE_INSTRUCTION_COUNT, f"{run_id} instruction count differs")
            require(observations["functionCount"] == (EXPECTED_AFTER_COUNT if applied else envelope.BASE_FUNCTION_COUNT), f"{run_id} function count differs")
            raw_digest = observations["projectFileSetSha256"]
            require(isinstance(raw_digest, str) and re.fullmatch(r"[0-9a-f]{64}", raw_digest) is not None, f"{run_id} project digest is malformed")
            if spec["finalRaw"] == "control":
                require(raw_digest == replica["controlProjectFileSetSha256"], f"{run_id} final control digest differs")
            elif spec["finalRaw"] == "apply":
                require(raw_digest == replica["applyProjectFileSetSha256"], f"{run_id} final apply digest differs")
            if applied:
                validate_applied_inventory(base_functions, base_program, functions, program, pilot)
            else:
                compare_to_base(functions, program, base_functions, base_program, run_id)
        elif kind == "envelope" and spec["verdict"] == "SURVIVED":
            require(set(observations) == {"output", "ready", "rowsSha256", "javaReady"}, f"{run_id} envelope observations differ")
            output = run_root / "envelopes.tsv"
            java_ready_path = run_root / "envelopes.ready.json"
            rows = validate_output(
                output, Path(spec["manifest"]), mode=str(spec["mode"]),
                count=int(spec["count"]), base_rows=base_rows,
            )
            java_ready = validate_java_ready(
                java_ready_path, output, mode=str(spec["mode"]),
                tool=tools["envelope"], manifest=Path(spec["manifest"]),
                count=int(spec["count"]),
            )
            require(observations["output"] == envelope.stamp(output, proof_root), f"{run_id} output stamp differs")
            require(observations["ready"] == envelope.stamp(java_ready_path, proof_root), f"{run_id} READY stamp differs")
            require(observations["rowsSha256"] == sha256_bytes(canonical_json(rows)), f"{run_id} row digest differs")
            require(observations["javaReady"] == java_ready, f"{run_id} Java READY observation differs")
        elif kind == "envelope":
            require(set(observations) == {
                "expectedPattern", "scriptErrorCount", "mutationTainted",
                "outputPublished", "readyPublished",
            }, f"{run_id} rejection observations differ")
            require(observations == {
                "expectedPattern": spec["pattern"],
                "scriptErrorCount": 1,
                "mutationTainted": spec["tainted"],
                "outputPublished": False,
                "readyPublished": False,
            }, f"{run_id} rejection observation values differ")
            require(not (run_root / "envelopes.tsv").exists() and not (run_root / "envelopes.ready.json").exists(), f"{run_id} rejection published output")
        elif kind == "diff":
            require(set(observations) == {"diff", "stdoutSha256"}, f"{run_id} diff observations differ")
            diff = run_root / "inventory-diff.json"
            require(observations["diff"] == envelope.stamp(diff, proof_root), f"{run_id} diff stamp differs")
            log = envelope.validate_frozen_stamp(proof_root, receipt["log"], f"{run_id} log")
            require(observations["stdoutSha256"] == sha256_bytes(log.read_bytes()), f"{run_id} stdout digest differs")
            payload = validate_inventory_diff_payload(diff, [row["entry"] for row in pilot_rows])
            require(payload.get("beforeFile") == str(base_functions.resolve()), f"{run_id} diff before path differs")
            require(payload.get("afterFile") == str((proof_root / "runs" / f"{replica_id}-apply-reopened" / "functions.tsv").resolve()), f"{run_id} diff after path differs")
        elif kind == "symbols":
            require(set(observations) == {
                "output", "ready", "javaReady", "projectFileSetSha256",
            }, f"{run_id} target-symbol observations differ")
            output = run_root / "target-symbols.tsv"
            java_ready_path = run_root / "target-symbols.ready.json"
            java_ready = validate_target_symbol_ready(
                java_ready_path, output, tool=tools["symbols"], manifest=pilot,
                count=PILOT_COUNT,
            )
            validate_applied_target_symbols(
                output, java_ready_path, tool=tools["symbols"], manifest=pilot,
                base_rows=base_rows, base_summary=base_symbol_summary,
            )
            require(observations == {
                "output": envelope.stamp(output, proof_root),
                "ready": envelope.stamp(java_ready_path, proof_root),
                "javaReady": java_ready,
                "projectFileSetSha256": replica["applyProjectFileSetSha256"],
            }, f"{run_id} target-symbol observation values differ")
        else:
            raise ProofError(f"unsupported run kind: {run_id} {kind}")

    after_functions = envelope.validate_frozen_stamp(proof_root, replica["afterFunctions"], f"{replica_id} after functions")
    after_program = envelope.validate_frozen_stamp(proof_root, replica["afterProgram"], f"{replica_id} after program")
    created = validate_applied_inventory(base_functions, base_program, after_functions, after_program, pilot)
    require(replica["createdEntries"] == sorted(created), f"{replica_id} created set does not reproduce")
    require(replica["createdRowsSha256"] == sha256_bytes(canonical_json(created)), f"{replica_id} created-row digest differs")
    validate_applied_target_symbols(
        envelope.validate_frozen_stamp(proof_root, replica["targetSymbols"], f"{replica_id} target symbols"),
        envelope.validate_frozen_stamp(proof_root, replica["targetSymbolsReady"], f"{replica_id} target-symbol READY"),
        tool=tools["symbols"], manifest=pilot, base_rows=base_rows,
        base_summary=base_symbol_summary,
    )
    require(
        replica["outsideTargetSymbolsSha256"] == base_symbol_summary["outsideTargetSymbolsSha256"],
        f"{replica_id} outside-target symbol digest differs",
    )


def verify_control_logs(proof_root: Path) -> None:
    for name, pattern in CONTROL_SPECIFICATIONS:
        root = proof_root / "runs" / f"replica-a-control-{name}"
        require(not (root / "envelopes.tsv").exists() and not (root / "envelopes.ready.json").exists(), f"{name} published output")
        text = (root / "headless.log").read_text(encoding="utf-8")
        require(text.count("REPORT SCRIPT ERROR") == 1 and re.search(pattern, text) is not None, f"{name} rejection differs")
        require("FUNCTION_ENVELOPE_MUTATION_TAINTED" in text, f"{name} lacks transaction taint")
        require("FUNCTION_ENVELOPE_OK" not in text, f"{name} emitted a success sentinel")
    root = proof_root / "runs/replica-a-reprobe-applied"
    require(not (root / "envelopes.tsv").exists() and not (root / "envelopes.ready.json").exists(), "reprobe published output")
    text = (root / "headless.log").read_text(encoding="utf-8")
    require(text.count("REPORT SCRIPT ERROR") == 1 and REPROBE_PATTERN in text, "reprobe rejection differs")
    require("FUNCTION_ENVELOPE_MUTATION_TAINTED" not in text, "reprobe was incorrectly transaction-tainted")
    require("FUNCTION_ENVELOPE_OK" not in text, "reprobe emitted a success sentinel")


def live_reverify(
    *, proof_root: Path, ready: dict[str, object], headless: Path, java: Path,
    inventory_tool: Path, symbol_tool: Path, pilot: Path,
    base_functions: Path, base_program: Path,
    base_rows: Mapping[str, Mapping[str, str]],
    base_symbol_summary: Mapping[str, object],
) -> None:
    source = envelope.require_plain_directory(Path(ready["sourceAuthority"]["projectRoot"]), "source project")
    projects: list[tuple[str, Path, Path, Path, str]] = [
        ("source-current", source, base_functions, base_program, envelope.BASE_PROJECT_FILE_SET_SHA256)
    ]
    for replica in ready["replicas"]:
        replica_id = replica["id"]
        projects.append((
            f"{replica_id}-control-current",
            envelope.require_plain_directory(proof_root / "projects" / f"{replica_id}-control", "retained control"),
            base_functions, base_program, replica["controlProjectFileSetSha256"],
        ))
        projects.append((
            f"{replica_id}-apply-current",
            envelope.require_plain_directory(proof_root / "projects" / f"{replica_id}-apply", "retained apply"),
            envelope.validate_frozen_stamp(proof_root, replica["afterFunctions"], "recorded functions"),
            envelope.validate_frozen_stamp(proof_root, replica["afterProgram"], "recorded program"),
            replica["applyProjectFileSetSha256"],
        ))
    with tempfile.TemporaryDirectory(prefix="bea-crt98-ready-verify-") as temporary:
        verification = Path(temporary)
        envelope.ensure_plain_directory(verification / "runs", "verification runs")
        envelope.ensure_plain_directory(verification / "work", "verification work")
        environment = envelope.sanitized_environment(verification, java)
        for run_id, project, expected_functions, expected_program, raw_digest in projects:
            before = envelope.project_rows(project)
            require(envelope.rows_digest(before) == raw_digest, f"retained {run_id} raw project differs")
            _, functions, program = envelope.run_inventory(
                proof_root=verification, run_id=run_id, headless=headless,
                project_root=project, inventory_tool=inventory_tool,
                cwd=verification / "work", environment=environment,
            )
            require(functions.read_bytes() == expected_functions.read_bytes(), f"retained {run_id} functions differ")
            require(program.read_bytes() == expected_program.read_bytes(), f"retained {run_id} program differs")
            require(envelope.project_rows(project) == before, f"retained {run_id} changed during readback")
            if run_id == "source-current" or run_id.endswith("-apply-current"):
                _, symbols, symbol_ready = run_target_symbol_inventory(
                    proof_root=verification, run_id=f"{run_id}-target-symbols",
                    headless=headless, project=project, tool=symbol_tool,
                    manifest=pilot, count=PILOT_COUNT, cwd=verification / "work",
                    environment=environment,
                )
                if run_id == "source-current":
                    require(
                        validate_base_target_symbols(
                            symbols, symbol_ready, tool=symbol_tool, manifest=pilot,
                        ) == base_symbol_summary,
                        "retained source target-symbol summary differs",
                    )
                else:
                    validate_applied_target_symbols(
                        symbols, symbol_ready, tool=symbol_tool, manifest=pilot,
                        base_rows=base_rows, base_summary=base_symbol_summary,
                    )


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
    require(isinstance(stamp, dict) and stamp.get("path") == f"runs/{run_id}/run.json", f"{receipt_name} path differs")
    receipt = envelope.verify_run_receipt(
        proof_root, stamp, receipt_name,
        expected_id=run_id,
        expected_argv=envelope.inventory_argv(
            headless, source_project, inventory_tool,
            run_root / "functions.tsv", run_root / "program.tsv",
        ),
        expected_cwd=proof_root / "work",
        expected_environment=envelope.expected_sanitized_environment(proof_root, java),
        expected_verdict="SURVIVED",
    )
    require(receipt["log"]["path"] == f"runs/{run_id}/headless.log", f"{run_id} log path differs")
    observations = receipt["observations"]
    require(set(observations) == {
        "functionCount", "instructionCount", "functions", "program", "projectFileSetSha256",
    }, f"{run_id} observations differ")
    functions = run_root / "functions.tsv"
    program = run_root / "program.tsv"
    require(observations == {
        "functionCount": envelope.BASE_FUNCTION_COUNT,
        "instructionCount": envelope.BASE_INSTRUCTION_COUNT,
        "functions": envelope.stamp(functions, proof_root),
        "program": envelope.stamp(program, proof_root),
        "projectFileSetSha256": envelope.BASE_PROJECT_FILE_SET_SHA256,
    }, f"{run_id} observation values differ")
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
    pilot: Path,
) -> dict[str, object]:
    run_root = proof_root / "runs" / run_id
    stamp = ready["sourceAuthority"][receipt_name]
    require(isinstance(stamp, dict) and stamp.get("path") == f"runs/{run_id}/run.json", f"{receipt_name} path differs")
    output = run_root / "target-symbols.tsv"
    java_ready_path = run_root / "target-symbols.ready.json"
    receipt = envelope.verify_run_receipt(
        proof_root, stamp, receipt_name,
        expected_id=run_id,
        expected_argv=target_symbol_argv(
            headless, source_project, symbol_tool, pilot, PILOT_COUNT,
            output, java_ready_path,
        ),
        expected_cwd=proof_root / "work",
        expected_environment=envelope.expected_sanitized_environment(proof_root, java),
        expected_verdict="SURVIVED",
    )
    require(receipt["log"]["path"] == f"runs/{run_id}/headless.log", f"{run_id} log path differs")
    java_ready = validate_target_symbol_ready(
        java_ready_path, output, tool=symbol_tool, manifest=pilot, count=PILOT_COUNT,
    )
    require(receipt["observations"] == {
        "output": envelope.stamp(output, proof_root),
        "ready": envelope.stamp(java_ready_path, proof_root),
        "javaReady": java_ready,
        "projectFileSetSha256": envelope.BASE_PROJECT_FILE_SET_SHA256,
    }, f"{run_id} target-symbol observations differ")
    require(
        ready["sourceAuthority"][output_name] == envelope.stamp(output, proof_root),
        f"{output_name} stamp differs",
    )
    return validate_base_target_symbols(
        output, java_ready_path, tool=symbol_tool, manifest=pilot,
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
    verify_artifact_items_for_ready(proof_root, ready, ready_path.name)
    require(proof_root.parent.name == "local-lab", "proof READY must remain one direct repository local-lab child")
    repo = envelope.require_plain_directory(proof_root.parent.parent, "proof repository")
    require((repo / "README.MD").is_file() and (repo / "tools").is_dir(), "proof parent is not Onslaught Toolkit")
    paths = default_paths(repo)

    input_sources = {
        "formal-proof.ready.json": (paths["formalReady"], FORMAL_READY_SHA256),
        "strata.READY.json": (paths["strataBundle"] / "READY.json", PILOT_READY_SHA256),
        "pilot98.tsv": (paths["pilotManifest"], PILOT_MANIFEST_SHA256),
        "full520.tsv": (paths["fullManifest"], FULL_MANIFEST_SHA256),
        "strata-owner.py": (
            paths["strataBundle"] / strata.OWNER_NAME,
            envelope.sha256_file(paths["strataBundle"] / strata.OWNER_NAME),
        ),
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
    frozen_pilot = proof_root / "inputs/pilot98.tsv"
    frozen_full = proof_root / "inputs/full520.tsv"
    pilot_rows = validate_manifest_lineage(frozen_pilot, frozen_full)
    require(ready["manifest"] == expected_manifest_summary(pilot_rows), "READY manifest values differ")
    controls = control_manifests(pilot_rows)
    control_paths: dict[str, Path] = {}
    for name, content in controls.items():
        path = envelope.require_plain_file(proof_root / "inputs/controls" / name, f"frozen {name}")
        require(path.read_bytes() == content, f"frozen control differs: {name}")
        control_paths[name] = path
    validate_lineage_poison(controls["lineage-swap.tsv"], frozen_full)

    base_functions = proof_root / "inputs/base-functions.tsv"
    base_program = proof_root / "inputs/base-program.tsv"
    envelope.validate_base_inventory(base_functions, base_program)
    _, base_rows = envelope.function_rows(base_functions)
    tools: dict[str, Path] = {}
    for role, digest in envelope.EXPECTED_TOOL_SHA256.items():
        record = ready["tools"][role]
        source = repo / "tools" / envelope.EXPECTED_TOOL_NAMES[role]
        require(record["source"] == envelope.external_stamp(source), f"{role} tool provenance source differs")
        require(record["snapshot"].get("path") == f"tools/{envelope.EXPECTED_TOOL_NAMES[role]}", f"{role} tool snapshot path differs")
        tool = envelope.validate_frozen_stamp(proof_root, record["snapshot"], f"frozen {role}")
        require(envelope.sha256_file(tool) == digest, f"frozen {role} hash differs")
        tools[role] = tool
    extra_tools = {
        "envelopeHelper": (repo / "tools/ghidra_function_envelope_proof.py", ENVELOPE_HELPER_SHA256),
        "strataHelper": (repo / "tools/re_crt_function_strata.py", envelope.sha256_file(repo / "tools/re_crt_function_strata.py")),
        "rttiHelper": (repo / "tools/re_rtti_vtables.py", RTTI_HELPER_SHA256),
        "targetSymbolInventory": (paths["targetSymbolTool"], TARGET_SYMBOL_TOOL_SHA256),
        "runner": (repo / "tools/ghidra_function_batch_proof.py", envelope.sha256_file(Path(__file__))),
    }
    for role, (source, expected_hash) in extra_tools.items():
        record = ready["tools"][role]
        require(record["source"] == envelope.external_stamp(source), f"{role} provenance source differs")
        require(record["snapshot"].get("path") == f"tools/{source.name}", f"{role} snapshot path differs")
        snapshot = envelope.validate_frozen_stamp(proof_root, record["snapshot"], f"frozen {role}")
        require(envelope.sha256_file(snapshot) == expected_hash, f"{role} snapshot hash differs")
        if role == "targetSymbolInventory":
            tools["symbols"] = snapshot
    runner = envelope.validate_frozen_stamp(proof_root, ready["tools"]["runner"]["snapshot"], "frozen runner")
    require(runner.read_bytes() == Path(__file__).read_bytes(), "invoke verifier with the exact frozen owner")

    toolchain = ready["toolchain"]
    headless = envelope.resolve_external_stamp(toolchain["analyzeHeadless"], "analyzeHeadless", expected_hash=envelope.ANALYZE_HEADLESS_SHA256)
    properties = envelope.resolve_external_stamp(toolchain["applicationProperties"], "Ghidra properties", expected_hash=envelope.GHIDRA_APPLICATION_PROPERTIES_SHA256)
    java = envelope.resolve_external_stamp(toolchain["java"], "Java", expected_hash=envelope.HOST_JAVA_SHA256)
    python = envelope.resolve_external_stamp(toolchain["python"], "Python", expected_hash=envelope.PYTHON_SHA256)
    require(properties == headless.parent.parent / "Ghidra/application.properties", "Ghidra launcher/properties roots differ")
    for label, root, spec, key, manifest_name in (
        ("Ghidra", headless.parent.parent, envelope.GHIDRA_DISTRIBUTION, "ghidraDistribution", "ghidra-files.tsv"),
        ("JDK", java.parent.parent, envelope.JDK_DISTRIBUTION, "jdkDistribution", "jdk-files.tsv"),
        ("Python", python.parent, envelope.PYTHON_DISTRIBUTION, "pythonDistribution", "python-files.tsv"),
    ):
        record = toolchain[key]
        require(record["manifest"].get("path") == f"inputs/toolchain/{manifest_name}", f"{label} distribution manifest path differs")
        manifest = envelope.validate_frozen_stamp(proof_root, record["manifest"], f"{label} distribution manifest")
        current = envelope.verify_distribution(root, manifest, spec, label)
        for field in ("root", "fileCount", "totalBytes", "fileSetSha256"):
            require(record.get(field) == current[field], f"{label} distribution differs")

    source_project = envelope.require_plain_directory(paths["sourceProject"], "derived source project")
    require(ready["sourceAuthority"]["projectRoot"] == str(source_project.resolve()), "READY source project path differs")
    require(envelope.rows_digest(envelope.validate_source_project(source_project)) == ready["sourceAuthority"]["projectFileSetSha256"], "READY source project identity differs")
    for receipt_name, run_id in (("sourceBeforeRun", "source-before"), ("sourceAfterRun", "source-after")):
        verify_source_inventory_receipt(
            proof_root=proof_root, ready=ready, receipt_name=receipt_name,
            run_id=run_id, headless=headless, java=java,
            source_project=source_project, inventory_tool=tools["inventory"],
            base_functions=base_functions, base_program=base_program,
        )
    before_symbol_summary = verify_source_symbol_receipt(
        proof_root=proof_root, ready=ready,
        receipt_name="targetSymbolsBeforeRun", output_name="targetSymbolsBefore",
        run_id="source-target-symbols-before", headless=headless, java=java,
        source_project=source_project, symbol_tool=tools["symbols"], pilot=frozen_pilot,
    )
    after_symbol_summary = verify_source_symbol_receipt(
        proof_root=proof_root, ready=ready,
        receipt_name="targetSymbolsAfterRun", output_name="targetSymbolsAfter",
        run_id="source-target-symbols-after", headless=headless, java=java,
        source_project=source_project, symbol_tool=tools["symbols"], pilot=frozen_pilot,
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
            proof_root=proof_root, replica=replica, headless=headless,
            java=java, python=python, source_project=source_project,
            tools=tools, pilot=frozen_pilot, controls=control_paths,
            base_functions=base_functions, base_program=base_program,
            base_rows=base_rows, base_symbol_summary=before_symbol_summary,
            pilot_rows=pilot_rows,
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
        proof_root=proof_root, ready=ready, headless=headless, java=java,
        inventory_tool=tools["inventory"], symbol_tool=tools["symbols"],
        pilot=frozen_pilot, base_functions=base_functions,
        base_program=base_program, base_rows=base_rows,
        base_symbol_summary=before_symbol_summary,
    )
    verify_artifact_items_for_ready(proof_root, ready, ready_path.name)
    published = ready_path.name == "proof.ready.json"
    return {
        "schema": SCHEMA,
        "verdict": VERDICT,
        "ready": str(ready_path),
        "readySha256": envelope.sha256_file(ready_path),
        "replicas": 2,
        "retainedProjectsReopenedReadOnly": 5,
        "pilotTargets": PILOT_COUNT,
        "publicationStatus": "READY" if published else "CANDIDATE",
        "full520ScratchAuthorized": published,
        "livePromotionAuthorized": False,
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
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0
    except (ProofError, OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"UNSCORED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
