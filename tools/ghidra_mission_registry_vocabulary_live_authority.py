#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Seal the completed 75-row Mission-registry vocabulary live promotion.

This target-specific owner is read-only except for its explicit JSON output.
It never launches or opens Ghidra.  It validates the committed ceremony inputs,
the final scratch authority, live dry/apply/separate-readback evidence, PRE and
POST recovery copies, live/tracked/POST byte equality, the refreshed name
projection, and exact full-inventory collateral before publishing one receipt.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


SCRIPT = Path(__file__).resolve()
AUTHORITY_TOOL_RELATIVE = Path(
    "tools/ghidra_mission_registry_vocabulary_live_authority.py"
)
SCHEMA = "bea.ghidra.mission-registry-vocabulary-live-authority.v1"
TOOL_SCHEMA = "bea.ghidra.mission-registry-vocabulary.v1"
BACKUP_SCHEMA = "onslaught-ghidra-project-backup.v2"
BASE_COMMIT = "0132d3cdd55a335e1f0d3e64de0f13de24477356"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
PROGRAM_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
CANONICAL_MAPPING_SHA256 = "39a9f2f01eb82c9f1924f716cb621dd9d9f680f7c584315e770f7731a0da9992"
PRE_PROJECT_SHA256 = "682950bbb57b2658d8cbbe1894bfac66902392e5fff91513f85b4592532137a0"
POST_PROJECT_SHA256 = "b0635c394c57ddbc7ccbe8f239c2fec811e445bffca7d813e1d562c0d350c6ef"
PROJECTION_SHA256 = "f7f987b55730fb074d8b1fe31998553a9b94432dea31b1134f6a207defdfa51e"
SCRATCH_SEAL_SHA256 = "1ee8f6b1a9cca61857f528f173b40828172ed0bee82dc751ec65e26276d3b4e0"
FUNCTION_COUNT = 8_170
OPEN_FUNCTION_COUNT = 8_394
INSTRUCTION_COUNT = 549_872
TARGET_COUNT = 75
PROJECT_FILES = 19
PRE_PROJECT_BYTES = 186_551_173
POST_PROJECT_BYTES = 186_665_861
ANALYZE_HEADLESS = Path(
    r"D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC\support\analyzeHeadless.bat"
)

PRE_FUNCTIONS_STAMP = (
    7_082_637,
    "8aa8b4468f463053d25084de86bec2a701ed1064c13f77fd47d16f9dda6cf259",
)
PRE_PROGRAM_STAMP = (
    1_267,
    "cb4c2194e30e074e443779d9b42587072568f104fc76f671d40757af7b106075",
)
POST_FUNCTIONS_STAMP = (
    7_086_689,
    "da9f20a5ae3de150546e5b103bd9914e1a4ec7492bbafe5d35c4cc79b46d4756",
)
POST_PROGRAM_STAMP = (
    1_267,
    "c29aa646da238babd81b2bd1206e3c0d6f853d74f2aca237bbb008c64be52f87",
)

# Git blob identities and the hashes of the normalized blob bytes.  A working
# tree may have a filter-equivalent terminal newline representation; the Git
# hash-object check below proves that its normalized content is this exact blob.
COMMITTED_FILES: dict[str, tuple[str, int, str]] = {
    "tools/GhidraApplyMissionRegistryVocabulary.java": (
        "9707b0963e85f3e278be61946ac41b23d31ea6d5", 52_561,
        "bcb34399d628b5c23cee88f96bcf056b530804e93d91288eb4984a514ed066ff",
    ),
    "tools/ExportFullFunctionInventory.java": (
        "07873c2c0c55892b7ebf57afd3bdc8d2020c5f00", 23_963,
        "04519cd813f2fc25ddea8a6660f87c010f8aa4e053560993e4b35cafcc0b5197",
    ),
    "tools/GhidraProjectOpenProbe.java": (
        "ef59c6053bf9585d60c49dd78342529e82065189", 3_452,
        "fab2f701dfefe8604c1718d007dbe0ad59d330a9b3ec081ef2f2fe253b441fab",
    ),
    "tools/ghidra_project_backup.py": (
        "9e965d7a1c62419428b61d94b4fb1fc0078da5bb", 27_502,
        "0f426982916f0aab982efe54664342a5d34607c2f89707159ecf6c07e205ad58",
    ),
    "tools/ghidra_mission_registry_vocabulary_authority.py": (
        "69a9a775871aad7a8804638c5221a3cf8bac6506", 37_038,
        "7939a37067124961af8ecc1f86c4cf81118716e6b5c405dac700f4ce3ef11b5f",
    ),
    "tools/ghidra_mission_registry_vocabulary_authority_tests.py": (
        "81f8b13e1195cbc77a6613981426497f379c8b1c", 6_574,
        "46d2f8c9783401649d370f6731858280570b3cb716b9a9a24540ca078727a64a",
    ),
    "tools/ghidra_mission_registry_vocabulary_mutator_tests.py": (
        "b31abe5a21da7b6083a0e36ccded45efd0a2ed00", 3_787,
        "d7b96e8bf39de679e28a142c55db890e9ca16e91a4f5b0afe4c219904ca30e1a",
    ),
    "reverse-engineering/binary-analysis/mission-script-registry-vocabulary-normalization-2026-08-13.tsv": (
        "34e87e145bb4bdfe1dac35c5286f64a8738a86e3", 7_299,
        "a30897bbb1c842fa046af62f3dc1f91b7888af162963d01422074f083c513145",
    ),
    "reverse-engineering/binary-analysis/mission-script-registry-vocabulary-normalization-pre-metadata-2026-08-13.tsv": (
        "ac9c2eb4161de375fdb9fafed08a0f04bbf874a5", 22_628,
        "cc7cc62d64bcd62f6024f2b4ccc66c369426853c638ba90a773d537fd269470b",
    ),
    "reverse-engineering/binary-analysis/mission-script-registry-vocabulary-normalization-2026-08-13.md": (
        "205de0341589913f5af5676a5261c75c49fceae7", 11_148,
        "ac26beab94426fff3d30a04490200ce41e125787d5f5ad0784ee37dfd0114e01",
    ),
}

