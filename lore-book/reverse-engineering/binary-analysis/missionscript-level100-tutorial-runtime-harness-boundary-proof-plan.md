# MissionScript Level100 Tutorial Runtime Harness Boundary Proof Plan

Status: runtime-harness boundary proof plan complete, not runtime proof
Last updated: 2026-06-08
Scope: `missionscript-level100-tutorial-runtime-harness-boundary`
Public proof anchor: `missionscript-level100-tutorial-runtime-harness-boundary-proof-plan.md`

This slice converts the completed Level100 static event/command walkthrough and text/speaker resolution into a bounded runtime-harness contract for a later copied-profile proof. It does not run BEA, mutate Ghidra, mutate the installed game, patch an executable, capture screenshots, drive native input, attach a debugger, load a live mission, start Godot work, or claim runtime MissionScript behavior.

Machine-checkable schema: `missionscript-level100-tutorial-runtime-harness-boundary.v1.json`.

Primary static inputs:

- [MissionScript Level100 Tutorial Static Event/Command Walkthrough Proof Plan](missionscript-level100-tutorial-static-walkthrough-proof-plan.md), backed by `missionscript-level100-tutorial-static-walkthrough.v1.json`.
- [MissionScript Level100 Tutorial Text/Speaker Resolution Static Proof Plan](missionscript-level100-tutorial-text-speaker-resolution-proof-plan.md), backed by `missionscript-level100-tutorial-text-speaker-resolution.v1.json`.
- [MissionScript Packed-vs-Loose Script Selection Proof Plan](missionscript-packed-vs-loose-script-selection-proof-plan.md), which remains source-selection planning only.
- [MissionScript / IScript Static Contract](missionscript-iscript-static-contract.md).
- [MissionScript Event / Object-Code Lifecycle Proof](missionscript-event-object-code-lifecycle-proof.md).

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup: `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

This boundary plan does not create a new static RE percentage and does not require a new Ghidra backup because it performs no Ghidra mutation.

## Static Inputs Selected For Future Harness

The later harness should be scoped to the already mapped Level100 tutorial surface:

| Surface | Static input |
| --- | --- |
| Loose corpus | `LevelScript.msl`, `25` Level100 `.msl` files, `24` extra scripts, `1469` parsed MSL lines. |
| Event surface | `26` unique event names, `34` handler declarations, and `41` `PostEvent` callsites. |
| Event mismatch | Preserve `Destroyed Friendly Building` versus `Friendly Building Destroyed`; do not normalize it away. |
| Message/audio surface | `45` `PlayCharMessage*` rows, `43` unique message tokens, `6` `AddHelpMessage` tokens, and speakers `P_TATIANA`, `P_KRAMER`, and `P_TECHNICIAN`. |
| Text resolution | `68/68` relevant static tokens resolved and `0 missing` references. |
| Objective/loss surface | `_100_OBJECTIVE_1` through `_100_OBJECTIVE_4` and `LOSE_TUTORIAL_BROKE`. |
| HUD/display surface | `HUD_BATTLE_LINE_MAP`, `HUD_COMPASS`, `HUD_CURRENT_WEAPON`, `HUD_ENERGY_BAR`, `HUD_HEALTH_BAR`, and `HUD_RADAR`. |
| Object/spawn surface | `18` raw `GetThingRef`, `15` unique object names, `20` `SpawnThing` rows, and spawn families `Target Drone`, `Air Trainer`, `Target Tank`, and `Target Truck`. |
| Source-selection boundary | `0x00539dc0 CMissionScriptObjectCode__StartLoadAsync`, `0x00539ca0 CMissionScriptObjectCode__LoadAsync`, `this+0x20`, `this+0x124`, and `CDXMemBuffer__InitFromFile`. |

## MissionScript Anchor Boundary

The later harness may use these anchors as observation planning context only:

- `0x005383c0 IScript__ScheduleEvent`
- `0x00538b70 CScriptEventNB__PostEvent`
- `0x0052fda0 CEventFunction__Execute`
- `0x00539a60 CScriptObjectCode__CallEventDirect`
- `0x00539b00 CScriptObjectCode__Run`
- `0x0064ce50` descriptor table with `144` slots
- `0x0052ea40 CAsmInstruction__ExecuteCall`
- `0x0052ec60 CDataType__CreateFromType`
- `0x00539dc0 CMissionScriptObjectCode__StartLoadAsync`
- `0x00539ca0 CMissionScriptObjectCode__LoadAsync`
- `this+0x20`
- `this+0x124`
- `CDXMemBuffer__InitFromFile`

These are static retail anchors only. They do not prove runtime event outcomes, command effects, live loose-MSL loading, packed-vs-loose selection, or exact object-code layout.

## Command-Family Boundary Counts

The later harness must keep each command family independently bounded:

- `4` `GetSlot` rows.
- `4` `SetSlotSave` rows.
- `45` `PlayCharMessage*` rows and `43` unique message tokens.
- `6` `AddHelpMessage` tokens.
- `7` `HighlightHudPart` rows.
- `7` `UnHighlightHudPart` rows.
- `18` raw `GetThingRef` rows and `15` unique object names.
- `20` `SpawnThing` rows.

## Packed/Loose Planning Counts

The source-selection boundary inherits only static planning counts from the packed-vs-loose slice:

- `733` loose MissionScript files in the copied corpus index.
- `32` Goodie-state calls in the static loose corpus.
- Target script indices `72-74` have no Goodie-state target hits in that scan.
- `95` level rows in the event/object-code context.
- `795` loose event-name counts.
- `301` top-level AYA archives in the narrow packed-resource literal scan.
- `0` inflate errors.
- `0` literal Goodie API/token hits.

This does not prove live source selection. It only sets the future observation checklist.

## Allowed Future Inputs

A later runtime observation proof may use only app-owned or copied inputs:

- copied profile root
- copied BEA.exe specimen only if a later proof explicitly requires launch
- copied real save/options baselines when needed
- app-owned logs, frame captures, debugger logs, and manifests
- sanitized public summaries derived from private proof artifacts

This slice itself does not create or run any of those runtime artifacts.

## Forbidden During This Slice

This boundary plan specifically forbids the following work in this slice:

- launch BEA
- patch any executable
- capture screenshots or frames
- drive native input
- attach a debugger
- load a live mission
- mutate the installed Steam game
- start Godot work
- claim runtime behavior

## Later Runtime Observation Plan

The first later executable proof should be narrow and reversible:

1. Select one copied-profile Level100 launch target.
2. Verify specimen bytes before any future patch candidate.
3. Record source-selection expectations separately from live proof.
4. Observe only a narrow tutorial path or abort as inconclusive.
5. Capture private artifacts under app-owned or ignored roots.
6. Publish only sanitized counts and bounded conclusions.

## Required Future Artifacts

A later proof should not claim runtime behavior unless it produces these private or public-safe artifacts:

- copied profile manifest
- specimen hash and byte-check report
- launch command manifest
- source-selection observation log
- bounded event/message/HUD/object observation checklist
- private artifact inventory
- public-safe result summary

## Stop Conditions

Stop and record a bounded blocked/deferred result if any of these occur:

- installed game or original executable would be touched
- runtime source selection is ambiguous
- script behavior differs from static expectation
- event mismatch blocks interpretation
- text/audio/HUD output cannot be observed without broadening scope
- private raw dialogue, save data, screenshots, or paths would leak
- patching or native input is needed before the later proof explicitly arms it
- Godot/rebuild work is required to make the claim

## Claims

This slice proves only:

- The Level100 static walkthrough and text/speaker slices are strong enough to define a copied-profile runtime-harness boundary.
- The boundary plan selects allowed future inputs, required artifacts, and stop conditions without executing runtime proof.
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
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

## Exit Gate

This boundary slice is complete only when:

- This document and `missionscript-level100-tutorial-runtime-harness-boundary.v1.json` have lore-book mirrors.
- `roadmap/static-to-proof-rebuild-transition-backlog.md`, `mapped-systems.md`, `_index.md`, and `RE-INDEX.md` point to this plan.
- Level100 walkthrough, text/speaker, packed-vs-loose, MissionScript contract, MissionScript event lifecycle, and mission corpus docs point to this plan.
- `release/readiness/missionscript_level100_tutorial_runtime_harness_boundary_proof_plan_2026-06-08.md` records the same claim boundaries.
- `tools/missionscript_level100_tutorial_runtime_harness_boundary_proof_plan_probe.py --check` passes.

## Follow-Up Child Lane

The `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Boundary Planning Proof Plan` follow-up is now complete at `missionscript-level100-tutorial-copied-profile-runtime-observation-boundary-proof-plan.md`, backed by `missionscript-level100-tutorial-copied-profile-runtime-observation-boundary.v1.json`. The next selected static-to-proof child lane is `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Artifact Manifest Proof Plan`. That follow-up is still pre-launch planning only: it must not create a copied profile, launch BEA, patch an executable, capture screenshots or frames, drive native input, attach a debugger, start Godot work, or claim runtime behavior unless a later focused proof explicitly arms those actions with copied/app-owned inputs, proof artifacts, stop conditions, private/public separation, and no-mutation rules.
