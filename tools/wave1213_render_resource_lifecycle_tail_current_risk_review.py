#!/usr/bin/env python3
"""Validate Wave1213 render-resource lifecycle tail current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1213-render-resource-lifecycle-tail-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1213-render-resource-lifecycle-tail-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1213-render-resource-lifecycle-tail-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1213_render_resource_lifecycle_tail_current_risk_review_2026-06-07.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
ACCOUNTING = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-accounting-guard.md"
MEASUREMENT_REGISTER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-measurement-register.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RENDER_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "mesh-resource-render-static-contract.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
CIBUFFER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ibuffer.cpp" / "_index.md"
DXLANDSCAPE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXLandscape.cpp" / "_index.md"
DXSURF_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXSurf.cpp" / "CDXSurf__UnlinkNodeFromGlobalList.md"
DXBATTLELINE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "DXBattleLine.cpp.md"
PACKAGE_JSON = ROOT / "package.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260607-074242_post_wave1213_render_resource_lifecycle_tail_current_risk_review_verified"

TARGETS = {
    "0x00488330": (
        "CIBuffer__CreateConfigured",
        "int __thiscall CIBuffer__CreateConfigured(void * this, int size_bytes, int usage_flags, int index_format, int buffer_type)",
        ("CVBufTexture__ResizeIndexBuffer", "CDXLandscape__Init", "RET\t0x10"),
    ),
    "0x004885e0": (
        "CIBuffer__LockDirect",
        "int __thiscall CIBuffer__LockDirect(void * this, void * * out_data)",
        ("CVBufTexture__AddIndices", "CDXLandscape__UpdateLOD", "0x2800", "0x800"),
    ),
    "0x004f2790": (
        "CDXSurf__UnlinkNodeFromGlobalList",
        "void __fastcall CDXSurf__UnlinkNodeFromGlobalList(void * texture_base)",
        ("DAT_0083d9b0", "0xa0", "texture_base-0x08"),
    ),
    "0x0053a140": (
        "CDXBattleLine__DestructorThunk",
        "void __fastcall CDXBattleLine__DestructorThunk(void * this)",
        ("JMP\t0x00556d90", "CDXSurf__dtor", "CDXBattleLine__scalar_deleting_dtor"),
    ),
    "0x00544a60": (
        "CDXLandscape__Destructor",
        "void __fastcall CDXLandscape__Destructor(void * this)",
        ("0x005e50d0", "CShaderBase__UnlinkFromRenderObjectLists", "CDXLandscape__ReleaseMixerDetailTextureRef"),
    ),
    "0x00544eb0": (
        "CDXLandscape__ReleaseBuffers",
        "int __fastcall CDXLandscape__ReleaseBuffers(void * this)",
        ("0x005e50e0", "IUnknown__ReleaseAndNull", "return 0"),
    ),
}

TARGET_XREFS = {
    "0x00488330": (("00500887", "UNCONDITIONAL_CALL"), ("00544c52", "UNCONDITIONAL_CALL")),
    "0x004885e0": (("005008bb", "UNCONDITIONAL_CALL"), ("00500afa", "UNCONDITIONAL_CALL"), ("00546d95", "UNCONDITIONAL_CALL")),
    "0x004f2790": (("00556e70", "UNCONDITIONAL_CALL"), ("005d7d36", "UNCONDITIONAL_CALL"), ("005d7d81", "UNCONDITIONAL_CALL")),
    "0x0053a140": (("0053a123", "UNCONDITIONAL_CALL"),),
    "0x00544a60": (("00544a43", "UNCONDITIONAL_CALL"),),
    "0x00544eb0": (("005e50e0", "DATA"),),
}

DOC_TOKENS = (
    "Wave1213",
    "wave1213-render-resource-lifecycle-tail-current-risk-review",
    "6 render-resource lifecycle tail current-risk rows",
    "1125/1179 = 95.42%",
    "remaining active focused work: 54",
    "1156/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current focused candidates: 1127",
    "live regenerated current focused candidates: 1127",
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
    "no Cursor/Composer",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "13 xref rows",
    "152 instruction rows",
    "6 decompile rows",
    "41 context xref rows",
    "1369 context instruction rows",
    "15 context decompile rows",
    BACKUP,
    "static-reaudit-current-risk-ledger.json",
    "static-reaudit-measurement-register.md",
    "mesh-resource-render-static-contract.md",
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "continuity denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

OWNER_DOC_TOKENS = {
    CIBUFFER_DOC: ("Wave1213", "CIBuffer__CreateConfigured", "CIBuffer__LockDirect", BACKUP),
    DXLANDSCAPE_DOC: ("Wave1213", "CDXLandscape__Destructor", "CDXLandscape__ReleaseBuffers", BACKUP),
    DXSURF_DOC: ("Wave1213", "CDXSurf__UnlinkNodeFromGlobalList", BACKUP),
    DXBATTLELINE_DOC: ("Wave1213", "CDXBattleLine__DestructorThunk", BACKUP),
}

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime direct3d behavior proven",
    "runtime terrain/hud output proven",
    "runtime lost-device behavior proven",
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
        "pre-xrefs.tsv": 13,
        "pre-instructions.tsv": 152,
        "pre-decompile/index.tsv": 6,
        "context-metadata.tsv": 15,
        "context-tags.tsv": 15,
        "context-xrefs.tsv": 41,
        "context-instructions.tsv": 1369,
        "context-decompile/index.tsv": 15,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-tags.tsv")}
    xrefs = read_tsv(BASE / "pre-xrefs.tsv")
    evidence_text = (
        read_text(BASE / "pre-metadata.tsv")
        + read_text(BASE / "pre-instructions.tsv")
        + read_text(BASE / "pre-decompile" / "00488330_CIBuffer__CreateConfigured.c")
        + read_text(BASE / "pre-decompile" / "004885e0_CIBuffer__LockDirect.c")
        + read_text(BASE / "pre-decompile" / "004f2790_CDXSurf__UnlinkNodeFromGlobalList.c")
        + read_text(BASE / "pre-decompile" / "0053a140_CDXBattleLine__DestructorThunk.c")
        + read_text(BASE / "pre-decompile" / "00544a60_CDXLandscape__Destructor.c")
        + read_text(BASE / "pre-decompile" / "00544eb0_CDXLandscape__ReleaseBuffers.c")
        + read_text(BASE / "context-metadata.tsv")
        + read_text(BASE / "context-instructions.tsv")
    )

    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in ("Static", "evidence only"):
                require(token in row.get("comment", ""), f"missing bounded comment token at {address}: {token}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tag row for {address}", failures)
        if tag_row is not None:
            actual_tags = set(tag_row.get("tags", "").split(";"))
            require("static-reaudit" in actual_tags, f"missing static-reaudit tag at {address}", failures)
            require("retail-binary-evidence" in actual_tags, f"missing retail-binary-evidence tag at {address}", failures)

        for from_addr, ref_type in TARGET_XREFS[address]:
            require(
                any(
                    normalize_address(row.get("target_addr", "")) == address
                    and row.get("from_addr") == from_addr
                    and row.get("ref_type") == ref_type
                    for row in xrefs
                ),
                f"missing xref {from_addr} {ref_type} for {address}",
                failures,
            )
        for token in tokens:
            require(contains_token(evidence_text, token), f"missing evidence token for {address}: {token}", failures)

    logs = {
        "pre-metadata.log": "targets=6 found=6 missing=0",
        "pre-tags.log": "rows=6 missing=0",
        "pre-xrefs.log": "Wrote 13 rows",
        "pre-instructions.log": "Wrote 152 function-body instruction rows",
        "pre-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "context-metadata.log": "targets=15 found=15 missing=0",
        "context-tags.log": "rows=15 missing=0",
        "context-xrefs.log": "Wrote 41 rows",
        "context-instructions.log": "Wrote 1369 function-body instruction rows",
        "context-decompile.log": "targets=15 dumped=15 missing=0 failed=0",
    }
    for relative, token in logs.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "BADADDR", "MISSING", "FAIL", "missing=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)


def check_backup_and_progress(failures: list[str]) -> None:
    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176425863 or backup.get("totalBytes") == 176425863.0, "backup bytes mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current.get("focusedReviewed") == 1125, "progress focused reviewed mismatch", failures)
    require(current.get("focusedReviewedPercent") == "95.42%", "progress percent mismatch", failures)
    require(current.get("remainingFocusedAfterLatestReview") == 54, "progress remaining mismatch", failures)
    require(current.get("latestReviewTag") == "wave1213-render-resource-lifecycle-tail-current-risk-review", "latest review tag mismatch", failures)

    ledger = read_json(LEDGER)
    require(ledger.get("correctedUniqueReviewed") == 1125, "ledger reviewed mismatch", failures)
    require(ledger.get("remainingUnique") == 54, "ledger remaining mismatch", failures)
    require(ledger.get("latestWaveTag") == "wave1213-render-resource-lifecycle-tail-current-risk-review", "ledger latest tag mismatch", failures)


def check_docs(failures: list[str]) -> None:
    docs = [
        NOTE,
        READINESS,
        PROGRESS,
        ACCOUNTING,
        MEASUREMENT_REGISTER,
        MAPPED,
        CAMPAIGN,
        RENDER_CONTRACT,
        RANK,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        for bad in OVERCLAIMS:
            require(bad not in text.lower(), f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    for path, tokens in OWNER_DOC_TOKENS.items():
        text = read_text(path)
        for token in tokens:
            require(contains_token(text, token), f"missing owner-doc token in {path.relative_to(ROOT)}: {token}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "wave note mirror mismatch", failures)
    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1213-render-resource-lifecycle-tail-current-risk-review")
        == r"py -3 tools\wave1213_render_resource_lifecycle_tail_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_backup_and_progress(failures)
    check_docs(failures)

    if failures:
        print("Wave1213 render-resource lifecycle tail current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1213 render-resource lifecycle tail current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
