# Ghidra InfluenceMap Wave418 Static Correction

Date: 2026-05-14

## Summary

Wave418 saved a focused static-Ghidra correction for the InfluenceMap queue head. The pass corrected or hardened 17 CInfluenceMap / CInfluenceMapManager targets, created four previously missing vtable-slot function objects, corrected three stale saved labels, refreshed the full static re-audit queue, and backed up the live Ghidra project to `[maintainer-local-ghidra-backup-root]\BEA_20260514_135504_post_wave418_influencemap_verified`.

This is public-safe saved static retail-binary evidence. It is not runtime AI proof, not exact source-body recovery, not concrete class-layout recovery, and not rebuild parity.

## Saved Ghidra Changes

| Address | Saved state | Evidence boundary |
| --- | --- | --- |
| `0x0048afb0` | `CInfluenceMap__FreeObjectIfPresent` | Hardened cleanup helper signature/comment around manager/map-owned object-set cleanup. |
| `0x0048b010` | `CInfluenceMapManager__Load` | Hardened load signature/comment around versioned InfluenceMap data and map/link allocation context. |
| `0x0048b5f0` | `CInfluenceMap__GetTypeName_0048b5f0` | Created vtable-slot helper returning the `CInfluenceNode` string. |
| `0x0048b600` | `CInfluenceMap__GetTypeId_0048b600` | Created vtable-slot helper returning type id `0x1e`. |
| `0x0048b610` | `CInfluenceMap__GetInfluenceRadius_0048b610` | Created vtable-slot getter returning the field at `this+0x94`. |
| `0x0048b620` | `CInfluenceMap__ResetInfluence` | Hardened reset signature/comment around influence/distance fields. |
| `0x0048b660` | `CInfluenceMapManager__SkipLoad` | Hardened skip-load signature/comment for versioned data discard. |
| `0x0048b7d0` | `CInfluenceMapManager__PropagateDistances` | Hardened distance-propagation signature/comment and event scheduling context. |
| `0x0048b8e0` | `CInfluenceMapManager__Update` | Hardened update signature/comment around reset, nearest-map, propagation, and event context. |
| `0x0048bf70` | `CInfluenceMapManager__DecayInfluence` | Hardened temporary influence decay signature/comment. |
| `0x0048c000` | `CInfluenceMapManager__FindNearestMap` | Hardened nearest-map / temporary influence record signature/comment. |
| `0x0048c2d0` | `CInfluenceMapManager__IsEmpty` | Hardened manager-count predicate signature/comment. |
| `0x0048c2e0` | `CInfluenceMap__scalar_deleting_dtor` | Corrected stale `CInfluenceMap__ScalarDelete` label to destructor-wrapper shape. |
| `0x0048c300` | `CInfluenceMap__dtor` | Corrected stale destructor label and hardened cleanup-body context. |
| `0x0048c350` | `CInfluenceMap__DetachNeighborLinks_0048c350` | Created vtable-slot cleanup helper for neighbor-link detachment. |
| `0x0048c390` | `CInfluenceMap__InitFromComplexThingInit_0048c390` | Corrected stale `CInfluenceMap__RemoveFromList`; body is an init-forwarding wrapper, not list removal. |
| `0x0048c3b0` | `CInfluenceMap__CalculateInfluence` | Hardened influence-calculation signature/comment. |

The current repo snapshot of Stuart's source did not provide a directly matching InfluenceMap source body for this tranche. Historical debug-path strings and retail static evidence are useful context, but the saved names/comments remain bounded to retail-binary read-back.

## Validation

- Headless dry run: `updated=0 skipped=13 created=0 would_create=4 renamed=0 would_rename=3 missing=0 bad=0`.
- Headless apply: `updated=17 skipped=0 created=4 would_create=0 renamed=3 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Read-back exports verified `17` metadata rows, `17` tag rows, `24` xref rows, `1683` instruction rows, `17` decompile rows, active vtable `0x005dc050` slot resolution, and the `CInfluenceNode` string token.
- Focused probe tests passed: `py -3 tools\ghidra_influencemap_wave418_probe_test.py`.
- Focused probe passed through npm: `cmd.exe /c npm run test:ghidra-influencemap-wave418`.
- Python compile check passed for the Wave418 probe and tests.
- Full static queue refreshed to `6043` functions, `1641` commented functions, `4402` commentless functions, `1878` undefined signatures, and `1822` `param_N` signatures.
- Current confirmation proxies are telemetry only: comment-backed `1641/6043 = 27.16%`; strict comment-plus-clean-signature `1578/6043 = 26.11%`.
- Live Ghidra backup verification: `19` files, `155061127` bytes, `HashDiffCount=0`.

## Not Proven

- Runtime InfluenceMap AI behavior is not proven.
- Exact Stuart-source method identity is not proven for all saved labels.
- Concrete CInfluenceMap / CInfluenceMapManager layouts, locals, and structure types remain open.
- BEA was not launched, patched, or debugged in this wave.
- This does not prove rebuild parity or game-behavior equivalence.
