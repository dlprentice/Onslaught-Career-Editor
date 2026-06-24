#!/usr/bin/env python3
"""Self-tests for ghidra_ground_attack_aircraft_wave391_probe.py."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import ghidra_ground_attack_aircraft_wave391_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path, *, overclaim: bool = False) -> argparse.Namespace:
    metadata = root / "metadata.tsv"
    tags = root / "tags.tsv"
    decompile_dir = root / "decompile"
    vtable_types = root / "vtable_types.tsv"
    vtable_slots = root / "vtable_slots.tsv"
    pointer_table = root / "pointer_table.tsv"
    xrefs = root / "xrefs.tsv"
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
                "005dbd4c\t005dbd48\t006140c0\t0x0\t0\t0\t0x0\t0x0\t.?AVCGroundAttackAI@@\tCGroundAttackAI",
                "005dbd20\t005dbd1c\t00614118\t0x0\t0\t0\t0x0\t0x0\t.?AVCGroundAttackGuide@@\tCGroundAttackGuide",
            ]
        )
        + "\n",
    )
    write(
        vtable_slots,
        "\n".join(
            [
                "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\tcontaining_entry\tcontaining_name\tstatus",
                "005dbd4c\t1\t005dbd50\t0x0047bd70\t0047bd70\t0047bd70\tCGroundAttackAI__ScalarDeletingDestructor\t0047bd70\tCGroundAttackAI__ScalarDeletingDestructor\tOK",
                "005dbd20\t1\t005dbd24\t0x0047be30\t0047be30\t0047be30\tCGroundAttackGuide__ScalarDeletingDestructor\t0047be30\tCGroundAttackGuide__ScalarDeletingDestructor\tOK",
            ]
        )
        + "\n",
    )
    write(
        pointer_table,
        "\n".join(
            [
                "slot\tentry_addr\tptr\tptr_name\tptr_signature",
                "0\t005e2bf0\t0047bbf0\tCGroundAttackAircraft__Init\tvoid __thiscall CGroundAttackAircraft__Init(void * this, void * init_data)",
                "50\t005e2cb8\t0047c040\tCGroundAttackAircraft__AdvanceCloseShootAnimationState\tint __fastcall CGroundAttackAircraft__AdvanceCloseShootAnimationState(void * this)",
            ]
        )
        + "\n",
    )
    write(
        xrefs,
        "\n".join(
            [
                "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type",
                "0047bab0\tCGroundAttackAI__InitState\t0047bc92\t0047bbf0\tCGroundAttackAircraft__Init\tUNCONDITIONAL_CALL",
                "0047bd90\tCGroundAttackAI__Destructor\t0047bd73\t0047bd70\tCGroundAttackAI__ScalarDeletingDestructor\tUNCONDITIONAL_CALL",
                "0047be50\tCGroundAttackGuide__Destructor\t0047be33\t0047be30\tCGroundAttackGuide__ScalarDeletingDestructor\tUNCONDITIONAL_CALL",
                "0047bff0\tCGroundAttackAircraft__CloseBay\t0047baee\t0047bab0\tCGroundAttackAI__InitState\tUNCONDITIONAL_CALL",
            ]
        )
        + "\n",
    )
    write(dry_log, "SUMMARY updated=0 skipped=9 renamed=0 would_rename=7 missing=0 bad=0\n")
    write(apply_log, "SUMMARY updated=9 skipped=0 renamed=7 would_rename=0 missing=0 bad=0\n")

    return argparse.Namespace(
        metadata=metadata,
        tags=tags,
        decompile_dir=decompile_dir,
        vtable_types=vtable_types,
        vtable_slots=vtable_slots,
        pointer_table=pointer_table,
        xrefs=xrefs,
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
    print("PASS ghidra_ground_attack_aircraft_wave391_probe_test: 2/2")
