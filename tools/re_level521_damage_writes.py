#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Verify and package the retained Level 521 player Damage/Hit write evidence.

This owner never records a trace and never opens Ghidra.  It independently
parses two Damage and two Hit observations from the same bounded TTD window,
checks their path-neutral replication, proves the writer-PC/body relation from
the pristine specimen, joins the exact Stuart ABI and focused reconstruction
test, and exercises the witnessed-write gate's missing-range adverse control.

The claim is deliberately narrow: one observed Damage invocation wrote five
named, offset-bound fields in a fixed order; one observed Hit invocation wrote
none of those seven watched fields.  The Damage window is not gap-free, no
typed return or death branch is proved, and the retained trace is receipt-bound
and size-checked rather than rehashed on every verification.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROOF_SCHEMA = "bea.re.level521-damage-hit-write-proof.v2"
OBSERVATION_SCHEMA = "bea.re.level521-damage-hit-write-observation.v1"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
RUNTIME_SHA256 = "e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4"
TRACE_SHA256 = "45ab04297f32bb27ac0c80e8ecb0b332e666a9955caea0763a83984affb74ac2"
TRACE_BYTES = 14_214_496_256
TRACE_PATH = Path(r"G:\bea-ttd\level521-native-20260802-0018-take4\level521-native-20260802-0018-take4.run")
PARENT_RELATIVE = Path("local-lab/re-campaign-incident-recovery-20260808-v1/generation-11-gen73-claims-resealed-v2")
PARENT_READY_SHA256 = "9b3769c503f003b34d3915047be28c24036567f260de1933591f0254d992686d"
PARENT_REDUCER_ID = "e88c973967a0458f500ff2cc1508d417b60487a4886703c4bd3dcfd197246993"
PARENT_COUNTS = {
    "functions": 8124,
    "residuals": 6117,
    "questions": 15241,
    "scenarios": 72,
    "levers": 915,
    "contracts": 14241,
    "adjudications": 6088,
    "supersessions": 584,
}
MEASURED_AT_UTC = "2026-08-04T21:52:47.3386214Z"
PLAYER_THIS = 0x079B9750
DAMAGE_ENTRY = 0x0040A890
DAMAGE_END_EXCLUSIVE = 0x0040AC25
HIT_ENTRY = 0x00407350
HIT_END_EXCLUSIVE = 0x004074CC
VTABLE = 0x005D89C4
DAMAGE_BODY_SHA256 = "224c0577b539bbf0d6fa118a6355502f9aead3bc588e59ae3bf08bdf3cd1ff91"
HIT_BODY_SHA256 = "8034efee2c37c5e02579dc82d4405b758cedc96d62b27909f5c66a6cea43ae8a"
DAMAGE_PATH_NEUTRAL_SHA256 = "2554189f273909c541bbfa2b068290a1f590eb04c12315bfe47e01bc9857af8c"
HIT_PATH_NEUTRAL_SHA256 = "00615c6355fa485dec803e87285d3f3b38ab5cc4bd3023fee1617fd00084bd60"

