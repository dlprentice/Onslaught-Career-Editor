#!/usr/bin/env python3
"""Build a private level-854 fire/input-to-weapon-handoff proof bundle."""

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

import build_winui_original_binary_level854_outcome_semantics_observer_bundle as observer


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_PROOF_ROOT = observer.PRIVATE_PROOF_ROOT
DEFAULT_ARTIFACT_ROOT = PRIVATE_PROOF_ROOT / "level854-fire-handoff-20260619"
DEFAULT_OUTPUT = DEFAULT_ARTIFACT_ROOT / "level854-fire-handoff-proof.json"
DEFAULT_GAME_ROOT = observer.DEFAULT_GAME_ROOT
DEFAULT_EXE_OVERRIDE = observer.DEFAULT_EXE_OVERRIDE
COMMAND_FILE = ROOT / "tools" / "runtime-probes" / "local-multiplayer-level854-fire-handoff-observer.cdb.txt"

SCHEMA = "winui-original-binary-level854-fire-handoff.v1"
PROTOCOL = "level854-fire-handoff.v1"
HELPER = "winui-original-binary-level854-fire-handoff"
HELPER_VERSION = "level854-fire-handoff.v1"
SCOPE = "level854-fire-input-to-weapon-handoff-not-online-proof"
RUNTIME_PROFILE = observer.RUNTIME_PROFILE
MAX_LIVE_SMOKE_ATTEMPTS = 2
FOREGROUND_CHANGED_TOKEN = "Foreground window changed before scoped input delivery"
POINTER_CHAIN_MISSING_TOKEN = "no same-window input-to-fire-burst pointer chain was observed"
EXPECTED_SOURCE_FIRE_BUTTON = 18
OBSERVED_RUNTIME_FIRE_BUTTON = 19
INPUT_SEQUENCES = [
    "wait:1500",
    "down:Q,wait:2500,up:Q",
    "wait:1000",
    "down:Q,wait:2500,up:Q",
    "wait:1000",
    "down:E,wait:2500,up:E",
    "wait:1500",
]

