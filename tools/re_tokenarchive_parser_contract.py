#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reprove CTokenArchive::ReadNextToken and the shipped particle-token corpus.

This is a static, specimen-bound proof.  It decodes the retail token-name and
parser dispatch tables directly from the pristine PE, validates every authored
line in all three shipped ParticleSets files, extracts every retail writer call
from exact xrefs plus machine bytes, and cross-walks the thirteen descriptor
loaders in the latest verified Ghidra POST backup.  It does not execute the
game, mutate Ghidra, or claim runtime path coverage.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import struct
import tempfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA = "bea.re.tokenarchive-parser-contract-reproof.v1"
CLAIM = "CTOKENARCHIVE_READNEXTTOKEN_STATIC_CONTRACT_AND_PARTICLE_CORPUS_CROSSWALK"
SPECIMEN_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
EVIDENCE_RELATIVE = Path("local-lab/tokenarchive-parser-contract-reproof-20260809-v1")
READY_NAME = "proof.ready.json"

PARENT_RELATIVE = Path(
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-17-lockhit-bounded-contract-v1"
)
PARENT_READY_SHA256 = "6d794905d6fc5daea11f99b781cf8eb7740765e749c784d02507d43436b801a2"
PARENT_REDUCER_ID = "fbb343d629fa12a641aced04db88b59e5270e1f45990d9d203284302f8761621"
PARENT_AUTHORITY_SHA256 = "c37aae056dc2f04d946db69d4e13d276dbc11d1a52976c97657af0a5549b00cb"
PARENT_COUNTS = {
    "functions": 8125,
    "residuals": 6118,
    "questions": 15253,
    "scenarios": 72,
    "levers": 915,
    "contracts": 14243,
    "adjudications": 6096,
    "supersessions": 588,
}

ENTITY_KEY = (
    "CODE:" + SPECIMEN_SHA256
    + ":VA=0x004f57b0:RANGES=bedc826d01b6a8a1792de76da45537e1b3f6f663051efecc30414377d0efe76b"
)
CONTRACT_ID = "C-a1dd659dcb7d74c1"
QUESTION_ID = "Q-f40657bf78b29abb"

GET_TOKEN_NAME = 0x004F52B0
GET_TOKEN_NAME_END = 0x004F55B2
GET_TOKEN_NAME_JUMPS = 0x004F55B4
READ_NEXT_TOKEN = 0x004F57B0
READ_NEXT_TOKEN_END = 0x004F5AC5
DISPATCH_POINTERS = 0x004F5AC8
TOKEN_KIND_INDEX = 0x004F5AE4
FACTORY = 0x004CC020
FACTORY_END = 0x004CC814
LOAD_FROM_ARCHIVE = 0x004CD7F0
LOAD_FROM_ARCHIVE_END = 0x004CDA59

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
CATEGORY_NAMES = {
    0: "INVALID_OR_UNKNOWN",
    1: "MARKER_NO_VALUE",
    2: "DIRECT_FLOAT",
    3: "DIRECT_INT",
    4: "RAW_REMAINDER_STRING",
    5: "FLOAT_WITH_OPTIONAL_REFERENCE",
    6: "REFERENCE_NAME",
}
WRITER_TARGETS = {
    0x004F5C90: "DIRECT_INT",
    0x004F5CD0: "DIRECT_FLOAT",
    0x004F5D10: "RAW_REMAINDER_STRING",
    0x004F5D50: "REFERENCE_NAME",
    0x004F5DC0: "FLOAT_WITH_OPTIONAL_REFERENCE",
}
WRITER_COUNTS = {
    "DIRECT_INT": 60,
    "DIRECT_FLOAT": 17,
    "RAW_REMAINDER_STRING": 4,
    "REFERENCE_NAME": 21,
    "FLOAT_WITH_OPTIONAL_REFERENCE": 39,
}
CORPUS_CATEGORY_OCCURRENCES = {
    "MARKER_NO_VALUE": 1482,
    "DIRECT_FLOAT": 2844,
    "DIRECT_INT": 12559,
    "RAW_REMAINDER_STRING": 2063,
    "FLOAT_WITH_OPTIONAL_REFERENCE": 5034,
    "REFERENCE_NAME": 3204,
}

D_BACKUP_ROOT = Path(
    r"D:\BEA-Ghidra-Backups\2026-08-09-post-recovery\setpos-post-live"
)

