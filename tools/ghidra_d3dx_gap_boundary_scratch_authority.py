#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Seal or verify the two-function D3DX boundary scratch campaign.

This authority is read-only except when ``seal`` creates one new aggregate
receipt.  It never opens Ghidra and never authorizes a live or tracked project
write.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Iterable

sys.dont_write_bytecode = True


class AuthorityError(ValueError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise AuthorityError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stamp(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    require(path.is_file(), f"missing artifact: {relative}")
    return {
        "path": relative.replace("\\", "/"),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def require_stamp(
    root: Path,
    relative: str,
    *,
    size: int | None = None,
    sha256: str | None = None,
) -> dict[str, Any]:
    actual = stamp(root, relative)
    if size is not None:
        require(actual["bytes"] == size, f"byte drift: {relative}")
    if sha256 is not None:
        require(actual["sha256"] == sha256, f"hash drift: {relative}")
    return actual


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream, delimiter="\t")
        require(reader.fieldnames is not None, f"missing TSV header: {path}")
        return list(reader.fieldnames), list(reader)


def metrics(path: Path) -> dict[str, str]:
    fields, rows = read_tsv(path)
    require(fields == ["metric", "value"], f"metric schema drift: {path}")
    result: dict[str, str] = {}
    for row in rows:
        require(row["metric"] not in result, f"duplicate metric: {row['metric']}")
        result[row["metric"]] = row["value"]
    return result


RETAIL_MD5 = "3b456964020070efe696d2cc09464a55"
RETAIL_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
DB_SHA256 = "615497847b0c732077ee7164b0973b9012092523e9ad99b91c21781952420ebe"
MANIFEST_SHA256 = "2d8f16415206538d0377fafe70c210bf8de65b442e2162ad5f5909d01c21fefd"
MUTATOR_SHA256 = "8767c361207de1718c3d3742fa43f76e9d897772ecd6a8123116299277a3f710"
PRE_FUNCTIONS_SHA256 = "c3942b9e340cef71b731290b845843697af5c53204449c51949b779e896272d6"
PRE_PROGRAM_SHA256 = "3e51ce1d5e926c632869b2058c9d89e91f48345a329a724ea9520570bd91212d"
POST_FUNCTIONS_SHA256 = "1a269f886c7cc7c11c854aa1219b81384102a530550277e88b83e9b3c043916d"
POST_PROGRAM_SHA256 = "9d224178c0a4b85418364b47be996d48f83c970e399ab5fc28383858d1f0ff2a"
DRY_BOUNDARIES_SHA256 = "ebafb3f84a3e0f1dc631f6929200693ff499d195b518e96d0a4342e291f9dc28"
APPLY_BOUNDARIES_SHA256 = "b3651e2f11334a5e0dd0305b205b061a6803d4254068c3cb14891472c81ae2be"
READBACK_BOUNDARIES_SHA256 = "b6e75cef06e9425687ee600bff6bdff31dae0120d2351dcaedbe29949a01fd88"

BOUNDARY_FIELDS = [
    "candidateId",
    "cohort",
    "entry",
    "status",
    "name",
    "nameSource",
    "expectedRanges",
    "actualRanges",
    "expectedBodyBytes",
    "actualBodyBytes",
    "expectedRangeSha256",
    "actualRangeSha256",
    "expectedBodyBytesSha256",
    "actualBodyBytesSha256",
    "externalInstructionCount",
    "actualGhidraInstructionCount",
]

TARGETS = {
    "0x00595fc9": {
        "candidateId": "D3DX-GAP-002",
        "range": "0x00595fc9-0x00596028",
        "bytes": "95",
        "rangeSha256": "1cea7a5ba832f2c8ca7487f3bcb5f2bbeefcdb5aa3ba42ba639a53eccba7a15d",
        "bodySha256": "b91d66da66baa5048ca7c1f09fd8763ec7e8396094cf465b7eb0811eeae50be9",
        "instructions": "35",
        "name": "FUN_00595fc9",
    },
    "0x00596028": {
        "candidateId": "D3DX-GAP-003",
        "range": "0x00596028-0x005960c1",
        "bytes": "153",
        "rangeSha256": "5d164cd810a8e0e4c15f0968d2c751452c1ee44287d68bdb063af4d2746c79d0",
        "bodySha256": "9c8ef8f1b2207d973324d8d7fe2e793cfc3d486a931a5a18ac75cb75817beb9b",
        "instructions": "57",
        "name": "FUN_00596028",
    },
}


def verify_manifest(root: Path) -> list[dict[str, Any]]:
    artifacts = [
        require_stamp(root, "inputs/manifest.tsv", size=608, sha256=MANIFEST_SHA256),
        require_stamp(
            root,
            "inputs/pre/functions.tsv",
            size=7_161_942,
            sha256=PRE_FUNCTIONS_SHA256,
        ),
        require_stamp(
            root,
            "inputs/pre/program.tsv",
            size=1_267,
            sha256=PRE_PROGRAM_SHA256,
        ),
    ]
    fields, rows = read_tsv(root / "inputs/manifest.tsv")
    require(
        fields
        == [
            "entry",
            "expectedRanges",
            "expectedBodyBytes",
            "expectedRangeDigest",
            "expectedBodyBytesSha256",
            "expectedInstructionCount",
            "currentState",
            "promotionLane",
        ],
        "manifest schema drift",
    )
    require(len(rows) == 2, "manifest row count")
    require({row["entry"] for row in rows} == set(TARGETS), "manifest target set")
    for row in rows:
        target = TARGETS[row["entry"]]
        require(row["expectedRanges"] == target["range"], "manifest range drift")
        require(row["expectedBodyBytes"] == target["bytes"], "manifest byte drift")
        require(row["expectedRangeDigest"] == target["rangeSha256"], "manifest digest drift")
        require(
            row["expectedBodyBytesSha256"] == target["bodySha256"],
            "manifest body hash drift",
        )
        require(row["expectedInstructionCount"] == target["instructions"], "manifest instructions")
        require(
            row["currentState"] == "ABSENT_FROM_CURRENT_8280_FUNCTION_CENSUS",
            "manifest PRE state",
        )
        require(row["promotionLane"] == "D3DX_GAP_TWO_SCRATCH_ONLY", "manifest policy")
    return artifacts


def verify_static_reconciliation(root: Path) -> list[dict[str, Any]]:
    expected = {
        "current-dispositions.tsv": (1_651, "8d6149eed095426e59a1769b5d78b3fbce645027e6a0786f8b429907ca1931ac"),
        "current-reconciliation.ready.json": (8_382, "ce3e210427a5675e3ab37ad112f3dea1fd5433e178746888fc0a479ef08a59fa"),
        "verify_current.py": (16_310, "eaf1d610a04c3908b9bd99142752a6e15e13dbc6bcb24efe31323cca8d99154e"),
        "d3dx-gap-cohort.tsv": (3_437, "c493202f367fdcd4e11059dc731f2588646e6e122fbcc3690bb39bcfb1719400"),
        "d3dx-gap-cohort-cfg.tsv": (7_691, "013cdd9d93cc25ef893ddc524b24bda6096cc90f535a630185213f360730de41"),
        "d3dx-gap-cohort.ready.json": (7_545, "0865a4ed4669426ad0cc347044910ff7caed9da413e4e95d22f187a82faf9e88"),
    }
    artifacts = [
        require_stamp(root, f"inputs/static-current/{name}", size=size, sha256=digest)
        for name, (size, digest) in expected.items()
    ]
    ready = read_json(root / "inputs/static-current/current-reconciliation.ready.json")
    require(ready["schema"] == "bea.re.pc-xbox-d3dx-gap-current8280.v1", "static schema")
    require(ready["verdict"] == "PASS_CURRENT_RECONCILIATION_NO_GHIDRA_MUTATION", "static verdict")
    require(ready["ghidraMutation"] is False, "static mutation boundary")
    require(ready["current"] == {
        "bodyRanges": 8400,
        "functions": 8280,
        "ownedTextBytes": 1794212,
        "textBytes": 1929117,
        "unownedTextBytes": 134905,
    }, "static PRE census")
    require(ready["cohort"]["missingBoundaries"] == 2, "static missing count")
    require(ready["cohort"]["missingBytes"] == 248, "static missing bytes")
    require(ready["cohort"]["missingInstructions"] == 92, "static missing instructions")
    missing = {
        row["pcStart"]: row
        for row in ready["dispositions"]
        if row["currentDisposition"] == "STATIC_BOUNDARY_REPRODUCED_NOT_ADMITTED"
    }
    require(set(missing) == set(TARGETS), "static missing target set")
    for entry, target in TARGETS.items():
        row = missing[entry]
        require(row["bytes"] == target["bytes"], f"static bytes {entry}")
        require(row["instructionCount"] == target["instructions"], f"static instructions {entry}")
        require(row["bodySha256"] == target["bodySha256"], f"static body hash {entry}")
    return artifacts


def validate_receipt(value: dict[str, Any], mode: str, expected_path: str) -> None:
    require(value["schemaVersion"] == "bea.ghidra.d3dx-gap-two-boundaries.v1", f"{mode} schema")
    require(value["mode"] == mode, f"{mode} mode")
    require(value["tool"] == {
        "path": "tools/GhidraApplyD3dxGapBoundaries.java",
        "bytes": 46_399,
        "sha256": MUTATOR_SHA256,
    }, f"{mode} tool stamp")
    require(value["manifest"] == {
        "path": "reverse-engineering/binary-analysis/d3dx-gap-two-function-scratch-manifest-2026-08-14.tsv",
        "bytes": 608,
        "sha256": MANIFEST_SHA256,
    }, f"{mode} manifest stamp")
    require(value["output"]["path"] == expected_path, f"{mode} output path")
    require(value["program"] == {
        "name": "BEA.exe",
        "md5": RETAIL_MD5,
        "sha256": RETAIL_SHA256,
    }, f"{mode} program identity")
    expected_counts = {
        "dry": {
            "targets": 2,
            "functionsBefore": 8280,
            "functionsAfter": 8280,
            "instructionsBefore": 550991,
            "instructionsAfter": 550991,
            "referencesBefore": 234495,
            "referencesAfter": 234495,
        },
        "apply": {
            "targets": 2,
            "functionsBefore": 8280,
            "functionsAfter": 8282,
            "instructionsBefore": 550991,
            "instructionsAfter": 550991,
            "referencesBefore": 234495,
            "referencesAfter": 234495,
        },
        "readback": {
            "targets": 2,
            "functionsBefore": 8282,
            "functionsAfter": 8282,
            "instructionsBefore": 550991,
            "instructionsAfter": 550991,
            "referencesBefore": 234495,
            "referencesAfter": 234495,
        },
    }
    require(value["counts"] == expected_counts[mode], f"{mode} counts")
    require(value["explicitBodySetsAuthorized"] is True, f"{mode} body authorization")
    require(value["namesAuthorized"] is False, f"{mode} name boundary")
    require(value["metadataAuthorized"] is False, f"{mode} metadata boundary")
    require(value["separateReadbackRequired"] is (mode != "readback"), f"{mode} readback policy")


def validate_boundary_rows(rows: list[dict[str, str]], status: str) -> None:
    require(len(rows) == 2, f"{status} boundary row count")
    require({row["entry"] for row in rows} == set(TARGETS), f"{status} target set")
    for row in rows:
        target = TARGETS[row["entry"]]
        require(row["candidateId"] == target["candidateId"], f"{status} candidate id")
        require(row["cohort"] == "D3DX_GAP_TWO", f"{status} cohort")
        require(row["status"] == status, f"{status} state")
        require(row["expectedRanges"] == target["range"], f"{status} expected ranges")
        require(row["expectedBodyBytes"] == target["bytes"], f"{status} expected bytes")
        require(row["expectedRangeSha256"] == target["rangeSha256"], f"{status} range hash")
        require(row["expectedBodyBytesSha256"] == target["bodySha256"], f"{status} body hash")
        require(row["externalInstructionCount"] == target["instructions"], f"{status} instructions")
        if status == "ready_absent":
            require(row["name"] == row["nameSource"] == "", "dry name fields")
            require(row["actualRanges"] == "", "dry actual ranges")
            require(row["actualBodyBytes"] == "0", "dry actual bytes")
            require(row["actualRangeSha256"] == row["actualBodyBytesSha256"] == "", "dry actual hashes")
            require(row["actualGhidraInstructionCount"] == "0", "dry instruction count")
        else:
            require(row["name"] == target["name"], f"{status} default name")
            require(row["nameSource"] == "DEFAULT", f"{status} name source")
            require(row["actualRanges"] == target["range"], f"{status} actual ranges")
            require(row["actualBodyBytes"] == target["bytes"], f"{status} actual bytes")
            require(row["actualRangeSha256"] == target["rangeSha256"], f"{status} actual range hash")
            require(row["actualBodyBytesSha256"] == target["bodySha256"], f"{status} actual body hash")
            require(row["actualGhidraInstructionCount"] == target["instructions"], f"{status} actual instructions")


def verify_boundary_run(root: Path, run: str, mode: str, status: str, expected_hash: str) -> list[dict[str, Any]]:
    prefix = f"runs/{run}"
    result = require_stamp(root, f"{prefix}/boundaries.tsv", sha256=expected_hash)
    ready_stamp = require_stamp(root, f"{prefix}/boundaries.ready.json")
    fields, rows = read_tsv(root / f"{prefix}/boundaries.tsv")
    require(fields == BOUNDARY_FIELDS, f"boundary schema drift: {run}")
    validate_boundary_rows(rows, status)
    value = read_json(root / f"{prefix}/boundaries.ready.json")
    validate_receipt(
        value,
        mode,
        f"local-lab/d3dx-gap-two-boundary-scratch-20260814-v1/{prefix}/boundaries.tsv",
    )
    require(value["output"]["bytes"] == result["bytes"], f"{run} output bytes")
    require(value["output"]["sha256"] == result["sha256"], f"{run} output hash")
    log = require_stamp(root, f"{prefix}/ghidra.log")
    text = (root / f"{prefix}/ghidra.log").read_text(encoding="utf-8", errors="strict")
    require("D3DX_GAP_BOUNDARIES_OK" in text, f"{run} success marker")
    require("REPORT SCRIPT ERROR:" not in text, f"{run} unexpected script error")
    return [result, ready_stamp, log]


def rows_by_address(path: Path) -> tuple[list[str], dict[str, dict[str, str]]]:
    fields, rows = read_tsv(path)
    result = {row["address"]: row for row in rows}
    require(len(result) == len(rows), f"duplicate address: {path}")
    return fields, result


def verify_positive_replicas(root: Path) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for replica in ("a", "b"):
        artifacts.extend(verify_boundary_run(root, f"replica-{replica}-dry", "dry", "ready_absent", DRY_BOUNDARIES_SHA256))
        artifacts.extend(verify_boundary_run(root, f"replica-{replica}-apply", "apply", "created", APPLY_BOUNDARIES_SHA256))
        artifacts.extend(verify_boundary_run(root, f"replica-{replica}-readback", "readback", "verified", READBACK_BOUNDARIES_SHA256))
        artifacts.extend([
            require_stamp(root, f"runs/replica-{replica}-readback/functions.tsv", size=7_163_259, sha256=POST_FUNCTIONS_SHA256),
            require_stamp(root, f"runs/replica-{replica}-readback/program.tsv", size=1_267, sha256=POST_PROGRAM_SHA256),
        ])

    pre_fields, pre = rows_by_address(root / "inputs/pre/functions.tsv")
    post_fields, post = rows_by_address(root / "runs/replica-a-readback/functions.tsv")
    require(pre_fields == post_fields, "function inventory schema drift")
    require(len(pre) == 8280 and len(post) == 8282, "function inventory cardinality")
    require(set(pre).issubset(post), "PRE function set not preserved")
    for address, row in pre.items():
        require(row == post[address], f"PRE function row drift: {address}")
    require(set(post) - set(pre) == set(TARGETS), "POST extra target set")
    for address, target in TARGETS.items():
        row = post[address]
        require(row["name"] == target["name"], f"POST name: {address}")
        require(row["nameSource"] == row["sigSource"] == "DEFAULT", f"POST source: {address}")
        require(row["bodyBytes"] == target["bytes"], f"POST bytes: {address}")
        require(row["bodyRanges"] == "1", f"POST ranges: {address}")
        require(row["bodyDigest"] == target["rangeSha256"], f"POST body digest: {address}")
        require(row["instrCount"] == target["instructions"], f"POST instructions: {address}")

    pre_metrics = metrics(root / "inputs/pre/program.tsv")
    post_metrics = metrics(root / "runs/replica-a-readback/program.tsv")
    changed = {key for key in pre_metrics if pre_metrics[key] != post_metrics[key]}
    require(changed == {"functions"}, f"unexpected program metric delta: {changed}")
    require(pre_metrics["functions"] == "8280" and post_metrics["functions"] == "8282", "program function counts")
    require(post_metrics["instructions"] == "550991", "program instruction count")
    require(post_metrics["references"] == "234495", "program reference count")
    return artifacts


def verify_controls(root: Path) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    adverse = {
        "failure-after-one": [
            "D3DX_GAP_BOUNDARIES_FORCED_AFTER_ONE_FAILURE",
            "D3DX_GAP_BOUNDARIES_MUTATION_TAINTED mode=probe-after-one",
            "forced failure after one D3DX gap function",
        ],
        "failure-post-inner": [
            "D3DX_GAP_BOUNDARIES_COMPENSATING_PRE_RESTORE_COMPLETE",
            "D3DX_GAP_BOUNDARIES_FORCED_POST_INNER_FAILURE",
            "D3DX_GAP_BOUNDARIES_MUTATION_TAINTED mode=probe-post-inner",
        ],
        "containment-output": ["receipts must stay inside this repository's local-lab tree"],
        "containment-ready": ["receipts must stay inside this repository's local-lab tree"],
    }
    for run, markers in adverse.items():
        log_stamp = require_stamp(root, f"runs/{run}/ghidra.log")
        artifacts.append(log_stamp)
        text = (root / f"runs/{run}/ghidra.log").read_text(encoding="utf-8", errors="strict")
        require("REPORT SCRIPT ERROR:" in text, f"{run} expected script error")
        for marker in markers:
            require(marker in text, f"{run} marker missing: {marker}")
        require(not (root / f"runs/{run}/boundaries.tsv").exists(), f"{run} published output")
        require(not (root / f"runs/{run}/boundaries.ready.json").exists(), f"{run} published READY")

    for run in (
        "failure-after-one-readback",
        "failure-post-inner-readback",
        "containment-output-readback",
        "containment-ready-readback",
    ):
        artifacts.extend(verify_boundary_run(root, run, "dry", "ready_absent", DRY_BOUNDARIES_SHA256))
        artifacts.extend([
            require_stamp(root, f"runs/{run}/functions.tsv", size=7_161_942, sha256=PRE_FUNCTIONS_SHA256),
            require_stamp(root, f"runs/{run}/program.tsv", size=1_267, sha256=PRE_PROGRAM_SHA256),
        ])
    return artifacts


def project_manifest(root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    project_files = []
    for candidate in root.rglob("*"):
        if not candidate.is_file():
            continue
        relative = candidate.relative_to(root)
        if relative.as_posix() == "BEA.gpr" or relative.parts[0] == "BEA.rep":
            project_files.append(candidate)
    for path in sorted(project_files, key=lambda item: item.relative_to(root).as_posix()):
        require(not is_reparse(path), f"reparse point in project: {path}")
        rows.append({
            "relative_path": path.relative_to(root).as_posix(),
            "size": path.stat().st_size,
            "sha256": sha256_file(path),
        })
    return rows


def verify_backup(root: Path, repo: Path) -> list[dict[str, Any]]:
    ready_path = root / "runs/base-restore/base-restore.ready.json"
    ready_stamp = require_stamp(root, "runs/base-restore/base-restore.ready.json", size=5_993)
    value = read_json(ready_path)
    require(value["schemaVersion"] == "onslaught-ghidra-project-backup.v2", "backup schema")
    require(value["sourceStable"] is True, "backup source stability")
    require(value["copyComparison"]["matches"] is True, "backup copy equality")
    source = value["source"]
    require(source["fileCount"] == 19 and source["totalBytes"] == 186_960_773, "backup source size")
    require(source["structurallyComplete"] is True, "backup structural completeness")
    expected_rows = source["files"]
    require(project_manifest(repo / "reverse-engineering/ghidra") == expected_rows, "current tracked project differs from backup source")
    probe_root = root / "projects/base-restore-probe-root"
    probes = [path for path in probe_root.iterdir() if path.is_dir()]
    require(len(probes) == 1 and probes[0].name.startswith("BEA-open-probe-"), "retained probe topology")
    require(project_manifest(probes[0]) == expected_rows, "retained probe differs from source")
    readonly = value["readonlyOpen"]
    require(readonly["opened"] is True and readonly["exitCode"] == 0, "read-only open result")
    require(readonly["contentStable"] is True, "read-only open content stability")
    require(readonly["postOpenComparison"]["matches"] is True, "read-only post-open equality")
    require(readonly["observedProgramMd5"] == RETAIL_MD5, "open MD5")
    require(readonly["observedProgramSha256"] == RETAIL_SHA256, "open SHA-256")
    argv = readonly["commandArgv"]
    require("-readOnly" in argv and "-noanalysis" in argv, "unsafe open argv")
    require("-commit" not in argv, "open argv permits commit")
    require(argv[-4:] == ["GhidraProjectOpenProbe.java", "BEA.exe", RETAIL_MD5, RETAIL_SHA256], "open probe argv tail")
    require(Path(argv[1]).name == probes[0].name, "open probe project role")
    probe_log = readonly["probeLog"]
    log_stamp = require_stamp(
        root,
        f"runs/base-restore/{probe_log['path']}",
        size=probe_log["bytes"],
        sha256=probe_log["sha256"],
    )
    text = (root / f"runs/base-restore/{probe_log['path']}").read_text(encoding="utf-8", errors="strict")
    require("GHIDRA_PROJECT_OPEN_PROBE_OK" in text, "open sentinel")
    require("REPORT SCRIPT ERROR:" not in text, "open log contains script error")
    db = [row for row in expected_rows if row["relative_path"].endswith("db.18613.gbf")]
    require(db == [{
        "relative_path": "BEA.rep/idata/00/~00000000.db/db.18613.gbf",
        "sha256": DB_SHA256,
        "size": 68_337_664,
    }], "db.18613 identity")
    return [ready_stamp, log_stamp]


EXPECTED_RUN_FILES = {
    "base-restore": {"base-restore.ready.json", "base-restore.ready.open-probe.log"},
    "containment-output": {"ghidra.log"},
    "containment-ready": {"ghidra.log"},
    "failure-after-one": {"ghidra.log"},
    "failure-post-inner": {"ghidra.log"},
    "replica-a-dry": {"boundaries.tsv", "boundaries.ready.json", "ghidra.log", "project-after.json"},
    "replica-b-dry": {"boundaries.tsv", "boundaries.ready.json", "ghidra.log", "project-after.json"},
    "replica-a-apply": {"boundaries.tsv", "boundaries.ready.json", "ghidra.log"},
    "replica-b-apply": {"boundaries.tsv", "boundaries.ready.json", "ghidra.log"},
    "exploratory-dry": {"boundaries.tsv", "boundaries.ready.json", "ghidra.log"},
    "exploratory-apply": {"boundaries.tsv", "boundaries.ready.json", "ghidra.log"},
    "exploratory-readback": {"boundaries.tsv", "boundaries.ready.json", "functions.tsv", "ghidra.log", "inventory-diff.json", "program.tsv"},
}
for _name in (
    "replica-a-readback",
    "replica-b-readback",
    "failure-after-one-readback",
    "failure-post-inner-readback",
    "containment-output-readback",
    "containment-ready-readback",
):
    EXPECTED_RUN_FILES[_name] = {"boundaries.tsv", "boundaries.ready.json", "functions.tsv", "ghidra.log", "program.tsv"}

EXPECTED_PROJECTS = {
    "base-restore-probe-root",
    "containment-output",
    "containment-ready",
    "exploratory",
    "failure-after-one",
    "failure-post-inner",
    "replica-a",
    "replica-b",
}


def verify_topology(root: Path) -> None:
    runs = root / "runs"
    actual_runs = {path.name for path in runs.iterdir() if path.is_dir()}
    require(actual_runs == set(EXPECTED_RUN_FILES), f"run directory census drift: {actual_runs ^ set(EXPECTED_RUN_FILES)}")
    require(all(path.is_dir() for path in runs.iterdir()), "non-directory entry under runs")
    for run, expected in EXPECTED_RUN_FILES.items():
        actual = {path.name for path in (runs / run).iterdir()}
        require(actual == expected, f"run file-set drift {run}: {actual ^ expected}")
        require(all(path.is_file() and not is_reparse(path) for path in (runs / run).iterdir()), f"unsafe entry under run {run}")
    projects = root / "projects"
    actual_projects = {path.name for path in projects.iterdir() if path.is_dir()}
    require(actual_projects == EXPECTED_PROJECTS, f"project directory census drift: {actual_projects ^ EXPECTED_PROJECTS}")
    require(all(path.is_dir() for path in projects.iterdir()), "non-directory entry under projects")


def is_reparse(path: Path) -> bool:
    try:
        stat = path.lstat()
    except FileNotFoundError as exc:
        raise AuthorityError(f"artifact disappeared during verification: {path}") from exc
    return path.is_symlink() or bool(getattr(stat, "st_file_attributes", 0) & 0x400)


def artifact_tree(root: Path, excluded: Path) -> dict[str, Any]:
    root = root.resolve(strict=True)
    excluded = excluded.resolve(strict=False)
    rows: list[tuple[str, int, str]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        require(not is_reparse(path), f"reparse point in package: {path}")
        relative = path.relative_to(root).as_posix()
        require("__pycache__" not in path.parts and path.suffix != ".pyc", f"Python cache in package: {relative}")
        if path.is_dir():
            continue
        require(path.is_file(), f"non-file package entry: {relative}")
        if path.resolve(strict=True) == excluded:
            continue
        rows.append((relative, path.stat().st_size, sha256_file(path)))
    digest = hashlib.sha256()
    for relative, size, file_hash in rows:
        digest.update(f"{relative}\0{size}\0{file_hash}\n".encode("utf-8"))
    return {
        "files": len(rows),
        "bytes": sum(size for _, size, _ in rows),
        "sha256": digest.hexdigest(),
    }


def verify_tools(root: Path, repo: Path) -> list[dict[str, Any]]:
    expected = {
        "GhidraApplyD3dxGapBoundaries.java": (46_399, MUTATOR_SHA256),
        "ExportFullFunctionInventory.java": (23_963, "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197"),
        "ghidra_project_backup.py": (27_502, "0f426982916f0aab982efe54664342a5d34607c2f89707159ecf6c07e205ad58"),
        "GhidraProjectOpenProbe.java": (3_452, "fab2f701dfefe8604c1718d007dbe0ad59d330a9b3ec081ef2f2fe253b441fab"),
    }
    artifacts: list[dict[str, Any]] = []
    for name, (size, digest) in expected.items():
        packaged = require_stamp(root, f"tools/{name}", size=size, sha256=digest)
        tracked = require_stamp(repo, f"tools/{name}", size=size, sha256=digest)
        artifacts.extend((packaged, {**tracked, "path": f"repo/{tracked['path']}"}))
    authority = Path(__file__).resolve(strict=True)
    require(authority == (root / "tools/ghidra_d3dx_gap_boundary_scratch_authority.py").resolve(strict=True), "authority must run from sealed package")
    return artifacts


def verify_semantics(root: Path) -> dict[str, Any]:
    root = root.resolve(strict=True)
    require(root.name == "d3dx-gap-two-boundary-scratch-20260814-v1", "package name drift")
    repo = root.parent.parent.resolve(strict=True)
    require((repo / ".git").exists(), "repository root not found")
    tracked_manifest = require_stamp(
        repo,
        "reverse-engineering/binary-analysis/d3dx-gap-two-function-scratch-manifest-2026-08-14.tsv",
        size=608,
        sha256=MANIFEST_SHA256,
    )
    verify_topology(root)
    artifacts = [
        *verify_manifest(root),
        *verify_static_reconciliation(root),
        *verify_positive_replicas(root),
        *verify_controls(root),
        *verify_backup(root, repo),
        *verify_tools(root, repo),
        {**tracked_manifest, "path": f"repo/{tracked_manifest['path']}"},
    ]
    require(len({row["path"] for row in artifacts}) == len(artifacts), "duplicate semantic artifact path")
    return {
        "schema": "bea.ghidra.d3dx-gap-two-scratch-authority.v1",
        "status": "READY",
        "verdict": "SCRATCH_READY_LIVE_FORBIDDEN",
        "policy": "LIVE_FORBIDDEN",
        "program": {"name": "BEA.exe", "md5": RETAIL_MD5, "sha256": RETAIL_SHA256},
        "pre": {
            "functions": 8280,
            "bodyRanges": 8400,
            "ownedTextBytes": 1794212,
            "instructions": 550991,
            "references": 234495,
            "db": "db.18613.gbf",
            "dbSha256": DB_SHA256,
        },
        "post": {
            "functions": 8282,
            "bodyRanges": 8402,
            "ownedTextBytes": 1794460,
            "instructions": 550991,
            "references": 234495,
            "newDefaultFunctions": 2,
            "addedOwnedTextBytes": 248,
        },
        "proof": {
            "positiveReplicas": 2,
            "separateReadbacks": 2,
            "unchangedPreRowsExact": 8280,
            "forcedRollbackControls": 2,
            "containmentRefusals": 2,
            "restoredPreReadbacksExact": 4,
            "readOnlyBackupOpen": "PASS",
        },
        "limitations": [
            "The two functions retain DEFAULT names and metadata; this campaign authorizes no D3DX-compatible semantic names, signatures, comments, or grades.",
            "The D3DX API-compatible classifications are static compatibility claims, not original linker-symbol identities or runtime parity claims.",
            "The exploratory project and exploratory runs are preserved but superseded; only replica-a, replica-b, the four controls, and their separate readbacks are load-bearing.",
            "The backup receipt preserves ceremony-time absolute location fields; this verifier rebinds project roles to the current repository and sealed package and validates both physical trees exactly.",
            "This scratch receipt never authorizes a live, shared, tracked, or canonical Ghidra mutation.",
        ],
        "semanticArtifacts": sorted(artifacts, key=lambda row: row["path"]),
    }


def seal(root: Path, receipt_path: Path) -> dict[str, Any]:
    require(not receipt_path.exists(), "refusing to overwrite authority receipt")
    require(receipt_path.parent == root, "authority receipt must be at package root")
    receipt = verify_semantics(root)
    receipt["artifactTreeExcludingReceipt"] = artifact_tree(root, receipt_path)
    receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def verify(root: Path, receipt_path: Path) -> dict[str, Any]:
    require(receipt_path.is_file(), "authority receipt is missing")
    require(receipt_path.parent == root, "authority receipt must be at package root")
    expected = read_json(receipt_path)
    actual = verify_semantics(root)
    for key in actual:
        require(expected.get(key) == actual[key], f"authority receipt semantic drift: {key}")
    require(expected.get("artifactTreeExcludingReceipt") == artifact_tree(root, receipt_path), "artifact tree drift")
    return expected


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("seal", "verify"))
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args(argv)
    root = args.package_root.resolve(strict=True)
    receipt = args.receipt.resolve(strict=False)
    result = seal(root, receipt) if args.mode == "seal" else verify(root, receipt)
    print(
        "D3DX_GAP_TWO_SCRATCH_AUTHORITY_VERIFIED "
        f"functions={result['post']['functions']} targets=2 replicas=2 controls=4 "
        "verdict=SCRATCH_READY_LIVE_FORBIDDEN"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuthorityError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        raise SystemExit(2)