TARGETS: tuple[dict[str, str], ...] = (
    {"name": "CGame__Render", "address": "0x0046e460", "category": "p1p2-render-graph"},
    {"name": "CController__SendButtonAction", "address": "0x0042e4d0", "category": "input-dispatch"},
    {"name": "CPlayer__ReceiveButtonAction", "address": "0x004d3110", "category": "input-dispatch"},
    {"name": "CBattleEngineWalkerPart__FireWeapon", "address": "0x00413cc0", "category": "walkerpart-fire-entry"},
    {"name": "CBattleEngineWalkerPart__GetCurrentWeapon", "address": "0x00414030", "category": "walkerpart-current-weapon"},
    {"name": "CBattleEngineWalkerPart__WeaponFired", "address": "0x004140d0", "category": "walkerpart-fired-bookkeeping"},
    {"name": "CBattleEngineWalkerPart__CanWeaponFire", "address": "0x00414630", "category": "walkerpart-fire-predicate"},
    {"name": "CBattleEngineJetPart__WeaponFired", "address": "0x00412050", "category": "jetpart-fired-bookkeeping"},
    {"name": "CWeapon__HandleFireBurstEvent", "address": "0x00506930", "category": "weapon-burst-event"},
    {"name": "CWeapon__DoesTargetMaskMatchDistanceProfile", "address": "0x005061f0", "category": "weapon-target-profile"},
    {"name": "CWeapon__AdvanceChargeProgressIfAnySlotAssigned", "address": "0x005068f0", "category": "weapon-charge-progress"},
    {"name": "ProjectileBurst__SpawnFromCurrentPreset", "address": "0x005069f0", "category": "projectile-burst-current-preset"},
    {"name": "ProjectileBurst__SpawnFromPercentBucketFallback", "address": "0x00506010", "category": "projectile-burst-fallback"},
    {"name": "ProjectileBurstPreset__GetListEntryIdByIndex", "address": "0x005078b0", "category": "projectile-burst-preset-index"},
    {"name": "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "address": "0x00406560", "category": "battleengine-projectile-updater"},
    {"name": "CBattleEngine__AddProjectile", "address": "0x00406fc0", "category": "battleengine-projectile-add"},
    {"name": "OID__CreateObject", "address": "0x004bf090", "category": "oid-shell-factory"},
    {"name": "CShell__Constructor", "address": "0x004df4c0", "category": "shell-materialization"},
    {"name": "CShell__CopyResourceNameToInlineBuffer", "address": "0x004df530", "category": "shell-materialization"},
    {"name": "CShell__Init", "address": "0x004df550", "category": "shell-materialization"},
    {"name": "CWorldPhysicsManager__CreateProjectile", "address": "0x0050f7a0", "category": "projectile-factory"},
    {"name": "CRound__ctor", "address": "0x004d81e0", "category": "round-projectile-factory"},
    {"name": "CRound__Init", "address": "0x004d8410", "category": "round-projectile-factory"},
    {"name": "CRound__SelectBestTargetReaderAndSyncAimState", "address": "0x004dac90", "category": "round-targeting"},
    {"name": "CRound__UpdateRoundAndTriggerLaunchEffect", "address": "0x004d9ef0", "category": "round-projectile-factory"},
    {"name": "CRound__SpawnConfiguredProjectile", "address": "0x004db150", "category": "round-projectile-spawn"},
    {"name": "CRound__ArmProjectileAndSpawnTrailEffect", "address": "0x004db630", "category": "round-projectile-arm-trail"},
)
TARGET_NAMES = [row["name"] for row in TARGETS]
INPUT_TARGET_NAMES = ["CController__SendButtonAction", "CPlayer__ReceiveButtonAction"]
DIRECT_FIRE_TARGET_NAMES = [
    "CBattleEngineWalkerPart__FireWeapon",
    "CBattleEngineWalkerPart__WeaponFired",
    "CBattleEngineJetPart__WeaponFired",
]
BURST_TARGET_NAMES = [
    "CWeapon__HandleFireBurstEvent",
    "CWeapon__DoesTargetMaskMatchDistanceProfile",
    "CWeapon__AdvanceChargeProgressIfAnySlotAssigned",
    "ProjectileBurst__SpawnFromCurrentPreset",
    "ProjectileBurst__SpawnFromPercentBucketFallback",
    "ProjectileBurstPreset__GetListEntryIdByIndex",
]
BATTLEENGINE_PROJECTILE_TARGET_NAMES = [
    "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
    "CBattleEngine__AddProjectile",
]
SHELL_TARGET_NAMES = [
    "OID__CreateObject",
    "CShell__Constructor",
    "CShell__CopyResourceNameToInlineBuffer",
    "CShell__Init",
]
PROJECTILE_FACTORY_TARGET_NAMES = [
    "CBattleEngine__AddProjectile",
    "CWorldPhysicsManager__CreateProjectile",
    "CRound__ctor",
    "CRound__Init",
    "CRound__SelectBestTargetReaderAndSyncAimState",
    "CRound__UpdateRoundAndTriggerLaunchEffect",
]
ROUND_TARGET_NAMES = [
    "CWorldPhysicsManager__CreateProjectile",
    "CRound__ctor",
    "CRound__Init",
    "CRound__SelectBestTargetReaderAndSyncAimState",
    "CRound__UpdateRoundAndTriggerLaunchEffect",
    "CRound__SpawnConfiguredProjectile",
    "CRound__ArmProjectileAndSpawnTrailEffect",
]


class Level854FireHandoffBuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Level854FireHandoffBuildError(message)


def require_private_path(path: Path, *, must_exist: bool = False) -> Path:
    return observer.require_private_path(path, must_exist=must_exist)


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
    return PRIVATE_PROOF_ROOT / f"level854-fire-handoff-live-{stamp}"


def live_attempt_root(artifact_root: Path, attempt: int) -> Path:
    require(attempt >= 1, "live smoke attempt index must be positive")
    if attempt == 1:
        return artifact_root
    return artifact_root.with_name(f"{artifact_root.name}-retry{attempt:02d}")


def runtime_artifact_has_foreground_abort(runtime_artifact: Path) -> bool:
    if not runtime_artifact.is_file():
        return False
    try:
        payload = read_json(runtime_artifact)
    except (OSError, json.JSONDecodeError, Level854FireHandoffBuildError):
        return False
    rows = payload.get("input")
    if not isinstance(rows, list):
        return False
    for row in rows:
        if not isinstance(row, dict) or row.get("status") != "failed":
            continue
        text = "\n".join(str(row.get(key, "")) for key in ("stderr", "stdout", "note"))
        if FOREGROUND_CHANGED_TOKEN in text:
            return True
    return False


def runtime_artifact_has_basic_fire_handoff(runtime_artifact: Path) -> bool:
    if not runtime_artifact.is_file():
        return False
    try:
        _, _, _, windows = validate_runtime_artifact(runtime_artifact)
    except (OSError, json.JSONDecodeError, Level854FireHandoffBuildError):
        return False
    return any(bool(row.get("sameWindowInputFireHandoff")) for row in windows)


def relative_path(base: Path, target: Path) -> str:
    return os.path.relpath(target.resolve(), base.resolve()).replace("\\", "/")


def require_path_under(path: Path, root: Path, label: str) -> Path:
    resolved = path.resolve()
    root_resolved = root.resolve()
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise Level854FireHandoffBuildError(f"{label} must stay under {root_resolved}: {resolved}") from exc
    return resolved


def require_recorded_path(raw: Any, expected: Path, label: str) -> Path:
    require(isinstance(raw, str) and raw.strip(), f"{label} path missing")
    resolved = Path(raw).resolve()
    require(resolved == expected.resolve(), f"{label} path mismatch: {resolved} != {expected.resolve()}")
    return resolved


def object_at(value: dict[str, Any], key: str) -> dict[str, Any]:
    child = value.get(key)
    require(isinstance(child, dict), f"missing object: {key}")
    return child


def list_at(value: dict[str, Any], key: str) -> list[Any]:
    child = value.get(key)
    require(isinstance(child, list), f"missing list: {key}")
    return child


def validate_command_file(path: Path = COMMAND_FILE) -> None:
    path = path.resolve()
    require(path.is_file(), f"fire-handoff CDB command file missing: {path}")
    text = path.read_text(encoding="utf-8", errors="replace")
    for pattern in (
        r"^\s*\.shell\b",
        r"^\s*\.dump\b",
        r"^\s*\.writemem\b",
        r"^\s*ed\s+",
        r"^\s*eb\s+",
        r"^\s*ew\s+",
        r"^\s*eq\s+",
        r"^\s*r\s+",
    ):
        require(
            re.search(pattern, text, re.IGNORECASE | re.MULTILINE) is None,
            f"CDB command file contains mutating command pattern: {pattern}",
        )
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(".echo") or stripped.startswith("bp ") or stripped == "g" or stripped in {"vertarget", "lm m BEA"}:
            continue
        raise Level854FireHandoffBuildError(f"CDB command file contains unsupported command: {stripped}")


def nonzero_hex(value: str) -> bool:
    try:
        return int(value, 16) != 0
    except ValueError:
        return False


HOOK_RE = re.compile(
    r"FIRE_HANDOFF_HOOK_TARGET name=(?P<name>[A-Za-z0-9_]+) address=(?P<address>0x[0-9a-fA-F]{8}) category=(?P<category>[A-Za-z0-9_-]+)"
)
HIT_RE = re.compile(r"FIRE_HANDOFF_HIT name=(?P<name>[A-Za-z0-9_]+)")
BUTTON_RE = re.compile(
    r"FIRE_HANDOFF_HIT name=(?:CController__SendButtonAction|CPlayer__ReceiveButtonAction)\b[^\n]*\bbutton=(?P<button>\d+)\b"
)
RENDER_RE = re.compile(
    r"FIRE_HANDOFF_HIT name=CGame__Render this=(?P<this>[0-9a-fA-F]+) players=(?P<players>\d+) "
    r"level=(?P<level>\d+) horizSplit=(?P<horizSplit>\d+) p0=(?P<p0>[0-9a-fA-F]+) "
    r"p1=(?P<p1>[0-9a-fA-F]+) cam0=(?P<cam0>[0-9a-fA-F]+) cam1=(?P<cam1>[0-9a-fA-F]+) world=(?P<world>[0-9a-fA-F]+)"
)
RENDER_CHECKSUM_WARNING_SPLIT_RE = re.compile(
    r"(FIRE_HANDOFF_HIT name=CGame__Render this=)\*\*\* WARNING: Unable to verify checksum for [^\r\n]+[\r\n]+"
    r"(?=[0-9a-fA-F]+ players=)"
)
WEAPON_FIRED_RE = re.compile(
    r"FIRE_HANDOFF_HIT name=CBattleEngineWalkerPart__WeaponFired this=(?P<part>[0-9a-fA-F]+) weapon=(?P<weapon>[0-9a-fA-F]+)"
)
WEAPON_BURST_RE = re.compile(
    r"FIRE_HANDOFF_HIT name=CWeapon__HandleFireBurstEvent this=(?P<context>[0-9a-fA-F]+) "
    r"eventRecord=(?P<eventRecord>[0-9a-fA-F]+) eventHeadRaw=(?P<eventHeadRaw>[0-9a-fA-F]+)"
)
BURST_CONTEXT_RE = re.compile(
    r"FIRE_HANDOFF_HIT name=ProjectileBurst__(?:SpawnFromCurrentPreset|SpawnFromPercentBucketFallback) burstContext=(?P<context>[0-9a-fA-F]+)"
)
ROUND_DEFINITION_RE = re.compile(
    r"FIRE_HANDOFF_HIT name=CWorldPhysicsManager__CreateProjectile roundDefinition=(?P<definition>[0-9a-fA-F]+)"
)
ROUND_CTOR_RE = re.compile(r"FIRE_HANDOFF_HIT name=CRound__ctor this=(?P<round>[0-9a-fA-F]+) init=(?P<init>[0-9a-fA-F]+)")


def count_hits(text: str, names: list[str]) -> dict[str, int]:
    return {name: len(re.findall(rf"FIRE_HANDOFF_HIT name={re.escape(name)}\b", text)) for name in names}


def count_buttons(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for match in BUTTON_RE.finditer(text):
        key = match.group("button")
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: int(item[0])))


