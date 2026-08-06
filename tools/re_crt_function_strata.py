#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Derive exact Ghidra-envelope strata for the clean CRT 520 cohort.

This owner does not authorize a mutation.  It binds the pristine specimen, the
clean-520 residual boundary, and a separately verified formal two-range canary
proof; decodes every candidate body from retail bytes; distinguishes ordinary
RET bodies, ECX-load tail-jump cleanup bodies, and true one-instruction thunks;
then emits a 98-entry graph-aware risk pilot and the complete 520-entry manifest.
Both manifests remain prospective scratch-project hypotheses.
"""

from __future__ import annotations

import argparse
from collections import Counter
import csv
from dataclasses import dataclass
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Iterable, Mapping, Sequence

from capstone import Cs, CS_ARCH_X86, CS_GRP_CALL, CS_GRP_JUMP, CS_GRP_RET, CS_MODE_32
from capstone.x86 import X86_INS_JMP, X86_OP_IMM, X86_OP_REG, X86_REG_ECX

TOOLS_DIRECTORY = Path(__file__).resolve().parent
if str(TOOLS_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIRECTORY))

try:
    import ghidra_function_envelope_proof as envelope
    from re_rtti_vtables import PEImage
except ModuleNotFoundError:  # supports imports from repository root
    from tools import ghidra_function_envelope_proof as envelope
    from tools.re_rtti_vtables import PEImage


SCHEMA = "bea.re.crt-function-envelope-strata.v2"
READY_SCHEMA = "bea.re.crt-function-envelope-strata-ready.v2"
STATUS = "READY"
OWNER_NAME = "crt-function-strata-owner.py"

PRISTINE_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
BOUNDARY_READY_SHA256 = "53ab9de5bc113ad45d593f3732627860f2639c819d21c771d8369d139a4c6832"
BOUNDARY_TSV_SHA256 = "101f9a24cec637f6790db60284bccff81283ae5a2cf85982e26d2d5c90c4832f"
DETAILS_SHA256 = "f3830c816677b3dcd6f2794e218cc8b073570e2de7786f485b6701068387f220"
BASE_FUNCTIONS_SHA256 = "26977c69e3530ff9344c6456b3a0dac218775eaf0c1043ac2c89c6a9b95ab368"

EXPECTED_KIND_COUNTS = {
    "DIRECT_JMP_THUNK": 2,
    "ECX_LOAD_TAIL_JUMP": 65,
    "RET_TERMINATED": 453,
}
EXPECTED_COHORT_COUNTS = {
    "direct_call_closure": 1,
    "initializer": 449,
    "onexit_registration": 70,
}
EXPECTED_FULL_COUNT = 520
EXPECTED_FULL_BYTES = 58157
EXPECTED_FULL_INSTRUCTIONS = 10782
EXPECTED_SHAPES = 31
EXPECTED_PILOT_COUNT = 98
EXPECTED_DIRECT_CALLS = 128
EXPECTED_DIRECT_CALL_TARGETS = 24
EXPECTED_TAIL_JUMPS = 67
EXPECTED_TAIL_TARGETS = 21
EXPECTED_SIDE_TAIL_TARGET_KINDS = {False: 14, True: 51}
EXPECTED_TRUE_THUNKS = {
    0x00518BE0: 0x00518BF0,
    0x0052FF20: 0x0052FF30,
}
EXPECTED_INTERNAL_BRANCH_TARGETS = {
    0x00441630: (0x00441664,),
    0x00449670: (0x0044967D, 0x00449696),
    0x004BC1E0: (0x004BC21F, 0x004BC22A),
    0x004F5F30: (0x004F5F3C,),
    0x00542840: (0x0054284C,),
}
GRAPH_AWARE_MINIMUM = (
    0x00402080, 0x00404CE0, 0x0040F4E0, 0x00426D20, 0x004295A0,
    0x00440AC0, 0x00441620, 0x00441630, 0x004424A0, 0x00449670,
    0x0044AF90, 0x00453090, 0x0045A910, 0x004710C0, 0x00491880,
    0x004B5220, 0x004BC1E0, 0x004CBFC0, 0x004F5F30, 0x00501650,
    0x005152C0, 0x005154B0, 0x00515F30, 0x005168A0, 0x00518BE0,
    0x0051FE80, 0x00527930, 0x0052FF20, 0x0053A2D0, 0x0053A330,
    0x0053D340, 0x005412D0, 0x00542840, 0x00564FD6,
)
GRAPH_AWARE_MINIMUM_SHA256 = "515db6b5d6fdfd231d0d4badbd95a92f44256b4f73239bf6877c8252daad0354"

BOUNDARY_COLUMNS = (
    "address", "endExclusive", "bytes", "bytesSha256", "cohort",
    "residualEntityKey", "questionId", "contractId", "lineageKinds",
    "promotionLane",
)
DETAIL_COLUMNS = (
    "strength", "cohort", "entry", "endExclusive", "length",
    "bytesSha256", "instructionCount", "listingState", "observedBytes",
)
STRATA_COLUMNS = (
    "entry", "endExclusive", "bodyBytes", "bodyBytesSha256",
    "instructionCount", "cohort", "terminalKind", "tailTarget",
    "tailTargetBaseIsThunk", "internalBranchTargets", "directCallTargets",
    "expectedIsThunk", "expectedThunkTarget", "shapeKey", "pilotSelected",
    "residualEntityKey", "questionId", "contractId", "lineageKinds",
)
OUTPUT_NAMES = (
    OWNER_NAME,
    "crt520-strata.tsv",
    "crt520-stratified-pilot.tsv",
    "crt520-full.tsv",
    "strata-summary.json",
)


class StrataError(ValueError):
    """An input or derived manifest violates the specimen-bound contract."""


@dataclass(frozen=True)
class Target:
    entry: int
    end: int
    body_sha256: str
    instruction_count: int
    cohort: str
    terminal_kind: str
    tail_target: int | None
    shape_key: str
    residual_entity_key: str
    question_id: str
    contract_id: str
    lineage_kinds: str
    internal_branch_targets: tuple[int, ...] = ()
    direct_call_targets: tuple[int, ...] = ()
    tail_target_base_is_thunk: bool | None = None

    @property
    def body_bytes(self) -> int:
        return self.end - self.entry

    @property
    def expected_is_thunk(self) -> bool:
        return self.terminal_kind == "DIRECT_JMP_THUNK"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8")


def duplicate_key(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise StrataError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json(data: bytes, role: str) -> object:
    try:
        return json.loads(data.decode("utf-8"), object_pairs_hook=duplicate_key)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise StrataError(f"{role} is not strict UTF-8 JSON: {error}") from error


def plain_file(path: Path, role: str, expected_hash: str | None = None) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise StrataError(f"{role} is not a plain file: {path}")
    data = path.read_bytes()
    if expected_hash is not None and sha256_bytes(data) != expected_hash:
        raise StrataError(f"{role} SHA-256 differs")
    return data


def parse_tsv(data: bytes, columns: Sequence[str], role: str) -> list[dict[str, str]]:
    if not data or not data.endswith(b"\n") or b"\r" in data or data.endswith(b"\n\n"):
        raise StrataError(f"{role} is not canonical LF TSV")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise StrataError(f"{role} is not UTF-8: {error}") from error
    reader = csv.DictReader(io.StringIO(text, newline=""), delimiter="\t")
    if tuple(reader.fieldnames or ()) != tuple(columns):
        raise StrataError(f"{role} header differs")
    rows: list[dict[str, str]] = []
    for number, row in enumerate(reader, start=2):
        if None in row or any(value is None for value in row.values()):
            raise StrataError(f"{role} row {number} has a shifted field count")
        rows.append(dict(row))
    if not rows:
        raise StrataError(f"{role} has no rows")
    return rows


def render_tsv(columns: Sequence[str], rows: Iterable[Mapping[str, object]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(
        stream,
        fieldnames=list(columns),
        delimiter="\t",
        lineterminator="\n",
        extrasaction="raise",
    )
    writer.writeheader()
    for row in rows:
        writer.writerow({column: row[column] for column in columns})
    return stream.getvalue().encode("utf-8")


def va(address: int) -> str:
    return f"0x{address:08x}"


def default_paths(repo: Path) -> dict[str, Path]:
    cohort = repo / "local-lab" / "crt-recursive-cohort-2026-08-02"
    boundary = cohort / "clean520-boundary-v3-canary-refuted"
    return {
        "specimen": repo / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup",
        "boundaryReady": boundary / "boundary-targets.ready.json",
        "boundaryTsv": boundary / "boundary-targets.tsv",
        "details": cohort / "architect" / "body-projection-details.tsv",
    }


def validate_boundary_ready(data: bytes) -> dict[str, object]:
    value = parse_json(data, "boundary READY")
    if not isinstance(value, dict):
        raise StrataError("boundary READY root is not an object")
    if value.get("schema") != "bea.re.crt-text-residual-boundary-targets.v2":
        raise StrataError("boundary READY schema differs")
    if value.get("count") != EXPECTED_FULL_COUNT or value.get("bytes") != EXPECTED_FULL_BYTES:
        raise StrataError("boundary READY count/bytes differ")
    selection = value.get("selection")
    if not isinstance(selection, dict) or selection.get("batchAuthorized") is not False:
        raise StrataError("boundary READY no longer carries the blocked batch gate")
    if selection.get("canaryAdjudication") != "REFUTED_ORIGINAL_ONE_RESIDUAL_BODY":
        raise StrataError("boundary READY canary lineage differs")
    outputs = value.get("outputs")
    entry = outputs.get("boundary-targets.tsv") if isinstance(outputs, dict) else None
    if not isinstance(entry, dict) or entry.get("sha256") != BOUNDARY_TSV_SHA256:
        raise StrataError("boundary READY does not bind the exact target TSV")
    return value


def validate_formal_proof(repo: Path, ready_path: Path) -> tuple[dict[str, object], bytes, bytes]:
    ready_path = ready_path.resolve()
    local_lab = (repo / "local-lab").resolve()
    if ready_path.name != "proof.ready.json" or ready_path.parent.parent != local_lab:
        raise StrataError("formal proof READY must be in one direct local-lab child")
    ready_data = plain_file(ready_path, "formal proof READY")
    # This is deliberately the expensive independent verifier: it reopens all
    # retained clones and does not trust the READY's labels.
    envelope.verify_ready(ready_path)
    ready = parse_json(ready_data, "formal proof READY")
    if not isinstance(ready, dict) or ready.get("status") != "READY" or ready.get("verdict") != "SURVIVED":
        raise StrataError("formal proof did not survive")
    checks = ready.get("checks")
    if not isinstance(checks, dict) or checks.get("batch520Authorized") is not False:
        raise StrataError("formal proof improperly claims batch authority")
    base = ready_path.parent / "inputs" / "base-functions.tsv"
    base_data = plain_file(base, "formal proof base inventory", BASE_FUNCTIONS_SHA256)
    return ready, ready_data, base_data


def base_function_info(data: bytes) -> dict[int, bool]:
    if not data.endswith(b"\n") or b"\r" in data:
        raise StrataError("base function inventory is not canonical TSV")
    reader = csv.DictReader(io.StringIO(data.decode("utf-8"), newline=""), delimiter="\t")
    if not reader.fieldnames or not {"address", "isThunk"}.issubset(reader.fieldnames):
        raise StrataError("base function inventory lacks address/isThunk")
    functions: dict[int, bool] = {}
    for row in reader:
        address = int(row["address"], 16)
        if address in functions:
            raise StrataError(f"base inventory repeats {va(address)}")
        if row["isThunk"] not in {"true", "false"}:
            raise StrataError(f"base inventory has non-boolean isThunk at {va(address)}")
        functions[address] = row["isThunk"] == "true"
    if len(functions) != envelope.BASE_FUNCTION_COUNT:
        raise StrataError("base function count differs")
    return functions


def base_function_starts(data: bytes) -> set[int]:
    """Compatibility view for callers that need only exact base entries."""
    return set(base_function_info(data))


def classify(instructions: Sequence[object], raw: bytes, entry: int) -> tuple[str, int | None]:
    if not instructions:
        raise StrataError(f"empty body at {va(entry)}")
    last = instructions[-1]
    if len(instructions) == 1 and last.id == X86_INS_JMP:
        if raw[:1] != b"\xe9" or not last.operands or last.operands[0].type != X86_OP_IMM:
            raise StrataError(f"unsupported single-instruction jump at {va(entry)}")
        return "DIRECT_JMP_THUNK", last.operands[0].imm & 0xFFFFFFFF
    if last.id == X86_INS_JMP:
        if (
            len(instructions) != 2
            or not last.operands
            or last.operands[0].type != X86_OP_IMM
            or instructions[0].mnemonic != "mov"
            or len(instructions[0].operands) != 2
            or instructions[0].operands[0].type != X86_OP_REG
            or instructions[0].operands[0].reg != X86_REG_ECX
            or instructions[0].operands[1].type != X86_OP_IMM
        ):
            raise StrataError(f"unsupported side-effect tail jump at {va(entry)}")
        return "ECX_LOAD_TAIL_JUMP", last.operands[0].imm & 0xFFFFFFFF
    if last.group(CS_GRP_RET):
        return "RET_TERMINATED", None
    raise StrataError(f"unsupported terminal instruction at {va(entry)}: {last.mnemonic}")


def derive_targets(
    specimen: bytes,
    boundary_rows: Sequence[Mapping[str, str]],
    detail_rows: Sequence[Mapping[str, str]],
    existing_functions: Mapping[int, bool],
) -> list[Target]:
    if sha256_bytes(specimen) != PRISTINE_SHA256:
        raise StrataError("specimen SHA-256 differs")
    image = PEImage(specimen)
    decoder = Cs(CS_ARCH_X86, CS_MODE_32)
    decoder.detail = True
    details = {int(row["entry"], 16): row for row in detail_rows}
    if len(details) != len(detail_rows):
        raise StrataError("body details repeat an entry")
    targets: list[Target] = []
    seen: set[int] = set()
    previous_end: int | None = None
    for row in boundary_rows:
        entry = int(row["address"], 16)
        end = int(row["endExclusive"], 16)
        if entry in seen or entry >= end or (previous_end is not None and entry <= previous_end):
            raise StrataError(f"boundary order/overlap differs at {va(entry)}")
        seen.add(entry)
        previous_end = end
        detail = details.get(entry)
        if detail is None:
            raise StrataError(f"missing body details for {va(entry)}")
        if (
            detail["strength"] != "HARD"
            or detail["listingState"] != "INSTRUCTION_PRESENT"
            or detail["cohort"] != row["cohort"]
            or int(detail["endExclusive"], 16) != end
            or int(detail["length"]) != end - entry
            or int(detail["observedBytes"]) != end - entry
            or detail["bytesSha256"] != row["bytesSha256"]
            or int(row["bytes"]) != end - entry
        ):
            raise StrataError(f"boundary/detail lineage differs at {va(entry)}")
        offset = image.va_to_file(entry, end - entry)
        if offset is None:
            raise StrataError(f"body is not file-backed at {va(entry)}")
        raw = specimen[offset:offset + end - entry]
        if sha256_bytes(raw) != row["bytesSha256"]:
            raise StrataError(f"body bytes differ at {va(entry)}")
        instructions = list(decoder.disasm(raw, entry))
        if (
            not instructions
            or instructions[0].address != entry
            or instructions[-1].address + instructions[-1].size != end
            or sum(item.size for item in instructions) != len(raw)
            or any(
                left.address + left.size != right.address
                for left, right in zip(instructions, instructions[1:])
            )
        ):
            raise StrataError(f"Capstone coverage is not exact at {va(entry)}")
        if len(instructions) != int(detail["instructionCount"]):
            raise StrataError(f"instruction count differs at {va(entry)}")
        instruction_addresses = {item.address for item in instructions}
        internal_branch_targets: list[int] = []
        direct_call_targets: list[int] = []
        for instruction in instructions:
            if instruction.group(CS_GRP_CALL):
                if not instruction.operands or instruction.operands[0].type != X86_OP_IMM:
                    raise StrataError(f"indirect CALL in clean body at {va(instruction.address)}")
                target = instruction.operands[0].imm & 0xFFFFFFFF
                if target not in existing_functions:
                    raise StrataError(
                        f"CALL target is not an existing function: {va(instruction.address)} -> {va(target)}"
                    )
                direct_call_targets.append(target)
            if instruction.group(CS_GRP_JUMP) and instruction is not instructions[-1]:
                if not instruction.operands or instruction.operands[0].type != X86_OP_IMM:
                    raise StrataError(f"indirect/internal jump in clean body at {va(instruction.address)}")
                target = instruction.operands[0].imm & 0xFFFFFFFF
                if not entry <= target < end or target not in instruction_addresses:
                    raise StrataError(
                        f"branch escapes or splits an instruction: {va(instruction.address)} -> {va(target)}"
                    )
                internal_branch_targets.append(target)
        terminal_kind, tail_target = classify(instructions, raw, entry)
        if tail_target is not None and tail_target not in existing_functions:
            raise StrataError(f"tail target is not an existing function: {va(entry)} -> {va(tail_target)}")
        shape_key = (
            f"{row['cohort']}|{terminal_kind}|bytes={len(raw)}|"
            f"instructions={len(instructions)}"
        )
        targets.append(Target(
            entry=entry,
            end=end,
            body_sha256=row["bytesSha256"],
            instruction_count=len(instructions),
            cohort=row["cohort"],
            terminal_kind=terminal_kind,
            tail_target=tail_target,
            shape_key=shape_key,
            residual_entity_key=row["residualEntityKey"],
            question_id=row["questionId"],
            contract_id=row["contractId"],
            lineage_kinds=row["lineageKinds"],
            internal_branch_targets=tuple(sorted(set(internal_branch_targets))),
            direct_call_targets=tuple(direct_call_targets),
            tail_target_base_is_thunk=(
                existing_functions[tail_target] if tail_target is not None else None
            ),
        ))
    if len(targets) != EXPECTED_FULL_COUNT or sum(item.body_bytes for item in targets) != EXPECTED_FULL_BYTES:
        raise StrataError("full cohort count/bytes differ")
    kind_counts = Counter(item.terminal_kind for item in targets)
    cohort_counts = Counter(item.cohort for item in targets)
    if dict(sorted(kind_counts.items())) != EXPECTED_KIND_COUNTS:
        raise StrataError(f"terminal-kind counts differ: {dict(kind_counts)}")
    if dict(sorted(cohort_counts.items())) != EXPECTED_COHORT_COUNTS:
        raise StrataError(f"cohort counts differ: {dict(cohort_counts)}")
    true_thunks = {
        item.entry: item.tail_target
        for item in targets if item.terminal_kind == "DIRECT_JMP_THUNK"
    }
    if true_thunks != EXPECTED_TRUE_THUNKS:
        raise StrataError(f"true thunk identities differ: {true_thunks}")
    if len({item.shape_key for item in targets}) != EXPECTED_SHAPES:
        raise StrataError("shape count differs")
    if sum(item.instruction_count for item in targets) != EXPECTED_FULL_INSTRUCTIONS:
        raise StrataError("full instruction count differs")
    internal = {
        item.entry: item.internal_branch_targets
        for item in targets if item.internal_branch_targets
    }
    if internal != EXPECTED_INTERNAL_BRANCH_TARGETS:
        raise StrataError(f"internal branch graph differs: {internal}")
    call_targets = [target for item in targets for target in item.direct_call_targets]
    if len(call_targets) != EXPECTED_DIRECT_CALLS or len(set(call_targets)) != EXPECTED_DIRECT_CALL_TARGETS:
        raise StrataError("direct CALL dependency census differs")
    tail_targets = [item.tail_target for item in targets if item.tail_target is not None]
    if len(tail_targets) != EXPECTED_TAIL_JUMPS or len(set(tail_targets)) != EXPECTED_TAIL_TARGETS:
        raise StrataError("terminal JMP dependency census differs")
    target_entries = {item.entry for item in targets}
    if target_entries.intersection(call_targets) or target_entries.intersection(tail_targets):
        raise StrataError("a CALL/JMP dependency unexpectedly targets another batch entry")
    side_target_kinds = Counter(
        item.tail_target_base_is_thunk
        for item in targets if item.terminal_kind == "ECX_LOAD_TAIL_JUMP"
    )
    if dict(side_target_kinds) != EXPECTED_SIDE_TAIL_TARGET_KINDS:
        raise StrataError(f"side-tail target-kind split differs: {dict(side_target_kinds)}")
    return targets


def select_pilot(
    targets: Sequence[Target],
    graph_minimum: Sequence[int] = GRAPH_AWARE_MINIMUM,
) -> set[int]:
    selected = {
        item.entry for item in targets if item.terminal_kind != "RET_TERMINATED"
    }
    ret_representatives: dict[str, int] = {}
    for item in targets:
        if item.terminal_kind == "RET_TERMINATED":
            ret_representatives.setdefault(item.shape_key, item.entry)
    selected.update(ret_representatives.values())
    graph_minimum_bytes = "".join(f"{va(entry)}\n" for entry in graph_minimum).encode("ascii")
    if tuple(graph_minimum) == GRAPH_AWARE_MINIMUM and sha256_bytes(graph_minimum_bytes) != GRAPH_AWARE_MINIMUM_SHA256:
        raise StrataError("graph-aware minimum address-list digest differs")
    available = {item.entry for item in targets}
    if not set(graph_minimum).issubset(available):
        raise StrataError("graph-aware minimum contains an entry outside clean520")
    selected.update(graph_minimum)
    if tuple(graph_minimum) == GRAPH_AWARE_MINIMUM and len(selected) != EXPECTED_PILOT_COUNT:
        raise StrataError(f"pilot count differs: {len(selected)}")
    return selected


def manifest_bytes(targets: Sequence[Target], lane_prefix: str) -> bytes:
    rows: list[str] = [envelope.MANIFEST_HEADER]
    for item in targets:
        expected_range = f"{va(item.entry)}-{va(item.end)}"
        fields = (
            va(item.entry),
            expected_range,
            str(item.body_bytes),
            envelope.canonical_range_digest([(item.entry, item.end)]),
            item.body_sha256,
            str(item.instruction_count),
            str(item.expected_is_thunk).lower(),
            va(item.tail_target) if item.expected_is_thunk and item.tail_target is not None else "",
            ";".join(va(target) for target in item.internal_branch_targets),
            item.residual_entity_key,
            item.question_id,
            item.contract_id,
            f"{lane_prefix}_{item.terminal_kind}",
        )
        if any("\t" in value or "\n" in value or "\r" in value for value in fields):
            raise StrataError(f"manifest field contains control text at {va(item.entry)}")
        rows.append("\t".join(fields))
    return ("\n".join(rows) + "\n").encode("utf-8")


def derive_outputs(
    specimen: bytes,
    boundary_data: bytes,
    detail_data: bytes,
    base_functions: bytes,
    input_stamps: Mapping[str, Mapping[str, object]],
) -> tuple[dict[str, bytes], dict[str, object]]:
    boundary_rows = parse_tsv(boundary_data, BOUNDARY_COLUMNS, "boundary targets")
    detail_rows = parse_tsv(detail_data, DETAIL_COLUMNS, "body projection details")
    targets = derive_targets(
        specimen,
        boundary_rows,
        detail_rows,
        base_function_info(base_functions),
    )
    pilot_entries = select_pilot(targets)
    pilot = [item for item in targets if item.entry in pilot_entries]
    strata_rows = []
    for item in targets:
        strata_rows.append({
            "entry": va(item.entry),
            "endExclusive": va(item.end),
            "bodyBytes": item.body_bytes,
            "bodyBytesSha256": item.body_sha256,
            "instructionCount": item.instruction_count,
            "cohort": item.cohort,
            "terminalKind": item.terminal_kind,
            "tailTarget": va(item.tail_target) if item.tail_target is not None else "",
            "tailTargetBaseIsThunk": (
                "" if item.tail_target_base_is_thunk is None
                else str(item.tail_target_base_is_thunk).lower()
            ),
            "internalBranchTargets": ";".join(
                va(target) for target in item.internal_branch_targets
            ),
            "directCallTargets": ";".join(
                va(target) for target in item.direct_call_targets
            ),
            "expectedIsThunk": str(item.expected_is_thunk).lower(),
            "expectedThunkTarget": va(item.tail_target) if item.expected_is_thunk and item.tail_target is not None else "",
            "shapeKey": item.shape_key,
            "pilotSelected": str(item.entry in pilot_entries).lower(),
            "residualEntityKey": item.residual_entity_key,
            "questionId": item.question_id,
            "contractId": item.contract_id,
            "lineageKinds": item.lineage_kinds,
        })
    summary = {
        "schema": SCHEMA,
        "status": STATUS,
        "inputs": dict(input_stamps),
        "counts": {
            "fullTargets": len(targets),
            "fullBodyBytes": sum(item.body_bytes for item in targets),
            "pilotTargets": len(pilot),
            "shapeKeys": len({item.shape_key for item in targets}),
            "fullInstructions": sum(item.instruction_count for item in targets),
            "directCalls": sum(len(item.direct_call_targets) for item in targets),
            "distinctDirectCallTargets": len({
                target for item in targets for target in item.direct_call_targets
            }),
            "terminalJumps": sum(item.tail_target is not None for item in targets),
            "distinctTerminalJumpTargets": len({
                item.tail_target for item in targets if item.tail_target is not None
            }),
            "internalBranches": sum(len(item.internal_branch_targets) for item in targets),
            "terminalKinds": dict(sorted(Counter(item.terminal_kind for item in targets).items())),
            "cohorts": dict(sorted(Counter(item.cohort for item in targets).items())),
            "pilotTerminalKinds": dict(sorted(Counter(item.terminal_kind for item in pilot).items())),
        },
        "trueThunks": [
            {"entry": va(item.entry), "target": va(item.tail_target or 0)}
            for item in targets if item.expected_is_thunk
        ],
        "dependencyGraph": {
            "internalBranchTargets": {
                va(item.entry): [va(target) for target in item.internal_branch_targets]
                for item in targets if item.internal_branch_targets
            },
            "sideTailTargetBaseKinds": {
                "ordinary": sum(
                    item.terminal_kind == "ECX_LOAD_TAIL_JUMP"
                    and item.tail_target_base_is_thunk is False
                    for item in targets
                ),
                "thunk": sum(
                    item.terminal_kind == "ECX_LOAD_TAIL_JUMP"
                    and item.tail_target_base_is_thunk is True
                    for item in targets
                ),
            },
            "batchEntriesTargetedByDirectCallOrTerminalJump": 0,
        },
        "selection": {
            "pilotRule": "all non-RET bodies plus the lowest-address representative of every RET shapeKey, union the independently derived 34-entry graph-aware minimum",
            "shapeKey": "cohort|terminalKind|bodyBytes|instructionCount",
            "graphAwareMinimumTargets": len(GRAPH_AWARE_MINIMUM),
            "graphAwareMinimumSha256": GRAPH_AWARE_MINIMUM_SHA256,
            "pilotAuthorized": False,
            "fullScratchAuthorized": False,
            "livePromotionAuthorized": False,
        },
        "claimBoundary": [
            "The formal two-range canary proves the envelope instrument on two disposable clone pairs; it explicitly does not authorize this 520-entry cohort.",
            "The 98-entry pilot includes both true thunks, all 65 ECX-load tail-jump bodies, one deterministic representative of every RET shape, and every entry in the independent 34-entry graph-aware minimum.",
            "Seven internal branch targets are forbidden function entries so natural inference must keep the five conditional bodies contiguous.",
            "Shape equality is a targeting heuristic, not proof that omitted members infer the same Ghidra body; a full 520 scratch probe remains mandatory.",
            "Expected function kinds are pristine-byte hypotheses until separate probe/apply/reopen receipts survive on fresh disposable projects.",
            "No semantic names, signatures, contracts, live Ghidra mutation, or rebuild parity follow from these manifests.",
        ],
    }
    outputs = {
        "crt520-strata.tsv": render_tsv(STRATA_COLUMNS, strata_rows),
        "crt520-stratified-pilot.tsv": manifest_bytes(pilot, "CRT520_STRATIFIED_PILOT"),
        "crt520-full.tsv": manifest_bytes(targets, "CRT520_FULL_SCRATCH"),
        "strata-summary.json": canonical_json(summary),
    }
    return outputs, summary


def source_stamp(path: Path, data: bytes, repo: Path) -> dict[str, object]:
    try:
        relative = path.resolve().relative_to(repo.resolve()).as_posix()
    except ValueError:
        relative = str(path.resolve())
    return {"path": relative, "bytes": len(data), "sha256": sha256_bytes(data)}


def load_and_derive(repo: Path, proof_ready: Path) -> tuple[dict[str, bytes], dict[str, object]]:
    paths = default_paths(repo)
    specimen = plain_file(paths["specimen"], "pristine specimen", PRISTINE_SHA256)
    boundary_ready_data = plain_file(paths["boundaryReady"], "boundary READY", BOUNDARY_READY_SHA256)
    validate_boundary_ready(boundary_ready_data)
    boundary_data = plain_file(paths["boundaryTsv"], "boundary targets", BOUNDARY_TSV_SHA256)
    detail_data = plain_file(paths["details"], "body projection details", DETAILS_SHA256)
    _, proof_data, base_data = validate_formal_proof(repo, proof_ready)
    inputs = {
        "specimen": source_stamp(paths["specimen"], specimen, repo),
        "boundaryReady": source_stamp(paths["boundaryReady"], boundary_ready_data, repo),
        "boundaryTargets": source_stamp(paths["boundaryTsv"], boundary_data, repo),
        "bodyProjectionDetails": source_stamp(paths["details"], detail_data, repo),
        "formalEnvelopeProof": source_stamp(proof_ready, proof_data, repo),
        "baseFunctions": source_stamp(proof_ready.parent / "inputs" / "base-functions.tsv", base_data, repo),
    }
    outputs, summary = derive_outputs(specimen, boundary_data, detail_data, base_data, inputs)
    return outputs, summary


def expected_ready(
    owner: bytes,
    dependencies: Mapping[str, bytes],
    outputs: Mapping[str, bytes],
    summary: Mapping[str, object],
) -> dict[str, object]:
    published = {OWNER_NAME: owner, **outputs}
    return {
        "schema": READY_SCHEMA,
        "status": STATUS,
        "ownerSha256": sha256_bytes(owner),
        "dependencies": {
            name: {"bytes": len(data), "sha256": sha256_bytes(data)}
            for name, data in sorted(dependencies.items())
        },
        "inputs": summary["inputs"],
        "counts": summary["counts"],
        "selection": summary["selection"],
        "outputs": {
            name: {"bytes": len(data), "sha256": sha256_bytes(data)}
            for name, data in sorted(published.items())
        },
    }


def dependency_bytes() -> dict[str, bytes]:
    tools = Path(__file__).resolve().parent
    return {
        "ghidra_function_envelope_proof.py": plain_file(
            tools / "ghidra_function_envelope_proof.py", "envelope dependency"
        ),
        "re_rtti_vtables.py": plain_file(tools / "re_rtti_vtables.py", "PE dependency"),
    }


def build_bundle(repo: Path, proof_ready: Path, out: Path) -> dict[str, object]:
    if out.exists() or out.is_symlink():
        raise StrataError(f"output already exists: {out}")
    owner = plain_file(Path(__file__).resolve(), "owner")
    dependencies = dependency_bytes()
    outputs, summary = load_and_derive(repo, proof_ready)
    ready = expected_ready(owner, dependencies, outputs, summary)
    out.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=f".{out.name}-", dir=out.parent))
    try:
        (staging / OWNER_NAME).write_bytes(owner)
        for name, data in outputs.items():
            (staging / name).write_bytes(data)
        (staging / "READY.json").write_bytes(canonical_json(ready))
        os.replace(staging, out)
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
    return ready


def verify_bundle(repo: Path, proof_ready: Path, bundle: Path) -> dict[str, object]:
    if bundle.is_symlink() or not bundle.is_dir():
        raise StrataError(f"bundle is not a plain directory: {bundle}")
    expected_names = set(OUTPUT_NAMES) | {"READY.json"}
    members = list(bundle.iterdir())
    actual_names = {item.name for item in members}
    if actual_names != expected_names:
        raise StrataError(
            f"bundle members differ: missing={sorted(expected_names - actual_names)} "
            f"extra={sorted(actual_names - expected_names)}"
        )
    if any(item.is_symlink() or not item.is_file() for item in members):
        raise StrataError("bundle contains a non-plain member")
    owner = plain_file(Path(__file__).resolve(), "executed owner")
    if (bundle / OWNER_NAME).read_bytes() != owner:
        raise StrataError("frozen owner differs from the verifier")
    dependencies = dependency_bytes()
    outputs, summary = load_and_derive(repo, proof_ready)
    expected = expected_ready(owner, dependencies, outputs, summary)
    ready_data = (bundle / "READY.json").read_bytes()
    published = parse_json(ready_data, "READY.json")
    if not isinstance(published, dict) or canonical_json(published) != ready_data:
        raise StrataError("READY.json is not canonical JSON")
    if published != expected:
        raise StrataError("READY semantics differ from fresh derivation")
    for name, data in {OWNER_NAME: owner, **outputs}.items():
        if (bundle / name).read_bytes() != data:
            raise StrataError(f"published output differs: {name}")
    return expected


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build")
    build.add_argument("--proof-ready", required=True, type=Path)
    build.add_argument("--out", required=True, type=Path)
    verify = commands.add_parser("verify")
    verify.add_argument("--proof-ready", required=True, type=Path)
    verify.add_argument("--bundle", required=True, type=Path)
    arguments = parser.parse_args(argv)
    try:
        repo = arguments.repo_root.resolve()
        if arguments.command == "build":
            result = build_bundle(repo, arguments.proof_ready.resolve(), arguments.out.resolve())
        else:
            result = verify_bundle(repo, arguments.proof_ready.resolve(), arguments.bundle.resolve())
    except (StrataError, envelope.ProofError, OSError, ValueError) as error:
        print(f"REFUSED: {error}", file=sys.stderr)
        return 2
    counts = result["counts"]
    print(
        f"READY: {counts['fullTargets']} targets / {counts['fullBodyBytes']} bytes; "
        f"pilot={counts['pilotTargets']} shapes={counts['shapeKeys']}; "
        "batch authority=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
