#!/usr/bin/env python3
"""Validate repeated local-multiplayer visible movement-delta proof artifacts."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_local_multiplayer_visible_movement_delta_check as visible_delta


class VisibleMovementReplayabilityError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VisibleMovementReplayabilityError(message)


def validate_artifact_pair(
    paths: list[Path],
    *,
    min_capture_count: int,
    min_render_samples: int,
    pixel_threshold: int = 16,
    min_target_changed_ratio: float = 0.002,
    min_target_to_baseline_ratio: float = 1.25,
    min_target_to_nontarget_ratio: float = 1.05,
    expected_controller_configuration: int = 2,
    expected_qe_proof_lever: str = visible_delta.state_delta.DEFAULT_QE_PROOF_LEVER,
) -> dict[str, Any]:
    require(len(paths) >= 2, "at least two artifacts are required for visible movement replayability")
    resolved_paths = [path.resolve() for path in paths]
    require(len(set(resolved_paths)) == len(resolved_paths), "artifact paths must be distinct")

    artifacts: list[dict[str, Any]] = []
    runtime_identities: set[tuple[Any, ...]] = set()
    process_ids: set[Any] = set()
    log_paths: set[str] = set()

    for path in paths:
        summary = visible_delta.validate_artifact(
            path,
            min_capture_count=min_capture_count,
            min_render_samples=min_render_samples,
            pixel_threshold=pixel_threshold,
            min_target_changed_ratio=min_target_changed_ratio,
            min_target_to_baseline_ratio=min_target_to_baseline_ratio,
            min_target_to_nontarget_ratio=min_target_to_nontarget_ratio,
            expected_controller_configuration=expected_controller_configuration,
            expected_qe_proof_lever=expected_qe_proof_lever,
        )
        raw_artifact = visible_delta.read_json(path)
        launch = raw_artifact.get("launch") if isinstance(raw_artifact.get("launch"), dict) else {}
        observer = raw_artifact.get("cdbObserver") if isinstance(raw_artifact.get("cdbObserver"), dict) else {}
        result = observer.get("result") if isinstance(observer.get("result"), dict) else {}
        process_id = launch.get("processId")
        log_path = str(result.get("logPath") or observer.get("logPath") or "")
        q_state = summary["q"]["state"]
        e_state = summary["e"]["state"]

        require(q_state.get("inputDevice") == 0, f"{path} Q visible proof did not use input device 0")
        require(e_state.get("inputDevice") == 1, f"{path} E visible proof did not use input device 1")
        require(q_state.get("player") == summary.get("p0"), f"{path} Q visible proof did not bind to P0")
        require(e_state.get("player") == summary.get("p1"), f"{path} E visible proof did not bind to P1")
        require(
            q_state.get("targetPositionChanged") is True or q_state.get("targetVelocityChanged") is True,
            f"{path} Q visible proof lacks render movement-state delta",
        )
        require(
            e_state.get("targetPositionChanged") is True or e_state.get("targetVelocityChanged") is True,
            f"{path} E visible proof lacks render movement-state delta",
        )
        require(q_state.get("routeType") in {"walker-forward", "jet-thrust"}, f"{path} Q visible proof route is invalid")
        require(e_state.get("routeType") in {"walker-forward", "jet-thrust"}, f"{path} E visible proof route is invalid")

        runtime_identity = (
            summary["p0"],
            summary["p1"],
            q_state["controller"],
            e_state["controller"],
            q_state["battleEngine"],
            e_state["battleEngine"],
            q_state["walker"],
            e_state["walker"],
        )
        require(runtime_identity not in runtime_identities, f"{path} repeats an earlier runtime identity")
        runtime_identities.add(runtime_identity)
        require(process_id not in process_ids, f"{path} repeats an earlier process id")
        process_ids.add(process_id)
        require(log_path and log_path not in log_paths, f"{path} repeats an earlier CDB log path")
        log_paths.add(log_path)

        artifacts.append(
            {
                "artifact": str(path),
                "processId": process_id,
                "cdbLogPath": log_path,
                "p0": summary["p0"],
                "p1": summary["p1"],
                "q": {
                    "role": "P0",
                    "inputDevice": q_state["inputDevice"],
                    "player": q_state["player"],
                    "controller": q_state["controller"],
                    "battleEngine": q_state["battleEngine"],
                    "walker": q_state["walker"],
                    "routeType": q_state["routeType"],
                    "targetPositionChanged": q_state["targetPositionChanged"],
                    "targetVelocityChanged": q_state["targetVelocityChanged"],
                    "targetChangedRatio": summary["q"]["targetVisualDelta"]["changedRatio"],
                    "baselineChangedRatio": summary["q"]["baselineVisualDelta"]["changedRatio"],
                    "nonTargetChangedRatio": summary["q"]["nonTargetVisualDelta"]["changedRatio"],
                },
                "e": {
                    "role": "P1",
                    "inputDevice": e_state["inputDevice"],
                    "player": e_state["player"],
                    "controller": e_state["controller"],
                    "battleEngine": e_state["battleEngine"],
                    "walker": e_state["walker"],
                    "routeType": e_state["routeType"],
                    "targetPositionChanged": e_state["targetPositionChanged"],
                    "targetVelocityChanged": e_state["targetVelocityChanged"],
                    "targetChangedRatio": summary["e"]["targetVisualDelta"]["changedRatio"],
                    "baselineChangedRatio": summary["e"]["baselineVisualDelta"]["changedRatio"],
                    "nonTargetChangedRatio": summary["e"]["nonTargetVisualDelta"]["changedRatio"],
                },
            }
        )

    return {
        "claim": f"repeated config-{expected_controller_configuration} Movement/Forward visible movement-delta role replayability",
        "controllerConfiguration": expected_controller_configuration,
        "proofLever": expected_qe_proof_lever,
        "artifactCount": len(artifacts),
        "roleInvariant": "Q->P0/inputDevice0/top split half; E->P1/inputDevice1/bottom split half",
        "artifacts": artifacts,
        "claimBoundary": (
            f"This proves the accepted level 850 config-{expected_controller_configuration} keyboard Q/E Movement/Forward visible movement-delta pattern repeats across "
            "distinct copied-profile artifacts with distinct process IDs, CDB logs, and runtime player/controller/"
            "BattleEngine/WalkerPart tuples. It compares player roles, input-device routing, movement-state evidence, "
            "and split-screen target-half deltas rather than requiring equal process-local pointers across runs. It "
            "does not prove improved control feel, gamepad coverage, all controller configurations, online networking, "
            "deterministic sync, exact full layout, rebuild parity, or no-noticeable-difference parity."
        ),
    }


def replace_fixture_pointers(path: Path, replacements: dict[str, str]) -> None:
    artifact = json.loads(path.read_text(encoding="utf-8"))
    observer = artifact["cdbObserver"]
    result = observer["result"]
    log_path = Path(result["logPath"])
    log_text = log_path.read_text(encoding="utf-8")
    for old, new in replacements.items():
        log_text = log_text.replace(old, new)
    log_path.write_text(log_text, encoding="utf-8")


def set_fixture_process_id(path: Path, process_id: int) -> None:
    artifact = json.loads(path.read_text(encoding="utf-8"))
    artifact["launch"]["processId"] = process_id
    artifact["cdbObserver"]["result"]["targetProcessId"] = process_id
    path.write_text(json.dumps(artifact), encoding="utf-8")


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        first_root = root / "first"
        second_root = root / "second"
        first_root.mkdir()
        second_root.mkdir()
        first = visible_delta.make_visible_fixture(first_root)
        second = visible_delta.make_visible_fixture(second_root)
        replace_fixture_pointers(
            second,
            {
                "04646090": "04aa0090",
                "0465d890": "04bb8890",
                "046460f0": "04aa00f0",
                "0465d8f0": "04bb88f0",
                "03867570": "07aa7570",
                "0386d570": "07bbd570",
                "04700010": "04cc0010",
                "04710010": "04dd0010",
            },
        )
        set_fixture_process_id(second, 5678)
        summary = validate_artifact_pair([first, second], min_capture_count=5, min_render_samples=2)
        require(summary["artifactCount"] == 2, "expected two visible artifacts")
        require(
            summary["artifacts"][0]["q"]["player"] != summary["artifacts"][1]["q"]["player"],
            "self-test should accept different process-local P0 pointers",
        )

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        first_root = root / "config1-first"
        second_root = root / "config1-second"
        first_root.mkdir()
        second_root.mkdir()
        first = visible_delta.make_visible_fixture(
            first_root,
            controller_configuration=1,
            qe_proof_lever="input-isolation-forward-qe",
        )
        second = visible_delta.make_visible_fixture(
            second_root,
            controller_configuration=1,
            qe_proof_lever="input-isolation-forward-qe",
        )
        replace_fixture_pointers(
            second,
            {
                "04646090": "04aa0090",
                "0465d890": "04bb8890",
                "046460f0": "04aa00f0",
                "0465d8f0": "04bb88f0",
                "03867570": "07aa7570",
                "0386d570": "07bbd570",
                "04700010": "04cc0010",
                "04710010": "04dd0010",
            },
        )
        set_fixture_process_id(second, 5678)
        summary = validate_artifact_pair(
            [first, second],
            min_capture_count=5,
            min_render_samples=2,
            expected_controller_configuration=1,
            expected_qe_proof_lever="input-isolation-forward-qe",
        )
        require(summary["controllerConfiguration"] == 1, "expected config-1 replayability acceptance")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        first_root = root / "first"
        second_root = root / "second"
        first_root.mkdir()
        second_root.mkdir()
        first = visible_delta.make_visible_fixture(first_root)
        second = visible_delta.make_visible_fixture(second_root, collapse_e=True)
        replace_fixture_pointers(second, {"04646090": "04aa0090", "0465d890": "04bb8890"})
        set_fixture_process_id(second, 5678)
        try:
            validate_artifact_pair([first, second], min_capture_count=5, min_render_samples=2)
        except (
            VisibleMovementReplayabilityError,
            visible_delta.VisibleMovementDeltaError,
            visible_delta.movement_state.MovementStateDeltaError,
            visible_delta.state_delta.ArtifactError,
        ):
            pass
        else:
            raise VisibleMovementReplayabilityError("collapsed second visible artifact should fail replayability")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "single"
        root.mkdir()
        path = visible_delta.make_visible_fixture(root)
        try:
            validate_artifact_pair([path, path], min_capture_count=5, min_render_samples=2)
        except VisibleMovementReplayabilityError:
            pass
        else:
            raise VisibleMovementReplayabilityError("duplicate artifact paths should fail replayability")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        first_root = root / "same-runtime-different-pid-first"
        second_root = root / "same-runtime-different-pid-second"
        first_root.mkdir()
        second_root.mkdir()
        first = visible_delta.make_visible_fixture(first_root)
        second = visible_delta.make_visible_fixture(second_root)
        set_fixture_process_id(second, 5678)
        try:
            validate_artifact_pair([first, second], min_capture_count=5, min_render_samples=2)
        except VisibleMovementReplayabilityError:
            pass
        else:
            raise VisibleMovementReplayabilityError("same runtime tuple with different process id should fail replayability")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        first_root = root / "same-runtime-first"
        second_root = root / "same-runtime-second"
        first_root.mkdir()
        second_root.mkdir()
        first = visible_delta.make_visible_fixture(first_root)
        second = visible_delta.make_visible_fixture(second_root)
        try:
            validate_artifact_pair([first, second], min_capture_count=5, min_render_samples=2)
        except VisibleMovementReplayabilityError:
            pass
        else:
            raise VisibleMovementReplayabilityError("same runtime identity under distinct paths should fail replayability")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifacts", nargs="*", type=Path)
    parser.add_argument("--min-capture-count", type=int, default=5)
    parser.add_argument("--min-render-samples", type=int, default=2)
    parser.add_argument("--pixel-threshold", type=int, default=16)
    parser.add_argument("--min-target-changed-ratio", type=float, default=0.002)
    parser.add_argument("--min-target-to-baseline-ratio", type=float, default=1.25)
    parser.add_argument("--min-target-to-nontarget-ratio", type=float, default=1.05)
    parser.add_argument("--expected-controller-configuration", type=int, default=2, choices=(1, 2, 3, 4))
    parser.add_argument(
        "--expected-qe-proof-lever",
        default=visible_delta.state_delta.DEFAULT_QE_PROOF_LEVER,
        choices=tuple(visible_delta.state_delta.QE_PROOF_LEVERS),
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("WinUI safe-copy local multiplayer visible movement replayability checker self-test: PASS")
        return 0
    summary = validate_artifact_pair(
        args.artifacts,
        min_capture_count=args.min_capture_count,
        min_render_samples=args.min_render_samples,
        pixel_threshold=args.pixel_threshold,
        min_target_changed_ratio=args.min_target_changed_ratio,
        min_target_to_baseline_ratio=args.min_target_to_baseline_ratio,
        min_target_to_nontarget_ratio=args.min_target_to_nontarget_ratio,
        expected_controller_configuration=args.expected_controller_configuration,
        expected_qe_proof_lever=args.expected_qe_proof_lever,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        VisibleMovementReplayabilityError,
        visible_delta.VisibleMovementDeltaError,
        visible_delta.movement_state.MovementStateDeltaError,
        visible_delta.state_delta.ArtifactError,
    ) as exc:
        print(f"WinUI safe-copy local multiplayer visible movement replayability check: FAIL: {exc}")
        raise SystemExit(2)
