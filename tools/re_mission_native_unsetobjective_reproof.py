#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Verify the frozen Mission-native UnsetObjective body/NOP proof.

This proof is static and read-only. It binds the pristine retail executable,
canonical Generation 18, the shipped Mission-native registry, the preserved
police-reopen disposition, a frozen Ghidra POST manifest, a read-only Ghidra
listing/xref export, and the pinned GPL source. The historical project database
is cold recovery material now: verification requires an explicitly restored
copy and never falls through to the active mutable Linux project.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import os
import stat
import struct
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


SCHEMA = "bea.re.mission-native-unsetobjective-boundary-reproof.v1"
CLAIM = "MISSION_NATIVE_UNSETOBJECTIVE_EXACT_FUNCTION_NOP_PARTITION_AND_STATIC_CONTRACT"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
EVIDENCE_RELATIVE = Path("local-lab/mission-native-unsetobjective-boundary-reproof-20260809-v1")
READY_NAME = "proof.ready.json"
HISTORICAL_PROJECT_RELATIVE = Path(
    "local-lab/ghidra-mission-native-setpos-live-promotion-20260809-v1/"
    "backups/post-live"
)
ACTIVE_MUTABLE_PROJECT_RELATIVE = Path("local-lab/ghidra-projects/BEA")
TRACKED_CHECKPOINT_RELATIVE = Path("reverse-engineering/ghidra")
COLD_PACKAGE_PARENT = Path("/srv/archive-a/onslaught-ghidra-cold/codex-consolidated-2026-08-31")
COLD_RESTORE_GUIDANCE = (
    f"locate {HISTORICAL_PROJECT_RELATIVE.as_posix()} in a package catalog "
    "under /srv/archive-a/onslaught-ghidra-cold/codex-consolidated-2026-08-31, restore its tree to a new "
    "empty writable directory, then pass --ghidra-project-root; never use the "
    "active mutable project or tracked checkpoint"
)
HISTORICAL_AUTHOR_STAMP = {
    "path": "tools/re_mission_native_unsetobjective_reproof.py",
    "bytes": 52_888,
    "sha256": "1d67823b54c465986b8b2e83ea9e1b278eef2e5dd91e509404399c21eba456fb",
}

PARENT_RELATIVE = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-18-tokenarchive-parser-contract-v1"
)
PARENT_AUTHORITY_RELATIVE = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-18-tokenarchive-parser-contract-authority.ready.json"
)
PARENT_READY_SHA256 = "4ae3a7b8dc4baa7cb83125fc8005503499b083fd1944f19bdfb84755f663d97e"
PARENT_REDUCER_ID = "ee8bddfb4cf6f05f768d9e067ea1330753eecbb3f7eb97553dfe6fa4da8bad74"
PARENT_AUTHORITY_SHA256 = "c13dcef4aaae7c95b08bd75a502069a47274e9d577b48b05c57a5f3adcf6b7a6"
PARENT_COUNTS = {
    "functions": 8125,
    "residuals": 6118,
    "questions": 15254,
    "scenarios": 72,
    "levers": 915,
    "contracts": 14243,
    "adjudications": 6097,
    "supersessions": 588,
}

CLOSURE_RELATIVE = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/gen73-claim-closure-v1"
)
CLOSURE_READY_SHA256 = "94d7a9eb380752671fdc5d5a152e1491bc6d4e4c87c225b8a1c385e39d0323e0"
POLICE_SHA256 = "83720df93d8a808e8083ffb276f51dcf034b5bfd4992b7bd832acf6182d9a701"

RESIDUAL_START = 0x00535EDD
FUNCTION_START = 0x00535EE0
FUNCTION_END = 0x00535EED
RESIDUAL_END = 0x00535EF0
TWIN_START = 0x00535ED0
TWIN_END = 0x00535EDD
CALLEE_START = 0x004F3970
CALLEE_END = 0x004F39AD
REGISTRY_HANDLER_LOAD = 0x005309AB
REGISTRY_HANDLER_STORE = 0x005309B5
REGISTRY_NAME_STORE = 0x00530A30
REGISTRY_RECORD = 0x0064D5A0
REGISTRY_SLOT = 0x0064D5D0
NAME_ADDRESS = 0x0064F8DC

RESIDUAL_SHA256 = "8d2e6f2033636447b425869b01e7e137c04f547be820d27e0fbff8978950d8dc"
PADDING_SHA256 = "e65ca7c06ae3e9bacd16f6d87026d2fd51447f87f8771676568af93c6313d707"
BODY_SHA256 = "0ec7dfff6ad0dba017b45b0a9840f6b587b899e88aaedb29d1d0eabfb842b35f"
TWIN_SHA256 = "e1e368b83a8c664935143709b40f4ad2bf7c6217003492b5d64c2562a48f666b"
CALLEE_SHA256 = "da733fdd7e7575a433875b1f7179c538834892d555e8d02db320a269353980b0"
RANGE_SHA256 = "4a4cca6c22bcdfb84d88f4fc67200da6ab7e629759e0006593d75459f04c056d"

OLD_ENTITY = (
    "TEXT_RESIDUAL:" + SPECIMEN_SHA256 + ":0x00535EDD-0x00535EF0"
)
OLD_CONTRACT = "C-46870cdfcfe2780a"
RESIDUAL_QUESTION = "Q-b27b396c572d0aa2"
CANDIDATE_ENTITY = (
    "CODE_CANDIDATE:" + SPECIMEN_SHA256 + ":VA=0X00535EE0"
)
CANDIDATE_QUESTION = "Q-0de52a13680b6c1d"
NEW_ENTITY = (
    "CODE:" + SPECIMEN_SHA256
    + ":VA=0x00535ee0:RANGES=" + RANGE_SHA256
)
NEW_CONTRACT = "C-7c57eb48898953d7"
SUCCESSOR_QUESTION = "Q-bcd5a5ae82cbaff7"
PREFIX_ENTITY = (
    "TEXT_RESIDUAL:" + SPECIMEN_SHA256 + ":0x00535EDD-0x00535EE0"
)
PREFIX_CONTRACT = "C-bc690b03be084fa5"
SUFFIX_ENTITY = (
    "TEXT_RESIDUAL:" + SPECIMEN_SHA256 + ":0x00535EED-0x00535EF0"
)
SUFFIX_CONTRACT = "C-5a1d44f0a144194b"

INSTRUCTIONS = (
    (0x00535EE0, "8b 49 10", "MOV", "ECX, dword ptr [ECX + 0x10]"),
    (0x00535EE3, "6a 00", "PUSH", "0x0"),
    (0x00535EE5, "e8 86 da fb ff", "CALL", "0x004f3970"),
    (0x00535EEA, "c2 0c 00", "RET", "0xc"),
)

TWIN_INSTRUCTIONS = (
    (0x00535ED0, "8b 49 10", "MOV", "ECX, dword ptr [ECX + 0x10]"),
    (0x00535ED3, "6a 01", "PUSH", "0x1"),
    (0x00535ED5, "e8 96 da fb ff", "CALL", "0x004f3970"),
    (0x00535EDA, "c2 0c 00", "RET", "0xc"),
)

