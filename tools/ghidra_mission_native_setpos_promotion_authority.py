#!/usr/bin/env python3
"""Seal the bounded Mission-native SetPos Ghidra promotion ceremony.

This owner is intentionally specific.  It admits exactly one new function at
0x00536C70, one reviewed name/signature/comment, two independent scratch
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
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


REPO = Path(__file__).resolve().parent.parent
SCRIPT = Path(__file__).resolve()
LANE = REPO / "local-lab" / "ghidra-mission-native-setpos-live-promotion-20260809-v1"
LIVE = Path(r"C:\Users\david\Ghidra\Projects")
SOURCE_PRE = (
    REPO / "local-lab" / "ghidra-tokenarchive-dispatch-live-promotion-20260809-v1"
    / "backups" / "post-live"
)
SOURCE_MANIFEST = SOURCE_PRE / "backup_manifest.json"
SOURCE_AUTHORITY = (
    REPO / "local-lab" / "ghidra-tokenarchive-dispatch-live-promotion-20260809-v1"
    / "promotion" / "promotion.ready.json"
)
SOURCE_RESTORE = (
    REPO / "local-lab" / "ghidra-tokenarchive-dispatch-live-promotion-20260809-v1"
    / "post-live-restore.ready.json"
)
TOOL = REPO / "tools" / "GhidraApplyMissionNativeSetPos.java"
INVENTORY_TOOL = REPO / "tools" / "ExportFullFunctionInventory.java"
OPEN_PROBE_TOOL = REPO / "tools" / "GhidraProjectOpenProbe.java"
CAMPAIGN = (
    REPO / "local-lab" / "re-campaign-incident-recovery-20260808-v1"
    / "generation-14-tokenarchive-dispatch-reproof-v1" / "campaign.ready.json"
)
PROOF = (
    REPO / "local-lab" / "mission-native-setpos-boundary-reproof-20260809-v1"
    / "proof.ready.json"
)
CAMPAIGN_AUTHORITY = (
    REPO / "local-lab" / "re-campaign-incident-recovery-20260808-v1"
    / "generation-14-tokenarchive-dispatch-reproof-authority.ready.json"
)
BOUNDARY = (
    REPO / "local-lab" / "mission-native-setpos-boundary-reproof-20260809-v1"
    / "setpos-boundary.tsv"
)
PRE_BACKUP = LANE / "backups" / "pre-live"
PRE_MANIFEST = PRE_BACKUP / "backup_manifest.json"
PRE_RESTORE = LANE / "pre-live-restore.ready.json"
POST_BACKUP = LANE / "backups" / "post-live"
POST_MANIFEST = POST_BACKUP / "backup_manifest.json"
POST_RESTORE = LANE / "post-live-restore.ready.json"
SCRATCH_READY = LANE / "promotion" / "scratch-authority-v2.ready.json"
LIVE_READY = LANE / "promotion" / "promotion.ready.json"
ANALYZE_HEADLESS = Path(
    r"D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC\support\analyzeHeadless.bat"
)

SCHEMA = "bea.ghidra.mission-native-setpos-promotion-authority.v1"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
PROGRAM_SHA = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
TOOL_STAMP = (38_069, "f42d1e29d99e79eee5b9720f1f58a51b04ed50c06b84b8d0900114b0689bf602")
INVENTORY_TOOL_STAMP = (
    23_963, "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197"
)
CAMPAIGN_STAMP = (16_930, "9864424def44034a5a5e9a68814ce111076182ad7ea898c9d0040d888c92f32b")
PROOF_STAMP = (12_100, "7fca2c1e960166603ece107c112217ea674e6c2d898622594432817a803a0a7d")
CAMPAIGN_AUTHORITY_STAMP = (
    8_215, "83a5544bdde805762b01983171c336826ea62a8b2dd8be94109bef959560ff72"
)
BOUNDARY_STAMP = (596, "ff51232a512bd2d67be184d3c17c68cea2a2b5f9a4899706de6ab7002dc14c3c")
SOURCE_MANIFEST_STAMP = (
    7_589, "ad7e7ce4e8d135f5455355946cbdb7eeb7111cb99c0d54045723d736b4ed908b"
)
SOURCE_AUTHORITY_STAMP = (
    6_072, "8ca256ec03e36aa27c4f25720ce6882fc1ece3d91d408a4097b2740e239ec632"
)
SOURCE_RESTORE_STAMP = (
    6_007, "2bfbd3728a1c237efc2b340a1230052ea299c5ad6f17844fa6daf15d094afd77"
)
PRE_FUNCTIONS = (7_051_668, "075165bae3616dda0adf534625db612990daee9974b3fc85429d3b5b408ee979")
PRE_PROGRAM = (1_267, "fce597559bd1baf48d0c2759ef89aa277ba5cc0dbe6ae9a8071df5e7562adb4e")
POST_FUNCTIONS = (7_052_417, "f05259cda1c5d956098062220d6e3aada9bff4a61896a77c8fc153826691f9d0")
POST_PROGRAM = (1_267, "6907443d213f6632c778a1c0e48f2070d5b268136b55e0e5f5c187f74dcbcf8f")
PHASE_TSV_STAMPS = {
    "dry": (634, "906dd4ddf1b5e218cad97863162aba7a4100a40cf769c773ca47ee04ab4d7bb3"),
    "apply": (779, "2bd49f28caa20f41547d90616a2baa6c4bd8d31d87221c8a1d185d107d1abc3a"),
    "readback": (782, "de3ba3e722269187ff6e98b4daf570dfad4565f02559ff0246a12998fa05b508"),
}
TSV_HEADER = [
    "address", "mode", "state", "functionPresent", "name", "nameSource",
    "signatureSource", "signature", "bodyBytes", "bodyRangeSha256",
    "bodySha256", "instructionCount", "isThunk", "parameterCount",
    "stackParameterBytes", "commentBytes", "commentSha256", "functions",
    "instructions", "prefixSha256", "suffixSha256",
]
POST_SIGNATURE = (
    "void __thiscall IScript__SetPos(void * this, void * scriptArgs, "
    "void * unusedState, void * outResult)"
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
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ProofError(f"invalid JSON at {path}: {exc}") from exc


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
        if not path.is_file() or path.name == "backup_manifest.json":
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
    require_stamp(SOURCE_MANIFEST, SOURCE_MANIFEST_STAMP, "TokenArchive POST manifest")
    receipt = load_json(SOURCE_MANIFEST)
    require(receipt.get("schemaVersion") == "onslaught-ghidra-project-backup.v2",
            "TokenArchive POST manifest schema differs")
    require(receipt.get("sourceStable") is True, "TokenArchive POST source was unstable")
    zero_comparison(receipt.get("copyComparison", {}), "TokenArchive POST")
    source = project_fields(receipt["source"])
    destination = project_fields(receipt["destination"])
    require(source == destination, "TokenArchive POST source/destination differ")
    require(destination["fileCount"] == 19 and destination["totalBytes"] == 186_485_637,
            "TokenArchive POST aggregate differs")
    require(actual_project(SOURCE_PRE) == destination,
            "TokenArchive POST backup differs from its manifest")
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
            if not path.is_file() or path.name == "backup_manifest.json":
                continue
            result = path.stat()
            identity = (result.st_dev, result.st_ino)
            require(identity not in identities,
                    f"project file alias: {path} and {identities.get(identity)}")
            identities[identity] = path


def require_exact_files(root: Path, names: set[str], label: str) -> None:
    actual = {path.name for path in root.iterdir() if path.is_file()}
    require(actual == names, f"{label} file set differs: {sorted(actual)}")


def validate_phase_tsv(path: Path, phase: str) -> dict[str, str]:
    require_stamp(path, PHASE_TSV_STAMPS[phase], f"{phase} SetPos TSV")
    header, rows = read_tsv(path)
    require(header == TSV_HEADER and len(rows) == 1, f"{phase} TSV shape differs")
    row = rows[0]
    post = phase in {"apply", "readback"}
    require(row["address"] == "0x00536c70" and row["mode"] == phase,
            f"{phase} row identity differs")
    require(row["state"] == ("POST" if post else "PRE"), f"{phase} state differs")
    require(row["functionPresent"] == str(post).lower(), f"{phase} function state differs")
    require(row["name"] == ("IScript__SetPos" if post else ""), f"{phase} name differs")
    require(row["signature"] == (POST_SIGNATURE if post else ""),
            f"{phase} signature differs")
    require(row["bodyBytes"] == "42" and row["instructionCount"] == "17",
            f"{phase} body counts differ")
    require(row["bodyRangeSha256"] ==
            "cf2bfd1bce0725661afc92fb3713a23787d1bb7de771184f2e8ce5d97fd95fa2",
            f"{phase} body range differs")
    require(row["bodySha256"] ==
            "1a1ecfe8dde56ad132cc0a5d05010ebe43936f01602cc47012e4826c55ff9fa1",
            f"{phase} body bytes differ")
    require(row["functions"] == ("8125" if post else "8124") and
            row["instructions"] == "549872", f"{phase} program counts differ")
    if post:
        require(row["nameSource"] == "USER_DEFINED" and
                row["signatureSource"] == "USER_DEFINED" and
                row["parameterCount"] == "4" and row["stackParameterBytes"] == "12" and
                row["commentBytes"] == "722" and
                row["commentSha256"] ==
                "5684cf8c43a3c08df5ef0df37fb5f99d0b70e4503220edc3fbaf586359e64ea8",
                f"{phase} POST metadata differs")
    return row


def validate_run(label: str, run_name: str, phase: str, project: Path,
                 *, require_read_only: bool | None = None) -> dict[str, Any]:
    root = LANE / "runs" / run_name
    require_exact_files(root, {"headless.log", "setpos.tsv", "setpos.ready.json"}, label)
    tsv = root / "setpos.tsv"
    ready_path = root / "setpos.ready.json"
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
    require(ready["schema"] == "bea.ghidra.mission-native-setpos-promotion.v1",
            f"{label} schema differs")
    require(ready["mode"] == phase and ready["state"] == ("PRE" if phase == "dry" else "POST"),
            f"{label} mode/state differs")
    require(Path(ready["tool"]["path"]).resolve() == TOOL.resolve() and
            (ready["tool"]["bytes"], ready["tool"]["sha256"]) == TOOL_STAMP,
            f"{label} tool identity differs")
    expected_evidence = {
        "campaign": (CAMPAIGN, CAMPAIGN_STAMP), "proof": (PROOF, PROOF_STAMP),
        "authority": (CAMPAIGN_AUTHORITY, CAMPAIGN_AUTHORITY_STAMP),
        "boundaryManifest": (BOUNDARY, BOUNDARY_STAMP),
    }
    require(set(ready["evidence"]) == set(expected_evidence), f"{label} evidence shape differs")
    for key, (path, expected) in expected_evidence.items():
        value = ready["evidence"][key]
        require(Path(value["path"]).resolve() == path.resolve() and
                (value["bytes"], value["sha256"]) == expected,
                f"{label} {key} differs")
    require(Path(ready["output"]["path"]).resolve() == tsv.resolve() and
            (ready["output"]["bytes"], ready["output"]["sha256"]) ==
            PHASE_TSV_STAMPS[phase], f"{label} output differs")
    require(ready["mutation"]["entry"] == "0x00536c70" and
            ready["mutation"]["name"] == "IScript__SetPos" and
            ready["mutation"]["functionCreated"] is (phase != "dry") and
            all(ready["mutation"][key] == 0 for key in
                ("bytesChanged", "instructionsChanged", "dataUnitsChanged", "referencesChanged")),
            f"{label} mutation boundary differs")
    require(ready["counts"] == {
        "functions": 8124 if phase == "dry" else 8125,
        "instructions": 549872, "bodyBytes": 42, "bodyInstructions": 17,
        "leadingNopBytes": 15, "trailingNopBytes": 6,
    }, f"{label} counts differ")
    require(ready["commitRequested"] is (phase == "apply") and
            ready["nestedEndReturnedCommitted"] is False and
            ready["loadedStateVerified"] is (phase == "readback"),
            f"{label} transaction/readback flags differ")
    text = log.read_text(encoding="utf-8", errors="replace")
    marker = {
        "dry": "MISSION_SETPOS_DRY_COMPLETE entry=0x00536c70 mutations=0",
        "apply": "MISSION_SETPOS_APPLY_COMPLETE entry=0x00536c70 function_count=8125 reopen_verification_required=true",
        "readback": "MISSION_SETPOS_READBACK_COMPLETE entry=0x00536c70 function_count=8125 loaded_state_verified=true",
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
    require(metrics["programName"] == "BEA.exe" and metrics["executableSHA256"] == PROGRAM_SHA,
            f"{root_name} specimen differs")
    require(metrics["functions"] == ("8125" if state == "POST" else "8124") and
            metrics["instructions"] == "549872" and metrics["definedData"] == "48585" and
            metrics["references"] == "234357", f"{root_name} protected counts differ")
    if state == "POST":
        baseline = parse_program(
            REPO / "local-lab" / "ghidra-tokenarchive-dispatch-live-promotion-20260809-v1"
            / "runs" / "live-readback" / "program.tsv")
        changed = {key for key in metrics if metrics.get(key) != baseline.get(key)}
        require(changed == {"functions", "symbolsUserDefined", "symbolsDefaultOther",
                            "comments", "commentsSha256"},
                f"{root_name} changed unrelated program metrics: {sorted(changed)}")
        require(metrics["symbolsUserDefined"] == "6005" and
                metrics["symbolsDefaultOther"] == "61693" and metrics["comments"] == "9100",
                f"{root_name} POST semantic delta differs")
    text = (root / "headless.log").read_text(encoding="utf-8", errors="replace")
    require(str(project.resolve()) + "\\BEA" in text and
            "Processing read-only project file: /BEA.exe" in text and
            f"INVENTORY_OK functions={'8125' if state == 'POST' else '8124'} " in text and
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
        "MISSION_SETPOS_PREFLIGHT_OK entry=0x00536c70 body_bytes=42 instructions=17",
        f"MISSION_SETPOS_MUTATION_TAINTED mode={kind}",
        "ERROR REPORT SCRIPT ERROR",
        str(project.resolve()) + "\\BEA",
    ]
    specific = {
        "probe-after-create": [
            "MISSION_SETPOS_FORCED_AFTER_CREATE_FAILURE rollback_required=true",
            "recovery=RESTORE_VERIFIED_SCRATCH_BASE",
            "intentional Mission SetPos after-create rollback probe",
        ],
        "probe-post-inner": [
            "MISSION_SETPOS_COMPENSATING_PRE_RESTORE_COMPLETE entry=0x00536c70",
            "MISSION_SETPOS_FORCED_POST_INNER_FAILURE pre_restored=true",
            "recovery=COMPENSATING_PRE_RESTORE_VERIFIED",
            "intentional Mission SetPos post-inner rollback probe",
        ],
    }[kind]
    for marker in common + specific:
        require(marker in text, f"{kind} lacks marker: {marker}")
    require(not (root / "setpos.tsv").exists() and
            not (root / "setpos.ready.json").exists(), f"{kind} published success artifacts")
    inventory = validate_inventory(inventory_name, project, "PRE")
    return {"project": display_path(project), "failureLog": stamp(log),
            "postFailurePre": inventory, "successArtifactsAbsent": True,
            "preStateRestoredExactly": True}


def validate_restore(expected: Mapping[str, Any], receipt_path: Path,
                     probe_parent: Path, expected_functions: int, label: str) -> dict[str, Any]:
    receipt = load_json(receipt_path)
    require(receipt.get("schemaVersion") == "onslaught-ghidra-project-backup.v2",
            f"{label} schema differs")
    require(receipt.get("sourceStable") is True, f"{label} source was unstable")
    zero_comparison(receipt.get("copyComparison", {}), f"{label} copy")
    require(receipt.get("probeCopyDisposition") == "RETAINED_AT_VERIFICATION",
            f"{label} probe was not retained")
    probe = raw_absolute(Path(receipt.get("probeCopy", "")))
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
    log_path = receipt_path.parent / log_value.get("path", "")
    actual_log = stamp(log_path)
    require((log_value.get("bytes"), log_value.get("sha256")) ==
            (actual_log["bytes"], actual_log["sha256"]), f"{label} probe log differs")
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    require(str(probe) + "\\BEA" in log_text and
            "Processing read-only project file: /BEA.exe" in log_text and
            "SCRIPT ERROR" not in log_text, f"{label} probe log content differs")
    require(project_fields(receipt["source"]) == expected, f"{label} source differs")
    return stamp(receipt_path)


def build_scratch(generated_at: str, *, require_current_live_pre: bool) -> dict[str, Any]:
    generated_time = parse_utc(generated_at, "scratch generatedAtUtc")
    require(generated_time <= datetime.now(timezone.utc), "scratch time is in future")
    inputs = {
        "tool": require_stamp(TOOL, TOOL_STAMP, "SetPos Ghidra tool"),
        "inventoryTool": require_stamp(INVENTORY_TOOL, INVENTORY_TOOL_STAMP, "inventory tool"),
        "campaign": require_stamp(CAMPAIGN, CAMPAIGN_STAMP, "Generation 14 READY"),
        "proof": require_stamp(PROOF, PROOF_STAMP, "SetPos proof"),
        "campaignAuthority": require_stamp(
            CAMPAIGN_AUTHORITY, CAMPAIGN_AUTHORITY_STAMP, "Generation 14 authority"),
        "boundaryManifest": require_stamp(BOUNDARY, BOUNDARY_STAMP, "SetPos boundary"),
    }
    expected = baseline_project()
    predecessor = {
        "liveAuthority": require_stamp(
            SOURCE_AUTHORITY, SOURCE_AUTHORITY_STAMP, "TokenArchive live authority"),
        "postBackupManifest": require_stamp(
            SOURCE_MANIFEST, SOURCE_MANIFEST_STAMP, "TokenArchive POST manifest"),
        "postRestoreReceipt": require_stamp(
            SOURCE_RESTORE, SOURCE_RESTORE_STAMP, "TokenArchive POST restore"),
        "exactProjectContinuity": True,
    }
    if require_current_live_pre:
        require(actual_project(LIVE) == expected, "maintainer project drifted from exact PRE")
    names = ["replica-final-a", "replica-final-b", "probe-after-create-v3", "probe-post-inner-v3"]
    roots = [LANE / "scratch" / name for name in names]
    require_distinct_projects([LIVE, SOURCE_PRE, *roots])
    copies = {name: validate_copy(name, expected) for name in names}
    replicas: dict[str, Any] = {}
    evidence_times: list[datetime] = []
    for suffix, project_name in (("a", "replica-final-a"), ("b", "replica-final-b")):
        project = LANE / "scratch" / project_name
        dry = validate_run(f"replica {suffix} dry", f"replica-final-{suffix}-dry", "dry", project)
        apply = validate_run(f"replica {suffix} apply", f"replica-final-{suffix}-apply", "apply", project)
        readback = validate_run(
            f"replica {suffix} readback", f"replica-final-{suffix}-readback", "readback", project)
        inventory = validate_inventory(f"replica-final-{suffix}-inventory", project, "POST")
        copy_time = parse_utc(copies[project_name]["createdAtUtc"], f"replica {suffix} copy")
        dry_time = parse_utc(dry["completedAtUtc"], f"replica {suffix} dry")
        apply_time = parse_utc(apply["completedAtUtc"], f"replica {suffix} apply")
        readback_time = parse_utc(readback["completedAtUtc"], f"replica {suffix} readback")
        require(copy_time < dry_time < apply_time < readback_time,
                f"replica {suffix} chronology differs")
        require((LANE / "runs" / f"replica-final-{suffix}-inventory" /
                 "functions.tsv").stat().st_mtime_ns >
                (LANE / "runs" / f"replica-final-{suffix}-readback" /
                 "setpos.ready.json").stat().st_mtime_ns,
                f"replica {suffix} inventory did not follow readback")
        evidence_times.append(readback_time)
        replicas[suffix] = {"project": display_path(project), "dry": dry, "apply": apply,
                            "readback": readback, "inventory": inventory}
    for phase in ("dry", "apply", "readback"):
        a = LANE / "runs" / f"replica-final-a-{phase}"
        b = LANE / "runs" / f"replica-final-b-{phase}"
        require((a / "setpos.tsv").read_bytes() == (b / "setpos.tsv").read_bytes(),
                f"replica {phase} TSVs differ")
        require(normalize_ready(a / "setpos.ready.json") ==
                normalize_ready(b / "setpos.ready.json"),
                f"replica {phase} receipts differ beyond time/path")
    for artifact in ("functions.tsv", "program.tsv"):
        require((LANE / "runs" / "replica-final-a-inventory" / artifact).read_bytes() ==
                (LANE / "runs" / "replica-final-b-inventory" / artifact).read_bytes(),
                f"replica POST {artifact} differs")
    adverse = {
        "afterCreate": validate_adverse(
            "probe-after-create", "probe-after-create-v3", "probe-after-create-final-v3",
            "probe-after-create-final-v3-post-inventory"),
        "postInner": validate_adverse(
            "probe-post-inner", "probe-post-inner-v3", "probe-post-inner-test-v3",
            "probe-post-inner-test-v3-post-inventory"),
    }
    evidence_times.extend(datetime.fromtimestamp(
        (LANE / "runs" / name / "program.tsv").stat().st_mtime, timezone.utc)
        for name in ("probe-after-create-final-v3-post-inventory",
                     "probe-post-inner-test-v3-post-inventory"))
    require(max(evidence_times) < generated_time, "scratch authority predates evidence")
    return {
        "schema": SCHEMA, "phase": "SCRATCH_AUTHORITY", "verdict": "READY",
        "generatedAtUtc": generated_at,
        "claim": "ONE_MISSION_NATIVE_SETPOS_FUNCTION_AUTHORIZED_FOR_ONE_LIVE_APPLY",
        "author": stamp(SCRIPT), "inputs": inputs, "predecessor": predecessor,
        "copies": copies, "replicas": replicas, "adverseControls": adverse,
        "delta": {
            "functionEntry": "0x00536c70", "functionsAdded": 1,
            "name": "IScript__SetPos", "signature": POST_SIGNATURE,
            "commentBytes": 722, "bodyBytes": 42, "bodyInstructions": 17,
            "leadingNopBytes": 15, "trailingNopBytes": 6,
            "bytesChanged": 0, "instructionsChanged": 0, "dataUnitsChanged": 0,
            "referencesChanged": 0,
        },
        "authorization": {
            "liveApplyAuthorized": True, "oneMutationProcess": True,
            "separateReadbackRequired": True, "postBackupAndRestoreRequired": True,
            "additionalClaimsAuthorized": False,
        },
        "limitations": [
            "The promotion records a C1_STATIC function contract, not runtime vector values or target-side writes.",
            "The two callee-cleaned stack slots unused by the body retain bounded neutral names.",
            "No executable byte, instruction, data-unit, or reference mutation is authorized.",
        ],
    }


def validate_backup(manifest_path: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
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
    pre_manifest = validate_backup(PRE_MANIFEST, baseline, "PRE live backup")
    pre_restore = validate_restore(
        baseline, PRE_RESTORE, LANE / "backups" / "pre-live-restore-drill", 8348,
        "PRE restore")
    live_dry = validate_run(
        "live immediate PRE", "live-preapply-dry", "dry", LIVE, require_read_only=True)
    live_pre_inventory = validate_inventory("live-preapply-inventory", LIVE, "PRE")
    live_apply = validate_run("live apply", "live-apply", "apply", LIVE)
    live_readback = validate_run("live readback", "live-readback", "readback", LIVE)
    live_inventory = validate_inventory("live-inventory", LIVE, "POST")
    for phase in ("apply", "readback"):
        live = LANE / "runs" / f"live-{phase}"
        scratch_root = LANE / "runs" / f"replica-final-a-{phase}"
        require((live / "setpos.tsv").read_bytes() ==
                (scratch_root / "setpos.tsv").read_bytes(),
                f"live {phase} differs from scratch")
        require(normalize_ready(live / "setpos.ready.json") ==
                normalize_ready(scratch_root / "setpos.ready.json"),
                f"live {phase} receipt differs beyond time/path")
    for artifact in ("functions.tsv", "program.tsv"):
        require((LANE / "runs" / "live-inventory" / artifact).read_bytes() ==
                (LANE / "runs" / "replica-final-a-inventory" / artifact).read_bytes(),
                f"live POST {artifact} differs from scratch")
    post_project = actual_project(LIVE)
    post_manifest = validate_backup(POST_MANIFEST, post_project, "POST live backup")
    post_restore = validate_restore(
        post_project, POST_RESTORE, LANE / "backups" / "post-live-restore-drill", 8349,
        "POST restore")
    require_distinct_projects([LIVE, PRE_BACKUP, POST_BACKUP])
    scratch_time = parse_utc(saved_scratch["generatedAtUtc"], "scratch time")
    pre_backup_time = parse_utc(load_json(PRE_MANIFEST)["createdAtUtc"], "PRE backup time")
    pre_restore_time = parse_utc(load_json(PRE_RESTORE)["verifiedAtUtc"], "PRE restore time")
    dry_time = parse_utc(live_dry["completedAtUtc"], "live PRE dry time")
    apply_time = parse_utc(live_apply["completedAtUtc"], "live apply time")
    readback_time = parse_utc(live_readback["completedAtUtc"], "live readback time")
    post_backup_time = parse_utc(load_json(POST_MANIFEST)["createdAtUtc"], "POST backup time")
    post_restore_time = parse_utc(load_json(POST_RESTORE)["verifiedAtUtc"], "POST restore time")
    require(pre_backup_time < pre_restore_time and
            max(scratch_time, pre_restore_time) < dry_time < apply_time < readback_time <
            post_backup_time < post_restore_time < generated_time,
            "scratch/backup/live chronology differs")
    return {
        "schema": SCHEMA, "phase": "LIVE_PROMOTED", "verdict": "READY",
        "generatedAtUtc": generated_at,
        "claim": "MISSION_NATIVE_SETPOS_PROMOTED_AND_SEPARATELY_READ_BACK",
        "author": stamp(SCRIPT), "tool": stamp(TOOL),
        "scratchAuthority": stamp(SCRATCH_READY),
        "live": {
            "project": str(LIVE.resolve()), "preBackupManifest": pre_manifest,
            "preRestoreReceipt": pre_restore, "immediatePreDry": live_dry,
            "immediatePreInventory": live_pre_inventory, "apply": live_apply,
            "readback": live_readback, "postInventory": live_inventory,
            "postBackupManifest": post_manifest, "postRestoreReceipt": post_restore,
        },
        "result": {
            "functionEntry": "0x00536c70", "functionName": "IScript__SetPos",
            "functionsAdded": 1, "bodyBytes": 42, "bodyInstructions": 17,
            "separateReadbackPassed": True, "recoverablePreBackupPassed": True,
            "recoverablePostBackupPassed": True, "bytesChanged": 0,
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
        partial.replace(path)
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
        publish(SCRATCH_READY, payload)
        result = verify_saved(
            SCRATCH_READY, lambda value: build_scratch(value, require_current_live_pre=True))
        print(f"MISSION_SETPOS_SCRATCH_AUTHORITY_READY sha256={result['sha256']}")
    elif args.command == "verify-scratch":
        result = verify_saved(
            SCRATCH_READY, lambda value: build_scratch(value, require_current_live_pre=False))
        print(f"MISSION_SETPOS_SCRATCH_AUTHORITY_VERIFIED sha256={result['sha256']}")
    elif args.command == "seal-live":
        payload = build_live(utc_now())
        publish(LIVE_READY, payload)
        result = verify_saved(LIVE_READY, build_live)
        print(f"MISSION_SETPOS_LIVE_PROMOTION_READY sha256={result['sha256']}")
    else:
        result = verify_saved(LIVE_READY, build_live)
        print(f"MISSION_SETPOS_LIVE_PROMOTION_VERIFIED sha256={result['sha256']}")
    return 0


AUTHOR_START = stamp(SCRIPT)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProofError as exc:
        print(f"MISSION_SETPOS_PROMOTION_REFUSED {exc}")
        raise SystemExit(10)
