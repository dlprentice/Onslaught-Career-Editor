#!/usr/bin/env python3
"""Validate Wave1207 D3D/render-resource lifecycle current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1207-d3d-render-resource-lifecycle-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1207-d3d-render-resource-lifecycle-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1207-d3d-render-resource-lifecycle-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1207_d3d_render_resource_lifecycle_current_risk_review_2026-06-07.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
ACCOUNTING = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-accounting-guard.md"
MEASUREMENT_REGISTER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-measurement-register.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
MESH_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "mesh-resource-render-static-contract.md"
VERTEX_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "VertexShader.cpp" / "_index.md"
DXMESHVB_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXMeshVB.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER_JSONL = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPTS = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
README = ROOT / "README.MD"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-033229_post_wave1207_d3d_render_resource_lifecycle_current_risk_review_verified"

TARGETS = {
    "0x00501890": ("CVertexShader__scalar_deleting_dtor", "void * __thiscall CVertexShader__scalar_deleting_dtor(void * this, byte delete_flags)"),
    "0x00501a10": ("CVertexShader__VFunc_02_00501a10", "int __thiscall CVertexShader__VFunc_02_00501a10(void * this)"),
    "0x00512d50": ("DeviceObject__dtor_body", "void __thiscall DeviceObject__dtor_body(void * this)"),
    "0x00512dc0": ("DeviceObject__scalar_deleting_dtor", "void * __thiscall DeviceObject__scalar_deleting_dtor(void * this, byte flags)"),
    "0x0054bff0": ("CDXMeshVB__scalar_deleting_dtor", "void * __thiscall CDXMeshVB__scalar_deleting_dtor(void * this, byte flags)"),
    "0x0054c010": ("CDXMeshVB__dtor_base", "void __thiscall CDXMeshVB__dtor_base(void * this)"),
}

TAG_TOKENS = {
    "0x00501890": ("static-reaudit", "cvertexshader", "scalar-deleting-destructor", "cvertexshader-core-wave533"),
    "0x00501a10": ("static-reaudit", "cvertexshader", "vtable-slot-2", "wave961-readback-verified"),
    "0x00512d50": ("static-reaudit", "deviceobject", "dtor-body", "wave802-readback-verified"),
    "0x00512dc0": ("static-reaudit", "device-object", "scalar-deleting-dtor", "render-list"),
    "0x0054bff0": ("static-reaudit", "cdxmeshvb", "scalar-deleting-dtor", "vtable-slot-0"),
    "0x0054c010": ("static-reaudit", "cdxmeshvb", "destructor-base", "resource-release"),
}

COMMENT_TOKENS = {
    "0x00501890": ("scalar-deleting destructor wrapper", "CVertexShader__dtor", "CDXMemoryManager__Free"),
    "0x00501a10": ("vtable slot-2 boundary recovery", "CEngine__DeviceCall16C_CreateVertexShaderLike", "0x80004005"),
    "0x00512d50": ("DeviceObject cleanup body", "DAT_00889074", "DAT_00889078"),
    "0x00512dc0": ("DeviceObject vtable slot 0", "global render/device-object lists", "CDXMemoryManager"),
    "0x0054bff0": ("scalar-deleting destructor wrapper", "CDXMeshVB__dtor_base", "flags&1"),
    "0x0054c010": ("CDXMeshVB__ReleaseResources", "base device-object teardown", "+0x124"),
}

DECOMPILE_TOKENS = (
    "CVertexShader__dtor",
    "CDXMemoryManager__Free",
    "CEngine__SetVertexShadersEnabled",
    "CEngine__DeviceCall16C_CreateVertexShaderLike",
    "CVertexShader__LoadCompiledShaderBlobFromVSOFile",
    "DAT_00889074",
    "DAT_00889078",
    "CDXMeshVB__ReleaseResources",
    "DeviceObject__dtor_body",
)

DOC_TOKENS = (
    "Wave1207",
    "wave1207-d3d-render-resource-lifecycle-current-risk-review",
    "6 D3D/render-resource lifecycle current-risk rows",
    "1089/1179 = 92.37%",
    "remaining active focused work: 90",
    "legacy additive counter is deprecated",
    "1120/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current focused candidates: 1141",
    "live regenerated current focused candidates: 1141",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "read-only review",
    "no mutation",
    "no rename",
    "no signature change",
    "no comment change",
    "no tag change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consults used",
    "CVertexShader__scalar_deleting_dtor",
    "CVertexShader__VFunc_02_00501a10",
    "DeviceObject__dtor_body",
    "DeviceObject__scalar_deleting_dtor",
    "CDXMeshVB__scalar_deleting_dtor",
    "CDXMeshVB__dtor_base",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "36 xref rows",
    "260 instruction rows",
    "6 decompile rows",
    BACKUP,
    "static-reaudit-current-risk-ledger.json",
    "static-reaudit-measurement-register.md",
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "continuity denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime direct3d behavior proven",
    "runtime shader behavior proven",
    "runtime render-resource behavior proven",
    "exact layout proven",
    "exact source identity proven",
    "rebuild parity proven",
    "no-noticeable-difference parity proven",
)


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in read_text(path).splitlines() if line.strip()]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 6,
        "pre-tags.tsv": 6,
        "pre-xrefs.tsv": 36,
        "pre-instructions.tsv": 260,
        "pre-decompile/index.tsv": 6,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            require("runtime" in comment.lower() or "rebuild parity" in comment.lower(), f"missing runtime/rebuild boundary at {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            for token in TAG_TOKENS[address]:
                require(token in actual, f"missing tag at {address}: {token}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xref_targets = {normalize_address(row["target_addr"]) for row in xrefs}
    for address in TARGETS:
        require(address in xref_targets, f"missing xref coverage for {address}", failures)

    callers = {row.get("from_function", "") for row in xrefs}
    for caller in (
        "CVertexShader__dtor",
        "CUMTexture__dtor_base",
        "CIBuffer__Destructor",
        "CVBuffer__dtor_base",
        "CDXLandscape__Destructor",
        "CDXMeshVB__dtor_base",
        "CRenderQueue__dtor",
        "CWaterRenderSystem__dtor",
        "CDXMeshVB__scalar_deleting_dtor",
    ):
        require(caller in callers, f"missing xref caller: {caller}", failures)

    decompile_text = "\n".join(path.read_text(encoding="utf-8-sig") for path in (BASE / "pre-decompile").glob("*.c"))
    for token in DECOMPILE_TOKENS:
        require(token in decompile_text, f"missing decompile token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=6 found=6 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=6 missing=0",
        "pre-xrefs.log": "Wrote 36 rows",
        "pre-instructions.log": "Wrote 260 function-body instruction rows",
        "pre-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 18, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176425863 or backup.get("totalBytes") == 176425863.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_progress_and_docs(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current.get("focusedReviewed") == 1089, "focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "92.37%", "focused reviewed percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 90, "remaining focused mismatch", failures)
    require(current.get("liveFocusedCandidatesAfterLatestReview") == 1141, "live focused mismatch", failures)
    require(current.get("legacyAdditiveReviewedDeprecated") == 1120, "legacy additive mismatch", failures)
    require(current.get("duplicateAddressOvercountCorrected") == 26, "duplicate overcount mismatch", failures)
    require(current.get("wave1145ArithmeticOvercountCorrected") == 5, "Wave1145 overcount mismatch", failures)
    require(current.get("latestReviewWave") == "Wave1207 D3D Render Resource Lifecycle Current-Risk Review", "latest review wave mismatch", failures)

    ledger = read_json(LEDGER)
    require(ledger.get("latestWave") == "Wave1207 D3D Render Resource Lifecycle Current-Risk Review", "ledger latest wave mismatch", failures)
    require(ledger.get("correctedUniqueReviewed") == 1089, "ledger unique mismatch", failures)
    require(ledger.get("correctedUniquePercent") == "92.37%", "ledger percent mismatch", failures)
    require(ledger.get("remainingUnique") == 90, "ledger remaining mismatch", failures)
    require(ledger.get("countedRowsThroughWave1207") == 1115, "ledger counted row mismatch", failures)
    require(ledger.get("duplicateAddressOvercount") == 26, "ledger duplicate mismatch", failures)

    prose_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        MAPPED,
        CAMPAIGN,
        RANK,
        BINARY_INDEX,
        RE_INDEX,
        BACKLOG,
        MESH_CONTRACT,
        VERTEX_DOC,
        DXMESHVB_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        PROGRESS,
        LEDGER,
        ACCOUNTING,
        MEASUREMENT_REGISTER,
    ]
    for path in prose_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim in {path.relative_to(ROOT)}: {bad}", failures)

    readme_text = read_text(README)
    require("static-reaudit-measurement-register.md" in readme_text, "README missing measurement-register pointer", failures)
    for bad in ("Current static snapshot after Wave", "Latest completed backup:", "/1179"):
        require(bad not in readme_text, f"README still duplicates active static metric: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1207 note mirror mismatch", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1207-d3d-render-resource-lifecycle-current-risk-review")
        == r"py -3 tools\wave1207_d3d_render_resource_lifecycle_current_risk_review.py --check",
        "missing package script",
        failures,
    )

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6411, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)

    task = "Wave1207 D3D render-resource lifecycle current-risk review"
    ledger_rows = read_jsonl(LEDGER_JSONL)
    attempt_rows = read_jsonl(ATTEMPTS)
    require(any(row.get("task") == task for row in ledger_rows), "missing Wave1207 ledger row", failures)
    require(any(row.get("task") == task and row.get("result") == "success" for row in attempt_rows), "missing Wave1207 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_progress_and_docs(failures)

    if failures:
        print("Wave1207 D3D render-resource lifecycle current-risk review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1207 D3D render-resource lifecycle current-risk review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
