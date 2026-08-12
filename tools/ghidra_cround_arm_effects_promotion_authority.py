#!/usr/bin/env python3
"""Fail-closed authority for the Generation 23 CRound Ghidra comments.

The owner never mutates Ghidra. It verifies two persistent scratch replicas,
two rollback probes, the exact PRE backup/live identity, and later the separate
live apply/readback/full-inventory/post-backup/restore ceremony.
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
from typing import Any, Callable, Mapping, Sequence


REPO = Path(__file__).resolve().parent.parent
SCRIPT = Path(__file__).resolve()
LANE = REPO / "local-lab" / "ghidra-cround-handle-event-arm-effects-live-promotion-20260812-v1"
LIVE = Path(r"C:\Users\david\Ghidra\Projects")
PRE_BACKUP = Path(r"D:\BEA-Ghidra-Backups\2026-08-12-cround-handle-event-gen23-pre-live")
POST_BACKUP = Path(r"D:\BEA-Ghidra-Backups\2026-08-12-cround-handle-event-gen23-post-live")
TOOL = REPO / "tools" / "GhidraApplyCRoundArmEffectsComments.java"
PRISTINE = REPO / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
SCRATCH_READY = LANE / "scratch-authority.ready.json"
LIVE_READY = LANE / "live-promotion-v2.ready.json"

SCHEMA = "bea.ghidra.cround-arm-effects-promotion-authority.v1"
PROGRAM_SHA = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
TOOL_STAMP = (42_562, "3030eebc9de7a85d08ff74dc72d8ba9ddbbb4487a47ef1a0bc7c75d97ad87a1c")
PRE_FUNCTIONS_STAMP = (7_059_965, "38b86d40e937e982f7228ebf84fe88b8a4fc1f6e2113d2938bf14c85b0d57c86")
PRE_PROGRAM_STAMP = (1_267, "46f59a47f830c0d093ff32d301e215a9af98b73b75f57f2c3f4b438696787180")
PRE_COMMENTS_STAMP = (4_158, "7376e9dc32555fde6ed4ade1fa036e45fe50903c75a96c85ff3e2cf42ae34a7f")
APPLY_TSV_STAMP = (4_200, "3a32ddc522753f9590c850dea2cbd600d91a6a490aebd7f7f9ba88e1a139c4e6")
READBACK_TSV_STAMP = (4_236, "b5126f8b5de390e51269c4be6bd6f480440ae24db753c006e6573c56122bc3b3")
POST_FUNCTIONS_STAMP = (7_059_971, "356001a1910712b65e80886281c8536ba59b3e26d440c87bdd5a5fc0a92642b4")
POST_PROGRAM_STAMP = (1_267, "790ae35e391077ca7e4f8656ea229ea4ffb16ddf306ed5dcb4b06815498ce8f9")
SCRATCH_AUTHORITY_STAMP = (13_125, "292ec71ef7234d43270e8a714b4dca886a5b0884208f7abba74b0511491926c4")
TARGETS = {
    "0x004015e0", "0x004019e0", "0x00404150", "0x004cb3d0",
    "0x004d8ae0", "0x004d8e40", "0x004d9910", "0x004d9f30",
    "0x004dac90", "0x004f3cb0", "0x004f43d0", "0x004f4430",
}
EVIDENCE = {
    "proof": (LANE.parent / "cround-handle-event-arm-effects-20260812-v1/proof-v1/proof.ready.json",
              90_443, "974cbb86f8857d44369aef03e72b61656960147b7161466c4823e8d0c6ee867d"),
    "runtimeOverlay": (LANE.parent / "cround-handle-event-arm-effects-20260812-v1/runtime-overlay-v1/runtime-contracts.ready.json",
                       11_552, "341834e47349dc8e2c7097f40f9bc6d390e216d61a32b6d3a36df2d0c2983307"),
    "refuterFinding": (LANE.parent / "cround-handle-event-arm-effects-20260812-v1/refuter-finding-v1.json",
                       10_355, "28682d68afb0c3ddc8bcc17523657650b2e0800e2f87c6880127530f4795953a"),
    "refuterResult": (LANE.parent / "cround-handle-event-arm-effects-20260812-v1/refuter-result-v1.json",
                      5_305, "222898ab36605d5a2c3ec5642e8572197dd74cacd8af995e69d37c6379a90e67"),
    "adjudication": (LANE.parent / "cround-handle-event-arm-effects-20260812-v1/adjudication-v1.json",
                     3_019, "f1778fde37cdb61df8179b4a8de020909c54c4901ac7e01b5a98fe785413e17d"),
    "generation23": (LANE.parent / "re-campaign-incident-recovery-20260808-v1/generation-23-cround-handle-event-arm-effects-v1/campaign.ready.json",
                     20_860, "4471fdfe105340ad06c2ad28d945eb05e9bc94f002110888b164581ccf1a93fc"),
    "generation23Authority": (LANE.parent / "re-campaign-incident-recovery-20260808-v1/generation-23-cround-handle-event-arm-effects-authority.ready.json",
                              10_522, "12509207913b0116a94c923da7fe163c47de226b7733538baea54eb31df73ba8"),
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


def rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO).as_posix()
    except ValueError:
        return str(resolved)


def stamp(path: Path) -> dict[str, Any]:
    path = path.resolve()
    require(path.is_file(), f"required file is absent: {path}")
    result = path.stat()
    require(not path.is_symlink(), f"file is a symlink: {path}")
    require(not (getattr(result, "st_file_attributes", 0) & 0x400),
            f"file is a reparse point: {path}")
    require(result.st_nlink == 1, f"file is not single-link: {path}")
    return {"path": rel(path), "bytes": result.st_size, "sha256": sha256_file(path)}


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


def parse_utc(value: Any, label: str) -> None:
    require(isinstance(value, str) and value.endswith("Z"), f"{label} is not UTC")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ProofError(f"{label} is malformed") from exc


def plain_project(root: Path) -> dict[str, Any]:
    root = Path(os.path.abspath(root))
    require(root.is_dir(), f"project root is absent: {root}")
    files: list[dict[str, Any]] = []
    total = 0
    for path in [root, *root.rglob("*")]:
        result = path.lstat()
        require(not path.is_symlink(), f"project contains symlink: {path}")
        require(not (getattr(result, "st_file_attributes", 0) & 0x400),
                f"project contains reparse point: {path}")
        if not path.is_file() or path.name == "backup_manifest.json":
            continue
        require(result.st_nlink == 1, f"project contains linked file: {path}")
        relative = path.relative_to(root).as_posix()
        if relative != "BEA.gpr" and not relative.startswith("BEA.rep/"):
            continue
        files.append({"relative_path": relative, "sha256": sha256_file(path), "size": result.st_size})
        total += result.st_size
    files.sort(key=lambda row: row["relative_path"])
    return {
        "projectName": "BEA",
        "fileCount": len(files),
        "totalBytes": total,
        "structurallyComplete": any(row["relative_path"] == "BEA.gpr" for row in files)
            and any(row["relative_path"].startswith("BEA.rep/") for row in files),
        "files": files,
    }


def project_fields(value: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value.get(key) for key in
            ("projectName", "fileCount", "totalBytes", "structurallyComplete", "files")}


def pre_project() -> dict[str, Any]:
    manifest = load_json(PRE_BACKUP / "backup_manifest.json")
    require(manifest.get("sourceStable") is True, "PRE backup source was not stable")
    require(manifest.get("copyComparison", {}).get("matches") is True,
            "PRE backup copy comparison failed")
    expected = project_fields(manifest["destination"])
    require(expected == project_fields(manifest["source"]), "PRE source/destination differ")
    require(plain_project(PRE_BACKUP) == expected, "PRE backup bytes differ from manifest")
    return expected


def validate_restore(path: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    receipt = load_json(path)
    require(receipt.get("sourceStable") is True, f"{label} source was unstable")
    require(receipt.get("copyComparison", {}).get("matches") is True,
            f"{label} copy comparison failed")
    readonly = receipt.get("readonlyOpen", {})
    require(readonly.get("opened") is True and readonly.get("contentStable") is True,
            f"{label} read-only open failed")
    require(readonly.get("postOpenComparison", {}).get("matches") is True,
            f"{label} changed during read-only open")
    require(readonly.get("observedProgramMd5") == PROGRAM_MD5,
            f"{label} program MD5 differs")
    require(readonly.get("observedProgramSha256") == PROGRAM_SHA,
            f"{label} program SHA-256 differs")
    require(project_fields(receipt["source"]) == expected, f"{label} source project differs")
    return stamp(path)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def validate_comment_tsv(path: Path, phase: str) -> dict[str, Any]:
    expected = {"dry": PRE_COMMENTS_STAMP, "apply": APPLY_TSV_STAMP,
                "readback": READBACK_TSV_STAMP}[phase]
    result = require_stamp(path, expected, f"{phase} comments TSV")
    rows = read_tsv(path)
    require(len(rows) == 12, f"{phase} comment row count differs")
    require({row.get("address") for row in rows} == TARGETS, f"{phase} target set differs")
    require(all(row.get("mode") == phase for row in rows), f"{phase} mode differs")
    state = "PRE" if phase == "dry" else "POST"
    require(all(row.get("state") == state for row in rows), f"{phase} state differs")
    return result


def validate_ready(path: Path, phase: str) -> dict[str, Any]:
    value = load_json(path)
    require(value.get("schema") == "bea.ghidra.cround-arm-effects-comments.v1",
            f"{phase} Ghidra receipt schema differs")
    parse_utc(value.get("completedAtUtc"), f"{phase} completedAtUtc")
    require(value.get("mode") == phase, f"{phase} Ghidra receipt mode differs")
    require(value.get("state") == ("PRE" if phase == "dry" else "POST"),
            f"{phase} Ghidra receipt state differs")
    require(value.get("program", {}).get("executableSha256") == PROGRAM_SHA,
            f"{phase} executable differs")
    require(value.get("program", {}).get("functions") == 8136 and
            value.get("program", {}).get("instructions") == 549872,
            f"{phase} database counts differ")
    mutation = value.get("mutation", {})
    require(mutation == {"targetComments": 12, "namesChanged": 0,
                         "signaturesChanged": 0, "boundariesChanged": 0,
                         "bytesChanged": 0, "instructionsChanged": 0,
                         "dataUnitsChanged": 0, "referencesChanged": 0},
            f"{phase} mutation envelope differs")
    require(value.get("loadedStateVerified") is (phase == "readback"),
            f"{phase} loaded-state marker differs")
    return stamp(path)


def validate_inventory(functions: Path, program: Path) -> dict[str, Any]:
    functions_stamp = require_stamp(functions, POST_FUNCTIONS_STAMP, "POST functions")
    program_stamp = require_stamp(program, POST_PROGRAM_STAMP, "POST program")
    metrics = {row["metric"]: row["value"] for row in read_tsv(program)}
    require(metrics.get("programName") == "BEA.exe", "POST program name differs")
    require(metrics.get("executableSHA256") == PROGRAM_SHA, "POST executable differs")
    require(metrics.get("functions") == "8136" and metrics.get("instructions") == "549872",
            "POST function/instruction counts differ")
    require(metrics.get("definedData") == "48585" and metrics.get("references") == "234357",
            "POST data/reference counts differ")
    require(metrics.get("comments") == "9111", "POST comment-address count differs")
    before = {row["address"]: row for row in read_tsv(
        LANE / "audit/live-pre-full-inventory/functions.tsv")}
    after = {row["address"]: row for row in read_tsv(functions)}
    require(before.keys() == after.keys(), "POST function key set differs")
    changed: dict[str, list[str]] = {}
    for address in before:
        fields = [key for key in before[address] if before[address][key] != after[address][key]]
        if fields:
            changed[address] = fields
    require(set(changed) == TARGETS, f"POST changed address set differs: {set(changed)}")
    require(all(fields == ["commentLen", "commentSha256"] for fields in changed.values()),
            f"POST changed fields exceed comments: {changed}")
    return {"functions": functions_stamp, "program": program_stamp,
            "changedAddresses": sorted(changed), "changedFields": ["commentLen", "commentSha256"]}


def require_current_live_pre(expected: Mapping[str, Any]) -> dict[str, Any]:
    actual = plain_project(LIVE)
    require(actual == expected, "maintainer project drifted from verified PRE backup")
    inspect = load_json(LANE / "live-preapply-inspect.json")
    require(project_fields(inspect.get("manifest", {})) == expected,
            "live PRE inspection differs from verified PRE backup")
    return stamp(LANE / "live-preapply-inspect.json")


def validate_scratch_run(name: str, phase: str) -> dict[str, Any]:
    root = LANE / "runs" / f"{name}-{phase}"
    return {
        "comments": validate_comment_tsv(root / "comments.tsv", phase),
        "ready": validate_ready(root / "comments.ready.json", phase),
        "log": stamp(root / "ghidra.log"),
    }


def validate_probe(name: str, required_markers: Sequence[str]) -> dict[str, Any]:
    root = LANE / "runs" / name
    require(not (root / "comments.tsv").exists() and not (root / "comments.ready.json").exists(),
            f"{name} unexpectedly published success artifacts")
    text = (root / "ghidra.log").read_text(encoding="utf-8", errors="replace")
    require(all(marker in text for marker in required_markers), f"{name} marker is absent")
    readback = LANE / "runs" / f"{name}-readback"
    return {
        "failureLog": stamp(root / "ghidra.log"),
        "preStateReadback": validate_comment_tsv(readback / "comments.tsv", "dry"),
        "preStateReady": validate_ready(readback / "comments.ready.json", "dry"),
    }


def build_scratch(generated_at: str, *, require_live_pre: bool = True) -> dict[str, Any]:
    parse_utc(generated_at, "generatedAtUtc")
    require_stamp(PRISTINE, (2_506_752, PROGRAM_SHA), "pristine specimen")
    expected = pre_project()
    require_stamp(TOOL, TOOL_STAMP, "Ghidra comment tool")
    evidence = {name: require_stamp(path, (size, digest), name)
                for name, (path, size, digest) in EVIDENCE.items()}
    pre = {
        "backupManifest": stamp(PRE_BACKUP / "backup_manifest.json"),
        "restoreReceipt": validate_restore(LANE / "pre-backup-restore.ready.json",
                                           expected, "PRE restore"),
        "functions": require_stamp(LANE / "audit/live-pre-full-inventory/functions.tsv",
                                   PRE_FUNCTIONS_STAMP, "PRE functions"),
        "program": require_stamp(LANE / "audit/live-pre-full-inventory/program.tsv",
                                 PRE_PROGRAM_STAMP, "PRE program"),
    }
    if require_live_pre:
        pre["liveInspection"] = require_current_live_pre(expected)
    replicas: dict[str, Any] = {}
    for name in ("replica-a", "replica-b"):
        manifest = load_json(LANE / "scratch" / name / "backup_manifest.json")
        require(manifest.get("sourceStable") is True and
                manifest.get("copyComparison", {}).get("matches") is True,
                f"{name} source copy was not stable/exact")
        replicas[name] = {
            "copyManifest": stamp(LANE / "scratch" / name / "backup_manifest.json"),
            "apply": validate_scratch_run(name, "apply"),
            "readback": validate_scratch_run(name, "readback"),
            "postInventory": validate_inventory(
                LANE / "runs" / f"{name}-post-inventory/functions.tsv",
                LANE / "runs" / f"{name}-post-inventory/program.tsv"),
        }
    for relative in ("comments.tsv",):
        require((LANE / "runs/replica-a-apply" / relative).read_bytes() ==
                (LANE / "runs/replica-b-apply" / relative).read_bytes(),
                "replica apply TSVs differ")
        require((LANE / "runs/replica-a-readback" / relative).read_bytes() ==
                (LANE / "runs/replica-b-readback" / relative).read_bytes(),
                "replica readback TSVs differ")
    require((LANE / "runs/replica-a-post-inventory/functions.tsv").read_bytes() ==
            (LANE / "runs/replica-b-post-inventory/functions.tsv").read_bytes(),
            "replica full function inventories differ")
    require((LANE / "runs/replica-a-post-inventory/program.tsv").read_bytes() ==
            (LANE / "runs/replica-b-post-inventory/program.tsv").read_bytes(),
            "replica program inventories differ")
    adverse = {
        "probeAfterOne": validate_probe("probe-after-one", [
            "CROUND_ARM_COMMENTS_FORCED_AFTER_ONE_FAILURE rollback_required=true",
            "CROUND_ARM_COMMENTS_MUTATION_TAINTED mode=probe-after-one"]),
        "probePostInner": validate_probe("probe-post-inner", [
            "CROUND_ARM_COMMENTS_COMPENSATING_PRE_RESTORE_COMPLETE targets=12",
            "CROUND_ARM_COMMENTS_FORCED_POST_INNER_FAILURE pre_restored=true"]),
    }
    wrong = LANE / "runs/adverse-wrong-proof-path"
    require(not (wrong / "comments.tsv").exists() and not (wrong / "comments.ready.json").exists(),
            "wrong-proof adverse control published artifacts")
    wrong_text = (wrong / "ghidra.log").read_text(encoding="utf-8", errors="replace")
    require("canonical path differs" in wrong_text, "wrong-proof rejection marker absent")
    adverse["wrongProofPath"] = {"log": stamp(wrong / "ghidra.log"),
                                  "publishedArtifacts": 0}
    return {
        "schema": SCHEMA, "phase": "SCRATCH_AUTHORITY", "verdict": "READY",
        "generatedAtUtc": generated_at,
        "claim": "TWELVE_BOUNDED_GEN23_FUNCTION_COMMENTS_AUTHORIZED_FOR_ONE_LIVE_APPLY",
        "specimen": stamp(PRISTINE), "author": stamp(SCRIPT), "tool": stamp(TOOL),
        "evidence": evidence, "pre": pre, "replicas": replicas,
        "adverseControls": adverse,
        "delta": {"targetComments": 12, "addresses": sorted(TARGETS),
                  "functionCount": 8136, "instructionCount": 549872,
                  "namesChanged": 0, "signaturesChanged": 0,
                  "boundariesChanged": 0, "bytesChanged": 0,
                  "dataUnitsChanged": 0, "referencesChanged": 0},
        "authorization": {"liveApplyAuthorized": True, "oneMutationProcess": True,
                          "separateReadbackRequired": True,
                          "postBackupAndRestoreRequired": True,
                          "repositorySnapshotRefreshRequired": True,
                          "additionalClaimsAuthorized": False},
        "limitations": [
            "Only five selected invocations in two sealed sessions are described.",
            "Only default/3000 and event 4003 are gap-free.",
            "External writes/effects, event 2000, event 4002, CMissile placement, field meanings, source spelling, and direct rebuild parity remain open.",
        ],
    }


def validate_post_backup(expected: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = load_json(POST_BACKUP / "backup_manifest.json")
    require(manifest.get("sourceStable") is True and
            manifest.get("copyComparison", {}).get("matches") is True,
            "POST backup was not stable/exact")
    require(project_fields(manifest["source"]) == expected == project_fields(manifest["destination"]),
            "POST backup project identity differs")
    require(plain_project(POST_BACKUP) == expected, "POST backup bytes differ from manifest")
    receipt_path = LANE / "post-backup-restore.ready.json"
    return stamp(POST_BACKUP / "backup_manifest.json"), validate_restore(
        receipt_path, expected, "POST restore")


def build_live(generated_at: str) -> dict[str, Any]:
    parse_utc(generated_at, "generatedAtUtc")
    scratch_stamp = require_stamp(SCRATCH_READY, SCRATCH_AUTHORITY_STAMP,
                                  "immutable pre-live scratch authority")
    scratch = load_json(SCRATCH_READY)
    require(scratch.get("schema") == SCHEMA and scratch.get("phase") == "SCRATCH_AUTHORITY"
            and scratch.get("verdict") == "READY", "scratch authority envelope differs")
    require(scratch.get("authorization", {}).get("liveApplyAuthorized") is True,
            "scratch authority did not authorize the live apply")
    live_apply = validate_scratch_run("live", "apply")
    live_readback = validate_scratch_run("live", "readback")
    live_inventory = validate_inventory(
        LANE / "runs/live-post-inventory/functions.tsv",
        LANE / "runs/live-post-inventory/program.tsv")
    require((LANE / "runs/live-apply/comments.tsv").read_bytes() ==
            (LANE / "runs/replica-a-apply/comments.tsv").read_bytes(),
            "live apply differs from scratch")
    require((LANE / "runs/live-readback/comments.tsv").read_bytes() ==
            (LANE / "runs/replica-a-readback/comments.tsv").read_bytes(),
            "live readback differs from scratch")
    require((LANE / "runs/live-post-inventory/functions.tsv").read_bytes() ==
            (LANE / "runs/replica-a-post-inventory/functions.tsv").read_bytes(),
            "live full inventory differs from scratch")
    expected = plain_project(LIVE)
    post_inspect = load_json(LANE / "live-postapply-inspect.json")
    require(project_fields(post_inspect.get("manifest", {})) == expected,
            "live POST inspection differs from live bytes")
    post_manifest, post_restore = validate_post_backup(expected)
    repo_snapshot = plain_project(REPO / "reverse-engineering/ghidra")
    require(repo_snapshot == expected, "tracked Ghidra snapshot differs from live POST")
    tracked_restore = validate_restore(
        LANE / "tracked-snapshot-restore.ready.json", expected, "tracked snapshot restore")
    return {
        "schema": SCHEMA, "phase": "LIVE_PROMOTED", "verdict": "READY",
        "generatedAtUtc": generated_at,
        "claim": "GEN23_COMMENTS_SAVED_READ_BACK_BACKED_UP_AND_TRACKED_SNAPSHOT_REFRESHED",
        "author": stamp(SCRIPT), "tool": stamp(TOOL),
        "scratchAuthority": scratch_stamp,
        "live": {"apply": live_apply, "readback": live_readback,
                 "postInventory": live_inventory,
                 "postInspection": stamp(LANE / "live-postapply-inspect.json"),
                 "postBackupManifest": post_manifest,
                 "postRestoreReceipt": post_restore},
        "trackedSnapshot": {"root": rel(REPO / "reverse-engineering/ghidra"),
                            "fileCount": expected["fileCount"],
                            "totalBytes": expected["totalBytes"],
                            "restoreReceipt": tracked_restore},
        "result": {"targetComments": 12, "functionCount": 8136,
                   "instructionCount": 549872, "namesChanged": 0,
                   "signaturesChanged": 0, "boundariesChanged": 0,
                   "bytesChanged": 0, "dataUnitsChanged": 0,
                   "referencesChanged": 0, "livePromotionApplied": True,
                   "separateReadbackPassed": True,
                   "recoverablePostBackupPassed": True,
                   "trackedSnapshotMatchesLive": True},
        "limitations": scratch["limitations"],
    }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def publish(path: Path, payload: Mapping[str, Any]) -> None:
    require(not path.exists(), f"refusing to overwrite authority receipt: {path}")
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


def verify_saved(path: Path, builder: Callable[[str], dict[str, Any]]) -> dict[str, Any]:
    saved = load_json(path)
    require(isinstance(saved, dict), f"receipt is not an object: {path}")
    expected = builder(saved.get("generatedAtUtc"))
    require(saved == expected, f"receipt does not reproduce: {path}")
    return saved


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("seal-scratch", "verify-scratch",
                                           "seal-live", "verify-live"))
    args = parser.parse_args(argv)
    if args.command == "seal-scratch":
        publish(SCRATCH_READY, build_scratch(utc_now()))
        verify_saved(SCRATCH_READY, build_scratch)
        print(f"CROUND_ARM_SCRATCH_AUTHORITY_READY sha256={sha256_file(SCRATCH_READY)}")
    elif args.command == "verify-scratch":
        verify_saved(SCRATCH_READY, build_scratch)
        print(f"CROUND_ARM_SCRATCH_AUTHORITY_VERIFIED sha256={sha256_file(SCRATCH_READY)}")
    elif args.command == "seal-live":
        publish(LIVE_READY, build_live(utc_now()))
        verify_saved(LIVE_READY, build_live)
        print(f"CROUND_ARM_LIVE_PROMOTION_READY sha256={sha256_file(LIVE_READY)}")
    else:
        verify_saved(LIVE_READY, build_live)
        print(f"CROUND_ARM_LIVE_PROMOTION_VERIFIED sha256={sha256_file(LIVE_READY)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
