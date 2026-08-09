#!/usr/bin/env python3
"""Fail-closed authority for the Generation 14 TokenArchive Ghidra promotion.

This owner never mutates Ghidra.  It validates the exact two-replica scratch
ceremony and, after a separately executed live apply/readback/backup ceremony,
publishes the bounded live-promotion receipt.  The historical compiler failures
and scratch replicas are evidence only; neither may select live authority.
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
LANE = REPO / "local-lab" / "ghidra-tokenarchive-dispatch-live-promotion-20260809-v1"
LIVE = Path(r"C:\Users\david\Ghidra\Projects")
PRISTINE = REPO / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
TOOL = REPO / "tools" / "GhidraApplyTokenArchiveDispatchData.java"
OPEN_PROBE_TOOL = REPO / "tools" / "GhidraProjectOpenProbe.java"
ANALYZE_HEADLESS = Path(
    r"D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC\support\analyzeHeadless.bat"
)

CAMPAIGN = (
    REPO / "local-lab" / "re-campaign-incident-recovery-20260808-v1"
    / "generation-14-tokenarchive-dispatch-reproof-v1" / "campaign.ready.json"
)
PROOF = REPO / "local-lab" / "tokenarchive-dispatch-table-reproof-20260809-v1" / "proof.ready.json"
CAMPAIGN_AUTHORITY = (
    REPO / "local-lab" / "re-campaign-incident-recovery-20260808-v1"
    / "generation-14-tokenarchive-dispatch-reproof-authority.ready.json"
)
PREDECESSOR_AUTHORITY = (
    REPO / "local-lab" / "ghidra-damage-hit-semantic-live-promotion-20260809-v1"
    / "promotion" / "promotion.ready.json"
)
PREDECESSOR_POST_MANIFEST = (
    REPO / "local-lab" / "ghidra-damage-hit-semantic-live-promotion-20260809-v1"
    / "backups" / "post-live" / "backup_manifest.json"
)

PRE_BACKUP = LANE / "backups" / "pre-live"
PRE_MANIFEST = PRE_BACKUP / "backup_manifest.json"
PRE_RESTORE = LANE / "pre-live-restore.ready.json"
PRE_FUNCTIONS = LANE / "pre-observation" / "functions.tsv"
PRE_PROGRAM = LANE / "pre-observation" / "program.tsv"
LIVE_PRE_INSPECT = LANE / "live-preapply-inspect.json"
LIVE_POST_INSPECT = LANE / "live-postapply-inspect.json"
LIVE_PRE_RUN = LANE / "runs" / "live-preapply-adversarial-readonly"
SCRATCH_READY = LANE / "promotion" / "scratch-authority.ready.json"
LIVE_READY = LANE / "promotion" / "promotion.ready.json"

SCHEMA = "bea.ghidra.tokenarchive-dispatch-promotion-authority.v1"
INSPECT_SCHEMA = "bea.ghidra.tokenarchive-dispatch-project-inspection.v1"
PROGRAM_SHA = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
TOOL_STAMP = (38_766, "bb0f184498f47c11c56279d13368c1366f98227e05c4e44a4ec04ab61e07fc43")
CAMPAIGN_STAMP = (16_930, "9864424def44034a5a5e9a68814ce111076182ad7ea898c9d0040d888c92f32b")
PROOF_STAMP = (11_257, "182d302e45ff42b389b54c85f92576864f9ef9dc30887ee5fc6db86b307faf7f")
CAMPAIGN_AUTHORITY_STAMP = (8_215, "83a5544bdde805762b01983171c336826ea62a8b2dd8be94109bef959560ff72")
PREDECESSOR_AUTHORITY_STAMP = (4_453, "f13caf898ee760e3af8bbe6634d595cfec4f765897dac0b572d713bed82492cd")
PREDECESSOR_POST_MANIFEST_STAMP = (
    7_589, "7a2797143f306c528f2ef6ef45701abd5b253d12900eca5d5528c61f57bcad8b"
)
PRE_MANIFEST_STAMP = (7_589, "48891a91b779ee329f81ad39fea710dc2072a5d79d960429cb0259b50b1a1020")
PRE_RESTORE_STAMP = (6_003, "637bf1a5479c1b2702b24feb1316c2ef0f13158a1842868adecf078b1ebf4177")
COMPILE_DRY_LOG_STAMP = (5_412, "e39d8c2c6b8ad6b2ba9c950eba0924ecb4ff72e4e3e5dfa7f99548b718f7f15b")

PRE_FUNCTIONS_STAMP = (7_051_668, "075165bae3616dda0adf534625db612990daee9974b3fc85429d3b5b408ee979")
PRE_PROGRAM_STAMP = (1_267, "e1724ff7ae231326cd4b25a6c8d8d0d53ebb844a509541c402cdd64436474029")
POST_FUNCTIONS_STAMP = PRE_FUNCTIONS_STAMP
POST_PROGRAM_STAMP = (1_267, "fce597559bd1baf48d0c2759ef89aa277ba5cc0dbe6ae9a8071df5e7562adb4e")
PHASE_TSV_STAMPS = {
    "dry": (1_032, "23d314394e07e8f2a7dda170186c6f1ee629177e8f3e97ed88a185cd5ce20c1f"),
    "apply": (1_234, "b3314e8436795ccdd6f9458cbf91b24a199b6a38e3342c98c03528573b477659"),
    "readback": (1_249, "8785c1774ea53adee718b2dc0ec8f1d91c2dce048f383d8c315ece6c836aca18"),
}

ADDRESSES = ["0x004f5ac5", "0x004f5ac8", "0x004f5ae4", "0x004f5b61", "0x004f583b"]
ROLES = ["ALIGN_PREFIX", "DISPATCH_POINTERS", "TOKEN_KIND_INDEX", "ALIGN_SUFFIX", "DISPATCH_CONSUMER"]
POST_LABELS = {
    "0x004f5ac5": "CTokenArchive__ReadNextToken_DispatchAlignPrefix",
    "0x004f5ac8": "CTokenArchive__ReadNextToken_DispatchTargets",
    "0x004f5ae4": "CTokenArchive__ReadNextToken_TokenKindByIndex",
    "0x004f5b61": "CTokenArchive__ReadNextToken_DispatchAlignSuffix",
    "0x004f583b": "",
}
PRE_LABELS = {
    "0x004f5ac5": "",
    "0x004f5ac8": "switchdataD_004f5ac8",
    "0x004f5ae4": "switchdataD_004f5ae4",
    "0x004f5b61": "",
    "0x004f583b": "",
}
PRE_PROGRAM_METRICS = {
    "functions": "8124", "instructions": "549872",
    "instructionLayoutSha256": "ba8b9d6380c2acb63f625b95d6a08d3ae4df209a9da0fa41ae4c13c86e3f4ba2",
    "definedData": "48585", "definedDataSha256": "3b87eb91228e20c1d627318cc2563811043c1500af1497575ab128e7edf6e9e3",
    "undefinedData": "3912345", "symbolsUserDefined": "6000", "symbolsAnalysis": "18006",
    "symbolsImported": "907", "symbolsDefaultOther": "61694",
    "nonFunctionSymbolsSha256": "632f89d973cdc607e2223dc2f1eb9aa2040f28264fbf66f9a4a3e5671c2261ea",
    "references": "234357", "referencesSha256": "704d5f045abfdf899761990b23494bf78f4d214bc0f55785184ec431b41abccf",
    "comments": "9094", "commentsSha256": "fafe62e4cfe9444afd88f9f32c49a8bcaa2c7b752f9001df9c8c9feb25293971",
}
POST_PROGRAM_METRICS = PRE_PROGRAM_METRICS | {
    "symbolsUserDefined": "6004",
    "nonFunctionSymbolsSha256": "3e9936f251588865a77b62bdf577c110a7346e57c0e5a234e1feab9ab41622ac",
    "comments": "9099",
    "commentsSha256": "ee042b0aa963d6a64d2a5e9dbedb8bbd201acea83359d10e5dc3126ea41be2fd",
}


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


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO).as_posix()
    except ValueError:
        return str(resolved)


def raw_absolute(path: Path) -> Path:
    return Path(os.path.abspath(path))


def assert_plain_path(path: Path, label: str, *, directory: bool | None = None) -> Path:
    raw = raw_absolute(path)
    require(raw.exists(), f"{label} is absent: {raw}")
    chain = list(reversed(raw.parents)) + [raw]
    for part in chain:
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
    stat_result = resolved.stat()
    return {"path": display_path(resolved), "bytes": stat_result.st_size, "sha256": sha256_file(resolved)}


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


def project_fields(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "projectName": value.get("projectName"),
        "fileCount": value.get("fileCount"),
        "totalBytes": value.get("totalBytes"),
        "structurallyComplete": value.get("structurallyComplete"),
        "files": value.get("files"),
    }


def actual_project(root: Path) -> dict[str, Any]:
    assert_plain_tree(root, f"project {root}")
    files: list[dict[str, Any]] = []
    total = 0
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == "backup_manifest.json":
            continue
        relative = path.relative_to(root).as_posix()
        size = path.stat().st_size
        files.append({"relative_path": relative, "sha256": sha256_file(path), "size": size})
        total += size
    return {
        "projectName": "BEA", "fileCount": len(files), "totalBytes": total,
        "structurallyComplete": any(row["relative_path"] == "BEA.gpr" for row in files)
            and any(row["relative_path"].startswith("BEA.rep/") for row in files),
        "files": files,
    }


def pre_project() -> dict[str, Any]:
    require_stamp(PRE_MANIFEST, PRE_MANIFEST_STAMP, "PRE backup manifest")
    receipt = load_json(PRE_MANIFEST)
    require(receipt.get("schemaVersion") == "onslaught-ghidra-project-backup.v2",
            "PRE backup schema differs")
    require(receipt.get("sourceStable") is True, "PRE backup source was unstable")
    comparison = receipt.get("copyComparison", {})
    require(comparison.get("matches") is True, "PRE backup comparison failed")
    for field in ("missingCount", "extraCount", "sizeDiffCount", "hashDiffCount"):
        require(comparison.get(field) == 0, f"PRE backup {field} is nonzero")
    source = project_fields(receipt["source"])
    destination = project_fields(receipt["destination"])
    require(source == destination, "PRE backup source/destination inventories differ")
    require(actual_project(PRE_BACKUP) == destination, "PRE backup bytes differ from manifest")
    require(source["fileCount"] == 19 and source["totalBytes"] == 186_469_253,
            "PRE backup aggregate identity differs")
    return source


def validate_predecessor(expected: Mapping[str, Any]) -> dict[str, Any]:
    authority = require_stamp(PREDECESSOR_AUTHORITY, PREDECESSOR_AUTHORITY_STAMP,
                              "Damage/Hit predecessor authority")
    manifest_stamp = require_stamp(PREDECESSOR_POST_MANIFEST,
                                   PREDECESSOR_POST_MANIFEST_STAMP,
                                   "Damage/Hit POST manifest")
    manifest = load_json(PREDECESSOR_POST_MANIFEST)
    require(project_fields(manifest["source"]) == expected,
            "TokenArchive PRE is not exact Damage/Hit POST source")
    require(project_fields(manifest["destination"]) == expected,
            "TokenArchive PRE is not exact Damage/Hit POST backup")
    return {"liveAuthority": authority, "postBackupManifest": manifest_stamp,
            "exactProjectContinuity": True}


def validate_restore(expected: Mapping[str, Any], receipt_path: Path, label: str) -> dict[str, Any]:
    receipt = load_json(receipt_path)
    require(receipt.get("schemaVersion") == "onslaught-ghidra-project-backup.v2",
            f"{label} schema differs")
    require(receipt.get("sourceStable") is True, f"{label} source was unstable")
    comparison = receipt.get("copyComparison", {})
    require(comparison.get("matches") is True, f"{label} comparison failed")
    for field in ("missingCount", "extraCount", "sizeDiffCount", "hashDiffCount"):
        require(comparison.get(field) == 0, f"{label} copy {field} is nonzero")
    for field in ("missing", "extra", "sizeDifferences", "hashDifferences"):
        require(comparison.get(field) == [], f"{label} copy {field} is nonempty")
    require(receipt.get("probeCopyDisposition") == "RETAINED_AT_VERIFICATION",
            f"{label} probe copy was not retained")
    probe = raw_absolute(Path(receipt.get("probeCopy", "")))
    expected_probe_parent = (
        LANE / "backups" /
        ("pre-live-restore-drill" if receipt_path == PRE_RESTORE else "post-live-restore-drill")
    ).resolve()
    require(probe.parent.resolve() == expected_probe_parent,
            f"{label} probe root differs")
    require(probe.name.startswith("BEA-open-probe-") and len(probe.name) > 20,
            f"{label} probe name differs")
    require(actual_project(probe) == expected, f"{label} retained probe bytes differ")
    readonly = receipt.get("readonlyOpen", {})
    require(readonly.get("opened") is True and readonly.get("contentStable") is True,
            f"{label} read-only open failed")
    post = readonly.get("postOpenComparison", {})
    require(post.get("matches") is True, f"{label} changed while opened")
    for field in ("missingCount", "extraCount", "sizeDiffCount", "hashDiffCount"):
        require(post.get(field) == 0, f"{label} post-open {field} is nonzero")
    for field in ("missing", "extra", "sizeDifferences", "hashDifferences"):
        require(post.get(field) == [], f"{label} post-open {field} is nonempty")
    expected_command = [
        str(ANALYZE_HEADLESS), str(probe), "BEA", "-process", "BEA.exe",
        "-readOnly", "-noanalysis", "-scriptPath", str((REPO / "tools").resolve()),
        "-postScript", OPEN_PROBE_TOOL.name, "BEA.exe", PROGRAM_MD5, PROGRAM_SHA,
    ]
    require(readonly.get("commandArgv") == expected_command,
            f"{label} read-only command differs")
    require(readonly.get("exitCode") == 0, f"{label} read-only exit differs")
    require(readonly.get("expectedProgramMd5") == PROGRAM_MD5 and
            readonly.get("expectedProgramSha256") == PROGRAM_SHA,
            f"{label} expected program identity differs")
    require(readonly.get("observedProgramName") == "BEA.exe" and
            readonly.get("observedProgramMd5") == PROGRAM_MD5 and
            readonly.get("observedProgramSha256") == PROGRAM_SHA and
            readonly.get("observedFunctionCount") == 8348,
            f"{label} observed program identity differs")
    log_stamp = readonly.get("probeLog", {})
    expected_log_name = receipt_path.name.removesuffix(".json") + ".open-probe.log"
    require(log_stamp.get("path") == expected_log_name,
            f"{label} probe log path differs")
    log_path = receipt_path.parent / expected_log_name
    actual_log = stamp(log_path)
    require((log_stamp.get("bytes"), log_stamp.get("sha256")) ==
            (actual_log["bytes"], actual_log["sha256"]),
            f"{label} probe log stamp differs")
    log_text = log_path.read_text(encoding="utf-8", errors="replace")
    require(str(probe) + "\\BEA" in log_text and
            "REPORT: Processing read-only project file: /BEA.exe" in log_text and
            f"GHIDRA_PROJECT_OPEN_PROBE_OK program=BEA.exe md5={PROGRAM_MD5} "
            f"sha256={PROGRAM_SHA} functions=8348" in log_text and
            "SCRIPT ERROR" not in log_text,
            f"{label} probe log content differs")
    require(project_fields(receipt["source"]) == expected, f"{label} source differs")
    return stamp(receipt_path)


def validate_copy(name: str, expected: Mapping[str, Any]) -> dict[str, Any]:
    root = LANE / "scratch" / name
    assert_plain_tree(root, f"scratch {name}")
    receipt_path = root / "backup_manifest.json"
    receipt = load_json(receipt_path)
    require(receipt.get("schemaVersion") == "onslaught-ghidra-project-backup.v2",
            f"{name} copy schema differs")
    require(receipt.get("sourceStable") is True, f"{name} source was unstable")
    comparison = receipt.get("copyComparison", {})
    require(comparison.get("matches") is True, f"{name} copy comparison failed")
    for field in ("missingCount", "extraCount", "sizeDiffCount", "hashDiffCount"):
        require(comparison.get(field) == 0, f"{name} copy {field} is nonzero")
    require(project_fields(receipt["source"]) == expected, f"{name} copy source differs")
    require(project_fields(receipt["destination"]) == expected, f"{name} copy destination differs")
    return {"manifest": stamp(receipt_path), "project": display_path(root),
            "createdAtUtc": receipt["createdAtUtc"]}


def require_distinct_projects(roots: Sequence[Path]) -> None:
    resolved = [assert_plain_path(root, f"project root {root}", directory=True) for root in roots]
    require(len(set(resolved)) == len(resolved), "project roots are not distinct")
    for index, left in enumerate(resolved):
        for right in resolved[index + 1:]:
            require(not os.path.samefile(left, right), f"project roots alias: {left} / {right}")


def require_exact_files(root: Path, names: set[str], label: str) -> None:
    actual = {path.name for path in root.iterdir() if path.is_file()}
    require(actual == names, f"{label} file set differs: {sorted(actual)}")


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def validate_phase_tsv(path: Path, phase: str) -> None:
    require_stamp(path, PHASE_TSV_STAMPS[phase], f"{phase} TokenArchive TSV")
    header, rows = read_tsv(path)
    require(header == ["address", "role", "mode", "state", "primarySymbol",
                       "symbolSource", "dataLength", "components", "bytesSha256",
                       "commentBytes", "commentSha256"], f"{phase} TSV header differs")
    require([row["address"] for row in rows] == ADDRESSES, f"{phase} address order differs")
    require([row["role"] for row in rows] == ROLES, f"{phase} roles differ")
    post = phase in {"apply", "readback"}
    expected_labels = POST_LABELS if post else PRE_LABELS
    for row in rows:
        require(row["mode"] == phase, f"{phase} mode differs at {row['address']}")
        require(row["state"] == ("POST" if post else "PRE"),
                f"{phase} state differs at {row['address']}")
        require(row["primarySymbol"] == expected_labels[row["address"]],
                f"{phase} primary differs at {row['address']}")
        expected_source = "USER_DEFINED" if post and row["address"] != "0x004f583b" else (
            "ANALYSIS" if not post and row["address"] in {"0x004f5ac8", "0x004f5ae4"} else "")
        require(row["symbolSource"] == expected_source,
                f"{phase} source differs at {row['address']}")
        require((row["commentBytes"] != "0") is post,
                f"{phase} comment state differs at {row['address']}")


def normalize_run_ready(path: Path) -> dict[str, Any]:
    value = copy.deepcopy(load_json(path))
    value.pop("completedAtUtc")
    value["output"]["path"] = "<lane-output>"
    return value


def validate_run(label: str, run_name: str, phase: str, project: Path,
                 *, inventory: bool = False, log_name: str = "headless.log",
                 exact_files: bool = True) -> dict[str, Any]:
    root = LANE / "runs" / run_name
    tsv = root / "tokenarchive.tsv"
    ready_path = root / "tokenarchive.ready.json"
    log = root / log_name
    expected_files = {log_name, "tokenarchive.tsv", "tokenarchive.ready.json"}
    if inventory:
        expected_files |= {"functions.tsv", "program.tsv"}
    if exact_files:
        require_exact_files(root, expected_files, label)
    validate_phase_tsv(tsv, phase)
    ready = load_json(ready_path)
    expected_keys = {
        "schema", "completedAtUtc", "mode", "state", "tool",
        "campaignReadySha256", "proofReadySha256", "authorityReadySha256",
        "program", "partition", "output", "commitRequested",
        "nestedEndReturnedCommitted", "loadedStateVerified",
        "semanticTokenKindsAuthorized", "functionOrBoundaryMutationAuthorized",
        "authorityBoundary",
    }
    require(set(ready) == expected_keys, f"{label} READY shape differs")
    completed = parse_utc(ready["completedAtUtc"], f"{label} completedAtUtc")
    require(ready["schema"] == "bea.ghidra.tokenarchive-dispatch-structure.v1",
            f"{label} schema differs")
    require(ready["mode"] == phase and ready["state"] == ("PRE" if phase == "dry" else "POST"),
            f"{label} mode/state differs")
    require(Path(ready["tool"]["path"]).resolve() == TOOL.resolve(), f"{label} tool path differs")
    require((ready["tool"]["bytes"], ready["tool"]["sha256"]) == TOOL_STAMP,
            f"{label} tool identity differs")
    require(ready["campaignReadySha256"] == CAMPAIGN_STAMP[1], f"{label} campaign differs")
    require(ready["proofReadySha256"] == PROOF_STAMP[1], f"{label} proof differs")
    require(ready["authorityReadySha256"] == CAMPAIGN_AUTHORITY_STAMP[1],
            f"{label} campaign authority differs")
    require(ready["program"] == {
        "name": "BEA.exe", "md5": PROGRAM_MD5, "sha256": PROGRAM_SHA,
        "functions": 8124, "instructions": 549872,
    }, f"{label} program identity differs")
    require(ready["partition"] == {
        "wholeBytes": 171, "dataBytes": 153, "alignmentBytes": 18,
        "pointerTargets": 7, "indexBytes": 125, "indexMax": 6,
        "preExistingDefinedDataUnitsPreserved": 132,
    }, f"{label} partition differs")
    require(Path(ready["output"]["path"]).resolve() == tsv.resolve(),
            f"{label} output path differs")
    require((ready["output"]["bytes"], ready["output"]["sha256"]) == PHASE_TSV_STAMPS[phase],
            f"{label} output stamp differs")
    require(ready["commitRequested"] is (phase == "apply"), f"{label} commit flag differs")
    require(ready["nestedEndReturnedCommitted"] is False, f"{label} nested result differs")
    require(ready["loadedStateVerified"] is (phase == "readback"),
            f"{label} loaded-state flag differs")
    require(ready["semanticTokenKindsAuthorized"] is False,
            f"{label} self-authorized token semantics")
    require(ready["functionOrBoundaryMutationAuthorized"] is False,
            f"{label} self-authorized function mutation")
    require(ready["authorityBoundary"] == "requires_external_two_replica_or_separate_live_readback",
            f"{label} authority boundary differs")
    text = log.read_text(encoding="utf-8", errors="replace")
    markers = {
        "dry": "TOKENARCHIVE_DISPATCH_DRY_COMPLETE mutations=0",
        "apply": "TOKENARCHIVE_DISPATCH_APPLY_COMPLETE data_units=132 labels=4 reopen_verification_required=true",
        "readback": "TOKENARCHIVE_DISPATCH_READBACK_COMPLETE data_units=132 labels=4",
    }
    require(markers[phase] in text and "REPORT SCRIPT ERROR" not in text,
            f"{label} did not close cleanly")
    require(str(project.resolve()) + "\\BEA" in text, f"{label} opened the wrong project")
    require(str(tsv.resolve()) in text and str(ready_path.resolve()) in text,
            f"{label} log does not bind exact outputs")
    require(f"'{phase}'" in text, f"{label} log does not bind exact mode")
    if phase == "apply":
        require("Save succeeded for processed file: /BEA.exe" in text,
                f"{label} save did not complete")
    else:
        require("Processing read-only project file: /BEA.exe" in text,
                f"{label} was not read-only")
    result = {"tsv": stamp(tsv), "ready": stamp(ready_path), "log": stamp(log),
              "completedAtUtc": ready["completedAtUtc"]}
    if inventory:
        result["inventory"] = validate_inventory(root, "POST" if phase == "readback" else "PRE")
    return result


def parse_program(path: Path) -> dict[str, str]:
    rows = path.read_text(encoding="utf-8").splitlines()
    require(rows and rows[0] == "metric\tvalue", f"program header differs: {path}")
    result: dict[str, str] = {}
    for row in rows[1:]:
        key, value = row.split("\t", 1)
        require(key not in result, f"duplicate program metric: {key}")
        result[key] = value
    return result


def validate_inventory(root: Path, state: str) -> dict[str, Any]:
    functions = root / "functions.tsv"
    program = root / "program.tsv"
    expected_functions = POST_FUNCTIONS_STAMP if state == "POST" else PRE_FUNCTIONS_STAMP
    expected_program = POST_PROGRAM_STAMP if state == "POST" else PRE_PROGRAM_STAMP
    require_stamp(functions, expected_functions, f"{state} functions")
    require_stamp(program, expected_program, f"{state} program")
    metrics = parse_program(program)
    require(metrics["programName"] == "BEA.exe" and metrics["executableSHA256"] == PROGRAM_SHA,
            f"{state} inventory specimen differs")
    expected_metrics = POST_PROGRAM_METRICS if state == "POST" else PRE_PROGRAM_METRICS
    for key, value in expected_metrics.items():
        require(metrics.get(key) == value, f"{state} program metric differs: {key}")
    if state == "POST":
        pre_metrics = parse_program(PRE_PROGRAM)
        changed = {key for key in metrics if metrics.get(key) != pre_metrics.get(key)}
        require(changed == {"symbolsUserDefined", "nonFunctionSymbolsSha256",
                            "comments", "commentsSha256"},
                f"POST program changed unrelated metrics: {sorted(changed)}")
    return {"functions": stamp(functions), "program": stamp(program)}


def validate_probe(name: str, project: Path) -> dict[str, Any]:
    failure_root = LANE / "runs" / name
    require_exact_files(failure_root, {"headless.log"}, name)
    log = failure_root / "headless.log"
    text = log.read_text(encoding="utf-8", errors="replace")
    common = [
        "TOKENARCHIVE_DISPATCH_PREFLIGHT_OK data_units=132 labels=4",
        "TOKENARCHIVE_DISPATCH_MUTATION_TAINTED mode=",
        "REPORT SCRIPT ERROR",
        "Save succeeded for processed file: /BEA.exe",
    ]
    specific = {
        "probe-after-one": [
            "TOKENARCHIVE_DISPATCH_FORCED_AFTER_ONE_FAILURE rollback_required=true",
            "recovery=RESTORE_VERIFIED_SCRATCH_BASE",
            "intentional TokenArchive dispatch after-one rollback probe",
        ],
        "probe-post-inner": [
            "TOKENARCHIVE_DISPATCH_COMPENSATING_PRE_RESTORE_COMPLETE",
            "TOKENARCHIVE_DISPATCH_FORCED_POST_INNER_FAILURE pre_restored=true",
            "recovery=COMPENSATING_PRE_RESTORE_VERIFIED",
            "intentional TokenArchive dispatch post-inner rollback probe",
        ],
    }[name]
    for marker in common + specific:
        require(marker in text, f"{name} log lacks marker: {marker}")
    require(str(project.resolve()) + "\\BEA" in text, f"{name} opened wrong project")
    require(not (failure_root / "tokenarchive.tsv").exists(), f"{name} published success TSV")
    require(not (failure_root / "tokenarchive.ready.json").exists(), f"{name} published success READY")
    post_name = f"{name}-post-inventory"
    post = validate_run(name + " post-failure PRE", post_name, "dry", project, inventory=True)
    require(post["inventory"]["functions"]["sha256"] == PRE_FUNCTIONS_STAMP[1],
            f"{name} functions did not restore")
    require(post["inventory"]["program"]["sha256"] == PRE_PROGRAM_STAMP[1],
            f"{name} program did not restore")
    return {"failureLog": stamp(log), "postFailurePre": post,
            "successArtifactsAbsent": True, "preStateRestoredExactly": True,
            "wrapperExitCodeAuthoritative": False,
            "scriptFailureAndSeparatePreReadbackAuthoritative": True}


def validate_compile_dry() -> dict[str, Any]:
    root = LANE / "runs" / "compile-dry"
    success_log = root / "headless-v6.log"
    require_stamp(success_log, COMPILE_DRY_LOG_STAMP, "final compile/dry log")
    validate_phase_tsv(root / "tokenarchive.tsv", "dry")
    text = success_log.read_text(encoding="utf-8", errors="replace")
    require("TOKENARCHIVE_DISPATCH_DRY_COMPLETE mutations=0" in text,
            "final compile/dry success marker absent")
    require("REPORT SCRIPT ERROR" not in text, "final compile/dry contains script error")
    failures = []
    for name in ("headless.log", "headless-v2.log", "headless-v3.log",
                 "headless-v4.log", "headless-v5.log"):
        path = root / name
        failure_text = path.read_text(encoding="utf-8", errors="replace")
        require("REPORT SCRIPT ERROR" in failure_text, f"historical failed log lacks error: {name}")
        failures.append({"artifact": stamp(path), "admitted": False,
                         "disposition": "FAILED_PRECONDITION_OR_COMPILATION_ATTEMPT"})
    return {"successfulFinalLog": stamp(success_log), "dryTsv": stamp(root / "tokenarchive.tsv"),
            "dryReady": stamp(root / "tokenarchive.ready.json"), "failedAttempts": failures}


def validate_inspection(path: Path, expected: Mapping[str, Any], phase: str) -> dict[str, Any]:
    value = load_json(path)
    require(set(value) == {"schema", "createdAtUtc", "phase", "project", "manifest"},
            f"{phase} inspection shape differs")
    parse_utc(value["createdAtUtc"], f"{phase} inspection time")
    require(value["schema"] == INSPECT_SCHEMA and value["phase"] == phase,
            f"{phase} inspection identity differs")
    require(value["project"] == str(LIVE.resolve()), f"{phase} inspection project differs")
    require(value["manifest"] == expected, f"{phase} inspection manifest differs")
    return stamp(path)


def build_scratch(generated_at: str, *, require_current_live_pre: bool = True) -> dict[str, Any]:
    generated_time = parse_utc(generated_at, "generatedAtUtc")
    require(generated_time <= datetime.now(timezone.utc),
            "scratch generatedAtUtc is in the future")
    specimen = require_stamp(PRISTINE, (2_506_752, PROGRAM_SHA), "pristine specimen")
    tool = require_stamp(TOOL, TOOL_STAMP, "TokenArchive Ghidra tool")
    campaign = require_stamp(CAMPAIGN, CAMPAIGN_STAMP, "Generation 14 READY")
    proof = require_stamp(PROOF, PROOF_STAMP, "TokenArchive proof")
    campaign_authority = require_stamp(CAMPAIGN_AUTHORITY, CAMPAIGN_AUTHORITY_STAMP,
                                       "Generation 14 authority")
    expected = pre_project()
    predecessor = validate_predecessor(expected)
    restore = validate_restore(expected, PRE_RESTORE, "PRE restore")
    require_stamp(PRE_RESTORE, PRE_RESTORE_STAMP, "PRE restore receipt")
    require_stamp(PRE_FUNCTIONS, PRE_FUNCTIONS_STAMP, "PRE functions")
    require_stamp(PRE_PROGRAM, PRE_PROGRAM_STAMP, "PRE program")
    live_inspect = validate_inspection(LIVE_PRE_INSPECT, expected, "PRE")
    if require_current_live_pre:
        require(actual_project(LIVE) == expected, "maintainer project drifted from PRE backup")
    names = ["replica-a", "replica-b", "probe-after-one", "probe-post-inner"]
    roots = [LANE / "scratch" / name for name in names]
    require_distinct_projects([LIVE, PRE_BACKUP, *roots])
    copies = {name: validate_copy(name, expected) for name in names}
    replicas: dict[str, Any] = {}
    latest_evidence_times: list[datetime] = []
    for name in ("replica-a", "replica-b"):
        project = LANE / "scratch" / name
        dry = validate_run(name + " dry", f"{name}-dry", "dry", project)
        apply = validate_run(name + " apply", f"{name}-apply", "apply", project)
        readback = validate_run(name + " readback", f"{name}-readback", "readback",
                                project, inventory=True)
        copy_time = parse_utc(copies[name]["createdAtUtc"], f"{name} copy time")
        dry_time = parse_utc(dry["completedAtUtc"], f"{name} dry time")
        apply_time = parse_utc(apply["completedAtUtc"], f"{name} apply time")
        readback_time = parse_utc(readback["completedAtUtc"], f"{name} readback time")
        require(copy_time < dry_time < apply_time < readback_time,
                f"{name} chronology differs")
        latest_evidence_times.append(readback_time)
        replicas[name] = {"project": display_path(project), "dry": dry,
                          "apply": apply, "readback": readback}
    for phase in ("dry", "apply", "readback"):
        a = LANE / "runs" / f"replica-a-{phase}"
        b = LANE / "runs" / f"replica-b-{phase}"
        require((a / "tokenarchive.tsv").read_bytes() == (b / "tokenarchive.tsv").read_bytes(),
                f"replica {phase} TSVs differ")
        require(normalize_run_ready(a / "tokenarchive.ready.json") ==
                normalize_run_ready(b / "tokenarchive.ready.json"),
                f"replica {phase} receipts differ beyond time/path")
    for artifact in ("functions.tsv", "program.tsv"):
        require((LANE / "runs/replica-a-readback" / artifact).read_bytes() ==
                (LANE / "runs/replica-b-readback" / artifact).read_bytes(),
                f"replica POST {artifact} differs")
    adverse = {
        name: validate_probe(name, LANE / "scratch" / name)
        for name in ("probe-after-one", "probe-post-inner")
    }
    latest_evidence_times.extend(
        parse_utc(value["postFailurePre"]["completedAtUtc"], f"{name} post-failure time")
        for name, value in adverse.items()
    )
    latest_evidence_times.extend([
        parse_utc(load_json(LIVE_PRE_INSPECT)["createdAtUtc"], "live PRE inspection time"),
        parse_utc(load_json(LANE / "pre-observation/tokenarchive.ready.json")["completedAtUtc"],
                  "PRE observation time"),
        parse_utc(load_json(LANE / "runs/compile-dry/tokenarchive.ready.json")["completedAtUtc"],
                  "compile/dry time"),
    ])
    require(max(latest_evidence_times) < generated_time,
            "scratch authority predates required evidence")
    return {
        "schema": SCHEMA, "phase": "SCRATCH_AUTHORITY", "verdict": "READY",
        "generatedAtUtc": generated_at,
        "claim": "FOUR_TOKENARCHIVE_LABELS_AND_FIVE_COMMENTS_AUTHORIZED_FOR_ONE_LIVE_APPLY",
        "specimen": specimen, "author": stamp(SCRIPT), "tool": tool,
        "generation14": {"campaign": campaign, "proof": proof,
                         "authority": campaign_authority},
        "predecessor": predecessor,
        "pre": {"backupManifest": stamp(PRE_MANIFEST), "restoreReceipt": restore,
                "functions": stamp(PRE_FUNCTIONS), "program": stamp(PRE_PROGRAM),
                "liveInspection": live_inspect, "liveMatchesBackup": True},
        "compileDry": validate_compile_dry(),
        "copies": copies, "replicas": replicas, "adverseControls": adverse,
        "delta": {
            "labelsAdded": 4, "commentsAdded": 5, "functionsChanged": 0,
            "boundariesChanged": 0, "instructionsChanged": 0, "definedDataChanged": 0,
            "referencesChanged": 0, "userDefinedSymbols": [6000, 6004],
            "comments": [9094, 9099], "addresses": ADDRESSES,
            "dataUnitsPreserved": 132,
        },
        "authorization": {"liveApplyAuthorized": True, "oneMutationProcess": True,
                          "separateReadbackRequired": True,
                          "postBackupAndRestoreRequired": True,
                          "additionalClaimsAuthorized": False},
        "limitations": [
            "Token-category meanings and runtime frequencies remain unassigned.",
            "No function boundary, signature, data-unit, reference, or rebuild behavior change is authorized.",
            "The historical failed compile/precondition logs are explicitly non-authoritative.",
        ],
    }


def validate_post_backup(expected: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    backup = LANE / "backups" / "post-live"
    manifest_path = backup / "backup_manifest.json"
    manifest = load_json(manifest_path)
    require(manifest.get("sourceStable") is True, "POST backup source was unstable")
    require(manifest.get("copyComparison", {}).get("matches") is True,
            "POST backup comparison failed")
    require(project_fields(manifest["source"]) == expected, "POST backup source differs")
    require(project_fields(manifest["destination"]) == expected, "POST backup destination differs")
    require(actual_project(backup) == expected, "POST backup actual bytes differ")
    restore_path = LANE / "post-live-restore.ready.json"
    restore = validate_restore(expected, restore_path, "POST restore")
    return stamp(manifest_path), restore


def build_live(generated_at: str) -> dict[str, Any]:
    generated_time = parse_utc(generated_at, "generatedAtUtc")
    require(generated_time <= datetime.now(timezone.utc),
            "live generatedAtUtc is in the future")
    scratch_saved = load_json(SCRATCH_READY)
    scratch = build_scratch(scratch_saved["generatedAtUtc"], require_current_live_pre=False)
    require(scratch_saved == scratch, "scratch authority no longer verifies")
    live_pre = validate_run("live immediate PRE", LIVE_PRE_RUN.name, "dry", LIVE,
                            inventory=True)
    require(live_pre["inventory"]["functions"]["sha256"] == PRE_FUNCTIONS_STAMP[1],
            "live immediate PRE function inventory differs")
    require(live_pre["inventory"]["program"]["sha256"] == PRE_PROGRAM_STAMP[1],
            "live immediate PRE program inventory differs")
    live_apply = validate_run("live apply", "live-apply", "apply", LIVE)
    live_readback = validate_run("live readback", "live-readback", "readback", LIVE,
                                 inventory=True)
    for phase in ("apply", "readback"):
        live_root = LANE / "runs" / f"live-{phase}"
        scratch_root = LANE / "runs" / f"replica-a-{phase}"
        require((live_root / "tokenarchive.tsv").read_bytes() ==
                (scratch_root / "tokenarchive.tsv").read_bytes(),
                f"live {phase} TSV differs from scratch")
        require(normalize_run_ready(live_root / "tokenarchive.ready.json") ==
                normalize_run_ready(scratch_root / "tokenarchive.ready.json"),
                f"live {phase} receipt differs beyond time/path")
    for artifact in ("functions.tsv", "program.tsv"):
        require((LANE / "runs/live-readback" / artifact).read_bytes() ==
                (LANE / "runs/replica-a-readback" / artifact).read_bytes(),
                f"live POST {artifact} differs from scratch")
    expected = actual_project(LIVE)
    post_inspect = validate_inspection(LIVE_POST_INSPECT, expected, "POST")
    post_manifest, post_restore = validate_post_backup(expected)
    require_distinct_projects([LIVE, PRE_BACKUP, LANE / "backups/post-live"])
    scratch_time = parse_utc(scratch_saved["generatedAtUtc"], "scratch authority time")
    live_pre_time = parse_utc(live_pre["completedAtUtc"], "live immediate PRE time")
    apply_time = parse_utc(live_apply["completedAtUtc"], "live apply time")
    readback_time = parse_utc(live_readback["completedAtUtc"], "live readback time")
    post_inspect_time = parse_utc(load_json(LIVE_POST_INSPECT)["createdAtUtc"],
                                  "live POST inspection time")
    post_backup_time = parse_utc(
        load_json(LANE / "backups/post-live/backup_manifest.json")["createdAtUtc"],
        "live POST backup time")
    post_restore_time = parse_utc(
        load_json(LANE / "post-live-restore.ready.json")["verifiedAtUtc"],
        "live POST restore time")
    require(scratch_time < live_pre_time < apply_time < readback_time <= post_inspect_time
            < post_backup_time < post_restore_time < generated_time,
            "scratch/live PRE/apply/readback/backup chronology differs")
    return {
        "schema": SCHEMA, "phase": "LIVE_PROMOTED", "verdict": "READY",
        "generatedAtUtc": generated_at,
        "claim": "TOKENARCHIVE_DISPATCH_STRUCTURE_PROMOTED_AND_SEPARATELY_READ_BACK",
        "author": stamp(SCRIPT), "tool": stamp(TOOL),
        "scratchAuthority": stamp(SCRATCH_READY),
        "live": {"project": str(LIVE.resolve()), "immediatePreReadback": live_pre,
                 "apply": live_apply,
                 "readback": live_readback, "postInspection": post_inspect,
                 "postBackupManifest": post_manifest, "postRestoreReceipt": post_restore},
        "result": {"labelsAdded": 4, "commentsAdded": 5, "functionsChanged": 0,
                   "boundariesChanged": 0, "instructionsChanged": 0,
                   "definedDataChanged": 0, "referencesChanged": 0,
                   "livePromotionApplied": True, "separateReadbackPassed": True,
                   "recoverablePostBackupPassed": True},
        "limitations": scratch["limitations"],
    }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def publish(path: Path, payload: Mapping[str, Any]) -> None:
    require(not path.exists(), f"refusing to overwrite receipt: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    with tempfile.NamedTemporaryFile(prefix=f".{path.name}.", suffix=".partial",
                                     dir=path.parent, delete=False) as stream:
        partial = Path(stream.name)
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        os.replace(partial, path)
    finally:
        partial.unlink(missing_ok=True)


def inspect_live(path: Path, phase: str) -> None:
    payload = {"schema": INSPECT_SCHEMA, "createdAtUtc": utc_now(), "phase": phase,
               "project": str(LIVE.resolve()), "manifest": actual_project(LIVE)}
    publish(path, payload)
    validate_inspection(path, payload["manifest"], phase)


def verify_saved(path: Path, builder: Callable[[str], dict[str, Any]]) -> dict[str, Any]:
    saved = load_json(path)
    require(isinstance(saved, dict), f"receipt is not an object: {path}")
    expected = builder(saved.get("generatedAtUtc"))
    require(saved == expected, f"receipt does not reproduce: {path}")
    return saved


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=(
        "inspect-live-pre", "seal-scratch", "verify-scratch",
        "inspect-live-post", "seal-live", "verify-live",
    ))
    args = parser.parse_args(argv)
    if args.command == "inspect-live-pre":
        expected = pre_project()
        require(actual_project(LIVE) == expected, "live project differs from PRE backup")
        inspect_live(LIVE_PRE_INSPECT, "PRE")
        print(f"TOKENARCHIVE_LIVE_PRE_INSPECTED sha256={sha256_file(LIVE_PRE_INSPECT)}")
    elif args.command == "seal-scratch":
        payload = build_scratch(utc_now())
        publish(SCRATCH_READY, payload)
        verify_saved(SCRATCH_READY, build_scratch)
        print(f"TOKENARCHIVE_SCRATCH_AUTHORITY_READY sha256={sha256_file(SCRATCH_READY)}")
    elif args.command == "verify-scratch":
        verify_saved(SCRATCH_READY, build_scratch)
        print(f"TOKENARCHIVE_SCRATCH_AUTHORITY_VERIFIED sha256={sha256_file(SCRATCH_READY)}")
    elif args.command == "inspect-live-post":
        inspect_live(LIVE_POST_INSPECT, "POST")
        print(f"TOKENARCHIVE_LIVE_POST_INSPECTED sha256={sha256_file(LIVE_POST_INSPECT)}")
    elif args.command == "seal-live":
        payload = build_live(utc_now())
        publish(LIVE_READY, payload)
        verify_saved(LIVE_READY, build_live)
        print(f"TOKENARCHIVE_LIVE_PROMOTION_READY sha256={sha256_file(LIVE_READY)}")
    else:
        verify_saved(LIVE_READY, build_live)
        print(f"TOKENARCHIVE_LIVE_PROMOTION_VERIFIED sha256={sha256_file(LIVE_READY)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
