# MissionScript Slot Bitset/Save Copied-File Byte-Diff Readiness Note

Status: complete copied-file byte-diff proof
Date: 2026-06-09
Scope: `missionscript-slot-bitset-save-copied-file-byte-diff`

This slice completed the copied-file child lane after the deterministic codec proof. It used a validated copied real career `.bes` baseline from prior ignored evidence and published only sanitized public artifacts.

Proof name: MissionScript Slot Bitset/Save Copied-File Byte-Diff Proof.

Artifacts:

- `reverse-engineering/binary-analysis/missionscript-slot-bitset-save-copied-file-byte-diff-proof.md`
- `reverse-engineering/binary-analysis/missionscript-slot-bitset-save-copied-file-byte-diff.v1.json`
- `tools/missionscript_slot_bitset_save_copied_file_byte_diff_probe.py`

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

Validation scope:

- The copied save remained `10004` bytes and retained version `0x4BD1`.
- The source copied baseline was copied before write, the source remained unchanged, and the target mask was initially clear before the set operation.
- The set operation changed only the true-view target range `0x240E-0x2411`, with observed dword XOR `0x60000000`.
- No-op copy, idempotent set, and clear roundtrip checks passed.
- Public artifacts omit source paths, source hashes, artifact hashes, and raw before/after dwords.

Boundary:

This is copied-file byte-diff evidence only. Runtime MissionScript execution, runtime command effects, runtime slot persistence, runtime save/load behavior, runtime defaultoptions behavior, tutorial progression, live loose-MSL loading, packed-resource script selection, defaultoptions mutation, installed-game changes, Ghidra mutation, executable patching, Godot parity, rebuild implementation, rebuild parity, and no-noticeable-difference parity remain separate proof lanes.
