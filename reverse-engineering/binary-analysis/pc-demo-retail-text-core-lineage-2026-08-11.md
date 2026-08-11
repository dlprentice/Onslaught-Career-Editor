# PC demo/retail text-core lineage

Status: active, bounded semantic recovery
Last updated: 2026-08-11
Evidence: MEASURED — exact Ghidra instruction ranges from the pristine retail
program, body-relative demo decoding, normalized instruction comparison,
literal-string equality, mapped callees, and language jump-table targets;
UNKNOWN — runtime locale selection, the contents of every distributed language
file, and fatal-dialog/process behavior.
Verdict: `CText::Init` and `FatalError_LocalizedStringId` are not product-code
divergences. The first whole-function mapper conservatively left them changed
because each retail function has two non-contiguous Ghidra body ranges. Direct
range-for-range comparison now shows zero normalized instruction differences
and preserves every relevant literal, branch target, and callee.

Specimen: pristine PC retail `BEA.exe`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`;
PC demo `BEA.exe`, 2,510,848 bytes, SHA-256
`d8637dd755b21c720c0cb8f71923f94d2a04a184d90f5343c2e868ce8606e5c2`.

The machine-readable result is
[`pc-demo-retail-text-core-lineage-2026-08-11.tsv`](pc-demo-retail-text-core-lineage-2026-08-11.tsv).
It is 1,035 bytes with SHA-256
`3e66b59441c68f62c7d1dc2bfd9da34cea3e455b32186ec4e1bb7505d9897f6b`.
It records both exact instruction streams and their raw-byte hashes. These two
closures reduce the original changed/incompletely-bounded queue to 52.

## Why the first map abstained

The whole-function mapper deliberately required a single contiguous Ghidra
body before declaring a demo body normalized-identical. Both rows violate only
that mechanical precondition:

| Function | Retail Ghidra ranges | Bytes / instructions |
| --- | --- | ---: |
| `FatalError_LocalizedStringId` | `0x0042D080–0x0042D0A5`; `0x0042D0A9–0x0042D0AB` | 41 / 14 |
| `CText::Init` | `0x004F21F0–0x004F22E7`; `0x004F2324–0x004F2496` | 619 / 177 |

The exact retail instruction addresses were taken from the existing Ghidra
export. Each was translated by its paired entry delta and independently decoded
from the demo bytes. Instruction size, mnemonic, opcode/prefix/ModRM/SIB shape,
and bytes after masking only Capstone-reported encoded immediates and
displacements all agree at every row.

## `FatalError_LocalizedStringId`

Retail `0x0042D080` and demo `0x0042D070` have the same 14-instruction contract:

- return when the guard byte is nonzero;
- otherwise forward `stringId` to the localization lookup;
- convert the returned wide string through `FromWCHAR`;
- pass the converted message and caller's code to the fatal exit owner.

Only four raw instruction bytes differ, all in two relocated call operands:

| Retail callee | Demo callee |
| --- | --- |
| `0x00524830 Localization::GetStringById` | `0x00524B40` |
| `0x004F7D30 FromWCHAR` | `0x004F7DD0` |

The terminal fatal-exit call retains the same relative displacement in both
builds. No predicate, argument order, scalar constant, opcode, or control-flow
target changes.

## `CText::Init`

Retail `0x004F21F0` and demo `0x004F2270` preserve all 177 instructions. Their
58 raw-different bytes occur only in relocated code, global, source-path, format,
and language-name operands. Every paired literal has identical content:

| Role | Literal in both builds |
| --- | --- |
| Language names | `english`, `french`, `spanish`, `italian`, `german` |
| Ordinary path | `data\LANGUAGE\%s.DAT` |
| American override | `data\LANGUAGE\american.DAT` |
| Invalid-language diagnostic | `ERROR: unkown language %d` |
| Unknown-version diagnostic | `unknown version in text file` |
| Source owner | `C:\dev\ONSLAUGHT2\text.cpp` |

The American-English global moves from retail `0x0083D990` to demo
`0x0083EC50`, matching the parser and shell consumers already recovered in the
startup report. The five-entry language switch table also preserves the exact
body-relative destinations in both builds:

`0x9A, 0x6B, 0x72, 0x79, 0x80`.

The rest of the body retains the released loader contract: reject re-init,
choose the language path, load through `CDXMemBuffer`, allocate and retain the
file bytes, recognize legacy and `0xFFFFFFBB` versioned layouts, establish text
and audio-name tables, preserve optional high-bit metadata, close the buffer,
and mark initialization complete.

This matters architecturally: demo-specific language fallback is policy in the
command-line/global producer. The text parser/loader itself is unchanged.

## Boundary and next use

The result proves instruction and operand-role equivalence for the exact body
ranges plus literal and switch-target equality. It does not prove that demo and
retail ship identical language-file contents, that the same locale is selected
in every launch environment, or that fatal errors are reached the same way.

These are instrument false negatives, not excuses to weaken the original map.
Keeping the conservative map immutable and recording a narrower second-pass
closure preserves both facts: why the first method abstained and what direct
reading subsequently established.
