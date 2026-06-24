#!/usr/bin/env python3
"""Self-tests for ghidra_imposter_wave415_probe.py."""

from __future__ import annotations

import tempfile
from pathlib import Path

import ghidra_imposter_wave415_probe as probe


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def populate_good_fixture(base: Path) -> None:
    write(
        base / "apply_dry.log",
        "SUMMARY updated=0 skipped=3 created=0 would_create=2 renamed=0 would_rename=1 missing=0 bad=0\n",
    )
    write(
        base / "apply_apply.log",
        "SUMMARY updated=5 skipped=0 created=2 would_create=0 renamed=1 would_rename=0 missing=0 bad=0\n",
    )
    rows = [
        (
            "0x004888f0",
            "CImposter__FindOrCreate",
            "void * __cdecl CImposter__FindOrCreate(char * name, int key_24, int key_40, int key_30, int key_44, int key_48, int key_34)",
            "find-or-create helper searches global imposter list 0x0067a678 with stricmp and matching key fields +0x24 +0x30 +0x34 +0x40 +0x44 +0x48, allocates 0x4c OID type 0x39 from imposter.cpp, and keeps runtime rendering behavior and rebuild parity unproven",
        ),
        (
            "0x00488a70",
            "CImposter__AddToList",
            "void __thiscall CImposter__AddToList(void * this)",
            "appends this imposter to global singly linked list 0x0067a678 and clears the next pointer; runtime rendering behavior and rebuild parity remain unproven",
        ),
        (
            "0x00488aa0",
            "CImposter__GetFrameHeightForOwnerSlot",
            "float __thiscall CImposter__GetFrameHeightForOwnerSlot(void * this, void * owner)",
            "owner/signature correction from stale CIBuffer label: called by CDXTrees__BuildTreeGeometry, uses owner+0x08 vtable slot +0x6c to choose a frame index, then returns frame-table float at this+0x3c +0x10 + index*0x18; runtime tree rendering behavior remains unproven",
        ),
        (
            "0x00488ac0",
            "ImposterGlobals__ClearTailSlots",
            "void __cdecl ImposterGlobals__ClearTailSlots(void)",
            "recovered static-init table function boundary from data xref 0x006223b4; clears imposter-adjacent globals 0x0067a6b8 through 0x0067a6c0; exact source identity and runtime rendering behavior remain unproven",
        ),
        (
            "0x00488ae0",
            "ImposterGlobals__InitDefaultFrameData",
            "void __cdecl ImposterGlobals__InitDefaultFrameData(void)",
            "recovered static-init table function boundary from data xref 0x006223b8; initializes imposter-adjacent default frame/global data at 0x0067a688 through 0x0067a6b4 with 0.0 and 1.0 float patterns; exact source identity and runtime rendering behavior remain unproven",
        ),
    ]
    write(
        base / "metadata_after.tsv",
        "address\tname\tsignature\tcomment\tstatus\n"
        + "\n".join("\t".join(row) + "\tOK" for row in rows)
        + "\n",
    )
    common = "static-reaudit;imposter-wave415;retail-binary-evidence;"
    write(
        base / "tags_after.tsv",
        "address\tname\ttags\tstatus\n"
        "004888f0\tCImposter__FindOrCreate\t" + common + "imposter;signature-hardened;comment-hardened\tOK\n"
        "00488a70\tCImposter__AddToList\t" + common + "imposter;linked-list;signature-hardened;comment-hardened\tOK\n"
        "00488aa0\tCImposter__GetFrameHeightForOwnerSlot\t" + common + "imposter;owner-corrected;tree-rendering;signature-corrected;comment-hardened\tOK\n"
        "00488ac0\tImposterGlobals__ClearTailSlots\t" + common + "imposter;function-boundary;static-init;comment-hardened\tOK\n"
        "00488ae0\tImposterGlobals__InitDefaultFrameData\t" + common + "imposter;function-boundary;static-init;comment-hardened\tOK\n",
    )
    write(
        base / "xrefs_after.tsv",
        "target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type\n"
        "004888f0\tCImposter__FindOrCreate\t004dc904\t004dc370\tCRTMesh__Init\tUNCONDITIONAL_CALL\n"
        "00488a70\tCImposter__AddToList\t0054402c\t00543f50\tCDXImposter__Create\tUNCONDITIONAL_CALL\n"
        "00488aa0\tCImposter__GetFrameHeightForOwnerSlot\t0055a843\t0055a420\tCDXTrees__BuildTreeGeometry\tUNCONDITIONAL_CALL\n"
        "00488ac0\tImposterGlobals__ClearTailSlots\t006223b4\t<none>\t<no_function>\tDATA\n"
        "00488ae0\tImposterGlobals__InitDefaultFrameData\t006223b8\t<none>\t<no_function>\tDATA\n",
    )
    write(
        base / "instructions_after.tsv",
        "target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type\n"
        "0x00488aa0\t0x00488aa0\tAFTER\t5\t0x00488aad\t0x00488aa0\tCImposter__GetFrameHeightForOwnerSlot\tCALL\tdword ptr [EDX + 0x6c]\tff 52 6c\tCOMPUTED_CALL\n"
        "0x00488aa0\t0x00488aa0\tAFTER\t9\t0x00488ab7\t0x00488aa0\tCImposter__GetFrameHeightForOwnerSlot\tFLD\tfloat ptr [ECX + EAX*0x8 + 0x10]\td9 44 c1 10\tFALL_THROUGH\n"
        "0x00488ac0\t0x00488ac0\tTARGET\t0\t0x00488ac0\t0x00488ac0\tImposterGlobals__ClearTailSlots\tMOV\tdword ptr [0x0067a6b8], 0x0\tc7 05 b8 a6 67 00 00 00 00 00\tFALL_THROUGH\n"
        "0x00488ae0\t0x00488ae0\tAFTER\t5\t0x00488ae3\t0x00488ae0\tImposterGlobals__InitDefaultFrameData\tMOV\tdword ptr [ESP], 0x3f800000\tc7 44 24 00 00 00 80 3f\tFALL_THROUGH\n",
    )


def test_good_fixture_passes() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        assert probe.check_targets(base) == []


def test_stale_cibuffer_owner_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        populate_good_fixture(base)
        text = (base / "metadata_after.tsv").read_text(encoding="utf-8")
        text = text.replace("CImposter__GetFrameHeightForOwnerSlot", "CIBuffer__GetEntryHeightByOwnerSlot")
        (base / "metadata_after.tsv").write_text(text, encoding="utf-8")
        failures = probe.check_targets(base)
        assert any("0x00488aa0 name expected" in failure for failure in failures)


def main() -> int:
    tests = [test_good_fixture_passes, test_stale_cibuffer_owner_fails]
    for test in tests:
        test()
    print(f"PASS {len(tests)}/{len(tests)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
