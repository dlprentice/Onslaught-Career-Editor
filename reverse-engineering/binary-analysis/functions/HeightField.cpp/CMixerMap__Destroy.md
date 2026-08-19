# CMixerMap__Destroy

Status: active static function note
Last updated: 2026-08-19
Source File: MixerMap.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Slot contents and `CMixerMap__DestroySlot` are **not** this
proof.

> Address: `0x00523230`

## Contract

`thiscall`. Zero stack args. `ECX`→`EBX`. One bare `ret` (`c3`) at
`0x005232ad`. Body `0x00523230`–`0x005232ad` is 126 bytes, SHA-256
`35b83eea1e5b68e7ccb25c413b0dd1f194e7b6188da7b180dfd88b2e3fe8706c`.
Four `E8`, zero `E9`. Three of the `E8`s are
`CDXMemoryManager__Free` (`0x00549220`) with `ecx = 0x009c3df0`.
The remaining `E8` is table label
`CRT__EhVectorDestructorIterator_WithUnwind` (`0x0055db0a`). That
helper's body is **not** claimed.

One inbound `.text` rel32, zero inbound `E8`: `E9` at `0x00490f4a`
inside already-pinned `CHeightField__ShutdownAndDestroyMixerMap`.
That site loads a different this than the heightfield BSS:

```
call 0x0047e8a0
mov  ecx, 0x0089bd80
jmp  0x00523230
```

File `0x00090f45` is `b9 80 bd 89 00`. File `0x00123230` is
`53 8b d9` (`push ebx` / `mov ebx, ecx`).

If `[this+0]` is live: walk that pointer with `edi += 0x14` until
`edi == 0x14000` (`0x14000 / 0x14 = 0x1000` steps). Each step, if
`[ptr+edi+4]` is live: `push` it, Free, then store 0. Then, still
on a live `[this+0] = eax`:

```
push 0x00523210
push dword [eax-4]
push 0x14
push eax
call 0x0055db0a
```

`0x00523210` is table label `CMixerMap__DestroySlot`. It is a
pushed callback, not an `E8`/`E9` (image scan of that VA is 0/0).
Its body is **not** claimed. After the iterator returns, Free
`eax-4` and `[this+0] = 0`.

If `[this+4]` is live: `push` it, Free, then `[this+4] = 0`.

Authored names for `+0` / `+4` / the `+4` slot field are **not**
claimed. `CMixerMap__Init` is **not** this proof.

Cheapest falsifier: file `0x00123230` is not `53 8b d9`,
**or** `0x001232ad` is not `c3`, **or** body SHA-256 is not
`35b83eea…706c`, **or** `tools/call_xref_scan.py` on `0x00523230`
is not exactly `E9` at `0x00490f4a`, **or** `0x00090f45` is not
`b9 80 bd 89 00`, **or** `0x0012324a` is not `b9 f0 3d 9c 00`,
**or** `0x0012325e` is not `81 ff 00 40 01 00`, **or**
`0x00123273` is not `68 10 32 52 00`, **or** `0x00123292` is not
`8b 43 04`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x00523230` | `CMixerMap__Destroy` | `538bd9 … 81ff00400100 … 6810325200 … 8b4304 … c3` | thiscall; bare ret; this imm `0x0089bd80`; walk `[+0]` stride `0x14` to `0x14000` Free `[slot+4]`; then iterator + Free `eax-4`; then Free `[+4]`. HIGH on ABI, inbound jmp, both this-slots, stride/limit, four E8 targets. **Not** on slot payload or DestroySlot. |
