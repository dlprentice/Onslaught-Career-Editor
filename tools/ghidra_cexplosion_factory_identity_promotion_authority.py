#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Seal the isolated 0x0050ff10 CExplosion-factory scratch ceremony.

This owner never opens or mutates Ghidra.  It accepts only two independently
copied positive replicas, separate-process POST readbacks, two fail-closed
rollback/compensation controls, a recoverable PRE backup/open probe, and the
exact one-row metadata delta authorized by the immutable promotion manifest.
It deliberately does not authorize or perform a live-project write.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


REPO = Path(__file__).resolve().parent.parent
SCRIPT = Path(__file__).resolve()
LANE = REPO / "local-lab/ghidra-cexplosion-identity-scratch-20260813-v7"
BASELINE = LANE / "baseline"
INSPECTION = LANE / "inspection-v1"
PRE_FUNCTIONS = INSPECTION / "functions.tsv"
PRE_PROGRAM = INSPECTION / "program.tsv"
MANIFEST = (
    REPO / "reverse-engineering/binary-analysis/"
    "cexplosion-factory-identity-promotion-2026-08-13.tsv"
)
OWNER = MANIFEST.with_suffix(".md")
REPROOF = (
    REPO / "local-lab/ghidra-cexplosion-identity-scratch-20260813-v7/"
    "reproof-v7/reproof.ready.json"
)
TOOL = REPO / "tools/GhidraApplyCExplosionFactoryIdentity.java"
INSPECTOR = REPO / "tools/GhidraInspectCExplosionFactoryIdentity.java"
REPROOF_TOOL = REPO / "tools/re_cexplosion_factory_identity_reproof.py"
INVENTORY_TOOL = REPO / "tools/ExportFullFunctionInventory.java"
BACKUP_TOOL = REPO / "tools/ghidra_project_backup.py"
OPEN_PROBE = REPO / "tools/GhidraProjectOpenProbe.java"
ANALYZE_HEADLESS = Path(
    r"D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC\support\analyzeHeadless.bat"
)
APPLICATION_PROPERTIES = ANALYZE_HEADLESS.parent.parent / "Ghidra/application.properties"
SCRATCH_READY = LANE / "scratch-authority.ready.json"
EXTERNAL_PROBE_ROOT = REPO.parent / "bea-cexplosion-v7-external-path-probe"

SCHEMA = "bea.ghidra.cexplosion-factory-identity-scratch-authority.v1"
TOOL_SCHEMA = "bea.ghidra.cexplosion-factory-identity.v1"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
PROGRAM_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
MEMORY_SHA256 = "5398f750f1ffb59873a6ec7e1750b51d11b5b844a8fda8d4e43649b5b9e5089d"
FUNCTION_COUNT = 8_170
OPEN_FUNCTION_COUNT = 8_394
INSTRUCTION_COUNT = 549_872
TARGET = "0x0050ff10"

STAMPS = {
    OWNER: (6_950, "059e2a9a1a18b6fcf301238764e9cedc75e69fc057e7d16cb40c5f3fe0f57e31"),
    MANIFEST: (1_474, "4eb65da2e50c31dc6151c270808c2bdf83b2cea0b70f1a3ab60173ec55fbc1e8"),
    REPROOF: (4_241, "fe1bfd62f94694a27c80383647f65952c0a9fbc0b85385a43c4543c20fe3db89"),
    TOOL: (39_751, "77ce5000c240673a25716f8ce5a42aa12fc7154d2362d7894893704b631c73d0"),
    INSPECTOR: (17_658, "8deb289dca518aa34a6219e95481c79cf4052a6a0a5aec27af6c4bb6f0b27655"),
    REPROOF_TOOL: (20_005, "54c6e6b0bc99923aff951cd4598a2f4c2e537e9dbbfdd8d969b10ffccea8d4c4"),
    INVENTORY_TOOL: (23_963, "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197"),
    BACKUP_TOOL: (27_502, "0f426982916f0aab982efe54664342a5d34607c2f89707159ecf6c07e205ad58"),
    OPEN_PROBE: (3_452, "fab2f701dfefe8604c1718d007dbe0ad59d330a9b3ec081ef2f2fe253b441fab"),
    PRE_FUNCTIONS: (7_086_689, "da9f20a5ae3de150546e5b103bd9914e1a4ec7492bbafe5d35c4cc79b46d4756"),
    PRE_PROGRAM: (1_267, "c29aa646da238babd81b2bd1206e3c0d6f853d74f2aca237bbb008c64be52f87"),
    ANALYZE_HEADLESS: (2_930, "dd7b9d17d32ed70a71df82a43a21cdaed6c4ce67064e30f8642c149f81c2ae07"),
    APPLICATION_PROPERTIES: (659, "80890f309379ef60ecbb376a95448bd79e874145544ffcfabb5ba1835ac8a2cf"),
}

