# Goodies Grid Mapping AppCore Guard - 2026-05-07

## Scope

This pass converted the compiled `get_goodie_number(x, y)` wall mapping into an AppCore guard so future WinUI/Product code can reuse the same source-grid truth instead of hand-maintaining only prose docs.

## TDD Record

Red test first:

```powershell
dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~GoodieWallGridMappingService"
```

Expected failure:

```text
CS0103: The name 'GoodieWallGridMappingService' does not exist in the current context
```

Green result after minimal implementation:

```text
Passed!  - Failed: 0, Passed: 20, Skipped: 0, Total: 20
```

## What Is Guarded

- Row `0` maps bios, race unlocks, and developer items.
- Row `1` maps unit/model gallery items.
- Row `2` maps FMV slots `201..232`.
- Row `3` maps concept-art slots `78..200`.
- Invalid coordinates return `-1`.
- Shipped archive slots `71..73` are not treated as source-grid-visible.

## Follow-Up Guard

The later Wave 166 check added two stronger invariants:

- Every source-grid-visible Goodie index from `0..232`, excluding shipped-but-hidden `71..73`, must round-trip through `Locate(index)` and then `Resolve(x, y)` back to the same index.
- Every coordinate returned by the compiled visible wall mapping must be unique. The guard expects `230` visible mapped indices, excludes `71`, `72`, and `73`, and includes displayable FMV slot `232`.

Focused validation:

```powershell
dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo --filter "FullyQualifiedName~GoodieWallGridMappingService"
```

Result: PASS

Important output:

```text
Passed!  - Failed: 0, Passed: 32, Skipped: 0, Total: 32
```

Broader AppCore validation:

```powershell
dotnet test .\OnslaughtCareerEditor.AppCore.Tests\OnslaughtCareerEditor.AppCore.Tests.csproj --nologo
```

Result: PASS

Important output:

```text
Passed!  - Failed: 0, Passed: 79, Skipped: 0, Total: 79
```

## What This Does Not Prove

- It does not launch the game.
- It does not replay the Goodies wall at runtime.
- It does not prove final textured or animated native model rendering.
- It does not patch or mutate the installed `BEA.exe`.

## Follow-Up

Use this AppCore mapping as the stable bridge for future save-aware Goodies browser work and any copied-profile runtime replay comparison.
