#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Verify and seal an already-completed Ghidra live promotion.

The verifier is deliberately read-only with one exception: ``seal`` creates
the requested aggregate JSON receipt.  It never launches Ghidra.  Promotion-
specific facts live in a tracked manifest so later cohorts can reuse this
mechanism without cloning another one-shot authority program.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import ghidra_project_backup as project_backup  # noqa: E402
import re_ghidra_name_projection as name_projection  # noqa: E402


RECEIPT_SCHEMA = "bea.ghidra.live-promotion-authority.v1"
MANIFEST_SCHEMA = "bea.ghidra.live-promotion-manifest.v1"


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


def stamp(path: Path, label: str | None = None) -> dict[str, Any]:
    require(path.is_file(), f"{label or path} is absent: {path}")
    return {"bytes": path.stat().st_size, "sha256": sha256_file(path)}


def load_json(path: Path, label: str | None = None) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AuthorityError(f"{label or path} is not valid UTF-8 JSON") from exc
    require(isinstance(value, dict), f"{label or path} must contain a JSON object")
    return value


def parse_utc(value: Any, label: str) -> datetime:
    require(isinstance(value, str) and value.endswith("Z"), f"{label} is not UTC")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise AuthorityError(f"{label} is malformed") from exc
    return parsed


def expect_stamp(
    path: Path,
    expected: Mapping[str, Any],
    label: str,
    *,
    role: str,
) -> dict[str, Any]:
    measured = stamp(path, label)
    require(
        measured == {"bytes": expected.get("bytes"), "sha256": expected.get("sha256")},
        f"{label} stamp differs: expected={dict(expected)} actual={measured}",
    )
    return {"role": role, **measured}


def clean_path(path: Path) -> Path:
    return Path(os.path.abspath(path))


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


@dataclass(frozen=True)
class Config:
    repo: Path
    manifest_path: Path
    live_lane: Path
    pre_readback: Path
    scratch_receipt: Path
    live_project: Path
    pre_backup: Path
    post_backup: Path
    output: Path

    @property
    def tracked_project(self) -> Path:
        return self.repo / "reverse-engineering/ghidra"

    @property
    def authority_repo(self) -> Path:
        return Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class TsvTable:
    fields: tuple[str, ...]
    order: tuple[str, ...]
    rows: Mapping[str, Mapping[str, str]]
    raw_rows: Mapping[str, bytes]


def load_keyed_tsv(path: Path, key: str, *, lowercase_key: bool = True) -> TsvTable:
    raw = path.read_bytes()
    require(raw.endswith(b"\n") and b"\r" not in raw, f"{path} must be LF-only with final LF")
    lines = raw.splitlines()
    require(lines, f"{path} is empty")
    try:
        fields = tuple(lines[0].decode("utf-8").split("\t"))
        text = raw.decode("utf-8")
    except UnicodeError as exc:
        raise AuthorityError(f"{path} is not UTF-8") from exc
    require(key in fields and len(fields) == len(set(fields)), f"{path} header differs")
    reader = csv.DictReader(text.splitlines(), delimiter="\t")
    rows: dict[str, Mapping[str, str]] = {}
    raw_rows: dict[str, bytes] = {}
    order: list[str] = []
    for number, (row, raw_line) in enumerate(zip(reader, lines[1:]), start=2):
        value = row.get(key) or ""
        if lowercase_key:
            value = value.lower()
        require(value and value not in rows, f"{path}:{number} has duplicate/empty {key}")
        require(None not in row, f"{path}:{number} has surplus columns")
        rows[value] = dict(row)
        raw_rows[value] = raw_line
        order.append(value)
    require(len(order) == len(lines) - 1, f"{path} row parsing is incomplete")
    return TsvTable(fields, tuple(order), rows, raw_rows)


def load_program(path: Path) -> tuple[dict[str, str], tuple[str, ...]]:
    table = load_keyed_tsv(path, "metric", lowercase_key=False)
    require(table.fields == ("metric", "value"), f"{path} program header differs")
    return ({key: str(row["value"]) for key, row in table.rows.items()}, table.order)


def project_value(root: Path) -> dict[str, Any]:
    try:
        manifest = project_backup.build_manifest(root, "BEA")
    except project_backup.BackupError as exc:
        raise AuthorityError(str(exc)) from exc
    files = [row.to_json() for row in manifest.files]
    return {
        "projectName": "BEA",
        "fileCount": len(files),
        "totalBytes": sum(int(row["size"]) for row in files),
        "structurallyComplete": True,
        "files": files,
    }


