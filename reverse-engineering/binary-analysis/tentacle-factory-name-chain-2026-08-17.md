# CTentacle factory-name chain — evidence and rehearsal

Status: **promoted.** Both ceremonies landed on live through the shared cohort
framework: `db.18622` → `db.18623` → `db.18624`, tracked snapshot refreshed on
proven byte equality.
Last updated: 2026-08-17.
Evidence: MEASURED — RTTI Complete Object Locator anchors re-derived from the
pristine specimen bytes, a read-only export of all 86,721 symbols proving each
proposed name free at its own ceremony's gate, per-ceremony identity, dry-run,
apply and separate-process readback receipts, and collateral over all 8,329
function rows showing exactly one changed row and zero non-target movement.
Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Summary: the three CTentacle factory names at vtable slots 117/118/119 were
rotated by one. Slot 117 was corrected by the 2026-08-17 name cohort. This
document records the byte evidence for the remaining two, the two-ceremony
staging they required, the scratch rehearsal, and the two live ceremonies with
their measured collateral.

## What is wrong, and how it is known

`CTentacle`'s vtable head is `0x005e3f9c` (the `colOffset=0` Complete Object
Locator, i.e. the complete object). Three consecutive slots hold three factories:

| Slot | Slot address | Factory | Class its vtable names | Name it carried | Name now |
| --- | --- | --- | --- | --- | --- |
| 117 | `0x005e4170` | `0x004f0760` | `.?AVCMCTentacle@@` (via callee) | `CreateTentacleGuide` | `CTentacle__CreateMCTentacle` |
| 118 | `0x005e4174` | `0x004f07e0` | `.?AVCTentacleGuide@@` | `CreateTentacleAI` | `CTentacle__CreateTentacleGuide` |
| 119 | `0x005e4178` | `0x004f0860` | `.?AVCTentacleAI@@` | `CreateWarspiteAI` | `CTentacle__CreateTentacleAI` |

Every value below was re-derived from the pristine specimen
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
(2,506,752 bytes) and, independently, from the live database's own memory image.
The flat mapping `fileOffset = VA - 0x400000` was proved from the PE section
table rather than assumed: it holds for `.text` (`0x00401000`/raw `0x1000`),
`.rdata` (`0x005d8000`/`0x1d8000`) and `.data` (`0x00622000`/`0x222000`), and
does **not** hold for `.rsrc` (`0x009d5000`/`0x261000`).

**`0x004f07e0`** — body `0x004f07e0`–`0x004f085a`, 123 bytes. At `0x004f0827` it
executes `c7 06 6c f4 5d 00` = `mov dword ptr [esi], 0x005df46c`. That immediate
occurs **exactly once in the whole `.text` section**, and the function enclosing
that one occurrence is `0x004f07e0`. `[0x005df46c-4]` is COL `0x00616cd0`
(`signature=0`, `colOffset=0`); its type descriptor is `0x00632cf0`, whose
mangled-name field at `0x00632cf8` reads `.?AVCTentacleGuide@@`. Its class
hierarchy descriptor `0x00616cc0` lists four bases:
`CTentacleGuide, CGuide, CMonitor, IListener`.

**`0x004f0860`** — body `0x004f0860`–`0x004f08e3`, 132 bytes. At `0x004f08ac` it
executes `c7 06 98 f4 5d 00` = `mov dword ptr [esi], 0x005df498`, again the only
occurrence of that immediate in `.text`, again enclosed by this function.
`[0x005df498-4]` is COL `0x00616d28` (`colOffset=0`) → TD `0x00632d10` → name at
`0x00632d18` = `.?AVCTentacleAI@@`; CHD `0x00616d18` lists
`CTentacleAI, CUnitAI, CMonitor, IListener`.

