#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Seal or reproduce the isolated 23-boundary CRT P0 admission.

The owner is read-only except for create-new publication of one aggregate
receipt.  It never launches Ghidra and never authorizes live or tracked-project
mutation.
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
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).resolve()
LANE_REL = Path("local-lab/ghidra-crt23-p0-boundary-scratch-20260814-v1")
LANE = REPO / LANE_REL
READY = LANE / "scratch-authority.ready.json"
SCHEMA = "bea.ghidra.crt-p0-boundary-scratch-authority.v1"
BASE_COMMIT = "1727d94ace29a60430d0982a188548d55aae5d1b"
COMPATIBLE_COMMIT = "e7aa7548fe99ff7866f57955624968b097375e20"
DERIVATION_BASE_COMMIT = "5f4319c3decf8f73a07d5ebb90812bad41f28185"

MANIFEST = REPO / "reverse-engineering/binary-analysis/crt-runtime-p0-function-boundaries-2026-08-14.tsv"
MUTATOR = REPO / "tools/GhidraApplyCrtP0Boundaries.java"
INVENTORY = REPO / "tools/ExportFullFunctionInventory.java"
DIFF = REPO / "tools/ghidra_inventory_diff.py"
BACKUP = REPO / "tools/ghidra_project_backup.py"
OPEN_PROBE = REPO / "tools/GhidraProjectOpenProbe.java"
DIAGNOSTIC = REPO / "tools/DiagnoseAddressListingState.java"

PROGRAM_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
DEMO_SHA256 = "d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2"
SOURCE_COHORT_SHA256 = "bc16df601740afec41bdba306d7e02996171da1cc10d3491da38d6d022bdbf5a"
TARGET_COUNT = 23
BODY_BYTES = 1131
BODY_RANGES = 24
BODY_INSTRUCTIONS = 312
PRE_FUNCTIONS = 8280
POST_FUNCTIONS = 8303
PRE_RANGES = 8400
POST_RANGES = 8424
PRE_INSTRUCTIONS = 550991
POST_INSTRUCTIONS = 551069
PRE_REFERENCES = 234495
POST_REFERENCES = 234506
FORBIDDEN = ("0x00542720", "0x005d0ad6", "0x005d0aea")
EXCLUDED_CANARY = "0x005b8500"
THUNK_ENTRY = "0x0045ac20"
THUNK_TARGET = "0x0045ac30"
THUNK_INHERITED_NAME = "CFEPGoodies__BuildStaticGoodieDataTable"

STAMPS = {
    MANIFEST: (6176, "c60359ecfd58e7c97c45a45e1b83d034e6cc104c222781f6f611e158b459d7df"),
    MUTATOR: (57698, "7ba41a9601de7039a49c346c968adabc368586672a188ae0d88d8b26ae1f338c"),
    INVENTORY: (23963, "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197"),
    DIFF: (9622, "b4956fbf9c9125cfdd7b7810cdc15f298fef8a081a880f82d6231a6dcbb25460"),
    BACKUP: (27502, "0f426982916f0aab982efe54664342a5d34607c2f89707159ecf6c07e205ad58"),
    OPEN_PROBE: (3452, "fab2f701dfefe8604c1718d007dbe0ad59d330a9b3ec081ef2f2fe253b441fab"),
    DIAGNOSTIC: (3956, "183394907659e7810c77a9720e1899fd8a6296e6e86673495d68a2764edefe69"),
}

FROZEN_STAMPS = {
    "crt-runtime-p0-function-boundaries-2026-08-14.tsv": STAMPS[MANIFEST],
    "crt22-analyze.py": (67149, "259e6e62b5d799b8ae5004dd85f0997e56556068f04ac40e668e358d37e48598"),
    "crt22-verify.py": (24641, "8bc41942f433a1f2585c05245a62eb14e31ee79dff198e9f705d82c22265ff27"),
    "current-8280-body-ranges.tsv": (1198388, "0101e6e8b34eaea8bd646a0fa9a8e4e448bef586c8b2b898c78241befde3aa6b"),
    "DiagnoseAddressListingState.java": STAMPS[DIAGNOSTIC],
    "diagnostic-addresses.txt": (88, "9da8bd194362ee3b0306d1de3fc68ef44c219e4184338a48783a7dfca3bf1505"),
    "ExportFullFunctionInventory.java": STAMPS[INVENTORY],
    "ghidra_inventory_diff.py": STAMPS[DIFF],
    "ghidra_project_backup.py": STAMPS[BACKUP],
    "GhidraApplyCrtP0Boundaries.java": STAMPS[MUTATOR],
    "GhidraProjectOpenProbe.java": STAMPS[OPEN_PROBE],
}

RUN_C_STAMPS = {
    "candidates.tsv": (12732, "d5442f9c0f991bd537cdf6191b3c16bd61a77a57c1cc6c80df12ebb8c7a15f3b"),
    "delta.tsv": (1325, "3f55b8126d6e676a34fe2107bf5ffb0cb97d75561cf38c013fae172d47f3b585"),
    "demo-twins.tsv": (6790, "5b666719bbdfbe194d54bca4baa5a08a93773a33314386a9819ddd3f22904502"),
    "disassembly.tsv": (22015, "96cecbe34493322c7ba44e478ae02065f8f87a8e9c6fe6deb7561e3d28487114"),
    "falsifiers.tsv": (1471, "88be5fe2994d4eebc1c65efd0b4111fe94f2b8050b3062e64109c1a5852ac5f9"),
    "input-manifest.json": (7027, "a98fcc7bb1447a53a4a35252cceede9d8cb4ed5f18bf63d936a2a7c3d1067b9c"),
    "lineage-validation.tsv": (3355, "cb1a1dfa6a95aa1fdfefba5fbe80e2587db4065abd10b2ea1e0acc88fd3dd2bd"),
    "promotion-cohort.tsv": (6949, SOURCE_COHORT_SHA256),
    "reconciliation.tsv": (753, "28390976a4570cb06b43f691119704226c50b14e2cf7c6201ba8d233fd6aa76b"),
    "report.md": (4675, "a8b9e68e77bb83fecab5fa7a56e68f42b4c4fea2fe4e0967ace438f456e6327c"),
    "result.ready.json": (2878, "dec2716598862c2838387e8a08fcd4a2f2172be4bebb06156ba56242a7fb995f"),
}

