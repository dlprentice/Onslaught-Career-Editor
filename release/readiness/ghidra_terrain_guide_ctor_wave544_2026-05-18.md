# Ghidra TerrainGuide Constructor Wave544 Readiness Note

Date: 2026-05-18

## Scope

Wave544 saved a static Ghidra name/signature/comment/tag hardening pass for one TerrainGuide constructor wrapper and refreshed one stale caller comment that still referenced the old constructor-like symbol:

| Address | Saved name | Saved signature |
| --- | --- | --- |
| `0x004f1ec0` | `CTerrainGuide__ctor` | `void * __thiscall CTerrainGuide__ctor(void * this, void * guideOwner)` |

The constructor forwards `guideOwner` to `CGuide__ctor_base`, installs vtable `0x005df4ec`, returns `this`, and ends with `RET 0x4`, proving one explicit owner/guideOwner stack argument after the ECX receiver. The known callers are GillM, WarspiteDome, Cannon, and Sentinel init paths that allocate a pool-`0x17` `0x20`-byte helper object and store the returned pointer at owner offset `+0x208`.

## Evidence

- Apply script: `tools/ApplyTerrainGuideCtorWave544.java`.
- Caller-comment drift script: `tools/ApplyTerrainGuideCallerCommentWave544.java`.
- Probe: `tools/ghidra_terrain_guide_ctor_wave544_probe.py`.
- Read-back artifacts: `subagents/ghidra-static-reaudit/wave544-cterrainguide-ctor-004f1ec0/`.
- Constructor dry run: `updated=0 skipped=1 renamed=0 would_rename=1 missing=0 bad=0`.
- Constructor apply: `updated=1 skipped=0 renamed=1 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Constructor verify dry: `updated=0 skipped=1 renamed=0 would_rename=0 missing=0 bad=0`.
- GillM caller-comment dry/apply/verify refreshed `CGillM__InitTerrainGuideComponent` so it now names `CTerrainGuide__ctor`; apply reported `updated=1 skipped=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Post read-back verified `1` metadata row, `1` tag row, `4` constructor xref rows, `225` target instruction rows, `1` target decompile export, `4` caller decompile exports, and `8` vtable rows for `0x005df4ec`.
- Focused probe: `py -3 tools\ghidra_terrain_guide_ctor_wave544_probe.py --check` PASS.
- Npm wrapper: `cmd.exe /c npm run test:ghidra-terrain-guide-ctor-wave544` PASS.
- Queue refresh: `py -3 tools\ghidra_static_reaudit_queue_probe.py --check --json` PASS after refreshing the live quality snapshot.
- Backup: `G:\GhidraBackups\BEA_20260518-102611_post_wave544_terrain_guide_ctor_verified`, `19` files, `159320967` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

## Queue Snapshot

Fresh queue telemetry after Wave544:

| Metric | Value |
| --- | ---: |
| Function objects | `6089` |
| Commented functions | `2650` |
| Commentless functions | `3439` |
| Exact-undefined signatures | `1535` |
| `param_N` signatures | `1291` |
| Comment-backed proxy | `2650/6089 = 43.52%` |
| Strict comment-plus-clean-signature proxy | `2596/6089 = 42.63%` |

This is telemetry only, not a completion milestone.

## Not Proven

- Exact `CTerrainGuide` source class identity.
- Concrete guide object layout or all vtable slot semantics.
- Runtime terrain-guidance behavior.
- Source-body parity, BEA launch, executable patching, and rebuild parity.
