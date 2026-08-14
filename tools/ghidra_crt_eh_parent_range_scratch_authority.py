#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Seal and verify the db.18616 CRT EH parent-range scratch campaign."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


SCHEMA = "bea.ghidra.crt-eh-parent-range-scratch-authority.v1"
MUTATOR_SCHEMA = "bea.ghidra.crt-eh-parent-range-repair.v1"
POLICY = "LIVE_FORBIDDEN"
RECEIPT_REL = Path("authority/scratch-authority.ready.json")
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PACKAGE = REPO_ROOT / "local-lab/crt-eh-parent-repair-db18616-20260814-v1/formal"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
PROGRAM_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
MANIFEST_SHA256 = "272062f47b6ef2c45a29e1bbe07a0f186ac1ae6ad8259bfd4f0a3d33edcf8831"
DB18616_SHA256 = "f0d4988cfa1f36529ed3687816e231bfcc8323240e7d3f9837de48941b8f64fc"
STATIC_TREE_SHA256 = "da2506cf73127dfee89f1ddaabe13a742995c8eb2f84bfc668a714e824dfb0d8"
STATIC_RESULT_SHA256 = "dec2716598862c2838387e8a08fcd4a2f2172be4bebb06156ba56242a7fb995f"
ENTRY = "0x005d0a9f"
NAME = "CRT__LongJmpProbe_NoOp"
PRE_RANGES = "0x005d0a9f-0x005d0ad6;0x005d0aef-0x005d0b04"
REPAIR_RANGE = "0x005d0ad6-0x005d0aef"
POST_RANGES = "0x005d0a9f-0x005d0b04"
REPAIR_SHA256 = "e4be71ffc2e3b62db42a6ae7cedc791eaeb8f7c8c05e986bf0ece195613f414a"
LAYOUT_SHA256 = "4b9994ab4ef5418af4737cf919d43132d4b072bd96a585ba52da834e1dfacc1c"
PRE_COUNTS = {
    "functions": 8327,
    "bodyRanges": 8458,
    "ownedBytes": 1811418,
    "instructions": 551133,
    "references": 234478,
}
POST_COUNTS = {
    "functions": 8327,
    "bodyRanges": 8457,
    "ownedBytes": 1811443,
    "instructions": 551143,
    "references": 234478,
}

RUN_FILES = {
    "compile-dry": {"ghidra.log", "result.ready.json", "result.tsv", "script.log", "stdout.log"},
    "replica-a-dry": {"ghidra.log", "result.ready.json", "result.tsv", "script.log", "stdout.log"},
    "replica-a-apply": {"ghidra.log", "result.ready.json", "result.tsv", "script.log", "stdout.log"},
    "replica-a-readback": {"ghidra.log", "result.ready.json", "result.tsv", "script.log", "stdout.log"},
    "replica-b-dry": {"ghidra.log", "result.ready.json", "result.tsv", "script.log", "stdout.log"},
    "replica-b-apply": {"ghidra.log", "result.ready.json", "result.tsv", "script.log", "stdout.log"},
    "replica-b-readback": {"ghidra.log", "result.ready.json", "result.tsv", "script.log", "stdout.log"},
    "control-one-adverse": {"ghidra.log", "script.log", "stdout.log"},
    "control-one-adverse-readback": {"ghidra.log", "result.ready.json", "result.tsv", "script.log", "stdout.log"},
    "control-one-restored": {"ghidra.log", "result.ready.json", "result.tsv", "script.log", "stdout.log"},
    "control-all-adverse": {"ghidra.log", "script.log", "stdout.log"},
    "control-all-adverse-readback": {"ghidra.log", "result.ready.json", "result.tsv", "script.log", "stdout.log"},
    "control-all-restored": {"ghidra.log", "result.ready.json", "result.tsv", "script.log", "stdout.log"},
    "containment-external": {"ghidra.log", "script.log", "stdout.log"},
    "inventory-pre": {"functions.tsv", "ghidra.log", "program.tsv", "script.log", "stdout.log"},
    "inventory-post-a": {"functions.tsv", "ghidra.log", "inventory-diff.json", "program.tsv", "script.log", "stdout.log"},
    "inventory-post-b": {"functions.tsv", "ghidra.log", "inventory-diff.json", "program.tsv", "script.log", "stdout.log"},
}

