#!/usr/bin/env python3
"""Build a private level-854 fire-to-damage/outcome observer bundle."""

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

import build_winui_original_binary_level854_fire_handoff_bundle as fire
import build_winui_original_binary_level854_outcome_semantics_observer_bundle as observer


ROOT = Path(__file__).resolve().parents[1]
PRIVATE_PROOF_ROOT = observer.PRIVATE_PROOF_ROOT
DEFAULT_ARTIFACT_ROOT = PRIVATE_PROOF_ROOT / "level854-fire-damage-outcome-20260619"
DEFAULT_OUTPUT = DEFAULT_ARTIFACT_ROOT / "level854-fire-damage-outcome-proof.json"
DEFAULT_EXE_OVERRIDE = observer.DEFAULT_EXE_OVERRIDE
COMMAND_FILE = ROOT / "tools" / "runtime-probes" / "local-multiplayer-level854-fire-damage-outcome-observer.cdb.txt"

SCHEMA = "winui-original-binary-level854-fire-damage-outcome.v1"
PROTOCOL = "level854-fire-damage-outcome.v1"
HELPER = "winui-original-binary-level854-fire-damage-outcome"
HELPER_VERSION = "level854-fire-damage-outcome.v1"
SCOPE = "level854-fire-to-damage-outcome-observer-not-online-proof"
RUNTIME_PROFILE = observer.RUNTIME_PROFILE
EXPECTED_SOURCE_FIRE_BUTTON = fire.EXPECTED_SOURCE_FIRE_BUTTON
OBSERVED_RUNTIME_FIRE_BUTTON = fire.OBSERVED_RUNTIME_FIRE_BUTTON
INPUT_SEQUENCES = fire.INPUT_SEQUENCES

TARGETS: tuple[dict[str, str], ...] = (
    {"name": "CGame__Render", "address": "0x0046e460", "category": "p1p2-render-graph"},
    {"name": "CController__SendButtonAction", "address": "0x0042e4d0", "category": "input-dispatch"},
    {"name": "CPlayer__ReceiveButtonAction", "address": "0x004d3110", "category": "input-dispatch"},
    {"name": "CBattleEngineWalkerPart__FireWeapon", "address": "0x00413cc0", "category": "walkerpart-fire-entry"},
    {"name": "CBattleEngineWalkerPart__WeaponFired", "address": "0x004140d0", "category": "walkerpart-fired-bookkeeping"},
    {"name": "CWeapon__HandleFireBurstEvent", "address": "0x00506930", "category": "weapon-burst-event"},
    {"name": "ProjectileBurst__SpawnFromCurrentPreset", "address": "0x005069f0", "category": "projectile-burst-current-preset"},
    {"name": "ProjectileBurst__SpawnFromPercentBucketFallback", "address": "0x00506010", "category": "projectile-burst-fallback"},
    {"name": "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles", "address": "0x00406560", "category": "battleengine-projectile-updater"},
    {"name": "CBattleEngine__AddProjectile", "address": "0x00406fc0", "category": "battleengine-projectile-add"},
    {"name": "CWorldPhysicsManager__CreateProjectile", "address": "0x0050f7a0", "category": "projectile-factory"},
    {"name": "CRound__ctor", "address": "0x004d81e0", "category": "round-projectile-factory"},
    {"name": "CRound__SpawnConfiguredProjectile", "address": "0x004db150", "category": "round-projectile-spawn"},
    {"name": "VFuncSlot_39_004d8ae0", "address": "0x004d8ae0", "category": "round-collision-hit"},
    {"name": "CUnit__ApplyDamage", "address": "0x004f9a90", "category": "unit-damage"},
    {"name": "CBattleEngine__StartDieProcess", "address": "0x0040bfd0", "category": "death-start"},
    {"name": "CGame__DeclarePlayerDead", "address": "0x0046f550", "category": "death-transition"},
    {"name": "CGame__RespawnPlayer", "address": "0x00470120", "category": "respawn-transition"},
    {"name": "CGame__MPDeclarePlayerWon", "address": "0x0046f360", "category": "multiplayer-win-transition"},
    {"name": "CGame__MPDeclareGameDrawn", "address": "0x0046f3e0", "category": "multiplayer-draw-transition"},
    {"name": "CGame__DeclareLevelWon", "address": "0x0046f2f0", "category": "level-win-transition"},
    {"name": "CGame__DeclareLevelLost", "address": "0x0046f430", "category": "level-loss-transition"},
)
TARGET_NAMES = [row["name"] for row in TARGETS]
INPUT_TARGET_NAMES = ["CController__SendButtonAction", "CPlayer__ReceiveButtonAction"]
FIRE_TARGET_NAMES = [
    "CBattleEngineWalkerPart__FireWeapon",
    "CBattleEngineWalkerPart__WeaponFired",
    "CWeapon__HandleFireBurstEvent",
    "ProjectileBurst__SpawnFromCurrentPreset",
    "ProjectileBurst__SpawnFromPercentBucketFallback",
]
PROJECTILE_TARGET_NAMES = [
    "CBattleEngine__UpdateAutoTargetSetAndFireProjectiles",
    "CBattleEngine__AddProjectile",
    "CWorldPhysicsManager__CreateProjectile",
    "CRound__ctor",
    "CRound__SpawnConfiguredProjectile",
]
DAMAGE_TARGET_NAMES = ["VFuncSlot_39_004d8ae0", "CUnit__ApplyDamage"]
OUTCOME_TARGET_NAMES = [
    "CBattleEngine__StartDieProcess",
    "CGame__DeclarePlayerDead",
    "CGame__RespawnPlayer",
    "CGame__MPDeclarePlayerWon",
    "CGame__MPDeclareGameDrawn",
    "CGame__DeclareLevelWon",
    "CGame__DeclareLevelLost",
]


