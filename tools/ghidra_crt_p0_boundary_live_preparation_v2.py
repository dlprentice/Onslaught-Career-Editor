#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reproduce the current db.18615 CRT23 live-promotion preparation.

This authority is deliberately read-only. It verifies the corrected sealed v2
scratch campaign, the exact current live/tracked PRE, and two independently
saved disposable db.18616 prospective-POST replicas. It creates no ceremony
directory, backup, Ghidra save, tracked refresh, or mutation authority.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
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


SCHEMA = "bea.ghidra.crt-p0-boundary-live-preparation.v2"
POLICY = "PREPARATION_ONLY"
BASE_COMMIT = "c8678d80e4d0373d25e1452b8fcaf6af44761387"
PROGRAM_NAME = "BEA.exe"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
PROGRAM_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"

TARGETS = 23
BODY_RANGES = 24
BODY_BYTES = 1131
BODY_INSTRUCTIONS = 312
PRE_FUNCTIONS = 8304
POST_FUNCTIONS = 8327
PRE_RANGES = 8434
POST_RANGES = 8458
PRE_OWNED = 1810287
POST_OWNED = 1811418
PRE_INSTRUCTIONS = 551055
POST_INSTRUCTIONS = 551133
PRE_REFERENCES = 234467
POST_REFERENCES = 234478
TEXT_START = 0x00401000
TEXT_END = 0x005D7F9D
TEXT_BYTES = TEXT_END - TEXT_START

PRE_PROJECT = {
    "fileCount": 19,
    "totalBytes": 186993541,
    "canonicalInventorySha256":
        "3cd459d5461919934199e3346f6a92ce14946f42af400488ccde733173a40627",
}
POST_PROJECT_BYTES = 187009925
DB_18614 = (
    68337664,
    "d7f0011ea337f58b710415d5664e73d91ca9f1f61e20a836278d3e71b71b2865",
)
DB_18615 = (
    68354048,
    "6c2fc2f12394cf7b63f4f335173ba0a19b52b92c50dc4d2da987170501bc9681",
)
POST_DB_18616 = {
    "a": (68354048, "e309c00f67efb4f3ac93c72cad83e064efa9c7930b15c8b77bba268a407e2c36"),
    "b": (68354048, "6f806cce1543d0971d66b2ef3c9c2b5c3fe6de439556223b1a579b6ed7428eed"),
}
POST_DB_REPLICA_DIFFERING_BYTES = 53
PRE_OLD_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18614.gbf"
PRE_STABLE_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18615.gbf"
POST_ROLLING_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18616.gbf"

MANIFEST_REL = (
    "reverse-engineering/binary-analysis/"
    "crt-runtime-p0-function-boundaries-2026-08-14.tsv"
)
PROJECTION_REL = (
    "reverse-engineering/binary-analysis/"
    "ghidra-function-name-table-2026-08-13.tsv"
)
MUTATOR_REL = "tools/GhidraApplyCrtP0BoundariesV4.java"
PREP_LANE_REL = "local-lab/ghidra-crt23-p0-boundary-live-prep-db18615-v4"
SCRATCH_LANE_REL = "local-lab/ghidra-crt23-p0-boundary-scratch-20260814-v2"
SCRATCH_READY_REL = f"{SCRATCH_LANE_REL}/scratch-authority-v2.ready.json"
SCRATCH_TOOL_REL = "tools/ghidra_crt_p0_boundary_scratch_authority_v2.py"
LIVE_LANE_REL = (
    "local-lab/ghidra-crt23-p0-boundary-live-promotion-db18615-20260814-v2"
)
AUTHORITY_ROOT_REL = (
    "local-lab/ghidra-crt23-p0-boundary-live-authority-db18615-20260814-v2"
)

