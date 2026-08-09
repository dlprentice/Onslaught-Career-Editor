#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Package the regenerated bounded CUnit::ApplyDamage TTD contract.

This owner reuses one retained authored Level 100 trace.  It does not record
gameplay, mutate Ghidra, or treat the deleted CDB logs as primary evidence.
It proves one exact call entry and two exact field-write pairs, preserves the
known replay gap that prevents return association, and requires a replicated
positive plus a real expectation-poison refusal.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import struct
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "bea.re.cunit-applydamage-primary-ttd-reproof.v1"
CLAIM = "CUNIT_APPLYDAMAGE_ENTRY_AND_ZERO_SHIELD_OVERKILL_C2_BOUNDED"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
RUNTIME_SHA256 = "e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4"
TRACE_SHA256 = "994a6aa99444176ec4b8985d03bd95549a07f9eead6e41492a24c4567c9befcd"
TRACE_BYTES = 25_769_803_776
TRACE_PATH = Path(r"G:\bea-ttd\damage-script-level100-20260802-a\damage-script-level100-20260802-a.run")
EVIDENCE_RELATIVE = Path("local-lab/applydamage-primary-ttd-reproof-20260809-v1")
READY_NAME = "proof.ready.json"
PARENT_READY_SHA256 = "9d2b903d451cb62fd6fb599b915dd57a0e6f313e610a348022fabf26ee265747"
PARENT_REDUCER_ID = "1bcd8b1bff0bd9182872c221df8060aff8da263a89d94052ede2e80127812385"
PARENT_AUTHORITY_SHA256 = "c3531b495084ec73fc2b76a70be3409ca120448ba6831cbfa96a70866e182cba"
ENTRY = 0x004F9A90
END_EXCLUSIVE = 0x004FA4AA
BODY_BYTES = END_EXCLUSIVE - ENTRY
RAW_BODY_SHA256 = "c00c805fc86ad1f52e6ab7d8fc739c456983914319ad99870d49c88b8733f859"
GHIDRA_BODY_DIGEST = "6d887e5b714b5c78474870ba56e04925a0b1652f2464f9484a4d03d26e353e45"
ENTITY_KEY = (
    "CODE:" + SPECIMEN_SHA256 +
    ":VA=0x004f9a90:RANGES=3c07541ed870843444b66909c62014e975fc8f43c349891da0e9129654016c97"
)
CONTRACT_ID = "C-76bfed114f4326d4"
QUESTION_ID = "Q-178b10ce57ab15db"
RECEIVER = 0x080DC630
SOURCE = 0x080E1A10
RETURN_ADDRESS = 0x005348E9
CALL_PC = 0x005348E3
LIFE_ADDRESS = RECEIVER + 0xF8
SHIELD_ADDRESS = RECEIVER + 0x100
VTABLE = 0x005E24DC
CALL_NEUTRAL_SHA256 = "4c6600a28e7380969ba5f37571b560495ac2408f28bb5258fe2a986af3a9f2c2"
WRITES_NEUTRAL_SHA256 = "ac74050f870d129628ec09a950468ad31a3bff9bc6861f4a626d51c4531f0015"


