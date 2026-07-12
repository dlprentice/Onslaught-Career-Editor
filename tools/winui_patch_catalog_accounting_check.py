#!/usr/bin/env python3
"""Validate the active patch/profile contracts and their public accounting."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "patches" / "catalog" / "patches.v2.json"
PROFILE_CATALOG = ROOT / "patches" / "catalog" / "safe-copy-profiles.v1.json"
REGISTER = ROOT / "roadmap" / "mod-patch-runtime-rebuild-register.md"
PATCH_README = ROOT / "patches" / "README.md"
CURRENT_CAPABILITIES = ROOT / "CURRENT_CAPABILITIES.md"
CURRENT_CAPABILITIES_LORE = ROOT / "lore-book" / "CURRENT_CAPABILITIES.md"
RE_ORCHESTRATOR_STATE = ROOT / "re_orchestrator_state.json"
CATALOG_HASH_PIN_SOURCES = (
    (ROOT / "OnslaughtCareerEditor.AppCore" / "BinaryPatchEngine.cs", "ExpectedPatchCatalogSha256"),
    (ROOT / "tools" / "apply_bea_catalog_patch.py", "EXPECTED_CATALOG_SHA256"),
)
STATE_FILES = (
    ROOT / "developer_agent_state.json",
    ROOT / "documentation_agent_state.json",
    RE_ORCHESTRATOR_STATE,
)

CATALOG_VERSION = "2.1"
PROFILE_SCHEMA_VERSION = "safe-copy-profiles.v1"
TARGET_HASH = "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750"
TARGET_SIZE = 2_506_752
WINDOWED_PAIR = {"resolution_gate", "force_windowed"}
ALLOWED_TRACKS = {"stable", "experimental"}
ALLOWED_SELECTABILITY = {
    "profile_visible",
    "optional_visible",
    "experimental_visible",
    "hidden_companion",
}
ALLOWED_CONFIDENCE = {"high", "medium-high", "medium", "low"}
ALLOWED_PROOF_LEVELS = {
    "byte_verified_static_and_copied_launch_pair",
    "byte_verified_static_and_copied_launch_smoke",
    "companion_payload_byte_verified",
    "experimental_byte_verified_startup_path",
    "experimental_copied_runtime_cdb_ordered_o_window_proof",
    "experimental_copied_runtime_cdb_q_backward_proof",
    "experimental_copied_runtime_cdb_q_forward_proof",
    "experimental_copied_runtime_cdb_q_pitch_down_proof",
    "experimental_copied_runtime_cdb_q_pitch_up_proof",
    "experimental_copied_runtime_cdb_q_strafe_left_proof",
    "experimental_copied_runtime_cdb_q_strafe_right_proof",
    "experimental_copied_runtime_cdb_q_yaw_left_proof",
    "experimental_copied_runtime_cdb_q_yaw_right_proof",
    "experimental_copied_runtime_cdb_toggle_proof",
    "goodies_wall_runtime_visual_smoke",
    "title_screen_runtime_visual_smoke",
}
STALE_PHRASES = (
    "25/25 rows",
    "25/25 target",
    "18 visible",
    "18/18 visible",
    "validated and ready for commit/push",
    "Commit/push the validated free-camera Q-pitch remap proof slice",
)
HEX_BYTE = re.compile(r"^[0-9A-Fa-f]{2}$")
HEX_OFFSET = re.compile(r"^0x[0-9A-Fa-f]+$")
DIAGNOSTIC_STATUS = re.compile(r"(?im)^Status:.*\b(rejected|diagnostic|negative|exploratory)\b")
FORBIDDEN_REFERENCE_ROOTS = {
    ".codex",
    "game",
    "local-proofs",
    "runtime-proofs",
    "save-attempts",
    "subagents",
}
FULL_FILE_ROLLBACK_STRATEGY = (
    "Restore the copied BEA.exe from its verified full-file BEA.exe.original.backup snapshot; "
    "do not restore individual patch rows."
)
EXPECTED_PROOF_BY_ID = {
    "resolution_gate": "byte_verified_static_and_copied_launch_pair",
    "force_windowed": "byte_verified_static_and_copied_launch_pair",
    "extra_graphics_default_on": "byte_verified_static_and_copied_launch_smoke",
    "ignore_cardid_tweak_overrides": "byte_verified_static_and_copied_launch_smoke",
    "version_overlay_use_patched_format_pointer": "title_screen_runtime_visual_smoke",
    "version_overlay_patched_format_cave_string": "companion_payload_byte_verified",
    "frontend_clear_screen_dark_red": "title_screen_runtime_visual_smoke",
    "frontend_clear_screen_dark_green": "title_screen_runtime_visual_smoke",
    "frontend_clear_screen_black": "title_screen_runtime_visual_smoke",
    "goodies_gallery_display_unlock": "goodies_wall_runtime_visual_smoke",
    "skip_auto_toggle": "experimental_byte_verified_startup_path",
    "pause_o_scan_initializer_experiment": "experimental_copied_runtime_cdb_ordered_o_window_proof",
    "free_camera_aurore_gate_bypass": "experimental_copied_runtime_cdb_toggle_proof",
}
REQUIRED_EVIDENCE_BY_ID: dict[str, set[str]] = {
    "resolution_gate": {"release/readiness/winui_safe_copy_live_runtime_smoke_2026-06-17.md"},
    "force_windowed": {"release/readiness/winui_safe_copy_live_runtime_smoke_2026-06-17.md"},
    "extra_graphics_default_on": {"release/readiness/winui_modern_graphics_live_runtime_smoke_2026-06-17.md"},
    "ignore_cardid_tweak_overrides": {"release/readiness/winui_modern_graphics_live_runtime_smoke_2026-06-17.md"},
    "version_overlay_use_patched_format_pointer": {"release/readiness/winui_version_overlay_runtime_smoke_2026-06-17.md"},
    "version_overlay_patched_format_cave_string": {"release/readiness/winui_version_overlay_runtime_smoke_2026-06-17.md"},
    "frontend_clear_screen_dark_red": {
        "release/readiness/winui_frontend_clear_screen_color_patch_2026-06-16.md",
        "release/readiness/winui_frontend_color_navigated_runtime_proof_2026-06-18.md",
    },
    "frontend_clear_screen_dark_green": {
        "release/readiness/winui_frontend_clear_screen_color_patch_2026-06-16.md",
        "release/readiness/winui_frontend_color_navigated_runtime_proof_2026-06-18.md",
    },
    "frontend_clear_screen_black": {
        "release/readiness/winui_frontend_clear_screen_color_patch_2026-06-16.md",
        "release/readiness/winui_frontend_color_navigated_runtime_proof_2026-06-18.md",
    },
    "goodies_gallery_display_unlock": {"release/readiness/winui_goodies_gallery_display_unlock_2026-06-17.md"},
    "pause_o_scan_initializer_experiment": {
        "release/readiness/winui_pause_o_scan_initializer_runtime_2026-06-18.md",
        "release/readiness/winui_pause_o_scan_initializer_normal_gameplay_resume_2026-06-19.md",
    },
    "free_camera_aurore_gate_bypass": {
        "release/readiness/winui_free_camera_aurore_gate_bypass_2026-06-17.md",
        "release/readiness/winui_safe_copy_free_camera_toggle_2026-06-18.md",
    },
}
for _mode in (
    "forward",
    "backward",
    "strafe_left",
    "strafe_right",
    "yaw_left",
    "yaw_right",
    "pitch_up",
    "pitch_down",
):
    _proof = f"experimental_copied_runtime_cdb_q_{_mode}_proof"
    _evidence = f"release/readiness/winui_free_camera_q_{_mode}_runtime_2026-06-18.md"
    for _kind in ("cave", "hook"):
        _patch_id = f"free_camera_keyboard_{_mode}_q_{_kind}"
        EXPECTED_PROOF_BY_ID[_patch_id] = _proof
        REQUIRED_EVIDENCE_BY_ID[_patch_id] = {_evidence}


class AccountingError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AccountingError(message)


def read_json_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def require_text(value: Any, label: str) -> str:
    require(isinstance(value, str) and bool(value.strip()), f"{label} must be a non-empty string")
    return value.strip()


def string_list(value: Any, label: str, *, allow_empty: bool = True) -> list[str]:
    require(isinstance(value, list), f"{label} must be an array")
    require(all(isinstance(item, str) and item.strip() for item in value), f"{label} must contain non-empty strings")
    result = [item.strip() for item in value]
    require(len(result) == len({item.casefold() for item in result}), f"{label} contains duplicate values")
    if not allow_empty:
        require(bool(result), f"{label} must not be empty")
    return result


def require_review_date(document: dict[str, Any], label: str) -> None:
    require("generated_at" not in document, f"{label} uses stale generated_at metadata; use last_reviewed_at")
    raw = require_text(document.get("last_reviewed_at"), f"{label}.last_reviewed_at")
    try:
        date.fromisoformat(raw)
    except ValueError as exc:
        raise AccountingError(f"{label}.last_reviewed_at must be an ISO date") from exc


def parse_hex_bytes(value: Any, label: str) -> bytes:
    text = require_text(value, label)
    tokens = text.split()
    require(bool(tokens) and all(HEX_BYTE.fullmatch(token) for token in tokens), f"{label} must be space-delimited two-digit hex bytes")
    return bytes(int(token, 16) for token in tokens)


def validate_reference(ref: str, label: str, root: Path, *, accepted: bool) -> None:
    relative = Path(ref)
    require(not relative.is_absolute() and ".." not in relative.parts, f"{label} must be a safe repository-relative path")
    first_part = relative.parts[0].lower() if relative.parts else ""
    require(first_part not in FORBIDDEN_REFERENCE_ROOTS, f"{label} points to a private/runtime evidence root: {ref}")
    resolved_root = root.resolve()
    resolved = (root / relative).resolve()
    require(resolved == resolved_root or resolved_root in resolved.parents, f"{label} escapes the repository")
    require(resolved.is_file(), f"{label} does not exist: {ref}")
    if accepted:
        text = resolved.read_text(encoding="utf-8", errors="replace")
        require(not DIAGNOSTIC_STATUS.search(text), f"{label} points to diagnostic evidence: {ref}")
    else:
        text = resolved.read_text(encoding="utf-8", errors="replace")
        classified = "diagnostic" in relative.name.lower() or bool(DIAGNOSTIC_STATUS.search(text))
        require(classified, f"{label} is not classified as diagnostic evidence: {ref}")


def is_hidden(row: dict[str, Any]) -> bool:
    return str(row.get("selectability", "")).lower() == "hidden_companion"


def track_counts(rows: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        track = str(row.get("track", "")).lower()
        counts[track] = counts.get(track, 0) + 1
    return counts


def validate_row(row: dict[str, Any], root: Path) -> tuple[int, int]:
    row_id = require_text(row.get("id"), "patch row id")
    prefix = f"patch {row_id}"
    require_text(row.get("title"), f"{prefix}.title")
    track = require_text(row.get("track"), f"{prefix}.track").lower()
    require(track in ALLOWED_TRACKS, f"{prefix}.track must be stable or experimental")
    require(row.get("target_binary_hashes") == [TARGET_HASH], f"{prefix} has non-canonical target hashes")
    require(row.get("target_binary_size") == TARGET_SIZE, f"{prefix} has non-canonical target size")

    offset_text = require_text(row.get("file_offset"), f"{prefix}.file_offset")
    require(bool(HEX_OFFSET.fullmatch(offset_text)), f"{prefix}.file_offset must be 0x-prefixed hex")
    offset = int(offset_text, 16)
    original = parse_hex_bytes(row.get("expected_original_bytes"), f"{prefix}.expected_original_bytes")
    patched = parse_hex_bytes(row.get("patched_bytes"), f"{prefix}.patched_bytes")
    require(len(original) == len(patched), f"{prefix} must have equal byte lengths")
    require(original != patched, f"{prefix} defines a no-op mutation")
    require(offset + len(original) <= TARGET_SIZE, f"{prefix} byte span exceeds the target binary")

    require_text(row.get("purpose"), f"{prefix}.purpose")
    string_list(row.get("preconditions"), f"{prefix}.preconditions", allow_empty=False)
    effects = row.get("side_effects")
    postconditions = row.get("postconditions")
    require(effects is not None or postconditions is not None, f"{prefix} needs side_effects or postconditions")
    if effects is not None:
        string_list(effects, f"{prefix}.side_effects", allow_empty=False)
    if postconditions is not None:
        string_list(postconditions, f"{prefix}.postconditions", allow_empty=False)
    rollback_strategy = require_text(row.get("rollback_strategy"), f"{prefix}.rollback_strategy")
    require(
        rollback_strategy == FULL_FILE_ROLLBACK_STRATEGY,
        f"{prefix}.rollback_strategy must use the verified full-file backup snapshot",
    )
    require_text(row.get("verification_probe"), f"{prefix}.verification_probe")
    confidence = require_text(row.get("confidence"), f"{prefix}.confidence").lower()
    require(confidence in ALLOWED_CONFIDENCE, f"{prefix}.confidence is not supported")

    require("references" not in row, f"{prefix} uses the legacy references alias")
    evidence_refs = string_list(row.get("evidence_refs"), f"{prefix}.evidence_refs", allow_empty=False)
    diagnostic_refs = string_list(row.get("diagnostic_refs", []), f"{prefix}.diagnostic_refs")
    accepted_paths = {ref.casefold() for ref in evidence_refs}
    diagnostic_paths = {ref.casefold() for ref in diagnostic_refs}
    require(not accepted_paths.intersection(diagnostic_paths), f"{prefix} mixes accepted and diagnostic references")
    for ref in evidence_refs:
        validate_reference(ref, f"{prefix}.evidence_refs", root, accepted=True)
    for ref in diagnostic_refs:
        validate_reference(ref, f"{prefix}.diagnostic_refs", root, accepted=False)

    require(isinstance(row.get("optional"), bool), f"{prefix}.optional must be boolean")
    string_list(row.get("dependencies"), f"{prefix}.dependencies")
    string_list(row.get("conflicts"), f"{prefix}.conflicts")
    exclusive_group = row.get("exclusive_group")
    require(isinstance(exclusive_group, str), f"{prefix}.exclusive_group must be a string")
    require(not exclusive_group or bool(exclusive_group.strip()), f"{prefix}.exclusive_group cannot be whitespace")
    require(exclusive_group == exclusive_group.strip(), f"{prefix}.exclusive_group must be trimmed")
    proof_level = require_text(row.get("proof_level"), f"{prefix}.proof_level")
    require(proof_level in ALLOWED_PROOF_LEVELS, f"{prefix}.proof_level is not a supported evidence class")
    expected_proof = EXPECTED_PROOF_BY_ID.get(row_id)
    require(expected_proof is not None, f"{prefix} has no row-specific proof contract")
    require(proof_level == expected_proof, f"{prefix}.proof_level drifted from its accepted evidence class")
    required_evidence = REQUIRED_EVIDENCE_BY_ID.get(row_id, set())
    missing_evidence = sorted(required_evidence.difference(evidence_refs))
    require(not missing_evidence, f"{prefix} is missing required evidence: {', '.join(missing_evidence)}")
    selectability = require_text(row.get("selectability"), f"{prefix}.selectability").lower()
    require(selectability in ALLOWED_SELECTABILITY, f"{prefix}.selectability is not supported")
    preset_eligibility = string_list(row.get("preset_eligibility"), f"{prefix}.preset_eligibility")
    require(isinstance(row.get("requires_windowed_pair"), bool), f"{prefix}.requires_windowed_pair must be boolean")
    if selectability == "hidden_companion":
        require(row["optional"] is True, f"{prefix} hidden companion must be optional")
        require(not preset_eligibility, f"{prefix} hidden companion cannot be preset eligible")

    return offset, offset + len(original)


def dependency_closure(start: Iterable[str], by_id: dict[str, dict[str, Any]]) -> set[str]:
    closure = set(start)
    pending = list(start)
    while pending:
        current = pending.pop()
        for dependency in by_id[current]["dependencies"]:
            if dependency not in closure:
                closure.add(dependency)
                pending.append(dependency)
    return closure


def assert_graph(rows: list[dict[str, Any]], spans: dict[str, tuple[int, int]]) -> dict[str, int]:
    by_id = {row["id"]: row for row in rows}
    canonical_ids = {row_id.casefold(): row_id for row_id in by_id}
    for row in rows:
        for field in ("dependencies", "conflicts"):
            row[field] = [canonical_ids.get(value.casefold(), value) for value in row[field]]
    ids = set(by_id)

    for row in rows:
        row_id = row["id"]
        dependencies = row["dependencies"]
        conflicts = row["conflicts"]
        require(row_id not in dependencies, f"patch {row_id} depends on itself")
        require(row_id not in conflicts, f"patch {row_id} conflicts with itself")
        unknown_dependency = next((value for value in dependencies if value not in ids), None)
        require(unknown_dependency is None, f"patch {row_id} has unknown dependency {unknown_dependency}")
        unknown_conflict = next((value for value in conflicts if value not in ids), None)
        require(unknown_conflict is None, f"patch {row_id} has unknown conflict {unknown_conflict}")
        for conflict in conflicts:
            require(row_id in by_id[conflict]["conflicts"], f"asymmetric conflict between {row_id} and {conflict}")

    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(row_id: str, path: list[str]) -> None:
        if row_id in visiting:
            cycle = " -> ".join([*path, row_id])
            raise AccountingError(f"dependency cycle: {cycle}")
        if row_id in visited:
            return
        visiting.add(row_id)
        for dependency in by_id[row_id]["dependencies"]:
            visit(dependency, [*path, row_id])
        visiting.remove(row_id)
        visited.add(row_id)

    for row_id in ids:
        visit(row_id, [])

    exclusive_groups: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        if row["exclusive_group"]:
            exclusive_groups.setdefault(row["exclusive_group"].casefold(), []).append(row)
    for members in exclusive_groups.values():
        for index, left in enumerate(members):
            for right in members[index + 1 :]:
                require(
                    right["id"] in left["conflicts"] and left["id"] in right["conflicts"],
                    f"exclusive group peers must conflict: {left['id']} and {right['id']}",
                )

    visible_ids = {row["id"] for row in rows if not is_hidden(row)}
    reachable = dependency_closure(visible_ids, by_id)
    orphaned = sorted(row["id"] for row in rows if is_hidden(row) and row["id"] not in reachable)
    require(not orphaned, f"orphaned hidden companion rows: {', '.join(orphaned)}")

    for visible_id in visible_ids:
        expanded = dependency_closure({visible_id}, by_id)
        if any(by_id[key]["requires_windowed_pair"] for key in expanded):
            expanded = dependency_closure(expanded | WINDOWED_PAIR, by_id)
        for key in expanded:
            conflict = next((item for item in by_id[key]["conflicts"] if item in expanded), None)
            require(
                conflict is None,
                f"visible row closure contains conflicting rows: {visible_id} expands to {key} and {conflict}",
            )
        selected_groups = [by_id[key]["exclusive_group"].casefold() for key in expanded if by_id[key]["exclusive_group"]]
        require(
            len(selected_groups) == len(set(selected_groups)),
            f"visible row closure contains multiple rows from one exclusive group: {visible_id}",
        )

    for index, left in enumerate(rows):
        left_start, left_end = spans[left["id"]]
        for right in rows[index + 1 :]:
            right_start, right_end = spans[right["id"]]
            overlap_start = max(left_start, right_start)
            overlap_end = min(left_end, right_end)
            if overlap_start >= overlap_end:
                continue
            left_original = parse_hex_bytes(left["expected_original_bytes"], "left expected bytes")
            left_patched = parse_hex_bytes(left["patched_bytes"], "left patched bytes")
            right_original = parse_hex_bytes(right["expected_original_bytes"], "right expected bytes")
            right_patched = parse_hex_bytes(right["patched_bytes"], "right patched bytes")
            identical = (
                left_start == right_start
                and left_end == right_end
                and left_original == right_original
                and left_patched == right_patched
            )
            explicit_conflict = right["id"] in left["conflicts"] and left["id"] in right["conflicts"]
            require(
                identical or explicit_conflict,
                f"overlapping mutation {left['id']} and {right['id']} lacks exclusion",
            )

    return {
        "dependencyEdges": sum(len(row["dependencies"]) for row in rows),
        "conflictEdges": sum(len(row["conflicts"]) for row in rows),
    }


def assert_profiles(document: dict[str, Any], rows: list[dict[str, Any]], root: Path) -> None:
    require(document.get("schema_version") == PROFILE_SCHEMA_VERSION, "safe-copy profile schema version is unsupported")
    require_review_date(document, "safe-copy profile catalog")
    profiles = document.get("profiles")
    require(isinstance(profiles, list) and all(isinstance(profile, dict) for profile in profiles), "safe-copy profile catalog must contain profile objects")
    profile_ids = [require_text(profile.get("id"), "profile id") for profile in profiles]
    require(
        len(profile_ids) == len({profile_id.casefold() for profile_id in profile_ids}),
        "safe-copy profile catalog contains case-insensitive duplicate ids",
    )
    known_profile_ids = {profile_id.casefold() for profile_id in profile_ids}
    for row in rows:
        unknown_eligibility = next(
            (
                profile_id
                for profile_id in row["preset_eligibility"]
                if profile_id.casefold() not in known_profile_ids
            ),
            None,
        )
        require(
            unknown_eligibility is None,
            f"patch {row['id']} names unknown preset eligibility {unknown_eligibility}",
        )
    by_id = {row["id"]: row for row in rows}
    canonical_ids = {row_id.casefold(): row_id for row_id in by_id}

    for profile in profiles:
        profile_id = profile["id"]
        prefix = f"profile {profile_id}"
        require_text(profile.get("display_name"), f"{prefix}.display_name")
        require_text(profile.get("description"), f"{prefix}.description")
        require_text(profile.get("proof_status"), f"{prefix}.proof_status")
        require(isinstance(profile.get("is_selectable"), bool), f"{prefix}.is_selectable must be boolean")
        raw_keys = string_list(profile.get("patch_keys"), f"{prefix}.patch_keys")
        if profile_id.casefold() != "custom":
            require(bool(raw_keys), f"{prefix} non-custom profile must select a patch row")
        unknown = next((key for key in raw_keys if key.casefold() not in canonical_ids), None)
        require(unknown is None, f"{prefix} uses unknown patch row {unknown}")
        keys = [canonical_ids[key.casefold()] for key in raw_keys]
        if profile_id.casefold() != "custom":
            require(bool(keys), f"{prefix} non-custom profile must select a patch row")
        hidden = next((key for key in keys if is_hidden(by_id[key])), None)
        require(hidden is None, f"{prefix} directly selects hidden companion {hidden}")
        profile_key = profile_id.casefold()
        ineligible = next(
            (
                key
                for key in keys
                if profile_key not in {value.casefold() for value in by_id[key]["preset_eligibility"]}
            ),
            None,
        )
        require(ineligible is None, f"{prefix} patch row {ineligible} is not eligible for this preset")

        expanded = dependency_closure(keys, by_id)
        if any(by_id[key]["requires_windowed_pair"] for key in expanded):
            require(WINDOWED_PAIR.issubset(expanded), f"{prefix} omits the required windowed pair")
        for key in expanded:
            conflict = next((item for item in by_id[key]["conflicts"] if item in expanded), None)
            require(conflict is None, f"{prefix} expands to conflicting rows {key} and {conflict}")

        modules = profile.get("modules")
        require(isinstance(modules, list) and all(isinstance(module, dict) for module in modules), f"{prefix}.modules must contain objects")
        module_ids = [require_text(module.get("id"), f"{prefix} module id") for module in modules]
        require(
            len(module_ids) == len({module_id.casefold() for module_id in module_ids}),
            f"{prefix} contains case-insensitive duplicate module ids",
        )
        module_keys: set[str] = set()
        module_key_owners: dict[str, int] = {}
        for module in modules:
            module_id = module["id"]
            module_prefix = f"{prefix} module {module_id}"
            for field in ("display_name", "category", "proof_status", "claim_boundary", "restore_strategy"):
                require_text(module.get(field), f"{module_prefix}.{field}")
            non_claims = string_list(module.get("non_claims"), f"{module_prefix}.non_claims", allow_empty=False)
            require(bool(non_claims), f"{module_prefix} needs explicit non-claims")
            evidence_refs = string_list(module.get("evidence_refs"), f"{module_prefix}.evidence_refs", allow_empty=False)
            for ref in evidence_refs:
                validate_reference(ref, f"{module_prefix}.evidence_refs", root, accepted=True)
            raw_current_keys = string_list(module.get("patch_keys"), f"{module_prefix}.patch_keys")
            unknown_module_key = next(
                (key for key in raw_current_keys if key.casefold() not in canonical_ids),
                None,
            )
            require(unknown_module_key is None, f"{module_prefix} uses unknown patch row {unknown_module_key}")
            current_keys = [canonical_ids[key.casefold()] for key in raw_current_keys]
            module_keys.update(current_keys)
            for key in current_keys:
                module_key_owners[key] = module_key_owners.get(key, 0) + 1
            require(set(current_keys).issubset(keys), f"{module_prefix} names a row outside its profile")
            string_list(module.get("launch_arguments"), f"{module_prefix}.launch_arguments")
            string_list(module.get("copied_options_edits"), f"{module_prefix}.copied_options_edits")
        require(module_keys == set(keys), f"{prefix} module patch coverage differs from profile patch_keys")
        ambiguous_keys = sorted(key for key, owners in module_key_owners.items() if owners != 1)
        require(not ambiguous_keys, f"{prefix} module patch ownership is ambiguous: {', '.join(ambiguous_keys)}")


def validate_catalog_and_profiles(
    catalog: dict[str, Any],
    profiles: dict[str, Any],
    *,
    root: Path = ROOT,
) -> dict[str, Any]:
    require(catalog.get("catalog_version") == CATALOG_VERSION, "patch catalog version is unsupported")
    require(catalog.get("binary") == "BEA.exe", "patch catalog binary must be BEA.exe")
    require_review_date(catalog, "patch catalog")
    rows = catalog.get("patches")
    require(isinstance(rows, list) and all(isinstance(row, dict) for row in rows), "patch catalog must contain patch objects")
    ids = [require_text(row.get("id"), "patch row id") for row in rows]
    require(
        len(ids) == len({row_id.casefold() for row_id in ids}),
        "patch catalog contains case-insensitive duplicate ids",
    )
    spans = {row["id"]: validate_row(row, root) for row in rows}
    graph = assert_graph(rows, spans)
    assert_profiles(profiles, rows, root)

    visible = [row for row in rows if not is_hidden(row)]
    visible_tracks = track_counts(visible)
    all_tracks = track_counts(rows)
    require(set(all_tracks).issubset(ALLOWED_TRACKS), "catalog contains an unsupported track")

    return {
        "total": len(rows),
        "visible": len(visible),
        "hidden": len(rows) - len(visible),
        "allTracks": all_tracks,
        "visibleTracks": visible_tracks,
        "identityRows": len(rows),
        "policyRows": len(rows),
        **graph,
    }


def extract_hash_pin(source: str, constant_name: str) -> str:
    pattern = re.compile(
        rf'(?m)^[ \t]*(?:private[ \t]+const[ \t]+string[ \t]+)?{re.escape(constant_name)}'
        rf'[ \t]*=[ \t]*"([0-9A-Fa-f]{{64}})"[ \t]*;?[ \t]*$'
    )
    matches = pattern.findall(source)
    require(len(matches) == 1, f"expected exactly one active {constant_name} assignment")
    return matches[0].lower()


def assert_catalog_hash_pins() -> str:
    digest = hashlib.sha256(CATALOG.read_bytes()).hexdigest()
    for path, constant_name in CATALOG_HASH_PIN_SOURCES:
        text = path.read_text(encoding="utf-8")
        actual = extract_hash_pin(text, constant_name)
        require(actual == digest, f"{path.relative_to(ROOT)} has a stale {constant_name} pin")
    return digest


def assert_register(summary: dict[str, Any]) -> None:
    text = REGISTER.read_text(encoding="utf-8")
    expected_snippets = [
        f"| Visible executable patch options | `{summary['visible']} visible options: {summary['visibleTracks']['stable']} stable, {summary['visibleTracks']['experimental']} experimental`",
        f"| Patch-row proof clarity | `{summary['visible']}/{summary['visible']} visible rows with proof drawer fields`",
        f"| Catalog rows with target specimen identity | `{summary['total']}/{summary['total']} rows`",
        f"| Catalog rows with policy metadata | `{summary['total']}/{summary['total']} rows`",
        f"policy metadata for all {summary['total']} rows",
    ]
    missing = [snippet for snippet in expected_snippets if snippet not in text]
    require(not missing, "register missing expected accounting snippets: " + "; ".join(missing))
    for phrase in ("25/25 rows", "25/25 target", "18 visible", "18/18 visible", "all 14 rows"):
        require(phrase not in text, f"register contains stale phrase: {phrase}")


def assert_public_markers(summary: dict[str, Any]) -> None:
    marker = (
        f"Current patch catalog accounting: {summary['total']} total rows; "
        f"{summary['visible']} visible options "
        f"({summary['visibleTracks']['stable']} stable, {summary['visibleTracks']['experimental']} experimental); "
        f"{summary['hidden']} hidden companions."
    )
    for path in (PATCH_README, CURRENT_CAPABILITIES):
        text = path.read_text(encoding="utf-8")
        require(marker in text, f"{path.relative_to(ROOT)} missing current patch catalog accounting marker")
    if CURRENT_CAPABILITIES_LORE.exists():
        text = CURRENT_CAPABILITIES_LORE.read_text(encoding="utf-8")
        require(marker in text, f"{CURRENT_CAPABILITIES_LORE.relative_to(ROOT)} missing current patch catalog accounting marker")


def expected_state_counters(summary: dict[str, Any]) -> tuple[str, str]:
    visible = f"{summary['visible']} visible options: {summary['visibleTracks']['stable']} stable, {summary['visibleTracks']['experimental']} experimental"
    catalog = f"{summary['total']}/{summary['total']} target specimen identity and policy metadata rows"
    return visible, catalog


def assert_state(
    summary: dict[str, Any],
    *,
    state_files: Iterable[Path] = STATE_FILES,
    counter_owner: Path = RE_ORCHESTRATOR_STATE,
) -> None:
    expected_visible, expected_catalog = expected_state_counters(summary)
    owner = counter_owner.resolve()
    for path in state_files:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in STALE_PHRASES:
            require(phrase not in text, f"{path.name} contains stale phrase: {phrase}")
        state = json.loads(text)
        require(isinstance(state, dict), f"{path.name} must contain a JSON object")
        if path.resolve() != owner:
            continue
        counters = state.get("currentCounters", {})
        require(isinstance(counters, dict), f"{path.name} currentCounters must be an object")
        require(counters.get("visiblePatchRows") == expected_visible, f"{path.name} visiblePatchRows is stale")
        require(counters.get("catalogRows") == expected_catalog, f"{path.name} catalogRows is stale")


def check() -> dict[str, Any]:
    assert_catalog_hash_pins()
    summary = validate_catalog_and_profiles(
        read_json_object(CATALOG),
        read_json_object(PROFILE_CATALOG),
    )
    assert_register(summary)
    assert_public_markers(summary)
    assert_state(summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate patch catalog accounting.")
    args = parser.parse_args()
    if not args.check:
        parser.error("--check is required")

    try:
        summary = check()
    except (AccountingError, json.JSONDecodeError) as exc:
        print(f"WinUI patch catalog accounting check: FAIL: {exc}")
        return 1

    print(
        json.dumps(
            {
                "status": "PASS",
                "totalRows": summary["total"],
                "visibleRows": summary["visible"],
                "hiddenRows": summary["hidden"],
                "dependencyEdges": summary["dependencyEdges"],
                "conflictEdges": summary["conflictEdges"],
                "visibleTracks": summary["visibleTracks"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
