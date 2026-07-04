# Ghidra PC Platform/Resource Tail Wave852 Readiness Note

Status: complete static read-back evidence
Date: 2026-05-25
Scope: `pc-platform-resource-tail-wave852`

Wave852 PC platform/resource tail saved comments and tags for seven important PC platform and render-resource connector rows from `0x00515ab0 D3DDevice__SetViewport` through `0x005164b0 CResourceDescriptorTable__InstantiateChain`. The pass made no renames, no signature changes, no function-boundary changes, and no executable-byte changes.

Representative anchors:

| Address | Saved state | Evidence |
| --- | --- | --- |
| `0x00515ab0 D3DDevice__SetViewport` | `void __stdcall D3DDevice__SetViewport(void * viewport)` | Called by `CDXEngine__PreRender`, `CDXEngine__Render`, `CDXEngine__PostRender`, `CEngine__SelectViewpoint`, and `CHud__RenderTargetIndicatorOverlay`; builds a D3DVIEWPORT-style stack record and calls global device `DAT_00888a50` vtable slot `0xbc`. |
| `0x00515b10 PCPlatform__DeserializeFontsAndAssets` | `void __thiscall PCPlatform__DeserializeFontsAndAssets(void * this, int chunk_reader)` | Called by `CResourceAccumulator__ReadResourceFile`; frees existing font slots, warns `Warning : deserializing font twice!`, allocates four `0x1180` CDXBitmapFont-like objects, deserializes from the chunk reader, and sets the main-font swap flag. |
| `0x00515db0 Registry__SetStringValue_HKCU` | `void __stdcall Registry__SetStringValue_HKCU(char * value_name, uchar * value_text)` | Called by `CConsole__Init` and `CConsole__AddString`; writes `REG_SZ` strings under `HKEY_CURRENT_USER\Software\Lost Toys\Battle Engine Aquila`. |
| `0x00515f60 CResourceDescriptorTable__ctor` | `void * __fastcall CResourceDescriptorTable__ctor(void * this)` | DATA xref `0x00515f35`; vector-constructs one `0x41c`-byte descriptor-like entry and sets `this+0x424` to `1`. |
| `0x00515fb0 CResourceDescriptorTable__InitDefaultMeshNames` | `void CResourceDescriptorTable__InitDefaultMeshNames(void)` | Called by `CLTShell__InitializeRuntimeAndLoadCoreResources`; initializes a global `0x428`-byte-stride descriptor table with default mesh/resource names including `default.msh`, `cannon1.msh`, `radar1.msh`, `plane1.msh`, `tree2.msh`, `tank1.msh`, `Enemymech.msh`, `bloke.msh`, `EnemyT~1.msh`, `shell.msh`, `cockpit2.msh`, and `carrier.msh`, then sets `DAT_00896488` to `0x17`. |
| `0x00516450 CResourceDescriptorTable__FreeAllEntries` | `void CResourceDescriptorTable__FreeAllEntries(void)` | Called by `CLTShell__ShutdownRuntimeAndReleaseResources`; walks descriptor records from `DAT_0088a510` toward `0x00896868`, frees per-descriptor pointer arrays through `CDXMemoryManager__Free`, and nulls entries. |
| `0x005164b0 CResourceDescriptorTable__InstantiateChain` | `void * __cdecl CResourceDescriptorTable__InstantiateChain(void * descriptor_table, int owner_tag)` | Called by `CThing__InitRenderThing`; scans descriptor records, calls `PCRTID__CreateObject`, stores `owner_tag` into the descriptor payload, invokes created-object init vfunc slot `+4`, and links created objects into a local chain. |

Read-back evidence:

- `ApplyPcPlatformResourceTailWave852.java dry`: `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 missing=0 bad=0`
- `ApplyPcPlatformResourceTailWave852.java apply`: `updated=7 skipped=0 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=7 missing=0 bad=0`
- `ApplyPcPlatformResourceTailWave852.java final dry`: `updated=0 skipped=7 renamed=0 would_rename=0 signature_updated=0 comment_only_updated=0 missing=0 bad=0`
- Post exports: `7` metadata rows, `7` tag rows, `14` xref rows, `2107` instruction rows, and `7` decompile rows.
- Additional read-only evidence: `9` context metadata rows, `9` context decompile rows, `15` string dumps, and source-context search hits.
- Queue after Wave852: `6098` total functions, `5736` commented, `362` commentless, `0` exact-undefined signatures, `0` `param_N`, comment-backed proxy `5736/6098 = 94.06%`, strict clean-signature proxy `5736/6098 = 94.06%`.
- Next raw commentless row: `0x005168d0 CPCSoundManager__dtor`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260525-093157_post_wave852_pc_platform_resource_tail_verified`, `19` files, `172034951` bytes, `DiffCount=0`.

What this proves:

- The seven target rows exist in the saved Ghidra project with the Wave852 comments/tags and current signatures above.
- The rows are important static connector infrastructure for D3D viewport handoff, PC font/resource deserialization, HKCU registry persistence, and render-resource descriptor table construction, defaulting, teardown, and instantiation.

What remains unproven:

- Runtime D3D viewport behavior, runtime font/resource loading, runtime registry side effects, runtime render-object/resource behavior, and runtime shutdown behavior.
- Exact viewport/font/resource/descriptor field schemas, full asset taxonomy, returned chain/list-head semantics, and exact source-body parity.
- BEA patching behavior.
- Rebuild parity.
