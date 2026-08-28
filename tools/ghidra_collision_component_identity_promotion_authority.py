#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Fail-closed authority for the five-function collision identity repair.

The owner never mutates Ghidra.  It validates the exact static proof, verified
PRE backup/restore, two persistent positive replicas, two rollback probes,
fresh-process readbacks, and full 8,136-function collateral comparison.  After
the separately executed live ceremony it also validates live equality, POST
backup/restore, and the tracked Ghidra snapshot.
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
LANE = REPO / "local-lab/ghidra-collision-component-identity-live-promotion-20260812-v1"
LIVE = Path(r"C:\Users\david\Ghidra\Projects")
TRACKED = REPO / "reverse-engineering/ghidra"
PRE_BACKUP = Path(r"H:\BEA-Ghidra-Backups\2026-08-12-collision-component-identity-pre-live")
POST_BACKUP = Path(r"H:\BEA-Ghidra-Backups\2026-08-12-collision-component-identity-post-live")
PROOF = REPO / "local-lab/collision-component-identity-reproof-20260812-v1/proof.ready.json"
TOOL = REPO / "tools/GhidraApplyCollisionComponentIdentity.java"
PRE_FUNCTIONS = (
    REPO / "local-lab/ghidra-hud-source-identity-live-promotion-20260812-v1/"
    "runs/live-readback/functions.tsv"
)
PRE_PROGRAM = PRE_FUNCTIONS.with_name("program.tsv")
SCRATCH_READY = LANE / "scratch-authority.ready.json"
LIVE_READY = LANE / "live-promotion.ready.json"