LIVE_ARTIFACT_STAMPS: dict[str, tuple[int, str]] = {
    "ghidra-function-name-table-2026-08-13.tsv": (502_868, PROJECTION_SHA256),
    "live-pre-inspect.json": (3_760, "6db2901135c85830eac41c6587ca1b1457c9daddac9f62d4dc04731eb1458345"),
    "tracked-pre-inspect.json": (3_804, "c493d3a9aae6e9649887591f32a4485776fcf427835fccd14230cac3a57cc4f7"),
    "live-post-inspect.json": (3_760, "5d0bb89765dbee06ec79d6c6b8e13341371cf68bfcce4e54377dc90e7bb24a50"),
    "tracked-post-inspect.json": (3_804, "5935147106ff25e0a7d59e23b8344ffcc530ee6edeab409e9cd40a74df658a95"),
    "pre-backup-restore.ready.json": (5_924, "be14d6eb4980b17b28b9b1afa1930b392817ac2278bde7af1bee7a5a792b4746"),
    "pre-backup-restore.ready.open-probe.log": (4_532, "b44db89e67fed01fbd1edc9860736620ef839fb4ea01739b252aa4255f9f3ffe"),
    "post-backup-restore.ready.json": (5_928, "1fde14015dc9a55132d3b5b93452a93e8c1b0ff2a0cfee603f37eedab82f9ebd"),
    "post-backup-restore.ready.open-probe.log": (4_534, "73ba37ddf775ef858ea7377d785bcee79d598ee3834f19b50f5551dff44b75e7"),
    "tracked-snapshot-restore.ready.json": (5_945, "3e87b1d7fc2665c6c04b78b2cffa69889e9815d928b99dc0e28fa87122d61470"),
    "tracked-snapshot-restore.ready.open-probe.log": (4_540, "9f1785d37f8db9f02c7f85b03009de317c27f2fca66b135415d52b8f4648d7d5"),
    "runs/live-dry/ghidra.log": (5_316, "48c45e012cf87d905d577211bb58d25bcbe1aba78ed28522694d134d726f15e9"),
    "runs/live-dry/vocabulary.ready.json": (2_451, "91f96d54a631d53727c8cbf65d3e19711d06fe2fa0acdb199305e0b9100ca0dd"),
    "runs/live-dry/vocabulary.tsv": (34_601, "f35cf3f835f74c0d2af432952029b7870185b68e5a1292300fdeaf91f785dc8f"),
    "runs/live-apply/ghidra.log": (5_438, "df4e2c7f14705cbc162c7a7ba04d250ebd2d42e90bf2d3179204d127eac096d4"),
    "runs/live-apply/vocabulary.ready.json": (2_455, "9e5f1e98b511294e20bde6c7babf8f3df35cc848316013f7fccfc1b05ee97487"),
    "runs/live-apply/vocabulary.tsv": (38_528, "7acce453f894e5bc65cc2a68fb43782ee8bf0db3c97f5c7d6a4d48d103e913a3"),
    "runs/live-readback/ghidra.log": (6_120, "844fcae30864fc3213530bf6344ae70cd3a531ad72ec86f9381db2ec0cf77712"),
    "runs/live-readback/vocabulary.ready.json": (2_461, "e19d69331969718a4c0832c6155a556769a66fdc49feda8e74e8e139d5a07232"),
    "runs/live-readback/vocabulary.tsv": (38_753, "00720bb074deae89b857c051ca39435ec7c182940fa3890abef47f47e6d8d033"),
    "runs/live-readback/functions.tsv": POST_FUNCTIONS_STAMP,
    "runs/live-readback/program.tsv": POST_PROGRAM_STAMP,
}

BACKUP_MANIFEST_STAMPS = {
    "PRE": (7_589, "0ebb538d9b5e933c2860e88b5f0e223faea6f39416746a12a1d52994037a12ff"),
    "POST": (7_589, "81e9e15bda6ab8cb3faf027725d6eac8cf0d16e1f26cc4df891ac0799ce632d1"),
}

SCRATCH_FILE_STAMPS = {
    "pre/functions.tsv": PRE_FUNCTIONS_STAMP,
    "pre/program.tsv": PRE_PROGRAM_STAMP,
    "runs/replica-a-dry/vocabulary.tsv": LIVE_ARTIFACT_STAMPS["runs/live-dry/vocabulary.tsv"],
    "runs/replica-a-apply/vocabulary.tsv": LIVE_ARTIFACT_STAMPS["runs/live-apply/vocabulary.tsv"],
    "runs/replica-a-readback/vocabulary.tsv": LIVE_ARTIFACT_STAMPS["runs/live-readback/vocabulary.tsv"],
    "runs/replica-a-readback/functions.tsv": POST_FUNCTIONS_STAMP,
    "runs/replica-a-readback/program.tsv": POST_PROGRAM_STAMP,
}

ALLOWED_TARGET_FIELDS = {
    "name", "nameLen", "nameSha256", "fqname", "fqnameLen", "fqnameSha256",
    "nameSource", "signature", "signatureLen", "signatureSha256",
    "commentPresent", "commentLen", "commentSha256", "tagCount", "tagsSha256", "tags",
}
EXPECTED_CHANGED_TARGET_FIELDS = sorted(ALLOWED_TARGET_FIELDS)
EXPECTED_PROGRAM_CHANGES = sorted(
    {"comments", "commentsSha256", "symbolsDefaultOther", "symbolsUserDefined"}
)


class AuthorityError(RuntimeError):
    pass


