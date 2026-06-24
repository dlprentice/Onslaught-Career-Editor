#!/usr/bin/env python3
"""Unit checks for the Wave463 particle manager probe helpers."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_particle_manager_wave463_probe as probe


def test_normalize_address() -> None:
    assert probe.normalize_address("004CAE50") == "0x004cae50"
    assert probe.normalize_address("0x4cc850") == "0x004cc850"
    assert probe.normalize_address("<none>") == "<none>"


def test_parse_summary() -> None:
    text = "--- SUMMARY ---\nupdated=17 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0"
    assert probe.parse_summary(text) == {
        "updated": 17,
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
            "004CAE50\t0046CC82\tline one\\nline two\n",
            encoding="utf-8",
        )
        rows = probe.read_tsv(path)
    assert rows == [
        {
            "address": "0x004cae50",
            "from_addr": "0x0046cc82",
            "comment": "line one\nline two",
        }
    ]


def test_target_contract_counts() -> None:
    assert len(probe.TARGETS) == 17
    assert probe.EXPECTED_DRY["skipped"] == 17
    assert probe.EXPECTED_APPLY["updated"] == 17


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
