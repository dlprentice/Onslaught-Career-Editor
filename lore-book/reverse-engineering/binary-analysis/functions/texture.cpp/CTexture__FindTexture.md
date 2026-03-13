# CTexture__FindTexture

> Address: 0x004f27f0
> Source: texture.cpp (debug path at 0x00632ef0)

## Summary
Main texture lookup function. Searches the global texture cache by name and loads textures on demand if not found.

## Signature
```cpp
CTexture* CTexture__FindTexture(
    const char* name,       // param_1: Texture name to find
    int textureType,        // param_2: Texture type/format (0 = any)
    unknown param_3,        // param_3: Unknown
    int mipmapCount,        // param_4: Required mipmap count (-1 = any)
    int useFallback,        // param_5: If true, return fallback texture on failure
    unknown param_6         // param_6: Unknown (passed to load method)
);
```

## Decompiled Code
```cpp
int * CTexture__FindTexture(undefined4 param_1,int param_2,undefined4 param_3,int param_4,int param_5,
                  undefined4 param_6)
{
  void **ppvVar1;
  int iVar2;
  int *piVar3;
  undefined1 local_20c [256];
  undefined1 local_10c [256];
  void *local_c;
  undefined1 *puStack_8;
  undefined4 local_4;

  local_4 = 0xffffffff;
  puStack_8 = &LAB_005d513c;
  ppvVar1 = &local_c;
  local_c = ExceptionList;
  piVar3 = DAT_0083d9b0;  // Head of texture linked list
  do {
    ExceptionList = ppvVar1;
    if (piVar3 == (int *)0x0) {
      // Texture not found in cache - load it
      if ((DAT_00662f3c == '\0') && (DAT_00662dd4 == 0)) {
        FUN_0042c750(param_1,0xffffffff);
      }
      sprintf(local_10c,s_Warning___loading_texture__s_man_00632f10,param_1);
      DebugTrace(local_10c);  // Debug output

      // Allocate new texture (0x158 = 344 bytes)
      iVar2 = OID__AllocObject(0x158,2,s_C__dev_ONSLAUGHT2_texture_cpp_00632ef0,0x98);
      piVar3 = (int *)0x0;
      local_4 = 0;
      if (iVar2 != 0) {
        piVar3 = (int *)CTexture__ctor();  // Construct new texture
      }
      local_4 = 0xffffffff;

      // Call virtual load method (vtable + 0x14)
      iVar2 = (**(code **)(*piVar3 + 0x14))(param_1,param_2,param_3,param_4,param_6);

      if (iVar2 == 0) {
        // Load failed
        piVar3[0x29] = piVar3[0x29] + -1;  // Decrement ref count
        CTexture__Release();
        if (param_5 == 0) {
          piVar3 = (int *)0x0;
        }
        else {
          // Return fallback texture
          piVar3 = DAT_0083d9b4;
          if (DAT_0083d9b4 != (int *)0x0) {
            DAT_0083d9b4[0x29] = DAT_0083d9b4[0x29] + 1;
            piVar3 = DAT_0083d9b4;
          }
        }
      }
      else if (DAT_0083d9b8 != 0) {
        CConsole__Printf(&DAT_0066f580,s_Texture___s__not_found_in_level_r_00632ec0,param_1);
      }
      ExceptionList = local_c;
      return piVar3;
    }

    // Check if this texture matches
    iVar2 = stricmp(param_1,piVar3 + 2);  // String compare with texture name
    if ((iVar2 == 0) && ((param_2 == piVar3[0x2a] || (param_2 == 0)))) {
      iVar2 = piVar3[0x52];  // Mipmap count
      if (param_4 == -1) {
        if (iVar2 == -1) {
LAB_004f2958:
          piVar3[0x29] = piVar3[0x29] + 1;  // Increment ref count
          ExceptionList = local_c;
          return piVar3;
        }
      }
      else if (param_4 == iVar2) goto LAB_004f2958;

      // Mipmap mismatch warning
      sprintf(local_20c,s_Found_possible_match_for_texture_00632f38,param_1,iVar2,param_4);
      DebugTrace(local_20c);
    }
    piVar3 = (int *)piVar3[0x28];  // Next texture in list
    ppvVar1 = ExceptionList;
  } while( true );
}
```

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
- FUN_0042c750 (texture mode setup)
- sprintf (0x0055de9b, was `FUN_0055de9b`)
- DebugTrace (debug output)
- OID__AllocObject (memory allocation)
- CTexture__ctor (constructor)
- CTexture__Release (cleanup)
- CConsole__Printf (`FUN_00441740`) (error logging)

## Related
- Unwind handler: [CTexture__FindTexture_Unwind](CTexture__FindTexture_Unwind.md) at 0x005d5120
- Constructor: CTexture__ctor at 0x00556cc0
- Parent: [_index.md](_index.md)