SCHEMA = "bea.ghidra.collision-component-identity-promotion-authority.v1"
PROGRAM_SHA = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
PROOF_STAMP = (20_927, "63b88d3179edde082c915ac269b98ea26fd6fe3e2ab8e1315e11a0adad2e1ddb")
TOOL_STAMP = (43_726, "685175d69a0c7caf0c76e50668cbb24e73b74a765f0d103200f6916fa396b5f6")
PRE_FUNCTIONS_STAMP = (7_059_968, "fa2c9d749c97f1ab439b90572fd8f2292c9f5dcf4cc8b9b4f29f1756f088fed1")
PRE_PROGRAM_STAMP = (1_267, "cb47f9cf9e395b1cd9c31eedf4daba4564db2184484846d392b2a693dbcc5444")
TARGETS = {
    "0x004263f0", "0x004264a0", "0x004269b0", "0x00426a00", "0x00426a20",
}
ALLOWED_FUNCTION_FIELDS = {
    "name", "nameLen", "nameSha256", "fqname", "fqnameLen", "fqnameSha256",
    "signature", "signatureLen", "signatureSha256", "commentLen", "commentSha256",
    "tagCount", "tagsSha256", "tags",
}
POST = {
    "0x004263f0": {
        "name": "CCollisionSeekingThing__dtor_base",
        "signature": "void __fastcall CCollisionSeekingThing__dtor_base(void * this)",
        "commentLen": "642",
        "commentSha256": "8ae6efaba7a4920d42b76e1e8ea3e51f1bec909ce828c0cf3f9141ee52813b4b",
        "tags": "collision-seeking,collision-seeking-round-tail-review-wave1059,"
                "collision-seeking-thing,comment-hardened,destructor,identity-corrected,"
                "monitor-shutdown,owner-corrected,retail-binary-evidence,static-reaudit,"
                "tag-normalized,wave1059-readback-verified",
    },
    "0x004264a0": {
        "name": "CCollisionSeekingThing__ResolveCollisionResponse",
        "signature": "void __thiscall CCollisionSeekingThing__ResolveCollisionResponse"
                     "(void * this, void * otherRound)",
        "commentLen": "668",
        "commentSha256": "49dd9c620812a1e1656f9ef0ca755f1d4d64b250a3a783da6b12065168bf9bac",
        "tags": "collision-response,collision-seeking-round-tail-review-wave1059,"
                "collision-seeking-thing,comment-hardened,delayed-ready-flag,"
                "identity-corrected,owner-corrected,peer-collision,retail-binary-evidence,"
                "static-reaudit,tag-normalized,wave1059-readback-verified",
    },
    "0x004269b0": {
        "name": "CCSPersistentThing__Init",
        "signature": "void __thiscall CCSPersistentThing__Init(void * this, void * roundConfig)",
        "commentLen": "642",
        "commentSha256": "2ca95da8964d32862b20b5f8c2f96629f8591f2248dcb896b9fec2fb574991cc",
        "tags": "collision-seeking,comment-hardened,delayed-ready-flag,event-scheduling,"
                "identity-corrected,initial-collision-scan,owner-corrected,"
                "persistent-collision,persistent-slot,retail-binary-evidence,static-reaudit",
    },
    "0x00426a00": {
        "name": "CCSPersistentThing__ProcessMapWhoCollisionSweep",
        "signature": "void __thiscall CCSPersistentThing__ProcessMapWhoCollisionSweep"
                     "(void * this, void * startOrContext, void * endOrContext)",
        "commentLen": "669",
        "commentSha256": "3e370d6374b274c6ac044efe7697257555159b3f2b041a277af6d710f5552b31",
        "tags": "collision-seeking-round-tail-review-wave1059,comment-hardened,"
                "hlcollisiondetector-bridge,identity-corrected,mapwho-sweep,owner-corrected,"
                "persistent-collision,persistent-slot,retail-binary-evidence,static-reaudit,"
                "tag-normalized,wave1059-readback-verified",
    },
    "0x00426a20": {
        "name": "CCSPersistentThing__HandleEvent",
        "signature": "void __thiscall CCSPersistentThing__HandleEvent(void * this, void * event)",
        "commentLen": "619",
        "commentSha256": "ec07471bf4a889e23f3362148733e186fe6c14518419586dd9a6982f2d88ff42",
        "tags": "collision-seeking-round-tail-review-wave1059,comment-hardened,"
                "delayed-ready-flag,event-callback,event-handler,identity-corrected,"
                "owner-corrected,persistent-collision,persistent-slot,"
                "retail-binary-evidence,static-reaudit,tag-normalized,"
                "wave1059-readback-verified",
    },
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


def require_stamp(path: Path, expected: tuple[int, str], label: str) -> dict[str, Any]:
    actual = stamp(path)
    require((actual["bytes"], actual["sha256"]) == expected,
            f"{label} identity differs: {actual}")
    return actual


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise AuthorityError(f"invalid JSON at {path}: {exc}") from exc


def parse_utc(value: Any, label: str) -> None:
    require(isinstance(value, str) and value.endswith("Z"), f"{label} is not UTC")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise AuthorityError(f"{label} is malformed") from exc


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


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
        files.append({"relative_path": relative, "sha256": sha256_file(path), "size": stat.st_size})
        total += stat.st_size
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


def backup_project(root: Path, label: str) -> dict[str, Any]:
    manifest_path = root / "backup_manifest.json"
    manifest = load_json(manifest_path)
    require(manifest.get("sourceStable") is True, f"{label} source was unstable")
    require(manifest.get("copyComparison", {}).get("matches") is True,
            f"{label} copy differs")
    source = project_fields(manifest.get("source", {}))
    destination = project_fields(manifest.get("destination", {}))
    require(source == destination == plain_project(root), f"{label} project bytes differ")
    return {"manifest": stamp(manifest_path), "project": destination}


def initial_copy_project(root: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    """Validate the immutable copy receipt, not a replica's later POST bytes."""
    manifest_path = root / "backup_manifest.json"
    manifest = load_json(manifest_path)
    require(manifest.get("sourceStable") is True, f"{label} source was unstable")
    require(manifest.get("copyComparison", {}).get("matches") is True,
            f"{label} initial copy differs")
    source = project_fields(manifest.get("source", {}))
    destination = project_fields(manifest.get("destination", {}))
    require(source == destination == expected, f"{label} initial PRE copy differs")
    return {"manifest": stamp(manifest_path), "initialProject": destination}


def validate_restore(path: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    receipt = load_json(path)
    require(receipt.get("sourceStable") is True, f"{label} source was unstable")
    require(receipt.get("copyComparison", {}).get("matches") is True,
            f"{label} copy differs")
    readonly = receipt.get("readonlyOpen", {})
    require(readonly.get("opened") is True and readonly.get("contentStable") is True,
            f"{label} read-only open failed")
    require(readonly.get("postOpenComparison", {}).get("matches") is True,
            f"{label} changed during read-only open")
    require(readonly.get("observedProgramMd5") == PROGRAM_MD5 and
            readonly.get("observedProgramSha256") == PROGRAM_SHA,
            f"{label} program identity differs")
    require(project_fields(receipt.get("source", {})) == expected,
            f"{label} source project differs")
    return stamp(path)


def validate_ready(path: Path, mode: str, state: str) -> dict[str, Any]:
    value = load_json(path)
    require(value.get("schema") == "bea.ghidra.collision-component-identity.v1",
            f"{mode} receipt schema differs")
    parse_utc(value.get("completedAtUtc"), f"{mode} completedAtUtc")
    require(value.get("mode") == mode and value.get("state") == state,
            f"{mode} state differs")
    require(value.get("targets") == 5, f"{mode} target count differs")
    require(value.get("proof", {}).get("bytes") == PROOF_STAMP[0] and
            value.get("proof", {}).get("sha256") == PROOF_STAMP[1],
            f"{mode} proof binding differs")
    require(value.get("tool", {}).get("bytes") == TOOL_STAMP[0] and
            value.get("tool", {}).get("sha256") == TOOL_STAMP[1],
            f"{mode} tool binding differs")
    program = value.get("program", {})
    require(program.get("sha256") == PROGRAM_SHA and program.get("functions") == 8136 and
            program.get("instructions") == 549872, f"{mode} program differs")
    require(value.get("mutation") == {
        "namesChanged": 5, "displayedSignaturesChanged": 5, "commentsChanged": 5,
        "tagSetsChanged": 5, "boundariesChanged": 0, "bytesChanged": 0,
        "instructionsChanged": 0, "dataUnitsChanged": 0, "referencesChanged": 0,
    }, f"{mode} mutation envelope differs")
    require(value.get("loadedStateVerified") is (mode == "readback"),
            f"{mode} loaded-state marker differs")
    require(value.get("implementationIdentityNamesAuthorized") is True and
            value.get("runtimeSemanticsAuthorized") is False and
            value.get("rebuildReadyAuthorized") is False,
            f"{mode} authority boundary differs")
    output = Path(value.get("output", {}).get("path", ""))
    require(output.is_file() and output.stat().st_size == value["output"]["bytes"] and
            sha256_file(output) == value["output"]["sha256"],
            f"{mode} output stamp differs")
    return stamp(path)


def validate_collision_tsv(path: Path, mode: str, state: str) -> dict[str, Any]:
    rows = read_tsv(path)
    require(len(rows) == 5 and {row.get("address") for row in rows} == TARGETS,
            f"{mode} collision row census differs")
    require(all(row.get("mode") == mode and row.get("state") == state for row in rows),
            f"{mode} collision mode/state differs")
    if state == "POST":
        for row in rows:
            expected = POST[row["address"]]
            projected = {
                "name": expected["name"],
                "signature": expected["signature"],
                "commentBytes": expected["commentLen"],
                "commentSha256": expected["commentSha256"],
                "tags": expected["tags"],
            }
            require(all(row.get(key) == value for key, value in projected.items()),
                    f"{mode} POST row differs at {row['address']}")
    return stamp(path)


def validate_run(name: str, mode: str, state: str, marker: str,
                 *, inventory: bool = False) -> dict[str, Any]:
    root = LANE / "runs" / name
    log = root / "ghidra.log"
    text = log.read_text(encoding="utf-8", errors="replace")
    require(marker in text and "REPORT SCRIPT ERROR" not in text,
            f"{name} success marker/error state differs")
    result = {
        "collision": validate_collision_tsv(root / "collision.tsv", mode, state),
        "ready": validate_ready(root / "collision.ready.json", mode, state),
        "log": stamp(log),
    }
    if inventory:
        result["functions"] = stamp(root / "functions.tsv")
        result["program"] = stamp(root / "program.tsv")
    return result


def validate_adverse(name: str, markers: tuple[str, ...], readback: str) -> dict[str, Any]:
    root = LANE / "runs" / name
    log = root / "ghidra.log"
    text = log.read_text(encoding="utf-8", errors="replace")
    require(all(marker in text for marker in markers), f"{name} marker is absent")
    require("REPORT SCRIPT ERROR" in text, f"{name} did not fail intentionally")
    require(not (root / "collision.tsv").exists() and not (root / "collision.ready.json").exists(),
            f"{name} published success artifacts")
    return {
        "failureLog": stamp(log),
        "publishedSuccessArtifacts": 0,
        "separatePreReadback": validate_run(
            readback, "dry", "PRE", "COLLISION_COMPONENT_IDENTITY_DRY_COMPLETE targets=5 mutations=0"),
    }


def compare_inventories(pre_path: Path, post_path: Path, label: str) -> dict[str, Any]:
    pre = {row["address"]: row for row in read_tsv(pre_path)}
    post = {row["address"]: row for row in read_tsv(post_path)}
    require(len(pre) == len(post) == 8136 and pre.keys() == post.keys(),
            f"{label} function key set differs")
    changed: dict[str, list[str]] = {}
    for address in sorted(pre):
        fields = [key for key in pre[address] if pre[address][key] != post[address][key]]
        if fields:
            changed[address] = fields
    require(set(changed) == TARGETS, f"{label} changed address set differs: {set(changed)}")
    require(all(set(fields) <= ALLOWED_FUNCTION_FIELDS for fields in changed.values()),
            f"{label} changed fields exceed authority: {changed}")
    for address, expected in POST.items():
        require(all(post[address].get(key) == value for key, value in expected.items()),
                f"{label} final row differs at {address}")
    return {"changedAddresses": sorted(changed), "changedFields": changed}


def compare_programs(pre_path: Path, post_path: Path, label: str) -> dict[str, Any]:
    pre = {row["metric"]: row["value"] for row in read_tsv(pre_path)}
    post = {row["metric"]: row["value"] for row in read_tsv(post_path)}
    require(pre.keys() == post.keys(), f"{label} program metric keys differ")
    changed = [key for key in sorted(pre) if pre[key] != post[key]]
    require(changed == ["commentsSha256"], f"{label} program metric changes differ: {changed}")
    return {"changedMetrics": changed, "functionCount": int(post["functions"]),
            "instructionCount": int(post["instructions"])}


def build_scratch(generated_at: str, *, require_live_pre: bool = True) -> dict[str, Any]:
    parse_utc(generated_at, "generatedAtUtc")
    proof = require_stamp(PROOF, PROOF_STAMP, "collision identity proof")
    tool = require_stamp(TOOL, TOOL_STAMP, "collision Ghidra mutator")
    pre_functions = require_stamp(PRE_FUNCTIONS, PRE_FUNCTIONS_STAMP, "PRE functions")
    pre_program = require_stamp(PRE_PROGRAM, PRE_PROGRAM_STAMP, "PRE program")
    pre = backup_project(PRE_BACKUP, "PRE backup")
    restore = validate_restore(LANE / "pre-backup-restore.ready.json", pre["project"], "PRE restore")
    inspect = load_json(LANE / "live-pre-inspect.json")
    require(project_fields(inspect.get("manifest", {})) == pre["project"],
            "live PRE inspection differs")
    if require_live_pre:
        require(plain_project(LIVE) == pre["project"], "live project drifted from PRE")
        require(plain_project(TRACKED) == pre["project"], "tracked snapshot drifted from PRE")

    replicas: dict[str, Any] = {}
    for name in ("replica-a", "replica-b"):
        scratch = initial_copy_project(LANE / "scratch" / name, pre["project"], name)
        dry_name = "replica-a-dry-v2" if name == "replica-a" else "replica-b-dry"
        replicas[name] = {
            "copyManifest": scratch["manifest"],
            "dry": validate_run(dry_name, "dry", "PRE",
                                 "COLLISION_COMPONENT_IDENTITY_DRY_COMPLETE targets=5 mutations=0"),
            "apply": validate_run(name + "-apply", "apply", "POST",
                                  "COLLISION_COMPONENT_IDENTITY_APPLY_COMPLETE targets=5 "
                                  "reopen_verification_required=true"),
            "readback": validate_run(name + "-readback", "readback", "POST",
                                     "COLLISION_COMPONENT_IDENTITY_READBACK_COMPLETE targets=5 "
                                     "loaded_state_verified=true", inventory=True),
        }
        replicas[name]["collateral"] = {
            "functions": compare_inventories(
                PRE_FUNCTIONS, LANE / "runs" / f"{name}-readback/functions.tsv", name),
            "program": compare_programs(
                PRE_PROGRAM, LANE / "runs" / f"{name}-readback/program.tsv", name),
        }

    for artifact in ("collision.tsv", "functions.tsv", "program.tsv"):
        a = LANE / "runs/replica-a-readback" / artifact
        b = LANE / "runs/replica-b-readback" / artifact
        require(a.read_bytes() == b.read_bytes(), f"replica readback {artifact} differs")
    require((LANE / "runs/replica-a-dry-v2/collision.tsv").read_bytes() ==
            (LANE / "runs/replica-b-dry/collision.tsv").read_bytes(), "replica dry TSVs differ")
    require((LANE / "runs/replica-a-apply/collision.tsv").read_bytes() ==
            (LANE / "runs/replica-b-apply/collision.tsv").read_bytes(), "replica apply TSVs differ")

    adverse = {
        "afterOne": validate_adverse("probe-after-one", (
            "COLLISION_COMPONENT_IDENTITY_FORCED_AFTER_ONE_FAILURE rollback_required=true",
            "COLLISION_COMPONENT_IDENTITY_MUTATION_TAINTED mode=probe-after-one",
        ), "probe-after-one-readback"),
        "postInner": validate_adverse("probe-post-inner", (
            "COLLISION_COMPONENT_IDENTITY_COMPENSATING_PRE_RESTORE_COMPLETE targets=5",
            "COLLISION_COMPONENT_IDENTITY_FORCED_POST_INNER_FAILURE pre_restored=true",
            "COLLISION_COMPONENT_IDENTITY_MUTATION_TAINTED mode=probe-post-inner",
        ), "probe-post-inner-readback"),
    }
    incomplete = LANE / "runs/replica-a-dry/ghidra.log"
    excluded: dict[str, Any] = {"reason": "initial dry run rejected the mistaken UTF-8 byte-length constant before mutation"}
    if incomplete.is_file():
        text = incomplete.read_text(encoding="utf-8", errors="replace")
        require("COLLISION_COMPONENT_IDENTITY_PREFLIGHT_OK" not in text,
                "excluded initial dry unexpectedly reached preflight completion")
        excluded["log"] = stamp(incomplete)

    return {
        "schema": SCHEMA,
        "phase": "SCRATCH_AUTHORITY",
        "verdict": "READY",
        "generatedAtUtc": generated_at,
        "claim": "FIVE_COLLISION_COMPONENT_IDENTITIES_AUTHORIZED_FOR_ONE_LIVE_APPLY",
        "author": stamp(SCRIPT),
        "proof": proof,
        "tool": tool,
        "pre": {"backup": pre["manifest"], "restore": restore,
                "liveInspection": stamp(LANE / "live-pre-inspect.json"),
                "functions": pre_functions, "program": pre_program},
        "replicas": replicas,
        "adverseControls": adverse,
        "excludedEvidence": {"excludedInitialDry": excluded},
        "delta": {"addresses": sorted(TARGETS), "namesChanged": 5,
                  "displayedSignaturesChanged": 5, "commentsChanged": 5,
                  "tagSetsChanged": 5, "functionCount": 8136,
                  "instructionCount": 549872, "boundariesChanged": 0,
                  "bytesChanged": 0, "dataUnitsChanged": 0, "referencesChanged": 0},
        "authorization": {"liveApplyAuthorized": True, "mutationProcessLimit": 1,
                          "separateReadbackRequired": True,
                          "postBackupAndRestoreRequired": True,
                          "trackedSnapshotRefreshRequired": True,
                          "runtimeClaimsAuthorized": False,
                          "rebuildReadyAuthorized": False},
        "limitations": [
            "Only bounded base implementation-owner and role identities are promoted.",
            "No folded-alias exclusion, complete runtime collision behavior, field layout, or source-body equality is claimed.",
            "No reconstruction mapping or REBUILD_READY status is authorized.",
        ],
    }


def build_live(generated_at: str) -> dict[str, Any]:
    parse_utc(generated_at, "generatedAtUtc")
    scratch = load_json(SCRATCH_READY)
    require(scratch == build_scratch(scratch.get("generatedAtUtc", ""), require_live_pre=False),
            "scratch authority no longer reproduces")
    require(scratch.get("authorization", {}).get("liveApplyAuthorized") is True,
            "scratch authority does not authorize live apply")
    live_dry = validate_run("live-dry", "dry", "PRE",
                            "COLLISION_COMPONENT_IDENTITY_DRY_COMPLETE targets=5 mutations=0")
    live_apply = validate_run("live-apply", "apply", "POST",
                              "COLLISION_COMPONENT_IDENTITY_APPLY_COMPLETE targets=5 "
                              "reopen_verification_required=true")
    live_readback = validate_run("live-readback", "readback", "POST",
                                 "COLLISION_COMPONENT_IDENTITY_READBACK_COMPLETE targets=5 "
                                 "loaded_state_verified=true", inventory=True)
    for phase in ("apply", "readback"):
        require((LANE / f"runs/live-{phase}/collision.tsv").read_bytes() ==
                (LANE / f"runs/replica-a-{phase}/collision.tsv").read_bytes(),
                f"live {phase} differs from replica")
    require((LANE / "runs/live-readback/functions.tsv").read_bytes() ==
            (LANE / "runs/replica-a-readback/functions.tsv").read_bytes(),
            "live full function inventory differs from replica")
    require((LANE / "runs/live-readback/program.tsv").read_bytes() ==
            (LANE / "runs/replica-a-readback/program.tsv").read_bytes(),
            "live program inventory differs from replica")
    collateral = {
        "functions": compare_inventories(PRE_FUNCTIONS, LANE / "runs/live-readback/functions.tsv", "live"),
        "program": compare_programs(PRE_PROGRAM, LANE / "runs/live-readback/program.tsv", "live"),
    }
    post = backup_project(POST_BACKUP, "POST backup")
    require(plain_project(LIVE) == post["project"], "live project differs from POST backup")
    post_restore = validate_restore(LANE / "post-backup-restore.ready.json",
                                    post["project"], "POST restore")
    post_inspect = load_json(LANE / "live-post-inspect.json")
    require(project_fields(post_inspect.get("manifest", {})) == post["project"],
            "live POST inspection differs")
    require(plain_project(TRACKED) == post["project"], "tracked snapshot differs from live POST")
    tracked_restore = validate_restore(LANE / "tracked-snapshot-restore.ready.json",
                                       post["project"], "tracked snapshot restore")
    live_logs = sorted((LANE / "runs").glob("live-*/ghidra.log"))
    mutating = [path for path in live_logs if "COLLISION_COMPONENT_IDENTITY_APPLY_COMPLETE" in
                path.read_text(encoding="utf-8", errors="replace")]
    require(mutating == [LANE / "runs/live-apply/ghidra.log"],
            "live mutation-process census differs from one")
    return {
        "schema": SCHEMA,
        "phase": "LIVE_PROMOTED",
        "verdict": "READY",
        "generatedAtUtc": generated_at,
        "claim": "COLLISION_IDENTITIES_SAVED_READ_BACK_BACKED_UP_AND_TRACKED_SNAPSHOT_REFRESHED",
        "author": stamp(SCRIPT),
        "scratchAuthority": stamp(SCRATCH_READY),
        "live": {"dry": live_dry, "apply": live_apply, "readback": live_readback,
                 "collateral": collateral, "postInspection": stamp(LANE / "live-post-inspect.json"),
                 "postBackupManifest": post["manifest"], "postRestore": post_restore},
        "trackedSnapshot": {"root": rel(TRACKED), "fileCount": post["project"]["fileCount"],
                            "totalBytes": post["project"]["totalBytes"],
                            "restore": tracked_restore},
        "result": {"addresses": sorted(TARGETS), "namesChanged": 5,
                   "displayedSignaturesChanged": 5, "commentsChanged": 5,
                   "tagSetsChanged": 5, "functionCount": 8136,
                   "instructionCount": 549872, "boundariesChanged": 0,
                   "bytesChanged": 0, "dataUnitsChanged": 0, "referencesChanged": 0,
                   "liveMutationProcesses": 1, "separateReadbackPassed": True,
                   "recoverablePostBackupPassed": True,
                   "trackedSnapshotMatchesLive": True},
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
    require(isinstance(saved, dict), f"receipt is not an object: {path}")
    require(saved == builder(saved.get("generatedAtUtc", "")),
            f"receipt does not reproduce: {path}")
    return saved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("seal-scratch", "verify-scratch",
                                           "seal-live", "verify-live"))
    args = parser.parse_args()
    if args.command == "seal-scratch":
        publish(SCRATCH_READY, build_scratch(utc_now()))
        verify_saved(SCRATCH_READY, build_scratch)
        print(f"COLLISION_IDENTITY_SCRATCH_AUTHORITY_READY sha256={sha256_file(SCRATCH_READY)}")
    elif args.command == "verify-scratch":
        verify_saved(SCRATCH_READY, build_scratch)
        print(f"COLLISION_IDENTITY_SCRATCH_AUTHORITY_VERIFIED sha256={sha256_file(SCRATCH_READY)}")
    elif args.command == "seal-live":
        publish(LIVE_READY, build_live(utc_now()))
        verify_saved(LIVE_READY, build_live)
        print(f"COLLISION_IDENTITY_LIVE_PROMOTION_READY sha256={sha256_file(LIVE_READY)}")
    else:
        verify_saved(LIVE_READY, build_live)
        print(f"COLLISION_IDENTITY_LIVE_PROMOTION_VERIFIED sha256={sha256_file(LIVE_READY)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
