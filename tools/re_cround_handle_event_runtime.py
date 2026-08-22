#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Prove and package the bounded CRound shared slot-0 event-routing envelope.

This proof is read-only. It reparses two retained TTD recordings, their
discovery/exact replay pairs, and one deliberately poisoned replay. It joins
the observed call, receiver, event-pointer, selected-arm, and return envelopes
to pristine bytes and the Generation 21 frontier. It does not assign arm
effects, claim event 4002 was executed, extend the observation to the shared
CMissile-style placement, promote an original symbol spelling, or claim rebuild
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


SCHEMA = "bea.re.cround-handle-event-runtime-proof.v1"
READY_NAME = "proof.ready.json"
CLAIM = "CROUND_SHARED_SLOT0_STRICT_RECEIVER_EVENT_ROUTING_ENVELOPE_C2_BOUNDED"
OVERLAY_SCHEMA = "bea.re.runtime-contract-overlay.v1"
ADJUDICATION_SCHEMA = "bea.re.runtime-contract-adjudication.v1"
REFUTER_SUBJECT_SCHEMA = "bea.re.refuter-subject.v1"

SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
RUNTIME_SHA256 = "e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4"
ENTITY_KEY = (
    "CODE:" + SPECIMEN_SHA256
    + ":VA=0x004d9910:RANGES=e285cbff91ced5bc10d7ba635f1f46c107615698ebd98d46c299c22bea5666b3"
)
CONTRACT_ID = "C-ff8b9307fccfd0ac"
QUESTION_ID = "Q-96638757ab82dce0"
CURRENT_NAME = "VFuncSlot_00_004d9910"

EVIDENCE_RELATIVE = Path("local-lab/cround-handle-event-existing-trace-20260812-v1")
CAMPAIGN_RELATIVE = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-21-cround-move-runtime-v1"
)
CAMPAIGN_READY_SHA256 = "9699d0b55dc19c3dc88ba94341e0e76c000a8835d749e9d307ed063a2cb50158"
CAMPAIGN_REDUCER_ID = "b67132c21e683c4566cc3938275ef98b68c20a7d4759f91ab1fc0eea3f74f95e"
CAMPAIGN_AUTHORITY = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-21-cround-move-runtime-authority.ready.json"
)
CAMPAIGN_AUTHORITY_STAMP = (
    14_948,
    "331db4093dd7f94e7a2d8d50dedc21dc814d98d1ac2d937b493994d6740c6a96",
)

ENTRY = 0x004D9910
END_EXCLUSIVE = 0x004D9D46
BODY_SHA256 = "d54da932205b40f631e650c2f3902faa230f69c1efe029c428aff1305cff2c2b"
CALL_SITE = 0x0044B68A
FALLTHROUGH = 0x0044B68C
RETURN_SITE = 0x004D9D43
CROUND_VTABLE = 0x005DE82C
CMISSILE_VTABLE = 0x005E3BA4
ARM_ENTRIES = {
    1: 0x004D9A54,
    2: 0x004D997E,
    3: 0x004D995E,
    4: 0x004D9951,
    5: 0x004D9D23,
}
ARM_RANGES = {
    0: [
        {"rva_start": "0xD9910", "rva_end_exclusive": "0xD9951"},
        {"rva_start": "0xD9965", "rva_end_exclusive": "0xD997E"},
        {"rva_start": "0xD9984", "rva_end_exclusive": "0xD9A54"},
        {"rva_start": "0xD9A5A", "rva_end_exclusive": "0xD9D23"},
        {"rva_start": "0xD9D2B", "rva_end_exclusive": "0xD9D46"},
    ],
    1: [{"rva_start": "0xD9A54", "rva_end_exclusive": "0xD9A5A"}],
    2: [{"rva_start": "0xD997E", "rva_end_exclusive": "0xD9984"}],
    3: [{"rva_start": "0xD995E", "rva_end_exclusive": "0xD9965"}],
    4: [{"rva_start": "0xD9951", "rva_end_exclusive": "0xD995E"}],
    5: [{"rva_start": "0xD9D23", "rva_end_exclusive": "0xD9D2B"}],
}

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
    "preregistration.md": (3_312, "9857afbad53f7c765383d186aacba48ea20c0b9bd8c0b756b577dfb9de393a12"),
    "preregistration-amendment-1.md": (1_177, "f7f13b5643bea5b42452b7bd8fd100c9841318d4c472e9864e7e0b9f95716325"),
    "preregistration-amendment-2.md": (1_217, "ebab6aff0b5ee029718ff5f70f79e53a882310a52e30d15f5f0afb968d60c0d2"),
    "preregistration-amendment-3.md": (1_308, "b6d3e28245279361e3d9fb976db5773e9679b21ec11a8db676d4834206e8fb52"),
    "discovery-result-freeze.md": (1_839, "51fae9c5fb3d81df96b5bcc28967d5f7285dc7a8729878ddec2ec8dbd18c4472"),
    "holdout-preregistration.md": (1_725, "e0d5bc40090356d8dd5f2743c2c26c67e1e3970b7b435fd81bca27591c27f0ed"),
    "holdout-result-freeze.md": (1_274, "c1abee483719495f091c77358941fab3d0007ffb96dd09ff8c78806a023a3e91"),
    "targets-discovery-v2.tsv": (416, "9c8928b5132a6dfca2fd4966a325ab2746797a5c951533909fcb97b1052674bb"),
    "targets-level521-exact.tsv": (497, "976ef8c4105b19b30359adee792cf65eb219ed3c5f4a54e02db670703fd10fda"),
    "targets-level521-poison-2532.tsv": (497, "5cfa33ee6632f6cf021573ff0270910a88e3fa2101fc521d04dfb6d1c52327ee"),
    "targets-level512-exact.tsv": (462, "ac3b6bd371fd5cafae66f051d47048e176a9dcc4125586641c16a45ae6094566"),
    "level521-take4-discovery-v4/READY": (585, "60a3ba2f147860fd92e2431eb9a4bfd3f6ee628c1bfb5c3d74e0ea72576842ff"),
    "level521-take4-discovery-v4/receipt.json": (7_896, "98fcc0115775ab3f80759ab24e12d46ebb7a785ce5a3801a4eb52682fc42d51f"),
    "level521-take4-discovery-v4/manifest.json": (4_067, "cf23e312fe8281f56ff743e04a931884c8e312088637fb8721716bf533a29dae"),
    "level521-take4-discovery-v4/call-context.jsonl": (12_502_701, "f67e613a27012c89253451a19ea46685745f31db04c6c6cacd3925dd27ea3f7e"),
    "level521-take4-discovery-v4/targets.tsv": (416, "9c8928b5132a6dfca2fd4966a325ab2746797a5c951533909fcb97b1052674bb"),
    "level521-take4-exact-v1/READY": (581, "c371b516df720eaa5481b96093ee8b2592e7aab612ebf135f15ea56600e48530"),
    "level521-take4-exact-v1/receipt.json": (7_871, "88c1a07f19f4e69adec902d02914474f291294f6f225e271e2d4b1a8fa984e2d"),
    "level521-take4-exact-v1/manifest.json": (4_039, "870a63389fcc27fbea75c2718007a89f84bb8d5e45b9843614006727eb975e5a"),
    "level521-take4-exact-v1/call-context.jsonl": (12_502_694, "caf6dbd35edaccfd351b8ffe423691a0120e39c990afdbe17bcf163e0928016f"),
    "level521-take4-exact-v1/targets.tsv": (497, "976ef8c4105b19b30359adee792cf65eb219ed3c5f4a54e02db670703fd10fda"),
    "level521-take4-poison-2532-v1/receipt.json": (7_925, "40ef35430db84e37aa2c047ae869b9eb3d3610edb199d82854ee9d675ba3d996"),
    "level521-take4-poison-2532-v1/manifest.json": (4_090, "f168a22b47a56b00e7114370c27aae80fa65dceaced8914dfcf97069883b3c48"),
    "level521-take4-poison-2532-v1/call-context.jsonl": (12_502_704, "688b99afee79a0dbc672d73819dd33a75b48135d5f18f834d8a44405b962ca32"),
    "level521-take4-poison-2532-v1/targets.tsv": (497, "5cfa33ee6632f6cf021573ff0270910a88e3fa2101fc521d04dfb6d1c52327ee"),
    "level512-holdout-discovery-v1/READY": (587, "3adbe7bbd5b126d0b18bbc262b3f2faa5dbeb60c5bb9c4815862645ff03c6bed"),
    "level512-holdout-discovery-v1/receipt.json": (7_833, "c2809a04cb800aa4ae71e886e788c4e2457345e754a6c2c398df602fb671807e"),
    "level512-holdout-discovery-v1/manifest.json": (4_066, "0fa6a1769b7db681ed79bd5865f2c9ca80182ca7d58d4e547a0b7460784751a8"),
    "level512-holdout-discovery-v1/call-context.jsonl": (125_134, "76fad30470285cd492d45a3fb15ce4e05701c21c7e8824dfaae187e7d9bd0064"),
    "level512-holdout-discovery-v1/targets.tsv": (416, "9c8928b5132a6dfca2fd4966a325ab2746797a5c951533909fcb97b1052674bb"),
    "level512-holdout-exact-v1/READY": (583, "853b86a57e3242a004154d4ebed569719de7b348afa51f1480174ba051e76eb0"),
    "level512-holdout-exact-v1/receipt.json": (7_807, "9b2bbf360751027c5e1b6e4a95404e365e1820ae29516ddda3598f5d0b79c886"),
    "level512-holdout-exact-v1/manifest.json": (4_038, "d4566d9175db081b7fbdefac839c312836a8245b9c817b975356781e3e3d1cf6"),
    "level512-holdout-exact-v1/call-context.jsonl": (125_116, "650b1dc07d32065261eea367170ad8966e86e895e3316862f99c8ad1a1b637c5"),
    "level512-holdout-exact-v1/targets.tsv": (462, "ac3b6bd371fd5cafae66f051d47048e176a9dcc4125586641c16a45ae6094566"),
}

