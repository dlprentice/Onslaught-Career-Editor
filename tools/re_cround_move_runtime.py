#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Prove and package the bounded CRound slot-66 runtime envelope.

This proof is read-only.  It independently parses two retained TTD traces,
their discovery/exact replay pairs, and one deliberately poisoned replay.  It
then joins the observed dispatcher placement to pristine vtable/body bytes,
the exact PC-demo fingerprint, the current campaign frontier, and the partial
Level 100 reconstruction owner.  It does not claim complete Move semantics,
receiver writes, CMissile behavior, a shipped symbol spelling, or rebuild
parity.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import os
import struct
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "bea.re.cround-move-runtime-proof.v1"
READY_NAME = "proof.ready.json"
CLAIM = "CROUND_SLOT66_STRICT_RECEIVER_PLACEMENT_AND_CALL_ENVELOPE_C2_BOUNDED"
OVERLAY_SCHEMA = "bea.re.runtime-contract-overlay.v1"
ADJUDICATION_SCHEMA = "bea.re.runtime-contract-adjudication.v1"
REFUTER_SUBJECT_SCHEMA = "bea.re.refuter-subject.v1"

SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
RUNTIME_SHA256 = "e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4"
ENTITY_KEY = (
    "CODE:" + SPECIMEN_SHA256
    + ":VA=0x004d8e40:RANGES=daccc55d23d64d0459770c104dbecdd1d6d8d2544be953af8c35fc866f67b796"
)
CONTRACT_ID = "C-baf981daeeb74c4c"
QUESTION_ID = "Q-74904e8721aa85b9"
CURRENT_NAME = "VFuncSlot_66_004d8e40"

EVIDENCE_RELATIVE = Path("local-lab/cround-move-existing-trace-20260812-v1")
CAMPAIGN_RELATIVE = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-20-cexplosion-hit-runtime-v1"
)
CAMPAIGN_READY_SHA256 = "13326fed25845e2351a2c68b57afe1bf2593786d2feb5f9e7d045fb7120a44ea"
CAMPAIGN_REDUCER_ID = "6e5777916ec5c7b94cdf6db727873bef589a14fec3bfac7ea4d895afda59c7fe"

ENTRY = 0x004D8E40
END_EXCLUSIVE = 0x004D9905
BODY_SHA256 = "819f5211e6e246292a3f0a9bbfa60b712711d7c8ded288d26e08734a88071638"
CALL_SITE = 0x00401AEA
FALLTHROUGH = 0x00401AF0
RETURN_SITE = 0x004D9904
CROUND_VTABLE = 0x005DE82C
CMISSILE_VTABLE = 0x005E3BA4
CROUND_SLOT66_CELL = CROUND_VTABLE + 66 * 4
CMISSILE_SLOT66_CELL = CMISSILE_VTABLE + 66 * 4

RUNTIME_COLUMNS = [
    "contractId", "entityKey", "entityKind", "entryVa", "currentName",
    "nativeShippedName", "contractState", "semanticGrade", "receiver", "inputs",
    "returns", "writes", "sideEffects", "preconditions", "failureModes",
    "authorVerdict", "runtimeVerdict", "refuterVerdict", "questionIds",
    "evidenceRefs", "cheapestFalsifier", "rebuildOwner", "rebuildImplementation",
    "parityTests", "rebuildState", "remainingUncertainty", "supersedesEntityKeys",
    "lastMeasurementDate", "scopeKind", "payloadSha256", "receiverVtable",
    "observedCallVas", "controlSummary", "runtimeEvidenceSha256", "baseContractId",
    "questionIdsAddressed",
]

PINS: dict[str, tuple[int, str]] = {
    "preregistration.md": (2085, "15d1b2602b381471dae33f91a099602ba6ee9ae0a70a5cfaeacb733a80090efe"),
    "targets-discovery.tsv": (155, "f1779d919f896ec5c52fb49f9a7bb64374e95bb9f47a8e1f8b47b788530ba501"),
    "targets-level522-exact.tsv": (164, "07f9c82e9420405bb3ddc1aabd41e7b08824c4c0fb89bc1b8b311eb309f09b38"),
    "targets-level741-exact.tsv": (167, "fbee5921f4e6a03926570a82c9ebc16f0fdbefb7031b8096ca4710fb02456639"),
    "targets-level522-poison-232.tsv": (164, "3c8ed048e5eb66c714a3239df21e8562c8b408d2e3b16c19b608d66adddb475c"),
    "level522-discovery-v1/call-context.jsonl": (828925, "d236a65235a7e7757822d31f71e73513dce2ddf39320d7500bd43dfddc9396d5"),
    "level522-discovery-v1/receipt.json": (7698, "a0ca4bd775b13c0e77689f78be94c4ff55d0b438914ecac98e2e3827fabae057"),
    "level522-discovery-v1/manifest.json": (3956, "992fd35c94a7602f47d04c3cef80a7b9f725bafad170929c4ddde119bab59516"),
    "level522-discovery-v1/READY": (571, "379bd888ca3b36dd1d48c8de9f35de419f313f5c3d5f33ce15add8e11d22ff3f"),
    "level522-discovery-v1/targets.tsv": (155, "f1779d919f896ec5c52fb49f9a7bb64374e95bb9f47a8e1f8b47b788530ba501"),
    "level522-exact-v1/call-context.jsonl": (828924, "63e51e69b5aa64e66af708fb583842ece5267cbe4f5bb454ea71b5c84e57a0d8"),
    "level522-exact-v1/receipt.json": (7675, "f3717fcf504e34fb783bdfd297ef1c546c0b97e879fbb2fa2e70896aee3dc532"),
    "level522-exact-v1/manifest.json": (3928, "73c3f2e15ce7237541065e67c72eddb622ef2c4ef2c45064565a23075777dcbd"),
    "level522-exact-v1/READY": (567, "1276daa759a759a5bc5099cbc38f9d0c9ee6a72687f3bc30c17a1f222c754643"),
    "level522-exact-v1/targets.tsv": (164, "07f9c82e9420405bb3ddc1aabd41e7b08824c4c0fb89bc1b8b311eb309f09b38"),
    "level741-holdout-discovery-v1/call-context.jsonl": (26138679, "1dc803c4d403c832bf4694cb5530f363cfeeb09b1f5dd386bb076e34095d5ae2"),
    "level741-holdout-discovery-v1/receipt.json": (7784, "946400f3bc8311abbb45a017df94b03c5564e9ec83dcb1d94f6746f31adfd18b"),
    "level741-holdout-discovery-v1/manifest.json": (4024, "3218d6dd232e1cc303511b0e7a026eee077028755015686a40bb66c8ddbdae53"),
    "level741-holdout-discovery-v1/READY": (579, "d0ff8c116b322e11e136072ddcb935fb1a20a6e6a137aa943153470491c9c63a"),
    "level741-holdout-discovery-v1/targets.tsv": (155, "f1779d919f896ec5c52fb49f9a7bb64374e95bb9f47a8e1f8b47b788530ba501"),
    "level741-holdout-exact-v1/call-context.jsonl": (26138681, "86061da6689510b616232316f9a0e382df1bb10150e6054e2b15519de324c76d"),
    "level741-holdout-exact-v1/receipt.json": (7761, "20ab8d4af4bb4a9654366a0aa548f1590ae12c45cc0e958311ca7e653290149b"),
    "level741-holdout-exact-v1/manifest.json": (3996, "c43dfd0f207a9f28ff528037faf1d9103a888bf7ca5b77d355e1d34587e86d21"),
    "level741-holdout-exact-v1/READY": (575, "cdd80e5884184de58d312aea9a21d44dc721d0c8d02182908e0d3948e5d4008b"),
    "level741-holdout-exact-v1/targets.tsv": (167, "fbee5921f4e6a03926570a82c9ebc16f0fdbefb7031b8096ca4710fb02456639"),
    "level522-poison-232-v1/call-context.jsonl": (828933, "d70efd69105052f582a4b01d0a2d9084426ed92b3dda85a1723a07b12fe104f0"),
    "level522-poison-232-v1/receipt.json": (7721, "6e87afad6d6d256750d03053fdb4a0986e462638489f5ee8307ff9d2b09dd2e3"),
    "level522-poison-232-v1/manifest.json": (3972, "e57e95461fe6df37d192b0b390eb1d0099cee6888487ae5b3581128ef7aef576"),
    "level522-poison-232-v1/targets.tsv": (164, "3c8ed048e5eb66c714a3239df21e8562c8b408d2e3b16c19b608d66adddb475c"),
}

