# CFrontEnd__SetLanguage

Status: active bounded contract; actual localization acceptance pending
Last updated: 2026-09-20
Summary: unchecked cache selection, cleanup and active text copy; the requested selector and persisted language have distinct owners.
Source File: `references/Onslaught/FrontEnd.cpp:557–560` (partial-source comparison) | Binary: pristine `BEA.exe.original.backup`.
Evidence: MEASURED — unchanged original bodies in the composed language controls below.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Address: `0x00466ab0`

## Rechecked behavior

The 39-byte original body calls cleanup `0051f8e0`, then passes
`this + 0xbf40 + language_index * 0x30` to
[`CText__CopyFrom`](../text.cpp/CText__CopyFrom.md), with active destination
`0083d960`. It pops one argument. It checks neither selector bounds nor
whether the selected language is already active.

Fresh instructions at `004667f6..00466814` initialize exactly five cache
objects with stride `0x30`. The pinned source
`5352a81cdb838b145a57f7febc5d9fc4b0129ebb` corroborates the five-element
cache and assignment relationship (`Frontend.h:288–289`,
`Career.h:24`, `FrontEnd.cpp:302–307,557–560`). Its SetLanguage omits
the retail cleanup call; source agreement does not replace the binary evidence.

The cleanup body reads `0089bc30`. Null returns immediately. Nonnull calls
the object's virtual slot `+4` with argument 1, then clears that global
after return. The composed experiment executes the actual null path; it does
not replace nonnull destruction with a presumed simple clear.

## Relationship to save settings

TailRead zero-extends its saved language WORD, calls this function, then stores
that selector to `0066305c`. This function itself does not update that
mirror. The active header's language comes from the selected source object's
`+1c`, and TailWrite serializes its low WORD at `0083d97c`.

Sixteen [composed controls](../../save-options-static-review-2026-05-26.md#original-language-application-and-persistence)
execute real Load/TailRead/preset/language-copy/Save bodies. A deliberately
mismatched cache index 2/header language 4 leaves mirror 2 and saves 4.
Selecting the same cache twice repeats the buffer free/allocation/copy.
An authored adjacent header at index 5 demonstrates unchecked address selection,
not support for a sixth language.

These controls supply cache bytes and allocator/free behavior. They do not
initialize real language files, execute nonnull cleanup, display text or prove
retail localization. Older naming/signature readback is historical evidence;
no Ghidra metadata was changed in this recheck. Exact commands and artifacts
are in [VALIDATION.md](../../../../VALIDATION.md#original-language-copy-and-save-composition--september-20).
