#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Prove and package the bounded CExplosion::Hit slot-40 carrier contract.

The proof replays no game and mutates no specimen. It independently parses
three retained, hash-pinned TTD call-context exports and one deliberately
poisoned export, then joins the observed call sites to pristine instructions,
the existing static C1 closure, the current campaign frontier, and the partial
Level 100 rebuild mapping.
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


SCHEMA = "bea.re.cexplosion-hit-runtime-proof.v1"
READY_NAME = "proof.ready.json"
CLAIM = "CEXPLOSION_SLOT40_ARGUMENT_CARRIER_C2_BOUNDED"
OVERLAY_SCHEMA = "bea.re.runtime-contract-overlay.v1"
ADJUDICATION_SCHEMA = "bea.re.runtime-contract-adjudication.v1"
REFUTER_SUBJECT_SCHEMA = "bea.re.refuter-subject.v1"

SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
RUNTIME_SHA256 = "e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4"
ENTITY_KEY = (
    "CODE:" + SPECIMEN_SHA256
    + ":VA=0x0044bf10:RANGES=b61c167530383dc9d17a16505e35d702f71f15972f58abbfcfc61f59aefb3fbd"
)
CONTRACT_ID = "C-fa1c3cbbcc43d1e4"
QUESTION_ID = "Q-5e64a170c6a1dd45"
CURRENT_NAME = "CExplosion__VFunc_39_0044bf10"

EVIDENCE_RELATIVE = Path("local-lab/cexplosion-hit-existing-trace-20260812-v1")
CAMPAIGN_RELATIVE = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-19-mission-native-unsetobjective-reproof-v1"
)
CAMPAIGN_READY_SHA256 = "f83dbb6eddaa16deed5f2a2460d393dc4525a63ae243b6cac0c656056b69ab9a"
CAMPAIGN_REDUCER_ID = "151acbe5c1571dca2c53c68dd79281cf20c69af609523d54f25953643dcff3e2"

EXPLOSION_ENTRY = 0x0044BF10
EXPLOSION_END = 0x0044C0EF
EXPLOSION_BODY_SHA256 = "39e060a24fb364ff853e91d4825136bf8859bce85dea28d03a48c7e0928d7872"
CUNIT_BODY_SHA256 = "c00c805fc86ad1f52e6ab7d8fc739c456983914319ad99870d49c88b8733f859"
SEGMENT_BODY_SHA256 = "393ce58690812c3eebaa92dedebd34fcaf159e267a7cb9fc72d28d06c97a3240"

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
    "damage-targets.tsv": (407, "c99352d0a2edd73c4dd6dbd2b977c95eed957968e79d0535c1fc019eafa6c13e"),
    "damage-targets-poison-cunit-seven.tsv": (437, "5492ad3925b64b498e105b8af2d8b8c979067d5eb1732a0409643c5413a4c498"),
    "preregistration.md": (3311, "20e62c3a693dcd589e1135fd9eba1af81122c328d24191bd8e0126bce9bb5bb0"),
    "level231-damage-window/call-context.jsonl": (31795, "5d0014bbaa5bc46ad2420480d75f6560cb12417b67bf7539b60c15d59008d675"),
    "level231-damage-window/receipt.json": (7721, "f961854ab6076c39bbf8b85ad3b46f9b2226d80929a030ba22e59cbe30e8bf1a"),
    "level231-damage-window/manifest.json": (3973, "6d07ea5d70e36d3443ccace8e8211c3ce69929041230d63d11dabde790fdd41d"),
    "level231-damage-window/READY": (575, "d49b2f14ea889d96544e508f2d16b18548d0e0d5d5dad9a16f555e5416aa5a55"),
    "level110-replication/call-context.jsonl": (43737, "0c1ad6846eb21951f0a23024898d58c3d98c9313af68318414892f4148d9c712"),
    "level110-replication/receipt.json": (7707, "38d9003a1c53814df54bcec9a0e3b1370bac10886a52386bbbd5def81a0c2786"),
    "level110-replication/manifest.json": (3961, "0f35fc7f86bb7be8dc303624365bda21d072e7333939293d5674debb34b70b32"),
    "level110-replication/READY": (573, "f9f3152e621425f5956b1d33b3121ea337c83ebc6d3063dce49cd71b5a7532d3"),
    "level854-large-arm/call-context.jsonl": (15917, "3045f3a8e2a736a15b9ef6fa87f90cd07778ec6233dfe8811767c56538bb58f5"),
    "level854-large-arm/receipt.json": (7692, "64907e548997a42997df7cb1c9bec07a3c19a339e0a33a284e79cb16cc6b2870"),
    "level854-large-arm/manifest.json": (3946, "dbda1d4684fc96be8a709b6adf1edd8345b43ff04b8902a9d3e7a3760bd309b7"),
    "level854-large-arm/READY": (571, "2242485f8bf20e6afdc0d2fce95fbe15582a4f5f05336ac04484973b119743fd"),
    "level231-poison-cunit-seven/call-context.jsonl": (31774, "c6118cbf75e12759ee9df52ffaa58375a9b0a58e3649fc6e664273aa2147cf38"),
    "level231-poison-cunit-seven/receipt.json": (7781, "45ded44c0ea01e11799d068ecaa7c5fb9d5e8d72d42b92fc851a793adc853aeb"),
    "level231-poison-cunit-seven/manifest.json": (4017, "d9fc71c864638f1a762870912d24fca4a8a5a8dbba6545c8dafc4b152f01a8c8"),
}

