# Ghidra CRadar / Goodies Boundary Recovery Wave1088 Readiness Note

Status: complete static read-back evidence
Date: 2026-06-04
Scope: `cradar-goodies-boundary-recovery-wave1088`

Wave1088 recovered and saved seven previously missing Ghidra function boundaries from the CRadar residual vtable sample at `0x005dd710`, then hardened three Goodies/frontend helper functions that Ghidra auto-analysis created during Wave1088 evidence recovery. The sidecar recovery restored the all-function quality queue to zero weak/commentless/signature debt. The pass made no executable-byte changes, no installed-game changes, and no runtime claims.

Representative CRadar recovered rows:

| Address | Saved name | Static evidence |
| --- | --- | --- |
| `0x004bfb00` | `CRadarVFunc__GetClassNameString_004bfb00` | Slot `37`, DATA xref `0x005dd7a4`; returns string `0x00630c44`, read back as `CRadar`. |
| `0x0052ddb0` | `SharedUnitVFunc__ReturnInt10_0052ddb0` | Slot `38`, DATA xref `0x005dd7a8` plus additional DATA refs `0x005ddbbc` and `0x005e4ca8`; returns `0x0a`. |
| `0x004d6360` | `CRadarVFunc__FlagArg70AndSeedMotion280_004d6360` | Slot `39`, DATA xref `0x005dd7ac`; sets bit `0x20` in `arg+0x70`, calls `0x004f86d0`, copies from `0x0083c9d8` into `this+0x250`, derives a pseudo-random float, and stores it at `this+0x280`. |
| `0x004bfb20` | `CRadarVFunc__ReturnFloat005d8bb8_004bfb20` | Slot `46`, DATA xref `0x005dd7c8`; returns float data at `0x005d8bb8`. |
| `0x004bfb10` | `CRadarVFunc__ForwardArgWithLowFlag20_004bfb10` | Slot `68`, DATA xref `0x005dd820`; ORs the low byte of the stack value with `0x20`, forwards to `0x004fcdc0`, and returns with `RET 0x4`. |
| `0x004d63c0` | `CRadarVFunc__UpdateMotionVector250FromAngle280_004d63c0` | Slot `96`, DATA xref `0x005dd890`; advances wrapped angle/state `this+0x280`, computes sine/cosine values, and writes vector/matrix-like fields through `this+0x250..0x278`. |
| `0x004f6560` | `CRadarVFunc__CopyFrameOrComputedTransformToOut_004f6560` | Slot `149`, DATA xref `0x005dd964`; copies a 12-dword frame transform from `0x008406b8 + index*0x30` or computes/copies a transform through vector helpers. |

Goodies/frontend sidecar recovery rows:

| Address | Saved name | Static evidence |
| --- | --- | --- |
| `0x0041c160` | `CCareer__GetKillCounterLow24ByType_0041c160` | `0x0045a940` calls this helper; body reads `this+0x23f4+killType*4`, masks with `0x00ffffff`, and returns with `RET 0x4`. |
| `0x0045a940` | `CFEPGoodies__BuildGoodieRequirementText_0045a940` | `CFEPGoodies__Render` callsite `0x0045e906`; builds wide requirement/status text using `CText__GetStringById`, `CRT__WStrCpy`, `Text__AsciiToWideScratch`, `CRT__WStrCat`, kill-count requirements, and grade-related requirement cases. |
| `0x0045ff80` | `CFEPGoodies__ClassifyGoodieIndexForRender_0045ff80` | `CFEPGoodies__Render` callsite `0x0045e930`; returns `2` for Goodie indices `<= 7`, otherwise returns `1` for indices `<= 0x41` and `0` above `0x41`. |

Read-back evidence:

- CRadar dry-run: `updated=0 skipped=0 created=0 would_create=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0`
- CRadar apply: `updated=7 skipped=0 created=7 would_create=0 renamed=0 would_rename=0 signature_updated=7 comment_only_updated=0 bad=0`
- CRadar final dry-run: `updated=0 skipped=7 created=0 would_create=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 bad=0`
- Goodies recovery dry-run: `updated=0 skipped=3 renamed=0 would_rename=3 signature_updated=3 comment_only_updated=0 missing=0 bad=0`
- Goodies recovery apply: `updated=3 skipped=0 renamed=3 would_rename=0 signature_updated=3 comment_only_updated=0 missing=0 bad=0`
- Goodies recovery final dry-run: `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- CRadar post exports: `7` metadata rows, `7` tag rows, `9` xref rows, `350` function-body instruction rows, `7` decompile rows, and `1600` post vtable-slot rows.
- Goodies post-recovery exports: `3` metadata rows, `3` tag rows, `4` xref rows, `263` function-body instruction rows, and `3` decompile rows.
- Vtable sample after Wave1088: `1545` OK and `55` `NO_FUNCTION_AT_POINTER`; the seven selected CRadar code pointers now resolve to saved functions. CRadar slots `29` (`0x00615728`) and `147` (`0x006155d0`) remain deliberate `.rdata`/non-function entries.
- Queue after Wave1088: `6375/6375 = 100.00%` static function-quality closure, with `0` commentless functions, `0` exact-`undefined` signatures, `0` `param_N` signatures, `0` uncertain-owner rows, `0` helper-address rows, and `0` wrapper-address rows.
- Expanded static re-audit surface: `1492/1560 = 95.64%`. Wave911 focused remains `812/1408 = 57.67%`; top-500 remains `500/500 = 100.00%`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260604-121500_post_wave1088_cradar_goodies_boundary_recovery_verified`, `19` files, `175344519` bytes, `DiffCount=0`.

What this proves:

- The seven CRadar target code addresses now exist as saved Ghidra function entries.
- The three Goodies/frontend sidecar rows have bounded saved names/signatures/comments/tags instead of temporary weak auto-analysis names.
- The saved comments/tags/signatures match the bounded Wave1088 static evidence.
- The all-function quality queue is closed again at 100%.

What remains unproven:

- Exact source virtual names.
- Concrete CRadar, CFEPGoodies, and CCareer layout semantics.
- Runtime Goodies behavior or CRadar/unit behavior.
- BEA patching behavior.
- Clean-room rebuild parity.

Probe token anchor: Wave1088; cradar-residual-vtable-tail-wave1088; goodies-autoanalysis-boundary-recovery-wave1088; `0x004bfb00 CRadarVFunc__GetClassNameString_004bfb00`; `0x004d6360 CRadarVFunc__FlagArg70AndSeedMotion280_004d6360`; `0x004f6560 CRadarVFunc__CopyFrameOrComputedTransformToOut_004f6560`; `0x0041c160 CCareer__GetKillCounterLow24ByType_0041c160`; `0x0045a940 CFEPGoodies__BuildGoodieRequirementText_0045a940`; `0x0045ff80 CFEPGoodies__ClassifyGoodieIndexForRender_0045ff80`; `1545` OK / `55` `NO_FUNCTION_AT_POINTER`; `1492/1560 = 95.64%`; `812/1408 = 57.67%`; `500/500 = 100.00%`; `6375/6375 = 100.00%`; `[maintainer-local-ghidra-backup-root]\BEA_20260604-121500_post_wave1088_cradar_goodies_boundary_recovery_verified`; boundary recovery.
