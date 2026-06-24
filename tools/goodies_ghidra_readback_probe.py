#!/usr/bin/env python3
"""Validate read-only Ghidra decompile exports for Goodies 71-73 reachability.

This probe consumes decompile files exported by
``ExportFunctionsByAddressDecompile.java``. It does not launch the game, read or
write BEA.exe directly, mutate a Ghidra project, or apply a rename map.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECOMPILE_DIR = (
    ROOT
    / "subagents"
    / "goodies-71-73-ghidra-readback"
    / "current"
    / "decompile"
)
DEFAULT_OUT = (
    ROOT
    / "subagents"
    / "goodies-71-73-ghidra-readback"
    / "current"
    / "goodies-ghidra-readback.json"
)
DEFAULT_XREF_TSV = (
    ROOT
    / "subagents"
    / "goodies-71-73-ghidra-readback"
    / "current"
    / "goodies-xrefs.tsv"
)
DEFAULT_INSTRUCTION_TSV = (
    ROOT
    / "subagents"
    / "goodies-71-73-ghidra-readback"
    / "current"
    / "goodies-unattributed-instructions.tsv"
)
DEFAULT_UNLOCK_DECOMPILE = (
    ROOT
    / "subagents"
    / "ghidra-goodies-unlock-readback-2026-05-07"
    / "decompile"
    / "0041c470_CCareer__UpdateGoodieStates.c"
)
FEPGOODIES_HEADER = ROOT / "references" / "Onslaught" / "FEPGoodies.h"


@dataclass(frozen=True)
class FunctionExpectation:
    address: str
    name: str
    signature_tokens: tuple[str, ...]
    file_token: str
    required_tokens: tuple[str, ...]
    identity_note: str


@dataclass(frozen=True)
class InstructionContextExpectation:
    address: str
    role: str
    required_tokens: tuple[str, ...]
    identity_note: str
    expected_function_name: str = "CFEPGoodies__ButtonPressed"


@dataclass(frozen=True)
class FieldMapExpectation:
    offset: str
    field_name: str
    meaning: str
    source_tokens: tuple[str, ...]
    decompile_tokens: tuple[str, ...]


EXPECTATIONS: tuple[FunctionExpectation, ...] = (
    FunctionExpectation(
        "0x0045cb80",
        "get_goodie_number",
        ("get_goodie_number", "__cdecl"),
        "0045cb80_get_goodie_number.c",
        (
            "return x + 0x3a;",
            "return 0x4a;",
            "return 0x4b;",
            "return 0x4c;",
            "return (-(uint)(x != 0x10) & 0xffffffb2) + 0x4d;",
            "return x + 0xc9;",
            "return x + 0x4e;",
        ),
        "Retail coordinate mapper returns 66-70, 74-77, 201-232, and 78-200, leaving 71-73 without a normal wall coordinate.",
    ),
    FunctionExpectation(
        "0x0045c9f0",
        "CFEPGoodies__StartLoadingGoody",
        ("CFEPGoodies__StartLoadingGoody", "__fastcall"),
        "0045c9f0_CFEPGoodies__StartLoadingGoody.c",
        (
            "get_goodie_number(*(int *)((int)this + 0x13c),*(int *)((int)this + 0x140))",
            "else if (iVar1 < 0x47)",
            "else if (iVar1 < 0x4a)",
            "else if (iVar1 == 0x4a)",
            "else if (iVar1 == 0x4d)",
        ),
        "Retail loader resolves the selected id from mCX/mCY, while its type split still has an image bucket for 71-73.",
    ),
    FunctionExpectation(
        "0x0045cc10",
        "CFEPGoodies__LoadingGoodyPoll",
        ("CFEPGoodies__LoadingGoodyPoll", "__fastcall"),
        "0045cc10_CFEPGoodies__LoadingGoodyPoll.c",
        (
            "get_goodie_number(*(int *)((int)this + 0x13c),*(int *)((int)this + 0x140))",
            "CFEPGoodies__LoadingGoodyPoll",
        ),
        "Retail async load poll reuses the same selected coordinate id rather than a direct Goodie id parameter.",
    ),
    FunctionExpectation(
        "0x0045cde0",
        "CFEPGoodies__ButtonPressed",
        ("CFEPGoodies__ButtonPressed", "__thiscall", "button", "val"),
        "0045cde0_CFEPGoodies__ButtonPressed.c",
        (
            "void __thiscall CFEPGoodies__ButtonPressed",
            "switch(button)",
            "get_goodie_number(*(int *)((int)this + 0x13c),iVar11)",
            "CFEPGoodies__StartLoadingGoody(this);",
            "(&g_Career_mGoodies)[iVar11] = 3;",
        ),
        "Retail ButtonPressed read-back owns the formerly no-function navigation/selection xrefs and still routes selected Goodies through mCX/mCY coordinates.",
    ),
    FunctionExpectation(
        "0x0045d7e0",
        "CFEPGoodies__Process",
        ("CFEPGoodies__Process", "__thiscall"),
        "0045d7e0_CFEPGoodies__Process.c",
        (
            "CFEPGoodies__LoadingGoodyPoll(this);",
            "get_goodie_number(*(int *)((int)this + 0x13c),*(int *)((int)this + 0x140))",
            "if (iVar7 == 0x4d)",
            "CFEPCommon__StopVideo",
            "CFEPCommon__StartVideo",
        ),
        "Retail process/read-back keeps mCX/mCY as the selection source for FMV, level, and developer/cheat bucket branches; the frontend video restart helpers are CFEPCommon-owned after Wave374.",
    ),
    FunctionExpectation(
        "0x0045ac30",
        "CFEPGoodies__BuildStaticGoodieDataTable",
        ("CFEPGoodies__BuildStaticGoodieDataTable",),
        "0045ac30_CFEPGoodies__BuildStaticGoodieDataTable.c",
        (
            "CFEPGoodies__BuildStaticGoodieDataTable",
            "CGoodieData__ctor(",
        ),
        "Retail static table builder remains named and decompilable; exact 71-73 table semantics are guarded through source and asset metadata.",
    ),
)

INSTRUCTION_CONTEXTS: tuple[InstructionContextExpectation, ...] = (
    InstructionContextExpectation(
        "0x0045ce53",
        "vertical-up-scan",
        (
            "PUSH ESI",
            "CALL 0x0045cb80",
            "CMP EAX, -0x1",
            "DEC ESI",
            "JNS 0x0045ce4b",
        ),
        "Source-correlates with ButtonPressed menu-up scanning mCY upward until get_goodie_number(mCX, ny) is valid.",
    ),
    InstructionContextExpectation(
        "0x0045ce87",
        "vertical-down-scan",
        (
            "CMP ESI, 0x4",
            "CALL 0x0045cb80",
            "CMP EAX, -0x1",
            "INC ESI",
        ),
        "Source-correlates with ButtonPressed menu-down scanning mCY downward until get_goodie_number(mCX, ny) is valid.",
    ),
    InstructionContextExpectation(
        "0x0045cf2a",
        "right-probe-after-clamp",
        (
            "MOV dword ptr [EBX + 0x13c], 0x7a",
            "CALL 0x0045cb80",
            "CMP EAX, -0x1",
        ),
        "Source-correlates with ButtonPressed menu-right clamping mCX to NUM_GOODIES_X_INC - 1 before probing the coordinate.",
    ),
    InstructionContextExpectation(
        "0x0045cf4c",
        "right-backtrack-scan",
        (
            "DEC EAX",
            "MOV dword ptr [EBX + 0x13c], EAX",
            "CALL 0x0045cb80",
            "JZ 0x0045cf37",
        ),
        "Source-correlates with ButtonPressed menu-right backing mCX left while get_goodie_number(mCX, mCY) is invalid.",
    ),
    InstructionContextExpectation(
        "0x0045d03b",
        "selected-state-precheck",
        (
            "PUSH ECX",
            "CALL 0x0045cb80",
            "CMP EAX, -0x1",
            "CMP dword ptr [EAX*0x4 + 0x662564], 0x2",
        ),
        "Source-correlates with selection-state checks over the current mCX/mCY coordinate before load/display handling.",
    ),
    InstructionContextExpectation(
        "0x0045d070",
        "selected-load-gate",
        (
            "MOV EAX, dword ptr [EBX + 0x140]",
            "MOV ECX, dword ptr [EBX + 0x13c]",
            "CALL 0x0045cb80",
            "CMP dword ptr [EAX*0x4 + 0x662564], 0x3",
            "CALL 0x0045c9f0",
        ),
        "Source-correlates with the select path: validate current coordinate state, then call StartLoadingGoody.",
    ),
    InstructionContextExpectation(
        "0x0045d0be",
        "post-load-state-check",
        (
            "CALL 0x0045c9f0",
            "PUSH ESI",
            "PUSH EDI",
            "CALL 0x0045cb80",
            "CMP EAX, -0x1",
        ),
        "Source-correlates with the selected coordinate being re-read immediately after StartLoadingGoody.",
    ),
    InstructionContextExpectation(
        "0x0045d0cd",
        "mark-selected-old",
        (
            "CALL 0x0045cb80",
            "MOV dword ptr [EAX*0x4 + 0x662564], 0x3",
        ),
        "Source-correlates with set_goodie_state(mCX, mCY, GS_OLD) after the selected Goodie is opened.",
    ),
)

UNLOCK_READBACK_TOKENS: tuple[str, ...] = (
    "CCareer__UpdateGoodieStates",
    "CCareer__GetGoodiePtr(this_00,0x47)",
    "CCareer__GetGoodiePtr(this_00,0x48)",
    "CCareer__GetGoodiePtr(this_00,0x49)",
)

TARGET_GOODIE_CONSTANT_TOKENS: tuple[str, ...] = ("0x47", "0x48", "0x49")

SELECTION_TARGET_CONSTANT_FILES: tuple[tuple[str, str], ...] = (
    (
        "0045cde0_CFEPGoodies__ButtonPressed.c",
        "ButtonPressed input/selection handling",
    ),
    (
        "0045d7e0_CFEPGoodies__Process.c",
        "Process display/update handling",
    ),
    (
        "0045cc10_CFEPGoodies__LoadingGoodyPoll.c",
        "LoadingGoodyPoll async selected-load handling",
    ),
)

FIELD_MAP_EXPECTATIONS: tuple[FieldMapExpectation, ...] = (
    FieldMapExpectation(
        "0x13c",
        "mCX",
        "current Goodies wall grid X coordinate",
        ("SINT\tmCX, mCY;",),
        ("((int)this + 0x13c)", "dword ptr [EBX + 0x13c]"),
    ),
    FieldMapExpectation(
        "0x140",
        "mCY",
        "current Goodies wall grid Y coordinate",
        ("SINT\tmCX, mCY;",),
        ("((int)this + 0x140)", "dword ptr [EBX + 0x140]"),
    ),
    FieldMapExpectation(
        "0x154",
        "mCurrentGoodyType",
        "selected Goodie content type bucket",
        ("EGoodieType\tmCurrentGoodyType;",),
        ("((int)this + 0x154)", "*(uint *)((int)this + 0x154) = uVar2;"),
    ),
    FieldMapExpectation(
        "0x1d8",
        "mGoodyState",
        "resource load state for the current Goodie preview",
        ("EGoodyState mGoodyState;",),
        ("((int)this + 0x1d8)", "*(undefined4 *)((int)this + 0x1d8) = 2;"),
    ),
)


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def line_hits(lines: list[str], tokens: tuple[str, ...]) -> dict[str, list[int]]:
    return {
        token: [index + 1 for index, line in enumerate(lines) if token in line]
        for token in tokens
    }


def parse_index(index_path: Path) -> dict[tuple[str, str], dict[str, str]]:
    rows: dict[tuple[str, str], dict[str, str]] = {}
    if not index_path.is_file():
        return rows
    for line in index_path.read_text(encoding="utf-8", errors="replace").splitlines()[1:]:
        cells = line.split("\t")
        if len(cells) < 4:
            continue
        address, name, signature, status = cells[:4]
        rows[(address.lower(), name)] = {
            "address": address,
            "name": name,
            "signature": signature,
            "status": status,
        }
    return rows


def parse_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines:
        return []
    headers = lines[0].split("\t")
    rows: list[dict[str, str]] = []
    for line in lines[1:]:
        cells = line.split("\t")
        rows.append({header: cells[index] if index < len(cells) else "" for index, header in enumerate(headers)})
    return rows


def summarize_expectation(
    expectation: FunctionExpectation,
    decompile_dir: Path,
    index_rows: dict[tuple[str, str], dict[str, str]],
) -> dict[str, object]:
    row = index_rows.get((expectation.address.lower(), expectation.name))
    row_failures: list[str] = []
    if row is None:
        row_failures.append("missing index row")
        row = {
            "address": expectation.address,
            "name": expectation.name,
            "signature": "",
            "status": "MISSING",
        }
    if row.get("status") != "OK":
        row_failures.append(f"index status is {row.get('status')}")

    signature_hits = {
        token: token in row.get("signature", "")
        for token in expectation.signature_tokens
    }
    missing_signature_tokens = [
        token for token, present in signature_hits.items() if not present
    ]

    decompile_path = decompile_dir / expectation.file_token
    decompile_failures: list[str] = []
    token_hits: dict[str, list[int]] = {}
    if not decompile_path.is_file():
        decompile_failures.append("missing decompile file")
    else:
        token_hits = line_hits(read_lines(decompile_path), expectation.required_tokens)
        decompile_failures.extend(
            f"missing token: {token}"
            for token, hits in token_hits.items()
            if not hits
        )

    status = (
        "PASS"
        if not row_failures and not missing_signature_tokens and not decompile_failures
        else "FAIL"
    )
    return {
        "address": expectation.address,
        "name": expectation.name,
        "status": status,
        "identityNote": expectation.identity_note,
        "indexStatus": row.get("status"),
        "signatureTokenPresence": signature_hits,
        "missingSignatureTokens": missing_signature_tokens,
        "decompileFile": relative(decompile_path),
        "tokenLineHits": token_hits,
        "rowFailures": row_failures,
        "decompileFailures": decompile_failures,
    }


def summarize_xrefs(xref_tsv: Path) -> dict[str, object]:
    rows = parse_tsv(xref_tsv)
    expected_named_callers = {
        "CFEPGoodies__ButtonPressed",
        "CFEPGoodies__StartLoadingGoody",
        "CFEPGoodies__LoadingGoodyPoll",
        "CFEPGoodies__Process",
    }
    named_callers = {
        row.get("from_function", "")
        for row in rows
        if row.get("from_function") not in {"", "<none>", "<no_function>"}
    }
    missing_named_callers = sorted(expected_named_callers - named_callers)
    unattributed_rows = [
        row
        for row in rows
        if row.get("from_function") in {"<none>", "<no_function>"}
        or row.get("from_function_addr") in {"<none>", ""}
    ]
    non_call_rows = [
        row for row in rows if row.get("ref_type") != "UNCONDITIONAL_CALL"
    ]
    failures: list[str] = []
    if not xref_tsv.is_file():
        failures.append("missing xref TSV")
    if missing_named_callers:
        failures.append("missing expected named callers")
    if non_call_rows:
        failures.append("non-call xref rows present")
    return {
        "status": "PASS" if not failures else "FAIL",
        "xrefFile": relative(xref_tsv),
        "rowCount": len(rows),
        "targetNames": sorted({row.get("target_name", "") for row in rows}),
        "namedCallers": sorted(named_callers),
        "missingNamedCallers": missing_named_callers,
        "unattributedRowCount": len(unattributed_rows),
        "unattributedFromAddresses": [
            row.get("from_addr", "") for row in unattributed_rows
        ],
        "nonCallRowCount": len(non_call_rows),
        "failures": failures,
    }


def instruction_text(row: dict[str, str]) -> str:
    return " ".join(
        [
            row.get("mnemonic", ""),
            row.get("operands", ""),
            row.get("flow_type", ""),
        ]
    )


def summarize_instruction_contexts(instruction_tsv: Path) -> dict[str, object]:
    rows = parse_tsv(instruction_tsv)
    rows_by_target: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        target = row.get("target_addr", "").lower()
        if target:
            rows_by_target.setdefault(target, []).append(row)

    contexts: list[dict[str, object]] = []
    failures: list[str] = []
    if not instruction_tsv.is_file():
        failures.append("missing instruction TSV")

    for expected in INSTRUCTION_CONTEXTS:
        target_rows = rows_by_target.get(expected.address.lower(), [])
        joined = "\n".join(instruction_text(row) for row in target_rows)
        missing_tokens = [
            token for token in expected.required_tokens if token not in joined
        ]
        target_rows_at_zero = [
            row for row in target_rows if row.get("role") == "TARGET"
        ]
        target_function_names = sorted(
            {
                row.get("function_name", "")
                for row in target_rows_at_zero
            }
        )
        target_call_rows = [
            row
            for row in target_rows_at_zero
            if row.get("mnemonic") == "CALL"
            and row.get("operands") == "0x0045cb80"
        ]
        if missing_tokens:
            failures.append(f"{expected.address} missing expected instruction tokens")
        if not target_call_rows:
            failures.append(f"{expected.address} target row is not a get_goodie_number call")
        if expected.expected_function_name not in target_function_names:
            failures.append(f"{expected.address} not contained by {expected.expected_function_name}")
        contexts.append(
            {
                "address": expected.address,
                "role": expected.role,
                "status": (
                    "PASS"
                    if not missing_tokens
                    and target_call_rows
                    and expected.expected_function_name in target_function_names
                    else "FAIL"
                ),
                "identityNote": expected.identity_note,
                "rowCount": len(target_rows),
                "missingTokens": missing_tokens,
                "expectedFunctionName": expected.expected_function_name,
                "targetFunctionNames": target_function_names,
            }
        )

    unexpected_targets = sorted(
        set(rows_by_target) - {expected.address.lower() for expected in INSTRUCTION_CONTEXTS}
    )
    if unexpected_targets:
        failures.append("unexpected instruction target addresses")

    return {
        "status": "PASS" if not failures else "FAIL",
        "instructionFile": relative(instruction_tsv),
        "rowCount": len(rows),
        "contextCount": len(contexts),
        "passedContextCount": sum(1 for context in contexts if context["status"] == "PASS"),
        "unexpectedTargets": unexpected_targets,
        "failures": failures,
        "contexts": contexts,
    }


def summarize_unlock_readback(unlock_decompile: Path) -> dict[str, object]:
    failures: list[str] = []
    token_hits: dict[str, list[int]] = {}
    if not unlock_decompile.is_file():
        failures.append("missing unlock decompile file")
    else:
        token_hits = line_hits(read_lines(unlock_decompile), UNLOCK_READBACK_TOKENS)
        failures.extend(
            f"missing token: {token}"
            for token, hits in token_hits.items()
            if not hits
        )
    return {
        "status": "PASS" if not failures else "FAIL",
        "decompileFile": relative(unlock_decompile),
        "identityNote": "Retail UpdateGoodieStates decompile read-back includes Goodie 71-73 pointer constants 0x47, 0x48, and 0x49, matching the source unlock branch.",
        "tokenLineHits": token_hits,
        "failures": failures,
    }


def summarize_field_map(decompile_dir: Path) -> dict[str, object]:
    failures: list[str] = []
    if not FEPGOODIES_HEADER.is_file():
        return {
            "status": "FAIL",
            "sourceFile": relative(FEPGOODIES_HEADER),
            "fields": [],
            "failures": ["missing FEPGoodies.h"],
        }

    source_text = FEPGOODIES_HEADER.read_text(encoding="utf-8", errors="replace")
    selected_files = [
        decompile_dir / "0045c9f0_CFEPGoodies__StartLoadingGoody.c",
        decompile_dir / "0045cde0_CFEPGoodies__ButtonPressed.c",
        decompile_dir / "0045d7e0_CFEPGoodies__Process.c",
        decompile_dir.parent / "goodies-unattributed-instructions.tsv",
    ]
    decompile_text_parts: list[str] = []
    missing_files: list[str] = []
    for path in selected_files:
        if path.is_file():
            decompile_text_parts.append(path.read_text(encoding="utf-8", errors="replace"))
        else:
            missing_files.append(relative(path))
    if missing_files:
        failures.extend(f"missing field-map input: {path}" for path in missing_files)
    decompile_text = "\n".join(decompile_text_parts)

    fields: list[dict[str, object]] = []
    for expected in FIELD_MAP_EXPECTATIONS:
        missing_source = [
            token for token in expected.source_tokens if token not in source_text
        ]
        missing_decompile = [
            token for token in expected.decompile_tokens if token not in decompile_text
        ]
        field_status = "PASS" if not missing_source and not missing_decompile else "FAIL"
        if field_status != "PASS":
            failures.append(f"{expected.offset} {expected.field_name} field-map evidence incomplete")
        fields.append(
            {
                "offset": expected.offset,
                "fieldName": expected.field_name,
                "meaning": expected.meaning,
                "status": field_status,
                "missingSourceTokens": missing_source,
                "missingDecompileTokens": missing_decompile,
            }
        )

    return {
        "status": "PASS" if not failures else "FAIL",
        "sourceFile": relative(FEPGOODIES_HEADER),
        "inputFiles": [relative(path) for path in selected_files],
        "fields": fields,
        "failures": failures,
    }


def summarize_selection_target_constants(decompile_dir: Path) -> dict[str, object]:
    failures: list[str] = []
    files: list[dict[str, object]] = []
    total_hits = 0
    for file_name, role in SELECTION_TARGET_CONSTANT_FILES:
        path = decompile_dir / file_name
        if not path.is_file():
            failures.append(f"missing selection constant input: {relative(path)}")
            files.append(
                {
                    "file": relative(path),
                    "role": role,
                    "status": "FAIL",
                    "targetConstantHits": {},
                    "hitCount": 0,
                }
            )
            continue
        hits = line_hits(read_lines(path), TARGET_GOODIE_CONSTANT_TOKENS)
        hit_count = sum(len(lines) for lines in hits.values())
        total_hits += hit_count
        if hit_count:
            failures.append(f"{file_name} contains direct 71-73 target constants")
        files.append(
            {
                "file": relative(path),
                "role": role,
                "status": "PASS" if hit_count == 0 else "FAIL",
                "targetConstantHits": hits,
                "hitCount": hit_count,
            }
        )

    return {
        "status": "PASS" if not failures else "FAIL",
        "targetConstants": list(TARGET_GOODIE_CONSTANT_TOKENS),
        "totalHitCount": total_hits,
        "identityNote": (
            "ButtonPressed, Process, and LoadingGoodyPoll read-back currently "
            "contain no direct 0x47/0x48/0x49 constants; selected rows still "
            "flow through get_goodie_number(mCX, mCY)."
        ),
        "files": files,
        "failures": failures,
    }


def build_report(
    decompile_dir: Path,
    xref_tsv: Path,
    instruction_tsv: Path,
    unlock_decompile: Path,
) -> dict[str, object]:
    index_rows = parse_index(decompile_dir / "index.tsv")
    functions = [
        summarize_expectation(expectation, decompile_dir, index_rows)
        for expectation in EXPECTATIONS
    ]
    failed = [fn["name"] for fn in functions if fn["status"] != "PASS"]
    xrefs = summarize_xrefs(xref_tsv)
    instruction_contexts = summarize_instruction_contexts(instruction_tsv)
    unlock_readback = summarize_unlock_readback(unlock_decompile)
    field_map = summarize_field_map(decompile_dir)
    selection_target_constants = summarize_selection_target_constants(decompile_dir)
    return {
        "schema": "goodies-ghidra-readback.v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "decompileDir": relative(decompile_dir),
        "status": (
            "PASS"
            if not failed
            and xrefs["status"] == "PASS"
            and instruction_contexts["status"] == "PASS"
            and unlock_readback["status"] == "PASS"
            and field_map["status"] == "PASS"
            and selection_target_constants["status"] == "PASS"
            else "FAIL"
        ),
        "summary": {
            "functionCount": len(functions),
            "passedFunctions": len(functions) - len(failed),
            "failedFunctions": len(failed),
            "failedFunctionNames": failed,
            "xrefStatus": xrefs["status"],
            "instructionContextStatus": instruction_contexts["status"],
            "unlockReadbackStatus": unlock_readback["status"],
            "fieldMapStatus": field_map["status"],
            "selectionTargetConstantStatus": selection_target_constants["status"],
        },
        "safety": {
            "launchesGame": False,
            "readsOrWritesOriginalExe": False,
            "mutatesGhidraProject": False,
            "appliesRenameMap": False,
            "writesPrivateAssetOutputs": False,
            "requiresIgnoredDecompileInput": True,
        },
        "currentClaims": [
            "Retail get_goodie_number read-back leaves 71-73 without a normal Goodies wall coordinate.",
            "Retail StartLoadingGoody and LoadingGoodyPoll read selected ids through mCX/mCY.",
            "Retail StartLoadingGoody still has a content-type bucket covering ids 71-73.",
            "Retail Process read-back uses mCX/mCY for FMV, level, and developer/cheat branches.",
            "Retail xrefs to get_goodie_number include the expected named frontend Goodies callers.",
            "Formerly unattributed get_goodie_number xref rows now read back under CFEPGoodies__ButtonPressed and source-correlate with Goodies wall navigation, selected-coordinate load gates, and selected-state updates.",
            "ButtonPressed, Process, and LoadingGoodyPoll read-back contain no direct 0x47/0x48/0x49 target constants.",
            "Retail UpdateGoodieStates read-back includes Goodie 71-73 pointer constants matching the source unlock branch.",
            "Selected CFEPGoodies field offsets now have source-correlated names for current grid X, current grid Y, current Goodie type, and current Goodie load state.",
        ],
        "notClaimed": [
            "This probe does not launch BEA.exe.",
            "This probe does not mutate Ghidra names, signatures, or comments.",
            "This probe does not prove there is no hidden runtime path for 71-73.",
            "This probe verifies selected CFEPGoodies field offsets by source/decompile correlation, but does not mutate Ghidra field types or harden every local variable.",
            "This probe does not inspect private screenshot or extracted asset payloads.",
        ],
        "functions": functions,
        "xrefs": xrefs,
        "instructionContexts": instruction_contexts,
        "unlockReadback": unlock_readback,
        "fieldMap": field_map,
        "selectionTargetConstants": selection_target_constants,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--decompile-dir", type=Path, default=DEFAULT_DECOMPILE_DIR)
    parser.add_argument("--xref-tsv", type=Path, default=DEFAULT_XREF_TSV)
    parser.add_argument("--instruction-tsv", type=Path, default=DEFAULT_INSTRUCTION_TSV)
    parser.add_argument("--unlock-decompile", type=Path, default=DEFAULT_UNLOCK_DECOMPILE)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero when any expectation fails.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    report = build_report(
        args.decompile_dir,
        args.xref_tsv,
        args.instruction_tsv,
        args.unlock_decompile,
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"{report['status']}: wrote {relative(args.out)}")
    print(
        "functions: "
        f"{report['summary']['passedFunctions']}/{report['summary']['functionCount']} passing"
    )
    print(
        "instruction contexts: "
        f"{report['instructionContexts']['passedContextCount']}/"
        f"{report['instructionContexts']['contextCount']} passing"
    )
    print(f"unlock read-back: {report['unlockReadback']['status']}")
    print(f"field map: {report['fieldMap']['status']}")
    print(
        "selection target constants: "
        f"{report['selectionTargetConstants']['status']} "
        f"hits={report['selectionTargetConstants']['totalHitCount']}"
    )
    if args.check and report["status"] != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
