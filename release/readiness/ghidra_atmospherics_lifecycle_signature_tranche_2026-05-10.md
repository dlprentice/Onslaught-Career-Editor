# Ghidra Atmospherics Lifecycle Signature Tranche - 2026-05-10

## Scope

This note records a saved Ghidra signature/comment hardening tranche for eight Atmospherics lifecycle/list and trail setup helpers. It is public-safe static RE evidence only: no BEA launch, no debugger attach, no executable patching, no installed-game mutation, and no private decompile excerpt is included here.

## Saved Targets

| Address | Current saved name | Saved signature boundary |
| --- | --- | --- |
| `0x004046d0` | `CAtmospheric__Constructor` | `void * __thiscall ...(void * this, void * ownerThing)` |
| `0x00404a00` | `Atmospherics__Init` | `void __cdecl ...(void)` |
| `0x00404b90` | `Atmospherics__ResetAndUpdate` | `void __cdecl ...(void)` |
| `0x00404bd0` | `Atmospherics__UpdateAll` | `void __cdecl ...(void)` |
| `0x00404bf0` | `Atmospherics__RenderAll` | `void __cdecl ...(void)` |
| `0x00404c10` | `Atmospherics__Shutdown` | `void __cdecl ...(void)` |
| `0x00404c90` | `Atmospherics__NotifyAll` | `void __cdecl ...(int eventCode)` |
| `0x004f44a0` | `CThing__AddTrail` | `void __thiscall ...(void * this, int samplerIndex, int resetBlendPosition, int blendMode)` |

## Evidence Summary

- Headless dry/apply saved eight names/signatures/comments with dry `updated=0 skipped=8 missing=0 bad=0` and apply `updated=8 skipped=0 missing=0 bad=0`.
- Final metadata and decompile read-back found `8/8` targets.
- Final xref export produced `66` xref rows across the targets.
- Final instruction export produced `1192` instruction rows across the targets.
- The focused probe reports `8` targets, `0` stale signature hits, `0` comment overclaims, `8` xref-evidence hits, and `7` return-evidence hits.
- `CAtmospheric__Constructor` is corrected from the prior float-parameter interpretation: checked caller and decompile evidence show `CThing__AddTrail` passes the owning `CThing` pointer, and the constructor stores that pointer at `+0x20`.
- `CThing__AddTrail` now carries three named stack arguments from `ret 0xc` evidence and the post-call `CAtmospheric__ConfigureTrail` shape.

## Boundary

This tranche improves saved Ghidra signatures/comments only. It does not prove concrete `CAtmospheric` or `CThing` structure layouts, exact Stuart-source identity for all helpers, concrete virtual slot names for the global atmospheric list walkers, runtime weather/trail behavior, BEA launch behavior, game patching, or rebuild parity.
