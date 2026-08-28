#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Fail-closed receipt owner for the 34 Mission-registry boundaries.

This program never opens or mutates Ghidra.  It seals already-produced
scratch or live evidence only after checking the immutable campaign inputs,
backup/restore receipts, two positive scratch replicas, two adverse controls,
separate-process readbacks, and exact full-inventory collateral deltas.
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
from typing import Any, Callable, Mapping


REPO = Path(__file__).resolve().parent.parent
SCRIPT = Path(__file__).resolve()
LANE = REPO / "local-lab/ghidra-mission-registry-boundary-live-promotion-20260813-v1"
LIVE = Path(r"C:\Users\david\Ghidra\Projects")
TRACKED = REPO / "reverse-engineering/ghidra"
PRE_BACKUP = Path(r"H:\BEA-Ghidra-Backups\2026-08-13-mission-registry-boundaries-pre-live")
POST_BACKUP = Path(r"H:\BEA-Ghidra-Backups\2026-08-13-mission-registry-boundaries-post-live")
PRE_FUNCTIONS = (
    REPO / "local-lab/ghidra-collision-component-identity-live-promotion-20260812-v1/"
    "runs/live-readback/functions.tsv"
)
PRE_PROGRAM = PRE_FUNCTIONS.with_name("program.tsv")
MANIFEST = (
    REPO / "reverse-engineering/binary-analysis/"
    "mission-script-registry-missing-function-boundaries-2026-08-13.tsv"
)
OWNER = MANIFEST.with_suffix(".md")
REGISTRY = (
    REPO / "reverse-engineering/binary-analysis/"
    "mission-script-command-registry-2026-08-12.tsv"
)
TOOL = REPO / "tools/GhidraApplyMissionRegistryBoundaries.java"
INVENTORY_TOOL = REPO / "tools/ExportFullFunctionInventory.java"
OPEN_PROBE = REPO / "tools/GhidraProjectOpenProbe.java"
ANALYZE_HEADLESS = Path(
    r"D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC\support\analyzeHeadless.bat"
)
SCRATCH_READY = LANE / "scratch-authority.ready.json"
LIVE_READY = LANE / "live-promotion.ready.json"

SCHEMA = "bea.ghidra.mission-registry-boundary-authority.v1"
TOOL_SCHEMA = "bea.ghidra.mission-registry-boundaries.v1"
PROGRAM_SHA = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
PRE_FUNCTION_COUNT = 8_136
POST_FUNCTION_COUNT = 8_170
# The generic project-open probe uses FunctionManager.getFunctionCount(), which
# includes 224 external/import functions.  Full inventories intentionally use
# getFunctions(true) and count internal functions only.  These are two exact,
# independently named censuses; neither is a substitute for the other.
PRE_OPEN_FUNCTION_COUNT = 8_360
POST_OPEN_FUNCTION_COUNT = 8_394
INSTRUCTION_COUNT = 549_872
TARGET_COUNT = 34
STAMPS = {
    MANIFEST: (7_264, "e53fd6f4c44ab7f91779e0673e91ae3701514c486594cc733025334fe6289a42"),
    OWNER: (6_481, "6c6bc9334fadf64f3c7785901331c84a7223b728670a55b56bf2e4774bce8041"),
    REGISTRY: (6_924, "61a44b1a393251bfd32c28a037648968575bfbd55afc1cba8e39bd269a5e1fdd"),
    TOOL: (44_683, "209f0b12e6c841d49ffb719d689f97461a36782fda40ed6b2ca0155ba00f7791"),
    INVENTORY_TOOL: (23_963, "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197"),
    OPEN_PROBE: (3_453, "18bbfdebc56081e7d4c47871d56e9e0964a21e478d1036c9e527051ac7f9e490"),
    PRE_FUNCTIONS: (7_060_261, "8261d68189cad3433cb6ea26806e4d5687f0c1179fc399b460abc40917e1b7fc"),
    PRE_PROGRAM: (1_267, "cfecff143ddd2b30fae92ad98235d24e1bfa38e44b035a904769527131cc212f"),
}


