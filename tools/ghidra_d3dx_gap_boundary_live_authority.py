#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Prepare, reproduce, and seal the db.18617 D3DX two-boundary promotion.

This authority never launches Ghidra and never mutates a project. ``preflight``
replays the complete disposable preparation and proves exact live/tracked PRE
state. ``check-live`` proves a separately run one-save live ceremony while the
tracked snapshot remains PRE. ``seal`` creates one new ignored aggregate receipt
after tracked refresh, restore probes, projection, and body accounting.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import ghidra_d3dx_gap_boundary_current_preparation_authority as prep  # noqa: E402
import ghidra_project_backup as project_backup  # noqa: E402
import re_ghidra_name_projection as name_projection  # noqa: E402


SCHEMA = "bea.ghidra.d3dx-gap-two-live-authority.v1"
POLICY = "PREPARATION_ONLY"
BASE_COMMIT = "028edae969f9ffb92e2f73ae394cbcf282b9fed8"
PROGRAM_NAME = "BEA.exe"
AGGREGATE_PRE_FUNCTIONS = 8_551
AGGREGATE_POST_FUNCTIONS = 8_553

LIVE_LANE_REL = (
    "local-lab/ghidra-d3dx-gap-two-boundary-live-promotion-db18617-20260814-v1"
)
AUTHORITY_RECEIPT_REL = (
    "local-lab/ghidra-d3dx-gap-two-boundary-live-authority-20260814-v1/"
    "live-promotion.ready.json"
)
PREPARATION_REL = "local-lab/d3dx-gap-two-boundary-current-preparation-20260814-v1"
PREPARATION_RECEIPT_REL = f"{PREPARATION_REL}/preparation-authority.ready.json"
SCRATCH_REL = "local-lab/d3dx-gap-two-boundary-scratch-20260814-v1"
PROJECTION_REL = (
    "reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-13.tsv"
)
POST_PROJECTION_SOURCE = "d3dx-gap-two-db18617-post"
PRE_ACCOUNTING_REL = (
    "local-lab/ghidra-crt-eh-parent-range-live-promotion-db18616-20260814-v1/"
    "tracked-post-accounting/body-ranges.tsv"
)
PRE_DIRECT_CALLS_REL = (
    "local-lab/ghidra-crt-eh-parent-range-live-promotion-db18616-20260814-v1/"
    "tracked-post-accounting/direct-calls.tsv"
)

PREPARATION_RECEIPT_STAMP = (
    18_831,
    "4c5c45dcd68c04a0679371a0e392e38331ebd945c115e3a59abc8a548cf34f00",
)
PREPARATION_TREE = {
    "files": 223,
    "bytes": 1_366_092_719,
    "sha256": "f8689877ded68fc8e0eb4804d2c2808370e371cc1346a52a9f040c326c98f664",
}
PRE_PROJECTION_STAMP = (
    510_431,
    "64c87111651ad37437be96ce3712abe6fafb762f0e545393c8dc65f8ac583669",
)
PRE_BODY_RANGES_STAMP = (
    1_205_601,
    "45e9521e8145c506842767604f10c04fdb0087ad199859207736e5e7d58bdbce",
)

PRE_OLD_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18616.gbf"
PRE_STABLE_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18617.gbf"
POST_ROLLING_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18618.gbf"
PRE_DB_STAMP = (68_354_048, prep.PRE_DB_SHA256)

# These physical identities were measured only after the one-save ceremony.
POST_PROJECT_SHA256 = (
    "c6cb2a228f110a8c7949d8f337a41fc4f060fb33b959bc11868e5cb315e1df7a"
)
POST_DB_SHA256 = (
    "189bc6c738dadcc1796228c6e8c4efbd66acad617098ac5dd19045ac57e50c78"
)

EXPECTED_REPO_INPUTS = {
    prep.MANIFEST_REL: prep.MANIFEST_STAMP,
    "tools/GhidraApplyD3dxGapBoundariesV2.java": prep.MUTATOR_STAMP,
    "tools/ExportFullFunctionInventory.java": (
        23_963,
        "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197",
    ),
    "tools/ExportParityLabGraph.java": (
        17_663,
        "e91e26c428f593e3fd49f755fcc8551dd685ce41825fe180966be49594cbbec9",
    ),
    "tools/DiagnoseAddressListingState.java": (
        3_956,
        "183394907659e7810c77a9720e1899fd8a6296e6e86673495d68a2764edefe69",
    ),
    "tools/ghidra_inventory_diff.py": (
        9_622,
        "b4956fbf9c9125cfdd7b7810cdc15f298fef8a081a880f82d6231a6dcbb25460",
    ),
    "tools/ghidra_project_backup.py": (
        27_502,
        "0f426982916f0aab982efe54664342a5d34607c2f89707159ecf6c07e205ad58",
    ),
    "tools/GhidraProjectOpenProbe.java": (
        3_452,
        "fab2f701dfefe8604c1718d007dbe0ad59d330a9b3ec081ef2f2fe253b441fab",
    ),
    "tools/re_ghidra_name_projection.py": (
        6_139,
        "d13d5f4d3b20cbd1e1baf24cd924d454c6c07b0bbf5517834c4089357f14ecdb",
    ),
    "tools/ghidra_d3dx_gap_boundary_current_preparation_authority.py": (
        58_010,
        "f6e932736298ecb070b1762f96e999b7b7d37d3b3c0320633e9b8b7ef7bc0406",
    ),
}

RUN_LAYOUT = {
    "dry": "live-pre-readback",
    "apply": "live-apply",
    "readback": "live-readback",
}
BOUNDARY_HASHES = {
    "dry": prep.DRY_BOUNDARIES_SHA256,
    "apply": prep.APPLY_BOUNDARIES_SHA256,
    "readback": prep.READBACK_BOUNDARIES_SHA256,
}
BOUNDARY_STATUS = {
    "dry": "ready_absent",
    "apply": "created",
    "readback": "verified",
}
CLAIMS = (
    "Exactly two DEFAULT-source functions were created at the reviewed entries.",
    "All 8,327 PRE function rows remain byte-identical and only two rows are new.",
    "The one writable headless process is bracketed by separate read-only exports.",
    "Live, tracked, POST backup, and retained POST restore projects are byte-identical.",
    "No semantic name, signature, comment, tag, grade, byte, data, or explicit reference was promoted.",
)