INPUTS: dict[str, tuple[int, str]] = {
    "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup": (
        2_506_752, SPECIMEN_SHA256),
    f"{PARENT_RELATIVE.as_posix()}/campaign.ready.json": (
        21_499, PARENT_READY_SHA256),
    f"{PARENT_RELATIVE.as_posix()}/campaign-functions.tsv": (
        5_131_014, "50970af530be6cf9885de7af33cede59f8ed80f2f98bf6541ec4239a77db1bd2"),
    f"{PARENT_RELATIVE.as_posix()}/campaign-contracts.tsv": (
        10_919_636, "166358f44a0e1bad7c29b541d3602fa722f8b57c7b70aee28ace6e247c89e1c1"),
    f"{PARENT_RELATIVE.as_posix()}/campaign-questions.tsv": (
        8_370_034, "e86ead4f97a94182750a522c9cf44d0664108dec3b81678c28be14531213a3b0"),
    "local-lab/re-campaign-incident-recovery-20260808-v1/"
    "generation-17-lockhit-bounded-contract-authority.ready.json": (
        9_956, PARENT_AUTHORITY_SHA256),
    "local-lab/tokenarchive-dispatch-table-reproof-20260809-v1/proof.ready.json": (
        11_257, "182d302e45ff42b389b54c85f92576864f9ef9dc30887ee5fc6db86b307faf7f"),
    "tools/re_tokenarchive_dispatch_reproof.py": (
        27_014, "9fa0a7bce82f234991843aa0047d4f33aeeb9342cf9397887b87572eb3c5d55e"),
    "local-lab/ghidra-mission-native-setpos-live-promotion-20260809-v1/"
    "promotion/promotion.ready.json": (
        6_782, "e64be82f360203fd2864450c5b3bd2d0a46441b9120eb79c8c423c3fe1ca0340"),
    "local-lab/ghidra-mission-native-setpos-live-promotion-20260809-v1/"
    "backups/post-live/backup_manifest.json": (
        7_589, "df2c7ad5c2367801c6fa359ec4be7bcf65864306f87860f643f886d0517724bc"),
    "local-lab/ghidra-fullpass-2026-07-23/exports/W007/xrefs.tsv": (
        396_362, "e87a563935893819ac48f9ecacdabde869de0ef01ddd5b8751a159820912cc37"),
    "local-lab/safe-copy-bea-pristine/data/ParticleSets/Frontend.par": (
        28_702, "01a4c73d7cfc666b4a367736fabd1d91bf3459ed1c538b6ca77f70c069cf8bc6"),
    "local-lab/safe-copy-bea-pristine/data/ParticleSets/MainSet.par": (
        685_194, "a51fe4419b55e1af132e31c6b3cd8133c937745d8f4ab691eb5a0d81017ded06"),
    "local-lab/safe-copy-bea-pristine/data/ParticleSets/ModelViewer.par": (
        3_465, "32d85d1f0400f46a45078d49c695967cde60ed572053059fd6246227162115a9"),
    "local-lab/tokenarchive-parser-contract-reproof-20260809-v1/addresses.txt": (
        286, "d269e77c8fe627ec9c4de23c3e1dd33ba5d9753ef9d0fcd99013f15bf4351fc6"),
    "local-lab/tokenarchive-parser-contract-reproof-20260809-v1/headless-decompile.log": (
        5_213, "e918f43c307126859ed00875d35f6f721f492876f2e40737e33ff3470b155f2a"),
    "local-lab/tokenarchive-parser-contract-reproof-20260809-v1/ghidra-decompile/index.tsv": (
        3_271, "965c6d76defdd9e3b25d1e17ff6bb367e06637544827463f8cabe377155572ec"),
    "local-lab/tokenarchive-parser-contract-reproof-20260809-v1/createbytype-address.txt": (
        11, "77aa1df71f15d125a3e00245f71cab34f46db81396b5acf878a3494ff3506037"),
    "local-lab/tokenarchive-parser-contract-reproof-20260809-v1/headless-createbytype.log": (
        5_231, "50edfd87f735cbf442b9ce8c9ef0b73edfe81a8885e04b97327956b1d91436bf"),
    "local-lab/tokenarchive-parser-contract-reproof-20260809-v1/ghidra-createbytype/index.tsv": (
        175, "866994c6e1c44b916e3176942346635257f875d2a09c34c9926e78ed7206c4bd"),
    "local-lab/tokenarchive-parser-contract-reproof-20260809-v1/ghidra-createbytype/"
    "004cc020_CParticleSet__CreateByType.c": (
        16_981, "9d8036df3116c928bb1be77d9bd346d2127f7e98e91cad0444862e5a07f4c76a"),
    "tools/ExportFunctionsByAddressDecompile.java": (
        5_278, "5afec283ecd778d6f77fd9a7514028bd89e1c96d3e2d1e7fc211da407f2b03e2"),
}

DECOMPILE_INPUTS: dict[str, tuple[int, str]] = {
    "0048de00_CTokenArchive__ReadLine.c": (1_216, "7e4d9d292ba0ca863d5b8dae2b7ef3cc392a38b6e9a5cd8c81baf65dc03274a7"),
    "004c05c0_CPDSimpleSprite__VFunc_6_004c05c0.c": (2_725, "63764292bf851e7247da93e48b8f0a2948094d285a3ed44e890b7834ae6b81b5"),
    "004c1810_CPDEmitter__VFunc_6_004c1810.c": (3_039, "cdfa575f0858166d2fceee2a93a1c837068c0e8d99aefc816d7af8be3ac48f75"),
    "004c20c0_CPDModifier__VFunc_6_004c20c0.c": (1_465, "583dd911222ab3bb8b8eb57d48d2c7287a8ea805c98e506cc2b35b242a357a28"),
    "004c2130_CPDSelector__VFunc_6_004c2130.c": (2_318, "950aa9b485dee6f64d7c1ccc159c4dc7052e32d672b1d66e6240d652efba0e6f"),
    "004c2300_CPDColourRange__VFunc_6_004c2300.c": (2_756, "e3ba3e899bc62e4574a35134a76615af497a28c16233f1e5929ae6ea35bcba58"),
    "004c24c0_CPDTimeline__VFunc_6_004c24c0.c": (1_379, "591131d36e58a5669cd95f79bce2e02981f23a78c420b209fc0fcaf5bc79698e"),
    "004c2b70_CPDShape__VFunc_6_004c2b70.c": (2_277, "541e48179fdbcf21fb4f48097a611029d985e1f2b5cfa578164118e9aa93a5dd"),
    "004c3120_CPDTrail__VFunc_6_004c3120.c": (4_885, "7fa710e947a9cb26fe250552ab7e76c4d1697cd97caa4a4724f76727af171324"),
    "004c4420_CPDMover__VFunc_6_004c4420.c": (2_290, "4d4eeb0c6179dada6cf4f1cb96373fa5ecb94faac5b0c88120b2ffef04c6847e"),
    "004c4840_CPDFunction__VFunc_6_004c4840.c": (2_431, "30dd6dbac4ba711c04c761b3163c8161f5e4330cab2d5927166baaf9557b4834"),
    "004c4b00_CPDMesh__VFunc_6_004c4b00.c": (1_462, "19aa83d5879af6ddcd007f0d12639bde0f601c270296c1ce8b745115f8dce02a"),
    "004c5330_CPDFoR__VFunc_6_004c5330.c": (944, "320647c4af2fb8041c4225185cc1c3277398a827bd290eaa3dcbe67aeffb5970"),
    "004c5730_CPDPMesh__Load.c": (3_316, "0bca7b73dc52631f89caf7719c0814f9d5fdf563c3d87663b97e62040a738d68"),
    "004cd7f0_CParticleSet__LoadFromArchive.c": (3_548, "192623b27314184aa5ca0107c45fb73153a59f4790c652472db7b6c4bed28f75"),
    "004cda60_CParticleSet__LoadParticleSetFile.c": (3_365, "e10282ddb8670642cd07f8ae9a44e3a587bdb87943ac6c8fb3bac48b3d10797e"),
    "004f52b0_CTokenArchive__GetTokenName.c": (7_004, "aa4651f56d3d7c71e850ff025088fba0fbec011788d8247889032bafaf03c88c"),
    "004f57b0_CTokenArchive__ReadNextToken.c": (9_643, "37084af563c82882bccb6be0ab6ce39c348e378592c43af20fc9d3a8ab43d633"),
    "004f5b70_CTokenArchive__BindIndexedFieldPointer.c": (1_333, "cb4141932ec8c3f1d50ae5aed89a4fbe439b6ed9b109605349a7991e90697fa9"),
    "004f5b80_CTokenArchive__RegisterReferenceFixup.c": (873, "f1df2a4a4dca14b9902073f909316fd59ef0e5c5f35de09b62b6483cc34e1af2"),
    "004f5ba0_CTokenArchive__ResolveReferences.c": (2_094, "e3fdcad027e98cc62faf973afb293cf1366f1559d4e56d8ad7a30ec43a8b3aac"),
    "004f5c90_CTokenArchive__WriteInt.c": (686, "2d27e58a953aaa13e160716c2ce0d0b3308d978bd1f42caed226e92cba513045"),
    "004f5cd0_CTokenArchive__WriteFloat.c": (694, "c4c4524670b748b25a4b1c757ad10d6728e7ab507e72a768be7c579fb385c178"),
    "004f5d10_CTokenArchive__WriteString.c": (699, "6d6572d26e2f0c9dc1a03a14e80a7bb39fb8774471eac17e68e8bfdf7afd1161"),
    "004f5d50_CTokenArchive__WritePointer.c": (865, "2742e934dfaa8218182884411b9dc87f5202a53de29a7760e19b438492886edb"),
    "004f5dc0_CTokenArchive__WriteFloatPointer.c": (977, "1bf5b602d4ea9c4a7f063e12321dd9ccc74fe3cca637f1e3976ac953da15c786"),
}


