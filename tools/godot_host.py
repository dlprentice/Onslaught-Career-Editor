#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Owned-process support for the companion's Godot and .NET commands.

companion_godot.py runs its engine and SDK commands through run_process, which stops the whole
process group on timeout or interruption, and reports failures with print_process_output. This
module names no engine version and has no rebuild, retail-data or simulation dependencies.
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path


def _stop_owned_group(process: subprocess.Popen[str]) -> None:
    """Stop descendants too, including children left after the leader exits."""
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        process.wait()
        return
    deadline = time.monotonic() + 0.5
    while time.monotonic() < deadline:
        process.poll()
        try:
            os.killpg(process.pid, 0)
        except ProcessLookupError:
            break
        time.sleep(0.01)
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    process.wait()


def run_process(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: float | None,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run one owned Linux process group; preserve output and nonzero exits."""
    process = subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        start_new_session=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )
    timed_out: subprocess.TimeoutExpired | None = None
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        result = subprocess.CompletedProcess(command, process.returncode, stdout, stderr)
        result.check_returncode()
        return result
    except subprocess.TimeoutExpired as error:
        timed_out = error
        raise
    finally:
        try:
            # Also clean up an engine/build tool which exits but leaves workers alive.
            _stop_owned_group(process)
            if timed_out is not None and capture:
                try:
                    stdout, stderr = process.communicate(timeout=1.0)
                except subprocess.TimeoutExpired as drain_error:
                    # An escaped descendant may still hold a pipe. Keep the
                    # latest partial output without turning this into a hang.
                    if drain_error.output is not None:
                        timed_out.output = drain_error.output
                    if drain_error.stderr is not None:
                        timed_out.stderr = drain_error.stderr
                    timed_out.add_note("Owned process group stopped; output drain exceeded one second.")
                except UnicodeError:
                    # Preserve the original byte diagnostics and timeout even
                    # when a tool's final output is not valid text.
                    timed_out.add_note("Owned process group stopped; final output could not be decoded.")
                else:
                    # communicate() normalizes text; TimeoutExpired diagnostics
                    # remain bytes, as in subprocess's public exception contract.
                    encoding = process.encoding or "utf-8"
                    timed_out.output = stdout.encode(encoding) if stdout is not None else None
                    timed_out.stderr = stderr.encode(encoding) if stderr is not None else None
        finally:
            for stream in (process.stdout, process.stderr):
                if stream is not None:
                    stream.close()


def print_process_output(error: subprocess.CalledProcessError | subprocess.TimeoutExpired) -> None:
    """Print captured diagnostics without byte-literal reprs or lost partial lines."""
    for output in (error.output, error.stderr):
        if output:
            text = output.decode("utf-8", errors="replace") if isinstance(output, bytes) else output
            print(text, file=sys.stderr, end="" if text.endswith("\n") else "\n")
    for note in getattr(error, "__notes__", ()):
        print(note, file=sys.stderr)