CALLEE_INSTRUCTIONS = (
    (0x004F3970, "8b 44 24 04", "MOV", "EAX, dword ptr [ESP + 0x4]"),
    (0x004F3974, "56", "PUSH", "ESI"),
    (0x004F3975, "8b f1", "MOV", "ESI, ECX"),
    (0x004F3977, "83 f8 01", "CMP", "EAX, 0x1"),
    (0x004F397A, "8a 46 2c", "MOV", "AL, byte ptr [ESI + 0x2c]"),
    (0x004F397D, "75 17", "JNZ", "0x004f3996"),
    (0x004F397F, "a8 20", "TEST", "AL, 0x20"),
    (0x004F3981, "75 26", "JNZ", "0x004f39a9"),
    (0x004F3983, "56", "PUSH", "ESI"),
    (0x004F3984, "b9 40 51 85 00", "MOV", "ECX, 0x855140"),
    (0x004F3989, "e8 f2 20 ff ff", "CALL", "0x004e5a80"),
    (0x004F398E, "80 4e 2c 20", "OR", "byte ptr [ESI + 0x2c], 0x20"),
    (0x004F3992, "5e", "POP", "ESI"),
    (0x004F3993, "c2 04 00", "RET", "0x4"),
    (0x004F3996, "a8 20", "TEST", "AL, 0x20"),
    (0x004F3998, "74 0f", "JZ", "0x004f39a9"),
    (0x004F399A, "56", "PUSH", "ESI"),
    (0x004F399B, "b9 40 51 85 00", "MOV", "ECX, 0x855140"),
    (0x004F39A0, "e8 2b 22 ff ff", "CALL", "0x004e5bd0"),
    (0x004F39A5, "80 66 2c df", "AND", "byte ptr [ESI + 0x2c], 0xdf"),
    (0x004F39A9, "5e", "POP", "ESI"),
    (0x004F39AA, "c2 04 00", "RET", "0x4"),
)

REQUESTED_ADDRESSES = (
    0x005309AB, 0x005309B7, 0x00530A30,
    0x0064D5A0, 0x0064D5D0, 0x0064F8DC,
    0x00535ED0,
    *range(RESIDUAL_START, RESIDUAL_END),
    0x00535EF0,
    0x004F3970, 0x004F3977, 0x004F397F, 0x004F3983,
    0x004F3989, 0x004F398E, 0x004F3996, 0x004F399A,
    0x004F39A0, 0x004F39A5, 0x004F39AA,
)

INPUTS: dict[str, tuple[int, str]] = {
    "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup": (2_506_752, SPECIMEN_SHA256),
    f"{PARENT_RELATIVE.as_posix()}/campaign.ready.json": (22_974, PARENT_READY_SHA256),
    f"{PARENT_RELATIVE.as_posix()}/campaign-functions.tsv": (5_131_253, "cfaf73803c360285ecedfda29e7a89c8119d05bbf2d047e124522dedc9256454"),
    f"{PARENT_RELATIVE.as_posix()}/campaign-residuals.tsv": (2_865_308, "6aaa5da3917079de3a172fb24b7de2b3ba99f1bc05ad40c4c427fcaa76d55ab6"),
    f"{PARENT_RELATIVE.as_posix()}/campaign-questions.tsv": (8_370_802, "1b0609bada6a4595b8420f15ec3bd4d5c743d79100fa8012bd26cb9be15b3a56"),
    f"{PARENT_RELATIVE.as_posix()}/campaign-contracts.tsv": (10_923_965, "f9a7674757ad85fc7ec8fa3d5dbff1b933b0f950b5b6c323ffe088d3a137752c"),
    PARENT_AUTHORITY_RELATIVE.as_posix(): (12_742, PARENT_AUTHORITY_SHA256),
    f"{CLOSURE_RELATIVE.as_posix()}/closure.ready.json": (48_533, CLOSURE_READY_SHA256),
    f"{CLOSURE_RELATIVE.as_posix()}/police-dispositions.tsv": (11_251, POLICE_SHA256),
    "local-lab/ghidra-from-trace-2026-07-28/script-native-table-144.tsv": (9_016, "42027af22e1d4a0611bf7286fd1ea0df17adf01f7bf54ad5a2196f8484f40d86"),
    "local-lab/re-ledger/coverage-ledger-2026-08-02-baseline7555-exact-v5-ready/ledger-native-handlers.tsv": (14_810, "4a4ad8ec134a03dbf3438137013c877361db2f4708189a2410a8fcc97baa5563"),
    "local-lab/scenario-primitives-2026-08-02/native_signatures.tsv": (7_043, "cb7608e18b76e35a9499e36ed8415314e9240a954a089516488cdf9a5d2986a6"),
    "local-lab/msl-logger-census-2026-08-03-v3-ready/native-summary.tsv": (16_144, "533afac4865fb724d7ac90753f1f8d8f158c1d7d36c379b7deeb1c9b5d6c26ec"),
    "references/Onslaught/thing.cpp": (19_657, "e930244e01fbad5fe7e15c2595ce595282fb4c982a469cf604e5b9e0de09727e"),
    "references/Onslaught/thing.h": (11_680, "cf0c15e24869d57ab354251f465aee6dc1780c6f7c557fec27d081d71a46e8fe"),
    "local-lab/ghidra-mission-native-setpos-live-promotion-20260809-v1/promotion/promotion.ready.json": (6_782, "e64be82f360203fd2864450c5b3bd2d0a46441b9120eb79c8c423c3fe1ca0340"),
    "local-lab/ghidra-mission-native-setpos-live-promotion-20260809-v1/backups/post-live/backup_manifest.json": (7_589, "df2c7ad5c2367801c6fa359ec4be7bcf65864306f87860f643f886d0517724bc"),
    "local-lab/ghidra-mission-native-setpos-live-promotion-20260809-v1/post-live-restore.ready.json": (6_007, "5a081e72c43c2152623a02319b16a75a79f2632546f63428192e123509fb75cf"),
    "local-lab/ghidra-mission-native-setpos-live-promotion-20260809-v1/runs/live-inventory/functions.tsv": (7_052_417, "f05259cda1c5d956098062220d6e3aada9bff4a61896a77c8fc153826691f9d0"),
    "local-lab/ghidra-mission-native-setpos-live-promotion-20260809-v1/runs/live-inventory/program.tsv": (1_267, "6907443d213f6632c778a1c0e48f2070d5b268136b55e0e5f5c187f74dcbcf8f"),
    "tools/ExportInstructionsAroundAddresses.java": (6_474, "a7eb34bb929a99a0ef247211ca109dc9ce39533d05cc607bf135595903e9ab7a"),
    "tools/ExportXrefsForAddresses.java": (4_164, "52fcf62439a65265107ea95bde1d0d2725e6a074fe3035689ce51ea3bdef7b14"),
    f"{EVIDENCE_RELATIVE.as_posix()}/addresses-byte-complete.txt": (525, "508c83eee27eb7f44098000759a4341c62d3fef65b25ec33026b926a75348051"),
    f"{EVIDENCE_RELATIVE.as_posix()}/ghidra-readonly-byte-complete/instructions.tsv": (220_537, "2225b37a9e83347fa0f46f45fefd4ade45be6ba021f87e51ed299ff5ebd5340d"),
    f"{EVIDENCE_RELATIVE.as_posix()}/ghidra-readonly-byte-complete/xrefs.tsv": (2_376, "05ee583ab5be4448d669b373050eb807230821045e43278d122e644e16cb1f9e"),
    f"{EVIDENCE_RELATIVE.as_posix()}/ghidra-readonly-byte-complete/headless.log": (5_597, "6c5f478d1f650d32cd72a4ba0a08ca9a51b803cb7aaa1c8dbd87baa0165565ff"),
}