REPO_PINS: dict[str, tuple[int, str]] = {
    "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup": (2_506_752, SPECIMEN_SHA256),
    "local-lab/safe-copy-bea-pristine/BEA.exe": (2_506_752, RUNTIME_SHA256),
    "reverse-engineering/binary-analysis/pc-demo-retail-virtual-target-map-2026-08-11.tsv": (1_204_103, "ba2db0551beeed458ea6265b87d1a5cf93bc2dd2c464da3f7f0c6702a4d4c750"),
    "reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv": (3_288_437, "cfe90af382269cb2e64996d10df7777bd00fcd8e1844b9823ef74bc6199b8974"),
    "reverse-engineering/binary-analysis/ghidra-function-name-table-2026-07-27.tsv": (475_327, "44f49ca1ccb326b5fb425e1639b6a0650565d7567a6afae96f28414aa9e68b11"),
    "rebuild/OnslaughtRebuild.Core/Level100ActorWeaponRuntime.cs": (32_010, "8f8692250e70eea6bea0702dfd56d1c3c90ad17dd8dffd65acf639cec4ba6197"),
    "rebuild/OnslaughtRebuild.Core.Tests/Level100ActorWeaponTests.cs": (17_484, "cb64be81481a0d6712a13d7f7a16449974d38ba047617444b6f96c9d024c2bfc"),
    "tools/Invoke-TtdCallContextV2.ps1": (91_832, "0017181805a38cebfa82cd0ddd802aa7a23f06fda39f03ecc201729e4ad185d7"),
    "tools/ttd_pipeline_contract_tests.py": (203_517, "5b577e04e441b822b3bb30287f53402fb0be606b57a2078e8fde62f05e56c2b4"),
}

