# CThing__Init

Status: active — **RED C2 gate; static contract retained**
Last updated: 2026-08-24
Verdict: **RED — retained evidence proves execution and caller-family counts, but no retained target-specific call→entry→return record binds `this`, `init`, receiver writes, and registration readback. The grade remains `C1_CANDIDATE_PARTIAL / OPEN_EXECUTED`; no C2 promotion is claimed.**
Evidence: MEASURED — exact specimen/body receipts, tracked layout, retained trace counts, and a current 98-file call-context census with can-fail corpus controls; the requested runtime state transfer remains UNKNOWN.
Specimen: pristine PC retail `BEA.exe`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750` for static identity. Retained TTD captures ran force-windowed image `e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4`; they are not substituted for the pristine specimen.
Source File: references/Onslaught/thing.cpp | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004f34a0`

## Identity

- Body `[0x004f34a0,0x004f35cc]` inclusive / `[0x004f34a0,0x004f35cd)` half-open, 301 bytes and 106 instructions; raw pristine-body SHA-256 `b54ff4165a998127328eafd4e63175249216437d2cfc3996f74beb2a388d35d4`.
- Exact range-set SHA-256 `639d6610c0906f371345f06e0bf3442d6bad31da53525b26844f9a48fa9a3ea8`. The current Generation-32 function and contract rows use this same specimen, VA, range-set identity, byte count, and `WORLD_SIM` route.
- Retained retail decompile SHA-256 `981970a1f60fc2f83ae8b2a9f6eb38f489c97eb64e4bf1f68e2502fc5947beec`. It is static evidence, not runtime state-transfer proof.
- Current authority is Generation 32 canonical READY `08ed89644ed25feb9e85fefb5b31ab2bdecbbd91b8aca720e20c53a7fbc5e73f`; the target remains `C1_CANDIDATE_PARTIAL / OPEN_EXECUTED`, question `Q-5083ac6b0979162a`, status `OPEN`.

## Calling convention

The retained body and `RET 0x4` support the displayed prototype `void __thiscall CThing__Init(void *this, void *init)`: `ECX` supplies the receiver and one stack dword supplies `init`. This is a static ABI statement. No retained target-specific entry record currently proves the live `ECX` value, stack pointer value, or their continuity through a matching return.

## Prototype and parameter semantics

- Static instructions copy the 16 bytes at `init+[0x04,0x14)` to `this+[0x1c,0x2c)`. The tracked layout identifies that complete receiver interval as `mPos` (`FVector`); no narrower component semantics are added here.
- Static instructions then conditionally replace `this+0x24`, test and conditionally OR `this+0x2c`, conditionally OR `this+0x34`, pass `init+0xa8` to the embedded map-who path, pass `init+0x68` to virtual slot `+0x8c`, and test `init+0x3ac` before virtual slot `+0x5c`.
- Those offsets and transfer sites are specimen-bound static facts. Their live values, pointer validity, aliasing, subtype-specific virtual targets, and invocation-local before/after relation are not present in the retained runtime products.

## Return value meaning

The displayed function returns `void`. No scalar result is claimed. A C2 state-transfer contract still requires a matching return boundary so that post-state belongs to the same invocation rather than to a later object or caller.

## Globals read/written

- Static body references `0x006fadc8` for the height sample, `0x006fbdfc` for the second vertical clamp, `0x00855170` for conditional tail insertion, and `0x00855090` for unconditional head insertion.
- The historical access scan observed writes to head address `0x00855090`, including non-zero node values, but the contemporaneous arbitrary-position `dd` read falsely reported zero. That experiment explicitly refuted its own world-set walk.
- No retained target-return plate reads the inserted node, follows its element pointer, and proves that the element equals the same invocation's receiver. Registration therefore remains static-call-edge plus untied global-write evidence, not a C2 registration claim.

## Callees relied on / callers

- Direct static calls: height sample `0x0047eb80`, `CMapWhoEntry__SetPosition` `0x00492ba0`, `CSPtrSet__AddToTail` `0x004e5b20`, and `CSPtrSet__AddToHead` `0x004e5a80`.
- Receiver virtual sites occur at slots `+0x88`, `+0x98`, `+0xb0`, `+0x50`, `+0xc4`, `+0x8c`, and `+0x5c`. Their concrete derived targets remain invocation-dependent.
- Four direct static caller sites are retained: `CComplexThing__Init` at `0x004f40de` and `0x004f4102`, `CTree__Init` at `0x004f6363`, and `CWaypoint__InitAndLink` at `0x005057c1`. Their return addresses are `0x004f40e3`, `0x004f4107`, `0x004f6368`, and `0x005057c6` respectively.

## Behavior summary

Static order is: optional render initialization; virtual type setup; `init` position copy; conditional height and water clamps; conditional map-who, large-set, and collision-seeking initialization; conditional renderable-bit update; conditional activation; unconditional world-set insertion. This is bounded body/dataflow recovery only.

