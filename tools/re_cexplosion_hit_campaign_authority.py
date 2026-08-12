#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Select the literal-pinned canonical Generation 20 CExplosion campaign."""

from __future__ import annotations

import csv
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
EVIDENCE = ROOT / "local-lab/cexplosion-hit-existing-trace-20260812-v1"
CANONICAL = BASE / "generation-20-cexplosion-hit-runtime-v1"
REPLICA = BASE / "generation-20-cexplosion-hit-runtime-replica-v1"
PARENT = BASE / "generation-19-mission-native-unsetobjective-reproof-v1"
PARENT_AUTHORITY = (
    BASE
    / "generation-19-mission-native-unsetobjective-reproof-authority.ready.json"
)
PROOF = EVIDENCE / "proof-v1"
OVERLAY = EVIDENCE / "runtime-overlay-v1"
FINDING = EVIDENCE / "refuter-finding-v1.json"
RESULT = EVIDENCE / "refuter-result-v1.json"
ADJUDICATION = EVIDENCE / "adjudication-v1.json"
OUT = BASE / "generation-20-cexplosion-hit-runtime-authority.ready.json"

REDUCER_ID = "6e5777916ec5c7b94cdf6db727873bef589a14fec3bfac7ea4d895afda59c7fe"
READY = {
    CANONICAL.name: "13326fed25845e2351a2c68b57afe1bf2593786d2feb5f9e7d045fb7120a44ea",
    REPLICA.name: "a2a4b8d825b0cd6916f42abfb97cea6a34a72db97da131d3c133cdbccc0c4415",
}
OUTPUTS = {
    "campaign-functions.tsv": (
        5132136,
        "6dc341415dd0e5a3aa74db712878f995da5cc436233b2e911af9f23bdc85f5be",
    ),
    "campaign-residuals.tsv": (
        2865672,
        "f24a5f1d8a16fd5857d2801848af6fc59820a7590e5056b01efb8fdedd9528b9",
    ),
    "campaign-questions.tsv": (
        8372980,
        "7c9e41267a1e714548fe681efe695e1d92a92061290dc0ec403804bcf5760f07",
    ),
    "campaign-scenarios.tsv": (
        31860,
        "35a84fad46065d1317e48b41c66889a1dd12327077766423693b8839be857542",
    ),
    "campaign-levers.tsv": (
        329226,
        "fa337d96cfe7b6eca266b44aa39deded516e3a8cc02979a31671b449c66e3cdc",
    ),
    "campaign-contracts.tsv": (
        10934481,
        "0016a8a69b62968e873c445577fe6b4f8241b9dcd86f5d52f783dace1b9e5b03",
    ),
    "campaign-adjudications.tsv": (
        3334839,
        "cfc59b86e2ad9ef08971bc7fa4bd25f3292798792dd57269226a842910c763a8",
    ),
    "campaign-supersessions.tsv": (
        462797,
        "87d58f2344ade1589a34360cdb21345fa3b2edc4965c6d41e1267df3c718eab4",
    ),
}
COUNTS = {
    "functions": 8126,
    "residuals": 6119,
    "questions": 15257,
    "scenarios": 72,
    "levers": 915,
    "contracts": 14245,
    "adjudications": 6100,
    "supersessions": 592,
}
PARENT_READY = (
    27833,
    "f83dbb6eddaa16deed5f2a2460d393dc4525a63ae243b6cac0c656056b69ab9a",
)
PARENT_REDUCER_ID = (
    "151acbe5c1571dca2c53c68dd79281cf20c69af609523d54f25953643dcff3e2"
)
PARENT_AUTHORITY_STAMP = (
    12562,
    "72c22f029cd2f845c853dfbf2f5746062eed85ccc11d0291b531051c1e432360",
)
PROOF_READY = (
    25043,
    "ec7c4bcec3f11357de5afb8482179f67e030623bce38374be0afe8bf82620b66",
)
OVERLAY_READY = (
    5247,
    "326ba3fba46de7a2998798835aef97fdc2c675f30be9dfe6fc37cbc354b8d24e",
)
FINDING_STAMP = (
    8985,
    "2d67859596cb7b475fa02af564d13ab6a06e6aea8fe2341caaa44b2228989cdb",
)
RESULT_STAMP = (
    5143,
    "cad6b4e5de6c6d6772223dab3fb381a878959a44559dff5eb3f996f1d46a5244",
)
ADJUDICATION_STAMP = (
    2881,
    "a116cae373eec3ac78d3c7e1087b51df07b443c397baf0b158da5c0dc93dc7e5",
)
CAMPAIGN_AUTHOR = (
    1143703,
    "6b5d42fb4fcfc14475a4607ae5d1dca9b27852c24b4be20d81373c8e1c766ed4",
)
PROOF_AUTHOR = (
    55724,
    "d0fec4412497159c676f89a6d97be662987a03e812c0395cf9f2ead31318874c",
)
BOOTSTRAP = (
    17831,
    "98b453b84bb4d312691f38e59a3a662d990963f3fdfac28f7e72ea1c1376562b",
)
REFUTER = (
    45250,
    "21db5759f5aba97435cc3b8595f7d21e173780f8848da0f73584e6dbe6b30fc8",
)
REBUILD_FILES = {
    "owner": (
        ROOT / "rebuild/OnslaughtRebuild.Core/Level100Destruction.cs",
        40342,
        "295799e0c509ef48ddc10965eca9829034d2a4439e0424339785d9eabee7c72f",
    ),
    "test": (
        ROOT
        / "rebuild/OnslaughtRebuild.Core.Tests/Level100DestructionContactTests.cs",
        33186,
        "a2f728debefa6a0ad0d850489e1427959619da1884dffeaa79772005f3e388d2",
    ),
}