**Warspite is refuted by its own class.** `CWarspiteAI` exists separately: its
type-descriptor struct begins at `0x0063d110`, its mangled-name field is at
`0x0063d118`, its COL is `0x00617198`, and it has its own vtable `0x005dfbdc`
whose slot 0 is `0x004ff330`. That vtable's immediate appears once in `.text`, at
`0x005044ae`, inside the function beginning `0x00504460` — nowhere near
`0x004f0860`. Its CHD bases are `CWarspiteAI, CUnitAI, CMonitor, IListener`, so
it is a *sibling* of `CTentacleAI`, not the same class.

**Name freedom, measured rather than asserted.** A read-only census of all
**86,721** symbols (26,096 non-dynamic) across every `SymbolType`, every
namespace, dynamic symbols included, found **zero** holders of
`CTentacle__CreateTentacleGuide` and **exactly one** holder of
`CTentacle__CreateTentacleAI` — `0x004f07e0` itself. That single holder is the
whole reason this is a chain. The instrument is
[`tools/GhidraInspectTentacleChain.java`](../../tools/GhidraInspectTentacleChain.java),
which opens no transaction and calls no mutator.

## Two corrections to the record

1. **The `CWarspiteAI` anchor address was quoted 8 bytes off.** Prior notes place
   "a separate `.?AVCWarspiteAI@@` type descriptor at `0x0063d118`". `0x0063d118`
   is the descriptor's mangled-**name** field; the `TypeDescriptor` struct starts
   at `0x0063d110` (`pVFTable = 0x005e5aa4`, spare `0`). The refutation is
   unaffected — the project's `@file` convention quotes name-string locations —
   but "type descriptor at" is the wrong words for that address.
2. **`0x004f0760` installs no vtable in its own body.** Its 118-byte body calls
   `0x005490e0` then `0x0049cad0`, and it is `0x0049cad0` that installs
   `0x005dc450` = `.?AVCMCTentacle@@`. So the already-landed `CreateMCTentacle`
   rests on a one-hop callee chain, while the two remaining rows install their
   vtables *directly*. Any future claim of a direct in-body install for
   `0x004f0760` is wrong.

A third, downstream correction is applied in
[`functions/MCTentacle.cpp.md`](functions/MCTentacle.cpp.md): Wave1021 named the
caller of `0x0049cad0` as `CTentacle__CreateTentacleGuide`, a name that has since
moved off `0x004f0760` and is destined for `0x004f07e0` — a function that never
reaches `0x0049cad0`. The caller is now pinned by address.

## Why two ceremonies, and why one cohort cannot work

Row B wants the name row A currently holds. Because this Ghidra build has **no
usable in-process rollback** (measured 2026-08-17: `endTransaction(id, false)`
does not revert, `canUndo()` is false, and a headless write advances the db
version even when the script throws), every non-mutating gate must pass *before*
the first write. A single cohort therefore cannot clear both rows: any honest
pre-flight check rejects row B while row A still holds the name.

That is not a hypothesis. The shared framework, handed the chain as one cohort,
refuses on its `noCycle` and collision gates — and handed ceremony B's one-row
spec against an un-swapped database it refuses with three independent failures:

```
PRE function NAME digest ee545445… != pinned 8485ddc9…
PRE frozen-census digest fc12cad5… != pinned b1a31f0b…
0x004f0860: collision: proposed name 'CTentacle__CreateTentacleAI' for 0x004f0860 already exists at 0x004f07e0
```

The collision literal is the same one the single-cohort attempt produced, so
splitting the chain into two one-row cohorts **keeps** the cycle and collision
gates rather than routing around them. Landing A frees the name; only then does
B's spec become satisfiable.

## What was rehearsed

Both ceremonies run through the shared framework
(`tools/GhidraApplyCohortManifest.java`) as two one-row `SET_NAME` cohorts —
[`tentacle-chain-a.spec.tsv`](../../tools/cohort-specs/tentacle-chain-a.spec.tsv)
and [`tentacle-chain-b.spec.tsv`](../../tools/cohort-specs/tentacle-chain-b.spec.tsv)
— against a replica restored byte-identically from an off-volume PRE backup of
live `db.18622`. No bespoke applier is involved and no new gate was written.

