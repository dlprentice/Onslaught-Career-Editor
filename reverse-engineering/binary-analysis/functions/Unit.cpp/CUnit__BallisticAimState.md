# Pod ballistic launch and aim

Status: active static and bounded original-code contract; historical path retained
Last updated: 2026-10-01 (Pod ownership, constants and native aiming comparison)
Summary: launch-state writes, pitch search and its uninitialized-output paths; not live projectile acceptance.
Specimen: pristine `local-lab/safe-copy-bea-pristine/BEA.exe.original.backup`, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.

## Identity and launch boundary

This page's old `CUnit` labels described inherited storage but obscured the concrete
Pod owner. Retail RTTI identifies the primary table at `0x005dff8c` as `CPod`, with
`CUnit` immediately below it in the base hierarchy. Its slot `+0xb4` points to the
seven-byte gravity getter `0x004d38b0`, returning binary32 0.001 from `0x005d8580`.
The reconstructed source calls these methods `CPod::Launch` and `CPod::Aim`;
their original source spellings are not established by this experiment.

| Address | Saved Ghidra label | Current reconstruction |
| --- | --- | --- |
| `0x004d36c0` | `CUnit__InitBallisticAimState` | `CPod::Launch(FVector)` |
| `0x004d3730` | `CUnit__ComputeBallisticLaunchVelocity` | `CPod::Aim()` |

Fresh instructions confirm that Launch receives the receiver in ECX and a four-word
vector on the stack, returning with `ret 0x10`. When `+0x254` is zero, it copies all
four words to `+0x258..+0x264`, calls `0x0047eb80` with ECX `0x006fadc8` and EDX
pointing at the input vector, and stores the returned height at `+0x260`. It then
calls Aim, writes 1 to `+0x254` and 0 to `+0x250`. This replaces the earlier unverified
`CStaticShadows` name for the height call with its measured address; the sampler
and complete launch/script chain were not executed in the October 1 comparison.
The Launch reconstruction is an exact whole-section/relocation control in the fresh Pod build.

Aim has no stack arguments and uses ECX as its receiver; the old `__fastcall`
display is not evidence of an EDX argument. This documentation correction does
not change the saved Ghidra project.

## Measured aiming behavior

The original body is `[0x004d3730,0x004d3887)`, 343 bytes. It derives yaw from the
target at `+0x258/+0x25c` and position at `+0x1c/+0x20`, and height difference from
`+0x260` and `+0x24`. The speed field is read through `receiver+0x164`, offset
`+0xb4`, multiplied by binary32 0.05 (`0x005d8584`) and stored as binary32.

The pitch search starts at binary32 −π/2 (`0x005d85c8`), adds binary32 0.02
(`0x005d8cb8`) and continues while the running angle is below zero. For each
angle it requires a positive discriminant, positive horizontal travel and an
absolute horizontal-distance error strictly below the best error. The initial
best error is 99999.0. Only an improving iteration writes the selected pitch.
These are instruction-level floating-point operations, not an assertion that
an algebraically equivalent ballistic formula will reproduce their rounding.

The tail calls the original Euler matrix helper `0x004062d0`, scales its forward
column by the stored speed and writes velocity XYZ at `+0x7c/+0x80/+0x84`.
It also copies a fourth word to `+0x88` from an unwritten stack slot.

**A failed search does not supply a default pitch.** If no iteration improves the
sentinel, `0x004d3825` reads the unwritten pitch slot. This occurs in finite authored
positive-speed cases as well as zero/negative-speed probes. With both positions
zero and the raw speed field 2000 (scaled speed 100), stack seeds 0.125, −0.75
and 1.25 produce different launch directions. Whether actual shipped descriptors
and gameplay reach this state remains open; this is not a reported player-visible bug.

## Native comparison and limits

The lead freshly compiled Pod and reproduced 5,940 finite cases under masked x87
PC24/PC53/PC64, round-to-nearest, with three finite stack seeds per logical state.
The complete original and candidate Aim execute with the actual Pod gravity
getter and original Euler helper; all other code traps. Receiver/data guards,
input preservation, stack canaries, callee-saved registers, ESP, control word,
FPU stack state and exception flags are checked. The observed internal values,
velocity words, object state and exception flags agree throughout.

There are 2,061 cases with no pitch update: 594 zero-speed, 1,161 positive-speed
and 306 negative-speed cases. All 687 corresponding three-seed groups show
bitwise XYZ dependence on the stack seed. The fourth velocity word retains its
seed even when a pitch is successfully chosen. Doubling the search step to 0.04
changes 2,208 observations; missing-vtable and truncated-input controls fail.

The candidate remains unmatched: a 368-byte section with seven relocations
versus the 343-byte retail body. All 13 exact Pod controls survive. Finite agreement
does not establish arbitrary-input equivalence, original source, live FPU settings,
shipped-state reachability or reconstruction parity. No source fix or match credit
was inferred from the agreeing experiment. The cheapest next runtime falsifier is
a controlled original Pod launch with a recorded descriptor, entry state and stack;
it requires a separately admitted game execution route.

Private root evidence in `bea-decomp/.worktrees/codex-equiv-20260930/`:
`local-data/pod-aim-root-20261001/native-full-v01/receipt.json`, SHA-256
`131a7fdf448207be106f015ddc4a4b7ca77aa42a7e5526830436223739cbb7bb`;
inputs SHA-256 `30ee3a01eadc607841546a7dde15266701345b6736d1dccaf3acb3d8ddb345d6`.
Inputs and all original/candidate/control output bytes reproduce the worker's
frozen run. `static-readback/` holds the separate Launch and gravity instruction reads.
