# Ghidra Geometry Guide Heightfield Spine Review Wave1009 Readiness Note

Status: complete saved static read-back evidence
Date: 2026-05-31
Scope: `geometry-guide-heightfield-spine-review-wave1009`

Wave1009 re-reviewed the geometry / guide / heightfield spine around `CStaticShadows__SampleShadowHeightBilinear` and recovered ten DATA-backed function boundaries from previously no-function static-shadow caller islands. The pass created ten function objects, saved names/signatures/comments/tags for those recovered rows, refreshed the function-quality queue to `6233/6233 = 100.00%`, and made no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Primary carried-forward anchors:

| Address | Evidence |
| --- | --- |
| `0x00479630 Geometry__RaySphereEntryDistance` | Wave387 ray/sphere entry-distance helper remained coherent. |
| `0x00479770 Geometry__DistanceOutsideAabb` | Wave387 AABB overhang-distance helper remained coherent. |
| `0x0047e290 CGuide__ctor_base` | Wave359 guide base constructor evidence remained coherent across guide-owner callers. |
| `0x0047eb80 CStaticShadows__SampleShadowHeightBilinear` | Wave394 static-shadow height sampler remained the central terrain-height call target; fresh xrefs exposed orphan caller islands. |
| `0x0047ef20 CHeightField__RecomputeGridExtentsAndHeightRange` | Wave396 heightfield range/extents owner correction remained coherent. |

Recovered boundary anchors:

| Address | Evidence |
| --- | --- |
| `0x00448580 CDropshipAI__VFunc_09_00448580` | DATA ref `0x005db218` from CDropshipAI RTTI/vtable slot; samples global static-shadow heightfield `0x006fadc8` while advancing dropship AI state. |
| `0x00448930 CDropshipGuide__VFunc_03_00448930` | DATA ref `0x005db234` from CDropshipGuide RTTI/vtable slot; samples static-shadow height while steering / ground-height clamping guide movement. |
| `0x004dfaa0 VFuncSlot_09_004dfaa0` | DATA ref `0x005dfe44`; owner kept generic because the slot owner is unresolved; body samples static-shadow height and may dispatch/create pickup-style state. |
| `0x004e9600 CSquadNormal__VFunc_20_004e9600` | DATA ref `0x005df144` from CNormalSquad RTTI/vtable slot; forwards position and reclamps member heights against static-shadow terrain. |
| `0x004e96f0 CSquadNormal__VFunc_21_004e96f0` | DATA ref `0x005df148` from CNormalSquad RTTI/vtable slot; forwards orientation and recomputes member offsets / height clamps. |
| `0x004e9f00 CSquadNormal__VFunc_52_004e9f00` | DATA ref `0x005df1c4` from CNormalSquad RTTI/vtable slot; render/debug body that samples static-shadow height and draws beam/debug-volume helpers. |
| `0x004eaae0 CRelaxedSquad__VFunc_07_004eaae0` | DATA ref `0x005e3a9c` in relaxed-squad table area; samples static-shadow height before debug-volume / overlay rendering. |
| `0x004f0e40 CTentacle__VFunc_22_004f0e40` | DATA ref `0x005e3ff4` from CTentacle RTTI/vtable slot; activation/effect path samples static-shadow height and updates particle-link coordinates. |
| `0x0050a3a0 CWingmanStart__VFunc_09_0050a3a0` | DATA ref `0x005dcb7c` from CWingmanStart RTTI/vtable slot; clamps init height and selects Tara/Billy fighter spawners by global state. |
| `0x00534ac0 ScriptCommand__SampleStaticShadowHeight_00534ac0` | DATA ref `0x00531270` in `ScriptCommandRegistry__InitBuiltins`; samples static-shadow height for a script value and returns an 8-byte CDataType scalar wrapper allocated from MissionScript.cpp line token `0x2e3`. |

Read-back evidence:

- Pre-review exports: 5 metadata rows, 5 tag rows, 127 xref rows, 423 body-instruction rows, and 5 decompile rows.
- Context exports: 6 metadata rows, 38 xref rows, 1115 body-instruction rows, and 6 decompile rows.
- Static-shadow no-function caller evidence: 29 xref callsites, 1421 narrow instruction rows, and 6989 wide instruction rows.
- Boundary candidate evidence: 17 candidate-entry xref rows, 384 pointer-table window rows, and 237 RTTI/base-candidate rows.
- Boundary creation dry/apply: dry reported `targets=10 created=0 would_create=10 already_exists=0 renamed=0 would_rename=0 failed=0`; apply reported `targets=10 created=10 would_create=0 already_exists=0 renamed=10 would_rename=0 failed=0`.
- Hardening dry/apply/final dry: dry reported `updated=0 skipped=10 signature_updated=10 comment_updated=10 tag_updated=10 missing=0 bad=0`; apply reported `updated=10 skipped=0 signature_updated=10 comment_updated=10 tag_updated=10 missing=0 bad=0`; final dry reported `updated=0 skipped=10 signature_updated=0 comment_updated=0 tag_updated=0 missing=0 bad=0`.
- Final exports: 15 metadata rows, 15 tag rows, 137 xref rows, 2569 body-instruction rows, and 15 decompile rows.
- Queue closure after refresh: `6233/6233 = 100.00%`, with 0 commentless functions, 0 exact-undefined signatures, and 0 `param_N` signatures.
- Re-audit progress after Wave1009: Wave911 focused `499/1408 = 35.44%`; expanded static surface `694/1488 = 46.64%`; Wave911 top-500 risk-ranked `403/500 = 80.60%`.
- Verified backup: `G:\GhidraBackups\BEA_20260531-155648_post_wave1009_geometry_guide_heightfield_spine_review_verified`, 19 files, 173935495 bytes, `DiffCount=0`, `HashDiffCount=0`.

What this proves:

- The ten recovered rows now exist as saved function objects in the loaded Ghidra database.
- The recovered rows have saved bounded names, signatures, comments, and `geometry-guide-heightfield-spine-review-wave1009` / `wave1009-readback-verified` tags.
- Static xref, instruction, decompile, RTTI/vtable, queue-refresh, and backup evidence support the saved boundary recovery and static-shadow caller classification.

What remains unproven:

- Runtime dropship, squad, tentacle, wingman, MissionScript, terrain, or shadow behavior.
- Exact source method names or exact source-body identity for the recovered vtable slots and script callback.
- Concrete object layouts beyond observed offsets.
- Full closure of every no-function static-shadow caller; jump-only / non-DATA-backed call islands remain deferred.
- BEA patching behavior.
- Rebuild parity.
