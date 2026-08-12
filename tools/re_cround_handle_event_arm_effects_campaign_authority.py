#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Select the literal-pinned canonical Generation 23 arm-effects campaign."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "local-lab/re-campaign-incident-recovery-20260808-v1"
EVIDENCE = ROOT / "local-lab/cround-handle-event-arm-effects-20260812-v1"
CANONICAL = BASE / "generation-23-cround-handle-event-arm-effects-v1"
REPLICA = BASE / "generation-23-cround-handle-event-arm-effects-replica-v1"
PARENT = BASE / "generation-22-cround-handle-event-runtime-v1"
PARENT_AUTHORITY = BASE / "generation-22-cround-handle-event-runtime-authority.ready.json"
PROOF = EVIDENCE / "proof-v1"
OVERLAY = EVIDENCE / "runtime-overlay-v1"
FINDING = EVIDENCE / "refuter-finding-v1.json"
RESULT = EVIDENCE / "refuter-result-v1.json"
ADJUDICATION = EVIDENCE / "adjudication-v1.json"
OUT = BASE / "generation-23-cround-handle-event-arm-effects-authority.ready.json"

REDUCER_ID = "a757bc51cd8302cf0e889c7db72ca58f9d865597b250371444d8c2285537db09"
READY = {
    CANONICAL.name: "4471fdfe105340ad06c2ad28d945eb05e9bc94f002110888b164581ccf1a93fc",
    REPLICA.name: "6cee7a24763fb24b9a83ab32cd56a445d2b6fbe839c381dd75b5e4fc90005a38",
}
OUTPUTS = {
    "campaign-functions.tsv": (5_132_331, "da7b433165535360b1a40ca8317509d2f1a48b24eaa1c0f9f652e13e886a79cb"),
    "campaign-residuals.tsv": (2_865_672, "f24a5f1d8a16fd5857d2801848af6fc59820a7590e5056b01efb8fdedd9528b9"),
    "campaign-questions.tsv": (8_377_693, "b42926642ce618444ab5b2887d973717ec37f95f1a6b0dacfa27a0b1aa4eecb0"),
    "campaign-scenarios.tsv": (31_860, "35a84fad46065d1317e48b41c66889a1dd12327077766423693b8839be857542"),
    "campaign-levers.tsv": (329_226, "fa337d96cfe7b6eca266b44aa39deded516e3a8cc02979a31671b449c66e3cdc"),
    "campaign-contracts.tsv": (10_939_169, "49214126f0b32154b645b01584197c5ab71d38ea4baa4ca0e3046deab4ca680f"),
    "campaign-adjudications.tsv": (3_337_186, "b173569be1d619f872a6dae7f6a2f616c86c25242a0426dcd0ccac9a0ed9b542"),
    "campaign-supersessions.tsv": (462_797, "87d58f2344ade1589a34360cdb21345fa3b2edc4965c6d41e1267df3c718eab4"),
}
COUNTS = {
    "functions": 8_126, "residuals": 6_119, "questions": 15_264,
    "scenarios": 72, "levers": 915, "contracts": 14_245,
    "adjudications": 6_103, "supersessions": 592,
}

PARENT_READY = (20_759, "a0c8d3fb8d31f36e03b417b179bbe2f2c99f6dd47700e0f0ad2e8fad5feeac90")
PARENT_AUTHORITY_STAMP = (15_761, "86b3fb12b18622dd837eb5e92b9f7ed8ecb7452c125f27bdca9d2fa98efab5b0")
PROOF_READY = (90_443, "974cbb86f8857d44369aef03e72b61656960147b7161466c4823e8d0c6ee867d")
OVERLAY_READY = (11_552, "341834e47349dc8e2c7097f40f9bc6d390e216d61a32b6d3a36df2d0c2983307")
FINDING_STAMP = (10_355, "28682d68afb0c3ddc8bcc17523657650b2e0800e2f87c6880127530f4795953a")
RESULT_STAMP = (5_305, "222898ab36605d5a2c3ec5642e8572197dd74cacd8af995e69d37c6379a90e67")
ADJUDICATION_STAMP = (3_019, "f1778fde37cdb61df8179b4a8de020909c54c4901ac7e01b5a98fe785413e17d")
CAMPAIGN_AUTHOR = (1_170_467, "2cffc1f9b5a4e9c48c7c56a77df64b2d514c5cda26592fb2dc7f08eedf0787d1")
PROOF_AUTHOR = (62_971, "1da51cc025a724fd6145c3c6cd3ec2a91379481b7b7eabf5c8c8baf674762f2b")
PROOF_TEST = (3_108, "9eabe73bde7398d034a691fd71ed7749003990dac7e6816f12b773580760d37e")
BOOTSTRAP = (17_831, "98b453b84bb4d312691f38e59a3a662d990963f3fdfac28f7e72ea1c1376562b")
REFUTER = (45_250, "21db5759f5aba97435cc3b8595f7d21e173780f8848da0f73584e6dbe6b30fc8")
REBUILD_OWNER = (31_466, "7942536b60d3bab2d0e534f2030fa74b4329b3bf9c2c19324e244c91aa33597b")
REBUILD_TEST = (17_883, "2232bde202407035adc81317058b5594ad69e038d0889e8fb2762058d7e7529c")

