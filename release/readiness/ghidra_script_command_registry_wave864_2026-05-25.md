# Ghidra Script Command Registry Wave864 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `script-command-registry-wave864`

Wave864 script command registry saved the comment, tags, and `void __cdecl ScriptCommandRegistry__InitBuiltins(void)` signature for `0x0052ff30 ScriptCommandRegistry__InitBuiltins`. The pass made no renames, made no function-boundary changes, and made no executable-byte changes.

Representative anchors:

| Address | Evidence |
| --- | --- |
| `0x0052ff30 ScriptCommandRegistry__InitBuiltins` | No-argument MissionScript built-in command registry initializer reached from adjacent xref row `0x0052ff20`. The saved body writes 144 contiguous 0x40-byte command descriptor records from `0x0064ce50` through `0x0064f210`. |
| Name fields | Name assignments run from `s_FollowWaypointWait_0064fa14` to `s_IsOverWater_0064f234` and include `PostEvent`, `PlaySample`, `GetThingRef`, `GetVectorLength` / `Magnitude`, `Goto3PointPanCamera`, `SetGoodieState`, `SetSlotSave`, `SetStealth`, and `ToggleCockpit`. |
| Handler fields | The table stores named handlers such as `IScript__ScheduleEvent`, `IScript__IsFriendly`, `IScript__PlaySound`, `IScript__Create3PointPanCamera`, `IScript__SetGoodieState`, and `IScript__SetSlotSave`, plus many still-anonymous `LAB_...` handlers. |

Read-back evidence:

- `ApplyScriptCommandRegistryWave864.java dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`.
- `ApplyScriptCommandRegistryWave864.java apply`: `updated=1 skipped=0 renamed=0 would_rename=0 signature_updated=1 comment_only_updated=0 missing=0 bad=0`, with one `READBACK_OK` row and `REPORT: Save succeeded`.
- `ApplyScriptCommandRegistryWave864.java final dry`: `updated=0 skipped=1 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`.
- Post exports: 1 metadata row, 1 tag row, 1 xref row, 2456 bounded function-body instruction rows, and 1 decompile row.
- Queue after Wave864: 6105 total, 5810 commented, 295 commentless, 0 exact-undefined signatures, 0 `param_N`, comment-backed proxy `5810/6105 = 95.17%`, strict clean-signature proxy `5810/6105 = 95.17%`.
- Next raw commentless row: `0x0053df40 CDXEngine__RenderTexturedBeamQuad`.
- Commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-153044_post_wave864_script_command_registry_verified`, 19 files, 172264327 bytes, `DiffCount=0`.

What this proves:

- The target function row exists in the saved Ghidra project.
- The saved signature is `void __cdecl ScriptCommandRegistry__InitBuiltins(void)`.
- The saved function comment and tags include `script-command-registry-wave864` and `wave864-readback-verified`.
- The observed 144-record registry initializer body is static retail Ghidra evidence tied to post-mutation metadata, tag, xref, function-body instruction, and decompile exports.

What remains unproven:

- Exact command descriptor schema.
- Full command semantics.
- Runtime MissionScript dispatch or argument behavior.
- Source identity.
- BEA patching behavior.
- Rebuild parity.
