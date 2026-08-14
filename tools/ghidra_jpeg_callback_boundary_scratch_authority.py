#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Seal or reproduce the isolated 24-function IJG callback admission.

This owner is read-only except for create-new publication of its aggregate
receipt. It never launches Ghidra and never authorizes live or tracked-project
mutation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import stat
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).resolve()
LANE_REL = Path("local-lab/ghidra-jpeg24-boundary-current-scratch-20260814-v1")
LANE = REPO / LANE_REL
READY = LANE / "scratch-authority.ready.json"
SCHEMA = "bea.ghidra.jpeg-callback-boundary-scratch-authority.v1"
BASE_COMMIT = "d5e238cdc43f3dd03dba120c6236c9f33e791656"

MANIFEST = REPO / "reverse-engineering/binary-analysis/jpeg-ijg-callback-function-boundaries-2026-08-14.tsv"
MUTATOR = REPO / "tools/GhidraApplyJpegCallbackBoundaries.java"
INVENTORY = REPO / "tools/ExportFullFunctionInventory.java"
DIFF = REPO / "tools/ghidra_inventory_diff.py"
BACKUP = REPO / "tools/ghidra_project_backup.py"
OPEN_PROBE = REPO / "tools/GhidraProjectOpenProbe.java"
DIAGNOSTIC = REPO / "tools/DiagnoseAddressListingState.java"

PROGRAM_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
TARGET_COUNT = 24
BODY_BYTES = 14817
BODY_RANGES = 38
EXTERNAL_INSTRUCTIONS = 4497
CFG_EDGES = 4745
PRE_FUNCTIONS = 8280
POST_FUNCTIONS = 8304
PRE_INSTRUCTIONS = 550991
POST_INSTRUCTIONS = 551032
PRE_REFERENCES = 234495
POST_REFERENCES = 234484

STAMPS = {
    MANIFEST: (15295, "6253c29d77e6676f2843ca8adf3d9c52b4b4fa86f088f6086ea00b90dde89fd6"),
    MUTATOR: (61032, "16b8fbf6e4ffdab716b5359e8610c77b83bb6a32b6e2ac7d98e34efbe500c480"),
    INVENTORY: (23963, "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197"),
    DIFF: (9622, "b4956fbf9c9125cfdd7b7810cdc15f298fef8a081a880f82d6231a6dcbb25460"),
    BACKUP: (27502, "0f426982916f0aab982efe54664342a5d34607c2f89707159ecf6c07e205ad58"),
    OPEN_PROBE: (3452, "fab2f701dfefe8604c1718d007dbe0ad59d330a9b3ec081ef2f2fe253b441fab"),
    DIAGNOSTIC: (3956, "183394907659e7810c77a9720e1899fd8a6296e6e86673495d68a2764edefe69"),
}

FROZEN_STAMPS = {
    "analyze.py": (34715, "a746da869ebe22ad09299cd82e7a5dffd89b188ad001c96fd212a7397712bc73"),
    "current-8280-body-ranges.tsv": (1198388, "0101e6e8b34eaea8bd646a0fa9a8e4e448bef586c8b2b898c78241befde3aa6b"),
    "DiagnoseAddressListingState.java": STAMPS[DIAGNOSTIC],
    "diagnostic-addresses.txt": (88, "e0c3f01b6fcea1c9fe0de328c7850a7c29e9f7aae59cd4ef9549bf013c917aa9"),
    "ExportFullFunctionInventory.java": STAMPS[INVENTORY],
    "ghidra_inventory_diff.py": STAMPS[DIFF],
    "ghidra_project_backup.py": STAMPS[BACKUP],
    "GhidraApplyJpegCallbackBoundaries.java": STAMPS[MUTATOR],
    "GhidraProjectOpenProbe.java": STAMPS[OPEN_PROBE],
    "jpeg-ijg-callback-function-boundaries-2026-08-14.tsv": STAMPS[MANIFEST],
}

REPRO_OUTPUTS = {
    "cfg-edges.tsv": (344028, "75b4263ae6a8f69fd10655aa0542890e5c3426773826a887fb41b7d1b8a44d0d"),
    "functions.tsv": (15288, "af7633744f2dbb1868d0843fd2de4a97b7449ad7cb39e31c66a5e2063de1ef8b"),
    "gap-accounting.tsv": (1868, "81466fe9c725cdb504717644d848812e492367d98351fde8b91393bc8607b2c5"),
    "instructions.txt": (176569, "504302b5c62d9cf0c25d83f04bf7fe832193a10148336cdbc79ea0fc439aa8ab"),
    "remnant-classification.tsv": (841, "27a30877db91079dc81d04d3812fae11ebcfb4c8a7e8804d3561476dafbdbaa4"),
    "result.json": (9502, "6cc7f3a0030b90a4481592a00dfdd32ddbf34f97d8c68ccc923742399631f649"),
}

PRE_FUNCTIONS_STAMP = (7161942, "c3942b9e340cef71b731290b845843697af5c53204449c51949b779e896272d6")
PRE_PROGRAM_STAMP = (1267, "3e51ce1d5e926c632869b2058c9d89e91f48345a329a724ea9520570bd91212d")
POST_FUNCTIONS_STAMP = (7177775, "dce886c9ee9ddee96a2e27baff616723211b7818c2d9277e19e3202d6a307804")
POST_PROGRAM_STAMP = (1267, "b154869020140b266e06dd5ef07d4fd99c71e328a1ffb1223d4d4c6db4b3a5e9")
DRY_BOUNDARIES_STAMP = (9972, "5ba3201c0b852d485434701b768257e404c9fc963a3349f5f3855528662d3ac3")
APPLY_BOUNDARIES_STAMP = (12745, "2864f5c2085b395fcc8270f490c706cb245f299e58a6d3d62998fcc5c4ddfb7f")
READBACK_BOUNDARIES_STAMP = (12769, "956426b50f1997227828958e38399ba1106bbfdb36f4503c769338a387fffdfb")
PRE_LISTING_STAMP = (946, "aeddd26c2ebd4845436335263c5d620dbc8c1a242d9d96bcfb78a2ef8581ca98")
POST_LISTING_STAMP = (955, "55944e2cc03902c8f99d273aaa51ca98f1bfdedbe129bf18ad4441d21c6e0271")

