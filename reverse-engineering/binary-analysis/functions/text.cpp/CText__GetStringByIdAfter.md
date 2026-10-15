# CText__GetStringByIdAfter

Status: independently rechecked static and bounded original-code contract
Last updated: 2026-09-20
Summary: physical-record displacement after the first ID match; version rejection logs and returns null.
Source File: `text.cpp` is absent from the pinned partial-source snapshot | Binary: pristine `BEA.exe.original.backup`.
Evidence: MEASURED — complete pristine-body inspection and original execution on captured parser/copy state and owned derivatives.
Specimen: `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Address: `0x004f2500`

ECX is the header; the two stack arguments are `(text_id, after_index)`.
The body returns a pointer with `RET 8`.

## Selection and failure

The signed version comparison at `004f2505` rejects values above 3.
That branch calls ordinary diagnostic `00441740` at `004f2514` and
then explicitly returns null. The old note's “triggers a fatal error” wording
confused diagnostic text with termination; this is not the separate nonreturning
fatal helper used by Init on an Open failure.

Every admitted version uses the same 12-byte record stride, including version
1, zero and negative values. This is not the eight-byte version-1 search in
[GetStringById](CText__GetStringById.md), nor a legacy-format adapter.

The search starts at `buffer+0xc` and chooses the first physical matching ID.
At `004f256f..004f2572`, the function reads the text-offset field
`after_index * 12` bytes away from that matched record. It does not search
for another occurrence of the ID. The result is `textPool + 2*offset`.
A missing ID or nonpositive signed count logs and returns the text-pool base.

There are no loaded-state, displacement, table/pool or termination checks.
Negative displacements and 32-bit multiplication/address wrap are not rejected.

## Executed evidence and limits

The [lookup controls](../../../../VALIDATION.md#original-language-lookups-from-parser-output--september-20)
query all 2,571 IDs in each of six preserved v3 files using original parser/copy
output. The displacement is +1 except for the final record and missing-ID
control, which use zero. IDs are unique in each measured resource.

Separate owned controls establish first-duplicate selection, zero/+1/negative
displacement, reading the next owned record beyond a deliberately reduced
declared count, and multiplication wrapping for `0x40000000`. They also
exercise signed version rejection and the version-1 stride discrepancy.
The experiment compares adverse returned pointers without dereferencing them.

Diagnostics are intercepted; no unsupported version is called a valid language
file. Physical adjacency is a data relationship, not proof that a caller
intends a grouped sentence or that the rendered result is correct.

Related: [Init](CText__Init.md) and [audio lookup](CText__GetAudioNameById.md).
