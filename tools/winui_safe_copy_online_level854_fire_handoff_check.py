#!/usr/bin/env python3
"""Validate the level-854 fire/input-to-weapon-handoff proof bundle."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import build_winui_original_binary_level854_fire_handoff_bundle as builder


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROOF = builder.DEFAULT_OUTPUT
PUBLIC_JSON = ROOT / "roadmap" / "original-binary-online-level854-fire-handoff.v1.json"
READINESS_NOTE = ROOT / "release" / "readiness" / "original_binary_level854_fire_handoff_2026-06-19.md"
CAPABILITIES_DOC = ROOT / "CURRENT_CAPABILITIES.md"
FEASIBILITY_DOC = ROOT / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
REGISTER_DOC = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
CONTRACT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "local-multiplayer-static-runtime-contract.md"
PACKAGE_JSON = ROOT / "package.json"
CLASSIFICATION_TSV = ROOT / "roadmap" / "release-allowlist-classification.tsv"
PUBLIC_ALLOWLIST_TSV = ROOT / "release" / "readiness" / "public_candidate_allowlist.tsv"
PRIVATE_INVENTORY_TSV = ROOT / "release" / "readiness" / "private_only_inventory.tsv"
RELEASE_PROFILE_DOC = ROOT / "roadmap" / "release-allowlist-profile.md"

PUBLIC_REQUIRED_FALSE_TOKENS = (
    "button18RuntimeDispatchObserved=false",
    "button19RuntimeDispatchObserved=true",
    "sameWindowFireBurstPointerChainWindowCount=1",
    "sameWindowFireBurstPointerChainObserved=true",
    "sameWindowOrderedFireBurstPointerChainWindowCount=0",
    "sameWindowOrderedFireBurstPointerChainObserved=false",
    "runtimeOutcomeProof=false",
    "roundProjectileCausalityProof=false",
    "baseOnlineMultiplayerReady=false",
    "publicMatchmakingProof=false",
    "nativeBeaNetcodeProof=false",
    "activeP3P4OriginalBinaryGameplayProof=false",
)
PUBLIC_FORBIDDEN_TRUE_TOKENS = (
    "button18RuntimeDispatchObserved=true",
    "runtimeOutcomeProof=true",
    "roundProjectileCausalityProof=true",
    "baseOnlineMultiplayerReady=true",
    "publicMatchmakingProof=true",
    "multiHostLanProof=true",
    "nativeBeaNetcodeProof=true",
    "activeP3P4OriginalBinaryGameplayProof=true",
)
PUBLIC_RELEASE_ALLOW_ROWS = (
    "roadmap/original-binary-online-level854-fire-handoff.v1.json\tR0_ALLOW",
    "tools/runtime-probes/local-multiplayer-level854-fire-handoff-observer.cdb.txt\tR0_ALLOW",
)
PRIVATE_RELEASE_DENY_ROWS = (
    "tools/build_winui_original_binary_level854_fire_handoff_bundle.py\tR4_DENY",
    "tools/winui_safe_copy_online_level854_fire_handoff_check.py\tR4_DENY",
    "tools/winui_safe_copy_online_level854_fire_handoff_check_test.py\tR4_DENY",
)
PUBLIC_RUNTIME_POINTER_KEYS = {"p1Pointer", "p2Pointer", "runtimePointer", "rawRuntimePointer"}
PUBLIC_PRIVATE_PATH_MARKERS = ("C:\\", "C:/", "/Users/", "subagents/", "AppData", "G:\\", "G:/")


class Level854FireHandoffError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Level854FireHandoffError(message)


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
    except builder.Level854FireHandoffBuildError as exc:
        raise Level854FireHandoffError(str(exc)) from exc
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


def require_fire_binding(bundle: dict[str, Any]) -> dict[str, Any]:
    binding = object_at(bundle, "fireBinding")
    require(binding.get("copiedDefaultOptionsFireWeaponQe") is True, "copied defaultoptions fire Q/E flag missing")
    require(binding.get("controlOptionsProofLever") == "copied-defaultoptions-weapon-fire-qe", "wrong proof lever")
    require(binding.get("sourceExpectedFireButton") == 18, "source expected fire button mismatch")
    require(binding.get("observedRuntimeFireButton") == 19, "observed runtime fire button mismatch")
    require(binding.get("button18DispatchCount") == 0, "button 18 dispatch must remain absent in this proof")
    require(int(binding.get("button19DispatchCount", 0)) > 0, "button 19 dispatch must be observed")
    require(binding.get("button18RuntimeDispatchObserved") is False, "button 18 overclaim")
    require(binding.get("button19RuntimeDispatchObserved") is True, "button 19 observed flag missing")
    require(binding.get("expectedSourceButton18NotRuntimeObserved") is True, "button 18 caveat missing")
    return binding


def require_fire_handoff(bundle: dict[str, Any], parsed: dict[str, Any], parsed_windows: list[dict[str, Any]]) -> dict[str, Any]:
    handoff = object_at(bundle, "fireHandoff")
    windows = list_at(handoff, "inputWindowSummaries")
    require(windows == parsed_windows, "input window summaries must match parsed CDB windows")
    require(handoff.get("inputWindowCount") == len(windows), "input window count mismatch")
    stimulus_count = len([row for row in windows if isinstance(row, dict) and row.get("stimulusWindow") is True])
    wait_count = len([row for row in windows if isinstance(row, dict) and row.get("stimulusWindow") is False])
    positive_count = len([row for row in windows if isinstance(row, dict) and row.get("sameWindowInputFireHandoff") is True])
    wait_button_count = sum(int(row.get("button19DispatchCount", 0)) for row in windows if isinstance(row, dict) and row.get("stimulusWindow") is False)
    same_window_battleengine_projectile = any(
        isinstance(row, dict) and row.get("sameWindowBattleEngineProjectile") is True for row in windows
    )
    same_window_shell_materialization = any(
        isinstance(row, dict) and row.get("sameWindowShellMaterialization") is True for row in windows
    )
    same_window_projectile_factory = any(
        isinstance(row, dict) and row.get("sameWindowProjectileFactory") is True for row in windows
    )
    same_window_round_projectile = any(
        isinstance(row, dict) and row.get("sameWindowRoundProjectileCausality") is True for row in windows
    )
    same_window_fire_burst_pointer_chain = [
        row for row in windows if isinstance(row, dict) and row.get("sameWindowFireBurstPointerChain") is True
    ]
    same_window_ordered_fire_burst_pointer_chain = [
        row for row in windows if isinstance(row, dict) and row.get("sameWindowOrderedFireBurstPointerChain") is True
    ]
    pointer_chain_contexts = sorted(
        {
            context
            for row in same_window_fire_burst_pointer_chain
            for context in object_at(row, "fireBurstPointerChain").get("correlatedWeaponBurstContexts", [])
        },
        key=lambda item: int(str(item), 16),
    )
    round_definition_correlation = any(
        isinstance(row, dict) and object_at(row, "fireBurstPointerChain").get("roundDefinitionCorrelationObserved") is True
        for row in windows
    )
    require(stimulus_count > 0, "no stimulus windows recorded")
    require(wait_count > 0, "no wait/no-input controls recorded")
    require(handoff.get("stimulusWindowCount") == stimulus_count, "stimulus window count mismatch")
    require(handoff.get("waitControlWindowCount") == wait_count, "wait window count mismatch")
    require(handoff.get("sameWindowInputFireHandoffWindowCount") == positive_count, "positive handoff window count mismatch")
    require(handoff.get("sameWindowInputFireHandoffObserved") is (positive_count > 0), "positive handoff flag mismatch")
    require(positive_count > 0, "fire handoff proof needs same-window input plus handoff hits")
    require(
        handoff.get("sameWindowFireBurstPointerChainWindowCount") == len(same_window_fire_burst_pointer_chain),
        "same-window fire/burst pointer-chain count mismatch",
    )
    require(
        handoff.get("sameWindowFireBurstPointerChainObserved") is bool(same_window_fire_burst_pointer_chain),
        "same-window fire/burst pointer-chain flag mismatch",
    )
    require(same_window_fire_burst_pointer_chain, "fire handoff proof needs same-window pointer-correlated fire/burst chain")
    require(
        handoff.get("sameWindowOrderedFireBurstPointerChainWindowCount")
        == len(same_window_ordered_fire_burst_pointer_chain),
        "same-window ordered fire/burst pointer-chain count mismatch",
    )
    require(
        handoff.get("sameWindowOrderedFireBurstPointerChainObserved") is bool(same_window_ordered_fire_burst_pointer_chain),
        "same-window ordered fire/burst pointer-chain flag mismatch",
    )
    require(
        handoff.get("fireBurstPointerChainContexts") == pointer_chain_contexts,
        "fire/burst pointer-chain context list mismatch",
    )
    ordered_pointer_chain_contexts = sorted(
        {
            context
            for row in same_window_ordered_fire_burst_pointer_chain
            for context in object_at(row, "fireBurstPointerChain").get("orderedCorrelatedWeaponBurstContexts", [])
        },
        key=lambda item: int(str(item), 16),
    )
    require(
        handoff.get("orderedFireBurstPointerChainContexts", []) == ordered_pointer_chain_contexts,
        "ordered fire/burst pointer-chain context list mismatch",
    )
    require(handoff.get("waitWindowFireButtonDispatchCount") == wait_button_count == 0, "wait windows must not dispatch fire input")
    require(handoff.get("waitWindowCausalProof") is False, "wait windows cannot be causal proof")
    require(handoff.get("battleEngineProjectileTotalHitCount") == parsed["battleEngineProjectileHitCount"], "BattleEngine projectile total mismatch")
    require(handoff.get("shellMaterializationTotalHitCount") == parsed["shellMaterializationHitCount"], "shell materialization total mismatch")
    require(handoff.get("projectileFactoryTotalHitCount") == parsed["projectileFactoryHitCount"], "projectile factory total mismatch")
    require(handoff.get("roundProjectileTotalHitCount") == parsed["roundProjectileHitCount"], "round projectile total mismatch")
    require(
        handoff.get("sameWindowBattleEngineProjectileObserved") is same_window_battleengine_projectile,
        "same-window BattleEngine projectile flag mismatch",
    )
    require(
        handoff.get("sameWindowShellMaterializationObserved") is same_window_shell_materialization,
        "same-window shell materialization flag mismatch",
    )
    require(
        handoff.get("sameWindowProjectileFactoryObserved") is same_window_projectile_factory,
        "same-window projectile factory flag mismatch",
    )
    require(
        handoff.get("roundProjectileSameWindowCoincidenceObserved") is same_window_round_projectile,
        "same-window round projectile coincidence flag mismatch",
    )
    require(
        handoff.get("roundDefinitionCorrelationObserved") is round_definition_correlation,
        "round-definition correlation flag mismatch",
    )
    require(handoff.get("roundProjectileSameWindowCausalityProof") is False, "round/projectile causality must not be promoted")
    return handoff


def require_handoff_surface(bundle: dict[str, Any], parsed: dict[str, Any]) -> dict[str, Any]:
    surface = object_at(bundle, "handoffSurface")
    require(surface.get("hookTargetCount") == parsed["hookTargetCount"], "hook target count mismatch")
    require(surface.get("expectedHookTargetCount") == len(builder.TARGETS), "expected hook target count mismatch")
    require(surface.get("hitCounts") == parsed["hitCounts"], "hit counts mismatch")
    require(surface.get("buttonCounts") == parsed["buttonCounts"], "button counts mismatch")
    require(surface.get("directFireDispatchHitCount") == parsed["directFireDispatchHitCount"], "direct fire hit count mismatch")
    require(surface.get("burstOrProjectilePresetHitCount") == parsed["burstOrProjectilePresetHitCount"], "burst hit count mismatch")
    require(surface.get("battleEngineProjectileHitCount") == parsed["battleEngineProjectileHitCount"], "BattleEngine projectile hit count mismatch")
    require(surface.get("shellMaterializationHitCount") == parsed["shellMaterializationHitCount"], "shell materialization hit count mismatch")
    require(surface.get("projectileFactoryHitCount") == parsed["projectileFactoryHitCount"], "projectile factory hit count mismatch")
    require(surface.get("roundProjectileHitCount") == parsed["roundProjectileHitCount"], "round hit count mismatch")
    require(surface.get("modeRuntimeProofSlicesAdded") == 0, "mode proof count must stay zero")
    require(surface.get("coOpVersusModeRuntimeProofSlicesAdded") == 0, "co-op/versus proof count must stay zero")
    require(surface.get("currentRuntimeModeClassification") == "unclassified-local-multiplayer", "mode classification must stay unclassified")
    return surface


def require_boundaries(bundle: dict[str, Any]) -> dict[str, Any]:
    slot = object_at(bundle, "slotBoundary")
    require(slot.get("acceptedOriginalBinaryGameplaySlots") == ["P1", "P2"], "accepted slots mismatch")
    require(slot.get("metadataOnlySlots") == ["P3", "P4"], "metadata-only slots mismatch")
    require(slot.get("activeP3P4OriginalBinaryGameplayProof") is False, "P3/P4 proof must stay false")
    require(slot.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player runtime proof must stay zero")
    nonclaims = object_at(bundle, "nonClaims")
    for key, value in nonclaims.items():
        require(value is False, f"non-claim must remain false: {key}")
    return nonclaims


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
    _runtime_artifact, parsed, windows = require_source_artifacts(bundle, path)
    receipt = object_at(bundle, "executionReceipt")
    if not allow_fixture:
        require(receipt.get("freshLiveExecution") is True, "default proof must come from fresh live execution")
        require(str(receipt.get("runtimeArtifactRootName", "")).startswith("level854-fire-handoff-live-"), "runtime artifact root must be fresh fire-handoff live root")
    runtime = require_runtime_evidence(bundle, parsed)
    binding = require_fire_binding(bundle)
    handoff = require_fire_handoff(bundle, parsed, windows)
    surface = require_handoff_surface(bundle, parsed)
    nonclaims = require_boundaries(bundle)
    claim = str(bundle.get("claimBoundary", ""))
    for token in (
        "fire-input-to-weapon-handoff",
        "pointer-correlated WeaponFired.weapon",
        "button18RuntimeDispatchObserved=false",
        "button19RuntimeDispatchObserved=true",
        "Wait-window burst or handoff hits are ambient",
        "not base online multiplayer",
        "not native BEA netcode",
        "not runtime outcome/damage/kill proof",
        "not active P3/P4 gameplay",
    ):
        require(token in claim, f"claim boundary missing token: {token}")
    return {
        "artifact": "<private-level854-fire-handoff-proof>",
        "schemaVersion": bundle["schemaVersion"],
        "proofScope": bundle["proofScope"],
        "newBeaLaunchCount": runtime["newBeaLaunchCount"],
        "cdbAttachCount": runtime["cdbAttachCount"],
        "boundedCaptureCount": runtime["boundedCaptureCount"],
        "visualCaptureCount": runtime["visualCaptureCount"],
        "button18DispatchCount": binding["button18DispatchCount"],
        "button19DispatchCount": binding["button19DispatchCount"],
        "sameWindowInputFireHandoffWindowCount": handoff["sameWindowInputFireHandoffWindowCount"],
        "sameWindowFireBurstPointerChainWindowCount": handoff["sameWindowFireBurstPointerChainWindowCount"],
        "sameWindowOrderedFireBurstPointerChainWindowCount": handoff["sameWindowOrderedFireBurstPointerChainWindowCount"],
        "sameWindowOrderedFireBurstPointerChainObserved": handoff["sameWindowOrderedFireBurstPointerChainObserved"],
        "fireBurstPointerChainContexts": handoff["fireBurstPointerChainContexts"],
        "orderedFireBurstPointerChainContexts": handoff["orderedFireBurstPointerChainContexts"],
        "waitWindowFireButtonDispatchCount": handoff["waitWindowFireButtonDispatchCount"],
        "roundProjectileTotalHitCount": handoff["roundProjectileTotalHitCount"],
        "battleEngineProjectileTotalHitCount": handoff["battleEngineProjectileTotalHitCount"],
        "shellMaterializationTotalHitCount": handoff["shellMaterializationTotalHitCount"],
        "projectileFactoryTotalHitCount": handoff["projectileFactoryTotalHitCount"],
        "sameWindowBattleEngineProjectileObserved": handoff["sameWindowBattleEngineProjectileObserved"],
        "sameWindowShellMaterializationObserved": handoff["sameWindowShellMaterializationObserved"],
        "sameWindowProjectileFactoryObserved": handoff["sameWindowProjectileFactoryObserved"],
        "roundProjectileCausalityProof": nonclaims["roundProjectileCausalityProof"],
        "directFireDispatchHitCount": surface["directFireDispatchHitCount"],
        "burstOrProjectilePresetHitCount": surface["burstOrProjectilePresetHitCount"],
        "battleEngineProjectileHitCount": surface["battleEngineProjectileHitCount"],
        "shellMaterializationHitCount": surface["shellMaterializationHitCount"],
        "projectileFactoryHitCount": surface["projectileFactoryHitCount"],
        "baseOnlineMultiplayerReady": nonclaims["baseOnlineMultiplayerReady"],
        "nativeBeaNetcodeProof": nonclaims["nativeBeaNetcodeProof"],
        "activeP3P4OriginalBinaryGameplayProof": nonclaims["activeP3P4OriginalBinaryGameplayProof"],
    }


def require_public_claim_tokens(text: str, label: str, required_tokens: tuple[str, ...] = PUBLIC_REQUIRED_FALSE_TOKENS) -> None:
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


def require_public_json_release_boundary(value: Any, *, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            require(key not in PUBLIC_RUNTIME_POINTER_KEYS, f"public JSON publishes raw runtime pointer field: {child_path}")
            lowered = key.lower()
            if ("pid" in lowered or lowered.endswith("processid")) and not isinstance(child, bool):
                raise Level854FireHandoffError(f"public JSON publishes raw runtime PID/process field: {child_path}")
            if "logpath" in lowered and not isinstance(child, bool):
                raise Level854FireHandoffError(f"public JSON publishes raw CDB/log path field: {child_path}")
            require_public_json_release_boundary(child, path=child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            require_public_json_release_boundary(child, path=f"{path}[{index}]")
    elif isinstance(value, str):
        normalized = value.replace("\\", "/")
        for marker in PUBLIC_PRIVATE_PATH_MARKERS:
            require(marker.replace("\\", "/") not in normalized, f"public JSON publishes private path-like value at {path}")


def validate_repo() -> dict[str, Any]:
    summary = validate_bundle(DEFAULT_PROOF)
    package_text = read_text(PACKAGE_JSON)
    for token in (
        "test:winui-original-binary-level854-fire-handoff",
        "build_winui_original_binary_level854_fire_handoff_bundle.py",
        "winui_safe_copy_online_level854_fire_handoff_check_test.py",
        "winui_safe_copy_online_level854_fire_handoff_check.py --self-test",
        "winui_safe_copy_online_level854_fire_handoff_check.py --check",
    ):
        require(token in package_text, f"package script missing token: {token}")

    public_json = read_json(PUBLIC_JSON)
    require_public_json_release_boundary(public_json)
    require(public_json.get("proofScope") == builder.SCOPE, "public JSON proof scope mismatch")
    binding = object_at(public_json, "fireBinding")
    handoff = object_at(public_json, "fireHandoff")
    nonclaims = object_at(public_json, "nonClaims")
    release_boundary = object_at(public_json, "releaseBoundary")
    claim_boundary = str(public_json.get("claimBoundary", ""))
    require(binding.get("button18RuntimeDispatchObserved") is False, "public JSON button 18 overclaim")
    require(binding.get("button19RuntimeDispatchObserved") is True, "public JSON button 19 flag missing")
    require(int(binding.get("button19DispatchCount", 0)) > 0, "public JSON button 19 count missing")
    require(handoff.get("sameWindowInputFireHandoffObserved") is True, "public JSON fire handoff flag missing")
    require(
        handoff.get("sameWindowFireBurstPointerChainWindowCount", 0) > 0,
        "public JSON fire/burst pointer-chain count missing",
    )
    require(
        handoff.get("sameWindowFireBurstPointerChainObserved") is True,
        "public JSON fire/burst pointer-chain flag missing",
    )
    require(
        handoff.get("sameWindowOrderedFireBurstPointerChainWindowCount") == 0,
        "public JSON ordered fire/burst pointer-chain count must stay zero until proven",
    )
    require(
        handoff.get("sameWindowOrderedFireBurstPointerChainObserved") is False,
        "public JSON ordered fire/burst pointer-chain must stay false until proven",
    )
    require("fireBurstPointerChainContexts" not in handoff, "public JSON must not publish raw runtime pointer contexts")
    require("orderedFireBurstPointerChainContexts" not in handoff, "public JSON must not publish raw ordered pointer contexts")
    require(
        handoff.get("fireBurstPointerChainContextCount", 0) == handoff.get("sameWindowFireBurstPointerChainWindowCount", 0),
        "public JSON fire/burst pointer-chain context count mismatch",
    )
    require(handoff.get("waitWindowCausalProof") is False, "public JSON wait-window causality overclaim")
    require(handoff.get("roundProjectileSameWindowCausalityProof") is False, "public JSON round causality overclaim")
    for token in (
        "not runtime outcome proof",
        "not online multiplayer",
        "not native BEA netcode",
        "not active P3/P4 gameplay",
        "not round/projectile causality proof",
    ):
        require(token in claim_boundary, f"public JSON claim boundary missing token: {token}")
    for key in (
        "baseOnlineMultiplayerReady",
        "secondPhysicalHostProof",
        "multiHostLanProof",
        "publicMatchmakingProof",
        "nativeBeaNetcodeProof",
        "coOpModeRuntimeProof",
        "versusModeRuntimeProof",
        "activeP3P4OriginalBinaryGameplayProof",
        "runtimeOutcomeProof",
        "damageProof",
        "killProof",
        "roundProjectileCausalityProof",
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
        require("fire-handoff" in text or "fire handoff" in text, f"{label} missing fire-handoff reference")
        require("button 19" in text or "button19" in text, f"{label} missing button 19 caveat")
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
    button18_dispatch: bool = False,
    no_direct_fire: bool = False,
    no_burst: bool = False,
    mismatched_burst_context: bool = False,
    unordered_fire_burst_events: bool = False,
    wait_window_button: bool = False,
    background_window_messages: bool = False,
    external_cdb_log: bool = False,
    wrong_command_file: bool = False,
    overclaim_online: bool = False,
) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    cdb_root = root / "cdb"
    cdb_root.mkdir(parents=True, exist_ok=True)
    log_path = Path(tempfile.gettempdir()) / "level854-fire-handoff-external-cdb.log" if external_cdb_log else cdb_root / "fixture-cdb.log"
    chunks: list[str] = []
    prelude = [
        ".echo === fixture ===\n",
        *[
            f"FIRE_HANDOFF_HOOK_TARGET name={target['name']} address={target['address']} category={target['category']}\n"
            for target in builder.TARGETS
        ],
        "FIRE_HANDOFF_HIT name=CGame__Render this=008a9a98 players=2 level=854 horizSplit=1 p0=0467c090 p1=04693890 cam0=04111111 cam1=04222222 world=00855090\n",
    ]
    chunks.append("".join(prelude))
    windows: list[dict[str, Any]] = []
    cursor = len("".join(chunks).encode("utf-8"))
    for index, sequence in enumerate(builder.INPUT_SEQUENCES, start=1):
        body = ""
        stimulus = not builder.is_wait_only_sequence(sequence)
        if wait_window_button and not stimulus and index == 1:
            body += "FIRE_HANDOFF_HIT name=CController__SendButtonAction controller=00112233 button=19 analogRaw=00000000 inputDevice=00000000 controllerConfig=00000001 target=0467c090\n"
        if stimulus and not no_button19:
            body += "FIRE_HANDOFF_HIT name=CController__SendButtonAction controller=00112233 button=19 analogRaw=00000000 inputDevice=00000000 controllerConfig=00000001 target=0467c090\n"
            body += "FIRE_HANDOFF_HIT name=CPlayer__ReceiveButtonAction player=0467c090 fromController=00112233 button=19 analogRaw=00000000 gameP0=0467c090 gameP1=04693890 be=04770000 state098=00000000 state260=00000002\n"
        if stimulus and button18_dispatch:
            body += "FIRE_HANDOFF_HIT name=CController__SendButtonAction controller=00112233 button=18 analogRaw=00000000 inputDevice=00000000 controllerConfig=00000001 target=0467c090\n"
        if stimulus and not no_direct_fire:
            body += "FIRE_HANDOFF_HIT name=CBattleEngineWalkerPart__FireWeapon this=04770000\n"
            if unordered_fire_burst_events:
                deferred_weapon_fired = "FIRE_HANDOFF_HIT name=CBattleEngineWalkerPart__WeaponFired this=04770000 weapon=04990000\n"
            else:
                body += "FIRE_HANDOFF_HIT name=CBattleEngineWalkerPart__WeaponFired this=04770000 weapon=04990000\n"
        else:
            deferred_weapon_fired = ""
        if stimulus and not no_burst:
            burst_context = "04990010" if mismatched_burst_context else "04990000"
            projectile_context = "04990020" if mismatched_burst_context else burst_context
            body += f"FIRE_HANDOFF_HIT name=CWeapon__HandleFireBurstEvent this={burst_context} eventRecord=05000000 eventHeadRaw={burst_context}\n"
            body += f"FIRE_HANDOFF_HIT name=ProjectileBurst__SpawnFromCurrentPreset burstContext={projectile_context}\n"
            body += deferred_weapon_fired
        if not stimulus and index == 3:
            body += "FIRE_HANDOFF_HIT name=CWeapon__HandleFireBurstEvent this=04990000 eventRecord=05000000 eventHeadRaw=00001389\n"
        start = cursor
        end = start + len(body.encode("utf-8"))
        windows.append({"index": index, "sequence": sequence, "logPath": str(log_path), "logStartByte": start, "logEndByte": end})
        chunks.append(body)
        cursor = end
    log_path.write_bytes("".join(chunks).encode("utf-8"))
    command_file = ROOT / "tools" / "runtime-probes" / "local-multiplayer-level854-outcome-semantics-observer.cdb.txt" if wrong_command_file else builder.COMMAND_FILE
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
    output = root / "level854-fire-handoff-proof.json"
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
    if overclaim_online:
        bundle = read_json(output)
        bundle["nonClaims"]["baseOnlineMultiplayerReady"] = True
        write_json(output, bundle)
    return output


def self_test() -> None:
    builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
        summary = validate_bundle(make_fixture(Path(tmp)), allow_fixture=True)
        require(summary["button19DispatchCount"] > 0, "default fixture should observe button 19")
        require(summary["sameWindowInputFireHandoffWindowCount"] > 0, "default fixture should prove handoff")
    for kwargs, label in (
        ({"no_button19": True}, "missing button 19"),
        ({"button18_dispatch": True}, "button 18 overclaim"),
        ({"no_direct_fire": True}, "missing direct fire"),
        ({"no_burst": True}, "missing burst"),
        ({"mismatched_burst_context": True}, "mismatched fire/burst pointer chain"),
        ({"wait_window_button": True}, "wait-window button dispatch"),
        ({"external_cdb_log": True}, "external CDB log"),
        ({"wrong_command_file": True}, "wrong command file"),
    ):
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            try:
                path = make_fixture(Path(tmp), **kwargs)
                validate_bundle(path, allow_fixture=True)
            except (Level854FireHandoffError, builder.Level854FireHandoffBuildError):
                pass
            else:
                raise Level854FireHandoffError(f"{label} fixture should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("proof", nargs="?", type=Path, default=DEFAULT_PROOF)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        print("WinUI original-binary level854 fire-handoff checker self-test: PASS")
        return 0
    if args.check:
        print(json.dumps(validate_repo(), indent=2, sort_keys=True))
        return 0
    print(json.dumps(validate_bundle(args.proof), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (Level854FireHandoffError, builder.Level854FireHandoffBuildError) as exc:
        print(f"WinUI original-binary level854 fire-handoff check: FAIL: {exc}")
        raise SystemExit(2)
