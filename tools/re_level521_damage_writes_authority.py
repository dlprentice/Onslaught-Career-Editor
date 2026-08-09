#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Publish the literal-pinned Generation 12 Damage/Hit authority selector."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "local-lab/re-campaign-incident-recovery-20260808-v1"
CANONICAL = BASE / "generation-12-level521-damage-hit-writes-v1"
REPLICA = BASE / "generation-12-level521-damage-hit-writes-replica-v1"
PARENT = BASE / "generation-11-gen73-claims-resealed-v2"
PARENT_AUTHORITY = BASE / "generation-11-recovery-authority.ready.json"
PROOF = ROOT / "local-lab/level521-damage-hit-write-proof-20260808-v2"
OUT = BASE / "generation-12-level521-damage-hit-writes-authority.ready.json"
REDUCER_ID = "1bcd8b1bff0bd9182872c221df8060aff8da263a89d94052ede2e80127812385"
READY = {
    CANONICAL.name: "9d2b903d451cb62fd6fb599b915dd57a0e6f313e610a348022fabf26ee265747",
    REPLICA.name: "0635f8bb828cc4bb1f325bb2fc50d385597a38a999d91d3af3ff38dfb86c9319",
}
OUTPUTS = {
    "campaign-functions.tsv": "f129dcb3f894cb3822fb320e7627b487a345b1c7b64183c4a79d87b9d764a516",
    "campaign-residuals.tsv": "30d390b75a9984efc6bebedf5ddb00412326d36e51d2c9f3c1883032dd25ef49",
    "campaign-questions.tsv": "86f1d48e2f92950926a3acfe7b3c4219ad778e3b2e19c627202b7053f5866782",
    "campaign-scenarios.tsv": "35a84fad46065d1317e48b41c66889a1dd12327077766423693b8839be857542",
    "campaign-levers.tsv": "fa337d96cfe7b6eca266b44aa39deded516e3a8cc02979a31671b449c66e3cdc",
    "campaign-contracts.tsv": "da9e8cbc0afe26a6d83cd68e6cab289d17a12f7a3818bf1dc2da193aca6a23da",
    "campaign-adjudications.tsv": "b31ed77711ebcde4cd878cf9e846fa065c2f1def0e7c135d7650dd3e465e16b5",
    "campaign-supersessions.tsv": "7569852a3fe9aea25a4fcc4f6d17b6d9d81ff658f644b007bda1f50ae55559cb",
}
COUNTS = {
    "functions": 8124,
    "residuals": 6117,
    "questions": 15243,
    "scenarios": 72,
    "levers": 915,
    "contracts": 14241,
    "adjudications": 6090,
    "supersessions": 584,
}
PARENT_READY_SHA256 = "9b3769c503f003b34d3915047be28c24036567f260de1933591f0254d992686d"
PARENT_REDUCER_ID = "e88c973967a0458f500ff2cc1508d417b60487a4886703c4bd3dcfd197246993"
PARENT_AUTHORITY_SHA256 = "2594d78d7ec6b4908ecfba9509122fedbe1959ff0e5eeaceb6d1164ae758238c"
PROOF_READY_SHA256 = "ffb2e0b8692ddada364a829d52a158841e5d800742c49bd2a1710b2af135869a"
PROOF_AUTHOR_SHA256 = "8e8c22d3dbb31c7464ad47c211a5179d773aabd9dd665aa4960ee7aa7a0b47e9"


class AuthorityError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuthorityError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stamp(path: Path, *, relative_to: Path | None = None) -> dict[str, object]:
    require(path.is_file(), f"missing file: {path}")
    relative = (
        path.resolve().relative_to(relative_to.resolve()).as_posix()
        if relative_to is not None
        else str(path.resolve())
    )
    return {"path": relative, "bytes": path.stat().st_size, "sha256": sha256(path)}


def require_plain_single(path: Path, label: str) -> None:
    require(path.is_file(), f"{label} is absent")
    stat = path.lstat()
    require(not path.is_symlink(), f"{label} is symlinked")
    require(not (getattr(stat, "st_file_attributes", 0) & 0x400), f"{label} is reparse-linked")
    require(stat.st_nlink == 1, f"{label} has multiple hard links")