FROZEN_SOURCE_INPUTS = {
    "references/Onslaught/thing.cpp",
    "references/Onslaught/thing.h",
    "tools/ExportInstructionsAroundAddresses.java",
    "tools/ExportXrefsForAddresses.java",
}


class ProofError(ValueError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise ProofError(message)


def repo_root() -> Path:
    configured = os.environ.get("BEA_REPO_ROOT")
    if configured:
        return require_plain_path(
            Path(os.path.abspath(configured)), "BEA_REPO_ROOT", file=False
        )
    return Path(__file__).resolve().parents[1]


def source_root() -> Path:
    return Path(__file__).resolve().parents[1]


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def require_plain_path(path: Path, label: str, *, file: bool | None = None) -> Path:
    raw = Path(os.path.abspath(path))
    current = Path(raw.anchor)
    for part in raw.parts[1:]:
        current /= part
        try:
            info = current.lstat()
        except OSError as exc:
            raise ProofError(f"{label} cannot be inspected: {exc}") from exc
        attributes = getattr(info, "st_file_attributes", 0)
        require(
            not stat.S_ISLNK(info.st_mode)
            and not (attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT),
            f"{label} contains a link or reparse point: {current}",
        )
    resolved = raw.resolve(strict=True)
    require(resolved == raw, f"{label} aliases another path")
    info = raw.lstat()
    if file is True:
        require(stat.S_ISREG(info.st_mode), f"{label} is not a file")
        require(info.st_nlink == 1, f"{label} has multiple hard links")
    elif file is False:
        require(stat.S_ISDIR(info.st_mode), f"{label} is not a directory")
    return raw


def logical_stamp(path: Path, logical_path: str) -> dict[str, Any]:
    plain = require_plain_path(path, logical_path, file=True)
    return {
        "path": logical_path,
        "bytes": plain.stat().st_size,
        "sha256": sha256_file(plain),
    }


def restored_project_root(root: Path, candidate: Path | None) -> Path:
    require(
        candidate is not None,
        f"historical Ghidra project is not selected; {COLD_RESTORE_GUIDANCE}",
    )
    selected = candidate if candidate.is_absolute() else root / candidate
    project = require_plain_path(
        selected, "restored historical Ghidra project", file=False
    )
    forbidden = {
        (root / ACTIVE_MUTABLE_PROJECT_RELATIVE).resolve(),
        (root / TRACKED_CHECKPOINT_RELATIVE).resolve(),
    }
    require(
        project not in forbidden,
        "historical proof must not consume the active mutable project or tracked checkpoint",
    )
    try:
        project.relative_to(COLD_PACKAGE_PARENT.resolve())
    except ValueError:
        pass
    else:
        raise ProofError(
            "do not open or validate a project in place inside the sealed recovery package; "
            "restore it to a separate directory first"
        )
    return project


def read_json(path: Path) -> dict[str, Any]:
    def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            require(key not in result, f"duplicate JSON key in {path}: {key}")
            result[key] = value
        return result

    try:
        value = json.loads(
            path.read_text(encoding="utf-8"), object_pairs_hook=strict_object
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise ProofError(f"cannot parse {path}: {exc}") from exc
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def read_tsv(path: Path, *, campaign: bool = False) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        first = stream.readline()
        if campaign:
            require(first.rstrip("\r\n") == "# bea.re.campaign.v5", f"campaign marker differs: {path}")
            source = stream
        else:
            while first.startswith("# "):
                first = stream.readline()
            require(first, f"TSV header is missing: {path}")
            source = [first, *stream]
        rows = list(csv.DictReader(source, delimiter="\t"))
    require(rows, f"TSV has no rows: {path}")
    return rows


def exact_inputs(root: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for relative, expected in sorted(INPUTS.items()):
        base = source_root() if relative in FROZEN_SOURCE_INPUTS else root
        actual = logical_stamp(base / relative, relative)
        require((actual["bytes"], actual["sha256"]) == expected, f"input identity differs: {relative}")
        result[relative] = actual
    return result


def pe_layout(image: bytes) -> tuple[int, list[tuple[int, int, int, int]]]:
    pe = struct.unpack_from("<I", image, 0x3C)[0]
    require(image[pe:pe + 4] == b"PE\0\0", "pristine PE signature differs")
    sections = struct.unpack_from("<H", image, pe + 6)[0]
    optional_size = struct.unpack_from("<H", image, pe + 20)[0]
    optional = pe + 24
    image_base = struct.unpack_from("<I", image, optional + 28)[0]
    table = optional + optional_size
    result = []
    for index in range(sections):
        row = table + index * 40
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from("<IIII", image, row + 8)
        result.append((virtual_address, virtual_size, raw_size, raw_pointer))
    return image_base, result


def pe_offset(image: bytes, va: int) -> int:
    image_base, sections = pe_layout(image)
    rva = va - image_base
    for virtual_address, virtual_size, raw_size, raw_pointer in sections:
        if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
            return raw_pointer + rva - virtual_address
    raise ProofError(f"VA is not mapped: 0x{va:08x}")


def va_bytes(image: bytes, start: int, end: int) -> bytes:
    offset = pe_offset(image, start)
    value = image[offset:offset + end - start]
    require(len(value) == end - start, f"short PE span at 0x{start:08x}")
    return value


def instruction_bytes(rows: tuple[tuple[int, str, str, str], ...]) -> bytes:
    return b"".join(bytes.fromhex(row[1]) for row in rows)


def validate_pristine(
    image: bytes,
    *,
    require_specimen: bool = True,
    function_start: int = FUNCTION_START,
    function_end: int = FUNCTION_END,
) -> dict[str, Any]:
    if require_specimen:
        require(
            len(image) == 2_506_752 and sha256_bytes(image) == SPECIMEN_SHA256,
            "pristine specimen differs",
        )
    require(
        (function_start, function_end) == (FUNCTION_START, FUNCTION_END),
        "proposed function boundary differs",
    )
    spans = {
        "prefixPadding": (RESIDUAL_START, function_start, 3, PADDING_SHA256),
        "functionBody": (function_start, function_end, 13, BODY_SHA256),
        "suffixPadding": (function_end, RESIDUAL_END, 3, PADDING_SHA256),
        "oldResidual": (RESIDUAL_START, RESIDUAL_END, 19, RESIDUAL_SHA256),
        "symmetricSetObjective": (TWIN_START, TWIN_END, 13, TWIN_SHA256),
        "CThingSetObjective": (CALLEE_START, CALLEE_END, 61, CALLEE_SHA256),
    }
    raw: dict[str, bytes] = {}
    for name, (start, end, size, digest) in spans.items():
        value = va_bytes(image, start, end)
        require(len(value) == size and sha256_bytes(value) == digest, f"{name} bytes differ")
        raw[name] = value
    require(raw["prefixPadding"] == b"\x90" * 3, "prefix is not exact NOP padding")
    require(raw["suffixPadding"] == b"\x90" * 3, "suffix is not exact NOP padding")
    require(instruction_bytes(INSTRUCTIONS) == raw["functionBody"], "instruction framing does not cover exact body")
    require(instruction_bytes(TWIN_INSTRUCTIONS) == raw["symmetricSetObjective"], "SetObjective twin framing differs")
    require(instruction_bytes(CALLEE_INSTRUCTIONS) == raw["CThingSetObjective"], "callee framing differs")
    cursor = FUNCTION_START
    for address, encoded, _mnemonic, _operands in INSTRUCTIONS:
        require(address == cursor, f"instruction sequence has a gap at 0x{cursor:08x}")
        cursor += len(bytes.fromhex(encoded))
    require(cursor == FUNCTION_END, "instruction sequence does not end at proposed boundary")
    require(
        va_bytes(image, REGISTRY_HANDLER_LOAD, REGISTRY_HANDLER_LOAD + 5)
        == bytes.fromhex("bf e0 5e 53 00"),
        "registry handler load differs",
    )
    require(
        va_bytes(image, REGISTRY_HANDLER_STORE, REGISTRY_HANDLER_STORE + 6)
        == bytes.fromhex("89 3d d0 d5 64 00"),
        "registry handler-slot store differs",
    )
    require(
        va_bytes(image, REGISTRY_NAME_STORE, REGISTRY_NAME_STORE + 10)
        == bytes.fromhex("c7 05 a0 d5 64 00 dc f8 64 00"),
        "registry record-name store differs",
    )
    require(
        va_bytes(image, NAME_ADDRESS, NAME_ADDRESS + 15) == b"UnsetObjective\0",
        "shipped UnsetObjective string differs",
    )
    require(image.count(struct.pack("<I", FUNCTION_START)) == 1, "handler immediate is not unique in pristine bytes")
    return {
        "oldResidual": {
            "startVa": "0x00535edd", "endVa": "0x00535ef0",
            "bytes": 19, "sha256": RESIDUAL_SHA256,
        },
        "partition": [
            {"kind": "NOP_PADDING", "startVa": "0x00535edd", "endVa": "0x00535ee0", "bytes": 3, "sha256": PADDING_SHA256},
            {"kind": "MISSION_NATIVE_FUNCTION", "startVa": "0x00535ee0", "endVa": "0x00535eed", "bytes": 13, "sha256": BODY_SHA256, "bodyRangeSetSha256": RANGE_SHA256},
            {"kind": "NOP_PADDING", "startVa": "0x00535eed", "endVa": "0x00535ef0", "bytes": 3, "sha256": PADDING_SHA256},
        ],
        "instructionCount": len(INSTRUCTIONS),
        "calleeCleanupBytes": 12,
        "registryInitializer": {
            "handlerLoadVa": "0x005309ab",
            "handlerStoreVa": "0x005309b5",
            "recordNameStoreVa": "0x00530a30",
            "recordVa": "0x0064d5a0",
            "slotVa": "0x0064d5d0",
            "handlerVa": "0x00535ee0",
        },
        "shippedName": {"address": "0x0064f8dc", "value": "UnsetObjective"},
        "symmetricTrueWrapper": {
            "entryVa": "0x00535ed0",
            "bodySha256": TWIN_SHA256,
            "literal": 1,
            "calleeVa": "0x004f3970",
        },
        "callee": {
            "entryVa": "0x004f3970",
            "bodyBytes": 61,
            "bodySha256": CALLEE_SHA256,
            "flagOffset": "0x2c",
            "flagMask": "0x20",
            "falsePath": "IF_SET_CALL_0x004E5BD0_WITH_ECX_0x00855140_AND_PUSH_THIS_THEN_CLEAR_BIT",
            "alreadyFalsePath": "NO_CALL_NO_WRITE",
        },
    }


def one(rows: list[dict[str, str]], key: str, value: str, label: str) -> dict[str, str]:
    matches = [row for row in rows if row.get(key) == value]
    require(len(matches) == 1, f"{label} census differs")
    return matches[0]


def validate_parent(root: Path) -> dict[str, Any]:
    ready = read_json(root / PARENT_RELATIVE / "campaign.ready.json")
    require(ready.get("generation") == 18, "parent generation differs")
    require(ready.get("counts") == PARENT_COUNTS, "parent counts differ")
    require(ready.get("reducer", {}).get("id") == PARENT_REDUCER_ID, "parent reducer differs")
    residual = one(
        read_tsv(root / PARENT_RELATIVE / "campaign-residuals.tsv", campaign=True),
        "entityKey", OLD_ENTITY, "parent residual",
    )
    contract = one(
        read_tsv(root / PARENT_RELATIVE / "campaign-contracts.tsv", campaign=True),
        "contractId", OLD_CONTRACT, "parent residual contract",
    )
    questions = read_tsv(root / PARENT_RELATIVE / "campaign-questions.tsv", campaign=True)
    residual_question = one(questions, "questionId", RESIDUAL_QUESTION, "parent residual question")
    candidate_question = one(questions, "questionId", CANDIDATE_QUESTION, "parent native-boundary question")
    require(
        residual.get("startVa") == "0x00535edd"
        and residual.get("endVa") == "0x00535ef0"
        and residual.get("bytes") == "19"
        and residual.get("classification") == "AMBIGUOUS"
        and residual.get("classificationVerdict") == "UNSCORED"
        and residual.get("terminalState") == "OPEN_CLASSIFICATION"
        and residual.get("questionIds") == RESIDUAL_QUESTION,
        "parent residual is not exact open frontier",
    )
    require(
        contract.get("entityKey") == OLD_ENTITY
        and contract.get("contractState") == "OPEN_CLASSIFICATION"
        and contract.get("semanticGrade") == "C0_OPAQUE"
        and contract.get("questionIds") == RESIDUAL_QUESTION,
        "parent residual contract differs",
    )
    require(
        residual_question.get("entityKey") == OLD_ENTITY
        and residual_question.get("state") == "OPEN"
        and residual_question.get("attemptCount") == "0",
        "parent residual question differs",
    )
    require(
        candidate_question.get("entityKey") == CANDIDATE_ENTITY
        and candidate_question.get("questionType") == "NATIVE_BOUNDARY"
        and candidate_question.get("state") == "OPEN"
        and candidate_question.get("source") == "native:30",
        "parent native-boundary question differs",
    )
    functions = read_tsv(root / PARENT_RELATIVE / "campaign-functions.tsv", campaign=True)
    require(not any(row.get("entryVa") == "0x00535ee0" for row in functions), "parent already contains UnsetObjective function")
    previous = one(functions, "entryVa", "0x00535ed0", "parent SetObjective twin")
    following = one(functions, "entryVa", "0x00535ef0", "parent following function")
    require(
        previous.get("bodyRangesRva") == "0x135ed0-0x135edd"
        and previous.get("currentName") == "SetObjective",
        "parent SetObjective twin differs",
    )
    require(
        following.get("bodyRangesRva") == "0x135ef0-0x135f70"
        and following.get("currentName") == "IsObjective",
        "parent following function differs",
    )
    return {
        "generation": 18,
        "readySha256": PARENT_READY_SHA256,
        "reducerId": PARENT_REDUCER_ID,
        "authorityReceiptSha256": PARENT_AUTHORITY_SHA256,
        "oldEntityKey": OLD_ENTITY,
        "oldContractId": OLD_CONTRACT,
        "questions": [RESIDUAL_QUESTION, CANDIDATE_QUESTION],
    }


def validate_police_rows(rows: list[dict[str, str]], closure: dict[str, Any]) -> dict[str, Any]:
    require(
        closure.get("schema") == "bea.re.candidate-chain-post-loss-closure.v1"
        and closure.get("verdict") == "READY"
        and closure.get("claim") == "FIELD_SCOPED_RESEAL_PLAN_FROM_CANONICAL_10R",
        "claim-closure receipt differs",
    )
    require(
        closure.get("outputs", {}).get("police-dispositions.tsv")
        == {"path": "police-dispositions.tsv", "bytes": 11_251, "sha256": POLICE_SHA256},
        "claim-closure police output stamp differs",
    )
    row = one(rows, "entityKey", OLD_ENTITY, "police disposition")
    expected = {
        "entityKey": OLD_ENTITY,
        "startVa": "0x00535edd",
        "endVa": "0x00535ef0",
        "policeReason": "OFFSET_ENVELOPE_vs_deeper_open",
        "disposition": "PRESERVE_EXACT_10R_OPEN_FRONTIER",
        "candidateQuestionId": "Q-8c6381dd12b719",
        "candidateQuestion": "Reopened after police: OFFSET_ENVELOPE_vs_deeper_open at 0x00535edd",
        "candidateRecommendedInstrument": "residual-split|inbound|strict-envelope",
        "candidateCheapestFalsifier": (
            "Police reopen: Gen16 OFFSET_ENVELOPE whole-span terminal disagreed with deeper "
            "wholeSpanTerminal=false / openBytes; re-check with full-cover+control-end envelope "
            "gate; residual-split or inbound before re-terminal"
        ),
        "candidateState": "OPEN",
    }
    require(row == expected, "police disposition content differs")
    return {
        "reason": row["policeReason"],
        "requiredInstrument": row["candidateRecommendedInstrument"],
        "gateSatisfiedBy": [
            "EXACT_3_13_3_FULL_COVER_PARTITION",
            "UNIQUE_REGISTRY_INBOUND_AT_FUNCTION_ENTRY",
            "TERMINATING_RET_0x0C_AND_EXACT_FOLLOWING_BOUNDARY",
        ],
    }


def validate_police(root: Path) -> dict[str, Any]:
    return validate_police_rows(
        read_tsv(root / CLOSURE_RELATIVE / "police-dispositions.tsv"),
        read_json(root / CLOSURE_RELATIVE / "closure.ready.json"),
    )


def validate_registry(root: Path) -> dict[str, Any]:
    table = read_tsv(root / "local-lab/ghidra-from-trace-2026-07-28/script-native-table-144.tsv")
    row = one(table, "index", "30", "shipped native registry row")
    require(
        row == {
            "index": "30", "record": "0x0064d5a0", "handler": "0x00535ee0",
            "shippedName": "UnsetObjective", "ghidraName": "", "status": "NO_FUNCTION",
        },
        "shipped native registry row differs",
    )
    ledger = read_tsv(
        root / "local-lab/re-ledger/coverage-ledger-2026-08-02-baseline7555-exact-v5-ready/ledger-native-handlers.tsv"
    )
    state = one(ledger, "index", "30", "native boundary ledger row")
    require(
        state.get("handlerVa") == "0x00535ee0"
        and state.get("shippedName") == "UnsetObjective"
        and state.get("registryStatus") == "NO_FUNCTION"
        and state.get("functionPresent") == "False"
        and state.get("terminalState") == "BOUNDARY_MISSING"
        and state.get("needsBoundaryReview") == "True",
        "native boundary ledger row differs",
    )
    signatures = read_tsv(root / "local-lab/scenario-primitives-2026-08-02/native_signatures.tsv")
    signature = one(signatures, "index", "30", "native signature row")
    require(
        signature.get("handler") == "0x00535ee0"
        and signature.get("name") == "UnsetObjective"
        and signature.get("argc") == "0"
        and signature.get("returns") == "0"
        and signature.get("returnType") == "void",
        "native signature row differs",
    )
    summary = one(
        read_tsv(root / "local-lab/msl-logger-census-2026-08-03-v3-ready/native-summary.tsv"),
        "nativeIndex", "30", "shipped call census row",
    )
    require(
        summary.get("nativeName") == "UnsetObjective"
        and summary.get("handlerVa") == "0x00535ee0"
        and summary.get("sourceCallCount") == "250"
        and summary.get("sourceFileCount") == "217"
        and summary.get("sourceLevelCount") == "59"
        and summary.get("compiledCallCount") == "264"
        and summary.get("compiledArchiveCount") == "57"
        and summary.get("coverageObserved") == "False",
        "shipped call census differs",
    )
    return {
        "index": 30,
        "recordVa": "0x0064d5a0",
        "slotVa": "0x0064d5d0",
        "handlerVa": "0x00535ee0",
        "shippedName": "UnsetObjective",
        "priorState": "BOUNDARY_MISSING",
        "signature": "void UnsetObjective()",
        "shippedUsage": {"sourceCalls": 250, "sourceFiles": 217, "sourceLevels": 59, "compiledCalls": 264, "compiledArchives": 57},
        "runtimeCoverageObserved": False,
    }


def validate_source(root: Path) -> dict[str, Any]:
    cpp = (source_root() / "references/Onslaught/thing.cpp").read_text(encoding="utf-8")
    header = (source_root() / "references/Onslaught/thing.h").read_text(encoding="utf-8")
    require("void\tCThing::SetObjective(BOOL val)" in cpp, "source SetObjective definition differs")
    require("WORLD.GetObjectiveThingNB().Add(this)" in cpp, "source objective add path differs")
    require("WORLD.GetObjectiveThingNB().Remove(this)" in cpp, "source objective remove path differs")
    require("mFlags &= ~TF_MARKED_OBJECTIVE" in cpp, "source objective clear differs")
    require("TF_MARKED_OBJECTIVE = 32" in header, "source objective mask differs")
    require("void\t\t\tSetObjective(BOOL val)" in header, "source declaration differs")
    return {
        "role": "GPL_ARCHITECTURE_AND_INTENT_CORROBORATION_NOT_RETAIL_IDENTITY",
        "method": "CThing::SetObjective(BOOL)",
        "falsePath": "REMOVE_FROM_OBJECTIVE_NOTICEBOARD_AND_CLEAR_TF_MARKED_OBJECTIVE_IF_SET",
        "alreadyFalsePath": "NO_OP",
    }


def validate_listing_rows(
    instructions: list[dict[str, str]],
    xrefs: list[dict[str, str]],
) -> dict[str, Any]:
    central_rows = [
        row for row in instructions if row.get("role") in {"TARGET", "MISSING"}
    ]
    expected_targets = {f"0x{address:08x}" for address in REQUESTED_ADDRESSES}
    require(
        {row.get("target_addr") for row in central_rows} == expected_targets
        and len(central_rows) == len(expected_targets),
        "Ghidra central-row census differs",
    )
    target_rows = {
        row["target_addr"]: row for row in central_rows if row.get("role") == "TARGET"
    }
    expected_containing: dict[int, tuple[int, str, str, str]] = {}
    for address, encoded, mnemonic, operands in INSTRUCTIONS:
        for byte_address in range(address, address + len(bytes.fromhex(encoded))):
            expected_containing[byte_address] = (address, encoded, mnemonic, operands)
    for byte_address in range(RESIDUAL_START, RESIDUAL_END):
        address_text = f"0x{byte_address:08x}"
        rows = [
            row for row in instructions
            if row.get("target_addr") == address_text
            and row.get("role") in {"TARGET", "MISSING"}
        ]
        require(len(rows) == 1, f"Ghidra residual byte census differs at {address_text}")
        row = rows[0]
        expected = expected_containing.get(byte_address)
        if expected is None:
            require(
                row.get("role") == "MISSING"
                and row.get("instruction_addr") == "<none>"
                and row.get("function_entry") == "<none>",
                f"Ghidra padding byte is defined at {address_text}",
            )
        else:
            instruction_address, encoded, mnemonic, operands = expected
            require(
                row.get("role") == "TARGET"
                and row.get("instruction_addr") == f"0x{instruction_address:08x}"
                and row.get("function_entry") == "<none>"
                and row.get("function_name") == "<no_function>"
                and (row.get("mnemonic"), row.get("operands"), row.get("bytes"))
                == (mnemonic, operands, encoded),
                f"Ghidra body byte differs at {address_text}",
            )
    for address, encoded, mnemonic, operands in INSTRUCTIONS:
        row = target_rows.get(f"0x{address:08x}")
        require(row is not None, f"Ghidra instruction missing at 0x{address:08x}")
        require(
            row.get("instruction_addr") == f"0x{address:08x}"
            and row.get("function_entry") == "<none>"
            and row.get("function_name") == "<no_function>"
            and (row.get("mnemonic"), row.get("operands"), row.get("bytes"))
            == (mnemonic, operands, encoded),
            f"Ghidra instruction differs at 0x{address:08x}",
        )
    for address, encoded, mnemonic, operands in TWIN_INSTRUCTIONS:
        row = next(
            (item for item in instructions if item.get("instruction_addr") == f"0x{address:08x}"),
            None,
        )
        require(
            row is not None
            and row.get("function_entry") == "0x00535ed0"
            and row.get("function_name") == "FUN_00535ed0"
            and (row.get("mnemonic"), row.get("operands"), row.get("bytes"))
            == (mnemonic, operands, encoded),
            f"Ghidra SetObjective twin differs at 0x{address:08x}",
        )
    for address, encoded, mnemonic, operands in CALLEE_INSTRUCTIONS:
        row = next(
            (item for item in instructions if item.get("instruction_addr") == f"0x{address:08x}"),
            None,
        )
        require(
            row is not None
            and row.get("function_entry") == "0x004f3970"
            and row.get("function_name") == "CThing__SetObjective"
            and (row.get("mnemonic"), row.get("operands"), row.get("bytes"))
            == (mnemonic, operands, encoded),
            f"Ghidra CThing::SetObjective differs at 0x{address:08x}",
        )
    expected_registry = {
        "0x005309ab": ("0x005309ab", "MOV", "EDI, 0x535ee0", "bf e0 5e 53 00"),
        "0x005309b7": ("0x005309b5", "MOV", "dword ptr [0x0064d5d0], EDI", "89 3d d0 d5 64 00"),
        "0x00530a30": ("0x00530a30", "MOV", "dword ptr [0x0064d5a0], 0x64f8dc", "c7 05 a0 d5 64 00 dc f8 64 00"),
    }
    for target, expected in expected_registry.items():
        row = target_rows.get(target)
        require(
            row is not None
            and row.get("function_name") == "ScriptCommandRegistry__InitBuiltins"
            and (row.get("instruction_addr"), row.get("mnemonic"), row.get("operands"), row.get("bytes")) == expected,
            f"Ghidra registry row differs: {target}",
        )
    missing = {
        row.get("target_addr")
        for row in instructions
        if row.get("role") == "MISSING" and row.get("instruction_addr") == "<none>"
    }
    require(
        {"0x00535edd", "0x00535eed"}.issubset(missing),
        "Ghidra padding is unexpectedly defined as code",
    )
    actual_refs = {
        (row.get("target_addr"), row.get("from_addr"), row.get("from_function"), row.get("ref_type"))
        for row in xrefs
        if row.get("from_addr") != "<none>"
    }
    required_refs = {
        ("0064d5a0", "00530a30", "ScriptCommandRegistry__InitBuiltins", "WRITE"),
        ("0064d5d0", "005309b5", "ScriptCommandRegistry__InitBuiltins", "WRITE"),
        ("0064f8dc", "00530a30", "ScriptCommandRegistry__InitBuiltins", "DATA"),
        ("00535ee0", "005309ab", "ScriptCommandRegistry__InitBuiltins", "DATA"),
        ("004f3970", "00535ed5", "FUN_00535ed0", "UNCONDITIONAL_CALL"),
        ("004f3970", "00535ee5", "<no_function>", "UNCONDITIONAL_CALL"),
        ("004f3996", "004f397d", "CThing__SetObjective", "CONDITIONAL_JUMP"),
    }
    require(required_refs.issubset(actual_refs), "Ghidra required xref set differs")
    residual_xrefs = [
        row for row in xrefs
        if RESIDUAL_START <= int(row.get("target_addr", "0"), 16) < RESIDUAL_END
    ]
    expected_residual_xrefs = [
        {
            "target_addr": f"{address:08x}",
            "target_name": "<no_function>",
            "from_addr": "005309ab" if address == FUNCTION_START else "<none>",
            "from_function_addr": "0052ff30" if address == FUNCTION_START else "<none>",
            "from_function": "ScriptCommandRegistry__InitBuiltins" if address == FUNCTION_START else "<none>",
            "ref_type": "DATA" if address == FUNCTION_START else "<none>",
        }
        for address in range(RESIDUAL_START, RESIDUAL_END)
    ]
    require(
        residual_xrefs == expected_residual_xrefs,
        "Ghidra residual xref set differs",
    )
    return {
        "listingDecodedInstructions": len(INSTRUCTIONS),
        "calleeDecodedInstructions": len(CALLEE_INSTRUCTIONS),
        "proposedBodyCurrentlyHasFunction": False,
        "residualByteAddressesChecked": RESIDUAL_END - RESIDUAL_START,
        "interiorInboundReferences": 0,
        "entryInboundReference": {
            "fromVa": "0x005309ab",
            "fromFunction": "ScriptCommandRegistry__InitBuiltins",
            "type": "DATA",
        },
    }


def validate_project_tree(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    project = require_plain_path(root, "Ghidra POST backup root", file=False)
    expected_rows = manifest.get("destination", {}).get("files")
    require(isinstance(expected_rows, list) and len(expected_rows) == 19, "Ghidra POST backup manifest files differ")
    expected = {row["relative_path"]: (row["size"], row["sha256"]) for row in expected_rows}
    actual_files = {
        path.relative_to(project).as_posix(): path
        for path in project.rglob("*")
        if path.is_file() and path != project / "backup_manifest.json"
    }
    require(set(actual_files) == set(expected), "Ghidra POST backup file set differs")
    for relative, path in actual_files.items():
        plain = require_plain_path(path, f"Ghidra POST backup file {relative}", file=True)
        require((plain.stat().st_size, sha256_file(plain)) == expected[relative], f"Ghidra POST backup file differs: {relative}")
    return {
        "fileCount": 19,
        "totalBytes": sum(size for size, _digest in expected.values()),
        "manifestSha256": "df2c7ad5c2367801c6fa359ec4be7bcf65864306f87860f643f886d0517724bc",
    }


def validate_ghidra(root: Path, ghidra_project_root: Path | None) -> dict[str, Any]:
    base = root / "local-lab/ghidra-mission-native-setpos-live-promotion-20260809-v1"
    promotion = read_json(base / "promotion/promotion.ready.json")
    require(
        promotion.get("verdict") == "READY"
        and promotion.get("phase") == "LIVE_PROMOTED"
        and promotion.get("result", {}).get("functionsAdded") == 1
        and promotion.get("result", {}).get("functionEntry") == "0x00536c70"
        and promotion.get("live", {}).get("postInventory", {}).get("functions", {}).get("sha256")
        == "f05259cda1c5d956098062220d6e3aada9bff4a61896a77c8fc153826691f9d0",
        "latest live Ghidra authority differs",
    )
    backup = read_json(base / "backups/post-live/backup_manifest.json")
    require(
        backup.get("sourceStable") is True
        and backup.get("copyComparison", {}).get("matches") is True
        and backup.get("source") == backup.get("destination")
        and backup.get("source", {}).get("fileCount") == 19,
        "latest Ghidra POST backup is not exact and recoverable",
    )
    project = validate_project_tree(
        restored_project_root(root, ghidra_project_root), backup
    )
    restore = read_json(base / "post-live-restore.ready.json")
    require(
        restore.get("sourceStable") is True
        and restore.get("copyComparison", {}).get("matches") is True
        and restore.get("probeCopyDisposition") == "RETAINED_AT_VERIFICATION"
        and restore.get("readonlyOpen", {}).get("opened") is True
        and restore.get("readonlyOpen", {}).get("contentStable") is True
        and restore.get("readonlyOpen", {}).get("postOpenComparison", {}).get("matches") is True,
        "latest Ghidra POST restore drill differs",
    )
    functions = read_tsv(base / "runs/live-inventory/functions.tsv")
    require(not any(row.get("address") == "0x00535ee0" for row in functions), "UnsetObjective is already a live function")
    previous = one(functions, "address", "0x00535ed0", "live SetObjective twin")
    following = one(functions, "address", "0x00535ef0", "live following function")
    callee = one(functions, "address", "0x004f3970", "live CThing::SetObjective")
    require(previous.get("bodyMax") == "0x00535edc" and previous.get("bodyBytes") == "13", "live SetObjective boundary differs")
    require(following.get("bodyMin") == "0x00535ef0", "live following boundary differs")
    require(callee.get("name") == "CThing__SetObjective" and callee.get("bodyBytes") == "61", "live callee identity differs")
    instructions = read_tsv(root / EVIDENCE_RELATIVE / "ghidra-readonly-byte-complete/instructions.tsv")
    xrefs = read_tsv(root / EVIDENCE_RELATIVE / "ghidra-readonly-byte-complete/xrefs.tsv")
    listing = validate_listing_rows(instructions, xrefs)
    log = (root / EVIDENCE_RELATIVE / "ghidra-readonly-byte-complete/headless.log").read_text(encoding="utf-8")
    require("Processing read-only project file: /BEA.exe" in log, "Ghidra export was not read-only")
    require("backups\\post-live\\BEA" in log, "Ghidra export source project differs")
    require("ExportInstructionsAroundAddresses.java> targets=38 missing=9" in log, "Ghidra instruction export marker differs")
    require("ExportXrefsForAddresses.java> Wrote 39 rows" in log, "Ghidra xref export marker differs")
    require("SCRIPT ERROR" not in log and "ERROR REPORT" not in log, "Ghidra export reports an error")
    return {
        "sourceProject": "SETPOS_LIVE_POST_BACKUP_READ_ONLY",
        "project": project,
        "functionCount": 8125,
        **listing,
        "neighbors": [
            {"entryVa": "0x00535ed0", "name": previous["name"], "bodyMax": previous["bodyMax"]},
            {"entryVa": "0x00535ef0", "name": following["name"], "bodyMin": following["bodyMin"]},
        ],
    }


def derive(root: Path, ghidra_project_root: Path | None = None) -> dict[str, Any]:
    require((root / EVIDENCE_RELATIVE).is_dir(), "UnsetObjective evidence root is missing")
    inputs = exact_inputs(root)
    image = (root / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup").read_bytes()
    return {
        "schema": SCHEMA,
        "verdict": "PASS",
        "claim": CLAIM,
        "specimen": {"sha256": SPECIMEN_SHA256, "role": "STATIC_BYTE_AUTHORITY_UNCHANGED"},
        "parent": validate_parent(root),
        "policeDisposition": validate_police(root),
        "registry": validate_registry(root),
        "staticProof": validate_pristine(image),
        "sourceCorroboration": validate_source(root),
        "ghidra": validate_ghidra(root, ghidra_project_root),
        "adjudication": {
            "oldEntityKey": OLD_ENTITY,
            "oldContractId": OLD_CONTRACT,
            "newFunctionEntityKey": NEW_ENTITY,
            "newFunctionContractId": NEW_CONTRACT,
            "newPaddingEntities": [PREFIX_ENTITY, SUFFIX_ENTITY],
            "newPaddingContractIds": [PREFIX_CONTRACT, SUFFIX_CONTRACT],
            "questionsAddressed": [RESIDUAL_QUESTION, CANDIDATE_QUESTION],
            "successorQuestionId": SUCCESSOR_QUESTION,
            "successorQuestionType": "FUNCTION_CONTRACT",
            "newName": "IScript__UnsetObjective",
            "nativeShippedName": "UnsetObjective",
            "functionBoundaryVerdict": "SURVIVED",
            "residualPartitionVerdict": "SURVIVED",
            "semanticGradeCeiling": "C1_STATIC",
            "semanticPromotionApplied": False,
        },
        "boundedContract": {
            "callingConvention": "__thiscall",
            "calleeCleanupBytes": 12,
            "opaqueVmStackSlots": 3,
            "opaqueVmStackSlotsRead": 0,
            "receiver": "DEREFERENCE_THIS_PLUS_0x10_TO_CTHING",
            "literalArgument": False,
            "callee": "CThing__SetObjective@0x004f3970",
            "falsePath": "IF_FLAG_0x20_SET_CALL_OPAQUE_0x004E5BD0_WITH_ECX_0x00855140_AND_PUSH_CTHING_THEN_CLEAR_FLAG",
            "alreadyFalsePath": "NO_CALL_NO_WRITE",
            "returns": "NO_DEFINED_EAX_RETURN_CLAIM",
            "writes": "CThing_PLUS_0x2C_FLAG_CLEAR_ON_TRANSITION;_0x004E5BD0_EFFECTS_UNCLAIMED",
        },
        "limitations": [
            "The shipped registry and unique initializer reference prove the UnsetObjective handler identity and entry; exact bytes and Ghidra listing prove the bounded static contract.",
            "The false wrapper path and CThing::SetObjective body prove a conditional call to opaque 0x004E5BD0 followed by bit 0x20 clearing, but no retail runtime invocation was observed.",
            "The pinned GPL source independently corroborates architecture and intent; pristine retail bytes remain the released-behavior authority.",
            "The GPL source identifies 0x004E5BD0's architectural role as objective-list removal, but this retail proof leaves that opaque callee's semantics unclaimed.",
            "The three callee-cleaned VM stack slots are not read by the wrapper; their semantic names remain unknown.",
            "No defined EAX return value, HUD presentation, invalid-object behavior, object lifetime behavior, or complete objective-system contract is claimed.",
            "No gameplay, TTD replay, executable write, or Ghidra mutation occurred while producing this proof.",
            "generatedAtUtc is informational publication metadata, not a behavioral or evidence-authority input.",
        ],
        "inputs": inputs,
        # This is the author of the sealed 2026-08-09 proof, not the evolving
        # compatibility verifier that is executing today.
        "author": dict(HISTORICAL_AUTHOR_STAMP),
    }


def validate_saved(
    saved: dict[str, Any], root: Path, ghidra_project_root: Path | None = None
) -> None:
    fresh = derive(root, ghidra_project_root)
    require(set(saved) == set(fresh) | {"generatedAtUtc"}, "proof top-level shape differs")
    generated = saved.get("generatedAtUtc")
    require(isinstance(generated, str) and generated.endswith("Z"), "proof timestamp is not UTC")
    parsed = datetime.fromisoformat(generated[:-1] + "+00:00")
    require(parsed.tzinfo is not None, "proof timestamp lacks timezone")
    stable = dict(saved)
    del stable["generatedAtUtc"]
    require(stable == fresh, "proof content differs from independently rederived evidence")


def expect_refused(label: str, expected: str, action: Callable[[], object]) -> None:
    try:
        action()
    except ProofError as exc:
        require(expected in str(exc), f"{label} refused for wrong reason: {exc}")
        return
    raise ProofError(f"counterexample accepted: {label}")


def mutated_image(image: bytes, va: int) -> bytes:
    value = bytearray(image)
    offset = pe_offset(image, va)
    value[offset] ^= 1
    return bytes(value)


def selftest(root: Path, ghidra_project_root: Path | None = None) -> None:
    derive(root, ghidra_project_root)
    image = (root / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup").read_bytes()
    attacks = (
        ("prefix byte", "prefixPadding bytes differ", lambda: validate_pristine(mutated_image(image, RESIDUAL_START), require_specimen=False)),
        ("body literal", "functionBody bytes differ", lambda: validate_pristine(mutated_image(image, 0x00535EE4), require_specimen=False)),
        ("suffix byte", "suffixPadding bytes differ", lambda: validate_pristine(mutated_image(image, FUNCTION_END), require_specimen=False)),
        ("handler immediate", "registry handler load differs", lambda: validate_pristine(mutated_image(image, REGISTRY_HANDLER_LOAD + 1), require_specimen=False)),
        ("name byte", "shipped UnsetObjective string differs", lambda: validate_pristine(mutated_image(image, NAME_ADDRESS), require_specimen=False)),
        ("callee false branch", "CThingSetObjective bytes differ", lambda: validate_pristine(mutated_image(image, 0x004F3996), require_specimen=False)),
        ("shifted entry", "proposed function boundary differs", lambda: validate_pristine(image, require_specimen=False, function_start=FUNCTION_START + 1)),
        ("shifted end", "proposed function boundary differs", lambda: validate_pristine(image, require_specimen=False, function_end=FUNCTION_END - 1)),
    )
    for label, expected, action in attacks:
        expect_refused(label, expected, action)
    instructions = read_tsv(root / EVIDENCE_RELATIVE / "ghidra-readonly-byte-complete/instructions.tsv")
    xrefs = read_tsv(root / EVIDENCE_RELATIVE / "ghidra-readonly-byte-complete/xrefs.tsv")
    function_alias = copy.deepcopy(instructions)
    targets = [
        row for row in function_alias
        if row.get("target_addr") == "0x00535ee0" and row.get("role") == "TARGET"
    ]
    require(len(targets) == 1, "selftest target census differs")
    target = targets[0]
    target["function_entry"] = "0x00535ee0"
    target["function_name"] = "FORGED"
    expect_refused(
        "pre-existing function laundering",
        "Ghidra body byte differs at 0x00535ee0",
        lambda: validate_listing_rows(function_alias, xrefs),
    )
    duplicate_target = copy.deepcopy(instructions)
    forged_target = dict(target)
    forged_target["function_entry"] = "0x00535ee0"
    forged_target["function_name"] = "FORGED"
    duplicate_target.insert(0, forged_target)
    expect_refused(
        "duplicate central-row laundering",
        "Ghidra central-row census differs",
        lambda: validate_listing_rows(duplicate_target, xrefs),
    )
    duplicate_entry_ref = copy.deepcopy(xrefs)
    duplicate_entry_ref.append({
        "target_addr": "00535ee0",
        "target_name": "<no_function>",
        "from_addr": "00534000",
        "from_function_addr": "00534000",
        "from_function": "ATTACKER",
        "ref_type": "DATA",
    })
    expect_refused(
        "second entry inbound reference",
        "Ghidra residual xref set differs",
        lambda: validate_listing_rows(instructions, duplicate_entry_ref),
    )
    for label, address in (
        ("prefix inbound reference", "00535ede"),
        ("instruction-interior inbound reference", "00535ee1"),
        ("suffix inbound reference", "00535eee"),
    ):
        forged_xrefs = copy.deepcopy(xrefs)
        target = one(forged_xrefs, "target_addr", address, f"selftest {label}")
        target.update({
            "from_addr": "00530000",
            "from_function_addr": "0052ff30",
            "from_function": "ScriptCommandRegistry__InitBuiltins",
            "ref_type": "DATA",
        })
        expect_refused(
            label,
            "Ghidra residual xref set differs",
            lambda forged=forged_xrefs: validate_listing_rows(instructions, forged),
        )
    police = read_tsv(root / CLOSURE_RELATIVE / "police-dispositions.tsv")
    forged_police = copy.deepcopy(police)
    one(forged_police, "entityKey", OLD_ENTITY, "selftest police")["disposition"] = "TERMINAL"
    closure = read_json(root / CLOSURE_RELATIVE / "closure.ready.json")
    expect_refused(
        "police disposition laundering",
        "police disposition content differs",
        lambda: validate_police_rows(forged_police, closure),
    )
    with tempfile.TemporaryDirectory() as temporary:
        duplicate_json = Path(temporary) / "duplicate.json"
        duplicate_json.write_text(
            '{"verdict":"FAIL","verdict":"PASS"}\n', encoding="utf-8"
        )
        expect_refused(
            "duplicate JSON key laundering",
            "duplicate JSON key",
            lambda: read_json(duplicate_json),
        )


def build(root: Path) -> Path:
    del root
    raise ProofError(
        "this one-shot proof is frozen and cannot be rebuilt; verify the sealed "
        "READY with an explicitly restored historical project"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify", "selftest"))
    parser.add_argument(
        "--ghidra-project-root",
        type=Path,
        help=(
            "new writable restore of the historical SetPos POST project; the "
            "active mutable project and tracked checkpoint are forbidden"
        ),
    )
    args = parser.parse_args(argv)
    root = repo_root()
    ready = root / EVIDENCE_RELATIVE / READY_NAME
    try:
        if args.command == "build":
            path = build(root)
            print(f"MISSION_NATIVE_UNSETOBJECTIVE_REPROOF_READY {logical_stamp(path, (EVIDENCE_RELATIVE / READY_NAME).as_posix())}")
        elif args.command == "verify":
            validate_saved(read_json(ready), root, args.ghidra_project_root)
            print(f"MISSION_NATIVE_UNSETOBJECTIVE_REPROOF_VERIFIED {logical_stamp(ready, (EVIDENCE_RELATIVE / READY_NAME).as_posix())}")
        else:
            selftest(root, args.ghidra_project_root)
            print("MISSION_NATIVE_UNSETOBJECTIVE_REPROOF_SELFTEST_OK 16 targeted counterexamples rejected")
    except (ProofError, KeyError, IndexError, ValueError, OSError, struct.error) as exc:
        print(f"MISSION_NATIVE_UNSETOBJECTIVE_REPROOF_REFUSED {exc}", file=os.sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
