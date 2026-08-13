# Mission-script registry vocabulary normalization

Status: scratch-gated candidate; no live mutation authorized by this owner
Last updated: 2026-08-13
Evidence: MEASURED — the shipped 144-slot MissionScript command registry, the
adjudicated naming convention, and the exact current 8,170-function Ghidra
projection; UNKNOWN — every behavior, signature, argument contract, failure
path, and original C++ identity not independently established elsewhere.
Verdict: exactly 75 existing function entries may receive Tier-2 script-facing
registry names, bounded caveat comments, and two evidence tags. The operation
does not create boundaries, does not touch `0x0050FF10`, and must preserve all
ABI, signature-source, storage, body, instruction, byte, data, reference, and
non-target metadata.
Specimen: pristine PC retail `BEA.exe`, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Candidate tracked base: `581bcabfc1d7bbe4f83e3a977079b505a2d9ae81`.

## Exact cohort

The immutable TSV beside this owner is the complete mutation manifest. It has
75 unique indices, 75 unique handler addresses, and 75 unique proposed names:

- `DEFAULT54`: 54 entries already present before the boundary campaign and
  still carrying their saved `FUN_*` labels;
- `MSG5`: five message handlers whose descriptive `PlaySound*` labels lose to
  the shipped registry vocabulary;
- `CLASS3_16`: sixteen other descriptive or mechanism-facing labels that lose
  to Tier-2 registry vocabulary.

The canonical projection
`index<TAB>handlerVa<TAB>expectedPreName<TAB>proposedName<LF>` is 4,035 bytes,
SHA-256
`39a9f2f01eb82c9f1924f716cb621dd9d9f680f7c584315e770f7731a0da9992`.
This is an independent integration-owner fingerprint; a generator or reviewer
must report any difference rather than silently normalizing it.

The companion immutable PRE-metadata TSV pins each target's exact comment,
repeatable-comment, and tag-set identity from the current full inventory. It is
75 rows / 22,628 bytes / SHA-256
`cc7cc62d64bcd62f6024f2b4ccc66c369426853c638ba90a773d537fd269470b`.
It exists so a separate readback can prove exact preservation for the 70
append-only rows and exact, recoverable replacement for the five `MSG5` rows.
The final `preTags` column uses the literal `<EMPTY>` for an empty tag set; both
authorities require and losslessly decode that sentinel. No data row ends in a
tab or other whitespace, so Git's staged diff gate covers the TSV cleanly.

The following are deliberately outside the cohort:

- the 34 boundaries created on 2026-08-13, which now carry separately reviewed
  `C1_CANDIDATE_PARTIAL` static envelopes but retain default metadata and
  require their own later naming cohort;
- registry indices 114 and 115, whose shipped Tier-1 error strings preserve
  `IScript__Create3PointPanCamera` and `IScript__Create4PointPanCamera` over the
  script commands `Goto3PointPanCamera` and `Goto4PointPanCamera`;
- index 2 `SetSpeed`, which is registered on the shared no-op and is not one of
  the reviewed 54/21 sets;
- all other already named registry handlers; and
- `0x0050FF10 CWorldPhysicsManager__CreateExplosion`, which is a separate
  corruption-repair ceremony.

## Exact metadata policy

For every manifest row the saved function name becomes
`IScript__<registry-command>` with `USER_DEFINED` name source. This is the
project's Tier-2 naming convention. The name records the script-facing command
for a registry slot; it is not a recovered original C++ symbol and supplies no
behavior or ABI evidence.

For the 70 `DEFAULT54` and `CLASS3_16` rows, the mutator appends one
blank-line-separated paragraph to the existing function comment, or installs
that paragraph when the PRE comment is absent. The common paragraph is:

> Mission registry vocabulary: slot `<index>` (record `<registryRecordVa>`)
> registers this handler as `<command>`. The promoted
> `IScript__<command>` name is Tier 2 script-facing vocabulary under the
> project naming convention, not a recovered C++ symbol and not evidence of
> this handler's signature, arguments, side effects, failure behavior, or
> complete semantics.

`DEFAULT54` adds:

> This function had only a default `FUN_*` label before this metadata
> promotion; no behavior claim is added.

`CLASS3_16` adds:

> The prior label `<expectedPreName>` was a Tier 3 mechanism-facing
> description. Its bounded body/callee observations remain in the pre-existing
> comment and tags where present; this vocabulary rename neither refutes those
> observations nor upgrades them into a behavior contract.

For the five `MSG5` rows, retaining the old comment would retain the very
callback/fade claims this adjudication refutes. Their function comments are
therefore replaced in full, not appended. Each replacement begins with the same
registry-vocabulary paragraph and then records only the measured row-specific
message, queue, and constructor-axis facts:

