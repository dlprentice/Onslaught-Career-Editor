# Ghidra CVBufTexture Cursor Wave867 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `cvbuftexture-cursor-wave867`

Wave867 CVBufTexture cursor saved comments, tags, and corrected signatures for three adjacent vertex-buffer cursor helpers from `0x005501d0 CVBufTexture__GetVertexWriteCursorPlusOne` through `0x00550200 CVBufTexture__GetVertexPtrAt`. The pass made no renames, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Saved signature | Evidence |
| --- | --- | --- |
| `0x005501d0 CVBufTexture__GetVertexWriteCursorPlusOne` | `int __thiscall CVBufTexture__GetVertexWriteCursorPlusOne(void * this)` | Returns cached cursor field `this+0x19c` plus one; xrefs `0x004c970f` and `0x004ca24d` use the value as the next sprite vertex index. |
| `0x005501e0 CVBufTexture__ReserveOneVertex` | `void __thiscall CVBufTexture__ReserveOneVertex(void * this, void * vertex_src)` | `RET 0x4`; loads backing CVBufTexture from `this+0x198`, calls `CVBufTexture__AddVertices(vertex_src, 1)`, and stores the returned starting index at `this+0x19c`. |
| `0x00550200 CVBufTexture__GetVertexPtrAt` | `void __thiscall CVBufTexture__GetVertexPtrAt(void * this, int vertex_count, void * * out_vertex_ptr, int * out_start_index)` | `RET 0xc` plus ECX use proves this is a member helper, not a standalone stdcall; forwards to `CVBufTexture__GetVertexPtr(out_vertex_ptr, vertex_count)` and writes the returned starting index through `out_start_index`. |

Read-back evidence:

- `ApplyCVBufTextureCursorWave867.java dry`: `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=0 missing=0 bad=0`
- `ApplyCVBufTextureCursorWave867.java apply`: `updated=3 skipped=0 renamed=0 would_rename=0 signature_updated=3 comment_only_updated=0 missing=0 bad=0`
- `ApplyCVBufTextureCursorWave867.java final dry`: `updated=0 skipped=3 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Apply log contains three `READBACK_OK` rows and `REPORT: Save succeeded`.
- Post exports verified `3` metadata rows, `3` tag rows, `6` xref rows, `22` instruction rows, and `3` decompile rows.
- Callsite export verified `270` instruction rows around six xrefs, including CPDSimpleSprite callsites `0x004c767b` and `0x004c8a09` that push `vertex_count` 4 plus stack-local output pointers.
- Queue after Wave867: `6105` total functions, `5823` commented, `282` commentless, `0` exact-undefined signatures, `0` `param_N`, comment-backed proxy `5823/6105 = 95.38%`, strict clean-signature proxy `5823/6105 = 95.38%`.
- Next raw commentless row: `0x005508a0 CDXEngine__ClearMatrixBlock`; commentless high-signal, signature, and name-confidence queues remain empty.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-165414_post_wave867_cvbuftexture_cursor_verified`, `19` files, `172362631` bytes, `DiffCount=0`.

What this proves:

- The three target rows exist in the saved Ghidra project.
- The saved signatures use member-helper calling conventions and pointer-shaped output parameters matching static callsite/body evidence.
- The saved comments and tags include `cvbuftexture-cursor-wave867` and `wave867-readback-verified`.
- These helpers are low local-evidence-density but important connective renderer infrastructure, not low-importance code.

What remains unproven:

- Exact CVBufTexture field names and layouts.
- Exact sprite-particle source-body identity.
- Runtime rendering behavior.
- BEA patching behavior.
- Rebuild parity.