| Step | Ceremony A | Ceremony B |
| --- | --- | --- |
| `identity` | PASS | PASS |
| `dry` | PASS | PASS |
| `apply` | PASS | PASS |
| `readback` (separate process) | PASS | PASS |
| `functionsExamined` | 8,329 | 8,329 |
| `functionsChanged` | 1 | 1 |
| `functionsUntouched` | 8,328 | 8,328 |
| `columnsMoved` | `{name=1}` | `{name=1}` |
| symbols pre/post | 26,096 / 26,096 | 26,096 / 26,096 |
| symbols added/removed | 1 / 1 | 1 / 1 |
| frozen-census digest | `fc12cad5…` → `b1a31f0b…` | `b1a31f0b…` → `c7bdf231…` |

An independent external diff of the full 8,329-row inventory taken before and
after both applies — computed outside the framework, from separate-process
exports — shows exactly **two** changed rows (`0x004f07e0`, `0x004f0860`), **zero**
frozen-column movement, and **zero** program-scope metric movement across all
metrics the inventory reports (`memorySha256`, `instructionLayoutSha256`,
`definedDataSha256`, `nonFunctionSymbolsSha256`, `referencesSha256`,
`commentsSha256`, `relocations`, and every count). On each target row only the
nine name-derived columns moved, and the rendered prototype moved by exactly the
name substitution:

```
void __fastcall CTentacle__CreateTentacleAI(void * this)
   -> void __fastcall CTentacle__CreateTentacleGuide(void * this)
void __thiscall CTentacle__CreateWarspiteAI(void * this, void * init_context)
   -> void __thiscall CTentacle__CreateTentacleAI(void * this, void * init_context)
```

`bodyDigest` is byte-identical on both rows before and after.

### Refusal paths exercised

Twelve provocations, all in replicas, none in write mode against live:
containment (rehearsal instrument pointed at live; live twin pointed at a
replica; both twins pointed at the tracked snapshot), tampered manifest, wrong
caller-supplied digest, unknown ceremony, ceremony B before A, re-applying a
landed ceremony, and the absolute no-collision gate provoked three ways — a
single foreign-namespace `ANALYSIS` label, 218 such labels, and a label planted
on a function entry point.

**One ordering finding worth keeping.** Planting the colliding labels on
*function entry points* refuses one gate **earlier** than the collision gate: a
created label can take primary at an entry whose function symbol is a default
name, which moves `Function.getName(true)` and trips the whole-database PRE
name-digest gate first (measured: expected `ee545445…`, actual `d31ce246…`). That
is a stronger refusal, not a weaker one, but it means the collision gate can only
be isolated by planting holders where no functions live — initialized `.data`.

## Reversibility

Never claimed as rollback. In-process rollback is recorded as
`NOT_AVAILABLE_MEASURED_2026_08_17`. The only reversibility claim these receipts
carry is ceremony-level restore from a verified off-volume PRE backup, and it was
demonstrated: the backup was written, proved byte-identical to live across all 19
payload files (187,239,301 bytes), restored to a scratch location, proved
byte-identical again, and reopened read-only with the program identity asserted
(`BEA.exe`, md5 `3b456964020070efe696d2cc09464a55`, sha256 `74154bfa…7750`).

Read-only opens were separately measured to be inert: the replica tree digest was
byte-identical after each `-readOnly` run, and live's digest and db version set
were byte-identical after the read-only probes described below.

## The live ceremonies

Both ran through `GhidraApplyCohortManifestLive.java` — the framework's live twin,
not a bespoke applier — with `identity`, `dry`, `apply` and `readback` as four
separate JVM invocations, the first two and the last read-only.

The live twin refuses any cohort id absent from its compiled allowlist, which is
the framework's per-cohort grant surface. Before the grant, measured read-only
against live with live left byte-identical:

