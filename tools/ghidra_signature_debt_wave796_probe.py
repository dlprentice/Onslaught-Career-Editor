#!/usr/bin/env python3
"""Validate Wave796 final param-signature-debt read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave796-final-param-signature-debt"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_signature_debt_wave796_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
MESH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "mesh.cpp" / "_index.md"
DXTEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXTexture.cpp" / "_index.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
FASTVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FastVB.cpp" / "_index.md"
PCRTID_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PCRTID.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260524-050846_post_wave796_final_param_signature_debt_verified"

TARGETS = {
    "0x004bbcd0": (
        "CNamedMesh__VFunc_09_004bbcd0",
        "void __thiscall CNamedMesh__VFunc_09_004bbcd0(void * this, void * init_record, void * unused_slot_arg)",
        ("init_record", "second visible slot remains unused", "hidden register/thiscall storage"),
    ),
    "0x00564486": (
        "CRT__FmodReduceCore",
        "int __cdecl CRT__FmodReduceCore(int divisor_mantissa_low, uint divisor_mid_bits, int divisor_sign_exp_high)",
        ("visible packed divisor words", "custom hidden EAX path", "runtime rounding behavior"),
    ),
    "0x00574a99": (
        "`vector_constructor_iterator'",
        "void __stdcall `vector_constructor_iterator'(void * base, uint element_size, int element_count, _func_void_ptr_void_ptr * constructor)",
        ("base", "element_size", "constructor"),
    ),
    "0x00591460": (
        "CDXTexture__DecodeJpegSegment_StartOfFrame",
        "int __fastcall CDXTexture__DecodeJpegSegment_StartOfFrame(int sof_marker)",
        ("sof_marker", "hidden EAX/ESI/EBX/EBP ABI"),
    ),
    "0x00591fc0": (
        "CDXTexture__ParseJfifApp0Header",
        "void __fastcall CDXTexture__ParseJfifApp0Header(int segment_start_offset)",
        ("segment_start_offset", "hidden EAX/ESI/EDI ABI"),
    ),
    "0x005921a0": (
        "CDXTexture__ParseAdobeApp14Header",
        "void __thiscall CDXTexture__ParseAdobeApp14Header(void * this, uint segment_start_offset, int unused_context)",
        ("segment_start_offset", "unused_context", "payload length as the synthetic this"),
    ),
    "0x00592ca0": (
        "CDXTexture__FormatChunkTagForDiagnostics",
        "void __thiscall CDXTexture__FormatChunkTagForDiagnostics(void * this, int decode_state, int message_text, void * unused_context)",
        ("decode_state", "message_text", "unused_context"),
    ),
    "0x0059c070": (
        "CTexture__ProcessRowBatchesLinearStride",
        "void __stdcall CTexture__ProcessRowBatchesLinearStride(int callback_context, int callback_mode)",
        ("callback_context", "callback_mode", "hidden ESI row-batch descriptor"),
    ),
    "0x0059c110": (
        "CTexture__ProcessRowBatchesMcuStride128",
        "void __stdcall CTexture__ProcessRowBatchesMcuStride128(int callback_context, int callback_mode)",
        ("callback_context", "callback_mode", "0x80-scaled byte counts"),
    ),
    "0x0059e310": (
        "CDXTexture__WriteJpegHuffmanTable",
        "void __thiscall CDXTexture__WriteJpegHuffmanTable(void * this, int table_index, int unused_context)",
        ("table_index", "unused_context", "Hidden EAX selects the table class"),
    ),
    "0x005a7617": (
        "CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles",
        "void __stdcall CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles(void * out_matrix4, int packed_angle_pair_low, int packed_angle_pair_high)",
        ("visible output matrix pointer", "packed_angle_pair_high, packed_angle_pair_low", "runtime math correctness"),
    ),
}

COMMON_TAGS = {
    "static-reaudit",
    "signature-debt-wave796",
    "wave796-readback-verified",
    "retail-binary-evidence",
    "signature-hardened",
    "param-name-hardened",
    "final-param-signature-debt",
}

CORE_ANCHORS = (
    "Wave796 signature debt",
    "signature-debt-wave796",
    "0x004bbcd0 CNamedMesh__VFunc_09_004bbcd0",
    "0x00564486 CRT__FmodReduceCore",
    "0x00574a99 `vector_constructor_iterator'",
    "0x00591460 CDXTexture__DecodeJpegSegment_StartOfFrame",
    "0x00591fc0 CDXTexture__ParseJfifApp0Header",
    "0x005921a0 CDXTexture__ParseAdobeApp14Header",
    "0x00592ca0 CDXTexture__FormatChunkTagForDiagnostics",
    "0x0059c070 CTexture__ProcessRowBatchesLinearStride",
    "0x0059c110 CTexture__ProcessRowBatchesMcuStride128",
    "0x0059e310 CDXTexture__WriteJpegHuffmanTable",
    "0x005a7617 CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles",
    "0 exact-undefined signatures",
    "0 param_N signatures",
    "0x0042f220 CSPtrSet__Clear",
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime decode fidelity proven",
    "runtime jpeg output fidelity proven",
    "runtime math correctness proven",
    "fully reverse-engineered",
    "rebuild parity proven",
)


def normalize_address(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def signature_counts(rows: list[dict[str, str]]) -> tuple[int, int]:
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    strict_clean = sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )
    return commented, strict_clean


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 11,
        "pre-tags.tsv": 11,
        "pre-xrefs.tsv": 45,
        "pre-instructions.tsv": 539,
        "pre-decompile/index.tsv": 11,
        "post-metadata.tsv": 11,
        "post-tags.tsv": 11,
        "post-xrefs.tsv": 45,
        "post-instructions.tsv": 539,
        "post-decompile/index.tsv": 11,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require("Wave796 final param-signature-debt hardening" in comment, f"missing Wave796 comment token at {address}", failures)
            for token in tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"tags missing at {address}: {COMMON_TAGS - actual_tags}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=11 skipped=0 renamed=0 would_rename=0 signature_updated=11 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=11 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=11 found=11 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "post-xrefs.log": "Wrote 45 rows",
        "post-instructions.log": "Wrote 539 instruction rows",
        "post-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5544",
        "queue-probe.log": "Param signatures: 0",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave796.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave796_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 554, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    require(queue["priorityQueues"]["signature"] == [], "signature queue should be empty", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5544, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5544, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("address") == "0x0042f220", "raw commentless head mismatch", failures)
    require(raw_commentless is not None and raw_commentless.get("name") == "CSPtrSet__Clear", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 171314055, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    broad_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in broad_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        MESH_DOC: (
            "Wave796 signature debt",
            "signature-debt-wave796",
            "0x004bbcd0 CNamedMesh__VFunc_09_004bbcd0",
            "0 exact-undefined signatures",
            "0 param_N signatures",
            BACKUP_PATH,
        ),
        PCRTID_DOC: (
            "Wave796 signature debt",
            "signature-debt-wave796",
            "0x00564486 CRT__FmodReduceCore",
            "0x00574a99 `vector_constructor_iterator'",
            "0 exact-undefined signatures",
            "0 param_N signatures",
            BACKUP_PATH,
        ),
        DXTEXTURE_DOC: (
            "Wave796 signature debt",
            "signature-debt-wave796",
            "0x00591460 CDXTexture__DecodeJpegSegment_StartOfFrame",
            "0x00591fc0 CDXTexture__ParseJfifApp0Header",
            "0x005921a0 CDXTexture__ParseAdobeApp14Header",
            "0x00592ca0 CDXTexture__FormatChunkTagForDiagnostics",
            "0x0059e310 CDXTexture__WriteJpegHuffmanTable",
            "0 exact-undefined signatures",
            "0 param_N signatures",
            BACKUP_PATH,
        ),
        TEXTURE_DOC: (
            "Wave796 signature debt",
            "signature-debt-wave796",
            "0x0059c070 CTexture__ProcessRowBatchesLinearStride",
            "0x0059c110 CTexture__ProcessRowBatchesMcuStride128",
            "0 exact-undefined signatures",
            "0 param_N signatures",
            BACKUP_PATH,
        ),
        FASTVB_DOC: (
            "Wave796 signature debt",
            "signature-debt-wave796",
            "0x005a7617 CFastVB__DispatchOp_BuildRotationMatrixFromEulerAngles",
            "0 exact-undefined signatures",
            "0 param_N signatures",
            BACKUP_PATH,
        ),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(scripts.get("test:ghidra-signature-debt-wave796") == r"py -3 tools\ghidra_signature_debt_wave796_probe.py --check", "missing package script", failures)
    require(any(row.get("task") == "Wave796 signature debt" for row in read_jsonl(LEDGER)), "missing Wave796 ledger row", failures)
    require(any(row.get("task") == "Wave796 signature debt" and row.get("attempt_id") == 20451 for row in read_jsonl(ATTEMPT_LOG)), "missing Wave796 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave796 signature-debt probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave796 signature-debt probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
