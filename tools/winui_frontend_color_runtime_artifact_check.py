#!/usr/bin/env python3
"""Validate copied-game frontend clear-screen color runtime artifacts."""

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


EXPECTED_SCHEMA = "winui-safe-copy-live-runtime-smoke.v1"
BASE_PATCH_KEYS = {"resolution_gate", "force_windowed"}
COLOR_PATCHES: dict[str, tuple[str, tuple[int, int, int]]] = {
    "frontend_clear_screen_dark_red": ("red", (191, 31, 31)),
    "frontend_clear_screen_dark_green": ("green", (31, 191, 31)),
    "frontend_clear_screen_black": ("black", (0, 0, 0)),
}


class ArtifactError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ArtifactError(message)


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), "Artifact root must be a JSON object.")
    return value


def object_at(value: Any, key: str) -> dict[str, Any]:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, dict), f"Missing object: {key}")
    return child


def list_at(value: Any, key: str) -> list[Any]:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, list), f"Missing list: {key}")
    return child


def bool_at(value: Any, key: str) -> bool:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, bool), f"Missing boolean: {key}")
    return child


def int_at(value: Any, key: str) -> int:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, int), f"Missing integer: {key}")
    return int(child)


def string_at(value: Any, key: str) -> str:
    child = value.get(key) if isinstance(value, dict) else None
    require(isinstance(child, str), f"Missing string: {key}")
    return child


