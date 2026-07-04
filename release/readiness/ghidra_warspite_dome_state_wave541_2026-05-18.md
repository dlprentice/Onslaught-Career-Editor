# Ghidra WarspiteDome State-Tail Wave541 Readiness Note

Date: 2026-05-18

## Scope

Wave541 saved static Ghidra owner/signature/comment/tag corrections for four adjacent WarspiteDome state-tail helpers:

| Address | Saved name | Saved signature |
| --- | --- | --- |
| `0x00504a50` | `CWarspiteDome__UpdatePitchStateAndBlendTracks` | `void __fastcall CWarspiteDome__UpdatePitchStateAndBlendTracks(void * this)` |
| `0x00504b40` | `CWarspiteDome__UpdateTrackedPitchWithClamp` | `void __fastcall CWarspiteDome__UpdateTrackedPitchWithClamp(void * this)` |
| `0x00504cf0` | `CWarspiteDome__ShouldSkipUpdateByStateFlags` | `bool __fastcall CWarspiteDome__ShouldSkipUpdateByStateFlags(void * this)` |
| `0x00504d30` | `CWarspiteDome__IsTransitionAllowedByState` | `bool __fastcall CWarspiteDome__IsTransitionAllowedByState(void * this)` |

The important correction is owner cleanup: these functions previously carried stale `CVBufTexture__...` labels. Fresh vtable rows at `0x005e02c0` and `0x005e0380`, the adjacent `CWarspiteDome__Init` field setup from Wave536, and the current decompile/xref read-back support WarspiteDome state ownership instead.

## Evidence

- Apply script: `tools/ApplyWarspiteDomeStateTailWave541.java`.
- Probe: `tools/ghidra_warspite_dome_state_wave541_probe.py`.
- Read-back artifacts: `subagents/ghidra-static-reaudit/wave541-cvbuftexture-state-tail-00504a50/`.
- Dry run: `updated=0 skipped=4 renamed=0 would_rename=4 missing=0 bad=0`.
- Apply: `updated=4 skipped=0 renamed=4 would_rename=0 missing=0 bad=0`, with `REPORT: Save succeeded`.
- Verify dry: `updated=0 skipped=4 renamed=0 would_rename=0 missing=0 bad=0`.
- Post read-back verified `4` metadata rows, `4` tag rows, `4` xref rows, `724` instruction rows, `4` decompile exports, and `64` vtable rows.
- Focused probe: `py -3 tools\ghidra_warspite_dome_state_wave541_probe.py --check` PASS.
- Npm wrapper: `cmd.exe /c npm run test:ghidra-warspite-dome-state-wave541` PASS.
- Queue refresh: `py -3 tools\ghidra_static_reaudit_queue_probe.py --check --json` PASS after refreshing the live quality snapshot.
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260518-091727_post_wave541_warspite_dome_state_verified`, `19` files, `159320967` bytes, `MissingCount=0`, `ExtraCount=0`, `HashDiffCount=0`.

## Queue Snapshot

Fresh queue telemetry after Wave541:

| Metric | Value |
| --- | ---: |
| Function objects | `6089` |
| Commented functions | `2647` |
| Commentless functions | `3442` |
| Exact-undefined signatures | `1535` |
| `param_N` signatures | `1294` |
| Comment-backed proxy | `2647/6089 = 43.47%` |
| Strict comment-plus-clean-signature proxy | `2593/6089 = 42.58%` |

This is telemetry only, not a completion milestone.

## Not Proven

- Runtime WarspiteDome pitch, transition, linked-effect, or state-machine behavior.
- Exact `CWarspiteDome`, `CGroundUnit`, target/profile, effect-track, or state-array layouts beyond observed offsets.
- Exact source-body identity; source/init/vtable context is supporting evidence only here.
- BEA launch, executable patching, and rebuild parity.
