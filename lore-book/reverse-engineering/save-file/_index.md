# Save File Documentation

> .BES file format analysis for Battle Engine Aquila career saves

## Overview

This folder contains documentation for the 10,004-byte `.bes` save file format used by the retail/Steam build. In the **true dword view**, integers are stored as normal little-endian 32-bit values and floats are raw IEEE-754. The historical “shift-16” appearance comes from viewing dwords at 4-byte aligned offsets even though `BEA.exe` copies CCareer bytes from/to `file+2`.

Wave902 (`save-options-static-review-wave902`) reviewed the save/options/career surface after loaded Ghidra function-quality closure (`6113/6113 = 100.00%`). It records a **static review slice** for save/options/career on the fixed `10004`-byte container, version `0x4BD1`, true-view base `0x0002`, kill counters at `0x23F6`, options entries at `0x24BE`, `0x56`-byte tail, `CCareer__Load`, `CCareer__Save`, `OptionsTail_Write`, `OptionsTail_Read`, `CFEPOptions__WriteDefaultOptionsFile`, and `CPauseMenu__ResumeGameAndPersistOptions`. Verified read-only backup: `G:\GhidraBackups\BEA_20260526-093817_post_wave902_save_options_static_review_verified`. Runtime menu/controller/Goodies-wall behavior remains separate proof.

The current static-to-proof front door for this area is [Save / Options Controller Byte-Preservation Proof Plan](../binary-analysis/save-options-controller-byte-preservation-proof-plan.md), followed by [Save / Options Controller Byte-Preservation Copied-File Proof](../binary-analysis/save-options-controller-byte-preservation-copied-file-proof.md), [save-options-controller-byte-preservation-copied-file.v1.json](../binary-analysis/save-options-controller-byte-preservation-copied-file.v1.json), [Save / Options Byte-Preservation AppCore Implementation Contract Proof](../binary-analysis/save-options-byte-preservation-appcore-implementation-contract-proof.md), [save-options-byte-preservation-appcore-implementation-contract.v1.json](../binary-analysis/save-options-byte-preservation-appcore-implementation-contract.v1.json), [Save / Options Byte-Preservation Runtime-Proof Readiness Gate](../binary-analysis/save-options-byte-preservation-runtime-proof-readiness-gate.md), [save-options-byte-preservation-runtime-proof-readiness-gate.v1.json](../binary-analysis/save-options-byte-preservation-runtime-proof-readiness-gate.v1.json), [Save / Options Byte-Preservation AppCore Fixture Matrix Proof](../binary-analysis/save-options-byte-preservation-appcore-fixture-matrix-proof.md), and [save-options-byte-preservation-appcore-fixture-matrix.v1.json](../binary-analysis/save-options-byte-preservation-appcore-fixture-matrix.v1.json). The fixture matrix records saveOptionsBytePreservationAppCoreFixtureMatrixStatus=save-options-byte-preservation-appcore-fixture-matrix-complete-copied-real-baseline-services-not-runtime-proof; selectedNextSlice=Static-To-Proof Rebuild Transition Next Safe Slice Selection Refresh Proof Plan; fixtureFamilyCount=8; appCoreFixtureCaseCount=36; unexpectedDiffCount=0; legacyTrapHitCountNonSlot=0; runtimeExecution=false; beLaunch=false; godotWork=false. It proves only copied-baseline AppCore fixture-matrix byte-preservation contracts. Runtime save/load, defaultoptions boot, menu/controller behavior, Goodies wall behavior, patch behavior, visual QA, Godot parity, rebuild parity, and no-noticeable-difference parity remain separate proof. active next static child lane: Static-To-Proof Rebuild Transition Next Safe Slice Selection Refresh Proof Plan.

Completed AppCore fixture-matrix anchor: saveOptionsBytePreservationAppCoreFixtureMatrixStatus=save-options-byte-preservation-appcore-fixture-matrix-complete-copied-real-baseline-services-not-runtime-proof; selectedNextSlice=Static-To-Proof Rebuild Transition Next Safe Slice Selection Refresh Proof Plan; fixtureFamilyCount=8; appCoreFixtureCaseCount=36; containerAnalyzerCaseCount=2; careerKillCategoryCaseCount=5; killBoundaryCaseCount=3; defaultOptionsSettingCaseCount=10; optionsCopyCaseCount=4; controllerKeybindCaseCount=4; slotBitsetCaseCount=4; rejectionNoOpLegacyCaseCount=4; outputCaseCount=29; rejectionCaseCount=5; noOpCaseCount=1; noOpDiffCount=0; unexpectedDiffCount=0; legacyTrapHitCountNonSlot=0; allRejectionsOutputNotCreated=true; keybindDiffsWithinOptionsEntriesAndTailControlScheme=true; slotRoundTripCaseCount=4; derivedInvalidFixtureCount=2; expectedSize=10004; versionWord=0x4BD1; trueViewRule=file_offset = 0x0002 + career_offset; careerSlotsBase=0x240A; careerSlotsEndExclusive=0x248A; optionsEntriesRange=0x24BE-0x26BD; optionsTailRange=0x26BE-0x2713; allOutputsFileSizePreserved=true; allOutputsVersionWordPreserved=true; acceptedFixturesDerivedFromCopiedBaselines=true; invalidFixturesRejectionOnly=true; runtimeExecution=false; beLaunch=false; godotWork=false.

