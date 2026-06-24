#!/usr/bin/env python3
"""Unit checks for the Wave462 particle sprite/render probe helpers."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_particle_sprite_render_wave462_probe as probe


def test_normalize_address() -> None:
    assert probe.normalize_address("004C0940") == "0x004c0940"
    assert probe.normalize_address("0x4cac80") == "0x004cac80"
    assert probe.normalize_address("<none>") == "<none>"


def test_parse_summary() -> None:
    text = "INFO SUMMARY updated=14 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0"
    assert probe.parse_summary(text) == {
        "updated": 14,
        "skipped": 0,
        "created": 0,
        "would_create": 0,
        "renamed": 0,
        "would_rename": 0,
        "missing": 0,
        "bad": 0,
    }


def test_read_tsv_normalizes_addresses_and_comments() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "sample.tsv"
        path.write_text(
            "address\tfrom_addr\tcomment\n"
            "004C0940\t004C0770\tline one\\nline two\n",
            encoding="utf-8",
        )
        rows = probe.read_tsv(path)
    assert rows == [
        {
            "address": "0x004c0940",
            "from_addr": "0x004c0770",
            "comment": "line one\nline two",
        }
    ]


def test_target_contract_counts() -> None:
    assert len(probe.TARGETS) == 14
    assert probe.EXPECTED_DRY["skipped"] == 14
    assert probe.EXPECTED_APPLY["updated"] == 14


def main() -> int:
    tests = [
        test_normalize_address,
        test_parse_summary,
        test_read_tsv_normalizes_addresses_and_comments,
        test_target_contract_counts,
    ]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
