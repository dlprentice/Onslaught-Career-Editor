#!/usr/bin/env python3
"""Run one private music audible-output live raw-bundle attempt.

This is a private proof executor. It may launch a copied BEA instance, attach
observer-only CDB, and capture loopback audio only when explicitly armed. It
never mutates the installed Steam game folder or original executable.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import winui_safe_copy_music_audible_output_materializer as materializer
import winui_safe_copy_music_audible_output_two_run_harness_check as final_check
import winui_safe_copy_music_timestamped_cdb_log_producer as timestamp_producer


ROOT = Path(__file__).resolve().parents[1]
ARM_PHRASE = "RUN PRIVATE MUSIC AUDIBLE LIVE BUNDLE"
LIVE_ARM = "LAUNCH SAFE COPY BEA"
CDB_ARM = "ATTACH CDB TO SAFE COPY BEA"
AUDIO_ARM = "CAPTURE LOOPBACK AUDIO"
CORRELATION_ARM = "BUILD CAPTURE SOURCE CORRELATION"
EXTERNAL_LIVE_ROOT_ARM = "ALLOW EXTERNAL LIVE SMOKE ARTIFACT ROOT"
PREARM_SCHEMA = "winui-safe-copy-music-audible-output-live-bundle-prearm-readiness.v1"
PREARM_ACCEPTED_STATUS = "accepted-private-prearm-readiness"
REQUIRED_RESOURCE_LEASES = (
    "bea-runtime",
    "cdb-debugger",
    "audio-loopback",
    "proof-root",
)
LEVEL_ID = 100
PRESET_ID = "use-bea02-for-bea04"
TARGET = "BEA_04(Master).ogg"
REPLACEMENT = "BEA_02(Master).ogg"
OBSERVATION_SCHEMA = "winui-safe-copy-timestamped-cdb-log-observations.v1"
TIMESTAMP_SOURCE = "trusted-tail-wrapper-observation-ledger"
ROLE_DIRS = {
    "ambientNoBea": "ambient-no-bea",
    "cleanBaseline": "clean-baseline",
    "stagedPositive": "staged-positive",
    "muteControl": "mute-control",
}
RAW_LINE_INTERVAL_MS = 100
CDB_STAGE_ROLES = {"cleanBaseline", "stagedPositive"}
CDB_CLEANUP_ACCEPTED_STATUSES = {"stopped", "already-exited"}
AUDIO_CAPTURE_STARTUP_MARGIN_MS = 15000
DEFAULT_LIVE_AUDIO_DURATION_MS = 60000
MIN_LIVE_ATTEMPT_AUDIO_DURATION_MS = 60000
SAFE_ENV_KEYS = {
    "ALLUSERSPROFILE",
    "APPDATA",
    "COMSPEC",
    "CommonProgramFiles",
    "CommonProgramFiles(x86)",
    "CommonProgramW6432",
    "HOMEDRIVE",
    "HOMEPATH",
    "LOCALAPPDATA",
    "NUMBER_OF_PROCESSORS",
    "OS",
    "PATH",
    "PATHEXT",
    "PROCESSOR_ARCHITECTURE",
    "PROCESSOR_IDENTIFIER",
    "PROCESSOR_LEVEL",
    "PROCESSOR_REVISION",
    "ProgramData",
    "ProgramFiles",
    "ProgramFiles(x86)",
    "ProgramW6432",
    "SystemDrive",
    "SystemRoot",
    "TEMP",
    "TMP",
    "USERDOMAIN",
    "USERNAME",
    "USERPROFILE",
    "WINDIR",
}
SAFE_ENV_KEYS_LOWER = {key.lower() for key in SAFE_ENV_KEYS}


class LiveBundleError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise LiveBundleError(message)


def validate_live_attempt_audio_duration(duration_ms: int) -> None:
    require(
        duration_ms >= MIN_LIVE_ATTEMPT_AUDIO_DURATION_MS,
        f"--audio-duration-ms must be at least {MIN_LIVE_ATTEMPT_AUDIO_DURATION_MS} for live bundle attempts.",
    )


def format_utc(value: dt.datetime) -> str:
    value = value.astimezone(dt.timezone.utc)
    if value.microsecond:
        text = value.isoformat(timespec="milliseconds")
    else:
        text = value.isoformat(timespec="seconds")
    return text.replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    require(isinstance(value, dict), f"JSON input must be an object: {path}")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sanitized_child_env() -> dict[str, str]:
    env: dict[str, str] = {}
    for key, value in os.environ.items():
        if key.lower() in SAFE_ENV_KEYS_LOWER:
            env[key] = value
    env["DOTNET_CLI_TELEMETRY_OPTOUT"] = "1"
    env["DOTNET_SKIP_FIRST_TIME_EXPERIENCE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return env


def is_same_or_under(path: Path, root: Path) -> bool:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    return resolved_path == resolved_root or resolved_root in resolved_path.parents


def paths_overlap(left: Path, right: Path) -> bool:
    return is_same_or_under(left, right) or is_same_or_under(right, left)


def validate_no_symlink_or_reparse(path: Path) -> None:
    try:
        materializer.validate_no_symlink_or_reparse(path)
    except materializer.MaterializerError as exc:
        raise LiveBundleError(str(exc)) from exc


@dataclass(frozen=True)
class StagePaths:
    role: str
    root: Path

    @property
    def live_root(self) -> Path:
        return self.root / "live"

    @property
    def live_json(self) -> Path:
        return self.live_root / "live-safe-copy-runtime-smoke.json"

    @property
    def raw_cdb_log(self) -> Path:
        return self.live_root / "cdb" / "windbg.log"

    @property
    def cdb_observation_ledger(self) -> Path:
        return self.root / "cdb" / "timestamp-observations.json"

    @property
    def timestamped_cdb_log(self) -> Path:
        return self.root / "cdb" / "windbg.timestamped.log"

    @property
    def timestamped_cdb_receipt(self) -> Path:
        return self.root / "cdb" / "timestamped-cdb-log-receipt.json"

    @property
    def timeline(self) -> Path:
        return self.root / "cdb" / "timeline.json"

    @property
    def audio_root(self) -> Path:
        return self.root / "audio"

    @property
    def audio_json(self) -> Path:
        return self.audio_root / f"{self.role}.json"

    @property
    def audio_wav(self) -> Path:
        return self.audio_root / f"{self.role}.wav"

    @property
    def source_snapshot(self) -> Path:
        return self.root / "source-music-before.json"

    @property
    def source_safety(self) -> Path:
        return self.root / "source-music-safety.json"

    @property
    def ambient_samples(self) -> Path:
        return self.root / "ambient-process-samples.json"

    @property
    def ambient_census(self) -> Path:
        return self.root / "no-bea-census.json"


@dataclass(frozen=True)
class BundleLayout:
    root: Path

    def stage(self, role: str) -> StagePaths:
        require(role in ROLE_DIRS, f"Unknown music bundle role: {role}")
        return StagePaths(role=role, root=self.root / "raw" / ROLE_DIRS[role])

    @property
    def raw_root(self) -> Path:
        return self.root / "raw"

    @property
    def correlation(self) -> Path:
        return self.raw_root / "capture-source-correlation.json"

    @property
    def capture_source_correlation_rejection(self) -> Path:
        return self.raw_root / "capture-source-correlation-rejection.json"

    @property
    def final_proof(self) -> Path:
        return self.raw_root / "audible-proof.json"

    @property
    def receipt(self) -> Path:
        return self.root / "live-bundle-attempt-receipt.json"


def build_layout(root: Path) -> BundleLayout:
    return BundleLayout(root=root.resolve())


def audio_capture_command(stage: StagePaths, *, duration_ms: int, source_root: Path) -> list[str]:
    return [
        "py",
        "-3",
        r"tools\capture_audio_loopback.py",
        "--capture",
        "--allowed-output-root",
        str(stage.audio_root),
        "--output-wav",
        str(stage.audio_wav),
        "--output-json",
        str(stage.audio_json),
        "--source-game-root",
        str(source_root),
        "--duration-ms",
        str(duration_ms),
        "--arm-capture-audio",
        AUDIO_ARM,
    ]


def live_smoke_command(
    layout: BundleLayout,
    role: str,
    *,
    source_root: Path,
    timeout_seconds: int = 24,
    capture_count: int = 2,
) -> list[str]:
    stage = layout.stage(role)
    post_window_delay_seconds = "0" if role in {"cleanBaseline", "stagedPositive"} else "2"
    command = [
        "py",
        "-3",
        r"tools\winui_safe_copy_live_runtime_smoke.py",
        "--source-root",
        str(source_root),
        "--artifact-root",
        str(stage.live_root),
        "--arm-external-artifact-root",
        EXTERNAL_LIVE_ROOT_ARM,
        "--timeout-seconds",
        str(timeout_seconds),
        "--capture-count",
        str(capture_count),
        "--capture-interval-seconds",
        "2",
        "--post-window-delay-seconds",
        post_window_delay_seconds,
        "--level-id",
        str(LEVEL_ID),
        "--arm-live-bea",
        LIVE_ARM,
    ]
    if role in {"cleanBaseline", "stagedPositive"}:
        command.extend(
            [
                "--enable-cdb-observer",
                "--arm-cdb-observer",
                CDB_ARM,
                "--cdb-command-file",
                r"tools\runtime-probes\safe-copy-music-selection-decode-observer.cdb.txt",
                "--cdb-log-ready-timeout-ms",
                "20000",
                "--cdb-post-attach-wait-seconds",
                "4",
                "--cdb-attach-phase",
                "after-launch",
            ]
        )
    if role == "stagedPositive":
        command.extend(["--stage-music-replacement", "--music-swap-preset-id", PRESET_ID])
    if role == "muteControl":
        command.append("--launch-nomusic")
    return command


def source_snapshot_command(stage: StagePaths, *, source_root: Path) -> list[str]:
    return [
        "py",
        "-3",
        r"tools\winui_safe_copy_music_source_music_safety_sidecar.py",
        "--source-root",
        str(source_root),
        "--snapshot-output",
        str(stage.source_snapshot),
    ]


def source_safety_command(stage: StagePaths, *, source_root: Path) -> list[str]:
    return [
        "py",
        "-3",
        r"tools\winui_safe_copy_music_source_music_safety_sidecar.py",
        "--source-root",
        str(source_root),
        "--before-snapshot",
        str(stage.source_snapshot),
        "--live",
        str(stage.live_json),
        "--output",
        str(stage.source_safety),
        "--role",
        stage.role,
    ]


def timestamped_log_command(stage: StagePaths) -> list[str]:
    return [
        "py",
        "-3",
        r"tools\winui_safe_copy_music_timestamped_cdb_log_producer.py",
        "--raw-cdb-log",
        str(stage.raw_cdb_log),
        "--observation-ledger",
        str(stage.cdb_observation_ledger),
        "--timestamped-log-output",
        str(stage.timestamped_cdb_log),
        "--receipt-output",
        str(stage.timestamped_cdb_receipt),
        "--allowed-output-root",
        str(stage.root),
        "--role",
        stage.role,
    ]


def timeline_command(stage: StagePaths) -> list[str]:
    return [
        "py",
        "-3",
        r"tools\winui_safe_copy_music_cdb_timeline_sidecar.py",
        "--live",
        str(stage.live_json),
        "--timestamped-cdb-log",
        str(stage.timestamped_cdb_log),
        "--output",
        str(stage.timeline),
        "--role",
        stage.role,
    ]


def ambient_census_command(stage: StagePaths, *, observe_ms: int) -> list[str]:
    return [
        "py",
        "-3",
        r"tools\winui_safe_copy_music_ambient_no_bea_census.py",
        "--audio",
        str(stage.audio_json),
        "--output",
        str(stage.ambient_census),
        "--observe-ms",
        str(observe_ms),
        "--poll-ms",
        "250",
        "--write-samples",
        str(stage.ambient_samples),
    ]


def capture_source_correlation_command(layout: BundleLayout, *, source_root: Path) -> list[str]:
    return [
        "py",
        "-3",
        r"tools\winui_safe_copy_music_capture_source_correlation_builder.py",
        "--build",
        "--clean-audio",
        str(layout.stage("cleanBaseline").audio_json),
        "--staged-audio",
        str(layout.stage("stagedPositive").audio_json),
        "--source-root",
        str(source_root),
        "--allowed-output-root",
        str(layout.raw_root),
        "--output",
        str(layout.correlation),
        "--rejection-diagnostic-output",
        str(layout.capture_source_correlation_rejection),
        "--arm-correlation",
        CORRELATION_ARM,
    ]


def materializer_command(layout: BundleLayout) -> list[str]:
    return [
        "py",
        "-3",
        r"tools\winui_safe_copy_music_audible_output_materializer.py",
        "--clean-live",
        str(layout.stage("cleanBaseline").live_json),
        "--staged-live",
        str(layout.stage("stagedPositive").live_json),
        "--mute-live",
        str(layout.stage("muteControl").live_json),
        "--clean-timeline",
        str(layout.stage("cleanBaseline").timeline),
        "--staged-timeline",
        str(layout.stage("stagedPositive").timeline),
        "--clean-source-music-safety",
        str(layout.stage("cleanBaseline").source_safety),
        "--mute-source-music-safety",
        str(layout.stage("muteControl").source_safety),
        "--ambient-census",
        str(layout.stage("ambientNoBea").ambient_census),
        "--ambient-audio",
        str(layout.stage("ambientNoBea").audio_json),
        "--clean-audio",
        str(layout.stage("cleanBaseline").audio_json),
        "--staged-audio",
        str(layout.stage("stagedPositive").audio_json),
        "--mute-audio",
        str(layout.stage("muteControl").audio_json),
        "--capture-source-correlation",
        str(layout.correlation),
        "--output",
        str(layout.final_proof),
    ]


def checker_command(layout: BundleLayout) -> list[str]:
    return ["py", "-3", r"tools\winui_safe_copy_music_audible_output_two_run_harness_check.py", str(layout.final_proof)]


def write_observation_ledger(
    *,
    raw_cdb_log: Path,
    output: Path,
    role: str,
    observed_at_start: dt.datetime,
) -> dict[str, Any]:
    require(raw_cdb_log.is_file(), f"Raw CDB log missing: {raw_cdb_log}")
    lines = raw_cdb_log.read_text(encoding="utf-8", errors="replace").splitlines()
    require(lines, "Raw CDB log is empty.")
    observations = []
    for index, line in enumerate(lines):
        observations.append(
            {
                "lineIndex": index,
                "lineSha256": sha256_text(line),
                "observedAtUtc": format_utc(observed_at_start + dt.timedelta(milliseconds=index * RAW_LINE_INTERVAL_MS)),
            }
        )
    payload = {
        "schemaVersion": OBSERVATION_SCHEMA,
        "role": role,
        "timestampSource": TIMESTAMP_SOURCE,
        "rawCdbLogSha256": sha256_file(raw_cdb_log),
        "observations": observations,
    }
    write_json(output, payload)
    return payload


class CdbLogTailer:
    def __init__(self, *, raw_cdb_log: Path, role: str) -> None:
        self.raw_cdb_log = raw_cdb_log
        self.role = role
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._observed: dict[int, dt.datetime] = {}

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, name=f"cdb-tail-{self.role}", daemon=True)
        self._thread.start()

    def stop_and_write(self, output: Path) -> dict[str, Any]:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=5)
        self._observe_once(include_partial=True)
        require(self.raw_cdb_log.is_file(), f"Raw CDB log missing after live run: {self.raw_cdb_log}")
        lines = self.raw_cdb_log.read_text(encoding="utf-8", errors="replace").splitlines()
        require(lines, "Raw CDB log is empty after live run.")
        fallback_at = dt.datetime.now(dt.timezone.utc)
        observations = []
        previous_at: dt.datetime | None = None
        for index, line in enumerate(lines):
            observed_at = self._observed.get(index) or (fallback_at + dt.timedelta(milliseconds=index * RAW_LINE_INTERVAL_MS))
            if previous_at is not None and observed_at < previous_at:
                observed_at = previous_at
            previous_at = observed_at
            observations.append({"lineIndex": index, "lineSha256": sha256_text(line), "observedAtUtc": format_utc(observed_at)})
        payload = {
            "schemaVersion": OBSERVATION_SCHEMA,
            "role": self.role,
            "timestampSource": TIMESTAMP_SOURCE,
            "rawCdbLogSha256": sha256_file(self.raw_cdb_log),
            "observations": observations,
        }
        write_json(output, payload)
        return payload

    def _run(self) -> None:
        while not self._stop.is_set():
            self._observe_once(include_partial=False)
            self._stop.wait(0.1)

    def _observe_once(self, *, include_partial: bool) -> None:
        if not self.raw_cdb_log.is_file():
            return
        text = self.raw_cdb_log.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        if not include_partial and text and not text.endswith(("\n", "\r")):
            lines = lines[:-1]
        now = dt.datetime.now(dt.timezone.utc)
        for index in range(len(lines)):
            self._observed.setdefault(index, now)


def terminate_process_tree(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
            env=sanitized_child_env(),
        )
    if process.poll() is None:
        process.kill()


def run_command(command: list[str], *, log_root: Path, label: str, timeout_seconds: int | None = None) -> subprocess.CompletedProcess[str]:
    log_root.mkdir(parents=True, exist_ok=True)
    (log_root / f"{label}.command.json").write_text(json.dumps(command, indent=2) + "\n", encoding="utf-8")
    process = subprocess.Popen(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=sanitized_child_env(),
    )
    try:
        stdout_text, stderr_text = process.communicate(timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        terminate_process_tree(process)
        stdout_text, stderr_text = process.communicate(timeout=10)
        (log_root / f"{label}.stdout.log").write_text(stdout_text or "", encoding="utf-8")
        (log_root / f"{label}.stderr.log").write_text(stderr_text or "", encoding="utf-8")
        raise LiveBundleError(f"{label} timed out after {timeout_seconds} seconds.") from exc
    result = subprocess.CompletedProcess(command, process.returncode, stdout_text, stderr_text)
    (log_root / f"{label}.stdout.log").write_text(result.stdout, encoding="utf-8")
    (log_root / f"{label}.stderr.log").write_text(result.stderr, encoding="utf-8")
    if result.returncode != 0:
        raise LiveBundleError(f"{label} failed with exit code {result.returncode}.")
    return result


def start_command(command: list[str], *, log_root: Path, label: str) -> tuple[subprocess.Popen[str], Any, Any]:
    log_root.mkdir(parents=True, exist_ok=True)
    (log_root / f"{label}.command.json").write_text(json.dumps(command, indent=2) + "\n", encoding="utf-8")
    stdout = (log_root / f"{label}.stdout.log").open("w", encoding="utf-8")
    stderr = (log_root / f"{label}.stderr.log").open("w", encoding="utf-8")
    process = subprocess.Popen(command, cwd=ROOT, text=True, stdout=stdout, stderr=stderr, env=sanitized_child_env())
    return process, stdout, stderr


def wait_process(process: subprocess.Popen[str], stdout: Any, stderr: Any, *, label: str, timeout_seconds: int) -> None:
    try:
        return_code = process.wait(timeout=timeout_seconds)
    except subprocess.TimeoutExpired as exc:
        terminate_process_tree(process)
        process.wait(timeout=10)
        raise LiveBundleError(f"{label} timed out after {timeout_seconds} seconds.") from exc
    finally:
        stdout.close()
        stderr.close()
    if return_code != 0:
        raise LiveBundleError(f"{label} failed with exit code {return_code}.")


def parse_tasklist_csv(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in csv.reader(io.StringIO(text)):
        if len(row) < 2 or row[0].strip().lower() == "image name":
            continue
        rows.append({"imageName": row[0].strip(), "pid": row[1].strip()})
    return rows


def process_row_pid(row: dict[str, Any]) -> int:
    raw = row.get("ProcessId", row.get("processId", row.get("pid")))
    try:
        value = int(str(raw))
    except (TypeError, ValueError) as exc:
        raise LiveBundleError(f"Process row has invalid PID: {row}") from exc
    require(value > 0, f"Process row has invalid PID: {row}")
    return value


def process_row_name(row: dict[str, Any]) -> str:
    return str(row.get("Name", row.get("imageName", ""))).strip()


def process_row_executable_path(row: dict[str, Any]) -> str:
    return str(row.get("ExecutablePath", row.get("executablePath", "")) or "").strip()


def process_row_command_line(row: dict[str, Any]) -> str:
    return str(row.get("CommandLine", row.get("commandLine", "")) or "").strip()


def powershell_executable() -> str:
    return shutil.which("pwsh") or shutil.which("powershell") or "powershell"


def snapshot_bea_or_cdb_processes() -> list[dict[str, Any]]:
    command = [
        powershell_executable(),
        "-NoProfile",
        "-Command",
        (
            "$items = @(Get-CimInstance Win32_Process "
            "-Filter \"Name = 'BEA.exe' OR Name = 'cdb.exe'\" | "
            "Select-Object Name,ProcessId,ExecutablePath,CommandLine,CreationDate); "
            "if ($items.Count -eq 0) { '[]' } else { $items | ConvertTo-Json -Compress }"
        ),
    ]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=20, check=False, env=sanitized_child_env())
    require(result.returncode == 0, "PowerShell process snapshot failed before live bundle attempt.")
    text = result.stdout.strip()
    if not text:
        return []
    payload = json.loads(text)
    if isinstance(payload, dict):
        return [payload]
    require(isinstance(payload, list), "PowerShell process snapshot did not return a JSON list.")
    return [row for row in payload if isinstance(row, dict)]


def snapshot_process_by_pid(pid: int) -> dict[str, Any] | None:
    command = [
        powershell_executable(),
        "-NoProfile",
        "-Command",
        (
            f"$item = Get-CimInstance Win32_Process -Filter \"ProcessId = {pid}\" | "
            "Select-Object Name,ProcessId,ExecutablePath,CommandLine,CreationDate; "
            "if ($null -eq $item) { 'null' } else { $item | ConvertTo-Json -Compress }"
        ),
    ]
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=20, check=False, env=sanitized_child_env())
    require(result.returncode == 0, f"PowerShell process revalidation failed for PID {pid}.")
    payload = json.loads(result.stdout.strip() or "null")
    if payload is None:
        return None
    require(isinstance(payload, dict), f"PowerShell process revalidation did not return an object for PID {pid}.")
    return payload


def command_line_contains_path(command_line: str, path: Path) -> bool:
    if not command_line:
        return False
    normalized_line = os.path.normcase(command_line).replace("/", "\\")
    normalized_path = os.path.normcase(str(path.resolve())).replace("/", "\\").rstrip("\\")
    index = normalized_line.find(normalized_path)
    while index >= 0:
        before = normalized_line[index - 1] if index > 0 else ""
        after_index = index + len(normalized_path)
        after = normalized_line[after_index] if after_index < len(normalized_line) else ""
        if before in {"", '"', "'", " ", "="} and after in {"", "\\", '"', "'", " ", ";"}:
            return True
        index = normalized_line.find(normalized_path, index + 1)
    return False


def stage_live_roots(layout: BundleLayout) -> tuple[Path, ...]:
    return tuple(layout.stage(role).live_root for role in ROLE_DIRS)


def stage_cdb_log_paths(layout: BundleLayout) -> tuple[Path, ...]:
    return tuple(layout.stage(role).raw_cdb_log for role in CDB_STAGE_ROLES)


def is_generated_profile_exe(path: Path, live_roots: tuple[Path, ...]) -> bool:
    if path.name.lower() != "bea.exe":
        return False
    for live_root in live_roots:
        try:
            if not is_same_or_under(path, live_root):
                continue
        except OSError:
            continue
        parts = {part.lower() for part in path.parts}
        if "gameprofiles" not in parts:
            return False
        manifest = path.parent / "onslaught-profile-manifest.json"
        return manifest.is_file()
    return False


def process_attempt_match(row: dict[str, Any], layout: BundleLayout) -> str | None:
    name = process_row_name(row).lower()
    if name not in {"bea.exe", "cdb.exe"}:
        return None
    live_roots = stage_live_roots(layout)
    executable_path = process_row_executable_path(row)
    if name == "bea.exe" and executable_path:
        try:
            if is_generated_profile_exe(Path(executable_path), live_roots):
                return "executablePath"
        except OSError:
            pass
    if name == "cdb.exe":
        command_line = process_row_command_line(row)
        for cdb_log_path in stage_cdb_log_paths(layout):
            if command_line_contains_path(command_line, cdb_log_path):
                return "commandLine"
    return None


def cleanup_attempt_owned_processes(layout: BundleLayout) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    for row in snapshot_bea_or_cdb_processes():
        match = process_attempt_match(row, layout)
        if match is None:
            continue
        pid = process_row_pid(row)
        image_name = process_row_name(row)
        creation_date = str(row.get("CreationDate", "") or "")
        current = snapshot_process_by_pid(pid)
        if current is None:
            results.append(
                {
                    "imageName": image_name,
                    "processId": pid,
                    "matchedBy": match,
                    "status": "already-exited-before-kill",
                    "stopped": True,
                }
            )
            continue
        revalidated_match = process_attempt_match(current, layout)
        current_creation_date = str(current.get("CreationDate", "") or "")
        if revalidated_match is None or (creation_date and current_creation_date and creation_date != current_creation_date):
            results.append(
                {
                    "imageName": image_name,
                    "processId": pid,
                    "matchedBy": match,
                    "status": "skipped-revalidation-failed",
                    "stopped": False,
                }
            )
            continue
        kill_result = subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=15,
            check=False,
            env=sanitized_child_env(),
        )
        results.append(
            {
                "imageName": image_name,
                "processId": pid,
                "matchedBy": revalidated_match,
                "status": "taskkill-executed",
                "exitCode": kill_result.returncode,
                "stopped": kill_result.returncode == 0,
            }
        )
    return {
        "schemaVersion": "winui-safe-copy-live-bundle-failure-process-cleanup.v1",
        "attemptRoot": str(layout.root),
        "matchedProcessCount": len(results),
        "results": results,
    }


def ensure_no_bea_or_cdb_processes() -> None:
    matches = []
    for row in snapshot_bea_or_cdb_processes():
        name = process_row_name(row).lower()
        if name in {"bea.exe", "cdb.exe"}:
            matches.append({"imageName": process_row_name(row), "pid": str(process_row_pid(row))})
    require(not matches, f"Refusing live bundle attempt while BEA/CDB processes exist: {matches}")


def validate_roots(layout: BundleLayout, source_root: Path) -> None:
    require(source_root.is_dir(), f"Source root does not exist: {source_root}")
    require(not paths_overlap(layout.root, source_root), "Live bundle root must not overlap the source game root.")
    layout.root.mkdir(parents=True, exist_ok=True)
    validate_no_symlink_or_reparse(layout.root)
    validate_no_symlink_or_reparse(source_root)
    require(not any(layout.root.iterdir()), "Live bundle root must be empty for a new attempt.")


def nested_dict(value: Any, *, label: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{label} must be a JSON object.")
    return value


def require_exact_keys(value: dict[str, Any], expected: set[str], *, label: str) -> None:
    actual = set(value)
    require(actual == expected, f"{label} keys changed: expected {sorted(expected)}, got {sorted(actual)}")


def require_true(value: dict[str, Any], key: str, *, label: str) -> None:
    require(value.get(key) is True, f"{label}.{key} must be true.")


def positive_int(value: Any, *, label: str) -> int:
    require(isinstance(value, int) and value > 0, f"{label} must be a positive integer.")
    return value


def validate_private_prearm_readiness(path: Path) -> dict[str, Any]:
    require(path.is_file(), "Provide --prearm-readiness-json for a private accepted pre-arm readiness artifact.")
    payload = read_json(path)
    require_exact_keys(
        payload,
        {
            "schemaVersion",
            "status",
            "runtimeAudibleOutputProof",
            "liveArmAllowedByPrearm",
            "runtimeProofAuthority",
            "resourceLeases",
            "processPreflight",
            "proofRootPreflight",
            "sourceMutationPolicy",
            "captureSpanDecodeWindowPreflight",
            "rawProofPolicy",
            "readinessFailurePolicy",
            "claimBoundary",
        },
        label="prearm",
    )
    require(payload.get("schemaVersion") == PREARM_SCHEMA, "Private pre-arm readiness schema changed.")
    require(payload.get("status") == PREARM_ACCEPTED_STATUS, "Private pre-arm readiness status is not accepted.")
    require(payload.get("runtimeAudibleOutputProof") is False, "Private pre-arm readiness must not claim runtime audible output.")
    require(payload.get("liveArmAllowedByPrearm") is True, "Private pre-arm readiness must explicitly allow the live arm.")

    authority = nested_dict(payload.get("runtimeProofAuthority"), label="runtimeProofAuthority")
    require_exact_keys(authority, {"explicitRuntimeProofAuthorityRecorded", "requiredArmPhrase"}, label="runtimeProofAuthority")
    require_true(authority, "explicitRuntimeProofAuthorityRecorded", label="runtimeProofAuthority")
    require(authority.get("requiredArmPhrase") == ARM_PHRASE, "Private pre-arm readiness arm phrase mismatch.")

    leases = nested_dict(payload.get("resourceLeases"), label="resourceLeases")
    require_exact_keys(leases, set(REQUIRED_RESOURCE_LEASES), label="resourceLeases")
    for lease in REQUIRED_RESOURCE_LEASES:
        require_true(leases, lease, label="resourceLeases")

    process = nested_dict(payload.get("processPreflight"), label="processPreflight")
    require_exact_keys(process, {"noPreexistingBeaOrCdb", "passiveProcessCensusOnly"}, label="processPreflight")
    require_true(process, "noPreexistingBeaOrCdb", label="processPreflight")
    require_true(process, "passiveProcessCensusOnly", label="processPreflight")

    proof_root = nested_dict(payload.get("proofRootPreflight"), label="proofRootPreflight")
    require_exact_keys(
        proof_root,
        {"emptyIsolatedPrivateProofRoot", "mustNotOverlapReadOnlySourceRoot", "localIgnoredRawProofOnly"},
        label="proofRootPreflight",
    )
    for key in proof_root:
        require_true(proof_root, key, label="proofRootPreflight")

    mutation = nested_dict(payload.get("sourceMutationPolicy"), label="sourceMutationPolicy")
    require_exact_keys(
        mutation,
        {"copiedProfileAndAppOwnedArtifactRootsOnly", "installedGameAndOriginalBeaReadOnly"},
        label="sourceMutationPolicy",
    )
    for key in mutation:
        require_true(mutation, key, label="sourceMutationPolicy")

    capture_span = nested_dict(payload.get("captureSpanDecodeWindowPreflight"), label="captureSpanDecodeWindowPreflight")
    require_exact_keys(
        capture_span,
        {
            "captureStartedUtcStopwatchAlignmentVerified",
            "wavWallClockDurationCoversCdbDecodeWindow",
            "helperAuthoredWallClockPaddingMetadataPresent",
            "capturedBytesPlusSilencePaddingBytesEqualsBytesRecorded",
            "canonicalWavHeaderAndDataFrameConsistencyVerified",
            "outOfRangeDecodeWindowRejectedBeforeProofClaim",
        },
        label="captureSpanDecodeWindowPreflight",
    )
    for key in capture_span:
        require_true(capture_span, key, label="captureSpanDecodeWindowPreflight")

    raw_policy = nested_dict(payload.get("rawProofPolicy"), label="rawProofPolicy")
    require_exact_keys(raw_policy, {"rawProofArtifactsStayLocalIgnored", "privatePathsNotForTrackedDocs"}, label="rawProofPolicy")
    for key in raw_policy:
        require_true(raw_policy, key, label="rawProofPolicy")

    failure_policy = nested_dict(payload.get("readinessFailurePolicy"), label="readinessFailurePolicy")
    require_exact_keys(
        failure_policy,
        {"runtimeAudibleOutputProofForcedFalseOnFailure", "readinessFailureCannotClaimAudibleOutput"},
        label="readinessFailurePolicy",
    )
    for key in failure_policy:
        require_true(failure_policy, key, label="readinessFailurePolicy")

    claim_boundary = str(payload.get("claimBoundary", "")).lower()
    require("not runtime audible-output proof" in claim_boundary, "Private pre-arm readiness claim boundary must preserve the non-claim.")
    return {
        "schemaVersion": PREARM_SCHEMA,
        "status": PREARM_ACCEPTED_STATUS,
        "runtimeAudibleOutputProof": False,
        "liveArmAllowedByPrearm": True,
        "resourceLeaseCount": len(REQUIRED_RESOURCE_LEASES),
    }


def validate_live_stage_cdb_cleanup(stage: StagePaths) -> None:
    if stage.role not in CDB_STAGE_ROLES:
        return
    payload = read_json(stage.live_json)
    launch = nested_dict(payload.get("launch"), label=f"{stage.role} launch")
    launch_process_id = positive_int(launch.get("processId"), label=f"{stage.role} launch.processId")
    cdb = nested_dict(payload.get("cdbObserver"), label=f"{stage.role} cdbObserver")
    require(cdb.get("enabled") is True, f"{stage.role} CDB observer must be enabled.")
    result = nested_dict(cdb.get("result"), label=f"{stage.role} cdbObserver.result")
    result_status = str(result.get("status", ""))
    require(result_status.lower() == "attached", f"{stage.role} CDB observer result was not attached: {result_status}")
    target_process_id = positive_int(result.get("targetProcessId"), label=f"{stage.role} cdbObserver.result.targetProcessId")
    require(
        target_process_id == launch_process_id,
        f"{stage.role} CDB target process id mismatch: {target_process_id} != {launch_process_id}",
    )
    result_cdb_process_id = positive_int(result.get("cdbProcessId"), label=f"{stage.role} cdbObserver.result.cdbProcessId")
    cleanup = nested_dict(cdb.get("cleanup"), label=f"{stage.role} cdbObserver.cleanup")
    cleanup_status = str(cleanup.get("status", ""))
    require(
        cleanup_status in CDB_CLEANUP_ACCEPTED_STATUSES,
        f"{stage.role} CDB cleanup status is not safe: {cleanup_status}",
    )
    cleanup_cdb_process_id = positive_int(cleanup.get("cdbProcessId"), label=f"{stage.role} cdbObserver.cleanup.cdbProcessId")
    require(
        cleanup_cdb_process_id == result_cdb_process_id,
        f"{stage.role} CDB cleanup process id mismatch: {cleanup_cdb_process_id} != {result_cdb_process_id}",
    )


def run_ambient_stage(layout: BundleLayout, *, source_root: Path, audio_duration_ms: int, log_root: Path) -> None:
    stage = layout.stage("ambientNoBea")
    stage.audio_root.mkdir(parents=True, exist_ok=True)
    census_process, census_stdout, census_stderr = start_command(
        ambient_census_command(stage, observe_ms=audio_duration_ms + AUDIO_CAPTURE_STARTUP_MARGIN_MS),
        log_root=log_root,
        label="ambient-census",
    )
    time.sleep(0.25)
    try:
        run_command(audio_capture_command(stage, duration_ms=audio_duration_ms, source_root=source_root), log_root=log_root, label="ambient-audio", timeout_seconds=(audio_duration_ms // 1000) + 30)
    finally:
        wait_process(census_process, census_stdout, census_stderr, label="ambient-census", timeout_seconds=(audio_duration_ms // 1000) + 30)


def run_live_audio_stage(
    layout: BundleLayout,
    role: str,
    *,
    source_root: Path,
    audio_duration_ms: int,
    live_timeout_seconds: int,
    log_root: Path,
) -> None:
    stage = layout.stage(role)
    stage.audio_root.mkdir(parents=True, exist_ok=True)
    if role in {"cleanBaseline", "muteControl"}:
        run_command(source_snapshot_command(stage, source_root=source_root), log_root=log_root, label=f"{role}-source-snapshot")
    audio_process, audio_stdout, audio_stderr = start_command(
        audio_capture_command(stage, duration_ms=audio_duration_ms, source_root=source_root),
        log_root=log_root,
        label=f"{role}-audio",
    )
    tailer = CdbLogTailer(raw_cdb_log=stage.raw_cdb_log, role=role) if role in {"cleanBaseline", "stagedPositive"} else None
    if tailer is not None:
        tailer.start()
    try:
        time.sleep(AUDIO_CAPTURE_STARTUP_MARGIN_MS / 1000.0)
        run_command(
            live_smoke_command(layout, role, source_root=source_root, timeout_seconds=live_timeout_seconds),
            log_root=log_root,
            label=f"{role}-live",
            timeout_seconds=live_timeout_seconds + 90,
        )
    finally:
        try:
            if tailer is not None:
                tailer.stop_and_write(stage.cdb_observation_ledger)
        finally:
            wait_process(audio_process, audio_stdout, audio_stderr, label=f"{role}-audio", timeout_seconds=(audio_duration_ms // 1000) + 30)
    if role in {"cleanBaseline", "stagedPositive"}:
        validate_live_stage_cdb_cleanup(stage)
        ensure_no_bea_or_cdb_processes()
        run_command(timestamped_log_command(stage), log_root=log_root, label=f"{role}-timestamped-cdb")
        run_command(timeline_command(stage), log_root=log_root, label=f"{role}-timeline")
    if role in {"cleanBaseline", "muteControl"}:
        run_command(source_safety_command(stage, source_root=source_root), log_root=log_root, label=f"{role}-source-safety")


def materialize_attempt(layout: BundleLayout, *, source_root: Path, log_root: Path) -> dict[str, Any]:
    run_command(capture_source_correlation_command(layout, source_root=source_root), log_root=log_root, label="capture-source-correlation", timeout_seconds=120)
    run_command(materializer_command(layout), log_root=log_root, label="materializer", timeout_seconds=60)
    result = run_command(checker_command(layout), log_root=log_root, label="final-checker", timeout_seconds=30)
    return json.loads(result.stdout)


def run_live_bundle(
    *,
    layout: BundleLayout,
    source_root: Path,
    audio_duration_ms: int,
    live_timeout_seconds: int,
) -> dict[str, Any]:
    log_root = layout.root / "executor-logs"
    validate_roots(layout, source_root)
    started_at = dt.datetime.now(dt.timezone.utc)
    receipt: dict[str, Any] = {
        "schemaVersion": "winui-safe-copy-music-audible-output-live-bundle-attempt.v1",
        "startedAtUtc": format_utc(started_at),
        "runtimeAudibleOutputProof": False,
        "artifactRoot": str(layout.root),
        "claimBoundary": "Private live raw-bundle attempt receipt. Final audible proof requires materializer and checker acceptance.",
    }
    final_process_check_error: str | None = None
    failure_process_cleanup: dict[str, Any] | None = None
    failure_process_cleanup_error: str | None = None
    try:
        ensure_no_bea_or_cdb_processes()
        run_ambient_stage(layout, source_root=source_root, audio_duration_ms=audio_duration_ms, log_root=log_root)
        run_live_audio_stage(layout, "cleanBaseline", source_root=source_root, audio_duration_ms=audio_duration_ms, live_timeout_seconds=live_timeout_seconds, log_root=log_root)
        run_live_audio_stage(layout, "stagedPositive", source_root=source_root, audio_duration_ms=audio_duration_ms, live_timeout_seconds=live_timeout_seconds, log_root=log_root)
        run_live_audio_stage(layout, "muteControl", source_root=source_root, audio_duration_ms=audio_duration_ms, live_timeout_seconds=live_timeout_seconds, log_root=log_root)
        summary = materialize_attempt(layout, source_root=source_root, log_root=log_root)
        ensure_no_bea_or_cdb_processes()
        receipt.update(
            {
                "status": "accepted",
                "finishedAtUtc": format_utc(dt.datetime.now(dt.timezone.utc)),
                "runtimeAudibleOutputProof": bool(summary.get("runtimeAudibleOutputProof")),
                "finalProof": str(layout.final_proof),
                "summary": summary,
            }
        )
    except Exception as exc:
        try:
            failure_process_cleanup = cleanup_attempt_owned_processes(layout)
        except Exception as cleanup_exc:  # noqa: BLE001 - keep original failure primary in receipt.
            failure_process_cleanup_error = materializer.sanitize_error_message(str(cleanup_exc))
        try:
            ensure_no_bea_or_cdb_processes()
        except Exception as cleanup_exc:  # noqa: BLE001 - keep original failure primary in receipt.
            final_process_check_error = materializer.sanitize_error_message(str(cleanup_exc))
        receipt.update(
            {
                "status": "failed",
                "finishedAtUtc": format_utc(dt.datetime.now(dt.timezone.utc)),
                "runtimeAudibleOutputProof": False,
                "error": materializer.sanitize_error_message(str(exc)),
            }
        )
        if final_process_check_error:
            receipt["finalProcessCheckError"] = final_process_check_error
        if failure_process_cleanup is not None:
            receipt["failureProcessCleanup"] = failure_process_cleanup
        if failure_process_cleanup_error:
            receipt["failureProcessCleanupError"] = failure_process_cleanup_error
        write_json(layout.receipt, receipt)
        raise
    write_json(layout.receipt, receipt)
    return receipt


def self_test() -> None:
    with tempfile.TemporaryDirectory(prefix="music-live-bundle-executor-") as temp_dir:
        root = Path(temp_dir)
        source_root = root / "source"
        source_root.mkdir()
        layout = build_layout(root / "bundle")
        clean_command = live_smoke_command(layout, "cleanBaseline", source_root=source_root)
        staged_command = live_smoke_command(layout, "stagedPositive", source_root=source_root)
        mute_command = live_smoke_command(layout, "muteControl", source_root=source_root)
        require("--enable-cdb-observer" in clean_command, "clean run must attach CDB.")
        require("--enable-cdb-observer" in staged_command, "staged run must attach CDB.")
        require("--enable-cdb-observer" not in mute_command, "mute run must not attach CDB.")
        require("--stage-music-replacement" in staged_command, "staged run must stage music replacement.")
        require("--launch-nomusic" in mute_command, "mute run must be a mute control.")
        raw_log = root / "windbg.log"
        raw_log.write_text(
            "\n".join(line.split(" ", 1)[1] for line in _timestamped_fixture_log().splitlines()) + "\n",
            encoding="utf-8",
        )
        ledger = root / "timestamp-observations.json"
        write_observation_ledger(
            raw_cdb_log=raw_log,
            output=ledger,
            role="cleanBaseline",
            observed_at_start=dt.datetime(2026, 6, 24, 12, 0, 0, tzinfo=dt.timezone.utc),
        )
        timestamped = root / "out" / "windbg.timestamped.log"
        receipt = root / "out" / "receipt.json"
        timestamp_producer.build_timestamped_log_from_paths(
            raw_cdb_log=raw_log,
            observation_ledger=ledger,
            timestamped_log_output=timestamped,
            receipt_output=receipt,
            allowed_output_root=root / "out",
            role="cleanBaseline",
        )
        prearm = root / "prearm.json"
        write_json(
            prearm,
            {
                "schemaVersion": PREARM_SCHEMA,
                "status": PREARM_ACCEPTED_STATUS,
                "runtimeAudibleOutputProof": False,
                "liveArmAllowedByPrearm": True,
                "runtimeProofAuthority": {
                    "explicitRuntimeProofAuthorityRecorded": True,
                    "requiredArmPhrase": ARM_PHRASE,
                },
                "resourceLeases": {lease: True for lease in REQUIRED_RESOURCE_LEASES},
                "processPreflight": {
                    "noPreexistingBeaOrCdb": True,
                    "passiveProcessCensusOnly": True,
                },
                "proofRootPreflight": {
                    "emptyIsolatedPrivateProofRoot": True,
                    "mustNotOverlapReadOnlySourceRoot": True,
                    "localIgnoredRawProofOnly": True,
                },
                "sourceMutationPolicy": {
                    "copiedProfileAndAppOwnedArtifactRootsOnly": True,
                    "installedGameAndOriginalBeaReadOnly": True,
                },
                "captureSpanDecodeWindowPreflight": {
                    "captureStartedUtcStopwatchAlignmentVerified": True,
                    "wavWallClockDurationCoversCdbDecodeWindow": True,
                    "helperAuthoredWallClockPaddingMetadataPresent": True,
                    "capturedBytesPlusSilencePaddingBytesEqualsBytesRecorded": True,
                    "canonicalWavHeaderAndDataFrameConsistencyVerified": True,
                    "outOfRangeDecodeWindowRejectedBeforeProofClaim": True,
                },
                "rawProofPolicy": {
                    "rawProofArtifactsStayLocalIgnored": True,
                    "privatePathsNotForTrackedDocs": True,
                },
                "readinessFailurePolicy": {
                    "runtimeAudibleOutputProofForcedFalseOnFailure": True,
                    "readinessFailureCannotClaimAudibleOutput": True,
                },
                "claimBoundary": "Private pre-arm readiness only; not runtime audible-output proof.",
            },
        )
        validate_private_prearm_readiness(prearm)
        final_check.self_test()


def _timestamped_fixture_log() -> str:
    return "\n".join(
        [
            "2026-06-22T00:00:01.100Z CGame__PlayMusicForCurrentLevel this=008a9a98 level=100 raw=00000064",
            "2026-06-22T00:00:01.200Z CMusic__PlaySelection entry this=00889a48 selection=2 fade=0 playing=0 head=04400000 current=00000000",
            r"2026-06-22T00:00:01.400Z PCPlatform__KickAsyncMusicStreamRead path=data\music\BEA_04(Master).ogg",
            r"2026-06-22T00:00:01.500Z COggFileRead__OpenFileAndPrimeDecoder this=0440a000 path=data\music\BEA_04(Master).ogg",
            "2026-06-22T00:00:01.600Z COggFileRead__ReadDecodedPcm this=0440a000 request=4096 out=04500000 outBytes=0019f4b0",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", type=Path, default=None)
    parser.add_argument("--source-root", type=Path, default=None)
    parser.add_argument("--prearm-readiness-json", type=Path, default=None)
    parser.add_argument("--audio-duration-ms", type=int, default=DEFAULT_LIVE_AUDIO_DURATION_MS)
    parser.add_argument("--live-timeout-seconds", type=int, default=24)
    parser.add_argument("--arm-live-bundle", default="")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    try:
        if args.self_test:
            self_test()
            print("WinUI safe-copy music audible-output live-bundle executor self-test: PASS")
            return 0
        require(args.arm_live_bundle == ARM_PHRASE, f'Refusing live bundle attempt without --arm-live-bundle "{ARM_PHRASE}".')
        require(5000 <= args.audio_duration_ms <= 60000, "--audio-duration-ms must be between 5000 and 60000.")
        validate_live_attempt_audio_duration(args.audio_duration_ms)
        require(5 <= args.live_timeout_seconds <= 120, "--live-timeout-seconds must be between 5 and 120.")
        artifact_root = args.artifact_root
        require(artifact_root is not None, "Provide --artifact-root for a private ignored proof root or use --self-test.")
        require(args.source_root is not None, "Provide --source-root for the read-only copied/source game root or use --self-test.")
        require(
            args.prearm_readiness_json is not None,
            "Provide --prearm-readiness-json for a private accepted pre-arm readiness artifact.",
        )
        validate_private_prearm_readiness(args.prearm_readiness_json)
        receipt = run_live_bundle(
            layout=build_layout(artifact_root),
            source_root=args.source_root.resolve(),
            audio_duration_ms=args.audio_duration_ms,
            live_timeout_seconds=args.live_timeout_seconds,
        )
        print(json.dumps({"receipt": str(build_layout(artifact_root).receipt), "status": receipt["status"], "runtimeAudibleOutputProof": receipt["runtimeAudibleOutputProof"]}, indent=2))
        return 0
    except (LiveBundleError, materializer.MaterializerError, final_check.ProofError, timestamp_producer.TimestampedCdbLogProducerError) as exc:
        print(f"WinUI safe-copy music audible-output live bundle: FAIL: {materializer.sanitize_error_message(str(exc))}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