LOADER_SPECS = (
    (1, "CPDSimpleSprite", 0x004C05C0, "004c05c0_CPDSimpleSprite__VFunc_6_004c05c0.c", tuple(range(6, 26)) + (27,), 405),
    (2, "CPDEmitter", 0x004C1810, "004c1810_CPDEmitter__VFunc_6_004c1810.c", tuple(range(26, 41)), 338),
    (3, "CPDModifier", 0x004C20C0, "004c20c0_CPDModifier__VFunc_6_004c20c0.c", (), 0),
    (4, "CPDSelector", 0x004C2130, "004c2130_CPDSelector__VFunc_6_004c2130.c", tuple(range(41, 49)), 40),
    (5, "CPDColourRange", 0x004C2300, "004c2300_CPDColourRange__VFunc_6_004c2300.c", tuple(range(49, 61)), 97),
    (6, "CPDTimeline", 0x004C24C0, "004c24c0_CPDTimeline__VFunc_6_004c24c0.c", (28, 34, 61, 62), 258),
    (7, "CPDShape", 0x004C2B70, "004c2b70_CPDShape__VFunc_6_004c2b70.c", (6, 63, 64, 65, 66, 67, 68, 69, 70), 77),
    (8, "CPDTrail", 0x004C3120, "004c3120_CPDTrail__VFunc_6_004c3120.c", (8, 11, 13, 14, 16, 27, 34, 63, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 103), 100),
    (9, "CPDMover", 0x004C4420, "004c4420_CPDMover__VFunc_6_004c4420.c", (85, 86, 87, 88, 89, 90, 91), 14),
    (10, "CPDFunction", 0x004C4840, "004c4840_CPDFunction__VFunc_6_004c4840.c", (92, 93, 94, 95, 96, 97, 98, 99, 100), 46),
    (11, "CPDMesh", 0x004C4B00, "004c4b00_CPDMesh__VFunc_6_004c4b00.c", (8, 9, 27, 34, 101, 102, 103, 104), 13),
    (12, "CPDFoR", 0x004C5330, "004c5330_CPDFoR__VFunc_6_004c5330.c", (40, 105, 106), 24),
    (13, "CPDPMesh", 0x004C5730, "004c5730_CPDPMesh__Load.c", (11, 13, 16, 27, 63, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123), 67),
)


class ProofError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
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


def read_tsv(path: Path, *, campaign: bool = False) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        first = stream.readline()
        if campaign:
            require(first.rstrip("\r\n") == "# bea.re.campaign.v5", f"campaign marker differs: {path}")
        else:
            stream.seek(0)
        return list(csv.DictReader(stream, delimiter="\t"))


def exact_inputs(root: Path) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    all_inputs = dict(INPUTS)
    for name, expected in DECOMPILE_INPUTS.items():
        all_inputs[(EVIDENCE_RELATIVE / "ghidra-decompile" / name).as_posix()] = expected
    for relative, expected in sorted(all_inputs.items()):
        actual = stamp(root / relative, root)
        require((actual["bytes"], actual["sha256"]) == expected, f"input identity differs: {relative}")
        result[relative] = actual
    return result


def pe_layout(
    image: bytes,
    *,
    require_specimen: bool = True,
) -> tuple[int, list[tuple[int, int, int, int]]]:
    if require_specimen:
        require(len(image) == 2_506_752 and sha256_bytes(image) == SPECIMEN_SHA256, "pristine specimen differs")
    pe = struct.unpack_from("<I", image, 0x3C)[0]
    require(image[pe:pe + 4] == b"PE\0\0", "pristine PE signature differs")
    sections = struct.unpack_from("<H", image, pe + 6)[0]
    optional_size = struct.unpack_from("<H", image, pe + 20)[0]
    optional = pe + 24
    image_base = struct.unpack_from("<I", image, optional + 28)[0]
    table = optional + optional_size
    rows = []
    for index in range(sections):
        row = table + index * 40
        virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from("<IIII", image, row + 8)
        rows.append((virtual_address, max(virtual_size, raw_size), raw_pointer, raw_size))
    return image_base, rows


def pe_offset(image: bytes, va: int, *, require_specimen: bool = True) -> int:
    image_base, sections = pe_layout(image, require_specimen=require_specimen)
    rva = va - image_base
    for virtual_address, extent, raw_pointer, _raw_size in sections:
        if virtual_address <= rva < virtual_address + extent:
            return raw_pointer + rva - virtual_address
    raise ProofError(f"VA is not mapped: 0x{va:08x}")


def va_bytes(image: bytes, start: int, end: int, *, require_specimen: bool = True) -> bytes:
    offset = pe_offset(image, start, require_specimen=require_specimen)
    value = image[offset:offset + end - start]
    require(len(value) == end - start, f"short PE span at 0x{start:08x}")
    return value


def read_c_string(image: bytes, va: int, *, require_specimen: bool = True) -> str:
    offset = pe_offset(image, va, require_specimen=require_specimen)
    try:
        end = image.index(0, offset)
    except ValueError as exc:
        raise ProofError(f"unterminated PE string at 0x{va:08x}") from exc
    try:
        return image[offset:end].decode("ascii")
    except UnicodeDecodeError as exc:
        raise ProofError(f"non-ASCII PE string at 0x{va:08x}") from exc


