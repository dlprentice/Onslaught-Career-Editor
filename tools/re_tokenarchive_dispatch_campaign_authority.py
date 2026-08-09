#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Select the literal-pinned canonical Generation 14 TokenArchive campaign."""

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
CANONICAL = BASE / "generation-14-tokenarchive-dispatch-reproof-v1"
REPLICA = BASE / "generation-14-tokenarchive-dispatch-reproof-replica-v1"
PARENT = BASE / "generation-13-applydamage-primary-reproof-v1"
PARENT_AUTHORITY = BASE / "generation-13-applydamage-primary-reproof-authority.ready.json"
PROOF = ROOT / "local-lab/tokenarchive-dispatch-table-reproof-20260809-v1"
OUT = BASE / "generation-14-tokenarchive-dispatch-reproof-authority.ready.json"
REDUCER_ID = "ec58dc9ec399d719677c5ab98ab0ac2efe60d8138c4f2c829f3e5930a946dec2"
READY = {
    CANONICAL.name: "9864424def44034a5a5e9a68814ce111076182ad7ea898c9d0040d888c92f32b",
    REPLICA.name: "4f834364ebd9f39e02a4a1781180d79b95ededda3f8d6f6aaac0845bfb8d8a01",
}
OUTPUTS = {
    "campaign-functions.tsv": "eeb992ab962308b97834f314675521bb82064f50d37ca57f40ff6ad5c54a4534",
    "campaign-residuals.tsv": "b0611722b49bbebbb666bce2c51d534e30ac7ad561d43daa594f5c40fcfdb1c3",
    "campaign-questions.tsv": "49e3987f4bfa1996838d62823c2d8cc74f26e82843099fadbd055ef52cf4b40d",
    "campaign-scenarios.tsv": "35a84fad46065d1317e48b41c66889a1dd12327077766423693b8839be857542",
    "campaign-levers.tsv": "fa337d96cfe7b6eca266b44aa39deded516e3a8cc02979a31671b449c66e3cdc",
    "campaign-contracts.tsv": "7d5cefef1a6c18fdac8cbe9fa46ea119a6e6d47528f1a5743d9124c22c12a4f8",
    "campaign-adjudications.tsv": "de317f245b8c3c0e71002a82f73f2dbcc08284cee7c9cddd84c30e8777da7994",
    "campaign-supersessions.tsv": "7569852a3fe9aea25a4fcc4f6d17b6d9d81ff658f644b007bda1f50ae55559cb",
}
COUNTS = {
    "functions": 8124,
    "residuals": 6117,
    "questions": 15245,
    "scenarios": 72,
    "levers": 915,
    "contracts": 14241,
    "adjudications": 6092,
    "supersessions": 584,
}
PARENT_READY_SHA256 = "8436a5a99145f6910cd147bdb419a0efbfb071fcf16d8f42ec330182a97df63e"
PARENT_REDUCER_ID = "988e0660634b6fa59b2018a96545cdf84666e2c219c7a7ac89809c4ef99fac2e"
PARENT_AUTHORITY_SHA256 = "772f65ba5210c6d022bff64aefb6523a563ed1b8c3ab53eb87aef8dfe4b1944d"
PROOF_READY_SHA256 = "182d302e45ff42b389b54c85f92576864f9ef9dc30887ee5fc6db86b307faf7f"
PROOF_AUTHOR_SHA256 = "9fa0a7bce82f234991843aa0047d4f33aeeb9342cf9397887b87572eb3c5d55e"
PROOF_ID = "TD-489e2736dd47aa51"
ADJUDICATION_ID = "A-6c8984dc61c86b0d"


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
    require(
        not (getattr(stat, "st_file_attributes", 0) & 0x400),
        f"{label} is reparse-linked",
    )
    require(stat.st_nlink == 1, f"{label} has multiple hard links")


