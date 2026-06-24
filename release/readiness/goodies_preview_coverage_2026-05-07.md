# Goodies Preview Coverage Evidence - 2026-05-07

## Scope

This pass added a read-only AppCore.Host command that measures Goodies preview readiness from a generated asset catalog without exposing private paths or asset payloads in public evidence.

Raw generated JSON remains ignored/private under:

```text
subagents/goodies-preview-coverage/current/goodies-preview-coverage.json
```

## Commands

```powershell
dotnet build OnslaughtCareerEditor.AppCore.Host/OnslaughtCareerEditor.AppCore.Host.csproj --nologo
dotnet test OnslaughtCareerEditor.AppCore.Tests/OnslaughtCareerEditor.AppCore.Tests.csproj --nologo
dotnet run --project OnslaughtCareerEditor.AppCore.Host/OnslaughtCareerEditor.AppCore.Host.csproj -- inspect-goodie-preview-coverage <private catalog.json> --sample-limit 16
```

Results:

- AppCore.Host build: PASS, 0 warnings, 0 errors.
- AppCore tests: PASS, 75 passed, 0 failed, 0 skipped.
- Goodies preview coverage command: PASS.

## Public-Safe Summary

Catalog summary from the private full-install catalog:

| Catalog family | Count |
| --- | ---: |
| Total catalog entries | 4,050 |
| Goodie rows | 233 |
| Texture rows | 828 |
| Loose mesh rows | 213 |
| Video rows | 66 |

Goodies preview coverage:

| Coverage check | Count |
| --- | ---: |
| Displayable Goodie rows | 233 |
| Source-grid-visible rows | 230 |
| Source-grid-hidden rows | 3 |
| Texture-bearing rows | 194 |
| Texture rows matched to catalog exports | 194 |
| Texture previews ready | 194 |
| Model-bearing rows | 45 |
| Model rows matched to catalog exports | 45 |
| Model FBX exports ready | 45 |
| Model wireframes ready | 45 |
| Video rows | 34 |
| Video rows linked to catalog videos | 34 |
| Rows without local preview | 5 |

The five rows without local preview are level-unlock metadata rows. The current WinUI path handles them as unlock/status information rather than image, model, or video previews.

## What This Proves

- AppCore.Host can now produce repeatable Goodies preview coverage from a generated catalog.
- The private full-install catalog has preview-ready texture coverage for all 194 texture-bearing Goodies.
- The private full-install catalog has FBX export and wireframe coverage for all 45 model-bearing Goodies.
- All 34 video Goodies have catalog video links for Media-section handoff.
- Goodies 71-73 remain counted as source-grid-hidden shipped artwork rows, but their texture previews are present.

## What This Does Not Prove

- It does not prove final textured or animated in-app 3D model rendering.
- It does not prove runtime replay of every Goodies wall navigation path.
- It does not prove that the five level-unlock rows should have visual previews.
- It does not commit or redistribute extracted assets, raw catalog content, private paths, screenshots, frames, or proof JSON.