class Level854FireDamageOutcomeBuildError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Level854FireDamageOutcomeBuildError(message)


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
    return PRIVATE_PROOF_ROOT / f"level854-fire-damage-outcome-live-{stamp}"


def relative_path(base: Path, target: Path) -> str:
    return os.path.relpath(target.resolve(), base.resolve()).replace("\\", "/")


def require_path_under(path: Path, root: Path, label: str) -> Path:
    resolved = path.resolve()
    root_resolved = root.resolve()
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise Level854FireDamageOutcomeBuildError(f"{label} must stay under {root_resolved}: {resolved}") from exc
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
    require(path.is_file(), f"fire/damage/outcome CDB command file missing: {path}")
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
        lowered = stripped.lower()
        for pattern in (r"\.shell\b", r"\.dump\b", r"\.writemem\b", r"\bed\s+", r"\beb\s+", r"\bew\s+", r"\beq\s+"):
            require(
                re.search(pattern, lowered) is None,
                f"CDB command line contains mutating command pattern: {pattern}",
            )
        if stripped.startswith(".echo") or stripped.startswith("bp ") or stripped == "g" or stripped in {"vertarget", "lm m BEA"}:
            continue
        raise Level854FireDamageOutcomeBuildError(f"CDB command file contains unsupported command: {stripped}")


def nonzero_hex(value: str) -> bool:
    try:
        return int(value, 16) != 0
    except ValueError:
        return False


def normalized_hex(value: str) -> str:
    return f"{int(value, 16):08x}"


def unique_sorted(values: set[str]) -> list[str]:
    return sorted(values, key=lambda item: int(item, 16))


