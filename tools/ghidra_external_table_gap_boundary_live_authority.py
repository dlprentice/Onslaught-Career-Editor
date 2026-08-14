#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Preflight, reproduce, and seal the 79-function live-promotion ceremony.

This authority never launches Ghidra and never mutates the live or tracked
project.  ``preflight`` only hashes the current PRE state and reproduces the
sealed scratch authority.  ``check-live`` proves the completed live phase while
the tracked project must still be PRE.  ``seal`` has one write: create-new
publication of a portable aggregate receipt after the separately authorized
tracked refresh.  ``verify`` reproduces an existing aggregate receipt.
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

import ghidra_external_table_gap_boundary_scratch_authority as scratch  # noqa: E402
import ghidra_project_backup as project_backup  # noqa: E402
import re_ghidra_name_projection as name_projection  # noqa: E402


SCHEMA = "bea.ghidra.external-table-gap-boundary-live-authority.v1"
BASE_COMMIT = "2509f65d90c86d6328c0b584dcf5eb0e08e02471"
PROGRAM_NAME = "BEA.exe"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
PROGRAM_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
ANALYZE_HEADLESS = Path(
    r"D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC\support\analyzeHeadless.bat"
)

TARGETS = 79
BODY_BYTES = 9234
PRE_FUNCTIONS = 8201
POST_FUNCTIONS = 8280
PRE_INSTRUCTIONS = 550982
POST_INSTRUCTIONS = 550991
PRE_REFERENCES = 234537
POST_REFERENCES = 234495
EXTERNAL_INSTRUCTIONS = 3319
GHIDRA_BODY_INSTRUCTIONS = 3318
PRE_TOTAL_FUNCTIONS = 8425
POST_TOTAL_FUNCTIONS = 8504

PRE_PROJECT = {
    "fileCount": 19,
    "totalBytes": 186911621,
    "canonicalInventorySha256":
        "91776fb4a67579950afc4fb3b48ea8a866733628aecfdae7a2cb918c615fe211",
}
DB_18611 = (
    68288512,
    "6f45cdac7ae1f10987280f0ec247e6b5d6dcf866eae79e5982efa78dd68455ce",
)
DB_18612 = (
    68321280,
    "424775377ea0f40d9e429c9219b9310d427760acc40548dbc588ca285f932f7b",
)
PRE_OLD_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18611.gbf"
PRE_STABLE_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18612.gbf"
POST_ROLLING_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18613.gbf"

MANIFEST_REL = (
    "reverse-engineering/binary-analysis/"
    "external-table-gap-function-boundaries-2026-08-13.tsv"
)
CONSUMED_PROOF_REL = (
    "reverse-engineering/binary-analysis/"
    "d3dx-vec4cross-crossbuild-boundary-2026-08-13.md"
)
PROJECTION_REL = (
    "reverse-engineering/binary-analysis/"
    "ghidra-function-name-table-2026-08-13.tsv"
)
LIVE_LANE_REL = (
    "local-lab/ghidra-external-table-gap-boundary-live-promotion-20260814-v1"
)
AUTHORITY_RECEIPT_REL = (
    "local-lab/ghidra-external-table-gap-boundary-live-authority-20260814-v1/"
    "live-promotion.ready.json"
)
SCRATCH_LANE_REL = (
    "local-lab/ghidra-external-table-gap-boundary-current-scratch-20260814-v1"
)
SCRATCH_RECEIPT_REL = f"{SCRATCH_LANE_REL}/scratch-authority-v3.ready.json"
PROJECTION_SOURCE = f"{LIVE_LANE_REL}/runs/live-readback/functions.tsv"

PRE_FUNCTIONS_STAMP = (
    7109943,
    "2cc0b74f9284a3d6d59effa857cb6766bb78b08d50a7896d0dda8631f7c93314",
)
PRE_PROGRAM_STAMP = (
    1267,
    "be169e6bae9bbd32c822a70c180e43960336fd85ee8ad52f5f494090c0a1e636",
)
POST_FUNCTIONS_STAMP = (
    7161942,
    "c3942b9e340cef71b731290b845843697af5c53204449c51949b779e896272d6",
)
POST_PROGRAM_STAMP = (
    1267,
    "3e51ce1d5e926c632869b2058c9d89e91f48345a329a724ea9520570bd91212d",
)
BOUNDARY_STAMPS = {
    "dry": (
        21022,
        "a09a264de05e7394384eac466ad8ab1357252e1bd2c663a8ee7858db39462594",
    ),
    "apply": (
        29018,
        "97db9f391eb4a42a6a5f192ed37dfe3f29bdf6229c3437f17b1bd787a6007592",
    ),
    "readback": (
        29097,
        "2f4b23ac985f55562a1897dc3d4163bd546b8b752c1c302e7d35f1d6ae365eb9",
    ),
}
PRE_PROJECTION_STAMP = (
    504598,
    "c6084999cefebdb900ec752be5c4cb45ed1d7dcbdd086a53cbd207b91db84d20",
)
POST_PROJECTION_STAMP = (
    508242,
    "6e22a93a4792a2b5a9a6109a65e3b6460dc1ef6dc0606cc195a9a50e30ebdd68",
)
SCRATCH_RECEIPT_STAMP = (
    7597,
    "a8e196c3dee91c1fb0600ea63fb5096ad7665159066c7ca40f58a124be48a691",
)

