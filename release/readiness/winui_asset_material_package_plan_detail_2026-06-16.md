# WinUI Asset Material Package Plan Detail Readiness Note

Status: local WinUI/AppCore product proof
Date: 2026-06-16
Scope: active WinUI Asset Library selected-model detail panel

This slice surfaces the material package plan at the selected model row in the active WinUI Asset Library. The model facts panel now shows package readiness, package-relative model destination, resolved texture-reference counts, and sample package-relative texture destinations for loose and embedded model exports.

Validation:

- `dotnet build OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo`: PASS.
- `dotnet test OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "Name=AssetLibrary_CyclesRepresentativeRealRowsWhenCatalogProvided"` with `ONSLAUGHT_WINUI_REAL_ASSET_CATALOG=subagents\texture_mesh_asset_bridge_proof_2026-06-08\asset_catalog\catalog.json`: PASS, `1` test, `0` skipped.

What the UIA proof asserts:

- Representative loose and embedded model rows still expose metadata, wireframe availability, direct catalog texture links, and sidecar summary text.
- The selected model detail now includes `Material package plan: ready`.
- The selected model detail includes `model destination models/`.
- The selected model detail includes resolved texture-reference text and package-relative `textures/catalog/` destinations.

Boundary:

- The private copied-corpus catalog and extracted assets stayed under ignored `subagents/`.
- No asset bytes were copied into a new package.
- No real importer was executed.
- No installed game files or original `BEA.exe` bytes were mutated.
- No private asset payloads are committed.
- This proves selected-row WinUI visibility of deterministic package-relative planning only.
- This is not Godot work, native textured rendering, animation, runtime model-viewer behavior, gameplay proof, rebuild parity, or no-noticeable-difference parity.
