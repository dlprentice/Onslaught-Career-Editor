#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Seal or reproduce the isolated 79-row external-table gap admission.

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
import re
import stat
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[1]
SCRIPT = Path(__file__).resolve()
LANE = REPO / "local-lab/ghidra-external-table-gap-boundary-current-scratch-20260814-v1"
READY = LANE / "scratch-authority-v3.ready.json"
SCHEMA = "bea.ghidra.external-table-gap-boundary-scratch-authority.v3"

MANIFEST = (
    REPO
    / "reverse-engineering/binary-analysis/"
    "external-table-gap-function-boundaries-2026-08-13.tsv"
)
CONSUMED_PROOF = (
    REPO
    / "reverse-engineering/binary-analysis/"
    "d3dx-vec4cross-crossbuild-boundary-2026-08-13.md"
)
MUTATOR = REPO / "tools/GhidraApplyExternalTableGapBoundaries.java"
INVENTORY = REPO / "tools/ExportFullFunctionInventory.java"
DIFF = REPO / "tools/ghidra_inventory_diff.py"
BACKUP = REPO / "tools/ghidra_project_backup.py"
OPEN_PROBE = REPO / "tools/GhidraProjectOpenProbe.java"

PROGRAM_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
TARGET_COUNT = 79
PRE_FUNCTIONS = 8201
POST_FUNCTIONS = 8280
PRE_INSTRUCTIONS = 550982
POST_INSTRUCTIONS = 550991
PRE_REFERENCES = 234537
POST_REFERENCES = 234495
EXTERNAL_INSTRUCTIONS = 3319
GHIDRA_BODY_INSTRUCTIONS = 3318

STAMPS = {
    MANIFEST: (30020, "4293ebb936639299301985f128728b127ca60014693871a981d2324d47f2044f"),
    CONSUMED_PROOF: (4862, "1a7e705984830fee60f3d0710c0b017bd663ef27a805f1aa14beb0625863d306"),
    MUTATOR: (57413, "82e58540077a6099c433797d7150480f68e41eb995709f7df16ad2182a0c68eb"),
    INVENTORY: (23963, "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197"),
    DIFF: (9622, "b4956fbf9c9125cfdd7b7810cdc15f298fef8a081a880f82d6231a6dcbb25460"),
    BACKUP: (27502, "0f426982916f0aab982efe54664342a5d34607c2f89707159ecf6c07e205ad58"),
    OPEN_PROBE: (3452, "fab2f701dfefe8604c1718d007dbe0ad59d330a9b3ec081ef2f2fe253b441fab"),
}

PRE_FUNCTIONS_SHA256 = "2cc0b74f9284a3d6d59effa857cb6766bb78b08d50a7896d0dda8631f7c93314"
PRE_PROGRAM_SHA256 = "be169e6bae9bbd32c822a70c180e43960336fd85ee8ad52f5f494090c0a1e636"
POST_FUNCTIONS_SHA256 = "c3942b9e340cef71b731290b845843697af5c53204449c51949b779e896272d6"
POST_PROGRAM_SHA256 = "3e51ce1d5e926c632869b2058c9d89e91f48345a329a724ea9520570bd91212d"
DRY_BOUNDARIES_SHA256 = "a09a264de05e7394384eac466ad8ab1357252e1bd2c663a8ee7858db39462594"
APPLY_BOUNDARIES_SHA256 = "97db9f391eb4a42a6a5f192ed37dfe3f29bdf6229c3437f17b1bd787a6007592"
READBACK_BOUNDARIES_SHA256 = "2f4b23ac985f55562a1897dc3d4163bd546b8b752c1c302e7d35f1d6ae365eb9"
DB_18612 = (
    68321280,
    "424775377ea0f40d9e429c9219b9310d427760acc40548dbc588ca285f932f7b",
)
BASE_PROJECT = (19, 186911621)
CANONICAL_PROJECT_SHA256 = (
    "91776fb4a67579950afc4fb3b48ea8a866733628aecfdae7a2cb918c615fe211"
)
SUPERSEDED_AUTHORITY = (
    6276,
    "ab4bdc76df4dafbea2aa7da1613aac5a4673d89100b4f5f2ccff1dc02174072a",
)
SUPERSEDED_RESTORE = (
    6281,
    "5c3de62c4b484657061de53df4a208281fbd7d42e7339784c876bef20918144e",
)
SUPERSEDED_PROBE_LOG = (
    116,
    "33f37a2cf262eb69e9f3a2691a6696f92bb429ae493214eea388738cbc548ec3",
)