def project_digest(value: Mapping[str, Any]) -> str:
    lines = sorted(
        f"{row['sha256']}\t{row['size']}\t{row['relative_path']}"
        for row in value.get("files", [])
    )
    raw = ("\n".join(lines) + "\n").encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def project_summary(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "fileCount": value.get("fileCount"),
        "totalBytes": value.get("totalBytes"),
        "canonicalInventorySha256": project_digest(value),
    }


def project_fields(value: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value.get(key) for key in
            ("projectName", "fileCount", "totalBytes", "structurallyComplete", "files")}


def exact_comparison(value: Mapping[str, Any], label: str) -> None:
    require(
        value.get("matches") is True
        and all(value.get(key) == 0 for key in
                ("missingCount", "extraCount", "sizeDiffCount", "hashDiffCount"))
        and all(value.get(key) == [] for key in
                ("missing", "extra", "sizeDifferences", "hashDifferences")),
        f"{label} does not report exact equality",
    )


def validate_manifest(config: Config) -> dict[str, Any]:
    manifest = load_json(config.manifest_path, "promotion manifest")
    require(manifest.get("schema") == MANIFEST_SCHEMA, "promotion manifest schema differs")
    require(manifest.get("id"), "promotion manifest id is absent")
    return manifest


def validate_stamps(config: Config, manifest: Mapping[str, Any]) -> dict[str, Any]:
    tracked: dict[str, Any] = {}
    for relative, expected in manifest.get("trackedFiles", {}).items():
        tracked[relative] = expect_stamp(
            config.repo / relative, expected, f"tracked {relative}", role=relative
        )
    artifacts: dict[str, Any] = {}
    for relative, expected in manifest.get("artifacts", {}).items():
        artifacts[relative] = expect_stamp(
            config.live_lane / relative,
            expected,
            f"live artifact {relative}",
            role=f"live-lane/{relative}",
        )
    excluded_roots = set(manifest.get("retainedProjectRoots", []))
    observed_artifacts = {
        str(path.relative_to(config.live_lane)).replace("\\", "/")
        for path in config.live_lane.rglob("*")
        if path.is_file()
        and path.relative_to(config.live_lane).parts[0] not in excluded_roots
    }
    require(
        observed_artifacts == set(artifacts),
        "live artifact census differs: "
        f"missing={sorted(set(artifacts) - observed_artifacts)} "
        f"extra={sorted(observed_artifacts - set(artifacts))}",
    )
    external = manifest["externalStamps"]
    pre_functions = expect_stamp(
        config.pre_readback / "functions.tsv",
        external["preFunctions"],
        "PRE functions",
        role="pre-readback/functions.tsv",
    )
    pre_program = expect_stamp(
        config.pre_readback / "program.tsv",
        external["preProgram"],
        "PRE program",
        role="pre-readback/program.tsv",
    )
    scratch = expect_stamp(
        config.scratch_receipt,
        external["scratchReceipt"],
        "scratch authority receipt",
        role="scratch-authority/ready.json",
    )
    pre_manifest = expect_stamp(
        config.pre_backup / "backup_manifest.json",
        external["preBackupManifest"],
        "PRE backup manifest",
        role="pre-backup/backup_manifest.json",
    )
    post_manifest = expect_stamp(
        config.post_backup / "backup_manifest.json",
        external["postBackupManifest"],
        "POST backup manifest",
        role="post-backup/backup_manifest.json",
    )
    return {
        "tracked": tracked,
        "liveArtifacts": artifacts,
        "external": {
            "preFunctions": pre_functions,
            "preProgram": pre_program,
            "scratchReceipt": scratch,
            "preBackupManifest": pre_manifest,
            "postBackupManifest": post_manifest,
        },
    }


def target_rows(config: Config, manifest: Mapping[str, Any]) -> dict[str, Mapping[str, str]]:
    spec = manifest["functionDelta"]
    table = load_keyed_tsv(config.repo / spec["targetManifest"], spec["targetAddressField"])
    require(len(table.rows) == spec["targets"], "target manifest count differs")
    return dict(table.rows)


