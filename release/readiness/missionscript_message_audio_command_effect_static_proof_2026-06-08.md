# MissionScript Message/Audio Command-Effect Static Proof Readiness Note

Status: static message/audio command-effect schema proof complete, not runtime proof
Date: 2026-06-08
Scope: `missionscript-message-audio-command-effect-static`

This readiness note records the static-to-proof consolidation for `missionscript-message-audio-command-effect-static-proof.md` and `missionscript-message-audio-command-effect.v1.json`. It adds no Ghidra mutation, no executable mutation, no runtime proof, no visual QA, no patch, no Godot work, and no rebuild parity claim.

Static closeout remains unchanged:

- Static Ghidra function-quality closure: `6411/6411 = 100.00%`.
- Static debt: `0 / 0 / 0`.
- Expanded post-100 static surface: `1560/1560 = 100.00%`.
- Active current-risk focused accounting: `1179/1179 = 100.00%`.
- Remaining active focused work: `0`.
- Latest verified Ghidra backup remains `[maintainer-local-ghidra-backup-root]\BEA_20260607-230027_post_wave1219_final_score16_current_risk_review_verified`.

Representative anchors:

| Surface | Evidence |
| --- | --- |
| Descriptor names | `PlayCharMessage`, `PlayCharMessageWait`, `PlayPCharMessage`, `PlayPCharMessageWait`, `SwitchMessagesOn`, `SwitchMessagesOff`, `AddHelpMessage`, `PrintText`, and `AddMessage` are preserved from the finite `144`-slot descriptor schema. |
| Message/audio queue bodies | `IScript__PlaySound`, `IScript__PlaySoundWithCallback`, `IScript__PlaySoundWithFade`, `IScript__PlaySoundWithPriority`, and `IScript__PlaySoundWithFadeAndPriority` enqueue `CMessage` objects through `CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance` when static guard/context evidence allows. |
| Console text boundary | `IScript__PrintText` calls `CText__GetStringById` and `CConsole__Printf("%w")`. |
| Message lifecycle context | `CMessage__ctor_base`, `CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance`, `CMessageBox__StartVoiceOrFallbackTextReveal`, `CMessageBox__AdvanceRevealAndScheduleNextTick`, `CMessageBox__StopVoicePlaybackIfNotInCutscene`, and `CMessageBox__RenderOverlay`. |
| Loose message corpus | `1365 PlayCharMessage`, `7 AddHelpMessage`, `110 LevelLost-family`, `71 LevelWon-family`, `1553 detailed message rows`, `11 speakers`, and `499 unique message tokens`. |

Evidence counts:

- Wave584: `11` metadata rows, `11` tag rows, `11` xref rows, `4059` instruction rows, `11` decompile rows, and `64` vtable rows.
- Wave1015: `7` metadata rows, `7` tag rows, `14` xref rows, `195` instruction rows, `7` decompile rows, plus `17` context metadata, `549` context xref, `548` context instruction, and `17` context decompile rows.
- Wave1074: `1` metadata row, `1` tag row, `1` xref row, `13` body instruction rows, and `1` decompile row.
- Focused schema probe: `tools/missionscript_message_audio_command_effect_static_probe.py --check`.

What this proves:

- The static descriptor table contains the selected message/audio/HUD-adjacent command names and record addresses.
- Saved IScript message/audio bodies statically bridge text ids, payload arguments, fade/priority context, `CMessage` construction, and `CMessageBox` queue insertion.
- `IScript__PrintText` has a saved console/text static boundary.
- The loose-MSL message corpus has reproducible aggregate and detailed callsite counts.

What remains unproven:

- Runtime MissionScript execution.
- Runtime command effects.
- Runtime message display.
- Runtime voice/audio playback.
- Runtime HUD output.
- Runtime queue ordering.
- Live loose-MSL loading or packed-vs-loose resource selection.
- Exact descriptor, `CMessage`, or `CMessageBox` concrete layout.
- BEA patching behavior.
- Visual QA.
- Godot parity.
- Rebuild parity.
- No-noticeable-difference parity.
