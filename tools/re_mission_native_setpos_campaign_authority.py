#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Select the literal-pinned canonical Generation 15 SetPos campaign."""

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
CANONICAL = BASE / "generation-15-mission-native-setpos-reproof-v2"
REPLICA = BASE / "generation-15-mission-native-setpos-reproof-replica-v2"
PARENT = BASE / "generation-14-tokenarchive-dispatch-reproof-v1"
PARENT_AUTHORITY = BASE / "generation-14-tokenarchive-dispatch-reproof-authority.ready.json"
PROOF = ROOT / "local-lab/mission-native-setpos-boundary-reproof-20260809-v1"
GHIDRA = ROOT / "local-lab/ghidra-mission-native-setpos-live-promotion-20260809-v1"
OUT = BASE / "generation-15-mission-native-setpos-reproof-authority.ready.json"

REDUCER_ID = "16ecb8974a7cd229015b2a5e0fd4f445d5f763d79aa2d667462324aa9e4ddfe9"
READY = {
    CANONICAL.name: "629b32daf62f7c85e4819a024e0ade705be5548960d81cc320b636afa53e58a7",
    REPLICA.name: "3dc9d0f848bc78f1d587030fe95f21283441800f161c599df87e9bec4857c4d1",
}
OUTPUTS = {
    "campaign-functions.tsv": "5139617ef08e09bd316bae150dde6cadb499733bdea071df8765df34d69fcead",
    "campaign-residuals.tsv": "6aaa5da3917079de3a172fb24b7de2b3ba99f1bc05ad40c4c427fcaa76d55ab6",
    "campaign-questions.tsv": "f9a88ede7b7930ea32b43456d9c2d301c0078a63cb934752b6e41013b1cd8198",
    "campaign-scenarios.tsv": "35a84fad46065d1317e48b41c66889a1dd12327077766423693b8839be857542",
    "campaign-levers.tsv": "fa337d96cfe7b6eca266b44aa39deded516e3a8cc02979a31671b449c66e3cdc",
    "campaign-contracts.tsv": "33ee92294f764e2aab8c45329983f02ca02be45c46ce699f6b93cffe87872643",
    "campaign-adjudications.tsv": "512cf71273e9f8e45c55231e6a27a287d8fba4980a54dae45ba1645cdcf31a4b",
    "campaign-supersessions.tsv": "4da539b16248ae9f5abfe5aa61845d9ec96351605060b8b05f16abb7353b008e",
}
COUNTS = {
    "functions": 8125,
    "residuals": 6118,
    "questions": 15246,
    "scenarios": 72,
    "levers": 915,
    "contracts": 14243,
    "adjudications": 6094,
    "supersessions": 588,
}
PARENT_READY_SHA256 = "9864424def44034a5a5e9a68814ce111076182ad7ea898c9d0040d888c92f32b"
PARENT_REDUCER_ID = "ec58dc9ec399d719677c5ab98ab0ac2efe60d8138c4f2c829f3e5930a946dec2"
PARENT_AUTHORITY_SHA256 = "83a5544bdde805762b01983171c336826ea62a8b2dd8be94109bef959560ff72"
PROOF_READY_SHA256 = "7fca2c1e960166603ece107c112217ea674e6c2d898622594432817a803a0a7d"
PROOF_AUTHOR_SHA256 = "97cbc606a0c3a537e1a19234c7f2b3e9a304ed4e75fcff80f5c0e2739f0c43c9"
GHIDRA_SCRATCH_SHA256 = "35bb58e3111124b8ad934d561850fe5e517ebfc80af0c51ba9dcadfb86976491"
GHIDRA_LIVE_SHA256 = "e64be82f360203fd2864450c5b3bd2d0a46441b9120eb79c8c423c3fe1ca0340"
GHIDRA_OWNER_SHA256 = "0c2b703bed6ad1060d6297cf8b81af6f9d74f5406b95919598930cc04124d66f"
GHIDRA_TOOL_SHA256 = "f42d1e29d99e79eee5b9720f1f58a51b04ed50c06b84b8d0900114b0689bf602"
PROMOTION_ID = "SP-279860c25156b65d"
FUNCTION_ENTITY = (
    "CODE:74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750:"
    "VA=0x00536c70:RANGES=679f653081c42099a6f086e0ff7e656596f1e5ca8588272c1bb35db45c7780fa"
)


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
    function = advance.get("function", {})
    partition = advance.get("partition", {})
    require(receipt.get("generation") == 15, f"{root.name} generation differs")
    require(receipt.get("counts") == COUNTS, f"{root.name} counts differ")
    require(
        receipt.get("reducer", {}).get("id") == REDUCER_ID,
        f"{root.name} reducer differs",
    )
    require(
        advance.get("kind") == "MISSION_NATIVE_SETPOS_BOUNDARY_AND_STATIC_CONTRACT_REPROOF"
        and advance.get("schema")
        == "bea.re.mission-native-setpos-boundary-static-contract-reproof-advance.v1"
        and advance.get("branchId") == "incident-20260806-recovery-v1"
        and advance.get("promotionId") == PROMOTION_ID,
        f"{root.name} advance identity differs",
    )
    require(
        function.get("entityKey") == FUNCTION_ENTITY
        and function.get("name") == "IScript__SetPos"
        and function.get("nativeShippedName") == "SetPos"
        and function.get("bodyBytes") == 42
        and function.get("instructionCount") == 17
        and function.get("semanticGrade") == "C1_CANDIDATE_PARTIAL"
        and function.get("semanticGradeCeiling") == "C1_STATIC"
        and function.get("runtimeVerdict") == "UNSCORED"
        and function.get("semanticPromotionApplied") is False,
        f"{root.name} SetPos claim boundary differs",
    )
    require(
        partition.get("parentBytes") == 63
        and partition.get("functionCount") == 1
        and partition.get("functionBytes") == 42
        and partition.get("paddingCount") == 2
        and partition.get("paddingBytes") == 21,
        f"{root.name} SetPos partition differs",
    )
    require(
        advance.get("questions", {}).get("closed")
        == ["Q-b87fb6bcbb8fb28d", "Q-417d6c90fb7c0519"]
        and advance.get("questions", {}).get("opened") == ["Q-b9d7aa552ce48a32"]
        and advance.get("adjudications", {})
        == {
            "partition": "A-78f0343e9f41235c",
            "boundary": "A-88a1cc899a6a5975",
        },
        f"{root.name} SetPos question/adjudication boundary differs",
    )
    require(
        advance.get("ghidraPromotion", {}).get("liveAuthority", {}).get("sha256")
        == GHIDRA_LIVE_SHA256,
        f"{root.name} live Ghidra authority differs",
    )
    for name, expected in OUTPUTS.items():
        path = root / name
        require_plain_single(path, f"{root.name} {name}")
        require(sha256(path) == expected, f"{root.name} output differs: {name}")
    manifest = receipt.get("reducer", {}).get("files")
    require(isinstance(manifest, list) and len(manifest) == 23, "reducer manifest differs")
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
    require(
        completed.returncode == 0 and "CAMPAIGN_VERIFIED" in completed.stdout,
        f"full replay failed for {root.name}: {completed.stderr}",
    )
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
        require(sha256(PARENT / "campaign.ready.json") == PARENT_READY_SHA256, "parent READY differs")
        require(sha256(PARENT_AUTHORITY) == PARENT_AUTHORITY_SHA256, "parent authority differs")
        require(sha256(PROOF / "proof.ready.json") == PROOF_READY_SHA256, "proof READY differs")
        require(sha256(ROOT / "tools/re_mission_native_setpos_reproof.py") == PROOF_AUTHOR_SHA256, "proof author differs")
        require(sha256(GHIDRA / "promotion/scratch-authority-v2.ready.json") == GHIDRA_SCRATCH_SHA256, "Ghidra scratch authority differs")
        require(sha256(GHIDRA / "promotion/promotion.ready.json") == GHIDRA_LIVE_SHA256, "Ghidra live authority differs")
        require(sha256(ROOT / "tools/ghidra_mission_native_setpos_promotion_authority.py") == GHIDRA_OWNER_SHA256, "Ghidra authority author differs")
        require(sha256(ROOT / "tools/GhidraApplyMissionNativeSetPos.java") == GHIDRA_TOOL_SHA256, "Ghidra Java tool differs")
        canonical_verify = run_full(CANONICAL, READY[CANONICAL.name])
        replica_verify = run_full(REPLICA, READY[REPLICA.name])
        require(Path(__file__).resolve().read_bytes() == author_start, "authority author changed during execution")
        receipt = {
            "schema": "bea.re.mission-native-setpos-generation15-authority.v1",
            "verdict": "READY",
            "authorityClass": "FULL_REPLAY_CAMPAIGN_AUTHORITY",
            "replayScope": "FULL_CAMPAIGN_REDUCER_REPLAY_NOT_GAME_TTD_OR_GHIDRA_REPLAY",
            "completedAtUtc": datetime.now(timezone.utc).isoformat(),
            "lineageId": "incident-20260806-recovery-v1",
            "author": {
                "path": "tools/re_mission_native_setpos_campaign_authority.py",
                "bytes": len(author_start),
                "sha256": hashlib.sha256(author_start).hexdigest(),
            },
            "canonical": {
                "absolutePath": str(CANONICAL),
                "ready": stamp(CANONICAL / "campaign.ready.json", relative_to=CANONICAL),
                "reducerId": REDUCER_ID,
                "generation": 15,
                "kind": "MISSION_NATIVE_SETPOS_BOUNDARY_AND_STATIC_CONTRACT_REPROOF",
                "promotionId": PROMOTION_ID,
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
                "schema": "bea.re.mission-native-setpos-boundary-reproof.v1",
            },
            "ghidraPromotion": {
                "path": GHIDRA.relative_to(ROOT).as_posix(),
                "scratchAuthoritySha256": GHIDRA_SCRATCH_SHA256,
                "liveAuthoritySha256": GHIDRA_LIVE_SHA256,
                "ownerSha256": GHIDRA_OWNER_SHA256,
                "toolSha256": GHIDRA_TOOL_SHA256,
                "scope": "ONE_FUNCTION_NAME_SIGNATURE_COMMENT_NO_BINARY_CHANGE",
            },
            "counts": COUNTS,
            "outputs": {
                name: {"bytes": (CANONICAL / name).stat().st_size, "sha256": digest}
                for name, digest in OUTPUTS.items()
            },
            "claimBoundary": {
                "functionEntityAdded": FUNCTION_ENTITY,
                "functionRowsAdded": 1,
                "residualRowsRemoved": 1,
                "residualRowsAdded": 2,
                "contractRowsRemoved": 1,
                "contractRowsAdded": 3,
                "questionsClosed": 2,
                "questionsAdded": 1,
                "nonsemanticAdjudicationsAdded": 2,
                "supersessionsAdded": 4,
                "functionName": "IScript__SetPos",
                "bodyBytes": 42,
                "instructionCount": 17,
                "paddingBytes": 21,
                "semanticGradeCeiling": "C1_STATIC",
                "runtimeVerdict": "UNSCORED",
                "liveGhidraMutation": True,
                "executableBytesChanged": 0,
                "rebuildState": "NOT_READY",
            },
            "determinism": {
                "allEightLedgersByteIdentical": True,
                "allTwentyThreeReducerFilesByteIdentical": True,
                "normalizedReadyReceiptsEqual": True,
                "normalizedFields": ["generatedAtUtc", "outputs.*.lastWriteUtc"],
            },
            "verification": {
                "canonicalLiteralPinnedFullReplay": canonical_verify,
                "replicaLiteralPinnedFullReplay": replica_verify,
            },
            "frozenOwners": {
                "campaign": stamp(CANONICAL / "_reducer/tools/re_campaign.py", relative_to=ROOT),
                "proof": stamp(CANONICAL / "_reducer/tools/re_mission_native_setpos_reproof.py", relative_to=ROOT),
                "ghidraAuthority": stamp(CANONICAL / "_reducer/tools/ghidra_mission_native_setpos_promotion_authority.py", relative_to=ROOT),
                "ghidraTool": stamp(CANONICAL / "_reducer/tools/GhidraApplyMissionNativeSetPos.java", relative_to=ROOT),
                "preImportLauncher": stamp(ROOT / "tools/re_campaign_frozen_bootstrap.py", relative_to=ROOT),
            },
            "selectionRule": {
                "requiredAbsolutePath": str(CANONICAL),
                "literalReadySha256ByRoot": READY,
                "requiredReducerId": REDUCER_ID,
                "requiredMode": "FULL",
                "reject": [
                    "replica as authority",
                    "Generation 15 v1 drafts rejected by frozen portability gate",
                    "generation-number or matching-ledger selection",
                    "self-derived READY or reducer pins",
                    "unpinned or integrity-only verifier success",
                    "runtime vector, complete write-set, failure-path, or rebuild claims",
                ],
            },
            "limitations": {
                "proofScope": "STATIC_BOUNDARY_NAME_CALL_SHAPE_PLUS_SEPARATELY_READ_BACK_LIVE_GHIDRA_METADATA",
                "gameRunOrCaptureForThisAdvance": False,
                "ttdReplayForThisAdvance": False,
                "liveGhidraMutation": True,
                "runtimeVectorValues": "OPEN",
                "runtimeTargetWrites": "OPEN",
                "failureBehavior": "OPEN",
                "rebuildState": "NOT_READY_PENDING_RUNTIME_CONTRACT",
                "nextValidGeneration": 16,
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
        print(f"MISSION_SETPOS_GEN15_AUTHORITY_READY bytes={OUT.stat().st_size} sha256={sha256(OUT)} path={OUT}")
        return 0
    except (AuthorityError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(f"MISSION_SETPOS_GEN15_AUTHORITY_REFUSED: {exc}", file=sys.stderr)
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