def derive_static_tables(
    image: bytes,
    *,
    require_specimen: bool = True,
) -> tuple[list[dict[str, Any]], bytes]:
    def span(start: int, end: int) -> bytes:
        return va_bytes(image, start, end, require_specimen=require_specimen)

    def string_at(va: int) -> str:
        return read_c_string(image, va, require_specimen=require_specimen)

    require(
        sha256_bytes(span(GET_TOKEN_NAME, GET_TOKEN_NAME_END))
        == "f60b16324b476da3213a4062ede1722a8d4e60bed39088538583e1797780af2c",
        "GetTokenName body differs",
    )
    require(
        sha256_bytes(span(READ_NEXT_TOKEN, READ_NEXT_TOKEN_END))
        == "e77885aa506084274deabe51f714adb713314e84b217e8736ba7153afe87cc58",
        "ReadNextToken body differs",
    )
    require(
        sha256_bytes(span(FACTORY, FACTORY_END))
        == "7c70841e58dffea534e84bdf30de5054e6a86eb1ed789380e5ea71a86ed2c505",
        "particle factory body differs",
    )
    require(
        sha256_bytes(span(LOAD_FROM_ARCHIVE, LOAD_FROM_ARCHIVE_END))
        == "629f6a56c6f13220786e0637bb602e7441292aacf3c497957a1b09fdde846494",
        "particle archive loader body differs",
    )
    prologue = span(GET_TOKEN_NAME, GET_TOKEN_NAME + 20)
    require(
        prologue == bytes.fromhex("8b44240483f87b0f87ef020000ff2485b4554f00"),
        "GetTokenName range check or jump table differs",
    )
    return_blocks = struct.unpack("<124I", span(GET_TOKEN_NAME_JUMPS, GET_TOKEN_NAME_JUMPS + 496))
    kinds = span(TOKEN_KIND_INDEX, TOKEN_KIND_INDEX + 125)
    pointers = struct.unpack("<7I", span(DISPATCH_POINTERS, DISPATCH_POINTERS + 28))
    require(pointers == POINTER_TARGETS, "ReadNextToken dispatch pointers differ")
    require(dict(sorted(Counter(kinds).items())) == INDEX_COUNTS, "ReadNextToken category census differs")
    tokens = []
    names = set()
    for token_id, block in enumerate(return_blocks):
        code = span(block, block + 6)
        require(code[0] == 0xB8 and code[5] == 0xC3, f"token-name return block differs: {token_id}")
        string_va = struct.unpack_from("<I", code, 1)[0]
        name = string_at(string_va)
        require(name not in names, f"duplicate retail token name: {name}")
        names.add(name)
        kind_index = kinds[token_id + 1]
        tokens.append({
            "tokenId": token_id,
            "name": name,
            "nameVa": f"0x{string_va:08x}",
            "returnBlockVa": f"0x{block:08x}",
            "parseIndex": kind_index,
            "parseKind": CATEGORY_NAMES[kind_index],
            "dispatchTargetVa": f"0x{pointers[kind_index]:08x}",
        })
    require(len(tokens) == len(names) == 124, "retail token registry census differs")
    require(string_at(0x006332A0) == "***Unknown_Token***", "unknown-token string differs")
    require(kinds[0] == 0, "unknown token does not use reject category")
    return tokens, kinds


def validate_parent(root: Path) -> tuple[dict[str, Any], dict[int, dict[str, str]]]:
    ready = read_json(root / PARENT_RELATIVE / "campaign.ready.json")
    require(ready.get("generation") == 17, "parent generation differs")
    require(ready.get("counts") == PARENT_COUNTS, "parent counts differ")
    require(ready.get("reducer", {}).get("id") == PARENT_REDUCER_ID, "parent reducer differs")
    functions = read_tsv(root / PARENT_RELATIVE / "campaign-functions.tsv", campaign=True)
    contracts = read_tsv(root / PARENT_RELATIVE / "campaign-contracts.tsv", campaign=True)
    questions = read_tsv(root / PARENT_RELATIVE / "campaign-questions.tsv", campaign=True)
    function = [row for row in functions if row["entityKey"] == ENTITY_KEY]
    contract = [row for row in contracts if row["contractId"] == CONTRACT_ID]
    question = [row for row in questions if row["questionId"] == QUESTION_ID]
    require(len(function) == len(contract) == len(question) == 1, "parent parser frontier census differs")
    require(
        function[0]["entryVa"] == "0x004f57b0"
        and function[0]["currentName"] == "CTokenArchive__ReadNextToken"
        and function[0]["semanticGrade"] == "OPAQUE",
        "parent parser function differs",
    )
    require(
        contract[0]["entityKey"] == ENTITY_KEY
        and contract[0]["contractState"] == "OPEN"
        and contract[0]["semanticGrade"] == "C0_OPAQUE"
        and contract[0]["questionIds"] == QUESTION_ID,
        "parent parser contract differs",
    )
    require(
        question[0]["entityKey"] == ENTITY_KEY
        and question[0]["state"] == "OPEN"
        and question[0]["lastOutcome"] == "UNSCORED",
        "parent parser question differs",
    )
    by_address = {int(row["entryVa"], 16): row for row in functions}
    return ready, by_address


def validate_ghidra_source(root: Path) -> dict[str, Any]:
    manifest_path = root / (
        "local-lab/ghidra-mission-native-setpos-live-promotion-20260809-v1/"
        "backups/post-live/backup_manifest.json"
    )
    manifest = read_json(manifest_path)
    destination = manifest.get("destination", {})
    expected = {
        row["relative_path"]: (row["size"], row["sha256"])
        for row in destination.get("files", [])
    }
    require(
        manifest.get("sourceStable") is True
        and manifest.get("copyComparison", {}).get("matches") is True
        and destination.get("fileCount") == 19
        and destination.get("totalBytes") == 186_485_637
        and len(expected) == 19,
        "SetPos POST backup manifest differs",
    )
    require(D_BACKUP_ROOT.is_dir(), "D-drive SetPos POST disaster backup is absent")
    disaster_manifest_path = D_BACKUP_ROOT / "backup_manifest.json"
    disaster_manifest = read_json(disaster_manifest_path)
    disaster_source = {
        row["relative_path"]: (row["size"], row["sha256"])
        for row in disaster_manifest.get("source", {}).get("files", [])
    }
    disaster_destination = {
        row["relative_path"]: (row["size"], row["sha256"])
        for row in disaster_manifest.get("destination", {}).get("files", [])
    }
    disaster_comparison = disaster_manifest.get("copyComparison", {})
    require(
        disaster_manifest.get("schemaVersion") == "onslaught-ghidra-project-backup.v2"
        and disaster_manifest.get("sourceStable") is True
        and disaster_comparison.get("matches") is True
        and all(disaster_comparison.get(key) == 0 for key in (
            "missingCount", "extraCount", "sizeDiffCount", "hashDiffCount"
        ))
        and disaster_source == expected
        and disaster_destination == expected,
        "D-drive Ghidra disaster-backup manifest differs",
    )
    actual_paths = {
        path.relative_to(D_BACKUP_ROOT).as_posix(): path
        for path in D_BACKUP_ROOT.rglob("*")
        if path.is_file() and path != disaster_manifest_path
    }
    require(set(actual_paths) == set(expected), "D-drive Ghidra snapshot file set differs")
    for relative, identity in expected.items():
        path = actual_paths[relative]
        require((path.stat().st_size, sha256_file(path)) == identity, f"D-drive Ghidra file differs: {relative}")
    for log_name in ("headless-decompile.log", "headless-createbytype.log"):
        text = (root / EVIDENCE_RELATIVE / log_name).read_text(encoding="utf-8", errors="strict")
        require(str(D_BACKUP_ROOT) in text, f"{log_name} does not bind the D-drive backup")
        require("Processing read-only project file: /BEA.exe" in text, f"{log_name} was not read-only")
        require("SCRIPT ERROR" not in text and "ERROR REPORT" not in text, f"{log_name} contains an error")
    index = read_tsv(root / EVIDENCE_RELATIVE / "ghidra-decompile/index.tsv")
    require(len(index) == 26 and all(row["status"] == "OK" for row in index), "Ghidra decompile index differs")
    factory_index = read_tsv(root / EVIDENCE_RELATIVE / "ghidra-createbytype/index.tsv")
    require(len(factory_index) == 1 and factory_index[0]["address"] == "0x004cc020" and factory_index[0]["status"] == "OK", "factory decompile index differs")
    return {
        "path": str(D_BACKUP_ROOT),
        "projectName": "BEA",
        "fileCount": 19,
        "totalBytes": 186_485_637,
        "canonicalInventorySha256": sha256_bytes(
            "".join(f"{name}\t{size}\t{digest}\n" for name, (size, digest) in sorted(expected.items())).encode("utf-8")
        ),
        "sourceManifest": stamp(manifest_path, root),
        "disasterBackupManifest": stamp(disaster_manifest_path, root),
        "accessMode": "READ_ONLY_NOANALYSIS",
    }