@dataclass(frozen=True)
class Config:
    shared_repo: Path
    live_lane: Path
    scratch_seal: Path
    live_project: Path
    pre_backup: Path
    post_backup: Path
    output: Path

    @property
    def tracked_project(self) -> Path:
        return self.shared_repo / "reverse-engineering/ghidra"

    @property
    def projection(self) -> Path:
        return self.shared_repo / (
            "reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-13.tsv"
        )

    @property
    def manifest(self) -> Path:
        return self.shared_repo / (
            "reverse-engineering/binary-analysis/"
            "mission-script-registry-vocabulary-normalization-2026-08-13.tsv"
        )

    @property
    def scratch_formal(self) -> Path:
        return self.scratch_seal.parent


def require(value: bool, message: str) -> None:
    if not value:
        raise AuthorityError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stamp(path: Path) -> dict[str, Any]:
    path = Path(os.path.abspath(path))
    require(path.is_file(), f"required file is absent: {path}")
    stat = path.stat()
    require(not path.is_symlink(), f"file is a symlink: {path}")
    require(not (getattr(stat, "st_file_attributes", 0) & 0x400),
            f"file is a reparse point: {path}")
    require(stat.st_nlink == 1, f"file is not single-link: {path}")
    return {"path": str(path), "bytes": stat.st_size, "sha256": sha256_file(path)}


def require_stamp(path: Path, expected: tuple[int, str], label: str) -> dict[str, Any]:
    actual = stamp(path)
    require((actual["bytes"], actual["sha256"]) == expected,
            f"{label} identity differs: {actual}")
    return actual


def authority_tool_stamp(config: Config) -> dict[str, Any]:
    """Bind the running tool to its repository copy without a checkout path."""
    running = stamp(SCRIPT)
    shared = stamp(config.shared_repo / AUTHORITY_TOOL_RELATIVE)
    require(
        (running["bytes"], running["sha256"])
        == (shared["bytes"], shared["sha256"]),
        "running authority tool differs from the shared repository copy",
    )
    return {
        "path": AUTHORITY_TOOL_RELATIVE.as_posix(),
        "bytes": shared["bytes"],
        "sha256": shared["sha256"],
    }


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise AuthorityError(f"invalid JSON at {path}: {exc}") from exc


def read_tsv(path: Path, *, comments: bool = False) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        lines = (line for line in stream if not comments or not line.startswith("#"))
        return list(csv.DictReader(lines, delimiter="\t"))


def parse_utc(value: Any, label: str) -> None:
    require(isinstance(value, str) and value.endswith("Z"), f"{label} is not UTC")
    try:
        datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise AuthorityError(f"{label} is malformed") from exc


def project_fields(value: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value.get(key) for key in
            ("projectName", "fileCount", "totalBytes", "structurallyComplete", "files")}


def plain_project(root: Path, cache: dict[Path, dict[str, Any]] | None = None) -> dict[str, Any]:
    root = Path(os.path.abspath(root))
    if cache is not None and root in cache:
        return cache[root]
    require(root.is_dir(), f"project root is absent: {root}")
    files: list[dict[str, Any]] = []
    total = 0
    for path in [root, *root.rglob("*")]:
        stat = path.lstat()
        require(not path.is_symlink(), f"project contains symlink: {path}")
        require(not (getattr(stat, "st_file_attributes", 0) & 0x400),
                f"project contains reparse point: {path}")
        if not path.is_file() or path.name == "backup_manifest.json":
            continue
        require(stat.st_nlink == 1, f"project contains linked file: {path}")
        relative = path.relative_to(root).as_posix()
        if relative != "BEA.gpr" and not relative.startswith("BEA.rep/"):
            continue
        files.append({"relative_path": relative, "sha256": sha256_file(path),
                      "size": stat.st_size})
        total += stat.st_size
    files.sort(key=lambda row: row["relative_path"])
    result = {
        "projectName": "BEA", "fileCount": len(files), "totalBytes": total,
        "structurallyComplete": any(row["relative_path"] == "BEA.gpr" for row in files)
        and any(row["relative_path"].startswith("BEA.rep/") for row in files),
        "files": files,
    }
    if cache is not None:
        cache[root] = result
    return result


def canonical_project_digest(project: Mapping[str, Any]) -> str:
    lines = sorted(
        f"{row['sha256']}\t{row['size']}\t{row['relative_path']}"
        for row in project.get("files", [])
    )
    return sha256_bytes(("\n".join(lines) + "\n").encode("utf-8"))


def project_summary(project: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "fileCount": project.get("fileCount"), "totalBytes": project.get("totalBytes"),
        "canonicalInventorySha256": canonical_project_digest(project),
        "canonicalization": (
            "sha256<TAB>bytes<TAB>relative-posix-path<LF>, sorted by rendered line"
        ),
    }


def run_git(repo: Path, *args: str, binary: bool = False) -> bytes | str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], check=False, capture_output=True,
        text=not binary,
    )
    require(result.returncode == 0,
            f"git {' '.join(args)} failed: {result.stderr if not binary else result.stderr.decode(errors='replace')}")
    return result.stdout if binary else result.stdout.strip()


def validate_committed_inputs(config: Config) -> dict[str, Any]:
    head = str(run_git(config.shared_repo, "rev-parse", "HEAD"))
    resolved = str(run_git(config.shared_repo, "rev-parse", BASE_COMMIT + "^{commit}"))
    require(resolved == BASE_COMMIT, "ceremony base commit does not resolve exactly")
    run_git(config.shared_repo, "merge-base", "--is-ancestor", BASE_COMMIT, head)
    files: dict[str, Any] = {}
    for relative, (expected_oid, expected_bytes, expected_sha) in COMMITTED_FILES.items():
        oid = str(run_git(config.shared_repo, "rev-parse", f"{BASE_COMMIT}:{relative}"))
        require(oid == expected_oid, f"committed blob differs: {relative}")
        blob = run_git(config.shared_repo, "cat-file", "blob", oid, binary=True)
        require(isinstance(blob, bytes), "binary Git read returned text")
        require((len(blob), sha256_bytes(blob)) == (expected_bytes, expected_sha),
                f"committed blob bytes differ: {relative}")
        work_path = config.shared_repo / relative
        working = stamp(work_path)
        normalized_oid = str(run_git(
            config.shared_repo, "hash-object", "--path", relative, str(work_path)
        ))
        require(normalized_oid == expected_oid,
                f"working file does not normalize to committed blob: {relative}")
        run_git(config.shared_repo, "diff", "--quiet", BASE_COMMIT, "--", relative)
        run_git(config.shared_repo, "diff", "--cached", "--quiet", BASE_COMMIT, "--", relative)
        files[relative] = {
            "blobOid": oid, "blobBytes": expected_bytes, "blobSha256": expected_sha,
            "workingFile": working, "filterNormalizedToBlob": True,
        }
    return {"commit": BASE_COMMIT, "isAncestorOfCurrentHead": True, "files": files,
            "historicalScratchVerifierIsOneShot": True}


