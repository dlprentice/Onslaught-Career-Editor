# CTexture__FindTexture

Source File: retained texture.cpp coordinate mapping | Binary: BEA.exe (earlier analysis, not remeasured by this callee rename)

Status: active function reference; retained evidence limits apply
Summary: existing function analysis with current CDebugLog callee naming.

Last updated: 2026-09-19 (logger callee names; earlier measurement limits retained)

> Address: 0x004f27f0
> Source: texture.cpp (debug path at 0x00632ef0)

## Summary
Main texture lookup function. Searches the global texture cache by name/type/mipmap requirement and loads textures on demand if not found. Wave513 hardened the saved Ghidra signature/comment on 2026-05-17; `load_arg` and `load_flags` are intentionally conservative names for arguments forwarded to the texture load vtable slot.

## Signature
```cpp
void * CTexture__FindTexture(
    char* name,             // Texture name to find
    int texture_type,       // Texture type/format (0 = any)
    int load_arg,           // Forwarded to load vtable slot +0x14
    int required_mip_count, // Required mipmap count (-1 = any)
    int allow_fallback,     // If true, return fallback texture on failure
    int load_flags          // Forwarded to load vtable slot +0x14
);
```

## Wave513 Evidence Boundary

The saved comment/signature are static retail evidence. The body walks `DAT_0083d9b0`, compares names with `stricmp`, accepts `texture_type == 0` as wildcard, accepts `required_mip_count == -1` as wildcard, allocates a `0x158`-byte `CTexture` from `texture.cpp` line `0x98` on a miss, calls `CTexture__ctor`, forwards the load arguments to vtable slot `+0x14`, and returns fallback `DAT_0083d9b4` when load fails and `allow_fallback` is set.

Not proven: forwarded loader argument semantics, exact CTexture layout beyond observed fields, runtime rendering behavior, BEA launch behavior, game patching, and rebuild parity.

## Decompiler listing
*Decompiler listing removed from the public tree (private RE archive: `scrubbed-passages/reverse-engineering/binary-analysis/functions/texture.cpp/CTexture__FindTexture.md`, block 1).*

## Algorithm

1. **Search texture cache**: Iterate linked list starting at `DAT_0083d9b0`
2. **Match criteria**:
   - Name must match (via string compare)
   - Texture type must match (or param_2 == 0 for any)
   - Mipmap count must match (or param_4 == -1 for any)
3. **On cache hit**: Increment reference count and return
4. **On cache miss**:
   - Log warning message
   - Allocate 344 bytes for new CTexture
   - Call constructor
   - Call virtual load method
   - If load fails and useFallback is set, return default texture

## Global Variables Used

| Address | Name | Purpose |
|---------|------|---------|
| 0x0083d9b0 | g_pTextureListHead | Head of texture linked list |
| 0x0083d9b4 | g_pDefaultTexture | Fallback texture |
| 0x0083d9b8 | g_bDebugOutput | Enable debug logging |
| 0x00662f3c | g_textureMode1 | Texture loading mode flag |
| 0x00662dd4 | g_textureMode2 | Another texture mode flag |

## CTexture Field Offsets Used

| Offset | Field | Purpose |
|--------|-------|---------|
| 0x00 | vtable | Virtual function table |
| 0x08 | name[128] | Texture name string |
| 0x28 (0xA0) | pNext | Next texture in linked list |
| 0x29 (0xA4) | refCount | Reference count |
| 0x2a (0xA8) | type | Texture type/format |
| 0x52 (0x148) | mipmapCount | Number of mipmaps |

## Cross-References

**Called by**: 248 locations throughout the codebase
- Model loading
- UI/HUD rendering
- Effects system
- Level loading

**Calls**:
- stricmp (0x00568390, was `FUN_00568390`)
- FatalError__ExitWithLocalizedPrefix_A (Wave998 no-return fatal texture/resource failure path)
- sprintf (0x0055de9b, was `FUN_0055de9b`)
- DebugTrace (debug output)
- OID__AllocObject (memory allocation)
- CTexture__ctor (constructor)
- CTexture__Release (cleanup)
- CDebugLog__Printf (`FUN_00441740`) (error logging)

## Related
- Unwind handler: [CTexture__FindTexture_Unwind](CTexture__FindTexture_Unwind.md) at 0x005d5120
- Constructor: CTexture__ctor at 0x00556cc0
- Parent: [retained function index](../_index.md)
