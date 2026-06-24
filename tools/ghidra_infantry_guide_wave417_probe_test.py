#!/usr/bin/env python3
"""Self-tests for ghidra_infantry_guide_wave417_probe.py."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_infantry_guide_wave417_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def populate_good_fixture(base: Path) -> None:
    write(
        base / "apply_dry.log",
        "SUMMARY updated=0 skipped=5 created=0 would_create=2 boundary_moved=0 would_boundary_move=1 renamed=0 would_rename=3 missing=0 bad=0\n",
    )
    write(
        base / "apply_apply.log",
        "SUMMARY updated=7 skipped=0 created=2 would_create=0 boundary_moved=1 would_boundary_move=0 renamed=2 would_rename=0 missing=0 bad=0\n",
    )
    rows = [
        (
            "0x0048a3c0",
            "CInfantryGuide__ctor",
            "void * __thiscall CInfantryGuide__ctor(void * this, void * owner_unit)",
            "Wave417 signature/name hardening: CInfantryGuide constructor calls CGuide__ctor_base with owner_unit, installs vtable 0x005dbfa8, allocates two 0x54 guide buffers, initializes the reader field, schedules event 2000, and keeps runtime guide behavior and rebuild parity remain unproven.",
            "OK",
        ),
        (
            "0x0048a4b0",
            "SharedGuide__GetField24Block_0048a4b0",
            "void * __fastcall SharedGuide__GetField24Block_0048a4b0(void * this)",
            "Wave417 recovered shared guide vtable helper: returns this+0x24 and is referenced by CInfantryGuide and CGroundVehicleGuide vtables. Exact field semantics, runtime guide behavior, and rebuild parity remain unproven.",
            "OK",
        ),
        (
            "0x0048a4c0",
            "CInfantryGuide__scalar_deleting_dtor",
            "void * __thiscall CInfantryGuide__scalar_deleting_dtor(void * this, byte flags)",
            "Wave417 name/signature correction: scalar-deleting destructor wrapper calls CInfantryGuide__dtor, checks flags bit 0, optionally frees through OID__FreeObject, returns this, and keeps runtime cleanup behavior unproven.",
            "OK",
        ),
        (
            "0x0048a4e0",
            "CInfantryGuide__dtor",
            "void __fastcall CInfantryGuide__dtor(void * this)",
            "Wave417 signature/comment hardening: destructor body reached by CInfantryGuide scalar deleting destructor removes the reader link at this+0x44, frees guide buffers +0x3c/+0x34, calls CMonitor__Shutdown, and keeps runtime cleanup behavior unproven.",
            "OK",
        ),
        (
            "0x0048a570",
            "CInfantryGuide__UpdateGuidanceState_0048a570",
            "void __fastcall CInfantryGuide__UpdateGuidanceState_0048a570(void * this)",
            "Wave417 recovered CInfantryGuide vtable slot 3 body: updates guide state and target line using owner/reader positions. Stuart source body is absent; runtime guide behavior and rebuild parity remain unproven.",
            "OK",
        ),
        (
            "0x0048ac70",
            "CInfantryGuide__HandleTargetRecheckEvent",
            "void __thiscall CInfantryGuide__HandleTargetRecheckEvent(void * this, void * event)",
            "Wave417 function-boundary correction: CInfantryGuide event handler starts at 0x0048ac70, not stale mid-body 0x0048ac80. It checks event id 0x7d0, calls CInfantryGuide__SelectNearestTargetReader, reschedules event 2000, and keeps runtime guide behavior unproven.",
            "OK",
        ),
        (
            "0x0048ac80",
            "<none>",
            "<none>",
            "",
            "MISSING",
        ),
        (
            "0x0048ace0",
            "CInfantryGuide__SelectNearestTargetReader",
            "void __fastcall CInfantryGuide__SelectNearestTargetReader(void * this)",
            "Wave417 signature/comment hardening: clears active reader at +0x44, scans MapWho radius 1.0, filters candidate flags/team, chooses nearest hostile/preferred reader using threshold constants 0x005d8568/0x005dbfd0, and keeps runtime target behavior unproven.",
            "OK",
        ),
    ]
    write(
        base / "metadata_after.tsv",
        "address\tname\tsignature\tcomment\tstatus\n"
        + "\n".join("\t".join(row) for row in rows)
        + "\n",
    )
    common = "static-reaudit;infantry-guide-wave417;retail-binary-evidence;"
    write(
        base / "tags_after.tsv",
        "address\tname\ttags\tstatus\n"
        "0048a3c0\tCInfantryGuide__ctor\t" + common + "infantry-guide;constructor;signature-corrected;comment-hardened\tOK\n"
        "0048a4b0\tSharedGuide__GetField24Block_0048a4b0\t" + common + "guide;shared-helper;function-boundary;signature-hardened;comment-hardened\tOK\n"
        "0048a4c0\tCInfantryGuide__scalar_deleting_dtor\t" + common + "infantry-guide;destructor;owner-corrected;signature-corrected;comment-hardened\tOK\n"
        "0048a4e0\tCInfantryGuide__dtor\t" + common + "infantry-guide;destructor;signature-hardened;comment-hardened\tOK\n"
        "0048a570\tCInfantryGuide__UpdateGuidanceState_0048a570\t" + common + "infantry-guide;vtable-slot;function-boundary;signature-hardened;comment-hardened\tOK\n"
        "0048ac70\tCInfantryGuide__HandleTargetRecheckEvent\t" + common + "infantry-guide;event-handler;function-boundary;signature-corrected;comment-hardened\tOK\n"
        "0048ace0\tCInfantryGuide__SelectNearestTargetReader\t" + common + "infantry-guide;target-selection;signature-hardened;comment-hardened\tOK\n",
    )
    write(
        base / "instructions_after.tsv",
        "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
        "0x0048a3c0\t0x0048a3c0\tAFTER\t14\t0x0048a3e5\t0x0048a3c0\tCInfantryGuide__ctor\tCALL\t0x0047e290\te8 a6 3e ff ff\tUNCONDITIONAL_CALL\n"
        "0x0048a3c0\t0x0048a3c0\tAFTER\t69\t0x0048a4a1\t0x0048a3c0\tCInfantryGuide__ctor\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        "0x0048a4b0\t0x0048a4b0\tTARGET\t0\t0x0048a4b0\t0x0048a4b0\tSharedGuide__GetField24Block_0048a4b0\tLEA\tEAX, [ECX + 0x24]\t8d 41 24\tFALL_THROUGH\n"
        "0x0048a4b0\t0x0048a4b0\tAFTER\t1\t0x0048a4b3\t0x0048a4b0\tSharedGuide__GetField24Block_0048a4b0\tRET\t\tc3\tTERMINATOR\n"
        "0x0048a4c0\t0x0048a4c0\tAFTER\t3\t0x0048a4c8\t0x0048a4c0\tCInfantryGuide__scalar_deleting_dtor\tTEST\tbyte ptr [ESP + 0x8], 0x1\tf6 44 24 08 01\tFALL_THROUGH\n"
        "0x0048a4c0\t0x0048a4c0\tAFTER\t10\t0x0048a4dd\t0x0048a4c0\tCInfantryGuide__scalar_deleting_dtor\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        "0x0048a4e0\t0x0048a4e0\tAFTER\t20\t0x0048a51c\t0x0048a4e0\tCInfantryGuide__dtor\tCALL\t0x004e5bd0\te8 af b6 05 00\tUNCONDITIONAL_CALL\n"
        "0x0048a4e0\t0x0048a4e0\tAFTER\t35\t0x0048a558\t0x0048a4e0\tCInfantryGuide__dtor\tCALL\t0x004bac40\te8 e3 06 03 00\tUNCONDITIONAL_CALL\n"
        "0x0048a570\t0x0048a570\tTARGET\t0\t0x0048a570\t0x0048a570\tCInfantryGuide__UpdateGuidanceState_0048a570\tSUB\tESP, 0x48\t83 ec 48\tFALL_THROUGH\n"
        "0x0048a570\t0x0048a570\tAFTER\t80\t0x0048ac59\t0x0048a570\tCInfantryGuide__UpdateGuidanceState_0048a570\tRET\t\tc3\tTERMINATOR\n"
        "0x0048ac70\t0x0048ac70\tAFTER\t4\t0x0048ac78\t0x0048ac70\tCInfantryGuide__HandleTargetRecheckEvent\tCMP\tword ptr [EDI + 0x4], 0x7d0\t66 81 7f 04 d0 07\tFALL_THROUGH\n"
        "0x0048ac70\t0x0048ac70\tAFTER\t25\t0x0048acd8\t0x0048ac70\tCInfantryGuide__HandleTargetRecheckEvent\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        "0x0048ace0\t0x0048ace0\tAFTER\t24\t0x0048ad20\t0x0048ace0\tCInfantryGuide__SelectNearestTargetReader\tCALL\t0x00491ea0\te8 7b 71 00 00\tUNCONDITIONAL_CALL\n"
        "0x0048ace0\t0x0048ace0\tAFTER\t30\t0x0048ad39\t0x0048ace0\tCInfantryGuide__SelectNearestTargetReader\tCALL\t0x00492c90\te8 52 7f 00 00\tUNCONDITIONAL_CALL\n",
    )
    write(
        base / "vtable_slots_after.tsv",
        "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\tcontaining_entry\tcontaining_name\tstatus\n"
        "005dbfa8\t0\t005dbfa8\t0x0048ac70\t0048ac70\t0048ac70\tCInfantryGuide__HandleTargetRecheckEvent\t0048ac70\tCInfantryGuide__HandleTargetRecheckEvent\tOK\n"
        "005dbfa8\t1\t005dbfac\t0x0048a4c0\t0048a4c0\t0048a4c0\tCInfantryGuide__scalar_deleting_dtor\t0048a4c0\tCInfantryGuide__scalar_deleting_dtor\tOK\n"
        "005dbfa8\t3\t005dbfb4\t0x0048a570\t0048a570\t0048a570\tCInfantryGuide__UpdateGuidanceState_0048a570\t0048a570\tCInfantryGuide__UpdateGuidanceState_0048a570\tOK\n"
        "005dbfa8\t9\t005dbfcc\t0x0048a4b0\t0048a4b0\t0048a4b0\tSharedGuide__GetField24Block_0048a4b0\t0048a4b0\tSharedGuide__GetField24Block_0048a4b0\tOK\n"
        "005dbd90\t9\t005dbdb4\t0x0048a4b0\t0048a4b0\t0048a4b0\tSharedGuide__GetField24Block_0048a4b0\t0048a4b0\tSharedGuide__GetField24Block_0048a4b0\tOK\n",
    )
    write(
        base / "decompile_after" / "index.tsv",
        "address\tname\tpath\tstatus\n"
        + "\n".join(f"{address[2:]}\t{name}\t{name}.c\tOK" for address, name in [
            ("0x0048a3c0", "CInfantryGuide__ctor"),
            ("0x0048a4b0", "SharedGuide__GetField24Block_0048a4b0"),
            ("0x0048a4c0", "CInfantryGuide__scalar_deleting_dtor"),
            ("0x0048a4e0", "CInfantryGuide__dtor"),
            ("0x0048a570", "CInfantryGuide__UpdateGuidanceState_0048a570"),
            ("0x0048ac70", "CInfantryGuide__HandleTargetRecheckEvent"),
            ("0x0048ace0", "CInfantryGuide__SelectNearestTargetReader"),
        ])
        + "\n",
    )


def test_good_fixture_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        assert probe.check_targets(base) == []


def test_stale_mid_body_entry_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        text = text.replace("0x0048ac80\t<none>\t<none>\t\tMISSING", "0x0048ac80\tCInfantryGuide__SelectTargetAndScheduleRecheck\tvoid foo(void)\t\tOK")
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("0x0048ac80 expected MISSING" in failure for failure in failures)


def test_vtable_slot_name_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "vtable_slots_after.tsv").read_text(encoding="utf-8")
        text = text.replace("CInfantryGuide__HandleTargetRecheckEvent", "CInfantryGuide__SelectTargetAndScheduleRecheck", 1)
        (base / "vtable_slots_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("vtable slot 0x005dbfa8[0] name mismatch" in failure for failure in failures)


def test_runtime_overclaim_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        text = text.replace("runtime target behavior unproven", "runtime target behavior proven")
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("overclaim token" in failure for failure in failures)


def main() -> int:
    tests = [
        test_good_fixture_passes,
        test_stale_mid_body_entry_fails,
        test_vtable_slot_name_fails,
        test_runtime_overclaim_fails,
    ]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
