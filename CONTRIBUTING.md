# Contributing

Onslaught Toolkit accepts focused changes to the WinUI product, shared
AppCore/CLI behavior, deterministic rebuild, and evidence-backed preservation
material. Git history is the archive: do not add mirrors, wave bookkeeping,
generated inventories, handoff files, or replacement process machinery.

## Start here

1. Read [`AGENTS.md`](AGENTS.md), [`README.MD`](README.MD), and only the owning
   README or evidence files for your change.
2. Confirm the branch, upstream, dirty state, and submodule pins before editing.
3. Preserve unrelated work and keep `references/Onslaught` pinned unless a
   separately authorized source-reference update requires otherwise.
4. Make the smallest coherent change that fixes a current product, contract,
   evidence, or contributor problem.
5. Run the smallest check capable of falsifying that change.

No game installation is required to build or test ordinary source changes.

```powershell
npm test
npm run dev
```

Root [`package.json`](package.json) is the command authority. Do not duplicate
its command list in new documents.

## Ownership

- WinUI owns navigation, interaction, accessibility, and presentation.
- AppCore owns save/options preservation, copied-target safety, patch planning,
  media/catalog parsing, and other shared correctness.
- The C# CLI adapts AppCore behavior; it should not fork file-format rules.
- `OnslaughtRebuild.Core` owns deterministic simulation truth and remains free
  of presentation, filesystem, clock, process, network, and GPU APIs.
- `lore/` is the canonical public lore/history source.
- `reverse-engineering/` retains unique, provenance-bounded evidence. Static,
  runtime, source-reference, and reconstruction claims must remain distinct.

## Product changes

Keep primary workflows understandable without lab knowledge. Use clear action
labels, explicit target paths, visible success/error state, keyboard focus,
accessible names, and sufficient contrast. Mutating actions must state whether
they write a selected file, a copy, or an app-owned profile.

Do not expose Host/Join as available, represent a generated catalog as bundled
game content, claim reconstruction parity, or turn research controls into a
normal-user promise without corresponding proven behavior.

## Files and retail inputs

Never commit retail binaries, arbitrary saves, copied executables, full Ghidra
stores/backups, debugger logs, private captures, credentials, or `.env*` files.
Use the ignored locations described in [`LOCAL_LAB_OVERLAY.md`](LOCAL_LAB_OVERLAY.md)
for bulk extraction and experiments. The project has permission to use, modify,
and distribute original game assets, but a contribution should add only the
curated inputs a current product or rebuild path consumes, with credits,
provenance, and third-party terms intact.

Save edits must start from a real baseline and preserve unknown bytes. Retail
executable mutation must target a verified copy, never an installed game
directory. Exporters must require explicit local inputs and a separate local
output root.

## Reverse engineering and rebuild

Use [`reverse-engineering/RE-INDEX.md`](reverse-engineering/RE-INDEX.md) to find
the canonical evidence owner. Retain raw or bulky proof locally; commit only the
smallest public-safe evidence needed to support a current contract. Cite the
evidence class and state what it does not prove.

Before changing `rebuild/`, read [`rebuild/PROVENANCE.md`](rebuild/PROVENANCE.md)
and [`rebuild/README.md`](rebuild/README.md). GPL-compatible source adaptation
and authorized original assets are permitted; retail executable/decompiler text
and separately licensed third-party material are not.

## Validation

Use [`VALIDATION.md`](VALIDATION.md) to choose checks. Typical focused commands
are:

```powershell
npm run test:appcore
npm run test:ui
npm run test:safe-copy
npm run test:docs
npm run test:safety
npm run test:rebuild-core
```

Launch the real app after changing a primary WinUI workflow. Use the native
Godot smoke only when the engine setup, rendering, input, launch, or clean-exit
path changed. Do not run the root aggregate merely for ceremony.

Release preparation is separate from publication. Follow
[`README.RELEASE.md`](README.RELEASE.md) and
[`release/readiness/PUBLIC_SIGNOFF_COMMANDS.md`](release/readiness/PUBLIC_SIGNOFF_COMMANDS.md)
only when release boundaries or candidate inputs changed.
