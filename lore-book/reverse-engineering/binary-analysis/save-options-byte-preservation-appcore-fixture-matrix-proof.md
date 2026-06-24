# Save / Options Byte-Preservation AppCore Fixture Matrix Proof

Status: complete copied-real-baseline AppCore fixture matrix, not runtime proof
Date: 2026-06-09

This slice expands the save/options AppCore proof from a narrow implementation-contract sample into a bounded copied-real-baseline fixture matrix. Accepted fixture outputs are derived from copied private baselines; derived invalid fixtures are rejection-only. This is still non-runtime proof.

Evidence schema: [save-options-byte-preservation-appcore-fixture-matrix.v1.json](save-options-byte-preservation-appcore-fixture-matrix.v1.json)

Core result tokens:

- saveOptionsBytePreservationAppCoreFixtureMatrixStatus=save-options-byte-preservation-appcore-fixture-matrix-complete-copied-real-baseline-services-not-runtime-proof
- previousSlice=Save / Options Byte-Preservation Runtime-Proof Readiness Gate
- selectedNextSlice=Static-To-Proof Rebuild Transition Next Safe Slice Selection Refresh Proof Plan
- toolProjectPath=tools/SaveOptionsAppCoreFixtureMatrixHarness/SaveOptionsAppCoreFixtureMatrixHarness.csproj
- appCoreSavePatchPath=OnslaughtCareerEditor.AppCore/BesFilePatcher.cs
- saveEditorServicePath=OnslaughtCareerEditor.AppCore/SaveEditorService.cs
- configurationEditorServicePath=OnslaughtCareerEditor.AppCore/ConfigurationEditorService.cs
- slotCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs
- appCoreServicesUsed=true
- productUiWired=false
- harnessFileIo=true
- privateArtifactMaterialized=true
- copiedArtifactCount=36
- sourcePathsPublic=false
- sourceHashesPublic=false
- artifactPathsPublic=false
- artifactHashesPublic=false
- rawBytesPublic=false
- acceptedFixturesDerivedFromCopiedBaselines=true
- invalidFixturesRejectionOnly=true

Container and true-view anchors:

- expectedSize=10004
- versionWord=0x4BD1
- trueViewRule=file_offset = 0x0002 + career_offset
- careerSlotsBase=0x240A
- careerSlotsEndExclusive=0x248A
- optionsEntriesRange=0x24BE-0x26BD
- optionsTailRange=0x26BE-0x2713
- allOutputsFileSizePreserved=true
- allOutputsVersionWordPreserved=true

Matrix accounting:

- fixtureFamilyCount=8
- appCoreFixtureCaseCount=36
- containerAnalyzerCaseCount=2
- careerKillCategoryCaseCount=5
- killBoundaryCaseCount=3
- defaultOptionsSettingCaseCount=10
- optionsCopyCaseCount=4
- controllerKeybindCaseCount=4
- slotBitsetCaseCount=4
- rejectionNoOpLegacyCaseCount=4
- outputCaseCount=29
- rejectionCaseCount=5
- noOpCaseCount=1
- noOpDiffCount=0
- unexpectedDiffCount=0
- legacyTrapHitCountNonSlot=0
- allRejectionsOutputNotCreated=true
- keybindDiffsWithinOptionsEntriesAndTailControlScheme=true
- slotRoundTripCaseCount=4
- derivedInvalidFixtureCount=2

Representative case anchors:

- career-kill-aircraft
- career-kill-vehicles
- career-kill-emplacements
- career-kill-infantry
- career-kill-mechs
- kill-negative-clamps-zero
- kill-zero-boundary
- kill-overflow-clamps-max
- sound-volume
- music-volume
- walker-invert-p1
- walker-invert-p2
- flight-invert-p1
- flight-invert-p2
- vibration-p1
- vibration-p2
- controller-config-p1
- controller-config-p2
- options-copy-entries-only
- options-copy-tail-only
- options-copy-combined
- options-copy-same-source-noop
- keybind-look-mousex
- keybind-zoom-wheel
- keybind-fire-mouseleft-mirror
- keybind-invalid-token-rejected
- slot-bitset-pair-0-31
- slot-bitset-pair-32-63
- slot-bitset-pair-128-159
- slot-bitset-pair-224-255
- save-no-selected-sections-rejected
- config-no-pending-rejected
- wrong-size-derived-rejected
- wrong-version-derived-rejected

Negative guards:

- saveSynthesis=false
- installedGameMutation=false
- originalExecutableMutation=false
- runtimeExecution=false
- beLaunch=false
- newLaunch=false
- screenshotCapture=false
- nativeInput=false
- debuggerAttachment=false
- copiedExecutablePatchApplied=false
- binaryPatchEngineUsed=false
- patchCatalogTouched=false
- ghidraMutation=false
- executablePatching=false
- godotWork=false
- rebuildImplementation=false
- runtimeSaveLoadProof=false
- runtimeDefaultOptionsProof=false
- publicLeakCheck=PASS

What this proves:

- AppCore copied-baseline save/options fixture coverage exists across eight bounded families.
- All five kill categories stay inside their true-view lower-24 payload bytes while preserving metadata.
- Defaultoptions scalar, controller, keybind, and options-copy cases stay inside expected true-view fields or options ranges.
- Representative copied-baseline slot-bitset cases round-trip inside expected saved dwords.
- No-op and rejection cases are bounded and do not create unintended outputs.

What remains separate:

- Runtime save/load behavior.
- Runtime defaultoptions boot behavior.
- Runtime menu behavior.
- Runtime controller remap/input behavior.
- Runtime Goodies wall behavior.
- Installed game mutation or original executable mutation.
- Product UI behavior.
- Ghidra mutation.
- Executable patching.
- Godot parity.
- Rebuild implementation, rebuild parity, and no-noticeable-difference parity.
