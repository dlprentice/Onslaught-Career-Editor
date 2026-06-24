# WinUI Patch Target Safety Wave Readiness Note

Status: validated local product/tooling safety wave
Date: 2026-06-16

Scope: WinUI/AppCore executable patch lane safety and mod/proof accounting.

This wave moves the existing Patch Bench safety rule from UI-only enforcement into AppCore mutation APIs. `BinaryPatchEngine.ApplyPatchesToFile` and `BinaryPatchEngine.RestoreFromBackup` now require `BinaryPatchTargetOptions` with an app-owned allowed root. Product apply refuses fallback catalog rows, requires `BEA.exe`, keeps backups inside the allowed root, and accepts copied executables only when the specimen is either the known clean Steam retail SHA-256 or an explicit byte-layout-only copied-target operation.

Tracked outcomes:

| Area | Result |
| --- | --- |
| Catalog identity | `patches/catalog/patches.v2.json` rows carry SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` and size `2506752`. |
| Product packaging | WinUI copies `patches/catalog/patches.v2.json` into the app output. |
| Mutation boundary | AppCore apply/restore require app-owned Patch Bench root and reject outside-root targets. |
| Existing UX | Patch Bench remains copy-first; installed/original `BEA.exe` stays read-only source material. |
| Measurement | New `roadmap/mod-patch-runtime-rebuild-register.md` separates patch/mod/runtime/rebuild proof counters from static RE counters. |

Validation run:

- `dotnet test OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~BinaryPatchRegressionTests|FullyQualifiedName~WinUiProductLaneTests|FullyQualifiedName~WinUiAccessibilityAuditTests"` - passed, 36/36.
- `dotnet build OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo` - passed, 0 warnings, 0 errors.
- Built output contains `OnslaughtCareerEditor.WinUI\bin\Debug\net10.0-windows10.0.19041.0\win-x64\patches\catalog\patches.v2.json`.

Not claimed:

- No runtime launch/capture proof.
- No music/color/resource mod proof.
- No installed-game mutation.
- No Godot or clean-room rebuild demo.
- No netcode work.