def compare_function_inventories(
    pre_path: Path,
    post_path: Path,
    targets: Mapping[str, Mapping[str, str]],
    spec: Mapping[str, Any],
) -> dict[str, Any]:
    pre = load_keyed_tsv(pre_path, "address")
    post = load_keyed_tsv(post_path, "address")
    require(pre.fields == post.fields, "PRE/POST function headers differ")
    require(pre.order == post.order, "PRE/POST function address order differs")
    require(len(pre.rows) == len(post.rows) == spec["functionCount"], "function count differs")
    require(set(targets) <= set(pre.rows), "target manifest contains absent functions")

    non_targets = set(pre.rows) - set(targets)
    changed_non_targets = [key for key in sorted(non_targets)
                           if pre.raw_rows[key] != post.raw_rows[key]]
    require(not changed_non_targets,
            f"non-target function rows changed: {changed_non_targets[:5]}")
    require(len(non_targets) == spec["nonTargets"], "non-target count differs")

    expected_fields = set(spec["expectedChangedTargetFields"])
    observed_sets: set[tuple[str, ...]] = set()
    for address, target in targets.items():
        before = pre.rows[address]
        after = post.rows[address]
        changed = {field for field in pre.fields if before[field] != after[field]}
        require(changed == expected_fields,
                f"{address} changed fields differ: {sorted(changed)}")
        observed_sets.add(tuple(sorted(changed)))
        require(before["name"] == target[spec["expectedPreNameField"]],
                f"{address} PRE name differs")
        require(after["name"] == target[spec["proposedNameField"]],
                f"{address} POST name differs")
        require(before["nameSource"] == target[spec["expectedPreSourceField"]]
                and after["nameSource"] == spec["postNameSource"],
                f"{address} name-source transition differs")
        require(before["commentPresent"] == "false" and after["commentPresent"] == "true"
                and int(after["commentLen"]) > 0,
                f"{address} comment transition differs")
        require(before["repeatableCommentPresent"] == "false"
                and after["repeatableCommentPresent"] == "false"
                and before["repeatableCommentSha256"] == after["repeatableCommentSha256"],
                f"{address} repeatable comment changed")
        require(before["tagCount"] == "0" and after["tagCount"] == str(len(spec["postTags"]))
                and after["tags"] == ",".join(spec["postTags"]),
                f"{address} tag transition differs")
    require(len(observed_sets) == 1, "target field deltas are not uniform")
    return {
        "pre": stamp(pre_path),
        "post": stamp(post_path),
        "functions": len(pre.rows),
        "targets": len(targets),
        "nonTargetsByteIdentical": len(non_targets),
        "changedTargetFields": sorted(expected_fields),
        "preTable": pre,
        "postTable": post,
    }


def compare_programs(pre_path: Path, post_path: Path, spec: Mapping[str, Any]) -> dict[str, Any]:
    before, before_order = load_program(pre_path)
    after, after_order = load_program(post_path)
    require(before_order == after_order and set(before) == set(after), "program metric set differs")
    changed = {key for key in before if before[key] != after[key]}
    expected = spec["expectedChanges"]
    require(changed == set(expected), f"program changed metrics differ: {sorted(changed)}")
    for key, values in expected.items():
        require(before[key] == str(values["before"]) and after[key] == str(values["after"]),
                f"program metric {key} transition differs")
    return {
        "pre": stamp(pre_path),
        "post": stamp(post_path),
        "changedMetrics": sorted(changed),
        "changes": expected,
    }


def validate_inventory_diff(
    config: Config,
    manifest: Mapping[str, Any],
    targets: Mapping[str, Mapping[str, str]],
) -> dict[str, Any]:
    spec = manifest["inventoryDiff"]
    value = load_json(config.live_lane / spec["path"], "retained inventory diff")
    before = str(value.get("beforeFile", "")).replace("\\", "/")
    after = str(value.get("afterFile", "")).replace("\\", "/")
    require(before.endswith(spec["beforeSuffix"]) and after.endswith(spec["afterSuffix"]),
            "retained inventory-diff source roles differ")
    require(value.get("counts") == spec["counts"], "retained inventory-diff counts differ")
    require(value.get("created") == [] and value.get("destroyed") == [],
            "retained inventory-diff reports function creation/destruction")
    dangerous = value.get("dangerous", {})
    require(dangerous and all(item in (0, []) for item in dangerous.values()),
            "retained inventory-diff reports dangerous collateral")
    changes = value.get("changesByField", {})
    expected_lengths = spec["changesByField"]
    require(set(changes) == set(expected_lengths)
            and {key: len(rows) for key, rows in changes.items()} == expected_lengths,
            "retained inventory-diff field census differs")
    target_addresses = set(targets)
    for field, expected_count in expected_lengths.items():
        if expected_count:
            require({str(row.get("address", "")).lower() for row in changes[field]}
                    == target_addresses,
                    f"retained inventory-diff {field} target set differs")
    return {"stamp": stamp(config.live_lane / spec["path"]),
            "targets": len(target_addresses), "dangerousCollateral": 0}