BASE_PROJECT = (19, 186960773, "ae422079966978ec2f8f5b951b0ef5812b1074bd708ab8d782179f51c90efcf2")
DB_18613 = (68337664, "615497847b0c732077ee7164b0973b9012092523e9ad99b91c21781952420ebe")

PRE_PROGRAM = {
    "programName": "BEA.exe",
    "executableMD5": PROGRAM_MD5,
    "executableSHA256": PROGRAM_SHA256,
    "imageBase": "0x00400000",
    "language": "x86:LE:32:default",
    "compilerSpec": "windows",
    "memorySha256": "5398f750f1ffb59873a6ec7e1750b51d11b5b844a8fda8d4e43649b5b9e5089d",
    "functions": "8280",
    "instructions": "550991",
    "instructionLayoutSha256": "6e432dd36dd5964a95d982091188a24d1a3add46ade7b44a387bac205c475658",
    "definedData": "48585",
    "definedDataSha256": "3b87eb91228e20c1d627318cc2563811043c1500af1497575ab128e7edf6e9e3",
    "undefinedData": "3908482",
    "symbolsUserDefined": "6104",
    "symbolsAnalysis": "18006",
    "symbolsImported": "907",
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
    **PRE_PROGRAM,
    "functions": "8304",
    "instructions": "551032",
    "instructionLayoutSha256": "73d8910f39dddfcd731b51e4599fa4b087add43281e3e15e06e82e941d0794df",
    "undefinedData": "3908362",
    "symbolsDefaultOther": "61685",
    "references": "234484",
    "referencesSha256": "621f36bcdef31c608f8888acb59c7139102f51ac5cd8b4002402440d9ad19cf2",
}

