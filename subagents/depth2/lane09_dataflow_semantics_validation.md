# Lane 09 - Dataflow/Semantics Validation (.bes vs .bea + Options Tail)

## Scope and canonical baseline
Validated wording against:
- `reverse-engineering/save-file/save-format.md:288-295,345,407-435`
- `reverse-engineering/binary-analysis/functions/FEPLoadGame.cpp/CFEPLoadGame__DoLoad.md:32`
- `reverse-engineering/binary-analysis/functions/FEPOptions.cpp/CFEPOptions__WriteDefaultOptionsFile.md:36-37`
- `reverse-engineering/binary-analysis/high-impact-call-chain-appendix.md:10`
- `reverse-engineering/game-assets/game-folder-analysis.md:42-46`

## Contradictions and exact wording fixes

### 1) Load-game write to `defaultoptions.bea` is stated as unconditional in multiple places

Canonical behavior: load path write is conditional (`DAT_0082b5b0 == 0`) and other save/menu flows can also write `defaultoptions.bea`.

- Contradicting wording:
  - `AGENTS.md:167`
  - `reverse-engineering/save-file/save-format.md:291`
  - `reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md:35`
  - `BesFilePatcher.cs:1607`
  - `patcher.py:1187`

Exact wording fixes:
- `AGENTS.md:167` replace with:
  - `Frontend nuance (Steam build): in CFEPLoadGame__DoLoad (0x00461e20), the game may write defaultoptions.bea from the loaded save buffer via CFEPOptions__WriteDefaultOptionsFile(source, size) when DAT_0082b5b0 == 0. Other save/menu flows can also update defaultoptions.bea, so a patched .bes can still become next-boot global options after load/save + restart.`
- `reverse-engineering/save-file/save-format.md:291` replace with:
  - `When you load a career save in the frontend (CFEPLoadGame__DoLoad at 0x00461e20), the game may write defaultoptions.bea from the loaded save buffer via CFEPOptions__WriteDefaultOptionsFile(source, size) when DAT_0082b5b0 == 0.`
- `reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md:35` replace with:
  - `The frontend load path CFEPLoadGame__DoLoad (0x00461e20) calls CCareer::Load(..., flag=1) and may write defaultoptions.bea from the loaded save buffer (load-path condition: DAT_0082b5b0 == 0) via CFEPOptions__WriteDefaultOptionsFile(source, size).`
- `BesFilePatcher.cs:1607` replace with:
  - `        CCareer::Load(flag=1) skips applying options entries/tail at runtime; frontend load/save flows may rewrite defaultoptions.bea from loaded/current buffers for the next boot.`
- `patcher.py:1187` replace with:
  - `        Frontend load/save flows may rewrite defaultoptions.bea from loaded/current buffers for the next boot (load path is conditional on DAT_0082b5b0 == 0).`

### 2) `CCareer__Load` summaries are too narrow and miss options entries/tail semantics

Canonical behavior: `flag=0` applies sound/music and applies options entries + tail; `flag!=0` preserves pre-load sound/music and skips entries/tail apply.

- Contradicting wording:
  - `reverse-engineering/binary-analysis/executable-analysis.md:43`
  - `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md:824`

Exact wording fix (both locations):
- Replace description with:
  - `Deserializes buffer to career (`flag=0`: boot/defaultoptions path, applies Sound/Music and options entries/tail globals; `flag!=0`: career .bes load, preserves pre-load Sound/Music and skips options entries/tail apply).`

### 3) Roadmap text still describes `defaultoptions.bea` as a “template”

Canonical behavior: it is a global options baseline/snapshot with runtime overwrite side effects, not only a one-time template.

- Contradicting wording:
  - `lore-book/roadmap/re-investigation.md:173` (`understand template`)
  - `lore-book/roadmap/re-investigation.md:245` (`This is the template used when creating new career saves.`)

Exact wording fixes:
- `lore-book/roadmap/re-investigation.md:173` replace `understand template` with:
  - `understand baseline/snapshot and overwrite side effects`
- `lore-book/roadmap/re-investigation.md:245` replace with:
  - `This is a global options baseline/snapshot (same 10,004-byte envelope as .bes), not just a one-time new-save template.`

### 4) UI/app copy over-prescribes “patch defaultoptions.bea” without noting load/save sync path

Canonical behavior: direct `.bes` load does not apply entries/tail immediately, but frontend flows may sync to `defaultoptions.bea` for next boot.

- Wording needing correction:
  - `Views/SaveEditorView.xaml:496`
  - `Views/SaveEditorView.xaml:723-724`
  - `onslaught/gui/tabs/save_editor.py:344-345`
  - `Views/SaveEditorView.xaml.cs:1175`

Exact wording fixes:
- `Views/SaveEditorView.xaml:496` replace sentence after `...does not immediately apply options entries/tail...` with:
  - `For deterministic global settings changes, patch defaultoptions.bea directly; alternatively, load/save frontend flows can sync a .bes buffer into defaultoptions.bea for next boot (restart still required).`
- `Views/SaveEditorView.xaml:723-724` replace with:
  - `Note (Steam build): defaultoptions.bea is authoritative at boot for keybinds and most global options. If .bes changes do not appear immediately, restart after a load/save flow (which may sync defaultoptions.bea), or patch defaultoptions.bea directly.`
- `onslaught/gui/tabs/save_editor.py:344-345` replace with:
  - `Note: Steam build loads these options from defaultoptions.bea at boot. Copying into a .bes save does not apply immediately; next-boot behavior can come from load/save sync into defaultoptions.bea or direct defaultoptions patching.`
- `Views/SaveEditorView.xaml.cs:1175` replace with:
  - `Tip: global keybinds apply at boot from defaultoptions.bea; load/save flows may sync it from .bes for next boot.`

### 5) Options-tail status wording is stale vs current mapped-tail docs

Canonical tail semantics now document offset mapping across the full 0x56 block (`save-format.md:407-435`), with limited remaining uncertainty.

- Stale wording:
  - `CURRENT_CAPABILITIES.md:64` (`Partial identification of some tail snapshot globals...`)

Exact wording fix:
- Replace with:
  - `Tail snapshot mapping is largely documented (0x56 bytes; input/render/audio globals mapped at tail-relative offsets), with remaining unknown/reserved fields explicitly preserved.`
