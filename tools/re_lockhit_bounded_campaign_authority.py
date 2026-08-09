#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Select the literal-pinned canonical Generation 17 LockHit campaign."""

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
CANONICAL = BASE / "generation-17-lockhit-bounded-contract-v1"
REPLICA = BASE / "generation-17-lockhit-bounded-contract-replica-v1"
PARENT = BASE / "generation-16-mission-native-setpos-runtime-v1"
PARENT_AUTHORITY = (
    BASE / "generation-16-mission-native-setpos-runtime-authority.ready.json"
)
PROOF = ROOT / "local-lab/lockhit-bounded-contract-reproof-20260809-v1"
GHIDRA = (
    ROOT
    / "local-lab/ghidra-target-lock-semantic-live-promotion-20260804-v2/"
    "promotion/promotion.ready.json"
)
OUT = BASE / "generation-17-lockhit-bounded-contract-authority.ready.json"

REDUCER_ID = "fbb343d629fa12a641aced04db88b59e5270e1f45990d9d203284302f8761621"
READY = {
    CANONICAL.name: "6d794905d6fc5daea11f99b781cf8eb7740765e749c784d02507d43436b801a2",
    REPLICA.name: "dcef22def1e4190fd32366637654587202635c185f0088ca39d883168bba7ba6",
}
OUTPUTS = {
    "campaign-functions.tsv": "50970af530be6cf9885de7af33cede59f8ed80f2f98bf6541ec4239a77db1bd2",
    "campaign-residuals.tsv": "6aaa5da3917079de3a172fb24b7de2b3ba99f1bc05ad40c4c427fcaa76d55ab6",
    "campaign-questions.tsv": "e86ead4f97a94182750a522c9cf44d0664108dec3b81678c28be14531213a3b0",
    "campaign-scenarios.tsv": "35a84fad46065d1317e48b41c66889a1dd12327077766423693b8839be857542",
    "campaign-levers.tsv": "fa337d96cfe7b6eca266b44aa39deded516e3a8cc02979a31671b449c66e3cdc",
    "campaign-contracts.tsv": "166358f44a0e1bad7c29b541d3602fa722f8b57c7b70aee28ace6e247c89e1c1",
    "campaign-adjudications.tsv": "ec23e0831400085e456b386ab190116700de6cae43da4f6bde071df9a8cb4770",
    "campaign-supersessions.tsv": "4da539b16248ae9f5abfe5aa61845d9ec96351605060b8b05f16abb7353b008e",
}
COUNTS = {
    "functions": 8125,
    "residuals": 6118,
    "questions": 15253,
    "scenarios": 72,
    "levers": 915,
    "contracts": 14243,
    "adjudications": 6096,
    "supersessions": 588,
}
PARENT_READY_SHA256 = "97493a76de550f5ae35074e285e39a561d9a323219741a42ac2ff25643cdc880"
PARENT_REDUCER_ID = "453fdb4df7233c6d3f8be04a6ba67b3762982bc4513ca4990b46f01141d55db0"
PARENT_AUTHORITY_SHA256 = "1d04fef865c510cacd4c545999367d88c214b0ffe5a7bc4eac68e50d185a6981"
PROOF_READY_SHA256 = "aeb60bd5565872579fd58a2a557a1b466ca81a89e06dcf0a2cce632fa7448739"
PROOF_AUTHOR_SHA256 = "84cb66a4fc318fec37ad2f1e0645982a7cc29131019bc0d333028b484d5509b7"
PROOF_OBSERVATION_SHA256 = "a9ffb3babd37eb8a15ccc56f9a710219aaf002fc741c3980d621774f707a8a8b"
GHIDRA_LIVE_SHA256 = "77f635e552b7a2dd8425af012204f8172eadcb1de8ecdb02a30e2c12ff9b9945"
OBSERVATION_ID = "LHC-997ec4a9b32a80a8"
ADJUDICATION_ID = "A-9d0865b13dd319ef"
FUNCTION_ENTITY = (
    "CODE:74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750:"
    "VA=0x00407140:RANGES=6c9813a631717dc2e10869bce7bacb6bab2063ad4621edf0dbe218c69a9c4302"
)
CONTRACT_ID = "C-f37e6a92ba35a0bf"
PARENT_QUESTION = "Q-47284f43220ab833"
SUCCESSORS = [
    "Q-2e152f6c1ad74504",
    "Q-b4838b78fddb5be6",
    "Q-560e644e27958b87",
    "Q-b0230a2ddfa473a1",
]


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
    name = (
        path.resolve().relative_to(relative_to.resolve()).as_posix()
        if relative_to is not None
        else str(path.resolve())
    )
    return {"path": name, "bytes": path.stat().st_size, "sha256": sha256(path)}


