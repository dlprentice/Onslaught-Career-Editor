#!/usr/bin/env python3
"""Validate the level-850 P1/P2 mode-semantics observer proof."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import build_winui_original_binary_level850_mode_semantics_observer_bundle as builder


ROOT = Path(__file__).resolve().parents[1]
READINESS = ROOT / "release" / "readiness" / "original_binary_level850_mode_semantics_observer_2026-06-19.md"
FEASIBILITY = ROOT / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
FEASIBILITY_MIRROR = ROOT / "lore-book" / "roadmap" / "original-binary-online-multiplayer-feasibility.md"
LOCAL_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "local-multiplayer-static-runtime-contract.md"
LOCAL_CONTRACT_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "local-multiplayer-static-runtime-contract.md"
REGISTER = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
REGISTER_MIRROR = ROOT / "lore-book" / "roadmap" / "mod-patch-runtime-rebuild-register.md"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
CAPABILITIES_MIRROR = ROOT / "lore-book" / "CURRENT_CAPABILITIES.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
SCALABILITY = ROOT / "roadmap" / "original-binary-online-session-scalability-contract.v1.json"
MODE_CLASSIFIER = ROOT / "roadmap" / "original-binary-online-mode-classifier.v1.json"
CONTRACT = ROOT / "roadmap" / "original-binary-online-level850-mode-semantics-observer.v1.json"
PACKAGE_JSON = ROOT / "package.json"

EXPECTED_SCRIPT = (
    r"py -3 tools\build_winui_original_binary_level850_mode_semantics_observer_bundle.py && "
    r"py -3 tools\winui_safe_copy_online_level850_mode_semantics_observer_check_test.py && "
    r"py -3 tools\winui_safe_copy_online_level850_mode_semantics_observer_check.py --self-test && "
    r"py -3 tools\winui_safe_copy_online_level850_mode_semantics_observer_check.py --check"
)


class Level850ModeSemanticsObserverError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Level850ModeSemanticsObserverError(message)


def read_text(path: Path) -> str:
    require(path.is_file(), f"missing file: {path}")
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(read_text(path))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def resolve_source(path: Path, raw: str) -> Path:
    candidate = Path(raw)
    require(raw and not candidate.is_absolute(), f"source artifact reference must be relative: {raw}")
    resolved = (path.parent / candidate).resolve()
    require(resolved.is_file(), f"source artifact missing: {resolved}")
    return resolved


def require_source_artifacts(bundle: dict[str, Any], path: Path) -> None:
    artifacts = object_at(bundle, "sourceArtifacts")
    runtime_path = resolve_source(path, str(artifacts.get("liveRuntimeArtifact", "")))
    observer_file = resolve_source(path, str(artifacts.get("observerCommandFile", "")))
    require(artifacts.get("liveRuntimeArtifactSha256") == builder.sha256_file(runtime_path), "runtime artifact hash mismatch")
    runtime, log_path, parsed = builder.validate_runtime_artifact(runtime_path)
    require(artifacts.get("cdbLogSha256") == builder.sha256_file(log_path), "CDB log hash mismatch")
    require(observer_file == builder.OBSERVER_COMMAND_FILE.resolve(), "observer command file path mismatch")
    require(artifacts.get("observerCommandFileSha256") == builder.sha256_file(observer_file), "observer command hash mismatch")
    require(parsed["hookTargetCount"] == len(builder.TARGETS), "parsed hook target count mismatch")
    require(object_at(runtime, "source").get("installedHashUnchanged") is True, "runtime source hash boundary drifted")


def require_runtime_evidence(bundle: dict[str, Any]) -> dict[str, Any]:
    runtime = object_at(bundle, "runtimeEvidence")
    require(runtime.get("safeCopyLaunchLevel") == 850, "safe-copy launch level mismatch")
    require(runtime.get("controllerConfiguration") == 1, "controller configuration mismatch")
    require(runtime.get("newBeaLaunchCount") == 1, "fresh BEA launch count mismatch")
    require(runtime.get("cdbAttachCount") == 1, "CDB attach count mismatch")
    require(runtime.get("boundedCaptureCount") == 2, "bounded capture count mismatch")
    require(runtime.get("visualCaptureCount") == 2, "visual capture count mismatch")
    require(runtime.get("exactPidCdbObserverProven") is True, "exact-PID CDB observer flag missing")
    require(runtime.get("renderPlayers") == 2, "render player count mismatch")
    require(runtime.get("renderLevel") == 850, "render level mismatch")
    require(runtime.get("horizontalSplit") is True, "horizontal split flag missing")
    require(runtime.get("p1p2PointersDistinct") is True, "P1/P2 distinct pointer flag missing")
    require(runtime.get("sourceHashesUnchanged") is True, "source hash boundary missing")
    require(runtime.get("managedStopClean") is True, "managed stop boundary missing")
    return runtime


def require_mode_surface(bundle: dict[str, Any]) -> dict[str, Any]:
    surface = object_at(bundle, "modeSemanticsSurface")
    require(surface.get("modeSemanticsObserverProven") is True, "mode-semantics observer flag missing")
    require(surface.get("hookTargetCount") == len(builder.TARGETS), "hook target count mismatch")
    require(surface.get("expectedHookTargetCount") == len(builder.TARGETS), "expected hook target count mismatch")
    targets = surface.get("hookTargets")
    require(isinstance(targets, list) and len(targets) == len(builder.TARGETS), "hook target list mismatch")
    require([row.get("name") for row in targets if isinstance(row, dict)] == builder.TARGET_NAMES, "hook target names drifted")
    hit_counts = surface.get("hitCounts")
    require(isinstance(hit_counts, dict), "hit counts missing")
    require(hit_counts.get("CGame__Render", 0) >= 1, "CGame__Render must be observed")
    require(surface.get("unforcedTransitionTargets") == builder.UNFORCED_TRANSITION_TARGETS, "transition target list mismatch")
    require(surface.get("objectiveSurfaceTargets") == builder.OBJECTIVE_TARGETS, "objective target list mismatch")
    require(surface.get("forcedWinDeathRespawn") is False, "forced transition flag must remain false")
    require(surface.get("modeRuntimeProofSlicesAdded") == 0, "mode proof slice count must stay zero")
    require(surface.get("coOpVersusModeRuntimeProofSlicesAdded") == 0, "co-op/versus proof slice count must stay zero")
    require(surface.get("currentRuntimeModeClassification") == "unclassified-local-multiplayer", "classification must stay unclassified")
    return surface


def require_slot_and_nonclaims(bundle: dict[str, Any]) -> dict[str, Any]:
    slot = object_at(bundle, "slotBoundary")
    require(slot.get("acceptedOriginalBinaryGameplaySlots") == ["P1", "P2"], "accepted original-binary slots mismatch")
    require(slot.get("metadataOnlySlots") == ["P3", "P4"], "metadata-only slots mismatch")
    require(slot.get("rejectedGameplayRouteSlots") == ["P3", "P4"], "rejected slots mismatch")
    require(slot.get("maxOriginalBinaryActiveSlotsProven") == 2, "max active slots must stay two")
    require(slot.get("slotCapacity") == 4, "schema slot capacity must stay four")
    require(slot.get("nPlayerOriginalBinaryRuntimeProof") == 0, "N-player proof must stay zero")
    require(slot.get("activeP3P4OriginalBinaryGameplayProof") is False, "P3/P4 proof must stay false")
    require(slot.get("beyondTwoPlayersRequiresNewProofClass") is True, "beyond-two proof-class flag missing")
    nonclaims = object_at(bundle, "nonClaims")
    for key, value in nonclaims.items():
        require(value is False, f"non-claim must remain false: {key}")
    release = object_at(bundle, "releaseBoundary")
    require(release.get("privateProofReleaseExcludedByPolicy") is True, "private proof release boundary missing")
    for key, value in release.items():
        if key != "privateProofReleaseExcludedByPolicy":
            require(value is False, f"release boundary must remain false: {key}")
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
    require(bundle.get("observerScope") == builder.OBSERVER_SCOPE, "observer scope mismatch")
    require(bundle.get("runtimeProfile") == builder.RUNTIME_PROFILE, "runtime profile mismatch")
    require_source_artifacts(bundle, path)
    runtime = require_runtime_evidence(bundle)
    surface = require_mode_surface(bundle)
    nonclaims = require_slot_and_nonclaims(bundle)
    claim = str(bundle.get("claimBoundary", ""))
    for token in (
        "level-850/config-1 P1/P2 local split-screen mode-semantics observer",
        "observed the two-player render graph",
        "objective, win/loss, death, lives, and respawn paths",
        "does not force or prove win, death, respawn",
        "public matchmaking",
        "native BEA netcode",
        "active P3/P4 gameplay",
    ):
        require(token in claim, f"claim boundary missing token: {token}")
    return {
        "artifact": "<private-level850-mode-semantics-proof>",
        "schemaVersion": bundle["schemaVersion"],
        "observerScope": bundle["observerScope"],
        "newBeaLaunchCount": runtime["newBeaLaunchCount"],
        "cdbAttachCount": runtime["cdbAttachCount"],
        "boundedCaptureCount": runtime["boundedCaptureCount"],
        "visualCaptureCount": runtime["visualCaptureCount"],
        "renderPlayers": runtime["renderPlayers"],
        "renderLevel": runtime["renderLevel"],
        "hookTargetCount": surface["hookTargetCount"],
        "unforcedTransitionHitCount": surface["unforcedTransitionHitCount"],
        "objectiveSurfaceHitCount": surface["objectiveSurfaceHitCount"],
        "modeRuntimeProofSlicesAdded": surface["modeRuntimeProofSlicesAdded"],
        "currentRuntimeModeClassification": surface["currentRuntimeModeClassification"],
        "baseOnlineMultiplayerReady": nonclaims["baseOnlineMultiplayerReady"],
        "publicMatchmakingProof": nonclaims["publicMatchmakingProof"],
        "nativeBeaNetcodeProof": nonclaims["nativeBeaNetcodeProof"],
        "activeP3P4OriginalBinaryGameplayProof": nonclaims["activeP3P4OriginalBinaryGameplayProof"],
    }


def validate_contract_json() -> None:
    contract = read_json(CONTRACT)
    require(contract.get("schemaVersion") == builder.SCHEMA, "contract schema mismatch")
    require(contract.get("observerScope") == builder.OBSERVER_SCOPE, "contract observer scope mismatch")
    runtime = object_at(contract, "runtimeEvidence")
    require(runtime.get("newBeaLaunchCount") == 1, "contract launch count mismatch")
    require(runtime.get("cdbAttachCount") == 1, "contract CDB count mismatch")
    require(runtime.get("boundedCaptureCount") == 2, "contract bounded capture count mismatch")
    require(runtime.get("visualCaptureCount") == 2, "contract visual capture count mismatch")
    surface = object_at(contract, "modeSemanticsSurface")
    require(surface.get("hookTargetCount") == len(builder.TARGETS), "contract hook count mismatch")
    require(surface.get("modeRuntimeProofSlicesAdded") == 0, "contract must not add mode proof slices")
    require(surface.get("currentRuntimeModeClassification") == "unclassified-local-multiplayer", "contract classification mismatch")
    nonclaims = object_at(contract, "nonClaims")
    for key, value in nonclaims.items():
        require(value is False, f"contract non-claim must remain false: {key}")


def check_tokens(path: Path, tokens: tuple[str, ...], failures: list[str]) -> None:
    text = read_text(path)
    for token in tokens:
        if token not in text:
            failures.append(f"{path}: missing token {token!r}")


def validate_repo() -> None:
    failures: list[str] = []
    validate_contract_json()
    for path, tokens in {
        READINESS: (
            "Original Binary Level850 Mode Semantics Observer Readiness Note",
            builder.SCHEMA,
            builder.OBSERVER_SCOPE,
            "modeSemanticsObserverProven=true",
            f"hookTargetCount={len(builder.TARGETS)}",
            "newBeaLaunchCount=1",
            "cdbAttachCount=1",
            "boundedCaptureCount=2",
            "visualCaptureCount=2",
            "forcedWinDeathRespawn=false",
            "modeRuntimeProofSlicesAdded=0",
            "coOpVersusModeRuntimeProofSlicesAdded=0",
            "currentRuntimeModeClassification=unclassified-local-multiplayer",
            "baseOnlineMultiplayerReady=false",
            "publicMatchmakingProof=false",
            "nativeBeaNetcodeProof=false",
            "activeP3P4OriginalBinaryGameplayProof=false",
        ),
        FEASIBILITY: (
            "Level-850 P1/P2 mode-semantics observer",
            builder.OBSERVER_SCOPE,
            "modeSemanticsObserverProven=true",
            "forcedWinDeathRespawn=false",
            "modeRuntimeProofSlicesAdded=0",
            "currentRuntimeModeClassification=unclassified-local-multiplayer",
        ),
        LOCAL_CONTRACT: (
            "level-850 mode-semantics observer",
            builder.OBSERVER_SCOPE,
            f"hookTargetCount={len(builder.TARGETS)}",
            "forcedWinDeathRespawn=false",
            "modeRuntimeProofSlicesAdded=0",
        ),
        REGISTER: (
            "level-850 mode-semantics observer",
            "modeSemanticsObserverProven=true",
            "forcedWinDeathRespawn=false",
            "modeRuntimeProofSlicesAdded=0",
        ),
        CAPABILITIES: (
            "level-850 mode-semantics observer",
            "modeSemanticsObserverProven=true",
            "currentRuntimeModeClassification=unclassified-local-multiplayer",
            "baseOnlineMultiplayerReady=false",
        ),
        MAPPED_SYSTEMS: (
            "level-850 mode-semantics observer",
            "objective/win/death/respawn observer",
            "modeRuntimeProofSlicesAdded=0",
        ),
    }.items():
        check_tokens(path, tokens, failures)
    if read_text(FEASIBILITY) != read_text(FEASIBILITY_MIRROR):
        failures.append("online feasibility lore mirror mismatch")
    if read_text(LOCAL_CONTRACT) != read_text(LOCAL_CONTRACT_MIRROR):
        failures.append("local contract lore mirror mismatch")
    if read_text(REGISTER) != read_text(REGISTER_MIRROR):
        failures.append("register lore mirror mismatch")
    if read_text(CAPABILITIES) != read_text(CAPABILITIES_MIRROR):
        failures.append("capabilities lore mirror mismatch")
    if read_text(MAPPED_SYSTEMS) != read_text(MAPPED_SYSTEMS_MIRROR):
        failures.append("mapped systems lore mirror mismatch")
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    if scripts.get("test:winui-original-binary-level850-mode-semantics-observer") != EXPECTED_SCRIPT:
        failures.append("package level850 mode-semantics script mismatch")
    if "test:winui-original-binary-level850-mode-semantics-observer" not in str(scripts.get("test:winui-copied-profile-runtime", "")):
        failures.append("aggregate runtime script missing level850 mode-semantics observer")
    if not builder.DEFAULT_OUTPUT.is_file():
        failures.append(f"default level850 mode-semantics proof is missing: {builder.DEFAULT_OUTPUT}")
    if failures:
        raise Level850ModeSemanticsObserverError("\n".join(failures))


def make_fixture(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    log_path = root / "cdb" / "windbg.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    hook_lines = "\n".join(
        f"MODE_SEM_HOOK_TARGET name={target['name']} address={target['address']} category={target['category']}"
        for target in builder.TARGETS
    )
    log_path.write_text(
        hook_lines
        + "\nMODE_SEM_HIT name=CGame__Render this=008a9a98 players=2 level=850 horizSplit=1 "
        + "p0=04646090 p1=0465d890 cam0=046d97f0 cam1=046d98a0 world=038c0840\n",
        encoding="utf-8",
    )
    runtime_path = root / "live-safe-copy-runtime-smoke.json"
    runtime_path.write_text(
        json.dumps(
            {
                "schemaVersion": "winui-safe-copy-live-runtime-smoke.v1",
                "source": {
                    "installedHashUnchanged": True,
                    "overrideHashUnchanged": True,
                    "saveAndOptions": {"unchanged": True},
                },
                "launch": {"arguments": ["-skipfmv", "-level", "850", "-configuration", "1"]},
                "processBaseline": {"noPreexistingBea": True, "noBeaAfterStop": True},
                "stop": {"Success": True},
                "captures": [
                    {"status": "captured", "visualProof": True},
                    {"status": "captured", "visualProof": True},
                ],
                "cdbObserver": {
                    "enabled": True,
                    "result": {"status": "attached", "logExists": True, "logPath": str(log_path)},
                    "cleanup": {"status": "stopped"},
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    output = root / "level850-mode-semantics-observer-proof.json"
    builder.build_bundle_from_runtime(runtime_path, output)
    return output


def run_self_test() -> None:
    builder.PRIVATE_PROOF_ROOT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
        path = make_fixture(Path(tmp))
        summary = validate_bundle(path, allow_fixture=True)
        require(summary["hookTargetCount"] == len(builder.TARGETS), "fixture hook target mismatch")
        require(summary["baseOnlineMultiplayerReady"] is False, "fixture online boundary mismatch")

    for name, mutate in (
        ("online-ready claim should fail", lambda value: value["nonClaims"].__setitem__("baseOnlineMultiplayerReady", True)),
        ("mode runtime proof count should fail", lambda value: value["modeSemanticsSurface"].__setitem__("modeRuntimeProofSlicesAdded", 1)),
        ("forced transition claim should fail", lambda value: value["modeSemanticsSurface"].__setitem__("forcedWinDeathRespawn", True)),
        ("P3/P4 runtime claim should fail", lambda value: value["slotBoundary"].__setitem__("activeP3P4OriginalBinaryGameplayProof", True)),
        ("native netcode claim should fail", lambda value: value["nonClaims"].__setitem__("nativeBeaNetcodeProof", True)),
        ("public matchmaking claim should fail", lambda value: value["nonClaims"].__setitem__("publicMatchmakingProof", True)),
        ("wrong render player count should fail", lambda value: value["runtimeEvidence"].__setitem__("renderPlayers", 4)),
    ):
        with tempfile.TemporaryDirectory(dir=builder.PRIVATE_PROOF_ROOT) as tmp:
            path = make_fixture(Path(tmp))
            payload = read_json(path)
            mutate(payload)
            write_json(path, payload)
            try:
                validate_bundle(path, allow_fixture=True)
            except Level850ModeSemanticsObserverError:
                continue
            raise Level850ModeSemanticsObserverError(name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        run_self_test()
        print("WinUI original-binary level850 mode-semantics observer checker self-test: PASS")
        return 0
    if args.check:
        validate_repo()
        print(json.dumps(validate_bundle(builder.DEFAULT_OUTPUT), indent=2, sort_keys=True))
        return 0
    if args.bundle is None:
        raise SystemExit("bundle is required unless --self-test or --check is used")
    print(json.dumps(validate_bundle(args.bundle), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        Level850ModeSemanticsObserverError,
        builder.Level850ModeSemanticsBuildError,
    ) as exc:
        print(f"WinUI original-binary level850 mode-semantics observer check: FAIL: {exc}")
        raise SystemExit(2)
