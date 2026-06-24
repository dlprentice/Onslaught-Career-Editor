# MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Visual Frame Triage Proof

Status: complete direct Level100 copied-profile visual frame triage proof, not visual correctness or MissionScript/runtime behavior proof
Last updated: 2026-06-09
Scope: `missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage`
Public proof anchor: `missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage-proof.md`
Completed slice token: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Visual Frame Triage Proof Plan`

This slice triages the private still frame captured by the completed direct `-skipfmv -level 100` copied-profile screenshot-capture proof. The raw PNG remains private under the ignored evidence root; public docs expose only visual classes, dimensions already published by the screenshot-capture proof, and claim-boundary flags.

Machine-checkable result: `missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-visual-frame-triage.v1.json`.

Previous completed slice: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Screenshot Capture Proof Plan`, backed by `missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture-proof.md` and `missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture.v1.json`.

## Static Authority

Current static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup: `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

This visual triage proof performs no Ghidra mutation and does not require a new Ghidra backup.

## Visual Triage Result

The private frame triage records:

- `status=COMPLETE`
- `directLevel100VisualFrameTriageStatus=direct-level100-private-still-frame-visually-triaged`
- `profileId=level100-clean-materialized-20260608-214752`
- `selectedRoute=direct-level100-candidate`
- `launchArguments=-skipfmv -level 100`
- `sourceCaptureStatus=direct-level100-copied-profile-window-still-frame-captured`
- `captureFrameCount=1`
- `captureWidth=656`
- `captureHeight=539`
- `visualTriageMethod=codex-root-private-still-frame-review`
- `sourceCaptureProof=missionscript-level100-tutorial-copied-profile-runtime-observation-direct-level100-screenshot-capture.v1.json`
- `sourceCaptureFrameCount=1`
- `triagedFrameCount=1`
- `newLaunch=false`
- `newScreenshotCapture=false`
- `captureArtifactClass=private-still-frame-png`
- `privateFrameArtifactClass=private-still-frame-png`
- `privateFrameReviewedByClass=codex-root-private-visual-triage`
- `captureArtifactPublished=false`
- `privateProofAssetPublished=false`
- `privatePathIncluded=false`
- `rawArtifactIncluded=false`
- `privateCaptureLocatorIncluded=false`
- `privateArtifactHashIncluded=false`
- `privateArtifactBytesIncluded=false`
- `privateWindowIdentifiersIncluded=false`
- `visibleStateClass=in-level-visual-candidate`
- `visualFrameReadable=true`
- `visualFrameBlank=false`
- `visualFrameOcclusionClass=unknown`
- `visualFrameTriageRows=1`
- `visibleTextExcerptPublished=false`
- `visualCorrectnessClaim=false`
- `pixelCorrectnessClaim=false`
- `beWindowFrameVisible=true`
- `inGameRenderedFrameVisible=true`
- `sceneNotBlackOrBlank=true`
- `terrainSkyLightingVisible=true`
- `cockpitHudVisible=true`
- `centralReticleVisible=true`
- `leftRadarHudVisible=true`
- `rightCircularHudVisible=true`
- `bottomTutorialTextPanelVisible=true`
- `tutorialTextGlyphsVisible=true`
- `menuOnlyOrDesktopOnlyFrame=false`
- `crashDialogVisible=false`
- `blankFrameVisible=false`
- `visualCorrectnessProven=false`
- `exactTextOcrPerformed=false`
- `missionScriptRuntimeEvidenceRows=0`
- `nativeInput=false`
- `debuggerAttachment=false`
- `godotWork=false`
- `privatePathLeakCount=0`
- `rawArtifactLeakCount=0`
- `publicLeakCheck=PASS`

No public artifact contains the raw PNG path, raw PNG hash, raw PNG byte count, process id, window handle, capture source hint, or private proof path.

## Level100 Static Anchors Preserved

The triage proof preserves the same static context as non-runtime background only; this frame does not prove those static anchors executed at runtime:

- Source-selection anchors: `0x00539dc0`, `0x00539ca0`, `this+0x20`, `this+0x124`, and `CDXMemBuffer__InitFromFile`.
- Event ingress: `26` unique event names, `34` handlers, and `41` `PostEvent` callsites.
- Event mismatch row: `Destroyed Friendly Building` versus `Friendly Building Destroyed`.
- Message/text/speaker: `45` `PlayCharMessage*` rows, `43` message tokens, `6` `AddHelpMessage` tokens, speakers `P_TATIANA`, `P_KRAMER`, and `P_TECHNICIAN`, and `68/68` static tokens resolved with `0` missing references.
- HUD/display: `HUD_BATTLE_LINE_MAP`, `HUD_RADAR`, `7` `HighlightHudPart`, and `7` `UnHighlightHudPart`.
- Object/spawn: `18` raw `GetThingRef`, `15` unique object names, `20` `SpawnThing`, `Target Drone`, `Air Trainer`, `Target Tank`, and `Target Truck`.
- Slot/objective: `4` `GetSlot`, `4` `SetSlotSave`, `_100_OBJECTIVE_1` through `_100_OBJECTIVE_4`, and `LOSE_TUTORIAL_BROKE`.

## Claims

This slice proves only:

- The previously captured direct Level100 copied-profile private still frame contains a nonblank rendered game frame.
- The frame is not merely a menu-only, desktop-only, blank, or crash-dialog capture.
- The frame visibly includes broad gameplay, HUD, and tutorial-overlay classes: window frame, in-game scene, terrain, sky, lighting, cockpit HUD, central reticle, left radar HUD, right circular HUD, bottom tutorial text panel, and visible tutorial text glyphs.
- The visual triage was recorded without publishing the raw still-frame artifact.

This slice does not prove runtime MissionScript execution, Level100 script source selection, runtime command effects, event outcomes, live loose-MSL loading, packed-vs-loose script selection, runtime Level100 mission outcome, runtime objective UI, runtime message/audio output, exact text/OCR identity, runtime HUD flashing, runtime object identity, `SpawnThing`, `GetThingRef`, visual correctness, occlusion-free pixel correctness, timing correctness, native input, debugger observation, in-game screenshot command behavior, Godot parity, rebuild parity, or no-noticeable-difference parity.

Follow-up child lane: `MissionScript Level100 Tutorial Copied-Profile Runtime Observation Direct Level100 Text Overlay Correlation Proof Plan`.