def validate_artifact_ledger(config: Config) -> dict[str, Any]:
    require(config.live_lane.is_dir(), f"live evidence lane is absent: {config.live_lane}")
    actual: dict[str, Any] = {}
    measured = {
        path.relative_to(config.live_lane).as_posix()
        for path in config.live_lane.rglob("*") if path.is_file()
        and "restore-probe" not in path.relative_to(config.live_lane).parts
    }
    require(set(LIVE_ARTIFACT_STAMPS) <= measured,
            f"live evidence ledger is missing files: {sorted(set(LIVE_ARTIFACT_STAMPS) - measured)}")
    for relative, expected in LIVE_ARTIFACT_STAMPS.items():
        actual[relative] = require_stamp(config.live_lane / relative, expected, relative)
    return actual


def validate_scratch(config: Config) -> dict[str, Any]:
    seal_stamp = require_stamp(
        config.scratch_seal, (17_087, SCRATCH_SEAL_SHA256), "final scratch authority"
    )
    value = load_json(config.scratch_seal)
    require(value.get("schema") == "bea.ghidra.mission-registry-vocabulary-authority.v1",
            "scratch authority schema differs")
    parse_utc(value.get("completedAtUtc"), "scratch completedAtUtc")
    require(value.get("verdict") == "SCRATCH_AUTHORITY_READY_LIVE_FORBIDDEN" and
            value.get("liveGhidraMutated") is False and
            value.get("trackedGhidraMutated") is False and
            value.get("liveMutationAuthorized") is False,
            "scratch authority claim boundary differs")
    require(value.get("authorityTool", {}).get("bytes") == 37_038 and
            value.get("authorityTool", {}).get("sha256") ==
            COMMITTED_FILES["tools/ghidra_mission_registry_vocabulary_authority.py"][2],
            "scratch authority tool binding differs")
    evidence = value.get("evidence", {})
    require(evidence.get("canonicalProjection") == {
        "bytes": 4_035, "sha256": CANONICAL_MAPPING_SHA256,
    }, "scratch canonical mapping differs")
    functions = evidence.get("functionCollateral", {})
    require(functions.get("targets") == TARGET_COUNT and
            functions.get("nonTargetsByteIdentical") == FUNCTION_COUNT - TARGET_COUNT and
            functions.get("changedTargetFields") == EXPECTED_CHANGED_TARGET_FIELDS,
            "scratch function collateral differs")
    program = evidence.get("programCollateral", {})
    require(program.get("changedMetrics") == EXPECTED_PROGRAM_CHANGES and
            program.get("newUserSymbols") == 54 and
            program.get("retiredDefaultSymbols") == 54 and
            program.get("newComments") == 54,
            "scratch program collateral differs")
    files: dict[str, Any] = {}
    for relative, expected in SCRATCH_FILE_STAMPS.items():
        files[relative] = require_stamp(
            config.scratch_formal / relative, expected, "scratch " + relative
        )
    for phase in ("dry", "apply", "readback"):
        live = config.live_lane / f"runs/live-{phase}/vocabulary.tsv"
        scratch = config.scratch_formal / f"runs/replica-a-{phase}/vocabulary.tsv"
        require(live.read_bytes() == scratch.read_bytes(),
                f"live {phase} output differs from final scratch authority")
    for name in ("functions.tsv", "program.tsv"):
        live = config.live_lane / "runs/live-readback" / name
        scratch = config.scratch_formal / "runs/replica-a-readback" / name
        require(live.read_bytes() == scratch.read_bytes(),
                f"live {name} differs from final scratch authority")
    return {"seal": seal_stamp, "criticalFiles": files,
            "livePhaseOutputsByteIdentical": True,
            "livePostInventoriesByteIdentical": True}


def load_manifest(config: Config) -> dict[str, dict[str, str]]:
    rows = read_tsv(config.manifest)
    require(len(rows) == TARGET_COUNT, "target manifest row count differs")
    result = {row["handlerVa"].lower(): row for row in rows}
    require(len(result) == TARGET_COUNT, "target manifest addresses are not unique")
    require(len({row["proposedName"] for row in rows}) == TARGET_COUNT,
            "target manifest names are not unique")
    canonical = "".join(
        f"{row['index']}\t{row['handlerVa']}\t{row['expectedPreName']}\t{row['proposedName']}\n"
        for row in rows
    ).encode("utf-8")
    require(len(canonical) == 4_035 and sha256_bytes(canonical) == CANONICAL_MAPPING_SHA256,
            "target manifest canonical mapping differs")
    return result


