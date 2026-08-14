#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reproduce and seal the completed CRT23 P0 live promotion.

This authority never launches Ghidra and never writes either project.  ``seal``
has one create-new write: a portable aggregate receipt after independently
replaying the retained ceremony, project, backup, projection, and accounting
evidence.  ``verify`` recomputes that receipt from the saved artifacts and the
current live/tracked POST projects.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping


sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import ghidra_project_backup as project_backup  # noqa: E402
import re_ghidra_name_projection as name_projection  # noqa: E402


SCHEMA = "bea.ghidra.crt-p0-boundary-live-authority.v2"
POLICY = "LIVE_PROMOTION_VERIFIED"
BASE_COMMIT = "e1e25d4956d7df325aba12a164e32224df5ace48"
PROGRAM_NAME = "BEA.exe"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
PROGRAM_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
ANALYZE_HEADLESS = Path(
    r"D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC\support\analyzeHeadless.bat"
)

TARGETS = 23
BODY_RANGES = 24
BODY_BYTES = 1131
EXTERNAL_INSTRUCTIONS = 312
PRE_FUNCTIONS = 8304
POST_FUNCTIONS = 8327
PRE_TOTAL_FUNCTIONS = 8528
POST_TOTAL_FUNCTIONS = 8551
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
POST_PROJECT = {
    "fileCount": 19,
    "totalBytes": 187009925,
    "canonicalInventorySha256":
        "61f77b70fdf807c960a9441ea8e5c4a5b5bd6281675864089a52d61481432f1f",
}
DB_18614 = (
    68337664,
    "d7f0011ea337f58b710415d5664e73d91ca9f1f61e20a836278d3e71b71b2865",
)
DB_18615 = (
    68354048,
    "6c2fc2f12394cf7b63f4f335173ba0a19b52b92c50dc4d2da987170501bc9681",
)
DB_18616 = (
    68354048,
    "f0d4988cfa1f36529ed3687816e231bfcc8323240e7d3f9837de48941b8f64fc",
)
PRE_OLD_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18614.gbf"
STABLE_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18615.gbf"
POST_ROLLING_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18616.gbf"

LIVE_LANE_REL = Path(
    "local-lab/ghidra-crt23-p0-boundary-live-promotion-db18615-20260814-v2"
)
PREP_LANE_REL = Path("local-lab/ghidra-crt23-p0-boundary-live-prep-db18615-v4")
MANIFEST_REL = Path(
    "reverse-engineering/binary-analysis/"
    "crt-runtime-p0-function-boundaries-2026-08-14.tsv"
)
PROJECTION_REL = Path(
    "reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-13.tsv"
)
PROJECTION_SOURCE = (
    "local-lab/ghidra-crt23-p0-boundary-live-promotion-db18615-20260814-v2/"
    "runs/live-readback/functions.tsv"
)
RECEIPT_NAME = "live-promotion.ready.json"

EXPECTED_REPO_INPUTS: dict[str, tuple[int, str]] = {
    "tools/GhidraApplyCrtP0BoundariesV4.java": (
        57278,
        "ac003bde10aea75cdf6849385017e15ef80c87e199ebeedf703108fb64334cc8",
    ),
    MANIFEST_REL.as_posix(): (
        6176,
        "c60359ecfd58e7c97c45a45e1b83d034e6cc104c222781f6f611e158b459d7df",
    ),
    "tools/ghidra_crt_p0_boundary_live_preparation_v2.py": (
        34889,
        "ad59a84a59705a54be1e6a72313978b1b6822460b1b6855e502c740d351002e6",
    ),
    "tools/ghidra_project_backup.py": (
        27502,
        "0f426982916f0aab982efe54664342a5d34607c2f89707159ecf6c07e205ad58",
    ),
    "tools/re_ghidra_name_projection.py": (
        6139,
        "d13d5f4d3b20cbd1e1baf24cd924d454c6c07b0bbf5517834c4089357f14ecdb",
    ),
}

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
POST_BODY_RANGES_STAMP = (
    1205737,
    "46138dc9b81ce2d0f835994f38581ba07564ddf17a7774ddbedfdb2e3d33e335",
)
POST_DIRECT_CALLS_STAMP = (
    1397680,
    "159f7c89aae54df927186d71263941b5f0857debe09556097820f098da8fa9d8",
)
POST_PARITY_STAMP = (
    767,
    "485f9b748e267533dce022d3ceb54f847e64eb0035d3a1b7faa1459972accf0a",
)
POST_INVENTORY_DIFF_STAMP = (
    5079,
    "82a36f4c008cffd4007ba43d614eb20f47139f538f059c2bf1d45d80fbf8d1f5",
)
POST_PROJECTION_STAMP = (
    510429,
    "17c7153cca64cf6b887dc0bd8d6a7576cfdcd41ce81528c516065ef7e9fa041c",
)

EXPECTED_RUN_FILES = {
    "live-pre-readback": {
        "boundaries.ready.json", "boundaries.tsv", "functions.tsv", "ghidra.log",
        "listing-state.tsv", "program.tsv",
    },
    "live-apply": {"boundaries.ready.json", "boundaries.tsv", "ghidra.log"},
    "live-readback": {
        "body-ranges.tsv", "boundaries.ready.json", "boundaries.tsv",
        "direct-calls.tsv", "functions.tsv", "ghidra.log", "inventory-diff.json",
        "listing-state.tsv", "parity-graph.ready.json", "program.tsv",
    },
}
EXPECTED_ACCOUNTING_FILES = {
    "body-ranges.tsv", "boundaries.ready.json", "boundaries.tsv",
    "direct-calls.tsv", "functions.tsv", "ghidra.log", "listing-state.tsv",
    "parity-graph.ready.json", "program.tsv",
}
CLAIMS = (
    "The completed ceremony contains exactly one writable live apply between read-only PRE and separate read-only POST runs.",
    "All 8,304 PRE function rows remain byte-identical; the exact 23-entry manifest adds 24 disjoint body ranges and 1,131 owned bytes.",
    "The 23 additions retain default metadata; no names, signatures, comments, tags, data definitions, or runtime semantics were promoted.",
    "The protected entries 0x00542720, 0x005D0AD6, and 0x005D0AEA remain non-entry addresses, and 0x005B8500 remains excluded.",
    "The physical transition removes db.18614 and adds db.18616 while db.18615 and every other common file remain exact.",
    "PRE and POST backups reopen read-only; tracked remained PRE through POST recovery, then tracked POST and its retained restore equal live POST byte-for-byte.",
    "The tracked 8,327-row projection and 1,811,418-byte body accounting are mechanically derived from the proved POST state.",
    "Static demo twins and CRT lineage remain evidence bounds, not authorization for private names, source equivalence, runtime effects, or rebuild parity.",
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
    value = stamp(path, role)
    require((value["bytes"], value["sha256"]) == expected, f"{role} stamp differs")
    return value


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
        return datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise AuthorityError(f"{label} UTC timestamp") from exc


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
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            ensure_portable(child, f"{label}[{index}]")
    elif isinstance(value, str):
        require(not re.match(r"^[A-Za-z]:[\\/]", value), f"absolute path leaked at {label}")
        require(not value.startswith("\\\\"), f"UNC path leaked at {label}")
        require(not value.startswith("/"), f"absolute POSIX path leaked at {label}")


def tree_identity(root: Path, excluded: Iterable[str] = ()) -> dict[str, Any]:
    require(root.is_dir(), f"missing evidence tree: {root}")
    skip = set(excluded)
    rows: list[tuple[str, int, str]] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.relative_to(root).as_posix()):
        require(not project_backup.is_reparse(path), f"evidence reparse entry: {path}")
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        if relative in skip:
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
        "canonicalization":
            "sha256<TAB>bytes<TAB>relative-posix-path<LF>, relative-path order",
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