def validate_campaign(root: Path, expected_ready: str) -> dict:
    require(root.resolve() == root, f"campaign root is not canonical: {root}")
    ready_path = root / "campaign.ready.json"
    require_plain_single(ready_path, f"{root.name} READY")
    require(sha256(ready_path) == expected_ready, f"{root.name} READY differs")
    receipt = json.loads(ready_path.read_text(encoding="utf-8"))
    advance = receipt.get("advance", {})
    promotion = advance.get("promotion", {})
    require(receipt.get("generation") == 14, f"{root.name} generation differs")
    require(receipt.get("counts") == COUNTS, f"{root.name} counts differ")
    require(
        receipt.get("reducer", {}).get("id") == REDUCER_ID,
        f"{root.name} reducer differs",
    )
    require(
        advance.get("kind") == "STATIC_TOKENARCHIVE_READNEXTTOKEN_DISPATCH_TABLE_REPROOF"
        and advance.get("schema")
        == "bea.re.static-tokenarchive-readnexttoken-dispatch-table-reproof-advance.v1"
        and advance.get("branchId") == "incident-20260806-recovery-v1"
        and advance.get("proofId") == PROOF_ID,
        f"{root.name} advance identity differs",
    )
    require(
        promotion.get("adjudicationId") == ADJUDICATION_ID
        and promotion.get("entityKey")
        == "TEXT_RESIDUAL:74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750:0x004F5AC5-0x004F5B70"
        and promotion.get("classification") == "DATA"
        and promotion.get("terminalState") == "TERMINAL_DATA"
        and promotion.get("semanticPromotionApplied") is False
        and promotion.get("wholeBytes") == 171
        and promotion.get("dispatchPointerBytes") == 28
        and promotion.get("indexBytes") == 125
        and promotion.get("alignmentBytes") == 18,
        f"{root.name} promotion boundary differs",
    )
    for name, expected in OUTPUTS.items():
        path = root / name
        require_plain_single(path, f"{root.name} {name}")
        require(sha256(path) == expected, f"{root.name} output differs: {name}")
    manifest = receipt.get("reducer", {}).get("files")
    require(isinstance(manifest, list) and len(manifest) == 20, "reducer manifest differs")
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
    for name in (
        "PYTHONHOME",
        "PYTHONPATH",
        "PYTHONSTARTUP",
        "PYTHONINSPECT",
        "PYTHONUSERBASE",
    ):
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
        require(
            sha256(ROOT / "tools/re_tokenarchive_dispatch_reproof.py")
            == PROOF_AUTHOR_SHA256,
            "proof author differs",
        )
        canonical_verify = run_full(CANONICAL, READY[CANONICAL.name])
        replica_verify = run_full(REPLICA, READY[REPLICA.name])
        require(
            Path(__file__).resolve().read_bytes() == author_start,
            "authority author changed during execution",
        )
        receipt = {
            "schema": "bea.re.tokenarchive-dispatch-generation14-authority.v1",
            "verdict": "READY",
            "authorityClass": "FULL_REPLAY_CAMPAIGN_AUTHORITY",
            "replayScope": "FULL_CAMPAIGN_REDUCER_REPLAY_NOT_GAME_TTD_OR_GHIDRA_REPLAY",
            "completedAtUtc": datetime.now(timezone.utc).isoformat(),
            "lineageId": "incident-20260806-recovery-v1",
            "author": {
                "path": "tools/re_tokenarchive_dispatch_campaign_authority.py",
                "bytes": len(author_start),
                "sha256": hashlib.sha256(author_start).hexdigest(),
            },
            "canonical": {
                "absolutePath": str(CANONICAL),
                "ready": stamp(CANONICAL / "campaign.ready.json", relative_to=CANONICAL),
                "reducerId": REDUCER_ID,
                "generation": 14,
                "kind": "STATIC_TOKENARCHIVE_READNEXTTOKEN_DISPATCH_TABLE_REPROOF",
                "proofId": PROOF_ID,
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
                "schema": "bea.re.tokenarchive-readnexttoken-dispatch-table-reproof.v1",
            },
            "counts": COUNTS,
            "outputs": {
                name: {"bytes": (CANONICAL / name).stat().st_size, "sha256": digest}
                for name, digest in OUTPUTS.items()
            },
            "claimBoundary": {
                "functionRowsModified": 0,
                "residualRowsModified": 1,
                "contractRowsModified": 1,
                "questionsClosed": 1,
                "questionsAdded": 0,
                "nonsemanticAdjudicationsAdded": 1,
                "classification": "DATA",
                "terminalState": "TERMINAL_DATA",
                "wholeBytes": 171,
                "dispatchPointerBytes": 28,
                "indexBytes": 125,
                "alignmentBytes": 18,
                "pointerTargets": 7,
                "namesChanged": 0,
                "rangesChanged": 0,
                "rebuildState": "NOT_STARTED",
            },
            "determinism": {
                "allEightLedgersByteIdentical": True,
                "allTwentyReducerFilesByteIdentical": True,
                "normalizedReadyReceiptsEqual": True,
                "normalizedFields": ["generatedAtUtc", "outputs.*.lastWriteUtc"],
            },
            "verification": {
                "canonicalLiteralPinnedFullReplay": canonical_verify,
                "replicaLiteralPinnedFullReplay": replica_verify,
            },
            "frozenOwners": {
                "campaign": stamp(CANONICAL / "_reducer/tools/re_campaign.py", relative_to=ROOT),
                "proof": stamp(
                    CANONICAL / "_reducer/tools/re_tokenarchive_dispatch_reproof.py",
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
                    "generation-number selection",
                    "matching-ledger selection",
                    "self-derived READY or reducer pins",
                    "unpinned frozen-verifier success",
                    "integrity-only success",
                    "function, runtime-frequency, token-meaning, or rebuild claims",
                ],
            },
            "limitations": {
                "proofScope": "STATIC_PRISTINE_BYTES_PLUS_READ_ONLY_GHIDRA_CONSUMER_AND_XREF_GRAPH",
                "indexCategorySemantics": "UNASSIGNED_0_THROUGH_6",
                "gameRunOrCapture": False,
                "ttdReplay": False,
                "liveGhidraMutation": False,
                "rebuildState": "NOT_STARTED_NO_BEHAVIORAL_CONTRACT_CLAIM",
                "nextValidGeneration": 15,
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
            "TOKENARCHIVE_GEN14_AUTHORITY_READY "
            f"bytes={OUT.stat().st_size} sha256={sha256(OUT)} path={OUT}"
        )
        return 0
    except (AuthorityError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(f"TOKENARCHIVE_GEN14_AUTHORITY_REFUSED: {exc}", file=sys.stderr)
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
