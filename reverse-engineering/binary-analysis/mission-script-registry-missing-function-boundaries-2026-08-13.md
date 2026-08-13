# Mission-script registry missing function boundaries

Status: promoted boundary manifest; live and tracked Ghidra synchronized
Last updated: 2026-08-13
Verdict: the shipped MissionScript registry proves 34 callable retail entries
that were absent from the PRE 8,136-function Ghidra inventory. The full backed-
up promotion gate succeeded, so all 34 now exist with default metadata in the
current 8,170-function live and tracked snapshot.
Evidence: MEASURED — pristine registry pointers, already-defined retail
instructions, isolated natural Ghidra function recovery, pristine body bytes,
and exact whole-program before/after inventories; UNKNOWN — signatures,
arguments, returns, side effects, original C++ symbols, and runtime behaviour.
Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

## Result

The shipped MissionScript registry contains 144 command/handler pairs. At the
PRE checkpoint, 110 had exact entries in the 8,136-function Ghidra inventory;
the other 34 pointers were initialized executable `.text` instructions in
clean gaps, never interiors of PRE functions. The verified promotion created
those 34 boundaries only. Current Ghidra therefore resolves all 144 handlers
and contains 8,170 saved functions.

[`mission-script-registry-missing-function-boundaries-2026-08-13.tsv`](mission-script-registry-missing-function-boundaries-2026-08-13.tsv)
seals those 34 entries and the exact bodies Ghidra naturally recovers from the
already-defined instruction graph. It is 7,264 bytes, SHA-256
`e53fd6f4c44ab7f91779e0673e91ae3701514c486594cc733025334fe6289a42`.
Every row is a distinct, contiguous, non-thunk function body. Together they add
34 entries while retaining the existing 549,872 instructions.

The registry proves that each address is a command handler entry. It does not
prove an original C++ symbol. This boundary cohort deliberately creates only
default `FUN_<address>` functions. Script-facing `IScript__<command>` names,
comments, signatures, parameters, returns, and tags belong to a later naming
cohort after the boundary result has been reopened and read back.

## Range convention

`reachableBodyRanges` is canonical and **half-open**: every component is
`[start,endExclusive)`. Ghidra's `AddressSet` is inclusive, so the mutator must
use `endExclusive - 1`. `bodyBytes` is the sum of
`endExclusive - start` across all components. For example, `SetVisible` owns
`0x00535ea0-0x00535ecd`, exactly 45 bytes, and its inclusive Ghidra maximum is
`0x00535ecc`. Treating the endpoint as inclusive would steal one byte and is a
hard failure.

`bodyRangeSha256` uses the existing full-inventory convention: for each range,
hash lowercase, prefix-free `start:maxInclusive;` bytes in address order.
`bodyBytesSha256` hashes the specimen bytes in increasing address order.

## Reproduction and independent checks

- Registry identities come from
  [`mission-script-command-registry-2026-08-12.tsv`](mission-script-command-registry-2026-08-12.tsv),
  reconstructed from the record array at `0x0064ce20`, stride `0x40`, handler
  pointer at `+0x30`.
- The exact PRE inventory is 8,136 functions and 549,872 defined instructions.
  Comparing every candidate against every PRE function range found zero body
  intersections.
- A disposable copy of the tracked Ghidra snapshot created all 34 functions in
  one transaction with `CreateFunctionsFromAddressList.java`. A separate
  read-only reopen reproduced 8,170 functions, the same 549,872 instructions,
  and the manifest's exact bodies and default metadata.
- The pristine bytes independently reproduce every body-byte digest. Exact
  instruction coverage reproduces every instruction count; no range begins or
  ends inside an instruction.
- Full program inventories before and after the disposable apply differ only in
  the function census (`8,136` to `8,170`). Memory, instruction layout, defined
  and undefined data, non-function symbols, references, comments, relocations,
  and all pre-existing function rows remain unchanged.

The disposable discovery evidence is machine-local under
`local-lab/ghidra-mission-registry-boundary-campaign-20260813-v1/`. It is not a
live promotion receipt and does not authorize using that mutated discovery copy
as a scratch authority.

The formal ceremony wrote only under
`local-lab/ghidra-mission-registry-boundary-live-promotion-20260813-v1/`.
Its exact PRE inventory is
`local-lab/ghidra-collision-component-identity-live-promotion-20260812-v1/runs/live-readback/functions.tsv`
(7,060,261 bytes, SHA-256 `8261d681…`) and adjacent `program.tsv` (1,267
bytes, SHA-256 `cfecff14…`). The registry owner is 6,924 bytes, SHA-256
`61a44b1a…`; `ExportFullFunctionInventory.java` is 23,963 bytes, SHA-256
`04519cd8…`. The authority wrapper pins the complete hashes and refuses drift.

## Promotion gate that passed

The target-specific mutator is
`tools/GhidraApplyMissionRegistryBoundaries.java`; the receipt owner is
`tools/ghidra_mission_registry_boundary_authority.py`. Before a live write, the
owner must prove all of the following:

1. exact pristine program and manifest identity;
2. a recoverable off-volume PRE backup and read-only restore/open probe;
3. two independent persistent scratch replicas copied from that exact PRE;
4. dry, apply, and separate-process readback on both replicas;
5. forced rollback after one created function and compensating PRE restoration
   after the full inner mutation, each followed by an exact PRE readback;
6. the exact `+34` function census, exact 34 default-name rows, unchanged 8,136
   pre-existing rows, and unchanged program metrics other than `functions`;
7. target-symbol collision checks and unchanged non-target symbol state;
8. unchanged bytes, instruction layout, data, references, comments, and
   relocations;
9. one live apply process only, followed by separate readback, recoverable POST
   backup, and byte equality among live, POST backup, and tracked snapshot.

Every headless ceremony command must use `-noanalysis`. These ranges are
already fully disassembled; allowing analysis to run can create unrelated data
or instructions after an intentional probe failure. The exact program and
full-inventory comparisons reject that drift, but preventing it keeps each
scratch result attributable to the boundary mutator alone.

No stale historical launcher, frozen generation input, or dated name projection
is repinned by this campaign.

The sealed live receipt is
`local-lab/ghidra-mission-registry-boundary-live-promotion-20260813-v1/live-promotion.ready.json`,
9,956 bytes, SHA-256
`363a57afda96560b214c01e3a75422702ae6ac2cdeb89ed2d069231414722322`.
It proves the exact 8,136 → 8,170 census, zero pre-existing-row or program-
listing collateral, restore-tested PRE/POST backups, and byte equality among
live Ghidra, the POST backup, and the tracked snapshot.

## Open

- Exact signatures and complete semantics remain open. A later reviewed
  [static-contract addendum](mission-script-registry-new-function-static-contracts-2026-08-13.md)
  supplies bounded C1 envelopes and falsifiers without changing Ghidra metadata.
- The later Tier-2 script-facing naming cohort.
- Runtime reachability and reconstruction parity.
