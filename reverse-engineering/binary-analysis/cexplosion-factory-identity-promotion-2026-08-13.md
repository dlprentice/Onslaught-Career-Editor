# `CWorldPhysicsManager::CreateExplosion` Ghidra repair owner

Status: scratch validated — candidate for a separately gated live repair; no
live or tracked Ghidra mutation is authorized by this document or its scratch
receipt
Last updated: 2026-08-13
Evidence: MEASURED — exact pristine body and call-site bytes, strict
`CExplosion` RTTI/vtables, current Ghidra metadata, and independent
scratch/readback receipts establish a bounded C1 static implementation
identity; UNKNOWN — exact source spelling/type, runtime reachability and
effects, failure frequency, full layout, and rebuild parity.
Verdict: the saved retail function at `0x0050FF10` independently passed the
separate one-row scratch ceremony that replaces the disproved pickup metadata
with a bounded explosion-factory identity. The scratch result is sealed and
base-compatible; live apply remains forbidden until a fresh exact live PRE and
recoverable pre-write backup pass the separate live gate. Tracked-snapshot
refresh and any merge remain later integration-owner actions.
Specimen: pristine Steam `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Exact proposed mutation

Only the function metadata at `0x0050FF10` may change:

- name:
  `CWorldPhysicsManager__CreatePickup` →
  `CWorldPhysicsManager__CreateExplosion`;
- displayed signature:
  `void * __cdecl CWorldPhysicsManager__CreatePickup(int pickup_type)` →
  `void * __cdecl CWorldPhysicsManager__CreateExplosion(int explosion_definition_index)`;
- comment: completely replace the stale pickup prose with the exact text below;
- tags: remove `pickup`, add `explosion` and `identity-corrected`, and preserve
  every other applicable pre-existing tag.

The exact POST comment is:

> Identity correction (2026-08-13): pristine retail body 0x0050FF10..0x0050FFA7 rejects when the heap metric is below 0x32000 or explosion_definition_index is negative, allocates 0x94 bytes through CDXMemoryManager::Alloc, calls CComplexThing__ctor_base, clears +0x90, installs strict CExplosion vtables 0x005E4454 and 0x005E43DC, and returns null on rejected or allocation-null paths. All 24 pristine direct call sites push one factory argument and caller-clean it; two CRound paths feed the immediately returned ordinal from resolver 0x004DAA20. The separately pinned caller-family join classifies all 24 as explosion paths. High-confidence C1 static implementation identity and bounded cdecl signature only; the parameter name is descriptive. Exact original source spelling/type, runtime reachability/effects, failure frequency, full layout, and rebuild parity remain open. CExplosion factory reproof fe1bfd62f946.

That UTF-8 comment is 915 bytes, SHA-256
`f512ec67c3b7851821c57906c16b08be05c45d3b525de08ebc27c244dabfc5a8`.
The sibling TSV is the immutable machine-readable one-row manifest.

## Independent reproof

The fresh read-only census was taken from a disposable copy of the current
8,170-function canonical project, not from the live maintainer project. It
measured one global, primary, user-defined function symbol at the entry, no
alias, no collision with the proposed name, and no external reference to an
interior instruction. Current ABI/storage is one cdecl `int` at
`Stack[0x4]:4`, a `void *` result in `EAX:4`, dynamic storage, no thunk, no
varargs, no inline flag, and no no-return flag.

The pristine body is one contiguous `0x0050FF10..0x0050FFA7` range: 152 bytes,
39 gapless instructions, byte SHA-256
`24f43aa5cdf6fff0d9d8ec700ec2de8fb221acc3fc49af3f3738e5b596160e5b`.
It checks the heap metric against `0x32000`, rejects negative indices, passes
`0x94` to the allocator, calls `CComplexThing__ctor_base`, clears `+0x90`,
installs `0x005E4454` and `0x005E43DC`, and returns zero on both failure paths.
The sealed strict-RTTI census independently assigns those two tables to
`CExplosion` (68 and 29 slots respectively).

A byte-level scan of the complete pristine `.text` section finds exactly 24
direct relative calls to the entry, identical to the fresh Ghidra reference
census. Every call immediately pushes one factory argument. Twenty-two clean
that dword with `ADD ESP,4`; the two `CRound` paths combine its cleanup with
the preceding cdecl resolver argument in `ADD ESP,8`. At `0x004DA521` and
`0x004DA6EA`, the return in `EAX` from resolver `0x004DAA20` is immediately
pushed into this factory. The separately reviewed caller-family owner classifies
all 24 callers as explosion paths.

The current reproof READY is ignored local evidence at
`local-lab/ghidra-cexplosion-identity-scratch-20260813-v7/reproof-v7/reproof.ready.json`,
4,241 bytes, SHA-256
`fe1bfd62f94694a27c80383647f65952c0a9fbc0b85385a43c4543c20fe3db89`.
Its 24-row call-site table is 867 bytes, SHA-256
`030238e8567855f59e0188ac4e153dd6eea41ddf8482999861f0fecb66b217ab`.
Earlier reproof receipts remain preserved but superseded. V1 did not bind its
producer tools, v2 did not inspect parameter source, and v3 predates the
POST-75 canonical Ghidra checkpoint.

Additional pinned owners:

- [`cexplosion-factory-callers-2026-08-10.md`](cexplosion-factory-callers-2026-08-10.md),
  6,358 bytes / SHA-256
  `695a20b579d6b0b2469991026977f6f281ca3327b62d4e8a5cee38e42b68f604`;
- its ignored 24-row `xrefs.tsv`, 3,236 bytes / SHA-256
  `d8dbf296bddfd882c13429d8c0f7af5003c68d6bd674a4e39e8645a6cee656d8`;
- [`cround-hit-damage-path-2026-08-10.md`](cround-hit-damage-path-2026-08-10.md),
  20,567 bytes / SHA-256
  `1d91d1f9b42127cebf251a0e2c16e2991819a70cb4e5164706af17b1080f084d`;
- strict RTTI READY, 1,864 bytes / SHA-256
  `772630978cdbb2a6b4a95613f425136002381f348917041a9289dff818dbe4d2`,
  and its 431,350-byte vtable table, SHA-256
  `2f1602d4c7ffffa9c2b5116c60a23d23b2f8bf923495feded54ebb67aff1f178`.

## Mutation boundary and stop condition

The mutator must preserve the exact function body/range, all instruction and
program bytes, calling convention, return type/storage, parameter type/storage/source,
signature source, namespace, symbol source/primary status, thunk/varargs/
custom-storage/inline/no-return flags, every non-target function row, every
non-function symbol, all data units, and all references. The parameter name is
descriptive rather than recovered source spelling.

The sealed scratch ceremony completed two independent current-PRE replicas,
dry/apply/separate-process readback, after-one forced rollback, post-inner
forced failure with compensating PRE restore, and backup restore/open
verification. Failed or superseded receipts remain evidence but never become
authority. The scratch authority deliberately stopped before live apply. A
future live ceremony requires a fresh exact live PRE, a recoverable PRE backup,
one bounded mutation process, separate readback, a verified POST backup, and
explicit synchronization of the current projection and tracked snapshot.

This repair authorizes no runtime behavior claim, reconstruction mapping, or
`REBUILD_READY` status.