REPO_PINS: dict[str, tuple[int, str]] = {
    "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup": (2_506_752, SPECIMEN_SHA256),
    "local-lab/safe-copy-bea-pristine/BEA.exe": (2_506_752, RUNTIME_SHA256),
    "reverse-engineering/binary-analysis/pc-demo-retail-virtual-target-map-2026-08-11.tsv": (1_204_103, "ba2db0551beeed458ea6265b87d1a5cf93bc2dd2c464da3f7f0c6702a4d4c750"),
    "reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv": (3_288_437, "cfe90af382269cb2e64996d10df7777bd00fcd8e1844b9823ef74bc6199b8974"),
    "reverse-engineering/binary-analysis/ghidra-function-name-table-2026-07-27.tsv": (475_327, "44f49ca1ccb326b5fb425e1639b6a0650565d7567a6afae96f28414aa9e68b11"),
    "rebuild/OnslaughtRebuild.Core/Level100ActorWeaponRuntime.cs": (32_010, "8f8692250e70eea6bea0702dfd56d1c3c90ad17dd8dffd65acf639cec4ba6197"),
    "rebuild/OnslaughtRebuild.Core.Tests/Level100ActorWeaponTests.cs": (17_484, "cb64be81481a0d6712a13d7f7a16449974d38ba047617444b6f96c9d024c2bfc"),
}

RUNS = {
    "level522-discovery-v1": {
        "trace": ("G:\\bea-ttd\\level-opening-3m-v1-level522\\level-opening-3m-v1-level522.run", 5_473_566_720, "f0169a05e03f3fda581d4c7f5cd5e8987a88494f44761fb31b74ac8c1647115d"),
        "counts": (231, 217, 14), "exact": False, "receivers": 21,
    },
    "level522-exact-v1": {
        "trace": ("G:\\bea-ttd\\level-opening-3m-v1-level522\\level-opening-3m-v1-level522.run", 5_473_566_720, "f0169a05e03f3fda581d4c7f5cd5e8987a88494f44761fb31b74ac8c1647115d"),
        "counts": (231, 217, 14), "exact": True, "receivers": 21,
    },
    "level741-holdout-discovery-v1": {
        "trace": ("G:\\bea-ttd\\level-opening-3m-v1-level741\\level-opening-3m-v1-level741.run", 8_405_385_216, "8f929994ba50d7a54148e0bf96d1363aa2fb940f4c9f5afa2414daf61c41e324"),
        "counts": (7_282, 6_987, 295), "exact": False, "receivers": 50,
    },
    "level741-holdout-exact-v1": {
        "trace": ("G:\\bea-ttd\\level-opening-3m-v1-level741\\level-opening-3m-v1-level741.run", 8_405_385_216, "8f929994ba50d7a54148e0bf96d1363aa2fb940f4c9f5afa2414daf61c41e324"),
        "counts": (7_282, 6_987, 295), "exact": True, "receivers": 50,
    },
}


class ProofError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProofError(message)


