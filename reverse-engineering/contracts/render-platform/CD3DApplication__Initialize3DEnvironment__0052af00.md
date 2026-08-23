# CD3DApplication__Initialize3DEnvironment

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CD3DApplication__Initialize3DEnvironment` at `0x0052af00` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: `references/Onslaught/d3dapp.cpp` | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x0052af00`

## Identity
- Body `[0x0052af00,0x0052b753]`, 2132 bytes, 612 closure instructions. Raw pristine-body SHA-256 `bf98f3c6884486a9f4d40fed2a60d1b21641ea622fa85eb2aaeddc99a1a60379`; closure range SHA-256 `3fdf4c8ba9cba92a892c905aed37a3d2e05c052f5c1a98a80636c2f83f1ceb3c`; packet range-plus-bytes SHA-256 `55255e33ccbd04e0b11d2edf786b2196025b8b3027c5aea37886b51025288f2d`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CD3DApplication__Initialize3DEnvironment`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `e8bafd7ff0c65fe0497d30ddf30e5229775739a0101aa2dc817c04c43f8ca57c` and decompile SHA-256 `f221914063c36d362c93ac9e24217aa7bd12928d107a60a3fdc8b9b3e75f7840` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CD3DApplication__Initialize3DEnvironment(void * this, bool reuse_existing_device)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CD3DApplication__Initialize3DEnvironment(void * this, bool reuse_existing_device)
```
- Packet-declared parameter list: `void * this, bool reuse_existing_device`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment or source-first boundary below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented.