PRE_EXPORTS = {
    "boundaries.tsv": (8714, "2bddb34eb5ce07fb0a5cd0d2883ce8ba045b1ad01acd56d214efd7461ed8beeb"),
    "functions.tsv": (7161942, "c3942b9e340cef71b731290b845843697af5c53204449c51949b779e896272d6"),
    "program.tsv": (1267, "3e51ce1d5e926c632869b2058c9d89e91f48345a329a724ea9520570bd91212d"),
    "listing-state.tsv": (961, "999957bb3347c795ded269fb4a9735d767bcc382c01c7af78dd307fe0adf97f4"),
}
APPLY_EXPORTS = {
    "boundaries.tsv": (11071, "3a2cea602914b776376229542e997d9363525a9c13ab5774b1efeb9c94e5957b"),
    "functions.tsv": (7177146, "2c1e2842fabd8be4cb840c35bc56074559041404e0c474fee50aad6e98cf4dc5"),
    "program.tsv": (1267, "7bce8becc7dc4cbbf9f513bec0effc75889e90079882c5623933aba335f59a4b"),
    "listing-state.tsv": (1033, "ffedbd49109971f452ce0518cf7defd2ac70cdc8173830b5cccc58f08853d8bf"),
}
READBACK_EXPORTS = {**APPLY_EXPORTS, "boundaries.tsv": (
    11094, "8d9999a7396378776c9ac8c664b0b5cc330fcd400a37ed0789ff614daa117485"
)}

BASE_PROJECT = (19, 186960773, "ae422079966978ec2f8f5b951b0ef5812b1074bd708ab8d782179f51c90efcf2")
DB_18613 = (68337664, "615497847b0c732077ee7164b0973b9012092523e9ad99b91c21781952420ebe")
OPENED_PROJECTS = {
    "external-output": (19, 186977157, "7c9e439b0f8812b640eedf64b0151eddaa06a4e9a9a96499197674f6db000698"),
    "external-ready": (19, 186977157, "804369ed157e242d63268398c64703a7a85c2686a558ae5c8fefe72902176691"),
    "probe-after-one": (19, 186977157, "337b86a5c264cb68acfb4e1433405e74a604b5a4f84f42a3b80a0106b1e885c3"),
    "probe-post-inner": (19, 186977157, "b2f2ac9e2d2bced0b07f92711ebdfb85b27726aafc2bb127fc6f2a17ebd5f013"),
    "replica-a": (19, 186977157, "11754ca93e1a3826c97500fe9eb38c73dc3348843db3b5b908de0529e3550705"),
    "replica-b": (19, 186977157, "cb71c4d6175e7318647ddf484873e8cacbbf5a8ab2a8a46e2a1fc74f3fa3d876"),
}

PRE_PROGRAM = {
    "programName": "BEA.exe", "executableMD5": PROGRAM_MD5,
    "executableSHA256": PROGRAM_SHA256, "imageBase": "0x00400000",
    "language": "x86:LE:32:default", "compilerSpec": "windows",
    "memorySha256": "5398f750f1ffb59873a6ec7e1750b51d11b5b844a8fda8d4e43649b5b9e5089d",
    "functions": "8280", "instructions": "550991",
    "instructionLayoutSha256": "6e432dd36dd5964a95d982091188a24d1a3add46ade7b44a387bac205c475658",
    "definedData": "48585",
    "definedDataSha256": "3b87eb91228e20c1d627318cc2563811043c1500af1497575ab128e7edf6e9e3",
    "undefinedData": "3908482", "symbolsUserDefined": "6104",
    "symbolsAnalysis": "18006", "symbolsImported": "907",
    "symbolsDefaultOther": "61684",
    "nonFunctionSymbolsSha256": "3e9936f251588865a77b62bdf577c110a7346e57c0e5a234e1feab9ab41622ac",
    "references": "234495",
    "referencesSha256": "e916cafb16fac23196717e182645066ba48f3cb6eccf10713be8b1435b3233e7",
    "comments": "9199",
    "commentsSha256": "37a7b6d7dd4049a2e45e7d941de0bde92fadca50a03369e2401046b7cab3e927",
    "relocations": "0",
    "block:Headers": "0x00400000-0x00400fff size=4096 x=false",
    "block:.text": "0x00401000-0x005d7fff size=1929216 x=true",
    "block:.rdata": "0x005d8000-0x00621fff size=303104 x=false",
    "block:.data": "0x00622000-0x009d4613 size=3876372 x=false",
    "block:.rsrc": "0x009d5000-0x009d7fff size=12288 x=false",
    "block:tdb": "0xffdff000-0xffdfffff size=4096 x=false",
}
POST_PROGRAM = {
    **PRE_PROGRAM, "functions": "8303", "instructions": "551069",
    "instructionLayoutSha256": "f27118e20464b70b370ac71c6d5f437d719cf75e8080b36bf83a3a518528219f",
    "undefinedData": "3908140", "symbolsDefaultOther": "61704",
    "references": "234506",
    "referencesSha256": "64db5ac9599f54d53578a69a5e7d500d5aa965100094e2b42f80d5e6bc6c1df2",
}

