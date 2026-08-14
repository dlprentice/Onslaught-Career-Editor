#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reproduce the current db.18614 CRT23 promotion preparation.

This tool is deliberately read-only. It verifies the corrected sealed v2
scratch campaign, the exact current live/tracked PRE, and two fresh disposable
db.18614 replicas. It creates no ceremony directory, backup, Ghidra save, or
tracked projection and grants no mutation authority.
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
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping


sys.dont_write_bytecode = True


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import ghidra_crt_p0_boundary_scratch_authority_v2 as scratch_v2  # noqa: E402
import ghidra_project_backup as project_backup  # noqa: E402


SCHEMA = "bea.ghidra.crt-p0-boundary-live-preparation.v1"
POLICY = "PREPARATION_ONLY"
BASE_COMMIT = "4d7ba6f938ea54ed1312e0f61ba208b0d285b84e"
PROGRAM_NAME = "BEA.exe"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
PROGRAM_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"

TARGETS = 23
BODY_RANGES = 24
BODY_BYTES = 1131
BODY_INSTRUCTIONS = 312
PRE_FUNCTIONS = 8280
POST_FUNCTIONS = 8303
PRE_RANGES = 8396
POST_RANGES = 8420
PRE_OWNED = 1795470
POST_OWNED = 1796601
PRE_INSTRUCTIONS = 551014
POST_INSTRUCTIONS = 551092
PRE_REFERENCES = 234478
POST_REFERENCES = 234489
TEXT_START = 0x00401000
TEXT_END = 0x005D7F9D
TEXT_BYTES = TEXT_END - TEXT_START

PRE_PROJECT = {
    "fileCount": 19,
    "totalBytes": 186977157,
    "canonicalInventorySha256":
        "cda0938c1a266fbe1751a8b0bf175b90c63b296f21fc9631b5bade1ecf93e541",
}
DB_18613 = (
    68337664,
    "615497847b0c732077ee7164b0973b9012092523e9ad99b91c21781952420ebe",
)
DB_18614 = (
    68337664,
    "d7f0011ea337f58b710415d5664e73d91ca9f1f61e20a836278d3e71b71b2865",
)
PRE_OLD_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18613.gbf"
PRE_STABLE_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18614.gbf"
POST_ROLLING_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18615.gbf"

MANIFEST_REL = (
    "reverse-engineering/binary-analysis/"
    "crt-runtime-p0-function-boundaries-2026-08-14.tsv"
)
PROJECTION_REL = (
    "reverse-engineering/binary-analysis/"
    "ghidra-function-name-table-2026-08-13.tsv"
)
MUTATOR_REL = "tools/GhidraApplyCrtP0BoundariesV3.java"
PREP_LANE_REL = "local-lab/ghidra-crt23-p0-boundary-live-prep-db18614-v3"
SCRATCH_LANE_REL = "local-lab/ghidra-crt23-p0-boundary-scratch-20260814-v2"
SCRATCH_READY_REL = f"{SCRATCH_LANE_REL}/scratch-authority-v2.ready.json"
SCRATCH_TOOL_REL = "tools/ghidra_crt_p0_boundary_scratch_authority_v2.py"
LIVE_LANE_REL = "local-lab/ghidra-crt23-p0-boundary-live-promotion-20260814-v1"
AUTHORITY_ROOT_REL = "local-lab/ghidra-crt23-p0-boundary-live-authority-20260814-v1"

PREP_TREE = {
    "fileCount": 91,
    "totalBytes": 411654188,
    "sha256": "668406c2b262c072837e985fec97c4de53f6ffeba0d5d208e98a83f23a50a966",
}
SCRATCH_TREE = {
    "fileCount": 313,
    "totalBytes": 1574566435,
    "sha256": "e8cc6ab0c70f730719e8dea9a0c798a66a397c37b9911ff4ffa4620424cb36e4",
}
SCRATCH_READY_STAMP = (
    8216,
    "e6b0dc6c99856836aeef2047eb7f1665064d21e5b5a49a166d03ebfbbbb25d23",
)

