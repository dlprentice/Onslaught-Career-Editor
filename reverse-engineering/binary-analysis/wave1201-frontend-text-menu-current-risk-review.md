# Wave1201 Frontend Text Menu Current-Risk Review

Status: complete read-only static evidence; historical artifact committed
Date: 2026-06-06
Tag: `wave1201-frontend-text-menu-current-risk-review`

Wave1201 re-read `25 frontend/text/menu current-risk rows` from the `wave1108-current-risk-rank` current-risk denominator. The cluster covers frontend wide-text wrapping and localization fallback, game-interface menu control dispatch, FEP briefing/demo/development/main/save/load/wingmen/directory page helpers, level briefing log construction/destruction, and compact menu-item vtable/destructor helpers.

Representative anchors:

| Address | Name | Evidence |
| --- | --- | --- |
| `0x00465a20` | `TextLayout__WrapWideTextToFixedLines` | Text layout helper for fixed wide-text line buffers; prior owner/name/signature correction remains current. |
| `0x0046b1e0` | `FrontEndText__GetAsciiFallbackTextByToken` | Frontend localization fallback helper. |
| `0x00472d50` | `CGameInterface__VFunc_03_HandleMenuControlInput` | Menu-control input dispatch path; keep vfunc identity bounded. |
| `0x00459920` | `CFEPMultiplayerStart__SubObj8848__ctor` | Multiplayer-start subobject constructor; no friendly rename from weak evidence. |
| `0x0051ad30` | `CFEPDirectory__RefreshSaveFileList` | Directory/save-file list refresh helper. |
| `0x00521c80` | `CFEPWingmen__Update` | Wingmen frontend page update helper. |
| `0x004f2190` | `CText__GetLanguageName` | CText language-name fallback helper. |

Fresh Ghidra export evidence:

- `25` metadata rows.
- `25` tag rows.
- `78 xref rows`.
- `1264 instruction rows`.
- `25 decompile rows`.
- Verified backup: `[maintainer-local-ghidra-backup-root]\BEA_20260606-235230_post_wave1201_frontend_text_menu_current_risk_review_verified`.

Mutation status: read-only review. The wave made no rename, no signature change, no comment change, no tag change, no function-boundary change, and no executable-byte change.

Accounting:

- Static Ghidra function-quality closure remains `6411/6411 = 100.00%`.
- Commentless / exact-undefined / `param_N` debt remains `0 / 0 / 0`.
- Corrected active current-risk progress is `1042/1179 = 88.38%`.
- Remaining active focused work: `137`.
- Current risk candidates: `6166`.
- Current focused candidates: `1141`.
- Live regenerated current focused candidates: `1141`.
- The legacy additive counter is deprecated (`1073/1179`) because it includes a 26 duplicate-address overcount and Wave1145 arithmetic overcount: 5.
- Wave911 is historical-retired/non-reconstructable at `812/1408 = 57.67%`; this is not Wave911 reconstruction.
- Active target remains `1179/1179 current-risk focused rows reviewed or superseded with bounded static evidence`.

Boundary: this proves fresh static Ghidra metadata/tag/xref/instruction/decompile read-back for the listed frontend/text/menu rows only. Runtime frontend behavior, runtime text rendering, visual parity, exact layouts, exact source-body identity, BEA patching behavior, rebuild parity, and no-noticeable-difference parity remain separate proof.

Probe token anchor: Wave1201; wave1201-frontend-text-menu-current-risk-review; 25 frontend/text/menu current-risk rows; 1042/1179 = 88.38%; current focused candidates: 1141; live regenerated current focused candidates: 1141; remaining active focused work: 137; current risk candidates: 6166; fresh Ghidra export; read-only review; no rename; no signature change; no comment change; no tag change; no function-boundary change; no executable-byte change; TextLayout__WrapWideTextToFixedLines; CGameInterface__VFunc_03_HandleMenuControlInput; CFEPMultiplayerStart__SubObj8848__ctor; CFEPDirectory__RefreshSaveFileList; CFEPWingmen__Update; CText__GetLanguageName; 0 / 0 / 0; 6411/6411 = 100.00%; 78 xref rows; 1264 instruction rows; 25 decompile rows; [maintainer-local-ghidra-backup-root]\BEA_20260606-235230_post_wave1201_frontend_text_menu_current_risk_review_verified; static-reaudit-current-risk-ledger.json; wave1108-current-risk-rank; current-risk denominator; focused threshold `15`; not Wave911 reconstruction; rebuild-grade static contracts; no noticeable difference.
