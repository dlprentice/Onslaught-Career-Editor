# D3DX two-function Ghidra live promotion

Status: reviewed completed live/tracked structural promotion

Last updated: 2026-08-14

Evidence: **MEASURED** — pristine body bytes, two saved disposable replicas,
separate live PRE/apply/POST processes, exact function/program/listing exports,
one writable-save log, content-addressed PRE/POST backups and retained read-only
restore probes, exact live/tracked project manifests, and two independent
current-ownership replays. **UNKNOWN** — original linker symbols, exact linked
D3DX release, runtime reachability, numerical corner cases, semantic grades,
and rebuild parity.

Specimen: pristine Steam `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

Verdict: two reviewed loose-code bodies are now saved as DEFAULT-source
functions at `0x00595FC9` and `0x00596028`. The structural census advances
from 8,327 to 8,329 functions and from 8,457 to 8,459 exact ranges; owned
`.text` advances by 248 bytes to 1,811,691 / 1,929,117 = 93.912966399%.
All 8,327 PRE function rows remain byte-identical. No semantic name, signature,
comment, tag, grade, byte, data, instruction, or explicit reference was added.

## Exact structural result

The exact two-row input remains the
[`current manifest`](d3dx-gap-two-function-current-manifest-2026-08-14.tsv).
The preceding
[`current preparation`](d3dx-gap-two-function-ghidra-live-promotion-preparation-2026-08-14.md)
proved the result twice on disposable db.18617 copies before this ceremony.

| Entry | Saved body | Saved result | Compatibility-scoped static owner |
| --- | ---: | --- | --- |
| `0x00595FC9` | 95 B / 35 instructions | `FUN_00595fc9`, `DEFAULT`, one range | `D3DXVec3TransformNormal`-compatible |
| `0x00596028` | 153 B / 57 instructions | `FUN_00596028`, `DEFAULT`, one range | `D3DXVec4Transform`-compatible |

| Metric | PRE | POST | Delta |
| --- | ---: | ---: | ---: |
| Internal functions | 8,327 | 8,329 | +2 |
| Exact body ranges | 8,457 | 8,459 | +2 |
| Multi-range functions | 76 | 76 | 0 |
| Owned `.text` bytes | 1,811,443 | 1,811,691 | +248 |
| `.text` ownership | 93.900110776% | 93.912966399% | +0.012855623 points |
| Unowned `.text` bytes | 117,674 | 117,426 | -248 |
| Instructions | 551,143 | 551,143 | 0 |
| References | 234,478 | 234,478 | 0 |

Both bodies were already completely decoded loose instructions. The separate
POST function inventory is 7,194,298 bytes, SHA-256
`7b343b3578a01562daca02ec431586cf39e042d0daab9d6aa9448b779f880ef0`.
Its only rows absent from PRE are the two manifest entries. The POST program
inventory is 1,267 bytes, SHA-256
`a34ca7df45912ed4c7987e59082fcd489726a498721a81ef8aee5ce718c8f523`;
only its function count changes.

## Recovery and project identity

The ceremony used exactly one writable headless apply between separate
read-only PRE and POST processes. PRE and POST were each copied to distinct
off-volume backups and independently reopened read-only. Tracked Ghidra stayed
exact PRE until the live POST backup and restore proof completed.

The physical project transition removes only `db.18616.gbf`, adds only
`db.18618.gbf`, and changes no common file. Stable `db.18617.gbf` remains
68,354,048 bytes / SHA-256
`52cedb3555f418ea8000b0f8bb4c14cddc8c88954b3a5f3104e7600c487b52b0`.
New `db.18618.gbf` is 68,354,048 bytes / SHA-256
`189bc6c738dadcc1796228c6e8c4efbd66acad617098ac5dd19045ac57e50c78`.

Live, tracked, the POST backup, and retained POST/tracked restore copies are
exact 19-file / 187,009,925-byte twins with canonical inventory SHA-256
`c6cb2a228f110a8c7949d8f337a41fc4f060fb33b959bc11868e5cb315e1df7a`.
The PRE backup remains the exact prior project at canonical SHA-256
`a7916b5642b808f468ef113e731a4cfcf225287c94264009fde1034edd9b91cf`.

The current 8,329-row name projection is 510,444 bytes / SHA-256
`6b54dc9459ca3f54f4606117943ee7d34e236bccb6fa2e7eff1e3aef8d2dd2b8`.
The exact 8,459-range export is 1,205,856 bytes / SHA-256
`dd655ef41d127a48cbd936cf6022c4216453d8c636c8e95c6b591e281780ea76`.
The direct-call export remains byte-identical at 1,397,680 bytes / SHA-256
`159f7c89aae54df927186d71263941b5f0857debe09556097820f098da8fa9d8`,
14,598 edges, and 27,244 call sites.

## Current ownership and campaign boundary

Two independent range-union replays close at 8,329 functions / 8,459 ranges /
1,811,691 owned bytes with zero overlap. One new read-only listing export and
two byte-identical offline joins partition the 117,426-byte remainder into
18,674 decoded-instruction bytes outside functions, 46,918 defined-data bytes,
and 51,834 listing-unclassified bytes. The result is structural accounting,
not a semantic or runtime percentage.

Machine-local ownership evidence is under
`local-lab/current-text-ownership-post-d3dx-two-20260814-v1/`. Its canonical
receipts are:

- `run-a/result.ready.json`: 14,303 bytes, SHA-256
  `a97d79aa966a0599eca209940085bfd898a2d028148b474de5169d3af7ac8fb8`;
- `gap-evidence/text-gap-evidence.ready.json`: 1,027 bytes, SHA-256
  `25109242d94b29e40cc7a83c3c039505050fac60023c73f5b8c638cb74e6fc49`;
- `gap-accounting-a/result.ready.json`: 3,399 bytes, SHA-256
  `e735c9757bd5278daba491f3bc25ad650dafaad4cca35662041f17123745b864`.

Generation 28 remains the frozen 8,327-row semantic campaign authority on the
immediately prior db.18617 geometry. These two new structural rows are ungraded
and outside that frozen campaign. A later Generation 29 reseed may carry them
as OPAQUE; no Generation 28 reducer, ledger, or receipt is rewritten here.

## Aggregate authority and claim boundary

The create-new aggregate receipt is
`local-lab/ghidra-d3dx-gap-two-boundary-live-authority-20260814-v1/live-promotion.ready.json`,
21,564 bytes, SHA-256
`b68c593c0266e197011e0a841db5a7510aa8eb35a10b976b97a6198a5cd1831a`.
Its 50,209-byte read-only verifier has SHA-256
`41f214dfe779787baf7a032b3524ada0318217e185bac515fcc709d25aa59d8e`.
Two consecutive verifies from different working directories passed.

Promoted here:

- two exact DEFAULT-source body owners and only those owners;
- exact PRE-row preservation and zero instruction/reference collateral;
- one writable save, separate readback, PRE/POST recovery, tracked refresh,
  exact project rotation, name projection, and current body accounting.

Not promoted here:

- source-exact D3DX names, ABI or signature changes, comments, tags, or grades;
- an original linker symbol or exact upstream D3DX library identity;
- runtime execution, numerical equivalence, source equivalence, or rebuild
  parity; or
- a Generation 29 campaign or any semantic-grade movement.
