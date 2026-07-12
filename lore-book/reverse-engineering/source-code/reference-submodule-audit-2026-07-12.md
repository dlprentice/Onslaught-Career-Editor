# Reference Submodule Audit - 2026-07-12

Status: current pinned-submodule inventory; not a build-complete or license-approval claim

## Purpose

This audit defines what the two reference submodules can and cannot establish.
Both are useful inputs to reverse engineering, but neither is the released Steam
program and neither is allowed to override Steam binary or runtime evidence.

## Pinned Revisions

| Corpus | Tracked remote | Pinned commit | Upstream baseline in fork history |
| --- | --- | --- | --- |
| Onslaught source | `https://github.com/dlprentice/Onslaught.git` | `792545b996365f383781c666d145ea6cbda83f3a` | Stuart repository commit `5352a81cdb838b145a57f7febc5d9fc4b0129ebb` |
| AYAResourceExtractor | `https://github.com/dlprentice/AYAResourceExtractor.git` | `6f3df296201ecc62bc09c39f7a93d8a4fb2f1638` | Stuart repository commit `4e04952a200e29040a68fc8648e835f9a7d608d1` |

The Onslaught fork differs from that upstream baseline only in tracked Git
attributes/ignore files. The AYA fork also contains the local DDS wrapper copy-
bounds correction. These facts were checked from commit ancestry and diffs, not
inferred from repository names.

## Onslaught Source

| Area | Current finding |
| --- | --- |
| Inventory | 110 Git-tracked files: 52 `.cpp`, 54 `.h`, and 4 repository/support files. The older 111-file manifest counted the submodule worktree's `.git` control file as source inventory. |
| Build posture | No solution, project, make, or build-system file is present. Across tracked C/C++ files, 254 distinct quoted include targets are referenced and 202 are absent from the supplied tree using case-insensitive path/basename matching. This is an incomplete architecture corpus, not a buildable game checkout. |
| Behavioral use | Class ownership, subsystem relationships, candidate method names, and source-order logic are useful hypotheses. Steam `BEA.exe` static evidence and copied-runtime observation decide released behavior. |
| License posture | A root GPLv3 text is present. Four Direct3D-derived files also carry Microsoft copyright notices. The root license must not be treated as erasing file-level notices. |
| Tests | No source-project build or test suite exists in the pinned tree. Repository-side crosswalk checks can test our interpretation, not compile or certify the missing program. |

## AYAResourceExtractor

| Area | Current finding |
| --- | --- |
| Inventory | 74 Git-tracked files, including 24 C# files, 30 C/C++ files, four `.csproj`, three `.vcxproj`, one solution, and the tracked `BoxWithTextures.fbx` template. The older 75-file manifest likewise counted the submodule `.git` control file. |
| Build posture | Windows/Visual Studio 2022, v143 C++/CLI, Windows SDK, .NET 6 Windows, and Win32/x86 are required. The repo harness is .NET 10/x86 but reflection-loads the legacy `AYAResourceExtractor.dll`, `DDSTextureUncompress.dll`, and `Fbx.dll`. A fresh solution build on this workstation fails with `MSB4278` because `Microsoft.Cpp.Default.props` / `VCTargetsPath` is unavailable; the C# FBX project builds, but this is not a reproducible native extractor build. |
| Supported lane | PC model `.aya` decompression, static mesh parsing, texture lookup/decompression, PNG output, and ASCII/binary FBX output. |
| Known format gaps | The upstream README disclaims full model coverage, flags some wrong normals, no single-primitive multitexture blending, static single-object output, and no animation or bone export. Current corpus counts prove breadth only; they do not prove semantic fidelity or format completeness. |
| Reproducibility gap | `export_game_assets.py` preflights the AYA and DDS assemblies, while the harness also requires `Fbx.dll` and the FBX template. No tracked public fixture currently drives a synthetic AYA/model/texture payload through the complete legacy importer, DDS decoder, and FBX writer contract. |
| License posture | The root MIT text still contains `[year] [fullname]`. Bundled code has separate zlib notices and DDSReader GPL3/FreeImage-derived notices; the FBX code/template provenance is described in README but lacks a complete component notice in this pin. This is an unresolved redistribution review item, not a finding that local use is blocked. |

## Evidence Hierarchy

1. Stuart source suggests architecture, ownership, vocabulary, and candidate logic.
2. Steam binary static evidence establishes released code identity and structure.
3. Copied-runtime observation establishes actual released behavior and measured values.
4. Synthetic and authorized local exporter fixtures establish concrete format support.
5. The rebuild consumes an accepted contract; its own output cannot prove retail truth.

## Reproduction

Run from the repository root:

```powershell
git submodule status
git -C references\Onslaught rev-parse HEAD
git -C references\Onslaught ls-files
git -C references\AYAResourceExtractor rev-parse HEAD
git -C references\AYAResourceExtractor ls-files
```

The quoted-include result is obtained by scanning directives matching
`^\s*#\s*include\s*"..."` in the tracked Onslaught `.cpp`/`.h` set and
resolving each target case-insensitively against both its normalized relative
path and basename. Allowing whitespace between `#` and `include` is required
to include `# include "ltshell.h"` in `DX.H`.

## Next Improvement

The smallest useful exporter advancement is a generated, public-safe export-
contract self-test that exercises parsing, DDS-to-PNG conversion, FBX creation,
and dependency preflight without retail assets. It should be designed before
implementation and must not convert private corpus success into a completeness
claim.