CLAIMS = (
    "Two independent disposable replicas persist exactly the 24 manifest-bound IJG callback bodies and reproduce byte-identical full function, program, boundary, and correction-state readbacks.",
    "All 8,280 PRE function rows remain byte-identical; the only new rows are 24 default-metadata boundaries totaling 14,817 bytes and 4,497 Ghidra instructions.",
    "The 0x005B6800 correction replaces the false orphan instruction at 0x005B6900, which is read back only as the final byte of MOVZX at 0x005B68FE and is neither data nor a function entry.",
    "The seven-entry 0x005B4EB0 switch table and four-byte NOP alignment region are classified and preserved without data mutation.",
    "Forced failure after one target and after a complete validated batch both reopen to byte-identical PRE function and program inventories.",
    "Two external-path controls refuse publication, and a retained exact project copy opens read-only without changing its 19-file tree.",
    "Provider-qualified IJG identities, source anchors, and PC-demo normalized/CFG twins are evidence only; the Ghidra mutation applies no names, signatures, comments, tags, ABI, bytes, explicit references, or data definitions.",
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


def stamp(path: Path) -> dict[str, Any]:
    require(path.is_file(), f"missing file: {path}")
    relative = path.resolve().relative_to(REPO.resolve()).as_posix()
    return {"path": relative, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def verify_portable_path(value: Any, label: str) -> None:
    require(isinstance(value, str) and value and "\\" not in value
            and not value.startswith("/") and ":" not in value
            and ".." not in PurePosixPath(value).parts,
            f"{label} must be a repository-relative POSIX path")


def verify_stamp(path: Path, expected: tuple[int, str], label: str) -> None:
    require(path.is_file(), f"{label} missing")
    require((path.stat().st_size, sha256_file(path)) == expected, f"{label} stamp drift")


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def program_rows(path: Path) -> dict[str, str]:
    rows = read_tsv(path)
    result: dict[str, str] = {}
    for row in rows:
        key = row.get("metric")
        value = row.get("value")
        require(isinstance(key, str) and isinstance(value, str) and key not in result,
                f"invalid or duplicate program metric in {path}")
        result[key] = value
    return result


def parse_ranges(text: str) -> list[tuple[int, int]]:
    result = []
    for piece in text.split(";"):
        start, end = piece.split("-", 1)
        a, b = int(start, 16), int(end, 16)
        require(a < b, f"invalid half-open range: {piece}")
        result.append((a, b))
    return result


def canonical_ledger(files: Iterable[dict[str, Any]], label: str) -> tuple[int, int, str]:
    rows: list[tuple[str, int, str]] = []
    for row in files:
        relative = row.get("relative_path")
        size = row.get("size")
        digest = row.get("sha256")
        require(isinstance(relative, str) and relative and "\\" not in relative
                and not relative.startswith("/") and ":" not in relative,
                f"{label} relative path")
        require(isinstance(size, int) and size >= 0, f"{label} size")
        require(isinstance(digest, str) and len(digest) == 64, f"{label} hash")
        rows.append((digest, size, relative))
    rows.sort(key=lambda item: item[2])
    require(len({row[2] for row in rows}) == len(rows), f"{label} duplicate path")
    canonical = b"".join(
        f"{digest}\t{size}\t{relative}\n".encode("utf-8")
        for digest, size, relative in rows
    )
    return len(rows), sum(row[1] for row in rows), hashlib.sha256(canonical).hexdigest()


def actual_project(project_root: Path, label: str) -> tuple[int, int, str]:
    roots = [project_root / "BEA.gpr", project_root / "BEA.rep"]
    require(roots[0].is_file() and roots[1].is_dir(), f"{label} project pair")
    paths = [roots[0], *(path for path in roots[1].rglob("*") if path.is_file())]
    files = [
        {
            "relative_path": path.relative_to(project_root).as_posix(),
            "size": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in paths
    ]
    actual = canonical_ledger(files, label)
    require(actual == BASE_PROJECT, f"{label} project tree drift: {actual}")
    return actual


def verify_copy_receipt(path: Path, label: str) -> None:
    value = read_json(path)
    require(value.get("schemaVersion") == "onslaught-ghidra-project-backup.v2",
            f"{label} schema")
    comparison = value.get("copyComparison")
    require(isinstance(comparison, dict) and comparison.get("matches") is True,
            f"{label} comparison")
    for key in ("missingCount", "extraCount", "sizeDiffCount", "hashDiffCount"):
        require(comparison.get(key) == 0, f"{label} {key}")
    for side in ("source", "destination"):
        ledger = value.get(side)
        require(isinstance(ledger, dict), f"{label} {side}")
        require(canonical_ledger(ledger.get("files", []), f"{label} {side}") == BASE_PROJECT,
                f"{label} {side} inventory")


def verify_reproof() -> list[dict[str, str]]:
    inputs = LANE / "inputs"
    for name, expected in FROZEN_STAMPS.items():
        verify_stamp(inputs / name, expected, f"frozen input {name}")
    require((inputs / "GhidraApplyJpegCallbackBoundaries.java").read_bytes()
            == MUTATOR.read_bytes(), "tracked/frozen mutator differs")
    require((inputs / "jpeg-ijg-callback-function-boundaries-2026-08-14.tsv").read_bytes()
            == MANIFEST.read_bytes(), "tracked/frozen manifest differs")
    for run in ("reproof-a", "reproof-b"):
        for name, expected in REPRO_OUTPUTS.items():
            verify_stamp(inputs / run / name, expected, f"{run}/{name}")
    for name in REPRO_OUTPUTS:
        require((inputs / "reproof-a" / name).read_bytes()
                == (inputs / "reproof-b" / name).read_bytes(),
                f"reproof output differs: {name}")

    result = read_json(inputs / "reproof-a/result.json")
    expected_result = {
        "requestedFunctions": 23,
        "requestedRetailBodyBytes": 14171,
        "requestedRetailInstructions": 4294,
        "requestedDemoNormalizedTwins": 23,
        "allCandidateFunctions": 24,
        "discoveredAdditionalFunctions": 1,
        "retailBodyBytes": BODY_BYTES,
        "retailInstructions": EXTERNAL_INSTRUCTIONS,
        "pairwiseOverlapBytes": 0,
        "saved8201BodyOverlapBytes": 0,
        "demoNormalizedTwins": 24,
        "demoRawTwins": 14,
        "gapCount": 8,
        "gapBytes": 15227,
        "gapFunctionBodyBytes": BODY_BYTES,
        "gapUnownedBytes": 410,
    }
    for key, expected in expected_result.items():
        require(result.get(key) == expected, f"reproof result {key}")
    require(result.get("remnantClassifications") == {
        "0x005B4EB0": "SWITCH_JUMP_TABLE_DATA",
        "0x005B4ECC": "NOP_ALIGNMENT_PADDING",
        "0x005B6800": "CALLABLE_BODY_NOT_DATA__LIBJPEG6B_h2v2_smooth_downsample",
        "0x005B6900": "FALSE_TEXT_ADDRESS_COINCIDENCE__FIXED_POINT_INTEGER",
    }, "reproof remnant classifications")

    evidence_rows = read_tsv(inputs / "reproof-a/functions.tsv")
    manifest_rows = read_tsv(MANIFEST)
    require(len(evidence_rows) == len(manifest_rows) == TARGET_COUNT, "manifest/reproof rows")
    for evidence, manifest in zip(evidence_rows, manifest_rows, strict=True):
        for key, value in evidence.items():
            mapped = "current_8280_body_overlap_bytes" if key == "saved_body_overlap_bytes" else key
            require(manifest.get(mapped) == value, f"manifest/reproof drift at {manifest.get('retail_va')} {mapped}")
        require(manifest["normalized_equal"] == "true"
                and manifest["identity_grade"] == "EXACT_IJG_V6B_SOURCE_ALGORITHM",
                f"manifest evidence grade at {manifest['retail_va']}")

    owner_rows = read_tsv_ignoring_comments(inputs / "current-8280-body-ranges.tsv")
    owner_ranges = [
        (int(row["rangeMin"], 16), int(row["rangeEndExclusive"], 16))
        for row in owner_rows
    ]
    target_ranges: list[tuple[int, int]] = []
    for row in manifest_rows:
        for start, end in parse_ranges(row["body_ranges"]):
            require(not any(max(start, a) < min(end, b) for a, b in owner_ranges),
                    f"current 8,280 overlap at {row['retail_va']}")
            require(not any(max(start, a) < min(end, b) for a, b in target_ranges),
                    f"pairwise target overlap at {row['retail_va']}")
            target_ranges.append((start, end))
    require(len(target_ranges) == BODY_RANGES, "target range count")
    require(sum(end - start for start, end in target_ranges) == BODY_BYTES,
            "target body byte union")
    correction = next(row for row in manifest_rows if row["retail_va"] == "0x005B6800")
    require(correction["cohort"] == "DISCOVERED_CORRECTION"
            and correction["body_ranges"] == "0x005B6800-0x005B6A86"
            and correction["body_sha256"] == "dafa1afd702c5a85511d2d1185658f58d56e1b0755d98228edeb48a0ee5d21b8",
            "corrected callback row")
    require(all(row["retail_va"] != "0x005B6900" for row in manifest_rows),
            "0x005B6900 appears as a target")
    return manifest_rows


def read_tsv_ignoring_comments(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader((line for line in stream if not line.startswith("#")), delimiter="\t"))


def verify_ready(path: Path, mode: str, run_rel: str, output_stamp: tuple[int, str]) -> None:
    value = read_json(path)
    require(value.get("schemaVersion") == "bea.ghidra.jpeg-callback-boundaries.v1",
            f"{run_rel} ready schema")
    require(value.get("mode") == mode, f"{run_rel} ready mode")
    require(value.get("program") == {"name": "BEA.exe", "md5": PROGRAM_MD5,
                                     "sha256": PROGRAM_SHA256},
            f"{run_rel} ready program")
    require(value.get("explicitBodySetsAuthorized") is True
            and value.get("postCountsPinned") is True
            and value.get("namesAuthorized") is False
            and value.get("metadataAuthorized") is False,
            f"{run_rel} authority flags")
    require(value.get("fixedPointAddressIsFunctionEntry") is False
            and value.get("fixedPointAddressIsData") is False
            and value.get("fixedPointInstructionOwner") == "0x005b68fe",
            f"{run_rel} correction flags")
    expected_counts = {
        "dry": (PRE_FUNCTIONS, PRE_FUNCTIONS, PRE_INSTRUCTIONS, PRE_INSTRUCTIONS),
        "apply": (PRE_FUNCTIONS, POST_FUNCTIONS, PRE_INSTRUCTIONS, POST_INSTRUCTIONS),
        "readback": (POST_FUNCTIONS, POST_FUNCTIONS, POST_INSTRUCTIONS, POST_INSTRUCTIONS),
    }[mode]
    counts = value.get("counts")
    require(isinstance(counts, dict), f"{run_rel} counts")
    require((counts.get("targets"), counts.get("externalInstructions"),
             counts.get("ghidraBodyInstructions")) ==
            (TARGET_COUNT, EXTERNAL_INSTRUCTIONS, EXTERNAL_INSTRUCTIONS),
            f"{run_rel} target counts")
    require(tuple(counts.get(key) for key in (
        "functionsBefore", "functionsAfter", "instructionsBefore", "instructionsAfter"
    )) == expected_counts, f"{run_rel} PRE/POST counts")
    require(value.get("separateReadbackRequired") is (mode != "readback"),
            f"{run_rel} separate readback flag")
    require(value.get("tool") == {
        "path": (LANE_REL / "inputs/GhidraApplyJpegCallbackBoundaries.java").as_posix(),
        "bytes": STAMPS[MUTATOR][0], "sha256": STAMPS[MUTATOR][1],
    }, f"{run_rel} tool stamp")
    require(value.get("manifest") == {
        "path": MANIFEST.relative_to(REPO).as_posix(),
        "bytes": STAMPS[MANIFEST][0], "sha256": STAMPS[MANIFEST][1],
    }, f"{run_rel} manifest stamp")
    require(value.get("output") == {
        "path": (LANE_REL / "runs" / run_rel / "boundaries.tsv").as_posix(),
        "bytes": output_stamp[0], "sha256": output_stamp[1],
    }, f"{run_rel} output stamp")
    completed = value.get("completedAtUtc")
    require(isinstance(completed, str), f"{run_rel} completion time")
    datetime.fromisoformat(completed.replace("Z", "+00:00"))


def verify_boundaries(path: Path, mode: str, manifest_rows: list[dict[str, str]]) -> None:
    rows = read_tsv(path)
    require(len(rows) == TARGET_COUNT, f"{path} row count")
    expected_status = {"dry": "ready_absent", "apply": "created", "readback": "verified"}[mode]
    for index, (row, source) in enumerate(zip(rows, manifest_rows, strict=True), 1):
        entry = source["retail_va"].lower()
        require(row["candidateId"] == f"JPEG-{index:03d}" and row["entry"] == entry,
                f"boundary identity at {entry}")
        require(row["status"] == expected_status, f"boundary status at {entry}")
        require(row["cohort"] == source["cohort"]
                and row["providerIdentity"] == source["provider_identity"]
                and row["identityGrade"] == source["identity_grade"],
                f"boundary evidence at {entry}")
        require(row["expectedRanges"] == source["body_ranges"].lower()
                and row["expectedBodyBytes"] == source["body_bytes"]
                and row["expectedBodySha256"] == source["body_sha256"]
                and row["externalInstructionCount"] == source["instruction_count"],
                f"boundary envelope at {entry}")
        if mode == "dry":
            require(row["name"] == row["nameSource"] == row["actualRanges"] == ""
                    and row["actualBodyBytes"] == "0"
                    and row["actualBodySha256"] == ""
                    and row["actualGhidraInstructionCount"] == "0",
                    f"dry boundary state at {entry}")
        else:
            require(row["name"] == f"FUN_{entry[2:]}" and row["nameSource"] == "DEFAULT"
                    and row["actualRanges"] == row["expectedRanges"]
                    and row["actualBodyBytes"] == row["expectedBodyBytes"]
                    and row["actualBodySha256"] == row["expectedBodySha256"]
                    and row["actualGhidraInstructionCount"] == row["externalInstructionCount"],
                    f"present boundary state at {entry}")


def verify_diff(path: Path, created: int) -> None:
    value = read_json(path)
    counts = value.get("counts")
    require(isinstance(counts, dict), f"{path} diff counts")
    expected = {
        "before": PRE_FUNCTIONS,
        "after": PRE_FUNCTIONS + created,
        "created": created,
        "destroyed": 0,
        "boundsChanged": 0,
        "callingConvChanged": 0,
        "instrCountChanged": 0,
        "namesChanged": 0,
        "noReturnChanged": 0,
        "paramCountChanged": 0,
        "returnTypeChanged": 0,
        "sigSourceChanged": 0,
        "signaturesChanged": 0,
        "thunkFlagChanged": 0,
    }
    require(counts == expected, f"{path} diff changes")
    dangerous = value.get("dangerous")
    require(isinstance(dangerous, dict)
            and all(dangerous.get(key) == 0 for key in (
                "gradedBoundsMovedCount", "gradedDemotedCount",
                "gradedDestroyedCount", "gradedRenamedCount")),
            f"{path} dangerous diff")


def verify_listing(path: Path, post: bool) -> None:
    rows = {row["input"].lower(): row for row in read_tsv(path)}
    require(set(rows) == {"0x005b4eb0", "0x005b4ecc", "0x005b4ed0", "0x005b6800",
                          "0x005b68fe", "0x005b6900", "0x005b6a86", "0x005b6a90"},
            f"{path} diagnostic targets")
    require(rows["0x005b4eb0"]["status"] == "DEFINED_DATA"
            and rows["0x005b4ecc"]["status"] == "UNDEFINED",
            f"{path} table classification")
    fixed = rows["0x005b6900"]
    require(fixed["data_at"] == fixed["data_containing"] == "<none>"
            and fixed["function_at"] == "<none>",
            f"{path} fixed-point data/function entry")
    if post:
        require(fixed["instruction_at"] == "<none>"
                and fixed["instruction_containing"].startswith("MOVZX EAX,byte ptr [EAX]")
                and fixed["function_containing"] == "FUN_005b6800",
                f"{path} corrected fixed-point ownership")
        require(rows["0x005b68fe"]["instruction_at"].startswith("MOVZX EAX,byte ptr [EAX]")
                and rows["0x005b6800"]["function_at"] == "FUN_005b6800",
                f"{path} corrected callback state")
    else:
        require(fixed["instruction_at"].startswith("ADD byte ptr")
                and fixed["function_containing"] == "<none>"
                and rows["0x005b68fe"]["status"] == "UNDEFINED",
                f"{path} pinned PRE misdecode")


def verify_function_preservation(manifest_rows: list[dict[str, str]]) -> None:
    before_path = LANE / "runs/base-inventory/functions.tsv"
    after_path = LANE / "runs/formal-replica-a-readback/functions.tsv"
    verify_stamp(before_path, PRE_FUNCTIONS_STAMP, "PRE functions")
    verify_stamp(after_path, POST_FUNCTIONS_STAMP, "POST functions")
    before = read_tsv(before_path)
    after = read_tsv(after_path)
    require(len(before) == PRE_FUNCTIONS and len(after) == POST_FUNCTIONS,
            "full function inventory counts")
    before_map = {row["address"]: row for row in before}
    after_map = {row["address"]: row for row in after}
    require(len(before_map) == len(before) and len(after_map) == len(after),
            "duplicate function address")
    for address, row in before_map.items():
        require(after_map.get(address) == row, f"PRE function row changed at {address}")
    created = set(after_map) - set(before_map)
    expected = {row["retail_va"].lower() for row in manifest_rows}
    require(created == expected, "created function set")
    source_by_entry = {row["retail_va"].lower(): row for row in manifest_rows}
    for address in sorted(created):
        row, source = after_map[address], source_by_entry[address]
        require(row["name"] == f"FUN_{address[2:]}"
                and row["nameSource"] == row["sigSource"] == "DEFAULT"
                and row["bodyBytes"] == source["body_bytes"]
                and row["bodyRanges"] == source["body_range_count"]
                and row["instrCount"] == source["instruction_count"]
                and row["paramCount"] == "0"
                and row["isThunk"] == row["noReturn"] == "false"
                and row["commentPresent"] == row["repeatableCommentPresent"] == "false"
                and row["tagCount"] == "0",
                f"created default metadata at {address}")


def verify_positive(run: str, manifest_rows: list[dict[str, str]]) -> None:
    dry_rel = f"formal-{run}-dry"
    apply_rel = f"formal-{run}-apply"
    read_rel = f"formal-{run}-readback"
    for rel, mode, expected in (
        (dry_rel, "dry", DRY_BOUNDARIES_STAMP),
        (apply_rel, "apply", APPLY_BOUNDARIES_STAMP),
        (read_rel, "readback", READBACK_BOUNDARIES_STAMP),
    ):
        directory = LANE / "runs" / rel
        verify_stamp(directory / "boundaries.tsv", expected, f"{rel} boundaries")
        verify_boundaries(directory / "boundaries.tsv", mode, manifest_rows)
        verify_ready(directory / "boundaries.ready.json", mode, rel, expected)
        log = (directory / "ghidra.log").read_text(encoding="utf-8", errors="replace")
        require(f"JPEG_CALLBACK_BOUNDARIES_OK mode={mode}" in log
                and "REPORT SCRIPT ERROR" not in log,
                f"{rel} log")
        if mode == "apply":
            require("Save succeeded for processed file: /BEA.exe" in log,
                    f"{rel} save")
    read = LANE / "runs" / read_rel
    verify_stamp(read / "functions.tsv", POST_FUNCTIONS_STAMP, f"{run} functions")
    verify_stamp(read / "program.tsv", POST_PROGRAM_STAMP, f"{run} program")
    verify_stamp(read / "listing-state.tsv", POST_LISTING_STAMP, f"{run} listing")
    require(program_rows(read / "program.tsv") == POST_PROGRAM, f"{run} program rows")
    verify_listing(read / "listing-state.tsv", True)
    verify_diff(read / "inventory-diff.json", TARGET_COUNT)


def verify_rollback(name: str, markers: tuple[str, ...]) -> None:
    probe = LANE / "runs" / f"formal-{name}"
    log = (probe / "ghidra.log").read_text(encoding="utf-8", errors="replace")
    require(all(marker in log for marker in markers)
            and "JPEG_CALLBACK_BOUNDARIES_OK" not in log
            and "REPORT SCRIPT ERROR" in log
            and "Save succeeded for processed file: /BEA.exe" in log,
            f"{name} probe log")
    require(not (probe / "boundaries.tsv").exists()
            and not (probe / "boundaries.ready.json").exists(),
            f"{name} unexpectedly published receipts")
    read_rel = f"formal-{name}-readback"
    read = LANE / "runs" / read_rel
    verify_stamp(read / "boundaries.tsv", DRY_BOUNDARIES_STAMP, f"{name} dry boundaries")
    verify_boundaries(read / "boundaries.tsv", "dry", read_tsv(MANIFEST))
    verify_ready(read / "boundaries.ready.json", "dry", read_rel, DRY_BOUNDARIES_STAMP)
    verify_stamp(read / "functions.tsv", PRE_FUNCTIONS_STAMP, f"{name} functions")
    verify_stamp(read / "program.tsv", PRE_PROGRAM_STAMP, f"{name} program")
    verify_stamp(read / "listing-state.tsv", PRE_LISTING_STAMP, f"{name} listing")
    require(program_rows(read / "program.tsv") == PRE_PROGRAM, f"{name} program rows")
    verify_listing(read / "listing-state.tsv", False)
    verify_diff(read / "inventory-diff.json", 0)


def verify_preflights() -> None:
    for suffix in ("external-output", "external-ready"):
        directory = LANE / "runs" / f"formal-preflight-{suffix}"
        log = (directory / "ghidra.log").read_text(encoding="utf-8", errors="replace")
        require("receipts must stay inside this repository's local-lab tree" in log
                and "REPORT SCRIPT ERROR" in log
                and "JPEG_CALLBACK_BOUNDARIES_OK" not in log,
                f"external {suffix} preflight")
        require(not (directory / "boundaries.tsv").exists()
                and not (directory / "boundaries.ready.json").exists(),
                f"external {suffix} publication")


def verify_recoverability() -> None:
    actual_project(LANE / "projects/base", "base")
    db = LANE / "projects/base/BEA.rep/idata/00/~00000000.db/db.18613.gbf"
    verify_stamp(db, DB_18613, "base db.18613")
    for name in ("base", "replica-a", "replica-b", "probe-after-one", "probe-post-inner"):
        verify_copy_receipt(LANE / "projects" / name / "backup_manifest.json",
                            f"{name} initial copy")
    receipt_path = LANE / "base-restore.ready.json"
    receipt = read_json(receipt_path)
    require(receipt.get("schemaVersion") == "onslaught-ghidra-project-backup.v2"
            and receipt.get("sourceStable") is True
            and receipt.get("probeCopyDisposition") == "RETAINED_AT_VERIFICATION",
            "restore receipt")
    comparison = receipt.get("copyComparison")
    require(isinstance(comparison, dict) and comparison.get("matches") is True
            and all(comparison.get(key) == 0 for key in (
                "missingCount", "extraCount", "sizeDiffCount", "hashDiffCount")),
            "restore copy comparison")
    source = receipt.get("source")
    require(isinstance(source, dict)
            and canonical_ledger(source.get("files", []), "restore source") == BASE_PROJECT,
            "restore source inventory")
    opened = receipt.get("readonlyOpen")
    require(isinstance(opened, dict) and opened.get("opened") is True
            and opened.get("contentStable") is True and opened.get("exitCode") == 0
            and opened.get("observedFunctionCount") == 8504
            and opened.get("observedProgramMd5") == PROGRAM_MD5
            and opened.get("observedProgramSha256") == PROGRAM_SHA256,
            "read-only restore open")
    argv = opened.get("commandArgv")
    require(isinstance(argv, list) and "-readOnly" in argv and "-noanalysis" in argv
            and "-commit" not in argv and "GhidraProjectOpenProbe.java" in argv,
            "read-only restore command")
    probe_log = LANE / "base-restore.ready.open-probe.log"
    expected_log = opened.get("probeLog")
    require(isinstance(expected_log, dict)
            and (expected_log.get("bytes"), expected_log.get("sha256")) ==
                (probe_log.stat().st_size, sha256_file(probe_log)),
            "restore probe log stamp")
    text = probe_log.read_text(encoding="utf-8", errors="replace")
    require(text.count("GHIDRA_PROJECT_OPEN_PROBE_OK") == 1
            and "REPORT SCRIPT ERROR" not in text,
            "restore probe log markers")
    restored = [path for path in (LANE / "restore-probe").iterdir() if path.is_dir()]
    require(len(restored) == 1, "retained restore count")
    actual_project(restored[0], "retained restore")


def verify_campaign() -> dict[str, Any]:
    for path, expected in STAMPS.items():
        verify_stamp(path, expected, path.name)
    manifest_rows = verify_reproof()
    verify_recoverability()
    verify_stamp(LANE / "runs/base-inventory/functions.tsv", PRE_FUNCTIONS_STAMP,
                 "base full functions")
    verify_stamp(LANE / "runs/base-inventory/program.tsv", PRE_PROGRAM_STAMP,
                 "base program")
    require(program_rows(LANE / "runs/base-inventory/program.tsv") == PRE_PROGRAM,
            "base program rows")
    verify_preflights()
    verify_positive("replica-a", manifest_rows)
    verify_positive("replica-b", manifest_rows)
    for name in ("boundaries.tsv", "functions.tsv", "program.tsv", "listing-state.tsv"):
        require((LANE / "runs/formal-replica-a-readback" / name).read_bytes()
                == (LANE / "runs/formal-replica-b-readback" / name).read_bytes(),
                f"positive replica output differs: {name}")
    verify_function_preservation(manifest_rows)
    verify_rollback("probe-after-one", (
        "JPEG_CALLBACK_BOUNDARIES_FORCED_AFTER_ONE_FAILURE",
        "JPEG_CALLBACK_BOUNDARIES_MUTATION_TAINTED mode=probe-after-one",
    ))
    verify_rollback("probe-post-inner", (
        "JPEG_CALLBACK_BOUNDARIES_POST_INNER_ROLLBACK_REQUESTED",
        "JPEG_CALLBACK_BOUNDARIES_FORCED_POST_INNER_FAILURE",
        "JPEG_CALLBACK_BOUNDARIES_MUTATION_TAINTED mode=probe-post-inner",
    ))
    return {
        "targets": TARGET_COUNT,
        "bodyBytes": BODY_BYTES,
        "bodyRanges": BODY_RANGES,
        "externalInstructions": EXTERNAL_INSTRUCTIONS,
        "ghidraBodyInstructions": EXTERNAL_INSTRUCTIONS,
        "cfgEdges": CFG_EDGES,
        "demoNormalizedTwins": TARGET_COUNT,
        "demoRawTwins": 14,
        "preFunctions": PRE_FUNCTIONS,
        "postFunctions": POST_FUNCTIONS,
        "preservedPreFunctionRows": PRE_FUNCTIONS,
        "instructionDelta": POST_INSTRUCTIONS - PRE_INSTRUCTIONS,
        "referenceDelta": POST_REFERENCES - PRE_REFERENCES,
        "replicas": 2,
        "adverseControls": 2,
        "externalPathPreflights": 2,
        "readonlyRestoreProofs": 1,
        "current8280OverlapBytes": 0,
        "pairwiseOverlapBytes": 0,
    }


def is_reparse(path: Path) -> bool:
    try:
        return bool(path.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT)
    except AttributeError:
        return path.is_symlink()


def artifact_tree() -> dict[str, Any]:
    require(LANE.is_dir(), "saved lane missing")
    rows: list[tuple[str, int, str]] = []
    total = 0
    for path in sorted(LANE.rglob("*"), key=lambda item: item.relative_to(LANE).as_posix()):
        if path == READY:
            continue
        require(not is_reparse(path), f"artifact tree contains reparse point: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(LANE).as_posix()
        size = path.stat().st_size
        rows.append((sha256_file(path), size, relative))
        total += size
    canonical = b"".join(
        f"{digest}\t{size}\t{relative}\n".encode("utf-8")
        for digest, size, relative in rows
    )
    return {"fileCount": len(rows), "totalBytes": total,
            "sha256": hashlib.sha256(canonical).hexdigest()}


def build_payload(completed_at: str) -> dict[str, Any]:
    summary = verify_campaign()
    return {
        "schemaVersion": SCHEMA,
        "completedAtUtc": completed_at,
        "baseCommit": BASE_COMMIT,
        "verdict": "SCRATCH_READY_LIVE_FORBIDDEN",
        "liveMutationAuthorized": False,
        "trackedGhidraMutationAuthorized": False,
        "program": {"name": "BEA.exe", "md5": PROGRAM_MD5, "sha256": PROGRAM_SHA256},
        "preProject": {"files": BASE_PROJECT[0], "bytes": BASE_PROJECT[1],
                       "canonicalInventorySha256": BASE_PROJECT[2]},
        "preDatabase": {"name": "db.18613.gbf", "bytes": DB_18613[0],
                        "sha256": DB_18613[1]},
        "summary": summary,
        "correction": {
            "functionEntry": "0x005B6800",
            "functionEndExclusive": "0x005B6A86",
            "bodyBytes": 646,
            "bodySha256": "dafa1afd702c5a85511d2d1185658f58d56e1b0755d98228edeb48a0ee5d21b8",
            "fixedPointAddress": "0x005B6900",
            "fixedPointIsFunctionEntry": False,
            "fixedPointIsData": False,
            "containingInstruction": "0x005B68FE-0x005B6901",
            "containingInstructionBytes": "0fb600",
        },
        "manifest": stamp(MANIFEST),
        "tools": {
            "authority": stamp(SCRIPT),
            "mutator": stamp(MUTATOR),
            "inventory": stamp(INVENTORY),
            "diff": stamp(DIFF),
            "backup": stamp(BACKUP),
            "openProbe": stamp(OPEN_PROBE),
            "diagnostic": stamp(DIAGNOSTIC),
        },
        "evidence": {
            "preFunctions": stamp(LANE / "runs/base-inventory/functions.tsv"),
            "preProgram": stamp(LANE / "runs/base-inventory/program.tsv"),
            "replicaAFunctions": stamp(LANE / "runs/formal-replica-a-readback/functions.tsv"),
            "replicaAProgram": stamp(LANE / "runs/formal-replica-a-readback/program.tsv"),
            "replicaBFunctions": stamp(LANE / "runs/formal-replica-b-readback/functions.tsv"),
            "replicaBProgram": stamp(LANE / "runs/formal-replica-b-readback/program.tsv"),
            "recoverability": stamp(LANE / "base-restore.ready.json"),
            "recoverabilityProbeLog": stamp(LANE / "base-restore.ready.open-probe.log"),
            "reproofResult": stamp(LANE / "inputs/reproof-a/result.json"),
        },
        "claims": list(CLAIMS),
        "artifactTree": artifact_tree(),
    }


def write_new(path: Path, payload: dict[str, Any]) -> None:
    require(not path.exists(), f"authority receipt already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
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


def verify_payload(payload: Any) -> None:
    require(isinstance(payload, dict) and payload.get("schemaVersion") == SCHEMA,
            "authority schema")
    require(set(payload) == {
        "artifactTree", "baseCommit", "claims", "completedAtUtc", "correction",
        "evidence", "liveMutationAuthorized", "manifest", "preDatabase",
        "preProject", "program", "schemaVersion", "summary", "tools",
        "trackedGhidraMutationAuthorized", "verdict",
    }, "authority envelope fields")
    require(payload.get("baseCommit") == BASE_COMMIT
            and payload.get("verdict") == "SCRATCH_READY_LIVE_FORBIDDEN"
            and payload.get("liveMutationAuthorized") is False
            and payload.get("trackedGhidraMutationAuthorized") is False,
            "authority boundary")
    completed = payload.get("completedAtUtc")
    require(isinstance(completed, str), "authority completion time")
    datetime.fromisoformat(completed.replace("Z", "+00:00"))
    require(payload.get("program") == {
        "name": "BEA.exe", "md5": PROGRAM_MD5, "sha256": PROGRAM_SHA256,
    }, "authority program")
    require(payload.get("preProject") == {
        "files": BASE_PROJECT[0], "bytes": BASE_PROJECT[1],
        "canonicalInventorySha256": BASE_PROJECT[2],
    }, "authority PRE project")
    require(payload.get("preDatabase") == {
        "name": "db.18613.gbf", "bytes": DB_18613[0], "sha256": DB_18613[1],
    }, "authority PRE database")
    require(payload.get("correction") == {
        "functionEntry": "0x005B6800",
        "functionEndExclusive": "0x005B6A86",
        "bodyBytes": 646,
        "bodySha256": "dafa1afd702c5a85511d2d1185658f58d56e1b0755d98228edeb48a0ee5d21b8",
        "fixedPointAddress": "0x005B6900",
        "fixedPointIsFunctionEntry": False,
        "fixedPointIsData": False,
        "containingInstruction": "0x005B68FE-0x005B6901",
        "containingInstructionBytes": "0fb600",
    }, "authority correction")
    require(payload.get("summary") == verify_campaign(), "authority summary drift")
    require(payload.get("artifactTree") == artifact_tree(), "artifact tree drift")
    expected_manifest = stamp(MANIFEST)
    require(payload.get("manifest") == expected_manifest, "authority manifest drift")
    verify_portable_path(expected_manifest["path"], "authority manifest path")
    tools = payload.get("tools")
    expected_tools = {
        "authority": stamp(SCRIPT),
        "mutator": stamp(MUTATOR),
        "inventory": stamp(INVENTORY),
        "diff": stamp(DIFF),
        "backup": stamp(BACKUP),
        "openProbe": stamp(OPEN_PROBE),
        "diagnostic": stamp(DIAGNOSTIC),
    }
    require(tools == expected_tools, "authority tool drift")
    for name, value in expected_tools.items():
        verify_portable_path(value["path"], f"authority {name} tool path")
    expected_evidence = {
        "preFunctions": stamp(LANE / "runs/base-inventory/functions.tsv"),
        "preProgram": stamp(LANE / "runs/base-inventory/program.tsv"),
        "replicaAFunctions": stamp(LANE / "runs/formal-replica-a-readback/functions.tsv"),
        "replicaAProgram": stamp(LANE / "runs/formal-replica-a-readback/program.tsv"),
        "replicaBFunctions": stamp(LANE / "runs/formal-replica-b-readback/functions.tsv"),
        "replicaBProgram": stamp(LANE / "runs/formal-replica-b-readback/program.tsv"),
        "recoverability": stamp(LANE / "base-restore.ready.json"),
        "recoverabilityProbeLog": stamp(LANE / "base-restore.ready.open-probe.log"),
        "reproofResult": stamp(LANE / "inputs/reproof-a/result.json"),
    }
    require(payload.get("evidence") == expected_evidence, "authority evidence drift")
    for name, value in expected_evidence.items():
        verify_portable_path(value["path"], f"authority {name} evidence path")
    require(tuple(payload.get("claims", [])) == CLAIMS, "authority claims drift")


def seal() -> None:
    completed = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    payload = build_payload(completed)
    write_new(READY, payload)
    verify_payload(read_json(READY))
    print(f"JPEG_CALLBACK_SCRATCH_AUTHORITY_SEALED targets={TARGET_COUNT} functions={POST_FUNCTIONS}")


def verify() -> None:
    require(READY.is_file(), f"saved authority receipt missing: {READY}")
    verify_payload(read_json(READY))
    print(f"JPEG_CALLBACK_SCRATCH_AUTHORITY_VERIFIED targets={TARGET_COUNT} functions={POST_FUNCTIONS}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("seal", "verify"))
    args = parser.parse_args()
    if args.mode == "seal":
        seal()
    else:
        verify()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
