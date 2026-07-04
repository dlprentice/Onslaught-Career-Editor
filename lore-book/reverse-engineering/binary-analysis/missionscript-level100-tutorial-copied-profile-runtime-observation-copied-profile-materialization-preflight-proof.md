# MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Preflight

Status: deferred because source specimen hash does not match the canonical clean retail specimen
Last updated: 2026-06-08
Scope: `missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight`
Public proof anchor: `missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight-proof.md`

This slice attempted the safe preflight for the selected Level100 copied-profile materialization lane. It did not create a copied profile, copy an executable, run BEA, patch an executable, capture screenshots or frames, drive native input, attach a debugger, start Godot work, or claim runtime MissionScript behavior.

Machine-checkable preflight result: `missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight.v1.json`.

Previous completed slice: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Preparation Proof Plan`, backed by `missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation-proof-plan.md` and `missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation.v1.json`.

Selected static mission surface remains `level100`, `LevelScript.msl`, `25` Level100 `.msl` files, `24` extra scripts, and `1469` parsed MSL lines.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup: `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

This materialization preflight performs no Ghidra mutation and does not require a new Ghidra backup.

## Preflight Result

The source specimen byte-check preflight found a hash mismatch:

- Expected clean retail SHA-256: `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
- Observed source SHA-256: `e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918`
- Observed source size: `2506752`
- Tracked authority search: the observed `e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918` hash is not recognized in tracked repo specimen authority.
- Hash class: `mismatch-unrecognized`

Because the active patch/static contract is tied to the `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` specimen, this slice stops before copying. That preserves the proof boundary: a mismatched source executable must be resolved through a separate specimen-authority slice before a runtime observation profile is materialized.

## Guard Outcomes

The materialization preflight records:

- `status=DEFERRED`
- `deferReason=source-specimen-hash-mismatch`
- `hashClass=mismatch-unrecognized`
- `observedSourceSize=2506752`
- `materializationAttempted=false`
- `sourceSpecimenMatchesExpected=false`
- `sourceSpecimenRecognized=false`
- `copiedProfileCreated=false`
- `copiedExecutableCreated=false`
- `copiedSpecimenHashChecked=false`
- `installedGameMutation=false`
- `originalExecutableMutation=false`
- `beLaunch=false`
- `launchArmed=false`
- `executablePatch=false`
- `screenshotCapture=false`
- `nativeInput=false`
- `debuggerAttachment=false`
- `godotWork=false`
- `runtimeEvidenceRows=0`
- `privatePathLeakCount=0`
- `rawArtifactLeakCount=0`
- `publicLeakCheck=PASS`

No local path is public evidence. Public docs may report hash equality or mismatch class, file size, stop condition, and claim boundary only.

## Level100 Static Anchors Preserved

The later copied-profile materialization or runtime-observation lane must preserve the same Level100 static anchors:

- Source-selection anchors: `0x00539dc0`, `0x00539ca0`, `this+0x20`, `this+0x124`, and `CDXMemBuffer__InitFromFile`.
- Event ingress: `26` unique event names, `34` handlers, and `41` `PostEvent` callsites.
- Event mismatch row: `Destroyed Friendly Building` versus `Friendly Building Destroyed`.
- Message/text/speaker: `45` `PlayCharMessage*` rows, `43` message tokens, `6` `AddHelpMessage` tokens, speakers `P_TATIANA`, `P_KRAMER`, and `P_TECHNICIAN`, and `68/68` static tokens resolved with `0` missing references.
- HUD/display: `HUD_BATTLE_LINE_MAP`, `HUD_RADAR`, `7` `HighlightHudPart`, and `7` `UnHighlightHudPart`.
- Object/spawn: `18` raw `GetThingRef`, `15` unique object names, `20` `SpawnThing`, `Target Drone`, `Air Trainer`, `Target Tank`, and `Target Truck`.
- Slot/objective: `4` `GetSlot`, `4` `SetSlotSave`, `_100_OBJECTIVE_1` through `_100_OBJECTIVE_4`, and `LOSE_TUTORIAL_BROKE`.

## Claims

This slice proves only:

- The materialization lane was preflighted against the current specimen authority.
- The observed source executable hash does not match the canonical clean retail hash.
- The observed hash is not recognized in tracked repo specimen authority.
- No copied profile or copied executable was created.
- Launch, patching, screenshots, native input, debugger, Godot, runtime proof, rebuild parity, and no-noticeable-difference parity remain disabled.

This slice does not prove:

- The observed `e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918` specimen is bad, patched, unsafe, or unusable.
- A copied profile exists.
- A copied executable exists.
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

## Follow-Up Child Lane

The next selected static-to-proof child lane is `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Clean Source Specimen Resolution Proof Plan`. That follow-up must either locate/restore a source specimen matching the canonical hash or create a separate reviewed specimen-authority update before copied-profile materialization is retried.