def repository_root() -> Path:
    configured = os.environ.get("BEA_REPO_ROOT")
    return Path(configured).resolve() if configured else Path(__file__).resolve().parents[1]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stamp(path: Path, relative_to: Path | None = None) -> dict[str, Any]:
    require(path.is_file(), f"missing file: {path}")
    label = (
        path.resolve().relative_to(relative_to.resolve()).as_posix()
        if relative_to is not None else str(path.resolve())
    )
    return {"path": label, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProofError(f"cannot parse {path}: {exc}") from exc
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    except (OSError, json.JSONDecodeError) as exc:
        raise ProofError(f"cannot parse {path}: {exc}") from exc
    require(rows and all(isinstance(row, dict) for row in rows), f"JSONL is empty/malformed: {path}")
    return rows


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        lines = [line for line in stream if not line.startswith("#")]
    return list(csv.DictReader(lines, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        stream.write(f"# {OVERLAY_SCHEMA}\n")
        writer = csv.DictWriter(stream, fieldnames=RUNTIME_COLUMNS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in RUNTIME_COLUMNS})


def exact_inputs(root: Path, evidence: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for relative, expected in PINS.items():
        actual = stamp(evidence / relative, root)
        require((actual["bytes"], actual["sha256"]) == expected, f"evidence identity differs: {relative}")
        result[relative] = actual
    for relative, expected in REPO_PINS.items():
        actual = stamp(root / relative, root)
        require((actual["bytes"], actual["sha256"]) == expected, f"repository input differs: {relative}")
        result[relative] = actual
    return result


def as_int(value: Any) -> int:
    return int(str(value), 0)


def observation_projection(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [copy.deepcopy(row) for row in rows if row.get("kind") in {"event", "invocation", "gap-summary"}]


def one_kind(rows: list[dict[str, Any]], kind: str, lane: str) -> dict[str, Any]:
    matches = [row for row in rows if row.get("kind") == kind]
    require(len(matches) == 1, f"{lane} {kind} cardinality differs")
    return matches[0]


def validate_observations(
    rows: list[dict[str, Any]], lane: str, spec: dict[str, Any]
) -> dict[str, Any]:
    calls_expected, gap_free_expected, orphan_expected = spec["counts"]
    metadata = one_kind(rows, "metadata", lane)
    target = one_kind(rows, "target", lane)
    summary = one_kind(rows, "summary", lane)
    one_kind(rows, "gap-summary", lane)
    events = [row for row in rows if row.get("kind") == "event"]
    invocations = [row for row in rows if row.get("kind") == "invocation"]
    require(len(events) == calls_expected * 3, f"{lane} event count differs")
    require(len(invocations) == calls_expected, f"{lane} invocation count differs")
    require(len(rows) == calls_expected * 4 + 4, f"{lane} JSONL row count differs")
    require(metadata.get("schema") == "bea.ttd.call-context.v3", f"{lane} metadata schema differs")
    require(metadata.get("module_base") == "0x400000" and metadata.get("module_size") == "0x5D8000", f"{lane} module identity differs")
    require(metadata.get("replay_mode") == "sequential-all-segments" and metadata.get("stack_bytes_requested") == 64, f"{lane} collection mode differs")
    require(target.get("entry_va") == "0x4D8E40" and target.get("entry_rva") == "0xD8E40", f"{lane} target entry differs")
    require(target.get("ranges") == [{"rva_start": "0xD8E40", "rva_end_exclusive": "0xD9905"}], f"{lane} target range differs")
    expected_text = str(calls_expected) if spec["exact"] else None
    for field in ("expected_entry_count", "expected_call_count", "expected_return_count"):
        require(target.get(field) == expected_text, f"{lane} {field} differs")
    target_counts = (
        as_int(target["observed_call_count"]), as_int(target["observed_entry_count"]),
        as_int(target["observed_return_count"]), as_int(target["observed_validated_return_count"]),
        as_int(target["observed_orphan_return_count"]), as_int(target["observed_gap_free_envelope_count"]),
    )
    require(target_counts == (calls_expected, calls_expected, calls_expected, gap_free_expected, orphan_expected, gap_free_expected), f"{lane} target counts differ")
    require(target.get("expectations_passed") is True, f"{lane} target expectations failed")

    event_by_index: dict[int, dict[str, Any]] = {}
    for event in events:
        index = as_int(event["event_index"])
        require(index not in event_by_index, f"{lane} duplicate event index")
        event_by_index[index] = event
    require(set(event_by_index) == set(range(calls_expected * 3)), f"{lane} event indexes differ")
    event_types = Counter(str(row.get("event_type")) for row in events)
    require(event_types == Counter({"call": calls_expected, "entry": calls_expected, "return": calls_expected}), f"{lane} event types differ")

    receivers: set[int] = set()
    grades: Counter[str] = Counter()
    referenced_returns: set[int] = set()
    for invocation in invocations:
        index = as_int(invocation["invocation_index"])
        require(invocation.get("schema") == "bea.ttd.call-context.v3" and invocation.get("target_index") == 0, f"{lane} invocation identity differs")
        require(invocation.get("call_entry_checks_passed") is True, f"{lane} call-entry checks failed")
        call = event_by_index[as_int(invocation["call_event_index"])]
        entry = event_by_index[as_int(invocation["entry_event_index"])]
        require(call.get("event_type") == "call" and entry.get("event_type") == "entry", f"{lane} invocation event roles differ")
        require(call.get("invocation_index") == index and entry.get("invocation_index") == index, f"{lane} invocation indexes differ")
        require(call.get("pc") == "0x401AEA" and as_int(call.get("instruction_target")) == ENTRY and as_int(call.get("fallthrough")) == FALLTHROUGH, f"{lane} inherited dispatcher call differs")
        require(entry.get("pc") == "0x4D8E40" and as_int(entry.get("instruction_target")) == ENTRY, f"{lane} entry event differs")
        require(entry.get("previous_position") == call.get("position"), f"{lane} call-entry ordering differs")
        require(call.get("unique_thread_id") == entry.get("unique_thread_id"), f"{lane} call-entry thread differs")
        for event, role in ((call, "call"), (entry, "entry")):
            require(event.get("integer_registers_valid") is True and event.get("register_views_agree") is True, f"{lane} {role} registers invalid")
        call_regs = call["registers"]
        entry_regs = entry["registers"]
        receiver = as_int(call_regs["ecx"])
        require(as_int(call_regs["edx"]) == CROUND_VTABLE, f"{lane} strict CRound vtable differs")
        require(as_int(call_regs["edx"]) != CMISSILE_VTABLE, f"{lane} CMissile placement observed")
        require(receiver == as_int(call_regs["esi"]), f"{lane} call receiver is not ESI")
        require(receiver == as_int(entry_regs["ecx"]) == as_int(entry_regs["esi"]), f"{lane} call-entry receiver differs")
        require(as_int(entry_regs["edx"]) == CROUND_VTABLE, f"{lane} entry vtable register differs")
        receivers.add(receiver)
        grade = str(invocation.get("grade"))
        grades[grade] += 1
        if grade == "CALL_ENTRY_RETURN":
            require(invocation.get("return_checks_passed") is True and invocation.get("return_event_index") is not None, f"{lane} validated return differs")
            return_index = as_int(invocation["return_event_index"])
            returned = event_by_index[return_index]
            referenced_returns.add(return_index)
            require(returned.get("event_type") == "return" and returned.get("invocation_index") == index, f"{lane} paired return differs")
            require(returned.get("unique_thread_id") == call.get("unique_thread_id"), f"{lane} return thread differs")
        elif grade == "CALL_ENTRY":
            require(invocation.get("return_checks_passed") is False and invocation.get("return_event_index") is None, f"{lane} orphan-return grade differs")
            require(invocation.get("continuity_break_crossed") is True, f"{lane} orphan lacks continuity barrier")
        else:
            raise ProofError(f"{lane} unsupported invocation grade: {grade}")

    require(grades == Counter({"CALL_ENTRY_RETURN": gap_free_expected, "CALL_ENTRY": orphan_expected}), f"{lane} invocation grades differ")
    require(len(referenced_returns) == gap_free_expected, f"{lane} validated return references differ")
    raw_returns = [row for row in events if row.get("event_type") == "return"]
    for returned in raw_returns:
        require(as_int(returned.get("pc")) == RETURN_SITE, f"{lane} return site differs")
        require(as_int(returned.get("instruction_target")) == FALLTHROUGH, f"{lane} return target differs")
        instruction = returned.get("instruction_bytes", {})
        require(returned.get("decoded_near_return") is True and instruction.get("query_valid") is True and str(instruction.get("hex", "")).upper() == "C39090", f"{lane} return decode differs")
    require(len(receivers) == spec["receivers"], f"{lane} receiver population differs")
    summary_counts = (
        as_int(summary["call_entry_pair_count"]), as_int(summary["validated_return_count"]),
        as_int(summary["raw_return_count"]), as_int(summary["orphan_return_count"]),
        as_int(summary["gap_free_envelope_count"]),
    )
    require(summary_counts == (calls_expected, gap_free_expected, calls_expected, orphan_expected, gap_free_expected), f"{lane} summary counts differ")
    for field in ("replay_complete", "replay_counters_sane", "ordering_valid", "contexts_valid", "expectations_passed", "pairing_expectations_passed", "collector_checks_passed"):
        require(summary.get(field) is True, f"{lane} summary failed: {field}")
    require(summary.get("truncated") is False and summary.get("callback_failed") is False, f"{lane} replay truncated/failed")
    return {
        "calls": calls_expected,
        "callEntryPairs": calls_expected,
        "rawReturns": calls_expected,
        "gapFreeReturns": gap_free_expected,
        "rawOrphanReturns": orphan_expected,
        "sessionLocalReceivers": len(receivers),
        "receiverVtable": "0x005de82c",
        "callVa": "0x00401aea",
        "entryVa": "0x004d8e40",
        "returnVa": "0x004d9904",
    }


def validate_ready_envelope(evidence: Path, lane: str, spec: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    lane_root = evidence / lane
    receipt = read_json(lane_root / "receipt.json")
    manifest = read_json(lane_root / "manifest.json")
    ready = read_json(lane_root / "READY")
    trace_path, trace_bytes, trace_sha = spec["trace"]
    require(receipt.get("schemaVersion") == "bea-ttd-call-context-receipt.v3", f"{lane} receipt schema differs")
    require(receipt.get("collectorExitCode") == 0 and receipt.get("exitCode") == 0 and receipt.get("readyEligible") is True, f"{lane} is not READY")
    require(receipt.get("trace", {}).get("path") == trace_path and receipt["trace"].get("bytes") == trace_bytes and str(receipt["trace"].get("sha256", "")).lower() == trace_sha, f"{lane} trace identity differs")
    trace = Path(trace_path)
    require(trace.is_file() and trace.stat().st_size == trace_bytes, f"{lane} retained trace path/size differs")
    require(str(receipt.get("target", {}).get("sha256", "")).lower() == RUNTIME_SHA256 and receipt["target"].get("bytes") == 2_506_752, f"{lane} runtime image differs")
    invocation = receipt.get("invocation", {})
    require(invocation.get("from") == "" and invocation.get("to") == "" and invocation.get("stackBytes") == 64 and invocation.get("eventLimit") == 100000 and invocation.get("replayMode") == "sequential-all-segments", f"{lane} replay invocation differs")
    calls, gap_free, orphan = spec["counts"]
    context = receipt.get("callContext", {})
    require((context.get("eventCount"), context.get("invocationCount"), context.get("callEntryPairCount"), context.get("validatedReturnCount"), context.get("rawReturnCount"), context.get("orphanReturnCount"), context.get("gapFreeEnvelopeCount")) == (calls * 3, calls, calls, gap_free, calls, orphan, gap_free), f"{lane} receipt counts differ")
    require(manifest.get("schemaVersion") == "bea-ttd-call-context-manifest.v3" and manifest.get("status") == "READY" and manifest.get("proof", {}).get("collectorChecksPassed") is True, f"{lane} manifest is not READY")
    require(ready.get("schemaVersion") == "bea-ttd-call-context-ready.v3", f"{lane} READY schema differs")
    require(str(ready.get("receiptSha256", "")).lower() == sha256_file(lane_root / "receipt.json"), f"{lane} READY receipt binding differs")
    require(str(ready.get("callContextSha256", "")).lower() == sha256_file(lane_root / "call-context.jsonl"), f"{lane} READY JSONL binding differs")
    require(str(ready.get("manifest", {}).get("sha256", "")).lower() == sha256_file(lane_root / "manifest.json"), f"{lane} READY manifest binding differs")
    rows = read_jsonl(lane_root / "call-context.jsonl")
    summary = validate_observations(rows, lane, spec)
    return rows, summary


def validate_runtime(root: Path, evidence: Path) -> dict[str, Any]:
    rows_by_lane: dict[str, list[dict[str, Any]]] = {}
    summaries: dict[str, dict[str, Any]] = {}
    for lane, spec in RUNS.items():
        rows, summary = validate_ready_envelope(evidence, lane, spec)
        rows_by_lane[lane] = rows
        summaries[lane] = summary
    require(observation_projection(rows_by_lane["level522-discovery-v1"]) == observation_projection(rows_by_lane["level522-exact-v1"]), "Level 522 exact replay differs from discovery observations")
    require(observation_projection(rows_by_lane["level741-holdout-discovery-v1"]) == observation_projection(rows_by_lane["level741-holdout-exact-v1"]), "Level 741 exact replay differs from discovery observations")

    poison_root = evidence / "level522-poison-232-v1"
    poison_receipt = read_json(poison_root / "receipt.json")
    poison_manifest = read_json(poison_root / "manifest.json")
    poison_rows = read_jsonl(poison_root / "call-context.jsonl")
    require(poison_receipt.get("collectorExitCode") == 10 and poison_receipt.get("exitCode") == 10 and poison_receipt.get("readyEligible") is False, "poison collector did not refuse")
    require(poison_manifest.get("status") == "BLOCKED" and poison_manifest.get("proof", {}).get("collectorChecksPassed") is False, "poison manifest did not block")
    require(not (poison_root / "READY").exists(), "poison published READY")
    poison_summary = poison_receipt.get("summary", {})
    require(poison_summary.get("replay_complete") is True and poison_summary.get("expectations_passed") is False and poison_summary.get("pairing_expectations_passed") is False and poison_summary.get("collector_checks_passed") is False, "poison summary did not fail only the expected gates")
    require(observation_projection(poison_rows) == observation_projection(rows_by_lane["level522-exact-v1"]), "poison changed the observed event stream")
    return {
        "traceIdentityMode": "WRAPPER_HASH_RECEIPT_PLUS_CURRENT_SIZE_NOT_REHASHED_BY_PROOF",
        "independentTraceSessions": 2,
        "exactReplayCalls": 7_513,
        "callEntryPairs": 7_513,
        "rawReturnCallbacks": 7_513,
        "gapFreeReturns": 7_204,
        "rawOrphanReturns": 309,
        "sessionLocalReceiverInstances": 71,
        "strictCRoundVtableAllCalls": True,
        "cmissileStyleVtableObserved": False,
        "receiverContinuityAllCallEntryPairs": True,
        "runs": {lane: summaries[lane] for lane in ("level522-exact-v1", "level741-holdout-exact-v1")},
        "discoveryExactProjectionEqual": {"level522": True, "level741": True},
        "poisonControl": {
            "kind": "EXPECTED_CALL_ENTRY_RETURN_COUNT_232_VERSUS_OBSERVED_231",
            "collectorExitCode": 10,
            "readyPublished": False,
            "eventStreamPreserved": True,
            "expectationsPassed": False,
            "pairingExpectationsPassed": False,
        },
    }


def pe_offset(image: bytes, va: int) -> int:
    pe = struct.unpack_from("<I", image, 0x3C)[0]
    require(image[pe:pe + 4] == b"PE\0\0", "pristine PE signature differs")
    count = struct.unpack_from("<H", image, pe + 6)[0]
    optional_size = struct.unpack_from("<H", image, pe + 20)[0]
    optional = pe + 24
    image_base = struct.unpack_from("<I", image, optional + 28)[0]
    rva = va - image_base
    table = optional + optional_size
    for index in range(count):
        row = table + index * 40
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from("<IIII", image, row + 8)
        if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
            return raw_pointer + rva - virtual_address
    raise ProofError(f"VA is not mapped: 0x{va:08x}")


def body(image: bytes, start: int, end: int) -> bytes:
    offset = pe_offset(image, start)
    return image[offset:offset + end - start]


def direct_call_targets(image: bytes, start: int, end: int) -> set[int]:
    raw = body(image, start, end)
    targets: set[int] = set()
    for index in range(len(raw) - 4):
        if raw[index] == 0xE8:
            relative = struct.unpack_from("<i", raw, index + 1)[0]
            targets.add(start + index + 5 + relative)
    return targets


def validate_static(root: Path) -> dict[str, Any]:
    pristine = (root / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup").read_bytes()
    runtime = (root / "local-lab/safe-copy-bea-pristine/BEA.exe").read_bytes()
    function = body(pristine, ENTRY, END_EXCLUSIVE)
    require(len(function) == 2_757 and sha256_bytes(function) == BODY_SHA256, "CRound slot-66 body differs")
    require(body(runtime, ENTRY, END_EXCLUSIVE) == function, "runtime slot-66 body differs from pristine")
    require(body(pristine, CALL_SITE, CALL_SITE + 6).hex() == "ff9208010000", "slot-66 dispatcher instruction differs")
    require(body(runtime, CALL_SITE, CALL_SITE + 6) == body(pristine, CALL_SITE, CALL_SITE + 6), "runtime dispatcher differs from pristine")
    require(struct.unpack("<I", body(pristine, CROUND_SLOT66_CELL, CROUND_SLOT66_CELL + 4))[0] == ENTRY, "strict CRound slot-66 cell differs")
    require(struct.unpack("<I", body(pristine, CMISSILE_SLOT66_CELL, CMISSILE_SLOT66_CELL + 4))[0] == ENTRY, "CMissile-style slot-66 cell differs")
    calls = direct_call_targets(pristine, ENTRY, END_EXCLUSIVE)
    require(0x004015E0 in calls and 0x004D9F30 in calls, "slot-66 static callees differ")

    demo_rows = read_tsv(root / "reverse-engineering/binary-analysis/pc-demo-retail-virtual-target-map-2026-08-11.tsv")
    demo = next((row for row in demo_rows if row.get("retail_va") == "0x004d8e40"), None)
    require(demo is not None, "PC-demo slot-66 row is absent")
    require(
        demo.get("demo_va") == "0x004d8d20"
        and demo.get("owner_classes") == "CMissile|CRound"
        and demo.get("placement_count") == "2"
        and demo.get("retail_body_bytes") == "2757"
        and demo.get("retail_instruction_count") == "826"
        and demo.get("demo_instruction_count") == "826"
        and demo.get("exact_zero_normalized") == "true"
        and demo.get("retail_instruction_stream_raw_sha256") == BODY_SHA256
        and demo.get("retail_instruction_stream_normalized_sha256") == demo.get("demo_instruction_stream_normalized_sha256"),
        "PC-demo slot-66 exact fingerprint differs",
    )
    names = read_tsv(root / "reverse-engineering/binary-analysis/ghidra-function-name-table-2026-07-27.tsv")
    named = next((row for row in names if row.get("address") == "0x004d8e40"), None)
    require(named is not None and named.get("name") == "CRound__Move" and named.get("bodyMin") == "0x004d8e40" and named.get("bodyMax") == "0x004d9904", "current saved project name/range differs")
    closure_rows = read_tsv(root / "reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv")
    closure = next((row for row in closure_rows if row.get("entryVa") == "0x004d8e40"), None)
    require(
        closure is not None
        and closure.get("trackedName") == "CRound__Move"
        and closure.get("disposableName") == "HYP__VFuncSlot_66_004d8e40"
        and closure.get("gradeAfter") == "C1_CANDIDATE_PARTIAL"
        and closure.get("bodyBytes") == "2757",
        "slot-66 static C1 closure differs",
    )
    return {
        "function": {"entryVa": "0x004d8e40", "endExclusive": "0x004d9905", "bytes": 2_757, "sha256": BODY_SHA256},
        "dispatcher": {"callVa": "0x00401aea", "instruction": "call dword ptr [edx+0x108]", "fallthrough": "0x00401af0"},
        "placements": {
            "strictCRound": {"vtable": "0x005de82c", "slot66Cell": "0x005de934", "target": "0x004d8e40"},
            "cmissileStyle": {"vtable": "0x005e3ba4", "slot66Cell": "0x005e3cac", "target": "0x004d8e40"},
        },
        "currentSavedProjectName": "CRound__Move",
        "sourceSpellingStatus": "OPEN_NOT_PROMOTED_BY_THIS_PROOF",
        "scopedIdentity": "CRound slot-66 Move/update override on observed strict-CRound receivers",
        "pcDemo": {"entryVa": "0x004d8d20", "instructionCount": 826, "exactZeroNormalized": True},
        "staticCallees": {"CActorMove": "0x004015e0", "effectHelper": "0x004d9f30"},
        "staticGradeBeforeRuntime": "C1_CANDIDATE_PARTIAL",
    }


def validate_campaign(root: Path, campaign: Path) -> dict[str, Any]:
    ready_path = campaign / "campaign.ready.json"
    require(sha256_file(ready_path) == CAMPAIGN_READY_SHA256, "Generation 20 READY differs")
    ready = read_json(ready_path)
    require(ready.get("generation") == 20 and ready.get("reducer", {}).get("id") == CAMPAIGN_REDUCER_ID, "Generation 20 identity differs")
    function = next(row for row in read_tsv(campaign / "campaign-functions.tsv") if row["entityKey"] == ENTITY_KEY)
    contract = next(row for row in read_tsv(campaign / "campaign-contracts.tsv") if row["contractId"] == CONTRACT_ID)
    question = next(row for row in read_tsv(campaign / "campaign-questions.tsv") if row["questionId"] == QUESTION_ID)
    require(function["currentName"] == CURRENT_NAME and function["resolutionState"] == "OPEN_JOIN" and function["semanticGrade"] == "OPAQUE" and function["campaignState"] == "OPEN_EXECUTED", "Generation 20 function frontier differs")
    require(contract["entityKey"] == ENTITY_KEY and contract["contractState"] == "OPEN" and contract["semanticGrade"] == "C0_OPAQUE" and contract["refuterVerdict"] == "UNSCORED", "Generation 20 contract frontier differs")
    require(question["entityKey"] == ENTITY_KEY and question["state"] == "OPEN" and question["questionType"] == "EXECUTED_FUNCTION_IDENTITY", "Generation 20 question frontier differs")
    return {"generation": 20, "ready": stamp(ready_path, root), "reducerId": CAMPAIGN_REDUCER_ID, "function": function, "contract": contract, "question": question}


EXPECTED_BOUNDARY = {
    "slot66CallsObserved": 7_513,
    "independentTraceSessions": 2,
    "sessionLocalReceiverInstances": 71,
    "callEntryPairsObserved": 7_513,
    "gapFreeReturnEnvelopes": 7_204,
    "rawOrphanReturnCallbacks": 309,
    "strictCRoundVtableAllObservedCalls": True,
    "receiverContinuityAllObservedCallEntryPairs": True,
    "cmissileStyleReceiverObserved": False,
    "receiverWritesObserved": False,
    "semanticReturnValueObserved": False,
    "completeMoveSemanticsClaimed": False,
    "allSubclassBehaviorClaimed": False,
    "shippedSourceSpellingClaimed": False,
    "rebuildState": "PARTIAL_CONTRACT",
}


def validate_claim_boundary(value: dict[str, Any]) -> None:
    require(value == EXPECTED_BOUNDARY, "claim boundary differs")


def derive(root: Path, campaign: Path) -> dict[str, Any]:
    evidence = root / EVIDENCE_RELATIVE
    require(evidence.is_dir(), "CRound Move evidence root is missing")
    inputs = exact_inputs(root, evidence)
    runtime = validate_runtime(root, evidence)
    static = validate_static(root)
    frontier = validate_campaign(root, campaign)
    boundary = dict(EXPECTED_BOUNDARY)
    validate_claim_boundary(boundary)
    return {
        "schema": SCHEMA,
        "verdict": "PASS",
        "claim": CLAIM,
        "specimen": {"sha256": SPECIMEN_SHA256, "role": "PRISTINE_STATIC_AUTHORITY_UNCHANGED"},
        "runtimeImage": {"sha256": RUNTIME_SHA256, "role": "EXISTING_TRACE_IMAGE_BODY_EQUAL_TO_PRISTINE_IN_SCOPE"},
        "entity": {
            "entityKey": ENTITY_KEY, "contractId": CONTRACT_ID,
            "questionId": QUESTION_ID, "currentName": CURRENT_NAME,
            "scopedIdentity": static["scopedIdentity"],
            "sourceSpellingStatus": static["sourceSpellingStatus"],
        },
        "campaign": frontier,
        "runtime": runtime,
        "static": static,
        "adjudication": {
            "semanticGrade": "C2_BOUNDED_RUNTIME",
            "contractState": "BOUNDED_CONTRACT_ADVANCED",
            "runtimeVerdict": "MEASURED_BOUNDED_STRICT_CROUND_SLOT66_CALL_ENVELOPE",
            "refuterVerdict": "SURVIVED",
            "questionDisposition": "CLOSE_BASE_AND_OPEN_NARROW_SUCCESSORS",
        },
        "rebuild": {
            "state": "PARTIAL_CONTRACT",
            "owner": inputs["rebuild/OnslaughtRebuild.Core/Level100ActorWeaponRuntime.cs"],
            "test": inputs["rebuild/OnslaughtRebuild.Core.Tests/Level100ActorWeaponTests.cs"],
            "implementation": "Level100ActorMechanics.AdvanceActorRounds / SteerSeekingRound",
            "scope": "partial Level 100 round integration and Forseti homing only; no complete retail slot-66 parity claim",
        },
        "claimBoundary": boundary,
        "limitations": [
            "The retained multi-gigabyte traces are wrapper-hash-bound and current-size-checked, not rehashed by this proof.",
            "The 7,513 calls span two independent traces; discovery and exact replays of one trace are calibration repeats, not additional sessions.",
            "All observed dispatches used the strict CRound vtable; no CMissile-style receiver was observed.",
            "The proof records call/entry receiver continuity and raw return callbacks, not receiver field writes or branch-specific state transitions.",
            "The function is treated as void; raw EAX values at return are not assigned semantic meaning.",
            "Static identity bounds the body as the slot-66 Move/update override; it does not prove original shipped symbol spelling.",
            "The rebuild mapping is PARTIAL_CONTRACT, not REBUILD_READY; no rebuild change is authorized by this proof.",
            "No game, trace, Ghidra project, or executable was mutated while producing this proof.",
        ],
        "inputs": inputs,
        "author": stamp(Path(__file__).resolve(), root),
    }


def selftest(root: Path, campaign: Path) -> dict[str, Any]:
    rows = read_jsonl(root / EVIDENCE_RELATIVE / "level522-exact-v1/call-context.jsonl")
    attacks: list[tuple[str, list[dict[str, Any]], str]] = []
    forged = copy.deepcopy(rows)
    next(row for row in forged if row.get("kind") == "event" and row.get("event_type") == "call")["registers"]["edx"] = "0x5E3BA4"
    attacks.append(("cmissile-vtable", forged, "strict CRound vtable differs"))
    forged = copy.deepcopy(rows)
    next(row for row in forged if row.get("kind") == "event" and row.get("event_type") == "entry")["registers"]["ecx"] = "0x1"
    attacks.append(("receiver-discontinuity", forged, "call-entry receiver differs"))
    forged = copy.deepcopy(rows)
    next(row for row in forged if row.get("kind") == "event" and row.get("event_type") == "return")["pc"] = "0x4D9903"
    attacks.append(("return-outside-body", forged, "return site differs"))
    rejected: list[str] = []
    for label, forged_rows, expected in attacks:
        try:
            validate_observations(forged_rows, f"selftest-{label}", RUNS["level522-exact-v1"])
        except ProofError as exc:
            require(expected in str(exc), f"{label} rejected by unintended gate: {exc}")
            rejected.append(label)
        else:
            raise ProofError(f"selftest attack accepted: {label}")
    for label, key in (
        ("complete-move-overclaim", "completeMoveSemanticsClaimed"),
        ("all-subclass-overclaim", "allSubclassBehaviorClaimed"),
        ("rebuild-ready-overclaim", "rebuildState"),
    ):
        forged_boundary = dict(EXPECTED_BOUNDARY)
        forged_boundary[key] = "REBUILD_READY" if key == "rebuildState" else True
        try:
            validate_claim_boundary(forged_boundary)
        except ProofError:
            rejected.append(label)
        else:
            raise ProofError(f"selftest attack accepted: {label}")
    require(validate_campaign(root, campaign)["generation"] == 20, "selftest campaign gate failed")
    return {"count": len(rejected), "attacks": rejected}


def validate_saved(saved: dict[str, Any], root: Path, campaign: Path) -> None:
    require(set(saved) == set(derive(root, campaign)) | {"generatedAtUtc", "selftest"}, "proof top-level shape differs")
    generated = saved.get("generatedAtUtc")
    require(isinstance(generated, str) and generated.endswith("Z"), "proof timestamp is not UTC")
    datetime.fromisoformat(generated[:-1] + "+00:00")
    stable = dict(saved)
    stable.pop("generatedAtUtc")
    tests = stable.pop("selftest")
    require(tests == selftest(root, campaign), "proof selftest differs")
    require(stable == derive(root, campaign), "proof content differs from independently rederived evidence")


def build(root: Path, campaign: Path, out: Path) -> Path:
    out = out.resolve()
    require(not out.exists(), f"refusing existing proof root: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))
    try:
        value = derive(root, campaign)
        value["selftest"] = selftest(root, campaign)
        value["generatedAtUtc"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        ready = stage / READY_NAME
        ready.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        validate_saved(read_json(ready), root, campaign)
        os.replace(stage, out)
        return out / READY_NAME
    except Exception:
        if stage.exists():
            import shutil
            shutil.rmtree(stage, ignore_errors=True)
        raise


def verify(root: Path, campaign: Path, proof: Path) -> dict[str, Any]:
    value = read_json(proof / READY_NAME)
    validate_saved(value, root, campaign)
    return value


def relative_artifact(proof_ready: Path, path: Path, role: str) -> dict[str, Any]:
    require(path.is_file(), f"overlay artifact is missing: {role}")
    relative = os.path.relpath(path.resolve(), proof_ready.parent.resolve()).replace("\\", "/")
    value = stamp(path)
    return {"role": role, "path": relative, "bytes": value["bytes"], "sha256": value["sha256"]}


def build_overlay(root: Path, campaign: Path, proof: Path, out: Path) -> Path:
    saved = verify(root, campaign, proof)
    require(not out.exists(), f"refusing existing overlay root: {out}")
    base = saved["campaign"]["contract"]
    evidence_refs = [
        str((proof / READY_NAME).resolve()),
        str((root / EVIDENCE_RELATIVE / "preregistration.md").resolve()),
        str((root / "reverse-engineering/binary-analysis/pc-demo-retail-virtual-target-map-2026-08-11.tsv").resolve()),
        str((root / "reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv").resolve()),
    ]
    row = dict(base)
    row.update({
        "contractState": "RUNTIME_CANDIDATE_NEEDS_REFUTER",
        "semanticGrade": "C2_BOUNDED_RUNTIME",
        "receiver": "7,513 observed call-entry pairs across two retained traces; 21+50 session-local receivers; call EDX was strict CRound vtable 0x005de82c and call ECX=ESI continued unchanged into entry ECX",
        "inputs": "receiver-only inherited actor slot-66 dispatch observed at 0x00401aea; raw call/entry registers and 64 stack bytes retained; no explicit semantic argument established",
        "returns": "7,513 raw callbacks at RET 0x004d9904: 7,204 gap-free paired envelopes and 309 raw orphan returns across continuity barriers; void function, so raw EAX is not a semantic return",
        "writes": "not measured; no receiver field-write or branch-specific state claim",
        "sideEffects": "runtime proves entry into the pristine 2,757-byte body; static body contains calls to CActor::Move and the 0x004d9f30 effect helper, but their conditional effects are not isolated here",
        "preconditions": "the named complete Level 522 and Level 741 retained retail trace windows, replayed once for discovery and once with exact counts",
        "failureModes": "CMissile-style placement, other CRound populations, receiver writes, branch ordering, contact/lifetime behavior, and semantic return values remain open",
        "authorVerdict": "SUPPORTED_BY_PRISTINE_SLOT66_STATIC_JOIN_AND_TWO_INDEPENDENT_TTD_TRACE_SESSIONS",
        "runtimeVerdict": "MEASURED_BOUNDED_STRICT_CROUND_SLOT66_CALL_ENVELOPE",
        "refuterVerdict": "UNSCORED",
        "questionIds": QUESTION_ID,
        "evidenceRefs": ";".join(evidence_refs),
        "cheapestFalsifier": "Replay one retained trace that enters 0x004d8e40 with call EDX other than 0x005de82c or whose call ECX differs from entry ECX.",
        "rebuildOwner": "rebuild/OnslaughtRebuild.Core/Level100ActorWeaponRuntime.cs",
        "rebuildImplementation": "Level100ActorMechanics.AdvanceActorRounds / SteerSeekingRound",
        "parityTests": "Level100ActorWeaponTests.ForsetiMissile_HomesOnAMovingTarget",
        "rebuildState": "PARTIAL_CONTRACT",
        "remainingUncertainty": "receiver writes and branch ordering; CMissile-style runtime placement; complete contact/lifetime/effect behavior; original shipped symbol spelling; broader round population; full rebuild parity",
        "lastMeasurementDate": "2026-08-12",
        "scopeKind": "EXISTING_TTD_TWO_TRACE_STRICT_CROUND_SLOT66_CALL_ENTRY_RETURN_ENVELOPE",
        "payloadSha256": "",
        "receiverVtable": "0x005de82c",
        "observedCallVas": "0x00401aea",
        "controlSummary": "Level 522 poison required 232 calls/entries/returns versus 231 observed; exit 10, expectation/pairing/collector gates false, no READY, observation projection unchanged",
        "runtimeEvidenceSha256": ";".join(
            saved["inputs"][f"{lane}/call-context.jsonl"]["sha256"]
            for lane in ("level522-exact-v1", "level741-holdout-exact-v1")
        ),
        "baseContractId": CONTRACT_ID,
        "questionIdsAddressed": QUESTION_ID,
    })
    out.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))
    try:
        ledger = stage / "runtime-contracts.tsv"
        write_tsv(ledger, [row])
        artifacts = [
            relative_artifact(proof / READY_NAME, Path(__file__).resolve(), "proof-author"),
            relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / "preregistration.md", "preregistration"),
            relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / "level522-discovery-v1/call-context.jsonl", "runtime-level522-discovery"),
            relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / "level522-exact-v1/call-context.jsonl", "runtime-level522-exact"),
            relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / "level741-holdout-discovery-v1/call-context.jsonl", "runtime-level741-discovery"),
            relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / "level741-holdout-exact-v1/call-context.jsonl", "runtime-level741-exact"),
            relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / "level522-poison-232-v1/call-context.jsonl", "poison-level522"),
            relative_artifact(proof / READY_NAME, root / "reverse-engineering/binary-analysis/pc-demo-retail-virtual-target-map-2026-08-11.tsv", "static-demo-retail-map"),
            relative_artifact(proof / READY_NAME, root / "reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv", "static-c1-closure"),
            relative_artifact(proof / READY_NAME, root / "reverse-engineering/binary-analysis/ghidra-function-name-table-2026-07-27.tsv", "static-name-table"),
            relative_artifact(proof / READY_NAME, root / "rebuild/OnslaughtRebuild.Core/Level100ActorWeaponRuntime.cs", "rebuild-owner"),
            relative_artifact(proof / READY_NAME, root / "rebuild/OnslaughtRebuild.Core.Tests/Level100ActorWeaponTests.cs", "rebuild-test"),
        ]
        receipt = {
            "schema": OVERLAY_SCHEMA,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "sourceCampaign": {
                "path": str(campaign.resolve()),
                "ready": stamp(campaign / "campaign.ready.json"),
                "specimen": read_json(campaign / "campaign.ready.json")["sourceSnapshot"]["specimen"],
            },
            "inputContract": stamp(proof / READY_NAME),
            "artifacts": artifacts,
            "authorVerification": {"checks": saved["selftest"], "claimBoundary": saved["claimBoundary"]},
            "count": 1,
            "policy": {
                "namesAuthorized": False,
                "ghidraMutationAuthorized": False,
                "promotionAuthorized": False,
                "requiresRefuter": True,
                "maximumImportedGrade": "C2_BOUNDED_RUNTIME",
                "artifactClaimsParsed": True,
                "runtimeExecutableRelationValidated": True,
            },
            "output": {**stamp(ledger), "path": ledger.name},
        }
        (stage / "runtime-contracts.ready.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        os.replace(stage, out)
        return out / "runtime-contracts.ready.json"
    except Exception:
        if stage.exists():
            import shutil
            shutil.rmtree(stage, ignore_errors=True)
        raise


def overlay_subject(overlay: Path) -> dict[str, Any]:
    rows = read_tsv(overlay / "runtime-contracts.tsv")
    require(len(rows) == 1, "overlay row count differs")
    row = rows[0]
    canonical = json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "schema": REFUTER_SUBJECT_SCHEMA,
        "baseContractId": row["baseContractId"],
        "entityKey": row["entityKey"],
        "overlayReadySha256": sha256_file(overlay / "runtime-contracts.ready.json"),
        "questionIdsAddressed": [value for value in row["questionIdsAddressed"].split(";") if value],
        "candidateRowSha256": sha256_bytes(canonical),
    }