CLAIMS = (
    "Corrected CRT22 run-c is pinned and reproduced byte-for-byte twice; run-a and run-b are not authorities.",
    "Two disposable db.18613 replicas persist exactly 23 P0 boundaries in 24 ranges / 1,131 bytes and separately read back the same 8,303-function state.",
    "Every field of all 8,280 PRE function rows is unchanged; the only new rows are the 23 audited boundaries.",
    "0x00542720, 0x005D0AD6, and 0x005D0AEA remain forbidden entries, 0x005B8500 remains excluded, and 0x0045AC20 is a thunk to 0x0045AC30.",
    "The thunk's default presentation inherits its existing target name and signature relationally; no name or signature setter is called and no pre-existing row changes.",
    "Two forced failures reopen to exact PRE and two external publication probes refuse before mutation.",
    "Memory, defined data, stored non-function symbols, comments, and all mutation-external function state remain exact; instruction/reference changes are body-contained by the mutator's pre-commit gates.",
    "Live and tracked Ghidra promotion remain forbidden and require a separate authorized ceremony.",
)


class AuthorityError(ValueError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise AuthorityError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_stamp(path: Path, expected: tuple[int, str], label: str) -> None:
    require(path.is_file(), f"{label} missing")
    require((path.stat().st_size, sha256_file(path)) == expected, f"{label} stamp drift")


def stamp(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing file: {path}")
    return {"path": path.resolve().relative_to(REPO.resolve()).as_posix(),
            "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def portable(value: Any, label: str) -> None:
    require(isinstance(value, str) and value and "\\" not in value
            and not value.startswith("/") and ":" not in value
            and ".." not in PurePosixPath(value).parts,
            f"{label} must be a repository-relative POSIX path")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def read_tsv(path: Path, comments: bool = False) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        lines: Iterable[str] = stream
        if comments:
            lines = (line for line in stream if not line.startswith("#"))
        return list(csv.DictReader(lines, delimiter="\t"))


def parse_ranges(text: str) -> list[tuple[int, int]]:
    ranges = []
    for item in text.split(";"):
        start, end = item.split("-", 1)
        a, b = int(start, 16), int(end, 16)
        require(a < b, f"invalid range {item}")
        ranges.append((a, b))
    return ranges


def program_rows(path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for row in read_tsv(path):
        key, value = row.get("metric"), row.get("value")
        require(isinstance(key, str) and isinstance(value, str) and key not in result,
                f"invalid or duplicate program metric in {path}")
        result[key] = value
    return result


def pe_image(path: Path) -> tuple[bytes, int, list[tuple[int, int, int, int]]]:
    data = path.read_bytes()
    require(data[:2] == b"MZ", f"not a PE file: {path}")
    pe = struct.unpack_from("<I", data, 0x3c)[0]
    require(data[pe:pe + 4] == b"PE\0\0", f"invalid PE signature: {path}")
    sections, optional_size = struct.unpack_from("<H12xH", data, pe + 6)
    optional = pe + 24
    require(struct.unpack_from("<H", data, optional)[0] == 0x10b, "expected PE32")
    image_base = struct.unpack_from("<I", data, optional + 28)[0]
    table = optional + optional_size
    result = []
    for index in range(sections):
        row = table + index * 40
        virtual_size, virtual_address, raw_size, raw_offset = struct.unpack_from("<IIII", data, row + 8)
        result.append((virtual_address, max(virtual_size, raw_size), raw_offset, raw_size))
    return data, image_base, result


def pe_range_bytes(image: tuple[bytes, int, list[tuple[int, int, int, int]]],
                   ranges: list[tuple[int, int]]) -> bytes:
    data, image_base, sections = image
    output = bytearray()
    for start, end in ranges:
        rva, length = start - image_base, end - start
        matched = False
        for section_rva, span, raw_offset, raw_size in sections:
            if section_rva <= rva and rva + length <= section_rva + min(span, raw_size):
                offset = raw_offset + rva - section_rva
                output.extend(data[offset:offset + length])
                matched = True
                break
        require(matched, f"VA range is not file-backed: 0x{start:08x}-0x{end:08x}")
    return bytes(output)


def canonical_ledger(files: Iterable[dict[str, Any]], label: str) -> tuple[int, int, str]:
    rows: list[tuple[str, int, str]] = []
    for row in files:
        relative, size, digest = row.get("relative_path"), row.get("size"), row.get("sha256")
        require(isinstance(relative, str) and relative and "\\" not in relative
                and not relative.startswith("/") and ":" not in relative,
                f"{label} relative path")
        require(isinstance(size, int) and size >= 0, f"{label} size")
        require(isinstance(digest, str) and len(digest) == 64, f"{label} hash")
        rows.append((digest, size, relative))
    rows.sort(key=lambda item: item[2])
    require(len({row[2] for row in rows}) == len(rows), f"{label} duplicate path")
    encoded = b"".join(f"{digest}\t{size}\t{relative}\n".encode()
                        for digest, size, relative in rows)
    return len(rows), sum(row[1] for row in rows), hashlib.sha256(encoded).hexdigest()


def actual_project(root: Path, label: str) -> tuple[int, int, str]:
    require((root / "BEA.gpr").is_file() and (root / "BEA.rep").is_dir(),
            f"{label} project pair")
    paths = [root / "BEA.gpr", *(p for p in (root / "BEA.rep").rglob("*") if p.is_file())]
    rows = [{"relative_path": p.relative_to(root).as_posix(), "size": p.stat().st_size,
             "sha256": sha256_file(p)} for p in paths]
    return canonical_ledger(rows, label)


def inspection(path: Path, expected: tuple[int, int, str], label: str) -> None:
    value = read_json(path)
    require(value.get("schemaVersion") == "onslaught-ghidra-project-backup.v2", f"{label} schema")
    manifest = value.get("manifest")
    require(isinstance(manifest, dict), f"{label} manifest")
    require(canonical_ledger(manifest.get("files", []), label) == expected, f"{label} inventory")
    require(manifest.get("fileCount") == expected[0]
            and manifest.get("totalBytes") == expected[1]
            and manifest.get("structurallyComplete") is True, f"{label} summary")


def verify_inputs() -> list[dict[str, str]]:
    for path, expected in STAMPS.items():
        verify_stamp(path, expected, path.name)
    inputs = LANE / "inputs"
    for name, expected in FROZEN_STAMPS.items():
        verify_stamp(inputs / name, expected, f"frozen {name}")
    require((inputs / MUTATOR.name).read_bytes() == MUTATOR.read_bytes(), "tracked/frozen mutator differs")
    require((inputs / MANIFEST.name).read_bytes() == MANIFEST.read_bytes(), "tracked/frozen manifest differs")
    for run in ("run-c", "reproof-a-base5f", "reproof-b-base5f"):
        for name, expected in RUN_C_STAMPS.items():
            verify_stamp(inputs / run / name, expected, f"{run}/{name}")
    for name in RUN_C_STAMPS:
        original = (inputs / "run-c" / name).read_bytes()
        require(original == (inputs / "reproof-a-base5f" / name).read_bytes()
                == (inputs / "reproof-b-base5f" / name).read_bytes(),
                f"run-c reproof differs: {name}")

    ready = read_json(inputs / "run-c/result.ready.json")
    require(ready.get("schema") == "bea.re.crt22-current-gap-recovery.v1"
            and ready.get("baseCommit") == DERIVATION_BASE_COMMIT
            and ready.get("compatibleCommit") == BASE_COMMIT
            and ready.get("compatibleTrackedInputsUnchanged") is True
            and ready.get("verdict") == "READY_FOR_ISOLATED_SCRATCH_PROMOTION_ONLY",
            "run-c identity or verdict")
    require(tuple(value.lower() for value in ready.get("forbiddenEntries", [])) == FORBIDDEN,
            "run-c forbidden entries")
    require(ready.get("counts", {}).get("p0Creates") == TARGET_COUNT
            and ready.get("counts", {}).get("currentFunctions") == PRE_FUNCTIONS
            and ready.get("counts", {}).get("currentBodyRanges") == PRE_RANGES,
            "run-c counts")

    manifest = read_tsv(MANIFEST)
    require(len(manifest) == TARGET_COUNT, "manifest target count")
    entries = [row["entry"].lower() for row in manifest]
    require(entries == sorted(entries) and len(set(entries)) == TARGET_COUNT, "manifest entries")
    require(not set(FORBIDDEN + (EXCLUDED_CANARY,)).intersection(entries), "protected entry in manifest")
    promotion = {row["entry"].lower(): row for row in read_tsv(inputs / "run-c/promotion-cohort.tsv")
                 if row["priority"] == "P0"}
    require(set(promotion) == set(entries), "manifest/run-c P0 join")

    all_ranges: list[tuple[int, int]] = []
    for row in manifest:
        entry, source = row["entry"].lower(), promotion[row["entry"].lower()]
        require(source["action"] == "CREATE_FUNCTION_BOUNDARY"
                and source["body_ranges"].lower() == row["expectedRanges"].lower()
                and source["body_bytes"] == row["expectedBodyBytes"]
                and source["body_sha256"] == row["expectedBodyBytesSha256"]
                and row["contractIds"] == "BOUNDARY_ONLY"
                and row["promotionLane"] == "CRT22_P0_SCRATCH_ONLY",
                f"manifest/run-c field drift at {entry}")
        ranges = parse_ranges(row["expectedRanges"])
        require(sum(b - a for a, b in ranges) == int(row["expectedBodyBytes"]),
                f"manifest body size at {entry}")
        for a, b in ranges:
            require(not any(max(a, c) < min(b, d) for c, d in all_ranges),
                    f"manifest pairwise overlap at {entry}")
            all_ranges.append((a, b))
    require(len(all_ranges) == BODY_RANGES
            and sum(b - a for a, b in all_ranges) == BODY_BYTES,
            "manifest range/byte totals")

    owner_ranges = [(int(row["rangeMin"], 16), int(row["rangeEndExclusive"], 16))
                    for row in read_tsv(inputs / "current-8280-body-ranges.tsv", comments=True)]
    require(len(owner_ranges) == PRE_RANGES, "current body-range count")
    for a, b in all_ranges:
        require(not any(max(a, c) < min(b, d) for c, d in owner_ranges),
                f"current body overlap at 0x{a:08x}")

    retail = inputs / "specimens/retail-BEA.exe"
    demo = inputs / "specimens/demo-BEA.exe"
    verify_stamp(retail, (2506752, PROGRAM_SHA256), "pristine retail specimen")
    verify_stamp(demo, (2510848, DEMO_SHA256), "PC demo specimen")
    retail_image, demo_image = pe_image(retail), pe_image(demo)
    twins = {row["retail_entry"].lower(): row for row in read_tsv(inputs / "run-c/demo-twins.tsv")}
    disassembly: dict[str, int] = {}
    for row in read_tsv(inputs / "run-c/disassembly.tsv"):
        if row["segment_kind"] == "BODY":
            key = row["candidate_entry"].lower()
            disassembly[key] = disassembly.get(key, 0) + 1
    raw_twins = 0
    for row in manifest:
        entry = row["entry"].lower()
        ranges = parse_ranges(row["expectedRanges"])
        retail_bytes = pe_range_bytes(retail_image, ranges)
        require(hashlib.sha256(retail_bytes).hexdigest() == row["expectedBodyBytesSha256"],
                f"pristine body hash at {entry}")
        require(disassembly.get(entry) == int(row["expectedInstructionCount"]),
                f"run-c instruction count at {entry}")
        twin = twins.get(entry)
        require(twin is not None and twin["retail_ranges"].lower() == row["expectedRanges"].lower()
                and twin["body_bytes"] == row["expectedBodyBytes"]
                and twin["normalized_equal"] == "true" and twin["cfg_equal"] == "true",
                f"demo evidence join at {entry}")
        demo_bytes = pe_range_bytes(demo_image, parse_ranges(twin["demo_ranges"]))
        actual_raw = retail_bytes == demo_bytes
        require(actual_raw is (twin["raw_equal"] == "true"), f"demo raw equality at {entry}")
        raw_twins += int(actual_raw)
    require(sum(disassembly.values()) >= BODY_INSTRUCTIONS, "disassembly evidence total")
    require(raw_twins == 6, "target raw demo-twin count")
    return manifest


def verify_ready(path: Path, mode: str, run: str, output: tuple[int, str]) -> None:
    value = read_json(path)
    require(value.get("schemaVersion") == "bea.ghidra.crt-p0-boundaries.v1"
            and value.get("mode") == mode, f"{run} ready identity")
    require(value.get("program") == {"name": "BEA.exe", "md5": PROGRAM_MD5,
                                      "sha256": PROGRAM_SHA256}, f"{run} program")
    require(value.get("sourceCohortSha256") == SOURCE_COHORT_SHA256
            and value.get("bodyBytes") == BODY_BYTES
            and value.get("bodyRanges") == BODY_RANGES
            and value.get("preFunctionRanges") == PRE_RANGES
            and value.get("postFunctionRanges") == POST_RANGES,
            f"{run} cohort counts")
    require(tuple(value.get("protectedEntries", [])) == FORBIDDEN
            and value.get("excludedCanary") == EXCLUDED_CANARY,
            f"{run} protected entries")
    require(value.get("explicitBodySetsAuthorized") is True
            and value.get("postCountsPinned") is True
            and value.get("namesAuthorized") is False
            and value.get("metadataAuthorized") is False,
            f"{run} authority flags")
    counts_by_mode = {
        "dry": (PRE_FUNCTIONS, PRE_FUNCTIONS, PRE_INSTRUCTIONS, PRE_INSTRUCTIONS),
        "apply": (PRE_FUNCTIONS, POST_FUNCTIONS, PRE_INSTRUCTIONS, POST_INSTRUCTIONS),
        "readback": (POST_FUNCTIONS, POST_FUNCTIONS, POST_INSTRUCTIONS, POST_INSTRUCTIONS),
    }
    counts = value.get("counts", {})
    require((counts.get("targets"), counts.get("externalInstructions"),
             counts.get("ghidraBodyInstructions")) ==
            (TARGET_COUNT, BODY_INSTRUCTIONS, BODY_INSTRUCTIONS), f"{run} body counts")
    require(tuple(counts.get(key) for key in (
        "functionsBefore", "functionsAfter", "instructionsBefore", "instructionsAfter"
    )) == counts_by_mode[mode], f"{run} PRE/POST counts")
    require(value.get("separateReadbackRequired") is (mode != "readback"), f"{run} readback flag")
    expected_tool = {"path": (LANE_REL / "inputs" / MUTATOR.name).as_posix(),
                     "bytes": STAMPS[MUTATOR][0], "sha256": STAMPS[MUTATOR][1]}
    expected_manifest = {"path": MANIFEST.relative_to(REPO).as_posix(),
                         "bytes": STAMPS[MANIFEST][0], "sha256": STAMPS[MANIFEST][1]}
    expected_output = {"path": (LANE_REL / "runs" / run / "boundaries.tsv").as_posix(),
                       "bytes": output[0], "sha256": output[1]}
    require(value.get("tool") == expected_tool and value.get("manifest") == expected_manifest
            and value.get("output") == expected_output, f"{run} portable stamps")
    for item in (expected_tool, expected_manifest, expected_output):
        portable(item["path"], f"{run} path")
    datetime.fromisoformat(value["completedAtUtc"].replace("Z", "+00:00"))


def verify_function_state(manifest: list[dict[str, str]]) -> None:
    runs = LANE / "runs"
    pre = runs / "formal-replica-a-dry/functions.tsv"
    post = runs / "formal-replica-a-readback/functions.tsv"
    pre_rows = read_tsv(pre)
    post_rows = read_tsv(post)
    require(len(pre_rows) == PRE_FUNCTIONS and len(post_rows) == POST_FUNCTIONS,
            "full function inventory counts")
    before = {row["address"]: row for row in pre_rows}
    after = {row["address"]: row for row in post_rows}
    require(len(before) == PRE_FUNCTIONS and len(after) == POST_FUNCTIONS, "duplicate function entry")
    for address, row in before.items():
        require(after.get(address) == row, f"PRE function row changed at {address}")
    targets = {row["entry"].lower(): row for row in manifest}
    require(set(after) - set(before) == set(targets), "created function set")
    for address, expected in targets.items():
        row = after[address]
        require(row["bodyBytes"] == expected["expectedBodyBytes"]
                and row["bodyRanges"] == str(len(parse_ranges(expected["expectedRanges"])))
                and row["bodyDigest"] == expected["expectedRangeDigest"]
                and row["instrCount"] == expected["expectedInstructionCount"]
                and row["nameSource"] == "DEFAULT" and row["commentPresent"] == "false"
                and row["repeatableCommentPresent"] == "false" and row["tagCount"] == "0",
                f"created boundary fields at {address}")
        if address == THUNK_ENTRY:
            require(row["isThunk"] == "true" and row["thunkTarget"] == THUNK_TARGET
                    and row["name"] == THUNK_INHERITED_NAME
                    and row["sigSource"] == "USER_DEFINED", "thunk readback")
        else:
            require(row["isThunk"] == "false" and row["thunkTarget"] == ""
                    and row["name"] == "FUN_" + address[2:], f"default boundary at {address}")
    require(not set(FORBIDDEN + (EXCLUDED_CANARY,)).intersection(after), "protected entry created")


def verify_inventory_diff(path: Path, label: str) -> None:
    value = read_json(path)
    counts = value.get("counts", {})
    require((counts.get("before"), counts.get("after"), counts.get("created"),
             counts.get("destroyed"), counts.get("boundsChanged"),
             counts.get("namesChanged"), counts.get("signaturesChanged"),
             counts.get("paramCountChanged"), counts.get("thunkFlagChanged")) ==
            (PRE_FUNCTIONS, POST_FUNCTIONS, TARGET_COUNT, 0, 0, 0, 0, 0, 0),
            f"{label} inventory diff counts")
    require(value.get("destroyed") == [] and len(value.get("created", [])) == TARGET_COUNT,
            f"{label} inventory created/destroyed")
    dangerous = value.get("dangerous", {})
    require(all(dangerous.get(key) in (0, []) for key in dangerous), f"{label} dangerous diff")


def verify_projects() -> None:
    inspection(LANE / "tracked-base-inspection.json", BASE_PROJECT, "tracked base")
    inspection(LANE / "base-project-backup-inspection.json", BASE_PROJECT, "base backup")
    require(actual_project(LANE / "base-project-backup", "base backup actual") == BASE_PROJECT,
            "base backup actual inventory")
    receipt = read_json(LANE / "base-restore-open.ready.json")
    require(receipt.get("schemaVersion") == "onslaught-ghidra-project-backup.v2"
            and receipt.get("sourceStable") is True
            and receipt.get("copyComparison", {}).get("matches") is True,
            "backup/restore receipt")
    require(canonical_ledger(receipt.get("source", {}).get("files", []), "backup source") == BASE_PROJECT,
            "backup source inventory")
    opened = receipt.get("readonlyOpen", {})
    require(opened.get("opened") is True and opened.get("contentStable") is True
            and opened.get("exitCode") == 0
            and opened.get("observedProgramName") == "BEA.exe"
            and opened.get("observedProgramMd5") == PROGRAM_MD5
            and opened.get("observedProgramSha256") == PROGRAM_SHA256
            and opened.get("postOpenComparison", {}).get("matches") is True,
            "read-only restored open")
    restore_dirs = [path for path in (LANE / "restore-probe").iterdir() if path.is_dir()]
    require(len(restore_dirs) == 1
            and actual_project(restore_dirs[0], "restore probe actual") == BASE_PROJECT,
            "restore probe actual inventory")
    for name, expected in OPENED_PROJECTS.items():
        inspection(LANE / f"projects-{name}-inspection.json", expected, f"{name} inspection")
        require(actual_project(LANE / "projects" / name, f"{name} actual") == expected,
                f"{name} actual inventory")
        require(expected[0] == BASE_PROJECT[0] and expected[1] - BASE_PROJECT[1] == 16384,
                f"{name} exact physical delta")


def verify_compatibility() -> None:
    value = read_json(LANE / "e7aa-compatibility.json")
    require(value.get("schemaVersion") == "bea.ghidra.crt-p0-e7aa-compatibility.v1"
            and value.get("baseCommit") == BASE_COMMIT
            and value.get("targetCommit") == COMPATIBLE_COMMIT
            and value.get("verdict") == "COMPATIBLE_NO_LOAD_BEARING_INPUT_MOVED",
            "e7aa compatibility identity")
    changed = value.get("changedBetweenCommits")
    require(changed == [
        "rebuild/OnslaughtRebuild.Core.Tests/BattleEngineMovementContractTests.cs",
        "rebuild/OnslaughtRebuild.Core.Tests/Level100ChainAutopilot.cs",
        "rebuild/OnslaughtRebuild.Core.Tests/Level100ColdStartTests.cs",
        "rebuild/OnslaughtRebuild.Core.Tests/Level100FullChainTests.cs",
        "rebuild/OnslaughtRebuild.Core.Tests/ReplayTests.cs",
        "rebuild/OnslaughtRebuild.Core.Tests/SimulationTests.cs",
        "rebuild/OnslaughtRebuild.Core/Simulation.cs",
        "rebuild/OnslaughtRebuild.Core/SimulationConstants.cs",
        "rebuild/OnslaughtRebuild.Core/SimulationTypes.cs",
        "rebuild/PROVENANCE.md", "rebuild/README.md", "reverse-engineering/delta.md",
    ], "e7aa changed-path set")
    expected_inputs = [
        ("reverse-engineering/ghidra", "tree", None, None,
         "ccda09669b3ae74c11bfbcece95692e899833b6a"),
        ("reverse-engineering/binary-analysis/external-table-gap-function-boundaries-2026-08-13.tsv",
         "blob", 30020, "4293ebb936639299301985f128728b127ca60014693871a981d2324d47f2044f",
         "c3ec5e8f5dcda553fda8b3ae4c82aa4ad2e5ee9c"),
        ("reverse-engineering/binary-analysis/pc-demo-retail-function-map-2026-08-11.tsv",
         "blob", 1314885, "cdb26380bb6b29e82edd601bb95dfc215f62813d925e2f4c4c78452a7af7c68a",
         "d55a181088a3973dfdcc4700e4aa882c45d8aeaf"),
        ("tools/ExportFullFunctionInventory.java", "blob", 23963,
         STAMPS[INVENTORY][1], "07873c2c0c55892b7ebf57afd3bdc8d2020c5f00"),
        ("tools/ghidra_inventory_diff.py", "blob", 9622,
         STAMPS[DIFF][1], "42b394e75529a27bd8122123ec8b429715e68088"),
        ("tools/ghidra_project_backup.py", "blob", 27502,
         STAMPS[BACKUP][1], "9e965d7a1c62419428b61d94b4fb1fc0078da5bb"),
        ("tools/GhidraProjectOpenProbe.java", "blob", 3452,
         STAMPS[OPEN_PROBE][1], "ef59c6053bf9585d60c49dd78342529e82065189"),
        ("tools/DiagnoseAddressListingState.java", "blob", 3956,
         STAMPS[DIAGNOSTIC][1], "c6250ce79717afa0bab1bfc1e582f13487d6586d"),
    ]
    rows = value.get("loadBearingTrackedInputs")
    require(isinstance(rows, list) and len(rows) == len(expected_inputs),
            "e7aa load-bearing input count")
    for row, (path, kind, size, digest, oid) in zip(rows, expected_inputs, strict=True):
        portable(row.get("path"), "e7aa load-bearing path")
        expected = {"path": path, "kind": kind, "gitObjectAtBothCommits": oid}
        if kind == "blob":
            expected.update({"bytes": size, "sha256": digest})
            local = REPO / path
            verify_stamp(local, (size, digest), f"e7aa load-bearing {path}")
        require(row == expected, f"e7aa load-bearing identity at {path}")
    delta = value.get("nonLoadBearingTrackedChange", {})
    require(delta.get("path") == "reverse-engineering/delta.md"
            and delta.get("baseBytes") == 177520
            and delta.get("baseSha256") == "12732b77236d112a44cde5d7455b028d17ce58364557d87d320a34b861770ec5"
            and delta.get("targetBytes") == 177865
            and delta.get("targetSha256") == "ed5f8840f4ded656cbddd6a3cc925f9aff3acf9acfb44c78c2cc2640642535ea",
            "e7aa delta.md classification")
    transplant = value.get("transplant", {})
    require(transplant == {
        "head": COMPATIBLE_COMMIT, "candidateFilesByteIdentical": True,
        "mutatorTests": 5, "authorityTests": 6,
        "authorityCampaignSkippedBecauseIgnoredEvidenceNotCopied": 1,
        "diffCheckClean": True, "linksPresent": True,
        "commitStagePushPerformed": False, "liveOrCanonicalMutationPerformed": False,
    }, "e7aa transplant result")


def verify_campaign() -> dict[str, int]:
    manifest = verify_inputs()
    runs = LANE / "runs"
    for replica in ("a", "b"):
        for suffix, mode, stamps in (("dry", "dry", PRE_EXPORTS),
                                     ("apply", "apply", APPLY_EXPORTS),
                                     ("readback", "readback", READBACK_EXPORTS)):
            run = f"formal-replica-{replica}-{suffix}"
            for name, expected in stamps.items():
                verify_stamp(runs / run / name, expected, f"{run}/{name}")
            verify_ready(runs / run / "boundaries.ready.json", mode, run,
                         stamps["boundaries.tsv"])
    verify_function_state(manifest)
    verify_inventory_diff(runs / "formal-replica-a-readback/inventory-diff.json", "replica A")
    verify_inventory_diff(runs / "formal-replica-b-readback/inventory-diff.json", "replica B")

    for replica in ("a", "b"):
        require((runs / f"formal-replica-{replica}-apply/functions.tsv").read_bytes()
                == (runs / f"formal-replica-{replica}-readback/functions.tsv").read_bytes(),
                f"replica {replica} apply/readback functions")
        require((runs / f"formal-replica-{replica}-apply/program.tsv").read_bytes()
                == (runs / f"formal-replica-{replica}-readback/program.tsv").read_bytes(),
                f"replica {replica} apply/readback program")
    for name in ("functions.tsv", "program.tsv", "listing-state.tsv", "boundaries.tsv"):
        require((runs / f"formal-replica-a-readback/{name}").read_bytes()
                == (runs / f"formal-replica-b-readback/{name}").read_bytes(),
                f"replica readback differs: {name}")

    require(program_rows(runs / "formal-replica-a-dry/program.tsv") == PRE_PROGRAM,
            "PRE program collateral")
    require(program_rows(runs / "formal-replica-a-readback/program.tsv") == POST_PROGRAM,
            "POST program collateral")

    for probe, marker in (
        ("formal-probe-after-one", "CRT_P0_BOUNDARIES_FORCED_AFTER_ONE_FAILURE"),
        ("formal-probe-post-inner", "CRT_P0_BOUNDARIES_FORCED_POST_INNER_FAILURE"),
    ):
        text = (runs / probe / "console.log").read_text(encoding="utf-8", errors="replace")
        require(marker in text and "CRT_P0_BOUNDARIES_MUTATION_TAINTED" in text,
                f"{probe} failure markers")
        require(not (runs / probe / "boundaries.tsv").exists()
                and not (runs / probe / "boundaries.ready.json").exists(),
                f"{probe} published on failure")
        readback = runs / f"{probe}-readback"
        for name, expected in PRE_EXPORTS.items():
            verify_stamp(readback / name, expected, f"{probe} rollback/{name}")
        verify_ready(readback / "boundaries.ready.json", "dry", f"{probe}-readback",
                     PRE_EXPORTS["boundaries.tsv"])

    for control in ("external-output", "external-ready"):
        refusal = runs / f"formal-{control}-refusal"
        text = (refusal / "console.log").read_text(encoding="utf-8", errors="replace")
        require("receipts must stay inside this repository's local-lab tree" in text,
                f"{control} refusal marker")
        require(not (refusal / "boundaries.tsv").exists()
                and not (refusal / "boundaries.ready.json").exists(),
                f"{control} refusal published")
        readback = runs / f"formal-{control}-readback"
        for name in ("boundaries.tsv", "functions.tsv", "program.tsv"):
            verify_stamp(readback / name, PRE_EXPORTS[name], f"{control} readback/{name}")
    require(not (REPO.parent / "crt23-p0-external-output.tsv").exists()
            and not (REPO.parent / "crt23-p0-external-ready.json").exists(),
            "external containment artifact exists")
    verify_compatibility()
    verify_projects()
    return {
        "targets": TARGET_COUNT, "bodyRanges": BODY_RANGES, "bodyBytes": BODY_BYTES,
        "bodyInstructions": BODY_INSTRUCTIONS, "preFunctions": PRE_FUNCTIONS,
        "postFunctions": POST_FUNCTIONS, "preFunctionRanges": PRE_RANGES,
        "postFunctionRanges": POST_RANGES, "preservedPreFunctionRows": PRE_FUNCTIONS,
        "instructionDelta": POST_INSTRUCTIONS - PRE_INSTRUCTIONS,
        "referenceDelta": POST_REFERENCES - PRE_REFERENCES,
        "replicas": 2, "rollbackControls": 2, "containmentControls": 2,
        "readonlyRestoreProofs": 1, "current8280OverlapBytes": 0,
        "pairwiseOverlapBytes": 0,
    }


def artifact_tree() -> dict[str, Any]:
    rows = []
    for path in sorted((p for p in LANE.rglob("*") if p.is_file()
                        and p.resolve() != READY.resolve()), key=lambda p: p.as_posix()):
        relative = path.relative_to(LANE).as_posix()
        rows.append((sha256_file(path), path.stat().st_size, relative))
    encoded = b"".join(f"{digest}\t{size}\t{relative}\n".encode()
                        for digest, size, relative in rows)
    return {"fileCount": len(rows), "bytes": sum(row[1] for row in rows),
            "sha256": hashlib.sha256(encoded).hexdigest(),
            "excludes": "scratch-authority.ready.json"}


def build_payload(completed: str) -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA, "completedAtUtc": completed,
        "baseCommit": BASE_COMMIT, "derivationBaseCommit": DERIVATION_BASE_COMMIT,
        "verdict": "SCRATCH_READY_LIVE_FORBIDDEN",
        "liveMutationAuthorized": False, "trackedGhidraMutationAuthorized": False,
        "program": {"name": "BEA.exe", "md5": PROGRAM_MD5, "sha256": PROGRAM_SHA256},
        "sourceCohort": {"generation": "corrected-run-c", "bytes": 6949,
                         "sha256": SOURCE_COHORT_SHA256},
        "preProject": {"files": BASE_PROJECT[0], "bytes": BASE_PROJECT[1],
                       "canonicalInventorySha256": BASE_PROJECT[2]},
        "preDatabase": {"name": "db.18613.gbf", "bytes": DB_18613[0],
                        "sha256": DB_18613[1]},
        "manifest": stamp(MANIFEST),
        "tools": {"authority": stamp(SCRIPT), "mutator": stamp(MUTATOR),
                  "inventory": stamp(INVENTORY), "diff": stamp(DIFF),
                  "backup": stamp(BACKUP), "openProbe": stamp(OPEN_PROBE),
                  "diagnostic": stamp(DIAGNOSTIC)},
        "evidence": {
            "e7aaCompatibility": stamp(LANE / "e7aa-compatibility.json"),
            "runC": stamp(LANE / "inputs/run-c/result.ready.json"),
            "runCPromotionCohort": stamp(LANE / "inputs/run-c/promotion-cohort.tsv"),
            "preFunctions": stamp(LANE / "runs/formal-replica-a-dry/functions.tsv"),
            "postReplicaAFunctions": stamp(LANE / "runs/formal-replica-a-readback/functions.tsv"),
            "postReplicaBFunctions": stamp(LANE / "runs/formal-replica-b-readback/functions.tsv"),
            "postProgram": stamp(LANE / "runs/formal-replica-a-readback/program.tsv"),
            "recoverability": stamp(LANE / "base-restore-open.ready.json"),
        },
        "summary": verify_campaign(), "claims": list(CLAIMS),
        "artifactTree": artifact_tree(),
    }


def verify_payload(payload: Any) -> None:
    require(isinstance(payload, dict) and payload.get("schemaVersion") == SCHEMA,
            "authority schema")
    require(payload.get("baseCommit") == BASE_COMMIT
            and payload.get("derivationBaseCommit") == DERIVATION_BASE_COMMIT
            and payload.get("verdict") == "SCRATCH_READY_LIVE_FORBIDDEN"
            and payload.get("liveMutationAuthorized") is False
            and payload.get("trackedGhidraMutationAuthorized") is False,
            "authority boundary")
    datetime.fromisoformat(payload["completedAtUtc"].replace("Z", "+00:00"))
    expected = build_payload(payload["completedAtUtc"])
    require(payload == expected, "authority payload drift")
    for value in [payload["manifest"], *payload["tools"].values(), *payload["evidence"].values()]:
        portable(value["path"], "authority artifact path")


def write_new(path: Path, payload: dict[str, Any]) -> None:
    require(not path.exists(), f"authority receipt already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()
    handle, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".partial",
                                               dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(encoded)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def seal() -> None:
    completed = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    payload = build_payload(completed)
    write_new(READY, payload)
    verify_payload(read_json(READY))
    print(f"CRT_P0_SCRATCH_AUTHORITY_SEALED targets={TARGET_COUNT} functions={POST_FUNCTIONS}")


def verify() -> None:
    require(READY.is_file(), f"saved authority receipt missing: {READY}")
    verify_payload(read_json(READY))
    print(f"CRT_P0_SCRATCH_AUTHORITY_VERIFIED targets={TARGET_COUNT} functions={POST_FUNCTIONS}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("seal", "verify"))
    args = parser.parse_args()
    seal() if args.mode == "seal" else verify()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