REPO_PINS: dict[str, tuple[int, str]] = {
    "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup": (2_506_752, SPECIMEN_SHA256),
    "local-lab/safe-copy-bea-pristine/BEA.exe": (2_506_752, RUNTIME_SHA256),
    "local-lab/cround-explosion-semantic-20260810-v1/decompile/0044bf10_HYP__CombatAiStaticBody__0044bf10.c": (10939, "18ba6a7f2fe855d9f613527ad8b8fc0af86e84bf317e11b791608a1ddfd3c19e"),
    "local-lab/damage-chain-pilot-2026-08-02/static/decompile/004f9a90_CUnit__ApplyDamage.c": (20732, "71e926df3a4817c546db0886fffa155705a5335c4f06e17aa5dcf2414ccdba14"),
    "local-lab/ghidra-fullpass-2026-07-23/exports/W003/decompile/00444030_CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold.c": (3338, "cd479637fef534b2cf71f2f8e89e7414db80c6199b0d0417e58dcf9df37c3795"),
    "reverse-engineering/binary-analysis/ghidra-function-name-table-2026-07-27.tsv": (475327, "44f49ca1ccb326b5fb425e1639b6a0650565d7567a6afae96f28414aa9e68b11"),
    "reverse-engineering/binary-analysis/pc-demo-retail-virtual-target-map-2026-08-11.tsv": (1204103, "ba2db0551beeed458ea6265b87d1a5cf93bc2dd2c464da3f7f0c6702a4d4c750"),
    "reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv": (3288437, "cfe90af382269cb2e64996d10df7777bd00fcd8e1844b9823ef74bc6199b8974"),
    "rebuild/OnslaughtRebuild.Core/Level100Destruction.cs": (40342, "295799e0c509ef48ddc10965eca9829034d2a4439e0424339785d9eabee7c72f"),
    "rebuild/OnslaughtRebuild.Core.Tests/Level100DestructionContactTests.cs": (33186, "a2f728debefa6a0ad0d850489e1427959619da1884dffeaa79772005f3e388d2"),
}

RUNS = {
    "level231-damage-window": {
        "trace": ("G:\\bea-ttd\\level-opening-3m-v1-level231\\level-opening-3m-v1-level231.run", 6_190_792_704, "2e2e9c147d44d602408167c9200d2c16adbdf096e9d96737e1aa3494260bfe4f"),
        "window": ("0x199000:0x0", "0x1D0000:0x0"),
        "counts": (18, 6, 6, 6, 0),
    },
    "level110-replication": {
        "trace": ("G:\\bea-ttd\\level-opening-3m-v1-level110\\level-opening-3m-v1-level110.run", 6_924_795_904, "5156445ee5e1078dc3bd76eb52f512edaf1ab4e3c755848bfe95756a6f1daf4c"),
        "window": ("", "0x20E000:0x0"),
        "counts": (27, 9, 9, 8, 1),
    },
    "level854-large-arm": {
        "trace": ("G:\\bea-ttd\\level-opening-3m-v1-level854\\level-opening-3m-v1-level854.run", 7_864_320_000, "f3d3c1227fefd836b6b8e294c22f48de17a81b03384787f050aa5c88bf535f4b"),
        "window": ("", "0x267700:0x0"),
        "counts": (6, 2, 2, 0, 2),
    },
}

