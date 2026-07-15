#!/usr/bin/env python3
"""Shared fail-closed lifecycle helpers for native WinUI acceptance gates."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import stat
import struct
import subprocess
import xml.etree.ElementTree as ET
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


RELEVANT_PROCESS_NAMES = {
    "onslaughtcareereditor.winui",
    "testhost",
    "vstest.console",
    "bea",
    "cdb",
    "windbg",
    "windbgx",
}
PNG_SIGNATURE = bytes((137, 80, 78, 71, 13, 10, 26, 10))
MAX_PNG_FILE_BYTES = 64 * 1024 * 1024
MAX_PNG_DIMENSION = 4096
MAX_PNG_PIXELS = 16_000_000
MAX_PNG_INFLATED_BYTES = 64 * 1024 * 1024


class NativeAcceptanceError(RuntimeError):
    pass


@dataclass(frozen=True)
class OwnedProcessIdentity:
    process_id: int
    start_time_utc_ticks: int
    executable_path: Path


@dataclass(frozen=True)
class PngRgba:
    width: int
    height: int
    pixels: bytes

    def pixel(self, x: int, y: int) -> tuple[int, int, int, int]:
        offset = (y * self.width + x) * 4
        return tuple(self.pixels[offset : offset + 4])  # type: ignore[return-value]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise NativeAcceptanceError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def normalized(path: str | Path) -> str:
    return os.path.normcase(str(Path(path).resolve()))


def png_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as stream:
        header = stream.read(24)
    require(header[:8] == PNG_SIGNATURE, f"capture is not PNG: {path.name}")
    require(header[12:16] == b"IHDR" and len(header) == 24, f"capture PNG lacks IHDR: {path.name}")
    return struct.unpack(">II", header[16:24])


def decode_png_rgba(path: Path) -> PngRgba:
    """Decode a non-interlaced 8-bit RGB/RGBA PNG using only the stdlib."""
    file_size = path.stat().st_size
    require(
        0 < file_size <= MAX_PNG_FILE_BYTES,
        f"capture PNG exceeds safety limits: {path.name}",
    )
    data = path.read_bytes()
    require(len(data) == file_size, f"capture PNG changed while reading: {path.name}")
    return decode_png_rgba_bytes(data, name=path.name)


def decode_png_rgba_bytes(data: bytes, *, name: str = "capture.png") -> PngRgba:
    """Decode one bounded PNG byte snapshot without reopening its source path."""
    require(0 < len(data) <= MAX_PNG_FILE_BYTES, f"capture PNG exceeds safety limits: {name}")
    require(data[:8] == PNG_SIGNATURE, f"capture is not PNG: {name}")
    position = 8
    ihdr: bytes | None = None
    compressed = bytearray()
    saw_iend = False
    while position < len(data):
        require(position + 12 <= len(data), f"capture PNG chunk is truncated: {name}")
        length = struct.unpack_from(">I", data, position)[0]
        chunk_type = data[position + 4 : position + 8]
        payload_start = position + 8
        payload_end = payload_start + length
        crc_end = payload_end + 4
        require(crc_end <= len(data), f"capture PNG chunk is truncated: {name}")
        payload = data[payload_start:payload_end]
        expected_crc = struct.unpack_from(">I", data, payload_end)[0]
        require(
            zlib.crc32(chunk_type + payload) & 0xFFFFFFFF == expected_crc,
            f"capture PNG chunk CRC changed: {name}",
        )
        if chunk_type == b"IHDR":
            require(ihdr is None and position == 8, f"capture PNG IHDR is not canonical: {name}")
            ihdr = payload
        elif chunk_type == b"IDAT":
            compressed.extend(payload)
        elif chunk_type == b"IEND":
            require(length == 0, f"capture PNG IEND is malformed: {name}")
            saw_iend = True
            position = crc_end
            break
        position = crc_end

    require(ihdr is not None and len(ihdr) == 13, f"capture PNG lacks IHDR: {name}")
    require(saw_iend and position == len(data), f"capture PNG lacks canonical IEND: {name}")
    width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(">IIBBBBB", ihdr)
    require(width > 0 and height > 0, f"capture PNG dimensions are invalid: {name}")
    require(
        bit_depth == 8 and color_type in {2, 6} and compression == 0 and filtering == 0 and interlace == 0,
        f"capture PNG format is unsupported: {name}",
    )
    require(
        width <= MAX_PNG_DIMENSION
        and height <= MAX_PNG_DIMENSION
        and width * height <= MAX_PNG_PIXELS,
        f"capture PNG exceeds safety limits: {name}",
    )
    bytes_per_pixel = 4 if color_type == 6 else 3
    stride = width * bytes_per_pixel
    expected_inflated_length = (stride + 1) * height
    require(
        len(compressed) <= MAX_PNG_FILE_BYTES
        and expected_inflated_length <= MAX_PNG_INFLATED_BYTES,
        f"capture PNG exceeds safety limits: {name}",
    )
    try:
        decoder = zlib.decompressobj()
        filtered = decoder.decompress(bytes(compressed), expected_inflated_length + 1)
    except zlib.error as exc:
        raise NativeAcceptanceError(f"capture PNG IDAT is invalid: {name}") from exc
    require(
        decoder.eof
        and not decoder.unconsumed_tail
        and not decoder.unused_data
        and len(filtered) == expected_inflated_length,
        f"capture PNG scanline length changed: {name}",
    )

    reconstructed = bytearray()
    prior = bytearray(stride)
    offset = 0
    for _ in range(height):
        filter_type = filtered[offset]
        scanline = filtered[offset + 1 : offset + 1 + stride]
        offset += stride + 1
        row = bytearray(stride)
        for index, value in enumerate(scanline):
            left = row[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            above = prior[index]
            upper_left = prior[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            if filter_type == 0:
                predictor = 0
            elif filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = above
            elif filter_type == 3:
                predictor = (left + above) // 2
            elif filter_type == 4:
                predictor = _paeth(left, above, upper_left)
            else:
                raise NativeAcceptanceError(f"capture PNG filter is unsupported: {name}")
            row[index] = (value + predictor) & 0xFF
        if color_type == 6:
            reconstructed.extend(row)
        else:
            for index in range(0, len(row), 3):
                reconstructed.extend(row[index : index + 3])
                reconstructed.append(255)
        prior = row
    return PngRgba(width, height, bytes(reconstructed))


def require_toolkit_visual_evidence(
    path: Path,
    marker_bounds: list[tuple[int, int, int, int]],
    *,
    label: str,
) -> None:
    image = decode_png_rgba(path)
    require_toolkit_visual_evidence_image(image, marker_bounds, label=label, name=path.name)


def require_toolkit_visual_evidence_image(
    image: PngRgba,
    marker_bounds: list[tuple[int, int, int, int]],
    *,
    label: str,
    name: str = "capture.png",
) -> None:
    """Validate visual semantics for a previously decoded immutable PNG snapshot."""
    require(_has_meaningful_frame_coverage(image), f"{label} lacks meaningful visual coverage: {name}")
    require(_has_rendered_toolkit_header(image), f"{label} lacks the rendered Toolkit header: {name}")
    for bounds in marker_bounds:
        x, y, width, height = bounds
        require(
            width > 0
            and height > 0
            and x >= 0
            and y >= 0
            and x + width <= image.width
            and y + height <= image.height,
            f"{label} marker bounds escape the PNG: {name}",
        )
        require(
            _has_rendered_activity(image, bounds),
            f"{label} marker lacks rendered activity at {bounds}: {name}",
        )


def _paeth(left: int, above: int, upper_left: int) -> int:
    estimate = left + above - upper_left
    left_distance = abs(estimate - left)
    above_distance = abs(estimate - above)
    upper_left_distance = abs(estimate - upper_left)
    if left_distance <= above_distance and left_distance <= upper_left_distance:
        return left
    if above_distance <= upper_left_distance:
        return above
    return upper_left


def _luminance(pixel: tuple[int, int, int, int]) -> int:
    red, green, blue, _ = pixel
    return (red * 299 + green * 587 + blue * 114) // 1000


def _quantize(pixel: tuple[int, int, int, int]) -> int:
    red, green, blue, _ = pixel
    return ((red >> 4) << 8) | ((green >> 4) << 4) | (blue >> 4)


def _color_distance(
    left: tuple[int, int, int, int],
    right: tuple[int, int, int, int],
) -> int:
    return sum(abs(left[index] - right[index]) for index in range(3))


def _has_meaningful_frame_coverage(image: PngRgba) -> bool:
    if image.width < 320 or image.height < 320:
        return False
    samples = opaque = non_dark = 0
    minimum_luminance = 255
    maximum_luminance = 0
    colors: set[int] = set()
    for y in range(0, image.height, 4):
        for x in range(0, image.width, 4):
            pixel = image.pixel(x, y)
            samples += 1
            opaque += int(pixel[3] >= 250)
            luminance = _luminance(pixel)
            non_dark += int(luminance >= 32)
            minimum_luminance = min(minimum_luminance, luminance)
            maximum_luminance = max(maximum_luminance, luminance)
            colors.add(_quantize(pixel))
    return (
        samples > 0
        and opaque >= samples * 99 // 100
        and non_dark >= samples * 7 // 10
        and len(colors) >= 8
        and maximum_luminance - minimum_luminance >= 80
    )


def _has_rendered_toolkit_header(image: PngRgba) -> bool:
    if image.width < 320 or image.height < 117:
        return False
    samples = blue_opaque = 0
    for y in range(40, 116, 4):
        for x in range(0, image.width, 4):
            red, green, blue, alpha = image.pixel(x, y)
            samples += 1
            blue_opaque += int(alpha >= 250 and blue >= red + 40 and blue >= green + 30)
    return samples > 0 and blue_opaque >= samples * 7 // 10


def _has_rendered_activity(image: PngRgba, bounds: tuple[int, int, int, int]) -> bool:
    left, top, width, height = bounds
    right = left + width - 1
    bottom = top + height - 1
    if right - left < 3 or bottom - top < 3:
        return False
    samples = opaque = transitions = 0
    minimum_luminance = 255
    maximum_luminance = 0
    colors: set[int] = set()
    prior_rows: dict[int, tuple[int, int, int, int]] = {}
    for y in range(top, bottom + 1, 2):
        prior: tuple[int, int, int, int] | None = None
        for x in range(left, right + 1, 2):
            pixel = image.pixel(x, y)
            samples += 1
            opaque += int(pixel[3] >= 250)
            luminance = _luminance(pixel)
            minimum_luminance = min(minimum_luminance, luminance)
            maximum_luminance = max(maximum_luminance, luminance)
            colors.add(_quantize(pixel))
            if prior is not None and _color_distance(pixel, prior) >= 24:
                transitions += 1
            if x in prior_rows and _color_distance(pixel, prior_rows[x]) >= 24:
                transitions += 1
            prior = pixel
            prior_rows[x] = pixel
    return (
        samples > 0
        and opaque >= samples * 98 // 100
        and len(colors) >= 3
        and maximum_luminance - minimum_luminance >= 20
        and transitions >= max(8, samples // 100)
    )


def validate_exact_trx(
    path: Path,
    expected_method_name: str,
    label: str,
) -> dict[str, int]:
    require(path.is_file(), f"{label} TRX is missing: {path}")
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise NativeAcceptanceError(f"{label} TRX is malformed: {exc}") from exc

    def local_name(element: ET.Element) -> str:
        return element.tag.rsplit("}", 1)[-1]

    counters = next((element for element in root.iter() if local_name(element) == "Counters"), None)
    results = [element for element in root.iter() if local_name(element) == "UnitTestResult"]
    require(counters is not None, f"{label} TRX has no result counters")

    def count(name: str) -> int:
        value = counters.attrib.get(name, "0")
        try:
            return int(value)
        except ValueError as exc:
            raise NativeAcceptanceError(f"{label} TRX counter {name} is invalid: {value}") from exc

    summary = {
        name: count(name)
        for name in (
            "total",
            "executed",
            "passed",
            "failed",
            "error",
            "timeout",
            "aborted",
            "inconclusive",
            "notExecuted",
        )
    }
    exact_pass = (
        summary["total"] == 1
        and summary["executed"] == 1
        and summary["passed"] == 1
        and all(
            summary[name] == 0
            for name in (
                "failed",
                "error",
                "timeout",
                "aborted",
                "inconclusive",
                "notExecuted",
            )
        )
        and len(results) == 1
        and results[0].attrib.get("testName") == expected_method_name
        and results[0].attrib.get("outcome") == "Passed"
    )
    require(
        exact_pass,
        f"{label} TRX must contain exactly one executed passing test: {summary}",
    )
    return summary


def process_census(repo_root: Path) -> dict[int, dict[str, Any]]:
    command = (
        "$names=@('OnslaughtCareerEditor.WinUI','testhost','vstest.console','BEA','cdb','windbg','WinDbgX');"
        "@(Get-Process -ErrorAction SilentlyContinue | Where-Object { $names -contains $_.ProcessName } | "
        "Select-Object Id,ProcessName,StartTime,@{Name='StartTimeUtcTicks';Expression={$_.StartTime.ToUniversalTime().Ticks}},Path) | ConvertTo-Json -Compress"
    )
    completed = subprocess.run(
        ["powershell.exe", "-NoLogo", "-NoProfile", "-Command", command],
        cwd=repo_root,
        text=True,
        capture_output=True,
        timeout=20,
    )
    require(completed.returncode == 0, f"relevant-process census failed: {completed.stderr.strip()}")
    raw = completed.stdout.strip()
    if not raw:
        return {}
    parsed = json.loads(raw)
    rows = parsed if isinstance(parsed, list) else [parsed]
    census: dict[int, dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        name = str(row.get("ProcessName", "")).lower()
        process_id = row.get("Id")
        if name in RELEVANT_PROCESS_NAMES and isinstance(process_id, int):
            census[process_id] = row
    return census


def describe_processes(census: dict[int, dict[str, Any]]) -> str:
    return ", ".join(
        f"{row.get('ProcessName')}[{process_id}]"
        for process_id, row in sorted(census.items())
    ) or "zero"


def require_reparse_free_tree(root: Path, *, label: str) -> None:
    if not os.path.lexists(root):
        return
    reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    pending = [root]
    while pending:
        directory = pending.pop()
        directory_stat = os.lstat(directory)
        require(
            not os.path.islink(directory)
            and not (getattr(directory_stat, "st_file_attributes", 0) & reparse_flag),
            f"{label} contains a reparse point: {directory}",
        )
        with os.scandir(directory) as entries:
            for entry in entries:
                entry_stat = entry.stat(follow_symlinks=False)
                entry_path = Path(entry.path)
                require(
                    not entry.is_symlink()
                    and not (getattr(entry_stat, "st_file_attributes", 0) & reparse_flag),
                    f"{label} contains a reparse point: {entry_path}",
                )
                if entry.is_dir(follow_symlinks=False):
                    pending.append(entry_path)


def remove_reparse_free_tree(root: Path, *, label: str) -> None:
    require_reparse_free_tree(root, label=label)
    if os.path.lexists(root):
        root_stat = os.lstat(root)
        reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
        require(
            not os.path.islink(root)
            and not (getattr(root_stat, "st_file_attributes", 0) & reparse_flag),
            f"{label} root became a reparse point before removal: {root}",
        )
        shutil.rmtree(root)


def capture_owned_process_identity(
    process_id: int,
    *,
    repo_root: Path,
) -> OwnedProcessIdentity:
    script = (
        "$expectedPid=[int]$env:ONSLAUGHT_NATIVE_CAPTURE_PID;"
        "$p=Get-Process -Id $expectedPid -ErrorAction SilentlyContinue;"
        "if($null -eq $p){exit 44};"
        "[pscustomobject]@{Id=$p.Id;"
        "StartTimeUtcTicks=$p.StartTime.ToUniversalTime().Ticks;"
        "Path=$p.Path}|ConvertTo-Json -Compress"
    )
    environment = os.environ.copy()
    environment["ONSLAUGHT_NATIVE_CAPTURE_PID"] = str(process_id)
    completed = subprocess.run(
        ["powershell.exe", "-NoLogo", "-NoProfile", "-Command", script],
        cwd=repo_root,
        env=environment,
        text=True,
        capture_output=True,
        timeout=20,
    )
    require(
        completed.returncode == 0,
        f"could not capture owned process identity for {process_id}: "
        f"{completed.stderr.strip() or completed.stdout.strip() or f'exit {completed.returncode}'}",
    )
    try:
        row = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise NativeAcceptanceError(f"owned process identity for {process_id} is malformed") from exc
    require(
        isinstance(row, dict)
        and row.get("Id") == process_id
        and isinstance(row.get("StartTimeUtcTicks"), int)
        and row["StartTimeUtcTicks"] > 0
        and isinstance(row.get("Path"), str)
        and row["Path"],
        f"owned process identity for {process_id} is incomplete",
    )
    return OwnedProcessIdentity(
        process_id=process_id,
        start_time_utc_ticks=row["StartTimeUtcTicks"],
        executable_path=Path(row["Path"]),
    )


def terminate_owned_process_tree(
    identity: OwnedProcessIdentity,
    *,
    repo_root: Path,
) -> None:
    script = (
        "$expectedPid=[int]$env:ONSLAUGHT_NATIVE_CLEANUP_PID;"
        "$expectedPath=$env:ONSLAUGHT_NATIVE_CLEANUP_PATH;"
        "$expectedTicks=[long]$env:ONSLAUGHT_NATIVE_CLEANUP_START_TICKS;"
        "$p=Get-Process -Id $expectedPid -ErrorAction SilentlyContinue;"
        "if($null -eq $p){exit 0};"
        "if(-not [string]::Equals("
        "[IO.Path]::GetFullPath($p.Path),[IO.Path]::GetFullPath($expectedPath),"
        "[StringComparison]::OrdinalIgnoreCase)){exit 41};"
        "if($p.StartTime.ToUniversalTime().Ticks -ne $expectedTicks){exit 42};"
        "& taskkill.exe /PID $expectedPid /T /F *> $null;"
        "$taskkillExit=$LASTEXITCODE;"
        "if($taskkillExit -ne 0 -and $taskkillExit -ne 128){exit 43}"
    )
    environment = os.environ.copy()
    environment.update(
        {
            "ONSLAUGHT_NATIVE_CLEANUP_PID": str(identity.process_id),
            "ONSLAUGHT_NATIVE_CLEANUP_PATH": str(identity.executable_path),
            "ONSLAUGHT_NATIVE_CLEANUP_START_TICKS": str(identity.start_time_utc_ticks),
        }
    )
    completed = subprocess.run(
        ["powershell.exe", "-NoLogo", "-NoProfile", "-Command", script],
        cwd=repo_root,
        env=environment,
        text=True,
        capture_output=True,
        timeout=20,
    )
    if completed.returncode in {41, 42}:
        raise NativeAcceptanceError(
            f"refusing to terminate process tree {identity.process_id}: live identity no longer matches capture"
        )
    require(
        completed.returncode == 0,
        f"failed to terminate owned process tree {identity.process_id}: "
        f"{completed.stderr.strip() or completed.stdout.strip()}",
    )


def run_command(
    command: list[str],
    *,
    repo_root: Path,
    timeout: int,
    env_overrides: dict[str, str] | None = None,
) -> None:
    print(f"\n$ {' '.join(command)}", flush=True)
    env = os.environ.copy()
    env["MSBUILDDISABLENODEREUSE"] = "1"
    if env_overrides:
        env.update(env_overrides)
    process = subprocess.Popen(command, cwd=repo_root, env=env)
    try:
        identity = capture_owned_process_identity(process.pid, repo_root=repo_root)
    except Exception:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=20)
        raise
    try:
        return_code = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired as timeout_error:
        termination_error: Exception | None = None
        try:
            if process.poll() is None:
                terminate_owned_process_tree(identity, repo_root=repo_root)
        except Exception as exc:
            termination_error = exc
        try:
            process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
        if termination_error is not None:
            raise NativeAcceptanceError(
                f"command timed out and identity-bound tree termination failed: {termination_error}"
            ) from timeout_error
        raise timeout_error
    require(return_code == 0, f"command exited {return_code}: {' '.join(command)}")


def validate_invocation_id(invocation_id: str) -> None:
    require(
        re.fullmatch(r"[0-9a-f]{32}", invocation_id) is not None,
        "runner invocation ID is invalid",
    )


def shutdown_build_servers(repo_root: Path) -> None:
    completed = subprocess.run(
        ["dotnet", "build-server", "shutdown"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        timeout=30,
    )
    require(completed.returncode == 0, f"dotnet build-server shutdown exited {completed.returncode}")


def append_cleanup_error(
    error: Exception | None,
    phase: str,
    cleanup_error: Exception,
) -> NativeAcceptanceError:
    prefix = f"{error}; " if error is not None else ""
    return NativeAcceptanceError(f"{prefix}{phase} failed: {cleanup_error}")
