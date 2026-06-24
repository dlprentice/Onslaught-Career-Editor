#!/usr/bin/env python3
"""Validate Wave1093 CEngine core bootstrap review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1093-cengine-core-bootstrap-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cengine_core_bootstrap_review_wave1093_2026-06-04.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1093_recheck_2026-06-04.md"
PACKAGE_JSON = ROOT / "package.json"
PROGRESS_JSON = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
README = ROOT / "README.MD"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
AGENTS = ROOT / "AGENTS.md"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260604-155838_post_wave1093_cengine_core_bootstrap_review_verified"
WAVE_TAG = "cengine-core-bootstrap-review-wave1093"

TARGETS = {
    "0x00449820": (
        "CEngine__ctor",
        "void __fastcall CEngine__ctor(void * engine)",
        ("engine vtable", "render-landscape flag", "+0x4a8"),
    ),
    "0x00449890": (
        "CEngine__Shutdown",
        "void __fastcall CEngine__Shutdown(void * engine)",
        ("screen effects", "shadow/tree systems", "VB/IB pool"),
    ),
    "0x004499d0": (
        "CEngine__Init",
        "int __fastcall CEngine__Init(void * engine)",
        ("cg_renderlandscape", "cg_drawpolybuckets", "screen effects/shadows/trees"),
    ),
    "0x00449d50": (
        "CEngine__InitResources",
        "void __fastcall CEngine__InitResources(void * engine)",
        ("hilight.tga", "hiteffect.tga", "cloak.tga"),
    ),
    "0x00449dc0": (
        "CEngine__LoadAllNamedMeshes",
        "void __thiscall CEngine__LoadAllNamedMeshes(void * this, void * dataFile)",
        ("Loading named meshes", "case-insensitive compare", "CMesh__FindOrCreate"),
    ),
    "0x00449ef0": (
        "CEngine__GetViewMatrixFromCamera",
        "void __thiscall CEngine__GetViewMatrixFromCamera(void * this, void * camera, void * outViewMatrix)",
        ("RET 0x8", "camera orientation vfunc", "twelve dwords"),
    ),
    "0x0044a020": (
        "CEngine__SetViewpoint",
        "void __thiscall CEngine__SetViewpoint(void * this, int viewpoint, void * camera, void * viewport, void * player)",
        ("RET 0x10", "CInterpolatedCamera", "selected viewpoint"),
    ),
    "0x0044a0d0": (
        "CEngine__SelectViewpoint",
        "void __thiscall CEngine__SelectViewpoint(void * this, int viewpoint)",
        ("RET 0x4", "+0x4ac", "D3DDevice__SetViewport"),
    ),
    "0x0044a110": (
        "CEngine__ResetPos",
        "void __thiscall CEngine__ResetPos(void * this, int x, int y)",
        ("RET 0x8", "mLandscape", "reset-position"),
    ),
    "0x0044a130": (
        "CEngine__InitDamageSystem",
        "void __fastcall CEngine__InitDamageSystem(void * engine)",
        ("damage tables", "tree-shadow", "LockCurrentDamage"),
    ),
    "0x0044a1f0": (
        "CEngine__LoadMixers",
        "void __thiscall CEngine__LoadMixers(void * this, int set)",
        ("CMapTex__LoadMixerTextureSet", "set/6/0x100", "copied mixer levels"),
    ),
    "0x0044a6e0": (
        "CEngine__Deserialize",
        "void __thiscall CEngine__Deserialize(void * this, void * chunkReader)",
        ("ENGN", "CChunkReader", "MAP deserialize"),
    ),
}

DOC_TOKENS = (
    "Wave1093",
    WAVE_TAG,
    "0x00449820 CEngine__ctor",
    "0x004499d0 CEngine__Init",
    "0x00449dc0 CEngine__LoadAllNamedMeshes",
    "0x00449ef0 CEngine__GetViewMatrixFromCamera",
    "0x0044a020 CEngine__SetViewpoint",
    "0x0044a0d0 CEngine__SelectViewpoint",
    "0x0044a1f0 CEngine__LoadMixers",
    "0x0044a6e0 CEngine__Deserialize",
    "0x005290a0 CD3DApplication__Create",
    "0x0052af00 CD3DApplication__Initialize3DEnvironment",
    "1560/1560 = 100.00%",
    "812/1408 = 57.67%",
    "500/500 = 100.00%",
    "6410/6410 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime engine boot proven",
    "runtime rendering behavior proven",
    "patch behavior proven",
    "rebuild parity proven",
    "all systems complete",
    "every system is complete",
    "fully reverse-engineered",
    "fully reverse engineered",
    "exact source-layout identity proven",
    "exact source layout identity proven",
)


def normalize_address(value: str) -> str:
    text = value.strip().lower()
    if text.startswith("0x"):
        text = text[2:]
    return "0x" + text.zfill(8)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig", errors="replace").replace("\x00", "")


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


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "primary-metadata.tsv": 12,
        "primary-tags.tsv": 12,
        "primary-xrefs.tsv": 25,
        "primary-instructions.tsv": 785,
        "primary-decompile/index.tsv": 12,
        "context-metadata.tsv": 10,
        "context-tags.tsv": 10,
        "context-xrefs.tsv": 17,
        "context-instructions.tsv": 1231,
        "context-decompile/index.tsv": 10,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "primary-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "primary-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "primary-decompile" / "index.tsv")}

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            require("Static retail evidence only" in comment, f"missing boundary text at {address}", failures)
            for token in comment_tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags at {address}", failures)
        if tag_row is not None:
            tag_text = tag_row.get("tags", "")
            for token in ("static-reaudit", "engine", "retail-binary-evidence"):
                require(token in tag_text, f"missing tag at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile at {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

    xrefs = read_tsv(BASE / "primary-xrefs.tsv")
    xref_pairs = {(normalize_address(row["target_addr"]), row.get("from_function", "")) for row in xrefs}
    for address, caller in (
        ("0x004499d0", "CDXEngine__Init"),
        ("0x00449d50", "CDXEngine__InitResources"),
        ("0x00449dc0", "CWorld__LoadWorld"),
        ("0x00449ef0", "CDXEngine__Render"),
        ("0x00449ef0", "CFrontEnd__RenderStart"),
        ("0x0044a020", "CGame__Render"),
        ("0x0044a0d0", "CHud__RenderOverlayForViewpoint"),
        ("0x0044a6e0", "CResourceAccumulator__ReadResourceFile"),
    ):
        require((address, caller) in xref_pairs, f"missing xref {caller} -> {address}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "primary-metadata.log": "targets=12 found=12 missing=0",
        "primary-tags.log": "ExportFunctionTagsByAddress complete: rows=12 missing=0",
        "primary-xrefs.log": "Wrote 25 rows",
        "primary-instructions.log": "Wrote 785 function-body instruction rows",
        "primary-decompile.log": "targets=12 dumped=12 missing=0 failed=0",
        "context-metadata.log": "targets=10 found=10 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=10 missing=0",
        "context-xrefs.log": "Wrote 17 rows",
        "context-instructions.log": "Wrote 1231 function-body instruction rows",
        "context-decompile.log": "targets=10 dumped=10 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "BADNAME:", "BADSIG:", "BADCOMMENT:", "BADTAGS:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 175541127 or backup.get("totalBytes") == 175541127.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs_and_state(failures: list[str]) -> None:
    core_docs = [
        NOTE,
        AGGREGATE_NOTE,
        PROGRESS_JSON,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        ENGINE_DOC,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        README,
        CAPABILITIES,
        AGENTS,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing doc token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    progress = read_json(PROGRESS_JSON)
    require(progress["latestWave"]["wave"] == "Wave1093 CEngine core bootstrap review", "progress latest wave mismatch", failures)
    require(progress["latestWave"]["status"] in {"validation_pending", "validated_pending_commit", "committed"}, "progress status mismatch", failures)
    require(progress["latestWave"]["backup"] == BACKUP_PATH, "progress backup mismatch", failures)
    require(progress["functionQuality"]["totalFunctions"] == 6410, "progress total mismatch", failures)
    require(progress["post100Reaudit"]["expandedStaticSurface"]["completed"] == 1560, "expanded count mismatch", failures)
    require(progress["post100Reaudit"]["wave911Focused"]["completed"] == 812, "wave911 focused mismatch", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(scripts.get("test:ghidra-cengine-core-bootstrap-review-wave1093") == r"py -3 tools\ghidra_cengine_core_bootstrap_review_wave1093_probe.py --check", "missing focused package script", failures)
    require(scripts.get("test:ghidra-wave900-plus-through-wave1093-recheck") == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1093 --check", "missing aggregate package script", failures)

    ledger = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1093 CEngine core bootstrap review" for row in ledger), "missing Wave1093 ledger row", failures)
    require(any(row.get("task") == "Wave1093 CEngine core bootstrap review" and row.get("attempt_id") == 20673 for row in attempts), "missing Wave1093 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs_and_state(failures)

    if failures:
        print("Wave1093 CEngine core bootstrap review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1093 CEngine core bootstrap review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
