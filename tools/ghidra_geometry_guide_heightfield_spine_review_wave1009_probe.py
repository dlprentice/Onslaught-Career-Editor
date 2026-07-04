#!/usr/bin/env python3
"""Validate Wave1009 geometry / guide / heightfield spine review artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1009-geometry-guide-heightfield-spine-review"
NOTE = ROOT / "release" / "readiness" / "ghidra_geometry_guide_heightfield_spine_review_wave1009_2026-05-31.md"
RECHECK_NOTE = ROOT / "release" / "readiness" / "ghidra_wave900_plus_through_wave1009_recheck_2026-05-31.md"
PACKAGE_JSON = ROOT / "package.json"
GHIDRA_REFERENCE = ROOT / "reverse-engineering" / "binary-analysis" / "GHIDRA-REFERENCE.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
BACKLOG = ROOT / "reverse-engineering" / "binary-analysis" / "MCP-MUTATION-BACKLOG.md"
DROPSHIP_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Dropship.cpp" / "_index.md"
GUIDE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Guide.cpp" / "_index.md"
HEIGHTFIELD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "HeightField.cpp" / "_index.md"
STATIC_SHADOWS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "StaticShadows.cpp" / "_index.md"
SQUAD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SquadNormal.cpp" / "_index.md"
RELAXED_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "SquadRelaxed.cpp" / "_index.md"
TENTACLE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Tentacle.cpp" / "_index.md"
ISCRIPT_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "IScript.cpp.md"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_ledger.jsonl"
ATTEMPT_LOG = ROOT / "reverse-engineering" / "binary-analysis" / "function_mutation_attempt_log.jsonl"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"

BACKUP_PATH = r"[maintainer-local-ghidra-backup-root]\BEA_20260531-155648_post_wave1009_geometry_guide_heightfield_spine_review_verified"

TARGETS = {
    "0x00448580": (
        "CDropshipAI__VFunc_09_00448580",
        "void __thiscall CDropshipAI__VFunc_09_00448580(void * this, void * context)",
        "0x005db218",
        ("CDropshipAI", "CStaticShadows__SampleShadowHeightBilinear", "0x006fadc8"),
    ),
    "0x00448930": (
        "CDropshipGuide__VFunc_03_00448930",
        "void __fastcall CDropshipGuide__VFunc_03_00448930(void * this)",
        "0x005db234",
        ("CDropshipGuide", "guide", "0x006fadc8"),
    ),
    "0x004dfaa0": (
        "VFuncSlot_09_004dfaa0",
        "void __fastcall VFuncSlot_09_004dfaa0(void * this)",
        "0x005dfe44",
        ("Owner remains conservatively bounded", "pickup", "0x006fadc8"),
    ),
    "0x004e9600": (
        "CSquadNormal__VFunc_20_004e9600",
        "void __thiscall CSquadNormal__VFunc_20_004e9600(void * this, void * position)",
        "0x005df144",
        ("CNormalSquad", "CThing__Teleport", "this+0xa4"),
    ),
    "0x004e96f0": (
        "CSquadNormal__VFunc_21_004e96f0",
        "void __thiscall CSquadNormal__VFunc_21_004e96f0(void * this, void * orientation)",
        "0x005df148",
        ("CNormalSquad", "CComplexThing__TeleportOrientation", "virtual slot +0x54"),
    ),
    "0x004e9f00": (
        "CSquadNormal__VFunc_52_004e9f00",
        "void __fastcall CSquadNormal__VFunc_52_004e9f00(void * this)",
        "0x005df1c4",
        ("CUnit__RenderWithIdentityWorldAndShadowProbe", "CDXEngine", "debug"),
    ),
    "0x004eaae0": (
        "CRelaxedSquad__VFunc_07_004eaae0",
        "void __fastcall CRelaxedSquad__VFunc_07_004eaae0(void * this)",
        "0x005e3a9c",
        ("relaxed-squad", "CThing__RenderDebugVolumeOverlay", "0x006fadc8"),
    ),
    "0x004f0e40": (
        "CTentacle__VFunc_22_004f0e40",
        "void __fastcall CTentacle__VFunc_22_004f0e40(void * this)",
        "0x005e3ff4",
        ("CTentacle", "Tentacle_Activation_Effect", "particle"),
    ),
    "0x0050a3a0": (
        "CWingmanStart__VFunc_09_0050a3a0",
        "void __thiscall CWingmanStart__VFunc_09_0050a3a0(void * this, void * init)",
        "0x005dcb7c",
        ("CWingmanStart", "Tara_Fighter", "Billy_Fighter"),
    ),
    "0x00534ac0": (
        "ScriptCommand__SampleStaticShadowHeight_00534ac0",
        "void __stdcall ScriptCommand__SampleStaticShadowHeight_00534ac0(void * script_value, void * unused_arg, void * out_result)",
        "0x00531270",
        ("ScriptCommandRegistry__InitBuiltins", "MissionScript.cpp", "0x2e3"),
    ),
}

PRE_EXISTING = {
    "0x00479630": "Geometry__RaySphereEntryDistance",
    "0x00479770": "Geometry__DistanceOutsideAabb",
    "0x0047e290": "CGuide__ctor_base",
    "0x0047eb80": "CStaticShadows__SampleShadowHeightBilinear",
    "0x0047ef20": "CHeightField__RecomputeGridExtentsAndHeightRange",
}

DOC_TOKENS = (
    "Wave1009",
    "geometry-guide-heightfield-spine-review-wave1009",
    "0x0047eb80 CStaticShadows__SampleShadowHeightBilinear",
    "0x00448580 CDropshipAI__VFunc_09_00448580",
    "0x00448930 CDropshipGuide__VFunc_03_00448930",
    "0x004dfaa0 VFuncSlot_09_004dfaa0",
    "0x004e9600 CSquadNormal__VFunc_20_004e9600",
    "0x004e96f0 CSquadNormal__VFunc_21_004e96f0",
    "0x004e9f00 CSquadNormal__VFunc_52_004e9f00",
    "0x004eaae0 CRelaxedSquad__VFunc_07_004eaae0",
    "0x004f0e40 CTentacle__VFunc_22_004f0e40",
    "0x0050a3a0 CWingmanStart__VFunc_09_0050a3a0",
    "0x00534ac0 ScriptCommand__SampleStaticShadowHeight_00534ac0",
    "499/1408 = 35.44%",
    "694/1488 = 46.64%",
    "403/500 = 80.60%",
    "6233/6233 = 100.00%",
    BACKUP_PATH,
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime dropship behavior proven",
    "runtime squad behavior proven",
    "runtime tentacle behavior proven",
    "runtime script behavior proven",
    "exact source method identity proven",
    "exact source-body identity proven",
    "exact layout proven",
    "full closure of every no-function static-shadow caller proven",
    "rebuild parity proven",
)


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


def normalize_address(value: str) -> str:
    value = value.strip().lower()
    if value.startswith("0x"):
        value = value[2:]
    return "0x" + value.zfill(8)


def row_by_address(rows: list[dict[str, str]], address: str, field: str = "address") -> dict[str, str] | None:
    target = normalize_address(address)
    for row in rows:
        if normalize_address(row.get(field, "")) == target:
            return row
    return None


def contains_token(text: str, token: str) -> bool:
    return (
        token in text
        or token.replace("\\", "\\\\") in text
        or token.replace("\\", "\\\\\\\\") in text
        or token.replace("\\\\", "\\") in text.replace("\\\\\\\\", "\\").replace("\\\\", "\\")
    )


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_artifacts(failures: list[str]) -> None:
    expected_counts = {
        "pre-metadata.tsv": 5,
        "pre-tags.tsv": 5,
        "pre-xrefs.tsv": 127,
        "pre-instructions.tsv": 423,
        "pre-decompile/index.tsv": 5,
        "context-metadata.tsv": 6,
        "context-xrefs.tsv": 38,
        "context-instructions.tsv": 1115,
        "context-decompile/index.tsv": 6,
        "callsite-instructions.tsv": 153,
        "no-function-shadow-xref-instructions.tsv": 1421,
        "no-function-shadow-xref-instructions-wide.tsv": 6989,
        "shadow-caller-boundary-candidate-entry-xrefs.tsv": 17,
        "shadow-caller-pointer-table-windows.tsv": 384,
        "shadow-caller-rtti-base-candidates.tsv": 237,
        "post-created-metadata.tsv": 10,
        "post-created-tags.tsv": 10,
        "post-created-xrefs.tsv": 10,
        "post-created-instructions.tsv": 2146,
        "post-created-decompile/index.tsv": 10,
        "final-metadata.tsv": 15,
        "final-tags.tsv": 15,
        "final-xrefs.tsv": 137,
        "final-instructions.tsv": 2569,
        "final-decompile/index.tsv": 15,
    }
    for relative, expected in expected_counts.items():
        actual = len(read_tsv(BASE / relative))
        require(actual == expected, f"{relative} row count {actual} != {expected}", failures)

    metadata = read_tsv(BASE / "final-metadata.tsv")
    tags = read_tsv(BASE / "final-tags.tsv")
    decompile_index = read_tsv(BASE / "final-decompile" / "index.tsv")
    xrefs = read_tsv(BASE / "final-xrefs.tsv")

    for address, name in PRE_EXISTING.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"metadata missing carried-forward {address}", failures)
        if row:
            require(row.get("name") == name, f"carried-forward name mismatch {address}", failures)
            require(row.get("status") == "OK", f"carried-forward status mismatch {address}", failures)

    for address, (name, signature, data_xref, comment_tokens) in TARGETS.items():
        row = row_by_address(metadata, address)
        require(row is not None, f"metadata missing recovered {address}", failures)
        if row:
            require(row.get("name") == name, f"metadata name mismatch {address}", failures)
            require(row.get("signature") == signature, f"metadata signature mismatch {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch {address}", failures)
            comment = row.get("comment", "")
            for token in ("Wave1009 boundary recovery", "Static retail evidence only", *comment_tokens):
                require(token in comment, f"comment token missing {address}: {token}", failures)

        tag_row = row_by_address(tags, address)
        require(tag_row is not None, f"tags missing {address}", failures)
        if tag_row:
            actual_tags = set(filter(None, tag_row.get("tags", "").split(";")))
            for tag in (
                "static-reaudit",
                "geometry-guide-heightfield-spine-review-wave1009",
                "wave1009-readback-verified",
                "function-boundary-recovered",
                "signature-hardened",
                "comment-hardened",
                "static-shadow",
            ):
                require(tag in actual_tags, f"missing tag {address}: {tag}", failures)
            require(tag_row.get("status") == "OK", f"tag status mismatch {address}", failures)

        dec = row_by_address(decompile_index, address)
        require(dec is not None, f"decompile missing {address}", failures)
        if dec:
            require(dec.get("name") == name, f"decompile name mismatch {address}", failures)
            require(dec.get("signature") == signature, f"decompile signature mismatch {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch {address}", failures)

        xref_row = row_by_address(xrefs, address, "target_addr")
        require(xref_row is not None, f"xref missing {address}", failures)
        if xref_row:
            require(normalize_address(xref_row.get("from_addr", "")) == data_xref, f"xref source mismatch {address}", failures)
            require(xref_row.get("ref_type") == "DATA", f"xref type mismatch {address}", failures)


def check_logs_queue_backup(failures: list[str]) -> None:
    expected_log_tokens = {
        "shadow-caller-boundary-create-dry.log": "CreateFunctionsFromAddressList complete: mode=dry targets=10 created=0 would_create=10 already_exists=0 renamed=0 would_rename=0 failed=0",
        "shadow-caller-boundary-create-apply.log": "CreateFunctionsFromAddressList complete: mode=apply targets=10 created=10 would_create=0 already_exists=0 renamed=10 would_rename=0 failed=0",
        "apply-hardening-dry.log": "SUMMARY updated=0 skipped=10 signature_updated=10 comment_updated=10 tag_updated=10 missing=0 bad=0",
        "apply-hardening.log": "SUMMARY updated=10 skipped=0 signature_updated=10 comment_updated=10 tag_updated=10 missing=0 bad=0",
        "apply-hardening-final-dry.log": "SUMMARY updated=0 skipped=10 signature_updated=0 comment_updated=0 tag_updated=0 missing=0 bad=0",
        "final-metadata.log": "targets=15 found=15 missing=0",
        "final-tags.log": "ExportFunctionTagsByAddress complete: rows=15 missing=0",
        "final-decompile.log": "targets=15 dumped=15 missing=0 failed=0",
        "quality-refresh.log": "total_functions=6233 commented_functions=6233",
    }
    for relative, token in expected_log_tokens.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token {relative}: {token}", failures)
        require("REPORT: Save succeeded" in text, f"missing save token in {relative}", failures)
        for bad in ("LockException", "BADADDR", "BADNAME", "MISSING:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {})
    require(queue.get("status") == "PASS", "queue status mismatch", failures)
    require(queue.get("totalFunctions") == 6233, "queue total mismatch", failures)
    require(quality.get("commentlessFunctionCount") == 0, "queue commentless mismatch", failures)
    require(quality.get("undefinedSignatureCount") == 0, "queue undefined mismatch", failures)
    require(quality.get("paramSignatureCount") == 0, "queue param_N mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP_PATH, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 173935495 or backup.get("totalBytes") == 173935495.0, "backup byte count mismatch", failures)
    for key in ("missingCount", "extraCount", "diffCount", "hashDiffCount"):
        require(backup.get(key) == 0, f"backup {key} mismatch", failures)


def check_docs(failures: list[str]) -> None:
    core_docs = (
        NOTE,
        RECHECK_NOTE,
        GHIDRA_REFERENCE,
        CAMPAIGN,
        FUNCTION_INDEX,
        FUNCTION_COVERAGE,
        BACKLOG,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    )
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    owner_docs = {
        DROPSHIP_DOC,
        GUIDE_DOC,
        HEIGHTFIELD_DOC,
        STATIC_SHADOWS_DOC,
        SQUAD_DOC,
        RELAXED_DOC,
        TENTACLE_DOC,
        ISCRIPT_DOC,
    }
    owner_required = {
        DROPSHIP_DOC: ("0x00448580 CDropshipAI__VFunc_09_00448580", "0x00448930 CDropshipGuide__VFunc_03_00448930"),
        GUIDE_DOC: ("0x0047e290 CGuide__ctor_base", "0x00448930 CDropshipGuide__VFunc_03_00448930"),
        HEIGHTFIELD_DOC: ("0x0047ef20 CHeightField__RecomputeGridExtentsAndHeightRange", "0x0047eb80 CStaticShadows__SampleShadowHeightBilinear"),
        STATIC_SHADOWS_DOC: ("0x0047eb80 CStaticShadows__SampleShadowHeightBilinear", "0x00534ac0 ScriptCommand__SampleStaticShadowHeight_00534ac0"),
        SQUAD_DOC: (
            "0x004e9600 CSquadNormal__VFunc_20_004e9600",
            "0x004e96f0 CSquadNormal__VFunc_21_004e96f0",
            "0x004e9f00 CSquadNormal__VFunc_52_004e9f00",
        ),
        RELAXED_DOC: ("0x004eaae0 CRelaxedSquad__VFunc_07_004eaae0",),
        TENTACLE_DOC: ("0x004f0e40 CTentacle__VFunc_22_004f0e40",),
        ISCRIPT_DOC: ("0x00534ac0 ScriptCommand__SampleStaticShadowHeight_00534ac0", "MissionScript.cpp"),
    }
    common_owner_tokens = (
        "Wave1009",
        "geometry-guide-heightfield-spine-review-wave1009",
        "6233/6233 = 100.00%",
        BACKUP_PATH,
    )
    for path in owner_docs:
        text = read_text(path)
        for token in (*common_owner_tokens, *owner_required[path]):
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    scripts = package.get("scripts", {})
    require(
        scripts.get("test:ghidra-geometry-guide-heightfield-spine-review-wave1009")
        == r"py -3 tools\ghidra_geometry_guide_heightfield_spine_review_wave1009_probe.py --check",
        "missing Wave1009 package script",
        failures,
    )
    require(
        scripts.get("test:ghidra-wave900-plus-through-wave1009-recheck")
        == r"py -3 tools\ghidra_wave900_plus_through_wave983_recheck.py --last-wave 1009 --check",
        "missing Wave1009 aggregate recheck script",
        failures,
    )

    ledger_rows = read_jsonl(LEDGER)
    attempts = read_jsonl(ATTEMPT_LOG)
    require(any(row.get("task") == "Wave1009 geometry guide heightfield spine review" for row in ledger_rows), "missing Wave1009 ledger row", failures)
    require(
        any(row.get("task") == "Wave1009 geometry guide heightfield spine review" and row.get("attempt_id") == 20591 for row in attempts),
        "missing Wave1009 attempt row",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_queue_backup(failures)
    check_docs(failures)
    if failures:
        print("Wave1009 geometry guide heightfield spine review probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1009 geometry guide heightfield spine review probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
