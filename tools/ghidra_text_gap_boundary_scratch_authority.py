#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Seal or reproduce the isolated 31-row text-gap scratch admission.

This owner is read-only except for create-new publication of the authority
receipt.  It never opens Ghidra and never authorizes a live or tracked-project
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
from pathlib import Path
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).resolve()
LANE = REPO / "local-lab/ghidra-text-gap-boundary-scratch-20260813-v3"
READY = LANE / "scratch-authority.ready.json"
SCHEMA = "bea.ghidra.text-gap-boundary-scratch-authority.v2"

MANIFEST = (
    REPO
    / "reverse-engineering/binary-analysis/"
    "text-gap-missing-function-boundaries-2026-08-13.tsv"
)
MUTATOR = REPO / "tools/GhidraApplyTextGapBoundaries.java"
INVENTORY = REPO / "tools/ExportFullFunctionInventory.java"
DIFF = REPO / "tools/ghidra_inventory_diff.py"
BACKUP = REPO / "tools/ghidra_project_backup.py"
OPEN_PROBE = REPO / "tools/GhidraProjectOpenProbe.java"

PROGRAM_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
TARGET_COUNT = 31
PRE_FUNCTIONS = 8170
POST_FUNCTIONS = 8201
PRE_INSTRUCTIONS = 549872
POST_INSTRUCTIONS = 550982
PRE_REFERENCES = 234357
POST_REFERENCES = 234537

STAMPS = {
    MANIFEST: (14930, "afc13e4c56a5598c06872326e05e7e61d535a1271e81943c498303a46ee1a586"),
    MUTATOR: (47139, "9c488f095c85852d69cafc02e65efdac0c5bfa82538df38f5bbfb039c1e0390d"),
    INVENTORY: (23963, "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197"),
    DIFF: (9622, "b4956fbf9c9125cfdd7b7810cdc15f298fef8a081a880f82d6231a6dcbb25460"),
    BACKUP: (27502, "0f426982916f0aab982efe54664342a5d34607c2f89707159ecf6c07e205ad58"),
    OPEN_PROBE: (3452, "fab2f701dfefe8604c1718d007dbe0ad59d330a9b3ec081ef2f2fe253b441fab"),
}

PRE_FUNCTIONS_SHA256 = "ee3090360bd4f4b68d1ac52c59ab397e7ac37d81c76029d492e2a9d046902f1d"
PRE_PROGRAM_SHA256 = "2360923e0fa95648a708ee44297006dee222036662d7b34108d10a1fa405dc02"
POST_FUNCTIONS_SHA256 = "2cc0b74f9284a3d6d59effa857cb6766bb78b08d50a7896d0dda8631f7c93314"
POST_PROGRAM_SHA256 = "be169e6bae9bbd32c822a70c180e43960336fd85ee8ad52f5f494090c0a1e636"
DRY_BOUNDARIES_SHA256 = "a02922eb296d7388c1101c926ace46ccd862bb6f92739cca7cdb5c40a82642fe"
APPLY_BOUNDARIES_SHA256 = "2898bc62b33e94d1478e7848ff051e71c9a576a3c9df7699f5180c8e321b9ecf"
READBACK_BOUNDARIES_SHA256 = "15411a14e5cb011d8c6d28948280d8a8a4bf9f144e8a9859c456e6b5841a8597"
DB_18611 = (
    68288512,
    "6f45cdac7ae1f10987280f0ec247e6b5d6dcf866eae79e5982efa78dd68455ce",
)
BASE_PROJECT = (19, 186813317)