INPUTS: dict[str, tuple[int, str]] = {
    "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/damage-run-a/data-writes.jsonl": (21247, "7f6a78ce19d1de3459d8e74d3f7766597c2f24c546e553287b2ec418bc621f9c"),
    "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/damage-run-a/receipt.json": (10242, "28d8549f8f67c0dbdb4add7215f5abba3307434880c1df257c241c7cf020cb5d"),
    "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/damage-run-a/manifest.json": (6481, "dfc3502ba156a716033eab273d19cfd864002047058f3064b4d764a8b2e79109"),
    "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/damage-run-a/READY_WITNESSED_WRITES": (1503, "c7aa3d363432e9732626d1bc861e41f1e08ea1ba1625de5e4c26149cabaabe31"),
    "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/damage-run-a/targets.tsv": (206, "b1c1661db02ad2d536a9f509b180c144a615bfe2ad1196a15d6fa62ba7965515"),
    "local-lab/ttd-data-writes-level521-damage-fields-20260804-v1/run-b-closed/data-writes.jsonl": (21242, "090f3af4553dd200be81bbfd0c0834d27bc255ff89a2b940ea4e9964be1e7313"),
    "local-lab/ttd-data-writes-level521-damage-fields-20260804-v1/run-b-closed/receipt.json": (9512, "0b06f1b03e678031cfae06ff01fe77ff1843f33de7b3eca35f87ba54dc790661"),
    "local-lab/ttd-data-writes-level521-damage-fields-20260804-v1/run-b-closed/manifest.json": (5763, "024a3795a2cef41c3c5776730b648f637a20b8e5a9a39af98d3eb76996c7b25f"),
    "local-lab/ttd-data-writes-level521-damage-fields-20260804-v1/run-b-closed/targets.tsv": (206, "b1c1661db02ad2d536a9f509b180c144a615bfe2ad1196a15d6fa62ba7965515"),
    "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/hit-run-a/data-writes.jsonl": (10050, "303aea84e32a6b826cbfeec3cad1e16f2b05bb3064145c9834fa39ef3204675c"),
    "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/hit-run-a/receipt.json": (10132, "1a4df8ef711b0513f755ad5837a41c2f89d88a639661fb74e6304aeefee0a5bc"),
    "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/hit-run-a/manifest.json": (6394, "8c58890ef9a7b6c6672decf614b8387bf916fb02e9ac47fe5c6a47361c25c579"),
    "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/hit-run-a/READY": (959, "cf4ca4fc49d87a87e852ea03c4a37352e867c7e1e69e2834f51a7d16cc06cedb"),
    "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/hit-run-a/READY_WITNESSED_WRITES": (1435, "8fb696ae915492d0d76ce01f1ed4f8fbcdb01ebc02e957858d81e30ec4fde14f"),
    "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/hit-run-a/targets.tsv": (206, "9cb5382cb2ce8d9fe27c79dc161044028181a00511aeee5e5ef5863aa1e94ff3"),
    "local-lab/ttd-data-writes-level521-hit-control-20260804-v1/run-a/data-writes.jsonl": (10040, "9e1f693462eddd0d50e812e181092887968d1ef1daf0638619ea9c7e65cebbb5"),
    "local-lab/ttd-data-writes-level521-hit-control-20260804-v1/run-a/receipt.json": (9413, "c0e1d8196fe21ab6198b6a2bbc65ad89a66958dae27760ff5d3933af566cb10a"),
    "local-lab/ttd-data-writes-level521-hit-control-20260804-v1/run-a/manifest.json": (5671, "4d6fb758d599a5dd4354df30204d784f76bf0a13146e403e6fe73a8fc0116317"),
    "local-lab/ttd-data-writes-level521-hit-control-20260804-v1/run-a/READY": (919, "b454e497b6441c3a151fe43ba6764468f8db7b17ea89d4bb41e513f5f609c4e4"),
    "local-lab/ttd-data-writes-level521-hit-control-20260804-v1/run-a/targets.tsv": (206, "9cb5382cb2ce8d9fe27c79dc161044028181a00511aeee5e5ef5863aa1e94ff3"),
    "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/damage-poison-no-ranges/data-writes.jsonl": (21258, "152b67c22dea9286128f21967cfa332a608585e2e04bdc9c46ba6d839e60ad3b"),
    "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/damage-poison-no-ranges/receipt.json": (10351, "a60d96c0fba6b6b97f424fca2114bb30582be03c3ece53463e0933f05499bf7c"),
    "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/damage-poison-no-ranges/manifest.json": (6608, "8e46e65c357557eb849d1fb253b8e74506958fb6c82bb3946c3923d69872c67c"),
    "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/damage-poison-no-ranges/targets.tsv": (206, "b1c1661db02ad2d536a9f509b180c144a615bfe2ad1196a15d6fa62ba7965515"),
    "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup": (2506752, SPECIMEN_SHA256),
    "local-lab/safe-copy-bea-pristine/BEA.exe": (2506752, RUNTIME_SHA256),
    "references/Onslaught/BattleEngine.cpp": (93772, "138a18d10ad6aa3cb95211d3a1c7e2a14aaaaaf58210ad0d06abff55f2b33d31"),
    "references/Onslaught/BattleEngine.h": (13293, "84c88f5526e951389683e1fb132f70d7f1935139e582c8d9a8d41b2b6b516ccd"),
    "rebuild/OnslaughtRebuild.Core/Level100PlayerDamage.cs": (5193, "a9ed7758d722d4925f7d954511bb1a7bc6c0e3cc5a1454778ddcb734ffd874ad"),
    "rebuild/OnslaughtRebuild.Core.Tests/Level100PlayerDamageTests.cs": (13265, "7cfc42678c32a2f47aa6a581e4a47083849fff376e3f052be1285272aa4bdb80"),
    "local-lab/damage-chain-pilot-2026-08-02/static/damage-instructions.tsv": (117518, "9a1cbacc1da7af8731a99250f7f3679cfd31b90ef3127a17bea4da3906952800"),
    "local-lab/ghidra-target-lock-semantic-live-promotion-20260804-v2/promotion/runs/live-post-inventory/functions.tsv": (7051712, "f9a06dcdb0ac7510b8bfbf9d655dcf3935a24da603dbc9d3e00f0095fc36af7b"),
}

FIELD_SPECS = (
    (0, "mLife", 0xF8, PLAYER_THIS + 0xF8),
    (1, "mEnergy", 0xFC, PLAYER_THIS + 0xFC),
    (2, "mShields", 0x100, PLAYER_THIS + 0x100),
    (3, "mLastDamageTime", 0x2D4, PLAYER_THIS + 0x2D4),
    (4, "mAugValue", 0x2F8, PLAYER_THIS + 0x2F8),
    (5, "mAugActive", 0x2FC, PLAYER_THIS + 0x2FC),
    (6, "mVulnerable", 0x15C, PLAYER_THIS + 0x15C),
)
WRITE_ORDER = (2, 4, 0, 3, 1)
WRITER_PCS = (0x40A944, 0x40A969, 0x40A9C6, 0x40A9F1, 0x40AABA)
WRITER_BYTES = {
    0x40A944: bytes.fromhex("d99e00010000"),
    0x40A969: bytes.fromhex("d99ef8020000"),
    0x40A9C6: bytes.fromhex("d996f8000000"),
    0x40A9F1: bytes.fromhex("8986d4020000"),
    0x40AABA: bytes.fromhex("8986fc000000"),
}


