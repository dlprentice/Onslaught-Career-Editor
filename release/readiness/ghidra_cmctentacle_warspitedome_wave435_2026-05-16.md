# Ghidra CMCTentacle / CMCWarspiteDome Wave435 Correction

Status: public-safe static Ghidra evidence note
Date: 2026-05-16
Scope: saved retail `BEA.exe` Ghidra create/name/signature/comment/tag correction

## Summary

Wave435 corrected the `CMCTentacle` cluster and the adjacent `CMCWarspiteDome` motion-controller table. It recovered four missing vtable-slot function boundaries from vtables `0x005dc450` and `0x005dc484`, corrected stale owner labels for the tentacle mesh-part filter and mesh predicate, and saved lifecycle/signature/comment/tag evidence for `18` targets.

This is public-safe static evidence only. It does not launch or patch `BEA.exe`, does not mutate the installed Steam game, and does not include raw decompile text or private runtime proof.

## Saved Ghidra Changes

| Address | Saved state | Static evidence summary |
| --- | --- | --- |
| `0x0049cad0` | `CMCTentacle__Constructor` | Calls the base motion-controller constructor, installs vtable `0x005dc450`, stores owner tentacle at `+0x08`, and clears setup state. |
| `0x0049cb20` | `CMCTentacle__ScalarDeletingDestructor` | Delete-flags wrapper for `CMCTentacle__Destructor`; frees through `OID__FreeObject` only when flag bit 0 is set. |
| `0x0049cb40` | `CMCTentacle__Destructor` | Restores vtable `0x005dc450`, releases owned buffers, clears owner/setup fields, and tails into the base motion-controller destructor. |
| `0x0049cc40` | `CMCTentacle__Init` | Initializes from the mesh model, allocates current/previous bone state and spline buffers, scans control-bone names, and marks setup at `this+0x2c`. |
| `0x0049d280` | `CMCTentacle__UpdateBone` | Recursive per-bone transform update with lazy init, special control-bone handling, cached previous-state writes, and child traversal. |
| `0x0049dc90` | `CMCTentacle__Factorial` | Iterative factorial helper used by Bezier coefficient math. |
| `0x0049dcb0` | `CMCTentacle__Power` | Iterative float power helper used by Bezier polynomial math. |
| `0x0049dcd0` | `CMCTentacle__UpdateSpline` | Evaluates cubic Bezier spline positions, builds orientation matrices, and writes spline position/matrix buffers. |
| `0x0049e4b0` | `CMCTentacle__BuildOrientationMatrix` | Builds a 3x4 orientation matrix from direction/up vectors; read-back keeps the output matrix pointer as Ghidra's hidden `this`. |
| `0x0049e660` | `CMCTentacle__VFunc_04_UpdateInterpolatedBoneTransform_0049e660` | Created vtable slot-4 boundary for interpolated tentacle bone transform output and cached timing refresh. |
| `0x0049ead0` | `CMCTentacle__VFunc_05_WriteInterpolatedBoneFloat_0049ead0` | Created vtable slot-5 boundary for interpolated per-bone float output. |
| `0x0049ec80` | `CMCTentacle__VFunc_08_CheckCachedUpdateTime_0049ec80` | Created vtable slot-8 boundary for compact cached-update predicate. |
| `0x0049eca0` | `CMeshPart__NameAvoidsTentacleOptimizationTokens` | Corrected old backwards `CMCTentacle__ValidateBoneStructure` label; returns false for protected tokens `tether`, `head`, `tethercp`, `headcp`, `tentacle`, or `bone` prefix, true otherwise. |
| `0x0049ed30` | `CMesh__HasTentacleBone` | Corrected old instance-method ownership to a mesh-level scan for a `tentacle` bone. |
| `0x0049ef80` | `CMCWarspiteDome__Constructor` | Installs vtable `0x005dc484`, stores owner dome at `+0x08`, and clears cached state. |
| `0x0049efa0` | `CMCWarspiteDome__ScalarDeletingDestructor` | Delete-flags wrapper for `CMCWarspiteDome__Destructor`. |
| `0x0049efc0` | `CMCWarspiteDome__Destructor` | Restores vtable `0x005dc484`, clears owner/cached fields, and tails into the base motion-controller destructor. |
| `0x0049efe0` | `CMCWarspiteDome__VFunc_04_UpdateDomeTransform_0049efe0` | Created dome vtable slot-4 boundary for owner-driven dome mesh-part transform updates. |

## Validation

| Command or check | Result | Important output |
| --- | --- | --- |
| `py -3 -m py_compile tools\ghidra_cmctentacle_warspitedome_wave435_probe.py tools\ghidra_cmctentacle_warspitedome_wave435_probe_test.py` | PASS | Focused probe modules compile. |
| `py -3 tools\ghidra_cmctentacle_warspitedome_wave435_probe_test.py` | PASS | Focused tests passed `4/4`. |
| Headless `ApplyCmcTentacleWarspiteDomeWave435.java` dry/apply/correction/verify | PASS | Dry `updated=0 skipped=14 created=0 would_create=4 renamed=0 would_rename=8 missing=0 bad=0`; apply `updated=18 skipped=0 created=4 would_create=0 renamed=8 would_rename=0 missing=0 bad=0`; corrective apply `updated=18 skipped=0 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`; verify dry `updated=0 skipped=18 created=0 would_create=0 renamed=0 would_rename=0 missing=0 bad=0`; apply passes included `REPORT: Save succeeded`. |
| Post-apply metadata/tag/xref/vtable/instruction/decompile read-back | PASS | Verified `18` metadata rows, `18` tag rows, `28` xref rows, `32` vtable-slot rows, `4338` instruction rows, and `18` target decompile exports. |
| `cmd.exe /c npm run test:ghidra-cmctentacle-warspitedome-wave435` | PASS | Focused probe returned `status: PASS` for all `18` saved targets. |
| `cmd.exe /c npm run test:ghidra-static-reaudit-queue` | PASS | Queue reports `6055` total functions, `1791` commented functions, `4264` commentless functions, `1803` undefined signatures, and `1762` `param_N` signatures. |
| Actual Ghidra project backup verification after Wave435 mutation | PASS | Copied the live project to `[maintainer-local-ghidra-backup-root]\BEA_20260516-000814_post_wave435_cmctentacle_warspitedome_verified`; compared `19` files and `155880327` bytes with `MissingCount=0`, `HashDiffCount=0`, and `ExtraCount=0`. |

## Current Queue Telemetry

The refreshed static re-audit queue currently reports:

- Total function objects: `6055`
- Commented function objects: `1791`
- Commentless function objects: `4264`
- `undefined` signatures: `1803`
- Signatures still using `param_N`: `1762`

Telemetry-only proxies are comment-backed `1791/6055 = 29.58%` and strict clean-signature `1729/6055 = 28.55%`. These are not certification and are not completion gates.

## Not Proven

This wave does not prove runtime tentacle or dome motion behavior; exact concrete layouts beyond observed offsets; exact virtual method names; exact local variable names/types; exact source-body identity; source-to-retail rebuild parity; BEA launch behavior; game patching; or runtime gameplay behavior.