HOOK_RE = re.compile(
    r"FIRE_DAMAGE_HOOK_TARGET name=(?P<name>[A-Za-z0-9_]+) address=(?P<address>0x[0-9a-fA-F]{8}) category=(?P<category>[A-Za-z0-9_-]+)"
)
HIT_RE = re.compile(r"FIRE_DAMAGE_HIT name=(?P<name>[A-Za-z0-9_]+)")
BUTTON_RE = re.compile(
    r"FIRE_DAMAGE_HIT name=(?:CController__SendButtonAction|CPlayer__ReceiveButtonAction)\b[^\n]*\bbutton=(?P<button>\d+)\b"
)
RENDER_RE = re.compile(
    r"FIRE_DAMAGE_HIT name=CGame__Render this=(?P<this>[0-9a-fA-F]+) players=(?P<players>\d+) "
    r"level=(?P<level>\d+) horizSplit=(?P<horizSplit>\d+) p0=(?P<p0>[0-9a-fA-F]+) "
    r"p1=(?P<p1>[0-9a-fA-F]+) cam0=(?P<cam0>[0-9a-fA-F]+) cam1=(?P<cam1>[0-9a-fA-F]+) world=(?P<world>[0-9a-fA-F]+)"
)
WEAPON_FIRED_RE = re.compile(
    r"FIRE_DAMAGE_HIT name=CBattleEngineWalkerPart__WeaponFired this=(?P<part>[0-9a-fA-F]+) weapon=(?P<weapon>[0-9a-fA-F]+)"
)
WEAPON_BURST_RE = re.compile(
    r"FIRE_DAMAGE_HIT name=CWeapon__HandleFireBurstEvent this=(?P<context>[0-9a-fA-F]+) "
    r"eventRecord=(?P<eventRecord>[0-9a-fA-F]+) eventHeadRaw=(?P<eventHeadRaw>[0-9a-fA-F]+)"
)
BURST_CONTEXT_RE = re.compile(
    r"FIRE_DAMAGE_HIT name=ProjectileBurst__(?:SpawnFromCurrentPreset|SpawnFromPercentBucketFallback) burstContext=(?P<context>[0-9a-fA-F]+)"
)
APPLY_DAMAGE_RE = re.compile(
    r"FIRE_DAMAGE_HIT name=CUnit__ApplyDamage this=(?P<target>[0-9a-fA-F]+) damageRaw=(?P<damageRaw>[0-9a-fA-F]+) "
    r"damageSource=(?P<source>[0-9a-fA-F]+) applyShields=(?P<applyShields>[0-9a-fA-F]+) "
    r"meshPartIndex=(?P<meshPartIndex>[0-9a-fA-F]+)"
)
ROUND_HIT_RE = re.compile(
    r"FIRE_DAMAGE_HIT name=VFuncSlot_39_004d8ae0 this=(?P<round>[0-9a-fA-F]+) other=(?P<other>[0-9a-fA-F]+)"
)


def count_hits(text: str, names: list[str]) -> dict[str, int]:
    return {name: len(re.findall(rf"FIRE_DAMAGE_HIT name={re.escape(name)}\b", text)) for name in names}


def count_buttons(text: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for match in BUTTON_RE.finditer(text):
        key = match.group("button")
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda item: int(item[0])))


def parse_fire_chain(text: str) -> dict[str, Any]:
    weapon_contexts = {
        normalized_hex(match.group("weapon"))
        for match in WEAPON_FIRED_RE.finditer(text)
        if nonzero_hex(match.group("weapon"))
    }
    burst_event_contexts = {
        normalized_hex(match.group("context"))
        for match in WEAPON_BURST_RE.finditer(text)
        if nonzero_hex(match.group("context"))
    }
    burst_spawn_contexts = {
        normalized_hex(match.group("context"))
        for match in BURST_CONTEXT_RE.finditer(text)
        if nonzero_hex(match.group("context"))
    }
    correlated = weapon_contexts & burst_event_contexts & burst_spawn_contexts
    return {
        "weaponFiredContexts": unique_sorted(weapon_contexts),
        "burstEventContexts": unique_sorted(burst_event_contexts),
        "burstSpawnContexts": unique_sorted(burst_spawn_contexts),
        "correlatedWeaponBurstContexts": unique_sorted(correlated),
        "fireBurstPointerChainObserved": bool(correlated),
    }


def parse_damage_identities(text: str) -> dict[str, Any]:
    damage_targets = {normalized_hex(match.group("target")) for match in APPLY_DAMAGE_RE.finditer(text)}
    damage_sources = {normalized_hex(match.group("source")) for match in APPLY_DAMAGE_RE.finditer(text)}
    round_others = {normalized_hex(match.group("other")) for match in ROUND_HIT_RE.finditer(text)}
    return {
        "damageTargetContexts": unique_sorted({value for value in damage_targets if nonzero_hex(value)}),
        "damageSourceContexts": unique_sorted({value for value in damage_sources if nonzero_hex(value)}),
        "roundCollisionOtherContexts": unique_sorted({value for value in round_others if nonzero_hex(value)}),
        "damageSourceMatchesRoundOtherContext": bool(damage_sources & round_others),
    }


