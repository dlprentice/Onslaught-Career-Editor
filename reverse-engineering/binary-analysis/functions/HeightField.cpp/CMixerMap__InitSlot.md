# CMixerMap__InitSlot

Status: active static function note
Last updated: 2026-08-19
Source File: MixerMap.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Callee bodies are **not** this proof.

> Address: `0x00523190`

## Contract

`thiscall`. `ECX`→`ESI` (the slot, not the mixer BSS). One stack
dword (`ret 4` at `0x005231f7`); that arg is copied to `EDI` and
used as `ECX` for every `0x00423910` / `0x00423960`. Body
`0x00523190`–`0x005231f9` is 106 bytes, SHA-256
`4c73238fdce26ab139f04eee4d70be8e86c37c6bb97cc17bcd3ce63db66e32da`.
Six `E8`, zero `E9`. Image encodings of imm `90 31 52 00` are
zero.

One inbound `.text` `E8`, zero `E9`: `0x00523381` inside
already-pinned `CMixerMap__Init`. File `0x0012337a` is
`8b 17 8b ce 53 03 ca e8 0a fe ff ff`:

```
mov  edx, dword ptr [edi]   ; mixer[+0]
mov  ecx, esi
push ebx
add  ecx, edx
call 0x00523190
```

`ESI` there is the `0x14` walk. Caller body beyond that site is
**not** claimed.

First the body `Read`s `0x14` bytes onto this (`push 1` / `push
0x14` / `push esi`). If `[this+4]` is live: another `GetNext`,
then Alloc size `([this+0]*9)*9` with string `0x00640030`
(`C:\dev\ONSLAUGHT2\mixermap.cpp`), store that pointer at
`[this+4]`, then `Read` that many bytes into it. Alloc this is
`0x009c3df0`. Authored names and the `*9*9` meaning are **not**
claimed.

Cheapest falsifier: file `0x00123190` is not
`56 57 8b 7c 24 0c 8b f1`, **or** `0x001231f7` is not `c2 04 00`,
**or** body SHA-256 is not `4c73238f…32da`, **or**
`tools/call_xref_scan.py` on `0x00523190` is not exactly `E8` at
`0x00523381`, **or** `0x0012337a` is not
`8b 17 8b ce 53 03 ca e8 0a fe ff ff`, **or** `0x001231a8` is not
`6a 14`, **or** `0x001231df` is not `89 46 04`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00523190` | `CMixerMap__InitSlot` | `5657 8b7c240c 8bf1 … 6a14 56 … 8b4604 … 894604 … c20400` | thiscall; ret 4; slot this from mixer`[+0]+walk`; 6 E8 / 0 E9; 1 inbound Init; Read `0x14` onto this; optional Alloc into `[+4]`. HIGH on ABI, inbound site, those two slots, Read size. **Not** on `*9*9` meaning or callee bodies. |