PRE_PROGRAM = {
    "programName": "BEA.exe",
    "executableMD5": PROGRAM_MD5,
    "executableSHA256": PROGRAM_SHA256,
    "imageBase": "0x00400000",
    "language": "x86:LE:32:default",
    "compilerSpec": "windows",
    "memorySha256": "5398f750f1ffb59873a6ec7e1750b51d11b5b844a8fda8d4e43649b5b9e5089d",
    "functions": "8170",
    "instructions": "549872",
    "instructionLayoutSha256": "ba8b9d6380c2acb63f625b95d6a08d3ae4df209a9da0fa41ae4c13c86e3f4ba2",
    "definedData": "48585",
    "definedDataSha256": "3b87eb91228e20c1d627318cc2563811043c1500af1497575ab128e7edf6e9e3",
    "undefinedData": "3912345",
    "symbolsUserDefined": "6104",
    "symbolsAnalysis": "18006",
    "symbolsImported": "907",
    "symbolsDefaultOther": "61594",
    "nonFunctionSymbolsSha256": "3e9936f251588865a77b62bdf577c110a7346e57c0e5a234e1feab9ab41622ac",
    "references": "234357",
    "referencesSha256": "704d5f045abfdf899761990b23494bf78f4d214bc0f55785184ec431b41abccf",
    "comments": "9199",
    "commentsSha256": "37a7b6d7dd4049a2e45e7d941de0bde92fadca50a03369e2401046b7cab3e927",
    "relocations": "0",
}

POST_PROGRAM = {
    **PRE_PROGRAM,
    "functions": "8201",
    "instructions": "550982",
    "instructionLayoutSha256": "1147925bc6a74dcb3a978ce9c4e5f82f7e2f798d18c067ddf6c12a2428cf6e05",
    "undefinedData": "3908592",
    "symbolsDefaultOther": "61686",
    "references": "234537",
    "referencesSha256": "af3ea9116ad127f153902ad9c3143510057062f4ad03869ac4136d2962d2fb01",
}

