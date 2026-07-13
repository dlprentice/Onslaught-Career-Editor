# Ghidra IScript Object/Audio Wave584 Readiness Note

<!-- ghidra-full-reaudit-20260713:start -->
> **2026-07-13 semantic revalidation:** Historical record; `0x005362a0` comment correction. The original text below remains provenance rather than current semantic authority. Use the [closeout](../../reverse-engineering/binary-analysis/ghidra-full-reaudit-closeout-2026-07-13.md); exact records are in `reverse-engineering/binary-analysis/ghidra-full-reaudit-corrections-2026-07-13.json` and `reverse-engineering/binary-analysis/ghidra-targeted-revalidation-corrections-2026-07-13.json`.
<!-- ghidra-full-reaudit-20260713:end -->

Date: 2026-05-19
Status: static saved-Ghidra evidence only

Wave584 hardened 11 adjacent IScript object/audio command handlers at `0x00535670`, `0x005357b0`, `0x00535fa0`, `0x005362a0`, `0x005363e0`, `0x00536ca0`, `0x00537410`, `0x00537500`, `0x005375f0`, `0x005377e0`, and `0x005378e0`.

Saved rows:

| Address | Function |
| --- | --- |
| `0x00535670` | `IScript__GetThingName` |
| `0x005357b0` | `IScript__GetThingTypeName` |
| `0x00535fa0` | `IScript__Attack` |
| `0x005362a0` | `IScript__GetTextWidth` |
| `0x005363e0` | `IScript__GetPlayerBattleEngine` |
| `0x00536ca0` | `IScript__TriggerHitEffect` |
| `0x00537410` | `IScript__PlaySound` |
| `0x00537500` | `IScript__PlaySoundWithCallback` |
| `0x005375f0` | `IScript__PlaySoundWithFade` |
| `0x005377e0` | `IScript__PlaySoundWithPriority` |
| `0x005378e0` | `IScript__PlaySoundWithFadeAndPriority` |

What is proven:

- The saved functions are registered by `ScriptCommandRegistry__InitBuiltins`.
- Ghidra now records the script-context ABI shape for all 11 rows: `__thiscall` implicit `this` plus `script_args`, `unused_state`, and `out_result`; instruction read-back confirms `RET 0xc`.
- Post-save read-back verified 11 metadata rows, 11 tag rows, 11 xref rows, 4059 instruction rows, 11 decompile rows, and 64 vtable rows.
- The queue refresh reports `6093` total functions, `2963` commented, `3130` commentless, `1404` exact-undefined signatures, and `1117` `param_N` signatures.
- The next high-signal queue head is `0x00537fd0 CBoolDataType__ctor_like_00537fd0`.
- The live Ghidra project backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260519-091559_post_wave584_iscript_object_audio_verified` with 19 files, 160664455 bytes, `DiffCount=0`, and manifest hash `e2d334693fa1ddec75eb52efad37d966384ac44f6fd560d86f900a423a710b08`.

What is not proven:

- runtime mission-script behavior remains unproven.
- Script corpus coverage remains separate evidence.
- Exact command descriptor layout and exact audio/message/fade semantics remain unproven.
- BEA patching, gameplay behavior, and rebuild parity remain unproven.