STATIC_OUTPUTS = (
    "input-manifest.json", "delta.tsv", "candidates.tsv", "promotion-cohort.tsv",
    "demo-twins.tsv", "lineage-validation.tsv", "disassembly.tsv",
    "reconciliation.tsv", "falsifiers.tsv", "report.md", "result.ready.json",
)


class VerifyError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise VerifyError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(8 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def stamp(path: Path, root: Path | None = None) -> dict[str, Any]:
    require(path.is_file(), f"missing file: {path}")
    label = path.name if root is None else path.relative_to(root).as_posix()
    return {"path": label, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerifyError(f"invalid JSON {path}: {exc}") from exc
    require(isinstance(value, dict), f"JSON object required: {path}")
    return value


def is_reparse(path: Path) -> bool:
    attributes = getattr(os.lstat(path), "st_file_attributes", 0)
    return path.is_symlink() or bool(attributes & 0x400)


def tree_stamp(root: Path) -> dict[str, Any]:
    rows: list[tuple[str, int, str]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        require(not is_reparse(path), f"reparse point forbidden: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative == RECEIPT_REL.as_posix():
            continue
        size = path.stat().st_size
        rows.append((relative, size, sha256_file(path)))
    digest = hashlib.sha256()
    total = 0
    for relative, size, file_hash in rows:
        digest.update(f"{file_hash}\t{size}\t{relative}\n".encode("utf-8"))
        total += size
    return {"files": len(rows), "bytes": total, "sha256": digest.hexdigest()}


def tsv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def project_inventory(project_root: Path) -> dict[str, tuple[int, str]]:
    project = project_root / "BEA.gpr"
    rep = project_root / "BEA.rep"
    require(project.is_file() and rep.is_dir(), f"incomplete Ghidra project: {project_root}")
    files = [project] + sorted(path for path in rep.rglob("*") if path.is_file())
    result: dict[str, tuple[int, str]] = {}
    for path in files:
        require(not is_reparse(path), f"project reparse point forbidden: {path}")
        relative = path.relative_to(project_root).as_posix()
        result[relative] = (path.stat().st_size, sha256_file(path))
    return result


def manifest_inventory(receipt: dict[str, Any], key: str) -> dict[str, tuple[int, str]]:
    owner = receipt.get(key)
    require(isinstance(owner, dict), f"missing inventory owner: {key}")
    rows = owner.get("files")
    require(isinstance(rows, list), f"missing inventory rows: {key}")
    result = {str(row["relative_path"]): (int(row["size"]), str(row["sha256"])) for row in rows}
    require(len(result) == len(rows), f"duplicate project inventory row: {key}")
    require(owner.get("fileCount") == len(rows), f"project file count: {key}")
    require(owner.get("totalBytes") == sum(size for size, _ in result.values()), f"project byte count: {key}")
    return result


def validate_project_topology(root: Path) -> dict[str, Any]:
    backup = read_json(root / "backup/base-openability.json")
    require(backup.get("schemaVersion") == "onslaught-ghidra-project-backup.v2", "backup schema")
    require(backup.get("sourceStable") is True, "backup source stability")
    require(backup.get("copyComparison", {}).get("matches") is True, "backup copy comparison")
    opened = backup.get("readonlyOpen", {})
    require(opened.get("opened") is True and opened.get("contentStable") is True, "backup read-only open")
    require(opened.get("exitCode") == 0, "backup open exit")
    argv = opened.get("commandArgv", [])
    require("-readOnly" in argv and "-noanalysis" in argv and "-commit" not in argv, "backup open safety argv")
    require(opened.get("observedProgramMd5") == PROGRAM_MD5, "backup observed MD5")
    require(opened.get("observedProgramSha256") == PROGRAM_SHA256, "backup observed SHA256")
    require(opened.get("postOpenComparison", {}).get("matches") is True, "backup post-open stability")
    probe_log = root / "backup" / str(opened.get("probeLog", {}).get("path"))
    require(stamp(probe_log)["bytes"] == opened["probeLog"]["bytes"], "probe log bytes")
    require(sha256_file(probe_log) == opened["probeLog"]["sha256"], "probe log hash")
    require("GHIDRA_PROJECT_OPEN_PROBE_OK" in probe_log.read_text(encoding="utf-8", errors="replace"), "probe log sentinel")

    base = project_inventory(root / "projects/base")
    require(base == manifest_inventory(backup, "source"), "base project differs from backup receipt")
    require(len(base) == 19 and sum(size for size, _ in base.values()) == 187009925, "base project totals")
    db16 = "BEA.rep/idata/00/~00000000.db/db.18616.gbf"
    db15 = "BEA.rep/idata/00/~00000000.db/db.18615.gbf"
    db17 = "BEA.rep/idata/00/~00000000.db/db.18617.gbf"
    require(base.get(db16) == (68354048, DB18616_SHA256), "base db.18616 identity")
    require(db15 in base and db17 not in base, "base database generation topology")

    probe_dirs = [path for path in (root / "openability-probe").iterdir() if path.is_dir()]
    require(len(probe_dirs) == 1, "retained openability probe count")
    require(project_inventory(probe_dirs[0]) == base, "retained openability probe differs from base")

    for name in ("control-one-restored", "control-all-restored"):
        require(project_inventory(root / "projects" / name) == base, f"{name} is not exact PRE")
        inspect = read_json(root / "projects" / f"{name}.inspect.json")
        require(manifest_inventory(inspect, "manifest") == base, f"{name} inspection differs")

    post_inventories: dict[str, dict[str, tuple[int, str]]] = {}
    for name in ("replica-a", "replica-b", "control-one", "control-all"):
        actual = project_inventory(root / "projects" / name)
        inspect = read_json(root / "projects" / f"{name}.inspect.json")
        require(actual == manifest_inventory(inspect, "manifest"), f"{name} inspection differs")
        require(len(actual) == 19 and sum(size for size, _ in actual.values()) == 187009925, f"{name} totals")
        require(db15 not in actual and db17 in actual, f"{name} generation topology")
        require(actual.get(db16) == base[db16], f"{name} changed db.18616")
        for path, value in base.items():
            if path != db15:
                require(actual.get(path) == value, f"{name} collateral project drift: {path}")
        post_inventories[name] = actual
    common_paths = set(post_inventories["replica-a"]) - {db17}
    require(all({path: values[path] for path in common_paths} ==
                {path: post_inventories["replica-a"][path] for path in common_paths}
                for values in post_inventories.values()), "post/control collateral inventories differ")
    return {"baseFiles": len(base), "baseBytes": sum(size for size, _ in base.values()), "db18616": DB18616_SHA256}


def validate_run_files(root: Path) -> None:
    runs = root / "runs"
    actual: dict[str, set[str]] = {}
    for directory in runs.iterdir():
        if directory.is_dir():
            names = {path.name for path in directory.iterdir() if path.is_file()}
            if names:
                actual[directory.name] = names
            require(not any(path.is_dir() for path in directory.iterdir()), f"nested run directory: {directory}")
    require(actual == RUN_FILES, f"run file census differs: {actual}")


def validate_result_row(path: Path, mode: str, post: bool) -> None:
    rows = tsv_rows(path)
    require(len(rows) == 1, f"result row count: {path}")
    row = rows[0]
    expected = {
        "entry": ENTRY, "name": NAME, "mode": mode,
        "status": "POST_VERIFIED" if post else "PRE_VERIFIED",
        "preBodyRanges": PRE_RANGES, "repairRanges": REPAIR_RANGE,
        "postBodyRanges": POST_RANGES, "repairBytes": "25",
        "repairSha256": REPAIR_SHA256, "repairInstructions": "10",
        "repairInstructionLayoutSha256": LAYOUT_SHA256,
        "actualBodyRanges": POST_RANGES if post else PRE_RANGES,
        "actualRepairInstructions": "10" if post else "0",
        "actualRepairInstructionLayoutSha256": LAYOUT_SHA256 if post else "",
        "rollbackVerified": "false",
    }
    require(row == expected, f"result semantics differ: {path}: {row}")


def validate_ready(root: Path, run_name: str, mode: str, post: bool) -> None:
    run = root / "runs" / run_name
    ready = read_json(run / "result.ready.json")
    require(ready.get("schema") == MUTATOR_SCHEMA, f"ready schema: {run_name}")
    require(ready.get("status") == "READY_FOR_SCRATCH_ONLY" and ready.get("policy") == POLICY, f"ready policy: {run_name}")
    require(ready.get("mode") == mode, f"ready mode: {run_name}")
    manifest = stamp(root / "static/final-a/fragment-manifest.tsv")
    tool = stamp(root / "tools/GhidraApplyCrtEhParentRange.java")
    output = stamp(run / "result.tsv")
    require(ready.get("manifest") == {"name": "fragment-manifest.tsv", "bytes": manifest["bytes"], "sha256": manifest["sha256"]}, f"ready manifest: {run_name}")
    require(ready.get("tool") == {"name": "GhidraApplyCrtEhParentRange.java", "bytes": tool["bytes"], "sha256": tool["sha256"]}, f"ready tool: {run_name}")
    require(ready.get("output") == {"name": "result.tsv", "bytes": output["bytes"], "sha256": output["sha256"]}, f"ready output: {run_name}")
    require(ready.get("program") == {"name": "BEA.exe", "md5": PROGRAM_MD5, "sha256": PROGRAM_SHA256}, f"ready program: {run_name}")
    expected_counts = POST_COUNTS if post else PRE_COUNTS
    require(ready.get("countsBefore") == (PRE_COUNTS if mode == "apply" else expected_counts), f"ready before counts: {run_name}")
    require(ready.get("countsAfter") == expected_counts, f"ready after counts: {run_name}")
    require(ready.get("targets") == 1 and ready.get("repairBytes") == 25, f"ready repair totals: {run_name}")
    require(ready.get("postVerified") is post and ready.get("rollbackVerified") is False, f"ready verification flags: {run_name}")
    require(ready.get("newFunctionsAuthorized") is False and ready.get("namesSignaturesCommentsTagsDataAuthorized") is False, f"ready authority boundary: {run_name}")
    require(ready.get("separateSavedReadbackRequired") is (mode == "apply"), f"ready readback flag: {run_name}")
    validate_result_row(run / "result.tsv", mode, post)


def validate_runs(root: Path) -> None:
    validate_run_files(root)
    dry_runs = (
        "compile-dry", "replica-a-dry", "replica-b-dry",
        "control-one-adverse-readback", "control-one-restored",
        "control-all-adverse-readback", "control-all-restored",
    )
    for run in dry_runs:
        validate_ready(root, run, "dry", False)
    for replica in ("a", "b"):
        validate_ready(root, f"replica-{replica}-apply", "apply", True)
        validate_ready(root, f"replica-{replica}-readback", "readback", True)

    baseline = (root / "runs/compile-dry/result.tsv").read_bytes()
    require(all((root / "runs" / run / "result.tsv").read_bytes() == baseline for run in dry_runs), "PRE result TSVs differ")
    require((root / "runs/replica-a-apply/result.tsv").read_bytes() == (root / "runs/replica-b-apply/result.tsv").read_bytes(), "apply replica TSVs differ")
    require((root / "runs/replica-a-readback/result.tsv").read_bytes() == (root / "runs/replica-b-readback/result.tsv").read_bytes(), "readback replica TSVs differ")

    for which, mode in (("one", "probe-after-one"), ("all", "probe-after-all")):
        run = root / "runs" / f"control-{which}-adverse"
        text = (run / "stdout.log").read_text(encoding="utf-8", errors="replace")
        require(f"CRT_EH_PARENT_RANGE_ADVERSE_CONTROL mode={mode}" in text, f"missing adverse sentinel: {which}")
        require("IntentionalProbeException" in text and "Save succeeded" in text, f"incomplete adverse evidence: {which}")
        require(not (run / "result.tsv").exists() and not (run / "result.ready.json").exists(), f"adverse control published output: {which}")

    external = (root / "runs/containment-external/stdout.log").read_text(encoding="utf-8", errors="replace")
    require("escapes package root" in external, "external output containment refusal")
    tamper_root = root / "controls/tampered-manifest"
    require(sha256_file(tamper_root / "static/final-a/fragment-manifest.tsv") != MANIFEST_SHA256, "tampered manifest is not tampered")
    tamper = (tamper_root / "logs/stdout.log").read_text(encoding="utf-8", errors="replace")
    require("manifest sha256" in tamper and "SCRIPT ERROR" in tamper, "tampered manifest refusal")


def function_rows(path: Path) -> tuple[list[str], dict[str, dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        require(reader.fieldnames is not None, f"function inventory header: {path}")
        rows = {row["address"]: row for row in reader}
        require(len(rows) == 8327, f"function inventory count: {path}")
        return list(reader.fieldnames), rows


def program_rows(path: Path) -> dict[str, str]:
    rows = tsv_rows(path)
    result: dict[str, str] = {}
    for row in rows:
        require(row["metric"] not in result, f"duplicate program metric: {path}")
        result[row["metric"]] = row["value"]
    return result


def validate_inventories(root: Path) -> dict[str, Any]:
    pre_path = root / "runs/inventory-pre/functions.tsv"
    post_a_path = root / "runs/inventory-post-a/functions.tsv"
    post_b_path = root / "runs/inventory-post-b/functions.tsv"
    require(post_a_path.read_bytes() == post_b_path.read_bytes(), "post function inventories differ")
    fields, pre = function_rows(pre_path)
    post_fields, post = function_rows(post_a_path)
    require(fields == post_fields and set(pre) == set(post), "function inventory topology differs")
    changed: dict[str, tuple[dict[str, str], dict[str, str]]] = {}
    for address in pre:
        if pre[address] != post[address]:
            changed[address] = (pre[address], post[address])
    require(set(changed) == {ENTRY}, f"unexpected function row drift: {sorted(changed)}")
    before, after = changed[ENTRY]
    allowed = {"bodyBytes", "bodyDigest", "bodyRanges", "instrCount"}
    require({field for field in fields if before[field] != after[field]} == allowed, "target function changed unauthorized fields")
    require(before["name"] == NAME and before["bodyBytes"] == "76" and after["bodyBytes"] == "101", "target body byte delta")
    require(before["bodyRanges"] == "2" and after["bodyRanges"] == "1", "target body range delta")
    require(before["instrCount"] == "28" and after["instrCount"] == "38", "target instruction delta")
    require(before["bodyMin"] == after["bodyMin"] == "0x005d0a9f" and before["bodyMax"] == after["bodyMax"] == "0x005d0b03", "target envelope")

    pre_program_path = root / "runs/inventory-pre/program.tsv"
    post_a_program_path = root / "runs/inventory-post-a/program.tsv"
    post_b_program_path = root / "runs/inventory-post-b/program.tsv"
    require(post_a_program_path.read_bytes() == post_b_program_path.read_bytes(), "post program inventories differ")
    pre_program = program_rows(pre_program_path)
    post_program = program_rows(post_a_program_path)
    require(set(pre_program) == set(post_program), "program metric topology differs")
    changed_metrics = {key for key in pre_program if pre_program[key] != post_program.get(key)}
    require(changed_metrics == {"instructions", "instructionLayoutSha256", "undefinedData"}, f"program collateral drift: {changed_metrics}")
    require(pre_program["instructions"] == "551133" and post_program["instructions"] == "551143", "program instruction delta")
    require(pre_program["undefinedData"] == "3907928" and post_program["undefinedData"] == "3907903", "program undefined-data delta")
    require(pre_program["references"] == post_program["references"] == "234478", "program reference stability")
    for replica in ("a", "b"):
        diff = read_json(root / "runs" / f"inventory-post-{replica}" / "inventory-diff.json")
        require(diff.get("counts") == {"after": 8327, "before": 8327, "boundsChanged": 1, "callingConvChanged": 0, "created": 0, "destroyed": 0, "instrCountChanged": 1, "namesChanged": 0, "noReturnChanged": 0, "paramCountChanged": 0, "returnTypeChanged": 0, "sigSourceChanged": 0, "signaturesChanged": 0, "thunkFlagChanged": 0}, f"inventory diff counts: {replica}")
        require(diff.get("dangerous", {}).get("gradedBoundsMovedCount") == 1, f"intended reviewed-body repair absent: {replica}")
        require(diff.get("dangerous", {}).get("gradedDestroyedCount") == 0 and diff.get("dangerous", {}).get("gradedRenamedCount") == 0 and diff.get("dangerous", {}).get("gradedDemotedCount") == 0, f"dangerous collateral drift: {replica}")
    return {"unchangedFunctionRows": 8326, "changedFunctionRows": 1, "instructionsAdded": 10, "ownedBytesAdded": 25, "bodyRangesRemoved": 1}


def canonical_static_tree(path: Path) -> str:
    digest = hashlib.sha256()
    actual = {item.name for item in path.iterdir() if item.is_file()}
    require(actual == set(STATIC_OUTPUTS), f"static replica files: {path}")
    for name in STATIC_OUTPUTS:
        item = path / name
        digest.update(f"{sha256_file(item)}\t{item.stat().st_size}\t{name}\n".encode("utf-8"))
    return digest.hexdigest()


def validate_static(root: Path) -> dict[str, Any]:
    static = root / "static/crt22-corrected"
    run_c = static / "run-c"
    run_d = static / "run-d"
    require(canonical_static_tree(run_c) == STATIC_TREE_SHA256, "corrected CRT22 run-c tree")
    require(canonical_static_tree(run_d) == STATIC_TREE_SHA256, "corrected CRT22 run-d tree")
    require(all((run_c / name).read_bytes() == (run_d / name).read_bytes() for name in STATIC_OUTPUTS), "corrected CRT22 replicas differ")
    receipt = read_json(static / "current-db18616-static-verification.ready.json")
    require(receipt.get("schema") == "bea.re.crt22-current-gap-recovery-verifier.v1", "static verifier schema")
    require(receipt.get("replicaTreeSha256") == STATIC_TREE_SHA256 and receipt.get("analysisResultSha256") == STATIC_RESULT_SHA256, "static verifier result")
    checks = receipt.get("checks", {})
    require(checks.get("parentRepairs") == 1 and checks.get("currentParentBoundariesReconciled") is True and checks.get("demoNormalizedCfgTwins") == 26, "static verifier claims")
    require(sha256_file(run_c / "result.ready.json") == STATIC_RESULT_SHA256, "static analysis result hash")
    cohort = {row["entry"]: row for row in tsv_rows(run_c / "promotion-cohort.tsv")}
    require(cohort["0x005D0A9F"] == {"priority": "REPAIR", "action": "REPAIR_EXISTING_FUNCTION_BODY", "entry": "0x005D0A9F", "body_ranges": "0x005D0A9F-0x005D0B04", "body_bytes": "101", "body_sha256": "50016632446f1259b35479440c4a14ca82c8ac59a6c4f78a34f146bd119b61c3", "safe_name_candidate": "CRT__LongJmpProbe_NoOp", "name_policy": "PRESERVE_CURRENT_NAME", "scratch_gate": "admit 0x005D0AD6-0x005D0AEF into parent only; forbid new entries at filter and handler"}, "static parent-repair row")
    candidates = {row["retail_entry"]: row for row in tsv_rows(run_c / "candidates.tsv")}
    require(candidates["0x005D0AD6"]["classification"] == "EH_FILTER_FUNCLET" and candidates["0x005D0AD6"]["recommended_action"] == "REPAIR_PARENT_BODY_ONLY", "static EH classification")
    demo = {row["retail_entry"]: row for row in tsv_rows(run_c / "demo-twins.tsv")}
    require(demo["0x005D0AD6"]["demo_entry"] == "0x005D11D6" and demo["0x005D0AD6"]["normalized_equal"] == "true" and demo["0x005D0AD6"]["cfg_equal"] == "true", "static demo twin")
    return {"replicaTreeSha256": STATIC_TREE_SHA256, "analysisResultSha256": STATIC_RESULT_SHA256, "parentRepairs": 1}


def validate_manifest(root: Path) -> dict[str, Any]:
    path = root / "static/final-a/fragment-manifest.tsv"
    require(path.stat().st_size == 464 and sha256_file(path) == MANIFEST_SHA256, "formal manifest identity")
    rows = tsv_rows(path)
    require(len(rows) == 1, "formal manifest row count")
    row = rows[0]
    require(row == {"entry": ENTRY, "current_name": NAME, "pre_body_ranges": PRE_RANGES, "repair_ranges": REPAIR_RANGE, "post_body_ranges": POST_RANGES, "repair_bytes": "25", "repair_sha256": REPAIR_SHA256, "repair_instruction_count": "10", "repair_instruction_layout_sha256": LAYOUT_SHA256, "mutation_scope": "BODY_RANGE_AND_BOUNDED_DISASSEMBLY_ONLY"}, "formal manifest semantics")
    return stamp(path, root)


def validate_semantics(root: Path) -> dict[str, Any]:
    require(root.is_dir(), f"missing package root: {root}")
    require(not is_reparse(root), f"package root may not be a reparse point: {root}")
    manifest = validate_manifest(root)
    validate_runs(root)
    projects = validate_project_topology(root)
    inventories = validate_inventories(root)
    static = validate_static(root)
    require(not (root / "../external-control.tsv").resolve().exists(), "external control TSV exists")
    require(not (root / "../external-control.ready.json").resolve().exists(), "external control READY exists")
    return {"manifest": manifest, "projects": projects, "inventories": inventories, "static": static}


def receipt_artifacts(root: Path) -> dict[str, Any]:
    paths = {
        "mutator": "tools/GhidraApplyCrtEhParentRange.java",
        "manifest": "static/final-a/fragment-manifest.tsv",
        "staticVerifier": "static/crt22-corrected/current-db18616-static-verification.ready.json",
        "backup": "backup/base-openability.json",
        "replicaAApply": "runs/replica-a-apply/result.ready.json",
        "replicaAReadback": "runs/replica-a-readback/result.ready.json",
        "replicaBApply": "runs/replica-b-apply/result.ready.json",
        "replicaBReadback": "runs/replica-b-readback/result.ready.json",
        "preFunctions": "runs/inventory-pre/functions.tsv",
        "postFunctionsA": "runs/inventory-post-a/functions.tsv",
        "postFunctionsB": "runs/inventory-post-b/functions.tsv",
    }
    return {key: stamp(root / relative, root) for key, relative in paths.items()}


def build_receipt(root: Path) -> dict[str, Any]:
    semantics = validate_semantics(root)
    return {
        "schema": SCHEMA,
        "status": "SEALED_SCRATCH_READY_LIVE_FORBIDDEN",
        "policy": POLICY,
        "tree": tree_stamp(root),
        "artifacts": receipt_artifacts(root),
        "claims": {
            "functions": {"pre": 8327, "post": 8327, "delta": 0},
            "bodyRanges": {"pre": 8458, "post": 8457, "delta": -1},
            "ownedBytes": {"pre": 1811418, "post": 1811443, "delta": 25},
            "instructions": {"pre": 551133, "post": 551143, "delta": 10},
            "references": {"pre": 234478, "post": 234478, "delta": 0},
            "unchangedFunctionRows": 8326,
            "changedFunctionRows": 1,
            "newFunctionEntriesAuthorized": 0,
            "forbiddenEntries": ["0x005d0ad6", "0x005d0aea"],
            "liveMutationAuthorized": False,
        },
        "semanticSummary": semantics,
    }


def verify_receipt(root: Path) -> dict[str, Any]:
    receipt_path = root / RECEIPT_REL
    receipt = read_json(receipt_path)
    require(receipt.get("schema") == SCHEMA, "authority schema")
    require(receipt.get("status") == "SEALED_SCRATCH_READY_LIVE_FORBIDDEN" and receipt.get("policy") == POLICY, "authority status")
    semantics = validate_semantics(root)
    require(receipt.get("semanticSummary") == semantics, "authority semantic summary")
    require(receipt.get("artifacts") == receipt_artifacts(root), "authority artifact stamps")
    require(receipt.get("tree") == tree_stamp(root), "authority tree differs")
    claims = receipt.get("claims", {})
    require(claims.get("unchangedFunctionRows") == 8326 and claims.get("changedFunctionRows") == 1, "authority function-row claims")
    require(claims.get("liveMutationAuthorized") is False and claims.get("newFunctionEntriesAuthorized") == 0, "authority mutation boundary")
    return receipt


def write_receipt(root: Path, receipt: dict[str, Any]) -> Path:
    output = root / RECEIPT_REL
    require(not output.exists(), f"authority receipt already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode("utf-8")
    handle, temporary_name = tempfile.mkstemp(prefix=".scratch-authority.", suffix=".partial", dir=output.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    return output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("seal", "verify"))
    parser.add_argument("--root", type=Path, default=DEFAULT_PACKAGE)
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.mode == "seal":
            output = write_receipt(root, build_receipt(root))
            receipt = verify_receipt(root)
            print(f"CRT_EH_PARENT_SCRATCH_SEALED functions={receipt['claims']['functions']['post']} owned={receipt['claims']['ownedBytes']['post']} receipt={sha256_file(output)}")
        else:
            receipt = verify_receipt(root)
            print(f"CRT_EH_PARENT_SCRATCH_VERIFIED functions={receipt['claims']['functions']['post']} owned={receipt['claims']['ownedBytes']['post']} tree={receipt['tree']['sha256']}")
    except VerifyError as exc:
        print(f"REFUSED: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