The current source crosswalk class is `SOURCE_ANALOG` at thing.cpp line 40 and was remediated to a name-only analogy. The pinned GPL source may explain intended architecture, but it is not used here as retail runtime proof or as a C2 substitute.

## Error / edge behavior

The static branches distinguish a null `this+0x30`, virtual height/underwater predicates, receiver flag bit `0x2`, embedded map-who state below 3, a non-null render pointer, and raw `init+0x3ac`. Retained evidence does not establish invalid-pointer behavior, allocation failure, virtual-callee failure, exception transfer, rollback, duplicate initialization, or nullability. No whole-lifetime or whole-class parity is claimed.

## Runtime corroboration (TTD, bounded)

### Five-wave reuse preflight

The counting unit is one unique reused authority artifact, one analytical
extension, or one new offline measurement; duplicate copies and search hits are
excluded.

| Wave | REUSED | EXTENDED | NEW_MEASUREMENT | Exact authority / result |
| --- | ---: | ---: | ---: | --- |
| Tracked `CThing` / `CComplexThing` layout and existing function owners | 4 | 0 | 0 | Pre-edit layout `fe279fdc47174f19d47c8531819aa44188024066b937c131bf1ba26a00d10a13`; vtable semantics `5ae2f7aa713f549153de959b1a022489f09a297502b21b9ae447284ab79df710`; closure `cfe90af382269cb2e64996d10df7777bd00fcd8e1844b9823ef74bc6199b8974`; evidence register `4862fc61391c9bf65cd7183752e99b9b02b6bfb721e5b4b5c1e7c5fae5b885b4`. |
| Current Generation-32 target rows | 3 | 0 | 0 | `campaign-functions.tsv` `a63f42e331c265c94866ae944abc74e6a985dfb590f87419309c24932a951c63`; `campaign-contracts.tsv` `d4ddaa1054a4e27bfad0b4fbbbbdc817216c0329d580ae1419cdbcac5fa97409`; `campaign-questions.tsv` `0969bf5c5dcee73d9e046e37894db12f4becce65114d427de6329a0968a706ca`. Exact target/range-set/301-byte identity matches; grade/open state is unchanged. |
| Current and historical campaign reports | 3 | 1 | 0 | Historical Level-100 report `7a48338e5db25db2f324f9a22ef6875b6e58b8117a432c555b6de23c6833e674`; 2026-08-19 FillOut report `e1c762863092f245c3c8311cd6fa4d8f29fc1c5fa12082511e8fe4d0c8c382e9`; current deep-mine `values.tsv` `6495234233f05e29c7d8ef11342deb3426d3018eaeac10f2da57329c8cde0f5b`. This contract's witness-matrix join is the one extension; it adds no runtime observation. |
| Three promoted G: routing inventories | 3 | 0 | 0 | `DRIVE-INVENTORY-2026-08-17.md` `3778443cecee5c342626edfe33262132a543be278acca2aa72ad6d3650df5fde`; `DRIVE-AUDIT-G-2026-08-17.md` `c43cdf1e16668a2d355cab02e20210716fe1d84bbd15a79b9c488a3537c4f458`; `g-drive-triage-2026-08-17.md` `c1c189f445fa7af7f443376c6a8600da35b5b2bcf14e815cc1a2c4a0fc8ee52d`. They route the corpus without raw G: access. |
| Retained trace / TTD / CDB catalogs and call-context corpus | 3 | 0 | 1 | TTD catalog `REPORT.md` `9ff584135d237d56cee6d230d992d93520cfd577af7b944d47189a701f7559e1`; `sessions.tsv` `6ba813d8d1afb838e5a5bc1bc34a3eb22df5312a091357e72b033991c8b34a79`; runtime/CDB route `INDEX-CATALOG-2026-08-17.md` `8d50dc0d0fcfcae2fc1e64c77f20ee0c0bcc9be6cd4bb9f54065f2f543051040`. New read-only census: 98 `call-context.jsonl` files, zero `0x4F34A0` target rows and zero current deep-mine target mentions; positive control `CUnit__ApplyDamage @ 0x4F9A90` appears in 11 files / 11 target rows; wrong-address `0x4F34A1` appears in zero. Poisoned expected-target-files=1 exits 5; correct expected zero exits 0. |
| **Total** | **16** | **1** | **1** | No new inventory, crosswalk, deep-mine, evidence root, replay, or recording. |

### What the retained traces do prove

- Historical play-Level-100 query report SHA-256 `7a48338e5db25db2f324f9a22ef6875b6e58b8117a432c555b6de23c6833e674` pins 1,579 calls in trace SHA-256 `03599cea7459810f601174a6713ebf17cf12dfe88d593d7f87fd5b94c564e40e`.
- That trace's caller histogram partitions exactly into `CTree__Init` 1,481, `CComplexThing__Init` Euler branch 68, authored-basis branch 0, and `CWaypoint__InitAndLink` 30. It also states that per-call `this` was not read.
- Independent retained query report SHA-256 `e1c762863092f245c3c8311cd6fa4d8f29fc1c5fa12082511e8fe4d0c8c382e9` records 1,579 calls in play-Level-100 and 1,578 in damage-script-Level-100; the latter trace SHA-256 is `994a6aa99444176ec4b8985d03bd95549a07f9eead6e41492a24c4567c9befcd`.
- These traces recorded force-windowed image `e1436ef7e0ad9ccbddd43aaaca952f6e84d4b1a282835cead745efcfc32fadf4`. The call counts and families are bounded runtime evidence; they do not identify receiver/init pointers or owned writes.