RUNS: dict[str, dict[str, Any]] = {
    "level521-take4-discovery-v4": {
        "trace": ("G:\\bea-ttd\\level521-native-20260802-0018-take4\\level521-native-20260802-0018-take4.run", 14_214_496_256, "45ab04297f32bb27ac0c80e8ecb0b332e666a9955caea0763a83984affb74ac2"),
        "to": "0x1EAB39:0x270F", "calls": 2_531, "arms": (114, 3, 0, 75, 2_339),
        "gapFree": 1_960, "orphans": 571, "receivers": 40, "eventPointers": 412,
        "eventIds": {4000: 114, 4001: 3, 4003: 75, 3000: 2_178, 2000: 161},
        "exact": False, "projection": "fd8ab7d0854d8c1caa63175acd76356d8b0ca50ae54c7bb66967f524a1e574fc",
    },
    "level521-take4-exact-v1": {
        "trace": ("G:\\bea-ttd\\level521-native-20260802-0018-take4\\level521-native-20260802-0018-take4.run", 14_214_496_256, "45ab04297f32bb27ac0c80e8ecb0b332e666a9955caea0763a83984affb74ac2"),
        "to": "0x1EAB39:0x270F", "calls": 2_531, "arms": (114, 3, 0, 75, 2_339),
        "gapFree": 1_960, "orphans": 571, "receivers": 40, "eventPointers": 412,
        "eventIds": {4000: 114, 4001: 3, 4003: 75, 3000: 2_178, 2000: 161},
        "exact": True, "projection": "fd8ab7d0854d8c1caa63175acd76356d8b0ca50ae54c7bb66967f524a1e574fc",
    },
    "level512-holdout-discovery-v1": {
        "trace": ("G:\\bea-ttd\\level-opening-3m-v1-level512\\level-opening-3m-v1-level512.run", 6_031_409_152, "3d3a118fe211ead7b1e41055e4150dcff576b6d0cc64879c52d1163beca94808"),
        "to": "0x1ED069:0xEA7", "calls": 24, "arms": (6, 0, 0, 0, 18),
        "gapFree": 12, "orphans": 12, "receivers": 6, "eventPointers": 18,
        "eventIds": {4000: 6, 3000: 12, 2000: 6},
        "exact": False, "projection": "b47a0533bc5abe787771ed2c411c1e68a4c0b78d672f7aee0741a607c7170543",
    },
    "level512-holdout-exact-v1": {
        "trace": ("G:\\bea-ttd\\level-opening-3m-v1-level512\\level-opening-3m-v1-level512.run", 6_031_409_152, "3d3a118fe211ead7b1e41055e4150dcff576b6d0cc64879c52d1163beca94808"),
        "to": "0x1ED069:0xEA7", "calls": 24, "arms": (6, 0, 0, 0, 18),
        "gapFree": 12, "orphans": 12, "receivers": 6, "eventPointers": 18,
        "eventIds": {4000: 6, 3000: 12, 2000: 6},
        "exact": True, "projection": "b47a0533bc5abe787771ed2c411c1e68a4c0b78d672f7aee0741a607c7170543",
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


def signed32(value: int) -> int:
    return value - 0x1_0000_0000 if value & 0x8000_0000 else value


def stack_pair(event: dict[str, Any], lane: str, role: str) -> tuple[int, int]:
    value = event.get("stack", {})
    require(value.get("query_valid") is True and as_int(value.get("valid_bytes")) >= 8, f"{lane} {role} stack unavailable")
    raw = bytes.fromhex(str(value.get("hex", "")))
    require(len(raw) >= 8, f"{lane} {role} stack bytes are short")
    return struct.unpack_from("<II", raw)


def observation_projection(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [copy.deepcopy(row) for row in rows if row.get("kind") in {"event", "invocation", "gap-summary"}]


def projection_sha256(rows: list[dict[str, Any]]) -> str:
    value = json.dumps(observation_projection(rows), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(value)


def one_kind(rows: list[dict[str, Any]], kind: str, lane: str) -> dict[str, Any]:
    matches = [row for row in rows if row.get("kind") == kind]
    require(len(matches) == 1, f"{lane} {kind} cardinality differs")
    return matches[0]


def validate_targets(rows: list[dict[str, Any]], lane: str, spec: dict[str, Any]) -> None:
    targets = [row for row in rows if row.get("kind") == "target"]
    require(len(targets) == 6, f"{lane} target count differs")
    by_index = {as_int(row["target_index"]): row for row in targets}
    require(set(by_index) == set(range(6)), f"{lane} target indexes differ")
    counts = [spec["calls"], *spec["arms"]]
    entries = [ENTRY, *ARM_ENTRIES.values()]
    for index in range(6):
        target = by_index[index]
        observed = counts[index]
        require(as_int(target["entry_va"]) == entries[index], f"{lane} target {index} entry differs")
        require(target.get("ranges") == ARM_RANGES[index], f"{lane} target {index} ranges differ")
        require(as_int(target["observed_entry_count"]) == observed, f"{lane} target {index} entry count differs")
        require(as_int(target["observed_call_count"]) == (spec["calls"] if index == 0 else 0), f"{lane} target {index} call count differs")
        require(as_int(target["observed_return_count"]) == (spec["calls"] if index == 0 else 0), f"{lane} target {index} return count differs")
        expected_entry = str(observed) if spec["exact"] else None
        expected_outer = str(spec["calls"]) if spec["exact"] and index == 0 else ("0" if spec["exact"] else None)
        require(target.get("expected_entry_count") == expected_entry, f"{lane} target {index} expected entry differs")
        require(target.get("expected_call_count") == expected_outer, f"{lane} target {index} expected call differs")
        require(target.get("expected_return_count") == expected_outer, f"{lane} target {index} expected return differs")
        require(target.get("expectations_passed") is True, f"{lane} target {index} expectations failed")


def validate_observations(rows: list[dict[str, Any]], lane: str, spec: dict[str, Any]) -> dict[str, Any]:
    calls = int(spec["calls"])
    gap_free = int(spec["gapFree"])
    orphans = int(spec["orphans"])
    metadata = one_kind(rows, "metadata", lane)
    summary = one_kind(rows, "summary", lane)
    one_kind(rows, "gap-summary", lane)
    validate_targets(rows, lane, spec)
    events = [row for row in rows if row.get("kind") == "event"]
    invocations = [row for row in rows if row.get("kind") == "invocation"]
    require(len(events) == calls * 4, f"{lane} event count differs")
    require(len(invocations) == calls * 2, f"{lane} invocation count differs")
    require(len(rows) == calls * 6 + 9, f"{lane} JSONL row count differs")
    require(metadata.get("schema") == "bea.ttd.call-context.v3", f"{lane} metadata schema differs")
    require(metadata.get("module_base") == "0x400000" and metadata.get("module_size") == "0x5D8000", f"{lane} module identity differs")
    require(metadata.get("requested_to") == spec["to"] and metadata.get("lifetime_max") == spec["to"], f"{lane} replay endpoint differs")
    require(metadata.get("replay_mode") == "sequential-all-segments" and metadata.get("stack_bytes_requested") == 64, f"{lane} collection mode differs")

    event_by_index: dict[int, dict[str, Any]] = {}
    for event in events:
        index = as_int(event["event_index"])
        require(index not in event_by_index, f"{lane} duplicate event index")
        event_by_index[index] = event
    require(set(event_by_index) == set(range(calls * 4)), f"{lane} event indexes differ")
    require(Counter((as_int(e["target_index"]), str(e["event_type"])) for e in events) == Counter(
        {(0, "call"): calls, (0, "entry"): calls, (0, "return"): calls,
         **{(index, "entry"): spec["arms"][index - 1] for index in range(1, 6)}}
    ), f"{lane} event role counts differ")

    outer_invocations = [row for row in invocations if as_int(row["target_index"]) == 0]
    arm_invocations = [row for row in invocations if as_int(row["target_index"]) != 0]
    require(len(outer_invocations) == calls and len(arm_invocations) == calls, f"{lane} invocation roles differ")
    arm_events: list[dict[str, Any]] = []
    for invocation in arm_invocations:
        require(invocation.get("grade") == "ENTRY_ONLY", f"{lane} arm invocation grade differs")
        require(invocation.get("call_event_index") is None and invocation.get("return_event_index") is None, f"{lane} arm invocation unexpectedly has call/return")
        require(invocation.get("call_entry_checks_passed") is False and invocation.get("return_checks_passed") is False, f"{lane} arm invocation checks differ")
        event = event_by_index[as_int(invocation["entry_event_index"])]
        require(event.get("event_type") == "entry" and as_int(event["target_index"]) == as_int(invocation["target_index"]), f"{lane} arm event binding differs")
        arm_events.append(event)

    receivers: set[int] = set()
    event_pointers: set[int] = set()
    grades: Counter[str] = Counter()
    referenced_returns: set[int] = set()
    outer: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]] = []
    for invocation in outer_invocations:
        require(invocation.get("schema") == "bea.ttd.call-context.v3", f"{lane} outer invocation schema differs")
        require(invocation.get("call_entry_checks_passed") is True, f"{lane} call-entry checks failed")
        call = event_by_index[as_int(invocation["call_event_index"])]
        entry = event_by_index[as_int(invocation["entry_event_index"])]
        require(call.get("event_type") == "call" and entry.get("event_type") == "entry", f"{lane} outer event roles differ")
        require(call.get("pc") == "0x44B68A" and as_int(call["instruction_target"]) == ENTRY and as_int(call["fallthrough"]) == FALLTHROUGH, f"{lane} slot-0 call differs")
        require(entry.get("pc") == "0x4D9910" and as_int(entry["instruction_target"]) == ENTRY, f"{lane} outer entry differs")
        require(entry.get("previous_position") == call.get("position"), f"{lane} call-entry ordering differs")
        require(call.get("unique_thread_id") == entry.get("unique_thread_id"), f"{lane} call-entry thread differs")
        for event, role in ((call, "call"), (entry, "entry")):
            require(event.get("integer_registers_valid") is True and event.get("register_views_agree") is True, f"{lane} {role} registers invalid")
        call_regs = call["registers"]
        entry_regs = entry["registers"]
        receiver = as_int(call_regs["ecx"])
        event_pointer = as_int(call_regs["eax"])
        require(as_int(call_regs["edx"]) == CROUND_VTABLE and as_int(entry_regs["edx"]) == CROUND_VTABLE, f"{lane} strict CRound vtable differs")
        require(as_int(call_regs["edx"]) != CMISSILE_VTABLE, f"{lane} CMissile-style placement observed")
        require(receiver == as_int(entry_regs["ecx"]), f"{lane} call-entry receiver differs")
        require(event_pointer == as_int(entry_regs["eax"]), f"{lane} call-entry event pointer differs")
        call_return, call_arg = stack_pair(call, lane, "call")
        entry_return, entry_arg = stack_pair(entry, lane, "entry")
        require((call_return, entry_return) == (FALLTHROUGH, FALLTHROUGH), f"{lane} caller return address differs")
        require(call_arg == entry_arg == event_pointer, f"{lane} stack event argument differs")
        require(call.get("sp") == entry.get("sp") and call["stack"]["hex"] == entry["stack"]["hex"], f"{lane} call-entry stack continuity differs")
        receivers.add(receiver)
        event_pointers.add(event_pointer)
        outer.append((invocation, call, entry))
        grade = str(invocation.get("grade"))
        grades[grade] += 1
        if grade == "CALL_ENTRY_RETURN":
            require(invocation.get("return_checks_passed") is True and invocation.get("return_event_index") is not None, f"{lane} paired return differs")
            return_index = as_int(invocation["return_event_index"])
            returned = event_by_index[return_index]
            require(returned.get("event_type") == "return" and returned.get("unique_thread_id") == call.get("unique_thread_id"), f"{lane} paired return binding differs")
            referenced_returns.add(return_index)
        elif grade == "CALL_ENTRY":
            require(invocation.get("return_checks_passed") is False and invocation.get("return_event_index") is None, f"{lane} orphan grade differs")
            require(
                invocation.get("continuity_break_crossed") is True
                or invocation.get("gap_crossed") is True,
                f"{lane} orphan lacks gap/continuity barrier",
            )
        else:
            raise ProofError(f"{lane} unsupported outer invocation grade: {grade}")
    require(grades == Counter({"CALL_ENTRY_RETURN": gap_free, "CALL_ENTRY": orphans}), f"{lane} outer grades differ")
    require(len(referenced_returns) == gap_free, f"{lane} paired return references differ")

    arm_by_thread: dict[str, list[dict[str, Any]]] = {}
    outer_by_thread: dict[str, list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]]] = {}
    for event in arm_events:
        arm_by_thread.setdefault(str(event["unique_thread_id"]), []).append(event)
    for item in outer:
        outer_by_thread.setdefault(str(item[2]["unique_thread_id"]), []).append(item)
    selected: set[int] = set()
    event_ids: Counter[int] = Counter()
    for thread, items in outer_by_thread.items():
        ordered = sorted(items, key=lambda item: as_int(item[2]["event_index"]))
        arms = sorted(arm_by_thread.get(thread, []), key=lambda event: as_int(event["event_index"]))
        for index, (_invocation, call, entry) in enumerate(ordered):
            low = as_int(entry["event_index"])
            high = as_int(ordered[index + 1][2]["event_index"]) if index + 1 < len(ordered) else calls * 4
            candidates = [event for event in arms if low < as_int(event["event_index"]) < high]
            require(len(candidates) == 1, f"{lane} outer invocation does not select exactly one arm")
            arm = candidates[0]
            selected.add(as_int(arm["event_index"]))
            target_index = as_int(arm["target_index"])
            require(as_int(arm["pc"]) == ARM_ENTRIES[target_index] and as_int(arm["instruction_target"]) == ARM_ENTRIES[target_index], f"{lane} selected arm entry differs")
            require(arm.get("integer_registers_valid") is True and arm.get("register_views_agree") is True, f"{lane} arm registers invalid")
            regs = arm["registers"]
            require(as_int(regs["esi"]) == as_int(call["registers"]["ecx"]), f"{lane} arm receiver differs")
            require(as_int(regs["ecx"]) == as_int(call["registers"]["eax"]), f"{lane} arm event pointer differs")
            normalized = signed32(as_int(regs["eax"]))
            if target_index < 5:
                require(normalized == target_index - 1, f"{lane} fixed arm EAX differs")
            else:
                require(normalized not in range(4), f"{lane} default arm overlaps fixed switch")
            event_ids[normalized + 4000] += 1
    require(len(selected) == calls and selected == {as_int(event["event_index"]) for event in arm_events}, f"{lane} arm accounting differs")
    require(event_ids == Counter(spec["eventIds"]), f"{lane} event ID distribution differs")

    raw_returns = [event for event in events if event.get("event_type") == "return"]
    for returned in raw_returns:
        instruction = returned.get("instruction_bytes", {})
        require(as_int(returned["pc"]) == RETURN_SITE and as_int(returned["instruction_target"]) == FALLTHROUGH, f"{lane} return envelope differs")
        require(returned.get("decoded_near_return") is True and instruction.get("query_valid") is True and str(instruction.get("hex", "")).upper() == "C20400", f"{lane} RET 4 decode differs")
    require(len(receivers) == spec["receivers"], f"{lane} receiver population differs")
    require(len(event_pointers) == spec["eventPointers"], f"{lane} event-pointer population differs")
    summary_counts = (
        as_int(summary["call_entry_pair_count"]), as_int(summary["validated_return_count"]),
        as_int(summary["raw_return_count"]), as_int(summary["orphan_return_count"]),
        as_int(summary["gap_free_envelope_count"]), as_int(summary["event_count"]),
        as_int(summary["invocation_count"]),
    )
    require(summary_counts == (calls, gap_free, calls, orphans, gap_free, calls * 4, calls * 2), f"{lane} summary counts differ")
    for field in ("replay_complete", "replay_counters_sane", "ordering_valid", "contexts_valid", "expectations_passed", "pairing_expectations_passed", "collector_checks_passed"):
        require(summary.get(field) is True, f"{lane} summary failed: {field}")
    require(summary.get("truncated") is False and summary.get("callback_failed") is False, f"{lane} replay truncated/failed")
    projection = projection_sha256(rows)
    require(projection == spec["projection"], f"{lane} observation projection differs")
    return {
        "slot0Calls": calls, "callEntryPairs": calls, "armEntries": calls,
        "rawReturns": calls, "gapFreeReturns": gap_free, "rawOrphanReturns": orphans,
        "sessionLocalReceivers": len(receivers), "sessionLocalEventPointers": len(event_pointers),
        "eventIds": {str(key): event_ids[key] for key in sorted(event_ids)},
        "event4002Observed": event_ids[4002] != 0,
        "receiverVtable": "0x005de82c", "callVa": "0x0044b68a",
        "entryVa": "0x004d9910", "returnVa": "0x004d9d43",
        "projectionSha256": projection,
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
    require(invocation.get("from") == "" and invocation.get("to") == spec["to"] and invocation.get("stackBytes") == 64 and invocation.get("eventLimit") == 1_000_000 and invocation.get("replayMode") == "sequential-all-segments", f"{lane} replay invocation differs")
    calls = spec["calls"]
    context = receipt.get("callContext", {})
    require((context.get("eventCount"), context.get("invocationCount"), context.get("callEntryPairCount"), context.get("validatedReturnCount"), context.get("rawReturnCount"), context.get("orphanReturnCount"), context.get("gapFreeEnvelopeCount")) == (calls * 4, calls * 2, calls, spec["gapFree"], calls, spec["orphans"], spec["gapFree"]), f"{lane} receipt counts differ")
    require(manifest.get("schemaVersion") == "bea-ttd-call-context-manifest.v3" and manifest.get("status") == "READY" and manifest.get("proof", {}).get("collectorChecksPassed") is True, f"{lane} manifest is not READY")
    require(ready.get("schemaVersion") == "bea-ttd-call-context-ready.v3", f"{lane} READY schema differs")
    require(str(ready.get("receiptSha256", "")).lower() == sha256_file(lane_root / "receipt.json"), f"{lane} READY receipt binding differs")
    require(str(ready.get("callContextSha256", "")).lower() == sha256_file(lane_root / "call-context.jsonl"), f"{lane} READY JSONL binding differs")
    require(str(ready.get("manifest", {}).get("sha256", "")).lower() == sha256_file(lane_root / "manifest.json"), f"{lane} READY manifest binding differs")
    rows = read_jsonl(lane_root / "call-context.jsonl")
    return rows, validate_observations(rows, lane, spec)


def validate_runtime(root: Path, evidence: Path) -> dict[str, Any]:
    rows_by_lane: dict[str, list[dict[str, Any]]] = {}
    summaries: dict[str, dict[str, Any]] = {}
    for lane, spec in RUNS.items():
        rows, summary = validate_ready_envelope(evidence, lane, spec)
        rows_by_lane[lane] = rows
        summaries[lane] = summary
    require(observation_projection(rows_by_lane["level521-take4-discovery-v4"]) == observation_projection(rows_by_lane["level521-take4-exact-v1"]), "Level 521 exact replay differs from discovery observations")
    require(observation_projection(rows_by_lane["level512-holdout-discovery-v1"]) == observation_projection(rows_by_lane["level512-holdout-exact-v1"]), "Level 512 exact replay differs from discovery observations")

    poison_root = evidence / "level521-take4-poison-2532-v1"
    poison_receipt = read_json(poison_root / "receipt.json")
    poison_manifest = read_json(poison_root / "manifest.json")
    poison_rows = read_jsonl(poison_root / "call-context.jsonl")
    require(poison_receipt.get("collectorExitCode") == 10 and poison_receipt.get("exitCode") == 10 and poison_receipt.get("readyEligible") is False, "poison collector did not refuse")
    require(poison_manifest.get("status") == "BLOCKED" and poison_manifest.get("proof", {}).get("collectorChecksPassed") is False, "poison manifest did not block")
    require(not (poison_root / "READY").exists(), "poison published READY")
    poison_summary = poison_receipt.get("summary", {})
    require(poison_summary.get("replay_complete") is True and poison_summary.get("replay_counters_sane") is True and poison_summary.get("ordering_valid") is True and poison_summary.get("contexts_valid") is True, "poison replay did not otherwise complete cleanly")
    require(poison_summary.get("expectations_passed") is False and poison_summary.get("pairing_expectations_passed") is False and poison_summary.get("collector_checks_passed") is False, "poison summary did not fail the expected gates")
    require(poison_summary.get("truncated") is False and poison_summary.get("callback_failed") is False, "poison replay truncated/failed")
    require(projection_sha256(poison_rows) == RUNS["level521-take4-exact-v1"]["projection"], "poison changed the observed event stream")
    poison_targets = {as_int(row["target_index"]): row for row in poison_rows if row.get("kind") == "target"}
    require(poison_targets[0].get("expected_entry_count") == "2532" and as_int(poison_targets[0]["observed_entry_count"]) == 2_531, "poison did not assert the +1 outer count")
    require(poison_targets[0].get("expectations_passed") is False, "poison target unexpectedly passed")

    event_ids = Counter()
    for lane in ("level521-take4-exact-v1", "level512-holdout-exact-v1"):
        event_ids.update({int(key): value for key, value in summaries[lane]["eventIds"].items()})
    return {
        "traceIdentityMode": "WRAPPER_HASH_RECEIPT_PLUS_CURRENT_SIZE_NOT_REHASHED_BY_PROOF",
        "independentTraceSessions": 2,
        "slot0CallsObserved": 2_555,
        "callEntryPairs": 2_555,
        "armEntries": 2_555,
        "rawReturnCallbacks": 2_555,
        "gapFreeReturns": 1_972,
        "rawOrphanReturns": 583,
        "sessionLocalReceiverInstancesByTrace": [40, 6],
        "sessionLocalEventPointersByTrace": [412, 18],
        "strictCRoundVtableAllCalls": True,
        "cmissileStyleVtableObserved": False,
        "receiverContinuityAllCallEntryPairs": True,
        "eventPointerContinuityAllCallEntryArmPaths": True,
        "exactlyOneArmPerInvocation": True,
        "observedEventIds": {str(key): event_ids[key] for key in sorted(event_ids)},
        "event4002Observed": False,
        "runs": {lane: summaries[lane] for lane in ("level521-take4-exact-v1", "level512-holdout-exact-v1")},
        "discoveryExactProjectionEqual": {"level521": True, "level512": True},
        "poisonControl": {
            "kind": "EXPECTED_OUTER_COUNT_2532_VERSUS_OBSERVED_2531",
            "collectorExitCode": 10, "readyPublished": False,
            "eventStreamPreserved": True, "expectationsPassed": False,
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


def validate_static(root: Path) -> dict[str, Any]:
    pristine = (root / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup").read_bytes()
    runtime = (root / "local-lab/safe-copy-bea-pristine/BEA.exe").read_bytes()
    function = body(pristine, ENTRY, END_EXCLUSIVE)
    require(len(function) == 1_078 and sha256_bytes(function) == BODY_SHA256, "shared slot-0 body differs")
    require(body(runtime, ENTRY, END_EXCLUSIVE) == function, "runtime slot-0 body differs from pristine")
    require(body(pristine, CALL_SITE - 3, CALL_SITE + 2).hex() == "8b1150ff12", "slot-0 caller bytes differ")
    require(body(runtime, CALL_SITE - 3, CALL_SITE + 2) == body(pristine, CALL_SITE - 3, CALL_SITE + 2), "runtime caller differs from pristine")
    require(struct.unpack("<I", body(pristine, CROUND_VTABLE, CROUND_VTABLE + 4))[0] == ENTRY, "strict CRound slot-0 cell differs")
    require(struct.unpack("<I", body(pristine, CMISSILE_VTABLE, CMISSILE_VTABLE + 4))[0] == ENTRY, "CMissile-style slot-0 cell differs")
    require(body(pristine, 0x004D9938, 0x004D9938 + 25).hex() == "0fbf41040560f0ffff83f8030f87d9030000ff2485489d4d00", "event switch bytes differ")
    require(list(struct.unpack("<IIII", body(pristine, 0x004D9D48, 0x004D9D58))) == [ARM_ENTRIES[i] for i in range(1, 5)], "event switch table differs")
    require(function.count(b"\xC2\x04\x00") == 1 and body(pristine, RETURN_SITE, RETURN_SITE + 3) == b"\xC2\x04\x00", "sole RET 4 identity differs")

    demo_rows = read_tsv(root / "reverse-engineering/binary-analysis/pc-demo-retail-virtual-target-map-2026-08-11.tsv")
    demo = next((row for row in demo_rows if row.get("retail_va") == "0x004d9910"), None)
    require(demo is not None, "PC-demo shared slot-0 row is absent")
    require(
        demo.get("demo_va") == "0x004d97f0"
        and demo.get("owner_classes") == "CMissile|CRound"
        and demo.get("placement_count") == "2"
        and demo.get("retail_body_bytes") == "1078"
        and demo.get("retail_instruction_count") == "296"
        and demo.get("demo_instruction_count") == "296"
        and demo.get("exact_zero_normalized") == "true"
        and demo.get("retail_instruction_stream_raw_sha256") == BODY_SHA256
        and demo.get("retail_instruction_stream_normalized_sha256") == demo.get("demo_instruction_stream_normalized_sha256"),
        "PC-demo shared slot-0 fingerprint differs",
    )
    names = read_tsv(root / "reverse-engineering/binary-analysis/ghidra-function-name-table-2026-07-27.tsv")
    named = next((row for row in names if row.get("address") == "0x004d9910"), None)
    require(named is not None and named.get("name") == "CRound__HandleEvent" and named.get("bodyMin") == "0x004d9910" and named.get("bodyMax") == "0x004d9d45", "tracked static label/range differs")
    closure_rows = read_tsv(root / "reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv")
    closure = next((row for row in closure_rows if row.get("entryVa") == "0x004d9910"), None)
    require(
        closure is not None
        and closure.get("trackedName") == "CRound__HandleEvent"
        and closure.get("disposableName") == "HYP__VFuncSlot_00_004d9910"
        and closure.get("gradeAfter") == "C1_CANDIDATE_PARTIAL"
        and closure.get("bodyBytes") == "1078"
        and closure.get("instrCount") == "296",
        "shared slot-0 static C1 closure differs",
    )
    return {
        "function": {"entryVa": "0x004d9910", "endExclusive": "0x004d9d46", "bytes": 1_078, "sha256": BODY_SHA256},
        "dispatcher": {"callVa": "0x0044b68a", "instruction": "call dword ptr [edx]", "fallthrough": "0x0044b68c"},
        "placements": {
            "strictCRound": {"vtable": "0x005de82c", "slot0Cell": "0x005de82c", "target": "0x004d9910"},
            "cmissileStyle": {"vtable": "0x005e3ba4", "slot0Cell": "0x005e3ba4", "target": "0x004d9910"},
        },
        "switch": {
            "eventIdField": "signed word [event_record+4]", "normalization": "event_id - 4000",
            "fixedArms": {"4000": "0x004d9a54", "4001": "0x004d997e", "4002": "0x004d995e", "4003": "0x004d9951"},
            "defaultArm": "0x004d9d23",
        },
        "trackedStaticLabel": "CRound__HandleEvent",
        "campaignNameRetained": CURRENT_NAME,
        "sourceSpellingStatus": "OPEN_NOT_PROMOTED_BY_THIS_PROOF",
        "scopedIdentity": "shared slot-0 event-dispatch body observed on strict CRound receivers",
        "pcDemo": {"entryVa": "0x004d97f0", "instructionCount": 296, "exactZeroNormalized": True},
        "staticGradeBeforeRuntime": "C1_CANDIDATE_PARTIAL",
    }


def validate_campaign(root: Path, campaign: Path) -> dict[str, Any]:
    ready_path = campaign / "campaign.ready.json"
    require(sha256_file(ready_path) == CAMPAIGN_READY_SHA256, "Generation 21 READY differs")
    authority = stamp(root / CAMPAIGN_AUTHORITY, root)
    require((authority["bytes"], authority["sha256"]) == CAMPAIGN_AUTHORITY_STAMP, "Generation 21 authority differs")
    ready = read_json(ready_path)
    require(ready.get("generation") == 21 and ready.get("reducer", {}).get("id") == CAMPAIGN_REDUCER_ID, "Generation 21 identity differs")
    function = next(row for row in read_tsv(campaign / "campaign-functions.tsv") if row["entityKey"] == ENTITY_KEY)
    contract = next(row for row in read_tsv(campaign / "campaign-contracts.tsv") if row["contractId"] == CONTRACT_ID)
    question = next(row for row in read_tsv(campaign / "campaign-questions.tsv") if row["questionId"] == QUESTION_ID)
    require(function["currentName"] == CURRENT_NAME and function["resolutionState"] == "OPEN_JOIN" and function["semanticGrade"] == "OPAQUE" and function["campaignState"] == "OPEN_EXECUTED", "Generation 21 function frontier differs")
    require(contract["entityKey"] == ENTITY_KEY and contract["contractState"] == "OPEN" and contract["semanticGrade"] == "C0_OPAQUE" and contract["refuterVerdict"] == "UNSCORED", "Generation 21 contract frontier differs")
    require(question["entityKey"] == ENTITY_KEY and question["state"] == "OPEN" and question["questionType"] == "EXECUTED_FUNCTION_IDENTITY", "Generation 21 question frontier differs")
    return {"generation": 21, "ready": stamp(ready_path, root), "authority": authority, "reducerId": CAMPAIGN_REDUCER_ID, "function": function, "contract": contract, "question": question}


EXPECTED_BOUNDARY = {
    "slot0CallsObserved": 2_555,
    "independentTraceSessions": 2,
    "sessionLocalReceiverInstancesByTrace": [40, 6],
    "sessionLocalEventPointersByTrace": [412, 18],
    "callEntryPairsObserved": 2_555,
    "eventArmEntriesObserved": 2_555,
    "gapFreeReturnEnvelopes": 1_972,
    "rawOrphanReturnCallbacks": 583,
    "strictCRoundVtableAllObservedCalls": True,
    "receiverContinuityAllObservedCallEntryArmPaths": True,
    "eventPointerContinuityAllObservedCallEntryArmPaths": True,
    "exactlyOneArmPerObservedInvocation": True,
    "observedEventIds": {"2000": 167, "3000": 2_190, "4000": 120, "4001": 3, "4003": 75},
    "event4002Observed": False,
    "cmissileStyleReceiverObserved": False,
    "receiverWritesObserved": False,
    "armEffectsClaimed": False,
    "completeSubclassBehaviorClaimed": False,
    "shippedSourceSpellingClaimed": False,
    "rebuildState": "PARTIAL_CONTRACT",
}


def validate_claim_boundary(value: dict[str, Any]) -> None:
    require(value == EXPECTED_BOUNDARY, "claim boundary differs")


def derive(root: Path, campaign: Path) -> dict[str, Any]:
    evidence = root / EVIDENCE_RELATIVE
    require(evidence.is_dir(), "CRound shared slot-0 evidence root is missing")
    inputs = exact_inputs(root, evidence)
    runtime = validate_runtime(root, evidence)
    static = validate_static(root)
    frontier = validate_campaign(root, campaign)
    boundary = copy.deepcopy(EXPECTED_BOUNDARY)
    validate_claim_boundary(boundary)
    return {
        "schema": SCHEMA,
        "verdict": "PASS",
        "claim": CLAIM,
        "specimen": {"sha256": SPECIMEN_SHA256, "role": "PRISTINE_STATIC_AUTHORITY_UNCHANGED"},
        "runtimeImage": {"sha256": RUNTIME_SHA256, "role": "EXISTING_TRACE_IMAGE_BODY_EQUAL_TO_PRISTINE_IN_SCOPE"},
        "entity": {
            "entityKey": ENTITY_KEY, "contractId": CONTRACT_ID, "questionId": QUESTION_ID,
            "currentName": CURRENT_NAME, "scopedIdentity": static["scopedIdentity"],
            "trackedStaticLabel": static["trackedStaticLabel"],
            "sourceSpellingStatus": static["sourceSpellingStatus"],
        },
        "campaign": frontier,
        "runtime": runtime,
        "static": static,
        "adjudication": {
            "semanticGrade": "C2_BOUNDED_RUNTIME",
            "contractState": "BOUNDED_CONTRACT_ADVANCED",
            "runtimeVerdict": "MEASURED_BOUNDED_STRICT_CROUND_SLOT0_EVENT_ROUTING_ENVELOPE",
            "refuterVerdict": "SURVIVED",
            "questionDisposition": "CLOSE_BASE_AND_OPEN_NARROW_SUCCESSORS",
        },
        "rebuild": {
            "state": "PARTIAL_CONTRACT",
            "owner": inputs["rebuild/OnslaughtRebuild.Core/Level100ActorWeaponRuntime.cs"],
            "test": inputs["rebuild/OnslaughtRebuild.Core.Tests/Level100ActorWeaponTests.cs"],
            "implementation": "Level100ActorMechanics.AdvanceActorRounds",
            "scope": "nearest partial round launch/update/removal owner; no explicit retail event queue or direct event-routing parity test",
        },
        "claimBoundary": boundary,
        "limitations": [
            "The retained multi-gigabyte traces are wrapper-hash-bound and current-size-checked, not rehashed by this proof.",
            "The 2,555 calls span two independent recordings; discovery/exact repeats are calibration, not extra sessions.",
            "All observed dispatches used strict CRound vtable 0x005DE82C; the shared CMissile-style placement was not observed.",
            "Event 4002 was not observed, and no runtime semantic claim is assigned to its static arm.",
            "The proof records receiver/event-pointer continuity and exact selected-arm routing, not arm writes, callees, or transitive effects.",
            "The tracked CRound__HandleEvent label is static metadata, not proven original source spelling; the campaign name stays generic.",
            "The rebuild mapping is PARTIAL_CONTRACT; no explicit retail event queue or direct parity test exists, so no rebuild change is authorized.",
            "No game, trace, Ghidra project, executable, or rebuild source was mutated while producing this proof.",
        ],
        "inputs": inputs,
        "author": stamp(Path(__file__).resolve(), root),
    }


def selftest(root: Path, campaign: Path) -> dict[str, Any]:
    rows = read_jsonl(root / EVIDENCE_RELATIVE / "level512-holdout-exact-v1/call-context.jsonl")
    attacks: list[tuple[str, list[dict[str, Any]], str]] = []
    forged = copy.deepcopy(rows)
    next(row for row in forged if row.get("kind") == "event" and row.get("event_type") == "call")["registers"]["edx"] = "0x5E3BA4"
    attacks.append(("cmissile-vtable", forged, "strict CRound vtable differs"))
    forged = copy.deepcopy(rows)
    next(row for row in forged if row.get("kind") == "event" and row.get("event_type") == "entry" and row.get("target_index") == 0)["registers"]["ecx"] = "0x1"
    attacks.append(("receiver-discontinuity", forged, "call-entry receiver differs"))
    forged = copy.deepcopy(rows)
    event = next(row for row in forged if row.get("kind") == "event" and row.get("event_type") == "call")
    raw = bytearray.fromhex(event["stack"]["hex"])
    struct.pack_into("<I", raw, 4, 1)
    event["stack"]["hex"] = raw.hex().upper()
    attacks.append(("event-argument-discontinuity", forged, "stack event argument differs"))
    forged = copy.deepcopy(rows)
    next(row for row in forged if row.get("kind") == "event" and row.get("target_index") == 1)["registers"]["eax"] = "0x1"
    attacks.append(("arm-id-mismatch", forged, "fixed arm EAX differs"))
    forged = copy.deepcopy(rows)
    next(row for row in forged if row.get("kind") == "event" and row.get("event_type") == "return")["pc"] = "0x4D9D42"
    attacks.append(("return-outside-body", forged, "return envelope differs"))
    rejected: list[str] = []
    for label, forged_rows, expected in attacks:
        try:
            validate_observations(forged_rows, f"selftest-{label}", RUNS["level512-holdout-exact-v1"])
        except ProofError as exc:
            require(expected in str(exc), f"{label} rejected by unintended gate: {exc}")
            rejected.append(label)
        else:
            raise ProofError(f"selftest attack accepted: {label}")
    for label, key, value in (
        ("event4002-overclaim", "event4002Observed", True),
        ("arm-effects-overclaim", "armEffectsClaimed", True),
        ("complete-subclass-overclaim", "completeSubclassBehaviorClaimed", True),
        ("rebuild-ready-overclaim", "rebuildState", "REBUILD_READY"),
    ):
        forged_boundary = copy.deepcopy(EXPECTED_BOUNDARY)
        forged_boundary[key] = value
        try:
            validate_claim_boundary(forged_boundary)
        except ProofError:
            rejected.append(label)
        else:
            raise ProofError(f"selftest attack accepted: {label}")
    require(validate_campaign(root, campaign)["generation"] == 21, "selftest campaign gate failed")
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
        str((root / EVIDENCE_RELATIVE / "holdout-preregistration.md").resolve()),
        str((root / "reverse-engineering/binary-analysis/pc-demo-retail-virtual-target-map-2026-08-11.tsv").resolve()),
        str((root / "reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv").resolve()),
    ]
    row = dict(base)
    row.update({
        "contractState": "RUNTIME_CANDIDATE_NEEDS_REFUTER",
        "semanticGrade": "C2_BOUNDED_RUNTIME",
        "receiver": "2,555 slot-0 call-entry pairs across two retained recordings; 40+6 session-local receivers; call and entry EDX were strict CRound vtable 0x005de82c, with call ECX=entry ECX=selected-arm ESI",
        "inputs": "call/entry EAX and caller stack dword +4 held one event-record pointer, preserved into selected-arm ECX; pristine signed word[event+4]-4000 switch joins the observed arm EAX to event IDs",
        "returns": "2,555 raw callbacks at sole RET 4 0x004d9d43 to 0x0044b68c: 1,972 gap-free paired envelopes and 583 raw orphan callbacks across continuity barriers; no semantic EAX return assigned",
        "writes": "not measured; no receiver or external write claim",
        "sideEffects": "exactly one fixed arm entered for every observed outer invocation; arm callees, writes, ordering, and transitive effects were not isolated",
        "preconditions": "complete named Level 521 take 4 and Level 512 retained trace lifetimes, each replayed for discovery and exact-count repeat",
        "failureModes": "event 4002, other default IDs, CMissile-style placement, arm writes/effects, broader populations, and exact source spelling remain open",
        "authorVerdict": "SUPPORTED_BY_PRISTINE_SLOT0_SWITCH_JOIN_AND_TWO_INDEPENDENT_TTD_TRACE_SESSIONS",
        "runtimeVerdict": "MEASURED_BOUNDED_STRICT_CROUND_SLOT0_EVENT_ROUTING_ENVELOPE",
        "refuterVerdict": "UNSCORED",
        "questionIds": QUESTION_ID,
        "evidenceRefs": ";".join(evidence_refs),
        "cheapestFalsifier": "Reparse either exact JSONL and find one call with EDX other than 0x005de82c, a receiver/event-pointer discontinuity, or an invocation without exactly one static-table-consistent arm.",
        "rebuildOwner": "rebuild/OnslaughtRebuild.Core/Level100ActorWeaponRuntime.cs",
        "rebuildImplementation": "Level100ActorMechanics.AdvanceActorRounds (nearest partial round owner; no explicit retail event queue)",
        "parityTests": "Level100ActorWeaponTests.ActorArmament_IsCanonicalReplayState (nearest partial state test; no direct event-routing parity test)",
        "rebuildState": "PARTIAL_CONTRACT",
        "remainingUncertainty": "exact arm writes, callees, and ordering; unobserved event 4002; shared CMissile-style slot-0 runtime placement; original source spelling; explicit reconstruction event-routing owner and parity test",
        "lastMeasurementDate": "2026-08-12",
        "scopeKind": "EXISTING_TTD_TWO_TRACE_STRICT_CROUND_SLOT0_EVENT_ROUTING_ENVELOPE",
        "payloadSha256": "",
        "receiverVtable": "0x005de82c",
        "observedCallVas": "0x0044b68a",
        "controlSummary": "Level 521 poison required 2,532 outer calls/entries/returns versus 2,531 observed; exit 10, expectation/pairing/collector gates false, no READY, observation projection unchanged",
        "runtimeEvidenceSha256": ";".join(saved["inputs"][f"{lane}/call-context.jsonl"]["sha256"] for lane in ("level521-take4-exact-v1", "level512-holdout-exact-v1")),
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
            relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / "preregistration-amendment-1.md", "preregistration-amendment-1"),
            relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / "preregistration-amendment-2.md", "preregistration-amendment-2"),
            relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / "preregistration-amendment-3.md", "preregistration-amendment-3"),
            relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / "holdout-preregistration.md", "holdout-preregistration"),
            relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / "level521-take4-discovery-v4/call-context.jsonl", "runtime-level521-discovery"),
            relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / "level521-take4-exact-v1/call-context.jsonl", "runtime-level521-exact"),
            relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / "level512-holdout-discovery-v1/call-context.jsonl", "runtime-level512-discovery"),
            relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / "level512-holdout-exact-v1/call-context.jsonl", "runtime-level512-exact"),
            relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / "level521-take4-poison-2532-v1/call-context.jsonl", "poison-level521"),
            relative_artifact(proof / READY_NAME, root / "tools/Invoke-TtdCallContextV2.ps1", "call-context-wrapper-v2"),
            relative_artifact(proof / READY_NAME, root / "tools/ttd_pipeline_contract_tests.py", "wrapper-contract-test"),
            relative_artifact(proof / READY_NAME, root / "reverse-engineering/binary-analysis/pc-demo-retail-virtual-target-map-2026-08-11.tsv", "static-demo-retail-map"),
            relative_artifact(proof / READY_NAME, root / "reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv", "static-c1-closure"),
            relative_artifact(proof / READY_NAME, root / "reverse-engineering/binary-analysis/ghidra-function-name-table-2026-07-27.tsv", "static-name-table"),
            relative_artifact(proof / READY_NAME, root / "rebuild/OnslaughtRebuild.Core/Level100ActorWeaponRuntime.cs", "rebuild-nearest-owner"),
            relative_artifact(proof / READY_NAME, root / "rebuild/OnslaughtRebuild.Core.Tests/Level100ActorWeaponTests.cs", "rebuild-nearest-test"),
        ]
        receipt = {
            "schema": OVERLAY_SCHEMA,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "sourceCampaign": {"path": str(campaign.resolve()), "ready": stamp(campaign / "campaign.ready.json"), "specimen": read_json(campaign / "campaign.ready.json")["sourceSnapshot"]["specimen"]},
            "inputContract": stamp(proof / READY_NAME),
            "artifacts": artifacts,
            "authorVerification": {"checks": saved["selftest"], "claimBoundary": saved["claimBoundary"]},
            "count": 1,
            "policy": {
                "namesAuthorized": False, "ghidraMutationAuthorized": False,
                "promotionAuthorized": False, "requiresRefuter": True,
                "maximumImportedGrade": "C2_BOUNDED_RUNTIME",
                "artifactClaimsParsed": True, "runtimeExecutableRelationValidated": True,
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
    prereg = "local-lab/cround-handle-event-existing-trace-20260812-v1/holdout-preregistration.md"
    finding = {
        "schemaVersion": 1,
        "id": "cround-slot0-strict-event-routing-envelope-2026-08-12",
        "title": "CRound shared slot-0 strict receiver event-routing envelope in two retained traces",
        "date": "2026-08-12", "lane": "ttd/existing-trace", "author": "recursive RE campaign",
        "sourceNote": str((proof / READY_NAME).resolve()), "findingKind": "instrument-derived",
        "claim": {
            "statement": "In the named Level 521 and Level 512 recordings, strict CRound slot-0 calls to 0x004D9910 preserved receiver and event-pointer identity into exactly one static-table-consistent event arm.",
            "grade": "EXECUTED", "mechanism": ["cround.slot0.event_routing_envelope"],
        },
        "scope": {
            "population": "slot-0 calls to 0x004D9910 in the complete named Level 521 take 4 and Level 512 retained recordings",
            "covered": "2,531 Level 521 and 24 Level 512 call-entry-arm paths, plus 1,972 gap-free paired and 583 raw orphan return callbacks",
            "notCovered": [
                "CMissile-style receiver placement", "event 4002 and default event IDs other than 2000/3000",
                "arm writes, callees, ordering, and transitive effects", "populations outside the two recordings",
                "original source spelling and direct reconstruction parity",
            ],
        },
        "rivals": [
            {
                "id": "rival-cmissile-placement",
                "statement": "The shared 0x004D9910 body was reached through CMissile-style rather than strict CRound placement.",
                "indistinguishableOn": ["entry coverage at 0x004D9910", "the shared static slot-0 target"],
                "discriminator": {
                    "description": "read raw EDX at every indirect slot-0 call and paired entry",
                    "mechanism": ["cround.slot0.receiver_placement"],
                    "expectedUnderClaim": "EDX is strict CRound vtable 0x005DE82C",
                    "expectedUnderRival": "EDX is CMissile-style vtable 0x005E3BA4",
                    "status": "observed", "outcome": "claim", "evidenceRef": ["e-level521", "e-level512"],
                },
            },
            {
                "id": "rival-non-event-arm-coincidence",
                "statement": "Observed interior entries were unrelated coverage and did not route the caller-supplied event record through the fixed switch.",
                "indistinguishableOn": ["outer entry coverage", "interior arm coverage without raw context"],
                "discriminator": {
                    "description": "bind each call/entry event pointer and receiver to exactly one subsequent arm and compare arm EAX with the pristine switch",
                    "mechanism": ["cround.slot0.event_pointer_and_arm_routing"],
                    "expectedUnderClaim": "call EAX/stack+4 equals entry EAX equals arm ECX, call/entry ECX equals arm ESI, and arm EAX selects the static event-ID arm",
                    "expectedUnderRival": "an invocation lacks those identities, has zero/multiple arms, or enters an arm inconsistent with its normalized EAX",
                    "status": "observed", "outcome": "claim", "evidenceRef": ["e-level521", "e-level512"],
                },
            },
        ],
        "predictions": [
            {
                "id": "p-level512-placement",
                "statement": "The independent Level 512 holdout will reproduce strict-CRound slot-0 placement and receiver/event continuity.",
                "procedure": "replay the complete retained Level 512 lifetime with the preregistered six-target partition and inspect call, entry, and arm registers",
                "expected": "every call/entry has EDX 0x005DE82C and every selected arm preserves the receiver and event pointer",
                "wouldFalsifyIf": "any call uses another vtable or any path changes the receiver/event pointer",
                "predictedInAdvance": True, "statedAt": prereg, "result": "match",
                "observed": "24 calls all used EDX 0x005DE82C and all call-entry-arm receiver/event identities matched",
                "evidenceRef": ["e-level512"],
            },
            {
                "id": "p-level512-arm-accounting",
                "statement": "The independent Level 512 holdout will contain at least one invocation and one arm with complete one-arm accounting.",
                "procedure": "collect the complete retained Level 512 lifetime and partition arm entries by thread between consecutive outer entries",
                "expected": "at least one outer path and one fixed arm, with exactly one arm for every invocation",
                "wouldFalsifyIf": "the holdout has no call/arm or any invocation has zero or multiple selected arms",
                "predictedInAdvance": True, "statedAt": prereg, "result": "match",
                "observed": "24 outer paths selected exactly 24 arms: six event-4000 and eighteen default arms",
                "evidenceRef": ["e-level512"],
            },
        ],
        "evidence": [
            {
                "id": "e-level521", "grade": "EXECUTED", "instrument": "hash-pinned TTD schema-v3 call-context replay",
                "summary": "2,531 strict-CRound call-entry-arm paths; 1,960 gap-free returns; 571 raw orphan returns; 40 receiver and 412 event-pointer addresses local to this recording",
                "sample": {"n": 2_531, "units": "slot-0 call-entry-arm paths", "independentReplicates": 1, "sessions": 1},
                "specimen": {"path": RUNS["level521-take4-exact-v1"]["trace"][0], "sha256": RUNS["level521-take4-exact-v1"]["trace"][2]},
            },
            {
                "id": "e-level512", "grade": "EXECUTED", "instrument": "hash-pinned TTD schema-v3 call-context replay",
                "summary": "24 strict-CRound call-entry-arm paths; 12 gap-free returns; 12 raw orphan returns; six receiver and 18 event-pointer addresses local to this recording",
                "sample": {"n": 24, "units": "slot-0 call-entry-arm paths", "independentReplicates": 1, "sessions": 1},
                "specimen": {"path": RUNS["level512-holdout-exact-v1"]["trace"][0], "sha256": RUNS["level512-holdout-exact-v1"]["trace"][2]},
            },
        ],
        "residuals": [
            {"id": "res-arm-effects", "statement": "Arm-specific writes, callees, ordering, and transitive effects were not measured.", "mechanism": ["cround.event_arm.state_effects"], "blocksClaim": False},
            {"id": "res-event4002", "statement": "Event 4002 did not occur in either recording.", "mechanism": ["cround.event4002.runtime_population"], "blocksClaim": False},
            {"id": "res-cmissile-population", "statement": "Neither recording supplied a CMissile-style receiver.", "mechanism": ["cmissile.slot0.runtime_population"], "blocksClaim": False},
            {"id": "res-source-rebuild", "statement": "Original source spelling and an explicit reconstruction event-routing owner/test remain open.", "mechanism": ["cround.source_and_rebuild_scope"], "blocksClaim": False},
        ],
        "poisonControl": {
            "id": "control-level521-expected-2532", "kind": "poison",
            "description": "the Level 521 target falsely requires 2,532 outer calls, entries, and returns although the recording contains 2,531",
            "predictedOutcome": "collector exits nonzero, fails expectation/pairing/collector gates, and publishes no READY without changing observations",
            "observedOutcome": "exit 10; expectation, pairing, and collector checks false; no READY; observation projection identical",
            "result": "failed_as_predicted",
        },
        "overturnedBy": [
            {"id": "kill-independent-reparse", "procedure": "independently parse either hash-pinned exact JSONL and find a named invocation with non-strict EDX, changed receiver/event pointer, or non-unique/inconsistent arm", "wouldShow": "the bounded routing claim is false for its named population", "cost": "one independent JSONL parser"},
            {"id": "kill-independent-replay", "procedure": "replay either hash-pinned recording with an independent context collector and obtain a call-entry-arm path inconsistent with the saved exact projection", "wouldShow": "the saved collector projection is not a faithful execution observation", "cost": "one full retained-trace replay"},
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
            "refuterEvidence": [evidence_ref(out, finding, "refuter-finding"), evidence_ref(out, result, "refuter-result")],
            "terminalState": "", "measuredAtUtc": measured,
            "remainingUncertainty": "Strict-CRound slot-0 event routing is bounded for two recordings, while exact arm writes/callees/order, event 4002, shared CMissile placement, original source spelling, and an explicit reconstruction event-queue mapping remain unresolved.",
            "nextQuestions": [
                {
                    "questionType": "CROUND_HANDLEEVENT_ARM_EFFECTS_AND_WRITES",
                    "question": "Which receiver and external writes, callees, and ordering occur in each observed 4000, 4001, 4003, and default arm of 0x004D9910?",
                    "recommendedInstrument": "TTD_BRANCH_AND_DATA_WRITE_ENVELOPE_ON_GAP_FREE_EXISTING_TRACE_INVOCATIONS",
                    "cheapestFalsifier": "Bind one gap-free invocation per observed arm to exact receiver/external write watches and compare its order with the pristine branch path.",
                    "requiresElevation": False, "priority": 1, "score": 700.0,
                    "source": "CRound shared slot-0 Gen22 adjudication", "currentOwner": "recursive-re-campaign",
                },
                {
                    "questionType": "CROUND_HANDLEEVENT_EVENT4002_RUNTIME_PLACEMENT",
                    "question": "When does event 4002 enter static arm 0x004D995E, and what exact state transition does that arm perform?",
                    "recommendedInstrument": "EXISTING_TRACE_SEARCH_THEN_PREREGISTERED_SAFE_COPY_EVENT4002_PROBE",
                    "cheapestFalsifier": "Find one hash-bound event-4002 invocation and bind its call, arm, writes, and return envelope.",
                    "requiresElevation": False, "priority": 2, "score": 650.0,
                    "source": "CRound shared slot-0 Gen22 adjudication", "currentOwner": "recursive-re-campaign",
                },
                {
                    "questionType": "CMISSILE_SLOT0_HANDLEEVENT_RUNTIME_PLACEMENT",
                    "question": "When does shared target 0x004D9910 execute through CMissile-style vtable 0x005E3BA4, and which event arms occur for that receiver population?",
                    "recommendedInstrument": "EXISTING_TRACE_SEARCH_THEN_TARGETED_SAFE_COPY_IF_ABSENT",
                    "cheapestFalsifier": "Find one 0x0044B68A call with EDX 0x005E3BA4 and bind its receiver, event pointer, selected arm, and return.",
                    "requiresElevation": False, "priority": 3, "score": 600.0,
                    "source": "CRound shared slot-0 Gen22 adjudication", "currentOwner": "recursive-re-campaign",
                },
            ],
            "rebuildMapping": {
                "rebuildOwner": "rebuild/OnslaughtRebuild.Core/Level100ActorWeaponRuntime.cs",
                "rebuildImplementation": "Level100ActorMechanics.AdvanceActorRounds (nearest partial round owner; no explicit retail event queue)",
                "parityTests": "Level100ActorWeaponTests.ActorArmament_IsCanonicalReplayState (nearest partial state test; no direct event-routing parity test)",
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
            print(f"CROUND_HANDLE_EVENT_RUNTIME_PROOF_READY {stamp(path)}")
        elif args.command == "verify":
            value = verify(root, campaign, args.proof.resolve())
            print(f"CROUND_HANDLE_EVENT_RUNTIME_PROOF_VERIFIED verdict={value['verdict']} calls={value['runtime']['slot0CallsObserved']}")
        elif args.command == "selftest":
            value = selftest(root, campaign)
            print(f"CROUND_HANDLE_EVENT_RUNTIME_SELFTEST_OK attacks={value['count']}")
        elif args.command == "overlay":
            path = build_overlay(root, campaign, args.proof.resolve(), args.out.resolve())
            print(f"CROUND_HANDLE_EVENT_RUNTIME_OVERLAY_READY {stamp(path)}")
        elif args.command == "finding":
            path = build_finding(root, args.proof.resolve(), args.overlay.resolve(), args.out.resolve())
            print(f"CROUND_HANDLE_EVENT_RUNTIME_FINDING_READY {stamp(path)}")
        else:
            path = build_adjudication(campaign, args.overlay.resolve(), args.finding.resolve(), args.result.resolve(), args.out.resolve())
            print(f"CROUND_HANDLE_EVENT_RUNTIME_ADJUDICATION_READY {stamp(path)}")
        return 0
    except (ProofError, OSError, ValueError, KeyError, struct.error) as exc:
        print(f"CROUND_HANDLE_EVENT_RUNTIME_REFUSED: {exc}", file=os.sys.stderr)
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