ALLOWED_FUNCTION_COLUMNS = {
    "name", "nameLen", "nameSha256", "fqname", "fqnameLen", "fqnameSha256",
    "signature", "signatureLen", "signatureSha256", "commentLen", "commentSha256",
    "tagCount", "tagsSha256", "tags",
}


class AuthorityError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise AuthorityError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_text(value: str) -> str:
    return sha256_bytes(value.encode("utf-8"))


def inventory_sorted_digest(values: list[str]) -> str:
    digest = hashlib.sha256()
    for value in sorted(values):
        raw = value.encode("utf-8")
        digest.update(len(raw).to_bytes(4, "big"))
        digest.update(raw)
    return digest.hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO).as_posix()
    except ValueError:
        return str(resolved)


def require_repo_path_claim(value: Any, expected: Path, label: str,
                            *, allow_absolute_legacy: bool = False) -> str:
    require(isinstance(value, str) and value, f"{label} path is absent")
    expected_relative = rel(expected)
    require(not Path(expected_relative).is_absolute(),
            f"{label} expected path is outside repository: {expected}")
    normalized = value.replace("\\", "/")
    if Path(value).is_absolute():
        require(allow_absolute_legacy and
                normalized.casefold().endswith("/" + expected_relative.casefold()),
                f"{label} absolute path is not a recognized historical repo path")
    else:
        require(normalized == expected_relative,
                f"{label} repo-relative path differs: {normalized}")
    return expected_relative


def require_repo_descendant_claim(value: Any, parent: Path, label: str,
                                  *, allow_absolute_legacy: bool = False
                                  ) -> tuple[str, Path]:
    require(isinstance(value, str) and value, f"{label} path is absent")
    parent_relative = rel(parent).rstrip("/")
    normalized = value.replace("\\", "/")
    if Path(value).is_absolute():
        marker = "/" + parent_relative + "/"
        offset = normalized.casefold().rfind(marker.casefold())
        require(allow_absolute_legacy and offset >= 0,
                f"{label} absolute path is not a recognized historical repo path")
        normalized = normalized[offset + 1:]
    require(normalized.startswith(parent_relative + "/"),
            f"{label} is not below expected repository directory")
    resolved = (REPO / normalized).resolve()
    try:
        resolved.relative_to(parent.resolve())
    except ValueError as exc:
        raise AuthorityError(f"{label} escapes expected repository directory") from exc
    return normalized, resolved


def stamp(path: Path) -> dict[str, Any]:
    path = path.resolve()
    require(path.is_file(), f"required file is absent: {path}")
    stat = path.stat()
    require(not path.is_symlink(), f"file is a symlink: {path}")
    require(not (getattr(stat, "st_file_attributes", 0) & 0x400),
            f"file is a reparse point: {path}")
    require(stat.st_nlink == 1, f"file is not single-link: {path}")
    return {"path": rel(path), "bytes": stat.st_size, "sha256": sha256_file(path)}


def require_stamp(path: Path) -> dict[str, Any]:
    actual = stamp(path)
    require((actual["bytes"], actual["sha256"]) == STAMPS[path],
            f"immutable input differs: {actual}")
    return actual


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise AuthorityError(f"invalid JSON at {path}: {exc}") from exc


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def parse_utc(value: Any, label: str) -> None:
    require(isinstance(value, str) and value.endswith("Z"), f"{label} is not UTC")
    require("T" in value, f"{label} is malformed")


