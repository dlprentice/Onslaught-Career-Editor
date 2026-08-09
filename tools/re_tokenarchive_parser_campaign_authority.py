#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Select the literal-pinned canonical Generation 18 TokenArchive campaign."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "local-lab/re-campaign-incident-recovery-20260808-v1"
CANONICAL = BASE / "generation-18-tokenarchive-parser-contract-v1"
REPLICA = BASE / "generation-18-tokenarchive-parser-contract-replica-v1"
PARENT = BASE / "generation-17-lockhit-bounded-contract-v1"
PARENT_AUTHORITY = BASE / "generation-17-lockhit-bounded-contract-authority.ready.json"
PROOF = ROOT / "local-lab/tokenarchive-parser-contract-reproof-20260809-v7"
OUT = BASE / "generation-18-tokenarchive-parser-contract-authority.ready.json"

REDUCER_ID = "ee8bddfb4cf6f05f768d9e067ea1330753eecbb3f7eb97553dfe6fa4da8bad74"
READY = {
    CANONICAL.name: "4ae3a7b8dc4baa7cb83125fc8005503499b083fd1944f19bdfb84755f663d97e",
    REPLICA.name: "9267333dc7492e3ffa36cd4dbb771797046dfdbf1782a451b1e8853022efb4d1",
}
OUTPUTS = {
    "campaign-functions.tsv": "cfaf73803c360285ecedfda29e7a89c8119d05bbf2d047e124522dedc9256454",
    "campaign-residuals.tsv": "6aaa5da3917079de3a172fb24b7de2b3ba99f1bc05ad40c4c427fcaa76d55ab6",
    "campaign-questions.tsv": "1b0609bada6a4595b8420f15ec3bd4d5c743d79100fa8012bd26cb9be15b3a56",
    "campaign-scenarios.tsv": "35a84fad46065d1317e48b41c66889a1dd12327077766423693b8839be857542",
    "campaign-levers.tsv": "fa337d96cfe7b6eca266b44aa39deded516e3a8cc02979a31671b449c66e3cdc",
    "campaign-contracts.tsv": "f9a7674757ad85fc7ec8fa3d5dbff1b933b0f950b5b6c323ffe088d3a137752c",
    "campaign-adjudications.tsv": "70a957db451bea6653020cb9829416b363a2f541a357bf6682a12cbc122b7bab",
    "campaign-supersessions.tsv": "4da539b16248ae9f5abfe5aa61845d9ec96351605060b8b05f16abb7353b008e",
}
COUNTS = {
    "functions": 8125,
    "residuals": 6118,
    "questions": 15254,
    "scenarios": 72,
    "levers": 915,
    "contracts": 14243,
    "adjudications": 6097,
    "supersessions": 588,
}
PARENT_READY_SHA256 = "6d794905d6fc5daea11f99b781cf8eb7740765e749c784d02507d43436b801a2"
PARENT_REDUCER_ID = "fbb343d629fa12a641aced04db88b59e5270e1f45990d9d203284302f8761621"
PARENT_AUTHORITY_SHA256 = "c37aae056dc2f04d946db69d4e13d276dbc11d1a52976c97657af0a5549b00cb"
PROOF_READY_SHA256 = "ed2aca4f54a82476a9f1cc1cb7e1a81376fae9b9c6dee22fcf890fe15fbf07bc"
PROOF_AUTHOR_SHA256 = "b94a2216233fbd0623a14df8e27cbb4d1b66d978da43f8744b0e479d7e9c8ee1"
PROOF_OUTPUTS = {
    "tokens.tsv": (20309, "cf9a77aea8df2e375361750657ce16f7b3d10df5f6ea0a6a26e15e4c9d14cc6d"),
    "writer-calls.tsv": (18016, "00ff838d301ae36f81fca93280c2b988c89ed84c49b435b933dc67750e756579"),
    "descriptor-loaders.tsv": (8208, "cf9ea88b76d7a3e1a8f91f22bb9f41e4605055642dd855679bd2599cfefea4fc"),
    "readnexttoken-contract.json": (3480, "51fc9479fccf9f09a71e7baf7a76d48e8d5ccf18ac07fa8447629edbb5d3c641"),
}
REBUILD_FILES = {
    "owner": (
        ROOT / "rebuild/OnslaughtRebuild.Client/ParticleSetFile.cs",
        23400,
        "9f798cf3e489b26ae8bc3caaedd6fd87ddf8aea8b149200f4b2ce7848aa8ea8d",
    ),
    "resolver": (
        ROOT / "rebuild/OnslaughtRebuild.Client/ParticleEffectResolver.cs",
        29245,
        "623903cc81af90b185e7ee628315723832e71711adec3d0c26393013723022dc",
    ),
    "test": (
        ROOT / "rebuild/OnslaughtRebuild.Client.Tests/ParticleSetTests.cs",
        29191,
        "f2c5e308dda9b7ef73c42068e645a8a7d592f9315611558544329b3a8fee6728",
    ),
}
OBSERVATION_ID = "TPC-c23c8c9e0fdbe42c"
ADJUDICATION_ID = "A-a6a3bc60970e8e72"
FUNCTION_ENTITY = (
    "CODE:74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750:"
    "VA=0x004f57b0:RANGES=bedc826d01b6a8a1792de76da45537e1b3f6f663051efecc30414377d0efe76b"
)
CONTRACT_ID = "C-a1dd659dcb7d74c1"
PARENT_QUESTION = "Q-f40657bf78b29abb"
SUCCESSOR_QUESTION = "Q-439e6a926003084e"


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
    require(path.resolve(strict=True) == path, f"{label} has a linked ancestor")
    info = path.lstat()
    require(not path.is_symlink(), f"{label} is symlinked")
    require(
        not (getattr(info, "st_file_attributes", 0) & 0x400),
        f"{label} is reparse-linked",
    )
    require(info.st_nlink == 1, f"{label} has multiple hard links")


