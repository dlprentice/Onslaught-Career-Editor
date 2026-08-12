#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Prove five collision-component implementation identities in PC retail.

This proof is static and read-only.  It binds pristine retail bytes, the latest
verified live-Ghidra inventory, strict RTTI/vtable placement, supplied source,
legacy instruction/xref exports, and the normalized-identical PC demo map.  It
proves bounded implementation-owner and role labels; it does not exclude
identical-code-folded derived aliases or prove runtime collision behavior.
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
from typing import Any, Iterable


SCHEMA = "bea.re.collision-component-identity-reproof.v1"
CLAIM = "PC_RETAIL_COLLISION_COMPONENT_IMPLEMENTATION_IDENTITIES"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
EVIDENCE_RELATIVE = Path("local-lab/collision-component-identity-reproof-20260812-v1")
READY_NAME = "proof.ready.json"

INPUTS: dict[str, tuple[int, str]] = {
    "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup":
        (2_506_752, SPECIMEN_SHA256),
    "references/Onslaught/thing.cpp":
        (19_657, "e930244e01fbad5fe7e15c2595ce595282fb4c982a469cf604e5b9e0de09727e"),
    "references/Onslaught/InitThing.h":
        (24_366, "5a7132f3d0fe5f95a8696675c99ef19fa6ddcc941d9065c7efd3018beab82fef"),
    "references/Onslaught/eventmanager.cpp":
        (14_523, "613f4628471bbc3206f61dcfa9718dc6799f56e759fa7776a5fad204ba7af893"),
    "local-lab/re-ledger/rtti-vtables.tsv":
        (443_128, "8f9900e89ba420090b0234615118794b3c62194eb058bc3992edb37edcc01195"),
    "local-lab/re-ledger/naming-wave-2026-07-27/anc-independent.json":
        (46_714, "459b278b26e6107644ee51165352c303a3dece79c29aa139694d0c6e848e735a"),
    "local-lab/re-ledger/rtti-conflict-adjudication.tsv":
        (90_744, "081177e936b28a30208be2b75a27af7d8e55895d4dd028dc3ca894b32b3b2a7c"),
    "reverse-engineering/binary-analysis/pc-demo-retail-virtual-target-map-2026-08-11.tsv":
        (1_204_103, "ba2db0551beeed458ea6265b87d1a5cf93bc2dd2c464da3f7f0c6702a4d4c750"),
    "local-lab/ghidra-fullpass-2026-07-23/exports/W002/instructions.tsv":
        (3_493_653, "27fe9a5591055dcbc52b31c95dccf9e9125012605d090bb4d7a7483650cf8a4d"),
    "local-lab/ghidra-fullpass-2026-07-23/exports/W002/xrefs.tsv":
        (289_551, "0a79df20947c2ae56bd7d694b3e012950677d44cb52dad818b1d52c225c544c8"),
    "local-lab/ghidra-hud-source-identity-live-promotion-20260812-v1/"
    "runs/live-readback/functions.tsv":
        (7_059_968, "fa2c9d749c97f1ab439b90572fd8f2292c9f5dcf4cc8b9b4f29f1756f088fed1"),
    "local-lab/ghidra-hud-source-identity-live-promotion-20260812-v1/"
    "runs/live-readback/program.tsv":
        (1_267, "cb47f9cf9e395b1cd9c31eedf4daba4564db2184484846d392b2a693dbcc5444"),
    "local-lab/ghidra-hud-source-identity-live-promotion-20260812-v1/"
    "live-promotion.ready.json":
        (6_905, "cd524c7976d27c7688800919eb0ef385795cdfe84715c880c153684ace27a5a5"),
    "local-lab/ghidra-hud-source-identity-live-promotion-20260812-v1/"
    "tracked-snapshot-restore.ready.json":
        (5_947, "42c5ca3cf7394b1ad20b4e53598dd40404addca87a36a38dc5880d6e19cb535e"),
}