```
COHORT_REFUSE reason=cohort_not_live_authorized cohort=tentacle-chain-a
  allowlist=[boundary-cohort41, name-cohort160, abi-cohort294]
```

The grant was then recorded by adding both ids to `LIVE_AUTHORIZED_COHORTS`
through the framework's own reviewed derivation
(`tools/ghidra_cohort_framework_tests.py --emit-live`), which reproduced the twin
with a **one-line** diff and left all 49 framework tests passing, including the
negative controls that would catch a weakened pin, a widened mutable-column set,
a smuggled verb, or a reintroduced rollback claim.

**Instrument identity for both live applies.** The framework does not record its
own source digest in its receipts — a gap worth closing — so the instrument is
pinned here by reproduction instead. Both applies used the live twin derived from
the reviewed base at commit `ac659fd9` plus the one-line grant:
**141,393 bytes, SHA-256
`758105c26a757848fd0deebd1f763e0eacbfbc5fd28b4068934d22b3b7021ba8`**. It is
reproducible by replaying `derive_live` over `HEAD:tools/GhidraApplyCohortManifest.java`
and inserting the grant line; the ungranted derivation is
`35feb215…` / 141,345 bytes and reproduces the committed twin exactly. That
instrument contains **no** part of the concurrent manifest-driven-varargs work,
which regenerated the twin to `f570d34e…` only after both ceremonies had
completed.

| | Ceremony A | Ceremony B |
| --- | --- | --- |
| db version before | `db.18622` | `db.18623` |
| db version after | `db.18623` | `db.18624` |
| target | `0x004f07e0` | `0x004f0860` |
| `identity` / `dry` (read-only) | PASS / PASS | PASS / PASS |
| live byte-unchanged after both read-only runs | yes | yes |
| `apply` | PASS | PASS |
| `readback`, separate process | PASS | PASS |
| `functionsExamined` | 8,329 | 8,329 |
| `functionsChanged` / `functionsUntouched` | 1 / 8,328 | 1 / 8,328 |
| `columnsMoved` | `{name=1}` | `{name=1}` |
| frozen-census digest | `fc12cad5…` → `b1a31f0b…` | `b1a31f0b…` → `c7bdf231…` |
| symbols pre/post, added/removed | 26,096 / 26,096, 1 / 1 | 26,096 / 26,096, 1 / 1 |
| external diff: changed rows | 1 (`0x004f07e0`) | 1 (`0x004f0860`) |
| external diff: non-target movement | 0 | 0 |
| external diff: frozen-column drift | 0 | 0 |
| program-scope metrics compared / moved | 29 / 0 | 29 / 0 |
| `bodyDigest` unchanged on the target | yes | yes |
| POST backup verified + restore-proven | yes | yes |
| tracked refresh on proven byte equality | yes | yes |

Ceremony A's measured post-apply frozen digest, `b1a31f0b…`, is exactly the value
ceremony B's spec pins as its **PRE** frozen digest — the pin was written from the
rehearsal measurement before A ran live, and live reproduced it. Ceremony A was
closed in full, including its POST backup and tracked refresh, before ceremony B's
gates were evaluated.

The tracked snapshot is now `db.18624`: 19 files, 187,403,141 bytes, canonical
inventory `1ecf589ac5168ff12f42ba67d10bca13a5ae0104521cd0418924f8c5b3db566b`,
measured byte-identical to live with zero per-file mismatches.

### An integrity gate that fired on our own artifact

The framework pins spec integrity by hashing **raw bytes**, and `.gitattributes`
carries `* text=auto`, so committing normalises CRLF to LF and changes the digest.
Ceremony B's spec was first authored with CRLF, rehearsed at
`53b34527…`, and then normalised — which made the rehearsal receipt name bytes
that no longer existed. The gate was right and the artifact really had changed, so
the fix was to re-rehearse the whole chain from a fresh replica against the
committed LF bytes (`629b47c8…` for A, `6ef24e0e…` for B) rather than to relax the
check. Both live ceremonies then ran against those same committed digests.
