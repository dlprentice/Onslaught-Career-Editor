# CD3DApplication__BuildDeviceList

Status: active static contract (factory draft)
Last updated: 2026-08-23
Summary: specimen-bound static contract for `CD3DApplication__BuildDeviceList` at `0x00529350` in the render/effects/platform-support cohort; bounded behavior, evidence limits, and no-promotion disposition are explicit.
Evidence: MEASURED — current name/register identity, READY packet/decompile, structured edges, closure range, and independently recomputed pristine body bytes; source and runtime limits remain explicit.
Specimen: pristine `BEA.exe.original.backup`, 2,506,752 bytes, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`.
Source File: `references/Onslaught/d3dapp.cpp` | Binary: BEA.exe, SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`

> Address: `0x00529350`

## Identity
- Body `[0x00529350,0x0052a6f1]`, 5026 bytes, 1475 closure instructions. Raw pristine-body SHA-256 `a8374027bde940888504ac4b3a1a1a701baacc01629cbbce08ab83d560d3a8dc`; closure range SHA-256 `feff08e7e119bc86e22604017a04ef9959dd8245eb21d5cce23480385ca871e1`; packet range-plus-bytes SHA-256 `1b744528cae100f4e04b5cf9f48edb50d56bbce3c599170ce2f53081def00fe9`. All three were independently recomputed over the exact single contiguous inclusive range.
- Current 8,329-row name table and current EVIDENCE-REGISTER both name `CD3DApplication__BuildDeviceList`. The READY packet agrees. The dated closure spelling also matches the current identity.
- Packet name/signature provenance is counted metadata, not semantic proof. Packet file SHA-256 `a70d33df70f55531ec34fb074027162b15a874d6214a67e77f1ed56fb412ed84` and decompile SHA-256 `cc821235cf987b8f4471c539bac3fc2cf73372dd8ca6366a3714ab01574073e6` bind the retained review input without citing a writer-local scratch path.
- Campaign grade `C1_CANDIDATE_PARTIAL` / register grade `C1_CANDIDATE_PARTIAL` / register contract state `OPEN_EXECUTED` / closure class `SEALED_STATIC_RECEIPT` / packet confidence `MEDIUM_STATIC`. Proposed promotion: false.

## Calling convention
Packet records `__thiscall` for `int __thiscall CD3DApplication__BuildDeviceList(void * this)`. Register/stack placement beyond that packet declaration is not_determinable without a separate instruction-level ABI review.

## Prototype and parameter semantics
```c
int __thiscall CD3DApplication__BuildDeviceList(void * this)
```
- Packet-declared parameter list: `void * this`. Parameter labels are analyst/source intent; concrete object layouts, units, ownership, aliasing, and nullability remain not_determinable unless directly stated by the quoted packet comment or source-first boundary below.

## Return value meaning
The packet signature declares `int`. Exact domain meaning of the returned bits/value is not_determinable from identity and decompile evidence alone; no stronger meaning is invented.

## Globals read/written
- Decompile symbol references: `DAT_006245d8`, `DAT_0063e3dc`, `DAT_00662b2c`, `DAT_00662df0`, `DAT_0066eb90`, `DAT_0089c0ac`, `s_Adapter__d_0064c1c0`, `s_Available_modes__0064c0a0`, `s_But_no_depth_stencil_available__0064bfec`, `s_Can_do_multisample_2_0064bf68`, `s_Can_do_multisample_3_0064bf50`, `s_Can_do_multisample_4_0064bf38`, `s_Can_do_multisample_6_0064bf20`, `s_Can_do_multisample_8_0064bf08`, `s_Can_do_texture_A8R8G8B8_0064bfd4`, `s_Can_do_texture_D16_0064bf80`, `s_Can_do_texture_D24X8_0064bf94`, `s_Can_do_texture_DXT1_0064bfc0`, `s_Can_do_texture_DXT2_0064bfac`, `s_CheckDeviceType_failed_for_a___d_0064c050`, `s_D3D_`, `s_Desc____s_0064c1a8`, `s_Driver____s_0064c1b4`, `s_IDs___V___x__D___x__SS___x__R____0064c16c`, `s_Using__s_on__s__0064bee8`, `s_Version___08x_08x_0064c194`, `s_WHQL____d_0064c160`, `s___dx_d___d___s___0064c0b4`, `s__s__HWTNL_OK_0064c02c`, `s__s__HWTNL___PURE_OK_0064c03c`, `s__s__MIXED_TNL_OK_0064c018`, `s__s__SWVP_OK_0064c00c`, `s__s_accepted__0064bef8`, `s__s_caps__0064c094`. Read/write direction for each symbol is not independently instruction-verified by this factory.