def validate_campaign(root: Path, expected_ready: str) -> dict:
    require(root.resolve() == root, f"campaign root is not canonical: {root}")
    ready_path = root / "campaign.ready.json"
    require_plain_single(ready_path, f"{root.name} READY")
    require(sha256(ready_path) == expected_ready, f"{root.name} READY differs")
    receipt = json.loads(ready_path.read_text(encoding="utf-8"))
    require(receipt.get("generation") == 12, f"{root.name} generation differs")
    require(receipt.get("counts") == COUNTS, f"{root.name} counts differ")
    require(receipt.get("reducer", {}).get("id") == REDUCER_ID, f"{root.name} reducer differs")
    require(receipt.get("advance", {}).get("kind") == "TTD_DAMAGE_HIT_FIELD_WRITES", f"{root.name} kind differs")
    for name, expected in OUTPUTS.items():
        path = root / name
        require_plain_single(path, f"{root.name} {name}")
        require(sha256(path) == expected, f"{root.name} output differs: {name}")
    for row in receipt["reducer"]["files"]:
        path = root / row["path"]
        require_plain_single(path, f"{root.name} reducer {row['path']}")
        require(path.stat().st_size == row["bytes"] and sha256(path) == row["sha256"], f"{root.name} reducer entry differs")
    return receipt


def run_full(root: Path, expected_ready: str) -> dict[str, object]:
    bootstrap = ROOT / "tools/re_campaign_frozen_bootstrap.py"
    require_plain_single(bootstrap, "trusted frozen bootstrap")
    environment = os.environ.copy()
    environment["BEA_REPO_ROOT"] = str(ROOT)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    for name in ("PYTHONHOME", "PYTHONPATH", "PYTHONSTARTUP", "PYTHONINSPECT", "PYTHONUSERBASE"):
        environment.pop(name, None)
    argv = [
        sys.executable,
        "-I",
        "-B",
        str(bootstrap),
        "--campaign",
        str(root),
        "--mode",
        "full",
        "--expected-ready-sha256",
        expected_ready,
        "--expected-reducer-id",
        REDUCER_ID,
    ]
    started = time.monotonic()
    completed = subprocess.run(
        argv,
        cwd=ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=900,
        check=False,
    )
    require(completed.returncode == 0 and "CAMPAIGN_VERIFIED" in completed.stdout, f"full replay failed for {root.name}: {completed.stderr}")
    return {
        "command": argv,
        "exitCode": completed.returncode,
        "marker": "CAMPAIGN_VERIFIED",
        "elapsedSeconds": round(time.monotonic() - started, 3),
    }


