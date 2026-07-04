#!/usr/bin/env python3
"""Validate Wave959 DiveBomber/Dropship aircraft read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave959-divebomber-dropship-aircraft-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_dive_dropship_aircraft_review_wave959_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DIVE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DiveBomber.cpp" / "_index.md"
DROPSHIP_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Dropship.cpp" / "_index.md"
AIRUNIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "AirUnit.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260528-120725_post_wave959_dive_dropship_aircraft_review_verified"

EXPECTED_METADATA = {
    "0x00445380": ("CDiveBomberAI__scalar_deleting_dtor", "void * __thiscall CDiveBomberAI__scalar_deleting_dtor(void * this, int flags)"),
    "0x004453a0": ("CDiveBomberAI__dtor_base", "void __fastcall CDiveBomberAI__dtor_base(void * this)"),
    "0x00445440": ("CDiveBomberGuide__scalar_deleting_dtor", "void * __thiscall CDiveBomberGuide__scalar_deleting_dtor(void * this, int flags)"),
    "0x00445460": ("CDiveBomberGuide__dtor_base", "void __fastcall CDiveBomberGuide__dtor_base(void * this)"),
    "0x00446d70": ("CDropship__Init", "void __thiscall CDropship__Init(void * this, void * initThing)"),
    "0x00447040": ("CDropshipAI__scalar_deleting_dtor", "void * __thiscall CDropshipAI__scalar_deleting_dtor(void * this, int flags)"),
    "0x00447060": ("CDropshipAI__dtor_base", "void __fastcall CDropshipAI__dtor_base(void * this)"),
    "0x00447100": ("CDropship__dtor_base", "void __fastcall CDropship__dtor_base(void * this)"),
    "0x00447120": ("CDropship__ProcessDoorThrustersAndChildUnits", "void __fastcall CDropship__ProcessDoorThrustersAndChildUnits(void * this)"),
    "0x00448170": ("CDropship__TraceGroundAndSpawnThrusterDust", "void __stdcall CDropship__TraceGroundAndSpawnThrusterDust(void * effectPoint, void * transformMatrix)"),
    "0x00402dd0": ("ShadowHeightfield__AnyBoundsCornerAboveSampledHeight", "int __thiscall ShadowHeightfield__AnyBoundsCornerAboveSampledHeight(void * this)"),
    "0x00445070": ("CDiveBomber__SelectTarget", "void __thiscall CDiveBomber__SelectTarget(void * this, void * out_target_position)"),
    "0x0050eed0": ("CDiveBomber__scalar_deleting_dtor", "void * __thiscall CDiveBomber__scalar_deleting_dtor(void * this, byte delete_flags)"),
    "0x0050ee70": ("CDropship__scalar_deleting_dtor", "void * __thiscall CDropship__scalar_deleting_dtor(void * this, byte delete_flags)"),
    "0x0050f1f0": ("CDropship__Destructor_VFunc01", "void __fastcall CDropship__Destructor_VFunc01(void * this)"),
    "0x0050f2d0": ("CDiveBomber__Destructor_VFunc01", "void __fastcall CDiveBomber__Destructor_VFunc01(void * this)"),
    "0x00496090": ("CMCDropship__Ctor", "void * __thiscall CMCDropship__Ctor(void * this, void * ownerField8)"),
    "0x004960c0": ("CMCDropship__ScalarDeletingDestructor", "void * __thiscall CMCDropship__ScalarDeletingDestructor(void * this, uint flags)"),
    "0x004960e0": ("CMCDropship__Dtor", "void __thiscall CMCDropship__Dtor(void * this)"),
    "0x00496100": ("CMCDropship__VFunc_05_UpdateDoorAnimationValue", "void __thiscall CMCDropship__VFunc_05_UpdateDoorAnimationValue(void * this, void * meshPart, void * doorAnimationValueOut)"),
    "0x00496200": ("CMCDropship__VFunc_08_CheckOwnerStateAndTimeWindow", "bool __thiscall CMCDropship__VFunc_08_CheckOwnerStateAndTimeWindow(void * this)"),
    "0x0050f0a0": ("CAirUnit__ctor_base", "void * __fastcall CAirUnit__ctor_base(void * this)"),
    "0x0050f420": ("CAirUnit__scalar_deleting_dtor", "void * __thiscall CAirUnit__scalar_deleting_dtor(void * this, byte delete_flags)"),
    "0x0050f440": ("CAirUnit__ClearPtrSetsRemoveFromGlobalListAndDestruct", "void __fastcall CAirUnit__ClearPtrSetsRemoveFromGlobalListAndDestruct(void * this)"),
}

COMMENT_TOKENS = {
    "0x00447120": ("dooropening", "doorclosing", "child-unit linked lists", "remain unproven"),
    "0x00448170": ("RET 0x8", "thruster dust", "remain unproven"),
    "0x00445070": ("Wave800", "CCannon__SelectTarget", "single stack output pointer"),
    "0x00402dd0": ("attached-bounds", "CStaticShadows__SampleShadowHeightBilinear", "runtime shadow behavior"),
}

INSTRUCTION_EVIDENCE = (
    ("0x00446d70", "0x00446e96", "CALL", "0x00496090"),
    ("0x00447120", "0x004478a3", "CALL", "0x00402dd0"),
    ("0x00447120", "0x004472b2", "CALL", "0x00448170"),
    ("0x00447120", "0x004473f9", "CALL", "0x00448170"),
    ("0x00447100", "0x00447110", "CALL", "0x00402d30"),
    ("0x0050ee70", "0x0050ee73", "CALL", "0x0050f1f0"),
    ("0x0050eed0", "0x0050eed3", "CALL", "0x0050f2d0"),
    ("0x0050f420", "0x0050f423", "CALL", "0x0050f440"),
    ("0x00445380", "0x0044539d", "RET", "0x4"),
    ("0x00445440", "0x0044545d", "RET", "0x4"),
    ("0x00447040", "0x0044705d", "RET", "0x4"),
    ("0x00448170", "0x0044835c", "RET", "0x8"),
)

XREF_EVIDENCE = (
    ("0x00445380", "0x005db1b0", "<no_function>", "DATA"),
    ("0x00445440", "0x005db184", "<no_function>", "DATA"),
    ("0x00446d70", "0x005e1dfc", "<no_function>", "DATA"),
    ("0x00447040", "0x005db1f8", "<no_function>", "DATA"),
    ("0x00447100", "0x005e1de0", "<no_function>", "DATA"),
    ("0x00447120", "0x005e1ee0", "<no_function>", "DATA"),
    ("0x00448170", "0x004472b2", "CDropship__ProcessDoorThrustersAndChildUnits", "UNCONDITIONAL_CALL"),
    ("0x00448170", "0x004473f9", "CDropship__ProcessDoorThrustersAndChildUnits", "UNCONDITIONAL_CALL"),
    ("0x00402dd0", "0x004478a3", "CDropship__ProcessDoorThrustersAndChildUnits", "UNCONDITIONAL_CALL"),
    ("0x00445070", "0x004fd4e1", "CCannon__SelectTarget", "UNCONDITIONAL_CALL"),
    ("0x00496090", "0x00446e96", "CDropship__Init", "UNCONDITIONAL_CALL"),
    ("0x00496100", "0x005dc318", "<no_function>", "DATA"),
    ("0x00496200", "0x005dc324", "<no_function>", "DATA"),
)

VTABLE_EVIDENCE = (
    ("005e1dfc", "57", "00447120", "CDropship__ProcessDoorThrustersAndChildUnits"),
    ("005dc304", "5", "00496100", "CMCDropship__VFunc_05_UpdateDoorAnimationValue"),
    ("005dc304", "8", "00496200", "CMCDropship__VFunc_08_CheckOwnerStateAndTimeWindow"),
)

STRING_EXPECTATIONS = {
    "string-006289c0.tsv": r"[maintainer-local-source-export-root]\DiveBomber.cpp",
    "string-00628a54.tsv": r"[maintainer-local-source-export-root]\Dropship.cpp",
    "string-00628a74.tsv": "wingflat",
    "string-00628a80.tsv": "doorclosed",
    "string-00628a98.tsv": "dooropening",
    "string-00628a8c.tsv": "doorclosing",
    "string-00628a3c.tsv": "Thruster Dust Effect",
    "string-00623080.tsv": "Thruster",
}

CORE_TOKENS = (
    "Wave959",
    "dive-dropship-aircraft-review-wave959",
    "0x00447120 CDropship__ProcessDoorThrustersAndChildUnits",
    "0x00448170 CDropship__TraceGroundAndSpawnThrusterDust",
    "0x00402dd0 ShadowHeightfield__AnyBoundsCornerAboveSampledHeight",
    "0x00445070 CDiveBomber__SelectTarget",
    "303/1408 = 21.52%",
    "6151/6151 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime dropship door behavior proven",
    "runtime thruster dust behavior proven",
    "runtime dive-bomber targeting proven",
    "source method identity proven",
    "layout proven",
    "rebuild parity proven",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def norm(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    if value in {"", "<none>", "none"}:
        return value
    return "0x" + value.zfill(8)


def bare(address: str) -> str:
    return norm(address).removeprefix("0x")


def contains_token(text: str, token: str) -> bool:
    stripped = text.replace("`", "")
    return token in text or token in stripped or token.replace("\\", "\\\\") in text or token.replace("\\", "\\\\") in stripped


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_artifacts(failures: list[str]) -> None:
    counts = {
        "metadata.tsv": 24,
        "tags.tsv": 24,
        "xrefs.tsv": 31,
        "instructions.tsv": 10296,
        "body-instructions.tsv": 1703,
        "decompile/index.tsv": 24,
        "vtables.tsv": 256,
    }
    for relative, expected in counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count mismatch: {actual} != {expected}", failures)

    metadata = {norm(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {norm(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    decompile = {norm(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}

    for address, (name, signature) in EXPECTED_METADATA.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch at {address}: {row.get('name')}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}: {row.get('status')}", failures)
            for token in COMMENT_TOKENS.get(address, ()):
                require(contains_token(row.get("comment", ""), token), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None and tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)
        dec_row = decompile.get(address)
        require(dec_row is not None and dec_row.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    body_rows = read_tsv(BASE / "body-instructions.tsv")
    for target, instr, mnemonic, operand_token in INSTRUCTION_EVIDENCE:
        hit = any(
            norm(row.get("target_addr", "")) == target
            and norm(row.get("instruction_addr", "")) == instr
            and row.get("mnemonic") == mnemonic
            and operand_token in row.get("operands", "")
            for row in body_rows
        )
        require(hit, f"missing body instruction evidence: {target} {instr} {mnemonic} {operand_token}", failures)

    xrefs = read_tsv(BASE / "xrefs.tsv")
    for target, source, from_function, ref_type in XREF_EVIDENCE:
        hit = any(
            norm(row.get("target_addr", "")) == target
            and norm(row.get("from_addr", "")) == source
            and row.get("from_function") == from_function
            and row.get("ref_type") == ref_type
            for row in xrefs
        )
        require(hit, f"missing xref evidence: {source} -> {target} {from_function} {ref_type}", failures)

    vtables = read_tsv(BASE / "vtables.tsv")
    for vtable, slot, pointer, name in VTABLE_EVIDENCE:
        hit = any(
            row.get("vtable") == vtable
            and row.get("slot_index") == slot
            and row.get("pointer_addr") == pointer
            and row.get("function_name") == name
            and row.get("status") == "OK"
            for row in vtables
        )
        require(hit, f"missing vtable evidence: {vtable} slot {slot} -> {pointer} {name}", failures)

    for filename, expected in STRING_EXPECTATIONS.items():
        rows = read_tsv(BASE / filename)
        require(rows and rows[0].get("cstring") == expected, f"string mismatch in {filename}", failures)

    consult = read_text(BASE / "cursor-consult-wave959.txt")
    lowered_consult = consult.lower()
    require("read-only pass" in lowered_consult, "Cursor consult missing read-only boundary", failures)
    require("wave959 advisory" in lowered_consult, "Cursor consult missing Wave959 advisory marker", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_logs = {
        "metadata.log": "targets=24 found=24 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=24 missing=0",
        "xrefs.log": "Wrote 31 rows",
        "instructions.log": "Wrote 10296 instruction rows",
        "body-instructions.log": "Wrote 1703 function-body instruction rows",
        "decompile.log": "targets=24 dumped=24 missing=0 failed=0",
        "vtables.log": "ExportVtableSlots complete: targets=2 rows=256",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "Invalid script", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173542279, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    docs = [
        NOTE,
        CAMPAIGN,
        GHIDRA_REFERENCE,
        FUNCTION_INDEX,
        DIVE_DOC,
        DROPSHIP_DOC,
        AIRUNIT_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in CORE_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    queue = read_json(QUEUE_JSON)
    require(queue.get("totalFunctions") == 6151, "queue total mismatch", failures)
    quality = queue.get("qualitySignals", {})
    require(quality.get("commentlessFunctionCount") == 0, "commentless count mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "undefined count mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "param_N count mismatch", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-dive-dropship-aircraft-review-wave959")
        == r"py -3 tools\ghidra_dive_dropship_aircraft_review_wave959_probe.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs_and_state(failures)
    if failures:
        print("Wave959 Dive/Dropship aircraft review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave959 Dive/Dropship aircraft review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
