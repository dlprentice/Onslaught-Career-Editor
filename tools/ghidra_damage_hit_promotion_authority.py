#!/usr/bin/env python3
"""Fail-closed authority for the Generation 12 Damage/Hit Ghidra promotion.

This owner does not mutate Ghidra.  It independently validates the two-replica
scratch ceremony and, after a separately executed live apply/readback/backup,
publishes the bounded live-promotion receipt.  Historical or pilot evidence is
never accepted through a fallback path.
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
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


REPO = Path(__file__).resolve().parent.parent
SCRIPT = Path(__file__).resolve()
LANE = REPO / "local-lab" / "ghidra-damage-hit-semantic-live-promotion-20260809-v1"
LIVE = Path(r"C:\Users\david\Ghidra\Projects")
PRISTINE = REPO / "local-lab" / "safe-copy-bea-pristine" / "BEA.exe.original.backup"
TOOL = REPO / "tools" / "GhidraApplyDamageHitContracts.java"
PRE_BACKUP = LANE / "backups" / "pre-live"
PRE_MANIFEST = PRE_BACKUP / "backup_manifest.json"
PRE_RESTORE = LANE / "pre-live-restore.ready.json"
PRE_FUNCTIONS = LANE / "pre-observation" / "functions.tsv"
PRE_PROGRAM = LANE / "pre-observation" / "program.tsv"
LIVE_PRE_INSPECT = LANE / "live-preapply-inspect.json"
SCRATCH_READY = LANE / "promotion" / "scratch-authority.ready.json"
LIVE_READY = LANE / "promotion" / "promotion.ready.json"

SCHEMA = "bea.ghidra.damage-hit-semantic-promotion-authority.v1"
PROGRAM_SHA = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
TOOL_SHA = "aa80734cb1185721d05f3971c30be1351370d55cd1f986e3d11a3555b11828bc"
TOOL_BYTES = 41601
CAMPAIGN_SHA = "9d2b903d451cb62fd6fb599b915dd57a0e6f313e610a348022fabf26ee265747"
PROOF_SHA = "ffb2e0b8692ddada364a829d52a158841e5d800742c49bd2a1710b2af135869a"
AUTHORITY_SHA = "c3531b495084ec73fc2b76a70be3409ca120448ba6831cbfa96a70866e182cba"
PRE_FUNCTIONS_STAMP = (7_051_723, "b55e91ee42af8ba554453a80241e9d43f321070d4942dd0a3a00ae605f6ed5cd")
PRE_PROGRAM_STAMP = (1_267, "6a74dff3b4c28e351eb3ffcbf4abf2ee55b01c10ad1719f373b5556a71472edc")
POST_FUNCTIONS_STAMP = (7_051_668, "075165bae3616dda0adf534625db612990daee9974b3fc85429d3b5b408ee979")
POST_PROGRAM_STAMP = (1_267, "e1724ff7ae231326cd4b25a6c8d8d0d53ebb844a509541c402cdd64436474029")
PHASE_TSV_SHA = {
    "dry": (947, "0a001bbf698266d3883580f907a67d842bea10b0f20aede2b897418acd67d70e"),
    "apply": (935, "a4ce6fdbc2f2f6df6eae05652dd9885e4df2d7d190a775b64d97acb4606768b7"),
    "readback": (941, "3ceffd904f5a7baf685af2c863047a0c348d3631da8f070b610b82805c07ac8d"),
}
TARGETS = {
    "0x00407350": {
        "preName": "CBattleEngine__VFunc_39_00407350",
        "postName": "CBattleEngine__Hit",
        "preSignature": "undefined __thiscall CBattleEngine__VFunc_39_00407350(void * this, int * param_1, void * param_2)",
        "postSignature": "void __thiscall CBattleEngine__Hit(void * this, void * otherThing, void * report)",
        "bodyBytes": "380",
        "bodySha256": "8034efee2c37c5e02579dc82d4405b758cedc96d62b27909f5c66a6cea43ae8a",
        "instructionCount": "114",
    },
    "0x0040a890": {
        "preName": "CBattleEngine__VFunc_40_0040a890",
        "postName": "CBattleEngine__Damage",
        "preSignature": "undefined __thiscall CBattleEngine__VFunc_40_0040a890(void * this, float param_1, int param_2, int param_3)",
        "postSignature": "void __thiscall CBattleEngine__Damage(void * this, float amount, void * inByThis, int inDamageShields, int meshPartNo)",
        "bodyBytes": "917",
        "bodySha256": "224c0577b539bbf0d6fa118a6355502f9aead3bc588e59ae3bf08bdf3cd1ff91",
        "instructionCount": "233",
    },
}


class ProofError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProofError(message)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return path.resolve().relative_to(REPO).as_posix()


def stamp(path: Path) -> dict[str, Any]:
    path = path.resolve()
    require(path.is_file(), f"required file is absent: {path}")
    stat_result = path.stat()
    require(stat_result.st_nlink == 1, f"file is not single-link: {path}")
    require(not path.is_symlink(), f"file is a symlink: {path}")
    require(not (getattr(stat_result, "st_file_attributes", 0) & 0x400),
            f"file is a reparse point: {path}")
    return {"path": rel(path), "bytes": stat_result.st_size, "sha256": sha256_file(path)}


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


def project_fields(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "projectName": value.get("projectName"),
        "fileCount": value.get("fileCount"),
        "totalBytes": value.get("totalBytes"),
        "structurallyComplete": value.get("structurallyComplete"),
        "files": value.get("files"),
    }


def assert_plain_tree(root: Path, label: str) -> None:
    raw = Path(os.path.abspath(root))
    require(raw.exists() and raw.is_dir(), f"{label} root is absent")
    for path in [raw, *raw.rglob("*")]:
        stat_result = path.lstat()
        require(not path.is_symlink(), f"{label} contains symlink: {path}")
        require(not (getattr(stat_result, "st_file_attributes", 0) & 0x400),
                f"{label} contains reparse point: {path}")
        if path.is_file():
            require(stat_result.st_nlink == 1, f"{label} contains linked file: {path}")


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
        "projectName": "BEA",
        "fileCount": len(files),
        "totalBytes": total,
        "structurallyComplete": any(row["relative_path"] == "BEA.gpr" for row in files)
            and any(row["relative_path"].startswith("BEA.rep/") for row in files),
        "files": files,
    }


def pre_project() -> dict[str, Any]:
    receipt = load_json(PRE_MANIFEST)
    require(receipt.get("schemaVersion") == "onslaught-ghidra-project-backup.v2",
            "PRE backup schema differs")
    require(receipt.get("sourceStable") is True, "PRE backup source was unstable")
    require(receipt.get("copyComparison", {}).get("matches") is True,
            "PRE backup copy comparison failed")
    source = project_fields(receipt["source"])
    destination = project_fields(receipt["destination"])
    require(source == destination, "PRE backup source/destination inventories differ")
    require(actual_project(PRE_BACKUP) == destination, "PRE backup bytes differ from manifest")
    return destination


def validate_copy(name: str, expected: Mapping[str, Any]) -> dict[str, Any]:
    root = LANE / "scratch-v2" / name
    receipt_path = root / "backup_manifest.json"
    receipt = load_json(receipt_path)
    require(receipt.get("schemaVersion") == "onslaught-ghidra-project-backup.v2",
            f"{name} copy schema differs")
    require(receipt.get("sourceStable") is True, f"{name} source was unstable")
    comparison = receipt.get("copyComparison", {})
    require(comparison.get("matches") is True, f"{name} copy comparison failed")
    for field in ("missingCount", "extraCount", "sizeDiffCount", "hashDiffCount"):
        require(comparison.get(field) == 0, f"{name} {field} is nonzero")
    require(project_fields(receipt["source"]) == expected, f"{name} copy source differs")
    require(project_fields(receipt["destination"]) == expected, f"{name} copy destination differs")
    # Positive replicas are intentionally POST by the time this ceremony seals,
    # and adverse projects may have new Ghidra container bytes despite a semantic
    # PRE rollback.  Their separate full inventories below prove final state;
    # this manifest proves only that every lane began as the exact PRE clone.
    return {"manifest": stamp(receipt_path), "project": rel(root)}


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        return list(reader.fieldnames or []), list(reader)


def validate_target_tsv(path: Path, phase: str) -> None:
    _, rows = read_tsv(path)
    require(len(rows) == 2, f"{phase} TSV row count differs")
    require([row["address"] for row in rows] == list(TARGETS),
            f"{phase} TSV target order differs")
    post = phase in {"apply", "readback"}
    state = "POST" if post else "PRE"
    for row in rows:
        target = TARGETS[row["address"]]
        require(row["mode"] == phase and row["state"] == state,
                f"{phase} row mode/state differs at {row['address']}")
        require(row["name"] == target["postName" if post else "preName"],
                f"{phase} row name differs at {row['address']}")
        require(row["signature"] == target["postSignature" if post else "preSignature"],
                f"{phase} signature differs at {row['address']}")
        require(row["bodyBytes"] == target["bodyBytes"], f"{phase} body size differs")
        require(row["bodySha256"] == target["bodySha256"], f"{phase} body hash differs")
        require(row["instructionCount"] == target["instructionCount"],
                f"{phase} instruction count differs")
        require(row["sigSource"] == ("USER_DEFINED" if post else "ANALYSIS"),
                f"{phase} signature source differs")


def validate_run(label: str, run_name: str, phase: str) -> dict[str, Any]:
    root = LANE / "runs-v2" / run_name
    tsv = root / "damage-hit.tsv"
    ready_path = root / "damage-hit.ready.json"
    log = root / "headless.log"
    require_stamp(tsv, PHASE_TSV_SHA[phase], f"{label} {phase} TSV")
    validate_target_tsv(tsv, phase)
    ready = load_json(ready_path)
    expected_keys = {
        "schema", "completedAtUtc", "mode", "state", "tool",
        "campaignReadySha256", "proofReadySha256", "authorityReadySha256",
        "program", "targets", "output", "commitRequested",
        "nestedEndReturnedCommitted", "loadedStateVerified",
        "semanticNamesAuthorized", "authorityBoundary",
    }
    require(set(ready) == expected_keys, f"{label} {phase} READY shape differs")
    parse_utc(ready["completedAtUtc"], f"{label} {phase} completedAtUtc")
    require(ready["schema"] == "bea.ghidra.damage-hit-semantic.v1",
            f"{label} {phase} schema differs")
    require(ready["mode"] == phase, f"{label} READY mode differs")
    require(ready["state"] == ("PRE" if phase == "dry" else "POST"),
            f"{label} READY state differs")
    require(Path(ready["tool"]["path"]).resolve() == TOOL.resolve(),
            f"{label} tool path differs")
    require((ready["tool"]["bytes"], ready["tool"]["sha256"]) == (TOOL_BYTES, TOOL_SHA),
            f"{label} tool identity differs")
    require(ready["campaignReadySha256"] == CAMPAIGN_SHA, "campaign identity differs")
    require(ready["proofReadySha256"] == PROOF_SHA, "proof identity differs")
    require(ready["authorityReadySha256"] == AUTHORITY_SHA, "authority identity differs")
    require(ready["program"] == {
        "name": "BEA.exe", "md5": PROGRAM_MD5, "sha256": PROGRAM_SHA,
        "functions": 8124, "instructions": 549872,
    }, f"{label} program identity differs")
    require(ready["targets"] == 2, f"{label} target count differs")
    require(Path(ready["output"]["path"]).resolve() == tsv.resolve(),
            f"{label} output path differs")
    require(ready["output"] | {"path": rel(tsv)} == stamp(tsv),
            f"{label} output stamp differs")
    require(ready["commitRequested"] is (phase == "apply"),
            f"{label} commit flag differs")
    require(ready["nestedEndReturnedCommitted"] is False,
            f"{label} nested transaction result differs")
    require(ready["loadedStateVerified"] is (phase == "readback"),
            f"{label} loaded-state flag differs")
    require(ready["semanticNamesAuthorized"] is False,
            f"{label} self-authorized semantics")
    log_text = log.read_text(encoding="utf-8", errors="replace")
    marker = {
        "dry": "DAMAGE_HIT_DRY_COMPLETE rows=2 mutations=0",
        "apply": "DAMAGE_HIT_APPLY_COMPLETE rows=2 reopen_verification_required=true",
        "readback": "DAMAGE_HIT_READBACK_COMPLETE rows=2",
    }[phase]
    require(marker in log_text and "SCRIPT ERROR" not in log_text,
            f"{label} {phase} log did not close cleanly")
    return {"tsv": stamp(tsv), "ready": stamp(ready_path), "log": stamp(log)}


def normalize_run_receipt(path: Path) -> dict[str, Any]:
    value = copy.deepcopy(load_json(path))
    value.pop("completedAtUtc")
    value["output"]["path"] = "<lane-output>"
    return value


def validate_post_inventory(label: str, run_name: str) -> dict[str, Any]:
    root = LANE / "runs-v2" / run_name
    functions = root / "functions.tsv"
    program = root / "program.tsv"
    require_stamp(functions, POST_FUNCTIONS_STAMP, f"{label} post functions")
    require_stamp(program, POST_PROGRAM_STAMP, f"{label} post program")
    pre_header, pre_rows = read_tsv(PRE_FUNCTIONS)
    post_header, post_rows = read_tsv(functions)
    require(pre_header == post_header, f"{label} inventory columns differ")
    require(len(pre_rows) == len(post_rows) == 8124, f"{label} function count differs")
    changed = []
    for before, after in zip(pre_rows, post_rows, strict=True):
        require(before["address"] == after["address"], f"{label} inventory order differs")
        if before != after:
            changed.append(after["address"].lower())
    require(changed == ["0x00407350", "0x0040a890"],
            f"{label} changed function set differs: {changed}")
    by_address = {row["address"].lower(): row for row in post_rows}
    for address, target in TARGETS.items():
        row = by_address[address]
        require(row["name"] == target["postName"], f"{label} post name differs")
        require(row["signature"] == target["postSignature"], f"{label} post signature differs")
        require(row["sigSource"] == "USER_DEFINED", f"{label} post sig source differs")
        require(row["returnType"] == "void", f"{label} post return type differs")
        require(row["commentPresent"] == "true", f"{label} bounded comment absent")
    return {"functions": stamp(functions), "program": stamp(program)}


def validate_adverse(name: str) -> dict[str, Any]:
    root = LANE / "runs-v2" / name
    log = root / "headless.log"
    text = log.read_text(encoding="utf-8", errors="replace")
    common = [
        "DAMAGE_HIT_PREFLIGHT_OK rows=2",
        "DAMAGE_HIT_MUTATION_TAINTED mode=",
        "REPORT SCRIPT ERROR",
        "Save succeeded for processed file: /BEA.exe",
    ]
    specific = {
        "probe-after-one": [
            "DAMAGE_HIT_FORCED_AFTER_ONE_FAILURE rollback_required=true",
            "recovery=RESTORE_VERIFIED_SCRATCH_BASE",
            "intentional Damage/Hit after-one rollback probe",
        ],
        "probe-post-inner": [
            "DAMAGE_HIT_COMPENSATING_PRE_RESTORE_COMPLETE rows=2",
            "DAMAGE_HIT_FORCED_POST_INNER_FAILURE pre_restored=true",
            "recovery=COMPENSATING_PRE_RESTORE_VERIFIED",
            "intentional Damage/Hit post-inner rollback probe",
        ],
    }[name]
    for marker in common + specific:
        require(marker in text, f"{name} log lacks marker: {marker}")
    require(not (root / "damage-hit.tsv").exists(), f"{name} published success TSV")
    require(not (root / "damage-hit.ready.json").exists(), f"{name} published success READY")
    inventory = LANE / "runs-v2" / f"{name}-post-inventory"
    functions = inventory / "functions.tsv"
    program = inventory / "program.tsv"
    require_stamp(functions, PRE_FUNCTIONS_STAMP, f"{name} rollback functions")
    require_stamp(program, PRE_PROGRAM_STAMP, f"{name} rollback program")
    return {
        "failureLog": stamp(log),
        "functionsAfter": stamp(functions),
        "programAfter": stamp(program),
        "successArtifactsAbsent": True,
        "preStateRestoredExactly": True,
    }


def verify_pre_restore(expected: Mapping[str, Any]) -> dict[str, Any]:
    receipt = load_json(PRE_RESTORE)
    require(receipt.get("schemaVersion") == "onslaught-ghidra-project-backup.v2",
            "PRE restore schema differs")
    require(receipt.get("copyComparison", {}).get("matches") is True,
            "PRE restore comparison failed")
    readonly = receipt.get("readonlyOpen", {})
    require(readonly.get("opened") is True and readonly.get("contentStable") is True,
            "PRE restore read-only open failed")
    require(readonly.get("postOpenComparison", {}).get("matches") is True,
            "PRE restore changed while opened")
    require(project_fields(receipt["source"]) == expected,
            "PRE restore source identity differs")
    return stamp(PRE_RESTORE)


def validate_live_inspect(path: Path, expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    receipt = load_json(path)
    parse_utc(receipt.get("createdAtUtc"), f"{label} createdAtUtc")
    require(project_fields(receipt.get("manifest", {})) == expected,
            f"{label} manifest differs")
    return stamp(path)


def require_distinct_projects(roots: Sequence[Path]) -> None:
    resolved = [root.resolve() for root in roots]
    require(len(set(resolved)) == len(resolved), "project roots are not distinct")
    for index, left in enumerate(resolved):
        for right in resolved[index + 1:]:
            require(not os.path.samefile(left, right), f"project roots alias: {left} / {right}")


def build_scratch(generated_at: str, *, require_current_live_pre: bool = True) -> dict[str, Any]:
    parse_utc(generated_at, "generatedAtUtc")
    require_stamp(PRISTINE, (2_506_752, PROGRAM_SHA), "pristine specimen")
    require_stamp(TOOL, (TOOL_BYTES, TOOL_SHA), "Ghidra promotion tool")
    expected = pre_project()
    require_stamp(PRE_FUNCTIONS, PRE_FUNCTIONS_STAMP, "PRE functions")
    require_stamp(PRE_PROGRAM, PRE_PROGRAM_STAMP, "PRE program")
    restore = verify_pre_restore(expected)
    if require_current_live_pre:
        require(actual_project(LIVE) == expected, "maintainer project drifted from PRE backup")
    live_inspect = validate_live_inspect(LIVE_PRE_INSPECT, expected, "live PRE inspection")
    project_names = ["replica-a", "replica-b", "probe-after-one", "probe-post-inner"]
    require_distinct_projects([LIVE, PRE_BACKUP, *[LANE / "scratch-v2" / name for name in project_names]])
    copies = {name: validate_copy(name, expected) for name in project_names}
    replicas: dict[str, Any] = {}
    for name in ("replica-a", "replica-b"):
        replicas[name] = {
            "project": rel(LANE / "scratch-v2" / name),
            "dry": validate_run(name, f"{name}-dry", "dry"),
            "apply": validate_run(name, f"{name}-apply", "apply"),
            "readback": validate_run(name, f"{name}-readback", "readback"),
            "postInventory": validate_post_inventory(name, f"{name}-post-inventory"),
        }
    for phase in ("dry", "apply", "readback"):
        a_root = LANE / "runs-v2" / f"replica-a-{phase}"
        b_root = LANE / "runs-v2" / f"replica-b-{phase}"
        require((a_root / "damage-hit.tsv").read_bytes() == (b_root / "damage-hit.tsv").read_bytes(),
                f"replica {phase} TSVs differ")
        require(normalize_run_receipt(a_root / "damage-hit.ready.json") ==
                normalize_run_receipt(b_root / "damage-hit.ready.json"),
                f"replica {phase} receipts differ beyond time/path")
    require((LANE / "runs-v2/replica-a-post-inventory/functions.tsv").read_bytes() ==
            (LANE / "runs-v2/replica-b-post-inventory/functions.tsv").read_bytes(),
            "replica post function inventories differ")
    require((LANE / "runs-v2/replica-a-post-inventory/program.tsv").read_bytes() ==
            (LANE / "runs-v2/replica-b-post-inventory/program.tsv").read_bytes(),
            "replica post program inventories differ")
    adverse = {
        "probe-after-one": validate_adverse("probe-after-one"),
        "probe-post-inner": validate_adverse("probe-post-inner"),
    }
    return {
        "schema": SCHEMA,
        "phase": "SCRATCH_AUTHORITY",
        "verdict": "READY",
        "generatedAtUtc": generated_at,
        "claim": "TWO_EXACT_DAMAGE_HIT_METADATA_CHANGES_AUTHORIZED_FOR_ONE_LIVE_APPLY",
        "specimen": stamp(PRISTINE),
        "author": stamp(SCRIPT),
        "tool": stamp(TOOL),
        "generation12": {
            "campaignReadySha256": CAMPAIGN_SHA,
            "proofReadySha256": PROOF_SHA,
            "authorityReadySha256": AUTHORITY_SHA,
        },
        "pre": {
            "backupManifest": stamp(PRE_MANIFEST),
            "restoreReceipt": restore,
            "functions": stamp(PRE_FUNCTIONS),
            "program": stamp(PRE_PROGRAM),
            "liveInspection": live_inspect,
            "liveMatchesBackup": True,
        },
        "copies": copies,
        "replicas": replicas,
        "adverseControls": adverse,
        "delta": {
            "functionsChanged": 2,
            "addresses": ["0x00407350", "0x0040a890"],
            "functionCount": 8124,
            "instructionCount": 549872,
            "bodyBytesChanged": 0,
            "boundariesChanged": 0,
            "semanticNamesAuthorized": ["CBattleEngine__Hit", "CBattleEngine__Damage"],
        },
        "authorization": {
            "liveApplyAuthorized": True,
            "oneMutationProcess": True,
            "separateReadbackRequired": True,
            "postBackupAndRestoreRequired": True,
            "additionalClaimsAuthorized": False,
        },
        "limitations": [
            "The Damage runtime write set is bounded to one replicated invocation plus two zero-write controls.",
            "Hit zero-write evidence covers seven watched fields in one gap-free invocation, not all memory or paths.",
            "No complete behavior, lethal-path, negative-damage, or rebuild-ready claim is authorized.",
        ],
    }


def validate_post_backup(expected: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    backup = LANE / "backups" / "post-live"
    manifest_path = backup / "backup_manifest.json"
    receipt = load_json(manifest_path)
    require(receipt.get("sourceStable") is True, "POST backup source was unstable")
    require(receipt.get("copyComparison", {}).get("matches") is True,
            "POST backup comparison failed")
    require(project_fields(receipt["source"]) == expected, "POST backup source differs")
    require(project_fields(receipt["destination"]) == expected, "POST backup destination differs")
    require(actual_project(backup) == expected, "POST backup actual bytes differ")
    restore_path = LANE / "post-live-restore.ready.json"
    restore = load_json(restore_path)
    require(restore.get("copyComparison", {}).get("matches") is True,
            "POST restore comparison failed")
    readonly = restore.get("readonlyOpen", {})
    require(readonly.get("opened") is True and readonly.get("contentStable") is True,
            "POST restore read-only open failed")
    require(readonly.get("postOpenComparison", {}).get("matches") is True,
            "POST restore changed while opened")
    require(project_fields(restore["source"]) == expected, "POST restore source differs")
    return stamp(manifest_path), stamp(restore_path)


def build_live(generated_at: str) -> dict[str, Any]:
    parse_utc(generated_at, "generatedAtUtc")
    scratch = build_scratch(
        load_json(SCRATCH_READY)["generatedAtUtc"], require_current_live_pre=False)
    require(load_json(SCRATCH_READY) == scratch, "scratch authority receipt no longer verifies")
    live_apply = validate_run("live", "live-apply", "apply")
    live_readback = validate_run("live", "live-readback", "readback")
    live_inventory = validate_post_inventory("live", "live-post-inventory")
    for phase in ("apply", "readback"):
        live_root = LANE / "runs-v2" / f"live-{phase}"
        scratch_root = LANE / "runs-v2" / f"replica-a-{phase}"
        require((live_root / "damage-hit.tsv").read_bytes() ==
                (scratch_root / "damage-hit.tsv").read_bytes(),
                f"live {phase} TSV differs from scratch")
        require(normalize_run_receipt(live_root / "damage-hit.ready.json") ==
                normalize_run_receipt(scratch_root / "damage-hit.ready.json"),
                f"live {phase} receipt differs beyond time/path")
    require((LANE / "runs-v2/live-post-inventory/functions.tsv").read_bytes() ==
            (LANE / "runs-v2/replica-a-post-inventory/functions.tsv").read_bytes(),
            "live POST function inventory differs from scratch")
    require((LANE / "runs-v2/live-post-inventory/program.tsv").read_bytes() ==
            (LANE / "runs-v2/replica-a-post-inventory/program.tsv").read_bytes(),
            "live POST program inventory differs from scratch")
    expected = actual_project(LIVE)
    post_inspect = validate_live_inspect(
        LANE / "live-postapply-inspect.json", expected, "live POST inspection")
    post_manifest, post_restore = validate_post_backup(expected)
    require_distinct_projects([LIVE, PRE_BACKUP, LANE / "backups/post-live"])
    return {
        "schema": SCHEMA,
        "phase": "LIVE_PROMOTED",
        "verdict": "READY",
        "generatedAtUtc": generated_at,
        "claim": "DAMAGE_HIT_METADATA_PROMOTED_AND_SEPARATELY_READ_BACK",
        "author": stamp(SCRIPT),
        "tool": stamp(TOOL),
        "scratchAuthority": stamp(SCRATCH_READY),
        "live": {
            "project": str(LIVE.resolve()),
            "apply": live_apply,
            "readback": live_readback,
            "postInventory": live_inventory,
            "postInspection": post_inspect,
            "postBackupManifest": post_manifest,
            "postRestoreReceipt": post_restore,
        },
        "result": {
            "functionsChanged": 2,
            "addresses": ["0x00407350", "0x0040a890"],
            "functionCount": 8124,
            "instructionCount": 549872,
            "bodyBytesChanged": 0,
            "boundariesChanged": 0,
            "livePromotionApplied": True,
            "separateReadbackPassed": True,
            "recoverablePostBackupPassed": True,
        },
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
    generated = saved.get("generatedAtUtc")
    expected = builder(generated)
    require(saved == expected, f"receipt does not reproduce: {path}")
    return saved


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("seal-scratch", "verify-scratch", "seal-live", "verify-live"))
    args = parser.parse_args(argv)
    if args.command == "seal-scratch":
        payload = build_scratch(utc_now())
        publish(SCRATCH_READY, payload)
        verify_saved(SCRATCH_READY, build_scratch)
        print(f"DAMAGE_HIT_SCRATCH_AUTHORITY_READY sha256={sha256_file(SCRATCH_READY)}")
    elif args.command == "verify-scratch":
        verify_saved(SCRATCH_READY, build_scratch)
        print(f"DAMAGE_HIT_SCRATCH_AUTHORITY_VERIFIED sha256={sha256_file(SCRATCH_READY)}")
    elif args.command == "seal-live":
        payload = build_live(utc_now())
        publish(LIVE_READY, payload)
        verify_saved(LIVE_READY, build_live)
        print(f"DAMAGE_HIT_LIVE_PROMOTION_READY sha256={sha256_file(LIVE_READY)}")
    else:
        verify_saved(LIVE_READY, build_live)
        print(f"DAMAGE_HIT_LIVE_PROMOTION_VERIFIED sha256={sha256_file(LIVE_READY)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
