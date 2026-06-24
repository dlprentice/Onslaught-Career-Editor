#!/usr/bin/env python3
"""Validate local-multiplayer input-correlated movement-state delta artifacts."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import winui_safe_copy_local_multiplayer_input_state_delta_check as state_delta


class MovementStateDeltaError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise MovementStateDeltaError(message)


def count_by(values: list[str | int]) -> dict[str, int]:
    return {str(key): count for key, count in sorted(Counter(values).items(), key=lambda item: str(item[0]))}


def vector_tuple(raw: str) -> tuple[str, str, str]:
    parts = raw.split("/")
    require(len(parts) == 3, f"malformed vector tuple: {raw}")
    return tuple(part.lower() for part in parts)  # type: ignore[return-value]


def render_movement_rows(window_text: str) -> list[dict[str, Any]]:
    pattern = (
        r"CGame__RenderMovement this=([0-9a-fA-F]+) players=(\d+) level=(\d+) horizSplit=(\d+) "
        r"p0=([0-9a-fA-F]+) p1=([0-9a-fA-F]+) p0be=([0-9a-fA-F]+) p1be=([0-9a-fA-F]+) "
        r"p0pos=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) "
        r"p0oldpos=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) "
        r"p0vel=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) "
        r"p1pos=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) "
        r"p1oldpos=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+) "
        r"p1vel=([0-9a-fA-F]+/[0-9a-fA-F]+/[0-9a-fA-F]+)"
    )
    rows: list[dict[str, Any]] = []
    for match in re.finditer(pattern, window_text, flags=re.IGNORECASE):
        rows.append(
            {
                "game": match.group(1).lower(),
                "players": int(match.group(2)),
                "level": int(match.group(3)),
                "horizSplit": int(match.group(4)),
                "p0": match.group(5).lower(),
                "p1": match.group(6).lower(),
                "p0be": match.group(7).lower(),
                "p1be": match.group(8).lower(),
                "p0pos": vector_tuple(match.group(9)),
                "p0oldpos": vector_tuple(match.group(10)),
                "p0vel": vector_tuple(match.group(11)),
                "p1pos": vector_tuple(match.group(12)),
                "p1oldpos": vector_tuple(match.group(13)),
                "p1vel": vector_tuple(match.group(14)),
            }
        )
    return rows


def window_for(summary: dict[str, Any], key: str) -> dict[str, Any]:
    strict = summary.get("strictStateProof")
    require(isinstance(strict, dict), "missing strict state proof summary")
    windows = strict.get("windows")
    require(isinstance(windows, list), "strict state proof windows missing")
    matches = [
        row for row in windows
        if isinstance(row, dict) and f"down:{key.lower()}" in str(row.get("sequence", "")).lower()
    ]
    require(len(matches) == 1, f"expected exactly one strict {key} state proof window")
    return matches[0]


def movement_summary(
    *,
    artifact_path: Path,
    key: str,
    role: str,
    role_prefix: str,
    baseline_rows: list[dict[str, Any]],
    target_rows: list[dict[str, Any]],
    state_window: dict[str, Any],
    expected_player: str,
    min_render_samples: int,
) -> dict[str, Any]:
    require(len(baseline_rows) >= min_render_samples, f"{artifact_path} {key}/{role} baseline render sample count below {min_render_samples}")
    require(len(target_rows) >= min_render_samples, f"{artifact_path} {key}/{role} target render sample count below {min_render_samples}")
    for row in baseline_rows + target_rows:
        require(row["players"] == 2, f"{artifact_path} {key}/{role} render row did not report two players")
        require(row["level"] == 850, f"{artifact_path} {key}/{role} render row did not report level 850")
        require(row["horizSplit"] == 1, f"{artifact_path} {key}/{role} render row did not report horizontal split")

    pos_key = f"{role_prefix}pos"
    vel_key = f"{role_prefix}vel"
    baseline_positions = [row[pos_key] for row in baseline_rows]
    baseline_velocities = [row[vel_key] for row in baseline_rows]
    target_positions = [row[pos_key] for row in target_rows]
    target_velocities = [row[vel_key] for row in target_rows]
    target_position_changed = target_positions[0] != target_positions[-1]
    target_velocity_changed = target_velocities[0] != target_velocities[-1]
    target_differs_from_baseline = (
        target_positions[-1] != baseline_positions[-1]
        or target_velocities[-1] != baseline_velocities[-1]
    )
    require(target_position_changed or target_velocity_changed, f"{artifact_path} {key}/{role} target window had no render movement-state delta")
    require(target_differs_from_baseline, f"{artifact_path} {key}/{role} target window did not differ from adjacent no-input baseline")
    require(state_window.get("player") == expected_player, f"{artifact_path} {key}/{role} state window bound to unexpected player")
    require(state_window.get("observedVectorDelta") is True, f"{artifact_path} {key}/{role} state window did not report vector delta")
    require(state_window.get("nonzeroStoredLastMoveYValues"), f"{artifact_path} {key}/{role} has no nonzero movement-state store")

    return {
        "key": key,
        "role": role,
        "inputDevice": state_window.get("inputDevice"),
        "player": state_window.get("player"),
        "controller": state_window.get("controller"),
        "battleEngine": state_window.get("battleEngine"),
        "walker": state_window.get("walker"),
        "routeType": state_window.get("routeType"),
        "button31ReceiveRows": state_window.get("button31ReceiveRows"),
        "forwardStateStoreRows": state_window.get("forwardStateStoreRows"),
        "nonzeroStoredLastMoveYValues": state_window.get("nonzeroStoredLastMoveYValues"),
        "stateWindowPositionTupleCount": state_window.get("positionTupleCount"),
        "stateWindowVelocityTupleCount": state_window.get("velocityTupleCount"),
        "baselineRenderSamples": len(baseline_rows),
        "targetRenderSamples": len(target_rows),
        "baselinePositionTupleCounts": count_by(["/".join(value) for value in baseline_positions]),
        "targetPositionTupleCounts": count_by(["/".join(value) for value in target_positions]),
        "baselineVelocityTupleCounts": count_by(["/".join(value) for value in baseline_velocities]),
        "targetVelocityTupleCounts": count_by(["/".join(value) for value in target_velocities]),
        "targetPositionChanged": target_position_changed,
        "targetVelocityChanged": target_velocity_changed,
        "targetDiffersFromAdjacentBaseline": target_differs_from_baseline,
    }


def validate_artifact(
    path: Path,
    *,
    min_capture_count: int,
    min_render_samples: int,
    expected_controller_configuration: int = 2,
    expected_qe_proof_lever: str = state_delta.DEFAULT_QE_PROOF_LEVER,
) -> dict[str, Any]:
    state_summary = state_delta.validate_artifact(
        path,
        min_capture_count=min_capture_count,
        expected_controller_configuration=expected_controller_configuration,
        expected_qe_proof_lever=expected_qe_proof_lever,
    )
    raw_artifact = state_delta.read_json(path)
    observer = raw_artifact.get("cdbObserver") if isinstance(raw_artifact.get("cdbObserver"), dict) else {}
    result = observer.get("result") if isinstance(observer.get("result"), dict) else {}
    log_path = Path(str(result.get("logPath") or observer.get("logPath") or ""))
    require(log_path.is_file(), f"CDB log path is missing: {log_path}")

    windows = state_delta.sequence_windows_from_artifact(raw_artifact, log_path)
    require(set(windows) == {1, 2, 3, 4}, "movement-state delta expects wait/Q/wait/E CDB windows")
    wait1 = render_movement_rows(windows[1][2])
    q_rows = render_movement_rows(windows[2][2])
    wait3 = render_movement_rows(windows[3][2])
    e_rows = render_movement_rows(windows[4][2])
    require(wait1, "wait window 1 had no render movement samples")
    require(q_rows, "Q target window had no render movement samples")
    require(wait3, "wait window 3 had no render movement samples")
    require(e_rows, "E target window had no render movement samples")

    q = movement_summary(
        artifact_path=path,
        key="Q",
        role="P0",
        role_prefix="p0",
        baseline_rows=wait1,
        target_rows=q_rows,
        state_window=window_for(state_summary, "Q"),
        expected_player=str(state_summary["p0"]),
        min_render_samples=min_render_samples,
    )
    e = movement_summary(
        artifact_path=path,
        key="E",
        role="P1",
        role_prefix="p1",
        baseline_rows=wait3,
        target_rows=e_rows,
        state_window=window_for(state_summary, "E"),
        expected_player=str(state_summary["p1"]),
        min_render_samples=min_render_samples,
    )
    require(q["inputDevice"] == 0, f"{path} Q movement-state window did not use input device 0")
    require(e["inputDevice"] == 1, f"{path} E movement-state window did not use input device 1")

    return {
        "artifact": str(path),
        "claim": f"config-{expected_controller_configuration} Movement/Forward input-correlated movement-state delta",
        "controllerConfiguration": expected_controller_configuration,
        "proofLever": expected_qe_proof_lever,
        "captureCount": state_summary["captureCount"],
        "visualCaptureCount": state_summary["visualCaptureCount"],
        "p0": state_summary["p0"],
        "p1": state_summary["p1"],
        "q": q,
        "e": e,
        "claimBoundary": (
            f"This proves one copied-profile level 850 config-{expected_controller_configuration} keyboard Q/E Movement/Forward run where exact-PID CDB windows show "
            "clean no-input baselines, nonzero P0/P1 movement-state stores, and input-window render movement-state "
            "deltas for the matching player roles. It does not prove visible movement causality, improved control feel, "
            "gamepad coverage, all controller configurations, online networking, deterministic sync, exact full layout, "
            "rebuild parity, or no-noticeable-difference proof."
        ),
    }


def inject_render_rows(path: Path, *, collapse_q: bool = False, collapse_e: bool = False) -> None:
    artifact = json.loads(path.read_text(encoding="utf-8"))
    log_path = Path(artifact["cdbObserver"]["result"]["logPath"])
    text = log_path.read_text(encoding="utf-8")
    windows = artifact["inputCdbWindows"]
    chunks: list[str] = []
    cursor = 0
    p0 = "04646090"
    p1 = "0465d890"
    p0be = "03867570"
    p1be = "0386d570"

    def row(p0pos: str, p0vel: str, p1pos: str, p1vel: str) -> str:
        return (
            "CGame__RenderMovement this=008a9a98 players=2 level=850 horizSplit=1 "
            f"p0={p0} p1={p1} p0be={p0be} p1be={p1be} "
            f"p0pos={p0pos} p0oldpos=00000001/00000002/00000003 p0vel={p0vel} "
            f"p1pos={p1pos} p1oldpos=00000004/00000005/00000006 p1vel={p1vel} "
        )

    render_by_window = {
        1: row("00000001/00000002/00000003", "00000000/00000000/00000000", "00000004/00000005/00000006", "00000000/00000000/00000000")
        + row("00000001/00000002/00000003", "00000000/00000000/00000000", "00000004/00000005/00000006", "00000000/00000000/00000000"),
        2: row("00000001/00000002/00000003", "00000000/00000000/00000000", "00000004/00000005/00000006", "00000000/00000000/00000000")
        + row(
            "00000001/00000002/00000003" if collapse_q else "00000002/00000002/00000003",
            "00000000/00000000/00000000" if collapse_q else "00000000/bf000000/00000000",
            "00000004/00000005/00000006",
            "00000000/00000000/00000000",
        ),
        3: row("00000002/00000002/00000003", "00000000/00000000/00000000", "00000004/00000005/00000006", "00000000/00000000/00000000")
        + row("00000002/00000002/00000003", "00000000/00000000/00000000", "00000004/00000005/00000006", "00000000/00000000/00000000"),
        4: row("00000002/00000002/00000003", "00000000/00000000/00000000", "00000004/00000005/00000006", "00000000/00000000/00000000")
        + row(
            "00000002/00000002/00000003",
            "00000000/00000000/00000000",
            "00000004/00000005/00000006" if collapse_e else "00000005/00000005/00000006",
            "00000000/00000000/00000000" if collapse_e else "00000000/bf000000/00000000",
        ),
    }

    for window in windows:
        start = window["logStartByte"]
        end = window["logEndByte"]
        chunks.append(text[cursor:start])
        new_start = sum(len(chunk.encode("utf-8")) for chunk in chunks)
        window_text = render_by_window[window["index"]] + text[start:end]
        chunks.append(window_text)
        new_end = sum(len(chunk.encode("utf-8")) for chunk in chunks)
        window["logStartByte"] = new_start
        window["logEndByte"] = new_end
        cursor = end
    chunks.append(text[cursor:])
    log_path.write_text("".join(chunks), encoding="utf-8")
    path.write_text(json.dumps(artifact), encoding="utf-8")


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        path = state_delta.make_artifact(root)
        inject_render_rows(path)
        summary = validate_artifact(path, min_capture_count=1, min_render_samples=2)
        require(summary["q"]["targetPositionChanged"] is True, "Q target position should change")
        require(summary["e"]["targetPositionChanged"] is True, "E target position should change")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        path = state_delta.make_artifact(root, controller_configuration=1, qe_proof_lever="input-isolation-forward-qe")
        inject_render_rows(path)
        summary = validate_artifact(
            path,
            min_capture_count=1,
            min_render_samples=2,
            expected_controller_configuration=1,
            expected_qe_proof_lever="input-isolation-forward-qe",
        )
        require(summary["controllerConfiguration"] == 1, "config-1 movement-state proof should be accepted")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        path = state_delta.make_artifact(root)
        inject_render_rows(path, collapse_q=True)
        try:
            validate_artifact(path, min_capture_count=1, min_render_samples=2)
        except MovementStateDeltaError:
            pass
        else:
            raise MovementStateDeltaError("collapsed Q movement-state vectors should fail")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        path = state_delta.make_artifact(root)
        inject_render_rows(path, collapse_e=True)
        try:
            validate_artifact(path, min_capture_count=1, min_render_samples=2)
        except MovementStateDeltaError:
            pass
        else:
            raise MovementStateDeltaError("collapsed E movement-state vectors should fail")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", nargs="?", type=Path)
    parser.add_argument("--min-capture-count", type=int, default=1)
    parser.add_argument("--min-render-samples", type=int, default=2)
    parser.add_argument("--expected-controller-configuration", type=int, default=2, choices=(1, 2, 3, 4))
    parser.add_argument("--expected-qe-proof-lever", default=state_delta.DEFAULT_QE_PROOF_LEVER, choices=tuple(state_delta.QE_PROOF_LEVERS))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("WinUI safe-copy local multiplayer movement-state delta checker self-test: PASS")
        return 0
    if args.artifact is None:
        raise SystemExit("artifact is required unless --self-test is used")
    summary = validate_artifact(
        args.artifact,
        min_capture_count=args.min_capture_count,
        min_render_samples=args.min_render_samples,
        expected_controller_configuration=args.expected_controller_configuration,
        expected_qe_proof_lever=args.expected_qe_proof_lever,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (MovementStateDeltaError, state_delta.ArtifactError) as exc:
        print(f"WinUI safe-copy local multiplayer movement-state delta check: FAIL: {exc}")
        raise SystemExit(2)