### C2 witness matrix

| Required witness | Retained result | Gate |
| --- | --- | --- |
| Call→entry→return envelope from one derived family | No target row in 98 retained call-context files | `MISSING` |
| Independent envelope from a materially different family | Caller counts exist for trees, complex things, and waypoints; no entry/return context exists for any | `MISSING` |
| Exact `this` and `init` continuity | Historical report explicitly says per-call `this` was not read; no target stack/register row exists | `MISSING` |
| Before/after `this+[0x1c,0x2c)`, `+0x2c`, and `+0x34` tied to the body | Static stores exist; no invocation-local runtime before/after plate | `MISSING` |
| Initialized/default contrast | No paired raw `init+0x3ac == 0` / non-zero or equivalent preregistered contrast | `MISSING` |
| Wrong-receiver, swapped-init, wrong-field, cross-invocation controls | No target-specific state verifier exists to poison | `MISSING` |
| Registration pointed-memory readback | Set-head writes exist, but the retained direct read was refuted and no node element was tied to the receiver | `MISSING` |

## Evidence

- Current tracked layout owner: `reverse-engineering/binary-analysis/cthing-ccomplexthing-layout-2026-08-13.md`.
- Current tracked target/grade owners: `reverse-engineering/EVIDENCE-REGISTER.tsv`, `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`, and `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`.
- Current target row is pinned by Generation-32 READY `08ed89644ed25feb9e85fefb5b31ab2bdecbbd91b8aca720e20c53a7fbc5e73f`; canonical and replica target rows agree on VA, range-set, 301 bytes, `COVERED`, grade, and open state.
- Retained static decompile, historical Level-100 report, 2026-08-19 FillOut report, 2026-08-18 TTD catalog, and 2026-08-22 deep-mine table were hash-read before this verdict. Their SHA-256 values are recorded above where they bear on the claim; the deep-mine table SHA-256 is `6495234233f05e29c7d8ef11342deb3426d3018eaeac10f2da57329c8cde0f5b`.
- Deterministic retained-corpus verifier: enumerate files named call-context.jsonl, parse only JSON `kind == "target"`, normalize `entry_va`, then assert target, positive-control, wrong-address, Generation-32, and report tokens. Correct expectations returned 0; injected expected-target-files=1 returned 5. This is a corpus-absence check, not a runtime falsifier.
- No browser, live Ghidra, raw ROM, pristine write, save access, G:/H:/D: write, native launch, or new recording occurred.

## Confidence

1 — exact static identity, current campaign state, caller-family counts, and the absence of a retained target-specific call-context row are reconciled with a can-fail census. Runtime `this`/`init` continuity, receiver writes, registration readback, and edge behavior remain unproved, so confidence does not imply C2.

## Unresolved questions

- Obtain at least two hash-bound target envelopes from materially different caller families: one `CTree__Init` invocation (`0x004f6363 → 0x004f6368`) and one `CWaypoint__InitAndLink` or `CComplexThing__Init` invocation (`0x005057c1 → 0x005057c6` or `0x004f40de → 0x004f40e3`). Each must preserve call/entry/return association and exact `ECX`/`init` continuity.
- For each selected invocation, capture raw `init+[0x04,0x14)`, receiver `this+[0x0c,0x38)`, and the exact before/after fields touched by this body. Separate direct body writes from caller, derived-class, and callee-owned writes.
- Include a preregistered raw-field contrast such as `init+0x3ac == 0` versus non-zero, without assigning a semantic label until measured.
- Require can-fail controls: wrong receiver base, invocation-A receiver with invocation-B `init`, wrong destination offset/value pairing, and invocation-A entry joined to invocation-B return. Every poison must fail.
- For world insertion, inspect the access-scan event at the selected return, follow the resulting set node, and prove its element pointer equals the same receiver. Use touched-memory controls; arbitrary-position `dd` is already refuted for this BSS region.
- Cheapest offline instrument: query the existing hash-bound play-Level-100 capture only. First select one invocation from two caller-family return-address groups; then run [`tools/Invoke-TtdCallContextV2.ps1`](../../../tools/Invoke-TtdCallContextV2.ps1) for bounded call/entry/return windows and [`tools/Invoke-TtdDataWrites.ps1`](../../../tools/Invoke-TtdDataWrites.ps1) for preregistered receiver/set ranges. Do not record a new session unless retained traces cannot supply the two envelopes.
