#!/usr/bin/env python3
"""Validate read-only Ghidra read-back for IScript Goodie state handlers.

The probe consumes ignored decompile output from
``ExportFunctionsByAddressDecompile.java``. It does not launch the game, read or
write BEA.exe directly, mutate Ghidra, or touch save files.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECOMPILE_DIR = (
    ROOT
    / "subagents"
    / "iscript-goodie-state-readback-2026-05-07"
    / "current"
    / "decompile"
)
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "iscript-goodie-state-readback-2026-05-07"
    / "current"
    / "iscript-goodie-state-readback.json"
)

EXPECTED = {
    "set": {
        "path": "00533a70_IScript__SetGoodieState.c",
        "tokens": [
            "IScript__SetGoodieState",
            "&DAT_00662560 + iVar2 * 4",
            "ctx[1]",
            "*ctx",
        ],
    },
    "get": {
        "path": "00533aa0_IScript__GetGoodieState.c",
        "tokens": [
            "IScript__GetGoodieState",
            "(&g_Career_mGoodies)[iVar3 + -1]",
            "OID__AllocObject",
            "*param_3 = puVar2",
        ],
    },
    "index": {
        "path": "index.tsv",
        "tokens": [
            "0x00533a70\tIScript__SetGoodieState",
            "0x00533aa0\tIScript__GetGoodieState",
            "\tOK",
        ],
    },
}


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def build_report(decompile_dir: Path) -> dict[str, object]:
    failures: list[str] = []
    files: dict[str, object] = {}
    for key, spec in EXPECTED.items():
        path = decompile_dir / spec["path"]
        missing_tokens: list[str] = []
        if not path.is_file():
            failures.append(f"missing decompile file: {relative(path)}")
            text = ""
        else:
            text = read_text(path)
            missing_tokens = [token for token in spec["tokens"] if token not in text]
            if missing_tokens:
                failures.append(f"{spec['path']} missing expected token(s)")
        files[key] = {
            "path": relative(path),
            "status": "PASS" if not missing_tokens and path.is_file() else "FAIL",
            "missingTokens": missing_tokens,
        }

    return {
        "schema": "goodies-iscript-readback.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": "PASS" if not failures else "FAIL",
        "decompileDir": relative(decompile_dir),
        "files": files,
        "currentClaims": [
            "Retail IScript__SetGoodieState writes Goodie state through a 1-based script index.",
            "Retail IScript__GetGoodieState reads g_Career_mGoodies[index-1] and returns a scalar script result.",
            "Mission scripts can mutate/read Goodie state independently of the frontend wall coordinate mapper.",
        ],
        "notClaimed": [
            "This probe does not identify any mission script that calls these handlers for Goodies 71-73.",
            "This probe does not launch BEA.exe or prove runtime reachability.",
            "This probe does not mutate the Ghidra project or executable.",
        ],
        "failures": failures,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if expected read-back tokens are missing.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = build_report(args.decompile_dir)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {relative(args.out)}")
    print(
        "IScript Goodie handlers: "
        + ", ".join(f"{key}={value['status']}" for key, value in report["files"].items())
    )
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
