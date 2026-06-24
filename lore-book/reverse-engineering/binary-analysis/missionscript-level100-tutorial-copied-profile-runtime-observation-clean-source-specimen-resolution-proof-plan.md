# MissionScript Level100 Tutorial Copied-Profile Runtime Observation Clean Source Specimen Resolution Proof Plan

Status: complete source-specimen authority resolution before copied-profile materialization
Last updated: 2026-06-08
Scope: `missionscript-level100-tutorial-copied-profile-runtime-observation-clean-source-specimen-resolution`
Public proof anchor: `missionscript-level100-tutorial-copied-profile-runtime-observation-clean-source-specimen-resolution-proof-plan.md`

This slice resolves the copied-profile materialization preflight stop condition by verifying a read-only clean backup specimen that matches the canonical Steam retail Ghidra/static authority. It also classifies the current installed convenience executable as the clean specimen plus known patch-catalog deltas. It does not create a copied profile, copy an executable, run BEA, patch an executable, capture screenshots or frames, drive native input, attach a debugger, start Godot work, or claim runtime MissionScript behavior.

Machine-checkable result: `missionscript-level100-tutorial-copied-profile-runtime-observation-clean-source-specimen-resolution.v1.json`.

Previous stopped slice: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Preflight`, backed by `missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight-proof.md` and `missionscript-level100-tutorial-copied-profile-runtime-observation-copied-profile-materialization-preflight.v1.json`.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup: `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

This specimen-resolution proof performs no Ghidra mutation and does not require a new Ghidra backup.

## Specimen Resolution

Read-only hash and byte checks produced the following source-authority result:

- Expected clean retail SHA-256: `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
- Clean backup specimen SHA-256: `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
- Clean backup specimen size: `2506752`.
- Clean backup authority class: `canonical-clean-retail-match`.
- Current installed convenience specimen SHA-256: `e78818292a1dbe31dc6987c71665857de3a8cf3e7619745689d74c7da829c918`.
- Current installed convenience specimen size: `2506752`.
- Current specimen class: `known-stable-patch-catalog-deltas-from-clean`.
- Full clean-versus-current byte compare: `sameLength=true`, `byteDiffCount=28`, `unknownDiffCount=0`.

Known patch-catalog deltas observed in the current convenience executable:

| Patch id | File offset | Clean bytes | Current bytes | State |
| --- | --- | --- | --- | --- |
| `resolution_gate` | `0x129696` | `CC` | `00` | `patched` |
| `force_windowed` | `0x12A644` | `A1 F0 2D 66 00` | `B8 01 00 00 00` | `patched` |
| `version_overlay_use_patched_format_pointer` | `0x06416F` | `54 94 62 00` | `44 A4 5A 00` | `patched` |
| `version_overlay_patched_format_cave_string` | `0x1AA444` | `CC CC CC CC CC CC CC CC CC CC CC CC CC CC CC CC CC CC CC CC` | `56 25 31 64 2E 25 30 32 64 20 2D 20 50 41 54 43 48 45 44 00` | `patched` |
| `skip_auto_toggle` | `0x12BB97` | `75 20` | `75 20` | `original` |

The prior materialization preflight remained correct to stop before copying from the mismatched current convenience executable. This resolution slice adds the missing authority: the clean backup specimen matches the canonical hash and is suitable as read-only source material for the next copied-profile materialization attempt.

## Guard Outcomes

The specimen-resolution proof records:

- `status=COMPLETE`
- `resolutionStatus=clean-backup-specimen-verified`
- `cleanBackupMatchesExpected=true`
- `cleanBackupAuthorityClass=canonical-clean-retail-match`
- `currentSpecimenClass=known-stable-patch-catalog-deltas-from-clean`
- `sameLength=true`
- `byteDiffCount=28`
- `unknownDiffCount=0`
- `materializationAttempted=false`
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

No local path is public evidence. Public docs may report hash equality, patch classifications, file size, stop-condition resolution, and claim boundary only.

## Claims

This slice proves only:

- A read-only clean backup specimen matches the canonical Steam retail Ghidra/static specimen hash.
- The current convenience executable differs from the clean backup by known patch-catalog deltas only.
- The previously observed current-executable mismatch is explained by known stable patch-catalog bytes, not an unknown specimen.
- No copied profile or copied executable was created.
- Launch, patching, screenshots, native input, debugger, Godot, runtime proof, rebuild parity, and no-noticeable-difference parity remain disabled.

This slice does not prove:

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

The next selected static-to-proof child lane is `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Proof Plan`. That follow-up must copy from the verified clean backup specimen into an app-owned artifact root, verify the copied executable hash before patching, apply any needed windowed/catalog patch only to the copied executable, and keep installed/original source material read-only.