def validate_campaign(root: Path, expected_ready: str) -> dict:
    require(root.resolve() == root, f"campaign root is not canonical: {root}")
    root_info = root.lstat()
    require(
        not root.is_symlink()
        and not (getattr(root_info, "st_file_attributes", 0) & 0x400),
        f"campaign root is linked: {root}",
    )
    ready_path = root / "campaign.ready.json"
    require_plain_single(ready_path, f"{root.name} READY")
    require(sha256(ready_path) == expected_ready, f"{root.name} READY differs")
    receipt = json.loads(ready_path.read_text(encoding="utf-8"))
    advance = receipt.get("advance", {})
    promotion = advance.get("promotion", {})
    proof = advance.get("proof", {})
    mapping = advance.get("rebuildMapping", {})
    require(receipt.get("generation") == 18, f"{root.name} generation differs")
    require(receipt.get("counts") == COUNTS, f"{root.name} counts differ")
    require(
        receipt.get("reducer", {}).get("id") == REDUCER_ID,
        f"{root.name} reducer differs",
    )
    require(
        advance.get("kind") == "STATIC_TOKENARCHIVE_READNEXTTOKEN_PARSER_CONTRACT"
        and advance.get("schema")
        == "bea.re.static-tokenarchive-readnexttoken-parser-contract-advance.v1"
        and advance.get("branchId") == "incident-20260806-recovery-v1"
        and advance.get("observationId") == OBSERVATION_ID
        and advance.get("verdict") == "SURVIVED",
        f"{root.name} advance identity differs",
    )
    require(
        promotion.get("entityKey") == FUNCTION_ENTITY
        and promotion.get("contractId") == CONTRACT_ID
        and promotion.get("parentQuestionId") == PARENT_QUESTION
        and promotion.get("successorQuestionId") == SUCCESSOR_QUESTION
        and promotion.get("adjudicationId") == ADJUDICATION_ID
        and promotion.get("gradeFrom") == "C0_OPAQUE"
        and promotion.get("gradeTo") == "C1_CANDIDATE_PARTIAL",
        f"{root.name} parser promotion differs",
    )
    require(
        advance.get("questionsClosed") == 1
        and advance.get("questionsAdded") == 1
        and advance.get("adjudicationsAdded") == 1
        and advance.get("runtimeReplaysProved") == 0
        and advance.get("retailTokenIds") == 124
        and advance.get("shippedCorpusLinesValidated") == 27186
        and advance.get("writerCallsValidated") == 141
        and advance.get("descriptorFactoryRttiMappingsDerived") == 13
        and advance.get("descriptorLoaderSwitchCorroborationsValidated") == 13
        and advance.get("retailDefectsProved") == 1
        and mapping.get("contractId") == CONTRACT_ID
        and mapping.get("state") == "PARTIAL_CONTRACT"
        and mapping.get("owner")
        == "rebuild/OnslaughtRebuild.Client/ParticleSetFile.cs",
        f"{root.name} bounded static claim differs",
    )
    require(
        proof.get("root") == "local-lab/tokenarchive-parser-contract-reproof-20260809-v7"
        and proof.get("schema") == "bea.re.tokenarchive-parser-contract-reproof.v7"
        and proof.get("ready", {}).get("sha256") == PROOF_READY_SHA256
        and proof.get("author", {}).get("sha256") == PROOF_AUTHOR_SHA256
        and {
            name: (row.get("bytes"), row.get("sha256"))
            for name, row in proof.get("outputs", {}).items()
        }
        == PROOF_OUTPUTS
        and advance.get("liveGhidraDisposition")
        == "READ_ONLY_EXACT_POST_BACKUP_DECOMPILE_NO_LIVE_MUTATION",
        f"{root.name} proof or Ghidra disposition differs",
    )
    receipt_outputs = receipt.get("outputs", {})
    require(set(receipt_outputs) == set(OUTPUTS), f"{root.name} output set differs")
    for name, expected in OUTPUTS.items():
        path = root / name
        require_plain_single(path, f"{root.name} {name}")
        require(
            sha256(path) == expected
            and receipt_outputs[name].get("path") == name
            and receipt_outputs[name].get("bytes") == path.stat().st_size
            and receipt_outputs[name].get("sha256") == expected,
            f"{root.name} output differs: {name}",
        )
    manifest = receipt.get("reducer", {}).get("files")
    require(isinstance(manifest, list) and len(manifest) == 33, "reducer manifest differs")
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


