# MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Executable Patch Proof

Status: complete copied-executable stable patch proof, not launch or runtime proof
Last updated: 2026-06-08
Scope: `missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch`
Public proof anchor: `missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch-proof.md`

This slice dry-ran, applied, and read back four stable patch-catalog rows on the copied `BEA.exe` inside the sanitized Level100 copied-profile artifact-root class. It used the clean copied profile from the materialization proof and preserved a clean backup beside the copied executable. It did not run BEA, capture screenshots or frames, drive native input, attach a debugger, start Godot work, or claim runtime MissionScript behavior.

Machine-checkable result: `missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch.v1.json`.

Previous completed slice: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Proof Plan`, backed by `missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-proof.md` and `missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization.v1.json`.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup: `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

This copied-executable patch proof performs no Ghidra mutation and does not require a new Ghidra backup.

## Patch Result

Private patch evidence exists under the ignored artifact-root class. Public docs expose only sanitized counts/classes, patch ids, byte offsets, hash classes, and command outcomes:

- Sanitized profile id: `level100-clean-materialized-20260608-214752`.
- Artifact-root class: `repo-local ignored private evidence root`.
- Target executable class: `copied-profile-BEA.exe`.
- Patch helper: `tools/apply_bea_catalog_patch.py`.
- Patch catalog: `patches/catalog/patches.v2.json`.
- Stable patch row count: `4`.
- `skipAutoToggleArmed=false`.
- Pre-patch copied executable SHA-256: `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
- Post-patch copied executable SHA-256: `e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918`.
- Backup executable SHA-256: `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
- Target executable bytes: `2506752`.
- Backup executable bytes: `2506752`.
- Dry-run message: `dry-run: no bytes were written`.
- Apply message: `patch apply complete`.
- Read-back message: `verified: no bytes were written`.

Stable rows:

| Patch id | Track | File offset | Dry-run state | Apply before | Apply after | Read-back state |
| --- | --- | --- | --- | --- | --- | --- |
| `resolution_gate` | `stable` | `0x129696` | `ready (original)` | `ready (original)` | `already patched` | `already patched` |
| `force_windowed` | `stable` | `0x12A644` | `ready (original)` | `ready (original)` | `already patched` | `already patched` |
| `version_overlay_use_patched_format_pointer` | `stable` | `0x6416F` | `ready (original)` | `ready (original)` | `already patched` | `already patched` |
| `version_overlay_patched_format_cave_string` | `stable` | `0x1AA444` | `ready (original)` | `ready (original)` | `already patched` | `already patched` |

The experimental `skip_auto_toggle` row remains unarmed and is not part of this copied-executable patch proof.

## Guard Outcomes

The copied-executable patch proof records:

- `status=COMPLETE`
- `patchStatus=stable-copied-executable-patched`
- `profileId=level100-clean-materialized-20260608-214752`
- `artifactRootClass=repo-local-ignored-private-evidence-root`
- `targetExecutableClass=copied-profile-BEA.exe`
- `stablePatchRows=4`
- `skipAutoToggleArmed=false`
- `prePatchSha256=74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
- `targetHash=e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918`
- `backupHash=74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
- `targetBytes=2506752`
- `backupBytes=2506752`
- `dryRunMessage=dry-run: no bytes were written`
- `applyMessage=patch apply complete`
- `readbackMessage=verified: no bytes were written`
- `installedGameMutation=false`
- `originalExecutableMutation=false`
- `beLaunch=false`
- `launchArmed=false`
- `screenshotCapture=false`
- `nativeInput=false`
- `debuggerAttachment=false`
- `godotWork=false`
- `runtimeEvidenceRows=0`
- `privatePathLeakCount=0`
- `rawArtifactLeakCount=0`
- `publicLeakCheck=PASS`

No local path is public evidence. Public docs may report sanitized profile id, stable patch ids, offsets, byte-state outcomes, hash classes, redaction status, stop conditions, and claim boundary only.

## Level100 Static Anchors Preserved

The patched copied executable remains tied to the same Level100 observation surface:

- Source-selection anchors: `0x00539dc0`, `0x00539ca0`, `this+0x20`, `this+0x124`, and `CDXMemBuffer__InitFromFile`.
- Event ingress: `26` unique event names, `34` handlers, and `41` `PostEvent` callsites.
- Event mismatch row: `Destroyed Friendly Building` versus `Friendly Building Destroyed`.
- Message/text/speaker: `45` `PlayCharMessage*` rows, `43` message tokens, `6` `AddHelpMessage` tokens, speakers `P_TATIANA`, `P_KRAMER`, and `P_TECHNICIAN`, and `68/68` static tokens resolved with `0` missing references.
- HUD/display: `HUD_BATTLE_LINE_MAP`, `HUD_RADAR`, `7` `HighlightHudPart`, and `7` `UnHighlightHudPart`.
- Object/spawn: `18` raw `GetThingRef`, `15` unique object names, `20` `SpawnThing`, `Target Drone`, `Air Trainer`, `Target Tank`, and `Target Truck`.
- Slot/objective: `4` `GetSlot`, `4` `SetSlotSave`, `_100_OBJECTIVE_1` through `_100_OBJECTIVE_4`, and `LOSE_TUTORIAL_BROKE`.

## Claims

This slice proves only:

- A copied-profile `BEA.exe` was stable-patch dry-run checked, patched, and read back in an app-owned ignored artifact-root class.
- The dry-run saw all four stable rows in `ready (original)` state.
- The apply wrote the copied executable only and left all four stable rows in `already patched` state.
- The read-back dry-run saw all four stable rows in `already patched` state with no bytes written.
- A clean backup exists beside the copied executable and matches the canonical clean Steam retail/Ghidra specimen hash.
- The installed game root and original executable remained read-only.

This slice does not prove:

- BEA launch behavior.
- Runtime behavior of any patch row.
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
- Screenshot/capture proof.
- Native input behavior.
- Debugger observation behavior.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.

## Follow-Up Child Lane

The next selected static-to-proof child lane is `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Command Proof Plan`. That follow-up must prove launch command construction, copied-profile path selection, launch arming, and stop conditions before any live BEA process is started.
