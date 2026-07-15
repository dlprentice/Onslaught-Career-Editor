# Media And Asset Library Native Workflow Harness Design

Status: unattended maintainer-approved design
Date: 2026-07-15

## Goal

Turn representative Media and Asset Library catalog journeys into one
repeatable native WinUI acceptance gate. The gate must launch only the exact
repository build, use generated public-safe fixtures, exercise discovery,
filtering, selection, texture preview, and model wireframe behavior through UI
Automation, validate normal and compact rendering from receipt-bound pixels,
and publish complete ignored/local evidence without subjective review.

This is Toolkit catalog-workflow evidence only. It does not consume a Battle
Engine Aquila install or copied retail payload, initialize playback, launch
Explorer, a browser, VLC, or BEA, prove extraction completeness or retail
formats, authorize Host/Join, or authorize a release.

## Existing Foundation

The product already has:

- source and AppCore coverage for synthetic Media directory discovery;
- a deterministic schema-2 Asset Library fixture in the broad visual smoke;
- explicit native Media playback and private real-catalog smokes;
- exact-build Home and Save Lab gates with receipt-bound identity, captures,
  atomic ignored/local publication, exact TRX accounting, and zero-process
  cleanup; and
- shared process, command, PNG, TRX, capture, and Toolkit-pixel primitives.

The broad visual smoke is optional, captures dated directories without a
canonical manifest, accepts ambient build selection, and does not bind catalog
behavior to exact fixture bytes. The real Media and Asset smokes require a
local install or private extraction output and may initialize decoders. They
cannot be the unattended fresh-worktree contract for M5.5.

## Selected Architecture

Add a separate `test:winui-media-asset-native-workflow` gate. Preserve Home and
Save Lab as independently attributable surfaces. Reuse their low-level native
identity, visual-capture, process-census, TRX, cleanup, and path-safety
primitives while keeping M5.5's fixture, workflow, and manifest schema
surface-specific.

One explicit native test performs three isolated launches:

1. **Media audio selection.** Load a synthetic game-shaped directory containing
   a zero-byte, non-executable `BEA.exe` marker, `data/`, and four zero-byte OGG
   catalog names spanning Music, Mission, Tutorial, and Status Messages. Start
   directly on the Audio Library, set the search through UIA ValuePattern,
   select `TUTORIAL_intro` through SelectionItem, and verify the selected title,
   public-safe source summary, catalog group, and enabled Play action without
   invoking it.
2. **Media video selection without playback initialization.** Reuse the same
   synthetic root with four zero-byte VID catalog names spanning Main Videos,
   Cutscenes, and Mission Briefings. Start directly on the Video page through
   `ONSLAUGHT_WINUI_TEST_INITIAL_MEDIA_TAB=1`, whose constructor deliberately
   defers video initialization. Search and select `UsTheMovie` through UIA,
   require the human label `Credits Video` and public-safe source summary, and
   assert the live process has loaded neither `libvlc.dll` nor
   `libvlccore.dll`. Do not click the Video tab or any transport/reveal action.
3. **Asset catalog browsing.** Load a generated schema-2 catalog containing one
   texture, one loose mesh, one embedded mesh, and one model Goodie. Its local
   exports are a deterministic synthetic PNG and a minimal binary FBX triangle
   with three vertices, three polygon-index entries, one material, and one
   texture binding. Select the texture, verify the generated preview, then
   invoke the Meshes tab through UIA, select the loose mesh, and verify the
   wireframe and model metadata. Do not invoke export, clipboard, package, or
   external-open actions.

Each launch receives its own isolated app-data directory and empty discovery
candidates. The synthetic game-shaped directory is never executable and is
never passed to a process launcher.

## Exact Visual Contract

The eight captures are:

- `media-audio-selected-normal.png` and `media-audio-selected-760.png`;
- `media-video-selected-normal.png` and `media-video-selected-760.png`;
- `asset-texture-selected-normal.png` and
  `asset-texture-selected-760.png`; and
- `asset-model-wireframe-normal.png` and
  `asset-model-wireframe-760.png`.

Normal means an exact 1100x900 HWND and compact means an exact 760x820 HWND.
Each phase has a fixed focus target and fixed UIA marker set. The capture path
must realize any required TreeView/ListView or preview-scroll item using UIA
ScrollItem/Scroll only, reject horizontal overflow at the accepted widths,
bind global focus to the exact launch HWND, and require every marker to remain
inside the bitmap before and after the shutter.

Toolkit images must be fully opaque at sampled points, have meaningful
luminance/color coverage, contain the rendered Toolkit header, reject the
known Codex Desktop signature, and contain rendered activity inside every
marker rectangle. Per-run raster hashes protect artifact integrity; they are
not cross-machine pixel goldens.

