#!/usr/bin/env python3
"""Validate Wave1216 render/resource/texture/HUD tail current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1216-render-resource-texture-hud-tail-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1216-render-resource-texture-hud-tail-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1216-render-resource-texture-hud-tail-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1216_render_resource_texture_hud_tail_current_risk_review_2026-06-07.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
LEDGER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-current-risk-ledger.json"
ACCOUNTING = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-accounting-guard.md"
MEASUREMENT_REGISTER = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-measurement-register.md"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
MESH_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "mesh-resource-render-static-contract.md"
TEXTURE_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "texture-resource-decode-static-contract.md"
HUD_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "hud-frontend-overlay-static-contract.md"
THING_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "thing.cpp" / "_index.md"
TEXTURE_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "texture.cpp" / "_index.md"
HUD_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Hud.cpp" / "_index.md"
ATMOS_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "Atmospherics.cpp" / "_index.md"
MESH_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "mesh.cpp" / "_index.md"
PACKAGE_JSON = ROOT / "package.json"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"

BACKUP = r"G:\GhidraBackups\BEA_20260607-101007_post_wave1216_render_resource_texture_hud_tail_current_risk_review_verified"

TARGETS = {
    "0x004176c0": "CThing__InitRenderThingFromInitMeshName",
    "0x004c49b0": "CPDMesh__dtor_base",
    "0x00527de0": "CWaterRenderSystem__ResetAndMarkSourceFlag",
    "0x00555020": "CAtmosphericsProfile__ResetAndInitSnowResources",
    "0x0054b800": "CHudComponent__RenderPassEntry",
    "0x005997e1": "CTexture__NodeType11_Ctor_WithDescriptorCopy",
    "0x0059996f": "CTexture__NodeType12_Ctor_WithStackScalars",
}

POST_SIGNATURES = {
    "0x004176c0": "void __thiscall CThing__InitRenderThingFromInitMeshName(void * this, void * init)",
    "0x004c49b0": "void __fastcall CPDMesh__dtor_base(void * this)",
    "0x00527de0": "void __fastcall CWaterRenderSystem__ResetAndMarkSourceFlag(void * validation_record)",
    "0x00555020": "void __thiscall CAtmosphericsProfile__ResetAndInitSnowResources(void * this)",
    "0x0054b800": "void __cdecl CHudComponent__RenderPassEntry(void * mesh_entry, void * hud_component)",
    "0x005997e1": "int CTexture__NodeType11_Ctor_WithDescriptorCopy(void)",
    "0x0059996f": "int CTexture__NodeType12_Ctor_WithStackScalars(void)",
}

TEXTURE_CONTEXT = {
    "0x005997a5": "CFastVB__InitNodeType17",
    "0x00599831": "CTexture__NodeType11_Dtor_DeleteOnFlag_Body",
    "0x0059993c": "CTexture__NodeType12_Ctor",
    "0x005999b5": "CTexture__NodeType12_ScalarDeletingDtor_Body",
    "0x00599a3c": "CTexture__NodeType11_Dtor_DeleteOnFlag",
    "0x00599a58": "CTexture__NodeType12_ScalarDeletingDtor",
}

TEXTURE_TAGS = {
    "0x005997e1": ("node-type-0x11", "constructor", "descriptor-copy", "texture-node-label-corrected", "wave1216-readback-verified"),
    "0x0059996f": ("node-type-0x12", "constructor", "stack-scalars", "texture-node-label-corrected", "wave1216-readback-verified"),
    "0x00599831": ("node-type-0x11", "destructor-body", "texture-node-label-corrected", "wave1216-readback-verified"),
    "0x00599a3c": ("node-type-0x11", "scalar-deleting-dtor", "texture-node-label-corrected", "wave1216-readback-verified"),
}

DOC_TOKENS = (
    "Wave1216",
    "wave1216-render-resource-texture-hud-tail-current-risk-review",
    "7 render/resource/texture/HUD tail current-risk rows",
    "1145/1179 = 97.12%",
    "remaining active focused work: 34",
    "1176/1179",
    "26 duplicate-address overcount",
    "Wave1145 arithmetic overcount: 5",
    "current focused candidates: 1127",
    "live regenerated current focused candidates: 1127",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "texture label correction",
    "4 renamed",
    "4 comments updated",
    "25 tags added",
    "no signature change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consults used",
    "no Cursor/Composer",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "12 xref rows",
    "962 instruction rows",
    "7 decompile rows",
    "28 context xref rows",
    "1015 context instruction rows",
    "9 context decompile rows",
    "6 texture-context xref rows",
    "111 texture-context instruction rows",
    "6 texture-context decompile rows",
    "13 data-xref rows",
    "CTexture__NodeType11_Ctor_WithDescriptorCopy",
    "CTexture__NodeType11_Dtor_DeleteOnFlag_Body",
    "CTexture__NodeType11_Dtor_DeleteOnFlag",
    "CTexture__NodeType12_Ctor_WithStackScalars",
    BACKUP,
    "static-reaudit-current-risk-ledger.json",
    "static-reaudit-measurement-register.md",
    "mesh-resource-render-static-contract.md",
    "texture-resource-decode-static-contract.md",
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "continuity denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
)

OWNER_DOC_TOKENS = {
    THING_DOC: (
        "Wave1216",
        "wave1216-render-resource-texture-hud-tail-current-risk-review",
        "CThing__InitRenderThingFromInitMeshName",
        BACKUP,
    ),
    TEXTURE_DOC: (
        "Wave1216",
        "wave1216-render-resource-texture-hud-tail-current-risk-review",
        "CTexture__NodeType11_Ctor_WithDescriptorCopy",
        "CTexture__NodeType11_Dtor_DeleteOnFlag_Body",
        "CTexture__NodeType11_Dtor_DeleteOnFlag",
        "CTexture__NodeType12_Ctor_WithStackScalars",
        BACKUP,
    ),
    HUD_DOC: (
        "Wave1216",
        "wave1216-render-resource-texture-hud-tail-current-risk-review",
        "CHudComponent__RenderPassEntry",
        BACKUP,
    ),
    ATMOS_DOC: (
        "Wave1216",
        "wave1216-render-resource-texture-hud-tail-current-risk-review",
        "CAtmosphericsProfile__ResetAndInitSnowResources",
        BACKUP,
    ),
    MESH_DOC: (
        "Wave1216",
        "wave1216-render-resource-texture-hud-tail-current-risk-review",
        "CPDMesh__dtor_base",
        BACKUP,
    ),
}

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime texture behavior proven",
    "runtime hud behavior proven",
    "runtime render behavior proven",
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
        "pre-metadata.tsv": 7,
        "pre-tags.tsv": 7,
        "pre-xrefs.tsv": 12,
        "pre-instructions.tsv": 962,
        "pre-decompile/index.tsv": 7,
        "context-metadata.tsv": 9,
        "context-tags.tsv": 9,
        "context-xrefs.tsv": 28,
        "context-instructions.tsv": 1015,
        "context-decompile/index.tsv": 9,
        "texture-context-metadata.tsv": 6,
        "texture-context-tags.tsv": 6,
        "texture-context-xrefs.tsv": 6,
        "texture-context-instructions.tsv": 111,
        "texture-context-decompile/index.tsv": 6,
        "data-xrefs.tsv": 13,
        "post-metadata.tsv": 7,
        "post-tags.tsv": 7,
        "post-xrefs.tsv": 12,
        "post-instructions.tsv": 962,
        "post-decompile/index.tsv": 7,
        "post-context-metadata.tsv": 9,
        "post-context-tags.tsv": 9,
        "post-context-xrefs.tsv": 28,
        "post-context-instructions.tsv": 1015,
        "post-context-decompile/index.tsv": 9,
        "post-texture-context-metadata.tsv": 6,
        "post-texture-context-tags.tsv": 6,
        "post-texture-context-xrefs.tsv": 6,
        "post-texture-context-instructions.tsv": 111,
        "post-texture-context-decompile/index.tsv": 6,
        "post-data-xrefs.tsv": 13,
    }
    for relative, expected in expected_counts.items():
        rows = read_tsv(BASE / relative)
        require(len(rows) == expected, f"{relative} row count mismatch: {len(rows)} != {expected}", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    texture_metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-texture-context-metadata.tsv")}
    texture_tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-texture-context-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}

    for address, name in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing post metadata: {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == POST_SIGNATURES[address], f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            boundary_tokens = ("runtime", "rebuild parity remain unproven")
            if address in ("0x005997e1", "0x0059996f"):
                boundary_tokens = ("Wave1216 static read-back/name correction", "runtime", "rebuild parity remain unproven")
            for token in boundary_tokens:
                require(token.lower() in row.get("comment", "").lower(), f"comment boundary missing at {address}: {token}", failures)
        dec = decompile.get(address)
        require(dec is not None and dec.get("name") == name and dec.get("status") == "OK", f"decompile mismatch at {address}", failures)
        tag_row = tags.get(address)
        require(tag_row is not None and tag_row.get("status") == "OK", f"tag row mismatch at {address}", failures)

    for address, name in TEXTURE_CONTEXT.items():
        row = texture_metadata.get(address)
        require(row is not None, f"missing texture context metadata: {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"texture context name mismatch at {address}", failures)
            require(row.get("status") == "OK", f"texture context status mismatch at {address}", failures)

    combined_tags = {**tags, **texture_tags}
    for address, expected_tags in TEXTURE_TAGS.items():
        row = combined_tags.get(address)
        require(row is not None, f"missing texture tag row at {address}", failures)
        if row is not None:
            actual = set(row.get("tags", "").split(";"))
            for tag in expected_tags:
                require(tag in actual, f"missing tag at {address}: {tag}", failures)

    data_text = read_text(BASE / "post-data-xrefs.tsv")
    for token in (
        "005ef374",
        "CTexture__NodeType11_Ctor_WithDescriptorCopy",
        "CTexture__NodeType11_Dtor_DeleteOnFlag_Body",
        "005ef384",
        "CTexture__NodeType12_Ctor_WithStackScalars",
        "CTexture__NodeType12_Ctor",
        "00854dd8",
        "CWaterRenderSystem__ResetAndMarkSourceFlag",
    ):
        require(token in data_text, f"missing data-xref token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=4 signature_updated=0 comment_only_updated=4 tags_added=25 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=4 skipped=0 renamed=4 would_rename=0 signature_updated=0 comment_only_updated=4 tags_added=25 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=4 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=7 found=7 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=7 missing=0",
        "post-xrefs.log": "Wrote 12 rows",
        "post-instructions.log": "Wrote 962 function-body instruction rows",
        "post-decompile.log": "targets=7 dumped=7 missing=0 failed=0",
        "post-context-metadata.log": "targets=9 found=9 missing=0",
        "post-context-xrefs.log": "Wrote 28 rows",
        "post-context-instructions.log": "Wrote 1015 function-body instruction rows",
        "post-context-decompile.log": "targets=9 dumped=9 missing=0 failed=0",
        "post-texture-context-metadata.log": "targets=6 found=6 missing=0",
        "post-texture-context-xrefs.log": "Wrote 6 rows",
        "post-texture-context-instructions.log": "Wrote 111 function-body instruction rows",
        "post-texture-context-decompile.log": "targets=6 dumped=6 missing=0 failed=0",
        "post-data-xrefs.log": "Wrote 13 rows",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176425863 or backup.get("totalBytes") == 176425863.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_accounting_and_docs(failures: list[str]) -> None:
    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 1145, "progress reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "97.12%", "progress percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 34, "progress remaining mismatch", failures)
    require(current["legacyAdditiveReviewedDeprecated"] == 1176, "legacy additive mismatch", failures)
    require(current["duplicateAddressOvercountCorrected"] == 26, "duplicate overcount mismatch", failures)
    require(current["wave1145ArithmeticOvercountCorrected"] == 5, "Wave1145 overcount mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1127, "live focused mismatch", failures)
    require(current["latestReviewTag"] == "wave1216-render-resource-texture-hud-tail-current-risk-review", "latest review tag mismatch", failures)

    ledger = read_json(LEDGER)
    require(ledger["correctedUniqueReviewed"] == 1145, "ledger reviewed mismatch", failures)
    require(ledger["correctedUniquePercent"] == "97.12%", "ledger percent mismatch", failures)
    require(ledger["remainingUnique"] == 34, "ledger remaining mismatch", failures)
    require(ledger["countedRowsThroughWave1216"] == 1171, "ledger counted-row mismatch", failures)
    require(ledger["legacyAdditiveThroughWave1216Deprecated"] == 1176, "ledger legacy additive mismatch", failures)

    core_docs = [
        NOTE,
        NOTE_MIRROR,
        READINESS,
        PROGRESS,
        LEDGER,
        ACCOUNTING,
        MEASUREMENT_REGISTER,
        MAPPED,
        CAMPAIGN,
        RANK,
        MESH_CONTRACT,
        TEXTURE_CONTRACT,
        HUD_CONTRACT,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    owner_docs = [
        THING_DOC,
        TEXTURE_DOC,
        HUD_DOC,
        ATMOS_DOC,
        MESH_DOC,
    ]
    for path in core_docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)
    for path in owner_docs:
        text = read_text(path)
        for token in OWNER_DOC_TOKENS[path]:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lower = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lower, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "wave note mirror mismatch", failures)
    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1216-render-resource-texture-hud-tail-current-risk-review")
        == r"py -3 tools\wave1216_render_resource_texture_hud_tail_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_accounting_and_docs(failures)

    if failures:
        print("Wave1216 render/resource/texture/HUD tail current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1216 render/resource/texture/HUD tail current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
