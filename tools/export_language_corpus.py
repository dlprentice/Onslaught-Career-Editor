#!/usr/bin/env python3
"""
Batch export Battle Engine Aquila LANGUAGE/*.DAT into TSV/JSON plus a merged matrix.

Default output root:
    .artifacts/language-export/YYYY-MM-DD
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

import language_dat_decode as langdat
from safe_generated_output import SecuredOutputRoot


def _dump_tsv(output: SecuredOutputRoot, path: Path, rows: list[dict[str, object]]) -> None:
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
    output.atomic_write_text(path, "\n".join(lines) + "\n")


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
        default=Path(".artifacts") / "language-export" / date.today().isoformat(),
        help="Output directory for TSV/JSON/matrix exports",
    )
    return ap.parse_args()


def main() -> int:
    args = parse_args()
    language_dir = args.language_dir.resolve(strict=True)
    stf_path = args.stf.resolve(strict=True) if args.stf.exists() else args.stf.resolve()
    out_dir = args.out_dir.resolve()

    id_to_name: dict[int, str] = {}
    if stf_path.exists():
        id_to_name = langdat.parse_text_stf(stf_path)

    files = sorted(language_dir.glob("*.dat"))
    if not files:
        raise SystemExit(f"no language dat files found under {language_dir}")

    merged: dict[int, dict[str, object]] = {}
    language_summary: list[dict[str, object]] = []

    protected_sources = (
        (language_dir, *files, stf_path)
        if stf_path.exists()
        else (language_dir, *files)
    )
    with SecuredOutputRoot(out_dir, protected_sources=protected_sources) as output:
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
            output.atomic_write_text(
                out_dir / f"{path.stem.lower()}.json",
                json.dumps(json_payload, indent=2, ensure_ascii=False),
            )
            _dump_tsv(output, out_dir / f"{path.stem.lower()}.tsv", rows)

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
        output.atomic_write_text(
            out_dir / "merged_matrix.json",
            json.dumps({"rows": merged_rows}, indent=2, ensure_ascii=False),
        )

        matrix_lines = ["id\thex\tname\tamerican\tenglish\tfrench\tgerman\titalian\tspanish"]
        for row in merged_rows:
            columns = [str(row["id"]), row["hex"], row["name"] or ""]
            for lang_name in ("american", "english", "french", "german", "italian", "spanish"):
                text = row["languages"].get(lang_name, {}).get("text", "")
                columns.append(str(text).replace("\t", "\\t").replace("\n", "\\n"))
            matrix_lines.append("\t".join(columns))
        output.atomic_write_text(out_dir / "merged_matrix.tsv", "\n".join(matrix_lines) + "\n")

        summary = {
            "language_count": len(files),
            "languages": language_summary,
            "merged_row_count": len(merged_rows),
            "stf_names_loaded": len(id_to_name),
        }
        output.atomic_write_json(out_dir / "summary.json", summary)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