EXPECTED_REPO_INPUTS = {
    MANIFEST_REL: (
        6176,
        "c60359ecfd58e7c97c45a45e1b83d034e6cc104c222781f6f611e158b459d7df",
    ),
    MUTATOR_REL: (
        57278,
        "e92b445e34d183ae0102fe3bfa8c608cf324dad11f4ff7aedd3b04381bbc5211",
    ),
    "tools/ExportFullFunctionInventory.java": (
        23963,
        "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197",
    ),
    "tools/ExportParityLabGraph.java": (
        17663,
        "e91e26c428f593e3fd49f755fcc8551dd685ce41825fe180966be49594cbbec9",
    ),
    "tools/ghidra_inventory_diff.py": (
        9622,
        "b4956fbf9c9125cfdd7b7810cdc15f298fef8a081a880f82d6231a6dcbb25460",
    ),
    "tools/ghidra_project_backup.py": (
        27502,
        "0f426982916f0aab982efe54664342a5d34607c2f89707159ecf6c07e205ad58",
    ),
    "tools/DiagnoseAddressListingState.java": (
        3956,
        "183394907659e7810c77a9720e1899fd8a6296e6e86673495d68a2764edefe69",
    ),
    "tools/re_ghidra_name_projection.py": (
        6139,
        "d13d5f4d3b20cbd1e1baf24cd924d454c6c07b0bbf5517834c4089357f14ecdb",
    ),
    SCRATCH_TOOL_REL: (
        52378,
        "2c37c094b4b89f1c93111e00165164c0e56beee9934efb2ed37aa47d862958dd",
    ),
}

PRE_FUNCTIONS_STAMP = (
    7161943,
    "d2ff1e8e7bd91454fff9822fb7ecc8e624525fa5c6cbc9dcfe06f4e0212b750d",
)
POST_FUNCTIONS_STAMP = (
    7177147,
    "a05b55051aad3dc5ab0ea76a1afa79c7bc00ffae2e66749bdac96d3a6c46aac5",
)
PRE_PROGRAM_STAMP = (
    1267,
    "b389487a65d6271329703c9e3ec9186b7261aa871a154c31179322780e1c132e",
)
POST_PROGRAM_STAMP = (
    1267,
    "3749f822330ece0e56c9120274b76d10faea5fe10d3c130dd9f1d97e86e9c41d",
)
PRE_LISTING_STAMP = (
    961,
    "999957bb3347c795ded269fb4a9735d767bcc382c01c7af78dd307fe0adf97f4",
)
POST_LISTING_STAMP = (
    1033,
    "ffedbd49109971f452ce0518cf7defd2ac70cdc8173830b5cccc58f08853d8bf",
)
BOUNDARY_STAMPS = {
    "dry": (
        5182,
        "f2ddf6eb485eb535c7e451f87f31a49c24e9af8b54f6c479632dffa707408723",
    ),
    "apply": (
        7663,
        "e04f1632d0c06f4c589788c7800310e05156d13cc1148a297639b40c101fcd22",
    ),
    "readback": (
        7686,
        "d98a4113ee4fedea7232dfeed43a4679f3e88768bb031e28747fc614e16b87fb",
    ),
}
PRE_BODY_RANGES_STAMP = (
    1197803,
    "495f1a86490e7b2646d2a0a6cd86bf6e4cdb071d5932b7d65ded1377621582e2",
)
PRE_DIRECT_CALLS_STAMP = (
    1395238,
    "611e97141c1de4baf985aed8507c1295969d02115f1d2066c6f3af7886ee01f2",
)
PRE_GRAPH_STAMP = (
    767,
    "145d88d9c765b873afe09149d5e9753b7c2393969c0ec4589e7d429388471d3b",
)
POST_BODY_RANGES_STAMP = (
    1200879,
    "2cefa1f3d3efaaccdec5e0624c1d7bbd81d2b03747822c738f070c913ae1c3f9",
)
POST_DIRECT_CALLS_STAMP = (
    1396248,
    "d44397b910123ddabb4c598bf3be3b33b22af9df78645e258a6049f7e7878b6f",
)
POST_GRAPH_STAMP = (
    767,
    "d6d0430c20cc8b302080c1a3ee4fe1b68eb8719ab8eb2ab80aacb0b13da5b682",
)
PRE_PROJECTION_STAMP = (
    508239,
    "267210a78248f58da6bca1b4d11ee7b1812481602413e8bcac2fb4e4b4c4cb84",
)
POST_PROJECTION_STAMP = (
    509317,
    "a9725f263a11c13c7bad2ca944f06d6f7d91a5622a22febaa8c711aa5e08a713",
)

