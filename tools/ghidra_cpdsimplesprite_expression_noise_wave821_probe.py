#!/usr/bin/env python3
"""Validate Wave821 CPDSimpleSprite expression/noise read-back artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave821-cpdsimplesprite-expression-noise"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_cpdsimplesprite_expression_noise_wave821_2026-05-24.md"
PACKAGE_JSON = ROOT / "package.json"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
PARTICLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleDescriptor.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260524-173755_post_wave821_cpdsimplesprite_expression_noise_verified"
NEXT_HEAD = "0x004caf30 CParticleManager__ClearParticleOwnerBacklinks"

TARGET_SIGNATURES = {
    "0x004c0c70": "double __cdecl CPDSimpleSprite__EvalExpressionNode(float base_value, void * post_scale_node, void * pre_scale_node, void * pre_offset_node, void * post_offset_node, int operator_id, int output_mode, float time_scale)",
    "0x004c7db0": "void __cdecl CPDSimpleSprite__InitNoiseTableOnce(void)",
}

TARGET_NAMES = {
    "0x004c0c70": "CPDSimpleSprite__EvalExpressionNode",
    "0x004c7db0": "CPDSimpleSprite__InitNoiseTableOnce",
}

COMMENT_TOKENS = {
    "0x004c0c70": (
        "Wave821 static read-back",
        "x87 ST0",
        "0x004c0d2c",
        "0x004c0fec",
        "CPDSimpleSprite__EvaluateExpressionRecursive",
        "rand jitter",
    ),
    "0x004c7db0": (
        "Wave821 static read-back",
        "DAT_0082b398",
        "DAT_0082a358",
        "0x400-dword",
        "32x32",
        "_rand",
        "0x004c5d5e",
        "0x004c8043",
        "0x004c900c",
    ),
}

TARGET_XREFS = {
    "0x004c0c70": {"0x004c0d2c", "0x004c0ddf", "0x004c0f3a", "0x004c0fec", "0x004c173a", "0x004ca390"},
    "0x004c7db0": {"0x004c5d5e", "0x004c8043", "0x004c900c"},
}

COMMON_TAGS = {
    "static-reaudit",
    "cpdsimplesprite-expression-noise-wave821",
    "wave821-readback-verified",
    "retail-binary-evidence",
    "comment-hardened",
    "signature-hardened",
    "cpdsimplesprite",
    "particle-descriptor",
}

EXTRA_TAGS = {
    "0x004c0c70": {"expression-evaluator", "recursive", "x87-return"},
    "0x004c7db0": {"noise-table", "one-shot-initializer", "render-helper"},
}

HELPER_NAMES = {
    "CPDSimpleSprite__SetUVFromTileIndex",
    "CPDSimpleSprite__EvaluateExpressionRecursive",
    "CPDSimpleSprite__VFunc_10_004c14f0",
    "CPDSimpleSprite__CopyTransformMatrix",
    "CPDSimpleSprite__BuildUvAtlasBuckets",
    "CPDSimpleSprite__ProcessAndRenderSpriteList",
    "CPDSimpleSprite__ScaleVec3InPlace",
    "CPDSimpleSprite__ReciprocalVec3Magnitude",
    "Vec3__NormalizeInPlace",
    "CPDSimpleSprite__EvaluateCurveDrivenScale",
    "Vec3__CopyXYZ",
    "CPDSimpleSprite__VFunc_23_004c8040",
    "CEngine__ComputeSpriteTintByDistance",
}

CORE_ANCHORS = (
    "Wave821 CPDSimpleSprite expression/noise",
    "cpdsimplesprite-expression-noise-wave821",
    "0x004c0c70 CPDSimpleSprite__EvalExpressionNode",
    "0x004c7db0 CPDSimpleSprite__InitNoiseTableOnce",
    "CPDSimpleSprite__EvaluateExpressionRecursive",
    "DAT_0082b398",
    "DAT_0082a358",
    "5622/6098 = 92.19%",
    NEXT_HEAD,
    BACKUP_PATH,
)

OVERCLAIM_TOKENS = (
    "runtime particle rendering behavior proven",
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
        "pre-metadata.tsv": 2,
        "pre-tags.tsv": 2,
        "pre-xrefs.tsv": 18,
        "pre-instructions.tsv": 1802,
        "pre-helper-metadata.tsv": 13,
        "pre-helper-instructions.tsv": 2873,
        "pre-decompile/index.tsv": 2,
        "post-metadata.tsv": 2,
        "post-tags.tsv": 2,
        "post-xrefs.tsv": 18,
        "post-instructions.tsv": 1802,
        "post-helper-metadata.tsv": 13,
        "post-helper-instructions.tsv": 2873,
        "post-decompile/index.tsv": 2,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    helper_names = {row["name"] for row in read_tsv(BASE / "post-helper-metadata.tsv")}
    xrefs: dict[str, set[str]] = {}
    for row in read_tsv(BASE / "post-xrefs.tsv"):
        xrefs.setdefault(normalize_address(row["target_addr"]), set()).add(normalize_address(row["from_addr"]))

    require(HELPER_NAMES.issubset(helper_names), f"missing helper rows: {HELPER_NAMES - helper_names}", failures)

    for address, name in TARGET_NAMES.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == TARGET_SIGNATURES[address], f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            required = COMMON_TAGS | EXTRA_TAGS[address]
            require(required.issubset(actual_tags), f"tags missing at {address}: {required - actual_tags}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == TARGET_SIGNATURES[address], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        require(TARGET_XREFS[address].issubset(xrefs.get(address, set())), f"xrefs missing at {address}: {TARGET_XREFS[address] - xrefs.get(address, set())}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry-compile-error.log": "no suitable method found for updateFunction",
        "apply-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=2 skipped=0 renamed=0 would_rename=0 signature_updated=2 comment_only_updated=0 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=2 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=2 found=2 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=2 missing=0",
        "post-xrefs.log": "Wrote 18 rows",
        "post-instructions.log": "Wrote 1802 instruction rows",
        "post-helper-metadata.log": "targets=13 found=13 missing=0",
        "post-helper-instructions.log": "Wrote 2873 instruction rows",
        "post-decompile.log": "targets=2 dumped=2 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6098 commented_functions=5622",
        "queue-probe.log": "Commentless functions: 476",
    }
    log_aliases = {
        "quality-refresh.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "export-functions-quality-wave821.log",
        "queue-probe.log": ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "wave821_queue_probe.log",
    }
    for relative, token in expected.items():
        path = log_aliases.get(relative, BASE / relative)
        text = read_text(path)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        if relative == "apply-dry-compile-error.log":
            continue
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6098, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 476, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)
    for key in ("commentlessHighSignal", "signature", "nameConfidence", "legacyWeakNames"):
        require(queue["priorityQueues"][key] == [], f"expected empty priority queue: {key}", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    raw_commentless = next((row for row in rows if not row.get("comment", "").strip()), None)
    require(len(rows) == 6098, "quality TSV row count mismatch", failures)
    require(commented == 5622, "quality TSV commented count mismatch", failures)
    require(strict_clean == 5622, "strict clean-signature count mismatch", failures)
    require(raw_commentless is not None and row_id(raw_commentless) == NEXT_HEAD, "raw commentless head mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes", 0)) == 171510663, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def row_id(row: dict[str, str]) -> str:
    return f"{normalize_address(row.get('address', ''))} {row.get('name', '')}"


def check_docs(failures: list[str]) -> None:
    docs = [
        PUBLIC_NOTE,
        FUNCTION_INDEX,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        BACKLOG,
        PARTICLE_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in CORE_ANCHORS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIM_TOKENS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-cpdsimplesprite-expression-noise-wave821") == r"py -3 tools\ghidra_cpdsimplesprite_expression_noise_wave821_probe.py --check", "missing package script", failures)

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave821 CPDSimpleSprite expression/noise" for row in ledger_rows), "missing Wave821 ledger row", failures)
    require(any(row.get("task") == "Wave821 CPDSimpleSprite expression/noise" and row.get("attempt_id") == 20476 for row in attempts), "missing Wave821 attempt row", failures)


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
        print("Wave821 CPDSimpleSprite expression/noise probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave821 CPDSimpleSprite expression/noise probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