def normalized_hex(value: str) -> str:
    return f"{int(value, 16):08x}"


def unique_sorted(values: set[str]) -> list[str]:
    return sorted(values, key=lambda item: int(item, 16))


def parse_fire_burst_chain(text: str) -> dict[str, Any]:
    weapon_fired = [
        {
            "walkerPart": normalized_hex(match.group("part")),
            "weapon": normalized_hex(match.group("weapon")),
            "byteOffset": match.start(),
        }
        for match in WEAPON_FIRED_RE.finditer(text)
    ]
    burst_events = [
        {
            "context": normalized_hex(match.group("context")),
            "eventRecord": normalized_hex(match.group("eventRecord")),
            "eventHeadRaw": normalized_hex(match.group("eventHeadRaw")),
            "eventHeadMatchesContext": normalized_hex(match.group("context")) == normalized_hex(match.group("eventHeadRaw")),
            "byteOffset": match.start(),
        }
        for match in WEAPON_BURST_RE.finditer(text)
    ]
    burst_spawns = [
        {
            "context": normalized_hex(match.group("context")),
            "byteOffset": match.start(),
        }
        for match in BURST_CONTEXT_RE.finditer(text)
    ]
    burst_contexts = {row["context"] for row in burst_spawns if nonzero_hex(row["context"])}
    weapon_contexts = {row["weapon"] for row in weapon_fired if nonzero_hex(row["weapon"])}
    burst_event_contexts = {row["context"] for row in burst_events if nonzero_hex(row["context"])}
    correlated_contexts = weapon_contexts & burst_event_contexts & burst_contexts
    ordered_contexts = {
        weapon["weapon"]
        for weapon in weapon_fired
        for event in burst_events
        for spawn in burst_spawns
        if weapon["weapon"] == event["context"] == spawn["context"]
        and event["eventHeadMatchesContext"]
        and int(weapon["byteOffset"]) < int(event["byteOffset"]) < int(spawn["byteOffset"])
    }
    round_definitions = {normalized_hex(match.group("definition")) for match in ROUND_DEFINITION_RE.finditer(text)}
    round_ctor_inits = {normalized_hex(match.group("init")) for match in ROUND_CTOR_RE.finditer(text)}
    round_definition_correlations = round_definitions & round_ctor_inits
    return {
        "weaponFiredCount": len(weapon_fired),
        "weaponFiredContexts": unique_sorted(weapon_contexts),
        "burstEventCount": len(burst_events),
        "burstEventContexts": unique_sorted(burst_event_contexts),
        "burstSpawnContexts": unique_sorted(burst_contexts),
        "eventHeadMatchesContextCount": len([row for row in burst_events if row["eventHeadMatchesContext"]]),
        "correlatedWeaponBurstContexts": unique_sorted(correlated_contexts),
        "fireBurstPointerChainObserved": bool(correlated_contexts),
        "orderedCorrelatedWeaponBurstContexts": unique_sorted(ordered_contexts),
        "orderedFireBurstPointerChainObserved": bool(ordered_contexts),
        "roundDefinitionCount": len(round_definitions),
        "roundCtorInitDefinitionCount": len(round_ctor_inits),
        "roundDefinitionCorrelationCount": len(round_definition_correlations),
        "roundDefinitionCorrelationObserved": bool(round_definition_correlations),
    }