def string_list_at(value: Any, key: str) -> list[str]:
    values = list_at(value, key)
    require(all(isinstance(item, str) for item in values), f"{key} must contain only strings.")
    return [str(item) for item in values]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_png_rgb(path: Path) -> tuple[int, int, list[bytes], int]:
    data = path.read_bytes()
    require(data.startswith(b"\x89PNG\r\n\x1a\n"), f"Not a PNG file: {path}")
    position = 8
    width = height = bit_depth = color_type = None
    compressed = bytearray()

    while position < len(data):
        require(position + 12 <= len(data), "PNG chunk header is truncated.")
        chunk_size = struct.unpack(">I", data[position : position + 4])[0]
        chunk_type = data[position + 4 : position + 8]
        chunk_data = data[position + 8 : position + 8 + chunk_size]
        position += 12 + chunk_size
        if chunk_type == b"IHDR":
            width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack(
                ">IIBBBBB",
                chunk_data,
            )
            require(bit_depth == 8, "Only 8-bit PNG captures are supported by this checker.")
            require(color_type in (2, 6), "Only RGB/RGBA PNG captures are supported by this checker.")
            require(compression == 0 and filter_method == 0 and interlace == 0, "Unsupported PNG encoding.")
        elif chunk_type == b"IDAT":
            compressed.extend(chunk_data)
        elif chunk_type == b"IEND":
            break

    require(width is not None and height is not None and color_type is not None, "PNG is missing IHDR.")
    channels = 4 if color_type == 6 else 3
    stride = width * channels
    raw = zlib.decompress(bytes(compressed))
    rows: list[bytes] = []
    previous = bytearray(stride)
    cursor = 0

    for _ in range(height):
        require(cursor < len(raw), "PNG scanline is truncated.")
        filter_type = raw[cursor]
        cursor += 1
        current = bytearray(raw[cursor : cursor + stride])
        require(len(current) == stride, "PNG scanline has an unexpected length.")
        cursor += stride
        for index in range(stride):
            left = current[index - channels] if index >= channels else 0
            up = previous[index]
            up_left = previous[index - channels] if index >= channels else 0
            if filter_type == 1:
                current[index] = (current[index] + left) & 0xFF
            elif filter_type == 2:
                current[index] = (current[index] + up) & 0xFF
            elif filter_type == 3:
                current[index] = (current[index] + ((left + up) // 2)) & 0xFF
            elif filter_type == 4:
                predictor = left + up - up_left
                distance_left = abs(predictor - left)
                distance_up = abs(predictor - up)
                distance_up_left = abs(predictor - up_left)
                current[index] = (
                    current[index]
                    + (
                        left
                        if distance_left <= distance_up and distance_left <= distance_up_left
                        else up
                        if distance_up <= distance_up_left
                        else up_left
                    )
                ) & 0xFF
            elif filter_type != 0:
                raise ArtifactError(f"Unsupported PNG filter type: {filter_type}")
        rows.append(bytes(current))
        previous = current

    return width, height, rows, channels


def write_fixture_png(path: Path, color: tuple[int, int, int], *, wrong_color: bool = False) -> None:
    width = 64
    height = 32
    margin = 12
    fill = (13, 17, 19) if wrong_color else color
    rows = []
    for y in range(height):
        row = bytearray()
        for x in range(width):
            rgb = fill if x < margin or x >= width - margin else (40 + (x % 20), 50 + (y % 20), 70)
            row.extend((*rgb, 255))
        rows.append(b"\x00" + bytes(row))
    raw = zlib.compress(b"".join(rows))

    def chunk(kind: bytes, payload: bytes) -> bytes:
        return (
            struct.pack(">I", len(payload))
            + kind
            + payload
            + struct.pack(">I", binascii.crc32(kind + payload) & 0xFFFFFFFF)
        )

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", raw)
        + chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def capture_has_visual_proof(capture: dict[str, Any]) -> bool:
    if capture.get("foregroundMatchesTarget") is True or capture.get("visualProof") is True:
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
    return Path(string_at(capture, "outputPath")).name.lower()


def verify_capture_file(capture: dict[str, Any], *, require_files: bool) -> Path | None:
    output_path = Path(string_at(capture, "outputPath"))
    if not output_path.exists():
        require(not require_files, f"Capture file is missing: {output_path}")
        return None
    require(output_path.stat().st_size == int_at(capture, "fileSize"), f"Capture file size mismatch: {output_path}")
    expected_hash = string_at(capture, "sha256").lower()
    require(sha256_file(output_path) == expected_hash, f"Capture file hash mismatch: {output_path}")
    return output_path


def is_color_family_match(rgb: tuple[int, int, int], expected_rgb: tuple[int, int, int]) -> bool:
    red, green, blue = (int(channel) for channel in rgb)
    if expected_rgb == COLOR_PATCHES["frontend_clear_screen_dark_red"][1]:
        return red >= 100 and red >= green * 3 and red >= blue * 3
    if expected_rgb == COLOR_PATCHES["frontend_clear_screen_dark_green"][1]:
        return green >= 100 and green >= red * 3 and green >= blue * 3
    if expected_rgb == COLOR_PATCHES["frontend_clear_screen_black"][1]:
        return red <= 8 and green <= 8 and blue <= 8
    return False


def color_match_count(path: Path, expected_rgb: tuple[int, int, int]) -> dict[str, Any]:
    width, height, rows, channels = read_png_rgb(path)
    margin_width = max(4, min(80, width // 8))
    y_start = min(height, max(0, height // 8))
    y_end = max(y_start, height - max(1, height // 8))
    sample_count = 0
    match_count = 0
    exact_match_count = 0
    family_match_count = 0
    tolerance = 3

    for y in range(y_start, y_end):
        row = rows[y]
        for x in list(range(0, margin_width)) + list(range(width - margin_width, width)):
            index = x * channels
            rgb = tuple(row[index : index + 3])
            sample_count += 1
            exact_match = all(abs(int(rgb[i]) - expected_rgb[i]) <= tolerance for i in range(3))
            family_match = is_color_family_match(rgb, expected_rgb)
            if exact_match:
                exact_match_count += 1
            if family_match:
                family_match_count += 1
            if exact_match or family_match:
                match_count += 1

    ratio = match_count / sample_count if sample_count else 0.0
    return {
        "path": str(path),
        "width": width,
        "height": height,
        "marginWidth": margin_width,
        "sampleCount": sample_count,
        "matchCount": match_count,
        "exactMatchCount": exact_match_count,
        "familyMatchCount": family_match_count,
        "matchRatio": ratio,
    }


def validate_artifact(
    payload: dict[str, Any],
    *,
    expected_patch_key: str,
    min_capture_count: int,
    min_color_captures: int,
    min_visual_captures: int,
    min_margin_ratio: float,
    require_files: bool,
    require_input: bool,
    require_after_input_color: bool,
) -> dict[str, Any]:
    require(expected_patch_key in COLOR_PATCHES, "Unknown expected frontend color patch key.")
    color_name, expected_rgb = COLOR_PATCHES[expected_patch_key]
    require(payload.get("schemaVersion") == EXPECTED_SCHEMA, "Unexpected artifact schema.")

    source = object_at(payload, "source")
    require(bool_at(source, "installedHashUnchanged"), "Installed BEA.exe hash changed.")
    require(bool_at(source, "overrideHashUnchanged"), "Clean executable override hash changed.")
    source_save_options = object_at(source, "saveAndOptions")
    require(bool_at(source_save_options, "unchanged"), "Source defaultoptions/savegames hashes changed.")

    safe_copy = object_at(payload, "safeCopy")
    patch_keys = set(string_list_at(safe_copy, "patchKeys"))
    require(BASE_PATCH_KEYS.issubset(patch_keys), "Safe copy did not apply required windowed compatibility patch keys.")
    require(expected_patch_key in patch_keys, f"Missing expected patch key: {expected_patch_key}")
    conflicting_colors = sorted((set(COLOR_PATCHES) - {expected_patch_key}) & patch_keys)
    require(not conflicting_colors, f"Artifact includes conflicting frontend color patches: {', '.join(conflicting_colors)}")

    launch = object_at(payload, "launch")
    process_id = int_at(launch, "processId")
    hwnd = string_at(launch, "mainWindowHandle").lower()
    require(bool_at(launch, "observedAlive"), "Copied BEA process was not observed alive.")
    process_baseline = object_at(payload, "processBaseline")
    require(bool_at(process_baseline, "noPreexistingBea"), "A BEA process existed before launch.")
    require(bool_at(process_baseline, "noBeaAfterStop"), "A BEA process remained after stop.")
    stop = object_at(payload, "stop")
    require(bool_at(stop, "Success"), "Managed copied-game stop did not succeed.")

    if require_input:
        input_summary = object_at(payload, "inputSummary")
        require(int_at(input_summary, "inputSequencesSent") >= 1, "No scoped input sequence was reported sent.")
        require(int_at(input_summary, "inputActionCount") >= 1, "No scoped input actions were reported.")
        sent_inputs = 0
        for item in list_at(payload, "input"):
            require(isinstance(item, dict), "Each input result must be an object.")
            if item.get("status") == "sent":
                sent_inputs += 1
                require(item.get("processId") == process_id, "Input process id does not match launched process.")
                require(str(item.get("hwndHex", "")).lower() == hwnd, "Input hwnd does not match launched main window.")
        require(sent_inputs >= 1, "No sent input result matched the launched process/window.")
        capture_plan = object_at(payload, "capturePlan")
        require(
            bool_at(capture_plan, "captureAfterEachInputSequence"),
            "Navigated color proof must request capture-after-each-input-sequence.",
        )

    captures = list_at(payload, "captures")
    require(len(captures) >= min_capture_count, f"Expected at least {min_capture_count} capture(s).")
    visual_count = 0
    matching_color_captures = 0
    after_input_color_captures = 0
    sampled: list[dict[str, Any]] = []

    for capture in captures:
        require(isinstance(capture, dict), "Each capture must be an object.")
        require(capture.get("status") == "captured", "Each capture must have captured status.")
        require(capture.get("processId") == process_id, "Capture process id does not match launched process.")
        require(str(capture.get("hwndHex", "")).lower() == hwnd, "Capture hwnd does not match launched main window.")
        require(int_at(capture, "fileSize") > 0, "Capture file size must be positive.")
        if capture_has_visual_proof(capture):
            visual_count += 1
        capture_path = verify_capture_file(capture, require_files=require_files)
        if capture_path is None:
            continue
        stats = color_match_count(capture_path, expected_rgb)
        stats["captureName"] = capture_name(capture)
        sampled.append(stats)
        if stats["matchRatio"] >= min_margin_ratio:
            matching_color_captures += 1
            if stats["captureName"].startswith("safe-copy-after-input-"):
                after_input_color_captures += 1

    require(visual_count >= min_visual_captures, f"Expected at least {min_visual_captures} visual capture(s).")
    require(matching_color_captures >= min_color_captures, f"Expected at least {min_color_captures} capture(s) with {color_name} margin pixels.")
    if require_after_input_color:
        require(after_input_color_captures >= 1, "No after-input capture contained the expected frontend margin color.")

    boundary = string_at(payload, "claimBoundary")
    require("visual parity" in boundary, "Claim boundary must keep visual parity separate.")

    return {
        "schema": "winui-frontend-color-runtime-proof.v1",
        "expectedPatchKey": expected_patch_key,
        "colorName": color_name,
        "expectedRgb": expected_rgb,
        "captureCount": len(captures),
        "visualCaptureCount": visual_count,
        "matchingColorCaptureCount": matching_color_captures,
        "afterInputColorCaptureCount": after_input_color_captures,
        "sourceSaveOptionsUnchanged": True,
        "installedExeUnchanged": True,
        "overrideExeUnchanged": True,
        "noBeaAfterStop": True,
        "sampledCaptures": sampled,
        "claimBoundary": (
            "copied-game frontend clear-screen exact/title or color-family navigated margin proof only; not a full theme, "
            "texture replacement, gameplay rendering, visual parity, or rebuild proof"
        ),
    }


def capture_fixture(root: Path, *, color: tuple[int, int, int], wrong_color: bool = False, name: str = "safe-copy-after-input-01-frame.png") -> dict[str, Any]:
    output = root / name
    write_fixture_png(output, color, wrong_color=wrong_color)
    return {
        "status": "captured",
        "processId": 1234,
        "hwndHex": "0x123",
        "foregroundMatchesTarget": True,
        "visualProof": True,
        "outputPath": str(output),
        "fileSize": output.stat().st_size,
        "sha256": sha256_file(output),
    }


def fixture(root: Path, *, expected_patch_key: str = "frontend_clear_screen_dark_red", wrong_color: bool = False, with_input: bool = True) -> dict[str, Any]:
    _, color = COLOR_PATCHES[expected_patch_key]
    capture = capture_fixture(root, color=color, wrong_color=wrong_color)
    return {
        "schemaVersion": EXPECTED_SCHEMA,
        "source": {
            "installedHashUnchanged": True,
            "overrideHashUnchanged": True,
            "saveAndOptions": {
                "unchanged": True,
            },
        },
        "safeCopy": {
            "patchKeys": ["resolution_gate", "force_windowed", expected_patch_key],
        },
        "launch": {
            "processId": 1234,
            "observedAlive": True,
            "mainWindowHandle": "0x123",
        },
        "processBaseline": {
            "noPreexistingBea": True,
            "noBeaAfterStop": True,
        },
        "input": [
            {
                "status": "sent",
                "processId": 1234,
                "hwndHex": "0x123",
            }
        ]
        if with_input
        else [],
        "inputSummary": {
            "inputSequencesSent": 1 if with_input else 0,
            "inputActionCount": 2 if with_input else 0,
        },
        "capturePlan": {
            "captureAfterEachInputSequence": True,
        },
        "captures": [capture],
        "stop": {
            "Success": True,
        },
        "claimBoundary": "This does not prove rendering correctness, visual parity, unoccluded pixels, or rebuild parity.",
    }


def run_self_test() -> None:
    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        for patch_key in COLOR_PATCHES:
            validate_artifact(
                fixture(root, expected_patch_key=patch_key),
                expected_patch_key=patch_key,
                min_capture_count=1,
                min_color_captures=1,
                min_visual_captures=1,
                min_margin_ratio=0.50,
                require_files=True,
                require_input=True,
                require_after_input_color=True,
            )

        wrong = fixture(root, wrong_color=True)
        try:
            validate_artifact(
                wrong,
                expected_patch_key="frontend_clear_screen_dark_red",
                min_capture_count=1,
                min_color_captures=1,
                min_visual_captures=1,
                min_margin_ratio=0.50,
                require_files=True,
                require_input=True,
                require_after_input_color=True,
            )
        except ArtifactError:
            pass
        else:
            raise ArtifactError("Self-test expected wrong margin color to fail.")

        no_input = fixture(root, with_input=False)
        try:
            validate_artifact(
                no_input,
                expected_patch_key="frontend_clear_screen_dark_red",
                min_capture_count=1,
                min_color_captures=1,
                min_visual_captures=1,
                min_margin_ratio=0.50,
                require_files=True,
                require_input=True,
                require_after_input_color=True,
            )
        except ArtifactError:
            pass
        else:
            raise ArtifactError("Self-test expected missing input proof to fail.")

        conflict = fixture(root)
        conflict["safeCopy"]["patchKeys"].append("frontend_clear_screen_black")
        try:
            validate_artifact(
                conflict,
                expected_patch_key="frontend_clear_screen_dark_red",
                min_capture_count=1,
                min_color_captures=1,
                min_visual_captures=1,
                min_margin_ratio=0.50,
                require_files=True,
                require_input=True,
                require_after_input_color=True,
            )
        except ArtifactError:
            pass
        else:
            raise ArtifactError("Self-test expected conflicting color patch to fail.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifact", nargs="?", help="Path to a safe-copy runtime smoke JSON artifact")
    parser.add_argument("--expected-patch-key", choices=sorted(COLOR_PATCHES), default="frontend_clear_screen_dark_red")
    parser.add_argument("--min-capture-count", type=int, default=1)
    parser.add_argument("--min-color-captures", type=int, default=1)
    parser.add_argument("--min-visual-captures", type=int, default=1)
    parser.add_argument("--min-margin-ratio", type=float, default=0.50)
    parser.add_argument("--require-files", action="store_true")
    parser.add_argument("--require-input", action="store_true")
    parser.add_argument("--require-after-input-color", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        require(args.min_capture_count > 0, "--min-capture-count must be positive.")
        require(args.min_color_captures > 0, "--min-color-captures must be positive.")
        require(args.min_visual_captures >= 0, "--min-visual-captures must be non-negative.")
        require(0.0 < args.min_margin_ratio <= 1.0, "--min-margin-ratio must be > 0 and <= 1.")
        if args.self_test:
            run_self_test()
            print("WinUI frontend color runtime artifact checker self-test: PASS")
            return 0

        require(bool(args.artifact), "Provide an artifact path or --self-test.")
        summary = validate_artifact(
            read_json(Path(args.artifact)),
            expected_patch_key=args.expected_patch_key,
            min_capture_count=args.min_capture_count,
            min_color_captures=args.min_color_captures,
            min_visual_captures=args.min_visual_captures,
            min_margin_ratio=args.min_margin_ratio,
            require_files=args.require_files,
            require_input=args.require_input,
            require_after_input_color=args.require_after_input_color,
        )
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    except ArtifactError as exc:
        print(f"WinUI frontend color runtime artifact check: FAIL: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
