# MissionScript Level100 Tutorial Copied-Profile Runtime Observation Boundary Planning Proof Plan

Status: copied-profile runtime observation boundary planning complete, not runtime proof
Last updated: 2026-06-08
Scope: `missionscript-level100-tutorial-copied-profile-runtime-observation-boundary`
Public proof anchor: `missionscript-level100-tutorial-copied-profile-runtime-observation-boundary-proof-plan.md`

This slice converts the completed Level100 runtime-harness boundary into an observation checklist for a later explicitly armed copied-profile proof. It does not create a copied profile, run BEA, patch an executable, capture screenshots or frames, drive native input, attach a debugger, start Godot work, or claim runtime MissionScript behavior.

Machine-checkable schema: `missionscript-level100-tutorial-copied-profile-runtime-observation-boundary.v1.json`.

Primary inputs:

- [MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan](missionscript-level100-tutorial-runtime-harness-boundary-proof-plan.md), backed by `missionscript-level100-tutorial-runtime-harness-boundary.v1.json`.
- [MissionScript Level100 Tutorial Static Event/Command Walkthrough Proof Plan](missionscript-level100-tutorial-static-walkthrough-proof-plan.md), backed by `missionscript-level100-tutorial-static-walkthrough.v1.json`.
- [MissionScript Level100 Tutorial Text/Speaker Resolution Static Proof Plan](missionscript-level100-tutorial-text-speaker-resolution-proof-plan.md), backed by `missionscript-level100-tutorial-text-speaker-resolution.v1.json`.
- [MissionScript Packed-vs-Loose Script Selection Proof Plan](missionscript-packed-vs-loose-script-selection-proof-plan.md), which remains source-selection planning only.
- [MissionScript / IScript Static Contract](missionscript-iscript-static-contract.md).
- [MissionScript Event / Object-Code Lifecycle Proof](missionscript-event-object-code-lifecycle-proof.md).

Selected static mission surface: `level100`, `LevelScript.msl`, `25` Level100 `.msl` files, `24` extra scripts, and `1469` parsed MSL lines.

Required future artifacts use these exact manifest classes: copied profile manifest, specimen hash and byte-check report, launch command manifest, source-selection observation log, bounded event/message/HUD/object observation checklist, private artifact inventory, and public-safe result summary.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup: `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

This planning slice performs no Ghidra mutation and does not require a new Ghidra backup.

## Copied-Profile Envelope

A later runtime observation proof must use a copied/app-owned envelope with these private artifacts:

| Artifact | Required contents | Public treatment |
| --- | --- | --- |
| Copied profile manifest | Profile id, source install hash summary, copied root, copied resource root, copied executable path, copied save/options paths, artifact root, creation timestamp, and no-mutation assertion. | Public docs may report only sanitized counts and hashes, not local private paths. |
| Specimen hash and byte-check report | Known clean specimen hash `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, copied executable hash, original-byte check, and patch-state field. | Public docs may report hash equality or mismatch without private path disclosure. |
| Launch command manifest | Intended copied executable, working directory, arguments, windowing/patch prerequisites, environment, and stop-on-mismatch rules. | Public docs may report the argument class and whether launch remained unarmed. |
| Source-selection observation log | Expected source-selection anchors `0x00539dc0`, `0x00539ca0`, `this+0x20`, `this+0x124`, and `CDXMemBuffer__InitFromFile`; observed script source class; inconclusive marker. | Public docs may report bounded source-selection result only. |
| Observation checklist | Event, message, HUD, object, spawn, slot/objective, and abort rows with observed/not-observed/inconclusive states. | Public docs may report aggregate counts and bounded conclusions only. |
| Private artifact inventory | Logs, captures, debugger transcripts, copied files, generated manifests, and redaction status. | Public docs may report artifact classes and counts only. |
| Public-safe result summary | Sanitized counts, hashes, claim boundary, stop conditions, and what remains unproven. | Public release candidate may include this summary if allowlist checks pass. |

## Observation Checklist

The later runtime proof may observe only the surfaces below unless a later proof plan explicitly broadens scope.

