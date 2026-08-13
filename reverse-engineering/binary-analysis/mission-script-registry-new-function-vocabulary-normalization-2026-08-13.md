# MissionScript new-function vocabulary normalization

Status: isolated scratch validated; live Ghidra promotion remains forbidden
Last updated: 2026-08-13
Evidence: MEASURED — the shipped 144-slot MissionScript registry, the exact
promoted 34-function boundaries, current db.18610 readback, and the reviewed
row-specific static-contract table; INFERRED — only mechanism wording already
marked as such in that table; UNKNOWN — original C++ symbols and signatures,
runtime reachability and causality, complete semantics, source equivalence, and
reconstruction parity.
Verdict: exactly 34 newly admitted default-metadata functions may receive
Tier-2 script-facing names, bounded static-envelope comments, and the two
existing registry-vocabulary tags. No signature, parameter, storage, body,
instruction, byte, data, reference, or non-target metadata may change.
Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Candidate Git base: `ce06f52404704a124653a7af7b71ed1ad9baadf5`.
Candidate Ghidra PRE: db.18610, 19 project files / 186,747,781 bytes,
canonical inventory SHA-256
`8eb664062a8ba67005e9f8ad8f61aa2222585622c41022a69080c5e408cd3cf6`.

## Exact cohort and naming boundary

The sibling TSV is the complete 34-row mutation manifest. Every row joins
one-to-one by registry index, command, and entry address to both the promoted
boundary manifest and the static-contract table. Every PRE name is the exact
saved `FUN_*` default and every POST name is
`IScript__<shipped-registry-command>` with `USER_DEFINED` name source.

This convention records the command vocabulary by which the script registry
exposes the handler. It does **not** recover an original C++ symbol and does
not prove that the visible body implements the full ordinary-language meaning
of the command. In particular, 22 of the 34 registry labels are broader than
the locally visible mechanism. Their names remain Tier 2 script vocabulary,
not Tier 1 source identity.

The canonical projection
`index<TAB>handlerVa<TAB>expectedPreName<TAB>proposedName<LF>` is 1,684 bytes,
SHA-256
`cc769cb0b83aec0105d365e77f0702adcc1024914453b0f5615c8d7d1b333ce9`.
The immutable PRE-metadata TSV has 34 rows. It pins that every target begins
with no function comment, no repeatable comment, and no function tags; the
literal `<EMPTY>` sentinel makes the empty final tag field lossless.

The cohort excludes the already completed 75-row vocabulary normalization,
indices 114/115 whose Tier-1 error strings win over the registry label, index 2
`SetSpeed` on the shared no-op, the four unresolved HUD names, and the separate
`0x0050FF10` CExplosion repair.

## Exact comment and tag policy

Each function receives one comment with four explicitly separated layers:

1. the exact registry slot, record, command, Tier-2 promoted name, and warning
   that the name is not an original C++ symbol or ABI claim;
2. the row's verbatim `C1_CANDIDATE_PARTIAL` /
   `STATIC_HYPOTHESIS_ONLY` static envelope and its registry-label relation;
3. the row's bounded visible failure/no-op wording; and
4. the row's explicit remaining unknowns and cheapest falsifier.

Every comment ends by stating that no runtime reachability, causal behavior,
source equivalence, or reconstruction parity is admitted. The mutator loads
those row-specific fields from the separately reviewed static-contract TSV;
it does not infer or rewrite them.

Every row receives the already-existing `script-command-registry` and
`tier2-script-facing-name` tags. No new tag definition is created. The PRE
catalog has 6,854 definitions, definitions SHA-256
`074dd7480aebfe46aabe5a48c1429348a814c9b51b0d71d985cbdac6e764603f`,
and usage SHA-256
`0ac85baaf38153328266bf4c54178f44ad871f273dabba03dfd13aaf4ded1a97`.
The exact POST keeps the same definitions and changes only those two use counts
from 94/75 to 128/109, producing usage SHA-256
`0cbec4d3c190f2df8be5a3bd67ceeeaa419d3d5d9b20602b7ff9e400ade12971`.

## ABI and collateral preservation

The operation may change only each target's primary name/name source,
name-derived fully qualified name and rendered signature text, function
comment, and two tag associations. The signature text is allowed to differ
only because Ghidra renders the function name inside the otherwise unchanged
prototype.

For every target, the gate snapshots and compares signature source, calling
convention, return type/storage, parameter count plus every parameter's name,
datatype, ordinal, storage, and source, custom-storage/varargs/no-return flags,
stack purge, frame/local/parameter sizes, thunk/external/inline state, exact
body ranges and bytes, and instruction count. Repeatable comments remain
absent. All 8,136 non-target function rows must remain byte-identical.

Program memory, instruction layout, defined and undefined data, references,
relocations, non-function symbols, memory blocks, and the 8,170-function census
must remain exact. The only permitted program-inventory deltas are exactly 34
default function symbols becoming user-defined and exactly 34 new function
comments. The expected function-tag delta is exactly 68 associations and zero
definitions.

## Pinned evidence inputs

| Input | Bytes | SHA-256 |
| --- | ---: | --- |
| shipped registry TSV | 6,924 | `61a44b1a393251bfd32c28a037648968575bfbd55afc1cba8e39bd269a5e1fdd` |
| shipped registry report | 22,464 | `337ee300b0a55eaeb4c4a66669621a2a1937b72bd8ac2bb373508d3a005ab34a` |
| naming convention | 4,255 | `2ed51bc92a265043194426976df8138c009b64058581475de62f398e50ed4381` |
| current name projection | 502,854 | `515170759dda2686db408d25296362275f8913f7be42b6f0536b986c591786ee` |
| exact 34-boundary manifest | 7,264 | `e53fd6f4c44ab7f91779e0673e91ae3701514c486594cc733025334fe6289a42` |
| boundary live report | 4,433 | `6753b80ad39c3e535ebbb8985e69f2bcf9282092ac16d27429d32c2f2e53a248` |
| static-contract owner | 9,113 | `c8b599b7cce79beba453a39d78523b616bcf83f45403423872f533086ed761b7` |
| static-contract rows | 21,608 | `86c0c4a0e0d5fe0078cb21f271b4985cb1c4fe89aa035b66215076dfbe784a31` |
| completed 75-row live report | 6,675 | `0408c6e67171213cf4fbb510806137420f2194cca2d8a6c3790e7584c7507c32` |
| current full function inventory | 7,086,736 | `8eded18abddfc0726517f2a88c7f4b2df15ff0cd13d3b70a5ca7ebd5a7afea5b` |
| current program inventory | 1,267 | `a3c505c34b7ba26dec7088d9ee22e0f9c13365ae979be1ffc8f52301e1f368c1` |

Historical 75-row launchers and receipts remain frozen. They are templates and
evidence, not authority for this distinct cohort.

## Scratch authority and stop boundary

The target-specific scratch authority requires a verified baseline copy and
read-only restore probe, two independent fresh replicas, dry/apply/separate
loaded-state readback on both, byte-identical POST inventories, fail-after-one
rollback and post-inner compensation controls with exact PRE readback, and
repository-contained output preflight before any transaction. The resulting
receipt remains machine-local under
`local-lab/ghidra-mission-registry-new34-vocabulary-20260813-v1/`.

This owner authorizes no live Ghidra mutation, canonical snapshot refresh,
commit, or push. Any later live ceremony still requires a fresh verified
off-volume PRE backup, one writable process, separate readback, verified POST
backup/restore, exact live/tracked/POST equality, and refreshed projections and
current-state documents.