def validate_tool_receipt(
    config: Config,
    manifest: Mapping[str, Any],
    phase: str,
) -> tuple[dict[str, Any], TsvTable, datetime]:
    run = manifest["runs"][phase]
    receipt_path = config.live_lane / run["receipt"]
    value = load_json(receipt_path, f"{phase} receipt")
    require(value.get("schema") == manifest["toolReceiptSchema"], f"{phase} schema differs")
    require(value.get("mode") == run["mode"] and value.get("state") == run["state"],
            f"{phase} mode/state differs")
    completed = parse_utc(value.get("completedAtUtc"), f"{phase} completedAtUtc")
    for claim, relative in manifest["receiptBindings"].items():
        measured = stamp(config.repo / relative)
        observed = value.get(claim, {})
        require((observed.get("bytes"), observed.get("sha256")) ==
                (measured["bytes"], measured["sha256"]),
                f"{phase} {claim} binding differs")
        require(observed.get("path") == relative, f"{phase} {claim} path differs")
    output_path = config.live_lane / run["output"]
    output = stamp(output_path)
    claim = value.get("output", {})
    require((claim.get("bytes"), claim.get("sha256")) ==
            (output["bytes"], output["sha256"]), f"{phase} output binding differs")
    require(str(claim.get("path", "")).replace("\\", "/").endswith(run["output"]),
            f"{phase} output path differs")
    program = manifest["program"]
    require(value.get("program") == {
        "name": program["name"], "md5": program["md5"],
        "sha256": program["sha256"], "functions": program["internalFunctions"],
        "instructions": program["instructions"],
    }, f"{phase} program identity differs")
    require(value.get("targets") == manifest["targetCensus"], f"{phase} target census differs")
    require(value.get("mutation") == manifest["mutationSummary"],
            f"{phase} mutation summary differs")
    expected_catalog = manifest["tagCatalog"]["pre" if run["state"] == "PRE" else "post"]
    require(value.get("tagCatalog") == expected_catalog, f"{phase} tag catalog differs")
    require(value.get("commitRequested") == (phase == "apply")
            and value.get("nestedEndReturnedCommitted") is False
            and value.get("loadedStateVerified") == (phase == "readback")
            and value.get("registryNamesAreOriginalCppSymbols") is False
            and value.get("runtimeBehaviorAuthorized") is False
            and value.get("reconstructionParityAuthorized") is False
            and value.get("liveMutationAuthorized") is False,
            f"{phase} claim boundary differs")
    return value, load_keyed_tsv(output_path, "handlerVa"), completed


def validate_runs(
    config: Config,
    manifest: Mapping[str, Any],
    targets: Mapping[str, Mapping[str, str]],
    functions: Mapping[str, Any],
) -> tuple[dict[str, Any], dict[str, datetime]]:
    receipts: dict[str, Any] = {}
    tables: dict[str, TsvTable] = {}
    times: dict[str, datetime] = {}
    for phase in ("dry", "apply", "readback"):
        receipt, table, completed = validate_tool_receipt(config, manifest, phase)
        require(len(table.rows) == len(targets), f"{phase} vocabulary row count differs")
        receipts[phase] = stamp(config.live_lane / manifest["runs"][phase]["receipt"])
        tables[phase] = table
        phase_paths = [
            config.live_lane / manifest["runs"][phase][key]
            for key in ("receipt", "output", "log")
        ]
        if phase == "readback":
            phase_paths.extend((
                config.live_lane / "runs/live-readback/functions.tsv",
                config.live_lane / "runs/live-readback/program.tsv",
            ))
        times[phase] = max(
            [completed]
            + [datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
               for path in phase_paths]
        )

    def without_mode(row: Mapping[str, str]) -> dict[str, str]:
        return {key: value for key, value in row.items() if key != "mode"}

    for address, target in targets.items():
        dry = tables["dry"].rows[address]
        apply = tables["apply"].rows[address]
        readback = tables["readback"].rows[address]
        require(without_mode(apply) == without_mode(readback),
                f"{address} apply/readback vocabulary differs")
        require(dry["state"] == "PRE" and apply["state"] == "POST",
                f"{address} vocabulary state differs")
        require(dry["name"] == target[manifest["functionDelta"]["expectedPreNameField"]]
                and apply["name"] == target[manifest["functionDelta"]["proposedNameField"]],
                f"{address} vocabulary name differs")
        require(dry["invariantSha256"] == apply["invariantSha256"]
                and dry["abiSha256"] == apply["abiSha256"]
                and dry["repeatableCommentSha256"] == apply["repeatableCommentSha256"],
                f"{address} vocabulary invariant differs")
        full = functions["postTable"].rows[address]
        for field in ("name", "nameSource", "commentLen", "commentSha256",
                      "repeatableCommentSha256", "tagCount", "tags"):
            require(apply[field] == full[field], f"{address} vocabulary/full {field} differs")

    log_paths = {str(path.relative_to(config.live_lane)).replace("\\", "/")
                 for path in (config.live_lane / "runs").rglob("ghidra.log")}
    expected_logs = {run["log"] for run in manifest["runs"].values()}
    require(log_paths == expected_logs,
            f"live Ghidra log census differs: expected={sorted(expected_logs)} actual={sorted(log_paths)}")
    writable = 0
    logs: dict[str, Any] = {}
    for phase, run in manifest["runs"].items():
        path = config.live_lane / run["log"]
        text = path.read_text(encoding="utf-8", errors="strict")
        require(text.count("Execute script: GhidraApplyMissionRegistryNewFunctionVocabulary.java") == 1,
                f"{phase} mutator execution count differs")
        require(all(text.count(item) == 1 for item in run["sentinels"]),
                f"{phase} success sentinel differs")
        require(not any(item in text for item in
                        ("MUTATION_TAINTED", "GHIDRA_PROJECT_OPEN_PROBE_FAIL", "SCRIPT ERROR")),
                f"{phase} log contains a failure sentinel")
        read_only = text.count("Processing read-only project file: /BEA.exe")
        saves = text.count("Save succeeded for processed file: /BEA.exe")
        require(read_only == (1 if run["readOnly"] else 0)
                and saves == run["saveCount"], f"{phase} read/write disposition differs")
        writable += int(saves == 1)
        logs[phase] = stamp(path)
    require(writable == 1, "live log census does not contain exactly one writable save")
    return {
        "receipts": receipts,
        "outputs": {phase: stamp(config.live_lane / run["output"])
                    for phase, run in manifest["runs"].items()},
        "logs": logs,
        "logCount": len(log_paths),
        "writableSaveLogs": writable,
        "applyReadbackByteEquivalentExceptMode": True,
        "completedAtUtc": {
            phase: value.isoformat().replace("+00:00", "Z")
            for phase, value in times.items()
        },
    }, times