PRE_PROGRAM = {
    "programName": "BEA.exe",
    "executableMD5": PROGRAM_MD5,
    "executableSHA256": PROGRAM_SHA256,
    "imageBase": "0x00400000",
    "language": "x86:LE:32:default",
    "compilerSpec": "windows",
    "memorySha256": "5398f750f1ffb59873a6ec7e1750b51d11b5b844a8fda8d4e43649b5b9e5089d",
    "functions": "8201",
    "instructions": "550982",
    "instructionLayoutSha256": "1147925bc6a74dcb3a978ce9c4e5f82f7e2f798d18c067ddf6c12a2428cf6e05",
    "definedData": "48585",
    "definedDataSha256": "3b87eb91228e20c1d627318cc2563811043c1500af1497575ab128e7edf6e9e3",
    "undefinedData": "3908592",
    "symbolsUserDefined": "6104",
    "symbolsAnalysis": "18006",
    "symbolsImported": "907",
    "symbolsDefaultOther": "61686",
    "nonFunctionSymbolsSha256": "3e9936f251588865a77b62bdf577c110a7346e57c0e5a234e1feab9ab41622ac",
    "references": "234537",
    "referencesSha256": "af3ea9116ad127f153902ad9c3143510057062f4ad03869ac4136d2962d2fb01",
    "comments": "9199",
    "commentsSha256": "37a7b6d7dd4049a2e45e7d941de0bde92fadca50a03369e2401046b7cab3e927",
    "relocations": "0",
}

POST_PROGRAM = {
    **PRE_PROGRAM,
    "functions": "8280",
    "instructions": "550991",
    "instructionLayoutSha256": "6e432dd36dd5964a95d982091188a24d1a3add46ade7b44a387bac205c475658",
    "undefinedData": "3908482",
    "symbolsDefaultOther": "61684",
    "references": "234495",
    "referencesSha256": "e916cafb16fac23196717e182645066ba48f3cb6eccf10713be8b1435b3233e7",
}

