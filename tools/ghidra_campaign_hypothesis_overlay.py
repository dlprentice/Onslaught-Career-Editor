#!/usr/bin/env python3
"""Build a clearly noncanonical Ghidra rename overlay from campaign hypotheses."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from collections import Counter
from pathlib import Path


IMAGE_BASE = 0x00400000
FUN_RE = re.compile(r"^FUN_[0-9A-Fa-f]{8}$")
NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_:$@?]{0,255}$")


class OverlayError(RuntimeError):
    pass


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        rows = [line for line in stream if not line.startswith("#")]
    if not rows:
        raise OverlayError(f"empty TSV: {path}")
    return list(csv.DictReader(rows, delimiter="\t"))


def by_entry(rows: list[dict[str, str]], field: str) -> dict[int, dict[str, str]]:
    result: dict[int, dict[str, str]] = {}
    for row in rows:
        value = int(row[field], 16)
        if value in result:
            raise OverlayError(f"duplicate {field}: 0x{value:08x}")
        result[value] = row
    return result


def ghidra_body_digest(ranges_rva: str) -> str:
    encoded: list[str] = []
    previous_end = -1
    for token in ranges_rva.split(";"):
        start_text, end_text = token.split("-", 1)
        start = int(start_text, 16)
        end = int(end_text, 16)
        if start < 0 or end <= start or start < previous_end:
            raise OverlayError(f"invalid body range set: {ranges_rva}")
        previous_end = end
        encoded.append(f"{IMAGE_BASE + start:08x}:{IMAGE_BASE + end - 1:08x};")
    return hashlib.sha256("".join(encoded).encode("ascii")).hexdigest()


def build(
    campaign_path: Path,
    inventory_path: Path,
    output_dir: Path,
    fallback_path: Path | None,
) -> tuple[int, Counter[str], Counter[str]]:
    campaign = by_entry(read_tsv(campaign_path), "entryVa")
    inventory = by_entry(read_tsv(inventory_path), "address")
    fallback = by_entry(read_tsv(fallback_path), "entryVa") if fallback_path else {}

    hypotheses: list[dict[str, str]] = []
    seen_overlay_names: set[str] = set()
    for entry, live in sorted(inventory.items()):
        live_name = live["name"]
        if not FUN_RE.fullmatch(live_name):
            continue
        current = campaign.get(entry)
        if current is None:
            raise OverlayError(f"campaign is missing live FUN_ entry 0x{entry:08x}")
        if int(current["bodyBytes"]) != int(live["bodyBytes"]):
            raise OverlayError(f"body byte count differs at 0x{entry:08x}")
        if ghidra_body_digest(current["bodyRangesRva"]) != live["bodyDigest"].lower():
            raise OverlayError(f"body range identity differs at 0x{entry:08x}")

        source = "GEN19_CURRENT_CAMPAIGN"
        candidate = current["currentName"]
        if FUN_RE.fullmatch(candidate):
            older = fallback.get(entry)
            if older is None or FUN_RE.fullmatch(older["currentName"]):
                candidate = f"Unresolved_{entry:08x}"
                source = "UNRESOLVED_ADDRESS_ONLY"
            else:
                if older["bodyRangesRva"] != current["bodyRangesRva"]:
                    raise OverlayError(f"fallback body identity differs at 0x{entry:08x}")
                candidate = older["currentName"]
                source = "HISTORICAL_CANDIDATE_HYPOTHESIS_ONLY"

        overlay_name = f"HYP__{candidate}"
        if not NAME_RE.fullmatch(overlay_name):
            raise OverlayError(f"invalid overlay name at 0x{entry:08x}: {overlay_name}")
        if overlay_name in seen_overlay_names:
            raise OverlayError(f"duplicate overlay name: {overlay_name}")
        seen_overlay_names.add(overlay_name)
        hypotheses.append(
            {
                "entryVa": f"0x{entry:08x}",
                "liveName": live_name,
                "overlayName": overlay_name,
                "candidateName": candidate,
                "candidateSource": source,
                "nameClass": current["nameClass"],
                "semanticGrade": current["semanticGrade"],
                "resolutionState": current["resolutionState"],
                "understoodTier": current["understoodTier"],
                "reachClass": current["reachClass"],
                "evidenceStates": current["evidenceStates"],
                "cheapestFalsifier": current["cheapestFalsifier"],
                "bodyBytes": current["bodyBytes"],
                "bodyRangesRva": current["bodyRangesRva"],
            }
        )

    if not hypotheses:
        raise OverlayError("inventory contains no literal FUN_* rows")
    output_dir.mkdir(parents=True, exist_ok=False)
    ledger_path = output_dir / "function-hypotheses.tsv"
    fields = list(hypotheses[0])
    with ledger_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(hypotheses)
    with (output_dir / "rename-map.tsv").open("w", encoding="utf-8", newline="") as stream:
        stream.write("# NONCANONICAL hypothesis overlay; never apply to live Ghidra\n")
        for row in hypotheses:
            stream.write(f"{row['entryVa']}\t{row['overlayName']}\n")

    return (
        len(hypotheses),
        Counter(row["nameClass"] for row in hypotheses),
        Counter(row["semanticGrade"] for row in hypotheses),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", required=True, type=Path)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--fallback-campaign", type=Path)
    args = parser.parse_args()
    count, names, grades = build(
        args.campaign.resolve(),
        args.inventory.resolve(),
        args.out,
        args.fallback_campaign.resolve() if args.fallback_campaign else None,
    )
    print(f"HYPOTHESIS_OVERLAY_BUILT rows={count}")
    print("nameClass=" + ",".join(f"{key}:{names[key]}" for key in sorted(names)))
    print("semanticGrade=" + ",".join(f"{key}:{grades[key]}" for key in sorted(grades)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