EXPECTED: dict[str, tuple[int, str]] = {
    "preregistration.md": (1642, "3d5258eddd31ad2e422b33e3a0f790876b08841b425442628c07c1b2c6547cd6"),
    "call-targets.tsv": (190, "00e1fdf3d38c97bec6c93c76a58e226aaf953c777c4e1398d9c52d93c3dce6ba"),
    "data-targets-discovery.tsv": (123, "5cb422f4e78373376720b968eec6030bd9c114f0075534e3815eddfcb8b5754b"),
    "data-targets-closed.tsv": (129, "73a6fc5e3459b6a2a03c1f0d9eafa6a9aa8db78ccb9662681af49e6efd645e87"),
    "data-targets-poison-life-two.tsv": (129, "3abf8c1fd263abe9e5d4033ab912b815bc81c5b6132432da4aee04b4c0c15086"),
    "call-run-a-v2/call-context.jsonl": (7416, "9a70a5bd2edf26d777a297b6ed8bcd91da552c7a061e6df51b7adc21aa5dd226"),
    "call-run-a-v2/receipt.json": (7657, "90deaf56197baa4573b8693f111b47cccde1afa384e94468a948aa795c98d5fb"),
    "call-run-a-v2/READY": (568, "0d027afeaed658461b72b9681205d94b94c115d711a21ddcc04cec6f4f553f5f"),
    "call-run-b/call-context.jsonl": (7413, "b376ce3d740b2e1197699313ebab7c24d314cc23b030331f46b930688c2b544b"),
    "call-run-b/receipt.json": (7637, "a6ce0589dd71c58970843d9a592b35a44e476f5a9191a17301b55d25e5f77c44"),
    "call-run-b/READY": (565, "6fa2a7715704b9e51e31685b605f05f5d3e27cb58a7dca874d3871e31f510b27"),
    "writes-run-a-discovery/data-writes.jsonl": (11374, "f36ceb3bbdc992b6a1e4c4c9e72a80fabcb4e36fa540c405334c1f70e948ac4c"),
    "writes-run-a-discovery/receipt.json": (10126, "1e6a63857d80eabcd28ff0304c968321ddbd3929c27d0ceb7dc9e1abb329821a"),
    "writes-run-a-closed/data-writes.jsonl": (11385, "c51db0d157c30e82110a6e9b3e0c6bd1c000e02cf05b153423518ba6a05b2c64"),
    "writes-run-a-closed/receipt.json": (10080, "0db25db06b7401ad313ca1209b8c013c9db217dac0a72f9ec1f40c1f95cbff50"),
    "writes-run-a-closed/READY_WITNESSED_WRITES": (1502, "8c68ee20bf539cf5bcc8515abb459f82002e41fd133f1c34060819efdc024904"),
    "writes-run-b-closed/data-writes.jsonl": (11385, "14ffadb06afc07f95e9e246d65d0b9e60844f9670707ffe68937ca93e811f4f4"),
    "writes-run-b-closed/receipt.json": (10079, "26d7669b55b9488af0b2b59b8c4d3bad090de28ce87178eb2ea6da34753388e8"),
    "writes-run-b-closed/READY_WITNESSED_WRITES": (1502, "3e26693b324bf7c146f0fefb1e7110d6b22c9ff81b7645d6b32d120ed48d1dda"),
    "writes-poison-life-two/data-writes.jsonl": (11378, "31bb2ee0298184876cf057c5f1bf1fce72b0c68834fa7c50a7d4c55c37484f3b"),
    "writes-poison-life-two/receipt.json": (10176, "391597dd9b5a88d083f820fe21071b0d3ffc4db2ba23cb18cdcd54462f9f7d96"),
}

REPO_INPUTS: dict[str, tuple[int, str]] = {
    "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup": (2_506_752, SPECIMEN_SHA256),
    "local-lab/safe-copy-bea-pristine/BEA.exe": (2_506_752, RUNTIME_SHA256),
    "local-lab/damage-chain-pilot-2026-08-02/static/damage-instructions.tsv": (117518, "9a1cbacc1da7af8731a99250f7f3679cfd31b90ef3127a17bea4da3906952800"),
    "local-lab/damage-chain-pilot-2026-08-02/static/decompile/004f9a90_CUnit__ApplyDamage.c": (20732, "71e926df3a4817c546db0886fffa155705a5335c4f06e17aa5dcf2414ccdba14"),
    "local-lab/ghidra-damage-hit-semantic-live-promotion-20260809-v1/runs-v2/live-post-inventory/functions.tsv": (7051668, "075165bae3616dda0adf534625db612990daee9974b3fc85429d3b5b408ee979"),
    "local-lab/re-campaign-incident-recovery-20260808-v1/generation-12-level521-damage-hit-writes-v1/campaign.ready.json": (17110, PARENT_READY_SHA256),
    "local-lab/re-campaign-incident-recovery-20260808-v1/generation-12-level521-damage-hit-writes-v1/campaign-functions.tsv": (5129730, "f129dcb3f894cb3822fb320e7627b487a345b1c7b64183c4a79d87b9d764a516"),
    "local-lab/re-campaign-incident-recovery-20260808-v1/generation-12-level521-damage-hit-writes-v1/campaign-contracts.tsv": (10901722, "da9e8cbc0afe26a6d83cd68e6cab289d17a12f7a3818bf1dc2da193aca6a23da"),
    "local-lab/re-campaign-incident-recovery-20260808-v1/generation-12-level521-damage-hit-writes-v1/campaign-questions.tsv": (8363102, "86f1d48e2f92950926a3acfe7b3c4219ad778e3b2e19c627202b7053f5866782"),
    "local-lab/re-campaign-incident-recovery-20260808-v1/generation-12-level521-damage-hit-writes-authority.ready.json": (8456, PARENT_AUTHORITY_SHA256),
}


