#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded-parallel Claude Opus 5 headless reviews for per-gen matrix.

Lanes (effort × role):
  opus5-medium-normal / opus5-medium-adversarial  --effort medium

Standing RE uses Opus 5 medium only (FRAGO 2026-08-05 six-way pin; AGENTS.md).
Opus effort max is retired for standing plates — one-off use only with
explicit maintainer re-authorization.

Model: claude-opus-5 via `claude -p`. Read-only intent; no --dangerously-*.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "local-lab" / "per-gen-review-gen26-33-20260805-v1"

CLAUDE_JOBS = [
    ("opus5-medium-normal", "medium", "normal", "PROMPT-NORMAL.txt"),
    ("opus5-medium-adversarial", "medium", "adversarial", "PROMPT-ADVERSARIAL.txt"),
]
# Standing RE uses Opus 5 medium only (FRAGO 2026-08-05 six-way pin; AGENTS.md).
# Opus effort max is retired for standing plates — one-off use only with
# explicit maintainer re-authorization. Do not add max jobs back here.


def find_claude() -> str:
    p = shutil.which("claude") or shutil.which("claude.exe")
    if p:
        return p
    cand = Path.home() / ".local/bin/claude.exe"
    if cand.is_file():
        return str(cand)
    raise SystemExit("claude CLI not found")


def parse_gens(spec: str) -> list[int]:
    gens: list[int] = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            gens.extend(range(int(a), int(b) + 1))
        else:
            gens.append(int(part))
    return sorted(set(gens))


def already_ok(gdir: Path, job_id: str) -> bool:
    rec = gdir / f"{job_id}-receipt.json"
    if not rec.is_file():
        return False
    try:
        data = json.loads(rec.read_text(encoding="utf-8"))
    except Exception:
        return False
    return data.get("exitCode") == 0 and data.get("note") in {"OK", "OK_RETRY"}


def run_one(
    *,
    claude: str,
    gen: int,
    job_id: str,
    effort: str,
    role: str,
    prompt_file: Path,
    gdir: Path,
    timeout_sec: int,
    attempt: int,
) -> dict:
    prompt = prompt_file.read_text(encoding="utf-8").strip()
    stdout_p = gdir / f"{job_id}-stdout.txt"
    stderr_p = gdir / f"{job_id}-stderr.txt"
    receipt_p = gdir / f"{job_id}-receipt.json"
    (gdir / f"{job_id}-prompt.txt").write_text(prompt + "\n", encoding="utf-8")

    start = datetime.now(timezone.utc).isoformat()
    # Headless print mode; tools allowed for read-only inspection.
    cmd = [
        claude,
        "-p",
        prompt,
        "--model",
        "claude-opus-5",
        "--effort",
        effort,
        "--output-format",
        "text",
    ]
    print(f"START gen{gen:02d} {job_id} effort={effort} attempt={attempt}", flush=True)
    try:
        completed = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_sec,
            shell=False,
        )
        exit_code = completed.returncode
        stdout_p.write_text(completed.stdout or "", encoding="utf-8")
        stderr_p.write_text(completed.stderr or "", encoding="utf-8")
        note = "OK" if exit_code == 0 else "FAIL"
    except subprocess.TimeoutExpired as exc:
        exit_code = -1
        note = "TIMEOUT"
        stdout_p.write_text(
            (exc.stdout or b"").decode("utf-8", "replace")
            if isinstance(exc.stdout, (bytes, bytearray))
            else (exc.stdout or ""),
            encoding="utf-8",
        )
        stderr_p.write_text(
            (exc.stderr or b"").decode("utf-8", "replace")
            if isinstance(exc.stderr, (bytes, bytearray))
            else (exc.stderr or ""),
            encoding="utf-8",
        )
    except Exception as exc:  # noqa: BLE001
        exit_code = -1
        note = f"ERROR:{type(exc).__name__}"
        stdout_p.write_text("", encoding="utf-8")
        stderr_p.write_text(str(exc), encoding="utf-8")

    finish = datetime.now(timezone.utc).isoformat()
    grade = None
    try:
        for line in reversed(
            stdout_p.read_text(encoding="utf-8", errors="replace").splitlines()
        ):
            if "GRADE:" in line.upper():
                grade = line.strip()
                break
    except Exception:
        pass
    if attempt > 1 and note == "OK":
        note = "OK_RETRY"
    receipt = {
        "id": job_id,
        "gen": gen,
        "model": "claude-opus-5",
        "effort": effort,
        "role": role,
        "startUtc": start,
        "finishUtc": finish,
        "exitCode": exit_code,
        "note": note,
        "gradeLine": grade,
        "attempt": attempt,
        "stdout": str(stdout_p),
        "stderr": str(stderr_p),
    }
    receipt_p.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(
        f"END gen{gen:02d} {job_id} exit={exit_code} {note} grade={grade}",
        flush=True,
    )
    return receipt


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--gens", default="26-33")
    p.add_argument("--base", type=Path, default=DEFAULT_BASE)
    p.add_argument("--concurrency", type=int, default=2)
    p.add_argument("--timeout-sec", type=int, default=2400)
    p.add_argument("--jobs", default="all")
    p.add_argument("--retries", type=int, default=1)
    p.add_argument("--no-skip-done", action="store_true")
    args = p.parse_args(argv)
    base = args.base if args.base.is_absolute() else ROOT / args.base
    skip_done = not args.no_skip_done
    want = {j[0] for j in CLAUDE_JOBS}
    if args.jobs != "all":
        want = {x.strip() for x in args.jobs.split(",") if x.strip()}
    claude = find_claude()
    print(f"claude={claude} concurrency={args.concurrency} base={base}", flush=True)

    work: list[tuple] = []
    for gen in parse_gens(args.gens):
        gdir = base / f"gen{gen:02d}"
        if not gdir.is_dir():
            print(f"SKIP gen{gen:02d} missing scaffold", flush=True)
            continue
        for job_id, effort, role, prompt_name in CLAUDE_JOBS:
            if job_id not in want:
                continue
            if skip_done and already_ok(gdir, job_id):
                print(f"SKIP gen{gen:02d} {job_id} already OK", flush=True)
                continue
            prompt_file = gdir / prompt_name
            if not prompt_file.is_file():
                print(f"SKIP gen{gen:02d} {job_id} no prompt", flush=True)
                continue
            work.append((gen, job_id, effort, role, prompt_file, gdir))

    print(f"queue={len(work)}", flush=True)
    receipts: list[dict] = []

    def worker(item: tuple) -> dict:
        gen, job_id, effort, role, prompt_file, gdir = item
        last: dict = {}
        for attempt in range(1, args.retries + 2):
            last = run_one(
                claude=claude,
                gen=gen,
                job_id=job_id,
                effort=effort,
                role=role,
                prompt_file=prompt_file,
                gdir=gdir,
                timeout_sec=args.timeout_sec,
                attempt=attempt,
            )
            if last.get("exitCode") == 0:
                return last
            if attempt <= args.retries:
                time.sleep(2 * attempt)
        return last

    with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool:
        futs = [pool.submit(worker, item) for item in work]
        for fut in as_completed(futs):
            receipts.append(fut.result())

    out = base / "claude-opus-parallel-receipts.json"
    out.write_text(
        json.dumps(
            {
                "whenUtc": datetime.now(timezone.utc).isoformat(),
                "base": str(base),
                "concurrency": args.concurrency,
                "receipts": receipts,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    fails = [r for r in receipts if r.get("exitCode") != 0]
    print(f"WROTE {out} n={len(receipts)} fails={len(fails)}", flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
