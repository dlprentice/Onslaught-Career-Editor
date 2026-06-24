# Lane 09 - Semantics Wording + UI Text Fix Cards

Source findings consumed: `subagents/depth2/lane09_dataflow_semantics_validation.md`.

## Canonical Semantics Anchors (Authoritative)
- `reverse-engineering/binary-analysis/functions/FEPLoadGame.cpp/CFEPLoadGame__DoLoad.md:32`
- `reverse-engineering/binary-analysis/functions/FEPOptions.cpp/CFEPOptions__WriteDefaultOptionsFile.md:36-37`
- `reverse-engineering/binary-analysis/high-impact-call-chain-appendix.md:10-12`
- `reverse-engineering/binary-analysis/functions/Career.cpp/CCareer__Load.md:37-40,49-50`
- `reverse-engineering/save-file/save-format.md:288-295,345,407-435`
- `reverse-engineering/game-assets/game-folder-analysis.md:42-46`

## Card L9-SEM-01 (Critical)
- Title: Make `defaultoptions.bea` load-path overwrite wording conditional and multi-flow accurate.
- Target edits:
  - `AGENTS.md:167`
  - `reverse-engineering/save-file/save-format.md:291`
  - `reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md:35`
  - `BesFilePatcher.cs:1607`
  - `patcher.py:1187`
- Exact replacement wording:
  - `AGENTS.md`
    - `Frontend nuance (Steam build): in CFEPLoadGame__DoLoad (0x00461e20), the game may write defaultoptions.bea from the loaded save buffer via CFEPOptions__WriteDefaultOptionsFile(source, size) when DAT_0082b5b0 == 0. Other save/menu flows can also update defaultoptions.bea, so a patched .bes can still become next-boot global options after load/save + restart.`
  - `reverse-engineering/save-file/save-format.md`
    - `When you load a career save in the frontend (CFEPLoadGame__DoLoad at 0x00461e20), the game may write defaultoptions.bea from the loaded save buffer via CFEPOptions__WriteDefaultOptionsFile(source, size) when DAT_0082b5b0 == 0.`
  - `reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md`
    - `The frontend load path CFEPLoadGame__DoLoad (0x00461e20) calls CCareer::Load(..., flag=1) and may write defaultoptions.bea from the loaded save buffer (load-path condition: DAT_0082b5b0 == 0) via CFEPOptions__WriteDefaultOptionsFile(source, size).`
  - `BesFilePatcher.cs`
    - `CCareer::Load(flag=1) skips applying options entries/tail at runtime; frontend load/save flows may rewrite defaultoptions.bea from loaded/current buffers for the next boot.`
  - `patcher.py`
    - `Frontend load/save flows may rewrite defaultoptions.bea from loaded/current buffers for the next boot (load path is conditional on DAT_0082b5b0 == 0).`
- Authoritative references:
  - `reverse-engineering/binary-analysis/functions/FEPLoadGame.cpp/CFEPLoadGame__DoLoad.md:32`
  - `reverse-engineering/binary-analysis/functions/FEPOptions.cpp/CFEPOptions__WriteDefaultOptionsFile.md:36-37`
  - `reverse-engineering/binary-analysis/high-impact-call-chain-appendix.md:10-12`
- Verification steps:
  1. `rg -n "may write defaultoptions\.bea.*DAT_0082b5b0 == 0|load-path condition: DAT_0082b5b0 == 0" AGENTS.md reverse-engineering/save-file/save-format.md reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md`
  2. `rg -n "frontend load/save flows may rewrite defaultoptions\.bea" BesFilePatcher.cs patcher.py`
  3. `rg -n "the game writes defaultoptions\.bea from the loaded save buffer" AGENTS.md reverse-engineering/save-file/save-format.md reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md` (expected: no remaining unconditional wording in these targets)

## Card L9-SEM-02 (High)
- Title: Expand `CCareer__Load` table summaries to include options entries/tail behavior.
- Target edits:
  - `reverse-engineering/binary-analysis/executable-analysis.md:43`
  - `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md:824`
- Exact replacement wording (both locations):
  - `Deserializes buffer to career (flag=0: boot/defaultoptions path, applies Sound/Music and options entries/tail globals; flag!=0: career .bes load, preserves pre-load Sound/Music and skips options entries/tail apply).`
- Authoritative references:
  - `reverse-engineering/binary-analysis/functions/Career.cpp/CCareer__Load.md:37-40,49-50`
  - `reverse-engineering/save-file/save-format.md:288-290,345`
- Verification steps:
  1. `rg -n "boot/defaultoptions path, applies Sound/Music and options entries/tail globals" reverse-engineering/binary-analysis/executable-analysis.md reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md`
  2. `rg -n "applies options floats, flag!=0 preserves them" reverse-engineering/binary-analysis/executable-analysis.md reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md` (expected: no matches)

## Card L9-SEM-03 (High)
- Title: Remove stale “template-only” framing for `defaultoptions.bea` in roadmap notes.
- Target edits:
  - `lore-book/roadmap/re-investigation.md:173`
  - `lore-book/roadmap/re-investigation.md:245`
- Exact replacement wording:
  - Line 173 phrase replacement: `understand baseline/snapshot and overwrite side effects`
  - Line 245 sentence replacement: `This is a global options baseline/snapshot (same 10,004-byte envelope as .bes), not just a one-time new-save template.`
- Authoritative references:
  - `reverse-engineering/game-assets/game-folder-analysis.md:42-46`
  - `reverse-engineering/save-file/save-format.md:291-295`
