# CFeature__Init

Status: active static function note
Last updated: 2026-08-19
Source File: CFeature.cpp (absent from the pinned GPL
`references/Onslaught/` drop) | Binary: BEA.exe, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Evidence: MEASURED — independently re-read 2026-08-19 from official
`local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`. Twin
`local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
matches. The Ghidra database was not opened. Table name is a research
label. Iceberg 1–4 occupancy after this physics.dat update is
measured below. Live heap was not sampled.

> Address: `0x0044ca30`

## Contract

`thiscall`. `ECX`→`EBX`. One stack arg (`ret 4` at `0x0044cbd6`);
that arg is the InitThing (`EBP` from `[esp+0x440]` after the
frame). Body `0x0044ca30`–`0x0044cbd8` is 425 bytes, SHA-256
`58b0f15b4b04b3c3e150c45c1b527f9a3b282e458302c886258727b2132749a4`.
Six `E8`, zero `E9`. Zero inbound `.text` `E8`/`E9` (virtual
Init). Callee bodies are **not** claimed.

Stores `[init+0x3bc]` at `[this+0xe4]` (`89 83 e4 00 00 00` at
`0x0044ca8e`). Then `[this+0xe0] = [[this+0xe4]+0x18]`
(`8b 48 18 89 8b e0 00 00 00` at `0x0044cb36`). Those two stores
are the already-pinned slot-40 seeds. Authored names are **not**
claimed.

On this `default physics.dat` (SHA-256
`e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14`),
Iceberg 1–4 are type-8 with value-ids 2 then 4 (payload `1.0f`).
Create `xor ebp,ebp` at `0x00431386` then `[+0x18]=[+0x10]=0`
(`89 6b 18 89 6b 10`). Id-4 apply writes `[+0x10]=1` at
`0x0043bd1b` because `1.0f != 0.0f` at `0x005d856c`. No id-1
node, so `[+0x18]` stays 0. Live heap was not sampled.

Cheapest falsifier: file `0x0004ca30` is not
`6a ff 68 8b 25 5d 00`, **or** `0x0004cbd6` is not `c2 04 00`,
**or** body SHA-256 is not `58b0f15b…49a4`, **or**
`tools/call_xref_scan.py` on `0x0044ca30` is not empty, **or**
`0x0004ca8e` is not `89 83 e4 00 00 00`, **or** `0x0004cb36` is
not `8b 48 18 89 8b e0 00 00 00`, **or** Iceberg 1 at file
172516 is not `Iceberg 1`, **or** its second value-id is not 4
with payload `00 00 80 3f`.

## Functions

| Address | Name | Byte evidence | Contract (confidence) |
| --- | --- | --- | --- |
| `0x0044ca30` | `CFeature__Init` | `6aff688b255d00 … 8983e4000000 … 8b4818 898be0000000 … c20400` | thiscall; ret 4; 425 B; 6 E8 / 0 E9; 0 inbound; writes `[+0xe4]` then `[+0xe0]=[data+0x18]`. HIGH on ABI, those two stores. Iceberg 1–4 occupancy after this physics.dat update: `[data+0x10]=1`, `[data+0x18]=0`. **Not** on live RAM or authored names. |
