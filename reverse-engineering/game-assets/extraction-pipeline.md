# Guarded asset extraction pipeline

Status: active local analysis path

The public repository contains parsers and exporters, not Battle Engine Aquila
asset archives. Tools read a retail installation and write derived files to a
separate ignored workspace. The project has permission to use, modify, and
distribute original game assets, but bulk extraction remains local; only a
curated, attributed asset set consumed by an active product/rebuild slice should
enter source or packaging.

## Supported flow

1. Choose a real retail installation as read-only input.
2. Inventory AYA archives with `tools/aya_archive_inventory.py` when archive
   structure is the question.
3. Export only the needed local texture/mesh/catalog slice with
   `tools/export_game_assets.py` or a more focused exporter listed in
   [`tools/README.md`](../../tools/README.md).
4. Write to an explicit ignored root such as `local-lab/asset-export/`; never
   write into the game installation or a tracked repository directory.
5. Open the generated catalog in the WinUI Asset Library for local inspection.
   Preview metadata and wireframes are inspection aids, not final retail
   rendering.

Python exporters publish through guarded output handling: the destination must
be separate from tracked source and retail input, pre-existing unsafe content
is rejected, and output is replaced only after a complete staging pass. The C#
asset services use package-relative paths and keep private absolute source paths
out of generated metadata.

## Format and provenance boundaries

- The pinned AYA extractor is a reference implementation and bridge, not proof
  of complete Steam-format support.
- Exported FBX, PNG, model summaries, material slots, UV/normal metadata, and
  catalog links describe the files the selected tools could read. They do not
  prove animation, skinning, texture assignment, lighting, collision, or visual
  fidelity in the retail engine or rebuild.
- Goodies links combine catalog, save-state, and source/static evidence. They
  do not permanently award Goodies, edit the source save, or prove every
  in-game viewer state.
- Counts from a local installation are observations, not durable
  repository truth. The generated catalog is the owner for that run; this page
  does not mirror its inventory.

## Focused verification

```powershell
npm run test:tools
```

The command exercises the retained AYA inventory/export parser contracts and
the guarded copied-runtime helper tests. For a change to one exporter, run its
matching focused test directly instead of treating the combined command as a
release checklist.

## Source boundary

Do not track retail archives, copied executables, saves, raw machine-local
catalogs, debugger logs, screenshots, or generated extraction trees. A selected
original asset may be tracked or released only when it has a current consumer,
clear provenance and attribution, and no conflicting third-party term.
