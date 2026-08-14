#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Prepare, reproduce, and seal the five-range live-promotion ceremony.

The authority itself never launches Ghidra and never mutates the live or
tracked project. ``preflight`` hashes the exact PRE state and reproduces the
retained scratch package. ``check-live`` proves a separately authorized live
save while tracked must remain PRE. ``seal`` has one write: create-new
publication of a portable receipt after a separately authorized tracked
refresh, read-only restore, projection, and body-accounting export. ``verify``
reproduces that saved receipt.
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
from typing import Any, Iterable, Mapping, Sequence


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import ghidra_function_fragment_range_scratch_authority as scratch  # noqa: E402
import ghidra_project_backup as project_backup  # noqa: E402
import re_ghidra_name_projection as name_projection  # noqa: E402


SCHEMA = "bea.ghidra.function-fragment-range-live-authority.v1"
POLICY = "PREPARATION_ONLY"
BASE_COMMIT = "add5571c0779287f2e575c371e477cd33872662c"
PROGRAM_NAME = "BEA.exe"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
PROGRAM_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
TOTAL_FUNCTIONS = 8504

TARGETS = 5
REPAIR_BYTES = 1258
PRE_FUNCTIONS = POST_FUNCTIONS = 8280
PRE_RANGES = 8400
POST_RANGES = 8396
PRE_OWNED = 1794212
POST_OWNED = 1795470
PRE_INSTRUCTIONS = 550991
POST_INSTRUCTIONS = 551014
PRE_REFERENCES = 234495
POST_REFERENCES = 234478
TEXT_START = 0x00401000
TEXT_END = 0x005D7F9D
TEXT_BYTES = TEXT_END - TEXT_START

PRE_PROJECT = {
    "fileCount": 19,
    "totalBytes": 186960773,
    "canonicalInventorySha256":
        "ae422079966978ec2f8f5b951b0ef5812b1074bd708ab8d782179f51c90efcf2",
}
DB_18612 = (
    68321280,
    "424775377ea0f40d9e429c9219b9310d427760acc40548dbc588ca285f932f7b",
)
DB_18613 = (
    68337664,
    "615497847b0c732077ee7164b0973b9012092523e9ad99b91c21781952420ebe",
)
PRE_OLD_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18612.gbf"
PRE_STABLE_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18613.gbf"
POST_ROLLING_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18614.gbf"

MANIFEST_REL = (
    "reverse-engineering/binary-analysis/"
    "pc-function-body-fragment-repairs-2026-08-14.tsv"
)
PROJECTION_REL = (
    "reverse-engineering/binary-analysis/"
    "ghidra-function-name-table-2026-08-13.tsv"
)
LIVE_LANE_REL = (
    "local-lab/ghidra-function-fragment5-range-live-promotion-20260814-v1"
)
AUTHORITY_RECEIPT_REL = (
    "local-lab/ghidra-function-fragment5-range-live-authority-20260814-v1/"
    "live-promotion.ready.json"
)
SCRATCH_LANE_REL = (
    "local-lab/ghidra-function-fragment5-range-scratch-20260814-v1"
)
SCRATCH_PORTABLE_REL = f"{SCRATCH_LANE_REL}/portable"
SCRATCH_RECEIPT_REL = (
    f"{SCRATCH_PORTABLE_REL}/authority/sealed-primary.ready.json"
)
PRE_ACCOUNTING_REL = (
    "local-lab/current-text-ownership-post8280-20260814-v1/"
    "export/body-ranges.tsv"
)
PROJECTION_SOURCE = f"{LIVE_LANE_REL}/runs/live-readback/functions.tsv"

PRE_FUNCTIONS_STAMP = (
    7161942,
    "c3942b9e340cef71b731290b845843697af5c53204449c51949b779e896272d6",
)
PRE_PROGRAM_STAMP = (
    1267,
    "3e51ce1d5e926c632869b2058c9d89e91f48345a329a724ea9520570bd91212d",
)
POST_FUNCTIONS_STAMP = (
    7161943,
    "d2ff1e8e7bd91454fff9822fb7ecc8e624525fa5c6cbc9dcfe06f4e0212b750d",
)
POST_PROGRAM_STAMP = (
    1267,
    "b389487a65d6271329703c9e3ec9186b7261aa871a154c31179322780e1c132e",
)
PRE_PROJECTION_STAMP = (
    508242,
    "6e22a93a4792a2b5a9a6109a65e3b6460dc1ef6dc0606cc195a9a50e30ebdd68",
)
POST_PROJECTION_STAMP = (
    508239,
    "267210a78248f58da6bca1b4d11ee7b1812481602413e8bcac2fb4e4b4c4cb84",
)
PRE_BODY_RANGES_STAMP = (
    1198388,
    "0101e6e8b34eaea8bd646a0fa9a8e4e448bef586c8b2b898c78241befde3aa6b",
)
POST_BODY_RANGES_STAMP = (
    1197803,
    "495f1a86490e7b2646d2a0a6cd86bf6e4cdb071d5932b7d65ded1377621582e2",
)
SCRATCH_RECEIPT_STAMP = (
    9348,
    "a35f35ac99cd5d7251a86b7cf54c5aac2e2919870efca6566600045138571a04",
)
SCRATCH_TREE = {
    "fileCount": 515,
    "totalBytes": 3085497716,
    "treeSha256":
        "a4124ecf6186e977e86903cfef47535fece7a77bd202bcbceb34b2764cbad890",
    "canonicalization": "relative-posix-path<NUL>file-sha256<NUL>, path order",
}

RESULT_STAMPS = {
    "dry": (
        1930,
        "7b3809128cbdff5401a21ad9fe8b2262a00c3fe74358c83013ae012d230e5965",
    ),
    "apply": (
        2181,
        "f62ccc2ceb3b4ed775f19377cf1a514ae1eb4703088902e96ab8399b2347bc25",
    ),
    "readback": (
        2196,
        "4f765e7b84167abe034625a48b48b02af453406f91751ec1dfb67714c1268a06",
    ),
}

