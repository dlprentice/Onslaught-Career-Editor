#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Select the literal-pinned canonical Generation 19 UnsetObjective campaign."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "local-lab/re-campaign-incident-recovery-20260808-v1"
CANONICAL = BASE / "generation-19-mission-native-unsetobjective-reproof-v1"
REPLICA = BASE / "generation-19-mission-native-unsetobjective-reproof-replica-v1"
PARENT = BASE / "generation-18-tokenarchive-parser-contract-v1"
PARENT_AUTHORITY_PATH = BASE / "generation-18-tokenarchive-parser-contract-authority.ready.json"
PROOF = ROOT / "local-lab/mission-native-unsetobjective-boundary-reproof-20260809-v1"
OUT = BASE / "generation-19-mission-native-unsetobjective-reproof-authority.ready.json"

REDUCER_ID = "151acbe5c1571dca2c53c68dd79281cf20c69af609523d54f25953643dcff3e2"
READY = {
    CANONICAL.name: "f83dbb6eddaa16deed5f2a2460d393dc4525a63ae243b6cac0c656056b69ab9a",
    REPLICA.name: "df7cd19864d98a23687b33d0e148346b68e9a78191eebdd3b103ab04e0e0f214",
}
OUTPUTS = {
    "campaign-functions.tsv": (5132061, "df6c815c498b9eb025bb76fe90da943f84b7a83621901ea0398e9a1fc46779d1"),
    "campaign-residuals.tsv": (2865672, "f24a5f1d8a16fd5857d2801848af6fc59820a7590e5056b01efb8fdedd9528b9"),
    "campaign-questions.tsv": (8371625, "8f33b0de1c1f77724f75e39987e6d27e6028e63f872aed5107de67bffe8b4727"),
    "campaign-scenarios.tsv": (31860, "35a84fad46065d1317e48b41c66889a1dd12327077766423693b8839be857542"),
    "campaign-levers.tsv": (329226, "fa337d96cfe7b6eca266b44aa39deded516e3a8cc02979a31671b449c66e3cdc"),
    "campaign-contracts.tsv": (10932955, "2071c33a4d4e87e97a6695c53cc1982653d345a9a64d4c526ac61bd7fcd1b54a"),
    "campaign-adjudications.tsv": (3334135, "bfe26e695ecae93e18bea8749ef7438026002299b552be0587be6cecb6d24055"),
    "campaign-supersessions.tsv": (462797, "87d58f2344ade1589a34360cdb21345fa3b2edc4965c6d41e1267df3c718eab4"),
}
COUNTS = {
    "functions": 8126,
    "residuals": 6119,
    "questions": 15255,
    "scenarios": 72,
    "levers": 915,
    "contracts": 14245,
    "adjudications": 6099,
    "supersessions": 592,
}
PARENT_READY = (22974, "4ae3a7b8dc4baa7cb83125fc8005503499b083fd1944f19bdfb84755f663d97e")
PARENT_REDUCER_ID = "ee8bddfb4cf6f05f768d9e067ea1330753eecbb3f7eb97553dfe6fa4da8bad74"
PARENT_AUTHORITY_STAMP = (12742, "c13dcef4aaae7c95b08bd75a502069a47274e9d577b48b05c57a5f3adcf6b7a6")
PROOF_READY = (16268, "c6ae222d26b37863ae575b5af32ddf1a64d8660cb45adb60965610704ec37858")
PROOF_AUTHOR = (52888, "1d67823b54c465986b8b2e83ea9e1b278eef2e5dd91e509404399c21eba456fb")
BOOTSTRAP = (17831, "98b453b84bb4d312691f38e59a3a662d990963f3fdfac28f7e72ea1c1376562b")
REBUILD_FILES = {
    "registry": (
        ROOT / "rebuild/OnslaughtRebuild.Core/Level100ActorRegistry.cs",
        63729,
        "d322e8eb970b148cee2a7635ee420631726f50f0a8655afa491fe0284e13a385",
    ),
    "runtime": (
        ROOT / "rebuild/OnslaughtRebuild.Core/Level100ActorScriptRuntime.cs",
        55385,
        "157a95bb6bc4802702adcd74422c09765710563d1e50785bfd2074882c6371ae",
    ),
    "test": (
        ROOT / "rebuild/OnslaughtRebuild.Core.Tests/Level100MissionTests.cs",
        27944,
        "4315e6c96ebdc6c2d27e5e19d91a47c5af4d6d190a135a2051b20132c401f95a",
    ),
}
ADVANCE_KIND = "MISSION_NATIVE_UNSETOBJECTIVE_BOUNDARY_AND_STATIC_CONTRACT_REPROOF"
ADVANCE_SCHEMA = "bea.re.mission-native-unsetobjective-boundary-static-contract-reproof-advance.v1"
PROMOTION_ID = "UO-f5de853bbde17f5c"
FUNCTION_ENTITY = (
    "CODE:74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750:"
    "VA=0x00535ee0:RANGES=4a4cca6c22bcdfb84d88f4fc67200da6ab7e629759e0006593d75459f04c056d"
)
FUNCTION_CONTRACT = "C-7c57eb48898953d7"
OLD_RESIDUAL = (
    "TEXT_RESIDUAL:74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750:"
    "0x00535EDD-0x00535EF0"
)
PADDING_ENTITIES = [
    "TEXT_RESIDUAL:74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750:0x00535EDD-0x00535EE0",
    "TEXT_RESIDUAL:74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750:0x00535EED-0x00535EF0",
]
QUESTIONS_CLOSED = ["Q-b27b396c572d0aa2", "Q-0de52a13680b6c1d"]
QUESTION_OPENED = "Q-bcd5a5ae82cbaff7"
ADJUDICATIONS = ["A-3a5cac8bc4391299", "A-d88a8c2edca8efd9"]
SUPERSESSIONS = [
    "S-99aa8cdb6c9a69df",
    "S-80acc9905a069d0e",
    "S-3333cf315afdead7",
    "S-1f813c3a89bb9418",
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


def strict_json(path: Path) -> dict:
    def pairs(rows: list[tuple[str, object]]) -> dict[str, object]:
        value: dict[str, object] = {}
        for key, item in rows:
            require(key not in value, f"duplicate JSON key in {path}: {key}")
            value[key] = item
        return value

    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)
    require(isinstance(value, dict), f"JSON root is not an object: {path}")
    return value


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


