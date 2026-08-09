#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Select the literal-pinned canonical Generation 16 SetPos runtime campaign."""

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
CANONICAL = BASE / "generation-16-mission-native-setpos-runtime-v1"
REPLICA = BASE / "generation-16-mission-native-setpos-runtime-replica-v1"
PARENT = BASE / "generation-15-mission-native-setpos-reproof-v2"
PARENT_AUTHORITY = (
    BASE / "generation-15-mission-native-setpos-reproof-authority.ready.json"
)
PROOF = ROOT / "local-lab/mission-native-setpos-runtime-20260809-v1"
GHIDRA = ROOT / "local-lab/ghidra-mission-native-setpos-live-promotion-20260809-v1"
OUT = BASE / "generation-16-mission-native-setpos-runtime-authority.ready.json"

REDUCER_ID = "453fdb4df7233c6d3f8be04a6ba67b3762982bc4513ca4990b46f01141d55db0"
READY = {
    CANONICAL.name: "97493a76de550f5ae35074e285e39a561d9a323219741a42ac2ff25643cdc880",
    REPLICA.name: "69de7a0fe8f7abe74a345fbccc4abfdbd0cff77d4cae281dab581f6b1afe436f",
}
OUTPUTS = {
    "campaign-functions.tsv": "3b18ea14d343b7522085c1147bdc8fe252e8caa9467d17b08ec2902992d77039",
    "campaign-residuals.tsv": "6aaa5da3917079de3a172fb24b7de2b3ba99f1bc05ad40c4c427fcaa76d55ab6",
    "campaign-questions.tsv": "339050838d6b391ff8d7f8037befe26bfb67082fddbb92d3708ab5a8c461e2bc",
    "campaign-scenarios.tsv": "35a84fad46065d1317e48b41c66889a1dd12327077766423693b8839be857542",
    "campaign-levers.tsv": "fa337d96cfe7b6eca266b44aa39deded516e3a8cc02979a31671b449c66e3cdc",
    "campaign-contracts.tsv": "40fe17bceb5f3365b0076b0f17f38b137e61dfe0cea9a3361d29db3b23f5bdf7",
    "campaign-adjudications.tsv": "ec838904fe3c1563c484c924cd6858f07c93f34a6ec79e907db43d1e99c4247b",
    "campaign-supersessions.tsv": "4da539b16248ae9f5abfe5aa61845d9ec96351605060b8b05f16abb7353b008e",
}
COUNTS = {
    "functions": 8125,
    "residuals": 6118,
    "questions": 15249,
    "scenarios": 72,
    "levers": 915,
    "contracts": 14243,
    "adjudications": 6095,
    "supersessions": 588,
}
PARENT_READY_SHA256 = "629b32daf62f7c85e4819a024e0ade705be5548960d81cc320b636afa53e58a7"
PARENT_REDUCER_ID = "16ecb8974a7cd229015b2a5e0fd4f445d5f763d79aa2d667462324aa9e4ddfe9"
PARENT_AUTHORITY_SHA256 = "9fc1bf4eadd3ba654b80397c540515dba47022ce5905215851737673dc977ceb"
PROOF_READY_SHA256 = "40826e7e204bac8f9db1e64f7efb59e501f73401c58a48f051ac36244e7f22e0"
PROOF_AUTHOR_SHA256 = "8ee653ff31c42c011e5d25c49ec7acb0dd1c61b8d86b5f052f813624f44a2680"
GHIDRA_LIVE_SHA256 = "e64be82f360203fd2864450c5b3bd2d0a46441b9120eb79c8c423c3fe1ca0340"
PARITY_OWNER_SHA256 = "3ff10d190e286ae7a3d9ff29c1d91578e64ace45c3f94af879dace82c100743b"
PARITY_VALUE_SHA256 = "8318c0b785fe95d0a824c656f4b722e02083c830d6a924a8b72439ba4987ddb3"
PARITY_TEST_SHA256 = "ba96fae772bd1ae54e47057515fe5c0b4181c2af1802b82d70406ad8c9ad09c8"
OBSERVATION_ID = "SPR-0d5dfdddd2921cf3"
ADJUDICATION_ID = "A-16e165488adae1af"
FUNCTION_ENTITY = (
    "CODE:74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750:"
    "VA=0x00536c70:RANGES=679f653081c42099a6f086e0ff7e656596f1e5ca8588272c1bb35db45c7780fa"
)
CONTRACT_ID = "C-aca39413b2419b80"
PARENT_QUESTION = "Q-b9d7aa552ce48a32"
SUCCESSORS = [
    "Q-7b98e7f342645af1",
    "Q-aab3970a82afdd73",
    "Q-02e7898ea7e64827",
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
    require(receipt.get("generation") == 16, f"{root.name} generation differs")
    require(receipt.get("counts") == COUNTS, f"{root.name} counts differ")
    require(
        receipt.get("reducer", {}).get("id") == REDUCER_ID,
        f"{root.name} reducer differs",
    )
    require(
        advance.get("kind") == "MISSION_NATIVE_SETPOS_BOUNDED_RUNTIME_CONTRACT"
        and advance.get("schema")
        == "bea.re.mission-native-setpos-bounded-runtime-contract-advance.v1"
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
        and promotion.get("gradeFrom") == "C1_CANDIDATE_PARTIAL"
        and promotion.get("gradeTo") == "C2_BOUNDED_RUNTIME",
        f"{root.name} SetPos runtime claim boundary differs",
    )
    require(
        advance.get("questionsClosed") == 1
        and advance.get("questionsAdded") == 3
        and advance.get("adjudicationsAdded") == 1
        and advance.get("runtimeTreatmentsProved") == 2
        and advance.get("runtimeControlsProved") == 3
        and mapping.get("contractId") == CONTRACT_ID
        and mapping.get("state") == "PARTIAL_CONTRACT"
        and mapping.get("focusedTestsPassed") == 1
        and mapping.get("owner", {}).get("sha256") == PARITY_OWNER_SHA256
        and mapping.get("value", {}).get("sha256") == PARITY_VALUE_SHA256
        and mapping.get("test", {}).get("sha256") == PARITY_TEST_SHA256,
        f"{root.name} bounded mapping differs",
    )
    require(
        advance.get("proof", {}).get("ready", {}).get("sha256")
        == PROOF_READY_SHA256
        and advance.get("proof", {}).get("author", {}).get("sha256")
        == PROOF_AUTHOR_SHA256
        and advance.get("liveGhidraDisposition")
        == "EXISTING_GEN15_BOUNDARY_PROMOTION_CORROBORATED_NO_NEW_MUTATION",
        f"{root.name} proof or Ghidra disposition differs",
    )
    for name, expected in OUTPUTS.items():
        path = root / name
        require_plain_single(path, f"{root.name} {name}")
        require(sha256(path) == expected, f"{root.name} output differs: {name}")
    manifest = receipt.get("reducer", {}).get("files")
    require(isinstance(manifest, list) and len(manifest) == 27, "reducer manifest differs")
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
            sha256(PROOF / "runtime-proof.ready.json") == PROOF_READY_SHA256,
            "runtime proof READY differs",
        )
        require(
            sha256(ROOT / "tools/re_mission_native_setpos_runtime.py")
            == PROOF_AUTHOR_SHA256,
            "runtime proof author differs",
        )
        require(
            sha256(GHIDRA / "promotion/promotion.ready.json") == GHIDRA_LIVE_SHA256,
            "corroborating Ghidra authority differs",
        )
        require(
            sha256(ROOT / "rebuild/OnslaughtRebuild.Core/Level100ActorScriptRuntime.cs")
            == PARITY_OWNER_SHA256,
            "parity owner differs",
        )
        require(
            sha256(ROOT / "rebuild/OnslaughtRebuild.Core/Level100MissionProgram.cs")
            == PARITY_VALUE_SHA256,
            "parity value differs",
        )
        require(
            sha256(ROOT / "rebuild/OnslaughtRebuild.Core.Tests/Level100MissionTests.cs")
            == PARITY_TEST_SHA256,
            "parity test differs",
        )
        proof_verify = run_checked(
            [
                sys.executable,
                "-I",
                "-B",
                str(ROOT / "tools/re_mission_native_setpos_runtime.py"),
                "verify",
            ],
            "MISSION_NATIVE_SETPOS_RUNTIME_VERIFIED",
            timeout=120,
        )
        parity_verify = run_checked(
            [
                "dotnet",
                "test",
                str(
                    ROOT
                    / "rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj"
                ),
                "--no-restore",
                "--filter",
                "FullyQualifiedName~Level100MissionTests.MissionNativeSetPos_CopiesGetPosPositionAndPreservesOtherPoseState",
                "--verbosity",
                "minimal",
            ],
            "Passed!",
            timeout=180,
        )
        canonical_verify = run_full(CANONICAL, READY[CANONICAL.name])
        replica_verify = run_full(REPLICA, READY[REPLICA.name])
        require(
            Path(__file__).resolve().read_bytes() == author_start,
            "authority author changed during execution",
        )
        receipt = {
            "schema": "bea.re.mission-native-setpos-generation16-authority.v1",
            "verdict": "READY",
            "authorityClass": "FULL_REPLAY_CAMPAIGN_AUTHORITY",
            "replayScope": "FULL_CAMPAIGN_REDUCER_REPLAY_NOT_GAME_TTD_OR_GHIDRA_REPLAY",
            "completedAtUtc": datetime.now(timezone.utc).isoformat(),
            "lineageId": "incident-20260806-recovery-v1",
            "author": {
                "path": "tools/re_mission_native_setpos_runtime_campaign_authority.py",
                "bytes": len(author_start),
                "sha256": hashlib.sha256(author_start).hexdigest(),
            },
            "canonical": {
                "absolutePath": str(CANONICAL),
                "ready": stamp(CANONICAL / "campaign.ready.json", relative_to=CANONICAL),
                "reducerId": REDUCER_ID,
                "generation": 16,
                "kind": "MISSION_NATIVE_SETPOS_BOUNDED_RUNTIME_CONTRACT",
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
                "authorSha256": PROOF_AUTHOR_SHA256,
                "schema": "bea.re.mission-native-setpos-runtime-proof.v1",
                "claim": "MISSION_NATIVE_SETPOS_COPIES_POSITION_AND_IMMEDIATE_GETPOS_MATCHES",
            },
            "ghidraCorroboration": {
                "path": GHIDRA.relative_to(ROOT).as_posix(),
                "liveAuthoritySha256": GHIDRA_LIVE_SHA256,
                "scope": "EXISTING_GEN15_BOUNDARY_PROMOTION_NO_NEW_MUTATION",
            },
            "rebuild": {
                "state": "PARTIAL_CONTRACT",
                "owner": stamp(
                    ROOT / "rebuild/OnslaughtRebuild.Core/Level100ActorScriptRuntime.cs",
                    relative_to=ROOT,
                ),
                "value": stamp(
                    ROOT / "rebuild/OnslaughtRebuild.Core/Level100MissionProgram.cs",
                    relative_to=ROOT,
                ),
                "test": stamp(
                    ROOT / "rebuild/OnslaughtRebuild.Core.Tests/Level100MissionTests.cs",
                    relative_to=ROOT,
                ),
                "focusedParity": parity_verify,
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
                "treatmentReplications": 2,
                "controls": 3,
                "scriptVisiblePositionCopy": True,
                "completeInternalWriteSet": False,
                "liveGhidraMutation": False,
                "ttdReplay": False,
                "executableBytesChanged": 0,
                "rebuildState": "PARTIAL_CONTRACT",
            },
            "determinism": {
                "allEightLedgersByteIdentical": True,
                "allTwentySevenReducerFilesByteIdentical": True,
                "normalizedReadyReceiptsEqual": True,
                "normalizedFields": ["generatedAtUtc", "outputs.*.lastWriteUtc"],
            },
            "verification": {
                "runtimeProof": proof_verify,
                "canonicalLiteralPinnedFullReplay": canonical_verify,
                "replicaLiteralPinnedFullReplay": replica_verify,
            },
            "frozenOwners": {
                "campaign": stamp(
                    CANONICAL / "_reducer/tools/re_campaign.py", relative_to=ROOT
                ),
                "proof": stamp(
                    CANONICAL / "_reducer/tools/re_mission_native_setpos_runtime.py",
                    relative_to=ROOT,
                ),
                "parityOwner": stamp(
                    CANONICAL
                    / "_reducer/rebuild/OnslaughtRebuild.Core/Level100ActorScriptRuntime.cs",
                    relative_to=ROOT,
                ),
                "parityValue": stamp(
                    CANONICAL
                    / "_reducer/rebuild/OnslaughtRebuild.Core/Level100MissionProgram.cs",
                    relative_to=ROOT,
                ),
                "parityTest": stamp(
                    CANONICAL
                    / "_reducer/rebuild/OnslaughtRebuild.Core.Tests/Level100MissionTests.cs",
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
                    "complete write-set, arbitrary-vector, failure-path, persistence, or rebuild-ready overclaims",
                ],
            },
            "limitations": {
                "proofScope": "FORCED_SAFE_COPY_SETPOS_IMMEDIATE_GETPOS_ROUNDTRIP",
                "naturalShippedCall": False,
                "ttdTraceOrReplayForThisAdvance": False,
                "liveGhidraMutation": False,
                "internalWriteSet": "OPEN",
                "orientationCollisionPhysicsNavigationPersistence": "OPEN",
                "otherReceiversVectorsAndFailures": "OPEN",
                "rebuildState": "PARTIAL_CONTRACT",
                "nextValidGeneration": 17,
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
            "MISSION_SETPOS_GEN16_AUTHORITY_READY "
            f"bytes={OUT.stat().st_size} sha256={sha256(OUT)} path={OUT}"
        )
        return 0
    except (
        AuthorityError,
        OSError,
        subprocess.SubprocessError,
        json.JSONDecodeError,
    ) as exc:
        print(f"MISSION_SETPOS_GEN16_AUTHORITY_REFUSED: {exc}", file=sys.stderr)
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
