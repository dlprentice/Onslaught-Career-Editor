#!/usr/bin/env python3
"""
Batch export Battle Engine Aquila LANGUAGE/*.DAT into TSV/JSON plus a merged matrix.

Default output root:
    subagents/language_export_wave1_YYYY-MM-DD
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

import language_dat_decode as langdat


def _dump_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    lines = ["id\thex\tname\taudio\ttext"]
    for row in rows:
        lines.append(
            "{id}\t{hex}\t{name}\t{audio}\t{text}".format(
                id=row["id"],
                hex=row["hex"],
                name=row["name"] or "",
                audio=row["audio"] or "",
                text=str(row["text"]).replace("\t", "\\t").replace("\n", "\\n"),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--language-dir",
        type=Path,
        default=Path("game/data/LANGUAGE"),
        help="Directory containing language DAT files (default: game/data/LANGUAGE)",
    )
    ap.add_argument(
        "--stf",
        type=Path,
        default=Path("game/data/MissionScripts/text/text.stf"),
        help="Optional STF mapping file (default: game/data/MissionScripts/text/text.stf)",
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=Path("subagents") / f"language_export_wave1_{date.today().isoformat()}",
        help="Output directory for TSV/JSON/matrix exports",
    )
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    id_to_name: dict[int, str] = {}
    if args.stf.exists():
        id_to_name = langdat.parse_text_stf(args.stf)

    files = sorted(args.language_dir.glob("*.dat"))
    if not files:
        raise SystemExit(f"no language dat files found under {args.language_dir}")

    merged: dict[int, dict[str, object]] = {}
    language_summary: list[dict[str, object]] = []

    for path in files:
        lang = langdat.parse_lang_dat(path)
        data = path.read_bytes()
        rows = [langdat.entry_record(lang, data, entry, id_to_name=id_to_name) for entry in lang.entries]

        json_payload = {
            "path": str(path),
            "language": path.stem.lower(),
            "size": path.stat().st_size,
            "ver": lang.ver,
            "wide_flag": lang.wide_flag,
            "count": lang.count,
            "uvar7": lang.uvar7,
            "text_pool_off": lang.text_pool_off,
            "audio_pool_off": lang.audio_pool_off,
            "audio_pool_size": lang.audio_pool_size,
            "rows": rows,
        }
        (args.out_dir / f"{path.stem.lower()}.json").write_text(
            json.dumps(json_payload, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        _dump_tsv(args.out_dir / f"{path.stem.lower()}.tsv", rows)

        language_summary.append(
            {
                "language": path.stem.lower(),
                "path": str(path),
                "count": lang.count,
                "audio_named_count": sum(1 for row in rows if row["audio"]),
                "named_count": sum(1 for row in rows if row["name"]),
            }
        )

        for row in rows:
            item = merged.setdefault(
                row["id"],
                {
                    "id": row["id"],
                    "hex": row["hex"],
                    "name": row["name"],
                    "languages": {},
                },
            )
            if item["name"] is None and row["name"] is not None:
                item["name"] = row["name"]
            item["languages"][path.stem.lower()] = {
                "text": row["text"],
                "audio": row["audio"],
            }

    merged_rows = [merged[key] for key in sorted(merged)]
    (args.out_dir / "merged_matrix.json").write_text(
        json.dumps({"rows": merged_rows}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    matrix_lines = ["id\thex\tname\tamerican\tenglish\tfrench\tgerman\titalian\tspanish"]
    for row in merged_rows:
        columns = [str(row["id"]), row["hex"], row["name"] or ""]
        for lang_name in ("american", "english", "french", "german", "italian", "spanish"):
            text = row["languages"].get(lang_name, {}).get("text", "")
            columns.append(str(text).replace("\t", "\\t").replace("\n", "\\n"))
        matrix_lines.append("\t".join(columns))
    (args.out_dir / "merged_matrix.tsv").write_text("\n".join(matrix_lines) + "\n", encoding="utf-8")

    summary = {
        "language_count": len(files),
        "languages": language_summary,
        "merged_row_count": len(merged_rows),
        "stf_names_loaded": len(id_to_name),
    }
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