def validate_scratch(
    config: Config,
    manifest: Mapping[str, Any],
    functions: Mapping[str, Any],
    program: Mapping[str, Any],
) -> dict[str, Any]:
    value = load_json(config.scratch_receipt, "scratch authority receipt")
    spec = manifest["scratch"]
    require(value.get("schema") == spec["schema"] and value.get("verdict") == spec["verdict"],
            "scratch authority identity differs")
    require(value.get("liveGhidraMutated") is False
            and value.get("trackedGhidraMutated") is False
            and value.get("liveMutationAuthorized") is False,
            "scratch authority claim boundary differs")
    evidence = value.get("evidence", {})
    require(evidence.get("postFunctionsReplicasByteIdentical") is True
            and evidence.get("postProgramReplicasByteIdentical") is True,
            "scratch replicas were not sealed byte-identical")
    collateral = evidence.get("functionCollateral", {})
    require(collateral.get("targets") == manifest["functionDelta"]["targets"]
            and collateral.get("nonTargetsByteIdentical") == manifest["functionDelta"]["nonTargets"]
            and collateral.get("changedTargetFields") == functions["changedTargetFields"],
            "scratch function collateral differs")
    require((collateral.get("pre", {}).get("bytes"), collateral.get("pre", {}).get("sha256")) ==
            (functions["pre"]["bytes"], functions["pre"]["sha256"])
            and (collateral.get("post", {}).get("bytes"), collateral.get("post", {}).get("sha256")) ==
            (functions["post"]["bytes"], functions["post"]["sha256"]),
            "scratch function stamps differ from live PRE/POST")
    program_collateral = evidence.get("programCollateral", {})
    require(program_collateral.get("changedMetrics") == program["changedMetrics"]
            and (program_collateral.get("pre", {}).get("bytes"),
                 program_collateral.get("pre", {}).get("sha256")) ==
                (program["pre"]["bytes"], program["pre"]["sha256"])
            and (program_collateral.get("post", {}).get("bytes"),
                 program_collateral.get("post", {}).get("sha256")) ==
                (program["post"]["bytes"], program["post"]["sha256"]),
            "scratch program collateral differs")
    require(set(evidence.get("positiveReplicas", {})) == {"replica-a", "replica-b"}
            and set(evidence.get("adverseControls", {})) ==
                {"probe-after-one", "probe-post-inner"}
            and evidence.get("baselineRestore")
            and evidence.get("postBackupRestore")
            and evidence.get("preTransactionPathControls"),
            "scratch ceremony gates are incomplete")
    return {
        "receipt": stamp(config.scratch_receipt),
        "verdict": value["verdict"],
        "replicas": 2,
        "adverseControls": 2,
        "postFunctionsMatchLive": True,
        "postProgramMatchesLive": True,
    }


def validate_backup_manifest(path: Path, expected: Mapping[str, Any], label: str) -> datetime:
    value = load_json(path, label)
    require(value.get("schemaVersion") == "onslaught-ghidra-project-backup.v2"
            and value.get("sourceStable") is True and value.get("readonlyOpen") is None,
            f"{label} boundary differs")
    exact_comparison(value.get("copyComparison", {}), f"{label} copy")
    require(project_fields(value.get("source", {})) == expected
            and project_fields(value.get("destination", {})) == expected,
            f"{label} project payload differs")
    return parse_utc(value.get("createdAtUtc"), f"{label} createdAtUtc")


