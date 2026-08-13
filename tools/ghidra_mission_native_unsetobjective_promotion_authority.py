#!/usr/bin/env python3
"""Seal the bounded Mission-native UnsetObjective Ghidra promotion ceremony.

This owner is intentionally specific.  It admits exactly one new function at
0x00535EE0, one reviewed name/signature/comment, two independent scratch
replicas, two rollback controls, and (only after those pass) one live apply with
a separate read-only reopen and recoverable before/after backups.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping, Sequence


REPO = Path(__file__).resolve().parent.parent
SCRIPT = Path(__file__).resolve()
LANE = REPO / "local-lab" / "ghidra-mission-native-unsetobjective-live-promotion-20260809-v1"
LIVE = Path(r"C:\Users\david\Ghidra\Projects")
SOURCE_PRE = (
    REPO / "local-lab" / "ghidra-mission-native-setpos-live-promotion-20260809-v1"
    / "backups" / "post-live"
)
SOURCE_MANIFEST = SOURCE_PRE / "backup_manifest.json"
SOURCE_AUTHORITY = (
    REPO / "local-lab" / "ghidra-mission-native-setpos-live-promotion-20260809-v1"
    / "promotion" / "promotion.ready.json"
)
SOURCE_RESTORE = (
    REPO / "local-lab" / "ghidra-mission-native-setpos-live-promotion-20260809-v1"
    / "post-live-restore.ready.json"
)
SOURCE_FUNCTIONS = (
    REPO / "local-lab" / "ghidra-mission-native-setpos-live-promotion-20260809-v1"
    / "runs" / "live-inventory" / "functions.tsv"
)
SOURCE_PROGRAM = (
    REPO / "local-lab" / "ghidra-mission-native-setpos-live-promotion-20260809-v1"
    / "runs" / "live-inventory" / "program.tsv"
)
TOOL = REPO / "tools" / "GhidraApplyMissionNativeUnsetObjective.java"
INVENTORY_TOOL = REPO / "tools" / "ExportFullFunctionInventory.java"
OPEN_PROBE_TOOL = REPO / "tools" / "GhidraProjectOpenProbe.java"
CAMPAIGN = (
    REPO / "local-lab" / "re-campaign-incident-recovery-20260808-v1"
    / "generation-19-mission-native-unsetobjective-reproof-v1" / "campaign.ready.json"
)
PROOF = (
    REPO / "local-lab" / "mission-native-unsetobjective-boundary-reproof-20260809-v1"
    / "proof.ready.json"
)
CAMPAIGN_AUTHORITY = (
    REPO / "local-lab" / "re-campaign-incident-recovery-20260808-v1"
    / "generation-19-mission-native-unsetobjective-reproof-authority.ready.json"
)
BOUNDARY = (
    REPO / "local-lab" / "mission-native-unsetobjective-boundary-reproof-20260809-v1"
    / "ghidra-readonly-byte-complete" / "instructions.tsv"
)
PRE_BACKUP = LANE / "backups" / "pre-live"
PRE_MANIFEST = PRE_BACKUP / "backup_manifest.json"
PRE_RESTORE = LANE / "pre-live-restore.ready.json"
POST_BACKUP = LANE / "backups" / "post-live"
POST_MANIFEST = POST_BACKUP / "backup_manifest.json"
POST_RESTORE = LANE / "post-live-restore.ready.json"
SCRATCH_READY = LANE / "promotion" / "scratch-authority.ready.json"
LIVE_READY = LANE / "promotion" / "promotion.ready.json"
D_ROOT = Path(r"D:\BEA-Ghidra-Backups\2026-08-09-post-recovery")
D_PRE_BACKUP = D_ROOT / "unsetobjective-pre-live"
D_PRE_MANIFEST = D_PRE_BACKUP / "backup_manifest.json"
D_PRE_RESTORE = D_ROOT / "unsetobjective-pre-live-restore.ready.json"
D_POST_BACKUP = D_ROOT / "unsetobjective-post-live"
D_POST_MANIFEST = D_POST_BACKUP / "backup_manifest.json"
D_POST_RESTORE = D_ROOT / "unsetobjective-post-live-restore.ready.json"
ANALYZE_HEADLESS = Path(
    r"D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC\support\analyzeHeadless.bat"
)

SCHEMA = "bea.ghidra.mission-native-unsetobjective-promotion-authority.v1"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
PROGRAM_SHA = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
TOOL_STAMP = (38_732, "6cdba70a31491b1892fa6282fdfe689ba53fa1a1a3e75e16fdb95c3d09049eac")
INVENTORY_TOOL_STAMP = (
    23_963, "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197"
)
CAMPAIGN_STAMP = (27_833, "f83dbb6eddaa16deed5f2a2460d393dc4525a63ae243b6cac0c656056b69ab9a")
PROOF_STAMP = (16_268, "c6ae222d26b37863ae575b5af32ddf1a64d8660cb45adb60965610704ec37858")
PROOF_AUTHOR_STAMP = (
    52_888, "1d67823b54c465986b8b2e83ea9e1b278eef2e5dd91e509404399c21eba456fb"
)
CAMPAIGN_AUTHORITY_STAMP = (
    12_562, "72c22f029cd2f845c853dfbf2f5746062eed85ccc11d0291b531051c1e432360"
)
BOUNDARY_STAMP = (220_537, "2225b37a9e83347fa0f46f45fefd4ade45be6ba021f87e51ed299ff5ebd5340d")
SOURCE_MANIFEST_STAMP = (
    7_589, "df2c7ad5c2367801c6fa359ec4be7bcf65864306f87860f643f886d0517724bc"
)
SOURCE_AUTHORITY_STAMP = (
    6_782, "e64be82f360203fd2864450c5b3bd2d0a46441b9120eb79c8c423c3fe1ca0340"
)
SOURCE_RESTORE_STAMP = (
    6_007, "5a081e72c43c2152623a02319b16a75a79f2632546f63428192e123509fb75cf"
)
PRE_FUNCTIONS = (7_052_417, "f05259cda1c5d956098062220d6e3aada9bff4a61896a77c8fc153826691f9d0")
PRE_PROGRAM = (1_267, "6907443d213f6632c778a1c0e48f2070d5b268136b55e0e5f5c187f74dcbcf8f")
POST_FUNCTIONS = (0, "TO_BE_DERIVED")
POST_PROGRAM = (0, "TO_BE_DERIVED")
POST_COMMENT_BYTES = 0
POST_COMMENT_SHA256 = "TO_BE_DERIVED"
PHASE_TSV_STAMPS = {
    "dry": (633, "3d464e9d81025cdac4e9a19a5695e06e6d6ef3e8bdf5ad9449a378274fe2b8a6"),
    "apply": (0, "TO_BE_DERIVED"),
    "readback": (0, "TO_BE_DERIVED"),
}
TSV_HEADER = [
    "address", "mode", "state", "functionPresent", "name", "nameSource",
    "signatureSource", "signature", "bodyBytes", "bodyRangeSha256",
    "bodySha256", "instructionCount", "isThunk", "parameterCount",
    "stackParameterBytes", "commentBytes", "commentSha256", "functions",
    "instructions", "prefixSha256", "suffixSha256",
]
POST_SIGNATURE = (
    "void __thiscall IScript__UnsetObjective(void * this, undefined4 unusedVmSlot0, "
    "undefined4 unusedVmSlot1, undefined4 unusedVmSlot2)"
)


class ProofError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProofError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def raw_absolute(path: Path) -> Path:
    return Path(os.path.abspath(path))


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO).as_posix()
    except ValueError:
        return str(resolved)


def assert_plain_path(path: Path, label: str, *, directory: bool | None = None) -> Path:
    raw = raw_absolute(path)
    require(raw.exists(), f"{label} is absent: {raw}")
    for part in [*reversed(raw.parents), raw]:
        if not part.exists():
            continue
        stat_result = part.lstat()
        require(not part.is_symlink(), f"{label} traverses symlink: {part}")
        require(not (getattr(stat_result, "st_file_attributes", 0) & 0x400),
                f"{label} traverses reparse point: {part}")
    if directory is True:
        require(raw.is_dir(), f"{label} is not a directory")
    if directory is False:
        require(raw.is_file(), f"{label} is not a file")
        require(raw.stat().st_nlink == 1, f"{label} is not single-link")
    return raw.resolve()


def assert_plain_tree(root: Path, label: str) -> None:
    resolved = assert_plain_path(root, label, directory=True)
    for path in [resolved, *resolved.rglob("*")]:
        stat_result = path.lstat()
        require(not path.is_symlink(), f"{label} contains symlink: {path}")
        require(not (getattr(stat_result, "st_file_attributes", 0) & 0x400),
                f"{label} contains reparse point: {path}")
        if path.is_file():
            require(stat_result.st_nlink == 1, f"{label} contains linked file: {path}")


def stamp(path: Path) -> dict[str, Any]:
    resolved = assert_plain_path(path, f"evidence {path}", directory=False)
    return {"path": display_path(resolved), "bytes": resolved.stat().st_size,
            "sha256": sha256_file(resolved)}


def require_stamp(path: Path, expected: tuple[int, str], label: str) -> dict[str, Any]:
    actual = stamp(path)
    require((actual["bytes"], actual["sha256"]) == expected,
            f"{label} identity differs: {actual}")
    return actual


def load_json(path: Path) -> Any:
    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            require(key not in result, f"duplicate JSON key {key!r} at {path}")
            result[key] = value
        return result

    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    except Exception as exc:
        raise ProofError(f"invalid JSON at {path}: {exc}") from exc


def validate_proof_inputs() -> dict[str, Any]:
    proof = load_json(PROOF)
    require(set(proof.get("author", {})) == {"path", "bytes", "sha256"},
            "proof author stamp shape differs")
    author = REPO / proof["author"]["path"]
    require_stamp(author, PROOF_AUTHOR_STAMP, "UnsetObjective proof author")
    inputs = proof.get("inputs")
    require(isinstance(inputs, dict) and len(inputs) == 26, "proof input set differs")
    for key, row in inputs.items():
        require(isinstance(key, str) and isinstance(row, dict), "proof input row differs")
        require(set(row) == {"path", "bytes", "sha256"} and row.get("path") == key,
                f"proof input stamp shape differs: {key}")
        relative = PurePosixPath(key)
        require(not relative.is_absolute() and ".." not in relative.parts and
                str(relative) == key, f"proof input route differs: {key}")
        size, digest = row.get("bytes"), row.get("sha256")
        require(isinstance(size, int) and not isinstance(size, bool) and
                isinstance(digest, str) and re.fullmatch(r"[0-9a-f]{64}", digest),
                f"proof input identity differs: {key}")
        require_stamp(REPO / Path(*relative.parts), (size, digest), f"proof input {key}")
    return {"author": stamp(author), "inputCount": len(inputs)}


def parse_utc(value: Any, label: str) -> datetime:
    require(isinstance(value, str) and value.endswith("Z"), f"{label} is not UTC")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ProofError(f"{label} is malformed") from exc
    require(parsed.utcoffset() is not None and parsed.utcoffset().total_seconds() == 0,
            f"{label} is not zero-offset UTC")
    return parsed


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def project_fields(value: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value.get(key) for key in (
        "projectName", "fileCount", "totalBytes", "structurallyComplete", "files")}


def actual_project(root: Path) -> dict[str, Any]:
    assert_plain_tree(root, f"project {root}")
    rows: list[dict[str, Any]] = []
    total = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path == root / "backup_manifest.json":
            continue
        size = path.stat().st_size
        rows.append({"relative_path": path.relative_to(root).as_posix(),
                     "sha256": sha256_file(path), "size": size})
        total += size
    return {
        "projectName": "BEA", "fileCount": len(rows), "totalBytes": total,
        "structurallyComplete": any(row["relative_path"] == "BEA.gpr" for row in rows)
            and any(row["relative_path"].startswith("BEA.rep/") for row in rows),
        "files": rows,
    }


def zero_comparison(value: Mapping[str, Any], label: str) -> None:
    require(value.get("matches") is True, f"{label} comparison failed")
    for field in ("missingCount", "extraCount", "sizeDiffCount", "hashDiffCount"):
        require(value.get(field) == 0, f"{label} {field} is nonzero")
    for field in ("missing", "extra", "sizeDifferences", "hashDifferences"):
        require(value.get(field) == [], f"{label} {field} is nonempty")


def baseline_project() -> dict[str, Any]:
    require_stamp(SOURCE_MANIFEST, SOURCE_MANIFEST_STAMP, "SetPos POST manifest")
    receipt = load_json(SOURCE_MANIFEST)
    require(receipt.get("schemaVersion") == "onslaught-ghidra-project-backup.v2",
            "SetPos POST manifest schema differs")
    require(receipt.get("sourceStable") is True, "SetPos POST source was unstable")
    zero_comparison(receipt.get("copyComparison", {}), "SetPos POST")
    source = project_fields(receipt["source"])
    destination = project_fields(receipt["destination"])
    require(source == destination, "SetPos POST source/destination differ")
    require(destination["fileCount"] == 19 and destination["totalBytes"] == 186_485_637,
            "SetPos POST aggregate differs")
    require(actual_project(SOURCE_PRE) == destination,
            "SetPos POST backup differs from its manifest")
    return destination


def validate_copy(name: str, expected: Mapping[str, Any]) -> dict[str, Any]:
    root = LANE / "scratch" / name
    assert_plain_tree(root, f"scratch {name}")
    receipt_path = root / "backup_manifest.json"
    receipt = load_json(receipt_path)
    require(receipt.get("schemaVersion") == "onslaught-ghidra-project-backup.v2",
            f"{name} copy schema differs")
    require(receipt.get("sourceStable") is True, f"{name} source was unstable")
    zero_comparison(receipt.get("copyComparison", {}), f"{name} copy")
    require(project_fields(receipt["source"]) == expected, f"{name} source differs")
    require(project_fields(receipt["destination"]) == expected, f"{name} seed differs")
    return {"manifest": stamp(receipt_path), "project": display_path(root),
            "createdAtUtc": receipt["createdAtUtc"]}


def require_distinct_projects(roots: Sequence[Path]) -> None:
    resolved = [assert_plain_path(root, f"project root {root}", directory=True)
                for root in roots]
    require(len(set(resolved)) == len(resolved), "project roots are not distinct")
    identities: dict[tuple[int, int], Path] = {}
    for root in resolved:
        for path in root.rglob("*"):
            if not path.is_file() or path == root / "backup_manifest.json":
                continue
            result = path.stat()
            identity = (result.st_dev, result.st_ino)
            require(identity not in identities,
                    f"project file alias: {path} and {identities.get(identity)}")
            identities[identity] = path


def require_exact_files(root: Path, names: set[str], label: str) -> None:
    assert_plain_tree(root, label)
    actual = {path.relative_to(root).as_posix() for path in root.rglob("*")}
    require(actual == names, f"{label} file set differs: {sorted(actual)}")


def validate_phase_tsv(path: Path, phase: str) -> dict[str, str]:
    require_stamp(path, PHASE_TSV_STAMPS[phase], f"{phase} UnsetObjective TSV")
    header, rows = read_tsv(path)
    require(header == TSV_HEADER and len(rows) == 1, f"{phase} TSV shape differs")
    row = rows[0]
    post = phase in {"apply", "readback"}
    require(row["address"] == "0x00535ee0" and row["mode"] == phase,
            f"{phase} row identity differs")
    require(row["state"] == ("POST" if post else "PRE"), f"{phase} state differs")
    require(row["functionPresent"] == str(post).lower(), f"{phase} function state differs")
    require(row["name"] == ("IScript__UnsetObjective" if post else ""),
            f"{phase} name differs")
    require(row["signature"] == (POST_SIGNATURE if post else ""),
            f"{phase} signature differs")
    require(row["bodyBytes"] == "13" and row["instructionCount"] == "4",
            f"{phase} body counts differ")
    require(row["bodyRangeSha256"] ==
            "6c032733dc164b583a792a9d1b9fc951d07d9f8ec25c31591417b5dcf3b73ab1",
            f"{phase} body range differs")
    require(row["bodySha256"] ==
            "0ec7dfff6ad0dba017b45b0a9840f6b587b899e88aaedb29d1d0eabfb842b35f",
            f"{phase} body bytes differ")
    require(row["functions"] == ("8126" if post else "8125") and
            row["instructions"] == "549872", f"{phase} program counts differ")
    if post:
        require(row["nameSource"] == "USER_DEFINED" and
                row["signatureSource"] == "USER_DEFINED" and
                row["parameterCount"] == "4" and row["stackParameterBytes"] == "12" and
                row["commentBytes"] == str(POST_COMMENT_BYTES) and
                row["commentSha256"] == POST_COMMENT_SHA256,
                f"{phase} POST metadata differs")
    return row


def validate_run(label: str, run_name: str, phase: str, project: Path,
                 *, require_read_only: bool | None = None) -> dict[str, Any]:
    root = LANE / "runs" / run_name
    require_exact_files(
        root, {"headless.log", "unsetobjective.tsv", "unsetobjective.ready.json"}, label)
    tsv = root / "unsetobjective.tsv"
    ready_path = root / "unsetobjective.ready.json"
    log = root / "headless.log"
    validate_phase_tsv(tsv, phase)
    ready = load_json(ready_path)
    expected_keys = {
        "schema", "completedAtUtc", "mode", "state", "tool", "program", "evidence",
        "output", "mutation", "counts", "commitRequested",
        "nestedEndReturnedCommitted", "loadedStateVerified", "authorityBoundary",
        "limitations",
    }
    require(set(ready) == expected_keys, f"{label} READY shape differs")
    parse_utc(ready["completedAtUtc"], f"{label} completedAtUtc")
    require(ready["schema"] == "bea.ghidra.mission-native-unsetobjective-promotion.v1",
            f"{label} schema differs")
    require(ready["mode"] == phase and ready["state"] == ("PRE" if phase == "dry" else "POST"),
            f"{label} mode/state differs")
    require(ready["tool"]["path"] == str(TOOL.resolve()) and
            (ready["tool"]["bytes"], ready["tool"]["sha256"]) == TOOL_STAMP,
            f"{label} tool identity differs")
    expected_evidence = {
        "campaign": (CAMPAIGN, CAMPAIGN_STAMP), "proof": (PROOF, PROOF_STAMP),
        "authority": (CAMPAIGN_AUTHORITY, CAMPAIGN_AUTHORITY_STAMP),
        "listingManifest": (BOUNDARY, BOUNDARY_STAMP),
    }
    require(set(ready["evidence"]) == set(expected_evidence), f"{label} evidence shape differs")
    for key, (path, expected) in expected_evidence.items():
        assert_plain_path(path, f"{label} {key}", directory=False)
        value = ready["evidence"][key]
        require(value["path"] == str(path.resolve()) and
                (value["bytes"], value["sha256"]) == expected,
                f"{label} {key} differs")
    require(ready["output"]["path"] == str(tsv.resolve()) and
            (ready["output"]["bytes"], ready["output"]["sha256"]) ==
            PHASE_TSV_STAMPS[phase], f"{label} output differs")
    require(ready["mutation"]["entry"] == "0x00535ee0" and
            ready["mutation"]["name"] == "IScript__UnsetObjective" and
            ready["mutation"]["functionCreated"] is (phase != "dry") and
            all(ready["mutation"][key] == 0 for key in
                ("bytesChanged", "instructionsChanged", "dataUnitsChanged", "referencesChanged")),
            f"{label} mutation boundary differs")
    require(ready["counts"] == {
        "functions": 8125 if phase == "dry" else 8126,
        "instructions": 549872, "bodyBytes": 13, "bodyInstructions": 4,
        "leadingNopBytes": 3, "trailingNopBytes": 3,
    }, f"{label} counts differ")
    require(ready["commitRequested"] is (phase == "apply") and
            ready["nestedEndReturnedCommitted"] is False and
            ready["loadedStateVerified"] is (phase == "readback"),
            f"{label} transaction/readback flags differ")
    text = log.read_text(encoding="utf-8", errors="replace")
    marker = {
        "dry": "MISSION_UNSETOBJECTIVE_DRY_COMPLETE entry=0x00535ee0 mutations=0",
        "apply": "MISSION_UNSETOBJECTIVE_APPLY_COMPLETE entry=0x00535ee0 function_count=8126 reopen_verification_required=true",
        "readback": "MISSION_UNSETOBJECTIVE_READBACK_COMPLETE entry=0x00535ee0 function_count=8126 loaded_state_verified=true",
    }[phase]
    require(marker in text and "SCRIPT ERROR" not in text and "ERROR REPORT" not in text,
            f"{label} did not close cleanly")
    require(str(project.resolve()) + "\\BEA" in text, f"{label} opened wrong project")
    require(str(tsv.resolve()) in text and str(ready_path.resolve()) in text and
            f"'{phase}'" in text, f"{label} log does not bind outputs/mode")
    read_only = phase == "readback" if require_read_only is None else require_read_only
    if read_only:
        require("Processing read-only project file: /BEA.exe" in text,
                f"{label} was not read-only")
    else:
        require("Save succeeded for processed file: /BEA.exe" in text,
                f"{label} save did not complete")
    return {"tsv": stamp(tsv), "ready": stamp(ready_path), "log": stamp(log),
            "completedAtUtc": ready["completedAtUtc"]}


def parse_program(path: Path) -> dict[str, str]:
    rows = path.read_text(encoding="utf-8").splitlines()
    require(rows and rows[0] == "metric\tvalue", f"program header differs: {path}")
    result: dict[str, str] = {}
    for row in rows[1:]:
        key, value = row.split("\t", 1)
        require(key not in result, f"duplicate program metric: {key}")
        result[key] = value
    return result


def validate_function_delta(post_path: Path) -> None:
    pre_header, pre_rows = read_tsv(SOURCE_FUNCTIONS)
    post_header, post_rows = read_tsv(post_path)
    require(post_header == pre_header, "POST function inventory header differs")

    def indexed(rows: list[dict[str, str]], label: str) -> dict[str, dict[str, str]]:
        result: dict[str, dict[str, str]] = {}
        for row in rows:
            address = row.get("address", "")
            require(address not in result, f"duplicate {label} function address: {address}")
            result[address] = row
        return result

    pre = indexed(pre_rows, "PRE")
    post = indexed(post_rows, "POST")
    target = "0x00535ee0"
    require(set(post) == set(pre) | {target}, "POST function address set differs")
    for address, row in pre.items():
        require(post[address] == row, f"existing function row changed: {address}")
    created = post[target]
    empty_sha = hashlib.sha256(b"").hexdigest()
    expected = {
        "name": "IScript__UnsetObjective",
        "fqname": "IScript__UnsetObjective",
        "nameSource": "USER_DEFINED",
        "sigSource": "USER_DEFINED",
        "bodyBytes": "13",
        "bodyMin": target,
        "bodyMax": "0x00535eec",
        "bodyRanges": "1",
        "bodyDigest": "6c032733dc164b583a792a9d1b9fc951d07d9f8ec25c31591417b5dcf3b73ab1",
        "instrCount": "4",
        "paramCount": "4",
        "callingConv": "__thiscall",
        "returnType": "void",
        "varArgs": "false",
        "isThunk": "false",
        "thunkTarget": "",
        "isExternal": "false",
        "customStorage": "false",
        "inline": "false",
        "noReturn": "false",
        "paramSize": "12",
        "signature": POST_SIGNATURE,
        "commentPresent": "true",
        "commentLen": str(POST_COMMENT_BYTES),
        "commentSha256": POST_COMMENT_SHA256,
        "repeatableCommentPresent": "false",
        "repeatableCommentLen": "0",
        "repeatableCommentSha256": empty_sha,
        "tagCount": "0",
        "tags": "",
        "tagsSha256": empty_sha,
    }
    for field, value in expected.items():
        require(created.get(field) == value,
                f"created function {field} differs: {created.get(field)!r}")
    for field, length_field, digest_field in (
        ("name", "nameLen", "nameSha256"),
        ("fqname", "fqnameLen", "fqnameSha256"),
        ("signature", "signatureLen", "signatureSha256"),
    ):
        encoded = created[field].encode("utf-8")
        require(created[length_field] == str(len(encoded)) and
                created[digest_field] == hashlib.sha256(encoded).hexdigest(),
                f"created function {field} framing differs")


def validate_inventory(root_name: str, project: Path, state: str) -> dict[str, Any]:
    root = LANE / "runs" / root_name
    require_exact_files(root, {"headless.log", "functions.tsv", "program.tsv"}, root_name)
    functions = root / "functions.tsv"
    program = root / "program.tsv"
    expected_functions = POST_FUNCTIONS if state == "POST" else PRE_FUNCTIONS
    expected_program = POST_PROGRAM if state == "POST" else PRE_PROGRAM
    require_stamp(functions, expected_functions, f"{root_name} functions")
    require_stamp(program, expected_program, f"{root_name} program")
    metrics = parse_program(program)
    baseline = parse_program(SOURCE_PROGRAM)
    require(set(metrics) == set(baseline), f"{root_name} program metric set differs")
    require(metrics["programName"] == "BEA.exe" and metrics["executableSHA256"] == PROGRAM_SHA,
            f"{root_name} specimen differs")
    require(metrics["functions"] == ("8126" if state == "POST" else "8125") and
            metrics["instructions"] == "549872" and metrics["definedData"] == "48585" and
            metrics["references"] == "234357", f"{root_name} protected counts differ")
    if state == "POST":
        changed = {key for key in metrics if metrics.get(key) != baseline.get(key)}
        require(changed == {"functions", "symbolsUserDefined", "symbolsDefaultOther",
                            "comments", "commentsSha256"},
                f"{root_name} changed unrelated program metrics: {sorted(changed)}")
        require(metrics["symbolsUserDefined"] == "6006" and
                metrics["symbolsDefaultOther"] == "61692" and metrics["comments"] == "9101",
                f"{root_name} POST semantic delta differs")
        validate_function_delta(functions)
    else:
        require(metrics == baseline, f"{root_name} PRE program metrics differ")
    text = (root / "headless.log").read_text(encoding="utf-8", errors="replace")
    require(str(project.resolve()) + "\\BEA" in text and
            "Processing read-only project file: /BEA.exe" in text and
            f"INVENTORY_OK functions={'8126' if state == 'POST' else '8125'} " in text and
            "SCRIPT ERROR" not in text, f"{root_name} inventory log differs")
    return {"functions": stamp(functions), "program": stamp(program),
            "log": stamp(root / "headless.log")}


def normalize_ready(path: Path) -> dict[str, Any]:
    value = copy.deepcopy(load_json(path))
    value.pop("completedAtUtc")
    value["output"]["path"] = "<lane-output>"
    return value


def validate_adverse(kind: str, project_name: str, run_name: str,
                     inventory_name: str) -> dict[str, Any]:
    project = LANE / "scratch" / project_name
    root = LANE / "runs" / run_name
    require_exact_files(root, {"headless.log"}, kind)
    log = root / "headless.log"
    text = log.read_text(encoding="utf-8", errors="replace")
    common = [
        "MISSION_UNSETOBJECTIVE_PREFLIGHT_OK entry=0x00535ee0 body_bytes=13 instructions=4",
        f"MISSION_UNSETOBJECTIVE_MUTATION_TAINTED mode={kind}",
        "ERROR REPORT SCRIPT ERROR",
        str(project.resolve()) + "\\BEA",
    ]
    specific = {
        "probe-after-create": [
            "MISSION_UNSETOBJECTIVE_FORCED_AFTER_CREATE_FAILURE rollback_required=true",
            "recovery=RESTORE_VERIFIED_SCRATCH_BASE",
            "intentional Mission UnsetObjective after-create rollback probe",
        ],
        "probe-post-inner": [
            "MISSION_UNSETOBJECTIVE_COMPENSATING_PRE_RESTORE_COMPLETE entry=0x00535ee0",
            "MISSION_UNSETOBJECTIVE_FORCED_POST_INNER_FAILURE pre_restored=true",
            "recovery=COMPENSATING_PRE_RESTORE_VERIFIED",
            "intentional Mission UnsetObjective post-inner rollback probe",
        ],
    }[kind]
    for marker in common + specific:
        require(marker in text, f"{kind} lacks marker: {marker}")
    require(not (root / "unsetobjective.tsv").exists() and
            not (root / "unsetobjective.ready.json").exists(),
            f"{kind} published success artifacts")
    inventory = validate_inventory(inventory_name, project, "PRE")
    return {"project": display_path(project), "failureLog": stamp(log),
            "postFailurePre": inventory, "successArtifactsAbsent": True,
            "preStateRestoredExactly": True}


def validate_restore(
        expected: Mapping[str, Any], receipt_path: Path, source_root: Path,
        probe_parent: Path, expected_functions: int, label: str) -> dict[str, Any]:
    assert_plain_path(receipt_path, f"{label} receipt", directory=False)
    require(actual_project(source_root) == expected, f"{label} source bytes differ")
    receipt = load_json(receipt_path)
    require(receipt.get("schemaVersion") == "onslaught-ghidra-project-backup.v2",
            f"{label} schema differs")
    require(receipt.get("sourceStable") is True, f"{label} source was unstable")
    zero_comparison(receipt.get("copyComparison", {}), f"{label} copy")
    require(receipt.get("probeCopyDisposition") == "RETAINED_AT_VERIFICATION",
            f"{label} probe was not retained")
    probe_text = receipt.get("probeCopy", "")
    require(isinstance(probe_text, str) and ".." not in Path(probe_text).parts,
            f"{label} probe route is not lexical-canonical")
    probe = raw_absolute(Path(probe_text))
    require(str(probe) == probe_text, f"{label} probe route spelling differs")
    require(probe.parent.resolve() == probe_parent.resolve() and
            probe.name.startswith("BEA-open-probe-"), f"{label} probe path differs")
    require(actual_project(probe) == expected, f"{label} retained probe differs")
    readonly = receipt.get("readonlyOpen", {})
    require(readonly.get("opened") is True and readonly.get("contentStable") is True and
            readonly.get("exitCode") == 0, f"{label} read-only open failed")
    zero_comparison(readonly.get("postOpenComparison", {}), f"{label} post-open")
    expected_command = [
        str(ANALYZE_HEADLESS), str(probe), "BEA", "-process", "BEA.exe",
        "-readOnly", "-noanalysis", "-scriptPath", str((REPO / "tools").resolve()),
        "-postScript", OPEN_PROBE_TOOL.name, "BEA.exe", PROGRAM_MD5, PROGRAM_SHA,
    ]
    require(readonly.get("commandArgv") == expected_command,
            f"{label} read-only command differs")
    require(readonly.get("observedProgramName") == "BEA.exe" and
            readonly.get("observedProgramMd5") == PROGRAM_MD5 and
            readonly.get("observedProgramSha256") == PROGRAM_SHA and
            readonly.get("observedFunctionCount") == expected_functions,
            f"{label} observed program differs")
    log_value = readonly.get("probeLog", {})
    expected_log_name = receipt_path.stem + ".open-probe.log"
    require(log_value.get("path") == expected_log_name,
            f"{label} probe log route differs")
    log_path = receipt_path.parent / expected_log_name
    require(log_path.parent == receipt_path.parent, f"{label} probe log escaped receipt root")
    actual_log = stamp(log_path)
    require((log_value.get("bytes"), log_value.get("sha256")) ==
            (actual_log["bytes"], actual_log["sha256"]), f"{label} probe log differs")
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    require(str(probe) + "\\BEA" in log_text and
            "Processing read-only project file: /BEA.exe" in log_text and
            "SCRIPT ERROR" not in log_text, f"{label} probe log content differs")
    require(project_fields(receipt["source"]) == expected, f"{label} source differs")
    require(Path(receipt["source"].get("root", "")).resolve() == source_root.resolve(),
            f"{label} source route differs")
    return stamp(receipt_path)


def build_scratch(generated_at: str, *, require_current_live_pre: bool) -> dict[str, Any]:
    generated_time = parse_utc(generated_at, "scratch generatedAtUtc")
    require(generated_time <= datetime.now(timezone.utc), "scratch time is in future")
    inputs = {
        "tool": require_stamp(TOOL, TOOL_STAMP, "UnsetObjective Ghidra tool"),
        "inventoryTool": require_stamp(INVENTORY_TOOL, INVENTORY_TOOL_STAMP, "inventory tool"),
        "campaign": require_stamp(CAMPAIGN, CAMPAIGN_STAMP, "Generation 19 READY"),
        "proof": require_stamp(PROOF, PROOF_STAMP, "UnsetObjective proof"),
        "campaignAuthority": require_stamp(
            CAMPAIGN_AUTHORITY, CAMPAIGN_AUTHORITY_STAMP, "Generation 19 authority"),
        "listingManifest": require_stamp(
            BOUNDARY, BOUNDARY_STAMP, "UnsetObjective byte-complete listing"),
        "proofClosure": validate_proof_inputs(),
    }
    expected = baseline_project()
    predecessor = {
        "liveAuthority": require_stamp(
            SOURCE_AUTHORITY, SOURCE_AUTHORITY_STAMP, "SetPos live authority"),
        "postBackupManifest": require_stamp(
            SOURCE_MANIFEST, SOURCE_MANIFEST_STAMP, "SetPos POST manifest"),
        "postRestoreReceipt": require_stamp(
            SOURCE_RESTORE, SOURCE_RESTORE_STAMP, "SetPos POST restore"),
        "postFunctions": require_stamp(
            SOURCE_FUNCTIONS, PRE_FUNCTIONS, "SetPos POST function inventory"),
        "postProgram": require_stamp(
            SOURCE_PROGRAM, PRE_PROGRAM, "SetPos POST program inventory"),
        "exactProjectContinuity": True,
    }
    pre_backups = {
        "local": {
            "manifest": validate_backup(PRE_MANIFEST, expected, "C PRE live backup"),
            "restore": validate_restore(
                expected, PRE_RESTORE, PRE_BACKUP,
                LANE / "backups" / "pre-live-restore-drill",
                8349, "C PRE restore"),
        },
        "offVolume": {
            "manifest": validate_backup(D_PRE_MANIFEST, expected, "D PRE live backup"),
            "restore": validate_restore(
                expected, D_PRE_RESTORE, D_PRE_BACKUP,
                D_ROOT / "unsetobjective-pre-live-restore-drill",
                8349, "D PRE restore"),
        },
    }
    require(PRE_BACKUP.drive.lower() != D_PRE_BACKUP.drive.lower(),
            "PRE backups are not on distinct volumes")
    require(PRE_BACKUP.stat().st_dev != D_PRE_BACKUP.stat().st_dev,
            "PRE backup device identities are not distinct")
    if require_current_live_pre:
        require(actual_project(LIVE) == expected, "maintainer project drifted from exact PRE")
    names = ["replica-a", "replica-b", "probe-after-create", "probe-post-inner"]
    roots = [LANE / "scratch" / name for name in names]
    pre_probes = [Path(load_json(path)["probeCopy"])
                  for path in (PRE_RESTORE, D_PRE_RESTORE)]
    require_distinct_projects(
        [LIVE, SOURCE_PRE, PRE_BACKUP, D_PRE_BACKUP, *pre_probes, *roots])
    copies = {name: validate_copy(name, expected) for name in names}
    replicas: dict[str, Any] = {}
    evidence_times: list[datetime] = []
    for suffix, project_name in (("a", "replica-a"), ("b", "replica-b")):
        project = LANE / "scratch" / project_name
        dry = validate_run(f"replica {suffix} dry", f"replica-{suffix}-dry", "dry", project)
        apply = validate_run(f"replica {suffix} apply", f"replica-{suffix}-apply", "apply", project)
        readback = validate_run(
            f"replica {suffix} readback", f"replica-{suffix}-readback", "readback", project)
        inventory = validate_inventory(f"replica-{suffix}-inventory", project, "POST")
        copy_time = parse_utc(copies[project_name]["createdAtUtc"], f"replica {suffix} copy")
        dry_time = parse_utc(dry["completedAtUtc"], f"replica {suffix} dry")
        apply_time = parse_utc(apply["completedAtUtc"], f"replica {suffix} apply")
        readback_time = parse_utc(readback["completedAtUtc"], f"replica {suffix} readback")
        require(copy_time < dry_time < apply_time < readback_time,
                f"replica {suffix} chronology differs")
        require((LANE / "runs" / f"replica-{suffix}-inventory" /
                 "functions.tsv").stat().st_mtime_ns >
                (LANE / "runs" / f"replica-{suffix}-readback" /
                 "unsetobjective.ready.json").stat().st_mtime_ns,
                f"replica {suffix} inventory did not follow readback")
        evidence_times.append(readback_time)
        replicas[suffix] = {"project": display_path(project), "dry": dry, "apply": apply,
                            "readback": readback, "inventory": inventory}
    for phase in ("dry", "apply", "readback"):
        a = LANE / "runs" / f"replica-a-{phase}"
        b = LANE / "runs" / f"replica-b-{phase}"
        require((a / "unsetobjective.tsv").read_bytes() ==
                (b / "unsetobjective.tsv").read_bytes(),
                f"replica {phase} TSVs differ")
        require(normalize_ready(a / "unsetobjective.ready.json") ==
                normalize_ready(b / "unsetobjective.ready.json"),
                f"replica {phase} receipts differ beyond time/path")
    for artifact in ("functions.tsv", "program.tsv"):
        require((LANE / "runs" / "replica-a-inventory" / artifact).read_bytes() ==
                (LANE / "runs" / "replica-b-inventory" / artifact).read_bytes(),
                f"replica POST {artifact} differs")
    adverse = {
        "afterCreate": validate_adverse(
            "probe-after-create", "probe-after-create", "probe-after-create",
            "probe-after-create-post-inventory"),
        "postInner": validate_adverse(
            "probe-post-inner", "probe-post-inner", "probe-post-inner",
            "probe-post-inner-post-inventory"),
    }
    evidence_times.extend(datetime.fromtimestamp(
        (LANE / "runs" / name / "program.tsv").stat().st_mtime, timezone.utc)
        for name in ("probe-after-create-post-inventory",
                     "probe-post-inner-post-inventory"))
    require(max(evidence_times) < generated_time, "scratch authority predates evidence")
    return {
        "schema": SCHEMA, "phase": "SCRATCH_AUTHORITY", "verdict": "READY",
        "generatedAtUtc": generated_at,
        "claim": "ONE_MISSION_NATIVE_UNSETOBJECTIVE_FUNCTION_AUTHORIZED_FOR_ONE_LIVE_APPLY",
        "author": stamp(SCRIPT), "inputs": inputs, "predecessor": predecessor,
        "preBackups": pre_backups, "copies": copies, "replicas": replicas,
        "adverseControls": adverse,
        "delta": {
            "functionEntry": "0x00535ee0", "functionsAdded": 1,
            "name": "IScript__UnsetObjective", "signature": POST_SIGNATURE,
            "commentBytes": "TO_BE_DERIVED", "bodyBytes": 13, "bodyInstructions": 4,
            "leadingNopBytes": 3, "trailingNopBytes": 3,
            "bytesChanged": 0, "instructionsChanged": 0, "dataUnitsChanged": 0,
            "referencesChanged": 0,
        },
        "authorization": {
            "liveApplyAuthorized": True, "oneMutationProcess": True,
            "separateReadbackRequired": True, "postBackupAndRestoreRequired": True,
            "additionalClaimsAuthorized": False,
            "behavioralContractPromotionAuthorized": False,
        },
        "limitations": [
            "Only the scored boundary, shipped name, neutral ABI, and exact delegated call shape are promoted.",
            "The Generation 19 behavioral contract is not promoted because its runtime/refuter verdicts remain UNSCORED.",
            "The three callee-cleaned stack slots remain undefined4 with neutral names.",
            "Callee effects, HUD behavior, and full objective-system semantics remain open.",
            "No executable byte, instruction, data-unit, or reference mutation is authorized.",
        ],
    }


def validate_backup(
        manifest_path: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    receipt = load_json(manifest_path)
    require(receipt.get("schemaVersion") == "onslaught-ghidra-project-backup.v2",
            f"{label} schema differs")
    require(receipt.get("sourceStable") is True, f"{label} source was unstable")
    zero_comparison(receipt.get("copyComparison", {}), label)
    require(project_fields(receipt["source"]) == expected and
            project_fields(receipt["destination"]) == expected,
            f"{label} source/destination differ")
    require(actual_project(manifest_path.parent) == expected, f"{label} actual bytes differ")
    return stamp(manifest_path)


def build_live(generated_at: str) -> dict[str, Any]:
    generated_time = parse_utc(generated_at, "live generatedAtUtc")
    require(generated_time <= datetime.now(timezone.utc), "live time is in future")
    saved_scratch = load_json(SCRATCH_READY)
    scratch = build_scratch(saved_scratch["generatedAtUtc"], require_current_live_pre=False)
    require(saved_scratch == scratch, "scratch authority no longer verifies")
    baseline = baseline_project()
    pre_manifest = validate_backup(PRE_MANIFEST, baseline, "C PRE live backup")
    pre_restore = validate_restore(
        baseline, PRE_RESTORE, PRE_BACKUP,
        LANE / "backups" / "pre-live-restore-drill", 8349, "C PRE restore")
    d_pre_manifest = validate_backup(D_PRE_MANIFEST, baseline, "D PRE live backup")
    d_pre_restore = validate_restore(
        baseline, D_PRE_RESTORE, D_PRE_BACKUP,
        D_ROOT / "unsetobjective-pre-live-restore-drill", 8349, "D PRE restore")
    live_dry = validate_run(
        "live immediate PRE", "live-preapply-dry", "dry", LIVE, require_read_only=True)
    live_pre_inventory = validate_inventory("live-preapply-inventory", LIVE, "PRE")
    live_apply = validate_run("live apply", "live-apply", "apply", LIVE)
    live_readback = validate_run("live readback", "live-readback", "readback", LIVE)
    live_inventory = validate_inventory("live-inventory", LIVE, "POST")
    for phase in ("apply", "readback"):
        live = LANE / "runs" / f"live-{phase}"
        scratch_root = LANE / "runs" / f"replica-a-{phase}"
        require((live / "unsetobjective.tsv").read_bytes() ==
                (scratch_root / "unsetobjective.tsv").read_bytes(),
                f"live {phase} differs from scratch")
        require(normalize_ready(live / "unsetobjective.ready.json") ==
                normalize_ready(scratch_root / "unsetobjective.ready.json"),
                f"live {phase} receipt differs beyond time/path")
    for artifact in ("functions.tsv", "program.tsv"):
        require((LANE / "runs" / "live-inventory" / artifact).read_bytes() ==
                (LANE / "runs" / "replica-a-inventory" / artifact).read_bytes(),
                f"live POST {artifact} differs from scratch")
    post_project = actual_project(LIVE)
    post_manifest = validate_backup(POST_MANIFEST, post_project, "C POST live backup")
    post_restore = validate_restore(
        post_project, POST_RESTORE, POST_BACKUP,
        LANE / "backups" / "post-live-restore-drill", 8350, "C POST restore")
    d_post_manifest = validate_backup(D_POST_MANIFEST, post_project, "D POST live backup")
    d_post_restore = validate_restore(
        post_project, D_POST_RESTORE, D_POST_BACKUP,
        D_ROOT / "unsetobjective-post-live-restore-drill", 8350, "D POST restore")
    all_probes = [Path(load_json(path)["probeCopy"]) for path in
                  (PRE_RESTORE, D_PRE_RESTORE, POST_RESTORE, D_POST_RESTORE)]
    require_distinct_projects(
        [LIVE, PRE_BACKUP, D_PRE_BACKUP, POST_BACKUP, D_POST_BACKUP, *all_probes])
    require(PRE_BACKUP.stat().st_dev == POST_BACKUP.stat().st_dev and
            D_PRE_BACKUP.stat().st_dev == D_POST_BACKUP.stat().st_dev and
            PRE_BACKUP.stat().st_dev != D_PRE_BACKUP.stat().st_dev,
            "C/D backup device identities differ")
    scratch_time = parse_utc(saved_scratch["generatedAtUtc"], "scratch time")
    pre_backup_time = parse_utc(load_json(PRE_MANIFEST)["createdAtUtc"], "PRE backup time")
    pre_restore_time = parse_utc(load_json(PRE_RESTORE)["verifiedAtUtc"], "PRE restore time")
    d_pre_backup_time = parse_utc(
        load_json(D_PRE_MANIFEST)["createdAtUtc"], "D PRE backup time")
    d_pre_restore_time = parse_utc(
        load_json(D_PRE_RESTORE)["verifiedAtUtc"], "D PRE restore time")
    dry_time = parse_utc(live_dry["completedAtUtc"], "live PRE dry time")
    apply_time = parse_utc(live_apply["completedAtUtc"], "live apply time")
    readback_time = parse_utc(live_readback["completedAtUtc"], "live readback time")
    post_backup_time = parse_utc(load_json(POST_MANIFEST)["createdAtUtc"], "POST backup time")
    post_restore_time = parse_utc(load_json(POST_RESTORE)["verifiedAtUtc"], "POST restore time")
    d_post_backup_time = parse_utc(
        load_json(D_POST_MANIFEST)["createdAtUtc"], "D POST backup time")
    d_post_restore_time = parse_utc(
        load_json(D_POST_RESTORE)["verifiedAtUtc"], "D POST restore time")
    require(pre_backup_time < pre_restore_time and
            d_pre_backup_time < d_pre_restore_time and
            max(scratch_time, pre_restore_time, d_pre_restore_time) < dry_time <
            apply_time < readback_time < post_backup_time < post_restore_time <
            d_post_backup_time < d_post_restore_time < generated_time,
            "scratch/backup/live chronology differs")
    require(actual_project(LIVE) == post_project,
            "maintainer project drifted after POST backup validation")
    return {
        "schema": SCHEMA, "phase": "LIVE_PROMOTED", "verdict": "READY",
        "generatedAtUtc": generated_at,
        "claim": "MISSION_NATIVE_UNSETOBJECTIVE_PROMOTED_AND_SEPARATELY_READ_BACK",
        "author": stamp(SCRIPT), "tool": stamp(TOOL),
        "scratchAuthority": stamp(SCRATCH_READY),
        "live": {
            "project": str(LIVE.resolve()), "preBackupManifest": pre_manifest,
            "preRestoreReceipt": pre_restore, "offVolumePreBackupManifest": d_pre_manifest,
            "offVolumePreRestoreReceipt": d_pre_restore, "immediatePreDry": live_dry,
            "immediatePreInventory": live_pre_inventory, "apply": live_apply,
            "readback": live_readback, "postInventory": live_inventory,
            "postBackupManifest": post_manifest, "postRestoreReceipt": post_restore,
            "offVolumePostBackupManifest": d_post_manifest,
            "offVolumePostRestoreReceipt": d_post_restore,
        },
        "result": {
            "functionEntry": "0x00535ee0", "functionName": "IScript__UnsetObjective",
            "functionsAdded": 1, "bodyBytes": 13, "bodyInstructions": 4,
            "separateReadbackPassed": True, "recoverablePreBackupPassed": True,
            "recoverablePostBackupPassed": True, "offVolumePreAndPostPassed": True,
            "bytesChanged": 0,
            "instructionsChanged": 0, "dataUnitsChanged": 0, "referencesChanged": 0,
        },
        "limitations": scratch["limitations"],
    }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def publish(path: Path, payload: Mapping[str, Any]) -> None:
    require(not path.exists(), f"refusing to overwrite receipt: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    with tempfile.NamedTemporaryFile(
            prefix=f".{path.name}.", suffix=".partial", dir=path.parent,
            delete=False) as stream:
        partial = Path(stream.name)
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        require(stamp(SCRIPT) == AUTHOR_START, "authority author changed during execution")
        require(not path.exists(), f"authority receipt appeared during publication: {path}")
        os.link(partial, path)
        partial.unlink()
    finally:
        partial.unlink(missing_ok=True)


def verify_saved(path: Path, builder: Callable[[str], dict[str, Any]]) -> dict[str, Any]:
    saved = load_json(path)
    expected = builder(saved["generatedAtUtc"])
    require(saved == expected, f"saved receipt differs: {path}")
    return stamp(path)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=(
        "seal-scratch", "verify-scratch", "seal-live", "verify-live"))
    args = parser.parse_args(argv)
    if args.command == "seal-scratch":
        payload = build_scratch(utc_now(), require_current_live_pre=True)
        require(payload == build_scratch(
            payload["generatedAtUtc"], require_current_live_pre=True),
            "scratch evidence changed before publication")
        publish(SCRATCH_READY, payload)
        result = verify_saved(
            SCRATCH_READY, lambda value: build_scratch(value, require_current_live_pre=True))
        print(f"MISSION_UNSETOBJECTIVE_SCRATCH_AUTHORITY_READY sha256={result['sha256']}")
    elif args.command == "verify-scratch":
        result = verify_saved(
            SCRATCH_READY, lambda value: build_scratch(value, require_current_live_pre=False))
        print(f"MISSION_UNSETOBJECTIVE_SCRATCH_AUTHORITY_VERIFIED sha256={result['sha256']}")
    elif args.command == "seal-live":
        payload = build_live(utc_now())
        require(payload == build_live(payload["generatedAtUtc"]),
                "live evidence changed before publication")
        publish(LIVE_READY, payload)
        result = verify_saved(LIVE_READY, build_live)
        print(f"MISSION_UNSETOBJECTIVE_LIVE_PROMOTION_READY sha256={result['sha256']}")
    else:
        result = verify_saved(LIVE_READY, build_live)
        print(f"MISSION_UNSETOBJECTIVE_LIVE_PROMOTION_VERIFIED sha256={result['sha256']}")
    return 0


AUTHOR_START = stamp(SCRIPT)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProofError as exc:
        print(f"MISSION_UNSETOBJECTIVE_PROMOTION_REFUSED {exc}")
        raise SystemExit(10)
