#!/usr/bin/env python3
"""Second-level Wave900+ re-audit evidence/backups audit.

This is intentionally broader than the focused-probe sweep classifier. It
checks the public wave records, ignored evidence folders, backup paths, apply
script logs, and current queue closure before new post-981 Ghidra work starts.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "subagents" / "ghidra-static-reaudit" / "wave900-plus-evidence-audit"
OUT = BASE / "wave900-plus-evidence-audit-summary.json"
READINESS = ROOT / "release" / "readiness"
PACKAGE_JSON = ROOT / "package.json"
QUEUE_JSON = ROOT / "subagents" / "ghidra-static-reaudit" / "queue" / "current" / "static-reaudit-queue.json"
PROBE_SWEEP_SUMMARY = (
    ROOT
    / "subagents"
    / "ghidra-static-reaudit"
    / "wave900-plus-audit"
    / "wave900-plus-audit-summary.json"
)

FIRST_WAVE = 900
LAST_WAVE = 981
NON_BACKUP_OPERATIONAL_WAVES = {910, 911}
META_AUDIT_NOTE_PREFIXES = ("ghidra_wave900_plus_",)

WAVE_RE = re.compile(r"(?:wave|post_wave)(9\d\d)", re.IGNORECASE)
BACKUP_RE = re.compile(r"[maintainer-local-ghidra-backup-root]\\[^\s`|)]+")
PACKAGE_WAVE_RE = re.compile(r"wave9\d\d", re.IGNORECASE)
TOOL_PATH_RE = re.compile(r"tools[\\/][^\"'\s]+\.py", re.IGNORECASE)
BASE_RE = re.compile(
    r"BASE\s*=\s*ROOT\s*/\s*['\"]subagents['\"]\s*/\s*['\"]ghidra-static-reaudit['\"]\s*/\s*['\"]([^'\"]+)['\"]"
)

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


def wave_from_name(name: str) -> int | None:
    match = WAVE_RE.search(name)
    if not match:
        return None
    wave = int(match.group(1))
    if FIRST_WAVE <= wave <= LAST_WAVE:
        return wave
    return None


def operational_readiness_notes() -> list[dict[str, object]]:
    notes: list[dict[str, object]] = []
    for path in sorted(READINESS.glob("*.md")):
        wave = wave_from_name(path.name)
        if wave is None:
            continue
        is_meta = any(path.name.startswith(prefix) for prefix in META_AUDIT_NOTE_PREFIXES)
        if is_meta:
            continue
        text = read_text(path)
        backups = sorted({match.group(0).rstrip(".,;:") for match in BACKUP_RE.finditer(text)})
        overclaims = [token for token in OVERCLAIM_TOKENS if token in text.lower()]
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
                "overclaims": overclaims,
            }
        )
    return notes


def package_wave_scripts() -> dict[str, str]:
    scripts = read_json(PACKAGE_JSON).get("scripts", {})
    excluded = {
        "test:ghidra-wave900-plus-audit",
        "test:ghidra-wave900-plus-evidence-audit",
        "test:ghidra-wave900-plus-through-wave983-recheck",
        "test:ghidra-wave900-plus-through-wave984-recheck",
    }
    rows: dict[str, str] = {}
    for name, command in scripts.items():
        if name in excluded:
            continue
        waves = [wave_from_name(name), wave_from_name(str(command))]
        if any(wave is not None for wave in waves):
            rows[name] = str(command)
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
    name = path.name.lower()
    return any(
        token in name
        for token in (
            "pre-",
            "boundary-pre",
            "receive-context",
            "no-function",
            "slot2",
        )
    )


def scan_logs_for_bad_tokens(base: Path) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    hits: list[dict[str, object]] = []
    expected_context_missing: list[dict[str, object]] = []
    if not base.is_dir():
        return hits, expected_context_missing
    for path in base.rglob("*.log"):
        text = read_text(path)
        bad = [token for token in DISALLOWED_LOG_TOKENS if token in text]
        if bad:
            if bad == ["missing=1"] and is_expected_context_missing_log(path):
                expected_context_missing.append({"path": path.relative_to(ROOT).as_posix(), "tokens": bad})
            else:
                hits.append({"path": path.relative_to(ROOT).as_posix(), "tokens": bad})
    return hits, expected_context_missing


def apply_script_log_coverage() -> dict[str, object]:
    apply_scripts = [
        script for script in sorted(ROOT.joinpath("tools").glob("Apply*Wave9*.java")) if wave_from_name(script.name) is not None
    ]
    log_paths = sorted((ROOT / "subagents" / "ghidra-static-reaudit").glob("wave9*/**/*.log"))
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
                "cleanLogCount": sum(1 for row in found_logs if row["cleanSummary"]),
                "saveSucceededLogCount": sum(1 for row in found_logs if row["saveSucceeded"]),
            }
        )
    return {
        "applyScriptCount": len(apply_scripts),
        "scripts": rows,
        "missingLogScripts": [row["script"] for row in rows if row["logCount"] == 0],
        "missingCleanSummaryScripts": [row["script"] for row in rows if row["cleanLogCount"] == 0],
        "missingSaveSucceededScripts": [row["script"] for row in rows if row["saveSucceededLogCount"] == 0],
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
            queue.get("totalFunctions") == 6222
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
    artifact_rows = []
    missing_tools = []
    missing_bases = []
    weak_artifacts = []
    log_bad_hits = []
    expected_context_missing_log_hits = []
    for script_name, command in sorted(scripts.items()):
        tool = probe_tool_for_command(command)
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

    probe_sweep = read_json(PROBE_SWEEP_SUMMARY)
    if probe_sweep.get("status") != "PASS":
        failures.append("prior Wave900+ focused-probe sweep is not PASS")
    if probe_sweep.get("missingScriptCount") != 0 or probe_sweep.get("extraScriptCount") != 0:
        failures.append("prior Wave900+ focused-probe sweep script coverage mismatch")
    disallowed_probe_failures = [
        row
        for row in probe_sweep.get("failureCategories", [])
        if "evidence-mismatch" in row.get("categories", []) or "unclassified" in row.get("categories", [])
    ]
    if disallowed_probe_failures:
        failures.append(f"prior focused probes have evidence/unclassified failures: {len(disallowed_probe_failures)}")

    apply_logs = apply_script_log_coverage()
    if apply_logs["missingLogScripts"]:
        failures.append(f"apply scripts without any log coverage: {len(apply_logs['missingLogScripts'])}")
    if apply_logs["missingCleanSummaryScripts"]:
        failures.append(f"apply scripts without clean summary log: {len(apply_logs['missingCleanSummaryScripts'])}")
    if apply_logs["missingSaveSucceededScripts"]:
        failures.append(f"apply scripts without save-succeeded log: {len(apply_logs['missingSaveSucceededScripts'])}")

    queue = current_queue_summary()
    if not queue["ok"]:
        failures.append("current queue is not closed at 6222/6222 with zero debt")

    return {
        "schema": "ghidra-wave900-plus-evidence-audit.v1",
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
        "artifactBaseCount": len(artifact_rows),
        "artifactRows": artifact_rows,
        "missingProbeTools": missing_tools,
        "missingProbeBases": missing_bases,
        "weakArtifactBases": weak_artifacts,
        "evidenceLogBadTokenHits": log_bad_hits,
        "expectedContextMissingLogHits": expected_context_missing_log_hits,
        "priorProbeSweep": {
            "status": probe_sweep.get("status"),
            "packageWaveScriptCount": probe_sweep.get("packageWaveScriptCount"),
            "resultCount": probe_sweep.get("resultCount"),
            "passCount": probe_sweep.get("passCount"),
            "failCount": probe_sweep.get("failCount"),
            "disallowedFailureCount": len(disallowed_probe_failures),
        },
        "applyScriptLogCoverage": apply_logs,
        "currentQueue": queue,
        "failures": failures,
        "interpretation": [
            "Wave910 and Wave911 are intentionally reported as non-backup operational waves because they are queue/planning records, not saved Ghidra mutation/review records with a project backup note.",
            "This audit verifies presence and shape of Wave900-Wave981 evidence, backups, probe/script coverage, apply-log coverage, and queue closure; it does not prove runtime behavior, exact source-layout identity, or rebuild parity.",
            "Historical focused probes are still checked through the prior sweep classifier; this audit adds readiness/evidence/backup structure checks around that sweep.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    report = build_report()
    write_json(OUT, report)
    print("Wave900+ second-level evidence audit")
    print("Status:", report["status"])
    print("Readiness notes:", report["readinessNoteCount"])
    print("Covered waves:", report["coveredWaveCount"])
    print("Package probe scripts:", report["packageProbeScriptCount"])
    print("Evidence bases:", report["artifactBaseCount"])
    print("Backup references:", report["backupAudit"]["backupReferenceCount"])
    print("Apply scripts:", report["applyScriptLogCoverage"]["applyScriptCount"])
    print("Current queue:", report["currentQueue"])
    if report["failures"]:
        for failure in report["failures"]:
            print("-", failure)
    return 1 if args.check and report["status"] != "PASS" else 0


if __name__ == "__main__":
    raise SystemExit(main())
