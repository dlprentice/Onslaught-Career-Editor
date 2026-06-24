#!/usr/bin/env python3
"""Validate a CDB-backed safe-copy level-850 local multiplayer artifact."""

from __future__ import annotations

import argparse
import json
import re
import tempfile
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def nonzero_hex(value: str) -> bool:
    try:
        return int(value, 16) != 0
    except ValueError:
        return False


def validate_artifact(path: Path, min_capture_count: int) -> dict:
    failures: list[str] = []
    artifact = read_json(path)

    require(artifact.get("schemaVersion") == "winui-safe-copy-live-runtime-smoke.v1", "unexpected schema", failures)
    launch = artifact.get("launch") or {}
    require(launch.get("arguments") == ["-skipfmv", "-level", "850"], "launch args are not -skipfmv -level 850", failures)

    source = artifact.get("source") or {}
    require(source.get("installedHashUnchanged") is True, "installed BEA.exe changed", failures)
    require(source.get("overrideHashUnchanged") is True, "clean override BEA.exe changed", failures)
    require((source.get("saveAndOptions") or {}).get("unchanged") is True, "source save/options changed", failures)

    process_baseline = artifact.get("processBaseline") or {}
    require(process_baseline.get("noPreexistingBea") is True, "preexisting BEA process was present", failures)
    require(process_baseline.get("noBeaAfterStop") is True, "BEA process remained after stop", failures)
    require((artifact.get("stop") or {}).get("Success") is True, "managed stop did not succeed", failures)

    captures = artifact.get("captures") or []
    visual_captures = [capture for capture in captures if capture.get("visualProof") is True]
    require(len(captures) >= min_capture_count, f"capture count below {min_capture_count}", failures)
    require(bool(visual_captures), "no visual-proof captures", failures)

    observer = artifact.get("cdbObserver") or {}
    result = observer.get("result") or {}
    cleanup = observer.get("cleanup") or {}
    require(observer.get("enabled") is True, "CDB observer not enabled", failures)
    require(result.get("status") == "attached", "CDB observer did not attach", failures)
    require(result.get("logExists") is True, "CDB log was not created", failures)
    require(cleanup.get("status") in {"stopped", "already-exited"}, "CDB cleanup did not finish", failures)

    log_path = Path(result.get("logPath") or observer.get("logPath") or "")
    require(log_path.is_file(), f"CDB log path is missing: {log_path}", failures)
    log_text = log_path.read_text(encoding="utf-8", errors="replace") if log_path.is_file() else ""

    is_multiplayer = re.search(r"CGame__IsMultiplayer this=([0-9a-fA-F]+) level=(\d+) raw=([0-9a-fA-F]+)", log_text)
    world_mode = re.search(r"CWorld__IsMultiplayerMode world=([0-9a-fA-F]+) mode=(\d+) raw=([0-9a-fA-F]+)", log_text)
    render = re.search(
        r"CGame__Render this=([0-9a-fA-F]+) numRenders=(\d+) players=(\d+) level=(\d+) "
        r"fullscreenMP=(\d+) horizSplit=(\d+) p0=([0-9a-fA-F]+) p1=([0-9a-fA-F]+) "
        r"cam0=([0-9a-fA-F]+) cam1=([0-9a-fA-F]+) world=([0-9a-fA-F]+)",
        log_text,
    )
    set_num_viewpoints = re.search(r"CEngine__SetNumViewpoints engine=([0-9a-fA-F]+) requested=(\d+)", log_text)
    set_viewpoints = re.findall(
        r"CEngine__SetViewpoint engine=([0-9a-fA-F]+) vp=(\d+) camera=([0-9a-fA-F]+) "
        r"viewport=([0-9a-fA-F]+) player=([0-9a-fA-F]+) rect0=([0-9a-fA-F]+) "
        r"rect1=([0-9a-fA-F]+) rect2=([0-9a-fA-F]+) rect3=([0-9a-fA-F]+)",
        log_text,
    )

    require(is_multiplayer is not None, "missing CGame__IsMultiplayer observation", failures)
    require(world_mode is not None, "missing CWorld__IsMultiplayerMode observation", failures)
    require(render is not None, "missing CGame__Render observation", failures)
    require(set_num_viewpoints is not None, "missing CEngine__SetNumViewpoints observation", failures)
    require(bool(set_viewpoints), "missing CEngine__SetViewpoint observation", failures)

    summary: dict[str, object] = {
        "artifact": str(path),
        "captureCount": len(captures),
        "visualCaptureCount": len(visual_captures),
        "cdbStatus": result.get("status"),
        "cdbCleanup": cleanup.get("status"),
        "launchArguments": launch.get("arguments"),
    }

    if is_multiplayer:
        summary["levelFromIsMultiplayer"] = int(is_multiplayer.group(2))
        summary["gameThis"] = is_multiplayer.group(1)
        require(int(is_multiplayer.group(2)) == 850, "CGame__IsMultiplayer level was not 850", failures)
        require(is_multiplayer.group(3).lower() == "00000352", "CGame__IsMultiplayer raw level was not 0x352", failures)

    if world_mode:
        summary["worldMode"] = int(world_mode.group(2))
        summary["worldPointer"] = world_mode.group(1)
        require(int(world_mode.group(2)) in {1, 2}, "world multiplayer mode was not 1 or 2", failures)

    p0 = p1 = None
    if render:
        p0 = render.group(7)
        p1 = render.group(8)
        summary["players"] = int(render.group(3))
        summary["levelFromRender"] = int(render.group(4))
        summary["horizSplit"] = int(render.group(6))
        summary["p0"] = p0
        summary["p1"] = p1
        summary["cam0"] = render.group(9)
        summary["cam1"] = render.group(10)
        require(int(render.group(3)) == 2, "CGame__Render players was not 2", failures)
        require(int(render.group(4)) == 850, "CGame__Render level was not 850", failures)
        require(int(render.group(6)) == 1, "CGame__Render horizontal split flag was not 1", failures)
        require(nonzero_hex(p0) and nonzero_hex(p1) and p0.lower() != p1.lower(), "P0/P1 pointers were missing or not distinct", failures)

    if set_num_viewpoints:
        summary["requestedViewpoints"] = int(set_num_viewpoints.group(2))
        require(int(set_num_viewpoints.group(2)) == 2, "CEngine__SetNumViewpoints did not request 2", failures)

    if set_viewpoints:
        observed_viewpoints = sorted({int(row[1]) for row in set_viewpoints})
        summary["observedViewpoints"] = observed_viewpoints
        if p0 and p1:
            has_vp0_p0 = any(int(row[1]) == 0 and row[4].lower() == p0.lower() for row in set_viewpoints)
            has_vp1_p1 = any(int(row[1]) == 1 and row[4].lower() == p1.lower() for row in set_viewpoints)
            require(has_vp0_p0, "no CEngine__SetViewpoint vp=0 row matched P0", failures)
            require(has_vp1_p1, "no CEngine__SetViewpoint vp=1 row matched P1", failures)

    if failures:
        raise SystemExit("WinUI safe-copy local multiplayer CDB observer check: FAIL: " + "; ".join(failures))

    return summary


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        log_path = root / "windbg.log"
        log_path.write_text(
            "CGame__IsMultiplayer this=008a9a98 level=850 raw=00000352 "
            "CWorld__IsMultiplayerMode world=00855090 mode=1 raw=00000001 "
            "CGame__Render this=008a9a98 numRenders=0 players=2 level=850 fullscreenMP=0 horizSplit=1 "
            "p0=04646090 p1=0465d890 cam0=046d97f0 cam1=046d98a0 world=038c0840 "
            "CEngine__SetNumViewpoints engine=0089c9a0 requested=2 esp8=008a9a98 "
            "CEngine__SetViewpoint engine=0089c9a0 vp=0 camera=046d97f0 viewport=001af500 player=04646090 rect0=00000280 rect1=000000f0 rect2=00000000 rect3=00000000 "
            "CEngine__SetViewpoint engine=0089c9a0 vp=1 camera=046d98a0 viewport=001af500 player=0465d890 rect0=00000280 rect1=000000f0 rect2=00000000 rect3=000000f0",
            encoding="utf-8",
        )
        artifact_path = root / "artifact.json"
        artifact_path.write_text(
            json.dumps(
                {
                    "schemaVersion": "winui-safe-copy-live-runtime-smoke.v1",
                    "source": {
                        "installedHashUnchanged": True,
                        "overrideHashUnchanged": True,
                        "saveAndOptions": {"unchanged": True},
                    },
                    "launch": {"arguments": ["-skipfmv", "-level", "850"]},
                    "processBaseline": {"noPreexistingBea": True, "noBeaAfterStop": True},
                    "stop": {"Success": True},
                    "captures": [{"visualProof": True}],
                    "cdbObserver": {
                        "enabled": True,
                        "result": {"status": "attached", "logExists": True, "logPath": str(log_path)},
                        "cleanup": {"status": "stopped"},
                    },
                }
            ),
            encoding="utf-8",
        )
        validate_artifact(artifact_path, min_capture_count=1)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", nargs="?", type=Path)
    parser.add_argument("--min-capture-count", type=int, default=6)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("WinUI safe-copy local multiplayer CDB observer checker self-test: PASS")
        return 0

    if args.artifact is None:
        raise SystemExit("artifact is required unless --self-test is used")

    summary = validate_artifact(args.artifact, args.min_capture_count)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
