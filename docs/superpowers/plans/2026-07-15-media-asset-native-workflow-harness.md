# Media And Asset Library Native Workflow Harness Implementation Plan

> Execute test-first in the active main task. Keep generated evidence below the
> ignored local-lab root and preserve the unrelated `terminals/` path.

**Goal:** Land `M5.5-media-catalog-native-workflow-harness` as an unattended,
fail-closed, exact-build native gate over generated Media and Asset Library
fixtures.

**Architecture:** Reuse accepted native identity/capture/process primitives,
add a surface-specific fixture/evidence schema, run three isolated UIA-only
launches inside one explicit NUnit test, and reconcile its exact 1/1 TRX and
atomic ignored/local manifest from a Python runner.

**Constraints:** No installed game or proprietary payloads, no playback or
LibVLC initialization, no Explorer/browser/clipboard/export/package actions,
no release/tag/Host/Join, and no broad test thrash during edit loops.

## Task 1: Add Generated Fixture Contracts

**Files:**

- Create `OnslaughtCareerEditor.UiTests/MediaAssetNativeFixture.cs`
- Create `OnslaughtCareerEditor.UiTests/MediaAssetNativeFixtureTests.cs`
- Optionally modify `OnslaughtCareerEditor.UiTests/WinUiVisualSmokeTests.cs`
  only if the existing fixture can safely delegate without changing coverage

**Red tests:**

- exact media relative-path inventory and zero-byte payload hashes;
- synthetic marker root is game-shaped but its `BEA.exe` is zero length;
- schema-2 catalog exact counts and IDs;
- PNG exact dimensions/hash and FBX binary header/model summary;
- generated paths remain confined and reparse-free; and
- regenerated fixtures are byte-identical.

**Implementation:** Materialize the fixture below a caller-owned fresh staging
directory, flush all files, return immutable relative-path/hash records, and
independently reparse the completed fixture before returning it.

**Focused gate:**

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~MediaAssetNativeFixtureTests"
```

## Task 2: Define Evidence, Publication, And Path Contracts

**Files:**

- Create `OnslaughtCareerEditor.UiTests/MediaAssetNativeEvidence.cs`
- Create `OnslaughtCareerEditor.UiTests/MediaAssetNativeEvidenceAcceptance.cs`
- Create `OnslaughtCareerEditor.UiTests/MediaAssetNativeEvidenceAcceptanceTests.cs`
- Create `OnslaughtCareerEditor.UiTests/MediaAssetOwnedPathGuard.cs` only if
  the accepted guard cannot be reused without misleading Save-specific naming

**Red tests:**

- reject wrong schema/run ID/interaction mode;
- reject missing, duplicate, renamed, reordered, rehashed, absolute, escaping,
  or reparse-routed fixture/capture artifacts;
- reject any capture outside the exact eight-file matrix, wrong dimensions,
  markers, focus, identity, or raster hash;
- reject shared launch identities across the three workflows;
- reject wrong audio/video/asset readbacks or any playback-module observation;
- independently reparse the media tree, catalog, PNG, and FBX; and
- publish only a validated, flushed manifest through a fresh sibling rename.

**Focused gate:**

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~MediaAssetNativeEvidenceAcceptanceTests"
```

Commit after Tasks 1-2 are green:

```powershell
git add OnslaughtCareerEditor.UiTests docs/superpowers
git commit -m "test(winui): define media asset native evidence"
```

## Task 3: Add The Three-Launch Native Producer

**Files:**

- Create `OnslaughtCareerEditor.UiTests/MediaAssetNativeSession.cs` or extract
  one genuinely generic session without weakening Save Lab identity checks
- Create `OnslaughtCareerEditor.UiTests/MediaAssetNativeVisualCapture.cs`
- Create `OnslaughtCareerEditor.UiTests/WinUiMediaAssetNativeWorkflowTests.cs`
- Modify shared native files only for a proven reusable primitive

**Red tests/source checks:**

- exact test and environment names exist;
- interaction helpers contain no `.Click`, keyboard, pointer, playback,
  reveal, browse, clipboard, export, or package invocation;
- video launch starts on tab 1 with deferred initialization;
- module census rejects `libvlc.dll` and `libvlccore.dll`; and
- all three sessions use distinct app-data and launch identities.

**Implementation:**

1. Validate runner token and post-build executable/DLL hashes.
2. Materialize the exact fixture and three isolated app configs.
3. Launch Media audio, select `TUTORIAL_intro`, capture normal/760.
4. Launch deferred Media video, select `Credits Video`, assert no LibVLC
   modules, capture normal/760.
