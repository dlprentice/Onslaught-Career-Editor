# The Mission script-command registry, recovered from shipped data

Status: active, bounded static registry recovery
Last updated: 2026-08-12
Evidence: MEASURED — abstract interpretation of the stores in
`ScriptCommandRegistry__InitBuiltins` against the pristine specimen,
reconstructing the record array at `0x0064CE20` and reading its name/handler
pairs, joined to the current tracked Ghidra name projection; UNKNOWN — every
handler signature, argument contract, side effect and runtime behaviour, none of
which this recovery addresses.
Verdict: 144 script commands are paired with handler addresses by the game's own
data. 110 handlers resolve to known function entries and 54 of those functions
still carry default names, so the registry supplies a shipped-data name for 54
currently unnamed functions. No name was promoted to Ghidra.
Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Structure

`ScriptCommandRegistry__InitBuiltins @ 0x0052FF30` (13,429 bytes) populates a
record array at `0x0064CE20` using `mov [absolute], reg` and
`mov [absolute], imm` stores, holding shared constants in registers across long
runs. Interpreting those stores abstractly — tracking `mov reg, imm`,
`xor reg, reg`, and clearing on `call` — reconstructs the table with **zero
stores left on an untracked register**.

| Property | Value |
| --- | --- |
| Record stride | `0x40` |
| Command-name pointer | record `+0x00` |
| Handler function pointer | record `+0x30` |
| Records recovered | 144, terminating cleanly at index 144 |
| Handlers resolving to a known function entry | 110 |
| Handlers on still-default `FUN_` names | 54 |
| Handlers on the shared no-op | 1 |

The 144 count independently matches the 144-slot native table reached from the
opposite direction by the compiled-script work, which indexes this table with a
`CALL` operand masked to `& 0xff`.

## Two independent channels agree on three names

The same day, the
[PC-native source-coordinate instrument](pc-native-source-coordinates-2026-08-12.md)
singled out `0x005359D0`, `0x00535A30` and `0x00535A90` as unnamed functions
carrying exact `IScript.cpp` coordinates at lines 1158, 1173 and 1188. The
registry assigns those same three handlers the commands `GetRealHealth`,
`GetInitialHealth` and `SpawnersEmpty`.

Unlike the PC/Xbox coordinate pair — which share a signal and must not be cited
as mutual corroboration — these two channels are genuinely independent: one reads
debug-allocator arguments, the other reads a registrar's stores.

## A named dormant capability

Exactly one handler is the shared no-op, and its command is **`SetSpeed`**. The
mission language can call it, and this build accepts the call and does nothing.
The cheapest falsifier is a mission script that calls `SetSpeed` and observes no
effect.

## Boundary

A registry string is the **script-facing command name for that slot**. It is not
a recovered C++ symbol, and mapping it onto the existing `IScript__<Command>`
convention would be a well-supported naming choice rather than a proven identity.
This recovery establishes no handler signature, argument contract, write set,
failure behaviour or runtime semantics; the Generation 15/16/19 work on `SetPos`
and `UnsetObjective` shows what a real contract for one of these costs.

34 of the 144 handlers did not resolve to a known function entry, and whether
those are unrecovered boundaries or non-entry targets is untested here.

**No Ghidra mutation was made and none is authorised by this report.** Promoting
any of these names requires the full gate in
[`reverse-engineering/ghidra/README.md`](../ghidra/README.md). The mechanical
owner and its receipts are machine-local under
`local-lab/mission-native-registry-20260812-v1/`; the recovered pairing is
[`mission-script-command-registry-2026-08-12.tsv`](mission-script-command-registry-2026-08-12.tsv).
