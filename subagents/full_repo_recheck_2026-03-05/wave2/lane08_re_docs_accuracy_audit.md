# Lane 08 - Reverse-Engineering Docs Accuracy Audit

Scope: canonical `reverse-engineering/` docs relevant to save/options/binary patch behavior, checked against current code in `BesFilePatcher.cs`, `patcher.py`, `BinaryPatchEngine.cs`, `onslaught/core/binary_patches.py`, and `patches/catalog/patches.v2.json`.

## Overall

Core save/options docs are mostly aligned with the current implementations. The main retail facts still match live code:
- true-dword/file+2 model
- fixed 10,004-byte Steam envelope
- `defaultoptions.bea` boot/global semantics
- kill-counter top-byte preservation
- 233 retail-displayable goodies (`0..232`)

Actionable drift found: 5 items.

## Findings

1. High - `CLIParams.cpp/_index.md` still states the retail `-forcewindowed` guard default is `0x00`, which conflicts with the current canonical Steam-hash docs.
- Doc: `reverse-engineering/binary-analysis/functions/CLIParams.cpp/_index.md:45`
- Conflicting canonical RE docs: `reverse-engineering/binary-analysis/windowed-mode-analysis.md:11`, `reverse-engineering/binary-analysis/windowed-mode-analysis.md:37`, `reverse-engineering/binary-analysis/windowed-mode-analysis.md:108`
- Current patch surface: `BinaryPatchEngine.cs:44`, `patches/catalog/patches.v2.json:34`
- Why it is wrong: the CLIParams page says "Retail default is 0x00" and frames guard-byte normalization as the retail baseline, but the canonical current-Steam docs already record the repo's target Steam hash as `0x01` at `DAT_00662f3e`; the live patch surface also treats startup-flow patches as the main supported path, not a default-0x00 assumption.
- Recommended fix: rewrite the CLIParams note to match the current canonical wording: current Steam hash observed at `0x01`, historical variants may show `0x00`.

2. High - `windowed-mode-analysis.md` still treats `0x12BB97` as part of the stable recommendation, but the shipped catalog/engines mark it as experimental.
- Doc: `reverse-engineering/binary-analysis/windowed-mode-analysis.md:145`
- Current catalog/code: `patches/catalog/patches.v2.json:163`, `BinaryPatchEngine.cs:87`, `onslaught/core/binary_patches.py:92`
- Why it is wrong: the doc says the recommended "Binary Patches stable set" includes `0x12BB97`, but the catalog labels `skip_auto_toggle` as `track: experimental` and `optional: true`; both C# and Python engines surface it that way.
- Recommended fix: make the conclusion say `0x12A644` is the stable startup patch, with `0x12BB97` explicitly experimental/opt-in only.

3. Medium - `binary-analysis/README.md` overstates scope by saying analysis is based only on unmodified `BEA.exe` and that `BEA_Widescreen.exe` is not used for analysis, while canonical docs in the same folder analyze the widescreen executable diff directly.
- Doc: `reverse-engineering/binary-analysis/README.md:11`, `reverse-engineering/binary-analysis/README.md:24`
- Conflicting canonical RE docs: `reverse-engineering/binary-analysis/_index.md:19`, `reverse-engineering/binary-analysis/widescreen-patch-analysis.md:11`, `reverse-engineering/binary-analysis/widescreen-patch-analysis.md:13`
- Why it is wrong: much of the folder does target the unmodified Steam binary, but the canonical widescreen attribution pages explicitly analyze `BEA_Widescreen.exe` against `BEA.exe`. The README's current wording is too absolute.
- Recommended fix: narrow the README claim to say base-address/hash analysis targets the unmodified Steam executable, while dedicated diff docs also cover `BEA_Widescreen.exe` as a comparison target.

4. Medium - `functions/display-settings.md` still says the actual Video Options controller is "still being traced", but the frontend options-controller surface is already mapped in the current RE corpus.
- Doc: `reverse-engineering/binary-analysis/functions/display-settings.md:147`
- Conflicting canonical RE docs: `reverse-engineering/binary-analysis/functions/FEPOptions.cpp/_index.md:24`, `reverse-engineering/binary-analysis/functions/FEPOptions.cpp/_index.md:28`, `reverse-engineering/binary-analysis/functions/FEPOptions.cpp/_index.md:30`, `reverse-engineering/binary-analysis/functions/FEPOptions.cpp/_index.md:89`
- Why it is wrong: the function index already names `CFEPOptions__ProcessInput`, `CFEPOptions__Update`, `CFEPOptions__SaveDefaultOptions`, `CFEPOptions__WriteDefaultOptionsFile`, and `CFEPOptions__EnsureOptionsContext`, so the options handler/controller surface is no longer "still being traced" at that level.
- Recommended fix: update `display-settings.md` to point at the mapped `CFEPOptions__*` controller path and scope any remaining uncertainty narrowly to specific sub-actions.

5. Medium - `god-mode.md` frames `0x00662ab4` as a separate runtime global from the persisted `g_bGodModeEnabled` field, but the current canonical reference maps it as the in-memory location of the same `CAREER + 0x2494` slot.
- Doc: `reverse-engineering/game-mechanics/god-mode.md:24`, `reverse-engineering/game-mechanics/god-mode.md:35`
- Conflicting canonical RE docs: `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md:698`, `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md:702`, `reverse-engineering/binary-analysis/GHIDRA-REFERENCE.md:2181`
- Current code model: `BesFilePatcher.cs:194`, `patcher.py:1333`
- Why it is wrong: the GHIDRA reference identifies `0x00662ab4` as `CAREER + 0x2494` (file `0x2496`), not a separate storage location. The current wording invites readers to think there are two different god-mode booleans when the canonical RE map points to one persisted CCareer field viewed on disk vs in memory.
- Recommended fix: reword the note to distinguish on-disk offset vs in-memory address for the same field, not "persisted field vs separate runtime global".

## Confirmed Aligned (No Accuracy Issue Found)

- `reverse-engineering/save-file/save-format.md:138` remains aligned with `BesFilePatcher.cs:188` and `patcher.py:83` on file size, fixed-region offsets, and the true-dword/file+2 model.
- `reverse-engineering/save-file/save-format.md:286`, `reverse-engineering/save-file/_index.md:47`, `reverse-engineering/save-file/struct-layouts.md:42` remain aligned with `BesFilePatcher.cs:259`, `BesFilePatcher.cs:286`, and `patcher.py:1157` on `.bea` boot/global semantics versus `.bes` load semantics.
- `reverse-engineering/save-file/kill-tracking.md:57` remains aligned with `BesFilePatcher.cs:222` and `patcher.py:702` on lower-24-bit kill payloads and conservative top-byte preservation.
- `reverse-engineering/binary-analysis/extra-graphics-feature-gate-patch.md:13` remains aligned with stable catalog entries `extra_graphics_default_on` and `ignore_cardid_tweak_overrides` in `patches/catalog/patches.v2.json:61` and `patches/catalog/patches.v2.json:87`.
