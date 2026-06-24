# Mission Speaker Tokens (Global English)
> Source: `game/data/MissionScripts/text/english.txt`
> Generated: Feb 4, 2026

MissionScript Level100 Tutorial Static Event/Command Walkthrough proof planning is recorded in `../binary-analysis/missionscript-level100-tutorial-static-walkthrough-proof-plan.md` and `../binary-analysis/missionscript-level100-tutorial-static-walkthrough.v1.json`. The Level100 tutorial walkthrough uses `P_TATIANA`, `P_KRAMER`, and `P_TECHNICIAN` as static speaker-token evidence only; runtime text/audio behavior and live loose-MSL loading remain separate proof.

MissionScript Level100 Tutorial Text/Speaker Resolution static proof is recorded in `../binary-analysis/missionscript-level100-tutorial-text-speaker-resolution-proof-plan.md` and `../binary-analysis/missionscript-level100-tutorial-text-speaker-resolution.v1.json`. It resolves the Level100 speaker rows as `P_TATIANA` `40`, `P_KRAMER` `4`, and `P_TECHNICIAN` `1` through shared `text/english.txt` and shared `text/text.stf`; this is static label resolution only, not speaker portrait behavior, runtime message display, runtime voice/audio playback, live loose-MSL loading, visual QA, Godot, rebuild, or no-noticeable-difference proof.

| Token | Name | Comment |
|-------|------|---------|
| `P_TATIANA` | Tatiana Kiralova | Chief scientist |
| `P_KRAMER` | Col. Kramer | Chuck Kramer, C.O. |
| `P_FOX` | Lt. Fox | Tara Fox, wingman |
| `P_CASBAH` | Lt. Casbah | Billy Casbah, wingman |
| `P_LORENZO` | Maj. Lorenzo | Jason Lorenzo, wingman |
| `P_CARVER` | Lewis Carver | Nemesis |
| `P_RADAR` | Radar Officer | RADAR OFFICER |
| `P_TECHNICIAN` | Technician |  |
| `P_COMMANDER` | Commander | Ground officer, outdoors FIELD OFFICER |
| `P_OFFICER` | Officer | Indoors COMMS OFFICER |
| `P_TROOPER` | Trooper |  |
| `P_TANK_COMMANDER` | Tank Commander |  |
| `P_FORSETI_PILOT` | Pilot | Bombers, Fighters, Transports |
| `P_SURT` | Gen. Surt |  |
| `P_SIMMONS` | Admiral Simmons |  |
