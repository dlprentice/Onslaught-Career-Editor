#!/usr/bin/env python3
"""Self-tests for ghidra_initthing_wave419_probe.py."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_initthing_wave419_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def populate_good_fixture(base: Path) -> None:
    write(
        base / "apply_dry.log",
        "SUMMARY updated=0 skipped=4 created=0 would_create=0 renamed=0 would_rename=3 missing=0 bad=0\n",
    )
    write(
        base / "apply_apply.log",
        "SUMMARY updated=4 skipped=0 created=0 would_create=0 renamed=3 would_rename=0 missing=0 bad=0\n",
    )
    metadata_lines = ["address\tname\tsignature\tcomment\tstatus"]
    tag_lines = ["address\tname\ttags\tstatus"]
    for address, expected in probe.TARGETS.items():
        metadata_lines.append(
            "\t".join(
                [
                    address,
                    str(expected["name"]),
                    str(expected["signature"]),
                    " ".join(str(token) for token in expected["commentTokens"]),
                    "OK",
                ]
            )
        )
        tags = sorted(probe.COMMON_TAGS | set(expected["tags"]))  # type: ignore[arg-type]
        tag_lines.append(f"{address}\t{expected['name']}\t{';'.join(tags)}\tOK")
        clean = address.replace("0x", "")
        write(
            base / "decompile_after" / f"{clean}_{expected['name']}.c",
            " ".join(str(token) for token in expected["decompileTokens"]),
        )
    write(base / "metadata_after.tsv", "\n".join(metadata_lines) + "\n")
    write(base / "tags_after.tsv", "\n".join(tag_lines) + "\n")

    vtable_lines = [
        "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\tcontaining_entry\tcontaining_name\tstatus"
    ]
    for (vtable, slot), (pointer, name) in probe.VTABLE_EXPECTED.items():
        vtable_lines.append(f"{vtable}\t{slot}\t0x0\t{pointer}\t{pointer}\t{pointer}\t{name}\t{pointer}\t{name}\tOK")
    write(base / "vtable_slots_after.tsv", "\n".join(vtable_lines) + "\n")


def test_good_fixture_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        assert probe.check_targets(base) == []


def test_stale_name_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        text = text.replace("CInitThing__CopyFrom", "VFuncSlot_00_0040e1b0", 1)
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("stale names still present" in failure for failure in failures)


def test_vtable_slot_name_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "vtable_slots_after.tsv").read_text(encoding="utf-8")
        text = text.replace("CSquadInitThing__LoadFromMemBuffer", "CSquadInitThing__VFunc_01_0048d8d0", 1)
        (base / "vtable_slots_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("vtable slot 0x005dc1b0[1] name mismatch" in failure for failure in failures)


def test_runtime_overclaim_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        text = text.replace("runtime level-load behavior remains unproven", "runtime level-load behavior proven")
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("overclaim token" in failure for failure in failures)


def main() -> int:
    tests = [
        test_good_fixture_passes,
        test_stale_name_fails,
        test_vtable_slot_name_fails,
        test_runtime_overclaim_fails,
    ]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
