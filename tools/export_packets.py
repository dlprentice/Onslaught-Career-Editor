#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Batch function-triage packet exporter (PROGRAM.md P4).

Takes a VA list file and an output directory, invokes headless Ghidra ONCE
(``-readOnly`` against a named project copy or POST backup -- never the live
maintainer project), and emits one JSON packet per VA: decompile, xrefs
(callers/callees), string refs, observed RTTI/vtable evidence, and the
campaign grade joined from the tracked closure TSV when present.

Incremental: a re-run over the same output directory skips packets that
already belong to a verified matching-image run. ``--force`` replaces requested
packets only after the new export verifies. The Ghidra-side script refuses any leftover packet, so the skip
decision belongs here and only here.

Read-only posture:
  * every invocation carries ``-readOnly -noanalysis``
  * every current run must explicitly name its prepared project copy and
    headless Ghidra executable; no historical drive letter is a live default
  * passing the historical live maintainer project path is refused unless
    ``--allow-live-project`` is explicit (it still runs read-only)
  * outputs go to the caller's directory; the project is never written

Usage:
  python ./tools/export_packets.py <addresses.txt> <output-dir>
      --project-root DIR --ghidra PATH-to-analyzeHeadless
      [--project-name BEA] [--program BEA.exe] [--closure-tsv FILE]
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
import shlex
import tempfile
import shutil
import sys
import time
from pathlib import Path

SCHEMA_PACKET = "bea.re.triage-packet.v1"
SCHEMA_READY = "bea.re.triage-ready.v1"
EXPECTED_IMAGE_SHA256 = (
    "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
)
DEFAULT_PROJECT_NAME = "BEA"
DEFAULT_PROGRAM = "BEA.exe"
# This literal remains only as a safety fence for the retired Windows topology.
# It is not a current project default or a route to a Linux mutable authority.
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
            body = read_object(packet)
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
    parser.add_argument(
        "--project-root",
        type=Path,
        required=True,
        help="explicit prepared Ghidra project directory holding BEA.gpr",
    )
    parser.add_argument("--project-name", default=DEFAULT_PROJECT_NAME)
    parser.add_argument("--program", default=DEFAULT_PROGRAM)
    parser.add_argument(
        "--ghidra",
        type=Path,
        required=True,
        help="explicit native analyzeHeadless or Windows analyzeHeadless.bat path",
    )
    parser.add_argument("--closure-tsv", type=Path, default=None,
                        help="campaign closure TSV for grade joins "
                             "(default: the tracked c1-closure TSV when present)")
    parser.add_argument("--force", action="store_true",
                        help="replace requested packets after verified export; refuses existing run bookkeeping")
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


def headless_argv(headless: Path, arguments: list[str]) -> list[str]:
    """Use native argv on Linux; retain the guarded Windows batch launcher."""
    if headless.suffix.lower() in {".bat", ".cmd"}:
        if os.name != "nt":
            raise DriverError("Windows batch launcher cannot run here; select native analyzeHeadless")
        return windows_batch_argv(headless, arguments)
    if os.name != "nt" and not os.access(headless, os.X_OK):
        raise DriverError(f"native analyzeHeadless is not executable: {headless}")
    return [str(headless.resolve()), *arguments]


def read_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise DriverError(f"expected a JSON object: {path}")
    return value


def verified_run(output_root: Path) -> tuple[dict, dict]:
    """Verify the commit marker, manifest and every packet before reuse."""
    ready = read_object(output_root / "triage-ready.json")
    manifest_path = output_root / "run-manifest.json"
    manifest = read_object(manifest_path)
    if (ready.get("schema") != SCHEMA_READY or ready.get("status") != "READY"
            or ready.get("executableSha256") != EXPECTED_IMAGE_SHA256):
        raise DriverError("unexpected READY receipt schema/status/image")
    if (manifest.get("schema") != "bea.re.triage-run-manifest.v1"
            or manifest.get("executableSha256") != EXPECTED_IMAGE_SHA256):
        raise DriverError("unexpected run manifest schema/image")
    ready_manifest = ready.get("manifest")
    if not isinstance(ready_manifest, dict) or ready_manifest.get("sha256") != sha256_file(manifest_path):
        raise DriverError("READY manifest hash mismatch")
    packets = manifest.get("packets")
    if not isinstance(packets, dict) or not packets:
        raise DriverError("run manifest contains no packet map")
    if any(record.get("packetsWritten") != len(packets) for record in (ready, manifest)):
        raise DriverError("run receipt packet count mismatch")
    for name, record in packets.items():
        if not re.fullmatch(r"packet-0x[0-9a-f]{1,16}\.json", name):
            raise DriverError(f"invalid manifest packet name: {name!r}")
        packet = output_root / name
        if packet.is_symlink() or not packet.is_file():
            raise DriverError(f"promised plain packet absent: {packet}")
        if not isinstance(record, dict) or record.get("sha256") != sha256_file(packet):
            raise DriverError(f"manifest hash mismatch for {name}")
        body = read_object(packet)
        if (body.get("schema") != SCHEMA_PACKET
                or body.get("executableSha256") != EXPECTED_IMAGE_SHA256
                or body.get("requestedVa") != name[7:-5]):
            raise DriverError(f"packet identity/schema mismatch: {packet}")
    return ready, manifest


