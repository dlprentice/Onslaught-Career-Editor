#!/usr/bin/env python3
"""Validate Wave1046 RenderThing / CRTTree read-only review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1046-renderthing-crttree-review"
PUBLIC_NOTE = ROOT / "release" / "readiness" / "ghidra_renderthing_crttree_review_wave1046_2026-06-01.md"
AGGREGATE_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1046_recheck_2026-06-01.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
RTCUTSCENE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "RTCutscene.cpp" / "_index.md"
TREE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "tree.cpp" / "_index.md"
PCRTID_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "PCRTID.cpp" / "_index.md"
RTMESH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "rtmesh.cpp" / "_index.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
BACKUP_SUMMARY = BASE / "backup-summary.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260601-120449_post_wave1046_renderthing_crttree_review_verified"

TARGETS = {
    "0x004db880": (
        "CRenderThing__ForwardSlot26ToChildSlot68",
        "void __thiscall CRenderThing__ForwardSlot26ToChildSlot68(void * this, void * arg0, void * arg1)",
    ),
    "0x004dbb80": (
        "CRenderThing__VFunc_07_ClearRenderOutputs",
        "void __thiscall CRenderThing__VFunc_07_ClearRenderOutputs(void * this, void * arg0, void * arg1, void * out_vec4, void * out_matrix, void * arg4, void * arg5)",
    ),
    "0x004dbbe0": (
        "CRenderThing__VFunc_08_ClearVec3",
        "void __thiscall CRenderThing__VFunc_08_ClearVec3(void * this, void * out_vec3, void * arg1)",
    ),
    "0x004dbd20": ("CRenderThing__dtor", "void __fastcall CRenderThing__dtor(void * this)"),
    "0x004dbd50": (
        "CRenderThing__scalar_deleting_dtor",
        "void * __thiscall CRenderThing__scalar_deleting_dtor(void * this, byte flags)",
    ),
    "0x004dd960": (
        "CRTTree__VFuncSlot02_BuildRenderOutputs",
        "void __thiscall CRTTree__VFuncSlot02_BuildRenderOutputs(void * this, void * renderContext)",
    ),
    "0x004de050": (
        "CRTTree__VFuncSlot06_GetResourceScalar164",
        "float __fastcall CRTTree__VFuncSlot06_GetResourceScalar164(void * this)",
    ),
    "0x004de060": (
        "SharedVFunc__ReturnResourceField150_004de060",
        "void * __fastcall SharedVFunc__ReturnResourceField150_004de060(void * this)",
    ),
}

COMMENT_TOKENS = {
    "0x004db880": ("Wave497", "this+0x10", "+0x68", "CRTTree slot 26"),
    "0x004dbb80": ("Wave489", "0x0083ccd8", "RET 0x18"),
    "0x004dbbe0": ("Wave489", "RET 0x8", "clears three dwords"),
    "0x004dbd20": ("Wave489", "destructor body", "not as a constructor", "0x005deaac"),
    "0x004dbd50": ("Wave489", "scalar deleting destructor", "CDXMemoryManager__Free"),
    "0x004dd960": ("Wave497", "0x005deb9c slot 2", "DAT_0083cd58"),
    "0x004de050": ("Wave497", "0x005deb9c slot 6", "resource+0x164"),
    "0x004de060": ("Wave497", "CRTMesh/CRTTree", "resource+0x150"),
}

DECOMPILE_TOKENS = {
    "0x004db880": ("0x10", "0x68"),
    "0x004dbb80": ("0x0083ccd8",),
    "0x004dbbe0": ("out_vec3",),
    "0x004dbd20": ("0x005deaac",),
    "0x004dbd50": ("CDXMemoryManager__Free", "DAT_009c3df0"),
    "0x004dd960": ("DAT_0083cd58", "CDXEngine__SetWorldMatrixElements", "CSphere__RenderAnimatedRecursive"),
    "0x004de050": ("0x164",),
    "0x004de060": ("0x150",),
}

COMMON_TAGS = {"static-reaudit", "retail-binary-evidence"}
TAG_TOKENS = {
    "0x004db880": ("crenderthing", "crttree-wave497", "shared-vfunc"),
    "0x004dbb80": ("crenderthing", "rtcutscene-wave489", "render-output"),
    "0x004dbbe0": ("crenderthing", "rtcutscene-wave489", "clear-vec3"),
    "0x004dbd20": ("crenderthing", "rtcutscene-wave489", "destructor"),
    "0x004dbd50": ("crenderthing", "rtcutscene-wave489", "scalar-deleting-dtor"),
    "0x004dd960": ("crttree", "crttree-wave497", "render-output"),
    "0x004de050": ("crttree", "crttree-wave497", "float-getter"),
    "0x004de060": ("crttree", "rtmesh", "shared-vfunc"),
}

XREFS = {
    "0x004db880": {"0x005dea28", "0x005deaa0", "0x005deb14", "0x005deb84", "0x005dec04"},
    "0x004dbb80": {"0x005dea54", "0x005deac8", "0x005debb8"},
    "0x004dbbe0": {"0x005dea58", "0x005deacc", "0x005debbc"},
    "0x004dbd20": {"0x005d4a33", "0x005d4a83", "0x005d4aa3"},
    "0x004dbd50": {"0x005deaac"},
    "0x004dd960": {"0x005deba4"},
    "0x004de050": {"0x005debb4"},
    "0x004de060": {"0x005deb2c", "0x005debac"},
}

VTABLE_POINTERS = {
    ("0x005dea38", "0x004dbb80"),
    ("0x005dea38", "0x004dbbe0"),
    ("0x005dea38", "0x004db880"),
    ("0x005dea38", "0x004dbd50"),
    ("0x005deaac", "0x004dbd50"),
    ("0x005deaac", "0x004dbb80"),
    ("0x005deaac", "0x004dbbe0"),
    ("0x005deaac", "0x004db880"),
    ("0x005deaac", "0x004de060"),
    ("0x005deb1c", "0x004de060"),
    ("0x005deb1c", "0x004db880"),
    ("0x005deb1c", "0x004dd960"),
    ("0x005deb9c", "0x004dd960"),
    ("0x005deb9c", "0x004de060"),
    ("0x005deb9c", "0x004de050"),
    ("0x005deb9c", "0x004dbb80"),
    ("0x005deb9c", "0x004dbbe0"),
    ("0x005deb9c", "0x004db880"),
}

DOC_TOKENS = (
    "Wave1046",
    "renderthing-crttree-review-wave1046",
    "0x004db880 CRenderThing__ForwardSlot26ToChildSlot68",
    "0x004dbb80 CRenderThing__VFunc_07_ClearRenderOutputs",
    "0x004dbbe0 CRenderThing__VFunc_08_ClearVec3",
    "0x004dbd20 CRenderThing__dtor",
    "0x004dbd50 CRenderThing__scalar_deleting_dtor",
    "0x004dd960 CRTTree__VFuncSlot02_BuildRenderOutputs",
    "0x004de050 CRTTree__VFuncSlot06_GetResourceScalar164",
    "0x004de060 SharedVFunc__ReturnResourceField150_004de060",
    "0x005dea38",
    "0x005deaac",
    "0x005deb1c",
    "0x005deb9c",
    "DAT_0083cd58",
    "0x0083ccd8",
    "0x004b6260 CSphere__RenderAnimatedRecursive",
    "735/1408 = 52.20%",
    "993/1509 = 65.81%",
    "500/500 = 100.00%",
    "6246/6246 = 100.00%",
    BACKUP_PATH,
    "no mutation",
)

OVERCLAIMS = (
    "runtime tree behavior proven",
    "runtime cutscene behavior proven",
    "runtime render behavior proven",
    "exact source-body identity proven",
    "rebuild parity proven",
    "fully reverse-engineered",
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


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def read_json(path: Path):
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
        "metadata.tsv": 8,
        "tags.tsv": 8,
        "xrefs.tsv": 19,
        "instructions.tsv": 429,
        "decompile/index.tsv": 8,
        "vtable-slots.tsv": 144,
        "context-metadata.tsv": 20,
        "context-tags.tsv": 20,
        "context-xrefs.tsv": 1087,
        "context-instructions.tsv": 1090,
        "context-decompile/index.tsv": 20,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "decompile" / "index.tsv")}
    xrefs: dict[str, set[str]] = {}
    for row in read_tsv(BASE / "xrefs.tsv"):
        xrefs.setdefault(normalize_address(row["target_addr"]), set()).add(normalize_address(row["from_addr"]))
    vtable_pairs = {
        (normalize_address(row["vtable"]), normalize_address(row["pointer_addr"]))
        for row in read_tsv(BASE / "vtable-slots.tsv")
        if row.get("status") == "OK"
    }

    for address, (name, signature) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata at {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in COMMENT_TOKENS[address]:
                require(token in row.get("comment", ""), f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tag row at {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual_tags), f"missing common tags at {address}: {COMMON_TAGS - actual_tags}", failures)
            for token in TAG_TOKENS[address]:
                require(token in actual_tags, f"missing tag at {address}: {token}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch at {address}", failures)

        dec = decompile.get(address)
        require(dec is not None and dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
        text = read_text(BASE / "decompile" / f"{address[2:]}_{name}.c")
        for token in DECOMPILE_TOKENS[address]:
            require(token in text, f"missing decompile token at {address}: {token}", failures)

        require(XREFS[address].issubset(xrefs.get(address, set())), f"xref sources mismatch at {address}", failures)

    for pair in VTABLE_POINTERS:
        require(pair in vtable_pairs, f"missing vtable pointer pair {pair}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "metadata.log": "targets=8 found=8 missing=0",
        "tags.log": "ExportFunctionTagsByAddress complete: rows=8 missing=0",
        "xrefs.log": "Wrote 19 rows",
        "instructions.log": "Wrote 429 function-body instruction rows",
        "decompile.log": "targets=8 dumped=8 missing=0 failed=0",
        "vtable-slots.log": "ExportVtableSlots complete: targets=4 rows=144",
        "context-metadata.log": "targets=20 found=20 missing=0",
        "context-tags.log": "ExportFunctionTagsByAddress complete: rows=20 missing=0",
        "context-xrefs.log": "Wrote 1087 rows",
        "context-instructions.log": "Wrote 1090 function-body instruction rows",
        "context-decompile.log": "targets=20 dumped=20 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_queue_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("totalFunctions") == 6246, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "commentless count mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "undefined signature count mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "param_N count mismatch", failures)

    backup = read_json(BACKUP_SUMMARY)
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 174590855 or backup.get("totalBytes") == 174590855.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = [
        PUBLIC_NOTE,
        AGGREGATE_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        RTCUTSCENE_DOC: ("Wave1046", "0x004dbb80 CRenderThing__VFunc_07_ClearRenderOutputs", "0x004dbd50 CRenderThing__scalar_deleting_dtor", BACKUP_PATH),
        TREE_DOC: ("Wave1046", "0x004dd960 CRTTree__VFuncSlot02_BuildRenderOutputs", "DAT_0083cd58", BACKUP_PATH),
        PCRTID_DOC: ("Wave1046", "0x004db880 CRenderThing__ForwardSlot26ToChildSlot68", "0x005deb9c", BACKUP_PATH),
        RTMESH_DOC: ("Wave1046", "0x004de060 SharedVFunc__ReturnResourceField150_004de060", "0x005deb1c", BACKUP_PATH),
    }
    for path, tokens in owner_docs.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    require(
        scripts.get("test:ghidra-renderthing-crttree-review-wave1046")
        == r"py -3 tools\ghidra_renderthing_crttree_review_wave1046_probe.py --check",
        "missing Wave1046 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1046-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1046 --check",
        "missing Wave1046 aggregate recheck package script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempt_rows = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1046 renderthing crttree review" for row in ledger_rows), "missing Wave1046 ledger row", failures)
    require(any(row.get("task") == "Wave1046 renderthing crttree review" for row in attempt_rows), "missing Wave1046 attempt row", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_queue_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1046 RenderThing / CRTTree review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Wave1046 RenderThing / CRTTree review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