def normalize_render_observation_text(text: str) -> str:
    return RENDER_CHECKSUM_WARNING_SPLIT_RE.sub(r"\1", text)


def is_wait_only_sequence(sequence: str) -> bool:
    parts = [part.strip().lower() for part in sequence.split(",") if part.strip()]
    return bool(parts) and all(part.startswith("wait:") for part in parts)


def parse_cdb_log(log_path: Path) -> dict[str, Any]:
    text = log_path.read_text(encoding="utf-8", errors="replace")
    render_text = normalize_render_observation_text(text)
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
    render_match = RENDER_RE.search(render_text)
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
    require(not missing_hooks, f"CDB log missing fire-handoff hook target echoes: {', '.join(missing_hooks)}")
    require(not wrong_hooks, f"CDB log has wrong fire-handoff hook target addresses: {', '.join(wrong_hooks)}")
    require(render, "CDB log missing CGame__Render fire-handoff observation")
    require(render["players"] == 2, "render observation did not report two players")
    require(render["level"] == 854, "render observation did not report level 854")
    require(render["horizSplit"] == 1, "render observation did not report horizontal split")
    require(
        nonzero_hex(render["p0"]) and nonzero_hex(render["p1"]) and render["p0"] != render["p1"],
        "render P0/P1 pointers are invalid or not distinct",
    )
    button_counts = count_buttons(text)
    return {
        "hookTargets": hooks,
        "hookTargetCount": len(hooks),
        "hitCounts": hit_counts,
        "buttonCounts": button_counts,
        "button18DispatchCount": button_counts.get(str(EXPECTED_SOURCE_FIRE_BUTTON), 0),
        "button19DispatchCount": button_counts.get(str(OBSERVED_RUNTIME_FIRE_BUTTON), 0),
        "render": render,
        "directFireDispatchHitCount": sum(hit_counts[name] for name in DIRECT_FIRE_TARGET_NAMES),
        "burstOrProjectilePresetHitCount": sum(hit_counts[name] for name in BURST_TARGET_NAMES),
        "battleEngineProjectileHitCount": sum(hit_counts[name] for name in BATTLEENGINE_PROJECTILE_TARGET_NAMES),
        "shellMaterializationHitCount": sum(hit_counts[name] for name in SHELL_TARGET_NAMES),
        "projectileFactoryHitCount": sum(hit_counts[name] for name in PROJECTILE_FACTORY_TARGET_NAMES),
        "roundProjectileHitCount": sum(hit_counts[name] for name in ROUND_TARGET_NAMES),
    }


def cdb_log_from_runtime(runtime_artifact: dict[str, Any]) -> Path:
    return observer.cdb_log_from_runtime(runtime_artifact)