EXPECTED_REPO_INPUTS = {
    MANIFEST_REL: (
        30020,
        "4293ebb936639299301985f128728b127ca60014693871a981d2324d47f2044f",
    ),
    CONSUMED_PROOF_REL: (
        4862,
        "1a7e705984830fee60f3d0710c0b017bd663ef27a805f1aa14beb0625863d306",
    ),
    "tools/GhidraApplyExternalTableGapBoundaries.java": (
        57413,
        "82e58540077a6099c433797d7150480f68e41eb995709f7df16ad2182a0c68eb",
    ),
    "tools/ExportFullFunctionInventory.java": (
        23963,
        "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197",
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
    "tools/ghidra_external_table_gap_boundary_scratch_authority.py": (
        43501,
        "d76879f2505780574c7aab295a7bd627630e718ada2153a80a8267958b552dcc",
    ),
    "tools/re_ghidra_name_projection.py": (
        6139,
        "d13d5f4d3b20cbd1e1baf24cd924d454c6c07b0bbf5517834c4089357f14ecdb",
    ),
}

RUN_LAYOUT = {
    "replica-a": {
        "dry": "replica-a-dry",
        "apply": "replica-a-apply",
        "readback": "replica-a-readback",
    },
    "replica-b": {
        "dry": "replica-b-dry",
        "apply": "replica-b-apply",
        "readback": "replica-b-readback",
    },
    "live": {
        "dry": "live-pre-readback",
        "apply": "live-apply",
        "readback": "live-readback",
    },
}
EXPECTED_RUN_NAMES = frozenset(
    run_name for modes in RUN_LAYOUT.values() for run_name in modes.values()
)

CLAIMS = (
    "The exact committed 79-target scratch authority still reproduces two persistent replicas, two rollback controls, two external-path controls, and its read-only recovery proof.",
    "Two fresh current-state replicas and the live project reproduce the same exact 79 structural additions and byte-identical full POST function/program exports.",
    "Every field of all 8,201 PRE function rows remains byte-identical; the POST-only address set is exactly the manifest and matches the scratch rows.",
    "The live lane contains exactly one writable live apply and exactly one successful live save between read-only PRE and separate read-only POST runs.",
    "An exact-root tracked-project inspection durably proves tracked remained PRE after POST recovery and before the later tracked POST inspection.",
    "The only project-tree transition is db.18611 removal and db.18613 addition; db.18612 and every other common file remain exact.",
    "Live, POST backup, tracked snapshot, and retained POST restore projects are byte-identical; all recovery copies reopen read-only and remain byte-stable.",
    "The tracked 8,280-row projection is mechanically reproduced from the exact live POST full inventory.",
    "This authority admits default-metadata function bodies only; names, signatures, semantics, runtime reachability, and rebuild parity remain unauthorized.",
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
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AuthorityError(f"invalid JSON for {label}: {path}") from exc
    require(isinstance(value, dict), f"{label} must be a JSON object")
    return value


def parse_utc(value: Any, label: str) -> datetime:
    require(isinstance(value, str) and value.endswith("Z"), f"{label} is not UTC")
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise AuthorityError(f"{label} is malformed") from exc


def mtime_utc(path: Path) -> datetime:
    return datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)


def utc_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def clean_path(path: Path) -> Path:
    return Path(os.path.abspath(path))


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def portable_path(value: Any, expected: str, label: str) -> None:
    require(isinstance(value, str) and value == expected, f"{label} path differs")
    require(
        "\\" not in value and ":" not in value and not value.startswith("/"),
        f"{label} is not repository-relative POSIX",
    )


def exact_absolute_path(value: Any, expected: Path, label: str) -> Path:
    require(isinstance(value, str) and value != "", f"{label} path is absent")
    actual = Path(value)
    require(actual.is_absolute(), f"{label} path is not absolute")
    actual = clean_path(actual)
    require(actual == clean_path(expected), f"{label} path differs")
    return actual


def exact_directory_entries(
    root: Path,
    *,
    expected_files: Iterable[str],
    expected_directories: Iterable[str],
    label: str,
) -> None:
    require(root.is_dir() and not scratch.is_reparse(root), f"missing/unsafe {label}: {root}")
    files = set(expected_files)
    directories = set(expected_directories)
    require(not files.intersection(directories), f"{label} expected entry types overlap")
    entries = {path.name: path for path in root.iterdir()}
    require(
        set(entries) == files | directories,
        f"unexpected {label} entry set: {sorted(entries)}",
    )
    for name in files:
        path = entries[name]
        require(path.is_file() and not scratch.is_reparse(path), f"unsafe {label} file: {name}")
    for name in directories:
        path = entries[name]
        require(
            path.is_dir() and not scratch.is_reparse(path),
            f"unsafe {label} directory: {name}",
        )


def ensure_portable(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            ensure_portable(key)
            ensure_portable(child)
    elif isinstance(value, list):
        for child in value:
            ensure_portable(child)
    elif isinstance(value, str):
        require(
            re.match(r"^[A-Za-z]:[\\/]", value) is None,
            f"aggregate payload contains an absolute Windows path: {value}",
        )
        require(
            not value.startswith("/"),
            f"aggregate payload contains an absolute POSIX path: {value}",
        )
        require(
            "\\" not in value,
            f"aggregate payload contains a non-portable separator: {value}",
        )


def exact_comparison(value: Mapping[str, Any], label: str) -> None:
    require(value.get("matches") is True, f"{label} did not match")
    for field in ("missingCount", "extraCount", "sizeDiffCount", "hashDiffCount"):
        require(value.get(field) == 0, f"{label} {field}")
    for field in ("missing", "extra", "sizeDifferences", "hashDifferences"):
        require(value.get(field) == [], f"{label} {field}")


@dataclass(frozen=True)
class Config:
    repo: Path
    scratch_repo: Path
    live_project: Path
    live_lane: Path
    pre_backup: Path
    post_backup: Path
    output: Path | None = None

    @property
    def authority_repo(self) -> Path:
        return Path(__file__).resolve().parents[1]

    @property
    def tracked_project(self) -> Path:
        return self.repo / "reverse-engineering/ghidra"

    @property
    def manifest(self) -> Path:
        return self.repo / MANIFEST_REL

    @property
    def projection(self) -> Path:
        return self.repo / PROJECTION_REL

    @property
    def scratch_lane(self) -> Path:
        return self.scratch_repo / SCRATCH_LANE_REL

    @property
    def scratch_receipt(self) -> Path:
        return self.scratch_repo / SCRATCH_RECEIPT_REL


def validate_layout(config: Config) -> None:
    require(
        config.live_lane == clean_path(config.repo / LIVE_LANE_REL),
        "live lane must use the canonical repository-relative path",
    )
    roots = {
        "live project": config.live_project,
        "tracked project": config.tracked_project,
        "scratch lane": config.scratch_lane,
        "live lane": config.live_lane,
        "PRE backup": config.pre_backup,
        "POST backup": config.post_backup,
    }
    for left_name, left in roots.items():
        for right_name, right in roots.items():
            if left_name >= right_name:
                continue
            require(
                not is_within(left, right) and not is_within(right, left),
                f"{left_name} and {right_name} must be disjoint",
            )
    require(config.pre_backup != config.post_backup, "PRE and POST backups differ")


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
        "canonicalization": (
            "sha256<TAB>bytes<TAB>relative-posix-path<LF>, relative-path order"
        ),
    }


def project_file_map(value: Mapping[str, Any]) -> dict[str, tuple[int, str]]:
    return {
        str(row["relative_path"]): (int(row["size"]), str(row["sha256"]))
        for row in value.get("files", [])
    }


def require_same_project(
    left: Mapping[str, Any], right: Mapping[str, Any], label: str
) -> None:
    require(project_without_root(left) == project_without_root(right), f"{label} bytes differ")


def require_pre_project(value: Mapping[str, Any], label: str) -> None:
    require(value.get("projectName") == "BEA", f"{label} project name")
    require(value.get("structurallyComplete") is True, f"{label} completeness")
    measured = project_summary(value)
    for key, expected in PRE_PROJECT.items():
        require(measured.get(key) == expected, f"{label} {key} differs")
    files = project_file_map(value)
    require(files.get(PRE_OLD_DB_PATH) == DB_18611, f"{label} db.18611 identity")
    require(files.get(PRE_STABLE_DB_PATH) == DB_18612, f"{label} db.18612 identity")
    require(POST_ROLLING_DB_PATH not in files, f"{label} unexpectedly contains db.18613")


def validate_post_transition(
    pre: Mapping[str, Any], post: Mapping[str, Any], label: str
) -> dict[str, Any]:
    require(post.get("projectName") == "BEA", f"{label} project name")
    require(post.get("structurallyComplete") is True, f"{label} completeness")
    require(post.get("fileCount") == PRE_PROJECT["fileCount"], f"{label} file count")
    pre_map = project_file_map(pre)
    post_map = project_file_map(post)
    removed = sorted(set(pre_map) - set(post_map))
    added = sorted(set(post_map) - set(pre_map))
    changed = sorted(
        path for path in set(pre_map) & set(post_map) if pre_map[path] != post_map[path]
    )
    require(removed == [PRE_OLD_DB_PATH], f"{label} removed paths")
    require(added == [POST_ROLLING_DB_PATH], f"{label} added paths")
    require(changed == [], f"{label} changed common files")
    require(post_map.get(PRE_STABLE_DB_PATH) == DB_18612, f"{label} stable db.18612")
    rolling = post_map.get(POST_ROLLING_DB_PATH)
    require(rolling is not None and rolling[0] > 0, f"{label} rolling db.18613")
    return {
        "removed": removed,
        "added": added,
        "changedCommonFiles": changed,
        "byteDelta": int(post["totalBytes"]) - int(pre["totalBytes"]),
        "stableDatabase": {
            "path": PRE_STABLE_DB_PATH,
            "bytes": DB_18612[0],
            "sha256": DB_18612[1],
        },
        "rollingDatabase": {
            "path": POST_ROLLING_DB_PATH,
            "bytes": rolling[0],
            "sha256": rolling[1],
        },
    }


def validate_repo_inputs(config: Config) -> dict[str, Any]:
    ledger: dict[str, Any] = {}
    for relative, expected in EXPECTED_REPO_INPUTS.items():
        ledger[relative] = verify_stamp(config.repo / relative, expected, relative)
    imported = {
        "authority-import/ghidra_project_backup.py": Path(project_backup.__file__).resolve(),
        "authority-import/ghidra_external_table_gap_boundary_scratch_authority.py":
            Path(scratch.__file__).resolve(),
        "authority-import/re_ghidra_name_projection.py": Path(name_projection.__file__).resolve(),
    }
    expected_imports = {
        "authority-import/ghidra_project_backup.py":
            EXPECTED_REPO_INPUTS["tools/ghidra_project_backup.py"],
        "authority-import/ghidra_external_table_gap_boundary_scratch_authority.py":
            EXPECTED_REPO_INPUTS[
                "tools/ghidra_external_table_gap_boundary_scratch_authority.py"
            ],
        "authority-import/re_ghidra_name_projection.py":
            EXPECTED_REPO_INPUTS["tools/re_ghidra_name_projection.py"],
    }
    for role, path in imported.items():
        ledger[role] = verify_stamp(path, expected_imports[role], role)
    return ledger


def validate_scratch(config: Config) -> dict[str, Any]:
    tool = config.scratch_repo / (
        "tools/ghidra_external_table_gap_boundary_scratch_authority.py"
    )
    verify_stamp(
        tool,
        EXPECTED_REPO_INPUTS[
            "tools/ghidra_external_table_gap_boundary_scratch_authority.py"
        ],
        "scratch-authority/tool",
    )
    receipt_stamp = verify_stamp(
        config.scratch_receipt,
        SCRATCH_RECEIPT_STAMP,
        "scratch-authority/ready.json",
    )
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, "-I", "-B", str(tool), "verify"],
        cwd=config.scratch_repo,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=900,
    )
    require(
        result.returncode == 0,
        f"scratch authority verify failed: {result.stderr.strip()}",
    )
    sentinel = (
        "EXTERNAL_TABLE_GAP_SCRATCH_AUTHORITY_VERIFIED "
        f"sha256={SCRATCH_RECEIPT_STAMP[1]} live_authorized=false"
    )
    require(result.stdout.count(sentinel) == 1, "scratch authority sentinel")
    recorded = load_json(config.scratch_receipt, "scratch authority receipt")
    require(recorded.get("schemaVersion") == scratch.SCHEMA, "scratch schema")
    require(recorded.get("verdict") == "SCRATCH_READY_LIVE_FORBIDDEN", "scratch verdict")
    expected_summary = {
        "targets": TARGETS,
        "bodyBytes": BODY_BYTES,
        "externalInstructions": EXTERNAL_INSTRUCTIONS,
        "ghidraBodyInstructions": GHIDRA_BODY_INSTRUCTIONS,
        "rankCounts": {"P0": 12, "P1": 20, "P2": 47},
        "preFunctions": PRE_FUNCTIONS,
        "postFunctions": POST_FUNCTIONS,
        "preInstructions": PRE_INSTRUCTIONS,
        "postInstructions": POST_INSTRUCTIONS,
        "instructionDelta": POST_INSTRUCTIONS - PRE_INSTRUCTIONS,
        "preReferences": PRE_REFERENCES,
        "postReferences": POST_REFERENCES,
        "referenceDelta": POST_REFERENCES - PRE_REFERENCES,
        "preservedPreFunctionRows": PRE_FUNCTIONS,
        "replicas": 2,
        "adverseControls": 2,
        "externalPathPreflights": 2,
        "actualProjectTrees": 2,
        "readonlyRestoreProofs": 1,
        "reusedExactPositiveReplicas": 2,
    }
    require(recorded.get("summary") == expected_summary, "scratch summary")
    require(
        recorded.get("liveMutationAuthorized") is False
        and recorded.get("trackedGhidraMutationAuthorized") is False,
        "scratch mutation boundary",
    )
    return {
        "receipt": receipt_stamp,
        "semanticVerifyRebuilt": True,
        "targets": TARGETS,
        "replicas": 2,
        "adverseControls": 2,
        "externalPathPreflights": 2,
    }


