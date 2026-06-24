# Ghidra FEPOptions Core Wave858 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `fepoptions-core-wave858`

Wave858 FEPOptions core created four previously missing `CFEPOptions` vtable-slot function objects and saved bounded comments, tags, and signatures for nine important frontend/options connective rows. The pass made four function-object creations, no executable-byte changes, and no source-identity claim.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0051f370 CFEPOptions__GetState` | Called by `CFrontEnd__Process` at `0x00466c8d` and `CGame__LoadLevel` at `0x0046cf49`; returns signed byte `this+0x05`. |
| `0x0051f4b0 CFEPOptions__Init` | Created from CFEPOptions vtable `0x005db8a8` slot 0; clears page state at `this+0x04` and returns `1`. |
| `0x0051f4c0 CFEPOptions__Shutdown` | Created from vtable slot 1; frees non-null `g_pOptionsContext` through vtable slot `+4` with flag `1`, then clears `0x0089bc30`. |
| `0x0051f4e0 CFEPOptions__ButtonPressed` | Created from vtable slot 3; delegates button/analog arguments to `g_pOptionsContext` vtable slot `+0x0c` with a leading zero argument. |
| `0x0051f500 CFEPOptions__SaveDefaultOptions` | Serializes `CAREER` into a `CDXMemoryManager` buffer, writes `defaultoptions.bea`, and emits `Couldn't write defaultoptions` on failure. |
| `0x0051f600 CFEPOptions__ProcessInput` | CFEPOptions process/state vtable slot 2; advances page states and calls `CFEPOptions__SaveDefaultOptions(1)` on the observed confirm path. |
| `0x0051f6d0 CFEPOptions__RenderPreCommon` | Created from vtable slot 4; forces transition to `1.0` for destination/page ids `0x12` and `0x13`, then calls `CFrontEnd__RenderPreCommonFade`. |
| `0x0051f700 CFEPOptions__Update` | CFEPOptions render/update vtable slot 5; renders borders, `g_pOptionsContext`, title fallback id `0x265233`, help prompt id `1`, and overlay effects. |
| `0x0051f8e0 CFEPOptions__Cleanup` | Called from `CFrontEnd__SetLanguage` at `0x00466ab3`; mirrors options-context shutdown and clears `0x0089bc30`. |

Read-back evidence:

- `CreateFunctionsFromAddressList.java dry`: `created=0 would_create=4 failed=0`.
- `CreateFunctionsFromAddressList.java apply`: `created=4 renamed=4 failed=0`.
- `ApplyFEPOptionsCoreWave858.java dry`: `updated=9 skipped=0 renamed=0 would_rename=0 signature_updated=4 comment_only_updated=5 missing=0 bad=0`.
- First saved apply exposed only Ghidra prototype-string convention read-back mismatches for the four newly created rows; the metadata itself was saved and the log is preserved as evidence.
- Corrected redry and final dry: `updated=0 skipped=9 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports: 9 metadata rows, 9 tag rows, 11 xref rows, 333 instruction rows, 9 decompile rows, 15 context metadata rows, 15 context decompile rows, 18 vtable slot rows, and three string dumps.
- String anchors: `0x0063fc54` is `Couldn't write defaultoptions`, `0x0063fc74` is `defaultoptions.bea`, and `0x0063fc88` is `C:\dev\ONSLAUGHT2\FEPOptions.cpp`.
- Queue after Wave858: 6105 total functions, 5779 commented, 326 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5779/6105 = 94.66%`, strict comment-plus-clean-signature proxy `5779/6105 = 94.66%`.
- Next raw commentless row: `0x0051f9f0 CFEPScreenPos__Init`.
- Verified backup: `G:\GhidraBackups\BEA_20260525-124939_post_wave858_fepoptions_core_verified`, 19 files, 172198791 bytes, `DiffCount=0`.

What this proves:

- The nine target function rows exist in the saved Ghidra project.
- The four previously missing CFEPOptions vtable-slot function objects were created after a clean dry-run.
- Saved comments and tags include `fepoptions-core-wave858` and `wave858-readback-verified`.
- The observed static evidence ties CFEPOptions to frontend options page state, `defaultoptions.bea` writing, options-context delegation, render/update hooks, language-change cleanup, and the CFEPOptions vtable at `0x005db8a8`.

What remains unproven:

- Exact `CFEPOptions` layout.
- Exact options-context class/layout.
- Runtime options menu behavior.
- Runtime filesystem behavior for `defaultoptions.bea`.
- BEA patching behavior.
- Rebuild parity.