| Idx | Replacement fact boundary |
| ---: | --- |
| 17 `AddMessage` | Builds and queues a localized `CMessage`; queued advancement can reach voice playback. Constructor argument 1 is fixed global `0x0089C328`, argument 5 is a register in the optional-audio-reader slot, argument 6 is a register, and argument 7 is literal `0xA`. Argument 1 is the measured `AddMessage` distinction. |
| 28 `PlayCharMessage` | Builds and queues a localized `CMessage`; queued advancement can reach voice playback. Argument 5 is a register in the optional-audio-reader slot, argument 6 is literal `0`, and argument 7 is literal `0xA`. The measured body/call layer registers no callback. |
| 36 `PlayCharMessageWait` | Builds and queues a localized `CMessage`; queued advancement can reach voice playback. Argument 5 is a register in the optional-audio-reader slot, argument 6 is a register, and argument 7 is literal `0xA`; it also calls `CEventManager__GetNextFreeEvent` and `CScheduledEvent__Set`. Those facts establish the `Wait` scheduling axis, not fade. |
| 90 `PlayPCharMessage` | Builds and queues a localized `CMessage`; queued advancement can reach voice playback. Argument 5 is a register in the optional-audio-reader slot, argument 6 is literal `0`, and argument 7 is caller-varied. Argument 7 is the measured `P` axis; priority remains a plausible mechanism reading, not a recovered field meaning. |
| 91 `PlayPCharMessageWait` | Builds and queues a localized `CMessage`; queued advancement can reach voice playback. Arguments 5, 6, and 7 are registers; it also calls `CEventManager__GetNextFreeEvent` and `CScheduledEvent__Set`. Argument 6 plus scheduling establishes `Wait`, while argument 7 is the measured `P` axis; fade is refuted and priority remains plausible rather than proven. |

All five comments expressly leave complete behavior, unresolved constructor
slots and field meanings, failure paths, and original C++ identity open.

Every row adds `script-command-registry` when absent plus
`tier2-script-facing-name`. The 70 non-message rows retain their complete PRE
tag set. Among `MSG5`, index 28 removes the refuted `callback-message` tag;
indices 36 and 91 remove the refuted `fade-event` tag; indices 90 and 91 retain
`priority-message`; and indices 36 and 91 retain `scheduled-event-7d1`. All
other PRE tags survive. Repeatable comments are untouched. The
`script-command-registry` tag definition already exists. The one permitted
catalog-definition change is creation of the absent
`tier2-script-facing-name` definition with an empty definition comment; the
rollback controls must remove that definition again when restoring PRE.

## Preservation contract

The PRE is the 2026-08-13 synchronized 8,170-row tracked snapshot, not the
frozen 2026-08-12 projection. Its independently exported full inventory is
8,170 rows / 7,082,637 bytes / SHA-256
`8aa8b4468f463053d25084de86bec2a701ed1064c13f77fd47d16f9dda6cf259`.
Its program inventory is 1,267 bytes / SHA-256
`cb4c2194e30e074e443779d9b42587072568f104fc76f671d40757af7b106075`.

The only permitted row-field changes are:

- name, fully qualified name, their lengths and hashes, and name source;
- the rendered signature string, its length and hash, solely because Ghidra
  renders the function name inside the otherwise preserved prototype;
- function comment presence, length, and hash; and
- function tag count, hash, and names.

Every target must retain entry, body size/range/digest, instruction count,
signature source, parameter count, calling convention, return type, varargs,
thunk state/target, external/custom-storage/inline/no-return flags, frame/local/
parameter sizes, and repeatable comment. The mutator additionally snapshots
parameter names, datatypes, ordinals, and storage plus return storage so a name
change cannot silently rewrite the ABI beneath the coarser full inventory.

All 8,095 non-target full-inventory rows must remain byte-identical. Program
memory, instruction layout, defined/undefined data, references, relocations,
non-function symbols, memory blocks, and function count must remain exact. The
expected global metadata deltas are exactly 54 default function symbols
becoming user-defined, exactly 54 new function comments, 130 added and three
removed function-tag associations, and exactly one new empty function-tag
definition named `tier2-script-facing-name`; no other program-level count or tag
definition may move.

## Pinned inputs

| Input | Bytes | SHA-256 |
| --- | ---: | --- |
| `mission-script-command-registry-2026-08-12.tsv` | 6,924 | `61a44b1a393251bfd32c28a037648968575bfbd55afc1cba8e39bd269a5e1fdd` |
| registry report | 22,011 | `24592057078f6658889860527ee64a8f4a3fb9bcfff5f98171725c8400d98c46` |
| naming convention | 4,255 | `2ed51bc92a265043194426976df8138c009b64058581475de62f398e50ed4381` |
| current 2026-08-13 name projection | 502,664 | `19312b424e357ea8a95102927d6464c874c491bdfcb28de82b1175e352fbb5bf` |
| boundary live-promotion report | 4,433 | `6753b80ad39c3e535ebbb8985e69f2bcf9282092ac16d27429d32c2f2e53a248` |
| new-34 static-contract owner | 9,113 | `c8b599b7cce79beba453a39d78523b616bcf83f45403423872f533086ed761b7` |
| new-34 static-contract rows | 21,608 | `86c0c4a0e0d5fe0078cb21f271b4985cb1c4fe89aa035b66215076dfbe784a31` |

The dated 2026-08-12 name projection, old five-row `PROMOTION-READY.md`, old
launchers, and their receipts remain frozen historical evidence. They are not
inputs to this ceremony and must not be repinned or edited.

## Required gate

Before any live write, the target-specific authority must prove exact PRE
identity, two independent persistent scratch replicas, read-only dry runs,
apply plus separate-process readback on both replicas, fail-after-one and
fail-after-inner-commit rollback controls with exact PRE readback, name and
address collision/alias/thunk checks, full inventory collateral accounting,
and a sealed reproducible receipt. Live work then still needs a fresh verified
off-volume PRE backup, live dry/apply/separate readback, verified POST restore,
tracked snapshot refresh on exact equality, and a new current name projection.

This owner stops at scratch authority. It authorizes no live mutation, tracked
snapshot replacement, commit, or push.