def manifest_row() -> dict[str, str]:
    rows = read_tsv(MANIFEST)
    require(len(rows) == 1 and rows[0].get("address") == TARGET,
            "promotion manifest is not the exact one-row target")
    row = rows[0]
    require(row["reproofReadyBytes"] == str(STAMPS[REPROOF][0]) and
            row["reproofReadySha256"] == STAMPS[REPROOF][1],
            "manifest reproof binding differs")
    return row


def project_fields(value: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value.get(key) for key in
            ("projectName", "fileCount", "totalBytes", "structurallyComplete", "files")}


def plain_project(root: Path) -> dict[str, Any]:
    root = Path(os.path.abspath(root))
    require(root.is_dir(), f"project root is absent: {root}")
    files: list[dict[str, Any]] = []
    total = 0
    for path in [root, *root.rglob("*")]:
        stat = path.lstat()
        require(not path.is_symlink(), f"project contains symlink: {path}")
        require(not (getattr(stat, "st_file_attributes", 0) & 0x400),
                f"project contains reparse point: {path}")
        if not path.is_file() or path.name == "backup_manifest.json":
            continue
        relative = path.relative_to(root).as_posix()
        if relative != "BEA.gpr" and not relative.startswith("BEA.rep/"):
            continue
        require(stat.st_nlink == 1, f"project contains linked file: {path}")
        files.append({"relative_path": relative, "sha256": sha256_file(path),
                      "size": stat.st_size})
        total += stat.st_size
    files.sort(key=lambda row: row["relative_path"])
    return {"projectName": "BEA", "fileCount": len(files), "totalBytes": total,
            "structurallyComplete": any(row["relative_path"] == "BEA.gpr" for row in files)
            and any(row["relative_path"].startswith("BEA.rep/") for row in files),
            "files": files}


def baseline_project() -> tuple[dict[str, Any], dict[str, Any]]:
    path = BASELINE / "backup_manifest.json"
    value = load_json(path)
    require(value.get("schemaVersion") == "onslaught-ghidra-project-backup.v2" and
            value.get("sourceStable") is True and
            value.get("copyComparison", {}).get("matches") is True,
            "baseline backup receipt is not a stable exact copy")
    source = project_fields(value.get("source", {}))
    destination = project_fields(value.get("destination", {}))
    require(source == destination == plain_project(BASELINE),
            "baseline project bytes differ from its backup receipt")
    require(destination["fileCount"] == 19 and destination["totalBytes"] == 186_665_861,
            "baseline project census differs")
    return destination, stamp(path)


