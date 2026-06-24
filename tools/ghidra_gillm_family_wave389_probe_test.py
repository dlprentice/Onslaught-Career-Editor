#!/usr/bin/env python3
"""Self-tests for ghidra_gillm_family_wave389_probe.py."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import ghidra_gillm_family_wave389_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path, *, overclaim: bool = False) -> argparse.Namespace:
    metadata = root / "metadata.tsv"
    tags = root / "tags.tsv"
    decompile_dir = root / "decompile"
    vtable_types = root / "vtable_types.tsv"
    vtable_slots = root / "vtable_slots.tsv"
    cgillm_vtable_slots = root / "cgillm_vtable_slots.tsv"
    dry_log = root / "dry.log"
    apply_log = root / "apply.log"
    out = root / "out.json"

    metadata_lines = ["address\tname\tsignature\tcomment\tstatus"]
    tags_lines = ["address\tname\ttags\tstatus"]
    for idx, (addr, spec) in enumerate(probe.TARGETS.items()):
        comment_tokens = list(spec["commentTokens"])  # type: ignore[index]
        if overclaim and idx == 0:
            comment_tokens.append("runtime proof")
        comment = " ".join(str(token) for token in comment_tokens)
        metadata_lines.append(f"{addr}\t{spec['name']}\t{spec['signature']}\t{comment}\tOK")
        tags_lines.append(f"{addr}\t{spec['name']}\t{';'.join(spec['tags'])}\tOK")
        decompile = "\n".join(str(token) for token in spec["decompileTokens"])  # type: ignore[index]
        write(decompile_dir / f"{addr[2:]}_{spec['name']}.c", decompile)

    write(metadata, "\n".join(metadata_lines) + "\n")
    write(tags, "\n".join(tags_lines) + "\n")
    write(
        vtable_types,
        "\n".join(
            [
                "vtable\tcol_ptr_slot\tcol_addr\tsignature\toffset\tcd_offset\ttype_desc\tclass_desc\traw_type_name\tdemangled_type_name",
                "005e0b30\t005e0b2c\t006176a0\t0x0\t0\t0\t0x0\t0x0\t.?AVCGillM@@\tCGillM",
                "005dbc74\t005dbc70\t00613fb8\t0x0\t0\t0\t0x0\t0x0\t.?AVCMCGillM@@\tCMCGillM",
                "005dbcb4\t005dbcb0\t00614010\t0x0\t0\t0\t0x0\t0x0\t.?AVCGillMAI@@\tCGillMAI",
                "005d88ec\t005d88e8\t0060c550\t0x0\t0\t0\t0x0\t0x0\t.?AVCMCBattleEngine@@\tCMCBattleEngine",
                "005df890\t005df88c\t00616f58\t0x0\t0\t0\t0x0\t0x0\t.?AVCMCThunderHead@@\tCMCThunderHead",
            ]
        )
        + "\n",
    )
    write(
        cgillm_vtable_slots,
        "\n".join(
            [
                "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\tcontaining_entry\tcontaining_name\tstatus",
                "005e0b30\t9\t005e0b54\t0x004799c0\t004799c0\t004799c0\tCGillM__VFunc09_InitGroundedSpawnState\t004799c0\tCGillM__VFunc09_InitGroundedSpawnState\tOK",
                "005e0b30\t66\t005e0c38\t0x00479d10\t00479d10\t00479d10\tCGillM__UpdateGroundedVerticalDrift\t00479d10\tCGillM__UpdateGroundedVerticalDrift\tOK",
                "005e0b30\t117\t005e0d04\t0x00479a50\t00479a50\t00479a50\tCGillM__InitLegMotion\t00479a50\tCGillM__InitLegMotion\tOK",
                "005e0b30\t118\t005e0d08\t0x00479b60\t00479b60\t00479b60\tCGillM__InitGillMAIComponent\t00479b60\tCGillM__InitGillMAIComponent\tOK",
                "005e0b30\t119\t005e0d0c\t0x00479cb0\t00479cb0\t00479cb0\tCGillM__InitTerrainGuideComponent\t00479cb0\tCGillM__InitTerrainGuideComponent\tOK",
            ]
        )
        + "\n",
    )
    write(
        vtable_slots,
        "\n".join(
            [
                "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\tcontaining_entry\tcontaining_name\tstatus",
                "005dbcb4\t1\t005dbcb8\t0x00479bf0\t00479bf0\t00479bf0\tCGillMAI__ScalarDeletingDestructor\t00479bf0\tCGillMAI__ScalarDeletingDestructor\tOK",
                "005dbc74\t1\t005dbc78\t0x00479b40\t00479b40\t00479b40\tSharedCMCMech__ScalarDeletingDestructor\t00479b40\tSharedCMCMech__ScalarDeletingDestructor\tOK",
                "005d88ec\t1\t005d88f0\t0x00479b40\t00479b40\t00479b40\tSharedCMCMech__ScalarDeletingDestructor\t00479b40\tSharedCMCMech__ScalarDeletingDestructor\tOK",
                "005df890\t1\t005df894\t0x00479b40\t00479b40\t00479b40\tSharedCMCMech__ScalarDeletingDestructor\t00479b40\tSharedCMCMech__ScalarDeletingDestructor\tOK",
            ]
        )
        + "\n",
    )
    write(dry_log, "SUMMARY updated=0 skipped=11 renamed=0 would_rename=10 missing=0 bad=0\n")
    write(apply_log, "SUMMARY updated=11 skipped=0 renamed=10 would_rename=0 missing=0 bad=0\n")

    return argparse.Namespace(
        metadata=metadata,
        tags=tags,
        decompile_dir=decompile_dir,
        vtable_types=vtable_types,
        vtable_slots=vtable_slots,
        cgillm_vtable_slots=cgillm_vtable_slots,
        dry_log=dry_log,
        apply_log=apply_log,
        out=out,
    )


def test_happy_fixture() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp))
        report, status = probe.validate(args)
        assert status == 0, report["failures"]
        assert report["status"] == "PASS"


def test_overclaim_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        args = build_fixture(Path(tmp), overclaim=True)
        report, status = probe.validate(args)
        assert status == 1
        assert any("overclaim" in failure for failure in report["failures"])


if __name__ == "__main__":
    test_happy_fixture()
    test_overclaim_fails()
    print("PASS ghidra_gillm_family_wave389_probe_test: 2/2")
