#!/usr/bin/env python3
"""Validate Wave832 texture/surface prelude read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave832-texture-surface-prelude"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_texture_surface_prelude_wave832_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
TEXTURE_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
TEXTURE_INIT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "CTextureBase__Init.md"
DXSURF_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXSurf.cpp.md"
DXSURF_UNLINK_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXSurf.cpp" / "CDXSurf__UnlinkNodeFromGlobalList.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260524-230834_post_wave832_texture_surface_prelude_verified"
NEXT_HEAD = "0x004f5b70 CParticleDescriptor__SetIndexedParam"

TARGETS = {
    "0x004f2710": {
        "name": "CTextureBase__Init",
        "signature": "void * __fastcall CTextureBase__Init(void * texture_base)",
        "comment_tokens": (
            "Wave832 static read-back",
            "CTexture__ctor",
            "0x00556ce1",
            "DAT_0083d9b0",
            "texture_base-0x08",
            "JCLTEX #%d",
            "0x00632eb4",
            "DAT_0083d99c",
        ),
        "tags": ("texture-base-init", "jcltex-name"),
    },
    "0x004f2790": {
        "name": "CDXSurf__UnlinkNodeFromGlobalList",
        "signature": "void __fastcall CDXSurf__UnlinkNodeFromGlobalList(void * texture_base)",
        "comment_tokens": (
            "Wave832 static read-back",
            "ECX-only",
            "0x00556e70",
            "0x005d7d30",
            "0x005d7d50",
            "DAT_0083d9b0",
            "texture_base-0x08",
            "stale cdecl",
        ),
        "tags": ("global-list-unlink", "ecx-abi"),
    },
}

COMMON_TAGS = {
    "static-reaudit",
    "texture-surface-prelude-wave832",
    "wave832-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "texture-lifecycle",
    "surface-lifecycle",
    "global-texture-list",
}

CORE_ANCHORS = (
    "Wave832 Texture/Surface Prelude",
    "texture-surface-prelude-wave832",
    "0x004f2710 CTextureBase__Init",
    "void * __fastcall CTextureBase__Init(void * texture_base)",
    "0x004f2790 CDXSurf__UnlinkNodeFromGlobalList",
    "void __fastcall CDXSurf__UnlinkNodeFromGlobalList(void * texture_base)",
    "DAT_0083d9b0",
    "JCLTEX #%d",
    "0x00556ce1",
    "0x00556e70",
    "5654/6098 = 92.72%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime texture lifetime behavior proven",
    "runtime surface lifetime behavior proven",
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


def strict_clean_count(rows: list[dict[str, str]]) -> int:
    return sum(
        1
        for row in rows
        if row.get("comment", "").strip()
        and not row.get("signature", "").startswith("undefined ")
        and not re.search(r"\bparam_\d+\b", row.get("signature", ""))
    )


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 2,
        "pre-tags.tsv": 2,
        "pre-xrefs.tsv": 4,
        "pre-instructions.tsv": 74,
        "pre-decompile/index.tsv": 2,
        "pre-context-metadata.tsv": 11,
        "pre-context-decompile/index.tsv": 11,
        "pre-xref-site-instructions.tsv": 148,
        "post-metadata.tsv": 2,
        "post-tags.tsv": 2,
        "post-xrefs.tsv": 4,
        "post-instructions.tsv": 74,
        "post-decompile/index.tsv": 2,
        "post-context-metadata.tsv": 11,
        "post-context-decompile/index.tsv": 11,
        "post-xref-site-instructions.tsv": 148,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == expected["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in expected["comment_tokens"]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            expected_tags = COMMON_TAGS | set(expected["tags"])
            require(expected_tags.issubset(actual), f"tags missing at {address}: {expected_tags - actual}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xrefs = read_tsv(BASE / "post-xrefs.tsv")
    xref_pairs = {(normalize_address(row["target_addr"]), normalize_address(row["from_addr"])) for row in xrefs}
    for pair in (
        ("0x004f2710", "0x00556ce1"),
        ("0x004f2790", "0x00556e70"),
        ("0x004f2790", "0x005d7d36"),
        ("0x004f2790", "0x005d7d81"),
    ):
        require(pair in xref_pairs, f"missing xref pair {pair}", failures)

    string_expectations = {
        "string-00632eb4.tsv": "JCLTEX #%d",
        "string-00632ef0.tsv": r"[maintainer-local-source-export-root]\texture.cpp",
        "string-00652660.tsv": r"Texture %s refcount=%d\x0a",
    }
    for relative, token in string_expectations.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing string token in {relative}: {token}", failures)

    site_text = read_text(BASE / "post-xref-site-instructions.tsv")
    for token in ("LEA\tECX, [ESI + 0x8]", "JMP\t0x004f2790", "CALL\t0x004f2790"):
        require(token in site_text, f"missing xref-site instruction token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=2 found=2 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=2 missing=0",
        "post-xrefs.log": "Wrote 4 rows",
        "post-instructions.log": "Wrote 74 instruction rows",
        "post-decompile.log": "targets=2 dumped=2 missing=0 failed=0",
        "post-context-metadata.log": "targets=11 found=11 missing=0",
        "post-context-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
        "post-xref-site-instructions.log": "Wrote 148 instruction rows",
        "quality-refresh.log": "total_functions=6098 commented_functions=5654",
        "queue-probe.log": "Commentless functions: 444",
    }
    aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave832.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave832_queue_probe.log",
    }
    for relative, token in expected.items():
        path = aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BAD:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 444, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    raw = next((row for row in rows if not row.get("comment", "").strip()), None)
    commented = sum(1 for row in rows if row.get("comment", "").strip())
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5654, "quality TSV commented count mismatch", failures)
    require(strict_clean_count(rows) == 5654, "strict clean count mismatch", failures)
    require(raw is not None and raw.get("address") == "0x004f5b70", "raw commentless head mismatch", failures)
    require(raw is not None and raw.get("name") == "CParticleDescriptor__SetIndexedParam", "raw commentless head name mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 171772807 or backup.get("totalBytes") == 171772807.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        TEXTURE_INDEX,
        TEXTURE_INIT_DOC,
        DXSURF_DOC,
        DXSURF_UNLINK_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-texture-surface-prelude-wave832")
        == r"py -3 tools\ghidra_texture_surface_prelude_wave832_probe.py --check",
        "missing package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave832 texture/surface prelude" for row in ledger_rows), "missing Wave832 ledger row", failures)
    require(
        any(row.get("task") == "Wave832 texture/surface prelude" and row.get("attempt_id") == 20487 for row in attempts),
        "missing Wave832 attempt row",
        failures,
    )


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
        print("Wave832 texture/surface prelude probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave832 texture/surface prelude probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
