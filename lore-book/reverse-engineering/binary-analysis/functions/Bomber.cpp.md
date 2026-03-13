# Bomber.cpp Cross-Reference Analysis

**Date:** 2025-12-15
**Analyst:** RE Agent (Ghidra MCP)
**String Address:** 0x00623a78
**String Value:** `C:\dev\ONSLAUGHT2\Bomber.cpp`

## Summary

Found **4 cross-references** to the Bomber.cpp debug path string:
- 2 in exception unwinding handlers (recognized functions)
- 2 in C++ constructor code (unrecognized by Ghidra as functions)

**Key Finding:** The Bomber class source code is not present in the current public source snapshot. This represents missing functionality that exists in the retail binary but was not included in the available reference code.

## Cross-Reference Details

### 1. Unwind@005d1400 (Exception Handler)

**Address:** 0x005d1400
**Type:** Exception unwinding function
**Reference:** 0x005d1402 (offset +0x2)

**Decompiled Code:**
```c
void Unwind_005d1400(void)
{
  int unaff_EBP;

  // Frees the partially-constructed object on exception.
  // Note: call sites often also push (alloc tag / file / line) for debug xrefs.
  OID__FreeObject_Callback(*(undefined4 *)(unaff_EBP + 4));
  return;
}
```

**Analysis:**
- Exception handler for line 17 (0x11 hex) of Bomber.cpp
- Calls `OID__FreeObject_Callback` (wrapper around `OID__FreeObject`) to clean up on failure
- Standard MSVC exception unwinding pattern

**Suggested Name:** `CBomber__UnwindHandler_Line17`

---

### 2. Unwind@005d1416 (Exception Handler)

**Address:** 0x005d1416
**Type:** Exception unwinding function
**Reference:** 0x005d1418 (offset +0x2)

**Decompiled Code:**
```c
void Unwind_005d1416(void)
{
  int unaff_EBP;

  // Frees the partially-constructed object on exception.
  // Note: call sites often also push (alloc tag / file / line) for debug xrefs.
  OID__FreeObject_Callback(*(undefined4 *)(unaff_EBP + 4));
  return;
}
```

**Analysis:**
- Exception handler for line 22 (0x16 hex) of Bomber.cpp
- Same pattern as handler 1, different line number
- Paired with different constructor/destructor

**Suggested Name:** `CBomber__UnwindHandler_Line22`

---

### 3. Constructor Code @ 0x004160e4 (NOT A FUNCTION)

**Address:** 0x004160e4
**Type:** C++ constructor inline code
**Context:** Between FUN_00415d70 (ends 0x00415d86) and FUN_004161a0

**Disassembly Context:**
```asm
004160e0: FE FF          ???
004160e2: 6A 11          PUSH 0x11        ; Line 17 decimal
004160e4: 68 78 3A 62 00 PUSH 0x623a78    ; "C:\dev\ONSLAUGHT2\Bomber.cpp"
004160e9: 6A 17          PUSH 0x17        ; Unknown parameter
004160eb: 6A 30          PUSH 0x30        ; Unknown parameter
004160ed: B9 F0 3D 9C 00 MOV ECX, 0x9c3df0 ; Object pointer?
```

**Analysis:**
- This is NOT a standalone function - Ghidra failed to identify the function boundary
- Part of C++ constructor exception handling setup (MSVC-style)
- Pushes line number (17) and source file for debugging/exception context
- MOV ECX suggests this-pointer setup for a method call
- The 0x9c3df0 address may be a static/global CBomber instance

**Suggested Name:** `CBomber__Constructor_1` (if function were defined)

---

### 4. Constructor Code @ 0x0041611d (NOT A FUNCTION)

**Address:** 0x0041611d
**Type:** C++ constructor inline code
**Context:** Same region as reference #3

**Disassembly Context:**
```asm
00416117: EB 02          JMP ...
00416119: 33 FF          XOR EDI,EDI
0041611b: 6A 12          PUSH 0x12        ; Line 18 decimal
0041611d: 68 78 3A 62 00 PUSH 0x623a78    ; "C:\dev\ONSLAUGHT2\Bomber.cpp"
00416122: 6A 16          PUSH 0x16        ; Unknown parameter
00416124: 6A 64          PUSH 0x64        ; Unknown parameter (100 decimal)
00416126: B9 F0 3D 9C 00 MOV ECX, 0x9c3df0 ; Same object pointer
```

**Analysis:**
- Second constructor or initialization path for same CBomber object
- Line 18 of Bomber.cpp (0x12 hex)
- Same object pointer (0x9c3df0) as constructor #1
- Different parameters (0x16, 0x64) vs (0x17, 0x30)
- May be different constructor overload or initialization stage

**Suggested Name:** `CBomber__Constructor_2` (if function were defined)

---

## CBomber Class Analysis

### What We Know:

1. **Class Name:** CBomber (inferred from file name pattern)
2. **Source File:** Bomber.cpp (NOT in Stuart's source dump)
3. **Instance Location:** Global/static at 0x9c3df0
4. **Constructor Complexity:** Multi-stage initialization with exception handling
5. **Lines Referenced:** 17, 18, 22 (suggests small file, <30 lines?)

### What We Don't Know:

- Class purpose/functionality (enemy bomber aircraft? player bomber weapon?)
- Member variables and size
- Full method list
- Inheritance hierarchy
- Why it's missing from source code

### Hypotheses:

**Hypothesis 1: Console Port Addition**
- CBomber might be retail/porting-layer-only code (not present in Stuart's internal source snapshot)
- Not in Stuart's internal build source
- Explains why source is missing

**Hypothesis 2: Proprietary/Licensed Code**
- Could be third-party or middleware component
- Stuart may not have rights to share source
- Would explain selective omission

**Hypothesis 3: Gameplay Feature**
- Could be related to bomber aircraft enemies
- Or bomber-style gameplay mechanics
- Worth checking game levels for bomber units

---

## OID__FreeObject_Callback - Cleanup Helper

**Address:** 0x00449d40
**Called By:** Both Unwind handlers
**Signature:**
```c
void OID__FreeObject_Callback(void *ptr);
```

**Behavior:** Thin wrapper around `OID__FreeObject(ptr)`. Unwind stubs often carry debug context (alloc tag / file / line) on the stack, but this helper ultimately just frees the pointer.

---

## Next Steps

1. **Search for 0x9c3df0 references** - Find all code accessing this global CBomber instance
2. **Search for "bomber" strings** - Look for in-game references, weapon names, enemy types
3. **Check vtable at 0x5D8DBC** - Referenced in constructor code, may reveal class hierarchy
4. **RE the full constructor** - Define proper function boundaries for the constructor code
5. **Ask Stuart** - Inquire about missing Bomber.cpp in source dump

---

## Summary Table

| Address | Type | Line | Function Name (Current) | Suggested Name |
|---------|------|------|-------------------------|----------------|
| 0x005d1400 | Unwind Function | 17 | `Unwind@005d1400` | `CBomber__UnwindHandler_Line17` |
| 0x005d1416 | Unwind Function | 22 | `Unwind@005d1416` | `CBomber__UnwindHandler_Line22` |
| 0x004160e4 | Constructor Code | 17 | *(not a function)* | `CBomber__Constructor_1` |
| 0x0041611d | Constructor Code | 18 | *(not a function)* | `CBomber__Constructor_2` |

**Total References:** 4
**Recognized Functions:** 2
**Unrecognized Code:** 2
**Global Instance:** 0x9c3df0
**Vtable Pointer:** 0x5D8DBC (inferred)
