#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Reproduce and seal the completed 31-function text-gap live promotion.

The verifier never launches Ghidra and never mutates a project.  ``seal`` has
one write: create a new aggregate receipt under this checkout's ignored
``local-lab`` tree.  Every promoted fact is rebuilt from retained inventories,
run receipts, project bytes, backup/restore evidence, and the tracked name
projection; saved success booleans are not accepted without their bound files.
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


TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import ghidra_project_backup as project_backup  # noqa: E402
import ghidra_text_gap_boundary_scratch_authority as scratch  # noqa: E402
import re_ghidra_name_projection as name_projection  # noqa: E402


SCHEMA = "bea.ghidra.text-gap-boundary-live-authority.v1"
BASE_COMMIT = "f3a6a172dbaf03a3f3eebab6e09179effe2a6e5c"
PROGRAM_NAME = "BEA.exe"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
PROGRAM_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"

TARGETS = 31
PRE_FUNCTIONS = 8170
POST_FUNCTIONS = 8201
PRE_INSTRUCTIONS = 549872
POST_INSTRUCTIONS = 550982
PRE_REFERENCES = 234357
POST_REFERENCES = 234537

PRE_PROJECT = {
    "fileCount": 19,
    "totalBytes": 186813317,
    "canonicalInventorySha256":
        "a264bdc993a269452e90cea37c57ece685fcd38f1df073b67a2b237d01f83647",
}
POST_PROJECT = {
    "fileCount": 19,
    "totalBytes": 186911621,
    "canonicalInventorySha256":
        "91776fb4a67579950afc4fb3b48ea8a866733628aecfdae7a2cb918c615fe211",
}
REPLICA_PROJECTS = {
    "replica-a": {
        "fileCount": 19,
        "totalBytes": 186911621,
        "canonicalInventorySha256":
            "3cf563e0b29b9b392624f8640970eb20cb01a496de8996ef76ebefe5771db27a",
    },
    "replica-b": {
        "fileCount": 19,
        "totalBytes": 186911621,
        "canonicalInventorySha256":
            "9fa63c406e1f3fb1938874f16552728b97be808ec9e5ad4f848d7678a493b995",
    },
}
DB_18610 = (
    68222976,
    "210a0461a6b1746f7bbc53e883b616c4a02694a055f1bd23ccadaf44472c1356",
)
DB_18611 = (
    68288512,
    "6f45cdac7ae1f10987280f0ec247e6b5d6dcf866eae79e5982efa78dd68455ce",
)
DB_18612 = (
    68321280,
    "424775377ea0f40d9e429c9219b9310d427760acc40548dbc588ca285f932f7b",
)

MANIFEST_REL = (
    "reverse-engineering/binary-analysis/"
    "text-gap-missing-function-boundaries-2026-08-13.tsv"
)
PROJECTION_REL = (
    "reverse-engineering/binary-analysis/"
    "ghidra-function-name-table-2026-08-13.tsv"
)
LIVE_LANE_REL = "local-lab/ghidra-text-gap-boundary-live-promotion-20260814-v1"
SCRATCH_LANE_REL = "local-lab/ghidra-text-gap-boundary-scratch-20260813-v3"
SCRATCH_RECEIPT_REL = f"{SCRATCH_LANE_REL}/scratch-authority.ready.json"

