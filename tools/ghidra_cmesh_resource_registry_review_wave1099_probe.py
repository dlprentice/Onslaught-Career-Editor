#!/usr/bin/env python3
"""Validate Wave1099 CMesh resource registry read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1099-cmesh-resource-registry-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_cmesh_resource_registry_review_wave1099_2026-06-04.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1099_recheck_2026-06-04.md"
PACKAGE_JSON = ROOT / "package.json"
PROGRESS_JSON = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
MESH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "mesh.cpp" / "_index.md"
ENGINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "engine.cpp" / "_index.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
README = ROOT / "README.MD"
CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
AGENTS = ROOT / "AGENTS.md"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"G:\GhidraBackups\BEA_20260604-193549_post_wave1099_cmesh_resource_registry_review_verified"
WAVE_TAG = "cmesh-resource-registry-review-wave1099"

TARGETS = {
    "0x00449dc0": (
        "CEngine__LoadAllNamedMeshes",
        "void __thiscall CEngine__LoadAllNamedMeshes(void * this, void * dataFile)",
        ("Loading named meshes", "CMesh__FindOrCreate", "Static retail evidence only"),
    ),
    "0x004a5020": (
        "CMesh__Init",
        "void * __thiscall CMesh__Init(void * this)",
        ("Wave443", "DAT_00704ad8", "+0x158"),
    ),
    "0x004a50b0": (
        "CMesh__FreeResourcesAndUnlink",
        "void __thiscall CMesh__FreeResourcesAndUnlink(void * this)",
        ("Wave443", "CMesh__ReleaseEmbeddedResources", "+0x170"),
    ),
    "0x004a5200": (
        "CMesh__InitStatic",
        "int __cdecl CMesh__InitStatic(void)",
        ("Wave443", "DAT_00704adc", "meshtex\\default.tga"),
    ),
    "0x004a52b0": (
        "CMesh__ClearAllUsageMarkers",
        "void __cdecl CMesh__ClearAllUsageMarkers(void)",
        ("Wave813", "DAT_00704ad8", "CMesh__ClearOut"),
    ),
    "0x004a52d0": (
        "CMesh__ClearOut",
        "void __cdecl CMesh__ClearOut(void)",
        ("Wave813", "DAT_00704adc", "CMesh__FreeResourcesAndUnlink"),
    ),
    "0x004a53f0": (
        "CMesh__StatusLoadingMeshResources",
        "void __cdecl CMesh__StatusLoadingMeshResources(void)",
        ("Wave813", "Loading mesh resources", "CConsole__Status"),
    ),
    "0x004a5430": (
        "CMesh__FreeUnusedAndReportLeaks",
        "void __cdecl CMesh__FreeUnusedAndReportLeaks(void)",
        ("Wave813", "DAT_00704ae0", "end-of-level mesh leak"),
    ),
    "0x004a5970": (
        "CMesh__LoadByNameWithStatus",
        "int __thiscall CMesh__LoadByNameWithStatus(void * this, char * mesh_name, void * load_context)",
        ("Wave443", "data\\Meshes", "CMesh__Load"),
    ),
    "0x004a5b70": (
        "CMesh__Load",
        "int __thiscall CMesh__Load(void * this, void * mem_buffer, void * load_context)",
        ("Wave443", "CMesh__OptimizeTextures", "frame-cache setup"),
    ),
    "0x004aa410": (
        "CMesh__FindTextureByNameSuffixHint",
        "void * __cdecl CMesh__FindTextureByNameSuffixHint(void * texture_record)",
        ("Wave444", "texture lookup", "CTexture__FindTexture"),
    ),
    "0x004aa6b0": (
        "CMesh__GetNameOrUnknown",
        "void * __thiscall CMesh__GetNameOrUnknown(void * this)",
        ("Wave814", "DAT_00704ad8", "unknown mesh name"),
    ),
    "0x004aa6e0": (
        "CMesh__FindOrCreate",
        "void * __cdecl CMesh__FindOrCreate(char * mesh_name, void * load_context)",
        ("Wave444", "DAT_00704ad8", "+0x170"),
    ),
    "0x004aab90": (
        "CMesh__Deserialize",
        "void * __cdecl CMesh__Deserialize(void * primary_reader, void * resource_reader)",
        ("Wave445", "data\\resources\\meshes\\m_%s.aya", "chained mesh"),
    ),
    "0x004ab330": (
        "CMesh__FindByRuntimeId",
        "void * __cdecl CMesh__FindByRuntimeId(int runtime_id)",
        ("Wave445", "DAT_00704ad8", "+0x154"),
    ),
    "0x004ab360": (
        "CMesh__OptimizeParts",
        "void __thiscall CMesh__OptimizeParts(void * this)",
        ("Wave445", "DAT_00704af0", "DAT_00704af4"),
    ),
    "0x004adf90": (
        "CMesh__ReleaseEmbeddedResources",
        "void __thiscall CMesh__ReleaseEmbeddedResources(void * this)",
        ("Wave445", "0x24-byte", "resource record"),
    ),
    "0x004ae0d0": (
        "CMesh__InitPartVBufTextureFormats",
        "void __thiscall CMesh__InitPartVBufTextureFormats(void * this)",
        ("Wave445", "CVBufTexture__GetOrCreate", "VB format"),
    ),
}

COMMON_DOC_TOKENS = (
    "Wave1099",
    WAVE_TAG,
    "0x00449dc0 CEngine__LoadAllNamedMeshes",
    "0x004a5020 CMesh__Init",
    "0x004a50b0 CMesh__FreeResourcesAndUnlink",
    "0x004a5200 CMesh__InitStatic",
    "0x004a52d0 CMesh__ClearOut",
    "0x004a5430 CMesh__FreeUnusedAndReportLeaks",
    "0x004a5970 CMesh__LoadByNameWithStatus",
    "0x004a5b70 CMesh__Load",
    "0x004aa6e0 CMesh__FindOrCreate",
    "0x004aab90 CMesh__Deserialize",
    "0x004adf90 CMesh__ReleaseEmbeddedResources",
    "DAT_00704ad8",
    "DAT_00704adc",
    "data\\Meshes",
    "data\\resources\\meshes\\m_%s.aya",
    "1560/1560 = 100.00%",
    "812/1408 = 57.67%",
    "500/500 = 100.00%",
    "6410/6410 = 100.00%",
    BACKUP_PATH,
    "read-only review",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime proof complete",
    "patch behavior proven",
    "rebuild parity proven",
    "exact source-body identity proven",
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


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_token(text: str, token: str) -> bool:
    return token in text or token.replace("\\", "\\\\") in text


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 18,
        "pre-tags.tsv": 18,
        "pre-xrefs.tsv": 63,
        "pre-instructions.tsv": 6524,
        "pre-decompile/index.tsv": 18,
    }
    for relative, expected in expected_counts.items():
        rows = read_tsv(BASE / relative)
        require(len(rows) == expected, f"{relative} row count mismatch: {len(rows)} != {expected}", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}

    for address, (name, signature, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            comment = row.get("comment", "")
            for token in comment_tokens:
                require(contains_token(comment, token), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)
            actual_tags = {tag for tag in tag_row.get("tags", "").split(";") if tag}
            require("static-reaudit" in actual_tags, f"missing static-reaudit tag at {address}", failures)
            require("retail-binary-evidence" in actual_tags, f"missing retail evidence tag at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile index for {address}", failures)
        if dec is not None:
            require(dec.get("name") == name, f"decompile name mismatch at {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "pre-metadata.log": "targets=18 found=18 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=18 missing=0",
        "pre-xrefs.log": "Wrote 63 rows",
        "pre-instructions.log": "Wrote 6524 function-body instruction rows",
        "pre-decompile.log": "targets=18 dumped=18 missing=0 failed=0",
    }
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADADDR:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") in (175541127, 175541127.0), "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        AGGREGATE_NOTE,
        PROGRESS_JSON,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        MESH_DOC,
        ENGINE_DOC,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
        README,
        CAPABILITIES,
        AGENTS,
    ]
    for path in docs:
        text = read_text(path)
        for token in COMMON_DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-cmesh-resource-registry-review-wave1099")
        == r"py -3 tools\ghidra_cmesh_resource_registry_review_wave1099_probe.py --check",
        "missing focused package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1099-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1099 --check",
        "missing aggregate package script",
        failures,
    )

    progress = read_json(PROGRESS_JSON)
    require(progress["latestWave"]["wave"] == "Wave1099 CMesh resource registry review", "progress latest wave mismatch", failures)
    require(
        progress["latestWave"]["status"] in {"validation_pending", "validated_pending_commit", "committed", "pushed"},
        "progress status mismatch",
        failures,
    )
    require(progress["latestWave"]["backup"] == BACKUP_PATH, "progress backup mismatch", failures)
    require(progress["functionQuality"]["totalFunctions"] == 6410, "progress total mismatch", failures)
    require(progress["post100Reaudit"]["expandedStaticSurface"]["completed"] == 1560, "expanded count mismatch", failures)
    require(progress["post100Reaudit"]["wave911Focused"]["completed"] == 812, "wave911 focused mismatch", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1099 CMesh resource registry review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1099 CMesh resource registry review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
