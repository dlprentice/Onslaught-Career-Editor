#!/usr/bin/env python3
"""Validate repeated config-2 local-multiplayer input-dispatch proof artifacts."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

import winui_safe_copy_local_multiplayer_input_dispatch_census_check as census


class ReplayabilityError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReplayabilityError(message)


def validate_artifact_pair(paths: list[Path], min_capture_count: int) -> dict[str, Any]:
    require(len(paths) >= 2, "at least two artifacts are required for replayability")
    resolved_paths = [path.resolve() for path in paths]
    require(len(set(resolved_paths)) == len(resolved_paths), "artifact paths must be distinct")

    artifacts: list[dict[str, Any]] = []
    runtime_identities: set[tuple[Any, ...]] = set()
    process_ids: set[Any] = set()
    log_paths: set[str] = set()
    for path in paths:
        summary = census.validate_artifact(
            path,
            min_capture_count=min_capture_count,
            expected_controller_configuration=2,
            require_config2_forward_qe_isolation=True,
        )
        strict = summary.get("strictConfig2ForwardQeIsolation")
        require(isinstance(strict, dict), f"{path} missing strict config-2 Q/E isolation summary")
        windows = strict.get("windows")
        require(isinstance(windows, list) and len(windows) == 2, f"{path} did not produce exactly two strict Q/E proof windows")

        def window_for(key: str) -> dict[str, Any]:
            matches = [row for row in windows if isinstance(row, dict) and f"down:{key.lower()}" in str(row.get("sequence", "")).lower()]
            if not matches:
                matches = [row for row in windows if isinstance(row, dict) and f"tap:{key.lower()}" in str(row.get("sequence", "")).lower()]
            require(len(matches) == 1, f"{path} missing exactly one strict {key} proof window")
            return matches[0]

        q = window_for("Q")
        e = window_for("E")
        require(q.get("inputDevice") == 0, f"{path} Q proof did not use input device 0")
        require(e.get("inputDevice") == 1, f"{path} E proof did not use input device 1")
        require(q.get("player") == summary.get("p0"), f"{path} Q proof did not bind to P0")
        require(e.get("player") == summary.get("p1"), f"{path} E proof did not bind to P1")
        require(q.get("button31SendRows", 0) > 0 and q.get("button31ReceiveRows", 0) > 0, f"{path} Q proof has no button-31 rows")
        require(e.get("button31SendRows", 0) > 0 and e.get("button31ReceiveRows", 0) > 0, f"{path} E proof has no button-31 rows")

        raw_artifact = census.read_json(path)
        launch = raw_artifact.get("launch") if isinstance(raw_artifact.get("launch"), dict) else {}
        observer = raw_artifact.get("cdbObserver") if isinstance(raw_artifact.get("cdbObserver"), dict) else {}
        result = observer.get("result") if isinstance(observer.get("result"), dict) else {}
        log_path = str(result.get("logPath") or observer.get("logPath") or "")
        process_id = launch.get("processId")
        runtime_identity = (
            process_id,
            summary["p0"],
            summary["p1"],
            q["controller"],
            e["controller"],
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
                    "button31SendRows": q["button31SendRows"],
                    "button31ReceiveRows": q["button31ReceiveRows"],
                },
                "e": {
                    "role": "P1",
                    "inputDevice": e["inputDevice"],
                    "player": e["player"],
                    "controller": e["controller"],
                    "button31SendRows": e["button31SendRows"],
                    "button31ReceiveRows": e["button31ReceiveRows"],
                },
            }
        )

    return {
        "claim": "repeated config-2 movement-forward Q/E button-31 dispatch role replayability",
        "artifactCount": len(artifacts),
        "roleInvariant": "Q->P0/inputDevice0; E->P1/inputDevice1",
        "artifacts": artifacts,
        "claimBoundary": "This proves the accepted config-2 Movement/Forward Q/E button-31 dispatch role pattern repeats across distinct copied-profile artifacts with distinct process IDs, CDB logs, and runtime pointer/controller tuples. It compares player roles and input-device routing rather than requiring equal process-local pointers across runs, and does not prove visible movement causality, improved control feel, online networking, deterministic sync, or rebuild parity.",
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
        first = census.make_artifact(first_root, config2_forward_qe_isolation=True)
        second = census.make_artifact(second_root, config2_forward_qe_isolation=True)
        replace_fixture_pointers(
            second,
            {
                "04646090": "04aa0090",
                "0465d890": "04bb8890",
                "11110000": "33330000",
                "22220000": "44440000",
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
        first_root = root / "first"
        second_root = root / "second"
        first_root.mkdir()
        second_root.mkdir()
        first = census.make_artifact(first_root, config2_forward_qe_isolation=True)
        second = census.make_artifact(second_root, config2_forward_qe_isolation=True, wrong_isolation_player=True)
        try:
            validate_artifact_pair([first, second], min_capture_count=1)
        except (ReplayabilityError, census.ArtifactError):
            pass
        else:
            raise ReplayabilityError("wrong Q/E route should fail replayability")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / "single"
        root.mkdir()
        path = census.make_artifact(root, config2_forward_qe_isolation=True)
        try:
            validate_artifact_pair([path, path], min_capture_count=1)
        except ReplayabilityError:
            pass
        else:
            raise ReplayabilityError("duplicate artifact paths should fail replayability")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        first_root = root / "same-runtime-first"
        second_root = root / "same-runtime-second"
        first_root.mkdir()
        second_root.mkdir()
        first = census.make_artifact(first_root, config2_forward_qe_isolation=True)
        second = census.make_artifact(second_root, config2_forward_qe_isolation=True)
        try:
            validate_artifact_pair([first, second], min_capture_count=1)
        except ReplayabilityError:
            pass
        else:
            raise ReplayabilityError("same runtime identity under distinct paths should fail replayability")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifacts", nargs="*", type=Path)
    parser.add_argument("--min-capture-count", type=int, default=1)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("WinUI safe-copy local multiplayer input-dispatch replayability checker self-test: PASS")
        return 0
    summary = validate_artifact_pair(args.artifacts, min_capture_count=args.min_capture_count)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ReplayabilityError, census.ArtifactError) as exc:
        print(f"WinUI safe-copy local multiplayer input-dispatch replayability check: FAIL: {exc}")
        raise SystemExit(2)