ADVANCE_KIND = "RUNTIME_CONTRACT_ADJUDICATION"
ADVANCE_SCHEMA = "bea.re.runtime-contract-advance.v1"
ENTITY = (
    "CODE:74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750:"
    "VA=0x0044bf10:RANGES=b61c167530383dc9d17a16505e35d702f71f15972f58abbfcfc61f59aefb3fbd"
)
CONTRACT = "C-fa1c3cbbcc43d1e4"
BASE_QUESTION = "Q-5e64a170c6a1dd45"
SUCCESSOR_QUESTIONS = ["Q-7e201ac83de75cb2", "Q-c9da4883732b4020"]
ADJUDICATION_ID = "A-44d48a9710721d7d"


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


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as handle:
        rows = [line for line in handle if not line.startswith("#")]
    return list(csv.DictReader(rows, delimiter="\t"))


def keyed(root: Path, name: str, key: str) -> dict[str, dict[str, str]]:
    rows = read_tsv(root / name)
    result = {row[key]: row for row in rows}
    require(len(result) == len(rows) and all(result), f"{name} keys differ")
    return result


def changed_fields(before: dict[str, str], after: dict[str, str]) -> set[str]:
    require(set(before) == set(after), "row field set differs")
    return {name for name in before if before[name] != after[name]}


