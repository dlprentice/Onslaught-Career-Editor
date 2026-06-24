# Legacy Python App

Status: archived legacy reference
Last updated: 2026-05-04

This folder contains the archived Python GUI/CLI parity implementation. It was
once intended to track the WPF/WinUI application visually and from the command
line, but that parity lane proved too costly to maintain and is no longer an
active product or CLI lane.

Current replacement lanes:

- `OnslaughtCareerEditor.WinUI` for the primary user-facing Windows product
- `OnslaughtCareerEditor.AppCore` for shared correctness/core behavior
- `OnslaughtCareerEditor.Cli` for supported C# automation
- `tools/` for active Python utility/lab scripts
- `archive/electron-workbench/` only as archived Electron/TypeScript reference material

Temporary parity/reference surfaces:

- `OnslaughtCareerEditor.AppCore`
- `OnslaughtCareerEditor.AppCore.Host`
- `OnslaughtCareerEditor.Cli`

What is still valid:

- historical behavior and UI/reference material
- algorithm and regression-test ideas that should be ported deliberately before use
- optional script reference when an active `tools/` utility needs a verified idea

What is not valid:

- this is not the active Python tooling lane
- this is not an active parity target
- this is not part of the curated public/community surface
- Python app smoke/tests are no longer part of the active release gate
- do not revive this GUI/CLI without an explicit product-strategy decision
