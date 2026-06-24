#!/usr/bin/env python3
"""Unit tests for Wave468 particle descriptor probe helpers."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_particle_descriptor_wave468_probe as probe


def test_normalize_address() -> None:
    assert probe.normalize_address("004c04c0") == "0x004c04c0"
    assert probe.normalize_address("0x4c04c0") == "0x004c04c0"
    assert probe.normalize_address("<none>") == "<none>"


def test_parse_summary() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "dry.log"
        path.write_text(
            "SUMMARY updated=0 skipped=5 created=0 would_create=0 renamed=0 would_rename=3 missing=0 bad=0\n",
            encoding="utf-8",
        )
        assert probe.parse_summary(path) == probe.EXPECTED_DRY


def test_token_present_compacts_whitespace_and_case() -> None:
    assert probe.token_present("CEngine__UnlinkNodeFromDoublyLinkedList(&DAT_0082b400,\n  (int)this)", "unlinknodefromdoublylinkedlist")
    assert probe.token_present("*(int *)((int)this + 0x54)", "+ 0x54")


def test_read_tsv_unescapes_comments_and_addresses() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "rows.tsv"
        path.write_text(
            "address\tcomment\n004c04c0\tWave468 correction\\nslot\n",
            encoding="utf-8",
        )
        rows = probe.read_tsv(path)
        assert rows[0]["address"] == "0x004c04c0"
        assert rows[0]["comment"] == "Wave468 correction\nslot"


def main() -> int:
    tests = [
        test_normalize_address,
        test_parse_summary,
        test_token_present_compacts_whitespace_and_case,
        test_read_tsv_unescapes_comments_and_addresses,
    ]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
