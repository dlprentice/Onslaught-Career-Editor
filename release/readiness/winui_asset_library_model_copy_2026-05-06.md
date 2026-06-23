# WinUI Asset Library Model Copy Guard - 2026-05-06

Status: public-safe WinUI product-lane evidence

Source branch: `wip/sandbox`
Source commit under validation: `67a0d7c7f6f07fb62e65ee7455ccbb4ca377be91`
Evidence-report commit: `254a8ac87c33dd8808e8201ba9030440f9f986d9`

## Purpose

Correct stale Asset Library model-copy wording after the WinUI app gained bounded in-app wireframe preview support. The user-facing model summary should not say native 3D preview is only planned or unavailable when the current feature is a lightweight wireframe geometry check.

## Change

- Loose and embedded model summaries now state that the in-app wireframe is useful for a quick geometry check.
- Model empty/status copy now says the exported FBX remains the path for full material review.
- Product-lane tests now guard against the stale phrases:
  - `native 3D preview is planned`
  - `Native in-app 3D rendering is not enabled yet`

## Commands

| Command | Working directory | Result | Important output | What it proves |
| --- | --- | --- | --- | --- |
| `dotnet test .\OnslaughtCareerEditor.UiTests\OnslaughtCareerEditor.UiTests.csproj --nologo --filter "FullyQualifiedName~WinUiProductLaneTests"` | repo root | PASS | 12/12 tests passed. | WinUI product-lane source guards accept the updated Asset Library copy and reject stale model-preview claims. |
| process cleanup check for `OnslaughtCareerEditor.WinUI`, `dotnet`, `MSBuild`, `vstest.console`, `testhost`, `java`, and `javaw` | repo root | PASS | `none` | The targeted test run left no relevant app/build/test processes running. |

## Public-Safe Boundaries

- No game executable launch.
- No game install mutation.
- No private asset catalog, screenshots, or extracted media committed.
- No full native 3D/material/animation rendering claim.

## Remaining Limits

- The current WinUI model viewer remains a bounded wireframe and metadata preview.
- Full material rendering, animation, camera controls, and row-by-row visual coverage remain future product work.