def validate_tool_receipt(config: Config, phase: str,
                          mode: str, state: str) -> dict[str, Any]:
    root = config.live_lane / "runs" / ("live-" + phase)
    path = root / "vocabulary.ready.json"
    value = load_json(path)
    require(value.get("schema") == TOOL_SCHEMA and value.get("mode") == mode and
            value.get("state") == state, f"{phase} receipt identity differs")
    parse_utc(value.get("completedAtUtc"), f"{phase} completedAtUtc")
    require(value.get("program") == {
        "name": "BEA.exe", "md5": PROGRAM_MD5, "sha256": PROGRAM_SHA256,
        "functions": FUNCTION_COUNT, "instructions": INSTRUCTION_COUNT,
    }, f"{phase} program identity differs")
    require(value.get("targets") == {
        "total": 75, "DEFAULT54": 54, "MSG5": 5, "CLASS3_16": 16,
    }, f"{phase} target partition differs")
    require(value.get("mutation") == {
        "namesChanged": 75, "commentsChanged": 75, "newFunctionComments": 54,
        "tagAssociationsAdded": 130, "tagAssociationsRemoved": 3,
        "tagDefinitionsAdded": 1, "boundariesChanged": 0, "abiChanged": 0,
        "bytesChanged": 0, "instructionsChanged": 0, "referencesChanged": 0,
    }, f"{phase} mutation boundary differs")
    expected_catalog = (
        {"count": 6_853,
         "definitionsSha256": "351e7234d66db90af13a4f4ecfd3df9e1ed7f6db6b9828f97f0758f8cdeef811",
         "usageSha256": "bc7a8ba82155bb7a8f33fbb4ec2ebc15684dffa11b75b212338baf3eca06efd9"}
        if state == "PRE" else
        {"count": 6_854,
         "definitionsSha256": "074dd7480aebfe46aabe5a48c1429348a814c9b51b0d71d985cbdac6e764603f",
         "usageSha256": "a23aa97dca8f2f36646abc90a12363581a4d87610cc897b4c5558a8044bbcd78"}
    )
    require(value.get("tagCatalog") == expected_catalog, f"{phase} tag catalog differs")
    input_paths = {
        "tool": "tools/GhidraApplyMissionRegistryVocabulary.java",
        "manifest": "reverse-engineering/binary-analysis/mission-script-registry-vocabulary-normalization-2026-08-13.tsv",
        "preMetadata": "reverse-engineering/binary-analysis/mission-script-registry-vocabulary-normalization-pre-metadata-2026-08-13.tsv",
        "owner": "reverse-engineering/binary-analysis/mission-script-registry-vocabulary-normalization-2026-08-13.md",
    }
    for key, relative in input_paths.items():
        measured = value.get(key, {})
        actual = stamp(config.shared_repo / relative)
        require(Path(str(measured.get("path", ""))).resolve() ==
                (config.shared_repo / relative).resolve(), f"{phase} {key} path differs")
        require((measured.get("bytes"), measured.get("sha256")) ==
                (actual["bytes"], actual["sha256"]), f"{phase} {key} stamp differs")
    output = stamp(root / "vocabulary.tsv")
    measured_output = value.get("output", {})
    require(Path(str(measured_output.get("path", ""))).resolve() ==
            (root / "vocabulary.tsv").resolve(), f"{phase} output path differs")
    require((measured_output.get("bytes"), measured_output.get("sha256")) ==
            (output["bytes"], output["sha256"]), f"{phase} output stamp differs")
    require(value.get("commitRequested") is (mode == "apply") and
            value.get("nestedEndReturnedCommitted") is False and
            value.get("loadedStateVerified") is (mode == "readback"),
            f"{phase} transaction/readback flags differ")
    require(value.get("registryNamesAreOriginalCppSymbols") is False and
            value.get("behaviorContractsAuthorized") is False and
            value.get("liveMutationAuthorized") is False,
            f"{phase} claim boundary differs")
    rows = read_tsv(root / "vocabulary.tsv")
    require(len(rows) == TARGET_COUNT and len({row["handlerVa"] for row in rows}) == TARGET_COUNT,
            f"{phase} vocabulary census differs")
    require({row["mode"] for row in rows} == {mode} and
            {row["state"] for row in rows} == {state}, f"{phase} row state differs")
    return {"receipt": stamp(path), "table": output, "rows": rows}


def validate_log(config: Config, phase: str, marker: str,
                 *, writable: bool, inventory: bool = False) -> dict[str, Any]:
    path = config.live_lane / f"runs/live-{phase}/ghidra.log"
    text = path.read_text(encoding="utf-8", errors="strict")
    require(text.count(marker) == 1 and "REPORT SCRIPT ERROR" not in text,
            f"{phase} success/error marker differs")
    require(f"Opening existing project: {config.live_project / 'BEA'}" in text,
            f"{phase} does not name the live maintainer project")
    processing = "REPORT: Processing project file: /BEA.exe" if writable else \
        "REPORT: Processing read-only project file: /BEA.exe"
    require(processing in text, f"{phase} processing mode differs")
    require(str(config.shared_repo / "tools/GhidraApplyMissionRegistryVocabulary.java") in text,
            f"{phase} mutator path differs")
    require(("Save succeeded for processed file: /BEA.exe" in text) is writable,
            f"{phase} save marker differs")
    if inventory:
        require(str(config.shared_repo / "tools/ExportFullFunctionInventory.java") in text and
                "INVENTORY_OK functions=8170 instructions=549872" in text,
                f"{phase} full inventory marker differs")
    return stamp(path)


def validate_one_mutation_log(runs_root: Path) -> dict[str, Any]:
    logs = sorted(runs_root.glob("live-*/ghidra.log"))
    expected = [runs_root / f"live-{phase}/ghidra.log"
                for phase in ("apply", "dry", "readback")]
    require(logs == sorted(expected), f"live Ghidra log set differs: {logs}")
    mutating = []
    for path in logs:
        text = path.read_text(encoding="utf-8", errors="strict")
        if "MISSION_REGISTRY_VOCABULARY_APPLY_COMPLETE" in text or \
                "REPORT: Processing project file: /BEA.exe" in text or \
                "Save succeeded for processed file: /BEA.exe" in text:
            mutating.append(path)
    require(mutating == [runs_root / "live-apply/ghidra.log"],
            "mutation-log census differs from exactly one live apply")
    return {"logs": len(logs), "mutationLogs": 1,
            "mutationLog": stamp(mutating[0])}


def inventory_rows(path: Path) -> dict[str, dict[str, str]]:
    rows = read_tsv(path)
    result = {row["address"].lower(): row for row in rows}
    require(len(rows) == len(result) == FUNCTION_COUNT,
            f"full function inventory census differs: {path}")
    return result