def require_same_project(left: Mapping[str, Any], right: Mapping[str, Any], label: str) -> None:
    require(project_without_root(left) == project_without_root(right), f"{label} differs")


def require_project_summary(
    value: Mapping[str, Any], expected: Mapping[str, Any], label: str
) -> None:
    require(value.get("projectName") == "BEA", f"{label} project name")
    require(value.get("structurallyComplete") is True, f"{label} completeness")
    summary = project_summary(value)
    for key, wanted in expected.items():
        require(summary.get(key) == wanted, f"{label} {key} differs")


def validate_transition(pre: Mapping[str, Any], post: Mapping[str, Any]) -> dict[str, Any]:
    require_project_summary(pre, PRE_PROJECT, "PRE project")
    require_project_summary(post, POST_PROJECT, "POST project")
    before = project_file_map(pre)
    after = project_file_map(post)
    removed = sorted(set(before) - set(after))
    added = sorted(set(after) - set(before))
    changed = sorted(path for path in set(before) & set(after) if before[path] != after[path])
    require(removed == [PRE_OLD_DB_PATH], "project removed path")
    require(added == [POST_ROLLING_DB_PATH], "project added path")
    require(changed == [], "project common files changed")
    require(before.get(PRE_OLD_DB_PATH) == DB_18614, "PRE db.18614 identity")
    require(before.get(STABLE_DB_PATH) == DB_18615, "PRE db.18615 identity")
    require(after.get(STABLE_DB_PATH) == DB_18615, "POST stable db.18615 identity")
    require(after.get(POST_ROLLING_DB_PATH) == DB_18616, "POST db.18616 identity")
    return {
        "removed": removed,
        "added": added,
        "changedCommonFiles": changed,
        "byteDelta": int(post["totalBytes"]) - int(pre["totalBytes"]),
        "stableDatabase": {
            "path": STABLE_DB_PATH, "bytes": DB_18615[0], "sha256": DB_18615[1]
        },
        "rollingDatabase": {
            "path": POST_ROLLING_DB_PATH,
            "bytes": DB_18616[0],
            "sha256": DB_18616[1],
        },
    }


@dataclass(frozen=True)
class RawTable:
    fields: tuple[str, ...]
    order: tuple[str, ...]
    rows: Mapping[str, Mapping[str, str]]
    raw_rows: Mapping[str, bytes]


def raw_tsv(path: Path, key: str) -> RawTable:
    raw = path.read_bytes()
    require(raw.endswith(b"\n"), f"{path} must end with a newline")
    lines = raw.splitlines()
    require(lines, f"empty TSV: {path}")
    while lines and lines[0].startswith(b"#"):
        lines.pop(0)
    require(lines, f"headerless TSV: {path}")
    fields = tuple(lines[0].decode("utf-8").split("\t"))
    require(key in fields and len(fields) == len(set(fields)), f"bad TSV header: {path}")
    text = b"\n".join(lines).decode("utf-8")
    rows: dict[str, Mapping[str, str]] = {}
    raw_rows: dict[str, bytes] = {}
    order: list[str] = []
    reader = csv.DictReader(text.splitlines(), delimiter="\t")
    for number, (row, raw_line) in enumerate(zip(reader, lines[1:]), start=2):
        value = str(row.get(key) or "").lower()
        require(value and value not in rows and None not in row, f"bad {key} at {path}:{number}")
        rows[value] = {str(k): str(v) for k, v in row.items()}
        raw_rows[value] = raw_line
        order.append(value)
    require(len(order) == len(lines) - 1, f"TSV parse incomplete: {path}")
    return RawTable(fields, tuple(order), rows, raw_rows)


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