def require_stamp(path: Path, expected: tuple[int, str], label: str) -> None:
    require_plain_single(path, label)
    require(
        path.stat().st_size == expected[0] and sha256(path) == expected[1],
        f"{label} identity differs",
    )


def stamp(path: Path, *, relative_to: Path | None = None) -> dict[str, object]:
    require_plain_single(path, str(path))
    name = (
        path.relative_to(relative_to).as_posix()
        if relative_to is not None
        else str(path)
    )
    return {"path": name, "bytes": path.stat().st_size, "sha256": sha256(path)}


def validate_campaign(root: Path, expected_ready: str) -> dict:
    require(root.resolve(strict=True) == root, f"campaign root aliases: {root}")
    info = root.lstat()
    require(
        not root.is_symlink() and not (getattr(info, "st_file_attributes", 0) & 0x400),
        f"campaign root is linked: {root}",
    )
    ready_path = root / "campaign.ready.json"
    require_plain_single(ready_path, f"{root.name} READY")
    require(sha256(ready_path) == expected_ready, f"{root.name} READY differs")
    receipt = strict_json(ready_path)
    advance = receipt.get("advance", {})
    require(receipt.get("generation") == 19, f"{root.name} generation differs")
    require(receipt.get("counts") == COUNTS, f"{root.name} counts differ")
    require(
        receipt.get("reducer", {}).get("id") == REDUCER_ID,
        f"{root.name} reducer differs",
    )
    require(
        advance.get("kind") == ADVANCE_KIND
        and advance.get("schema") == ADVANCE_SCHEMA
        and advance.get("branchId") == "incident-20260806-recovery-v1"
        and advance.get("promotionId") == PROMOTION_ID
        and advance.get("verdict") == "SURVIVED",
        f"{root.name} advance identity differs",
    )
    proof = advance.get("proof", {})
    function = advance.get("function", {})
    partition = advance.get("partition", {})
    delta = advance.get("delta", {})
    mapping = advance.get("rebuildMapping", {})
    require(
        proof.get("root") == "local-lab/mission-native-unsetobjective-boundary-reproof-20260809-v1"
        and proof.get("schema") == "bea.re.mission-native-unsetobjective-boundary-reproof.v1"
        and proof.get("ready", {}).get("sha256") == PROOF_READY[1]
        and proof.get("author", {}).get("sha256") == PROOF_AUTHOR[1],
        f"{root.name} proof differs",
    )
    require(
        partition.get("parentBytes") == 19
        and partition.get("functionBytes") == 13
        and partition.get("paddingBytes") == 6
        and [row.get("kind") for row in partition.get("children", [])]
        == ["PADDING", "FUNCTION", "PADDING"],
        f"{root.name} partition differs",
    )
    require(
        function.get("entityKey") == FUNCTION_ENTITY
        and function.get("contractId") == FUNCTION_CONTRACT
        and function.get("name") == "IScript__UnsetObjective"
        and function.get("bodyBytes") == 13
        and function.get("instructionCount") == 4
        and function.get("bodySha256")
        == "0ec7dfff6ad0dba017b45b0a9840f6b587b899e88aaedb29d1d0eabfb842b35f"
        and function.get("semanticGrade") == "C1_CANDIDATE_PARTIAL"
        and function.get("semanticGradeCeiling") == "C1_STATIC"
        and function.get("runtimeVerdict") == "UNSCORED"
        and function.get("semanticPromotionApplied") is False,
        f"{root.name} function boundary differs",
    )
    require(
        delta.get("residualEntityRemoved") == OLD_RESIDUAL
        and delta.get("residualEntitiesAdded") == PADDING_ENTITIES
        and delta.get("adjudicationIdsAdded") == ADJUDICATIONS
        and delta.get("supersessionIdsAdded") == SUPERSESSIONS
        and delta.get("liveGhidraMutation") is False
        and delta.get("executableBytesChanged") == 0
        and advance.get("questions", {}).get("closed") == QUESTIONS_CLOSED
        and advance.get("questions", {}).get("opened") == [QUESTION_OPENED]
        and advance.get("runtimeReplaysProved") == 0,
        f"{root.name} exact delta differs",
    )
    require(
        mapping.get("contractId") == FUNCTION_CONTRACT
        and mapping.get("state") == "PARTIAL_CONTRACT"
        and mapping.get("owner")
        == "rebuild/OnslaughtRebuild.Core/Level100ActorScriptRuntime.cs"
        and advance.get("liveGhidraDisposition")
        == "SEPARATE_BACKED_UP_PROMOTION_PENDING_NO_LIVE_MUTATION_IN_GENERATION19",
        f"{root.name} rebuild/Ghidra boundary differs",
    )
    receipt_outputs = receipt.get("outputs", {})
    require(set(receipt_outputs) == set(OUTPUTS), f"{root.name} output set differs")
    for name, expected in OUTPUTS.items():
        path = root / name
        require_stamp(path, expected, f"{root.name} {name}")
        require(
            receipt_outputs[name].get("path") == name
            and receipt_outputs[name].get("bytes") == expected[0]
            and receipt_outputs[name].get("sha256") == expected[1],
            f"{root.name} output receipt differs: {name}",
        )
    manifest = receipt.get("reducer", {}).get("files")
    require(isinstance(manifest, list) and len(manifest) == 39, "reducer manifest differs")
    expected_paths = {str(row.get("path")) for row in manifest}
    actual_paths = {
        path.relative_to(root).as_posix()
        for path in (root / "_reducer").rglob("*")
        if path.is_file()
    }
    require(actual_paths == expected_paths, f"{root.name} reducer file set differs")
    for path in (root / "_reducer").rglob("*"):
        require(
            path.resolve(strict=True) == path,
            f"{root.name} reducer entry has a linked ancestor: {path}",
        )
        entry = path.lstat()
        require(
            not path.is_symlink()
            and not (getattr(entry, "st_file_attributes", 0) & 0x400),
            f"{root.name} reducer entry is linked: {path}",
        )
    for row in manifest:
        path = root / row["path"]
        require_stamp(
            path,
            (int(row["bytes"]), str(row["sha256"])),
            f"{root.name} reducer {row['path']}",
        )
    return receipt