def compare_inventory_records(pre: Mapping[str, Mapping[str, str]],
                              post: Mapping[str, Mapping[str, str]],
                              targets: Mapping[str, Mapping[str, str]]) -> dict[str, Any]:
    require(pre.keys() == post.keys(), "function address set changed")
    require(set(targets) <= set(pre), "target is absent from full inventory")
    non_target_differences = []
    changed_fields: set[str] = set()
    for address in pre:
        if address not in targets:
            if pre[address] != post[address]:
                non_target_differences.append(address)
            continue
        before, after, target = pre[address], post[address], targets[address]
        changed = {key for key in before if before[key] != after[key]}
        require(changed and changed <= ALLOWED_TARGET_FIELDS,
                f"forbidden/empty target delta at {address}: {sorted(changed)}")
        changed_fields.update(changed)
        require(before["name"] == target["expectedPreName"] and
                after["name"] == after["fqname"] == target["proposedName"] and
                after["nameSource"] == "USER_DEFINED",
                f"target name delta differs at {address}")
        require(after["signature"] == before["signature"].replace(
            target["expectedPreName"], target["proposedName"], 1),
            f"signature rendered beyond name substitution at {address}")
    require(not non_target_differences,
            f"non-target rows changed: {non_target_differences[:8]}")
    require(sorted(changed_fields) == EXPECTED_CHANGED_TARGET_FIELDS,
            f"aggregate target fields differ: {sorted(changed_fields)}")
    return {"targetsChangedOnlyWithinAllowedFields": len(targets),
            "nonTargetsByteIdentical": len(pre) - len(targets),
            "changedTargetFields": sorted(changed_fields)}


def compare_programs(pre_path: Path, post_path: Path) -> dict[str, Any]:
    before = {row["metric"]: row["value"] for row in read_tsv(pre_path)}
    after = {row["metric"]: row["value"] for row in read_tsv(post_path)}
    require(before.keys() == after.keys(), "program metric keys changed")
    changed = sorted(key for key in before if before[key] != after[key])
    require(changed == EXPECTED_PROGRAM_CHANGES, f"program collateral differs: {changed}")
    require(int(after["symbolsUserDefined"]) - int(before["symbolsUserDefined"]) == 54 and
            int(before["symbolsDefaultOther"]) - int(after["symbolsDefaultOther"]) == 54 and
            int(after["comments"]) - int(before["comments"]) == 54,
            "expected symbol/comment deltas differ")
    require(after["functions"] == str(FUNCTION_COUNT) and
            after["instructions"] == str(INSTRUCTION_COUNT) and
            after["executableSHA256"] == PROGRAM_SHA256,
            "program identity/census differs")
    return {"changedMetrics": changed, "newUserSymbols": 54,
            "retiredDefaultSymbols": 54, "newComments": 54}


def crosscheck_vocabulary(rows: Sequence[Mapping[str, str]],
                          functions: Mapping[str, Mapping[str, str]]) -> None:
    for row in rows:
        function = functions[row["handlerVa"].lower()]
        for output_key, inventory_key in (
            ("name", "name"), ("nameSource", "nameSource"),
            ("commentLen", "commentLen"), ("commentSha256", "commentSha256"),
            ("repeatableCommentSha256", "repeatableCommentSha256"),
            ("tagCount", "tagCount"), ("tags", "tags"),
        ):
            require(row[output_key] == function[inventory_key],
                    f"vocabulary/full-inventory mismatch at {row['handlerVa']}: {output_key}")


def validate_runs_and_collateral(config: Config) -> dict[str, Any]:
    dry = validate_tool_receipt(config, "dry", "dry", "PRE")
    apply = validate_tool_receipt(config, "apply", "apply", "POST")
    readback = validate_tool_receipt(config, "readback", "readback", "POST")
    logs = {
        "dry": validate_log(config, "dry", "MISSION_REGISTRY_VOCABULARY_DRY_COMPLETE",
                            writable=False),
        "apply": validate_log(config, "apply", "MISSION_REGISTRY_VOCABULARY_APPLY_COMPLETE",
                              writable=True),
        "readback": validate_log(
            config, "readback", "MISSION_REGISTRY_VOCABULARY_READBACK_COMPLETE",
            writable=False, inventory=True),
    }
    mutation = validate_one_mutation_log(config.live_lane / "runs")
    targets = load_manifest(config)
    pre_path = config.scratch_formal / "pre/functions.tsv"
    post_path = config.live_lane / "runs/live-readback/functions.tsv"
    pre, post = inventory_rows(pre_path), inventory_rows(post_path)
    collateral = compare_inventory_records(pre, post, targets)
    program = compare_programs(
        config.scratch_formal / "pre/program.tsv",
        config.live_lane / "runs/live-readback/program.tsv",
    )
    crosscheck_vocabulary(dry["rows"], pre)
    crosscheck_vocabulary(apply["rows"], post)
    crosscheck_vocabulary(readback["rows"], post)
    return {
        "dry": {key: value for key, value in dry.items() if key != "rows"},
        "apply": {key: value for key, value in apply.items() if key != "rows"},
        "readback": {key: value for key, value in readback.items() if key != "rows"},
        "logs": logs, "mutationProcessCensus": mutation,
        "functionCollateral": collateral, "programCollateral": program,
    }


def validate_inspect(path: Path, expected_root: Path,
                     expected: Mapping[str, Any], label: str) -> dict[str, Any]:
    value = load_json(path)
    require(value.get("schemaVersion") == BACKUP_SCHEMA, f"{label} schema differs")
    parse_utc(value.get("createdAtUtc"), f"{label} createdAtUtc")
    manifest = value.get("manifest", {})
    require(Path(str(manifest.get("root", ""))).resolve() == expected_root.resolve(),
            f"{label} root differs")
    require(project_fields(manifest) == project_fields(expected), f"{label} project differs")
    return stamp(path)


