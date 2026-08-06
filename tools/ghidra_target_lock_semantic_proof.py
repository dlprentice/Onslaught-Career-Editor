#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Freeze and verify the five-function BattleEngine target-lock scratch proof.

This is deliberately cohort-specific.  It validates the exact v4 scratch
boundary, negative controls, two independent applies, separate-process
readback, and complete PRE/POST inventories.  It never opens or mutates a
Ghidra project.  A core proof remains non-terminal until four exact-artifact
independent reviews and a separately frozen semantic refuter survive
``finalize``.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
from typing import Iterable, Mapping, Sequence
import uuid


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import ghidra_function_envelope_proof as common  # noqa: E402


ProofError = common.ProofError

CORE_SCHEMA = "bea.re.ghidra-target-lock-semantic-proof-core.v2"
SUBJECT_SCHEMA = "bea.re.ghidra-target-lock-semantic-refuter-subject.v2"
REVIEW_SCHEMA = "bea.re.ghidra-target-lock-semantic-review.v1"
REVIEW_RUN_SCHEMA = "bea.re.ghidra-target-lock-semantic-review-run.v1"
REFUTER_SCHEMA = "bea.re.ghidra-target-lock-semantic-refuter.v2"
READY_SCHEMA = "bea.re.ghidra-target-lock-semantic-proof-ready.v2"
JAVA_SCHEMA = "bea.ghidra.target-lock-semantic.v3"

ADDRESSES = (
    "0x00406fc0",
    "0x00407060",
    "0x00407140",
    "0x004071b0",
    "0x00407310",
)
PROPOSED_NAMES = {
    "0x00406fc0": "CBattleEngine__StartLock",
    "0x00407060": "CBattleEngine__FireLock",
    "0x00407140": "CBattleEngine__LockHit",
    "0x004071b0": "CBattleEngine__GetCurrentTarget",
    "0x00407310": "CBattleEngine__DisplayLock",
}

PLAN_SHA256 = "f6556238580a8d54b95e5603cd41e70313cebe7a9c92dff45687db7d21bc73c9"
EVIDENCE_SHA256 = "16c07f34feb374067ea19a9019da1f1a648778338d905928e989eced506e7ebc"
SEMANTIC_TOOL_SHA256 = "d3ab355408a70f66032f9a671c846ccf63d154fcd703d1ce20ee7a66396d4485"
INVENTORY_TOOL_SHA256 = "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197"
COMMON_HELPER_SHA256 = "e20d619c39dd0f2037523b4577860b6640ed76b0be058472834a587192b305e8"

PRE_FUNCTIONS_SHA256 = "e7ffc76b6073cf9f96c057ded436e24958596d9d14162e89f3e2d1007b620950"
PRE_PROGRAM_SHA256 = "050c1a9bfd6b421077cb5ea0f6f715edde6b0eac8f8cb65ad4c2294945366ac2"
DRY_OUTPUT_SHA256 = "753217a36ecaa2c817d74a9bf3bc0f86b98ae2604238ed9d873a5f40c61ab644"
APPLY_OUTPUT_SHA256 = "e583d6077425f02da8b34234f6e172ec89db56c39200dc992122a42f1ff90123"
READBACK_OUTPUT_SHA256 = "047a800a821be18ba10eb7cc325ee8d724cccba49049e4270f01e2f761329b7d"
POST_FUNCTIONS_SHA256 = "f9a06dcdb0ac7510b8bfbf9d655dcf3935a24da603dbc9d3e00f0095fc36af7b"
POST_PROGRAM_SHA256 = "0ec642e8e7fbcdedd06c8d679934b4194a290f70d3435ab08ea07fede4ff943a"

PRE_CATALOG = {
    "state": "PRE",
    "count": 6835,
    "sha256": "4da29322e70ac8a981e42a5b7ed4172d32225b44c85d5748de86b990933aa51e",
    "usageSha256": "562337a3570a06b6b0b7a9379409ce5fbbc74d4e64f3c53001d8a3fb37c566fe",
}
POST_CATALOG = {
    "state": "POST",
    "count": 6848,
    "sha256": "c6e13eb5f7ed6e821071646e5dc67a7f53b9d701e06eb13bb17af89d1a5ad4b1",
    "usageSha256": "67b98d47488603671eb54a0f99715b0f4d368ae9446e73366ac39478bd5d9343",
}
PROGRAM_IDENTITY = {
    "name": "BEA.exe",
    "executableMd5": "3b456964020070efe696d2cc09464a55",
    "executableSha256": "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
    "imageBase": "0x00400000",
    "language": "x86:LE:32:default",
    "compilerSpec": "windows",
    "memorySha256": "5398f750f1ffb59873a6ec7e1750b51d11b5b844a8fda8d4e43649b5b9e5089d",
    "functions": 8124,
    "instructions": 549872,
}
EXPECTED_PROGRAM_DELTA = {
    "comments": ("9091", "9092"),
    "commentsSha256": (
        "a2df1fbae136f89b9f8426d23949bb1e408ea0ad933c434b4328f80980ecb13d",
        "3646a3baf134da9061c4c5b78f19583eb975f99cb357cb6981b5dd49dcd9bf8f",
    ),
}

TIMESTAMP_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\.[0-9]{6,9}Z")
REVIEW_BEGIN = "BEGIN_TARGET_LOCK_REVIEW_JSON"
REVIEW_END = "END_TARGET_LOCK_REVIEW_JSON"
REVIEW_CONFIG = {
    "codex": {
        "provider": "codex-subagent",
        "model": "gpt-5.6-sol",
        "reasoning": "inherited",
        "launcher": "codex-collaboration-subagent",
    },
    "grok": {
        "provider": "grok-4.5-high",
        "model": "grok-4.5",
        "reasoning": "high",
        "launcher": "grok-headless-cli",
    },
    "opus-medium": {
        "provider": "claude-opus-5-medium",
        "model": "claude-opus-5",
        "reasoning": "medium",
        "launcher": "claude-code-headless-cli",
    },
    "opus-max": {
        "provider": "claude-opus-5-max",
        "model": "claude-opus-5",
        "reasoning": "max",
        "launcher": "claude-code-headless-cli",
    },
}

