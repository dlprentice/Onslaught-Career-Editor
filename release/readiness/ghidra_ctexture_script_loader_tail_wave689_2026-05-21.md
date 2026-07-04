# Ghidra CTexture Script Loader Tail Wave689 Readiness Note

Date: 2026-05-21

Wave689 CTexture script loader tail saved six script-loader, query-stub, query-interface, and memory-write-stream rows after serialized Ghidra dry/apply/final-dry read-back.

Tag anchors:

- `ctexture-script-loader-tail-wave689`
- `wave689-readback-verified`

Function anchors:

- `0x005907d9 CTexture__LoadScriptAndDispatchByVersion`
- `0x00590d3d CTexture__CreateMemoryWriteStream`
- Next queue head: `0x00590e10 CDXTexture__FillInputBufferFromSource`

## Saved Scope

| Address | Saved signature | Static evidence |
| --- | --- | --- |
| `0x005907d9` | `int __thiscall CTexture__LoadScriptAndDispatchByVersion(void * this, void * preprocessor_context, uint compile_flags, uint assembly_fragment_version, void * out_stream_slot, void * unused_context)` | Resets parser compile-context slots, optionally creates parser-state symbol tables for assembly fragments, reads/normalizes shader-version tokens, maps observed version constants to the internal version index, optionally creates the D3D9 shader validator callback, runs yacc parsing, finalizes symbol/debug chunks, writes the output memory stream, releases the validator, and pops the preprocessor frame. |
| `0x00590c4a` | `void __fastcall CTexture__SetQueryStubVtableAndReleaseChild(void * query_stub)` | Sets the query-stub vtable to `PTR_CDXTexture__QueryInterfaceByGuid_005ed3dc` and frees the child/callback pointer at `query_stub+0x0c`. |
| `0x00590cc2` | `void * __thiscall CTexture__Dtor_QueryStub_DeleteOnFlag(void * this, uint delete_flags)` | Scalar-deleting destructor wrapper for the query/memory-stream stub; calls the query-stub cleanup helper, frees `this` when `delete_flags` bit 0 is set, returns `this`, and ends with `RET 0x4`. |
| `0x00590cde` | `int __stdcall CDXTexture__QueryInterfaceByGuid(void * object_stub, void * requested_guid, void * out_interface_slot)` | Clears the output slot, compares the requested GUID against two observed 16-byte constants, returns `E_NOINTERFACE` on mismatch, otherwise writes the object pointer and calls the vtable AddRef-like slot at `+0x04`. |
| `0x00590d25` | `void __fastcall CTexture__InitMemoryWriteStream(void * memory_write_stream)` | Initializes a `0x10`-byte memory-write stream/query stub by clearing slots `+0x08/+0x0c`, installing the query-interface vtable, and setting the refcount-like field at `+0x04` to `1`. |
| `0x00590d3d` | `int __stdcall CTexture__CreateMemoryWriteStream(int initial_byte_count, void * out_stream_slot)` | Validates the output slot, allocates and initializes a memory-write stream/query stub, calls vtable `+0x18` with the initial byte count, releases through vtable `+0x14` on setup failure, and writes the stream pointer on success. |

## Evidence

`ApplyCTextureScriptLoaderTailWave689.java` dry/apply/final dry reported:

- Dry: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=6 varargs=0 missing=0 bad=0`
- Apply: `updated=6 skipped=0 renamed=0 would_rename=0 signature_updated=6 varargs=0 missing=0 bad=0`
- Final dry: `updated=0 skipped=6 renamed=0 would_rename=0 signature_updated=0 varargs=0 missing=0 bad=0`

All three passes reported `REPORT: Save succeeded`. Post exports verified `6` metadata rows, `6` tag rows, `7` xref rows, `546` instruction rows, and `6` clean decompile rows. Pre-state exports covered the same six rows, and candidate exports covered `13` adjacent script-loader/query-stub/memory-stream/JPEG rows with `17` xref rows, `1053` instruction rows, and `13` clean decompile rows before tranche selection.

Post-Wave689 queue telemetry is `6098` total functions, `3945` commented, `2153` commentless, `1216` exact-undefined signatures, and `376` `param_N` signatures. Comment-backed proxy is `3945/6098 = 64.69%`; strict clean-signature proxy is `3895/6098 = 63.87%`.

Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260521-120555_post_wave689_ctexture_script_loader_tail_verified`, `19` files, `164760455` bytes, `DiffCount=0`.

## Boundaries

This wave proves saved static Ghidra name/signature/comment/tag evidence only. Exact compile flag enum, shader-version enum, parser-context layout, D3D validator ABI, output stream contract, stub/stream object layouts, COM contract completeness, runtime texture compiler behavior, BEA patching, and rebuild parity remain unproven.

Probe: `cmd.exe /c npm run test:ghidra-ctexture-script-loader-tail-wave689`
