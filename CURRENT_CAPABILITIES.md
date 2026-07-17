# Current Capabilities

Onslaught Toolkit has two deliverables: the WinUI Windows toolkit and the
separately GPL-licensed, RE-informed rebuild. Reverse engineering, Lore, and
local tools support those deliverables; file counts and proof machinery are not
product features.

## WinUI Toolkit

The WinUI 3 app is the primary user-facing product. Its top navigation exposes
Home, Save Lab, Media, Asset Library, Lore, Windowed & Mods, Settings, and
About.

### Save Lab and Game Options

- Analyze existing `.bes` career saves and `.bea` options files.
- Write a separate career-save copy with selected mission, link, Goodie, rank,
  and kill-count changes.
- Edit supported startup, audio, controller, and binding values in a copied
  `defaultoptions.bea`.
- Compare files and show bounded structural details for diagnosis.

The toolkit never synthesizes a career save. AppCore begins with an existing
retail-generated baseline, preserves file size and unknown bytes outside the
selected regions, stages writes beside the destination, and verifies the
committed result. The tracked 10,004-byte fixture is the only narrow save-payload
exception in Git.

### Windowed & Mods

- Treat the configured retail install and original `BEA.exe` as read-only
  source material.
- Create an app-owned playable safe game copy.
- Apply catalogued, expected-byte-verified compatibility changes and optional
  patches only to that copy.
- Launch and stop only the copied-game process started by the app.
- Keep advanced BEA.exe-only technical copies separate from playable profiles.
- Offer a local split-screen launch preset for a safe copy.

Online Host/Join, public matchmaking, native BEA netcode, and active P3/P4 play
are not available. The current evidence boundary is summarized in the
[multiplayer feasibility note](roadmap/original-binary-online-multiplayer-feasibility.md).

### Media, assets, and Lore

- Media browses and plays supported installed audio/video as read-only input.
- Asset Library loads an existing generated local catalog and previews supported
  PNG/FBX metadata and bounded wireframes. It does not extract the installed
  game or bundle retail assets.
- Lore provides search, history, and an embedded reader for the canonical
  articles under [`lore/`](lore/_index.md). Portable builds use a short generated
  content pack; project source and external links are labeled as browser-opening
  actions.

The short [`lore-book/BOOK.md`](lore-book/BOOK.md) file is a package entry guide,
not a mirrored documentation tree.

## AppCore, CLI, and host

`OnslaughtCareerEditor.AppCore` owns save/options parsing and patching, unknown-
byte preservation, guarded publication, copied-target enforcement, patch plans,
media discovery, generated-asset catalogs, and Lore loading.

`OnslaughtCareerEditor.Cli` is the supported command-line surface for save and
options analysis/patching plus selected catalog workflows. Run its current help
instead of relying on copied command lists:

```powershell
npm run test:cli
```

`OnslaughtCareerEditor.AppCore.Host` remains a JSON/stdio diagnostic bridge for
read-only plans and bounded material-package operations. Exact-arm output
commands write only to validated caller-selected or app-owned targets; they do
not license extracted assets or prove renderer/rebuild parity.

## Rebuild

[`rebuild/`](rebuild/README.md) contains a GPL-3.0-or-later, RE-informed
original-code reconstruction. `OnslaughtRebuild.Core` owns deterministic
fixed-step simulation, state hashing, command-tape replay, movement, morphing,
energy/shield state, targets, and projectiles. The client layer owns scheduling,
input adaptation, camera, rendering, audio, and presentation rather than
simulation truth.

The Godot First Flight client uses original procedural content and needs no
retail installation or proprietary assets. It is a small playable prototype,
not a strict clean-room implementation and not retail gameplay, mission,
content, audio, online, visual, or no-noticeable-difference parity.

Read [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md) before changing this lane.

## Evidence and research

The [RE index](reverse-engineering/RE-INDEX.md) is the technical front door.
Current static authority is the
[2026-07-13 Ghidra closeout](reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md)
and its per-address decision log. Its `6,411/6,411` result closes a defined
metadata/export accounting contract; it does not prove universal semantic
correctness or runtime behavior.

The pinned `references/Onslaught` and `references/AYAResourceExtractor`
submodules are active reference evidence. Their provenance, build, format, test,
and license limits are recorded in the
[reference-submodule audit](reverse-engineering/source-code/reference-submodule-audit-2026-07-12.md).
They do not override observed Steam behavior or establish complete format
support.

## Distribution and limits

The published `v1.0.9` app is an unsigned portable Windows x64 ZIP. It does not
include the retail game, executables, saves, media, extracted assets, full
Ghidra databases, raw proof captures, an installer/MSIX identity, signing,
SmartScreen reputation, or the rebuild.

Current source keeps the same portable layout while generating the Lore pack
from the single canonical `lore/` tree. Publishing a release remains a separate
maintainer action.

## Focused commands

```powershell
npm test                 # WinUI/AppCore/UI plus deterministic rebuild Core
npm run dev              # build current Lore pack and launch the WinUI app
npm run test:safe-copy   # copied-target and patch-catalog contracts
npm run test:docs        # local Markdown links
npm run test:safety      # hard-payload, secret, and submodule boundary
npm run test:rebuild     # broad non-native rebuild contract gate
```

Use `npm run` to see the complete small command surface. The
[public sign-off guide](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md) adds only
the checks relevant to a source or portable-ZIP release.
