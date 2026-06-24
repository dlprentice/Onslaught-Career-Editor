#!/usr/bin/env python3
"""Self-tests for ghidra_infantry_lifecycle_wave416_probe.py."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_infantry_lifecycle_wave416_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def populate_good_fixture(base: Path) -> None:
    write(
        base / "apply_dry.log",
        "SUMMARY updated=0 skipped=10 created=0 would_create=0 renamed=0 would_rename=6 missing=0 bad=0\n",
    )
    write(
        base / "apply_apply.log",
        "SUMMARY updated=10 skipped=0 created=0 would_create=0 renamed=6 would_rename=0 missing=0 bad=0\n",
    )
    rows = [
        (
            "0x00488bb0",
            "CInfantry__Init",
            "void __thiscall CInfantry__Init(void * this, void * infantryInit)",
            "Signature/comment correction: Infantry init takes an infantry init pointer, allocates collision seeking and guide helpers, applies 4.0/1.0 scale context, calls CGroundUnit__Init, and keeps runtime infantry behavior and rebuild parity unproven.",
        ),
        (
            "0x00488dc0",
            "CInfantryAI__scalar_deleting_dtor",
            "void * __thiscall CInfantryAI__scalar_deleting_dtor(void * this, byte flags)",
            "Name/signature correction: scalar-deleting destructor wrapper calls CInfantryAI__dtor_body_00488de0, checks flags bit 0, optionally frees through OID__FreeObject, returns this, and keeps runtime cleanup behavior unproven.",
        ),
        (
            "0x00488de0",
            "CInfantryAI__dtor_body_00488de0",
            "void __fastcall CInfantryAI__dtor_body_00488de0(void * this)",
            "Name/signature correction: destructor body reached by CInfantryAI scalar deleting destructor restores CUnitAI base vtable 0x005d8d1c, removes +0x28/+0x24/+0x0c pointer-set links through CSPtrSet__Remove, calls CMonitor__Shutdown, and keeps runtime cleanup behavior unproven.",
        ),
        (
            "0x00488e80",
            "CCollisionSeekingInfantryBloke__scalar_deleting_dtor",
            "void * __thiscall CCollisionSeekingInfantryBloke__scalar_deleting_dtor(void * this, byte flags)",
            "Name/signature correction: scalar-deleting destructor wrapper calls CCollisionSeekingInfantryBloke__dtor_body_00488ea0, checks flags bit 0, optionally frees through OID__FreeObject, returns this, and keeps runtime collision behavior unproven.",
        ),
        (
            "0x00488ea0",
            "CCollisionSeekingInfantryBloke__dtor_body_00488ea0",
            "void __fastcall CCollisionSeekingInfantryBloke__dtor_body_00488ea0(void * this)",
            "Name/signature correction: destructor body reached by the collision-seeking infantry bloke scalar wrapper shuts down the monitor at this+0x24, calls CCollisionSeekingRound__Destructor, and keeps runtime collision behavior unproven.",
        ),
        (
            "0x00488ef0",
            "CCollisionSeekingThing__ctor_base",
            "void __fastcall CCollisionSeekingThing__ctor_base(void * this)",
            "Name/signature correction: constructor-base helper zeros field +0x04 and installs the shared CCollisionSeekingThing vtable 0x005d9608; exact source identity and rebuild parity remain unproven.",
        ),
        (
            "0x00488f00",
            "CHLCollisionDetector__ctor_base",
            "void __fastcall CHLCollisionDetector__ctor_base(void * this)",
            "Name/signature correction: constructor-base helper zeros field +0x04 and installs CHLCollisionDetector vtable 0x005dbf78; exact source identity and rebuild parity remain unproven.",
        ),
        (
            "0x00489040",
            "CUnitAI__TryPlayActivateAnimation",
            "int __fastcall CUnitAI__TryPlayActivateAnimation(void * this)",
            "Signature/comment hardening: activation-animation helper checks fields +0x140/+0x26c/+0x2c, calls CUnitAI__TrySpawnOrFinalizeAttachedUnit, writes state +0x268 to 0x12, and keeps runtime AI behavior unproven.",
        ),
        (
            "0x00489de0",
            "CUnitAI__PromoteDieAnimationToDeadVariant",
            "int __fastcall CUnitAI__PromoteDieAnimationToDeadVariant(void * this)",
            "Signature/comment hardening: maps current die animation tokens die_up/die_back/die_left/die_right to dead_up/dead_back/dead_left/dead_right or dead_forward and keeps runtime death behavior unproven.",
        ),
        (
            "0x00489ef0",
            "CUnitAI__ForceDeadForwardAndResetDeathState",
            "void __fastcall CUnitAI__ForceDeadForwardAndResetDeathState(void * this)",
            "Signature/comment hardening: if death flag bit +0x2c is set, selects dead_forward, clears +0x26c, refreshes the state timestamp, and keeps runtime death behavior unproven.",
        ),
    ]
    write(
        base / "metadata_after.tsv",
        "address\tname\tsignature\tcomment\tstatus\n"
        + "\n".join("\t".join(row) + "\tOK" for row in rows)
        + "\n",
    )
    common = "static-reaudit;infantry-wave416;retail-binary-evidence;"
    write(
        base / "tags_after.tsv",
        "address\tname\ttags\tstatus\n"
        "00488bb0\tCInfantry__Init\t" + common + "infantry;lifecycle;signature-hardened;comment-hardened\tOK\n"
        "00488dc0\tCInfantryAI__scalar_deleting_dtor\t" + common + "infantry;destructor;owner-corrected;signature-corrected;comment-hardened\tOK\n"
        "00488de0\tCInfantryAI__dtor_body_00488de0\t" + common + "infantry;destructor;owner-corrected;signature-corrected;comment-hardened\tOK\n"
        "00488e80\tCCollisionSeekingInfantryBloke__scalar_deleting_dtor\t" + common + "collision;destructor;owner-corrected;signature-corrected;comment-hardened\tOK\n"
        "00488ea0\tCCollisionSeekingInfantryBloke__dtor_body_00488ea0\t" + common + "collision;destructor;owner-corrected;signature-corrected;comment-hardened\tOK\n"
        "00488ef0\tCCollisionSeekingThing__ctor_base\t" + common + "collision;constructor;signature-corrected;comment-hardened\tOK\n"
        "00488f00\tCHLCollisionDetector__ctor_base\t" + common + "collision;constructor;signature-corrected;comment-hardened\tOK\n"
        "00489040\tCUnitAI__TryPlayActivateAnimation\t" + common + "unitai;animation;signature-hardened;comment-hardened\tOK\n"
        "00489de0\tCUnitAI__PromoteDieAnimationToDeadVariant\t" + common + "unitai;death-animation;signature-hardened;comment-hardened\tOK\n"
        "00489ef0\tCUnitAI__ForceDeadForwardAndResetDeathState\t" + common + "unitai;death-animation;signature-hardened;comment-hardened\tOK\n",
    )
    write(
        base / "xrefs_after.tsv",
        "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
        "00488bb0\tCInfantry__Init\t005e2750\t<none>\t<no_function>\tDATA\n"
        "00488dc0\tCInfantryAI__scalar_deleting_dtor\t005dbf18\t<none>\t<no_function>\tDATA\n"
        "00488de0\tCInfantryAI__dtor_body_00488de0\t00488dc3\t00488dc0\tCInfantryAI__scalar_deleting_dtor\tUNCONDITIONAL_CALL\n"
        "00488e80\tCCollisionSeekingInfantryBloke__scalar_deleting_dtor\t005dbf4c\t<none>\t<no_function>\tDATA\n"
        "00488ea0\tCCollisionSeekingInfantryBloke__dtor_body_00488ea0\t00488e83\t00488e80\tCCollisionSeekingInfantryBloke__scalar_deleting_dtor\tUNCONDITIONAL_CALL\n"
        "00488ef0\tCCollisionSeekingThing__ctor_base\t00488c0a\t00488bb0\tCInfantry__Init\tUNCONDITIONAL_CALL\n"
        "00488ef0\tCCollisionSeekingThing__ctor_base\t004d8639\t004d8410\tCRound__Init\tUNCONDITIONAL_CALL\n"
        "00488f00\tCHLCollisionDetector__ctor_base\t00488c17\t00488bb0\tCInfantry__Init\tUNCONDITIONAL_CALL\n"
        "00488f00\tCHLCollisionDetector__ctor_base\t004d8649\t004d8410\tCRound__Init\tUNCONDITIONAL_CALL\n"
        "00489040\tCUnitAI__TryPlayActivateAnimation\t005e2854\t<none>\t<no_function>\tDATA\n"
        "00489de0\tCUnitAI__PromoteDieAnimationToDeadVariant\t005e2818\t<none>\t<no_function>\tDATA\n"
        "00489ef0\tCUnitAI__ForceDeadForwardAndResetDeathState\t005e283c\t<none>\t<no_function>\tDATA\n",
    )
    write(
        base / "instructions_after.tsv",
        "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
        "0x00488dc0\t0x00488dc0\tAFTER\t3\t0x00488dc8\t0x00488dc0\tCInfantryAI__scalar_deleting_dtor\tTEST\tbyte ptr [ESP + 0x8], 0x1\tf6 44 24 08 01\tFALL_THROUGH\n"
        "0x00488dc0\t0x00488dc0\tAFTER\t10\t0x00488ddd\t0x00488dc0\tCInfantryAI__scalar_deleting_dtor\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        "0x00488de0\t0x00488de0\tAFTER\t9\t0x00488dfd\t0x00488de0\tCInfantryAI__dtor_body_00488de0\tMOV\tdword ptr [ESI], 0x5d8d1c\tc7 06 1c 8d 5d 00\tFALL_THROUGH\n"
        "0x00488e80\t0x00488e80\tAFTER\t3\t0x00488e88\t0x00488e80\tCCollisionSeekingInfantryBloke__scalar_deleting_dtor\tTEST\tbyte ptr [ESP + 0x8], 0x1\tf6 44 24 08 01\tFALL_THROUGH\n"
        "0x00488e80\t0x00488e80\tAFTER\t10\t0x00488e9d\t0x00488e80\tCCollisionSeekingInfantryBloke__scalar_deleting_dtor\tRET\t0x4\tc2 04 00\tTERMINATOR\n"
        "0x00488f00\t0x00488f00\tAFTER\t2\t0x00488f09\t0x00488f00\tCHLCollisionDetector__ctor_base\tMOV\tdword ptr [EAX], 0x5dbf78\tc7 00 78 bf 5d 00\tFALL_THROUGH\n"
        "0x00489de0\t0x00489de0\tAFTER\t10\t0x00489dfb\t0x00489de0\tCUnitAI__PromoteDieAnimationToDeadVariant\tPUSH\t0x62d560\t68 60 d5 62 00\tFALL_THROUGH\n"
        "0x00489ef0\t0x00489ef0\tAFTER\t10\t0x00489f2b\t0x00489ef0\tCUnitAI__ForceDeadForwardAndResetDeathState\tMOV\tdword ptr [ESI + 0x26c], 0x0\tc7 86 6c 02 00 00 00 00 00 00\tFALL_THROUGH\n",
    )


def test_good_fixture_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        assert probe.check_targets(base) == []


def test_stale_vfunc_name_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        text = text.replace("CInfantryAI__scalar_deleting_dtor", "CInfantryAI__VFunc_01_00488dc0")
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("0x00488dc0 name expected" in failure for failure in failures)


def test_runtime_overclaim_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        text = text.replace("runtime AI behavior unproven", "runtime AI behavior proven")
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("overclaim token" in failure for failure in failures)


def main() -> int:
    tests = [test_good_fixture_passes, test_stale_vfunc_name_fails, test_runtime_overclaim_fails]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
