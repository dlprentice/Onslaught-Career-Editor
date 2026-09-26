# Companion provenance and license

Status: active independent MIT application boundary
Last updated: 2026-09-25
Evidence: SOURCE — code-built C# application and linked safety source; executed package boundaries are recorded in VALIDATION.md.
Summary: the companion's C# derives only from MIT application references; retail data and GPL reconstruction remain separate.

All C# in this project is original MIT application code under the repository
[LICENSE](../../LICENSE). Save layout facts and behavior were ported from the MIT
`BesFilePatcher`, `SaveLabService` and their focused tests, through the companion's
earlier GDScript implementation. The interface, theme and styles are constructed in code
from Godot's built-in controls and default engine font.

[ProtectedSaveFiles](Files/ProtectedSaveFiles.cs) links `SaveLabFileTransaction.cs` and
`FileMutationSafety.cs` unchanged. It performs OS file protection and verified
publication only; it imports no C# save parser, AppCore assembly or third-party AppCore
media library. Godot .NET SDK `4.8.0-dev.6` and the self-contained .NET runtime are
disclosed production dependencies with their MIT and third-party notices, which every
export carries. Godot retains its own MIT and third-party licenses.

No source from `rebuild/` or `references/Onslaught`, decompiler output, proprietary
asset, font, music, executable or user save enters this application or its exports.
Using Godot in both lanes does not combine their licensing boundaries. No retail payload
is required to build or launch the companion.

Tests receive owned copies of the one registered
[real-save fixture](../../tests_shared/fixtures/README.md); it is neither modified nor
packaged. User-selected media is inventoried at runtime, not imported into the project.
Captures, private inputs, test outputs and packages remain in ignored `local-data/`.

Verification messages describe byte identity, file identity and an executed file
operation. They do not assert retail gameplay acceptance, crash or power-loss survival,
or Windows execution from a Linux test or cross-export.