| Checklist lane | Static expectation | Required observation artifact | Pass / inconclusive boundary |
| --- | --- | --- | --- |
| Source selection | Object-code load path is bounded by `0x00539dc0`, `0x00539ca0`, `this+0x20`, `this+0x124`, and `CDXMemBuffer__InitFromFile`. | Source-selection observation log. | Pass only if the copied-profile run identifies the script source class without touching installed files; otherwise inconclusive. |
| Event ingress | Level100 static surface has `26` unique event names, `34` handlers, and `41` `PostEvent` callsites. | Event observation checklist row set. | Pass only for observed event names in the selected path; do not claim all events fire. |
| Event mismatch | Preserve `Destroyed Friendly Building` versus `Friendly Building Destroyed`. | Explicit mismatch row in the observation checklist. | If the mismatch affects interpretation, stop as bounded/inconclusive. |
| Message/text/speaker | `45` `PlayCharMessage*` rows, `43` message tokens, `6` `AddHelpMessage` tokens, speakers `P_TATIANA`, `P_KRAMER`, and `P_TECHNICIAN`, and `68/68` static text tokens resolved with `0 missing`. | Message/text/speaker observation rows. | Pass only for tokens/speakers observed in the selected path; do not claim full audio or localization behavior. |
| HUD/display | Static HUD parts include `HUD_BATTLE_LINE_MAP`, `HUD_COMPASS`, `HUD_CURRENT_WEAPON`, `HUD_ENERGY_BAR`, `HUD_HEALTH_BAR`, and `HUD_RADAR`; command rows include `7` `HighlightHudPart` and `7` `UnHighlightHudPart`. | HUD observation rows, not raw public screenshots. | Pass only for the selected visible or logged HUD surface; visual parity remains separate. |
| Object lookup | Static corpus has `18` raw `GetThingRef` rows and `15` unique object names. | Object-reference observation rows. | Pass only for selected object names observed; do not claim exact object identity layout. |
| Spawn handoff | Static corpus has `20` `SpawnThing` rows over `Target Drone`, `Air Trainer`, `Target Tank`, and `Target Truck`. | Spawn observation rows. | Pass only for selected spawns observed; runtime spawn behavior and physics remain separate. |
| Slot/objective | Static walkthrough has `4` `GetSlot`, `4` `SetSlotSave`, `_100_OBJECTIVE_1` through `_100_OBJECTIVE_4`, and `LOSE_TUTORIAL_BROKE`. | Slot/objective observation rows. | Pass only for selected slot/objective rows; save/defaultoptions behavior remains separate. |

## Launch Arm Boundary

This slice does not authorize launch. A later launch-capable proof must first record:

1. copied profile manifest
2. specimen hash and byte-check report
3. launch command manifest
4. explicit operator-safe copied-profile target
5. no installed-game mutation assertion
6. private artifact root
7. stop conditions accepted before running

If a windowing patch is required, that is a separate byte-verified copied-executable patch proof, not part of this planning slice.

## Public / Private Boundary

Private artifacts may include local paths, screenshots, frames, copied saves, copied executables, logs, debugger transcripts, or raw media. Public artifacts may include only sanitized counts, hashes, claim boundaries, and redacted summaries. Raw dialogue, save data, private paths, screenshots, frames, copied executables, copied resources, and operator-only evidence stay out of public release scope.

## Stop Conditions

Stop and record a bounded blocked/deferred result if any of these occur:

- installed game or original executable would be touched
- copied specimen hash does not match the expected clean hash
- launch command requires a patch before a patch proof exists
- runtime source selection is ambiguous
- selected event/message/HUD/object observation cannot be tied to the static checklist
- the `Destroyed Friendly Building` / `Friendly Building Destroyed` mismatch blocks interpretation
- native input, debugger attachment, screenshots, frames, or patching are needed before a later proof explicitly arms them
- private data would leak into public docs
- Godot/rebuild work is required to make the claim

## Claims

This slice proves only:

- The Level100 runtime-harness boundary is specific enough to define copied-profile runtime observation manifests and checklists.
- The later runtime observation proof has a bounded artifact contract, observation checklist, launch arm boundary, public/private separation, and stop conditions.
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

- This document and `missionscript-level100-tutorial-copied-profile-runtime-observation-boundary.v1.json` have lore-book mirrors.
- `roadmap/static-to-proof-rebuild-transition-backlog.md`, `mapped-systems.md`, `_index.md`, and `RE-INDEX.md` point to this plan.
- The prior Level100 runtime-harness boundary points to this plan.
- `release/readiness/missionscript_level100_tutorial_copied_profile_runtime_observation_boundary_proof_plan_2026-06-08.md` records the same claim boundaries.
- `tools/missionscript_level100_tutorial_copied_profile_runtime_observation_boundary_probe.py --check` passes.

## Follow-Up Child Lane

The `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Artifact Manifest Proof Plan` follow-up is now complete at `missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest-proof-plan.md`, backed by `missionscript-level100-tutorial-copied-profile-runtime-observation-artifact-manifest.v1.json`. The next selected static-to-proof child lane is `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Manifest Template Generation Proof Plan`. That follow-up is still pre-launch preparation: it may create app-owned manifest template files only if explicitly bounded, but it must not create a real copied profile, launch BEA, patch an executable, capture screenshots or frames, drive native input, attach a debugger, start Godot work, or claim runtime behavior unless a later focused proof explicitly arms those actions.
