#!/usr/bin/env python3
"""Validate the level-854 fire-to-damage/outcome observer bundle."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path
from typing import Any

import build_winui_original_binary_level854_fire_damage_outcome_bundle as builder


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROOF = builder.DEFAULT_OUTPUT
PUBLIC_JSON = ROOT / "roadmap" / "original-binary-online-level854-fire-damage-outcome.v1.json"
READINESS_NOTE = ROOT / "release" / "readiness" / "original_binary_level854_fire_damage_outcome_2026-06-19.md"
CAPABILITIES_DOC = ROOT / "CURRENT_CAPABILITIES.md"
FEASIBILITY_DOC = ROOT / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
REGISTER_DOC = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
CONTRACT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "local-multiplayer-static-runtime-contract.md"
PACKAGE_JSON = ROOT / "package.json"
CLASSIFICATION_TSV = ROOT / "roadmap" / "release-allowlist-classification.tsv"
PUBLIC_ALLOWLIST_TSV = ROOT / "release" / "readiness" / "public_candidate_allowlist.tsv"
PRIVATE_INVENTORY_TSV = ROOT / "release" / "readiness" / "private_only_inventory.tsv"
RELEASE_PROFILE_DOC = ROOT / "roadmap" / "release-allowlist-profile.md"

PUBLIC_REQUIRED_TOKENS = (
    "level854-fire-to-damage-outcome-observer-not-online-proof",
    "button18RuntimeDispatchObserved=false",
    "button19RuntimeDispatchObserved=true",
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
    "roadmap/original-binary-online-level854-fire-damage-outcome.v1.json\tR0_ALLOW",
    "tools/runtime-probes/local-multiplayer-level854-fire-damage-outcome-observer.cdb.txt\tR0_ALLOW",
)
PRIVATE_RELEASE_DENY_ROWS = (
    "tools/build_winui_original_binary_level854_fire_damage_outcome_bundle.py\tR4_DENY",
    "tools/winui_safe_copy_online_level854_fire_damage_outcome_check.py\tR4_DENY",
    "tools/winui_safe_copy_online_level854_fire_damage_outcome_check_test.py\tR4_DENY",
)
PUBLIC_POINTER_FIELD_RE = re.compile(
    r"(?:pointer|ptr|address|runtimepointer|rawruntime|pid|processid|logpath|artifactpath|"
    r"weapon|projectile|round|victim|collider|collisionreport|damagesource|unit|be)$",
    re.IGNORECASE,
)
PUBLIC_PRIVATE_PATH_MARKERS = ("C:\\", "C:/", "/Users/", "subagents/", "AppData", "G:\\", "G:/")


class Level854FireDamageOutcomeError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Level854FireDamageOutcomeError(message)


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
    except builder.Level854FireDamageOutcomeBuildError as exc:
        raise Level854FireDamageOutcomeError(str(exc)) from exc
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


def require_fire_damage_outcome(bundle: dict[str, Any], parsed: dict[str, Any], parsed_windows: list[dict[str, Any]]) -> dict[str, Any]:
    section = object_at(bundle, "fireDamageOutcome")
    windows = list_at(section, "inputWindowSummaries")
    require(windows == parsed_windows, "input window summaries must match parsed CDB windows")
    require(section.get("copiedDefaultOptionsFireWeaponQe") is True, "copied Fire weapon Q/E flag missing")
    require(section.get("controlOptionsProofLever") == "copied-defaultoptions-weapon-fire-qe", "wrong proof lever")
    require(section.get("button18DispatchCount") == 0, "button 18 dispatch must remain absent in this proof")
    require(int(section.get("button19DispatchCount", 0)) > 0, "button 19 dispatch must be observed")
    require(section.get("button18RuntimeDispatchObserved") is False, "button 18 overclaim")
    require(section.get("button19RuntimeDispatchObserved") is True, "button 19 observed flag missing")
    require(section.get("inputWindowCount") == len(windows), "input window count mismatch")
    stimulus_windows = [row for row in windows if isinstance(row, dict) and row.get("stimulusWindow") is True]
    wait_windows = [row for row in windows if isinstance(row, dict) and row.get("stimulusWindow") is False]
    fire_windows = [row for row in stimulus_windows if row.get("sameWindowFireHandoff") is True]
    pointer_windows = [
        row
        for row in stimulus_windows
        if object_at(row, "fireBurstPointerChain").get("fireBurstPointerChainObserved") is True
    ]
    damage_windows = [row for row in stimulus_windows if row.get("sameWindowDamageSurface") is True]
    unit_damage_windows = [row for row in stimulus_windows if row.get("sameWindowUnitApplyDamage") is True]
    outcome_windows = [row for row in stimulus_windows if row.get("sameWindowOutcomeSurface") is True]
    wait_button_count = sum(int(row.get("button19DispatchCount", 0)) for row in wait_windows)
    wait_damage_count = sum(int(row.get("damageHitCount", 0)) for row in wait_windows)
    wait_outcome_count = sum(int(row.get("outcomeHitCount", 0)) for row in wait_windows)
    require(section.get("stimulusWindowCount") == len(stimulus_windows), "stimulus count mismatch")
    require(section.get("waitControlWindowCount") == len(wait_windows), "wait count mismatch")
    require(section.get("sameWindowFireHandoffWindowCount") == len(fire_windows), "fire window count mismatch")
    require(section.get("sameWindowFireBurstPointerChainWindowCount") == len(pointer_windows), "pointer-chain count mismatch")
    require(section.get("sameWindowDamageSurfaceWindowCount") == len(damage_windows), "damage window count mismatch")
    require(section.get("sameWindowUnitApplyDamageWindowCount") == len(unit_damage_windows), "unit damage window count mismatch")
    require(section.get("sameWindowOutcomeSurfaceWindowCount") == len(outcome_windows), "outcome window count mismatch")
    require(fire_windows, "fire/damage proof needs same-window fire handoff evidence")
    require(pointer_windows, "fire/damage proof needs same-window fire-to-burst pointer-chain evidence")
    require(section.get("waitWindowFireButtonDispatchCount") == wait_button_count == 0, "wait windows must not dispatch fire input")
    require(section.get("waitWindowDamageHitCount") == wait_damage_count, "wait damage count mismatch")
    require(section.get("waitWindowOutcomeHitCount") == wait_outcome_count, "wait outcome count mismatch")
    require(section.get("fireHitCount") == parsed["fireHitCount"], "fire hit count mismatch")
    require(section.get("projectileHitCount") == parsed["projectileHitCount"], "projectile hit count mismatch")
    require(section.get("damageHitCount") == parsed["damageHitCount"], "damage hit count mismatch")
    require(section.get("unitApplyDamageHitCount") == parsed["unitApplyDamageHitCount"], "unit damage hit count mismatch")
    require(section.get("roundCollisionHitCount") == parsed["roundCollisionHitCount"], "round collision hit count mismatch")
    require(section.get("outcomeHitCount") == parsed["outcomeHitCount"], "outcome hit count mismatch")
    damage_proof = bool(unit_damage_windows) and wait_damage_count == 0
    outcome_proof = bool(outcome_windows) and wait_outcome_count == 0
    require(section.get("damageProof") is damage_proof, "damage proof flag mismatch")
    require(section.get("runtimeOutcomeProof") is outcome_proof, "runtime outcome proof flag mismatch")
    require(section.get("fireToDamageOutcomePromotion") is (damage_proof and outcome_proof), "promotion flag mismatch")
    return section


def require_surfaces_and_boundaries(bundle: dict[str, Any], parsed: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    surface = object_at(bundle, "observerSurface")
    require(surface.get("hookTargetCount") == parsed["hookTargetCount"], "hook target count mismatch")
    require(surface.get("expectedHookTargetCount") == len(builder.TARGETS), "expected hook target count mismatch")
    require(surface.get("hitCounts") == parsed["hitCounts"], "total hit counts mismatch")
    require(surface.get("buttonCounts") == parsed["buttonCounts"], "button counts mismatch")
    require(surface.get("damageTargets") == builder.DAMAGE_TARGET_NAMES, "damage target list mismatch")
    require(surface.get("outcomeTargets") == builder.OUTCOME_TARGET_NAMES, "outcome target list mismatch")
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
        require(str(receipt.get("runtimeArtifactRootName", "")).startswith("level854-fire-damage-outcome-live-"), "runtime artifact root must be fresh fire/damage live root")
    runtime = require_runtime_evidence(bundle, parsed)
    section = require_fire_damage_outcome(bundle, parsed, parsed_windows)
    surface, nonclaims = require_surfaces_and_boundaries(bundle, parsed)
    claim = str(bundle.get("claimBoundary", ""))
    for token in (
        "fire-to-damage/outcome observer",
        "same-window runtime button 19 fire handoff",
        "CUnit__ApplyDamage appears inside a stimulus window",
        "not base online multiplayer",
        "not native BEA netcode",
        "not active P3/P4 gameplay",
    ):
        require(token in claim, f"claim boundary missing token: {token}")
    return {
        "artifact": "<private-level854-fire-damage-outcome-proof>",
        "schemaVersion": bundle["schemaVersion"],
        "proofScope": bundle["proofScope"],
        "newBeaLaunchCount": runtime["newBeaLaunchCount"],
        "cdbAttachCount": runtime["cdbAttachCount"],
        "boundedCaptureCount": runtime["boundedCaptureCount"],
        "visualCaptureCount": runtime["visualCaptureCount"],
        "button19DispatchCount": section["button19DispatchCount"],
        "sameWindowFireHandoffWindowCount": section["sameWindowFireHandoffWindowCount"],
        "sameWindowFireBurstPointerChainWindowCount": section["sameWindowFireBurstPointerChainWindowCount"],
        "sameWindowDamageSurfaceWindowCount": section["sameWindowDamageSurfaceWindowCount"],
        "sameWindowUnitApplyDamageWindowCount": section["sameWindowUnitApplyDamageWindowCount"],
        "sameWindowOutcomeSurfaceWindowCount": section["sameWindowOutcomeSurfaceWindowCount"],
        "waitWindowDamageHitCount": section["waitWindowDamageHitCount"],
        "waitWindowOutcomeHitCount": section["waitWindowOutcomeHitCount"],
        "damageHitCount": section["damageHitCount"],
        "unitApplyDamageHitCount": section["unitApplyDamageHitCount"],
        "roundCollisionHitCount": section["roundCollisionHitCount"],
        "outcomeHitCount": section["outcomeHitCount"],
        "damageProof": section["damageProof"],
        "runtimeOutcomeProof": section["runtimeOutcomeProof"],
        "fireToDamageOutcomePromotion": section["fireToDamageOutcomePromotion"],
        "hookTargetCount": surface["hookTargetCount"],
        "baseOnlineMultiplayerReady": nonclaims["baseOnlineMultiplayerReady"],
        "nativeBeaNetcodeProof": nonclaims["nativeBeaNetcodeProof"],
        "activeP3P4OriginalBinaryGameplayProof": nonclaims["activeP3P4OriginalBinaryGameplayProof"],
    }


def require_public_json_release_boundary(value: Any, *, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if PUBLIC_POINTER_FIELD_RE.search(key) and not isinstance(child, bool):
                raise Level854FireDamageOutcomeError(f"public JSON publishes raw runtime identity/path-like field: {child_path}")
            require_public_json_release_boundary(child, path=child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            require_public_json_release_boundary(child, path=f"{path}[{index}]")
    elif isinstance(value, str):
        normalized = value.replace("\\", "/")
        for marker in PUBLIC_PRIVATE_PATH_MARKERS:
            require(marker.replace("\\", "/") not in normalized, f"public JSON publishes private path-like value at {path}")
        if re.fullmatch(r"0x?[0-9a-fA-F]{7,8}", value):
            raise Level854FireDamageOutcomeError(f"public JSON publishes raw pointer-like value at {path}")


def require_public_claim_tokens(text: str, label: str, required_tokens: tuple[str, ...] = PUBLIC_REQUIRED_TOKENS) -> None:
    for token in required_tokens:
        require(token in text, f"{label} missing public boundary token: {token}")
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
        "test:winui-original-binary-level854-fire-damage-outcome",
        "build_winui_original_binary_level854_fire_damage_outcome_bundle.py",
        "winui_safe_copy_online_level854_fire_damage_outcome_check_test.py",
        "winui_safe_copy_online_level854_fire_damage_outcome_check.py --self-test",
        "winui_safe_copy_online_level854_fire_damage_outcome_check.py --check",
    ):
        require(token in package_text, f"package script missing token: {token}")

    public_json = read_json(PUBLIC_JSON)
    require_public_json_release_boundary(public_json)
    require(public_json.get("proofScope") == builder.SCOPE, "public JSON proof scope mismatch")
    section = object_at(public_json, "fireDamageOutcome")
    nonclaims = object_at(public_json, "nonClaims")
    release_boundary = object_at(public_json, "releaseBoundary")
    require(section.get("button18RuntimeDispatchObserved") is False, "public JSON button 18 overclaim")
    require(section.get("button19RuntimeDispatchObserved") is True, "public JSON button 19 flag missing")
    require(section.get("damageProof") == summary["damageProof"], "public JSON damage proof mismatch")
    require(section.get("runtimeOutcomeProof") == summary["runtimeOutcomeProof"], "public JSON outcome proof mismatch")
    require(section.get("fireToDamageOutcomePromotion") == summary["fireToDamageOutcomePromotion"], "public JSON promotion mismatch")
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
        "local multiplayer contract": read_text(CONTRACT_DOC),
    }
    for label, text in public_docs.items():
        require("fire-damage-outcome" in text or "fire-to-damage" in text, f"{label} missing fire/damage reference")
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
    no_button19: bool = False,
    no_fire: bool = False,
    no_pointer_chain: bool = False,
    unit_damage: bool = False,
    round_collision: bool = False,
    outcome: bool = False,
    wait_damage: bool = False,
    wait_outcome: bool = False,
    background_window_messages: bool = False,
    external_cdb_log: bool = False,
    wrong_command_file: bool = False,
) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    cdb_root = root / "cdb"
    cdb_root.mkdir(parents=True, exist_ok=True)
    log_path = Path(tempfile.gettempdir()) / "level854-fire-damage-outcome-external-cdb.log" if external_cdb_log else cdb_root / "fixture-cdb.log"
    chunks: list[str] = []
    prelude = [
        ".echo === fixture ===\n",
        *[
            f"FIRE_DAMAGE_HOOK_TARGET name={target['name']} address={target['address']} category={target['category']}\n"
            for target in builder.TARGETS
        ],
        "FIRE_DAMAGE_HIT name=CGame__Render this=008a9a98 players=2 level=854 horizSplit=1 p0=0467c090 p1=04693890 cam0=04111111 cam1=04222222 world=00855090\n",
    ]
    chunks.append("".join(prelude))
    windows: list[dict[str, Any]] = []
    cursor = len("".join(chunks).encode("utf-8"))
    for index, sequence in enumerate(builder.INPUT_SEQUENCES, start=1):
        body = ""
        stimulus = not builder.is_wait_only_sequence(sequence)
        if stimulus and not no_button19:
            body += "FIRE_DAMAGE_HIT name=CController__SendButtonAction controller=00112233 button=19 analogRaw=00000000 inputDevice=00000000 controllerConfig=00000001 target=0467c090\n"
            body += "FIRE_DAMAGE_HIT name=CPlayer__ReceiveButtonAction player=0467c090 fromController=00112233 button=19 analogRaw=00000000 gameP0=0467c090 gameP1=04693890 be=04770000 state098=00000000 state260=00000002\n"
        if stimulus and not no_fire:
            body += "FIRE_DAMAGE_HIT name=CBattleEngineWalkerPart__FireWeapon this=04770000\n"
            body += "FIRE_DAMAGE_HIT name=CBattleEngineWalkerPart__WeaponFired this=04770000 weapon=04990000\n"
            if not no_pointer_chain:
                body += "FIRE_DAMAGE_HIT name=CWeapon__HandleFireBurstEvent this=04990000 eventRecord=05000000 eventHeadRaw=04990000\n"
                body += "FIRE_DAMAGE_HIT name=ProjectileBurst__SpawnFromCurrentPreset burstContext=04990000\n"
        if stimulus and index == 2 and round_collision:
            body += "FIRE_DAMAGE_HIT name=VFuncSlot_39_004d8ae0 this=04aa0000 other=04bb0000 collisionReport=04cc0000 state124=00000000\n"
        if stimulus and index == 2 and unit_damage:
            body += "FIRE_DAMAGE_HIT name=CUnit__ApplyDamage this=04bb0000 damageRaw=3f800000 damageSource=04aa0000 applyShields=00000001 meshPartIndex=ffffffff lifeRaw=40a00000 shieldRaw=40000000\n"
        if stimulus and index == 2 and outcome:
            body += "FIRE_DAMAGE_HIT name=CBattleEngine__StartDieProcess be=04bb0000 player=0467c090 state098=00000001 state260=00000002 lifeRaw=00000000 shieldRaw=00000000\n"
            body += "FIRE_DAMAGE_HIT name=CGame__DeclarePlayerDead this=008a9a98 playerNumber=1\n"
        if not stimulus and index == 1 and wait_damage:
            body += "FIRE_DAMAGE_HIT name=CUnit__ApplyDamage this=04bb0000 damageRaw=3f800000 damageSource=04aa0000 applyShields=00000001 meshPartIndex=ffffffff lifeRaw=40a00000 shieldRaw=40000000\n"
        if not stimulus and index == 1 and wait_outcome:
            body += "FIRE_DAMAGE_HIT name=CGame__DeclarePlayerDead this=008a9a98 playerNumber=1\n"
        start = cursor
        end = start + len(body.encode("utf-8"))
        windows.append({"index": index, "sequence": sequence, "logPath": str(log_path), "logStartByte": start, "logEndByte": end})
        chunks.append(body)
        cursor = end
    log_path.write_bytes("".join(chunks).encode("utf-8"))
    command_file = ROOT / "tools" / "runtime-probes" / "local-multiplayer-level854-fire-handoff-observer.cdb.txt" if wrong_command_file else builder.COMMAND_FILE
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
        "safeCopy": {
            "controlOptions": {
                "requestedWeaponFireQe": True,
                "requestedInputIsolationForwardQe": False,
                "proofLever": "copied-defaultoptions-weapon-fire-qe",
                "OptionsPath": str(root / "GameProfiles" / "fixture" / "defaultoptions.bea"),
                "ProofStatus": "options_byte_materialized_only",
                "changedAfterPrepare": True,
                "changedRanges": [{"offset": 1, "length": 1}, {"offset": 2, "length": 1}],
            }
        },
        "processBaseline": {"noPreexistingBea": True, "noBeaAfterStop": True},
        "stop": {"Success": True},
        "captures": captures,
        "cdbObserver": {
            "enabled": True,
            "commandFile": str(command_file),
            "logPath": str(log_path),
            "result": {
                "status": "attached",
                "logExists": True,
                "commandFile": str(command_file),
                "logPath": str(log_path),
                "helperPayload": {"logPath": str(log_path)},
            },
            "cleanup": {"status": "stopped"},
        },
        "input": [{"status": "sent", "sequence": sequence} for sequence in builder.INPUT_SEQUENCES],
        "inputCdbWindows": windows,
        "inputPlan": {
            "inputSequenceCount": len(builder.INPUT_SEQUENCES),
            "inputStepDelayMs": 100,
            "allowBackgroundWindowMessages": False,
            "focusBeforePreInputCapture": True,
        },
        "inputSummary": {
            "inputSequencesSent": len(builder.INPUT_SEQUENCES),
            "focusedInputSequences": len(builder.INPUT_SEQUENCES),
            "inputActionCount": 9,
            "inputKeyEventsSent": 4,
            "inputSendInputEventsSent": 0,
            "inputScanKeybdEventsSent": 4,
            "inputWindowMessageEventsSent": 0,
            "inputMouseEventsSent": 0,
        },
    }
    write_json(runtime_path, runtime)
    output = root / "level854-fire-damage-outcome-proof.json"
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
        require(summary["damageProof"] is False, "default fixture should not prove damage")
        require(summary["runtimeOutcomeProof"] is False, "default fixture should not prove outcome")
    with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
        summary = validate_bundle(make_fixture(Path(tmp), unit_damage=True, round_collision=True), allow_fixture=True)
        require(summary["damageProof"] is True, "unit damage fixture should prove damage")
        require(summary["runtimeOutcomeProof"] is False, "damage-only fixture should not prove outcome")
    with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
        summary = validate_bundle(make_fixture(Path(tmp), unit_damage=True, round_collision=True, outcome=True), allow_fixture=True)
        require(summary["damageProof"] is True and summary["runtimeOutcomeProof"] is True, "damage/outcome fixture should promote")
    for kwargs, label in (
        ({"no_button19": True}, "missing button 19"),
        ({"no_fire": True}, "missing fire"),
        ({"no_pointer_chain": True}, "missing pointer chain"),
        ({"external_cdb_log": True}, "external CDB log"),
        ({"wrong_command_file": True}, "wrong command file"),
    ):
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            try:
                path = make_fixture(Path(tmp), **kwargs)
                validate_bundle(path, allow_fixture=True)
            except (Level854FireDamageOutcomeError, builder.Level854FireDamageOutcomeBuildError):
                pass
            else:
                raise Level854FireDamageOutcomeError(f"{label} fixture should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof", nargs="?", type=Path, default=DEFAULT_PROOF)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("WinUI original-binary level854 fire/damage/outcome checker self-test: PASS")
        return 0
    if args.check:
        print(json.dumps(validate_repo(), indent=2, sort_keys=True))
        return 0
    print(json.dumps(validate_bundle(args.proof), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Level854FireDamageOutcomeError, builder.Level854FireDamageOutcomeBuildError) as exc:
        print(f"WinUI original-binary level854 fire/damage/outcome check: FAIL: {exc}")
        raise SystemExit(2)
