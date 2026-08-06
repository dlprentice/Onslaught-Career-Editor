#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Serial DeepSeek direct OpenCode runs for per-gen review matrix.

Uses opencode.cmd (not Start-Process bare 'opencode' — fails on Windows npm shim).
Variant max only. One process at a time (OpenCode DB lock).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "local-lab" / "per-gen-review-20260805-v1"

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
    # npm global fallback
    npm = Path.home() / "AppData/Roaming/npm/opencode.cmd"
    if npm.is_file():
        return str(npm)
    raise SystemExit("opencode not found on PATH")


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
) -> dict:
    prompt = prompt_file.read_text(encoding="utf-8").strip().replace("\n", " ")
    title = f"per-gen-g{gen:02d}-{job_id}"
    stdout_p = gdir / f"{job_id}-stdout.txt"
    stderr_p = gdir / f"{job_id}-stderr.txt"
    receipt_p = gdir / f"{job_id}-receipt.json"
    (gdir / f"{job_id}-prompt.txt").write_text(prompt + "\n", encoding="utf-8")

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
    print(f"=== START gen{gen:02d} {job_id} {start} ===", flush=True)
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
        stdout_p.write_text((exc.stdout or b"").decode("utf-8", "replace"), encoding="utf-8")
        stderr_p.write_text((exc.stderr or b"").decode("utf-8", "replace"), encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        exit_code = -1
        note = f"ERROR:{type(exc).__name__}:{exc}"
        stdout_p.write_text("", encoding="utf-8")
        stderr_p.write_text(str(exc), encoding="utf-8")

    finish = datetime.now(timezone.utc).isoformat()
    grade = None
    try:
        text = stdout_p.read_text(encoding="utf-8", errors="replace")
        for line in reversed(text.splitlines()):
            if "GRADE:" in line.upper():
                grade = line.strip()
                break
    except Exception:
        pass

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
        "stdout": str(stdout_p),
        "stderr": str(stderr_p),
    }
    receipt_p.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"=== END gen{gen:02d} {job_id} exit={exit_code} {note} grade={grade} ===", flush=True)
    return receipt


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--gens",
        default="9-24",
        help="e.g. 9-12 or 9,10,11 or 24",
    )
    p.add_argument("--timeout-sec", type=int, default=2400)
    p.add_argument("--sleep-sec", type=int, default=3)
    p.add_argument(
        "--jobs",
        default="all",
        help="comma subset of flash-normal,flash-adversarial,pro-normal,pro-adversarial",
    )
    args = p.parse_args(argv)

    # parse gens
    gens: list[int] = []
    for part in args.gens.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            gens.extend(range(int(a), int(b) + 1))
        elif part:
            gens.append(int(part))
    gens = sorted(set(gens))

    want_jobs = {j[0] for j in DEEPSEEK_JOBS}
    if args.jobs != "all":
        want_jobs = {x.strip() for x in args.jobs.split(",") if x.strip()}

    opencode = find_opencode()
    print(f"opencode={opencode}", flush=True)

    all_receipts: list[dict] = []
    for gen in gens:
        gdir = BASE / f"gen{gen:02d}"
        if not gdir.is_dir():
            print(f"SKIP gen{gen:02d} missing scaffold", flush=True)
            continue
        for job_id, model, role, prompt_name in DEEPSEEK_JOBS:
            if job_id not in want_jobs:
                continue
            prompt_file = gdir / prompt_name
            if not prompt_file.is_file():
                print(f"SKIP gen{gen:02d} {job_id} no prompt", flush=True)
                continue
            rec = run_one(
                opencode=opencode,
                gen=gen,
                job_id=job_id,
                model=model,
                role=role,
                prompt_file=prompt_file,
                gdir=gdir,
                timeout_sec=args.timeout_sec,
            )
            all_receipts.append(rec)
            time.sleep(args.sleep_sec)

    out = BASE / "deepseek-serial-receipts.json"
    out.write_text(
        json.dumps(
            {
                "whenUtc": datetime.now(timezone.utc).isoformat(),
                "opencode": opencode,
                "receipts": all_receipts,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print("WROTE", out, "n=", len(all_receipts), flush=True)
    fails = [r for r in all_receipts if r.get("exitCode") != 0]
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