- Verification steps:
  1. `rg -n "baseline/snapshot and overwrite side effects|not just a one-time new-save template" lore-book/roadmap/re-investigation.md`
  2. `rg -n "understand template|template used when creating new career saves" lore-book/roadmap/re-investigation.md` (expected: no matches)

## Card L9-UI-01 (Critical)
- Title: Correct Save Editor warning text to reflect sync path and conditional load-write behavior.
- Target edit:
  - `Views/SaveEditorView.xaml:496`
- Exact replacement wording:
  - `Note (Steam build): loading a .bes save preserves current Sound/Music volumes and does not immediately apply options entries/tail (keybinds, mouse sensitivity, screen shape). For deterministic global settings changes, patch defaultoptions.bea directly; alternatively, load/save frontend flows can sync a .bes buffer into defaultoptions.bea for next boot (restart still required).`
- Authoritative references:
  - `reverse-engineering/save-file/save-format.md:288-293`
  - `reverse-engineering/binary-analysis/functions/FEPLoadGame.cpp/CFEPLoadGame__DoLoad.md:32,54`
- Verification steps:
  1. `rg -n "For deterministic global settings changes, patch defaultoptions\.bea directly; alternatively, load/save frontend flows can sync a \.bes buffer into defaultoptions\.bea for next boot" Views/SaveEditorView.xaml`
  2. Manual UI check: launch WPF app, open Save Editor, verify this note appears under `Career Settings Overrides`.

## Card L9-UI-02 (Critical)
- Title: Correct options-copy note to mention restart-after-sync path (not only direct patching).
- Target edit:
  - `Views/SaveEditorView.xaml:723-724`
- Exact replacement wording:
  - `Note (Steam build): defaultoptions.bea is authoritative at boot for keybinds and most global options. If .bes changes do not appear immediately, restart after a load/save flow (which may sync defaultoptions.bea), or patch defaultoptions.bea directly.`
- Authoritative references:
  - `reverse-engineering/save-file/save-format.md:289-295,345`
  - `reverse-engineering/binary-analysis/high-impact-call-chain-appendix.md:10-12`
- Verification steps:
  1. `rg -n "restart after a load/save flow \(which may sync defaultoptions\.bea\), or patch defaultoptions\.bea directly" Views/SaveEditorView.xaml`
  2. Manual UI check: confirm note under options copy controls in Save Editor.

## Card L9-UI-03 (High)
- Title: Align PyQt note text with `.bes` non-immediate apply semantics and sync path.
- Target edit:
  - `onslaught/gui/tabs/save_editor.py:344-345`
- Exact replacement wording:
  - `Note: Steam build loads these options from defaultoptions.bea at boot. Copying into a .bes save does not apply immediately; next-boot behavior can come from load/save sync into defaultoptions.bea or direct defaultoptions patching.`
- Authoritative references:
  - `reverse-engineering/save-file/save-format.md:289-295,345`
  - `reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md:33-36`
- Verification steps:
  1. `rg -n "does not apply immediately; next-boot behavior can come from load/save sync into defaultoptions\.bea" onslaught/gui/tabs/save_editor.py`
  2. Manual UI check: run PyQt app and confirm hint text in options copy area.

## Card L9-UI-04 (Medium)
- Title: Make WPF status tip accurate without over-prescribing direct patch-only workflow.
- Target edit:
  - `Views/SaveEditorView.xaml.cs:1175`
- Exact replacement wording:
  - `Tip: global keybinds apply at boot from defaultoptions.bea; load/save flows may sync it from .bes for next boot.`
- Authoritative references:
  - `reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md:35-36`
  - `reverse-engineering/binary-analysis/high-impact-call-chain-appendix.md:10-12`
- Verification steps:
  1. `rg -n "global keybinds apply at boot from defaultoptions\.bea; load/save flows may sync it from \.bes for next boot" Views/SaveEditorView.xaml.cs`
  2. Manual UI check: use keybind-load action and confirm status text includes updated tip.

## Card L9-SEM-04 (Medium)
- Title: Update capabilities wording for options-tail mapping maturity.
- Target edit:
  - `CURRENT_CAPABILITIES.md:64`
- Exact replacement wording:
  - `Tail snapshot mapping is largely documented (0x56 bytes; input/render/audio globals mapped at tail-relative offsets), with remaining unknown/reserved fields explicitly preserved.`
- Authoritative references:
  - `reverse-engineering/save-file/save-format.md:407-435`
- Verification steps:
  1. `rg -n "Tail snapshot mapping is largely documented" CURRENT_CAPABILITIES.md`
  2. `rg -n "Partial identification of some tail snapshot globals" CURRENT_CAPABILITIES.md` (expected: no matches)

## End-to-End Semantic Verification (After Applying Cards)
1. Static consistency check:
   - `rg -n "DAT_0082b5b0 == 0|may write defaultoptions\.bea|load/save flows" AGENTS.md reverse-engineering/save-file/save-format.md reverse-engineering/binary-analysis/functions/Controller.cpp/ControlBindings.md BesFilePatcher.cs patcher.py Views/SaveEditorView.xaml Views/SaveEditorView.xaml.cs onslaught/gui/tabs/save_editor.py`
2. Behavior check (manual game flow):
   - Patch `.bes` options entries/tail only.
   - Load that save (no restart), verify keybind/tail globals are not guaranteed to apply immediately.
   - Trigger a load/save menu flow, restart game, verify next-boot behavior reflects `defaultoptions.bea` sync path.
3. Tail-mapping doc check:
   - Confirm `CURRENT_CAPABILITIES.md` wording matches mapped-tail table in `reverse-engineering/save-file/save-format.md:407-435`.