def validate_restore(
    config: Config,
    manifest: Mapping[str, Any],
    spec: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> tuple[dict[str, Any], datetime]:
    path = config.live_lane / spec["receipt"]
    value = load_json(path, spec["receipt"])
    require(value.get("schemaVersion") == "onslaught-ghidra-project-backup.v2"
            and value.get("sourceStable") is True,
            f"{spec['receipt']} boundary differs")
    exact_comparison(value.get("copyComparison", {}), f"{spec['receipt']} copy")
    require(project_fields(value.get("source", {})) == expected,
            f"{spec['receipt']} source project differs")
    opened = value.get("readonlyOpen", {})
    program = manifest["program"]
    require(opened.get("opened") is True and opened.get("exitCode") == 0
            and opened.get("contentStable") is True
            and opened.get("observedProgramName") == program["name"]
            and opened.get("observedProgramMd5") == program["md5"]
            and opened.get("observedProgramSha256") == program["sha256"]
            and opened.get("observedFunctionCount") == program["aggregateFunctions"],
            f"{spec['receipt']} read-only open differs")
    exact_comparison(opened.get("postOpenComparison", {}), f"{spec['receipt']} post-open")
    argv = opened.get("commandArgv", [])
    require("-readOnly" in argv and "-noanalysis" in argv
            and "GhidraProjectOpenProbe.java" in argv,
            f"{spec['receipt']} was not a read-only no-analysis probe")
    probe = clean_path(Path(str(value.get("probeCopy", ""))))
    require(value.get("probeCopyDisposition") == "RETAINED_AT_VERIFICATION"
            and is_within(probe, clean_path(config.live_lane)),
            f"{spec['receipt']} retained probe path differs")
    require(project_value(probe) == expected, f"{spec['receipt']} retained probe differs")
    log_path = path.with_name(str(opened.get("probeLog", {}).get("path", "")))
    measured_log = stamp(log_path)
    claim = opened.get("probeLog", {})
    require((claim.get("bytes"), claim.get("sha256")) ==
            (measured_log["bytes"], measured_log["sha256"]),
            f"{spec['receipt']} probe-log binding differs")
    text = log_path.read_text(encoding="utf-8", errors="strict")
    sentinel = (f"GHIDRA_PROJECT_OPEN_PROBE_OK program={program['name']} "
                f"md5={program['md5']} sha256={program['sha256']} "
                f"functions={program['aggregateFunctions']}")
    require(text.count(sentinel) == 1 and "GHIDRA_PROJECT_OPEN_PROBE_FAIL" not in text,
            f"{spec['receipt']} probe sentinel differs")
    verified = parse_utc(value.get("verifiedAtUtc"), f"{spec['receipt']} verifiedAtUtc")
    return {
        "receipt": stamp(path), "probeLog": measured_log,
        "retainedProbeMatches": True, "readonlyOpen": True,
    }, verified


def inspect_time(path: Path, expected: Mapping[str, Any], label: str) -> datetime:
    value = load_json(path, label)
    require(value.get("schemaVersion") == "onslaught-ghidra-project-backup.v2"
            and project_fields(value.get("manifest", {})) == expected,
            f"{label} project differs")
    return parse_utc(value.get("createdAtUtc"), f"{label} createdAtUtc")


def validate_projects(
    config: Config,
    manifest: Mapping[str, Any],
    run_times: Mapping[str, datetime],
) -> dict[str, Any]:
    spec = manifest["projects"]
    current = {
        "live": project_value(config.live_project),
        "tracked": project_value(config.tracked_project),
        "preBackup": project_value(config.pre_backup),
        "postBackup": project_value(config.post_backup),
    }
    pre_expected = current["preBackup"]
    post_expected = current["postBackup"]
    require(project_summary(pre_expected) == spec["pre"], "PRE project summary differs")
    require(project_summary(post_expected) == spec["post"], "POST project summary differs")
    require(current["live"] == post_expected and current["tracked"] == post_expected,
            "current live/tracked projects differ from POST backup")
    pre_files = {
        row["relative_path"]: {"bytes": row["size"], "sha256": row["sha256"]}
        for row in pre_expected["files"]
    }
    post_files = {
        row["relative_path"]: {"bytes": row["size"], "sha256": row["sha256"]}
        for row in post_expected["files"]
    }
    project_delta = {
        "removed": sorted(set(pre_files) - set(post_files)),
        "added": sorted(set(post_files) - set(pre_files)),
        "changed": sorted(
            path for path in set(pre_files) & set(post_files)
            if pre_files[path] != post_files[path]
        ),
    }
    delta_spec = spec["delta"]
    require(project_delta == {
        "removed": delta_spec["removed"],
        "added": delta_spec["added"],
        "changed": delta_spec["changed"],
    }, f"PRE/POST project file delta differs: {project_delta}")
    require(
        {path: pre_files[path] for path in project_delta["removed"]}
        == delta_spec["removedRecords"]
        and {path: post_files[path] for path in project_delta["added"]}
        == delta_spec["addedRecords"],
        "PRE/POST rolling database identity differs",
    )

    times: dict[str, datetime] = {
        "livePreInspect": inspect_time(config.live_lane / "live-pre-inspect.json",
                                       pre_expected, "live PRE inspect"),
        "trackedPreInspect": inspect_time(config.live_lane / "tracked-pre-inspect.json",
                                          pre_expected, "tracked PRE inspect"),
        "safeStopInspect": inspect_time(config.live_lane / "live-safe-stop-inspect.json",
                                         pre_expected, "live safe-stop inspect"),
        "afterDryInspect": inspect_time(config.live_lane / "live-after-dry-inspect.json",
                                        pre_expected, "live after-dry inspect"),
        "livePostInspect": inspect_time(config.live_lane / "live-post-inspect.json",
                                        post_expected, "live POST inspect"),
        "trackedPostInspect": inspect_time(config.live_lane / "tracked-post-inspect.json",
                                           post_expected, "tracked POST inspect"),
        "dryCompleted": run_times["dry"], "applyCompleted": run_times["apply"],
        "readbackCompleted": run_times["readback"],
    }
    times["preBackupCreated"] = validate_backup_manifest(
        config.pre_backup / "backup_manifest.json", pre_expected, "PRE backup manifest"
    )
    times["postBackupCreated"] = validate_backup_manifest(
        config.post_backup / "backup_manifest.json", post_expected, "POST backup manifest"
    )
    restores: dict[str, Any] = {}
    for restore in manifest["restores"]:
        expected = pre_expected if restore["state"] == "PRE" else post_expected
        result, verified = validate_restore(config, manifest, restore, expected)
        restores[restore["name"]] = result
        times[restore["event"]] = verified
    for before, after in manifest["chronology"]:
        require(times[before] < times[after], f"chronology differs: {before} !< {after}")
    return {
        "pre": project_summary(pre_expected),
        "post": project_summary(post_expected),
        "liveTrackedPostBackupEqual": True,
        "delta": project_delta,
        "restores": restores,
        "chronology": [f"{before} < {after}" for before, after in manifest["chronology"]],
    }


def validate_projection(
    config: Config,
    manifest: Mapping[str, Any],
    post_functions: Path,
) -> dict[str, Any]:
    spec = manifest["projection"]
    expected = name_projection.projection_bytes(
        post_functions,
        expected_inventory_sha256=spec["sourceSha256"],
        source_label=spec["sourceLabel"],
        projection_date=spec["date"],
        specimen_sha256=manifest["program"]["sha256"],
    )
    tracked = config.repo / spec["trackedPath"]
    retained = config.live_lane / spec["retainedArtifact"]
    require(tracked.read_bytes() == expected and retained.read_bytes() == expected,
            "tracked/retained projection is not the mechanical POST projection")
    measured = {"bytes": len(expected), "sha256": hashlib.sha256(expected).hexdigest()}
    require(measured == spec["stamp"], "projection stamp differs")
    return {"tracked": {"path": spec["trackedPath"], **measured},
            "retained": {"path": spec["retainedArtifact"], **measured},
            "rows": manifest["program"]["internalFunctions"],
            "exactMechanicalProjection": True}


def validate_documentation(config: Config, manifest: Mapping[str, Any]) -> dict[str, Any]:
    checked: list[str] = []
    for contract in manifest.get("documentation", []):
        root_role = contract.get("root", "repo")
        roots = {"repo": config.repo, "authorityRepo": config.authority_repo}
        require(root_role in roots, f"unknown documentation root role: {root_role}")
        path = roots[root_role] / contract["path"]
        text = path.read_text(encoding="utf-8")
        missing = [item for item in contract.get("required", []) if item not in text]
        stale = [item for item in contract.get("forbidden", []) if item in text]
        require(not missing and not stale,
                f"documentation contract differs for {contract['path']}: missing={missing} stale={stale}")
        checked.append(f"{root_role}:{contract['path']}")
    return {"files": checked, "mutableSynthesisHashesPinned": False,
            "postFactsRequired": bool(checked)}


def build(config: Config) -> dict[str, Any]:
    manifest = validate_manifest(config)
    ledger = validate_stamps(config, manifest)
    targets = target_rows(config, manifest)
    post_functions = config.live_lane / "runs/live-readback/functions.tsv"
    post_program = config.live_lane / "runs/live-readback/program.tsv"
    functions = compare_function_inventories(
        config.pre_readback / "functions.tsv", post_functions,
        targets, manifest["functionDelta"],
    )
    program = compare_programs(
        config.pre_readback / "program.tsv", post_program, manifest["programDelta"]
    )
    inventory_diff = validate_inventory_diff(config, manifest, targets)
    runs, run_times = validate_runs(config, manifest, targets, functions)
    scratch = validate_scratch(config, manifest, functions, program)
    projects = validate_projects(config, manifest, run_times)
    projection = validate_projection(config, manifest, post_functions)
    documentation = validate_documentation(config, manifest)
    functions.pop("preTable")
    functions.pop("postTable")
    return {
        "manifestId": manifest["id"],
        "artifactLedger": ledger,
        "scratchAuthority": scratch,
        "liveRuns": runs,
        "functionCollateral": functions,
        "programCollateral": program,
        "retainedInventoryDiff": inventory_diff,
        "projectsAndRecovery": projects,
        "projection": projection,
        "documentation": documentation,
        "verdict": manifest["verdict"],
    }


def validate_output_path(config: Config, *, sealing: bool) -> None:
    output = clean_path(config.output)
    forbidden = [config.live_lane, config.live_project, config.pre_backup,
                 config.post_backup, config.tracked_project, config.scratch_receipt.parent]
    require(not any(is_within(output, clean_path(root)) for root in forbidden),
            "aggregate receipt overlaps an evidence/project root")
    if not sealing:
        require(output.is_file(), "saved aggregate receipt is absent")
        return
    local_lab = clean_path(config.authority_repo / "local-lab")
    require(is_within(output, local_lab), "aggregate receipt must be under repository local-lab")
    ignored = subprocess.run(
        ["git", "-C", str(config.authority_repo), "check-ignore", "-q", "--", str(output)],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    require(ignored.returncode == 0, "aggregate receipt path is not Git-ignored")


def atomic_new_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(not path.exists(), f"refusing to overwrite existing receipt: {path}")
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".partial", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def seal(config: Config) -> None:
    validate_output_path(config, sealing=True)
    value = {
        "schema": RECEIPT_SCHEMA,
        "completedAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "authorityTool": stamp(Path(__file__).resolve()),
        "manifest": stamp(config.manifest_path),
        "evidence": build(config),
        "liveGhidraOpenedByVerifier": False,
        "liveGhidraMutatedByVerifier": False,
        "trackedGhidraMutatedByVerifier": False,
    }
    atomic_new_json(config.output, value)
    print(f"LIVE_PROMOTION_AUTHORITY_READY receipt={config.output} sha256={sha256_file(config.output)}")


def verify(config: Config) -> None:
    validate_output_path(config, sealing=False)
    value = load_json(config.output, "aggregate receipt")
    require(value.get("schema") == RECEIPT_SCHEMA, "aggregate receipt schema differs")
    parse_utc(value.get("completedAtUtc"), "aggregate receipt completedAtUtc")
    require(value.get("authorityTool") == stamp(Path(__file__).resolve())
            and value.get("manifest") == stamp(config.manifest_path),
            "aggregate receipt tool/manifest identity differs")
    require(value.get("liveGhidraOpenedByVerifier") is False
            and value.get("liveGhidraMutatedByVerifier") is False
            and value.get("trackedGhidraMutatedByVerifier") is False,
            "aggregate receipt mutation boundary differs")
    require(value.get("evidence") == build(config), "aggregate evidence no longer reproduces")
    print(f"LIVE_PROMOTION_AUTHORITY_VERIFIED receipt_sha256={sha256_file(config.output)}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("seal", "verify"))
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--live-lane", required=True, type=Path)
    parser.add_argument("--pre-readback", required=True, type=Path)
    parser.add_argument("--scratch-receipt", required=True, type=Path)
    parser.add_argument("--live-project", required=True, type=Path)
    parser.add_argument("--pre-backup", required=True, type=Path)
    parser.add_argument("--post-backup", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = Config(*(
        clean_path(value) for value in
        (args.repo, args.manifest, args.live_lane, args.pre_readback,
         args.scratch_receipt, args.live_project, args.pre_backup,
         args.post_backup, args.output)
    ))
    if args.command == "seal":
        seal(config)
    else:
        verify(config)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AuthorityError, OSError, UnicodeError, name_projection.ProjectionError) as exc:
        print(f"AUTHORITY_REJECTED: {exc}", file=sys.stderr)
        raise SystemExit(1)