def build_finding(root: Path, proof: Path, overlay: Path, out: Path) -> Path:
    read_json(proof / READY_NAME)
    subject = overlay_subject(overlay)
    prereg = "local-lab/cround-move-existing-trace-20260812-v1/preregistration.md"
    finding = {
        "schemaVersion": 1,
        "id": "cround-slot66-strict-receiver-envelope-2026-08-12",
        "title": "CRound slot-66 strict receiver placement and call envelope in two retained traces",
        "date": "2026-08-12",
        "lane": "ttd/existing-trace",
        "author": "recursive RE campaign",
        "sourceNote": str((proof / READY_NAME).resolve()),
        "findingKind": "instrument-derived",
        "claim": {
            "statement": "In the named Level 522 and Level 741 traces, all 7,513 call-entry pairs at 0x00401AEA targeted 0x004D8E40 with strict CRound vtable 0x005DE82C and unchanged receiver continuity.",
            "grade": "EXECUTED",
            "mechanism": ["cround.slot66.strict_receiver_envelope"],
        },
        "scope": {
            "population": "slot-66 calls to 0x004D8E40 in the complete named Level 522 and Level 741 retained traces",
            "covered": "231 Level 522 and 7,282 Level 741 call-entry pairs, with 7,204 gap-free paired returns plus 309 raw orphan return callbacks",
            "notCovered": [
                "CMissile-style receiver placement",
                "round populations outside the two named trace sessions",
                "receiver field writes and branch-specific ordering",
                "complete movement, collision, lifetime, and effect semantics",
                "original shipped source spelling and complete rebuild parity",
            ],
        },
        "rivals": [
            {
                "id": "rival-cmissile-placement",
                "statement": "The shared 0x004D8E40 body was reached through the CMissile-style vtable placement rather than strict CRound placement.",
                "indistinguishableOn": ["entry coverage at 0x004D8E40", "the shared static slot-66 target"],
                "discriminator": {
                    "description": "read raw EDX at every inherited slot-66 indirect call",
                    "mechanism": ["cround.slot66.receiver_placement"],
                    "expectedUnderClaim": "EDX is strict CRound vtable 0x005DE82C",
                    "expectedUnderRival": "EDX is CMissile-style vtable 0x005E3BA4",
                    "status": "observed",
                    "outcome": "claim",
                    "evidenceRef": ["e-level522", "e-level741"],
                },
            },
            {
                "id": "rival-receiver-substitution",
                "statement": "The indirect caller's apparent CRound object was replaced or adjusted before the target body entered.",
                "indistinguishableOn": ["the call target address", "entry coverage without register context"],
                "discriminator": {
                    "description": "compare call ECX and ESI with entry ECX and ESI for each paired invocation",
                    "mechanism": ["cround.slot66.receiver_continuity"],
                    "expectedUnderClaim": "call ECX equals call ESI equals entry ECX equals entry ESI",
                    "expectedUnderRival": "at least one paired invocation changes or adjusts the receiver",
                    "status": "observed",
                    "outcome": "claim",
                    "evidenceRef": ["e-level522", "e-level741"],
                },
            },
        ],
        "predictions": [
            {
                "id": "p-level741-holdout-placement",
                "statement": "The independent Level 741 holdout will reproduce Level 522 strict-CRound receiver placement.",
                "procedure": "replay the complete retained Level 741 trace with the preregistered slot-66 target and inspect call/entry registers",
                "expected": "every call has EDX 0x005DE82C and unchanged ECX/ESI receiver continuity into entry",
                "wouldFalsifyIf": "any call uses another vtable or any paired entry changes the receiver",
                "predictedInAdvance": True,
                "statedAt": prereg,
                "result": "match",
                "observed": "7,282 Level 741 calls all used EDX 0x005DE82C; every call ECX/ESI matched entry ECX/ESI",
                "evidenceRef": ["e-level741"],
            },
            {
                "id": "p-level741-return-envelope",
                "statement": "The Level 741 holdout will reproduce the 0x004D9904 raw return site while preserving honest continuity-barrier orphans.",
                "procedure": "collect raw returns and independently score gap-free invocation associations over the complete Level 741 replay",
                "expected": "all raw callbacks decode RET at 0x004D9904, with paired and explicitly orphaned counts summing to all calls",
                "wouldFalsifyIf": "a raw return lands outside 0x004D9904 or paired plus orphaned counts do not account for the calls",
                "predictedInAdvance": True,
                "statedAt": prereg,
                "result": "match",
                "observed": "7,282 raw callbacks decoded RET at 0x004D9904; 6,987 paired plus 295 orphaned equals 7,282",
                "evidenceRef": ["e-level741"],
            },
        ],
        "evidence": [
            {
                "id": "e-level522", "grade": "EXECUTED",
                "instrument": "hash-pinned TTD schema-v3 call-context replay",
                "summary": "231 strict-CRound call-entry pairs; 217 gap-free returns and 14 raw orphan returns; 21 session-local receivers",
                "sample": {"n": 231, "units": "slot-66 call-entry pairs", "independentReplicates": 1, "sessions": 1},
                "specimen": {"path": RUNS["level522-exact-v1"]["trace"][0], "sha256": RUNS["level522-exact-v1"]["trace"][2]},
            },
            {
                "id": "e-level741", "grade": "EXECUTED",
                "instrument": "hash-pinned TTD schema-v3 call-context replay",
                "summary": "7,282 strict-CRound call-entry pairs; 6,987 gap-free returns and 295 raw orphan returns; 50 session-local receivers",
                "sample": {"n": 7_282, "units": "slot-66 call-entry pairs", "independentReplicates": 1, "sessions": 1},
                "specimen": {"path": RUNS["level741-holdout-exact-v1"]["trace"][0], "sha256": RUNS["level741-holdout-exact-v1"]["trace"][2]},
            },
        ],
        "residuals": [
            {"id": "res-writes-branches", "statement": "No receiver field writes or branch-specific ordering were measured.", "mechanism": ["cround.move.writes_and_branches"], "blocksClaim": False},
            {"id": "res-cmissile-population", "statement": "Neither trace supplied a CMissile-style receiver, so its runtime behavior remains unobserved.", "mechanism": ["cmissile.runtime_population"], "blocksClaim": False},
            {"id": "res-full-semantics", "statement": "The bounded envelope does not establish complete movement, collision, lifetime, effect, or return-value semantics.", "mechanism": ["cround.move.complete_semantics"], "blocksClaim": False},
            {"id": "res-source-parity", "statement": "Original shipped symbol spelling and complete reconstruction parity remain open.", "mechanism": ["cround.source_and_rebuild_scope"], "blocksClaim": False},
        ],
        "poisonControl": {
            "id": "control-level522-expected-232",
            "kind": "poison",
            "description": "the Level 522 target falsely requires 232 calls, entries, and returns although the retained trace contains 231",
            "predictedOutcome": "collector exits nonzero, fails expectation/pairing/collector gates, and publishes no READY without changing observations",
            "observedOutcome": "exit 10; expectation, pairing, and collector checks false; no READY; observation projection identical",
            "result": "failed_as_predicted",
        },
        "overturnedBy": [
            {"id": "kill-vtable-placement", "procedure": "replay another hash-pinned trace and observe a 0x004D8E40 call whose EDX is not 0x005DE82C", "wouldShow": "the strict-CRound placement does not extend to that call population", "cost": "one bounded retained-trace replay"},
            {"id": "kill-receiver-continuity", "procedure": "capture one paired dispatcher call and entry where call ECX/ESI differs from entry ECX/ESI", "wouldShow": "the inherited dispatcher adjusts or substitutes the receiver", "cost": "one schema-v3 call-context replay"},
        ],
        "subject": subject,
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    require(not out.exists(), f"refusing existing finding: {out}")
    out.write_text(json.dumps(finding, indent=2) + "\n", encoding="utf-8")
    return out


def evidence_ref(adjudication: Path, artifact: Path, role: str) -> dict[str, Any]:
    relative = os.path.relpath(artifact.resolve(), adjudication.parent.resolve()).replace("\\", "/")
    return {"role": role, "path": relative, "sha256": sha256_file(artifact)}


def build_adjudication(campaign: Path, overlay: Path, finding: Path, result: Path, out: Path) -> Path:
    refuter = read_json(result)
    require(refuter.get("tool") == "tools/probe/refute.py" and refuter.get("verdict") == "SURVIVED", "refuter did not survive")
    require(refuter.get("subject") == overlay_subject(overlay), "refuter subject differs")
    measured = datetime.now(timezone.utc).isoformat()
    value = {
        "schema": ADJUDICATION_SCHEMA,
        "baseCampaignReadySha256": sha256_file(campaign / "campaign.ready.json"),
        "overlayReadySha256": sha256_file(overlay / "runtime-contracts.ready.json"),
        "decision": {
            "baseContractId": CONTRACT_ID,
            "questionIdsAddressed": [QUESTION_ID],
            "refuterVerdict": "SURVIVED",
            "refuterEvidence": [
                evidence_ref(out, finding, "refuter-finding"),
                evidence_ref(out, result, "refuter-result"),
            ],
            "terminalState": "",
            "measuredAtUtc": measured,
            "remainingUncertainty": "The strict-CRound slot-66 call envelope is measured, but receiver writes, branch ordering, CMissile-style runtime placement, complete contact/lifetime/effect behavior, original source spelling, broader populations, and full rebuild parity remain open.",
            "nextQuestions": [
                {
                    "questionType": "CROUND_MOVE_RUNTIME_WRITES_AND_BRANCHES",
                    "question": "Which receiver fields and external state does 0x004D8E40 change, in what order, across seeking, non-seeking, contact, and lifetime branches?",
                    "recommendedInstrument": "TTD_BRANCH_AND_DATA_WRITE_ENVELOPE_ON_EXISTING_TRACES",
                    "cheapestFalsifier": "Capture one gap-accounted entry-to-return invocation with preregistered receiver-field watches and compare the changed offsets to the static branch path.",
                    "requiresElevation": False,
                    "priority": 1,
                    "score": 650.0,
                    "source": "CRound slot-66 Gen21 adjudication",
                    "currentOwner": "recursive-re-campaign",
                },
                {
                    "questionType": "CMISSILE_SLOT66_RUNTIME_PLACEMENT",
                    "question": "When does the shared 0x004D8E40 body execute through CMissile-style vtable 0x005E3BA4, and does its observed envelope differ from strict CRound placement?",
                    "recommendedInstrument": "EXISTING_TRACE_SEARCH_THEN_TARGETED_SAFE_COPY_IF_ABSENT",
                    "cheapestFalsifier": "Find one call at 0x00401AEA with EDX 0x005E3BA4 and bind its call/entry/return receiver envelope.",
                    "requiresElevation": False,
                    "priority": 2,
                    "score": 600.0,
                    "source": "CRound slot-66 Gen21 adjudication",
                    "currentOwner": "recursive-re-campaign",
                },
            ],
            "rebuildMapping": {
                "rebuildOwner": "rebuild/OnslaughtRebuild.Core/Level100ActorWeaponRuntime.cs",
                "rebuildImplementation": "Level100ActorMechanics.AdvanceActorRounds / SteerSeekingRound",
                "parityTests": "Level100ActorWeaponTests.ForsetiMissile_HomesOnAMovingTarget",
                "rebuildState": "PARTIAL_CONTRACT",
            },
            "supersessions": [],
        },
    }
    require(not out.exists(), f"refusing existing adjudication: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=repository_root())
    parser.add_argument("--campaign", type=Path)
    commands = parser.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build")
    build_parser.add_argument("--out", type=Path, required=True)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--proof", type=Path, required=True)
    commands.add_parser("selftest")
    overlay_parser = commands.add_parser("overlay")
    overlay_parser.add_argument("--proof", type=Path, required=True)
    overlay_parser.add_argument("--out", type=Path, required=True)
    finding_parser = commands.add_parser("finding")
    finding_parser.add_argument("--proof", type=Path, required=True)
    finding_parser.add_argument("--overlay", type=Path, required=True)
    finding_parser.add_argument("--out", type=Path, required=True)
    adjudication_parser = commands.add_parser("adjudication")
    adjudication_parser.add_argument("--overlay", type=Path, required=True)
    adjudication_parser.add_argument("--finding", type=Path, required=True)
    adjudication_parser.add_argument("--result", type=Path, required=True)
    adjudication_parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    root = args.repo.resolve()
    campaign = (args.campaign or root / CAMPAIGN_RELATIVE).resolve()
    try:
        if args.command == "build":
            path = build(root, campaign, args.out)
            print(f"CROUND_MOVE_RUNTIME_PROOF_READY {stamp(path)}")
        elif args.command == "verify":
            value = verify(root, campaign, args.proof.resolve())
            print(f"CROUND_MOVE_RUNTIME_PROOF_VERIFIED verdict={value['verdict']} calls={value['runtime']['exactReplayCalls']}")
        elif args.command == "selftest":
            value = selftest(root, campaign)
            print(f"CROUND_MOVE_RUNTIME_SELFTEST_OK attacks={value['count']}")
        elif args.command == "overlay":
            path = build_overlay(root, campaign, args.proof.resolve(), args.out.resolve())
            print(f"CROUND_MOVE_RUNTIME_OVERLAY_READY {stamp(path)}")
        elif args.command == "finding":
            path = build_finding(root, args.proof.resolve(), args.overlay.resolve(), args.out.resolve())
            print(f"CROUND_MOVE_RUNTIME_FINDING_READY {stamp(path)}")
        else:
            path = build_adjudication(campaign, args.overlay.resolve(), args.finding.resolve(), args.result.resolve(), args.out.resolve())
            print(f"CROUND_MOVE_RUNTIME_ADJUDICATION_READY {stamp(path)}")
        return 0
    except (ProofError, OSError, ValueError, KeyError, struct.error) as exc:
        print(f"CROUND_MOVE_RUNTIME_REFUSED: {exc}", file=os.sys.stderr)
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
