# Asset Model Texture Link Hardening - 2026-05-07

Status: public-safe AppCore evidence

Source branch: `wip/sandbox`
Source commits under validation:

- `2a347ba01526132452bc64d0e681f59d9c1aa9c5` - model texture-link blank-binding hardening.
- `e8d70b9589eed404b48b8271fc886baf68ae3a39` - FBX texture path separator normalization.

## Purpose

Tighten the Asset Library model-preview foundation before any richer model viewer or Goodies Browser work. The current WinUI model surface is a wireframe/export preview, but its texture-link summary still needs honest counts and stable catalog matching.

## Change

- `AssetModelTextureLinkService` now ignores blank or whitespace FBX texture binding names before sorting and matching.
- A focused AppCore test now covers malformed blank bindings plus common path/name variants such as `textures\texture_one.tga.png` and `Texture One.dds`.
- The guard keeps the UI from inflating texture-link counts or implying readable model texture links from empty binding strings.
- `FbxModelSummaryReader` now normalizes both Windows-style and POSIX-style separators before extracting texture filenames from FBX string properties.

## Commands

| Command | Working directory | Result | Important output | What it proves |
| --- | --- | --- | --- | --- |
| `dotnet test OnslaughtCareerEditor.AppCore.Tests/OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter FullyQualifiedName~ModelTextureLinks` | repo root | PASS | 2/2 tests passed. | Confirms the focused model texture-link tests pass, including blank-binding filtering and catalog matching. |
| `dotnet test OnslaughtCareerEditor.AppCore.Tests/OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter FullyQualifiedName~FbxModelSummaryReaderTests` | repo root | PASS | 3/3 tests passed. | Confirms FBX model-summary parsing still extracts texture filenames and wireframe metadata after separator normalization. |
| `dotnet test OnslaughtCareerEditor.AppCore.Tests/OnslaughtCareerEditor.AppCore.Tests.csproj --nologo` | repo root | PASS | 80/80 tests passed. | Confirms the broader AppCore correctness suite stays green after the hardening change. |
| `dotnet run --project OnslaughtCareerEditor.AppCore.Host/OnslaughtCareerEditor.AppCore.Host.csproj -- inspect-asset-model-preview <private full-install catalog> --sample-limit 16` | repo root | PASS | Public-safe summary: model rows `352`, existing exports `352`, metadata rows `352`, wireframe rows `352`, rows with texture bindings `352`, texture binding nodes `8448`, rows with catalog-matched texture links `352`, unmatched rows `0`, total catalog-matched texture links `1268`. | Confirms every full-catalog model row still has at least one catalog-matched texture link after the hardening. |

Important nuance: this proves row-level texture-link coverage, not total material completion. The private full-catalog output still has more FBX binding strings (`8448`) than catalog-matched texture names (`1268`), because many bindings are exporter/default placeholder names. A future textured model viewer must handle that distinction explicitly.

## Private Artifact Location

Raw JSON output was written under ignored private evidence:

```text
subagents/model-texture-link-hardening-2026-05-07/asset-model-preview-coverage.json
```

Do not commit that file; it contains private generated catalog evidence and sample row names from the local install.

## Public-Safe Boundaries

- No BEA launch.
- No installed game mutation.
- No Ghidra mutation.
- No private asset catalog, screenshots, extracted media, or copied game files committed.
- No claim of textured or animated in-app model rendering.

## Remaining Limits

- This hardening proves catalog matching behavior, not row-by-row full-install model texture coverage.
- Full-install model texture-link coverage is refreshed at the summary level above, but raw row payloads remain private and ignored.
- Row-level coverage does not mean every FBX material binding resolves to a recovered texture. Placeholder/default bindings remain part of the material-work follow-up.
- Current WinUI model viewing remains wireframe/export-based.
- Full material assignment, animation, camera controls, and from-scratch runtime reconstruction remain separate future work.