Completed runtime-readiness gate anchor: saveOptionsBytePreservationRuntimeProofReadinessGateStatus=save-options-byte-preservation-runtime-proof-readiness-gate-complete-runtime-deferred-no-launch; selectedNextSlice=Save / Options Byte-Preservation AppCore Fixture Matrix Proof Plan; runtimeObservationReadyNow=false; runtimeDeferred=true; explicitRuntimeObservationArmPresent=false; runtimeExecution=false; beLaunch=false; runtimeObservationRows=0; publicLeakCheck=PASS. active next static child lane: Save / Options Byte-Preservation AppCore Fixture Matrix Proof Plan.

Completed AppCore implementation-contract anchor: saveOptionsBytePreservationAppCoreImplementationContractStatus=save-options-byte-preservation-appcore-implementation-contract-complete-copied-real-baseline-services-not-runtime-proof; selectedNextSlice=Save / Options Byte-Preservation Runtime-Proof Readiness Gate Plan; copiedArtifactCount=10; appCoreServiceProofCaseCount=8; runtimeExecution=false; beLaunch=false; godotWork=false.

## Documents

| Document | Description |
|----------|-------------|
| [save-format.md](save-format.md) | Complete file structure, offset map, and reserved/unmapped-region handling |
| [struct-layouts.md](struct-layouts.md) | CCareerNode, CCareerNodeLink, CGoodie struct definitions |
| [career-graph.md](career-graph.md) | Campaign graph semantics: nodes vs links, `COMPLETE_BROKEN`, safe unlock strategies |
| [career-links.md](career-links.md) | Campaign link index map: link id -> from/to world, lower vs higher unlock conditions |
| [career-unlock-recipes.md](career-unlock-recipes.md) | Per-world unlock recipes: incoming link ids, minimal manual link patch, and natural unlock conditions |
| [grade-system.md](grade-system.md) | Raw float ranking bits, S-E grade calculation |
| [goodies-system.md](goodies-system.md) | 233 retail-displayable gallery slots (0-232), conditions, character bios |
| [kill-tracking.md](kill-tracking.md) | Kill categories at 0x23F6 (packed meta+payload; first two counters are confirmed metadata-bearing, and patchers should preserve the top byte on all five counters conservatively), unlock thresholds |

## Quick Reference

**File Layout:**
```
0x0000: Version word (0x4BD1) (16-bit)
0x0002: new_goodie_count (CCareer +0x0000)
0x0006: CCareerNode[100] (6400 bytes)
0x1906: CCareerNodeLink[200] (1600 bytes)
0x1F46: CGoodie[300] (1200 bytes)
0x23F6: Kill counters (20 bytes; packed meta+payload)
0x240A: Tech slots mSlots[32] (128 bytes)
0x248A: mCareerInProgress (CCareer +0x2488)
0x248E: mSoundVolume (float)
0x2492: mMusicVolume (float)
0x2496: g_bGodModeEnabled (CCareer +0x2494)
0x249A: reserved/unused; preserve
0x249E: Invert Y (Flight/Jet) (P1)
0x24A2: Invert Y (Flight/Jet) (P2)
0x24A6: Invert Y (Walker) (P1)
0x24AA: Invert Y (Walker) (P2)
0x24AE: Vibration (P1)
0x24B2: Vibration (P2)
0x24B6: Controller Config (P1)
0x24BA: Controller Config (P2)
0x24BE: Options entries (retail/Steam observed at N=16 => 0x20 * 16 bytes; engine save-size formula is 0x2514 + 0x20*N where N is enabled-entry count)
tail:   0x56-byte OptionsTail snapshot at end of file
```

Load semantics (Steam retail):
- options entries + tail are applied on `defaultoptions.bea` load (`CCareer::Load` flag=0)
- options entries + tail are skipped on career `.bes` load (`CCareer::Load` flag=1)

**Encoding (true dword view):**
- Integers: raw little-endian 32-bit at offsets where `file_offset % 4 == 2`
- Floats: raw IEEE-754
- Booleans/flags: typically raw `0`/`1` stored in 32-bit fields

## See Also

- [../binary-analysis/save-options-static-review-2026-05-26.md](../binary-analysis/save-options-static-review-2026-05-26.md) - Wave902 static review slice for save/options/career (not runtime proof)
- [../binary-analysis/save-options-controller-byte-preservation-proof-plan.md](../binary-analysis/save-options-controller-byte-preservation-proof-plan.md) - Static-to-proof copied-file byte-preservation proof plan for save/options/controller work (not runtime proof)
- [../binary-analysis/save-options-controller-byte-preservation-copied-file-proof.md](../binary-analysis/save-options-controller-byte-preservation-copied-file-proof.md) - Copied-file byte-preservation proof for save/options/controller work (not runtime proof)
- [../source-code/](../source-code/) - Stuart's source code analysis
- [../game-mechanics/](../game-mechanics/) - God mode, cheat codes
- [CURRENT_CAPABILITIES.md](/CURRENT_CAPABILITIES.md) - Current app surface and supported workflows

---

*Last updated: 2026-05-26*
