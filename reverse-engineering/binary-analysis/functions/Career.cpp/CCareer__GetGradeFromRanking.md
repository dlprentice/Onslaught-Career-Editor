# CCareer__GetGradeFromRanking

Status: active, bounded static and original-code contract; Ghidra ABI correction pending
Last updated: 2026-09-26
Summary: ranking produces a 16-bit character in AX; the saved full-int return is wrong, and negative ranking selects E.
Evidence: complete pristine bodies and 14 caller windows; 19 isolated original-code cases, not save/UI acceptance.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: `references/Onslaught/Career.cpp:1178` and `Career.h:150`, commit `5352a81cdb838b145a57f7febc5d9fc4b0129ebb` | Binary: pristine `BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

> Address: `0x00421470`

## Identity and pending metadata correction

The name is supported by the complete body `[0x00421470,0x004214dd)`,
109 bytes, SHA-256 `266785d836d9c0ec94904f7299c081b0f9d843b0126230a063d9e5ed6672e758`.
The current saved signature is `int __stdcall ...(float ranking)`; it is
incorrect. At `0x004214d4`, the function writes **AX only** with `MOV AX,[EAX]`,
then executes `RET 4` at `0x004214da`. Upper EAX bits from the conversion
helper's scratch pointer survive. A full integer return is not the grade.

All 14 direct callers set ECX to the career object `0x00660620` and supply one
four-byte ranking argument. The body itself never dereferences ECX; membership
is supported by those callers and the source's nonstatic declaration, not by
`RET 4` alone. Debriefing caller `0x00457d73` masks EAX with `0xffff` at
`0x00457d7e`; the rendering caller `0x00457936` also consumes the low word.

The supported interface is a 16-bit `WCHAR`/unsigned-short result in AX,
`__thiscall` with an automatic ECX receiver and one explicit float at entry
stack +4. No extra result pointer is present. A separate reviewed cohort must
apply that metadata; this document does not claim it is already live.

## Branches and arithmetic

With invalid floating-point exceptions masked:

1. Compare ranking against `1.0f` at `0x005d8568`. `TEST AH,0x40` selects
   character `S` for equality **or unordered comparison**.
2. Otherwise compare against zero at `0x005d856c`. Nonpositive ranking selects
   `E`. The former note's claim that `-1` displays no letter is disproved for
   this function; actual presentation is a separate caller/UI question.
3. For the remaining finite inputs, multiply by `4.0f` at `0x005d85bc`, store
   a binary64 argument and call retail `_floor` at `0x0055dfe7`. Convert its
   result to a signed qword with FISTP, use the low byte, and subtract it from
   byte `D`. There is no clamp above one. The source spells `floorf`; the
   emitted binary64 call is a lowering difference, not proof of source drift.
4. Form a two-byte string and call `Text__AsciiToWideScratch` at `0x004f7bf0`.
   Return its first word through AX. This helper advances a four-slot scratch
   ring and writes the widened string: the operation is not globally pure.
   It does not directly write career/save records.

| Ranking | Observed low-word character |
| --- | --- |
| -1, negative infinity, either zero | E |
| 0.15 / just below 0.25 | D |
| 0.25 / 0.5 / 0.75 | C / B / A |
| Just below 1 | A |
| 1 / masked NaNs | S |
| Just above 1 / 1.25 / 2 | @ / ? / < |
| 17 / 32 | zero character / `0x00c4` |

These out-of-range controls describe this routine, not valid save ranges or a
recommendation to synthesize career values. Exceptional floor/conversion
paths and arbitrary corrupted inputs remain outside the experiment.

## Original-code controls and limits

`local-data/test-runs/re-audit-20260926/career-grade/original_grade.py` executed
19 independent process cases. The accepted receipt is
`local-data/test-runs/re-audit-20260926/career-grade/run-gmqyky4j/grade.json`,
SHA-256 `e45f2da048070e70eaf7d0a8341ae1aa9a584869760de32f361bd6455d7ae419`.
Each input/output pair is retained separately. An earlier run retained only its
last raw pair because of a filename-extension error; its report is preserved
but is not the accepted replayable evidence set.

Five complete unchanged bodies execute at original addresses: this function,
ASCII widening, `_floor`, its rounding helper and control-word helper. The
conversion body `[0x004f7bf0,0x004f7c63)` is 115 bytes, SHA-256
`cafc9e21516602a2be5e16aacd19f947f6fa6d75d959eadd3e5bdfe5b13fabc7`.
Each ELF-embedded body and original data payload was compared with the pristine
specimen. Rankings and initial scratch contents/index are authored; CRT
exception branches are fail-closed traps and were not entered. Positive
infinity and conversion-overflow inputs were not admitted.

Checks cover the exact AX/full-EAX distinction, next scratch index, the entire
32,768-byte ring, stack cleanup, preserved registers, control word, empty x87
stack and denied `getpid` under a read/write/exit-only seccomp filter. The ring
comparison does not monitor all process memory. These runs establish bounded
calculation and scratch effects, not Windows startup, save publication,
rendered grades, or complete game acceptance.

Related: [GetGradeForWorld](CCareer__GetGradeForWorld.md) and
[TOTAL_S_GRADES](TOTAL_S_GRADES.md) remain separate contracts to recheck.
