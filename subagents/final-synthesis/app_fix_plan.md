# App Fix Plan

## Completed
1. Add shared patch catalog v2 and wire C# engine loader (`BinaryPatchEngine.cs`).
2. Add shared patch catalog v2 loader in Python core (`onslaught/core/binary_patches.py`).
3. Update PyQt Binary Patches tab to consume keyed specs from core catalog-loaded definitions.
4. Preserve existing verify/apply/restore and backup semantics while removing duplicated patch-bytes authority.

## Validation Completed
1. `dotnet build Onslaught - Career Editor.sln`
2. `dotnet test OnslaughtCareerEditor.UiTests/OnslaughtCareerEditor.UiTests.csproj`
3. `python3 -m unittest discover -v tests_pyqt -p 'test_*_unittest.py'`

## Deferred
1. Additional binary patch families beyond current display/windowed set are deferred pending new evidence-backed patch definitions.
2. Runtime matrix expansion for deep modernization remains outside this closure tranche.