def is_wait_only_sequence(sequence: str) -> bool:
    return fire.is_wait_only_sequence(sequence)


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
    missing_hooks = [target["name"] for target in TARGETS if target["name"] not in hooks]
    wrong_hooks = [
        target["name"]
        for target in TARGETS
        if target["name"] in hooks and hooks[target["name"]]["address"] != target["address"].lower()
    ]
    require(not missing_hooks, f"CDB log missing fire/damage/outcome hook target echoes: {', '.join(missing_hooks)}")
    require(not wrong_hooks, f"CDB log has wrong fire/damage/outcome hook target addresses: {', '.join(wrong_hooks)}")
    render_match = RENDER_RE.search(text)
    require(render_match is not None, "CDB log missing CGame__Render fire/damage observation")
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
    require(render["players"] == 2, "render observation did not report two players")
    require(render["level"] == 854, "render observation did not report level 854")
    require(render["horizSplit"] == 1, "render observation did not report horizontal split")
    require(nonzero_hex(render["p0"]) and nonzero_hex(render["p1"]) and render["p0"] != render["p1"], "invalid P1/P2 render pointers")
    return {
        "hookTargets": hooks,
        "hookTargetCount": len(hooks),
        "hitCounts": hit_counts,
        "buttonCounts": count_buttons(text),
        "render": render,
        "fireHitCount": sum(hit_counts[name] for name in FIRE_TARGET_NAMES),
        "projectileHitCount": sum(hit_counts[name] for name in PROJECTILE_TARGET_NAMES),
        "damageHitCount": sum(hit_counts[name] for name in DAMAGE_TARGET_NAMES),
        "unitApplyDamageHitCount": hit_counts["CUnit__ApplyDamage"],
        "roundCollisionHitCount": hit_counts["VFuncSlot_39_004d8ae0"],
        "outcomeHitCount": sum(hit_counts[name] for name in OUTCOME_TARGET_NAMES),
    }


def cdb_log_from_runtime(runtime_artifact: dict[str, Any]) -> Path:
    return observer.cdb_log_from_runtime(runtime_artifact)


def input_windows_from_runtime(runtime: dict[str, Any], log_path: Path) -> list[dict[str, Any]]:
    rows = list_at(runtime, "inputCdbWindows")
    data = log_path.resolve().read_bytes()
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
        fire_count = sum(hit_counts[name] for name in FIRE_TARGET_NAMES)
        projectile_count = sum(hit_counts[name] for name in PROJECTILE_TARGET_NAMES)
        unit_damage_count = hit_counts["CUnit__ApplyDamage"]
        round_collision_count = hit_counts["VFuncSlot_39_004d8ae0"]
        outcome_count = sum(hit_counts[name] for name in OUTCOME_TARGET_NAMES)
        damage_identities = parse_damage_identities(text)
        fire_chain = parse_fire_chain(text)
        button19 = button_counts.get(str(OBSERVED_RUNTIME_FIRE_BUTTON), 0)
        windows.append(
            {
                "index": index,
                "sequence": sequence,
                "stimulusWindow": stimulus,
                "byteCount": end - start,
                "button18DispatchCount": button_counts.get(str(EXPECTED_SOURCE_FIRE_BUTTON), 0),
                "button19DispatchCount": button19,
                "fireHitCount": fire_count,
                "projectileHitCount": projectile_count,
                "unitApplyDamageHitCount": unit_damage_count,
                "roundCollisionHitCount": round_collision_count,
                "damageHitCount": unit_damage_count + round_collision_count,
                "outcomeHitCount": outcome_count,
                "sameWindowFireHandoff": stimulus and button19 > 0 and fire_count > 0,
                "sameWindowProjectileSurface": stimulus and projectile_count > 0,
                "sameWindowDamageSurface": stimulus and (unit_damage_count + round_collision_count) > 0,
                "sameWindowUnitApplyDamage": stimulus and unit_damage_count > 0,
                "sameWindowOutcomeSurface": stimulus and outcome_count > 0,
                "fireBurstPointerChain": fire_chain,
                "damageIdentities": damage_identities,
            }
        )
    windows.sort(key=lambda item: int(item["index"]))
    require([row["sequence"] for row in windows] == INPUT_SEQUENCES, "input CDB window sequence list mismatch")
    return windows


def require_control_options(runtime: dict[str, Any]) -> None:
    return fire.require_control_options(runtime)


