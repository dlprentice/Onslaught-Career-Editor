#!/usr/bin/env python3
"""Self-tests for ghidra_cibuffer_index_buffer_wave413_probe.py."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_cibuffer_index_buffer_wave413_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def populate_good_fixture(base: Path) -> None:
    write(
        base / "apply_dry.log",
        "SUMMARY updated=0 skipped=10 created=0 would_create=2 renamed=0 would_rename=0 missing=0 bad=0\n",
    )
    write(
        base / "apply_apply.log",
        "SUMMARY updated=12 skipped=0 created=2 would_create=0 renamed=0 would_rename=0 missing=0 bad=0\n",
    )
    write(
        base / "metadata_after.tsv",
        "address\tname\tsignature\tcomment\tstatus\n"
        "0x00488210\tCIBuffer__Constructor\tvoid * __thiscall CIBuffer__Constructor(void * this)\t"
        "Wave413 signature/comment hardening: CIBuffer constructor sets the CIBuffer vtable 0x005dbec4, clears the D3D index-buffer pointer, initializes the base render/device object path, clears shadow-copy storage at +0x1c, and clears the lock flag at +0x20. Static retail evidence only; exact source body identity, concrete CIBuffer layout, runtime rendering behavior, and rebuild parity remain unproven.\tOK\n"
        "0x00488270\tCIBuffer__ScalarDeletingDestructor\tvoid * __thiscall CIBuffer__ScalarDeletingDestructor(void * this, byte flags)\t"
        "Wave413 signature/comment hardening: scalar deleting destructor wrapper calls CIBuffer__Destructor and conditionally frees the object when flags bit 0 is set. Static retail evidence only; exact source body identity, concrete allocator ownership, runtime rendering behavior, and rebuild parity remain unproven.\tOK\n"
        "0x00488290\tCIBuffer__Destructor\tvoid __thiscall CIBuffer__Destructor(void * this)\t"
        "Wave413 signature/comment hardening: CIBuffer destructor restores the CIBuffer vtable, runs the base unlink/shutdown path, releases the D3D index-buffer interface when present for static or dynamic buffers, clears +0x08, frees shadow-copy storage at +0x1c, and then runs the base device-object destructor path. Static retail evidence only; exact source body identity, concrete CIBuffer layout, runtime rendering behavior, and rebuild parity remain unproven.\tOK\n"
        "0x00488330\tCIBuffer__CreateConfigured\tint __thiscall CIBuffer__CreateConfigured(void * this, int size_bytes, int usage_flags, int index_format, int buffer_type)\t"
        "Wave413 signature/comment correction: configured CIBuffer create stores size_bytes at +0x0c, usage_flags at +0x10, index_format at +0x14, and buffer_type at +0x18, then dispatches vtable slot +0x04 for dynamic buffers or vtable slot +0x08 for static buffers before the localized HRESULT fatal-check gate. Static retail evidence only; exact source body identity, concrete CIBuffer layout, runtime rendering behavior, and rebuild parity remain unproven.\tOK\n"
        "0x00488380\tCIBuffer__Create\tint __thiscall CIBuffer__Create(void * this, int index_count)\t"
        "Wave413 signature/comment hardening: default CIBuffer create allocates a shadow index buffer of index_count*2 bytes from the ibuffer.cpp debug path, stores size/usage/format/type fields, dispatches the dynamic create vtable slot, and checks the HRESULT with the localized fatal gate. Static retail evidence only; exact source body identity, concrete CIBuffer layout, runtime rendering behavior, and rebuild parity remain unproven.\tOK\n"
        "0x004883f0\tCIBuffer__Unlock\tint __thiscall CIBuffer__Unlock(void * this)\t"
        "Wave413 signature/comment hardening: CIBuffer unlock returns zero when no D3D buffer exists, directly unlocks when the shadow-copy dirty flag is clear, or locks the D3D buffer with 0x800, copies +0x0c bytes from shadow storage +0x1c, clears +0x20, and unlocks. Static retail evidence only; exact source body identity, concrete CIBuffer layout, runtime rendering behavior, and rebuild parity remain unproven.\tOK\n"
        "0x00488460\tCIBuffer__CreateDynamic\tint __thiscall CIBuffer__CreateDynamic(void * this)\t"
        "Wave413 recovered function boundary: CIBuffer dynamic-create vtable slot 1 checks buffer_type +0x18 == 1, calls the D3D CreateIndexBuffer wrapper at 0x005137d0 with size/usage/format and dynamic pool token 1, returns 0x80004005 on create or follow-up lock failure, and copies the shadow buffer into the locked D3D buffer before unlocking when shadow storage exists. Static retail evidence only; exact source body identity, concrete CIBuffer layout, runtime rendering behavior, and rebuild parity remain unproven.\tOK\n"
        "0x004884f0\tCIBuffer__CreateStatic\tint __thiscall CIBuffer__CreateStatic(void * this)\t"
        "Wave413 recovered function boundary: CIBuffer static-create vtable slot 2 checks buffer_type +0x18 == 0, calls the D3D CreateIndexBuffer wrapper at 0x005137d0 with size/usage/format and pool token 0, returns 0x80004005 on failure, and otherwise returns zero. Static retail evidence only; exact source body identity, concrete CIBuffer layout, runtime rendering behavior, and rebuild parity remain unproven.\tOK\n"
        "0x00488520\tCIBuffer__ReleaseStatic\tint __thiscall CIBuffer__ReleaseStatic(void * this)\t"
        "Wave413 signature/comment hardening: CIBuffer static-release vtable slot releases and clears +0x08 only when buffer_type +0x18 is static zero and the D3D index-buffer pointer is present; it returns zero. Static retail evidence only; exact source body identity, concrete CIBuffer layout, runtime rendering behavior, and rebuild parity remain unproven.\tOK\n"
        "0x00488550\tCIBuffer__ReleaseDynamic\tint __thiscall CIBuffer__ReleaseDynamic(void * this)\t"
        "Wave413 signature/comment hardening: CIBuffer dynamic-release vtable slot releases and clears +0x08 only when buffer_type +0x18 is dynamic one and the D3D index-buffer pointer is present; it returns zero. Static retail evidence only; exact source body identity, concrete CIBuffer layout, runtime rendering behavior, and rebuild parity remain unproven.\tOK\n"
        "0x00488580\tCIBuffer__Lock\tint __thiscall CIBuffer__Lock(void * this, void * * out_data)\t"
        "Wave413 signature/comment hardening: CIBuffer lock returns shadow storage +0x1c through out_data and sets dirty flag +0x20 when a shadow copy exists; otherwise it locks the D3D index buffer at +0x08 with 0x2800 when usage flag 0x200 is set or 0x800 otherwise. Static retail evidence only; exact source body identity, concrete CIBuffer layout, runtime rendering behavior, and rebuild parity remain unproven.\tOK\n"
        "0x0048e350\tCIBuffer__Destructor_thunk\tvoid __thiscall CIBuffer__Destructor_thunk(void * this)\t"
        "Wave413 signature/comment hardening: CIBuffer destructor thunk preserves the thiscall receiver and jumps to CIBuffer__Destructor. Static retail evidence only; exact source body identity, concrete caller ownership, runtime rendering behavior, and rebuild parity remain unproven.\tOK\n",
    )
    common = "static-reaudit;cibuffer-index-buffer-wave413;retail-binary-evidence;ibuffer;"
    write(
        base / "tags_after.tsv",
        "address\tname\ttags\tstatus\n"
        f"00488210\tCIBuffer__Constructor\t{common}constructor;signature-hardened;comment-hardened\tOK\n"
        f"00488270\tCIBuffer__ScalarDeletingDestructor\t{common}destructor;signature-hardened;comment-hardened\tOK\n"
        f"00488290\tCIBuffer__Destructor\t{common}destructor;signature-hardened;comment-hardened\tOK\n"
        f"00488330\tCIBuffer__CreateConfigured\t{common}create;signature-corrected;comment-hardened\tOK\n"
        f"00488380\tCIBuffer__Create\t{common}create;shadow-buffer;signature-hardened;comment-hardened\tOK\n"
        f"004883f0\tCIBuffer__Unlock\t{common}lock-unlock;shadow-buffer;signature-hardened;comment-hardened\tOK\n"
        f"00488460\tCIBuffer__CreateDynamic\t{common}function-boundary;vtable-slot;create;dynamic-buffer;comment-hardened\tOK\n"
        f"004884f0\tCIBuffer__CreateStatic\t{common}function-boundary;vtable-slot;create;static-buffer;comment-hardened\tOK\n"
        f"00488520\tCIBuffer__ReleaseStatic\t{common}vtable-slot;release;static-buffer;signature-hardened;comment-hardened\tOK\n"
        f"00488550\tCIBuffer__ReleaseDynamic\t{common}vtable-slot;release;dynamic-buffer;signature-hardened;comment-hardened\tOK\n"
        f"00488580\tCIBuffer__Lock\t{common}lock-unlock;shadow-buffer;signature-hardened;comment-hardened\tOK\n"
        f"0048e350\tCIBuffer__Destructor_thunk\t{common}destructor;thunk;signature-hardened;comment-hardened\tOK\n",
    )
    write(
        base / "vtable_after.tsv",
        "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\tcontaining_entry\tcontaining_name\tstatus\n"
        "005dbec4\t0\t005dbec4\t0x00488270\t00488270\t00488270\tCIBuffer__ScalarDeletingDestructor\t00488270\tCIBuffer__ScalarDeletingDestructor\tOK\n"
        "005dbec4\t1\t005dbec8\t0x00488460\t00488460\t00488460\tCIBuffer__CreateDynamic\t00488460\tCIBuffer__CreateDynamic\tOK\n"
        "005dbec4\t2\t005dbecc\t0x004884f0\t004884f0\t004884f0\tCIBuffer__CreateStatic\t004884f0\tCIBuffer__CreateStatic\tOK\n"
        "005dbec4\t3\t005dbed0\t0x00488520\t00488520\t00488520\tCIBuffer__ReleaseStatic\t00488520\tCIBuffer__ReleaseStatic\tOK\n"
        "005dbec4\t4\t005dbed4\t0x00488550\t00488550\t00488550\tCIBuffer__ReleaseDynamic\t00488550\tCIBuffer__ReleaseDynamic\tOK\n",
    )
    write(
        base / "xrefs_after.tsv",
        "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
        "00488210\tCIBuffer__Constructor\t0050085e\t005007f0\tCVBufTexture__ResizeIndexBuffer\tUNCONDITIONAL_CALL\n"
        "00488330\tCIBuffer__CreateConfigured\t00500887\t005007f0\tCVBufTexture__ResizeIndexBuffer\tUNCONDITIONAL_CALL\n"
        "00488380\tCIBuffer__Create\t0051a5ae\t0051a510\tCFastVB__Render\tUNCONDITIONAL_CALL\n"
        "004883f0\tCIBuffer__Unlock\t005009fd\t005009f0\tCVBufTexture__UnlockIB\tUNCONDITIONAL_CALL\n"
        "00488460\tCIBuffer__CreateDynamic\t005dbec8\t<none>\t<no_function>\tDATA\n"
        "004884f0\tCIBuffer__CreateStatic\t005dbecc\t<none>\t<no_function>\tDATA\n"
        "00488580\tCIBuffer__Lock\t0051a5be\t0051a510\tCFastVB__Render\tUNCONDITIONAL_CALL\n"
        "0048e350\tCIBuffer__Destructor_thunk\t005506bc\t<none>\t<no_function>\tUNCONDITIONAL_CALL\n",
    )
    for address, (name, body) in {
        "00488330": ("CIBuffer__CreateConfigured", "size_bytes usage_flags index_format buffer_type + 0x18"),
        "00488380": ("CIBuffer__Create", "index_count 0x65"),
        "004883f0": ("CIBuffer__Unlock", "0x800 0x1c 0x20"),
        "00488460": ("CIBuffer__CreateDynamic", "0x005137d0 0x800 0x80004005 MOVSD.REP MOVSB.REP"),
        "004884f0": ("CIBuffer__CreateStatic", "0x005137d0 0x80004005"),
        "00488580": ("CIBuffer__Lock", "out_data 0x2800 0x800 0x200"),
    }.items():
        write(base / "decompile_after" / f"{address}_{name}.c", body)
    write(
        base / "create_slot_instructions_after.tsv",
        "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
        "0x00488460\t0x00488460\tTARGET\t0\t0x00488460\t0x00488460\tCIBuffer__CreateDynamic\tPUSH\tECX\t51\tFALL_THROUGH\n"
        "0x00488460\t0x00488460\tAFTER\t16\t0x00488482\t0x00488460\tCIBuffer__CreateDynamic\tCALL\t0x005137d0\te8 49 b3 08 00\tUNCONDITIONAL_CALL\n"
        "0x00488460\t0x00488460\tAFTER\t20\t0x0048848c\t0x00488460\tCIBuffer__CreateDynamic\tMOV\tEAX, 0x80004005\tb8 05 40 00 80\tFALL_THROUGH\n"
        "0x00488460\t0x00488460\tAFTER\t44\t0x004884c5\t0x00488460\tCIBuffer__CreateDynamic\tMOVSD.REP\tES:EDI, ESI\tf3 a5\tFALL_THROUGH\n"
        "0x004884f0\t0x004884f0\tTARGET\t0\t0x004884f0\t0x004884f0\tCIBuffer__CreateStatic\tMOV\tEAX, dword ptr [ECX + 0x18]\t8b 41 18\tFALL_THROUGH\n"
        "0x004884f0\t0x004884f0\tAFTER\t13\t0x0048850e\t0x004884f0\tCIBuffer__CreateStatic\tCALL\t0x005137d0\te8 bd b2 08 00\tUNCONDITIONAL_CALL\n"
        "0x004884f0\t0x004884f0\tAFTER\t16\t0x00488517\t0x004884f0\tCIBuffer__CreateStatic\tMOV\tEAX, 0x80004005\tb8 05 40 00 80\tFALL_THROUGH\n",
    )


def test_good_fixture_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        assert probe.check_targets(base) == []


def test_missing_created_boundary_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        text = text.replace("CIBuffer__CreateDynamic", "<none>")
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("0x00488460 name expected" in failure for failure in failures)


def main() -> int:
    tests = [test_good_fixture_passes, test_missing_created_boundary_fails]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