CALL_SITE_TO_TARGET = {
    0x0044C061: 0x0040A890,
    0x0044C08E: None,
}
TARGET_CLASS = {
    0x0040A890: "CBattleEngine",
    0x004F68E0: "CTree",
    0x004F9A90: "CUnit",
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


def stack_words(event: dict[str, Any], count: int = 5) -> tuple[int, ...]:
    stack = event.get("stack")
    require(isinstance(stack, dict) and stack.get("query_valid") is True, "call stack is unavailable")
    raw = bytes.fromhex(str(stack.get("hex", "")))
    require(len(raw) >= count * 4, "call stack is too short")
    return struct.unpack_from(f"<{count}I", raw)


def event_projection(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    projected = []
    for row in rows:
        if row.get("kind") not in {"event", "invocation", "gap-summary"}:
            continue
        value = copy.deepcopy(row)
        projected.append(value)
    return projected


def validate_ready_envelope(evidence: Path, lane: str, spec: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    lane_root = evidence / lane
    receipt = read_json(lane_root / "receipt.json")
    manifest = read_json(lane_root / "manifest.json")
    ready = read_json(lane_root / "READY")
    trace_path, trace_bytes, trace_sha = spec["trace"]
    require(receipt.get("schemaVersion") == "bea-ttd-call-context-receipt.v3", f"{lane} receipt schema differs")
    require(receipt.get("collectorExitCode") == 0 and receipt.get("exitCode") == 0 and receipt.get("readyEligible") is True, f"{lane} is not READY")
    require(manifest.get("status") == "READY" and manifest.get("proof", {}).get("collectorChecksPassed") is True, f"{lane} manifest is not READY")
    require(ready.get("schemaVersion") == "bea-ttd-call-context-ready.v3", f"{lane} READY schema differs")
    require(receipt["trace"]["path"] == trace_path and receipt["trace"]["bytes"] == trace_bytes and receipt["trace"]["sha256"].lower() == trace_sha, f"{lane} trace identity differs")
    trace = Path(trace_path)
    require(trace.is_file() and trace.stat().st_size == trace_bytes, f"{lane} retained trace path/size differs")
    require(receipt["target"]["sha256"].lower() == RUNTIME_SHA256, f"{lane} runtime image differs")
    require((receipt["invocation"]["from"], receipt["invocation"]["to"]) == spec["window"], f"{lane} replay window differs")
    require(receipt["invocation"]["stackBytes"] == 128 and receipt["invocation"]["eventLimit"] == 100000, f"{lane} replay limits differ")
    summary = receipt["summary"]
    for key in ("replay_complete", "replay_counters_sane", "ordering_valid", "contexts_valid", "expectations_passed", "pairing_expectations_passed", "collector_checks_passed"):
        require(summary.get(key) is True, f"{lane} summary failed: {key}")
    require(summary.get("truncated") is False and summary.get("callback_failed") is False, f"{lane} replay truncated/failed")
    expected_counts = spec["counts"]
    actual_counts = (
        receipt["callContext"]["eventCount"], receipt["callContext"]["invocationCount"],
        receipt["callContext"]["callEntryPairCount"], receipt["callContext"]["validatedReturnCount"],
        receipt["callContext"]["orphanReturnCount"],
    )
    require(actual_counts == expected_counts, f"{lane} event counts differ")
    require(ready["receiptSha256"].lower() == sha256_file(lane_root / "receipt.json"), f"{lane} READY receipt binding differs")
    require(ready["callContextSha256"].lower() == sha256_file(lane_root / "call-context.jsonl"), f"{lane} READY JSONL binding differs")
    require(ready["manifest"]["sha256"].lower() == sha256_file(lane_root / "manifest.json"), f"{lane} READY manifest binding differs")
    return read_jsonl(lane_root / "call-context.jsonl"), receipt


def call_record(lane: str, event: dict[str, Any]) -> dict[str, Any]:
    words = stack_words(event)
    pc = as_int(event["pc"])
    target = as_int(event["instruction_target"])
    return {
        "lane": lane,
        "position": event["position"],
        "callVa": f"0x{pc:08x}",
        "targetVa": f"0x{target:08x}",
        "targetClass": TARGET_CLASS.get(target, "UNKNOWN"),
        "receiver": f"0x{as_int(event['registers']['ecx']):08x}",
        "receiverVtable": f"0x{as_int(event['registers']['eax' if pc == 0x0044C08E else 'edx']):08x}",
        "damageBits": f"0x{words[1]:08x}",
        "source": f"0x{words[2]:08x}",
        "explosionThis": f"0x{as_int(event['registers']['esi']):08x}",
        "applyShields": words[3],
        "meshPartIndex": struct.unpack("<i", struct.pack("<I", words[4]))[0],
    }


def validate_runtime(root: Path, evidence: Path) -> dict[str, Any]:
    rows_by_lane: dict[str, list[dict[str, Any]]] = {}
    receipts: dict[str, dict[str, Any]] = {}
    calls: list[dict[str, Any]] = []
    direct_parts: list[int] = []
    paired: list[dict[str, Any]] = []
    for lane, spec in RUNS.items():
        rows, receipt = validate_ready_envelope(evidence, lane, spec)
        rows_by_lane[lane] = rows
        receipts[lane] = receipt
        events = [row for row in rows if row.get("kind") == "event" and row.get("event_type") == "call"]
        explosion_events = [row for row in events if as_int(row["pc"]) in CALL_SITE_TO_TARGET]
        calls.extend(call_record(lane, row) for row in explosion_events)
        if lane in {"level231-damage-window", "level110-replication"}:
            unit = [row for row in events if as_int(row["instruction_target"]) == 0x004F9A90]
            require(len(unit) % 2 == 0, f"{lane} CUnit pair count is odd")
            for direct, explosion in zip(unit[0::2], unit[1::2], strict=True):
                require(as_int(direct["pc"]) == 0x004D8CEF and as_int(explosion["pc"]) == 0x0044C08E, f"{lane} direct/explosion call order differs")
                require(as_int(direct["registers"]["ecx"]) == as_int(explosion["registers"]["ecx"]), f"{lane} paired receiver differs")
                direct_words = stack_words(direct)
                explosion_words = stack_words(explosion)
                direct_part = struct.unpack("<i", struct.pack("<I", direct_words[4]))[0]
                explosion_part = struct.unpack("<i", struct.pack("<I", explosion_words[4]))[0]
                direct_parts.append(direct_part)
                paired.append({
                    "lane": lane,
                    "receiver": f"0x{as_int(direct['registers']['ecx']):08x}",
                    "directCallVa": "0x004d8cef",
                    "directDamageBits": f"0x{direct_words[1]:08x}",
                    "directPart": direct_part,
                    "explosionCallVa": "0x0044c08e",
                    "explosionDamageBits": f"0x{explosion_words[1]:08x}",
                    "explosionPart": explosion_part,
                })

    require(len(calls) == 10, "CExplosion call population differs")
    require(Counter(row["callVa"] for row in calls) == Counter({"0x0044c08e": 8, "0x0044c061": 2}), "CExplosion arm counts differ")
    require(Counter(row["targetClass"] for row in calls) == Counter({"CUnit": 6, "CTree": 2, "CBattleEngine": 2}), "CExplosion target classes differ")
    require(all(row["source"] == row["explosionThis"] for row in calls), "CExplosion source is not this")
    require(all(row["applyShields"] == 1 for row in calls), "CExplosion shield carrier differs")
    require(all(row["meshPartIndex"] == -1 for row in calls), "CExplosion mesh-part carrier differs")
    require(all(row["damageBits"] == "0x3f000000" for row in calls if row["callVa"] == "0x0044c08e"), "small-arm damage differs")
    require([row["damageBits"] for row in calls if row["callVa"] == "0x0044c061"] == ["0x3c9429ee", "0x3bd92866"], "large-arm damage differs")
    require(len(paired) == 6 and direct_parts == [8, 0, 1, 0, 0, 8], "direct/explosion CUnit pairs differ")
    require(all(row["explosionPart"] == -1 and row["directPart"] != -1 for row in paired), "direct-part reuse rival survived")

    poison_root = evidence / "level231-poison-cunit-seven"
    poison_receipt = read_json(poison_root / "receipt.json")
    poison_manifest = read_json(poison_root / "manifest.json")
    poison_rows = read_jsonl(poison_root / "call-context.jsonl")
    require(poison_receipt.get("collectorExitCode") == 10 and poison_receipt.get("readyEligible") is False, "poison collector did not refuse")
    require(poison_manifest.get("status") == "BLOCKED" and poison_manifest.get("proof", {}).get("expectationsPassed") is False, "poison manifest did not block")
    require(not (poison_root / "READY").exists(), "poison published READY")
    poison_summary = poison_receipt.get("summary", {})
    require(poison_summary.get("expectations_passed") is False and poison_summary.get("pairing_expectations_passed") is False and poison_summary.get("collector_checks_passed") is False, "poison summary did not fail")
    require(event_projection(poison_rows) == event_projection(rows_by_lane["level231-damage-window"]), "poison changed the observed event stream")
    return {
        "traceIdentityMode": "WRAPPER_HASH_RECEIPT_PLUS_CURRENT_SIZE_NOT_REHASHED_BY_PROOF",
        "sessions": 3,
        "calls": calls,
        "callSiteCounts": {"smallArm0044c08e": 8, "largeArm0044c061": 2},
        "targetClassCounts": {"CUnit": 6, "CTree": 2, "CBattleEngine": 2},
        "directExplosionPairs": paired,
        "directParts": direct_parts,
        "carrier": {"sourceEqualsExplosionThis": True, "applyShields": 1, "meshPartIndex": -1},
        "poisonControl": {
            "kind": "EXPECTED_CUNIT_COUNT_SEVEN",
            "collectorExitCode": 10,
            "readyPublished": False,
            "eventStreamPreserved": True,
            "expectationsPassed": False,
        },
        "receipts": {lane: stamp(evidence / lane / "receipt.json", root) for lane in RUNS},
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
    explosion = body(pristine, EXPLOSION_ENTRY, EXPLOSION_END)
    require(len(explosion) == 479 and sha256_bytes(explosion) == EXPLOSION_BODY_SHA256, "CExplosion body differs")
    require(body(runtime, EXPLOSION_ENTRY, EXPLOSION_END) == explosion, "runtime CExplosion body differs from pristine")
    cunit = body(pristine, 0x004F9A90, 0x004FA4AA)
    segment = body(pristine, 0x00444030, 0x00444158)
    require(sha256_bytes(cunit) == CUNIT_BODY_SHA256, "CUnit ApplyDamage body differs")
    require(sha256_bytes(segment) == SEGMENT_BODY_SHA256, "segment controller body differs")
    instructions = {
        0x0044C03F: "51", 0x0044C040: "6a01", 0x0044C045: "56", 0x0044C046: "51",
        0x0044C05E: "d91c24", 0x0044C061: "ff92a0000000",
        0x0044C073: "51", 0x0044C07C: "6a01", 0x0044C081: "56", 0x0044C082: "51",
        0x0044C08B: "d91c24", 0x0044C08E: "ff90a0000000",
    }
    for va, expected in instructions.items():
        offset = pe_offset(pristine, va)
        require(pristine[offset:offset + len(expected) // 2].hex() == expected, f"carrier instruction differs at 0x{va:08x}")
    cunit_text = (root / "local-lab/damage-chain-pilot-2026-08-02/static/decompile/004f9a90_CUnit__ApplyDamage.c").read_text(encoding="utf-8")
    segment_text = (root / "local-lab/ghidra-fullpass-2026-07-23/exports/W003/decompile/00444030_CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold.c").read_text(encoding="utf-8")
    require("CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold" in cunit_text and "mesh_part_index,damage_amount,damage_source" in cunit_text, "CUnit segment forwarding join differs")
    require("if (segmentIndex != -1)" in segment_text, "segment -1 guard differs")
    name_rows = read_tsv(root / "reverse-engineering/binary-analysis/ghidra-function-name-table-2026-07-27.tsv")
    name = next((row for row in name_rows if row.get("address") == "0x0044bf10"), None)
    require(name is not None and name.get("name") == "CExplosion__Hit", "retail name-table identity differs")
    demo_rows = read_tsv(root / "reverse-engineering/binary-analysis/pc-demo-retail-virtual-target-map-2026-08-11.tsv")
    demo = next((row for row in demo_rows if row.get("retail_va") == "0x0044bf10"), None)
    require(
        demo is not None
        and demo.get("retail_instruction_stream_raw_sha256") == EXPLOSION_BODY_SHA256
        and demo.get("exact_zero_normalized") == "true",
        "PC-demo normalized equivalence differs",
    )
    closure_rows = read_tsv(root / "reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv")
    closure = next((row for row in closure_rows if row.get("entryVa") == "0x0044bf10" or row.get("entry") == "0x0044bf10"), None)
    require(closure is not None and "C1_CANDIDATE_PARTIAL" in closure.values(), "C1 static closure differs")
    return {
        "function": {"entryVa": "0x0044bf10", "endExclusive": "0x0044c0ef", "bytes": 479, "sha256": EXPLOSION_BODY_SHA256, "nameTable": "CExplosion__Hit"},
        "carrierSites": {
            "largeArm": {"meshPush": "0x0044c03f", "shieldPush": "0x0044c040", "sourcePush": "0x0044c045", "damageStore": "0x0044c05e", "call": "0x0044c061"},
            "smallArm": {"meshPush": "0x0044c073", "shieldPush": "0x0044c07c", "sourcePush": "0x0044c081", "damageStore": "0x0044c08b", "call": "0x0044c08e"},
        },
        "cunitApplyDamage": {"entryVa": "0x004f9a90", "bytes": 2586, "sha256": CUNIT_BODY_SHA256, "forwardsControllerBearingReceiver": True},
        "segmentController": {"entryVa": "0x00444030", "bytes": 296, "sha256": SEGMENT_BODY_SHA256, "minusOneSkipsIndexedSegmentDamage": True},
        "pcDemoNormalizedEquivalent": True,
        "staticGradeBeforeRuntime": "C1_CANDIDATE_PARTIAL",
    }


def validate_campaign(root: Path, campaign: Path) -> dict[str, Any]:
    ready_path = campaign / "campaign.ready.json"
    require(sha256_file(ready_path) == CAMPAIGN_READY_SHA256, "Generation 19 READY differs")
    ready = read_json(ready_path)
    require(ready.get("generation") == 19 and ready.get("reducer", {}).get("id") == CAMPAIGN_REDUCER_ID, "Generation 19 identity differs")
    function = next(row for row in read_tsv(campaign / "campaign-functions.tsv") if row["entityKey"] == ENTITY_KEY)
    contract = next(row for row in read_tsv(campaign / "campaign-contracts.tsv") if row["contractId"] == CONTRACT_ID)
    question = next(row for row in read_tsv(campaign / "campaign-questions.tsv") if row["questionId"] == QUESTION_ID)
    require(function["currentName"] == CURRENT_NAME and function["resolutionState"] == "OPEN_JOIN" and function["semanticGrade"] == "OPAQUE" and function["campaignState"] == "OPEN_EXECUTED", "Generation 19 function frontier differs")
    require(contract["entityKey"] == ENTITY_KEY and contract["contractState"] == "OPEN" and contract["semanticGrade"] == "C0_OPAQUE" and contract["refuterVerdict"] == "UNSCORED", "Generation 19 contract frontier differs")
    require(question["entityKey"] == ENTITY_KEY and question["state"] == "OPEN" and question["questionType"] == "EXECUTED_FUNCTION_CONTRACT", "Generation 19 question frontier differs")
    return {"generation": 19, "ready": stamp(ready_path, root), "reducerId": CAMPAIGN_REDUCER_ID, "function": function, "contract": contract, "question": question}


EXPECTED_BOUNDARY = {
    "internalSlot40CallsObserved": 10,
    "independentTraceSessions": 3,
    "bothDamageArmsObserved": True,
    "sourceEqualsExplosionThisAllObservedCalls": True,
    "applyShieldsOneAllObservedCalls": True,
    "meshPartMinusOneAllObservedCalls": True,
    "directPartReuseRefutedForSixCUnitPairs": True,
    "cexplosionEntryObserved": False,
    "cexplosionReturnObserved": False,
    "cexplosionOwnedWritesObserved": False,
    "nonnegativeExplosionPartObserved": False,
    "warehouseOrSegmentControllerReceiverObserved": False,
    "universalCarrierClaim": False,
    "rebuildState": "PARTIAL_CONTRACT",
}


def validate_claim_boundary(value: dict[str, Any]) -> None:
    require(value == EXPECTED_BOUNDARY, "claim boundary differs")


def derive(root: Path, campaign: Path) -> dict[str, Any]:
    evidence = root / EVIDENCE_RELATIVE
    require(evidence.is_dir(), "CExplosion evidence root is missing")
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
        "runtimeImage": {"sha256": RUNTIME_SHA256, "role": "FORCE_WINDOWED_EXISTING_TRACE_IMAGE"},
        "entity": {"entityKey": ENTITY_KEY, "contractId": CONTRACT_ID, "questionId": QUESTION_ID, "currentName": CURRENT_NAME, "nameTableIdentity": "CExplosion__Hit"},
        "campaign": frontier,
        "runtime": runtime,
        "static": static,
        "adjudication": {"semanticGrade": "C2_BOUNDED_RUNTIME", "contractState": "BOUNDED_CONTRACT_ADVANCED", "runtimeVerdict": "MEASURED_BOUNDED_INTERNAL_CALL_CARRIER", "refuterVerdict": "SURVIVED", "questionDisposition": "CLOSE_BASE_AND_OPEN_NARROW_SUCCESSORS"},
        "rebuild": {"state": "PARTIAL_CONTRACT", "owner": inputs["rebuild/OnslaughtRebuild.Core/Level100Destruction.cs"], "test": inputs["rebuild/OnslaughtRebuild.Core.Tests/Level100DestructionContactTests.cs"], "implementation": "Level100DestructionState.ApplyPulseHit", "scope": "whole-body Target Tank/Drone pulse stages only; Warehouse aggregate remains unchanged"},
        "claimBoundary": boundary,
        "limitations": [
            "The retained multi-gigabyte traces are wrapper-hash-bound and current-size-checked, not rehashed by this proof.",
            "The observation starts at CExplosion::Hit's internal slot-40 calls; it does not capture CExplosion::Hit entry, its return, or CExplosion-owned writes.",
            "Every observed explosion part is -1; no nonnegative part path is proved.",
            "No observed receiver is the Level 100 Warehouse or a controller-bearing segmented target, so Warehouse's exact explosion part and damage remain open.",
            "Ten calls across three independent existing trace sessions bound the carrier sample; they do not establish a universal all-level/all-target rule.",
            "CUnit's static controller forwarding and the controller's -1 guard explain the consequence for a controller-bearing receiver but do not prove one was observed here.",
            "The rebuild mapping is PARTIAL_CONTRACT, not REBUILD_READY; no new rebuild change is authorized by this proof.",
            "No game, trace, Ghidra project, or installed executable was mutated while producing this proof.",
        ],
        "inputs": inputs,
        "author": stamp(Path(__file__).resolve(), root),
    }


def selftest(root: Path, campaign: Path) -> dict[str, Any]:
    evidence = root / EVIDENCE_RELATIVE
    positive_rows = read_jsonl(evidence / "level231-damage-window/call-context.jsonl")
    attacks: list[tuple[str, list[dict[str, Any]], str]] = []
    for label, word_index, replacement, expected in (
        ("source", 2, 0, "source is not this"),
        ("shield", 3, 0, "shield carrier differs"),
        ("part", 4, 0, "mesh-part carrier differs"),
    ):
        rows = copy.deepcopy(positive_rows)
        event = next(row for row in rows if row.get("kind") == "event" and row.get("event_type") == "call" and row.get("pc") == "0x44C08E")
        raw = bytearray.fromhex(event["stack"]["hex"])
        struct.pack_into("<I", raw, word_index * 4, replacement)
        event["stack"]["hex"] = raw.hex().upper()
        attacks.append((label, rows, expected))

    rejected: list[str] = []
    for label, rows, expected in attacks:
        try:
            forged = [call_record("selftest", row) for row in rows if row.get("kind") == "event" and row.get("event_type") == "call" and as_int(row["pc"]) in CALL_SITE_TO_TARGET]
            require(all(row["source"] == row["explosionThis"] for row in forged), "source is not this")
            require(all(row["applyShields"] == 1 for row in forged), "shield carrier differs")
            require(all(row["meshPartIndex"] == -1 for row in forged), "mesh-part carrier differs")
        except ProofError as exc:
            require(expected in str(exc), f"{label} rejected by unintended gate: {exc}")
            rejected.append(label)
        else:
            raise ProofError(f"selftest attack accepted: {label}")
    for label, key in (
        ("entry-overclaim", "cexplosionEntryObserved"),
        ("warehouse-overclaim", "warehouseOrSegmentControllerReceiverObserved"),
        ("universal-overclaim", "universalCarrierClaim"),
    ):
        forged = dict(EXPECTED_BOUNDARY)
        forged[key] = True
        try:
            validate_claim_boundary(forged)
        except ProofError:
            rejected.append(label)
        else:
            raise ProofError(f"selftest attack accepted: {label}")
    require(validate_campaign(root, campaign)["generation"] == 19, "selftest campaign gate failed")
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
        str((root / "reverse-engineering/binary-analysis/cround-hit-damage-path-2026-08-10.md").resolve()),
    ]
    row = dict(base)
    row.update({
        "contractState": "RUNTIME_CANDIDATE_NEEDS_REFUTER",
        "semanticGrade": "C2_BOUNDED_RUNTIME",
        "receiver": "ten observed struck-thing receivers dispatching slot 40: six CUnit, two CTree, two CBattleEngine",
        "inputs": "internal slot-40 carrier: computed float32 damage; source CExplosion*=this; applyShields=1; meshPartIndex=-1 in all ten observed calls",
        "returns": "callee return envelopes: eight validated, two raw orphan returns; CExplosion::Hit entry/return itself unobserved",
        "writes": "not measured for CExplosion::Hit; callee side effects remain owned by their target contracts",
        "sideEffects": "dispatches radial damage through target vtable slot 40; six CUnit pairs prove the explosion call does not reuse direct parts 8/0/1/0/0/8",
        "preconditions": "three named existing retail trace windows where the internal small or large damage arm reaches a concrete slot-40 target",
        "failureModes": "no-call filters, nonnegative recorded part, controller-bearing segmented receiver, and CExplosion entry/return/write paths remain open",
        "authorVerdict": "SUPPORTED_BY_PRISTINE_STATIC_JOIN_AND_THREE_INDEPENDENT_TTD_TRACE_SESSIONS",
        "runtimeVerdict": "MEASURED_BOUNDED_INTERNAL_CALL_CARRIER",
        "refuterVerdict": "UNSCORED",
        "questionIds": QUESTION_ID,
        "evidenceRefs": ";".join(evidence_refs),
        "cheapestFalsifier": "Capture a controller-bearing segmented CExplosion receiver or a nonnegative explosion part and compare the exact slot-40 carrier.",
        "rebuildOwner": "rebuild/OnslaughtRebuild.Core/Level100Destruction.cs",
        "rebuildImplementation": "Level100DestructionState.ApplyPulseHit",
        "parityTests": "Level100DestructionContactTests.PulseHitPreservesDirectThenExplosionDamageOrder",
        "rebuildState": "PARTIAL_CONTRACT",
        "remainingUncertainty": "CExplosion entry/return and owned writes; nonnegative part path; controller-bearing receiver; Level 100 Warehouse exact explosion part/damage",
        "lastMeasurementDate": "2026-08-12",
        "scopeKind": "EXISTING_TTD_THREE_TRACE_INTERNAL_SLOT40_CALL_CARRIER",
        "payloadSha256": "",
        "receiverVtable": "0x005e24dc;0x005e297c;0x005dd9d8;0x005d89c4",
        "observedCallVas": "0x0044c061;0x0044c08e",
        "controlSummary": "Level231 CUnit expected-count poison 7 versus observed 6 exited 10, failed expectations/pairing/collector checks, and published no READY while preserving the event stream",
        "runtimeEvidenceSha256": ";".join(saved["inputs"][f"{lane}/call-context.jsonl"]["sha256"] for lane in ("level231-damage-window", "level110-replication", "level854-large-arm")),
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
            relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / "level231-damage-window/call-context.jsonl", "runtime-level231"),
            relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / "level110-replication/call-context.jsonl", "runtime-level110"),
            relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / "level854-large-arm/call-context.jsonl", "runtime-level854"),
            relative_artifact(proof / READY_NAME, root / EVIDENCE_RELATIVE / "level231-poison-cunit-seven/call-context.jsonl", "poison-level231"),
            relative_artifact(proof / READY_NAME, root / "local-lab/cround-explosion-semantic-20260810-v1/decompile/0044bf10_HYP__CombatAiStaticBody__0044bf10.c", "static-cexplosion"),
            relative_artifact(proof / READY_NAME, root / "local-lab/damage-chain-pilot-2026-08-02/static/decompile/004f9a90_CUnit__ApplyDamage.c", "static-cunit"),
            relative_artifact(proof / READY_NAME, root / "local-lab/ghidra-fullpass-2026-07-23/exports/W003/decompile/00444030_CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold.c", "static-segment-controller"),
            relative_artifact(proof / READY_NAME, root / "rebuild/OnslaughtRebuild.Core/Level100Destruction.cs", "rebuild-owner"),
            relative_artifact(proof / READY_NAME, root / "rebuild/OnslaughtRebuild.Core.Tests/Level100DestructionContactTests.cs", "rebuild-test"),
        ]
        receipt = {
            "schema": OVERLAY_SCHEMA,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "sourceCampaign": {"path": str(campaign.resolve()), "ready": stamp(campaign / "campaign.ready.json"), "specimen": read_json(campaign / "campaign.ready.json")["sourceSnapshot"]["specimen"]},
            "inputContract": stamp(proof / READY_NAME),
            "artifacts": artifacts,
            "authorVerification": {"checks": saved["selftest"], "claimBoundary": saved["claimBoundary"]},
            "count": 1,
            "policy": {"namesAuthorized": False, "ghidraMutationAuthorized": False, "promotionAuthorized": False, "requiresRefuter": True, "maximumImportedGrade": "C2_BOUNDED_RUNTIME", "artifactClaimsParsed": True, "runtimeExecutableRelationValidated": True},
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
    row = read_tsv(overlay / "runtime-contracts.tsv")
    require(len(row) == 1, "overlay row count differs")
    canonical = json.dumps(row[0], sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "schema": REFUTER_SUBJECT_SCHEMA,
        "baseContractId": row[0]["baseContractId"],
        "entityKey": row[0]["entityKey"],
        "overlayReadySha256": sha256_file(overlay / "runtime-contracts.ready.json"),
        "questionIdsAddressed": [value for value in row[0]["questionIdsAddressed"].split(";") if value],
        "candidateRowSha256": sha256_bytes(canonical),
    }


def build_finding(root: Path, proof: Path, overlay: Path, out: Path) -> Path:
    saved = read_json(proof / READY_NAME)
    subject = overlay_subject(overlay)
    finding = {
        "schemaVersion": 1,
        "id": "cexplosion-hit-slot40-carrier-2026-08-12",
        "title": "CExplosion Hit internal slot-40 argument carrier across three existing traces",
        "date": "2026-08-12",
        "lane": "ttd/existing-trace",
        "author": "recursive RE campaign",
        "sourceNote": str((proof / READY_NAME).resolve()),
        "findingKind": "instrument-derived",
        "claim": {"statement": "In the three retained trace sessions, every observed CExplosion::Hit internal slot-40 call carried source=this, applyShields=1, and meshPartIndex=-1.", "grade": "EXECUTED", "mechanism": ["cexplosion.slot40_argument_carrier"]},
        "scope": {"population": "ten CExplosion::Hit internal slot-40 calls in the named Level 231, 110, and 854 trace windows", "covered": "eight small-arm calls and two large-arm calls targeting six CUnit, two CTree, and two CBattleEngine implementations", "notCovered": ["CExplosion::Hit entry, return, and owned writes", "nonnegative explosion mesh parts", "controller-bearing segmented receivers and the Level 100 Warehouse", "all levels, targets, branches, and explosion configurations"]},
        "rivals": [
            {"id": "rival-branch-carrier", "statement": "The small and large CExplosion damage arms use different source, shield, or mesh-part carriers.", "indistinguishableOn": ["static decompiler type recovery alone", "coverage presence at both call sites"], "discriminator": {"description": "capture raw stacks at both slot-40 calls in independent retained traces", "mechanism": ["cexplosion.slot40_argument_carrier"], "expectedUnderClaim": "both arms carry explosion this, literal 1, and -1", "expectedUnderRival": "at least one large-arm or small-arm carrier differs", "status": "observed", "outcome": "claim", "evidenceRef": ["e-level231", "e-level110", "e-level854"]}},
            {"id": "rival-direct-part-reuse", "statement": "The explosion call reuses the direct CRound hit's collision mesh part on paired CUnit damage.", "indistinguishableOn": ["damage calls landing on the same receiver", "a pair where the direct part were also -1"], "discriminator": {"description": "pair consecutive direct and explosion CUnit calls on the same receiver and compare raw mesh-part words", "mechanism": ["cexplosion.slot40_argument_carrier"], "expectedUnderClaim": "direct parts 8/0/1/0/0/8 contrast with explosion -1", "expectedUnderRival": "each explosion part equals its paired direct part", "status": "observed", "outcome": "claim", "evidenceRef": ["e-level231", "e-level110"]}},
        ],
        "predictions": [
            {"id": "p-independent-small-arm", "statement": "Level 110 reproduces the Level 231 small-arm source/1/-1 carrier", "procedure": "replay the preregistered target table through Level 110 to 0x20E000 and parse call stacks at 0x0044C08E", "expected": "every small-arm call carries source equal ESI, shield 1, and part -1", "wouldFalsifyIf": "any carrier differs or the replay envelope fails", "predictedInAdvance": True, "statedAt": "local-lab/cexplosion-hit-existing-trace-20260812-v1/preregistration.md", "result": "match", "observed": "five Level 110 small-arm calls reproduce source=this, shield 1, part -1", "evidenceRef": ["e-level110"]},
            {"id": "p-large-arm-carrier", "statement": "The Level 854 large arm changes damage arithmetic but preserves source/1/-1", "procedure": "replay Level 854 to 0x267700 and parse call stacks at 0x0044C061", "expected": "both calls carry source equal ESI, shield 1, and part -1", "wouldFalsifyIf": "either call uses a different carrier", "predictedInAdvance": True, "statedAt": "local-lab/cexplosion-hit-existing-trace-20260812-v1/preregistration.md", "result": "match", "observed": "two large-arm calls with damage bits 0x3C9429EE/0x3BD92866 carry source=this, shield 1, part -1", "evidenceRef": ["e-level854"]},
        ],
        "evidence": [
            {"id": "e-level231", "grade": "EXECUTED", "instrument": "hash-pinned TTD schema-v3 call-context replay", "summary": "three small-arm CUnit explosion calls paired with direct parts 8, 0, and 1", "sample": {"n": 3, "units": "internal CExplosion slot-40 calls", "independentReplicates": 1, "sessions": 1}, "specimen": {"path": RUNS["level231-damage-window"]["trace"][0], "sha256": RUNS["level231-damage-window"]["trace"][2]}},
            {"id": "e-level110", "grade": "EXECUTED", "instrument": "hash-pinned TTD schema-v3 call-context replay", "summary": "three CUnit and two CTree small-arm calls; direct CUnit parts 0, 0, and 8", "sample": {"n": 5, "units": "internal CExplosion slot-40 calls", "independentReplicates": 1, "sessions": 1}, "specimen": {"path": RUNS["level110-replication"]["trace"][0], "sha256": RUNS["level110-replication"]["trace"][2]}},
            {"id": "e-level854", "grade": "EXECUTED", "instrument": "hash-pinned TTD schema-v3 call-context replay", "summary": "two large-arm calls to CBattleEngine::Damage", "sample": {"n": 2, "units": "internal CExplosion slot-40 calls", "independentReplicates": 1, "sessions": 1}, "specimen": {"path": RUNS["level854-large-arm"]["trace"][0], "sha256": RUNS["level854-large-arm"]["trace"][2]}},
        ],
        "residuals": [
            {"id": "res-warehouse", "statement": "No controller-bearing segmented receiver or Level 100 Warehouse was observed.", "mechanism": ["cexplosion.segmented_mesh_part"], "blocksClaim": False},
            {"id": "res-entry-return-writes", "statement": "The retained probe begins at internal calls and does not measure CExplosion entry, return, or owned writes.", "mechanism": ["cexplosion.function_envelope"], "blocksClaim": False},
            {"id": "res-population", "statement": "Three sessions and ten calls do not prove a universal carrier outside the named sample.", "mechanism": ["cexplosion.population_scope"], "blocksClaim": False},
        ],
        "poisonControl": {"id": "control-cunit-seven", "kind": "poison", "description": "the Level 231 target table falsely requires seven CUnit calls, entries, and returns although the retained trace contains six", "predictedOutcome": "collector exits nonzero, fails expectations, and publishes no READY while preserving observed events", "observedOutcome": "exit 10; expectations, pairing expectations, and collector checks false; no READY; event projection identical", "result": "failed_as_predicted"},
        "overturnedBy": [
            {"id": "kill-sampled-carrier", "procedure": "replay another hash-pinned trace and capture a CExplosion internal slot-40 call whose source, shield flag, or mesh part differs", "wouldShow": "the three-trace sample does not extend to that observed call", "cost": "one bounded existing-trace replay"},
            {"id": "kill-segment-rival", "procedure": "capture a controller-bearing segmented receiver with a nonnegative report part and compare its raw carrier", "wouldShow": "the -1 carrier is branch- or report-specific and cannot describe the segmented path", "cost": "one targeted existing trace or authored safe-copy scenario"},
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
            "terminalState": "",
            "measuredAtUtc": measured,
            "remainingUncertainty": "CExplosion entry/return and owned writes remain unobserved; no nonnegative part or controller-bearing segmented receiver identifies the Level 100 Warehouse explosion carrier.",
            "nextQuestions": [
                {"questionType": "SEGMENTED_EXPLOSION_MESH_PART", "question": "What exact mesh-part carrier and resulting damage reach a controller-bearing segmented CExplosion receiver, including the Level 100 Warehouse if obtainable?", "recommendedInstrument": "EXISTING_TRACE_OR_AUTHORED_SAFE_COPY_SEGMENTED_RECEIVER_PROBE", "cheapestFalsifier": "Capture one controller-bearing receiver at 0x0044C061/0x0044C08E with the raw report part and callee entry.", "requiresElevation": False, "priority": 1, "score": 500.0, "source": "CExplosion Hit Gen20 adjudication", "currentOwner": "recursive-re-campaign"},
                {"questionType": "CEXPLOSION_FUNCTION_ENVELOPE", "question": "What entry inputs, returns, owned writes, expanding-radius ordering, and filter/failure behavior complete CExplosion::Hit beyond its internal slot-40 carrier?", "recommendedInstrument": "TTD_ENTRY_RETURN_DATA_WRITE_ENVELOPE", "cheapestFalsifier": "Capture one gap-accounted CExplosion::Hit entry through return with preregistered owner-field watches and a no-call/filter control.", "requiresElevation": False, "priority": 2, "score": 479.0, "source": "CExplosion Hit Gen20 adjudication", "currentOwner": "recursive-re-campaign"},
            ],
            "rebuildMapping": {"rebuildOwner": "rebuild/OnslaughtRebuild.Core/Level100Destruction.cs", "rebuildImplementation": "Level100DestructionState.ApplyPulseHit", "parityTests": "Level100DestructionContactTests.PulseHitPreservesDirectThenExplosionDamageOrder", "rebuildState": "PARTIAL_CONTRACT"},
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
            print(f"CEXPLOSION_HIT_RUNTIME_PROOF_READY {stamp(path)}")
        elif args.command == "verify":
            value = verify(root, campaign, args.proof.resolve())
            print(f"CEXPLOSION_HIT_RUNTIME_PROOF_VERIFIED verdict={value['verdict']} calls={value['runtime']['claimBoundary'] if 'claimBoundary' in value['runtime'] else len(value['runtime']['calls'])}")
        elif args.command == "selftest":
            value = selftest(root, campaign)
            print(f"CEXPLOSION_HIT_RUNTIME_SELFTEST_OK attacks={value['count']}")
        elif args.command == "overlay":
            path = build_overlay(root, campaign, args.proof.resolve(), args.out.resolve())
            print(f"CEXPLOSION_HIT_RUNTIME_OVERLAY_READY {stamp(path)}")
        elif args.command == "finding":
            path = build_finding(root, args.proof.resolve(), args.overlay.resolve(), args.out.resolve())
            print(f"CEXPLOSION_HIT_RUNTIME_FINDING_READY {stamp(path)}")
        else:
            path = build_adjudication(campaign, args.overlay.resolve(), args.finding.resolve(), args.result.resolve(), args.out.resolve())
            print(f"CEXPLOSION_HIT_RUNTIME_ADJUDICATION_READY {stamp(path)}")
        return 0
    except (ProofError, OSError, ValueError, KeyError, struct.error) as exc:
        print(f"CEXPLOSION_HIT_RUNTIME_REFUSED: {exc}", file=os.sys.stderr)
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
