# MissionScript Level100 Tutorial Copied-Profile Runtime Observation Artifact Manifest Proof Plan

Status: artifact-manifest planning complete, not runtime proof
Last updated: 2026-06-08
Scope: `missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest`
Public proof anchor: `missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest-proof-plan.md`

This slice converts the completed copied-profile runtime observation boundary into a concrete manifest contract for a later explicitly armed Level100 runtime observation proof. It does not create a copied profile, run BEA, patch an executable, capture screenshots or frames, drive native input, attach a debugger, start Godot work, or claim runtime MissionScript behavior.

Machine-checkable schema: `missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest.v1.json`.

Primary inputs:

- [MissionScript Level100 Tutorial Copied-Profile Runtime Observation Boundary Planning Proof Plan](missionscript-level100-tutorial-copied-profile-runtime-observation-boundary-proof-plan.md), backed by `missionscript-level100-tutorial-copied-profile-runtime-observation-boundary.v1.json`.
- [MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan](missionscript-level100-tutorial-runtime-harness-boundary-proof-plan.md), backed by `missionscript-level100-tutorial-runtime-harness-boundary.v1.json`.
- [MissionScript Level100 Tutorial Static Event/Command Walkthrough Proof Plan](missionscript-level100-tutorial-static-walkthrough-proof-plan.md), backed by `missionscript-level100-tutorial-static-walkthrough.v1.json`.
- [MissionScript Level100 Tutorial Text/Speaker Resolution Static Proof Plan](missionscript-level100-tutorial-text-speaker-resolution-proof-plan.md), backed by `missionscript-level100-tutorial-text-speaker-resolution.v1.json`.
- [MissionScript Packed-vs-Loose Script Selection Proof Plan](missionscript-packed-vs-loose-script-selection-proof-plan.md).