def validate_initial_copy(root: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    path = root / "backup_manifest.json"
    value = load_json(path)
    require(value.get("schemaVersion") == "onslaught-ghidra-project-backup.v2" and
            value.get("sourceStable") is True and
            value.get("copyComparison", {}).get("matches") is True,
            f"{label} initial copy is not exact")
    require(project_fields(value.get("source", {})) == expected and
            project_fields(value.get("destination", {})) == expected,
            f"{label} initial copy differs from baseline")
    return stamp(path)


def validate_restore(path: Path, expected: Mapping[str, Any]) -> dict[str, Any]:
    value = load_json(path)
    require(value.get("schemaVersion") == "onslaught-ghidra-project-backup.v2" and
            value.get("sourceStable") is True and
            value.get("copyComparison", {}).get("matches") is True,
            "baseline restore copy differs")
    require(project_fields(value.get("source", {})) == expected,
            "baseline restore source differs")
    opened = value.get("readonlyOpen", {})
    require(opened.get("opened") is True and opened.get("contentStable") is True and
            opened.get("exitCode") == 0 and
            opened.get("postOpenComparison", {}).get("matches") is True,
            "baseline read-only open verification failed")
    require(opened.get("observedProgramMd5") == PROGRAM_MD5 and
            opened.get("observedProgramSha256") == PROGRAM_SHA256 and
            opened.get("observedFunctionCount") == OPEN_FUNCTION_COUNT,
            "baseline read-only open identity differs")
    normalized_probe, probe_copy = require_repo_descendant_claim(
        value.get("probeCopy"), LANE / "restore-probe",
        "baseline restore probeCopy", allow_absolute_legacy=True)
    require(project_fields(plain_project(probe_copy)) == expected,
            "retained restore probe bytes differ from baseline")
    actual_argv = opened.get("commandArgv")
    require(isinstance(actual_argv, list) and len(actual_argv) == 14,
            "baseline restore command shape differs")
    require(actual_argv[0] == str(ANALYZE_HEADLESS) and
            actual_argv[2:8] == ["BEA", "-process", "BEA.exe", "-readOnly",
                                  "-noanalysis", "-scriptPath"] and
            actual_argv[9:] == ["-postScript", OPEN_PROBE.name, "BEA.exe",
                                PROGRAM_MD5, PROGRAM_SHA256],
            "baseline restore command differs")
    normalized_script_path = require_repo_path_claim(
        actual_argv[8], REPO / "tools", "baseline restore scriptPath",
        allow_absolute_legacy=True)
    require_repo_path_claim(actual_argv[1], probe_copy,
                            "baseline restore command probeCopy",
                            allow_absolute_legacy=True)
    normalized_argv = list(actual_argv)
    normalized_argv[1] = normalized_probe
    normalized_argv[8] = normalized_script_path
    claim = opened.get("probeLog", {})
    log = path.with_name(str(claim.get("path", "")))
    actual = stamp(log)
    require((claim.get("bytes"), claim.get("sha256")) ==
            (actual["bytes"], actual["sha256"]), "restore log binding differs")
    return {"receipt": stamp(path), "log": actual, "retainedProbeMatches": True,
            "probeCopy": normalized_probe, "commandArgv": normalized_argv}


def expected_target(state: str) -> dict[str, str]:
    row = manifest_row()
    prefix = "pre" if state == "PRE" else "post"
    return {
        "address": TARGET,
        "state": state,
        "name": row[prefix + "Name"],
        "nameSource": "USER_DEFINED",
        "signatureSource": "USER_DEFINED",
        "signature": row[prefix + "Signature"],
        "parameterName": row[prefix + "ParameterName"],
        "parameterType": row["parameterType"],
        "parameterStorage": row["parameterStorage"],
        "parameterSource": row[prefix + "ParameterSource"],
        "callingConvention": row["callingConvention"],
        "returnType": row["returnType"],
        "returnStorage": row["returnStorage"],
        "bodyRanges": row["bodyRanges"],
        "bodyBytes": row["bodyBytes"],
        "bodyRangeSha256": row["bodyRangeSha256"],
        "bodyBytesSha256": row["bodyBytesSha256"],
        "instructionCount": row["instructionCount"],
        "commentBytes": row[prefix + "CommentBytes"],
        "commentSha256": row[prefix + "CommentSha256"],
        "tags": row[prefix + "Tags"],
        "tagsSha256": sha256_text(row[prefix + "Tags"]),
    }


def validate_target_tsv(path: Path, mode: str, state: str) -> dict[str, Any]:
    rows = read_tsv(path)
    require(len(rows) == 1, f"{mode} target output is not one row")
    expected = expected_target(state)
    expected["mode"] = mode
    actual = rows[0]
    require(set(actual) == set(expected), f"{mode} target columns differ")
    for key, value in expected.items():
        require(actual.get(key) == value, f"{mode} target {key} differs")
    return stamp(path)


def validate_ready(path: Path, mode: str, state: str, output: Path) -> dict[str, Any]:
    value = load_json(path)
    require(value.get("schema") == TOOL_SCHEMA, f"{mode} receipt schema differs")
    parse_utc(value.get("completedAtUtc"), f"{mode} completedAtUtc")
    require(value.get("mode") == mode and value.get("state") == state,
            f"{mode} receipt mode/state differs")
    for key, owner in (("tool", TOOL), ("owner", OWNER), ("manifest", MANIFEST),
                       ("reproof", REPROOF)):
        claim = value.get(key, {})
        require_repo_path_claim(claim.get("path"), owner, f"{mode} {key}")
        require((claim.get("bytes"), claim.get("sha256")) == STAMPS[owner],
                f"{mode} {key} binding differs")
    program = value.get("program", {})
    require(program == {"name": "BEA.exe", "md5": PROGRAM_MD5,
                        "sha256": PROGRAM_SHA256, "functions": FUNCTION_COUNT,
                        "instructions": INSTRUCTION_COUNT,
                        "memorySha256": MEMORY_SHA256},
            f"{mode} program envelope differs")
    target = value.get("target", {})
    require(target == {"address": TARGET, "bodyBytes": 152,
                       "bodySha256": manifest_row()["bodyBytesSha256"],
                       "directCallers": 24, "externalInteriorReferences": 0,
                       "parameterSource": manifest_row()[
                           ("pre" if state == "PRE" else "post") + "ParameterSource"
                       ]},
            f"{mode} target envelope differs")
    output_claim = value.get("output", {})
    output_stamp = stamp(output)
    require_repo_path_claim(output_claim.get("path"), output, f"{mode} output")
    require((output_claim.get("bytes"), output_claim.get("sha256")) ==
            (output_stamp["bytes"], output_stamp["sha256"]),
            f"{mode} output binding differs")
    changed = 1 if mode == "apply" else 0
    require(value.get("mutation") == {
        "namesChanged": changed, "parameterNamesChanged": changed,
        "parameterSourcesChanged": 0,
        "commentsChanged": changed, "tagSetsChanged": changed,
        "boundariesChanged": 0, "bytesChanged": 0, "instructionsChanged": 0,
        "dataUnitsChanged": 0, "referencesChanged": 0,
    }, f"{mode} mutation accounting differs")
    require(value.get("commitRequested") is (mode == "apply") and
            value.get("nestedEndReturnedCommitted") is False and
            value.get("loadedStateVerified") is (mode == "readback") and
            value.get("runtimeSemanticsAuthorized") is False and
            value.get("rebuildReadyAuthorized") is False and
            value.get("authorityBoundary") ==
            "scratch_only_until_sealed_and_fresh_live_pre_backup",
            f"{mode} authority boundary differs")
    return stamp(path)


def validate_run(name: str, mode: str, state: str, marker: str,
                 *, inventory: bool = False) -> dict[str, Any]:
    root = LANE / "runs" / name
    log = root / "ghidra.log"
    text = log.read_text(encoding="utf-8", errors="replace")
    require(marker in text and "REPORT SCRIPT ERROR" not in text,
            f"{name} did not complete cleanly")
    if mode == "apply":
        require("REPORT: Processing project file: /BEA.exe" in text and
                "REPORT: Save succeeded for processed file: /BEA.exe" in text,
                f"{name} was not the expected mutable/save process")
    else:
        require("REPORT: Processing read-only project file: /BEA.exe" in text,
                f"{name} was not read-only")
    target = root / "target.tsv"
    result = {
        "target": validate_target_tsv(target, mode, state),
        "ready": validate_ready(root / "target.ready.json", mode, state, target),
        "log": stamp(log),
    }
    if inventory:
        require("INVENTORY_OK functions=8170 instructions=549872" in text,
                f"{name} full inventory did not complete")
        result["functions"] = stamp(root / "functions.tsv")
        result["program"] = stamp(root / "program.tsv")
    return result


def indexed_rows(path: Path) -> dict[str, dict[str, str]]:
    rows = read_tsv(path)
    result = {row["address"]: row for row in rows}
    require(len(rows) == len(result), f"duplicate function address in {path}")
    return result


def compare_inventories(post_path: Path, label: str) -> dict[str, Any]:
    pre = indexed_rows(PRE_FUNCTIONS)
    post = indexed_rows(post_path)
    require(len(pre) == len(post) == FUNCTION_COUNT and pre.keys() == post.keys(),
            f"{label} function address census differs")
    changed_addresses = [address for address in pre if pre[address] != post[address]]
    require(changed_addresses == [TARGET], f"{label} changed function rows differ")
    before, after = pre[TARGET], post[TARGET]
    changed_columns = {key for key in before if before[key] != after[key]}
    require(changed_columns == ALLOWED_FUNCTION_COLUMNS,
            f"{label} changed target columns differ: {sorted(changed_columns)}")
    row = manifest_row()
    post_name, post_signature, post_tags = (
        row["postName"], row["postSignature"], row["postTags"])
    expected_changes = {
        "name": post_name, "nameLen": str(len(post_name)),
        "nameSha256": sha256_text(post_name), "fqname": post_name,
        "fqnameLen": str(len(post_name)), "fqnameSha256": sha256_text(post_name),
        "signature": post_signature, "signatureLen": str(len(post_signature)),
        "signatureSha256": sha256_text(post_signature),
        "commentLen": row["postCommentBytes"],
        "commentSha256": row["postCommentSha256"],
        "tagCount": str(len(post_tags.split(","))),
        "tagsSha256": inventory_sorted_digest(post_tags.split(",")), "tags": post_tags,
    }
    require(all(after[key] == value for key, value in expected_changes.items()),
            f"{label} target POST values differ")
    require(all(before[key] == after[key] for key in before if key not in changed_columns),
            f"{label} target invariant columns differ")
    return {"functionRows": FUNCTION_COUNT, "changedAddresses": changed_addresses,
            "changedColumns": sorted(changed_columns),
            "nonTargetRowsUnchanged": FUNCTION_COUNT - 1}


def compare_programs(post_path: Path, label: str) -> dict[str, Any]:
    pre_rows, post_rows = read_tsv(PRE_PROGRAM), read_tsv(post_path)
    require(len(pre_rows) == len(post_rows), f"{label} program metric count differs")
    pre = {row["metric"]: row["value"] for row in pre_rows}
    post = {row["metric"]: row["value"] for row in post_rows}
    require(len(pre) == len(pre_rows) and len(post) == len(post_rows) and
            pre.keys() == post.keys(), f"{label} program metric keys differ")
    changed = [key for key in pre if pre[key] != post[key]]
    require(changed == ["commentsSha256"],
            f"{label} program changes differ: {changed}")
    require(post["commentsSha256"] ==
            "7bf6458538656da36fea94f5ca62c41ca026d75f489e2b59fc3fd3c502c62c2a",
            f"{label} POST comment census digest differs")
    return {
        "changedMetrics": changed,
        "memoryBytesUnchanged": pre["memorySha256"] == post["memorySha256"],
        "instructionLayoutUnchanged":
            pre["instructionLayoutSha256"] == post["instructionLayoutSha256"],
        "definedDataUnchanged": pre["definedDataSha256"] == post["definedDataSha256"],
        "undefinedDataCountUnchanged": pre["undefinedData"] == post["undefinedData"],
        "nonFunctionSymbolsUnchanged":
            pre["nonFunctionSymbolsSha256"] == post["nonFunctionSymbolsSha256"],
        "referencesUnchanged": pre["referencesSha256"] == post["referencesSha256"],
        "commentCountUnchanged": pre["comments"] == post["comments"],
    }


def validate_adverse(name: str, markers: tuple[str, ...], readback_name: str,
                     expected_project: Mapping[str, Any]) -> dict[str, Any]:
    root = LANE / "runs" / name
    log = root / "ghidra.log"
    text = log.read_text(encoding="utf-8", errors="replace")
    require(all(marker in text for marker in markers) and
            "REPORT SCRIPT ERROR" in text and
            "REPORT: Save succeeded for processed file: /BEA.exe" in text,
            f"{name} did not fail through the expected save boundary")
    require(not (root / "target.tsv").exists() and
            not (root / "target.ready.json").exists(),
            f"{name} published success artifacts")
    readback = validate_run(
        readback_name, "dry", "PRE",
        "CEXPLOSION_FACTORY_IDENTITY_DRY_COMPLETE mutations=0", inventory=True)
    readback_root = LANE / "runs" / readback_name
    require((readback_root / "functions.tsv").read_bytes() == PRE_FUNCTIONS.read_bytes() and
            (readback_root / "program.tsv").read_bytes() == PRE_PROGRAM.read_bytes(),
            f"{name} separate readback did not restore exact PRE inventory")
    return {
        "copyManifest": validate_initial_copy(LANE / "scratch" / name,
                                                expected_project, name),
        "failureLog": stamp(log), "publishedSuccessArtifacts": 0,
        "separatePreReadback": readback, "exactPreInventoryRestored": True,
    }


def validate_external_path_controls(expected_project: Mapping[str, Any]) -> dict[str, Any]:
    external_output = EXTERNAL_PROBE_ROOT / "external-output.tsv"
    external_ready = EXTERNAL_PROBE_ROOT / "external-ready.json"
    require(EXTERNAL_PROBE_ROOT.is_dir(), "external-path probe directory is absent")
    require(not external_output.exists() and not external_ready.exists(),
            "external-path probe published an external artifact")

    controls: dict[str, Any] = {}
    cases = {
        "externalOutput": ("probe-external-output", (
            LANE / "runs/probe-external-output/target.ready.json",
        )),
        "externalReady": ("probe-external-ready", (
            LANE / "runs/probe-external-ready/target.tsv",
        )),
    }
    for label, (name, internal_artifacts) in cases.items():
        log = LANE / "runs" / name / "ghidra.log"
        text = log.read_text(encoding="utf-8", errors="replace")
        require("REPORT: Processing project file: /BEA.exe" in text and
                "REPORT SCRIPT ERROR" in text and
                "path is outside supplied repository root" in text and
                "REPORT: Save succeeded for processed file: /BEA.exe" in text,
                f"{name} did not exercise the mutable external-path rejection")
        require("CEXPLOSION_FACTORY_IDENTITY_PREFLIGHT_OK" not in text and
                "CEXPLOSION_FACTORY_IDENTITY_MUTATION_TAINTED" not in text and
                "CEXPLOSION_FACTORY_IDENTITY_APPLY_COMPLETE" not in text,
                f"{name} crossed the PRE/transaction boundary")
        require(all(not path.exists() for path in internal_artifacts),
                f"{name} published an internal success artifact")
        controls[label] = {"log": stamp(log), "publishedArtifacts": 0,
                           "rejectedBeforePreValidation": True,
                           "rejectedBeforeTransaction": True}

    readback = validate_run(
        "probe-external-readback", "dry", "PRE",
        "CEXPLOSION_FACTORY_IDENTITY_DRY_COMPLETE mutations=0", inventory=True)
    readback_root = LANE / "runs/probe-external-readback"
    require((readback_root / "functions.tsv").read_bytes() == PRE_FUNCTIONS.read_bytes() and
            (readback_root / "program.tsv").read_bytes() == PRE_PROGRAM.read_bytes(),
            "external-path controls did not preserve exact PRE inventory")
    return {
        "copyManifest": validate_initial_copy(
            LANE / "scratch/probe-after-one", expected_project,
            "external-path shared probe copy"),
        "controls": controls, "separatePreReadback": readback,
        "exactPreInventoryRestored": True,
    }


def immutable_inputs() -> dict[str, Any]:
    return {rel(path): require_stamp(path) for path in STAMPS}


def build(generated_at: str) -> dict[str, Any]:
    parse_utc(generated_at, "generatedAtUtc")
    inputs = immutable_inputs()
    project, baseline_manifest = baseline_project()
    restore = validate_restore(LANE / "baseline-restore.ready.json", project)
    pretransaction = validate_external_path_controls(project)
    replicas: dict[str, Any] = {}
    for name in ("replica-a", "replica-b"):
        root = LANE / "runs"
        replicas[name] = {
            "copyManifest": validate_initial_copy(LANE / "scratch" / name, project, name),
            "dry": validate_run(name + "-dry", "dry", "PRE",
                                "CEXPLOSION_FACTORY_IDENTITY_DRY_COMPLETE mutations=0"),
            "apply": validate_run(name + "-apply", "apply", "POST",
                                  "CEXPLOSION_FACTORY_IDENTITY_APPLY_COMPLETE target=1 "
                                  "reopen_verification_required=true"),
            "readback": validate_run(name + "-readback", "readback", "POST",
                                     "CEXPLOSION_FACTORY_IDENTITY_READBACK_COMPLETE "
                                     "loaded_state_verified=true", inventory=True),
            "functionDelta": compare_inventories(
                root / f"{name}-readback/functions.tsv", name),
            "programDelta": compare_programs(
                root / f"{name}-readback/program.tsv", name),
        }
    for artifact in ("target.tsv", "functions.tsv", "program.tsv"):
        require((LANE / f"runs/replica-a-readback/{artifact}").read_bytes() ==
                (LANE / f"runs/replica-b-readback/{artifact}").read_bytes(),
                f"positive replica readback {artifact} differs")
    for phase in ("dry", "apply"):
        require((LANE / f"runs/replica-a-{phase}/target.tsv").read_bytes() ==
                (LANE / f"runs/replica-b-{phase}/target.tsv").read_bytes(),
                f"positive replica {phase} target output differs")
    adverse = {
        "afterOne": validate_adverse("probe-after-one", (
            "CEXPLOSION_FACTORY_IDENTITY_FORCED_AFTER_ONE_FAILURE rollback_required=true",
            "CEXPLOSION_FACTORY_IDENTITY_MUTATION_TAINTED mode=probe-after-one",
        ), "probe-after-one-readback", project),
        "postInner": validate_adverse("probe-post-inner", (
            "CEXPLOSION_FACTORY_IDENTITY_COMPENSATING_PRE_RESTORE_COMPLETE target=1",
            "CEXPLOSION_FACTORY_IDENTITY_FORCED_POST_INNER_FAILURE pre_restored=true",
            "CEXPLOSION_FACTORY_IDENTITY_MUTATION_TAINTED mode=probe-post-inner",
        ), "probe-post-inner-readback", project),
    }
    return {
        "schema": SCHEMA, "phase": "SCRATCH_VALIDATED", "verdict": "READY",
        "generatedAtUtc": generated_at,
        "claim": "ONE_ROW_CEXPLOSION_FACTORY_IDENTITY_REPAIR_SCRATCH_VALIDATED",
        "author": stamp(SCRIPT), "immutableInputs": inputs,
        "baseline": {"backupManifest": baseline_manifest,
                     "projectFiles": project["fileCount"],
                     "projectBytes": project["totalBytes"], "restore": restore},
        "replicas": replicas, "preTransactionControls": pretransaction,
        "adverseControls": adverse,
        "result": {
            "target": TARGET, "positiveReplicas": 2, "adverseControls": 2,
            "preTransactionPathControls": 2,
            "functionRows": FUNCTION_COUNT, "nonTargetFunctionRowsUnchanged": 8_169,
            "functionRowsChanged": 1, "bytesChanged": 0,
            "instructionLayoutChanged": 0, "definedDataChanged": 0,
            "undefinedDataCountChanged": 0, "referencesChanged": 0,
            "nonFunctionSymbolsChanged": 0, "commentCountChanged": 0,
            "loadedPostReadbacks": 2, "exactPreAdverseReadbacks": 2,
        },
        "authorization": {
            "scratchRepairValidated": True, "liveApplyAuthorizedByThisReceipt": False,
            "externalOutputAndReadyPreflightValidated": True,
            "freshLivePreflightRequired": True, "freshLiveBackupRequired": True,
            "oneMutationProcessMaximum": True, "separateLiveReadbackRequired": True,
            "postBackupRestoreAndTrackedRefreshRequired": True,
            "runtimeSemanticsAuthorized": False, "rebuildReadyAuthorized": False,
        },
        "limitations": [
            "The identity and signature are bounded C1 static contracts; exact source spelling remains open.",
            "The parameter name is descriptive, not recovered source spelling.",
            "Runtime reachability, effects, failure frequency, layout completion, and rebuild parity remain open.",
            "No live or tracked-canonical Ghidra project was opened for mutation by this lane.",
        ],
    }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def publish(path: Path, payload: Mapping[str, Any]) -> None:
    require(not path.exists(), f"refusing to overwrite authority receipt: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    content = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
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


def verify_saved() -> dict[str, Any]:
    saved = load_json(SCRATCH_READY)
    require(isinstance(saved, dict) and
            saved == build(saved.get("generatedAtUtc", "")),
            "scratch authority receipt no longer reproduces")
    return saved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("seal", "verify"))
    args = parser.parse_args()
    if args.command == "seal":
        publish(SCRATCH_READY, build(utc_now()))
        verify_saved()
        print("CEXPLOSION_FACTORY_IDENTITY_SCRATCH_AUTHORITY_READY "
              f"sha256={sha256_file(SCRATCH_READY)}")
    else:
        verify_saved()
        print("CEXPLOSION_FACTORY_IDENTITY_SCRATCH_AUTHORITY_VERIFIED "
              f"sha256={sha256_file(SCRATCH_READY)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