def load_targets(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        rows = [{str(k): str(v) for k, v in row.items()}
                for row in csv.DictReader(stream, delimiter="\t")]
    require(len(rows) == TARGETS and all(None not in row for row in rows), "target manifest")
    entries = [row["entry"].lower() for row in rows]
    require(entries == sorted(entries) and len(set(entries)) == TARGETS, "target entry order")
    return rows


@dataclass(frozen=True)
class Config:
    repo: Path
    live_project: Path
    pre_backup: Path
    post_backup: Path
    output: Path | None

    @property
    def tracked_project(self) -> Path:
        return self.repo / "reverse-engineering/ghidra"

    @property
    def live_lane(self) -> Path:
        return self.repo / LIVE_LANE_REL

    @property
    def prep_lane(self) -> Path:
        return self.repo / PREP_LANE_REL

    @property
    def projection(self) -> Path:
        return self.repo / PROJECTION_REL


def validate_layout(config: Config, *, final: bool) -> None:
    require(config.repo.is_dir(), "repository root is missing")
    for root in (
        config.live_project, config.tracked_project, config.live_lane,
        config.prep_lane, config.pre_backup, config.post_backup,
    ):
        require(root.is_dir(), f"required root is missing: {root}")
    roots = [
        config.live_project, config.tracked_project, config.live_lane,
        config.prep_lane, config.pre_backup, config.post_backup,
    ]
    for index, left in enumerate(roots):
        for right in roots[index + 1:]:
            require_disjoint(clean_path(left), clean_path(right), "project/evidence roots overlap")
    top_files = {
        "ghidra-function-name-table-2026-08-13.tsv",
        "live-before-apply-inspect.json", "live-post-inspect.json",
        "live-pre-inspect.json", "post-backup-restore.ready.json",
        "post-backup-restore.ready.open-probe.log", "pre-backup-restore.ready.json",
        "pre-backup-restore.ready.open-probe.log", "tracked-post-inspect.json",
        "tracked-post-restore.ready.json", "tracked-post-restore.ready.open-probe.log",
        "tracked-pre-inspect.json", "tracked-still-pre-inspect.json",
    }
    if final:
        top_files.add(RECEIPT_NAME)
    exact_directory_entries(
        config.live_lane,
        expected_files=top_files,
        expected_directories={
            "post-backup-restore-probe", "pre-backup-restore-probe", "runs", "static",
            "tracked-post-accounting", "tracked-post-restore-probe",
        },
        label="live ceremony lane",
    )
    exact_directory_entries(
        config.live_lane / "static",
        expected_files={"diagnostic-addresses.txt", "GhidraApplyCrtP0BoundariesV4.java", "manifest.tsv"},
        expected_directories=(),
        label="live ceremony static inputs",
    )
    exact_directory_entries(
        config.live_lane / "runs",
        expected_files=(), expected_directories=set(EXPECTED_RUN_FILES), label="live run root",
    )
    for run, files in EXPECTED_RUN_FILES.items():
        exact_directory_entries(
            config.live_lane / "runs" / run,
            expected_files=files, expected_directories=(), label=f"live run {run}",
        )
    exact_directory_entries(
        config.live_lane / "tracked-post-accounting",
        expected_files=EXPECTED_ACCOUNTING_FILES,
        expected_directories=(), label="tracked POST accounting",
    )


def validate_repo_inputs(config: Config) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for relative, expected in EXPECTED_REPO_INPUTS.items():
        values[relative] = verify_stamp(config.repo / relative, expected, relative)
    require(
        (Path(project_backup.__file__).resolve().stat().st_size,
         sha256_file(Path(project_backup.__file__).resolve()))
        == EXPECTED_REPO_INPUTS["tools/ghidra_project_backup.py"],
        "imported backup helper differs",
    )
    require(
        (Path(name_projection.__file__).resolve().stat().st_size,
         sha256_file(Path(name_projection.__file__).resolve()))
        == EXPECTED_REPO_INPUTS["tools/re_ghidra_name_projection.py"],
        "imported projection helper differs",
    )
    static_pairs = {
        "GhidraApplyCrtP0BoundariesV4.java": "tools/GhidraApplyCrtP0BoundariesV4.java",
        "manifest.tsv": MANIFEST_REL.as_posix(),
    }
    for local, relative in static_pairs.items():
        require(
            (config.live_lane / "static" / local).read_bytes()
            == (config.repo / relative).read_bytes(),
            f"live static input differs: {local}",
        )
    return values


def validate_preparation(config: Config) -> dict[str, Any]:
    pre_files = {
        "functions.tsv": PRE_FUNCTIONS_STAMP,
        "program.tsv": PRE_PROGRAM_STAMP,
        "listing-state.tsv": PRE_LISTING_STAMP,
    }
    post_files = {
        "functions.tsv": POST_FUNCTIONS_STAMP,
        "program.tsv": POST_PROGRAM_STAMP,
        "listing-state.tsv": POST_LISTING_STAMP,
        "body-ranges.tsv": POST_BODY_RANGES_STAMP,
        "direct-calls.tsv": POST_DIRECT_CALLS_STAMP,
        "parity-graph.ready.json": POST_PARITY_STAMP,
    }
    ledger: dict[str, Any] = {}
    for name, expected in pre_files.items():
        path = config.prep_lane / "static/pre" / name
        ledger[f"static/pre/{name}"] = verify_stamp(path, expected, f"preparation PRE {name}")
    for replica in ("formal-a", "formal-b"):
        for name, expected in post_files.items():
            path = config.prep_lane / replica / "post-exports" / name
            ledger[f"{replica}/post-exports/{name}"] = verify_stamp(
                path, expected, f"preparation {replica} POST {name}"
            )
        for mode, live_name in (("dry", "live-pre-readback"), ("apply", "live-apply"), ("readback", "live-readback")):
            prepared = config.prep_lane / replica / mode / "boundaries.tsv"
            live = config.live_lane / "runs" / live_name / "boundaries.tsv"
            require(prepared.read_bytes() == live.read_bytes(), f"{replica}/{mode} boundary output")
    return {
        "tree": tree_identity(config.prep_lane),
        "criticalArtifacts": ledger,
        "replicas": 2,
        "postSemanticOutputsByteIdentical": True,
        "liveBoundaryOutputsMatchBothReplicas": True,
    }


def validate_function_delta(config: Config) -> dict[str, Any]:
    before_path = config.live_lane / "runs/live-pre-readback/functions.tsv"
    after_path = config.live_lane / "runs/live-readback/functions.tsv"
    verify_stamp(before_path, PRE_FUNCTIONS_STAMP, "live PRE functions")
    verify_stamp(after_path, POST_FUNCTIONS_STAMP, "live POST functions")
    before = raw_tsv(before_path, "address")
    after = raw_tsv(after_path, "address")
    require(before.fields == after.fields, "function headers differ")
    require(len(before.order) == PRE_FUNCTIONS, "PRE function count")
    require(len(after.order) == POST_FUNCTIONS, "POST function count")
    require(set(before.rows) <= set(after.rows), "PRE function destroyed")
    for address, raw in before.raw_rows.items():
        require(after.raw_rows.get(address) == raw, f"PRE row changed at {address}")
    targets = {row["entry"].lower(): row for row in load_targets(config.repo / MANIFEST_REL)}
    created = set(after.rows) - set(before.rows)
    require(created == set(targets), "POST-only function set differs")
    for address, manifest in targets.items():
        row = after.rows[address]
        require(row["nameSource"] == "DEFAULT", f"name source at {address}")
        require(int(row["bodyBytes"]) == int(manifest["expectedBodyBytes"]), f"body bytes at {address}")
        require(int(row["bodyRanges"]) == len(manifest["expectedRanges"].split(";")), f"body ranges at {address}")
        require(int(row["instrCount"]) == int(manifest["expectedInstructionCount"]), f"instructions at {address}")
        require(row["isThunk"].lower() == manifest["expectedIsThunk"].lower(), f"thunk flag at {address}")
        require(row["thunkTarget"].lower() == manifest["expectedThunkTarget"].lower(), f"thunk target at {address}")
        if manifest["expectedIsThunk"].lower() == "false":
            require(row["name"] == "FUN_" + address[2:], f"default name at {address}")
    return {
        "pre": stamp(before_path, "live-lane/runs/live-pre-readback/functions.tsv"),
        "post": stamp(after_path, "live-lane/runs/live-readback/functions.tsv"),
        "unchangedRowsExact": PRE_FUNCTIONS,
        "changedRowsExact": 0,
        "createdAddresses": sorted(created),
        "created": TARGETS,
        "destroyed": 0,
    }


def validate_program_delta(config: Config) -> dict[str, Any]:
    before_path = config.live_lane / "runs/live-pre-readback/program.tsv"
    after_path = config.live_lane / "runs/live-readback/program.tsv"
    verify_stamp(before_path, PRE_PROGRAM_STAMP, "live PRE program")
    verify_stamp(after_path, POST_PROGRAM_STAMP, "live POST program")
    before = read_metrics(before_path)
    after = read_metrics(after_path)
    require(set(before) == set(after), "program metric set differs")
    changed = {key for key in before if before[key] != after[key]}
    expected = {
        "functions", "instructions", "instructionLayoutSha256", "undefinedData",
        "symbolsDefaultOther", "references", "referencesSha256",
    }
    require(changed == expected, f"program changed metrics differ: {sorted(changed)}")
    require(before["functions"] == str(PRE_FUNCTIONS) and after["functions"] == str(POST_FUNCTIONS), "program functions")
    require(before["instructions"] == str(PRE_INSTRUCTIONS) and after["instructions"] == str(POST_INSTRUCTIONS), "program instructions")
    require(before["references"] == str(PRE_REFERENCES) and after["references"] == str(POST_REFERENCES), "program references")
    for key in ("programName", "executableMD5", "executableSHA256", "imageBase", "language", "compilerSpec", "memorySha256", "definedData", "definedDataSha256", "symbolsUserDefined", "symbolsAnalysis", "symbolsImported", "nonFunctionSymbolsSha256", "comments", "commentsSha256", "relocations"):
        require(before[key] == after[key], f"unexpected program drift: {key}")
    return {
        "pre": stamp(before_path, "live-lane/runs/live-pre-readback/program.tsv"),
        "post": stamp(after_path, "live-lane/runs/live-readback/program.tsv"),
        "changedMetrics": sorted(changed),
        "functions": {"before": PRE_FUNCTIONS, "after": POST_FUNCTIONS},
        "instructions": {"before": PRE_INSTRUCTIONS, "after": POST_INSTRUCTIONS},
        "references": {"before": PRE_REFERENCES, "after": POST_REFERENCES},
        "programBytesUnchanged": before["memorySha256"] == after["memorySha256"],
        "definedDataUnchanged": before["definedDataSha256"] == after["definedDataSha256"],
        "storedNonFunctionSymbolsUnchanged": before["nonFunctionSymbolsSha256"] == after["nonFunctionSymbolsSha256"],
        "commentsUnchanged": before["commentsSha256"] == after["commentsSha256"],
    }


def validate_inventory_diff(config: Config) -> dict[str, Any]:
    path = config.live_lane / "runs/live-readback/inventory-diff.json"
    verify_stamp(path, POST_INVENTORY_DIFF_STAMP, "live inventory diff")
    value = load_json(path, "live inventory diff")
    counts = value.get("counts", {})
    expected = {
        "after": POST_FUNCTIONS, "before": PRE_FUNCTIONS, "boundsChanged": 0,
        "callingConvChanged": 0, "created": TARGETS, "destroyed": 0,
        "instrCountChanged": 0, "namesChanged": 0, "noReturnChanged": 0,
        "paramCountChanged": 0, "returnTypeChanged": 0, "sigSourceChanged": 0,
        "signaturesChanged": 0, "thunkFlagChanged": 0,
    }
    require(counts == expected, "inventory-diff counts")
    require(all(rows == [] for rows in value.get("changesByField", {}).values()), "inventory field drift")
    dangerous = value.get("dangerous", {})
    require(all(
        dangerous.get(key) == 0
        for key in ("gradedBoundsMovedCount", "gradedDemotedCount", "gradedDestroyedCount", "gradedRenamedCount")
    ), "dangerous inventory drift")
    require(value.get("destroyed") == [] and len(value.get("created", [])) == TARGETS, "inventory population")
    return {"receipt": stamp(path, "live-lane/runs/live-readback/inventory-diff.json"), "counts": counts, "dangerousChanges": 0}


def validate_listing(config: Config) -> dict[str, Any]:
    before_path = config.live_lane / "runs/live-pre-readback/listing-state.tsv"
    after_path = config.live_lane / "runs/live-readback/listing-state.tsv"
    verify_stamp(before_path, PRE_LISTING_STAMP, "live PRE listing")
    verify_stamp(after_path, POST_LISTING_STAMP, "live POST listing")
    before = raw_tsv(before_path, "input")
    after = raw_tsv(after_path, "input")
    require(before.fields == after.fields and set(before.rows) == set(after.rows), "listing address set")
    for protected in ("0x00542720", "0x005d0ad6", "0x005d0aea"):
        require(after.rows[protected]["function_at"] == "<none>", f"protected entry promoted: {protected}")
    require(after.rows["0x005b8500"]["function_at"] == "<none>" and after.rows["0x005b8500"]["status"] == "UNDEFINED", "excluded canary")
    require(after.rows["0x00542720"]["function_containing"] == "FUN_00542710", "noncontiguous local tail ownership")
    require(after.rows["0x0045ac20"]["function_at"] == "CFEPGoodies__BuildStaticGoodieDataTable", "thunk listing identity")
    return {
        "pre": stamp(before_path, "live-lane/runs/live-pre-readback/listing-state.tsv"),
        "post": stamp(after_path, "live-lane/runs/live-readback/listing-state.tsv"),
        "protectedEntriesAbsent": 3,
        "excludedCanaryAbsent": True,
    }


def validate_boundary_receipt(config: Config, run: str, mode: str) -> tuple[dict[str, Any], datetime]:
    root = config.live_lane / "runs" / run
    value = load_json(root / "boundaries.ready.json", f"{run} boundary receipt")
    require(value.get("schemaVersion") == "bea.ghidra.crt-p0-boundaries.v4", f"{run} schema")
    require(value.get("mode") == mode, f"{run} mode")
    counts = value.get("counts", {})
    expected_counts = {
        "dry": (PRE_FUNCTIONS, PRE_FUNCTIONS, PRE_INSTRUCTIONS, PRE_INSTRUCTIONS),
        "apply": (PRE_FUNCTIONS, POST_FUNCTIONS, PRE_INSTRUCTIONS, POST_INSTRUCTIONS),
        "readback": (POST_FUNCTIONS, POST_FUNCTIONS, POST_INSTRUCTIONS, POST_INSTRUCTIONS),
    }[mode]
    require(
        (counts.get("functionsBefore"), counts.get("functionsAfter"), counts.get("instructionsBefore"), counts.get("instructionsAfter")) == expected_counts,
        f"{run} counters",
    )
    require(counts.get("targets") == TARGETS and counts.get("externalInstructions") == EXTERNAL_INSTRUCTIONS and counts.get("ghidraBodyInstructions") == EXTERNAL_INSTRUCTIONS, f"{run} target counters")
    require(value.get("bodyBytes") == BODY_BYTES and value.get("bodyRanges") == BODY_RANGES, f"{run} body counters")
    require(value.get("preFunctionRanges") == PRE_RANGES and value.get("postFunctionRanges") == POST_RANGES, f"{run} range counters")
    require(value.get("protectedEntries") == ["0x00542720", "0x005d0ad6", "0x005d0aea"], f"{run} protected entries")
    require(value.get("excludedCanary") == "0x005b8500", f"{run} canary")
    require(value.get("namesAuthorized") is False and value.get("metadataAuthorized") is False, f"{run} authorization boundary")
    require(value.get("program") == {"name": PROGRAM_NAME, "md5": PROGRAM_MD5, "sha256": PROGRAM_SHA256}, f"{run} specimen")
    tool = value.get("tool", {})
    manifest = value.get("manifest", {})
    require((tool.get("bytes"), tool.get("sha256")) == EXPECTED_REPO_INPUTS["tools/GhidraApplyCrtP0BoundariesV4.java"], f"{run} tool")
    require((manifest.get("bytes"), manifest.get("sha256")) == EXPECTED_REPO_INPUTS[MANIFEST_REL.as_posix()], f"{run} manifest")
    output = value.get("output", {})
    measured = stamp(root / "boundaries.tsv", f"live-lane/runs/{run}/boundaries.tsv")
    require((output.get("bytes"), output.get("sha256")) == (measured["bytes"], measured["sha256"]), f"{run} output")
    log_path = root / "ghidra.log"
    text = log_path.read_text(encoding="utf-8", errors="strict")
    if mode == "dry":
        sentinel = f"CRT_P0_BOUNDARIES_OK mode=dry targets={TARGETS} functions={PRE_FUNCTIONS}"
    elif mode == "apply":
        sentinel = f"CRT_P0_BOUNDARIES_OK mode=apply targets={TARGETS} functions_before={PRE_FUNCTIONS} functions_after={POST_FUNCTIONS}"
    else:
        sentinel = f"CRT_P0_BOUNDARIES_OK mode=readback targets={TARGETS} functions={POST_FUNCTIONS}"
    require(text.count(sentinel) == 1, f"{run} exact sentinel")
    saves = text.count("Save succeeded for processed file: /BEA.exe")
    require(saves == (1 if mode == "apply" else 0), f"{run} save count")
    require(("Processing read-only project file: /BEA.exe" in text) == (mode != "apply"), f"{run} read-only marker")
    require("REPORT SCRIPT ERROR" not in text, f"{run} script error")
    return {
        "receipt": stamp(root / "boundaries.ready.json", f"live-lane/runs/{run}/boundaries.ready.json"),
        "output": measured,
        "log": stamp(log_path, f"live-lane/runs/{run}/ghidra.log"),
        "mode": mode,
        "saveCount": saves,
    }, parse_utc(value.get("completedAtUtc"), f"{run} completedAtUtc")


def validate_runs(config: Config) -> tuple[dict[str, Any], dict[str, datetime]]:
    values: dict[str, Any] = {}
    times: dict[str, datetime] = {}
    for run, mode in (("live-pre-readback", "dry"), ("live-apply", "apply"), ("live-readback", "readback")):
        values[run], times[f"{run}.receipt"] = validate_boundary_receipt(config, run, mode)
        times[f"{run}.complete"] = max(mtime_utc(path) for path in (config.live_lane / "runs" / run).iterdir())
    require(sum(int(value["saveCount"]) for value in values.values()) == 1, "ceremony save count")
    return values, times


def manifest_value(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value.get(key)
        for key in ("projectName", "fileCount", "totalBytes", "structurallyComplete", "files")
    }


def require_exact_comparison(value: Mapping[str, Any], label: str) -> None:
    require(value.get("matches") is True, f"{label} comparison")
    for key in ("extraCount", "hashDiffCount", "missingCount", "sizeDiffCount"):
        require(value.get(key) == 0, f"{label} {key}")
    for key in ("extra", "hashDifferences", "missing", "sizeDifferences"):
        require(value.get(key) == [], f"{label} {key}")


def validate_inspect(path: Path, expected_root: Path, expected: Mapping[str, Any], label: str) -> datetime:
    value = load_json(path, label)
    require(value.get("schemaVersion") == project_backup.SCHEMA_VERSION, f"{label} schema")
    manifest = value.get("manifest", {})
    require(manifest_value(manifest) == project_without_root(expected), f"{label} manifest")
    require(clean_path(Path(str(manifest.get("root", "")))) == clean_path(expected_root), f"{label} root")
    return parse_utc(value.get("createdAtUtc"), f"{label} createdAtUtc")


def validate_backup_manifest(path: Path, expected: Mapping[str, Any], destination: Path, label: str) -> datetime:
    value = load_json(path, label)
    require(value.get("schemaVersion") == project_backup.SCHEMA_VERSION, f"{label} schema")
    require(value.get("sourceStable") is True and value.get("readonlyOpen") is None, f"{label} shape")
    require_exact_comparison(value.get("copyComparison", {}), f"{label} copy")
    require(manifest_value(value.get("source", {})) == project_without_root(expected), f"{label} source")
    require(manifest_value(value.get("destination", {})) == project_without_root(expected), f"{label} destination")
    require(clean_path(path.parent) == clean_path(destination), f"{label} destination path")
    return parse_utc(value.get("createdAtUtc"), f"{label} createdAtUtc")


def validate_restore(
    config: Config,
    receipt_name: str,
    probe_root_name: str,
    source_root: Path,
    expected: Mapping[str, Any],
    expected_total_functions: int,
    label: str,
) -> tuple[dict[str, Any], datetime]:
    path = config.live_lane / receipt_name
    value = load_json(path, label)
    require(value.get("schemaVersion") == project_backup.SCHEMA_VERSION, f"{label} schema")
    require(value.get("sourceStable") is True and value.get("probeCopyDisposition") == "RETAINED_AT_VERIFICATION", f"{label} retention")
    require(manifest_value(value.get("source", {})) == project_without_root(expected), f"{label} source")
    require(clean_path(Path(str(value.get("source", {}).get("root", "")))) == clean_path(source_root), f"{label} source root")
    require_exact_comparison(value.get("copyComparison", {}), f"{label} copy")
    opened = value.get("readonlyOpen", {})
    require(opened.get("opened") is True and opened.get("contentStable") is True and opened.get("exitCode") == 0, f"{label} open")
    require(opened.get("observedFunctionCount") == expected_total_functions, f"{label} function count")
    require(opened.get("expectedProgramMd5") == PROGRAM_MD5 and opened.get("expectedProgramSha256") == PROGRAM_SHA256, f"{label} expected specimen")
    require(opened.get("observedProgramName") == PROGRAM_NAME and opened.get("observedProgramMd5") == PROGRAM_MD5 and opened.get("observedProgramSha256") == PROGRAM_SHA256, f"{label} observed specimen")
    require_exact_comparison(opened.get("postOpenComparison", {}), f"{label} post-open")
    probe_root = config.live_lane / probe_root_name
    entries = list(probe_root.iterdir()) if probe_root.is_dir() else []
    require(len(entries) == 1 and entries[0].is_dir() and not project_backup.is_reparse(entries[0]), f"{label} probe topology")
    probe = clean_path(entries[0])
    require(clean_path(Path(str(value.get("probeCopy", "")))) == probe, f"{label} probe path")
    expected_command = project_backup.build_open_command(
        ANALYZE_HEADLESS, probe, "BEA", PROGRAM_NAME, config.repo / "tools", PROGRAM_MD5, PROGRAM_SHA256
    )
    require(opened.get("commandArgv") == expected_command, f"{label} read-only command")
    require_same_project(project_value(probe), expected, f"{label} retained probe")
    log_path = config.live_lane / receipt_name.replace(".json", ".open-probe.log")
    measured_log = stamp(log_path, f"live-lane/{log_path.name}")
    log = opened.get("probeLog", {})
    require(log.get("path") == log_path.name and (log.get("bytes"), log.get("sha256")) == (measured_log["bytes"], measured_log["sha256"]), f"{label} probe log")
    text = log_path.read_text(encoding="utf-8", errors="strict")
    sentinel = f"GHIDRA_PROJECT_OPEN_PROBE_OK program={PROGRAM_NAME} md5={PROGRAM_MD5} sha256={PROGRAM_SHA256} functions={expected_total_functions}"
    require(text.count(sentinel) == 1 and text.count("Processing read-only project file: /BEA.exe") == 1, f"{label} read-only sentinel")
    require("Save succeeded for processed file" not in text, f"{label} unexpected save")
    for marker in project_backup.GHIDRA_OPEN_ERROR_MARKERS:
        require(marker not in text, f"{label} error marker: {marker}")
    retained_manifest = probe / "backup_manifest.json"
    validate_backup_manifest(retained_manifest, expected, probe, f"{label} retained manifest")
    return {
        "receipt": stamp(path, f"live-lane/{receipt_name}"),
        "probeLog": measured_log,
        "source": project_summary(expected),
        "retainedProbeEqualsSource": True,
        "readOnlyOpen": True,
    }, parse_utc(value.get("verifiedAtUtc"), f"{label} verifiedAtUtc")


def validate_projects(config: Config) -> tuple[dict[str, Any], dict[str, datetime]]:
    times: dict[str, datetime] = {}
    pre = project_value(config.pre_backup)
    post = project_value(config.live_project)
    transition = validate_transition(pre, post)
    require_same_project(project_value(config.post_backup), post, "POST backup/live POST")
    require_same_project(project_value(config.tracked_project), post, "tracked/live POST")

    times["live.pre.inspect"] = validate_inspect(config.live_lane / "live-pre-inspect.json", config.live_project, pre, "live PRE inspect")
    times["tracked.pre.inspect"] = validate_inspect(config.live_lane / "tracked-pre-inspect.json", config.tracked_project, pre, "tracked PRE inspect")
    times["live.beforeApply.inspect"] = validate_inspect(config.live_lane / "live-before-apply-inspect.json", config.live_project, pre, "live before-apply inspect")
    times["live.post.inspect"] = validate_inspect(config.live_lane / "live-post-inspect.json", config.live_project, post, "live POST inspect")
    times["tracked.stillPre.inspect"] = validate_inspect(config.live_lane / "tracked-still-pre-inspect.json", config.tracked_project, pre, "tracked still-PRE inspect")
    times["tracked.post.inspect"] = validate_inspect(config.live_lane / "tracked-post-inspect.json", config.tracked_project, post, "tracked POST inspect")
    times["pre.backup.created"] = validate_backup_manifest(config.pre_backup / "backup_manifest.json", pre, config.pre_backup, "PRE backup")
    times["post.backup.created"] = validate_backup_manifest(config.post_backup / "backup_manifest.json", post, config.post_backup, "POST backup")
    pre_restore, times["pre.restore.verified"] = validate_restore(config, "pre-backup-restore.ready.json", "pre-backup-restore-probe", config.pre_backup, pre, PRE_TOTAL_FUNCTIONS, "PRE restore")
    post_restore, times["post.restore.verified"] = validate_restore(config, "post-backup-restore.ready.json", "post-backup-restore-probe", config.post_backup, post, POST_TOTAL_FUNCTIONS, "POST restore")
    tracked_restore, times["tracked.restore.verified"] = validate_restore(config, "tracked-post-restore.ready.json", "tracked-post-restore-probe", config.tracked_project, post, POST_TOTAL_FUNCTIONS, "tracked POST restore")
    return {
        "pre": project_summary(pre),
        "post": project_summary(post),
        "liveEqualsTrackedEqualsPostBackup": True,
        "trackedStillPreAfterPostRecovery": True,
        "rollingDelta": transition,
        "backups": {
            "pre": stamp(config.pre_backup / "backup_manifest.json", "pre-backup/backup_manifest.json"),
            "post": stamp(config.post_backup / "backup_manifest.json", "post-backup/backup_manifest.json"),
        },
        "restores": {"pre": pre_restore, "post": post_restore, "trackedPost": tracked_restore},
    }, times


def parse_body_rows(path: Path) -> list[dict[str, str]]:
    raw = path.read_bytes()
    require(raw.endswith(b"\n") and b"\r" not in raw, "body ranges framing")
    lines = raw.splitlines()
    while lines and lines[0].startswith(b"#"):
        lines.pop(0)
    require(lines, "body ranges header")
    rows = list(csv.DictReader(b"\n".join(lines).decode("utf-8").splitlines(), delimiter="\t"))
    require(all(None not in row for row in rows), "body ranges malformed row")
    return [{str(k): str(v) for k, v in row.items()} for row in rows]


def validate_accounting(config: Config) -> tuple[dict[str, Any], datetime]:
    root = config.live_lane / "tracked-post-accounting"
    live = config.live_lane / "runs/live-readback"
    for name in ("boundaries.tsv", "functions.tsv", "program.tsv", "listing-state.tsv", "body-ranges.tsv", "direct-calls.tsv", "parity-graph.ready.json"):
        require((root / name).read_bytes() == (live / name).read_bytes(), f"tracked accounting/live {name}")
    verify_stamp(root / "body-ranges.tsv", POST_BODY_RANGES_STAMP, "tracked POST body ranges")
    verify_stamp(root / "direct-calls.tsv", POST_DIRECT_CALLS_STAMP, "tracked POST direct calls")
    verify_stamp(root / "parity-graph.ready.json", POST_PARITY_STAMP, "tracked POST parity receipt")
    receipt = load_json(root / "parity-graph.ready.json", "tracked POST parity graph")
    require(receipt.get("schemaVersion") == "bea-ghidra-parity-graph-receipt.v2", "parity schema")
    require(receipt.get("bodyRanges", {}).get("functionCount") == POST_FUNCTIONS and receipt.get("bodyRanges", {}).get("rangeCount") == POST_RANGES, "parity body counts")
    require(receipt.get("directCalls", {}).get("directEdgeCount") == 14598 and receipt.get("directCalls", {}).get("directCallSiteCount") == 27244, "parity call counts")

    pre_rows = parse_body_rows(config.prep_lane / "static/pre/body-ranges.tsv")
    post_rows = parse_body_rows(root / "body-ranges.tsv")
    pre_by_function: dict[str, list[dict[str, str]]] = {}
    post_by_function: dict[str, list[dict[str, str]]] = {}
    for row in pre_rows:
        pre_by_function.setdefault(row["functionAddress"].lower(), []).append(row)
    for row in post_rows:
        post_by_function.setdefault(row["functionAddress"].lower(), []).append(row)
    targets = {row["entry"].lower(): row for row in load_targets(config.repo / MANIFEST_REL)}
    require(len(pre_by_function) == PRE_FUNCTIONS and len(pre_rows) == PRE_RANGES, "PRE body accounting")
    require(len(post_by_function) == POST_FUNCTIONS and len(post_rows) == POST_RANGES, "POST body accounting")
    require(set(post_by_function) - set(pre_by_function) == set(targets), "POST-only body owners")
    for address, rows in pre_by_function.items():
        require(post_by_function.get(address) == rows, f"PRE body rows changed at {address}")
    for address, manifest in targets.items():
        rows = post_by_function[address]
        expected_ranges = manifest["expectedRanges"].lower().split(";")
        require(len(rows) == len(expected_ranges), f"target body range count at {address}")
        for ordinal, (row, interval) in enumerate(zip(rows, expected_ranges), 1):
            start, end = interval.split("-")
            require(row["rangeOrdinal"] == str(ordinal), f"target body ordinal at {address}")
            require(row["rangeMin"].lower() == start and row["rangeEndExclusive"].lower() == end, f"target body interval at {address}")
        require(sum(int(row["rangeBytes"]) for row in rows) == int(manifest["expectedBodyBytes"]), f"target body bytes at {address}")
    intervals = sorted((int(row["rangeMin"], 16), int(row["rangeEndExclusive"], 16)) for row in post_rows)
    require(all(TEXT_START <= start < end <= TEXT_END for start, end in intervals), "body interval outside text")
    require(all(left[1] <= right[0] for left, right in zip(intervals, intervals[1:])), "body overlap")
    owned = sum(end - start for start, end in intervals)
    require(owned == POST_OWNED, "POST owned bytes")
    log = root / "ghidra.log"
    text = log.read_text(encoding="utf-8", errors="strict")
    require(text.count(f"PARITY_GRAPH_OK functions={POST_FUNCTIONS} ranges={POST_RANGES} directEdges=14598 directCallSites=27244") == 1, "accounting graph sentinel")
    require("Save succeeded for processed file" not in text and "REPORT SCRIPT ERROR" not in text, "accounting read-only shape")
    return {
        "bodyRanges": stamp(root / "body-ranges.tsv", "live-lane/tracked-post-accounting/body-ranges.tsv"),
        "directCalls": stamp(root / "direct-calls.tsv", "live-lane/tracked-post-accounting/direct-calls.tsv"),
        "parityReceipt": stamp(root / "parity-graph.ready.json", "live-lane/tracked-post-accounting/parity-graph.ready.json"),
        "functions": POST_FUNCTIONS,
        "ranges": POST_RANGES,
        "ownedBytes": owned,
        "uncoveredBytes": TEXT_BYTES - owned,
        "ownedPercent": owned * 100.0 / TEXT_BYTES,
        "preservedPreFunctionRows": PRE_FUNCTIONS,
        "createdFunctionRows": TARGETS,
        "bodyRangeDelta": BODY_RANGES,
        "ownedByteDelta": BODY_BYTES,
        "overlapBytes": 0,
    }, max(mtime_utc(path) for path in root.iterdir())


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
    require((len(expected), hashlib.sha256(expected).hexdigest()) == POST_PROJECTION_STAMP, "mechanical projection identity")
    require(retained.read_bytes() == expected, "retained projection is not mechanical")
    require(config.projection.read_bytes() == expected, "tracked projection is not mechanical")
    rows = sum(1 for line in expected.splitlines() if line and not line.startswith(b"#")) - 1
    require(rows == POST_FUNCTIONS, "projection row count")
    return {
        "rows": rows, "bytes": len(expected), "sha256": hashlib.sha256(expected).hexdigest(),
        "sourceInventory": stamp(inventory, "live-lane/runs/live-readback/functions.tsv"),
        "retained": stamp(retained, "live-lane/ghidra-function-name-table-2026-08-13.tsv"),
        "tracked": stamp(config.projection, PROJECTION_REL.as_posix()),
        "sourceLabel": PROJECTION_SOURCE,
    }, min(mtime_utc(retained), mtime_utc(config.projection))


def require_before(events: Mapping[str, datetime], left: str, right: str) -> None:
    require(events[left] < events[right], f"chronology does not advance: {left} -> {right}")


def validate_chronology(
    project_times: Mapping[str, datetime],
    run_times: Mapping[str, datetime],
    projection_time: datetime,
    accounting_time: datetime,
) -> list[dict[str, str]]:
    events = {**project_times, **run_times, "projection.complete": projection_time, "accounting.complete": accounting_time}
    edges = [
        ("live.pre.inspect", "pre.backup.created"),
        ("tracked.pre.inspect", "pre.backup.created"),
        ("pre.backup.created", "pre.restore.verified"),
        ("pre.restore.verified", "live-pre-readback.receipt"),
        ("live-pre-readback.receipt", "live-pre-readback.complete"),
        ("live-pre-readback.complete", "live.beforeApply.inspect"),
        ("live.beforeApply.inspect", "live-apply.receipt"),
        ("live-apply.receipt", "live-apply.complete"),
        ("live-apply.complete", "live-readback.receipt"),
        ("live-readback.receipt", "live-readback.complete"),
        ("live-readback.complete", "live.post.inspect"),
        ("live.post.inspect", "post.backup.created"),
        ("post.backup.created", "post.restore.verified"),
        ("post.restore.verified", "tracked.stillPre.inspect"),
        ("live-readback.complete", "projection.complete"),
        ("projection.complete", "tracked.post.inspect"),
        ("tracked.stillPre.inspect", "tracked.post.inspect"),
        ("tracked.post.inspect", "tracked.restore.verified"),
        ("tracked.restore.verified", "accounting.complete"),
    ]
    for left, right in edges:
        require_before(events, left, right)
    return [{"before": left, "after": right, "beforeUtc": utc_text(events[left]), "afterUtc": utc_text(events[right])} for left, right in edges]


def build_final(config: Config) -> dict[str, Any]:
    validate_layout(config, final=config.output is not None and config.output.exists())
    repo_inputs = validate_repo_inputs(config)
    preparation = validate_preparation(config)
    functions = validate_function_delta(config)
    program = validate_program_delta(config)
    inventory = validate_inventory_diff(config)
    listing = validate_listing(config)
    runs, run_times = validate_runs(config)
    projects, project_times = validate_projects(config)
    accounting, accounting_time = validate_accounting(config)
    projection, projection_time = validate_projection(config)
    chronology = validate_chronology(project_times, run_times, projection_time, accounting_time)
    tree = tree_identity(config.live_lane, excluded={RECEIPT_NAME})
    return {
        "schemaVersion": SCHEMA,
        "policy": POLICY,
        "verdict": "VERIFIED",
        "generatedAtUtc": utc_text(datetime.now(timezone.utc)),
        "baseCommit": BASE_COMMIT,
        "repoInputs": repo_inputs,
        "preparation": preparation,
        "ceremony": {
            "runs": runs,
            "saveCount": 1,
            "functionDelta": functions,
            "programDelta": program,
            "inventoryDiff": inventory,
            "listing": listing,
        },
        "projects": projects,
        "projection": projection,
        "accounting": accounting,
        "chronology": chronology,
        "artifactTree": tree,
        "claims": list(CLAIMS),
        "authorizationBoundary": {
            "names": False, "metadata": False, "data": False, "runtime": False,
            "sourceEquivalence": False, "rebuildParity": False,
        },
    }


def atomic_new_json(path: Path, value: Mapping[str, Any]) -> None:
    require(not path.exists(), f"output already exists: {path}")
    require(path.parent.is_dir(), f"output parent missing: {path.parent}")
    temp = path.with_name(path.name + ".tmp")
    require(not temp.exists(), f"temporary output already exists: {temp}")
    payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
    try:
        temp.write_text(payload, encoding="utf-8", newline="\n")
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def normalized(value: Mapping[str, Any]) -> dict[str, Any]:
    return {key: child for key, child in value.items() if key != "generatedAtUtc"}


def seal(config: Config) -> None:
    require(config.output is not None, "seal requires --output")
    require(clean_path(config.output) == clean_path(config.live_lane / RECEIPT_NAME), "non-canonical output path")
    validate_layout(config, final=False)
    value = build_final(config)
    ensure_portable(value)
    atomic_new_json(config.output, value)
    print(
        f"CRT_P0_LIVE_AUTHORITY_SEALED functions={POST_FUNCTIONS} targets={TARGETS} "
        f"receipt={config.output}"
    )


def verify(config: Config) -> None:
    require(config.output is not None and config.output.is_file(), "verify requires existing --output")
    require(clean_path(config.output) == clean_path(config.live_lane / RECEIPT_NAME), "non-canonical output path")
    saved = load_json(config.output, "saved live authority")
    ensure_portable(saved)
    require(saved.get("schemaVersion") == SCHEMA and saved.get("policy") == POLICY, "saved authority identity")
    regenerated = build_final(config)
    require(normalized(saved) == normalized(regenerated), "saved live authority differs from replay")
    print(
        f"CRT_P0_LIVE_AUTHORITY_VERIFIED functions={POST_FUNCTIONS} targets={TARGETS} "
        f"receipt={config.output}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("seal", "verify"))
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--live-project", type=Path, default=Path(r"C:\Users\david\Ghidra\Projects"))
    parser.add_argument("--pre-backup", type=Path, default=Path(r"D:\BEA-Ghidra-Backups\2026-08-14-crt23-db18615-pre-live-v2"))
    parser.add_argument("--post-backup", type=Path, default=Path(r"D:\BEA-Ghidra-Backups\2026-08-14-crt23-db18615-post-live-v2"))
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo = clean_path(args.repo)
    output = clean_path(args.output) if args.output else repo / LIVE_LANE_REL / RECEIPT_NAME
    config = Config(
        repo=repo,
        live_project=clean_path(args.live_project),
        pre_backup=clean_path(args.pre_backup),
        post_backup=clean_path(args.post_backup),
        output=output,
    )
    try:
        if args.command == "seal":
            seal(config)
        else:
            verify(config)
    except (AuthorityError, OSError, ValueError, KeyError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