If the native gate proves compact clipping or non-realized controls, the slice
may make only the smallest responsive MediaPage or AssetLibraryPage correction,
first guarded by a failing source/native regression. Both existing Home and
Save Lab native gates must remain green after shared or shell-level changes.

## Interaction And Identity Contract

Before every launch, the child hashes the exact adjacent repository
Debug/win-x64 executable and product DLL and compares them with runner-provided
post-build hashes. Every launch receipt binds PID, UTC start time, image
path/hash, loaded product DLL path/hash, main HWND, UIA HWND, and owner PID.
Every shutter revalidates the complete receipt before and after capture.

Allowed interaction is UIA Value, SelectionItem, ScrollItem, Scroll, Focus,
and Invoke only. Keyboard, pointer, FlaUI Click, playback, reveal, browse,
clipboard, export, and package actions are forbidden. The workflow records
whether LibVLC modules were present and accepts only `false`.

The outer runner requires zero Toolkit, testhost, vstest, BEA, debugger, and
playback-helper processes before and after the test. Cleanup authority remains
bound to exact PID/start/path receipts. An unreceipted survivor is reported but
not mutated; a receipt-authorized forced cleanup makes the gate fail even when
the final census becomes zero.

## Fixture And Evidence Contract

One invocation creates one sibling partial directory below
`local-lab/winui-media-asset-native-workflow/`. Generated fixtures, isolated
app data, captures, TRX, and the canonical schema-1 manifest remain ignored and
local.

The manifest contains:

- the lowercase 32-hex invocation ID and fixed UIA-only/no-playback mode;
- a canonical inventory for every synthetic media and asset fixture file with
  relative path, length, and SHA-256;
- exactly eight capture receipts with phase, dimensions, fixed marker bounds,
  owner-bound focus, and full launch identity;
- exactly three workflow receipts for Media audio, Media video, and Asset
  Library with selected row/readback values and full launch identity; and
- an explicit `PlaybackModulesLoaded=false` observation for the video launch.

Child-side acceptance reparses the asset catalog, PNG, binary FBX model
summary, and synthetic Media file inventory independently of the UIA strings.
The outer runner independently repeats the exact path confinement, hashes,
media inventory, catalog counts/IDs, PNG dimensions, binary FBX header, capture
set/dimensions, workflow mappings, identities, and no-playback assertion.

All manifest artifact paths are normalized relative paths confined to the
staging directory. The child validates and flushes a temporary manifest,
renames it to the canonical name, reopens it, and atomically publishes the
whole same-volume sibling directory. On failure, the caller-owned partial
directory remains for the outer runner to validate before removal.

The exact evidence root, every recursive cleanup tree, canonical manifest, and
all retained artifacts must remain regular and reparse-free. Receipt validation
is repeated before parsing, after parsing, and immediately before any
receipt-authorized survivor cleanup. The manifest hash captured before parsing
must remain unchanged before cleanup.

## Rejected Approaches

### Extend the broad visual smoke

Rejected because it permits skips, uses ambient build selection and dated
directories, and has no exact fixture/manifest/process contract.

### Use the installed game or a private full asset catalog

Rejected because it makes the gate non-reproducible, crosses the durable
public/local boundary, and could confuse catalog UI proof with extraction or
retail-format completeness.

### Exercise playback for stronger Media proof

Rejected because catalog discovery/selection is the M5.5 contract. Playback
adds decoder, device, timing, and proprietary-payload dependencies already
covered by separate explicit local smokes. This gate proves that selecting a
synthetic row does not itself initialize playback.

### Use one app launch for every phase

Rejected because Media audio, deferred video, and Asset Library have different
initialization boundaries. Three isolated identities make failures attributable
and prevent a prior phase from loading a decoder or carrying selection state.

### Pixel-perfect screenshot goldens

Rejected because Windows rendering can vary without changing the workflow.
Semantic markers, exact bounds, focus ownership, rendered activity, and
per-run integrity hashes are the bounded contract.

## Verification

The smallest complete proof set is:

- fixture, manifest, artifact, path, runner, TRX, and cleanup unit tests;
- focused existing Media/Asset AppCore and UI source tests;
- the existing Home and Save Lab runner unit tests after shared changes;
- `npm run test:winui-media-asset-native-workflow`;
- the primary WinUI lane before handoff;
- command inventory, docs/mirror/link, generated-output, hard-payload, repo
  hygiene, JSON, Python compile, and `git diff --check` gates; and
- a final zero relevant-process census.

Acceptance remains bounded to the exact repository build, generated fixture
recipe, selected states, and two window sizes. It is not retail game evidence,
media decoding proof, extraction completeness, general accessibility,
packaged-release fitness, or visual parity.
