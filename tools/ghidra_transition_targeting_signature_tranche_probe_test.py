#!/usr/bin/env python3
"""Self-tests for the transition/targeting Ghidra signature tranche probe."""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

import ghidra_transition_targeting_signature_tranche_probe as probe


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_tsv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def make_fixture(root: Path, *, stale_math_owner: bool = False) -> dict[str, Path]:
    decomp = root / "decompile_final"
    metadata_rows = []
    index_rows = []
    xref_rows = []
    instruction_rows = []

    signatures = {
        "0x0040a580": "void __fastcall CBattleEngine__Morph(void * battleEngine)",
        "0x0040ac50": "void __thiscall CBattleEngine__Rearm(void * this, float inAmount)",
        "0x0040acc0": "void * __thiscall CBattleEngine__CalcUnitOverCrossHair(void * this, void * event, int useMeshCollision, int updateReaders)",
        "0x0040b100": "void __fastcall CGeneralVolume__ctor_base(void * generalVolume)",
        "0x0040b120": "void __fastcall CBattleEngine__UpdateAutoAim(void * battleEngine)",
        "0x0040b660": "float __cdecl AngleDifference(float currentAngle, float targetAngle)",
        "0x0040b6d0": "void __thiscall CBattleEngine__HandleAutoAim(void * this, void * event)",
    }
    if stale_math_owner:
        signatures["0x0040b660"] = "float __cdecl CGeneralVolume__GetWrappedDeltaSigned(float currentAngle, float targetAngle)"

    comments = {
        "0x0040a580": "Source bridge/name correction: body matches Stuart CBattleEngine::Morph() by state gates, special-move lockouts, events 0x1771 / 6000, flytowalk/walktofly, and audio hooks. Runtime behavior and concrete layout remain unproven.",
        "0x0040ac50": "Source bridge/name correction: ret 0x4 and body match Stuart CBattleEngine::Rearm(float inAmount), iterating six stores and skipping heated stores. Runtime behavior and concrete layout remain unproven.",
        "0x0040acc0": "Source bridge/name correction: ret 0xc and body match Stuart CBattleEngine::CalcUnitOverCrossHair with view ray, mesh/outer-sphere selection, and event 0x1772. Runtime behavior and concrete layout remain unproven.",
        "0x0040b100": "Owner/name correction: body installs the CGeneralVolume vtable and zeroes +0x4/+0x8/+0xc; ResolveVtableTypeNames confirms CGeneralVolume RTTI. Runtime behavior and concrete layout remain unproven.",
        "0x0040b120": "Source bridge/name correction: body matches Stuart CBattleEngine::UpdateAutoAim and smooths +0x4e8/+0x4f4 using AngleDifference. Runtime behavior and rebuild parity remain unproven.",
        "0x0040b660": "Source bridge/name correction: free math helper matches Stuart AngleDifference signed wrapped angular delta from two float inputs and is not CGeneralVolume-owned. Runtime behavior, tags, and rebuild parity remain unproven.",
        "0x0040b6d0": "Source bridge/name correction: ret 0x4 and body match Stuart CBattleEngine::HandleAutoAim(CEvent *) with target reader +0x4e0, MapWho, line trace, and event 0x1773 context. Runtime behavior remains unproven.",
    }

    names = {
        "0x0040a580": "CBattleEngine__Morph",
        "0x0040ac50": "CBattleEngine__Rearm",
        "0x0040acc0": "CBattleEngine__CalcUnitOverCrossHair",
        "0x0040b100": "CGeneralVolume__ctor_base",
        "0x0040b120": "CBattleEngine__UpdateAutoAim",
        "0x0040b660": "AngleDifference" if not stale_math_owner else "CGeneralVolume__GetWrappedDeltaSigned",
        "0x0040b6d0": "CBattleEngine__HandleAutoAim",
    }

    decompile_tokens = {
        "0x0040a580": "battleEngine +0x260 CGeneralVolume__BeginFlyToWalkTransition CGeneralVolume__BeginWalkToFlyTransition s_flytowalk s_walktofly CBattleEngine__SwapPrimarySecondaryPartReadersForState",
        "0x0040ac50": "this inAmount +0x52c +0x4b0",
        "0x0040acc0": "this event useMeshCollision updateReaders CPlayer__GetCurrentViewPoint CPlayer__GetCurrentViewOrientation OID__TraceLineAndSelectBestTargetHit CEventManager__AddEvent_AtTime 0x1772",
        "0x0040b100": "generalVolume PTR_LAB_005d892c",
        "0x0040b120": "battleEngine +0x4e4 +0x4f0 CUnitAI__GetWorldPositionForTargeting AngleDifference",
        "0x0040b660": "currentAngle targetAngle _DAT_005d85e0",
        "0x0040b6d0": "this event CGenericActiveReader__SetReader CUnit__ComputeMinBallisticTravelDistance CUnit__ComputeMaxBallisticTravelDistance OID__TraceLineAndSelectBestTargetHit CEventManager__AddEvent_AtTime",
    }

    for address in probe.TARGETS:
        name = names[address]
        metadata_rows.append({
            "address": address,
            "name": name,
            "signature": signatures[address],
            "comment": comments[address],
            "status": "OK",
        })
        index_rows.append({"address": address, "name": name, "signature": signatures[address], "status": "OK"})
        xref_rows.append({
            "target_addr": address,
            "target_name": name,
            "from_addr": "00400000",
            "from_function_addr": "00400000",
            "from_function": "Fixture__Caller",
            "ref_type": "UNCONDITIONAL_CALL",
        })
        instruction_rows.append({
            "target_raw": address,
            "target_addr": address,
            "role": "AFTER",
            "ordinal": "1",
            "instruction_addr": address,
            "function_entry": address,
            "function_name": name,
            "mnemonic": "RET",
            "operands": probe.TARGETS[address]["instructionRet"],
            "bytes": "c2 04 00" if probe.TARGETS[address]["instructionRet"] == "0x4" else "c3",
            "flow_type": "TERMINATOR",
        })
        write_text(decomp / f"{address[2:]}_{name}.c", decompile_tokens[address])

    write_tsv(root / "metadata_final.tsv", metadata_rows, ["address", "name", "signature", "comment", "status"])
    write_tsv(root / "decompile_final" / "index.tsv", index_rows, ["address", "name", "signature", "status"])
    write_tsv(root / "xrefs_final.tsv", xref_rows, ["target_addr", "target_name", "from_addr", "from_function_addr", "from_function", "ref_type"])
    write_tsv(root / "instructions_final.tsv", instruction_rows, ["target_raw", "target_addr", "role", "ordinal", "instruction_addr", "function_entry", "function_name", "mnemonic", "operands", "bytes", "flow_type"])
    write_tsv(root / "vtables_final.tsv", [
        {
            "vtable": "005d892c",
            "col_ptr_slot": "005d8928",
            "col_addr": "0060c658",
            "signature": "0x00000000",
            "offset": "0",
            "cd_offset": "0",
            "type_desc": "0x00622f10",
            "class_desc": "0x0060c648",
            "raw_type_name": ".?AVCGeneralVolume@@",
            "demangled_type_name": "CGeneralVolume",
        },
    ], ["vtable", "col_ptr_slot", "col_addr", "signature", "offset", "cd_offset", "type_desc", "class_desc", "raw_type_name", "demangled_type_name"])
    write_text(root / "signature_dry.log", "--- SUMMARY ---\nupdated=0 skipped=7 missing=0 bad=0\n")
    write_text(root / "signature_apply.log", "--- SUMMARY ---\nupdated=7 skipped=0 missing=0 bad=0\n")

    return {
        "dry_log_path": root / "signature_dry.log",
        "apply_log_path": root / "signature_apply.log",
        "metadata_path": root / "metadata_final.tsv",
        "decompile_index_path": root / "decompile_final" / "index.tsv",
        "decompile_dir": decomp,
        "xrefs_path": root / "xrefs_final.tsv",
        "instructions_path": root / "instructions_final.tsv",
        "vtables_path": root / "vtables_final.tsv",
    }


def test_pass_fixture() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        paths = make_fixture(Path(tmp))
        report = probe.build_report(**paths)
        assert report["status"] == "PASS", report["failures"]
        assert report["summary"]["renamedTargets"] == 7
        assert report["summary"]["retEvidenceHits"] == 7


def test_stale_math_owner_fails() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        paths = make_fixture(Path(tmp), stale_math_owner=True)
        report = probe.build_report(**paths)
        assert report["status"] == "FAIL"
        assert any("0x0040b660" in failure for failure in report["failures"])


if __name__ == "__main__":
    test_pass_fixture()
    test_stale_math_owner_fails()
    print("PASS: ghidra_transition_targeting_signature_tranche_probe_test (2/2)")
