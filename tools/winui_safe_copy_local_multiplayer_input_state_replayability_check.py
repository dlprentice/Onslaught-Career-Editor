#!/usr/bin/env python3
"""Validate repeated local-multiplayer input-to-state proof artifacts."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_local_multiplayer_input_state_delta_check as state_delta


class StateReplayabilityError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise StateReplayabilityError(message)


def validate_artifact_pair(
    paths: list[Path],
    min_capture_count: int,
    *,
    expected_controller_configuration: int = 2,
    expected_qe_proof_lever: str = state_delta.DEFAULT_QE_PROOF_LEVER,
) -> dict[str, Any]:
    require(len(paths) >= 2, "at least two artifacts are required for state replayability")
    resolved_paths = [path.resolve() for path in paths]
    require(len(set(resolved_paths)) == len(resolved_paths), "artifact paths must be distinct")

    artifacts: list[dict[str, Any]] = []
    runtime_identities: set[tuple[Any, ...]] = set()
    process_ids: set[Any] = set()
    log_paths: set[str] = set()

    for path in paths:
        summary = state_delta.validate_artifact(
            path,
            min_capture_count=min_capture_count,
            expected_controller_configuration=expected_controller_configuration,
            expected_qe_proof_lever=expected_qe_proof_lever,
        )
        strict = summary.get("strictStateProof")
        require(isinstance(strict, dict), f"{path} missing strict state proof summary")
        windows = strict.get("windows")
        require(isinstance(windows, list) and len(windows) == 2, f"{path} did not produce exactly two strict state proof windows")

        def window_for(key: str) -> dict[str, Any]:
            matches = [
                row for row in windows
                if isinstance(row, dict) and f"down:{key.lower()}" in str(row.get("sequence", "")).lower()
            ]
            require(len(matches) == 1, f"{path} missing exactly one strict {key} state proof window")
            return matches[0]

        q = window_for("Q")
        e = window_for("E")
        require(q.get("inputDevice") == 0, f"{path} Q state proof did not use input device 0")
        require(e.get("inputDevice") == 1, f"{path} E state proof did not use input device 1")
        require(q.get("player") == summary.get("p0"), f"{path} Q state proof did not bind to P0")
        require(e.get("player") == summary.get("p1"), f"{path} E state proof did not bind to P1")
        require(q.get("routeType") in {"walker-forward", "jet-thrust"}, f"{path} Q state proof route is invalid")
        require(e.get("routeType") in {"walker-forward", "jet-thrust"}, f"{path} E state proof route is invalid")
        require(q.get("button31ReceiveRows", 0) > 0, f"{path} Q state proof has no button-31 receive rows")
        require(e.get("button31ReceiveRows", 0) > 0, f"{path} E state proof has no button-31 receive rows")
        require(q.get("nonzeroStoredLastMoveYValues"), f"{path} Q state proof has no nonzero store values")
        require(e.get("nonzeroStoredLastMoveYValues"), f"{path} E state proof has no nonzero store values")

        raw_artifact = state_delta.read_json(path)
        launch = raw_artifact.get("launch") if isinstance(raw_artifact.get("launch"), dict) else {}
        observer = raw_artifact.get("cdbObserver") if isinstance(raw_artifact.get("cdbObserver"), dict) else {}
        result = observer.get("result") if isinstance(observer.get("result"), dict) else {}
        process_id = launch.get("processId")
        log_path = str(result.get("logPath") or observer.get("logPath") or "")
        runtime_identity = (
            summary["p0"],
            summary["p1"],
            q["controller"],
            e["controller"],
            q["battleEngine"],
            e["battleEngine"],
            q["walker"],
            e["walker"],
        )
        require(runtime_identity not in runtime_identities, f"{path} repeats an earlier runtime identity")
        runtime_identities.add(runtime_identity)
        require(process_id not in process_ids, f"{path} repeats an earlier process id")
        process_ids.add(process_id)
        require(log_path not in log_paths, f"{path} repeats an earlier CDB log path")
        log_paths.add(log_path)

        artifacts.append(
            {
                "artifact": str(path),
                "processId": process_id,
                "cdbLogPath": log_path,
                "captureCount": summary["captureCount"],
                "visualCaptureCount": summary["visualCaptureCount"],
                "p0": summary["p0"],
                "p1": summary["p1"],
                "q": {
                    "role": "P0",
                    "inputDevice": q["inputDevice"],
                    "player": q["player"],
                    "controller": q["controller"],
                    "battleEngine": q["battleEngine"],
                    "walker": q["walker"],
                    "routeType": q["routeType"],
                    "button31ReceiveRows": q["button31ReceiveRows"],
                    "forwardStateStoreRows": q["forwardStateStoreRows"],
                    "nonzeroStoredLastMoveYValues": q["nonzeroStoredLastMoveYValues"],
                    "observedVectorDelta": q["observedVectorDelta"],
                },
                "e": {
                    "role": "P1",
                    "inputDevice": e["inputDevice"],
                    "player": e["player"],
                    "controller": e["controller"],
                    "battleEngine": e["battleEngine"],
                    "walker": e["walker"],
                    "routeType": e["routeType"],
                    "button31ReceiveRows": e["button31ReceiveRows"],
                    "forwardStateStoreRows": e["forwardStateStoreRows"],
                    "nonzeroStoredLastMoveYValues": e["nonzeroStoredLastMoveYValues"],
                    "observedVectorDelta": e["observedVectorDelta"],
                },
            }
        )

    return {
        "claim": f"repeated config-{expected_controller_configuration} movement-forward Q/E input-to-state replayability",
        "controllerConfiguration": expected_controller_configuration,
        "proofLever": expected_qe_proof_lever,
        "artifactCount": len(artifacts),
        "roleInvariant": "Q->P0/inputDevice0; E->P1/inputDevice1",
        "artifacts": artifacts,
        "claimBoundary": f"This proves the accepted level 850 config-{expected_controller_configuration} keyboard Q/E Movement/Forward input-to-state-store pattern repeats across distinct copied-profile artifacts with distinct process IDs, CDB logs, and runtime player/controller/BattleEngine/WalkerPart tuples. It compares player roles and input-device routing rather than requiring equal process-local pointers across runs, and does not prove visible movement causality, improved control feel, gamepad coverage, online networking, deterministic sync, exact full layout, or rebuild parity.",
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
        first = state_delta.make_artifact(first_root)
        second = state_delta.make_artifact(second_root)
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
        summary = validate_artifact_pair([first, second], min_capture_count=1)
        require(summary["artifactCount"] == 2, "expected two artifacts in replayability summary")
        require(summary["roleInvariant"] == "Q->P0/inputDevice0; E->P1/inputDevice1", "unexpected role invariant")
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
        first = state_delta.make_artifact(
            first_root,
            controller_configuration=1,
            qe_proof_lever="input-isolation-forward-qe",
        )
        second = state_delta.make_artifact(
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
            min_capture_count=1,
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
        first = state_delta.make_artifact(first_root)
        second = state_delta.make_artifact(second_root, missing_store=True)
        replace_fixture_pointers(second, {"04646090": "04aa0090", "0465d890": "04bb8890"})
        set_fixture_process_id(second, 5678)
        try:
            validate_artifact_pair([first, second], min_capture_count=1)
        except (StateReplayabilityError, state_delta.ArtifactError):
            pass
        else:
            raise StateReplayabilityError("missing state store should fail replayability")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "single"
        root.mkdir()
        path = state_delta.make_artifact(root)
        try:
            validate_artifact_pair([path, path], min_capture_count=1)
        except StateReplayabilityError:
            pass
        else:
            raise StateReplayabilityError("duplicate artifact paths should fail replayability")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        first_root = root / "same-runtime-different-pid-first"
        second_root = root / "same-runtime-different-pid-second"
        first_root.mkdir()
        second_root.mkdir()
        first = state_delta.make_artifact(first_root)
        second = state_delta.make_artifact(second_root)
        set_fixture_process_id(second, 5678)
        try:
            validate_artifact_pair([first, second], min_capture_count=1)
        except StateReplayabilityError:
            pass
        else:
            raise StateReplayabilityError("same runtime tuple with different process id should fail replayability")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        first_root = root / "same-runtime-first"
        second_root = root / "same-runtime-second"
        first_root.mkdir()
        second_root.mkdir()
        first = state_delta.make_artifact(first_root)
        second = state_delta.make_artifact(second_root)
        try:
            validate_artifact_pair([first, second], min_capture_count=1)
        except StateReplayabilityError:
            pass
        else:
            raise StateReplayabilityError("same runtime identity under distinct paths should fail replayability")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifacts", nargs="*", type=Path)
    parser.add_argument("--min-capture-count", type=int, default=1)
    parser.add_argument("--expected-controller-configuration", type=int, default=2, choices=(1, 2, 3, 4))
    parser.add_argument(
        "--expected-qe-proof-lever",
        default=state_delta.DEFAULT_QE_PROOF_LEVER,
        choices=tuple(state_delta.QE_PROOF_LEVERS),
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("WinUI safe-copy local multiplayer input-state replayability checker self-test: PASS")
        return 0
    summary = validate_artifact_pair(
        args.artifacts,
        min_capture_count=args.min_capture_count,
        expected_controller_configuration=args.expected_controller_configuration,
        expected_qe_proof_lever=args.expected_qe_proof_lever,
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (StateReplayabilityError, state_delta.ArtifactError) as exc:
        print(f"WinUI safe-copy local multiplayer input-state replayability check: FAIL: {exc}")
        raise SystemExit(2)
