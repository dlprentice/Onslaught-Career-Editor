#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Seal the completed one-row CExplosion factory identity live promotion.

This target-specific owner is read-only except for its explicit JSON output.
It never launches or opens Ghidra.  It validates the committed ceremony inputs,
the final V7 scratch authority, live dry/apply/separate-readback evidence, PRE
and POST recovery copies, live/tracked/POST byte equality, the refreshed name
projection, tracked documentation pins, and exact full-inventory collateral
before publishing one receipt.
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
    "tools/ghidra_cexplosion_factory_identity_live_authority.py"
)
SCHEMA = "bea.ghidra.cexplosion-factory-identity-live-authority.v1"
TOOL_SCHEMA = "bea.ghidra.cexplosion-factory-identity.v1"
BACKUP_SCHEMA = "onslaught-ghidra-project-backup.v2"
BASE_COMMIT = "daf7b3c7512fdfb078dabe9d6cde6b2648c19e58"
PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55"
PROGRAM_SHA256 = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
MEMORY_SHA256 = "5398f750f1ffb59873a6ec7e1750b51d11b5b844a8fda8d4e43649b5b9e5089d"
PRE_PROJECT_SHA256 = "b0635c394c57ddbc7ccbe8f239c2fec811e445bffca7d813e1d562c0d350c6ef"
POST_PROJECT_SHA256 = "8eb664062a8ba67005e9f8ad8f61aa2222585622c41022a69080c5e408cd3cf6"
POST_DB_SHA256 = "210a0461a6b1746f7bbc53e883b616c4a02694a055f1bd23ccadaf44472c1356"
PROJECTION_SHA256 = "515170759dda2686db408d25296362275f8913f7be42b6f0536b986c591786ee"
SCRATCH_SEAL_SHA256 = "a7cc0d76b1429d4a18aaa68b9bc506d378f1663041438cf50593bf416218ab6e"
FUNCTION_COUNT = 8_170
OPEN_FUNCTION_COUNT = 8_394
INSTRUCTION_COUNT = 549_872
TARGET = "0x0050ff10"
TARGET_COUNT = 1
PROJECT_FILES = 19
PRE_PROJECT_BYTES = 186_665_861
POST_PROJECT_BYTES = 186_747_781
ANALYZE_HEADLESS = Path(
    r"D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC\support\analyzeHeadless.bat"
)

PRE_FUNCTIONS_STAMP = (
    7_086_689,
    "da9f20a5ae3de150546e5b103bd9914e1a4ec7492bbafe5d35c4cc79b46d4756",
)
PRE_PROGRAM_STAMP = (
    1_267,
    "c29aa646da238babd81b2bd1206e3c0d6f853d74f2aca237bbb008c64be52f87",
)
POST_FUNCTIONS_STAMP = (
    7_086_736,
    "8eded18abddfc0726517f2a88c7f4b2df15ff0cd13d3b70a5ca7ebd5a7afea5b",
)
POST_PROGRAM_STAMP = (
    1_267,
    "a3c505c34b7ba26dec7088d9ee22e0f9c13365ae979be1ffc8f52301e1f368c1",
)

