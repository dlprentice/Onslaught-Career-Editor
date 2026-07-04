# Ghidra CScriptEventNB Wave586 Readiness Note

Date: 2026-05-19
Status: static saved-Ghidra evidence only

Wave586 hardened 13 adjacent `CScriptEventNB` listener/event-manager rows from `0x00538470` through `0x00538c70`.

Saved rows:

| Address | Function |
| --- | --- |
| `0x00538470` | `CScriptEventNB__UpdateWaypointFollowing` |
| `0x005385e0` | `CScriptEventNB__HandleMessage` |
| `0x005386b0` | `CScriptEventNB__ScalarDeletingDestructor` |
| `0x005386d0` | `CScriptEventNB__Destructor` |
| `0x00538760` | `CScriptEventNB__Init` |
| `0x00538780` | `CScriptEventNB__ScalarDeletingDestructor2` |
| `0x005387b0` | `CScriptEventNB__ClearEventListeners` |
| `0x00538860` | `CScriptEventNB__CreateEventListener` |
| `0x005388d0` | `CScriptEventNB__DestroyAllEvents` |
| `0x00538950` | `CScriptEventNB__BaseDestructor` |
| `0x00538960` | `CScriptEventNB__RegisterEventListener` |
| `0x00538b70` | `CScriptEventNB__PostEvent` |
| `0x00538c70` | `CScriptEventNB__HandleEventMessage` |

What is proven:

- Ghidra now records clean signatures, comments, and `scripteventnb-wave586` tags for all 13 rows.
- ECX-only helpers were saved as `__fastcall`; one-stack-argument methods were saved as `__thiscall`; deleting destructor wrappers preserve their `delete_flags` byte.
- `CScriptEventNB__RegisterEventListener` is reached from `IScript__CallEvent0AndRegisterNestedListeners`, where the caller loads `ECX=&DAT_0089c590` and pushes `event_name_ref` plus `event_function`; `RET 0x8` confirms two explicit stack arguments.
- `CScriptEventNB__PostEvent` and `CScriptEventNB__HandleEventMessage` share the named-listener dispatch pattern and execute stored `CEventFunction` callbacks on matching event names.
- Post-save read-back verified 13 metadata rows, 13 tag rows, 18 xref rows, 5577 instruction rows, 13 decompile rows, and 72 vtable-slot rows.
- The queue refresh reports `6093` total functions, `2978` commented, `3115` commentless, `1387` exact-undefined signatures, and `1116` `param_N` signatures.
- The next high-signal queue head is `0x00538ea0 CScriptObjectCode__scalar_deleting_dtor`.
- The live Ghidra project backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260519-100558_post_wave586_scripteventnb_verified` with 19 files, 160729991 bytes, `DiffCount=0`, and manifest hash `7123094a4ecc3b49020cfd84ce6d4b55784547783fd0ba2d7e0e3a981e93bd3b`.

What is not proven:

- runtime mission-script behavior remains unproven.
- Script corpus coverage remains separate evidence.
- Exact `CScriptEventNB`, listener-entry, message, payload, waypoint, and monitor/base-class layouts remain unproven.
- Exact source identity remains unproven because the current Stuart source snapshot does not include the matching implementation body.
- BEA patching, gameplay behavior, and rebuild parity remain unproven.