def clean_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment["BEA_REPO_ROOT"] = str(ROOT)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    for name in ("PYTHONHOME", "PYTHONPATH", "PYTHONSTARTUP", "PYTHONINSPECT", "PYTHONUSERBASE"):
        environment.pop(name, None)
    return environment


def run_checked(
    argv: list[str], marker: str, *, timeout: int, census: tuple[int, int, int, int] | None = None
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
        f"command failed: {argv}: {completed.stderr[-1200:]}",
    )
    result: dict[str, object] = {
        "command": argv,
        "exitCode": completed.returncode,
        "marker": marker,
        "elapsedSeconds": round(time.monotonic() - started, 3),
    }
    if census is not None:
        match = re.search(
            r"Failed:\s*(\d+),\s*Passed:\s*(\d+),\s*Skipped:\s*(\d+),\s*Total:\s*(\d+)",
            completed.stdout,
        )
        require(match is not None, "focused rebuild test census is absent")
        actual = tuple(int(value) for value in match.groups())
        require(actual == census, f"focused rebuild census differs: {actual}")
        result["testCensus"] = {
            "failed": actual[0], "passed": actual[1], "skipped": actual[2], "total": actual[3]
        }
    return result


def run_full(root: Path, expected_ready: str) -> dict[str, object]:
    bootstrap = ROOT / "tools/re_campaign_frozen_bootstrap.py"
    require_stamp(bootstrap, BOOTSTRAP, "trusted frozen bootstrap")
    result = run_checked(
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
        timeout=1500,
    )
    require_stamp(bootstrap, BOOTSTRAP, "trusted frozen bootstrap after replay")
    return result