## Globals read/written
- Decompile symbol references: `DAT_00622d9c`, `DAT_006245d8`, `DAT_006291c4`, `DAT_0063e3dc`, `DAT_0064c08c`, `DAT_00662db8`, `DAT_00662f39`, `DAT_00662f3d`, `DAT_0066eb90`, `DAT_0089c04c`, `DAT_0089c05c`, `DAT_0089c07c`, `DAT_0089c08c`, `DAT_0089c09c`, `DAT_009cc0e8`, `DAT_009cc108`, `s_Available_texture_memory___d_Mb_0064c29c`, `s_Creating_device____0064c35c`, `s_D3DA__I3DE_OK_0064c214`, `s_Failed_for__s__0064c334`, `s_Failed_for_device_lost__0064c344`, `s_Falling_back_to_a_friendly_mode_0064c2c8`, `s_Falling_back_to_no_lockable_back_0064c30c`, `s_Falling_back_to_no_multisampling_0064c2e8`, `s_Going_to_safe_mode_0064c370`, `s_Succeeded__0064c2bc`, `s__hw_vp__0064c268`, `s__mixed_vp__0064c248`, `s__pure_hw_vp__0064c28c`, `s__simulated_hw_vp__0064c254`, `s__simulated_mixed_vp__0064c230`, `s__simulated_pure_hw_vp__0064c274`, `s__sw_vp__0064c224`, `s_c__cardid_txt_0064c390`, `s_cardid_txt_0064c384`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `FatalError_LocalizedStringId` `0x0042d080` x1 site(s) (STATIC_DIRECT).
- Callee `CConsole__Printf` `0x00441740` x11 site(s) (STATIC_DIRECT).
- Callee `CDXEngine__SetGlobalTintColorOpaque` `0x004d1710` x2 site(s) (STATIC_DIRECT).
- Callee `StringScratch_T3_004f7c70` `0x004f7c70` x2 site(s) (STATIC_DIRECT).
- Callee `CD3DApplication__LoadCardIdAndApplyVendorTweaks` `0x005286e0` x1 site(s) (STATIC_DIRECT).
- Callee `CTweakSLONG__SetValueRounded` `0x00528ad0` x2 site(s) (STATIC_DIRECT).
- Callee `CD3DApplication__Initialize3DEnvironment` `0x0052af00` x1 site(s) (STATIC_DIRECT).
- Callee `CD3DApplication__DisplayErrorMsg` `0x0052c4f0` x1 site(s) (STATIC_DIRECT).
- Callee `CD3DApplication__SetDeviceCursorFromIcon` `0x0052c8d0` x1 site(s) (STATIC_DIRECT).
- Callee `sprintf` `0x0055de9b` x1 site(s) (STATIC_DIRECT).
- Callee `HResultToString` `0x005be628` x1 site(s) (STATIC_DIRECT).
- Caller `CD3DApplication__Create` `0x005290a0` x1 site(s) (instruction-flow).
- Caller `CD3DApplication__Initialize3DEnvironment` `0x0052af00` x1 site(s) (instruction-flow).
- Caller `CD3DApplication__ForceWindowed` `0x0052ba50` x1 site(s) (instruction-flow).
- Caller `CD3DApplication__Reset3DEnvironment` `0x0052bb80` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first pin: `references/Onslaught/d3dapp.cpp` lines `857-1033` defines `CD3DApplication::Initialize3DEnvironment` as `HRESULT CD3DApplication::Initialize3DEnvironment()`; exact extracted source-body SHA-256 `9aa43a9d5982e143567e32cec5d07a3f1b62ac49b41d8ddbe37850e357a24997`; crosswalk class `SOURCE_ANALOG`.
- Source architecture/ownership/target branch: the unguarded Direct3D-8 framework body `CD3DApplication::Initialize3DEnvironment` in `references/Onslaught/d3dapp.cpp` is a PC-framework source analog, not proof that the retail Direct3D-9 body is source-identical.
- Source algorithm: choose the current adapter/device/mode; adjust the window; populate presentation parameters; create the device; on success record caps/device text/backbuffer, initialize and restore device objects, and activate; on failure invalidate/delete/release state and, for a HAL failure, select REF then retry recursively; return `S_OK` or the final HRESULT.
- Source state/side effects: writes `m_d3dpp`, `m_pd3dDevice`, `m_d3dCaps`, `m_dwCreateFlags`, `m_strDeviceStats`, `m_d3dsdBackBuffer`, `m_bActive`, adapter/device selection, and window state; it may resize/show the window, configure the cursor, emit debug text, display an error, and release a failed device. Retail agreement is limited to the pinned packet/body and tracked `SOURCE_ANALOG` row; API version, concrete layout, fallback details, and exact call order remain open deltas.
- Source-vs-retail delta boundary: packet/pristine identity below independently pins the retail target. Only agreements explicitly shared by the source summary and packet comment/decompile are carried; platform conditionals, layouts, constants, omitted/inlined calls, failures, and runtime causality remain open.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave572 signature/comment hardening: retail D3D environment create/reset path. RET 0x4 confirms one stack bool after this; the body applies cardid.txt/CVar tweaks, builds presentation parameters, applies screen-shape scaling, creates or resets the D3D device, falls back from lockable backbuffer/multisampling/friendly modes, updates device stats/backbuffer/cursor state, calls init/restore vfuncs, and can retry through the REF device. Static retail evidence only; exact presentation-parameter layout, runtime D3D behavior, exact source identity, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `f221914063c36d362c93ac9e24217aa7bd12928d107a60a3fdc8b9b3e75f7840`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 4 caller record(s), 11 callee record(s), and 19 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
No TTD execution row exists for this VA in the bounded `ttd-deep-mine/values.tsv` corpus. This absence is not a dormancy claim and supplies no runtime semantic proof.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 23; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `e8bafd7ff0c65fe0497d30ddf30e5229775739a0101aa2dc817c04c43f8ca57c`, and packet decompile SHA-256 `f221914063c36d362c93ac9e24217aa7bd12928d107a60a3fdc8b9b3e75f7840`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `0052af00:0052b753;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x0064c214` length 14 SHA-256 `e9d9ca36d96ab437f24419348191ba5cc0ae5768168fe25b7cab66d0cbf46d6e` value “D3DA::I3DE OK”.
- Packet string ref `0x0064c224` length 9 SHA-256 `f7b20d66e3565630066a1e07ad3dab2ca176f34b1250fde7957587c3f8cbb6f4` value “ (sw vp)”.
- Packet string ref `0x0064c230` length 22 SHA-256 `b48087173f2c96c69a240e8b91779bdea47ee5ebd6c1f47c9e73e1e8fe1eaca1` value “ (simulated mixed vp)”.
- Packet string ref `0x0064c248` length 12 SHA-256 `2e89f68bb2a7693b0256e52b98c9ea4c1f8cce43ec7d0c490c55e5c55eb41488` value “ (mixed vp)”.
- Packet string ref `0x0064c254` length 19 SHA-256 `470aef1989552bfacccfdc9e6817a50637fdf0095e6ad7d130465a79188597fa` value “ (simulated hw vp)”.
- Packet string ref `0x0064c268` length 9 SHA-256 `96981465f0cffc13ac2b2f0e552883355325bc198b411ad57fcaec79d3853b47` value “ (hw vp)”.
- Packet string ref `0x0064c274` length 24 SHA-256 `94ef1b3d604ba5f23b157476d799014a9254890cfca0d9d261fbecbecd9215a6` value “ (simulated pure hw vp)”.
- Packet string ref `0x0064c28c` length 14 SHA-256 `55a8875d52d4617d020ff14973ab51041cb6b9837b41ac4bda7023c7b31ab424` value “ (pure hw vp)”.
- Packet string ref `0x0064c29c` length 32 SHA-256 `cf733ee3df64327960f7a3c3b3e3547673481200a9ae1841e7589af7f7ca63ea` value “Available texture memory: %d Mb”.
- Packet string ref `0x0064c2bc` length 11 SHA-256 `a9adcbe788843272d41fe0f6cce4d98c4201a3b7d6112dbf138e285836f8ee90` value “Succeeded.”.
- Packet string ref `0x0064c2c8` length 32 SHA-256 `517211432a42745c07f7e31710b3d967e7cceefab14c76ca330d115b317ae3b3` value “Falling back to a friendly mode”.
- Packet string ref `0x0064c2e8` length 33 SHA-256 `7cb82a82ff15be9cd3f32c3457abcddf40923898e811ca52de3739c5d8e6c49f` value “Falling back to no multisampling”.
- Packet string ref `0x0064c30c` length 39 SHA-256 `1e9b5f6268b57a3ae4ff79324606c48c984684d4915e790c1867c4130a66b753` value “Falling back to no lockable backbuffer”.
- Packet string ref `0x0064c334` length 15 SHA-256 `d4c7ceb300e4bb6226f994a9261ba63328a5bf59d4c7a60b83ff82e8d9249c9c` value “Failed for %s.”.
- Packet string ref `0x0064c344` length 24 SHA-256 `2e45ba99cf58f956474ab6e1f534148e12cfc53aba0c108ec9b5f9b646af4145` value “Failed for device lost.”.
- Packet string ref `0x0064c35c` length 19 SHA-256 `561d38aa241853d220269cbec92e7cd33f51f536f915d1e1eea4c886cfbcbc78` value “Creating device...”.
- Packet string ref `0x0064c370` length 19 SHA-256 `37b35bea0f9e7b371723a94833469dffc2dd5b7aa5092ea2e5d088ad14f6d236` value “Going to safe mode”.
- Packet string ref `0x0064c384` length 11 SHA-256 `da83093984a5e3e141b88aa1700a9f5d92707d76abcd23795be1959689440360` value “cardid.txt”.
- Packet string ref `0x0064c390` length 14 SHA-256 `12bafed7f68d37da7880383db1673f4a047d1d058f2031b30ae24995958e9f51` value “c:\\cardid.txt”.
- Source crosswalk: `references/Onslaught/d3dapp.cpp` `CD3DApplication::Initialize3DEnvironment` line 857 (`SOURCE_ANALOG`), owner `canonical_crosswalk` under `reverse-engineering/source-crosswalk`, evidence `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`, `reverse-engineering/source-crosswalk/audit/remediation-wave1.tsv`. This is source architecture/name evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are reconciled. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