def validate_runtime_artifact(runtime_path: Path) -> tuple[dict[str, Any], Path, dict[str, Any], list[dict[str, Any]]]:
    runtime_path = require_private_path(runtime_path, must_exist=True)
    runtime_root = runtime_path.parent.resolve()
    expected_cdb_root = runtime_root / "cdb"
    runtime = read_json(runtime_path)
    require(runtime.get("schemaVersion") == "winui-safe-copy-live-runtime-smoke.v1", "unexpected runtime artifact schema")
    require(object_at(runtime, "launch").get("arguments") == ["-skipfmv", "-level", "854", "-configuration", "1"], "runtime launch arguments must be -skipfmv -level 854 -configuration 1")
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
    require(input_plan.get("inputSequenceCount") == len(INPUT_SEQUENCES), "unexpected fire/damage input sequence count")
    require(input_plan.get("allowBackgroundWindowMessages") is False, "background window messages are not allowed")
    require(input_summary.get("inputSequencesSent") == input_plan.get("inputSequenceCount"), "not every input sequence was sent")
    require(input_summary.get("focusedInputSequences") == input_plan.get("inputSequenceCount"), "not every input sequence was focused")
    require(input_summary.get("inputWindowMessageEventsSent", 0) == 0, "background/window-message input is not allowed")
    require(input_summary.get("inputKeyEventsSent", 0) > 0, "fire/damage observer needs real key input")
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
    return runtime, log_path, parsed, windows