EXPECTED_REPO_INPUTS = {
    MANIFEST_REL: (
        2878,
        "c44e3671f1b5a28f7e214c572be2efd21046275cf4d97d7bdbac207ba15a87f0",
    ),
    "tools/GhidraApplyFunctionFragmentRanges.java": (
        50339,
        "fe845a9df094eff4a1d9b36c9d4a6b141f049356499016a20a673071d492ec4c",
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
    "tools/GhidraProjectOpenProbe.java": (
        3452,
        "fab2f701dfefe8604c1718d007dbe0ad59d330a9b3ec081ef2f2fe253b441fab",
    ),
    "tools/ghidra_function_fragment_range_scratch_authority.py": (
        24160,
        "1eed1350e38c4abbf840b2ae0fc1d444a4a818e154726c3a35ad347057f20678",
    ),
    "tools/re_ghidra_name_projection.py": (
        6139,
        "d13d5f4d3b20cbd1e1baf24cd924d454c6c07b0bbf5517834c4089357f14ecdb",
    ),
}

RUN_LAYOUT = {
    "dry": "live-pre-readback",
    "apply": "live-apply",
    "readback": "live-readback",
}

POST_BODY_ROWS = {
    "0x00462640": (
        ("0x00462640", "0x00462b63", "0x00462b64", "1316",
         "98821eecbe786c224f6af62fe40a8b60697469f685e182959e93778f3ac93dee"),
    ),
    "0x0046ff10": (
        ("0x0046ff10", "0x00470049", "0x0047004a", "314",
         "a61693db0f8e2e82dc69230a68fe6ba8e1628b068ece81b62ebb7830e98a2ef4"),
        ("0x0047005d", "0x004700f5", "0x004700f6", "153",
         "6c77882bd3665bff5e55f563972667fc70a56e78cb035d0fd14ca62df4e78014"),
    ),
    "0x00482590": (
        ("0x00482590", "0x00483504", "0x00483505", "3957",
         "670b052cdfe544cc4524dff10f28beaee6c7f3b30bffcb4734d3eddcc1915b23"),
    ),
    "0x004be420": (
        ("0x004be420", "0x004be94b", "0x004be94c", "1324",
         "1ad8fcdc99140166c01a439560701be9b737ae10e06dc1492219eefdd875c5f7"),
    ),
    "0x00559410": (
        ("0x00559410", "0x00559b69", "0x00559b6a", "1882",
         "7994ac019b8370d12a0a22e36486b50cc06c1239ac2de4f9d92c7ce47b39685f"),
    ),
}

CLAIMS = (
    "The retained 515-file scratch tree and exact sealed receipt reproduce two saved positive replicas, separate readbacks, adverse controls, and PRE recovery.",
    "Live and tracked were exact byte-identical db.18613 PRE projects before any ceremony artifact existed.",
    "The completed ceremony contains exactly one writable live apply between read-only PRE and separate read-only POST runs.",
    "All 8,275 non-target rows remain byte-identical; only the five reviewed owner rows change, functions remain 8,280, ranges become 8,396, and ownership gains exactly 1,258 bytes.",
    "The only physical project transition is db.18612 removal and db.18614 addition while db.18613 and every other common file remain exact.",
    "PRE and POST off-volume backups reopen read-only; tracked remains PRE through POST recovery, then tracked POST and its retained restore equal live POST byte-for-byte.",
    "The tracked projection and exact 1,795,470-byte body accounting are refreshed mechanically from the proved POST state.",
    "No name, signature, comment, tag, data, byte, behavior, runtime, or reconstruction claim is authorized by this structural promotion.",
)


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


def stamp(path: Path, role: str) -> dict[str, Any]:
    require(path.is_file(), f"missing {role}: {path}")
    return {"role": role, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def verify_stamp(path: Path, expected: tuple[int, str], role: str) -> dict[str, Any]:
    measured = stamp(path, role)
    require(
        (measured["bytes"], measured["sha256"]) == expected,
        f"{role} stamp differs",
    )
    return measured


def load_json(path: Path, label: str) -> dict[str, Any]:
    require(path.is_file(), f"missing {label}: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise AuthorityError(f"invalid {label}: {path}") from exc
    require(isinstance(value, dict), f"{label} is not an object")
    return value


def parse_utc(value: Any, label: str) -> datetime:
    require(isinstance(value, str) and value.endswith("Z"), f"{label} UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise AuthorityError(f"{label} UTC timestamp") from exc
    return parsed


def mtime_utc(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def clean_path(path: Path) -> Path:
    return Path(os.path.abspath(path)).resolve(strict=False)


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def require_disjoint(first: Path, second: Path, label: str) -> None:
    require(not is_within(first, second) and not is_within(second, first), label)


def exact_directory_entries(
    root: Path,
    *,
    expected_files: Iterable[str],
    expected_directories: Iterable[str],
    label: str,
) -> None:
    require(root.is_dir(), f"missing {label}: {root}")
    require(not project_backup.is_reparse(root), f"unsafe {label}: {root}")
    files: set[str] = set()
    directories: set[str] = set()
    for entry in root.iterdir():
        require(not project_backup.is_reparse(entry), f"unsafe {label} entry: {entry}")
        if entry.is_file():
            files.add(entry.name)
        elif entry.is_dir():
            directories.add(entry.name)
        else:
            raise AuthorityError(f"unsupported {label} entry: {entry}")
    require(files == set(expected_files), f"{label} file set differs: {sorted(files)}")
    require(
        directories == set(expected_directories),
        f"{label} directory set differs: {sorted(directories)}",
    )


def ensure_portable(value: Any, label: str = "root") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            ensure_portable(child, f"{label}.{key}")
    elif isinstance(value, list) or isinstance(value, tuple):
        for index, child in enumerate(value):
            ensure_portable(child, f"{label}[{index}]")
    elif isinstance(value, str):
        require(not re.match(r"^[A-Za-z]:[\\/]", value), f"absolute path leaked at {label}")
        require(not value.startswith("\\\\"), f"UNC path leaked at {label}")


def tree_identity(root: Path) -> dict[str, Any]:
    require(root.is_dir(), f"missing scratch tree: {root}")
    digest = hashlib.sha256()
    count = 0
    total = 0
    for path in sorted(root.rglob("*")):
        require(not project_backup.is_reparse(path), f"scratch tree reparse entry: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        file_digest = sha256_file(path)
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_digest.encode("utf-8"))
        digest.update(b"\0")
        count += 1
        total += path.stat().st_size
    return {
        "fileCount": count,
        "totalBytes": total,
        "treeSha256": digest.hexdigest(),
        "canonicalization": SCRATCH_TREE["canonicalization"],
    }


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
        "structurallyComplete": manifest.structurally_complete,
        "files": files,
    }


def project_without_root(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value.get(key)
        for key in ("projectName", "fileCount", "totalBytes", "structurallyComplete", "files")
    }


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
        "canonicalization":
            "sha256<TAB>bytes<TAB>relative-posix-path<LF>, relative-path order",
    }


def project_file_map(value: Mapping[str, Any]) -> dict[str, tuple[int, str]]:
    return {
        str(row["relative_path"]): (int(row["size"]), str(row["sha256"]))
        for row in value.get("files", [])
    }


def require_same_project(
    left: Mapping[str, Any], right: Mapping[str, Any], label: str
) -> None:
    require(project_without_root(left) == project_without_root(right), f"{label} differs")


def require_pre_project(value: Mapping[str, Any], label: str) -> None:
    require(value.get("projectName") == "BEA", f"{label} project name")
    require(value.get("structurallyComplete") is True, f"{label} completeness")
    summary = project_summary(value)
    for key, expected in PRE_PROJECT.items():
        require(summary.get(key) == expected, f"{label} {key} differs")
    files = project_file_map(value)
    require(files.get(PRE_OLD_DB_PATH) == DB_18612, f"{label} db.18612 identity")
    require(files.get(PRE_STABLE_DB_PATH) == DB_18613, f"{label} db.18613 identity")
    require(POST_ROLLING_DB_PATH not in files, f"{label} unexpectedly contains db.18614")


def validate_post_transition(
    pre: Mapping[str, Any], post: Mapping[str, Any], label: str
) -> dict[str, Any]:
    require(post.get("projectName") == "BEA", f"{label} project name")
    require(post.get("structurallyComplete") is True, f"{label} completeness")
    require(post.get("fileCount") == PRE_PROJECT["fileCount"], f"{label} file count")
    before = project_file_map(pre)
    after = project_file_map(post)
    removed = sorted(set(before) - set(after))
    added = sorted(set(after) - set(before))
    changed = sorted(
        path for path in set(before) & set(after) if before[path] != after[path]
    )
    require(removed == [PRE_OLD_DB_PATH], f"{label} removed paths")
    require(added == [POST_ROLLING_DB_PATH], f"{label} added paths")
    require(changed == [], f"{label} changed common files")
    require(after.get(PRE_STABLE_DB_PATH) == DB_18613, f"{label} stable db.18613")
    rolling = after.get(POST_ROLLING_DB_PATH)
    require(rolling is not None and rolling[0] > 0, f"{label} rolling db.18614")
    return {
        "removed": removed,
        "added": added,
        "changedCommonFiles": changed,
        "byteDelta": int(post["totalBytes"]) - int(pre["totalBytes"]),
        "stableDatabase": {
            "path": PRE_STABLE_DB_PATH,
            "bytes": DB_18613[0],
            "sha256": DB_18613[1],
        },
        "rollingDatabase": {
            "path": POST_ROLLING_DB_PATH,
            "bytes": rolling[0],
            "sha256": rolling[1],
        },
    }


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
    def projection(self) -> Path:
        return self.repo / PROJECTION_REL

    @property
    def scratch_lane(self) -> Path:
        return self.evidence_repo / SCRATCH_LANE_REL

    @property
    def scratch_portable(self) -> Path:
        return self.evidence_repo / SCRATCH_PORTABLE_REL

    @property
    def scratch_receipt(self) -> Path:
        return self.evidence_repo / SCRATCH_RECEIPT_REL

    @property
    def pre_accounting(self) -> Path:
        return self.evidence_repo / PRE_ACCOUNTING_REL


def validate_layout(config: Config) -> None:
    require(config.repo.is_dir(), "repository root is missing")
    require(config.evidence_repo.is_dir(), "evidence repository root is missing")
    require(config.live_project.is_dir(), "live project root is missing")
    require(config.tracked_project.is_dir(), "tracked project root is missing")
    require(
        clean_path(config.live_lane) == clean_path(config.evidence_repo / LIVE_LANE_REL),
        "live lane is not the canonical evidence path",
    )
    roots = [
        config.live_project,
        config.tracked_project,
        config.live_lane,
        config.pre_backup,
        config.post_backup,
    ]
    for index, left in enumerate(roots):
        for right in roots[index + 1:]:
            require_disjoint(clean_path(left), clean_path(right), "project/evidence roots overlap")


def validate_repo_inputs(config: Config) -> dict[str, Any]:
    ledger: dict[str, Any] = {}
    for relative, expected in EXPECTED_REPO_INPUTS.items():
        ledger[relative] = verify_stamp(config.repo / relative, expected, relative)
    imported = {
        "authority-import/ghidra_project_backup.py": Path(project_backup.__file__).resolve(),
        "authority-import/ghidra_function_fragment_range_scratch_authority.py":
            Path(scratch.__file__).resolve(),
        "authority-import/re_ghidra_name_projection.py": Path(name_projection.__file__).resolve(),
    }
    expected = {
        "authority-import/ghidra_project_backup.py":
            EXPECTED_REPO_INPUTS["tools/ghidra_project_backup.py"],
        "authority-import/ghidra_function_fragment_range_scratch_authority.py":
            EXPECTED_REPO_INPUTS[
                "tools/ghidra_function_fragment_range_scratch_authority.py"
            ],
        "authority-import/re_ghidra_name_projection.py":
            EXPECTED_REPO_INPUTS["tools/re_ghidra_name_projection.py"],
    }
    for role, path in imported.items():
        ledger[role] = verify_stamp(path, expected[role], role)
    return ledger


def load_targets(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    require(len(rows) == TARGETS and all(None not in row for row in rows), "target manifest")
    entries = [str(row["entry"]).lower() for row in rows]
    require(entries == sorted(entries) and len(set(entries)) == TARGETS, "target order")
    require(set(entries) == set(POST_BODY_ROWS), "target set")
    require(sum(int(row["repair_bytes"]) for row in rows) == REPAIR_BYTES, "repair bytes")
    require(sum(int(row["repair_instruction_count"]) for row in rows) == 325,
            "repair instructions")
    require(all(row["mutation_scope"] == "BODY_RANGE_AND_BOUNDED_DISASSEMBLY_ONLY"
                for row in rows), "target mutation scope")
    return [{str(key): str(value) for key, value in row.items()} for row in rows]


def validate_scratch(config: Config) -> dict[str, Any]:
    measured_tree = tree_identity(config.scratch_lane)
    require(measured_tree == SCRATCH_TREE, "retained full scratch tree identity differs")
    receipt = verify_stamp(
        config.scratch_receipt, SCRATCH_RECEIPT_STAMP, "scratch/authority receipt"
    )
    portable = config.scratch_portable
    static = scratch.verify_static(portable)
    inventory = scratch.verify_inventory_delta(portable)
    replicas = scratch.verify_replicas_and_controls(portable)
    backup = scratch.verify_backup(portable)
    tools = scratch.verify_tools(portable)
    recorded = load_json(config.scratch_receipt, "scratch authority receipt")
    require(recorded.get("status") == "READY", "scratch status")
    require(
        recorded.get("verdict") == "STRICT_GO_FOR_LATER_TRACKED_PREPARATION",
        "scratch verdict",
    )
    require(recorded.get("policy") == "LIVE_FORBIDDEN", "scratch policy")
    require(recorded.get("repair") == {
        "addedBodyBytes": REPAIR_BYTES,
        "bridgedPriorRangeComponents": 4,
        "existingFunctionsOnly": TARGETS,
        "extendedSinglePriorComponent": 1,
        "newFunctions": 0,
        "postBodyRanges": POST_RANGES,
        "postFunctions": POST_FUNCTIONS,
        "postInstructions": POST_INSTRUCTIONS,
        "postOwnedBytes": POST_OWNED,
        "postReferences": POST_REFERENCES,
    }, "scratch repair summary")
    return {
        "receipt": receipt,
        "fullTree": measured_tree,
        "manifestRows": static["manifestRows"],
        "unchangedFunctionRows": inventory["unchangedFunctionRows"],
        "changedFunctionRows": inventory["changedFunctionRows"],
        "positiveReplicas": replicas["positiveReplicas"],
        "savedReadbacks": replicas["savedReadbacks"],
        "adverseControls": replicas["adverseControls"],
        "restoredPreReadbacks": replicas["restoredPreReadbacks"],
        "containmentRefusals": replicas["containmentRefusals"],
        "backupReadOnlyOpen": backup["readOnlyOpen"],
        "packagedTools": len(tools),
    }


def preflight(config: Config) -> dict[str, Any]:
    validate_layout(config)
    repo_inputs = validate_repo_inputs(config)
    targets = load_targets(config.repo / MANIFEST_REL)
    scratch_result = validate_scratch(config)
    require(not config.live_lane.exists(), "canonical live lane already exists")
    require(not config.pre_backup.exists(), "PRE backup destination already exists")
    require(not config.post_backup.exists(), "POST backup destination already exists")
    authority_root = config.repo / Path(AUTHORITY_RECEIPT_REL).parent
    require(not authority_root.exists(), "canonical authority root already exists")
    evidence_authority_root = config.evidence_repo / Path(AUTHORITY_RECEIPT_REL).parent
    require(
        not evidence_authority_root.exists(),
        "canonical evidence-repository authority root already exists",
    )

    live_before = project_value(config.live_project)
    tracked = project_value(config.tracked_project)
    live_after = project_value(config.live_project)
    require_pre_project(live_before, "live PRE first read")
    require_pre_project(live_after, "live PRE second read")
    require_pre_project(tracked, "tracked PRE")
    require_same_project(live_before, live_after, "live PRE stability")
    require_same_project(live_before, tracked, "live/tracked PRE")
    projection = verify_stamp(config.projection, PRE_PROJECTION_STAMP, PROJECTION_REL)
    accounting = verify_stamp(
        config.pre_accounting, PRE_BODY_RANGES_STAMP, "evidence/PRE body ranges"
    )
    return {
        "baseCommit": BASE_COMMIT,
        "policy": POLICY,
        "repositoryInputs": repo_inputs,
        "targets": len(targets),
        "scratchAuthority": scratch_result,
        "livePre": project_summary(live_before),
        "trackedPre": project_summary(tracked),
        "liveStableAcrossTwoReads": True,
        "liveEqualsTracked": True,
        "preProjection": projection,
        "preBodyAccounting": accounting,
        "futureCeremonyArtifactsPresent": False,
        "futureMutationAuthorized": False,
        "blocker": "FUTURE_CEREMONY_ARTIFACTS_DO_NOT_EXIST",
        "verdict": "PREPARATION_READY_MUTATION_NOT_AUTHORIZED",
    }


@dataclass(frozen=True)
class RawTable:
    fields: tuple[str, ...]
    order: tuple[str, ...]
    rows: Mapping[str, Mapping[str, str]]
    raw_rows: Mapping[str, bytes]


def raw_tsv(path: Path, key: str) -> RawTable:
    raw = path.read_bytes()
    require(raw.endswith(b"\n") and b"\r" not in raw, f"{path} must be LF-only")
    lines = raw.splitlines()
    require(lines, f"empty TSV: {path}")
    while lines and lines[0].startswith(b"#"):
        lines.pop(0)
    require(lines, f"headerless TSV: {path}")
    try:
        fields = tuple(lines[0].decode("utf-8").split("\t"))
        text = b"\n".join(lines).decode("utf-8")
    except UnicodeError as exc:
        raise AuthorityError(f"invalid UTF-8 TSV: {path}") from exc
    require(key in fields and len(fields) == len(set(fields)), f"bad TSV header: {path}")
    rows: dict[str, Mapping[str, str]] = {}
    raw_rows: dict[str, bytes] = {}
    order: list[str] = []
    reader = csv.DictReader(text.splitlines(), delimiter="\t")
    for number, (row, raw_line) in enumerate(zip(reader, lines[1:]), start=2):
        value = str(row.get(key) or "").lower()
        require(value and value not in rows and None not in row,
                f"bad {key} at {path}:{number}")
        rows[value] = dict(row)
        raw_rows[value] = raw_line
        order.append(value)
    require(len(order) == len(lines) - 1, f"TSV parse incomplete: {path}")
    return RawTable(fields, tuple(order), rows, raw_rows)


def validate_function_delta(config: Config) -> dict[str, Any]:
    before_path = config.live_lane / "runs/live-pre-readback/functions.tsv"
    after_path = config.live_lane / "runs/live-readback/functions.tsv"
    verify_stamp(before_path, PRE_FUNCTIONS_STAMP, "live PRE functions")
    verify_stamp(after_path, POST_FUNCTIONS_STAMP, "live POST functions")
    scratch_before = config.scratch_portable / "inventories/base/functions.tsv"
    scratch_after = config.scratch_portable / "inventories/final-replica-a/functions.tsv"
    require(before_path.read_bytes() == scratch_before.read_bytes(), "live/scratch PRE functions")
    require(after_path.read_bytes() == scratch_after.read_bytes(), "live/scratch POST functions")
    before = raw_tsv(before_path, "address")
    after = raw_tsv(after_path, "address")
    require(before.fields == after.fields, "function headers differ")
    require(before.order == after.order and len(before.order) == PRE_FUNCTIONS,
            "function population/order differs")
    changed: set[str] = set()
    for address in before.order:
        if before.raw_rows[address] != after.raw_rows[address]:
            changed.add(address)
            fields = {
                name for name in before.fields
                if before.rows[address][name] != after.rows[address][name]
            }
            expected = scratch.TARGETS.get(address)
            require(expected is not None, f"unexpected changed row: {address}")
            require(fields == expected["changed"], f"changed fields differ at {address}")
            for name in expected["changed"]:
                require(after.rows[address][name] == expected[name],
                        f"POST {name} differs at {address}")
    require(changed == set(scratch.TARGETS), "changed function-row set differs")
    return {
        "pre": stamp(before_path, "live-lane/runs/live-pre-readback/functions.tsv"),
        "post": stamp(after_path, "live-lane/runs/live-readback/functions.tsv"),
        "unchangedRowsExact": PRE_FUNCTIONS - TARGETS,
        "changedRowsExact": TARGETS,
        "changedAddresses": sorted(changed),
        "created": 0,
        "destroyed": 0,
    }


def read_metrics(path: Path) -> dict[str, str]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    require(rows and all(None not in row for row in rows), f"invalid metrics: {path}")
    result: dict[str, str] = {}
    for row in rows:
        key = str(row["metric"])
        require(key not in result, f"duplicate metric: {key}")
        result[key] = str(row["value"])
    return result


def validate_program_delta(config: Config) -> dict[str, Any]:
    before_path = config.live_lane / "runs/live-pre-readback/program.tsv"
    after_path = config.live_lane / "runs/live-readback/program.tsv"
    verify_stamp(before_path, PRE_PROGRAM_STAMP, "live PRE program")
    verify_stamp(after_path, POST_PROGRAM_STAMP, "live POST program")
    require(
        before_path.read_bytes()
        == (config.scratch_portable / "inventories/base/program.tsv").read_bytes(),
        "live/scratch PRE program",
    )
    require(
        after_path.read_bytes()
        == (config.scratch_portable / "inventories/final-replica-a/program.tsv").read_bytes(),
        "live/scratch POST program",
    )
    before = read_metrics(before_path)
    after = read_metrics(after_path)
    require(set(before) == set(after), "program metric set differs")
    changed = {key for key in before if before[key] != after[key]}
    expected = {
        "instructions", "instructionLayoutSha256", "undefinedData",
        "symbolsDefaultOther", "references", "referencesSha256",
    }
    require(changed == expected, f"program changed metrics differ: {sorted(changed)}")
    require(before["functions"] == after["functions"] == str(PRE_FUNCTIONS),
            "program function count")
    return {
        "pre": stamp(before_path, "live-lane/runs/live-pre-readback/program.tsv"),
        "post": stamp(after_path, "live-lane/runs/live-readback/program.tsv"),
        "changedMetrics": sorted(changed),
        "instructions": {"before": PRE_INSTRUCTIONS, "after": POST_INSTRUCTIONS},
        "references": {"before": PRE_REFERENCES, "after": POST_REFERENCES},
        "memoryUnchanged": before["memorySha256"] == after["memorySha256"],
        "definedDataUnchanged": before["definedDataSha256"] == after["definedDataSha256"],
        "storedNonFunctionSymbolsUnchanged":
            before["nonFunctionSymbolsSha256"] == after["nonFunctionSymbolsSha256"],
        "commentsUnchanged": before["commentsSha256"] == after["commentsSha256"],
    }


def validate_inventory_diff(config: Config) -> dict[str, Any]:
    path = config.live_lane / "runs/live-readback/inventory-diff.json"
    value = load_json(path, "live inventory diff")
    expected_counts = {
        "after": 8280, "before": 8280, "boundsChanged": 5,
        "callingConvChanged": 0, "created": 0, "destroyed": 0,
        "instrCountChanged": 5, "namesChanged": 0, "noReturnChanged": 0,
        "paramCountChanged": 0, "returnTypeChanged": 0,
        "sigSourceChanged": 0, "signaturesChanged": 0, "thunkFlagChanged": 0,
    }
    require(value.get("counts") == expected_counts, "inventory-diff counts")
    targets = set(POST_BODY_ROWS)
    changes = value.get("changesByField", {})
    for field in ("bodyBytes", "bodyDigest", "instrCount"):
        require({row["address"] for row in changes.get(field, [])} == targets,
                f"inventory-diff {field} set")
    require({row["address"] for row in changes.get("bodyRanges", [])}
            == targets - {"0x00462640"}, "inventory-diff bodyRanges set")
    require({row["address"] for row in changes.get("bodyMax", [])}
            == {"0x00462640"}, "inventory-diff bodyMax set")
    for field in (
        "callingConv", "isThunk", "name", "nameSource", "noReturn",
        "paramCount", "returnType", "sigSource", "signature",
    ):
        require(changes.get(field) == [], f"inventory-diff {field} changed")
    dangerous = value.get("dangerous", {})
    require(dangerous.get("gradedBoundsMovedCount") == TARGETS,
            "inventory-diff authorized graded bounds")
    require({row["address"] for row in dangerous.get("gradedBoundsMoved", [])}
            == targets, "inventory-diff graded bounds set")
    for key in (
        "gradedDemotedCount", "gradedDestroyedCount", "gradedRenamedCount",
    ):
        require(dangerous.get(key) == 0, f"inventory-diff {key}")
    require(value.get("created") == [] and value.get("destroyed") == [],
            "inventory-diff population")
    return stamp(path, "live-lane/runs/live-readback/inventory-diff.json")


def validate_low_level_receipt(
    config: Config, run_name: str, mode: str
) -> datetime:
    root = config.live_lane / "runs" / run_name
    result_path = root / "result.tsv"
    receipt = load_json(root / "result.ready.json", f"{run_name} receipt")
    require(receipt.get("schema") == "bea.ghidra.function-fragment-range-repair.v1",
            f"{run_name} schema")
    require(receipt.get("status") == "READY_FOR_SCRATCH_ONLY", f"{run_name} status")
    require(receipt.get("policy") == "LIVE_FORBIDDEN", f"{run_name} inner policy")
    require(receipt.get("mode") == mode, f"{run_name} mode")
    require(receipt.get("manifest") == {
        "name": "fragment-manifest.tsv", "bytes": 2878,
        "sha256": EXPECTED_REPO_INPUTS[MANIFEST_REL][1],
    }, f"{run_name} manifest")
    require(receipt.get("tool") == {
        "name": "GhidraApplyFunctionFragmentRanges.java", "bytes": 50339,
        "sha256": EXPECTED_REPO_INPUTS["tools/GhidraApplyFunctionFragmentRanges.java"][1],
    }, f"{run_name} tool")
    measured = verify_stamp(result_path, RESULT_STAMPS[mode], f"{run_name} result")
    require(receipt.get("output") == {
        "name": "result.tsv", "bytes": measured["bytes"], "sha256": measured["sha256"],
    }, f"{run_name} output")
    require(receipt.get("program") == {
        "name": PROGRAM_NAME, "md5": PROGRAM_MD5, "sha256": PROGRAM_SHA256,
    }, f"{run_name} program")
    pre_counts = {
        "functions": PRE_FUNCTIONS, "bodyRanges": PRE_RANGES,
        "ownedBytes": PRE_OWNED, "instructions": PRE_INSTRUCTIONS,
        "references": PRE_REFERENCES,
    }
    post_counts = {
        "functions": POST_FUNCTIONS, "bodyRanges": POST_RANGES,
        "ownedBytes": POST_OWNED, "instructions": POST_INSTRUCTIONS,
        "references": POST_REFERENCES,
    }
    expected_before = post_counts if mode == "readback" else pre_counts
    expected_after = pre_counts if mode == "dry" else post_counts
    require(receipt.get("countsBefore") == expected_before, f"{run_name} PRE counts")
    require(receipt.get("countsAfter") == expected_after, f"{run_name} POST counts")
    require(receipt.get("targets") == TARGETS and receipt.get("repairBytes") == REPAIR_BYTES,
            f"{run_name} totals")
    require(receipt.get("postVerified") is (mode != "dry"), f"{run_name} post gate")
    require(receipt.get("rollbackVerified") is False, f"{run_name} rollback field")
    require(receipt.get("newFunctionsAuthorized") is False, f"{run_name} function policy")
    require(receipt.get("namesSignaturesCommentsTagsDataAuthorized") is False,
            f"{run_name} metadata policy")
    require(receipt.get("separateSavedReadbackRequired") is (mode == "apply"),
            f"{run_name} readback policy")
    scratch_run = {
        "dry": "runs/control-one-restored/result.tsv",
        "apply": "runs/final-replica-a-apply/result.tsv",
        "readback": "runs/final-replica-a-readback/result.tsv",
    }[mode]
    require(result_path.read_bytes() == (config.scratch_portable / scratch_run).read_bytes(),
            f"{run_name} differs from scratch {mode}")
    return parse_utc(receipt.get("completedAtUtc"), f"{run_name} completedAtUtc")


def validate_run_log(path: Path, mode: str) -> dict[str, int]:
    text = path.read_text(encoding="utf-8", errors="strict")
    require(text.count(f"FUNCTION_FRAGMENT_RANGES_OK mode={mode}") == 1,
            f"{path.parent.name} success marker")
    for marker in (
        "REPORT SCRIPT ERROR", "FUNCTION_FRAGMENT_RANGES_FAIL", "Exception", "Traceback",
    ):
        require(marker not in text, f"{path.parent.name} error marker: {marker}")
    saves = text.count("Save succeeded for processed file: /BEA.exe")
    read_only = text.count("Processing read-only project file: /BEA.exe")
    writable = len(re.findall(r"Processing project file: /BEA\.exe", text))
    if mode == "apply":
        require((saves, read_only, writable) == (1, 0, 1), f"{path.parent.name} apply shape")
    else:
        require((saves, read_only, writable) == (0, 1, 0), f"{path.parent.name} read-only shape")
    return {"successfulSaves": saves, "readOnlyOpens": read_only, "writableOpens": writable}


def validate_runs(config: Config) -> tuple[dict[str, Any], dict[str, datetime]]:
    exact_directory_entries(
        config.live_lane / "runs",
        expected_files=(), expected_directories=RUN_LAYOUT.values(), label="live runs root",
    )
    summaries: dict[str, Any] = {}
    times: dict[str, datetime] = {}
    saves = 0
    for mode, run_name in RUN_LAYOUT.items():
        root = config.live_lane / "runs" / run_name
        expected = {"result.tsv", "result.ready.json", "ghidra.log"}
        if mode in {"dry", "readback"}:
            expected |= {"functions.tsv", "program.tsv"}
        if mode == "readback":
            expected.add("inventory-diff.json")
        exact_directory_entries(
            root, expected_files=expected, expected_directories=(), label=f"run {run_name}"
        )
        times[f"live.{mode}.receipt"] = validate_low_level_receipt(config, run_name, mode)
        shape = validate_run_log(root / "ghidra.log", mode)
        saves += shape["successfulSaves"]
        times[f"live.{mode}.complete"] = max(mtime_utc(path) for path in root.iterdir())
        summaries[mode] = {
            "receipt": stamp(root / "result.ready.json", f"live-lane/runs/{run_name}/result.ready.json"),
            "result": stamp(root / "result.tsv", f"live-lane/runs/{run_name}/result.tsv"),
            "log": stamp(root / "ghidra.log", f"live-lane/runs/{run_name}/ghidra.log"),
            "processShape": shape,
        }
    require(saves == 1, "live lane does not contain exactly one successful save")
    summaries["functionDelta"] = validate_function_delta(config)
    summaries["programDelta"] = validate_program_delta(config)
    summaries["inventoryDiff"] = validate_inventory_diff(config)
    summaries["successfulLiveSaves"] = saves
    return summaries, times


def manifest_value(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value.get(key)
        for key in ("projectName", "fileCount", "totalBytes", "structurallyComplete", "files")
    }


def validate_inspect(
    path: Path, expected_root: Path, expected: Mapping[str, Any], label: str
) -> datetime:
    value = load_json(path, label)
    require(value.get("schemaVersion") == project_backup.SCHEMA_VERSION, f"{label} schema")
    require(manifest_value(value.get("manifest", {})) == project_without_root(expected),
            f"{label} manifest")
    require(clean_path(Path(value["manifest"].get("root", ""))) == clean_path(expected_root),
            f"{label} root")
    return parse_utc(value.get("createdAtUtc"), f"{label} createdAtUtc")


def validate_backup_manifest(
    path: Path, expected: Mapping[str, Any], label: str
) -> datetime:
    value = load_json(path, label)
    require(value.get("schemaVersion") == project_backup.SCHEMA_VERSION, f"{label} schema")
    require(value.get("sourceStable") is True, f"{label} source stability")
    require(value.get("probeCopyDisposition") == "RETAINED_AT_VERIFICATION",
            f"{label} probe retention")
    comparison = value.get("copyComparison", {})
    require(comparison.get("matches") is True, f"{label} copy comparison")
    require(manifest_value(value.get("source", {})) == project_without_root(expected),
            f"{label} source")
    require(manifest_value(value.get("destination", {})) == project_without_root(expected),
            f"{label} destination")
    return parse_utc(value.get("createdAtUtc"), f"{label} createdAtUtc")


def validate_restore(
    config: Config,
    receipt_name: str,
    probe_root_name: str,
    source_root: Path,
    expected: Mapping[str, Any],
    label: str,
) -> tuple[dict[str, Any], datetime]:
    path = config.live_lane / receipt_name
    value = load_json(path, label)
    require(value.get("schemaVersion") == project_backup.SCHEMA_VERSION, f"{label} schema")
    require(value.get("sourceStable") is True, f"{label} source stability")
    require(manifest_value(value.get("source", {})) == project_without_root(expected),
            f"{label} source")
    require(clean_path(Path(value["source"].get("root", ""))) == clean_path(source_root),
            f"{label} source root")
    require(value.get("copyComparison", {}).get("matches") is True,
            f"{label} copy comparison")
    opened = value.get("readonlyOpen", {})
    require(opened.get("opened") is True and opened.get("contentStable") is True,
            f"{label} read-only open")
    require(opened.get("exitCode") == 0 and opened.get("observedFunctionCount") == TOTAL_FUNCTIONS,
            f"{label} open result")
    require(opened.get("observedProgramName") == PROGRAM_NAME
            and opened.get("observedProgramMd5") == PROGRAM_MD5
            and opened.get("observedProgramSha256") == PROGRAM_SHA256,
            f"{label} program identity")
    require(opened.get("postOpenComparison", {}).get("matches") is True,
            f"{label} post-open comparison")
    log = opened.get("probeLog", {})
    log_path = config.live_lane / receipt_name.replace(".json", ".open-probe.log")
    require(log.get("path") == log_path.name, f"{label} probe-log path")
    measured_log = stamp(log_path, f"live-lane/{log_path.name}")
    require((log.get("bytes"), log.get("sha256"))
            == (measured_log["bytes"], measured_log["sha256"]), f"{label} probe log")
    text = log_path.read_text(encoding="utf-8", errors="strict")
    require(text.count("GHIDRA_PROJECT_OPEN_PROBE_OK") == 1
            and "GHIDRA_PROJECT_OPEN_PROBE_FAIL" not in text
            and "REPORT SCRIPT ERROR" not in text, f"{label} clean probe log")
    command = opened.get("commandArgv", [])
    require(isinstance(command, list) and command.count("-readOnly") == 1
            and command.count("-noanalysis") == 1
            and "GhidraProjectOpenProbe.java" in command,
            f"{label} read-only command shape")
    probe = clean_path(Path(value.get("probeCopy", "")))
    expected_probe_root = clean_path(config.live_lane / probe_root_name)
    require(is_within(probe, expected_probe_root) and probe != expected_probe_root,
            f"{label} retained probe containment")
    require_same_project(project_value(probe), expected, f"{label} retained probe")
    return {
        "receipt": stamp(path, f"live-lane/{receipt_name}"),
        "probeLog": measured_log,
        "source": project_summary(expected),
        "retainedProbeEqualsSource": True,
        "readOnlyOpen": True,
    }, parse_utc(value.get("verifiedAtUtc"), f"{label} verifiedAtUtc")


def validate_projects(
    config: Config, *, require_tracked_post: bool
) -> tuple[dict[str, Any], dict[str, datetime]]:
    times: dict[str, datetime] = {}
    pre = project_value(config.pre_backup)
    require_pre_project(pre, "PRE backup")
    live = project_value(config.live_project)
    transition = validate_post_transition(pre, live, "live POST")
    post_backup = project_value(config.post_backup)
    require_same_project(post_backup, live, "POST backup/live POST")
    tracked = project_value(config.tracked_project)
    if require_tracked_post:
        require_same_project(tracked, live, "tracked/live POST")
    else:
        require_pre_project(tracked, "tracked still PRE")

    times["live.pre.inspect"] = validate_inspect(
        config.live_lane / "live-pre-inspect.json", config.live_project, pre,
        "live PRE inspect",
    )
    times["tracked.pre.inspect"] = validate_inspect(
        config.live_lane / "tracked-pre-inspect.json", config.tracked_project, pre,
        "tracked PRE inspect",
    )
    times["live.beforeApply.inspect"] = validate_inspect(
        config.live_lane / "live-before-apply-inspect.json", config.live_project, pre,
        "live before-apply inspect",
    )
    times["live.post.inspect"] = validate_inspect(
        config.live_lane / "live-post-inspect.json", config.live_project, live,
        "live POST inspect",
    )
    times["tracked.stillPre.inspect"] = validate_inspect(
        config.live_lane / "tracked-still-pre-inspect.json", config.tracked_project, pre,
        "tracked still-PRE inspect",
    )
    times["pre.backup.created"] = validate_backup_manifest(
        config.pre_backup / "backup_manifest.json", pre, "PRE backup manifest"
    )
    times["post.backup.created"] = validate_backup_manifest(
        config.post_backup / "backup_manifest.json", live, "POST backup manifest"
    )
    pre_restore, times["pre.restore.verified"] = validate_restore(
        config, "pre-backup-restore.ready.json", "pre-backup-restore-probe",
        config.pre_backup, pre, "PRE restore",
    )
    post_restore, times["post.restore.verified"] = validate_restore(
        config, "post-backup-restore.ready.json", "post-backup-restore-probe",
        config.post_backup, live, "POST restore",
    )
    restores: dict[str, Any] = {"pre": pre_restore, "post": post_restore}
    if require_tracked_post:
        times["tracked.post.inspect"] = validate_inspect(
            config.live_lane / "tracked-post-inspect.json", config.tracked_project, live,
            "tracked POST inspect",
        )
        tracked_restore, times["tracked.restore.verified"] = validate_restore(
            config, "tracked-post-restore.ready.json", "tracked-post-restore-probe",
            config.tracked_project, live, "tracked POST restore",
        )
        restores["trackedPost"] = tracked_restore
    return {
        "pre": project_summary(pre),
        "post": project_summary(live),
        "liveEqualsPostBackup": True,
        "trackedState": "POST_EXACT" if require_tracked_post else "PRE_UNCHANGED",
        "trackedStillPreAfterPostRecovery": True,
        "rollingDelta": transition,
        "restores": restores,
        "backupReceipts": {
            "pre": stamp(config.pre_backup / "backup_manifest.json",
                         "pre-backup/backup_manifest.json"),
            "post": stamp(config.post_backup / "backup_manifest.json",
                          "post-backup/backup_manifest.json"),
        },
    }, times


def parse_body_rows(path: Path) -> tuple[list[bytes], list[dict[str, str]]]:
    raw = path.read_bytes()
    require(raw.endswith(b"\n") and b"\r" not in raw, "body ranges LF framing")
    lines = raw.splitlines()
    comments: list[bytes] = []
    while lines and lines[0].startswith(b"#"):
        comments.append(lines.pop(0))
    require(lines, "body ranges header")
    text = b"\n".join(lines).decode("utf-8")
    rows = list(csv.DictReader(text.splitlines(), delimiter="\t"))
    require(all(None not in row for row in rows), "body ranges malformed row")
    return comments, [{str(k): str(v) for k, v in row.items()} for row in rows]


def validate_body_accounting(config: Config) -> tuple[dict[str, Any], datetime]:
    root = config.live_lane / "tracked-post-accounting"
    exact_directory_entries(
        root,
        expected_files=("body-ranges.tsv", "direct-calls.tsv", "parity-graph.ready.json", "ghidra.log"),
        expected_directories=(), label="tracked POST accounting",
    )
    body = root / "body-ranges.tsv"
    verify_stamp(body, POST_BODY_RANGES_STAMP, "tracked POST body ranges")
    receipt = load_json(root / "parity-graph.ready.json", "tracked POST parity graph")
    require(receipt.get("schemaVersion") == "bea-ghidra-parity-graph-receipt.v2",
            "parity graph schema")
    program = receipt.get("program", {})
    require(program.get("executableMd5") == PROGRAM_MD5
            and program.get("imageBase") == "0x00400000"
            and program.get("language") == "x86:LE:32:default"
            and program.get("compilerSpec") == "windows", "parity graph program")
    measured_body = stamp(body, "live-lane/tracked-post-accounting/body-ranges.tsv")
    require(receipt.get("bodyRanges") == {
        "file": "body-ranges.tsv", "bytes": measured_body["bytes"],
        "sha256": measured_body["sha256"], "functionCount": POST_FUNCTIONS,
        "rangeCount": POST_RANGES,
    }, "parity graph body receipt")
    calls = stamp(root / "direct-calls.tsv",
                  "live-lane/tracked-post-accounting/direct-calls.tsv")
    call_receipt = receipt.get("directCalls", {})
    require(call_receipt.get("file") == "direct-calls.tsv"
            and (call_receipt.get("bytes"), call_receipt.get("sha256"))
            == (calls["bytes"], calls["sha256"]), "parity graph calls receipt")

    _, pre_rows = parse_body_rows(config.pre_accounting)
    _, post_rows = parse_body_rows(body)
    pre_by_function: dict[str, list[dict[str, str]]] = {}
    post_by_function: dict[str, list[dict[str, str]]] = {}
    for row in pre_rows:
        pre_by_function.setdefault(row["functionAddress"].lower(), []).append(row)
    for row in post_rows:
        post_by_function.setdefault(row["functionAddress"].lower(), []).append(row)
    require(set(pre_by_function) == set(post_by_function), "body function set")
    require(len(post_by_function) == POST_FUNCTIONS and len(post_rows) == POST_RANGES,
            "body population")
    for address in set(pre_by_function) - set(POST_BODY_ROWS):
        require(pre_by_function[address] == post_by_function[address],
                f"non-target body rows changed at {address}")
    manifest = {row["entry"].lower(): row for row in load_targets(config.repo / MANIFEST_REL)}
    for address, expected_rows in POST_BODY_ROWS.items():
        actual = post_by_function[address]
        require(len(actual) == len(expected_rows), f"body range count at {address}")
        require(all(row["functionName"] == manifest[address]["current_name"] for row in actual),
                f"body name at {address}")
        for ordinal, (row, expected) in enumerate(zip(actual, expected_rows), 1):
            require(row["rangeOrdinal"] == str(ordinal), f"body ordinal at {address}")
            measured = (
                row["rangeMin"], row["rangeMax"], row["rangeEndExclusive"],
                row["rangeBytes"], row["rangeSha256"],
            )
            require(measured == expected, f"body range identity at {address}:{ordinal}")
    intervals = sorted(
        (int(row["rangeMin"], 16), int(row["rangeEndExclusive"], 16))
        for row in post_rows
    )
    require(all(TEXT_START <= start < end <= TEXT_END for start, end in intervals),
            "body interval outside virtual text")
    require(all(left[1] <= right[0] for left, right in zip(intervals, intervals[1:])),
            "overlapping body intervals")
    owned = sum(end - start for start, end in intervals)
    require(owned == POST_OWNED, "POST body ownership")
    log = root / "ghidra.log"
    text = log.read_text(encoding="utf-8", errors="strict")
    require(text.count(f"PARITY_GRAPH_OK functions={POST_FUNCTIONS} ranges={POST_RANGES}") == 1,
            "accounting success marker")
    require(text.count("Processing read-only project file: /BEA.exe") == 1
            and "Save succeeded for processed file" not in text
            and "REPORT SCRIPT ERROR" not in text, "accounting read-only shape")
    complete = max(mtime_utc(path) for path in root.iterdir())
    return {
        "bodyRanges": measured_body,
        "parityGraphReceipt": stamp(root / "parity-graph.ready.json",
                                    "live-lane/tracked-post-accounting/parity-graph.ready.json"),
        "directCalls": calls,
        "log": stamp(log, "live-lane/tracked-post-accounting/ghidra.log"),
        "functions": POST_FUNCTIONS,
        "ranges": POST_RANGES,
        "ownedBytes": owned,
        "uncoveredBytes": TEXT_BYTES - owned,
        "ownedPercent": owned * 100.0 / TEXT_BYTES,
        "nonTargetRowsExact": PRE_FUNCTIONS - TARGETS,
        "changedOwnerRowsExact": TARGETS,
        "overlapBytes": 0,
    }, complete


def validate_projection(config: Config) -> tuple[dict[str, Any], datetime]:
    inventory = config.live_lane / "runs/live-readback/functions.tsv"
    retained = config.live_lane / "ghidra-function-name-table-2026-08-13.tsv"
    expected = name_projection.projection_bytes(
        inventory,
        expected_inventory_sha256=POST_FUNCTIONS_STAMP[1],
        source_label=PROJECTION_SOURCE,
        projection_date="2026-08-14",
        specimen_sha256=PROGRAM_SHA256,
    )
    require((len(expected), hashlib.sha256(expected).hexdigest()) == POST_PROJECTION_STAMP,
            "mechanical projection identity")
    require(retained.read_bytes() == expected, "retained projection is not mechanical")
    require(config.projection.read_bytes() == expected, "tracked projection is not mechanical")
    rows = sum(1 for line in expected.splitlines() if line and not line.startswith(b"#")) - 1
    require(rows == POST_FUNCTIONS, "projection row count")
    return {
        "rows": rows,
        "bytes": len(expected),
        "sha256": hashlib.sha256(expected).hexdigest(),
        "sourceInventory": stamp(inventory, "live-lane/runs/live-readback/functions.tsv"),
        "retained": stamp(retained, "live-lane/ghidra-function-name-table-2026-08-13.tsv"),
        "tracked": stamp(config.projection, PROJECTION_REL),
        "sourceLabel": PROJECTION_SOURCE,
    }, min(mtime_utc(retained), mtime_utc(config.projection))


def require_before(events: Mapping[str, datetime], left: str, right: str) -> None:
    require(events[left] < events[right], f"chronology does not advance: {left} -> {right}")


def validate_chronology(
    project_times: Mapping[str, datetime], run_times: Mapping[str, datetime],
    projection_time: datetime | None = None,
    accounting_time: datetime | None = None,
) -> list[dict[str, str]]:
    events = {**project_times, **run_times}
    edges = [
        ("live.pre.inspect", "pre.backup.created"),
        ("tracked.pre.inspect", "pre.backup.created"),
        ("pre.backup.created", "pre.restore.verified"),
        ("pre.restore.verified", "live.dry.receipt"),
        ("live.dry.receipt", "live.dry.complete"),
        ("live.dry.complete", "live.beforeApply.inspect"),
        ("live.beforeApply.inspect", "live.apply.receipt"),
        ("live.apply.receipt", "live.apply.complete"),
        ("live.apply.complete", "live.readback.receipt"),
        ("live.readback.receipt", "live.readback.complete"),
        ("live.readback.complete", "live.post.inspect"),
        ("live.post.inspect", "post.backup.created"),
        ("post.backup.created", "post.restore.verified"),
        ("post.restore.verified", "tracked.stillPre.inspect"),
    ]
    if projection_time is not None and accounting_time is not None:
        events["projection.complete"] = projection_time
        events["accounting.complete"] = accounting_time
        edges.extend([
            ("tracked.stillPre.inspect", "tracked.post.inspect"),
            ("tracked.post.inspect", "tracked.restore.verified"),
            ("tracked.restore.verified", "projection.complete"),
            ("tracked.restore.verified", "accounting.complete"),
        ])
    for left, right in edges:
        require_before(events, left, right)
    return [
        {"event": name, "atUtc": utc_text(events[name])}
        for name in sorted(events, key=lambda item: (events[item], item))
    ]


def expected_live_lane_topology(final: bool) -> tuple[set[str], set[str]]:
    files = {
        "live-pre-inspect.json", "tracked-pre-inspect.json",
        "pre-backup-restore.ready.json", "pre-backup-restore.ready.open-probe.log",
        "live-before-apply-inspect.json", "live-post-inspect.json",
        "post-backup-restore.ready.json", "post-backup-restore.ready.open-probe.log",
        "tracked-still-pre-inspect.json",
    }
    directories = {
        "static", "runs", "pre-backup-restore-probe", "post-backup-restore-probe",
    }
    if final:
        files |= {
            "tracked-post-inspect.json", "tracked-post-restore.ready.json",
            "tracked-post-restore.ready.open-probe.log",
            "ghidra-function-name-table-2026-08-13.tsv",
        }
        directories |= {"tracked-post-restore-probe", "tracked-post-accounting"}
    return files, directories


def validate_live_lane_topology(config: Config, *, final: bool) -> None:
    files, directories = expected_live_lane_topology(final)
    exact_directory_entries(
        config.live_lane, expected_files=files, expected_directories=directories,
        label="live evidence root",
    )
    exact_directory_entries(
        config.live_lane / "static", expected_files=(), expected_directories=("final-a",),
        label="live static root",
    )
    exact_directory_entries(
        config.live_lane / "static/final-a",
        expected_files=("fragment-manifest.tsv",), expected_directories=(),
        label="live manifest root",
    )
    verify_stamp(
        config.live_lane / "static/final-a/fragment-manifest.tsv",
        EXPECTED_REPO_INPUTS[MANIFEST_REL], "live manifest copy",
    )


def validate_small_artifact_set(config: Config, *, final: bool) -> dict[str, Any]:
    validate_live_lane_topology(config, final=final)
    relative = [
        "live-pre-inspect.json", "tracked-pre-inspect.json",
        "pre-backup-restore.ready.json", "pre-backup-restore.ready.open-probe.log",
        "live-before-apply-inspect.json", "live-post-inspect.json",
        "post-backup-restore.ready.json", "post-backup-restore.ready.open-probe.log",
        "tracked-still-pre-inspect.json", "static/final-a/fragment-manifest.tsv",
    ]
    if final:
        relative += [
            "tracked-post-inspect.json", "tracked-post-restore.ready.json",
            "tracked-post-restore.ready.open-probe.log",
            "ghidra-function-name-table-2026-08-13.tsv",
            "tracked-post-accounting/body-ranges.tsv",
            "tracked-post-accounting/direct-calls.tsv",
            "tracked-post-accounting/parity-graph.ready.json",
            "tracked-post-accounting/ghidra.log",
        ]
    ledger = {
        name: stamp(config.live_lane / name, f"live-lane/{name}") for name in relative
    }
    for mode, run_name in RUN_LAYOUT.items():
        names = ["result.ready.json", "result.tsv", "ghidra.log"]
        if mode in {"dry", "readback"}:
            names += ["functions.tsv", "program.tsv"]
        if mode == "readback":
            names.append("inventory-diff.json")
        for name in names:
            role = f"runs/{run_name}/{name}"
            ledger[role] = stamp(config.live_lane / role, f"live-lane/{role}")
    return ledger


def build_live_phase(config: Config) -> dict[str, Any]:
    validate_layout(config)
    repo_inputs = validate_repo_inputs(config)
    scratch_result = validate_scratch(config)
    load_targets(config.repo / MANIFEST_REL)
    projects, project_times = validate_projects(config, require_tracked_post=False)
    runs, run_times = validate_runs(config)
    chronology = validate_chronology(project_times, run_times)
    value = {
        "baseCommit": BASE_COMMIT,
        "policy": POLICY,
        "artifactLedger": {
            "repository": repo_inputs,
            "liveLane": validate_small_artifact_set(config, final=False),
        },
        "scratchAuthority": scratch_result,
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
    scratch_result = validate_scratch(config)
    load_targets(config.repo / MANIFEST_REL)
    projects, project_times = validate_projects(config, require_tracked_post=True)
    runs, run_times = validate_runs(config)
    projection, projection_time = validate_projection(config)
    accounting, accounting_time = validate_body_accounting(config)
    chronology = validate_chronology(
        project_times, run_times, projection_time, accounting_time
    )
    value = {
        "baseCommit": BASE_COMMIT,
        "policy": POLICY,
        "artifactLedger": {
            "repository": repo_inputs,
            "liveLane": validate_small_artifact_set(config, final=True),
        },
        "scratchAuthority": scratch_result,
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
    output = clean_path(config.output)
    require(output == clean_path(config.repo / AUTHORITY_RECEIPT_REL),
            "aggregate receipt must use the canonical authority path")
    for root in (
        config.live_lane, config.scratch_lane, config.live_project,
        config.pre_backup, config.post_backup, config.tracked_project,
    ):
        require(not is_within(output, clean_path(root)),
                "aggregate receipt overlaps an evidence or project root")
    if not sealing:
        require(output.is_file(), "saved aggregate receipt is absent")
        return
    require(not output.exists(), "refusing to overwrite aggregate receipt")
    require(is_within(output, clean_path(config.repo / "local-lab")),
            "aggregate receipt must be under local-lab")
    ignored = subprocess.run(
        ["git", "-C", str(config.repo), "check-ignore", "-q", "--", str(output)],
        check=False, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True,
    )
    require(ignored.returncode == 0, "aggregate receipt path is not Git-ignored")


def atomic_new_json(path: Path, value: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    require(not path.exists(), f"refusing to overwrite existing receipt: {path}")
    raw = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    descriptor, name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".partial", dir=path.parent
    )
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
        "completedAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "authorityTool": stamp(
            Path(__file__).resolve(),
            "tools/ghidra_function_fragment_range_live_authority.py",
        ),
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
    print(
        "FUNCTION_FRAGMENT_RANGE_LIVE_AUTHORITY_READY "
        f"receipt_sha256={sha256_file(config.output)} functions={POST_FUNCTIONS} "
        f"ranges={POST_RANGES} gain={REPAIR_BYTES}"
    )


def verify(config: Config) -> None:
    validate_output(config, sealing=False)
    assert config.output is not None
    recorded = load_json(config.output, "aggregate authority receipt")
    require(recorded.get("schemaVersion") == SCHEMA, "aggregate schema")
    parse_utc(recorded.get("completedAtUtc"), "aggregate completedAtUtc")
    require(recorded.get("authorityTool") == stamp(
        Path(__file__).resolve(),
        "tools/ghidra_function_fragment_range_live_authority.py",
    ), "aggregate authority-tool binding")
    require(recorded.get("policy") == POLICY, "aggregate policy")
    require(recorded.get("ghidraOpenedByAuthority") is False
            and recorded.get("liveGhidraMutatedByAuthority") is False
            and recorded.get("trackedGhidraMutatedByAuthority") is False
            and recorded.get("futureMutationAuthorized") is False,
            "aggregate mutation boundary")
    require(recorded.get("evidence") == build_final(config),
            "aggregate evidence differs")
    ensure_portable(recorded)
    print(
        "FUNCTION_FRAGMENT_RANGE_LIVE_AUTHORITY_VERIFIED "
        f"receipt_sha256={sha256_file(config.output)} functions={POST_FUNCTIONS} "
        f"ranges={POST_RANGES} gain={REPAIR_BYTES}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("preflight", "check-live", "seal", "verify"))
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--evidence-repo", type=Path, required=True)
    parser.add_argument("--live-project", type=Path, required=True)
    parser.add_argument("--live-lane", type=Path, required=True)
    parser.add_argument("--pre-backup", type=Path, required=True)
    parser.add_argument("--post-backup", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
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
            "FUNCTION_FRAGMENT_RANGE_LIVE_PREPARATION_READY "
            f"pre_project_sha256={result['livePre']['canonicalInventorySha256']} "
            f"scratch_receipt_sha256={SCRATCH_RECEIPT_STAMP[1]} "
            "live_equals_tracked=true db=db.18613.gbf "
            "policy=PREPARATION_ONLY mutation_authorized=false "
            "blocker=future_ceremony_artifacts_absent"
        )
    elif args.command == "check-live":
        require(config.output is None, "check-live does not accept --output")
        result = build_live_phase(config)
        print(
            "FUNCTION_FRAGMENT_RANGE_LIVE_PHASE_VERIFIED "
            f"post_functions={POST_FUNCTIONS} post_ranges={POST_RANGES} "
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
        OSError,
        UnicodeError,
        subprocess.SubprocessError,
        project_backup.BackupError,
        name_projection.ProjectionError,
        scratch.AuthorityError,
    ) as exc:
        print(f"FUNCTION_FRAGMENT_RANGE_LIVE_AUTHORITY_REFUSED reason={exc}", file=sys.stderr)
        raise SystemExit(1)
