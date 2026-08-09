#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Prove the exact Mission-native SetPos body and surrounding NOP partition.

This proof is static and read-only.  It binds the pristine executable, the
canonical Generation-14 frontier, the shipped native registry, the latest
recoverable live-Ghidra state, and an independent Ghidra listing/xref export.
It proves a boundary, shipped name, and bounded static call shape; it does not
claim runtime vector values, failure behavior, or rebuild parity.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import struct
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "bea.re.mission-native-setpos-boundary-reproof.v1"
CLAIM = "MISSION_NATIVE_SETPOS_EXACT_FUNCTION_AND_NOP_PARTITION"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
EVIDENCE_RELATIVE = Path("local-lab/mission-native-setpos-boundary-reproof-20260809-v1")
READY_NAME = "proof.ready.json"

PARENT_RELATIVE = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-14-tokenarchive-dispatch-reproof-v1"
)
PARENT_READY_SHA256 = "9864424def44034a5a5e9a68814ce111076182ad7ea898c9d0040d888c92f32b"
PARENT_REDUCER_ID = "ec58dc9ec399d719677c5ab98ab0ac2efe60d8138c4f2c829f3e5930a946dec2"
PARENT_AUTHORITY_SHA256 = "83a5544bdde805762b01983171c336826ea62a8b2dd8be94109bef959560ff72"
PARENT_COUNTS = {
    "functions": 8124,
    "residuals": 6117,
    "questions": 15245,
    "scenarios": 72,
    "levers": 915,
    "contracts": 14241,
    "adjudications": 6092,
    "supersessions": 584,
}

RESIDUAL_START = 0x00536C61
FUNCTION_START = 0x00536C70
FUNCTION_END = 0x00536C9A
RESIDUAL_END = 0x00536CA0
REGISTRY_INIT = 0x00532FC9
REGISTRY_SLOT = 0x0064F010
NAME_ADDRESS = 0x0064F2A4

RESIDUAL_SHA256 = "fe4f57175c4db002b63ebbe79638e460a4e4e5f28c90bdd431a95c2ce1939429"
PREFIX_SHA256 = "40f0d021fa824f3b40dc646f67479997734d273d9121690b6f042c512df3a838"
BODY_SHA256 = "1a1ecfe8dde56ad132cc0a5d05010ebe43936f01602cc47012e4826c55ff9fa1"
SUFFIX_SHA256 = "ff35ffe14925642da6f3a258b35811e08101c03f8b5db346e5afcca448677564"
RANGE_SHA256 = "679f653081c42099a6f086e0ff7e656596f1e5ca8588272c1bb35db45c7780fa"

OLD_ENTITY = (
    "TEXT_RESIDUAL:" + SPECIMEN_SHA256 + ":0x00536C61-0x00536CA0"
)
OLD_CONTRACT = "C-8a872897570c0c09"
RESIDUAL_QUESTION = "Q-b87fb6bcbb8fb28d"
CANDIDATE_ENTITY = (
    "CODE_CANDIDATE:" + SPECIMEN_SHA256 + ":VA=0X00536C70"
)
CANDIDATE_QUESTION = "Q-417d6c90fb7c0519"
NEW_ENTITY = (
    "CODE:" + SPECIMEN_SHA256
    + ":VA=0x00536c70:RANGES=" + RANGE_SHA256
)
NEW_CONTRACT = "C-aca39413b2419b80"
SUCCESSOR_QUESTION = "Q-b9d7aa552ce48a32"

