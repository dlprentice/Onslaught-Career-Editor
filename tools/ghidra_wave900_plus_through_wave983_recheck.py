#!/usr/bin/env python3
"""Recheck Wave900+ static re-audit evidence before new clusters.

This is a current-scope gate layered over the historical Wave900-Wave981
probe/evidence audits. It keeps older audit notes immutable as historical
records and can extend the current gate to later Wave900+ reviews plus the
current zero-debt queue.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
READINESS = ROOT / "release" / "readiness"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PRIOR_PROBE_SWEEP_SUMMARY = (
    ROOT
    / "subagents"
    / "ghidra-static-reaudit"
    / "wave900-plus-audit"
    / "wave900-plus-audit-summary.json"
)
PRIOR_EVIDENCE_AUDIT_SUMMARY = (
    ROOT
    / "subagents"
    / "ghidra-static-reaudit"
    / "wave900-plus-evidence-audit"
    / "wave900-plus-evidence-audit-summary.json"
)

FIRST_WAVE = 900
PRIOR_AUDIT_LAST_WAVE = 981
LAST_WAVE = 983
NON_BACKUP_OPERATIONAL_WAVES = {910, 911}
META_AUDIT_NOTE_PREFIXES = ("ghidra_wave900_plus_",)
META_PACKAGE_SCRIPTS = {
    "test:ghidra-wave900-plus-audit",
    "test:ghidra-wave900-plus-evidence-audit",
    "test:ghidra-wave900-plus-through-wave983-recheck",
    "test:ghidra-wave900-plus-through-wave984-recheck",
    "test:ghidra-wave900-plus-through-wave986-recheck",
    "test:ghidra-wave900-plus-through-wave987-recheck",
    "test:wave911-reconstruction-preflight",
    "test:wave911-residual-accounting",
}
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave900-plus-through-wave983-recheck"
OUT = BASE / "wave900-plus-through-wave983-recheck-summary.json"
DIRECT_RESULTS = BASE / "wave982-wave983-direct-probe-results.tsv"

WAVE_RE = re.compile(r"(?:wave|post_wave)(9\d\d|1\d{3})", re.IGNORECASE)
BACKUP_RE = re.compile(r"[maintainer-local-ghidra-backup-root]\\[^\s`|)]+")
TOOL_PATH_RE = re.compile(r"tools[\\/][^\"'\s]+\.py", re.IGNORECASE)
BASE_RE = re.compile(
    r"BASE\s*=\s*ROOT\s*/\s*['\"]subagents['\"]\s*/\s*['\"]ghidra-static-reaudit['\"]\s*/\s*['\"]([^'\"]+)['\"]"
)

CURRENT_STATE_TOKENS = (
    "developer_agent_state.json",
    "documentation_agent_state.json",
    "re_orchestrator_state.json",
    "function_mutation_tracking_state.json",
)
TRACKING_STATE_MISMATCH_RE = re.compile(r"^tracking [a-z0-9_]+ mismatch$", re.IGNORECASE)
QUEUE_TOKENS = (
    "queue total mismatch",
    "quality TSV row count mismatch",
    "quality TSV commented mismatch",
    "quality TSV commented count mismatch",
    "quality TSV strict clean mismatch",
    "quality TSV strict clean count mismatch",
    "quality TSV strict-clean mismatch",
    "quality TSV strict-clean count mismatch",
    "commented count mismatch",
    "strict clean count mismatch",
    "queue TSV row count mismatch",
    "strict clean-signature count mismatch",
    "expanded count mismatch",
    "expanded percent mismatch",
)
DOC_TOKENS = (
    "missing doc token in AGENTS.md",
    "missing token in AGENTS.md",
    "missing token in README.md",
    "missing token in CURRENT_CAPABILITIES.md",
    "missing token in reverse-engineering",
    "missing token in lore-book",
    "missing token in release",
    "missing token in roadmap",
)
DISALLOWED_PROBE_FAILURE_PATTERNS = (
    "metadata mismatch",
    "signature mismatch",
    "tag mismatch",
    "decompile mismatch",
    "missing metadata",
    "missing tags",
    "missing decompile",
    "backup summary mismatch",
    "backup path mismatch",
    "backup byte",
    "missing log token",
    "unexpected failure token",
    "dry log missing",
    "apply log missing",
    "final dry log missing",
    "LockException",
)
DISALLOWED_LOG_TOKENS = (
    "LockException",
    "Traceback (most recent call last)",
    "NullPointerException",
    "FileNotFoundException",
    "MISSING:",
    "BADADDR",
    "BADNAME",
    "FAIL:",
    "missing=1",
    "bad=1",
    "failed=1",
)
EXPECTED_MISSING_LOG_PATHS = {
    # Wave1032 intentionally probes stale non-function context at 0x0054d4ac
    # inside CDXMeshVB__ReleaseResources; these logs prove that boundary check.
    "subagents/ghidra-static-reaudit/wave1032-tweak-reconnect-interface-review/context-decompile.log",
    "subagents/ghidra-static-reaudit/wave1032-tweak-reconnect-interface-review/context-instructions.log",
    "subagents/ghidra-static-reaudit/wave1032-tweak-reconnect-interface-review/context-metadata.log",
    "subagents/ghidra-static-reaudit/wave1032-tweak-reconnect-interface-review/context-tags.log",
    # Wave1051 intentionally includes stale/no-function context at 0x0046a180
    # while consolidating the FEPWingmen page after boundary recovery.
    "subagents/ghidra-static-reaudit/wave1051-fepwingmen-page-review/context-decompile.log",
    "subagents/ghidra-static-reaudit/wave1051-fepwingmen-page-review/context-instructions.log",
    "subagents/ghidra-static-reaudit/wave1051-fepwingmen-page-review/context-metadata.log",
    "subagents/ghidra-static-reaudit/wave1051-fepwingmen-page-review/context-tags.log",
    # Wave1068 intentionally includes raw CRTBuilding/CRTMesh vtable-slot
    # pointers that are not function starts while validating the surrounding
    # vtable/context surface.
    "subagents/ghidra-static-reaudit/wave1068-rtbuilding-rtmesh-lifecycle-review/context-decompile.log",
    "subagents/ghidra-static-reaudit/wave1068-rtbuilding-rtmesh-lifecycle-review/context-instructions.log",
    "subagents/ghidra-static-reaudit/wave1068-rtbuilding-rtmesh-lifecycle-review/context-metadata.log",
    "subagents/ghidra-static-reaudit/wave1068-rtbuilding-rtmesh-lifecycle-review/context-tags.log",
    # Wave1069 intentionally includes raw ground-unit/motion-controller
    # neighborhood addresses that are not function starts; caller/vtable exports
    # carry the live function evidence for that context.
    "subagents/ghidra-static-reaudit/wave1069-groundunit-vfunc-motion-effects-review/context-metadata.log",
    # Wave1079 intentionally includes one raw/suspect address without a
    # function-body window while validating the CTGALoader adjacent table
    # boundary; diagnose/xref/vtable/post exports carry the boundary evidence.
    "subagents/ghidra-static-reaudit/wave1079-terrainguide-tga-table-review/suspect-instructions-around.log",
}
EXPECTED_RECOVERED_LOG_FAILURES = {
    "subagents/ghidra-static-reaudit/wave1045-frontend-residual-helper-review/apply.log": (
        "FAIL: 0x0045e0d0 CFEPGoodies__Render IllegalStateException: createFunction returned null at 0x0045e0d0 (disassemble=true)",
        "SUMMARY: updated=7 skipped=0 created=7 would_create=0 renamed=1 would_rename=0 signature_updated=6 comment_only_updated=1 missing=0 bad=1",
        "REPORT: Save succeeded",
    ),
}
OVERCLAIM_TOKENS = (
    "runtime behavior proven",
    "runtime gameplay behavior proven",
    "runtime proof complete",
    "patch behavior proven",
    "rebuild parity proven",
    "all systems complete",
    "every system is complete",
    "fully reverse-engineered",
    "fully reverse engineered",
    "exact source-layout identity proven",
    "exact source layout identity proven",
)


def configure_scope(last_wave: int) -> None:
    global LAST_WAVE, BASE, OUT, DIRECT_RESULTS
    if last_wave < PRIOR_AUDIT_LAST_WAVE + 1:
        raise ValueError(f"last wave must be >= {PRIOR_AUDIT_LAST_WAVE + 1}")
    LAST_WAVE = last_wave
    slug = f"wave900-plus-through-wave{LAST_WAVE}-recheck"
    BASE = ROOT / "subagents" / "ghidra-static-reaudit" / slug
    OUT = BASE / f"{slug}-summary.json"
    DIRECT_RESULTS = BASE / f"wave982-wave{LAST_WAVE}-direct-probe-results.tsv"


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    data = path.read_bytes()
    if not data:
        return ""
    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        return data.decode("utf-16", errors="replace")
    if b"\x00" in data[:200]:
        return data.decode("utf-16-le", errors="replace")
    return data.decode("utf-8-sig", errors="replace")


def read_json(path: Path) -> dict:
    text = read_text(path)
    return json.loads(text) if text else {}


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def wave_from_string(value: str) -> int | None:
    match = WAVE_RE.search(value)
    if not match:
        return None
    wave = int(match.group(1))
    if FIRST_WAVE <= wave <= LAST_WAVE:
        return wave
    return None


def normalize_backup_path(value: str) -> Path:
    cleaned = value.rstrip(".,;:")
    if cleaned.startswith("G:\\"):
        return Path("G:/") / cleaned[3:].replace("\\", "/")
    return Path(cleaned)


def recursive_file_stats(path: Path) -> tuple[int, int]:
    count = 0
    total = 0
    for item in path.rglob("*"):
        if item.is_file():
            count += 1
            total += item.stat().st_size
    return count, total


def operational_readiness_notes() -> list[dict[str, object]]:
    notes: list[dict[str, object]] = []
    for path in sorted(READINESS.glob("*.md")):
        if any(path.name.startswith(prefix) for prefix in META_AUDIT_NOTE_PREFIXES):
            continue
        wave = wave_from_string(path.name)
        if wave is None:
            continue
        text = read_text(path)
        backups = sorted({match.group(0).rstrip(".,;:") for match in BACKUP_RE.finditer(text)})
        notes.append(
            {
                "wave": wave,
                "path": path.relative_to(ROOT).as_posix(),
                "backupPaths": backups,
                "backupCount": len(backups),
                "hasValidationLanguage": bool(re.search(r"\b(PASS|passed|validated|verified|validation)\b", text, re.IGNORECASE)),
                "hasBoundaryLanguage": bool(
                    re.search(
                        r"(not prove|not proven|unproven|remain separate|remain deferred|separate proof|runtime.*separate|rebuild parity)",
                        text,
                        re.IGNORECASE,
                    )
                ),
                "overclaims": [token for token in OVERCLAIM_TOKENS if token in text.lower()],
            }
        )
    return notes


def is_meta_package_script(name: str) -> bool:
    return name in META_PACKAGE_SCRIPTS or name.startswith("test:ghidra-wave900-plus-through-wave")


def package_wave_scripts() -> dict[str, dict[str, object]]:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    rows: dict[str, dict[str, object]] = {}
    for name, command in scripts.items():
        if is_meta_package_script(name):
            continue
        waves = {
            int(match.group(1))
            for match in [*WAVE_RE.finditer(name), *WAVE_RE.finditer(str(command))]
            if FIRST_WAVE <= int(match.group(1)) <= LAST_WAVE
        }
        if waves:
            rows[name] = {"command": str(command), "waves": sorted(waves)}
    return rows


def probe_tool_for_command(command: str) -> Path | None:
    match = TOOL_PATH_RE.search(command)
    if not match:
        return None
    return ROOT / match.group(0).replace("\\", "/")


def base_from_probe(path: Path) -> Path | None:
    match = BASE_RE.search(read_text(path))
    if not match:
        return None
    return ROOT / "subagents" / "ghidra-static-reaudit" / match.group(1)


def artifact_summary(base: Path) -> dict[str, object]:
    files = [path for path in base.rglob("*") if path.is_file()]
    names = [path.name.lower() for path in files]
    return {
        "path": base.relative_to(ROOT).as_posix(),
        "exists": base.is_dir(),
        "fileCount": len(files),
        "tsvCount": sum(1 for name in names if name.endswith(".tsv")),
        "jsonCount": sum(1 for name in names if name.endswith(".json")),
        "logCount": sum(1 for name in names if name.endswith(".log")),
        "hasMetadata": any("metadata" in name and name.endswith(".tsv") for name in names),
        "hasTags": any("tags" in name and name.endswith(".tsv") for name in names),
        "hasInstructions": any("instruction" in name and name.endswith(".tsv") for name in names),
        "hasDecompileIndex": any(path.name.lower() == "index.tsv" and path.parent.name.lower().endswith("decompile") for path in files),
        "hasBackupSummary": any(name.endswith("backup-summary.json") for name in names),
    }


def is_expected_context_missing_log(path: Path) -> bool:
    relative = path.relative_to(ROOT).as_posix()
    if relative in EXPECTED_MISSING_LOG_PATHS:
        return True
    name = path.name.lower()
    return any(token in name for token in ("pre-", "boundary-pre", "receive-context", "no-function", "slot2", "partial-post"))


def is_expected_recovered_log_failure(path: Path, text: str) -> bool:
    relative = path.relative_to(ROOT).as_posix()
    required = EXPECTED_RECOVERED_LOG_FAILURES.get(relative)
    if not required:
        return False
    recovery_dry = path.parent / "apply-recovery-dry.log"
    recovery_apply = path.parent / "apply-recovery.log"
    final_dry = path.parent / "apply-final-dry.log"
    return (
        all(token in text for token in required)
        and "SUMMARY: updated=0 skipped=7 created=0 would_create=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0"
        in read_text(recovery_dry)
        and "SUMMARY: updated=1 skipped=7 created=1 would_create=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0"
        in read_text(recovery_apply)
        and "SUMMARY: updated=0 skipped=8 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0"
        in read_text(final_dry)
    )


def scan_logs_for_bad_tokens(base: Path) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    hits: list[dict[str, object]] = []
    expected_context_missing: list[dict[str, object]] = []
    if not base.is_dir():
        return hits, expected_context_missing
    for path in base.rglob("*.log"):
        text = read_text(path)
        bad = [token for token in DISALLOWED_LOG_TOKENS if token in text]
        if not bad:
            continue
        if bad == ["missing=1"] and is_expected_context_missing_log(path):
            expected_context_missing.append({"path": path.relative_to(ROOT).as_posix(), "tokens": bad})
        elif is_expected_recovered_log_failure(path, text):
            expected_context_missing.append({"path": path.relative_to(ROOT).as_posix(), "tokens": bad})
        else:
            hits.append({"path": path.relative_to(ROOT).as_posix(), "tokens": bad})
    return hits, expected_context_missing


def failure_lines(log_text: str) -> list[str]:
    return [line[2:].strip() for line in log_text.splitlines() if line.startswith("- ")]


def classify_failure(log_text: str) -> set[str]:
    lowered = log_text.lower()
    categories: set[str] = set()
    if any(token.lower() in lowered for token in CURRENT_STATE_TOKENS):
        categories.add("current-state-baton")
    if TRACKING_STATE_MISMATCH_RE.match(log_text.strip()):
        categories.add("current-state-baton")
    if any(token.lower() in lowered for token in QUEUE_TOKENS):
        categories.add("historical-live-queue")
    if any(token.lower() in lowered for token in DOC_TOKENS):
        categories.add("rolled-current-doc")
    if lowered.startswith("progress "):
        categories.add("rolled-current-doc")
    if lowered.startswith("missing token in progress:"):
        categories.add("rolled-current-doc")
    if lowered == "wave1108 focused row count mismatch":
        categories.add("rolled-current-doc")
    if (
        lowered.startswith("missing token in developer state:")
        or lowered.startswith("missing token in documentation state:")
        or lowered.startswith("missing token in re state:")
    ):
        categories.add("current-state-baton")
    if lowered == "latest sample mismatch":
        categories.add("rolled-current-doc")
    if "missing doc token " in lowered and any(
        token in lowered for token in ("agents.md", "reverse-engineering", "lore-book", "release", "roadmap", "readme.md", "current_capabilities.md")
    ):
        categories.add("rolled-current-doc")
    if " missing token:" in lowered and (
        lowered.startswith("reverse-engineering\\")
        or lowered.startswith("reverse-engineering/")
        or lowered.startswith("lore-book\\")
        or lowered.startswith("lore-book/")
        or "function_coverage_state.md" in lowered
        or "agents.md" in lowered
        or "readme.md" in lowered
        or "current_capabilities.md" in lowered
    ):
        categories.add("rolled-current-doc")
    if any(token.lower() in lowered for token in DISALLOWED_PROBE_FAILURE_PATTERNS) and not lowered.startswith("progress "):
        categories.add("evidence-mismatch")
    return categories


def classify_probe_log(log_text: str) -> tuple[list[dict[str, object]], set[str]]:
    lines = failure_lines(log_text)
    if not lines:
        categories = classify_failure(log_text)
        if not categories and log_text.strip():
            categories.add("unclassified")
        return [{"line": "<whole-log>", "categories": sorted(categories)}], categories

    details: list[dict[str, object]] = []
    aggregate: set[str] = set()
    for line in lines:
        categories = classify_failure(line)
        if not categories:
            categories.add("unclassified")
        aggregate.update(categories)
        details.append({"line": line, "categories": sorted(categories)})

    if "lockexception" in log_text.lower():
        aggregate.add("evidence-mismatch")
        details.append({"line": "<whole-log LockException>", "categories": ["evidence-mismatch"]})
    return details, aggregate


def run_new_direct_probes(scripts: dict[str, dict[str, object]]) -> dict[str, object]:
    BASE.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for script_name, row in sorted(scripts.items()):
        waves = row["waves"]
        if not any(PRIOR_AUDIT_LAST_WAVE < int(wave) <= LAST_WAVE for wave in waves):
            continue
        tool = probe_tool_for_command(str(row["command"]))
        if tool is None or not tool.is_file():
            rows.append(
                {
                    "status": "FAIL",
                    "wave": ",".join(str(wave) for wave in waves),
                    "script": script_name,
                    "log": "",
                    "categories": ["missing-tool"],
                    "lineClassifications": [],
                    "returnCode": None,
                }
            )
            continue
        command = [sys.executable, str(tool), "--check"]
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        log_text = completed.stdout + completed.stderr
        log_path = BASE / f"{script_name.replace(':', '_')}.log"
        log_path.write_text(log_text, encoding="utf-8")
        if completed.returncode == 0:
            line_details: list[dict[str, object]] = []
            categories: set[str] = set()
        else:
            line_details, categories = classify_probe_log(log_text)
        rows.append(
            {
                "status": "PASS" if completed.returncode == 0 else "FAIL",
                "wave": ",".join(str(wave) for wave in waves),
                "script": script_name,
                "log": log_path.relative_to(ROOT).as_posix(),
                "categories": sorted(categories),
                "lineClassifications": line_details,
                "returnCode": completed.returncode,
            }
        )

    with DIRECT_RESULTS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        for row in rows:
            writer.writerow([row["status"], row["wave"], row["script"], row["log"], ",".join(row["categories"])])

    disallowed = [
        row
        for row in rows
        if row["status"] != "PASS"
        and ("evidence-mismatch" in row["categories"] or "unclassified" in row["categories"] or "missing-tool" in row["categories"])
    ]
    return {
        "resultFile": DIRECT_RESULTS.relative_to(ROOT).as_posix(),
        "resultCount": len(rows),
        "passCount": sum(1 for row in rows if row["status"] == "PASS"),
        "failCount": sum(1 for row in rows if row["status"] != "PASS"),
        "disallowedFailureCount": len(disallowed),
        "rows": rows,
    }


def backup_audit(notes: list[dict[str, object]]) -> dict[str, object]:
    rows = []
    for note in notes:
        for backup in note["backupPaths"]:
            path = normalize_backup_path(str(backup))
            exists = path.is_dir()
            file_count = 0
            total_bytes = 0
            if exists:
                file_count, total_bytes = recursive_file_stats(path)
            rows.append(
                {
                    "wave": note["wave"],
                    "note": note["path"],
                    "backupPath": backup,
                    "exists": exists,
                    "fileCount": file_count,
                    "totalBytes": total_bytes,
                }
            )
    return {
        "backupReferenceCount": len(rows),
        "uniqueBackupCount": len({row["backupPath"] for row in rows}),
        "missingBackups": [row for row in rows if not row["exists"]],
        "suspiciousBackups": [
            row for row in rows if row["exists"] and (int(row["fileCount"]) < 10 or int(row["totalBytes"]) < 100_000_000)
        ],
        "rows": rows,
    }


def apply_script_log_coverage() -> dict[str, object]:
    apply_scripts = []
    for script in sorted(ROOT.joinpath("tools").glob("Apply*Wave*.java")):
        wave = wave_from_string(script.name)
        if wave is not None and FIRST_WAVE <= wave <= LAST_WAVE:
            apply_scripts.append(script)
    log_paths = sorted((ROOT / "subagents" / "ghidra-static-reaudit").glob("wave*/**/*.log"))
    log_texts = [(path, read_text(path)) for path in log_paths]
    rows = []
    for script in apply_scripts:
        found_logs = []
        for path, text in log_texts:
            if script.name in text:
                clean_summary = "bad=0" in text and ("missing=" not in text or "missing=0" in text)
                save_succeeded = "REPORT: Save succeeded" in text or "Save succeeded" in text
                found_logs.append(
                    {
                        "path": path.relative_to(ROOT).as_posix(),
                        "cleanSummary": clean_summary,
                        "saveSucceeded": save_succeeded,
                    }
                )
        rows.append(
            {
                "script": script.relative_to(ROOT).as_posix(),
                "logCount": len(found_logs),
                "cleanLogCount": sum(1 for log in found_logs if log["cleanSummary"]),
                "saveSucceededLogCount": sum(1 for log in found_logs if log["saveSucceeded"]),
            }
        )
    return {
        "applyScriptCount": len(apply_scripts),
        "scripts": rows,
        "missingLogScripts": [row["script"] for row in rows if row["logCount"] == 0],
        "missingCleanSummaryScripts": [row["script"] for row in rows if row["cleanLogCount"] == 0],
        "missingSaveSucceededScripts": [row["script"] for row in rows if row["saveSucceededLogCount"] == 0],
    }


def current_queue_summary() -> dict[str, object]:
    queue = read_json(QUEUE_JSON)
    quality = queue.get("qualitySignals", {}) if isinstance(queue, dict) else {}
    return {
        "totalFunctions": queue.get("totalFunctions"),
        "commentlessFunctionCount": quality.get("commentlessFunctionCount"),
        "undefinedSignatureCount": quality.get("undefinedSignatureCount"),
        "paramSignatureCount": quality.get("paramSignatureCount"),
        "status": queue.get("status"),
        "ok": (
            queue.get("status") == "PASS"
            and isinstance(queue.get("totalFunctions"), int)
            and queue.get("totalFunctions") > 0
            and quality.get("commentlessFunctionCount") == 0
            and quality.get("undefinedSignatureCount") == 0
            and quality.get("paramSignatureCount") == 0
        ),
    }


def build_report() -> dict[str, object]:
    failures: list[str] = []
    notes = operational_readiness_notes()
    by_wave: dict[int, list[dict[str, object]]] = {}
    for note in notes:
        by_wave.setdefault(int(note["wave"]), []).append(note)

    missing_waves = [wave for wave in range(FIRST_WAVE, LAST_WAVE + 1) if wave not in by_wave]
    if missing_waves:
        failures.append(f"missing readiness note waves: {missing_waves}")

    waves_without_backup = [
        wave
        for wave in range(FIRST_WAVE, LAST_WAVE + 1)
        if wave not in NON_BACKUP_OPERATIONAL_WAVES
        and not any(note["backupPaths"] for note in by_wave.get(wave, []))
    ]
    if waves_without_backup:
        failures.append(f"waves without backup evidence: {waves_without_backup}")

    note_overclaims = [note for note in notes if note["overclaims"]]
    if note_overclaims:
        failures.append(f"readiness notes with overclaim tokens: {len(note_overclaims)}")

    backups = backup_audit(notes)
    if backups["missingBackups"]:
        failures.append(f"missing backup directories: {len(backups['missingBackups'])}")
    if backups["suspiciousBackups"]:
        failures.append(f"suspicious backup directories: {len(backups['suspiciousBackups'])}")

    scripts = package_wave_scripts()
    old_script_count = sum(1 for row in scripts.values() if any(FIRST_WAVE <= int(wave) <= PRIOR_AUDIT_LAST_WAVE for wave in row["waves"]))
    new_script_count = sum(1 for row in scripts.values() if any(PRIOR_AUDIT_LAST_WAVE < int(wave) <= LAST_WAVE for wave in row["waves"]))

    artifact_rows = []
    missing_tools = []
    missing_bases = []
    weak_artifacts = []
    log_bad_hits = []
    expected_context_missing_log_hits = []
    for script_name, row in sorted(scripts.items()):
        tool = probe_tool_for_command(str(row["command"]))
        if tool is None or not tool.is_file():
            missing_tools.append(script_name)
            continue
        base = base_from_probe(tool)
        if base is None or not base.is_dir():
            missing_bases.append({"script": script_name, "tool": tool.relative_to(ROOT).as_posix()})
            continue
        summary = artifact_summary(base)
        summary["script"] = script_name
        summary["tool"] = tool.relative_to(ROOT).as_posix()
        summary["waves"] = row["waves"]
        artifact_rows.append(summary)
        if summary["fileCount"] == 0 or (summary["tsvCount"] == 0 and summary["jsonCount"] == 0):
            weak_artifacts.append(summary["path"])
        bad_hits, expected_hits = scan_logs_for_bad_tokens(base)
        log_bad_hits.extend(bad_hits)
        expected_context_missing_log_hits.extend(expected_hits)

    if missing_tools:
        failures.append(f"missing probe tool files: {len(missing_tools)}")
    if missing_bases:
        failures.append(f"missing probe evidence bases: {len(missing_bases)}")
    if weak_artifacts:
        failures.append(f"weak/empty evidence bases: {len(weak_artifacts)}")
    if log_bad_hits:
        failures.append(f"evidence logs with disallowed tokens: {len(log_bad_hits)}")

    prior_probe_sweep = read_json(PRIOR_PROBE_SWEEP_SUMMARY)
    if prior_probe_sweep.get("status") != "PASS":
        failures.append("prior Wave900-Wave981 focused-probe sweep is not PASS")
    if prior_probe_sweep.get("scope") != "Wave900-Wave981":
        failures.append("prior focused-probe sweep scope is not Wave900-Wave981")
    if prior_probe_sweep.get("missingScriptCount") != 0 or prior_probe_sweep.get("extraScriptCount") != 0:
        failures.append("prior focused-probe sweep script coverage mismatch")
    disallowed_prior_probe_failures = [
        row
        for row in prior_probe_sweep.get("failureCategories", [])
        if "evidence-mismatch" in row.get("categories", []) or "unclassified" in row.get("categories", [])
    ]
    if disallowed_prior_probe_failures:
        failures.append(f"prior focused probes have evidence/unclassified failures: {len(disallowed_prior_probe_failures)}")

    prior_evidence_audit = read_json(PRIOR_EVIDENCE_AUDIT_SUMMARY)
    if prior_evidence_audit.get("status") != "PASS":
        failures.append("prior Wave900-Wave981 evidence audit is not PASS")
    if prior_evidence_audit.get("scope") != "Wave900-Wave981":
        failures.append("prior evidence audit scope is not Wave900-Wave981")

    direct_probe = run_new_direct_probes(scripts)
    if direct_probe["resultCount"] != new_script_count:
        failures.append(f"Wave982-Wave{LAST_WAVE} direct probe result count mismatch")
    if direct_probe["disallowedFailureCount"]:
        failures.append(
            f"Wave982-Wave{LAST_WAVE} direct probes have evidence/unclassified failures: {direct_probe['disallowedFailureCount']}"
        )

    apply_logs = apply_script_log_coverage()
    if apply_logs["missingLogScripts"]:
        failures.append(f"apply scripts without any log coverage: {len(apply_logs['missingLogScripts'])}")
    if apply_logs["missingCleanSummaryScripts"]:
        failures.append(f"apply scripts without clean summary log: {len(apply_logs['missingCleanSummaryScripts'])}")
    if apply_logs["missingSaveSucceededScripts"]:
        failures.append(f"apply scripts without save-succeeded log: {len(apply_logs['missingSaveSucceededScripts'])}")

    queue = current_queue_summary()
    if not queue["ok"]:
        failures.append("current queue is not closed with PASS status and zero debt")

    return {
        "schema": f"ghidra-wave900-plus-through-wave{LAST_WAVE}-recheck.v1",
        "status": "PASS" if not failures else "FAIL",
        "scope": f"Wave{FIRST_WAVE}-Wave{LAST_WAVE}",
        "readinessNoteCount": len(notes),
        "coveredWaveCount": len(by_wave),
        "missingWaves": missing_waves,
        "nonBackupOperationalWaves": sorted(NON_BACKUP_OPERATIONAL_WAVES),
        "wavesWithoutBackupEvidence": waves_without_backup,
        "readinessNotesWithOverclaims": note_overclaims,
        "backupAudit": backups,
        "packageProbeScriptCount": len(scripts),
        "priorPackageProbeScriptCount": old_script_count,
        "newPackageProbeScriptCount": new_script_count,
        "artifactBaseCount": len(artifact_rows),
        "artifactRows": artifact_rows,
        "missingProbeTools": missing_tools,
        "missingProbeBases": missing_bases,
        "weakArtifactBases": weak_artifacts,
        "evidenceLogBadTokenHits": log_bad_hits,
        "expectedContextMissingLogHits": expected_context_missing_log_hits,
        "priorProbeSweep": {
            "status": prior_probe_sweep.get("status"),
            "scope": prior_probe_sweep.get("scope"),
            "packageWaveScriptCount": prior_probe_sweep.get("packageWaveScriptCount"),
            "resultCount": prior_probe_sweep.get("resultCount"),
            "passCount": prior_probe_sweep.get("passCount"),
            "failCount": prior_probe_sweep.get("failCount"),
            "disallowedFailureCount": len(disallowed_prior_probe_failures),
        },
        "priorEvidenceAudit": {
            "status": prior_evidence_audit.get("status"),
            "scope": prior_evidence_audit.get("scope"),
            "readinessNoteCount": prior_evidence_audit.get("readinessNoteCount"),
            "coveredWaveCount": prior_evidence_audit.get("coveredWaveCount"),
            "packageProbeScriptCount": prior_evidence_audit.get("packageProbeScriptCount"),
            "artifactBaseCount": prior_evidence_audit.get("artifactBaseCount"),
            "backupReferenceCount": prior_evidence_audit.get("backupAudit", {}).get("backupReferenceCount"),
            "applyScriptCount": prior_evidence_audit.get("applyScriptLogCoverage", {}).get("applyScriptCount"),
        },
        "newDirectProbe": direct_probe,
        "applyScriptLogCoverage": apply_logs,
        "currentQueue": queue,
        "failures": failures,
        "interpretation": [
            "Wave900-Wave981 are covered by the prior line-classified focused-probe sweep and second-level evidence audit.",
            f"Wave982-Wave{LAST_WAVE} focused probes are rerun directly by this gate; stale current-state baton failures are classified separately from evidence mismatches.",
            "Wave910 and Wave911 remain queue/planning records, not saved Ghidra mutation/review records with per-wave backup notes.",
            "This recheck validates static evidence structure, backups, apply logs, focused probe classifications, and current queue closure. It does not prove runtime behavior, exact source-layout identity, or rebuild parity.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--last-wave", type=int, default=983, help="last Wave900+ wave to include in the current gate")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    configure_scope(args.last_wave)

    report = build_report()
    write_json(OUT, report)
    print(f"Wave900-Wave{LAST_WAVE} static re-audit recheck")
    print("Status:", report["status"])
    print("Readiness notes:", report["readinessNoteCount"])
    print("Covered waves:", report["coveredWaveCount"])
    print("Package probe scripts:", report["packageProbeScriptCount"])
    print("Evidence bases:", report["artifactBaseCount"])
    print("Backup references:", report["backupAudit"]["backupReferenceCount"])
    print("Apply scripts:", report["applyScriptLogCoverage"]["applyScriptCount"])
    direct = report["newDirectProbe"]
    print(
        f"Wave982-Wave{LAST_WAVE} direct probes:",
        {
            "resultFile": direct["resultFile"],
            "resultCount": direct["resultCount"],
            "passCount": direct["passCount"],
            "failCount": direct["failCount"],
            "disallowedFailureCount": direct["disallowedFailureCount"],
        },
    )
    print("Current queue:", report["currentQueue"])
    if report["failures"]:
        for failure in report["failures"]:
            print("-", failure)
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
