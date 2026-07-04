#!/usr/bin/env python3
"""Validate Wave1193 top residual score20-18 current-risk artifacts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave1193-top-residual-score20-18-current-risk-review"
NOTE = ROOT / "reverse-engineering" / "binary-analysis" / "wave1193-top-residual-score20-18-current-risk-review.md"
NOTE_MIRROR = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "wave1193-top-residual-score20-18-current-risk-review.md"
READINESS = ROOT / "release" / "readiness" / "wave1193_top_residual_score20_18_current_risk_review_2026-06-06.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
CAMPAIGN = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-campaign.md"
RANK = ROOT / "reverse-engineering" / "binary-analysis" / "wave1108-current-risk-rank.md"
FUNCTION_COVERAGE = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "FUNCTION_COVERAGE_STATE.md"
FUNCTION_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "functions" / "_index.md"
BINARY_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
DEVELOPER_STATE = ROOT / "developer_agent_state.json"
DOCUMENTATION_STATE = ROOT / "documentation_agent_state.json"
RE_STATE = ROOT / "re_orchestrator_state.json"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
APPLY_SCRIPT = ROOT / "tools" / "ApplyTopResidualScoreCurrentRiskWave1193.java"

BACKUP = r"[maintainer-local-ghidra-backup-root]\BEA_20260606-185314_post_wave1193_top_residual_score20_18_current_risk_review_verified"

TARGETS = {
    "0x00424730": ("CCockpit__dtor_base", "void __fastcall CCockpit__dtor_base(void * this)", "score20", ("CCockpit destructor-base", "CMonitor__Shutdown")),
    "0x004df530": ("CShell__CopyResourceNameToInlineBuffer", "void __thiscall CShell__CopyResourceNameToInlineBuffer(void * this, char * resource_name)", "score20", ("ProjectileBurst__SpawnFromCurrentPreset", "this+0x110")),
    "0x0055da76": ("CRT__InitRuntimeFromStoredFrameGlobals", "void CRT__InitRuntimeFromStoredFrameGlobals(void)", "score20", ("CRT__InitFloatConversionDispatchTable", "DAT_009d08b8")),
    "0x0055dd7b": ("CRT__RunStaticInitRangesWithOptionalCallback", "void CRT__RunStaticInitRangesWithOptionalCallback(void)", "score20", ("CRT__InvokeFunctionPointerRange", "0x00622b10-0x00622b28")),
    "0x00562a89": ("CRT__SetErrnoForFpSourceKind", "void __cdecl CRT__SetErrnoForFpSourceKind(int sourceKind)", "score20", ("EDOM 0x21", "ERANGE 0x22")),
    "0x004014c0": ("SharedVFunc__NoOpOneArg_004014c0", "void __thiscall SharedVFunc__NoOpOneArg_004014c0(void * this, int arg0)", "score19", ("RET 0x4", "owner-neutral")),
    "0x00405930": ("SharedVFunc__ReturnZero_00405930", "int __thiscall SharedVFunc__ReturnZero_00405930(void * this)", "score19", ("integer zero", "owner-neutral")),
    "0x00452b60": ("CFrontEndPage__Process_NoOp", "void __thiscall CFrontEndPage__Process_NoOp(void * this, int state)", "score19", ("RET 0x4", "frontend page")),
    "0x00453ac0": ("SharedVFunc__NoOp_Ret0C", "void __stdcall SharedVFunc__NoOp_Ret0C(int unused0, int unused1, int unused2)", "score19", ("RET 0x0c", "owner-neutral")),
    "0x0047e6e0": ("CHazard__VFunc02_CleanupWorldSoundAndLinkedState", "void __fastcall CHazard__VFunc02_CleanupWorldSoundAndLinkedState(void * this)", "score19", ("kill hazard sound samples", "world occupancy grid")),
    "0x004bac10": ("CMissile__DispatchLinkedObjectVFunc68AndPostHook", "void __thiscall CMissile__DispatchLinkedObjectVFunc68AndPostHook(void * this, int arg0, int arg1)", "score19", ("this+0x30", "vfunc +0x68")),
    "0x004f45c0": ("SharedVFunc__ForwardField64FloatOrZero_004f45c0", "float __thiscall SharedVFunc__ForwardField64FloatOrZero_004f45c0(void * this)", "score19", ("this+0x64", "tail-jumps to 0x004048c0")),
    "0x0050a3a0": ("CWingmanStart__VFunc_09_0050a3a0", "void __thiscall CWingmanStart__VFunc_09_0050a3a0(void * this, void * init)", "score19", ("0x006fadc8", "Tara_Fighter")),
    "0x00541f00": ("CDXGame__dtor_thunk", "void __fastcall CDXGame__dtor_thunk(void * this)", "score19", ("unconditional jump to CGame__dtor", "CDXGame")),
    "0x0055e412": ("CRT__SpawnPathVarargsNoEnv_Thunk", "void __cdecl CRT__SpawnPathVarargsNoEnv_Thunk(int spawnMode, char * commandPath)", "score19", ("null environment pointer", "CRT__SpawnSearchPathWithFallbackExtensions")),
    "0x00421ba0": ("CCarrierAI__dtor_base", "void __fastcall CCarrierAI__dtor_base(void * this)", "score18", ("this+0x28", "CMonitor__Shutdown")),
    "0x00444660": ("CDestructableSegmentsController__Init", "void __fastcall CDestructableSegmentsController__Init(void * this)", "score18", ("CUnit__Init", "mesh root")),
    "0x00462640": ("CFEPMain__Process", "void __thiscall CFEPMain__Process(void * this, int state)", "score18", ("CCareer__Save", "CFEPOptions__WriteDefaultOptionsFile")),
    "0x0047c730": ("CGroundUnit__Init", "void __thiscall CGroundUnit__Init(void * this, void * init_data)", "score18", ("CUnit__Init", "Thruster markers")),
    "0x0047d420": ("CUnitAI__QueueFiringOrPostfireAnimation", "void __fastcall CUnitAI__QueueFiringOrPostfireAnimation(void * this)", "score18", ("CUnitAI__FinalizeSpawnAndAdvanceState", "vfunc +0xf0")),
    "0x00504510": ("CWarspite__Destructor", "void __fastcall CWarspite__Destructor(void * this)", "score18", ("0x005d8d1c", "CMonitor__Shutdown")),
    "0x005049b0": ("CWarspiteDome__Destructor", "void __fastcall CWarspiteDome__Destructor(void * this)", "score18", ("0x005d8d1c", "CMonitor__Shutdown")),
    "0x0050ed80": ("CBigAirUnit__ctor_base", "void * __fastcall CBigAirUnit__ctor_base(void * this)", "score18", ("CWorldPhysicsManager__CreateThingByType", "CWorldPhysicsManager__PushNodeGlobalList")),
    "0x00579273": ("CTexture__BuildTransformMatrixWithOptionalOffsets", "int CTexture__BuildTransformMatrixWithOptionalOffsets(void)", "score18", ("RET 0x1c", "CVertexShader__DispatchTableCall_656fc4")),
}

COMMON_TAGS = {
    "static-reaudit",
    "wave1193-top-residual-score20-18-current-risk-review",
    "wave1193-readback-verified",
    "retail-binary-evidence",
    "current-risk-review",
    "top-residual-score20-18",
    "source-identity-deferred",
    "exact-layout-deferred",
    "runtime-behavior-deferred",
    "rebuild-grade-static-contract",
    "no-noticeable-difference-boundary",
    "comment-hardened",
    "tag-normalized",
}

DOC_TOKENS = (
    "Wave1193",
    "wave1193-top-residual-score20-18-current-risk-review",
    "856/1179 = 72.60%",
    "24 top residual score20-18 current-risk rows",
    "score20 residual rows: 5",
    "score19 residual rows: 10",
    "score18 residual rows: 9",
    "current focused candidates: 1154",
    "live regenerated current focused candidates: 1154",
    "remaining active focused work: 323",
    "current risk candidates: 6166",
    "fresh Ghidra export",
    "comment/tag normalization",
    "updated=24 skipped=0",
    "comment_only_updated=24",
    "tags_added=319",
    "final dry updated=0 skipped=24",
    "no rename",
    "no signature change",
    "no function-boundary change",
    "no executable-byte change",
    "Codex read-only consults used",
    "no Cursor/Composer",
    "CCockpit__dtor_base",
    "CRT__RunStaticInitRangesWithOptionalCallback",
    "SharedVFunc__ReturnZero_00405930",
    "CHazard__VFunc02_CleanupWorldSoundAndLinkedState",
    "CDestructableSegmentsController__Init",
    "CFEPMain__Process",
    "CUnitAI__QueueFiringOrPostfireAnimation",
    "CTexture__BuildTransformMatrixWithOptionalOffsets",
    "0 / 0 / 0",
    "6411/6411 = 100.00%",
    "1554 xref rows",
    "1386 instruction rows",
    "24 decompile rows",
    BACKUP,
    "wave1108-current-risk-rank",
    "current-risk denominator",
    "focused threshold `15`",
    "not Wave911 reconstruction",
    "rebuild-grade static contracts",
    "no noticeable difference",
    "rebuild-grade specification",
)

OVERCLAIMS = (
    "runtime behavior proven",
    "runtime cleanup behavior proven",
    "runtime frontend behavior proven",
    "runtime projectile-shell behavior proven",
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
        "pre-metadata.tsv": 24,
        "pre-tags.tsv": 24,
        "pre-xrefs.tsv": 1554,
        "pre-instructions.tsv": 1386,
        "pre-decompile/index.tsv": 24,
        "post-metadata.tsv": 24,
        "post-tags.tsv": 24,
        "post-xrefs.tsv": 1554,
        "post-instructions.tsv": 1386,
        "post-decompile/index.tsv": 24,
    }
    for relative, expected in expected_counts.items():
        require(len(read_tsv(BASE / relative)) == expected, f"{relative} row count mismatch", failures)

    metadata = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-metadata.tsv")}
    tags = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-tags.tsv")}
    decompile = {normalize_address(row["address"]): row for row in read_tsv(BASE / "post-decompile" / "index.tsv")}
    xrefs = read_tsv(BASE / "post-xrefs.tsv")

    for address, (name, signature, score_tag, comment_tokens) in TARGETS.items():
        row = metadata.get(address)
        require(row is not None, f"missing metadata for {address}", failures)
        if row is not None:
            comment = row.get("comment", "")
            require(row.get("name") == name, f"name mismatch at {address}", failures)
            require(row.get("signature") == signature, f"signature mismatch at {address}: {row.get('signature')}", failures)
            require(row.get("status") == "OK", f"metadata status mismatch at {address}", failures)
            for token in (
                "Wave1193 static current-risk read-back",
                "Static rebuild contract only",
                "clean-room/no-noticeable-difference parity remain separate proof",
            ):
                require(token in comment, f"missing common comment token at {address}: {token}", failures)
            for token in comment_tokens:
                require(token in comment, f"missing comment token at {address}: {token}", failures)

        tag_row = tags.get(address)
        require(tag_row is not None, f"missing tags for {address}", failures)
        if tag_row is not None:
            actual = set(tag_row.get("tags", "").split(";"))
            require(COMMON_TAGS.issubset(actual), f"missing common tags at {address}: {COMMON_TAGS - actual}", failures)
            require(score_tag in actual, f"missing score tag at {address}: {score_tag}", failures)

        dec = decompile.get(address)
        require(dec is not None, f"missing decompile row for {address}", failures)
        if dec is not None:
            require(dec.get("signature") == signature, f"decompile signature mismatch at {address}", failures)
            require(dec.get("status") == "OK", f"decompile status mismatch at {address}", failures)

        rows = [row for row in xrefs if normalize_address(row.get("target_addr", "")) == address]
        require(rows, f"missing xrefs for {address}", failures)


def check_logs(failures: list[str]) -> None:
    expected = {
        "apply-dry.log": "SUMMARY: updated=0 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=24 tags_added=319 missing=0 bad=0",
        "apply.log": "SUMMARY: updated=24 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=24 tags_added=319 missing=0 bad=0",
        "apply-final-dry.log": "SUMMARY: updated=0 skipped=24 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 tags_added=0 missing=0 bad=0",
        "post-metadata.log": "targets=24 found=24 missing=0",
        "post-tags.log": "ExportFunctionTagsByAddress complete: rows=24 missing=0",
        "post-xrefs.log": "Wrote 1554 rows",
        "post-instructions.log": "Wrote 1386 function-body instruction rows",
        "post-decompile.log": "targets=24 dumped=24 missing=0 failed=0",
    }
    for relative, token in expected.items():
        text = read_text(BASE / relative)
        require(token in text, f"missing log token in {relative}: {token}", failures)
        for bad in ("LockException", "MISSING:", "BADNAME:", "BADSIG:", "VERIFY_", "missing=1", "bad=1", "failed=1"):
            require(bad not in text, f"unexpected failure token in {relative}: {bad}", failures)
    require("REPORT: Save succeeded" in read_text(BASE / "apply.log"), "apply save report missing", failures)


def check_progress_and_backup(failures: list[str]) -> None:
    queue = read_json(QUEUE_JSON)
    quality = queue["qualitySignals"]
    require(queue["totalFunctions"] == 6411, "queue total mismatch", failures)
    require(quality["commentlessFunctionCount"] == 0, "commentless count mismatch", failures)
    require(quality["undefinedSignatureCount"] == 0, "undefined count mismatch", failures)
    require(quality["paramSignatureCount"] == 0, "param_N count mismatch", failures)

    progress = read_json(PROGRESS)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 856, "focused reviewed mismatch", failures)
    require(current["focusedReviewedPercent"] == "72.60%", "focused percent mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 323, "remaining focused mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1154, "live focused mismatch", failures)
    require(current["broadRiskCandidates"] == 6166, "risk candidate mismatch", failures)
    require(progress["latestWave"]["artifactCommit"] == "pending Wave1193 artifact commit" or len(progress["latestWave"]["artifactCommit"]) == 40, "artifact commit field mismatch", failures)

    backup = read_json(BASE / "backup-summary.json")
    require(backup.get("backupPath") == BACKUP, "backup path mismatch", failures)
    require(backup.get("fileCount") == 19, "backup file count mismatch", failures)
    require(backup.get("totalBytes") == 176229255 or backup.get("totalBytes") == 176229255.0, "backup byte count mismatch", failures)
    require(backup.get("missingCount") == 0, "backup missing count mismatch", failures)
    require(backup.get("extraCount") == 0, "backup extra count mismatch", failures)
    require(backup.get("diffCount") == 0, "backup diff count mismatch", failures)
    require(backup.get("hashDiffCount") == 0, "backup hash diff count mismatch", failures)


def check_docs(failures: list[str]) -> None:
    require(read_text(NOTE) == read_text(NOTE_MIRROR), "Wave1193 note mirror mismatch", failures)
    docs = [
        NOTE,
        READINESS,
        PROGRESS,
        MAPPED,
        CAMPAIGN,
        RANK,
        FUNCTION_COVERAGE,
        FUNCTION_INDEX,
        BINARY_INDEX,
        RE_INDEX,
        DEVELOPER_STATE,
        DOCUMENTATION_STATE,
        RE_STATE,
    ]
    for path in docs:
        text = read_text(path)
        for token in DOC_TOKENS:
            require(contains_token(text, token), f"missing token in {path.relative_to(ROOT)}: {token}", failures)
        lowered = text.lower()
        for bad in OVERCLAIMS:
            require(bad not in lowered, f"overclaim token in {path.relative_to(ROOT)}: {bad}", failures)

    package = read_json(PACKAGE_JSON)
    require(
        package.get("scripts", {}).get("test:wave1193-top-residual-score20-18-current-risk-review")
        == r"py -3 tools\wave1193_top_residual_score20_18_current_risk_review.py --check",
        "missing package script",
        failures,
    )
    require(APPLY_SCRIPT.is_file(), "missing Wave1193 apply script", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_artifacts(failures)
    check_logs(failures)
    check_progress_and_backup(failures)
    check_docs(failures)

    if failures:
        print("Wave1193 top residual score20-18 current-risk probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Wave1193 top residual score20-18 current-risk probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
