#!/usr/bin/env python3
"""Self-tests for ghidra_ground_unit_vehicle_wave392_probe.py."""

from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import ghidra_ground_unit_vehicle_wave392_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_fixture(root: Path, *, overclaim: bool = False) -> argparse.Namespace:
    metadata = root / "metadata.tsv"
    tags = root / "tags.tsv"
    decompile_dir = root / "decompile"
    vtable_types = root / "vtable_types.tsv"
    vtable_slots = root / "vtable_slots.tsv"
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
                "005e32d4\t005e32d0\t00618060\t0x0\t0\t0\t0x0\t0x0\t.?AVCGroundUnit@@\tCGroundUnit",
                "005e297c\t005e2978\t00617ed8\t0x0\t0\t0\t0x0\t0x0\t.?AVCGroundVehicle@@\tCGroundVehicle",
                "005dbd90\t005dbd8c\t00614170\t0x0\t0\t0\t0x0\t0x0\t.?AVCGroundVehicleGuide@@\tCGroundVehicleGuide",
                "005dc35c\t005dc358\t00614b70\t0x0\t0\t0\t0x0\t0x0\t.?AVCMCGroundVehicle@@\tCMCGroundVehicle",
            ]
        )
        + "\n",
    )
    write(
        vtable_slots,
        "\n".join(
            [
                "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\tcontaining_entry\tcontaining_name\tstatus",
                "005e32d4\t9\t005e32f8\t0x0047c730\t0047c730\t0047c730\tCGroundUnit__Init\t0047c730\tCGroundUnit__Init\tOK",
                "005e32d4\t35\t005e3360\t0x0047c8e0\t0047c8e0\t0047c8e0\tCGroundUnit__CreateCollisionSphere\t0047c8e0\tCGroundUnit__CreateCollisionSphere\tOK",
                "005e32d4\t50\t005e339c\t0x0047ce80\t0047ce80\t0047ce80\tCGroundUnit__MarkDestroyedAndResetState\t0047ce80\tCGroundUnit__MarkDestroyedAndResetState\tOK",
                "005e32d4\t66\t005e33dc\t0x0047c970\t0047c970\t0047c970\tCGroundUnit__UpdateLinkedEffectsByHeightClearance\t0047c970\tCGroundUnit__UpdateLinkedEffectsByHeightClearance\tOK",
                "005e297c\t9\t005e29a0\t0x0047cfd0\t0047cfd0\t0047cfd0\tCGroundVehicle__Init\t0047cfd0\tCGroundVehicle__Init\tOK",
                "005e297c\t35\t005e2a08\t0x0047c8e0\t0047c8e0\t0047c8e0\tCGroundUnit__CreateCollisionSphere\t0047c8e0\tCGroundUnit__CreateCollisionSphere\tOK",
                "005dbd90\t1\t005dbd94\t0x0047d650\t0047d650\t0047d650\tCGroundVehicleGuide__ScalarDeletingDestructor\t0047d650\tCGroundVehicleGuide__ScalarDeletingDestructor\tOK",
                "005dc35c\t1\t005dc360\t0x00496a80\t00496a80\t00496a80\tCMCGroundVehicle__ScalarDeletingDestructor\t00496a80\tCMCGroundVehicle__ScalarDeletingDestructor\tOK",
            ]
        )
        + "\n",
    )
    write(
        xrefs,
        "\n".join(
            [
                "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type",
                "0047c730\tCGroundUnit__Init\t0047cff1\t0047cfd0\tCGroundVehicle__Init\tUNCONDITIONAL_CALL",
                "0047d590\tCGroundVehicleGuide__Constructor\t0047d158\t0047cfd0\tCGroundVehicle__Init\tUNCONDITIONAL_CALL",
                "0047d650\tCGroundVehicleGuide__ScalarDeletingDestructor\t005dbd94\t<none>\t<no_function>\tDATA",
                "0047d6d0\tCGroundVehicleGuide__Destructor\t0047d653\t0047d650\tCGroundVehicleGuide__ScalarDeletingDestructor\tUNCONDITIONAL_CALL",
                "00496a50\tCMCGroundVehicle__Constructor\t0047d110\t0047cfd0\tCGroundVehicle__Init\tUNCONDITIONAL_CALL",
                "00496aa0\tCMCGroundVehicle__Destructor\t00496a83\t00496a80\tCMCGroundVehicle__ScalarDeletingDestructor\tUNCONDITIONAL_CALL",
                "0050ed10\tCGroundUnit__Constructor\t0050e02d\t0050df80\tCWorldPhysicsManager__CreateThingByType\tUNCONDITIONAL_CALL",
            ]
        )
        + "\n",
    )
    write(dry_log, "SUMMARY updated=0 skipped=13 renamed=0 would_rename=10 missing=0 bad=0\n")
    write(apply_log, "SUMMARY updated=13 skipped=0 renamed=10 would_rename=0 missing=0 bad=0\n")

    return argparse.Namespace(
        metadata=metadata,
        tags=tags,
        decompile_dir=decompile_dir,
        vtable_types=vtable_types,
        vtable_slots=vtable_slots,
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
    print("PASS ghidra_ground_unit_vehicle_wave392_probe_test: 2/2")