## Callees relied on / callers
- Callee `CConsole__Printf` `0x00441740` x32 site(s) (STATIC_DIRECT).
- Callee `StringScratch_T3_004f7c70` `0x004f7c70` x2 site(s) (STATIC_DIRECT).
- Callee `CD3DApplication__FindDepthStencilFormat` `0x0052a830` x1 site(s) (STATIC_DIRECT).
- Callee `CD3DApplication__DisplayErrorMsg` `0x0052c4f0` x1 site(s) (STATIC_DIRECT).
- Callee `sprintf` `0x0055de9b` x1 site(s) (STATIC_DIRECT).
- Callee `Sort__QuickSortGeneric` `0x0055e7ae` x1 site(s) (STATIC_DIRECT).
- Callee `HResultToString` `0x005be628` x1 site(s) (STATIC_DIRECT).
- Caller `CD3DApplication__Create` `0x005290a0` x1 site(s) (instruction-flow).
- Structured packet arrays prove the listed direct/static edge identities and site counts only. Indirect vtable targets, library inlining, and data-driven dispatch remain unresolved unless separately named in the packet.

## Behavior summary
- Source-first pin: `references/Onslaught/d3dapp.cpp` lines `210-496` defines `CD3DApplication::BuildDeviceList` as `HRESULT CD3DApplication::BuildDeviceList()`; exact extracted source-body SHA-256 `62bc8659b85e8b46669deca8225a3fe069075a80a55cf0f80440552da0070eeb`; crosswalk class `SOURCE_ANALOG`.
- Source architecture/ownership/target branch: the unguarded Direct3D-8 framework body `CD3DApplication::BuildDeviceList` in `references/Onslaught/d3dapp.cpp` is a PC-framework source analog, not proof that the retail Direct3D-9 body is source-identical.
- Source algorithm: enumerate adapters; collect desktop and >=640x400 modes; deduplicate width/height/format and sort them; test HAL then REF device types, hardware/mixed/software vertex-processing modes, and optional depth/stencil formats; retain only compatible modes/devices/adapters; choose a windowable default device; return `S_OK`, `D3DAPPERR_NOCOMPATIBLEDEVICES`, or `D3DAPPERR_NOWINDOWABLEDEVICES`.
- Source state/side effects: fills `m_Adapters`, per-adapter device/mode arrays and compatibility flags; updates `m_dwNumAdapters`, `m_dwAdapter`, and `m_bWindowed`; may call `DisplayErrorMsg` when selecting REF. Retail agreement is limited to the separately pinned packet/body and the tracked `SOURCE_ANALOG` row; D3D8/D3D9 API, layout, limits, flags, and exact ordering remain possible divergences.
- Source-vs-retail delta boundary: packet/pristine identity below independently pins the retail target. Only agreements explicitly shared by the source summary and packet comment/decompile are carried; platform conditionals, layouts, constants, omitted/inlined calls, failures, and runtime causality remain open.
- Retail packet analyst comment (quoted as bounded packet evidence, never promoted by this file): “Wave572 signature/comment hardening: retail D3D adapter/device/mode enumeration path. ECX is this; it queries adapter count and display modes, filters small/non-allowed modes, honors DAT_0089c0ac widescreen allowance, probes HAL/REF format behavior, depth-stencil, texture, and multisample support, records default/friendly mode indexes, warns through DisplayErrorMsg, and returns D3DAPP-style HRESULT values. Static retail evidence only; exact structure layout, exact mode-list contract, runtime hardware behavior, exact source identity, and rebuild parity remain unproven.”
- The non-empty packet decompile is bound by SHA-256 `cc821235cf987b8f4471c539bac3fc2cf73372dd8ca6366a3714ab01574073e6`. This contract retains only its displayed control/side-effect envelope and does not infer unstated field meanings, units, ordering guarantees, or runtime causality.
- Structured inventory: 1 caller record(s), 7 callee record(s), and 38 string-ref record(s).

