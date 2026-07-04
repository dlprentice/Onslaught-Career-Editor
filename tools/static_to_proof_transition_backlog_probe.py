#!/usr/bin/env python3
"""Validate the static-to-proof transition backlog and closeout boundaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKLOG = ROOT / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
PROOF_PLAN = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-asset-bridge-proof-plan.md"
PHYSICS_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-schema-parser-proof-plan.md"
PHYSICS_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "physics-script-copied-corpus-parser-proof.md"
DESTROYABLE_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "destroyable-segments-damage-break-proof-plan.md"
HUD_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "hud-frontend-overlay-visual-runtime-proof-plan.md"
UNIT_TARGETING_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "unit-targeting-active-reader-proof-plan.md"
WEAPON_PROJECTILE_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "weapon-projectile-spawn-handoff-proof-plan.md"
SAVE_OPTIONS_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "save-options-controller-byte-preservation-proof-plan.md"
AUDIO_MEDIA_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "audio-media-cutscene-camera-proof-plan.md"
ENGINE_PLATFORM_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "engine-platform-math-memory-support-proof-plan.md"
FRONTEND_INPUT_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "frontend-input-game-loop-proof-plan.md"
MISSIONSCRIPT_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-proof-plan.md"
MISSIONSCRIPT_CONTRACT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
WORLD_THING_SPAWN_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-object-reference-proof-plan.md"
WORLD_THING_SPAWN_SCHEMA_PLAN = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-copied-corpus-schema-proof-plan.md"
WORLD_THING_SPAWN_SCHEMA_RESULT = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-copied-corpus-schema-proof.md"
WORLD_THING_SPAWN_HANDOFF = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-spawner-handoff-static-proof.md"
WORLD_THING_SPAWN_HANDOFF_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-spawner-handoff-static.v1.json"
WORLD_THING_SPAWN_GETTHINGREF = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-getthingref-object-reference-static-proof.md"
WORLD_THING_SPAWN_GETTHINGREF_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-getthingref-object-reference-static.v1.json"
MISSIONSCRIPT_CUTSCENE_CAMERA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-cutscene-pan-camera-position-command-effect-static-proof.md"
MISSIONSCRIPT_CUTSCENE_CAMERA_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-cutscene-pan-camera-position-command-effect.v1.json"
MISSIONSCRIPT_VECTOR_RANGE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-vector-range-command-effect-static-proof.md"
MISSIONSCRIPT_VECTOR_RANGE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-vector-range-command-effect.v1.json"
MISSIONSCRIPT_THING_VALUE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-thing-value-engine-helper-command-effect-static-proof.md"
MISSIONSCRIPT_THING_VALUE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-thing-value-engine-helper-command-effect.v1.json"
MISSIONSCRIPT_HUD_DISPLAY = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-hud-display-command-effect-static-proof.md"
MISSIONSCRIPT_HUD_DISPLAY_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-hud-display-command-effect.v1.json"
MISSIONSCRIPT_PLAYER_STATE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-player-state-score-command-effect-static-proof.md"
MISSIONSCRIPT_PLAYER_STATE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-player-state-score-command-effect.v1.json"
MISSIONSCRIPT_PACKED_LOOSE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-packed-vs-loose-script-selection-proof-plan.md"
MISSIONSCRIPT_PACKED_LOOSE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-packed-vs-loose-script-selection.v1.json"
MISSIONSCRIPT_LEVEL100 = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-static-walkthrough-proof-plan.md"
MISSIONSCRIPT_LEVEL100_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-static-walkthrough.v1.json"
MISSIONSCRIPT_LEVEL100_TEXT_SPEAKER = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-text-speaker-resolution-proof-plan.md"
MISSIONSCRIPT_LEVEL100_TEXT_SPEAKER_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-text-speaker-resolution.v1.json"
MISSIONSCRIPT_LEVEL100_RUNTIME_BOUNDARY = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-runtime-harness-boundary-proof-plan.md"
MISSIONSCRIPT_LEVEL100_RUNTIME_BOUNDARY_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-runtime-harness-boundary.v1.json"
MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_BOUNDARY = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-boundary-proof-plan.md"
MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_BOUNDARY_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-boundary.v1.json"
MISSIONSCRIPT_LEVEL100_ARTIFACT_MANIFEST = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest-proof-plan.md"
MISSIONSCRIPT_LEVEL100_ARTIFACT_MANIFEST_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest.v1.json"
MISSIONSCRIPT_LEVEL100_TEMPLATE_GENERATION = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-template-generation-proof-plan.md"
MISSIONSCRIPT_LEVEL100_TEMPLATE_GENERATION_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-templates.v1.json"
MISSIONSCRIPT_LEVEL100_DRY_RUN = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-dry-run-validation-proof-plan.md"
MISSIONSCRIPT_LEVEL100_DRY_RUN_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-dry-run-validation.v1.json"
MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_PREPARATION = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation-proof-plan.md"
MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_PREPARATION_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation.v1.json"
MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_MATERIALIZATION_PREFLIGHT = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight-proof.md"
MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_MATERIALIZATION_PREFLIGHT_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight.v1.json"
MISSIONSCRIPT_LEVEL100_CLEAN_SOURCE_SPECIMEN_RESOLUTION = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-clean-source-specimen-resolution-proof-plan.md"
MISSIONSCRIPT_LEVEL100_CLEAN_SOURCE_SPECIMEN_RESOLUTION_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-clean-source-specimen-resolution.v1.json"
MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_MATERIALIZATION = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-proof.md"
MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_MATERIALIZATION_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization.v1.json"
MISSIONSCRIPT_LEVEL100_COPIED_EXECUTABLE_PATCH = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch-proof.md"
MISSIONSCRIPT_LEVEL100_COPIED_EXECUTABLE_PATCH_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch.v1.json"
MISSIONSCRIPT_LEVEL100_LAUNCH_COMMAND = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command-proof-plan.md"
MISSIONSCRIPT_LEVEL100_LAUNCH_COMMAND_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command.v1.json"
MISSIONSCRIPT_LEVEL100_LAUNCH_WINDOW_SMOKE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke-proof.md"
MISSIONSCRIPT_LEVEL100_LAUNCH_WINDOW_SMOKE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke.v1.json"
MISSIONSCRIPT_LEVEL100_SCREENSHOT_CAPTURE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture-proof.md"
MISSIONSCRIPT_LEVEL100_SCREENSHOT_CAPTURE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture.v1.json"
MISSIONSCRIPT_LEVEL100_DIRECT_LAUNCH_WINDOW_SMOKE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke-proof.md"
MISSIONSCRIPT_LEVEL100_DIRECT_LAUNCH_WINDOW_SMOKE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke.v1.json"
MISSIONSCRIPT_LEVEL100_DIRECT_SCREENSHOT_CAPTURE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture-proof.md"
MISSIONSCRIPT_LEVEL100_DIRECT_SCREENSHOT_CAPTURE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture.v1.json"
MISSIONSCRIPT_LEVEL100_DIRECT_VISUAL_FRAME_TRIAGE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage-proof.md"
MISSIONSCRIPT_LEVEL100_DIRECT_VISUAL_FRAME_TRIAGE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage.v1.json"
MISSIONSCRIPT_LEVEL100_DIRECT_TEXT_OVERLAY_CORRELATION = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-text-overlay-correlation-proof.md"
MISSIONSCRIPT_LEVEL100_DIRECT_TEXT_OVERLAY_CORRELATION_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-text-overlay-correlation.v1.json"
MISSIONSCRIPT_LEVEL100_DIRECT_TIMED_FRAME_SET_CAPTURE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-capture-proof.md"
MISSIONSCRIPT_LEVEL100_DIRECT_TIMED_FRAME_SET_CAPTURE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-capture.v1.json"
MISSIONSCRIPT_LEVEL100_DIRECT_TIMED_FRAME_SET_TEXT_OVERLAY_PROGRESSION_CORRELATION = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-text-overlay-progression-correlation-proof.md"
MISSIONSCRIPT_LEVEL100_DIRECT_TIMED_FRAME_SET_TEXT_OVERLAY_PROGRESSION_CORRELATION_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-text-overlay-progression-correlation.v1.json"
MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_BOUNDARY = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-boundary-proof-plan.md"
MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_BOUNDARY_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-boundary.v1.json"
MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_TEMPLATE = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-template-proof-plan.md"
MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_TEMPLATE_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-template.v1.json"
MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_DRY_RUN = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-checklist-dry-run-validation.md"
MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_DRY_RUN_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-checklist-dry-run-validation.v1.json"
MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_ARM_BOUNDARY = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-private-frame-arm-boundary.md"
MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_ARM_BOUNDARY_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-private-frame-arm-boundary.v1.json"
MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_POPULATION = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-private-frame-checklist-population.md"
MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_POPULATION_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-private-frame-checklist-population.v1.json"
MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_PUBLIC_SAFE_SUMMARY = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-public-safe-result-summary.md"
MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_PUBLIC_SAFE_SUMMARY_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "level100-message-public-safe-result-summary.v1.json"
STATIC_TO_PROOF_NEXT_SAFE_SELECTION = ROOT / "reverse-engineering" / "binary-analysis" / "static-to-proof-next-safe-slice-selection.md"
STATIC_TO_PROOF_NEXT_SAFE_SELECTION_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "static-to-proof-next-safe-slice-selection.v1.json"
WORLD_THING_SPAWN_CROSSWALK = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-static-to-rebuild-contract-crosswalk.md"
WORLD_THING_SPAWN_CROSSWALK_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-static-to-rebuild-contract-crosswalk.v1.json"
MISSIONSCRIPT_COMMAND_EFFECT_ROLLUP = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-rebuild-interface-rollup.md"
MISSIONSCRIPT_COMMAND_EFFECT_ROLLUP_SCHEMA = ROOT / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-rebuild-interface-rollup.v1.json"
MAPPED = ROOT / "reverse-engineering" / "binary-analysis" / "mapped-systems.md"
MEASURE = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-measurement-register.md"
PROGRESS = ROOT / "reverse-engineering" / "binary-analysis" / "static-reaudit-progress.json"
RE_INDEX = ROOT / "reverse-engineering" / "RE-INDEX.md"
BIN_INDEX = ROOT / "reverse-engineering" / "binary-analysis" / "_index.md"
GAME_ASSETS_INDEX = ROOT / "reverse-engineering" / "game-assets" / "_index.md"
STRATEGY = ROOT / "roadmap" / "three-lane-product-strategy.md"
LORE_BACKLOG = ROOT / "lore-book" / "roadmap" / "static-to-proof-rebuild-transition-backlog.md"
LORE_PROOF_PLAN = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-asset-bridge-proof-plan.md"
LORE_PHYSICS_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-schema-parser-proof-plan.md"
LORE_PHYSICS_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "physics-script-copied-corpus-parser-proof.md"
LORE_DESTROYABLE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "destroyable-segments-damage-break-proof-plan.md"
LORE_HUD_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "hud-frontend-overlay-visual-runtime-proof-plan.md"
LORE_UNIT_TARGETING_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "unit-targeting-active-reader-proof-plan.md"
LORE_WEAPON_PROJECTILE_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "weapon-projectile-spawn-handoff-proof-plan.md"
LORE_SAVE_OPTIONS_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "save-options-controller-byte-preservation-proof-plan.md"
LORE_AUDIO_MEDIA_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "audio-media-cutscene-camera-proof-plan.md"
LORE_ENGINE_PLATFORM_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "engine-platform-math-memory-support-proof-plan.md"
LORE_FRONTEND_INPUT_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "frontend-input-game-loop-proof-plan.md"
LORE_MISSIONSCRIPT_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-proof-plan.md"
LORE_MISSIONSCRIPT_CONTRACT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-iscript-static-contract.md"
LORE_WORLD_THING_SPAWN_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-object-reference-proof-plan.md"
LORE_WORLD_THING_SPAWN_SCHEMA_PLAN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-copied-corpus-schema-proof-plan.md"
LORE_WORLD_THING_SPAWN_SCHEMA_RESULT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-copied-corpus-schema-proof.md"
LORE_WORLD_THING_SPAWN_HANDOFF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-spawner-handoff-static-proof.md"
LORE_WORLD_THING_SPAWN_HANDOFF_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-spawner-handoff-static.v1.json"
LORE_WORLD_THING_SPAWN_GETTHINGREF = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-getthingref-object-reference-static-proof.md"
LORE_WORLD_THING_SPAWN_GETTHINGREF_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-getthingref-object-reference-static.v1.json"
LORE_MISSIONSCRIPT_CUTSCENE_CAMERA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-cutscene-pan-camera-position-command-effect-static-proof.md"
LORE_MISSIONSCRIPT_CUTSCENE_CAMERA_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-cutscene-pan-camera-position-command-effect.v1.json"
LORE_MISSIONSCRIPT_VECTOR_RANGE = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-vector-range-command-effect-static-proof.md"
LORE_MISSIONSCRIPT_VECTOR_RANGE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-vector-range-command-effect.v1.json"
LORE_MISSIONSCRIPT_THING_VALUE = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-thing-value-engine-helper-command-effect-static-proof.md"
LORE_MISSIONSCRIPT_THING_VALUE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-thing-value-engine-helper-command-effect.v1.json"
LORE_MISSIONSCRIPT_HUD_DISPLAY = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-hud-display-command-effect-static-proof.md"
LORE_MISSIONSCRIPT_HUD_DISPLAY_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-hud-display-command-effect.v1.json"
LORE_MISSIONSCRIPT_PLAYER_STATE = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-player-state-score-command-effect-static-proof.md"
LORE_MISSIONSCRIPT_PLAYER_STATE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-player-state-score-command-effect.v1.json"
LORE_MISSIONSCRIPT_PACKED_LOOSE = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-packed-vs-loose-script-selection-proof-plan.md"
LORE_MISSIONSCRIPT_PACKED_LOOSE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-packed-vs-loose-script-selection.v1.json"
LORE_MISSIONSCRIPT_LEVEL100 = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-static-walkthrough-proof-plan.md"
LORE_MISSIONSCRIPT_LEVEL100_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-static-walkthrough.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_TEXT_SPEAKER = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-text-speaker-resolution-proof-plan.md"
LORE_MISSIONSCRIPT_LEVEL100_TEXT_SPEAKER_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-text-speaker-resolution.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_RUNTIME_BOUNDARY = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-runtime-harness-boundary-proof-plan.md"
LORE_MISSIONSCRIPT_LEVEL100_RUNTIME_BOUNDARY_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-runtime-harness-boundary.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_BOUNDARY = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-boundary-proof-plan.md"
LORE_MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_BOUNDARY_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-boundary.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_ARTIFACT_MANIFEST = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest-proof-plan.md"
LORE_MISSIONSCRIPT_LEVEL100_ARTIFACT_MANIFEST_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_TEMPLATE_GENERATION = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-template-generation-proof-plan.md"
LORE_MISSIONSCRIPT_LEVEL100_TEMPLATE_GENERATION_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-templates.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_DRY_RUN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-dry-run-validation-proof-plan.md"
LORE_MISSIONSCRIPT_LEVEL100_DRY_RUN_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-dry-run-validation.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_PREPARATION = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation-proof-plan.md"
LORE_MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_PREPARATION_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_MATERIALIZATION_PREFLIGHT = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight-proof.md"
LORE_MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_MATERIALIZATION_PREFLIGHT_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_CLEAN_SOURCE_SPECIMEN_RESOLUTION = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-clean-source-specimen-resolution-proof-plan.md"
LORE_MISSIONSCRIPT_LEVEL100_CLEAN_SOURCE_SPECIMEN_RESOLUTION_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-clean-source-specimen-resolution.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_MATERIALIZATION = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-proof.md"
LORE_MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_MATERIALIZATION_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_COPIED_EXECUTABLE_PATCH = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch-proof.md"
LORE_MISSIONSCRIPT_LEVEL100_COPIED_EXECUTABLE_PATCH_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_LAUNCH_COMMAND = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command-proof-plan.md"
LORE_MISSIONSCRIPT_LEVEL100_LAUNCH_COMMAND_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_LAUNCH_WINDOW_SMOKE = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke-proof.md"
LORE_MISSIONSCRIPT_LEVEL100_LAUNCH_WINDOW_SMOKE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_SCREENSHOT_CAPTURE = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture-proof.md"
LORE_MISSIONSCRIPT_LEVEL100_SCREENSHOT_CAPTURE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_LAUNCH_WINDOW_SMOKE = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke-proof.md"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_LAUNCH_WINDOW_SMOKE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_SCREENSHOT_CAPTURE = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture-proof.md"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_SCREENSHOT_CAPTURE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_VISUAL_FRAME_TRIAGE = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage-proof.md"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_VISUAL_FRAME_TRIAGE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_TEXT_OVERLAY_CORRELATION = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-text-overlay-correlation-proof.md"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_TEXT_OVERLAY_CORRELATION_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-text-overlay-correlation.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_TIMED_FRAME_SET_CAPTURE = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-capture-proof.md"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_TIMED_FRAME_SET_CAPTURE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-capture.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_TIMED_FRAME_SET_TEXT_OVERLAY_PROGRESSION_CORRELATION = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-text-overlay-progression-correlation-proof.md"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_TIMED_FRAME_SET_TEXT_OVERLAY_PROGRESSION_CORRELATION_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-text-overlay-progression-correlation.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_BOUNDARY = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-boundary-proof-plan.md"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_BOUNDARY_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-boundary.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_TEMPLATE = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-template-proof-plan.md"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_TEMPLATE_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-template.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_DRY_RUN = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "level100-message-checklist-dry-run-validation.md"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_DRY_RUN_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "level100-message-checklist-dry-run-validation.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_ARM_BOUNDARY = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "level100-message-private-frame-arm-boundary.md"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_ARM_BOUNDARY_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "level100-message-private-frame-arm-boundary.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_POPULATION = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "level100-message-private-frame-checklist-population.md"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_POPULATION_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "level100-message-private-frame-checklist-population.v1.json"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_PUBLIC_SAFE_SUMMARY = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "level100-message-public-safe-result-summary.md"
LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_PUBLIC_SAFE_SUMMARY_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "level100-message-public-safe-result-summary.v1.json"
LORE_STATIC_TO_PROOF_NEXT_SAFE_SELECTION = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-to-proof-next-safe-slice-selection.md"
LORE_STATIC_TO_PROOF_NEXT_SAFE_SELECTION_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "static-to-proof-next-safe-slice-selection.v1.json"
LORE_WORLD_THING_SPAWN_CROSSWALK = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-static-to-rebuild-contract-crosswalk.md"
LORE_WORLD_THING_SPAWN_CROSSWALK_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "world-thing-spawn-static-to-rebuild-contract-crosswalk.v1.json"
LORE_MISSIONSCRIPT_COMMAND_EFFECT_ROLLUP = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-rebuild-interface-rollup.md"
LORE_MISSIONSCRIPT_COMMAND_EFFECT_ROLLUP_SCHEMA = ROOT / "lore-book" / "reverse-engineering" / "binary-analysis" / "missionscript-command-effect-rebuild-interface-rollup.v1.json"
COPIED_CORPUS_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-asset-bridge-copied-corpus-proof.md"
LORE_COPIED_CORPUS_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-asset-bridge-copied-corpus-proof.md"
MATERIAL_LEDGER_RESULT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-ledger-proof.md"
LORE_MATERIAL_LEDGER_RESULT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-ledger-proof.md"
MATERIAL_CONTRACT_EXTENSION = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.md"
LORE_MATERIAL_CONTRACT_EXTENSION = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.md"
MATERIAL_FIXTURE_MATRIX = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-rebuild-fixture-matrix-proof.md"
LORE_MATERIAL_FIXTURE_MATRIX = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-rebuild-fixture-matrix-proof.md"
MATERIAL_IMPORTER_HARNESS = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.md"
LORE_MATERIAL_IMPORTER_HARNESS = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.md"
MATERIAL_IMPORTER_MATERIALIZATION = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan.md"
LORE_MATERIAL_IMPORTER_MATERIALIZATION = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan.md"
MATERIAL_IMPORTER_CONSUMER_DRY_RUN = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan.md"
LORE_MATERIAL_IMPORTER_CONSUMER_DRY_RUN = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan.md"
MATERIAL_IMPORTER_READINESS_GATE = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan.md"
LORE_MATERIAL_IMPORTER_READINESS_GATE = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan.md"
MATERIAL_IMPORTER_PUBLIC_CONTRACT_SKELETON = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan.md"
LORE_MATERIAL_IMPORTER_PUBLIC_CONTRACT_SKELETON = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan.md"
MATERIAL_IMPORTER_PRIVATE_BOUNDARY = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan.md"
LORE_MATERIAL_IMPORTER_PRIVATE_BOUNDARY = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan.md"
MATERIAL_IMPORTER_PRIVATE_CHECKLIST = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-proof-plan.md"
LORE_MATERIAL_IMPORTER_PRIVATE_CHECKLIST = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-proof-plan.md"
MATERIAL_IMPORTER_PRIVATE_READONLY_PREFLIGHT = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-proof-plan.md"
LORE_MATERIAL_IMPORTER_PRIVATE_READONLY_PREFLIGHT = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-proof-plan.md"
MATERIAL_IMPORTER_PRIVATE_MANIFEST_DRY_RUN = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run-proof-plan.md"
LORE_MATERIAL_IMPORTER_PRIVATE_MANIFEST_DRY_RUN = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run-proof-plan.md"
MATERIAL_IMPORTER_PRIVATE_MANIFEST_MATERIALIZATION = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-proof-plan.md"
LORE_MATERIAL_IMPORTER_PRIVATE_MANIFEST_MATERIALIZATION = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-proof-plan.md"
MATERIAL_IMPORTER_PRIVATE_MANIFEST_CONSUMER_VALIDATION = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-consumer-validation-proof-plan.md"
LORE_MATERIAL_IMPORTER_PRIVATE_MANIFEST_CONSUMER_VALIDATION = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-consumer-validation-proof-plan.md"
MATERIAL_IMPORTER_PRIVATE_MANIFEST_ADAPTER_DRY_RUN = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-dry-run-proof-plan.md"
LORE_MATERIAL_IMPORTER_PRIVATE_MANIFEST_ADAPTER_DRY_RUN = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-dry-run-proof-plan.md"
MATERIAL_IMPORTER_PRIVATE_MANIFEST_ADAPTER_CONSUMER_READINESS = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-readiness-gate-proof-plan.md"
LORE_MATERIAL_IMPORTER_PRIVATE_MANIFEST_ADAPTER_CONSUMER_READINESS = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-readiness-gate-proof-plan.md"
MATERIAL_IMPORTER_PRIVATE_MANIFEST_ADAPTER_CONSUMER_DRY_RUN = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-dry-run-proof-plan.md"
LORE_MATERIAL_IMPORTER_PRIVATE_MANIFEST_ADAPTER_CONSUMER_DRY_RUN = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-dry-run-proof-plan.md"
MATERIAL_IMPORTER_PRIVATE_REAL_IMPORTER_READINESS = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-readiness-gate-proof-plan.md"
LORE_MATERIAL_IMPORTER_PRIVATE_REAL_IMPORTER_READINESS = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-readiness-gate-proof-plan.md"
MATERIAL_IMPORTER_PRIVATE_REAL_IMPORTER_HARNESS_BOUNDARY = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan.md"
LORE_MATERIAL_IMPORTER_PRIVATE_REAL_IMPORTER_HARNESS_BOUNDARY = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan.md"
MATERIAL_IMPORTER_PRIVATE_REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-proof-plan.md"
LORE_MATERIAL_IMPORTER_PRIVATE_REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-proof-plan.md"
MATERIAL_IMPORTER_PRIVATE_REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION = ROOT / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-validation-proof-plan.md"
LORE_MATERIAL_IMPORTER_PRIVATE_REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION = ROOT / "lore-book" / "reverse-engineering" / "game-assets" / "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-validation-proof-plan.md"

REQUIRED_TOKENS = (
    "Static-To-Proof Rebuild Transition Backlog",
    "6411/6411 = 100.00%",
    "0 / 0 / 0",
    "1560/1560 = 100.00%",
    "1179/1179 = 100.00%",
    "remaining active focused work",
    "Active Proof Slice",
    "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Checklist Readiness Gate Proof Plan",
    "selected after the Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Checklist Validation Proof Plan completed",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Checklist Validation Proof Plan",
    "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-validation-proof.md",
    "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-validation-proof.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-complete-public-safe-not-run-checklist-rows-validated-no-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Checklist Readiness Gate Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan",
    "sourceCommandArmChecklistPopulationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-complete-public-safe-not-run-checklist-populated-no-command-arming",
    "sourceProofCount=66",
    "sourceCommandArmChecklistPopulationProofCount=65",
    "sourceCommandArmChecklistPopulationInterfaceCount=12",
    "commandArmChecklistValidationInterfaceCount=16",
    "commandArmChecklistRowsConsumed=99",
    "commandArmChecklistValidationRows=99",
    "passedCommandArmChecklistValidationRowCount=99",
    "failedCommandArmChecklistValidationRowCount=0",
    "validatedNotRunCommandArmChecklistRowCount=99",
    "validatedUnobservedCommandArmChecklistRowCount=99",
    "validatedNotArmedCommandArmChecklistRowCount=99",
    "validatedNotExecutedCommandArmChecklistRowCount=99",
    "readyForLaterCommandArmChecklistReadinessGateRowCount=99",
    "publicSafeCommandArmChecklistValidationArtifactRows=1",
    "falseGuardCount=317",
    "zeroCounterCount=258",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Checklist Population Proof Plan",
    "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-population-proof.md",
    "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-population-proof.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-complete-public-safe-not-run-checklist-populated-no-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Checklist Validation Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-proof-plan",
    "sourceCommandArmBoundaryStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-boundary-defined-public-safe-no-command-arming",
    "sourceProofCount=65",
    "sourceCommandArmBoundaryProofCount=64",
    "sourceCommandArmBoundaryInterfaceCount=10",
    "commandArmBoundaryRowsConsumed=99",
    "commandArmChecklistPopulationRows=99",
    "populatedCommandArmChecklistRowCount=99",
    "passedCommandArmChecklistPopulationRowCount=99",
    "failedCommandArmChecklistPopulationRowCount=0",
    "notRunCommandArmChecklistRowCount=99",
    "unobservedCommandArmChecklistRowCount=99",
    "readyForLaterCommandArmChecklistValidationRowCount=99",
    "publicSafeCommandArmChecklistPopulationArtifactRows=1",
    "publicAllowedOutputCount=122",
    "redactedFieldCount=56",
    "falseGuardCount=313",
    "zeroCounterCount=257",
    "commandArmChecklistValidationLaneSelected=true",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Boundary Proof Plan",
    "texture-mesh-material-sidecar-command-arm-checklist-command-arm-boundary-proof.md",
    "texture-mesh-material-sidecar-command-arm-checklist-command-arm-boundary-proof.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmBoundaryStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-boundary-defined-public-safe-no-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Checklist Population Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-proof-plan",
    "sourceCommandArmReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-complete-public-safe-readiness-only-not-command-arming",
    "sourceProofCount=64",
    "sourceCommandArmReadinessGateProofCount=63",
    "sourceCommandArmReadinessGateInterfaceCount=10",
    "commandArmBoundaryInterfaceCount=10",
    "commandArmReadinessGateRowsConsumed=99",
    "commandArmBoundaryRows=99",
    "definedCommandArmBoundaryRowCount=99",
    "passedCommandArmBoundaryRowCount=99",
    "failedCommandArmBoundaryRowCount=0",
    "armedCommandRowCount=0",
    "executedCommandRowCount=0",
    "shellDispatchedCommandRowCount=0",
    "readyForLaterCommandArmChecklistPopulationRowCount=99",
    "publicSafeCommandArmBoundaryArtifactRows=1",
    "publicAllowedOutputCount=122",
    "redactedFieldCount=56",
    "stopConditionCount=12",
    "falseGuardCount=308",
    "zeroCounterCount=250",
    "commandArmChecklistPopulationLaneSelected=true",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Readiness Gate Proof Plan",
    "texture-mesh-material-sidecar-command-arm-checklist-command-arm-readiness-gate-proof.md",
    "texture-mesh-material-sidecar-command-arm-checklist-command-arm-readiness-gate-proof.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-complete-public-safe-readiness-only-not-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Boundary Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-boundary-proof-plan",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-complete-public-safe-non-dispatched-command-dry-run-consumed-not-real-importer-execution",
    "sourceProofCount=63",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationProofCount=62",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInterfaceCount=10",
    "commandArmReadinessGateInterfaceCount=10",
    "commandDryRunConsumerValidationRowsConsumed=99",
    "commandArmReadinessGateRows=99",
    "passedCommandArmReadinessGateRowCount=99",
    "failedCommandArmReadinessGateRowCount=0",
    "readyForLaterCommandArmBoundaryRowCount=99",
    "publicSafeCommandArmReadinessGateArtifactRows=1",
    "publicAllowedOutputCount=119",
    "redactedFieldCount=55",
    "falseGuardCount=305",
    "zeroCounterCount=248",
    "commandArmBoundaryLaneSelected=true",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Dry-Run Consumer Validation Proof Plan",
    "texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-consumer-validation-proof.md",
    "texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-consumer-validation-proof.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-complete-public-safe-non-dispatched-command-dry-run-consumed-not-real-importer-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Readiness Gate Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-proof-plan",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-complete-public-safe-readiness-row-consumption-not-real-importer-execution",
    "sourceProofCount=62",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunProofCount=61",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunInterfaceCount=10",
    "commandDryRunConsumerValidationInterfaceCount=10",
    "commandDryRunRowsConsumed=99",
    "commandDryRunConsumerValidationRows=99",
    "validatedNonDispatchedCommandDryRunRowCount=99",
    "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowCount=99",
    "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactRows=1",
    "publicAllowedOutputCount=116",
    "redactedFieldCount=54",
    "falseGuardCount=297",
    "zeroCounterCount=242",
    "commandArmReadinessGateLaneSelected=true",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Dry-Run Proof Plan",
    "texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-proof.md",
    "texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-proof.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-complete-public-safe-readiness-row-consumption-not-real-importer-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Dry-Run Consumer Validation Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-proof-plan",
    "sourceProofCount=61",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateProofCount=60",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateInterfaceCount=10",
    "commandDryRunInterfaceCount=10",
    "commandReadinessGateRowsConsumed=99",
    "commandDryRunRows=99",
    "passedCommandDryRunRowCount=99",
    "failedCommandDryRunRowCount=0",
    "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRowCount=99",
    "publicAllowedOutputCount=113",
    "redactedFieldCount=53",
    "falseGuardCount=292",
    "zeroCounterCount=238",
    "commandDryRunConsumerValidationLaneSelected=true",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Readiness Gate Proof Plan",
    "texture-mesh-material-sidecar-command-arm-checklist-command-readiness-gate-proof.md",
    "texture-mesh-material-sidecar-command-arm-checklist-command-readiness-gate-proof.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-readiness-gate-complete-public-safe-readiness-only-not-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Dry-Run Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-proof-plan",
    "sourceProofCount=60",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationProofCount=59",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationInterfaceCount=12",
    "commandReadinessGateInterfaceCount=10",
    "commandReadinessGateRows=99",
    "passedCommandReadinessGateRowCount=99",
    "failedCommandReadinessGateRowCount=0",
    "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunRowCount=99",
    "publicAllowedOutputCount=109",
    "redactedFieldCount=50",
    "falseGuardCount=286",
    "zeroCounterCount=235",
    "commandDryRunLaneSelected=true",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Consumer Validation Proof Plan",
    "texture-mesh-material-sidecar-command-arm-checklist-command-consumer-validation-proof.md",
    "texture-mesh-material-sidecar-command-arm-checklist-command-consumer-validation-proof.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-consumer-validation-complete-public-safe-non-armed-command-contract-consumed-not-real-importer-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Readiness Gate Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-readiness-gate-proof-plan",
    "sourceProofCount=59",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationProofCount=58",
    "commandConsumerValidationRows=99",
    "validatedNonArmedCommandContractRowCount=99",
    "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateRowCount=99",
    "publicAllowedOutputCount=106",
    "redactedFieldCount=49",
    "falseGuardCount=278",
    "zeroCounterCount=230",
    "commandReadinessGateLaneSelected=true",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Materialization Proof Plan",
    "texture-mesh-material-sidecar-command-arm-checklist-command-materialization-proof.md",
    "texture-mesh-material-sidecar-command-arm-checklist-command-materialization-proof.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-materialization-complete-public-safe-non-armed-command-contract-not-command-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Consumer Validation Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-consumer-validation-proof-plan",
    "sourceProofCount=58",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryProofCount=57",
    "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandContractRows=99",
    "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationRowCount=99",
    "publicAllowedOutputCount=103",
    "redactedFieldCount=48",
    "falseGuardCount=273",
    "zeroCounterCount=226",
    "commandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationLaneSelected=true",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Boundary Proof Plan",
    "texture-mesh-material-sidecar-command-arm-checklist-boundary-proof.md",
    "texture-mesh-material-sidecar-command-arm-checklist-boundary-proof.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-boundary-defined-public-safe-no-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Materialization Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-materialization-proof-plan",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-readiness-gate-complete-public-safe-readiness-only-not-command-arming",
    "sourceProofCount=57",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateProofCount=56",
    "commandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRows=99",
    "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount=99",
    "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount=0",
    "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandMaterializationRowCount=99",
    "publicAllowedOutputCount=100",
    "redactedFieldCount=47",
    "falseGuardCount=266",
    "zeroCounterCount=220",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Readiness Gate Proof Plan",
    "texture-mesh-material-sidecar-command-arm-checklist-readiness-gate-proof.md",
    "texture-mesh-material-sidecar-command-arm-checklist-readiness-gate-proof.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-readiness-gate-complete-public-safe-readiness-only-not-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Boundary Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-boundary-proof-plan",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-complete-public-safe-not-run-checklist-rows-validated-no-command-arming",
    "sourceProofCount=56",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationProofCount=55",
    "commandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRows=99",
    "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowCount=99",
    "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowCount=0",
    "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistBoundaryRowCount=99",
    "publicAllowedOutputCount=97",
    "redactedFieldCount=46",
    "falseGuardCount=262",
    "zeroCounterCount=215",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Validation Proof Plan",
    "texture-mesh-material-sidecar-command-arm-checklist-validation-proof.md",
    "texture-mesh-material-sidecar-command-arm-checklist-validation-proof.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-complete-public-safe-not-run-checklist-rows-validated-no-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Readiness Gate Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-complete-public-safe-not-run-checklist-populated-no-command-arming",
    "sourceProofCount=55",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationProofCount=54",
    "commandArmChecklistCommandArmChecklistCommandArmChecklistRowsConsumed=99",
    "commandArmChecklistCommandArmChecklistCommandArmChecklistValidationRows=99",
    "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowCount=99",
    "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowCount=0",
    "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistReadinessGateRowCount=99",
    "publicAllowedOutputCount=94",
    "redactedFieldCount=45",
    "falseGuardCount=256",
    "zeroCounterCount=214",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Population Proof Plan",
    "texture-mesh-material-sidecar-command-arm-checklist-population-proof.md",
    "texture-mesh-material-sidecar-command-arm-checklist-population-proof.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-complete-public-safe-not-run-checklist-populated-no-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Validation Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-proof-plan",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-boundary-defined-public-safe-no-command-arming",
    "sourceProofCount=54",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmBoundaryProofCount=53",
    "commandArmChecklistCommandArmChecklistCommandArmBoundaryRowsConsumed=99",
    "commandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRows=99",
    "passedCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowCount=99",
    "failedCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowCount=0",
    "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistValidationRowCount=99",
    "publicAllowedOutputCount=91",
    "redactedFieldCount=44",
    "falseGuardCount=250",
    "zeroCounterCount=207",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Boundary Proof Plan",
    "texture-mesh-material-sidecar-command-arm-boundary-proof.md",
    "texture-mesh-material-sidecar-command-arm-boundary-proof.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmBoundaryStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-boundary-defined-public-safe-no-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Population Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-proof-plan",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-complete-public-safe-readiness-only-not-command-arming",
    "sourceProofCount=53",
    "sourceCommandArmChecklistCommandArmChecklistCommandArmReadinessGateProofCount=52",
    "commandArmChecklistCommandArmChecklistCommandArmReadinessGateRowsConsumed=99",
    "commandArmChecklistCommandArmChecklistCommandArmBoundaryRows=99",
    "passedCommandArmChecklistCommandArmChecklistCommandArmBoundaryRowCount=99",
    "failedCommandArmChecklistCommandArmChecklistCommandArmBoundaryRowCount=0",
    "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationRowCount=99",
    "publicAllowedOutputCount=88",
    "redactedFieldCount=43",
    "falseGuardCount=247",
    "zeroCounterCount=206",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Readiness Gate Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-complete-public-safe-readiness-only-not-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Boundary Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-command-arm-boundary-proof",
    "sourceCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-complete-public-safe-non-dispatched-command-arm-checklist-command-arm-checklist-command-dry-run-consumed-not-real-importer-execution",
    "sourceProofCount=52",
    "sourceCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationProofCount=51",
    "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRowsConsumed=99",
    "commandArmChecklistCommandArmChecklistCommandArmReadinessGateRows=99",
    "passedCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowCount=99",
    "failedCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowCount=0",
    "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmBoundaryRowCount=99",
    "publicAllowedOutputCount=85",
    "redactedFieldCount=42",
    "falseGuardCount=243",
    "zeroCounterCount=201",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Dry-Run Consumer Validation Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-complete-public-safe-non-dispatched-command-arm-checklist-command-arm-checklist-command-dry-run-consumed-not-real-importer-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Readiness Gate Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-proof-plan",
    "sourceCommandArmChecklistCommandArmChecklistCommandDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-dry-run-complete-public-safe-readiness-row-consumption-not-real-importer-execution",
    "sourceProofCount=51",
    "sourceCommandArmChecklistCommandArmChecklistCommandDryRunProofCount=50",
    "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInterfaceCount=10",
    "commandArmChecklistCommandArmChecklistCommandDryRunRowsConsumed=99",
    "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRows=99",
    "validatedNonDispatchedCommandArmChecklistCommandArmChecklistCommandDryRunRowCount=99",
    "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowCount=99",
    "publicSafeCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactRows=1",
    "publicAllowedOutputCount=82",
    "redactedFieldCount=41",
    "falseGuardCount=238",
    "zeroCounterCount=195",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Dry-Run Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-dry-run-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-dry-run-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-dry-run-complete-public-safe-readiness-row-consumption-not-real-importer-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Dry-Run Consumer Validation Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-proof-plan",
    "sourceCommandArmChecklistCommandArmChecklistCommandReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-readiness-gate-complete-public-safe-readiness-only-not-command-execution",
    "sourceProofCount=50",
    "sourceCommandArmChecklistCommandArmChecklistCommandReadinessGateProofCount=49",
    "sourceCommandArmChecklistCommandArmChecklistCommandReadinessGateInterfaceCount=10",
    "commandArmChecklistCommandArmChecklistCommandDryRunInterfaceCount=10",
    "commandArmChecklistCommandArmChecklistCommandReadinessGateRowsConsumed=99",
    "commandArmChecklistCommandArmChecklistCommandDryRunRows=99",
    "passedCommandArmChecklistCommandArmChecklistCommandDryRunRowCount=99",
    "failedCommandArmChecklistCommandArmChecklistCommandDryRunRowCount=0",
    "readyForLaterCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRowCount=99",
    "publicSafeCommandArmChecklistCommandArmChecklistCommandDryRunArtifactRows=1",
    "publicAllowedOutputCount=79",
    "redactedFieldCount=40",
    "falseGuardCount=233",
    "zeroCounterCount=191",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Materialization Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-materialization-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-materialization-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandMaterializationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-materialization-complete-public-safe-non-armed-command-arm-checklist-command-contract-not-command-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Consumer Validation Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-consumer-validation-proof-plan",
    "sourceCommandArmChecklistCommandArmChecklistBoundaryStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-boundary-defined-public-safe-no-command-arming",
    "sourceProofCount=47",
    "sourceCommandArmChecklistCommandArmChecklistBoundaryProofCount=46",
    "sourceCommandArmChecklistCommandArmChecklistBoundaryInterfaceCount=10",
    "commandArmChecklistCommandArmChecklistCommandMaterializationInterfaceCount=12",
    "commandArmChecklistCommandArmChecklistCommandConsumerValidationLaneSelected=true",
    "commandArmChecklistCommandArmChecklistBoundaryRowsConsumed=99",
    "commandArmChecklistCommandArmChecklistCommandContractRows=99",
    "nonArmedCommandArmChecklistCommandArmChecklistCommandContractRowCount=99",
    "readyForLaterCommandArmChecklistCommandArmChecklistCommandConsumerValidationRowCount=99",
    "publicSafeCommandArmChecklistCommandArmChecklistCommandContractArtifactRows=1",
    "publicAllowedOutputCount=70",
    "redactedFieldCount=36",
    "falseGuardCount=217",
    "zeroCounterCount=180",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Boundary Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-boundary-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-boundary-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistBoundaryStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-boundary-defined-public-safe-no-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Materialization Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-materialization-proof-plan",
    "sourceCommandArmChecklistCommandArmChecklistReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-readiness-gate-complete-public-safe-readiness-only-not-command-arming",
    "sourceProofCount=46",
    "sourceCommandArmChecklistCommandArmChecklistReadinessGateProofCount=45",
    "sourceCommandArmChecklistCommandArmChecklistReadinessGateInterfaceCount=10",
    "commandArmChecklistCommandArmChecklistBoundaryInterfaceCount=10",
    "commandArmChecklistCommandArmChecklistReadinessGateRowsConsumed=99",
    "commandArmChecklistCommandArmChecklistBoundaryRows=99",
    "definedCommandArmChecklistCommandArmChecklistBoundaryRowCount=99",
    "passedCommandArmChecklistCommandArmChecklistBoundaryRowCount=99",
    "failedCommandArmChecklistCommandArmChecklistBoundaryRowCount=0",
    "readyForLaterCommandArmChecklistCommandArmChecklistCommandMaterializationRowCount=99",
    "publicSafeCommandArmChecklistCommandArmChecklistBoundaryArtifactRows=1",
    "publicAllowedOutputCount=67",
    "redactedFieldCount=35",
    "stopConditionCount=12",
    "falseGuardCount=212",
    "zeroCounterCount=174",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Readiness Gate Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-readiness-gate-complete-public-safe-readiness-only-not-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Boundary Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-boundary-proof-plan",
    "sourceCommandArmChecklistCommandArmChecklistValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-validation-complete-public-safe-not-run-checklist-rows-validated-no-command-arming",
    "sourceProofCount=45",
    "sourceCommandArmChecklistCommandArmChecklistValidationProofCount=44",
    "sourceCommandArmChecklistCommandArmChecklistValidationInterfaceCount=16",
    "commandArmChecklistCommandArmChecklistReadinessGateInterfaceCount=10",
    "commandArmChecklistCommandArmChecklistValidationRowsConsumed=99",
    "commandArmChecklistCommandArmChecklistReadinessGateRows=99",
    "passedCommandArmChecklistCommandArmChecklistReadinessGateRowCount=99",
    "failedCommandArmChecklistCommandArmChecklistReadinessGateRowCount=0",
    "readyForLaterCommandArmChecklistCommandArmChecklistBoundaryRowCount=99",
    "publicSafeCommandArmChecklistCommandArmChecklistReadinessGateArtifactRows=1",
    "publicAllowedOutputCount=64",
    "redactedFieldCount=34",
    "falseGuardCount=208",
    "zeroCounterCount=169",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Validation Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-validation-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-validation-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-validation-complete-public-safe-not-run-checklist-rows-validated-no-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Readiness Gate Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-readiness-gate-proof-plan",
    "sourceCommandArmChecklistCommandArmChecklistPopulationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-population-complete-public-safe-not-run-checklist-populated-no-command-arming",
    "sourceProofCount=44",
    "sourceCommandArmChecklistCommandArmChecklistPopulationProofCount=43",
    "sourceCommandArmChecklistCommandArmChecklistPopulationInterfaceCount=12",
    "commandArmChecklistCommandArmChecklistValidationInterfaceCount=16",
    "commandArmChecklistCommandArmChecklistRowsConsumed=99",
    "commandArmChecklistCommandArmChecklistValidationRows=99",
    "validatedNotRunCommandArmChecklistRowCount=99",
    "validatedUnobservedCommandArmChecklistRowCount=99",
    "validatedNotArmedCommandArmChecklistRowCount=99",
    "validatedNotExecutedCommandArmChecklistRowCount=99",
    "readyForLaterCommandArmChecklistCommandArmChecklistReadinessGateRowCount=99",
    "publicSafeCommandArmChecklistCommandArmChecklistValidationArtifactRows=1",
    "publicAllowedOutputCount=61",
    "redactedFieldCount=33",
    "falseGuardCount=200",
    "zeroCounterCount=165",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Population Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-population-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-population-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistPopulationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-population-complete-public-safe-not-run-checklist-populated-no-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Validation Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-validation-proof-plan",
    "sourceCommandArmChecklistCommandArmBoundaryStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-boundary-defined-public-safe-no-command-arming",
    "sourceProofCount=43",
    "sourceCommandArmChecklistCommandArmBoundaryProofCount=42",
    "sourceCommandArmChecklistCommandArmBoundaryInterfaceCount=10",
    "commandArmChecklistCommandArmChecklistPopulationInterfaceCount=12",
    "commandArmChecklistCommandArmBoundaryRowsConsumed=99",
    "commandArmChecklistCommandArmChecklistPopulationRows=99",
    "notRunCommandArmChecklistRowCount=99",
    "unobservedCommandArmChecklistRowCount=99",
    "readyForLaterCommandArmChecklistCommandArmChecklistValidationRowCount=99",
    "publicSafeCommandArmChecklistCommandArmChecklistPopulationArtifactRows=1",
    "publicAllowedOutputCount=58",
    "redactedFieldCount=32",
    "falseGuardCount=196",
    "zeroCounterCount=162",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Boundary Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-boundary-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-boundary-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmBoundaryStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-boundary-defined-public-safe-no-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Population Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-population-proof-plan",
    "sourceCommandArmChecklistCommandArmReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-readiness-gate-complete-public-safe-readiness-only-not-command-arming",
    "sourceProofCount=42",
    "sourceCommandArmChecklistCommandArmReadinessGateProofCount=41",
    "sourceCommandArmChecklistCommandArmReadinessGateInterfaceCount=10",
    "commandArmChecklistCommandArmBoundaryInterfaceCount=10",
    "commandArmChecklistCommandArmReadinessGateRowsConsumed=99",
    "commandArmChecklistCommandArmBoundaryRows=99",
    "definedCommandArmChecklistCommandArmBoundaryRowCount=99",
    "passedCommandArmChecklistCommandArmBoundaryRowCount=99",
    "failedCommandArmChecklistCommandArmBoundaryRowCount=0",
    "readyForLaterCommandArmChecklistCommandArmChecklistPopulationRowCount=99",
    "publicSafeCommandArmChecklistCommandArmBoundaryArtifactRows=1",
    "publicAllowedOutputCount=55",
    "redactedFieldCount=31",
    "stopConditionCount=12",
    "falseGuardCount=193",
    "zeroCounterCount=161",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Readiness Gate Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-readiness-gate-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-readiness-gate-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-readiness-gate-complete-public-safe-readiness-only-not-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Boundary Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-boundary-proof-plan",
    "sourceCommandArmChecklistCommandDryRunConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-dry-run-consumer-validation-complete-public-safe-non-dispatched-command-arm-checklist-command-dry-run-consumed-not-real-importer-execution",
    "sourceProofCount=41",
    "sourceCommandArmChecklistCommandDryRunConsumerValidationProofCount=40",
    "sourceCommandArmChecklistCommandDryRunConsumerValidationInterfaceCount=10",
    "commandArmChecklistCommandArmReadinessGateInterfaceCount=10",
    "commandArmChecklistCommandDryRunConsumerValidationRowsConsumed=99",
    "commandArmChecklistCommandArmReadinessGateRows=99",
    "passedCommandArmChecklistCommandArmReadinessGateRowCount=99",
    "failedCommandArmChecklistCommandArmReadinessGateRowCount=0",
    "readyForLaterCommandArmChecklistCommandArmBoundaryRowCount=99",
    "publicSafeCommandArmChecklistCommandArmReadinessGateArtifactRows=1",
    "publicAllowedOutputCount=52",
    "redactedFieldCount=30",
    "falseGuardCount=189",
    "zeroCounterCount=156",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Dry-Run Consumer Validation Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-dry-run-consumer-validation-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-dry-run-consumer-validation-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandDryRunConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-dry-run-consumer-validation-complete-public-safe-non-dispatched-command-arm-checklist-command-dry-run-consumed-not-real-importer-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Readiness Gate Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-readiness-gate-proof-plan",
    "sourceCommandArmChecklistCommandDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-dry-run-complete-public-safe-readiness-row-consumption-not-real-importer-execution",
    "sourceProofCount=40",
    "sourceCommandArmChecklistCommandDryRunProofCount=39",
    "sourceCommandArmChecklistCommandDryRunInterfaceCount=10",
    "commandArmChecklistCommandDryRunConsumerValidationInterfaceCount=10",
    "commandArmChecklistCommandDryRunRowsConsumed=99",
    "commandArmChecklistCommandDryRunConsumerValidationRows=99",
    "validatedNonDispatchedCommandArmChecklistCommandDryRunRowCount=99",
    "readyForLaterCommandArmChecklistCommandArmReadinessGateRowCount=99",
    "publicSafeCommandArmChecklistCommandDryRunConsumerValidationArtifactRows=1",
    "publicAllowedOutputCount=49",
    "redactedFieldCount=29",
    "falseGuardCount=184",
    "zeroCounterCount=150",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Dry-Run Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-dry-run-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-dry-run-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-dry-run-complete-public-safe-readiness-row-consumption-not-real-importer-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Dry-Run Consumer Validation Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-dry-run-consumer-validation-proof-plan",
    "sourceCommandArmChecklistCommandReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-readiness-gate-complete-public-safe-readiness-only-not-command-execution",
    "sourceProofCount=39",
    "sourceCommandArmChecklistCommandReadinessGateProofCount=38",
    "sourceCommandArmChecklistCommandReadinessGateInterfaceCount=10",
    "commandArmChecklistCommandDryRunInterfaceCount=10",
    "commandArmChecklistCommandReadinessGateRowsConsumed=99",
    "commandArmChecklistCommandDryRunRows=99",
    "passedCommandArmChecklistCommandDryRunRowCount=99",
    "failedCommandArmChecklistCommandDryRunRowCount=0",
    "readyForLaterCommandArmChecklistCommandDryRunConsumerValidationRowCount=99",
    "publicSafeCommandArmChecklistCommandDryRunArtifactRows=1",
    "publicAllowedOutputCount=46",
    "redactedFieldCount=28",
    "falseGuardCount=179",
    "zeroCounterCount=146",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Readiness Gate Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-readiness-gate-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-readiness-gate-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-readiness-gate-complete-public-safe-readiness-only-not-command-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Dry-Run Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-dry-run-proof-plan",
    "sourceCommandArmChecklistCommandConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-consumer-validation-complete-public-safe-non-armed-command-contract-consumed-not-real-importer-execution",
    "sourceProofCount=38",
    "sourceCommandArmChecklistCommandConsumerValidationProofCount=37",
    "sourceCommandArmChecklistCommandConsumerValidationInterfaceCount=12",
    "commandArmChecklistCommandReadinessGateInterfaceCount=10",
    "commandArmChecklistCommandConsumerValidationRowsConsumed=99",
    "commandArmChecklistCommandReadinessGateRows=99",
    "passedCommandArmChecklistCommandReadinessGateRowCount=99",
    "failedCommandArmChecklistCommandReadinessGateRowCount=0",
    "readyForLaterCommandArmChecklistCommandDryRunRowCount=99",
    "publicSafeCommandArmChecklistCommandReadinessGateArtifactRows=1",
    "publicAllowedOutputCount=42",
    "redactedFieldCount=26",
    "falseGuardCount=173",
    "zeroCounterCount=143",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Consumer Validation Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-consumer-validation-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-consumer-validation-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-consumer-validation-complete-public-safe-non-armed-command-contract-consumed-not-real-importer-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Readiness Gate Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-readiness-gate-proof-plan",
    "sourceCommandArmChecklistCommandMaterializationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-materialization-complete-public-safe-non-armed-command-contract-not-command-execution",
    "sourceProofCount=37",
    "sourceCommandArmChecklistCommandMaterializationProofCount=36",
    "commandConsumerValidationInterfaceCount=12",
    "commandArmChecklistCommandContractRowsConsumed=99",
    "commandConsumerValidationRows=99",
    "validatedNonArmedCommandContractRowCount=99",
    "readyForLaterCommandReadinessGateRowCount=99",
    "publicSafeCommandArmChecklistCommandConsumerValidationArtifactRows=1",
    "falseGuardCount=167",
    "zeroCounterCount=137",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Readiness Gate Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-readiness-gate-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-readiness-gate-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-readiness-gate-complete-public-safe-readiness-only-no-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Materialization Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-materialization-proof-plan",
    "sourceCommandArmChecklistValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-validation-complete-public-safe-not-run-checklist-rows-validated-no-command-arming",
    "sourceProofCount=35",
    "sourceCommandArmChecklistValidationProofCount=34",
    "commandArmChecklistReadinessGateInterfaceCount=12",
    "commandArmChecklistValidationRowsConsumedByReadinessGate=true",
    "commandArmChecklistReadinessGateRows=99",
    "readyForLaterCommandArmChecklistCommandMaterializationRowCount=99",
    "publicSafeCommandArmChecklistReadinessGateArtifactRows=1",
    "falseGuardCount=155",
    "zeroCounterCount=129",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Materialization Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-materialization-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-materialization-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandMaterializationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-materialization-complete-public-safe-non-armed-command-contract-not-command-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Consumer Validation Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-consumer-validation-proof-plan",
    "sourceCommandArmChecklistReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-readiness-gate-complete-public-safe-readiness-only-no-command-arming",
    "sourceProofCount=36",
    "sourceCommandArmChecklistReadinessGateProofCount=35",
    "commandArmChecklistCommandMaterializationInterfaceCount=12",
    "commandArmChecklistCommandContractRows=99",
    "readyForLaterCommandArmChecklistCommandConsumerValidationRowCount=99",
    "falseGuardCount=162",
    "zeroCounterCount=135",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Validation Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-validation-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-validation-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-validation-complete-public-safe-not-run-checklist-rows-validated-no-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Readiness Gate Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-readiness-gate-proof-plan",
    "sourceCommandArmChecklistPopulationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-population-complete-public-safe-not-run-checklist-populated-no-command-arming",
    "sourceProofCount=34",
    "sourceCommandArmChecklistPopulationProofCount=33",
    "commandArmChecklistValidationInterfaceCount=16",
    "commandArmChecklistValidationInputAccepted=true",
    "commandArmChecklistRowsConsumed=99",
    "commandArmChecklistValidationRows=99",
    "passedCommandArmChecklistValidationRowCount=99",
    "readyForLaterCommandArmChecklistReadinessGateRowCount=99",
    "publicSafeCommandArmChecklistValidationArtifactRows=1",
    "publicLeakCheck=PASS",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Population Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-population-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-population-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistPopulationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-population-complete-public-safe-not-run-checklist-populated-no-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Validation Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-validation-proof-plan",
    "sourceCommandArmBoundaryStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-boundary-defined-public-safe-no-command-arming",
    "sourceProofCount=33",
    "sourceCommandArmBoundaryProofCount=32",
    "sourceCommandArmBoundaryInterfaceCount=10",
    "commandArmChecklistPopulationInterfaceCount=12",
    "privateCorpusRealImporterDryRunHarnessCommandArmChecklistPopulationOnly=true",
    "commandArmBoundaryProofConsumed=true",
    "commandArmBoundaryProofContinuityValidated=true",
    "commandArmBoundaryRowsConsumedByChecklistPopulation=true",
    "commandArmChecklistPopulationRowsPopulated=true",
    "commandArmChecklistValidationLaneSelected=true",
    "commandArmBoundaryRowsConsumed=99",
    "commandArmChecklistPopulationRows=99",
    "populatedCommandArmChecklistRowCount=99",
    "passedCommandArmChecklistPopulationRowCount=99",
    "failedCommandArmChecklistPopulationRowCount=0",
    "notRunCommandArmChecklistRowCount=99",
    "unobservedCommandArmChecklistRowCount=99",
    "readyForLaterCommandArmChecklistValidationRowCount=99",
    "preflightCheckCount=17",
    "passedPreflightCheckCount=17",
    "failedPreflightCheckCount=0",
    "publicSafeCommandArmChecklistPopulationArtifactRows=1",
    "publicAllowedOutputCount=28",
    "redactedFieldCount=21",
    "falseGuardCount=143",
    "zeroCounterCount=122",
    "realImporterDryRunHarnessCommandArmChecklistValidationRows=0",
    "commandArmChecklistDryRunRows=0",
    "commandArmChecklistPrivateOutputRows=0",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Boundary Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-boundary-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-boundary-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmBoundaryStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-boundary-defined-public-safe-no-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Population Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-population-proof-plan",
    "sourceCommandArmReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-readiness-gate-complete-public-safe-readiness-only-not-command-arming",
    "sourceProofCount=32",
    "sourceCommandArmReadinessGateProofCount=31",
    "sourceCommandArmReadinessGateInterfaceCount=10",
    "commandArmBoundaryInterfaceCount=10",
    "privateCorpusRealImporterDryRunHarnessCommandArmBoundaryOnly=true",
    "commandArmReadinessGateProofConsumed=true",
    "commandArmReadinessGateProofContinuityValidated=true",
    "commandArmReadinessGateProofRowsConsumed=true",
    "commandArmBoundaryDefined=true",
    "commandArmBoundaryInputAccepted=true",
    "commandArmBoundaryRowStatusesValidated=true",
    "commandArmBoundaryRowOrdinalsValidated=true",
    "commandArmBoundaryCategoryCountsValidated=true",
    "commandArmBoundaryInterfacesValidated=true",
    "commandArmBoundaryStopConditionsValidated=true",
    "commandArmBoundaryEmitsOnlyPublicSafeRows=true",
    "commandArmBoundaryRedactionPolicyValidated=true",
    "harnessCommandArmChecklistPopulationLaneSelected=true",
    "futureCommandArmRequiresExplicitOperatorArm=true",
    "commandArmReadinessGateRowsConsumed=99",
    "commandArmBoundaryRows=99",
    "definedCommandArmBoundaryRowCount=99",
    "passedCommandArmBoundaryRowCount=99",
    "failedCommandArmBoundaryRowCount=0",
    "readyForLaterCommandArmChecklistPopulationRowCount=99",
    "publicSafeCommandArmBoundaryArtifactRows=1",
    "publicAllowedOutputCount=25",
    "redactedFieldCount=20",
    "stopConditionCount=12",
    "falseGuardCount=136",
    "zeroCounterCount=115",
    "realImporterDryRunHarnessCommandArmBoundaryRows=0",
    "realImporterDryRunHarnessCommandArmChecklistPopulationRows=0",
    "publicLeakCheck=PASS",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Readiness Gate Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-readiness-gate-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-readiness-gate-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandArmReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-readiness-gate-complete-public-safe-readiness-only-not-command-arming",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Boundary Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-boundary-proof-plan",
    "sourceCommandDryRunConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-dry-run-consumer-validation-complete-public-safe-non-dispatched-command-dry-run-consumed-not-real-importer-execution",
    "sourceProofCount=31",
    "sourceCommandDryRunConsumerValidationProofCount=30",
    "commandDryRunConsumerValidationRowsConsumed=99",
    "commandArmReadinessGateRows=99",
    "passedCommandArmReadinessGateRowCount=99",
    "failedCommandArmReadinessGateRowCount=0",
    "readyForLaterCommandArmBoundaryRowCount=99",
    "publicSafeCommandArmReadinessGateArtifactRows=1",
    "publicAllowedOutputCount=22",
    "redactedFieldCount=19",
    "falseGuardCount=132",
    "zeroCounterCount=110",
    "publicLeakCheck=PASS",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Dry-Run Consumer Validation Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-dry-run-consumer-validation-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-dry-run-consumer-validation-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandDryRunConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-dry-run-consumer-validation-complete-public-safe-non-dispatched-command-dry-run-consumed-not-real-importer-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Readiness Gate Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-readiness-gate-proof-plan",
    "sourceCommandDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-dry-run-complete-public-safe-readiness-row-consumption-not-real-importer-execution",
    "sourceProofCount=30",
    "sourceCommandDryRunProofCount=29",
    "commandDryRunConsumerValidationRows=99",
    "validatedNonDispatchedCommandDryRunRowCount=99",
    "readyForLaterCommandArmReadinessGateRowCount=99",
    "publicSafeCommandDryRunConsumerValidationArtifactRows=1",
    "publicAllowedOutputCount=19",
    "redactedFieldCount=18",
    "falseGuardCount=127",
    "zeroCounterCount=104",
    "publicLeakCheck=PASS",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Dry-Run Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-dry-run-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-dry-run-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-dry-run-complete-public-safe-readiness-row-consumption-not-real-importer-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Dry-Run Consumer Validation Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-dry-run-consumer-validation-proof-plan",
    "sourceCommandReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-readiness-gate-complete-public-safe-readiness-only-not-command-execution",
    "sourceProofCount=29",
    "sourceCommandReadinessGateProofCount=28",
    "commandReadinessGateRowsConsumed=99",
    "commandDryRunRows=99",
    "passedCommandDryRunRowCount=99",
    "failedCommandDryRunRowCount=0",
    "readyForLaterCommandDryRunConsumerValidationRowCount=99",
    "publicSafeCommandDryRunArtifactRows=1",
    "publicAllowedOutputCount=16",
    "redactedFieldCount=17",
    "falseGuardCount=122",
    "zeroCounterCount=100",
    "publicLeakCheck=PASS",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Readiness Gate Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-readiness-gate-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-readiness-gate-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-readiness-gate-complete-public-safe-readiness-only-not-command-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Dry-Run Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-dry-run-proof-plan",
    "sourceCommandConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-consumer-validation-complete-public-safe-non-armed-command-contract-consumed-not-real-importer-execution",
    "sourceProofCount=28",
    "sourceCommandConsumerValidationProofCount=27",
    "commandConsumerValidationRowsConsumed=99",
    "commandReadinessGateRows=99",
    "passedCommandReadinessGateRowCount=99",
    "failedCommandReadinessGateRowCount=0",
    "readyForLaterCommandDryRunRowCount=99",
    "publicSafeCommandReadinessGateArtifactRows=1",
    "publicAllowedOutputCount=12",
    "redactedFieldCount=14",
    "falseGuardCount=116",
    "zeroCounterCount=98",
    "publicLeakCheck=PASS",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Consumer Validation Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-consumer-validation-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-consumer-validation-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-consumer-validation-complete-public-safe-non-armed-command-contract-consumed-not-real-importer-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Readiness Gate Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-readiness-gate-proof-plan",
    "sourceCommandMaterializationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-materialization-complete-public-safe-non-armed-command-contract-not-real-importer-execution",
    "sourceProofCount=27",
    "sourceCommandMaterializationProofCount=26",
    "harnessCommandContractRowsConsumed=99",
    "commandConsumerValidationRows=99",
    "validatedNonArmedCommandContractRowCount=99",
    "readyForLaterCommandReadinessGateRowCount=99",
    "publicSafeCommandConsumerValidationArtifactRows=1",
    "publicAllowedOutputCount=9",
    "redactedFieldCount=13",
    "falseGuardCount=111",
    "zeroCounterCount=92",
    "publicLeakCheck=PASS",    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Materialization Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-materialization-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-materialization-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessCommandMaterializationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-materialization-complete-public-safe-non-armed-command-contract-not-real-importer-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Consumer Validation Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-consumer-validation-proof-plan",
    "sourceRealImporterHarnessChecklistReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-readiness-gate-complete-public-safe-readiness-only-not-real-importer-execution",
    "sourceProofCount=26",
    "sourceReadinessGateProofCount=25",
    "realImporterHarnessChecklistReadinessGateProofConsumed=true",
    "realImporterHarnessChecklistReadinessGateProofContinuityValidated=true",
    "realImporterDryRunHarnessCommandMaterializationExecuted=true",
    "realImporterDryRunHarnessCommandMaterializationInputAccepted=true",
    "publicSafeNonArmedHarnessCommandContractMaterialized=true",
    "publicSafeNonArmedHarnessCommandContractStoredInTrackedProof=true",
    "publicSafeNonArmedHarnessCommandContractPathPublished=false",
    "harnessCommandContractRowsGenerated=true",
    "harnessCommandContractRowsValidated=true",
    "harnessCommandContractAggregateCountsValidated=true",
    "harnessCommandContractInterfacesValidated=true",
    "harnessCommandContractEmitsOnlyPublicSafeRows=true",
    "harnessCommandContractRedactionPolicyValidated=true",
    "harnessCommandConsumerValidationLaneSelected=true",
    "harnessChecklistReadinessGateRowsConsumed=99",
    "harnessCommandContractRows=99",
    "nonArmedCommandContractRowCount=99",
    "armedCommandRowCount=0",
    "executedCommandRowCount=0",
    "shellDispatchedCommandRowCount=0",
    "publicSafeHarnessCommandContractArtifactRows=1",
    "falseGuardCount=106",
    "zeroCounterCount=88",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Readiness Gate Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-readiness-gate-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-readiness-gate-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessChecklistReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-readiness-gate-complete-public-safe-readiness-only-not-real-importer-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Materialization Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-materialization-proof-plan",
    "sourceRealImporterHarnessChecklistValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-validation-complete-public-safe-checklist-rows-validated-not-real-importer-execution",
    "sourceProofCount=25",
    "sourceChecklistValidationProofCount=24",
    "realImporterHarnessChecklistValidationProofConsumed=true",
    "realImporterHarnessChecklistValidationProofContinuityValidated=true",
    "realImporterHarnessChecklistValidationRowsConsumed=true",
    "realImporterDryRunHarnessChecklistReadinessGateExecuted=true",
    "harnessChecklistReadinessGatePreconditionsValidated=true",
    "harnessChecklistReadyRowStatusesValidated=true",
    "harnessChecklistReadinessGateRowOrdinalsValidated=true",
    "harnessChecklistReadinessGateCategoryCountsValidated=true",
    "harnessChecklistCommandPrerequisiteClassesValidated=true",
    "harnessChecklistReadinessGateEmitsOnlyPublicSafeRows=true",
    "harnessChecklistReadinessGateRedactionPolicyValidated=true",
    "harnessCommandMaterializationLaneSelected=true",
    "harnessChecklistValidationRowsConsumed=99",
    "harnessChecklistReadinessGateRows=99",
    "passedReadinessGateRowCount=99",
    "failedReadinessGateRowCount=0",
    "readyForLaterCommandMaterializationRowCount=99",
    "readyForLaterHarnessArmRowCount=99",
    "falseGuardCount=100",
    "zeroCounterCount=85",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Validation Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-validation-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-validation-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessChecklistValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-validation-complete-public-safe-checklist-rows-validated-not-real-importer-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Readiness Gate Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-readiness-gate-proof-plan",
    "sourceRealImporterHarnessChecklistPopulationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-complete-public-safe-checklist-populated-not-real-importer-execution",
    "sourceProofCount=24",
    "sourceChecklistPopulationProofCount=23",
    "privateCorpusRealImporterDryRunHarnessChecklistValidationOnly=true",
    "realImporterHarnessChecklistPopulationProofConsumed=true",
    "realImporterHarnessChecklistPopulationProofContinuityValidated=true",
    "realImporterDryRunHarnessChecklistValidationExecuted=true",
    "realImporterDryRunHarnessChecklistValidationInputAccepted=true",
    "harnessChecklistSchemaValidated=true",
    "harnessChecklistRowOrdinalsValidated=true",
    "harnessChecklistCategoryCountsValidated=true",
    "harnessChecklistNotRunStatusesValidated=true",
    "harnessChecklistUnobservedStatusesValidated=true",
    "harnessChecklistReadinessGateLaneSelected=true",
    "harnessChecklistRowsConsumed=99",
    "harnessChecklistValidationRows=99",
    "validatedNotRunChecklistRowCount=99",
    "validatedUnobservedChecklistRowCount=99",
    "publicSafeHarnessChecklistValidationArtifactRows=1",
    "publicAllowedOutputCount=5",
    "redactedFieldCount=10",
    "falseGuardCount=98",
    "zeroCounterCount=85",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Population Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessChecklistPopulationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-complete-public-safe-checklist-populated-not-real-importer-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Validation Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-validation-proof-plan",
    "sourceRealImporterHarnessBoundaryStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-defined-public-safe-boundary-only-not-real-importer-execution",
    "sourceProofCount=23",
    "sourceHarnessBoundaryProofCount=22",
    "privateCorpusRealImporterDryRunHarnessChecklistPopulationOnly=true",
    "realImporterHarnessBoundaryProofConsumed=true",
    "realImporterHarnessBoundaryProofContinuityValidated=true",
    "realImporterHarnessBoundaryRowsConsumedByChecklistPopulation=true",
    "realImporterDryRunHarnessChecklistPopulated=true",
    "harnessChecklistRowsPopulated=true",
    "harnessChecklistArchiveClassRowsPopulated=true",
    "harnessChecklistInputClassRowsPopulated=true",
    "harnessChecklistRequiredArtifactRowsPopulated=true",
    "harnessChecklistStopConditionRowsPopulated=true",
    "harnessChecklistValidationLaneSelected=true",
    "harnessChecklistRows=99",
    "notRunChecklistRowCount=99",
    "unobservedChecklistRowCount=99",
    "preflightCheckCount=17",
    "realImporterDryRunHarnessChecklistValidationExecuted=false",
    "falseGuardCount=94",
    "zeroCounterCount=79",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Boundary Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunHarnessBoundaryStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-defined-public-safe-boundary-only-not-real-importer-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Population Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-checklist-population-proof-plan",
    "sourceRealImporterReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-readiness-gate-complete-public-safe-readiness-only-not-real-importer-execution",
    "sourceProofCount=22",
    "privateCorpusRealImporterDryRunHarnessBoundaryOnly=true",
    "realImporterReadinessGateProofConsumed=true",
    "realImporterReadinessGateProofContinuityValidated=true",
    "realImporterReadinessRowsConsumedByHarnessBoundary=true",
    "realImporterDryRunHarnessBoundaryDefined=true",
    "harnessBoundaryRows=5",
    "harnessBoundaryArchiveClassRows=5",
    "consumerArchiveTotalCount=301",
    "realImporterDryRunHarnessBoundaryInterfaceCount=10",
    "harnessAllowedFutureInputClassCount=5",
    "harnessRequiredFutureArtifactClassCount=6",
    "harnessStopConditionCount=12",
    "publicAllowedOutputCount=33",
    "redactedFieldCount=28",
    "falseGuardCount=85",
    "zeroCounterCount=69",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Readiness Gate Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-readiness-gate-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-readiness-gate-proof-plan.v1.json",
    "privateCorpusRealImporterDryRunReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-readiness-gate-complete-public-safe-readiness-only-not-real-importer-execution",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Boundary Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-boundary-proof-plan",
    "sourceAdapterConsumerDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-dry-run-complete-public-safe-readiness-row-consumption-not-real-importer",
    "sourceProofCount=21",
    "privateCorpusRealImporterDryRunReadinessGateOnly=true",
    "adapterConsumerDryRunProofConsumed=true",
    "adapterConsumerDryRunProofContinuityValidated=true",
    "adapterConsumerDryRunRowsConsumedByReadinessGate=true",
    "realImporterDryRunReadinessGateExecuted=true",
    "realImporterReadinessArchiveClassOrderValidated=true",
    "realImporterReadinessArchiveClassCountsValidated=true",
    "realImporterReadinessGuardCountersValidated=true",
    "realImporterReadinessInterfacesValidated=true",
    "realImporterDryRunHarnessBoundaryLaneSelected=true",
    "realImporterReadinessEmitsOnlyPublicSafeRows=true",
    "realImporterReadinessArchiveClassRows=5",
    "consumerArchiveTotalCount=301",
    "realImporterDryRunReadinessInterfaceCount=8",
    "publicAllowedOutputCount=27",
    "redactedFieldCount=23",
    "falseGuardCount=77",
    "zeroCounterCount=63",
    "realImporterDryRunHarnessExecuted=false",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Consumer Dry-Run Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-dry-run-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-dry-run-proof-plan.v1.json",
    "privateCorpusRedactedManifestImporterContractAdapterConsumerDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-dry-run-complete-public-safe-readiness-row-consumption-not-real-importer",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Readiness Gate Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-readiness-gate-proof-plan",
    "sourceConsumerReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-readiness-gate-complete-public-safe-next-lane-selected-not-real-importer",
    "sourceProofCount=20",
    "redactedManifestImporterContractAdapterConsumerDryRunOnly=true",
    "consumerReadinessProofConsumed=true",
    "consumerReadinessProofContinuityValidated=true",
    "consumerReadinessGateRowsConsumed=true",
    "adapterConsumerDryRunExecuted=true",
    "adapterConsumerDryRunRowsGenerated=true",
    "adapterConsumerDryRunRowsValidated=true",
    "adapterConsumerDryRunArchiveClassRows=5",
    "consumerArchiveTotalCount=301",
    "adapterConsumerDryRunInterfaceCount=8",
    "publicSafeAdapterConsumerDryRunSummaryRows=1",
    "realImporterImplementation=false",
    "realImporterExecuted=false",
    "privateImporterDryRunExecuted=false",
    "realImporterDryRunExecuted=false",
    "actualAssetImportRows=0",
    "generatedAssetRows=0",
    "outputArtifactRows=0",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Consumer Readiness Gate Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-readiness-gate-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-readiness-gate-proof-plan.v1.json",
    "privateCorpusRedactedManifestImporterContractAdapterConsumerReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-readiness-gate-complete-public-safe-next-lane-selected-not-real-importer",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Consumer Dry-Run Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-dry-run-proof-plan",
    "sourceConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-consumer-validation-complete-public-safe-materialized-adapter-artifact-consumed-not-real-importer",
    "sourceProofCount=19",
    "consumerValidationProofConsumed=true",
    "consumerValidationProofContinuityValidated=true",
    "consumerReadinessGateExecuted=true",
    "consumerDryRunLaneSelected=true",
    "consumerReadinessGateRows=5",
    "consumerReadinessArchiveClassRows=5",
    "publicSafeConsumerReadinessArtifactRows=1",
    "adapterConsumerDryRunExecuted=false",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Materialization Consumer Validation Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-consumer-validation-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-consumer-validation-proof-plan.v1.json",
    "privateCorpusRedactedManifestImporterContractAdapterMaterializationConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-consumer-validation-complete-public-safe-materialized-adapter-artifact-consumed-not-real-importer",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Consumer Readiness Gate Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-consumer-readiness-gate-proof-plan",
    "sourceMaterializationStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-complete-public-safe-adapter-dry-run-row-artifact-not-real-importer",
    "sourceProofCount=18",
    "materializedAdapterArtifactConsumed=true",
    "materializedAdapterArtifactContinuityValidated=true",
    "consumerValidationExecuted=true",
    "consumerValidationRows=5",
    "consumerValidationArchiveClassRows=5",
    "consumerArchiveTotalCount=301",
    "publicSafeConsumerValidationArtifactRows=1",
    "realImporterConsumerValidationExecuted=false",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Dry-Run Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-dry-run-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-dry-run-proof-plan.v1.json",
    "privateCorpusRedactedManifestImporterContractAdapterDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-dry-run-complete-public-safe-adapter-row-consumption-not-real-importer",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Materialization Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-proof-plan",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Materialization Proof Plan",
    "privateCorpusRedactedManifestImporterContractAdapterMaterializationStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-complete-public-safe-adapter-dry-run-row-artifact-not-real-importer",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Materialization Consumer Validation Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-materialization-consumer-validation-proof-plan",
    "sourceAdapterStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-complete-public-safe-adapter-rows-not-real-importer",
    "sourceProofCount=16",
    "redactedManifestImporterContractAdapterDryRunOnly=true",
    "adapterProofConsumed=true",
    "adapterContractDryRunExecuted=true",
    "adapterDryRunRowsGenerated=true",
    "adapterDryRunRowsValidated=true",
    "adapterDryRunArchiveClassRows=5",
    "adapterDryRunInterfaceCount=8",
    "realImporterDryRunExecuted=false",
    "privateImporterMaterializationExecuted=false",
    "adapterDryRunReadPrivateInputs=false",
    "privateDryRunRows=0",
    "realImporterDryRunRows=0",
    "rawDryRunTraceRows=0",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-proof-plan.v1.json",
    "privateCorpusRedactedManifestImporterContractAdapterStatus=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-complete-public-safe-adapter-rows-not-real-importer",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Dry-Run Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-dry-run-proof-plan",
    "sourceConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-consumer-validation-complete-redacted-manifest-consumed-no-content-read",
    "sourcePublicContractSkeletonStatus=texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-complete-public-contract-only-not-real-importer-proof",
    "redactedManifestImporterContractAdapterImplemented=true",
    "adapterRowsGenerated=true",
    "adapterRowsValidated=true",
    "adapterArchiveClassRows=5",
    "adapterArchiveTotalCount=301",
    "adapterContractInterfaceCount=7",
    "privateImporterDryRunExecuted=false",
    "actualAssetImportRows=0",
    "generatedAssetRows=0",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Consumer Validation Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-consumer-validation-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-consumer-validation-proof-plan.v1.json",
    "privateCorpusReadOnlyManifestConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-consumer-validation-complete-redacted-manifest-consumed-no-content-read",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-redacted-manifest-importer-contract-adapter-proof-plan",
    "sourceMaterializationStatus=texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-complete-redacted-private-manifest-artifact-no-content-read",
    "privateCorpusReadOnlyManifestConsumerValidationExecuted=true",
    "redactedPrivateManifestArtifactConsumed=true",
    "redactedPrivateManifestArtifactPathPublished=false",
    "ignoredArtifactPathPublished=false",
    "consumerInputAccepted=true",
    "consumerSchemaValidated=true",
    "consumerArchiveClassRowsValidated=5",
    "consumerArchiveTotalCount=301",
    "rawPrivateManifestConsumed=false",
    "importerContractAdapterImplemented=false",
    "rawManifestPathRows=0",
    "ignoredArtifactPathRows=0",
    "importerContractAdapterRows=0",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Materialization Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-proof-plan.v1.json",
    "privateCorpusReadOnlyManifestMaterializationStatus=texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-complete-redacted-private-manifest-artifact-no-content-read",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Consumer Validation Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-consumer-validation-proof-plan",
    "sourceDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run-complete-redacted-class-manifest-shape-no-content-read",
    "privateCorpusReadOnlyManifestMaterializationExecuted=true",
    "sourceDryRunEvidenceConsumed=true",
    "redactedPrivateManifestMaterialized=true",
    "redactedPrivateManifestArtifactWritten=true",
    "redactedPrivateManifestArtifactStoredOutsidePublicReleaseScope=true",
    "redactedPrivateManifestArtifactPathPublished=false",
    "privateManifestMaterialized=false",
    "privateRawManifestMaterialized=false",
    "privateRawManifestRowsObserved=false",
    "privateManifestRowsPublished=false",
    "publicSafeRedactedManifestArtifactRows=1",
    "materializedRedactedManifestClassRowCount=5",
    "materializedRedactedManifestArchiveTotalCount=301",
    "redactedPrivateManifestRows=5",
    "redactedPrivateManifestSummaryRows=1",
    "privateManifestRows=0",
    "rawPrivateManifestRows=0",
    "outputArtifactRows=0",
    "privateArtifactRows=0",
    "publicLeakCheck=PASS",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Dry-Run Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run-proof-plan.v1.json",
    "privateCorpusReadOnlyManifestDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run-complete-redacted-class-manifest-shape-no-content-read",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Materialization Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-materialization-proof-plan",
    "sourcePreflightStatus=texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-complete-redacted-class-count-summary-no-content-read",
    "privateCorpusReadOnlyManifestDryRunExecuted=true",
    "redactedManifestShapeGenerated=true",
    "manifestClassRowsGenerated=true",
    "manifestDryRunClassRowCount=5",
    "manifestDryRunArchiveTotalCount=301",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Inventory Preflight Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-proof-plan.v1.json",
    "privateCorpusReadOnlyInventoryPreflightStatus=texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-complete-redacted-class-count-summary-no-content-read",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Dry-Run Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-read-only-manifest-dry-run-proof-plan",
    "sourceChecklistPopulationStatus=texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-complete-public-safe-checklist-populated-no-private-corpus-read",
    "privateCorpusReadOnlyInventoryPreflightExecuted=true",
    "privateResourceArchiveClassEnumerationPerformed=true",
    "privateCorpusReadOnlyInventoryGenerated=true",
    "privateEvidenceStoredOutsidePublicReleaseScope=true",
    "allRequiredArchiveClassesObserved=true",
    "ayaArchiveTotalCount=301",
    "observedRequiredArchiveClassCount=5",
    "unknownAyaArchiveClassCount=0",
    "rawPathRows=0",
    "rawFilenameRows=0",
    "rawHashRows=0",
    "byteLengthRows=0",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Safety Packet Checklist Population Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-proof-plan.v1.json",
    "privateCorpusSafetyPacketChecklistPopulationStatus=texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-complete-public-safe-checklist-populated-no-private-corpus-read",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Inventory Preflight Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-read-only-inventory-preflight-proof-plan",
    "sourcePrivateCorpusSafetyBoundaryStatus=texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-defined-no-private-corpus-read",
    "checklistPopulationOnly=true",
    "safetyPacketChecklistPopulated=true",
    "futureReadOnlyPrivateCorpusSliceSelectable=true",
    "futureReadOnlyPrivateCorpusUseAllowedWhenSelected=true",
    "futurePrivateCorpusReadRequiresSelectedReadOnlySlice=true",
    "blockedByMissingExplicitPrivateCorpusArm=true",
    "defaultChecklistRowStatus=not-run",
    "defaultObservationStatus=unobserved",
    "checklistGroupCount=6",
    "checklistRowCount=53",
    "notRunChecklistRowCount=53",
    "unobservedChecklistRowCount=53",
    "observedChecklistRowCount=0",
    "rowStatusChangedCount=0",
    "preflightCheckCount=14",
    "falseGuardCount=51",
    "zeroCounterCount=42",
    "readOnlyInventoryRows=0",
    "privateImporterDryRunRows=0",
    "Completed Texture / Mesh Material Sidecar Importer Private Corpus Safety Boundary Proof Plan",
    "texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan.md",
    "texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan.v1.json",
    "privateCorpusSafetyBoundaryStatus=texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-defined-no-private-corpus-read",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Safety Packet Checklist Population Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-safety-packet-checklist-population-proof-plan",
    "sourcePublicContractSkeletonStatus=texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-complete-public-contract-only-not-real-importer-proof",
    "safetyPacketItemCount=10",
    "authorizationGateCount=8",
    "privateCorpusClassCount=5",
    "redactedFieldCount=12",
    "falseGuardCount=45",
    "zeroCounterCount=36",
    "privateCorpusReadRows=0",
    "realImporterImplementation=false",
    "realImporterExecuted=false",
    "Completed Texture / Mesh Material Sidecar Importer Public Contract Skeleton Implementation Proof Plan",
    "texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan.md",
    "texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan.v1.json",
    "publicContractSkeletonStatus=texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-complete-public-contract-only-not-real-importer-proof",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Private Corpus Safety Boundary Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-private-corpus-safety-boundary-proof-plan",
    "sourceImplementationReadinessStatus=texture-mesh-material-sidecar-importer-implementation-readiness-gate-complete-public-contract-skeleton-ready-not-real-importer-proof",
    "contractInterfaceCount=6",
    "implementedContractInterfaceCount=6",
    "contractFunctionCount=2",
    "publicContractSkeletonImplementationRows=1",
    "skeletonContractCheckCount=46",
    "failedSkeletonContractChecks=0",
    "Completed Texture / Mesh Material Sidecar Importer Implementation Readiness Gate Proof Plan",
    "texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan.md",
    "texture-mesh-material-sidecar-importer-implementation-readiness-gate-proof-plan.v1.json",
    "implementationReadinessStatus=texture-mesh-material-sidecar-importer-implementation-readiness-gate-complete-public-contract-skeleton-ready-not-real-importer-proof",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Public Contract Skeleton Implementation Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-public-contract-skeleton-implementation-proof-plan",
    "sourceConsumerDryRunStatus=texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan-complete-public-safe-consumer-dry-run-not-importer-execution-proof",
    "readinessGateCount=8",
    "readinessCheckCount=16",
    "publicContractSkeletonReadyNow=true",
    "realImporterImplementationReadyNow=false",
    "realImporterExecutionReadyNow=false",
    "Completed Texture / Mesh Material Sidecar Importer Fixture Harness Consumer Dry-Run Proof Plan",
    "Completed Texture / Mesh Material Sidecar Importer Fixture Harness Materialization Proof Plan",
    "texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan.md",
    "texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan.v1.json",
    "materializationStatus=texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan-complete-public-safe-deterministic-fixture-row-materialization-not-runtime-proof",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Fixture Harness Consumer Dry-Run Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-fixture-harness-consumer-dry-run-proof-plan",
    "sourceHarnessStatus=texture-mesh-material-sidecar-importer-fixture-harness-proof-plan-complete-static-importer-harness-contract-not-runtime-proof",
    "materializedFixtureRowCount=8",
    "derivedAssertionCount=6",
    "Completed Texture / Mesh Material Sidecar Importer Fixture Harness Proof Plan",
    "texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.md",
    "texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.v1.json",
    "importerFixtureHarnessStatus=texture-mesh-material-sidecar-importer-fixture-harness-proof-plan-complete-static-importer-harness-contract-not-runtime-proof",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Fixture Harness Materialization Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-fixture-harness-materialization-proof-plan",
    "sourceFixtureMatrixStatus=texture-mesh-material-sidecar-rebuild-fixture-matrix-complete-static-fixture-matrix-not-runtime-proof",
    "harnessDimensionCount=7",
    "harnessCaseCount=8",
    "importerAssertionGroupCount=8",
    "publicSyntheticFixtureCount=8",
    "Completed Texture / Mesh Material Sidecar Rebuild Fixture Matrix Proof Plan",
    "texture-mesh-material-sidecar-rebuild-fixture-matrix-proof.md",
    "texture-mesh-material-sidecar-rebuild-fixture-matrix.v1.json",
    "fixtureMatrixStatus=texture-mesh-material-sidecar-rebuild-fixture-matrix-complete-static-fixture-matrix-not-runtime-proof",
    "selectedNextSlice=Texture / Mesh Material Sidecar Importer Fixture Harness Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-importer-fixture-harness-proof-plan",
    "matrixDimensionCount=7",
    "fixtureCaseCount=8",
    "uniqueModelTextureRefUnion=213",
    "familyUniqueRefsAreNotAdditive=true",
    "embeddedDuplicateOutputSurplusRows=32",
    "publicEdgeCaseIdCount=2",
    "Completed Texture / Mesh Material Sidecar Rebuild Contract Extension Proof Plan",
    "texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.md",
    "texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.v1.json",
    "contractExtensionStatus=texture-mesh-material-sidecar-rebuild-contract-extension-complete-static-contract-extension-not-runtime-proof",
    "selectedNextSlice=Texture / Mesh Material Sidecar Rebuild Fixture Matrix Proof Plan",
    "selectedNextScope=texture-mesh-material-sidecar-rebuild-fixture-matrix-proof-plan",
    "contractVocabularyTermCount=14",
    "ambiguousCatalogRefs=1",
    "embeddedDuplicateOutputBoundaryRows=32",
    "contractFalseGuardCount=39",
    "contractZeroCounterCount=33",
    "Completed Static-To-Proof Rebuild Transition Post-PhysicsScript Fixture Next Safe Slice Selection Refresh Proof Plan",
    "static-to-proof-post-physics-script-fixture-next-safe-slice-selection-refresh.md",
    "static-to-proof-post-physics-script-fixture-next-safe-slice-selection-refresh.v1.json",
    "selectionRefreshStatus=static-to-proof-post-physics-script-fixture-next-safe-slice-selection-refresh-complete-texture-mesh-material-sidecar-contract-extension-selected",
    "selectedChildLane=Texture / Mesh Material Sidecar Rebuild Contract Extension Proof Plan",
    "selectedChildScope=texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan",
    "consultCount=2",
    "candidateCount=4",
    "selectedCandidateRank=1",
    "selectedSourceProofCount=5",
    "completedPhysicsScriptFixtureFamilyCount=9",
    "remainingPhysicsScriptFixtureFamilyCount=0",
    "materialSidecarModelRowsWithRefs=352/352",
    "materialSidecarUniqueRefs=213",
    "materialSidecarFiles=213",
    "materialSidecarMissingRefs=0",
    "catalogMissingRefs=0",
    "selectionFalseGuardCount=45",
    "selectionZeroCounterCount=35",
    "latestGhidraBackupClass=verified-static-backup-redacted",
    "Completed PhysicsScript Unit Rebuild Fixture Proof Plan",
    "physics-script-unit-rebuild-fixture-proof-plan.md",
    "physics-script-unit-rebuild-fixture-proof-plan.v1.json",
    "physics-script-unit-rebuild-fixture-proof-plan-complete-static-unit-value-interface-fixture-not-runtime-proof",
    "selectedNextSlice=PhysicsScript Fixture Family Completion Rollup Proof Plan",
    "selectedNextScope=physics-script-fixture-family-completion-rollup-proof-plan",
    "selectedFixtureFamily=unit",
    "selectedFixturePath=unit-selected-value-id-interface-static-fixture",
    "selectedValueIds=7/8/20/21/22/25/60/61",
    "factoryOnlyValueIds=20/25",
    "selectedUnselectedObservedValueIdCount=48",
    "selectedMixedPayloadShapeValueIds=none",
    "unselectedObservedValueIds=1/2/3/5/6/9/10/11/12/13/14/18/23/27/28/29/30/31/32/33/36/38/39/40/41/42/43/44/45/46/47/48/50/51/52/53/54/55/56/57/58/62/63/65/66/67/68/70",
    "CUnitStatement__LoadFromMemBuffer",
    "CPhysicsUnitValueList__LoadFromMemBuffer",
    "CUnitStatement__CreateUnitAndRecurse",
    "CUnitAI__CreateAndRegisterByName",
    "DAT_008553fc",
    "Completed PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan",
    "physics-script-weapon-mode-rebuild-fixture-proof-plan.md",
    "physics-script-weapon-mode-rebuild-fixture-proof-plan.v1.json",
    "physics-script-weapon-mode-rebuild-fixture-proof-plan-complete-static-weapon-mode-value-interface-fixture-not-runtime-proof",
    "selectedNextSlice=PhysicsScript Unit Rebuild Fixture Proof Plan",
    "selectedNextScope=physics-script-unit-rebuild-fixture-proof-plan",
    "selectedFixtureFamily=weapon-mode",
    "selectedFixturePath=weapon-mode-selected-value-id-interface-static-fixture",
    "selectedValueIds=2/6/15/18/24/28/31/34/36",
    "factoryOnlyValueIds=15/36",
    "selectedUnselectedObservedValueIdCount=25",
    "selectedMixedPayloadShapeValueIds=2/24",
    "unselectedObservedValueIds=1/3/4/5/8/9/10/11/12/13/14/16/17/19/20/21/22/23/26/27/29/30/32/33/35",
    "CWeaponModeStatement__LoadFromMemBuffer",
    "CPhysicsWeaponModeValueList__LoadFromMemBuffer",
    "CWeaponModeStatement__CreateWeaponModeAndRecurse",
    "DAT_008553ec",
    "Completed PhysicsScript Round Rebuild Fixture Proof Plan",
    "physics-script-round-rebuild-fixture-proof-plan.md",
    "physics-script-round-rebuild-fixture-proof-plan.v1.json",
    "physics-script-round-rebuild-fixture-proof-plan-complete-static-round-value-interface-fixture-not-runtime-proof",
    "selectedNextSlice=PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan",
    "selectedNextScope=physics-script-weapon-mode-rebuild-fixture-proof-plan",
    "selectedFixtureFamily=round",
    "selectedFixturePath=round-selected-value-id-interface-static-fixture",
    "selectedValueIds=4/8/9/24/33/35/36",
    "selectedUnselectedObservedValueIdCount=26",
    "selectedMixedPayloadShapeValueIds=8/9",
    "unselectedObservedValueIds=1/2/3/5/6/10/11/12/13/14/15/16/17/18/19/22/23/26/27/28/29/30/31/32/37/38",
    "CRoundStatement__LoadFromMemBuffer",
    "CPhysicsRoundValueList__LoadFromMemBuffer",
    "CRoundStatement__CreateRoundAndRecurse",
    "DAT_008553f0",
    "Completed PhysicsScript Weapon Rebuild Fixture Proof Plan",
    "physics-script-weapon-rebuild-fixture-proof-plan.md",
    "physics-script-weapon-rebuild-fixture-proof-plan.v1.json",
    "physics-script-weapon-rebuild-fixture-proof-plan-complete-static-weapon-value-interface-fixture-not-runtime-proof",
    "selectedNextSlice=PhysicsScript Round Rebuild Fixture Proof Plan",
    "selectedNextScope=physics-script-round-rebuild-fixture-proof-plan",
    "selectedFixtureFamily=weapon",
    "selectedFixturePath=weapon-selected-value-id-interface-static-fixture",
    "selectedValueIds=1/4/5/14",
    "selectedObservedValueIdCount=4",
    "selectedFactoryOnlyValueIdCount=0",
    "selectedUnselectedObservedValueIdCount=10",
    "selectedPayloadShapeCaseCount=5",
    "selectedMixedPayloadShapeValueIds=1",
    "unselectedObservedValueIds=2/3/6/7/8/9/10/11/12/13",
    "CWeaponStatement__LoadFromMemBuffer",
    "CPhysicsWeaponValueList__LoadFromMemBuffer",
    "CWeaponStatement__CreateWeaponAndRecurse",
    "DAT_008553e8",
    "Completed PhysicsScript Component Rebuild Fixture Proof Plan",
    "physics-script-component-rebuild-fixture-proof-plan.md",
    "physics-script-component-rebuild-fixture-proof-plan.v1.json",
    "physics-script-component-rebuild-fixture-proof-plan-complete-static-component-value-interface-fixture-not-runtime-proof",
    "selectedNextSlice=PhysicsScript Weapon Rebuild Fixture Proof Plan",
    "selectedFixtureFamily=component",
    "selectedFixturePath=component-selected-value-id-interface-static-fixture",
    "selectedValueIds=1/3/6/7/8/9/10/11/12/13/15/16/17/18/20/21/22/23/24/25",
    "selectedObservedValueIdCount=16",
    "selectedFactoryOnlyValueIdCount=4",
    "selectedUnselectedObservedValueIdCount=4",
    "selectedPayloadShapeCaseCount=16",
    "factoryOnlyValueIds=10/16/17/24",
    "unselectedObservedValueIds=2/4/14/19",
    "Completed PhysicsScript Feature Rebuild Fixture Proof Plan",
    "physics-script-feature-rebuild-fixture-proof-plan.md",
    "physics-script-feature-rebuild-fixture-proof-plan.v1.json",
    "physics-script-feature-rebuild-fixture-proof-plan-complete-static-feature-value-interface-fixture-not-runtime-proof",
    "selectedNextSlice=PhysicsScript Component Rebuild Fixture Proof Plan",
    "selectedFixtureFamily=feature",
    "selectedFixturePath=feature-selected-value-id-interface-static-fixture",
    "selectedValueIds=1/2/3/4/5/6/7",
    "selectedObservedValueIdCount=5",
    "selectedFactoryOnlyValueIdCount=2",
    "selectedUnselectedObservedValueIdCount=0",
    "selectedPayloadShapeCaseCount=6",
    "selectedMixedPayloadShapeValueIds=2",
    "meshObservedOwnedStringShapeCount=40",
    "meshObservedThreeScalarShapeCount=2",
    "factoryOnlyValueIds=5/7",
    "Completed PhysicsScript Hazard Rebuild Fixture Proof Plan",
    "physics-script-hazard-rebuild-fixture-proof-plan.md",
    "physics-script-hazard-rebuild-fixture-proof-plan.v1.json",
    "physics-script-hazard-rebuild-fixture-proof-plan-complete-static-hazard-value-interface-fixture-not-runtime-proof",
    "selectedNextSlice=PhysicsScript Feature Rebuild Fixture Proof Plan",
    "selectedFixtureFamily=hazard",
    "selectedFixturePath=hazard-selected-value-id-interface-static-fixture",
    "selectedValueIds=1/2/3/4",
    "selectedObservedValueIdCount=3",
    "selectedFactoryOnlyValueIdCount=1",
    "selectedPayloadShapeCaseCount=4",
    "selectedMixedPayloadShapeValueIds=2",
    "effectObservedOwnedStringShapeCount=3",
    "effectObservedThreeScalarShapeCount=1",
    "factoryOnlyValueIds=4",
    "Completed PhysicsScript Spawner Rebuild Fixture Proof Plan",
    "physics-script-spawner-rebuild-fixture-proof-plan.md",
    "physics-script-spawner-rebuild-fixture-proof-plan.v1.json",
    "physics-script-spawner-rebuild-fixture-proof-plan-complete-static-spawner-value-interface-fixture-not-runtime-proof",
    "selectedNextSlice=PhysicsScript Hazard Rebuild Fixture Proof Plan",
    "selectedFixtureFamily=spawner",
    "selectedFixturePath=spawner-selected-value-id-interface-static-fixture",
    "selectedValueIds=1/2/3/4/5/6/7/8/9/10/11/12/13/14",
    "selectedObservedValueIdCount=10",
    "selectedFactoryOnlyValueIdCount=4",
    "selectedUnselectedObservedValueIdCount=0",
    "selectedPayloadShapeCaseCount=11",
    "selectedMixedPayloadShapeValueIds=1",
    "factoryOnlyValueIds=4/5/10/13",
    "Completed PhysicsScript Explosion Rebuild Fixture Proof Plan",
    "physics-script-explosion-rebuild-fixture-proof-plan.md",
    "physics-script-explosion-rebuild-fixture-proof-plan.v1.json",
    "physics-script-explosion-rebuild-fixture-proof-plan-complete-static-explosion-value-interface-fixture-not-runtime-proof",
    "selectedNextSlice=PhysicsScript Spawner Rebuild Fixture Proof Plan",
    "selectedPayloadShapeCaseCount=15",
    "selectedMixedPayloadShapeValueIds=10",
    "soundObservedOwnedStringShapeCount=79",
    "soundObservedThreeScalarShapeCount=7",
    "deferredFactoryValueIds=14",
    "falseGuardCount=40",
    "zeroCounterCount=26",
    "publicLeakCheck=PASS",
    "Completed PhysicsScript Rebuild Fixture Selection Proof Plan",
    "physics-script-rebuild-fixture-selection.md",
    "physics-script-rebuild-fixture-selection.v1.json",
    "fixtureSelectionStatus=physics-script-rebuild-fixture-selection-complete-explosion-selected",
    "selectedFixtureFamily=explosion",
    "selectedChildLane=PhysicsScript Explosion Rebuild Fixture Proof Plan",
    "selectedValueInterfaceRowCount=14",
    "selectedValueIds=1/2/3/4/5/6/7/8/9/10/11/12/13/15",
    "selectedFactoryOnlyValueIdCount=0",
    "selectedUnselectedObservedValueIdCount=0",
    "falseGuardCount=37",
    "zeroCounterCount=23",
    "Completed PhysicsScript Rebuild Interface Rollup Proof Plan",
    "physics-script-rebuild-interface-rollup.md",
    "physics-script-rebuild-interface-rollup.v1.json",
    "rollupStatus=physics-script-rebuild-interface-rollup-complete-static-interface-vocabulary-not-runtime-proof",
    "physicsScriptRebuildInterfaceRollupStatus=physics-script-rebuild-interface-rollup-complete-static-interface-vocabulary-not-runtime-proof",
    "selectedNextSlice=PhysicsScript Rebuild Fixture Selection Proof Plan",
    "selectedSourceProofCount=5",
    "sourceSchemaCount=3",
    "sourceMirrorPairCount=8",
    "topLevelFamilyCount=9",
    "valueInterfaceRowCount=87",
    "unselectedObservedRowCount=113",
    "recommendedNextFixtureFamily=explosion",
    "Completed PhysicsScript Value-ID Semantic Crosswalk Proof Plan",
    "physics-script-value-id-semantic-crosswalk-proof-plan.md",
    "physics-script-value-id-semantic-crosswalk.v1.json",
    "crosswalkStatus=physics-script-value-id-semantic-crosswalk-complete-bounded-static-crosswalk-not-runtime-proof",
    "selectedNextSlice=PhysicsScript Rebuild Interface Rollup Proof Plan",
    "boundedCrosswalkRowCount=87",
    "observedSelectedRowCount=72",
    "factoryOnlySelectedRowCount=15",
    "completeValueIdSemanticsProven=false",
    "all185PairsSemanticallyNamed=false",
    "Completed PhysicsScript Scalar/String Value Decoder Fixture Proof Plan",
    "physics-script-scalar-string-value-decoder-fixture-proof-plan.md",
    "physics-script-scalar-string-value-decoder-fixture-proof-plan.v1.json",
    "fixtureStatus=physics-script-scalar-string-value-decoder-fixture-complete-static-decode-roundtrip-not-runtime-proof",
    "selectedNextSlice=PhysicsScript Value-ID Semantic Crosswalk Proof Plan",
    "fixtureClassCounts=3912/1737/361/132/661",
    "syntheticFixtureCaseCount=13",
    "Completed PhysicsScript Semantic Value-Field Schema Ledger Proof Plan",
    "physics-script-semantic-value-field-schema-ledger-proof-plan.md",
    "physics-script-semantic-value-field-schema-ledger.v1.json",
    "ledgerStatus=physics-script-semantic-value-field-schema-ledger-complete-static-semantic-ledger-not-runtime-proof",
    "selectedNextSlice=PhysicsScript Scalar/String Value Decoder Fixture Proof Plan",
    "semanticBucketCount=10",
    "Completed Static-To-Proof Rebuild Transition Post-Command-Effect Fixture Next Safe Slice Selection Refresh Proof Plan",
    "static-to-proof-post-command-effect-fixture-next-safe-slice-selection-refresh.md",
    "static-to-proof-post-command-effect-fixture-next-safe-slice-selection-refresh.v1.json",
    "selectionRefreshStatus=static-to-proof-post-command-effect-fixture-next-safe-slice-selection-refresh-complete-physics-script-semantic-value-field-schema-ledger-selected",
    "selectedChildLane=PhysicsScript Semantic Value-Field Schema Ledger Proof Plan",
    "selectedChildScope=physics-script-semantic-value-field-schema-ledger-proof-plan",
    "completedMissionScriptFixtureFamilyCount=9",
    "remainingMissionScriptFixtureFamilyCount=0",
    "physicsScriptTopLevelStatementCount=777",
    "physicsScriptValueListNodeCount=6803",
    "physicsScriptStatementValuePairCount=185",
    "physicsScriptRawValuePayloadBytesPreserved=73796",
    "Completed MissionScript Command-Effect Fixture Family Completion Rollup Proof Plan",
    "missionscript-command-effect-fixture-family-completion-rollup-proof-plan.md",
    "missionscript-command-effect-fixture-family-completion-rollup-proof-plan.v1.json",
    "missionScriptCommandEffectFixtureFamilyCompletionRollupProofPlanStatus=missionscript-command-effect-fixture-family-completion-rollup-proof-plan-complete-nine-family-static-fixture-rollup-not-runtime-proof",
    "selectedNextSlice=Static-To-Proof Rebuild Transition Post-Command-Effect Fixture Next Safe Slice Selection Refresh Proof Plan",
    "completedFixtureFamilyCount=9",
    "remainingFixtureFamilyCount=0",
    "heterogeneousFixtureCaseCount=114",
    "descriptorRecordCount=52",
    "uniqueDescriptorIndexCount=48",
    "runtimeExecution=false",
    "ghidraMutation=false",
    "godotWork=false",
    "rebuildImplementation=false",
    "Completed MissionScript Player-State / Score Command-Effect Fixture Proof Plan",
    "missionscript-player-state-score-command-effect-fixture-proof-plan.md",
    "missionscript-player-state-score-command-effect-fixture-proof-plan.v1.json",
    "missionScriptPlayerStateScoreCommandEffectFixtureProofPlanStatus=missionscript-player-state-score-command-effect-fixture-proof-plan-complete-static-player-state-score-context-table-not-runtime-proof",
    "selectedFixtureFamily=player-state-score",
    "selectedFixturePath=player-state-score-descriptor-alias-boundary-table",
    "selectedNextSlice=MissionScript Command-Effect Fixture Family Completion Rollup Proof Plan",
    "descriptorContextCaseCount=3",
    "staticContextFixtureCaseCount=3",
    "deterministicFixtureCaseCount=3",
    "aliasBoundaryCaseCount=1",
    "rawLabelOnlyCaseCount=2",
    "handlerBodyProvenCount=0",
    "directNonCommentLooseMslRows=25",
    "falseGuardCount=53",
    "zeroCounterCount=39",
    "publicLeakCheck=PASS",
    "Completed MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan",
    "missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan.md",
    "missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan.v1.json",
    "missionScriptThingValueEngineHelperCommandEffectFixtureProofPlanStatus=missionscript-thing-value-engine-helper-command-effect-fixture-proof-plan-complete-static-thing-engine-dispatch-table-not-runtime-proof",
    "selectedFixtureFamily=thing-value-engine-helper",
    "selectedFixturePath=thing-vfunc-engine-unit-helper-dispatch-table",
    "selectedNextSlice=MissionScript Player-State / Score Command-Effect Fixture Proof Plan",
    "handlerDispatchCaseCount=6",
    "thingVfuncDispatchCaseCount=3",
    "engineHelperDispatchCaseCount=2",
    "unitHelperDispatchCaseCount=1",
    "directNonCommentLooseMslRows=27",
    "falseGuardCount=58",
    "zeroCounterCount=44",
    "publicLeakCheck=PASS",
    "Completed MissionScript HUD / Display Command-Effect Fixture Proof Plan",
    "missionscript-hud-display-command-effect-fixture-proof-plan.md",
    "missionscript-hud-display-command-effect-fixture-proof-plan.v1.json",
    "missionScriptHudDisplayCommandEffectFixtureProofPlanStatus=missionscript-hud-display-command-effect-fixture-proof-plan-complete-static-hud-variable-display-effect-table-not-runtime-proof",
    "selectedFixtureFamily=hud-variable-display",
    "selectedFixturePath=hud-part-variable-display-effect-table",
    "selectedNextSlice=MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan",
    "plannedHudPartToggleCaseCount=6",
    "plannedVariableLifecycleCaseCount=6",
    "deterministicFixtureCaseCount=12",
    "hudCommandStepCount=12",
    "variableCommandStepCount=18",
    "totalStaticCommandStepCount=30",
    "falseGuardCount=50",
    "zeroCounterCount=37",
    "publicLeakCheck=PASS",
    "Completed MissionScript Message/Audio Command-Effect Fixture Proof Plan",
    "missionscript-message-audio-command-effect-fixture-proof-plan.md",
    "missionscript-message-audio-command-effect-fixture-proof-plan.v1.json",
    "missionScriptMessageAudioCommandEffectFixtureProofPlanStatus=missionscript-message-audio-command-effect-fixture-proof-plan-complete-static-message-audio-console-effect-table-not-runtime-proof",
    "selectedFixtureFamily=message-audio-console",
    "selectedFixturePath=message-audio-queue-console-effect-table",
    "selectedNextSlice=MissionScript HUD / Display Command-Effect Fixture Proof Plan",
    "plannedMessageQueueCaseCount=5",
    "plannedConsoleTextCaseCount=1",
    "deterministicFixtureCaseCount=6",
    "falseGuardCount=48",
    "zeroCounterCount=38",
    "publicLeakCheck=PASS",
    "Completed MissionScript Objective/Outcome Command-Effect Fixture Proof Plan",
    "missionscript-objective-outcome-command-effect-fixture-proof-plan.md",
    "missionscript-objective-outcome-command-effect-fixture-proof-plan.v1.json",
    "missionScriptObjectiveOutcomeCommandEffectFixtureProofPlanStatus=missionscript-objective-outcome-command-effect-fixture-proof-plan-complete-static-objective-outcome-effect-table-not-runtime-proof",
    "selectedFixtureFamily=objective-outcome",
    "selectedFixturePath=objective-state-and-level-result-effect-table",
    "selectedNextSlice=MissionScript Message/Audio Command-Effect Fixture Proof Plan",
    "plannedObjectiveEffectCaseCount=4",
    "plannedOutcomeEffectCaseCount=3",
    "deterministicFixtureCaseCount=7",
    "falseGuardCount=43",
    "zeroCounterCount=32",
    "publicLeakCheck=PASS",
    "Completed MissionScript Cutscene Pan-Camera / Position Command-Effect Deterministic Fixture Proof Plan",
    "Completed MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof",
    "missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness-proof.md",
    "missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness.v1.json",
    "missionscript-goodie-state-save-appcore-copied-baseline-boundary-corpus-harness-complete-copied-real-baseline-boundary-corpus-not-runtime-proof",
    "selectedNextSlice=MissionScript Command-Effect Post-Goodie Selection Refresh Proof Plan",
    "copiedArtifactCount=12",
    "sampleBoundaryArtifactCount=8",
    "storageVectorCopiedBaselineReadCaseCount=300",
    "displayableCopiedBaselineRoundTripCaseCount=233",
    "reservedCopiedBaselineRejectionCaseCount=67",
    "boundaryStateCopiedBaselineMatrixCaseCount=32",
    "copiedBaselineBoundaryCorpusCaseCount=632",
    "allDisplayableCopiedBaselineRoundTrip=true",
    "allReservedCopiedBaselineRejectionsLeaveBufferUnchanged=true",
    "Completed MissionScript Goodie State / Save AppCore Boundary-Corpus Fixture Matrix Proof",
    "missionscript-goodie-state-save-appcore-boundary-corpus-fixture-matrix-proof.md",
    "missionscript-goodie-state-save-appcore-boundary-corpus-fixture-matrix.v1.json",
    "missionScriptGoodieStateSaveAppCoreBoundaryCorpusFixtureMatrixStatus=missionscript-goodie-state-save-appcore-boundary-corpus-fixture-matrix-complete-651-appcore-cases-not-runtime-proof",
    "selectedNextSlice=MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof Plan",
    "xunitTestCaseCount=651",
    "storageVectorCaseCount=300",
    "displayableRoundTripCaseCount=233",
    "reservedMutationRejectionCaseCount=67",
    "displayableBoundaryStateMatrixCaseCount=32",
    "invalidRawStateCaseCount=3",
    "boundaryScriptIndices=1,2,51,53,68,71,232,233",
    "boundaryOffsets=0x1F46,0x1F4A,0x200E,0x2016,0x2052,0x205E,0x22E2,0x22E6",
    "allStorageScriptIndicesVectorized=true",
    "allReservedScriptIndicesRejected=true",
    "allBoundaryStatesRoundTrip=true",
    "Completed MissionScript Goodie State / Save Runtime-Proof Readiness Gate",
    "missionscript-goodie-state-save-runtime-proof-readiness-gate.md",
    "missionscript-goodie-state-save-runtime-proof-readiness-gate.v1.json",
    "missionScriptGoodieStateSaveRuntimeProofReadinessGateStatus=missionscript-goodie-state-save-runtime-proof-readiness-gate-complete-runtime-deferred-no-launch",
    "selectedNextSlice=MissionScript Goodie State / Save AppCore Boundary-Corpus Fixture Matrix Proof Plan",
    "runtimeObservationReadyNow=false",
    "runtimeDeferred=true",
    "deferReason=explicit-runtime-observation-arm-and-private-output-review-absent-continue-non-runtime-appcore-boundary-corpus-fixture-proof",
    "explicitRuntimeObservationArmPresent=false",
    "operatorPrivateOutputReviewAvailable=false",
    "runtimeObservationRows=0",
    "Completed MissionScript Goodie State / Save AppCore Copied-Baseline Codec Harness Proof",
    "missionscript-goodie-state-save-appcore-copied-baseline-codec-harness-proof.md",
    "missionscript-goodie-state-save-appcore-copied-baseline-codec-harness.v1.json",
    "missionscript-goodie-state-save-appcore-copied-baseline-codec-harness-complete-appcore-copied-real-baseline-byte-preservation-not-runtime-proof",
    "selectedNextSlice=MissionScript Goodie State / Save Runtime-Proof Readiness Gate Plan",
    "toolProjectPath=tools/MissionScriptGoodieStateSaveCodecHarness/MissionScriptGoodieStateSaveCodecHarness.csproj",
    "appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptGoodieStateSaveCodec.cs",
    "interfaceKind=AppCore Goodie codec applied by proof-only copied-baseline harness",
    "manualGoodieDwordWriteInHarness=false",
    "targetReadbackMismatchCount=0",
    "roundtripToBaselineDiffCount=0",
    "Completed MissionScript Goodie State / Save Clean-Room Codec Interface Proof",
    "missionscript-goodie-state-save-clean-room-codec-interface-proof.md",
    "missionscript-goodie-state-save-clean-room-codec-interface-proof.v1.json",
    "missionScriptGoodieStateSaveCleanRoomCodecInterfaceProofStatus=missionscript-goodie-state-save-clean-room-codec-interface-proof-complete-pure-appcore-buffer-codec-not-runtime-proof",
    "selectedNextSlice=MissionScript Goodie State / Save AppCore Copied-Baseline Codec Harness Proof Plan",
    "appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptGoodieStateSaveCodec.cs",
    "appCoreTestPath=OnslaughtCareerEditor.AppCore.Tests/MissionScriptGoodieStateSaveCodecTests.cs",
    "interfaceKind=pure AppCore in-memory buffer codec",
    "appCoreCodecUsed=true",
    "appCorePatcherUsed=false",
    "scriptIndexing=1-based",
    "mappingFormula=save_goodie_index = script_index - 1",
    "offsetFormula=0x1F46 + (script_index - 1) * 4",
    "reservedWritePolicy=displayable-only-default-rejects-reserved",
    "xunitTestCaseCount=249",
    "testMethodCount=7",
    "allDisplayableScriptIndexCaseCount=233",
    "invalidMixedBatchLeavesBufferUnchanged=true",
    "fileIoPerformed=false",
    "copiedFileMutationPerformed=false",
    "sourceBaselineRead=false",
    "privateArtifactMaterialized=false",
    "Completed MissionScript Goodie State / Save Copied-Baseline Byte-Diff Fixture Proof",
    "missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof.md",
    "missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof.v1.json",
    "missionScriptGoodieStateSaveCopiedBaselineByteDiffFixtureProofStatus=missionscript-goodie-state-save-copied-baseline-byte-diff-fixture-proof-complete-copied-real-baseline-appcore-byte-diff-not-runtime-proof",
    "appCoreService=BesFilePatcher.PatchGoodieStates",
    "patcherInputIndexClass=zero-based-save-goodie-index",
    "scriptIndexSaveIndexDisambiguated=true",
    "scriptIndices=1,51,53,68,71,233",
    "saveGoodieIndices=0,50,52,67,70,232",
    "changedOffsets=0x1F46,0x200E,0x2016,0x2052,0x205E,0x22E6",
    "roundtripToBaselineDiffCount=0",
    "Completed MissionScript Goodie State / Save Command-Effect Fixture Proof Plan",
    "missionscript-goodie-state-save-command-effect-fixture-proof-plan.md",
    "missionscript-goodie-state-save-command-effect-fixture-proof-plan.v1.json",
    "missionScriptGoodieStateSaveCommandEffectFixtureProofPlanStatus=missionscript-goodie-state-save-command-effect-fixture-proof-plan-complete-static-offset-state-fixture-plan-not-runtime-proof",
    "selectedFixtureFamily=goodie-state-save",
    "selectedFixturePath=goodie-state-save-index-state-byte-preservation",
    "selectedNextSlice=MissionScript Goodie State / Save Copied-Baseline Byte-Diff Fixture Proof Plan",
    "plannedGoodieFixtureCaseCount=43",
    "descriptorBoundaryCaseCount=5",
    "scriptIndexOffsetCaseCount=12",
    "stateValueCaseCount=4",
    "corpusBoundaryCaseCount=9",
    "appCoreCopiedSaveSafetyCaseCount=13",
    "Completed MissionScript Vector/Range Command-Effect Deterministic Helper Fixture Proof Plan",
    "missionscript-vector-range-deterministic-helper-fixture-proof-plan.md",
    "missionscript-vector-range-deterministic-helper-fixture-proof-plan.v1.json",
    "missionScriptVectorRangeDeterministicHelperFixtureProofPlanStatus=missionscript-vector-range-deterministic-helper-fixture-proof-plan-complete-pure-helper-fixture-not-runtime-proof",
    "plannedVectorAssertionCount=16",
    "plannedHelperAssertionCount=28",
    "deterministicHelperCaseCount=28",
    "nonFiniteFloatBehaviorDeferred=true",
    "Completed Static-To-Proof Rebuild Transition Next Safe Slice Selection Refresh Proof Plan",
    "static-to-proof-next-safe-slice-selection-refresh.md",
    "static-to-proof-next-safe-slice-selection-refresh.v1.json",
    "selectionRefreshStatus=static-to-proof-next-safe-slice-selection-refresh-complete-vector-range-deterministic-helper-fixture-selected",
    "selectedChildLane=MissionScript Vector/Range Command-Effect Deterministic Helper Fixture Proof Plan",
    "completedSlotSaveChainCount=8",
    "selectionFalseGuardCount=31",
    "selectionZeroCounterCount=26",
    "Completed Save / Options Byte-Preservation AppCore Fixture Matrix Proof Plan",
    "save-options-byte-preservation-appcore-fixture-matrix-proof.md",
    "save-options-byte-preservation-appcore-fixture-matrix.v1.json",
    "saveOptionsBytePreservationAppCoreFixtureMatrixStatus=save-options-byte-preservation-appcore-fixture-matrix-complete-copied-real-baseline-services-not-runtime-proof",
    "selectedNextSlice=Static-To-Proof Rebuild Transition Next Safe Slice Selection Refresh Proof Plan",
    "fixtureFamilyCount=8",
    "appCoreFixtureCaseCount=36",
    "unexpectedDiffCount=0",
    "legacyTrapHitCountNonSlot=0",
    "Completed Save / Options Byte-Preservation Runtime-Proof Readiness Gate",
    "save-options-byte-preservation-runtime-proof-readiness-gate.md",
    "save-options-byte-preservation-runtime-proof-readiness-gate.v1.json",
    "saveOptionsBytePreservationRuntimeProofReadinessGateStatus=save-options-byte-preservation-runtime-proof-readiness-gate-complete-runtime-deferred-no-launch",
    "selectedNextSlice=Save / Options Byte-Preservation AppCore Fixture Matrix Proof Plan",
    "runtimeObservationReadyNow=false",
    "runtimeDeferred=true",
    "explicitRuntimeObservationArmPresent=false",
    "beLaunch=false",
    "runtimeObservationRows=0",
    "Completed Save / Options Byte-Preservation AppCore Implementation Contract Proof",
    "save-options-byte-preservation-appcore-implementation-contract-proof.md",
    "save-options-byte-preservation-appcore-implementation-contract.v1.json",
    "saveOptionsBytePreservationAppCoreImplementationContractStatus=save-options-byte-preservation-appcore-implementation-contract-complete-copied-real-baseline-services-not-runtime-proof",
    "selectedNextSlice=Save / Options Byte-Preservation Runtime-Proof Readiness Gate Plan",
    "appCoreServiceProofCaseCount=8",
    "SaveEditorService.PatchSave",
    "ConfigurationEditorService.PatchConfiguration",
    "BesFilePatcher.AnalyzeSave",
    "MissionScriptSlotBitsetSaveCodec",
    "runtimeSaveLoadProof=false",
    "runtimeDefaultOptionsProof=false",
    "Completed MissionScript Slot Bitset/Save AppCore Copied-Baseline Boundary Corpus Harness Proof",
    "missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness-proof.md",
    "missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness.v1.json",
    "slotBitsetSaveAppCoreCopiedBaselineBoundaryCorpusHarnessStatus=missionscript-slot-bitset-save-appcore-copied-baseline-boundary-corpus-harness-complete-copied-real-baseline-boundary-corpus-not-runtime-proof",
    "selectedNextSlice=Save / Options Byte-Preservation AppCore Implementation Contract Proof Plan",
    "copiedArtifactCount=6",
    "sampleBoundaryArtifactCount=4",
    "singleSlotCopiedBaselineRoundTripCaseCount=256",
    "copiedBaselineHarnessCaseCount=264",
    "allBoundaryPairSetXorMatchesBaselineState=true",
    "sourceBaselineRead=true",
    "privateArtifactMaterialized=true",
    "Completed MissionScript Slot Bitset/Save AppCore Boundary-Slot Corpus Proof",
    "missionscript-slot-bitset-save-appcore-boundary-slot-corpus-proof.md",
    "missionscript-slot-bitset-save-appcore-boundary-slot-corpus.v1.json",
    "slotBitsetSaveAppCoreBoundarySlotCorpusStatus=missionscript-slot-bitset-save-appcore-boundary-slot-corpus-complete-273-appcore-cases-not-runtime-proof",
    "selectedNextSlice=MissionScript Slot Bitset/Save AppCore Copied-Baseline Boundary Corpus Harness Proof Plan",
    "xunitTestCaseCount=273",
    "singleSlotRoundTripCaseCount=256",
    "boundaryPairMaskCaseCount=8",
    "boundaryVectorSlots=63,64,224,255",
    "crossDwordMaskRejected=true",
    "slot256Rejected=true",
    "Completed MissionScript Slot Bitset/Save Runtime-Proof Readiness Gate",
    "missionscript-slot-bitset-save-runtime-proof-readiness-gate.md",
    "missionscript-slot-bitset-save-runtime-proof-readiness-gate.v1.json",
    "slotBitsetSaveRuntimeProofReadinessGateStatus=missionscript-slot-bitset-save-runtime-proof-readiness-gate-complete-runtime-deferred-no-launch",
    "selectedNextSlice=MissionScript Slot Bitset/Save AppCore Boundary-Slot Corpus Proof Plan",
    "runtimeReadinessGateComplete=true",
    "runtimeObservationReadyNow=false",
    "runtimeDeferred=true",
    "explicitRuntimeObservationArmPresent=false",
    "beLaunch=false",
    "runtimeObservationRows=0",
    "Completed MissionScript Slot Bitset/Save AppCore Copied-Baseline Codec Harness Proof",
    "missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness-proof.md",
    "missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness.v1.json",
    "slotBitsetSaveAppCoreCopiedBaselineCodecHarnessStatus=missionscript-slot-bitset-save-appcore-copied-baseline-codec-harness-complete-appcore-copied-real-baseline-byte-preservation-not-runtime-proof",
    "selectedNextSlice=MissionScript Slot Bitset/Save Runtime-Proof Readiness Gate Plan",
    "toolProjectPath=tools/MissionScriptSlotBitsetSaveHarness/MissionScriptSlotBitsetSaveHarness.csproj",
    "appCoreCodecUsed=true",
    "manualSlotDwordWriteInHarness=false",
    "clearToBaselineDiffCount=0",
    "Completed MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof",
    "missionscript-slot-bitset-save-clean-room-codec-interface-proof.md",
    "missionscript-slot-bitset-save-clean-room-codec-interface.v1.json",
    "slotBitsetSaveCleanRoomCodecInterfaceStatus=missionscript-slot-bitset-save-clean-room-codec-interface-complete-appcore-pure-buffer-contract-not-runtime-proof",
    "selectedNextSlice=MissionScript Slot Bitset/Save AppCore Copied-Baseline Codec Harness Proof Plan",
    "appCoreCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs",
    "interfaceOperationCount=8",
    "xunitTestCaseCount=9",
    "Completed MissionScript Slot Bitset/Save Copied-File Byte-Diff Proof",
    "slotBitsetSaveCopiedFileByteDiffStatus=missionscript-slot-bitset-save-copied-file-byte-diff-complete-copied-real-baseline-not-runtime-proof",
    "observedDwordXorMask=0x60000000",
    "baselineToSetChangedOffsets=0x2411",
    "clearToBaselineDiffCount=0",
    "Completed MissionScript Slot Bitset/Save Deterministic Codec Proof Plan",
    "missionscript-slot-bitset-save-deterministic-codec-proof-plan.md",
    "missionscript-slot-bitset-save-deterministic-codec-proof-plan.v1.json",
    "slotBitsetSaveDeterministicCodecProofPlanStatus=missionscript-slot-bitset-save-deterministic-codec-proof-plan-complete-pure-codec-not-runtime-proof",
    "selectedNextSlice=MissionScript Slot Bitset/Save Copied-File Byte-Diff Proof Plan",
    "usedSlotDwords=8",
    "reservedSlotStorageDwords=32",
    "Completed MissionScript Slot Bitset/Save Rebuild Fixture Proof Plan",
    "missionscript-slot-bitset-save-rebuild-fixture-proof-plan.md",
    "missionscript-slot-bitset-save-rebuild-fixture-proof-plan.v1.json",
    "slotBitsetSaveFixturePlanStatus=missionscript-slot-bitset-save-rebuild-fixture-proof-plan-complete-deterministic-codec-selected",
    "selectedNextSlice=MissionScript Slot Bitset/Save Deterministic Codec Proof Plan",
    "deterministicBitsetVectorCount=5",
    "falseGuardCount=40",
    "zeroCounterCount=29",
    "Completed MissionScript Command-Effect Rebuild Fixture Selection Proof Plan",
    "missionscript-command-effect-fixture-selection.md",
    "missionscript-command-effect-fixture-selection.v1.json",
    "fixtureSelectionStatus=missionscript-command-effect-fixture-selection-complete-slot-bitset-save-selected",
    "selectedFixtureFamily=slot-bitset-save",
    "selectedChildLane=MissionScript Slot Bitset/Save Rebuild Fixture Proof Plan",
    "selectedLooseCorpusRows=18",
    "falseGuardCount=34",
    "zeroCounterCount=25",
    "Completed MissionScript Command-Effect Rebuild Interface Rollup Proof Plan",
    "missionscript-command-effect-rebuild-interface-rollup.md",
    "missionscript-command-effect-rebuild-interface-rollup.v1.json",
    "rollupStatus=missionscript-command-effect-rebuild-interface-rollup-complete-static-interface-contract-not-runtime-proof",
    "missionScriptCommandEffectRebuildInterfaceRollupStatus=missionscript-command-effect-rebuild-interface-rollup-complete-static-interface-contract-not-runtime-proof",
    "descriptorSchemaCount=1",
    "commandEffectSchemaCount=9",
    "sourceSchemaCount=10",
    "sourceMirrorPairCount=20",
    "descriptorRecordCount=52",
    "uniqueDescriptorTokenCount=48",
    "duplicateDescriptorTokenCount=4",
    "sourceClaimsCount=29",
    "uniqueEvidenceWaveCount=16",
    "falseGuardCount=60",
    "zeroCounterCount=25",
    "publicLeakCheck=PASS",
    "selectedNextSlice=MissionScript Command-Effect Rebuild Fixture Selection Proof Plan",
    "33 HighlightHudPart",
    "34 UnHighlightHudPart",
    "84 AddScore",
    "105 LevelLostString",
    "Completed World / Thing / Spawn Static-To-Rebuild Contract Crosswalk Proof Plan",
    "world-thing-spawn-static-to-rebuild-contract-crosswalk.md",
    "world-thing-spawn-static-to-rebuild-contract-crosswalk.v1.json",
    "crosswalkStatus=world-thing-spawn-static-to-rebuild-contract-crosswalk-complete-static-contract-not-runtime-proof",
    "worldThingSpawnStaticToRebuildContractCrosswalkStatus=world-thing-spawn-static-to-rebuild-contract-crosswalk-complete-static-contract-not-runtime-proof",
    "sourceSchemaCount=3",
    "contractSectionCount=9",
    "contractFalseGuardCount=35",
    "contractZeroCounterCount=16",
    "beProcessesAfterCrosswalk=0",
    "selectedNextSlice=MissionScript Command-Effect Rebuild Interface Rollup Proof Plan",
    "Completed Static-To-Proof Rebuild Transition Next Safe Slice Selection Proof Plan",
    "static-to-proof-next-safe-slice-selection.md",
    "static-to-proof-next-safe-slice-selection.v1.json",
    "complete next safe slice selection",
    "selectionStatus=static-to-proof-next-safe-slice-selection-complete-world-thing-spawn-rebuild-contract-crosswalk-selected",
    "selectedChildLane=World / Thing / Spawn Static-To-Rebuild Contract Crosswalk Proof Plan",
    "selectedChildScope=world-thing-spawn-static-to-rebuild-contract-crosswalk",
    "consultCount=2",
    "candidateCount=4",
    "selectedCandidateRank=1",
    "selectedSourceProofCount=3",
    "selectionFalseGuardCount=19",
    "selectionZeroCounterCount=12",
    "runtimeExecution=false",
    "beLaunch=false",
    "screenshotCapture=false",
    "privateFrameReviewPerformed=false",
    "godotWork=false",
    "ghidraMutation=false",
    "rebuildImplementation=false",
    "beProcessesAfterSelection=0",
    "World / Thing / Spawn Copied-Corpus Schema Proof",
    "World / Thing / Spawn Spawner Handoff Static Proof",
    "World / Thing / Spawn GetThingRef Object-Reference Static Proof",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Public-Safe Result Summary Proof Plan",
    "level100-message-public-safe-result-summary.md",
    "level100-message-public-safe-result-summary.v1.json",
    "complete public-safe result summary",
    "directLevel100RuntimeMessageDisplayObservationPublicSafeResultSummaryStatus=direct-level100-runtime-message-display-observation-public-safe-result-summary-complete-private-frame-review-deferred",
    "publicSummaryOnly=true",
    "summaryRows=1",
    "sourceChecklistRowsMaterialized=9",
    "sourceChecklistFamilyCount=5",
    "sourceNotRunRows=9",
    "sourceUnobservedRows=9",
    "sourceObservedRows=0",
    "sourceRuntimeObservationRows=0",
    "sourceRowStatusChangedCount=0",
    "sourceFalseGuardCount=47",
    "sourceZeroCounterCount=19",
    "privateFrameReviewDeferred=true",
    "futureReviewRequiresExplicitOperatorArm=true",
    "runtimeMessageDisplayClaim=false",
    "runtimeMessageDisplayProven=false",
    "sourceSelectionObserved=false",
    "sourceSelectionProven=false",
    "missionScriptRuntimeEvidenceRows=0",
    "summaryFalseGuardCount=45",
    "summaryZeroCounterCount=12",
    "falseGuardCount=45",
    "zeroCounterCount=12",
    "Follow-up child lane: Static-To-Proof Rebuild Transition Next Safe Slice Selection Proof Plan",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Private-Frame Review Checklist Population Proof Plan",
    "level100-message-private-frame-checklist-population.md",
    "level100-message-private-frame-checklist-population.v1.json",
    "complete public-safe checklist skeleton population",
    "directLevel100RuntimeMessageDisplayObservationChecklistPrivateFrameReviewChecklistPopulationStatus=direct-level100-runtime-message-display-observation-checklist-private-frame-review-checklist-population-deferred-pending-explicit-operator-arm",
    "checklistPopulationOnly=true",
    "publicSafeChecklistRowsMaterialized=true",
    "checklistRowsMaterialized=9",
    "checklistFamilyCount=5",
    "notRunRows=9",
    "unobservedRows=9",
    "observedRows=0",
    "rowStatusChangedCount=0",
    "blockedByMissingExplicitOperatorArm=true",
    "checklistObservationPerformed=false",
    "falseGuardCount=47",
    "zeroCounterCount=19",
    "Follow-up child lane: MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Public-Safe Result Summary Proof Plan",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Private-Frame Review Arm Boundary Proof Plan",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Dry-Run Validation Proof Plan",
    "level100-message-checklist-dry-run-validation.md",
    "level100-message-checklist-dry-run-validation.v1.json",
    "complete public-safe checklist dry-run validation",
    "directLevel100RuntimeMessageDisplayObservationChecklistDryRunValidationStatus=direct-level100-runtime-message-display-observation-checklist-dry-run-validation-pass-no-runtime-message-proof",
    "dryRunValidationOnly=true",
    "validationMethod=schema-and-guard-dry-run-no-private-frame-review",
    "templateMutation=false",
    "dryRunTemplateClassCount=5",
    "dryRunArtifactKeyCount=5",
    "dryRunRowFamilyCount=5",
    "dryRunValidationRows=9",
    "allowedRowStatuses=not-run/observed/inconclusive/blocked/out-of-scope",
    "defaultStatusesNotRun=true",
    "observationStatusesUnobserved=true",
    "falseGuardCount=33",
    "zeroCounterCount=9",
    "beLaunch=false",
    "launchArmed=false",
    "screenshotCapture=false",
    "beProcessesAfterDryRun=0",
    "Follow-up child lane: MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Private-Frame Review Arm Boundary Proof Plan",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Template Proof Plan",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-template-proof-plan.md",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-template.v1.json",
    "complete public-safe runtime message display observation checklist-template proof plan",
    "directLevel100RuntimeMessageDisplayObservationChecklistTemplateStatus=direct-level100-runtime-message-display-observation-checklist-template-defined-no-runtime-message-proof",
    "templateOnly=true",
    "runtimeExecution=false",
    "messageObservationPerformed=false",
    "sourceSelectionProven=false",
    "messageDisplayClassificationProven=false",
    "timingOrderProven=false",
    "defaultStatus=not-run",
    "observationStatus=unobserved",
    "templateClassCount=5",
    "privateFrameMessageObservationChecklistRows=3",
    "sourceSelectionBoundaryRows=1",
    "messageDisplayClassificationRows=3",
    "timingOrderClassificationRows=1",
    "publicSafeResultSummaryRows=1",
    "private_frame_message_observation_checklist.v1",
    "source_selection_boundary_row.v1",
    "message_display_classification_row.v1",
    "timing_order_classification_row.v1",
    "public_safe_result_summary.v1",
    "Follow-up child lane: MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Dry-Run Validation Proof Plan",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Boundary Proof Plan",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-boundary-proof-plan.md",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-boundary.v1.json",
    "complete public-safe runtime message display boundary proof plan",
    "directLevel100RuntimeMessageDisplayBoundaryStatus=direct-level100-runtime-message-display-boundary-defined-no-runtime-message-proof",
    "sourceProgressionCorrelationStatus=direct-level100-timed-frame-set-text-overlay-progression-correlated-to-static-level100-token-surface",
    "sourceStaticWalkthroughStatus=PASS",
    "boundaryMethod=public-parent-schema-boundary-from-class-count-correlation",
    "messageDisplayBoundaryRows=3",
    "messageDisplayCandidateFrameRows=3",
    "requiredFutureProofArtifactCount=5",
    "requiredFutureProofArtifacts=private-frame-message-observation-checklist/source-selection-boundary-row/message-display-classification-row/timing-order-classification-row/public-safe-result-summary",
    "Follow-up child lane: MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Template Proof Plan",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Text Overlay Progression Correlation Proof Plan",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-text-overlay-progression-correlation-proof.md",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-text-overlay-progression-correlation.v1.json",
    "complete public-safe timed frame-set text-overlay progression correlation proof",
    "directLevel100TimedFrameSetTextOverlayProgressionCorrelationStatus=direct-level100-timed-frame-set-text-overlay-progression-correlated-to-static-level100-token-surface",
    "sourceTimedFrameSetCaptureStatus=direct-level100-copied-profile-timed-private-frame-set-captured",
    "sourceTextOverlayCorrelationStatus=direct-level100-text-overlay-correlated-to-static-level100-token-surface",
    "textOverlayProgressionCorrelationMethod=public-parent-schema-correlation-no-ocr",
    "progressionCorrelationRows=4",
    "publicFrameClassBuckets=exterior-world-no-tutorial-panel:1/cockpit-hud-tutorial-overlay:3",
    "timedFrameSetTextOverlayProgressionClass=exterior-world-to-cockpit-hud-tutorial-overlay-change-class",
    "perFrameTokenIdentityClaim=false",
    "perFrameSpeakerIdentityClaim=false",
    "Follow-up child lane: MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Boundary Proof Plan",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Capture Proof Plan",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-capture-proof.md",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-capture.v1.json",
    "complete direct Level100 timed private frame-set capture proof",
    "directLevel100TimedFrameSetCaptureStatus=direct-level100-copied-profile-timed-private-frame-set-captured",
    "profileIdClass=level100-clean-materialized-copied-profile",
    "profileIdPublished=false",
    "requestedFrameCount=4",
    "capturedFrameCount=4",
    "frameScheduleClass=bounded-four-frame-schedule",
    "captureDurationSeconds=25",
    "captureStatusesClass=all-captured",
    "frameDimensionClass=stable-656x539",
    "sameProcessWindowAcrossFrames=true",
    "allFrameArtifactsPrivate=true",
    "visibleProgressionClassOnly=true",
    "visualFrameSetTriageRows=4",
    "nonblankFrameRows=4",
    "inGameRenderedFrameRows=4",
    "cockpitHudFrameRows=3",
    "bottomTutorialTextPanelVisibleFrameRows=3",
    "textOverlayChangedAcrossFrameSetClass=true",
    "sourceSelectionObserved=false",
    "missionScriptRuntimeEvidenceRows=0",
    "publicLeakCheckMode=regex-and-field-scan",
    "publicSha256ValueLeakCount=0",
    "publicWindowIdentifierLeakCount=0",
    "publicProcessIdentifierLeakCount=0",
    "Follow-up child lane: MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Text Overlay Progression Correlation Proof Plan",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Text Overlay Correlation Proof Plan",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-text-overlay-correlation-proof.md",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-text-overlay-correlation.v1.json",
    "complete direct Level100 text-overlay correlation proof",
    "directLevel100TextOverlayCorrelationStatus=direct-level100-text-overlay-correlated-to-static-level100-token-surface",
    "sourceVisualFrameTriageStatus=direct-level100-private-still-frame-visually-triaged",
    "sourceStaticTextSpeakerStatus=PASS",
    "correlatedFrameCount=1",
    "textOverlayCorrelationMethod=public-parent-schema-correlation-no-ocr",
    "textOverlayCorrelationRows=1",
    "tokenUniverseClass=static-level100-message-help-objective-loss-speaker-token-surface",
    "relevantStaticTokensResolved=68/68",
    "missingReferenceTokens=0",
    "messageRows=45",
    "messageUnique=43",
    "speakerRows=45",
    "speakerTokens=P_TATIANA/P_KRAMER/P_TECHNICIAN",
    "rawDialoguePublished=false",
    "exactVisibleTokenIdentityClaim=false",
    "runtimeMessageDisplayClaim=false",
    "rawDialogueLeakCount=0",
    "Follow-up child lane: MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Capture Proof Plan",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Visual Frame Triage Proof Plan",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage-proof.md",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage.v1.json",
    "complete direct Level100 private still-frame visual triage proof",
    "directLevel100VisualFrameTriageStatus=direct-level100-private-still-frame-visually-triaged",
    "sourceCaptureProof=missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture.v1.json",
    "sourceCaptureStatus=direct-level100-copied-profile-window-still-frame-captured",
    "sourceCaptureFrameCount=1",
    "triagedFrameCount=1",
    "newLaunch=false",
    "newScreenshotCapture=false",
    "visualTriageMethod=codex-root-private-still-frame-review",
    "privateFrameArtifactClass=private-still-frame-png",
    "privateFrameReviewedByClass=codex-root-private-visual-triage",
    "privateProofAssetPublished=false",
    "privateCaptureLocatorIncluded=false",
    "privateArtifactHashIncluded=false",
    "privateArtifactBytesIncluded=false",
    "privateWindowIdentifiersIncluded=false",
    "visibleStateClass=in-level-visual-candidate",
    "visualFrameReadable=true",
    "visualFrameBlank=false",
    "visualFrameOcclusionClass=unknown",
    "visualFrameTriageRows=1",
    "visibleTextExcerptPublished=false",
    "visualCorrectnessClaim=false",
    "pixelCorrectnessClaim=false",
    "beWindowFrameVisible=true",
    "inGameRenderedFrameVisible=true",
    "bottomTutorialTextPanelVisible=true",
    "tutorialTextGlyphsVisible=true",
    "visualCorrectnessProven=false",
    "exactTextOcrPerformed=false",
    "Follow-up child lane: MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Text Overlay Correlation Proof Plan",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Screenshot Capture Proof Plan",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture-proof.md",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture.v1.json",
    "complete direct Level100 copied-profile screenshot capture proof, not MissionScript/runtime behavior or visual correctness proof",
    "directLevel100ScreenshotCaptureStatus=direct-level100-copied-profile-window-still-frame-captured",
    "directLevel100RouteStatus=still-frame-captured-no-missionscript-proof",
    "exactProcessWindowCount=1",
    "captureFrameCount=1",
    "captureStatus=captured",
    "captureWidth=656",
    "captureHeight=539",
    "captureArtifactBytesRecordedPrivately=true",
    "captureArtifactHashRecordedPrivately=true",
    "captureArtifactPublished=false",
    "captureOutputPathClass=short-private-output-path",
    "pathLengthMitigation=short-private-output-path-used-after-gdi-plus-long-path-save-failure",
    "Follow-up child lane: MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Visual Frame Triage Proof Plan",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Launch Smoke Proof Plan",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke-proof.md",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke.v1.json",
    "complete direct Level100 copied-profile launch-window smoke proof, not MissionScript/runtime behavior proof",
    "directLevel100LaunchWindowSmokeStatus=direct-level100-copied-profile-window-smoke-complete",
    "selectedRoute=direct-level100-candidate",
    "launchArguments=-skipfmv -level 100",
    "directLevel100RouteStatus=window-smoke-complete-no-missionscript-proof",
    "windowHelperPowerShellCompatibilityFix=runningOnWindows-local-variable",
    "observationDelaySeconds=15",
    "windowScanStatus=ready",
    "exactPidWindowCount=1",
    "screenshotCapture=false",
    "captureFrameCount=0",
    "copiedTargetHashStableDuringSmoke=true",
    "installedTargetHashStableDuringSmoke=true",
    "Follow-up child lane: MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Screenshot Capture Proof Plan",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Screenshot Capture Proof Plan",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture-proof.md",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture.v1.json",
    "complete copied-profile screenshot capture proof, not MissionScript/runtime behavior or visual correctness proof",
    "screenshotCaptureStatus=copied-profile-window-still-frame-captured",
    "windowScanHelper=tools/list_game_windows.ps1",
    "windowScanHelperSchema=game-window-scan-helper.v1",
    "captureHelper=tools/capture_game_window.ps1",
    "captureHelperSchema=game-window-capture-helper.v1",
    "windowCandidateCount=1",
    "exactPidHwndWindowMatch=true",
    "captureFrameCount=1",
    "captureStatus=captured",
    "captureWidth=656",
    "captureHeight=539",
    "captureArtifactClass=private-still-frame-png",
    "captureArtifactPublished=false",
    "screenshotCaptureEvidenceRows=1",
    "Follow-up child lane: MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Launch Smoke Proof Plan",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Window Smoke Proof Plan",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke-proof.md",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke.v1.json",
    "complete copied-profile launch-window smoke proof, not MissionScript/runtime behavior proof",
    "launchWindowSmokeStatus=copied-profile-window-smoke-complete",
    "selectedRoute=skip-fmv-copied-profile-launch",
    "launchHelperSchema=game-launch-process.v1",
    "launchArmed=true",
    "beLaunch=true",
    "processStarted=true",
    "mainWindowHandleObserved=true",
    "mainWindowTitleClass=BEA",
    "processCleanup=PASS",
    "missionScriptRuntimeEvidenceRows=0",
    "Follow-up child lane: MissionScript Level100 Tutorial Copied-Profile Runtime Observation Screenshot Capture Proof Plan",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Command Proof Plan",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command-proof-plan.md",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command.v1.json",
    "complete launch-command proof, not BEA launch or runtime proof",
    "launchCommandStatus=ready-unarmed-command-proof",
    "workingDirectoryClass=copied-profile-root",
    "launchHelper=tools/start_game_profile.ps1",
    "launchHelperMode=PrintOnly",
    "commandClassCount=3",
    "selectedInitialRoute=skip-fmv-copied-profile-launch",
    "directLevel100Route=direct-level100-candidate",
    "directLevel100RouteStatus=candidate-unproven-unarmed",
    "launchCommandExecuted=false",
    "processStarted=false",
    "stopBeforeCreateProcess=true",
    "launchArmGateSpecified=true",
    "invalidArgumentRejected=true",
    "Follow-up child lane: MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Window Smoke Proof Plan",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Executable Patch Proof Plan",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch-proof.md",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch.v1.json",
    "complete copied-executable stable patch proof, not launch or runtime proof",
    "patchStatus=stable-copied-executable-patched",
    "targetExecutableClass=copied-profile-BEA.exe",
    "stablePatchRows=4",
    "skipAutoToggleArmed=false",
    "prePatchSha256=74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
    "targetHash=e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918",
    "backupHash=74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750",
    "targetBytes=2506752",
    "backupBytes=2506752",
    "dryRunMessage=dry-run: no bytes were written",
    "applyMessage=patch apply complete",
    "readbackMessage=verified: no bytes were written",
    "Follow-up child lane: MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Command Proof Plan",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Proof Plan",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-proof.md",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization.v1.json",
    "complete clean copied-profile materialization, not patch or runtime proof",
    "materializationStatus=clean-copied-profile-created",
    "profileId=level100-clean-materialized-20260608-214752",
    "artifactRootClass=repo-local-ignored-private-evidence-root",
    "sourceExecutableClass=canonical-clean-retail-backup-specimen",
    "sourceResourceClass=read-only-installed-game-resource-material",
    "copiedProfileCreated=true",
    "copiedExecutableCreated=true",
    "copiedSpecimenHashChecked=true",
    "copiedExecutableSha256Class=matches-canonical-clean-retail",
    "copiedExecutableBytes=2506752",
    "payloadFileCount=5479",
    "payloadTotalBytes=696783748",
    "dataFileCount=5464",
    "savegameFileCount=9",
    "privateEvidenceFileCount=3",
    "localPrivateArtifactFileCount=5482",
    "localPrivateArtifactTotalBytes=696793402",
    "Follow-up child lane: MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Executable Patch Proof Plan",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Clean Source Specimen Resolution Proof Plan",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-clean-source-specimen-resolution-proof-plan.md",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-clean-source-specimen-resolution.v1.json",
    "complete source-specimen authority resolution before copied-profile materialization",
    "status=COMPLETE",
    "resolutionStatus=clean-backup-specimen-verified",
    "cleanBackupMatchesExpected=true",
    "cleanBackupAuthorityClass=canonical-clean-retail-match",
    "currentSpecimenClass=known-stable-patch-catalog-deltas-from-clean",
    "sameLength=true",
    "byteDiffCount=28",
    "unknownDiffCount=0",
    "resolution_gate",
    "force_windowed",
    "version_overlay_use_patched_format_pointer",
    "version_overlay_patched_format_cave_string",
    "skip_auto_toggle",
    "Follow-up child lane: MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Proof Plan",
    "source-specimen-hash-mismatch",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Preflight",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight-proof.md",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight.v1.json",
    "deferred because source specimen hash does not match the canonical clean retail specimen",
    "status=DEFERRED",
    "deferReason=source-specimen-hash-mismatch",
    "hashClass=mismatch-unrecognized",
    "e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918",
    "observedSourceSize=2506752",
    "sourceSpecimenMatchesExpected=false",
    "sourceSpecimenRecognized=false",
    "materializationAttempted=false",
    "copiedSpecimenHashChecked=false",
    "Follow-up child lane: MissionScript Level100 Tutorial Copied-Profile Runtime Observation Clean Source Specimen Resolution Proof Plan",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Preparation Proof Plan",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation-proof-plan.md",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation.v1.json",
    "copied-profile preparation planning complete, not copied-profile creation or runtime proof",
    "planned-not-created",
    "preparationOnly=true",
    "preparationPlanComplete=true",
    "copiedExecutableCreated=false",
    "originalExecutableMutation=false",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Manifest Dry-Run Validation Proof Plan",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-dry-run-validation-proof-plan.md",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-dry-run-validation.v1.json",
    "dry-run validation complete, not runtime proof",
    "publicLeakCheck=PASS",
    "observedRowCount=0",
    "runtimeEvidenceRows=0",
    "privatePathLeakCount=0",
    "rawArtifactLeakCount=0",
    "Follow-up child lane: MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Preparation Proof Plan",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Manifest Template Generation Proof Plan",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-template-generation-proof-plan.md",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-templates.v1.json",
    "manifest-template generation complete, not runtime proof",
    "public-safe empty template bundle",
    "templateOnly=true",
    "runtimeExecution=false",
    "containsPrivatePath=false",
    "containsRawArtifact=false",
    "redactionPolicy=public-safe-placeholder-only",
    "launchArmed=false",
    "installedGameMutation=false",
    "privatePathsRedactedInPublic=true",
    "<COPIED_PROFILE_ID_PENDING>",
    "<APP_OWNED_ARTIFACT_ROOT_PENDING>",
    "<PRIVATE_PATH_REDACTED>",
    "<PRIVATE_ARTIFACT_PATH_REDACTED>",
    "redaction placeholders",
    "Boundary token: runtimeExecution=false; beLaunch=false; newLaunch=false; screenshotCapture=false; privateFrameReviewPerformed=false; rowObservation=false; sourceSelectionObserved=false; sourceSelectionProven=false; nativeInput=false; debuggerAttachment=false; godotWork=false; ghidraMutation=false; executablePatching=false; productUiWired=false; rebuildImplementation=false; runtimeMissionScriptExecutionProven=false; runtimeCommandEffectsProven=false; runtimePhysicsScriptBehaviorProven=false",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Artifact Manifest Proof Plan",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest-proof-plan.md",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest.v1.json",
    "artifact-manifest planning complete, not runtime proof",
    "concrete manifest classes",
    "copied_profile_manifest.v1",
    "specimen_byte_check.v1",
    "launch_command_manifest.v1",
    "source_selection_observation.v1",
    "level100_observation_checklist.v1",
    "private_artifact_inventory.v1",
    "public_safe_result_summary.v1",
    "not-run",
    "observed",
    "inconclusive",
    "blocked",
    "out-of-scope",
    "Follow-up child lane MissionScript Level100 Tutorial Copied-Profile Runtime Observation Manifest Template Generation Proof Plan is complete; next child lane: MissionScript Level100 Tutorial Copied-Profile Runtime Observation Manifest Dry-Run Validation Proof Plan",
    "Completed MissionScript Level100 Tutorial Copied-Profile Runtime Observation Boundary Planning Proof Plan",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-boundary-proof-plan.md",
    "missionscript-level100-tutorial-copied-profile-runtime-observation-boundary.v1.json",
    "copied-profile runtime observation boundary planning complete, not runtime proof",
    "copied-profile runtime observation boundary planning",
    "launch command manifest",
    "Completed MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan",
    "missionscript-level100-tutorial-runtime-harness-boundary-proof-plan.md",
    "missionscript-level100-tutorial-runtime-harness-boundary.v1.json",
    "runtime-harness boundary proof plan complete, not runtime proof",
    "copied profile manifest",
    "specimen hash and byte-check report",
    "source-selection observation log",
    "bounded event/message/HUD/object observation checklist",
    "private artifact inventory",
    "public-safe result summary",
    "Completed MissionScript Level100 Tutorial Text/Speaker Resolution Static Proof Plan",
    "missionscript-level100-tutorial-text-speaker-resolution-proof-plan.md",
    "missionscript-level100-tutorial-text-speaker-resolution.v1.json",
    "static text/speaker resolution proof plan complete, not runtime proof",
    "English.txt",
    "Global.txt",
    "level-local `text.stf`",
    "shared `text/english.txt`",
    "shared `text/text.stf`",
    "2571",
    "TUTORIAL_13_MOD",
    "TUTORIAL_DODGE_MOD",
    "TUTORIAL_THROTTLE_MOD",
    "HELP_FIRE",
    "HELP_RETRO",
    "HELP_TRANSFORM",
    "HELP_WEAPON_SELECT",
    "HELP_ZOOM_IN",
    "HELP_ZOOM_OUT",
    "LOSE_TUTORIAL_BROKE",
    "68/68",
    "0 missing",
    "Completed MissionScript Level100 Tutorial Static Event/Command Walkthrough Proof Plan",
    "missionscript-level100-tutorial-static-walkthrough-proof-plan.md",
    "missionscript-level100-tutorial-static-walkthrough.v1.json",
    "static walkthrough proof plan complete, not runtime proof",
    "level100",
    "LevelScript.msl",
    "1469",
    "Destroyed Friendly Building",
    "Friendly Building Destroyed",
    "P_TATIANA",
    "P_KRAMER",
    "P_TECHNICIAN",
    "0x005383c0 IScript__ScheduleEvent",
    "0x00539dc0 CMissionScriptObjectCode__StartLoadAsync",
    "Completed MissionScript Packed-vs-Loose Script Selection Proof Plan",
    "missionscript-packed-vs-loose-script-selection-proof-plan.md",
    "missionscript-packed-vs-loose-script-selection.v1.json",
    "static proof plan complete, not runtime proof",
    "MissionScript Packed-vs-Loose Script Selection Proof Plan",
    "733",
    "32",
    "72-74",
    "95",
    "795",
    "301",
    "0` inflate errors",
    "0` literal Goodie API/token hits",
    "0x00539dc0 CMissionScriptObjectCode__StartLoadAsync",
    "0x00539ca0 CMissionScriptObjectCode__LoadAsync",
    "CDXMemBuffer__InitFromFile",
    "Completed MissionScript Player-State / Score Command-Effect Static Proof",
    "missionscript-player-state-score-command-effect-static-proof.md",
    "missionscript-player-state-score-command-effect.v1.json",
    "static player-state/score command-effect schema proof complete, not runtime proof",
    "MissionScript Player-State / Score Command-Effect",
    "84 AddScore",
    "136 ToggleCockpit",
    "137 SetStealth",
    "IScript__Unk_00534410",
    "&LAB_00533950",
    "&LAB_00533980",
    "0x00534410 IScript__SecondaryObjectiveComplete",
    "15 / 0 / 10",
    "12 / 0 / 4",
    "CGame::IncScore",
    "CBattleEngine::ToggleCockpit",
    "CBattleEngine__HandleCloak",
    "runtime score behavior",
    "runtime cockpit behavior",
    "runtime stealth behavior",
    "weapon-fire/stealth interaction",
    "Completed MissionScript HUD / Display Command-Effect Static Proof",
    "missionscript-hud-display-command-effect-static-proof.md",
    "missionscript-hud-display-command-effect.v1.json",
    "static HUD/display command-effect schema proof complete, not runtime proof",
    "MissionScript HUD / Display Command-Effect",
    "33 HighlightHudPart",
    "34 UnHighlightHudPart",
    "75 InitVariable",
    "76 SetVariable",
    "77 ShutdownVariable",
    "&LAB_00535d70",
    "&LAB_00535e60",
    "&LAB_00536210",
    "&LAB_00536230",
    "&LAB_00536260",
    "13 / 13 / 77 / 146 / 26",
    "CHud__SetHudComponent",
    "CHud__RenderOverlayForViewpoint",
    "CHudComponent__RenderPass",
    "CWorld__PushWorldTextSlot",
    "CWorld__UpdateWorldTextSlotTiming",
    "CWorld__ClearWorldTextSlot",
    "CWorld__GetWorldTextSlotTimerValue",
    "hud-frontend-overlay-static-contract.md",
    "hud-frontend-overlay-visual-runtime-proof-plan.md",
    "runtime HUD behavior",
    "visible HUD flashing",
    "variable display",
    "missionscript-thing-value-engine-helper-command-effect-static-proof.md",
    "missionscript-thing-value-engine-helper-command-effect.v1.json",
    "static thing-value/engine-helper command-effect schema proof complete, not runtime proof",
    "MissionScript Thing Value / Engine Helper Command-Effect",
    "IScript__SetThingValueViaVFunc198_FromArg",
    "IScript__SetThingValueViaVFunc19C_FromArg",
    "IScript__SetThingValueViaEngineHelper4FE390_FromArg",
    "IScript__SetThingValueViaEngineHelper4FE3F0_FromArg",
    "IScript__SetThingFloatViaVFunc1C8_FromArg",
    "IScript__SetThingRefViaCUnitHelper4FD830_FromArg",
    "0x00534fb0",
    "0x00534fe0",
    "0x00535010",
    "0x00535040",
    "0x00535530",
    "0x00535560",
    "+0x38",
    "+0x30",
    "+0x198",
    "+0x19c",
    "+0x1c8",
    "CEngine__EnableThingByNameFlag",
    "CEngine__DisableThingByNameFlag",
    "CUnit__SetFactionForHierarchy",
    "DisableWeapon",
    "EnableFlightMode",
    "DisableSpawner",
    "SetName",
    "TeleportOrientation",
    "SetWindVector",
    "15 / 1 / 2 / 4 / 5 / 0",
    "Wave582 evidence counts",
    "`534` instruction rows",
    "`32` vtable rows",
    "Completed MissionScript Thing Value / Engine Helper Command-Effect Static Proof",
    "missionscript-vector-range-command-effect-static-proof.md",
    "missionscript-vector-range-command-effect.v1.json",
    "static vector/range command-effect schema proof complete, not runtime proof",
    "MissionScript Vector/Range Command-Effect",
    "IScript__GetVectorLength",
    "IScript__CheckValueInRange",
    "IScript__GetVectorX",
    "IScript__GetVectorY",
    "IScript__GetVectorZ",
    "0x005345d0",
    "0x005347b0",
    "0x00534b80",
    "0x00534c10",
    "0x00534ca0",
    "+0x44",
    "+0x34",
    "0x005e4ea4",
    "0x005e4d50",
    "component offsets `+0`, `+4`, and `+8`",
    "no direct non-comment loose-MSL rows",
    "Wave581 evidence counts",
    "`3545` instruction rows",
    "`24` vtable rows",
    "Completed MissionScript Vector/Range Command-Effect Static Proof",
    "missionscript-cutscene-pan-camera-position-command-effect-static-proof.md",
    "missionscript-cutscene-pan-camera-position-command-effect.v1.json",
    "static cutscene pan-camera/position command-effect schema proof complete, not runtime proof",
    "MissionScript Cutscene Pan-Camera / Position Command-Effect",
    "CreatePosition",
    "Goto3PointPanCamera",
    "Goto4PointPanCamera",
    "CPositionDataType",
    "0x0064de90",
    "0x0064ea90",
    "0x005e4da4",
    "0x00533b70 IScript__Create3PointPanCamera",
    "0x00533eb0 IScript__Create4PointPanCamera",
    "CGame__SetCurrentCamera",
    "CPanCamera",
    "CBSpline",
    "DAT_0083d9c0",
    "GetThingRef(\"Fenrir\")",
    "level741",
    "level742",
    "6 cutscene Fenrir GetThingRef rows",
    "world-thing-spawn-getthingref-object-reference-static-proof.md",
    "world-thing-spawn-getthingref-object-reference-static.v1.json",
    "static GetThingRef object-reference proof complete, not runtime proof",
    "training-target-zone-getthingref-family",
    "`9` raw selected `GetThingRef` rows",
    "`8` selected unique object-reference rows",
    "`8` selected unique file/thing rows",
    "`1` duplicate-call row",
    "`9` empty-spawner rows",
    "Level22Script.msl",
    "LevelScript.msl",
    "Target Zone 1",
    "Target Zone 4",
    "world-thing-spawn-spawner-handoff-static-proof.md",
    "world-thing-spawn-spawner-handoff-static.v1.json",
    "static spawner handoff proof complete, not runtime proof",
    "training-target-spawn-family",
    "0x0050f970 CWorldPhysicsManager__CreateSpawner",
    "DAT_008553f4",
    "0x005115b0 CWorldPhysicsManager__MapGunOrSpawnerTagToIndex",
    "0x00511ad0 CWorldPhysicsManager__AddSpawnerByName",
    "0x004e3c60 CSpawnerThng__DoSpawn",
    "0x004e3f90 CSpawnerThng__ProcessSpawnWave",
    "CUnit__VFunc08_InitAndAddToWorld",
    "0x004fc3a0 CUnit__SetSpawnCooldownState3",
    "Completed World / Thing / Spawn Spawner Handoff Static Proof",
    "Completed World / Thing / Spawn Copied-Corpus Schema Proof",
    "save-options-controller-byte-preservation-copied-file-proof.md",
    "save-options-controller-byte-preservation-copied-file.v1.json",
    "copied-file byte-preservation proof complete, not runtime proof",
    "0x23F6-0x23F8",
    "0x23F9",
    "DiffCount=0",
    "0x24BE-0x26BD",
    "0x26BE-0x2713",
    "0x23A4",
    "0x22D4",
    "0x240C",
    "Completed MissionScript Goodie State Command-Effect static proof",
    "missionscript-goodie-state-command-effect-static-proof.md",
    "missionscript-goodie-state-command-effect.v1.json",
    "static Goodie state command-effect schema proof complete, not runtime proof",
    "MissionScript Goodie State Command-Effect",
    "IScript__SetGoodieState",
    "IScript__GetGoodieState",
    "g_Career_mGoodies[index-1]",
    "0x00662564",
    "0x1F46",
    "script index N maps to save Goodie index N-1",
    "descriptor/name context only",
    "missionscript-message-audio-command-effect-static-proof.md",
    "missionscript-message-audio-command-effect.v1.json",
    "static message/audio command-effect schema proof complete, not runtime proof",
    "MissionScript Message/Audio Command-Effect",
    "IScript__PlaySound",
    "IScript__PlaySoundWithCallback",
    "IScript__PlaySoundWithFade",
    "IScript__PlaySoundWithPriority",
    "IScript__PlaySoundWithFadeAndPriority",
    "IScript__PrintText",
    "CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance",
    "CMessageBox__StartVoiceOrFallbackTextReveal",
    "1365 PlayCharMessage",
    "7 AddHelpMessage",
    "1553 detailed message rows",
    "11 speakers",
    "499 unique message tokens",
    "missionscript-objective-outcome-command-effect-static-proof.md",
    "missionscript-objective-outcome-command-effect.v1.json",
    "static objective/outcome command-effect schema proof complete, not runtime proof",
    "MissionScript Objective/Outcome Command-Effect",
    "IScript__PrimaryObjectiveComplete",
    "IScript__SecondaryObjectiveComplete",
    "IScript__PrimaryObjectiveFailed",
    "IScript__SecondaryObjectiveFailed",
    "IScript__LevelWon",
    "IScript__LevelLost",
    "IScript__LevelLostString",
    "CGame__FillOutEndLevelData",
    "CGame__DeclareLevelWon",
    "CGame__DeclareLevelLost",
    "CCareer__Update",
    "CEndLevelData__IsAllSecondaryObjectivesComplete",
    "115 primary-complete",
    "42 secondary-complete",
    "102 primary-failed",
    "79 LevelWon",
    "13 LevelLost",
    "110 LevelLost-family",
    "71 LevelWon-family",
    "missionscript-slot-command-effect-static-proof.md",
    "missionscript-slot-command-effect.v1.json",
    "static slot command-effect schema proof complete, not runtime proof",
    "MissionScript Slot Command-Effect",
    "IScript__SetSlot",
    "IScript__SetSlotSave",
    "IScript__GetSlotBitValue",
    "CGame__SetSlot",
    "CGame__GetSlot",
    "CCareer__SetSlot",
    "CGame+0x308",
    "0x240A",
    "6 slot-using level rows",
    "18 detailed slot call rows",
    "6 GetSlot",
    "8 SetSlot",
    "4 SetSlotSave",
    "missionscript-event-object-code-lifecycle-proof.md",
    "missionscript-event-object-code-lifecycle.v1.json",
    "static event/object-code lifecycle schema proof complete, not runtime proof",
    "IScript__ScheduleEvent",
    "CScriptEventNB__PostEvent",
    "CEventFunction__Execute",
    "CScriptObjectCode__CallEventDirect",
    "CMissionScriptObjectCode__LoadAsync",
    "Completed MissionScript event/object-code lifecycle schema proof",
    "missionscript-vm-datatype-opcode-schema-proof.md",
    "missionscript-vm-datatype-opcode-schema.v1.json",
    "static VM/datatype/opcode schema proof complete, not runtime proof",
    "`27` opcode factory cases",
    "`6` datatype factory cases",
    "Completed World / Thing / Spawn / Object-Reference Bridge Proof Plan",
    "World / Thing / Spawn / Object-Reference Bridge Proof Plan",
    "world-thing-spawn-object-reference-proof-plan.md",
    "MissionScript `GetThingRef` / `SpawnThing`",
    "runtime object identity",
    "runtime spawn behavior",
    "runtime world loading",
    "spawner-preserving",
    "duplicate-call counts",
    "Completed MissionScript / IScript static-contract extraction slice",
    "MissionScript / IScript Static Contract",
    "missionscript-iscript-static-contract.md",
    "static contract extraction complete, not runtime proof",
    "command registry, IScript handlers, VM/datatype/opcode core, event/object-code lifecycle, game/career bridge, thing/spawn/object-reference bridge, and loose MSL corpus boundaries",
    "Completed MissionScript / IScript proof-plan slice",
    "MissionScript / IScript proof plan",
    "MissionScript / IScript Proof Plan",
    "missionscript-iscript-proof-plan.md",
    "Completed MissionScript VM/datatype/opcode schema proof",
    "command descriptor schema",
    "IScript command handlers",
    "VM/datatype/opcode behavior",
    "event/object-code lifecycle",
    "loose MSL corpus linkage",
    "mission outcome/event planning",
    "thing/spawn/object-reference bridge",
    "message/objective/HUD command planning",
    "Do not broaden into live mission execution, broad mission simulation, save/career mutation, native input, audio/message/HUD output, packed-vs-loose resource selection, Godot, patching, broad runtime proof, or rebuild parity.",
    "Completed Frontend / input / game-loop proof-plan slice",
    "Frontend / input / game-loop proof plan",
    "Frontend / Input / Game Loop Proof Plan",
    "frontend-input-game-loop-proof-plan.md",
    "game-loop route accounting",
    "frontend page transition design",
    "input/controller mapping design",
    "save/load/options menu handoff design",
    "pause/message lifecycle design",
    "frontend-video wrapper design",
    "Goodies/level/multiplayer page behavior design",
    "Do not broaden into broad game-loop runtime, native input driving, save/options mutation, frontend-video playback, HUD visual proof, audio playback, Godot, patching, broad runtime proof, or rebuild parity.",
    "Engine / platform / math / memory support proof plan",
    "Engine / Platform / Math / Memory Support Proof Plan",
    "engine-platform-math-memory-support-proof-plan.md",
    "pure math equivalence",
    "render-state/matrix support",
    "allocator harnesses",
    "monitor/safe-pointer behavior",
    "platform/file I/O",
    "console command paths",
    "CRT/FPU side-effect isolation",
    "Do not broaden into device handling, platform I/O, allocator/OOM, console execution, monitor/safe-pointer behavior, CRT/FPU side effects, visual QA, Godot, patching, broad runtime proof, or rebuild parity.",
    "Audio / media / cutscene / camera proof plan",
    "Audio / Media / Cutscene / Camera Proof Plan",
    "audio-media-cutscene-camera-proof-plan.md",
    "audio sample lifecycle",
    "reader framing",
    "FMV/cache",
    "cutscene sync",
    "camera behavior",
    "Do not broaden into DirectSound playback, Ogg/WAV decode, Bink/FMV playback, music switching, cutscene sync, camera switching, visual/audio QA, Godot, patching, broad runtime proof, or rebuild parity.",
    "Save / options controller byte-preservation proof plan",
    "Save / Options Controller Byte-Preservation Proof Plan",
    "save-options-controller-byte-preservation-proof-plan.md",
    "copied real `.bes` and `defaultoptions.bea`",
    "true-view offsets",
    "proof plan complete, not runtime proof",
    "Weapon / projectile spawn handoff proof plan",
    "Weapon / Projectile Spawn Handoff Proof Plan",
    "weapon-projectile-spawn-handoff-proof-plan.md",
    "one selected weapon path through WalkerPart or JetPart weapon state",
    "proof plan complete, not runtime proof",
    "Unit targeting / active-reader proof plan",
    "Unit Targeting / Active-Reader Proof Plan",
    "unit-targeting-active-reader-proof-plan.md",
    "proof plan complete, not runtime proof",
    "HUD/frontend overlay proof plan",
    "HUD / Frontend Overlay Visual Runtime Proof Plan",
    "hud-frontend-overlay-visual-runtime-proof-plan.md",
    "visual/runtime proof plan complete, not runtime proof",
    "Destroyable Segments Damage/Break Proof Plan",
    "gameplay-contract proof plan complete, not runtime proof",
    "Texture/resource/decode plus mesh asset bridge",
    "texture-mesh-asset-bridge-proof-plan.md",
    "texture-mesh-asset-bridge-copied-corpus-proof.md",
    "texture-mesh-material-sidecar-ledger-proof.md",
    "copied-corpus inventory/export proof complete, not runtime proof",
    "PhysicsScript schema/parser",
    "physics-script-schema-parser-proof-plan.md",
    "physics-script-copied-corpus-parser-proof.md",
    "Schema/parser proof checklist and corpus requirement list",
    "copied-corpus parser/census proof complete, not runtime proof",
    "Destroyable-segments damage/break micro-slice",
    "destroyable-segments-damage-break-proof-plan.md",
    "No screenshot/capture proof, broad frontend/game-loop runtime proof",
    "No runtime weapon fire behavior, runtime projectile behavior",
    "No runtime save/load behavior, runtime defaultoptions boot behavior",
    "Do not broaden into runtime save/load, defaultoptions boot, menu/controller input, Goodies wall, patching, visual QA, Godot, broad app runtime proof, or rebuild parity.",
    "Do not broaden into collision, terrain interaction, damage, target kill, cloak/stealth, exact CBattleEngine::WeaponFired, or full Unit/BattleEngine runtime proof.",
    "No runtime targeting behavior, broad squad AI behavior",
    "Do not broaden into weapon fire, damage, collision, morph/mode, cloak/stealth, or full Unit/BattleEngine runtime proof.",
    "No broad Unit/BattleEngine runtime proof",
    "No runtime pixel, GPU upload, visual QA, or parity claim.",
    "No mission outcome or serialized completeness claim until corpus proof exists.",
    "No active repo Godot project and not parity proof",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    return path.read_text(encoding="utf-8-sig")


def active_slice_block(text: str) -> str:
    marker = "## Active Proof Slice"
    start = text.find(marker)
    if start < 0:
        return ""
    next_heading = text.find("\n## ", start + len(marker))
    return text[start:] if next_heading < 0 else text[start:next_heading]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_backlog(failures: list[str]) -> None:
    text = read_text(BACKLOG)
    active = active_slice_block(text)
    lower_text = text.lower()
    for token in REQUIRED_TOKENS:
        require(token in text or token.lower() in lower_text, f"backlog missing token: {token}", failures)
    for bad in (
        "runtime proof complete",
        "visual QA complete",
        "rebuild parity proven",
        "no-noticeable-difference parity proven",
        "Godot is the active product lane",
        "asset bridge counts prove runtime render correctness",
        "runtime destruction behavior proven",
        "runtime hud behavior proven",
        "visible hud output proven",
        "screenshot proof complete",
        "broad unit/battleengine runtime proof complete",
        "runtime weapon fire behavior proven",
        "runtime save/load behavior proven",
        "runtime defaultoptions boot behavior proven",
        "runtime menu behavior proven",
        "runtime controller remap/input behavior proven",
        "runtime goodies wall behavior proven",
        "weapon_fire_breaks_stealth proven",
        "exact retail cbattleengine::weaponfired identity proven",
    ):
        require(bad not in text.lower(), f"backlog overclaims: {bad}", failures)
    require(
        "The selected active static-to-proof slice is [World / Thing / Spawn GetThingRef Object-Reference Static Proof]" not in text,
        "backlog still has stale active GetThingRef proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is [MissionScript Cutscene Pan-Camera / Position Command-Effect Static Proof]" not in text,
        "backlog still has stale active cutscene proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is [MissionScript Vector/Range Command-Effect Static Proof]" not in text,
        "backlog still has stale active vector/range proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is [MissionScript Thing Value / Engine Helper Command-Effect Static Proof]" not in text,
        "backlog still has stale active thing-value proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript HUD / Display Command-Effect Static Proof" not in text,
        "backlog still has stale active HUD/display proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Player-State / Score Command-Effect Static Proof" not in text,
        "backlog still has stale active player-state/score proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Packed-vs-Loose Script Selection Proof Plan" not in text,
        "backlog still has stale active packed-vs-loose proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Static Event/Command Walkthrough Proof Plan" not in text,
        "backlog still has stale active Level100 walkthrough proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan" not in text,
        "backlog still has stale active Level100 runtime-harness boundary proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Boundary Planning Proof Plan" not in text,
        "backlog still has stale active Level100 copied-profile runtime observation boundary proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Artifact Manifest Proof Plan" not in text,
        "backlog still has stale active Level100 copied-profile artifact-manifest proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Manifest Template Generation Proof Plan" not in text,
        "backlog still has stale active Level100 manifest-template generation proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Manifest Dry-Run Validation Proof Plan" not in text,
        "backlog still has stale active Level100 manifest dry-run validation proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Preparation Proof Plan" not in text,
        "backlog still has stale active Level100 copied-profile preparation proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Proof Plan" not in text,
        "backlog still has stale active Level100 copied-profile materialization proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Capture Proof Plan" not in text,
        "backlog still has stale active Level100 direct timed frame-set capture proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Timed Frame Set Text Overlay Progression Correlation Proof Plan" not in text,
        "backlog still has stale active Level100 timed frame-set text-overlay progression proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Boundary Proof Plan" not in text,
        "backlog still has stale active Level100 runtime message display boundary proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Template Proof Plan" not in text,
        "backlog still has stale active Level100 runtime message display checklist-template proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Private-Frame Review Checklist Population Proof Plan. Status: selected" not in text,
        "backlog still has stale active Level100 private-frame checklist-population proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Public-Safe Result Summary Proof Plan. Status: selected" not in text,
        "backlog still has stale active Level100 public-safe result summary proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Static-To-Proof Rebuild Transition Next Safe Slice Selection Proof Plan. Status: selected" not in text,
        "backlog still has stale active next-safe selection proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is World / Thing / Spawn Static-To-Rebuild Contract Crosswalk Proof Plan. Status: selected" not in text,
        "backlog still has stale active World/Thing/Spawn crosswalk proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Command-Effect Rebuild Interface Rollup Proof Plan. Status: selected" not in text,
        "backlog still has stale active MissionScript command-effect rollup proof slice",
        failures,
    )
    require(
        "Completed MissionScript Command-Effect Rebuild Interface Rollup Proof Plan" in text,
        "backlog missing completed MissionScript command-effect rollup proof slice",
        failures,
    )
    require(
        "Completed MissionScript Command-Effect Rebuild Fixture Selection Proof Plan" in text,
        "backlog missing completed MissionScript command-effect fixture-selection proof slice",
        failures,
    )
    require(
        "Completed MissionScript Slot Bitset/Save Rebuild Fixture Proof Plan" in text,
        "backlog missing completed MissionScript slot bitset/save proof-plan slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Command-Effect Rebuild Fixture Selection Proof Plan. Status: selected" not in text,
        "backlog still has stale active MissionScript command-effect fixture-selection proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Slot Bitset/Save Rebuild Fixture Proof Plan. Status: selected" not in text,
        "backlog still has stale active MissionScript slot bitset/save proof-plan slice",
        failures,
    )
    require(
        "Completed MissionScript Slot Bitset/Save Deterministic Codec Proof Plan" in text,
        "backlog missing completed MissionScript slot bitset/save deterministic codec proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Slot Bitset/Save Deterministic Codec Proof Plan. Status: selected" not in text,
        "backlog still has stale active MissionScript slot bitset/save deterministic codec proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Slot Bitset/Save Copied-File Byte-Diff Proof Plan. Status: selected" not in text,
        "backlog still has stale active MissionScript slot bitset/save copied-file byte-diff proof slice",
        failures,
    )
    require(
        "Completed MissionScript Slot Bitset/Save Copied-File Byte-Diff Proof" in text,
        "backlog missing completed MissionScript slot bitset/save copied-file byte-diff proof slice",
        failures,
    )
    require(
        "Completed MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof" in text,
        "backlog missing completed MissionScript slot bitset/save clean-room codec interface proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof Plan. Status: selected" not in text,
        "backlog still marks MissionScript slot bitset/save clean-room codec interface proof slice active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Slot Bitset/Save Runtime-Proof Readiness Gate Plan. Status: selected" not in text,
        "backlog still marks MissionScript slot bitset/save runtime-proof readiness gate active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Slot Bitset/Save AppCore Boundary-Slot Corpus Proof Plan. Status: selected" not in text,
        "backlog still marks MissionScript slot bitset/save AppCore boundary-slot corpus slice active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Slot Bitset/Save AppCore Copied-Baseline Boundary Corpus Harness Proof Plan. Status: selected" not in text,
        "backlog still marks MissionScript slot bitset/save copied-baseline boundary corpus harness slice active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Save / Options Byte-Preservation AppCore Implementation Contract Proof Plan. Status: selected" not in text,
        "backlog still marks Save / Options AppCore implementation-contract slice active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Save / Options Byte-Preservation Runtime-Proof Readiness Gate Plan. Status: selected" not in text,
        "backlog still marks Save / Options runtime-proof readiness gate slice active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Save / Options Byte-Preservation AppCore Fixture Matrix Proof Plan. Status: selected" not in text,
        "backlog still marks Save / Options AppCore fixture-matrix slice active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Static-To-Proof Rebuild Transition Next Safe Slice Selection Refresh Proof Plan. Status: selected" not in text,
        "backlog still marks next-slice selection refresh slice active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Vector/Range Command-Effect Deterministic Helper Fixture Proof Plan. Status: selected" not in text,
        "backlog still marks MissionScript vector/range deterministic helper fixture slice active",
        failures,
    )
    require(
        "Completed MissionScript Command-Effect Post-Goodie Selection Refresh Proof Plan" in text,
        "backlog missing completed MissionScript post-Goodie selection refresh slice",
        failures,
    )
    require(
        "Completed MissionScript Cutscene Pan-Camera / Position Command-Effect Deterministic Fixture Proof Plan" in text,
        "backlog missing completed MissionScript cutscene pan-camera/position fixture slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Cutscene Pan-Camera / Position Command-Effect Deterministic Fixture Proof Plan. Status: selected" not in text,
        "backlog still marks MissionScript cutscene pan-camera/position fixture slice active",
        failures,
    )
    require(
        "Completed MissionScript Objective/Outcome Command-Effect Fixture Proof Plan" in text,
        "backlog missing completed MissionScript objective/outcome fixture slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Objective/Outcome Command-Effect Fixture Proof Plan. Status: selected" not in text,
        "backlog still marks MissionScript objective/outcome fixture slice active",
        failures,
    )
    require(
        "Completed MissionScript Message/Audio Command-Effect Fixture Proof Plan" in text,
        "backlog missing completed MissionScript message/audio fixture slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Message/Audio Command-Effect Fixture Proof Plan. Status: selected" not in text,
        "backlog still marks MissionScript message/audio fixture slice active",
        failures,
    )
    require(
        "Completed MissionScript HUD / Display Command-Effect Fixture Proof Plan" in text,
        "backlog missing completed MissionScript HUD/display fixture slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript HUD / Display Command-Effect Fixture Proof Plan. Status: selected" not in text,
        "backlog still marks MissionScript HUD/display fixture slice active",
        failures,
    )
    require(
        "Completed MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan" in text,
        "backlog missing completed MissionScript Thing Value / Engine Helper fixture slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Thing Value / Engine Helper Command-Effect Fixture Proof Plan. Status: selected" not in text,
        "backlog still marks MissionScript Thing Value / Engine Helper fixture slice active",
        failures,
    )
    require(
        "Completed MissionScript Player-State / Score Command-Effect Fixture Proof Plan" in text,
        "backlog missing completed MissionScript Player-State / Score fixture slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Player-State / Score Command-Effect Fixture Proof Plan. Status: selected" not in text,
        "backlog still marks MissionScript Player-State / Score fixture slice active",
        failures,
    )
    require(
        "Completed MissionScript Command-Effect Fixture Family Completion Rollup Proof Plan" in text,
        "backlog missing completed MissionScript command-effect fixture family completion rollup slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Command-Effect Fixture Family Completion Rollup Proof Plan. Status: selected" not in text,
        "backlog still marks MissionScript command-effect fixture family completion rollup slice active",
        failures,
    )
    require(
        "Completed Static-To-Proof Rebuild Transition Post-Command-Effect Fixture Next Safe Slice Selection Refresh Proof Plan" in text,
        "backlog missing completed post-command-effect fixture next-safe selection refresh slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Static-To-Proof Rebuild Transition Post-Command-Effect Fixture Next Safe Slice Selection Refresh Proof Plan. Status: selected" not in text,
        "backlog still marks post-command-effect fixture next-safe selection refresh slice active",
        failures,
    )
    require(
        "Completed PhysicsScript Semantic Value-Field Schema Ledger Proof Plan" in text,
        "backlog missing completed PhysicsScript semantic value-field schema ledger slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is PhysicsScript Semantic Value-Field Schema Ledger Proof Plan. Status: selected" not in text,
        "backlog still marks PhysicsScript semantic value-field schema ledger slice active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is PhysicsScript Scalar/String Value Decoder Fixture Proof Plan. Status: selected" not in text,
        "backlog still marks PhysicsScript scalar/string value decoder fixture slice active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is PhysicsScript Value-ID Semantic Crosswalk Proof Plan. Status: selected" not in text,
        "backlog still marks PhysicsScript value-ID semantic crosswalk slice active",
        failures,
    )
    require(
        "Completed PhysicsScript Rebuild Interface Rollup Proof Plan" in text,
        "backlog missing completed PhysicsScript rebuild interface rollup slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is PhysicsScript Rebuild Interface Rollup Proof Plan. Status: selected" not in text,
        "backlog still marks PhysicsScript rebuild interface rollup slice active",
        failures,
    )
    require(
        "Completed PhysicsScript Rebuild Fixture Selection Proof Plan" in text,
        "backlog missing completed PhysicsScript rebuild fixture selection slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is PhysicsScript Rebuild Fixture Selection Proof Plan. Status: selected" not in text,
        "backlog still marks PhysicsScript rebuild fixture selection slice active",
        failures,
    )
    require(
        "Completed PhysicsScript Explosion Rebuild Fixture Proof Plan" in text,
        "backlog missing completed PhysicsScript explosion fixture slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is PhysicsScript Explosion Rebuild Fixture Proof Plan. Status: selected" not in text,
        "backlog still marks PhysicsScript explosion fixture slice active",
        failures,
    )
    require(
        "Completed PhysicsScript Spawner Rebuild Fixture Proof Plan" in text,
        "backlog missing completed PhysicsScript spawner fixture slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is PhysicsScript Spawner Rebuild Fixture Proof Plan. Status: selected" not in text,
        "backlog still marks PhysicsScript spawner fixture slice active",
        failures,
    )
    require(
        "Completed PhysicsScript Hazard Rebuild Fixture Proof Plan" in text,
        "backlog missing completed PhysicsScript hazard fixture slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is PhysicsScript Hazard Rebuild Fixture Proof Plan. Status: selected" not in text,
        "backlog still marks PhysicsScript hazard fixture slice active",
        failures,
    )
    require(
        "Completed PhysicsScript Feature Rebuild Fixture Proof Plan" in text,
        "backlog missing completed PhysicsScript feature fixture slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is PhysicsScript Feature Rebuild Fixture Proof Plan. Status: selected" not in text,
        "backlog still marks PhysicsScript feature fixture slice active",
        failures,
    )
    require(
        "Completed PhysicsScript Component Rebuild Fixture Proof Plan" in text,
        "backlog missing completed PhysicsScript component fixture slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is PhysicsScript Component Rebuild Fixture Proof Plan. Status: selected" not in text,
        "backlog still marks PhysicsScript component fixture slice active",
        failures,
    )
    require(
        "Completed PhysicsScript Weapon Rebuild Fixture Proof Plan" in text,
        "backlog missing completed PhysicsScript weapon fixture slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is PhysicsScript Weapon Rebuild Fixture Proof Plan. Status: selected" not in text,
        "backlog still marks PhysicsScript weapon fixture slice active",
        failures,
    )
    require(
        "Completed PhysicsScript Round Rebuild Fixture Proof Plan" in text,
        "backlog missing completed PhysicsScript round fixture slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is PhysicsScript Round Rebuild Fixture Proof Plan. Status: selected" not in text,
        "backlog still marks PhysicsScript round fixture slice active",
        failures,
    )
    require(
        "Completed PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan" in text,
        "backlog missing completed PhysicsScript weapon-mode fixture slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is PhysicsScript Weapon-Mode Rebuild Fixture Proof Plan. Status: selected" not in text,
        "backlog still marks PhysicsScript weapon-mode fixture slice active",
        failures,
    )
    require(
        "Completed PhysicsScript Unit Rebuild Fixture Proof Plan" in text,
        "backlog missing completed PhysicsScript unit fixture slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is PhysicsScript Unit Rebuild Fixture Proof Plan. Status: selected" not in text,
        "backlog still marks PhysicsScript unit fixture slice active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is PhysicsScript Fixture Family Completion Rollup Proof Plan. Status: selected" not in text,
        "backlog still marks PhysicsScript fixture-family completion rollup slice active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Static-To-Proof Rebuild Transition Post-PhysicsScript Fixture Next Safe Slice Selection Refresh Proof Plan. Status: selected" not in text,
        "backlog still marks post-PhysicsScript fixture selection-refresh slice active",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Rebuild Contract Extension Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar contract extension slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Rebuild Contract Extension Proof Plan. Status: selected" not in text,
        "backlog still marks texture/mesh material sidecar contract extension slice active",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Rebuild Fixture Matrix Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar fixture matrix slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Rebuild Fixture Matrix Proof Plan. Status: selected" not in text,
        "backlog still marks texture/mesh material sidecar fixture matrix slice active",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Fixture Harness Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer fixture harness slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Fixture Harness Proof Plan. Status: selected" not in text,
        "backlog still marks texture/mesh material sidecar importer fixture harness slice active",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Fixture Harness Materialization Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer fixture harness materialization slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Fixture Harness Materialization Proof Plan. Status: selected" not in text,
        "backlog still marks texture/mesh material sidecar importer fixture harness materialization slice active",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Fixture Harness Consumer Dry-Run Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer fixture harness consumer dry-run slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Fixture Harness Consumer Dry-Run Proof Plan. Status: selected" not in text,
        "backlog still marks texture/mesh material sidecar importer fixture harness consumer dry-run slice active",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Implementation Readiness Gate Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer implementation-readiness gate",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Implementation Readiness Gate Proof Plan. Status: selected" not in text,
        "backlog still marks texture/mesh material sidecar importer implementation-readiness gate active",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Public Contract Skeleton Implementation Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer public contract skeleton",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Public Contract Skeleton Implementation Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer public contract skeleton active",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Safety Boundary Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus safety boundary",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Safety Packet Checklist Population Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus safety packet checklist population",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Inventory Preflight Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus read-only inventory preflight",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Dry-Run Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus read-only manifest dry-run",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Materialization Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus read-only manifest materialization",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Consumer Validation Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus read-only manifest consumer validation",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Safety Boundary Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus safety boundary active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Safety Packet Checklist Population Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus safety packet checklist population active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Inventory Preflight Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus read-only inventory preflight active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Dry-Run Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus read-only manifest dry-run active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Materialization Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus read-only manifest materialization active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Read-Only Manifest Consumer Validation Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus read-only manifest consumer validation active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus redacted manifest importer contract adapter active",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Dry-Run Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus redacted manifest importer contract adapter dry-run",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Dry-Run Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus redacted manifest importer contract adapter dry-run active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Consumer Readiness Gate Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus redacted manifest importer contract adapter consumer readiness active",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Consumer Dry-Run Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus redacted manifest importer contract adapter consumer dry-run",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Redacted Manifest Importer Contract Adapter Consumer Dry-Run Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus redacted manifest importer contract adapter consumer dry-run active",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Readiness Gate Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus real importer dry-run readiness gate",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Readiness Gate Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run readiness gate active",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Boundary Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus real importer dry-run harness boundary",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Boundary Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness boundary active",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Population Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus real importer dry-run harness checklist population",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Population Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness checklist population active",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Validation Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus real importer dry-run harness checklist validation",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Validation Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness checklist validation active",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Readiness Gate Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus real importer dry-run harness checklist readiness gate",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Materialization Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus real importer dry-run harness command materialization",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Checklist Readiness Gate Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness checklist readiness gate active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Materialization Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command materialization active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Readiness Gate Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command readiness gate active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Dry-Run Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command dry-run active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Dry-Run Consumer Validation Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command dry-run consumer validation active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Readiness Gate Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm readiness gate active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Boundary Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm boundary active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Population Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist population active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Validation Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist validation active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Readiness Gate Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist readiness gate active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Materialization Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command materialization active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Readiness Gate Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command readiness gate active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Dry-Run Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command dry-run active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Dry-Run Consumer Validation Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command dry-run consumer-validation active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Readiness Gate Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm-readiness active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Boundary Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm-boundary active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Population Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist-population active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Validation Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist-validation active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Readiness Gate Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist-readiness-gate active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Boundary Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist-boundary active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Materialization Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-materialization active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Consumer Validation Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-consumer-validation active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Readiness Gate Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-readiness-gate active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Dry-Run Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-dry-run active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Dry-Run Consumer Validation Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-dry-run consumer-validation active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Population Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-arm-checklist-population active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Validation Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-arm-checklist-validation active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Readiness Gate Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-arm-checklist-readiness-gate active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Boundary Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-arm-checklist-boundary active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Materialization Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-arm-checklist-command-materialization active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Dry-Run Consumer Validation Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-arm-checklist-command-dry-run-consumer-validation active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Readiness Gate Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-arm-checklist-command-arm-readiness-gate active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Boundary Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-arm-checklist-command-arm-boundary active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Checklist Validation Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-arm-checklist-command-arm-checklist-validation active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Checklist Readiness Gate Proof Plan. Status: selected" in active,
        "active block missing texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-arm-checklist-command-arm-checklist-readiness-gate active lane",
        failures,
    )
    require(
        "The selected active static-to-proof slice is Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Dry-Run Proof Plan. Status: selected" not in active,
        "active block still marks texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-arm-checklist-command-dry-run active lane",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Validation Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-arm-checklist-validation lane",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Readiness Gate Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-arm-checklist-readiness-gate lane",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Boundary Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-arm-checklist-boundary lane",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Consumer Validation Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-arm-checklist-command-consumer-validation lane",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Readiness Gate Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-arm-checklist-command-readiness-gate lane",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Dry-Run Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-arm-checklist-command-dry-run lane",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Dry-Run Consumer Validation Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-arm-checklist-command-dry-run-consumer-validation lane",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Readiness Gate Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-arm-checklist-command-arm-readiness-gate lane",
        failures,
    )
    require(
        "Completed Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Boundary Proof Plan" in text,
        "backlog missing completed texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-arm-checklist-command-arm-boundary lane",
        failures,
    )
    require(
        "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-proof-plan" in active,
        "active block missing texture/mesh material sidecar importer private corpus real importer dry-run harness command arm checklist command arm checklist command-arm-checklist-command-arm-checklist-validation scope",
        failures,
    )
    require(
        active.count("The selected active static-to-proof slice is ") == 1,
        "active block should have exactly one active slice sentence",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Goodie State / Save Command-Effect Fixture Proof Plan. Status: selected" not in text,
        "backlog still marks Goodie State / Save fixture slice active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Goodie State / Save Copied-Baseline Byte-Diff Fixture Proof Plan. Status: selected" not in text,
        "backlog still marks Goodie State / Save copied-baseline byte-diff fixture slice active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Goodie State / Save Clean-Room Codec Interface Proof Plan. Status: selected" not in text,
        "backlog still marks Goodie State / Save clean-room codec interface slice active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Goodie State / Save Runtime-Proof Readiness Gate Plan. Status: selected" not in text,
        "backlog still marks Goodie State / Save runtime-readiness gate slice active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Goodie State / Save AppCore Boundary-Corpus Fixture Matrix Proof Plan. Status: selected" not in text,
        "backlog still marks Goodie State / Save AppCore boundary-corpus fixture matrix slice active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Goodie State / Save AppCore Copied-Baseline Boundary Corpus Harness Proof Plan. Status: selected" not in text,
        "backlog still marks Goodie State / Save AppCore copied-baseline boundary corpus harness slice active",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Command Proof Plan" not in text,
        "backlog still has stale active Level100 launch-command proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Window Smoke Proof Plan" not in text,
        "backlog still has stale active Level100 launch-window smoke proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Screenshot Capture Proof Plan" not in text,
        "backlog still has stale active Level100 screenshot capture proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Launch Smoke Proof Plan" not in text,
        "backlog still has stale active direct Level100 launch smoke proof slice",
        failures,
    )
    require(
        "The selected active static-to-proof slice is MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Screenshot Capture Proof Plan" not in text,
        "backlog still has stale active direct Level100 screenshot capture proof slice",
        failures,
    )
    require(read_text(LORE_BACKLOG) == text, "lore backlog mirror mismatch", failures)

    proof = read_text(PROOF_PLAN)
    require(read_text(LORE_PROOF_PLAN) == proof, "lore proof-plan mirror mismatch", failures)
    physics_plan = read_text(PHYSICS_PLAN)
    require(read_text(LORE_PHYSICS_PLAN) == physics_plan, "lore PhysicsScript proof-plan mirror mismatch", failures)
    physics_result = read_text(PHYSICS_RESULT)
    require(read_text(LORE_PHYSICS_RESULT) == physics_result, "lore PhysicsScript copied-corpus result mirror mismatch", failures)
    destroyable_plan = read_text(DESTROYABLE_PLAN)
    require(read_text(LORE_DESTROYABLE_PLAN) == destroyable_plan, "lore destroyable proof-plan mirror mismatch", failures)
    hud_plan = read_text(HUD_PLAN)
    require(read_text(LORE_HUD_PLAN) == hud_plan, "lore HUD proof-plan mirror mismatch", failures)
    unit_targeting_plan = read_text(UNIT_TARGETING_PLAN)
    require(read_text(LORE_UNIT_TARGETING_PLAN) == unit_targeting_plan, "lore Unit targeting proof-plan mirror mismatch", failures)
    weapon_projectile_plan = read_text(WEAPON_PROJECTILE_PLAN)
    require(read_text(LORE_WEAPON_PROJECTILE_PLAN) == weapon_projectile_plan, "lore Weapon/projectile proof-plan mirror mismatch", failures)
    save_options_plan = read_text(SAVE_OPTIONS_PLAN)
    require(read_text(LORE_SAVE_OPTIONS_PLAN) == save_options_plan, "lore Save/options proof-plan mirror mismatch", failures)
    audio_media_plan = read_text(AUDIO_MEDIA_PLAN)
    require(read_text(LORE_AUDIO_MEDIA_PLAN) == audio_media_plan, "lore Audio/media proof-plan mirror mismatch", failures)
    engine_platform_plan = read_text(ENGINE_PLATFORM_PLAN)
    require(read_text(LORE_ENGINE_PLATFORM_PLAN) == engine_platform_plan, "lore Engine/platform proof-plan mirror mismatch", failures)
    frontend_input_plan = read_text(FRONTEND_INPUT_PLAN)
    require(read_text(LORE_FRONTEND_INPUT_PLAN) == frontend_input_plan, "lore Frontend/input proof-plan mirror mismatch", failures)
    missionscript_plan = read_text(MISSIONSCRIPT_PLAN)
    require(read_text(LORE_MISSIONSCRIPT_PLAN) == missionscript_plan, "lore MissionScript/IScript proof-plan mirror mismatch", failures)
    missionscript_contract = read_text(MISSIONSCRIPT_CONTRACT)
    require(read_text(LORE_MISSIONSCRIPT_CONTRACT) == missionscript_contract, "lore MissionScript/IScript static-contract mirror mismatch", failures)
    world_thing_spawn_plan = read_text(WORLD_THING_SPAWN_PLAN)
    require(read_text(LORE_WORLD_THING_SPAWN_PLAN) == world_thing_spawn_plan, "lore World/Thing/Spawn proof-plan mirror mismatch", failures)
    world_thing_spawn_schema_plan = read_text(WORLD_THING_SPAWN_SCHEMA_PLAN)
    require(read_text(LORE_WORLD_THING_SPAWN_SCHEMA_PLAN) == world_thing_spawn_schema_plan, "lore World/Thing/Spawn schema proof-plan mirror mismatch", failures)
    world_thing_spawn_schema_result = read_text(WORLD_THING_SPAWN_SCHEMA_RESULT)
    require(read_text(LORE_WORLD_THING_SPAWN_SCHEMA_RESULT) == world_thing_spawn_schema_result, "lore World/Thing/Spawn schema result mirror mismatch", failures)
    world_thing_spawn_handoff = read_text(WORLD_THING_SPAWN_HANDOFF)
    require(read_text(LORE_WORLD_THING_SPAWN_HANDOFF) == world_thing_spawn_handoff, "lore World/Thing/Spawn spawner handoff proof mirror mismatch", failures)
    world_thing_spawn_handoff_schema = read_text(WORLD_THING_SPAWN_HANDOFF_SCHEMA)
    require(read_text(LORE_WORLD_THING_SPAWN_HANDOFF_SCHEMA) == world_thing_spawn_handoff_schema, "lore World/Thing/Spawn spawner handoff schema mirror mismatch", failures)
    world_thing_spawn_getthingref = read_text(WORLD_THING_SPAWN_GETTHINGREF)
    require(read_text(LORE_WORLD_THING_SPAWN_GETTHINGREF) == world_thing_spawn_getthingref, "lore World/Thing/Spawn GetThingRef proof mirror mismatch", failures)
    world_thing_spawn_getthingref_schema = read_text(WORLD_THING_SPAWN_GETTHINGREF_SCHEMA)
    require(read_text(LORE_WORLD_THING_SPAWN_GETTHINGREF_SCHEMA) == world_thing_spawn_getthingref_schema, "lore World/Thing/Spawn GetThingRef schema mirror mismatch", failures)
    missionscript_command_effect_rollup = read_text(MISSIONSCRIPT_COMMAND_EFFECT_ROLLUP)
    require(read_text(LORE_MISSIONSCRIPT_COMMAND_EFFECT_ROLLUP) == missionscript_command_effect_rollup, "lore MissionScript command-effect rollup proof mirror mismatch", failures)
    missionscript_command_effect_rollup_schema = read_text(MISSIONSCRIPT_COMMAND_EFFECT_ROLLUP_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_COMMAND_EFFECT_ROLLUP_SCHEMA) == missionscript_command_effect_rollup_schema, "lore MissionScript command-effect rollup schema mirror mismatch", failures)
    missionscript_cutscene_camera = read_text(MISSIONSCRIPT_CUTSCENE_CAMERA)
    require(read_text(LORE_MISSIONSCRIPT_CUTSCENE_CAMERA) == missionscript_cutscene_camera, "lore MissionScript cutscene camera proof mirror mismatch", failures)
    missionscript_cutscene_camera_schema = read_text(MISSIONSCRIPT_CUTSCENE_CAMERA_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_CUTSCENE_CAMERA_SCHEMA) == missionscript_cutscene_camera_schema, "lore MissionScript cutscene camera schema mirror mismatch", failures)
    missionscript_vector_range = read_text(MISSIONSCRIPT_VECTOR_RANGE)
    require(read_text(LORE_MISSIONSCRIPT_VECTOR_RANGE) == missionscript_vector_range, "lore MissionScript vector/range proof mirror mismatch", failures)
    missionscript_vector_range_schema = read_text(MISSIONSCRIPT_VECTOR_RANGE_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_VECTOR_RANGE_SCHEMA) == missionscript_vector_range_schema, "lore MissionScript vector/range schema mirror mismatch", failures)
    missionscript_thing_value = read_text(MISSIONSCRIPT_THING_VALUE)
    require(read_text(LORE_MISSIONSCRIPT_THING_VALUE) == missionscript_thing_value, "lore MissionScript thing-value proof mirror mismatch", failures)
    missionscript_thing_value_schema = read_text(MISSIONSCRIPT_THING_VALUE_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_THING_VALUE_SCHEMA) == missionscript_thing_value_schema, "lore MissionScript thing-value schema mirror mismatch", failures)
    missionscript_hud_display = read_text(MISSIONSCRIPT_HUD_DISPLAY)
    require(read_text(LORE_MISSIONSCRIPT_HUD_DISPLAY) == missionscript_hud_display, "lore MissionScript HUD/display proof mirror mismatch", failures)
    missionscript_hud_display_schema = read_text(MISSIONSCRIPT_HUD_DISPLAY_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_HUD_DISPLAY_SCHEMA) == missionscript_hud_display_schema, "lore MissionScript HUD/display schema mirror mismatch", failures)
    missionscript_player_state = read_text(MISSIONSCRIPT_PLAYER_STATE)
    require(read_text(LORE_MISSIONSCRIPT_PLAYER_STATE) == missionscript_player_state, "lore MissionScript player-state/score proof mirror mismatch", failures)
    missionscript_player_state_schema = read_text(MISSIONSCRIPT_PLAYER_STATE_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_PLAYER_STATE_SCHEMA) == missionscript_player_state_schema, "lore MissionScript player-state/score schema mirror mismatch", failures)
    missionscript_packed_loose = read_text(MISSIONSCRIPT_PACKED_LOOSE)
    require(read_text(LORE_MISSIONSCRIPT_PACKED_LOOSE) == missionscript_packed_loose, "lore MissionScript packed-vs-loose proof mirror mismatch", failures)
    missionscript_packed_loose_schema = read_text(MISSIONSCRIPT_PACKED_LOOSE_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_PACKED_LOOSE_SCHEMA) == missionscript_packed_loose_schema, "lore MissionScript packed-vs-loose schema mirror mismatch", failures)
    missionscript_level100 = read_text(MISSIONSCRIPT_LEVEL100)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100) == missionscript_level100, "lore MissionScript Level100 walkthrough proof mirror mismatch", failures)
    missionscript_level100_schema = read_text(MISSIONSCRIPT_LEVEL100_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_SCHEMA) == missionscript_level100_schema, "lore MissionScript Level100 walkthrough schema mirror mismatch", failures)
    missionscript_level100_text_speaker = read_text(MISSIONSCRIPT_LEVEL100_TEXT_SPEAKER)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_TEXT_SPEAKER) == missionscript_level100_text_speaker, "lore MissionScript Level100 text/speaker proof mirror mismatch", failures)
    missionscript_level100_text_speaker_schema = read_text(MISSIONSCRIPT_LEVEL100_TEXT_SPEAKER_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_TEXT_SPEAKER_SCHEMA) == missionscript_level100_text_speaker_schema, "lore MissionScript Level100 text/speaker schema mirror mismatch", failures)
    missionscript_level100_runtime_boundary = read_text(MISSIONSCRIPT_LEVEL100_RUNTIME_BOUNDARY)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_RUNTIME_BOUNDARY) == missionscript_level100_runtime_boundary, "lore MissionScript Level100 runtime-harness boundary proof mirror mismatch", failures)
    missionscript_level100_runtime_boundary_schema = read_text(MISSIONSCRIPT_LEVEL100_RUNTIME_BOUNDARY_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_RUNTIME_BOUNDARY_SCHEMA) == missionscript_level100_runtime_boundary_schema, "lore MissionScript Level100 runtime-harness boundary schema mirror mismatch", failures)
    missionscript_level100_copied_profile_boundary = read_text(MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_BOUNDARY)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_BOUNDARY) == missionscript_level100_copied_profile_boundary, "lore MissionScript Level100 copied-profile runtime observation boundary proof mirror mismatch", failures)
    missionscript_level100_copied_profile_boundary_schema = read_text(MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_BOUNDARY_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_BOUNDARY_SCHEMA) == missionscript_level100_copied_profile_boundary_schema, "lore MissionScript Level100 copied-profile runtime observation boundary schema mirror mismatch", failures)
    missionscript_level100_artifact_manifest = read_text(MISSIONSCRIPT_LEVEL100_ARTIFACT_MANIFEST)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_ARTIFACT_MANIFEST) == missionscript_level100_artifact_manifest, "lore MissionScript Level100 copied-profile artifact-manifest proof mirror mismatch", failures)
    missionscript_level100_artifact_manifest_schema = read_text(MISSIONSCRIPT_LEVEL100_ARTIFACT_MANIFEST_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_ARTIFACT_MANIFEST_SCHEMA) == missionscript_level100_artifact_manifest_schema, "lore MissionScript Level100 copied-profile artifact-manifest schema mirror mismatch", failures)
    missionscript_level100_template_generation = read_text(MISSIONSCRIPT_LEVEL100_TEMPLATE_GENERATION)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_TEMPLATE_GENERATION) == missionscript_level100_template_generation, "lore MissionScript Level100 manifest-template generation proof mirror mismatch", failures)
    missionscript_level100_template_generation_schema = read_text(MISSIONSCRIPT_LEVEL100_TEMPLATE_GENERATION_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_TEMPLATE_GENERATION_SCHEMA) == missionscript_level100_template_generation_schema, "lore MissionScript Level100 manifest-template generation schema mirror mismatch", failures)
    missionscript_level100_dry_run = read_text(MISSIONSCRIPT_LEVEL100_DRY_RUN)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DRY_RUN) == missionscript_level100_dry_run, "lore MissionScript Level100 manifest dry-run validation proof mirror mismatch", failures)
    missionscript_level100_dry_run_schema = read_text(MISSIONSCRIPT_LEVEL100_DRY_RUN_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DRY_RUN_SCHEMA) == missionscript_level100_dry_run_schema, "lore MissionScript Level100 manifest dry-run validation schema mirror mismatch", failures)
    missionscript_level100_prep = read_text(MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_PREPARATION)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_PREPARATION) == missionscript_level100_prep, "lore MissionScript Level100 copied-profile preparation proof mirror mismatch", failures)
    missionscript_level100_prep_schema = read_text(MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_PREPARATION_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_PREPARATION_SCHEMA) == missionscript_level100_prep_schema, "lore MissionScript Level100 copied-profile preparation schema mirror mismatch", failures)
    missionscript_level100_materialization_preflight = read_text(MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_MATERIALIZATION_PREFLIGHT)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_MATERIALIZATION_PREFLIGHT) == missionscript_level100_materialization_preflight, "lore MissionScript Level100 copied-profile materialization preflight proof mirror mismatch", failures)
    missionscript_level100_materialization_preflight_schema = read_text(MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_MATERIALIZATION_PREFLIGHT_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_MATERIALIZATION_PREFLIGHT_SCHEMA) == missionscript_level100_materialization_preflight_schema, "lore MissionScript Level100 copied-profile materialization preflight schema mirror mismatch", failures)
    missionscript_level100_clean_source = read_text(MISSIONSCRIPT_LEVEL100_CLEAN_SOURCE_SPECIMEN_RESOLUTION)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_CLEAN_SOURCE_SPECIMEN_RESOLUTION) == missionscript_level100_clean_source, "lore MissionScript Level100 clean source specimen resolution proof mirror mismatch", failures)
    missionscript_level100_clean_source_schema = read_text(MISSIONSCRIPT_LEVEL100_CLEAN_SOURCE_SPECIMEN_RESOLUTION_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_CLEAN_SOURCE_SPECIMEN_RESOLUTION_SCHEMA) == missionscript_level100_clean_source_schema, "lore MissionScript Level100 clean source specimen resolution schema mirror mismatch", failures)
    missionscript_level100_materialization = read_text(MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_MATERIALIZATION)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_MATERIALIZATION) == missionscript_level100_materialization, "lore MissionScript Level100 copied-profile materialization proof mirror mismatch", failures)
    missionscript_level100_materialization_schema = read_text(MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_MATERIALIZATION_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_COPIED_PROFILE_MATERIALIZATION_SCHEMA) == missionscript_level100_materialization_schema, "lore MissionScript Level100 copied-profile materialization schema mirror mismatch", failures)
    missionscript_level100_patch = read_text(MISSIONSCRIPT_LEVEL100_COPIED_EXECUTABLE_PATCH)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_COPIED_EXECUTABLE_PATCH) == missionscript_level100_patch, "lore MissionScript Level100 copied-executable patch proof mirror mismatch", failures)
    missionscript_level100_patch_schema = read_text(MISSIONSCRIPT_LEVEL100_COPIED_EXECUTABLE_PATCH_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_COPIED_EXECUTABLE_PATCH_SCHEMA) == missionscript_level100_patch_schema, "lore MissionScript Level100 copied-executable patch schema mirror mismatch", failures)
    missionscript_level100_launch_command = read_text(MISSIONSCRIPT_LEVEL100_LAUNCH_COMMAND)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_LAUNCH_COMMAND) == missionscript_level100_launch_command, "lore MissionScript Level100 launch-command proof mirror mismatch", failures)
    missionscript_level100_launch_command_schema = read_text(MISSIONSCRIPT_LEVEL100_LAUNCH_COMMAND_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_LAUNCH_COMMAND_SCHEMA) == missionscript_level100_launch_command_schema, "lore MissionScript Level100 launch-command schema mirror mismatch", failures)
    missionscript_level100_launch_window_smoke = read_text(MISSIONSCRIPT_LEVEL100_LAUNCH_WINDOW_SMOKE)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_LAUNCH_WINDOW_SMOKE) == missionscript_level100_launch_window_smoke, "lore MissionScript Level100 launch-window smoke proof mirror mismatch", failures)
    missionscript_level100_launch_window_smoke_schema = read_text(MISSIONSCRIPT_LEVEL100_LAUNCH_WINDOW_SMOKE_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_LAUNCH_WINDOW_SMOKE_SCHEMA) == missionscript_level100_launch_window_smoke_schema, "lore MissionScript Level100 launch-window smoke schema mirror mismatch", failures)
    missionscript_level100_screenshot_capture = read_text(MISSIONSCRIPT_LEVEL100_SCREENSHOT_CAPTURE)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_SCREENSHOT_CAPTURE) == missionscript_level100_screenshot_capture, "lore MissionScript Level100 screenshot capture proof mirror mismatch", failures)
    missionscript_level100_screenshot_capture_schema = read_text(MISSIONSCRIPT_LEVEL100_SCREENSHOT_CAPTURE_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_SCREENSHOT_CAPTURE_SCHEMA) == missionscript_level100_screenshot_capture_schema, "lore MissionScript Level100 screenshot capture schema mirror mismatch", failures)
    missionscript_level100_direct_launch_window_smoke = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_LAUNCH_WINDOW_SMOKE)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_LAUNCH_WINDOW_SMOKE) == missionscript_level100_direct_launch_window_smoke, "lore MissionScript Level100 direct launch-window smoke proof mirror mismatch", failures)
    missionscript_level100_direct_launch_window_smoke_schema = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_LAUNCH_WINDOW_SMOKE_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_LAUNCH_WINDOW_SMOKE_SCHEMA) == missionscript_level100_direct_launch_window_smoke_schema, "lore MissionScript Level100 direct launch-window smoke schema mirror mismatch", failures)
    missionscript_level100_direct_screenshot_capture = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_SCREENSHOT_CAPTURE)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_SCREENSHOT_CAPTURE) == missionscript_level100_direct_screenshot_capture, "lore MissionScript Level100 direct screenshot capture proof mirror mismatch", failures)
    missionscript_level100_direct_screenshot_capture_schema = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_SCREENSHOT_CAPTURE_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_SCREENSHOT_CAPTURE_SCHEMA) == missionscript_level100_direct_screenshot_capture_schema, "lore MissionScript Level100 direct screenshot capture schema mirror mismatch", failures)
    missionscript_level100_direct_visual_frame_triage = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_VISUAL_FRAME_TRIAGE)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_VISUAL_FRAME_TRIAGE) == missionscript_level100_direct_visual_frame_triage, "lore MissionScript Level100 direct visual frame triage proof mirror mismatch", failures)
    missionscript_level100_direct_visual_frame_triage_schema = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_VISUAL_FRAME_TRIAGE_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_VISUAL_FRAME_TRIAGE_SCHEMA) == missionscript_level100_direct_visual_frame_triage_schema, "lore MissionScript Level100 direct visual frame triage schema mirror mismatch", failures)
    missionscript_level100_direct_text_overlay_correlation = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_TEXT_OVERLAY_CORRELATION)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_TEXT_OVERLAY_CORRELATION) == missionscript_level100_direct_text_overlay_correlation, "lore MissionScript Level100 direct text-overlay correlation proof mirror mismatch", failures)
    missionscript_level100_direct_text_overlay_correlation_schema = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_TEXT_OVERLAY_CORRELATION_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_TEXT_OVERLAY_CORRELATION_SCHEMA) == missionscript_level100_direct_text_overlay_correlation_schema, "lore MissionScript Level100 direct text-overlay correlation schema mirror mismatch", failures)
    missionscript_level100_direct_timed_frame_set_capture = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_TIMED_FRAME_SET_CAPTURE)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_TIMED_FRAME_SET_CAPTURE) == missionscript_level100_direct_timed_frame_set_capture, "lore MissionScript Level100 direct timed frame-set capture proof mirror mismatch", failures)
    missionscript_level100_direct_timed_frame_set_capture_schema = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_TIMED_FRAME_SET_CAPTURE_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_TIMED_FRAME_SET_CAPTURE_SCHEMA) == missionscript_level100_direct_timed_frame_set_capture_schema, "lore MissionScript Level100 direct timed frame-set capture schema mirror mismatch", failures)
    missionscript_level100_direct_timed_frame_set_text_overlay_progression_correlation = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_TIMED_FRAME_SET_TEXT_OVERLAY_PROGRESSION_CORRELATION)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_TIMED_FRAME_SET_TEXT_OVERLAY_PROGRESSION_CORRELATION) == missionscript_level100_direct_timed_frame_set_text_overlay_progression_correlation, "lore MissionScript Level100 direct timed frame-set text-overlay progression correlation proof mirror mismatch", failures)
    missionscript_level100_direct_timed_frame_set_text_overlay_progression_correlation_schema = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_TIMED_FRAME_SET_TEXT_OVERLAY_PROGRESSION_CORRELATION_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_TIMED_FRAME_SET_TEXT_OVERLAY_PROGRESSION_CORRELATION_SCHEMA) == missionscript_level100_direct_timed_frame_set_text_overlay_progression_correlation_schema, "lore MissionScript Level100 direct timed frame-set text-overlay progression correlation schema mirror mismatch", failures)
    missionscript_level100_direct_runtime_message_display_boundary = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_BOUNDARY)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_BOUNDARY) == missionscript_level100_direct_runtime_message_display_boundary, "lore MissionScript Level100 direct runtime message display boundary proof mirror mismatch", failures)
    missionscript_level100_direct_runtime_message_display_boundary_schema = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_BOUNDARY_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_BOUNDARY_SCHEMA) == missionscript_level100_direct_runtime_message_display_boundary_schema, "lore MissionScript Level100 direct runtime message display boundary schema mirror mismatch", failures)
    missionscript_level100_direct_runtime_message_display_checklist_template = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_TEMPLATE)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_TEMPLATE) == missionscript_level100_direct_runtime_message_display_checklist_template, "lore MissionScript Level100 direct runtime message display checklist-template proof mirror mismatch", failures)
    missionscript_level100_direct_runtime_message_display_checklist_template_schema = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_TEMPLATE_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_TEMPLATE_SCHEMA) == missionscript_level100_direct_runtime_message_display_checklist_template_schema, "lore MissionScript Level100 direct runtime message display checklist-template schema mirror mismatch", failures)
    missionscript_level100_direct_runtime_message_display_checklist_dry_run = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_DRY_RUN)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_DRY_RUN) == missionscript_level100_direct_runtime_message_display_checklist_dry_run, "lore MissionScript Level100 direct runtime message display checklist dry-run proof mirror mismatch", failures)
    missionscript_level100_direct_runtime_message_display_checklist_dry_run_schema = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_DRY_RUN_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_DRY_RUN_SCHEMA) == missionscript_level100_direct_runtime_message_display_checklist_dry_run_schema, "lore MissionScript Level100 direct runtime message display checklist dry-run schema mirror mismatch", failures)
    missionscript_level100_direct_runtime_message_display_checklist_arm_boundary = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_ARM_BOUNDARY)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_ARM_BOUNDARY) == missionscript_level100_direct_runtime_message_display_checklist_arm_boundary, "lore MissionScript Level100 direct runtime message display private-frame arm-boundary proof mirror mismatch", failures)
    missionscript_level100_direct_runtime_message_display_checklist_arm_boundary_schema = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_ARM_BOUNDARY_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_ARM_BOUNDARY_SCHEMA) == missionscript_level100_direct_runtime_message_display_checklist_arm_boundary_schema, "lore MissionScript Level100 direct runtime message display private-frame arm-boundary schema mirror mismatch", failures)
    missionscript_level100_direct_runtime_message_display_checklist_population = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_POPULATION)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_POPULATION) == missionscript_level100_direct_runtime_message_display_checklist_population, "lore MissionScript Level100 direct runtime message display private-frame checklist-population proof mirror mismatch", failures)
    missionscript_level100_direct_runtime_message_display_checklist_population_schema = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_POPULATION_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_CHECKLIST_POPULATION_SCHEMA) == missionscript_level100_direct_runtime_message_display_checklist_population_schema, "lore MissionScript Level100 direct runtime message display private-frame checklist-population schema mirror mismatch", failures)
    missionscript_level100_direct_runtime_message_display_public_safe_summary = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_PUBLIC_SAFE_SUMMARY)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_PUBLIC_SAFE_SUMMARY) == missionscript_level100_direct_runtime_message_display_public_safe_summary, "lore MissionScript Level100 direct runtime message display public-safe summary proof mirror mismatch", failures)
    missionscript_level100_direct_runtime_message_display_public_safe_summary_schema = read_text(MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_PUBLIC_SAFE_SUMMARY_SCHEMA)
    require(read_text(LORE_MISSIONSCRIPT_LEVEL100_DIRECT_RUNTIME_MESSAGE_DISPLAY_PUBLIC_SAFE_SUMMARY_SCHEMA) == missionscript_level100_direct_runtime_message_display_public_safe_summary_schema, "lore MissionScript Level100 direct runtime message display public-safe summary schema mirror mismatch", failures)
    static_to_proof_next_safe_selection = read_text(STATIC_TO_PROOF_NEXT_SAFE_SELECTION)
    require(read_text(LORE_STATIC_TO_PROOF_NEXT_SAFE_SELECTION) == static_to_proof_next_safe_selection, "lore static-to-proof next-safe selection proof mirror mismatch", failures)
    static_to_proof_next_safe_selection_schema = read_text(STATIC_TO_PROOF_NEXT_SAFE_SELECTION_SCHEMA)
    require(read_text(LORE_STATIC_TO_PROOF_NEXT_SAFE_SELECTION_SCHEMA) == static_to_proof_next_safe_selection_schema, "lore static-to-proof next-safe selection schema mirror mismatch", failures)
    world_thing_spawn_crosswalk = read_text(WORLD_THING_SPAWN_CROSSWALK)
    require(read_text(LORE_WORLD_THING_SPAWN_CROSSWALK) == world_thing_spawn_crosswalk, "lore World/Thing/Spawn static-to-rebuild crosswalk proof mirror mismatch", failures)
    world_thing_spawn_crosswalk_schema = read_text(WORLD_THING_SPAWN_CROSSWALK_SCHEMA)
    require(read_text(LORE_WORLD_THING_SPAWN_CROSSWALK_SCHEMA) == world_thing_spawn_crosswalk_schema, "lore World/Thing/Spawn static-to-rebuild crosswalk schema mirror mismatch", failures)
    result = read_text(COPIED_CORPUS_RESULT)
    require(read_text(LORE_COPIED_CORPUS_RESULT) == result, "lore copied-corpus result mirror mismatch", failures)
    material = read_text(MATERIAL_LEDGER_RESULT)
    require(read_text(LORE_MATERIAL_LEDGER_RESULT) == material, "lore material ledger result mirror mismatch", failures)
    material_contract = read_text(MATERIAL_CONTRACT_EXTENSION)
    require(read_text(LORE_MATERIAL_CONTRACT_EXTENSION) == material_contract, "lore material contract extension mirror mismatch", failures)
    material_fixture_matrix = read_text(MATERIAL_FIXTURE_MATRIX)
    require(read_text(LORE_MATERIAL_FIXTURE_MATRIX) == material_fixture_matrix, "lore material fixture matrix mirror mismatch", failures)
    material_importer_harness = read_text(MATERIAL_IMPORTER_HARNESS)
    require(read_text(LORE_MATERIAL_IMPORTER_HARNESS) == material_importer_harness, "lore material importer harness mirror mismatch", failures)
    material_importer_materialization = read_text(MATERIAL_IMPORTER_MATERIALIZATION)
    require(read_text(LORE_MATERIAL_IMPORTER_MATERIALIZATION) == material_importer_materialization, "lore material importer materialization mirror mismatch", failures)
    material_importer_consumer_dry_run = read_text(MATERIAL_IMPORTER_CONSUMER_DRY_RUN)
    require(read_text(LORE_MATERIAL_IMPORTER_CONSUMER_DRY_RUN) == material_importer_consumer_dry_run, "lore material importer consumer dry-run mirror mismatch", failures)
    material_importer_readiness_gate = read_text(MATERIAL_IMPORTER_READINESS_GATE)
    require(read_text(LORE_MATERIAL_IMPORTER_READINESS_GATE) == material_importer_readiness_gate, "lore material importer readiness-gate mirror mismatch", failures)
    material_importer_public_contract_skeleton = read_text(MATERIAL_IMPORTER_PUBLIC_CONTRACT_SKELETON)
    require(read_text(LORE_MATERIAL_IMPORTER_PUBLIC_CONTRACT_SKELETON) == material_importer_public_contract_skeleton, "lore material importer public contract skeleton mirror mismatch", failures)
    material_importer_private_boundary = read_text(MATERIAL_IMPORTER_PRIVATE_BOUNDARY)
    require(read_text(LORE_MATERIAL_IMPORTER_PRIVATE_BOUNDARY) == material_importer_private_boundary, "lore material importer private-corpus safety boundary mirror mismatch", failures)
    material_importer_private_checklist = read_text(MATERIAL_IMPORTER_PRIVATE_CHECKLIST)
    require(read_text(LORE_MATERIAL_IMPORTER_PRIVATE_CHECKLIST) == material_importer_private_checklist, "lore material importer private-corpus safety packet checklist mirror mismatch", failures)
    material_importer_private_readonly_preflight = read_text(MATERIAL_IMPORTER_PRIVATE_READONLY_PREFLIGHT)
    require(read_text(LORE_MATERIAL_IMPORTER_PRIVATE_READONLY_PREFLIGHT) == material_importer_private_readonly_preflight, "lore material importer private-corpus read-only inventory preflight mirror mismatch", failures)
    material_importer_private_manifest_dry_run = read_text(MATERIAL_IMPORTER_PRIVATE_MANIFEST_DRY_RUN)
    require(read_text(LORE_MATERIAL_IMPORTER_PRIVATE_MANIFEST_DRY_RUN) == material_importer_private_manifest_dry_run, "lore material importer private-corpus read-only manifest dry-run mirror mismatch", failures)
    material_importer_private_manifest_materialization = read_text(MATERIAL_IMPORTER_PRIVATE_MANIFEST_MATERIALIZATION)
    require(read_text(LORE_MATERIAL_IMPORTER_PRIVATE_MANIFEST_MATERIALIZATION) == material_importer_private_manifest_materialization, "lore material importer private-corpus read-only manifest materialization mirror mismatch", failures)
    material_importer_private_manifest_consumer_validation = read_text(MATERIAL_IMPORTER_PRIVATE_MANIFEST_CONSUMER_VALIDATION)
    require(read_text(LORE_MATERIAL_IMPORTER_PRIVATE_MANIFEST_CONSUMER_VALIDATION) == material_importer_private_manifest_consumer_validation, "lore material importer private-corpus read-only manifest consumer-validation mirror mismatch", failures)
    material_importer_private_manifest_adapter_dry_run = read_text(MATERIAL_IMPORTER_PRIVATE_MANIFEST_ADAPTER_DRY_RUN)
    require(read_text(LORE_MATERIAL_IMPORTER_PRIVATE_MANIFEST_ADAPTER_DRY_RUN) == material_importer_private_manifest_adapter_dry_run, "lore material importer private-corpus redacted manifest adapter dry-run mirror mismatch", failures)
    material_importer_private_manifest_adapter_consumer_readiness = read_text(MATERIAL_IMPORTER_PRIVATE_MANIFEST_ADAPTER_CONSUMER_READINESS)
    require(
        read_text(LORE_MATERIAL_IMPORTER_PRIVATE_MANIFEST_ADAPTER_CONSUMER_READINESS) == material_importer_private_manifest_adapter_consumer_readiness,
        "lore material importer private-corpus redacted manifest adapter consumer-readiness mirror mismatch",
        failures,
    )
    material_importer_private_manifest_adapter_consumer_dry_run = read_text(MATERIAL_IMPORTER_PRIVATE_MANIFEST_ADAPTER_CONSUMER_DRY_RUN)
    require(
        read_text(LORE_MATERIAL_IMPORTER_PRIVATE_MANIFEST_ADAPTER_CONSUMER_DRY_RUN) == material_importer_private_manifest_adapter_consumer_dry_run,
        "lore material importer private-corpus redacted manifest adapter consumer dry-run mirror mismatch",
        failures,
    )
    material_importer_private_real_importer_readiness = read_text(MATERIAL_IMPORTER_PRIVATE_REAL_IMPORTER_READINESS)
    require(
        read_text(LORE_MATERIAL_IMPORTER_PRIVATE_REAL_IMPORTER_READINESS) == material_importer_private_real_importer_readiness,
        "lore material importer private-corpus real importer dry-run readiness mirror mismatch",
        failures,
    )
    material_importer_private_real_importer_harness_boundary = read_text(MATERIAL_IMPORTER_PRIVATE_REAL_IMPORTER_HARNESS_BOUNDARY)
    require(
        read_text(LORE_MATERIAL_IMPORTER_PRIVATE_REAL_IMPORTER_HARNESS_BOUNDARY) == material_importer_private_real_importer_harness_boundary,
        "lore material importer private-corpus real importer dry-run harness boundary mirror mismatch",
        failures,
    )
    material_importer_private_real_importer_harness_checklist_population = read_text(
        MATERIAL_IMPORTER_PRIVATE_REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION
    )
    require(
        read_text(LORE_MATERIAL_IMPORTER_PRIVATE_REAL_IMPORTER_HARNESS_CHECKLIST_POPULATION)
        == material_importer_private_real_importer_harness_checklist_population,
        "lore material importer private-corpus real importer dry-run harness checklist population mirror mismatch",
        failures,
    )
    material_importer_private_real_importer_harness_checklist_validation = read_text(
        MATERIAL_IMPORTER_PRIVATE_REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION
    )
    require(
        read_text(LORE_MATERIAL_IMPORTER_PRIVATE_REAL_IMPORTER_HARNESS_CHECKLIST_VALIDATION)
        == material_importer_private_real_importer_harness_checklist_validation,
        "lore material importer private-corpus real importer dry-run harness checklist validation mirror mismatch",
        failures,
    )
    for token in (
        "Status: active public-safe proof plan, not runtime proof",
        "copied/app-owned",
        "deterministic manifest and copied-output inventory plan",
        "py -3 tools\\export_asset_catalog.py --self-test",
        "No runtime pixel, GPU upload, visual QA, or parity claim.",
        "texture-mesh-asset-bridge-copied-corpus-proof.md",
        "texture-mesh-material-sidecar-ledger-proof.md",
    ):
        require(token in proof, f"proof plan missing token: {token}", failures)
    for token in (
        "PhysicsScript Schema/Parser Proof Plan",
        "Schema/parser proof checklist and corpus requirement list",
        "physics-script-static-contract.md",
        "CPhysicsScript__Load",
        "statement type ids `1..9`",
        "copied/app-owned script/resource evidence",
        "No mission outcome or serialized completeness claim until corpus proof exists.",
    ):
        require(token in physics_plan, f"PhysicsScript proof plan missing token: {token}", failures)
    for token in (
        "Status: copied-corpus parser/census proof complete, not runtime proof",
        "physics-script-copied-corpus-parser.v1",
        "data/default physics.dat",
        "175603",
        "0x12",
        "777",
        "6803",
        "185",
        "73796",
        "0` unknown top-level ids",
        "shallow framed parser/census proof only",
    ):
        require(token in physics_result, f"PhysicsScript copied-corpus result missing token: {token}", failures)
    for token in (
        "Status: active public-safe proof plan, not runtime proof",
        "destroyable-segments-static-contract.md",
        "CDestructableSegment__RegisterChild",
        "CDestroyableCoreSegment__AreCoreChildrenDestroyed",
        "CDestructableSegmentsController__DamageSegmentByIndexAndUpdateThreshold",
        "CDestroyableSegment__VFunc_03_ApplyDamage",
        "CDestroyableSegment__VFunc_08_HandleSegmentBreak",
        "CDestroyableSegment__VFunc_10_SpawnRubbleEffects",
        "copied-profile guardrails",
        "Stop on crash, non-reproducible target, ambiguous object identity",
        "Use a single selected object/level target; do not broaden into full Unit/BattleEngine",
    ):
        require(token in destroyable_plan, f"destroyable proof plan missing token: {token}", failures)
    for token in (
        "HUD / Frontend Overlay Visual Runtime Proof Plan",
        "Status: active public-safe proof plan, not runtime proof",
        "hud-frontend-overlay-static-contract.md",
        "visual/runtime proof plan only",
        "No screenshot or runtime claim until app-owned capture is run.",
        "CHud__RenderOverlayForViewpoint",
        "CHud__RenderBattleline",
        "CHud__RenderActiveHudComponentPass",
        "CHudComponent__RenderPassEntry",
        "HudRenderState__ApplyOverlaySpriteState",
        "CDXCompass__ApplyRenderStateModulate",
        "CDXCompass__ApplyRenderStateAdditive",
        "copied-profile guardrails",
        "Stop on crash, non-reproducible state, ambiguous viewpoint/object identity",
        "No screenshot/capture proof",
    ):
        require(token in hud_plan, f"HUD proof plan missing token: {token}", failures)
    for token in (
        "Weapon / Projectile Spawn Handoff Proof Plan",
        "Status: active public-safe proof plan, not runtime proof",
        "weapon-projectile-spawn-handoff-proof-plan",
        "unit-battleengine-gameplay-static-contract.md",
        "wave1160-weapon-projectile-targeting-current-risk-review",
        "battleengine-walkerpart-weapon-spine-review-wave1027",
        "battleengine-jetpart-weapon-status-review-wave1029",
        "projectile-burst-spawn-spine-review-wave1020",
        "0x00413cc0 CBattleEngineWalkerPart__FireWeapon",
        "0x004140d0 CBattleEngineWalkerPart__WeaponFired",
        "0x00412050 CBattleEngineJetPart__WeaponFired",
        "0x005061f0 CWeapon__DoesTargetMaskMatchDistanceProfile",
        "0x00506930 CWeapon__HandleFireBurstEvent",
        "0x00506010 ProjectileBurst__SpawnFromPercentBucketFallback",
        "0x005069f0 ProjectileBurst__SpawnFromCurrentPreset",
        "0x004db150 CRound__SpawnConfiguredProjectile",
        "0x004db630 CRound__ArmProjectileAndSpawnTrailEffect",
        "Wave1161/Wave1162 collision and terrain rows as context only",
        "copied-profile guardrails",
        "Stop on crash, non-reproducible weapon path, ambiguous weapon identity",
    ):
        require(token in weapon_projectile_plan, f"Weapon/projectile proof plan missing token: {token}", failures)
    for token in (
        "Unit Targeting / Active-Reader Proof Plan",
        "Status: active public-safe proof plan, not runtime proof",
        "unit-battleengine-gameplay-static-contract.md",
        "target acquisition, candidate filtering/scoring, active-reader assignment, heading update, and iterator snapshot behavior",
        "wave1215-unit-targeting-combat-residual-current-risk-review",
        "cunit-active-reader-targeting-review-wave927",
        "0x004027c0 CAirGuide__AcquireNearestTargetReader",
        "0x00445070 CDiveBomber__SelectTarget",
        "0x0044e640 ComponentTargeting__ScanListsAndMaybeTriggerAction_0044e640",
        "0x00477cb0 CSquadNormal__SelectBestEngagementTarget",
        "0x004ea8d0 CRelaxedSquad__CreateIterator",
        "0x00428b50 CUnit__SetReaderAndComputeRelativeYaw",
        "0x00429270 CUnitAI__UpdateHeadingTowardTargetClamped",
        "0x004fd3d0 CUnit__IsCandidateSideCompatibleForTargeting",
        "copied-profile guardrails",
        "Stop on crash, non-reproducible target, ambiguous unit/squad identity",
        "Use a single selected unit/squad/state target; do not broaden into weapon fire",
    ):
        require(token in unit_targeting_plan, f"Unit targeting proof plan missing token: {token}", failures)
    for token in (
        "Frontend / Input / Game Loop Proof Plan",
        "Status: active public-safe proof plan, not runtime proof",
        "frontend-input-game-loop-proof-plan",
        "frontend-input-game-loop-static-review-wave907",
        "frontend-text-layout-review-wave922",
        "wave1179-input-audio-support-current-risk-review",
        "wave1197-fepbeconfig-frontend-residual-current-risk-review",
        "`436` selected function rows",
        "`33` families",
        "0x0046eee0 CGame__MainLoop",
        "0x004684d0 CFrontEnd__Run",
        "0x0042db40 CController__DoMappings",
        "0x00513370 PlatformInput__PollPadState",
        "0x004d06e0 CPauseMenu__ResumeGameAndPersistOptions",
        "0x00541790 CDXFrontEndVideo__Render",
        "Stop on installed-game mutation need",
    ):
        require(token in frontend_input_plan, f"Frontend/input proof plan missing token: {token}", failures)
    for token in (
        "MissionScript / IScript Proof Plan",
        "Status: active public-safe proof plan, not runtime proof",
        "missionscript-iscript-proof-plan",
        "missionscript-static-review-wave903",
        "wave1189-missionscript-bytecode-iscript-current-risk-review",
        "wave1208-cbooldatatype-current-risk-review",
        "`169` saved Ghidra rows",
        "`144` contiguous `0x40`-byte command descriptor records",
        "`49` `IScript__*` functions",
        "`37` datatype rows",
        "`19` instruction/opcode rows",
        "`22` `CScriptObjectCode`",
        "`13` `CScriptEventNB`",
        "`7` `CMissionScriptObjectCode`",
        "`5` `CEventFunction` rows",
        "command descriptor schema",
        "IScript command handlers",
        "VM/datatype/opcode behavior",
        "event/object-code lifecycle",
        "loose MSL corpus linkage",
        "Mission outcome/event proof design",
        "thing/spawn/object-reference bridge",
        "message/objective/HUD command design",
        "ScriptCommandRegistry__InitBuiltins",
        "0x0064ce50",
        "0x0064f210",
        "IScript__ScheduleEvent",
        "IScript__SetSlotSave",
        "IScript__LevelWon",
        "CScriptObjectCode__Run",
        "CScriptEventNB__PostEvent",
        "CMissionScriptObjectCode__LoadAsync",
        "CInstructionOP_PLUS__VFunc_00_0052e180",
        "CInstructionOP_MINUS__VFunc_00_0052e1d0",
        "CInstructionOP_MULTIPLY__VFunc_00_0052e220",
        "CInstructionOP_DIVIDE__VFunc_00_0052e270",
        "CInstructionOP_CMP__VFunc_00_0052e330",
        "CBoolDataType__Equals",
        "CBoolDataType__NotEquals",
        "CBoolDataType__Assign",
        r"[maintainer-local-ghidra-backup-root]\BEA_20260526-095411_post_wave903_missionscript_static_review_verified",
        r"[maintainer-local-ghidra-backup-root]\BEA_20260606-164704_post_wave1189_missionscript_bytecode_iscript_current_risk_review_verified",
        r"[maintainer-local-ghidra-backup-root]\BEA_20260607-040938_post_wave1208_cbooldatatype_current_risk_review_verified",
    ):
        require(token in missionscript_plan, f"MissionScript/IScript proof plan missing token: {token}", failures)
    for token in (
        "MissionScript / IScript Static Contract",
        "Status: static contract extraction complete, not runtime proof",
        "missionscript-iscript-static-contract",
        "missionscript-static-review-wave903",
        "wave1189-missionscript-bytecode-iscript-current-risk-review",
        "wave1208-cbooldatatype-current-risk-review",
        "`169` selected MissionScript family rows",
        "`144` contiguous `0x40`-byte command descriptor records",
        "`49` `IScript__*` functions",
        "`37` datatype rows",
        "`19` instruction/opcode rows",
        "`22` `CScriptObjectCode`",
        "`13` `CScriptEventNB`",
        "`7` `CMissionScriptObjectCode`",
        "`5` `CEventFunction`",
        "`57` level rows",
        "`418` `GetThingRef`",
        "`18` `SpawnThing`",
        "`436` total thing/spawn refs",
        "World/thing/spawn bridge",
        "world-thing-spawn-object-reference-proof-plan.md",
        r"[maintainer-local-ghidra-backup-root]\BEA_20260526-095411_post_wave903_missionscript_static_review_verified",
    ):
        require(token in missionscript_contract, f"MissionScript/IScript static contract missing token: {token}", failures)
    for token in (
        "World / Thing / Spawn / Object-Reference Bridge Proof Plan",
        "Status: proof plan complete, not runtime proof",
        "world-thing-spawn-object-reference-proof-plan",
        "world-thing-spawn-copied-corpus-schema-proof-plan.md",
        "missionscript-iscript-static-contract.md",
        "missionscript-iscript-proof-plan.md",
        "IScript__GetThingRef",
        "IScript__SpawnThing",
        "0x0052ff30",
        "`144` contiguous `0x40`-byte command descriptor records",
        "`57` level rows",
        "`418` `GetThingRef`",
        "`18` `SpawnThing`",
        "`436` total thing/spawn refs",
        "0x005392a0 CScriptObjectCode__CollectSpawnThings",
        "opcode `0x18`",
        "CWorldMeshList__Add",
        "CWorld__LoadWorld",
        "CWorldPhysicsManager__CreateThingByType",
        "0x0048c650 InitThing__CreateThingByType",
        "0x004e3c60 CSpawnerThng__DoSpawn",
        "copied/app-owned only, no runtime object identity claim",
    ):
        require(token in world_thing_spawn_plan, f"World/Thing/Spawn proof plan missing token: {token}", failures)
    for token in (
        "World / Thing / Spawn Copied-Corpus Object-Reference Schema Proof Plan",
        "Status: active public-safe copied-corpus schema proof plan, not runtime proof",
        "world-thing-spawn-copied-corpus-schema-proof-plan",
        "world-thing-spawn-object-reference-proof-plan.md",
        "Raw detailed call rows",
        "Published unique object-reference rows",
        "Spawn-preserving unique rows",
        "`574`",
        "`70`",
        "`644`",
        "`418`",
        "`18`",
        "`436`",
        "`29`",
        "`447`",
        "`34` raw `SpawnThing` rows",
        "`6` unique `Level + Dir + Call + Thing` rows",
        "`4` unique thing labels",
        "`8` unique `Level + Dir + File + Thing + Spawner` rows",
        "level022",
        "Hangar.msl",
        "Target Drone",
        "SpawnerA",
        "SpawnerB",
        "0x005392a0 CScriptObjectCode__CollectSpawnThings",
        "opcode `0x18`",
        "CWorldMeshList__Add",
        "0x004e3c60 CSpawnerThng__DoSpawn",
        "not runtime proof",
    ):
        require(token in world_thing_spawn_schema_plan, f"World/Thing/Spawn schema proof plan missing token: {token}", failures)
    for token in (
        "Engine / Platform / Math / Memory Support Proof Plan",
        "Status: active public-safe proof plan, not runtime proof",
        "engine-platform-math-memory-support-proof-plan",
        "engine-platform-support-static-review-wave909",
        "crt-fpu-runtime-tail-review-wave1041",
        "memory-heap-allocator-review-wave1042",
        "render-state-matrix-support-review-wave1095",
        "wave1214-math-color-screen-dispatch-current-risk-review",
        "CEngine__Init",
        "CD3DApplication__BuildDeviceList",
        "CConsole__RegisterBuiltinCommands",
        "CMonitor__AddDeletionEvent",
        "CMemoryHeap__Alloc",
        "Math__InvLerpClamp01",
        "D3DStateCache__SetSlotMode4or5",
        "CRT__FpuIntrinsicDispatch2Thunk",
        "Stop on installed-game mutation need",
    ):
        require(token in engine_platform_plan, f"Engine/platform proof plan missing token: {token}", failures)
    for token in (
        "Audio / Media / Cutscene / Camera Proof Plan",
        "Status: active public-safe proof plan, not runtime proof",
        "audio-media-cutscene-camera-proof-plan",
        "audio-media-cutscene-static-review-wave908",
        "ogg-message-lifecycle-review-wave1015",
        "wave1179-input-audio-support-current-risk-review",
        "wave1219-final-score16-current-risk-review",
        "CSoundManager__Init",
        "CPCSoundManager__DecodeADPCM",
        "COggLoader__ThreadProc_ReadPathIntoBuffer",
        "CBinkOpenThread__WorkerMain",
        "CCutscene__Update",
        "CRTCutscene__BuildCurrentFrameOutputs",
        "CMovieCamera__GetPos",
        "CPanCamera__Update",
        "copied profile or app-owned artifact root",
        "Stop on private media leakage risk",
    ):
        require(token in audio_media_plan, f"Audio/media proof plan missing token: {token}", failures)
    for token in (
        "Save / Options Controller Byte-Preservation Proof Plan",
        "Status: active public-safe proof plan, not runtime proof",
        "save-options-controller-byte-preservation-proof-plan",
        "save-options-static-review-wave902",
        "career-controller-residual-review-wave1044",
        "wave1212-options-detail-tweak-current-risk-review",
        "10004",
        "0x2714",
        "0x4BD1",
        "file_offset = 0x0002 + career_offset",
        "0x24BE-0x26BD",
        "0x26BE-0x2713",
        "N=16",
        "flag=0",
        "flag=1",
        "mControllerConfigurationNum[0/1]",
        "g_ControlSchemeIndex=0",
        "copied real `.bes` and `defaultoptions.bea`",
        "Never synthesize a save/options buffer from scratch",
        "Stop on wrong size, wrong version, unexpected diff outside allowlist",
    ):
        require(token in save_options_plan, f"Save/options proof plan missing token: {token}", failures)
    for token in (
        "Status: copied-corpus inventory/export proof complete, not runtime proof",
        "not a new static re-audit wave",
        "8574",
        "250335133",
        "TEXT 18857",
        "MESH 3492",
        "GDIE 232",
        "601/601",
        "209/209",
        "206/206",
        "42/42",
        "4050",
        "texture-mesh-material-sidecar-ledger-proof.md",
        "Follow-up generated material/sidecar ledger proof",
    ):
        require(token in result, f"copied-corpus result missing token: {token}", failures)
    for token in (
        "Status: generated material/sidecar ledger proof complete, not runtime proof",
        "asset-material-sidecar-ledger.v1",
        "352/352",
        "213",
        "0` missing sidecar",
        "0` catalog-missing",
        "Embedded mesh duplicate-output caveat",
    ):
        require(token in material, f"material ledger result missing token: {token}", failures)


def check_front_doors(failures: list[str]) -> None:
    progress = json.loads(read_text(PROGRESS))
    require(progress["functionQuality"]["totalFunctions"] == 6411, "progress total mismatch", failures)
    require(progress["functionQuality"]["commentlessFunctions"] == 0, "progress commentless mismatch", failures)
    require(progress["functionQuality"]["undefinedSignatures"] == 0, "progress undefined mismatch", failures)
    require(progress["functionQuality"]["paramSignatures"] == 0, "progress param_N mismatch", failures)
    current = progress["post100Reaudit"]["currentRiskRank"]
    require(current["focusedReviewed"] == 1179, "current-risk reviewed mismatch", failures)
    require(current["remainingFocusedAfterLatestReview"] == 0, "current-risk remaining mismatch", failures)
    require(current["liveFocusedCandidatesAfterLatestReview"] == 1117, "live focused count mismatch", failures)
    require(current["legacyAdditiveReviewedDeprecated"] == 1210, "legacy additive mismatch", failures)
    require(current["isWave911Reconstruction"] is False, "Wave911 reconstruction flag mismatch", failures)

    for path in (MAPPED, RE_INDEX, BIN_INDEX, STRATEGY):
        text = read_text(path)
        require("static-to-proof-rebuild-transition-backlog.md" in text, f"{path.relative_to(ROOT)} missing backlog link", failures)
    for path in (MAPPED, RE_INDEX, BIN_INDEX, GAME_ASSETS_INDEX):
        text = read_text(path)
        for token in (
            "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Dry-Run Proof Plan",
            "texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-proof.md",
            "texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-proof.v1.json",
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-complete-public-safe-readiness-row-consumption-not-real-importer-execution",
            "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Dry-Run Consumer Validation Proof Plan",
            "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-proof-plan",
            "sourceProofCount=61",
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateProofCount=60",
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateInterfaceCount=10",
            "commandDryRunInterfaceCount=10",
            "commandReadinessGateRowsConsumed=99",
            "commandDryRunRows=99",
            "passedCommandDryRunRowCount=99",
            "failedCommandDryRunRowCount=0",
            "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRowCount=99",
            "publicAllowedOutputCount=113",
            "redactedFieldCount=53",
            "falseGuardCount=292",
            "zeroCounterCount=238",
            "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Readiness Gate Proof Plan",
            "texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-consumer-validation-proof.md",
            "texture-mesh-material-sidecar-command-arm-checklist-command-dry-run-consumer-validation-proof.v1.json",
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-complete-public-safe-non-dispatched-command-dry-run-consumed-not-real-importer-execution",
            "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Readiness Gate Proof Plan",
            "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-proof-plan",
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-complete-public-safe-readiness-row-consumption-not-real-importer-execution",
            "sourceProofCount=62",
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunProofCount=61",
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunInterfaceCount=10",
            "commandDryRunConsumerValidationInterfaceCount=10",
            "commandDryRunRowsConsumed=99",
            "commandDryRunConsumerValidationRows=99",
            "validatedNonDispatchedCommandDryRunRowCount=99",
            "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowCount=99",
            "publicSafeCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationArtifactRows=1",
            "publicAllowedOutputCount=116",
            "redactedFieldCount=54",
            "falseGuardCount=297",
            "zeroCounterCount=242",
            "commandArmReadinessGateLaneSelected=true",
            "unknownAyaArchiveClassCount=0",
            "outputArtifactRows=0",
            "rawFilenameRows=0",
            "byteLengthRows=0",
            "texture-mesh-material-sidecar-command-arm-checklist-command-arm-readiness-gate-proof.md",
            "texture-mesh-material-sidecar-command-arm-checklist-command-arm-readiness-gate-proof.v1.json",
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-complete-public-safe-readiness-only-not-command-arming",
            "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Boundary Proof Plan",
            "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-boundary-proof-plan",
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-complete-public-safe-non-dispatched-command-dry-run-consumed-not-real-importer-execution",
            "sourceProofCount=63",
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationProofCount=62",
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationInterfaceCount=10",
            "commandArmReadinessGateInterfaceCount=10",
            "commandDryRunConsumerValidationRowsConsumed=99",
            "commandArmReadinessGateRows=99",
            "passedCommandArmReadinessGateRowCount=99",
            "readyForLaterCommandArmBoundaryRowCount=99",
            "publicSafeCommandArmReadinessGateArtifactRows=1",
            "publicAllowedOutputCount=119",
            "redactedFieldCount=55",
            "falseGuardCount=305",
            "zeroCounterCount=248",
            "commandArmBoundaryLaneSelected=true",
            "texture-mesh-material-sidecar-command-arm-checklist-command-arm-boundary-proof.md",
            "texture-mesh-material-sidecar-command-arm-checklist-command-arm-boundary-proof.v1.json",
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmBoundaryStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-boundary-defined-public-safe-no-command-arming",
            "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Checklist Population Proof Plan",
            "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-proof-plan",
            "sourceCommandArmReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-complete-public-safe-readiness-only-not-command-arming",
            "sourceProofCount=64",
            "sourceCommandArmReadinessGateProofCount=63",
            "sourceCommandArmReadinessGateInterfaceCount=10",
            "commandArmBoundaryInterfaceCount=10",
            "commandArmReadinessGateRowsConsumed=99",
            "commandArmBoundaryRows=99",
            "definedCommandArmBoundaryRowCount=99",
            "passedCommandArmBoundaryRowCount=99",
            "readyForLaterCommandArmChecklistPopulationRowCount=99",
            "publicSafeCommandArmBoundaryArtifactRows=1",
            "publicAllowedOutputCount=122",
            "redactedFieldCount=56",
            "stopConditionCount=12",
            "falseGuardCount=308",
            "zeroCounterCount=250",
            "commandArmChecklistPopulationLaneSelected=true",
            "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-population-proof.md",
            "texture-mesh-material-sidecar-command-arm-checklist-command-arm-checklist-population-proof.v1.json",
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandArmChecklistPopulationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-population-complete-public-safe-not-run-checklist-populated-no-command-arming",
            "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Arm Checklist Validation Proof Plan",
            "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-checklist-validation-proof-plan",
            "sourceCommandArmBoundaryStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-arm-boundary-defined-public-safe-no-command-arming",
            "sourceProofCount=65",
            "sourceCommandArmBoundaryProofCount=64",
            "sourceCommandArmBoundaryInterfaceCount=10",
            "commandArmBoundaryRowsConsumed=99",
            "commandArmChecklistPopulationRows=99",
            "populatedCommandArmChecklistRowCount=99",
            "passedCommandArmChecklistPopulationRowCount=99",
            "readyForLaterCommandArmChecklistValidationRowCount=99",
            "publicAllowedOutputCount=122",
            "redactedFieldCount=56",
            "falseGuardCount=313",
            "zeroCounterCount=257",
            "commandArmChecklistValidationLaneSelected=true",
            "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Readiness Gate Proof Plan",
            "texture-mesh-material-sidecar-command-arm-checklist-command-readiness-gate-proof.md",
            "texture-mesh-material-sidecar-command-arm-checklist-command-readiness-gate-proof.v1.json",
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-readiness-gate-complete-public-safe-readiness-only-not-command-arming",
            "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Checklist Command Dry-Run Proof Plan",
            "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-checklist-command-dry-run-proof-plan",
            "sourceProofCount=60",
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationProofCount=59",
            "sourceCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandConsumerValidationInterfaceCount=12",
            "commandReadinessGateInterfaceCount=10",
            "commandReadinessGateRows=99",
            "passedCommandReadinessGateRowCount=99",
            "failedCommandReadinessGateRowCount=0",
            "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmChecklistCommandDryRunRowCount=99",
            "publicAllowedOutputCount=109",
            "redactedFieldCount=50",
            "falseGuardCount=286",
            "zeroCounterCount=235",
            "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Readiness Gate Proof Plan",
            "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-proof-plan.md",
            "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-proof-plan.v1.json",
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandArmReadinessGateStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-complete-public-safe-readiness-only-not-command-arming",
            "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Boundary Proof Plan",
            "texture-mesh-material-sidecar-command-arm-boundary-proof",
            "sourceProofCount=52",
            "sourceCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationProofCount=51",
            "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRowsConsumed=99",
            "commandArmChecklistCommandArmChecklistCommandArmReadinessGateRows=99",
            "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmBoundaryRowCount=99",
            "publicAllowedOutputCount=85",
            "redactedFieldCount=42",
            "falseGuardCount=243",
            "zeroCounterCount=201",
            "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Dry-Run Consumer Validation Proof Plan",
            "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-proof-plan.md",
            "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-proof-plan.v1.json",
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-complete-public-safe-non-dispatched-command-arm-checklist-command-arm-checklist-command-dry-run-consumed-not-real-importer-execution",
            "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Arm Readiness Gate Proof Plan",
            "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-arm-readiness-gate-proof-plan",
            "sourceProofCount=51",
            "sourceCommandArmChecklistCommandArmChecklistCommandDryRunProofCount=50",
            "commandArmChecklistCommandArmChecklistCommandDryRunRowsConsumed=99",
            "commandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRows=99",
            "readyForLaterCommandArmChecklistCommandArmChecklistCommandArmReadinessGateRowCount=99",
            "publicAllowedOutputCount=82",
            "redactedFieldCount=41",
            "falseGuardCount=238",
            "zeroCounterCount=195",
            "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Dry-Run Proof Plan",
            "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-dry-run-proof-plan.md",
            "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-dry-run-proof-plan.v1.json",
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandDryRunStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-dry-run-complete-public-safe-readiness-row-consumption-not-real-importer-execution",
            "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Dry-Run Consumer Validation Proof Plan",
            "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-dry-run-consumer-validation-proof-plan",
            "sourceProofCount=50",
            "sourceCommandArmChecklistCommandArmChecklistCommandReadinessGateProofCount=49",
            "commandArmChecklistCommandArmChecklistCommandReadinessGateRowsConsumed=99",
            "commandArmChecklistCommandArmChecklistCommandDryRunRows=99",
            "readyForLaterCommandArmChecklistCommandArmChecklistCommandDryRunConsumerValidationRowCount=99",
            "publicAllowedOutputCount=79",
            "redactedFieldCount=40",
            "falseGuardCount=233",
            "zeroCounterCount=191",
            "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Consumer Validation Proof Plan",
            "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-consumer-validation-proof-plan.md",
            "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-consumer-validation-proof-plan.v1.json",
            "privateCorpusRealImporterDryRunHarnessCommandArmChecklistCommandArmChecklistCommandConsumerValidationStatus=texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-consumer-validation-complete-public-safe-non-armed-command-contract-consumed-not-real-importer-execution",
            "Texture / Mesh Material Sidecar Importer Private Corpus Real Importer Dry-Run Harness Command Arm Checklist Command Arm Checklist Command Readiness Gate Proof Plan",
            "texture-mesh-material-sidecar-importer-private-corpus-real-importer-dry-run-harness-command-arm-checklist-command-arm-checklist-command-readiness-gate-proof-plan",
            "sourceProofCount=48",
            "sourceCommandArmChecklistCommandArmChecklistCommandMaterializationProofCount=47",
            "commandArmChecklistCommandArmChecklistCommandContractRowsConsumed=99",
            "commandConsumerValidationRows=99",
            "readyForLaterCommandArmChecklistCommandArmChecklistCommandReadinessGateRowCount=99",
            "publicAllowedOutputCount=72",
            "redactedFieldCount=37",
            "falseGuardCount=221",
            "zeroCounterCount=182",
            "publicLeakCheck=PASS",
        ):
            require(token in text, f"{path.relative_to(ROOT)} missing command consumer-validation front-door token: {token}", failures)
    for path in (MAPPED, RE_INDEX):
        text = read_text(path)
        require("texture-mesh-asset-bridge-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing proof-plan link", failures)
        require("texture-mesh-asset-bridge-copied-corpus-proof.md" in text, f"{path.relative_to(ROOT)} missing copied-corpus result link", failures)
        require("texture-mesh-material-sidecar-ledger-proof.md" in text, f"{path.relative_to(ROOT)} missing material ledger result link", failures)
        require("texture-mesh-material-sidecar-rebuild-contract-extension-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing material sidecar contract extension link", failures)
        require("texture-mesh-material-sidecar-rebuild-fixture-matrix-proof.md" in text, f"{path.relative_to(ROOT)} missing material sidecar fixture matrix link", failures)
        require("texture-mesh-material-sidecar-importer-fixture-harness-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing material sidecar importer harness link", failures)
        require("physics-script-schema-parser-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing PhysicsScript proof-plan link", failures)
        require("physics-script-copied-corpus-parser-proof.md" in text, f"{path.relative_to(ROOT)} missing PhysicsScript copied-corpus result link", failures)
        require("destroyable-segments-damage-break-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing destroyable proof-plan link", failures)
        require("hud-frontend-overlay-visual-runtime-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing HUD proof-plan link", failures)
        require("unit-targeting-active-reader-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing Unit targeting proof-plan link", failures)
        require("weapon-projectile-spawn-handoff-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing Weapon/projectile proof-plan link", failures)
        require("save-options-controller-byte-preservation-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing Save/options proof-plan link", failures)
        require("audio-media-cutscene-camera-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing Audio/media proof-plan link", failures)
        require("engine-platform-math-memory-support-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing Engine/platform proof-plan link", failures)
        require("frontend-input-game-loop-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing Frontend/input proof-plan link", failures)
        require("missionscript-iscript-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing MissionScript/IScript proof-plan link", failures)
        require("missionscript-iscript-static-contract.md" in text, f"{path.relative_to(ROOT)} missing MissionScript/IScript static-contract link", failures)
        require("world-thing-spawn-object-reference-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing World/Thing/Spawn proof-plan link", failures)
        require("world-thing-spawn-copied-corpus-schema-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing World/Thing/Spawn schema proof-plan link", failures)
        require("world-thing-spawn-copied-corpus-schema-proof.md" in text, f"{path.relative_to(ROOT)} missing World/Thing/Spawn schema result link", failures)
        require("world-thing-spawn-spawner-handoff-static-proof.md" in text, f"{path.relative_to(ROOT)} missing World/Thing/Spawn spawner handoff proof link", failures)
        require("world-thing-spawn-spawner-handoff-static.v1.json" in text, f"{path.relative_to(ROOT)} missing World/Thing/Spawn spawner handoff schema link", failures)
        require("world-thing-spawn-getthingref-object-reference-static-proof.md" in text, f"{path.relative_to(ROOT)} missing World/Thing/Spawn GetThingRef proof link", failures)
        require("world-thing-spawn-getthingref-object-reference-static.v1.json" in text, f"{path.relative_to(ROOT)} missing World/Thing/Spawn GetThingRef schema link", failures)
        require("missionscript-cutscene-pan-camera-position-command-effect-static-proof.md" in text, f"{path.relative_to(ROOT)} missing MissionScript cutscene camera proof link", failures)
        require("missionscript-cutscene-pan-camera-position-command-effect.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript cutscene camera schema link", failures)
        require("missionscript-vector-range-command-effect-static-proof.md" in text, f"{path.relative_to(ROOT)} missing MissionScript vector/range proof link", failures)
        require("missionscript-vector-range-command-effect.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript vector/range schema link", failures)
        require("missionscript-thing-value-engine-helper-command-effect-static-proof.md" in text, f"{path.relative_to(ROOT)} missing MissionScript thing-value proof link", failures)
        require("missionscript-thing-value-engine-helper-command-effect.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript thing-value schema link", failures)
        require("missionscript-hud-display-command-effect-static-proof.md" in text, f"{path.relative_to(ROOT)} missing MissionScript HUD/display proof link", failures)
        require("missionscript-hud-display-command-effect.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript HUD/display schema link", failures)
        require("missionscript-player-state-score-command-effect-static-proof.md" in text, f"{path.relative_to(ROOT)} missing MissionScript player-state/score proof link", failures)
        require("missionscript-player-state-score-command-effect.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript player-state/score schema link", failures)
        require("missionscript-event-object-code-lifecycle-proof.md" in text, f"{path.relative_to(ROOT)} missing MissionScript event/object-code lifecycle proof link", failures)
        require("missionscript-event-object-code-lifecycle.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript event/object-code lifecycle schema link", failures)
        require("missionscript-packed-vs-loose-script-selection-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing MissionScript packed-vs-loose proof link", failures)
        require("missionscript-packed-vs-loose-script-selection.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript packed-vs-loose schema link", failures)
        require("missionscript-level100-tutorial-static-walkthrough-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 walkthrough proof link", failures)
        require("missionscript-level100-tutorial-static-walkthrough.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 walkthrough schema link", failures)
        require("missionscript-level100-tutorial-runtime-harness-boundary-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime-harness boundary proof link", failures)
        require("missionscript-level100-tutorial-runtime-harness-boundary.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime-harness boundary schema link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-boundary-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 copied-profile runtime observation boundary proof link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-boundary.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 copied-profile runtime observation boundary schema link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 copied-profile artifact-manifest proof link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 copied-profile artifact-manifest schema link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-template-generation-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 manifest-template proof link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-templates.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 manifest-template schema link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-dry-run-validation-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 manifest dry-run validation proof link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-dry-run-validation.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 manifest dry-run validation schema link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 copied-profile preparation proof link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 copied-profile preparation schema link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight-proof.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 copied-profile materialization preflight proof link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 copied-profile materialization preflight schema link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-clean-source-specimen-resolution-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 clean source specimen resolution proof link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-clean-source-specimen-resolution.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 clean source specimen resolution schema link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-proof.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 copied-profile materialization proof link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 copied-profile materialization schema link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch-proof.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 copied-executable patch proof link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 copied-executable patch schema link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 launch-command proof link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-launch-command.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 launch-command schema link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke-proof.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 launch-window smoke proof link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-launch-window-smoke.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 launch-window smoke schema link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture-proof.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 screenshot capture proof link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-screenshot-capture.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 screenshot capture schema link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke-proof.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 direct launch-window smoke proof link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-launch-window-smoke.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 direct launch-window smoke schema link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture-proof.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 direct screenshot capture proof link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 direct screenshot capture schema link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage-proof.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 direct visual frame triage proof link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 direct visual frame triage schema link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-text-overlay-correlation-proof.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 direct text-overlay correlation proof link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-text-overlay-correlation.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 direct text-overlay correlation schema link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-capture-proof.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 direct timed frame-set capture proof link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-capture.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 direct timed frame-set capture schema link", failures)
        require("direct-level100-copied-profile-timed-private-frame-set-captured" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 direct timed frame-set capture status", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-text-overlay-progression-correlation-proof.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 timed frame-set text-overlay progression correlation proof link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-timed-frame-set-text-overlay-progression-correlation.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 timed frame-set text-overlay progression correlation schema link", failures)
        require("direct-level100-timed-frame-set-text-overlay-progression-correlated-to-static-level100-token-surface" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 timed frame-set text-overlay progression correlation status", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-boundary-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display boundary proof link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-boundary.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display boundary schema link", failures)
        require("direct-level100-runtime-message-display-boundary-defined-no-runtime-message-proof" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display boundary status", failures)
        require("MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Template Proof Plan" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display checklist-template follow-up slice", failures)
        require("runtimeMessageDisplayProven=false" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display proof guard", failures)
        require("messageDisplayBoundaryRows=3" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message boundary row count", failures)
        require("requiredFutureProofArtifactCount=5" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message future artifact count", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-template-proof-plan.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display checklist-template proof link", failures)
        require("missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-runtime-message-display-observation-checklist-template.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display checklist-template schema link", failures)
        require("direct-level100-runtime-message-display-observation-checklist-template-defined-no-runtime-message-proof" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display checklist-template status", failures)
        require("templateClassCount=5" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display checklist-template class count", failures)
        require("defaultStatus=not-run" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display checklist-template default status", failures)
        require("observationStatus=unobserved" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display checklist-template observation status", failures)
        require("MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Dry-Run Validation Proof Plan" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display checklist dry-run follow-up slice", failures)
        require("level100-message-checklist-dry-run-validation.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display checklist dry-run proof link", failures)
        require("level100-message-checklist-dry-run-validation.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display checklist dry-run schema link", failures)
        require("direct-level100-runtime-message-display-observation-checklist-dry-run-validation-pass-no-runtime-message-proof" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display checklist dry-run status", failures)
        require("dryRunValidationOnly=true" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display checklist dry-run flag", failures)
        require("dryRunValidationRows=9" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display checklist dry-run row count", failures)
        require("falseGuardCount=33" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display checklist dry-run false guard count", failures)
        require("zeroCounterCount=9" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display checklist dry-run zero counter count", failures)
        require("beLaunch=false" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display checklist dry-run launch guard", failures)
        require("launchArmed=false" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display checklist dry-run arm guard", failures)
        require("screenshotCapture=false" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display checklist dry-run screenshot guard", failures)
        require("beProcessesAfterDryRun=0" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 runtime message display checklist dry-run process cleanup count", failures)
        require("MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Private-Frame Review Arm Boundary Proof Plan" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 private-frame arm-boundary follow-up slice", failures)
        require("level100-message-private-frame-arm-boundary.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 private-frame arm-boundary proof link", failures)
        require("level100-message-private-frame-arm-boundary.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 private-frame arm-boundary schema link", failures)
        require("direct-level100-runtime-message-display-observation-checklist-private-frame-review-arm-boundary-defined-no-private-frame-review-performed" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 private-frame arm-boundary status", failures)
        require("MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Checklist Private-Frame Review Checklist Population Proof Plan" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 private-frame checklist population follow-up slice", failures)
        require("armBoundaryOnly=true" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 arm-boundary-only guard", failures)
        require("privateFrameReviewArmed=false" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 private-frame review arm guard", failures)
        require("privateFrameReviewPerformed=false" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 private-frame review performed guard", failures)
        require("futureReviewRequiresExplicitOperatorArm=true" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 future operator arm guard", failures)
        require("reviewablePrivateFrameRows=3" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 reviewable private-frame row count", failures)
        require("armableChecklistRows=9" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 armable checklist row count", failures)
        require("redactedFieldCount=14" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 redacted field count", failures)
        require("stopConditionCount=12" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 stop condition count", failures)
        require("falseGuardCount=40" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 arm-boundary false guard count", failures)
        require("zeroCounterCount=11" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 arm-boundary zero counter count", failures)
        require("MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Runtime Message Display Observation Public-Safe Result Summary Proof Plan" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 public-safe result summary slice", failures)
        require("level100-message-public-safe-result-summary.md" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 public-safe result summary proof link", failures)
        require("level100-message-public-safe-result-summary.v1.json" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 public-safe result summary schema link", failures)
        require("direct-level100-runtime-message-display-observation-public-safe-result-summary-complete-private-frame-review-deferred" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 public-safe result summary status", failures)
        require("publicSummaryOnly=true" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 public-safe summary-only flag", failures)
        require("summaryRows=1" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 public-safe summary row count", failures)
        require("sourceChecklistRowsMaterialized=9" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 public-safe source checklist count", failures)
        require("sourceNotRunRows=9" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 public-safe source not-run count", failures)
        require("sourceUnobservedRows=9" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 public-safe source unobserved count", failures)
        require("sourceObservedRows=0" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 public-safe source observed count", failures)
        require("privateFrameReviewDeferred=true" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 public-safe deferred flag", failures)
        require("summaryFalseGuardCount=45" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 public-safe summary false guard count", failures)
        require("summaryZeroCounterCount=12" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 public-safe summary zero counter count", failures)
        require("Static-To-Proof Rebuild Transition Next Safe Slice Selection Proof Plan" in text, f"{path.relative_to(ROOT)} missing next safe slice selection", failures)
        require("source-specimen-hash-mismatch" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 specimen mismatch boundary", failures)
        require("clean-backup-specimen-verified" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 clean backup verification boundary", failures)
        require("known-stable-patch-catalog-deltas-from-clean" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 current specimen classification", failures)
        require("clean-copied-profile-created" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 copied-profile materialization classification", failures)
        require("matches-canonical-clean-retail" in text, f"{path.relative_to(ROOT)} missing MissionScript Level100 copied executable hash class", failures)

    measured = read_text(MEASURE)
    require("after Wave1219 it is deprecated at `1210/1179`" in measured, "measurement register stale additive counter wording", failures)
    require("after Wave1218 it is deprecated at `1194/1179`" not in measured, "measurement register still has stale additive counter wording", failures)

    mapped = read_text(MAPPED)
    require("Historical measured anchors below are at-wave snapshots" in mapped, "mapped systems missing historical anchor guard", failures)
    require("Post-Wave1220 Transition Candidates" in mapped, "mapped systems missing transition candidates", failures)
    require("Completed World / Thing / Spawn / Object-Reference Bridge Proof Plan" in mapped, "mapped systems missing completed World/Thing/Spawn bridge slice", failures)
    require("Completed World / Thing / Spawn Spawner Handoff Static Proof" in mapped, "mapped systems missing completed World/Thing/Spawn spawner handoff proof", failures)
    require("static spawner handoff proof complete, not runtime proof" in mapped, "mapped systems missing World/Thing/Spawn spawner handoff status", failures)
    require("DAT_008553f4" in mapped, "mapped systems missing corrected World/Thing/Spawn spawner-list anchor", failures)
    require("static GetThingRef object-reference proof complete, not runtime proof" in mapped, "mapped systems missing World/Thing/Spawn GetThingRef status", failures)
    require("training-target-zone-getthingref-family" in mapped, "mapped systems missing World/Thing/Spawn GetThingRef selected family", failures)
    require("World / Thing / Spawn Static-To-Rebuild Contract Crosswalk Proof Plan" in mapped, "mapped systems missing World/Thing/Spawn crosswalk proof", failures)
    require("world-thing-spawn-static-to-rebuild-contract-crosswalk.md" in mapped, "mapped systems missing World/Thing/Spawn crosswalk proof link", failures)
    require("world-thing-spawn-static-to-rebuild-contract-crosswalk.v1.json" in mapped, "mapped systems missing World/Thing/Spawn crosswalk schema link", failures)
    require("world-thing-spawn-static-to-rebuild-contract-crosswalk-complete-static-contract-not-runtime-proof" in mapped, "mapped systems missing World/Thing/Spawn crosswalk status", failures)
    require("contractSectionCount=9" in mapped, "mapped systems missing World/Thing/Spawn crosswalk section count", failures)
    require("MissionScript Command-Effect Rebuild Interface Rollup Proof Plan" in mapped, "mapped systems missing MissionScript command-effect rollup active lane", failures)
    require("Completed MissionScript Cutscene Pan-Camera / Position Command-Effect Static Proof" in mapped, "mapped systems missing completed MissionScript cutscene camera proof", failures)
    require("static cutscene pan-camera/position command-effect schema proof complete, not runtime proof" in mapped, "mapped systems missing MissionScript cutscene camera status", failures)
    require("6 cutscene Fenrir GetThingRef rows" in mapped, "mapped systems missing MissionScript cutscene Fenrir corpus count", failures)
    require("MissionScript Vector/Range Command-Effect" in mapped, "mapped systems missing MissionScript vector/range proof", failures)
    require("static vector/range command-effect schema proof complete, not runtime proof" in mapped, "mapped systems missing MissionScript vector/range status", failures)
    require("no direct non-comment loose-MSL rows" in mapped, "mapped systems missing MissionScript vector/range corpus boundary", failures)
    require("MissionScript Thing Value / Engine Helper Command-Effect" in mapped, "mapped systems missing MissionScript thing-value proof", failures)
    require("static thing-value/engine-helper command-effect schema proof complete, not runtime proof" in mapped, "mapped systems missing MissionScript thing-value status", failures)
    require("CEngine__EnableThingByNameFlag" in mapped, "mapped systems missing MissionScript thing-value engine helper anchor", failures)
    require("CUnit__SetFactionForHierarchy" in mapped, "mapped systems missing MissionScript thing-value unit helper anchor", failures)
    require("15 / 1 / 2 / 4 / 5 / 0" in mapped, "mapped systems missing MissionScript thing-value corpus counts", failures)
    require("MissionScript HUD / Display Command-Effect" in mapped, "mapped systems missing MissionScript HUD/display proof", failures)
    require("static HUD/display command-effect schema proof complete, not runtime proof" in mapped, "mapped systems missing MissionScript HUD/display status", failures)
    require("HighlightHudPart" in mapped, "mapped systems missing MissionScript HUD/display highlight anchor", failures)
    require("ShutdownVariable" in mapped, "mapped systems missing MissionScript HUD/display variable anchor", failures)
    require("13 / 13 / 77 / 146 / 26" in mapped, "mapped systems missing MissionScript HUD/display corpus counts", failures)
    require("MissionScript Player-State / Score Command-Effect" in mapped, "mapped systems missing MissionScript player-state/score proof", failures)
    require("static player-state/score command-effect schema proof complete, not runtime proof" in mapped, "mapped systems missing MissionScript player-state/score status", failures)
    require("AddScore" in mapped, "mapped systems missing MissionScript player-state/score AddScore anchor", failures)
    require("ToggleCockpit" in mapped, "mapped systems missing MissionScript player-state/score ToggleCockpit anchor", failures)
    require("SetStealth" in mapped, "mapped systems missing MissionScript player-state/score SetStealth anchor", failures)
    require("0x00534410 IScript__SecondaryObjectiveComplete" in mapped, "mapped systems missing MissionScript player-state/score alias boundary", failures)
    require("15 / 0 / 10" in mapped, "mapped systems missing MissionScript player-state/score corpus counts", failures)
    require("Completed MissionScript Packed-vs-Loose Script Selection Proof Plan" in mapped, "mapped systems missing completed MissionScript packed-vs-loose proof", failures)
    require("missionscript-packed-vs-loose-script-selection-proof-plan.md" in mapped, "mapped systems missing MissionScript packed-vs-loose proof link", failures)
    require("missionscript-packed-vs-loose-script-selection.v1.json" in mapped, "mapped systems missing MissionScript packed-vs-loose schema link", failures)
    require("static proof plan complete, not runtime proof" in mapped, "mapped systems missing MissionScript packed-vs-loose status", failures)
    require("733" in mapped, "mapped systems missing MissionScript packed-vs-loose loose corpus count", failures)
    require("301" in mapped, "mapped systems missing MissionScript packed archive count", failures)
    require("CDXMemBuffer__InitFromFile" in mapped, "mapped systems missing MissionScript packed-vs-loose load anchor", failures)
    require("Completed MissionScript Level100 Tutorial Static Event/Command Walkthrough Proof Plan" in mapped, "mapped systems missing completed MissionScript Level100 walkthrough proof", failures)
    require("missionscript-level100-tutorial-static-walkthrough-proof-plan.md" in mapped, "mapped systems missing MissionScript Level100 walkthrough proof link", failures)
    require("missionscript-level100-tutorial-static-walkthrough.v1.json" in mapped, "mapped systems missing MissionScript Level100 walkthrough schema link", failures)
    require("static walkthrough proof plan complete, not runtime proof" in mapped, "mapped systems missing MissionScript Level100 walkthrough status", failures)
    require("Destroyed Friendly Building" in mapped, "mapped systems missing MissionScript Level100 mismatched posted-event token", failures)
    require("Friendly Building Destroyed" in mapped, "mapped systems missing MissionScript Level100 declared-event token", failures)
    require("MissionScript Level100 Tutorial Text/Speaker Resolution Static Proof Plan" in mapped, "mapped systems missing next MissionScript Level100 text/speaker slice", failures)
    require("Completed MissionScript VM/datatype/opcode schema result" in mapped, "mapped systems missing completed MissionScript VM/datatype/opcode schema result", failures)
    require("missionscript-vm-datatype-opcode-schema-proof.md" in mapped, "mapped systems missing MissionScript VM/datatype/opcode proof link", failures)
    require("missionscript-vm-datatype-opcode-schema.v1.json" in mapped, "mapped systems missing MissionScript VM/datatype/opcode schema link", failures)
    require("Completed MissionScript event/object-code lifecycle schema result" in mapped, "mapped systems missing completed MissionScript event/object-code lifecycle schema result", failures)
    require("missionscript-event-object-code-lifecycle-proof.md" in mapped, "mapped systems missing MissionScript event/object-code lifecycle proof link", failures)
    require("missionscript-event-object-code-lifecycle.v1.json" in mapped, "mapped systems missing MissionScript event/object-code lifecycle schema link", failures)
    require("Completed MissionScript / IScript static-contract extraction slice" in mapped, "mapped systems missing completed MissionScript/IScript static-contract slice", failures)
    require("Completed MissionScript / IScript proof-plan slice" in mapped, "mapped systems missing completed MissionScript/IScript proof-plan slice", failures)
    require("Active MissionScript / IScript proof-plan slice" not in mapped, "mapped systems still has stale active MissionScript/IScript proof-plan slice", failures)
    require("Active MissionScript / IScript static-contract extraction slice" not in mapped, "mapped systems still has stale active MissionScript/IScript static-contract slice", failures)
    require("MissionScript / IScript Core" in mapped, "mapped systems missing MissionScript/IScript core row", failures)
    require("Completed frontend/input/game-loop proof-plan slice" in mapped, "mapped systems missing completed Frontend/input slice", failures)
    require("Completed Engine / platform / math / memory support proof-plan slice" in mapped, "mapped systems missing completed Engine/platform slice", failures)
    require("Completed Audio / media / cutscene / camera proof-plan slice" in mapped, "mapped systems missing completed Audio/media slice", failures)
    require("Completed Save / options controller byte-preservation proof-plan slice" in mapped, "mapped systems missing completed Save/options slice", failures)
    require("Completed Save / Options Controller Byte-Preservation Copied-File Proof" in mapped, "mapped systems missing completed Save/options copied-file proof", failures)
    require("save-options-controller-byte-preservation-copied-file-proof.md" in mapped, "mapped systems missing Save/options copied-file proof link", failures)
    require("save-options-controller-byte-preservation-copied-file.v1.json" in mapped, "mapped systems missing Save/options copied-file schema link", failures)
    require("Completed Weapon / projectile spawn handoff proof-plan slice" in mapped, "mapped systems missing completed Weapon/projectile slice", failures)
    require("Completed Unit targeting / active-reader proof-plan slice" in mapped, "mapped systems missing completed Unit targeting slice", failures)
    require("Completed HUD/frontend overlay visual/runtime proof-plan slice" in mapped, "mapped systems missing completed HUD slice", failures)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.parse_args()

    failures: list[str] = []
    check_backlog(failures)
    check_front_doors(failures)
    if failures:
        print("Static-to-proof transition backlog probe: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Static-to-proof transition backlog probe: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
