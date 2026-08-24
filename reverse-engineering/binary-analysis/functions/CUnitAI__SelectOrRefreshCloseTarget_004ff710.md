# CUnitAI__SelectOrRefreshCloseTarget_004ff710

> Address: `0x004ff710`

Status: active replicated bounded-runtime function note
Last updated: 2026-08-24
Source File: none — no current source-crosswalk row | Binary: pristine
`BEA.exe.original.backup`, 2,506,752 bytes, SHA-256
`74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
Summary: exact static body/ABI identity plus replicated Level-521 call-context
behavior for the close-target selector. The function ran 86 times on 50
receivers; 41 gap-free returns were all heap-shaped pointers, and every call was
nested in `CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0` on the same
receiver.
Evidence: MEASURED — exact pristine body authority from the canonical contract,
then independently reproduced call-context event/invocation rows from two
serialized read-only replays over the retained Level-521 take2 trace. The second
replay was preregistered with exact positive and dark controls, reached wrapper
READY, and reproduced all 1,169 shared cohort/control rows byte-for-byte.

## Static identity and ABI

- Canonical contract:
  [`../../contracts/unitai/CUnitAI__SelectOrRefreshCloseTarget_004ff710__004ff710.md`](../../contracts/unitai/CUnitAI__SelectOrRefreshCloseTarget_004ff710__004ff710.md).
- Body `[0x004ff710,0x004ffb57]`, 1,096 bytes; pristine-body SHA-256
  `e4f2106e542daa0af8b3f92409641169e35f6c7a573c73956693545756703d05`.
- ABI: `void * __thiscall (void * this)`. The static body has a bare `RET`;
  runtime carries the receiver in `ECX` and the return bits in `EAX`. The
  pointer is intentionally untyped; no concrete unit/reader class is inferred.
- Runtime caller site is uniquely `0x004ff702`, eight bytes before the recorded
  end of `CUnitAI__UpdateTargetSupportAndFireFlags_004ff4f0`.

## Replicated bounded-runtime contract

Scenario: retained `level521-native-20260802-0018-take2` combat trace,
full native replay window. Trace SHA-256
`F7A8F93F7E499C4C92E6CC8FF5C301BDBBF1A70C80B64185E7A71A9D3A59FD5C`;
runtime specimen SHA-256
`E1436EF7E0AD9CCBDDD43AAACA952F6E84D4B1A282835CEAD745EFCFC32FADF4`.

- Corrected replay target 0: 86 calls / 86 entries / 41 raw returns; 41
  validated gap-free return envelopes; every exact-count expectation passed.
- All 86 calls occur inside an open ff4f0 invocation with equal `ECX`; the
  measured stack-depth delta is exactly 52 bytes on all 86.
- Receiver containment is `|r(ff710)|=50`, `|r(ff4f0)|=76`, and
  `r(ff710) ⊆ r(ff4f0)` with intersection size 50.
- All 41 validated return values are outside the module image and above the
  small-integer band: seven non-null heap-shaped values. This establishes a
  raw pointer-shaped return domain in this trace, not pointed-to RTTI or
  ownership.
- The positive rival `CWarspite__SetReaderAndRefreshSupportSelection` ran
  73/73/73 times only from the two formation-builder sites; its receiver set is
  disjoint from ff710. The exact dark `CWaypoint__RandomizeOffsetVectors` body
  stayed 0/0/0. Both preregistered controls survived.
- After excluding metadata and target rows, which encode the corrected table,
  all event/invocation rows for targets 0..2 match run-a byte-for-byte; both
  normalized streams SHA-256 to
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
  plate. Promotion rests on the later preregistered corrected replay, not on a
  post-hoc reinterpretation of that first control.
- The take2 recorder receipt is RECONSTRUCTED/PARTIAL: the trace bytes are
  hash-bound after lock release, but capture-time target hash was not
  independently bound. All claims here inherit that provenance limit and are
  bounded to this copied-runtime trace.
- No state-write watchpoint was collected. Exact mutation ordering for
  `this+0xc`, `+0x18`, and `+0x1c`, pointed-to RTTI, other levels, and rebuild
  parity remain open.

## Cheapest falsifier

Replay the same exact corrected table and pinned v2 collector. Any non-READY
wrapper result; a count other than 86/86/41; an ff710 call outside an open
same-ECX ff4f0 frame; any caller other than `0x004ff702`; a validated EAX in the
small-integer/module-image bands; receiver-containment failure; a control
failure; or a shared-row hash other than `AD623E03…CDB0F` falsifies this bounded
contract.
