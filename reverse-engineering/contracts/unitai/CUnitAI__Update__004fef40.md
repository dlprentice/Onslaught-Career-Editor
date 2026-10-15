# CUnitAI__Update

Status: active PC retail/demo static contract with deterministic rebuild boundary
Last updated: 2026-08-28
Summary: exact branch, side-effect, random-consumption, return-delay, and event-3000 scheduling contract for shared `CUnitAI` virtual slot 3 at `0x004fef40`.
Evidence: MEASURED — pristine retail instructions and constants were independently decoded; the complete PC demo body and its event-3000 caller reproduce the same normalized instruction stream; no runtime or console equivalence is claimed.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: not_applicable (the pinned source drop has no UnitAI implementation) | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x004fef40`

## Identity

- Body `[0x004fef40,0x004ff322)`: 994 bytes, 300 instructions, raw pristine-body SHA-256 `7aca029cc9b576958d86a01282e847e6b624d29dcbc23b4ae2b89cbf8193fffe`.
- PC demo correspondent `[0x004feff0,0x004ff3d2)`: 994 bytes, 300 instructions, raw SHA-256 `6b676728052401d5acfdabedae081ad48bca95557f080629b59c471afa2a45c6`.
- Independent Capstone decode found equal mnemonic and instruction-size sequences. Zeroing only encoded immediates/displacements produced the same SHA-256 `d0cd8f0e845a2589b53a61373cc9d08d809a3e7a38086ebed8eb0183bd6b8b34`; the 41 raw-different instructions / 60 bytes are relocated calls, globals, or constants.
- The nine referenced zero/jitter/step/base/pitch-bias scalar dwords are byte-identical at their relocated demo addresses; normalized instruction identity is therefore not being used to hide a changed cadence constant.
- This is virtual slot 3 (`+0x0c`) shared by 16 PC retail/demo AI vtables: `CBoatAI`, `CCarrierAI`, `CCarverAI`, `CComponentBomberAI`, `CFenrirMainGunAI`, `CGillMAI`, `CGroundAttackAI`, `CInfantryAI`, `CMechAI`, `CPlaneAI`, `CRepairPadAI`, `CSubmarineAI`, `CTentacleAI`, `CUnitAI`, `CWarspiteAI`, and `CWarspiteDomeAI`. The old decompiler name `CWarspite__Update` was too narrow.
- The packet closure digest is `e39944ad5f5c17b54941b7ff7204609f72aecb3f98553dd5109773fb2d6ff305`. Packet metadata remains provenance, not the basis of the branch claims below.

## Calling convention

- Receiver is in `ECX`; there are no stack arguments and the body uses a bare
  `ret`.
- The result remains in x87 `ST0`; no hidden return buffer is used.

## Prototype and parameter semantics

```c
double-x87 __thiscall CUnitAI__Update(CUnitAI *this);
```

`this` is the shared Unit-AI state owner. Its deletion-aware reader and branch
fields are read at the offsets documented below. There are no explicit
parameters; captured virtual results and RNG values are adapter inputs only in
the deterministic reconstruction boundary, not in the retail ABI.

## Return value meaning

- The x87 result is the delay used by the enclosing event-3000 handler, not an
  angle and not an opaque “float-like” result.
- `CUnitAI__VFunc_9_004fec60` calls slot 3 at `0x004feefd`, optionally discards its result in favor of positive zero, adds event-manager time without an intervening float store, then stores the absolute due time once as float32.
- That caller schedules event `3000` (`0x0bb8`) to the same AI at start-of-frame priority `0`, with null data, and passes its incoming scheduled-event pointer as the reuse object. It does not allocate a fresh event for the ordinary cadence loop.
- Retail caller `[0x004fec60,0x004fef40)` is 736 bytes / 229 instructions, raw SHA-256 `31974fd1b8d3abc3adc6d2ba0e3007478b5113af8c936caf9221dc5e89927911`. Demo `[0x004fed10,0x004feff0)` is raw SHA-256 `c86710170e63bffce43deedd2b4d66277039e2e05ad557a163b52ec8ca359fab`; both normalize to `7afed8ca31a90a7030131f9bb29429f9599702e949ddf7c576396041649e1216` with identical 229-instruction shape.

## Globals read/written

The body consumes the shared gameplay RNG through `Random__NextLCGAbs`; its
enclosing caller reads event-manager time and schedules through the event
manager. No direct mutable-global store is established in slot 3. Its owned
writes are the AI jitter/target fields `this+0x34`, `+0x48..+0x5c`, reader and
support state `this+0x0c/+0x10`, and owner idle flags `+0x1e8/+0x1ec`, subject
to the mutually exclusive arms below.

## Behavior summary

Every invocation first calls this AI's virtual slot 4, currently documented as `CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0`, and then owner virtual `+0x150`. The following arms are mutually exclusive.

### Primary/current-target arm

This arm requires owner virtual `+0x150` to return nonzero and deletion-aware reader `this+0x0c` to be nonnull.

If profile `[[owner+0x164]+0x19c]` is nonzero:

1. Call target virtual `+0x168`, writing the four-float target point at `this+0x34`.
2. Consume four shared `Random__NextLCGAbs` results in order.
3. Store `this+0x48` and `this+0x54` as `float32(low16 * 0x3523d70a + 0x3d23d70a)`, i.e. approximately `0.04 + low16*(0.04/65536)`.
4. For draws three and four independently negate `+0x48` / `+0x54` only when `low16/65536` is strictly greater than `0.5`; equality at `32768` does not negate.
5. Store `+0x4c=+0x48`, `+0x50=-+0x48`, `+0x58=+0x54`, and `+0x5c=-+0x54`; rotate the target-relative vector through the local Euler matrix; then call `CUnit__ForwardAimTransformAndAttachTargetReader` using a fresh read of `this+0x0c`.
6. Set the returned delay to positive zero.

If profile `+0x19c` is zero, call the forward-aim helper with the entry target and `this+0x34`, consume one random result, and store the delay local as float32 `0.5 + low16/65536`.

Both sub-arms then call owner virtual `+0x128`. If the profile value at `[[owner+0x164]+0x128]` is nonzero after that call, they invoke `SetReader(this+0x0c,null)`, run the support/attack-provider helper with null, and zero `this+0x10`. This cleanup does not roll back the already-issued aim call or returned delay.

### Fire-support arm

When the primary arm is not admitted, nonzero `this+0x18` plus a nonnull fresh `this+0x0c` selects this arm:

1. Run the support/attack-provider helper on that reader.
2. If the then-current profile `+0x19c` is zero and owner field `+0x168` is not `1`, reload the reader, call its virtual `+0x168` into `this+0x34`, reload the reader again, and invoke forward aim. A null reader at the indirect virtual call would fault; there is no recovery branch.
3. Call owner virtual `+0x158`.
4. Return `CWarspite__GetMountedUnitPitchOrZero(owner) + float32(0.1)` in x87 precision. This arm consumes no random result.

### Idle arm

Every other state:

1. Writes owner `+0x1ec=0`, then owner `+0x1e8=0`.
2. Calls `CWarspite__TransitionToUndeploying` when profile `+0x108` is nonzero.
3. Re-reads owner `+0x110` after that call and consumes one random result.
4. Nonzero `+0x110` returns `1.5 + low16/65536`; zero returns `3.0 + low16*(2/65536)`. Neither expression is stored to float before returning in `ST0`.

The authored meanings of profile `+0x108/+0x128/+0x19c`, owner `+0x110/+0x150/+0x158/+0x168`, and the jitter cells remain open. Offset-bearing names are retained rather than guessed.

## Floating-point and random law

- The shipped constants are exact float32 bits: jitter step `0x3523d70a`, jitter base `0x3d23d70a`, unit step `0x37800000`, double step `0x38000000`, half `0x3f000000`, pitch bias `0x3dcccccd`, short base `0x3fc00000`, and long base `0x40400000`.
- The repeated `and eax,0x8000ffff` plus sign fix-up is MSVC's signed remainder-by-65536 lowering. `Random__NextLCGAbs` sign-normalizes its ordinary output, so observed samples are the low 16 bits; the exact lowering remains relevant at the `INT_MIN` edge.
- PC retains the fire and idle delay expressions on x87. The Win32 process precision control is 53 bits, so a binary64 intermediate reproduces these sums for float32 operands. Rounding pitch bias before adding manager time is observably wrong: manager time bits `0x4192430b` and pitch bits `0x3f2924b6` produce due bits `0x419858fd`; float-rounding the pitch sum first produces `0x419858fe`.
- The caller's preceding aim-convergence path sets a local flag that discards the slot-3 delay and schedules at current manager time. Slot 3 still performs its complete branch and consumes its branch-specific random results before that override.

## Error / edge behavior

- The fire-support aim-refresh path reloads `this+0x0c` before its indirect
  virtual call but has no null recovery; a concurrent/stage-local null value
  would fault.
- `Random__NextLCGAbs` normally returns a sign-normalized value, while the
  compiler's signed remainder lowering retains a distinct `INT_MIN` edge.
- Profile pointers, owner pointers, and virtual results are trusted. Corrupt
  pointers or non-finite virtual pitch values have no accepted bounded witness.
- The caller may discard a fully computed delay after this body has already
  performed its branch effects and consumed RNG; that is released ordering,
  not rollback.

## Callees relied on / callers

- `CGenericActiveReader__SetReader` `0x00401000` ×1.
- `vector_constructor_iterator_nothrow` `0x004011b0` ×1.
- `Vec3__SetXYZ` `0x00401ec0` ×3.
- `Mat34__SetFromEulerAngles_004062d0` `0x004062d0` ×1.
- `Random__NextLCGAbs` `0x004de8d0` ×7 static sites across mutually exclusive arms.
- `CUnit__ForwardAimTransformAndAttachTargetReader` `0x004fb650` ×3.
- support/attack-provider helper `0x004fb840` ×2.
- mounted-unit pitch helper `0x004fbc90` ×1.
- undeploy transition `0x004fde70` ×1.

Indirect calls are this slot 4, owner slots `+0x150/+0x128/+0x158`, and target slot `+0x168`. Exact instruction order—not callee labels—is the authority.

## Rebuild carry-forward

`RetailUnitAIUpdateTransaction` reproduces the five finite paths, stage-local reader identities, ordered calls/writes, exact random-result consumption, final jitter cells, returned delay, caller zero override, and absolute event-3000 due bits. It accepts already-captured virtual results and random values so the shared RNG is not consumed before an earlier side-effecting virtual call. Concrete monitors, geometry/matrix execution, helper bodies, event dispatch, and actor wiring remain adapter-owned.

Six focused tests cover both primary sub-arms, fire-support with and without aim refresh, both idle cadences, strict sign equality, target rereads, clear-tail order, caller override, and the one-bit x87 rounding discriminator. They are contract tests, not proof of autonomous gameplay parity.

## Runtime corroboration (TTD, bounded)

No controlled-runtime execution row is claimed for this VA. Existing evidence
is exact PC retail static reconstruction plus an independently normalized PC
demo body and caller. Those establish duplicated machine-code structure, not
natural branch frequency, live pointer validity, or console behavior.

## Evidence

- Canonical disassembly summary: `reverse-engineering/binary-analysis/functions/IScript.cpp.md`, rows for `0x004fec60` and `0x004fef40`.
- PC retail/demo body map: `reverse-engineering/binary-analysis/pc-demo-retail-virtual-target-map-2026-08-11.tsv`.
- Packet: `D:/packet-runs/wave1-contracts-20260822/packet-0x004fef40.json`, schema `bea.re.triage-packet.v1`, SHA-256 `ec950bb31e461a9ab0ad94b40f9e794bb2590ecc35e4708121ac5fba1a9375d8`.
- Displayed decompile SHA-256 `77c66f4c1018ca9940b8e60b676339ec87a2703e2703ae5846b82e2df48a8124`.
- Pinned `references/Onslaught/eventmanager.cpp`,
  `references/Onslaught/scheduledevent.cpp`, and
  `references/Onslaught/activereader.cpp` independently support event
  reuse/scheduling and reader architecture. The pinned source drop contains no
  UnitAI implementation and does not prove the branch fields.
- No Ghidra project was changed. A symbol/comment promotion would still require the separate Ghidra backup, scratch, apply/readback, and independent-refutation gate.

## Confidence

1 — exact PC retail identity, complete branch/action/random/return law, enclosing event-3000 consumer, constants, and independently reproduced demo instruction shape are closed. Authored field names, virtual/helper side effects, runtime scenario distribution, console correspondence, and autonomous integration remain open.

## Unresolved questions

- Authored meanings of profile fields `+0x108/+0x128/+0x19c`, owner fields
  `+0x110/+0x150/+0x158/+0x168`, and the two jitter-cell pairs remain open.
- Concrete helper side effects beyond the ordered calls and stores proved here,
  natural runtime branch distribution, exceptional pointer/value behavior,
  and autonomous actor integration remain open.
- Console correspondence requires independent MIPS/PPC reconstruction; PC
  retail/demo identity does not establish it.

## Cheapest falsifiers

- A cold decode of either named body that changes one mnemonic, instruction size, branch edge, constant bit pattern, or random-site order invalidates the static contract.
- A controlled copied-runtime breakpoint at slot 3 that observes a returned delay outside the selected arm's domain, different draw count, or a non-3000/non-reused caller admission invalidates the transaction mapping.
- Console promotion requires independent MIPS/PPC body and caller reconstruction; vtable placement or a plausible label alone is insufficient.