## Error / edge behavior
Nullability, invalid-state behavior, allocation/device failure, indirect-call failure, overflow/NaN behavior, and rollback semantics are not_determinable as a class from packet metadata. The decompile, quoted comment, and any source-first algorithm above are bounded evidence; missing branch-level behavior remains open rather than receiving an invented default.

## Runtime corroboration (TTD, bounded)
The bounded TTD table contains these exact rows; they establish only execution/coverage in the named captures unless a row states a stronger measured fact:
- Session `all level-openings`; question `corpus-open-core`; value: invariant across all 66 openings; 221,100 cumulative covered bytes; evidence `name=CD3DApplication__BuildDeviceList`.

## Evidence
- Writer authority: task `t_5b694f87`, immutable cohort-9 manifest SHA-256 `ebf607a5672b6d0dd95cf0ecf31d8fa9c2053b4ebe50fd2fe2f39bb8ceda9be8`, row 11; specimen `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, exact current identity, and proposed promotion false. The task comment and independent review receipt are the durable manifest route; no writer-local scratch path is cited here.
- Current identity joins: `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/EVIDENCE-REGISTER.tsv`, and `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`. The current name table/register pair wins over any dated closure spelling.
- READY packet schema `bea.re.triage-packet.v1`, image `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`, packet-file SHA-256 `a70d33df70f55531ec34fb074027162b15a874d6214a67e77f1ed56fb412ed84`, and packet decompile SHA-256 `cc821235cf987b8f4471c539bac3fc2cf73372dd8ca6366a3714ab01574073e6`; retained locally for cold review without a tracked local-path citation.
- Digest derivation: closure SHA-256 hashes canonical range text `00529350:0052a6f1;`; packet SHA-256 hashes that range text followed by exact pristine bytes; raw SHA-256 hashes only those bytes.
- Closure execution state `PARTIAL` and confidence `MEDIUM_STATIC`; these are inherited bounded grades, not this factory's promotion decision.
- Packet string ref `0x0064bee8` length 16 SHA-256 `3b6064aa564ee45e32a905da065397b73902f3232b24973f4f2c0e3f75ee3b99` value “Using %s on %s.”.
- Packet string ref `0x0064bef8` length 13 SHA-256 `67da447dc97d750239a5414e9be0c4be9c0fc8650c7d72ec8c0504a0dd7375bf` value “%s accepted.”.
- Packet string ref `0x0064bf08` length 21 SHA-256 `8b3f8407dea65da78524c4c241665f7b1493e78f823f353003a0d00077323934` value “Can do multisample 8”.
- Packet string ref `0x0064bf20` length 21 SHA-256 `1be06c692d5cbd861c1e0585dff7ddcfb97456c5de1070532579863d498cdfcf` value “Can do multisample 6”.
- Packet string ref `0x0064bf38` length 21 SHA-256 `198169d7776e91e8b70c570fd7d4a8aa803ac2f5ec7557faf3d8fadaa3e4febd` value “Can do multisample 4”.
- Packet string ref `0x0064bf50` length 21 SHA-256 `828ff8d7392ee528ade09b4bc7c94df478fbbc20e6d0f5121563237dc95a2a8d` value “Can do multisample 3”.
- Packet string ref `0x0064bf68` length 21 SHA-256 `99ed62f39a835fe6bb5b25d3c98a97fae1367c5ba07489456823f3c2e3bf05ed` value “Can do multisample 2”.
- Packet string ref `0x0064bf80` length 19 SHA-256 `f8ef5a68dc72643807a2bf56cbc1a1dfd131e9109058cb7530f3c52223f35429` value “Can do texture D16”.
- Packet string ref `0x0064bf94` length 21 SHA-256 `723f4163a7307123c6bd16795988ee37b84217b274897a4396610d415934719e` value “Can do texture D24X8”.
- Packet string ref `0x0064bfac` length 20 SHA-256 `894f1469461fefa5db255dc8e4fe53b979209e47ffdb854a90857e63c9d72827` value “Can do texture DXT2”.
- Packet string ref `0x0064bfc0` length 20 SHA-256 `5369186691b95b5025d5e7476463ac7c6256ccabe6a55045bfea13796058c508` value “Can do texture DXT1”.
- Packet string ref `0x0064bfd4` length 24 SHA-256 `648b298f2367068142456770c3209d7248e52c6e5ed0fead1c76fc1847ecdb4c` value “Can do texture A8R8G8B8”.
- Packet string ref `0x0064bfec` length 32 SHA-256 `63c1a3c336091e33547277c8467eb2ba499507cd62aae45728004e7ceaba35f8` value “But no depth/stencil available.”.
- Packet string ref `0x0064c00c` length 12 SHA-256 `72d37083afba8528a218d9eb1cb72c3719cb654e873980075344c75fddc0c307` value “%s: SWVP OK”.
- Packet string ref `0x0064c018` length 17 SHA-256 `c63ce13d463963d8b3544648c3f06878e18645b0a1f4c7a67572325a415aaf93` value “%s: MIXED TNL OK”.
- Packet string ref `0x0064c02c` length 13 SHA-256 `6f6def888f553cf131c69d3bed55c250db39dd8bffbbc5e0db7d8b66834e1fd6` value “%s: HWTNL OK”.
- Packet string ref `0x0064c03c` length 20 SHA-256 `0f9b62819d207293c117a62fa2273160c523eb6f39275f98879135ea1486786e` value “%s: HWTNL + PURE OK”.
- Packet string ref `0x0064c050` length 58 SHA-256 `82fa242680717a6308990d46b22c0453362e9a7770a4bd38e2c55010f84103a3` value “CheckDeviceType failed for a: %d, t: %s, f: %s because %s”.
- Packet string ref `0x0064c094` length 9 SHA-256 `c817e2a9e645df5103c615d4d63d536a11c6db509e8a88876be7e227ee002383` value “%s caps:”.
- Packet string ref `0x0064c0a0` length 17 SHA-256 `34e9fce32e1a3eee49123e58ace6d9a57b857b9d50c3ee07d2462d9ace214337` value “Available modes:”.
- Packet string ref `0x0064c0b4` length 17 SHA-256 `8c6d7393eef4b4e8a23503ebfc1ae7c4966e5aecd56b1cd5369eaed5d09ab0e2` value “{%dx%d: %d (%s)}”.
- Packet string ref `0x0064c0c8` length 12 SHA-256 `80ba3fc53fa807e21ecba9e9656137bf162898607ceab1a50bd4cbd05b2666a0` value “D3DFMT_DXT4”.
- Packet string ref `0x0064c0d4` length 17 SHA-256 `a302781e86b2878050d07d32f8130eb5ea62f20e57f0122253e98657bc39e8a1` value “<unknown format>”.
- Packet string ref `0x0064c0e8` length 12 SHA-256 `38124606be6d70103f50c8d68ae302e5254d0973e90893b03089417977f99fb1` value “D3DFMT_DXT2”.
- Packet string ref `0x0064c0f4` length 16 SHA-256 `1a31ae51f9791234856a9e88a650564b60c31bc3a0f44e462bdb1950f6de1e74` value “D3DFMT_A4R4G4B4”.
- Packet string ref `0x0064c104` length 12 SHA-256 `a2470b2335c44e21bbbed7269a782e42aced33833899538248b47529c7c51b6e` value “D3DFMT_DXT1”.
- Packet string ref `0x0064c110` length 16 SHA-256 `2b85486de8cbb0ee2df982246d4f0541f567c81906f31f51e5372b6213186481` value “D3DFMT_A1R5G5B5”.
- Packet string ref `0x0064c120` length 14 SHA-256 `2da69f9ef7daefe9dfae31bdfa555723d18c7da389018b390d6c16e792b37685` value “D3DFMT_R5G6B5”.
- Packet string ref `0x0064c130` length 16 SHA-256 `e207f772d8a1255cccc64e704f2ab11c3739b05f8800558e5131ef84f7f40627` value “D3DFMT_A8R8G8B8”.
- Packet string ref `0x0064c140` length 16 SHA-256 `fba20b871b65c865abebc87fe9458df54e56a1830ba650b8f29b64b6a6ca5950` value “D3DFMT_X8R8G8B8”.
- Packet string ref `0x0064c150` length 15 SHA-256 `9867379fb365b96221deec2afe4d1510c424c363151fa90294213ae861cabe1f` value “D3DFMT_UNKNOWN”.
- Packet string ref `0x0064c160` length 12 SHA-256 `2b2e4dc26c7d51e6cbd5b9deedcef598c89d04b922590a5b2a1a83e75fb5b3c7` value “WHQL   : %d”.
- Packet string ref `0x0064c16c` length 37 SHA-256 `c90efe5d4d6f28aaf689cace8243d3ee7edc48fcb4dd3b80b25b455bd763f5bd` value “IDs    : V: %x, D: %x, SS: %x, R: %x”.
- Packet string ref `0x0064c194` length 18 SHA-256 `40318ef5bea68af3549a0486c723e504f4fdc2397da783f67f8089eacaf9b7ee` value “Version: %08x%08x”.
- Packet string ref `0x0064c1a8` length 12 SHA-256 `aeb8b0c40e5eb092894923ddd816a949048cf6aade255433563f00531c1c0e7e` value “Desc   : %s”.
- Packet string ref `0x0064c1b4` length 12 SHA-256 `6537de0869b82807501910663e285c24277c2e93a37d6eef6665411e58efc3fb` value “Driver : %s”.
- Packet string ref `0x0064c1c0` length 11 SHA-256 `6c51cb1b83803748ca5c41356f065b49783d1fdee8f85263291a432b32d3a9dc` value “Adapter %d”.
- Packet string ref `0x0064c1cc` length 28 SHA-256 `44cefa9f04653eef2c047700a4a8499b47771732f04b674dd7f443398f48ee74` value “D3D->GetAdapterCount(): %d\n”.
- Source crosswalk: `references/Onslaught/d3dapp.cpp` `CD3DApplication::BuildDeviceList` line 210 (`SOURCE_ANALOG`), owner `canonical_crosswalk` under `reverse-engineering/source-crosswalk`, evidence `reverse-engineering/binary-analysis/ghidra-function-name-table-2026-08-17.tsv`, `reverse-engineering/binary-analysis/function-c1-closure-2026-08-11.tsv`, `reverse-engineering/source-crosswalk/audit/remediation-wave1.tsv`. This is source architecture/name evidence at the stated class, not independent retail behavior proof.

## Confidence
1 — exact current identity, contiguous pristine bytes, digest derivations, signature text, structured edge inventory, comments, strings, source joins, and TTD presence/absence are reconciled. Field-level semantics and runtime causality remain bounded. Proposed promotion: false.

## Unresolved questions
- Instruction-level read/write direction and concrete layout for every referenced field/global.
- Complete indirect-call target set and failure/nullability behavior.
- Runtime ordering, side effects, return-domain meaning, and caller expectations beyond the bounded packet/source/TTD evidence.
- Cheapest falsifier: cold-disassemble this exact raw-body digest, compare every branch/load/store/call against the packet decompile and structured arrays, then run a controlled copied-runtime probe for the named input/state transition.
