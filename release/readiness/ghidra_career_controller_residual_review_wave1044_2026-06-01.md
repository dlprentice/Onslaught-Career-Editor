# Ghidra Career Controller Residual Review Wave1044

Status: complete static read-only evidence
Date: 2026-06-01
Scope: `career-controller-residual-review-wave1044`

Wave1044 re-read nine Career.cpp / Controller.cpp residual rows that remained under-documented in tracked public RE text even though the loaded Ghidra rows already had coherent names, signatures, and comments. The pass was read-only with no mutation: no rename, no signature change, no comment/tag write, no function-boundary change, no executable-byte change, no BEA launch, and no runtime/game-file mutation.

Reviewed rows:

| Address | Evidence |
| --- | --- |
| `0x0041b740 CCareerNode__Blank` | Called by `CCareer__StaticInitDefaults`; source/decompile body clears world/attempt/complete fields, sets link/base-thing dwords to `0xffffffff`, and writes ranking `0xbf800000` (`-1.0f`). |
| `0x0041c180 CCareer__UpdateThingsKilled` | Called by `CCareer__Update`; skips world `100`, adds five `g_LevelKillCounts` counters into career kill counters near `this+0x23f4`, and logs category totals masked with `0x00ffffff`. |
| `0x0041c470 CCareer__UpdateGoodieStates` | Called by `CCareer__Blank` and `CCareer__Update`; source/decompile evidence walks 300 Goodies states at `this+0x1f44`, uses completion/grade tests such as `CCareer__GetGradeForWorld` and `CGrade__operator_gte`, and promotes unlock states when conditions pass. |
| `0x004214e0 CCareer__SetSlot` | Called by `IScript__SetSlotSave`; validates slot range `0..0xff`, computes `1 << (slot & 31)`, and sets or clears the matching dword at `this+0x2408+(slot>>5)*4`. |
| `0x0042d640 CController__Init` | Called by `CController__ctor`; initializes `CSPtrSet` and `CDXMemBuffer`, registers a monitored active-reader node against `player+0x04`, stores input/config fields, and clears playback/recording state. |
| `0x0042d8a0 CController__StartRecording` | Called by `CGame__PostLoadProcess`; sets recording flag `this+0x160` and opens controller data buffer for write via `CDXMemBuffer__OpenWrite`. |
| `0x0042d8c0 CController__StartPlayback` | Called by `CGame__PostLoadProcess`; sets playback flag `this+0x161` and initializes the controller data buffer from file via `CDXMemBuffer__InitFromFile`. |
| `0x0042d8e0 CController__dtor` | Called by `CLTShell__InitializeRuntimeAndLoadCoreResources`, `CController__scalar_deleting_dtor`, and `CController__dtor_Thunk`; closes active playback/recording buffer, removes monitored active-reader nodes through `CMonitor__DeleteDeletionEvent`, frees them with `CDXMemoryManager__Free`, clears the set, and runs `CDXMemBuffer__dtor_base`. |
| `0x004f00d0 CController__dtor_Thunk` | Called by `Unwind@005d5030` and `CPCController__scalar_deleting_dtor`; direct thunk forwarding to `CController__dtor`. |

Context anchors include `0x0041b7c0 CCareer__Blank`, `0x0041bd00 CCareer__Update`, `0x0041bdf0 CCareer__ReCalcLinks`, `0x00421200 CCareer__Load`, `0x00421350 CCareer__Save`, `0x0042d780 CController__scalar_deleting_dtor`, `0x0042d9d0 CController__Flush`, `0x0042db40 CController__DoMappings`, `0x005145f0 CController__ctor`, `0x00514720 CPCController__RecordControllerState`, and `0x00514760 CPCController__ReadControllerState`.

Read-back evidence:

- Primary exports: 9 metadata rows, 9 tag rows, 14 xref rows, 5815 body-instruction rows, and 9 decompile rows.
- Context exports: 11 metadata rows, 11 tag rows, 25 xref rows, 1259 body-instruction rows, and 11 decompile rows.
- Queue after Wave1044 remains 6238 total, 6238 commented, 0 commentless, 0 exact-undefined signatures, 0 `param_N`, strict clean-signature proxy `6238/6238 = 100.00%`.
- Wave1044 targets are not Wave911 focused TSV rows, so Wave911 focused progress remains `735/1408 = 52.20%`; expanded static surface progress advances to `977/1493 = 65.44%`; top-500 risk-ranked coverage remains `500/500 = 100.00%`.
- Verified backup: `G:\GhidraBackups\BEA_20260601-103855_post_wave1044_career_controller_residual_review_verified`, 19 files, 174263175 bytes, `DiffCount=0`, `HashDiffCount=0`.

What remains separate proof:

- Runtime save/progression behavior.
- Runtime Goodies unlock behavior.
- Runtime controller/input/recording/playback behavior.
- Concrete `CCareer`, `CCareerNode`, `CController`, `CPCController`, and active-reader layouts beyond observed offsets.
- Exact source-body identity.
- BEA patching behavior.
- Gameplay outcomes.
- Rebuild parity.