FUNCTIONS_RELATIVE = next(key for key in INPUTS if key.endswith("/functions.tsv"))
PROGRAM_RELATIVE = next(key for key in INPUTS if key.endswith("/program.tsv"))
INSTRUCTIONS_RELATIVE = next(key for key in INPUTS if key.endswith("W002/instructions.tsv"))
XREFS_RELATIVE = next(key for key in INPUTS if key.endswith("W002/xrefs.tsv"))
VTABLES_RELATIVE = "local-lab/re-ledger/rtti-vtables.tsv"
ANCESTORS_RELATIVE = "local-lab/re-ledger/naming-wave-2026-07-27/anc-independent.json"
ADJUDICATION_RELATIVE = "local-lab/re-ledger/rtti-conflict-adjudication.tsv"
VIRTUAL_MAP_RELATIVE = (
    "reverse-engineering/binary-analysis/pc-demo-retail-virtual-target-map-2026-08-11.tsv")

TARGETS: dict[str, dict[str, Any]] = {
    "0x004263f0": {
        "preName": "CCollisionSeekingRound__Destructor",
        "postName": "CCollisionSeekingThing__dtor_base",
        "bodyEnd": 0x00426454,
        "bodyBytes": 100,
        "bodySha256": "b3763d249257fab412f20d423661ca1ad401f0c45d20203393dc62edcded7f4b",
        "bodyDigest": "21005db99300ad4864944885e7e132f47092c311bf918441f9a3710af8d666f4",
        "instructionCount": 31,
        "preSignature": "void __fastcall CCollisionSeekingRound__Destructor(void * this)",
        "commentSha256": "0c5340eb07914ecc053cff3b9c5ea86a1c1355c335ad50005f999ad5c4e872ef",
        "tagsSha256": "03d646be238db405cd9b2351a5067a8424f85907ac46c7a027c3d47bb8546229",
        "landmarks": (
            ("0x0042640d", "MOV", "dword ptr [ESI], 0x5d9608"),
            ("0x00426413", "MOV", "ECX, dword ptr [ESI + 0x14]"),
            ("0x00426428", "MOV", "ECX, dword ptr [ESI + 0x18]"),
            ("0x0042643f", "CALL", "0x004bac40"),
        ),
    },
    "0x004264a0": {
        "preName": "CCollisionSeekingThing__ResolveRoundCollisionResponse",
        "postName": "CCollisionSeekingThing__ResolveCollisionResponse",
        "bodyEnd": 0x004268F1,
        "bodyBytes": 1105,
        "bodySha256": "4aa1dd31761d87e3ed4bd32a5f722d496484c783e7cc01c410fdb116ccd28f6c",
        "bodyDigest": "bb2981e7511f01d47d9c41e1f8b671f8cede7108b5a28ec8c42042331b9ccef0",
        "instructionCount": 330,
        "preSignature": (
            "void __thiscall CCollisionSeekingThing__ResolveRoundCollisionResponse"
            "(void * this, void * otherRound)"),
        "commentSha256": "90cb46900ab8c29b049f519e72014162bab5765d65f407f154c3aabdce3672bd",
        "tagsSha256": "1398c31d17a7e88b9dc0e52fa2e7a87b3a3c12c4ea6dbb7917d62779fb8adb8c",
        "landmarks": (
            ("0x004264af", "TEST", "AH, 0x4"),
            ("0x004264c5", "CMP", "ECX, EAX"),
            ("0x004267cb", "CALL", "dword ptr [EDX + 0x14]"),
            ("0x004268cb", "CALL", "dword ptr [EDX + 0x9c]"),
        ),
    },
    "0x004269b0": {
        "preName": "CCSPersistentThing__InitWithSound",
        "postName": "CCSPersistentThing__Init",
        "bodyEnd": 0x004269F6,
        "bodyBytes": 70,
        "bodySha256": "bd4cf3f803c5d5a661b2d81ef96d1c2753a6ba4be722a4d1c6673ea96dedddd4",
        "bodyDigest": "566ba611eacde225e7bbc21672b0b5537de8d3013edfa56dead81680fe2adac8",
        "instructionCount": 27,
        "preSignature": (
            "void __thiscall CCSPersistentThing__InitWithSound"
            "(void * this, void * roundConfig)"),
        "commentSha256": "374ad3ee3c4f18ab55ccaf5a0eacac511259200582a1859bc9fa48f97c7f554a",
        "tagsSha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "landmarks": (
            ("0x004269b9", "CALL", "0x00426150"),
            ("0x004269be", "MOV", "EAX, dword ptr [EDI + 0x20]"),
            ("0x004269d5", "PUSH", "0xbb8"),
            ("0x004269e3", "CALL", "0x0044b2d0"),
            ("0x004269ec", "CALL", "0x00480a30"),
        ),
    },
    "0x00426a00": {
        "preName": "CCollisionSeekingRound__ProcessMapWhoCollisionSweep",
        "postName": "CCSPersistentThing__ProcessMapWhoCollisionSweep",
        "bodyEnd": 0x00426A15,
        "bodyBytes": 21,
        "bodySha256": "3bbee0a1544633b9f917ddd44b5a4bc4864499a9042a0d21cd8038251d709424",
        "bodyDigest": "01f8d02a6e32b1785f396eae0cfa6c2a2dc60e1239edfdb0aa09d542caca8ca6",
        "instructionCount": 7,
        "preSignature": (
            "void __thiscall CCollisionSeekingRound__ProcessMapWhoCollisionSweep"
            "(void * this, void * startOrContext, void * endOrContext)"),
        "commentSha256": "813256d29226faf2c561fe9d9538edb9a40c68efa88ebacc31576982e344c6db",
        "tagsSha256": "ead5ed68c3b7122aa2f501da1a3512d56ae61210d613c4cdddb49c92ee0ff23d",
        "landmarks": (
            ("0x00426a0a", "ADD", "ECX, 0x24"),
            ("0x00426a0d", "CALL", "0x00481060"),
            ("0x00426a12", "RET", "0x8"),
        ),
    },
    "0x00426a20": {
        "preName": "CCollisionSeekingRound__MarkDelayedCollisionReady",
        "postName": "CCSPersistentThing__HandleEvent",
        "bodyEnd": 0x00426A38,
        "bodyBytes": 24,
        "bodySha256": "0cf29c9c31fba213a38f5dfb2e4dbb21d7526f4d19fdbbcd5a64dca9ab82ea9b",
        "bodyDigest": "34e6532e3dc7757596029d98cf76f202d843a415b4dbbff9153d8df92cd861b0",
        "instructionCount": 7,
        "preSignature": (
            "void __thiscall CCollisionSeekingRound__MarkDelayedCollisionReady"
            "(void * this, void * event)"),
        "commentSha256": "07462366f96214cce6a7354813e6460f84657c3c52a9593821c8a23bf91939ae",
        "tagsSha256": "48742362cc4bab568a10b2d8467e283cce96d0ab790fe83a5642671d6281d8d6",
        "landmarks": (
            ("0x00426a24", "CMP", "word ptr [EAX + 0x4], 0xbb8"),
            ("0x00426a2f", "OR", "AH, 0x4"),
            ("0x00426a35", "RET", "0x4"),
        ),
    },
}

