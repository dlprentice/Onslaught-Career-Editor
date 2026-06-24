#!/usr/bin/env python3
"""Validate Wave1062 Mat34 orientation/scale review artifacts."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1062-mat34-orientation-scale-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_mat34_orientation_scale_review_wave1062_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1062_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
DOCS = [
    PUBLIC_NOTE,
    AGGREGATE_NOTE,
    ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Math.cpp" / "_index.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md",
    ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_tracking_state.json",
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    ROOT / "re_orchestrator_state.json",
]
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"
BACKUP_PATH = r"G:\GhidraBackups\BEA_20260601-215617_post_wave1062_mat34_orientation_scale_review_verified"

EXPECTED_SIGNATURES = {
    "0x0040d1f0": ("Mat34__SetFromEulerAngles", "void __thiscall Mat34__SetFromEulerAngles(void * this, float angle0, float angle1, float angle2)"),
    "0x0040d2c0": ("Mat34__TransformVec3ByBasisToOut", "void __thiscall Mat34__TransformVec3ByBasisToOut(void * this, void * outVec, void * vec)"),
    "0x0040d320": ("Mat34__MultiplyBasisToOut", "void * __thiscall Mat34__MultiplyBasisToOut(void * this, void * out_basis, void * rhs_basis)"),
    "0x00495ed0": ("Mat34__ScaleByScalar", "void __thiscall Mat34__ScaleByScalar(void * this, void * outMatrix, float scalar)"),
    "0x004f7e90": ("CUnit__ctor_base", "void * __fastcall CUnit__ctor_base(void * this)"),
    "0x004f8140": ("Mat34__SetFromEulerDegrees", "void __thiscall Mat34__SetFromEulerDegrees(void * this, int yaw_deg, int pitch_deg, int roll_deg)"),
    "0x005b86c0": ("CFastVB__FastAcosApprox_Scalar", "int CFastVB__FastAcosApprox_Scalar(void)"),
}

NORMALIZED_TAGS = {
    "static-reaudit",
    "mat34-orientation-scale-review-wave1062",
    "wave1062-readback-verified",
    "retail-binary-evidence",
    "comment-normalized",
    "tag-normalized",
    "mat34",
    "matrix-basis",
}

DOC_TOKENS = (
    "Wave1062",
    "mat34-orientation-scale-review-wave1062",
    "0x00495ed0 Mat34__ScaleByScalar",
    "0x004f8140 Mat34__SetFromEulerDegrees",
    "0x0040d1f0 Mat34__SetFromEulerAngles",
    "0x0040d2c0 Mat34__TransformVec3ByBasisToOut",
    "0x0040d320 Mat34__MultiplyBasisToOut",
    "0x004f7e90 CUnit__ctor_base",
    "0x005b86c0 CFastVB__FastAcosApprox_Scalar",
    "812/1408 = 57.67%",
    "1170/1531 = 76.42%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "comment/tag normalization",
)

OVERCLAIMS = (
    "runtime transform behavior proven",
    "runtime orientation behavior proven",
    "fully reverse-engineered runtime",
    "rebuild parity proven",
    "exact source-layout identity proven",
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


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def norm(address: str) -> str:
    value = address.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "primary-metadata.tsv": 2,
        "primary-tags.tsv": 2,
        "primary-xrefs.tsv": 14,
        "primary-instructions.tsv": 306,
        "primary-decompile/index.tsv": 2,
        "context-metadata.tsv": 5,
        "context-tags.tsv": 5,
        "context-xrefs.tsv": 168,
        "context-instructions.tsv": 418,
        "context-decompile/index.tsv": 5,
        "post-metadata.tsv": 7,
        "post-tags.tsv": 7,
        "post-xrefs.tsv": 182,
        "post-instructions.tsv": 724,
        "post-decompile/index.tsv": 7,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {norm(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {norm(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {norm(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "post-xrefs.tsv")

    for address, (name, signature) in EXPECTED_SIGNATURES.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata {address}", failures)
        if row:
            require(row.get("name") == name, f"name mismatch {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
        dec = decompile.get(address)
        require(dec is not None, f"missing decompile {address}", failures)
        if dec:
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)

    for address, extra in {
        "0x0040d1f0": {"euler", "basis-builder", "angle-floats"},
        "0x0040d2c0": {"vec3-transform", "basis-transform", "translation-unproven"},
    }.items():
        row = metadata[address]
        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags {address}", failures)
        actual_tags = set((tag_row or {}).get("tags", "").split(";"))
        require((NORMALIZED_TAGS | extra).issubset(actual_tags), f"normalized tags missing {address}", failures)
        comment = row.get("comment", "")
        require("Wave1062 comment/tag normalization" in comment, f"missing Wave1062 comment token {address}", failures)
        require("tags, locals" not in comment.lower(), f"stale tags/locals wording remains {address}", failures)

    xref_names = {(norm(row["target_addr"]), row["from_function"]) for row in xrefs}
    require(("0x0040d1f0", "CBattleEngine__GetLaunchPosition") in xref_names, "missing SetFromEulerAngles BattleEngine xref", failures)
    require(("0x0040d2c0", "CBattleEngine__GetLaunchPosition") in xref_names, "missing TransformVec3 BattleEngine xref", failures)
    require(any(norm(row["target_addr"]) == "0x0040d2c0" and row["from_function"] == "CMCBuggy__UpdateWheel" for row in xrefs), "missing TransformVec3 CMCBuggy xref", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 tags_added=22 comment_updated=2 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=2 skipped=0 tags_added=22 comment_updated=2 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=2 tags_added=0 comment_updated=0 missing=0 bad=0",
        "post-metadata.log": "targets=7 found=7 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "post-xrefs.log": "Wrote 182 rows",
        "post-instructions.log": "Wrote 724 function-body instruction rows",
        "post-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token {relative}: {bad}", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "missing apply save report", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6246, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 174721927, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    for path in DOCS:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-mat34-orientation-scale-review-wave1062")
        == r"py -3 tools\ghidra_mat34_orientation_scale_review_wave1062_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1062-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1062 --check",
        "missing aggregate package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1062 mat34 orientation scale review" for row in ledger_rows), "missing Wave1062 ledger row", failures)
    require(any(row.get("task") == "Wave1062 mat34 orientation scale review" and row.get("attempt_id") == 20644 for row in attempt_rows), "missing Wave1062 attempt row", failures)


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
        print("Wave1062 Mat34 orientation/scale probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1062 Mat34 orientation/scale probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