def preflight(config: Config) -> dict[str, Any]:
    validate_layout(config)
    repo_inputs = validate_repo_inputs(config)
    scratch_result = validate_scratch(config)
    require(not config.live_lane.exists(), "canonical live lane already exists")
    require(not config.pre_backup.exists(), "PRE backup destination already exists")
    require(not config.post_backup.exists(), "POST backup destination already exists")
    authority_root = (config.repo / AUTHORITY_RECEIPT_REL).parent
    require(not authority_root.exists(), "canonical aggregate authority root already exists")
    live = project_value(config.live_project)
    tracked = project_value(config.tracked_project)
    require_pre_project(live, "live PRE")
    require_pre_project(tracked, "tracked PRE")
    require_same_project(live, tracked, "live/tracked PRE")
    projection = verify_stamp(config.projection, PRE_PROJECTION_STAMP, PROJECTION_REL)
    return {
        "baseCommit": BASE_COMMIT,
        "repositoryInputs": repo_inputs,
        "scratchAuthority": scratch_result,
        "livePre": project_summary(live),
        "trackedPre": project_summary(tracked),
        "liveEqualsTracked": True,
        "preProjection": projection,
        "futureMutationAuthorized": False,
        "verdict": "PREFLIGHT_READY_MUTATION_NOT_AUTHORIZED",
    }


