#!/usr/bin/env python3
"""
Incrementally tail a WinDbg/CDB log file.

This is intended for the server/client-style workflow documented in
`reverse-engineering/binary-analysis/windbg-cdb-runbook.md`.

Example:
    py -3 tools/windbg_tail.py --log C:\\temp\\bea-windbg.log
"""

from __future__ import annotations

import argparse
from pathlib import Path


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", type=Path, required=True, help="WinDbg/CDB server log file to tail")
    ap.add_argument(
        "--cursor",
        type=Path,
        help="Path to the cursor file storing the last-read byte offset (default: <log>.cursor)",
    )
    ap.add_argument(
        "--tail-bytes",
        type=int,
        default=0,
        help="When no cursor exists yet, start from the last N bytes instead of byte 0 (default: 0 = whole file)",
    )
    ap.add_argument("--reset", action="store_true", help="Ignore any saved cursor and start fresh")
    return ap.parse_args()


def read_cursor(path: Path) -> int:
    try:
        return int(path.read_text(encoding="utf-8").strip() or "0")
    except Exception:
        return 0


def main() -> int:
    args = parse_args()
    log_path = args.log
    cursor_path = args.cursor or log_path.with_suffix(log_path.suffix + ".cursor")

    if not log_path.exists():
        raise SystemExit(f"log file does not exist: {log_path}")

    log_size = log_path.stat().st_size
    if args.reset or not cursor_path.exists():
        start = max(log_size - max(args.tail_bytes, 0), 0) if args.tail_bytes > 0 else 0
    else:
        start = read_cursor(cursor_path)
        if start < 0 or start > log_size:
            start = 0

    with log_path.open("rb") as f:
        f.seek(start)
        chunk = f.read()

    cursor_path.write_text(str(log_size), encoding="utf-8")
    print(chunk.decode("utf-8", errors="replace"), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
