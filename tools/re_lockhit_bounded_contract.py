#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reprove the bounded retail CBattleEngine::LockHit removal contract.

This owner records no trace and mutates neither the game nor Ghidra.  It binds
the exact Generation 16 campaign, independently parses three retained replays
of one immutable Level 521 write window and two retained call-context replays,
joins those observations to pristine retail bytes, Stuart's source, and the
already-promoted Ghidra identity, and emits a narrow post-loss proof.

The result proves one non-null, sole-matching-node path.  It deliberately does
not promote null, not-found, multi-node, payload-destruction, full-return, or
direct global-free-head observations.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import os
import shutil
import struct
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROOF_SCHEMA = "bea.re.lockhit-bounded-contract-proof.v1"
OBSERVATION_SCHEMA = "bea.re.lockhit-bounded-contract-observation.v1"
READY_NAME = "proof.ready.json"
OBSERVATION_NAME = "observation.json"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
RUNTIME_SHA256 = "e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4"
TRACE_SHA256 = "45ab04297f32bb27ac0c80e8ecb0b332e666a9955caea0763a83984affb74ac2"
TRACE_BYTES = 14_214_496_256
TRACE_PATH = Path(
    r"G:\bea-ttd\level521-native-20260802-0018-take4\level521-native-20260802-0018-take4.run"
)
PARENT_RELATIVE = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-16-mission-native-setpos-runtime-v1"
)
PARENT_READY_BYTES = 20_363
PARENT_READY_SHA256 = "97493a76de550f5ae35074e285e39a561d9a323219741a42ac2ff25643cdc880"
PARENT_REDUCER_ID = "453fdb4df7233c6d3f8be04a6ba67b3762982bc4513ca4990b46f01141d55db0"
PARENT_COUNTS = {
    "functions": 8125,
    "residuals": 6118,
    "questions": 15249,
    "scenarios": 72,
    "levers": 915,
    "contracts": 14243,
    "adjudications": 6095,
    "supersessions": 588,
}

LOCKHIT_ENTRY = 0x00407140
LOCKHIT_END = 0x004071A9
LOCKHIT_BODY_SHA256 = "eb6914393a80a1a0d314385955c4188946ad9a2115fe5d49da6224c7dd80605c"
REMOVE_ENTRY = 0x004E5BD0
REMOVE_END = 0x004E5C22
REMOVE_BODY_SHA256 = "b7c2068bacc0f54ec7d65b33b75253a434a9fc8e15ab44a63d2c9dd96f14371a"
LOCKHIT_ENTITY = (
    "CODE:" + SPECIMEN_SHA256
    + ":VA=0x00407140:RANGES=6c9813a631717dc2e10869bce7bacb6bab2063ad4621edf0dbe218c69a9c4302"
)
LOCKHIT_CONTRACT = "C-f37e6a92ba35a0bf"
LOCKHIT_QUESTION = "Q-47284f43220ab833"
RECEIVER = 0x079B9750
LIST_BASE = RECEIVER + 0x2A4
TARGET = 0x0450D080
NODE = 0x038735A8
PAYLOAD = 0x03BD6710
OLD_FREE_HEAD = 0x03873F18
DATA_PATH_NEUTRAL_BYTES = 17_074
DATA_PATH_NEUTRAL_SHA256 = "af8cd84f1de72734f8928a3528b6c4d2806c47703a4347548abb85e96cdfc57d"
CALL_PATH_NEUTRAL_BYTES = 1_550_073
CALL_PATH_NEUTRAL_SHA256 = "6a846da2f9e605b41e623d2a798f6718d09880fb80ee1f8ab89aca6a509f936d"

DATA_ROOT = Path("local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1")
CALL_ROOT = Path("local-lab/ttd-call-context-level521-target-lock-20260803-v3")
GHIDRA_PROMOTION = Path(
    "local-lab/ghidra-target-lock-semantic-live-promotion-20260804-v2/"
    "promotion/promotion.ready.json"
)
GHIDRA_FUNCTIONS = Path(
    "local-lab/ghidra-target-lock-semantic-live-promotion-20260804-v2/"
    "promotion/runs/live-post-inventory/functions.tsv"
)

