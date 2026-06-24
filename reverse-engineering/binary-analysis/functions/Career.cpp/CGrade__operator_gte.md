# CGrade__operator_gte

> Address: `0x00420ac0`
>
> Source: `references/Onslaught/Career.h` line 35 (`CGrade::operator >=`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes

## Signature
```c
bool CGrade__operator_gte(void * this, char right_grade);
```

## Behavior (source-parity)
Equivalent to Stuart's inline operator:
```cpp
if (grade == 'S') return TRUE;
if (right.grade == 'S') return FALSE;
return grade <= right.grade;
```

Interpretation:
- Treats `S` as strictly highest.
- Otherwise grade letters are compared lexicographically (`A` better than `B`, etc.).
- Used as "left grade is at least as good as right grade."

## Notes
- Called many times inside `CCareer__UpdateGoodieStates` to evaluate grade-gated goodies.
- Decompile/mutation was validated via direct HTTP plugin route after MCP bridge transport closed.

## Related
- [CGrade__ctor_char](CGrade__ctor_char.md)
- [CCareer__UpdateGoodieStates](CCareer__UpdateGoodieStates.md)
