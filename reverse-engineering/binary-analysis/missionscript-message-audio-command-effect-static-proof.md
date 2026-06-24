# MissionScript Message/Audio Command-Effect Static Proof

Status: static message/audio command-effect schema proof complete, not runtime proof
Last updated: 2026-06-08
Scope: `missionscript-message-audio-command-effect-static`
Artifact: `missionscript-message-audio-command-effect-static-proof.md`; schema: `missionscript-message-audio-command-effect.v1.json`

This proof converts saved retail Ghidra evidence from Wave584, Wave903, Wave1015, and Wave1074 plus public-safe loose MissionScript message indexes into a machine-checkable message/audio command-effect map at `missionscript-message-audio-command-effect.v1.json`. It is the next narrow IScript command-effect child lane after the completed slot and objective/outcome proofs.

Static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0` commentless, exact-undefined, and `param_N` rows.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup remains `G:\GhidraBackups\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

## Schema Result

| Surface | Static result |
| --- | --- |
| Descriptor slots | The descriptor schema records `PlaySample` index `9` at `0x0064d090`, `PrintText` index `15` at `0x0064d210`, `AddMessage` index `16` at `0x0064d250`, `PlayCharMessage` index `27` at `0x0064d510`, `HighlightHudPart` index `33` at `0x0064d690`, `UnHighlightHudPart` index `34` at `0x0064d6d0`, `PlayCharMessageWait` index `35` at `0x0064d710`, `PlayPCharMessage` index `89` at `0x0064e490`, `PlayPCharMessageWait` index `90` at `0x0064e4d0`, `SwitchMessagesOn` index `111` at `0x0064ea10`, `SwitchMessagesOff` index `112` at `0x0064ea50`, and `AddHelpMessage` index `117` at `0x0064eb90`. |
| Descriptor raw-entry boundary | The schema preserves raw entry values such as `&LAB_00535890`, `&LAB_00535e80`, `IScript__PlaySoundWithPriority`, and `IScript__GetThingTypeName` as static table evidence only. Exact command descriptor field layout and one-to-one command-handler mapping remain bounded, not proven. |
| Message/audio queue handlers | Wave584 saved `IScript__PlaySound`, `IScript__PlaySoundWithCallback`, `IScript__PlaySoundWithFade`, `IScript__PlaySoundWithPriority`, and `IScript__PlaySoundWithFadeAndPriority`. These bodies read text ids, float payloads, priority/fade arguments, and active-reader context where present, then enqueue `CMessage` objects through `CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance` when `DAT_008a9d84` is present. |
| Console text boundary | Wave1074 saved `0x00537c40 IScript__PrintText`, tied to `s_PrintText_0064f984` and `0x0064d220` descriptor/name evidence. Its body reads `script_args[0]`, calls `CText__GetStringById`, and forwards the localized text through `CConsole__Printf("%w")`. |
| MessageBox queue context | Wave1015 and the MessageBox owner docs preserve `CMessage__ctor_base`, `CMessage__scalar_deleting_dtor`, `CMessage__dtor_base`, `CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance`, `CMessageBox__StartVoiceOrFallbackTextReveal`, `CMessageBox__AdvanceRevealAndScheduleNextTick`, `CMessageBox__StopVoicePlaybackIfNotInCutscene`, and `CMessageBox__RenderOverlay` as the static queued-message lifecycle context. |
| Loose message corpus | `mission-message-usage.md` records `67` level rows, `1365 PlayCharMessage`, `7 AddHelpMessage`, `110 LevelLost-family`, and `71 LevelWon-family`. The split detailed callsite tables record `1553 detailed message rows`, `11 speakers`, and `499 unique message tokens`. |

Evidence rows consumed by the schema:

| Evidence | Count |
| --- | ---: |
| Wave584 metadata/tag/xref/decompile rows | `11` / `11` / `11` / `11` |
| Wave584 instruction rows and vtable rows | `4059` / `64` |
| Wave1015 metadata/tag/xref/decompile rows | `7` / `7` / `14` / `7` |
| Wave1015 instruction rows | `195` |
| Wave1015 context metadata/xref/instruction/decompile rows | `17` / `549` / `548` / `17` |
| Wave1074 metadata/tag/xref/decompile rows | `1` / `1` / `1` / `1` |
| Wave1074 body instruction rows | `13` |

Backups already verified by their original waves:

- Wave584: `G:\GhidraBackups\BEA_20260519-091559_post_wave584_iscript_object_audio_verified`
- Wave1015: `G:\GhidraBackups\BEA_20260531-192131_post_wave1015_ogg_message_lifecycle_review_verified`
- Wave1074: `G:\GhidraBackups\BEA_20260602-052830_post_wave1074_script_text_console_boundary_verified`

## Why This Matters

This gives clean-room MissionScript planning a bounded message/audio bridge: descriptor names, raw descriptor entries, saved IScript message/audio queue bodies, CMessage/CMessageBox lifecycle context, console text output context, and loose-MSL message corpus counts. It turns scattered wave notes into a reusable contract for later interpreter, message-log, audio, HUD, or rebuild slices.

The proof intentionally keeps `LevelLost` / `LevelWon` message-family counts separate from the completed objective/outcome proof. It also keeps `HighlightHudPart` and `UnHighlightHudPart` as descriptor context only here; the later `missionscript-hud-display-command-effect-static-proof.md` / `missionscript-hud-display-command-effect.v1.json` slice records the MissionScript HUD / Display Command-Effect static descriptor/corpus bridge, while concrete runtime HUD behavior and visual output remain deferred to copied/app-owned proof.

## Claim Boundary

This proves static message/audio command-effect accounting from saved retail Ghidra evidence and public-safe loose-MSL corpus counts. It does not prove runtime MissionScript execution, runtime command effects, runtime message display, runtime voice playback, runtime audio playback, runtime HUD output, runtime queue ordering, live loose-MSL loading, packed-vs-loose script selection, exact command descriptor layout, exact arity, exact argument type schema, exact `CMessage` layout, exact `CMessageBox` layout, BEA patching behavior, visual QA, Godot parity, rebuild parity, or no-noticeable-difference parity.
