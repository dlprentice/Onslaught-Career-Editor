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


class NativeAcceptanceError(RuntimeError):
    pass


@dataclass(frozen=True)
class OwnedProcessIdentity:
    process_id: int
    start_time_utc_ticks: int
    executable_path: Path


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
