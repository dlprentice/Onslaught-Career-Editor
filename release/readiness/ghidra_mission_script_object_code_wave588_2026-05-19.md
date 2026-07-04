# Ghidra CMissionScriptObjectCode Wave588 Readiness Note

Date: 2026-05-19
Status: static saved-Ghidra evidence only

Wave588 hardened 6 adjacent `CMissionScriptObjectCode` / HUD script-field-block rows from `0x00539c80` through `0x00539f40`.

Saved rows:

| Address | Function |
| --- | --- |
| `0x00539c80` | `CMissionScriptObjectCode__CMissionScriptObjectCode` |
| `0x00539ca0` | `CMissionScriptObjectCode__LoadAsync` |
| `0x00539dc0` | `CMissionScriptObjectCode__StartLoadAsync` |
| `0x00539f00` | `CMissionScriptObjectCode__InitFields` |
| `0x00539f30` | `CMissionScriptObjectCode__ClearFields_Thunk` |
| `0x00539f40` | `CMissionScriptObjectCode__ClearFields` |

What is proven:

- Ghidra now records clean signatures, comments, and `mission-script-object-code-wave588` tags for all 6 rows.
- `0x00539f30` was corrected to `CMissionScriptObjectCode__ClearFields_Thunk`, a one-instruction jump thunk into `CMissionScriptObjectCode__ClearFields`.
- The constructor calls `CWaitingThread__ctor_base`, installs observed vtable pointer `0x005e4f5c`, clears the first path byte, and returns `this`.
- Vtable evidence is bounded: only slot `0x005e4f5c[0]` is proven for `CMissionScriptObjectCode__LoadAsync`; adjacent slot evidence crosses into `CDXBattleLine__scalar_deleting_dtor`, so the full vtable boundary remains unproven.
- `CMissionScriptObjectCode__LoadAsync` allocates/initializes a `CDXMemBuffer` for the stored path and clears the path byte on return.
- `CMissionScriptObjectCode__StartLoadAsync` has `RET 0x8` evidence for `filename` and `buffer_size`, copies the filename to the object path buffer, stores the buffer size, and starts the async worker through `CBinkOpenThread__StartAsync`.
- `CMissionScriptObjectCode__InitFields`, `CMissionScriptObjectCode__ClearFields_Thunk`, and `CMissionScriptObjectCode__ClearFields` are reached from `CHud__Init` / `CHud__ShutDown` and are kept as HUD script-field-block helpers rather than proof of a complete `CMissionScriptObjectCode` instance layout.
- Post-save read-back verified 6 metadata rows, 6 tag rows, 7 xref rows, 534 instruction rows, 6 decompile rows, and 64 vtable-slot rows.
- The queue refresh reports `6093` total functions, `3006` commented, `3087` commentless, `1359` exact-undefined signatures, and `1116` `param_N` signatures.
- The next high-signal queue head is `0x0053a050 CDXBattleLine__Constructor`.
- The live Ghidra project backup verified at `[maintainer-local-ghidra-backup-root]\BEA_20260519-111437_post_wave588_cmission_script_object_code_verified` with 19 files, 160893831 bytes, `DiffCount=0`, and manifest hash `ef5cc4c7c0c7f5ef102a1a748647b231a36c39b430e5379fb06a627992982841`.

What is not proven:

- runtime mission-script, Goodie loading, or HUD script behavior remains unproven.
- Exact `CMissionScriptObjectCode`, HUD field-block, async-cache, object-code-record, and file path ownership layouts remain unproven.
- Exact source identity remains unproven because no matching tracked Stuart source implementation body was found for this wave.
- The full vtable boundary remains unproven beyond observed slot `0x005e4f5c[0]`.
- BEA patching, gameplay behavior, and rebuild parity remain unproven.
