#!/usr/bin/env python3
"""Reprove the bounded 0x0050ff10 explosion-factory identity.

This tool is read-only.  It joins pristine retail bytes to a fresh read-only
Ghidra census and the sealed strict-RTTI vtable census.  It does not treat any
existing function name or narrative report as proof.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from capstone import CS_ARCH_X86, CS_MODE_32, Cs
from capstone.x86_const import X86_INS_ADD, X86_OP_IMM, X86_OP_REG, X86_REG_ESP


SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
ENTRY = 0x0050FF10
END_EXCLUSIVE = 0x0050FFA8
BODY_SHA256 = "24f43aa5cdf6fff0d9d8ec700ec2de8fb221acc3fc49af3f3738e5b596160e5b"
BODY_RANGE_SHA256 = "c8ccd2348be7a47f2d032bdd5f3b15716f327ce90683a437caafc7b0d57bd3df"
EXPECTED_CALLS = (
    0x0040E040, 0x004156C3, 0x00417A92, 0x004283C5, 0x00442741, 0x0044797D,
    0x0044CDDE, 0x0044D145, 0x0044E40E, 0x00480401, 0x00489B89, 0x0049FCA2,
    0x004BA83C, 0x004D7EFF, 0x004DA521, 0x004DA6EA, 0x004DEFDF, 0x004DFB85,
    0x004F0AB5, 0x004F1089, 0x004F4C01, 0x004F9375, 0x004F954B, 0x004FD253,
)
RESOLVER_FLOW_CALLS = (0x004DA521, 0x004DA6EA)
RESOLVER = 0x004DAA20
VTABLES = (0x005E4454, 0x005E43DC)

EXPECTED_INSPECTION_HASHES = {
    "functions.tsv": "da9f20a5ae3de150546e5b103bd9914e1a4ec7492bbafe5d35c4cc79b46d4756",
    "incoming.tsv": "bfe755cb63afb8e152f42adbe9c2940bef2fdb61de27b9f5954963423aee82b5",
    "instructions.tsv": "f9492c6f1242752bc4df282f687aa22f02177f7808c02601fbffda46c7f4759a",
    "name-census.tsv": "34558df82bd85a5fecca9876685af7fcbeca679b4e4a9e0f64d43c908b46df17",
    "outgoing.tsv": "8abd60ba53603a426c7cc52ebb7ee258f5e5274d67ba0b6e53240052e11ab931",
    "pre-comment.txt": "8d6cd69dd6ccdf0bbddcfe5db0cefe85bd7387c9576ac6d4f05912ac73a716b4",
    "program.tsv": "c29aa646da238babd81b2bd1206e3c0d6f853d74f2aca237bbb008c64be52f87",
    "summary.tsv": "ba2ca57bce3d6fdd9d4bde86ef03b3433ab3566bf4f3d1efc9076b4308f92fc8",
    "symbols.tsv": "a6ecdd15c353665a028dd0e768a6711cdb7bee432e25dc3139ddc41a85ab114a",
    "target.tsv": "f341774a26e8c70a2866eecb8efdb146b51fb31fa2b209d396f179bdd6ae33f7",
}
STRICT_READY_SHA256 = "772630978cdbb2a6b4a95613f425136002381f348917041a9289dff818dbe4d2"
STRICT_VTABLES_SHA256 = "2f1602d4c7ffffa9c2b5116c60a23d23b2f8bf923495feded54ebb67aff1f178"


class ReproofError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReproofError(message)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def read_bound(path: Path, expected: str) -> bytes:
    raw = path.read_bytes()
    require(sha256_bytes(raw) == expected, f"SHA-256 differs: {path}")
    return raw


@dataclass(frozen=True)
class Section:
    name: str
    start: int
    virtual_size: int
    raw_size: int
    raw_offset: int


class PeImage:
    def __init__(self, raw: bytes) -> None:
        require(raw[:2] == b"MZ", "specimen lacks MZ")
        pe = struct.unpack_from("<I", raw, 0x3C)[0]
        require(raw[pe : pe + 4] == b"PE\0\0", "specimen lacks PE signature")
        count = struct.unpack_from("<H", raw, pe + 6)[0]
        optional_size = struct.unpack_from("<H", raw, pe + 20)[0]
        optional = pe + 24
        require(struct.unpack_from("<H", raw, optional)[0] == 0x10B, "not PE32")
        self.image_base = struct.unpack_from("<I", raw, optional + 28)[0]
        rows = optional + optional_size
        sections: list[Section] = []
        for index in range(count):
            offset = rows + index * 40
            name = raw[offset : offset + 8].split(b"\0", 1)[0].decode("ascii")
            virtual_size, rva, raw_size, raw_offset = struct.unpack_from("<IIII", raw, offset + 8)
            require(raw_offset + raw_size <= len(raw), f"section outside file: {name}")
            sections.append(Section(name, self.image_base + rva, virtual_size, raw_size, raw_offset))
        self.raw = raw
        self.sections = tuple(sections)

    def section(self, name: str) -> Section:
        rows = [section for section in self.sections if section.name == name]
        require(len(rows) == 1, f"section count differs for {name}")
        return rows[0]

    def offset(self, va: int, size: int = 1) -> int:
        for section in self.sections:
            span = max(section.virtual_size, section.raw_size)
            if section.start <= va and va + size <= section.start + span:
                offset = section.raw_offset + va - section.start
                require(offset + size <= section.raw_offset + section.raw_size,
                    f"VA has no raw bytes: 0x{va:08x}")
                return offset
        raise ReproofError(f"VA is outside specimen sections: 0x{va:08x}")

    def bytes(self, start: int, end: int) -> bytes:
        require(end >= start, "negative byte range")
        offset = self.offset(start, end - start)
        return self.raw[offset : offset + end - start]


def direct_target(instruction) -> int | None:
    if instruction.mnemonic != "call" or len(instruction.operands) != 1:
        return None
    operand = instruction.operands[0]
    return int(operand.imm) if operand.type == X86_OP_IMM else None


def decode_exact(decoder: Cs, image: PeImage, start: int, end: int):
    rows = list(decoder.disasm(image.bytes(start, end), start))
    require(rows, f"no instructions at 0x{start:08x}")
    cursor = start
    for instruction in rows:
        require(instruction.address == cursor, f"decode gap at 0x{cursor:08x}")
        cursor += instruction.size
    require(cursor == end, f"decode does not end at 0x{end:08x}")
    return rows


def scan_direct_calls(image: PeImage, target: int) -> tuple[int, ...]:
    text = image.section(".text")
    raw = image.raw[text.raw_offset : text.raw_offset + text.raw_size]
    hits: list[int] = []
    for index in range(len(raw) - 4):
        if raw[index] != 0xE8:
            continue
        displacement = struct.unpack_from("<i", raw, index + 1)[0]
        address = text.start + index
        if address + 5 + displacement == target:
            hits.append(address)
    return tuple(hits)


def cleanup_after(decoder: Cs, image: PeImage, call: int) -> tuple[int, int]:
    rows = list(decoder.disasm(image.bytes(call + 5, call + 5 + 24), call + 5))
    for index, instruction in enumerate(rows[:5]):
        if instruction.id != X86_INS_ADD or len(instruction.operands) != 2:
            continue
        left, right = instruction.operands
        if left.type == X86_OP_REG and left.reg == X86_REG_ESP and right.type == X86_OP_IMM:
            return index, int(right.imm)
    raise ReproofError(f"no bounded caller cleanup after 0x{call:08x}")


def verify_body(image: PeImage) -> dict:
    decoder = Cs(CS_ARCH_X86, CS_MODE_32)
    decoder.detail = True
    body = image.bytes(ENTRY, END_EXCLUSIVE)
    require(len(body) == 152, "body byte count differs")
    require(sha256_bytes(body) == BODY_SHA256, "body SHA-256 differs")
    rows = decode_exact(decoder, image, ENTRY, END_EXCLUSIVE)
    require(len(rows) == 39, "body instruction count differs")
    require(rows[-1].address == 0x0050FFA7 and rows[-1].mnemonic == "ret" and not rows[-1].op_str,
        "terminal RET differs")

    expected = {
        0x0050FF2A: ("cmp", "eax, 0x32000"),
        0x0050FF32: ("cmp", "dword ptr [esp + 0x14], -1"),
        0x0050FF39: ("push", "0x109"),
        0x0050FF3E: ("push", "0x63d798"),
        0x0050FF43: ("push", "0x3f"),
        0x0050FF45: ("push", "0x94"),
        0x0050FF4F: ("call", "0x5490e0"),
        0x0050FF5A: ("test", "esi, esi"),
        0x0050FF68: ("call", "0x4f3e10"),
        0x0050FF6D: ("mov", "dword ptr [esi + 0x90], 0"),
        0x0050FF77: ("mov", "dword ptr [esi], 0x5e4454"),
        0x0050FF7D: ("mov", "dword ptr [esi + 8], 0x5e43dc"),
        0x0050FF9A: ("xor", "eax, eax"),
    }
    by_address = {row.address: row for row in rows}
    for address, pair in expected.items():
        row = by_address.get(address)
        require(row is not None and (row.mnemonic, row.op_str) == pair,
            f"semantic instruction differs at 0x{address:08x}")
    require(image.bytes(END_EXCLUSIVE, 0x0050FFB0) == b"\x90" * 8,
        "trailing eight-byte alignment pad differs")
    return {
        "start": f"0x{ENTRY:08x}",
        "endExclusive": f"0x{END_EXCLUSIVE:08x}",
        "bytes": len(body),
        "sha256": BODY_SHA256,
        "instructions": len(rows),
        "gapless": True,
        "allocationBytes": 0x94,
        "clearsOffset": "0x90",
        "constructor": "0x004f3e10",
        "vtables": [f"0x{value:08x}" for value in VTABLES],
        "failureReturnsNull": True,
    }


def verify_calls(image: PeImage) -> tuple[list[dict], dict]:
    decoder = Cs(CS_ARCH_X86, CS_MODE_32)
    decoder.detail = True
    calls = scan_direct_calls(image, ENTRY)
    require(calls == EXPECTED_CALLS, "pristine direct-call census differs")
    rows: list[dict] = []
    for call in calls:
        instruction = decode_exact(decoder, image, call, call + 5)[0]
        require(direct_target(instruction) == ENTRY, f"direct target differs at 0x{call:08x}")
        require(image.bytes(call - 1, call) == b"\x50", f"factory argument is not immediate PUSH EAX at 0x{call:08x}")
        cleanup_index, cleanup_bytes = cleanup_after(decoder, image, call)
        expected_cleanup = 8 if call in RESOLVER_FLOW_CALLS else 4
        require(cleanup_bytes == expected_cleanup, f"caller cleanup differs at 0x{call:08x}")
        rows.append({
            "callSite": f"0x{call:08x}",
            "factoryArgumentPush": f"0x{call - 1:08x}",
            "cleanupInstructionOrdinalAfterCall": cleanup_index,
            "cleanupBytes": cleanup_bytes,
            "combinedResolverCleanup": call in RESOLVER_FLOW_CALLS,
        })

    for call in RESOLVER_FLOW_CALLS:
        sequence = list(decoder.disasm(image.bytes(call - 7, call + 13), call - 7))
        by_address = {row.address: row for row in sequence}
        resolver_call = by_address.get(call - 6)
        result_push = by_address.get(call - 1)
        require(resolver_call is not None and direct_target(resolver_call) == RESOLVER,
            f"resolver call differs before 0x{call:08x}")
        require(result_push is not None and result_push.mnemonic == "push" and result_push.op_str == "eax",
            f"resolver result is not pushed into factory at 0x{call:08x}")

    return rows, {
        "directCalls": len(calls),
        "singleFactoryArgumentPushes": len(calls),
        "fourByteDedicatedCallerCleanups": len(calls) - len(RESOLVER_FLOW_CALLS),
        "eightByteCombinedTwoCallCleanups": len(RESOLVER_FLOW_CALLS),
        "resolverResultFlows": len(RESOLVER_FLOW_CALLS),
    }


def tsv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def verify_inspection(directory: Path) -> dict:
    artifacts: dict[str, dict] = {}
    for name, expected in EXPECTED_INSPECTION_HASHES.items():
        path = directory / name
        raw = read_bound(path, expected)
        artifacts[name] = {"bytes": len(raw), "sha256": expected}

    target_rows = tsv_rows(directory / "target.tsv")
    require(len(target_rows) == 1, "target census row count differs")
    row = target_rows[0]
    expected_fields = {
        "address": "0x0050ff10",
        "name": "CWorldPhysicsManager__CreatePickup",
        "fqname": "CWorldPhysicsManager__CreatePickup",
        "namespace": "Global",
        "nameSource": "USER_DEFINED",
        "signatureSource": "USER_DEFINED",
        "callingConvention": "__cdecl",
        "returnType": "void *",
        "returnStorage": "EAX:4",
        "parameterCount": "1",
        "parameterName": "pickup_type",
        "parameterType": "int",
        "parameterStorage": "Stack[0x4]:4",
        "parameterSource": "USER_DEFINED",
        "stackParameterBytes": "4",
        "customStorage": "false",
        "varArgs": "false",
        "inline": "false",
        "noReturn": "false",
        "isThunk": "false",
        "thunkTarget": "",
        "bodyRanges": "0x0050ff10-0x0050ffa7",
        "bodyBytes": "152",
        "bodyRangeSha256": BODY_RANGE_SHA256,
        "bodyBytesSha256": BODY_SHA256,
        "instructionCount": "39",
        "commentBytes": "512",
        "commentSha256": EXPECTED_INSPECTION_HASHES["pre-comment.txt"],
        "repeatableCommentBytes": "0",
        "tags": "comment-hardened,factory,pickup,retail-binary-evidence,signature-corrected,"
                "signature-recovered,static-reaudit,world-physics-manager,worldphysics-factory-tail-wave558",
    }
    for field, expected in expected_fields.items():
        require(row.get(field) == expected, f"current target {field} differs")

    incoming = tsv_rows(directory / "incoming.tsv")
    entry_rows = [item for item in incoming if item["toAddress"] == "0x0050ff10" and item["fromInTargetBody"] == "false"]
    require(len(entry_rows) == 24, "Ghidra entry-reference count differs")
    require(tuple(sorted(int(item["fromAddress"], 16) for item in entry_rows)) == EXPECTED_CALLS,
        "Ghidra/pristine caller sets differ")
    require(all(item["referenceType"] == "UNCONDITIONAL_CALL" for item in entry_rows),
        "non-call reference reaches target entry")
    external_interior = [item for item in incoming if item["toAddress"] != "0x0050ff10" and item["fromInTargetBody"] == "false"]
    require(not external_interior, "external reference reaches target interior")

    symbols = tsv_rows(directory / "symbols.tsv")
    require(len(symbols) == 1, "alias/symbol count at target differs")
    require(symbols[0]["namespace"] == "Global" and symbols[0]["type"] == "Function" and
            symbols[0]["source"] == "USER_DEFINED" and symbols[0]["primary"] == "true",
        "target symbol envelope differs")
    names = tsv_rows(directory / "name-census.tsv")
    require(len(names) == 1 and names[0]["query"] == "CWorldPhysicsManager__CreatePickup",
        "pre/post name collision census differs")

    outgoing = tsv_rows(directory / "outgoing.tsv")
    required_edges = {
        ("0x0050ff4f", "0x005490e0", "UNCONDITIONAL_CALL"),
        ("0x0050ff68", "0x004f3e10", "UNCONDITIONAL_CALL"),
        ("0x0050ff77", "0x005e4454", "DATA"),
        ("0x0050ff7d", "0x005e43dc", "DATA"),
    }
    actual_edges = {(item["fromAddress"], item["toAddress"], item["referenceType"]) for item in outgoing}
    require(required_edges <= actual_edges, "required constructor/vtable Ghidra edges differ")
    return {"artifacts": artifacts, "externalInteriorReferences": 0, "aliasesAtEntry": 0,
            "postNameCollisions": 0, "entryCallReferences": 24,
            "parameterSource": row["parameterSource"]}


def verify_strict_rtti(ready_path: Path, vtables_path: Path) -> dict:
    ready_raw = read_bound(ready_path, STRICT_READY_SHA256)
    vtables_raw = read_bound(vtables_path, STRICT_VTABLES_SHA256)
    ready = json.loads(ready_raw)
    require(ready.get("status") == "READY", "strict RTTI receipt is not READY")
    artifact = ready.get("artifacts", {}).get("vtables.tsv", {})
    require(artifact.get("bytes") == len(vtables_raw) and artifact.get("sha256") == STRICT_VTABLES_SHA256,
        "strict RTTI receipt does not bind vtables.tsv")
    rows = tsv_rows(vtables_path)
    explosion = [row for row in rows if row["class"] == "CExplosion"]
    by_table: dict[int, list[dict[str, str]]] = {}
    for row in explosion:
        by_table.setdefault(int(row["vtable_va"], 16), []).append(row)
    require(set(by_table) == set(VTABLES), "strict CExplosion vtable set differs")
    require(len(by_table[0x005E4454]) == 68 and len(by_table[0x005E43DC]) == 29,
        "strict CExplosion slot counts differ")
    return {
        "ready": {"bytes": len(ready_raw), "sha256": STRICT_READY_SHA256},
        "vtables": {"bytes": len(vtables_raw), "sha256": STRICT_VTABLES_SHA256},
        "class": "CExplosion",
        "tables": {"0x005e4454": 68, "0x005e43dc": 29},
    }


def write_call_sites(path: Path, rows: Iterable[dict]) -> None:
    require(not path.exists(), f"output exists: {path}")
    with path.open("x", encoding="utf-8", newline="") as stream:
        fields = ("callSite", "factoryArgumentPush", "cleanupInstructionOrdinalAfterCall",
                  "cleanupBytes", "combinedResolverCleanup")
        writer = csv.DictWriter(stream, delimiter="\t", fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def run(args: argparse.Namespace) -> dict:
    repository_root = Path(__file__).resolve().parent.parent
    producer_paths = {
        "reproof": Path(__file__).resolve(),
        "ghidraInspection": repository_root / "tools" / "GhidraInspectCExplosionFactoryIdentity.java",
        "fullInventory": repository_root / "tools" / "ExportFullFunctionInventory.java",
    }
    producers: dict[str, dict] = {}
    for role, path in producer_paths.items():
        raw = path.read_bytes()
        producers[role] = {
            "path": path.relative_to(repository_root).as_posix(),
            "bytes": len(raw),
            "sha256": sha256_bytes(raw),
        }
    specimen_raw = read_bound(args.specimen, SPECIMEN_SHA256)
    image = PeImage(specimen_raw)
    require(image.image_base == 0x00400000, "image base differs")
    body = verify_body(image)
    call_rows, calls = verify_calls(image)
    inspection = verify_inspection(args.inspection)
    strict_rtti = verify_strict_rtti(args.strict_ready, args.strict_vtables)

    args.output.mkdir(parents=True, exist_ok=False)
    calls_path = args.output / "call-sites.tsv"
    write_call_sites(calls_path, call_rows)
    calls_raw = calls_path.read_bytes()
    result = {
        "schema": "bea.re.cexplosion-factory-identity-reproof.v1",
        "status": "READY",
        "producers": producers,
        "specimen": {"bytes": len(specimen_raw), "sha256": SPECIMEN_SHA256},
        "target": body,
        "calls": calls,
        "callSites": {"bytes": len(calls_raw), "sha256": sha256_bytes(calls_raw)},
        "currentGhidra": inspection,
        "strictRtti": strict_rtti,
        "conclusion": {
            "boundedIdentity": "CWorldPhysicsManager__CreateExplosion",
            "signature": "void * __cdecl CWorldPhysicsManager__CreateExplosion(int explosion_definition_index)",
            "confidenceCeiling": "C1_STATIC",
            "runtimeSemanticsAuthorized": False,
            "rebuildReadyAuthorized": False,
        },
        "limitations": [
            "The explosion identity is bounded by strict RTTI, construction, and all direct callers; exact source spelling remains open.",
            "The parameter is an explosion-definition ordinal; the proposed parameter name is descriptive, not recovered source spelling.",
            "Runtime reachability, later effects, failure frequency, and general rebuild parity remain open.",
        ],
    }
    ready_path = args.output / "reproof.ready.json"
    ready_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return result


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--specimen", type=Path, required=True)
    result.add_argument("--inspection", type=Path, required=True)
    result.add_argument("--strict-ready", type=Path, required=True)
    result.add_argument("--strict-vtables", type=Path, required=True)
    result.add_argument("--output", type=Path, required=True)
    return result


def main() -> int:
    args = parser().parse_args()
    result = run(args)
    print("CEXPLOSION_FACTORY_IDENTITY_REPROOF_READY "
          f"calls={result['calls']['directCalls']} bodyBytes={result['target']['bytes']} ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