def input_windows_from_runtime(runtime: dict[str, Any], log_path: Path) -> list[dict[str, Any]]:
    rows = list_at(runtime, "inputCdbWindows")
    log_path = log_path.resolve()
    data = log_path.read_bytes()
    windows: list[dict[str, Any]] = []
    for row in rows:
        require(isinstance(row, dict), "inputCdbWindows row is not an object")
        index = row.get("index")
        sequence = row.get("sequence")
        start = row.get("logStartByte")
        end = row.get("logEndByte")
        require(isinstance(index, int) and index > 0, "inputCdbWindows row has invalid index")
        require(isinstance(sequence, str) and sequence, f"inputCdbWindows row {index} has invalid sequence")
        require(isinstance(start, int) and isinstance(end, int), f"inputCdbWindows row {index} is missing byte offsets")
        require(0 <= start <= end <= len(data), f"inputCdbWindows row {index} byte offsets are out of range")
        require_recorded_path(row.get("logPath"), log_path, f"inputCdbWindows row {index} log")
        text = data[start:end].decode("utf-8", errors="replace")
        stimulus = not is_wait_only_sequence(sequence)
        hit_counts = count_hits(text, TARGET_NAMES)
        button_counts = count_buttons(text)
        button18 = button_counts.get(str(EXPECTED_SOURCE_FIRE_BUTTON), 0)
        button19 = button_counts.get(str(OBSERVED_RUNTIME_FIRE_BUTTON), 0)
        direct_fire = sum(hit_counts[name] for name in DIRECT_FIRE_TARGET_NAMES)
        burst = sum(hit_counts[name] for name in BURST_TARGET_NAMES)
        battleengine_projectile_hits = sum(hit_counts[name] for name in BATTLEENGINE_PROJECTILE_TARGET_NAMES)
        shell_hits = sum(hit_counts[name] for name in SHELL_TARGET_NAMES)
        projectile_factory_hits = sum(hit_counts[name] for name in PROJECTILE_FACTORY_TARGET_NAMES)
        round_hits = sum(hit_counts[name] for name in ROUND_TARGET_NAMES)
        fire_burst_chain = parse_fire_burst_chain(text)
        windows.append(
            {
                "index": index,
                "sequence": sequence,
                "stimulusWindow": stimulus,
                "byteCount": end - start,
                "buttonCounts": button_counts,
                "button18DispatchCount": button18,
                "button19DispatchCount": button19,
                "directFireDispatchHitCount": direct_fire,
                "burstOrProjectilePresetHitCount": burst,
                "battleEngineProjectileHitCount": battleengine_projectile_hits,
                "shellMaterializationHitCount": shell_hits,
                "projectileFactoryHitCount": projectile_factory_hits,
                "roundProjectileHitCount": round_hits,
                "sameWindowInputFireHandoff": stimulus and button19 > 0 and direct_fire > 0 and burst > 0,
                "sameWindowBattleEngineProjectile": stimulus and button19 > 0 and battleengine_projectile_hits > 0,
                "sameWindowShellMaterialization": stimulus and button19 > 0 and shell_hits > 0,
                "sameWindowProjectileFactory": stimulus and button19 > 0 and projectile_factory_hits > 0,
                "sameWindowRoundProjectileCausality": stimulus and button19 > 0 and round_hits > 0,
                "sameWindowFireBurstPointerChain": stimulus and button19 > 0 and fire_burst_chain["fireBurstPointerChainObserved"],
                "sameWindowOrderedFireBurstPointerChain": stimulus
                and button19 > 0
                and fire_burst_chain["orderedFireBurstPointerChainObserved"],
                "fireBurstPointerChain": fire_burst_chain,
                "hitCounts": hit_counts,
            }
        )
    windows.sort(key=lambda item: int(item["index"]))
    require(any(row["stimulusWindow"] for row in windows), "fire-handoff proof needs at least one stimulus input window")
    require(any(not row["stimulusWindow"] for row in windows), "fire-handoff proof needs at least one wait/no-input control window")
    return windows


def require_control_options(runtime: dict[str, Any]) -> dict[str, Any]:
    safe_copy = object_at(runtime, "safeCopy")
    control = object_at(safe_copy, "controlOptions")
    require(control.get("requestedWeaponFireQe") is True, "runtime artifact did not request weapon-fire Q/E binding")
    require(control.get("requestedInputIsolationForwardQe") is False, "fire-handoff proof must not use forward Q/E lever")
    require(control.get("proofLever") == "copied-defaultoptions-weapon-fire-qe", "wrong control-options proof lever")
    require(control.get("changedAfterPrepare") is True, "copied defaultoptions.bea was not changed after prepare")
    require(str(control.get("ProofStatus", "")) == "options_byte_materialized_only", "unexpected control-options proof status")
    require(str(control.get("OptionsPath", "")).lower().endswith("defaultoptions.bea"), "control-options path must be copied defaultoptions.bea")
    ranges = control.get("changedRanges")
    require(isinstance(ranges, list) and len(ranges) >= 2, "fire Q/E materialization needs changed byte ranges")
    return control


