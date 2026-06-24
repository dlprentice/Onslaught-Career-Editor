# Save / Options Byte-Preservation AppCore Fixture Matrix Readiness Note

Status: complete AppCore fixture-matrix proof, not runtime proof
Date: 2026-06-09

This readiness note records the public-safe closeout for the Save / Options Byte-Preservation AppCore Fixture Matrix Proof.

Artifacts:

- Proof: `reverse-engineering/binary-analysis/save-options-byte-preservation-appcore-fixture-matrix-proof.md`
- Schema: `reverse-engineering/binary-analysis/save-options-byte-preservation-appcore-fixture-matrix.v1.json`
- Harness: `tools/SaveOptionsAppCoreFixtureMatrixHarness/SaveOptionsAppCoreFixtureMatrixHarness.csproj`
- Probe: `tools/save_options_byte_preservation_appcore_fixture_matrix_probe.py`

Closeout tokens:

- saveOptionsBytePreservationAppCoreFixtureMatrixStatus=save-options-byte-preservation-appcore-fixture-matrix-complete-copied-real-baseline-services-not-runtime-proof
- previousSlice=Save / Options Byte-Preservation Runtime-Proof Readiness Gate
- selectedNextSlice=Static-To-Proof Rebuild Transition Next Safe Slice Selection Refresh Proof Plan
- toolProjectPath=tools/SaveOptionsAppCoreFixtureMatrixHarness/SaveOptionsAppCoreFixtureMatrixHarness.csproj
- appCoreSavePatchPath=OnslaughtCareerEditor.AppCore/BesFilePatcher.cs
- saveEditorServicePath=OnslaughtCareerEditor.AppCore/SaveEditorService.cs
- configurationEditorServicePath=OnslaughtCareerEditor.AppCore/ConfigurationEditorService.cs
- slotCodecPath=OnslaughtCareerEditor.AppCore/MissionScriptSlotBitsetSaveCodec.cs
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
- expectedSize=10004
- versionWord=0x4BD1
- trueViewRule=file_offset = 0x0002 + career_offset
- careerSlotsBase=0x240A
- careerSlotsEndExclusive=0x248A
- optionsEntriesRange=0x24BE-0x26BD
- optionsTailRange=0x26BE-0x2713
- allOutputsFileSizePreserved=true
- allOutputsVersionWordPreserved=true
- sourcePathsPublic=false
- sourceHashesPublic=false
- artifactPathsPublic=false
- artifactHashesPublic=false
- rawBytesPublic=false
- acceptedFixturesDerivedFromCopiedBaselines=true
- invalidFixturesRejectionOnly=true
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

This proves only copied-baseline AppCore fixture-matrix behavior. Runtime save/load behavior, runtime defaultoptions boot behavior, runtime menu/controller behavior, runtime Goodies wall behavior, installed-game mutation, executable mutation, product UI behavior, Godot parity, rebuild implementation, rebuild parity, and no-noticeable-difference parity remain separate proof.
