#!/usr/bin/env python3
"""Validate interleaved local-multiplayer visible movement-delta artifacts."""

from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import struct
import tempfile
import zlib
from pathlib import Path
from typing import Any

import winui_safe_copy_local_multiplayer_movement_state_delta_check as movement_state
import winui_safe_copy_local_multiplayer_input_state_delta_check as state_delta


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class VisibleMovementDeltaError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VisibleMovementDeltaError(message)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), "artifact root must be a JSON object")
    return value


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def chunk(kind: bytes, payload: bytes) -> bytes:
    crc = binascii.crc32(kind)
    crc = binascii.crc32(payload, crc) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", crc)


def write_png_rgb(path: Path, width: int, height: int, pixels: list[tuple[int, int, int]]) -> None:
    require(len(pixels) == width * height, "pixel buffer length mismatch")
    rows = []
    for y in range(height):
        row = bytearray([0])
        for r, g, b in pixels[y * width:(y + 1) * width]:
            row.extend((r, g, b))
        rows.append(bytes(row))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    data = PNG_SIGNATURE + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(b"".join(rows))) + chunk(b"IEND", b"")
    path.write_bytes(data)


def paeth(left: int, up: int, upper_left: int) -> int:
    p = left + up - upper_left
    pa = abs(p - left)
    pb = abs(p - up)
    pc = abs(p - upper_left)
    if pa <= pb and pa <= pc:
        return left
    if pb <= pc:
        return up
    return upper_left