CLAIMS = (
    "Two independent disposable db.18611 replicas persist exactly the 31 manifest-bound function bodies and reproduce byte-identical full function and program inventories.",
    "Admission defines 1,110 previously undefined instructions and 180 derived references; every new instruction and reference source is constrained to the admitted body sets by the mutator, while memory, defined data, stored non-function symbols, comments, and all 8,170 PRE function rows remain unchanged.",
    "A forced failure after the first target and a forced failure after full nested commit plus explicit compensation both reopen to byte-identical PRE exported state.",
    "Names, signatures, semantics, runtime reachability, rebuild parity, and live or tracked Ghidra promotion are not authorized by this scratch receipt.",
    "This is unsigned machine-local evidence for a trusted quiescent host, not hostile-actor-resistant or portable archival proof.",
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


def stamp(path: Path, root: Path = REPO) -> dict[str, Any]:
    require(path.is_file(), f"missing artifact: {path}")
    return {
        "path": path.resolve().relative_to(root.resolve()).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AuthorityError(f"invalid JSON: {path}") from exc


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def function_inventory(path: Path) -> tuple[list[str], dict[str, tuple[str, ...]]]:
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.reader(stream, delimiter="\t")
        header = next(reader, None)
        require(header is not None and "address" in header, f"bad function header: {path}")
        require(len(header) == len(set(header)), f"duplicate function header: {path}")
        address_index = header.index("address")
        rows: dict[str, tuple[str, ...]] = {}
        for row in reader:
            require(len(row) == len(header), f"bad function row: {path}")
            address = row[address_index]
            require(address not in rows, f"duplicate function address: {address}")
            rows[address] = tuple(row)
    return header, rows


def verify_full_pre_rows_equal(before: Path, after: Path, label: str) -> None:
    before_header, before_rows = function_inventory(before)
    after_header, after_rows = function_inventory(after)
    require(before_header == after_header, f"{label} function header drift")
    require(len(before_rows) == PRE_FUNCTIONS, f"{label} PRE function row count")
    require(len(after_rows) == POST_FUNCTIONS, f"{label} POST function row count")
    for address, row in before_rows.items():
        require(after_rows.get(address) == row, f"{label} full PRE row drift at {address}")


def verify_portable_path(value: Any, expected: str, label: str) -> None:
    require(isinstance(value, str) and value == expected, f"{label} path")
    require("\\" not in value and ":" not in value, f"{label} path is not POSIX relative")
    require(not value.startswith("/"), f"{label} path is absolute")


def program_rows(path: Path) -> dict[str, str]:
    rows: dict[str, str] = {}
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.reader(stream, delimiter="\t")
        require(next(reader, None) == ["metric", "value"], f"bad program header: {path}")
        for row in reader:
            require(len(row) == 2 and row[0] not in rows, f"bad program row: {path}")
            rows[row[0]] = row[1]
    return rows


def verify_stamp(path: Path, expected: tuple[int, str], label: str) -> None:
    require(path.is_file(), f"missing {label}: {path}")
    require(path.stat().st_size == expected[0], f"{label} byte count drift")
    require(sha256_file(path) == expected[1], f"{label} SHA-256 drift")


def verify_project_copy_receipt(path: Path, label: str) -> None:
    payload = read_json(path)
    require(payload.get("schemaVersion") == "onslaught-ghidra-project-backup.v2", f"{label} schema")
    require(payload.get("copyComparison", {}).get("matches") is True, f"{label} copy mismatch")
    for role in ("source", "destination"):
        project = payload.get(role, {})
        require(
            (project.get("fileCount"), project.get("totalBytes")) == BASE_PROJECT,
            f"{label} {role} identity mismatch",
        )


def manifest_targets() -> list[dict[str, str]]:
    rows = read_tsv(MANIFEST)
    require(len(rows) == TARGET_COUNT, "target manifest count drift")
    expected_ids = [f"CF-{index:03d}" for index in range(1, TARGET_COUNT + 1)]
    require([row["candidateId"] for row in rows] == expected_ids, "target ids drift")
    require(len({row["retailEntry"].lower() for row in rows}) == TARGET_COUNT, "duplicate entries")
    return rows


def verify_boundary_rows(path: Path, mode: str, targets: list[dict[str, str]]) -> None:
    rows = read_tsv(path)
    require(len(rows) == TARGET_COUNT, f"{mode} boundary row count")
    status = {"dry": "ready_absent", "apply": "created", "readback": "verified"}[mode]
    for expected, actual in zip(targets, rows, strict=True):
        entry = expected["retailEntry"].lower()
        require(actual["candidateId"] == expected["candidateId"], f"{mode} candidate id")
        require(actual["cohort"] == expected["cohort"], f"{mode} cohort")
        require(actual["entry"] == entry and actual["status"] == status, f"{mode} entry/status")
        require(actual["expectedRanges"] == expected["retailBodyRangesHalfOpen"].lower(), f"{mode} ranges")
        require(actual["expectedBodyBytes"] == expected["bodyBytes"], f"{mode} body bytes")
        require(actual["expectedRangeSha256"] == expected["bodyRangeSha256"], f"{mode} range hash")
        require(actual["expectedBodyBytesSha256"] == expected["bodyBytesSha256"], f"{mode} body hash")
        require(actual["externalInstructionCount"] == expected["instructionCount"], f"{mode} instruction count")
        if mode == "dry":
            for field in (
                "name", "nameSource", "actualRanges", "actualRangeSha256",
                "actualBodyBytesSha256",
            ):
                require(actual[field] == "", f"dry unexpectedly populated {field}")
            require(actual["actualBodyBytes"] == "0", "dry actual body bytes")
            require(actual["actualGhidraInstructionCount"] == "0", "dry actual instructions")
        else:
            require(actual["name"] == "FUN_" + entry[2:], f"{mode} default name")
            require(actual["nameSource"] == "DEFAULT", f"{mode} name source")
            require(actual["actualRanges"] == actual["expectedRanges"], f"{mode} actual ranges")
            require(actual["actualBodyBytes"] == actual["expectedBodyBytes"], f"{mode} actual bytes")
            require(actual["actualRangeSha256"] == actual["expectedRangeSha256"], f"{mode} actual range hash")
            require(actual["actualBodyBytesSha256"] == actual["expectedBodyBytesSha256"], f"{mode} actual body hash")
            require(
                actual["actualGhidraInstructionCount"] == actual["externalInstructionCount"],
                f"{mode} Ghidra/external instruction mismatch",
            )


def verify_ready(path: Path, mode: str, output: Path, expected_counts: dict[str, int]) -> None:
    payload = read_json(path)
    require(payload.get("schemaVersion") == "bea.ghidra.text-gap-boundaries.v2", f"{mode} ready schema")
    require(payload.get("mode") == mode, f"{mode} ready mode")
    tool = payload.get("tool", {})
    require((tool.get("bytes"), tool.get("sha256")) == STAMPS[MUTATOR], f"{mode} tool stamp")
    verify_portable_path(
        tool.get("path"),
        (LANE / "inputs/GhidraApplyTextGapBoundaries.java").relative_to(REPO).as_posix(),
        f"{mode} tool",
    )
    manifest = payload.get("manifest", {})
    require((manifest.get("bytes"), manifest.get("sha256")) == STAMPS[MANIFEST], f"{mode} manifest stamp")
    verify_portable_path(
        manifest.get("path"), MANIFEST.relative_to(REPO).as_posix(), f"{mode} manifest"
    )
    observed_output = payload.get("output", {})
    verify_portable_path(
        observed_output.get("path"), output.relative_to(REPO).as_posix(), f"{mode} output"
    )
    require((observed_output.get("bytes"), observed_output.get("sha256")) == (output.stat().st_size, sha256_file(output)), f"{mode} output stamp")
    require(payload.get("counts") == expected_counts, f"{mode} counts")
    require(payload.get("explicitBodySetsAuthorized") is True, f"{mode} body authorization")
    require(payload.get("namesAuthorized") is False, f"{mode} name boundary")
    require(payload.get("metadataAuthorized") is False, f"{mode} metadata boundary")
    require(payload.get("separateReadbackRequired") is (mode != "readback"), f"{mode} readback flag")


def verify_diff(path: Path, targets: list[dict[str, str]]) -> None:
    payload = read_json(path)
    counts = payload.get("counts", {})
    expected_counts = {
        "before": PRE_FUNCTIONS,
        "after": POST_FUNCTIONS,
        "created": TARGET_COUNT,
        "destroyed": 0,
        "boundsChanged": 0,
        "namesChanged": 0,
        "signaturesChanged": 0,
        "paramCountChanged": 0,
        "callingConvChanged": 0,
        "returnTypeChanged": 0,
        "sigSourceChanged": 0,
        "instrCountChanged": 0,
        "noReturnChanged": 0,
        "thunkFlagChanged": 0,
    }
    require(counts == expected_counts, "inventory diff counts")
    dangerous = payload.get("dangerous", {})
    for key in (
        "gradedDestroyedCount", "gradedRenamedCount", "gradedDemotedCount",
        "gradedBoundsMovedCount",
    ):
        require(dangerous.get(key) == 0, f"inventory diff dangerous {key}")
    require(payload.get("destroyed") == [], "inventory diff destroyed rows")
    require(all(not value for value in payload.get("changesByField", {}).values()), "inventory diff field changes")
    created = payload.get("created", [])
    require(len(created) == TARGET_COUNT, "inventory diff created rows")
    for expected, actual in zip(targets, created, strict=True):
        entry = expected["retailEntry"].lower()
        require(actual == {
            "address": entry,
            "name": "FUN_" + entry[2:],
            "bodyBytes": expected["bodyBytes"],
            "instrCount": expected["instructionCount"],
            "nameSource": "DEFAULT",
        }, f"created row mismatch at {entry}")


def verify_run_file_set(run: str, expected: Iterable[str]) -> None:
    root = LANE / "runs" / run
    require(root.is_dir(), f"missing run: {run}")
    actual = sorted(path.name for path in root.iterdir() if path.is_file())
    require(actual == sorted(expected), f"unexpected output file set for {run}: {actual}")


def verify_campaign() -> dict[str, Any]:
    require(LANE.is_dir(), "formal scratch lane is missing")
    for path, expected in STAMPS.items():
        verify_stamp(path, expected, path.name)
    copied = {
        MUTATOR: LANE / "inputs/GhidraApplyTextGapBoundaries.java",
        INVENTORY: LANE / "inputs/ExportFullFunctionInventory.java",
        DIFF: LANE / "inputs/ghidra_inventory_diff.py",
        MANIFEST: LANE / "inputs/text-gap-missing-function-boundaries-2026-08-13.tsv",
    }
    for source, copy in copied.items():
        verify_stamp(copy, STAMPS[source], f"frozen {source.name}")

    db = LANE / "projects/base/BEA.rep/idata/00/~00000000.db/db.18611.gbf"
    verify_stamp(db, DB_18611, "db.18611 PRE")
    inspect = read_json(LANE / "base-project.inspect.json")
    manifest = inspect.get("manifest", {})
    require((manifest.get("fileCount"), manifest.get("totalBytes")) == BASE_PROJECT, "base inspect identity")
    db_rows = {row.get("relative_path"): row for row in manifest.get("files", [])}
    require(db_rows.get("BEA.rep/idata/00/~00000000.db/db.18611.gbf") == {
        "relative_path": "BEA.rep/idata/00/~00000000.db/db.18611.gbf",
        "size": DB_18611[0],
        "sha256": DB_18611[1],
    }, "base inspect db.18611 row")

    for project in ("base", "replica-a", "replica-b", "probe-after-one", "probe-post-inner"):
        verify_project_copy_receipt(
            LANE / "projects" / project / "backup_manifest.json", project
        )
    restore = read_json(LANE / "base-restore.ready.json")
    require(restore.get("schemaVersion") == "onslaught-ghidra-project-backup.v2", "restore schema")
    require(restore.get("copyComparison", {}).get("matches") is True, "restore copy")
    require(
        restore.get("probeCopyDisposition") == "RETAINED_AT_VERIFICATION",
        "restore probe was not retained",
    )
    retained = [path for path in (LANE / "restore-probe-final").iterdir() if path.is_dir()]
    require(len(retained) == 1, "restore probe directory count")
    require(
        Path(str(restore.get("probeCopy", ""))).name == retained[0].name,
        "restore probe basename mismatch",
    )
    verify_project_copy_receipt(
        retained[0] / "backup_manifest.json", "retained restore probe"
    )
    opened = restore.get("readonlyOpen", {})
    require(opened.get("opened") is True and opened.get("contentStable") is True, "restore open")
    require(opened.get("exitCode") == 0 and opened.get("observedFunctionCount") == 8394, "restore census")
    require(opened.get("observedProgramSha256") == PROGRAM_SHA256, "restore program")

    targets = manifest_targets()
    base_functions = LANE / "runs/base-inventory/functions.tsv"
    base_program = LANE / "runs/base-inventory/program.tsv"
    verify_stamp(base_functions, (7089535, PRE_FUNCTIONS_SHA256), "PRE functions")
    verify_stamp(base_program, (1267, PRE_PROGRAM_SHA256), "PRE program")
    require(program_rows(base_program) == PRE_PROGRAM | {
        key: value for key, value in program_rows(base_program).items() if key.startswith("block:")
    }, "PRE program metrics")
    require(len(read_tsv(base_functions)) == PRE_FUNCTIONS, "PRE function rows")

    verify_run_file_set("base-inventory", ("console.log", "functions.tsv", "ghidra.log", "program.tsv"))
    expected_mode_counts = {
        "dry": {
            "targets": 31, "functionsBefore": 8170, "functionsAfter": 8170,
            "instructionsBefore": 549872, "instructionsAfter": 549872,
        },
        "apply": {
            "targets": 31, "functionsBefore": 8170, "functionsAfter": 8201,
            "instructionsBefore": 549872, "instructionsAfter": 550982,
        },
        "readback": {
            "targets": 31, "functionsBefore": 8201, "functionsAfter": 8201,
            "instructionsBefore": 550982, "instructionsAfter": 550982,
        },
    }
    for replica in ("replica-a", "replica-b"):
        for mode, expected_hash in (
            ("dry", DRY_BOUNDARIES_SHA256),
            ("apply", APPLY_BOUNDARIES_SHA256),
            ("readback", READBACK_BOUNDARIES_SHA256),
        ):
            run = f"{replica}-{mode}"
            root = LANE / "runs" / run
            expected_files = ["boundaries.ready.json", "boundaries.tsv", "console.log", "ghidra.log"]
            if mode == "readback":
                expected_files += ["functions.tsv", "inventory-diff.json", "inventory-diff.log", "program.tsv"]
            verify_run_file_set(run, expected_files)
            boundaries = root / "boundaries.tsv"
            expected_size = {"dry": 7095, "apply": 12286, "readback": 12317}[mode]
            verify_stamp(boundaries, (expected_size, expected_hash), f"{run} boundaries")
            verify_boundary_rows(boundaries, mode, targets)
            verify_ready(root / "boundaries.ready.json", mode, boundaries, expected_mode_counts[mode])
        readback = LANE / "runs" / f"{replica}-readback"
        verify_stamp(readback / "functions.tsv", (7109943, POST_FUNCTIONS_SHA256), f"{replica} functions")
        verify_stamp(readback / "program.tsv", (1267, POST_PROGRAM_SHA256), f"{replica} program")
        require(program_rows(readback / "program.tsv") == POST_PROGRAM | {
            key: value for key, value in program_rows(readback / "program.tsv").items() if key.startswith("block:")
        }, f"{replica} program metrics")
        require(len(read_tsv(readback / "functions.tsv")) == POST_FUNCTIONS, f"{replica} function rows")
        verify_full_pre_rows_equal(base_functions, readback / "functions.tsv", replica)
        verify_diff(readback / "inventory-diff.json", targets)

    for relative in ("boundaries.tsv", "functions.tsv", "program.tsv"):
        require(
            sha256_file(LANE / "runs/replica-a-readback" / relative)
            == sha256_file(LANE / "runs/replica-b-readback" / relative),
            f"replica readback differs: {relative}",
        )

    controls = {
        "probe-after-one": (
            "TEXT_GAP_BOUNDARIES_FORCED_AFTER_ONE_FAILURE",
            "TEXT_GAP_BOUNDARIES_MUTATION_TAINTED mode=probe-after-one",
        ),
        "probe-post-inner": (
            "TEXT_GAP_BOUNDARIES_COMPENSATING_PRE_RESTORE_COMPLETE",
            "TEXT_GAP_BOUNDARIES_FORCED_POST_INNER_FAILURE",
        ),
    }
    for control, markers in controls.items():
        verify_run_file_set(control, ("console.log", "ghidra.log"))
        text = (LANE / "runs" / control / "console.log").read_text(encoding="utf-8")
        require(text.count("REPORT SCRIPT ERROR") == 1, f"{control} script-error count")
        for marker in markers:
            require(text.count(marker) == 1, f"{control} marker: {marker}")
        readback = LANE / "runs" / f"{control}-readback"
        verify_run_file_set(f"{control}-readback", ("console.log", "functions.tsv", "ghidra.log", "program.tsv"))
        verify_stamp(readback / "functions.tsv", (7089535, PRE_FUNCTIONS_SHA256), f"{control} functions")
        verify_stamp(readback / "program.tsv", (1267, PRE_PROGRAM_SHA256), f"{control} program")

    for preflight in ("preflight-external-output", "preflight-external-ready"):
        verify_run_file_set(preflight, ("console.log", "ghidra.log"))
        text = (LANE / "runs" / preflight / "console.log").read_text(encoding="utf-8")
        require(text.count("REPORT SCRIPT ERROR") == 1, f"{preflight} script-error count")
        require(
            text.count("receipts must stay inside this repository's local-lab tree") == 1,
            f"{preflight} containment refusal",
        )

    return {
        "targets": TARGET_COUNT,
        "bodyBytes": sum(int(row["bodyBytes"]) for row in targets),
        "preFunctions": PRE_FUNCTIONS,
        "postFunctions": POST_FUNCTIONS,
        "preInstructions": PRE_INSTRUCTIONS,
        "postInstructions": POST_INSTRUCTIONS,
        "newInstructions": POST_INSTRUCTIONS - PRE_INSTRUCTIONS,
        "preReferences": PRE_REFERENCES,
        "postReferences": POST_REFERENCES,
        "newReferences": POST_REFERENCES - PRE_REFERENCES,
        "preservedPreFunctionRows": PRE_FUNCTIONS,
        "replicas": 2,
        "adverseControls": 2,
        "externalPathPreflights": 2,
    }


def is_reparse(path: Path) -> bool:
    info = path.lstat()
    return path.is_symlink() or bool(
        getattr(info, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    )


def artifact_tree() -> dict[str, Any]:
    rows: list[tuple[str, int, str]] = []
    for path in sorted(LANE.rglob("*"), key=lambda item: item.as_posix().casefold()):
        require(not is_reparse(path), f"artifact tree contains reparse point: {path}")
        if not path.is_file() or path == READY or ".partial-" in path.name:
            continue
        relative = path.relative_to(LANE).as_posix()
        rows.append((relative, path.stat().st_size, sha256_file(path)))
    digest = hashlib.sha256()
    for relative, size, file_hash in rows:
        digest.update(f"{relative}\t{size}\t{file_hash}\n".encode("utf-8"))
    return {
        "fileCount": len(rows),
        "totalBytes": sum(row[1] for row in rows),
        "sha256": digest.hexdigest(),
    }


def build_payload(completed_at: str) -> dict[str, Any]:
    summary = verify_campaign()
    return {
        "schemaVersion": SCHEMA,
        "completedAtUtc": completed_at,
        "verdict": "SCRATCH_ADMISSION_READY_LIVE_NOT_AUTHORIZED",
        "baseCommit": "fa07f0a8c970b3040bab98708badb01685fe1546",
        "program": {"name": "BEA.exe", "md5": PROGRAM_MD5, "sha256": PROGRAM_SHA256},
        "preDatabase": {"name": "db.18611.gbf", "bytes": DB_18611[0], "sha256": DB_18611[1]},
        "summary": summary,
        "tools": {
            "authority": stamp(SCRIPT),
            "mutator": stamp(MUTATOR),
            "inventory": stamp(INVENTORY),
            "diff": stamp(DIFF),
            "backup": stamp(BACKUP),
            "openProbe": stamp(OPEN_PROBE),
        },
        "manifest": stamp(MANIFEST),
        "evidence": {
            "preFunctions": stamp(LANE / "runs/base-inventory/functions.tsv"),
            "preProgram": stamp(LANE / "runs/base-inventory/program.tsv"),
            "replicaAFunctions": stamp(LANE / "runs/replica-a-readback/functions.tsv"),
            "replicaAProgram": stamp(LANE / "runs/replica-a-readback/program.tsv"),
            "replicaBFunctions": stamp(LANE / "runs/replica-b-readback/functions.tsv"),
            "replicaBProgram": stamp(LANE / "runs/replica-b-readback/program.tsv"),
            "recoverability": stamp(LANE / "base-restore.ready.json"),
        },
        "artifactTree": artifact_tree(),
        "claims": list(CLAIMS),
        "liveMutationAuthorized": False,
        "trackedGhidraMutationAuthorized": False,
    }


def write_new(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(not path.exists(), f"refusing to overwrite: {path}")
    content = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def seal() -> None:
    completed_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    payload = build_payload(completed_at)
    write_new(READY, payload)
    print(
        "TEXT_GAP_SCRATCH_AUTHORITY_READY "
        f"targets={payload['summary']['targets']} "
        f"post_functions={payload['summary']['postFunctions']} "
        "live_authorized=false"
    )


def verify() -> None:
    recorded = read_json(READY)
    require(recorded.get("schemaVersion") == SCHEMA, "authority schema drift")
    completed_at = recorded.get("completedAtUtc")
    require(isinstance(completed_at, str) and completed_at.endswith("Z"), "authority timestamp")
    require(recorded == build_payload(completed_at), "authority receipt does not reproduce")
    print(
        "TEXT_GAP_SCRATCH_AUTHORITY_VERIFIED "
        f"sha256={sha256_file(READY)} live_authorized=false"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("seal", "verify"))
    args = parser.parse_args()
    try:
        seal() if args.command == "seal" else verify()
    except AuthorityError as exc:
        print(f"TEXT_GAP_SCRATCH_AUTHORITY_REFUSED reason={exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
