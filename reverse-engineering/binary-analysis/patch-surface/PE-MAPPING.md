# Patch-surface PE mapping (pristine specimen)

Status: active — BSS versus file-backed VAs for this image
Last updated: 2026-08-22
Summary: `file offset = VA − 0x400000` is only valid inside a section's
raw range. `.data` VirtualSize is far larger than SizeOfRawData, so most
runtime globals (including `g_bGodModeEnabled`, the mapping table, and
the script objective / goodie arrays) are BSS and are not file-patchable.
Evidence: MEASURED — PE section table and VA-to-file map re-read from the
named specimen on 2026-08-22; hash matched.
Specimen: `local-lab/pristine-verification-2026-07-26/pristine-target/BEA.exe`
SHA-256 `74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750`
(2,506,752 bytes).

## Parsed section table

Re-read 2026-08-22 from the named specimen (2,506,752 bytes; hash match).
PE32, `image_base=0x00400000`, four sections:

| name | VA | VirtualSize | raw | SizeOfRawData | file-backed VA end |
|---|---|---|---|---|---|
| `.text` | `0x00401000` | `0x1D6F9D` | `0x1000` | `0x1D7000` | `0x005D8000` |
| `.rdata` | `0x005D8000` | `0x4985C` | `0x1D8000` | `0x4A000` | `0x00622000` |
| `.data` | `0x00622000` | `0x3B2614` | `0x222000` | `0x3F000` | `0x00661000` |
| `.rsrc` | `0x009D5000` | `0x2F50` | `0x261000` | `0x3000` | `0x009D8000` |

`.data` virtual end is `0x009D4614`. Everything from `0x00661000` through
that virtual end is **BSS**: the loader zero-fills it; those VAs have no
file bytes. A naive `VA − 0x400000` landing past `0x00261000` hits
`.rsrc` raw (or past EOF), not the runtime global.

## Consequence for the first-cut census

`t_7b48b14a` rowed `g_bGodModeEnabled` `0x00662AB4` as a file-born TRUE
patch. That VA maps into `.data` BSS (`delta 0x40AB4` ≥ raw `0x3F000`).
The zeros previously read at file `0x262AB4` are `.rsrc` bytes, not the
flag. File-patching them would corrupt resources and would not set god
mode. Successor `t_14fcbbed` retracts that TSV row.

Same BSS class (not file-patchable):

| VA | first-cut label | refs of the address dword |
|---|---|---|
| `0x00662AB4` | `g_bGodModeEnabled` | 1 |
| `0x00662DD0` | water-death conjunct (not `0x00662DF4`) | 10 |
| `0x00662DF4` | claimed `g_bDevModeEnabled`; file-flat bytes are UTF-16 `scen` in `.rsrc` | 39 |
| `0x00679EC1` | `g_bAllCheatsEnabled` | — |
| `0x00672E20` | FillOut ranking destination | — |
| `0x0089C800` | script pause stop-flag | — |
| `0x008A9AC0` | `g_GameState` | — |
| `0x008A9A98` | `CGame` singleton (`SetPlayerLives` / RBA `this`) | — |
| `0x008A9ADC` | primary-objective array | — |
| `0x008A9B2C` | secondary-objective array | — |
| `0x00662560` | `SetGoodieState` dword table | — |
| `0x008892D8` / `0x008892DC` | 47-row mapping table | — |
| `0x008A9D3C` | player-camera / `GetPlayer` slot table | — |
| `0x008A9D84` | MessageBox singleton | — |
| `0x008A9D90` | `AddHelpMessage` singleton | — |
| `0x00672FD0` | `GameTime` source | — |
| `0x006FBDFC` | `GetWaterHeight` source | — |
| `0x00662564` | `GetGoodieState` view (same table as `0x00662560`) | — |
| `0x008AA51C` | `HighlightHudPart` dword table | — |
| `0x008A9D9C` | `Rand` / `GetFloatRand` RNG object | — |
| `0x006FADC8` | `GetMapHeight` world | — |
| `0x008551C0` / `0x00855228` | `GetNumUnits` allegiance tables | — |
| `0x00855090` | `InitVariable` / `PlayCutscene` lookup `this` | — |
| `0x00672FC8` | `PostEvent` / `Shutdown` event-manager `this` | — |
| `0x00662F10` | `CRTTree__Init` 45.0 override flag | 2 |
| `0x009C7558` | `SetQualityLevel` lod-table dest | 6 |
| `0x00809598` | occupancy bitplane scratch | — |

`t_17fa180d` added the last five after the IScript / SendButtonAction
pin. `t_120c3e1b` added the GetPlayer / MessageBox / GameTime /
GetWaterHeight / HighlightHud / GetGoodieState-view VAs.
`t_94b70425` added `Rand`/`GetFloatRand` `0x008A9D9C`, `GetMapHeight` `0x006FADC8`,
the `GetNumUnits` tables `0x008551C0` / `0x00855228`, lookup
`this` `0x00855090`, and event-manager `this` `0x00672FC8`. `t_94ad2658`
added CRTTree 45-override flag `0x00662F10`, quality-table dest
`0x009C7558`, and occupancy scratch `0x00809598`. Same rule: never
promote those VAs to a file row; patch the `.text` store or the
`.text` jcc that consumes them.

Private `.rdata` added this cut (file-backed, patch the dword /
qword — they are not BSS):

| VA | role | address refs |
|---|---|---|
| `0x005E4FD8` | sky/Kempy far = `sqrt(double)` | 1 |
| `0x005E50F0` | UpdateLOD root 16384.0 | 1 |
| `0x005E50EC` | UpdateLOD level-1 4096.0 | 1 |
| `0x005E50E8` | UpdateLOD level-2 1024.0 | 1 |
| `0x005E50C8` | UpdateLOD camera smoothing 0.03f | 6 (all UpdateLOD) |

Shared, do not value-patch: UpdateLOD shift 60/28/12 at
`0x005DB538` / `0x005DBE34` / `0x005DB4E8`; the other 0.03f
at `0x005D87C0` (20 refs). FOGEND dest is `this+0xE20` on
the engine object, not a global.

Weather dests `0x00660188` / `8C` / `90` / `98..A4` are
**file-backed** `.data` (before `0x00661000`) but ship as zero
and are written again by the init block at `0x00404A20`. They
are not BSS; they are also not useful as file-data patches.
Patch the init `mov` or the IScript `fstp`.

`g_MeshQualityDistance` `0x006321A0`, `cg_meshlodbias`
`0x00631E88`, and scale `0x00630E0C` are file-backed and ship
non-zero, but `CRTMesh__SetQualityLevel` / `CRTTree__Init`
overwrite them. Patch those writers. SP aspect `0x005D8BC4`
(0.75f) is file-backed with **42** address refs — not a value
row; patch `CCamera__GetAspectRatio`'s `je`.

## Rule for later rows

A candidate VA is file-patchable only when it falls in a section's
`[VA, VA + SizeOfRawData)` range. Prefer `.text` instruction patches and
`.rdata` private constants. Never promote a BSS global to a file row.