class ProofError(ValueError):
    """The retained evidence does not satisfy the bounded proof contract."""


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def repository_root() -> Path:
    configured = os.environ.get("BEA_REPO_ROOT")
    return Path(configured).resolve() if configured else Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProofError(message)


def stamp(path: Path, root: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing evidence file: {path}")
    try:
        relative = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        relative = str(path.resolve())
    return {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProofError(f"cannot parse {label}: {exc}") from exc
    require(isinstance(value, dict), f"{label} root is not an object")
    return value


def exact_inputs(root: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for relative, (size, digest) in sorted(INPUTS.items()):
        path = root / relative
        actual = stamp(path, root)
        require(actual["bytes"] == size and actual["sha256"] == digest, f"input identity differs: {relative}")
        result[relative] = actual
    return result


def _pe_offset(image: bytes, va: int) -> int:
    require(len(image) >= 0x100, "pristine PE is truncated")
    pe = struct.unpack_from("<I", image, 0x3C)[0]
    require(image[pe:pe + 4] == b"PE\0\0", "pristine PE signature differs")
    section_count = struct.unpack_from("<H", image, pe + 6)[0]
    optional_size = struct.unpack_from("<H", image, pe + 20)[0]
    optional = pe + 24
    require(struct.unpack_from("<H", image, optional)[0] == 0x10B, "pristine PE is not PE32")
    image_base = struct.unpack_from("<I", image, optional + 28)[0]
    rva = va - image_base
    sections = optional + optional_size
    for index in range(section_count):
        row = sections + 40 * index
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from("<IIII", image, row + 8)
        if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
            return raw_pointer + rva - virtual_address
    raise ProofError(f"VA is not mapped by pristine PE: 0x{va:08x}")


def validate_static(root: Path) -> dict[str, Any]:
    image_path = root / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup"
    image = image_path.read_bytes()
    damage_offset = _pe_offset(image, DAMAGE_ENTRY)
    hit_offset = _pe_offset(image, HIT_ENTRY)
    damage_body = image[damage_offset:damage_offset + (DAMAGE_END_EXCLUSIVE - DAMAGE_ENTRY)]
    hit_body = image[hit_offset:hit_offset + (HIT_END_EXCLUSIVE - HIT_ENTRY)]
    require(sha256_bytes(damage_body) == DAMAGE_BODY_SHA256, "Damage pristine body differs")
    require(sha256_bytes(hit_body) == HIT_BODY_SHA256, "Hit pristine body differs")
    slot39 = struct.unpack_from("<I", image, _pe_offset(image, VTABLE + 39 * 4))[0]
    slot40 = struct.unpack_from("<I", image, _pe_offset(image, VTABLE + 40 * 4))[0]
    require((slot39, slot40) == (HIT_ENTRY, DAMAGE_ENTRY), "Battle Engine vtable slots 39/40 differ")
    for pc, expected in WRITER_BYTES.items():
        offset = _pe_offset(image, pc)
        require(image[offset:offset + len(expected)] == expected, f"writer instruction differs at 0x{pc:08x}")

    cpp = (root / "references/Onslaught/BattleEngine.cpp").read_text(encoding="utf-8", errors="strict")
    header = (root / "references/Onslaught/BattleEngine.h").read_text(encoding="utf-8", errors="strict")
    require("void\tCBattleEngine::Damage(" in cpp, "Stuart Damage definition differs")
    require("void\t\tCBattleEngine::Hit(CThing* other_thing, CCollisionReport* report)" in cpp, "Stuart Hit definition differs")
    require("virtual void\t\t\tHit(CThing* other_thing, CCollisionReport* report)" in header, "Stuart Hit declaration differs")
    require("virtual void\t\t\tDamage(float amount,CThing *inByThis,BOOL inDamageShields=TRUE, int mesh_part_no = -1);" in header, "Stuart Damage declaration differs")
    require("mShields-=shieldDamage;" in cpp and "mLife-=inAmount;" in cpp and "mEnergy=mShields;" in cpp, "Stuart Damage write law differs")

    inventory_path = root / "local-lab/ghidra-target-lock-semantic-live-promotion-20260804-v2/promotion/runs/live-post-inventory/functions.tsv"
    lines = inventory_path.read_text(encoding="utf-8").splitlines()
    header_row = lines[0].split("\t")
    by_address = {row.split("\t")[0]: dict(zip(header_row, row.split("\t"))) for row in lines[1:]}
    damage = by_address.get("0x0040a890")
    hit = by_address.get("0x00407350")
    require(damage is not None and hit is not None, "live POST inventory lacks Damage/Hit functions")
    require(damage["bodyBytes"] == "917" and damage["bodyMin"] == "0x0040a890" and damage["bodyMax"] == "0x0040ac24", "live POST Damage envelope differs")
    require(hit["bodyBytes"] == "380" and hit["bodyMin"] == "0x00407350" and hit["bodyMax"] == "0x004074cb", "live POST Hit envelope differs")
    return {
        "vtable": {"address": "0x005d89c4", "slot39": "0x00407350", "slot40": "0x0040a890"},
        "damage": {"entryVa": "0x0040a890", "endExclusive": "0x0040ac25", "bytes": len(damage_body), "sha256": DAMAGE_BODY_SHA256},
        "hit": {"entryVa": "0x00407350", "endExclusive": "0x004074cc", "bytes": len(hit_body), "sha256": HIT_BODY_SHA256},
        "writerInstructions": [{"pc": f"0x{pc:08x}", "bytesHex": value.hex()} for pc, value in WRITER_BYTES.items()],
        "prototype": "void __thiscall CBattleEngine__Damage(CBattleEngine *this, float amount, CThing *source, BOOL damageShields, int meshPartNo)",
        "hitPrototype": "void __thiscall CBattleEngine__Hit(CBattleEngine *this, CThing *otherThing, CCollisionReport *report)",
    }


def parse_jsonl(path: Path) -> tuple[list[dict[str, Any]], str]:
    raw_lines = path.read_bytes().splitlines(keepends=True)
    try:
        rows = [json.loads(line) for line in raw_lines]
    except json.JSONDecodeError as exc:
        raise ProofError(f"invalid data-write JSONL {path}: {exc}") from exc
    require(all(isinstance(row, dict) for row in rows), "data-write JSONL has a non-object row")
    path_neutral = sha256_bytes(b"".join(raw_lines[1:]))
    return rows, path_neutral


def _int(value: Any, label: str) -> int:
    try:
        return int(str(value), 0)
    except (TypeError, ValueError) as exc:
        raise ProofError(f"{label} is not an integer") from exc


def _f32(hex_value: str) -> float:
    try:
        raw = bytes.fromhex(hex_value)
    except ValueError as exc:
        raise ProofError("write evidence contains malformed bytes") from exc
    require(len(raw) == 4, "write evidence value is not one float32")
    return struct.unpack("<f", raw)[0]


def validate_rows(rows: list[dict[str, Any]], *, mode: str) -> dict[str, Any]:
    expected_kinds = (
        Counter({"metadata": 1, "target": 7, "event": 10, "pair": 5, "continuity-break": 9, "gap-summary": 1, "summary": 1})
        if mode == "damage"
        else Counter({"metadata": 1, "target": 7, "gap-summary": 1, "summary": 1})
    )
    require(Counter(row.get("kind") for row in rows) == expected_kinds, f"{mode} row-kind census differs")
    metadata = next(row for row in rows if row.get("kind") == "metadata")
    expected_window = (
        ("0x14B569:0x6F2", "0x14B571:0x78")
        if mode == "damage"
        else ("0x14B654:0x264", "0x14B654:0x29C")
    )
    required_metadata = {
        "schema": "bea.ttd.data-writes.v3",
        "processor_architecture": "x86",
        "module_base": "0x400000",
        "module_size": "0x5D8000",
        "module_timestamp": "0x3ED21313",
        "trace_bytes": str(TRACE_BYTES),
        "requested_from": expected_window[0],
        "requested_to": expected_window[1],
        "actual_from": expected_window[0],
        "replay_mode": "sequential-all-segments",
        "pairing_policy": "exact-same-boundary-structural-candidate",
        "raw_value_policy": "untyped-registers-and-bytes",
    }
    require(all(metadata.get(key) == value for key, value in required_metadata.items()), f"{mode} metadata differs")
    require(Path(str(metadata.get("trace"))).resolve() == TRACE_PATH.resolve(), f"{mode} trace path differs")

    targets = sorted((row for row in rows if row.get("kind") == "target"), key=lambda row: _int(row.get("target_index"), "target index"))
    for row, (index, _name, _offset, address) in zip(targets, FIELD_SPECS, strict=True):
        positive = mode == "damage" and index in WRITE_ORDER
        count = "1" if positive else "0"
        require(row.get("target_index") == index and _int(row.get("address"), "target address") == address and row.get("size") == 4, f"{mode} target {index} identity differs")
        require(row.get("expected_overwrite_count") == count and row.get("expected_write_count") == count, f"{mode} target {index} expectation differs")
        require(row.get("observed_overwrite_count") == count and row.get("observed_write_count") == count and row.get("observed_pair_count") == count, f"{mode} target {index} count differs")
        expected_grade = "WATCHPOINT_CHAIN_CLOSED" if positive else "NO_WRITE_CALLBACK_WITNESS"
        require(row.get("evidence_grade") == expected_grade and row.get("transition_chain_closed") is True and row.get("evidence_checks_passed") is True and row.get("expectations_passed") is True, f"{mode} target {index} grade differs")
        if not positive:
            require(row["initial_memory"].get("hex") == row["final_memory"].get("hex"), f"{mode} zero-write target {index} changed")

    summary = next(row for row in rows if row.get("kind") == "summary")
    expected_summary = {
        "target_count": 7,
        "event_count": 10 if mode == "damage" else 0,
        "pair_count": "5" if mode == "damage" else "0",
        "orphan_event_count": "0",
        "callback_hits": "10" if mode == "damage" else "0",
        "nontrivial_gap_count": "5" if mode == "damage" else "0",
        "continuity_break_count": "9" if mode == "damage" else "0",
        "instructions_executed": "386" if mode == "damage" else "56",
        "steps_executed": "386" if mode == "damage" else "56",
        "final_position": expected_window[1],
        "replay_complete": True,
        "pairing_complete": True,
        "target_evidence_passed": True,
        "expectations_passed": True,
        "collector_checks_passed": False if mode == "damage" else True,
    }
    require(all(summary.get(key) == value for key, value in expected_summary.items()), f"{mode} summary differs")

    gap = next(row for row in rows if row.get("kind") == "gap-summary")
    require(gap.get("kind_context_switch") == ("3" if mode == "damage" else "0") and gap.get("kind_unrecorded") == ("2" if mode == "damage" else "0"), f"{mode} gap census differs")
    if mode == "hit":
        return {
            "window": {"from": expected_window[0], "to": expected_window[1]},
            "fields": [name for _idx, name, _offset, _address in FIELD_SPECS],
            "allSevenFieldsZeroWrite": True,
            "gapFree": True,
        }

    breaks = sorted(_int(row.get("ordinal"), "continuity ordinal") for row in rows if row.get("kind") == "continuity-break")
    require(breaks == list(range(9)), "Damage continuity-break ledger differs")
    events = sorted((row for row in rows if row.get("kind") == "event"), key=lambda row: _int(row.get("event_index"), "event index"))
    pairs = sorted((row for row in rows if row.get("kind") == "pair"), key=lambda row: _int(row.get("pair_index"), "pair index"))
    observations: list[dict[str, Any]] = []
    for pair_index, (target_index, writer_pc) in enumerate(zip(WRITE_ORDER, WRITER_PCS, strict=True)):
        pair = pairs[pair_index]
        overwrite = events[pair_index * 2]
        write = events[pair_index * 2 + 1]
        require(pair.get("pair_index") == pair_index and pair.get("target_index") == target_index and pair.get("overwrite_event_index") == pair_index * 2 and pair.get("write_event_index") == pair_index * 2 + 1 and pair.get("grade") == "STRUCTURAL_WRITE_PAIR" and pair.get("checks_passed") is True and pair.get("changed") is True, f"Damage pair {pair_index} differs")
        common = ("target_index", "pair_index", "continuity_epoch", "position", "pc", "access_address", "access_size", "unique_thread_id", "os_thread_id", "registers")
        require(all(overwrite.get(key) == write.get(key) for key in common), f"Damage pair {pair_index} overwrite/write boundary differs")
        require(overwrite.get("event_type") == "Overwrite" and write.get("event_type") == "Write", f"Damage pair {pair_index} phases differ")
        require(_int(write.get("pc"), "writer PC") == writer_pc and DAMAGE_ENTRY <= writer_pc < DAMAGE_END_EXCLUSIVE, f"Damage pair {pair_index} writer PC differs")
        field = FIELD_SPECS[target_index]
        require(_int(write.get("access_address"), "write address") == field[3], f"Damage pair {pair_index} address differs")
        registers = write.get("registers")
        require(isinstance(registers, dict) and _int(registers.get("esi"), "ESI") == PLAYER_THIS and _int(registers.get("edi"), "EDI") == PLAYER_THIS, f"Damage pair {pair_index} receiver differs")
        pre_hex = str(overwrite.get("observed_memory", {}).get("hex", ""))
        post_hex = str(write.get("observed_memory", {}).get("hex", ""))
        pre = _f32(pre_hex)
        post = _f32(post_hex)
        observations.append({
            "order": pair_index + 1,
            "field": field[1],
            "offset": f"0x{field[2]:x}",
            "address": f"0x{field[3]:08x}",
            "writerPc": f"0x{writer_pc:08x}",
            "position": write.get("position"),
            "preHex": pre_hex,
            "postHex": post_hex,
            "preFloat32": pre,
            "postFloat32": post,
            "deltaFloat32": post - pre,
        })

    by_name = {row["field"]: row for row in observations}
    require(math.isclose(by_name["mShields"]["deltaFloat32"], -0.049, abs_tol=2e-6), "Damage shield delta differs")
    require(math.isclose(by_name["mAugValue"]["deltaFloat32"], 0.049, abs_tol=2e-6), "Damage augment delta differs")
    require(math.isclose(by_name["mLife"]["deltaFloat32"], -0.001, abs_tol=2e-6), "Damage life delta differs")
    require(math.isclose(by_name["mLastDamageTime"]["deltaFloat32"], 6.45, abs_tol=2e-5), "Damage time delta differs")
    require(by_name["mEnergy"]["postHex"] == by_name["mShields"]["postHex"], "Damage walker energy/shield post-state differs")
    return {
        "window": {"from": expected_window[0], "to": expected_window[1]},
        "receiver": "0x079b9750",
        "orderedWrites": observations,
        "zeroWriteControls": [FIELD_SPECS[5][1], FIELD_SPECS[6][1]],
        "gapFree": False,
        "witnessedWritesEligible": True,
    }


def validate_receipt(
    path: Path,
    *,
    mode: str,
    writer_ranges: bool,
    legacy_no_range_profile: bool = False,
    adverse_missing_ranges: bool = False,
) -> dict[str, Any]:
    receipt = read_json(path, f"{mode} receipt")
    require(receipt.get("schemaVersion") == "bea-ttd-data-writes-receipt.v3", f"{mode} receipt schema differs")
    trace = receipt.get("trace")
    target = receipt.get("target")
    invocation = receipt.get("invocation")
    require(isinstance(trace, dict) and trace.get("bytes") == TRACE_BYTES and str(trace.get("sha256", "")).lower() == TRACE_SHA256, f"{mode} trace receipt differs")
    require(isinstance(target, dict) and target.get("bytes") == 2506752 and str(target.get("sha256", "")).lower() == RUNTIME_SHA256, f"{mode} runtime receipt differs")
    require(isinstance(invocation, dict), f"{mode} invocation receipt is absent")
    ranges = invocation.get("writerBodyRanges")
    expected_ranges: Any = ["0x40A890:0x40AC25"] if writer_ranges else []
    if legacy_no_range_profile:
        expected_ranges = None
    require(ranges == expected_ranges, f"{mode} writer range receipt differs")
    data = receipt.get("dataWrites")
    require(isinstance(data, dict) and data.get("schemaVersion") == "bea.ttd.data-writes.v3", f"{mode} data-write receipt differs")
    if mode == "damage":
        require(receipt.get("collectorExitCode") == 10 and receipt.get("exitCode") == 10 and receipt.get("readyGapFreeEligible") is not True, "Damage gap-free failure disposition differs")
        if writer_ranges:
            require(receipt.get("witnessedWritesEligible") is True, "Damage witnessed-write eligibility differs")
            grade = receipt.get("witnessedGrade")
            require(isinstance(grade, dict) and grade.get("eligible") is True and grade.get("outOfBodyPcs") == [] and grade.get("eventCount") == 10 and grade.get("pairCount") == 5, "Damage witnessed-write grade differs")
        elif adverse_missing_ranges:
            require(receipt.get("witnessedWritesEligible") is False, "missing-range adverse control was accepted")
            grade = receipt.get("witnessedGrade")
            require(isinstance(grade, dict) and grade.get("reasons") == ["writer_body_ranges_required_when_events_present"], "missing-range adverse reason differs")
        else:
            require(legacy_no_range_profile, "Damage receipt lacks a recognized grade profile")
            require("witnessedWritesEligible" not in receipt and "witnessedGrade" not in receipt, "legacy Damage replica unexpectedly carries a witnessed grade")
    else:
        require(receipt.get("collectorExitCode") == 0 and receipt.get("exitCode") == 0 and receipt.get("readyEligible") is True, "Hit READY receipt differs")
    return receipt


def validate_trace_boundary() -> dict[str, Any]:
    raw = Path(os.path.abspath(TRACE_PATH))
    require(str(raw).lower() == str(TRACE_PATH).lower(), "trace lexical path differs")
    require(raw.is_file(), "bound Level 521 trace is absent")
    stat = raw.lstat()
    reparse = getattr(stat, "st_file_attributes", 0) & 0x400
    require(not reparse and not raw.is_symlink(), "bound Level 521 trace path is reparse/symlinked")
    require(stat.st_size == TRACE_BYTES, "bound Level 521 trace size differs")
    return {
        "path": str(TRACE_PATH),
        "bytes": TRACE_BYTES,
        "receiptSha256": TRACE_SHA256,
        "actualSizeVerified": True,
        "actualHashRecomputed": False,
    }


def validate_evidence(root: Path) -> dict[str, Any]:
    root = root.resolve()
    inputs = exact_inputs(root)
    trace = validate_trace_boundary()
    static = validate_static(root)
    paths = {
        "damageA": root / "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/damage-run-a/data-writes.jsonl",
        "damageB": root / "local-lab/ttd-data-writes-level521-damage-fields-20260804-v1/run-b-closed/data-writes.jsonl",
        "hitA": root / "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/hit-run-a/data-writes.jsonl",
        "hitB": root / "local-lab/ttd-data-writes-level521-hit-control-20260804-v1/run-a/data-writes.jsonl",
        "poison": root / "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/damage-poison-no-ranges/data-writes.jsonl",
    }
    parsed = {name: parse_jsonl(path) for name, path in paths.items()}
    require(parsed["damageA"][1] == parsed["damageB"][1] == parsed["poison"][1] == DAMAGE_PATH_NEUTRAL_SHA256, "Damage replicas/path-neutral adverse bytes differ")
    require(parsed["hitA"][1] == parsed["hitB"][1] == HIT_PATH_NEUTRAL_SHA256, "Hit replicas path-neutral bytes differ")
    damage_a = validate_rows(parsed["damageA"][0], mode="damage")
    damage_b = validate_rows(parsed["damageB"][0], mode="damage")
    hit_a = validate_rows(parsed["hitA"][0], mode="hit")
    hit_b = validate_rows(parsed["hitB"][0], mode="hit")
    require(damage_a == damage_b, "Damage semantic replicas differ")
    require(hit_a == hit_b, "Hit semantic replicas differ")
    require(parsed["damageA"][0][1:] == parsed["poison"][0][1:], "missing-range adverse data differs from positive observation")

    validate_receipt(root / "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/damage-run-a/receipt.json", mode="damage", writer_ranges=True)
    validate_receipt(root / "local-lab/ttd-data-writes-level521-damage-fields-20260804-v1/run-b-closed/receipt.json", mode="damage", writer_ranges=False, legacy_no_range_profile=True)
    validate_receipt(root / "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/hit-run-a/receipt.json", mode="hit", writer_ranges=False)
    validate_receipt(root / "local-lab/ttd-data-writes-level521-hit-control-20260804-v1/run-a/receipt.json", mode="hit", writer_ranges=False, legacy_no_range_profile=True)
    validate_receipt(root / "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/damage-poison-no-ranges/receipt.json", mode="damage", writer_ranges=False, adverse_missing_ranges=True)
    return {
        "schema": OBSERVATION_SCHEMA,
        "specimen": {"sha256": SPECIMEN_SHA256},
        "runtime": {"sha256": RUNTIME_SHA256, "fourBytePatchOutsideTargetBodies": True},
        "trace": trace,
        "static": static,
        "damage": damage_a,
        "hit": hit_a,
        "replication": {
            "damageReplicas": 2,
            "hitReplicas": 2,
            "damagePathNeutralSha256": DAMAGE_PATH_NEUTRAL_SHA256,
            "hitPathNeutralSha256": HIT_PATH_NEUTRAL_SHA256,
            "semanticReplicaEquality": True,
        },
        "adverseControls": {
            "missingWriterBodyRangesRejected": True,
            "sameObservationBytes": True,
            "reason": "writer_body_ranges_required_when_events_present",
        },
        "inputs": inputs,
        "claimBoundary": {
            "damageWritesProved": ["mShields", "mAugValue", "mLife", "mLastDamageTime", "mEnergy"],
            "damageZeroWriteControls": ["mAugActive", "mVulnerable"],
            "hitSevenFieldZeroWriteControl": True,
            "damageGapFree": False,
            "typedReturnProved": False,
            "deathBranchProved": False,
            "repairBranchProved": False,
            "allCallsProved": False,
        },
    }


def validate_parent(root: Path) -> dict[str, Any]:
    campaign = (root / PARENT_RELATIVE).resolve()
    ready_path = campaign / "campaign.ready.json"
    require(ready_path.is_file() and sha256_file(ready_path) == PARENT_READY_SHA256, "Generation 11 parent READY differs")
    receipt = read_json(ready_path, "Generation 11 READY")
    reducer = receipt.get("reducer")
    require(receipt.get("generation") == 11 and receipt.get("counts") == PARENT_COUNTS, "Generation 11 parent population differs")
    require(isinstance(reducer, dict) and reducer.get("id") == PARENT_REDUCER_ID, "Generation 11 parent reducer differs")
    return {"path": PARENT_RELATIVE.as_posix(), "ready": stamp(ready_path, root), "reducerId": PARENT_REDUCER_ID}


def run_process(arguments: list[str], *, cwd: Path, timeout: int) -> dict[str, Any]:
    environment = os.environ.copy()
    environment["DOTNET_CLI_TELEMETRY_OPTOUT"] = "1"
    completed = subprocess.run(arguments, cwd=cwd, env=environment, text=True, capture_output=True, timeout=timeout, check=False)
    return {"argv": arguments, "exitCode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def selftest(root: Path) -> dict[str, Any]:
    source, _digest = parse_jsonl(root / "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/damage-run-a/data-writes.jsonl")
    hit, _hit_digest = parse_jsonl(root / "local-lab/ttd-data-writes-level521-gap-aware-regrade-20260804-v1/hit-run-a/data-writes.jsonl")
    attacks: list[tuple[str, list[dict[str, Any]], str, str]] = []
    outside = copy.deepcopy(source)
    for row in outside:
        if row.get("kind") == "event" and row.get("pair_index") == 0:
            row["pc"] = "0x40AC25"
    attacks.append(("writer-pc", outside, "damage", "writer PC differs"))
    receiver = copy.deepcopy(source)
    for row in receiver:
        if row.get("kind") == "event" and row.get("pair_index") == 0:
            row["registers"]["esi"] = "0x79B9751"
    attacks.append(("receiver", receiver, "damage", "receiver differs"))
    order = copy.deepcopy(source)
    first_pair = next(row for row in order if row.get("kind") == "pair" and row.get("pair_index") == 0)
    first_pair["target_index"] = 4
    attacks.append(("write-order", order, "damage", "pair 0 differs"))
    hit_write = copy.deepcopy(hit)
    next(row for row in hit_write if row.get("kind") == "target")["observed_write_count"] = "1"
    attacks.append(("hit-write", hit_write, "hit", "target 0 count differs"))
    rejected: list[str] = []
    for label, rows, mode, expected in attacks:
        try:
            validate_rows(rows, mode=mode)
        except ProofError as exc:
            require(expected in str(exc), f"{label} rejected by unintended gate: {exc}")
            rejected.append(label)
        else:
            raise ProofError(f"selftest attack accepted: {label}")
    return {"attacks": rejected, "count": len(rejected)}


def _validate_saved_receipt(root: Path, proof_root: Path, receipt: dict[str, Any]) -> dict[str, Any]:
    require(set(receipt) == {"schema", "generatedAtUtc", "verdict", "author", "parent", "observation", "parity", "selftest", "limitations"}, "proof receipt shape differs")
    require(receipt.get("schema") == PROOF_SCHEMA and receipt.get("verdict") == "SURVIVED", "proof receipt verdict differs")
    frozen_author = proof_root / "author.py"
    observed_author = stamp(frozen_author, proof_root)
    require(receipt.get("author") == observed_author, "frozen proof author identity differs")
    require(frozen_author.read_bytes() == Path(__file__).resolve().read_bytes(), "executing proof author differs from frozen proof author")
    require(receipt.get("parent") == validate_parent(root), "proof parent binding differs")
    observation_path = proof_root / "observation.json"
    require(receipt.get("observation") == stamp(observation_path, proof_root), "proof observation stamp differs")
    observed = read_json(observation_path, "saved observation")
    require(observed == validate_evidence(root), "saved observation does not rederive")
    parity = receipt.get("parity")
    require(isinstance(parity, dict) and set(parity) == {"command", "exitCode", "testsPassed", "testsFailed", "testsSkipped", "stdout", "stderr", "scope"}, "parity receipt shape differs")
    require(parity.get("exitCode") == 0 and parity.get("testsPassed") == 21 and parity.get("testsFailed") == 0 and parity.get("testsSkipped") == 0, "focused parity result differs")
    require(parity.get("scope") == "Level100PlayerDamageTests", "focused parity scope differs")
    require(parity.get("stdout") == stamp(proof_root / "parity.stdout.txt", proof_root), "parity stdout stamp differs")
    require(parity.get("stderr") == stamp(proof_root / "parity.stderr.txt", proof_root), "parity stderr stamp differs")
    require(receipt.get("selftest") == selftest(root), "proof selftest differs")
    limitations = receipt.get("limitations")
    require(isinstance(limitations, list) and "The retained 14 GiB trace is receipt-hash-bound and actual-size-checked, not rehashed by this proof." in limitations, "proof trace limitation is absent")
    return receipt


def build(root: Path, out: Path) -> dict[str, Any]:
    root = root.resolve()
    out = out.resolve()
    require(not out.exists(), f"refusing existing proof root: {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    author_path = Path(__file__).resolve()
    author_start = author_path.read_bytes()
    parent = validate_parent(root)
    observation = validate_evidence(root)
    tests = selftest(root)
    stage = Path(tempfile.mkdtemp(prefix=f".{out.name}.", dir=out.parent))
    try:
        frozen_author = stage / "author.py"
        frozen_author.write_bytes(author_start)
        observation_path = stage / "observation.json"
        observation_path.write_text(json.dumps(observation, indent=2) + "\n", encoding="utf-8")
        command = [
            "dotnet", "test",
            "rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj",
            "--filter", "FullyQualifiedName~Level100PlayerDamageTests",
            "--no-restore",
        ]
        process = run_process(command, cwd=root, timeout=180)
        (stage / "parity.stdout.txt").write_text(process["stdout"], encoding="utf-8")
        (stage / "parity.stderr.txt").write_text(process["stderr"], encoding="utf-8")
        require(process["exitCode"] == 0, "focused Level100PlayerDamage parity failed")
        output = process["stdout"] + process["stderr"]
        require("Passed:    21" in output and "Failed:     0" in output and "Skipped:     0" in output, "focused parity census differs")
        require(author_path.read_bytes() == author_start, "proof author changed during execution")
        receipt = {
            "schema": PROOF_SCHEMA,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "verdict": "SURVIVED",
            "author": stamp(frozen_author, stage),
            "parent": parent,
            "observation": stamp(observation_path, stage),
            "parity": {
                "command": command,
                "exitCode": process["exitCode"],
                "testsPassed": 21,
                "testsFailed": 0,
                "testsSkipped": 0,
                "stdout": stamp(stage / "parity.stdout.txt", stage),
                "stderr": stamp(stage / "parity.stderr.txt", stage),
                "scope": "Level100PlayerDamageTests",
            },
            "selftest": tests,
            "limitations": [
                "The Damage observation is READY_WITNESSED_WRITES, not gap-free READY; five nontrivial gaps and nine continuity breaks remain explicit.",
                "The retained 14 GiB trace is receipt-hash-bound and actual-size-checked, not rehashed by this proof.",
                "The observed invocation proves five exact writes and two zero-write controls only; it does not prove all branches, all calls, repair, death, god-mode restoration, or a typed return.",
                "The Hit negative control is bounded to seven watched fields in one exact gap-free invocation window; it is not a universal no-write law.",
                "Stuart source supports architecture and identity; pristine bytes and TTD observations own released-state claims.",
            ],
        }
        (stage / "proof.ready.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        _validate_saved_receipt(root, stage, receipt)
        require(author_path.read_bytes() == author_start, "proof author changed before publication")
        os.replace(stage, out)
        return _validate_saved_receipt(root, out, read_json(out / "proof.ready.json", "proof READY"))
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def verify(root: Path, proof_root: Path) -> dict[str, Any]:
    root = root.resolve()
    proof_root = proof_root.resolve()
    receipt = read_json(proof_root / "proof.ready.json", "proof READY")
    return _validate_saved_receipt(root, proof_root, receipt)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=repository_root())
    commands = parser.add_subparsers(dest="command", required=True)
    build_parser = commands.add_parser("build")
    build_parser.add_argument("--out", type=Path, required=True)
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--proof", type=Path, required=True)
    commands.add_parser("selftest")
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            receipt = build(args.repo, args.out)
            print(f"LEVEL521_DAMAGE_WRITES_PROOF_READY verdict={receipt['verdict']}")
        elif args.command == "verify":
            receipt = verify(args.repo, args.proof)
            print(f"LEVEL521_DAMAGE_WRITES_PROOF_VERIFIED verdict={receipt['verdict']}")
        else:
            result = selftest(args.repo.resolve())
            print(f"LEVEL521_DAMAGE_WRITES_SELFTEST_OK attacks={result['count']}")
        return 0
    except (ProofError, OSError, subprocess.SubprocessError) as exc:
        print(f"LEVEL521_DAMAGE_WRITES_PROOF_FAILED: {exc}", file=sys.stderr)
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