def normalized(receipt: dict) -> dict:
    value = json.loads(json.dumps(receipt))
    value.pop("generatedAtUtc")
    for output in value["outputs"].values():
        output.pop("lastWriteUtc")
    return value


def validate_pair() -> tuple[dict, dict]:
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
    reducer = lambda root: {
        path.relative_to(root / "_reducer").as_posix(): path.read_bytes()
        for path in (root / "_reducer").rglob("*")
        if path.is_file()
    }
    require(reducer(CANONICAL) == reducer(REPLICA), "replica reducer differs")
    require(normalized(canonical) == normalized(replica), "normalized READY differs")
    return canonical, replica


def validate_proof_inputs() -> None:
    proof_ready = strict_json(PROOF / "proof.ready.json")
    inputs = proof_ready.get("inputs")
    require(isinstance(inputs, dict) and len(inputs) == 26, "proof input set differs")
    for key, row in inputs.items():
        require(isinstance(key, str) and isinstance(row, dict), "proof input row differs")
        require(
            set(row) == {"path", "bytes", "sha256"} and row.get("path") == key,
            f"proof input stamp shape differs: {key}",
        )
        relative = PurePosixPath(key)
        require(
            not relative.is_absolute()
            and ".." not in relative.parts
            and str(relative) == key,
            f"proof input route differs: {key}",
        )
        size = row.get("bytes")
        digest = row.get("sha256")
        require(
            isinstance(size, int)
            and not isinstance(size, bool)
            and isinstance(digest, str)
            and re.fullmatch(r"[0-9a-f]{64}", digest) is not None,
            f"proof input identity differs: {key}",
        )
        require_stamp(ROOT / Path(*relative.parts), (size, digest), f"proof input {key}")


def validate_external_inputs() -> None:
    require_stamp(PARENT / "campaign.ready.json", PARENT_READY, "parent READY")
    require_stamp(PARENT_AUTHORITY_PATH, PARENT_AUTHORITY_STAMP, "parent authority")
    require_stamp(PROOF / "proof.ready.json", PROOF_READY, "proof READY")
    require_stamp(ROOT / "tools/re_mission_native_unsetobjective_reproof.py", PROOF_AUTHOR, "proof author")
    validate_proof_inputs()
    require_stamp(ROOT / "tools/re_campaign_frozen_bootstrap.py", BOOTSTRAP, "frozen bootstrap")
    for label, (path, size, digest) in REBUILD_FILES.items():
        require_stamp(path, (size, digest), f"rebuild {label}")