def load_targets(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    require(len(rows) == TARGETS, "target manifest count")
    entries = [int(str(row.get("retail_va", "")), 16) for row in rows]
    require(entries == sorted(entries), "target manifest order")
    require(len(set(entries)) == TARGETS, "target manifest duplicate entry")
    require(sum(int(row["body_bytes"]) for row in rows) == BODY_BYTES, "body bytes")
    require(
        sum(int(row["instruction_count"]) for row in rows) == EXTERNAL_INSTRUCTIONS,
        "external instructions",
    )
    require(
        {rank: sum(row["rank"] == rank for row in rows) for rank in ("P0", "P1", "P2")}
        == {"P0": 12, "P1": 20, "P2": 47},
        "rank partition",
    )
    occupied: list[tuple[int, int]] = []
    result: list[dict[str, str]] = []
    for index, source in enumerate(rows, 1):
        require(None not in source, f"malformed target row {index}")
        row = {str(key): str(value) for key, value in source.items()}
        row["candidateId"] = f"ETG-{index:03d}"
        for piece in row["body_ranges"].split(";"):
            start_text, end_text = piece.split("-", 1)
            start, end = int(start_text, 16), int(end_text, 16)
            require(start < end, f"empty target range {row['candidateId']}")
            require(
                all(end <= old_start or start >= old_end for old_start, old_end in occupied),
                f"overlapping target range {row['candidateId']}",
            )
            occupied.append((start, end))
        result.append(row)
    require(
        next(row for row in result if row["retail_va"].lower() == "0x005762dd")
        ["already_prepared_receipt"] == "true",
        "Vec4Cross proof consumption",
    )
    yuv = next(row for row in result if row["retail_va"].lower() == "0x0058862e")
    require(
        yuv["identity_status"] == "D3DX_SHARED_YUV_CODEC_DTOR_LINEAGE"
        and yuv["safe_name_candidate"]
        == "D3DX_COMPAT__CCodecYUVFamily__SharedScalarDeletingDtor",
        "YUV identity boundary",
    )
    return result


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
    try:
        text = raw.decode("utf-8")
        fields = tuple(lines[0].decode("utf-8").split("\t"))
    except UnicodeError as exc:
        raise AuthorityError(f"invalid UTF-8 TSV: {path}") from exc
    require(key in fields and len(fields) == len(set(fields)), f"bad TSV header: {path}")
    rows: dict[str, Mapping[str, str]] = {}
    raw_rows: dict[str, bytes] = {}
    order: list[str] = []
    reader = csv.DictReader(text.splitlines(), delimiter="\t")
    for number, (row, raw_line) in enumerate(zip(reader, lines[1:]), start=2):
        value = str(row.get(key) or "").lower()
        require(value and value not in rows and None not in row, f"bad {key} at {path}:{number}")
        rows[value] = dict(row)
        raw_rows[value] = raw_line
        order.append(value)
    require(len(order) == len(lines) - 1, f"TSV parse incomplete: {path}")
    return RawTable(fields, tuple(order), rows, raw_rows)


def validate_function_delta(
    pre_path: Path,
    post_path: Path,
    scratch_pre_path: Path,
    scratch_post_path: Path,
    targets: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    verify_stamp(pre_path, PRE_FUNCTIONS_STAMP, "live PRE functions")
    verify_stamp(post_path, POST_FUNCTIONS_STAMP, "live POST functions")
    require(pre_path.read_bytes() == scratch_pre_path.read_bytes(), "live/scratch PRE differs")
    require(post_path.read_bytes() == scratch_post_path.read_bytes(), "live/scratch POST differs")
    pre = raw_tsv(pre_path, "address")
    post = raw_tsv(post_path, "address")
    scratch_post = raw_tsv(scratch_post_path, "address")
    require(pre.fields == post.fields == scratch_post.fields, "function headers differ")
    require(len(pre.rows) == PRE_FUNCTIONS, "PRE function census")
    require(len(post.rows) == POST_FUNCTIONS, "POST function census")
    require(set(pre.rows) <= set(post.rows), "PRE function address destroyed")
    for address, before in pre.raw_rows.items():
        require(post.raw_rows.get(address) == before, f"PRE row changed at {address}")
    target_addresses = {str(row["retail_va"]).lower() for row in targets}
    created = set(post.rows) - set(pre.rows)
    require(created == target_addresses, "POST-only target set differs")
    for address in target_addresses:
        row = post.rows[address]
        require(
            row.get("name") == "FUN_" + address[2:]
            and row.get("nameSource") == "DEFAULT",
            f"target metadata differs at {address}",
        )
        require(
            post.raw_rows[address] == scratch_post.raw_rows.get(address),
            f"live/scratch target row differs at {address}",
        )
    return {
        "pre": stamp(pre_path, "live-lane/runs/live-pre-readback/functions.tsv"),
        "post": stamp(post_path, "live-lane/runs/live-readback/functions.tsv"),
        "preRowsByteIdentical": PRE_FUNCTIONS,
        "createdAddressesExactManifest": TARGETS,
        "fullPostByteIdenticalToScratch": True,
        "destroyed": 0,
    }


def validate_program_delta(
    pre_path: Path,
    post_path: Path,
    scratch_pre_path: Path,
    scratch_post_path: Path,
) -> dict[str, Any]:
    verify_stamp(pre_path, PRE_PROGRAM_STAMP, "live PRE program")
    verify_stamp(post_path, POST_PROGRAM_STAMP, "live POST program")
    require(pre_path.read_bytes() == scratch_pre_path.read_bytes(), "live/scratch PRE program")
    require(post_path.read_bytes() == scratch_post_path.read_bytes(), "live/scratch POST program")
    before = scratch.program_rows(pre_path)
    after = scratch.program_rows(post_path)
    require(
        before == scratch.PRE_PROGRAM | {
            key: value for key, value in before.items() if key.startswith("block:")
        },
        "PRE program metrics",
    )
    require(
        after == scratch.POST_PROGRAM | {
            key: value for key, value in after.items() if key.startswith("block:")
        },
        "POST program metrics",
    )
    require(set(before) == set(after), "program metric set differs")
    changed = {key for key in before if before[key] != after[key]}
    expected = {
        "functions",
        "instructions",
        "instructionLayoutSha256",
        "undefinedData",
        "symbolsDefaultOther",
        "references",
        "referencesSha256",
    }
    require(changed == expected, f"program changed metrics differ: {sorted(changed)}")
    return {
        "pre": stamp(pre_path, "live-lane/runs/live-pre-readback/program.tsv"),
        "post": stamp(post_path, "live-lane/runs/live-readback/program.tsv"),
        "changedMetrics": sorted(changed),
        "functions": {"before": PRE_FUNCTIONS, "after": POST_FUNCTIONS},
        "instructions": {"before": PRE_INSTRUCTIONS, "after": POST_INSTRUCTIONS},
        "references": {"before": PRE_REFERENCES, "after": POST_REFERENCES},
        "memoryUnchanged": before["memorySha256"] == after["memorySha256"],
        "definedDataUnchanged": before["definedDataSha256"] == after["definedDataSha256"],
        "storedNonFunctionSymbolsUnchanged":
            before["nonFunctionSymbolsSha256"] == after["nonFunctionSymbolsSha256"],
        "commentsUnchanged": before["commentsSha256"] == after["commentsSha256"],
    }


def validate_run_file_set(root: Path, mode: str, *, live: bool) -> None:
    expected = {"boundaries.ready.json", "boundaries.tsv", "ghidra.log"}
    if mode == "readback" or (live and mode == "dry"):
        expected |= {"functions.tsv", "program.tsv"}
    if live and mode == "readback":
        expected.add("inventory-diff.json")
    exact_directory_entries(
        root,
        expected_files=expected,
        expected_directories=(),
        label=f"run {root.name}",
    )


def validate_run_directory_set(live_lane: Path) -> None:
    exact_directory_entries(
        live_lane / "runs",
        expected_files=(),
        expected_directories=EXPECTED_RUN_NAMES,
        label="live runs root",
    )
    expected_logs = {f"runs/{name}/ghidra.log" for name in EXPECTED_RUN_NAMES}
    log_paths = list(live_lane.rglob("ghidra.log"))
    require(
        all(path.is_file() and not scratch.is_reparse(path) for path in log_paths),
        "live evidence contains an unsafe ghidra.log entry",
    )
    measured_logs = {path.relative_to(live_lane).as_posix() for path in log_paths}
    require(measured_logs == expected_logs, "live evidence ghidra.log set differs")


def validate_run_receipt(
    config: Config,
    run_name: str,
    mode: str,
    targets: list[dict[str, str]],
) -> datetime:
    root = config.live_lane / "runs" / run_name
    boundary_path = root / "boundaries.tsv"
    receipt = load_json(root / "boundaries.ready.json", f"{run_name} receipt")
    require(
        receipt.get("schemaVersion") == "bea.ghidra.external-table-gap-boundaries.v2",
        f"{run_name} schema",
    )
    require(receipt.get("mode") == mode, f"{run_name} mode")
    tool_rel = "tools/GhidraApplyExternalTableGapBoundaries.java"
    portable_path(receipt.get("tool", {}).get("path"), tool_rel, f"{run_name} tool")
    require(
        (receipt["tool"].get("bytes"), receipt["tool"].get("sha256"))
        == EXPECTED_REPO_INPUTS[tool_rel],
        f"{run_name} tool binding",
    )
    portable_path(receipt.get("manifest", {}).get("path"), MANIFEST_REL, f"{run_name} manifest")
    require(
        (receipt["manifest"].get("bytes"), receipt["manifest"].get("sha256"))
        == EXPECTED_REPO_INPUTS[MANIFEST_REL],
        f"{run_name} manifest binding",
    )
    portable_path(
        receipt.get("consumedProof", {}).get("path"),
        CONSUMED_PROOF_REL,
        f"{run_name} consumed proof",
    )
    require(
        (
            receipt["consumedProof"].get("bytes"),
            receipt["consumedProof"].get("sha256"),
        ) == EXPECTED_REPO_INPUTS[CONSUMED_PROOF_REL],
        f"{run_name} consumed-proof binding",
    )
    output_rel = f"{LIVE_LANE_REL}/runs/{run_name}/boundaries.tsv"
    portable_path(receipt.get("output", {}).get("path"), output_rel, f"{run_name} output")
    measured = verify_stamp(boundary_path, BOUNDARY_STAMPS[mode], f"{run_name} boundaries")
    require(
        (receipt["output"].get("bytes"), receipt["output"].get("sha256"))
        == (measured["bytes"], measured["sha256"]),
        f"{run_name} output binding",
    )
    scratch_boundaries = (
        config.scratch_lane / f"runs/replica-a-{mode}/boundaries.tsv"
    )
    require(
        boundary_path.read_bytes() == scratch_boundaries.read_bytes(),
        f"{run_name} differs from scratch {mode}",
    )
    require(receipt.get("program") == {
        "name": PROGRAM_NAME,
        "md5": PROGRAM_MD5,
        "sha256": PROGRAM_SHA256,
    }, f"{run_name} program identity")
    expected_counts = {
        "dry": {
            "targets": TARGETS,
            "externalInstructions": EXTERNAL_INSTRUCTIONS,
            "ghidraBodyInstructions": GHIDRA_BODY_INSTRUCTIONS,
            "functionsBefore": PRE_FUNCTIONS,
            "functionsAfter": PRE_FUNCTIONS,
            "instructionsBefore": PRE_INSTRUCTIONS,
            "instructionsAfter": PRE_INSTRUCTIONS,
        },
        "apply": {
            "targets": TARGETS,
            "externalInstructions": EXTERNAL_INSTRUCTIONS,
            "ghidraBodyInstructions": GHIDRA_BODY_INSTRUCTIONS,
            "functionsBefore": PRE_FUNCTIONS,
            "functionsAfter": POST_FUNCTIONS,
            "instructionsBefore": PRE_INSTRUCTIONS,
            "instructionsAfter": POST_INSTRUCTIONS,
        },
        "readback": {
            "targets": TARGETS,
            "externalInstructions": EXTERNAL_INSTRUCTIONS,
            "ghidraBodyInstructions": GHIDRA_BODY_INSTRUCTIONS,
            "functionsBefore": POST_FUNCTIONS,
            "functionsAfter": POST_FUNCTIONS,
            "instructionsBefore": POST_INSTRUCTIONS,
            "instructionsAfter": POST_INSTRUCTIONS,
        },
    }[mode]
    require(receipt.get("counts") == expected_counts, f"{run_name} counts")
    require(
        receipt.get("explicitBodySetsAuthorized") is True
        and receipt.get("postCountsPinned") is True
        and receipt.get("namesAuthorized") is False
        and receipt.get("metadataAuthorized") is False
        and receipt.get("separateReadbackRequired") is (mode != "readback"),
        f"{run_name} claim boundary",
    )
    scratch.verify_boundary_rows(boundary_path, mode, targets)
    return parse_utc(receipt.get("completedAtUtc"), f"{run_name} completedAtUtc")


def validate_run_log(path: Path, mode: str) -> dict[str, int]:
    text = path.read_text(encoding="utf-8")
    require(
        text.count(f"EXTERNAL_TABLE_GAP_BOUNDARIES_OK mode={mode}") == 1,
        f"{path.parent.name} success marker",
    )
    for marker in (
        "REPORT SCRIPT ERROR",
        "EXTERNAL_TABLE_GAP_BOUNDARIES_FAIL",
        "EXTERNAL_TABLE_GAP_BOUNDARIES_MUTATION_TAINTED",
        "Exception",
        "Traceback",
    ):
        require(marker not in text, f"{path.parent.name} error marker: {marker}")
    saves = text.count("Save succeeded for processed file: /BEA.exe")
    read_only = text.count("Processing read-only project file: /BEA.exe")
    writable = len(re.findall(r"Processing project file: /BEA\.exe", text))
    if mode == "apply":
        require((saves, read_only, writable) == (1, 0, 1), f"{path.parent.name} apply shape")
    else:
        require((saves, read_only, writable) == (0, 1, 0), f"{path.parent.name} read-only shape")
    return {
        "successfulSaves": saves,
        "readOnlyOpens": read_only,
        "writableOpens": writable,
    }


def validate_runs(
    config: Config,
    targets: list[dict[str, str]],
) -> tuple[dict[str, Any], dict[str, datetime]]:
    times: dict[str, datetime] = {}
    summaries: dict[str, Any] = {}
    live_saves = 0
    validate_run_directory_set(config.live_lane)
    for owner, modes in RUN_LAYOUT.items():
        owner_summary: dict[str, Any] = {}
        for mode, run_name in modes.items():
            root = config.live_lane / "runs" / run_name
            validate_run_file_set(root, mode, live=owner == "live")
            times[f"{owner}.{mode}.receipt"] = validate_run_receipt(
                config, run_name, mode, targets
            )
            log_shape = validate_run_log(root / "ghidra.log", mode)
            if owner == "live":
                live_saves += log_shape["successfulSaves"]
            owner_summary[mode] = {
                "receipt": stamp(
                    root / "boundaries.ready.json",
                    f"live-lane/runs/{run_name}/boundaries.ready.json",
                ),
                "boundaries": stamp(
                    root / "boundaries.tsv",
                    f"live-lane/runs/{run_name}/boundaries.tsv",
                ),
                "log": stamp(root / "ghidra.log", f"live-lane/runs/{run_name}/ghidra.log"),
                **log_shape,
            }
        summaries[owner] = owner_summary
    require(live_saves == 1, "live lane did not contain exactly one successful save")

    scratch_pre_functions = config.scratch_lane / "runs/base-inventory/functions.tsv"
    scratch_pre_program = config.scratch_lane / "runs/base-inventory/program.tsv"
    scratch_post_functions = config.scratch_lane / "runs/replica-a-readback/functions.tsv"
    scratch_post_program = config.scratch_lane / "runs/replica-a-readback/program.tsv"
    pre_functions = config.live_lane / "runs/live-pre-readback/functions.tsv"
    pre_program = config.live_lane / "runs/live-pre-readback/program.tsv"
    post_functions = config.live_lane / "runs/live-readback/functions.tsv"
    post_program = config.live_lane / "runs/live-readback/program.tsv"
    function_delta = validate_function_delta(
        pre_functions, post_functions, scratch_pre_functions, scratch_post_functions, targets
    )
    program_delta = validate_program_delta(
        pre_program, post_program, scratch_pre_program, scratch_post_program
    )
    diff_path = config.live_lane / "runs/live-readback/inventory-diff.json"
    scratch.verify_diff(diff_path, targets)
    for replica in ("replica-a", "replica-b"):
        root = config.live_lane / "runs" / f"{replica}-readback"
        require(
            (root / "functions.tsv").read_bytes() == post_functions.read_bytes(),
            f"{replica} full functions differ from live POST",
        )
        require(
            (root / "program.tsv").read_bytes() == post_program.read_bytes(),
            f"{replica} full program differs from live POST",
        )
        times[f"{replica}.readback.complete"] = mtime_utc(root / "program.tsv")
    times["live.dry.complete"] = mtime_utc(pre_program)
    times["live.readback.complete"] = mtime_utc(post_program)
    times["live.inventoryDiff.complete"] = mtime_utc(diff_path)
    return {
        "runs": summaries,
        "liveSuccessfulSaves": live_saves,
        "functionDelta": function_delta,
        "programDelta": program_delta,
        "inventoryDiff": stamp(diff_path, "live-lane/runs/live-readback/inventory-diff.json"),
    }, times


def validate_inspect(
    path: Path,
    expected_root: Path,
    expected: Mapping[str, Any],
    label: str,
) -> datetime:
    value = load_json(path, label)
    require(value.get("schemaVersion") == project_backup.SCHEMA_VERSION, f"{label} schema")
    manifest = value.get("manifest", {})
    exact_absolute_path(manifest.get("root"), expected_root, f"{label} root")
    require_same_project(manifest, expected, label)
    return parse_utc(value.get("createdAtUtc"), f"{label} createdAtUtc")


def validate_backup_manifest(
    path: Path,
    expected: Mapping[str, Any],
    label: str,
) -> datetime:
    value = load_json(path, label)
    require(value.get("schemaVersion") == project_backup.SCHEMA_VERSION, f"{label} schema")
    require(value.get("sourceStable") is True, f"{label} source stability")
    exact_comparison(value.get("copyComparison", {}), f"{label} copy")
    require_same_project(value.get("source", {}), expected, f"{label} source")
    require_same_project(value.get("destination", {}), expected, f"{label} destination")
    require(value.get("readonlyOpen") is None, f"{label} unexpectedly opened Ghidra")
    return parse_utc(value.get("createdAtUtc"), f"{label} createdAtUtc")


def validate_restore_execution_paths(
    config: Config,
    value: Mapping[str, Any],
    retained_project: Path,
    expected_source_root: Path,
    label: str,
) -> None:
    source = value.get("source", {})
    exact_absolute_path(source.get("root"), expected_source_root, f"{label} source root")
    exact_absolute_path(value.get("probeCopy"), retained_project, f"{label} probe copy")
    opened = value.get("readonlyOpen", {})
    expected_argv = project_backup.build_open_command(
        ANALYZE_HEADLESS,
        retained_project,
        "BEA",
        PROGRAM_NAME,
        config.repo / "tools",
        PROGRAM_MD5,
        PROGRAM_SHA256,
    )
    require(opened.get("commandArgv") == expected_argv, f"{label} open command differs")


def validate_restore(
    config: Config,
    receipt_name: str,
    probe_root_name: str,
    expected_source_root: Path,
    expected: Mapping[str, Any],
    expected_functions: int,
    label: str,
) -> tuple[dict[str, Any], datetime]:
    lane = config.live_lane
    receipt_path = lane / receipt_name
    value = load_json(receipt_path, label)
    require(value.get("schemaVersion") == project_backup.SCHEMA_VERSION, f"{label} schema")
    require(value.get("sourceStable") is True, f"{label} source stability")
    require(
        value.get("probeCopyDisposition") == "RETAINED_AT_VERIFICATION",
        f"{label} probe disposition",
    )
    require_same_project(value.get("source", {}), expected, f"{label} source")
    exact_comparison(value.get("copyComparison", {}), f"{label} copy")

    opened = value.get("readonlyOpen", {})
    require(
        opened.get("opened") is True
        and opened.get("contentStable") is True
        and opened.get("exitCode") == 0,
        f"{label} open result",
    )
    require(
        opened.get("expectedProgramMd5") == PROGRAM_MD5
        and opened.get("expectedProgramSha256") == PROGRAM_SHA256
        and opened.get("observedProgramName") == PROGRAM_NAME
        and opened.get("observedProgramMd5") == PROGRAM_MD5
        and opened.get("observedProgramSha256") == PROGRAM_SHA256
        and opened.get("observedFunctionCount") == expected_functions,
        f"{label} observed program",
    )
    exact_comparison(opened.get("postOpenComparison", {}), f"{label} post-open")
    expected_log = receipt_name.replace(".json", ".open-probe.log")
    log_claim = opened.get("probeLog", {})
    portable_path(log_claim.get("path"), expected_log, f"{label} probe log")
    log_path = lane / expected_log
    log_stamp = stamp(log_path, f"live-lane/{expected_log}")
    require(
        (log_claim.get("bytes"), log_claim.get("sha256"))
        == (log_stamp["bytes"], log_stamp["sha256"]),
        f"{label} probe-log binding",
    )
    text = log_path.read_text(encoding="utf-8")
    sentinel = (
        f"GHIDRA_PROJECT_OPEN_PROBE_OK program={PROGRAM_NAME} md5={PROGRAM_MD5} "
        f"sha256={PROGRAM_SHA256} functions={expected_functions}"
    )
    require(text.count(sentinel) == 1, f"{label} success sentinel")
    require(
        text.count("Processing read-only project file: /BEA.exe") == 1,
        f"{label} read-only process marker",
    )
    for marker in project_backup.GHIDRA_OPEN_ERROR_MARKERS:
        require(marker not in text, f"{label} error marker: {marker}")

    probe_root = lane / probe_root_name
    entries = list(probe_root.iterdir()) if probe_root.is_dir() else []
    require(
        len(entries) == 1
        and entries[0].is_dir()
        and not scratch.is_reparse(probe_root)
        and not scratch.is_reparse(entries[0]),
        f"{label} retained probe topology",
    )
    retained_path = entries[0]
    validate_restore_execution_paths(
        config, value, retained_path, expected_source_root, label
    )
    retained_project = project_value(retained_path)
    require_same_project(retained_project, expected, f"{label} retained probe")
    retained_manifest = retained_path / "backup_manifest.json"
    validate_backup_manifest(retained_manifest, expected, f"{label} retained copy")
    return {
        "receipt": stamp(receipt_path, f"live-lane/{receipt_name}"),
        "probeLog": log_stamp,
        "retainedProject": project_summary(retained_project),
        "retainedCopyReceipt": stamp(
            retained_manifest,
            f"live-lane/{probe_root_name}/retained/backup_manifest.json",
        ),
        "observedInternalAndExternalFunctions": expected_functions,
        "readOnly": True,
        "contentStable": True,
    }, parse_utc(value.get("verifiedAtUtc"), f"{label} verifiedAtUtc")


def validate_live_projects(
    config: Config,
    *,
    require_tracked_post: bool,
) -> tuple[dict[str, Any], dict[str, datetime]]:
    pre = project_value(config.pre_backup)
    post = project_value(config.post_backup)
    live = project_value(config.live_project)
    tracked = project_value(config.tracked_project)
    require_pre_project(pre, "PRE backup")
    transition = validate_post_transition(pre, post, "POST backup")
    validate_post_transition(pre, live, "live POST")
    require_same_project(live, post, "live/POST backup")
    if require_tracked_post:
        validate_post_transition(pre, tracked, "tracked POST")
        require_same_project(tracked, post, "tracked/POST backup")
    else:
        require_pre_project(tracked, "tracked still PRE")

    times: dict[str, datetime] = {}
    times["live.pre.inspect"] = validate_inspect(
        config.live_lane / "live-pre-inspect.json",
        config.live_project,
        pre,
        "live PRE inspect",
    )
    times["tracked.pre.inspect"] = validate_inspect(
        config.live_lane / "tracked-pre-inspect.json",
        config.tracked_project,
        pre,
        "tracked PRE inspect",
    )
    times["live.beforeApply.inspect"] = validate_inspect(
        config.live_lane / "live-before-apply-inspect.json",
        config.live_project,
        pre,
        "live before-apply inspect",
    )
    times["live.post.inspect"] = validate_inspect(
        config.live_lane / "live-post-inspect.json",
        config.live_project,
        post,
        "live POST inspect",
    )
    times["tracked.stillPre.inspect"] = validate_inspect(
        config.live_lane / "tracked-still-pre-inspect.json",
        config.tracked_project,
        pre,
        "tracked still-PRE inspect",
    )

    pre_manifest = config.pre_backup / "backup_manifest.json"
    post_manifest = config.post_backup / "backup_manifest.json"
    times["pre.backup.created"] = validate_backup_manifest(
        pre_manifest, pre, "PRE backup manifest"
    )
    times["post.backup.created"] = validate_backup_manifest(
        post_manifest, post, "POST backup manifest"
    )
    pre_restore, times["pre.restore.verified"] = validate_restore(
        config,
        "pre-backup-restore.ready.json",
        "pre-backup-restore-probe",
        config.pre_backup,
        pre,
        PRE_TOTAL_FUNCTIONS,
        "PRE restore",
    )
    post_restore, times["post.restore.verified"] = validate_restore(
        config,
        "post-backup-restore.ready.json",
        "post-backup-restore-probe",
        config.post_backup,
        post,
        POST_TOTAL_FUNCTIONS,
        "POST restore",
    )

    replicas: dict[str, Any] = {}
    post_map = project_file_map(post)
    for replica in ("replica-a", "replica-b"):
        root = config.live_lane / "projects" / replica
        current = project_value(root)
        validate_post_transition(pre, current, f"{replica} persisted project")
        current_map = project_file_map(current)
        require(set(current_map) == set(post_map), f"{replica} path set")
        require(
            all(
                current_map[path] == post_map[path]
                for path in post_map
                if path != POST_ROLLING_DB_PATH
            ),
            f"{replica} changed a non-rolling project file",
        )
        require(
            current_map[POST_ROLLING_DB_PATH][0] == post_map[POST_ROLLING_DB_PATH][0],
            f"{replica} rolling database size",
        )
        manifest_path = root / "backup_manifest.json"
        times[f"{replica}.copy.created"] = validate_backup_manifest(
            manifest_path, pre, f"{replica} initial copy"
        )
        replicas[replica] = {
            "initialCopy": project_summary(pre),
            "persistedProject": project_summary(current),
            "onlyRollingDatabaseSerializationMayDifferFromLivePost": True,
            "backupReceipt": stamp(
                manifest_path,
                f"live-lane/projects/{replica}/backup_manifest.json",
            ),
        }

    restores: dict[str, Any] = {"pre": pre_restore, "post": post_restore}
    if require_tracked_post:
        times["tracked.post.inspect"] = validate_inspect(
            config.live_lane / "tracked-post-inspect.json",
            config.tracked_project,
            post,
            "tracked POST inspect",
        )
        tracked_restore, times["tracked.restore.verified"] = validate_restore(
            config,
            "tracked-post-restore.ready.json",
            "tracked-post-restore-probe",
            config.tracked_project,
            post,
            POST_TOTAL_FUNCTIONS,
            "tracked POST restore",
        )
        restores["trackedPost"] = tracked_restore

    return {
        "pre": project_summary(pre),
        "post": project_summary(post),
        "liveEqualsPost": True,
        "trackedState": "POST_EXACT" if require_tracked_post else "PRE_UNCHANGED",
        "postBackupEqualsPost": True,
        "trackedStillPreAfterPostRecovery": True,
        "rollingDelta": transition,
        "replicas": replicas,
        "restores": restores,
        "backupReceipts": {
            "pre": stamp(pre_manifest, "pre-backup/backup_manifest.json"),
            "post": stamp(post_manifest, "post-backup/backup_manifest.json"),
        },
    }, times


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
    require(
        (len(expected), hashlib.sha256(expected).hexdigest()) == POST_PROJECTION_STAMP,
        "mechanical projection identity",
    )
    require(retained.read_bytes() == expected, "retained projection is not mechanical")
    require(config.projection.read_bytes() == expected, "tracked projection is not mechanical")
    rows = sum(1 for line in expected.splitlines() if line and not line.startswith(b"#")) - 1
    require(rows == POST_FUNCTIONS, "projection row count")
    result = {
        "rows": rows,
        "bytes": len(expected),
        "sha256": hashlib.sha256(expected).hexdigest(),
        "sourceInventory": stamp(inventory, "live-lane/runs/live-readback/functions.tsv"),
        "retained": stamp(retained, "live-lane/ghidra-function-name-table-2026-08-13.tsv"),
        "tracked": stamp(config.projection, PROJECTION_REL),
        "sourceLabel": PROJECTION_SOURCE,
    }
    return result, min(mtime_utc(retained), mtime_utc(config.projection))


def require_before(
    events: Mapping[str, datetime],
    left: str,
    right: str,
) -> None:
    require(events[left] < events[right], f"chronology does not advance: {left} -> {right}")


def validate_chronology(
    project_times: Mapping[str, datetime],
    run_times: Mapping[str, datetime],
    projection_time: datetime | None = None,
) -> list[dict[str, str]]:
    events = {**project_times, **run_times}
    if projection_time is not None:
        events["projection.complete"] = projection_time

    edges: list[tuple[str, str]] = [
        ("live.pre.inspect", "pre.backup.created"),
        ("tracked.pre.inspect", "pre.backup.created"),
        ("pre.backup.created", "pre.restore.verified"),
        ("pre.restore.verified", "replica-a.copy.created"),
        ("pre.restore.verified", "replica-b.copy.created"),
    ]
    for replica in ("replica-a", "replica-b"):
        edges.extend([
            (f"{replica}.copy.created", f"{replica}.dry.receipt"),
            (f"{replica}.dry.receipt", f"{replica}.apply.receipt"),
            (f"{replica}.apply.receipt", f"{replica}.readback.receipt"),
            (f"{replica}.readback.receipt", f"{replica}.readback.complete"),
            (f"{replica}.readback.complete", "live.dry.receipt"),
        ])
    for dry_owner in ("replica-a", "replica-b"):
        for apply_owner in ("replica-a", "replica-b"):
            edges.append((f"{dry_owner}.dry.receipt", f"{apply_owner}.apply.receipt"))
    for apply_owner in ("replica-a", "replica-b"):
        for readback_owner in ("replica-a", "replica-b"):
            edges.append(
                (f"{apply_owner}.apply.receipt", f"{readback_owner}.readback.receipt")
            )
    edges.extend([
        ("live.dry.receipt", "live.dry.complete"),
        ("live.dry.complete", "live.beforeApply.inspect"),
        ("live.beforeApply.inspect", "live.apply.receipt"),
        ("live.apply.receipt", "live.readback.receipt"),
        ("live.readback.receipt", "live.readback.complete"),
        ("live.readback.complete", "live.inventoryDiff.complete"),
        ("live.inventoryDiff.complete", "live.post.inspect"),
        ("live.post.inspect", "post.backup.created"),
        ("post.backup.created", "post.restore.verified"),
        ("post.restore.verified", "tracked.stillPre.inspect"),
    ])
    if projection_time is not None:
        edges.extend([
            ("tracked.stillPre.inspect", "tracked.post.inspect"),
            ("tracked.post.inspect", "tracked.restore.verified"),
            ("tracked.restore.verified", "projection.complete"),
        ])
    for left, right in edges:
        require_before(events, left, right)
    return [
        {"event": name, "atUtc": utc_text(events[name])}
        for name in sorted(events, key=lambda item: (events[item], item))
    ]


def expected_live_lane_topology(final: bool) -> tuple[set[str], set[str]]:
    files = {
        "live-pre-inspect.json",
        "tracked-pre-inspect.json",
        "pre-backup-restore.ready.json",
        "pre-backup-restore.ready.open-probe.log",
        "live-before-apply-inspect.json",
        "live-post-inspect.json",
        "post-backup-restore.ready.json",
        "post-backup-restore.ready.open-probe.log",
        "tracked-still-pre-inspect.json",
    }
    directories = {
        "pre-backup-restore-probe",
        "post-backup-restore-probe",
        "projects",
        "runs",
    }
    if final:
        files |= {
            "tracked-post-inspect.json",
            "tracked-post-restore.ready.json",
            "tracked-post-restore.ready.open-probe.log",
            "ghidra-function-name-table-2026-08-13.tsv",
        }
        directories.add("tracked-post-restore-probe")
    return files, directories


def validate_live_lane_topology(config: Config, *, final: bool) -> None:
    files, directories = expected_live_lane_topology(final)
    exact_directory_entries(
        config.live_lane,
        expected_files=files,
        expected_directories=directories,
        label="live evidence root",
    )
    exact_directory_entries(
        config.live_lane / "projects",
        expected_files=(),
        expected_directories=("replica-a", "replica-b"),
        label="replica projects root",
    )
    validate_run_directory_set(config.live_lane)


def validate_small_artifact_set(config: Config, *, final: bool) -> dict[str, Any]:
    validate_live_lane_topology(config, final=final)
    relative = [
        "live-pre-inspect.json",
        "tracked-pre-inspect.json",
        "pre-backup-restore.ready.json",
        "pre-backup-restore.ready.open-probe.log",
        "live-before-apply-inspect.json",
        "live-post-inspect.json",
        "post-backup-restore.ready.json",
        "post-backup-restore.ready.open-probe.log",
        "tracked-still-pre-inspect.json",
    ]
    if final:
        relative += [
            "tracked-post-inspect.json",
            "tracked-post-restore.ready.json",
            "tracked-post-restore.ready.open-probe.log",
            "ghidra-function-name-table-2026-08-13.tsv",
        ]
    ledger = {
        name: stamp(config.live_lane / name, f"live-lane/{name}")
        for name in relative
    }
    for owner, modes in RUN_LAYOUT.items():
        for mode, run_name in modes.items():
            root = config.live_lane / "runs" / run_name
            names = ["boundaries.ready.json", "boundaries.tsv", "ghidra.log"]
            if mode == "readback" or (owner == "live" and mode == "dry"):
                names += ["functions.tsv", "program.tsv"]
            if owner == "live" and mode == "readback":
                names += ["inventory-diff.json"]
            for name in names:
                role = f"runs/{run_name}/{name}"
                ledger[role] = stamp(root / name, f"live-lane/{role}")
    return ledger


def build_live_phase(config: Config) -> dict[str, Any]:
    validate_layout(config)
    repo_inputs = validate_repo_inputs(config)
    scratch_result = validate_scratch(config)
    targets = load_targets(config.manifest)
    projects, project_times = validate_live_projects(config, require_tracked_post=False)
    runs, run_times = validate_runs(config, targets)
    chronology = validate_chronology(project_times, run_times)
    value = {
        "baseCommit": BASE_COMMIT,
        "program": {"name": PROGRAM_NAME, "md5": PROGRAM_MD5, "sha256": PROGRAM_SHA256},
        "artifactLedger": {
            "repository": repo_inputs,
            "liveLane": validate_small_artifact_set(config, final=False),
        },
        "scratchAuthority": scratch_result,
        "projectsAndRecovery": projects,
        "liveAndReplicaRuns": runs,
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
    targets = load_targets(config.manifest)
    projects, project_times = validate_live_projects(config, require_tracked_post=True)
    runs, run_times = validate_runs(config, targets)
    projection, projection_time = validate_projection(config)
    chronology = validate_chronology(project_times, run_times, projection_time)
    value = {
        "baseCommit": BASE_COMMIT,
        "program": {"name": PROGRAM_NAME, "md5": PROGRAM_MD5, "sha256": PROGRAM_SHA256},
        "artifactLedger": {
            "repository": repo_inputs,
            "liveLane": validate_small_artifact_set(config, final=True),
        },
        "scratchAuthority": scratch_result,
        "projectsAndRecovery": projects,
        "liveAndReplicaRuns": runs,
        "projection": projection,
        "chronology": chronology,
        "claims": list(CLAIMS),
        "verdict": "LIVE_PROMOTION_REPRODUCED",
    }
    ensure_portable(value)
    return value


def validate_output(config: Config, *, sealing: bool) -> None:
    require(config.output is not None, "aggregate output is required")
    output = clean_path(config.output)
    require(
        output == clean_path(config.authority_repo / AUTHORITY_RECEIPT_REL),
        "aggregate receipt must use the canonical authority path",
    )
    forbidden = (
        config.live_lane,
        config.scratch_lane,
        config.live_project,
        config.pre_backup,
        config.post_backup,
        config.tracked_project,
    )
    require(
        not any(is_within(output, clean_path(root)) for root in forbidden),
        "aggregate receipt overlaps an evidence or project root",
    )
    if not sealing:
        require(output.is_file(), "saved aggregate receipt is absent")
        return
    local_lab = clean_path(config.authority_repo / "local-lab")
    require(is_within(output, local_lab), "aggregate receipt must be under authority local-lab")
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
            "tools/ghidra_external_table_gap_boundary_live_authority.py",
        ),
        "evidence": build_final(config),
        "ghidraOpenedByAuthority": False,
        "liveGhidraMutatedByAuthority": False,
        "trackedGhidraMutatedByAuthority": False,
        "futureMutationAuthorized": False,
    }
    ensure_portable(value)
    assert config.output is not None
    atomic_new_json(config.output, value)
    print(
        "EXTERNAL_TABLE_GAP_LIVE_AUTHORITY_READY "
        f"receipt_sha256={sha256_file(config.output)} functions={POST_FUNCTIONS} "
        f"targets={TARGETS}"
    )


def verify(config: Config) -> None:
    validate_output(config, sealing=False)
    assert config.output is not None
    recorded = load_json(config.output, "aggregate authority receipt")
    require(recorded.get("schemaVersion") == SCHEMA, "aggregate schema")
    parse_utc(recorded.get("completedAtUtc"), "aggregate completedAtUtc")
    require(
        recorded.get("authorityTool") == stamp(
            Path(__file__).resolve(),
            "tools/ghidra_external_table_gap_boundary_live_authority.py",
        ),
        "aggregate authority-tool binding",
    )
    require(
        recorded.get("ghidraOpenedByAuthority") is False
        and recorded.get("liveGhidraMutatedByAuthority") is False
        and recorded.get("trackedGhidraMutatedByAuthority") is False
        and recorded.get("futureMutationAuthorized") is False,
        "aggregate mutation boundary",
    )
    require(recorded.get("evidence") == build_final(config), "aggregate evidence differs")
    ensure_portable(recorded)
    print(
        "EXTERNAL_TABLE_GAP_LIVE_AUTHORITY_VERIFIED "
        f"receipt_sha256={sha256_file(config.output)} functions={POST_FUNCTIONS} "
        f"targets={TARGETS}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("preflight", "check-live", "seal", "verify"))
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--scratch-repo", type=Path, required=True)
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
            args.repo,
            args.scratch_repo,
            args.live_project,
            args.live_lane,
            args.pre_backup,
            args.post_backup,
        )),
        clean_path(args.output) if args.output is not None else None,
    )
    if args.command == "preflight":
        require(config.output is None, "preflight does not accept --output")
        result = preflight(config)
        print(
            "EXTERNAL_TABLE_GAP_LIVE_PREFLIGHT_READY "
            f"pre_project_sha256={result['livePre']['canonicalInventorySha256']} "
            f"scratch_receipt_sha256={SCRATCH_RECEIPT_STAMP[1]} "
            "mutation_authorized=false"
        )
    elif args.command == "check-live":
        require(config.output is None, "check-live does not accept --output")
        result = build_live_phase(config)
        print(
            "EXTERNAL_TABLE_GAP_LIVE_PHASE_VERIFIED "
            f"post_functions={POST_FUNCTIONS} targets={TARGETS} "
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
        name_projection.ProjectionError,
        scratch.AuthorityError,
    ) as exc:
        print(f"EXTERNAL_TABLE_GAP_LIVE_AUTHORITY_REFUSED reason={exc}", file=sys.stderr)
        raise SystemExit(1)
