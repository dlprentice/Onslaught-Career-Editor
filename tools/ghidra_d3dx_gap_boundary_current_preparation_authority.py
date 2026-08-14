#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Seal or verify the current-db.18617 two-function D3DX preparation.

This owner is read-only except when ``seal`` creates one new aggregate receipt.
It never launches Ghidra and never authorizes a live or tracked project write.
The resulting policy remains PREPARATION_ONLY.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping


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


SCHEMA = "bea.ghidra.d3dx-gap-two-current-preparation-authority.v1"
POLICY = "PREPARATION_ONLY"
PACKAGE_NAME = "d3dx-gap-two-boundary-current-preparation-20260814-v1"
SCRATCH_PACKAGE_NAME = "d3dx-gap-two-boundary-scratch-20260814-v1"
SCRATCH_RECEIPT_SHA256 = (
    "f68ae99ed352b1f3087a8f0b61eb53dff95d978450a929e70e2d428451216a5d"
)
SCRATCH_TREE_SHA256 = (
    "655f53d43cd2afe2fab7912197e3d20f15ed21b538b6607d2b538d4f3ffa63f0"
)

RETAIL_MD5 = "3b456964020070efe696d2cc09464a55"
RETAIL_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
PRE_DB_SHA256 = "52cedb3555f418ea8000b0f8bb4c14cddc8c88954b3a5f3104e7600c487b52b0"
PRE_PROJECT_SHA256 = (
    "a7916b5642b808f468ef113e731a4cfcf225287c94264009fde1034edd9b91cf"
)
POST_PROJECT_SHA256 = {
    "a": "8c71ff4146f2d6c0be45fa53f3b8b0404f3413984be02bf71b37b943188b2570",
    "b": "06411067f1a9c5dd5df875f8f9b2f626d2561cd872aad8945139d535d04d7803",
}
POST_DB_SHA256 = {
    "a": "e9bac3ccf7ac1676444eef7386edf6806380691469ec318370329f30161bae2f",
    "b": "4f9121fd297eaefb029addcddf0a2ae223c563c4f2663593ce6073d0338c6896",
}
CONTROL_PROJECT_SHA256 = {
    "failure-after-one": "1532549bae0d9ff183fb4b826478a7bf9b51330a428d947a989680d4eedea6c7",
    "failure-post-inner": "dba31b192591e9e638dcb6f203c8b8865d8d01956c0cb95cc50b20606500e24d",
    "containment-output": "a3d5a8cd0ae7260912abf711069973ce34cde4f80b2737c88a85adb44a01ce42",
    "containment-ready": "d6801723d72585e8c14aceb1f4edbe6e88c6046c6434c4d6162659f1cc4dceda",
}
CONTROL_DB_SHA256 = {
    "failure-after-one": "7401e1c7155cc93458507e011a7856662640fbf9e4fd41d8c2fddefeeb5eed84",
    "failure-post-inner": "613ab452f8658c86bf74400b7a4b9bfc406749041f10a135b9f526b50e2fc0b9",
    "containment-output": "21ab50203592f884d14e2ed9ba9166c224b6949b251d5eb38e132ca21c0a651b",
    "containment-ready": "4a333bf144c2c4c8e42b6427dda5a3283ecd909b060ca2270331adf442ad62d0",
}

PRE_FUNCTIONS = 8327
POST_FUNCTIONS = 8329
PRE_RANGES = 8457
POST_RANGES = 8459
PRE_OWNED = 1_811_443
POST_OWNED = 1_811_691
PRE_INSTRUCTIONS = POST_INSTRUCTIONS = 551_143
PRE_REFERENCES = POST_REFERENCES = 234_478
TEXT_BYTES = 1_929_117

MANIFEST_REL = (
    "reverse-engineering/binary-analysis/"
    "d3dx-gap-two-function-current-manifest-2026-08-14.tsv"
)
MANIFEST_STAMP = (
    622,
    "48da3f9e6c6606a5a7c14443e6fe5f3191a24fb35dfc40ec67f886f27d0351e7",
)
MUTATOR_STAMP = (
    46_410,
    "124fead4f8729bc1ef484cc09eae2b871b5117535a1bfbcb377120883afd30c9",
)
PRE_FUNCTIONS_STAMP = (
    7_192_981,
    "08886e03b846668681301f0f2ec2ba9ac1af0463faa1835c57abe9e717ebd866",
)
PRE_PROGRAM_STAMP = (
    1_267,
    "e77082ead314ccb44ba070a7b42222e063ec1078d22ab2203fa6ee8968f99909",
)
POST_FUNCTIONS_STAMP = (
    7_194_298,
    "7b343b3578a01562daca02ec431586cf39e042d0daab9d6aa9448b779f880ef0",
)
POST_PROGRAM_STAMP = (
    1_267,
    "a34ca7df45912ed4c7987e59082fcd489726a498721a81ef8aee5ce718c8f523",
)
BODY_RANGES_STAMP = (
    1_205_856,
    "dd655ef41d127a48cbd936cf6022c4216453d8c636c8e95c6b591e281780ea76",
)
DIRECT_CALLS_STAMP = (
    1_397_680,
    "159f7c89aae54df927186d71263941b5f0857debe09556097820f098da8fa9d8",
)
LISTING_STAMP = (
    587,
    "db3a3db1d6a816be94c8d63707a5104ae06ce252e1bfd3a3ded839a9a331ca66",
)
PROJECTION_STAMP = (
    510_444,
    "6b54dc9459ca3f54f4606117943ee7d34e236bccb6fa2e7eff1e3aef8d2dd2b8",
)
DRY_BOUNDARIES_SHA256 = (
    "ebafb3f84a3e0f1dc631f6929200693ff499d195b518e96d0a4342e291f9dc28"
)
APPLY_BOUNDARIES_SHA256 = (
    "b3651e2f11334a5e0dd0305b205b061a6803d4254068c3cb14891472c81ae2be"
)
READBACK_BOUNDARIES_SHA256 = (
    "b6e75cef06e9425687ee600bff6bdff31dae0120d2351dcaedbe29949a01fd88"
)

