# CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0

> Address: `0x004ff4f0`

Status: active replicated bounded-runtime function note
Last updated: 2026-08-24
Source File: none — no current source-crosswalk row | Binary: pristine
`BEA.exe.original.backup`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: exact static body/ABI identity plus replicated Level-521 call-context
behavior for the target-support/fire-flag updater. The function ran 169 times on
76 receivers and supplied the enclosing frame for all 86 observed close-target
selector calls.
Evidence: MEASURED — exact pristine body authority from the canonical contract,
then independently reproduced call-context event/invocation rows from two
serialized read-only replays over the retained Level-521 take2 trace. The second
replay was preregistered with exact positive and dark controls, reached wrapper
READY, and reproduced all 1,169 shared cohort/control rows byte-for-byte.

## Static identity and ABI

- Canonical contract:
  [`../../contracts/unitai/CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0__004ff4f0.md`](../../contracts/unitai/CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0__004ff4f0.md).
- Body `[0x004ff4f0,0x004ff70a]`, 539 bytes; pristine-body SHA-256
  `4bf6a880bceb0db303c5adab07deb05430df97d61a8bdbe34b99cb608958f60d`.
- ABI: `void __thiscall (void * this)`. Runtime carries the receiver in `ECX`;
  EAX at return is residual and has no scalar return meaning.
- Runtime caller census: 167 calls from `CUnitAI__Update` site `0x004fef4a`;
  two from `CDiveBomberAI__VFunc_9_00445900` at `0x004459c9` and
  `0x004459f5`.
- The previously missing hottest static edge is measured at runtime:
  ff4f0 calls `CUnitAI__SelectOrRefreshCloseTarget_004ff710` only at
  `0x004ff702`, 86 times.

## Replicated bounded-runtime contract

Scenario: retained `level521-native-20260802-0018-take2` combat trace,
full native replay window. Trace SHA-256
`F7A8F93F7E499C4C92E6CC8FF5C301BDBBF1A70C80B64185E7A71A9D3A59FD5C`;
runtime specimen SHA-256
`E1436EF7E0AD9CCBDDD43AAACA952F6E84D4B1A282835CEAD745EFCFC32FADF4`.

- Corrected replay target 1: 169 calls / 169 entries / 71 raw returns; 70
  validated gap-free return envelopes; every exact-count expectation passed.
  The one unlinked raw return is retained as an orphan boundary, not attached to
  a guessed invocation.
- Every one of the 86 nested ff710 calls has an open ff4f0 frame with the same
  `ECX`; stack-depth delta is exactly 52 bytes. No enclosing invocation contains
  more than one ff710 call.
- Receiver containment is `50⊆76`. This proves one shared runtime envelope in
  this trace; it does not prove all ff4f0 paths select/refresh a close target.
- The positive formation-builder rival ran 73/73/73 with exact caller/body
  boundaries and disjoint receivers. The exact dark CWaypoint body stayed
  0/0/0. Both preregistered controls survived.
- After excluding metadata and target rows, all event/invocation rows for
  targets 0..2 match run-a byte-for-byte; both normalized streams SHA-256 to
  `AD623E03146985419C58F13B3364C1C12457034EFD53B2912B74AA7DAC0CDB0F`.

## Receipts and limits

- Corrected capture SHA-256
  `84DB81290B00CE15FBCEB579FD8BC8B4C793C3F947001544FA44918F4189D171`;
  wrapper receipt
  `A3D9E421EB12526405DF718C9142CE5BBE0AB829CAE6C9D614242BCE0138A96D`;
  manifest
  `9C3757B2670A67035FB25A093A8E36CFA0AA18BD44517E904BA410C1DA45999F`.
- Independent adjudication output SHA-256
  `2C4B7987EC08FBBFCC063C793196BD66BBF5093480B7D54899883F36AD6FF6A7`;
  promotion manifest:
  [`../unitai-targeting-runtime-replication-promotion-manifest-2026-08-24.tsv`](../unitai-targeting-runtime-replication-promotion-manifest-2026-08-24.tsv).
- The original run-a control design failed and remains preserved as a RED
  plate. Promotion rests on the later preregistered corrected replay.
- The take2 recorder receipt is RECONSTRUCTED/PARTIAL: the trace bytes are
  hash-bound after lock release, but capture-time target hash was not
  independently bound. All claims are bounded to this copied-runtime trace.
- No state-write watchpoint was collected. The body contract's field/state
  vocabulary is static; exact `+0xc/+0x18/+0x1c` write ordering and other-level
  behavior remain open.

## Cheapest falsifier

Replay the same exact corrected table and pinned v2 collector. Any non-READY
wrapper result; a count other than 169/169/71; a caller outside the three measured
sites; an ff710 call outside the unique `0x004ff702` same-ECX nested path;
receiver-containment failure; a control failure; or a shared-row hash other than
`AD623E03…CDB0F` falsifies this bounded contract.
