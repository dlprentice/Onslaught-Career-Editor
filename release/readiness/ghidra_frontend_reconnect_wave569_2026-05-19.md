# Ghidra Frontend/Reconnect Wave569 Readiness Note

Date: 2026-05-19
Status: PASS

## Scope

Wave569 hardened four saved Ghidra rows:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x00527960` | `void __thiscall CFEPMultiplayerStart__SetCurrentSelection(void * this, int selection_state)` | Stores `selection_state` at `this+0x08`; `RET 0x4` confirms one stack argument after `this`. |
| `0x00527c50` | `bool __thiscall CFrontEnd__AdvanceStateAndRelinquishControl(void * this, void * controller, int caller_state_token)` | Advances frontend handoff state, relinquishes `controller` on state `3`, and preserves the real `RET 0x8` consumed-but-unread second stack argument. |
| `0x00527c90` | `void * __thiscall CReconnectInterface__ctor(void * this, void * tweak_name, int default_index_one_based)` | Constructor-style CTweak-derived helper; installs vtable `0x005e4a80` and stores `default_index_one_based - 1`. |
| `0x00527d00` | `void __thiscall CReconnectInterface__VFunc_07_00527d00(void * this, float tweak_value)` | Rounds one float stack argument into `this+0x0c`, marks `this+0x10`, and is referenced by vtable/data slot `0x005e4a80` plus `-landscape0/-landscape1/-landscape2` CLI parse callsites. |

No `source-parity` tag was applied. This tranche is bounded to retail binary evidence.

## Verification

- Dry pass: `updated=0 skipped=4 renamed=0 would_rename=0 missing=0 bad=0`
- Apply pass: `updated=4 skipped=0 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Final dry: `updated=0 skipped=4 renamed=0 would_rename=0 missing=0 bad=0`, `REPORT: Save succeeded`
- Post exports: `4` metadata rows, `4` tag rows, `17` xref rows, `404` target instruction rows, `4` target decompiles, and `4` vtable-slot rows
- Queue refresh: `6093` total functions, `2832` commented, `3261` commentless, `1494` exact-undefined signatures, `1163` `param_N` signatures
- Comment-backed proxy: `2832 / 6093 = 46.48%`
- Focused probe: `py -3 tools\ghidra_frontend_reconnect_wave569_probe.py --check` PASS
- NPM wrapper: `cmd.exe /c npm run test:ghidra-frontend-reconnect-wave569` PASS
- Backup: `[maintainer-local-ghidra-backup-root]\BEA_20260518-231808_post_wave569_frontend_reconnect_verified`
- Backup verification: `19` files, `160041863` bytes, source/destination manifest hash `3D8F0AC26DA7EEE7F71D7F9357A3EC2B4B818C463AC10482AD107FF98E9F5DD1`

## Limits

This is saved static Ghidra evidence only. No runtime behavior was claimed. Runtime frontend/reconnect behavior, exact state enum/layout, exact class/source identity, BEA launch, game patching, and rebuild parity remain unproven.