PLAN_HEADER = (
    "address", "expected_body_min", "expected_body_max", "expected_body_bytes",
    "expected_body_digest", "expected_body_bytes_sha256", "expected_instruction_count",
    "expected_name", "expected_namespace", "expected_name_source",
    "expected_signature_source", "expected_signature_sha256",
    "expected_prototype_key_base64", "expected_local_variables_key_base64",
    "expected_local_variables_sha256", "expected_call_fixup_present",
    "expected_call_fixup_length", "expected_call_fixup_sha256", "expected_frame_size",
    "expected_local_size", "expected_parameter_size", "expected_parameter_offset",
    "expected_return_address_offset", "expected_comment_present",
    "expected_comment_length", "expected_comment_sha256",
    "expected_repeatable_comment_present", "expected_repeatable_comment_length",
    "expected_repeatable_comment_sha256", "expected_tags", "expected_tags_sha256",
    "expected_tag_catalog_count", "expected_tag_catalog_sha256",
    "expected_tag_usage_sha256", "allowed_new_tags", "proposed_tag_catalog_count",
    "proposed_tag_catalog_sha256", "proposed_tag_usage_sha256", "proposed_name",
    "proposed_calling_convention", "proposed_return_type", "proposed_parameters",
    "proposed_signature", "proposed_comment", "proposed_prototype_key_base64",
    "proposed_comment_length", "proposed_tags",
)
EVIDENCE_HEADER = (
    "address", "evidence_role", "artifact_path", "artifact_bytes",
    "artifact_sha256", "claim_boundary",
)
OBSERVATION_HEADER = (
    "address", "mode", "state", "status", "name", "namespace", "name_source",
    "signature_source", "signature_sha256", "prototype_key_base64",
    "local_variables_key_base64", "local_variables_sha256", "call_fixup_present",
    "call_fixup_length", "call_fixup_sha256", "frame_size", "local_size",
    "parameter_size", "parameter_offset", "return_address_offset", "comment_present",
    "comment_length", "comment_sha256", "repeatable_comment_present",
    "repeatable_comment_length", "repeatable_comment_sha256", "tags", "tags_sha256",
    "body_min", "body_max", "body_bytes", "body_digest", "body_bytes_sha256",
    "instruction_count",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProofError(message)


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n").encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def json_exact(actual: object, expected: object) -> bool:
    """Compare JSON-domain values without Python's ``True == 1`` coercion."""
    return canonical_json(actual) == canonical_json(expected)


def strict_tsv(path: Path, header: Sequence[str]) -> list[dict[str, str]]:
    raw = common.require_plain_file(path, "TSV").read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProofError(f"TSV is not UTF-8: {path}") from exc
    require(text.encode("utf-8") == raw, f"TSV is not canonical UTF-8: {path}")
    require("\r" not in text and text.endswith("\n"), f"TSV line endings differ: {path}")
    require("\n\n" not in text, f"TSV contains a blank row: {path}")
    reader = csv.DictReader(io.StringIO(text, newline=""), delimiter="\t")
    require(tuple(reader.fieldnames or ()) == tuple(header), f"TSV header differs: {path}")
    rows = [dict(row) for row in reader]
    require(all(set(row) == set(header) and None not in row for row in rows), f"TSV rows differ: {path}")
    return rows


def relative_path(path: Path, root: Path) -> str:
    path = common.require_plain_file(path, "artifact").resolve()
    try:
        return path.relative_to(root.resolve()).as_posix()
    except ValueError as exc:
        raise ProofError(f"artifact escapes repository: {path}") from exc


class ArtifactGraph:
    def __init__(self, repository: Path) -> None:
        self.repository = repository.resolve()
        self._items: dict[str, dict[str, object]] = {}

    def add(self, role: str, path: Path) -> dict[str, object]:
        relative = relative_path(path, self.repository)
        stamp = {
            "path": relative,
            "bytes": path.stat().st_size,
            "sha256": common.sha256_file(path),
        }
        item = self._items.get(relative)
        if item is None:
            item = {**stamp, "roles": [role]}
            self._items[relative] = item
        else:
            require(
                item["bytes"] == stamp["bytes"] and item["sha256"] == stamp["sha256"],
                f"artifact stamp changed while building core: {relative}",
            )
            roles = item["roles"]
            require(isinstance(roles, list), f"artifact roles malformed: {relative}")
            if role not in roles:
                roles.append(role)
                roles.sort()
        return stamp

    def items(self) -> list[dict[str, object]]:
        return [self._items[key] for key in sorted(self._items)]


def validate_plan(path: Path) -> list[dict[str, str]]:
    require(common.sha256_file(path) == PLAN_SHA256, "target-lock plan SHA-256 differs")
    rows = strict_tsv(path, PLAN_HEADER)
    require(tuple(row["address"] for row in rows) == ADDRESSES, "target-lock plan address order differs")
    require(len({row["address"] for row in rows}) == len(ADDRESSES), "target-lock plan addresses repeat")
    for row in rows:
        address = row["address"]
        require(row["proposed_name"] == PROPOSED_NAMES[address], f"proposed name differs at {address}")
        require(row["expected_tag_catalog_count"] == str(PRE_CATALOG["count"]), f"PRE tag count differs at {address}")
        require(row["expected_tag_catalog_sha256"] == PRE_CATALOG["sha256"], f"PRE tag digest differs at {address}")
        require(row["expected_tag_usage_sha256"] == PRE_CATALOG["usageSha256"], f"PRE tag use differs at {address}")
        require(row["proposed_tag_catalog_count"] == str(POST_CATALOG["count"]), f"POST tag count differs at {address}")
        require(row["proposed_tag_catalog_sha256"] == POST_CATALOG["sha256"], f"POST tag digest differs at {address}")
        require(row["proposed_tag_usage_sha256"] == POST_CATALOG["usageSha256"], f"POST tag use differs at {address}")
        require(
            int(row["proposed_comment_length"]) == len(row["proposed_comment"]),
            f"proposed comment length differs at {address}",
        )
    return rows


def validate_evidence(path: Path, repository: Path, graph: ArtifactGraph) -> list[dict[str, str]]:
    require(common.sha256_file(path) == EVIDENCE_SHA256, "target-lock evidence SHA-256 differs")
    rows = strict_tsv(path, EVIDENCE_HEADER)
    require(len(rows) == 96, "target-lock evidence row count differs")
    rendered = ["\t".join(row[column] for column in EVIDENCE_HEADER) for row in rows]
    require(rendered == sorted(rendered), "target-lock evidence row order differs")
    keys: set[tuple[str, str, str]] = set()
    covered: set[str] = set()
    artifacts: dict[str, tuple[int, str]] = {}
    current_lockhit = 0
    for row in rows:
        address = row["address"]
        require(address == "GLOBAL" or address in ADDRESSES, f"unknown evidence address: {address}")
        covered.add(address)
        key = (address, row["evidence_role"], row["artifact_path"])
        require(key not in keys, f"duplicate evidence key: {key}")
        keys.add(key)
        require(re.fullmatch(r"[a-z0-9][a-z0-9_-]*", row["evidence_role"]) is not None, "evidence role differs")
        relative = row["artifact_path"]
        require("\\" not in relative and not relative.startswith("/") and ":" not in relative, f"evidence path differs: {relative}")
        require("//" not in relative and "/../" not in f"/{relative}/", f"evidence path traversal: {relative}")
        require("ttd-data-writes-level521-lock-state-20260803-v1" not in relative, "historical LockHit authority admitted")
        artifact = (repository / Path(relative)).resolve()
        require(relative_path(artifact, repository) == relative, f"evidence path is not canonical: {relative}")
        expected = (int(row["artifact_bytes"]), row["artifact_sha256"])
        actual = (artifact.stat().st_size, common.sha256_file(artifact))
        require(actual == expected, f"evidence artifact differs: {relative}")
        require(artifacts.get(relative, expected) == expected, f"evidence artifact stamp conflicts: {relative}")
        artifacts[relative] = expected
        graph.add(f"semantic-evidence:{row['evidence_role']}", artifact)
        if address == "0x00407140" and "run-e-v3-source-bound/" in relative:
            current_lockhit += 1
    require(covered == {*ADDRESSES, "GLOBAL"}, "evidence address coverage differs")
    require(len(artifacts) == 27 and current_lockhit == 8, "evidence artifact/current-LockHit counts differ")
    return rows


def _reject_duplicate_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise ProofError(f"JSON contains a duplicate key: {key}")
        value[key] = item
    return value


def _reject_nonfinite(value: str) -> object:
    raise ProofError(f"JSON contains a non-finite number: {value}")


def read_json(path: Path, label: str, *, canonical: bool = False) -> dict[str, object]:
    path = common.require_plain_file(path, label)
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_nonfinite,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProofError(f"{label} is not strict UTF-8 JSON: {path}") from exc
    require(isinstance(value, dict), f"{label} is not a JSON object: {path}")
    if canonical:
        require(raw == canonical_json(value), f"{label} is not canonical JSON: {path}")
    return value


def parse_timestamp(value: object, label: str) -> datetime:
    require(isinstance(value, str) and TIMESTAMP_RE.fullmatch(value) is not None, f"{label} differs")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ProofError(f"{label} is not a real UTC timestamp") from exc
    require(parsed.tzinfo is not None and parsed.utcoffset() == timezone.utc.utcoffset(parsed), f"{label} is not UTC")
    return parsed


def validate_observations(path: Path, mode: str) -> list[dict[str, str]]:
    rows = strict_tsv(path, OBSERVATION_HEADER)
    require(tuple(row["address"] for row in rows) == ADDRESSES, f"{mode} observation addresses differ")
    expected_state = "PRE" if mode == "dry" else "POST"
    expected_status = {
        "dry": "validated_preimage",
        "apply": "applied_commit_requested",
        "readback": "verified_loaded_postimage",
    }[mode]
    for row in rows:
        require(row["mode"] == mode and row["state"] == expected_state, f"{mode} observation mode/state differs")
        require(row["status"] == expected_status, f"{mode} observation status differs")
    return rows


def normalized_observations(rows: Sequence[Mapping[str, str]]) -> list[dict[str, str]]:
    return [{key: value for key, value in row.items() if key not in {"mode", "status"}} for row in rows]


def validate_java_ready(
    ready_path: Path,
    output_path: Path,
    *,
    mode: str,
    semantic_tool: Path,
    plan: Path,
    evidence: Path,
) -> dict[str, object]:
    ready = read_json(ready_path, f"{mode} Java READY")
    require(set(ready) == {
        "schemaVersion", "completedAtUtc", "mode", "tool", "plan",
        "evidenceManifest", "program", "output", "catalog", "commitRequested",
        "rollbackRequested", "transactionEndReturnedCommitted", "loadedStateVerified",
        "reopenVerificationRequired", "semanticCandidateCohort",
        "semanticNamesAuthorized", "authorityBoundary",
    }, f"{mode} Java READY fields differ")
    require(ready.get("schemaVersion") == JAVA_SCHEMA and ready.get("mode") == mode, f"{mode} Java schema differs")
    parse_timestamp(ready.get("completedAtUtc"), f"{mode} Java timestamp")
    require(json_exact(ready.get("program"), PROGRAM_IDENTITY), f"{mode} Java program identity differs")
    expected_tool = common.external_stamp(semantic_tool)
    require(json_exact(ready.get("tool"), expected_tool), f"{mode} Java tool identity differs")
    require(
        json_exact(ready.get("plan"), {**common.external_stamp(plan), "targets": 5}),
        f"{mode} Java plan identity differs",
    )
    require(
        json_exact(ready.get("evidenceManifest"), {**common.external_stamp(evidence), "rows": 96}),
        f"{mode} Java evidence identity differs",
    )
    require(json_exact(ready.get("output"), common.external_stamp(output_path)), f"{mode} Java output identity differs")
    expected_catalog = PRE_CATALOG if mode == "dry" else POST_CATALOG
    require(json_exact(ready.get("catalog"), expected_catalog), f"{mode} Java catalog differs")
    flags = {
        "dry": (False, False, False, False, False),
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
    require(all(type(value) is bool for value in actual_flags), f"{mode} Java transaction/readback flag types differ")
    require(actual_flags == flags, f"{mode} Java transaction/readback flags differ")
    require(ready.get("semanticCandidateCohort") is True, f"{mode} Java semantic-candidate flag differs")
    require(ready.get("semanticNamesAuthorized") is False, f"{mode} Java issued false semantic authority")
    boundary = {
        "dry": "validated_exact_five_function_preimage_no_mutation",
        "apply": "provisional_until_separate_reopen_inventory_and_refutation",
        "readback": "loaded_exact_five_function_postimage",
    }[mode]
    require(ready.get("authorityBoundary") == boundary, f"{mode} Java authority boundary differs")
    return ready


def require_success_log(path: Path, mode: str, semantic_tool: Path) -> None:
    text = common.require_plain_file(path, f"{mode} application log").read_text(encoding="utf-8")
    require("REPORT SCRIPT ERROR" not in text, f"{mode} success log contains a script error")
    identity = (
        f"TARGET_LOCK_TOOL_OK schema={JAVA_SCHEMA} path={semantic_tool.resolve()} "
        f"bytes={semantic_tool.stat().st_size} sha256={SEMANTIC_TOOL_SHA256}"
    )
    require(text.count(identity) == 1, f"{mode} success log tool identity differs")
    marker = {
        "dry": "TARGET_LOCK_DRY_COMPLETE rows=5 mutations=0",
        "apply": "TARGET_LOCK_APPLY_COMPLETE rows=5 reopen_verification_required=true publication=BEGIN",
        "readback": "TARGET_LOCK_READBACK_COMPLETE rows=5",
    }[mode]
    require(text.count(marker) == 1, f"{mode} success marker differs")
    require("unexpected_final_commit=true" not in text and "persistence_tainted=true" not in text, f"{mode} persistence taint present")


def validate_success_run(
    run_root: Path,
    *,
    mode: str,
    output_hash: str,
    semantic_tool: Path,
    plan: Path,
    evidence: Path,
    graph: ArtifactGraph,
) -> tuple[list[dict[str, str]], dict[str, object]]:
    output = run_root / "observations.tsv"
    ready = run_root / "observations.ready.json"
    log = run_root / "application.log"
    require(common.sha256_file(output) == output_hash, f"{run_root.name} output SHA-256 differs")
    rows = validate_observations(output, mode)
    java = validate_java_ready(
        ready,
        output,
        mode=mode,
        semantic_tool=semantic_tool,
        plan=plan,
        evidence=evidence,
    )
    require_success_log(log, mode, semantic_tool)
    for file in run_root.iterdir():
        if file.is_file():
            graph.add(f"run:{run_root.name}", file)
    return rows, java


def require_rejection(
    run_root: Path,
    *,
    needles: Sequence[str],
    forbidden: Sequence[str] = (),
    graph: ArtifactGraph,
) -> None:
    log = run_root / "application.log"
    text = common.require_plain_file(log, "rejection application log").read_text(encoding="utf-8")
    require(text.count("REPORT SCRIPT ERROR") == 1, f"{run_root.name} script-error count differs")
    for needle in needles:
        require(text.count(needle) == 1, f"{run_root.name} rejection marker differs: {needle}")
    for marker in (*forbidden, "TARGET_LOCK_APPLY_COMPLETE", "TARGET_LOCK_READBACK_COMPLETE"):
        require(marker not in text, f"{run_root.name} contains forbidden success: {marker}")
    for name in ("observations.tsv", "observations.ready.json"):
        require(not (run_root / name).exists(), f"{run_root.name} published {name} on rejection")
    require(not list(run_root.glob(".*.partial-*")), f"{run_root.name} retained publication partials")
    for file in run_root.iterdir():
        if file.is_file():
            graph.add(f"rejection:{run_root.name}", file)


def validate_inventory_pair(functions: Path, program: Path, expected_functions: str, expected_program: str) -> None:
    require(common.sha256_file(functions) == expected_functions, f"function inventory differs: {functions}")
    require(common.sha256_file(program) == expected_program, f"program inventory differs: {program}")
    header, rows = common.function_rows(functions)
    require(len(rows) == 8124 and tuple(rows) == tuple(sorted(rows)), f"function inventory shape differs: {functions}")
    metrics = common.program_metrics(program)
    for key, expected in (
        ("programName", "BEA.exe"),
        ("executableMD5", PROGRAM_IDENTITY["executableMd5"]),
        ("executableSHA256", PROGRAM_IDENTITY["executableSha256"]),
        ("imageBase", PROGRAM_IDENTITY["imageBase"]),
        ("language", PROGRAM_IDENTITY["language"]),
        ("compilerSpec", PROGRAM_IDENTITY["compilerSpec"]),
        ("memorySha256", PROGRAM_IDENTITY["memorySha256"]),
        ("functions", "8124"),
        ("instructions", "549872"),
    ):
        require(metrics.get(key) == expected, f"program inventory identity differs: {program} {key}")
    require("address" in header, f"function inventory header differs: {functions}")


def validate_inventory_delta(
    pre_functions: Path,
    pre_program: Path,
    post_functions: Path,
    post_program: Path,
    plan_rows: Sequence[Mapping[str, str]],
) -> dict[str, object]:
    pre_header, before = common.function_rows(pre_functions)
    post_header, after = common.function_rows(post_functions)
    require(pre_header == post_header and tuple(before) == tuple(after), "PRE/POST function inventory keys differ")
    changed = [address for address in before if before[address] != after[address]]
    require(tuple(changed) == ADDRESSES, f"function inventory changed outside cohort: {changed}")
    critical_unchanged = {
        "bodyBytes", "bodyMin", "bodyMax", "bodyRanges", "bodyDigest", "instrCount",
        "isThunk", "thunkTarget", "isExternal", "customStorage", "inline", "noReturn",
        "frameSize", "localSize", "paramSize", "repeatableCommentPresent",
        "repeatableCommentLen", "repeatableCommentSha256",
    }
    plan = {row["address"]: row for row in plan_rows}
    for address in ADDRESSES:
        old = before[address]
        new = after[address]
        row = plan[address]
        require(all(old[field] == new[field] for field in critical_unchanged), f"critical target metadata drifted at {address}")
        require(new["name"] == row["proposed_name"], f"POST name differs at {address}")
        require(new["signature"] == row["proposed_signature"], f"POST signature differs at {address}")
        require(new["signatureSha256"] == sha256_bytes(row["proposed_signature"].encode()), f"POST signature hash differs at {address}")
        require(new["commentLen"] == row["proposed_comment_length"], f"POST comment length differs at {address}")
        require(new["commentSha256"] == sha256_bytes(row["proposed_comment"].encode()), f"POST comment hash differs at {address}")
        require(new["tags"] == row["proposed_tags"], f"POST tags differ at {address}")
    pre_metrics = common.program_metrics(pre_program)
    post_metrics = common.program_metrics(post_program)
    require(set(pre_metrics) == set(post_metrics), "PRE/POST program metric keys differ")
    delta = {key: (pre_metrics[key], post_metrics[key]) for key in pre_metrics if pre_metrics[key] != post_metrics[key]}
    require(delta == EXPECTED_PROGRAM_DELTA, f"program inventory delta differs: {delta}")
    return {"changedFunctions": changed, "programDelta": {key: list(value) for key, value in delta.items()}}


def is_reparse(path: Path) -> bool:
    info = path.lstat()
    attributes = getattr(info, "st_file_attributes", 0)
    flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    return path.is_symlink() or bool(attributes & flag) or getattr(path, "is_junction", lambda: False)()


def project_files(project: Path) -> list[Path]:
    project = common.require_plain_directory(project, "retained Ghidra project")
    roots = (project / "BEA.gpr", project / "BEA.rep")
    require(roots[0].is_file() and roots[1].is_dir(), f"Ghidra project pair is incomplete: {project}")
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
            continue
        for current, directories, names in os.walk(root):
            current_path = Path(current)
            require(not is_reparse(current_path), f"project directory is redirected: {current_path}")
            for name in directories:
                require(not is_reparse(current_path / name), f"project directory is redirected: {current_path / name}")
            for name in names:
                path = current_path / name
                require(path.is_file() and not is_reparse(path), f"project file is redirected: {path}")
                require(path.stat().st_nlink == 1, f"project file is hardlinked: {path}")
                files.append(path)
    return sorted(files, key=lambda path: path.relative_to(project).as_posix())


def project_stamp(project: Path, repository: Path, graph: ArtifactGraph, role: str) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    digest = hashlib.sha256()
    for path in project_files(project):
        relative = path.relative_to(project).as_posix()
        stamp = graph.add(role, path)
        row = {"path": relative, "bytes": stamp["bytes"], "sha256": stamp["sha256"]}
        rows.append(row)
        digest.update(canonical_json(row))
    return {
        "root": project.resolve().relative_to(repository.resolve()).as_posix(),
        "fileCount": len(rows),
        "totalBytes": sum(int(row["bytes"]) for row in rows),
        "filesSha256": digest.hexdigest(),
        "files": rows,
    }


def backup_files(manifest: Mapping[str, object], key: str) -> list[dict[str, object]]:
    value = manifest.get(key)
    require(isinstance(value, dict), f"backup manifest {key} differs")
    files = value.get("files")
    require(isinstance(files, list), f"backup manifest {key}.files differs")
    result: list[dict[str, object]] = []
    for item in files:
        require(isinstance(item, dict), f"backup manifest {key} row differs")
        result.append({
            "path": item.get("relative_path"),
            "bytes": item.get("size"),
            "sha256": item.get("sha256"),
        })
    return result


def validate_backup_manifest(path: Path, base_files: Sequence[Mapping[str, object]]) -> dict[str, object]:
    manifest = read_json(path, "scratch clone backup manifest")
    require(manifest.get("schemaVersion") == "onslaught-ghidra-project-backup.v2", "backup schema differs")
    require(manifest.get("sourceStable") is True, "backup source was not stable")
    comparison = manifest.get("copyComparison")
    require(isinstance(comparison, dict) and comparison.get("matches") is True, "backup copy comparison differs")
    require(backup_files(manifest, "source") == list(base_files), "backup source files differ from base")
    require(backup_files(manifest, "destination") == list(base_files), "backup destination files differ from base")
    return manifest


def add_run_files(graph: ArtifactGraph, run_root: Path, role: str) -> None:
    for path in sorted(run_root.iterdir()):
        if path.is_file():
            graph.add(role, path)


def assert_no_partials(root: Path) -> None:
    partials = [path for path in root.rglob("*") if path.is_file() and ".partial-" in path.name]
    require(not partials, f"publication partials survive: {[str(path) for path in partials]}")


def reconstruct_core(
    repository: Path,
    campaign: Path,
    output_root: Path,
    created_at: str,
) -> tuple[dict[str, object], list[dict[str, str]]]:
    repository = common.require_plain_directory(repository.resolve(), "repository")
    require(repository == Path(__file__).resolve().parents[1], "proof owner must run from its owning repository")
    campaign = common.require_plain_directory(campaign.resolve(), "target-lock campaign")
    require(campaign == default_campaign(repository), "target-lock campaign path differs")
    output_root = common.require_plain_directory(output_root.resolve(), "proof output root")
    require(output_root.parent == repository / "local-lab", "proof output must be one direct child of local-lab")
    parse_timestamp(created_at, "proof creation timestamp")

    graph = ArtifactGraph(repository)
    semantic_tool = repository / "tools/GhidraApplyTargetLockCorrections.java"
    inventory_tool = repository / "tools/ExportFullFunctionInventory.java"
    owner = Path(__file__).resolve()
    owner_tests = repository / "tools/ghidra_target_lock_semantic_proof_tests.py"
    helper = Path(common.__file__).resolve()
    backup_tool = repository / "tools/ghidra_project_backup.py"
    plan = campaign / "lock-five-semantic-plan-v3.candidate.tsv"
    evidence = campaign / "lock-five-semantic-evidence-v1.candidate.tsv"
    preregistration = campaign / "PREREGISTRATION.md"
    for role, path, digest in (
        ("semantic-tool", semantic_tool, SEMANTIC_TOOL_SHA256),
        ("inventory-tool", inventory_tool, INVENTORY_TOOL_SHA256),
        ("proof-owner", owner, common.sha256_file(owner)),
        ("proof-owner-tests", owner_tests, common.sha256_file(owner_tests)),
        ("proof-common-helper", helper, COMMON_HELPER_SHA256),
        ("backup-tool", backup_tool, common.sha256_file(backup_tool)),
        ("plan", plan, PLAN_SHA256),
        ("evidence-manifest", evidence, EVIDENCE_SHA256),
        ("preregistration", preregistration, common.sha256_file(preregistration)),
    ):
        require(common.sha256_file(path) == digest, f"{role} SHA-256 differs")
        graph.add(role, path)

    plan_rows = validate_plan(plan)
    evidence_rows = validate_evidence(evidence, repository, graph)
    runs = campaign / "scratch-proof/runs"

    successes: dict[str, dict[str, object]] = {}
    dry_names = (
        "hardening-v4-final-dry-r3",
        "hardening-v4-final-dry-r4",
        "hardening-v4-apply-a-dry",
        "hardening-v4-apply-b-dry",
    )
    dry_rows: list[list[dict[str, str]]] = []
    for name in dry_names:
        rows, ready = validate_success_run(
            runs / name,
            mode="dry",
            output_hash=DRY_OUTPUT_SHA256,
            semantic_tool=semantic_tool,
            plan=plan,
            evidence=evidence,
            graph=graph,
        )
        dry_rows.append(rows)
        successes[name] = {"mode": "dry", "readyAuthority": ready["authorityBoundary"]}
    require(all(rows == dry_rows[0] for rows in dry_rows[1:]), "replicated dry observations differ")

    apply_rows: dict[str, list[dict[str, str]]] = {}
    readback_rows: dict[str, list[dict[str, str]]] = {}
    for replica in ("a", "b"):
        apply_name = f"hardening-v4-apply-{replica}-apply"
        readback_name = f"hardening-v4-apply-{replica}-readback"
        apply, apply_ready = validate_success_run(
            runs / apply_name,
            mode="apply",
            output_hash=APPLY_OUTPUT_SHA256,
            semantic_tool=semantic_tool,
            plan=plan,
            evidence=evidence,
            graph=graph,
        )
        readback, readback_ready = validate_success_run(
            runs / readback_name,
            mode="readback",
            output_hash=READBACK_OUTPUT_SHA256,
            semantic_tool=semantic_tool,
            plan=plan,
            evidence=evidence,
            graph=graph,
        )
        require(normalized_observations(apply) == normalized_observations(readback), f"replica {replica} apply/readback differs")
        apply_rows[replica] = apply
        readback_rows[replica] = readback
        successes[apply_name] = {"mode": "apply", "readyAuthority": apply_ready["authorityBoundary"]}
        successes[readback_name] = {"mode": "readback", "readyAuthority": readback_ready["authorityBoundary"]}
    require(normalized_observations(apply_rows["a"]) == normalized_observations(apply_rows["b"]), "replica apply observations differ")
    require(normalized_observations(readback_rows["a"]) == normalized_observations(readback_rows["b"]), "replica readbacks differ")

    require_rejection(
        runs / "hardening-v4-row4-probe",
        needles=(
            "TARGET_LOCK_FORCED_ROW4_FAILURE rows_applied=4 rollback_requested=true",
            "TARGET_LOCK_TRANSACTION_END commit_requested=false returned_committed=false",
            "outer_rollback_requested=true unexpected_final_commit=false persistence_tainted=false",
            "intentional target-lock row-4 rollback probe",
        ),
        graph=graph,
    )
    require_rejection(
        runs / "hardening-v4-post-inner-probe",
        needles=(
            "TARGET_LOCK_TRANSACTION_END commit_requested=true returned_committed=false",
            "TARGET_LOCK_FORCED_POST_INNER_FAILURE rollback_requested=true",
            "outer_rollback_requested=true unexpected_final_commit=false persistence_tainted=false",
            "intentional target-lock post-inner rollback probe",
        ),
        graph=graph,
    )
    require_rejection(
        runs / "hardening-v4-poison-plan",
        needles=("mismatch at plan field=caller_sha256",),
        graph=graph,
    )
    require_rejection(
        runs / "hardening-v4-poison-evidence",
        needles=("mismatch at evidence field=caller_sha256",),
        graph=graph,
    )
    require_rejection(
        runs / "hardening-v4-pre-readback-rejection",
        needles=("mismatch at catalog field=count expected=6848 actual=6835",),
        graph=graph,
    )

    inventory_runs = {
        "row4-baseline": "hardening-v4-row4-baseline",
        "row4-reopen": "hardening-v4-row4-reopen",
        "post-inner-baseline": "hardening-v4-post-inner-baseline",
        "post-inner-reopen": "hardening-v4-post-inner-reopen",
        "rejection-base-reopen": "hardening-v4-base-reopen-after-rejections",
        "a-baseline": "hardening-v4-apply-a-baseline",
        "b-baseline": "hardening-v4-apply-b-baseline",
    }
    for role, name in inventory_runs.items():
        root = runs / name
        validate_inventory_pair(root / "functions.tsv", root / "program.tsv", PRE_FUNCTIONS_SHA256, PRE_PROGRAM_SHA256)
        add_run_files(graph, root, f"inventory:{role}")

    post_inventory: dict[str, dict[str, object]] = {}
    for replica in ("a", "b"):
        pre = runs / f"hardening-v4-apply-{replica}-baseline"
        post = runs / f"hardening-v4-apply-{replica}-post-inventory"
        validate_inventory_pair(post / "functions.tsv", post / "program.tsv", POST_FUNCTIONS_SHA256, POST_PROGRAM_SHA256)
        delta = validate_inventory_delta(
            pre / "functions.tsv",
            pre / "program.tsv",
            post / "functions.tsv",
            post / "program.tsv",
            plan_rows,
        )
        add_run_files(graph, post, f"inventory:{replica}-post")
        post_inventory[replica] = {
            "functions": graph.add(f"post-inventory:{replica}", post / "functions.tsv"),
            "program": graph.add(f"post-inventory:{replica}", post / "program.tsv"),
            "delta": delta,
        }
    require((runs / "hardening-v4-apply-a-post-inventory/functions.tsv").read_bytes() == (runs / "hardening-v4-apply-b-post-inventory/functions.tsv").read_bytes(), "replica POST function inventories differ")
    require((runs / "hardening-v4-apply-a-post-inventory/program.tsv").read_bytes() == (runs / "hardening-v4-apply-b-post-inventory/program.tsv").read_bytes(), "replica POST program inventories differ")

    assert_no_partials(runs)

    base_project = campaign / "scratch/replica-b"
    base_stamp = project_stamp(base_project, repository, graph, "retained-project:base")
    base_manifest_path = base_project / "backup_manifest.json"
    graph.add("base-project-copy-manifest", base_manifest_path)
    base_manifest = read_json(base_manifest_path, "base project backup manifest")
    base_files = backup_files(base_manifest, "destination")
    require(base_stamp["files"] == base_files, "current base project files differ from its verified copy")

    retained: dict[str, dict[str, object]] = {"base": base_stamp}
    clone_names = {
        "row4-control": "hardening-v4-row4",
        "post-inner-control": "hardening-v4-post-inner",
        "replica-a": "hardening-v4-apply-a",
        "replica-b": "hardening-v4-apply-b",
    }
    for role, name in clone_names.items():
        project = campaign / "scratch" / name
        manifest_path = project / "backup_manifest.json"
        validate_backup_manifest(manifest_path, base_files)
        graph.add(f"clone-manifest:{role}", manifest_path)
        retained[role] = project_stamp(project, repository, graph, f"retained-project:{role}")

    core = {
        "schema": CORE_SCHEMA,
        "status": "CORE_FROZEN_AWAITING_INDEPENDENT_REFUTER",
        "createdAtUtc": created_at,
        "repository": str(repository),
        "campaign": campaign.relative_to(repository).as_posix(),
        "proofRoot": output_root.relative_to(repository).as_posix(),
        "addresses": list(ADDRESSES),
        "proposedNames": PROPOSED_NAMES,
        "inputs": {
            "semanticToolSha256": SEMANTIC_TOOL_SHA256,
            "proofOwnerSha256": common.sha256_file(owner),
            "proofOwnerTestsSha256": common.sha256_file(owner_tests),
            "commonHelperSha256": COMMON_HELPER_SHA256,
            "planSha256": PLAN_SHA256,
            "evidenceSha256": EVIDENCE_SHA256,
            "evidenceRows": len(evidence_rows),
            "uniqueEvidenceArtifacts": 27,
        },
        "controls": {
            "wrongPlanHashRejected": True,
            "wrongEvidenceHashRejected": True,
            "preStateReadbackRejected": True,
            "row4RollbackReopenedExactPre": True,
            "postInnerRollbackReopenedExactPre": True,
            "rejectedPublicationPartials": 0,
        },
        "replication": {
            "dryOutputsSha256": DRY_OUTPUT_SHA256,
            "applyOutputsSha256": APPLY_OUTPUT_SHA256,
            "readbackOutputsSha256": READBACK_OUTPUT_SHA256,
            "preFunctionsSha256": PRE_FUNCTIONS_SHA256,
            "preProgramSha256": PRE_PROGRAM_SHA256,
            "postFunctionsSha256": POST_FUNCTIONS_SHA256,
            "postProgramSha256": POST_PROGRAM_SHA256,
            "replicaSemanticsExact": True,
            "replicaFullInventoriesExact": True,
            "changedFunctions": list(ADDRESSES),
            "programDelta": {key: list(value) for key, value in EXPECTED_PROGRAM_DELTA.items()},
        },
        "successRuns": successes,
        "postInventories": post_inventory,
        "retainedProjects": retained,
        "claims": {
            "scratchProofSurvived": True,
            "javaReceiptsRemainProvisional": True,
            "semanticNamesAuthorized": False,
            "liveMutationAuthorized": False,
            "independentSemanticRefuterRequired": True,
            "globalTargetLockParityProved": False,
            "staleOrGapCrossedReturnBacklinksAdmitted": False,
        },
        "artifacts": graph.items(),
    }
    return core, plan_rows


def expected_subject(
    repository: Path,
    core_path: Path,
    plan_rows: Sequence[Mapping[str, str]],
) -> dict[str, object]:
    core_hash = common.sha256_file(core_path)
    return {
        "schema": SUBJECT_SCHEMA,
        "status": "READY_FOR_INDEPENDENT_REFUTATION",
        "core": {
            "path": core_path.relative_to(repository).as_posix(),
            "bytes": core_path.stat().st_size,
            "sha256": core_hash,
        },
        "subjects": {
            "semanticToolSha256": SEMANTIC_TOOL_SHA256,
            "planSha256": PLAN_SHA256,
            "evidenceSha256": EVIDENCE_SHA256,
            "postFunctionsSha256": POST_FUNCTIONS_SHA256,
            "postProgramSha256": POST_PROGRAM_SHA256,
        },
        "decisionsRequired": [
            {
                "address": row["address"],
                "proposedName": row["proposed_name"],
                "proposedSignature": row["proposed_signature"],
                "proposedCommentSha256": sha256_bytes(row["proposed_comment"].encode()),
                "proposedTags": row["proposed_tags"],
            }
            for row in plan_rows
        ],
        "requiredWithholdings": {
            "staleOrGapCrossedReturnBacklinks": True,
            "globalTargetLockParity": True,
            "rebuildParity": True,
        },
        "coreVerified": True,
        "modelIdentityCryptographicallyAuthenticated": False,
    }


def build_core(repository: Path, campaign: Path, output_root: Path) -> tuple[Path, Path]:
    repository = common.require_plain_directory(repository.resolve(), "repository")
    output_root = common.require_plain_existing_ancestors(output_root.resolve(), "proof output root")
    require(output_root.parent == repository / "local-lab", "proof output must be one direct child of local-lab")
    require(not output_root.exists(), f"proof output root already exists: {output_root}")
    common.ensure_plain_directory(output_root, "proof output root")
    core, plan_rows = reconstruct_core(repository, campaign, output_root, common.utc_now())
    core_path = output_root / "proof.core.json"
    common.write_json_new(core_path, core)
    verified = verify_core(core_path)
    require(json_exact(verified, core), "newly frozen core did not verify exactly")
    subject = expected_subject(repository, core_path, plan_rows)
    subject_path = output_root / "refuter-subject.json"
    common.write_json_new(subject_path, subject)
    require(json_exact(validate_subject(subject_path, core_path), subject), "newly frozen subject did not verify exactly")
    return core_path, subject_path


def proof_context(core_path: Path) -> tuple[Path, Path, Path]:
    repository = common.require_plain_directory(Path(__file__).resolve().parents[1], "proof repository")
    core_path = common.require_plain_file(core_path.resolve(), "target-lock proof core")
    require(core_path.stat().st_nlink == 1, "target-lock proof core is hardlinked")
    require(core_path.name == "proof.core.json" and ":" not in core_path.name, "proof core filename differs")
    proof_root = common.require_plain_directory(core_path.parent, "target-lock proof root")
    require(":" not in proof_root.name, "target-lock proof root name differs")
    require(proof_root.parent == repository / "local-lab", "proof root must be one direct child of local-lab")
    require(core_path == proof_root / "proof.core.json", "proof core path differs")
    return repository, proof_root, core_path


def verify_core(core_path: Path) -> dict[str, object]:
    repository, proof_root, core_path = proof_context(core_path)
    core = read_json(core_path, "target-lock proof core", canonical=True)
    require(core.get("schema") == CORE_SCHEMA, "target-lock proof core schema differs")
    require(core.get("status") == "CORE_FROZEN_AWAITING_INDEPENDENT_REFUTER", "target-lock proof core status differs")
    created_at = core.get("createdAtUtc")
    parse_timestamp(created_at, "target-lock proof timestamp")
    require(isinstance(created_at, str), "target-lock proof timestamp differs")
    campaign = default_campaign(repository)
    expected, _ = reconstruct_core(repository, campaign, proof_root, created_at)
    require(json_exact(core, expected), "target-lock proof core differs from a full evidence reconstruction")
    return core


def validate_subject(subject_path: Path, core_path: Path) -> dict[str, object]:
    repository, proof_root, core_path = proof_context(core_path)
    subject_path = common.require_plain_file(subject_path.resolve(), "target-lock refuter subject")
    require(subject_path.stat().st_nlink == 1, "target-lock refuter subject is hardlinked")
    require(subject_path == proof_root / "refuter-subject.json", "refuter subject path differs")
    subject = read_json(subject_path, "target-lock refuter subject", canonical=True)
    verify_core(core_path)
    plan_rows = validate_plan(default_campaign(repository) / "lock-five-semantic-plan-v3.candidate.tsv")
    expected = expected_subject(repository, core_path, plan_rows)
    require(json_exact(subject, expected), "refuter subject differs from the complete expected subject")
    return subject


def proof_stamp(path: Path, proof_root: Path) -> dict[str, object]:
    path = common.require_plain_file(path.resolve(), "proof artifact")
    require(path.stat().st_nlink == 1, f"proof artifact is hardlinked: {path}")
    try:
        relative = path.relative_to(proof_root.resolve()).as_posix()
    except ValueError as exc:
        raise ProofError(f"proof artifact escapes proof root: {path}") from exc
    require(relative and "\\" not in relative and ":" not in relative, f"proof artifact path differs: {relative}")
    return {"path": relative, "bytes": path.stat().st_size, "sha256": common.sha256_file(path)}


def validate_proof_stamp(
    proof_root: Path,
    value: object,
    label: str,
    *,
    expected_relative: str | None = None,
) -> Path:
    require(isinstance(value, dict) and set(value) == {"path", "bytes", "sha256"}, f"{label} stamp differs")
    relative = value.get("path")
    require(isinstance(relative, str) and relative and "\\" not in relative and ":" not in relative and "\0" not in relative, f"{label} path differs")
    require(not relative.startswith("/") and "//" not in relative and "/../" not in f"/{relative}/", f"{label} path is unsafe")
    if expected_relative is not None:
        require(relative == expected_relative, f"{label} path differs")
    path = (proof_root / relative).resolve()
    require(path.is_relative_to(proof_root.resolve()), f"{label} escaped proof root")
    require(json_exact(proof_stamp(path, proof_root), value), f"{label} artifact differs")
    return path


def accepted_decisions(subject: Mapping[str, object]) -> list[dict[str, object]]:
    rows = subject.get("decisionsRequired")
    require(isinstance(rows, list), "subject decisions differ")
    result: list[dict[str, object]] = []
    for row in rows:
        require(isinstance(row, dict), "subject decision row differs")
        result.append({**row, "verdict": "ACCEPT"})
    return result


def global_refutation_boundary() -> dict[str, bool]:
    return {
        "staleOrGapCrossedReturnBacklinksRejected": True,
        "globalTargetLockParityWithheld": True,
        "rebuildParityWithheld": True,
    }


def expected_review_prompt(
    review_id: str,
    core_path: Path,
    subject_path: Path,
    subject: Mapping[str, object],
) -> bytes:
    require(review_id in REVIEW_CONFIG, f"unknown review id: {review_id}")
    config = REVIEW_CONFIG[review_id]
    template = {
        "schema": REVIEW_SCHEMA,
        "provider": config["provider"],
        "model": config["model"],
        "reasoning": config["reasoning"],
        "verdict": "ACCEPTED_EXACT_FIVE",
        "coreSha256": common.sha256_file(core_path),
        "subjectSha256": common.sha256_file(subject_path),
        "subjects": subject["subjects"],
        "decisions": accepted_decisions(subject),
        "global": global_refutation_boundary(),
        "assessment": "REPLACE_WITH_A_200_TO_40000_CHARACTER_EVIDENCE_BASED_ASSESSMENT_NAMING_ALL_FIVE_ADDRESSES_AND_NAMES",
        "modelIdentityCryptographicallyAuthenticated": False,
    }
    text = f"""# Battle Engine Aquila target-lock semantic refutation

You are the declared `{config['provider']}` read-only reviewer for an authorized preservation and reverse-engineering project. Do not modify files, launch Ghidra, run the game, or trust labels in the subject as proof. Read the exact frozen core, subject, plan, evidence manifest, source/disassembly receipts, scratch observations, and PRE/POST inventories they bind. Try to falsify every proposed name, full signature, comment boundary, and tag set—especially the corrected 32-bit retail BOOL/int return at 0x00407310.

Core: `{core_path}`
Core SHA-256: `{common.sha256_file(core_path)}`
Subject: `{subject_path}`
Subject SHA-256: `{common.sha256_file(subject_path)}`

Only emit `ACCEPTED_EXACT_FIVE` if all five complete decision rows survive. If any field does not survive, explain the rejection and do not emit the accepted marker payload. Preserve the three global withholdings. Your assessment must be substantive, must have no leading/trailing whitespace, and must explicitly name every address and proposed function name.

End your output with exactly one `{REVIEW_BEGIN}` line, the JSON object matching the template below, and exactly one `{REVIEW_END}` line. Replace only `assessment`; do not add, remove, or alter any other JSON field.

Exact subject:

```json
{canonical_json(subject).decode('utf-8').rstrip()}
```

Exact accepted-output template:

```json
{canonical_json(template).decode('utf-8').rstrip()}
```
"""
    return text.encode("utf-8")


def validate_prompt(
    review_id: str,
    path: Path,
    core_path: Path,
    subject_path: Path,
    subject: Mapping[str, object],
) -> None:
    path = common.require_plain_file(path, "review prompt")
    require(path.stat().st_nlink == 1, f"review prompt is hardlinked: {path}")
    require(
        path.read_bytes() == expected_review_prompt(review_id, core_path, subject_path, subject),
        f"{review_id} review prompt differs from the deterministic owner prompt",
    )


def review_executable(review_id: str) -> Path | None:
    if review_id == "grok":
        return Path.home() / ".grok/bin/grok.exe"
    if review_id in {"opus-medium", "opus-max"}:
        return Path.home() / ".local/bin/claude.exe"
    require(review_id == "codex", f"unknown review id: {review_id}")
    return None


def expected_review_command(
    review_id: str,
    repository: Path,
    prompt_path: Path,
    session_id: str,
) -> list[str]:
    if review_id == "codex":
        return ["codex-collaboration-subagent", session_id]
    executable = common.require_plain_file(review_executable(review_id), f"{review_id} executable")
    if review_id == "grok":
        return [
            str(executable), "--cwd", str(repository), "--model", "grok-4.5",
            "--reasoning-effort", "high", "--permission-mode", "dontAsk",
            "--tools", "Read,Glob,Grep",
            "--disable-web-search", "--no-memory", "--no-subagents",
            "--max-turns", "100", "--output-format", "plain",
            "--session-id", session_id, "--single", prompt_path.read_text(encoding="utf-8"),
        ]
    effort = "max" if review_id == "opus-max" else "medium"
    return [
        str(executable), "-p", "--input-format", "text", "--model", "claude-opus-5",
        "--effort", effort, "--output-format", "text", "--permission-mode", "plan",
        "--no-session-persistence", "--no-chrome", "--session-id", session_id,
        "--name", f"Target-lock exact semantic refuter ({effort})",
    ]


def parse_review_output(
    stdout_path: Path,
    config: Mapping[str, str],
    core_path: Path,
    subject_path: Path,
    subject: Mapping[str, object],
) -> dict[str, object]:
    raw = common.require_plain_file(stdout_path, "review stdout").read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProofError(f"review stdout is not UTF-8: {stdout_path}") from exc
    require(text.count(REVIEW_BEGIN) == 1 and text.count(REVIEW_END) == 1, "review decision markers differ")
    begin = text.index(REVIEW_BEGIN) + len(REVIEW_BEGIN)
    end = text.index(REVIEW_END)
    require(begin < end, "review decision marker order differs")
    payload_text = text[begin:end].strip()
    try:
        payload = json.loads(
            payload_text,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_nonfinite,
        )
    except json.JSONDecodeError as exc:
        raise ProofError(f"review decision payload is not strict JSON: {stdout_path}") from exc
    require(isinstance(payload, dict), "review decision payload is not an object")
    require(set(payload) == {
        "schema", "provider", "model", "reasoning", "verdict", "coreSha256",
        "subjectSha256", "subjects", "decisions", "global", "assessment",
        "modelIdentityCryptographicallyAuthenticated",
    }, "review decision fields differ")
    require(payload.get("schema") == REVIEW_SCHEMA, "review decision schema differs")
    for key in ("provider", "model", "reasoning"):
        require(payload.get(key) == config[key], f"review decision {key} differs")
    require(payload.get("verdict") == "ACCEPTED_EXACT_FIVE", "review did not accept the exact cohort")
    require(payload.get("coreSha256") == common.sha256_file(core_path), "review core binding differs")
    require(payload.get("subjectSha256") == common.sha256_file(subject_path), "review subject binding differs")
    require(json_exact(payload.get("subjects"), subject["subjects"]), "review subject hashes differ")
    require(json_exact(payload.get("decisions"), accepted_decisions(subject)), "review decisions differ from the full subject")
    require(json_exact(payload.get("global"), global_refutation_boundary()), "review global boundary differs")
    assessment = payload.get("assessment")
    require(
        isinstance(assessment, str)
        and assessment == assessment.strip()
        and 200 <= len(assessment) <= 40000,
        "review assessment length/whitespace differs",
    )
    for address, name in PROPOSED_NAMES.items():
        require(address in assessment and name in assessment, f"review assessment omitted {address}/{name}")
    require(payload.get("modelIdentityCryptographicallyAuthenticated") is False, "review falsely claims cryptographic model authentication")
    return payload


def validate_review_run(
    review_id: str,
    proof_root: Path,
    core_path: Path,
    subject_path: Path,
    subject: Mapping[str, object],
) -> dict[str, object]:
    require(review_id in REVIEW_CONFIG, f"unknown review id: {review_id}")
    config = REVIEW_CONFIG[review_id]
    review_root = common.require_plain_directory(proof_root / "reviews" / review_id, f"{review_id} review root")
    require(review_root.parent == proof_root / "reviews", f"{review_id} review root differs")
    expected_files = {"prompt.md", "stdout.txt", "stderr.txt", "run.json"}
    entries = list(review_root.iterdir())
    require({path.name for path in entries} == expected_files, f"{review_id} review artifact set differs")
    require(all(path.is_file() and not is_reparse(path) for path in entries), f"{review_id} review contains a non-plain entry")
    prompt = review_root / "prompt.md"
    stdout = review_root / "stdout.txt"
    stderr = review_root / "stderr.txt"
    run_path = review_root / "run.json"
    validate_prompt(review_id, prompt, core_path, subject_path, subject)
    try:
        common.require_plain_file(stderr, f"{review_id} stderr").read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProofError(f"{review_id} stderr is not UTF-8") from exc
    decision = parse_review_output(stdout, config, core_path, subject_path, subject)
    run = read_json(run_path, f"{review_id} review run", canonical=True)
    require(set(run) == {
        "schema", "provider", "model", "reasoning", "launcher", "sessionId",
        "startedAtUtc", "completedAtUtc", "exitCode", "workingDirectory", "readOnly",
        "command", "executable", "promptTransport", "prompt", "stdout", "stderr",
    }, f"{review_id} review run fields differ")
    require(run.get("schema") == REVIEW_RUN_SCHEMA, f"{review_id} review run schema differs")
    for key in ("provider", "model", "reasoning", "launcher"):
        require(run.get(key) == config[key], f"{review_id} review run {key} differs")
    session_id = run.get("sessionId")
    require(isinstance(session_id, str), f"{review_id} session id differs")
    try:
        uuid.UUID(session_id)
    except (ValueError, AttributeError) as exc:
        raise ProofError(f"{review_id} session id is not a UUID") from exc
    started = parse_timestamp(run.get("startedAtUtc"), f"{review_id} startedAtUtc")
    completed = parse_timestamp(run.get("completedAtUtc"), f"{review_id} completedAtUtc")
    core_created = parse_timestamp(read_json(core_path, "review-bound core", canonical=True).get("createdAtUtc"), "review-bound core timestamp")
    require(core_created <= started <= completed, f"{review_id} review timestamps are impossible")
    require(type(run.get("exitCode")) is int and run.get("exitCode") == 0, f"{review_id} exit code differs")
    require(run.get("readOnly") is True, f"{review_id} did not close as a read-only success")
    repository = Path(__file__).resolve().parents[1]
    require(run.get("workingDirectory") == str(repository), f"{review_id} working directory differs")
    command = run.get("command")
    require(json_exact(command, expected_review_command(review_id, repository, prompt, session_id)), f"{review_id} command differs")
    executable = review_executable(review_id)
    if executable is None:
        require(run.get("executable") is None and run.get("promptTransport") == "collaboration-message", f"{review_id} launcher evidence differs")
    else:
        require(json_exact(run.get("executable"), common.external_stamp(executable)), f"{review_id} executable differs")
        transport = "argv" if review_id == "grok" else "stdin"
        require(run.get("promptTransport") == transport, f"{review_id} prompt transport differs")
    prefix = f"reviews/{review_id}"
    require(validate_proof_stamp(proof_root, run.get("prompt"), f"{review_id} prompt", expected_relative=f"{prefix}/prompt.md") == prompt, f"{review_id} prompt path differs")
    require(validate_proof_stamp(proof_root, run.get("stdout"), f"{review_id} stdout", expected_relative=f"{prefix}/stdout.txt") == stdout, f"{review_id} stdout path differs")
    require(validate_proof_stamp(proof_root, run.get("stderr"), f"{review_id} stderr", expected_relative=f"{prefix}/stderr.txt") == stderr, f"{review_id} stderr path differs")
    return {"run": run, "runPath": run_path, "decision": decision}


def prepare_reviews(core_path: Path, subject_path: Path) -> Path:
    _, proof_root, core_path = proof_context(core_path)
    subject = validate_subject(subject_path, core_path)
    reviews_root = proof_root / "reviews"
    require(not reviews_root.exists(), "reviews root already exists")
    common.ensure_plain_directory(reviews_root, "reviews root")
    for review_id in REVIEW_CONFIG:
        review_root = reviews_root / review_id
        common.ensure_plain_directory(review_root, f"{review_id} review root")
        common.write_new(
            review_root / "prompt.md",
            expected_review_prompt(review_id, core_path, subject_path.resolve(), subject),
        )
        validate_prompt(review_id, review_root / "prompt.md", core_path, subject_path.resolve(), subject)
    return reviews_root


def review_run_payload(
    review_id: str,
    proof_root: Path,
    prompt: Path,
    stdout: Path,
    stderr: Path,
    session_id: str,
    started_at: str,
    completed_at: str,
) -> dict[str, object]:
    repository = Path(__file__).resolve().parents[1]
    config = REVIEW_CONFIG[review_id]
    executable = review_executable(review_id)
    return {
        "schema": REVIEW_RUN_SCHEMA,
        "provider": config["provider"],
        "model": config["model"],
        "reasoning": config["reasoning"],
        "launcher": config["launcher"],
        "sessionId": session_id,
        "startedAtUtc": started_at,
        "completedAtUtc": completed_at,
        "exitCode": 0,
        "workingDirectory": str(repository),
        "readOnly": True,
        "command": expected_review_command(review_id, repository, prompt, session_id),
        "executable": None if executable is None else common.external_stamp(executable),
        "promptTransport": "collaboration-message" if review_id == "codex" else ("argv" if review_id == "grok" else "stdin"),
        "prompt": proof_stamp(prompt, proof_root),
        "stdout": proof_stamp(stdout, proof_root),
        "stderr": proof_stamp(stderr, proof_root),
    }


def run_external_review(core_path: Path, subject_path: Path, review_id: str) -> Path:
    require(review_id in {"grok", "opus-medium", "opus-max"}, "run-review supports only external reviewers")
    repository, proof_root, core_path = proof_context(core_path)
    subject = validate_subject(subject_path, core_path)
    review_root = common.require_plain_directory(proof_root / "reviews" / review_id, f"{review_id} review root")
    prompt = common.require_plain_file(review_root / "prompt.md", f"{review_id} prompt")
    validate_prompt(review_id, prompt, core_path, subject_path.resolve(), subject)
    require({path.name for path in review_root.iterdir()} == {"prompt.md"}, f"{review_id} review already has run artifacts")
    session_id = str(uuid.uuid4())
    command = expected_review_command(review_id, repository, prompt, session_id)
    started_at = common.utc_now()
    try:
        process = subprocess.run(
            command,
            cwd=repository,
            input=prompt.read_bytes() if review_id.startswith("opus-") else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=7200,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise ProofError(f"{review_id} review exceeded the two-hour bound") from exc
    completed_at = common.utc_now()
    require(type(process.returncode) is int and process.returncode == 0, f"{review_id} exited {process.returncode}")
    try:
        process.stderr.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProofError(f"{review_id} stderr is not UTF-8") from exc
    with tempfile.TemporaryDirectory(prefix=f"bea-{review_id}-review-") as temporary:
        temporary_stdout = Path(temporary) / "stdout.txt"
        temporary_stdout.write_bytes(process.stdout)
        parse_review_output(temporary_stdout, REVIEW_CONFIG[review_id], core_path, subject_path.resolve(), subject)
    stdout = review_root / "stdout.txt"
    stderr = review_root / "stderr.txt"
    common.write_new(stdout, process.stdout)
    common.write_new(stderr, process.stderr)
    run_path = review_root / "run.json"
    common.write_json_new(
        run_path,
        review_run_payload(
            review_id, proof_root, prompt, stdout, stderr, session_id, started_at, completed_at,
        ),
    )
    validate_review_run(review_id, proof_root, core_path, subject_path.resolve(), subject)
    return run_path


def record_codex_review(
    core_path: Path,
    subject_path: Path,
    session_id: str,
    started_at: str,
    completed_at: str,
) -> Path:
    _, proof_root, core_path = proof_context(core_path)
    subject = validate_subject(subject_path, core_path)
    review_root = common.require_plain_directory(proof_root / "reviews/codex", "codex review root")
    prompt = common.require_plain_file(review_root / "prompt.md", "codex prompt")
    stdout = common.require_plain_file(review_root / "stdout.txt", "codex stdout")
    require({path.name for path in review_root.iterdir()} == {"prompt.md", "stdout.txt"}, "codex review has unexpected pre-seal artifacts")
    validate_prompt("codex", prompt, core_path, subject_path.resolve(), subject)
    parse_review_output(stdout, REVIEW_CONFIG["codex"], core_path, subject_path.resolve(), subject)
    stderr = review_root / "stderr.txt"
    common.write_new(stderr, b"")
    run_path = review_root / "run.json"
    common.write_json_new(
        run_path,
        review_run_payload(
            "codex", proof_root, prompt, stdout, stderr, session_id, started_at, completed_at,
        ),
    )
    validate_review_run("codex", proof_root, core_path, subject_path.resolve(), subject)
    return run_path


def expected_refuter(
    proof_root: Path,
    core_path: Path,
    subject_path: Path,
    subject: Mapping[str, object],
) -> dict[str, object]:
    reviews: list[dict[str, object]] = []
    session_ids: list[str] = []
    assessment_hashes: list[str] = []
    for review_id in REVIEW_CONFIG:
        result = validate_review_run(review_id, proof_root, core_path, subject_path, subject)
        config = REVIEW_CONFIG[review_id]
        session_ids.append(str(result["run"]["sessionId"]))
        assessment_hash = sha256_bytes(str(result["decision"]["assessment"]).encode("utf-8"))
        assessment_hashes.append(assessment_hash)
        reviews.append({
            "reviewId": review_id,
            "provider": config["provider"],
            "model": config["model"],
            "reasoning": config["reasoning"],
            "verdict": result["decision"]["verdict"],
            "run": proof_stamp(result["runPath"], proof_root),
            "decisionSha256": sha256_bytes(canonical_json(result["decision"])),
            "assessmentSha256": assessment_hash,
        })
    require(len(set(session_ids)) == len(REVIEW_CONFIG), "review session IDs are not distinct")
    require(len(set(assessment_hashes)) == len(REVIEW_CONFIG), "review assessments are not independent/distinct")
    return {
        "schema": REFUTER_SCHEMA,
        "status": "INDEPENDENT_REFUTATION_COMPLETE",
        "verdict": "ACCEPTED_EXACT_FIVE",
        "core": proof_stamp(core_path, proof_root),
        "subject": proof_stamp(subject_path, proof_root),
        "subjects": subject["subjects"],
        "decisions": accepted_decisions(subject),
        "global": global_refutation_boundary(),
        "reviews": reviews,
        "modelIdentityCryptographicallyAuthenticated": False,
        "liveMutationAuthorized": False,
    }


def build_refuter(core_path: Path, subject_path: Path, refuter_path: Path) -> Path:
    _, proof_root, core_path = proof_context(core_path)
    subject = validate_subject(subject_path, core_path)
    refuter_path = common.require_plain_existing_ancestors(refuter_path.resolve(), "semantic refuter output")
    require(refuter_path == proof_root / "refuter.json", "semantic refuter output path differs")
    require(not refuter_path.exists(), "semantic refuter already exists")
    refuter = expected_refuter(proof_root, core_path, subject_path.resolve(), subject)
    common.write_json_new(refuter_path, refuter)
    require(json_exact(validate_refuter(refuter_path, core_path, subject_path), refuter), "new semantic refuter did not verify exactly")
    return refuter_path


def validate_refuter(refuter_path: Path, core_path: Path, subject_path: Path) -> dict[str, object]:
    _, proof_root, core_path = proof_context(core_path)
    subject = validate_subject(subject_path, core_path)
    refuter_path = common.require_plain_file(refuter_path.resolve(), "independent target-lock semantic refuter")
    require(refuter_path.stat().st_nlink == 1, "semantic refuter is hardlinked")
    require(refuter_path == proof_root / "refuter.json", "semantic refuter path differs")
    refuter = read_json(refuter_path, "independent target-lock semantic refuter", canonical=True)
    expected = expected_refuter(proof_root, core_path, subject_path.resolve(), subject)
    require(json_exact(refuter, expected), "semantic refuter differs from the four parsed independent reviews")
    return refuter


def expected_ready(
    proof_root: Path,
    core_path: Path,
    subject_path: Path,
    refuter_path: Path,
    subject: Mapping[str, object],
    completed_at: str,
) -> dict[str, object]:
    require(TIMESTAMP_RE.fullmatch(completed_at) is not None, "READY completion timestamp differs")
    return {
        "schema": READY_SCHEMA,
        "status": "READY",
        "verdict": "SCRATCH_SEMANTIC_COHORT_AUTHORIZED",
        "completedAtUtc": completed_at,
        "core": proof_stamp(core_path, proof_root),
        "subject": proof_stamp(subject_path, proof_root),
        "refuter": proof_stamp(refuter_path, proof_root),
        "decisions": accepted_decisions(subject),
        "addresses": list(ADDRESSES),
        "proposedNames": PROPOSED_NAMES,
        "declaredReviewProviders": [REVIEW_CONFIG[key]["provider"] for key in REVIEW_CONFIG],
        "semanticNamesAuthorized": True,
        "liveMutationAuthorized": False,
        "liveGate": "PRE_LIVE_IDENTITY_BACKUP_QUIESCENCE_ONE_SHOT_APPLY_SEPARATE_READBACK_POST_BACKUP_REQUIRED",
        "globalTargetLockParityProved": False,
        "rebuildParityProved": False,
        "staleOrGapCrossedReturnBacklinksAdmitted": False,
        "modelIdentityCryptographicallyAuthenticated": False,
    }


def validate_proof_tree(proof_root: Path, *, ready_present: bool) -> None:
    expected_files = {"proof.core.json", "refuter-subject.json", "refuter.json"}
    if ready_present:
        expected_files.add("proof.ready.json")
    root_entries = list(proof_root.iterdir())
    require({path.name for path in root_entries} == expected_files | {"reviews"}, "proof-root artifact set differs")
    for path in root_entries:
        expected_directory = path.name == "reviews"
        require(
            not is_reparse(path) and (path.is_dir() if expected_directory else path.is_file()),
            f"proof-root entry is not the expected plain type: {path.name}",
        )
    reviews_root = common.require_plain_directory(proof_root / "reviews", "reviews root")
    review_entries = list(reviews_root.iterdir())
    require({path.name for path in review_entries} == set(REVIEW_CONFIG), "review directory set differs")
    require(all(path.is_dir() and not is_reparse(path) for path in review_entries), "reviews root contains a non-plain directory")
    assert_no_partials(proof_root)


def finalize(core_path: Path, subject_path: Path, refuter_path: Path, ready_path: Path) -> Path:
    _, proof_root, core_path = proof_context(core_path)
    subject = validate_subject(subject_path, core_path)
    validate_refuter(refuter_path, core_path, subject_path)
    ready_path = common.require_plain_existing_ancestors(ready_path.resolve(), "proof READY output")
    require(ready_path == proof_root / "proof.ready.json", "proof READY path differs")
    require(not ready_path.exists(), "proof READY already exists")
    validate_proof_tree(proof_root, ready_present=False)
    ready = expected_ready(proof_root, core_path, subject_path.resolve(), refuter_path.resolve(), subject, common.utc_now())
    common.write_json_new(ready_path, ready)
    require(json_exact(verify_ready(ready_path), ready), "new proof READY did not verify exactly")
    return ready_path


def verify_ready(ready_path: Path) -> dict[str, object]:
    ready_path = common.require_plain_file(ready_path.resolve(), "target-lock proof READY")
    require(ready_path.stat().st_nlink == 1, "target-lock proof READY is hardlinked")
    require(ready_path.name == "proof.ready.json", "proof READY filename differs")
    proof_root = common.require_plain_directory(ready_path.parent, "target-lock proof root")
    repository = common.require_plain_directory(Path(__file__).resolve().parents[1], "proof repository")
    require(proof_root.parent == repository / "local-lab", "proof READY root differs")
    core_path = proof_root / "proof.core.json"
    subject_path = proof_root / "refuter-subject.json"
    refuter_path = proof_root / "refuter.json"
    verify_core(core_path)
    subject = validate_subject(subject_path, core_path)
    validate_refuter(refuter_path, core_path, subject_path)
    validate_proof_tree(proof_root, ready_present=True)
    ready = read_json(ready_path, "target-lock proof READY", canonical=True)
    completed_at = ready.get("completedAtUtc")
    require(isinstance(completed_at, str), "proof READY completion timestamp differs")
    expected = expected_ready(proof_root, core_path, subject_path, refuter_path, subject, completed_at)
    require(json_exact(ready, expected), "proof READY differs from the complete reconstructed boundary")
    return ready


def default_campaign(repository: Path) -> Path:
    return repository / "local-lab/ghidra-target-lock-semantic-promotion-20260803-v1"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build-core", help="freeze the exact replicated scratch proof")
    build.add_argument("--campaign", type=Path)
    build.add_argument("--out", type=Path, required=True)

    verify = sub.add_parser("verify-core", help="rehash and verify a frozen proof core")
    verify.add_argument("core", type=Path)

    prepare = sub.add_parser("prepare-reviews", help="write the four deterministic exact-subject prompts")
    prepare.add_argument("--core", type=Path, required=True)
    prepare.add_argument("--subject", type=Path, required=True)

    run_review = sub.add_parser("run-review", help="run and seal one exact external review")
    run_review.add_argument("--core", type=Path, required=True)
    run_review.add_argument("--subject", type=Path, required=True)
    run_review.add_argument("--review-id", choices=("grok", "opus-medium", "opus-max"), required=True)

    record_codex = sub.add_parser("record-codex-review", help="seal a returned Codex collaboration review")
    record_codex.add_argument("--core", type=Path, required=True)
    record_codex.add_argument("--subject", type=Path, required=True)
    record_codex.add_argument("--session-id", required=True)
    record_codex.add_argument("--started-at", required=True)
    record_codex.add_argument("--completed-at", required=True)

    refuter = sub.add_parser("build-refuter", help="parse and bind the four exact independent reviews")
    refuter.add_argument("--core", type=Path, required=True)
    refuter.add_argument("--subject", type=Path, required=True)
    refuter.add_argument("--refuter", type=Path, required=True)

    final = sub.add_parser("finalize", help="bind an independent semantic refuter and issue scratch READY")
    final.add_argument("--core", type=Path, required=True)
    final.add_argument("--subject", type=Path, required=True)
    final.add_argument("--refuter", type=Path, required=True)
    final.add_argument("--ready", type=Path, required=True)

    verify_ready_parser = sub.add_parser("verify-ready", help="fully reconstruct a published scratch READY")
    verify_ready_parser.add_argument("ready", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    repository = args.repo_root.resolve()
    try:
        if args.command == "build-core":
            campaign = (args.campaign or default_campaign(repository)).resolve()
            core, subject = build_core(repository, campaign, args.out.resolve())
            print(
                f"CORE_FROZEN core_sha256={common.sha256_file(core)} "
                f"subject_sha256={common.sha256_file(subject)} semantic_names_authorized=false"
            )
        elif args.command == "verify-core":
            core = verify_core(args.core.resolve())
            print(
                f"CORE_VERIFIED status={core['status']} "
                f"sha256={common.sha256_file(args.core.resolve())}"
            )
        elif args.command == "prepare-reviews":
            reviews = prepare_reviews(args.core.resolve(), args.subject.resolve())
            print(f"REVIEWS_PREPARED root={reviews} prompts={len(REVIEW_CONFIG)}")
        elif args.command == "run-review":
            run = run_external_review(args.core.resolve(), args.subject.resolve(), args.review_id)
            print(f"REVIEW_COMPLETE id={args.review_id} run_sha256={common.sha256_file(run)}")
        elif args.command == "record-codex-review":
            run = record_codex_review(
                args.core.resolve(), args.subject.resolve(), args.session_id,
                args.started_at, args.completed_at,
            )
            print(f"REVIEW_COMPLETE id=codex run_sha256={common.sha256_file(run)}")
        elif args.command == "build-refuter":
            refuter = build_refuter(args.core.resolve(), args.subject.resolve(), args.refuter.resolve())
            print(f"REFUTER_FROZEN sha256={common.sha256_file(refuter)} live_mutation_authorized=false")
        elif args.command == "finalize":
            ready = finalize(
                args.core.resolve(),
                args.subject.resolve(),
                args.refuter.resolve(),
                args.ready.resolve(),
            )
            print(f"READY sha256={common.sha256_file(ready)} live_mutation_authorized=false")
        else:
            ready = verify_ready(args.ready.resolve())
            print(
                f"READY_VERIFIED status={ready['status']} "
                f"sha256={common.sha256_file(args.ready.resolve())} live_mutation_authorized=false"
            )
        return 0
    except ProofError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