INPUTS: dict[str, tuple[int, str]] = {
    "local-lab/ghidra-target-lock-semantic-live-promotion-20260804-v2/promotion/promotion.ready.json": (108418, "77f635e552b7a2dd8425af012204f8172eadcb1de8ecdb02a30e2c12ff9b9945"),
    "local-lab/ghidra-target-lock-semantic-live-promotion-20260804-v2/promotion/runs/live-post-inventory/functions.tsv": (7051712, "f9a06dcdb0ac7510b8bfbf9d655dcf3935a24da603dbc9d3e00f0095fc36af7b"),
    "local-lab/safe-copy-bea-pristine/BEA.exe": (2506752, RUNTIME_SHA256),
    "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup": (2506752, SPECIMEN_SHA256),
    "local-lab/ttd-call-context-level521-target-lock-20260803-v3/preregistration.md": (1942, "745d5073bc4c8509510830b6895e56e5ded8565b6b6acc18806ba6c85a52ecc5"),
    "local-lab/ttd-call-context-level521-target-lock-20260803-v3/run-a/call-context.jsonl": (1551354, "05d45bd7d0dcfb7b4e647efcc532c5171dd1164dd7059f7891b955aed6e135ce"),
    "local-lab/ttd-call-context-level521-target-lock-20260803-v3/run-a/collector-build-receipt.json": (4025, "ca8347c711a9d16b737cec9a5b3eff82be96cf0ef5e8a5d9f32dc6f4fee9b4e3"),
    "local-lab/ttd-call-context-level521-target-lock-20260803-v3/run-a/collector-tool/ttd_exec_coverage.exe": (197632, "bd13563bafdefaa88cfa2b893c5920cb2a68276d4989b0c9b242cc84a668ef47"),
    "local-lab/ttd-call-context-level521-target-lock-20260803-v3/run-a/collector-tool/TTDReplay.dll": (1128520, "b705235016778648f2c194aa76b54669c19ae318d16d340019f8a6f6c86fabbc"),
    "local-lab/ttd-call-context-level521-target-lock-20260803-v3/run-a/collector-tool/TTDReplayCPU.dll": (2865176, "b2a9a06a3c292ef58df31df70ab35a9440dceb3ee36de9c2b08ff4507dd8ef93"),
    "local-lab/ttd-call-context-level521-target-lock-20260803-v3/run-a/manifest.json": (3557, "b39aa024e9dc615174d95e820af3198cdfd991250c8fdf4fc9dbba7987da22e2"),
    "local-lab/ttd-call-context-level521-target-lock-20260803-v3/run-a/READY": (566, "40d70313099b6c804c67d08a5dc2274e0ccb237effd87fb9ddebcc121fa87968"),
    "local-lab/ttd-call-context-level521-target-lock-20260803-v3/run-a/receipt.json": (7315, "2ee4c1688a0c80c5cd10586494f1f1635639f1e1e7de126a4aab03eafe236856"),
    "local-lab/ttd-call-context-level521-target-lock-20260803-v3/run-a/targets.tsv": (535, "07af9d5bb0f45a0e344e3824c2cf5f2d0fa8380231f65cd8f2419ee7d7d373a8"),
    "local-lab/ttd-call-context-level521-target-lock-20260803-v3/run-b/call-context.jsonl": (1551354, "c496431e684e3b565bc37354c2244f9f019d9093fdd4dfa3d5da0065dcab51ef"),
    "local-lab/ttd-call-context-level521-target-lock-20260803-v3/run-b/collector-build-receipt.json": (4025, "ca8347c711a9d16b737cec9a5b3eff82be96cf0ef5e8a5d9f32dc6f4fee9b4e3"),
    "local-lab/ttd-call-context-level521-target-lock-20260803-v3/run-b/manifest.json": (3557, "3f6e48d1e5d2df4e6edde48c8098f8858889ad96586926b9b3b4f822e85eb490"),
    "local-lab/ttd-call-context-level521-target-lock-20260803-v3/run-b/READY": (566, "02d347723dbec2bc650780b7b4cb4960e37769b8febdf736b45006d410337b65"),
    "local-lab/ttd-call-context-level521-target-lock-20260803-v3/run-b/receipt.json": (7315, "ea5dec9f9b569dd9c7182e3bdfaeb68f209489501be7f931651667bb347031f8"),
    "local-lab/ttd-call-context-level521-target-lock-20260803-v3/run-b/targets.tsv": (535, "07af9d5bb0f45a0e344e3824c2cf5f2d0fa8380231f65cd8f2419ee7d7d373a8"),
    "local-lab/ttd-call-context-level521-target-lock-20260803-v3/targets.tsv": (535, "07af9d5bb0f45a0e344e3824c2cf5f2d0fa8380231f65cd8f2419ee7d7d373a8"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-c-v3/collector-build-receipt.json": (3865, "73633e97d424c67cc30c88a26b252108ac42d3136c5e4a825f0d360ce52ceef8"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-c-v3/data-writes.jsonl": (18599, "b03a5d2196a8852c6c9d621d6cb30b1c3f5ecdd08d9721cc53a9fc37436e7b9d"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-c-v3/manifest.json": (4446, "525e859d5cd7d20a46e1ba29363d4d5e7d236767cc60220324f4ab979b46ebbb"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-c-v3/READY": (648, "e1dd9b91f9df8d9872756480c5500fbe3b77ee4447541117f12f5c749e18a758"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-c-v3/receipt.json": (8239, "9d5f3743ac1a35081cd2e0033f95eebdab9af3e5891e162b0bd70ca6a2af7300"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-c-v3/targets.tsv": (167, "9577fcef1341d26e0a8d5c8685c36923f222f459f9f76be199e2d2716fd53cb2"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-d-v3-final/collector-build-receipt.json": (3865, "c30b402bb52cd913429346e5b0e41d474a8cb4d72daad52bf08d62132a87c789"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-d-v3-final/data-writes.jsonl": (18605, "c85386725a211ec4f002ecadfb41ff459dec6ba05638d3ed00e922ed572c4483"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-d-v3-final/manifest.json": (4488, "7b756119a150a39d05073863ebe9a6afa9bf21950073daabc0f6ce63a03ec7e1"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-d-v3-final/READY": (654, "3f47fbb387d7523126c7de7bb767abf8f9afaf7b2d417428f65231ba67b89ee6"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-d-v3-final/receipt.json": (8281, "fc48eef6e5500a52f3b595e060a9951cfd2d5cea79ba0d7dc612ec9a53ed8a4f"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-d-v3-final/targets.tsv": (167, "9577fcef1341d26e0a8d5c8685c36923f222f459f9f76be199e2d2716fd53cb2"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-e-v3-source-bound/collector-build-receipt.json": (3865, "c30b402bb52cd913429346e5b0e41d474a8cb4d72daad52bf08d62132a87c789"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-e-v3-source-bound/collector-tool/ttd_exec_coverage.exe": (250368, "f6c72a85492f186a1bcbba2af089ec8b6c8303e2621a809a552ae72efa21b6c0"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-e-v3-source-bound/collector-tool/TTDReplay.dll": (1128520, "b705235016778648f2c194aa76b54669c19ae318d16d340019f8a6f6c86fabbc"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-e-v3-source-bound/collector-tool/TTDReplayCPU.dll": (2865176, "b2a9a06a3c292ef58df31df70ab35a9440dceb3ee36de9c2b08ff4507dd8ef93"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-e-v3-source-bound/data-writes.jsonl": (18612, "be6dfbf804c34aa2e38431f67e1c1ade5c55386d66e681df979c090e46e96289"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-e-v3-source-bound/instrument-source/Invoke-TtdDataWrites.ps1": (59509, "5856534e992030a952cad887242222bca4fa82c4759cd48b4962d3d0486fb013"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-e-v3-source-bound/instrument-source/ttd_exec_coverage.cpp": (184335, "370d222100a67e4efaa29875486e5c3aca62cea955cf9b3937276c576c7c18b1"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-e-v3-source-bound/instrument-source/ttd_exec_coverage.vcxproj": (2953, "a152e5b1224a4f32237f6cc15f2fe0ce1d25c37bd88303c02af31f1fcc898d3d"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-e-v3-source-bound/manifest.json": (5786, "dfa248bff0a5af62dba535cfe40b5d531b851045dcd4a916a23c0d05c4eb06ec"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-e-v3-source-bound/READY": (939, "92e74ec7ad0fadbd956463141ffaa25487a310a956b9753d9666f6c179ce4615"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-e-v3-source-bound/receipt.json": (9539, "e39cc7a2a9bc9b801911e0441396ce4e00d86008f8bd97bda0c91a5b02370d74"),
    "local-lab/ttd-data-writes-level521-lockhit-removal-20260803-v1/run-e-v3-source-bound/targets.tsv": (167, "9577fcef1341d26e0a8d5c8685c36923f222f459f9f76be199e2d2716fd53cb2"),
    "references/Onslaught/BattleEngine.cpp": (93772, "138a18d10ad6aa3cb95211d3a1c7e2a14aaaaaf58210ad0d06abff55f2b33d31"),
    "references/Onslaught/BattleEngine.h": (13293, "84c88f5526e951389683e1fb132f70d7f1935139e582c8d9a8d41b2b6b516ccd"),
}


class ProofError(ValueError):
    """The retained evidence does not satisfy the bounded LockHit contract."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProofError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def repository_root() -> Path:
    configured = os.environ.get("BEA_REPO_ROOT")
    return Path(configured).resolve() if configured else Path(__file__).resolve().parents[1]


def read_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProofError(f"cannot parse {label}: {exc}") from exc
    require(isinstance(value, dict), f"{label} root is not an object")
    return value


def _plain_file(path: Path, label: str) -> None:
    require(path.is_file(), f"missing {label}: {path}")
    stat = path.lstat()
    reparse = getattr(stat, "st_file_attributes", 0) & 0x400
    require(not path.is_symlink() and not reparse, f"{label} is a symlink/reparse point")


def stamp(path: Path, root: Path) -> dict[str, Any]:
    _plain_file(path, "evidence file")
    try:
        relative = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        relative = str(path.resolve())
    return {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def exact_inputs(root: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for relative, (size, digest) in sorted(INPUTS.items()):
        path = root / relative
        observed = stamp(path, root)
        require(
            observed["bytes"] == size and observed["sha256"] == digest,
            f"input identity differs: {relative}",
        )
        result[relative] = observed
    return result


def _int(value: Any, label: str) -> int:
    try:
        return int(str(value), 0)
    except (TypeError, ValueError) as exc:
        raise ProofError(f"{label} is not an integer") from exc


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
        row = sections + index * 40
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from(
            "<IIII", image, row + 8
        )
        if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
            return raw_pointer + rva - virtual_address
    raise ProofError(f"VA is not mapped by pristine PE: 0x{va:08x}")


def validate_parent(root: Path) -> dict[str, Any]:
    campaign = root / PARENT_RELATIVE
    ready = campaign / "campaign.ready.json"
    observed = stamp(ready, root)
    require(
        observed["bytes"] == PARENT_READY_BYTES
        and observed["sha256"] == PARENT_READY_SHA256,
        "Generation 16 parent READY differs",
    )
    receipt = read_json(ready, "Generation 16 parent READY")
    reducer = receipt.get("reducer")
    require(
        receipt.get("generation") == 16 and receipt.get("counts") == PARENT_COUNTS,
        "Generation 16 parent population differs",
    )
    require(
        isinstance(reducer, dict) and reducer.get("id") == PARENT_REDUCER_ID,
        "Generation 16 parent reducer differs",
    )
    return {
        "path": PARENT_RELATIVE.as_posix(),
        "ready": observed,
        "reducerId": PARENT_REDUCER_ID,
    }


def validate_trace() -> dict[str, Any]:
    raw = Path(os.path.abspath(TRACE_PATH))
    require(str(raw).lower() == str(TRACE_PATH).lower(), "trace lexical path differs")
    _plain_file(raw, "bound Level 521 trace")
    require(raw.lstat().st_size == TRACE_BYTES, "bound Level 521 trace size differs")
    return {
        "path": str(TRACE_PATH),
        "bytes": TRACE_BYTES,
        "receiptSha256": TRACE_SHA256,
        "actualSizeVerified": True,
        "actualHashRecomputed": False,
    }


def parse_jsonl(path: Path, label: str) -> tuple[list[dict[str, Any]], bytes]:
    raw_lines = path.read_bytes().splitlines(keepends=True)
    try:
        rows = [json.loads(line) for line in raw_lines]
    except json.JSONDecodeError as exc:
        raise ProofError(f"cannot parse {label}: {exc}") from exc
    require(all(isinstance(row, dict) for row in rows), f"{label} has a non-object row")
    return rows, b"".join(raw_lines[1:])


EXPECTED_TRANSITIONS = (
    # target, writer PC, position, address, pre, post, required register subset
    (2, 0x00407157, "0xF379D:0xED4", LIST_BASE + 8, "00000000", "A8358703", {"eax": NODE, "ecx": LIST_BASE, "edx": TARGET}),
    (0, 0x004E5BF7, "0xF379D:0xEEB", LIST_BASE, "A8358703", "00000000", {"eax": NODE, "ecx": LIST_BASE, "esi": PAYLOAD}),
    (1, 0x004E5BFB, "0xF379D:0xEED", LIST_BASE + 4, "A8358703", "00000000", {"eax": NODE, "ecx": LIST_BASE, "esi": PAYLOAD}),
    (4, 0x004E5C13, "0xF379D:0xEF0", NODE + 4, "00000000", "183F8703", {"eax": NODE, "ecx": LIST_BASE, "edx": OLD_FREE_HEAD, "esi": PAYLOAD}),
    (3, 0x004E5C1B, "0xF379D:0xEF2", LIST_BASE + 12, "01000000", "00000000", {"eax": NODE, "ecx": LIST_BASE, "esi": PAYLOAD}),
)


def validate_data_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    require(
        Counter(row.get("kind") for row in rows)
        == Counter({"metadata": 1, "target": 5, "event": 10, "pair": 5, "gap-summary": 1, "summary": 1}),
        "data-write row-kind census differs",
    )
    metadata = next(row for row in rows if row.get("kind") == "metadata")
    expected_metadata = {
        "schema": "bea.ttd.data-writes.v3",
        "trace_bytes": str(TRACE_BYTES),
        "module_base": "0x400000",
        "module_size": "0x5D8000",
        "module_timestamp": "0x3ED21313",
        "requested_from": "0xF379D:0xED3",
        "requested_to": "0xF379D:0xEF3",
        "actual_from": "0xF379D:0xED3",
        "processor_architecture": "x86",
        "replay_mode": "sequential-all-segments",
        "pairing_policy": "exact-same-boundary-structural-candidate",
        "promotion_policy": "bea.ttd.data-writes.exact-window-watchpoint-chain.v1",
    }
    require(
        all(metadata.get(key) == value for key, value in expected_metadata.items()),
        "data-write metadata differs",
    )
    require(Path(str(metadata.get("trace"))).resolve() == TRACE_PATH.resolve(), "data-write trace differs")

    expected_targets = (
        (0, LIST_BASE, "A8358703", "00000000"),
        (1, LIST_BASE + 4, "A8358703", "00000000"),
        (2, LIST_BASE + 8, "00000000", "A8358703"),
        (3, LIST_BASE + 12, "01000000", "00000000"),
        (4, NODE + 4, "00000000", "183F8703"),
    )
    targets = sorted(
        (row for row in rows if row.get("kind") == "target"),
        key=lambda row: _int(row.get("target_index"), "target index"),
    )
    for row, (index, address, before, after) in zip(targets, expected_targets, strict=True):
        require(
            row.get("target_index") == index
            and _int(row.get("address"), "target address") == address
            and row.get("size") == 4,
            f"target {index} identity differs",
        )
        require(
            row.get("expected_overwrite_count") == "1"
            and row.get("expected_write_count") == "1"
            and row.get("observed_overwrite_count") == "1"
            and row.get("observed_write_count") == "1"
            and row.get("observed_pair_count") == "1",
            f"target {index} count differs",
        )
        require(
            row.get("evidence_grade") == "WATCHPOINT_CHAIN_CLOSED"
            and row.get("transition_chain_closed") is True
            and row.get("evidence_checks_passed") is True
            and row.get("expectations_passed") is True,
            f"target {index} grade differs",
        )
        require(
            row.get("initial_memory", {}).get("hex") == before
            and row.get("final_memory", {}).get("hex") == after,
            f"target {index} transition differs",
        )

    events = sorted(
        (row for row in rows if row.get("kind") == "event"),
        key=lambda row: _int(row.get("event_index"), "event index"),
    )
    pairs = sorted(
        (row for row in rows if row.get("kind") == "pair"),
        key=lambda row: _int(row.get("pair_index"), "pair index"),
    )
    writes: list[dict[str, Any]] = []
    for pair_index, expected in enumerate(EXPECTED_TRANSITIONS):
        target_index, pc, position, address, before, after, required_registers = expected
        pair = pairs[pair_index]
        overwrite, write = events[pair_index * 2:pair_index * 2 + 2]
        require(
            pair.get("pair_index") == pair_index
            and pair.get("target_index") == target_index
            and pair.get("overwrite_event_index") == pair_index * 2
            and pair.get("write_event_index") == pair_index * 2 + 1
            and pair.get("grade") == "STRUCTURAL_WRITE_PAIR"
            and pair.get("checks_passed") is True
            and pair.get("changed") is True,
            f"pair {pair_index} differs",
        )
        common = (
            "target_index", "pair_index", "continuity_epoch", "position", "previous_position",
            "unique_thread_id", "os_thread_id", "pc", "sp", "fp", "access_address",
            "access_size", "registers",
        )
        require(
            all(overwrite.get(key) == write.get(key) for key in common),
            f"pair {pair_index} overwrite/write boundary differs",
        )
        require(
            overwrite.get("event_index") == pair_index * 2
            and write.get("event_index") == pair_index * 2 + 1
            and overwrite.get("event_type") == "Overwrite"
            and write.get("event_type") == "Write",
            f"pair {pair_index} phases differ",
        )
        require(
            overwrite.get("target_index") == target_index
            and overwrite.get("pair_index") == pair_index
            and _int(overwrite.get("pc"), "writer PC") == pc
            and overwrite.get("position") == position
            and _int(overwrite.get("access_address"), "write address") == address
            and overwrite.get("access_size") == "4"
            and overwrite.get("continuity_epoch") == "0",
            f"pair {pair_index} identity differs",
        )
        require(
            overwrite.get("observed_memory", {}).get("hex") == before
            and write.get("observed_memory", {}).get("hex") == after,
            f"pair {pair_index} value differs",
        )
        registers = overwrite.get("registers")
        require(isinstance(registers, dict), f"pair {pair_index} registers are absent")
        require(
            all(_int(registers.get(name), f"pair {pair_index} {name}") == value for name, value in required_registers.items()),
            f"pair {pair_index} receiver/target/payload join differs",
        )
        writes.append({
            "order": pair_index + 1,
            "writerPc": f"0x{pc:08x}",
            "position": position,
            "address": f"0x{address:08x}",
            "beforeHex": before,
            "afterHex": after,
        })

    gap = next(row for row in rows if row.get("kind") == "gap-summary")
    require(
        all(str(value) == "0" for key, value in gap.items() if key not in {"schema", "kind"}),
        "data-write gap census differs",
    )
    summary = next(row for row in rows if row.get("kind") == "summary")
    expected_summary = {
        "target_count": 5,
        "event_count": 10,
        "pair_count": "5",
        "orphan_event_count": "0",
        "callback_hits": "10",
        "ambiguous_callbacks": "0",
        "nontrivial_gap_count": "0",
        "continuity_break_count": "0",
        "instructions_executed": "32",
        "steps_executed": "32",
        "final_position": "0xF379D:0xEF3",
        "replay_complete": True,
        "replay_counters_sane": True,
        "pairing_complete": True,
        "target_evidence_passed": True,
        "expectations_passed": True,
        "collector_checks_passed": True,
        "truncated": False,
        "callback_failed": False,
    }
    require(
        all(summary.get(key) == value for key, value in expected_summary.items()),
        "data-write summary differs",
    )
    return {
        "window": {"fromExclusive": "0xF379D:0xED3", "toInclusive": "0xF379D:0xEF3"},
        "receiver": f"0x{RECEIVER:08x}",
        "inputTarget": f"0x{TARGET:08x}",
        "listBase": f"0x{LIST_BASE:08x}",
        "soleNode": f"0x{NODE:08x}",
        "payload": f"0x{PAYLOAD:08x}",
        "oldFreeHead": f"0x{OLD_FREE_HEAD:08x}",
        "orderedWrites": writes,
        "instructions": 32,
        "gapFree": True,
    }


def validate_data_receipt(path: Path) -> dict[str, Any]:
    receipt = read_json(path, "source-bound data-write receipt")
    require(receipt.get("schemaVersion") == "bea-ttd-data-writes-receipt.v3", "data receipt schema differs")
    require(
        receipt.get("collectorExitCode") == 0
        and receipt.get("exitCode") == 0
        and receipt.get("readyEligible") is True,
        "data receipt READY disposition differs",
    )
    trace = receipt.get("trace")
    target = receipt.get("target")
    invocation = receipt.get("invocation")
    data = receipt.get("dataWrites")
    require(
        isinstance(trace, dict)
        and trace.get("bytes") == TRACE_BYTES
        and str(trace.get("sha256", "")).lower() == TRACE_SHA256,
        "data receipt trace differs",
    )
    require(
        isinstance(target, dict)
        and target.get("bytes") == 2_506_752
        and str(target.get("sha256", "")).lower() == RUNTIME_SHA256,
        "data receipt runtime differs",
    )
    require(
        isinstance(invocation, dict)
        and invocation.get("from") == "0xF379D:0xED3"
        and invocation.get("to") == "0xF379D:0xEF3"
        and invocation.get("replayMode") == "sequential-all-segments",
        "data receipt window differs",
    )
    require(
        isinstance(data, dict)
        and data.get("schemaVersion") == "bea.ttd.data-writes.v3"
        and data.get("lineCount") == 23
        and data.get("targetCount") == 5
        and data.get("eventCount") == 10
        and data.get("pairCount") == 5
        and data.get("orphanEventCount") == 0,
        "data receipt row census differs",
    )
    source = receipt.get("instrumentSource")
    require(
        isinstance(source, dict)
        and str(source.get("wrapper", {}).get("sha256", "")).lower()
        == "5856534e992030a952cad887242222bca4fa82c4759cd48b4962d3d0486fb013"
        and str(source.get("collectorCpp", {}).get("sha256", "")).lower()
        == "370d222100a67e4efaa29875486e5c3aca62cea955cf9b3937276c576c7c18b1",
        "data receipt source binding differs",
    )
    return receipt


def validate_data_evidence(root: Path) -> dict[str, Any]:
    paths = [
        root / DATA_ROOT / "run-c-v3/data-writes.jsonl",
        root / DATA_ROOT / "run-d-v3-final/data-writes.jsonl",
        root / DATA_ROOT / "run-e-v3-source-bound/data-writes.jsonl",
    ]
    parsed = [parse_jsonl(path, f"data-write replica {index + 1}") for index, path in enumerate(paths)]
    tails = [tail for _rows, tail in parsed]
    require(
        all(len(tail) == DATA_PATH_NEUTRAL_BYTES and sha256_bytes(tail) == DATA_PATH_NEUTRAL_SHA256 for tail in tails),
        "data-write path-neutral identity differs",
    )
    require(tails[0] == tails[1] == tails[2], "data-write replicas differ after metadata")
    results = [validate_data_rows(rows) for rows, _tail in parsed]
    require(results[0] == results[1] == results[2], "data-write semantic replicas differ")
    validate_data_receipt(root / DATA_ROOT / "run-e-v3-source-bound/receipt.json")
    ready = read_json(root / DATA_ROOT / "run-e-v3-source-bound/READY", "source-bound data READY")
    require(
        ready.get("schemaVersion") == "bea-ttd-data-writes-ready.v3"
        and str(ready.get("receiptSha256", "")).lower()
        == "e39cc7a2a9bc9b801911e0441396ce4e00d86008f8bd97bda0c91a5b02370d74"
        and str(ready.get("dataWritesSha256", "")).lower()
        == "be6dfbf804c34aa2e38431f67e1c1ade5c55386d66e681df979c090e46e96289",
        "source-bound data READY differs",
    )
    return {
        **results[0],
        "replicas": 3,
        "sameImmutableTraceEvent": True,
        "independentGameplayReplicas": False,
        "pathNeutralBytes": DATA_PATH_NEUTRAL_BYTES,
        "pathNeutralSha256": DATA_PATH_NEUTRAL_SHA256,
    }


def validate_call_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    require(
        Counter(row.get("kind") for row in rows)
        == Counter({"metadata": 1, "target": 14, "event": 1344, "invocation": 448, "gap-summary": 1, "summary": 1}),
        "call-context row-kind census differs",
    )
    metadata = next(row for row in rows if row.get("kind") == "metadata")
    expected_metadata = {
        "schema": "bea.ttd.call-context.v2",
        "trace_bytes": str(TRACE_BYTES),
        "module_base": "0x400000",
        "module_size": "0x5D8000",
        "module_timestamp": "0x3ED21313",
        "requested_from": "0x5FF4E:0x0",
        "requested_to": "0x1EAB39:0x270F",
        "processor_architecture": "x86",
        "replay_mode": "sequential-all-segments",
        "raw_value_policy": "untyped-registers-and-bytes",
        "stack_bytes_requested": 64,
    }
    require(
        all(metadata.get(key) == value for key, value in expected_metadata.items()),
        "call-context metadata differs",
    )
    lockhit_target = next(
        (row for row in rows if row.get("kind") == "target" and row.get("target_index") == 11),
        None,
    )
    require(
        isinstance(lockhit_target, dict)
        and lockhit_target.get("entry_va") == "0x407140"
        and lockhit_target.get("ranges") == [{"rva_start": "0x7140", "rva_end_exclusive": "0x71A9"}]
        and lockhit_target.get("observed_entry_count") == "24"
        and lockhit_target.get("observed_call_count") == "24"
        and lockhit_target.get("observed_return_count") == "24"
        and lockhit_target.get("observed_call_entry_pair_count") == "24"
        and lockhit_target.get("observed_validated_return_count") == "23"
        and lockhit_target.get("observed_gap_free_envelope_count") == "23"
        and lockhit_target.get("expectations_passed") is True,
        "LockHit call-context aggregate differs",
    )
    selected = [
        row for row in rows
        if row.get("kind") == "event"
        and row.get("target_index") == 11
        and row.get("invocation_index") == 189
        and row.get("position") in {"0xF379D:0xECC", "0xF379D:0xECD"}
    ]
    require(len(selected) == 2, "LockHit selected call/entry boundary differs")
    call, entry = selected
    require(call.get("event_type") == "call" and entry.get("event_type") == "entry", "LockHit selected phases differ")
    require(
        call.get("event_index") == 567
        and entry.get("event_index") == 568
        and call.get("pc") == "0x4D959A"
        and call.get("instruction_target") == "0x407140"
        and call.get("fallthrough") == "0x4D959F"
        and entry.get("pc") == "0x407140"
        and entry.get("previous_position") == "0xF379D:0xECC",
        "LockHit selected call/entry identity differs",
    )
    for event in (call, entry):
        registers = event.get("registers")
        require(
            isinstance(registers, dict)
            and _int(registers.get("ecx"), "call-context ECX") == RECEIVER
            and _int(registers.get("edx"), "call-context EDX") == TARGET
            and event.get("unique_thread_id") == "5"
            and event.get("os_thread_id") == "49924"
            and event.get("control_registers_valid") is True
            and event.get("integer_registers_valid") is True
            and event.get("register_views_agree") is True,
            "LockHit selected register boundary differs",
        )
    invocation = next(
        (row for row in rows if row.get("kind") == "invocation" and row.get("invocation_index") == 189),
        None,
    )
    require(
        isinstance(invocation, dict)
        and invocation.get("target_index") == 11
        and invocation.get("call_event_index") == 567
        and invocation.get("entry_event_index") == 568
        and invocation.get("return_event_index") is None
        and invocation.get("grade") == "CALL_ENTRY"
        and invocation.get("call_entry_checks_passed") is True
        and invocation.get("return_checks_passed") is False
        and invocation.get("gap_crossed") is True,
        "LockHit selected invocation grade differs",
    )
    summary = next(row for row in rows if row.get("kind") == "summary")
    expected_summary = {
        "target_count": 14,
        "event_count": 1344,
        "invocation_count": 448,
        "call_entry_pair_count": "448",
        "validated_return_count": "289",
        "gap_free_envelope_count": "289",
        "truncated": False,
        "callback_failed": False,
        "ordering_valid": True,
        "contexts_valid": True,
        "expectations_passed": True,
        "pairing_expectations_passed": True,
        "replay_complete": True,
        "collector_checks_passed": True,
    }
    require(
        all(summary.get(key) == value for key, value in expected_summary.items()),
        "call-context summary differs",
    )
    return {
        "callPosition": "0xF379D:0xECC",
        "entryPosition": "0xF379D:0xECD",
        "caller": "0x004d959a",
        "entry": "0x00407140",
        "receiver": f"0x{RECEIVER:08x}",
        "inputTarget": f"0x{TARGET:08x}",
        "callEntryReplicated": True,
        "selectedInvocationReturnObserved": False,
        "allLockHitCalls": 24,
        "allLockHitValidatedReturns": 23,
    }


def validate_call_receipt(path: Path) -> None:
    receipt = read_json(path, "call-context receipt")
    require(receipt.get("schemaVersion") == "bea-ttd-call-context-receipt.v2", "call receipt schema differs")
    require(
        receipt.get("collectorExitCode") == 0
        and receipt.get("exitCode") == 0
        and receipt.get("readyEligible") is True,
        "call receipt READY disposition differs",
    )
    trace = receipt.get("trace")
    target = receipt.get("target")
    invocation = receipt.get("invocation")
    context = receipt.get("callContext")
    require(
        isinstance(trace, dict)
        and trace.get("bytes") == TRACE_BYTES
        and str(trace.get("sha256", "")).lower() == TRACE_SHA256,
        "call receipt trace differs",
    )
    require(
        isinstance(target, dict)
        and target.get("bytes") == 2_506_752
        and str(target.get("sha256", "")).lower() == RUNTIME_SHA256,
        "call receipt runtime differs",
    )
    require(
        isinstance(invocation, dict)
        and invocation.get("from") == "0x5FF4E:0x0"
        and invocation.get("to") == "0x1EAB39:0x270F"
        and invocation.get("stackBytes") == 64
        and invocation.get("eventLimit") == 2500,
        "call receipt invocation differs",
    )
    require(
        isinstance(context, dict)
        and context.get("schemaVersion") == "bea.ttd.call-context.v2"
        and context.get("lineCount") == 1809
        and context.get("targetCount") == 14
        and context.get("eventCount") == 1344
        and context.get("invocationCount") == 448
        and context.get("callEntryPairCount") == 448
        and context.get("validatedReturnCount") == 289,
        "call receipt census differs",
    )


def validate_call_evidence(root: Path) -> dict[str, Any]:
    paths = [
        root / CALL_ROOT / "run-a/call-context.jsonl",
        root / CALL_ROOT / "run-b/call-context.jsonl",
    ]
    parsed = [parse_jsonl(path, f"call-context replica {index + 1}") for index, path in enumerate(paths)]
    tails = [tail for _rows, tail in parsed]
    require(
        all(len(tail) == CALL_PATH_NEUTRAL_BYTES and sha256_bytes(tail) == CALL_PATH_NEUTRAL_SHA256 for tail in tails),
        "call-context path-neutral identity differs",
    )
    require(tails[0] == tails[1], "call-context replicas differ after metadata")
    results = [validate_call_rows(rows) for rows, _tail in parsed]
    require(results[0] == results[1], "call-context semantic replicas differ")
    validate_call_receipt(root / CALL_ROOT / "run-a/receipt.json")
    validate_call_receipt(root / CALL_ROOT / "run-b/receipt.json")
    return {
        **results[0],
        "replicas": 2,
        "sameImmutableTrace": True,
        "independentGameplayReplicas": False,
        "pathNeutralBytes": CALL_PATH_NEUTRAL_BYTES,
        "pathNeutralSha256": CALL_PATH_NEUTRAL_SHA256,
    }


def validate_static(root: Path) -> dict[str, Any]:
    pristine = (root / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup").read_bytes()
    runtime = (root / "local-lab/safe-copy-bea-pristine/BEA.exe").read_bytes()
    lockhit_offset = _pe_offset(pristine, LOCKHIT_ENTRY)
    remove_offset = _pe_offset(pristine, REMOVE_ENTRY)
    lockhit = pristine[lockhit_offset:lockhit_offset + LOCKHIT_END - LOCKHIT_ENTRY]
    remove = pristine[remove_offset:remove_offset + REMOVE_END - REMOVE_ENTRY]
    require(len(lockhit) == 105 and sha256_bytes(lockhit) == LOCKHIT_BODY_SHA256, "LockHit body differs")
    require(len(remove) == 82 and sha256_bytes(remove) == REMOVE_BODY_SHA256, "CSPtrSet::Remove body differs")
    require(runtime[lockhit_offset:lockhit_offset + 105] == lockhit, "runtime LockHit bytes differ from pristine")
    require(runtime[remove_offset:remove_offset + 82] == remove, "runtime Remove bytes differ from pristine")
    differences = [index for index, (left, right) in enumerate(zip(pristine, runtime, strict=True)) if left != right]
    require(differences == [0x12A644, 0x12A645, 0x12A646, 0x12A647], "runtime patch boundary differs")
    require(
        lockhit == bytes.fromhex(
            "8b5424045685d2745c8b81a402000081c1a402000085c089410874048b00eb0233c0"
            "85c08bf0743d3916741d8b41088b400485c089410874048b00eb0233c085c08bf075"
            "e35ec2040056e841ea0d0085f674128bcee83640040056b9f03d9c00e87b2014005e"
            "c20400"
        ),
        "LockHit exact instruction bytes differ",
    )
    require(
        remove == bytes.fromhex(
            "8b0133d25685c074458b7424083930740d8bd08b400485c075f35ec204003901750e"
            "8b500485d289117512895104eb0d8b700485f689720475038951048b1530d183008950"
            "04a330d18300ff490c5ec20400"
        ),
        "CSPtrSet::Remove exact instruction bytes differ",
    )
    cpp = (root / "references/Onslaught/BattleEngine.cpp").read_text(encoding="utf-8")
    header = (root / "references/Onslaught/BattleEngine.h").read_text(encoding="utf-8")
    source_law = (
        "void\tCBattleEngine::LockHit(\n\tCThing\t\t*inUnit)\n{\n\tif (inUnit)\n\t{\n"
        "\t\tfor (CLockInfo *item=mFiredLocks.First(); item; item=mFiredLocks.Next())\n"
        "\t\t{\n\t\t\tif (item->mUnit.ToRead()==inUnit)\n\t\t\t{\n"
        "\t\t\t\tmFiredLocks.Remove(item);\n\t\t\t\tdelete item;\n\t\t\t\treturn;"
    )
    require(source_law in cpp, "Stuart LockHit source law differs")
    require(
        "void\t\t\t\t\tLockHit(" in header
        and "SPtrSet<CLockInfo>\t\tmFiredLocks;" in header,
        "Stuart LockHit declaration/storage differs",
    )
    return {
        "lockHit": {
            "entryVa": "0x00407140",
            "endExclusive": "0x004071a9",
            "bytes": 105,
            "sha256": LOCKHIT_BODY_SHA256,
            "instructions": 41,
            "prototype": "void __thiscall CBattleEngine__LockHit(CBattleEngine *this, CThing *inUnit)",
        },
        "remove": {
            "entryVa": "0x004e5bd0",
            "endExclusive": "0x004e5c22",
            "bytes": 82,
            "sha256": REMOVE_BODY_SHA256,
            "instructions": 33,
        },
        "sourceArchitectureJoined": True,
        "runtimePatchOffsets": ["0x12a644", "0x12a645", "0x12a646", "0x12a647"],
        "runtimePatchOutsideBothBodies": True,
    }


def validate_ghidra(root: Path) -> dict[str, Any]:
    promotion = read_json(root / GHIDRA_PROMOTION, "target-lock Ghidra promotion")
    require(
        promotion.get("schema") == "bea.re.ghidra-target-lock-semantic-live-promotion.v1"
        and promotion.get("status") == "READY"
        and promotion.get("state") == "POST"
        and promotion.get("campaignPublicationAuthorized") is True,
        "target-lock Ghidra promotion disposition differs",
    )
    with (root / GHIDRA_FUNCTIONS).open("r", encoding="utf-8", newline="") as stream:
        rows = {row["address"]: row for row in csv.DictReader(stream, delimiter="\t")}
    lockhit = rows.get("0x00407140")
    remove = rows.get("0x004e5bd0")
    require(lockhit is not None and remove is not None, "Ghidra inventory lacks LockHit/Remove")
    require(
        lockhit["name"] == "CBattleEngine__LockHit"
        and lockhit["nameSource"] == "USER_DEFINED"
        and lockhit["sigSource"] == "USER_DEFINED"
        and lockhit["bodyBytes"] == "105"
        and lockhit["bodyMin"] == "0x00407140"
        and lockhit["bodyMax"] == "0x004071a8"
        and lockhit["instrCount"] == "41"
        and lockhit["callingConv"] == "__thiscall"
        and lockhit["returnType"] == "void"
        and lockhit["signature"]
        == "void __thiscall CBattleEngine__LockHit(void * this, void * inUnit)",
        "Ghidra LockHit identity differs",
    )
    require(
        remove["name"] == "CSPtrSet__Remove"
        and remove["bodyBytes"] == "82"
        and remove["bodyMin"] == "0x004e5bd0"
        and remove["bodyMax"] == "0x004e5c21"
        and remove["instrCount"] == "33",
        "Ghidra Remove identity differs",
    )
    return {
        "promotionReady": stamp(root / GHIDRA_PROMOTION, root),
        "functionsInventory": stamp(root / GHIDRA_FUNCTIONS, root),
        "lockHitName": "CBattleEngine__LockHit",
        "removeName": "CSPtrSet__Remove",
        "liveMutationRequiredForThisContract": False,
        "reason": "the exact body, name, signature, and bounded runtime comment were already promoted and read back",
    }


EXPECTED_BOUNDARY = {
    "nonNullPathOnly": True,
    "soleMatchingNodeOnly": True,
    "containerEmptied": True,
    "nodeNextLinkedToOldFreeHeadDirectlyWatched": True,
    "globalFreeHeadStoreExecutedByGapFreeStaticJoin": True,
    "globalFreeHeadDirectlyWatched": False,
    "payloadDestructorObserved": False,
    "payloadFreeObserved": False,
    "fullSelectedInvocationReturnObserved": False,
    "nullPathProved": False,
    "notFoundPathProved": False,
    "multiNodePathProved": False,
    "independentGameplayReplication": False,
}


def validate_claim_boundary(value: dict[str, Any]) -> None:
    require(value == EXPECTED_BOUNDARY, "claim boundary differs")


def validate_evidence(root: Path) -> dict[str, Any]:
    root = root.resolve()
    inputs = exact_inputs(root)
    parent = validate_parent(root)
    trace = validate_trace()
    static = validate_static(root)
    calls = validate_call_evidence(root)
    writes = validate_data_evidence(root)
    ghidra = validate_ghidra(root)
    require(calls["receiver"] == writes["receiver"], "call/write receiver join differs")
    require(calls["inputTarget"] == writes["inputTarget"], "call/write target join differs")
    boundary = dict(EXPECTED_BOUNDARY)
    validate_claim_boundary(boundary)
    return {
        "schema": OBSERVATION_SCHEMA,
        "parent": parent,
        "specimen": {"bytes": 2_506_752, "sha256": SPECIMEN_SHA256},
        "runtime": {
            "bytes": 2_506_752,
            "sha256": RUNTIME_SHA256,
            "fourBytePatchOutsideTargetBodies": True,
        },
        "trace": trace,
        "static": static,
        "callContext": calls,
        "dataWrites": writes,
        "ghidra": ghidra,
        "contract": {
            "entityKey": LOCKHIT_ENTITY,
            "contractId": LOCKHIT_CONTRACT,
            "questionId": LOCKHIT_QUESTION,
            "grade": "C2_BOUNDED_RUNTIME",
            "receiver": "one observed CBattleEngine instance at 0x079b9750",
            "inputs": "one observed non-null CThing pointer 0x0450d080",
            "returns": "void ABI; the selected invocation's full return was not observed",
            "writes": (
                "mFiredLocks iterator/head/tail/size and removed SPtrSetNode next; "
                "gap-free static/runtime execution also reaches the global free-head store"
            ),
            "sideEffects": (
                "the observed sole matching fired-lock node is unlinked, the container becomes empty, "
                "and the node is linked to the prior free-list head"
            ),
            "preconditions": "observed target non-null; one-node fired-lock list; sole node payload points to target",
            "failureModes": "null, not-found, and multi-node behavior remain open",
            "authorVerdict": "SUPPORTED_BY_PE_OR_RUNTIME",
            "runtimeVerdict": "MEASURED_BOUNDED_PATH",
            "refuterVerdict": "SURVIVED",
            "rebuildDisposition": "CONTRACT_PROVED_SYSTEM_NOT_YET_MODELED",
        },
        "claimBoundary": boundary,
        "inputs": inputs,
    }


def selftest(root: Path) -> dict[str, Any]:
    source, _tail = parse_jsonl(
        root / DATA_ROOT / "run-e-v3-source-bound/data-writes.jsonl",
        "selftest data source",
    )
    attacks: list[tuple[str, list[dict[str, Any]], str]] = []
    wrong_receiver = copy.deepcopy(source)
    for row in wrong_receiver:
        if row.get("kind") == "event" and row.get("pair_index") == 0:
            row["registers"]["ecx"] = "0x79B99F5"
    attacks.append(("receiver", wrong_receiver, "receiver/target/payload join differs"))
    wrong_target = copy.deepcopy(source)
    for row in wrong_target:
        if row.get("kind") == "event" and row.get("pair_index") == 0:
            row["registers"]["edx"] = "0x450D084"
    attacks.append(("target", wrong_target, "receiver/target/payload join differs"))
    wrong_payload = copy.deepcopy(source)
    for row in wrong_payload:
        if row.get("kind") == "event" and row.get("pair_index") == 1:
            row["registers"]["esi"] = "0x3BD6714"
    attacks.append(("payload", wrong_payload, "receiver/target/payload join differs"))
    wrong_order = copy.deepcopy(source)
    pair = next(row for row in wrong_order if row.get("kind") == "pair" and row.get("pair_index") == 0)
    pair["target_index"] = 0
    attacks.append(("write-order", wrong_order, "pair 0 differs"))
    wrong_count = copy.deepcopy(source)
    target = next(row for row in wrong_count if row.get("kind") == "target" and row.get("target_index") == 3)
    target["observed_write_count"] = "2"
    attacks.append(("write-count", wrong_count, "target 3 count differs"))
    rejected: list[str] = []
    for name, rows, expected in attacks:
        try:
            validate_data_rows(rows)
        except ProofError as exc:
            require(expected in str(exc), f"{name} rejected by unintended gate: {exc}")
            rejected.append(name)
        else:
            raise ProofError(f"selftest attack accepted: {name}")

    for name, key in (
        ("global-head-direct-watch-overclaim", "globalFreeHeadDirectlyWatched"),
        ("full-return-overclaim", "fullSelectedInvocationReturnObserved"),
        ("payload-destruction-overclaim", "payloadDestructorObserved"),
        ("independent-gameplay-overclaim", "independentGameplayReplication"),
    ):
        forged = dict(EXPECTED_BOUNDARY)
        forged[key] = True
        try:
            validate_claim_boundary(forged)
        except ProofError as exc:
            require("claim boundary differs" in str(exc), f"{name} rejected by unintended gate")
            rejected.append(name)
        else:
            raise ProofError(f"selftest attack accepted: {name}")
    return {"count": len(rejected), "attacks": rejected}


def _validate_saved(root: Path, proof_root: Path, receipt: dict[str, Any]) -> dict[str, Any]:
    require(
        set(receipt)
        == {"schema", "generatedAtUtc", "verdict", "claim", "author", "parent", "observation", "selftest", "limitations"},
        "proof receipt shape differs",
    )
    require(
        receipt.get("schema") == PROOF_SCHEMA
        and receipt.get("verdict") == "SURVIVED"
        and receipt.get("claim") == "LOCKHIT_ONE_NODE_REMOVAL_BOUNDED_CONTRACT",
        "proof verdict/claim differs",
    )
    try:
        generated = datetime.fromisoformat(str(receipt.get("generatedAtUtc")))
    except ValueError as exc:
        raise ProofError("proof generatedAtUtc is invalid") from exc
    require(generated.tzinfo is not None, "proof generatedAtUtc lacks a timezone")
    frozen_author = proof_root / "author.py"
    require(receipt.get("author") == stamp(frozen_author, proof_root), "proof author stamp differs")
    require(frozen_author.read_bytes() == Path(__file__).resolve().read_bytes(), "executing/frozen proof authors differ")
    require(receipt.get("parent") == validate_parent(root), "proof parent differs")
    observation_path = proof_root / OBSERVATION_NAME
    require(receipt.get("observation") == stamp(observation_path, proof_root), "proof observation stamp differs")
    observed = read_json(observation_path, "saved LockHit observation")
    require(observed == validate_evidence(root), "saved LockHit observation does not rederive")
    require(receipt.get("selftest") == selftest(root), "proof selftest differs")
    limitations = receipt.get("limitations")
    require(
        isinstance(limitations, list)
        and "The retained 14 GiB trace is receipt-hash-bound and actual-size-checked, not rehashed by this proof." in limitations
        and "The three data-write outputs and two call-context outputs replay one immutable gameplay event; they are deterministic tool replications, not independent gameplay replications." in limitations
        and "No new Ghidra mutation is authorized or required: the exact LockHit identity and bounded runtime comment were already promoted and read back." in limitations,
        "proof limitations differ",
    )
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
        observation_path = stage / OBSERVATION_NAME
        observation_path.write_text(json.dumps(observation, indent=2) + "\n", encoding="utf-8")
        receipt = {
            "schema": PROOF_SCHEMA,
            "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
            "verdict": "SURVIVED",
            "claim": "LOCKHIT_ONE_NODE_REMOVAL_BOUNDED_CONTRACT",
            "author": stamp(frozen_author, stage),
            "parent": parent,
            "observation": stamp(observation_path, stage),
            "selftest": tests,
            "limitations": [
                "The retained 14 GiB trace is receipt-hash-bound and actual-size-checked, not rehashed by this proof.",
                "The three data-write outputs and two call-context outputs replay one immutable gameplay event; they are deterministic tool replications, not independent gameplay replications.",
                "The observed path has a non-null target and one matching fired-lock node; null, not-found, and multi-node behavior remain open.",
                "The selected call/entry pair has no validated return backlink, and the write window ends inside CSPtrSet::Remove; payload destruction/free and the full LockHit return remain unobserved.",
                "The global free-head store is reached by a gap-free static/runtime path, but the global itself was not directly watched before and after.",
                "Stuart source supplies architecture and names; pristine bytes and retained TTD evidence own the released-state claim.",
                "No new Ghidra mutation is authorized or required: the exact LockHit identity and bounded runtime comment were already promoted and read back.",
                "The target pointer is bounded to CComponent/CUnit lineage; faction, authored object, and model identity are not proved.",
                "The reconstruction does not yet model the fired-lock container; this proof establishes a retail contract rather than pretending a whole subsystem is rebuild-ready.",
            ],
        }
        (stage / READY_NAME).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        _validate_saved(root, stage, receipt)
        require(author_path.read_bytes() == author_start, "proof author changed before publication")
        os.replace(stage, out)
        return _validate_saved(root, out, read_json(out / READY_NAME, "LockHit proof READY"))
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def verify(root: Path, proof_root: Path) -> dict[str, Any]:
    return _validate_saved(
        root.resolve(),
        proof_root.resolve(),
        read_json(proof_root.resolve() / READY_NAME, "LockHit proof READY"),
    )


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
            print(f"LOCKHIT_BOUNDED_CONTRACT_PROOF_READY verdict={receipt['verdict']}")
        elif args.command == "verify":
            receipt = verify(args.repo, args.proof)
            print(f"LOCKHIT_BOUNDED_CONTRACT_PROOF_VERIFIED verdict={receipt['verdict']}")
        else:
            result = selftest(args.repo.resolve())
            print(f"LOCKHIT_BOUNDED_CONTRACT_SELFTEST_OK attacks={result['count']}")
        return 0
    except (OSError, ProofError) as exc:
        print(f"LOCKHIT_BOUNDED_CONTRACT_PROOF_FAILED: {exc}", file=sys.stderr)
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