def validate_campaign(root: Path, expected_ready: str) -> dict:
    require(root.resolve(strict=True) == root, f"campaign root aliases: {root}")
    root_info = root.lstat()
    require(
        not root.is_symlink()
        and not (getattr(root_info, "st_file_attributes", 0) & 0x400),
        f"campaign root is linked: {root}",
    )
    ready_path = root / "campaign.ready.json"
    require_plain_single(ready_path, f"{root.name} READY")
    require(sha256(ready_path) == expected_ready, f"{root.name} READY differs")
    receipt = strict_json(ready_path)
    advance = receipt.get("advance", {})
    parent = receipt.get("parentCampaign", {})
    require(receipt.get("generation") == 20, f"{root.name} generation differs")
    require(receipt.get("counts") == COUNTS, f"{root.name} counts differ")
    require(
        receipt.get("reducer", {}).get("id") == REDUCER_ID,
        f"{root.name} reducer differs",
    )
    require(
        parent.get("path") == str(PARENT)
        and parent.get("ready", {}).get("bytes") == PARENT_READY[0]
        and parent.get("ready", {}).get("sha256") == PARENT_READY[1],
        f"{root.name} parent differs",
    )
    require(
        advance.get("kind") == ADVANCE_KIND
        and advance.get("schema") == ADVANCE_SCHEMA
        and advance.get("adjudicationId") == ADJUDICATION_ID
        and advance.get("verdict") == "SURVIVED",
        f"{root.name} advance identity differs",
    )
    require(
        advance.get("overlay", {}).get("root") == str(OVERLAY)
        and advance.get("overlay", {}).get("ready", {}).get("bytes")
        == OVERLAY_READY[0]
        and advance.get("overlay", {}).get("ready", {}).get("sha256")
        == OVERLAY_READY[1]
        and advance.get("adjudication", {}).get("path") == str(ADJUDICATION)
        and advance.get("adjudication", {}).get("bytes")
        == ADJUDICATION_STAMP[0]
        and advance.get("adjudication", {}).get("sha256")
        == ADJUDICATION_STAMP[1],
        f"{root.name} overlay/adjudication differs",
    )
    require(
        [
            (row.get("role"), row.get("path"), row.get("bytes"), row.get("sha256"))
            for row in advance.get("refuterEvidence", [])
        ]
        == [
            (
                "refuter:refuter-finding",
                str(FINDING),
                FINDING_STAMP[0],
                FINDING_STAMP[1],
            ),
            (
                "refuter:refuter-result",
                str(RESULT),
                RESULT_STAMP[0],
                RESULT_STAMP[1],
            ),
        ],
        f"{root.name} refuter evidence differs",
    )
    receipt_outputs = receipt.get("outputs", {})
    require(set(receipt_outputs) == set(OUTPUTS), f"{root.name} output set differs")
    for name, expected in OUTPUTS.items():
        require_stamp(root / name, expected, f"{root.name} {name}")
        row = receipt_outputs[name]
        require(
            row.get("path") == name
            and row.get("bytes") == expected[0]
            and row.get("sha256") == expected[1],
            f"{root.name} output receipt differs: {name}",
        )
    manifest = receipt.get("reducer", {}).get("files")
    require(isinstance(manifest, list) and len(manifest) == 40, "reducer manifest differs")
    expected_paths = {str(row.get("path")) for row in manifest}
    actual_paths = {
        path.relative_to(root).as_posix()
        for path in (root / "_reducer").rglob("*")
        if path.is_file()
    }
    require(actual_paths == expected_paths, f"{root.name} reducer file set differs")
    for path in (root / "_reducer").rglob("*"):
        require(path.resolve(strict=True) == path, f"linked reducer path: {path}")
        entry = path.lstat()
        require(
            not path.is_symlink()
            and not (getattr(entry, "st_file_attributes", 0) & 0x400),
            f"linked reducer entry: {path}",
        )
    for row in manifest:
        require_stamp(
            root / row["path"],
            (int(row["bytes"]), str(row["sha256"])),
            f"{root.name} reducer {row['path']}",
        )
    return receipt


