#!/usr/bin/env python3
"""Validate the level-854 input-assisted outcome transition proof bundle."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import build_winui_original_binary_level854_input_assisted_outcome_bundle as builder


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROOF = builder.DEFAULT_OUTPUT
PUBLIC_JSON = ROOT / "roadmap" / "original-binary-online-level854-input-assisted-outcome.v1.json"
READINESS_NOTE = ROOT / "release" / "readiness" / "original_binary_level854_input_assisted_outcome_2026-06-19.md"
CAPABILITIES_DOC = ROOT / "CURRENT_CAPABILITIES.md"
FEASIBILITY_DOC = ROOT / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
REGISTER_DOC = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
PACKAGE_JSON = ROOT / "package.json"
CLASSIFICATION_TSV = ROOT / "roadmap" / "release-allowlist-classification.tsv"
PUBLIC_ALLOWLIST_TSV = ROOT / "release" / "readiness" / "public_candidate_allowlist.tsv"
PRIVATE_INVENTORY_TSV = ROOT / "release" / "readiness" / "private_only_inventory.tsv"
RELEASE_PROFILE_DOC = ROOT / "roadmap" / "release-allowlist-profile.md"

PUBLIC_REQUIRED_FALSE_TOKENS = (
    "runtimeOutcomeProof=false",
    "baseOnlineMultiplayerReady=false",
    "publicMatchmakingProof=false",
    "nativeBeaNetcodeProof=false",
    "activeP3P4OriginalBinaryGameplayProof=false",
)
PUBLIC_FORBIDDEN_TRUE_TOKENS = (
    "baseOnlineMultiplayerReady=true",
    "publicMatchmakingProof=true",
    "multiHostLanProof=true",
    "secondPhysicalHostProof=true",
    "nativeBeaNetcodeProof=true",
    "activeP3P4OriginalBinaryGameplayProof=true",
)
PUBLIC_RELEASE_ALLOW_ROWS = (
    "roadmap/original-binary-online-level854-input-assisted-outcome.v1.json\tR0_ALLOW",
    "tools/runtime-probes/local-multiplayer-level854-input-assisted-outcome-observer.cdb.txt\tR0_ALLOW",
)
PRIVATE_RELEASE_DENY_ROWS = (
    "tools/build_winui_original_binary_level854_input_assisted_outcome_bundle.py\tR4_DENY",
    "tools/winui_safe_copy_online_level854_input_assisted_outcome_check.py\tR4_DENY",
    "tools/winui_safe_copy_online_level854_input_assisted_outcome_check_test.py\tR4_DENY",
)


class Level854InputAssistedOutcomeError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Level854InputAssistedOutcomeError(message)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def read_text(path: Path) -> str:
    require(path.is_file(), f"required repo file missing: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8-sig")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def list_at(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    require(isinstance(child, list), f"missing list: {key}")
    return child


def resolve_source(path: Path, raw: str) -> Path:
    candidate = Path(raw)
    require(raw and not candidate.is_absolute(), f"source artifact reference must be relative: {raw}")
    resolved = (path.parent / candidate).resolve()
    require(resolved.is_file(), f"source artifact missing: {resolved}")
    return resolved


def require_source_artifacts(bundle: dict[str, Any], path: Path) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    artifacts = object_at(bundle, "sourceArtifacts")
    runtime_path = resolve_source(path, str(artifacts.get("liveRuntimeArtifact", "")))
    command_file = resolve_source(path, str(artifacts.get("observerCommandFile", "")))
    require(artifacts.get("liveRuntimeArtifactSha256") == builder.sha256_file(runtime_path), "runtime artifact hash mismatch")
    try:
        runtime, log_path, parsed, windows = builder.validate_runtime_artifact(runtime_path)
    except builder.Level854InputAssistedOutcomeBuildError as exc:
        raise Level854InputAssistedOutcomeError(str(exc)) from exc
    require(artifacts.get("cdbLogSha256") == builder.sha256_file(log_path), "CDB log hash mismatch")
    require(command_file == builder.COMMAND_FILE.resolve(), "observer command file path mismatch")
    require(artifacts.get("observerCommandFileSha256") == builder.sha256_file(command_file), "observer command file hash mismatch")
    return runtime, parsed, windows


def require_runtime_evidence(bundle: dict[str, Any], parsed: dict[str, Any]) -> dict[str, Any]:
    runtime = object_at(bundle, "runtimeEvidence")
    require(runtime.get("safeCopyLaunchLevel") == 854, "runtime level mismatch")
    require(runtime.get("controllerConfiguration") == 1, "controller configuration mismatch")
    require(runtime.get("newBeaLaunchCount") == 1, "launch count mismatch")
    require(runtime.get("cdbAttachCount") == 1, "CDB count mismatch")
    require(runtime.get("boundedCaptureCount", 0) >= 2, "bounded capture count too low")
    require(runtime.get("visualCaptureCount") == runtime.get("boundedCaptureCount"), "all captures must be visual")
    require(runtime.get("exactPidCdbObserverProven") is True, "exact PID CDB observer flag missing")
    require(runtime.get("renderPlayers") == 2, "render player count mismatch")
    require(runtime.get("renderLevel") == 854, "render level mismatch")
    require(runtime.get("horizontalSplit") is True, "horizontal split flag missing")
    require(runtime.get("p1p2PointersDistinct") is True, "P1/P2 distinct flag missing")
    require(runtime.get("sourceHashesUnchanged") is True, "source hash boundary missing")
    require(runtime.get("managedStopClean") is True, "managed stop boundary missing")
    require(parsed["render"]["level"] == 854 and parsed["render"]["players"] == 2, "parsed render evidence mismatch")
    return runtime


def require_input_outcome(bundle: dict[str, Any], parsed_windows: list[dict[str, Any]]) -> dict[str, Any]:
    section = object_at(bundle, "inputAssistedOutcome")
    require(section.get("inputAssistedOutcomeAttempted") is True, "input-assisted attempt flag missing")
    require(section.get("forcedOutcomeTransition") is False, "forced outcome transition must be false")
    require(section.get("forcedWinDeathRespawn") is False, "forced win/death/respawn must be false")
    require(section.get("backgroundWindowMessagesAllowed") is False, "background window messages must be false")
    windows = list_at(section, "inputWindowSummaries")
    require(windows == parsed_windows, "input window summaries must match parsed CDB windows")
    require(section.get("inputWindowCount") == len(windows), "input window count mismatch")
    stimulus_count = len([row for row in windows if isinstance(row, dict) and row.get("stimulusWindow") is True])
    wait_count = len([row for row in windows if isinstance(row, dict) and row.get("stimulusWindow") is False])
    require(stimulus_count > 0, "no stimulus input windows recorded")
    require(wait_count > 0, "no wait/no-input control windows recorded")
    require(section.get("stimulusWindowCount") == stimulus_count, "stimulus window count mismatch")
    require(section.get("waitControlWindowCount") == wait_count, "wait control window count mismatch")
    input_transition_count = sum(int(row.get("outcomeTransitionHitCount", 0)) for row in windows if isinstance(row, dict) and row.get("stimulusWindow") is True)
    wait_transition_count = sum(int(row.get("outcomeTransitionHitCount", 0)) for row in windows if isinstance(row, dict) and row.get("stimulusWindow") is False)
    require(section.get("inputWindowOutcomeTransitionHitCount") == input_transition_count, "input-window transition count mismatch")
    require(section.get("waitWindowOutcomeTransitionHitCount") == wait_transition_count, "wait-window transition count mismatch")
    require(wait_transition_count == 0, "wait/no-input window outcome transition cannot be causal proof")
    positive_stimulus_window_count = len(
        [
            row
            for row in windows
            if isinstance(row, dict)
            and row.get("stimulusWindow") is True
            and int(row.get("outcomeTransitionHitCount", 0)) > 0
            and int(row.get("inputAssistHitCount", 0)) > 0
        ]
    )
    require(
        section.get("positiveStimulusWindowCount") == positive_stimulus_window_count,
        "positive stimulus window count mismatch",
    )
    require(
        input_transition_count == 0 or positive_stimulus_window_count > 0,
        "stimulus-window transition requires same-window input-assist evidence",
    )
    require(
        section.get("runtimeOutcomeProof") is (positive_stimulus_window_count > 0),
        "runtime outcome flag must match transition-positive stimulus windows with input hits",
    )
    require(
        section.get("stimulusAttemptOnly") is (positive_stimulus_window_count == 0),
        "stimulus-attempt flag must match missing positive stimulus window",
    )
    if positive_stimulus_window_count > 0:
        require(section.get("minimalDeathOrRespawnProof") is True or section.get("strongWinOrDrawProof") is True, "positive outcome proof needs death/respawn/win/draw classification")
    return section


def require_surfaces_and_boundaries(bundle: dict[str, Any], parsed: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    surface = object_at(bundle, "outcomeSemanticsSurface")
    require(surface.get("outcomeHookSurfaceObserved") is True, "outcome hook surface flag missing")
    require(surface.get("selectedRuntimeCandidate") == 854, "selected runtime candidate mismatch")
    require(surface.get("outcomeHookTargetCount") == len(builder.observer.OUTCOME_TARGETS), "outcome hook target count mismatch")
    require(surface.get("hookTargetCount") == parsed["hookTargetCount"], "hook target count mismatch")
    require(surface.get("expectedHookTargetCount") == len(builder.observer.TARGETS), "expected hook target count mismatch")
    require(surface.get("hitCounts") == parsed["hitCounts"], "total hit counts mismatch")
    require(surface.get("unforcedTransitionTargets") == builder.observer.UNFORCED_TRANSITION_TARGETS, "transition target list mismatch")
    require(surface.get("totalUnforcedTransitionHitCount") == parsed["unforcedTransitionHitCount"], "total transition hit count mismatch")
    require(surface.get("modeRuntimeProofSlicesAdded") == 0, "mode proof count must stay zero")
    require(surface.get("coOpVersusModeRuntimeProofSlicesAdded") == 0, "co-op/versus proof count must stay zero")
    require(surface.get("currentRuntimeModeClassification") == "unclassified-local-multiplayer", "mode classification must stay unclassified")
    slot = object_at(bundle, "slotBoundary")
    require(slot.get("acceptedOriginalBinaryGameplaySlots") == ["P1", "P2"], "accepted slots mismatch")
    require(slot.get("metadataOnlySlots") == ["P3", "P4"], "metadata-only slots mismatch")
    require(slot.get("activeP3P4OriginalBinaryGameplayProof") is False, "P3/P4 proof must stay false")
    require(slot.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player runtime proof must stay zero")
    nonclaims = object_at(bundle, "nonClaims")
    for key, value in nonclaims.items():
        require(value is False, f"non-claim must remain false: {key}")
    return surface, nonclaims


def validate_bundle(path: Path, *, allow_fixture: bool = False) -> dict[str, Any]:
    path = path.resolve()
    if not allow_fixture:
        builder.require_private_path(path, must_exist=True)
    bundle = read_json(path)
    require(bundle.get("schemaVersion") == builder.SCHEMA, "schema mismatch")
    require(bundle.get("generatedBy") == builder.HELPER, "helper mismatch")
    require(bundle.get("helperVersion") == builder.HELPER_VERSION, "helper version mismatch")
    require(bundle.get("protocolVersion") == builder.PROTOCOL, "protocol mismatch")
    require(bundle.get("proofScope") == builder.SCOPE, "proof scope mismatch")
    runtime_artifact, parsed, parsed_windows = require_source_artifacts(bundle, path)
    receipt = object_at(bundle, "executionReceipt")
    require(receipt.get("runtimeGeneratedAt") == runtime_artifact.get("generatedAt"), "runtime generatedAt receipt mismatch")
    require(receipt.get("replayArtifactAcceptedForPromotion") is False, "replay artifact promotion must remain false")
    if not allow_fixture:
        require(receipt.get("freshLiveExecution") is True, "default proof must come from fresh live execution")
        require(str(receipt.get("runtimeArtifactRootName", "")).startswith("level854-input-assisted-outcome-live-"), "runtime artifact root must be fresh input-assisted live root")
    runtime = require_runtime_evidence(bundle, parsed)
    attempt = require_input_outcome(bundle, parsed_windows)
    surface, nonclaims = require_surfaces_and_boundaries(bundle, parsed)
    claim = str(bundle.get("claimBoundary", ""))
    for token in (
        "input-assisted outcome transition attempt",
        "focused scoped input",
        "Only outcome-transition hits inside stimulus input windows with same-window input-assist hits can promote runtimeOutcomeProof",
        "not real online multiplayer",
        "not native BEA netcode",
        "not active P3/P4 gameplay",
    ):
        require(token in claim, f"claim boundary missing token: {token}")
    return {
        "artifact": "<private-level854-input-assisted-outcome-proof>",
        "schemaVersion": bundle["schemaVersion"],
        "proofScope": bundle["proofScope"],
        "newBeaLaunchCount": runtime["newBeaLaunchCount"],
        "cdbAttachCount": runtime["cdbAttachCount"],
        "boundedCaptureCount": runtime["boundedCaptureCount"],
        "visualCaptureCount": runtime["visualCaptureCount"],
        "renderPlayers": runtime["renderPlayers"],
        "renderLevel": runtime["renderLevel"],
        "inputAssistedOutcomeAttempted": attempt["inputAssistedOutcomeAttempted"],
        "stimulusAttemptOnly": attempt["stimulusAttemptOnly"],
        "inputWindowOutcomeTransitionHitCount": attempt["inputWindowOutcomeTransitionHitCount"],
        "waitWindowOutcomeTransitionHitCount": attempt["waitWindowOutcomeTransitionHitCount"],
        "runtimeOutcomeProof": attempt["runtimeOutcomeProof"],
        "minimalDeathOrRespawnProof": attempt["minimalDeathOrRespawnProof"],
        "strongWinOrDrawProof": attempt["strongWinOrDrawProof"],
        "outcomeHookTargetCount": surface["outcomeHookTargetCount"],
        "totalUnforcedTransitionHitCount": surface["totalUnforcedTransitionHitCount"],
        "baseOnlineMultiplayerReady": nonclaims["baseOnlineMultiplayerReady"],
        "nativeBeaNetcodeProof": nonclaims["nativeBeaNetcodeProof"],
        "activeP3P4OriginalBinaryGameplayProof": nonclaims["activeP3P4OriginalBinaryGameplayProof"],
    }


def require_public_claim_tokens(text: str, label: str, required_tokens: tuple[str, ...] = PUBLIC_REQUIRED_FALSE_TOKENS) -> None:
    for token in required_tokens:
        require(token in text, f"{label} missing public non-claim token: {token}")
    for token in PUBLIC_FORBIDDEN_TRUE_TOKENS:
        require(token not in text, f"{label} contains forbidden overclaim token: {token}")


def require_release_boundaries(
    classification: str,
    public_allowlist: str,
    private_inventory: str,
    release_profile: str,
) -> None:
    for row in PUBLIC_RELEASE_ALLOW_ROWS:
        require(row in classification, f"classification missing public row: {row}")
        require(row in public_allowlist, f"public allowlist missing row: {row}")
    for row in PRIVATE_RELEASE_DENY_ROWS:
        require(row in classification, f"classification missing private-deny row: {row}")
        require(row in private_inventory, f"private inventory missing row: {row}")
        require(row.split("\t", 1)[0] in release_profile, f"release profile missing private-deny path: {row}")
        require(row.split("\t", 1)[0] not in public_allowlist, f"public allowlist includes private tool: {row}")
    require("subagents/" not in public_allowlist.replace("\\", "/"), "public allowlist must not include ignored private runtime artifacts")


def validate_repo() -> dict[str, Any]:
    summary = validate_bundle(DEFAULT_PROOF)
    package_text = read_text(PACKAGE_JSON)
    for token in (
        "test:winui-original-binary-level854-input-assisted-outcome",
        "build_winui_original_binary_level854_input_assisted_outcome_bundle.py",
        "winui_safe_copy_online_level854_input_assisted_outcome_check_test.py",
        "winui_safe_copy_online_level854_input_assisted_outcome_check.py --self-test",
        "winui_safe_copy_online_level854_input_assisted_outcome_check.py --check",
    ):
        require(token in package_text, f"package script missing token: {token}")

    public_json = read_json(PUBLIC_JSON)
    require(public_json.get("proofScope") == builder.SCOPE, "public JSON proof scope mismatch")
    input_section = object_at(public_json, "inputAssistedOutcome")
    nonclaims = object_at(public_json, "nonClaims")
    release_boundary = object_at(public_json, "releaseBoundary")
    claim_boundary = str(public_json.get("claimBoundary", ""))
    for token in (
        "not runtime outcome proof",
        "not online multiplayer",
        "not native BEA netcode",
        "not active P3/P4 gameplay",
    ):
        require(token in claim_boundary, f"public JSON claim boundary missing token: {token}")
    require(input_section.get("runtimeOutcomeProof") is False, "public JSON runtime outcome proof must be false")
    require(input_section.get("stimulusAttemptOnly") is True, "public JSON stimulus-attempt flag missing")
    require(input_section.get("positiveStimulusWindowCount") == 0, "public JSON positive window count must stay zero")
    for key in (
        "baseOnlineMultiplayerReady",
        "secondPhysicalHostProof",
        "multiHostLanProof",
        "publicMatchmakingProof",
        "nativeBeaNetcodeProof",
        "coOpModeRuntimeProof",
        "versusModeRuntimeProof",
        "activeP3P4OriginalBinaryGameplayProof",
        "moreThanTwoOriginalBinaryRuntimeProof",
    ):
        require(nonclaims.get(key) is False, f"public JSON non-claim must remain false: {key}")
    require(release_boundary.get("privateProofReleaseExcludedByPolicy") is True, "public JSON release exclusion flag missing")
    for key in (
        "rawPrivateProofPathPublished",
        "rawPrivateArtifactContentPublished",
        "absolutePrivatePathPublished",
        "rawRuntimePointerPublishedInPublicDocs",
        "rawRuntimePidPublishedInPublicDocs",
        "rawCdbLogPathPublishedInPublicDocs",
        "releaseIncludedPrivateArtifact",
    ):
        require(release_boundary.get(key) is False, f"public JSON release boundary must remain false: {key}")

    public_docs = {
        "readiness note": read_text(READINESS_NOTE),
        "CURRENT_CAPABILITIES.md": read_text(CAPABILITIES_DOC),
        "online feasibility doc": read_text(FEASIBILITY_DOC),
        "runtime rebuild register": read_text(REGISTER_DOC),
    }
    for label, text in public_docs.items():
        require("level854" in text or "level-854" in text, f"{label} missing level854 reference")
        require("input-assisted" in text, f"{label} missing input-assisted reference")
        require_public_claim_tokens(text, label)

    require_release_boundaries(
        read_text(CLASSIFICATION_TSV),
        read_text(PUBLIC_ALLOWLIST_TSV),
        read_text(PRIVATE_INVENTORY_TSV),
        read_text(RELEASE_PROFILE_DOC),
    )
    summary["repoClaimBoundaryValidated"] = True
    summary["releaseBoundaryValidated"] = True
    return summary


def make_fixture(
    root: Path,
    *,
    transition_in_stimulus_window: bool = False,
    transition_without_input_assist: bool = False,
    transition_in_wait_window: bool = False,
    background_window_messages: bool = False,
    external_cdb_log: bool = False,
    wrong_command_file: bool = False,
) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    cdb_root = root / "cdb"
    cdb_root.mkdir(parents=True, exist_ok=True)
    log_path = Path(tempfile.gettempdir()) / "level854-input-assisted-external-cdb.log" if external_cdb_log else cdb_root / "fixture-cdb.log"
    chunks: list[str] = []
    prelude = [
        ".echo === fixture ===\n",
        *[
            f"OUTCOME_SEM_HOOK_TARGET name={target['name']} address={target['address']} category={target['category']}\n"
            for target in builder.observer.TARGETS
        ],
        "OUTCOME_SEM_HIT name=CGame__Render this=008a9a98 players=2 level=854 horizSplit=1 p0=0467c090 p1=04693890 cam0=04111111 cam1=04222222 world=00855090\n",
        "INPUT_ASSIST_HOOK_TARGET name=CController__SendButtonAction address=0x0042e4d0 category=input-dispatch\n",
        "INPUT_ASSIST_HOOK_TARGET name=CPlayer__ReceiveButtonAction address=0x004d3110 category=input-dispatch\n",
        "INPUT_ASSIST_HOOK_TARGET name=CBattleEngine__StartDieProcess address=0x0040bfd0 category=death-start\n",
    ]
    chunks.append("".join(prelude))
    sequences = ["wait:1000", "down:Q,wait:500,up:Q", "wait:500", "down:E,wait:500,up:E", "wait:1000"]
    windows: list[dict[str, Any]] = []
    cursor = len("".join(chunks).encode("utf-8"))
    for index, sequence in enumerate(sequences, start=1):
        body = ""
        should_write_input_assist = not builder.is_wait_only_sequence(sequence) and not (
            transition_without_input_assist and index == 2
        )
        if should_write_input_assist:
            body += "INPUT_ASSIST_HIT name=CController__SendButtonAction controller=00112233 button=31 analogRaw=00000000 inputDevice=00000000 controllerConfig=00000001 target=0467c090\n"
            body += "INPUT_ASSIST_HIT name=CPlayer__ReceiveButtonAction player=0467c090 fromController=00112233 button=31 analogRaw=00000000 gameP0=0467c090 gameP1=04693890 be=04770000 state098=00000000 state260=00000002\n"
        if transition_in_stimulus_window and index == 2:
            body += "OUTCOME_SEM_HIT name=CGame__DeclarePlayerDead this=008a9a98 playerNumber=1\n"
        if transition_in_wait_window and index == 1:
            body += "OUTCOME_SEM_HIT name=CGame__DeclarePlayerDead this=008a9a98 playerNumber=1\n"
        start = cursor
        end = start + len(body.encode("utf-8"))
        windows.append({"index": index, "sequence": sequence, "logPath": str(log_path), "logStartByte": start, "logEndByte": end})
        chunks.append(body)
        cursor = end
    log_path.write_text("".join(chunks), encoding="utf-8")
    runtime_path = root / "live-safe-copy-runtime-smoke.json"
    captures = [
        {"status": "captured", "visualProof": True, "foregroundMatchesTarget": True, "outputPath": "capture-0.png"},
        {"status": "captured", "visualProof": True, "foregroundMatchesTarget": True, "outputPath": "capture-1.png"},
    ]
    runtime = {
        "schemaVersion": "winui-safe-copy-live-runtime-smoke.v1",
        "generatedAt": "2026-06-19T00:00:00Z",
        "launch": {"arguments": ["-skipfmv", "-level", "854", "-configuration", "1"]},
        "source": {"installedHashUnchanged": True, "overrideHashUnchanged": True, "saveAndOptions": {"unchanged": True}},
        "processBaseline": {"noPreexistingBea": True, "noBeaAfterStop": True},
        "stop": {"Success": True},
        "captures": captures,
        "cdbObserver": {
            "enabled": True,
            "commandFile": str(builder.ROOT / "tools" / "runtime-probes" / "local-multiplayer-level854-outcome-semantics-observer.cdb.txt") if wrong_command_file else str(builder.COMMAND_FILE),
            "logPath": str(log_path),
            "result": {
                "status": "attached",
                "logExists": True,
                "commandFile": str(builder.ROOT / "tools" / "runtime-probes" / "local-multiplayer-level854-outcome-semantics-observer.cdb.txt") if wrong_command_file else str(builder.COMMAND_FILE),
                "logPath": str(log_path),
                "helperPayload": {"logPath": str(log_path)},
            },
            "cleanup": {"status": "stopped"},
        },
        "input": [{"status": "sent", "sequence": sequence} for sequence in sequences],
        "inputCdbWindows": windows,
        "inputPlan": {
            "inputSequenceCount": len(sequences),
            "inputStepDelayMs": 100,
            "allowBackgroundWindowMessages": False,
            "focusBeforePreInputCapture": True,
        },
        "inputSummary": {
            "inputSequencesSent": len(sequences),
            "focusedInputSequences": len(sequences),
            "inputActionCount": 9,
            "inputKeyEventsSent": 4,
            "inputSendInputEventsSent": 4,
            "inputScanKeybdEventsSent": 0,
            "inputWindowMessageEventsSent": 0,
            "inputMouseEventsSent": 0,
        },
    }
    write_json(runtime_path, runtime)
    output = root / "level854-input-assisted-outcome-proof.json"
    builder.build_bundle_from_runtime(runtime_path, output)
    if background_window_messages:
        runtime = read_json(runtime_path)
        runtime["inputPlan"]["allowBackgroundWindowMessages"] = True
        runtime["inputSummary"]["focusedInputSequences"] = 0
        runtime["inputSummary"]["inputWindowMessageEventsSent"] = 1
        write_json(runtime_path, runtime)
        bundle = read_json(output)
        new_hash = builder.sha256_file(runtime_path)
        bundle["sourceArtifacts"]["liveRuntimeArtifactSha256"] = new_hash
        bundle["executionReceipt"]["runtimeArtifactSha256"] = new_hash
        write_json(output, bundle)
    return output


def self_test() -> None:
    builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
        summary = validate_bundle(make_fixture(Path(tmp)), allow_fixture=True)
        require(summary["stimulusAttemptOnly"] is True, "default fixture should be stimulus attempt only")
    with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
        summary = validate_bundle(make_fixture(Path(tmp), transition_in_stimulus_window=True), allow_fixture=True)
        require(summary["runtimeOutcomeProof"] is True, "transition fixture should prove runtime outcome")
    with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
        try:
            validate_bundle(
                make_fixture(Path(tmp), transition_in_stimulus_window=True, transition_without_input_assist=True),
                allow_fixture=True,
            )
        except (Level854InputAssistedOutcomeError, builder.Level854InputAssistedOutcomeBuildError):
            pass
        else:
            raise Level854InputAssistedOutcomeError("stimulus transition without same-window input assist should fail")
    with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
        try:
            validate_bundle(make_fixture(Path(tmp), transition_in_wait_window=True), allow_fixture=True)
        except (Level854InputAssistedOutcomeError, builder.Level854InputAssistedOutcomeBuildError):
            pass
        else:
            raise Level854InputAssistedOutcomeError("wait-window transition fixture should fail")
    with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
        try:
            validate_bundle(make_fixture(Path(tmp), external_cdb_log=True), allow_fixture=True)
        except (Level854InputAssistedOutcomeError, builder.Level854InputAssistedOutcomeBuildError):
            pass
        else:
            raise Level854InputAssistedOutcomeError("external CDB log fixture should fail")
    with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
        try:
            validate_bundle(make_fixture(Path(tmp), wrong_command_file=True), allow_fixture=True)
        except (Level854InputAssistedOutcomeError, builder.Level854InputAssistedOutcomeBuildError):
            pass
        else:
            raise Level854InputAssistedOutcomeError("wrong CDB command file fixture should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof", nargs="?", type=Path, default=DEFAULT_PROOF)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("WinUI original-binary level854 input-assisted outcome checker self-test: PASS")
        return 0
    if args.check:
        print(json.dumps(validate_repo(), indent=2, sort_keys=True))
        return 0
    print(json.dumps(validate_bundle(args.proof), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Level854InputAssistedOutcomeError, builder.Level854InputAssistedOutcomeBuildError) as exc:
        print(f"WinUI original-binary level854 input-assisted outcome check: FAIL: {exc}")
        raise SystemExit(2)
