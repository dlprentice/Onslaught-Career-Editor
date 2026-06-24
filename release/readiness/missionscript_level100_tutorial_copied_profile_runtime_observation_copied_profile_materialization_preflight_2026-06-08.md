# MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Preflight Readiness Note

Status: deferred because source specimen hash does not match the canonical clean retail specimen
Date: 2026-06-08
Scope: `missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight`

This readiness note records a public-safe stop before copied-profile materialization. The source specimen preflight observed SHA-256 `e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918`, while the canonical expected clean retail SHA-256 remains `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`. The observed hash is not recognized in tracked repo specimen authority.

Public proof files: `missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight-proof.md` and `missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight.v1.json`.

Previous completed slice: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Preparation Proof Plan`, backed by `missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation-proof-plan.md` and `missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-preparation.v1.json`.

Result:

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

Static context remains unchanged: `6411/6411 = 100.00%`, `0 / 0 / 0`, expanded post-100 static surface `1560/1560 = 100.00%`, active current-risk focused accounting `1179/1179 = 100.00%`, remaining active focused work `0`, latest verified Ghidra backup `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Level100 anchors preserved for later retry: `level100`, `LevelScript.msl`, `25` files, `24` extras, `1469` lines, `26` event names, `34` handlers, `41` `PostEvent` callsites, `Destroyed Friendly Building` versus `Friendly Building Destroyed`, `45` `PlayCharMessage*`, `43` message tokens, `6` `AddHelpMessage`, speakers `P_TATIANA`, `P_KRAMER`, and `P_TECHNICIAN`, `68/68` text tokens with `0` missing references, `HUD_BATTLE_LINE_MAP`, `HUD_RADAR`, `18` raw `GetThingRef`, `15` unique object names, `20` `SpawnThing`, `Target Drone`, `Air Trainer`, `Target Tank`, `Target Truck`, `4` `GetSlot`, `4` `SetSlotSave`, `0x00539dc0`, `0x00539ca0`, `this+0x20`, `this+0x124`, and `CDXMemBuffer__InitFromFile`.

This proves only that materialization was preflighted and stopped safely on an unrecognized specimen hash. It does not prove the observed specimen is bad, patched, unsafe, or unusable. It does not prove copied-profile creation, BEA launch, patching, runtime MissionScript behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.

Next selected child lane: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Clean Source Specimen Resolution Proof Plan`.
