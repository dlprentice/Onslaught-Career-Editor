# Guarded asset extraction pipeline

Status: local user-supplied inputs only

The public repository contains parsers and exporters, not Battle Engine Aquila
assets. A user may point the tools at their own retail installation and write
derived files to a separate ignored workspace. Neither source assets nor
exports may be committed or packaged with the toolkit or rebuild.

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
out of generated public-safe metadata. Materialization commands that copy
derived files require their explicit arm phrase; read-only inspection and
preflight do not.

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
- Counts from a private installation are local observations, not durable
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

## Prohibited outputs

Do not track or release retail archives, extracted textures/models/audio/video,
copied executables, saves, raw catalog payloads from a private installation,
debugger logs, screenshots, or generated material packages. Public examples
must be synthetic or one of the narrowly reviewed repository fixtures.
