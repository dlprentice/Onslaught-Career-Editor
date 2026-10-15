# CFrontEnd__SetLanguage

Status: active bounded contract; actual localization acceptance pending
Last updated: 2026-09-22
Summary: menu destruction precedes active text replacement; unchecked cache selection and persisted language have distinct owners.
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
after return. The September 20 save composition executes the actual null path;
the September 22 controls below separately execute the nonnull route.

## Nonnull cleanup before text replacement

Static instructions in `0051f7e0..0051f8dd` allocate a `0x4c` object, call
constructor `004cde60` and publish its result to `0089bc30`. The constructor
installs vtable `005de6fc`; slot `+4` contains deleting wrapper `004d04b0`,
which calls destructor `004d05e0`. This anchors the object reached by cleanup;
the large constructor and activation call do not execute in the controls.

Twenty-six [original-code controls](../../../../VALIDATION.md#original-nonnull-language-cleanup--september-22)
execute that destructor with authored owned objects. It first destroys nested
menu payloads and recycles their list nodes, then dispatches optional children
at `+8` and `+3c`, decrements resources at `+40`, `+44` and global `0082b490`,
and clears those owners. Original monitored-base cleanup clears traversed
pointer cells, recycles their nodes and frees their list container. Finally,
the deleting wrapper conditionally frees the outer object using flags bit zero.
The global owner stays nonnull throughout those calls and clears after return.

Original nested-menu, base-item and controller-item destruction executes.
List recycling uses nonzero count as its guard, retains the cursor field and
prepends nodes to the shared pool. Payload traversal stops at a null payload,
even if later nodes exist. Each occupied resource slot decrements its counter;
aliases are not deduplicated and zero wraps. These deliberately adverse controls
describe instructions, not healthy object construction or safe malformed input.

Controller-item destruction changes byte `006290b4` from zero to one and then
clears DWORD `00889008`; a preexisting nonzero byte skips that write. The
adapter at `005159c0` selects receiver `00855bb0`, and `005135f0` writes its
`+33458` field. The earlier private report/oracle misadded that address as
`00888008`; corrected capture now checks both locations and surrounding guards.
This establishes scalar state changes, not host input-device effects.

During every destruction/free observation, the old active text header and
buffer remain unchanged. Only after cleanup returns does CopyFrom free and
replace the text buffer. Repeated selection again copies the text; its second
cleanup sees the now-null owner. No new menu is constructed between those calls.

Allocation/free and both optional child virtual calls remain explicit recording
hooks. Numeric/sensitivity and other derived item destructors, real memory
reclamation, exception unwinding, reentrancy and UI reconstruction are excluded.
No Ghidra database or implementation-lane source changed.

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

Those September 20 save controls supply cache bytes and allocator/free behavior.
They do not initialize real language files or execute nonnull cleanup; the
separate controls above add bounded destruction without displaying text or
proving retail localization. Older naming/signature readback is historical evidence;
no Ghidra metadata was changed in this recheck. Exact commands and artifacts
are in [VALIDATION.md](../../../../VALIDATION.md#original-language-copy-and-save-composition--september-20).