def read_png_rgb(path: Path) -> tuple[int, int, bytes]:
    data = path.read_bytes()
    require(data.startswith(PNG_SIGNATURE), f"not a PNG file: {path}")
    offset = len(PNG_SIGNATURE)
    width = height = bit_depth = color_type = None
    idat_parts: list[bytes] = []
    while offset < len(data):
        require(offset + 8 <= len(data), f"truncated PNG chunk header: {path}")
        size = struct.unpack(">I", data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        payload_start = offset + 8
        payload_end = payload_start + size
        require(payload_end + 4 <= len(data), f"truncated PNG chunk payload: {path}")
        payload = data[payload_start:payload_end]
        if kind == b"IHDR":
            width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(">IIBBBBB", payload)
            require(bit_depth == 8, f"unsupported PNG bit depth {bit_depth}: {path}")
            require(color_type in (0, 2, 6), f"unsupported PNG color type {color_type}: {path}")
            require(compression == 0 and filter_method == 0 and interlace == 0, f"unsupported PNG encoding flags: {path}")
        elif kind == b"IDAT":
            idat_parts.append(payload)
        elif kind == b"IEND":
            break
        offset = payload_end + 4

    require(width is not None and height is not None and color_type is not None, f"PNG missing IHDR: {path}")
    channels = {0: 1, 2: 3, 6: 4}[int(color_type)]
    stride = int(width) * channels
    raw = zlib.decompress(b"".join(idat_parts))
    require(len(raw) >= (stride + 1) * int(height), f"PNG IDAT shorter than expected: {path}")
    previous = bytearray(stride)
    rgb = bytearray(int(width) * int(height) * 3)
    source = 0
    dest = 0
    for _y in range(int(height)):
        filter_type = raw[source]
        source += 1
        row = bytearray(raw[source:source + stride])
        source += stride
        for i, value in enumerate(row):
            left = row[i - channels] if i >= channels else 0
            up = previous[i]
            upper_left = previous[i - channels] if i >= channels else 0
            if filter_type == 0:
                decoded = value
            elif filter_type == 1:
                decoded = (value + left) & 0xFF
            elif filter_type == 2:
                decoded = (value + up) & 0xFF
            elif filter_type == 3:
                decoded = (value + ((left + up) // 2)) & 0xFF
            elif filter_type == 4:
                decoded = (value + paeth(left, up, upper_left)) & 0xFF
            else:
                raise VisibleMovementDeltaError(f"unsupported PNG row filter {filter_type}: {path}")
            row[i] = decoded
        previous = row
        for x in range(int(width)):
            if color_type == 0:
                gray = row[x]
                rgb[dest:dest + 3] = bytes((gray, gray, gray))
            elif color_type == 2:
                start = x * 3
                rgb[dest:dest + 3] = row[start:start + 3]
            else:
                start = x * 4
                rgb[dest:dest + 3] = row[start:start + 3]
            dest += 3
    return int(width), int(height), bytes(rgb)


def capture_has_visual_proof(capture: dict[str, Any]) -> bool:
    if capture.get("visualProof") is True or capture.get("foregroundMatchesTarget") is True:
        return True
    occlusion = capture.get("occlusion")
    return (
        isinstance(occlusion, dict)
        and occlusion.get("checked") is True
        and occlusion.get("targetFound") is True
        and occlusion.get("occlusionFree") is True
        and occlusion.get("occludingWindowCount") == 0
    )


def capture_name(capture: dict[str, Any]) -> str:
    output = capture.get("outputPath")
    require(isinstance(output, str) and output, "capture missing outputPath")
    return Path(output).name.lower()


def capture_by_name(captures: list[Any], name: str) -> dict[str, Any]:
    matches = [capture for capture in captures if isinstance(capture, dict) and capture_name(capture) == name]
    require(len(matches) == 1, f"expected exactly one capture named {name}")
    return matches[0]


def capture_path(capture: dict[str, Any]) -> Path:
    output = Path(str(capture.get("outputPath", "")))
    require(output.is_file(), f"capture file is missing: {output}")
    expected_size = capture.get("fileSize")
    expected_hash = str(capture.get("sha256", "")).lower()
    require(isinstance(expected_size, int) and expected_size > 0, f"capture has invalid fileSize: {output}")
    require(output.stat().st_size == expected_size, f"capture file size mismatch: {output}")
    require(len(expected_hash) == 64 and sha256_file(output) == expected_hash, f"capture sha256 mismatch: {output}")
    require(capture_has_visual_proof(capture), f"capture lacks foreground/z-order visual proof: {output}")
    return output


def roi(role: str, width: int, height: int) -> tuple[int, int, int, int]:
    split = height // 2
    guard = max(4, height // 80)
    if role == "P0":
        return 0, 0, width, max(1, split - guard)
    if role == "P1":
        return 0, min(height - 1, split + guard), width, height
    raise VisibleMovementDeltaError(f"unknown role: {role}")


def frame_delta(before: Path, after: Path, *, role: str, pixel_threshold: int) -> dict[str, Any]:
    bw, bh, bdata = read_png_rgb(before)
    aw, ah, adata = read_png_rgb(after)
    require((bw, bh) == (aw, ah), "capture dimensions differ")
    x0, y0, x1, y1 = roi(role, bw, bh)
    changed = 0
    total = 0
    abs_sum = 0
    for y in range(y0, y1):
        for x in range(x0, x1):
            index = (y * bw + x) * 3
            diffs = [abs(bdata[index + channel] - adata[index + channel]) for channel in range(3)]
            if max(diffs) >= pixel_threshold:
                changed += 1
            abs_sum += sum(diffs)
            total += 1
    require(total > 0, "empty ROI")
    return {
        "role": role,
        "before": str(before),
        "after": str(after),
        "width": bw,
        "height": bh,
        "roi": {"x0": x0, "y0": y0, "x1": x1, "y1": y1},
        "changedPixels": changed,
        "totalPixels": total,
        "changedRatio": changed / total,
        "meanAbsChannelDelta": abs_sum / (total * 3),
        "pixelThreshold": pixel_threshold,
    }


def require_target_delta(
    *,
    label: str,
    baseline: dict[str, Any],
    target: dict[str, Any],
    non_target: dict[str, Any],
    min_target_changed_ratio: float,
    min_target_to_baseline_ratio: float,
    min_target_to_nontarget_ratio: float,
) -> None:
    baseline_ratio = float(baseline["changedRatio"])
    target_ratio = float(target["changedRatio"])
    non_target_ratio = float(non_target["changedRatio"])
    require(target_ratio >= min_target_changed_ratio, f"{label} target visual delta below threshold")
    required_ratio = baseline_ratio * min_target_to_baseline_ratio
    require(target_ratio >= required_ratio, f"{label} target visual delta did not exceed adjacent no-input baseline")
    required_nontarget_ratio = non_target_ratio * min_target_to_nontarget_ratio
    require(target_ratio >= required_nontarget_ratio, f"{label} target visual delta did not exceed non-target split-screen half")


def validate_artifact(
    path: Path,
    *,
    min_capture_count: int,
    min_render_samples: int,
    pixel_threshold: int,
    min_target_changed_ratio: float,
    min_target_to_baseline_ratio: float,
    min_target_to_nontarget_ratio: float,
    expected_controller_configuration: int = 2,
    expected_qe_proof_lever: str = state_delta.DEFAULT_QE_PROOF_LEVER,
) -> dict[str, Any]:
    movement_summary = movement_state.validate_artifact(
        path,
        min_capture_count=min_capture_count,
        min_render_samples=min_render_samples,
        expected_controller_configuration=expected_controller_configuration,
        expected_qe_proof_lever=expected_qe_proof_lever,
    )
    artifact = read_json(path)
    capture_plan = artifact.get("capturePlan")
    require(isinstance(capture_plan, dict), "artifact missing capturePlan")
    require(capture_plan.get("captureAfterEachInputSequence") is True, "artifact did not request capture-after-each-input sequencing")

    captures = artifact.get("captures")
    require(isinstance(captures, list), "artifact missing captures")
    pre = capture_path(capture_by_name(captures, "safe-copy-pre-input-frame.png"))
    after_01 = capture_path(capture_by_name(captures, "safe-copy-after-input-01-frame.png"))
    after_02 = capture_path(capture_by_name(captures, "safe-copy-after-input-02-frame.png"))
    after_03 = capture_path(capture_by_name(captures, "safe-copy-after-input-03-frame.png"))
    after_04 = capture_path(capture_by_name(captures, "safe-copy-after-input-04-frame.png"))

    q_baseline = frame_delta(pre, after_01, role="P0", pixel_threshold=pixel_threshold)
    q_target = frame_delta(after_01, after_02, role="P0", pixel_threshold=pixel_threshold)
    q_non_target = frame_delta(after_01, after_02, role="P1", pixel_threshold=pixel_threshold)
    e_baseline = frame_delta(after_02, after_03, role="P1", pixel_threshold=pixel_threshold)
    e_target = frame_delta(after_03, after_04, role="P1", pixel_threshold=pixel_threshold)
    e_non_target = frame_delta(after_03, after_04, role="P0", pixel_threshold=pixel_threshold)
    require_target_delta(
        label="Q/P0",
        baseline=q_baseline,
        target=q_target,
        non_target=q_non_target,
        min_target_changed_ratio=min_target_changed_ratio,
        min_target_to_baseline_ratio=min_target_to_baseline_ratio,
        min_target_to_nontarget_ratio=min_target_to_nontarget_ratio,
    )
    require_target_delta(
        label="E/P1",
        baseline=e_baseline,
        target=e_target,
        non_target=e_non_target,
        min_target_changed_ratio=min_target_changed_ratio,
        min_target_to_baseline_ratio=min_target_to_baseline_ratio,
        min_target_to_nontarget_ratio=min_target_to_nontarget_ratio,
    )

    return {
        "artifact": str(path),
        "claim": f"config-{expected_controller_configuration} Movement/Forward visible movement-delta proof",
        "controllerConfiguration": expected_controller_configuration,
        "proofLever": expected_qe_proof_lever,
        "p0": movement_summary["p0"],
        "p1": movement_summary["p1"],
        "q": {
            "role": "P0",
            "state": movement_summary["q"],
            "baselineVisualDelta": q_baseline,
            "targetVisualDelta": q_target,
            "nonTargetVisualDelta": q_non_target,
        },
        "e": {
            "role": "P1",
            "state": movement_summary["e"],
            "baselineVisualDelta": e_baseline,
            "targetVisualDelta": e_target,
            "nonTargetVisualDelta": e_non_target,
        },
        "claimBoundary": (
            f"This proves copied-profile level 850 config-{expected_controller_configuration} keyboard Q/E Movement/Forward input has exact-PID CDB movement-state "
            "evidence plus target split-screen-half frame deltas that exceed adjacent no-input baselines and the "
            "opposite split-screen half in the same target window. It does "
            "not prove player feel, all controller configurations, gamepad behavior, online networking, deterministic "
            "sync, exact full layout, rebuild parity, or no-noticeable-difference parity."
        ),
    }


def solid_pixels(width: int, height: int, rgb: tuple[int, int, int]) -> list[tuple[int, int, int]]:
    return [rgb for _ in range(width * height)]


def draw_rect(
    pixels: list[tuple[int, int, int]],
    *,
    width: int,
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    rgb: tuple[int, int, int],
) -> None:
    for y in range(y0, y1):
        for x in range(x0, x1):
            pixels[y * width + x] = rgb


def add_capture(artifact: dict[str, Any], root: Path, name: str, pixels: list[tuple[int, int, int]], *, width: int, height: int) -> None:
    capture_path_value = root / name
    write_png_rgb(capture_path_value, width, height, pixels)
    artifact["captures"].append(
        {
            "status": "captured",
            "processId": 42464,
            "hwndHex": "0x1600d2a",
            "foregroundMatchesTarget": True,
            "visualProof": True,
            "outputPath": str(capture_path_value),
            "fileSize": capture_path_value.stat().st_size,
            "sha256": sha256_file(capture_path_value),
        }
    )


def make_visible_fixture(
    root: Path,
    *,
    controller_configuration: int = 2,
    qe_proof_lever: str = state_delta.DEFAULT_QE_PROOF_LEVER,
    collapse_q: bool = False,
    collapse_e: bool = False,
    wrong_half_q: bool = False,
    wrong_half_e: bool = False,
    omit_capture: bool = False,
) -> Path:
    artifact_path = state_delta.make_artifact(
        root,
        controller_configuration=controller_configuration,
        qe_proof_lever=qe_proof_lever,
    )
    movement_state.inject_render_rows(artifact_path)
    artifact = read_json(artifact_path)
    artifact["captures"] = []
    artifact["capturePlan"] = {
        "captureCount": 1,
        "preInputCaptureCount": 1,
        "captureAfterEachInputSequence": True,
        "afterInputCaptureDelayMs": 250,
    }
    width = 64
    height = 64
    pre = solid_pixels(width, height, (0, 0, 0))
    wait1 = solid_pixels(width, height, (0, 0, 0))
    q = solid_pixels(width, height, (0, 0, 0))
    if not collapse_q:
        if wrong_half_q:
            draw_rect(q, width=width, x0=4, y0=4, x1=12, y1=12, rgb=(220, 40, 40))
            draw_rect(q, width=width, x0=8, y0=40, x1=56, y1=60, rgb=(220, 40, 40))
        else:
            draw_rect(q, width=width, x0=4, y0=4, x1=28, y1=24, rgb=(220, 40, 40))
    wait3 = list(q)
    e = list(wait3)
    if not collapse_e:
        if wrong_half_e:
            draw_rect(e, width=width, x0=8, y0=42, x1=18, y1=50, rgb=(40, 120, 240))
            draw_rect(e, width=width, x0=8, y0=6, x1=56, y1=26, rgb=(40, 120, 240))
        else:
            draw_rect(e, width=width, x0=8, y0=42, x1=48, y1=60, rgb=(40, 120, 240))

    add_capture(artifact, root, "safe-copy-pre-input-frame.png", pre, width=width, height=height)
    add_capture(artifact, root, "safe-copy-after-input-01-frame.png", wait1, width=width, height=height)
    add_capture(artifact, root, "safe-copy-after-input-02-frame.png", q, width=width, height=height)
    add_capture(artifact, root, "safe-copy-after-input-03-frame.png", wait3, width=width, height=height)
    if not omit_capture:
        add_capture(artifact, root, "safe-copy-after-input-04-frame.png", e, width=width, height=height)
    artifact_path.write_text(json.dumps(artifact), encoding="utf-8")
    return artifact_path


def self_test() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        path = make_visible_fixture(Path(temp_dir))
        summary = validate_artifact(
            path,
            min_capture_count=5,
            min_render_samples=2,
            pixel_threshold=8,
            min_target_changed_ratio=0.01,
            min_target_to_baseline_ratio=1.25,
            min_target_to_nontarget_ratio=1.05,
        )
        require(summary["q"]["targetVisualDelta"]["changedRatio"] > 0, "Q target visual delta should be positive")
        require(summary["e"]["targetVisualDelta"]["changedRatio"] > 0, "E target visual delta should be positive")

    with tempfile.TemporaryDirectory() as temp_dir:
        path = make_visible_fixture(Path(temp_dir), controller_configuration=1, qe_proof_lever="input-isolation-forward-qe")
        summary = validate_artifact(
            path,
            min_capture_count=5,
            min_render_samples=2,
            pixel_threshold=8,
            min_target_changed_ratio=0.01,
            min_target_to_baseline_ratio=1.25,
            min_target_to_nontarget_ratio=1.05,
            expected_controller_configuration=1,
            expected_qe_proof_lever="input-isolation-forward-qe",
        )
        require(summary["controllerConfiguration"] == 1, "config-1 visible movement proof should be accepted")

    for kwargs, label in (
        ({"collapse_q": True}, "collapsed Q target should fail"),
        ({"collapse_e": True}, "collapsed E target should fail"),
        ({"wrong_half_q": True}, "wrong-half Q target should fail"),
        ({"wrong_half_e": True}, "wrong-half E target should fail"),
        ({"omit_capture": True}, "missing after-input capture should fail"),
    ):
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                validate_artifact(
                    make_visible_fixture(Path(temp_dir), **kwargs),
                    min_capture_count=5,
                    min_render_samples=2,
                    pixel_threshold=8,
                    min_target_changed_ratio=0.01,
                    min_target_to_baseline_ratio=1.25,
                    min_target_to_nontarget_ratio=1.05,
                )
            except (VisibleMovementDeltaError, movement_state.MovementStateDeltaError, state_delta.ArtifactError):
                pass
            else:
                raise VisibleMovementDeltaError(label)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("artifact", nargs="?", type=Path)
    parser.add_argument("--min-capture-count", type=int, default=5)
    parser.add_argument("--min-render-samples", type=int, default=2)
    parser.add_argument("--pixel-threshold", type=int, default=16)
    parser.add_argument("--min-target-changed-ratio", type=float, default=0.002)
    parser.add_argument("--min-target-to-baseline-ratio", type=float, default=1.25)
    parser.add_argument("--min-target-to-nontarget-ratio", type=float, default=1.05)
    parser.add_argument("--expected-controller-configuration", type=int, default=2, choices=(1, 2, 3, 4))
    parser.add_argument("--expected-qe-proof-lever", default=state_delta.DEFAULT_QE_PROOF_LEVER, choices=tuple(state_delta.QE_PROOF_LEVERS))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        self_test()
        print("WinUI safe-copy local multiplayer visible movement-delta checker self-test: PASS")
        return 0
    if args.artifact is None:
        raise SystemExit("artifact is required unless --self-test is used")
    summary = validate_artifact(
        args.artifact,
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
    except (VisibleMovementDeltaError, movement_state.MovementStateDeltaError, state_delta.ArtifactError) as exc:
        print(f"WinUI safe-copy local multiplayer visible movement-delta check: FAIL: {exc}")
        raise SystemExit(2)