def validate_corpus(root: Path, tokens: list[dict[str, Any]]) -> tuple[dict[int, dict[str, Any]], dict[str, Any]]:
    by_name = {row["name"]: row for row in tokens}
    corpus_paths = sorted((root / "local-lab/safe-copy-bea-pristine/data/ParticleSets").glob("*.par"))
    require([path.name for path in corpus_paths] == ["Frontend.par", "MainSet.par", "ModelViewer.par"], "particle corpus file set differs")
    descriptor_names: set[str] = set()
    file_lines: dict[str, list[bytes]] = {}
    for path in corpus_paths:
        raw = path.read_bytes()
        require(raw.endswith(b"\r\n"), f"particle file lacks final CRLF: {path.name}")
        require(b"\n" not in raw.replace(b"\r\n", b""), f"particle file has lone LF: {path.name}")
        lines = [line for line in raw.split(b"\r\n") if line]
        file_lines[path.name] = lines
        for line in lines:
            if line.startswith(b"Particle_Descriptor_Name "):
                descriptor_names.add(line.split(b" ", 1)[1].decode("ascii"))
    occurrences: Counter[int] = Counter()
    files: dict[int, set[str]] = defaultdict(set)
    shape_counts: dict[int, Counter[str]] = defaultdict(Counter)
    category_occurrences: Counter[str] = Counter()
    descriptor_types: Counter[int] = Counter()
    previous: tuple[int, str] | None = None
    velocity_predecessors = []
    for file_name, lines in file_lines.items():
        previous = None
        for line in lines:
            if line == b"*" * 65:
                key, value = "*****************************************************************", ""
            else:
                raw_key, separator, raw_value = line.partition(b" ")
                require(separator == b" " or raw_key.decode("ascii") in by_name, f"malformed corpus line in {file_name}")
                key, value = raw_key.decode("ascii"), raw_value.decode("ascii")
            require(key in by_name, f"unknown particle token in {file_name}: {key}")
            token = by_name[key]
            token_id = token["tokenId"]
            kind = token["parseKind"]
            occurrences[token_id] += 1
            files[token_id].add(file_name)
            category_occurrences[kind] += 1
            if kind == "MARKER_NO_VALUE":
                require(value == "", f"marker unexpectedly has a value: {key}")
                shape = "NO_VALUE"
            elif kind == "DIRECT_INT":
                require(len(value.split()) == 1, f"integer token has multiple fields: {key}")
                int(value, 10)
                shape = "SINGLE_INTEGER"
            elif kind == "DIRECT_FLOAT":
                fields = value.split()
                if token_id == 32:
                    require(
                        len(fields) == 1 or (len(fields) == 2 and fields[1] == "NONE"),
                        "Velocity_Randomness has a named or malformed ignored suffix",
                    )
                    float(fields[0])
                    shape = "FLOAT_WITH_IGNORED_" + ("MISSING_SUFFIX" if len(fields) == 1 else "NONE")
                else:
                    require(len(fields) == 1, f"float token has multiple fields: {key}")
                    float(fields[0])
                    shape = "SINGLE_FLOAT"
            elif kind == "RAW_REMAINDER_STRING":
                require(value != "", f"string token has no remainder: {key}")
                shape = "RAW_REMAINDER"
            elif kind == "FLOAT_WITH_OPTIONAL_REFERENCE":
                first, separator, suffix = value.partition(" ")
                float(first)
                require(not suffix or suffix == "NONE" or suffix in descriptor_names, f"unresolved float-reference name: {suffix}")
                shape = "FLOAT_PLUS_" + ("MISSING_SUFFIX" if not separator else "NONE" if suffix == "NONE" else "NAMED_REFERENCE")
            elif kind == "REFERENCE_NAME":
                require(value == "NONE" or value in descriptor_names, f"unresolved descriptor reference: {value}")
                shape = "NONE" if value == "NONE" else "NAMED_REFERENCE"
            else:
                raise ProofError(f"unsupported corpus category: {kind}")
            shape_counts[token_id][shape] += 1
            if token_id == 3:
                descriptor_types[int(value, 10)] += 1
            if token_id == 32:
                require(previous is not None, "Velocity_Randomness has no predecessor")
                velocity_predecessors.append((previous, value))
            previous = (token_id, value)
    require(set(occurrences) == set(range(124)), "shipped corpus does not exercise all 124 retail token IDs")
    require(sum(occurrences.values()) == 27_186, "particle corpus line census differs")
    require(dict(sorted(category_occurrences.items())) == dict(sorted(CORPUS_CATEGORY_OCCURRENCES.items())), "particle corpus category census differs")
    expected_types = {1: 405, 2: 338, 4: 40, 5: 97, 6: 258, 7: 77, 8: 100, 9: 14, 10: 46, 11: 13, 12: 24, 13: 67}
    require(dict(sorted(descriptor_types.items())) == expected_types, "particle descriptor type census differs")
    require(len(velocity_predecessors) == 338, "Velocity_Randomness census differs")
    require(all(previous_id == 31 for (previous_id, _), _ in velocity_predecessors), "Velocity_Randomness predecessor differs")
    previous_suffixes = Counter(
        previous_value.partition(" ")[2] if " " in previous_value else ""
        for (_, previous_value), _ in velocity_predecessors
    )
    velocity_suffixes = Counter(
        value.partition(" ")[2] if " " in value else ""
        for _, value in velocity_predecessors
    )
    require(previous_suffixes == velocity_suffixes == Counter({"NONE": 336, "": 2}), "Velocity_Randomness masking corpus differs")
    result = {}
    for token in tokens:
        token_id = token["tokenId"]
        result[token_id] = {
            "occurrences": occurrences[token_id],
            "files": sorted(files[token_id]),
            "valueShapes": dict(sorted(shape_counts[token_id].items())),
        }
    summary = {
        "files": 3,
        "lines": 27_186,
        "descriptors": sum(descriptor_types.values()),
        "uniqueDescriptorNames": len(descriptor_names),
        "descriptorTypeCounts": {str(key): value for key, value in sorted(descriptor_types.items())},
        "parseCategoryOccurrences": dict(sorted(category_occurrences.items())),
        "velocityRandomnessMask": {
            "occurrences": 338,
            "precedingTokenId": 31,
            "precedingNamedModifiers": 0,
            "velocityNamedModifiers": 0,
            "noneSuffixesEach": 336,
            "missingSuffixesEach": 2,
        },
    }
    return result, summary


