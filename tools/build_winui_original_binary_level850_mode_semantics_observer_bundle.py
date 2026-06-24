#!/usr/bin/env python3
"""Build a private level-850 P1/P2 mode-semantics observer proof bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_PROOF_ROOT = ROOT / "subagents" / "winui-safe-copy-live-runtime"
DEFAULT_ARTIFACT_ROOT = PRIVATE_PROOF_ROOT / "level850-mode-semantics-observer-20260619"
DEFAULT_OUTPUT = DEFAULT_ARTIFACT_ROOT / "level850-mode-semantics-observer-proof.json"
DEFAULT_RUNTIME_ARTIFACT = DEFAULT_ARTIFACT_ROOT / "live-safe-copy-runtime-smoke.json"
DEFAULT_GAME_ROOT = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila")
DEFAULT_EXE_OVERRIDE = DEFAULT_GAME_ROOT / "BEA.exe.original.backup"
OBSERVER_COMMAND_FILE = ROOT / "tools" / "runtime-probes" / "local-multiplayer-level850-mode-semantics-observer.cdb.txt"

SCHEMA = "winui-original-binary-level850-mode-semantics-observer.v1"
PROTOCOL = "level850-mode-semantics-observer.v1"
HELPER = "winui-original-binary-level850-mode-semantics-observer"
HELPER_VERSION = "level850-mode-semantics-observer.v1"
OBSERVER_SCOPE = "level850-p1p2-mode-semantics-observer-not-coop-versus-proof"
RUNTIME_PROFILE = "original-binary-copied-local-splitscreen"
EXPECTED_ACTIVE_SLOTS = ["P1", "P2"]
EXPECTED_METADATA_SLOTS = ["P3", "P4"]

TARGETS: tuple[dict[str, str], ...] = (
    {"name": "CGame__IsMultiplayer", "address": "0x004725d0", "category": "multiplayer-level-gate"},
    {"name": "CWorld__IsMultiplayerMode", "address": "0x0050d7d0", "category": "world-multiplayer-mode"},
    {"name": "CGame__Render", "address": "0x0046e460", "category": "p1p2-render-graph"},
    {"name": "CGame__GetPlayerLives", "address": "0x004725f0", "category": "lives-surface"},
    {"name": "CGame__DeclarePlayerDead", "address": "0x0046f550", "category": "death-transition"},
    {"name": "CGame__RespawnPlayer", "address": "0x00470120", "category": "respawn-transition"},
    {"name": "CGame__MPDeclarePlayerWon", "address": "0x0046f360", "category": "multiplayer-win-transition"},
    {"name": "CGame__MPDeclareGameDrawn", "address": "0x0046f3e0", "category": "multiplayer-draw-transition"},
    {"name": "CGame__DeclareLevelWon", "address": "0x0046f2f0", "category": "level-win-transition"},
    {"name": "CGame__DeclareLevelLost", "address": "0x0046f430", "category": "level-loss-transition"},
    {"name": "CGame__FillOutEndLevelData", "address": "0x0046d470", "category": "end-level-snapshot"},
    {"name": "CGame__GetNumPrimaryObjectives", "address": "0x00472670", "category": "objective-count"},
    {"name": "CGame__GetNumSecondaryObjectives", "address": "0x00472690", "category": "objective-count"},
    {"name": "CEndLevelData__IsAllSecondaryObjectivesComplete", "address": "0x004496e0", "category": "secondary-objective-predicate"},
    {"name": "IScript__PrimaryObjectiveComplete", "address": "0x005343e0", "category": "mission-objective-handler"},
    {"name": "IScript__SecondaryObjectiveComplete", "address": "0x00534410", "category": "mission-objective-handler"},
    {"name": "IScript__PrimaryObjectiveFailed", "address": "0x00534440", "category": "mission-objective-handler"},
    {"name": "IScript__SecondaryObjectiveFailed", "address": "0x00534470", "category": "mission-objective-handler"},
    {"name": "IScript__LevelLost", "address": "0x005381a0", "category": "mission-outcome-handler"},
    {"name": "IScript__LevelLostString", "address": "0x005381c0", "category": "mission-outcome-handler"},
    {"name": "IScript__LevelWon", "address": "0x005381e0", "category": "mission-outcome-handler"},
)
TARGET_NAMES = [row["name"] for row in TARGETS]
UNFORCED_TRANSITION_TARGETS = [
    "CGame__DeclarePlayerDead",
    "CGame__RespawnPlayer",
    "CGame__MPDeclarePlayerWon",
    "CGame__MPDeclareGameDrawn",
    "CGame__DeclareLevelWon",
    "CGame__DeclareLevelLost",
    "IScript__LevelLost",
    "IScript__LevelLostString",
    "IScript__LevelWon",
]
OBJECTIVE_TARGETS = [
    "CGame__FillOutEndLevelData",
    "CGame__GetNumPrimaryObjectives",
    "CGame__GetNumSecondaryObjectives",
    "CEndLevelData__IsAllSecondaryObjectivesComplete",
    "IScript__PrimaryObjectiveComplete",
    "IScript__SecondaryObjectiveComplete",
    "IScript__PrimaryObjectiveFailed",
    "IScript__SecondaryObjectiveFailed",
]


class Level850ModeSemanticsBuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Level850ModeSemanticsBuildError(message)


def require_private_path(path: Path, *, must_exist: bool = False) -> Path:
    resolved = path.resolve()
    root = PRIVATE_PROOF_ROOT.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise Level850ModeSemanticsBuildError(f"private proof path must stay under ignored proof root: {root}") from exc
    if must_exist:
        require(resolved.exists(), f"private proof path is missing: {resolved}")
    return resolved


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def fresh_artifact_root() -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return PRIVATE_PROOF_ROOT / f"level850-mode-semantics-observer-live-{stamp}"


def relative_path(base: Path, target: Path) -> str:
    return os.path.relpath(target.resolve(), base.resolve()).replace("\\", "/")


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def nonzero_hex(value: str) -> bool:
    try:
        return int(value, 16) != 0
    except ValueError:
        return False


HOOK_RE = re.compile(
    r"MODE_SEM_HOOK_TARGET name=(?P<name>[A-Za-z0-9_]+) address=(?P<address>0x[0-9a-fA-F]{8}) category=(?P<category>[A-Za-z0-9_-]+)"
)
HIT_RE = re.compile(r"MODE_SEM_HIT name=(?P<name>[A-Za-z0-9_]+)")
RENDER_RE = re.compile(
    r"MODE_SEM_HIT name=CGame__Render this=(?P<this>[0-9a-fA-F]+) players=(?P<players>\d+) "
    r"level=(?P<level>\d+) horizSplit=(?P<horizSplit>\d+) p0=(?P<p0>[0-9a-fA-F]+) "
    r"p1=(?P<p1>[0-9a-fA-F]+) cam0=(?P<cam0>[0-9a-fA-F]+) cam1=(?P<cam1>[0-9a-fA-F]+) world=(?P<world>[0-9a-fA-F]+)"
)


def cdb_log_from_runtime(runtime_artifact: dict[str, Any]) -> Path:
    observer = object_at(runtime_artifact, "cdbObserver")
    result = object_at(observer, "result")
    raw_log = str(result.get("logPath") or observer.get("logPath") or "")
    require(raw_log, "runtime artifact is missing CDB log path")
    log_path = Path(raw_log)
    require(log_path.is_file(), f"CDB log path is missing: {log_path}")
    return log_path


def parse_cdb_log(log_path: Path) -> dict[str, Any]:
    text = log_path.read_text(encoding="utf-8", errors="replace")
    hooks: dict[str, dict[str, str]] = {}
    for match in HOOK_RE.finditer(text):
        hooks[match.group("name")] = {
            "address": match.group("address").lower(),
            "category": match.group("category"),
        }
    hit_counts = {name: 0 for name in TARGET_NAMES}
    for raw_line in text.splitlines():
        if "> bp" in raw_line:
            continue
        for match in HIT_RE.finditer(raw_line):
            name = match.group("name")
            if name in hit_counts:
                hit_counts[name] += 1
    render_match = RENDER_RE.search(text)
    render: dict[str, Any] = {}
    if render_match:
        render = {
            "this": render_match.group("this").lower(),
            "players": int(render_match.group("players")),
            "level": int(render_match.group("level")),
            "horizSplit": int(render_match.group("horizSplit")),
            "p0": render_match.group("p0").lower(),
            "p1": render_match.group("p1").lower(),
            "cam0": render_match.group("cam0").lower(),
            "cam1": render_match.group("cam1").lower(),
            "world": render_match.group("world").lower(),
        }
    missing_hooks = [target["name"] for target in TARGETS if target["name"] not in hooks]
    wrong_hooks = [
        target["name"]
        for target in TARGETS
        if target["name"] in hooks and hooks[target["name"]]["address"] != target["address"].lower()
    ]
    require(not missing_hooks, f"CDB log missing observer hook target echoes: {', '.join(missing_hooks)}")
    require(not wrong_hooks, f"CDB log has wrong hook target addresses: {', '.join(wrong_hooks)}")
    require(render, "CDB log missing CGame__Render mode-semantics observation")
    require(render["players"] == 2, "render observation did not report two players")
    require(render["level"] == 850, "render observation did not report level 850")
    require(render["horizSplit"] == 1, "render observation did not report horizontal split")
    require(nonzero_hex(render["p0"]) and nonzero_hex(render["p1"]) and render["p0"] != render["p1"], "render P0/P1 pointers are invalid or not distinct")
    return {
        "hookTargets": hooks,
        "hookTargetCount": len(hooks),
        "hitCounts": hit_counts,
        "render": render,
        "unforcedTransitionHitCount": sum(hit_counts[name] for name in UNFORCED_TRANSITION_TARGETS),
        "objectiveSurfaceHitCount": sum(hit_counts[name] for name in OBJECTIVE_TARGETS),
        "logContainsPrivatePath": str(log_path) in text,
    }


def validate_runtime_artifact(runtime_path: Path) -> tuple[dict[str, Any], Path, dict[str, Any]]:
    runtime_path = require_private_path(runtime_path, must_exist=True)
    runtime = read_json(runtime_path)
    require(runtime.get("schemaVersion") == "winui-safe-copy-live-runtime-smoke.v1", "unexpected runtime artifact schema")
    launch = object_at(runtime, "launch")
    require(launch.get("arguments") == ["-skipfmv", "-level", "850", "-configuration", "1"], "runtime launch arguments must be -skipfmv -level 850 -configuration 1")
    source = object_at(runtime, "source")
    require(source.get("installedHashUnchanged") is True, "installed BEA.exe hash changed")
    require(source.get("overrideHashUnchanged") is True, "clean override BEA.exe hash changed")
    require(object_at(source, "saveAndOptions").get("unchanged") is True, "source save/options changed")
    process = object_at(runtime, "processBaseline")
    require(process.get("noPreexistingBea") is True, "pre-existing BEA process was present")
    require(process.get("noBeaAfterStop") is True, "BEA process remained after stop")
    require(object_at(runtime, "stop").get("Success") is True, "managed stop did not succeed")
    captures = runtime.get("captures")
    require(isinstance(captures, list), "runtime captures must be a list")
    require(len(captures) >= 1, "runtime artifact has no bounded captures")
    failed = [
        str(row.get("outputPath", f"capture[{index}]"))
        for index, row in enumerate(captures)
        if not isinstance(row, dict) or str(row.get("status", "")).lower() != "captured"
    ]
    require(not failed, "bounded captures must succeed: " + ", ".join(failed))
    observer = object_at(runtime, "cdbObserver")
    require(observer.get("enabled") is True, "CDB observer was not enabled")
    result = object_at(observer, "result")
    require(result.get("status") == "attached", "CDB observer did not attach")
    require(result.get("logExists") is True, "CDB observer log was not created")
    require(object_at(observer, "cleanup").get("status") in {"stopped", "already-exited"}, "CDB observer cleanup did not complete")
    log_path = cdb_log_from_runtime(runtime)
    parsed = parse_cdb_log(log_path)
    return runtime, log_path, parsed


def build_bundle_from_runtime(runtime_path: Path, output_path: Path) -> dict[str, Any]:
    output_path = require_private_path(output_path)
    runtime, log_path, parsed = validate_runtime_artifact(runtime_path)
    captures = runtime.get("captures") if isinstance(runtime.get("captures"), list) else []
    visual_count = len([row for row in captures if isinstance(row, dict) and row.get("visualProof") is True])
    render = parsed["render"]
    hit_counts = parsed["hitCounts"]
    bundle: dict[str, Any] = {
        "schemaVersion": SCHEMA,
        "generatedBy": HELPER,
        "helperVersion": HELPER_VERSION,
        "protocolVersion": PROTOCOL,
        "generatedAtUtc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "observerScope": OBSERVER_SCOPE,
        "runtimeProfile": RUNTIME_PROFILE,
        "sourceArtifacts": {
            "liveRuntimeArtifact": relative_path(output_path.parent, runtime_path),
            "liveRuntimeArtifactSha256": sha256_file(runtime_path),
            "cdbLogSha256": sha256_file(log_path),
            "observerCommandFile": relative_path(output_path.parent, OBSERVER_COMMAND_FILE),
            "observerCommandFileSha256": sha256_file(OBSERVER_COMMAND_FILE),
        },
        "runtimeEvidence": {
            "safeCopyLaunchLevel": 850,
            "controllerConfiguration": 1,
            "newBeaLaunchCount": 1,
            "cdbAttachCount": 1,
            "boundedCaptureCount": len(captures),
            "visualCaptureCount": visual_count,
            "exactPidCdbObserverProven": True,
            "renderPlayers": render["players"],
            "renderLevel": render["level"],
            "horizontalSplit": render["horizSplit"] == 1,
            "p1Pointer": render["p0"],
            "p2Pointer": render["p1"],
            "p1p2PointersDistinct": True,
            "sourceHashesUnchanged": True,
            "managedStopClean": True,
        },
        "modeSemanticsSurface": {
            "modeSemanticsObserverProven": True,
            "hookTargetCount": parsed["hookTargetCount"],
            "expectedHookTargetCount": len(TARGETS),
            "hookTargets": TARGETS,
            "hitCounts": hit_counts,
            "unforcedTransitionTargets": UNFORCED_TRANSITION_TARGETS,
            "unforcedTransitionHitCount": parsed["unforcedTransitionHitCount"],
            "objectiveSurfaceTargets": OBJECTIVE_TARGETS,
            "objectiveSurfaceHitCount": parsed["objectiveSurfaceHitCount"],
            "forcedWinDeathRespawn": False,
            "modeRuntimeProofSlicesAdded": 0,
            "coOpVersusModeRuntimeProofSlicesAdded": 0,
            "currentRuntimeModeClassification": "unclassified-local-multiplayer",
        },
        "slotBoundary": {
            "acceptedOriginalBinaryGameplaySlots": EXPECTED_ACTIVE_SLOTS,
            "metadataOnlySlots": EXPECTED_METADATA_SLOTS,
            "rejectedGameplayRouteSlots": EXPECTED_METADATA_SLOTS,
            "maxOriginalBinaryActiveSlotsProven": 2,
            "slotCapacity": 4,
            "nPlayerOriginalBinaryRuntimeProof": 0,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "beyondTwoPlayersRequiresNewProofClass": True,
        },
        "nonClaims": {
            "baseOnlineMultiplayerReady": False,
            "secondPhysicalHostProof": False,
            "multiHostLanProof": False,
            "publicMatchmakingProof": False,
            "nativeBeaNetcodeProof": False,
            "coOpModeRuntimeProof": False,
            "versusModeRuntimeProof": False,
            "teamVersusRuntimeProof": False,
            "spectatorAdminRuntimeProof": False,
            "moreThanTwoOriginalBinaryRuntimeProof": False,
            "activeP3P4OriginalBinaryGameplayProof": False,
            "safeToPatchMPlayersAbove2": False,
            "deterministicSyncProof": False,
            "rollbackProof": False,
            "antiCheatProof": False,
            "rebuildParityProof": False,
            "noNoticeableDifferenceProof": False,
        },
        "releaseBoundary": {
            "privateProofReleaseExcludedByPolicy": True,
            "rawPrivateProofPathPublished": False,
            "rawPrivateArtifactContentPublished": False,
            "absolutePrivatePathPublished": False,
            "rawRuntimePointerPublishedInPublicDocs": False,
            "rawRuntimePidPublishedInPublicDocs": False,
            "rawCdbLogPathPublishedInPublicDocs": False,
            "releaseIncludedPrivateArtifact": False,
        },
        "claimBoundary": (
            "This proves a copied original-binary level-850/config-1 P1/P2 local split-screen mode-semantics observer "
            "surface: a fresh safe-copy launch attached CDB to the exact managed BEA process, observed the two-player "
            "render graph, and installed/read hook targets for objective, win/loss, death, lives, and respawn paths. "
            "It does not force or prove win, death, respawn, co-op, versus, team-versus, spectator/admin, second-host "
            "LAN, public matchmaking, native BEA netcode, active P3/P4 gameplay, deterministic sync, rebuild parity, "
            "or no-noticeable-difference online parity."
        ),
    }
    write_json(output_path, bundle)
    return bundle


def build_live_bundle(artifact_root: Path, output_path: Path, *, exe_override: Path) -> dict[str, Any]:
    artifact_root = require_private_path(artifact_root)
    artifact_root.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        str(ROOT / "tools" / "winui_safe_copy_live_runtime_smoke.py"),
        "--artifact-root",
        str(artifact_root),
        "--arm-live-bea",
        "LAUNCH SAFE COPY BEA",
        "--timeout-seconds",
        "18",
        "--capture-count",
        "2",
        "--capture-interval-seconds",
        "1",
        "--post-window-delay-seconds",
        "1",
        "--level-id",
        "850",
        "--controller-configuration",
        "1",
        "--enable-cdb-observer",
        "--arm-cdb-observer",
        "ATTACH CDB TO SAFE COPY BEA",
        "--cdb-command-file",
        str(OBSERVER_COMMAND_FILE.relative_to(ROOT)),
        "--cdb-post-attach-wait-seconds",
        "2",
        "--exe-override",
        str(exe_override),
    ]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    (artifact_root / "mode-semantics-builder-stdout.log").write_text(result.stdout, encoding="utf-8")
    (artifact_root / "mode-semantics-builder-stderr.log").write_text(result.stderr, encoding="utf-8")
    runtime_artifact = artifact_root / "live-safe-copy-runtime-smoke.json"
    if result.returncode != 0:
        raise Level850ModeSemanticsBuildError(
            "live mode-semantics smoke failed with exit "
            f"{result.returncode}; see {artifact_root / 'mode-semantics-builder-stderr.log'}"
        )
    bundle = build_bundle_from_runtime(runtime_artifact, output_path)
    bundle["runtimeEvidence"]["liveSmokeExitCode"] = result.returncode
    bundle["runtimeEvidence"]["liveSmokeAcceptedDespiteNonzeroExit"] = False
    write_json(output_path, bundle)
    return bundle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-root", type=Path, default=None)
    parser.add_argument("--runtime-artifact", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--exe-override", type=Path, default=DEFAULT_EXE_OVERRIDE)
    args = parser.parse_args()
    if args.runtime_artifact is not None:
        bundle = build_bundle_from_runtime(args.runtime_artifact, args.output)
    else:
        bundle = build_live_bundle(args.artifact_root or fresh_artifact_root(), args.output, exe_override=args.exe_override)
    print(
        json.dumps(
            {
                "artifact": str(args.output),
                "schemaVersion": bundle["schemaVersion"],
                "observerScope": bundle["observerScope"],
                "newBeaLaunchCount": bundle["runtimeEvidence"]["newBeaLaunchCount"],
                "cdbAttachCount": bundle["runtimeEvidence"]["cdbAttachCount"],
                "hookTargetCount": bundle["modeSemanticsSurface"]["hookTargetCount"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Level850ModeSemanticsBuildError as exc:
        print(f"WinUI original-binary level850 mode-semantics observer build: FAIL: {exc}")
        raise SystemExit(2)
