# CLandscapeTexture__DeleteDeviceObjects

Status: active static function note
Last updated: 2026-09-27 (interface identity rederived; earlier body notes retain their stated limits)
Summary: retail device-lifecycle identity with retained, separately bounded August body analysis.
Source File: HeightField.cpp / LandscapeTexture.cpp (absent from the
pinned GPL `references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened for that August review. At that date,
the table name was a research label. The `[vtable+8]` callee is **not** this proof.

> Address: `0x0048e790`

## September 27 interface correction

The former label `CLandscapeTexture__VFunc_4_0048e790` is retained by this filename for stable links.
Fresh complete-body decoding, both typed list callers and all known RTTI holder
occurrences establish `CLandscapeTexture__DeleteDeviceObjects`; see the
[platform evidence](../../../source-code/core/platform-system.md#retail-device-lifecycle--september-27-correction).
The new name identifies its lifecycle interface. It does not establish the full
resource algorithm, source return type, callback lifetime or retail graphics
behavior. The August evidence statements below describe that earlier review;
its separate specimen twin was not reverified for this correction.

## Contract

The virtual caller supplies its receiver in `ECX`, but this implementation
never reads that incoming register. This does not disprove its member-interface
identity. There are no explicit stack arguments.
Bare `ret` at `0x0048e7ab`. Body `0x0048e790`–`0x0048e7ab` is 28
bytes, SHA-256
`3bb697ce5c313c376730111c0e8695a04241e877e7f02fbd89e64b1c04e39f7f`.
Zero `E8` / zero `E9`. If `[0x006fabf4]` is live, `call [[eax]+8]`
then store 0 at that BSS. `EAX` is forced 0. Four `nop`s after
the `ret` are **not** in the body.

Zero inbound `.text` `E8`/`E9`. Unique image copy of the entry
VA is vtable slot 4 at `0x005dc200` (slot 1 is already-pinned
`0x0048e670`; slot 2 is already-pinned Reset). Caller bodies are
**not** claimed.

Cheapest falsifier: file `0x0008e790` is not
`a1 f4 ab 6f 00 85 c0 74 10`, **or** `0x0008e7ab` is not `c3`,
**or** body SHA-256 is not `3bb697ce…9f7f`, **or**
`tools/call_xref_scan.py` on `0x0048e790` is not empty, **or**
`0x001dc200` is not `90 e7 48 00`, **or** `0x0008e79f` is not
`c7 05 f4 ab 6f 00 00 00 00 00`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0048e790` | `CLandscapeTexture__DeleteDeviceObjects` | `a1f4ab6f00 85c0 7410 8b08 50 ff5108 c705f4ab6f00 00000000 33c0 c3` | incoming ECX supplied but unused; bare ret; 28 B; 0 E8/E9; 0 inbound; vtable slot 4; zeros `[0x006fabf4]`. HIGH on ABI, inbound-empty, that slot, that store. **Not** on the `[vtable+8]` body. |
