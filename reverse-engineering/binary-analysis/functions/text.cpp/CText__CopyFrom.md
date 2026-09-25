# CText__CopyFrom

Status: active bounded contract; file initialization and localization acceptance pending
Last updated: 2026-09-20
Summary: selected header fields and backing bytes are copied; two pointers are rebased and the trailing 16 header bytes survive.
Source File: `text.cpp` is absent from the pinned partial-source snapshot | Binary: pristine `BEA.exe.original.backup`.
Evidence: MEASURED — selected pristine instructions and 16 composed original-code language controls.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Address: `0x004f2660`

## Exact bounded copy contract

The original body takes destination in ECX and one source pointer on the stack,
then returns with `RET 4`. Its caller
[`CFrontEnd__SetLanguage`](../FrontEnd.cpp/CFrontEnd__SetLanguage.md)
selects a cached header and uses active destination `0083d960`.

1. If destination `+4` is nonzero, free that buffer through `00549220`
   with memory-manager receiver `009c3df0`.
2. Clear destination `+0,+4,+14,+18` and write `-1` to `+1c`.
3. Copy source DWORDs `+0,+10,+14,+18,+1c` to the corresponding fields.
4. Allocate exactly source `+18` bytes through `005490e0`, receiver
   `009c3df0`, type `0x72`, debug-source pointer `00632dd8` and
   line token `0x155`. Store the returned pointer at destination `+4`.
5. Copy that byte count from source `+4` using dwords and trailing bytes.
6. Rebase destination `+8` and `+c` as
   `source_field - source_buffer + destination_buffer` using 32-bit arithmetic.

**Destination `+20..+2f` is unchanged.** The earlier assertion that the
entire text object is copied was too broad. The selected source's language
DWORD at `+1c` is copied as data; this function neither derives it from a
cache index nor checks it.

There is no loaded-state, allocation-failure, pointer-range or self-assignment
guard in this body. The zero-size path still calls the allocator. These static
absences do not establish the consequences of actual allocation failure,
self-assignment or other arbitrary invalid memory.

## Executed evidence

The [language composition](../../save-options-static-review-2026-05-26.md#original-language-application-and-persistence)
retains this unchanged body and its original caller, reached from real
Load/TailRead/ApplyPreset and followed by original Save. Authored source headers
and byte buffers distinguish every copied/preserved field. Cases cover lengths
0, 1, 3, 4, 7 and 17; existing/null destination buffers; repeated selection;
selector/header-language mismatch; and full-DWORD language truncation by Save.

Whole selected headers, source/destination buffers, guards and serialized
capacity are compared. Events establish that freeing sees the old active
header, allocation sees the newly copied fields with a cleared buffer pointer,
and the input-selector mirror changes only after the original copy returns.
Deliberately out-of-buffer source pointers are rebased without validation;
their resulting pointers are observed, not dereferenced as valid strings.

Allocator/free are intercepted, cleanup takes its original null path and source
cache data is authored. Actual file parsing, memory-manager ownership/failure,
nonnull cleanup and localized presentation remain open. The private receipt is
`language-run-n__ph8sw/language` under
`local-data/test-runs/save-startup-20260919/`; exact command and pins are in
[VALIDATION.md](../../../../VALIDATION.md#original-language-copy-and-save-composition--september-20).

## Historical boundary

Earlier Wave831 metadata/readback established the saved name and described the
copy shape. It was not complete semantic or runtime validation. This page now
uses freshly inspected instructions and the bounded execution above; no Ghidra
database was opened or changed. [CText__Init](CText__Init.md) remains the separate
file-loading owner whose older detailed format claims require their own recheck.