def build_bundle_from_runtime(runtime_path: Path, output_path: Path, *, fresh_live_execution: bool = False) -> dict[str, Any]:
    output_path = require_private_path(output_path)
    runtime, log_path, parsed, windows = validate_runtime_artifact(runtime_path)
    captures = runtime.get("captures") if isinstance(runtime.get("captures"), list) else []
    visual_count = len([row for row in captures if isinstance(row, dict) and row.get("visualProof") is True])
    render = parsed["render"]
    stimulus_windows = [row for row in windows if row["stimulusWindow"]]
    wait_windows = [row for row in windows if not row["stimulusWindow"]]
    fire_windows = [row for row in stimulus_windows if row["sameWindowFireHandoff"]]
    pointer_chain_windows = [
        row
        for row in stimulus_windows
        if row["fireBurstPointerChain"]["fireBurstPointerChainObserved"]
    ]
    damage_windows = [row for row in stimulus_windows if row["sameWindowDamageSurface"]]
    unit_damage_windows = [row for row in stimulus_windows if row["sameWindowUnitApplyDamage"]]
    outcome_windows = [row for row in stimulus_windows if row["sameWindowOutcomeSurface"]]
    wait_button_count = sum(int(row["button19DispatchCount"]) for row in wait_windows)
    wait_damage_count = sum(int(row["damageHitCount"]) for row in wait_windows)
    wait_outcome_count = sum(int(row["outcomeHitCount"]) for row in wait_windows)
    total_button18 = sum(int(row["button18DispatchCount"]) for row in windows)
    total_button19 = sum(int(row["button19DispatchCount"]) for row in windows)
    require(wait_button_count == 0, "wait/no-input windows must not contain fire button dispatch")
    require(total_button19 > 0, "runtime did not dispatch observed fire button 19")
    require(total_button18 == 0, "source-expected button 18 was observed; update the claim boundary before accepting")
    require(fire_windows, "no same-window fire handoff window was observed")
    require(pointer_chain_windows, "no same-window fire-to-burst pointer chain was observed")
    damage_proof = bool(unit_damage_windows) and wait_damage_count == 0
    outcome_proof = bool(outcome_windows) and wait_outcome_count == 0
    damage_source_matches_round = any(
        row["damageIdentities"]["damageSourceMatchesRoundOtherContext"] for row in damage_windows
    )
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
        "fireDamageOutcome": {
            "copiedDefaultOptionsFireWeaponQe": True,
            "controlOptionsProofLever": "copied-defaultoptions-weapon-fire-qe",
            "button18DispatchCount": total_button18,
            "button19DispatchCount": total_button19,
            "button18RuntimeDispatchObserved": total_button18 > 0,
            "button19RuntimeDispatchObserved": total_button19 > 0,
            "inputWindowCount": len(windows),
            "stimulusWindowCount": len(stimulus_windows),
            "waitControlWindowCount": len(wait_windows),
            "sameWindowFireHandoffWindowCount": len(fire_windows),
            "sameWindowFireBurstPointerChainWindowCount": len(pointer_chain_windows),
            "sameWindowProjectileSurfaceWindowCount": len([row for row in stimulus_windows if row["sameWindowProjectileSurface"]]),
            "sameWindowDamageSurfaceWindowCount": len(damage_windows),
            "sameWindowUnitApplyDamageWindowCount": len(unit_damage_windows),
            "sameWindowOutcomeSurfaceWindowCount": len(outcome_windows),
            "waitWindowFireButtonDispatchCount": wait_button_count,
            "waitWindowDamageHitCount": wait_damage_count,
            "waitWindowOutcomeHitCount": wait_outcome_count,
            "fireHitCount": parsed["fireHitCount"],
            "projectileHitCount": parsed["projectileHitCount"],
            "damageHitCount": parsed["damageHitCount"],
            "unitApplyDamageHitCount": parsed["unitApplyDamageHitCount"],
            "roundCollisionHitCount": parsed["roundCollisionHitCount"],
            "outcomeHitCount": parsed["outcomeHitCount"],
            "damageSourceMatchesRoundOtherContext": damage_source_matches_round,
            "damageProof": damage_proof,
            "runtimeOutcomeProof": outcome_proof,
            "fireToDamageOutcomePromotion": damage_proof and outcome_proof,
            "inputWindowSummaries": windows,
        },
        "observerSurface": {
            "hookTargets": TARGETS,
            "hookTargetCount": parsed["hookTargetCount"],
            "expectedHookTargetCount": len(TARGETS),
            "hitCounts": parsed["hitCounts"],
            "buttonCounts": parsed["buttonCounts"],
            "damageTargets": DAMAGE_TARGET_NAMES,
            "outcomeTargets": OUTCOME_TARGET_NAMES,
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
            "This is a copied original-binary level-854/config-1 P1/P2 fire-to-damage/outcome observer. "
            "It materializes Fire weapon Q/E only in copied defaultoptions.bea, launches a safe copied executable, "
            "attaches CDB to the exact managed PID, and requires same-window runtime button 19 fire handoff plus a "
            "fire-to-burst pointer chain before evaluating damage/outcome counters. Damage proof is promoted only when "
            "CUnit__ApplyDamage appears inside a stimulus window and no wait/no-input window contains damage hits. "
            "Runtime outcome proof is promoted only when death/respawn/win/loss hooks appear inside a stimulus window "
            "and no wait/no-input window contains outcome hits. This is not base online multiplayer, not second-host LAN, "
            "not public matchmaking, not native BEA netcode, not active P3/P4 gameplay, not more-than-two-player proof, "
            "and not rebuild/no-noticeable-difference parity."
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
    (artifact_root / "fire-damage-outcome-builder-stdout.log").write_text(result.stdout, encoding="utf-8")
    (artifact_root / "fire-damage-outcome-builder-stderr.log").write_text(result.stderr, encoding="utf-8")
    runtime_artifact = artifact_root / "live-safe-copy-runtime-smoke.json"
    if result.returncode != 0:
        raise Level854FireDamageOutcomeBuildError(
            "live level854 fire/damage/outcome smoke failed with exit "
            f"{result.returncode}; see {artifact_root / 'fire-damage-outcome-builder-stderr.log'}"
        )
    bundle = build_bundle_from_runtime(runtime_artifact, output_path, fresh_live_execution=True)
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
    section = bundle["fireDamageOutcome"]
    print(
        json.dumps(
            {
                "artifact": str(args.output),
                "schemaVersion": bundle["schemaVersion"],
                "proofScope": bundle["proofScope"],
                "button19DispatchCount": section["button19DispatchCount"],
                "sameWindowFireHandoffWindowCount": section["sameWindowFireHandoffWindowCount"],
                "sameWindowUnitApplyDamageWindowCount": section["sameWindowUnitApplyDamageWindowCount"],
                "sameWindowOutcomeSurfaceWindowCount": section["sameWindowOutcomeSurfaceWindowCount"],
                "damageProof": section["damageProof"],
                "runtimeOutcomeProof": section["runtimeOutcomeProof"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Level854FireDamageOutcomeBuildError as exc:
        print(f"WinUI original-binary level854 fire/damage/outcome build: FAIL: {exc}")
        raise SystemExit(2)