def validate_delta(root: Path) -> None:
    before_functions = keyed(PARENT, "campaign-functions.tsv", "entityKey")
    after_functions = keyed(root, "campaign-functions.tsv", "entityKey")
    require(set(before_functions) == set(after_functions), "function keys changed")
    require(
        {key for key in before_functions if before_functions[key] != after_functions[key]}
        == {ENTITY},
        "function delta differs",
    )
    require(
        changed_fields(before_functions[ENTITY], after_functions[ENTITY])
        == {
            "evidenceStates",
            "resolutionState",
            "semanticGrade",
            "campaignState",
            "lever",
            "cheapestFalsifier",
            "lastMeasurementDate",
        },
        "function field delta differs",
    )
    function = after_functions[ENTITY]
    require(
        function.get("currentName") == "CExplosion__VFunc_39_0044bf10"
        and function.get("semanticGrade") == "C2_BOUNDED_RUNTIME"
        and function.get("resolutionState") == "BOUNDED_CONTRACT"
        and function.get("campaignState") == "OPEN_AFTER_SURVIVED"
        and "RUNTIME_CONTRACT_REFUTER_SURVIVED"
        in function.get("evidenceStates", "").split(";"),
        "function bounded projection differs",
    )

    before_contracts = keyed(PARENT, "campaign-contracts.tsv", "contractId")
    after_contracts = keyed(root, "campaign-contracts.tsv", "contractId")
    require(set(before_contracts) == set(after_contracts), "contract keys changed")
    require(
        {key for key in before_contracts if before_contracts[key] != after_contracts[key]}
        == {CONTRACT},
        "contract delta differs",
    )
    require(
        changed_fields(before_contracts[CONTRACT], after_contracts[CONTRACT])
        == {
            "contractState",
            "semanticGrade",
            "receiver",
            "inputs",
            "returns",
            "writes",
            "sideEffects",
            "preconditions",
            "failureModes",
            "authorVerdict",
            "runtimeVerdict",
            "refuterVerdict",
            "questionIds",
            "evidenceRefs",
            "cheapestFalsifier",
            "rebuildOwner",
            "rebuildImplementation",
            "parityTests",
            "rebuildState",
            "remainingUncertainty",
            "lastMeasurementDate",
        },
        "contract field delta differs",
    )
    contract = after_contracts[CONTRACT]
    require(
        contract.get("entityKey") == ENTITY
        and contract.get("currentName") == "CExplosion__VFunc_39_0044bf10"
        and contract.get("contractState") == "BOUNDED_CONTRACT_ADVANCED"
        and contract.get("semanticGrade") == "C2_BOUNDED_RUNTIME"
        and contract.get("runtimeVerdict")
        == "MEASURED_BOUNDED_INTERNAL_CALL_CARRIER"
        and contract.get("refuterVerdict") == "SURVIVED"
        and contract.get("questionIds")
        == ";".join([BASE_QUESTION, *SUCCESSOR_QUESTIONS])
        and contract.get("rebuildState") == "PARTIAL_CONTRACT"
        and contract.get("rebuildImplementation")
        == "Level100DestructionState.ApplyPulseHit"
        and "Warehouse" in contract.get("remainingUncertainty", ""),
        "contract bounded projection differs",
    )

    before_questions = keyed(PARENT, "campaign-questions.tsv", "questionId")
    after_questions = keyed(root, "campaign-questions.tsv", "questionId")
    require(
        set(after_questions) - set(before_questions) == set(SUCCESSOR_QUESTIONS)
        and set(before_questions) - set(after_questions) == set(),
        "question key delta differs",
    )
    changed_existing = {
        key
        for key in before_questions
        if before_questions[key] != after_questions[key]
    }
    require(changed_existing == {BASE_QUESTION}, "existing question delta differs")
    require(
        changed_fields(before_questions[BASE_QUESTION], after_questions[BASE_QUESTION])
        == {"state", "attemptCount", "lastOutcome", "lastMeasurementDate"},
        "base question field delta differs",
    )
    require(
        after_questions[BASE_QUESTION].get("state") == "CLOSED_SURVIVED"
        and after_questions[BASE_QUESTION].get("lastOutcome") == "SURVIVED",
        "base question disposition differs",
    )
    require(
        [after_questions[item].get("questionType") for item in SUCCESSOR_QUESTIONS]
        == ["SEGMENTED_EXPLOSION_MESH_PART", "CEXPLOSION_FUNCTION_ENVELOPE"]
        and all(
            after_questions[item].get("state") == "OPEN"
            and after_questions[item].get("parentQuestionId") == BASE_QUESTION
            and after_questions[item].get("generation") == "20"
            for item in SUCCESSOR_QUESTIONS
        ),
        "successor questions differ",
    )

    before_adjudications = keyed(
        PARENT, "campaign-adjudications.tsv", "adjudicationId"
    )
    after_adjudications = keyed(
        root, "campaign-adjudications.tsv", "adjudicationId"
    )
    require(
        set(after_adjudications) - set(before_adjudications) == {ADJUDICATION_ID}
        and all(
            before_adjudications[key] == after_adjudications[key]
            for key in before_adjudications
        ),
        "adjudication delta differs",
    )
    adjudication = after_adjudications[ADJUDICATION_ID]
    require(
        adjudication.get("baseContractId") == CONTRACT
        and adjudication.get("entityKey") == ENTITY
        and adjudication.get("overlayReadySha256") == OVERLAY_READY[1]
        and adjudication.get("questionIdsAddressed") == BASE_QUESTION
        and adjudication.get("refuterVerdict") == "SURVIVED"
        and adjudication.get("semanticPromotionApplied") == "True"
        and adjudication.get("successorQuestionIds")
        == ";".join(SUCCESSOR_QUESTIONS)
        and adjudication.get("refuterEvidenceSha256")
        == ";".join([FINDING_STAMP[1], RESULT_STAMP[1]]),
        "adjudication projection differs",
    )


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
    validate_delta(CANONICAL)
    validate_delta(REPLICA)
    return canonical, replica