def run(args: argparse.Namespace) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "tools" / "ExportTriagePacket.java"
    headless = args.ghidra.resolve()
    if not headless.is_file():
        raise DriverError(f"analyzeHeadless not found: {headless}")
    project_root = args.project_root.resolve()
    project_file = project_root / f"{args.project_name}.gpr"
    if not project_file.is_file():
        raise DriverError(f"Ghidra project not found under: {project_root}")
    canonical = Path("/home/xsniper80/Projects/game-dev/Onslaught-Career-Editor")
    checkpoint = canonical / "reverse-engineering/ghidra/BEA.gpr"
    working = canonical / "local-lab/ghidra-projects/BEA/BEA.gpr"
    if checkpoint.is_file() and project_file.samefile(checkpoint):
        raise DriverError("refusing the reviewed checkpoint; use a prepared disposable project copy")
    live = (project_root == LIVE_PROJECT_ROOT.resolve()
            or (working.is_file() and project_file.samefile(working)))
    if live and not args.allow_live_project:
        raise DriverError("refusing the live maintainer project by default; pass "
                          "--allow-live-project to override (the run stays read-only)")
    if not script.is_file():
        raise DriverError(f"Ghidra script missing: {script}")
    addresses_path = args.addresses.resolve()
    if not addresses_path.is_file():
        raise DriverError(f"address list not found: {addresses_path}")
    entries = read_address_list(addresses_path)
    if args.timeout <= 0:
        raise DriverError("timeout must be positive")
    output_root = args.output_dir.absolute()
    if output_root.is_symlink() or (output_root.exists() and not output_root.is_dir()):
        raise DriverError(f"output must be a plain directory: {output_root}")
    if (output_root.resolve().is_relative_to(project_root)
            or any(parent.exists() and parent.samefile(project_root)
                   for parent in (output_root, *output_root.parents))):
        raise DriverError("packet output must be outside the Ghidra project directory")
    ready_path = output_root / "triage-ready.json"
    manifest_path = output_root / "run-manifest.json"
    touched = [ready_path, manifest_path, *(output_root / f"packet-{v}.json" for v in entries)]
    for path in touched:
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise DriverError(f"output is not a plain file: {path}")
    # Finish every refusal before mkdir, deletion, replacement or a process launch.
    if args.force and any(p.exists() for p in (manifest_path, ready_path)):
        raise DriverError("--force refuses to delete run bookkeeping; preserve it and use a fresh directory")
    closure_tsv = args.closure_tsv
    if closure_tsv is None:
        candidate = repo_root / "reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv"
        closure_tsv = candidate if candidate.is_file() else None
    elif not closure_tsv.is_file():
        raise DriverError(f"--closure-tsv not found: {closure_tsv}")
    closure_tsv = closure_tsv.resolve() if closure_tsv else None
    prior_manifest = None
    if ready_path.is_file():
        _, prior_manifest = verified_run(output_root)
        closure_hash = sha256_file(closure_tsv) if closure_tsv else None
        if prior_manifest.get("campaignGradesSha256") != closure_hash:
            raise DriverError("closure provenance differs from the committed run; use a fresh output directory")
    elif manifest_path.exists():
        raise DriverError("incomplete run bookkeeping; preserve it and use a fresh output directory")
    if args.force:
        todo, skipped = list(entries), []
    else:
        todo, skipped = plan(entries, output_root, EXPECTED_IMAGE_SHA256)
        if prior_manifest:
            uncommitted = [v for v in skipped if f"packet-{v}.json" not in prior_manifest["packets"]]
        else:
            uncommitted = list(skipped)
        if uncommitted:
            # An image field proves neither run membership nor permission to
            # replace a packet that may hold distinct retained evidence.
            raise DriverError("unregistered packet already exists; preserve it and use a fresh output directory "
                              "or explicitly --force a directory without run bookkeeping")
    def invocation(stage: Path) -> list[str]:
        return headless_argv(headless, [
            str(project_root), args.project_name, "-process", args.program,
            "-readOnly", "-noanalysis", "-scriptPath", str(script.parent),
            "-postScript", script.name, str(stage / "addresses.txt"),
            str(stage / "packets"), str(stage / "packets/triage-ready.json"),
            *([str(closure_tsv)] if closure_tsv else []),
        ])
    # The placeholder describes the staging layout without creating it.
    preview = invocation(output_root / ".triage-preview")
    if args.dry_run:
        print(f"DRY-RUN entries={len(entries)} todo={len(todo)} skipped={len(skipped)}")
        print("  " + shlex.join(preview))
        return 0
    if not todo:
        print(f"SKIP all {len(skipped)} requested VAs already have verified packets under {output_root}")
        return 0
    before = {p: sha256_file(p) if p.exists() else None for p in touched}
    output_root.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=".triage-", dir=output_root))
    staged_output = stage / "packets"
    staged_output.mkdir()
    (stage / "addresses.txt").write_text("\n".join(todo) + "\n", encoding="utf-8")
    started = time.monotonic()
    published: list[Path] = []
    previous = stage / "previous"
    try:
        completed = subprocess.run(invocation(stage), capture_output=True, text=True,
                                   timeout=args.timeout)
        combined = (completed.stdout or "") + (completed.stderr or "")
        for line in combined.splitlines():
            if line.startswith(("TRIAGE_", "INFO  TRIAGE_", "WARN", "ERROR")):
                print(line)
        if completed.returncode != 0 or "TRIAGE_PACKETS_READY" not in combined:
            raise DriverError(f"headless failed or emitted no READY marker (exit {completed.returncode}):\n"
                              + "\n".join(combined.splitlines()[-30:]))
        ready, manifest = verified_run(staged_output)
        expected = {f"packet-{v}.json" for v in todo}
        if set(manifest["packets"]) != expected:
            raise DriverError("exported packet population differs from the requested VAs")
        # Existing evidence remains intact until the complete new export verifies.
        for path, digest in before.items():
            if path.is_symlink() or (sha256_file(path) if path.exists() else None) != digest:
                raise DriverError(f"output changed during export: {path}")
        if prior_manifest:
            _, current_prior = verified_run(output_root)
            if current_prior != prior_manifest:
                raise DriverError("committed run changed during export")
            for field in ("programName", "programMd5", "imageBase", "language", "campaignGradesSha256"):
                if manifest.get(field) != prior_manifest.get(field):
                    raise DriverError(f"export provenance differs from the committed run: {field}")
            manifest["previousManifestSha256"] = before[manifest_path]
            manifest["packets"] = {**prior_manifest["packets"], **manifest["packets"]}
        manifest["requestedAddressList"] = str(addresses_path)
        manifest["packetsWritten"] = len(manifest["packets"])
        new_manifest = staged_output / "run-manifest.json"
        new_manifest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        ready["packetsWritten"] = len(manifest["packets"])
        ready["outputDirName"] = output_root.name
        ready["manifest"] = {"sha256": sha256_file(new_manifest)}
        new_ready = staged_output / "triage-ready.json"
        new_ready.write_text(json.dumps(ready, indent=2) + "\n", encoding="utf-8")
        destinations = [*(output_root / name for name in sorted(expected)), manifest_path, ready_path]
        previous.mkdir()
        for path in destinations:
            if before[path] is not None:
                backup = previous / path.name
                shutil.copy2(path, backup)
                if sha256_file(backup) != before[path]:
                    raise DriverError(f"original changed while preserving publication recovery: {path}")
        # Keep the old bytes recoverable until the complete public set verifies.
        for path in destinations:
            (staged_output / path.name).replace(path)
            published.append(path)
        verified_run(output_root)  # READY was published last.
    except (DriverError, OSError, json.JSONDecodeError, subprocess.TimeoutExpired) as error:
        recovery_errors = []
        for path in published:
            try:
                if before[path] is None:
                    path.unlink()
                else:
                    restore = stage / ("restore-" + path.name)
                    os.link(previous / path.name, restore)
                    os.replace(restore, path)
            except OSError as recovery_error:
                recovery_errors.append(f"{path}: {recovery_error}")
        detail = "\nRecovery needs attention; original bytes remain under previous/: " + "; ".join(recovery_errors) if recovery_errors else ""
        raise DriverError(f"{error}{detail}\nIncomplete export retained for review: {stage}") from error
    else:
        shutil.rmtree(stage)
    print(f"PACKETS_OK wrote={len(todo)} skipped={len(skipped)} "
          f"elapsed={time.monotonic() - started:.0f}s out={output_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