ENTITY = (
    "CODE:74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750:"
    "VA=0x004d9910:RANGES=e285cbff91ced5bc10d7ba635f1f46c107615698ebd98d46c299c22bea5666b3"
)
CONTRACT = "C-ff8b9307fccfd0ac"
BASE_QUESTION = "Q-43f69708557c9e15"
SUCCESSORS = ["Q-3a3b0f73e4293ef6", "Q-8f2e6951b7dee72b"]
ADJUDICATION_ID = "A-6d0ea5e65dd84a1c"


class AuthorityError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuthorityError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def stamp(path: Path, *, relative_to: Path | None = None) -> dict[str, Any]:
    require(path.is_file(), f"missing file: {path}")
    rendered = str(path.resolve())
    if relative_to is not None:
        rendered = os.path.relpath(path.resolve(), relative_to.resolve()).replace("\\", "/")
    return {"path": rendered, "bytes": path.stat().st_size, "sha256": sha256(path)}


def require_stamp(path: Path, expected: tuple[int, str], label: str) -> None:
    require(path.is_file(), f"{label} is missing")
    require((path.stat().st_size, sha256(path)) == expected, f"{label} differs")


def strict_json(path: Path) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            require(key not in result, f"duplicate JSON key in {path}: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)


def read_tsv(path: Path, key: str) -> dict[str, dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        first = handle.readline()
        if first.startswith("# "):
            first = handle.readline()
        rows = list(csv.DictReader([first, *handle], delimiter="\t"))
    result = {row[key]: row for row in rows}
    require(len(result) == len(rows), f"duplicate {key} in {path}")
    return result


def normalized_ready(value: dict[str, Any]) -> dict[str, Any]:
    copy = json.loads(json.dumps(value))
    copy.pop("generatedAtUtc", None)
    for output in copy.get("outputs", {}).values():
        output.pop("lastWriteUtc", None)
    return copy


def validate_campaign(root: Path, expected_ready: str) -> dict[str, Any]:
    ready_path = root / "campaign.ready.json"
    require(sha256(ready_path) == expected_ready, f"{root.name} READY differs")
    ready = strict_json(ready_path)
    require(ready.get("schema") == "bea.re.campaign.v5" and ready.get("generation") == 23, f"{root.name} generation differs")
    require(ready.get("reducer", {}).get("id") == REDUCER_ID and len(ready.get("reducer", {}).get("files", [])) == 44, f"{root.name} reducer differs")
    require(ready.get("counts") == COUNTS, f"{root.name} counts differ")
    parent = ready.get("parentCampaign", {})
    require(parent.get("ready", {}).get("sha256") == PARENT_READY[1], f"{root.name} parent differs")
    advance = ready.get("advance", {})
    require(
        advance.get("kind") == "RUNTIME_CONTRACT_ADJUDICATION"
        and advance.get("schema") == "bea.re.runtime-contract-advance.v1"
        and advance.get("overlay", {}).get("ready", {}).get("sha256") == OVERLAY_READY[1]
        and advance.get("adjudication", {}).get("sha256") == ADJUDICATION_STAMP[1]
        and advance.get("adjudicationId") == ADJUDICATION_ID
        and advance.get("verdict") == "SURVIVED",
        f"{root.name} advance differs",
    )
    for name, expected in OUTPUTS.items():
        require_stamp(root / name, expected, f"{root.name} {name}")
        output = ready.get("outputs", {}).get(name, {})
        require((output.get("bytes"), output.get("sha256")) == expected, f"{root.name} receipt output differs: {name}")
    return ready


def validate_pair() -> tuple[dict[str, Any], dict[str, Any]]:
    canonical = validate_campaign(CANONICAL, READY[CANONICAL.name])
    replica = validate_campaign(REPLICA, READY[REPLICA.name])
    require(CANONICAL.resolve() != REPLICA.resolve(), "campaign roots alias")
    for name in OUTPUTS:
        require((CANONICAL / name).read_bytes() == (REPLICA / name).read_bytes(), f"ledger pair differs: {name}")
    canonical_files = canonical["reducer"]["files"]
    replica_files = replica["reducer"]["files"]
    require(canonical_files == replica_files, "reducer manifests differ")
    for row in canonical_files:
        relative = Path(row["path"])
        require((CANONICAL / relative).read_bytes() == (REPLICA / relative).read_bytes(), f"reducer file pair differs: {relative}")
    require(normalized_ready(canonical) == normalized_ready(replica), "normalized READY receipts differ")
    return canonical, replica


def validate_delta() -> None:
    functions = read_tsv(CANONICAL / "campaign-functions.tsv", "entityKey")
    parent_functions = read_tsv(PARENT / "campaign-functions.tsv", "entityKey")
    require(set(functions) == set(parent_functions), "function identity set changed")
    changed_functions = [key for key in functions if functions[key] != parent_functions[key]]
    require(changed_functions == [ENTITY], "function delta is not the one target")
    require(
        {field for field in functions[ENTITY] if functions[ENTITY][field] != parent_functions[ENTITY][field]}
        == {"lever", "cheapestFalsifier"},
        "function field delta differs",
    )

    contracts = read_tsv(CANONICAL / "campaign-contracts.tsv", "contractId")
    parent_contracts = read_tsv(PARENT / "campaign-contracts.tsv", "contractId")
    require(set(contracts) == set(parent_contracts), "contract identity set changed")
    require([key for key in contracts if contracts[key] != parent_contracts[key]] == [CONTRACT], "contract delta is not the one target")
    contract = contracts[CONTRACT]
    require(contract["semanticGrade"] == "C2_BOUNDED_RUNTIME" and contract["refuterVerdict"] == "SURVIVED" and contract["rebuildState"] == "PARTIAL_CONTRACT", "contract grade boundary differs")
    require("43 default/3000" in contract["writes"] and "16 Level-512" in contract["writes"], "contract write summary differs")
    require("state-dependent" in contract["sideEffects"], "contract state divergence is absent")
    require(contract["questionIds"].endswith(";" + ";".join(SUCCESSORS)), "contract successors differ")

    questions = read_tsv(CANONICAL / "campaign-questions.tsv", "questionId")
    parent_questions = read_tsv(PARENT / "campaign-questions.tsv", "questionId")
    require(set(questions) - set(parent_questions) == set(SUCCESSORS) and not (set(parent_questions) - set(questions)), "question set delta differs")
    changed_questions = [key for key in parent_questions if questions[key] != parent_questions[key]]
    require(changed_questions == [BASE_QUESTION], "base question delta differs")
    require(questions[BASE_QUESTION]["state"] == "CLOSED_SURVIVED" and questions[BASE_QUESTION]["lastOutcome"] == "SURVIVED", "base question was not closed survived")
    require([questions[key]["questionType"] for key in SUCCESSORS] == ["CROUND_HANDLEEVENT_EXTERNAL_ARM_EFFECTS", "CROUND_HANDLEEVENT_EVENT2000_ARM_EFFECTS"], "successor types differ")

    adjudications = read_tsv(CANONICAL / "campaign-adjudications.tsv", "adjudicationId")
    parent_adjudications = read_tsv(PARENT / "campaign-adjudications.tsv", "adjudicationId")
    require(set(adjudications) - set(parent_adjudications) == {ADJUDICATION_ID} and not (set(parent_adjudications) - set(adjudications)), "adjudication set delta differs")
    row = adjudications[ADJUDICATION_ID]
    require(row["questionIdsAddressed"] == BASE_QUESTION and row["refuterVerdict"] == "SURVIVED" and row["successorQuestionIds"] == ";".join(SUCCESSORS), "adjudication row differs")

    for name in ("campaign-residuals.tsv", "campaign-scenarios.tsv", "campaign-levers.tsv", "campaign-supersessions.tsv"):
        require((CANONICAL / name).read_bytes() == (PARENT / name).read_bytes(), f"unrelated ledger changed: {name}")


def validate_external_inputs() -> None:
    require_stamp(PARENT / "campaign.ready.json", PARENT_READY, "parent READY")
    require_stamp(PARENT_AUTHORITY, PARENT_AUTHORITY_STAMP, "parent authority")
    require_stamp(PROOF / "proof.ready.json", PROOF_READY, "proof READY")
    require_stamp(OVERLAY / "runtime-contracts.ready.json", OVERLAY_READY, "overlay READY")
    require_stamp(FINDING, FINDING_STAMP, "refuter finding")
    require_stamp(RESULT, RESULT_STAMP, "refuter result")
    require_stamp(ADJUDICATION, ADJUDICATION_STAMP, "adjudication")
    require_stamp(ROOT / "tools/re_campaign.py", CAMPAIGN_AUTHOR, "campaign author")
    require_stamp(ROOT / "tools/re_cround_handle_event_arm_effects.py", PROOF_AUTHOR, "proof author")
    require_stamp(ROOT / "tools/re_cround_handle_event_arm_effects_tests.py", PROOF_TEST, "proof test")
    require_stamp(ROOT / "tools/re_campaign_frozen_bootstrap.py", BOOTSTRAP, "frozen bootstrap")
    require_stamp(ROOT / "tools/probe/refute.py", REFUTER, "probe refuter")
    require_stamp(ROOT / "rebuild/OnslaughtRebuild.Core/Level100ActorWeaponRuntime.cs", REBUILD_OWNER, "rebuild owner")
    require_stamp(ROOT / "rebuild/OnslaughtRebuild.Core.Tests/Level100ActorWeaponTests.cs", REBUILD_TEST, "rebuild test")

    proof = strict_json(PROOF / "proof.ready.json")
    boundary = proof.get("claimBoundary", {})
    require(
        proof.get("schema") == "bea.re.cround-handle-event-arm-effects-proof.v1"
        and proof.get("verdict") == "PASS"
        and proof.get("claim") == "CROUND_SLOT0_SELECTED_ARM_PATHS_AND_RECEIVER_WRITES_C2_BOUNDED"
        and proof.get("author", {}).get("sha256") == PROOF_AUTHOR[1]
        and proof.get("campaign", {}).get("ready", {}).get("sha256") == PARENT_READY[1]
        and boundary.get("selectedInvocations") == 5
        and boundary.get("default3000ExactReceiverWritePairs") == 43
        and boundary.get("event4003ExactReceiverWritePairs") == 4
        and boundary.get("event4001ExactReceiverWritePairs") == 9
        and boundary.get("event4000Level521ExactReceiverWritePairs") == 12
        and boundary.get("event4000Level512ExactReceiverWritePairs") == 16
        and boundary.get("event4000UniversalWriteSequenceClaimed") is False
        and boundary.get("externalWritesClaimed") is False
        and boundary.get("rebuildState") == "PARTIAL_CONTRACT",
        "proof boundary differs",
    )
    require(
        proof.get("crossSession", {}).get("normalizedSequencesDiffer") is True
        and proof.get("controls", {}).get("count") == 4
        and all(not row.get("accepted") for row in proof.get("controls", {}).get("controls", [])),
        "proof controls or divergence differ",
    )

    overlay = strict_json(OVERLAY / "runtime-contracts.ready.json")
    require(
        overlay.get("schema") == "bea.re.runtime-contract-overlay.v1"
        and overlay.get("count") == 1
        and overlay.get("sourceCampaign", {}).get("ready", {}).get("sha256") == PARENT_READY[1]
        and overlay.get("inputContract", {}).get("sha256") == PROOF_READY[1]
        and overlay.get("policy", {}).get("requiresRefuter") is True
        and overlay.get("policy", {}).get("namesAuthorized") is False
        and overlay.get("policy", {}).get("ghidraMutationAuthorized") is False
        and overlay.get("policy", {}).get("promotionAuthorized") is False,
        "overlay boundary differs",
    )
    finding, result, adjudication = strict_json(FINDING), strict_json(RESULT), strict_json(ADJUDICATION)
    subject = result.get("subject", {})
    require(
        finding.get("subject") == subject
        and result.get("verdict") == "SURVIVED"
        and result.get("rulesFired") == []
        and len(result.get("rulesPassed", [])) == 16
        and subject.get("baseContractId") == CONTRACT
        and subject.get("entityKey") == ENTITY
        and subject.get("overlayReadySha256") == OVERLAY_READY[1]
        and subject.get("questionIdsAddressed") == [BASE_QUESTION],
        "refuter subject/verdict differs",
    )
    decision = adjudication.get("decision", {})
    require(
        adjudication.get("baseCampaignReadySha256") == PARENT_READY[1]
        and adjudication.get("overlayReadySha256") == OVERLAY_READY[1]
        and decision.get("baseContractId") == CONTRACT
        and decision.get("questionIdsAddressed") == [BASE_QUESTION]
        and decision.get("refuterVerdict") == "SURVIVED"
        and [row.get("questionType") for row in decision.get("nextQuestions", [])]
        == ["CROUND_HANDLEEVENT_EXTERNAL_ARM_EFFECTS", "CROUND_HANDLEEVENT_EVENT2000_ARM_EFFECTS"]
        and decision.get("rebuildMapping", {}).get("rebuildState") == "PARTIAL_CONTRACT",
        "adjudication boundary differs",
    )


def clean_environment() -> dict[str, str]:
    environment = os.environ.copy()
    environment["BEA_REPO_ROOT"] = str(ROOT)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    for name in ("PYTHONHOME", "PYTHONPATH", "PYTHONSTARTUP", "PYTHONINSPECT", "PYTHONUSERBASE"):
        environment.pop(name, None)
    return environment


def run_checked(argv: list[str], marker: str | None, *, timeout: int) -> dict[str, Any]:
    completed = subprocess.run(argv, cwd=ROOT, env=clean_environment(), capture_output=True, text=True, timeout=timeout, check=False)
    require(completed.returncode == 0 and (marker is None or marker in completed.stdout), f"command failed: {argv}: {completed.stderr[-1200:]}")
    return {"command": argv, "exitCode": completed.returncode, "marker": marker or "EXIT_ZERO"}


def run_full(root: Path, ready: str) -> dict[str, Any]:
    return run_checked(
        [sys.executable, "-I", "-B", str(ROOT / "tools/re_campaign_frozen_bootstrap.py"), "--campaign", str(root), "--mode", "full", "--expected-ready-sha256", ready, "--expected-reducer-id", REDUCER_ID],
        "CAMPAIGN_VERIFIED", timeout=1_500,
    )


def main() -> int:
    try:
        require(not OUT.exists(), f"refusing existing authority receipt: {OUT}")
        author_bytes = Path(__file__).resolve().read_bytes()
        validate_pair()
        validate_delta()
        validate_external_inputs()

        proof_verify = run_checked([sys.executable, "-I", "-B", str(ROOT / "tools/re_cround_handle_event_arm_effects.py"), "--repo", str(ROOT), "--campaign", str(PARENT), "verify", "--proof", str(PROOF)], "CROUND_ARM_EFFECTS_PROOF_VERIFIED", timeout=300)
        proof_test = run_checked([sys.executable, "-I", "-B", str(ROOT / "tools/re_cround_handle_event_arm_effects_tests.py")], None, timeout=300)
        overlay_verify = run_checked([sys.executable, "-B", str(ROOT / "tools/re_campaign.py"), "verify-runtime-contract", "--out", str(OVERLAY)], "RUNTIME_CONTRACT_VERIFIED", timeout=300)
        refuter_verify = run_checked([sys.executable, "-I", "-B", str(ROOT / "tools/probe/refute.py"), str(FINDING), "--quiet"], None, timeout=300)
        canonical_verify = run_full(CANONICAL, READY[CANONICAL.name])
        replica_verify = run_full(REPLICA, READY[REPLICA.name])

        validate_pair()
        validate_delta()
        validate_external_inputs()
        require(Path(__file__).resolve().read_bytes() == author_bytes, "authority author changed")
        receipt = {
            "schema": "bea.re.cround-handle-event-arm-effects-generation23-authority.v1",
            "verdict": "READY", "authorityClass": "FULL_REPLAY_CAMPAIGN_AUTHORITY",
            "replayScope": "FULL_GENERATION23_REDUCER_REPLAY_WITH_EXACT_AUTHORITY_BACKED_GENERATION22_FROZEN_INTEGRITY_CARRY;_NO_GAME_TTD_GHIDRA_OR_REBUILD_REPLAY",
            "completedAtUtc": datetime.now(timezone.utc).isoformat(),
            "author": {"path": "tools/re_cround_handle_event_arm_effects_campaign_authority.py", "bytes": len(author_bytes), "sha256": hashlib.sha256(author_bytes).hexdigest()},
            "canonical": {"absolutePath": str(CANONICAL), "ready": stamp(CANONICAL / "campaign.ready.json", relative_to=CANONICAL), "reducerId": REDUCER_ID, "generation": 23, "adjudicationId": ADJUDICATION_ID},
            "replica": {"absolutePath": str(REPLICA), "ready": stamp(REPLICA / "campaign.ready.json", relative_to=REPLICA), "reducerId": REDUCER_ID, "role": "REPRODUCTION_ONLY_NOT_AUTHORITY_SELECTOR"},
            "parent": {"path": PARENT.relative_to(ROOT).as_posix(), "readySha256": PARENT_READY[1], "reducerId": REDUCER_ID, "authorityReceiptSha256": PARENT_AUTHORITY_STAMP[1], "carryBridge": "EXACT_AUTHORITY_BACKED_FROZEN_GENERATION22_INTEGRITY"},
            "evidence": {"proofReadySha256": PROOF_READY[1], "proofAuthorSha256": PROOF_AUTHOR[1], "overlayReadySha256": OVERLAY_READY[1], "refuterFindingSha256": FINDING_STAMP[1], "refuterResultSha256": RESULT_STAMP[1], "adjudicationSha256": ADJUDICATION_STAMP[1]},
            "counts": COUNTS,
            "outputs": {name: {"bytes": size, "sha256": digest} for name, (size, digest) in OUTPUTS.items()},
            "claimBoundary": {"functionEntity": ENTITY, "contractId": CONTRACT, "baseQuestionClosed": BASE_QUESTION, "successorQuestionsOpened": SUCCESSORS, "semanticGrade": "C2_BOUNDED_RUNTIME", "selectedInvocations": 5, "acceptedExactReceiverWritePairs": 84, "gapFreeInvocations": ["default3000", "event4003"], "witnessedOnlyInvocations": ["event4001", "event4000Level521", "event4000Level512"], "event4000CommonReceiverOffsetCount": 11, "event4000NormalizedSequencesDiffer": True, "externalWritesClaimed": False, "fieldMeaningsClaimed": False, "event2000EffectsClaimed": False, "event4002Observed": False, "cmissileStyleReceiverObserved": False, "completeArmSemanticsClaimed": False, "rebuildState": "PARTIAL_CONTRACT", "liveGhidraMutation": False, "executableBytesChanged": 0},
            "determinism": {"allEightLedgersByteIdentical": True, "allFortyFourReducerFilesByteIdentical": True, "normalizedReadyReceiptsEqual": True, "normalizedFields": ["generatedAtUtc", "outputs.*.lastWriteUtc"]},
            "verification": {"exactProof": proof_verify, "focusedProofTests": proof_test, "runtimeOverlay": overlay_verify, "probeRefuter": refuter_verify, "canonicalLiteralPinnedFullReplay": canonical_verify, "replicaLiteralPinnedFullReplay": replica_verify},
            "selectionRule": {"requiredAbsolutePath": str(CANONICAL), "literalReadySha256ByRoot": READY, "requiredReducerId": REDUCER_ID, "requiredMode": "FULL", "reject": ["replica as authority", "self-derived READY or reducer pins", "universal event4000 write sequence", "external-write or field-meaning overclaim", "gap-free upgrade of witnessed-only lanes", "Ghidra-live or rebuild-complete overclaim"]},
            "limitations": {"proofScope": "FIVE_SELECTED_SLOT0_ARM_PATHS_AND_EXACT_RECEIVER_WRITES", "externalAllocationContainerEventManagerEffects": "OPEN", "event2000Effects": "OPEN", "event4002Runtime": "OPEN", "cmissileStyleRuntimePlacement": "OPEN", "fieldMeanings": "OPEN", "broaderReceiverStates": "OPEN", "originalShippedSourceSpelling": "OPEN", "directRebuildParity": "OPEN", "liveGhidraMutation": False, "rebuildState": "PARTIAL_CONTRACT", "nextValidGeneration": 24},
        }
        OUT.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=OUT.parent, prefix=OUT.name + ".", suffix=".partial", delete=False) as handle:
            partial = Path(handle.name)
            json.dump(receipt, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        require(not OUT.exists(), "authority receipt appeared during execution")
        os.replace(partial, OUT)
        print(f"CROUND_ARM_EFFECTS_GEN23_AUTHORITY_READY bytes={OUT.stat().st_size} sha256={sha256(OUT)} path={OUT}")
        return 0
    except (AuthorityError, OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        print(f"CROUND_ARM_EFFECTS_GEN23_AUTHORITY_REFUSED: {exc}", file=sys.stderr)
        return 10


if __name__ == "__main__":
    raise SystemExit(main())