class ProofError(ValueError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise ProofError(message)


def root_path() -> Path:
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


def stamp(path: Path, root: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing file: {path}")
    try:
        name = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        name = str(path.resolve())
    return {"path": name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProofError(f"cannot parse {path}: {exc}") from exc
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def read_jsonl(path: Path) -> tuple[list[dict[str, Any]], bytes]:
    lines = path.read_bytes().splitlines(keepends=True)
    try:
        rows = [json.loads(line) for line in lines]
    except json.JSONDecodeError as exc:
        raise ProofError(f"invalid JSONL {path}: {exc}") from exc
    require(all(isinstance(row, dict) for row in rows), f"non-object JSONL row: {path}")
    neutral = b"".join(line for line, row in zip(lines, rows) if row.get("kind") != "metadata")
    return rows, neutral


def campaign_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        require(stream.readline().rstrip("\r\n") == "# bea.re.campaign.v5", f"campaign schema marker differs: {path}")
        return list(csv.DictReader(stream, delimiter="\t"))


def by_kind(rows: list[dict[str, Any]], kind: str) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("kind") == kind]


def as_int(value: Any) -> int:
    return int(str(value), 0)


def f32(hex_bytes: str) -> float:
    raw = bytes.fromhex(hex_bytes)
    require(len(raw) == 4, "float evidence is not four bytes")
    return struct.unpack("<f", raw)[0]


def exact_inputs(root: Path, evidence: Path) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for relative, (size, digest) in sorted(EXPECTED.items()):
        actual = stamp(evidence / relative, root)
        require((actual["bytes"], actual["sha256"]) == (size, digest), f"evidence identity differs: {relative}")
        output[relative] = actual
    for relative, (size, digest) in sorted(REPO_INPUTS.items()):
        actual = stamp(root / relative, root)
        require((actual["bytes"], actual["sha256"]) == (size, digest), f"repository input differs: {relative}")
        output[relative] = actual
    return output


def validate_receipt_common(receipt: dict[str, Any]) -> None:
    require(receipt["trace"]["bytes"] == TRACE_BYTES, "trace byte count differs")
    require(receipt["trace"]["sha256"].lower() == TRACE_SHA256, "trace receipt hash differs")
    require(receipt["target"]["sha256"].lower() == RUNTIME_SHA256, "runtime image differs")
    require(receipt["invocation"]["moduleName"] == "BEA.exe", "module differs")
    require(receipt["invocation"]["expectedBase"] == "0x00400000", "module base differs")
    require(receipt["invocation"]["from"] == "0x195B5C:0x80", "window start differs")
    require(receipt["invocation"]["to"] == "0x195B74:0x200", "window end differs")
    require(receipt["summary"]["replay_complete"] is True, "replay incomplete")
    require(receipt["summary"]["truncated"] is False, "replay truncated")


def validate_call(root: Path, evidence: Path) -> dict[str, Any]:
    neutral_values: list[bytes] = []
    for lane in ("call-run-a-v2", "call-run-b"):
        receipt = read_json(evidence / lane / "receipt.json")
        validate_receipt_common(receipt)
        require(receipt["schemaVersion"] == "bea-ttd-call-context-receipt.v3", "call receipt schema differs")
        require(receipt["readyEligible"] is True and receipt["collectorExitCode"] == 0, "call receipt is not READY")
        require(receipt["invocation"]["stackBytes"] == 64 and receipt["invocation"]["eventLimit"] == 64, "call limits differ")
        rows, neutral = read_jsonl(evidence / lane / "call-context.jsonl")
        neutral_values.append(neutral)
        targets = by_kind(rows, "target")
        require(len(targets) == 2, "call target count differs")
        positive, negative = targets
        require(positive["entry_va"] == "0x4F9A90" and positive["observed_call_count"] == "1", "ApplyDamage call count differs")
        require(positive["observed_entry_count"] == "1" and positive["observed_return_count"] == "1", "ApplyDamage event counts differ")
        require(positive["observed_validated_return_count"] == "0" and positive["observed_orphan_return_count"] == "1", "return-withhold counts differ")
        require(negative["entry_va"] == "0x42CFA0" and negative["observed_call_count"] == "0", "negative call control differs")
        events = by_kind(rows, "event")
        require([row["event_type"] for row in events] == ["call", "entry", "return"], "call event order differs")
        call, entry, returned = events
        require(as_int(call["pc"]) == CALL_PC and as_int(call["instruction_target"]) == ENTRY, "call edge differs")
        require(as_int(call["fallthrough"]) == RETURN_ADDRESS, "call fallthrough differs")
        require(as_int(entry["pc"]) == ENTRY and as_int(entry["registers"]["ecx"]) == RECEIVER, "entry receiver differs")
        non_pc_registers = ("eax", "ebx", "ecx", "edx", "esi", "edi", "ebp", "esp", "eflags")
        require(
            all(call["registers"][name] == entry["registers"][name] for name in non_pc_registers)
            and call["stack"] == entry["stack"],
            "pre-call and entry non-PC state differ",
        )
        stack = bytes.fromhex(entry["stack"]["hex"])
        require(len(stack) == 64 and entry["stack"]["query_valid"] is True, "entry stack is incomplete")
        words = struct.unpack_from("<5I", stack)
        require(words == (RETURN_ADDRESS, 0x447A0000, SOURCE, 1, 0xFFFFFFFF), "entry stack ABI differs")
        require(as_int(returned["pc"]) == 0x004FA4A7 and returned["instruction_bytes"]["hex"] == "C21000", "raw return differs")
        require(as_int(returned["instruction_target"]) == RETURN_ADDRESS and returned["decoded_near_return"] is True, "raw return target differs")
        invocation = by_kind(rows, "invocation")
        require(len(invocation) == 1, "invocation count differs")
        require(invocation[0]["grade"] == "CALL_ENTRY" and invocation[0]["gap_crossed"] is True, "gap-aware call grade differs")
        require(invocation[0]["return_event_index"] is None and invocation[0]["return_checks_passed"] is False, "return was incorrectly associated")
        summary = by_kind(rows, "summary")[0]
        require(summary["collector_checks_passed"] is True and summary["expectations_passed"] is True, "call collector checks failed")
    require(neutral_values[0] == neutral_values[1], "call replicas differ outside metadata")
    require(sha256_bytes(neutral_values[0]) == CALL_NEUTRAL_SHA256, "call neutral hash differs")
    return {
        "replicas": 2,
        "nonMetadataBytes": len(neutral_values[0]),
        "nonMetadataSha256": CALL_NEUTRAL_SHA256,
        "callPosition": "0x195B5C:0x98",
        "entryPosition": "0x195B5C:0x99",
        "rawReturnPosition": "0x195B74:0x18C",
        "returnAssociation": "WITHHELD_RECORDED_GAP",
        "receiver": "0x080dc630",
        "returnAddress": "0x005348e9",
        "arguments": {
            "damageAmountBits": "0x447a0000",
            "damageAmountF32": 1000.0,
            "damageSource": "0x080e1a10",
            "applyShields": 1,
            "meshPartIndex": -1,
        },
    }


def event_projection(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("kind") in {"event", "pair", "continuity-break", "gap-summary"}]


def validate_writes(evidence: Path) -> dict[str, Any]:
    neutral_values: list[bytes] = []
    positive_rows: list[list[dict[str, Any]]] = []
    for lane in ("writes-run-a-closed", "writes-run-b-closed"):
        receipt = read_json(evidence / lane / "receipt.json")
        validate_receipt_common(receipt)
        require(receipt["schemaVersion"] == "bea-ttd-data-writes-receipt.v3", "write receipt schema differs")
        require(receipt["witnessedWritesEligible"] is True, "witnessed-write grade withheld")
        require(receipt["readyEligible"] is False and receipt["readyGapFreeEligible"] is False, "gap-free grade was invented")
        require(receipt["witnessedGrade"]["reasons"] == [] and receipt["witnessedGrade"]["outOfBodyPcs"] == [], "write grade reasons differ")
        require(receipt["witnessedGrade"]["writerBodyRanges"] == ["0x4F9A90:0x4FA4AA"], "writer range differs")
        require(not (evidence / lane / "READY").exists(), "gap-free READY unexpectedly exists")
        require((evidence / lane / "READY_WITNESSED_WRITES").is_file(), "witnessed marker is missing")
        rows, neutral = read_jsonl(evidence / lane / "data-writes.jsonl")
        neutral_values.append(neutral)
        positive_rows.append(rows)
        targets = by_kind(rows, "target")
        require(len(targets) == 3, "write target count differs")
        vtable, life, shield = targets
        require(as_int(vtable["address"]) == RECEIVER and vtable["observed_write_count"] == "0", "vtable control differs")
        require(vtable["evidence_grade"] == "NO_WRITE_CALLBACK_WITNESS" and vtable["initial_memory"]["hex"] == "DC245E00", "vtable control grade differs")
        require(as_int(life["address"]) == LIFE_ADDRESS and life["observed_write_count"] == "1", "life write count differs")
        require(life["initial_memory"]["hex"] == "0BD7A33B" and life["final_memory"]["hex"] == "AEFF79C4", "life transition differs")
        require(life["evidence_grade"] == "WATCHPOINT_CHAIN_CLOSED", "life chain did not close")
        require(as_int(shield["address"]) == SHIELD_ADDRESS and shield["observed_write_count"] == "1", "shield write count differs")
        require(shield["initial_memory"]["hex"] == "00000000" and shield["final_memory"]["hex"] == "00000000", "shield transition differs")
        require(shield["evidence_grade"] == "WATCHPOINT_CHAIN_CLOSED", "shield chain did not close")
        events = by_kind(rows, "event")
        require(len(events) == 4 and [as_int(row["pc"]) for row in events] == [0x4F9E50, 0x4F9E50, 0x4F9E6E, 0x4F9E6E], "writer PCs differ")
        require(all(as_int(row["registers"]["esi"]) == RECEIVER for row in events), "writer receiver differs")
        pairs = by_kind(rows, "pair")
        require(len(pairs) == 2 and pairs[0]["changed"] is False and pairs[1]["changed"] is True, "write-pair change flags differ")
        summary = by_kind(rows, "summary")[0]
        require(summary["expectations_passed"] is True and summary["target_evidence_passed"] is True, "write expectations failed")
        require(summary["pairing_complete"] is True and summary["replay_complete"] is True, "write replay is incomplete")
    require(neutral_values[0] == neutral_values[1], "write replicas differ outside metadata")
    require(sha256_bytes(neutral_values[0]) == WRITES_NEUTRAL_SHA256, "write neutral hash differs")

    poison_receipt = read_json(evidence / "writes-poison-life-two/receipt.json")
    validate_receipt_common(poison_receipt)
    require(poison_receipt["witnessedWritesEligible"] is False, "count poison was admitted")
    require(poison_receipt["summary"]["expectations_passed"] is False, "count poison expectation unexpectedly passed")
    require(poison_receipt["witnessedGrade"]["reasons"] == ["expectations_failed", "target_evidence_failed"], "count poison reasons differ")
    require(not (evidence / "writes-poison-life-two/READY").exists(), "count poison published gap-free READY")
    require(not (evidence / "writes-poison-life-two/READY_WITNESSED_WRITES").exists(), "count poison published witnessed READY")
    poison_rows, _ = read_jsonl(evidence / "writes-poison-life-two/data-writes.jsonl")
    require(event_projection(poison_rows) == event_projection(positive_rows[0]), "count poison runtime events differ")

    discovery = read_json(evidence / "writes-run-a-discovery/receipt.json")
    require(discovery["witnessedWritesEligible"] is False, "blank-count discovery was admitted")
    require(discovery["witnessedGrade"]["reasons"] == ["target_evidence_failed"], "discovery refusal differs")
    require(not (evidence / "writes-run-a-discovery/READY_WITNESSED_WRITES").exists(), "discovery published witnessed READY")
    return {
        "replicas": 2,
        "nonMetadataBytes": len(neutral_values[0]),
        "nonMetadataSha256": WRITES_NEUTRAL_SHA256,
        "promotionPolicy": "bea.ttd.data-writes.witnessed-writes-with-gap-ledger.v1",
        "gapFree": False,
        "eventPairs": 2,
        "writerBodyRanges": ["0x004f9a90:0x004fa4aa"],
        "vtableControl": {"address": "0x080dc630", "initial": "0x005e24dc", "writes": 0},
        "life": {"offset": "0xf8", "address": "0x080dc728", "writerPc": "0x004f9e6e", "beforeBits": "0x3ba3d70b", "beforeF32": f32("0BD7A33B"), "afterBits": "0xc479ffae", "afterF32": f32("AEFF79C4")},
        "shields": {"offset": "0x100", "address": "0x080dc730", "writerPc": "0x004f9e50", "beforeBits": "0x00000000", "beforeF32": 0.0, "afterBits": "0x00000000", "afterF32": 0.0},
        "adverse": "LIFE_EXPECTED_TWO_WRITES_REFUSED",
    }


def pe_offset(image: bytes, va: int) -> int:
    pe = struct.unpack_from("<I", image, 0x3C)[0]
    require(image[pe:pe + 4] == b"PE\0\0", "pristine PE signature differs")
    sections = struct.unpack_from("<H", image, pe + 6)[0]
    optional_size = struct.unpack_from("<H", image, pe + 20)[0]
    optional = pe + 24
    image_base = struct.unpack_from("<I", image, optional + 28)[0]
    rva = va - image_base
    table = optional + optional_size
    for index in range(sections):
        row = table + index * 40
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from("<IIII", image, row + 8)
        if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
            return raw_pointer + rva - virtual_address
    raise ProofError(f"VA is not mapped: 0x{va:08x}")


def validate_static(root: Path) -> dict[str, Any]:
    image = (root / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup").read_bytes()
    offset = pe_offset(image, ENTRY)
    body = image[offset:offset + BODY_BYTES]
    require(len(body) == BODY_BYTES and sha256_bytes(body) == RAW_BODY_SHA256, "ApplyDamage pristine body differs")
    require(image[pe_offset(image, 0x004F9E50):pe_offset(image, 0x004F9E50) + 10] == bytes.fromhex("c7860001000000000000"), "shield writer instruction differs")
    require(image[pe_offset(image, 0x004F9E6E):pe_offset(image, 0x004F9E6E) + 6] == bytes.fromhex("d996f8000000"), "life writer instruction differs")

    inventory = root / "local-lab/ghidra-damage-hit-semantic-live-promotion-20260809-v1/runs-v2/live-post-inventory/functions.tsv"
    with inventory.open("r", encoding="utf-8", newline="") as stream:
        rows = {row["address"]: row for row in csv.DictReader(stream, delimiter="\t")}
    row = rows.get("0x004f9a90")
    require(row is not None, "live Ghidra inventory lacks ApplyDamage")
    require(row["name"] == "CUnit__ApplyDamage" and row["bodyBytes"] == "2586", "live Ghidra ApplyDamage identity differs")
    require(row["bodyDigest"] == GHIDRA_BODY_DIGEST, "live Ghidra ApplyDamage body digest differs")
    require(row["callingConv"] == "__thiscall" and row["paramCount"] == "5", "live Ghidra ApplyDamage ABI differs")
    require(row["returnType"] == "void", "live Ghidra ApplyDamage return type differs")

    parent = read_json(root / "local-lab/re-campaign-incident-recovery-20260808-v1/generation-12-level521-damage-hit-writes-v1/campaign.ready.json")
    require(parent["generation"] == 12 and parent["reducer"]["id"] == PARENT_REDUCER_ID, "Generation 12 parent differs")
    function_path = root / "local-lab/re-campaign-incident-recovery-20260808-v1/generation-12-level521-damage-hit-writes-v1/campaign-functions.tsv"
    functions = {row["entityKey"]: row for row in campaign_rows(function_path)}
    require(functions[ENTITY_KEY]["semanticGrade"] == "C1_CANDIDATE_PARTIAL", "parent function is not the expected C1 frontier")
    require(functions[ENTITY_KEY]["questionIds"] if "questionIds" in functions[ENTITY_KEY] else True, "parent function shape differs")
    contract_path = root / "local-lab/re-campaign-incident-recovery-20260808-v1/generation-12-level521-damage-hit-writes-v1/campaign-contracts.tsv"
    contracts = {row["contractId"]: row for row in campaign_rows(contract_path)}
    require(contracts[CONTRACT_ID]["semanticGrade"] == "C1_CANDIDATE_PARTIAL", "parent contract is not C1")
    require(contracts[CONTRACT_ID]["refuterVerdict"] == "UNSCORED", "parent refuter state differs")
    questions_path = root / "local-lab/re-campaign-incident-recovery-20260808-v1/generation-12-level521-damage-hit-writes-v1/campaign-questions.tsv"
    questions = {row["questionId"]: row for row in campaign_rows(questions_path)}
    require(questions[QUESTION_ID]["state"] == "OPEN", "parent ApplyDamage question is not open")
    return {
        "entryVa": "0x004f9a90",
        "endExclusive": "0x004fa4aa",
        "bodyBytes": BODY_BYTES,
        "rawContiguousBodySha256": RAW_BODY_SHA256,
        "ghidraBodyDigest": GHIDRA_BODY_DIGEST,
        "liveName": row["name"],
        "livePrototype": row["signature"],
        "parentSemanticGrade": "C1_CANDIDATE_PARTIAL",
    }


def derive(root: Path) -> dict[str, Any]:
    evidence = root / EVIDENCE_RELATIVE
    require(evidence.is_dir(), "ApplyDamage evidence root is missing")
    require(TRACE_PATH.is_file() and TRACE_PATH.stat().st_size == TRACE_BYTES, "retained trace path/size differs")
    inputs = exact_inputs(root, evidence)
    author = stamp(Path(__file__), root)
    call = validate_call(root, evidence)
    writes = validate_writes(evidence)
    static = validate_static(root)
    require(math.isclose(writes["life"]["beforeF32"], 0.0050000004, rel_tol=0, abs_tol=1e-10), "life preimage float differs")
    require(math.isclose(writes["life"]["afterF32"], -999.995, rel_tol=0, abs_tol=1e-4), "life postimage float differs")
    return {
        "schema": SCHEMA,
        "verdict": "PASS",
        "claim": CLAIM,
        "specimen": {"sha256": SPECIMEN_SHA256, "role": "STATIC_BYTE_AUTHORITY_UNCHANGED"},
        "runtimeImage": {"sha256": RUNTIME_SHA256, "role": "FORCE_WINDOWED_TRACE_IMAGE_NOT_PRISTINE"},
        "trace": {"path": str(TRACE_PATH), "bytes": TRACE_BYTES, "sha256": TRACE_SHA256, "identityMode": "DUAL_WRAPPER_HASH_RECEIPTS_PLUS_CURRENT_SIZE_NOT_REHASHED_BY_PROOF"},
        "parent": {"generation": 12, "readySha256": PARENT_READY_SHA256, "reducerId": PARENT_REDUCER_ID, "authorityReceiptSha256": PARENT_AUTHORITY_SHA256},
        "entity": {"entityKey": ENTITY_KEY, "contractId": CONTRACT_ID, "questionId": QUESTION_ID, "name": "CUnit__ApplyDamage"},
        "static": static,
        "callContext": call,
        "writes": writes,
        "adjudication": {
            "semanticGrade": "C2_BOUNDED_RUNTIME",
            "contractState": "BOUNDED_CONTRACT_ADVANCED",
            "authorVerdict": "SUPPORTED_BY_STATIC_AND_REPLICATED_TTD",
            "refuterVerdict": "SURVIVED",
            "runtimeVerdict": "MEASURED_BOUNDED_PATH",
            "questionDisposition": "CLOSE_BASE_AND_OPEN_NARROW_SUCCESSORS",
        },
        "limitations": [
            "The call/entry state is replicated, but a recorded kernel gap prevents pairing the raw ret 0x10 with that invocation.",
            "This proves one authored 1000.0-damage path on a receiver whose shields were already zero; it does not prove positive-shield absorption.",
            "The observed shield store wrote 0.0 over 0.0; alternate applyShields values are unobserved.",
            "Healing, segment selection, message/effect ordering, death virtual side effects, and other failure paths remain open.",
            "The deleted CDB logs and historical C2 package are corroboration only and are not inputs to this proof.",
            "No gameplay was recorded and no Ghidra or installed-game mutation occurred while producing this proof.",
        ],
        "inputs": inputs,
        "author": author,
    }


def validate_saved(saved: dict[str, Any], root: Path) -> None:
    require(set(saved) == set(derive(root)) | {"generatedAtUtc"}, "proof top-level shape differs")
    generated = saved["generatedAtUtc"]
    require(isinstance(generated, str) and generated.endswith("Z"), "proof timestamp is not UTC")
    datetime.fromisoformat(generated[:-1] + "+00:00")
    stable = dict(saved)
    del stable["generatedAtUtc"]
    require(stable == derive(root), "proof content differs from independently rederived evidence")


def build(root: Path) -> Path:
    evidence = root / EVIDENCE_RELATIVE
    ready = evidence / READY_NAME
    require(not ready.exists(), "proof READY already exists; verify it instead")
    author_before = stamp(Path(__file__), root)
    value = derive(root)
    require(value["author"] == author_before, "proof author changed during derivation")
    value["generatedAtUtc"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    validate_saved(value, root)
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd, temporary = tempfile.mkstemp(prefix=READY_NAME + ".", suffix=".partial", dir=evidence)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        require(stamp(Path(__file__), root) == author_before, "proof author changed before publication")
        validate_saved(read_json(Path(temporary)), root)
        os.replace(temporary, ready)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    validate_saved(read_json(ready), root)
    return ready


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify"))
    args = parser.parse_args()
    root = root_path()
    ready = root / EVIDENCE_RELATIVE / READY_NAME
    try:
        if args.command == "build":
            path = build(root)
            print(f"APPLYDAMAGE_REPROOF_READY {stamp(path, root)}")
        else:
            validate_saved(read_json(ready), root)
            print(f"APPLYDAMAGE_REPROOF_VERIFIED {stamp(ready, root)}")
    except (ProofError, KeyError, ValueError, OSError, struct.error) as exc:
        print(f"APPLYDAMAGE_REPROOF_REFUSED {exc}", file=os.sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