EXPECTED_VTABLES = {
    ("CCollisionSeekingThing", "0x005d9608", "6"): "0x004264a0",
    ("CCSPersistentThing", "0x005df6d8", "0"): "0x00426a20",
    ("CCSPersistentThing", "0x005df6d8", "3"): "0x004269b0",
    ("CCSPersistentThing", "0x005df6d8", "5"): "0x00426a00",
    ("CCSPersistentThing", "0x005df6d8", "6"): "0x004264a0",
}

EXPECTED_PLACEMENTS = {
    "0x004264a0": {
        "CCollisionSeekingThing", "CCSPersistentThing", "CCollisionSeekingRound",
        "CCollisionSeekingInfantryBloke", "CCSRay",
    },
    "0x004269b0": {"CCSPersistentThing", "CCollisionSeekingInfantryBloke"},
    "0x00426a00": {
        "CCSPersistentThing", "CCollisionSeekingRound", "CCollisionSeekingInfantryBloke"},
    "0x00426a20": {
        "CCSPersistentThing", "CCollisionSeekingRound", "CCollisionSeekingInfantryBloke"},
}

EXPECTED_ANCESTORS = {
    "CCollisionSeekingThing": ["CCollisionSeekingThing", "CMonitor", "IListener"],
    "CCSPersistentThing": [
        "CCSPersistentThing", "CCollisionSeekingThing", "CMonitor", "IListener"],
    "CCollisionSeekingRound": [
        "CCSPersistentThing", "CCollisionSeekingRound", "CCollisionSeekingThing",
        "CMonitor", "IListener"],
    "CCollisionSeekingInfantryBloke": [
        "CCSPersistentThing", "CCollisionSeekingInfantryBloke",
        "CCollisionSeekingThing", "CMonitor", "IListener"],
    "CCSRay": ["CCSRay", "CCollisionSeekingThing", "CMonitor", "IListener"],
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
    return {
        "path": path.resolve().relative_to(root.resolve()).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def exact_inputs(root: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for relative, expected in sorted(INPUTS.items()):
        actual = stamp(root / relative, root)
        require((actual["bytes"], actual["sha256"]) == expected,
                f"input identity differs: {relative}")
        result[relative] = actual
    return result


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProofError(f"cannot parse {path}: {exc}") from exc
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


def one(rows: Iterable[dict[str, str]], key: str, value: str, label: str) -> dict[str, str]:
    matches = [row for row in rows if row.get(key) == value]
    require(len(matches) == 1, f"{label} census differs")
    return matches[0]


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
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from(
            "<IIII", image, row + 8)
        if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
            return raw_pointer + rva - virtual_address
    raise ProofError(f"VA is not mapped: 0x{va:08x}")


def validate_pristine(image: bytes, *, require_whole_image: bool = True) -> dict[str, Any]:
    if require_whole_image:
        require(len(image) == 2_506_752 and sha256_bytes(image) == SPECIMEN_SHA256,
                "pristine specimen differs")
    bodies = []
    for address, spec in TARGETS.items():
        start = int(address, 16)
        end = int(spec["bodyEnd"])
        offset = pe_offset(image, start)
        body = image[offset:offset + end - start]
        require(len(body) == spec["bodyBytes"], f"body length differs: {address}")
        require(sha256_bytes(body) == spec["bodySha256"], f"body bytes differ: {address}")
        bodies.append({
            "address": address,
            "endExclusiveVa": f"0x{end:08x}",
            "bytes": len(body),
            "sha256": spec["bodySha256"],
        })
    return {"specimenSha256": SPECIMEN_SHA256, "bodies": bodies}


def validate_source_text(thing_text: str, init_text: str, event_text: str) -> dict[str, Any]:
    thing = thing_text.splitlines()
    init = init_text.splitlines()
    event = event_text.splitlines()
    expected_thing = {
        300: "void\tCThing::InitCollisionSeekingThing(CInitCSThing *init)",
        310: "mCollisionSeekingThing = new( MT_CST ) CCSPersistentThing  ;",
        322: "init->mForThing = this ;",
        323: "mCollisionSeekingThing->Init(init);",
    }
    expected_init = {
        85: "mStartCollideOnNextFrame = TRUE ;",
        86: "mTimeBeforeStart=-1; // force next frame // btw -1 means NEXT_FRAME to event_manager",
        104: "BOOL\t\t\t   mStartCollideOnNextFrame ;",
        107: "float\t\t\t   mTimeBeforeStart;",
    }
    expected_event = {
        337: "IListener* to_call = next_event->GetToCall() ;",
        341: "to_call->HandleEvent(next_event);",
        354: "IListener* to_call = next_event->GetToCall() ;",
        359: "to_call->HandleEvent(next_event);",
    }
    for lines, expected, label in (
        (thing, expected_thing, "thing.cpp"),
        (init, expected_init, "InitThing.h"),
        (event, expected_event, "eventmanager.cpp"),
    ):
        for number, text in expected.items():
            require(number <= len(lines) and lines[number - 1].strip() == text.strip(),
                    f"{label} source line differs: {number}")
    return {
        "allocationAndInit": [
            {"file": "thing.cpp", "line": number, "text": text.strip()}
            for number, text in expected_thing.items()
        ],
        "delayedStartFields": [
            {"file": "InitThing.h", "line": number, "text": text.strip()}
            for number, text in expected_init.items()
        ],
        "eventDispatch": [
            {"file": "eventmanager.cpp", "line": number, "text": text.strip()}
            for number, text in expected_event.items()
        ],
    }


def instruction_key(row: dict[str, str]) -> tuple[str, str, str]:
    return row.get("instruction_addr", ""), row.get("mnemonic", ""), row.get("operands", "")


def validate_instructions(instructions: list[dict[str, str]],
                          xrefs: list[dict[str, str]]) -> dict[str, Any]:
    body_observations: dict[str, list[dict[str, str]]] = {}
    for address, spec in TARGETS.items():
        rows = [row for row in instructions if row.get("function_entry") == address]
        require(len(rows) == spec["instructionCount"],
                f"instruction count differs: {address}")
        observed = {instruction_key(row) for row in rows}
        landmarks = []
        for landmark in spec["landmarks"]:
            require(landmark in observed,
                    f"retail body landmark differs: {address} {landmark[0]}")
            landmarks.append({
                "instructionVa": landmark[0], "mnemonic": landmark[1],
                "operands": landmark[2],
            })
        body_observations[address] = landmarks

    destructor_refs = {
        (row.get("from_function_addr"), row.get("from_function"), row.get("ref_type"))
        for row in xrefs if row.get("target_addr") == "004263f0"
    }
    expected_refs = {
        ("00426460", "CCollisionSeekingRound__ScalarDeletingDestructor", "UNCONDITIONAL_CALL"),
        ("00488ea0", "CCollisionSeekingInfantryBloke__dtor_body_00488ea0", "UNCONDITIONAL_CALL"),
        ("004d8a70", "CCollisionSeekingRound__ShutdownMonitorAndDestruct", "UNCONDITIONAL_CALL"),
        ("004d9dc0", "CCSRay__DestructorBody_004d9dc0", "UNCONDITIONAL_JUMP"),
        ("004f3a70", "CCSPersistentThing__dtor_base", "UNCONDITIONAL_CALL"),
    }
    require(expected_refs <= destructor_refs, "shared destructor fan-in differs")

    init_call = one(xrefs, "from_addr", "004f3a41", "CThing virtual Init call")
    require(init_call.get("target_addr") == "004269b0" and
            init_call.get("from_function_addr") == "004f39c0" and
            init_call.get("ref_type") == "COMPUTED_CALL",
            "CThing persistent Init call differs")
    return {
        "bodyLandmarks": body_observations,
        "sharedDestructorFanIn": [
            {"fromFunctionVa": item[0], "fromFunction": item[1], "referenceType": item[2]}
            for item in sorted(expected_refs)
        ],
        "persistentInitCallsite": {
            "fromInstructionVa": "0x004f3a41",
            "fromFunctionVa": "0x004f39c0",
            "targetVa": "0x004269b0",
            "referenceType": "COMPUTED_CALL",
        },
    }


def validate_inventory(functions: list[dict[str, str]],
                       program: list[dict[str, str]]) -> dict[str, Any]:
    metrics = {row["metric"]: row["value"] for row in program}
    require(metrics.get("programName") == "BEA.exe", "Ghidra program name differs")
    require(metrics.get("executableSHA256") == SPECIMEN_SHA256, "Ghidra specimen differs")
    require(metrics.get("memorySha256") ==
            "5398f750f1ffb59873a6ec7e1750b51d11b5b844a8fda8d4e43649b5b9e5089d",
            "Ghidra memory image differs")
    require(metrics.get("functions") == "8136" and metrics.get("instructions") == "549872",
            "Ghidra function/instruction census differs")
    rows = []
    for address, spec in TARGETS.items():
        row = one(functions, "address", address, f"Ghidra target {address}")
        require(row.get("name") == spec["preName"], f"Ghidra PRE name differs: {address}")
        require(row.get("nameSource") == "USER_DEFINED", f"name source differs: {address}")
        require(row.get("sigSource") == "USER_DEFINED", f"signature source differs: {address}")
        require(row.get("signature") == spec["preSignature"],
                f"Ghidra PRE signature differs: {address}")
        require(row.get("bodyBytes") == str(spec["bodyBytes"]) and
                row.get("bodyDigest") == spec["bodyDigest"] and
                row.get("instrCount") == str(spec["instructionCount"]),
                f"Ghidra body identity differs: {address}")
        require(row.get("commentSha256") == spec["commentSha256"],
                f"Ghidra PRE comment differs: {address}")
        require(row.get("tagsSha256") == spec["tagsSha256"],
                f"Ghidra PRE tags differ: {address}")
        rows.append({
            "address": address,
            "preName": spec["preName"],
            "postName": spec["postName"],
            "bodyDigest": spec["bodyDigest"],
            "instructionCount": spec["instructionCount"],
            "preCommentSha256": spec["commentSha256"],
            "preTagsSha256": spec["tagsSha256"],
        })
    return {
        "functionCount": 8136,
        "instructionCount": 549872,
        "memorySha256": metrics["memorySha256"],
        "targets": rows,
    }


def validate_vtables(rows: list[dict[str, str]]) -> dict[str, Any]:
    lookup = {
        (row["class"], row["vtable_va"], row["slot"]): row["function_va"]
        for row in rows
    }
    for key, value in EXPECTED_VTABLES.items():
        require(lookup.get(key) == value, f"strict vtable row differs: {key}")
    placements: dict[str, list[str]] = {}
    for address, expected in EXPECTED_PLACEMENTS.items():
        actual = {row["class"] for row in rows if row["function_va"] == address}
        require(actual == expected, f"strict virtual placement set differs: {address}")
        placements[address] = sorted(actual)
    return {
        "baseImplementationSlots": [
            {"class": key[0], "vtableVa": key[1], "slot": int(key[2]), "functionVa": value}
            for key, value in sorted(EXPECTED_VTABLES.items())
        ],
        "placementClasses": placements,
    }


def validate_ancestors(value: dict[str, Any]) -> dict[str, Any]:
    for class_name, expected in EXPECTED_ANCESTORS.items():
        require(value.get(class_name) == expected, f"strict ancestry differs: {class_name}")
    return {name: EXPECTED_ANCESTORS[name] for name in sorted(EXPECTED_ANCESTORS)}


def validate_historical(rows: list[dict[str, str]]) -> dict[str, Any]:
    expected = {
        "0x004264a0": ("CCollisionSeekingThing", "SAFE_REPREFIX"),
        "0x004269b0": ("CCSPersistentThing", "SAFE_REPREFIX"),
        "0x00426a00": ("CCSPersistentThing", "UNCERTAIN"),
        "0x00426a20": ("CCSPersistentThing", "UNCERTAIN"),
    }
    result = []
    for address, (owner, classification) in expected.items():
        row = one(rows, "address", address, f"historical adjudication {address}")
        require(row.get("rtti_owner") == owner and row.get("classification") == classification,
                f"historical adjudication differs: {address}")
        result.append({
            "address": address,
            "rttiOwner": owner,
            "historicalClassification": classification,
            "disposition": (
                "owner retained; role suffix independently re-proved"
                if classification == "SAFE_REPREFIX" else
                "base implementation label now proven; folded derived aliases remain open"
            ),
        })
    return {"rows": result, "destructorWasNotInTable": True}


def validate_virtual_map(rows: list[dict[str, str]]) -> dict[str, Any]:
    result = []
    for address, expected_classes in EXPECTED_PLACEMENTS.items():
        row = one(rows, "retail_va", address, f"PC demo map {address}")
        require(row.get("exact_zero_normalized") == "true" and
                row.get("full_demo_decode") == "true" and
                row.get("normalized_diff_instruction_count") == "0" and
                row.get("normalized_diff_byte_count") == "0",
                f"PC demo normalized identity differs: {address}")
        require(set(row.get("owner_classes", "").split("|")) == expected_classes,
                f"PC demo placement classes differ: {address}")
        require(row.get("retail_instruction_stream_raw_sha256") ==
                TARGETS[address]["bodySha256"], f"PC demo retail body digest differs: {address}")
        result.append({
            "retailVa": address,
            "demoVa": row["demo_va"],
            "ownerClasses": sorted(expected_classes),
            "normalizedInstructionIdentity": True,
            "retailRawSha256": row["retail_instruction_stream_raw_sha256"],
            "demoRawSha256": row["demo_instruction_stream_raw_sha256"],
        })
    return {"rows": result}


def validate_lineage(root: Path) -> dict[str, Any]:
    lane = root / "local-lab/ghidra-hud-source-identity-live-promotion-20260812-v1"
    promotion = read_json(lane / "live-promotion.ready.json")
    restore = read_json(lane / "tracked-snapshot-restore.ready.json")
    require(promotion.get("verdict") == "READY" and
            promotion.get("phase") == "LIVE_PROMOTED", "latest Ghidra promotion is not READY")
    require(promotion.get("result", {}).get("trackedSnapshotMatchesLive") is True,
            "tracked/live Ghidra equality is not proven")
    require(restore.get("readonlyOpen", {}).get("opened") is True and
            restore.get("readonlyOpen", {}).get("contentStable") is True,
            "tracked Ghidra restore was not stable")
    require(restore.get("copyComparison", {}).get("matches") is True,
            "tracked Ghidra restore copy differs")
    return {
        "latestLivePromotionReadySha256": INPUTS[
            next(key for key in INPUTS if key.endswith("live-promotion.ready.json"))][1],
        "trackedRestoreReadySha256": INPUTS[
            next(key for key in INPUTS if key.endswith("tracked-snapshot-restore.ready.json"))][1],
        "trackedSnapshotMatchesLive": True,
        "trackedRestoreReadOnlyOpen": True,
    }


def build(root: Path, generated_at: str) -> dict[str, Any]:
    datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    inputs = exact_inputs(root)
    image = (root / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup").read_bytes()
    source = validate_source_text(
        (root / "references/Onslaught/thing.cpp").read_text(encoding="utf-8"),
        (root / "references/Onslaught/InitThing.h").read_text(encoding="utf-8"),
        (root / "references/Onslaught/eventmanager.cpp").read_text(encoding="utf-8"),
    )
    instructions = validate_instructions(
        read_tsv(root / INSTRUCTIONS_RELATIVE), read_tsv(root / XREFS_RELATIVE))
    inventory = validate_inventory(
        read_tsv(root / FUNCTIONS_RELATIVE), read_tsv(root / PROGRAM_RELATIVE))
    vtables = validate_vtables(read_tsv(root / VTABLES_RELATIVE))
    ancestors = validate_ancestors(read_json(root / ANCESTORS_RELATIVE))
    historical = validate_historical(read_tsv(root / ADJUDICATION_RELATIVE))
    virtual_map = validate_virtual_map(read_tsv(root / VIRTUAL_MAP_RELATIVE))
    return {
        "schema": SCHEMA,
        "claim": CLAIM,
        "verdict": "READY",
        "generatedAtUtc": generated_at,
        "author": stamp(Path(__file__), root),
        "inputs": inputs,
        "lineage": validate_lineage(root),
        "pristine": validate_pristine(image),
        "sourceEvidence": source,
        "retailInstructionsAndXrefs": instructions,
        "ghidraPreimage": inventory,
        "strictRttiVtables": vtables,
        "strictRttiAncestors": ancestors,
        "historicalAdjudication": historical,
        "pcDemoCrossBuild": virtual_map,
        "adjudication": {
            "confidence": "HIGH_STATIC_IMPLEMENTATION_IDENTITY",
            "corrections": [
                {"address": address, "from": spec["preName"], "to": spec["postName"]}
                for address, spec in TARGETS.items()
            ],
            "authorizedMutationEnvelope": {
                "functionNames": 5,
                "selfDescribingSignatures": 5,
                "functionComments": 5,
                "staleOrRequiredFunctionTags": 5,
                "functionBoundaries": 0,
                "programBytes": 0,
                "instructions": 0,
                "dataUnits": 0,
                "references": 0,
            },
        },
        "limitations": [
            "The labels identify the shared base implementation body; they do not exclude identical-code-folded derived aliases at the same address.",
            "ResolveCollisionResponse and ProcessMapWhoCollisionSweep are bounded descriptive role labels, not proof of exact original source spelling.",
            "Supplied source fixes allocation, virtual Init dispatch, delayed-start fields, and listener event dispatch; it is not the retail collision-component source body.",
            "Static bytes, slots, and call edges do not prove exact runtime cadence, geometry, side effects, failure behavior, or complete field layouts.",
            "No reconstruction mapping or REBUILD_READY status is authorized.",
            "This receipt alone does not authorize a live Ghidra write; verified PRE backup, isolated scratch mutation, rollback probes, separate-process readback, POST backup, and tracked-snapshot equality remain required.",
        ],
    }


def json_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def publish_new(path: Path, content: bytes) -> None:
    require(not path.exists(), f"refusing to overwrite proof receipt: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=f".{path.name}.", suffix=".partial",
                                     dir=path.parent, delete=False) as stream:
        partial = Path(stream.name)
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.replace(partial, path)
    finally:
        partial.unlink(missing_ok=True)


def validate_saved(saved: dict[str, Any], root: Path) -> None:
    require(saved == build(root, saved.get("generatedAtUtc", "")), "saved proof content differs")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("seal", "verify"))
    args = parser.parse_args()
    root = root_path()
    ready = root / EVIDENCE_RELATIVE / READY_NAME
    if args.command == "seal":
        payload = build(root, utc_now())
        publish_new(ready, json_bytes(payload))
        validate_saved(read_json(ready), root)
    else:
        validate_saved(read_json(ready), root)
    print(f"COLLISION_COMPONENT_IDENTITY_REPROOF_READY sha256={sha256_file(ready)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