CLAIMS = (
    "Two independent disposable db.18612 replicas persist exactly the 79 manifest-bound function bodies and reproduce byte-identical full function and program inventories.",
    "Admission replaces instruction decoding only inside the 9,234 authorized body bytes, yielding 3,318 Ghidra instructions for the externally measured 3,319-instruction ledger; the sole difference is Ghidra folding one FWAIT prefix at 0x0055E3F4.",
    "Memory, defined data, stored non-function symbols, comments, and every field of all 8,201 PRE function rows remain unchanged; instruction and reference rows outside the admitted body sets are protected by the mutator.",
    "A forced failure after the first target and a forced failure after the complete validated batch requests both nested and outer rollback; separate saved readbacks reproduce byte-identical PRE state.",
    "The exact base and retained restore project trees independently hash to the pinned 19-file canonical inventory, and the bound read-only probe log contains one success sentinel and no error marker.",
    "The mutator, manifest, positive replicas, rollback readbacks, and their full inventories are byte-identical to the superseded v2 authority receipt; only the read-only restore proof and aggregate authority were rerun.",
    "The 0x005762DD Vec4Cross row consumes the existing tracked proof, and the corrected 0x0058862E YUV-family identity is pinned without applying any names.",
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


def canonical_project_sha256(project: dict[str, Any], label: str) -> str:
    files = project.get("files")
    require(isinstance(files, list) and len(files) == BASE_PROJECT[0],
            f"{label} file ledger")
    rows: list[tuple[str, int, str]] = []
    for row in files:
        require(isinstance(row, dict), f"{label} file row")
        relative = row.get("relative_path")
        size = row.get("size")
        file_hash = row.get("sha256")
        require(
            isinstance(relative, str)
            and relative
            and "\\" not in relative
            and ":" not in relative
            and not relative.startswith("/"),
            f"{label} relative path",
        )
        require(isinstance(size, int) and size >= 0, f"{label} file size")
        require(
            isinstance(file_hash, str)
            and re.fullmatch(r"[0-9a-f]{64}", file_hash) is not None,
            f"{label} file hash",
        )
        rows.append((relative, size, file_hash))
    require(len({relative for relative, _, _ in rows}) == len(rows),
            f"{label} duplicate path")
    digest = hashlib.sha256()
    for relative, size, file_hash in sorted(rows):
        digest.update(f"{file_hash}\t{size}\t{relative}\n".encode("utf-8"))
    return digest.hexdigest()


def verify_actual_project_tree(project_root: Path, label: str) -> dict[str, Any]:
    require(project_root.is_dir() and not is_reparse(project_root),
            f"{label} project root")
    gpr = project_root / "BEA.gpr"
    rep = project_root / "BEA.rep"
    require(gpr.is_file() and not is_reparse(gpr), f"{label} BEA.gpr")
    require(rep.is_dir() and not is_reparse(rep), f"{label} BEA.rep")

    files = [gpr]
    for current, directories, names in os.walk(rep, followlinks=False):
        current_path = Path(current)
        require(not is_reparse(current_path), f"{label} reparse directory")
        for name in directories:
            require(not is_reparse(current_path / name),
                    f"{label} reparse directory")
        for name in names:
            path = current_path / name
            require(path.is_file() and not is_reparse(path),
                    f"{label} non-plain project file")
            files.append(path)

    rows: list[tuple[str, int, str]] = []
    for path in files:
        relative = path.relative_to(project_root).as_posix()
        rows.append((relative, path.stat().st_size, sha256_file(path)))
    rows.sort()
    require(len(rows) == BASE_PROJECT[0], f"{label} actual file count")
    require(sum(size for _, size, _ in rows) == BASE_PROJECT[1],
            f"{label} actual byte count")
    digest = hashlib.sha256()
    for relative, size, file_hash in rows:
        digest.update(f"{file_hash}\t{size}\t{relative}\n".encode("utf-8"))
    require(digest.hexdigest() == CANONICAL_PROJECT_SHA256,
            f"{label} actual canonical inventory mismatch")
    db_rows = {relative: (size, file_hash) for relative, size, file_hash in rows}
    require(
        db_rows.get("BEA.rep/idata/00/~00000000.db/db.18612.gbf") == DB_18612,
        f"{label} actual db.18612 mismatch",
    )
    return {
        "fileCount": len(rows),
        "totalBytes": sum(size for _, size, _ in rows),
        "canonicalInventorySha256": digest.hexdigest(),
    }


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
        require(
            canonical_project_sha256(project, f"{label} {role}")
            == CANONICAL_PROJECT_SHA256,
            f"{label} {role} canonical inventory mismatch",
        )


def artifact_tuple(value: Any, label: str) -> tuple[int, str]:
    require(isinstance(value, dict), f"{label} artifact")
    size = value.get("bytes")
    file_hash = value.get("sha256")
    require(isinstance(size, int) and size >= 0, f"{label} bytes")
    require(
        isinstance(file_hash, str)
        and re.fullmatch(r"[0-9a-f]{64}", file_hash) is not None,
        f"{label} hash",
    )
    return size, file_hash


def verify_superseded_v1() -> None:
    root = LANE
    authority_path = root / "scratch-authority.ready.json"
    restore_path = root / "base-restore.ready.json"
    probe_path = root / "base-restore.ready.open-probe.log"
    verify_stamp(authority_path, SUPERSEDED_AUTHORITY, "superseded authority")
    verify_stamp(restore_path, SUPERSEDED_RESTORE, "superseded restore receipt")
    verify_stamp(probe_path, SUPERSEDED_PROBE_LOG, "superseded overwritten probe log")
    prior = read_json(authority_path)
    require(
        prior.get("schemaVersion")
        == "bea.ghidra.external-table-gap-boundary-scratch-authority.v2",
        "superseded authority schema",
    )
    require(prior.get("verdict") == "SCRATCH_READY_LIVE_FORBIDDEN",
            "superseded authority verdict")
    require(artifact_tuple(prior.get("manifest"), "superseded manifest")
            == STAMPS[MANIFEST], "superseded manifest identity")
    require(artifact_tuple(prior.get("consumedProof"), "superseded proof")
            == STAMPS[CONSUMED_PROOF], "superseded proof identity")
    tools = prior.get("tools", {})
    require(artifact_tuple(tools.get("mutator"), "superseded mutator")
            == STAMPS[MUTATOR], "superseded mutator identity")
    evidence = prior.get("evidence", {})
    expected = {
        "preFunctions": (7109943, PRE_FUNCTIONS_SHA256),
        "preProgram": (1267, PRE_PROGRAM_SHA256),
        "replicaAFunctions": (7161942, POST_FUNCTIONS_SHA256),
        "replicaAProgram": (1267, POST_PROGRAM_SHA256),
        "replicaBFunctions": (7161942, POST_FUNCTIONS_SHA256),
        "replicaBProgram": (1267, POST_PROGRAM_SHA256),
    }
    for name, exact in expected.items():
        require(artifact_tuple(evidence.get(name), f"superseded {name}") == exact,
                f"superseded {name} identity")


def verify_readonly_restore(
    restore: dict[str, Any], retained: Path, receipt_path: Path
) -> dict[str, Any]:
    opened = restore.get("readonlyOpen", {})
    require(isinstance(opened, dict), "restore readonly-open payload")
    require(opened.get("opened") is True and opened.get("contentStable") is True,
            "restore open")
    require(opened.get("exitCode") == 0 and opened.get("observedFunctionCount") == 8425,
            "restore census")
    require(opened.get("observedProgramSha256") == PROGRAM_SHA256,
            "restore program")

    argv = opened.get("commandArgv")
    require(isinstance(argv, list) and all(isinstance(arg, str) for arg in argv),
            "restore command argv")
    folded = [arg.casefold() for arg in argv]
    require(folded.count("-readonly") == 1, "restore command requires -readOnly")
    require(folded.count("-noanalysis") == 1, "restore command requires -noanalysis")
    require("-commit" not in folded, "restore command forbids -commit")
    require(folded.count("-process") == 1 and "bea.exe" in folded,
            "restore command process")
    require(argv.count("GhidraProjectOpenProbe.java") == 1,
            "restore command open probe")
    require(len(argv) > 1 and Path(argv[1]).name == retained.name,
            "restore command probe-copy basename")

    probe = opened.get("probeLog")
    require(isinstance(probe, dict), "restore probe-log receipt")
    expected_log_name = "base-restore-v2.ready.open-probe.log"
    require(probe.get("path") == expected_log_name, "restore probe-log path")
    log_path = receipt_path.parent / expected_log_name
    verify_stamp(log_path, artifact_tuple(probe, "restore probe log"),
                 "restore probe log")
    try:
        log_text = log_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise AuthorityError("restore probe log is unreadable") from exc
    sentinel = (
        "GHIDRA_PROJECT_OPEN_PROBE_OK program=BEA.exe "
        f"md5={PROGRAM_MD5} sha256={PROGRAM_SHA256} functions=8425"
    )
    require(log_text.count(sentinel) == 1, "restore probe success sentinel")
    for marker in (
        "REPORT SCRIPT ERROR",
        "GHIDRA_PROJECT_OPEN_PROBE_FAIL",
        "ERROR",
        "Exception",
        "Traceback",
    ):
        require(marker not in log_text, f"restore probe error marker: {marker}")
    require(log_text.count("Processing read-only project file: /BEA.exe") == 1,
            "restore probe read-only processing marker")

    console_path = receipt_path.parent / "base-restore-v2.console.log"
    require(console_path.is_file() and console_path.resolve() != log_path.resolve(),
            "restore console/log separation")
    console_text = console_path.read_text(encoding="utf-8")
    require(console_text.count("ReadOnlyOpen=PASS") == 1,
            "restore console success marker")
    require(sentinel not in console_text, "restore console replaced detailed probe log")
    return {
        "probeLog": (log_path.stat().st_size, sha256_file(log_path)),
        "consoleLog": (console_path.stat().st_size, sha256_file(console_path)),
    }


def manifest_targets() -> list[dict[str, str]]:
    rows = read_tsv(MANIFEST)
    require(len(rows) == TARGET_COUNT, "target manifest count drift")
    entries = [int(row["retail_va"], 16) for row in rows]
    require(entries == sorted(entries) and len(set(entries)) == TARGET_COUNT, "entry ordering")
    require(sum(int(row["body_bytes"]) for row in rows) == 9234, "body byte total")
    require(
        sum(int(row["instruction_count"]) for row in rows) == EXTERNAL_INSTRUCTIONS,
        "external instruction total",
    )
    require(
        {rank: sum(row["rank"] == rank for row in rows) for rank in ("P0", "P1", "P2")}
        == {"P0": 12, "P1": 20, "P2": 47},
        "rank counts",
    )
    require(all(row["demo_normalized_equal"] == "true" for row in rows), "demo evidence")
    require(sum(row["direct_defined_data_ref"] == "true" for row in rows) == 72, "direct refs")
    require(sum(row["already_prepared_receipt"] == "true" for row in rows) == 1, "proof count")

    occupied: list[tuple[int, int]] = []
    result: list[dict[str, str]] = []
    for index, source in enumerate(rows, 1):
        row = dict(source)
        row["candidateId"] = f"ETG-{index:03d}"
        require(
            (row["rank"] == "P2") == (row["safe_name_candidate"] == ""),
            f"rank/name boundary at {row['candidateId']}",
        )
        for piece in row["body_ranges"].split(";"):
            start_text, end_text = piece.split("-", 1)
            start, end = int(start_text, 16), int(end_text, 16)
            require(start < end, f"empty body range at {row['candidateId']}")
            require(all(end <= old_start or start >= old_end for old_start, old_end in occupied),
                    f"body overlap at {row['candidateId']}")
            occupied.append((start, end))
        result.append(row)

    vec4 = next(row for row in result if row["retail_va"].lower() == "0x005762dd")
    require(vec4["candidateId"] == "ETG-026", "Vec4Cross row id")
    require(vec4["already_prepared_receipt"] == "true", "Vec4Cross proof consumption")
    require(vec4["safe_name_candidate"] == "D3DX_COMPAT__c_D3DXVec4Cross", "Vec4 name")
    yuv = next(row for row in result if row["retail_va"].lower() == "0x0058862e")
    require(yuv["rank"] == "P1", "YUV rank")
    require(yuv["identity_status"] == "D3DX_SHARED_YUV_CODEC_DTOR_LINEAGE", "YUV identity")
    require(
        yuv["safe_name_candidate"]
        == "D3DX_COMPAT__CCodecYUVFamily__SharedScalarDeletingDtor",
        "YUV safe name",
    )
    return result


def verify_boundary_rows(path: Path, mode: str, targets: list[dict[str, str]]) -> None:
    rows = read_tsv(path)
    require(len(rows) == TARGET_COUNT, f"{mode} boundary row count")
    status = {"dry": "ready_absent", "apply": "created", "readback": "verified"}[mode]
    for expected, actual in zip(targets, rows, strict=True):
        entry = expected["retail_va"].lower()
        require(actual["candidateId"] == expected["candidateId"], f"{mode} candidate id")
        require(actual["rank"] == expected["rank"], f"{mode} rank")
        require(actual["identityStatus"] == expected["identity_status"], f"{mode} identity")
        require(actual["safeNameCandidate"] == expected["safe_name_candidate"], f"{mode} safe name")
        require(actual["cohort"] == expected["cohort"], f"{mode} cohort")
        require(actual["entry"] == entry and actual["status"] == status, f"{mode} entry/status")
        require(actual["expectedRanges"] == expected["body_ranges"].lower(), f"{mode} ranges")
        require(actual["expectedBodyBytes"] == expected["body_bytes"], f"{mode} body bytes")
        require(actual["expectedBodySha256"] == expected["body_sha256"], f"{mode} body hash")
        require(actual["externalInstructionCount"] == expected["instruction_count"], f"{mode} instruction count")
        require(actual["demoEntry"] == expected["demo_va"].lower(), f"{mode} demo entry")
        require(actual["demoCandidates"] == expected["demo_candidates"], f"{mode} demo candidates")
        require(actual["demoBasis"] == expected["demo_basis"], f"{mode} demo basis")
        require(actual["demoRawEqual"] == expected["demo_raw_equal"], f"{mode} demo raw equality")
        require(
            actual["alreadyPreparedReceipt"] == expected["already_prepared_receipt"],
            f"{mode} proof flag",
        )
        if mode == "dry":
            for field in ("name", "nameSource", "actualRanges", "actualBodySha256"):
                require(actual[field] == "", f"dry unexpectedly populated {field}")
            require(actual["actualBodyBytes"] == "0", "dry actual body bytes")
            require(actual["actualGhidraInstructionCount"] == "0", "dry actual instructions")
        else:
            require(actual["name"] == "FUN_" + entry[2:], f"{mode} default name")
            require(actual["nameSource"] == "DEFAULT", f"{mode} name source")
            require(actual["actualRanges"] == actual["expectedRanges"], f"{mode} actual ranges")
            require(actual["actualBodyBytes"] == actual["expectedBodyBytes"], f"{mode} actual bytes")
            require(actual["actualBodySha256"] == actual["expectedBodySha256"], f"{mode} actual body hash")
            expected_ghidra = "12" if entry == "0x0055e3f4" else expected["instruction_count"]
            require(actual["actualGhidraInstructionCount"] == expected_ghidra,
                    f"{mode} Ghidra instruction count")


def verify_ready(path: Path, mode: str, output: Path, expected_counts: dict[str, int]) -> None:
    payload = read_json(path)
    require(payload.get("schemaVersion") == "bea.ghidra.external-table-gap-boundaries.v2", f"{mode} ready schema")
    require(payload.get("mode") == mode, f"{mode} ready mode")
    tool = payload.get("tool", {})
    require((tool.get("bytes"), tool.get("sha256")) == STAMPS[MUTATOR], f"{mode} tool stamp")
    verify_portable_path(
        tool.get("path"),
        (LANE / "inputs/GhidraApplyExternalTableGapBoundaries.java").relative_to(REPO).as_posix(),
        f"{mode} tool",
    )
    manifest = payload.get("manifest", {})
    require((manifest.get("bytes"), manifest.get("sha256")) == STAMPS[MANIFEST], f"{mode} manifest stamp")
    verify_portable_path(
        manifest.get("path"), MANIFEST.relative_to(REPO).as_posix(), f"{mode} manifest"
    )
    consumed = payload.get("consumedProof", {})
    require((consumed.get("bytes"), consumed.get("sha256")) == STAMPS[CONSUMED_PROOF],
            f"{mode} consumed proof stamp")
    verify_portable_path(
        consumed.get("path"), CONSUMED_PROOF.relative_to(REPO).as_posix(),
        f"{mode} consumed proof",
    )
    observed_output = payload.get("output", {})
    verify_portable_path(
        observed_output.get("path"), output.relative_to(REPO).as_posix(), f"{mode} output"
    )
    require((observed_output.get("bytes"), observed_output.get("sha256")) == (output.stat().st_size, sha256_file(output)), f"{mode} output stamp")
    require(payload.get("counts") == expected_counts, f"{mode} counts")
    require(payload.get("explicitBodySetsAuthorized") is True, f"{mode} body authorization")
    require(payload.get("postCountsPinned") is True, f"{mode} post counts")
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
        entry = expected["retail_va"].lower()
        instruction_count = "12" if entry == "0x0055e3f4" else expected["instruction_count"]
        require(actual == {
            "address": entry,
            "name": "FUN_" + entry[2:],
            "bodyBytes": expected["body_bytes"],
            "instrCount": instruction_count,
            "nameSource": "DEFAULT",
        }, f"created row mismatch at {entry}")


def verify_run_file_set(run: str, expected: Iterable[str]) -> None:
    root = LANE / "runs" / run
    require(root.is_dir(), f"missing run: {run}")
    actual = sorted(path.name for path in root.iterdir() if path.is_file())
    require(actual == sorted(expected), f"unexpected output file set for {run}: {actual}")


def verify_campaign() -> dict[str, Any]:
    require(LANE.is_dir(), "formal scratch lane is missing")
    verify_superseded_v1()
    for path, expected in STAMPS.items():
        verify_stamp(path, expected, path.name)
    copied = {
        MUTATOR: LANE / "inputs/GhidraApplyExternalTableGapBoundaries.java",
        INVENTORY: LANE / "inputs/ExportFullFunctionInventory.java",
        DIFF: LANE / "inputs/ghidra_inventory_diff.py",
        MANIFEST: LANE / "inputs/external-table-gap-function-boundaries-2026-08-13.tsv",
        CONSUMED_PROOF: LANE / "inputs/d3dx-vec4cross-crossbuild-boundary-2026-08-13.md",
    }
    for source, copy in copied.items():
        verify_stamp(copy, STAMPS[source], f"frozen {source.name}")

    db = LANE / "projects/base/BEA.rep/idata/00/~00000000.db/db.18612.gbf"
    verify_stamp(db, DB_18612, "db.18612 PRE")
    base_actual = verify_actual_project_tree(LANE / "projects/base", "base project")
    inspect = read_json(LANE / "base-project.inspect.json")
    manifest = inspect.get("manifest", {})
    require((manifest.get("fileCount"), manifest.get("totalBytes")) == BASE_PROJECT, "base inspect identity")
    require(
        canonical_project_sha256(manifest, "base inspect")
        == CANONICAL_PROJECT_SHA256,
        "base inspect canonical inventory mismatch",
    )
    db_rows = {row.get("relative_path"): row for row in manifest.get("files", [])}
    require(db_rows.get("BEA.rep/idata/00/~00000000.db/db.18612.gbf") == {
        "relative_path": "BEA.rep/idata/00/~00000000.db/db.18612.gbf",
        "size": DB_18612[0],
        "sha256": DB_18612[1],
    }, "base inspect db.18612 row")

    for project in ("base", "replica-a", "replica-b", "probe-after-one", "probe-post-inner"):
        verify_project_copy_receipt(
            LANE / "projects" / project / "backup_manifest.json", project
        )
    restore_path = LANE / "base-restore-v2.ready.json"
    restore = read_json(restore_path)
    require(restore.get("schemaVersion") == "onslaught-ghidra-project-backup.v2", "restore schema")
    require(restore.get("copyComparison", {}).get("matches") is True, "restore copy")
    require(
        restore.get("probeCopyDisposition") == "RETAINED_AT_VERIFICATION",
        "restore probe was not retained",
    )
    retained = [
        path for path in (LANE / "restore-probe-final-v2").iterdir()
        if path.is_dir()
    ]
    require(len(retained) == 1, "restore probe directory count")
    require(
        Path(str(restore.get("probeCopy", ""))).name == retained[0].name,
        "restore probe basename mismatch",
    )
    verify_project_copy_receipt(
        retained[0] / "backup_manifest.json", "retained restore probe"
    )
    restore_actual = verify_actual_project_tree(
        retained[0], "retained restore project"
    )
    restore_logs = verify_readonly_restore(restore, retained[0], restore_path)
    require(base_actual == restore_actual, "actual base/restore tree mismatch")

    targets = manifest_targets()
    base_functions = LANE / "runs/base-inventory/functions.tsv"
    base_program = LANE / "runs/base-inventory/program.tsv"
    verify_stamp(base_functions, (7109943, PRE_FUNCTIONS_SHA256), "PRE functions")
    verify_stamp(base_program, (1267, PRE_PROGRAM_SHA256), "PRE program")
    require(program_rows(base_program) == PRE_PROGRAM | {
        key: value for key, value in program_rows(base_program).items() if key.startswith("block:")
    }, "PRE program metrics")
    require(len(read_tsv(base_functions)) == PRE_FUNCTIONS, "PRE function rows")

    verify_run_file_set("base-inventory", ("console.log", "functions.tsv", "ghidra.log", "program.tsv"))
    expected_mode_counts = {
        "dry": {
            "targets": 79, "externalInstructions": 3319, "ghidraBodyInstructions": 3318,
            "functionsBefore": 8201, "functionsAfter": 8201,
            "instructionsBefore": 550982, "instructionsAfter": 550982,
        },
        "apply": {
            "targets": 79, "externalInstructions": 3319, "ghidraBodyInstructions": 3318,
            "functionsBefore": 8201, "functionsAfter": 8280,
            "instructionsBefore": 550982, "instructionsAfter": 550991,
        },
        "readback": {
            "targets": 79, "externalInstructions": 3319, "ghidraBodyInstructions": 3318,
            "functionsBefore": 8280, "functionsAfter": 8280,
            "instructionsBefore": 550991, "instructionsAfter": 550991,
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
            expected_size = {"dry": 21022, "apply": 29018, "readback": 29097}[mode]
            verify_stamp(boundaries, (expected_size, expected_hash), f"{run} boundaries")
            verify_boundary_rows(boundaries, mode, targets)
            verify_ready(root / "boundaries.ready.json", mode, boundaries, expected_mode_counts[mode])
        readback = LANE / "runs" / f"{replica}-readback"
        verify_stamp(readback / "functions.tsv", (7161942, POST_FUNCTIONS_SHA256), f"{replica} functions")
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
            "EXTERNAL_TABLE_GAP_BOUNDARIES_FORCED_AFTER_ONE_FAILURE",
            "EXTERNAL_TABLE_GAP_BOUNDARIES_MUTATION_TAINTED mode=probe-after-one",
        ),
        "probe-post-inner": (
            "EXTERNAL_TABLE_GAP_BOUNDARIES_POST_INNER_ROLLBACK_REQUESTED",
            "EXTERNAL_TABLE_GAP_BOUNDARIES_FORCED_POST_INNER_FAILURE",
            "EXTERNAL_TABLE_GAP_BOUNDARIES_MUTATION_TAINTED mode=probe-post-inner",
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
        verify_stamp(readback / "functions.tsv", (7109943, PRE_FUNCTIONS_SHA256), f"{control} functions")
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
        "bodyBytes": sum(int(row["body_bytes"]) for row in targets),
        "externalInstructions": EXTERNAL_INSTRUCTIONS,
        "ghidraBodyInstructions": GHIDRA_BODY_INSTRUCTIONS,
        "rankCounts": {rank: sum(row["rank"] == rank for row in targets)
                       for rank in ("P0", "P1", "P2")},
        "preFunctions": PRE_FUNCTIONS,
        "postFunctions": POST_FUNCTIONS,
        "preInstructions": PRE_INSTRUCTIONS,
        "postInstructions": POST_INSTRUCTIONS,
        "instructionDelta": POST_INSTRUCTIONS - PRE_INSTRUCTIONS,
        "preReferences": PRE_REFERENCES,
        "postReferences": POST_REFERENCES,
        "referenceDelta": POST_REFERENCES - PRE_REFERENCES,
        "preservedPreFunctionRows": PRE_FUNCTIONS,
        "replicas": 2,
        "adverseControls": 2,
        "externalPathPreflights": 2,
        "actualProjectTrees": 2,
        "readonlyRestoreProofs": 1,
        "reusedExactPositiveReplicas": 2,
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
        "verdict": "SCRATCH_READY_LIVE_FORBIDDEN",
        "baseCommit": "b05623e57392c0ee1a66fe36c9b3900857a07ff3",
        "program": {"name": "BEA.exe", "md5": PROGRAM_MD5, "sha256": PROGRAM_SHA256},
        "preProject": {
            "files": BASE_PROJECT[0],
            "bytes": BASE_PROJECT[1],
            "canonicalInventorySha256": CANONICAL_PROJECT_SHA256,
        },
        "preDatabase": {"name": "db.18612.gbf", "bytes": DB_18612[0], "sha256": DB_18612[1]},
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
        "consumedProof": stamp(CONSUMED_PROOF),
        "evidence": {
            "preFunctions": stamp(LANE / "runs/base-inventory/functions.tsv"),
            "preProgram": stamp(LANE / "runs/base-inventory/program.tsv"),
            "replicaAFunctions": stamp(LANE / "runs/replica-a-readback/functions.tsv"),
            "replicaAProgram": stamp(LANE / "runs/replica-a-readback/program.tsv"),
            "replicaBFunctions": stamp(LANE / "runs/replica-b-readback/functions.tsv"),
            "replicaBProgram": stamp(LANE / "runs/replica-b-readback/program.tsv"),
            "recoverability": stamp(LANE / "base-restore-v2.ready.json"),
            "recoverabilityProbeLog": stamp(
                LANE / "base-restore-v2.ready.open-probe.log"
            ),
            "recoverabilityConsoleLog": stamp(
                LANE / "base-restore-v2.console.log"
            ),
            "supersededAuthority": stamp(
                LANE / "scratch-authority.ready.json"
            ),
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
        "EXTERNAL_TABLE_GAP_SCRATCH_AUTHORITY_READY "
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
        "EXTERNAL_TABLE_GAP_SCRATCH_AUTHORITY_VERIFIED "
        f"sha256={sha256_file(READY)} live_authorized=false"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("seal", "verify"))
    args = parser.parse_args()
    try:
        seal() if args.command == "seal" else verify()
    except AuthorityError as exc:
        print(f"EXTERNAL_TABLE_GAP_SCRATCH_AUTHORITY_REFUSED reason={exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
