#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Prove the exact ReadNextToken dispatch-table partition at 0x004F5AC5.

The proof is deliberately static.  It binds pristine bytes, the exact open
Generation 13 residual, the earlier over-broad small-table claim and police
reopen, and a read-only export from the latest verified Ghidra POST backup.
It does not execute the game or mutate Ghidra.
"""

from __future__ import annotations

import argparse
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


SCHEMA = "bea.re.tokenarchive-readnexttoken-dispatch-table-reproof.v1"
CLAIM = "TOKENARCHIVE_READNEXTTOKEN_EXACT_DISPATCH_TABLE_AND_ALIGNMENT_PARTITION"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
EVIDENCE_RELATIVE = Path("local-lab/tokenarchive-dispatch-table-reproof-20260809-v1")
READY_NAME = "proof.ready.json"

PARENT_RELATIVE = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-13-applydamage-primary-reproof-v1"
)
PARENT_READY_SHA256 = "8436a5a99145f6910cd147bdb419a0efbfb071fcf16d8f42ec330182a97df63e"
PARENT_REDUCER_ID = "988e0660634b6fa59b2018a96545cdf84666e2c219c7a7ac89809c4ef99fac2e"
PARENT_AUTHORITY_SHA256 = "772f65ba5210c6d022bff64aefb6523a563ed1b8c3ab53eb87aef8dfe4b1944d"
PARENT_COUNTS = {
    "functions": 8124,
    "residuals": 6117,
    "questions": 15245,
    "scenarios": 72,
    "levers": 915,
    "contracts": 14241,
    "adjudications": 6091,
    "supersessions": 584,
}

START = 0x004F5AC5
END = 0x004F5B70
PREFIX_END = 0x004F5AC8
POINTER_END = 0x004F5AE4
INDEX_END = 0x004F5B61
CONSUMER_START = 0x004F583B
CONSUMER_END = 0x004F5854
PREVIOUS_FUNCTION = 0x004F57B0
NEXT_FUNCTION = 0x004F5B70
POINTER_TARGETS = (
    0x004F5ABB,
    0x004F587E,
    0x004F588F,
    0x004F5854,
    0x004F58AE,
    0x004F59B7,
    0x004F5904,
)
INDEX_COUNTS = {0: 1, 1: 2, 2: 19, 3: 47, 4: 3, 5: 37, 6: 16}

WHOLE_SHA256 = "9b55806e7ca788cf70b9008ff81c64d034980f927690ecd33881a1c9cbad5510"
PREFIX_SHA256 = "53e090edb4fca0626d458dbefa0ae1bcbffc511ed159f1a70641610ad0d9a200"
POINTER_SHA256 = "d9bf96faa2cffa25a941f51f63255b8b6ee947dabf5792c405241eb78b4c3e2f"
INDEX_SHA256 = "26d7739dc4645ebf70177e7023862e1a57cf5e421e6cf6a60100f2f5d97c0d27"
SUFFIX_SHA256 = "40f0d021fa824f3b40dc646f67479997734d273d9121690b6f042c512df3a838"
CONSUMER_SHA256 = "0b326a88f87630cc23d08ad9e4538d06275c6ee4a25b1f823ec218d2cc05f9ca"

ENTITY_KEY = (
    "TEXT_RESIDUAL:" + SPECIMEN_SHA256 + ":0x004F5AC5-0x004F5B70"
)
CONTRACT_ID = "C-5bf283e320e74218"
QUESTION_ID = "Q-95c7eda9662e8e13"

INPUTS: dict[str, tuple[int, str]] = {
    "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup": (2_506_752, SPECIMEN_SHA256),
    f"{PARENT_RELATIVE.as_posix()}/campaign.ready.json": (17_270, PARENT_READY_SHA256),
    f"{PARENT_RELATIVE.as_posix()}/campaign-residuals.tsv": (2_864_870, "30d390b75a9984efc6bebedf5ddb00412326d36e51d2c9f3c1883032dd25ef49"),
    f"{PARENT_RELATIVE.as_posix()}/campaign-contracts.tsv": (10_904_270, "b27ea5a153833cda4fbeaae9a2f93a65312e64e956e72e01c57055f794713392"),
    f"{PARENT_RELATIVE.as_posix()}/campaign-questions.tsv": (8_364_518, "d4bfeae6720aad38e8508ec6b868ba55715dfd317d1cffba00b1f74049dffb0c"),
    "local-lab/re-campaign-incident-recovery-20260808-v1/generation-13-applydamage-primary-reproof-authority.ready.json": (8_873, PARENT_AUTHORITY_SHA256),
    "local-lab/re-campaign-incident-recovery-20260808-v1/gen73-claim-closure-v1/police-dispositions.tsv": (11_251, "83720df93d8a808e8083ffb276f51dcf034b5bfd4992b7bd832acf6182d9a701"),
    "local-lab/re-campaign-incident-recovery-20260808-v1/gen73-claim-closure-v1/source-dispositions.tsv": (2_556_390, "2bb817a0d4856b52fe107b4672adcdf62277c9ebe1c27ff85fcced4558e117db"),
    "local-lab/re-campaign-incident-recovery-20260808-v1/gen73-claim-closure-v1/effective-claims.tsv": (4_498_241, "433cc541b910a93a3d22b536aa3f91ac916e839872efa6982c88901461e6ceb1"),
    "local-lab/open-residual-gen23-small-table-20260805-v1/FORMAL-PACK.json": (76_419, "b3c1b12deb722b0a10e67cdd2cd64c5727aa85691419b224a79affd2e6f8f872"),
    "local-lab/ghidra-damage-hit-semantic-live-promotion-20260809-v1/promotion/promotion.ready.json": (4_453, "f13caf898ee760e3af8bbe6634d595cfec4f765897dac0b572d713bed82492cd"),
    "local-lab/ghidra-damage-hit-semantic-live-promotion-20260809-v1/backups/post-live/backup_manifest.json": (7_589, "7a2797143f306c528f2ef6ef45701abd5b253d12900eca5d5528c61f57bcad8b"),
    "local-lab/ghidra-damage-hit-semantic-live-promotion-20260809-v1/runs-v2/live-post-inventory/functions.tsv": (7_051_668, "075165bae3616dda0adf534625db612990daee9974b3fc85429d3b5b408ee979"),
    "local-lab/ghidra-damage-hit-semantic-live-promotion-20260809-v1/runs-v2/live-post-inventory/program.tsv": (1_267, "e1724ff7ae231326cd4b25a6c8d8d0d53ebb844a509541c402cdd64436474029"),
    "local-lab/tokenarchive-dispatch-table-reproof-20260809-v1/addresses.txt": (229, "9cd485fb7ee7728e7a9f6c4d9e2179b85fe447815aae0e096cb3bee1a70a0d40"),
    "local-lab/tokenarchive-dispatch-table-reproof-20260809-v1/ghidra-readonly/instructions.tsv": (16_671, "286cce4d79229ef626933a5c955fc20babe68708266f1fa11baaa1dddbcf0926"),
    "local-lab/tokenarchive-dispatch-table-reproof-20260809-v1/ghidra-readonly/xrefs.tsv": (3_936, "c18e6d7a1be12bee65f7a8e04acea928c748f30ed3ca2a1ed47aa8e9ba2e3242"),
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


def read_tsv(path: Path, campaign: bool = False) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        first = stream.readline()
        if campaign:
            require(first.rstrip("\r\n") == "# bea.re.campaign.v5", f"campaign marker differs: {path}")
        elif not first.startswith("# "):
            stream.seek(0)
        return list(csv.DictReader(stream, delimiter="\t"))


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


def validate_pristine(image: bytes, *, require_whole_image: bool = True) -> dict[str, Any]:
    if require_whole_image:
        require(len(image) == 2_506_752 and sha256_bytes(image) == SPECIMEN_SHA256, "pristine specimen differs")
    spans = {
        "whole": (START, END, 171, WHOLE_SHA256),
        "alignmentPrefix": (START, PREFIX_END, 3, PREFIX_SHA256),
        "pointerTable": (PREFIX_END, POINTER_END, 28, POINTER_SHA256),
        "indexTable": (POINTER_END, INDEX_END, 125, INDEX_SHA256),
        "alignmentSuffix": (INDEX_END, END, 15, SUFFIX_SHA256),
        "consumer": (CONSUMER_START, CONSUMER_END, 25, CONSUMER_SHA256),
    }
    raw: dict[str, bytes] = {}
    for name, (start, end, size, digest) in spans.items():
        value = va_bytes(image, start, end)
        require(len(value) == size and sha256_bytes(value) == digest, f"{name} bytes differ")
        raw[name] = value
    require(raw["alignmentPrefix"] == bytes.fromhex("8d4900"), "prefix is not the exact MSVC three-byte align NOP")
    require(raw["alignmentSuffix"] == b"\x90" * 15, "suffix is not fifteen one-byte NOPs")
    pointers = struct.unpack("<7I", raw["pointerTable"])
    require(pointers == POINTER_TARGETS, "dispatch pointer targets differ")
    require(all(PREVIOUS_FUNCTION <= target <= 0x004F5ABB for target in pointers), "dispatch target leaves ReadNextToken")
    counts = dict(sorted(Counter(raw["indexTable"]).items()))
    require(counts == INDEX_COUNTS, "dispatch index population differs")
    require(min(raw["indexTable"]) == 0 and max(raw["indexTable"]) == 6, "dispatch index exceeds seven-entry table")
    require(
        raw["consumer"] == bytes.fromhex("4083f87c0f877602000033c98a88e45a4f00ff248dc85a4f00"),
        "consumer bound/load/jump sequence differs",
    )
    return {
        "whole": {"startVa": "0x004f5ac5", "endVa": "0x004f5b70", "bytes": 171, "sha256": WHOLE_SHA256},
        "partition": [
            {"kind": "MSVC_ALIGNMENT_NOP", "startVa": "0x004f5ac5", "endVa": "0x004f5ac8", "bytes": 3, "sha256": PREFIX_SHA256},
            {"kind": "READNEXTTOKEN_DISPATCH_POINTER_TABLE", "startVa": "0x004f5ac8", "endVa": "0x004f5ae4", "bytes": 28, "sha256": POINTER_SHA256},
            {"kind": "READNEXTTOKEN_TOKEN_KIND_INDEX", "startVa": "0x004f5ae4", "endVa": "0x004f5b61", "bytes": 125, "sha256": INDEX_SHA256},
            {"kind": "MSVC_ALIGNMENT_NOP", "startVa": "0x004f5b61", "endVa": "0x004f5b70", "bytes": 15, "sha256": SUFFIX_SHA256},
        ],
        "dispatchTargets": [f"0x{value:08x}" for value in pointers],
        "indexValueCounts": {str(key): value for key, value in counts.items()},
        "consumer": {
            "function": "CTokenArchive__ReadNextToken",
            "startVa": "0x004f583b",
            "endVa": "0x004f5854",
            "bytes": 25,
            "sha256": CONSUMER_SHA256,
            "bound": "INC_EAX_THEN_UNSIGNED_MAX_0x7C",
            "indexLoad": "MOV_CL_[EAX+0x004F5AE4]",
            "dispatch": "JMP_[ECX*4+0x004F5AC8]",
        },
    }


def validate_parent(root: Path) -> dict[str, Any]:
    ready = read_json(root / PARENT_RELATIVE / "campaign.ready.json")
    require(ready.get("generation") == 13, "parent generation differs")
    require(ready.get("counts") == PARENT_COUNTS, "parent counts differ")
    require(ready.get("reducer", {}).get("id") == PARENT_REDUCER_ID, "parent reducer differs")
    residuals = read_tsv(root / PARENT_RELATIVE / "campaign-residuals.tsv", campaign=True)
    contracts = read_tsv(root / PARENT_RELATIVE / "campaign-contracts.tsv", campaign=True)
    questions = read_tsv(root / PARENT_RELATIVE / "campaign-questions.tsv", campaign=True)
    residual = [row for row in residuals if row["entityKey"] == ENTITY_KEY]
    contract = [row for row in contracts if row["contractId"] == CONTRACT_ID]
    question = [row for row in questions if row["questionId"] == QUESTION_ID]
    require(len(residual) == len(contract) == len(question) == 1, "parent frontier row census differs")
    require(
        residual[0]["startVa"] == "0x004f5ac5"
        and residual[0]["endVa"] == "0x004f5b70"
        and residual[0]["bytes"] == "171"
        and residual[0]["classification"] == "AMBIGUOUS"
        and residual[0]["classificationVerdict"] == "UNSCORED"
        and residual[0]["terminalState"] == "OPEN_CLASSIFICATION"
        and residual[0]["campaignState"] == "OPEN_DARK_RESIDUAL"
        and residual[0]["questionIds"] == QUESTION_ID,
        "parent residual is not the exact open frontier",
    )
    require(
        contract[0]["entityKey"] == ENTITY_KEY
        and contract[0]["contractState"] == "OPEN_CLASSIFICATION"
        and contract[0]["semanticGrade"] == "C0_OPAQUE"
        and contract[0]["authorVerdict"] == "UNSCORED"
        and contract[0]["refuterVerdict"] == "UNSCORED"
        and contract[0]["questionIds"] == QUESTION_ID,
        "parent contract differs",
    )
    require(
        question[0]["entityKey"] == ENTITY_KEY
        and question[0]["state"] == "OPEN"
        and question[0]["attemptCount"] == "0"
        and question[0]["lastOutcome"] == "UNSCORED",
        "parent question differs",
    )
    return {
        "generation": 13,
        "readySha256": PARENT_READY_SHA256,
        "reducerId": PARENT_REDUCER_ID,
        "authorityReceiptSha256": PARENT_AUTHORITY_SHA256,
        "frontier": {
            "entityKey": ENTITY_KEY,
            "contractId": CONTRACT_ID,
            "questionId": QUESTION_ID,
            "classification": "AMBIGUOUS",
            "state": "OPEN_CLASSIFICATION",
        },
    }


def validate_police_history(root: Path) -> dict[str, Any]:
    pack = read_json(root / "local-lab/open-residual-gen23-small-table-20260805-v1/FORMAL-PACK.json")
    require(pack.get("status") == "READY_FOR_GENERATION" and pack.get("n_proofs") == 47, "historical pack shape differs")
    proof = pack["proofs"][28]
    require(
        proof.get("entityKey") == ENTITY_KEY
        and proof.get("peBytesSha256") == WHOLE_SHA256
        and proof.get("tableBytes") == 28
        and proof.get("proposed", {}).get("classificationVerdict") == "STATIC_SMALL_CODE_PTR_TABLE",
        "historical small-table proof differs",
    )
    police_rows = read_tsv(
        root / "local-lab/re-campaign-incident-recovery-20260808-v1/gen73-claim-closure-v1/police-dispositions.tsv"
    )
    police = [row for row in police_rows if row["entityKey"] == ENTITY_KEY]
    require(len(police) == 1, "police disposition census differs")
    require(
        police[0]["policeReason"] == "SMALL_TABLE_BULK_INDEX"
        and police[0]["disposition"] == "PRESERVE_EXACT_10R_OPEN_FRONTIER"
        and "INDEX length cap" in police[0]["candidateCheapestFalsifier"],
        "police disposition differs",
    )
    source_rows = read_tsv(
        root / "local-lab/re-campaign-incident-recovery-20260808-v1/gen73-claim-closure-v1/source-dispositions.tsv"
    )
    source = [row for row in source_rows if row["entityKey"] == ENTITY_KEY]
    dispositions = {row["disposition"] for row in source}
    require(
        len(source) == 2
        and dispositions == {"REFUTED_BY_POLICE", "POLICE_PRESERVE_PARENT_OPEN"},
        "historical claim dispositions differ",
    )
    effective_rows = read_tsv(
        root / "local-lab/re-campaign-incident-recovery-20260808-v1/gen73-claim-closure-v1/effective-claims.tsv"
    )
    effective = [row for row in effective_rows if row["entityKey"] == ENTITY_KEY]
    require(
        len(effective) == 1
        and effective[0]["claimKind"] == "POLICE_OPEN_DISPOSITION"
        and effective[0]["disposition"] == "PRESERVE_10R_OPEN",
        "effective police-open projection differs",
    )
    return {
        "historicalClaim": "STATIC_SMALL_CODE_PTR_TABLE_ONLY",
        "historicalPackSha256": INPUTS["local-lab/open-residual-gen23-small-table-20260805-v1/FORMAL-PACK.json"][1],
        "disposition": "REFUTED_BY_POLICE_SMALL_TABLE_BULK_INDEX",
        "newProofDifference": "EXACT_125_BYTE_INDEX_LENGTH_AND_CONSUMER_BOUND_PLUS_GHIDRA_XREFS",
    }


def validate_ghidra_rows(
    instruction_rows: list[dict[str, str]],
    xref_rows: list[dict[str, str]],
    function_rows: list[dict[str, str]],
) -> dict[str, Any]:
    functions = {row["address"]: row for row in function_rows}
    previous = functions.get("0x004f57b0")
    following = functions.get("0x004f5b70")
    require(previous is not None and following is not None, "Ghidra neighbor functions are missing")
    require(
        previous["name"] == "CTokenArchive__ReadNextToken"
        and previous["bodyMin"] == "0x004f57b0"
        and previous["bodyMax"] == "0x004f5ac4"
        and previous["bodyBytes"] == "789"
        and previous["instrCount"] == "267",
        "Ghidra ReadNextToken identity differs",
    )
    require(
        following["name"] == "CTokenArchive__BindIndexedFieldPointer"
        and following["bodyMin"] == "0x004f5b70",
        "Ghidra following function differs",
    )
    by_target_role = {
        (row["target_addr"], row["role"]): row for row in instruction_rows
    }
    expected_instructions = {
        ("0x004f5847", "TARGET"): ("MOV", "CL, byte ptr [EAX + 0x4f5ae4]", "8a 88 e4 5a 4f 00"),
        ("0x004f584d", "TARGET"): ("JMP", "dword ptr [ECX*0x4 + 0x4f5ac8]", "ff 24 8d c8 5a 4f 00"),
        ("0x004f5b70", "TARGET"): ("MOV", "EDX, dword ptr [ESP + 0x4]", "8b 54 24 04"),
    }
    for key, expected in expected_instructions.items():
        row = by_target_role.get(key)
        require(row is not None, f"Ghidra instruction evidence missing: {key}")
        require((row["mnemonic"], row["operands"], row["bytes"]) == expected, f"Ghidra instruction differs: {key}")
        require(row["function_entry"] in {"0x004f57b0", "0x004f5b70"}, f"Ghidra instruction owner differs: {key}")
    for address in ("0x004f5ac5", "0x004f5ac8", "0x004f5ae4", "0x004f5b61"):
        row = by_target_role.get((address, "MISSING"))
        require(row is not None and row["instruction_addr"] == "<none>", f"Ghidra unexpectedly defines table/alignment as code: {address}")
    target_rows = {
        row["target_addr"]: row
        for row in instruction_rows
        if row["role"] == "TARGET" and row["target_addr"] in {f"0x{x:08x}" for x in POINTER_TARGETS}
    }
    require(set(target_rows) == {f"0x{x:08x}" for x in POINTER_TARGETS}, "Ghidra dispatch target census differs")
    require(
        all(row["function_entry"] == "0x004f57b0" and row["function_name"] == "CTokenArchive__ReadNextToken" for row in target_rows.values()),
        "Ghidra dispatch target leaves ReadNextToken",
    )

    xrefs = {
        (row["target_addr"].lower(), row["from_addr"].lower(), row["ref_type"])
        for row in xref_rows
    }
    require(("004f5ac8", "004f584d", "DATA") in xrefs, "Ghidra pointer-table reference is missing")
    require(("004f5ae4", "004f5847", "READ") in xrefs, "Ghidra index-table reference is missing")
    for index, target in enumerate(POINTER_TARGETS):
        slot = 0x004F5AC8 + index * 4
        require((f"{target:08x}", f"{slot:08x}", "DATA") in xrefs, f"Ghidra pointer slot {index} reference is missing")
        require((f"{target:08x}", "004f584d", "COMPUTED_JUMP") in xrefs, f"Ghidra computed target {index} is missing")
    return {
        "sourceProject": "LATEST_VERIFIED_DAMAGE_HIT_POST_BACKUP_READ_ONLY",
        "functionCount": 8124,
        "previousFunction": {
            "entryVa": "0x004f57b0",
            "name": "CTokenArchive__ReadNextToken",
            "bodyMax": "0x004f5ac4",
            "bodyBytes": 789,
            "instructionCount": 267,
        },
        "nextFunction": {"entryVa": "0x004f5b70", "name": "CTokenArchive__BindIndexedFieldPointer"},
        "tableInstructionsAbsent": True,
        "pointerTableReference": {"fromVa": "0x004f584d", "type": "DATA"},
        "indexTableReference": {"fromVa": "0x004f5847", "type": "READ"},
        "pointerSlotReferences": 7,
        "computedJumpTargets": 7,
    }


def validate_ghidra(root: Path) -> dict[str, Any]:
    promotion = read_json(
        root / "local-lab/ghidra-damage-hit-semantic-live-promotion-20260809-v1/promotion/promotion.ready.json"
    )
    require(
        promotion.get("verdict") == "READY"
        and promotion.get("phase") == "LIVE_PROMOTED"
        and promotion.get("result", {}).get("functionCount") == 8124
        and promotion.get("result", {}).get("boundariesChanged") == 0
        and promotion.get("result", {}).get("bodyBytesChanged") == 0,
        "latest Ghidra promotion authority differs",
    )
    backup = read_json(
        root / "local-lab/ghidra-damage-hit-semantic-live-promotion-20260809-v1/backups/post-live/backup_manifest.json"
    )
    require(
        backup.get("schemaVersion") == "onslaught-ghidra-project-backup.v2"
        and backup.get("sourceStable") is True
        and backup.get("copyComparison", {}).get("matches") is True
        and backup.get("source") == backup.get("destination")
        and backup.get("source", {}).get("fileCount") == 19,
        "latest Ghidra POST backup is not exact and recoverable",
    )
    instructions = read_tsv(root / EVIDENCE_RELATIVE / "ghidra-readonly/instructions.tsv")
    xrefs = read_tsv(root / EVIDENCE_RELATIVE / "ghidra-readonly/xrefs.tsv")
    functions = read_tsv(
        root / "local-lab/ghidra-damage-hit-semantic-live-promotion-20260809-v1/runs-v2/live-post-inventory/functions.tsv"
    )
    return validate_ghidra_rows(instructions, xrefs, functions)


def derive(root: Path) -> dict[str, Any]:
    evidence = root / EVIDENCE_RELATIVE
    require(evidence.is_dir(), "TokenArchive evidence root is missing")
    inputs = exact_inputs(root)
    image = (root / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup").read_bytes()
    partition = validate_pristine(image)
    parent = validate_parent(root)
    history = validate_police_history(root)
    ghidra = validate_ghidra(root)
    return {
        "schema": SCHEMA,
        "verdict": "PASS",
        "claim": CLAIM,
        "specimen": {"sha256": SPECIMEN_SHA256, "role": "STATIC_BYTE_AUTHORITY_UNCHANGED"},
        "parent": parent,
        "entity": {
            "entityKey": ENTITY_KEY,
            "contractId": CONTRACT_ID,
            "questionId": QUESTION_ID,
            "previousFunction": "CTokenArchive__ReadNextToken",
            "nextFunction": "CTokenArchive__BindIndexedFieldPointer",
        },
        "partition": partition,
        "ghidra": ghidra,
        "historicalDisposition": history,
        "adjudication": {
            "classification": "DATA",
            "classificationVerdict": "STATIC_CONSUMER_BOUND_DISPATCH_TABLE_PARTITION",
            "terminalState": "TERMINAL_DATA",
            "contractState": "TERMINAL_DATA",
            "authorVerdict": "SUPPORTED_BY_PRISTINE_BYTES_AND_GHIDRA_XREFS",
            "refuterVerdict": "SURVIVED",
            "semanticPromotionApplied": False,
            "questionDisposition": "CLOSE_BASE_WITHOUT_SUCCESSOR",
        },
        "limitations": [
            "The parent residual is classified by an exact four-span partition: 18 alignment bytes and 153 consumer-bound data bytes; it is not a function.",
            "The seven pointer destinations and 125 index values are exact, but the semantic names of index categories 0 through 6 remain unassigned.",
            "The proof establishes static ownership by CTokenArchive::ReadNextToken; it does not establish runtime token-frequency or error-path behavior.",
            "The earlier small-table terminal claim remains refuted; this proof adds the missing index-length cap, consumer instructions, and Ghidra reference graph.",
            "No gameplay, TTD replay, executable write, or Ghidra mutation occurred while producing this proof.",
        ],
        "inputs": inputs,
        "author": stamp(Path(__file__), root),
    }


def validate_saved(saved: dict[str, Any], root: Path) -> None:
    fresh = derive(root)
    require(set(saved) == set(fresh) | {"generatedAtUtc"}, "proof top-level shape differs")
    generated = saved["generatedAtUtc"]
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
    root = root_path()
    ready = root / EVIDENCE_RELATIVE / READY_NAME
    try:
        if args.command == "build":
            path = build(root)
            print(f"TOKENARCHIVE_DISPATCH_REPROOF_READY {stamp(path, root)}")
        else:
            validate_saved(read_json(ready), root)
            print(f"TOKENARCHIVE_DISPATCH_REPROOF_VERIFIED {stamp(ready, root)}")
    except (ProofError, KeyError, IndexError, ValueError, OSError, struct.error) as exc:
        print(f"TOKENARCHIVE_DISPATCH_REPROOF_REFUSED {exc}", file=os.sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
