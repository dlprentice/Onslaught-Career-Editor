# CTexture__FindTexture_Unwind

> Address: 0x005d5120
> Source: texture.cpp (debug path at 0x00632ef0)

## Summary
Exception unwind handler for CTexture__FindTexture. Called during stack unwinding when an exception occurs within the FindTexture function.

## Decompiled Code
```cpp
void CTexture__FindTexture_Unwind(void)
{
  int unaff_EBP;

  OID__FreeObject_Callback(*(undefined4 *)(unaff_EBP + -0x210));
  return;
}
```

## Purpose

This is an automatically generated exception handling function (SEH - Structured Exception Handling) for the `CTexture__FindTexture` function. When an exception is thrown during texture loading, this handler is called to properly clean up any partially constructed objects.

## Parameters

The function accesses the stack frame of `CTexture__FindTexture` via the unaffected EBP register:
- `unaff_EBP + -0x210`: Points to a local variable in the parent function (likely a texture object being constructed)

## Called Functions

| Address | Name | Purpose |
|---------|------|---------|
| 0x00449d40 | OID__FreeObject_Callback | Cleanup/deallocation callback wrapper (calls `OID__FreeObject`) |

Call sites often push additional debug context (alloc tag / file / line) for consistency with allocation sites, but this helper ultimately frees the pointer.

## Technical Details

**Exception Handling Chain**:
In `CTexture__FindTexture`, we see:
```cpp
local_4 = 0xffffffff;
puStack_8 = &LAB_005d513c;  // Exception handler registration
local_c = ExceptionList;
ExceptionList = &local_c;
```

The address `LAB_005d513c` is near `CTexture__FindTexture_Unwind` (0x005d5120), suggesting they are part of the same exception handling block. When `local_4` is set to different values (0, 1, 0xffffffff), it indicates the current state of construction, allowing the unwind handler to know what needs cleanup.

## Related
- Parent function: [CTexture__FindTexture](CTexture__FindTexture.md) at 0x004f27f0
- Parent: [_index.md](_index.md)