def main() -> int:
    try:
        require(not OUT.exists(), f"refusing existing authority receipt: {OUT}")
        partial = OUT.with_name(OUT.name + ".partial")
        require(not partial.exists(), f"stale partial authority receipt: {partial}")
        author_start = Path(__file__).resolve().read_bytes()
        validate_pair()
        validate_external_inputs()
        live_proof = ROOT / "tools/re_mission_native_unsetobjective_reproof.py"
        frozen_proof = CANONICAL / "_reducer/tools/re_mission_native_unsetobjective_reproof.py"
        require_stamp(frozen_proof, PROOF_AUTHOR, "frozen proof author")
        require_stamp(live_proof, PROOF_AUTHOR, "live proof author before verify")
        proof_verify = run_checked(
            [sys.executable, "-I", "-B", str(live_proof), "verify"],
            "MISSION_NATIVE_UNSETOBJECTIVE_REPROOF_VERIFIED",
            timeout=300,
        )
        require_stamp(live_proof, PROOF_AUTHOR, "live proof author after verify")
        validate_external_inputs()
        require_stamp(frozen_proof, PROOF_AUTHOR, "frozen proof author before selftest")
        validate_external_inputs()
        proof_selftest = run_checked(
            [sys.executable, "-I", "-B", str(frozen_proof), "selftest"],
            "MISSION_NATIVE_UNSETOBJECTIVE_REPROOF_SELFTEST_OK",
            timeout=300,
        )
        require_stamp(frozen_proof, PROOF_AUTHOR, "frozen proof author after selftest")
        validate_external_inputs()
        rebuild = run_checked(
            [
                "dotnet",
                "test",
                str(ROOT / "rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj"),
                "--no-restore",
                "--filter",
                "FullyQualifiedName~MissionNativeUnsetObjective_ClearsOnlyTheObjectiveFlagAndIsIdempotent",
            ],
            "Passed!",
            timeout=300,
            census=(0, 1, 0, 1),
        )
        validate_external_inputs()
        canonical_verify = run_full(CANONICAL, READY[CANONICAL.name])
        replica_verify = run_full(REPLICA, READY[REPLICA.name])
        canonical, replica = validate_pair()
        validate_external_inputs()
        require_stamp(live_proof, PROOF_AUTHOR, "live proof author before final verify")
        final_proof_verify = run_checked(
            [sys.executable, "-I", "-B", str(live_proof), "verify"],
            "MISSION_NATIVE_UNSETOBJECTIVE_REPROOF_VERIFIED",
            timeout=300,
        )
        require_stamp(live_proof, PROOF_AUTHOR, "live proof author after final verify")
        validate_external_inputs()
        canonical, replica = validate_pair()
        require(Path(__file__).resolve().read_bytes() == author_start, "authority author changed")
        receipt = {
            "schema": "bea.re.mission-native-unsetobjective-generation19-authority.v1",
            "verdict": "READY",
            "authorityClass": "FULL_REPLAY_CAMPAIGN_AUTHORITY",
            "replayScope": "FULL_CAMPAIGN_REDUCER_REPLAY_NOT_GAME_TTD_OR_GHIDRA_REPLAY",
            "completedAtUtc": datetime.now(timezone.utc).isoformat(),
            "lineageId": "incident-20260806-recovery-v1",
            "author": {
                "path": "tools/re_mission_native_unsetobjective_campaign_authority.py",
                "bytes": len(author_start),
                "sha256": hashlib.sha256(author_start).hexdigest(),
            },
            "canonical": {
                "absolutePath": str(CANONICAL),
                "ready": stamp(CANONICAL / "campaign.ready.json", relative_to=CANONICAL),
                "reducerId": REDUCER_ID,
                "generation": 19,
                "kind": ADVANCE_KIND,
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
                "readySha256": PARENT_READY[1],
                "reducerId": PARENT_REDUCER_ID,
                "authorityReceiptSha256": PARENT_AUTHORITY_STAMP[1],
            },
            "proof": {
                "path": PROOF.relative_to(ROOT).as_posix(),
                "readySha256": PROOF_READY[1],
                "authorSha256": PROOF_AUTHOR[1],
                "schema": "bea.re.mission-native-unsetobjective-boundary-reproof.v1",
                "claim": "MISSION_NATIVE_UNSETOBJECTIVE_EXACT_FUNCTION_NOP_PARTITION_AND_STATIC_CONTRACT",
            },
            "counts": COUNTS,
            "outputs": {
                name: {"bytes": size, "sha256": digest}
                for name, (size, digest) in OUTPUTS.items()
            },
            "claimBoundary": {
                "functionEntity": FUNCTION_ENTITY,
                "contractId": FUNCTION_CONTRACT,
                "residualRetired": OLD_RESIDUAL,
                "paddingEntities": PADDING_ENTITIES,
                "questionsClosed": QUESTIONS_CLOSED,
                "questionOpened": QUESTION_OPENED,
                "adjudicationIds": ADJUDICATIONS,
                "supersessionIds": SUPERSESSIONS,
                "staticProofGrade": "C1_STATIC",
                "campaignSemanticGrade": "C1_CANDIDATE_PARTIAL",
                "admissionAdjudicationVerdict": "SURVIVED",
                "contractRefuterVerdict": "UNSCORED",
                "runtimeVerdict": "UNSCORED",
                "runtimeReplays": 0,
                "partitionBytes": 19,
                "functionBytes": 13,
                "paddingBytes": 6,
                "opaque004e5bd0Semantics": "OPEN",
                "liveGhidraMutation": False,
                "executableBytesChanged": 0,
                "rebuildState": "PARTIAL_CONTRACT",
            },
            "rebuild": {
                "state": "PARTIAL_CONTRACT",
                "owner": "rebuild/OnslaughtRebuild.Core/Level100ActorScriptRuntime.cs",
                "registry": "rebuild/OnslaughtRebuild.Core/Level100ActorRegistry.cs",
                "tests": "rebuild/OnslaughtRebuild.Core.Tests/Level100MissionTests.cs",
                "focusedParity": rebuild,
            },
            "determinism": {
                "allEightLedgersByteIdentical": True,
                "allThirtyNineReducerFilesByteIdentical": True,
                "normalizedReadyReceiptsEqual": True,
                "normalizedFields": ["generatedAtUtc", "outputs.*.lastWriteUtc"],
            },
            "verification": {
                "exactStaticProof": proof_verify,
                "frozenStaticProofSelftest": proof_selftest,
                "finalExactStaticProof": final_proof_verify,
                "canonicalLiteralPinnedFullReplay": canonical_verify,
                "replicaLiteralPinnedFullReplay": replica_verify,
            },
            "frozenOwners": {
                "campaign": stamp(CANONICAL / "_reducer/tools/re_campaign.py", relative_to=ROOT),
                "proof": stamp(frozen_proof, relative_to=ROOT),
                "rebuildRegistry": stamp(CANONICAL / "_reducer/rebuild/OnslaughtRebuild.Core/Level100ActorRegistry.cs", relative_to=ROOT),
                "rebuildRuntime": stamp(CANONICAL / "_reducer/rebuild/OnslaughtRebuild.Core/Level100ActorScriptRuntime.cs", relative_to=ROOT),
                "rebuildTest": stamp(CANONICAL / "_reducer/rebuild/OnslaughtRebuild.Core.Tests/Level100MissionTests.cs", relative_to=ROOT),
                "preImportLauncher": stamp(ROOT / "tools/re_campaign_frozen_bootstrap.py", relative_to=ROOT),
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
                    "runtime, opaque-callee, Ghidra-live, or rebuild-complete overclaims",
                ],
            },
            "limitations": {
                "proofScope": "SPECIMEN_BOUND_STATIC_REGISTRY_WRAPPER_CALLEE_AND_BYTE_COMPLETE_GHIDRA_XREF_PROOF",
                "opaque004e5bd0Semantics": "OPEN",
                "runtimeBehavior": "OPEN",
                "hudAndLifetimeBehavior": "OPEN",
                "liveGhidraMutation": False,
                "rebuildState": "PARTIAL_CONTRACT",
                "nextValidGeneration": 20,
            },
        }
        require(Path(__file__).resolve().read_bytes() == author_start, "authority author changed before publication")
        OUT.parent.mkdir(parents=True, exist_ok=True)
        require(not OUT.exists(), f"authority receipt appeared during execution: {OUT}")
        require(not partial.exists(), f"partial receipt appeared during execution: {partial}")
        with partial.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(receipt, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        require(not OUT.exists(), f"authority receipt appeared before publication: {OUT}")
        os.rename(partial, OUT)
        print(
            "MISSION_NATIVE_UNSETOBJECTIVE_GEN19_AUTHORITY_READY "
            f"bytes={OUT.stat().st_size} sha256={sha256(OUT)} path={OUT}"
        )
        return 0
    except (AuthorityError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(f"MISSION_NATIVE_UNSETOBJECTIVE_GEN19_AUTHORITY_REFUSED: {exc}", file=sys.stderr)
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