def validate_backup(root: Path, expected_stamp: tuple[int, str], label: str,
                    cache: dict[Path, dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest_path = root / "backup_manifest.json"
    manifest_stamp = require_stamp(manifest_path, expected_stamp, f"{label} manifest")
    value = load_json(manifest_path)
    require(value.get("schemaVersion") == BACKUP_SCHEMA and
            value.get("sourceStable") is True and
            value.get("copyComparison", {}).get("matches") is True,
            f"{label} backup gate differs")
    require(value.get("readonlyOpen") is None, f"{label} copy manifest unexpectedly opened")
    project = plain_project(root, cache)
    require(project_fields(value.get("source", {})) == project and
            project_fields(value.get("destination", {})) == project,
            f"{label} backup bytes differ from its manifest")
    return project, manifest_stamp


def validate_restore(config: Config, relative: str, expected_root: Path,
                     expected_project: Mapping[str, Any], label: str,
                     cache: dict[Path, dict[str, Any]]) -> dict[str, Any]:
    path = config.live_lane / relative
    value = load_json(path)
    require(value.get("schemaVersion") == BACKUP_SCHEMA and
            value.get("sourceStable") is True and
            value.get("copyComparison", {}).get("matches") is True,
            f"{label} restore copy differs")
    source = value.get("source", {})
    require(Path(str(source.get("root", ""))).resolve() == expected_root.resolve() and
            project_fields(source) == project_fields(expected_project),
            f"{label} restore source differs")
    opened = value.get("readonlyOpen", {})
    require(opened.get("opened") is True and opened.get("contentStable") is True and
            opened.get("postOpenComparison", {}).get("matches") is True and
            opened.get("exitCode") == 0,
            f"{label} read-only open failed")
    require(opened.get("observedProgramName") == "BEA.exe" and
            opened.get("observedProgramMd5") == PROGRAM_MD5 and
            opened.get("observedProgramSha256") == PROGRAM_SHA256 and
            opened.get("observedFunctionCount") == OPEN_FUNCTION_COUNT,
            f"{label} opened program identity differs")
    probe_copy = Path(str(value.get("probeCopy", ""))).resolve()
    require(value.get("probeCopyDisposition") == "RETAINED_AT_VERIFICATION" and
            probe_copy.is_relative_to(config.live_lane.resolve()),
            f"{label} probe-copy disposition/root differs")
    require(plain_project(probe_copy, cache) == project_fields(expected_project),
            f"{label} retained probe copy differs")
    expected_argv = [
        str(ANALYZE_HEADLESS), str(probe_copy), "BEA", "-process", "BEA.exe",
        "-readOnly", "-noanalysis", "-scriptPath", str(config.shared_repo / "tools"),
        "-postScript", "GhidraProjectOpenProbe.java", "BEA.exe", PROGRAM_MD5,
        PROGRAM_SHA256,
    ]
    require(opened.get("commandArgv") == expected_argv, f"{label} open command differs")
    log_claim = opened.get("probeLog", {})
    log_path = path.with_name(str(log_claim.get("path", "")))
    log = stamp(log_path)
    require((log_claim.get("bytes"), log_claim.get("sha256")) ==
            (log["bytes"], log["sha256"]), f"{label} probe log stamp differs")
    text = log_path.read_text(encoding="utf-8", errors="strict")
    sentinel = (f"GHIDRA_PROJECT_OPEN_PROBE_OK program=BEA.exe md5={PROGRAM_MD5} "
                f"sha256={PROGRAM_SHA256} functions={OPEN_FUNCTION_COUNT}")
    require(text.count(sentinel) == 1 and "GHIDRA_PROJECT_OPEN_PROBE_FAIL" not in text,
            f"{label} probe sentinel differs")
    return {"receipt": stamp(path), "probeLog": log, "retainedProbeMatches": True}


def validate_projects_and_recovery(config: Config) -> dict[str, Any]:
    cache: dict[Path, dict[str, Any]] = {}
    pre, pre_manifest = validate_backup(
        config.pre_backup, BACKUP_MANIFEST_STAMPS["PRE"], "PRE", cache
    )
    post, post_manifest = validate_backup(
        config.post_backup, BACKUP_MANIFEST_STAMPS["POST"], "POST", cache
    )
    require(project_summary(pre) == {
        "fileCount": PROJECT_FILES, "totalBytes": PRE_PROJECT_BYTES,
        "canonicalInventorySha256": PRE_PROJECT_SHA256,
        "canonicalization": (
            "sha256<TAB>bytes<TAB>relative-posix-path<LF>, sorted by rendered line"
        ),
    }, "PRE project summary differs")
    require(project_summary(post) == {
        "fileCount": PROJECT_FILES, "totalBytes": POST_PROJECT_BYTES,
        "canonicalInventorySha256": POST_PROJECT_SHA256,
        "canonicalization": (
            "sha256<TAB>bytes<TAB>relative-posix-path<LF>, sorted by rendered line"
        ),
    }, "POST project summary differs")
    pre_inspects = {
        "live": validate_inspect(config.live_lane / "live-pre-inspect.json",
                                 config.live_project, pre, "live PRE inspect"),
        "tracked": validate_inspect(config.live_lane / "tracked-pre-inspect.json",
                                    config.tracked_project, pre, "tracked PRE inspect"),
    }
    post_inspects = {
        "live": validate_inspect(config.live_lane / "live-post-inspect.json",
                                 config.live_project, post, "live POST inspect"),
        "tracked": validate_inspect(config.live_lane / "tracked-post-inspect.json",
                                    config.tracked_project, post, "tracked POST inspect"),
    }
    require(plain_project(config.live_project, cache) == post,
            "current live project differs from POST backup")
    require(plain_project(config.tracked_project, cache) == post,
            "current tracked snapshot differs from POST backup")
    restores = {
        "preBackup": validate_restore(
            config, "pre-backup-restore.ready.json", config.pre_backup, pre,
            "PRE backup restore", cache),
        "postBackup": validate_restore(
            config, "post-backup-restore.ready.json", config.post_backup, post,
            "POST backup restore", cache),
        "trackedSnapshot": validate_restore(
            config, "tracked-snapshot-restore.ready.json", config.tracked_project, post,
            "tracked snapshot restore", cache),
    }
    return {
        "pre": {"project": project_summary(pre), "backupManifest": pre_manifest,
                "inspections": pre_inspects, "restore": restores["preBackup"]},
        "post": {"project": project_summary(post), "backupManifest": post_manifest,
                 "inspections": post_inspects, "postRestore": restores["postBackup"],
                 "trackedRestore": restores["trackedSnapshot"]},
        "equality": {"liveEqualsPostBackup": True, "trackedEqualsLive": True,
                     "trackedEqualsPostBackup": True},
    }


def validate_projection(config: Config) -> dict[str, Any]:
    shared = require_stamp(config.projection, (502_868, PROJECTION_SHA256),
                           "shared current projection")
    retained = require_stamp(
        config.live_lane / "ghidra-function-name-table-2026-08-13.tsv",
        (502_868, PROJECTION_SHA256), "retained current projection",
    )
    require(config.projection.read_bytes() ==
            (config.live_lane / "ghidra-function-name-table-2026-08-13.tsv").read_bytes(),
            "shared and retained projections differ")
    text = config.projection.read_text(encoding="utf-8")
    require("# Source bytes: 7086689" in text and
            f"# Source SHA-256: {POST_FUNCTIONS_STAMP[1]}" in text and
            "# Rows    : 8170 internal functions;" in text,
            "projection source binding differs")
    rows = read_tsv(config.projection, comments=True)
    functions = list(inventory_rows(
        config.live_lane / "runs/live-readback/functions.tsv").values())
    expected = [{key: row[key] for key in ("address", "name", "bodyMin", "bodyMax")}
                for row in functions]
    require(rows == expected, "projection does not exactly derive from live readback")
    return {"shared": shared, "retained": retained, "rows": len(rows),
            "sourceFunctions": {"bytes": POST_FUNCTIONS_STAMP[0],
                                "sha256": POST_FUNCTIONS_STAMP[1]},
            "exactMechanicalProjection": True}


def build(config: Config, generated_at: str) -> dict[str, Any]:
    parse_utc(generated_at, "generatedAtUtc")
    artifact_ledger = validate_artifact_ledger(config)
    committed = validate_committed_inputs(config)
    scratch = validate_scratch(config)
    runs = validate_runs_and_collateral(config)
    projects = validate_projects_and_recovery(config)
    projection = validate_projection(config)
    return {
        "schema": SCHEMA,
        "generatedAtUtc": generated_at,
        "verdict": "LIVE_PROMOTION_SAVED_READ_BACK_BACKED_UP_AND_TRACKED",
        "claim": "SEVENTY_FIVE_MISSION_REGISTRY_SCRIPT_VOCABULARY_ROWS_PROMOTED",
        "authorityTool": authority_tool_stamp(config),
        "ceremonyBase": committed,
        "artifactLedger": artifact_ledger,
        "scratchAuthority": scratch,
        "liveRuns": runs,
        "projectsAndRecovery": projects,
        "currentProjection": projection,
        "result": {
            "targets": TARGET_COUNT, "default54": 54, "msg5": 5, "class3_16": 16,
            "liveMutationProcesses": 1, "internalFunctions": FUNCTION_COUNT,
            "externalFunctions": OPEN_FUNCTION_COUNT - FUNCTION_COUNT,
            "instructions": INSTRUCTION_COUNT,
            "nonTargetRowsByteIdentical": FUNCTION_COUNT - TARGET_COUNT,
            "boundariesChanged": 0, "abiChanged": 0, "bytesChanged": 0,
            "instructionsChanged": 0, "referencesChanged": 0,
            "postProjectFiles": PROJECT_FILES, "postProjectBytes": POST_PROJECT_BYTES,
            "postProjectInventorySha256": POST_PROJECT_SHA256,
            "projectionSha256": PROJECTION_SHA256,
        },
        "limitations": [
            "The promoted names are Tier-2 script-facing registry vocabulary, not recovered original C++ symbols.",
            "This promotion adds no behavior, ABI, failure-path, runtime-causality, reconstruction, or REBUILD_READY claim.",
            "The separately created 34 Mission-registry boundaries and 0x0050FF10 CreateExplosion are outside this cohort.",
            "Raw project equality proves this saved checkpoint only; later authorized Ghidra work may advance the live project.",
        ],
    }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def publish(path: Path, value: Mapping[str, Any]) -> None:
    require(not path.exists(), f"refusing to overwrite receipt: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")
    handle, temporary = tempfile.mkstemp(prefix="." + path.name + ".", dir=path.parent)
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def verify_saved(config: Config) -> None:
    saved = load_json(config.output)
    require(saved == build(config, saved.get("generatedAtUtc", "")),
            "saved live authority no longer reproduces")


def parse_config(args: argparse.Namespace) -> Config:
    return Config(*(Path(getattr(args, name)).resolve() for name in (
        "shared_repo", "live_lane", "scratch_seal", "live_project",
        "pre_backup", "post_backup", "output",
    )))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("seal", "verify"))
    parser.add_argument("--shared-repo", required=True)
    parser.add_argument("--live-lane", required=True)
    parser.add_argument("--scratch-seal", required=True)
    parser.add_argument("--live-project", required=True)
    parser.add_argument("--pre-backup", required=True)
    parser.add_argument("--post-backup", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    config = parse_config(args)
    if args.command == "seal":
        publish(config.output, build(config, utc_now()))
        print(f"MISSION_REGISTRY_VOCABULARY_LIVE_AUTHORITY_SEALED "
              f"sha256={sha256_file(config.output)}")
    else:
        verify_saved(config)
        print(f"MISSION_REGISTRY_VOCABULARY_LIVE_AUTHORITY_VERIFIED "
              f"sha256={sha256_file(config.output)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuthorityError as exc:
        print(f"AUTHORITY_REJECTED: {exc}")
        raise SystemExit(1)
