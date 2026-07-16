#!/usr/bin/env python3
"""Generate or validate portable/export release-classification artifacts.

The public repository is the working source repo and may track private RE notes
and proof summaries. R4_DENY in this
script means excluded from portable app ZIPs and legacy curated export payloads;
it does not automatically mean "must be absent from public source."
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
import fnmatch
from pathlib import Path
import json
import subprocess
import sys
from typing import Dict, Iterable

sys.dont_write_bytecode = True

import public_allowlist_safety_check as payload_safety


ROOT = Path(__file__).resolve().parents[1]


DENY_PREFIXES = (
    ".github/workflows/",
    ".codex/",
    "archive/",
    "game/",
    "media/",
    "save-attempts/",
    "GameProfiles/",
    "PatchBench/",
    "subagents/",
    "release/artifacts/",
    "release/out/",
    "release/readiness/private_runtime_evidence/",
    "discord_channel_dumps/",
    "wave_online_audit/",
    "wave_online_audit2/",
    "reverse-engineering/binary-analysis/scratch/",
    "lore-book/reverse-engineering/binary-analysis/scratch/",
)
DENY_EXACT = (
    "AGENTS.md",
    "USER_SANITY_CHECK.md",
    "onslaught_codex_directive.md",
    "MCP_DEBUGGING_OPTIONS.md",
    "MCP_LIMITATIONS.md",
    "package-lock.json",
    "developer_agent_state.json",
    "documentation_agent_state.json",
    "re_orchestrator_state.json",
    ".gitignore",
    "roadmap/release-allowlist-classification.tsv",
    "lore-book/roadmap/release-allowlist-classification.tsv",
    "roadmap/release-allowlist-profile.md",
    "lore-book/roadmap/release-allowlist-profile.md",
    "release/readiness/private_only_inventory.tsv",
    "release/readiness/LOCAL_SIGNOFF_COMMANDS.md",
    "release/readiness/private_public_payload_text_guard_patterns.json",
    "release/readiness/ralph_loop_goal_evidence_2026-05-01.md",
    "reverse-engineering/binary-analysis/MCP-MUTATION-BACKLOG.md",
    "lore-book/reverse-engineering/binary-analysis/MCP-MUTATION-BACKLOG.md",
    "reverse-engineering/binary-analysis/ghydra-mcp-runbook.md",
    "lore-book/reverse-engineering/binary-analysis/ghydra-mcp-runbook.md",
    "reverse-engineering/binary-analysis/documentation-audit.md",
    "lore-book/reverse-engineering/binary-analysis/documentation-audit.md",
    "reverse-engineering/binary-analysis/semantic-audit-2026-02-12.md",
    "lore-book/reverse-engineering/binary-analysis/semantic-audit-2026-02-12.md",
    "reverse-engineering/game-assets/mission-text-map.tsv",
    "lore-book/reverse-engineering/game-assets/mission-text-map.tsv",
    "tools/run_ghidra_batch_rename_headless.sh",
    "tools/run_ghidra_headless_postscript.sh",
    "tools/semantic_audit_online.py",
    "setuphistory.txt",
)
ALLOW_EXACT = {
    "tools/runtime-probes/local-multiplayer-level854-fire-damage-outcome-observer.cdb.txt": "public-safe-runtime-probe",
    "tools/runtime-probes/local-multiplayer-level854-fire-handoff-observer.cdb.txt": "public-safe-runtime-probe",
    "tools/runtime-probes/local-multiplayer-level854-input-assisted-outcome-observer.cdb.txt": "public-safe-runtime-probe",
}
DENY_GLOBS = (
    "OnslaughtCareerEditor.UiTests/TestResults/**",
    "**/GameProfiles/**",
    "**/PatchBench/**",
    "reverse-engineering/binary-analysis/free-camera-aurore-gate-bypass-patch.md",
    "lore-book/reverse-engineering/binary-analysis/free-camera-aurore-gate-bypass-patch.md",
    "reverse-engineering/binary-analysis/frontend-clear-screen-color-patch.md",
    "lore-book/reverse-engineering/binary-analysis/frontend-clear-screen-color-patch.md",
    "reverse-engineering/binary-analysis/goodies-gallery-display-unlock-patch.md",
    "lore-book/reverse-engineering/binary-analysis/goodies-gallery-display-unlock-patch.md",
    "reverse-engineering/binary-analysis/local-multiplayer-static-runtime-contract.md",
    "lore-book/reverse-engineering/binary-analysis/local-multiplayer-static-runtime-contract.md",
    "tools/winui_safe_copy_live_runtime_smoke.py",
    "tools/winui_safe_copy_live_runtime_smoke_test.py",
    "tools/capture_audio_loopback.py",
    "tools/winui_safe_copy_music_source_audio_correlation_check.py",
    "tools/winui_safe_copy_music_source_audio_correlation_check_test.py",
    "tools/winui_safe_copy_music_capture_source_correlation_builder.py",
    "tools/winui_safe_copy_music_capture_source_correlation_builder_test.py",
    "tools/winui_safe_copy_music_decode_window_correlation_diagnostic.py",
    "tools/winui_safe_copy_music_decode_window_correlation_diagnostic_test.py",
    "tools/run_winui_safe_copy_music_audible_output_live_bundle.py",
    "tools/run_winui_safe_copy_music_audible_output_live_bundle_test.py",
    "tools/winui_safe_copy_music_timestamped_cdb_log_producer.py",
    "tools/winui_safe_copy_music_timestamped_cdb_log_producer_test.py",
    "tools/winui_safe_copy_music_capture_source_correlation_check.py",
    "tools/winui_safe_copy_music_capture_source_correlation_check_test.py",
    "tools/winui_control_feel_diagnostics_matrix.py",
    "tools/winui_control_feel_telemetry_bundle_check.py",
    "tools/winui_control_feel_telemetry_bundle_check_test.py",
    "tools/winui_control_input_delta_artifact_check.py",
    "tools/winui_control_causality_contract_check.py",
    "tools/winui_enhanced_preview_runtime_artifact_check.py",
    "tools/ghidra_static_reaudit_progress_probe.py",
    "tools/export_curated_release_tree.py",
    "tools/release_curated_manifest.py",
    "tools/release_curated_manifest_test.py",
    "tools/release_profile_snapshot.py",
    "tools/release_package.sh",
    "tools/legacy_patch_script_safety_test.py",
    "tests_shared/fixtures/**",
    "tools/*private*",
    "tools/*Private*",
    "tools/*runtime*",
    "tools/*Runtime*",
    "tools/build_winui_original_binary_*",
    "tools/winui_original_binary_*",
    "tools/winui_safe_copy_online_*",
    "tools/runtime-probes/**",
    "tools/texture_mesh_material_sidecar_command_arm*",
    "tools/build_winui_original_binary_host_authority_n_slot_concurrent_process_smoke_bundle.py",
    "tools/build_winui_original_binary_host_authority_n_slot_process_smoke_bundle.py",
    "tools/build_winui_original_binary_host_authority_two_client_smoke_bundle.py",
    "tools/build_winui_original_binary_host_authority_runtime_delivery_bundle.py",
    "tools/build_winui_original_binary_local_relay_session_bundle.py",
    "tools/build_winui_original_binary_private_lan_transport_smoke_bundle.py",
    "tools/build_winui_original_binary_private_remote_client_smoke_bundle.py",
    "tools/build_winui_original_binary_private_remote_client_runtime_causality_bundle.py",
    "tools/build_winui_original_binary_joined_session_runtime_causality_bundle.py",
    "tools/build_winui_original_binary_joined_session_same_host_runtime_authority_bundle.py",
    "tools/build_winui_original_binary_second_host_command_source_bundle.py",
    "tools/build_winui_original_binary_second_host_command_source_bundle_test.py",
    "tools/build_winui_original_binary_wsl_remote_client_smoke_bundle.py",
    "tools/winui_original_binary_second_host_command_source_client.py",
    "tools/winui_original_binary_second_host_command_source_client_test.py",
    "tools/winui_original_binary_second_host_live_run_kit.py",
    "tools/winui_original_binary_second_host_live_run_kit_test.py",
    "tools/winui_safe_copy_live_runtime_control_options_artifact_check.py",
    "tools/winui_safe_copy_local_multiplayer_artifact_check.py",
    "tools/winui_safe_copy_local_multiplayer_cdb_observer_check.py",
    "tools/winui_safe_copy_local_multiplayer_input_isolation_check.py",
    "tools/winui_safe_copy_music_selection_decode_artifact_check.py",
    "tools/winui_safe_copy_music_swap_level100_decode_proof_check.py",
    "tools/winui_safe_copy_music_swap_preset_artifact_check.py",
    "tools/winui_safe_copy_online_host_authority_runtime_delivery_check.py",
    "tools/winui_safe_copy_online_host_authority_runtime_delivery_replayability_check.py",
    "tools/winui_safe_copy_online_host_authority_runtime_executor_check.py",
    "tools/winui_safe_copy_online_host_authority_runtime_movement_bridge_check.py",
    "tools/winui_safe_copy_online_host_authority_n_slot_concurrent_process_smoke_check.py",
    "tools/winui_safe_copy_online_host_authority_n_slot_process_smoke_check.py",
    "tools/winui_safe_copy_online_host_authority_n_slot_runtime_bridge_check.py",
    "tools/winui_safe_copy_online_host_authority_secure_n_slot_runtime_bridge_check.py",
    "tools/winui_safe_copy_online_host_authority_secure_n_slot_runtime_bridge_check_test.py",
    "tools/winui_safe_copy_online_host_authority_secure_n_slot_runtime_executor_check.py",
    "tools/winui_safe_copy_online_host_authority_secure_n_slot_runtime_executor_check_test.py",
    "tools/winui_safe_copy_online_host_authority_secure_n_slot_runtime_executor_replayability_check.py",
    "tools/winui_safe_copy_online_host_authority_secure_n_slot_runtime_executor_replayability_check_test.py",
    "tools/winui_safe_copy_online_host_authority_state_authority_observer_check.py",
    "tools/winui_safe_copy_online_host_authority_state_authority_replayability_check.py",
    "tools/winui_safe_copy_online_private_remote_client_runtime_causality_check.py",
    "tools/winui_safe_copy_online_private_remote_client_runtime_causality_check_test.py",
    "tools/build_winui_original_binary_second_host_runtime_delivery_bridge_bundle.py",
    "tools/winui_safe_copy_online_second_host_runtime_delivery_bridge_check.py",
    "tools/winui_safe_copy_online_second_host_runtime_delivery_bridge_check_test.py",
    "tools/build_winui_original_binary_second_host_runtime_executor_bundle.py",
    "tools/winui_safe_copy_online_second_host_runtime_executor_check.py",
    "tools/winui_safe_copy_online_second_host_runtime_executor_check_test.py",
    "tools/winui_safe_copy_online_joined_session_same_host_runtime_authority_check.py",
    "tools/winui_safe_copy_online_joined_session_same_host_runtime_authority_check_test.py",
    "tools/winui_safe_copy_online_second_host_runtime_causality_check_test.py",
    "tools/winui_safe_copy_online_second_host_runtime_causality_check.py",
    "tools/winui_safe_copy_online_second_host_runtime_promotion_guard.py",
    "tools/winui_safe_copy_online_second_host_runtime_promotion_guard_test.py",
    "tools/winui_safe_copy_online_host_join_enablement_check.py",
    "tools/winui_safe_copy_online_host_join_enablement_check_test.py",
    "tools/winui_safe_copy_online_joined_session_runtime_causality_check.py",
    "tools/winui_safe_copy_online_joined_session_runtime_causality_check_test.py",
    "tools/winui_safe_copy_online_session_scalability_contract_check.py",
    "tools/winui_safe_copy_online_slot_ceiling_guard_check.py",
    "tools/winui_safe_copy_online_wsl_remote_client_smoke_check.py",
    "tools/build_winui_original_binary_level850_mode_semantics_observer_bundle.py",
    "tools/winui_safe_copy_online_level850_mode_semantics_observer_check.py",
    "tools/winui_safe_copy_online_level850_mode_semantics_observer_check_test.py",
    "tools/build_winui_original_binary_level854_outcome_semantics_observer_bundle.py",
    "tools/winui_safe_copy_online_level854_outcome_semantics_observer_check.py",
    "tools/winui_safe_copy_online_level854_outcome_semantics_observer_check_test.py",
    "tools/build_winui_original_binary_level854_input_assisted_outcome_bundle.py",
    "tools/winui_safe_copy_online_level854_input_assisted_outcome_check.py",
    "tools/winui_safe_copy_online_level854_input_assisted_outcome_check_test.py",
    "tools/build_winui_original_binary_level854_fire_handoff_bundle.py",
    "tools/winui_safe_copy_online_level854_fire_handoff_check.py",
    "tools/winui_safe_copy_online_level854_fire_handoff_check_test.py",
    "tools/build_winui_original_binary_level854_fire_damage_outcome_bundle.py",
    "tools/winui_safe_copy_online_level854_fire_damage_outcome_check.py",
    "tools/winui_safe_copy_online_level854_fire_damage_outcome_check_test.py",
    "**/onslaught-profile-manifest.json",
    "**/onslaught-control-options-manifest.json",
    "**/onslaught-music-replacement-manifest.json",
    ".tmp_cs_*/**",
    "__pycache__/**",
    "**/__pycache__/**",
    "*.trx",
    "**/*.trx",
    "*.exe",
    "**/*.exe",
    "*.dll",
    "**/*.dll",
    "*.bes",
    "**/*.bes",
    "*.bea",
    "**/*.bea",
    "*.gzf",
    "**/*.gzf",
    "reverse-engineering/binary-analysis/*.json",
    "reverse-engineering/binary-analysis/*.jsonl",
    "lore-book/reverse-engineering/binary-analysis/*.json",
    "lore-book/reverse-engineering/binary-analysis/*.jsonl",
    "reverse-engineering/source-code/*-file-manifest-2026-02-11.tsv",
    "lore-book/reverse-engineering/source-code/*-file-manifest-2026-02-11.tsv",
)
CURATED_MANIFEST_PATH = Path("release/readiness/curated_release_manifest.json")
IGNORED_PARTS = {
    ".git",
    ".vs",
    "__pycache__",
    "bin",
    "obj",
    "TestResults",
    "AppPackages",
    "BundleArtifacts",
    "MsixPackages",
    "publish",
}


PAYLOAD_SAFETY_SCANNER_PATH = "tools/public_allowlist_safety_check.py"


@dataclass(frozen=True)
class Classification:
    path: str
    cls: str
    reason: str


def classify_path(path: str) -> Classification:
    if path == ".gitmodules":
        return Classification(path, "R3_CONDITIONAL", "submodule-map-review")

    allow_reason = ALLOW_EXACT.get(path)
    if allow_reason is not None:
        return Classification(path, "R0_ALLOW", allow_reason)

    for prefix in DENY_PREFIXES:
        if path.startswith(prefix):
            return Classification(path, "R4_DENY", prefix)

    for exact in DENY_EXACT:
        if path == exact:
            return Classification(path, "R4_DENY", exact)

    for pattern in DENY_GLOBS:
        if fnmatch.fnmatchcase(path, pattern):
            return Classification(path, "R4_DENY", pattern)

    if (
        path == "references/Onslaught"
        or path.startswith("references/Onslaught/")
        or path == "references/AYAResourceExtractor"
        or path.startswith("references/AYAResourceExtractor/")
    ):
        return Classification(path, "R3_CONDITIONAL", "references-submodules")

    if (
        (
            path.startswith("reverse-engineering/binary-analysis/")
            or path.startswith("lore-book/reverse-engineering/binary-analysis/")
        )
        and (path.endswith(".json") or path.endswith(".jsonl"))
    ):
        return Classification(path, "R2_REVIEW", "analysis-operational-data")

    volatile = (
        path.startswith("reverse-engineering/binary-analysis/scratch/")
        or path.startswith("lore-book/reverse-engineering/binary-analysis/scratch/")
        or path.startswith(".tmp_cs_")
        or path.endswith(".trx")
        or path.startswith("__pycache__/")
        or "/__pycache__/" in path
        or path.endswith(".exe")
        or path.endswith(".dll")
        or path.endswith(".bes")
        or path.endswith(".bea")
        or path.endswith(".bin")
        or path.endswith(".gzf")
    )
    if volatile:
        return Classification(path, "R2_REVIEW", "volatile-or-generated")

    payload_error_reason = classify_public_payload_safety(path)
    if payload_error_reason:
        return Classification(path, "R4_DENY", payload_error_reason)

    return Classification(path, "R0_ALLOW", "default")


def classify_public_payload_safety(path: str) -> str | None:
    if path == PAYLOAD_SAFETY_SCANNER_PATH:
        return None
    if not payload_safety.is_text_candidate(path):
        return None

    full_path = ROOT / path
    if not full_path.is_file():
        return None

    text = full_path.read_text(encoding="utf-8", errors="replace")
    errors = payload_safety.find_text_payload_errors(path, text, require_private_text_guard=True)
    if not errors:
        return None

    labels = sorted({error.split(" in ", 1)[0] for error in errors})
    return "public-payload-safety:" + ",".join(labels[:8])


def get_files(root: Path) -> list[str]:
    try:
        top = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=root,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if Path(top).resolve() != root.resolve():
            raise RuntimeError("nested tree or no local git index")
        out = subprocess.check_output(["git", "ls-files"], cwd=root, text=True, stderr=subprocess.DEVNULL)
        files = [line.strip() for line in out.splitlines() if line.strip()]
    except Exception as exc:
        raise RuntimeError(
            "release profile snapshot requires a source tree with its own git index; "
            "refusing filesystem fallback for tracked-only release accounting"
        ) from exc
    return sorted(set(files))


def render_tsv(rows: Iterable[Classification]) -> str:
    return "".join(f"{row.path}\t{row.cls}\t{row.reason}\n" for row in rows)


def render_private_inventory(rows: Iterable[Classification]) -> str:
    lines = ["path\tclass\treason\tportable_or_legacy_export_posture\n"]
    for row in rows:
        if row.cls not in {"R3_CONDITIONAL", "R4_DENY"}:
            continue
        posture = "exclude_from_portable_or_legacy_export"
        if row.cls == "R3_CONDITIONAL":
            posture = "manual_review_required"
        lines.append(f"{row.path}\t{row.cls}\t{row.reason}\t{posture}\n")
    return "".join(lines)


def load_curated_patterns(root: Path) -> list[str]:
    manifest = root / CURATED_MANIFEST_PATH
    if not manifest.is_file():
        return ["(missing manifest)"]
    data = json.loads(manifest.read_text(encoding="utf-8"))
    return [str(x) for x in data.get("include", [])]


def render_profile(
    generated_at: str,
    counts: dict[str, int],
    r3_paths: list[str],
    r4_paths: list[str],
    curated_patterns: list[str],
) -> str:
    r4_sample = r4_paths[:120]
    remaining = max(0, len(r4_paths) - len(r4_sample))

    lines: list[str] = []
    lines.append("# Release Allowlist Profile")
    lines.append("")
    lines.append(f"> Generated: {generated_at}")
    lines.append("")
    lines.append("## Classification Summary")
    lines.append("")
    lines.append("| Class | Count | Meaning |")
    lines.append("|---|---:|---|")
    lines.append(f"| R0_ALLOW | {counts['R0_ALLOW']} | Default allow bucket for portable/export release accounting (still requires human review before publishing an artifact) |")
    lines.append(f"| R2_REVIEW | {counts['R2_REVIEW']} | Volatile/generated/binary artifacts; include only when intentional |")
    lines.append(f"| R3_CONDITIONAL | {counts['R3_CONDITIONAL']} | Reference submodule families requiring licensing/scope review |")
    lines.append(f"| R4_DENY | {counts['R4_DENY']} | Excluded from portable app ZIPs and legacy curated export payloads; may still be tracked public source when compact, non-secret project history |")
    lines.append("")
    lines.append("Public-primary note: this profile is not the boundary for what may exist in")
    lines.append("the public source repo. It is an app/export accounting artifact. The source")
    lines.append("repo can track useful source, docs, tools, RE notes, compact proof summaries,")
    lines.append("state batons, and agent reports while still excluding raw game payloads, full")
    lines.append("Ghidra databases/backups, copied runtime output, raw captures/logs, build")
    lines.append("outputs, and secrets.")
    lines.append("")
    lines.append("## Legacy Curated Export Include Patterns")
    lines.append("")
    for item in curated_patterns:
        lines.append(f"- `{item}`")
    lines.append("")
    lines.append("## Portable/Legacy Export Exclusions")
    lines.append("")
    for item in DENY_PREFIXES:
        lines.append(f"- `{item}**`")
    for item in DENY_EXACT:
        lines.append(f"- `{item}`")
    for item in DENY_GLOBS:
        lines.append(f"- `{item}`")
    lines.append("")
    lines.append("## R3 Conditional Families (Manual Decision Required)")
    lines.append("")
    if r3_paths:
        for p in r3_paths:
            lines.append(f"- `{p}`")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## R4 Portable/Legacy Export Exclusions (Current Working Tree)")
    lines.append("")
    for p in r4_sample:
        lines.append(f"- `{p}`")
    if remaining:
        lines.append(f"- ... ({remaining} more entries in `roadmap/release-allowlist-classification.tsv`)")
    lines.append("")
    lines.append("## Re-run Commands")
    lines.append("")
    lines.append("```bash")
    lines.append("python3 tools/docsync_check.py")
    lines.append("python3 tools/release_profile_snapshot.py")
    lines.append("python3 tools/release_curated_manifest.py")
    lines.append("./tools/release_package.sh --dry-run")
    lines.append("```")
    lines.append("")
    lines.append("Notes:")
    lines.append("- `docsync_check.py` validates strict mirrors, normalized mirror-pairs, and curated canonical-pointer hints.")
    lines.append("- `release_profile_snapshot.py` regenerates classification/profile/private-inventory artifacts.")
    lines.append("- `release_curated_manifest.py` materializes `public_candidate_allowlist.tsv` from curated manifest patterns.")
    lines.append("- `release_package.sh --dry-run` runs all release policy gates.")
    lines.append("")
    return "\n".join(lines)


def _norm_text(text: str) -> str:
    return text.replace("\r\n", "\n")


def _load_existing_generated_at(path: Path) -> str | None:
    if not path.is_file():
        return None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("> Generated: "):
            return line.removeprefix("> Generated: ").strip()
    return None


def build_outputs(root: Path, generated_at: str, rows: list[Classification] | None = None) -> Dict[Path, str]:
    if rows is None:
        files = get_files(root)
        rows = [classify_path(p) for p in files]
    counts = {"R0_ALLOW": 0, "R2_REVIEW": 0, "R3_CONDITIONAL": 0, "R4_DENY": 0}
    for row in rows:
        counts[row.cls] += 1

    r3_paths = sorted([r.path for r in rows if r.cls == "R3_CONDITIONAL"])
    r4_paths = sorted([r.path for r in rows if r.cls == "R4_DENY"])
    curated_patterns = load_curated_patterns(root)
    profile_text = render_profile(generated_at, counts, r3_paths, r4_paths, curated_patterns).rstrip() + "\n"

    tsv_text = render_tsv(rows)
    return {
        root / "roadmap" / "release-allowlist-classification.tsv": tsv_text,
        root / "lore-book" / "roadmap" / "release-allowlist-classification.tsv": tsv_text,
        root / "release" / "readiness" / "private_only_inventory.tsv": render_private_inventory(rows),
        root / "roadmap" / "release-allowlist-profile.md": profile_text,
        root / "lore-book" / "roadmap" / "release-allowlist-profile.md": profile_text,
    }


def write_outputs(outputs: Dict[Path, str]) -> None:
    for path, text in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="")


def check_outputs(outputs: Dict[Path, str]) -> list[str]:
    errors: list[str] = []
    for path, expected in outputs.items():
        if not path.is_file():
            errors.append(f"missing artifact: {path.as_posix()}")
            continue
        actual = _norm_text(path.read_text(encoding="utf-8", errors="replace"))
        if actual != _norm_text(expected):
            errors.append(f"stale artifact: {path.as_posix()}")
    return errors


def check_sensitive_tool_classification(root: Path, rows: Iterable[Classification]) -> list[str]:
    sensitive_tokens = (
        "credentialHex",
        "socket.create_connection(",
        ".listen(",
        "def run_server(",
        "listener.bind(",
    )
    errors: list[str] = []
    for row in rows:
        if row.cls == "R4_DENY":
            continue
        if not row.path.startswith("tools/") or not row.path.endswith(".py"):
            continue
        if row.path == "tools/release_profile_snapshot.py":
            continue
        path = root / row.path
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        hits = [token for token in sensitive_tokens if token in text]
        if hits:
            errors.append(f"sensitive live-network/proof helper is not R4_DENY: {row.path} ({', '.join(hits)})")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--check",
        action="store_true",
        help="Validate that tracked snapshot artifacts are current without rewriting them.",
    )
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[1]
    profile_path = root / "roadmap" / "release-allowlist-profile.md"
    generated_at = (
        _load_existing_generated_at(profile_path)
        if args.check
        else datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    )

    if args.check and not generated_at:
        print(f"ERROR: cannot validate snapshot; missing generated timestamp in {profile_path.as_posix()}")
        return 2

    files = get_files(root)
    rows = [classify_path(p) for p in files]
    outputs = build_outputs(root, generated_at, rows)
    sensitive_errors = check_sensitive_tool_classification(root, rows)
    counts = {"R0_ALLOW": 0, "R2_REVIEW": 0, "R3_CONDITIONAL": 0, "R4_DENY": 0}
    for row in rows:
        counts[row.cls] += 1

    if args.check:
        errors = check_outputs(outputs) + sensitive_errors
        if errors:
            print("Release profile snapshot check: FAIL")
            for err in errors:
                print(f"- {err}")
            return 1
        print("Release profile snapshot check: PASS")
        print(
            f"Counts: R0={counts['R0_ALLOW']} R2={counts['R2_REVIEW']} "
            f"R3={counts['R3_CONDITIONAL']} R4={counts['R4_DENY']}"
        )
        return 0

    if sensitive_errors:
        print("Release profile snapshot generation blocked:")
        for err in sensitive_errors:
            print(f"- {err}")
        return 1

    write_outputs(outputs)

    print("Generated release profile snapshot artifacts:")
    for path in outputs:
        print(f"- {path}")
    print(
        f"Counts: R0={counts['R0_ALLOW']} R2={counts['R2_REVIEW']} "
        f"R3={counts['R3_CONDITIONAL']} R4={counts['R4_DENY']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