INSTRUCTIONS = (
    (0x00536C70, "8b 44 24 04", "MOV", "EAX, dword ptr [ESP + 0x4]"),
    (0x00536C74, "83 ec 10", "SUB", "ESP, 0x10"),
    (0x00536C77, "56", "PUSH", "ESI"),
    (0x00536C78, "8b f1", "MOV", "ESI, ECX"),
    (0x00536C7A, "8b 08", "MOV", "ECX, dword ptr [EAX]"),
    (0x00536C7C, "8d 44 24 04", "LEA", "EAX, [ESP + 0x4]"),
    (0x00536C80, "50", "PUSH", "EAX"),
    (0x00536C81, "8b 11", "MOV", "EDX, dword ptr [ECX]"),
    (0x00536C83, "ff 52 44", "CALL", "dword ptr [EDX + 0x44]"),
    (0x00536C86, "8b 4e 10", "MOV", "ECX, dword ptr [ESI + 0x10]"),
    (0x00536C89, "8d 44 24 04", "LEA", "EAX, [ESP + 0x4]"),
    (0x00536C8D, "50", "PUSH", "EAX"),
    (0x00536C8E, "8b 11", "MOV", "EDX, dword ptr [ECX]"),
    (0x00536C90, "ff 52 50", "CALL", "dword ptr [EDX + 0x50]"),
    (0x00536C93, "5e", "POP", "ESI"),
    (0x00536C94, "83 c4 10", "ADD", "ESP, 0x10"),
    (0x00536C97, "c2 0c 00", "RET", "0xc"),
)

INPUTS: dict[str, tuple[int, str]] = {
    "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup": (2_506_752, SPECIMEN_SHA256),
    f"{PARENT_RELATIVE.as_posix()}/campaign.ready.json": (16_930, PARENT_READY_SHA256),
    f"{PARENT_RELATIVE.as_posix()}/campaign-functions.tsv": (5_129_929, "eeb992ab962308b97834f314675521bb82064f50d37ca57f40ff6ad5c54a4534"),
    f"{PARENT_RELATIVE.as_posix()}/campaign-residuals.tsv": (2_864_955, "b0611722b49bbebbb666bce2c51d534e30ac7ad561d43daa594f5c40fcfdb1c3"),
    f"{PARENT_RELATIVE.as_posix()}/campaign-questions.tsv": (8_364_524, "49e3987f4bfa1996838d62823c2d8cc74f26e82843099fadbd055ef52cf4b40d"),
    f"{PARENT_RELATIVE.as_posix()}/campaign-contracts.tsv": (10_905_813, "7d5cefef1a6c18fdac8cbe9fa46ea119a6e6d47528f1a5743d9124c22c12a4f8"),
    "local-lab/re-campaign-incident-recovery-20260808-v1/generation-14-tokenarchive-dispatch-reproof-authority.ready.json": (8_215, PARENT_AUTHORITY_SHA256),
    "local-lab/ghidra-from-trace-2026-07-28/script-native-table-144.tsv": (9_016, "42027af22e1d4a0611bf7286fd1ea0df17adf01f7bf54ad5a2196f8484f40d86"),
    "local-lab/re-ledger/coverage-ledger-2026-08-02-baseline7555-exact-v5-ready/ledger-native-handlers.tsv": (14_810, "4a4ad8ec134a03dbf3438137013c877361db2f4708189a2410a8fcc97baa5563"),
    "references/Onslaught/thing.h": (11_680, "cf0c15e24869d57ab354251f465aee6dc1780c6f7c557fec27d081d71a46e8fe"),
    "local-lab/ghidra-tokenarchive-dispatch-live-promotion-20260809-v1/promotion/promotion.ready.json": (6_072, "8ca256ec03e36aa27c4f25720ce6882fc1ece3d91d408a4097b2740e239ec632"),
    "local-lab/ghidra-tokenarchive-dispatch-live-promotion-20260809-v1/backups/post-live/backup_manifest.json": (7_589, "ad7e7ce4e8d135f5455355946cbdb7eeb7111cb99c0d54045723d736b4ed908b"),
    "local-lab/ghidra-tokenarchive-dispatch-live-promotion-20260809-v1/post-live-restore.ready.json": (6_007, "2bfbd3728a1c237efc2b340a1230052ea299c5ad6f17844fa6daf15d094afd77"),
    "local-lab/ghidra-tokenarchive-dispatch-live-promotion-20260809-v1/runs/live-readback/functions.tsv": (7_051_668, "075165bae3616dda0adf534625db612990daee9974b3fc85429d3b5b408ee979"),
    "local-lab/ghidra-tokenarchive-dispatch-live-promotion-20260809-v1/runs/live-readback/program.tsv": (1_267, "fce597559bd1baf48d0c2759ef89aa277ba5cc0dbe6ae9a8071df5e7562adb4e"),
    f"{EVIDENCE_RELATIVE.as_posix()}/addresses.txt": (330, "c07be6a60a9f2013a6849fde8b0505c5be4bf7cb5d851ee5176f5ec3fea89179"),
    f"{EVIDENCE_RELATIVE.as_posix()}/ghidra-readonly/instructions.tsv": (69_398, "33f022bee40ade1dcd3b96287a091cebafd2a3db46fb9bbbb6f9c16d3562e6d0"),
    f"{EVIDENCE_RELATIVE.as_posix()}/ghidra-readonly/xrefs.tsv": (1_410, "d4051e952d09d3e846fdb0afe4888214002fa243a25d710f9d3531fe9027a528"),
    f"{EVIDENCE_RELATIVE.as_posix()}/ghidra-readonly/headless.log": (5_464, "6da40f30069e8d39df37831a3860ede7ce18caffbe50881c58c2791a4f89afb1"),
}


