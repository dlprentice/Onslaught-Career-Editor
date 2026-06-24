#!/usr/bin/env python3
"""Validate Wave1150 particle-set/render-tail current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1150-particle-set-render-tail-current-risk-review"
FOCUSED_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.json"
RISK_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-risk-ranked-functions.json"
FOCUSED_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1108-current-risk-rank" / "wave1108-current-focused-candidates.tsv"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
QUEUE_TSV = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "functions_quality.tsv"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1150-particle-set-render-tail-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1150-particle-set-render-tail-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1150_particle_set_render_tail_current_risk_review_2026-06-05.md"
MAPPED_SYSTEMS = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MAPPED_SYSTEMS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
WAVE1108_NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
WAVE1108_READINESS = ROOT / "release" / "readiness" / "wave1108_current_risk_rank_2026-06-04.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
PARTICLE_DESCRIPTOR_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleDescriptor.cpp" / "_index.md"
PARTICLE_MANAGER_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleManager.cpp" / "_index.md"
PARTICLE_SET_DOC = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "ParticleSet.cpp" / "_index.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
PROGRESS_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
README = ROOT / "README.md"
AGENTS = ROOT / "AGENTS.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"

BACKUP = r"G:\GhidraBackups\BEA_20260605-194926_post_wave1150_particle_set_render_tail_current_risk_review_verified"
PRIOR_BACKUP = r"G:\GhidraBackups\BEA_20260605-192706_post_wave1149_particle_effects_score20_current_risk_review_verified"

TARGETS = {
    "0x004c0150": (
        "CParticle__ApplyParentTransformOrStoreLink",
        "void __stdcall CParticle__ApplyParentTransformOrStoreLink(void * particle, void * parent_particle, int link_parent_only)",
        ("parent_particle", "0xa0", "+0x58"),
    ),
    "0x004c14f0": (
        "CPDSimpleSprite__VFunc_10_004c14f0",
        "int __thiscall CPDSimpleSprite__VFunc_10_004c14f0(void * this, void * particle, int unused_context)",
        ("0x74", "0x80", "0x78"),
    ),
    "0x004c8040": (
        "CPDSimpleSprite__VFunc_23_004c8040",
        "void __fastcall CPDSimpleSprite__VFunc_23_004c8040(void * descriptor)",
        ("CPDSimpleSprite__InitNoiseTableOnce", "CPDSimpleSprite__ProcessAndRenderSpriteList"),
    ),
    "0x004ccb40": (
        "CParticleSet__shared_scalar_deleting_dtor",
        "void * __thiscall CParticleSet__shared_scalar_deleting_dtor(void * this, int flags)",
        ("CParticleSet__dtor_base", "CDXMemoryManager__Free"),
    ),
    "0x004ccc50": (
        "CPDSelector__DispatchChildVFunc20",
        "void __thiscall CPDSelector__DispatchChildVFunc20(void * this, int dispatch_context)",
        ("0x5c", "0x68", "dispatch_context"),
    ),
    "0x004cd290": (
        "CParticleSet__InitType11",
        "void __fastcall CParticleSet__InitType11(void * particle_set)",
        ("0x64", "0x74", "100"),
    ),
    "0x004cd2d0": (
        "CParticleSet__InitType12",
        "void __fastcall CParticleSet__InitType12(void * particle_set)",
        ("PTR_CParticleSet__shared_scalar_deleting_dtor_005ddfc8", "0x5c", "0x64"),
    ),
    "0x004cd3c0": (
        "CParticleSet__InitType13",
        "void __fastcall CParticleSet__InitType13(void * particle_set)",
        ("PTR_CParticleSet__shared_scalar_deleting_dtor_005de030", "180.0", "360.0"),
    ),
    "0x004cd7a0": (
        "CParticleSet__FindByNameAndTrackLinkSlot",
        "void * __thiscall CParticleSet__FindByNameAndTrackLinkSlot(void * this, char * set_name)",
        ("DAT_0082b3f8", "stricmp", "0x38"),
    ),
    "0x004cda60": (
        "CParticleSet__LoadParticleSetFile",
        "int __thiscall CParticleSet__LoadParticleSetFile(void * this, int particle_set_mode)",
        ("MainSet.par", "Frontend.par", "CParticleSet__LoadFromArchive"),
    ),
    "0x004cdbe0": (
        "CParticleManager__UnlinkNodeByOffset3C40",
        "void __thiscall CParticleManager__UnlinkNodeByOffset3C40(void * this, void * node)",
        ("0x3c", "0x40", "CParticleManager__UnlinkNodeFromActiveList"),
    ),
}

DOC_TOKENS = (
    "Wave1150",
    "wave1150-particle-set-render-tail-current-risk-review",
    "355/1179 = 30.11%",
    "11 current-risk rows",
    "current focused candidates: 1178",
    "live regenerated current focused candidates: 1178",
    "remaining active focused work: 824",
    "current risk candidates: 6166",
    "particle set/render tail current-risk review",
    "fresh Ghidra export",
    "particle parent-transform/link, simple-sprite vfunc 10/23, selector child vfunc dispatch, ParticleSet destructor/type init/load/name lookup, and manager offset +0x3c/+0x40 unlink helper",
    "read-only review",
    "no mutation",
    "no Codex subagent",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "CParticle__ApplyParentTransformOrStoreLink",
    "CPDSimpleSprite__VFunc_10_004c14f0",
    "CPDSimpleSprite__VFunc_23_004c8040",
    "CParticleSet__shared_scalar_deleting_dtor",
    "CPDSelector__DispatchChildVFunc20",
    "CParticleSet__InitType11",
    "CParticleSet__InitType12",
    "CParticleSet__InitType13",
    "CParticleSet__FindByNameAndTrackLinkSlot",
    "CParticleSet__LoadParticleSetFile",
    "CParticleManager__UnlinkNodeByOffset3C40",
    BACKUP,
    PRIOR_BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
)

OVERCLAIM_TOKENS = (
    "runtime particle behavior proven",
    "runtime effect behavior proven",
    "runtime render behavior proven",
    "runtime particleset loading proven",
    "runtime particle descriptor loading proven",
    "exact particle layout proven",
    "exact descriptor layout proven",
    "exact manager layout proven",
    "exact handle layout proven",
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
        "pre-metadata.tsv": 11,
        "pre-tags.tsv": 11,
        "pre-xrefs.tsv": 67,
        "pre-instructions.tsv": 565,
        "pre-decompile/index.tsv": 11,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-metadata.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "pre-decompile" / "index.tsv")}
    xref_targets = {normalize_address(row["target_addr"]) for row in read_tsv(BASE / "pre-xrefs.tsv")}
    evidence = "\n".join(row.get("comment", "") for row in metadata.values())
    evidence += "\n" + "\n".join(read_text(path) for path in (BASE / "pre-decompile").glob("*.c"))
    evidence += "\n" + "\n".join(
        f"{row.get('mnemonic','')} {row.get('operands','')}" for row in read_tsv(BASE / "pre-instructions.tsv")
    )
    compact = evidence.lower().replace(" ", "")

    for address, (name, signature, tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in tokens:
                token_ok = token.lower().replace(" ", "") in compact or token in evidence
                require(token_ok, f"missing evidence token at {address}: {token}", failures)
        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)
        require(address in xref_targets, f"missing xrefs for {address}", failures)

    for token in ("MainSet.par", "Frontend.par", "DAT_0082b3f8", "CParticleManager__UnlinkNodeFromActiveList"):
        require(token in evidence, f"missing global instruction/decompile token: {token}", failures)


def check_logs_and_backup(failures: list[str]) -> None:
    expected = {
        "pre-metadata.log": "targets=11 found=11 missing=0",
        "pre-tags.log": "ExportFunctionTagsByAddress complete: rows=11 missing=0",
        "pre-xrefs.log": "Wrote 67 rows",
        "pre-instructions.log": "Wrote 565 function-body instruction rows",
        "pre-decompile.log": "targets=11 dumped=11 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "SCRIPT ERROR", "BADADDR", "MISSING:", "BADNAME:", "BADSIG:", "FAIL:", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(int(backup.get("totalBytes")) == 175967111, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_queue_progress(failures: list[str]) -> None:
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
    require(read_json(RISK_JSON).get("candidateFunctions") == 6166, "current risk candidate mismatch", failures)
    require(read_json(FOCUSED_JSON).get("candidateFunctions") == 1178, "focused candidate mismatch", failures)
    focused_addresses = {normalize_address(row["address"]) for row in read_tsv(FOCUSED_TSV)}
    for address in TARGETS:
        require(address in focused_addresses, f"target absent from focused list: {address}", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    latest = progress["latestWave"]
    require(latest["wave"] == "Wave1150 particle set/render tail current-risk review", "progress latest wave mismatch", failures)
    require(latest["tag"] == "wave1150-particle-set-render-tail-current-risk-review", "progress latest tag mismatch", failures)
    require(latest["backup"] == BACKUP, "progress backup mismatch", failures)
    require(current["focusedReviewed"] == 355, "progress focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "30.11%", "progress focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 824, "progress remaining mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1178, "progress live focused mismatch", failures)


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
        PARTICLE_DESCRIPTOR_DOC,
        PARTICLE_MANAGER_DOC,
        PARTICLE_SET_DOC,
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

    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1150 note mirror mismatch", failures)
    require(read_text(MAPPED_SYSTEMS) == read_text(MAPPED_SYSTEMS_MIRROR), "mapped-systems mirror mismatch", failures)
    require(read_text(PROGRESS) == read_text(PROGRESS_MIRROR), "progress mirror mismatch", failures)
    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1150-particle-set-render-tail-current-risk-review")
        == r"py -3 tools\wave1150_particle_set_render_tail_current_risk_review.py --check",
        "missing package script",
        failures,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="run validation")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs_and_backup(failures)
    check_queue_progress(failures)
    check_docs(failures)
    if failures:
        print("Wave1150 particle-set/render-tail current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1150 particle-set/render-tail current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
