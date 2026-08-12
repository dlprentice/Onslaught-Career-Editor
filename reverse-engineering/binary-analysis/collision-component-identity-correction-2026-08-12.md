# Collision-component implementation-identity correction

Status: promoted, bounded static implementation identity
Last updated: 2026-08-12
Evidence: MEASURED — sealed pristine-body, RTTI/vtable, xref, PC-demo, source,
scratch/readback, live-promotion, backup/restore, and tracked-snapshot receipts
Specimen: pristine PC `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Verdict: five wrong or over-specialized labels were corrected in the backed-up
live Ghidra project and the byte-identical tracked snapshot. No boundary,
instruction, program-byte, data-unit, or reference changed.

## Promoted identities

| Address | Superseded label | Promoted label |
| --- | --- | --- |
| `0x004263f0` | `CCollisionSeekingRound__Destructor` | `CCollisionSeekingThing__dtor_base` |
| `0x004264a0` | `CCollisionSeekingThing__ResolveRoundCollisionResponse` | `CCollisionSeekingThing__ResolveCollisionResponse` |
| `0x004269b0` | `CCSPersistentThing__InitWithSound` | `CCSPersistentThing__Init` |
| `0x00426a00` | `CCollisionSeekingRound__ProcessMapWhoCollisionSweep` | `CCSPersistentThing__ProcessMapWhoCollisionSweep` |
| `0x00426a20` | `CCollisionSeekingRound__MarkDelayedCollisionReady` | `CCSPersistentThing__HandleEvent` |

These labels identify the shared base implementation at each address. They do
not exclude an identical-code-folded derived method alias at the same body.
`ResolveCollisionResponse` and `ProcessMapWhoCollisionSweep` are bounded role
labels; exact original source spelling is not claimed.

## Why the correction is firm enough for Ghidra

The sealed proof joins independent evidence instead of inferring ownership from
one call or one decompile:

- strict retail RTTI places `0x004264a0` in slot 6 of the
  `CCollisionSeekingThing` and `CCSPersistentThing` vtables and in the inherited
  vtables of `CCSRay`, `CCollisionSeekingInfantryBloke`, and
  `CCollisionSeekingRound`;
- strict RTTI places `0x004269b0`, `0x00426a00`, and `0x00426a20` in the
  corresponding `CCSPersistentThing` base slots, with inherited placements
  retained explicitly;
- five independently named destructors from four derived/base families call or
  tail-jump to `0x004263f0`, and its body installs the
  `CCollisionSeekingThing` vtable before releasing shared monitor/listener
  state;
- the supplied source allocates `CCSPersistentThing` and invokes its virtual
  `Init`, initializes the delayed-start event fields, and dispatches listener
  events through `HandleEvent`; these source facts agree with the retail slot,
  callsite, constant, and body landmarks without pretending the absent retail
  collision source was recovered;
- four applicable PC-demo bodies are normalized-instruction-identical to the
  retail bodies, providing a second-build check on address-local code identity.

The mechanical owner is
[`re_collision_component_identity_reproof.py`](../../tools/re_collision_component_identity_reproof.py).
Its READY receipt is
`local-lab/collision-component-identity-reproof-20260812-v1/proof.ready.json`
(20,927 bytes, SHA-256
`63b88d3179edde082c915ac269b98ea26fd6fe3e2ab8e1315e11a0adad2e1ddb`).
Eight focused proof tests pass.

## Saved promotion and recovery

The mutation was first reproduced in two independent persistent scratch
projects. Rollback was exercised both after the first change and after the
inner mutation transaction. Separate processes then read back the scratch and
live states. The live authority sealed exactly five name, displayed-signature,
comment, and function-tag changes against the expected PRE image; the other
8,131 internal function rows and all program-wide structural metrics remained
unchanged.

- PRE backup:
  `D:\BEA-Ghidra-Backups\2026-08-12-collision-component-identity-pre-live\`
- verified POST backup:
  `D:\BEA-Ghidra-Backups\2026-08-12-collision-component-identity-post-live\`
- live promotion receipt:
  `local-lab/ghidra-collision-component-identity-live-promotion-20260812-v1/live-promotion.ready.json`
  (8,008 bytes, SHA-256
  `b2a19bae9c420f1b2e12b2ff20d516c3031fa2fe09105ec92475cf6832635246`)
- tracked-snapshot restore receipt: 5,965 bytes, SHA-256
  `26514c374373012618334adfde814e4ec4dc2a45e492ca2d4f7b184497933811`
- POST-backup restore receipt: 5,945 bytes, SHA-256
  `d659878c3221e0990a614cc5ba11ddf28fa4898b97c314938d1f1aed4d3d08ed`

The POST backup and tracked project each contain 19 project files totaling
186,502,021 bytes. Their canonical sorted
`sha256<TAB>bytes<TAB>relative-posix-path<LF>` inventory SHA-256 is
`83330f4eae490686932d6b06fb6826019fb5e578b3b99ebee6cca7bf69cd70bb`.
Both were reopened read-only and reported the expected imported-program MD5
`3b456964020070efe696d2cc09464a55`.

## Claim boundary

This promotion establishes bounded static implementation identity. It does not
establish exact runtime cadence, geometry, all side effects, failure behavior,
complete object layouts, source-body equality, reconstruction mapping, or
`REBUILD_READY` status. The five Ghidra comments retain those limits and the
cheapest next falsifiers.
