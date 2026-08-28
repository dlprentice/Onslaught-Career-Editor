#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Batch function-triage packet exporter (PROGRAM.md P4).

Takes a VA list file and an output directory, invokes headless Ghidra ONCE
(``-readOnly`` against a named project copy or POST backup -- never the live
maintainer project), and emits one JSON packet per VA: decompile, xrefs
(callers/callees), string refs, observed RTTI/vtable evidence, and the
campaign grade joined from the tracked closure TSV when present.

Incremental: a re-run over the same output directory skips packets that
already exist with a matching image hash unless ``--force`` removes them
first. The Ghidra-side script refuses any leftover packet, so the skip
decision belongs here and only here.

Read-only posture:
  * every invocation carries ``-readOnly -noanalysis``
  * the default project location is the verified H: POST backup; passing the
    live maintainer project path is refused unless ``--allow-live-project``
    is explicit (it still runs read-only)
  * outputs go to the caller's directory; the project is never written

Usage:
  py -3 tools/export_packets.py <addresses.txt> <output-dir>
      [--project-root DIR] [--project-name BEA] [--program BEA.exe]
      [--ghidra PATH-to-analyzeHeadless.bat] [--closure-tsv FILE]
      [--force] [--timeout SECONDS] [--dry-run]

Exit codes: 0 packets complete and verify; 1 failure; 2 could not run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

SCHEMA_PACKET = "bea.re.triage-packet.v1"
SCHEMA_READY = "bea.re.triage-ready.v1"
EXPECTED_IMAGE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
DEFAULT_GHIDRA = Path(
    r"D:\ghidra_12.1.2_PUBLIC_20260605\ghidra_12.1.2_PUBLIC\support\analyzeHeadless.bat"
)
DEFAULT_PROJECT_ROOT = Path(r"H:\BEA-Ghidra-Backups\2026-08-17-vftable65-post-live")
DEFAULT_PROJECT_NAME = "BEA"
DEFAULT_PROGRAM = "BEA.exe"
LIVE_PROJECT_ROOT = Path(r"C:\Users\david\Ghidra\Projects")

VA_LINE = re.compile(r"^0x[0-9a-f]{1,16}$", re.IGNORECASE)


class DriverError(RuntimeError):
    """Raised when the run cannot proceed honestly."""


def read_address_list(path: Path) -> list[str]:
    entries: list[str] = []
    for ordinal, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#"):
            continue
        token = trimmed.split("#", 1)[0].strip()
        if not VA_LINE.match(token):
            raise DriverError(f"address line {ordinal} is not a 0x-hex VA: {trimmed!r}")
        canonical = "0x" + token[2:].lower()
        if canonical not in entries:
            entries.append(canonical)
    if not entries:
        raise DriverError(f"address list names no VA: {path}")
    return entries


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def windows_batch_argv(headless: Path, arguments: list[str]) -> list[str]:
    """analyzeHeadless.bat needs cmd.exe; quote exactly, refuse metacharacters."""
    values = [str(headless.resolve()), *map(str, arguments)]
    for value in values:
        if not value or re.search(r"[\x00\r\n\"&|<>^%()!]", value):
            raise DriverError(f"unsafe headless argument: {value!r}")
    return [
        str(Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "cmd.exe"),
        "/d",
        "/s",
        "/c",
        "call " + subprocess.list2cmdline(values),
    ]


