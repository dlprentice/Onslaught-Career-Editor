#!/usr/bin/env python3
"""Build timestamped CDB decode timeline sidecars for music audible proof."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from typing import Any

import winui_safe_copy_music_audible_output_materializer as materializer


SCHEMA = "winui-safe-copy-music-cdb-decode-timeline.v1"
TIMESTAMP_SOURCE = "timestamped-cdb-log"
LIVE_SCHEMA = "winui-safe-copy-live-runtime-smoke.v1"
LEVEL_ID = 100
SELECTION_ID = 2


class TimelineSidecarError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise TimelineSidecarError(message)


def utc_text(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"{path} must contain a JSON object.")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_sidecar(*, live_path: Path, timestamped_cdb_log: Path, output: Path, role: str) -> dict[str, Any]:
    live = read_json(live_path)
    require(live.get("schemaVersion") == LIVE_SCHEMA, "Live artifact schema changed.")
    require(role in {"cleanBaseline", "stagedPositive"}, "Timeline role must be cleanBaseline or stagedPositive.")
    raw_cdb_log = materializer.cdb_log_path_from_live(live)
    require(raw_cdb_log.is_file(), "Live artifact CDB log is missing.")
    require(timestamped_cdb_log.is_file(), "Timestamped CDB log is missing.")
    materializer.validate_no_symlink_or_reparse(raw_cdb_log)
    materializer.validate_no_symlink_or_reparse(timestamped_cdb_log)

    try:
        parsed = materializer.parse_cdb_log(timestamped_cdb_log)
    except materializer.MaterializerError as exc:
        raise TimelineSidecarError(str(exc)) from exc
    start_at = parsed["firstEvidenceAt"]
    end_at = parsed["lastEvidenceAt"]
    require(start_at <= end_at, "Timestamped CDB evidence window is inverted.")

    sidecar = {
        "schemaVersion": SCHEMA,
        "role": role,
        "timestampSource": TIMESTAMP_SOURCE,
        "cdbLogTimestamped": True,
        "liveArtifactSha256": materializer.sha256_file(live_path),
        "rawCdbLogSha256": materializer.sha256_file(raw_cdb_log),
        "timestampedCdbLogPath": str(timestamped_cdb_log.resolve()),
        "timestampedCdbLogSha256": materializer.sha256_file(timestamped_cdb_log),
        "cdbLogSha256": materializer.sha256_file(timestamped_cdb_log),
        "exactPidCdbObserver": True,
        "levelId": LEVEL_ID,
        "selectionId": SELECTION_ID,
        "playMusicForCurrentLevelObserved": True,
        "playSelectionObserved": True,
        "asyncKickPathMatched": True,
        "oggOpenPathMatched": True,
        "decodedPcmPositiveRequestObserved": True,
        "decodeWindowStartUtc": utc_text(start_at),
        "decodeWindowEndUtc": utc_text(end_at),
        "cdbEvidenceRowCounts": {
            "gameMusicRows": parsed["gameMusicRows"],
            "playSelectionRows": parsed["playSelectionRows"],
            "asyncKickRows": parsed["asyncKickRows"],
            "oggOpenRows": parsed["oggOpenRows"],
            "oggReadRows": parsed["oggReadRows"],
        },
        "claimBoundary": "Timestamped CDB timeline sidecar only; not audible-output proof by itself.",
    }
    write_json(output, sidecar)
    materializer.validate_timeline(output, live_path, live, role)
    return sidecar


def self_test() -> None:
    import tempfile

    from winui_safe_copy_music_audible_output_materializer_test import live_payload, log_text, untimestamped_log_text, write_json

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        raw_log = root / "clean" / "windbg.log"
        timestamped_log = root / "clean" / "windbg.timestamped.log"
        raw_log.parent.mkdir(parents=True, exist_ok=True)
        raw_log.write_text(untimestamped_log_text(), encoding="utf-8")
        timestamped_log.write_text(log_text(), encoding="utf-8")
        live_path = write_json(root / "clean" / "live.json", live_payload(raw_log, role="cleanBaseline", staged=False))
        build_sidecar(
            live_path=live_path,
            timestamped_cdb_log=timestamped_log,
            output=root / "clean" / "timeline.json",
            role="cleanBaseline",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", type=Path)
    parser.add_argument("--timestamped-cdb-log", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--role", default="")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            self_test()
            print("WinUI safe-copy music CDB timeline sidecar self-test: PASS")
            return 0
        require(args.live is not None, "Provide --live or --self-test.")
        require(args.timestamped_cdb_log is not None, "Provide --timestamped-cdb-log.")
        require(args.output is not None, "Provide --output.")
        require(bool(args.role), "Provide --role.")
        print(
            json.dumps(
                build_sidecar(
                    live_path=args.live,
                    timestamped_cdb_log=args.timestamped_cdb_log,
                    output=args.output,
                    role=args.role,
                ),
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    except (TimelineSidecarError, materializer.MaterializerError) as exc:
        print(f"WinUI safe-copy music CDB timeline sidecar: FAIL: {materializer.sanitize_error_message(str(exc))}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