EXPECTED_REPO_FILES = {
    MANIFEST_REL: (
        14930,
        "afc13e4c56a5598c06872326e05e7e61d535a1271e81943c498303a46ee1a586",
    ),
    "tools/GhidraApplyTextGapBoundaries.java": (
        47139,
        "9c488f095c85852d69cafc02e65efdac0c5bfa82538df38f5bbfb039c1e0390d",
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
    "tools/ghidra_text_gap_boundary_scratch_authority.py": (
        28308,
        "4b76bd3b62807b7188d4a369d3c84151e7643bb02fd0203a93a18c2739686238",
    ),
    "tools/re_ghidra_name_projection.py": (
        6139,
        "d13d5f4d3b20cbd1e1baf24cd924d454c6c07b0bbf5517834c4089357f14ecdb",
    ),
    PROJECTION_REL: (
        504598,
        "c6084999cefebdb900ec752be5c4cb45ed1d7dcbdd086a53cbd207b91db84d20",
    ),
}

EXPECTED_LANE_ARTIFACTS = {
    "live-pre-inspect.json": (3760, "78d0bd162227059523d43d02108f6d28c939fd9ba2eef87d4d9e94334cbdb9aa"),
    "tracked-pre-inspect.json": (3804, "3be8235a0ab30d0d70f3b9a8d96068cd76f81cec3e85404b1a93d74b91556a51"),
    "pre-backup-restore.ready.json": (5910, "237c3164d20eba16dbc856e678db131bfc1d08bb9d1c1e5875b8d680fd6b9a40"),
    "pre-backup-restore.ready.open-probe.log": (4526, "48ac2842ec3b74fe5a743fce82235350f276354100988b1bd013cb07aa266513"),
    "live-before-apply-inspect.json": (3760, "ce08e59bcab75a990cb2315da05df196825ec35e878e0a1fa35e5a24091e3936"),
    "live-post-inspect.json": (3760, "8bb865b846e67833873f9df34e8e3d29d045a586abba489398105e8a6656e603"),
    "post-backup-restore.ready.json": (5914, "159cf9d7149f01778baefdc68721eb7f1a342d33a722e2e066508467378baeae"),
    "post-backup-restore.ready.open-probe.log": (4529, "7cb409651e6f7da76f3c60d1ed96a68e7c039f52ec5dc182c9f0a13355cc7b9a"),
    "tracked-post-inspect.json": (3804, "5467f3422a3aeb753b6b0e9616069e21d985564bc39923689af45e59b3b8c879"),
    "tracked-post-restore.ready.json": (5931, "145ad8bc7cc779d7416cc27a8ff7b33f5262dfd3caf809fe5c581212200774ef"),
    "tracked-post-restore.ready.open-probe.log": (4531, "46df3bb3404976274118df442202ce76ac65bcf16300c6f5629485c08f3cb771"),
    "ghidra-function-name-table-2026-08-13.tsv": (504598, "c6084999cefebdb900ec752be5c4cb45ed1d7dcbdd086a53cbd207b91db84d20"),
    "refresh_tracked_snapshot.ps1": (2578, "ba678a60b4561d75fa492679b0b4ddf982492d5425b95dcbf43bcbb2e6bac470"),
    "runs/replica-a-dry/boundaries.ready.json": (1135, "7f8a302fe51929ceef7a4949be9a217d6ef6a417fc6741f812576d63d2332ee8"),
    "runs/replica-a-dry/boundaries.tsv": (7095, "a02922eb296d7388c1101c926ace46ccd862bb6f92739cca7cdb5c40a82642fe"),
    "runs/replica-a-dry/ghidra.log": (5224, "ec2e9ac7c6acf44c30e80c2b98d1b49b06241decba10d4dd9074ae04b7bb1759"),
    "runs/replica-a-apply/boundaries.ready.json": (1140, "9e520283e1b5f18adb5c1038d39fa96f41dd3af69b76687401a9764e6d24f7fb"),
    "runs/replica-a-apply/boundaries.tsv": (12286, "2898bc62b33e94d1478e7848ff051e71c9a576a3c9df7699f5180c8e321b9ecf"),
    "runs/replica-a-apply/ghidra.log": (5352, "ee52486add9e48bc0e0e4fcb219c993f2527b01f55a7a2285f575f83f7f74832"),
    "runs/replica-a-readback/boundaries.ready.json": (1147, "38a3c4d3f4d1159df6d4c4c37287066ffb267e03b2155b64f9e41ccc87c2bab3"),
    "runs/replica-a-readback/boundaries.tsv": (12317, "15411a14e5cb011d8c6d28948280d8a8a4bf9f144e8a9859c456e6b5841a8597"),
    "runs/replica-a-readback/ghidra.log": (6243, "b2315f363c0e279328c14d0fe94516dff1cd4fd65466b5707256ab045836c0ec"),
    "runs/replica-a-readback/functions.tsv": (7109943, "2cc0b74f9284a3d6d59effa857cb6766bb78b08d50a7896d0dda8631f7c93314"),
    "runs/replica-a-readback/program.tsv": (1267, "be169e6bae9bbd32c822a70c180e43960336fd85ee8ad52f5f494090c0a1e636"),
    "runs/replica-b-dry/boundaries.ready.json": (1135, "b58bb9ad3d2563e6c1db50fe287788ec6fc071dc99ed104cd516b3347f009f83"),
    "runs/replica-b-dry/boundaries.tsv": (7095, "a02922eb296d7388c1101c926ace46ccd862bb6f92739cca7cdb5c40a82642fe"),
    "runs/replica-b-dry/ghidra.log": (5224, "b11c709c07656eefb998ee508acb519036b9306e3b0c6e6b758d3daa765f72ea"),
    "runs/replica-b-apply/boundaries.ready.json": (1140, "2e0868d045bb5ba77436a7ab5962a154fcaa7f42790648ba9a62b48223502f91"),
    "runs/replica-b-apply/boundaries.tsv": (12286, "2898bc62b33e94d1478e7848ff051e71c9a576a3c9df7699f5180c8e321b9ecf"),
    "runs/replica-b-apply/ghidra.log": (5352, "9197c85cdafbaf7f75cf30bd4bfba7a7316c3792bdb42bbd6e66e11262dc5b99"),
    "runs/replica-b-readback/boundaries.ready.json": (1147, "6305cce8aa410f8a8f5e802e970afa880cbd61c338d9ccd167ff9ff1de82d831"),
    "runs/replica-b-readback/boundaries.tsv": (12317, "15411a14e5cb011d8c6d28948280d8a8a4bf9f144e8a9859c456e6b5841a8597"),
    "runs/replica-b-readback/ghidra.log": (6243, "d1514d6ab97ad2273e5fac84a04a1141525ccb7e53e46f1424c959e8c1108b88"),
    "runs/replica-b-readback/functions.tsv": (7109943, "2cc0b74f9284a3d6d59effa857cb6766bb78b08d50a7896d0dda8631f7c93314"),
    "runs/replica-b-readback/program.tsv": (1267, "be169e6bae9bbd32c822a70c180e43960336fd85ee8ad52f5f494090c0a1e636"),
    "runs/live-pre-readback/boundaries.ready.json": (1139, "f8aa50cb0147684c63266e563eb16941e6ea6b30b1846ca24be95c2a475cab13"),
    "runs/live-pre-readback/boundaries.tsv": (7095, "a02922eb296d7388c1101c926ace46ccd862bb6f92739cca7cdb5c40a82642fe"),
    "runs/live-pre-readback/ghidra.log": (6035, "8f450875f5d690b2d280c68b72e5ecee1c0ed8b77680d97ca63fb8e56fb44ed4"),
    "runs/live-pre-readback/functions.tsv": (7089535, "ee3090360bd4f4b68d1ac52c59ab397e7ac37d81c76029d492e2a9d046902f1d"),
    "runs/live-pre-readback/program.tsv": (1267, "2360923e0fa95648a708ee44297006dee222036662d7b34108d10a1fa405dc02"),
    "runs/live-apply/boundaries.ready.json": (1135, "ba10774cb68139e9d0291ca7b0a3bd786b63e2ad44b4cc8e2dc6435b97a15f6c"),
    "runs/live-apply/boundaries.tsv": (12286, "2898bc62b33e94d1478e7848ff051e71c9a576a3c9df7699f5180c8e321b9ecf"),
    "runs/live-apply/ghidra.log": (5144, "ece22399c20f2c0e698d3e53e5ae55c60ab9aa15b949b0683a55098d0146f82c"),
    "runs/live-readback/boundaries.ready.json": (1142, "ad51a411e782e0facc9b1027d158e9d6da77a91c08bb30d34dee35d4694a47a1"),
    "runs/live-readback/boundaries.tsv": (12317, "15411a14e5cb011d8c6d28948280d8a8a4bf9f144e8a9859c456e6b5841a8597"),
    "runs/live-readback/ghidra.log": (6025, "60ecbfb38ee75ace0536753e51ae5655fb939ac06185137417a09dba313fc9fd"),
    "runs/live-readback/functions.tsv": (7109943, "2cc0b74f9284a3d6d59effa857cb6766bb78b08d50a7896d0dda8631f7c93314"),
    "runs/live-readback/program.tsv": (1267, "be169e6bae9bbd32c822a70c180e43960336fd85ee8ad52f5f494090c0a1e636"),
    "runs/live-readback/inventory-diff.json": (13756, "fd01e6574a3335efdc708395832220e7af7e53b133c17d0873cd7816202f6659"),
}

EXPECTED_EXTERNAL = {
    "scratch-authority/ready.json": (
        5242,
        "e3d14106830b2b3645ffaf80c1b4cdbb73a5c0235b0afd2a4f3156702a46d2c4",
    ),
    "pre-backup/backup_manifest.json": (
        7589,
        "a7803b16a8f69d940aee487cf505cccc05578fcb2c51375ce3cce719dd06ef3a",
    ),
    "post-backup/backup_manifest.json": (
        7589,
        "6976b1094374fa4788bba4b74a9beda0c9ca9e1100fd0e0b14b1004d5f475484",
    ),
    "live-lane/projects/replica-a/backup_manifest.json": (
        7589,
        "cd75d9a631249d66ce1513694c1e1290dcee72194ab4c7f5f50bc14b19a301e5",
    ),
    "live-lane/projects/replica-b/backup_manifest.json": (
        7589,
        "1de6f0b642229d2a01ed81b03ec8bf034d4aec36935ea5f955b188c5e6400054",
    ),
}

PRE_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18610.gbf"
STABLE_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18611.gbf"
POST_DB_PATH = "BEA.rep/idata/00/~00000000.db/db.18612.gbf"
PROJECTION_SOURCE = f"{LIVE_LANE_REL}/runs/live-readback/functions.tsv"

CLAIMS = (
    "The sealed scratch authority still reproduces its two independent persistent replicas and adverse controls.",
    "Two fresh db.18611 disposable replicas and the live project reproduce the same exact 31 manifest-bound structural function additions.",
    "All 8,170 PRE function rows are byte-identical after promotion; the POST-only address set is exactly the 31-row manifest and matches the sealed scratch readback rows.",
    "The live run has one writable apply and exactly one successful save between read-only PRE/dry and separate read-only POST/readback runs.",
    "Live, tracked, POST backup, and retained POST restore-probe project bytes are identical at 19 files and 186,911,621 bytes with db.18612 as the rolling database.",
    "The tracked 8,201-row name projection is mechanically reproduced from the exact POST full inventory.",
    "This authority admits exact body ownership only; default FUN names are placeholders and original symbols, semantics, runtime reachability, and reconstruction parity remain unauthorized.",
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


def exact_comparison(value: Mapping[str, Any], label: str) -> None:
    require(value.get("matches") is True, f"{label} did not match")
    for field in ("missingCount", "extraCount", "sizeDiffCount", "hashDiffCount"):
        require(value.get(field) == 0, f"{label} {field}")
    for field in ("missing", "extra", "sizeDifferences", "hashDifferences"):
        require(value.get(field) == [], f"{label} {field}")


def portable_path(value: Any, expected: str, label: str) -> None:
    require(isinstance(value, str) and value == expected, f"{label} path differs")
    require("\\" not in value and ":" not in value and not value.startswith("/"),
            f"{label} is not repository-relative POSIX")


@dataclass(frozen=True)
class Config:
    repo: Path
    live_lane: Path
    scratch_repo: Path
    live_project: Path
    pre_backup: Path
    post_backup: Path
    output: Path

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
    def scratch_receipt(self) -> Path:
        return self.scratch_repo / SCRATCH_RECEIPT_REL


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
    return {key: value.get(key) for key in
            ("projectName", "fileCount", "totalBytes", "structurallyComplete", "files")}


def project_digest(value: Mapping[str, Any]) -> str:
    rows = list(value.get("files", []))
    paths = [str(row["relative_path"]) for row in rows]
    require(paths == sorted(paths), "project rows are not relative-path ordered")
    raw = "".join(
        f"{row['sha256']}\t{row['size']}\t{row['relative_path']}\n" for row in rows
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


def require_project(value: Mapping[str, Any], expected: Mapping[str, Any], label: str) -> None:
    require(value.get("projectName") == "BEA", f"{label} project name")
    require(value.get("structurallyComplete") is True, f"{label} structural completeness")
    measured = project_summary(value)
    for key, wanted in expected.items():
        require(measured.get(key) == wanted, f"{label} {key} differs")


def require_same_project(left: Mapping[str, Any], right: Mapping[str, Any], label: str) -> None:
    require(project_without_root(left) == project_without_root(right), f"{label} bytes differ")


def project_file_map(value: Mapping[str, Any]) -> dict[str, tuple[int, str]]:
    return {
        str(row["relative_path"]): (int(row["size"]), str(row["sha256"]))
        for row in value.get("files", [])
    }


def validate_inspect(path: Path, expected: Mapping[str, Any], label: str) -> datetime:
    value = load_json(path, label)
    require(value.get("schemaVersion") == project_backup.SCHEMA_VERSION, f"{label} schema")
    require_same_project(value.get("manifest", {}), expected, label)
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


def validate_restore(
    lane: Path,
    receipt_name: str,
    probe_root_name: str,
    expected: Mapping[str, Any],
    expected_functions: int,
    label: str,
) -> tuple[dict[str, Any], datetime]:
    receipt_path = lane / receipt_name
    value = load_json(receipt_path, label)
    require(value.get("schemaVersion") == project_backup.SCHEMA_VERSION, f"{label} schema")
    require(value.get("sourceStable") is True, f"{label} source stability")
    require(value.get("probeCopyDisposition") == "RETAINED_AT_VERIFICATION",
            f"{label} probe disposition")
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
    argv = opened.get("commandArgv")
    require(isinstance(argv, list), f"{label} command argv")
    for token in ("-readOnly", "-noanalysis", "GhidraProjectOpenProbe.java"):
        require(argv.count(token) == 1, f"{label} missing/duplicate {token}")
    require("-commit" not in argv, f"{label} restore probe requested a commit")

    log_claim = opened.get("probeLog", {})
    expected_log = receipt_name.replace(".json", ".open-probe.log")
    portable_path(log_claim.get("path"), expected_log, f"{label} probe log")
    log_path = lane / expected_log
    log_stamp = stamp(log_path, f"live-lane/{expected_log}")
    require(
        (log_claim.get("bytes"), log_claim.get("sha256"))
        == (log_stamp["bytes"], log_stamp["sha256"]),
        f"{label} probe-log binding",
    )
    log = log_path.read_text(encoding="utf-8")
    sentinel = (
        f"GHIDRA_PROJECT_OPEN_PROBE_OK program={PROGRAM_NAME} md5={PROGRAM_MD5} "
        f"sha256={PROGRAM_SHA256} functions={expected_functions}"
    )
    require(log.count(sentinel) == 1, f"{label} success sentinel")
    for marker in project_backup.GHIDRA_OPEN_ERROR_MARKERS:
        require(marker not in log, f"{label} error marker: {marker}")

    probe_root = lane / probe_root_name
    retained = sorted(path for path in probe_root.iterdir() if path.is_dir())
    require(len(retained) == 1, f"{label} retained probe count")
    require(Path(str(value.get("probeCopy", ""))).name == retained[0].name,
            f"{label} retained probe basename")
    retained_project = project_value(retained[0])
    require_same_project(retained_project, expected, f"{label} retained probe")
    retained_manifest = retained[0] / "backup_manifest.json"
    validate_backup_manifest(retained_manifest, expected, f"{label} retained copy")
    return {
        "receipt": stamp(receipt_path, f"live-lane/{receipt_name}"),
        "probeLog": log_stamp,
        "retainedProject": project_summary(retained_project),
        "retainedCopyReceipt": stamp(
            retained_manifest, f"live-lane/{probe_root_name}/retained/backup_manifest.json"
        ),
        "observedInternalAndExternalFunctions": expected_functions,
        "readOnly": True,
        "contentStable": True,
    }, parse_utc(value.get("verifiedAtUtc"), f"{label} verifiedAtUtc")


def validate_repo_files(config: Config) -> dict[str, Any]:
    ledger: dict[str, Any] = {}
    for relative, expected in EXPECTED_REPO_FILES.items():
        ledger[relative] = verify_stamp(config.repo / relative, expected, relative)
    return ledger


def validate_lane_stamps(config: Config) -> dict[str, Any]:
    return {
        relative: verify_stamp(
            config.live_lane / relative, expected, f"live-lane/{relative}"
        )
        for relative, expected in EXPECTED_LANE_ARTIFACTS.items()
    }


def validate_scratch(config: Config) -> dict[str, Any]:
    tool = config.scratch_repo / "tools/ghidra_text_gap_boundary_scratch_authority.py"
    verify_stamp(tool, EXPECTED_REPO_FILES["tools/ghidra_text_gap_boundary_scratch_authority.py"],
                 "scratch-authority/tool")
    receipt_stamp = verify_stamp(
        config.scratch_receipt,
        EXPECTED_EXTERNAL["scratch-authority/ready.json"],
        "scratch-authority/ready.json",
    )
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, str(tool), "verify"],
        cwd=config.scratch_repo,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=900,
    )
    require(result.returncode == 0, f"scratch authority verify failed: {result.stderr.strip()}")
    sentinel = (
        "TEXT_GAP_SCRATCH_AUTHORITY_VERIFIED "
        f"sha256={EXPECTED_EXTERNAL['scratch-authority/ready.json'][1]} "
        "live_authorized=false"
    )
    require(result.stdout.count(sentinel) == 1, "scratch authority sentinel")
    recorded = load_json(config.scratch_receipt, "scratch authority receipt")
    require(recorded.get("schemaVersion") == scratch.SCHEMA, "scratch authority schema")
    require(recorded.get("verdict") == "SCRATCH_ADMISSION_READY_LIVE_NOT_AUTHORIZED",
            "scratch authority verdict")
    require(recorded.get("summary") == {
        "targets": 31,
        "bodyBytes": 14049,
        "preFunctions": 8170,
        "postFunctions": 8201,
        "preInstructions": 549872,
        "postInstructions": 550982,
        "newInstructions": 1110,
        "preReferences": 234357,
        "postReferences": 234537,
        "newReferences": 180,
        "preservedPreFunctionRows": 8170,
        "replicas": 2,
        "adverseControls": 2,
        "externalPathPreflights": 2,
    }, "scratch authority summary")
    require(recorded.get("liveMutationAuthorized") is False
            and recorded.get("trackedGhidraMutationAuthorized") is False,
            "scratch authority mutation boundary")
    return {
        "receipt": receipt_stamp,
        "semanticVerifyRebuilt": True,
        "targets": 31,
        "replicas": 2,
        "adverseControls": 2,
    }


def load_targets(path: Path) -> list[dict[str, str]]:
    rows = scratch.read_tsv(path)
    require(len(rows) == TARGETS, "target manifest count")
    require([row.get("candidateId") for row in rows]
            == [f"CF-{index:03d}" for index in range(1, TARGETS + 1)],
            "target manifest ids")
    entries = [str(row.get("retailEntry", "")).lower() for row in rows]
    require(len(set(entries)) == TARGETS, "target manifest duplicate entries")
    return rows


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


def validate_target_row(row: Mapping[str, str], target: Mapping[str, str]) -> None:
    address = target["retailEntry"].lower()
    ranges = target["retailBodyRangesHalfOpen"].lower().split(";")
    parsed = [tuple(int(value, 16) for value in item.split("-", 1)) for item in ranges]
    require(row.get("address") == address, f"target address {address}")
    require(row.get("name") == "FUN_" + address[2:] and row.get("nameSource") == "DEFAULT",
            f"target default name {address}")
    require(row.get("bodyBytes") == target["bodyBytes"], f"target body bytes {address}")
    require(row.get("bodyMin") == f"0x{min(start for start, _ in parsed):08x}",
            f"target body min {address}")
    require(row.get("bodyMax") == f"0x{max(end for _, end in parsed) - 1:08x}",
            f"target body max {address}")
    require(row.get("bodyRanges") == str(len(parsed)), f"target range count {address}")
    require(row.get("bodyDigest") == target["bodyRangeSha256"], f"target range digest {address}")
    require(row.get("instrCount") == target["instructionCount"],
            f"target instruction count {address}")


def validate_function_delta(
    pre_path: Path,
    post_path: Path,
    scratch_post_path: Path,
    targets: list[dict[str, str]],
) -> dict[str, Any]:
    pre = raw_tsv(pre_path, "address")
    post = raw_tsv(post_path, "address")
    scratch_post = raw_tsv(scratch_post_path, "address")
    require(pre.fields == post.fields == scratch_post.fields, "function headers differ")
    require(len(pre.rows) == PRE_FUNCTIONS and len(post.rows) == POST_FUNCTIONS,
            "function census differs")
    require(set(pre.rows) <= set(post.rows), "PRE address was destroyed")
    for address, before in pre.raw_rows.items():
        require(post.raw_rows.get(address) == before, f"PRE row changed at {address}")
    target_by_address = {row["retailEntry"].lower(): row for row in targets}
    created = set(post.rows) - set(pre.rows)
    require(created == set(target_by_address), "POST-only target set differs")
    for address, target in target_by_address.items():
        validate_target_row(post.rows[address], target)
        require(post.raw_rows[address] == scratch_post.raw_rows.get(address),
                f"live/scratch target row differs at {address}")
    return {
        "pre": stamp(pre_path, "live-lane/runs/live-pre-readback/functions.tsv"),
        "post": stamp(post_path, "live-lane/runs/live-readback/functions.tsv"),
        "preRowsByteIdentical": PRE_FUNCTIONS,
        "createdAddressesExactManifest": TARGETS,
        "createdRowsByteIdenticalToScratch": TARGETS,
        "destroyed": 0,
    }


def validate_program_delta(pre_path: Path, post_path: Path) -> dict[str, Any]:
    before = scratch.program_rows(pre_path)
    after = scratch.program_rows(post_path)
    require(before == scratch.PRE_PROGRAM | {
        key: value for key, value in before.items() if key.startswith("block:")
    }, "PRE program metrics")
    require(after == scratch.POST_PROGRAM | {
        key: value for key, value in after.items() if key.startswith("block:")
    }, "POST program metrics")
    require(set(before) == set(after), "program metric set differs")
    changed = {key for key in before if before[key] != after[key]}
    expected = {
        "functions", "instructions", "instructionLayoutSha256", "undefinedData",
        "symbolsDefaultOther", "references", "referencesSha256",
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


RUN_LAYOUT = {
    "replica-a": {"dry": "replica-a-dry", "apply": "replica-a-apply", "readback": "replica-a-readback"},
    "replica-b": {"dry": "replica-b-dry", "apply": "replica-b-apply", "readback": "replica-b-readback"},
    "live": {"dry": "live-pre-readback", "apply": "live-apply", "readback": "live-readback"},
}


def validate_run_file_set(root: Path, mode: str, *, live: bool) -> None:
    expected = {"boundaries.ready.json", "boundaries.tsv", "ghidra.log"}
    if mode == "readback" or (live and mode == "dry"):
        expected |= {"functions.tsv", "program.tsv"}
    if live and mode == "readback":
        expected.add("inventory-diff.json")
    actual = {path.name for path in root.iterdir() if path.is_file()}
    require(actual == expected, f"unexpected run file set for {root.name}: {sorted(actual)}")


def validate_run_receipt(
    config: Config,
    run_name: str,
    mode: str,
    targets: list[dict[str, str]],
) -> datetime:
    root = config.live_lane / "runs" / run_name
    boundary_path = root / "boundaries.tsv"
    receipt = load_json(root / "boundaries.ready.json", f"{run_name} receipt")
    require(receipt.get("schemaVersion") == "bea.ghidra.text-gap-boundaries.v2",
            f"{run_name} schema")
    require(receipt.get("mode") == mode, f"{run_name} mode")
    portable_path(receipt.get("tool", {}).get("path"),
                  "tools/GhidraApplyTextGapBoundaries.java", f"{run_name} tool")
    require(
        (receipt["tool"].get("bytes"), receipt["tool"].get("sha256"))
        == EXPECTED_REPO_FILES["tools/GhidraApplyTextGapBoundaries.java"],
        f"{run_name} tool binding",
    )
    portable_path(receipt.get("manifest", {}).get("path"), MANIFEST_REL,
                  f"{run_name} manifest")
    require(
        (receipt["manifest"].get("bytes"), receipt["manifest"].get("sha256"))
        == EXPECTED_REPO_FILES[MANIFEST_REL],
        f"{run_name} manifest binding",
    )
    output_rel = f"{LIVE_LANE_REL}/runs/{run_name}/boundaries.tsv"
    portable_path(receipt.get("output", {}).get("path"), output_rel, f"{run_name} output")
    measured = stamp(boundary_path, f"live-lane/runs/{run_name}/boundaries.tsv")
    require((receipt["output"].get("bytes"), receipt["output"].get("sha256"))
            == (measured["bytes"], measured["sha256"]), f"{run_name} output binding")
    require(receipt.get("program") == {
        "name": PROGRAM_NAME, "md5": PROGRAM_MD5, "sha256": PROGRAM_SHA256,
    }, f"{run_name} program identity")
    expected_counts = {
        "dry": {"targets": 31, "functionsBefore": 8170, "functionsAfter": 8170,
                "instructionsBefore": 549872, "instructionsAfter": 549872},
        "apply": {"targets": 31, "functionsBefore": 8170, "functionsAfter": 8201,
                  "instructionsBefore": 549872, "instructionsAfter": 550982},
        "readback": {"targets": 31, "functionsBefore": 8201, "functionsAfter": 8201,
                     "instructionsBefore": 550982, "instructionsAfter": 550982},
    }[mode]
    require(receipt.get("counts") == expected_counts, f"{run_name} counts")
    require(receipt.get("explicitBodySetsAuthorized") is True
            and receipt.get("namesAuthorized") is False
            and receipt.get("metadataAuthorized") is False
            and receipt.get("separateReadbackRequired") is (mode != "readback"),
            f"{run_name} claim boundary")
    scratch.verify_boundary_rows(boundary_path, mode, targets)
    return parse_utc(receipt.get("completedAtUtc"), f"{run_name} completedAtUtc")


def validate_run_log(path: Path, mode: str, *, live: bool) -> dict[str, int]:
    text = path.read_text(encoding="utf-8")
    require(text.count(f"TEXT_GAP_BOUNDARIES_OK mode={mode}") == 1,
            f"{path.parent.name} success marker")
    for marker in ("REPORT SCRIPT ERROR", "TEXT_GAP_BOUNDARIES_FAIL", "Exception"):
        require(marker not in text, f"{path.parent.name} error marker: {marker}")
    saves = text.count("Save succeeded for processed file: /BEA.exe")
    read_only = text.count("Processing read-only project file: /BEA.exe")
    writable = len(re.findall(r"Processing project file: /BEA\.exe", text))
    if mode == "apply":
        require((saves, read_only, writable) == (1, 0, 1),
                f"{path.parent.name} writable/save shape")
    else:
        require((saves, read_only, writable) == (0, 1, 0),
                f"{path.parent.name} read-only shape")
    return {"successfulSaves": saves, "readOnlyOpens": read_only, "writableOpens": writable}


def validate_runs(
    config: Config,
    targets: list[dict[str, str]],
) -> tuple[dict[str, Any], dict[str, datetime]]:
    times: dict[str, datetime] = {}
    summaries: dict[str, Any] = {}
    total_live_saves = 0
    for owner, modes in RUN_LAYOUT.items():
        owner_summary: dict[str, Any] = {}
        for mode, run_name in modes.items():
            root = config.live_lane / "runs" / run_name
            validate_run_file_set(root, mode, live=owner == "live")
            times[f"{owner}.{mode}.receipt"] = validate_run_receipt(
                config, run_name, mode, targets
            )
            log_shape = validate_run_log(root / "ghidra.log", mode, live=owner == "live")
            if owner == "live":
                total_live_saves += log_shape["successfulSaves"]
            owner_summary[mode] = {
                "receipt": stamp(root / "boundaries.ready.json",
                                 f"live-lane/runs/{run_name}/boundaries.ready.json"),
                "boundaries": stamp(root / "boundaries.tsv",
                                    f"live-lane/runs/{run_name}/boundaries.tsv"),
                "log": stamp(root / "ghidra.log", f"live-lane/runs/{run_name}/ghidra.log"),
                **log_shape,
            }
        summaries[owner] = owner_summary
    require(total_live_saves == 1, "live run did not contain exactly one successful save")

    pre_functions = config.live_lane / "runs/live-pre-readback/functions.tsv"
    pre_program = config.live_lane / "runs/live-pre-readback/program.tsv"
    post_functions = config.live_lane / "runs/live-readback/functions.tsv"
    post_program = config.live_lane / "runs/live-readback/program.tsv"
    scratch_post = (
        config.scratch_repo / SCRATCH_LANE_REL / "runs/replica-a-readback/functions.tsv"
    )
    function_delta = validate_function_delta(pre_functions, post_functions, scratch_post, targets)
    program_delta = validate_program_delta(pre_program, post_program)
    scratch.verify_diff(config.live_lane / "runs/live-readback/inventory-diff.json", targets)

    for replica in ("replica-a", "replica-b"):
        root = config.live_lane / "runs" / f"{replica}-readback"
        require((root / "functions.tsv").read_bytes() == post_functions.read_bytes(),
                f"{replica} full functions differ from live POST")
        require((root / "program.tsv").read_bytes() == post_program.read_bytes(),
                f"{replica} full program differs from live POST")
        times[f"{replica}.readback.complete"] = mtime_utc(root / "program.tsv")

    times["live.dry.complete"] = mtime_utc(pre_program)
    times["live.readback.complete"] = mtime_utc(post_program)
    times["live.inventoryDiff.complete"] = mtime_utc(
        config.live_lane / "runs/live-readback/inventory-diff.json"
    )
    return {
        "runs": summaries,
        "liveSuccessfulSaves": total_live_saves,
        "functionDelta": function_delta,
        "programDelta": program_delta,
        "inventoryDiff": stamp(
            config.live_lane / "runs/live-readback/inventory-diff.json",
            "live-lane/runs/live-readback/inventory-diff.json",
        ),
    }, times


def validate_projects(
    config: Config,
) -> tuple[dict[str, Any], dict[str, datetime]]:
    pre = project_value(config.pre_backup)
    post = project_value(config.post_backup)
    live = project_value(config.live_project)
    tracked = project_value(config.tracked_project)
    require_project(pre, PRE_PROJECT, "PRE project")
    for label, value in (("POST backup", post), ("live", live), ("tracked", tracked)):
        require_project(value, POST_PROJECT, label)
    require_same_project(live, post, "live/POST backup")
    require_same_project(tracked, post, "tracked/POST backup")

    pre_map = project_file_map(pre)
    post_map = project_file_map(post)
    require(pre_map.get(PRE_DB_PATH) == DB_18610, "PRE db.18610 identity")
    require(pre_map.get(STABLE_DB_PATH) == DB_18611, "PRE db.18611 identity")
    require(POST_DB_PATH not in pre_map, "PRE unexpectedly contains db.18612")
    require(post_map.get(STABLE_DB_PATH) == DB_18611, "POST db.18611 identity")
    require(post_map.get(POST_DB_PATH) == DB_18612, "POST db.18612 identity")
    require(PRE_DB_PATH not in post_map, "POST retained db.18610")
    removed = sorted(set(pre_map) - set(post_map))
    added = sorted(set(post_map) - set(pre_map))
    changed = sorted(path for path in set(pre_map) & set(post_map)
                     if pre_map[path] != post_map[path])
    require(removed == [PRE_DB_PATH] and added == [POST_DB_PATH] and changed == [],
            "project rolling delta differs")

    times: dict[str, datetime] = {}
    times["live.pre.inspect"] = validate_inspect(
        config.live_lane / "live-pre-inspect.json", pre, "live PRE inspect"
    )
    times["tracked.pre.inspect"] = validate_inspect(
        config.live_lane / "tracked-pre-inspect.json", pre, "tracked PRE inspect"
    )
    times["live.beforeApply.inspect"] = validate_inspect(
        config.live_lane / "live-before-apply-inspect.json", pre,
        "live before-apply inspect",
    )
    times["live.post.inspect"] = validate_inspect(
        config.live_lane / "live-post-inspect.json", post, "live POST inspect"
    )
    times["tracked.post.inspect"] = validate_inspect(
        config.live_lane / "tracked-post-inspect.json", post, "tracked POST inspect"
    )

    pre_manifest = config.pre_backup / "backup_manifest.json"
    post_manifest = config.post_backup / "backup_manifest.json"
    verify_stamp(pre_manifest, EXPECTED_EXTERNAL["pre-backup/backup_manifest.json"],
                 "pre-backup/backup_manifest.json")
    verify_stamp(post_manifest, EXPECTED_EXTERNAL["post-backup/backup_manifest.json"],
                 "post-backup/backup_manifest.json")
    times["pre.backup.created"] = validate_backup_manifest(
        pre_manifest, pre, "PRE backup manifest"
    )
    times["post.backup.created"] = validate_backup_manifest(
        post_manifest, post, "POST backup manifest"
    )

    pre_restore, times["pre.restore.verified"] = validate_restore(
        config.live_lane, "pre-backup-restore.ready.json", "pre-backup-restore-probe",
        pre, 8394, "PRE restore",
    )
    post_restore, times["post.restore.verified"] = validate_restore(
        config.live_lane, "post-backup-restore.ready.json", "post-backup-restore-probe",
        post, 8425, "POST restore",
    )
    tracked_restore, times["tracked.restore.verified"] = validate_restore(
        config.live_lane, "tracked-post-restore.ready.json", "tracked-post-restore-probe",
        post, 8425, "tracked POST restore",
    )

    replica_summaries: dict[str, Any] = {}
    for replica in ("replica-a", "replica-b"):
        root = config.live_lane / "projects" / replica
        current = project_value(root)
        require_project(current, REPLICA_PROJECTS[replica], f"{replica} persisted project")
        current_map = project_file_map(current)
        require(set(current_map) == set(post_map), f"{replica} persisted path set")
        require(
            all(
                current_map[path] == post_map[path]
                for path in post_map
                if path != POST_DB_PATH
            ),
            f"{replica} changed a non-rolling project file",
        )
        require(current_map[POST_DB_PATH][0] == DB_18612[0],
                f"{replica} rolling database size")
        manifest_path = root / "backup_manifest.json"
        verify_stamp(
            manifest_path,
            EXPECTED_EXTERNAL[f"live-lane/projects/{replica}/backup_manifest.json"],
            f"live-lane/projects/{replica}/backup_manifest.json",
        )
        times[f"{replica}.copy.created"] = validate_backup_manifest(
            manifest_path, pre, f"{replica} initial copy"
        )
        replica_summaries[replica] = {
            "initialCopy": project_summary(pre),
            "persistedProject": project_summary(current),
            "onlyRollingDatabaseSerializationDiffersFromLivePost": True,
            "backupReceipt": stamp(
                manifest_path, f"live-lane/projects/{replica}/backup_manifest.json"
            ),
        }

    return {
        "pre": project_summary(pre),
        "post": project_summary(post),
        "liveEqualsPost": True,
        "trackedEqualsPost": True,
        "postBackupEqualsPost": True,
        "rollingDelta": {
            "removed": removed,
            "added": added,
            "changedCommonFiles": changed,
            "byteDelta": int(post["totalBytes"]) - int(pre["totalBytes"]),
            "stableDatabase": {"path": STABLE_DB_PATH, "bytes": DB_18611[0], "sha256": DB_18611[1]},
            "rollingDatabase": {"path": POST_DB_PATH, "bytes": DB_18612[0], "sha256": DB_18612[1]},
        },
        "replicas": replica_summaries,
        "restores": {
            "pre": pre_restore, "post": post_restore, "trackedPost": tracked_restore,
        },
        "backupReceipts": {
            "pre": stamp(pre_manifest, "pre-backup/backup_manifest.json"),
            "post": stamp(post_manifest, "post-backup/backup_manifest.json"),
        },
    }, times


def validate_projection(config: Config) -> tuple[dict[str, Any], datetime]:
    inventory = config.live_lane / "runs/live-readback/functions.tsv"
    lane_projection = config.live_lane / "ghidra-function-name-table-2026-08-13.tsv"
    tracked_projection = config.projection
    expected = name_projection.projection_bytes(
        inventory,
        expected_inventory_sha256=scratch.POST_FUNCTIONS_SHA256,
        source_label=PROJECTION_SOURCE,
        projection_date="2026-08-14",
        specimen_sha256=PROGRAM_SHA256,
    )
    require(lane_projection.read_bytes() == expected, "retained projection is not mechanical")
    require(tracked_projection.read_bytes() == expected, "tracked projection is not mechanical")
    data_rows = sum(
        1 for line in expected.splitlines()
        if line and not line.startswith(b"#")
    ) - 1
    require(data_rows == POST_FUNCTIONS, "projection row count")
    measured = {
        "rows": data_rows,
        "bytes": len(expected),
        "sha256": hashlib.sha256(expected).hexdigest(),
        "sourceInventory": stamp(inventory, "live-lane/runs/live-readback/functions.tsv"),
        "retained": stamp(lane_projection, "live-lane/ghidra-function-name-table-2026-08-13.tsv"),
        "tracked": stamp(tracked_projection, PROJECTION_REL),
        "sourceLabel": PROJECTION_SOURCE,
    }
    require((measured["bytes"], measured["sha256"])
            == EXPECTED_REPO_FILES[PROJECTION_REL], "projection identity")
    return measured, mtime_utc(lane_projection)


def validate_chronology(
    project_times: Mapping[str, datetime],
    run_times: Mapping[str, datetime],
    projection_time: datetime,
) -> list[dict[str, str]]:
    events = {
        **project_times,
        **run_times,
        "projection.complete": projection_time,
    }
    order = [
        "live.pre.inspect",
        "tracked.pre.inspect",
        "pre.backup.created",
        "pre.restore.verified",
        "replica-a.copy.created",
        "replica-b.copy.created",
        "replica-a.dry.receipt",
        "replica-b.dry.receipt",
        "replica-a.apply.receipt",
        "replica-b.apply.receipt",
        "replica-a.readback.receipt",
        "replica-b.readback.receipt",
        "replica-a.readback.complete",
        "replica-b.readback.complete",
        "live.dry.receipt",
        "live.dry.complete",
        "live.beforeApply.inspect",
        "live.apply.receipt",
        "live.readback.receipt",
        "live.readback.complete",
        "live.inventoryDiff.complete",
        "live.post.inspect",
        "post.backup.created",
        "post.restore.verified",
        "tracked.post.inspect",
        "tracked.restore.verified",
        "projection.complete",
    ]
    for left, right in zip(order, order[1:]):
        require(events[left] < events[right], f"chronology does not advance: {left} -> {right}")
    return [{"event": name, "atUtc": utc_text(events[name])} for name in order]


def ensure_portable(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            ensure_portable(key)
            ensure_portable(child)
    elif isinstance(value, list):
        for child in value:
            ensure_portable(child)
    elif isinstance(value, str):
        require(not re.match(r"^[A-Za-z]:[\\/]", value),
                f"aggregate payload contains an absolute Windows path: {value}")
        require(not value.startswith("/"),
                f"aggregate payload contains an absolute POSIX path: {value}")
        require("\\" not in value, f"aggregate payload contains a non-portable separator: {value}")


def build(config: Config) -> dict[str, Any]:
    repo_files = validate_repo_files(config)
    lane_files = validate_lane_stamps(config)
    scratch_result = validate_scratch(config)
    targets = load_targets(config.manifest)
    projects, project_times = validate_projects(config)
    runs, run_times = validate_runs(config, targets)
    projection, projection_time = validate_projection(config)
    chronology = validate_chronology(project_times, run_times, projection_time)
    value = {
        "baseCommit": BASE_COMMIT,
        "program": {"name": PROGRAM_NAME, "md5": PROGRAM_MD5, "sha256": PROGRAM_SHA256},
        "artifactLedger": {
            "repository": repo_files,
            "liveLane": lane_files,
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


def clean_path(path: Path) -> Path:
    return Path(os.path.abspath(path))


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def validate_output(config: Config, *, sealing: bool) -> None:
    output = clean_path(config.output)
    forbidden = (
        config.live_lane,
        config.scratch_repo / SCRATCH_LANE_REL,
        config.live_project,
        config.pre_backup,
        config.post_backup,
        config.tracked_project,
    )
    require(not any(is_within(output, clean_path(root)) for root in forbidden),
            "aggregate receipt overlaps an evidence or project root")
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
        "completedAtUtc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "authorityTool": stamp(Path(__file__).resolve(), "tools/ghidra_text_gap_boundary_live_authority.py"),
        "evidence": build(config),
        "ghidraOpenedByAuthority": False,
        "liveGhidraMutatedByAuthority": False,
        "trackedGhidraMutatedByAuthority": False,
        "futureMutationAuthorized": False,
    }
    ensure_portable(value)
    atomic_new_json(config.output, value)
    print(
        "TEXT_GAP_LIVE_AUTHORITY_READY "
        f"receipt_sha256={sha256_file(config.output)} functions={POST_FUNCTIONS} targets={TARGETS}"
    )


def verify(config: Config) -> None:
    validate_output(config, sealing=False)
    recorded = load_json(config.output, "aggregate authority receipt")
    require(recorded.get("schemaVersion") == SCHEMA, "aggregate schema")
    parse_utc(recorded.get("completedAtUtc"), "aggregate completedAtUtc")
    require(recorded.get("authorityTool")
            == stamp(Path(__file__).resolve(), "tools/ghidra_text_gap_boundary_live_authority.py"),
            "aggregate authority-tool binding")
    require(recorded.get("ghidraOpenedByAuthority") is False
            and recorded.get("liveGhidraMutatedByAuthority") is False
            and recorded.get("trackedGhidraMutatedByAuthority") is False
            and recorded.get("futureMutationAuthorized") is False,
            "aggregate mutation boundary")
    require(recorded.get("evidence") == build(config), "aggregate evidence does not reproduce")
    ensure_portable(recorded)
    print(
        "TEXT_GAP_LIVE_AUTHORITY_VERIFIED "
        f"receipt_sha256={sha256_file(config.output)} functions={POST_FUNCTIONS} targets={TARGETS}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("seal", "verify"))
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--live-lane", type=Path, required=True)
    parser.add_argument("--scratch-repo", type=Path, required=True)
    parser.add_argument("--live-project", type=Path, required=True)
    parser.add_argument("--pre-backup", type=Path, required=True)
    parser.add_argument("--post-backup", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = Config(*(clean_path(value) for value in (
        args.repo, args.live_lane, args.scratch_repo, args.live_project,
        args.pre_backup, args.post_backup, args.output,
    )))
    if args.command == "seal":
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
        print(f"TEXT_GAP_LIVE_AUTHORITY_REFUSED reason={exc}", file=sys.stderr)
        raise SystemExit(1)
