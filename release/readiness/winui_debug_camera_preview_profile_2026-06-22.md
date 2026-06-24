# WinUI Debug Camera Preview Profile Readiness Note

Status: product-surface profile contract validated
Date: 2026-06-22
Scope: `debug-camera-preview` safe-copy profile

This slice adds a selectable WinUI/AppCore safe-copy profile for an existing bounded free-camera path. It does not add new executable bytes or new runtime proof. It groups already cataloged rows into an explicit experimental preset so a user can prepare a safe copied game folder with the minimum windowed/debug-camera preview row set.

## Profile Shape

| Field | Value |
| --- | --- |
| Profile id | `debug-camera-preview` |
| Display name | `Debug Camera Preview` |
| Visible selected rows | `resolution_gate`, `force_windowed`, `free_camera_aurore_gate_bypass`, `free_camera_keyboard_forward_q_hook` |
| Hidden dependency expanded by AppCore | `free_camera_keyboard_forward_q_cave` |
| Module | `debug-camera-q-forward` |
| Proof posture | Experimental copied-runtime CDB proofs exist for the Aurore gate bypass and one Q-forward movement path. |

## Boundaries

- This is a preset/catalog/UI surfacing change over existing rows only.
- It does not launch BEA, attach CDB, send input, create a new runtime artifact, or mutate Ghidra.
- It does not prove a full free-camera control scheme, joystick/analog camera input, pause/menu safety, gameplay safety, online play, rebuild parity, or no-noticeable-difference parity.
- It keeps the installed Steam game folder and original `BEA.exe` as read-only source material; patch application remains confined to copied profiles/app-owned roots.

## Closeout Validation

Validation passed:

```powershell
dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~BinaryPatchRegressionTests.BinaryPatch_CatalogPresetEligibilityMatchesProfileDefinitions|FullyQualifiedName~BinaryPatchRegressionTests.BinaryPatchPlanBuilder_SafeCopyProfilePresetsCarryExpectedPolicy|FullyQualifiedName~WinUiProductLaneTests.PatchBench|FullyQualifiedName~WinUiAccessibilityAuditTests.PrimaryShellAndLongWorkflowControls"
dotnet build .\OnslaughtCareerEditor.WinUI\OnslaughtCareerEditor.WinUI.csproj --nologo
npm run test:winui-safe-copy-preflight
npm run test:winui-patch-catalog-accounting
py -3 tools\docsync_check.py
npm run test:doc-commands
npm run test:md-links
npm run test:public-allowlist
py -3 tools\release_profile_snapshot.py --check
py -3 tools\release_curated_manifest.py --check
npm run test:repo-hygiene
py -3 -c "import json; [json.load(open(p, encoding='utf-8-sig')) for p in ['developer_agent_state.json','documentation_agent_state.json','re_orchestrator_state.json']]; print('state json ok')"
git diff --check
```
