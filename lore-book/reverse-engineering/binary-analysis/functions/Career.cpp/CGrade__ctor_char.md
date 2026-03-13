# CGrade__ctor_char

> Address: `0x00420ab0`
>
> Source: `references/Onslaught/Career.h` (`CGrade(char g) : grade(g) {}`)

## Status
- **Named in Ghidra:** Yes
- **Signature Set:** Yes
- **Verified vs Source:** Yes

## Signature
```c
char * CGrade__ctor_char(void * this, char grade);
```

## Behavior
- Writes `grade` into the single-byte `CGrade::grade` field (`*(char *)this = grade`).
- Returns `this` pointer.

## Notes
- This tiny helper is heavily used by `CCareer__UpdateGoodieStates` (`0x0041c470`) when constructing temporary grade-comparison operands.
- Decompile/mutation was validated via direct HTTP plugin route after MCP bridge transport closed.

## Related
- [CGrade__operator_gte](CGrade__operator_gte.md)
- [CCareer__UpdateGoodieStates](CCareer__UpdateGoodieStates.md)