PREP_TREE = {
    "fileCount": 102,
    "totalBytes": 404643691,
    "sha256": "d48aa7bf784a7a82f867adc259868eff16f60a4ae9d103ee44c8f57361ed41b0",
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
        "ac003bde10aea75cdf6849385017e15ef80c87e199ebeedf703108fb64334cc8",
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

PRE_PROJECTION_STAMP = (
    509334,
    "5dd0d1145c2cf25004bd50208c624d9bf4f9c2fe0e4d307ac6c7ca88e8a5dfbc",
)
PRE_FUNCTIONS_STAMP = (
    7177776,
    "bceedfa2eec573ee95e42a703d6f3a552c4718115fa540f3eaca492322f9a173",
)
POST_FUNCTIONS_STAMP = (
    7192980,
    "8640c35a820b3c5e415b947fa8a13eeb5c7c535868780dc2fe511d020a54c40e",
)
PRE_PROGRAM_STAMP = (
    1267,
    "bcb364f619559879e815f8d95f5551ba10d9be0467023bd006ee1246b0f9b40f",
)
POST_PROGRAM_STAMP = (
    1267,
    "185dbd4a9939edacf7302c00c7c48351ad23ad51be14bd5d431130d13848170a",
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
    "dry": (5182, "f2ddf6eb485eb535c7e451f87f31a49c24e9af8b54f6c479632dffa707408723"),
    "apply": (7663, "e04f1632d0c06f4c589788c7800310e05156d13cc1148a297639b40c101fcd22"),
    "readback": (7686, "d98a4113ee4fedea7232dfeed43a4679f3e88768bb031e28747fc614e16b87fb"),
}
PRE_BODY_RANGES_STAMP = (
    1202661,
    "8e3640bfb280b6ce93a62db885183aa2239d1e74841685316b0117518eb63aaa",
)
PRE_DIRECT_CALLS_STAMP = (
    1396670,
    "e2c3e2d0ace69d13b4bffa4d12690e60f6cf0cc50d2ff846cdc37ace680a756f",
)
PRE_GRAPH_STAMP = (
    767,
    "bc3047480f43cbd31b762854eb9a0fc0e2b79564786a935c0c874fc589fb3d04",
)
POST_BODY_RANGES_STAMP = (
    1205737,
    "46138dc9b81ce2d0f835994f38581ba07564ddf17a7774ddbedfdb2e3d33e335",
)
POST_DIRECT_CALLS_STAMP = (
    1397680,
    "159f7c89aae54df927186d71263941b5f0857debe09556097820f098da8fa9d8",
)
POST_GRAPH_STAMP = (
    767,
    "485f9b748e267533dce022d3ceb54f847e64eb0035d3a1b7faa1459972accf0a",
)
POST_PROJECTION_STAMP = (
    510353,
    "0b9f08cbd8849d22068d5ad6261a45b745bf80581744f4814a201b8fc4647804",
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
    require(files.get(PRE_OLD_DB_PATH) == DB_18614, f"{label} db.18614")
    require(files.get(PRE_STABLE_DB_PATH) == DB_18615, f"{label} db.18615")
    require(POST_ROLLING_DB_PATH not in files, f"{label} contains db.18616")


def validate_post_transition(
    before_value: Mapping[str, Any], after_value: Mapping[str, Any], replica: str
) -> dict[str, Any]:
    before = project_file_map(before_value)
    after = project_file_map(after_value)
    label = f"replica {replica} POST"
    require(after_value.get("projectName") == "BEA", f"{label} name")
    require(after_value.get("structurallyComplete") is True, f"{label} completeness")
    require(after_value.get("fileCount") == PRE_PROJECT["fileCount"], f"{label} files")
    require(after_value.get("totalBytes") == POST_PROJECT_BYTES, f"{label} bytes")
    require(after_value.get("totalBytes") == sum(size for size, _ in after.values()),
            f"{label} byte total")
    removed = sorted(set(before) - set(after))
    added = sorted(set(after) - set(before))
    changed = sorted(path for path in set(before) & set(after) if before[path] != after[path])
    require(removed == [PRE_OLD_DB_PATH], f"{label} removed paths")
    require(added == [POST_ROLLING_DB_PATH], f"{label} added paths")
    require(changed == [], f"{label} common-file drift")
    require(after.get(PRE_STABLE_DB_PATH) == DB_18615, f"{label} stable db.18615")
    require(after.get(POST_ROLLING_DB_PATH) == POST_DB_18616[replica],
            f"{label} db.18616")
    return {"removed": removed, "added": added, "changedCommonFiles": changed,
            "rollingDatabase": {"bytes": POST_DB_18616[replica][0],
                                "sha256": POST_DB_18616[replica][1]}}


def differing_byte_count(first: Path, second: Path) -> int:
    require(first.stat().st_size == second.stat().st_size, "rolling DB sizes differ")
    count = 0
    with first.open("rb") as left, second.open("rb") as right:
        while True:
            a = left.read(1024 * 1024)
            b = right.read(1024 * 1024)
            require(len(a) == len(b), "rolling DB read length differs")
            if not a:
                break
            count += sum(x != y for x, y in zip(a, b))
    return count


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
        cwd=config.scratch_repo, text=True, capture_output=True, timeout=300, check=False,
    )
    require(completed.returncode == 0, "CRT23 v2 authority replay failed")
    require(completed.stdout.count(
        "CRT_P0_SCRATCH_AUTHORITY_V2_VERIFIED targets=23 functions=8303"
    ) == 1, "CRT23 v2 authority sentinel")
    return {"receipt": measured_ready, "tree": measured_tree, "semanticReplay": True}


def validate_boundary_receipt(config: Config, replica: str, mode: str) -> None:
    root = config.prep_lane / f"formal-{replica}/{mode}"
    value = load_json(root / "boundaries.ready.json", f"{replica} {mode} receipt")
    require(value.get("schemaVersion") == "bea.ghidra.crt-p0-boundaries.v4",
            f"{replica} {mode} schema")
    require(value.get("mode") == mode, f"{replica} {mode} mode")
    try:
        completed = datetime.fromisoformat(str(value.get("completedAtUtc")).replace("Z", "+00:00"))
    except ValueError as exc:
        raise PreparationError(f"{replica} {mode} completedAtUtc") from exc
    require(completed.tzinfo is not None, f"{replica} {mode} completedAtUtc timezone")
    require(value.get("tool") == {"path": MUTATOR_REL,
                                  "bytes": EXPECTED_REPO_INPUTS[MUTATOR_REL][0],
                                  "sha256": EXPECTED_REPO_INPUTS[MUTATOR_REL][1]},
            f"{replica} {mode} tool")
    require(value.get("manifest") == {"path": MANIFEST_REL,
                                      "bytes": EXPECTED_REPO_INPUTS[MANIFEST_REL][0],
                                      "sha256": EXPECTED_REPO_INPUTS[MANIFEST_REL][1]},
            f"{replica} {mode} manifest")
    output = verify_stamp(root / "boundaries.tsv", BOUNDARY_STAMPS[mode],
                          f"{replica} {mode} boundaries")
    require(value.get("output") == {
        "path": f"{PREP_LANE_REL}/formal-{replica}/{mode}/boundaries.tsv",
        "bytes": output["bytes"], "sha256": output["sha256"],
    }, f"{replica} {mode} output")
    require(value.get("program") == {"name": PROGRAM_NAME, "md5": PROGRAM_MD5,
                                      "sha256": PROGRAM_SHA256},
            f"{replica} {mode} program")
    before_functions = POST_FUNCTIONS if mode == "readback" else PRE_FUNCTIONS
    after_functions = PRE_FUNCTIONS if mode == "dry" else POST_FUNCTIONS
    before_instructions = POST_INSTRUCTIONS if mode == "readback" else PRE_INSTRUCTIONS
    after_instructions = PRE_INSTRUCTIONS if mode == "dry" else POST_INSTRUCTIONS
    require(value.get("counts") == {
        "targets": TARGETS, "externalInstructions": BODY_INSTRUCTIONS,
        "ghidraBodyInstructions": BODY_INSTRUCTIONS,
        "functionsBefore": before_functions, "functionsAfter": after_functions,
        "instructionsBefore": before_instructions, "instructionsAfter": after_instructions,
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
    scratch_v2.verify_boundaries(root / "boundaries.tsv", mode,
                                 read_tsv(config.repo / MANIFEST_REL))


def validate_boundary_log(path: Path, mode: str) -> None:
    text = path.read_text(encoding="utf-8", errors="strict")
    require(text.count(f"CRT_P0_BOUNDARIES_OK mode={mode}") == 1,
            f"{path.parent} success marker")
    for marker in ("REPORT SCRIPT ERROR", "CRT_P0_BOUNDARIES_FAIL"):
        require(marker not in text, f"{path.parent} error marker")
    saves = text.count("Save succeeded for processed file: /BEA.exe")
    read_only = text.count("Processing read-only project file: /BEA.exe")
    writable = len(re.findall(r"Processing project file: /BEA\.exe", text))
    expected = (1, 0, 1) if mode == "apply" else (0, 1, 0)
    require((saves, read_only, writable) == expected, f"{path.parent} process shape")


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
                    and row["name"] == THUNK_NAME, "retained thunk identity")
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
                and rows["0x00542710"]["function_at"] == "<none>", "PRE listing")


def validate_graph(root: Path, post: bool, label: str) -> None:
    body_stamp = POST_BODY_RANGES_STAMP if post else PRE_BODY_RANGES_STAMP
    direct_stamp = POST_DIRECT_CALLS_STAMP if post else PRE_DIRECT_CALLS_STAMP
    graph_stamp = POST_GRAPH_STAMP if post else PRE_GRAPH_STAMP
    verify_stamp(root / "body-ranges.tsv", body_stamp, f"{label} body ranges")
    verify_stamp(root / "direct-calls.tsv", direct_stamp, f"{label} direct calls")
    verify_stamp(root / "parity-graph.ready.json", graph_stamp, f"{label} graph receipt")
    value = load_json(root / "parity-graph.ready.json", f"{label} graph receipt")
    expected = ((POST_FUNCTIONS, POST_RANGES, POST_OWNED, 14598, 27244)
                if post else (PRE_FUNCTIONS, PRE_RANGES, PRE_OWNED, 14584, 27229))
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


def program_metrics(path: Path) -> dict[str, str]:
    rows = read_tsv(path)
    return {row["metric"]: row["value"] for row in rows if not row["metric"].startswith("block:")}


def validate_program_delta(before_path: Path, after_path: Path) -> None:
    before = program_metrics(before_path)
    after = program_metrics(after_path)
    expected_changes = {
        "functions": (str(PRE_FUNCTIONS), str(POST_FUNCTIONS)),
        "instructions": (str(PRE_INSTRUCTIONS), str(POST_INSTRUCTIONS)),
        "instructionLayoutSha256": (
            "53a1c7f666ed151a737c11cf3ad707d5b8683894a160b86cb20868455adfa28f",
            "cd3c05f20da89e035160dee4e2d0aea8c21cf7c3dcbb75ba5315d908fd5d647a",
        ),
        "undefinedData": ("3908270", "3907928"),
        "symbolsDefaultOther": ("61682", "61702"),
        "references": (str(PRE_REFERENCES), str(POST_REFERENCES)),
        "referencesSha256": (
            "7b683235141a3ca372c14dc4cd72f91346eb2a9e02b34fbb1a483f4539c48099",
            "22a0bf8c664af22d5f3c49524bea4029bb706175089f1fbe76c7f24bcbc2e383",
        ),
    }
    changed = {key: (before.get(key), after.get(key))
               for key in set(before) | set(after) if before.get(key) != after.get(key)}
    require(changed == expected_changes, "program collateral delta")


def validate_preparation(config: Config) -> dict[str, Any]:
    measured_tree = tree_identity(config.prep_lane)
    require(measured_tree == PREP_TREE, "current preparation tree differs")
    verify_stamp(config.prep_lane / "static/manifest.tsv",
                 EXPECTED_REPO_INPUTS[MANIFEST_REL], "frozen manifest")
    verify_stamp(config.prep_lane / "static/GhidraApplyCrtP0BoundariesV4.java",
                 EXPECTED_REPO_INPUTS[MUTATOR_REL], "frozen V4 mutator")
    require((config.prep_lane / "static/GhidraApplyCrtP0BoundariesV4.java").read_bytes()
            == (config.repo / MUTATOR_REL).read_bytes(), "tracked/frozen V4 mutator differs")
    verify_stamp(config.prep_lane / "static/diagnostic-addresses.txt",
                 (88, "9da8bd194362ee3b0306d1de3fc68ef44c219e4184338a48783a7dfca3bf1505"),
                 "diagnostic addresses")

    pre_live = load_json(config.prep_lane / "pre-live-inspect.json", "saved live PRE").get("manifest", {})
    pre_tracked = load_json(config.prep_lane / "pre-tracked-inspect.json", "saved tracked PRE").get("manifest", {})
    require_pre_project(pre_live, "saved live PRE")
    require_pre_project(pre_tracked, "saved tracked PRE")
    require(project_without_root(pre_live) == project_without_root(pre_tracked),
            "saved live/tracked PRE differ")

    pre_root = config.prep_lane / "static/pre"
    verify_stamp(pre_root / "functions.tsv", PRE_FUNCTIONS_STAMP, "PRE functions")
    verify_stamp(pre_root / "program.tsv", PRE_PROGRAM_STAMP, "PRE program")
    verify_stamp(pre_root / "listing-state.tsv", PRE_LISTING_STAMP, "PRE listing")
    validate_listing(pre_root / "listing-state.tsv", False)
    validate_graph(pre_root, False, "PRE")

    deterministic = (
        "dry/boundaries.tsv", "apply/boundaries.tsv", "readback/boundaries.tsv",
        "post-exports/functions.tsv", "post-exports/program.tsv",
        "post-exports/listing-state.tsv", "post-exports/body-ranges.tsv",
        "post-exports/direct-calls.tsv", "post-exports/parity-graph.ready.json",
        "post-exports/projection.tsv",
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
            validate_boundary_log(root / mode / "ghidra.log", mode)
        exports = root / "post-exports"
        verify_stamp(exports / "functions.tsv", POST_FUNCTIONS_STAMP,
                     f"{replica} POST functions")
        verify_stamp(exports / "program.tsv", POST_PROGRAM_STAMP,
                     f"{replica} POST program")
        verify_stamp(exports / "listing-state.tsv", POST_LISTING_STAMP,
                     f"{replica} POST listing")
        verify_stamp(exports / "projection.tsv", POST_PROJECTION_STAMP,
                     f"{replica} projection")
        validate_function_delta(pre_root / "functions.tsv", exports / "functions.tsv",
                                config.repo / MANIFEST_REL)
        validate_inventory_diff(root / "inventory-diff.json", f"{replica} diff")
        validate_listing(exports / "listing-state.tsv", True)
        validate_graph(exports, True, f"{replica} POST")
        validate_program_delta(pre_root / "program.tsv", exports / "program.tsv")
        require(len(read_commented_tsv(exports / "projection.tsv")) == POST_FUNCTIONS,
                f"{replica} projection rows")
        post_inspect = load_json(root / "post-project-inspect.json",
                                 f"{replica} POST inspect").get("manifest", {})
        transitions[replica] = validate_post_transition(destination, post_inspect, replica)
        actual_post = project_value(project)
        require(project_without_root(actual_post) == project_without_root(post_inspect),
                f"{replica} physical POST changed after inspection")
        raw[replica] = {relative: (root / relative).read_bytes() for relative in deterministic}
    for relative in deterministic:
        require(raw["a"][relative] == raw["b"][relative],
                f"replica semantic output differs: {relative}")

    first_db = config.prep_lane / "formal-a-project" / POST_ROLLING_DB_PATH
    second_db = config.prep_lane / "formal-b-project" / POST_ROLLING_DB_PATH
    differing = differing_byte_count(first_db, second_db)
    require(differing == POST_DB_REPLICA_DIFFERING_BYTES,
            "unexpected physical rolling-database replica delta")
    return {
        "tree": measured_tree, "replicas": 2,
        "semanticOutputsByteIdentical": True,
        "physicalRollingDatabaseDifferingBytes": differing,
        "preFunctions": PRE_FUNCTIONS, "postFunctions": POST_FUNCTIONS,
        "postRanges": POST_RANGES, "postOwnedBytes": POST_OWNED,
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
    for path in (config.live_lane, config.pre_backup, config.post_backup,
                 config.repo / AUTHORITY_ROOT_REL):
        require(not path.exists(), f"future ceremony path already exists: {path}")
    return {
        "schemaVersion": SCHEMA, "policy": POLICY, "baseCommit": BASE_COMMIT,
        "program": {"name": PROGRAM_NAME, "md5": PROGRAM_MD5, "sha256": PROGRAM_SHA256},
        "repoInputs": repo_inputs, "scratch": scratch, "preparation": preparation,
        "preProject": PRE_PROJECT,
        "prospectivePost": {
            "functions": POST_FUNCTIONS, "ranges": POST_RANGES,
            "ownedBytes": POST_OWNED, "unownedBytes": TEXT_BYTES - POST_OWNED,
            "ownershipPercent": round(100.0 * POST_OWNED / TEXT_BYTES, 9),
            "instructions": POST_INSTRUCTIONS, "references": POST_REFERENCES,
            "projection": {"bytes": POST_PROJECTION_STAMP[0],
                           "sha256": POST_PROJECTION_STAMP[1]},
        },
        "liveEqualsTracked": True, "mutationAuthorized": False,
        "blocker": "future_ceremony_artifacts_absent",
    }


def parse_config(args: argparse.Namespace) -> Config:
    return Config(
        repo=Path(args.repo).resolve(), scratch_repo=Path(args.scratch_repo).resolve(),
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
    result = preflight(parse_config(parser.parse_args()))
    print(
        "CRT_P0_BOUNDARY_LIVE_PREPARATION_V2_READY "
        f"pre_project_sha256={PRE_PROJECT['canonicalInventorySha256']} "
        f"scratch_receipt_sha256={SCRATCH_READY_STAMP[1]} "
        "live_equals_tracked=true db=db.18615.gbf "
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