EXPECTED_TOOLS = {
    "DiagnoseAddressListingState.java": (
        3_956,
        "183394907659e7810c77a9720e1899fd8a6296e6e86673495d68a2764edefe69",
    ),
    "ExportFullFunctionInventory.java": (
        23_963,
        "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197",
    ),
    "ExportParityLabGraph.java": (
        17_663,
        "e91e26c428f593e3fd49f755fcc8551dd685ce41825fe180966be49594cbbec9",
    ),
    "ghidra_project_backup.py": (
        27_502,
        "0f426982916f0aab982efe54664342a5d34607c2f89707159ecf6c07e205ad58",
    ),
    "GhidraApplyD3dxGapBoundariesV2.java": MUTATOR_STAMP,
    "GhidraProjectOpenProbe.java": (
        3_452,
        "fab2f701dfefe8604c1718d007dbe0ad59d330a9b3ec081ef2f2fe253b441fab",
    ),
    "re_ghidra_name_projection.py": (
        6_139,
        "d13d5f4d3b20cbd1e1baf24cd924d454c6c07b0bbf5517834c4089357f14ecdb",
    ),
}

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
        "rangeSha256": (
            "1cea7a5ba832f2c8ca7487f3bcb5f2bbeefcdb5aa3ba42ba639a53eccba7a15d"
        ),
        "bodySha256": (
            "b91d66da66baa5048ca7c1f09fd8763ec7e8396094cf465b7eb0811eeae50be9"
        ),
        "instructions": "35",
        "name": "FUN_00595fc9",
    },
    "0x00596028": {
        "candidateId": "D3DX-GAP-003",
        "range": "0x00596028-0x005960c1",
        "bytes": "153",
        "rangeSha256": (
            "5d164cd810a8e0e4c15f0968d2c751452c1ee44287d68bdb063af4d2746c79d0"
        ),
        "bodySha256": (
            "9c8ef8f1b2207d973324d8d7fe2e793cfc3d486a931a5a18ac75cb75817beb9b"
        ),
        "instructions": "57",
        "name": "FUN_00596028",
    },
}


def is_reparse(path: Path) -> bool:
    try:
        value = path.lstat()
    except FileNotFoundError as exc:
        raise AuthorityError(f"artifact disappeared: {path}") from exc
    return path.is_symlink() or bool(
        getattr(value, "st_file_attributes", 0) & 0x400
    )