def derive_writer_calls(root: Path, image: bytes, tokens: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[int, list[str]]]:
    xrefs = read_tsv(root / "local-lab/ghidra-fullpass-2026-07-23/exports/W007/xrefs.tsv")
    calls = []
    token_writers: dict[int, list[str]] = defaultdict(list)
    for row in xrefs:
        try:
            target = int(row["target_addr"], 16)
            call_va = int(row["from_addr"], 16)
        except ValueError:
            continue
        if target not in WRITER_TARGETS:
            continue
        call = va_bytes(image, call_va, call_va + 5)
        require(call[0] == 0xE8, f"writer xref is not a direct CALL: 0x{call_va:08x}")
        destination = call_va + 5 + struct.unpack_from("<i", call, 1)[0]
        require(destination == target, f"writer call target differs: 0x{call_va:08x}")
        prior2 = va_bytes(image, call_va - 2, call_va)
        prior4 = va_bytes(image, call_va - 4, call_va)
        if prior2[0] == 0x6A:
            token_id = prior2[1]
            push_va = call_va - 2
        elif prior4[0] == 0x6A and prior4[2:] == b"\x8b\xcf":
            token_id = prior4[1]
            push_va = call_va - 4
        else:
            raise ProofError(f"writer token push pattern differs: 0x{call_va:08x}")
        require(0 <= token_id < 124, f"writer token ID leaves registry: {token_id}")
        writer_kind = WRITER_TARGETS[target]
        parser_kind = tokens[token_id]["parseKind"]
        symmetry = "MATCH" if writer_kind == parser_kind else "MISMATCH"
        calls.append({
            "callVa": f"0x{call_va:08x}",
            "pushVa": f"0x{push_va:08x}",
            "writerVa": f"0x{target:08x}",
            "writerKind": writer_kind,
            "tokenId": token_id,
            "tokenName": tokens[token_id]["name"],
            "parserKind": parser_kind,
            "symmetry": symmetry,
            "callerEntry": row["from_function_addr"],
            "callerName": row["from_function"],
        })
        token_writers[token_id].append(writer_kind)
    calls.sort(key=lambda row: int(row["callVa"], 16))
    require(len(calls) == 141, "retail writer call census differs")
    require(Counter(row["writerKind"] for row in calls) == Counter(WRITER_COUNTS), "retail writer kind census differs")
    require(set(token_writers) == set(range(6, 124)), "retail field writers do not cover exactly token IDs 6..123")
    mismatches = [row for row in calls if row["symmetry"] == "MISMATCH"]
    require(
        len(mismatches) == 1
        and mismatches[0]["tokenId"] == 32
        and mismatches[0]["callVa"] == "0x004c19d1"
        and mismatches[0]["writerKind"] == "FLOAT_WITH_OPTIONAL_REFERENCE"
        and mismatches[0]["parserKind"] == "DIRECT_FLOAT",
        "writer/parser asymmetry population differs",
    )
    return calls, token_writers


def derive_loaders(
    root: Path,
    image: bytes,
    tokens: list[dict[str, Any]],
    function_rows: dict[int, dict[str, str]],
) -> list[dict[str, Any]]:
    decompile_root = root / EVIDENCE_RELATIVE / "ghidra-decompile"
    rows = []
    for type_id, class_name, address, filename, expected_tokens, expected_count in LOADER_SPECS:
        source = (decompile_root / filename).read_text(encoding="utf-8")
        require("CTokenArchive__ReadNextToken" in source and "return 1;" in source, f"loader loop differs: {class_name}")
        if type_id == 12:
            observed = {
                int(value, 0)
                for value in re.findall(r"local_[0-9a-z]+\s*==\s*(0x[0-9a-f]+|\d+)", source)
                if int(value, 0) != 5
            }
        else:
            observed = {
                int(value, 0)
                for value in re.findall(r"(?m)^\s*case\s+(0x[0-9a-f]+|\d+):", source)
            }
        require(observed == set(expected_tokens), f"loader token population differs: {class_name}")
        function = function_rows.get(address)
        require(function is not None, f"parent function row missing: 0x{address:08x}")
        body_bytes = int(function["bodyBytes"])
        body_raw = va_bytes(image, address, address + body_bytes)
        current_name = function["currentName"]
        require(current_name.startswith(class_name + "__"), f"loader RTTI owner differs: {class_name}")
        rows.append({
            "typeId": type_id,
            "className": class_name,
            "loaderVa": f"0x{address:08x}",
            "currentName": current_name,
            "proposedName": current_name if type_id == 13 else class_name + "__LoadTokenFields",
            "proposedSignature": f"int __thiscall {class_name}__LoadTokenFields(void *this, void *token_archive)",
            "bodyBytes": body_bytes,
            "bodySha256": sha256_bytes(body_raw),
            "bodyRangeSetSha256": function["bodyRangeSetSha256"],
            "corpusDescriptors": expected_count,
            "acceptedTokenIds": ";".join(str(value) for value in expected_tokens),
            "acceptedTokenNames": ";".join(tokens[value]["name"] for value in expected_tokens),
            "terminatorTokenId": 5,
            "staticVerdict": "EXACT_RTTI_OWNER_FACTORY_TYPE_AND_TOKEN_SWITCH",
            "limitations": "TYPE3_DORMANT_IN_SHIPPED_CORPUS" if type_id == 3 else "RUNTIME_SIDE_EFFECTS_NOT_REPLAYED",
        })
    require(sum(row["corpusDescriptors"] for row in rows) == 1479, "loader descriptor census differs")
    return rows