5. Launch Asset Library, select synthetic texture, capture normal/760; invoke
   Meshes, select the triangle, validate wireframe/model facts, capture
   normal/760.
6. Validate and atomically publish one schema-1 manifest.
7. Dispose each identity-bound session before starting the next.

**Focused gates:**

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~MediaAssetNative|FullyQualifiedName~NativeWinUi"
npm run test:winui-save-lab-native-workflow
```

Commit when the producer and existing Save Lab gate are green:

```powershell
git add OnslaughtCareerEditor.UiTests
git commit -m "test(winui): produce media asset native evidence"
```

## Task 4: Add The Fail-Closed Outer Runner

**Files:**

- Create `tools/run_winui_media_asset_native_workflow.py`
- Create `tools/run_winui_media_asset_native_workflow_test.py`
- Modify `package.json`
- Modify `CONTRIBUTING.md`
- Modify `VALIDATION.md`

**Red tests:**

- exact Debug/win-x64 build and post-build hashes are mandatory;
- baseline and final relevant-process census must be zero;
- stale partial/accepted roots, reparse points, and manifest swaps fail;
- exact one-total/one-executed/one-passed TRX is required with no skip;
- manifest, fixture, identity, workflow, PNG, and capture matrices are
  independently reconciled;
- missing receipt directory/manifest or changed pre-validation hash denies
  cleanup authority;
- only exact PID/start/path receipt survivors may receive bounded tree cleanup;
- forced cleanup still fails the gate; and
- scratch/build-server cleanup runs on every exit path.

**Implementation:** Reuse `winui_native_acceptance_support.py`; do not fork a
second command, process, PNG, or TRX parser. Keep M5.5 manifest reconciliation
surface-specific.

**Focused gates:**

```powershell
py -3 tools\run_winui_media_asset_native_workflow_test.py
py -3 -m py_compile tools\run_winui_media_asset_native_workflow.py tools\run_winui_media_asset_native_workflow_test.py
npm run test:validation-inventory
```

Commit when green:

```powershell
git add tools package.json CONTRIBUTING.md VALIDATION.md
git commit -m "test(winui): orchestrate media asset native acceptance"
```

## Task 5: Run Native Acceptance And Fix Only Proven Defects

Run:

```powershell
npm run test:winui-media-asset-native-workflow
```

If the gate fails, use systematic debugging. Fix harness defects in the
harness. Change `MediaPage.xaml`, `AssetLibraryPage.xaml`, or code-behind only
when exact native evidence proves a product defect, and add the smallest
source/native regression first. Do not initialize playback to make the test
easier.

After any shared native or product change rerun:

```powershell
npm run test:winui-home-native-visual-focus
npm run test:winui-save-lab-native-workflow
```

Commit only verified corrections with narrowly named commits.

## Task 6: Acceptance, Review, And Campaign Reconciliation

Run the primary lane serially:

```powershell
npm run test:winui-primary-lane
```

Then run proportional closeout:

```powershell
npm run test:validation-inventory
npm run test:docsync
npm run test:doc-commands
npm run test:md-links:public-core
npm run test:generated-output-safety
npm run test:hard-payload-safety
npm run test:repo-hygiene
git diff --check
```

Obtain one normal and one adversarial Codex review plus one sanitized normal
and one sanitized adversarial Cursor/Grok consult for the substantive M5.5
batch. Resolve every Critical/Important finding and rerun the smallest affected
gates; do not recursively start a new envelope for routine fixes.

Update:

- `CURRENT_CAPABILITIES.md` and its byte-identical Lore mirror;
- `goal.campaign.md` and `goal.md`;
- `developer_agent_state.json` and `documentation_agent_state.json`; and
- only command-authority docs changed by the new named gate.

Record exact counts, generated-fixture and no-playback boundaries, ignored/local
evidence disposition, zero final process census, installed game/original
`BEA.exe` untouched, and no release. Commit and fast-forward push only after
remote divergence is still safe, then select the next actionable campaign
slice rather than marking the long-horizon goal complete.

## Plan Self-Review

- The plan builds a new attributable gate instead of expanding an optional
  visual smoke.
- Every input is generated; the synthetic `BEA.exe` marker is zero length and
  never launched.
- Video selection proves deferred catalog behavior and explicitly denies
  decoder/playback initialization.
- Visual evidence is semantic and receipt-bound, not pixel-perfect.
- Product changes require a native failing case; the harness does not pretext
  an unsolicited redesign.
- Existing Home and Save Lab gates protect shared lifecycle behavior.