def plan(entries: list[str], output_root: Path, image_sha256: str) -> tuple[list[str], list[str]]:
    """Split entries into skips (existing packet with matching image hash) and todo."""
    todo: list[str] = []
    skipped: list[str] = []
    for entry in entries:
        packet = output_root / f"packet-{entry}.json"
        if not packet.is_file():
            todo.append(entry)
            continue
        try:
            body = json.loads(packet.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raise DriverError(
                f"existing packet is unreadable; remove it or use --force: {packet}"
            )
        if body.get("executableSha256") != image_sha256:
            raise DriverError(
                f"existing packet was cut from a different image "
                f"({body.get('executableSha256')}); remove it or use --force: {packet}"
            )
        skipped.append(entry)
    return todo, skipped


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("addresses", type=Path, help="VA list file (0x-hex per line)")
    parser.add_argument("output_dir", type=Path, help="packet output directory")
    parser.add_argument("--project-root", type=Path, default=DEFAULT_PROJECT_ROOT,
                        help="Ghidra project dir holding BEA.gpr (default: D: POST backup)")
    parser.add_argument("--project-name", default=DEFAULT_PROJECT_NAME)
    parser.add_argument("--program", default=DEFAULT_PROGRAM)
    parser.add_argument("--ghidra", type=Path, default=DEFAULT_GHIDRA,
                        help="path to analyzeHeadless.bat")
    parser.add_argument("--closure-tsv", type=Path, default=None,
                        help="campaign closure TSV for grade joins "
                             "(default: the tracked c1-closure TSV when present)")
    parser.add_argument("--force", action="store_true",
                        help="delete matching-image packets for requested VAs first")
    parser.add_argument("--allow-live-project", action="store_true",
                        help="permit pointing at the live maintainer project "
                             "(still read-only)")
    parser.add_argument("--timeout", type=int, default=1800,
                        help="headless timeout seconds (default 1800)")
    parser.add_argument("--dry-run", action="store_true",
                        help="print the planned invocation without running Ghidra")
    args = parser.parse_args(argv)

    try:
        return run(args)
    except DriverError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


def run(args: argparse.Namespace) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "tools" / "ExportTriagePacket.java"

    headless = args.ghidra
    if not headless.is_file():
        raise DriverError(f"analyzeHeadless not found: {headless}")
    project_root = args.project_root
    if not (project_root / f"{args.project_name}.gpr").is_file():
        raise DriverError(f"Ghidra project not found under: {project_root}")
    if not args.allow_live_project:
        try:
            same = project_root.resolve() == LIVE_PROJECT_ROOT.resolve()
        except OSError:
            same = False
        if same:
            raise DriverError(
                "refusing the live maintainer project by default; pass "
                "--allow-live-project to override (the run stays read-only)"
            )

    addresses_path = args.addresses
    if not addresses_path.is_file():
        raise DriverError(f"address list not found: {addresses_path}")
    entries = read_address_list(addresses_path)

    output_root = args.output_dir
    output_root.mkdir(parents=True, exist_ok=True)

    ready_path = output_root / "triage-ready.json"
    manifest_path = output_root / "run-manifest.json"

    closure_tsv = args.closure_tsv
    if closure_tsv is None:
        candidate = (
            repo_root
            / "reverse-engineering"
            / "binary-analysis"
            / "function-c1-closure-2026-08-11.tsv"
        )
        closure_tsv = candidate if candidate.is_file() else None
    elif not closure_tsv.is_file():
        raise DriverError(f"--closure-tsv not found: {closure_tsv}")

    # Incremental skip decision. The Ghidra-side script refuses leftovers, so
    # anything surviving this point must be removed before the invocation.
    if args.force:
        for entry in entries:
            packet = output_root / f"packet-{entry}.json"
            if packet.is_file():
                packet.unlink()
        stale_manifests = [manifest_path, ready_path]
        for stale in stale_manifests:
            if stale.exists():
                raise DriverError(
                    f"--force refuses to delete run bookkeeping; clean it by hand: {stale}"
                )
    todo, skipped = plan(entries, output_root, EXPECTED_IMAGE_SHA256)
    if not todo:
        ready_body = json.loads(ready_path.read_text(encoding="utf-8")) \
            if ready_path.is_file() else None
        if isinstance(ready_body, dict) and ready_body.get("schema") == SCHEMA_READY:
            print(
                f"SKIP all {len(skipped)} requested VAs already have "
                f"{EXPECTED_IMAGE_SHA256[:12]}... packets under {output_root}"
            )
            return 0
        # Packets survive but no READY commit marker: rerun everything fresh.
        for entry in entries:
            (output_root / f"packet-{entry}.json").unlink(missing_ok=True)
        manifest_path.unlink(missing_ok=True)
        todo, skipped = list(entries), []

    if args.dry_run:
        argv_display = windows_batch_argv(
            headless,
            [
                str(project_root),
                args.project_name,
                "-process", args.program,
                "-readOnly", "-noanalysis",
                "-scriptPath", str(script.parent),
                "-postScript", script.name,
                str(addresses_path),
                str(output_root),
                str(ready_path),
                *([str(closure_tsv)] if closure_tsv else []),
            ],
        )[-1]
        print(f"DRY-RUN entries={len(entries)} todo={len(todo)} skipped={len(skipped)}")
        print(f"  {argv_display}")
        return 0

    if not script.is_file():
        raise DriverError(f"Ghidra script missing: {script}")

    # Absolutize everything handed across the process boundary so the
    # headless child's working directory can never reinterpret a relative
    # path differently than the caller meant it.
    addresses_arg = addresses_path.resolve()
    output_arg = output_root.resolve()
    ready_arg = ready_path.resolve()
    closure_arg = closure_tsv.resolve() if closure_tsv else None

    batch_arguments = [
        str(project_root),
        args.project_name,
        "-process", args.program,
        "-readOnly", "-noanalysis",
        "-scriptPath", str(script.parent),
        "-postScript", script.name,
        str(addresses_arg),
        str(output_arg),
        str(ready_arg),
    ]
    if closure_arg:
        batch_arguments.append(str(closure_arg))
    argv = windows_batch_argv(headless, batch_arguments)

    started = time.monotonic()
    completed = subprocess.run(argv, capture_output=True, text=True,
                               timeout=args.timeout)
    elapsed = time.monotonic() - started
    combined = (completed.stdout or "") + (completed.stderr or "")
    for line in combined.splitlines():
        if line.startswith(("TRIAGE_", "INFO  TRIAGE_", "WARN", "ERROR")):
            print(line)
    if completed.returncode != 0:
        tail = "\n".join(combined.splitlines()[-30:])
        raise DriverError(
            f"headless exited {completed.returncode} after {elapsed:.0f}s\n{tail}"
        )
    if "TRIAGE_PACKETS_READY" not in combined:
        raise DriverError("headless finished but emitted no TRIAGE_PACKETS_READY marker")

    # Verify the READY receipt and every packet hash before claiming success.
    if not ready_path.is_file():
        raise DriverError("READY receipt absent after a marker-complete run")
    ready = json.loads(ready_path.read_text(encoding="utf-8"))
    if ready.get("schema") != SCHEMA_READY or ready.get("status") != "READY":
        raise DriverError(f"unexpected READY receipt schema/status: {ready_path}")
    if ready.get("executableSha256") != EXPECTED_IMAGE_SHA256:
        raise DriverError(
            f"READY receipt names image {ready.get('executableSha256')}, expected "
            f"{EXPECTED_IMAGE_SHA256}"
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_packets = manifest.get("packets", {})
    for entry in todo:
        packet = output_root / f"packet-{entry}.json"
        if not packet.is_file():
            raise DriverError(f"promised packet absent: {packet}")
        body = json.loads(packet.read_text(encoding="utf-8"))
        if body.get("schema") != SCHEMA_PACKET:
            raise DriverError(f"unexpected packet schema: {packet}")
        if body.get("executableSha256") != EXPECTED_IMAGE_SHA256:
            raise DriverError(f"packet names a foreign image: {packet}")
        recorded = manifest_packets.get(packet.name, {}).get("sha256")
        actual = sha256_file(packet)
        if recorded != actual:
            raise DriverError(f"manifest hash mismatch for {packet.name}")

    print(
        f"PACKETS_OK wrote={len(todo)} skipped={len(skipped)} "
        f"elapsed={elapsed:.0f}s out={output_root}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
