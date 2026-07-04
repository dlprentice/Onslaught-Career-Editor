#!/usr/bin/env python3
"""Validate Wave1146 mixed engine score20 current-risk review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1146-mixed-engine-score20-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1146-mixed-engine-score20-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1146-mixed-engine-score20-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1146_mixed_engine_score20_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
WAVE1108_NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
WAVE1108_READINESS = ROOT / "release" / "readiness" / "wave1108_current_risk_rank_2026-06-04.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
DAMAGE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "damage.cpp" / "_index.md"
CONSOLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "console.cpp" / "_index.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
README = ROOT / "README.md"
AGENTS = ROOT / "AGENTS.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-174520_post_wave1146_mixed_engine_score20_current_risk_review_verified"
PRIOR_BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260605-171711_post_wave1145_component_flag_current_risk_review_verified"

TARGETS = {
    "0x00440b70": {
        "name": "CDamage__ctor_clear_head_and_init_flag",
        "signature": "void __fastcall CDamage__ctor_clear_head_and_init_flag(void * damage)",
        "comment": ("+0x1588c", "CDamage__Init", "stale CUnitAI"),
        "tags": ("damage-system", "owner-corrected"),
        "tokens": ("0x1588c",),
    },
    "0x004416e0": {
        "name": "CConsole__ResetStatusHistoryBuffer",
        "signature": "void __fastcall CConsole__ResetStatusHistoryBuffer(void * console)",
        "comment": ("30 0x50-byte", "+0x9e4", "+0x9e8", "DAT_00662dd0"),
        "tags": ("console", "status-history"),
        "tokens": ("0x00662dd0",),
    },
    "0x00441e50": {
        "name": "CDebugMarkers__Shutdown",
        "signature": "void __fastcall CDebugMarkers__Shutdown(void * * head_ref)",
        "comment": ("DAT_0066ffb0", "CDXMemoryManager__Free", "0x00549220", "0x009c3df0"),
        "tags": ("debug-marker", "allocator-corrected"),
        "tokens": ("0x0066ffb0", "0x00549220"),
    },
    "0x00449d50": {
        "name": "CEngine__InitResources",
        "signature": "void __fastcall CEngine__InitResources(void * engine)",
        "comment": ("hilight.tga", "hiteffect.tga", "cloak.tga"),
        "tags": ("engine", "init-resources", "textures"),
        "tokens": ("hilight.tga", "hiteffect.tga", "cloak.tga"),
    },
    "0x00449dc0": {
        "name": "CEngine__LoadAllNamedMeshes",
        "signature": "void __thiscall CEngine__LoadAllNamedMeshes(void * this, void * dataFile)",
        "comment": ("Loading named meshes", "CMesh__FindOrCreate", "RET 0x4"),
        "tags": ("engine", "named-meshes", "world-load"),
        "tokens": ("Loading named meshes", "CMesh__FindOrCreate"),
    },
    "0x00449ef0": {
        "name": "CEngine__GetViewMatrixFromCamera",
        "signature": "void __thiscall CEngine__GetViewMatrixFromCamera(void * this, void * camera, void * outViewMatrix)",
        "comment": ("RET 0x8", "outViewMatrix", "twelve dwords"),
        "tags": ("camera-matrix", "engine", "viewpoint"),
        "tokens": ("outViewMatrix",),
    },
    "0x0044a110": {
        "name": "CEngine__ResetPos",
        "signature": "void __thiscall CEngine__ResetPos(void * this, int x, int y)",
        "comment": ("RET 0x8", "this+0x10", "landscape"),
        "tags": ("engine", "landscape", "position-reset"),
        "tokens": ("this+0x10",),
    },
    "0x0044a2d0": {
        "name": "CEngine__SetupLights",
        "signature": "void CEngine__SetupLights(void)",
        "comment": ("MAP sun vector", "Atmospherics", "render-light matrices"),
        "tags": ("engine", "lighting", "render-state"),
        "tokens": ("0x005d856c",),
    },
}

DOC_TOKENS = (
    "Wave1146",
    "wave1146-mixed-engine-score20-current-risk-review",
    "306/1179 = 25.95%",
    "8 current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 873",
    "current risk candidates: 6166",
    "mixed CDamage/CConsole/CDebugMarkers/CEngine score20 current-risk review",
    "fresh Ghidra export",
    "damage sentinel",
    "console status-history",
    "debug-marker shutdown",
    "engine resource/view/light helpers",
    "read-only review",
    "no mutation",
    "no Codex subagent",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "CDamage__ctor_clear_head_and_init_flag",
    "CConsole__ResetStatusHistoryBuffer",
    "CDebugMarkers__Shutdown",
    "CEngine__InitResources",
    "CEngine__LoadAllNamedMeshes",
    "CEngine__GetViewMatrixFromCamera",
    "CEngine__ResetPos",
    "CEngine__SetupLights",
    BACKUP,
    PRIOR_BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIM_TOKENS = (
    "runtime damage behavior proven",
    "runtime console behavior proven",
    "runtime debug-marker behavior proven",
    "runtime engine behavior proven",
    "runtime render behavior proven",
    "exact layouts proven",
    "rebuild parity proven",
)


def normalize_address(address: str) -> str:
    value = (address or "").strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


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
        "pre-metadata.tsv": 8,
        "pre-tags.tsv": 8,
        "pre-xrefs.tsv": 12,
        "pre-instructions.tsv": 466,
        "pre-decompile/index.tsv": 8,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    instructions = read_tsv(BASE / "pre-instructions.tsv")
    instruction_text = "\n".join(
        f"{row.get('address', '')} {row.get('mnemonic', '')} {row.get('operands', '')} {row.get('comment', '')}"
        for row in instructions
    )
    decompile_text = "\n".join(read_text(path) for path in (BASE / "pre-decompile").glob("*.c"))
    evidence_text = instruction_text + "\n" + decompile_text
    compact_evidence_text = evidence_text.replace(" ", "").lower()

    for address, expected in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == expected["name"], f"name mismatch at {address}", failures)
            require(row.get("signature") == expected["signature"], f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in expected["comment"]:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require({"static-reaudit", "retail-binary-evidence"}.issubset(actual_tags), f"common tags missing at {address}", failures)
            for tag in expected["tags"]:
                require(tag in actual_tags, f"missing tag at {address}: {tag}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == expected["signature"], f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        for token in expected["tokens"]:
            token_present = token.lower().replace(" ", "") in compact_evidence_text or token in evidence_text
            require(token_present, f"missing instruction/decompile token for {address}: {token}", failures)

    for token in ("0x1588c", "0x00662dd0", "0x0066ffb0", "0x00549220", "hilight.tga", "hiteffect.tga", "cloak.tga"):
        require(token.lower() in evidence_text.lower(), f"missing global instruction/decompile token: {token}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=8 found=8 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "pre-xrefs.log": "Wrote 12 rows",
        "pre-instructions.log": "Wrote 466 function-body instruction rows",
        "pre-decompile.log": "targets=8 dumped=8 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "SCRIPT ERROR", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_progress_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6411, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    rows = read_tsv(QUEUE_TSV)
    commented, strict_clean = signature_counts(rows)
    require(len(rows) == 6411, "quality TSV row count mismatch", failures)
    require(commented == 6411, "quality TSV commented count mismatch", failures)
    require(strict_clean == 6411, "strict clean-signature count mismatch", failures)

    risk = read_json(RISK_JSON)
    focused = read_json(FOCUSED_JSON)
    require(risk.get("candidateFunctions") == 6166, "current risk candidate mismatch", failures)
    require(focused.get("candidateFunctions") == 1178, "focused candidate mismatch", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    latest = progress["latestWave"]
    require(latest["wave"] == "Wave1146 mixed engine score20 current-risk review", "progress latest wave mismatch", failures)
    require(latest["tag"] == "wave1146-mixed-engine-score20-current-risk-review", "progress latest tag mismatch", failures)
    require(latest["backup"] == BACKUP, "progress latest backup mismatch", failures)
    artifact_commit = latest.get("artifactCommit", "")
    require(artifact_commit == "pending Wave1146 commit" or re.fullmatch(r"[0-9a-f]{40}", artifact_commit or ""), "progress artifact commit mismatch", failures)
    require(progress["functionQuality"]["strictCleanSignatureProxy"] == "6411/6411 = 100.00%", "progress strict proxy mismatch", failures)
    require(current["focusedReviewed"] == 306, "progress focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "25.95%", "progress focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 873, "progress remaining mismatch", failures)
    require(current["broadRiskCandidates"] == 6166, "progress broad candidates mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1178, "progress live focused mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        MAPPED_SYSTEMS,
        MAPPED_SYSTEMS_MIRROR,
        CAMPAIGN,
        WAVE1108_NOTE,
        WAVE1108_READINESS,
        BINARY_INDEX,
        RE_INDEX,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        DAMAGE_DOC,
        CONSOLE_DOC,
        ENGINE_DOC,
        PROGRESS,
        PROGRESS_MIRROR,
        README,
        AGENTS,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIM_TOKENS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1146 note mirror mismatch", failures)
    require(read_text(MAPPED_SYSTEMS) == read_text(MAPPED_SYSTEMS_MIRROR), "mapped-systems mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "progress mirror mismatch", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:wave1146-mixed-engine-score20-current-risk-review") == r"py -3 tools\wave1146_mixed_engine_score20_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_progress_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1146 mixed engine score20 current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1146 mixed engine score20 current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
