# Companion provenance and license

Status: active independent MIT application boundary
Last updated: 2026-09-19
Evidence: SOURCE — native scenes/domain and FileBridge project links; executed package boundaries are recorded in VALIDATION.md.
Summary: native companion scenes and GDScript derive only from MIT application references; retail data and GPL reconstruction remain separate.

The scenes, theme and typed GDScript in this project are original MIT application
code under the repository [LICENSE](../../LICENSE). Save layout facts and behavior
were ported from the existing MIT `BesFilePatcher`, `SaveLabService` and their
focused tests. The native parser is now the production companion owner; retained
C# save/UI code is a development reference, excluded from native exports.

The explicit [FileBridge](../OnslaughtToolkit.FileBridge/README.md) exception links
`SaveLabFileTransaction.cs` and `FileMutationSafety.cs` unchanged. It performs OS
file protection and verified publication only; it imports no C# save parser,
AppCore assembly, Godot .NET SDK or third-party AppCore media libraries. Its
self-contained .NET runtime remains a disclosed production dependency with its
own MIT and third-party notices. Standard Godot retains its MIT/third-party
licenses. The interface uses built-in controls and the default engine font.

No source from `rebuild/` or `references/Onslaught`, decompiler output, proprietary
asset, font, music, executable or user save enters this application or its exports.
Using Godot in both lanes does not combine their licensing boundaries. No retail
payload is required to open the editor or launch the companion.

Tests receive owned copies of the one registered
[real-save fixture](../../tests_shared/fixtures/README.md); it is neither modified
nor included in a package. User-selected media is inventoried locally at runtime,
not imported into this Godot project. All captures, private inputs, test outputs
and packages remain in ignored `local-data/`, never tracked source.

Verification messages describe byte identity, file identity and an executed file
operation. They do not assert retail gameplay acceptance, crash/power-loss survival
or Windows execution merely from a Linux test or cross-export.
