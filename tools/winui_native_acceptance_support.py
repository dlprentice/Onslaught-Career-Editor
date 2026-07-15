#!/usr/bin/env python3
"""Shared fail-closed lifecycle helpers for native WinUI acceptance gates."""

from __future__ import annotations

import hashlib
import json
import os
import re
import struct
import subprocess
import xml.etree.ElementTree as ET
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


class NativeAcceptanceError(RuntimeError):
    pass


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


def terminate_owned_process_tree(root_process_id: int, *, repo_root: Path) -> None:
    completed = subprocess.run(
        ["taskkill.exe", "/PID", str(root_process_id), "/T", "/F"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        timeout=20,
    )
    require(
        completed.returncode in {0, 128},
        f"failed to terminate owned process tree {root_process_id}: "
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
        return_code = process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        terminate_owned_process_tree(process.pid, repo_root=repo_root)
        try:
            process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
        raise
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