def validate_runtime_artifact(runtime_path: Path) -> tuple[dict[str, Any], Path, dict[str, Any], list[dict[str, Any]]]:
    runtime_path = require_private_path(runtime_path, must_exist=True)
    runtime_root = runtime_path.parent.resolve()
    expected_cdb_root = runtime_root / "cdb"
    runtime = read_json(runtime_path)
    require(runtime.get("schemaVersion") == "winui-safe-copy-live-runtime-smoke.v1", "unexpected runtime artifact schema")
    require(
        object_at(runtime, "launch").get("arguments") == ["-skipfmv", "-level", "854", "-configuration", "1"],
        "runtime launch arguments must be -skipfmv -level 854 -configuration 1",
    )
    require_control_options(runtime)
    source = object_at(runtime, "source")
    require(source.get("installedHashUnchanged") is True, "installed BEA.exe hash changed")
    require(source.get("overrideHashUnchanged") is True, "clean override BEA.exe hash changed")
    require(object_at(source, "saveAndOptions").get("unchanged") is True, "source save/options changed")
    baseline = object_at(runtime, "processBaseline")
    require(baseline.get("noPreexistingBea") is True, "pre-existing BEA process was present")
    require(baseline.get("noBeaAfterStop") is True, "BEA process remained after stop")
    require(object_at(runtime, "stop").get("Success") is True, "managed stop did not succeed")
    captures = runtime.get("captures")
    require(isinstance(captures, list) and captures, "runtime artifact has no bounded captures")
    require(all(isinstance(row, dict) and row.get("status") == "captured" for row in captures), "bounded captures must all be captured")
    require(all(isinstance(row, dict) and row.get("visualProof") is True for row in captures), "bounded captures must all carry visualProof=true")
    observer_state = object_at(runtime, "cdbObserver")
    require(observer_state.get("enabled") is True, "CDB observer was not enabled")
    expected_command = COMMAND_FILE.resolve()
    require_recorded_path(observer_state.get("commandFile"), expected_command, "CDB observer command")
    result = object_at(observer_state, "result")
    require(result.get("status") == "attached", "CDB observer did not attach")
    require(result.get("logExists") is True, "CDB log was not created")
    require_recorded_path(result.get("commandFile"), expected_command, "CDB observer result command")
    require(object_at(observer_state, "cleanup").get("status") in {"stopped", "already-exited"}, "CDB observer cleanup did not complete")
    input_plan = object_at(runtime, "inputPlan")
    input_summary = object_at(runtime, "inputSummary")
    require(input_plan.get("inputSequenceCount") == len(INPUT_SEQUENCES), "unexpected fire-handoff input sequence count")
    require(input_plan.get("allowBackgroundWindowMessages") is False, "background window messages are not allowed")
    require(input_summary.get("inputSequencesSent") == input_plan.get("inputSequenceCount"), "not every input sequence was sent")
    require(input_summary.get("focusedInputSequences") == input_plan.get("inputSequenceCount"), "not every input sequence was focused")
    require(input_summary.get("inputWindowMessageEventsSent", 0) == 0, "background/window-message input is not allowed")
    require(input_summary.get("inputKeyEventsSent", 0) > 0, "fire-handoff proof needs real key input")
    input_rows = runtime.get("input")
    require(isinstance(input_rows, list) and input_rows, "input result rows are missing")
    require(all(isinstance(row, dict) and row.get("status") == "sent" for row in input_rows), "all input result rows must have status=sent")
    log_path = require_path_under(cdb_log_from_runtime(runtime), expected_cdb_root, "CDB log")
    require_recorded_path(observer_state.get("logPath"), log_path, "CDB observer log")
    require_recorded_path(result.get("logPath"), log_path, "CDB observer result log")
    helper_payload = result.get("helperPayload")
    if isinstance(helper_payload, dict):
        require_recorded_path(helper_payload.get("logPath"), log_path, "CDB helper payload log")
    validate_command_file(COMMAND_FILE)
    parsed = parse_cdb_log(log_path)
    windows = input_windows_from_runtime(runtime, log_path)
    require([row["sequence"] for row in windows] == INPUT_SEQUENCES, "input CDB window sequence list mismatch")
    return runtime, log_path, parsed, windows