def require_plain_single(path: Path, label: str) -> None:
    require(path.is_file(), f"{label} is absent")
    file_stat = path.lstat()
    require(not path.is_symlink(), f"{label} is symlinked")
    require(
        not (getattr(file_stat, "st_file_attributes", 0) & 0x400),
        f"{label} is reparse-linked",
    )
    require(file_stat.st_nlink == 1, f"{label} has multiple hard links")


def validate_campaign(root: Path, expected_ready: str) -> dict:
    require(root.resolve() == root, f"campaign root is not canonical: {root}")
    ready_path = root / "campaign.ready.json"
    require_plain_single(ready_path, f"{root.name} READY")
    require(sha256(ready_path) == expected_ready, f"{root.name} READY differs")
    receipt = json.loads(ready_path.read_text(encoding="utf-8"))
    advance = receipt.get("advance", {})
    promotion = advance.get("promotion", {})
    mapping = advance.get("rebuildMapping", {})
    trace = advance.get("traceDisposition", {})
    require(receipt.get("generation") == 17, f"{root.name} generation differs")
    require(receipt.get("counts") == COUNTS, f"{root.name} counts differ")
    require(
        receipt.get("reducer", {}).get("id") == REDUCER_ID,
        f"{root.name} reducer differs",
    )
    require(
        advance.get("kind") == "TTD_CBATTLEENGINE_LOCKHIT_BOUNDED_CONTRACT"
        and advance.get("schema")
        == "bea.re.ttd-cbattleengine-lockhit-bounded-contract-advance.v1"
        and advance.get("branchId") == "incident-20260806-recovery-v1"
        and advance.get("observationId") == OBSERVATION_ID
        and advance.get("verdict") == "SURVIVED",
        f"{root.name} advance identity differs",
    )
    require(
        promotion.get("entityKey") == FUNCTION_ENTITY
        and promotion.get("contractId") == CONTRACT_ID
        and promotion.get("parentQuestionId") == PARENT_QUESTION
        and promotion.get("successorQuestionIds") == SUCCESSORS
        and promotion.get("adjudicationId") == ADJUDICATION_ID
        and promotion.get("gradeFrom") == "C0_OPAQUE"
        and promotion.get("gradeTo") == "C2_BOUNDED_RUNTIME",
        f"{root.name} LockHit claim boundary differs",
    )
    require(
        advance.get("questionsClosed") == 1
        and advance.get("questionsAdded") == 4
        and advance.get("adjudicationsAdded") == 1
        and advance.get("runtimeWriteReplaysProved") == 3
        and advance.get("runtimeCallContextReplaysProved") == 2
        and advance.get("independentGameplayReplications") == 0
        and mapping.get("contractId") == CONTRACT_ID
        and mapping.get("state") == "NOT_READY"
        and mapping.get("owner") == "UNASSIGNED"
        and mapping.get("implementation") == "UNMAPPED"
        and mapping.get("tests") == "UNMAPPED",
        f"{root.name} bounded contract disposition differs",
    )
    require(
        advance.get("proof", {}).get("ready", {}).get("sha256")
        == PROOF_READY_SHA256
        and advance.get("proof", {}).get("author", {}).get("sha256")
        == PROOF_AUTHOR_SHA256
        and advance.get("proof", {}).get("observation", {}).get("sha256")
        == PROOF_OBSERVATION_SHA256
        and advance.get("liveGhidraDisposition")
        == "EXISTING_TARGET_LOCK_SEMANTIC_PROMOTION_CORROBORATED_NO_NEW_MUTATION",
        f"{root.name} proof or Ghidra disposition differs",
    )
    require(
        trace.get("bytes") == 14_214_496_256
        and trace.get("receiptSha256")
        == "45ab04297f32bb27ac0c80e8ecb0b332e666a9955caea0763a83984affb74ac2"
        and trace.get("actualSizeVerified") is True
        and trace.get("actualHashRecomputed") is False,
        f"{root.name} trace disposition differs",
    )
    for name, expected in OUTPUTS.items():
        path = root / name
        require_plain_single(path, f"{root.name} {name}")
        require(sha256(path) == expected, f"{root.name} output differs: {name}")
    manifest = receipt.get("reducer", {}).get("files")
    require(isinstance(manifest, list) and len(manifest) == 28, "reducer manifest differs")
    expected_paths = {str(row.get("path")) for row in manifest}
    actual_paths = {
        path.relative_to(root).as_posix()
        for path in (root / "_reducer").rglob("*")
        if path.is_file()
    }
    require(actual_paths == expected_paths, f"{root.name} reducer file set differs")
    for row in manifest:
        path = root / row["path"]
        require_plain_single(path, f"{root.name} reducer {row['path']}")
        require(
            path.stat().st_size == row["bytes"] and sha256(path) == row["sha256"],
            f"{root.name} reducer entry differs: {row['path']}",
        )
    return receipt