def contract_record() -> dict[str, Any]:
    return {
        "entityKey": ENTITY_KEY,
        "contractId": CONTRACT_ID,
        "questionId": QUESTION_ID,
        "currentName": "CTokenArchive__ReadNextToken",
        "proposedSemanticGrade": "C1_STATIC",
        "receiver": (
            "CTokenArchive workspace: source pointer +0x0; pending reference count +0x8; "
            "10,000 fixup-target pointers from +0x0c; 10,000 allocated reference-name pointers "
            "from +0x9c4c; allocated workspace size 0x1388c"
        ),
        "inputs": (
            "this; required out_token_id; category-dependent out_int_or_ref_index, out_float, "
            "and out_string; one line supplied through CTokenArchive__ReadLine"
        ),
        "returns": (
            "1 for recognized markers and successfully parsed category paths; 0 for unknown token, "
            "missing required direct-output pointer, or missing required second scanned word"
        ),
        "writes": (
            "999-byte global line/token/value scratch; *out_token_id; category output; for reference "
            "categories an allocated remainder string at names[pending_count] and pending_count++"
        ),
        "sideEffects": (
            "reference-name allocation through the retail memory manager; tokens 49..57 scale direct "
            "color values by approximately 1/255 when no reference suffix exists"
        ),
        "preconditions": (
            "out_token_id is non-null; direct INT/FLOAT/STRING and REFERENCE categories require their "
            "documented output pointer and a second scanned word; caller supplies 1000-byte string buffers"
        ),
        "failureModes": (
            "unknown names return 0 after writing -1; direct categories fail closed on missing outputs/value; "
            "FLOAT_WITH_OPTIONAL_REFERENCE does not equivalently validate output pointers or scan count; "
            "no observed pending-reference bound check protects the 10,000-slot arrays"
        ),
        "ordering": (
            "read line -> sscanf first two words -> case-sensitive linear search IDs 0..123 -> write token ID -> "
            "dispatch through the 125-byte kind table -> parse/store -> return"
        ),
        "retailDefect": {
            "tokenId": 32,
            "tokenName": "Velocity_Randomness",
            "readerKind": "DIRECT_FLOAT",
            "writerKind": "FLOAT_WITH_OPTIONAL_REFERENCE",
            "loaderBehavior": (
                "CPDEmitter's type-2 loader passes the stale prior out_int_or_ref_index to "
                "RegisterReferenceFixup for token 32 because the direct-float reader never updates it"
            ),
            "shippedMask": (
                "all 338 token-32 lines immediately follow token 31; both fields have 336 NONE suffixes, "
                "two missing suffixes, and zero named modifiers, so shipped resolution collapses to null"
            ),
            "status": "PROVEN_STATIC_RETAIL_ASYMMETRY_MASKED_BY_SHIPPED_CORPUS",
        },
        "remainingUncertainty": (
            "runtime frequency and malformed-input causality; allocation-failure behavior; >998-byte lines; "
            "pending-reference overflow; behavior of authored token-32 named modifiers; full downstream particle effects"
        ),
        "cheapestFalsifier": (
            "load one disposable particle-set copy with a named token-31 or token-32 modifier while instrumenting "
            "pending slots and CPDEmitter +0x7c/+0x84 fixup destinations; never modify shipped data in place"
        ),
    }


def render_tsv(rows: list[dict[str, Any]], columns: list[str]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=columns, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in columns})
    return stream.getvalue().encode("utf-8")