def build_bundle_from_runtime(runtime_path: Path, output_path: Path, *, fresh_live_execution: bool = False) -> dict[str, Any]:
    output_path = require_private_path(output_path)
    runtime, log_path, parsed, windows = validate_runtime_artifact(runtime_path)
    captures = runtime.get("captures") if isinstance(runtime.get("captures"), list) else []
    visual_count = len([row for row in captures if isinstance(row, dict) and row.get("visualProof") is True])
    render = parsed["render"]
    positive_windows = [row for row in windows if row["sameWindowInputFireHandoff"]]
    pointer_chain_windows = [row for row in windows if row["sameWindowFireBurstPointerChain"]]
    ordered_pointer_chain_windows = [row for row in windows if row["sameWindowOrderedFireBurstPointerChain"]]
    wait_button_count = sum(int(row["button19DispatchCount"]) for row in windows if not row["stimulusWindow"])
    wait_handoff_count = sum(int(row["directFireDispatchHitCount"]) + int(row["burstOrProjectilePresetHitCount"]) for row in windows if not row["stimulusWindow"])
    total_button18 = sum(int(row["button18DispatchCount"]) for row in windows)
    total_button19 = sum(int(row["button19DispatchCount"]) for row in windows)
    require(wait_button_count == 0, "wait/no-input windows must not contain fire button dispatch")
    require(total_button19 > 0, "runtime did not dispatch observed fire button 19")
    require(total_button18 == 0, "source-expected button 18 was observed; update the claim boundary before accepting")
    require(positive_windows, "no same-window input-to-fire-handoff window was observed")
    require(pointer_chain_windows, "no same-window input-to-fire-burst pointer chain was observed")
    bundle: dict[str, Any] = {
        "schemaVersion": SCHEMA,
        "generatedBy": HELPER,
        "helperVersion": HELPER_VERSION,
        "protocolVersion": PROTOCOL,
        "generatedAtUtc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "proofScope": SCOPE,
        "runtimeProfile": RUNTIME_PROFILE,
        "executionReceipt": {
            "freshLiveExecution": fresh_live_execution,
            "runtimeGeneratedAt": runtime.get("generatedAt"),
            "runtimeArtifactRootName": runtime_path.parent.name,
            "runtimeArtifactSha256": sha256_file(runtime_path),
            "outputRootName": output_path.parent.name,
            "replayArtifactAcceptedForPromotion": False,
        },
        "sourceArtifacts": {
            "liveRuntimeArtifact": relative_path(output_path.parent, runtime_path),
            "liveRuntimeArtifactSha256": sha256_file(runtime_path),
            "cdbLogSha256": sha256_file(log_path),
            "observerCommandFile": relative_path(output_path.parent, COMMAND_FILE),
            "observerCommandFileSha256": sha256_file(COMMAND_FILE),
        },
        "runtimeEvidence": {
            "safeCopyLaunchLevel": 854,
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
        "fireBinding": {
            "copiedDefaultOptionsFireWeaponQe": True,
            "controlOptionsProofLever": "copied-defaultoptions-weapon-fire-qe",
            "sourceExpectedFireButton": EXPECTED_SOURCE_FIRE_BUTTON,
            "observedRuntimeFireButton": OBSERVED_RUNTIME_FIRE_BUTTON,
            "button18DispatchCount": total_button18,
            "button19DispatchCount": total_button19,
            "button18RuntimeDispatchObserved": total_button18 > 0,
            "button19RuntimeDispatchObserved": total_button19 > 0,
            "expectedSourceButton18NotRuntimeObserved": total_button18 == 0,
        },
        "fireHandoff": {
            "inputWindowCount": len(windows),
            "stimulusWindowCount": len([row for row in windows if row["stimulusWindow"]]),
            "waitControlWindowCount": len([row for row in windows if not row["stimulusWindow"]]),
            "sameWindowInputFireHandoffWindowCount": len(positive_windows),
            "sameWindowInputFireHandoffObserved": bool(positive_windows),
            "sameWindowFireBurstPointerChainWindowCount": len(pointer_chain_windows),
            "sameWindowFireBurstPointerChainObserved": bool(pointer_chain_windows),
            "sameWindowOrderedFireBurstPointerChainWindowCount": len(ordered_pointer_chain_windows),
            "sameWindowOrderedFireBurstPointerChainObserved": bool(ordered_pointer_chain_windows),
            "fireBurstPointerChainContexts": unique_sorted(
                {
                    context
                    for row in pointer_chain_windows
                    for context in row["fireBurstPointerChain"]["correlatedWeaponBurstContexts"]
                }
            ),
            "orderedFireBurstPointerChainContexts": unique_sorted(
                {
                    context
                    for row in ordered_pointer_chain_windows
                    for context in row["fireBurstPointerChain"]["orderedCorrelatedWeaponBurstContexts"]
                }
            ),
            "waitWindowFireButtonDispatchCount": wait_button_count,
            "waitWindowAmbientHandoffHitCount": wait_handoff_count,
            "waitWindowCausalProof": False,
            "roundProjectileTotalHitCount": parsed["roundProjectileHitCount"],
            "battleEngineProjectileTotalHitCount": parsed["battleEngineProjectileHitCount"],
            "shellMaterializationTotalHitCount": sum(parsed["hitCounts"][name] for name in SHELL_TARGET_NAMES),
            "projectileFactoryTotalHitCount": sum(parsed["hitCounts"][name] for name in PROJECTILE_FACTORY_TARGET_NAMES),
            "sameWindowBattleEngineProjectileObserved": any(row["sameWindowBattleEngineProjectile"] for row in windows),
            "sameWindowShellMaterializationObserved": any(row["sameWindowShellMaterialization"] for row in windows),
            "sameWindowProjectileFactoryObserved": any(row["sameWindowProjectileFactory"] for row in windows),
            "roundProjectileSameWindowCoincidenceObserved": any(row["sameWindowRoundProjectileCausality"] for row in windows),
            "roundDefinitionCorrelationObserved": any(
                row["fireBurstPointerChain"]["roundDefinitionCorrelationObserved"] for row in windows
            ),
            "roundProjectileSameWindowCausalityProof": False,
            "inputWindowSummaries": windows,
        },
        "handoffSurface": {
            "hookTargets": TARGETS,
            "hookTargetCount": parsed["hookTargetCount"],
            "expectedHookTargetCount": len(TARGETS),
            "hitCounts": parsed["hitCounts"],
            "buttonCounts": parsed["buttonCounts"],
            "directFireDispatchHitCount": parsed["directFireDispatchHitCount"],
            "burstOrProjectilePresetHitCount": parsed["burstOrProjectilePresetHitCount"],
            "battleEngineProjectileHitCount": parsed["battleEngineProjectileHitCount"],
            "shellMaterializationHitCount": sum(parsed["hitCounts"][name] for name in SHELL_TARGET_NAMES),
            "projectileFactoryHitCount": sum(parsed["hitCounts"][name] for name in PROJECTILE_FACTORY_TARGET_NAMES),
            "roundProjectileHitCount": parsed["roundProjectileHitCount"],
            "modeRuntimeProofSlicesAdded": 0,
            "coOpVersusModeRuntimeProofSlicesAdded": 0,
            "currentRuntimeModeClassification": "unclassified-local-multiplayer",
        },
        "slotBoundary": {
            "acceptedOriginalBinaryGameplaySlots": observer.EXPECTED_ACTIVE_SLOTS,
            "metadataOnlySlots": observer.EXPECTED_METADATA_SLOTS,
            "rejectedGameplayRouteSlots": observer.EXPECTED_METADATA_SLOTS,
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
            "runtimeOutcomeProof": False,
            "damageProof": False,
            "killProof": False,
            "visualProjectileProof": False,
            "exactCWeaponFireSourceIdentity": False,
            "exactCBattleEngineWeaponFiredIdentity": False,
            "roundProjectileCausalityProof": False,
            "stealthOrCloakProof": False,
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
            "This is a copied original-binary level-854/config-1 P1/P2 fire-input-to-weapon-handoff proof. "
            "It materializes Fire weapon Q/E only in the copied defaultoptions.bea, launches a safe copied executable, "
            "attaches CDB to the exact managed PID, and requires same-window observed runtime button 19 dispatch plus "
            "weapon/fire handoff hits and at least one pointer-correlated WeaponFired.weapon -> CWeapon::HandleFireBurstEvent.this -> "
            "ProjectileBurst context chain. Ordered fire/burst correlation is tracked separately and remains false when the correlated "
            "runtime sequence is not WeaponFired -> CWeapon::HandleFireBurstEvent -> ProjectileBurst. The source-expected button 18 did not dispatch in this run, so button18RuntimeDispatchObserved=false "
            "and button19RuntimeDispatchObserved=true are part of the accepted claim boundary. Wait-window burst or handoff hits are "
            "ambient and not causal proof. This is not base online multiplayer, not second-host LAN, not public matchmaking, "
            "not native BEA netcode, not runtime outcome/damage/kill proof, not active P3/P4 gameplay, not exact CWeapon::Fire "
            "source identity, not round-projectile causality unless separately promoted, and not rebuild/no-noticeable-difference parity."
        ),
    }
    write_json(output_path, bundle)
    return bundle


def build_live_bundle(artifact_root: Path, output_path: Path, *, exe_override: Path) -> dict[str, Any]:
    artifact_root = require_private_path(artifact_root)
    last_failure: tuple[int, Path, str] | None = None
    retried_after_foreground_abort = False
    retried_after_pointer_chain_miss = False
    for attempt in range(1, MAX_LIVE_SMOKE_ATTEMPTS + 1):
        current_root = require_private_path(live_attempt_root(artifact_root, attempt))
        current_root.mkdir(parents=True, exist_ok=True)
        command = [
            sys.executable,
            str(ROOT / "tools" / "winui_safe_copy_live_runtime_smoke.py"),
            "--artifact-root",
            str(current_root),
            "--arm-live-bea",
            "LAUNCH SAFE COPY BEA",
            "--timeout-seconds",
            "35",
            "--capture-count",
            "2",
            "--pre-input-capture-count",
            "1",
            "--focus-before-pre-input-capture",
            "--capture-after-each-input-sequence",
            "--after-input-capture-delay-ms",
            "350",
            "--capture-interval-seconds",
            "1",
            "--post-window-delay-seconds",
            "3",
            "--level-id",
            "854",
            "--controller-configuration",
            "1",
            "--bind-fire-qe-for-weapon-handoff",
            "--enable-cdb-observer",
            "--arm-cdb-observer",
            "ATTACH CDB TO SAFE COPY BEA",
            "--cdb-command-file",
            str(COMMAND_FILE.relative_to(ROOT)),
            "--cdb-log-ready-timeout-ms",
            "15000",
            "--cdb-post-attach-wait-seconds",
            "2",
            "--input-step-delay-ms",
            "100",
            "--exe-override",
            str(exe_override),
        ]
        for sequence in INPUT_SEQUENCES:
            command.extend(["--input-sequence", sequence])
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
        (current_root / "fire-handoff-builder-stdout.log").write_text(result.stdout, encoding="utf-8")
        (current_root / "fire-handoff-builder-stderr.log").write_text(result.stderr, encoding="utf-8")
        runtime_artifact = current_root / "live-safe-copy-runtime-smoke.json"
        if result.returncode == 0:
            try:
                bundle = build_bundle_from_runtime(runtime_artifact, output_path, fresh_live_execution=True)
            except Level854FireHandoffBuildError as exc:
                pointer_chain_miss = POINTER_CHAIN_MISSING_TOKEN in str(exc) and runtime_artifact_has_basic_fire_handoff(runtime_artifact)
                last_failure = (result.returncode, current_root, "pointer-chain-miss" if pointer_chain_miss else "promotion-error")
                if pointer_chain_miss and attempt < MAX_LIVE_SMOKE_ATTEMPTS:
                    retried_after_pointer_chain_miss = True
                    continue
                raise
            bundle["runtimeEvidence"]["liveSmokeExitCode"] = result.returncode
            bundle["runtimeEvidence"]["liveSmokeAcceptedDespiteNonzeroExit"] = False
            bundle["runtimeEvidence"]["liveSmokeAttemptCount"] = attempt
            bundle["runtimeEvidence"]["liveSmokeRetriedAfterForegroundAbort"] = retried_after_foreground_abort
            bundle["runtimeEvidence"]["liveSmokeRetriedAfterPointerChainMiss"] = retried_after_pointer_chain_miss
            write_json(output_path, bundle)
            return bundle
        foreground_abort = runtime_artifact_has_foreground_abort(runtime_artifact)
        last_failure = (result.returncode, current_root, "foreground-abort" if foreground_abort else "process-error")
        if not foreground_abort:
            break
        retried_after_foreground_abort = True
    if last_failure is None:
        raise Level854FireHandoffBuildError("live level854 fire-handoff smoke did not run")
    exit_code, failed_root, reason = last_failure
    retry_note = ""
    if reason == "foreground-abort":
        retry_note = " after retryable foreground focus-loss attempts"
    elif reason == "pointer-chain-miss":
        retry_note = " after retryable pointer-chain miss attempts"
    raise Level854FireHandoffBuildError(
        "live level854 fire-handoff smoke failed"
        f"{retry_note} with exit {exit_code}; see {failed_root / 'fire-handoff-builder-stderr.log'}"
    )


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
                "proofScope": bundle["proofScope"],
                "button18DispatchCount": bundle["fireBinding"]["button18DispatchCount"],
                "button19DispatchCount": bundle["fireBinding"]["button19DispatchCount"],
                "sameWindowInputFireHandoffWindowCount": bundle["fireHandoff"]["sameWindowInputFireHandoffWindowCount"],
                "sameWindowFireBurstPointerChainWindowCount": bundle["fireHandoff"]["sameWindowFireBurstPointerChainWindowCount"],
                "roundProjectileTotalHitCount": bundle["fireHandoff"]["roundProjectileTotalHitCount"],
                "roundProjectileSameWindowCausalityProof": bundle["fireHandoff"]["roundProjectileSameWindowCausalityProof"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Level854FireHandoffBuildError as exc:
        print(f"WinUI original-binary level854 fire-handoff build: FAIL: {exc}")
        raise SystemExit(2)
