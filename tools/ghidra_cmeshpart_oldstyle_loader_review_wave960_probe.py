#!/usr/bin/env python3
"""Validate Wave960 CMeshPart old-style loader read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave960-cmeshpart-oldstyle-loader-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cmeshpart_oldstyle_loader_review_wave960_2026-05-28.md"
PACKAGE_JSON = ROOT / "package.json"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
MESHPART_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "MeshPart.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260528-123300_post_wave960_cmeshpart_oldstyle_loader_review_verified"

EXPECTED_METADATA = {
    "0x004a5b70": ("CMesh__Load", "int __thiscall CMesh__Load(void * this, void * mem_buffer, void * load_context)"),
    "0x004adf80": ("CMesh__ClearField08", "void __thiscall CMesh__ClearField08(void * this)"),
    "0x004ae640": ("CMeshPart__FreeOwnedResourcePointers", "void __thiscall CMeshPart__FreeOwnedResourcePointers(void * this)"),
    "0x004aede0": ("CMeshPart__LoadOldStyle_VersionA", "int __thiscall CMeshPart__LoadOldStyle_VersionA(void * this, void * mem_buffer, void * parent_mesh, void * mesh_resource_records, int material_index_limit, int legacy_flags_or_zero)"),
    "0x004af110": ("CMeshPart__LoadOldStyle_VersionB_WithExtraBlock", "int __thiscall CMeshPart__LoadOldStyle_VersionB_WithExtraBlock(void * this, void * mem_buffer, void * parent_mesh, void * mesh_resource_records, int material_index_limit, int legacy_flags_or_zero)"),
    "0x004af470": ("CMeshPart__LoadVerticesAndTriangles", "void __thiscall CMeshPart__LoadVerticesAndTriangles(void * this, void * mem_buffer, void * part_table_entry, void * first_part_record, int part_index_limit, int unused_legacy_arg)"),
    "0x004afbb0": ("CMeshPart__LoadVerticesWithBones", "void __thiscall CMeshPart__LoadVerticesWithBones(void * this, void * mem_buffer, void * parent_mesh, int unused_arg3, int part_index_limit, int unused_arg5, int influence_count, int format_tag)"),
    "0x004b27a0": ("CMeshPart__LoadFromStream", "void * __cdecl CMeshPart__LoadFromStream(void * chunk_reader, void * mesh_part, void * parent_mesh)"),
    "0x004b3180": ("CMeshPart__LoadMaterial", "void * __cdecl CMeshPart__LoadMaterial(void * chunk_reader, void * existing_material)"),
}

COMMENT_TOKENS = {
    "0x004aede0": ("Wave815", "old-style CMeshPart loader", "RET 0x14", "0x60-byte vertex/material records"),
    "0x004af110": ("Wave815", "extra 4-byte block", "RET 0x14", "+0xb8"),
    "0x004af470": ("Wave449", "loads non-skinned", "ret 0x14"),
    "0x004afbb0": ("Wave449", "loads skinned", "ret 0x1c"),
}

INSTRUCTION_EVIDENCE = (
    ("0x004a5b70", "0x004a8f05", "CALL", "0x004aede0"),
    ("0x004a5b70", "0x004a8f49", "CALL", "0x004af110"),
    ("0x004a5b70", "0x004a8f5c", "CALL", "0x004af470"),
    ("0x004aede0", "0x004af101", "CALL", "0x004b1eb0"),
    ("0x004aede0", "0x004af10d", "RET", "0x14"),
    ("0x004af110", "0x004af456", "CALL", "0x004b1eb0"),
    ("0x004af110", "0x004af462", "RET", "0x14"),
    ("0x004af470", "0x004afba5", "RET", "0x14"),
    ("0x004afbb0", "0x004b07f0", "RET", "0x1c"),
)

XREF_EVIDENCE = (
    ("0x004aede0", "0x004a8f05", "CMesh__Load", "UNCONDITIONAL_CALL"),
    ("0x004af110", "0x004a8f49", "CMesh__Load", "UNCONDITIONAL_CALL"),
    ("0x004af470", "0x004a8f5c", "CMesh__Load", "UNCONDITIONAL_CALL"),
    ("0x004afbb0", "0x004a841d", "CMesh__Load", "UNCONDITIONAL_CALL"),
    ("0x004b3180", "0x004b2cf1", "CMeshPart__LoadFromStream", "UNCONDITIONAL_CALL"),
)

STRING_EXPECTATIONS = {
    "string-0062fe70.tsv": r"C:\dev\ONSLAUGHT2\MeshPart.cpp",
    "string-0062fc48.tsv": "2.01",
    "string-0062fc40.tsv": "2.02",
    "string-0062fc38.tsv": "2.03",
    "string-0062ff48.tsv": "2.06",
    "string-00630038.tsv": "HORI",
}

CORE_TOKENS = (
    "Wave960",
    "cmeshpart-oldstyle-loader-review-wave960",
    "0x004aede0 CMeshPart__LoadOldStyle_VersionA",
    "0x004af110 CMeshPart__LoadOldStyle_VersionB_WithExtraBlock",
    "0x004a8f05",
    "0x004a8f49",
    "0x004af10d RET 0x14",
    "0x004af462 RET 0x14",
    r"C:\dev\ONSLAUGHT2\MeshPart.cpp",
    "2.01",
    "2.02",
    "2.03",
    "2.06",
    "HORI",
    "305/1408 = 21.66%",
    "6151/6151 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "old mesh-format schema proven",
    "runtime mesh loading proven",
    "runtime render behavior proven",
    "layout proven",
    "source method identity proven",
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


def contains_token(text: str, token: str) -> bool:
    stripped = text.replace("`", "")
    return token in text or token in stripped or token.replace("\\", "\\\\") in text or token.replace("\\", "\\\\") in stripped


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_artifacts(failures: list[str]) -> None:
    counts = {
        "metadata.tsv": 9,
        "tags.tsv": 9,
        "xrefs.tsv": 15,
        "instructions.tsv": 729,
        "body-instructions.tsv": 7254,
        "decompile/index.tsv": 9,
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
        require(tags.get(address, {}).get("status") == "OK", f"tag status mismatch at {address}", failures)
        require(decompile.get(address, {}).get("status") == "OK", f"decompile status mismatch at {address}", failures)

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

    for filename, expected in STRING_EXPECTATIONS.items():
        rows = read_tsv(BASE / filename)
        require(rows and rows[0].get("cstring") == expected, f"string mismatch in {filename}", failures)

    consult = read_text(BASE / "cursor-consult-wave960.txt").lower()
    require("wave960 advisory" in consult, "Cursor consult missing Wave960 marker", failures)
    require("read-only" in consult and "no mutation" in consult, "Cursor consult missing read-only/no-mutation boundary", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_logs = {
        "metadata.log": "targets=9 found=9 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=9 missing=0",
        "xrefs.log": "Wrote 15 rows",
        "instructions.log": "Wrote 729 instruction rows",
        "body-instructions.log": "Wrote 7254 function-body instruction rows",
        "decompile.log": "targets=9 dumped=9 missing=0 failed=0",
    }
    for relative, token in expected_logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "Invalid script", "Usage:", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 173542279, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    docs = [NOTE, CAMPAIGN, GHIDRA_REFERENCE, FUNCTION_INDEX, MESHPART_DOC, DEVELOPER_STATE, DOCUMENTATION_STATE, RE_STATE]
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
        scripts.get("test:ghidra-cmeshpart-oldstyle-loader-review-wave960")
        == r"py -3 tools\ghidra_cmeshpart_oldstyle_loader_review_wave960_probe.py --check",
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
        print("Wave960 CMeshPart old-style loader review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave960 CMeshPart old-style loader review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