def derive(root: Path) -> tuple[dict[str, Any], dict[str, bytes]]:
    inputs = exact_inputs(root)
    parent, function_rows = validate_parent(root)
    ghidra_source = validate_ghidra_source(root)
    image = (root / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup").read_bytes()
    tokens, _kinds = derive_static_tables(image)
    corpus, corpus_summary = validate_corpus(root, tokens)
    writer_calls, token_writers = derive_writer_calls(root, image, tokens)
    loader_rows = derive_loaders(root, image, tokens, function_rows)

    token_rows = []
    for token in tokens:
        token_id = token["tokenId"]
        writer_kinds = sorted(set(token_writers.get(token_id, [])))
        if token_id < 6:
            symmetry = "ARCHIVE_CONTROL_NOT_EMITTED_BY_FIELD_WRITERS"
        elif token_id == 32:
            symmetry = "RETAIL_ASYMMETRY_MASKED_BY_SHIPPED_CORPUS"
        else:
            symmetry = "MATCH"
        token_rows.append({
            **token,
            "corpusOccurrences": corpus[token_id]["occurrences"],
            "corpusFiles": ";".join(corpus[token_id]["files"]),
            "valueShapes": ";".join(f"{key}:{value}" for key, value in corpus[token_id]["valueShapes"].items()),
            "writerKinds": ";".join(writer_kinds),
            "writerCallCount": len(token_writers.get(token_id, [])),
            "writerSymmetry": symmetry,
            "colorScaleOneOver255": str(49 <= token_id <= 57).lower(),
        })

    contract = contract_record()
    outputs = {
        "tokens.tsv": render_tsv(token_rows, [
            "tokenId", "name", "nameVa", "returnBlockVa", "parseIndex", "parseKind",
            "dispatchTargetVa", "corpusOccurrences", "corpusFiles", "valueShapes",
            "writerKinds", "writerCallCount", "writerSymmetry", "colorScaleOneOver255",
        ]),
        "writer-calls.tsv": render_tsv(writer_calls, [
            "callVa", "pushVa", "writerVa", "writerKind", "tokenId", "tokenName",
            "parserKind", "symmetry", "callerEntry", "callerName",
        ]),
        "descriptor-loaders.tsv": render_tsv(loader_rows, [
            "typeId", "className", "loaderVa", "currentName", "proposedName",
            "proposedSignature", "bodyBytes", "bodySha256", "bodyRangeSetSha256",
            "corpusDescriptors", "acceptedTokenIds", "acceptedTokenNames", "terminatorTokenId",
            "staticVerdict", "limitations",
        ]),
        "readnexttoken-contract.json": (json.dumps(contract, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    }
    proof_material = b"".join(name.encode("utf-8") + b"\0" + outputs[name] for name in sorted(outputs))
    proof_id = "TPC-" + sha256_bytes(proof_material)[:16]
    mismatches = [row for row in writer_calls if row["symmetry"] == "MISMATCH"]
    author = stamp(Path(__file__).resolve(), root)
    stable = {
        "schema": SCHEMA,
        "verdict": "READY",
        "claim": CLAIM,
        "proofId": proof_id,
        "parent": {
            "path": PARENT_RELATIVE.as_posix(),
            "generation": parent["generation"],
            "readySha256": PARENT_READY_SHA256,
            "reducerId": PARENT_REDUCER_ID,
            "authoritySha256": PARENT_AUTHORITY_SHA256,
        },
        "inputs": inputs,
        "ghidraSource": ghidra_source,
        "author": author,
        "results": {
            "retailTokenIds": 124,
            "retailTokenNames": 124,
            "shippedCorpusKeysCovered": 124,
            "shippedCorpus": corpus_summary,
            "writerCalls": len(writer_calls),
            "writerTokenIdsCovered": len(token_writers),
            "writerParserMismatches": len(mismatches),
            "descriptorLoaders": len(loader_rows),
            "descriptorTypesUsed": 12,
            "descriptorTypesDormant": [3],
            "parserBody": {
                "entryVa": "0x004f57b0",
                "bytes": 789,
                "sha256": "e77885aa506084274deabe51f714adb713314e84b217e8736ba7153afe87cc58",
            },
            "workspace": {
                "allocationBytes": 80_012,
                "sourceOffset": "0x0",
                "pendingReferenceCountOffset": "0x8",
                "fixupTargetArrayOffset": "0x0c",
                "referenceNameArrayOffset": "0x9c4c",
                "referenceCapacity": 10_000,
                "observedBoundsCheck": False,
            },
            "retailDefect": contract["retailDefect"],
        },
        "contract": contract,
        "limitations": [
            "This proof is static and specimen-bound; it does not replay the game or establish runtime frequency.",
            "Decompiler text is pinned corroboration. Token names, kinds, writer calls, body identities, and corpus facts are independently rederived from pristine bytes and authored files.",
            "C1_STATIC is bounded understanding, not proof of every malformed-input, allocation-failure, or downstream particle behavior.",
            "The token-32 defect is proven as an asymmetry and masked by shipped data; a named-modifier runtime outcome remains an explicit falsifier, not an observed shipped failure.",
            "No Ghidra or retail executable mutation is performed by this proof.",
        ],
    }
    return stable, outputs


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".partial", dir=path.parent)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def expected_output_stamps(outputs: dict[str, bytes]) -> dict[str, dict[str, Any]]:
    return {
        name: {"path": (EVIDENCE_RELATIVE / name).as_posix(), "bytes": len(data), "sha256": sha256_bytes(data)}
        for name, data in sorted(outputs.items())
    }


def build(root: Path) -> dict[str, Any]:
    evidence = root / EVIDENCE_RELATIVE
    ready_path = evidence / READY_NAME
    if ready_path.exists():
        return verify(root)
    author_start = Path(__file__).resolve().read_bytes()
    stable, outputs = derive(root)
    for name, data in outputs.items():
        write_atomic(evidence / name, data)
    stable_check, outputs_check = derive(root)
    require(stable_check == stable and outputs_check == outputs, "proof derivation changed before publication")
    require(Path(__file__).resolve().read_bytes() == author_start, "proof author changed during execution")
    receipt = {
        **stable,
        "generatedAtUtc": datetime.now(timezone.utc).isoformat(),
        "outputs": expected_output_stamps(outputs),
    }
    for name, expected in receipt["outputs"].items():
        require(stamp(evidence / name, root) == expected, f"staged output differs: {name}")
    write_atomic(ready_path, (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return verify(root)


def verify(root: Path) -> dict[str, Any]:
    evidence = root / EVIDENCE_RELATIVE
    ready_path = evidence / READY_NAME
    require(ready_path.is_file(), "proof READY is absent")
    receipt = read_json(ready_path)
    stable, outputs = derive(root)
    for key, expected in stable.items():
        require(receipt.get(key) == expected, f"proof receipt differs: {key}")
    require(set(receipt) == set(stable) | {"generatedAtUtc", "outputs"}, "proof receipt shape differs")
    datetime.fromisoformat(str(receipt["generatedAtUtc"]).replace("Z", "+00:00"))
    expected_stamps = expected_output_stamps(outputs)
    require(receipt.get("outputs") == expected_stamps, "proof output manifest differs")
    for name, data in outputs.items():
        path = evidence / name
        require(path.is_file() and path.read_bytes() == data, f"proof output differs: {name}")
        require(path.lstat().st_nlink == 1 and not path.is_symlink(), f"proof output is linked: {name}")
    require(ready_path.lstat().st_nlink == 1 and not ready_path.is_symlink(), "proof READY is linked")
    return receipt


def selftest(root: Path) -> None:
    image = bytearray((root / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup").read_bytes())
    offset = pe_offset(bytes(image), TOKEN_KIND_INDEX + 33)
    image[offset] = 7
    try:
        derive_static_tables(bytes(image), require_specimen=False)
    except ProofError as exc:
        require("category census differs" in str(exc), "category poison failed at the intended gate")
    else:
        raise ProofError("category poison was accepted")

    image = bytearray((root / "local-lab/safe-copy-bea-pristine/BEA.exe.original.backup").read_bytes())
    offset = pe_offset(bytes(image), GET_TOKEN_NAME_JUMPS)
    first_return_block = struct.unpack_from("<I", image, offset)[0]
    struct.pack_into("<I", image, offset + 4, first_return_block)
    try:
        derive_static_tables(bytes(image), require_specimen=False)
    except ProofError as exc:
        require("duplicate retail token name" in str(exc), "name-table poison failed at the intended gate")
    else:
        raise ProofError("name-table poison was accepted")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify", "selftest"))
    args = parser.parse_args()
    root = root_path()
    try:
        if args.command == "build":
            receipt = build(root)
            print(f"TOKENARCHIVE_PARSER_CONTRACT_READY proofId={receipt['proofId']} sha256={sha256_file(root / EVIDENCE_RELATIVE / READY_NAME)}")
        elif args.command == "verify":
            receipt = verify(root)
            print(f"TOKENARCHIVE_PARSER_CONTRACT_VERIFIED proofId={receipt['proofId']} sha256={sha256_file(root / EVIDENCE_RELATIVE / READY_NAME)}")
        else:
            selftest(root)
            print("TOKENARCHIVE_PARSER_CONTRACT_SELFTEST_OK")
        return 0
    except (OSError, ProofError, ValueError, csv.Error, struct.error) as exc:
        print(f"TOKENARCHIVE_PARSER_CONTRACT_REFUSED: {exc}", file=os.sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
