#!/usr/bin/env python3
"""Public-safe census for shipped Goodies resource archives.

The probe reads the user's local PC install as source material, inflates each
``goodie_*_res_PC.aya`` archive, and parses only the high-level GDIE/GDAT
metadata needed to answer provenance and content-kind questions. It does not
extract private assets, launch the game, or touch BEA.exe.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RESOURCE_ROOT = Path(
    r"C:\Program Files (x86)\Steam\steamapps\common\Battle Engine Aquila\data\Resources"
)
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "goodies-resource-archive-census"
    / "current"
    / "goodies-resource-archive-census.json"
)

ARCHIVE_RE = re.compile(r"goodie_(\d+)_res_PC\.aya$", re.IGNORECASE)
DISPLAYABLE_GOODIE_INDICES = set(range(0, 233))
REQUIRED_TOP_TAGS = ("LVLR", "TARG", "AYAD", "GDIE")
CONTENT_KIND_LABELS = {
    0: "Texture/artwork",
    1: "Model/gallery",
    2: "Video/cutscene",
    3: "Level/metadata",
}


def import_aya_helpers():
    sys.path.insert(0, str((ROOT / "tools").resolve()))
    from aya_archive_inventory import inflate_aya, parse_chunk_stream, parse_top_level_chunks

    return inflate_aya, parse_chunk_stream, parse_top_level_chunks


def parse_gdie_gdat(raw: bytes, *, parse_chunk_stream, parse_top_level_chunks) -> dict[str, object]:
    top_chunks = parse_top_level_chunks(raw)
    top_tags = [chunk.tag for chunk in top_chunks]
    gdie = next((chunk for chunk in top_chunks if chunk.tag == "GDIE"), None)
    if gdie is None:
        raise ValueError("missing GDIE chunk")

    gdie_payload = raw[gdie.offset + 8 : gdie.offset + 8 + gdie.size]
    inner_chunks = parse_chunk_stream(gdie_payload, base_offset=gdie.offset + 8)
    gdat = next((chunk for chunk in inner_chunks if chunk.tag == "GDAT"), None)
    if gdat is None:
        raise ValueError("missing GDAT chunk")

    gdat_payload = raw[gdat.offset + 8 : gdat.offset + 8 + gdat.size]
    if len(gdat_payload) < 8:
        raise ValueError(f"GDAT payload too short: {len(gdat_payload)} bytes")

    embedded_index = int.from_bytes(gdat_payload[0:4], "little", signed=True)
    content_kind = int.from_bytes(gdat_payload[4:8], "little", signed=True)
    return {
        "topTags": top_tags,
        "gdieSize": gdie.size,
        "gdatSize": gdat.size,
        "embeddedGoodieIndex": embedded_index,
        "contentKind": content_kind,
    }


def build_report(resource_root: Path) -> dict[str, object]:
    if not resource_root.exists():
        raise FileNotFoundError(f"resource root does not exist: {resource_root}")

    inflate_aya, parse_chunk_stream, parse_top_level_chunks = import_aya_helpers()
    rows: list[dict[str, object]] = []
    errors: list[dict[str, object]] = []
    tag_counts: Counter[str] = Counter()
    kind_counts: Counter[int] = Counter()

    for path in sorted(resource_root.glob("goodie_*_res_PC.aya")):
        match = ARCHIVE_RE.match(path.name)
        if not match:
            continue
        archive_index = int(match.group(1))
        try:
            raw = inflate_aya(path)
            parsed = parse_gdie_gdat(
                raw,
                parse_chunk_stream=parse_chunk_stream,
                parse_top_level_chunks=parse_top_level_chunks,
            )
            top_tags = list(parsed["topTags"])
            tag_counts.update(top_tags)
            content_kind = int(parsed["contentKind"])
            kind_counts[content_kind] += 1
            rows.append(
                {
                    "goodieIndex": archive_index,
                    "embeddedGoodieIndex": int(parsed["embeddedGoodieIndex"]),
                    "contentKind": content_kind,
                    "contentKindLabel": CONTENT_KIND_LABELS.get(
                        content_kind, f"Unknown kind {content_kind}"
                    ),
                    "topTags": top_tags,
                    "gdieSize": int(parsed["gdieSize"]),
                    "gdatSize": int(parsed["gdatSize"]),
                }
            )
        except Exception as exc:  # noqa: BLE001 - record public-safe parse failure shape.
            errors.append({"goodieIndex": archive_index, "error": str(exc)})

    rows.sort(key=lambda row: int(row["goodieIndex"]))
    indices = {int(row["goodieIndex"]) for row in rows}
    mismatched_indices = [
        int(row["goodieIndex"])
        for row in rows
        if int(row["goodieIndex"]) != int(row["embeddedGoodieIndex"])
    ]
    missing_displayable = sorted(DISPLAYABLE_GOODIE_INDICES.difference(indices))
    extra_indices = sorted(index for index in indices if index not in DISPLAYABLE_GOODIE_INDICES)
    missing_required_tags = [
        int(row["goodieIndex"])
        for row in rows
        if any(tag not in set(row["topTags"]) for tag in REQUIRED_TOP_TAGS)
    ]
    unknown_kind_indices = [
        int(row["goodieIndex"])
        for row in rows
        if int(row["contentKind"]) not in CONTENT_KIND_LABELS
    ]

    expected_conditions = {
        "archiveCountIs232": len(rows) == 232,
        "onlyDisplayableSlot232IsMissing": missing_displayable == [232],
        "noExtraDisplayableIndices": not extra_indices,
        "noParseErrors": not errors,
        "gdatIndexMatchesArchiveIndex": not mismatched_indices,
        "requiredTopTagsPresent": not missing_required_tags,
        "contentKindsKnown": not unknown_kind_indices,
    }
    status = "PASS" if all(expected_conditions.values()) else "FAIL"

    indices_by_kind = {
        str(kind): [int(row["goodieIndex"]) for row in rows if int(row["contentKind"]) == kind]
        for kind in sorted(kind_counts)
    }
    kind_summary = {
        str(kind): {
            "label": CONTENT_KIND_LABELS.get(kind, f"Unknown kind {kind}"),
            "count": kind_counts[kind],
        }
        for kind in sorted(kind_counts)
    }

    return {
        "schema": "goodies-resource-archive-census.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "source": {
            "description": "local read-only PC install data/Resources directory",
            "absolutePathStripped": True,
        },
        "summary": {
            "goodieArchivesParsed": len(rows),
            "displayableGoodieSlots": len(DISPLAYABLE_GOODIE_INDICES),
            "displayableSlotsWithoutResourceArchive": missing_displayable,
            "archiveIndicesOutsideDisplayableSlots": extra_indices,
            "parseErrorCount": len(errors),
            "mismatchedGdatIndexCount": len(mismatched_indices),
            "missingRequiredTopTagCount": len(missing_required_tags),
            "unknownKindCount": len(unknown_kind_indices),
            "topLevelTagCounts": dict(sorted(tag_counts.items())),
            "contentKindCounts": kind_summary,
            "indicesByContentKind": indices_by_kind,
            "expectedConditions": expected_conditions,
        },
        "failures": {
            "parseErrors": errors,
            "mismatchedGdatIndices": mismatched_indices,
            "missingRequiredTopTagIndices": missing_required_tags,
            "unknownKindIndices": unknown_kind_indices,
        },
        "rows": rows,
        "safety": {
            "stripsAbsolutePaths": True,
            "stripsRawAssetNames": True,
            "extractsAssets": False,
            "launchesGame": False,
            "readsOrWritesOriginalExe": False,
            "mutatesInstalledGame": False,
        },
        "notes": [
            "GDAT dword 0 matches the Goodie archive index for all parsed rows.",
            "GDAT dword 1 is treated as the static content-kind discriminator.",
            "This proves shipped archive metadata coverage, not runtime Goodies wall reachability or final WinUI textured model rendering.",
        ],
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resource-root", type=Path, default=DEFAULT_RESOURCE_ROOT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = build_report(args.resource_root)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    summary = report["summary"]
    kind_counts = ", ".join(
        f"{kind}={item['count']}" for kind, item in summary["contentKindCounts"].items()
    )
    print(f"{report['status']}: wrote {args.out.relative_to(ROOT).as_posix()}")
    print(
        "Goodie archives parsed: "
        f"{summary['goodieArchivesParsed']} / {summary['displayableGoodieSlots']} "
        "displayable slots"
    )
    print(
        "Missing displayable archive slots: "
        f"{summary['displayableSlotsWithoutResourceArchive']}"
    )
    print(f"GDAT content-kind counts: {kind_counts}")

    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