Selected static mission surface: `level100`, `LevelScript.msl`, `25` Level100 `.msl` files, `24` extra scripts, and `1469` parsed MSL lines.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup: `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

This planning slice performs no Ghidra mutation and does not require a new Ghidra backup.

## Manifest Contract

A later runtime observation proof must use app-owned, private manifests with these exact classes:

| Manifest class | Required fields | Public-safe output |
| --- | --- | --- |
| `copied_profile_manifest.v1` | `profileId`, `sourceSpecimenSha256`, `copiedRootClass`, `copiedExecutableClass`, `copiedResourceRootClass`, `copiedSaveOptionsClass`, `artifactRootClass`, `createdUtc`, `installedGameMutation`, and `privatePathsRedactedInPublic`. | Sanitized profile id, specimen hash equality, manifest class count, and no-mutation assertion only. |
| `specimen_byte_check.v1` | expected clean SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, copied executable hash class, original-byte verification status, patch-state field, and mismatch stop condition. | Hash equality or mismatch class, not local paths. |
| `launch_command_manifest.v1` | copied executable class, working directory class, argument vector, windowing prerequisite, environment class, and `launchArmed=false` until a later proof arms launch. | Argument class and armed/unarmed state only. |
| `source_selection_observation.v1` | static anchors `0x00539dc0`, `0x00539ca0`, `this+0x20`, `this+0x124`, `CDXMemBuffer__InitFromFile`, observed source class, observation status, and inconclusive reason. | Bounded source-selection class only after observation; until then `unobserved`. |
| `level100_observation_checklist.v1` | lanes for source selection, event ingress, event mismatch, message/text/speaker, HUD/display, object lookup, spawn handoff, and slot/objective rows. | Aggregate observed/inconclusive counts only. |
| `private_artifact_inventory.v1` | artifact class, private path class, redaction status, public inclusion policy, retention class, and leak-check status. | Artifact class counts and redaction status only. |
| `public_safe_result_summary.v1` | sanitized counts, hashes, claim boundary, stop conditions, unproven list, and public release allowlist status. | This is the only public-facing proof summary class. |

## Checklist Row Contract

The later checklist must preserve the static counts from the boundary plan:

- Source-selection anchors: `0x00539dc0`, `0x00539ca0`, `this+0x20`, `this+0x124`, and `CDXMemBuffer__InitFromFile`.
- Event ingress: `26` unique event names, `34` handlers, and `41` `PostEvent` callsites.
- Event mismatch row: `Destroyed Friendly Building` versus `Friendly Building Destroyed`.
- Message/text/speaker: `45` `PlayCharMessage*` rows, `43` message tokens, `6` `AddHelpMessage` tokens, speakers `P_TATIANA`, `P_KRAMER`, and `P_TECHNICIAN`, and `68/68` static tokens resolved with 0 missing references.
- HUD/display: `HUD_BATTLE_LINE_MAP`, `HUD_COMPASS`, `HUD_CURRENT_WEAPON`, `HUD_ENERGY_BAR`, `HUD_HEALTH_BAR`, `HUD_RADAR`, `7` `HighlightHudPart`, and `7` `UnHighlightHudPart`.
- Object/spawn: `18` raw `GetThingRef`, `15` unique object names, `20` `SpawnThing`, `Target Drone`, `Air Trainer`, `Target Tank`, and `Target Truck`.
- Slot/objective: `4` `GetSlot`, `4` `SetSlotSave`, `_100_OBJECTIVE_1` through `_100_OBJECTIVE_4`, and `LOSE_TUTORIAL_BROKE`.

Every checklist row must have one of these statuses: `not-run`, `observed`, `inconclusive`, `blocked`, or `out-of-scope`. The default status for this slice is `not-run`.

## Public / Private Boundary

Private manifests may include local copied-profile paths, copied executable paths, copied resource paths, copied save/options paths, screenshots, frames, logs, debugger transcripts, or raw media. Public outputs may include only sanitized counts, hash equality/mismatch classes, manifest schema names, redaction status, claim boundaries, and what remains unproven. Raw dialogue, private paths, save contents, copied executables, copied resources, screenshots, frames, debugger transcripts, and operator-only evidence stay out of public release scope.

## Stop Conditions

Stop and record a bounded blocked/deferred result if any later proof cannot satisfy these manifest gates before launch:

- copied profile manifest absent
- copied specimen hash mismatch
- byte-check report missing or inconclusive
- launch command manifest absent
- launch command needs a patch before a copied-executable patch proof exists
- `launchArmed` is true before a later runtime proof explicitly arms launch
- source-selection observation cannot be tied to the static anchors
- checklist row cannot map to the static Level100 boundary
- private path or raw artifact would leak into public docs
- Godot/rebuild work is required to make the runtime claim

## Claims

This slice proves only:

- The copied-profile runtime observation boundary has a concrete artifact manifest contract for a later explicitly armed proof.
- The required manifest classes, required fields, checklist row statuses, public/private redaction classes, and stop conditions are specified.
- Runtime MissionScript, source-selection, text/audio, HUD, object, patch, visual, Godot, rebuild, and no-noticeable-difference claims remain separate.

This slice does not prove:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime event outcomes.
- Live loose-MSL loading.
- Packed-vs-loose script selection.
- Runtime Level100 mission outcome.
- Runtime objective UI.
- Runtime message or audio output.
- Runtime HUD flashing.
- Runtime object identity.
- Runtime `SpawnThing` behavior.
- Runtime `GetThingRef` lookup behavior.
- BEA launch behavior.
- BEA patching behavior.
- Screenshot/capture proof.
- Native input behavior.
- Debugger observation behavior.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

## Exit Gate

This planning slice is complete only when:

- This document and `missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest.v1.json` have lore-book mirrors.
- `roadmap/static-to-proof-rebuild-transition-backlog.md`, `mapped-systems.md`, `_index.md`, and `RE-INDEX.md` point to this plan.
- The copied-profile runtime observation boundary points to this plan.
- `release/readiness/missionscript_level100_tutorial_copied_profile_runtime_observation_artifact_manifest_proof_plan_2026-06-08.md` records the same claim boundaries.
- `tools/missionscript_level100_tutorial_copied_profile_runtime_observation_artifact_manifest_probe.py --check` passes.

## Follow-Up Child Lane

Follow-up `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Manifest Template Generation Proof Plan` is complete and recorded in `missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-template-generation-proof-plan.md` with template bundle `missionscript-level100-tutorial-copied-profile-runtime-observation-manifest-templates.v1.json`. The next selected static-to-proof child lane is `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Manifest Dry-Run Validation Proof Plan`. That follow-up is still pre-launch validation: it may validate the empty manifest templates and redaction gates, but it must not create a real copied profile, launch BEA, patch an executable, capture screenshots or frames, drive native input, attach a debugger, start Godot work, or claim runtime behavior unless a later focused proof explicitly arms those actions.

The later `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Preparation Proof Plan` is also complete, and the current next child lane is `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Proof Plan`.