def clean_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment["BEA_REPO_ROOT"] = str(ROOT)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    for name in (
        "PYTHONHOME",
        "PYTHONPATH",
        "PYTHONSTARTUP",
        "PYTHONINSPECT",
        "PYTHONUSERBASE",
    ):
        environment.pop(name, None)
    return environment


def run_checked(argv: list[str], marker: str, *, timeout: int) -> dict[str, object]:
    started = time.monotonic()
    completed = subprocess.run(
        argv,
        cwd=ROOT,
        env=clean_environment(),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    require(
        completed.returncode == 0 and marker in completed.stdout,
        f"command failed: {argv}: {completed.stderr[-1000:]}",
    )
    return {
        "command": argv,
        "exitCode": completed.returncode,
        "marker": marker,
        "elapsedSeconds": round(time.monotonic() - started, 3),
    }


def run_full(root: Path, expected_ready: str) -> dict[str, object]:
    bootstrap = ROOT / "tools/re_campaign_frozen_bootstrap.py"
    require_plain_single(bootstrap, "trusted frozen bootstrap")
    return run_checked(
        [
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
        ],
        "CAMPAIGN_VERIFIED",
        timeout=1200,
    )


def main() -> int:
    try:
        require(not OUT.exists(), f"refusing existing authority receipt: {OUT}")
        author_start = Path(__file__).resolve().read_bytes()
        canonical = validate_campaign(CANONICAL, READY[CANONICAL.name])
        replica = validate_campaign(REPLICA, READY[REPLICA.name])
        require(not os.path.samefile(CANONICAL, REPLICA), "campaign roots alias")
        for name in OUTPUTS:
            require(
                (CANONICAL / name).read_bytes() == (REPLICA / name).read_bytes(),
                f"replica ledger differs: {name}",
            )
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
        for source in (canonical, replica):
            value = json.loads(json.dumps(source))
            value.pop("generatedAtUtc")
            for output in value["outputs"].values():
                output.pop("lastWriteUtc")
            normalized.append(value)
        require(normalized[0] == normalized[1], "normalized READY receipts differ")
        require(
            sha256(PARENT / "campaign.ready.json") == PARENT_READY_SHA256,
            "parent READY differs",
        )
        require(
            sha256(PARENT_AUTHORITY) == PARENT_AUTHORITY_SHA256,
            "parent authority differs",
        )
        require(
            sha256(PROOF / "proof.ready.json") == PROOF_READY_SHA256,
            "LockHit proof READY differs",
        )
        require(
            sha256(PROOF / "observation.json") == PROOF_OBSERVATION_SHA256,
            "LockHit proof observation differs",
        )
        require(
            sha256(ROOT / "tools/re_lockhit_bounded_contract.py")
            == PROOF_AUTHOR_SHA256,
            "LockHit proof author differs",
        )
        require(sha256(GHIDRA) == GHIDRA_LIVE_SHA256, "Ghidra corroboration differs")
        proof_verify = run_checked(
            [
                sys.executable,
                "-I",
                "-B",
                str(ROOT / "tools/re_lockhit_bounded_contract.py"),
                "--repo",
                str(ROOT),
                "verify",
                "--proof",
                str(PROOF),
            ],
            "LOCKHIT_BOUNDED_CONTRACT_PROOF_VERIFIED",
            timeout=180,
        )
        canonical_verify = run_full(CANONICAL, READY[CANONICAL.name])
        replica_verify = run_full(REPLICA, READY[REPLICA.name])
        require(
            Path(__file__).resolve().read_bytes() == author_start,
            "authority author changed during execution",
        )
        receipt = {
            "schema": "bea.re.lockhit-bounded-generation17-authority.v1",
            "verdict": "READY",
            "authorityClass": "FULL_REPLAY_CAMPAIGN_AUTHORITY",
            "replayScope": "FULL_CAMPAIGN_REDUCER_REPLAY_NOT_GAME_TTD_OR_GHIDRA_REPLAY",
            "completedAtUtc": datetime.now(timezone.utc).isoformat(),
            "lineageId": "incident-20260806-recovery-v1",
            "author": {
                "path": "tools/re_lockhit_bounded_campaign_authority.py",
                "bytes": len(author_start),
                "sha256": hashlib.sha256(author_start).hexdigest(),
            },
            "canonical": {
                "absolutePath": str(CANONICAL),
                "ready": stamp(CANONICAL / "campaign.ready.json", relative_to=CANONICAL),
                "reducerId": REDUCER_ID,
                "generation": 17,
                "kind": "TTD_CBATTLEENGINE_LOCKHIT_BOUNDED_CONTRACT",
                "observationId": OBSERVATION_ID,
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
                "observationSha256": PROOF_OBSERVATION_SHA256,
                "authorSha256": PROOF_AUTHOR_SHA256,
                "schema": "bea.re.lockhit-bounded-contract-proof.v1",
                "claim": "LOCKHIT_ONE_NODE_REMOVAL_BOUNDED_CONTRACT",
            },
            "ghidraCorroboration": {
                "path": GHIDRA.relative_to(ROOT).as_posix(),
                "liveAuthoritySha256": GHIDRA_LIVE_SHA256,
                "scope": "EXISTING_TARGET_LOCK_PROMOTION_NO_NEW_MUTATION",
            },
            "rebuild": {
                "state": "NOT_READY",
                "owner": "UNASSIGNED",
                "implementation": "UNMAPPED",
                "tests": "UNMAPPED",
                "reason": "no evidence-bound fired-lock container exists in the rebuild",
            },
            "counts": COUNTS,
            "outputs": {
                name: {"bytes": (CANONICAL / name).stat().st_size, "sha256": digest}
                for name, digest in OUTPUTS.items()
            },
            "claimBoundary": {
                "functionEntity": FUNCTION_ENTITY,
                "contractId": CONTRACT_ID,
                "parentQuestionClosed": PARENT_QUESTION,
                "successorQuestionsAdded": SUCCESSORS,
                "adjudicationId": ADJUDICATION_ID,
                "semanticGrade": "C2_BOUNDED_RUNTIME",
                "writeReplays": 3,
                "callContextReplays": 2,
                "sameImmutableGameplayEvent": True,
                "independentGameplayReplication": False,
                "nonNullSingleNodePath": True,
                "nullNotFoundMultiNodePaths": "OPEN",
                "globalFreeHeadDirectlyWatched": False,
                "payloadDestructorAndFullReturn": "OPEN",
                "liveGhidraMutation": False,
                "executableBytesChanged": 0,
                "rebuildState": "NOT_READY",
            },
            "determinism": {
                "allEightLedgersByteIdentical": True,
                "allTwentyEightReducerFilesByteIdentical": True,
                "normalizedReadyReceiptsEqual": True,
                "normalizedFields": ["generatedAtUtc", "outputs.*.lastWriteUtc"],
            },
            "verification": {
                "boundedProof": proof_verify,
                "canonicalLiteralPinnedFullReplay": canonical_verify,
                "replicaLiteralPinnedFullReplay": replica_verify,
            },
            "frozenOwners": {
                "campaign": stamp(
                    CANONICAL / "_reducer/tools/re_campaign.py", relative_to=ROOT
                ),
                "proof": stamp(
                    CANONICAL / "_reducer/tools/re_lockhit_bounded_contract.py",
                    relative_to=ROOT,
                ),
                "preImportLauncher": stamp(
                    ROOT / "tools/re_campaign_frozen_bootstrap.py", relative_to=ROOT
                ),
            },
            "selectionRule": {
                "requiredAbsolutePath": str(CANONICAL),
                "literalReadySha256ByRoot": READY,
                "requiredReducerId": REDUCER_ID,
                "requiredMode": "FULL",
                "reject": [
                    "replica as authority",
                    "generation-number or matching-ledger selection",
                    "self-derived READY or reducer pins",
                    "unpinned or integrity-only verifier success",
                    "independent-gameplay, complete-write-set, global-watch, destructor, full-return, or rebuild-ready overclaims",
                ],
            },
            "limitations": {
                "proofScope": "ONE_NON_NULL_SOLE_MATCHING_LOCKHIT_REMOVAL_EVENT",
                "sameImmutableGameplayEvent": True,
                "independentGameplayReplication": False,
                "traceActualHashRecomputed": False,
                "nullNotFoundMultiNodePaths": "OPEN",
                "globalFreeHeadDirectWatch": "OPEN",
                "payloadDestructorAndFullReturn": "OPEN",
                "liveGhidraMutation": False,
                "rebuildState": "NOT_READY",
                "nextValidGeneration": 18,
            },
        }
        require(
            Path(__file__).resolve().read_bytes() == author_start,
            "authority author changed before publication",
        )
        OUT.parent.mkdir(parents=True, exist_ok=True)
        partial = OUT.with_name(OUT.name + ".partial")
        require(not partial.exists(), f"stale partial receipt exists: {partial}")
        with partial.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(receipt, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(partial, OUT)
        print(
            "LOCKHIT_GEN17_AUTHORITY_READY "
            f"bytes={OUT.stat().st_size} sha256={sha256(OUT)} path={OUT}"
        )
        return 0
    except (
        AuthorityError,
        OSError,
        subprocess.SubprocessError,
        json.JSONDecodeError,
    ) as exc:
        print(f"LOCKHIT_GEN17_AUTHORITY_REFUSED: {exc}", file=sys.stderr)
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