FORBIDDEN = ("0x00542720", "0x005d0ad6", "0x005d0aea")
EXCLUDED_CANARY = "0x005b8500"
THUNK_ENTRY = "0x0045ac20"
THUNK_TARGET = "0x0045ac30"
THUNK_NAME = "CFEPGoodies__BuildStaticGoodieDataTable"


class PreparationError(RuntimeError):
    pass


def require(value: bool, message: str) -> None:
    if not value:
        raise PreparationError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stamp(path: Path, label: str) -> dict[str, Any]:
    require(path.is_file(), f"missing {label}: {path}")
    return {"bytes": path.stat().st_size, "sha256": sha256_file(path)}


def verify_stamp(path: Path, expected: tuple[int, str], label: str) -> dict[str, Any]:
    measured = stamp(path, label)
    require((measured["bytes"], measured["sha256"]) == expected,
            f"{label} stamp differs")
    return measured


def load_json(path: Path, label: str) -> dict[str, Any]:
    require(path.is_file(), f"missing {label}: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise PreparationError(f"invalid {label}: {path}") from exc
    require(isinstance(value, dict), f"{label} is not an object")
    return value


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def read_commented_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(
            (line for line in stream if not line.startswith("#")), delimiter="\t"
        ))


def tree_identity(root: Path, excluded: Iterable[str] = ()) -> dict[str, Any]:
    require(root.is_dir(), f"missing evidence tree: {root}")
    excluded_set = set(excluded)
    rows: list[tuple[str, int, str]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        require(not project_backup.is_reparse(path), f"evidence reparse entry: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative in excluded_set:
            continue
        rows.append((sha256_file(path), path.stat().st_size, relative))
    raw = b"".join(
        f"{digest}\t{size}\t{relative}\n".encode("utf-8")
        for digest, size, relative in rows
    )
    return {
        "fileCount": len(rows),
        "totalBytes": sum(size for _, size, _ in rows),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def project_value(root: Path) -> dict[str, Any]:
    try:
        manifest = project_backup.build_manifest(root, "BEA")
    except project_backup.BackupError as exc:
        raise PreparationError(str(exc)) from exc
    files = [row.to_json() for row in manifest.files]
    return {
        "projectName": "BEA",
        "fileCount": len(files),
        "totalBytes": sum(int(row["size"]) for row in files),
        "structurallyComplete": manifest.structurally_complete,
        "files": files,
    }


def project_without_root(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value.get(key)
        for key in ("projectName", "fileCount", "totalBytes", "structurallyComplete", "files")
    }


def project_file_map(value: Mapping[str, Any]) -> dict[str, tuple[int, str]]:
    rows = value.get("files", [])
    require(isinstance(rows, list), "project files are not a list")
    result = {
        str(row["relative_path"]): (int(row["size"]), str(row["sha256"]))
        for row in rows
    }
    require(len(result) == len(rows), "duplicate project file row")
    return result


def project_digest(value: Mapping[str, Any]) -> str:
    rows = list(value.get("files", []))
    paths = [str(row["relative_path"]) for row in rows]
    require(paths == sorted(paths), "project rows are not ordered")
    raw = "".join(
        f"{row['sha256']}\t{row['size']}\t{row['relative_path']}\n"
        for row in rows
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def require_pre_project(value: Mapping[str, Any], label: str) -> None:
    require(value.get("projectName") == "BEA", f"{label} name")
    require(value.get("structurallyComplete") is True, f"{label} completeness")
    require(value.get("fileCount") == PRE_PROJECT["fileCount"], f"{label} files")
    require(value.get("totalBytes") == PRE_PROJECT["totalBytes"], f"{label} bytes")
    require(project_digest(value) == PRE_PROJECT["canonicalInventorySha256"],
            f"{label} inventory")
    files = project_file_map(value)
    require(files.get(PRE_OLD_DB_PATH) == DB_18613, f"{label} db.18613")
    require(files.get(PRE_STABLE_DB_PATH) == DB_18614, f"{label} db.18614")
    require(POST_ROLLING_DB_PATH not in files, f"{label} contains db.18615")


def validate_post_transition(
    before_value: Mapping[str, Any], after_value: Mapping[str, Any], label: str
) -> dict[str, Any]:
    before = project_file_map(before_value)
    after = project_file_map(after_value)
    require(after_value.get("projectName") == "BEA", f"{label} name")
    require(after_value.get("structurallyComplete") is True, f"{label} completeness")
    require(after_value.get("fileCount") == PRE_PROJECT["fileCount"],
            f"{label} file count")
    require(len(after) == PRE_PROJECT["fileCount"], f"{label} file rows")
    require(after_value.get("totalBytes") == sum(size for size, _ in after.values()),
            f"{label} byte total")
    removed = sorted(set(before) - set(after))
    added = sorted(set(after) - set(before))
    changed = sorted(path for path in set(before) & set(after) if before[path] != after[path])
    require(removed == [PRE_OLD_DB_PATH], f"{label} removed paths")
    require(added == [POST_ROLLING_DB_PATH], f"{label} added paths")
    require(changed == [], f"{label} common-file drift")
    require(after.get(PRE_STABLE_DB_PATH) == DB_18614, f"{label} stable db.18614")
    rolling = after.get(POST_ROLLING_DB_PATH)
    require(rolling is not None and rolling[0] > 0, f"{label} db.18615")
    return {
        "removed": removed,
        "added": added,
        "changedCommonFiles": changed,
        "rollingDatabaseBytes": rolling[0],
        "physicalRollingDatabaseIdentityPinned": False,
    }


@dataclass(frozen=True)
class Config:
    repo: Path
    scratch_repo: Path
    live_project: Path
    live_lane: Path
    pre_backup: Path
    post_backup: Path

    @property
    def prep_lane(self) -> Path:
        return self.repo / PREP_LANE_REL

    @property
    def tracked_project(self) -> Path:
        return self.repo / "reverse-engineering/ghidra"


def validate_repo_inputs(config: Config) -> dict[str, Any]:
    result = {}
    for relative, expected in EXPECTED_REPO_INPUTS.items():
        result[relative] = verify_stamp(config.repo / relative, expected, relative)
    verify_stamp(config.repo / PROJECTION_REL, PRE_PROJECTION_STAMP, "current projection")
    return result


def validate_scratch(config: Config) -> dict[str, Any]:
    root = config.scratch_repo / SCRATCH_LANE_REL
    ready = config.scratch_repo / SCRATCH_READY_REL
    measured_ready = verify_stamp(ready, SCRATCH_READY_STAMP, "CRT23 v2 receipt")
    measured_tree = tree_identity(root, ("scratch-authority-v2.ready.json",))
    require(measured_tree == SCRATCH_TREE, "CRT23 v2 sealed tree differs")
    tool = config.scratch_repo / SCRATCH_TOOL_REL
    completed = subprocess.run(
        [sys.executable, "-I", "-B", str(tool), "verify"],
        cwd=config.scratch_repo,
        text=True,
        capture_output=True,
        timeout=300,
        check=False,
    )
    require(completed.returncode == 0, "CRT23 v2 authority replay failed")
    require(completed.stdout.count(
        "CRT_P0_SCRATCH_AUTHORITY_V2_VERIFIED targets=23 functions=8303"
    ) == 1, "CRT23 v2 authority sentinel")
    return {"receipt": measured_ready, "tree": measured_tree, "semanticReplay": True}


def validate_boundary_receipt(
    config: Config, replica: str, mode: str
) -> dict[str, Any]:
    root = config.prep_lane / f"formal-{replica}/{mode}"
    value = load_json(root / "boundaries.ready.json", f"{replica} {mode} receipt")
    require(value.get("schemaVersion") == "bea.ghidra.crt-p0-boundaries.v3",
            f"{replica} {mode} schema")
    require(value.get("mode") == mode, f"{replica} {mode} mode")
    try:
        completed = datetime.fromisoformat(
            str(value.get("completedAtUtc")).replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise PreparationError(f"{replica} {mode} completedAtUtc") from exc
    require(completed.tzinfo is not None, f"{replica} {mode} completedAtUtc timezone")
    require(value.get("tool") == {
        "path": MUTATOR_REL,
        "bytes": EXPECTED_REPO_INPUTS[MUTATOR_REL][0],
        "sha256": EXPECTED_REPO_INPUTS[MUTATOR_REL][1],
    }, f"{replica} {mode} tool")
    require(value.get("manifest") == {
        "path": MANIFEST_REL,
        "bytes": EXPECTED_REPO_INPUTS[MANIFEST_REL][0],
        "sha256": EXPECTED_REPO_INPUTS[MANIFEST_REL][1],
    }, f"{replica} {mode} manifest")
    output = verify_stamp(
        root / "boundaries.tsv", BOUNDARY_STAMPS[mode], f"{replica} {mode} boundaries"
    )
    require(value.get("output") == {
        "path": f"{PREP_LANE_REL}/formal-{replica}/{mode}/boundaries.tsv",
        "bytes": output["bytes"],
        "sha256": output["sha256"],
    }, f"{replica} {mode} output")
    require(value.get("program") == {
        "name": PROGRAM_NAME, "md5": PROGRAM_MD5, "sha256": PROGRAM_SHA256,
    }, f"{replica} {mode} program")
    before_functions = POST_FUNCTIONS if mode == "readback" else PRE_FUNCTIONS
    after_functions = PRE_FUNCTIONS if mode == "dry" else POST_FUNCTIONS
    before_instructions = POST_INSTRUCTIONS if mode == "readback" else PRE_INSTRUCTIONS
    after_instructions = PRE_INSTRUCTIONS if mode == "dry" else POST_INSTRUCTIONS
    require(value.get("counts") == {
        "targets": TARGETS,
        "externalInstructions": BODY_INSTRUCTIONS,
        "ghidraBodyInstructions": BODY_INSTRUCTIONS,
        "functionsBefore": before_functions,
        "functionsAfter": after_functions,
        "instructionsBefore": before_instructions,
        "instructionsAfter": after_instructions,
    }, f"{replica} {mode} counts")
    require(value.get("sourceCohortSha256") == scratch_v2.SOURCE_COHORT_SHA256
            and value.get("bodyBytes") == BODY_BYTES
            and value.get("bodyRanges") == BODY_RANGES
            and value.get("preFunctionRanges") == PRE_RANGES
            and value.get("postFunctionRanges") == POST_RANGES,
            f"{replica} {mode} structural counts")
    require(tuple(value.get("protectedEntries", ())) == FORBIDDEN
            and value.get("excludedCanary") == EXCLUDED_CANARY,
            f"{replica} {mode} exclusions")
    require(value.get("explicitBodySetsAuthorized") is True
            and value.get("postCountsPinned") is True
            and value.get("namesAuthorized") is False
            and value.get("metadataAuthorized") is False
            and value.get("separateReadbackRequired") is (mode != "readback"),
            f"{replica} {mode} policy")
    manifest = read_tsv(config.repo / MANIFEST_REL)
    scratch_v2.verify_boundaries(root / "boundaries.tsv", mode, manifest)
    return stamp(root / "boundaries.ready.json", f"{replica} {mode} receipt")


def validate_log(path: Path, mode: str) -> None:
    text = path.read_text(encoding="utf-8", errors="strict")
    require(text.count(f"CRT_P0_BOUNDARIES_OK mode={mode}") == 1,
            f"{path.parent} success marker")
    for marker in ("REPORT SCRIPT ERROR", "CRT_P0_BOUNDARIES_FAIL", "Exception"):
        require(marker not in text, f"{path.parent} error marker")
    saves = text.count("Save succeeded for processed file: /BEA.exe")
    read_only = text.count("Processing read-only project file: /BEA.exe")
    writable = len(re.findall(r"Processing project file: /BEA\.exe", text))
    if mode == "apply":
        require((saves, read_only, writable) == (1, 0, 1), f"{path.parent} apply shape")
    else:
        require((saves, read_only, writable) == (0, 1, 0),
                f"{path.parent} read-only shape")


def validate_function_delta(before_path: Path, after_path: Path, manifest_path: Path) -> None:
    before_rows = read_tsv(before_path)
    after_rows = read_tsv(after_path)
    manifest = read_tsv(manifest_path)
    require(len(before_rows) == PRE_FUNCTIONS and len(after_rows) == POST_FUNCTIONS,
            "function inventory counts")
    before = {row["address"]: row for row in before_rows}
    after = {row["address"]: row for row in after_rows}
    require(len(before) == PRE_FUNCTIONS and len(after) == POST_FUNCTIONS,
            "duplicate function entry")
    for address, row in before.items():
        require(after.get(address) == row, f"PRE function row changed at {address}")
    targets = {row["entry"].lower(): row for row in manifest}
    require(set(after) - set(before) == set(targets), "created function set")
    for address, expected in targets.items():
        row = after[address]
        require(row["bodyBytes"] == expected["expectedBodyBytes"]
                and row["bodyRanges"] == str(len(expected["expectedRanges"].split(";")))
                and row["bodyDigest"] == expected["expectedRangeDigest"]
                and row["instrCount"] == expected["expectedInstructionCount"]
                and row["nameSource"] == "DEFAULT"
                and row["commentPresent"] == "false"
                and row["repeatableCommentPresent"] == "false"
                and row["tagCount"] == "0",
                f"created function fields at {address}")
        if address == THUNK_ENTRY:
            require(row["isThunk"] == "true" and row["thunkTarget"] == THUNK_TARGET
                    and row["name"] == THUNK_NAME,
                    "retained thunk identity")
        else:
            require(row["isThunk"] == "false" and row["thunkTarget"] == ""
                    and row["name"] == "FUN_" + address[2:],
                    f"default function identity at {address}")
    require(not set(FORBIDDEN + (EXCLUDED_CANARY,)).intersection(after),
            "forbidden entry created")


def validate_inventory_diff(path: Path, label: str) -> None:
    value = load_json(path, label)
    counts = value.get("counts", {})
    require((counts.get("before"), counts.get("after"), counts.get("created"),
             counts.get("destroyed"), counts.get("boundsChanged"),
             counts.get("namesChanged"), counts.get("signaturesChanged"),
             counts.get("paramCountChanged"), counts.get("thunkFlagChanged")) ==
            (PRE_FUNCTIONS, POST_FUNCTIONS, TARGETS, 0, 0, 0, 0, 0, 0),
            f"{label} counts")
    require(value.get("destroyed") == [] and len(value.get("created", [])) == TARGETS,
            f"{label} created/destroyed")
    require(all(item == [] for item in value.get("changesByField", {}).values()),
            f"{label} field drift")


def validate_listing(path: Path, post: bool) -> None:
    rows = {"0x" + row["address"].lower(): row for row in read_tsv(path)}
    require(len(rows) == 8, "listing diagnostic row count")
    for address in (EXCLUDED_CANARY, "0x005d0ad6", "0x005d0aea"):
        require(rows[address]["function_at"] == "<none>"
                and rows[address]["function_containing"] == "<none>",
                f"protected listing at {address}")
    require(rows["0x005d0a9f"]["function_at"] == "CRT__LongJmpProbe_NoOp",
            "parent function identity")
    if post:
        require(rows[THUNK_ENTRY]["instruction_at"] == "JMP 0x0045ac30"
                and rows[THUNK_ENTRY]["function_at"] == THUNK_NAME,
                "POST thunk listing")
        require(rows["0x00542710"]["function_at"] == "FUN_00542710"
                and rows["0x00542720"]["function_at"] == "<none>"
                and rows["0x00542720"]["function_containing"] == "FUN_00542710",
                "POST noncontiguous function listing")
    else:
        require(rows[THUNK_ENTRY]["function_at"] == "<none>"
                and rows["0x00542710"]["function_at"] == "<none>",
                "PRE listing")


def validate_graph(root: Path, post: bool, label: str) -> None:
    body_stamp = POST_BODY_RANGES_STAMP if post else PRE_BODY_RANGES_STAMP
    direct_stamp = POST_DIRECT_CALLS_STAMP if post else PRE_DIRECT_CALLS_STAMP
    graph_stamp = POST_GRAPH_STAMP if post else PRE_GRAPH_STAMP
    verify_stamp(root / "body-ranges.tsv", body_stamp, f"{label} body ranges")
    verify_stamp(root / "direct-calls.tsv", direct_stamp, f"{label} direct calls")
    verify_stamp(root / "parity-graph.ready.json", graph_stamp, f"{label} graph receipt")
    value = load_json(root / "parity-graph.ready.json", f"{label} graph receipt")
    expected = (
        (POST_FUNCTIONS, POST_RANGES, POST_OWNED, 14582, 27211)
        if post else (PRE_FUNCTIONS, PRE_RANGES, PRE_OWNED, 14568, 27196)
    )
    rows = read_commented_tsv(root / "body-ranges.tsv")
    require(len(rows) == expected[1], f"{label} body-range rows")
    require(len({row["functionAddress"] for row in rows}) == expected[0],
            f"{label} body-range function count")
    require(sum(int(row["rangeBytes"]) for row in rows) == expected[2],
            f"{label} owned-byte total")
    require((value.get("bodyRanges", {}).get("functionCount"),
             value.get("bodyRanges", {}).get("rangeCount"),
             value.get("directCalls", {}).get("directEdgeCount"),
             value.get("directCalls", {}).get("directCallSiteCount")) ==
            (expected[0], expected[1], expected[3], expected[4]),
            f"{label} graph counts")


def validate_preparation(config: Config) -> dict[str, Any]:
    measured_tree = tree_identity(config.prep_lane)
    require(measured_tree == PREP_TREE, "current preparation tree differs")
    verify_stamp(config.prep_lane / "static/manifest.tsv",
                 EXPECTED_REPO_INPUTS[MANIFEST_REL], "frozen manifest")
    verify_stamp(config.prep_lane / "static/GhidraApplyCrtP0BoundariesV3.java",
                 EXPECTED_REPO_INPUTS[MUTATOR_REL], "frozen V3 mutator")
    require((config.prep_lane / "static/GhidraApplyCrtP0BoundariesV3.java").read_bytes()
            == (config.repo / MUTATOR_REL).read_bytes(), "tracked/frozen V3 mutator differs")
    verify_stamp(config.prep_lane / "static/diagnostic-addresses.txt",
                 (88, "9da8bd194362ee3b0306d1de3fc68ef44c219e4184338a48783a7dfca3bf1505"),
                 "diagnostic addresses")
    validate_graph(config.prep_lane / "static/pre-accounting", False, "PRE")

    deterministic = (
        "dry/boundaries.tsv", "dry/functions.tsv", "dry/program.tsv",
        "dry/listing-state.tsv", "apply/boundaries.tsv",
        "readback/boundaries.tsv", "readback/functions.tsv",
        "readback/program.tsv", "readback/listing-state.tsv",
        "accounting/body-ranges.tsv", "accounting/direct-calls.tsv",
        "accounting/parity-graph.ready.json", "projection.tsv",
    )
    raw: dict[str, dict[str, bytes]] = {}
    transitions = {}
    for replica in ("a", "b"):
        root = config.prep_lane / f"formal-{replica}"
        project = config.prep_lane / f"formal-{replica}-project"
        backup = load_json(project / "backup_manifest.json", f"{replica} source copy")
        require(backup.get("sourceStable") is True
                and backup.get("copyComparison", {}).get("matches") is True,
                f"{replica} source-copy identity")
        source = backup.get("source", {})
        destination = backup.get("destination", {})
        require_pre_project(source, f"{replica} source PRE")
        require_pre_project(destination, f"{replica} destination PRE")
        for mode in ("dry", "apply", "readback"):
            validate_boundary_receipt(config, replica, mode)
            validate_log(root / mode / "ghidra.log", mode)
        verify_stamp(root / "dry/functions.tsv", PRE_FUNCTIONS_STAMP,
                     f"{replica} PRE functions")
        verify_stamp(root / "dry/program.tsv", PRE_PROGRAM_STAMP,
                     f"{replica} PRE program")
        verify_stamp(root / "dry/listing-state.tsv", PRE_LISTING_STAMP,
                     f"{replica} PRE listing")
        verify_stamp(root / "readback/functions.tsv", POST_FUNCTIONS_STAMP,
                     f"{replica} POST functions")
        verify_stamp(root / "readback/program.tsv", POST_PROGRAM_STAMP,
                     f"{replica} POST program")
        verify_stamp(root / "readback/listing-state.tsv", POST_LISTING_STAMP,
                     f"{replica} POST listing")
        validate_function_delta(
            root / "dry/functions.tsv", root / "readback/functions.tsv",
            config.repo / MANIFEST_REL,
        )
        validate_inventory_diff(root / "inventory-diff.json", f"{replica} diff")
        validate_listing(root / "dry/listing-state.tsv", False)
        validate_listing(root / "readback/listing-state.tsv", True)
        validate_graph(root / "accounting", True, f"{replica} POST")
        verify_stamp(root / "projection.tsv", POST_PROJECTION_STAMP,
                     f"{replica} projection")
        require(len(read_commented_tsv(root / "projection.tsv")) == POST_FUNCTIONS,
                f"{replica} projection row count")
        post_inspect = load_json(
            config.prep_lane / f"formal-{replica}-post-inspect.json",
            f"{replica} POST inspect",
        ).get("manifest", {})
        transitions[replica] = validate_post_transition(
            destination, post_inspect, f"{replica} POST transition"
        )
        actual_post = project_value(project)
        require(project_without_root(actual_post) == project_without_root(post_inspect),
                f"{replica} physical POST changed after inspection")
        raw[replica] = {relative: (root / relative).read_bytes()
                        for relative in deterministic}
    for relative in deterministic:
        require(raw["a"][relative] == raw["b"][relative],
                f"replica semantic output differs: {relative}")
    return {
        "tree": measured_tree,
        "replicas": 2,
        "semanticOutputsByteIdentical": True,
        "preFunctions": PRE_FUNCTIONS,
        "postFunctions": POST_FUNCTIONS,
        "postRanges": POST_RANGES,
        "postOwnedBytes": POST_OWNED,
        "transitions": transitions,
    }


def preflight(config: Config) -> dict[str, Any]:
    repo_inputs = validate_repo_inputs(config)
    scratch = validate_scratch(config)
    preparation = validate_preparation(config)
    live = project_value(config.live_project)
    tracked = project_value(config.tracked_project)
    require_pre_project(live, "live PRE")
    require_pre_project(tracked, "tracked PRE")
    require(project_without_root(live) == project_without_root(tracked),
            "live/tracked PRE differ")
    future = (
        config.live_lane,
        config.pre_backup,
        config.post_backup,
        config.repo / AUTHORITY_ROOT_REL,
    )
    for path in future:
        require(not path.exists(), f"future ceremony path already exists: {path}")
    return {
        "schemaVersion": SCHEMA,
        "policy": POLICY,
        "baseCommit": BASE_COMMIT,
        "program": {"name": PROGRAM_NAME, "md5": PROGRAM_MD5,
                    "sha256": PROGRAM_SHA256},
        "repoInputs": repo_inputs,
        "scratch": scratch,
        "preparation": preparation,
        "preProject": PRE_PROJECT,
        "prospectivePost": {
            "functions": POST_FUNCTIONS,
            "ranges": POST_RANGES,
            "ownedBytes": POST_OWNED,
            "unownedBytes": TEXT_BYTES - POST_OWNED,
            "ownershipPercent": round(100.0 * POST_OWNED / TEXT_BYTES, 9),
            "instructions": POST_INSTRUCTIONS,
            "references": POST_REFERENCES,
            "projection": {"bytes": POST_PROJECTION_STAMP[0],
                           "sha256": POST_PROJECTION_STAMP[1]},
        },
        "liveEqualsTracked": True,
        "mutationAuthorized": False,
        "blocker": "future_ceremony_artifacts_absent",
    }


def parse_config(args: argparse.Namespace) -> Config:
    return Config(
        repo=Path(args.repo).resolve(),
        scratch_repo=Path(args.scratch_repo).resolve(),
        live_project=Path(args.live_project).resolve(),
        live_lane=Path(args.live_lane).resolve(strict=False),
        pre_backup=Path(args.pre_backup).resolve(strict=False),
        post_backup=Path(args.post_backup).resolve(strict=False),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("preflight",))
    parser.add_argument("--repo", required=True)
    parser.add_argument("--scratch-repo", required=True)
    parser.add_argument("--live-project", required=True)
    parser.add_argument("--live-lane", required=True)
    parser.add_argument("--pre-backup", required=True)
    parser.add_argument("--post-backup", required=True)
    args = parser.parse_args()
    result = preflight(parse_config(args))
    print(
        "CRT_P0_BOUNDARY_LIVE_PREPARATION_READY "
        f"pre_project_sha256={PRE_PROJECT['canonicalInventorySha256']} "
        f"scratch_receipt_sha256={SCRATCH_READY_STAMP[1]} "
        "live_equals_tracked=true db=db.18614.gbf "
        "policy=PREPARATION_ONLY mutation_authorized=false "
        f"blocker={result['blocker']}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (PreparationError, OSError, subprocess.SubprocessError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        raise SystemExit(1)