class AuthorityError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise AuthorityError(message)


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
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise AuthorityError(f"{label} is malformed") from exc


def load_targets() -> dict[str, dict[str, str]]:
    rows = read_tsv(MANIFEST)
    require(len(rows) == TARGET_COUNT, "boundary manifest target count differs")
    result = {row["entry"]: row for row in rows}
    require(len(result) == TARGET_COUNT, "boundary manifest entries are not distinct")
    return result


def range_bounds(text: str) -> tuple[int, int]:
    parts = text.split(",")
    require(len(parts) == 1, "this cohort requires one contiguous body per target")
    start_text, end_text = parts[0].split("-", 1)
    start, end_exclusive = int(start_text, 16), int(end_text, 16)
    require(start < end_exclusive, "empty or inverted half-open range")
    return start, end_exclusive


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
        require(stat.st_nlink == 1, f"project contains linked file: {path}")
        relative = path.relative_to(root).as_posix()
        if relative != "BEA.gpr" and not relative.startswith("BEA.rep/"):
            continue
        files.append({"relative_path": relative, "sha256": sha256_file(path),
                      "size": stat.st_size})
        total += stat.st_size
    files.sort(key=lambda row: row["relative_path"])
    return {"projectName": "BEA", "fileCount": len(files), "totalBytes": total,
            "structurallyComplete": any(row["relative_path"] == "BEA.gpr" for row in files)
            and any(row["relative_path"].startswith("BEA.rep/") for row in files),
            "files": files}


def project_fields(value: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value.get(key) for key in
            ("projectName", "fileCount", "totalBytes", "structurallyComplete", "files")}


def backup_project(root: Path, label: str) -> dict[str, Any]:
    manifest_path = root / "backup_manifest.json"
    value = load_json(manifest_path)
    require(value.get("sourceStable") is True, f"{label} source was unstable")
    require(value.get("copyComparison", {}).get("matches") is True,
            f"{label} copy differs")
    source = project_fields(value.get("source", {}))
    destination = project_fields(value.get("destination", {}))
    require(source == destination == plain_project(root), f"{label} project bytes differ")
    return {"manifest": stamp(manifest_path), "project": destination}