def validate_proof_inputs(proof: dict) -> None:
    inputs = proof.get("inputs")
    require(isinstance(inputs, dict) and len(inputs) == 28, "proof input set differs")
    for label, row in inputs.items():
        require(isinstance(label, str) and isinstance(row, dict), "proof input row differs")
        require(set(row) == {"path", "bytes", "sha256"}, f"proof input shape: {label}")
        relative = PurePosixPath(str(row.get("path", "")))
        require(
            not relative.is_absolute()
            and ".." not in relative.parts
            and relative.as_posix() == row.get("path"),
            f"proof input route differs: {label}",
        )
        size = row.get("bytes")
        digest = row.get("sha256")
        require(
            isinstance(size, int)
            and not isinstance(size, bool)
            and isinstance(digest, str)
            and re.fullmatch(r"[0-9a-f]{64}", digest) is not None,
            f"proof input stamp differs: {label}",
        )
        require_stamp(
            ROOT / Path(*relative.parts),
            (size, digest),
            f"proof input {label}",
        )


def validate_external_inputs() -> None:
    require_stamp(PARENT / "campaign.ready.json", PARENT_READY, "parent READY")
    require_stamp(PARENT_AUTHORITY, PARENT_AUTHORITY_STAMP, "parent authority")
    require_stamp(PROOF / "proof.ready.json", PROOF_READY, "runtime proof READY")
    require_stamp(
        OVERLAY / "runtime-contracts.ready.json",
        OVERLAY_READY,
        "runtime overlay READY",
    )
    require_stamp(FINDING, FINDING_STAMP, "refuter finding")
    require_stamp(RESULT, RESULT_STAMP, "refuter result")
    require_stamp(ADJUDICATION, ADJUDICATION_STAMP, "runtime adjudication")
    require_stamp(ROOT / "tools/re_campaign.py", CAMPAIGN_AUTHOR, "campaign author")
    require_stamp(
        ROOT / "tools/re_cexplosion_hit_runtime.py", PROOF_AUTHOR, "proof author"
    )
    require_stamp(
        ROOT / "tools/re_campaign_frozen_bootstrap.py", BOOTSTRAP, "frozen bootstrap"
    )
    require_stamp(ROOT / "tools/probe/refute.py", REFUTER, "probe refuter")
    for label, (path, size, digest) in REBUILD_FILES.items():
        require_stamp(path, (size, digest), f"rebuild {label}")

    proof = strict_json(PROOF / "proof.ready.json")
    require(
        proof.get("schema") == "bea.re.cexplosion-hit-runtime-proof.v1"
        and proof.get("verdict") == "PASS"
        and proof.get("claim") == "CEXPLOSION_SLOT40_ARGUMENT_CARRIER_C2_BOUNDED"
        and proof.get("author", {}).get("sha256") == PROOF_AUTHOR[1]
        and proof.get("campaign", {}).get("generation") == 19
        and proof.get("campaign", {}).get("ready", {}).get("sha256")
        == PARENT_READY[1]
        and proof.get("campaign", {}).get("reducerId") == PARENT_REDUCER_ID,
        "runtime proof identity differs",
    )
    boundary = proof.get("claimBoundary", {})
    runtime = proof.get("runtime", {})
    require(
        boundary.get("independentTraceSessions") == 3
        and boundary.get("internalSlot40CallsObserved") == 10
        and boundary.get("bothDamageArmsObserved") is True
        and boundary.get("sourceEqualsExplosionThisAllObservedCalls") is True
        and boundary.get("applyShieldsOneAllObservedCalls") is True
        and boundary.get("meshPartMinusOneAllObservedCalls") is True
        and boundary.get("directPartReuseRefutedForSixCUnitPairs") is True
        and boundary.get("cexplosionEntryObserved") is False
        and boundary.get("cexplosionReturnObserved") is False
        and boundary.get("cexplosionOwnedWritesObserved") is False
        and boundary.get("nonnegativeExplosionPartObserved") is False
        and boundary.get("warehouseOrSegmentControllerReceiverObserved") is False
        and boundary.get("universalCarrierClaim") is False
        and boundary.get("rebuildState") == "PARTIAL_CONTRACT"
        and runtime.get("sessions") == 3
        and len(runtime.get("calls", [])) == 10
        and runtime.get("callSiteCounts")
        == {"largeArm0044c061": 2, "smallArm0044c08e": 8}
        and runtime.get("targetClassCounts")
        == {"CBattleEngine": 2, "CTree": 2, "CUnit": 6}
        and runtime.get("poisonControl", {}).get("collectorExitCode") == 10
        and runtime.get("poisonControl", {}).get("readyPublished") is False,
        "runtime proof claim boundary differs",
    )
    validate_proof_inputs(proof)

    overlay = strict_json(OVERLAY / "runtime-contracts.ready.json")
    require(
        overlay.get("schema") == "bea.re.runtime-contract-overlay.v1"
        and overlay.get("count") == 1
        and overlay.get("sourceCampaign", {}).get("ready", {}).get("sha256")
        == PARENT_READY[1]
        and overlay.get("policy", {}).get("requiresRefuter") is True
        and overlay.get("policy", {}).get("namesAuthorized") is False
        and overlay.get("policy", {}).get("ghidraMutationAuthorized") is False
        and overlay.get("policy", {}).get("promotionAuthorized") is False,
        "runtime overlay boundary differs",
    )
    finding = strict_json(FINDING)
    result = strict_json(RESULT)
    adjudication = strict_json(ADJUDICATION)
    subject = result.get("subject", {})
    require(
        finding.get("subject") == subject
        and result.get("tool") == "tools/probe/refute.py"
        and result.get("verdict") == "SURVIVED"
        and subject.get("baseContractId") == CONTRACT
        and subject.get("entityKey") == ENTITY
        and subject.get("overlayReadySha256") == OVERLAY_READY[1]
        and subject.get("questionIdsAddressed") == [BASE_QUESTION],
        "refuter subject/verdict differs",
    )
    decision = adjudication.get("decision", {})
    require(
        adjudication.get("schema") == "bea.re.runtime-contract-adjudication.v1"
        and adjudication.get("baseCampaignReadySha256") == PARENT_READY[1]
        and adjudication.get("overlayReadySha256") == OVERLAY_READY[1]
        and decision.get("baseContractId") == CONTRACT
        and decision.get("questionIdsAddressed") == [BASE_QUESTION]
        and decision.get("refuterVerdict") == "SURVIVED"
        and decision.get("terminalState") == ""
        and [row.get("questionType") for row in decision.get("nextQuestions", [])]
        == ["SEGMENTED_EXPLOSION_MESH_PART", "CEXPLOSION_FUNCTION_ENVELOPE"]
        and decision.get("rebuildMapping", {}).get("rebuildState")
        == "PARTIAL_CONTRACT",
        "runtime adjudication boundary differs",
    )


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
    marker: str | None,
    *,
    timeout: int,
    census: tuple[int, int, int, int] | None = None,
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
        completed.returncode == 0
        and (marker is None or marker in completed.stdout),
        f"command failed: {argv}: {completed.stderr[-1200:]}",
    )
    result: dict[str, object] = {
        "command": argv,
        "exitCode": completed.returncode,
        "marker": marker or "EXIT_ZERO",
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
            "failed": actual[0],
            "passed": actual[1],
            "skipped": actual[2],
            "total": actual[3],
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


def main() -> int:
    try:
        require(not OUT.exists(), f"refusing existing authority receipt: {OUT}")
        partial = OUT.with_name(OUT.name + ".partial")
        require(not partial.exists(), f"stale partial authority receipt: {partial}")
        author_start = Path(__file__).resolve().read_bytes()
        validate_pair()
        validate_external_inputs()

        proof_author = ROOT / "tools/re_cexplosion_hit_runtime.py"
        frozen_proof = CANONICAL / "_reducer/tools/re_cexplosion_hit_runtime.py"
        require_stamp(proof_author, PROOF_AUTHOR, "live proof author before verify")
        require_stamp(frozen_proof, PROOF_AUTHOR, "frozen proof author")
        proof_verify = run_checked(
            [
                sys.executable,
                "-I",
                "-B",
                str(proof_author),
                "--repo",
                str(ROOT),
                "--campaign",
                str(PARENT),
                "verify",
                "--proof",
                str(PROOF),
            ],
            "CEXPLOSION_HIT_RUNTIME_PROOF_VERIFIED",
            timeout=300,
        )
        proof_selftest = run_checked(
            [
                sys.executable,
                "-I",
                "-B",
                str(proof_author),
                "--repo",
                str(ROOT),
                "--campaign",
                str(PARENT),
                "selftest",
            ],
            "CEXPLOSION_HIT_RUNTIME_SELFTEST_OK",
            timeout=300,
        )
        overlay_verify = run_checked(
            [
                sys.executable,
                "-B",
                str(ROOT / "tools/re_campaign.py"),
                "verify-runtime-contract",
                "--out",
                str(OVERLAY),
            ],
            "RUNTIME_CONTRACT_VERIFIED",
            timeout=300,
        )
        refuter_verify = run_checked(
            [
                sys.executable,
                "-I",
                "-B",
                str(ROOT / "tools/probe/refute.py"),
                str(FINDING),
                "--quiet",
            ],
            None,
            timeout=300,
        )
        rebuild = run_checked(
            [
                "dotnet",
                "test",
                str(
                    ROOT
                    / "rebuild/OnslaughtRebuild.Core.Tests/OnslaughtRebuild.Core.Tests.csproj"
                ),
                "--no-restore",
                "--filter",
                "FullyQualifiedName~PulseHitPreservesDirectThenExplosionDamageOrder",
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
        final_proof_verify = run_checked(
            [
                sys.executable,
                "-I",
                "-B",
                str(proof_author),
                "--repo",
                str(ROOT),
                "--campaign",
                str(PARENT),
                "verify",
                "--proof",
                str(PROOF),
            ],
            "CEXPLOSION_HIT_RUNTIME_PROOF_VERIFIED",
            timeout=300,
        )
        validate_pair()
        validate_external_inputs()
        require(
            Path(__file__).resolve().read_bytes() == author_start,
            "authority author changed",
        )

        receipt = {
            "schema": "bea.re.cexplosion-hit-generation20-authority.v1",
            "verdict": "READY",
            "authorityClass": "FULL_REPLAY_CAMPAIGN_AUTHORITY",
            "replayScope": (
                "FULL_GENERATION20_REDUCER_REPLAY_WITH_EXACT_FULL_REPLAY_"
                "AUTHORITY_BACKED_GENERATION19_FROZEN_INTEGRITY_CARRY;_"
                "NO_GAME_TTD_OR_GHIDRA_REPLAY"
            ),
            "completedAtUtc": datetime.now(timezone.utc).isoformat(),
            "lineageId": "incident-20260806-recovery-v1",
            "author": {
                "path": "tools/re_cexplosion_hit_campaign_authority.py",
                "bytes": len(author_start),
                "sha256": hashlib.sha256(author_start).hexdigest(),
            },
            "canonical": {
                "absolutePath": str(CANONICAL),
                "ready": stamp(
                    CANONICAL / "campaign.ready.json", relative_to=CANONICAL
                ),
                "reducerId": REDUCER_ID,
                "generation": 20,
                "kind": ADVANCE_KIND,
                "adjudicationId": ADJUDICATION_ID,
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
                "carryBridge": (
                    "EXACT_FULL_REPLAY_AUTHORITY_BACKED_FROZEN_"
                    "GENERATION19_INTEGRITY"
                ),
            },
            "evidence": {
                "proof": {
                    "path": PROOF.relative_to(ROOT).as_posix(),
                    "readySha256": PROOF_READY[1],
                    "authorSha256": PROOF_AUTHOR[1],
                    "schema": "bea.re.cexplosion-hit-runtime-proof.v1",
                    "claim": "CEXPLOSION_SLOT40_ARGUMENT_CARRIER_C2_BOUNDED",
                },
                "overlayReadySha256": OVERLAY_READY[1],
                "refuterFindingSha256": FINDING_STAMP[1],
                "refuterResultSha256": RESULT_STAMP[1],
                "adjudicationSha256": ADJUDICATION_STAMP[1],
            },
            "counts": COUNTS,
            "outputs": {
                name: {"bytes": size, "sha256": digest}
                for name, (size, digest) in OUTPUTS.items()
            },
            "claimBoundary": {
                "functionEntity": ENTITY,
                "contractId": CONTRACT,
                "currentNameUnchanged": "CExplosion__VFunc_39_0044bf10",
                "semanticGrade": "C2_BOUNDED_RUNTIME",
                "contractState": "BOUNDED_CONTRACT_ADVANCED",
                "runtimeVerdict": "MEASURED_BOUNDED_INTERNAL_CALL_CARRIER",
                "refuterVerdict": "SURVIVED",
                "internalSlot40CallsObserved": 10,
                "independentTraceSessions": 3,
                "targetClassCounts": {"CUnit": 6, "CTree": 2, "CBattleEngine": 2},
                "smallArmCalls": 8,
                "largeArmCalls": 2,
                "sourceEqualsExplosionThisAllObservedCalls": True,
                "applyShieldsOneAllObservedCalls": True,
                "meshPartMinusOneAllObservedCalls": True,
                "directPartReuseRefutedForSixCUnitPairs": True,
                "cexplosionEntryObserved": False,
                "cexplosionReturnObserved": False,
                "cexplosionOwnedWritesObserved": False,
                "nonnegativeExplosionPartObserved": False,
                "warehouseOrSegmentControllerReceiverObserved": False,
                "universalCarrierClaim": False,
                "baseQuestionClosed": BASE_QUESTION,
                "successorQuestionsOpened": SUCCESSOR_QUESTIONS,
                "adjudicationId": ADJUDICATION_ID,
                "liveGhidraMutation": False,
                "executableBytesChanged": 0,
                "rebuildState": "PARTIAL_CONTRACT",
            },
            "rebuild": {
                "state": "PARTIAL_CONTRACT",
                "owner": "rebuild/OnslaughtRebuild.Core/Level100Destruction.cs",
                "implementation": "Level100DestructionState.ApplyPulseHit",
                "tests": (
                    "rebuild/OnslaughtRebuild.Core.Tests/"
                    "Level100DestructionContactTests.cs"
                ),
                "focusedParity": rebuild,
            },
            "determinism": {
                "allEightLedgersByteIdentical": True,
                "allFortyReducerFilesByteIdentical": True,
                "normalizedReadyReceiptsEqual": True,
                "normalizedFields": ["generatedAtUtc", "outputs.*.lastWriteUtc"],
            },
            "verification": {
                "exactRuntimeProof": proof_verify,
                "runtimeProofSelftest": proof_selftest,
                "runtimeOverlay": overlay_verify,
                "probeRefuter": refuter_verify,
                "finalExactRuntimeProof": final_proof_verify,
                "canonicalLiteralPinnedFullReplay": canonical_verify,
                "replicaLiteralPinnedFullReplay": replica_verify,
            },
            "frozenOwners": {
                "campaign": stamp(
                    CANONICAL / "_reducer/tools/re_campaign.py", relative_to=ROOT
                ),
                "proof": stamp(frozen_proof, relative_to=ROOT),
                "refuter": stamp(
                    CANONICAL / "_reducer/tools/probe/refute.py", relative_to=ROOT
                ),
                "rebuildOwner": stamp(
                    CANONICAL
                    / "_reducer/rebuild/OnslaughtRebuild.Core/Level100Destruction.cs",
                    relative_to=ROOT,
                ),
                "rebuildTest": stamp(
                    CANONICAL
                    / (
                        "_reducer/rebuild/OnslaughtRebuild.Core.Tests/"
                        "Level100DestructionContactTests.cs"
                    ),
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
                    "unpinned or integrity-only Generation 20 verifier success",
                    "CExplosion name promotion",
                    "Warehouse or segmented-receiver inference",
                    "universal carrier inference",
                    "entry, return, or owned-write overclaim",
                    "Ghidra-live or rebuild-complete overclaim",
                ],
            },
            "limitations": {
                "proofScope": "BOUNDED_INTERNAL_SLOT40_ARGUMENT_CARRIER",
                "traceIdentityMode": (
                    "WRAPPER_HASH_RECEIPT_PLUS_CURRENT_SIZE_NOT_"
                    "MULTIGIGABYTE_TRACE_REHASH"
                ),
                "cexplosionEntryReturnAndOwnedWrites": "OPEN",
                "nonnegativeMeshPartPath": "OPEN",
                "warehouseAndSegmentedReceiver": "OPEN",
                "universalAllLevelAllTargetCarrier": "UNCLAIMED",
                "liveGhidraMutation": False,
                "executableBytesChanged": 0,
                "rebuildState": "PARTIAL_CONTRACT",
                "nextValidGeneration": 21,
            },
        }
        require(
            Path(__file__).resolve().read_bytes() == author_start,
            "authority author changed before publication",
        )
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
            "CEXPLOSION_HIT_GEN20_AUTHORITY_READY "
            f"bytes={OUT.stat().st_size} sha256={sha256(OUT)} path={OUT}"
        )
        return 0
    except (
        AuthorityError,
        OSError,
        subprocess.SubprocessError,
        json.JSONDecodeError,
    ) as exc:
        print(f"CEXPLOSION_HIT_GEN20_AUTHORITY_REFUSED: {exc}", file=sys.stderr)
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
