#!/usr/bin/env python3
"""Self-tests for ghidra_influencemap_wave418_probe.py."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_influencemap_wave418_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def populate_good_fixture(base: Path) -> None:
    write(
        base / "apply_dry.log",
        "SUMMARY updated=0 skipped=13 created=0 would_create=4 renamed=0 would_rename=3 missing=0 bad=0\n",
    )
    write(
        base / "apply_apply.log",
        "SUMMARY updated=17 skipped=0 created=4 would_create=0 renamed=3 would_rename=0 missing=0 bad=0\n",
    )
    rows = []
    for address, expected in probe.TARGETS.items():
        rows.append(
            (
                address,
                str(expected["name"]),
                str(expected["signature"]),
                " ".join(str(token) for token in expected["commentTokens"]),
                "OK",
            )
        )
    write(
        base / "metadata_after.tsv",
        "address\tname\tsignature\tcomment\tstatus\n" + "\n".join("\t".join(row) for row in rows) + "\n",
    )
    tag_lines = ["address\tname\ttags\tstatus"]
    for address, expected in probe.TARGETS.items():
        tags = sorted(probe.COMMON_TAGS | set(expected["tags"]))  # type: ignore[arg-type]
        tag_lines.append(f"{address}\t{expected['name']}\t{';'.join(tags)}\tOK")
    write(base / "tags_after.tsv", "\n".join(tag_lines) + "\n")

    instruction_lines = [
        "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type",
        "0x0048b5f0\t0x0048b5f0\tTARGET\t0\t0x0048b5f0\t0x0048b5f0\tCInfluenceMap__GetTypeName_0048b5f0\tMOV\tEAX, 0x62d658\t\tFALL_THROUGH",
        "0x0048b5f0\t0x0048b5f0\tAFTER\t1\t0x0048b5f5\t0x0048b5f0\tCInfluenceMap__GetTypeName_0048b5f0\tRET\t\t\tTERMINATOR",
        "0x0048b600\t0x0048b600\tTARGET\t0\t0x0048b600\t0x0048b600\tCInfluenceMap__GetTypeId_0048b600\tMOV\tEAX, 0x1e\t\tFALL_THROUGH",
        "0x0048b600\t0x0048b600\tAFTER\t1\t0x0048b605\t0x0048b600\tCInfluenceMap__GetTypeId_0048b600\tRET\t\t\tTERMINATOR",
        "0x0048b610\t0x0048b610\tTARGET\t0\t0x0048b610\t0x0048b610\tCInfluenceMap__GetInfluenceRadius_0048b610\tFLD\tfloat ptr [ECX + 0x94]\t\tFALL_THROUGH",
        "0x0048b610\t0x0048b610\tAFTER\t1\t0x0048b616\t0x0048b610\tCInfluenceMap__GetInfluenceRadius_0048b610\tRET\t\t\tTERMINATOR",
        "0x0048c350\t0x0048c350\tAFTER\t14\t0x0048c36a\t0x0048c350\tCInfluenceMap__DetachNeighborLinks_0048c350\tCALL\t0x004e5bd0\t\tUNCONDITIONAL_CALL",
        "0x0048c350\t0x0048c350\tAFTER\t17\t0x0048c375\t0x0048c350\tCInfluenceMap__DetachNeighborLinks_0048c350\tCALL\t0x00549220\t\tUNCONDITIONAL_CALL",
    ]
    write(base / "instructions_after.tsv", "\n".join(instruction_lines) + "\n")

    vtable_lines = [
        "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\tcontaining_entry\tcontaining_name\tstatus"
    ]
    for (vtable, slot), (pointer, name) in probe.VTABLE_EXPECTED.items():
        vtable_lines.append(f"{vtable}\t{slot}\t0x0\t{pointer}\t{pointer}\t{pointer}\t{name}\t{pointer}\t{name}\tOK")
    write(base / "influencemap_vtable_slots_after.tsv", "\n".join(vtable_lines) + "\n")
    write(base / "string_0062d658.tsv", "input_addr\tmode\tptr_raw\ttarget_addr\tcstring\n0062d658\tdirect\t\t0062d658\tCInfluenceNode\n")
    write(
        base / "decompile_after" / "index.tsv",
        "address\tname\tsignature\tstatus\n"
        + "\n".join(f"{address}\t{expected['name']}\t{expected['signature']}\tOK" for address, expected in probe.TARGETS.items())
        + "\n",
    )


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
        text = text.replace("CInfluenceMap__scalar_deleting_dtor", "CInfluenceMap__ScalarDelete", 1)
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("stale names still present" in failure for failure in failures)


def test_vtable_slot_status_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "influencemap_vtable_slots_after.tsv").read_text(encoding="utf-8")
        text = text.replace("CInfluenceMap__GetTypeName_0048b5f0", "CInfluenceMap__ScalarDelete", 1)
        (base / "influencemap_vtable_slots_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("vtable slot 0x005dc050[7] name mismatch" in failure for failure in failures)


def test_runtime_overclaim_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        text = text.replace("runtime AI behavior remain unproven", "runtime AI behavior proven")
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("overclaim token" in failure for failure in failures)


def main() -> int:
    tests = [
        test_good_fixture_passes,
        test_stale_name_fails,
        test_vtable_slot_status_fails,
        test_runtime_overclaim_fails,
    ]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