def run_checked(
    argv: list[str],
    marker: str,
    *,
    timeout: int,
    exact_test_census: tuple[int, int, int, int] | None = None,
) -> dict[str, object]:
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
    result: dict[str, object] = {
        "command": argv,
        "exitCode": completed.returncode,
        "marker": marker,
        "elapsedSeconds": round(time.monotonic() - started, 3),
    }
    if exact_test_census is not None:
        match = re.search(
            r"Failed:\s*(\d+),\s*Passed:\s*(\d+),\s*Skipped:\s*(\d+),\s*Total:\s*(\d+)",
            completed.stdout,
        )
        require(match is not None, "focused rebuild test census is absent")
        actual = tuple(int(value) for value in match.groups())
        require(actual == exact_test_census, "focused rebuild test census differs")
        result["testCensus"] = {
            "failed": actual[0],
            "passed": actual[1],
            "skipped": actual[2],
            "total": actual[3],
        }
    return result


def run_full(root: Path, expected_ready: str) -> dict[str, object]:
    bootstrap = ROOT / "tools/re_campaign_frozen_bootstrap.py"
    require_plain_single(bootstrap, "trusted frozen bootstrap")
    require(
        bootstrap.stat().st_size == 17831
        and sha256(bootstrap)
        == "98b453b84bb4d312691f38e59a3a662d990963f3fdfac28f7e72ea1c1376562b",
        "trusted frozen bootstrap identity differs",
    )
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
            require(
                not os.path.samefile(CANONICAL / name, REPLICA / name),
                f"replica ledger aliases canonical: {name}",
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
        for name, (size, digest) in PROOF_OUTPUTS.items():
            require(
                (PROOF / name).stat().st_size == size and sha256(PROOF / name) == digest,
                f"proof output differs: {name}",
            )
        for label, (path, size, digest) in REBUILD_FILES.items():
            require_plain_single(path, f"rebuild {label}")
            require(
                path.stat().st_size == size and sha256(path) == digest,
                f"rebuild {label} differs",
            )

        frozen_proof = CANONICAL / "_reducer/tools/re_tokenarchive_parser_contract.py"
        live_proof = ROOT / "tools/re_tokenarchive_parser_contract.py"
        require(
            frozen_proof.stat().st_size == 63516
            and sha256(frozen_proof) == PROOF_AUTHOR_SHA256,
            "frozen proof owner differs",
        )
        require_plain_single(live_proof, "exact live proof owner")
        require(
            live_proof.stat().st_size == 63516
            and sha256(live_proof) == PROOF_AUTHOR_SHA256,
            "live proof owner differs",
        )
        proof_verify = run_checked(
            [sys.executable, "-I", "-B", str(live_proof), "verify"],
            "TOKENARCHIVE_PARSER_CONTRACT_VERIFIED",
            timeout=300,
        )
        proof_selftest = run_checked(
            [sys.executable, "-I", "-B", str(frozen_proof), "selftest"],
            "TOKENARCHIVE_PARSER_CONTRACT_SELFTEST_OK",
            timeout=300,
        )
        rebuild_filter = (
            "FullyQualifiedName~ParticleSetTests.RetailTokenTableCoversEveryShippedKeyExactly|"
            "FullyQualifiedName~ParticleSetTests.VelocityRandomnessPinsTheMaskedRetailReaderDefect|"
            "FullyQualifiedName~ParticleSetTests.RetailDescriptorFactoryCoversAllThirteenTypes"
        )
        rebuild_verify = run_checked(
            [
                "dotnet",
                "test",
                str(ROOT / "rebuild/OnslaughtRebuild.Client.Tests/OnslaughtRebuild.Client.Tests.csproj"),
                "--no-restore",
                "--filter",
                rebuild_filter,
            ],
            "Passed!",
            timeout=300,
            exact_test_census=(0, 3, 0, 3),
        )
        canonical_verify = run_full(CANONICAL, READY[CANONICAL.name])
        replica_verify = run_full(REPLICA, READY[REPLICA.name])

        # The two full replays take several minutes. Rebind every selected byte
        # immediately before publication so none of the earlier evidence can
        # drift while the other copy is replaying.
        canonical_final = validate_campaign(CANONICAL, READY[CANONICAL.name])
        replica_final = validate_campaign(REPLICA, READY[REPLICA.name])
        for name in OUTPUTS:
            require(
                (CANONICAL / name).read_bytes() == (REPLICA / name).read_bytes(),
                f"final replica ledger differs: {name}",
            )
        require(
            {
                path.relative_to(CANONICAL / "_reducer").as_posix(): path.read_bytes()
                for path in (CANONICAL / "_reducer").rglob("*")
                if path.is_file()
            }
            == {
                path.relative_to(REPLICA / "_reducer").as_posix(): path.read_bytes()
                for path in (REPLICA / "_reducer").rglob("*")
                if path.is_file()
            },
            "final replica reducer differs",
        )
        final_normalized = []
        for source in (canonical_final, replica_final):
            value = json.loads(json.dumps(source))
            value.pop("generatedAtUtc")
            for output in value["outputs"].values():
                output.pop("lastWriteUtc")
            final_normalized.append(value)
        require(
            final_normalized[0] == final_normalized[1],
            "final normalized READY receipts differ",
        )
        for path, label in (
            (PARENT / "campaign.ready.json", "final parent READY"),
            (PARENT_AUTHORITY, "final parent authority"),
            (PROOF / "proof.ready.json", "final proof READY"),
        ):
            require_plain_single(path, label)
        require(
            sha256(PARENT / "campaign.ready.json") == PARENT_READY_SHA256
            and sha256(PARENT_AUTHORITY) == PARENT_AUTHORITY_SHA256
            and sha256(PROOF / "proof.ready.json") == PROOF_READY_SHA256,
            "final parent or proof identity differs",
        )
        for name, (size, digest) in PROOF_OUTPUTS.items():
            require_plain_single(PROOF / name, f"final proof output {name}")
            require(
                (PROOF / name).stat().st_size == size
                and sha256(PROOF / name) == digest,
                f"final proof output differs: {name}",
            )
        for label, (path, size, digest) in REBUILD_FILES.items():
            require_plain_single(path, f"final rebuild {label}")
            require(
                path.stat().st_size == size and sha256(path) == digest,
                f"final rebuild {label} differs",
            )
        bootstrap = ROOT / "tools/re_campaign_frozen_bootstrap.py"
        require_plain_single(bootstrap, "final frozen bootstrap")
        require_plain_single(live_proof, "final live proof owner")
        require(
            bootstrap.stat().st_size == 17831
            and sha256(bootstrap)
            == "98b453b84bb4d312691f38e59a3a662d990963f3fdfac28f7e72ea1c1376562b"
            and live_proof.stat().st_size == 63516
            and sha256(live_proof) == PROOF_AUTHOR_SHA256,
            "final launcher or proof owner differs",
        )
        require(
            Path(__file__).resolve().read_bytes() == author_start,
            "authority author changed during execution",
        )

        receipt = {
            "schema": "bea.re.tokenarchive-parser-generation18-authority.v1",
            "verdict": "READY",
            "authorityClass": "FULL_REPLAY_CAMPAIGN_AUTHORITY",
            "replayScope": "FULL_CAMPAIGN_REDUCER_REPLAY_NOT_GAME_TTD_OR_GHIDRA_REPLAY",
            "completedAtUtc": datetime.now(timezone.utc).isoformat(),
            "lineageId": "incident-20260806-recovery-v1",
            "author": {
                "path": "tools/re_tokenarchive_parser_campaign_authority.py",
                "bytes": len(author_start),
                "sha256": hashlib.sha256(author_start).hexdigest(),
            },
            "canonical": {
                "absolutePath": str(CANONICAL),
                "ready": stamp(CANONICAL / "campaign.ready.json", relative_to=CANONICAL),
                "reducerId": REDUCER_ID,
                "generation": 18,
                "kind": "STATIC_TOKENARCHIVE_READNEXTTOKEN_PARSER_CONTRACT",
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
                "schema": "bea.re.tokenarchive-parser-contract-reproof.v7",
                "claim": "CTOKENARCHIVE_READNEXTTOKEN_STATIC_CONTRACT_AND_PARTICLE_CORPUS_CROSSWALK",
                "outputs": {
                    name: {"bytes": size, "sha256": digest}
                    for name, (size, digest) in PROOF_OUTPUTS.items()
                },
            },
            "rebuild": {
                "state": "PARTIAL_CONTRACT",
                "owner": "rebuild/OnslaughtRebuild.Client/ParticleSetFile.cs",
                "resolver": "rebuild/OnslaughtRebuild.Client/ParticleEffectResolver.cs",
                "tests": "rebuild/OnslaughtRebuild.Client.Tests/ParticleSetTests.cs",
                "focusedParity": rebuild_verify,
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
                "successorQuestionAdded": SUCCESSOR_QUESTION,
                "adjudicationId": ADJUDICATION_ID,
                "staticProofGrade": "C1_STATIC",
                "campaignSemanticGrade": "C1_CANDIDATE_PARTIAL",
                "admissionAdjudicationVerdict": "SURVIVED",
                "contractRefuterVerdict": "UNSCORED",
                "runtimeVerdict": "UNSCORED",
                "runtimeReplays": 0,
                "retailTokenNames": 124,
                "parseIndexEntries": 125,
                "staticallyEncodedDirectWriterCalls": 141,
                "descriptorFactoryRttiMappings": 13,
                "loaderSwitchCorroborations": 13,
                "shippedCorpusLines": 27186,
                "token32StaticAsymmetry": True,
                "shippedCorpusMasksToken32Asymmetry": True,
                "liveGhidraMutation": False,
                "executableBytesChanged": 0,
                "rebuildState": "PARTIAL_CONTRACT",
            },
            "determinism": {
                "allEightLedgersByteIdentical": True,
                "allThirtyThreeReducerFilesByteIdentical": True,
                "normalizedReadyReceiptsEqual": True,
                "normalizedFields": ["generatedAtUtc", "outputs.*.lastWriteUtc"],
            },
            "verification": {
                "exactStaticProof": proof_verify,
                "frozenStaticProofSelftest": proof_selftest,
                "canonicalLiteralPinnedFullReplay": canonical_verify,
                "replicaLiteralPinnedFullReplay": replica_verify,
            },
            "frozenOwners": {
                "campaign": stamp(CANONICAL / "_reducer/tools/re_campaign.py", relative_to=ROOT),
                "proof": stamp(frozen_proof, relative_to=ROOT),
                "ghidraDecompileTool": stamp(
                    CANONICAL / "_reducer/tools/ExportFunctionsByAddressDecompile.java",
                    relative_to=ROOT,
                ),
                "rebuildOwner": stamp(
                    CANONICAL / "_reducer/rebuild/OnslaughtRebuild.Client/ParticleSetFile.cs",
                    relative_to=ROOT,
                ),
                "rebuildResolver": stamp(
                    CANONICAL / "_reducer/rebuild/OnslaughtRebuild.Client/ParticleEffectResolver.cs",
                    relative_to=ROOT,
                ),
                "rebuildTest": stamp(
                    CANONICAL / "_reducer/rebuild/OnslaughtRebuild.Client.Tests/ParticleSetTests.cs",
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
                    "runtime, complete-malformed-input, allocation, overflow, downstream-particle, or rebuild-complete overclaims",
                ],
            },
            "limitations": {
                "proofScope": "SPECIMEN_BOUND_STATIC_PARSER_WRITER_FACTORY_RTTI_AND_SHIPPED_CORPUS",
                "runtimeFrequency": "OPEN",
                "namedToken32ModifierOutcome": "OPEN",
                "malformedInputCausality": "OPEN",
                "allocationFailureBehavior": "OPEN",
                "pendingReferenceOverflow": "OPEN",
                "fullDownstreamParticleBehavior": "OPEN",
                "liveGhidraMutation": False,
                "rebuildState": "PARTIAL_CONTRACT",
                "nextValidGeneration": 19,
            },
        }
        require(
            Path(__file__).resolve().read_bytes() == author_start,
            "authority author changed before publication",
        )
        OUT.parent.mkdir(parents=True, exist_ok=True)
        partial = OUT.with_name(OUT.name + ".partial")
        require(not OUT.exists(), f"authority receipt appeared during execution: {OUT}")
        require(not partial.exists(), f"stale partial receipt exists: {partial}")
        with partial.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(receipt, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(partial, OUT)
        print(
            "TOKENARCHIVE_GEN18_AUTHORITY_READY "
            f"bytes={OUT.stat().st_size} sha256={sha256(OUT)} path={OUT}"
        )
        return 0
    except (
        AuthorityError,
        OSError,
        subprocess.SubprocessError,
        json.JSONDecodeError,
    ) as exc:
        print(f"TOKENARCHIVE_GEN18_AUTHORITY_REFUSED: {exc}", file=sys.stderr)
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