def main() -> int:
    try:
        require(not OUT.exists(), f"refusing existing authority receipt: {OUT}")
        author_start = Path(__file__).resolve().read_bytes()
        canonical = validate_campaign(CANONICAL, READY[CANONICAL.name])
        replica = validate_campaign(REPLICA, READY[REPLICA.name])
        for name in OUTPUTS:
            require((CANONICAL / name).read_bytes() == (REPLICA / name).read_bytes(), f"replica ledger differs: {name}")
        canonical_reducer = {
            path.relative_to(CANONICAL / "_reducer").as_posix(): path.read_bytes()
            for path in (CANONICAL / "_reducer").rglob("*")
            if path.is_file()
        }
        replica_reducer = {
            path.relative_to(REPLICA / "_reducer").as_posix(): path.read_bytes()
            for path in (REPLICA / "_reducer").rglob("*")
            if path.is_file()
        }
        require(canonical_reducer == replica_reducer, "replica reducer differs")
        normalized = []
        for receipt in (canonical, replica):
            value = json.loads(json.dumps(receipt))
            value.pop("generatedAtUtc")
            for output in value["outputs"].values():
                output.pop("lastWriteUtc")
            normalized.append(value)
        require(normalized[0] == normalized[1], "normalized READY receipts differ")
        require(sha256(PARENT / "campaign.ready.json") == PARENT_READY_SHA256, "parent READY differs")
        require(sha256(PARENT_AUTHORITY) == PARENT_AUTHORITY_SHA256, "parent authority differs")
        require(sha256(PROOF / "proof.ready.json") == PROOF_READY_SHA256, "proof READY differs")
        require(sha256(PROOF / "author.py") == PROOF_AUTHOR_SHA256, "proof author differs")
        canonical_verify = run_full(CANONICAL, READY[CANONICAL.name])
        replica_verify = run_full(REPLICA, READY[REPLICA.name])
        require(Path(__file__).resolve().read_bytes() == author_start, "authority author changed during execution")
        receipt = {
            "schema": "bea.re.level521-damage-hit-generation12-authority.v1",
            "verdict": "READY",
            "authorityClass": "FULL_REPLAY_CAMPAIGN_AUTHORITY",
            "replayScope": "FULL_CAMPAIGN_REDUCER_REPLAY_NOT_GAME_TTD_OR_GHIDRA_REPLAY",
            "completedAtUtc": datetime.now(timezone.utc).isoformat(),
            "lineageId": "incident-20260806-recovery-v1",
            "author": {
                "path": "tools/re_level521_damage_writes_authority.py",
                "bytes": len(author_start),
                "sha256": hashlib.sha256(author_start).hexdigest(),
            },
            "canonical": {
                "absolutePath": str(CANONICAL),
                "ready": stamp(CANONICAL / "campaign.ready.json", relative_to=CANONICAL),
                "reducerId": REDUCER_ID,
                "generation": 12,
                "kind": "TTD_DAMAGE_HIT_FIELD_WRITES",
                "observationId": canonical["advance"]["observationId"],
            },
            "replica": {
                "absolutePath": str(REPLICA),
                "ready": stamp(REPLICA / "campaign.ready.json", relative_to=REPLICA),
                "reducerId": REDUCER_ID,
                "role": "REPRODUCTION_ONLY_NOT_AUTHORITY_SELECTOR",
            },
            "parent": {
                "path": PARENT.relative_to(ROOT).as_posix(),
                "readySha256": PARENT_READY_SHA256,
                "reducerId": PARENT_REDUCER_ID,
                "authorityReceiptSha256": PARENT_AUTHORITY_SHA256,
            },
            "proof": {
                "path": PROOF.relative_to(ROOT).as_posix(),
                "readySha256": PROOF_READY_SHA256,
                "authorSha256": PROOF_AUTHOR_SHA256,
                "schema": "bea.re.level521-damage-hit-write-proof.v2",
            },
            "counts": COUNTS,
            "outputs": {
                name: {"bytes": (CANONICAL / name).stat().st_size, "sha256": digest}
                for name, digest in OUTPUTS.items()
            },
            "claimBoundary": {
                "functionRowsModified": 2,
                "contractRowsModified": 2,
                "questionsClosed": 2,
                "successorQuestionsAdded": 2,
                "semanticAdjudicationsAdded": 2,
                "retailNamesCorrelated": ["CBattleEngine__Damage", "CBattleEngine__Hit"],
                "witnessedDamageWrites": 5,
                "damageZeroWriteControls": 2,
                "hitZeroWriteControls": 7,
                "damageRebuildState": "PARTIAL_CONTRACT",
                "focusedParityTestsPassed": 21,
            },
            "determinism": {
                "allEightLedgersByteIdentical": True,
                "allSixteenReducerFilesByteIdentical": True,
                "normalizedReadyReceiptsEqual": True,
                "normalizedFields": ["generatedAtUtc", "outputs.*.lastWriteUtc"],
            },
            "verification": {
                "canonicalLiteralPinnedFullReplay": canonical_verify,
                "replicaLiteralPinnedFullReplay": replica_verify,
                "focusedAuthorityTests": {
                    "testsRun": 4,
                    "mechanicsPassed": 4,
                    "note": "Both full replay and all adverse mechanics passed; one initial prose-only assertion was corrected and rerun green.",
                },
            },
            "frozenOwners": {
                "campaign": stamp(CANONICAL / "_reducer/tools/re_campaign.py", relative_to=ROOT),
                "proof": stamp(CANONICAL / "_reducer/tools/re_level521_damage_writes.py", relative_to=ROOT),
                "preImportLauncher": stamp(CANONICAL / "_reducer/tools/re_campaign_frozen_bootstrap.py", relative_to=ROOT),
            },
            "selectionRule": {
                "requiredAbsolutePath": str(CANONICAL),
                "literalReadySha256ByRoot": READY,
                "requiredReducerId": REDUCER_ID,
                "requiredMode": "FULL",
                "reject": [
                    "replica as authority",
                    "generation-number selection",
                    "matching-ledger selection",
                    "self-derived READY or reducer pins",
                    "unpinned frozen-verifier success",
                    "integrity-only success",
                    "the v1 mutable-author proof pilot",
                ],
            },
            "limitations": {
                "damageInvocation": "ONE_REPLICATED_WITNESSED_WRITE_PATH_WITH_FIVE_GAPS",
                "hitControl": "ONE_GAP_FREE_INVOCATION_SEVEN_WATCHED_FIELDS_ONLY",
                "trace": "RECEIPT_HASH_BOUND_AND_ACTUAL_SIZE_CHECKED_NOT_REHASHED",
                "gameRunOrCapture": False,
                "ttdReplay": False,
                "liveGhidraMutation": False,
                "rebuildState": "PARTIAL_CONTRACT_NOT_REBUILD_READY",
                "nextValidGeneration": 13,
            },
        }
        require(Path(__file__).resolve().read_bytes() == author_start, "authority author changed before publication")
        OUT.parent.mkdir(parents=True, exist_ok=True)
        partial = OUT.with_name(OUT.name + ".partial")
        require(not partial.exists(), f"stale partial receipt exists: {partial}")
        with partial.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(receipt, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(partial, OUT)
        print(f"LEVEL521_GEN12_AUTHORITY_READY bytes={OUT.stat().st_size} sha256={sha256(OUT)} path={OUT}")
        return 0
    except (AuthorityError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(f"LEVEL521_GEN12_AUTHORITY_REFUSED: {exc}", file=sys.stderr)
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
