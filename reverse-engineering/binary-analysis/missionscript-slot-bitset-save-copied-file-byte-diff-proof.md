# MissionScript Slot Bitset/Save Copied-File Byte-Diff Proof

Status: copied-file byte-diff proof complete, not runtime proof
Last updated: 2026-06-09
Scope: `missionscript-slot-bitset-save-copied-file-byte-diff`

This proof completes the copied-file child lane selected by the [MissionScript Slot Bitset/Save Deterministic Codec Proof Plan](missionscript-slot-bitset-save-deterministic-codec-proof-plan.md). It uses a validated copied real career `.bes` baseline from prior ignored evidence, copies it again into a new private evidence root, applies the slot `61`/`62` target mask to the copied buffer, and records a sanitized public schema without source paths, source hashes, artifact hashes, raw before/after dwords, runtime launch, Ghidra mutation, executable patching, Godot work, or save synthesis.

Machine-checkable artifact:

- [missionscript-slot-bitset-save-copied-file-byte-diff.v1.json](missionscript-slot-bitset-save-copied-file-byte-diff.v1.json)

Proof tokens:

- `slotBitsetSaveCopiedFileByteDiffStatus=missionscript-slot-bitset-save-copied-file-byte-diff-complete-copied-real-baseline-not-runtime-proof`
- `previousSlice=MissionScript Slot Bitset/Save Deterministic Codec Proof Plan`
- `selectedFixtureFamily=slot-bitset-save`
- `selectedFixturePath=slot-bitset-save-core-handler-and-career-bridge`
- `selectedNextSlice=MissionScript Slot Bitset/Save Clean-Room Codec Interface Proof Plan`
- `copiedArtifactCount=5`
- `sourcePathsPublic=false`
- `sourceHashesPublic=false`
- `artifactHashesPublic=false`
- `rawBeforeAfterDwordsPublic=false`
- `copyBeforeWrite=true`
- `sourceAndOutputPathsDistinct=true`
- `sourceToNewBaselineDiffCount=0`
- `sourceUnchanged=true`
- `expectedSize=10004`
- `versionWord=0x4BD1`
- `trueViewRule=file_offset = 0x0002 + career_offset`
- `slots=61,62`
- `allowedDwordRange=0x240E-0x2411`
- `allowedDwordXorMask=0x60000000`
- `observedDwordXorMask=0x60000000`
- `baselineSelectedMaskInitiallyClear=true`
- `baselineToSetChangedOffsets=0x2411`
- `unexpectedDiffCount=0`
- `legacyTrapHitCount=0`
- `baselineToNoopDiffCount=0`
- `setToIdempotentDiffCount=0`
- `clearToBaselineDiffCount=0`
- `slotDword0Unchanged=true`
- `optionsEntriesUnchanged=true`
- `optionsTailUnchanged=true`
- `saveSynthesis=false`
- `runtimeExecution=false`
- `beLaunch=false`
- `ghidraMutation=false`
- `executablePatching=false`
- `godotWork=false`

## Static Closeout Context

| Track | Current |
| --- | --- |
| Static Ghidra function-quality closure | `6411/6411 = 100.00%` |
| Commentless / exact-undefined / `param_N` debt | `0 / 0 / 0` |
| Expanded post-100 static surface | `1560/1560 = 100.00%` |
| Active current-risk focused accounting | `1179/1179 = 100.00%` |
| Remaining active focused work | `0` |
| Latest verified Ghidra backup | `latestGhidraBackupClass=verified-static-backup-redacted` |

This proof does not change `static-reaudit-progress.json`, `static-reaudit-current-risk-ledger.json`, or the static RE percentages.

## Byte-Diff Result

| Check | Result |
| --- | --- |
| Container shape | Copied career save remains `expectedSize=10004`, `versionWord=0x4BD1`, with `trueViewRule=file_offset = 0x0002 + career_offset`. |
| Provenance guard | `copyBeforeWrite=true`; `sourceAndOutputPathsDistinct=true`; `sourceToNewBaselineDiffCount=0`; `sourceUnchanged=true`. |
| Target slots | `slots=61,62`; dword index `1`; `allowedDwordRange=0x240E-0x2411`. |
| Target masks | `slot61Mask=0x20000000`; `slot62Mask=0x40000000`; combined `allowedDwordXorMask=0x60000000`. |
| Set operation | `baselineSelectedMaskInitiallyClear=true`; `observedDwordXorMask=0x60000000`; `baselineToSetChangedOffsets=0x2411`; `unexpectedDiffCount=0`; `legacyTrapHitCount=0`. |
| No-op copy | `baselineToNoopDiffCount=0`. |
| Idempotent set | `setToIdempotentDiffCount=0`. |
| Clear roundtrip | `setToClearDwordXorMask=0x60000000`; `clearToBaselineDiffCount=0`. |
| Preservation | `slotDword0Unchanged=true`; remaining slot storage after the target dword unchanged; post-slot fields unchanged; `optionsEntriesUnchanged=true`; `optionsTailUnchanged=true`. |

The comparison mode is `little-endian dword XOR mask subset, not single-byte expectation`. The observed changed byte is useful as a sanity anchor, but the proof is governed by the dword mask in range `0x240E-0x2411`.

## Claim Boundary

This proves copied-file byte-diff behavior for the selected slot bitset save codec: a copied real career `.bes` baseline can be copied, no-oped, set for slots `61`/`62`, idempotently re-set, and cleared back to the copied baseline while preserving container shape and all checked non-target ranges.

It does not prove runtime MissionScript execution, runtime command effects, runtime slot persistence, runtime save/load behavior, runtime defaultoptions behavior, tutorial progression, live loose-MSL loading, packed-resource script selection, defaultoptions mutation, installed-game changes, Ghidra mutation, executable patching, Godot parity, rebuild implementation, rebuild parity, or no-noticeable-difference parity.
