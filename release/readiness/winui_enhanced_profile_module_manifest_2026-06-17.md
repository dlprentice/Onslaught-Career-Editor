# WinUI Enhanced Profile Module Manifest Readiness Note

Status: validated local contract and UI wiring
Date: 2026-06-17

Scope: make the `Enhanced Profile Preview` safe-copy profile auditable as a module manifest instead of an opaque mega patch.

Tracked outcomes:

| Area | Result |
| --- | --- |
| Profile contract | `SafeCopyProfilePreset` now carries explicit `SafeCopyProfileModule` rows with module id, display name, category, proof status, claim boundary, patch keys, launch arguments, and copied-options edits. |
| Enhanced modules | The current `Enhanced Profile Preview` records six modules: `windowed-compatibility`, `graphics-defaults`, `title-marker`, `frontend-red-margins`, `goodies-display-preview`, and `copied-options-control-defaults`. |
| Generated manifest | The generated safe-copy manifest writes those module rows under `profilePreset.modules` when the enhanced profile is prepared. |
| UI boundary | Patch Bench now states the current Enhanced modules, the accepted bounded combined safe-copy proof class, and that experimental camera/fullscreen rows, netcode, in-game toggle menus, and improved-control-feel claims are not included. |
| Future use | This is the foundation for future one-click enhanced/profile work: new modules can join only after they have proof, conflicts/dependencies, restore semantics, and bounded claims. |

Not claimed:

- No new executable patch row.
- The later 2026-06-18 follow-up added bounded combined safe-copy launch/capture/source-safety, red frontend-margin, and copied control-default materialization proof for the current module set. This note still does not claim gameplay, broad menu/theme coverage, online mode, or parity.
- No online multiplayer, netcode, in-game toggle menu, or monolithic mega patch.
- No improved-control-feel proof. The copied control defaults module records manifest/read-back scope only.
- No installed-game or original executable mutation.
- No Ghidra mutation.

Validation:

- `npm run test:winui-enhanced-profile-module-manifest`: PASS.
- `npm run test:winui-safe-copy-runtime`: PASS, 50 AppCore tests, 3 WinUI tests, control-options artifact checker, control-feel matrix checker, and live-runtime helper self-tests.
- `dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo`: PASS, 0 warnings, 0 errors.
- `python tools\docsync_check.py`: PASS.
- `npm run test:doc-commands`: PASS, 3925 documented command references checked.
- `npm run test:md-links`: PASS.
- `python tools\release_profile_snapshot.py --check`: PASS, R0=6082 R2=0 R3=2 R4=18397.
- `python tools\release_curated_manifest.py --check`: PASS, selected/public allowlist 4896.
- `npm run test:public-allowlist`: PASS, 4896 rows checked.
- `npm run test:repo-hygiene`: PASS, explicit text files checked 19008.
- `git diff --check`: PASS.

Current module list:

| Module | Payload | Boundary |
| --- | --- | --- |
| `windowed-compatibility` | `resolution_gate`, `force_windowed` | Compatibility baseline; no aspect-ratio gameplay parity claim. |
| `graphics-defaults` | `extra_graphics_default_on`, `ignore_cardid_tweak_overrides` | Launch-proofed rows; no rendering-quality parity claim. |
| `title-marker` | `version_overlay_use_patched_format_pointer` plus hidden dependency during patch resolution | One title/menu marker proof; not every overlay/gameplay path. |
| `frontend-red-margins` | `frontend_clear_screen_dark_red` | One title-screen margin proof; no whole-menu/HUD/gameplay color claim. |
| `goodies-display-preview` | `goodies_gallery_display_unlock` | Bounded Goodies-wall display proof; no permanent unlock/model/FMV/every-entry claim. |
| `copied-options-control-defaults` | copied `defaultoptions.bea` edits: `controllerConfiguration=1`, `mouseLookSensitivity=2.25` | Manifest/read-back only; no improved control feel, deadzone, camera, or movement proof. |