def project_files(root: Path) -> list[dict[str, Any]]:
    root = root.resolve(strict=True)
    rows: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        require(not is_reparse(path), f"reparse point in project: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative == "backup_manifest.json":
            continue
        if relative != "BEA.gpr" and not relative.startswith("BEA.rep/"):
            continue
        rows.append(
            {
                "relative_path": relative,
                "sha256": sha256_file(path),
                "size": path.stat().st_size,
            }
        )
    return rows


def project_digest(value: Mapping[str, Any]) -> str:
    rows = list(value.get("files", []))
    paths = [str(row["relative_path"]) for row in rows]
    require(paths == sorted(paths), "project rows are not relative-path ordered")
    raw = "".join(
        f"{row['sha256']}\t{row['size']}\t{row['relative_path']}\n"
        for row in rows
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def project_summary(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "fileCount": value.get("fileCount"),
        "totalBytes": value.get("totalBytes"),
        "canonicalInventorySha256": project_digest(value),
        "canonicalization": (
            "sha256<TAB>bytes<TAB>relative-posix-path<LF>, relative-path order"
        ),
    }


def project_file_map(value: Mapping[str, Any]) -> dict[str, tuple[int, str]]:
    return {
        str(row["relative_path"]): (int(row["size"]), str(row["sha256"]))
        for row in value.get("files", [])
    }


def normalized_path(value: Any) -> str:
    require(isinstance(value, str) and value != "", "missing recorded path")
    return os.path.normcase(os.path.normpath(value))


def require_recorded_path(value: Any, expected: Path, role: str) -> None:
    require(
        normalized_path(value) == normalized_path(str(expected)),
        f"{role} recorded root",
    )


def recorded_escape_path(log_text: str, leaf: str) -> Path:
    candidates = {
        Path(segment)
        for segment in log_text.split("'")
        if segment.replace("\\", "/").lower().endswith(
            f"/appdata/local/temp/bea-d3dx-containment-20260814/{leaf}".lower()
        )
    }
    require(len(candidates) == 1, f"recorded containment path for {leaf}")
    result = next(iter(candidates))
    require(result.is_absolute(), f"containment path is not absolute: {leaf}")
    return result


def validate_project_value(
    value: Mapping[str, Any], expected_digest: str, role: str
) -> dict[str, Any]:
    require(value.get("projectName") == "BEA", f"{role} project name")
    require(value.get("fileCount") == 19, f"{role} file count")
    require(value.get("totalBytes") == 187_009_925, f"{role} byte count")
    require(value.get("structurallyComplete") is True, f"{role} completeness")
    require(project_digest(value) == expected_digest, f"{role} project digest")
    return project_summary(value)


def inspect_manifest(
    path: Path,
    expected_digest: str,
    role: str,
    *,
    expected_recorded_root: Path | None = None,
) -> Mapping[str, Any]:
    value = read_json(path)
    require(
        value.get("schemaVersion") == "onslaught-ghidra-project-backup.v2",
        f"{role} inspect schema",
    )
    manifest = value.get("manifest")
    require(isinstance(manifest, dict), f"{role} inspect manifest")
    if expected_recorded_root is not None:
        require_recorded_path(
            manifest.get("root"), expected_recorded_root, f"{role} inspect"
        )
    validate_project_value(manifest, expected_digest, role)
    return manifest


def actual_project(root: Path, expected_digest: str, role: str) -> Mapping[str, Any]:
    files = project_files(root)
    value = {
        "projectName": "BEA",
        "fileCount": len(files),
        "totalBytes": sum(int(row["size"]) for row in files),
        "structurallyComplete": True,
        "files": files,
    }
    validate_project_value(value, expected_digest, role)
    return value


def verify_manifest(package: Path, repo: Path) -> list[dict[str, Any]]:
    artifacts = [
        require_stamp(
            package,
            "inputs/manifest.tsv",
            size=MANIFEST_STAMP[0],
            sha256=MANIFEST_STAMP[1],
        ),
        require_stamp(
            package,
            "inputs/pre/functions.tsv",
            size=PRE_FUNCTIONS_STAMP[0],
            sha256=PRE_FUNCTIONS_STAMP[1],
        ),
        require_stamp(
            package,
            "inputs/pre/program.tsv",
            size=PRE_PROGRAM_STAMP[0],
            sha256=PRE_PROGRAM_STAMP[1],
        ),
    ]
    tracked = require_stamp(
        repo, MANIFEST_REL, size=MANIFEST_STAMP[0], sha256=MANIFEST_STAMP[1]
    )
    artifacts.append({**tracked, "path": f"repo/{tracked['path']}"})
    fields, rows = read_tsv(package / "inputs/manifest.tsv")
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
        require(
            row["expectedRangeDigest"] == target["rangeSha256"],
            "manifest range digest drift",
        )
        require(
            row["expectedBodyBytesSha256"] == target["bodySha256"],
            "manifest body hash drift",
        )
        require(
            row["expectedInstructionCount"] == target["instructions"],
            "manifest instruction drift",
        )
        require(
            row["currentState"] == "ABSENT_FROM_CURRENT_8327_FUNCTION_CENSUS",
            "manifest PRE state",
        )
        require(
            row["promotionLane"] == "D3DX_GAP_TWO_CURRENT_PREPARATION",
            "manifest policy",
        )
    return artifacts


def verify_tools(package: Path, repo: Path) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for name, (size, digest) in EXPECTED_TOOLS.items():
        packaged = require_stamp(
            package, f"tools/{name}", size=size, sha256=digest
        )
        tracked = require_stamp(repo, f"tools/{name}", size=size, sha256=digest)
        artifacts.extend((packaged, {**tracked, "path": f"repo/{tracked['path']}"}))
    name = "ghidra_d3dx_gap_boundary_current_preparation_authority.py"
    packaged = require_stamp(package, f"tools/{name}")
    tracked = require_stamp(repo, f"tools/{name}")
    require(
        (packaged["bytes"], packaged["sha256"])
        == (tracked["bytes"], tracked["sha256"]),
        "packaged authority differs from tracked authority",
    )
    artifacts.extend((packaged, {**tracked, "path": f"repo/{tracked['path']}"}))
    return artifacts


def verify_scratch(package: Path, scratch_package: Path) -> dict[str, Any]:
    copied = require_stamp(
        package,
        "inputs/scratch/scratch-authority.ready.json",
        size=14_021,
        sha256=SCRATCH_RECEIPT_SHA256,
    )
    receipt = scratch_package / "scratch-authority.ready.json"
    require(receipt.is_file(), "retained D3DX scratch receipt is missing")
    require(
        (receipt.stat().st_size, sha256_file(receipt))
        == (copied["bytes"], copied["sha256"]),
        "retained scratch receipt differs from preparation input",
    )
    value = read_json(receipt)
    require(
        value.get("schema") == "bea.ghidra.d3dx-gap-two-scratch-authority.v1",
        "scratch authority schema",
    )
    require(value.get("status") == "READY", "scratch authority status")
    require(
        value.get("verdict") == "SCRATCH_READY_LIVE_FORBIDDEN",
        "scratch authority verdict",
    )
    require(value.get("policy") == "LIVE_FORBIDDEN", "scratch authority policy")
    require(value.get("post", {}).get("functions") == 8_282, "scratch POST functions")
    require(
        value.get("post", {}).get("newDefaultFunctions") == 2,
        "scratch target count",
    )
    tree = value.get("artifactTreeExcludingReceipt", {})
    require(tree.get("sha256") == SCRATCH_TREE_SHA256, "scratch tree identity")
    owner = scratch_package / "tools/ghidra_d3dx_gap_boundary_scratch_authority.py"
    require(owner.is_file(), "packaged scratch authority is missing")
    actual_tree = artifact_tree(scratch_package, receipt)
    require(actual_tree == tree, "retained scratch artifact-tree drift")
    return {
        "receiptBytes": copied["bytes"],
        "receiptSha256": copied["sha256"],
        "tree": tree,
        "verdict": value.get("verdict"),
        "verification": "EXACT_SEALED_TREE_REHASH",
        "currentRootReplay": "INTENTIONALLY_SUPERSEDED_BY_DB18617_REPLICAS",
    }


def validate_receipt(value: dict[str, Any], mode: str, expected_path: str) -> None:
    require(
        value.get("schemaVersion") == "bea.ghidra.d3dx-gap-two-boundaries.v2",
        f"{mode} receipt schema",
    )
    require(value.get("mode") == mode, f"{mode} receipt mode")
    require(
        value.get("tool")
        == {
            "path": "tools/GhidraApplyD3dxGapBoundariesV2.java",
            "bytes": MUTATOR_STAMP[0],
            "sha256": MUTATOR_STAMP[1],
        },
        f"{mode} tool stamp",
    )
    require(
        value.get("manifest")
        == {
            "path": MANIFEST_REL,
            "bytes": MANIFEST_STAMP[0],
            "sha256": MANIFEST_STAMP[1],
        },
        f"{mode} manifest stamp",
    )
    require(value.get("output", {}).get("path") == expected_path, f"{mode} path")
    require(
        value.get("program")
        == {"name": "BEA.exe", "md5": RETAIL_MD5, "sha256": RETAIL_SHA256},
        f"{mode} program identity",
    )
    expected_counts = {
        "dry": {
            "targets": 2,
            "functionsBefore": PRE_FUNCTIONS,
            "functionsAfter": PRE_FUNCTIONS,
            "instructionsBefore": PRE_INSTRUCTIONS,
            "instructionsAfter": PRE_INSTRUCTIONS,
            "referencesBefore": PRE_REFERENCES,
            "referencesAfter": PRE_REFERENCES,
        },
        "apply": {
            "targets": 2,
            "functionsBefore": PRE_FUNCTIONS,
            "functionsAfter": POST_FUNCTIONS,
            "instructionsBefore": PRE_INSTRUCTIONS,
            "instructionsAfter": POST_INSTRUCTIONS,
            "referencesBefore": PRE_REFERENCES,
            "referencesAfter": POST_REFERENCES,
        },
        "readback": {
            "targets": 2,
            "functionsBefore": POST_FUNCTIONS,
            "functionsAfter": POST_FUNCTIONS,
            "instructionsBefore": POST_INSTRUCTIONS,
            "instructionsAfter": POST_INSTRUCTIONS,
            "referencesBefore": POST_REFERENCES,
            "referencesAfter": POST_REFERENCES,
        },
    }
    require(value.get("counts") == expected_counts[mode], f"{mode} counts")
    require(value.get("explicitBodySetsAuthorized") is True, f"{mode} body policy")
    require(value.get("namesAuthorized") is False, f"{mode} name policy")
    require(value.get("metadataAuthorized") is False, f"{mode} metadata policy")
    require(
        value.get("separateReadbackRequired") is (mode != "readback"),
        f"{mode} readback policy",
    )


def validate_boundary_rows(rows: list[dict[str, str]], status: str) -> None:
    require(len(rows) == 2, f"{status} row count")
    require({row["entry"] for row in rows} == set(TARGETS), f"{status} target set")
    for row in rows:
        target = TARGETS[row["entry"]]
        require(row["candidateId"] == target["candidateId"], f"{status} candidate")
        require(row["cohort"] == "D3DX_GAP_TWO", f"{status} cohort")
        require(row["status"] == status, f"{status} status")
        require(row["expectedRanges"] == target["range"], f"{status} range")
        require(row["expectedBodyBytes"] == target["bytes"], f"{status} bytes")
        require(
            row["expectedRangeSha256"] == target["rangeSha256"],
            f"{status} range hash",
        )
        require(
            row["expectedBodyBytesSha256"] == target["bodySha256"],
            f"{status} body hash",
        )
        require(
            row["externalInstructionCount"] == target["instructions"],
            f"{status} instruction count",
        )
        if status == "ready_absent":
            require(row["name"] == row["nameSource"] == "", "dry name fields")
            require(row["actualRanges"] == "", "dry actual ranges")
            require(row["actualBodyBytes"] == "0", "dry actual bytes")
            require(
                row["actualRangeSha256"] == row["actualBodyBytesSha256"] == "",
                "dry actual hashes",
            )
            require(row["actualGhidraInstructionCount"] == "0", "dry instructions")
        else:
            require(row["name"] == target["name"], f"{status} default name")
            require(row["nameSource"] == "DEFAULT", f"{status} name source")
            require(row["actualRanges"] == target["range"], f"{status} actual range")
            require(row["actualBodyBytes"] == target["bytes"], f"{status} actual bytes")
            require(
                row["actualRangeSha256"] == target["rangeSha256"],
                f"{status} actual range hash",
            )
            require(
                row["actualBodyBytesSha256"] == target["bodySha256"],
                f"{status} actual body hash",
            )
            require(
                row["actualGhidraInstructionCount"] == target["instructions"],
                f"{status} actual instructions",
            )


def verify_boundary_run(
    package: Path,
    run: str,
    mode: str,
    status: str,
    expected_hash: str,
) -> list[dict[str, Any]]:
    prefix = f"runs/{run}"
    result = require_stamp(package, f"{prefix}/boundaries.tsv", sha256=expected_hash)
    ready = require_stamp(package, f"{prefix}/boundaries.ready.json")
    fields, rows = read_tsv(package / f"{prefix}/boundaries.tsv")
    require(fields == BOUNDARY_FIELDS, f"boundary schema drift: {run}")
    validate_boundary_rows(rows, status)
    value = read_json(package / f"{prefix}/boundaries.ready.json")
    validate_receipt(value, mode, f"local-lab/{PACKAGE_NAME}/{prefix}/boundaries.tsv")
    require(value["output"]["bytes"] == result["bytes"], f"{run} output bytes")
    require(value["output"]["sha256"] == result["sha256"], f"{run} output hash")
    log = require_stamp(package, f"{prefix}/ghidra.log")
    text = (package / f"{prefix}/ghidra.log").read_text(
        encoding="utf-8", errors="strict"
    )
    require("D3DX_GAP_BOUNDARIES_OK" in text, f"{run} success marker")
    require("REPORT SCRIPT ERROR:" not in text, f"{run} unexpected script error")
    return [result, ready, log]


def rows_by_address(path: Path) -> tuple[list[str], dict[str, dict[str, str]]]:
    fields, rows = read_tsv(path)
    result = {row["address"]: row for row in rows}
    require(len(result) == len(rows), f"duplicate address: {path}")
    return fields, result


def verify_ranges(path: Path) -> None:
    with path.open("r", encoding="utf-8", newline="") as stream:
        data = [line for line in stream if not line.startswith("#")]
    reader = csv.DictReader(data, delimiter="\t")
    require(reader.fieldnames is not None, "range header")
    rows = list(reader)
    require(len(rows) == POST_RANGES, "POST range count")
    require(len({row["functionAddress"] for row in rows}) == POST_FUNCTIONS, "range owners")
    require(sum(int(row["rangeBytes"]) for row in rows) == POST_OWNED, "owned bytes")
    intervals = sorted(
        (int(row["rangeMin"], 16), int(row["rangeMax"], 16), row) for row in rows
    )
    previous_end = -1
    for start, end, row in intervals:
        require(start > previous_end, f"overlapping range: {row['functionAddress']}")
        require(end >= start, f"backward range: {row['functionAddress']}")
        require(end - start + 1 == int(row["rangeBytes"]), "range byte arithmetic")
        previous_end = end
    target_rows = {
        row["functionAddress"]: row
        for row in rows
        if row["functionAddress"] in TARGETS
    }
    require(set(target_rows) == set(TARGETS), "target range set")
    for address, target in TARGETS.items():
        row = target_rows[address]
        require(row["rangeBytes"] == target["bytes"], f"target range bytes {address}")
        require(row["rangeSha256"] == target["bodySha256"], f"target byte hash {address}")


def verify_listing(path: Path) -> None:
    fields, rows = read_tsv(path)
    require(
        fields
        == [
            "input",
            "address",
            "memory_block",
            "byte0",
            "instruction_at",
            "instruction_containing",
            "data_at",
            "data_containing",
            "function_at",
            "function_containing",
            "status",
        ],
        "listing schema",
    )
    require(len(rows) == 4, "listing row count")
    by_input = {row["input"]: row for row in rows}
    require(set(by_input) == {"0x00595fc9", "0x00596027", "0x00596028", "0x005960c0"}, "listing target set")
    for entry in TARGETS:
        row = by_input[entry]
        require(row["memory_block"] == ".text", f"entry memory {entry}")
        require(row["instruction_at"] == "MOV EAX,dword ptr [ESP + 0x8]", f"entry instruction {entry}")
        require(row["data_at"] == row["data_containing"] == "<none>", f"entry data {entry}")
        require(row["function_at"] == TARGETS[entry]["name"], f"entry function {entry}")
        require(row["function_containing"] == TARGETS[entry]["name"], f"entry owner {entry}")
        require(row["status"] == "OK", f"entry listing status {entry}")
    tails = {"0x00596027": "FUN_00595fc9", "0x005960c0": "FUN_00596028"}
    for address, owner in tails.items():
        row = by_input[address]
        require(row["instruction_at"] == "<none>", f"tail exact instruction {address}")
        require(row["instruction_containing"] == "RET 0xc", f"tail containing instruction {address}")
        require(row["function_at"] == "<none>", f"tail function entry {address}")
        require(row["function_containing"] == owner, f"tail owner {address}")


def verify_positive_replicas(package: Path) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for replica in ("a", "b"):
        artifacts.extend(
            verify_boundary_run(
                package,
                f"replica-{replica}-dry",
                "dry",
                "ready_absent",
                DRY_BOUNDARIES_SHA256,
            )
        )
        artifacts.extend(
            verify_boundary_run(
                package,
                f"replica-{replica}-apply",
                "apply",
                "created",
                APPLY_BOUNDARIES_SHA256,
            )
        )
        artifacts.extend(
            verify_boundary_run(
                package,
                f"replica-{replica}-readback",
                "readback",
                "verified",
                READBACK_BOUNDARIES_SHA256,
            )
        )
        prefix = f"runs/replica-{replica}-readback"
        artifacts.extend(
            [
                require_stamp(
                    package,
                    f"{prefix}/functions.tsv",
                    size=POST_FUNCTIONS_STAMP[0],
                    sha256=POST_FUNCTIONS_STAMP[1],
                ),
                require_stamp(
                    package,
                    f"{prefix}/program.tsv",
                    size=POST_PROGRAM_STAMP[0],
                    sha256=POST_PROGRAM_STAMP[1],
                ),
                require_stamp(
                    package,
                    f"{prefix}/body-ranges.tsv",
                    size=BODY_RANGES_STAMP[0],
                    sha256=BODY_RANGES_STAMP[1],
                ),
                require_stamp(
                    package,
                    f"{prefix}/direct-calls.tsv",
                    size=DIRECT_CALLS_STAMP[0],
                    sha256=DIRECT_CALLS_STAMP[1],
                ),
                require_stamp(
                    package,
                    f"{prefix}/listing.tsv",
                    size=LISTING_STAMP[0],
                    sha256=LISTING_STAMP[1],
                ),
                require_stamp(
                    package,
                    f"{prefix}/name-projection.tsv",
                    size=PROJECTION_STAMP[0],
                    sha256=PROJECTION_STAMP[1],
                ),
            ]
        )
        verify_ranges(package / f"{prefix}/body-ranges.tsv")
        verify_listing(package / f"{prefix}/listing.tsv")
        parity = read_json(package / f"{prefix}/parity.ready.json")
        require(
            parity.get("schemaVersion") == "bea-ghidra-parity-graph-receipt.v2",
            "parity receipt schema",
        )
        require(parity["bodyRanges"]["functionCount"] == POST_FUNCTIONS, "parity functions")
        require(parity["bodyRanges"]["rangeCount"] == POST_RANGES, "parity ranges")
        require(parity["bodyRanges"]["sha256"] == BODY_RANGES_STAMP[1], "parity range hash")
        require(parity["directCalls"]["sha256"] == DIRECT_CALLS_STAMP[1], "parity call hash")

    pre_fields, pre = rows_by_address(package / "inputs/pre/functions.tsv")
    post_fields, post = rows_by_address(package / "runs/replica-a-readback/functions.tsv")
    require(pre_fields == post_fields, "function inventory schema drift")
    require(len(pre) == PRE_FUNCTIONS and len(post) == POST_FUNCTIONS, "function counts")
    require(set(pre).issubset(post), "PRE function set not preserved")
    for address, row in pre.items():
        require(row == post[address], f"PRE function row drift: {address}")
    require(set(post) - set(pre) == set(TARGETS), "POST extra target set")
    for address, target in TARGETS.items():
        row = post[address]
        require(row["name"] == target["name"], f"POST name {address}")
        require(row["nameSource"] == row["sigSource"] == "DEFAULT", f"POST source {address}")
        require(row["bodyBytes"] == target["bytes"], f"POST body bytes {address}")
        require(row["bodyRanges"] == "1", f"POST body ranges {address}")
        require(row["bodyDigest"] == target["rangeSha256"], f"POST range digest {address}")
        require(row["instrCount"] == target["instructions"], f"POST instructions {address}")

    pre_metrics = metrics(package / "inputs/pre/program.tsv")
    post_metrics = metrics(package / "runs/replica-a-readback/program.tsv")
    changed = {key for key in pre_metrics if pre_metrics[key] != post_metrics[key]}
    require(changed == {"functions"}, f"unexpected program delta: {changed}")
    require(pre_metrics["functions"] == str(PRE_FUNCTIONS), "PRE program functions")
    require(post_metrics["functions"] == str(POST_FUNCTIONS), "POST program functions")
    require(post_metrics["instructions"] == str(POST_INSTRUCTIONS), "POST instructions")
    require(post_metrics["references"] == str(POST_REFERENCES), "POST references")
    return artifacts


def verify_controls(package: Path) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    control_logs: dict[str, str] = {}
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
        "containment-output": [
            "receipts must stay inside this repository's local-lab tree"
        ],
        "containment-ready": [
            "receipts must stay inside this repository's local-lab tree"
        ],
    }
    for run, markers in adverse.items():
        log = require_stamp(package, f"runs/{run}/ghidra.log")
        artifacts.append(log)
        text = (package / f"runs/{run}/ghidra.log").read_text(
            encoding="utf-8", errors="strict"
        )
        control_logs[run] = text
        require("REPORT SCRIPT ERROR:" in text, f"{run} expected script error")
        for marker in markers:
            require(marker in text, f"{run} missing marker: {marker}")
        require(not (package / f"runs/{run}/boundaries.tsv").exists(), f"{run} output")
        require(
            not (package / f"runs/{run}/boundaries.ready.json").exists(),
            f"{run} READY",
        )

    escaped_output = recorded_escape_path(
        control_logs["containment-output"], "escaped-boundaries.tsv"
    )
    escaped_ready = recorded_escape_path(
        control_logs["containment-ready"], "escaped-ready.json"
    )
    require(
        not escaped_output.exists(),
        "external containment output exists",
    )
    require(
        not escaped_ready.exists(),
        "external containment READY exists",
    )

    for run in (
        "failure-after-one-readback",
        "failure-post-inner-readback",
        "containment-output-readback",
        "containment-ready-readback",
    ):
        artifacts.extend(
            verify_boundary_run(
                package, run, "dry", "ready_absent", DRY_BOUNDARIES_SHA256
            )
        )
        artifacts.extend(
            [
                require_stamp(
                    package,
                    f"runs/{run}/functions.tsv",
                    size=PRE_FUNCTIONS_STAMP[0],
                    sha256=PRE_FUNCTIONS_STAMP[1],
                ),
                require_stamp(
                    package,
                    f"runs/{run}/program.tsv",
                    size=PRE_PROGRAM_STAMP[0],
                    sha256=PRE_PROGRAM_STAMP[1],
                ),
            ]
        )
    return artifacts


def verify_projects(
    package: Path, repo: Path, live_root: Path
) -> tuple[dict[str, Any], list[dict[str, Any]], Path]:
    tracked_pre_value = read_json(package / "tracked-pre-inspect.json")
    tracked_pre_manifest = tracked_pre_value.get("manifest", {})
    ceremony_tracked_root = Path(str(tracked_pre_manifest.get("root", "")))
    require(ceremony_tracked_root.name == "ghidra", "ceremony tracked-root leaf")
    require(
        ceremony_tracked_root.parent.name == "reverse-engineering",
        "ceremony tracked-root parent",
    )
    ceremony_repo = ceremony_tracked_root.parent.parent
    ceremony_package = ceremony_repo / f"local-lab/{PACKAGE_NAME}"
    expected_roots = {
        "live-pre-inspect": live_root,
        "live-post-inspect": live_root,
        "tracked-pre-inspect": ceremony_tracked_root,
        "tracked-post-inspect": ceremony_tracked_root,
    }
    manifests = {
        name: inspect_manifest(
            package / f"{name}.json",
            PRE_PROJECT_SHA256,
            name,
            expected_recorded_root=expected_root,
        )
        for name, expected_root in expected_roots.items()
    }
    exact = [project_file_map(value) for value in manifests.values()]
    require(all(value == exact[0] for value in exact[1:]), "PRE inspect roles differ")
    pre_map = exact[0]
    require(
        pre_map["BEA.rep/idata/00/~00000000.db/db.18617.gbf"]
        == (68_354_048, PRE_DB_SHA256),
        "PRE rolling database identity",
    )
    live = actual_project(live_root, PRE_PROJECT_SHA256, "current live")
    tracked = actual_project(repo / "reverse-engineering/ghidra", PRE_PROJECT_SHA256, "tracked")
    require(project_file_map(live) == pre_map, "live project differs from preparation PRE")
    require(project_file_map(tracked) == pre_map, "tracked project differs from preparation PRE")

    initial_copy_summaries: dict[str, Any] = {}
    for project_name in EXPECTED_PROJECTS:
        backup_path = package / f"projects/{project_name}/backup_manifest.json"
        backup = read_json(backup_path)
        require(
            backup.get("schemaVersion") == "onslaught-ghidra-project-backup.v2",
            f"{project_name} initial-copy schema",
        )
        require(backup.get("sourceStable") is True, f"{project_name} source stability")
        require(
            backup.get("copyComparison", {}).get("matches") is True,
            f"{project_name} initial copy equality",
        )
        source = backup.get("source", {})
        destination = backup.get("destination", {})
        validate_project_value(source, PRE_PROJECT_SHA256, f"{project_name} copy source")
        validate_project_value(
            destination, PRE_PROJECT_SHA256, f"{project_name} copy destination"
        )
        require(
            project_file_map(source) == pre_map == project_file_map(destination),
            f"{project_name} initial PRE copy",
        )
        initial_copy_summaries[project_name] = {
            "receipt": stamp(package, f"projects/{project_name}/backup_manifest.json"),
            "preProject": project_summary(destination),
        }

    post_summaries: dict[str, Any] = {}
    for replica in ("a", "b"):
        inspected = inspect_manifest(
            package / f"replica-{replica}-post-inspect.json",
            POST_PROJECT_SHA256[replica],
            f"replica {replica} POST",
            expected_recorded_root=ceremony_package / f"projects/replica-{replica}",
        )
        actual = actual_project(
            package / f"projects/replica-{replica}",
            POST_PROJECT_SHA256[replica],
            f"replica {replica} project",
        )
        require(project_file_map(inspected) == project_file_map(actual), f"replica {replica} inspect drift")
        post_map = project_file_map(inspected)
        removed = set(pre_map) - set(post_map)
        added = set(post_map) - set(pre_map)
        require(
            removed == {"BEA.rep/idata/00/~00000000.db/db.18616.gbf"},
            f"replica {replica} removed project files",
        )
        require(
            added == {"BEA.rep/idata/00/~00000000.db/db.18618.gbf"},
            f"replica {replica} added project files",
        )
        for path in set(pre_map) & set(post_map):
            require(pre_map[path] == post_map[path], f"replica {replica} collateral project drift: {path}")
        require(
            post_map["BEA.rep/idata/00/~00000000.db/db.18618.gbf"]
            == (68_354_048, POST_DB_SHA256[replica]),
            f"replica {replica} rolling database identity",
        )
        post_summaries[replica] = project_summary(inspected)

    control_summaries: dict[str, Any] = {}
    for name, expected_digest in CONTROL_PROJECT_SHA256.items():
        control = actual_project(
            package / f"projects/{name}", expected_digest, f"{name} project"
        )
        control_map = project_file_map(control)
        require(
            set(pre_map) - set(control_map)
            == {"BEA.rep/idata/00/~00000000.db/db.18616.gbf"},
            f"{name} removed project files",
        )
        require(
            set(control_map) - set(pre_map)
            == {"BEA.rep/idata/00/~00000000.db/db.18618.gbf"},
            f"{name} added project files",
        )
        for path in set(pre_map) & set(control_map):
            require(
                pre_map[path] == control_map[path],
                f"{name} collateral physical drift: {path}",
            )
        require(
            control_map["BEA.rep/idata/00/~00000000.db/db.18618.gbf"]
            == (68_354_048, CONTROL_DB_SHA256[name]),
            f"{name} rolling database identity",
        )
        control_summaries[name] = project_summary(control)
    return {
        "pre": project_summary(manifests["live-pre-inspect"]),
        "postReplicas": post_summaries,
        "controlProjects": control_summaries,
        "initialCopies": initial_copy_summaries,
    }, [
        require_stamp(package, f"{name}.json")
        for name in (
            "live-pre-inspect",
            "live-post-inspect",
            "tracked-pre-inspect",
            "tracked-post-inspect",
            "replica-a-post-inspect",
            "replica-b-post-inspect",
        )
    ], ceremony_repo


def verify_backup(
    package: Path, tracked_root: Path, ceremony_repo: Path
) -> list[dict[str, Any]]:
    receipt = require_stamp(
        package,
        "base-restore.ready.json",
        size=6_033,
        sha256="33691ab57df1b97f9f9b6cd2adbd7c90f49157a8a949ab2d05b2eb99c3d3ccf3",
    )
    value = read_json(package / "base-restore.ready.json")
    require(value.get("schemaVersion") == "onslaught-ghidra-project-backup.v2", "backup schema")
    require(value.get("sourceStable") is True, "backup source stability")
    require(value.get("copyComparison", {}).get("matches") is True, "backup copy equality")
    source = value.get("source", {})
    require_recorded_path(
        source.get("root"),
        ceremony_repo / "reverse-engineering/ghidra",
        "backup source",
    )
    validate_project_value(source, PRE_PROJECT_SHA256, "backup source")
    current = actual_project(tracked_root, PRE_PROJECT_SHA256, "backup current tracked")
    require(project_file_map(source) == project_file_map(current), "backup source/current drift")
    probe_root = package / "base-restore-probe-root"
    probes = [path for path in probe_root.iterdir() if path.is_dir()]
    require(len(probes) == 1 and probes[0].name.startswith("BEA-open-probe-"), "probe topology")
    recorded_probe = ceremony_repo / f"local-lab/{PACKAGE_NAME}/base-restore-probe-root/{probes[0].name}"
    require_recorded_path(value.get("probeCopy"), recorded_probe, "backup probe copy")
    require(
        value.get("probeCopyDisposition") == "RETAINED_AT_VERIFICATION",
        "backup probe disposition",
    )
    probe = actual_project(probes[0], PRE_PROJECT_SHA256, "retained open probe")
    require(project_file_map(probe) == project_file_map(source), "probe/source drift")
    readonly = value.get("readonlyOpen", {})
    require(readonly.get("opened") is True and readonly.get("exitCode") == 0, "read-only open")
    require(readonly.get("contentStable") is True, "read-only content stability")
    require(readonly.get("postOpenComparison", {}).get("matches") is True, "post-open equality")
    require(readonly.get("observedProgramMd5") == RETAIL_MD5, "open MD5")
    require(readonly.get("observedProgramSha256") == RETAIL_SHA256, "open SHA-256")
    require(readonly.get("observedFunctionCount") == 8_551, "aggregate open function count")
    argv = readonly.get("commandArgv", [])
    require(len(argv) == 14, "open argv length")
    require(Path(str(argv[0])).name.lower() == "analyzeheadless.bat", "open executable")
    require(Path(str(argv[0])).is_absolute(), "open executable path")
    require_recorded_path(argv[1], recorded_probe, "open project root")
    require(
        argv[2:8] == ["BEA", "-process", "BEA.exe", "-readOnly", "-noanalysis", "-scriptPath"],
        "open argv operation",
    )
    require_recorded_path(argv[8], ceremony_repo / "tools", "open script root")
    require(argv[9] == "-postScript", "open post-script flag")
    require("-readOnly" in argv and "-noanalysis" in argv, "unsafe open argv")
    require("-commit" not in argv, "open argv permits commit")
    require(
        argv[-4:] == ["GhidraProjectOpenProbe.java", "BEA.exe", RETAIL_MD5, RETAIL_SHA256],
        "open argv tail",
    )
    probe_log = readonly.get("probeLog", {})
    require(
        probe_log.get("path") == "base-restore.ready.open-probe.log",
        "open probe-log path",
    )
    log = require_stamp(
        package,
        str(probe_log.get("path")),
        size=int(probe_log.get("bytes", -1)),
        sha256=str(probe_log.get("sha256")),
    )
    text = (package / str(probe_log["path"])).read_text(encoding="utf-8", errors="strict")
    require("GHIDRA_PROJECT_OPEN_PROBE_OK" in text, "open sentinel")
    require("REPORT SCRIPT ERROR:" not in text, "open script error")
    return [receipt, log]


EXPECTED_RUN_FILES = {
    "containment-output": {"ghidra.log"},
    "containment-ready": {"ghidra.log"},
    "failure-after-one": {"ghidra.log"},
    "failure-post-inner": {"ghidra.log"},
    "replica-a-dry": {"boundaries.tsv", "boundaries.ready.json", "ghidra.log"},
    "replica-b-dry": {"boundaries.tsv", "boundaries.ready.json", "ghidra.log"},
    "replica-a-apply": {"boundaries.tsv", "boundaries.ready.json", "ghidra.log"},
    "replica-b-apply": {"boundaries.tsv", "boundaries.ready.json", "ghidra.log"},
}
for _replica in ("a", "b"):
    EXPECTED_RUN_FILES[f"replica-{_replica}-readback"] = {
        "body-ranges.tsv",
        "boundaries.ready.json",
        "boundaries.tsv",
        "direct-calls.tsv",
        "export.log",
        "functions.tsv",
        "ghidra.log",
        "listing.log",
        "listing.tsv",
        "name-projection.tsv",
        "parity.ready.json",
        "program.tsv",
    }
for _name in ("failure-after-one-readback", "failure-post-inner-readback"):
    EXPECTED_RUN_FILES[_name] = {
        "boundaries.ready.json",
        "boundaries.tsv",
        "functions.tsv",
        "ghidra.log",
        "inventory.log",
        "program.tsv",
    }
for _name in ("containment-output-readback", "containment-ready-readback"):
    EXPECTED_RUN_FILES[_name] = {
        "boundaries.ready.json",
        "boundaries.tsv",
        "functions.tsv",
        "ghidra.log",
        "program.tsv",
    }

EXPECTED_PROJECTS = {
    "containment-output",
    "containment-ready",
    "failure-after-one",
    "failure-post-inner",
    "replica-a",
    "replica-b",
}


def verify_topology(package: Path, receipt: Path) -> None:
    allowed_root_files = {
        "base-restore.ready.json",
        "base-restore.ready.open-probe.log",
        "live-post-inspect.json",
        "live-pre-inspect.json",
        "replica-a-post-inspect.json",
        "replica-b-post-inspect.json",
        "target-addresses.txt",
        "tracked-post-inspect.json",
        "tracked-pre-inspect.json",
    }
    if receipt.exists():
        allowed_root_files.add(receipt.name)
    root_files = {path.name for path in package.iterdir() if path.is_file()}
    root_dirs = {path.name for path in package.iterdir() if path.is_dir()}
    require(root_files == allowed_root_files, f"package root file drift: {root_files ^ allowed_root_files}")
    require(
        root_dirs == {"base-restore-probe-root", "inputs", "projects", "runs", "tools"},
        f"package root directory drift: {root_dirs}",
    )
    runs = package / "runs"
    actual_runs = {path.name for path in runs.iterdir() if path.is_dir()}
    require(actual_runs == set(EXPECTED_RUN_FILES), f"run directory drift: {actual_runs ^ set(EXPECTED_RUN_FILES)}")
    require(all(path.is_dir() and not is_reparse(path) for path in runs.iterdir()), "unsafe runs entry")
    for run, expected in EXPECTED_RUN_FILES.items():
        actual = {path.name for path in (runs / run).iterdir()}
        require(actual == expected, f"run file drift {run}: {actual ^ expected}")
        require(
            all(path.is_file() and not is_reparse(path) for path in (runs / run).iterdir()),
            f"unsafe run entry: {run}",
        )
    projects = package / "projects"
    actual_projects = {path.name for path in projects.iterdir() if path.is_dir()}
    require(actual_projects == EXPECTED_PROJECTS, f"project directory drift: {actual_projects ^ EXPECTED_PROJECTS}")
    require(all(path.is_dir() and not is_reparse(path) for path in projects.iterdir()), "unsafe projects entry")
    for project in sorted(EXPECTED_PROJECTS):
        project_root = projects / project
        project_paths = {
            row["relative_path"] for row in project_files(project_root)
        }
        all_files = {
            path.relative_to(project_root).as_posix()
            for path in project_root.rglob("*")
            if path.is_file()
        }
        require(
            all_files == project_paths | {"backup_manifest.json"},
            f"unexpected project files: {project}",
        )
    inputs = package / "inputs"
    require({path.name for path in inputs.iterdir()} == {"manifest.tsv", "pre", "scratch"}, "input topology")
    require({path.name for path in (inputs / "pre").iterdir()} == {"functions.tsv", "program.tsv"}, "PRE inputs")
    require({path.name for path in (inputs / "scratch").iterdir()} == {"scratch-authority.ready.json"}, "scratch input")
    expected_tool_names = set(EXPECTED_TOOLS) | {
        "ghidra_d3dx_gap_boundary_current_preparation_authority.py"
    }
    require({path.name for path in (package / "tools").iterdir()} == expected_tool_names, "tool topology")


def artifact_tree(root: Path, excluded: Path) -> dict[str, Any]:
    root = root.resolve(strict=True)
    excluded = excluded.resolve(strict=False)
    require(not is_reparse(root), f"package root is a reparse point: {root}")
    rows: list[tuple[str, int, str]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        require(not is_reparse(path), f"reparse point in package: {path}")
        relative = path.relative_to(root).as_posix()
        require("__pycache__" not in path.parts and path.suffix != ".pyc", f"Python cache: {relative}")
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


def verify_semantics(
    package: Path,
    repo: Path,
    live_root: Path,
    scratch_package: Path,
    receipt: Path,
) -> dict[str, Any]:
    package = package.resolve(strict=True)
    repo = repo.resolve(strict=True)
    live_root = live_root.resolve(strict=True)
    scratch_package = scratch_package.resolve(strict=True)
    require(package.name == PACKAGE_NAME, "package name drift")
    require(scratch_package.name == SCRATCH_PACKAGE_NAME, "scratch package name drift")
    require((repo / ".git").exists(), "repository root not found")
    verify_topology(package, receipt)
    project_result, project_artifacts, ceremony_repo = verify_projects(
        package, repo, live_root
    )
    artifacts = [
        *verify_manifest(package, repo),
        *verify_tools(package, repo),
        *verify_positive_replicas(package),
        *verify_controls(package),
        *project_artifacts,
        *verify_backup(
            package, repo / "reverse-engineering/ghidra", ceremony_repo
        ),
    ]
    require(len({row["path"] for row in artifacts}) == len(artifacts), "duplicate semantic artifact path")
    scratch = verify_scratch(package, scratch_package)
    return {
        "schema": SCHEMA,
        "status": "READY",
        "verdict": "PREPARATION_READY_LIVE_FORBIDDEN",
        "policy": POLICY,
        "mutationAuthorized": False,
        "program": {"name": "BEA.exe", "md5": RETAIL_MD5, "sha256": RETAIL_SHA256},
        "pre": {
            "functions": PRE_FUNCTIONS,
            "bodyRanges": PRE_RANGES,
            "ownedTextBytes": PRE_OWNED,
            "instructions": PRE_INSTRUCTIONS,
            "references": PRE_REFERENCES,
            "db": "db.18617.gbf",
            "dbSha256": PRE_DB_SHA256,
            "project": project_result["pre"],
        },
        "post": {
            "functions": POST_FUNCTIONS,
            "bodyRanges": POST_RANGES,
            "ownedTextBytes": POST_OWNED,
            "ownedTextPercent": 100.0 * POST_OWNED / TEXT_BYTES,
            "instructions": POST_INSTRUCTIONS,
            "references": POST_REFERENCES,
            "newDefaultFunctions": 2,
            "addedOwnedTextBytes": 248,
            "projectReplicas": project_result["postReplicas"],
        },
        "proof": {
            "retainedScratch": scratch,
            "positiveReplicas": 2,
            "separateReadbacks": 2,
            "unchangedPreRowsExact": PRE_FUNCTIONS,
            "forcedFailureControls": 2,
            "afterOneOuterRollbackControls": 1,
            "postInnerCompensationControls": 1,
            "containmentRefusals": 2,
            "restoredPreReadbacksExact": 4,
            "readOnlyBackupOpen": "PASS",
            "liveAndTrackedStable": True,
        },
        "blocker": "SEPARATELY_AUTHORIZED_LIVE_CEREMONY_DOES_NOT_EXIST",
        "limitations": [
            "The two prepared functions retain DEFAULT names and metadata; this preparation authorizes no D3DX-compatible names, signatures, comments, or grades.",
            "The D3DX API-compatible classifications are static compatibility claims, not original linker identities or runtime-parity claims.",
            "The two positive replicas are semantically identical but have distinct physical db.18618 hashes; each failure/compensation and containment control also has an exact, distinct rolling database hash despite its byte-exact PRE semantic readback. The aggregate authority pins all six physical project trees.",
            "The retained db.18613 scratch package is historical: its original current-root verifier intentionally refuses after the tracked project advances. This authority instead rehashes its complete sealed tree and uses the new db.18617 replicas for current-state proof.",
            "Some inner receipts retain ceremony-time absolute location fields; this authority rebinds roles to exact current roots and verifies the physical projects independently.",
            "This receipt never authorizes a live, tracked, shared, canonical, or distributable Ghidra mutation.",
        ],
        "semanticArtifacts": sorted(artifacts, key=lambda row: row["path"]),
    }


def seal(
    package: Path,
    receipt: Path,
    repo: Path,
    live_root: Path,
    scratch_package: Path,
) -> dict[str, Any]:
    require(not receipt.exists(), "refusing to overwrite authority receipt")
    require(receipt.parent.resolve(strict=True) == package.resolve(strict=True), "receipt location")
    value = verify_semantics(package, repo, live_root, scratch_package, receipt)
    value["artifactTreeExcludingReceipt"] = artifact_tree(package, receipt)
    receipt.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return value


def verify(
    package: Path,
    receipt: Path,
    repo: Path,
    live_root: Path,
    scratch_package: Path,
) -> dict[str, Any]:
    require(receipt.is_file(), "authority receipt is missing")
    require(receipt.parent.resolve(strict=True) == package.resolve(strict=True), "receipt location")
    expected = read_json(receipt)
    actual = verify_semantics(package, repo, live_root, scratch_package, receipt)
    for key, value in actual.items():
        require(expected.get(key) == value, f"authority semantic drift: {key}")
    require(
        expected.get("artifactTreeExcludingReceipt") == artifact_tree(package, receipt),
        "artifact tree drift",
    )
    return expected


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("seal", "verify"))
    parser.add_argument("--package-root", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    parser.add_argument("--repo-root", type=Path)
    parser.add_argument("--live-root", type=Path)
    parser.add_argument("--scratch-package", type=Path)
    args = parser.parse_args(argv)
    package = args.package_root.resolve(strict=True)
    repo = (
        args.repo_root.resolve(strict=True)
        if args.repo_root is not None
        else package.parent.parent.resolve(strict=True)
    )
    live_root = (
        args.live_root.resolve(strict=True)
        if args.live_root is not None
        else (Path.home() / "Ghidra/Projects").resolve(strict=True)
    )
    scratch_package = (
        args.scratch_package.resolve(strict=True)
        if args.scratch_package is not None
        else (repo / f"local-lab/{SCRATCH_PACKAGE_NAME}").resolve(strict=True)
    )
    receipt = args.receipt.resolve(strict=False)
    result = (
        seal(package, receipt, repo, live_root, scratch_package)
        if args.mode == "seal"
        else verify(package, receipt, repo, live_root, scratch_package)
    )
    print(
        "D3DX_GAP_TWO_CURRENT_PREPARATION_VERIFIED "
        f"functions={result['post']['functions']} targets=2 replicas=2 controls=4 "
        "policy=PREPARATION_ONLY mutation_authorized=false"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuthorityError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        raise SystemExit(2)
