# MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Executable Patch Readiness Note

Status: complete copied-executable stable patch proof, not launch or runtime proof
Date: 2026-06-08
Scope: `missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch`

This slice dry-ran, applied, and read back four stable patch-catalog rows on the copied `BEA.exe` inside the sanitized Level100 copied-profile artifact-root class. It used the clean copied profile from the materialization proof and preserved a clean backup beside the copied executable. It did not run BEA, capture screenshots or frames, drive native input, attach a debugger, start Godot work, or claim runtime MissionScript behavior.

This readiness note is the release-facing summary for the MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Executable Patch Proof.

Previous completed slice: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Copied-Profile Materialization Proof Plan`.

Public proof files:

- `reverse-engineering/binary-analysis/missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch-proof.md`
- `reverse-engineering/binary-analysis/missionscript-level100-tutorial-copied-profile-runtime-observation-copied-executable-patch.v1.json`
- `tools/missionscript_level100_tutorial_copied_profile_runtime_observation_copied_executable_patch_probe.py`

Static authority remains:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup: `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Patch proof summary:

- `status=COMPLETE`
- `patchStatus=stable-copied-executable-patched`
- `profileId=level100-clean-materialized-20260608-214752`
- `artifactRootClass=repo-local-ignored-private-evidence-root`
- `targetExecutableClass=copied-profile-BEA.exe`
- Patch helper: `tools/apply_bea_catalog_patch.py`
- Patch catalog: `patches/catalog/patches.v2.json`
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

Stable rows:

| Patch id | Track | File offset | Dry-run state | Apply before | Apply after | Read-back state |
| --- | --- | --- | --- | --- | --- | --- |
| `resolution_gate` | `stable` | `0x129696` | `ready (original)` | `ready (original)` | `already patched` | `already patched` |
| `force_windowed` | `stable` | `0x12A644` | `ready (original)` | `ready (original)` | `already patched` | `already patched` |
| `version_overlay_use_patched_format_pointer` | `stable` | `0x6416F` | `ready (original)` | `ready (original)` | `already patched` | `already patched` |
| `version_overlay_patched_format_cave_string` | `stable` | `0x1AA444` | `ready (original)` | `ready (original)` | `already patched` | `already patched` |

The experimental `skip_auto_toggle` row remains unarmed and is not part of this proof.

Level100 static source-selection anchors preserved for the later launch-command proof: `0x00539dc0`, `0x00539ca0`, `this+0x20`, `this+0x124`, and `CDXMemBuffer__InitFromFile`.

What this proves:

- The copied executable patch dry-run saw all four stable rows in `ready (original)` state.
- The copied executable apply wrote the copied target and left all four stable rows in `already patched` state.
- The copied executable read-back dry-run saw all four stable rows in `already patched` state with no bytes written.
- A clean backup exists beside the copied target and matches the canonical clean Steam retail/Ghidra specimen hash.
- The installed game root and original executable remained read-only.

What remains unproven:

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

Next selected child lane: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Launch Command Proof Plan`.
