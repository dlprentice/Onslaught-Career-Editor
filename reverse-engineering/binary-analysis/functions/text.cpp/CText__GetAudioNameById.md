# CText__GetAudioNameById

Status: independently rechecked static and bounded original-code contract
Last updated: 2026-09-20
Summary: first-match audio-name lookup for versions 2/3, with a single null-offset sentinel.
Source File: `text.cpp` is absent from the pinned partial-source snapshot | Binary: pristine `BEA.exe.original.backup`.
Evidence: MEASURED — complete pristine-body inspection and original execution on captured parser/copy state and owned derivatives.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Address: `0x004f24b0`

ECX is the header and the stack argument is a 32-bit text ID. The body returns
a pointer or null with `RET 4` and invokes no other function.

Only versions 2 and 3 enter the scan. Records begin at `buffer+0xc`,
have stride 12, and contain `{id,textOffset,audioOffset}`. The signed count
at header `+0x10` bounds the forward search. Unsupported versions,
nonpositive counts and missing IDs return null without a diagnostic.

The first matching physical record wins. An audio offset of `0xffffffff`
returns null immediately, even if a later duplicate has an audio name.
Every other value is added to the audio-pool pointer at
`004f24f3..004f24f8` with 32-bit arithmetic. Audio offsets count bytes.
There are no loaded-state, pool-bound, termination or encoding checks;
`0xfffffffe` is not another null sentinel.

The [lookup controls](../../../../VALIDATION.md#original-language-lookups-from-parser-output--september-20)
execute this body for every ID in six preserved v3 resources, plus missing IDs,
using exact captured original Init/CopyFrom state. Offline checks find each
nonnull returned name within its declared audio pool, with a terminator and
ASCII-decodable bytes. Owned derivative controls confirm duplicate-first null
selection and the unchecked non-sentinel offset case.

This establishes name selection, not that a corresponding audio asset exists,
loads, plays or has the correct timing/volume. Version 2 has static coverage;
the admitted unmodified files are version 3.

Related: [Init](CText__Init.md), [text lookup](CText__GetStringById.md),
[adjacent lookup](CText__GetStringByIdAfter.md) and
[offline decoder](../../../../tools/language_dat_decode.py).
