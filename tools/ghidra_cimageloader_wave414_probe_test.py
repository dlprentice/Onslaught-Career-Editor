#!/usr/bin/env python3
"""Self-tests for ghidra_cimageloader_wave414_probe.py."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_cimageloader_wave414_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def populate_good_fixture(base: Path) -> None:
    write(
        base / "apply_dry.log",
        "SUMMARY updated=0 skipped=8 created=0 would_create=5 renamed=0 would_rename=1 missing=0 bad=0\n",
    )
    write(
        base / "apply_apply.log",
        "SUMMARY updated=13 skipped=0 created=5 would_create=0 renamed=1 would_rename=0 missing=0 bad=0\n",
    )
    rows = [
        ("0x004885e0", "CIBuffer__LockDirect", "int __thiscall CIBuffer__LockDirect(void * this, void * * out_data)", "direct CIBuffer D3D index-buffer lock helper +0x08 +0x10 0x2800 0x800 0x200 CVBufTexture index-buffer callers runtime rendering behavior and rebuild parity remain unproven"),
        ("0x00488620", "CImageLoader__Constructor", "void * __thiscall CImageLoader__Constructor(void * this, char * filename)", "CImageLoader constructor zeroes +0x04 through +0x14 vtable 0x005dbedc copies filename to +0x18 source body is absent runtime image loading remain unproven"),
        ("0x00488670", "CImageLoader__GetFilenamePtr", "char * __thiscall CImageLoader__GetFilenamePtr(void * this)", "recovered vtable function boundary returns this +0x18 filename pointer source body identity and runtime image loading remain unproven"),
        ("0x00488680", "CImageLoader__GetWidth", "int __thiscall CImageLoader__GetWidth(void * this)", "recovered vtable function boundary returns image width from +0x08 source body identity and runtime image loading remain unproven"),
        ("0x00488690", "CImageLoader__GetHeight", "int __thiscall CImageLoader__GetHeight(void * this)", "recovered vtable function boundary returns image height from +0x0c source body identity and runtime image loading remain unproven"),
        ("0x004886a0", "CImageLoader__ScalarDeletingDestructor", "void * __thiscall CImageLoader__ScalarDeletingDestructor(void * this, byte flags)", "scalar deleting destructor frees width and height buffers flags bit 0 source body identity and runtime image loading remain unproven"),
        ("0x00488700", "CImageLoader__Destructor", "void __thiscall CImageLoader__Destructor(void * this)", "CImageLoader destructor frees width and height buffers source body identity and runtime image loading remain unproven"),
        ("0x00488740", "CImageLoader__FreeWidthBuffer", "void __thiscall CImageLoader__FreeWidthBuffer(void * this)", "CImageLoader width-buffer free helper at +0x10 source body identity and runtime image loading remain unproven"),
        ("0x00488760", "CImageLoader__FreeHeightBuffer", "void __thiscall CImageLoader__FreeHeightBuffer(void * this)", "CImageLoader height-buffer free helper at +0x14 source body identity and runtime image loading remain unproven"),
        ("0x00488780", "CImageLoader__LoadWidthBuffer", "bool __thiscall CImageLoader__LoadWidthBuffer(void * this, void * alloc_context)", "calls vtable slot +0x24 then allocates 0x80 bytes for +0x10 using imageloader.cpp debug path line 0x2b source body identity and runtime image loading remain unproven"),
        ("0x004887c0", "CImageLoader__LoadHeightBuffer", "bool __thiscall CImageLoader__LoadHeightBuffer(void * this, void * alloc_context)", "calls vtable slot +0x28 then allocates 0x80 bytes for +0x14 using imageloader.cpp debug path line 0x32 source body identity and runtime image loading remain unproven"),
        ("0x0052f540", "SharedVFunc__ReturnField04_0052f540", "void * __thiscall SharedVFunc__ReturnField04_0052f540(void * this)", "recovered shared vtable function boundary returns field +0x04 across ImageLoader and other vtables source body identity and runtime behavior remain unproven"),
        ("0x004de070", "SharedVFunc__ReturnField14_004de070", "void * __thiscall SharedVFunc__ReturnField14_004de070(void * this)", "recovered shared vtable function boundary returns field +0x14 across ImageLoader and other vtables source body identity and runtime behavior remain unproven"),
    ]
    write(
        base / "metadata_after.tsv",
        "address\tname\tsignature\tcomment\tstatus\n"
        + "\n".join("\t".join(row) + "\tOK" for row in rows)
        + "\n",
    )
    common = "static-reaudit;cimageloader-wave414;retail-binary-evidence;"
    write(
        base / "tags_after.tsv",
        "address\tname\ttags\tstatus\n"
        "004885e0\tCIBuffer__LockDirect\t" + common + "ibuffer;owner-corrected;lock-unlock;signature-corrected;comment-hardened\tOK\n"
        "00488620\tCImageLoader__Constructor\t" + common + "imageloader;constructor;signature-hardened;comment-hardened\tOK\n"
        "00488670\tCImageLoader__GetFilenamePtr\t" + common + "imageloader;function-boundary;vtable-slot;getter;comment-hardened\tOK\n"
        "00488680\tCImageLoader__GetWidth\t" + common + "imageloader;function-boundary;vtable-slot;getter;comment-hardened\tOK\n"
        "00488690\tCImageLoader__GetHeight\t" + common + "imageloader;function-boundary;vtable-slot;getter;comment-hardened\tOK\n"
        "004886a0\tCImageLoader__ScalarDeletingDestructor\t" + common + "imageloader;destructor;signature-hardened;comment-hardened\tOK\n"
        "00488700\tCImageLoader__Destructor\t" + common + "imageloader;destructor;signature-hardened;comment-hardened\tOK\n"
        "00488740\tCImageLoader__FreeWidthBuffer\t" + common + "imageloader;buffer-lifecycle;signature-hardened;comment-hardened\tOK\n"
        "00488760\tCImageLoader__FreeHeightBuffer\t" + common + "imageloader;buffer-lifecycle;signature-hardened;comment-hardened\tOK\n"
        "00488780\tCImageLoader__LoadWidthBuffer\t" + common + "imageloader;buffer-lifecycle;signature-hardened;comment-hardened\tOK\n"
        "004887c0\tCImageLoader__LoadHeightBuffer\t" + common + "imageloader;buffer-lifecycle;signature-hardened;comment-hardened\tOK\n"
        "0052f540\tSharedVFunc__ReturnField04_0052f540\t" + common + "shared-vfunc;function-boundary;vtable-slot;getter;comment-hardened\tOK\n"
        "004de070\tSharedVFunc__ReturnField14_004de070\t" + common + "shared-vfunc;function-boundary;vtable-slot;getter;comment-hardened\tOK\n",
    )
    write(
        base / "vtable_after.tsv",
        "vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\tcontaining_entry\tcontaining_name\tstatus\n"
        "005dbedc\t0\t005dbedc\t0x004886a0\t004886a0\t004886a0\tCImageLoader__ScalarDeletingDestructor\t004886a0\tCImageLoader__ScalarDeletingDestructor\tOK\n"
        "005dbedc\t2\t005dbee4\t0x00488670\t00488670\t00488670\tCImageLoader__GetFilenamePtr\t00488670\tCImageLoader__GetFilenamePtr\tOK\n"
        "005dbedc\t3\t005dbee8\t0x0052f540\t0052f540\t0052f540\tSharedVFunc__ReturnField04_0052f540\t0052f540\tSharedVFunc__ReturnField04_0052f540\tOK\n"
        "005dbedc\t4\t005dbeec\t0x00488680\t00488680\t00488680\tCImageLoader__GetWidth\t00488680\tCImageLoader__GetWidth\tOK\n"
        "005dbedc\t5\t005dbef0\t0x00488690\t00488690\t00488690\tCImageLoader__GetHeight\t00488690\tCImageLoader__GetHeight\tOK\n"
        "005dbedc\t7\t005dbef8\t0x004de070\t004de070\t004de070\tSharedVFunc__ReturnField14_004de070\t004de070\tSharedVFunc__ReturnField14_004de070\tOK\n"
        "005dbedc\t9\t005dbf00\t0x00488740\t00488740\t00488740\tCImageLoader__FreeWidthBuffer\t00488740\tCImageLoader__FreeWidthBuffer\tOK\n"
        "005dbedc\t10\t005dbf04\t0x00488760\t00488760\t00488760\tCImageLoader__FreeHeightBuffer\t00488760\tCImageLoader__FreeHeightBuffer\tOK\n"
        "005dbedc\t11\t005dbf08\t0x00488780\t00488780\t00488780\tCImageLoader__LoadWidthBuffer\t00488780\tCImageLoader__LoadWidthBuffer\tOK\n"
        "005dbedc\t12\t005dbf0c\t0x004887c0\t004887c0\t004887c0\tCImageLoader__LoadHeightBuffer\t004887c0\tCImageLoader__LoadHeightBuffer\tOK\n",
    )
    write(
        base / "xrefs_after.tsv",
        "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
        "004885e0\tCIBuffer__LockDirect\t00500afa\t00500ac0\tCVBufTexture__AddIndices\tUNCONDITIONAL_CALL\n"
        "004885e0\tCIBuffer__LockDirect\t00546d95\t00546b40\tCDXLandscape__UpdateLOD\tUNCONDITIONAL_CALL\n"
        "00488670\tCImageLoader__GetFilenamePtr\t005dbee4\t<none>\t<no_function>\tDATA\n"
        "00488670\tCImageLoader__GetFilenamePtr\t005df520\t<none>\t<no_function>\tDATA\n"
        "0052f540\tSharedVFunc__ReturnField04_0052f540\t005dbee8\t<none>\t<no_function>\tDATA\n"
        "004de070\tSharedVFunc__ReturnField14_004de070\t005dbef8\t<none>\t<no_function>\tDATA\n",
    )
    for address, name, body in [
        ("004885e0", "CIBuffer__LockDirect", "out_data 0x2800 0x800 0x200"),
        ("00488620", "CImageLoader__Constructor", "filename 005dbedc"),
        ("00488670", "CImageLoader__GetFilenamePtr", "+ 0x18"),
        ("00488680", "CImageLoader__GetWidth", "+8"),
        ("00488690", "CImageLoader__GetHeight", "+ 0xc"),
        ("0052f540", "SharedVFunc__ReturnField04_0052f540", "+4"),
        ("004de070", "SharedVFunc__ReturnField14_004de070", "+ 0x14"),
        ("00488780", "CImageLoader__LoadWidthBuffer", "alloc_context 0x80 0x2b"),
        ("004887c0", "CImageLoader__LoadHeightBuffer", "alloc_context 0x80 0x32"),
    ]:
        write(base / "decompile_after" / f"{address}_{name}.c", body)
    write(
        base / "instructions_after.tsv",
        "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
        "0x00488670\t0x00488670\tTARGET\t0\t0x00488670\t0x00488670\tCImageLoader__GetFilenamePtr\tLEA\tEAX, [ECX + 0x18]\t8d 41 18\tFALL_THROUGH\n"
        "0x00488680\t0x00488680\tTARGET\t0\t0x00488680\t0x00488680\tCImageLoader__GetWidth\tMOV\tEAX, dword ptr [ECX + 0x8]\t8b 41 08\tFALL_THROUGH\n"
        "0x00488690\t0x00488690\tTARGET\t0\t0x00488690\t0x00488690\tCImageLoader__GetHeight\tMOV\tEAX, dword ptr [ECX + 0xc]\t8b 41 0c\tFALL_THROUGH\n"
        "0x0052f540\t0x0052f540\tTARGET\t0\t0x0052f540\t0x0052f540\tSharedVFunc__ReturnField04_0052f540\tMOV\tEAX, dword ptr [ECX + 0x4]\t8b 41 04\tFALL_THROUGH\n"
        "0x004de070\t0x004de070\tTARGET\t0\t0x004de070\t0x004de070\tSharedVFunc__ReturnField14_004de070\tMOV\tEAX, dword ptr [ECX + 0x14]\t8b 41 14\tFALL_THROUGH\n",
    )


def test_good_fixture_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        assert probe.check_targets(base) == []


def test_stale_owner_name_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        text = text.replace("CIBuffer__LockDirect", "CVBufTexture__SetTextureStageFilterByFlag200")
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("0x004885e0 name expected" in failure for failure in failures)


def main() -> int:
    tests = [test_good_fixture_passes, test_stale_owner_name_fails]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