class AuthorityError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise AuthorityError(message)


def sha256_file(path: Path) -> str:
    return prep.sha256_file(path)


def clean_path(path: Path) -> Path:
    return Path(os.path.abspath(path))


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def require_disjoint(first: Path, second: Path, label: str) -> None:
    require(
        not is_within(first, second) and not is_within(second, first),
        f"{label} must be disjoint",
    )


def stamp(path: Path, role: str) -> dict[str, Any]:
    require(path.is_file(), f"missing {role}: {path}")
    return {
        "path": role.replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def verify_stamp(path: Path, expected: tuple[int, str], role: str) -> dict[str, Any]:
    value = stamp(path, role)
    require(
        (value["bytes"], value["sha256"]) == expected,
        f"{role} identity differs",
    )
    return value


def read_json(path: Path, role: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AuthorityError(f"invalid {role}: {path}") from exc
    require(isinstance(value, dict), f"{role} must be a JSON object")
    return value


def parse_utc(value: Any, role: str) -> datetime:
    require(isinstance(value, str) and value.endswith("Z"), f"{role} is not UTC")
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise AuthorityError(f"malformed {role}") from exc


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def mtime_utc(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)


def exact_comparison(value: Mapping[str, Any], role: str) -> None:
    require(
        value.get("matches") is True
        and all(
            value.get(key) == 0
            for key in ("missingCount", "extraCount", "sizeDiffCount", "hashDiffCount")
        )
        and all(
            value.get(key) == []
            for key in ("missing", "extra", "sizeDifferences", "hashDifferences")
        ),
        f"{role} does not report exact equality",
    )


def exact_directory_entries(
    root: Path,
    *,
    expected_files: Iterable[str],
    expected_directories: Iterable[str],
    label: str,
) -> None:
    require(root.is_dir(), f"missing {label}: {root}")
    files: set[str] = set()
    directories: set[str] = set()
    for entry in root.iterdir():
        require(not prep.is_reparse(entry), f"reparse point in {label}: {entry}")
        if entry.is_file():
            files.add(entry.name)
        elif entry.is_dir():
            directories.add(entry.name)
        else:
            raise AuthorityError(f"unsupported entry in {label}: {entry}")
    require(files == set(expected_files), f"{label} file set differs: {sorted(files)}")
    require(
        directories == set(expected_directories),
        f"{label} directory set differs: {sorted(directories)}",
    )


def ensure_portable(value: Any, label: str = "root") -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            ensure_portable(item, f"{label}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            ensure_portable(item, f"{label}[{index}]")
    elif isinstance(value, str):
        require(not re.match(r"^[A-Za-z]:[\\/]", value), f"absolute path in {label}")
        require("\\" not in value, f"backslash in portable receipt: {label}")


def project_value(root: Path) -> dict[str, Any]:
    files = prep.project_files(root)
    return {
        "projectName": "BEA",
        "fileCount": len(files),
        "totalBytes": sum(int(row["size"]) for row in files),
        "structurallyComplete": True,
        "files": files,
    }


def project_summary(value: Mapping[str, Any]) -> dict[str, Any]:
    return prep.project_summary(value)


def project_map(value: Mapping[str, Any]) -> dict[str, tuple[int, str]]:
    return prep.project_file_map(value)


def require_project(value: Mapping[str, Any], digest: str, role: str) -> None:
    require(value.get("projectName") == "BEA", f"{role} project name")
    require(value.get("fileCount") == 19, f"{role} file count")
    require(value.get("totalBytes") == 187_009_925, f"{role} byte count")
    require(value.get("structurallyComplete") is True, f"{role} completeness")
    require(prep.project_digest(value) == digest, f"{role} project digest")


def require_same_project(left: Mapping[str, Any], right: Mapping[str, Any], role: str) -> None:
    require(project_map(left) == project_map(right), f"{role} project bytes differ")


def require_recorded_path(value: Any, expected: Path, role: str) -> None:
    prep.require_recorded_path(value, expected, role)


def require_final_constants() -> None:
    require(POST_PROJECT_SHA256 != "0" * 64, "POST project identity is not frozen")
    require(POST_DB_SHA256 != "0" * 64, "POST rolling database identity is not frozen")


def validate_post_transition(
    before: Mapping[str, Any], after: Mapping[str, Any], role: str
) -> dict[str, Any]:
    require_project(before, prep.PRE_PROJECT_SHA256, f"{role} PRE")
    require_final_constants()
    require_project(after, POST_PROJECT_SHA256, f"{role} POST")
    old = project_map(before)
    new = project_map(after)
    removed = sorted(set(old) - set(new))
    added = sorted(set(new) - set(old))
    require(removed == [PRE_OLD_DB_PATH], f"{role} removed files")
    require(added == [POST_ROLLING_DB_PATH], f"{role} added files")
    changed = [path for path in sorted(set(old) & set(new)) if old[path] != new[path]]
    require(not changed, f"{role} common-file drift: {changed}")
    require(old[PRE_STABLE_DB_PATH] == PRE_DB_STAMP, f"{role} stable PRE db")
    require(
        new[POST_ROLLING_DB_PATH] == (68_354_048, POST_DB_SHA256),
        f"{role} POST rolling db",
    )
    return {"removed": removed, "added": added, "changed": changed}


@dataclass(frozen=True)
class Config:
    repo: Path
    evidence_repo: Path
    live_project: Path
    live_lane: Path
    pre_backup: Path
    post_backup: Path
    output: Path | None

    @property
    def tracked_project(self) -> Path:
        return self.repo / "reverse-engineering/ghidra"

    @property
    def preparation(self) -> Path:
        return self.evidence_repo / PREPARATION_REL

    @property
    def preparation_receipt(self) -> Path:
        return self.evidence_repo / PREPARATION_RECEIPT_REL

    @property
    def scratch(self) -> Path:
        return self.evidence_repo / SCRATCH_REL

    @property
    def projection(self) -> Path:
        return self.repo / PROJECTION_REL

    @property
    def pre_accounting(self) -> Path:
        return self.evidence_repo / PRE_ACCOUNTING_REL

    @property
    def pre_direct_calls(self) -> Path:
        return self.evidence_repo / PRE_DIRECT_CALLS_REL


def validate_layout(config: Config) -> None:
    require(config.repo.is_dir(), "repository root is missing")
    require(config.evidence_repo.is_dir(), "evidence repository root is missing")
    require(config.live_project.is_dir(), "live project root is missing")
    require(config.tracked_project.is_dir(), "tracked project root is missing")
    require(
        clean_path(config.live_lane) == clean_path(config.evidence_repo / LIVE_LANE_REL),
        "live lane is not the canonical evidence path",
    )
    roots = (
        config.live_project,
        config.tracked_project,
        config.live_lane,
        config.pre_backup,
        config.post_backup,
    )
    for index, left in enumerate(roots):
        for right in roots[index + 1 :]:
            require_disjoint(clean_path(left), clean_path(right), "project/evidence roots")


def validate_repo_inputs(config: Config) -> dict[str, Any]:
    return {
        relative: verify_stamp(config.repo / relative, expected, relative)
        for relative, expected in EXPECTED_REPO_INPUTS.items()
    }


def validate_preparation_historical(config: Config) -> dict[str, Any]:
    verify_stamp(
        config.preparation_receipt,
        PREPARATION_RECEIPT_STAMP,
        PREPARATION_RECEIPT_REL,
    )
    tree = prep.artifact_tree(config.preparation, config.preparation_receipt)
    require(tree == PREPARATION_TREE, "preparation artifact tree identity differs")
    recorded = read_json(config.preparation_receipt, "preparation receipt")
    require(recorded.get("schema") == prep.SCHEMA, "preparation schema")
    require(recorded.get("status") == "READY", "preparation status")
    require(recorded.get("policy") == "PREPARATION_ONLY", "preparation policy")
    require(recorded.get("mutationAuthorized") is False, "preparation mutation boundary")
    require(recorded.get("pre", {}).get("functions") == prep.PRE_FUNCTIONS, "preparation PRE")
    require(recorded.get("post", {}).get("functions") == prep.POST_FUNCTIONS, "preparation POST")
    prep.verify_topology(config.preparation, config.preparation_receipt)
    prep.verify_manifest(config.preparation, config.repo)
    prep.verify_tools(config.preparation, config.repo)
    prep.verify_positive_replicas(config.preparation)
    prep.verify_controls(config.preparation)
    scratch = prep.verify_scratch(config.preparation, config.scratch)
    return {
        "receipt": {
            "path": PREPARATION_RECEIPT_REL,
            "bytes": PREPARATION_RECEIPT_STAMP[0],
            "sha256": PREPARATION_RECEIPT_STAMP[1],
        },
        "tree": tree,
        "positiveReplicas": 2,
        "adverseControls": 4,
        "scratch": scratch,
    }


def prospective_projection(config: Config) -> dict[str, Any]:
    source = config.preparation / "runs/replica-a-readback/functions.tsv"
    verify_stamp(source, prep.POST_FUNCTIONS_STAMP, "prepared POST functions")
    raw = name_projection.projection_bytes(
        source,
        expected_inventory_sha256=prep.POST_FUNCTIONS_STAMP[1],
        source_label=POST_PROJECTION_SOURCE,
        projection_date="2026-08-14",
        specimen_sha256=prep.RETAIL_SHA256,
    )
    measured = (len(raw), hashlib.sha256(raw).hexdigest())
    require(measured == prep.PROJECTION_STAMP, "prospective projection identity")
    return {"bytes": measured[0], "sha256": measured[1], "rows": prep.POST_FUNCTIONS}


def prospective_accounting(config: Config) -> dict[str, Any]:
    before = verify_stamp(config.pre_accounting, PRE_BODY_RANGES_STAMP, "PRE body ranges")
    after_path = config.preparation / "runs/replica-a-readback/body-ranges.tsv"
    after = verify_stamp(after_path, prep.BODY_RANGES_STAMP, "prepared POST body ranges")
    prep.verify_ranges(after_path)
    calls = verify_stamp(
        config.preparation / "runs/replica-a-readback/direct-calls.tsv",
        prep.DIRECT_CALLS_STAMP,
        "prepared POST direct calls",
    )
    require(
        verify_stamp(config.pre_direct_calls, prep.DIRECT_CALLS_STAMP, "PRE direct calls")[
            "sha256"
        ]
        == calls["sha256"],
        "direct-call graph drift",
    )
    return {"pre": before, "post": after, "directCalls": calls}


def preflight(config: Config) -> dict[str, Any]:
    validate_layout(config)
    repo_inputs = validate_repo_inputs(config)
    require(not config.live_lane.exists(), "canonical live lane already exists")
    require(not config.pre_backup.exists(), "PRE backup destination already exists")
    require(not config.post_backup.exists(), "POST backup destination already exists")
    require(
        not (config.repo / Path(AUTHORITY_RECEIPT_REL).parent).exists(),
        "canonical authority root already exists",
    )
    require(
        not (config.evidence_repo / Path(AUTHORITY_RECEIPT_REL).parent).exists(),
        "evidence-repository authority root already exists",
    )
    recorded = prep.verify(
        config.preparation,
        config.preparation_receipt,
        config.repo,
        config.live_project,
        config.scratch,
    )
    verify_stamp(config.projection, PRE_PROJECTION_STAMP, PROJECTION_REL)
    return {
        "baseCommit": BASE_COMMIT,
        "policy": POLICY,
        "repositoryInputs": repo_inputs,
        "preparationVerdict": recorded["verdict"],
        "livePre": recorded["pre"]["project"],
        "prospectiveProjection": prospective_projection(config),
        "prospectiveAccounting": prospective_accounting(config),
        "futureMutationAuthorized": False,
        "verdict": "PREPARATION_READY_MUTATION_NOT_AUTHORIZED",
        "blocker": "FUTURE_CEREMONY_ARTIFACTS_DO_NOT_EXIST",
    }


def inspect_receipt(
    path: Path, expected_root: Path, digest: str, role: str
) -> tuple[dict[str, Any], datetime]:
    value = read_json(path, role)
    require(value.get("schemaVersion") == project_backup.SCHEMA_VERSION, f"{role} schema")
    created = parse_utc(value.get("createdAtUtc"), f"{role} createdAtUtc")
    manifest = value.get("manifest")
    require(isinstance(manifest, dict), f"{role} manifest")
    require_recorded_path(manifest.get("root"), expected_root, role)
    require_project(manifest, digest, role)
    return dict(manifest), created


def validate_backup_manifest(
    path: Path,
    source_root: Path,
    destination_root: Path,
    expected: Mapping[str, Any],
    digest: str,
    role: str,
) -> tuple[dict[str, Any], datetime]:
    require(
        clean_path(path) == clean_path(destination_root / "backup_manifest.json"),
        f"{role} manifest location",
    )
    require_disjoint(clean_path(source_root), clean_path(destination_root), f"{role} roots")
    value = read_json(path, role)
    require(value.get("schemaVersion") == project_backup.SCHEMA_VERSION, f"{role} schema")
    created = parse_utc(value.get("createdAtUtc"), f"{role} createdAtUtc")
    require(value.get("sourceStable") is True, f"{role} source stability")
    exact_comparison(value.get("copyComparison", {}), f"{role} copy comparison")
    source = value.get("source")
    destination = value.get("destination")
    require(isinstance(source, dict) and isinstance(destination, dict), f"{role} projects")
    require("root" not in source and "root" not in destination, f"{role} unexpected roots")
    require_project(source, digest, f"{role} source")
    require_project(destination, digest, f"{role} destination")
    require_same_project(source, expected, f"{role} source/expected")
    require_same_project(destination, expected, f"{role} destination/expected")
    actual = project_value(destination_root)
    require_project(actual, digest, f"{role} actual destination")
    require_same_project(actual, destination, f"{role} receipt/actual")
    return dict(destination), created


def validate_restore(
    receipt: Path,
    source_root: Path,
    probe_root: Path,
    script_root: Path,
    expected: Mapping[str, Any],
    digest: str,
    expected_functions: int,
    role: str,
) -> tuple[dict[str, Any], datetime]:
    value = read_json(receipt, role)
    require(value.get("schemaVersion") == project_backup.SCHEMA_VERSION, f"{role} schema")
    verified = parse_utc(value.get("verifiedAtUtc"), f"{role} verifiedAtUtc")
    require(value.get("sourceStable") is True, f"{role} source stability")
    exact_comparison(value.get("copyComparison", {}), f"{role} copy")
    source = value.get("source")
    require(isinstance(source, dict), f"{role} source")
    require_recorded_path(source.get("root"), source_root, f"{role} source")
    require_project(source, digest, f"{role} source")
    require_same_project(source, expected, f"{role} source/expected")
    probe = Path(str(value.get("probeCopy", "")))
    require(probe.parent == probe_root and probe.name.startswith("BEA-open-probe-"), f"{role} probe path")
    require(value.get("probeCopyDisposition") == "RETAINED_AT_VERIFICATION", f"{role} probe disposition")
    actual_probe = project_value(probe)
    require_project(actual_probe, digest, f"{role} probe")
    require_same_project(actual_probe, expected, f"{role} probe/expected")
    opened = value.get("readonlyOpen")
    require(isinstance(opened, dict), f"{role} open result")
    require(opened.get("opened") is True and opened.get("exitCode") == 0, f"{role} open")
    require(opened.get("contentStable") is True, f"{role} open stability")
    exact_comparison(opened.get("postOpenComparison", {}), f"{role} post-open")
    require(opened.get("observedProgramName") == PROGRAM_NAME, f"{role} program")
    require(opened.get("observedProgramMd5") == prep.RETAIL_MD5, f"{role} MD5")
    require(opened.get("observedProgramSha256") == prep.RETAIL_SHA256, f"{role} SHA-256")
    require(opened.get("observedFunctionCount") == expected_functions, f"{role} function count")
    argv = opened.get("commandArgv")
    require(isinstance(argv, list) and len(argv) == 14, f"{role} argv")
    require(Path(str(argv[0])).name.lower() == "analyzeheadless.bat", f"{role} executable")
    require_recorded_path(argv[1], probe, f"{role} argv project")
    require(
        argv[2:8] == ["BEA", "-process", "BEA.exe", "-readOnly", "-noanalysis", "-scriptPath"],
        f"{role} argv operation",
    )
    require_recorded_path(argv[8], clean_path(script_root), f"{role} script root")
    require(argv[-4:] == ["GhidraProjectOpenProbe.java", "BEA.exe", prep.RETAIL_MD5, prep.RETAIL_SHA256], f"{role} argv tail")
    require("-commit" not in argv, f"{role} permits commit")
    log_claim = opened.get("probeLog")
    require(isinstance(log_claim, dict), f"{role} log claim")
    log = receipt.with_name(str(log_claim.get("path", "")))
    measured = stamp(log, f"{role}.open-probe.log")
    require((measured["bytes"], measured["sha256"]) == (log_claim.get("bytes"), log_claim.get("sha256")), f"{role} log identity")
    text = log.read_text(encoding="utf-8", errors="strict")
    require(text.count("GHIDRA_PROJECT_OPEN_PROBE_OK") == 1, f"{role} sentinel")
    require("REPORT SCRIPT ERROR:" not in text, f"{role} script error")
    return dict(source), verified


def validate_function_delta(pre_path: Path, post_path: Path) -> dict[str, Any]:
    verify_stamp(pre_path, prep.PRE_FUNCTIONS_STAMP, "live PRE functions")
    verify_stamp(post_path, prep.POST_FUNCTIONS_STAMP, "live POST functions")
    pre_fields, before = prep.rows_by_address(pre_path)
    post_fields, after = prep.rows_by_address(post_path)
    require(pre_fields == post_fields, "function inventory headers differ")
    require(len(before) == prep.PRE_FUNCTIONS and len(after) == prep.POST_FUNCTIONS, "function counts")
    require(set(before) <= set(after), "PRE functions are not preserved")
    changed = [address for address in before if before[address] != after[address]]
    require(not changed, f"PRE function rows changed: {changed[:5]}")
    created = sorted(set(after) - set(before))
    require(created == sorted(prep.TARGETS), f"created function set differs: {created}")
    for address in created:
        row = after[address]
        target = prep.TARGETS[address]
        require(row["name"] == target["name"], f"{address} name")
        require(
            row["nameSource"] == row["sigSource"] == "DEFAULT",
            f"{address} source",
        )
        require(row["bodyBytes"] == target["bytes"], f"{address} body bytes")
        require(row["bodyRanges"] == "1", f"{address} body range count")
        require(row["bodyDigest"] == target["rangeSha256"], f"{address} range digest")
        require(row["instrCount"] == target["instructions"], f"{address} instructions")
    return {"pre": stamp(pre_path, "functions.pre"), "post": stamp(post_path, "functions.post"), "unchangedPreRowsExact": len(before), "created": created}


def validate_program_delta(pre_path: Path, post_path: Path) -> dict[str, Any]:
    verify_stamp(pre_path, prep.PRE_PROGRAM_STAMP, "live PRE program")
    verify_stamp(post_path, prep.POST_PROGRAM_STAMP, "live POST program")
    before = prep.metrics(pre_path)
    after = prep.metrics(post_path)
    require(set(before) == set(after), "program metric set differs")
    changed = [key for key in before if before[key] != after[key]]
    require(changed == ["functions"], f"program collateral differs: {changed}")
    require(before["functions"] == "8327" and after["functions"] == "8329", "program function count")
    return {"pre": stamp(pre_path, "program.pre"), "post": stamp(post_path, "program.post"), "changedMetrics": changed}


def validate_inventory_diff(path: Path) -> dict[str, Any]:
    value = read_json(path, "inventory diff")
    counts = value.get("counts", {})
    require(counts.get("before") == prep.PRE_FUNCTIONS, "diff PRE count")
    require(counts.get("after") == prep.POST_FUNCTIONS, "diff POST count")
    require(counts.get("created") == 2 and counts.get("destroyed") == 0, "diff creation count")
    created = sorted(str(row.get("address", "")).lower() for row in value.get("created", []))
    require(created == sorted(prep.TARGETS), f"diff created set: {created}")
    require(value.get("destroyed") == [], "diff destroyed functions")
    dangerous = value.get("dangerous", {})
    require(dangerous and all(item in (0, []) for item in dangerous.values()), "dangerous function collateral")
    for key, rows in value.get("changesByField", {}).items():
        require(rows == [], f"existing function field changed: {key}")
    return {"stamp": stamp(path, "inventory-diff.json"), "created": created, "dangerous": 0}


def validate_run(
    config: Config, mode: str, run_name: str
) -> tuple[dict[str, Any], datetime]:
    root = config.live_lane / f"runs/{run_name}"
    names = {"boundaries.tsv", "boundaries.ready.json", "ghidra.log"}
    if mode in {"dry", "readback"}:
        names |= {"functions.tsv", "program.tsv"}
    if mode == "readback":
        names |= {"inventory-diff.json", "listing.tsv"}
    exact_directory_entries(root, expected_files=names, expected_directories=(), label=f"run {run_name}")
    output = root / "boundaries.tsv"
    ready = root / "boundaries.ready.json"
    verify_stamp(output, (output.stat().st_size, BOUNDARY_HASHES[mode]), f"{mode} boundaries")
    fields, rows = prep.read_tsv(output)
    require(fields == prep.BOUNDARY_FIELDS, f"{mode} boundary schema")
    prep.validate_boundary_rows(rows, BOUNDARY_STATUS[mode])
    value = read_json(ready, f"{mode} receipt")
    expected_path = f"{LIVE_LANE_REL}/runs/{run_name}/boundaries.tsv"
    prep.validate_receipt(value, mode, expected_path)
    require(value["output"]["bytes"] == output.stat().st_size, f"{mode} output bytes")
    require(value["output"]["sha256"] == sha256_file(output), f"{mode} output hash")
    completed = parse_utc(value.get("completedAtUtc"), f"{mode} completedAtUtc")
    log = root / "ghidra.log"
    text = log.read_text(encoding="utf-8", errors="strict")
    require(text.count("Execute script: GhidraApplyD3dxGapBoundariesV2.java") == 1, f"{mode} mutator count")
    expected_sentinel = {
        "dry": "D3DX_GAP_BOUNDARIES_OK mode=dry targets=2 functions=8327",
        "apply": "D3DX_GAP_BOUNDARIES_OK mode=apply targets=2 functions_before=8327 functions_after=8329",
        "readback": "D3DX_GAP_BOUNDARIES_OK mode=readback targets=2 functions=8329",
    }[mode]
    require(text.count(expected_sentinel) == 1, f"{mode} sentinel")
    require("REPORT SCRIPT ERROR:" not in text and "MUTATION_TAINTED" not in text, f"{mode} error marker")
    read_only_count = text.count("Processing read-only project file: /BEA.exe")
    save_count = text.count("Save succeeded for processed file: /BEA.exe")
    require(read_only_count == (0 if mode == "apply" else 1), f"{mode} read disposition")
    require(save_count == (1 if mode == "apply" else 0), f"{mode} save count")
    artifacts = {
        name: stamp(root / name, f"runs/{run_name}/{name}") for name in sorted(names)
    }
    return artifacts, max(completed, *(mtime_utc(root / name) for name in names))


def validate_runs(config: Config) -> tuple[dict[str, Any], dict[str, datetime]]:
    root = config.live_lane / "runs"
    exact_directory_entries(root, expected_files=(), expected_directories=RUN_LAYOUT.values(), label="live runs root")
    result: dict[str, Any] = {}
    times: dict[str, datetime] = {}
    for mode, run_name in RUN_LAYOUT.items():
        result[mode], times[f"live.{mode}.complete"] = validate_run(config, mode, run_name)
    functions = validate_function_delta(
        root / "live-pre-readback/functions.tsv", root / "live-readback/functions.tsv"
    )
    program = validate_program_delta(
        root / "live-pre-readback/program.tsv", root / "live-readback/program.tsv"
    )
    inventory = validate_inventory_diff(root / "live-readback/inventory-diff.json")
    prep.verify_listing(root / "live-readback/listing.tsv")
    logs = {str(path.relative_to(root)).replace("\\", "/") for path in root.rglob("ghidra.log")}
    require(logs == {f"{name}/ghidra.log" for name in RUN_LAYOUT.values()}, "live Ghidra log census")
    return {"artifacts": result, "functions": functions, "program": program, "inventoryDiff": inventory, "writableSaveLogs": 1}, times


def validate_projects(
    config: Config, *, require_tracked_post: bool
) -> tuple[dict[str, Any], dict[str, datetime]]:
    require_final_constants()
    live_pre, live_pre_time = inspect_receipt(
        config.live_lane / "live-pre-inspect.json",
        config.live_project,
        prep.PRE_PROJECT_SHA256,
        "live PRE inspect",
    )
    tracked_pre, tracked_pre_time = inspect_receipt(
        config.live_lane / "tracked-pre-inspect.json",
        config.repo / "reverse-engineering/ghidra",
        prep.PRE_PROJECT_SHA256,
        "tracked PRE inspect",
    )
    require_same_project(live_pre, tracked_pre, "live/tracked PRE")
    pre_backup, pre_backup_time = validate_backup_manifest(
        config.pre_backup / "backup_manifest.json",
        config.live_project,
        config.pre_backup,
        live_pre,
        prep.PRE_PROJECT_SHA256,
        "PRE backup",
    )
    _, pre_restore_time = validate_restore(
        config.live_lane / "pre-backup-restore.ready.json",
        config.pre_backup,
        config.live_lane / "pre-backup-restore-probe",
        config.repo / "tools",
        pre_backup,
        prep.PRE_PROJECT_SHA256,
        AGGREGATE_PRE_FUNCTIONS,
        "PRE restore",
    )
    before_apply, before_apply_time = inspect_receipt(
        config.live_lane / "live-before-apply-inspect.json",
        config.live_project,
        prep.PRE_PROJECT_SHA256,
        "live before apply",
    )
    require_same_project(before_apply, live_pre, "live PRE stability")
    live_post, live_post_time = inspect_receipt(
        config.live_lane / "live-post-inspect.json",
        config.live_project,
        POST_PROJECT_SHA256,
        "live POST inspect",
    )
    actual_live = project_value(config.live_project)
    require_project(actual_live, POST_PROJECT_SHA256, "actual live POST")
    require_same_project(actual_live, live_post, "actual/inspected live POST")
    transition = validate_post_transition(live_pre, live_post, "live")
    post_backup, post_backup_time = validate_backup_manifest(
        config.post_backup / "backup_manifest.json",
        config.live_project,
        config.post_backup,
        live_post,
        POST_PROJECT_SHA256,
        "POST backup",
    )
    _, post_restore_time = validate_restore(
        config.live_lane / "post-backup-restore.ready.json",
        config.post_backup,
        config.live_lane / "post-backup-restore-probe",
        config.repo / "tools",
        post_backup,
        POST_PROJECT_SHA256,
        AGGREGATE_POST_FUNCTIONS,
        "POST restore",
    )
    tracked_still_pre, tracked_still_pre_time = inspect_receipt(
        config.live_lane / "tracked-still-pre-inspect.json",
        config.repo / "reverse-engineering/ghidra",
        prep.PRE_PROJECT_SHA256,
        "tracked still PRE",
    )
    require_same_project(tracked_still_pre, tracked_pre, "tracked PRE persistence")
    result: dict[str, Any] = {
        "pre": project_summary(live_pre),
        "post": project_summary(live_post),
        "transition": transition,
        "preBackup": project_summary(pre_backup),
        "postBackup": project_summary(post_backup),
        "trackedStillPre": True,
    }
    times = {
        "live.pre.inspect": live_pre_time,
        "tracked.pre.inspect": tracked_pre_time,
        "pre.backup.created": pre_backup_time,
        "pre.restore.verified": pre_restore_time,
        "live.beforeApply.inspect": before_apply_time,
        "live.post.inspect": live_post_time,
        "post.backup.created": post_backup_time,
        "post.restore.verified": post_restore_time,
        "tracked.stillPre.inspect": tracked_still_pre_time,
    }
    if require_tracked_post:
        tracked_post, tracked_post_time = inspect_receipt(
            config.live_lane / "tracked-post-inspect.json",
            config.tracked_project,
            POST_PROJECT_SHA256,
            "tracked POST inspect",
        )
        actual_tracked = project_value(config.tracked_project)
        require_project(actual_tracked, POST_PROJECT_SHA256, "actual tracked POST")
        require_same_project(tracked_post, actual_tracked, "tracked inspect/actual POST")
        require_same_project(tracked_post, live_post, "tracked/live POST")
        _, tracked_restore_time = validate_restore(
            config.live_lane / "tracked-post-restore.ready.json",
            config.tracked_project,
            config.live_lane / "tracked-post-restore-probe",
            config.repo / "tools",
            tracked_post,
            POST_PROJECT_SHA256,
            AGGREGATE_POST_FUNCTIONS,
            "tracked POST restore",
        )
        result["trackedPost"] = project_summary(tracked_post)
        result["trackedRestore"] = "PASS"
        times["tracked.post.inspect"] = tracked_post_time
        times["tracked.restore.verified"] = tracked_restore_time
    return result, times


def validate_projection(config: Config) -> tuple[dict[str, Any], datetime]:
    source = config.live_lane / "runs/live-readback/functions.tsv"
    raw = name_projection.projection_bytes(
        source,
        expected_inventory_sha256=prep.POST_FUNCTIONS_STAMP[1],
        source_label=POST_PROJECTION_SOURCE,
        projection_date="2026-08-14",
        specimen_sha256=prep.RETAIL_SHA256,
    )
    require((len(raw), hashlib.sha256(raw).hexdigest()) == prep.PROJECTION_STAMP, "projection stamp")
    retained = config.live_lane / "ghidra-function-name-table-2026-08-13.tsv"
    require(config.projection.read_bytes() == raw, "tracked projection differs")
    require(retained.read_bytes() == raw, "retained projection differs")
    return {"path": PROJECTION_REL, "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(), "rows": prep.POST_FUNCTIONS}, max(mtime_utc(config.projection), mtime_utc(retained))


def validate_accounting(config: Config) -> tuple[dict[str, Any], datetime]:
    root = config.live_lane / "tracked-post-accounting"
    exact_directory_entries(
        root,
        expected_files=("body-ranges.tsv", "direct-calls.tsv", "parity-graph.ready.json", "ghidra.log"),
        expected_directories=(),
        label="tracked POST accounting",
    )
    body = verify_stamp(root / "body-ranges.tsv", prep.BODY_RANGES_STAMP, "POST body ranges")
    calls = verify_stamp(root / "direct-calls.tsv", prep.DIRECT_CALLS_STAMP, "POST direct calls")
    prep.verify_ranges(root / "body-ranges.tsv")
    value = read_json(root / "parity-graph.ready.json", "POST parity receipt")
    require(value.get("schemaVersion") == "bea-ghidra-parity-graph-receipt.v2", "parity schema")
    require(value.get("bodyRanges", {}).get("functionCount") == prep.POST_FUNCTIONS, "parity function count")
    require(value.get("bodyRanges", {}).get("rangeCount") == prep.POST_RANGES, "parity range count")
    require((value["bodyRanges"].get("bytes"), value["bodyRanges"].get("sha256")) == prep.BODY_RANGES_STAMP, "parity body binding")
    require((value["directCalls"].get("bytes"), value["directCalls"].get("sha256")) == prep.DIRECT_CALLS_STAMP, "parity call binding")
    text = (root / "ghidra.log").read_text(encoding="utf-8", errors="strict")
    require(text.count(f"PARITY_GRAPH_OK functions={prep.POST_FUNCTIONS} ranges={prep.POST_RANGES}") == 1, "parity sentinel")
    require("Processing read-only project file: /BEA.exe" in text, "parity read-only open")
    require("Save succeeded" not in text and "REPORT SCRIPT ERROR:" not in text, "parity unsafe log")
    completed = max(mtime_utc(path) for path in root.iterdir())
    return {"functions": prep.POST_FUNCTIONS, "ranges": prep.POST_RANGES, "ownedBytes": prep.POST_OWNED, "ownershipPercent": 100.0 * prep.POST_OWNED / prep.TEXT_BYTES, "bodyRanges": body, "directCalls": calls}, completed


def validate_chronology(
    projects: Mapping[str, datetime], runs: Mapping[str, datetime],
    projection_time: datetime | None = None, accounting_time: datetime | None = None,
) -> list[dict[str, str]]:
    events = dict(projects)
    events.update(runs)
    edges = [
        ("live.pre.inspect", "pre.backup.created"),
        ("tracked.pre.inspect", "pre.backup.created"),
        ("pre.backup.created", "pre.restore.verified"),
        ("pre.restore.verified", "live.dry.complete"),
        ("live.dry.complete", "live.beforeApply.inspect"),
        ("live.beforeApply.inspect", "live.apply.complete"),
        ("live.apply.complete", "live.readback.complete"),
        ("live.readback.complete", "live.post.inspect"),
        ("live.post.inspect", "post.backup.created"),
        ("post.backup.created", "post.restore.verified"),
        ("post.restore.verified", "tracked.stillPre.inspect"),
    ]
    if projection_time is not None and accounting_time is not None:
        events["projection.complete"] = projection_time
        events["accounting.complete"] = accounting_time
        edges += [
            ("tracked.stillPre.inspect", "tracked.post.inspect"),
            ("tracked.post.inspect", "tracked.restore.verified"),
            ("tracked.restore.verified", "projection.complete"),
            ("tracked.restore.verified", "accounting.complete"),
        ]
    for left, right in edges:
        require(events[left] < events[right], f"chronology differs: {left} !< {right}")
    return [
        {"event": key, "atUtc": utc_text(events[key])}
        for key in sorted(events, key=lambda item: (events[item], item))
    ]


def validate_topology(config: Config, *, final: bool) -> dict[str, Any]:
    files = {
        "live-pre-inspect.json", "tracked-pre-inspect.json",
        "pre-backup-restore.ready.json", "pre-backup-restore.ready.open-probe.log",
        "live-before-apply-inspect.json", "live-post-inspect.json",
        "post-backup-restore.ready.json", "post-backup-restore.ready.open-probe.log",
        "tracked-still-pre-inspect.json",
    }
    directories = {"static", "runs", "pre-backup-restore-probe", "post-backup-restore-probe"}
    if final:
        files |= {
            "tracked-post-inspect.json", "tracked-post-restore.ready.json",
            "tracked-post-restore.ready.open-probe.log",
            "ghidra-function-name-table-2026-08-13.tsv",
        }
        directories |= {"tracked-post-restore-probe", "tracked-post-accounting"}
    exact_directory_entries(config.live_lane, expected_files=files, expected_directories=directories, label="live evidence root")
    exact_directory_entries(config.live_lane / "static", expected_files=("addresses.txt", "manifest.tsv"), expected_directories=(), label="live static root")
    verify_stamp(config.live_lane / "static/manifest.tsv", prep.MANIFEST_STAMP, "live manifest copy")
    addresses = (config.live_lane / "static/addresses.txt").read_text(encoding="utf-8").splitlines()
    require(addresses == ["0x00595fc9", "0x00596027", "0x00596028", "0x005960c0"], "diagnostic address set")
    ledger: dict[str, Any] = {}
    for path in sorted(config.live_lane.rglob("*")):
        require(not prep.is_reparse(path), f"reparse point in live evidence: {path}")
        if path.is_file() and "BEA-open-probe-" not in path.as_posix():
            relative = path.relative_to(config.live_lane).as_posix()
            ledger[relative] = stamp(path, f"live-lane/{relative}")
    return ledger


def build_live_phase(config: Config) -> dict[str, Any]:
    validate_layout(config)
    repo_inputs = validate_repo_inputs(config)
    historical = validate_preparation_historical(config)
    projects, project_times = validate_projects(config, require_tracked_post=False)
    runs, run_times = validate_runs(config)
    chronology = validate_chronology(project_times, run_times)
    value = {
        "baseCommit": BASE_COMMIT,
        "policy": POLICY,
        "artifactLedger": {"repository": repo_inputs, "liveLane": validate_topology(config, final=False)},
        "preparationAuthority": historical,
        "projectsAndRecovery": projects,
        "liveRun": runs,
        "chronology": chronology,
        "trackedGhidraMutationPerformed": False,
        "futureMutationAuthorized": False,
        "verdict": "LIVE_PHASE_REPRODUCED_TRACKED_STILL_PRE",
    }
    ensure_portable(value)
    return value


def build_final(config: Config) -> dict[str, Any]:
    validate_layout(config)
    repo_inputs = validate_repo_inputs(config)
    historical = validate_preparation_historical(config)
    projects, project_times = validate_projects(config, require_tracked_post=True)
    runs, run_times = validate_runs(config)
    projection, projection_time = validate_projection(config)
    accounting, accounting_time = validate_accounting(config)
    chronology = validate_chronology(project_times, run_times, projection_time, accounting_time)
    value = {
        "baseCommit": BASE_COMMIT,
        "policy": POLICY,
        "artifactLedger": {"repository": repo_inputs, "liveLane": validate_topology(config, final=True)},
        "preparationAuthority": historical,
        "projectsAndRecovery": projects,
        "liveRun": runs,
        "projection": projection,
        "bodyAccounting": accounting,
        "chronology": chronology,
        "claims": list(CLAIMS),
        "verdict": "LIVE_PROMOTION_REPRODUCED",
    }
    ensure_portable(value)
    return value


def validate_output(config: Config, *, sealing: bool) -> None:
    require(config.output is not None, "aggregate output is required")
    expected = clean_path(config.repo / AUTHORITY_RECEIPT_REL)
    require(clean_path(config.output) == expected, "aggregate receipt path differs")
    for root in (
        config.live_lane, config.preparation, config.scratch, config.live_project,
        config.pre_backup, config.post_backup, config.tracked_project,
    ):
        require(not is_within(expected, clean_path(root)), "aggregate receipt overlaps evidence/project root")
    if not sealing:
        require(expected.is_file(), "saved aggregate receipt is absent")
        return
    require(not expected.exists(), "refusing to overwrite aggregate receipt")
    require(is_within(expected, clean_path(config.repo / "local-lab")), "aggregate receipt is not local evidence")
    ignored = subprocess.run(
        ["git", "-C", str(config.repo), "check-ignore", "-q", "--", str(expected)],
        check=False, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
    )
    require(ignored.returncode == 0, "aggregate receipt path is not Git-ignored")


def atomic_new_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(not path.exists(), f"refusing to overwrite receipt: {path}")
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".partial", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def seal(config: Config) -> None:
    validate_output(config, sealing=True)
    value = {
        "schemaVersion": SCHEMA,
        "completedAtUtc": utc_text(datetime.now(timezone.utc)),
        "authorityTool": stamp(Path(__file__).resolve(), "tools/ghidra_d3dx_gap_boundary_live_authority.py"),
        "evidence": build_final(config),
        "policy": POLICY,
        "ghidraOpenedByAuthority": False,
        "liveGhidraMutatedByAuthority": False,
        "trackedGhidraMutatedByAuthority": False,
        "futureMutationAuthorized": False,
    }
    ensure_portable(value)
    assert config.output is not None
    atomic_new_json(config.output, value)
    print(f"D3DX_GAP_TWO_LIVE_AUTHORITY_READY receipt_sha256={sha256_file(config.output)} functions={prep.POST_FUNCTIONS} ranges={prep.POST_RANGES} gain=248")


def verify(config: Config) -> None:
    validate_output(config, sealing=False)
    assert config.output is not None
    recorded = read_json(config.output, "aggregate authority receipt")
    require(recorded.get("schemaVersion") == SCHEMA, "aggregate schema")
    parse_utc(recorded.get("completedAtUtc"), "aggregate completedAtUtc")
    require(recorded.get("authorityTool") == stamp(Path(__file__).resolve(), "tools/ghidra_d3dx_gap_boundary_live_authority.py"), "aggregate authority binding")
    require(recorded.get("policy") == POLICY, "aggregate policy")
    require(recorded.get("ghidraOpenedByAuthority") is False and recorded.get("liveGhidraMutatedByAuthority") is False and recorded.get("trackedGhidraMutatedByAuthority") is False and recorded.get("futureMutationAuthorized") is False, "aggregate mutation boundary")
    require(recorded.get("evidence") == build_final(config), "aggregate evidence differs")
    ensure_portable(recorded)
    print(f"D3DX_GAP_TWO_LIVE_AUTHORITY_VERIFIED receipt_sha256={sha256_file(config.output)} functions={prep.POST_FUNCTIONS} ranges={prep.POST_RANGES} gain=248")


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("preflight", "check-live", "seal", "verify"))
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--evidence-repo", type=Path, required=True)
    parser.add_argument("--live-project", type=Path, required=True)
    parser.add_argument("--live-lane", type=Path, required=True)
    parser.add_argument("--pre-backup", type=Path, required=True)
    parser.add_argument("--post-backup", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)
    config = Config(
        *(clean_path(value) for value in (
            args.repo, args.evidence_repo, args.live_project, args.live_lane,
            args.pre_backup, args.post_backup,
        )),
        clean_path(args.output) if args.output is not None else None,
    )
    if args.command == "preflight":
        require(config.output is None, "preflight does not accept --output")
        result = preflight(config)
        print(
            "D3DX_GAP_TWO_LIVE_PREPARATION_READY "
            f"pre_project_sha256={result['livePre']['canonicalInventorySha256']} "
            f"preparation_receipt_sha256={PREPARATION_RECEIPT_STAMP[1]} "
            "live_equals_tracked=true db=db.18617.gbf policy=PREPARATION_ONLY "
            "mutation_authorized=false blocker=future_ceremony_artifacts_absent"
        )
    elif args.command == "check-live":
        require(config.output is None, "check-live does not accept --output")
        result = build_live_phase(config)
        print(
            "D3DX_GAP_TWO_LIVE_PHASE_VERIFIED "
            f"post_functions={prep.POST_FUNCTIONS} post_ranges={prep.POST_RANGES} "
            f"verdict={result['verdict']} tracked_mutation_authorized=false"
        )
    elif args.command == "seal":
        seal(config)
    else:
        verify(config)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        AuthorityError,
        prep.AuthorityError,
        project_backup.BackupError,
        name_projection.ProjectionError,
        OSError,
        UnicodeError,
        subprocess.SubprocessError,
    ) as exc:
        print(f"D3DX_GAP_TWO_LIVE_AUTHORITY_REFUSED reason={exc}", file=sys.stderr)
        raise SystemExit(1)