# Git blob identities and the hashes of the normalized blob bytes.  A working
# tree may have a filter-equivalent terminal newline representation; the Git
# hash-object check below proves that its normalized content is this exact blob.
COMMITTED_FILES: dict[str, tuple[str, int, str]] = {
    "tools/GhidraApplyCExplosionFactoryIdentity.java": (
        "3de7e4b92e65de7118146c302a6b9147c52ac872", 39_751,
        "77ce5000c240673a25716f8ce5a42aa12fc7154d2362d7894893704b631c73d0",
    ),
    "tools/GhidraInspectCExplosionFactoryIdentity.java": (
        "4209e40498b231f7fcd9f9241f3e609846a977d3", 17_658,
        "8deb289dca518aa34a6219e95481c79cf4052a6a0a5aec27af6c4bb6f0b27655",
    ),
    "tools/ghidra_cexplosion_factory_identity_mutator_tests.py": (
        "88e7d1a35940ce7543d2492cbf86ad9619db8050", 6_758,
        "d808f9c7e9cbc4485e9f0c91af15233c3aaddf95ac241c36c036ccfa7124e643",
    ),
    "tools/ghidra_cexplosion_factory_identity_promotion_authority.py": (
        "57a99bd49b9c1de929211749b97cefa911586e42", 34_237,
        "09434170d4ff522b852c57181398d360445da6e537a521f47b8e7341c74619c0",
    ),
    "tools/ghidra_cexplosion_factory_identity_promotion_authority_tests.py": (
        "7b026f9cd8566d3d35ef09324069014f6c0ab927", 11_297,
        "56b4411b810d2a67ff2d04cc491e1424c5b15f0cd4228fc7aff863f95a3cdfd3",
    ),
    "tools/re_cexplosion_factory_identity_reproof.py": (
        "1d2d63d2ce6010996c96cf2313da6b084a70c4ac", 20_005,
        "54c6e6b0bc99923aff951cd4598a2f4c2e537e9dbbfdd8d969b10ffccea8d4c4",
    ),
    "tools/re_cexplosion_factory_identity_reproof_tests.py": (
        "9ded52169ef8c32d27034d1427a0ed2bcb2a0a52", 6_756,
        "4ee9284eb65268c38051dc808ab3b041ab06290f92751abb07280f1e0a240bfb",
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
    "tools/re_ghidra_name_projection.py": (
        "abf1255b6a780a4dd2d2f206068645efcafff0b6", 6_139,
        "d13d5f4d3b20cbd1e1baf24cd924d454c6c07b0bbf5517834c4089357f14ecdb",
    ),
    "reverse-engineering/binary-analysis/cexplosion-factory-identity-promotion-2026-08-13.md": (
        "81ee0c679ef5e268d23d1da9aa41a96840ecdd36", 6_950,
        "059e2a9a1a18b6fcf301238764e9cedc75e69fc057e7d16cb40c5f3fe0f57e31",
    ),
    "reverse-engineering/binary-analysis/cexplosion-factory-identity-promotion-2026-08-13.tsv": (
        "567052597cb3a079cb0cabc20d805809817cc160", 1_474,
        "4eb65da2e50c31dc6151c270808c2bdf83b2cea0b70f1a3ab60173ec55fbc1e8",
    ),
}

LIVE_ARTIFACT_STAMPS: dict[str, tuple[int, str]] = {
    # Filled only from the completed retained ceremony; every row is immutable.
    "ghidra-function-name-table-2026-08-13.tsv": (502_854, PROJECTION_SHA256),
    "live-pre-inspect.json": (3_760, "10c04b251c313a48744154a69f009b4602547e6d546791dd2390b9da9de2d997"),
    "tracked-pre-inspect.json": (3_804, "b203d8777bca56ed39c9e5668443e44d99369680e55ad5176bee43d481289aa5"),
    "live-after-dry-inspect.json": (3_760, "28104c1646030202e78e1e39dcf9cf2290c84335cef33fc955d12a2f1fbc1965"),
    "live-post-inspect.json": (3_760, "888c226c651e5e6293f0335695b1f31c4a8b68c85f84252894a7adeb2c6dc0a7"),
    "tracked-post-inspect.json": (3_804, "787ca4507b213118306d4bed23432bd03a7d260626cd9f108f3ba02a6574a67e"),
    "pre-backup-restore.ready.json": (5_881, "8d07c4c68aa95c033ca61a2611bf84fdf6b158f13d2ca03681717b360ad79f9d"),
    "pre-backup-restore.ready.open-probe.log": (4_499, "d0d4b51605bde18f6f393a2c2028958503c3cb6816debbf43f5a10178ff9ab75"),
    "post-backup-restore.ready.json": (5_885, "dd79ba194b76db00af89a29454245d6446993371c330b65e0f8f331c6488b498"),
    "post-backup-restore.ready.open-probe.log": (4_501, "90742105f8ddd5f308395dc514a2c1d06829abbb211f2c5c3747840bb440ab67"),
    "tracked-snapshot-restore.ready.json": (5_911, "72fc473678d86a43dfd3dbb4f0df692e0c507342b5e29042c6ab30ba68ec3126"),
    "tracked-snapshot-restore.ready.open-probe.log": (4_506, "07e34116eeff7edce5d34fe2542eff2c03a9fba64e6e49b31b4e21e3eb3e901c"),
    "tracked-pre-db.18608.gbf": (68_141_056, "5f18f79d6eff16d6819c7dcaa7e70eac21a342aee66de211e4243eb2a1d33692"),
    "runs/live-dry/ghidra.log": (5_264, "b2cb59163f39c5c420e7a1d8acee917ccb863bbfb8637654ccee7ff84c6c455d"),
    "runs/live-dry/cexplosion.ready.json": (2_148, "6a6770d988c9ea423ca85002d49886f83db4eea7daaef74002cf5e280824708c"),
    "runs/live-dry/cexplosion.tsv": (947, "2fc10bb0c91c639a6250f9577ba9c3845a1a0e41c0ff91d677352364a997a46a"),
    "runs/live-apply/ghidra.log": (5_395, "0d0f3785b41ae375e0a12fca8ba0497e26e02f5d89bf30a8ecf42f03abeb3f9e"),
    "runs/live-apply/cexplosion.ready.json": (2_150, "cbd18234a84fab3fc5da17f3523fe88f01c845dcdb078855bb4e317e0330aeb1"),
    "runs/live-apply/cexplosion.tsv": (1_008, "4fb5e6311e72cb03af12db3f82de13e3ca31050ef714caefcfffa93d202772e0"),
    "runs/live-readback/ghidra.log": (6_025, "e9bed8666979ad1ef98497fe3d2817d2343f8eff23991f20939022b9c4640280"),
    "runs/live-readback/cexplosion.ready.json": (2_159, "1616fea1eb6276b052e99260a3f79084a76831544ae350a549783b5115ee3175"),
    "runs/live-readback/cexplosion.tsv": (1_011, "832e1c290458b3e79586b65e54ca031d03c2e3c2d922955e7968e8f44d52dd8f"),
    "runs/live-readback/functions.tsv": POST_FUNCTIONS_STAMP,
    "runs/live-readback/program.tsv": POST_PROGRAM_STAMP,
}

BACKUP_MANIFEST_STAMPS = {
    "PRE": (7_589, "7f676cec36be3ba1330c9b056131844a882546dae0afd08f5e2f75ad83a3172c"),
    "POST": (7_589, "f12a4138e44c2f8be01d108ae5d61a3dc80a4cc1504d3c3e57055eb19e12652e"),
}

SCRATCH_FILE_STAMPS = {
    "inspection-v1/functions.tsv": PRE_FUNCTIONS_STAMP,
    "inspection-v1/program.tsv": PRE_PROGRAM_STAMP,
    "runs/replica-a-dry/target.tsv": LIVE_ARTIFACT_STAMPS["runs/live-dry/cexplosion.tsv"],
    "runs/replica-a-apply/target.tsv": LIVE_ARTIFACT_STAMPS["runs/live-apply/cexplosion.tsv"],
    "runs/replica-a-readback/target.tsv": LIVE_ARTIFACT_STAMPS["runs/live-readback/cexplosion.tsv"],
    "runs/replica-a-readback/functions.tsv": POST_FUNCTIONS_STAMP,
    "runs/replica-a-readback/program.tsv": POST_PROGRAM_STAMP,
}

EXPECTED_CHANGED_TARGET_FIELDS = sorted({
    "name", "nameLen", "nameSha256", "fqname", "fqnameLen", "fqnameSha256",
    "signature", "signatureLen", "signatureSha256", "commentLen", "commentSha256",
    "tagCount", "tagsSha256", "tags",
})
EXPECTED_PROGRAM_CHANGES = ["commentsSha256"]

DOCUMENT_PATHS = {
    "goal": "GOAL.md",
    "reIndex": "reverse-engineering/RE-INDEX.md",
    "delta": "reverse-engineering/delta.md",
    "ghidraFunctions": "reverse-engineering/ghidra-functions.md",
    "ghidraReadme": "reverse-engineering/ghidra/README.md",
    "worldPhysicsManager": (
        "reverse-engineering/binary-analysis/functions/WorldPhysicsManager.cpp.md"
    ),
    "liveReport": (
        "reverse-engineering/binary-analysis/"
        "cexplosion-factory-identity-live-promotion-2026-08-13.md"
    ),
}


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
            "cexplosion-factory-identity-promotion-2026-08-13.tsv"
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


def parse_utc(value: Any, label: str) -> datetime:
    require(isinstance(value, str) and value.endswith("Z"), f"{label} is not UTC")
    try:
        return datetime.fromisoformat(value[:-1] + "+00:00")
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
    measured = set()
    for path in config.live_lane.rglob("*"):
        relative = path.relative_to(config.live_lane)
        if path.is_file() and not any(
            part.endswith("restore-probe") for part in relative.parts
        ):
            measured.add(relative.as_posix())
    require(
        set(LIVE_ARTIFACT_STAMPS) == measured,
        "live evidence ledger differs: "
        f"missing={sorted(set(LIVE_ARTIFACT_STAMPS) - measured)} "
        f"extra={sorted(measured - set(LIVE_ARTIFACT_STAMPS))}",
    )
    for relative, expected in LIVE_ARTIFACT_STAMPS.items():
        actual[relative] = require_stamp(config.live_lane / relative, expected, relative)
    return actual


def validate_scratch(config: Config) -> dict[str, Any]:
    seal_stamp = require_stamp(
        config.scratch_seal, (21_588, SCRATCH_SEAL_SHA256),
        "final V7 scratch authority",
    )
    value = load_json(config.scratch_seal)
    require(
        value.get("schema") ==
        "bea.ghidra.cexplosion-factory-identity-scratch-authority.v1",
        "scratch authority schema differs",
    )
    parse_utc(value.get("generatedAtUtc"), "scratch generatedAtUtc")
    require(
        value.get("phase") == "SCRATCH_VALIDATED"
        and value.get("verdict") == "READY"
        and value.get("claim") ==
        "ONE_ROW_CEXPLOSION_FACTORY_IDENTITY_REPAIR_SCRATCH_VALIDATED",
        "scratch authority claim boundary differs",
    )
    author = value.get("author", {})
    require(
        author.get("bytes") == 34_237
        and author.get("sha256") == COMMITTED_FILES[
            "tools/ghidra_cexplosion_factory_identity_promotion_authority.py"
        ][2],
        "scratch authority tool binding differs",
    )
    result = value.get("result", {})
    require(
        result == {
            "adverseControls": 2,
            "bytesChanged": 0,
            "commentCountChanged": 0,
            "definedDataChanged": 0,
            "exactPreAdverseReadbacks": 2,
            "functionRows": FUNCTION_COUNT,
            "functionRowsChanged": 1,
            "instructionLayoutChanged": 0,
            "loadedPostReadbacks": 2,
            "nonFunctionSymbolsChanged": 0,
            "nonTargetFunctionRowsUnchanged": FUNCTION_COUNT - 1,
            "positiveReplicas": 2,
            "preTransactionPathControls": 2,
            "referencesChanged": 0,
            "target": TARGET,
            "undefinedDataCountChanged": 0,
        },
        "scratch result boundary differs",
    )
    authorization = value.get("authorization", {})
    require(
        authorization.get("scratchRepairValidated") is True
        and authorization.get("externalOutputAndReadyPreflightValidated") is True
        and authorization.get("oneMutationProcessMaximum") is True
        and authorization.get("freshLiveBackupRequired") is True
        and authorization.get("separateLiveReadbackRequired") is True
        and authorization.get("postBackupRestoreAndTrackedRefreshRequired") is True
        and authorization.get("liveApplyAuthorizedByThisReceipt") is False
        and authorization.get("runtimeSemanticsAuthorized") is False
        and authorization.get("rebuildReadyAuthorized") is False,
        "scratch authorization boundary differs",
    )
    files: dict[str, Any] = {}
    for relative, expected in SCRATCH_FILE_STAMPS.items():
        files[relative] = require_stamp(
            config.scratch_formal / relative, expected, "scratch " + relative
        )
    for phase in ("dry", "apply", "readback"):
        live = config.live_lane / f"runs/live-{phase}/cexplosion.tsv"
        scratch = config.scratch_formal / f"runs/replica-a-{phase}/target.tsv"
        require(
            live.read_bytes() == scratch.read_bytes(),
            f"live {phase} output differs from final scratch authority",
        )
    for name in ("functions.tsv", "program.tsv"):
        live = config.live_lane / "runs/live-readback" / name
        scratch = config.scratch_formal / "runs/replica-a-readback" / name
        require(
            live.read_bytes() == scratch.read_bytes(),
            f"live {name} differs from final scratch authority",
        )
    return {
        "seal": seal_stamp,
        "criticalFiles": files,
        "livePhaseOutputsByteIdentical": True,
        "livePostInventoriesByteIdentical": True,
    }


def load_manifest(config: Config) -> dict[str, dict[str, str]]:
    rows = read_tsv(config.manifest)
    require(len(rows) == TARGET_COUNT, "target manifest row count differs")
    result = {row["address"].lower(): row for row in rows}
    require(len(result) == TARGET_COUNT, "target manifest addresses are not unique")
    row = rows[0]
    require(
        row["address"].lower() == TARGET
        and row["preName"] == "CWorldPhysicsManager__CreatePickup"
        and row["postName"] == "CWorldPhysicsManager__CreateExplosion"
        and row["preParameterSource"] == row["postParameterSource"] == "USER_DEFINED"
        and row["bodyBytesSha256"] ==
        "24f43aa5cdf6fff0d9d8ec700ec2de8fb221acc3fc49af3f3738e5b596160e5b",
        "target manifest identity differs",
    )
    return result


def validate_target_row(
    row: Mapping[str, str], manifest: Mapping[str, str], state: str
) -> None:
    """Bind each phase row to every authorized semantic and ABI field."""
    require(state in {"PRE", "POST"}, f"unknown target-row state: {state}")
    prefix = "pre" if state == "PRE" else "post"
    expected = {
        "address": TARGET,
        "state": state,
        "name": manifest[prefix + "Name"],
        "nameSource": "USER_DEFINED",
        "signatureSource": "USER_DEFINED",
        "signature": manifest[prefix + "Signature"],
        "parameterName": manifest[prefix + "ParameterName"],
        "parameterType": manifest["parameterType"],
        "parameterStorage": manifest["parameterStorage"],
        "parameterSource": manifest[prefix + "ParameterSource"],
        "callingConvention": manifest["callingConvention"],
        "returnType": manifest["returnType"],
        "returnStorage": manifest["returnStorage"],
        "bodyRanges": manifest["bodyRanges"],
        "bodyBytes": manifest["bodyBytes"],
        "bodyRangeSha256": manifest["bodyRangeSha256"],
        "bodyBytesSha256": manifest["bodyBytesSha256"],
        "instructionCount": manifest["instructionCount"],
        "commentBytes": manifest[prefix + "CommentBytes"],
        "commentSha256": manifest[prefix + "CommentSha256"],
        "tags": manifest[prefix + "Tags"],
    }
    for key, value in expected.items():
        require(row.get(key) == value, f"{state} target-row {key} differs")
    require(
        row.get("tagsSha256") == sha256_bytes(row["tags"].encode("utf-8")),
        f"{state} target-row tagsSha256 differs",
    )


def validate_tool_receipt(
    config: Config, phase: str, mode: str, state: str
) -> dict[str, Any]:
    root = config.live_lane / "runs" / ("live-" + phase)
    path = root / "cexplosion.ready.json"
    value = load_json(path)
    require(
        value.get("schema") == TOOL_SCHEMA
        and value.get("mode") == mode
        and value.get("state") == state,
        f"{phase} receipt identity differs",
    )
    parse_utc(value.get("completedAtUtc"), f"{phase} completedAtUtc")
    require(
        value.get("program") == {
            "name": "BEA.exe",
            "md5": PROGRAM_MD5,
            "sha256": PROGRAM_SHA256,
            "functions": FUNCTION_COUNT,
            "instructions": INSTRUCTION_COUNT,
            "memorySha256": MEMORY_SHA256,
        },
        f"{phase} program identity differs",
    )
    require(
        value.get("target") == {
            "address": TARGET,
            "bodyBytes": 152,
            "bodySha256":
            "24f43aa5cdf6fff0d9d8ec700ec2de8fb221acc3fc49af3f3738e5b596160e5b",
            "directCallers": 24,
            "externalInteriorReferences": 0,
            "parameterSource": "USER_DEFINED",
        },
        f"{phase} target identity differs",
    )
    mutation = {
        "namesChanged": 1 if mode == "apply" else 0,
        "parameterNamesChanged": 1 if mode == "apply" else 0,
        "parameterSourcesChanged": 0,
        "commentsChanged": 1 if mode == "apply" else 0,
        "tagSetsChanged": 1 if mode == "apply" else 0,
        "boundariesChanged": 0,
        "bytesChanged": 0,
        "instructionsChanged": 0,
        "dataUnitsChanged": 0,
        "referencesChanged": 0,
    }
    require(value.get("mutation") == mutation, f"{phase} mutation boundary differs")
    inputs = {
        "tool": "tools/GhidraApplyCExplosionFactoryIdentity.java",
        "owner": (
            "reverse-engineering/binary-analysis/"
            "cexplosion-factory-identity-promotion-2026-08-13.md"
        ),
        "manifest": (
            "reverse-engineering/binary-analysis/"
            "cexplosion-factory-identity-promotion-2026-08-13.tsv"
        ),
        "reproof": (
            "local-lab/ghidra-cexplosion-identity-scratch-20260813-v7/"
            "reproof-v7/reproof.ready.json"
        ),
    }
    for key, relative in inputs.items():
        measured = value.get(key, {})
        actual = stamp(config.shared_repo / relative)
        require(measured.get("path") == relative, f"{phase} {key} path differs")
        require(
            (measured.get("bytes"), measured.get("sha256")) ==
            (actual["bytes"], actual["sha256"]),
            f"{phase} {key} stamp differs",
        )
    relative_output = f"{config.live_lane.relative_to(config.shared_repo).as_posix()}/runs/live-{phase}/cexplosion.tsv"
    output = stamp(root / "cexplosion.tsv")
    measured_output = value.get("output", {})
    require(
        measured_output.get("path") == relative_output
        and (measured_output.get("bytes"), measured_output.get("sha256")) ==
        (output["bytes"], output["sha256"]),
        f"{phase} output stamp/path differs",
    )
    require(
        value.get("commitRequested") is (mode == "apply")
        and value.get("nestedEndReturnedCommitted") is False
        and value.get("loadedStateVerified") is (mode == "readback")
        and value.get("runtimeSemanticsAuthorized") is False
        and value.get("rebuildReadyAuthorized") is False
        and value.get("authorityBoundary") ==
        "scratch_only_until_sealed_and_fresh_live_pre_backup",
        f"{phase} transaction/authority flags differ",
    )
    rows = read_tsv(root / "cexplosion.tsv")
    require(
        len(rows) == 1
        and rows[0]["address"].lower() == TARGET
        and rows[0]["mode"] == mode
        and rows[0]["state"] == state,
        f"{phase} target row differs",
    )
    return {"receipt": stamp(path), "table": output, "row": rows[0]}


def validate_log(
    config: Config, phase: str, marker: str, *, writable: bool,
    inventory: bool = False,
) -> dict[str, Any]:
    path = config.live_lane / f"runs/live-{phase}/ghidra.log"
    text = path.read_text(encoding="utf-8", errors="strict")
    require(
        text.count(marker) == 1 and "REPORT SCRIPT ERROR" not in text,
        f"{phase} success/error marker differs",
    )
    require(
        f"Opening existing project: {config.live_project / 'BEA'}" in text,
        f"{phase} does not name the live maintainer project",
    )
    processing = (
        "REPORT: Processing project file: /BEA.exe" if writable
        else "REPORT: Processing read-only project file: /BEA.exe"
    )
    require(processing in text, f"{phase} processing mode differs")
    require(
        str(config.shared_repo / "tools/GhidraApplyCExplosionFactoryIdentity.java")
        in text,
        f"{phase} mutator path differs",
    )
    require(
        ("Save succeeded for processed file: /BEA.exe" in text) is writable,
        f"{phase} save marker differs",
    )
    if inventory:
        require(
            str(config.shared_repo / "tools/ExportFullFunctionInventory.java") in text
            and "INVENTORY_OK functions=8170 instructions=549872" in text,
            f"{phase} full inventory marker differs",
        )
    return stamp(path)


def validate_one_mutation_log(runs_root: Path) -> dict[str, Any]:
    logs = sorted(runs_root.glob("live-*/ghidra.log"))
    expected = sorted(
        runs_root / f"live-{phase}/ghidra.log"
        for phase in ("apply", "dry", "readback")
    )
    require(logs == expected, f"live Ghidra log set differs: {logs}")
    mutating = []
    for path in logs:
        text = path.read_text(encoding="utf-8", errors="strict")
        if (
            "CEXPLOSION_FACTORY_IDENTITY_APPLY_COMPLETE" in text
            or "REPORT: Processing project file: /BEA.exe" in text
            or "Save succeeded for processed file: /BEA.exe" in text
        ):
            mutating.append(path)
    require(
        mutating == [runs_root / "live-apply/ghidra.log"],
        "mutation-log census differs from exactly one live apply",
    )
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
        require(before.keys() == after.keys(),
                f"target inventory columns changed at {address}")
        changed = {key for key in before if before[key] != after[key]}
        require(sorted(changed) == EXPECTED_CHANGED_TARGET_FIELDS,
                f"target delta differs at {address}: {sorted(changed)}")
        changed_fields.update(changed)
        require(before["name"] == target["preName"] and
                after["name"] == after["fqname"] == target["postName"] and
                after["nameSource"] == "USER_DEFINED",
                f"target name delta differs at {address}")
        require(before["signature"] == target["preSignature"] and
                after["signature"] == target["postSignature"] and
                before["sigSource"] == after["sigSource"] == "USER_DEFINED",
                f"target signature/source delta differs at {address}")
        require(before["commentLen"] == target["preCommentBytes"] and
                before["commentSha256"] == target["preCommentSha256"] and
                after["commentLen"] == target["postCommentBytes"] and
                after["commentSha256"] == target["postCommentSha256"] and
                before["tags"] == target["preTags"] and
                after["tags"] == target["postTags"],
                f"target comment/tag delta differs at {address}")
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
    require(before["comments"] == after["comments"] and
            before["symbolsUserDefined"] == after["symbolsUserDefined"] and
            before["symbolsDefaultOther"] == after["symbolsDefaultOther"],
            "comment/symbol census moved")
    require(after["functions"] == str(FUNCTION_COUNT) and
            after["instructions"] == str(INSTRUCTION_COUNT) and
            after["executableSHA256"] == PROGRAM_SHA256,
            "program identity/census differs")
    return {"changedMetrics": changed, "commentCountUnchanged": True,
            "symbolCountsUnchanged": True}


def crosscheck_target(row: Mapping[str, str],
                      functions: Mapping[str, Mapping[str, str]]) -> None:
    function = functions[row["address"].lower()]
    for output_key, inventory_key in (
        ("name", "name"), ("nameSource", "nameSource"),
        ("signature", "signature"), ("commentBytes", "commentLen"),
        ("commentSha256", "commentSha256"), ("tags", "tags"),
        ("bodyBytes", "bodyBytes"), ("bodyRangeSha256", "bodyDigest"),
        ("instructionCount", "instrCount"),
    ):
        require(row[output_key] == function[inventory_key],
                f"target/full-inventory mismatch: {output_key}")


def validate_runs_and_collateral(config: Config) -> dict[str, Any]:
    dry = validate_tool_receipt(config, "dry", "dry", "PRE")
    apply = validate_tool_receipt(config, "apply", "apply", "POST")
    readback = validate_tool_receipt(config, "readback", "readback", "POST")
    logs = {
        "dry": validate_log(config, "dry", "CEXPLOSION_FACTORY_IDENTITY_DRY_COMPLETE",
                            writable=False),
        "apply": validate_log(config, "apply", "CEXPLOSION_FACTORY_IDENTITY_APPLY_COMPLETE",
                              writable=True),
        "readback": validate_log(
            config, "readback", "CEXPLOSION_FACTORY_IDENTITY_READBACK_COMPLETE",
            writable=False, inventory=True),
    }
    mutation = validate_one_mutation_log(config.live_lane / "runs")
    targets = load_manifest(config)
    target = targets[TARGET]
    validate_target_row(dry["row"], target, "PRE")
    validate_target_row(apply["row"], target, "POST")
    validate_target_row(readback["row"], target, "POST")
    pre_path = config.scratch_formal / "inspection-v1/functions.tsv"
    post_path = config.live_lane / "runs/live-readback/functions.tsv"
    pre, post = inventory_rows(pre_path), inventory_rows(post_path)
    collateral = compare_inventory_records(pre, post, targets)
    program = compare_programs(
        config.scratch_formal / "inspection-v1/program.tsv",
        config.live_lane / "runs/live-readback/program.tsv",
    )
    crosscheck_target(dry["row"], pre)
    crosscheck_target(apply["row"], post)
    crosscheck_target(readback["row"], post)
    return {
        "dry": {key: value for key, value in dry.items() if key != "row"},
        "apply": {key: value for key, value in apply.items() if key != "row"},
        "readback": {key: value for key, value in readback.items() if key != "row"},
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
    verified_at = value.get("verifiedAtUtc")
    parse_utc(verified_at, f"{label} verifiedAtUtc")
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
    return {
        "receipt": stamp(path), "probeLog": log, "retainedProbeMatches": True,
        "verifiedAtUtc": verified_at,
    }


def validate_ceremony_chronology(
    times: Mapping[str, datetime],
) -> dict[str, Any]:
    """Prove that recovery and readback gates surrounded the sole live write."""
    relations = (
        ("livePreInspect", "preBackupCreated"),
        ("trackedPreInspect", "preBackupCreated"),
        ("preBackupCreated", "preRestoreVerified"),
        ("preRestoreVerified", "dryCompleted"),
        ("dryCompleted", "afterDryInspect"),
        ("afterDryInspect", "applyCompleted"),
        ("applyCompleted", "readbackCompleted"),
        ("readbackCompleted", "livePostInspect"),
        ("livePostInspect", "postBackupCreated"),
        ("postBackupCreated", "postRestoreVerified"),
        ("postRestoreVerified", "trackedPostInspect"),
        ("trackedPostInspect", "trackedRestoreVerified"),
    )
    require(
        set(times) == {name for relation in relations for name in relation},
        "ceremony chronology timestamp set differs",
    )
    for before, after in relations:
        require(
            times[before] < times[after],
            f"ceremony chronology differs: {before} !< {after}",
        )
    return {
        "relations": [f"{before} < {after}" for before, after in relations],
        "freshPreBackupRestoredBeforeDry": True,
        "dryProvedReadOnlyBeforeApply": True,
        "separateReadbackAfterApply": True,
        "postBackupRestoredAfterReadback": True,
        "trackedRefreshRestoredAfterInspection": True,
    }


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
        "liveAfterDry": validate_inspect(
            config.live_lane / "live-after-dry-inspect.json",
            config.live_project, pre, "live after-dry inspect"),
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
    timestamp_text = {
        "livePreInspect": load_json(
            config.live_lane / "live-pre-inspect.json"
        ).get("createdAtUtc"),
        "trackedPreInspect": load_json(
            config.live_lane / "tracked-pre-inspect.json"
        ).get("createdAtUtc"),
        "preBackupCreated": load_json(
            config.pre_backup / "backup_manifest.json"
        ).get("createdAtUtc"),
        "preRestoreVerified": restores["preBackup"]["verifiedAtUtc"],
        "dryCompleted": load_json(
            config.live_lane / "runs/live-dry/cexplosion.ready.json"
        ).get("completedAtUtc"),
        "afterDryInspect": load_json(
            config.live_lane / "live-after-dry-inspect.json"
        ).get("createdAtUtc"),
        "applyCompleted": load_json(
            config.live_lane / "runs/live-apply/cexplosion.ready.json"
        ).get("completedAtUtc"),
        "readbackCompleted": load_json(
            config.live_lane / "runs/live-readback/cexplosion.ready.json"
        ).get("completedAtUtc"),
        "livePostInspect": load_json(
            config.live_lane / "live-post-inspect.json"
        ).get("createdAtUtc"),
        "postBackupCreated": load_json(
            config.post_backup / "backup_manifest.json"
        ).get("createdAtUtc"),
        "postRestoreVerified": restores["postBackup"]["verifiedAtUtc"],
        "trackedPostInspect": load_json(
            config.live_lane / "tracked-post-inspect.json"
        ).get("createdAtUtc"),
        "trackedRestoreVerified": restores["trackedSnapshot"]["verifiedAtUtc"],
    }
    chronology = validate_ceremony_chronology({
        key: parse_utc(value, key) for key, value in timestamp_text.items()
    })
    chronology["timestampsUtc"] = timestamp_text
    return {
        "pre": {"project": project_summary(pre), "backupManifest": pre_manifest,
                "inspections": pre_inspects, "restore": restores["preBackup"]},
        "post": {"project": project_summary(post), "backupManifest": post_manifest,
                 "inspections": post_inspects, "postRestore": restores["postBackup"],
                 "trackedRestore": restores["trackedSnapshot"]},
        "equality": {"liveEqualsPostBackup": True, "trackedEqualsLive": True,
                     "trackedEqualsPostBackup": True},
        "chronology": chronology,
    }


def validate_projection(config: Config) -> dict[str, Any]:
    shared = require_stamp(config.projection, (502_854, PROJECTION_SHA256),
                           "shared current projection")
    retained = require_stamp(
        config.live_lane / "ghidra-function-name-table-2026-08-13.tsv",
        (502_854, PROJECTION_SHA256), "retained current projection",
    )
    require(config.projection.read_bytes() ==
            (config.live_lane / "ghidra-function-name-table-2026-08-13.tsv").read_bytes(),
            "shared and retained projections differ")
    text = config.projection.read_text(encoding="utf-8")
    require("# Source bytes: 7086736" in text and
            f"# Source SHA-256: {POST_FUNCTIONS_STAMP[1]}" in text and
            "# Rows    : 8170 internal functions;" in text and
            ("0x0050ff10\tCWorldPhysicsManager__CreateExplosion\t"
             "0x0050ff10\t0x0050ffa7") in text and
            "0x0050ff10\tCWorldPhysicsManager__CreatePickup\t" not in text,
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


def require_text_contract(
    path: Path, required: Sequence[str], forbidden: Sequence[str] = ()
) -> None:
    text = path.read_text(encoding="utf-8")
    missing = [fragment for fragment in required if fragment not in text]
    present = [fragment for fragment in forbidden if fragment in text]
    require(not missing, f"documentation contract is missing from {path}: {missing}")
    require(not present, f"stale documentation contract remains in {path}: {present}")


def validate_documentation(config: Config) -> dict[str, Any]:
    """Require current semantic facts without hash-pinning mutable synthesis."""
    paths = {key: config.shared_repo / relative
             for key, relative in DOCUMENT_PATHS.items()}
    require_text_contract(
        paths["goal"],
        ["CWorldPhysicsManager__CreateExplosion", "It is now closed"],
        ["Repair `0x0050FF10` separately"],
    )
    require_text_contract(
        paths["reIndex"],
        ["factory identity/signature at `0x0050FF10`", "backed-up live-Ghidra ceremony"],
    )
    require_text_contract(
        paths["delta"],
        ["latest authorized live operation separately repaired `0x0050FF10`",
         "`8eb66406…3cf6`"],
    )
    require_text_contract(
        paths["ghidraFunctions"],
        ["CWorldPhysicsManager__CreateExplosion",
         "local-lab/ghidra-cexplosion-live-promotion-20260813-v1/",
         "`8eb66406…3cf6`", "`51517075…86ee`"],
    )
    require_text_contract(
        paths["ghidraReadme"],
        ["186,747,781 bytes", POST_PROJECT_SHA256, POST_DB_SHA256,
         "cexplosion-factory-identity-live-promotion-2026-08-13.md"],
        ["Project payload: 19 files, 186,665,861 bytes"],
    )
    require_text_contract(
        paths["worldPhysicsManager"],
        ["CWorldPhysicsManager__CreateExplosion", "explosion_definition_index",
         "matches the separately gated live-Ghidra explosion identity"],
        ["ghidra-name-drift-accepted: 0x0050ff10"],
    )
    require_text_contract(
        paths["liveReport"],
        ["# CExplosion factory identity live promotion", POST_PROJECT_SHA256,
         POST_DB_SHA256, PROJECTION_SHA256, SCRATCH_SEAL_SHA256],
    )

    state_path = config.shared_repo / "developer_state.json"
    state = load_json(state_path)
    audit = state.get("current_post_claude_reaudit_20260813", {})
    integrity = str(audit.get("ghidraIntegrity", ""))
    remaining = str(audit.get("remainingFrontier", ""))
    require(
        all(value in integrity for value in (
            "CWorldPhysicsManager__CreateExplosion", POST_PROJECT_SHA256,
            POST_FUNCTIONS_STAMP[1], PROJECTION_SHA256,
        )),
        "developer_state current Ghidra integrity is not the CExplosion POST",
    )
    require(
        "one-row CreateExplosion corruption repair are published" in remaining
        and "one-row CreateExplosion corruption repair as distinct future" not in remaining,
        "developer_state current frontier still treats the repair as future",
    )
    latest = state.get("current_re_authority", {}).get("latestLiveGhidraState", {})
    require(
        latest.get("postFunctionsBytes") == POST_FUNCTIONS_STAMP[0]
        and latest.get("postFunctionsSha256") == POST_FUNCTIONS_STAMP[1]
        and latest.get("postProgramBytes") == POST_PROGRAM_STAMP[0]
        and latest.get("postProgramSha256") == POST_PROGRAM_STAMP[1]
        and latest.get("trackedSnapshotFiles") == PROJECT_FILES
        and latest.get("trackedSnapshotBytes") == POST_PROJECT_BYTES
        and latest.get("trackedSnapshotInventorySha256") == POST_PROJECT_SHA256
        and PROJECTION_SHA256 in str(latest.get("currentNameProjection", ""))
        and latest.get("targetFunctionRowsChanged") == TARGET_COUNT
        and latest.get("nonTargetFunctionRowsChanged") == 0,
        "developer_state latestLiveGhidraState differs from the sealed POST",
    )
    recursive = state.get("_RECURSIVE_RE_CAMPAIGN_2026_08_02", {})
    require(
        "pristine_and_live_db" not in recursive
        and "pristine_and_live_db_historical_20260809_superseded" in recursive,
        "developer_state retains a stale present-tense live-Ghidra checkpoint",
    )
    return {
        "semanticContracts": {key: relative for key, relative in DOCUMENT_PATHS.items()},
        "developerState": "developer_state.json",
        "mutableSynthesisHashesPinned": False,
        "postFactsRequired": True,
    }


def build(config: Config, generated_at: str) -> dict[str, Any]:
    parse_utc(generated_at, "generatedAtUtc")
    artifact_ledger = validate_artifact_ledger(config)
    committed = validate_committed_inputs(config)
    scratch = validate_scratch(config)
    runs = validate_runs_and_collateral(config)
    projects = validate_projects_and_recovery(config)
    projection = validate_projection(config)
    documentation = validate_documentation(config)
    return {
        "schema": SCHEMA,
        "generatedAtUtc": generated_at,
        "verdict": "LIVE_PROMOTION_SAVED_READ_BACK_BACKED_UP_AND_TRACKED",
        "claim": "ONE_CEXPLOSION_FACTORY_IDENTITY_ROW_PROMOTED",
        "authorityTool": authority_tool_stamp(config),
        "ceremonyBase": committed,
        "artifactLedger": artifact_ledger,
        "scratchAuthority": scratch,
        "liveRuns": runs,
        "projectsAndRecovery": projects,
        "currentProjection": projection,
        "currentDocumentation": documentation,
        "result": {
            "target": TARGET, "targets": TARGET_COUNT,
            "liveMutationProcesses": 1, "internalFunctions": FUNCTION_COUNT,
            "externalFunctions": OPEN_FUNCTION_COUNT - FUNCTION_COUNT,
            "instructions": INSTRUCTION_COUNT,
            "nonTargetRowsByteIdentical": FUNCTION_COUNT - TARGET_COUNT,
            "boundariesChanged": 0, "abiChanged": 0, "bytesChanged": 0,
            "instructionsChanged": 0, "dataUnitsChanged": 0,
            "referencesChanged": 0, "commentCountChanged": 0,
            "postProjectFiles": PROJECT_FILES, "postProjectBytes": POST_PROJECT_BYTES,
            "postProjectInventorySha256": POST_PROJECT_SHA256,
            "postDb18610Sha256": POST_DB_SHA256,
            "projectionSha256": PROJECTION_SHA256,
        },
        "limitations": [
            "The promoted identity is a bounded C1 static implementation identity; exact original source spelling remains open.",
            "The descriptive parameter name is not recovered source spelling.",
            "This promotion adds no runtime-causality, reconstruction, or REBUILD_READY claim.",
            "The MissionScript-registry cohorts and every non-target function are outside this one-row repair.",
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
        print(f"CEXPLOSION_FACTORY_IDENTITY_LIVE_AUTHORITY_SEALED "
              f"sha256={sha256_file(config.output)}")
    else:
        verify_saved(config)
        print(f"CEXPLOSION_FACTORY_IDENTITY_LIVE_AUTHORITY_VERIFIED "
              f"sha256={sha256_file(config.output)}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuthorityError as exc:
        print(f"AUTHORITY_REJECTED: {exc}")
        raise SystemExit(1)
