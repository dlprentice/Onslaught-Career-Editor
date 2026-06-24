#!/usr/bin/env python3
"""Manage Battle Engine Aquila cardid.txt tweak presets with backup/restore safety."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

BEGIN_MARKER = "// BEGIN OCE_PRESET_MODERN"
END_MARKER = "// END OCE_PRESET_MODERN"
BACKUP_SUFFIX = ".original.backup"


def modern_block() -> str:
    return "\n".join(
        [
            BEGIN_MARKER,
            "// Managed by tools/cardid_preset_manager.py",
            "// Stable companion lane: modern high-quality tweak defaults.",
            "Tweak:GEFORCE_FX_POWER 1",
            "Tweak:SRT_ENABLE 1",
            "Tweak:IMPOSTOR_ENABLE 1",
            "Tweak:LANDSCAPE_LIGHTING 1",
            "Tweak:SNOW_ENABLE 1",
            "Tweak:GEFORCE_PARTICLE_FOG 1",
            END_MARKER,
            "",
        ]
    )


def backup_path(cardid_path: Path) -> Path:
    return Path(str(cardid_path) + BACKUP_SUFFIX)


def replace_or_append_block(text: str, block: str) -> tuple[str, str]:
    start = text.find(BEGIN_MARKER)
    end = text.find(END_MARKER)

    if start != -1 and end != -1 and end > start:
        end_after = end + len(END_MARKER)
        while end_after < len(text) and text[end_after] in "\r\n":
            end_after += 1
        updated = text[:start] + block + text[end_after:]
        return updated, "replaced"

    sep = "" if text.endswith("\n") else "\n"
    updated = text + sep + block
    return updated, "appended"


def run_restore(cardid_path: Path) -> int:
    bkp = backup_path(cardid_path)
    if not bkp.exists():
        print(f"ERROR: Backup not found: {bkp}", file=sys.stderr)
        return 1
    shutil.copy2(bkp, cardid_path)
    print(f"Restore complete: {cardid_path}")
    print(f"Source backup:   {bkp}")
    return 0


def run_apply(cardid_path: Path, output_path: Path | None, dry_run: bool) -> int:
    if not cardid_path.exists():
        print(f"ERROR: Input not found: {cardid_path}", file=sys.stderr)
        return 1

    original = cardid_path.read_text(encoding="utf-8", errors="replace")
    updated, action = replace_or_append_block(original, modern_block())

    changed = updated != original
    target = output_path if output_path else cardid_path

    print(f"Input:     {cardid_path}")
    print(f"Target:    {target}")
    print(f"Preset:    modern")
    print(f"Action:    {action}")
    print(f"Changed:   {'yes' if changed else 'no'}")

    if dry_run:
        print("Dry-run: no files written.")
        return 0

    if not changed:
        print("No write needed: preset block already current.")
        return 0

    if output_path is None:
        bkp = backup_path(cardid_path)
        if not bkp.exists():
            shutil.copy2(cardid_path, bkp)
            print(f"Backup created: {bkp}")
        else:
            print(f"Backup exists:  {bkp}")

    target.write_text(updated, encoding="utf-8")
    print("Write complete.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apply/restore managed cardid.txt presets (stable companion lane)."
    )
    parser.add_argument("--input", type=Path, required=True, help="Path to cardid.txt")
    parser.add_argument(
        "--preset",
        choices=["modern"],
        default="modern",
        help="Preset to apply (default: modern)",
    )
    parser.add_argument("--output", type=Path, help="Write output to a separate file")
    parser.add_argument("--dry-run", action="store_true", help="Report action only; no writes")
    parser.add_argument("--restore", action="store_true", help="Restore --input from .original.backup")
    parser.add_argument("--print-preset", action="store_true", help="Print preset block and exit")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.print_preset:
        print(modern_block(), end="")
        return 0

    if args.restore:
        return run_restore(args.input)

    if args.preset != "modern":
        print(f"ERROR: Unsupported preset: {args.preset}", file=sys.stderr)
        return 1

    return run_apply(args.input, args.output, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
