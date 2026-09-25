# CText__GetStringById

Status: independently rechecked static and bounded original-code contract
Last updated: 2026-09-20
Summary: ordered text lookup, missing-ID fallback, version-dependent stride and unchecked pool offsets.
Source File: `text.cpp` is absent from the pinned partial-source snapshot | Binary: pristine `BEA.exe.original.backup`.
Evidence: MEASURED — complete pristine-body inspection and original lookup execution using captured parser/copy output; legacy conversion is static-only.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Address: `0x004f2580`

## Exact selection

ECX is the text header; the one stack argument is a 32-bit ID/index and
the body returns a pointer with `RET 4`. For signed version `>=1`, it
searches physical records from `buffer+0xc`, stopping at the first equal ID.
The stride is 12 bytes for versions 2/3 and eight bytes for other positive
versions. Thus the function does not itself reject an unknown positive version.

A hit at `004f25be` returns `textPool + 2*textOffset` through
`004f25f3..004f25fb`, using 32-bit arithmetic. The offset counts UTF-16
code units, not bytes. The scan uses the signed count at header `+0x10`;
a nonpositive count or absent ID calls ordinary diagnostic `00441740`
and then returns the text-pool base. It does not return null on a normal miss.
Unsorted IDs work; a later duplicate never replaces the first match.

Neither the loaded flag nor allocation size admits the lookup. There is no
table/pool bound or string-termination check. An adverse offset can produce
an out-of-buffer pointer without a dereference by this body.

## Other versions

Version zero treats a nonnegative argument below the signed count as a legacy
offset-table index; otherwise it selects the text-pool base. It scans for a
byte terminator, then calls `MultiByteToWideChar` at IAT `005d81b8` with
code page/flags zero, source count `-1`, destination `0083d560` and a
capacity derived from the scanned byte length including its terminator.
The API result is ignored; the global scratch pointer is returned.
The static body supplies no independent scratch-capacity check.

A negative signed version simply returns the text-pool base. No legacy
conversion call was executed by the September 20 lookup experiment.

## Executed evidence and limits

The [language lookup controls](../../../../VALIDATION.md#original-language-lookups-from-parser-output--september-20)
import the exact active header and allocations captured after original
Init/CopyFrom. For each of six preserved version-3 resources, all 2,571 IDs
and one missing ID run through this body, audio lookup and adjacent-string
lookup. Pointer results and unchanged imported memory are checked; offline
checks validate returned strings against the declared pools.

Owned derivatives exercise duplicate-first selection, unknown/negative
versions, nonpositive counts, a cleared loaded flag and unchecked offsets.
They are not supported malformed-file configurations. The diagnostic is
intercepted. No rendered text, glyph coverage, thread-safety, live filesystem
or complete startup/save round trip is established.

Related: [Init](CText__Init.md), [adjacent lookup](CText__GetStringByIdAfter.md),
[audio-name lookup](CText__GetAudioNameById.md) and
[offline decoder](../../../../tools/language_dat_decode.py).