def initial_copy_project(root: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    value = load_json(root / "backup_manifest.json")
    require(value.get("sourceStable") is True and
            value.get("copyComparison", {}).get("matches") is True,
            f"{label} initial copy is not clean")
    require(project_fields(value.get("source", {})) == expected and
            project_fields(value.get("destination", {})) == expected,
            f"{label} initial PRE copy differs")
    return stamp(root / "backup_manifest.json")


def validate_restore(path: Path, expected: Mapping[str, Any], label: str,
                     expected_open_functions: int) -> dict[str, Any]:
    value = load_json(path)
    require(value.get("sourceStable") is True and
            value.get("copyComparison", {}).get("matches") is True,
            f"{label} copy differs")
    opened = value.get("readonlyOpen", {})
    require(opened.get("opened") is True and opened.get("contentStable") is True and
            opened.get("postOpenComparison", {}).get("matches") is True,
            f"{label} read-only restore/open probe failed")
    require(opened.get("observedProgramMd5") == PROGRAM_MD5 and
            opened.get("observedProgramSha256") == PROGRAM_SHA and
            opened.get("observedFunctionCount") == expected_open_functions,
            f"{label} program identity differs")
    expected_argv = [
        str(ANALYZE_HEADLESS), value.get("probeCopy"), "BEA", "-process", "BEA.exe",
        "-readOnly", "-noanalysis", "-scriptPath", str(REPO / "tools"),
        "-postScript", OPEN_PROBE.name, "BEA.exe", PROGRAM_MD5, PROGRAM_SHA,
    ]
    require(opened.get("commandArgv") == expected_argv,
            f"{label} open-probe command differs")
    log_claim = opened.get("probeLog", {})
    log_path = path.with_name(str(log_claim.get("path", "")))
    actual_log = stamp(log_path)
    require(log_claim.get("bytes") == actual_log["bytes"] and
            log_claim.get("sha256") == actual_log["sha256"],
            f"{label} open-probe log differs")
    require(project_fields(value.get("source", {})) == expected,
            f"{label} source project differs")
    return stamp(path)


def validate_boundary_tsv(path: Path, mode: str, state: str) -> dict[str, Any]:
    targets = load_targets()
    rows = read_tsv(path)
    require(len(rows) == TARGET_COUNT and {row.get("entry") for row in rows} == set(targets),
            f"{mode} boundary row census differs")
    for row in rows:
        target = targets[row["entry"]]
        for key in ("registryIndex", "command", "recordVa", "entry", "reachableBodyRanges",
                    "bodyBytes", "bodyRangeSha256", "bodyBytesSha256", "instructionCount"):
            require(row.get(key) == target[key], f"{mode} row {key} differs at {row['entry']}")
        require(row.get("mode") == mode and row.get("state") == state,
                f"{mode} mode/state differs at {row['entry']}")
        require(row.get("isThunk") == "false" and row.get("commentPresent") == "false" and
                row.get("repeatableCommentPresent") == "false" and row.get("tagCount") == "0",
                f"{mode} metadata envelope differs at {row['entry']}")
        if state == "PRE":
            require(not row.get("name") and not row.get("nameSource") and not row.get("sigSource"),
                    f"{mode} PRE target unexpectedly exists at {row['entry']}")
        else:
            require(row.get("name") == target["expectedDefaultName"] and
                    row.get("nameSource") == "DEFAULT" and row.get("sigSource") == "DEFAULT",
                    f"{mode} POST default identity differs at {row['entry']}")
    return stamp(path)


def validate_ready(path: Path, mode: str, state: str) -> dict[str, Any]:
    value = load_json(path)
    require(value.get("schemaVersion") == TOOL_SCHEMA, f"{mode} receipt schema differs")
    parse_utc(value.get("completedAtUtc"), f"{mode} completedAtUtc")
    require(value.get("mode") == mode and value.get("state") == state,
            f"{mode} receipt state differs")
    program = value.get("program", {})
    expected_functions = PRE_FUNCTION_COUNT if state == "PRE" else POST_FUNCTION_COUNT
    require(program.get("md5") == PROGRAM_MD5 and program.get("sha256") == PROGRAM_SHA and
            program.get("functions") == expected_functions and
            program.get("instructions") == INSTRUCTION_COUNT,
            f"{mode} receipt program differs")
    require(value.get("manifest", {}).get("bytes") == STAMPS[MANIFEST][0] and
            value.get("manifest", {}).get("sha256") == STAMPS[MANIFEST][1] and
            value.get("manifest", {}).get("targets") == TARGET_COUNT,
            f"{mode} manifest binding differs")
    require(value.get("tool", {}).get("bytes") == STAMPS[TOOL][0] and
            value.get("tool", {}).get("sha256") == STAMPS[TOOL][1],
            f"{mode} tool binding differs")
    require(value.get("boundariesChanged") == (0 if state == "PRE" else TARGET_COUNT) and
            value.get("namesAuthorized") is False and
            value.get("metadataAuthorized") is False,
            f"{mode} authority boundary differs")
    output = Path(value.get("output", {}).get("path", ""))
    require(output.is_file() and output.stat().st_size == value["output"]["bytes"] and
            sha256_file(output) == value["output"]["sha256"],
            f"{mode} output binding differs")
    return stamp(path)


def validate_run(name: str, mode: str, state: str, marker: str,
                 *, inventory: bool = False) -> dict[str, Any]:
    root = LANE / "runs" / name
    log = root / "ghidra.log"
    text = log.read_text(encoding="utf-8", errors="replace")
    require(marker in text and "REPORT SCRIPT ERROR" not in text,
            f"{name} success marker/error state differs")
    result = {"boundaries": validate_boundary_tsv(root / "boundaries.tsv", mode, state),
              "ready": validate_ready(root / "boundaries.ready.json", mode, state),
              "log": stamp(log)}
    if inventory:
        result["functions"] = stamp(root / "functions.tsv")
        result["program"] = stamp(root / "program.tsv")
    return result


def validate_adverse(name: str, markers: tuple[str, ...], readback: str) -> dict[str, Any]:
    root = LANE / "runs" / name
    log = root / "ghidra.log"
    text = log.read_text(encoding="utf-8", errors="replace")
    require(all(marker in text for marker in markers) and "REPORT SCRIPT ERROR" in text,
            f"{name} did not fail with the required markers")
    require(not (root / "boundaries.tsv").exists() and
            not (root / "boundaries.ready.json").exists(),
            f"{name} published success artifacts")
    separate = validate_run(
        readback, "dry", "PRE",
        "MISSION_REGISTRY_BOUNDARIES_DRY_COMPLETE targets=34 mutations=0", inventory=True)
    readback_root = LANE / "runs" / readback
    require((readback_root / "functions.tsv").read_bytes() == PRE_FUNCTIONS.read_bytes() and
            (readback_root / "program.tsv").read_bytes() == PRE_PROGRAM.read_bytes(),
            f"{name} separate readback did not restore exact PRE inventory")
    return {"failureLog": stamp(log), "publishedSuccessArtifacts": 0,
            "separatePreReadback": separate, "exactPreInventoryRestored": True}


def compare_inventories(pre_path: Path, post_path: Path, label: str) -> dict[str, Any]:
    targets = load_targets()
    pre_rows = read_tsv(pre_path)
    post_rows = read_tsv(post_path)
    pre = {row["address"]: row for row in pre_rows}
    post = {row["address"]: row for row in post_rows}
    require(len(pre) == PRE_FUNCTION_COUNT and len(post) == POST_FUNCTION_COUNT,
            f"{label} function census differs")
    added = set(post) - set(pre)
    require(not (set(pre) - set(post)) and added == set(targets),
            f"{label} added/removed address set differs")
    require(all(pre[address] == post[address] for address in pre),
            f"{label} changed a pre-existing function row")
    for address in sorted(added):
        row, target = post[address], targets[address]
        start, end_exclusive = range_bounds(target["reachableBodyRanges"])
        expected = {
            "name": target["expectedDefaultName"], "fqname": target["expectedDefaultName"],
            "nameSource": "DEFAULT", "sigSource": "DEFAULT",
            "bodyBytes": target["bodyBytes"], "bodyMin": f"0x{start:08x}",
            "bodyMax": f"0x{end_exclusive - 1:08x}", "bodyRanges": "1",
            "bodyDigest": target["bodyRangeSha256"], "instrCount": target["instructionCount"],
            "paramCount": "0", "callingConv": "unknown", "returnType": "undefined",
            "varArgs": "false", "isThunk": "false", "thunkTarget": "",
            "isExternal": "false", "customStorage": "false", "inline": "false",
            "noReturn": "false", "commentPresent": "false", "commentLen": "0",
            "repeatableCommentPresent": "false", "repeatableCommentLen": "0",
            "tagCount": "0", "tags": "",
        }
        require(all(row.get(key) == value for key, value in expected.items()),
                f"{label} added row metadata differs at {address}")
    return {"preFunctionsUnchanged": PRE_FUNCTION_COUNT,
            "addedAddresses": sorted(added), "postFunctions": POST_FUNCTION_COUNT}


def compare_programs(pre_path: Path, post_path: Path, label: str) -> dict[str, Any]:
    pre = {row["metric"]: row["value"] for row in read_tsv(pre_path)}
    post = {row["metric"]: row["value"] for row in read_tsv(post_path)}
    require(pre.keys() == post.keys(), f"{label} program metric keys differ")
    changed = [key for key in sorted(pre) if pre[key] != post[key]]
    require(changed == ["functions"] and pre["functions"] == str(PRE_FUNCTION_COUNT) and
            post["functions"] == str(POST_FUNCTION_COUNT),
            f"{label} program metric changes differ: {changed}")
    return {"changedMetrics": changed, "functionDelta": TARGET_COUNT,
            "instructions": int(post["instructions"])}


def immutable_inputs() -> dict[str, Any]:
    return {rel(path): require_stamp(path) for path in STAMPS}


def build_scratch(generated_at: str, *, require_live_pre: bool = True) -> dict[str, Any]:
    parse_utc(generated_at, "generatedAtUtc")
    inputs = immutable_inputs()
    pre = backup_project(PRE_BACKUP, "PRE backup")
    restore = validate_restore(LANE / "pre-backup-restore.ready.json", pre["project"],
                               "PRE restore", PRE_OPEN_FUNCTION_COUNT)
    inspect = load_json(LANE / "live-pre-inspect.json")
    require(project_fields(inspect.get("manifest", {})) == pre["project"],
            "live PRE inspection differs")
    if require_live_pre:
        require(plain_project(LIVE) == pre["project"], "live project drifted from PRE")
        require(plain_project(TRACKED) == pre["project"], "tracked snapshot drifted from PRE")

    replicas: dict[str, Any] = {}
    for name in ("replica-a", "replica-b"):
        replicas[name] = {
            "copyManifest": initial_copy_project(LANE / "scratch" / name, pre["project"], name),
            "dry": validate_run(name + "-dry", "dry", "PRE",
                                "MISSION_REGISTRY_BOUNDARIES_DRY_COMPLETE targets=34 mutations=0"),
            "apply": validate_run(name + "-apply", "apply", "POST",
                                  "MISSION_REGISTRY_BOUNDARIES_APPLY_COMPLETE targets=34 "
                                  "function_count=8170 reopen_verification_required=true"),
            "readback": validate_run(name + "-readback", "readback", "POST",
                                     "MISSION_REGISTRY_BOUNDARIES_READBACK_COMPLETE targets=34 "
                                     "function_count=8170 loaded_state_verified=true", inventory=True),
        }
        replicas[name]["collateral"] = {
            "functions": compare_inventories(
                PRE_FUNCTIONS, LANE / f"runs/{name}-readback/functions.tsv", name),
            "program": compare_programs(
                PRE_PROGRAM, LANE / f"runs/{name}-readback/program.tsv", name),
        }
    for artifact in ("boundaries.tsv", "functions.tsv", "program.tsv"):
        require((LANE / f"runs/replica-a-readback/{artifact}").read_bytes() ==
                (LANE / f"runs/replica-b-readback/{artifact}").read_bytes(),
                f"replica readback {artifact} differs")
    for phase in ("dry", "apply"):
        require((LANE / f"runs/replica-a-{phase}/boundaries.tsv").read_bytes() ==
                (LANE / f"runs/replica-b-{phase}/boundaries.tsv").read_bytes(),
                f"replica {phase} boundary output differs")
    adverse = {
        "afterOne": validate_adverse("probe-after-one", (
            "MISSION_REGISTRY_BOUNDARIES_FORCED_AFTER_ONE_FAILURE rollback_required=true",
            "MISSION_REGISTRY_BOUNDARIES_MUTATION_TAINTED mode=probe-after-one",
        ), "probe-after-one-readback"),
        "postInner": validate_adverse("probe-post-inner", (
            "MISSION_REGISTRY_BOUNDARIES_COMPENSATING_PRE_RESTORE_COMPLETE targets=34",
            "MISSION_REGISTRY_BOUNDARIES_FORCED_POST_INNER_FAILURE pre_restored=true",
            "MISSION_REGISTRY_BOUNDARIES_MUTATION_TAINTED mode=probe-post-inner",
        ), "probe-post-inner-readback"),
    }
    return {
        "schema": SCHEMA, "phase": "SCRATCH_AUTHORITY", "verdict": "READY",
        "generatedAtUtc": generated_at,
        "claim": "THIRTY_FOUR_MISSION_REGISTRY_FUNCTION_BOUNDARIES_AUTHORIZED_FOR_ONE_LIVE_APPLY",
        "author": stamp(SCRIPT), "immutableInputs": inputs,
        "pre": {"backup": pre["manifest"], "restore": restore,
                "liveInspection": stamp(LANE / "live-pre-inspect.json")},
        "replicas": replicas, "adverseControls": adverse,
        "delta": {"functionsBefore": PRE_FUNCTION_COUNT, "functionsAfter": POST_FUNCTION_COUNT,
                  "openProbeFunctionsBefore": PRE_OPEN_FUNCTION_COUNT,
                  "openProbeFunctionsAfter": POST_OPEN_FUNCTION_COUNT,
                  "boundariesCreated": TARGET_COUNT, "instructions": INSTRUCTION_COUNT,
                  "preExistingRowsChanged": 0, "bytesChanged": 0,
                  "instructionLayoutChanged": 0, "dataChanged": 0,
                  "referencesChanged": 0, "commentsChanged": 0,
                  "nonTargetSymbolsChanged": 0},
        "authorization": {"liveApplyAuthorized": True, "mutationProcessLimit": 1,
                          "separateReadbackRequired": True,
                          "postBackupAndRestoreRequired": True,
                          "trackedSnapshotRefreshRequired": True,
                          "namesAuthorized": False, "signaturesAuthorized": False,
                          "commentsAuthorized": False, "tagsAuthorized": False,
                          "runtimeClaimsAuthorized": False,
                          "rebuildReadyAuthorized": False},
        "limitations": [
            "The registry proves handler entries, not original C++ symbols.",
            "Only function boundaries with Ghidra default metadata are authorized.",
            "No signature, runtime behavior, reconstruction mapping, or REBUILD_READY status is authorized.",
        ],
    }


def build_live(generated_at: str) -> dict[str, Any]:
    parse_utc(generated_at, "generatedAtUtc")
    scratch = load_json(SCRATCH_READY)
    require(scratch == build_scratch(scratch.get("generatedAtUtc", ""), require_live_pre=False),
            "scratch authority no longer reproduces")
    require(scratch.get("authorization", {}).get("liveApplyAuthorized") is True,
            "scratch authority does not authorize live apply")
    dry = validate_run("live-dry", "dry", "PRE",
                       "MISSION_REGISTRY_BOUNDARIES_DRY_COMPLETE targets=34 mutations=0")
    apply = validate_run("live-apply", "apply", "POST",
                         "MISSION_REGISTRY_BOUNDARIES_APPLY_COMPLETE targets=34 "
                         "function_count=8170 reopen_verification_required=true")
    readback = validate_run("live-readback", "readback", "POST",
                            "MISSION_REGISTRY_BOUNDARIES_READBACK_COMPLETE targets=34 "
                            "function_count=8170 loaded_state_verified=true", inventory=True)
    for artifact in ("boundaries.tsv", "functions.tsv", "program.tsv"):
        require((LANE / f"runs/live-readback/{artifact}").read_bytes() ==
                (LANE / f"runs/replica-a-readback/{artifact}").read_bytes(),
                f"live readback {artifact} differs from scratch authority")
    collateral = {
        "functions": compare_inventories(PRE_FUNCTIONS, LANE / "runs/live-readback/functions.tsv",
                                         "live"),
        "program": compare_programs(PRE_PROGRAM, LANE / "runs/live-readback/program.tsv", "live"),
    }
    post = backup_project(POST_BACKUP, "POST backup")
    require(plain_project(LIVE) == post["project"], "live project differs from POST backup")
    post_restore = validate_restore(LANE / "post-backup-restore.ready.json", post["project"],
                                    "POST restore", POST_OPEN_FUNCTION_COUNT)
    require(plain_project(TRACKED) == post["project"], "tracked snapshot differs from live POST")
    tracked_restore = validate_restore(LANE / "tracked-snapshot-restore.ready.json",
                                       post["project"], "tracked snapshot restore",
                                       POST_OPEN_FUNCTION_COUNT)
    logs = sorted((LANE / "runs").glob("live-*/ghidra.log"))
    mutating = [path for path in logs if "MISSION_REGISTRY_BOUNDARIES_APPLY_COMPLETE" in
                path.read_text(encoding="utf-8", errors="replace")]
    require(mutating == [LANE / "runs/live-apply/ghidra.log"],
            "live mutation-process census differs from one")
    return {
        "schema": SCHEMA, "phase": "LIVE_PROMOTED", "verdict": "READY",
        "generatedAtUtc": generated_at,
        "claim": "MISSION_REGISTRY_BOUNDARIES_SAVED_READ_BACK_BACKED_UP_AND_TRACKED",
        "author": stamp(SCRIPT), "scratchAuthority": stamp(SCRATCH_READY),
        "live": {"dry": dry, "apply": apply, "readback": readback,
                 "collateral": collateral, "postBackup": post["manifest"],
                 "postRestore": post_restore},
        "trackedSnapshot": {"root": rel(TRACKED), "project": post["project"],
                            "restore": tracked_restore},
        "result": {"boundariesCreated": TARGET_COUNT, "functionCount": POST_FUNCTION_COUNT,
                   "instructionCount": INSTRUCTION_COUNT, "preExistingRowsChanged": 0,
                   "liveMutationProcesses": 1, "separateReadbackPassed": True,
                   "recoverablePostBackupPassed": True,
                   "trackedSnapshotMatchesLive": True,
                   "namesAuthorized": False, "metadataAuthorized": False},
        "limitations": scratch["limitations"],
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


def verify_saved(path: Path, builder: Callable[[str], dict[str, Any]]) -> dict[str, Any]:
    saved = load_json(path)
    require(isinstance(saved, dict) and
            saved == builder(saved.get("generatedAtUtc", "")),
            f"authority receipt does not reproduce: {path}")
    return saved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("seal-scratch", "verify-scratch",
                                           "seal-live", "verify-live"))
    args = parser.parse_args()
    if args.command == "seal-scratch":
        publish(SCRATCH_READY, build_scratch(utc_now()))
        verify_saved(SCRATCH_READY, build_scratch)
        print(f"MISSION_REGISTRY_BOUNDARY_SCRATCH_AUTHORITY_READY sha256={sha256_file(SCRATCH_READY)}")
    elif args.command == "verify-scratch":
        verify_saved(SCRATCH_READY, build_scratch)
        print(f"MISSION_REGISTRY_BOUNDARY_SCRATCH_AUTHORITY_VERIFIED sha256={sha256_file(SCRATCH_READY)}")
    elif args.command == "seal-live":
        publish(LIVE_READY, build_live(utc_now()))
        verify_saved(LIVE_READY, build_live)
        print(f"MISSION_REGISTRY_BOUNDARY_LIVE_PROMOTION_READY sha256={sha256_file(LIVE_READY)}")
    else:
        verify_saved(LIVE_READY, build_live)
        print(f"MISSION_REGISTRY_BOUNDARY_LIVE_PROMOTION_VERIFIED sha256={sha256_file(LIVE_READY)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