class ProofError(ValueError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise ProofError(message)


def repo_root() -> Path:
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


def read_tsv(path: Path, *, campaign: bool = False) -> list[dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if campaign:
        require(lines and lines[0] == "# bea.re.campaign.v5", f"campaign marker differs: {path}")
    rows = [line for line in lines if line and not line.startswith("# ")]
    require(rows, f"TSV has no rows: {path}")
    return list(csv.DictReader(rows, delimiter="\t"))


def exact_inputs(root: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for relative, expected in sorted(INPUTS.items()):
        actual = stamp(root / relative, root)
        require((actual["bytes"], actual["sha256"]) == expected, f"input identity differs: {relative}")
        result[relative] = actual
    return result


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


def va_bytes(image: bytes, start: int, end: int) -> bytes:
    offset = pe_offset(image, start)
    value = image[offset:offset + end - start]
    require(len(value) == end - start, f"short PE span at 0x{start:08x}")
    return value


def validate_pristine(image: bytes) -> dict[str, Any]:
    require(len(image) == 2_506_752 and sha256_bytes(image) == SPECIMEN_SHA256, "pristine specimen differs")
    spans = {
        "residual": (RESIDUAL_START, RESIDUAL_END, 63, RESIDUAL_SHA256),
        "prefixPadding": (RESIDUAL_START, FUNCTION_START, 15, PREFIX_SHA256),
        "functionBody": (FUNCTION_START, FUNCTION_END, 42, BODY_SHA256),
        "suffixPadding": (FUNCTION_END, RESIDUAL_END, 6, SUFFIX_SHA256),
    }
    raw: dict[str, bytes] = {}
    for name, (start, end, size, digest) in spans.items():
        value = va_bytes(image, start, end)
        require(len(value) == size and sha256_bytes(value) == digest, f"{name} bytes differ")
        raw[name] = value
    require(raw["prefixPadding"] == b"\x90" * 15, "prefix is not exact NOP padding")
    require(raw["suffixPadding"] == b"\x90" * 6, "suffix is not exact NOP padding")
    instruction_bytes = b"".join(bytes.fromhex(row[1]) for row in INSTRUCTIONS)
    require(instruction_bytes == raw["functionBody"], "instruction framing does not cover the exact body")
    cursor = FUNCTION_START
    for address, encoded, _mnemonic, _operands in INSTRUCTIONS:
        require(address == cursor, f"instruction sequence has a gap at 0x{cursor:08x}")
        cursor += len(bytes.fromhex(encoded))
    require(cursor == FUNCTION_END, "instruction sequence does not end at the proposed boundary")
    initializer = va_bytes(image, REGISTRY_INIT, REGISTRY_INIT + 11)
    require(
        initializer == bytes.fromhex("bf706c5300893d10f06400"),
        "registry initializer does not load SetPos and store it in the expected slot",
    )
    require(va_bytes(image, NAME_ADDRESS, NAME_ADDRESS + 7) == b"SetPos\0", "shipped SetPos string differs")
    return {
        "oldResidual": {"startVa": "0x00536c61", "endVa": "0x00536ca0", "bytes": 63, "sha256": RESIDUAL_SHA256},
        "partition": [
            {"kind": "NOP_PADDING", "startVa": "0x00536c61", "endVa": "0x00536c70", "bytes": 15, "sha256": PREFIX_SHA256},
            {"kind": "MISSION_NATIVE_FUNCTION", "startVa": "0x00536c70", "endVa": "0x00536c9a", "bytes": 42, "sha256": BODY_SHA256, "bodyRangeSetSha256": RANGE_SHA256},
            {"kind": "NOP_PADDING", "startVa": "0x00536c9a", "endVa": "0x00536ca0", "bytes": 6, "sha256": SUFFIX_SHA256},
        ],
        "instructionCount": len(INSTRUCTIONS),
        "calleeCleanupBytes": 12,
        "computedCalls": [
            {"at": "0x00536c83", "receiver": "FIRST_STACK_ARGUMENT_DEREFERENCE", "vtableOffset": "0x44", "output": "16_BYTE_STACK_TEMPORARY"},
            {"at": "0x00536c90", "receiver": "THIS_PLUS_0x10_DEREFERENCE", "vtableOffset": "0x50", "input": "SAME_16_BYTE_STACK_TEMPORARY"},
        ],
        "registryInitializer": {"startVa": "0x00532fc9", "slotVa": "0x0064f010", "handlerVa": "0x00536c70"},
        "shippedName": {"address": "0x0064f2a4", "value": "SetPos"},
    }


def one(rows: list[dict[str, str]], key: str, value: str, label: str) -> dict[str, str]:
    matches = [row for row in rows if row.get(key) == value]
    require(len(matches) == 1, f"{label} census differs")
    return matches[0]


def validate_parent(root: Path) -> dict[str, Any]:
    ready = read_json(root / PARENT_RELATIVE / "campaign.ready.json")
    require(ready.get("generation") == 14, "parent generation differs")
    require(ready.get("counts") == PARENT_COUNTS, "parent counts differ")
    require(ready.get("reducer", {}).get("id") == PARENT_REDUCER_ID, "parent reducer differs")
    residual = one(read_tsv(root / PARENT_RELATIVE / "campaign-residuals.tsv", campaign=True), "entityKey", OLD_ENTITY, "parent residual")
    contract = one(read_tsv(root / PARENT_RELATIVE / "campaign-contracts.tsv", campaign=True), "contractId", OLD_CONTRACT, "parent residual contract")
    questions = read_tsv(root / PARENT_RELATIVE / "campaign-questions.tsv", campaign=True)
    residual_question = one(questions, "questionId", RESIDUAL_QUESTION, "parent residual question")
    candidate_question = one(questions, "questionId", CANDIDATE_QUESTION, "parent native-boundary question")
    require(
        residual.get("startVa") == "0x00536c61"
        and residual.get("endVa") == "0x00536ca0"
        and residual.get("bytes") == "63"
        and residual.get("classification") == "AMBIGUOUS"
        and residual.get("classificationVerdict") == "UNSCORED"
        and residual.get("terminalState") == "OPEN_CLASSIFICATION"
        and residual.get("questionIds") == RESIDUAL_QUESTION,
        "parent residual is not the exact open frontier",
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
        and candidate_question.get("source") == "native:135",
        "parent native-boundary question differs",
    )
    functions = read_tsv(root / PARENT_RELATIVE / "campaign-functions.tsv", campaign=True)
    previous = one(functions, "entryVa", "0x00536c00", "previous campaign function")
    following = one(functions, "entryVa", "0x00536ca0", "following campaign function")
    require(previous.get("bodyRangesRva") == "0x136c00-0x136c61", "previous function does not end at residual")
    require(following.get("currentName") == "IScript__TriggerHitEffect", "following function identity differs")
    return {
        "generation": 14,
        "readySha256": PARENT_READY_SHA256,
        "reducerId": PARENT_REDUCER_ID,
        "authorityReceiptSha256": PARENT_AUTHORITY_SHA256,
        "oldEntityKey": OLD_ENTITY,
        "oldContractId": OLD_CONTRACT,
        "questions": [RESIDUAL_QUESTION, CANDIDATE_QUESTION],
    }


def validate_registry(root: Path) -> dict[str, Any]:
    table = read_tsv(root / "local-lab/ghidra-from-trace-2026-07-28/script-native-table-144.tsv")
    row = one(table, "index", "135", "shipped native registry row")
    require(
        row == {
            "index": "135",
            "record": "0x0064efe0",
            "handler": "0x00536c70",
            "shippedName": "SetPos",
            "ghidraName": "",
            "status": "NO_FUNCTION",
        },
        "shipped native registry row differs",
    )
    ledger = read_tsv(
        root / "local-lab/re-ledger/coverage-ledger-2026-08-02-baseline7555-exact-v5-ready/ledger-native-handlers.tsv"
    )
    state = one(ledger, "index", "135", "native boundary ledger row")
    require(
        state.get("handlerVa") == "0x00536c70"
        and state.get("shippedName") == "SetPos"
        and state.get("registryStatus") == "NO_FUNCTION"
        and state.get("functionPresent") == "False"
        and state.get("terminalState") == "BOUNDARY_MISSING"
        and state.get("needsBoundaryReview") == "True",
        "native boundary ledger row differs",
    )
    source = (root / "references/Onslaught/thing.h").read_text(encoding="utf-8", errors="strict")
    require("void\t\t\tSetPos(FVector &inPos)\t\t\t{ mPos=inPos; }" in source, "pinned source SetPos declaration differs")
    return {
        "index": 135,
        "recordVa": "0x0064efe0",
        "handlerVa": "0x00536c70",
        "shippedName": "SetPos",
        "priorState": "BOUNDARY_MISSING",
        "sourceCorroboration": "ARCHITECTURE_ONLY_CTHING_SETPOS_FVECTOR_REFERENCE_NOT_RETAIL_HANDLER_IDENTITY",
    }


def validate_ghidra(root: Path) -> dict[str, Any]:
    promotion = read_json(root / "local-lab/ghidra-tokenarchive-dispatch-live-promotion-20260809-v1/promotion/promotion.ready.json")
    require(
        promotion.get("verdict") == "READY"
        and promotion.get("phase") == "LIVE_PROMOTED"
        and promotion.get("result", {}).get("functionsChanged") == 0
        and promotion.get("result", {}).get("boundariesChanged") == 0
        and promotion.get("live", {}).get("readback", {}).get("inventory", {}).get("functions", {}).get("sha256")
        == "075165bae3616dda0adf534625db612990daee9974b3fc85429d3b5b408ee979",
        "latest live Ghidra authority differs",
    )
    backup = read_json(root / "local-lab/ghidra-tokenarchive-dispatch-live-promotion-20260809-v1/backups/post-live/backup_manifest.json")
    require(
        backup.get("sourceStable") is True
        and backup.get("copyComparison", {}).get("matches") is True
        and backup.get("source") == backup.get("destination")
        and backup.get("source", {}).get("fileCount") == 19,
        "latest Ghidra POST backup is not exact and recoverable",
    )
    restore = read_json(root / "local-lab/ghidra-tokenarchive-dispatch-live-promotion-20260809-v1/post-live-restore.ready.json")
    require(
        restore.get("sourceStable") is True
        and restore.get("copyComparison", {}).get("matches") is True
        and restore.get("probeCopyDisposition") == "RETAINED_AT_VERIFICATION"
        and restore.get("readonlyOpen", {}).get("opened") is True
        and restore.get("readonlyOpen", {}).get("contentStable") is True
        and restore.get("readonlyOpen", {}).get("postOpenComparison", {}).get("matches") is True,
        "latest Ghidra POST restore drill differs",
    )
    functions = read_tsv(root / "local-lab/ghidra-tokenarchive-dispatch-live-promotion-20260809-v1/runs/live-readback/functions.tsv")
    require(not any(row.get("address") == "0x00536c70" for row in functions), "SetPos is already a live function")
    previous = one(functions, "address", "0x00536c00", "live previous function")
    following = one(functions, "address", "0x00536ca0", "live following function")
    require(previous.get("bodyMax") == "0x00536c60" and previous.get("bodyBytes") == "97", "live previous boundary differs")
    require(following.get("name") == "IScript__TriggerHitEffect" and following.get("bodyMin") == "0x00536ca0", "live following boundary differs")

    instructions = read_tsv(root / EVIDENCE_RELATIVE / "ghidra-readonly/instructions.tsv")
    target_rows = {
        row["target_addr"]: row
        for row in instructions
        if row.get("role") == "TARGET" and row.get("target_addr") in {f"0x{address:08x}" for address, *_ in INSTRUCTIONS}
    }
    require(len(target_rows) == len(INSTRUCTIONS), "Ghidra instruction target census differs")
    for address, encoded, mnemonic, operands in INSTRUCTIONS:
        row = target_rows.get(f"0x{address:08x}")
        require(row is not None, f"Ghidra instruction missing at 0x{address:08x}")
        require(
            row.get("instruction_addr") == f"0x{address:08x}"
            and row.get("function_entry") == "<none>"
            and row.get("function_name") == "<no_function>"
            and (row.get("mnemonic"), row.get("operands"), row.get("bytes")) == (mnemonic, operands, encoded),
            f"Ghidra instruction differs at 0x{address:08x}",
        )
    missing = {
        row.get("target_addr")
        for row in instructions
        if row.get("role") == "MISSING" and row.get("instruction_addr") == "<none>"
    }
    require({"0x00536c61", "0x00536c9a"}.issubset(missing), "Ghidra padding is unexpectedly defined as code")
    init = [row for row in instructions if row.get("target_addr") == "0x00532fc9" and row.get("role") == "TARGET"]
    require(
        len(init) == 1
        and init[0].get("function_name") == "ScriptCommandRegistry__InitBuiltins"
        and init[0].get("mnemonic") == "MOV"
        and init[0].get("operands") == "EDI, 0x536c70",
        "Ghidra registry initializer instruction differs",
    )
    xrefs = read_tsv(root / EVIDENCE_RELATIVE / "ghidra-readonly/xrefs.tsv")
    actual_refs = {
        (row.get("target_addr"), row.get("from_addr"), row.get("from_function"), row.get("ref_type"))
        for row in xrefs if row.get("from_addr") != "<none>"
    }
    expected_refs = {
        ("0064f010", "00532fce", "ScriptCommandRegistry__InitBuiltins", "WRITE"),
        ("0064f2a4", "005330a9", "ScriptCommandRegistry__InitBuiltins", "DATA"),
        ("00536c70", "00532fc9", "ScriptCommandRegistry__InitBuiltins", "DATA"),
        ("00536ca0", "00532e4b", "ScriptCommandRegistry__InitBuiltins", "DATA"),
    }
    require(actual_refs == expected_refs, "Ghidra xref set differs or an interior entry exists")
    return {
        "sourceProject": "TOKENARCHIVE_LIVE_POST_BACKUP_READ_ONLY",
        "functionCount": 8124,
        "listingDecodedInstructions": 17,
        "proposedBodyCurrentlyHasFunction": False,
        "interiorInboundReferences": 0,
        "entryInboundReference": {
            "fromVa": "0x00532fc9",
            "fromFunction": "ScriptCommandRegistry__InitBuiltins",
            "type": "DATA",
        },
        "neighbors": [
            {"entryVa": "0x00536c00", "name": previous["name"], "bodyMax": previous["bodyMax"]},
            {"entryVa": "0x00536ca0", "name": following["name"], "bodyMin": following["bodyMin"]},
        ],
    }


def derive(root: Path) -> dict[str, Any]:
    require((root / EVIDENCE_RELATIVE).is_dir(), "SetPos evidence root is missing")
    inputs = exact_inputs(root)
    image = (root / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup").read_bytes()
    return {
        "schema": SCHEMA,
        "verdict": "PASS",
        "claim": CLAIM,
        "specimen": {"sha256": SPECIMEN_SHA256, "role": "STATIC_BYTE_AUTHORITY_UNCHANGED"},
        "parent": validate_parent(root),
        "registry": validate_registry(root),
        "staticProof": validate_pristine(image),
        "ghidra": validate_ghidra(root),
        "adjudication": {
            "oldEntityKey": OLD_ENTITY,
            "newFunctionEntityKey": NEW_ENTITY,
            "newFunctionContractId": NEW_CONTRACT,
            "questionsAddressed": [RESIDUAL_QUESTION, CANDIDATE_QUESTION],
            "successorQuestionId": SUCCESSOR_QUESTION,
            "successorQuestionType": "FUNCTION_CONTRACT",
            "newName": "IScript__SetPos",
            "nativeShippedName": "SetPos",
            "functionBoundaryVerdict": "SURVIVED",
            "residualPartitionVerdict": "SURVIVED",
            "semanticGradeCeiling": "C1_STATIC",
            "semanticPromotionApplied": False,
        },
        "boundedContract": {
            "callingConvention": "__thiscall",
            "calleeCleanupBytes": 12,
            "stackArguments": 3,
            "receiver": "ISCRIPT_LIKE_THIS_WITH_OBJECT_AT_PLUS_0x10",
            "firstInput": "POINTER_DEREFERENCED_TO_VTABLE_RECEIVER",
            "temporary": "16_BYTES_ON_STACK",
            "orderedCalls": ["FIRST_INPUT_VTABLE_PLUS_0x44", "THIS_PLUS_0x10_OBJECT_VTABLE_PLUS_0x50"],
            "returns": "NO_TYPED_RETURN_CLAIM_STATIC_ONLY",
            "writes": "DELEGATED_TARGET_STATE_UNKNOWN_WITHOUT_RUNTIME_PROBE",
        },
        "limitations": [
            "The shipped registry and unique initializer reference prove the SetPos handler identity and entry, while exact bytes and listing prove only the bounded static call shape.",
            "The first indirect call writes a 16-byte stack temporary and the second consumes it, but static evidence alone does not prove the vector's runtime values or all target-side effects.",
            "The pinned Stuart CThing::SetPos(FVector&) source is architecture corroboration only and is not used as released-handler identity or behavior authority.",
            "The proof does not claim that all three stack arguments are semantically used; only the first is read directly, while RET 0x0C proves callee cleanup of three slots.",
            "No gameplay, TTD replay, executable write, or Ghidra mutation occurred while producing this proof.",
        ],
        "inputs": inputs,
        "author": stamp(Path(__file__), root),
    }


def validate_saved(saved: dict[str, Any], root: Path) -> None:
    fresh = derive(root)
    require(set(saved) == set(fresh) | {"generatedAtUtc"}, "proof top-level shape differs")
    generated = saved.get("generatedAtUtc")
    require(isinstance(generated, str) and generated.endswith("Z"), "proof timestamp is not UTC")
    parsed = datetime.fromisoformat(generated[:-1] + "+00:00")
    require(parsed.tzinfo is not None, "proof timestamp lacks timezone")
    stable = dict(saved)
    del stable["generatedAtUtc"]
    require(stable == fresh, "proof content differs from independently rederived evidence")


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
    root = repo_root()
    ready = root / EVIDENCE_RELATIVE / READY_NAME
    try:
        if args.command == "build":
            path = build(root)
            print(f"MISSION_NATIVE_SETPOS_REPROOF_READY {stamp(path, root)}")
        else:
            validate_saved(read_json(ready), root)
            print(f"MISSION_NATIVE_SETPOS_REPROOF_VERIFIED {stamp(ready, root)}")
    except (ProofError, KeyError, IndexError, ValueError, OSError, struct.error) as exc:
        print(f"MISSION_NATIVE_SETPOS_REPROOF_REFUSED {exc}", file=os.sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
