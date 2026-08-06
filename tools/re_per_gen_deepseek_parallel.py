#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bounded-parallel DeepSeek OpenCode runs for per-gen review matrix.

Default concurrency=4 (remeasured OK on shared opencode.db 2026-08-05).
On exit!=0 or lock-ish stderr, retry the cell once. Optional --isolate-data
uses per-job XDG_DATA_HOME + copied auth.json to avoid shared-DB contention.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "local-lab" / "per-gen-review-20260805-v1"
AUTH = Path.home() / ".local/share/opencode/auth.json"

DEEPSEEK_JOBS = [
    ("flash-normal", "deepseek/deepseek-v4-flash", "normal", "PROMPT-NORMAL.txt"),
    (
        "flash-adversarial",
        "deepseek/deepseek-v4-flash",
        "adversarial",
        "PROMPT-ADVERSARIAL.txt",
    ),
    ("pro-normal", "deepseek/deepseek-v4-pro", "normal", "PROMPT-NORMAL.txt"),
    (
        "pro-adversarial",
        "deepseek/deepseek-v4-pro",
        "adversarial",
        "PROMPT-ADVERSARIAL.txt",
    ),
]


def find_opencode() -> str:
    for name in ("opencode.cmd", "opencode.exe", "opencode"):
        p = shutil.which(name)
        if p:
            return p
    npm = Path.home() / "AppData/Roaming/npm/opencode.cmd"
    if npm.is_file():
        return str(npm)
    raise SystemExit("opencode not found")


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
    opencode: str,
    gen: int,
    job_id: str,
    model: str,
    role: str,
    prompt_file: Path,
    gdir: Path,
    timeout_sec: int,
    isolate: bool,
    attempt: int,
) -> dict:
    prompt = prompt_file.read_text(encoding="utf-8").strip().replace("\n", " ")
    title = f"per-gen-g{gen:02d}-{job_id}-a{attempt}"
    stdout_p = gdir / f"{job_id}-stdout.txt"
    stderr_p = gdir / f"{job_id}-stderr.txt"
    receipt_p = gdir / f"{job_id}-receipt.json"
    (gdir / f"{job_id}-prompt.txt").write_text(prompt + "\n", encoding="utf-8")

    env = os.environ.copy()
    iso_dir = None
    if isolate:
        iso_dir = Path(tempfile.mkdtemp(prefix=f"oc-iso-g{gen:02d}-{job_id}-"))
        share = iso_dir / ".local" / "share" / "opencode"
        share.mkdir(parents=True, exist_ok=True)
        if AUTH.is_file():
            shutil.copy2(AUTH, share / "auth.json")
        env["XDG_DATA_HOME"] = str(iso_dir / ".local" / "share")
        env["HOME"] = str(iso_dir)

    start = datetime.now(timezone.utc).isoformat()
    cmd = [
        opencode,
        "run",
        "--pure",
        "-m",
        model,
        "--variant",
        "max",
        "--title",
        title,
        "--dir",
        str(ROOT),
        prompt,
    ]
    print(f"START gen{gen:02d} {job_id} attempt={attempt}", flush=True)
    try:
        completed = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_sec,
            env=env,
            shell=False,
        )
        exit_code = completed.returncode
        stdout_p.write_text(completed.stdout or "", encoding="utf-8")
        stderr_p.write_text(completed.stderr or "", encoding="utf-8")
        err = completed.stderr or ""
        locked = "database is locked" in err.lower() or "sqlite_busy" in err.lower()
        note = "OK" if exit_code == 0 else ("LOCK" if locked else "FAIL")
    except subprocess.TimeoutExpired as exc:
        exit_code = -1
        note = "TIMEOUT"
        locked = False
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
        locked = False
        stdout_p.write_text("", encoding="utf-8")
        stderr_p.write_text(str(exc), encoding="utf-8")

    finish = datetime.now(timezone.utc).isoformat()
    grade = None
    try:
        for line in reversed(stdout_p.read_text(encoding="utf-8", errors="replace").splitlines()):
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
        "model": model,
        "variant": "max",
        "role": role,
        "title": title,
        "startUtc": start,
        "finishUtc": finish,
        "exitCode": exit_code,
        "note": note,
        "gradeLine": grade,
        "attempt": attempt,
        "isolate": isolate,
        "stdout": str(stdout_p),
        "stderr": str(stderr_p),
    }
    receipt_p.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(
        f"END gen{gen:02d} {job_id} exit={exit_code} {note} grade={grade}",
        flush=True,
    )
    if iso_dir is not None:
        shutil.rmtree(iso_dir, ignore_errors=True)
    return receipt


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--gens", default="9-24")
    p.add_argument(
        "--base",
        type=Path,
        default=BASE,
        help="per-gen review root containing genNN/ scaffold dirs",
    )
    p.add_argument("--concurrency", type=int, default=4)
    p.add_argument("--timeout-sec", type=int, default=2400)
    p.add_argument(
        "--jobs",
        default="all",
        help="comma subset or all",
    )
    p.add_argument("--isolate-data", action="store_true")
    p.add_argument("--skip-done", action="store_true", default=True)
    p.add_argument("--no-skip-done", action="store_true")
    p.add_argument("--retries", type=int, default=1)
    args = p.parse_args(argv)
    skip_done = not args.no_skip_done
    base = args.base if args.base.is_absolute() else ROOT / args.base

    want = {j[0] for j in DEEPSEEK_JOBS}
    if args.jobs != "all":
        want = {x.strip() for x in args.jobs.split(",") if x.strip()}

    gens = parse_gens(args.gens)
    opencode = find_opencode()
    print(
        f"opencode={opencode} concurrency={args.concurrency} base={base}",
        flush=True,
    )

    work: list[tuple] = []
    for gen in gens:
        gdir = base / f"gen{gen:02d}"
        if not gdir.is_dir():
            print(f"SKIP gen{gen:02d} missing scaffold", flush=True)
            continue
        for job_id, model, role, prompt_name in DEEPSEEK_JOBS:
            if job_id not in want:
                continue
            if skip_done and already_ok(gdir, job_id):
                print(f"SKIP gen{gen:02d} {job_id} already OK", flush=True)
                continue
            prompt_file = gdir / prompt_name
            if not prompt_file.is_file():
                print(f"SKIP gen{gen:02d} {job_id} no prompt", flush=True)
                continue
            work.append((gen, job_id, model, role, prompt_file, gdir))

    print(f"queue={len(work)}", flush=True)
    receipts: list[dict] = []

    def worker(item: tuple) -> dict:
        gen, job_id, model, role, prompt_file, gdir = item
        last: dict = {}
        for attempt in range(1, args.retries + 2):
            last = run_one(
                opencode=opencode,
                gen=gen,
                job_id=job_id,
                model=model,
                role=role,
                prompt_file=prompt_file,
                gdir=gdir,
                timeout_sec=args.timeout_sec,
                isolate=args.isolate_data,
                attempt=attempt,
            )
            if last.get("exitCode") == 0:
                return last
            if last.get("note") not in {"LOCK", "FAIL", "TIMEOUT"} and attempt > 1:
                break
            if attempt <= args.retries:
                time.sleep(2 * attempt)
        return last

    with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool:
        futs = [pool.submit(worker, item) for item in work]
        for fut in as_completed(futs):
            receipts.append(fut.result())

    out = base / "deepseek-parallel-receipts.json"
    out.write_text(
        json.dumps(
            {
                "whenUtc": datetime.now(timezone.utc).isoformat(),
                "base": str(base),
                "concurrency": args.concurrency,
                "isolate": args.isolate_data,
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
