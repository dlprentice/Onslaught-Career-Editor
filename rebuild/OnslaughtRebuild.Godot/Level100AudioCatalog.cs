// SPDX-License-Identifier: GPL-3.0-or-later

using System.Collections.ObjectModel;

namespace OnslaughtRebuild.GodotClient;

public enum Level100EffectCue
{
    AquilaStrafe = 0,
    AquilaHydraulics = 1,
    AquilaIncomingMissile = 2,
    AquilaTargetLocked = 3,
    AquilaTargetAcquired = 4,
    PulseCannonFire = 5,
    VulcanCannonFire = 6,
    MicroMissileFire = 7,
    DroneVulcanFire = 8,
    PulseImpact = 9,
    MissileImpact = 10,
    TargetOrTrainerDestroyed = 11,
    DroneDestroyed = 12,
    FacilityDestroyed = 13,
    AquilaDestroyed = 14,
    TransportDestroyed = 15,
    ComponentDebrisDestroyed = 16,
    LargeDebrisDestroyed = 17,
    HugeGroundDebrisDestroyed = 18,
    RepairCharging = 19,
    RepairFull = 20,
}

public enum Level100TerminalCue
{
    AmmunitionDepleted = 0,
    ArmourLow = 1,
    EnergyLow = 2,
    HostileEnvironment = 3,
    IncomingMissile = 4,
    IncomingWarhead = 5,
    MicroMissilesSelected = 6,
    PulseCannonSelected = 7,
    VulcanCannonSelected = 8,
    WeaponOverheating = 9,
}

public enum AquilaWarningAudioState
{
    Normal = 0,
    EnergyLow = 1,
    HullCritical = 2,
}

public enum AquilaTransitionCue
{
    Takeoff = 0,
    InFlight = 1,
    Landing = 2,
}

public enum Level100ActorLoopCue
{
    AirTrainer = 0,
    Transport = 1,
    RepairPadIdle = 2,
}

public readonly record struct Level100MessageAudioSpec(
    int MessageId,
    string Symbol,
    string AudioStem,
    string ResourcePath);

public readonly record struct Level100AudioCueRecipe(
    string ResourcePath,
    int RetailSoundRecord,
    string RetailEffectName,
    float LinearVolume,
    int PitchVariancePercent,
    bool Looping);

public readonly record struct Level100MusicRecipe(
    string ResourcePath,
    string RetailSelection,
    int RetailTrackIndex,
    string RetailSourceName);

// Mix provenance, verified 2026-07-26 against the shipped retail table and the
// GPL-released Onslaught engine sources (see
// local-lab/LEVEL100-AUDIO-PARITY-2026-07-26.md):
//
// * RetailSoundRecord is the record index in data/sounds/sounds.sfx (a plaintext
//   "# SFX <n>" list, version 103, 170 records). RetailEffectName is that
//   record's SAMPLE-PATH field. Retail's own runtime lookup key is the record's
//   DISPLAY-NAME field instead, via CSoundManager::GetEffectByName, so these two
//   fields are provenance only and are not the retail selector.
// * CSoundManager::PlayEffect computes `volume = (volume * effect->mVolume) / 100`
//   where mVolume is the record's integer volume field and the caller's `volume`
//   defaults to DEFAULT_SOUND_VOLUME. Every LinearVolume below is that product.
// * DEFAULT_SOUND_VOLUME 0.7f, mHUDMessageVolume 0.45f and (PC branch)
//   mRadioMessageVolume 0.42f are the released constants. Battle Engine call
//   sites pass ENGINE_VOLUME 1.0f, which is why the engine, strafe and energy
//   cues carry the record volume unscaled.
// * PitchVariancePercent is the record's pitch-variance field; retail applies
//   `pitch += (rand() % variance) / 100`.
public static class Level100AudioCatalog
{
    public const float RetailRadioMessageVolume = 0.42f;
    public const float RetailHudMessageVolume = 0.45f;
    public const float RetailDefaultEffectVolume = 0.70f;

    private static readonly ReadOnlyCollection<Level100MessageAudioSpec>
        s_characterMessages = Array.AsReadOnly(new[]
        {
            Message(292_562, "HUD_01", "hud_01"),
            Message(293_386, "HUD_02", "hud_02"),
            Message(296_682, "HUD_06", "hud_06"),
            Message(-1_575_499_396, "TUTORIAL_MESSAGE_LOG", "tutorial_message_log"),
            Message(-257_967_449, "TUTORIAL_TECHNICIAN_01", "tutorial_technician_01"),
            Message(82_987_417, "TUTORIAL_13_MOD", "tutorial_13_mod"),
            Message(4_422_830, "TUTORIAL_01", "tutorial_01"),
            Message(175_347_826, "TUTORIAL_SCANNER", "tutorial_scanner"),
            Message(4_458_134, "TUTORIAL_02", "tutorial_02"),
            Message(4_493_438, "TUTORIAL_03", "tutorial_03"),
            Message(295_858, "HUD_05", "hud_05"),
            Message(1_339_691_000, "TUTORIAL_PULSE_CANNON", "tutorial_pulse_cannon"),
            Message(669_198_996, "TUTORIAL_OPEN_FIRE", "tutorial_open_fire"),
            Message(-1_715_818_922, "TUTORIAL_PULSE_CANNON_2", "tutorial_pulse_cannon_2"),
            Message(-1_616_775_312, "TUTORIAL_VULCAN_CANNON", "tutorial_vulcan_cannon"),
            Message(-1_860_407_443, "TUTORIAL_OPEN_FIRE_2", "tutorial_open_fire_2"),
            Message(864_965_454, "TUTORIAL_VULCAN_CANNON_2", "tutorial_vulcan_cannon_2"),
            Message(294_210, "HUD_03", "hud_03"),
            Message(295_034, "HUD_04", "hud_04"),
            Message(297_506, "HUD_07", "hud_07"),
            Message(298_330, "HUD_08", "hud_08"),
            Message(4_564_046, "TUTORIAL_05", "tutorial_05"),
            Message(22_775_962, "TUTORIAL_ZOOM", "tutorial_zoom"),
            Message(667_656_903, "TUTORIAL_DODGE_MOD", "tutorial_dodge_mod"),
            Message(150_647_733, "TUTORIAL_DODGE_2", "tutorial_dodge_2"),
            Message(151_778_876, "TUTORIAL_DODGE_3", "tutorial_dodge_3"),
            Message(1_326_027_769, "TUTORIAL_DODGE_GOOD", "tutorial_dodge_good"),
            Message(623_538_785, "TUTORIAL_DODGE_BAD", "tutorial_dodge_bad"),
            Message(4_528_742, "TUTORIAL_04", "tutorial_04"),
            Message(165_861_931, "TUTORIAL_LANDING", "tutorial_landing"),
            Message(4_599_350, "TUTORIAL_06", "tutorial_06"),
            Message(1_062_059_777, "TUTORIAL_THROTTLE_MOD", "tutorial_throttle_mod"),
            Message(4_475_837, "TUTORIAL_12", "tutorial_12"),
            Message(4_705_262, "TUTORIAL_09", "tutorial_09"),
            Message(4_634_654, "TUTORIAL_07", "tutorial_07"),
            Message(80_260_569, "TUTORIAL_STRAFE", "tutorial_strafe"),
            Message(4_669_958, "TUTORIAL_08", "tutorial_08"),
            Message(4_440_532, "TUTORIAL_11", "tutorial_11"),
            Message(162_342_028, "TUTORIAL_ABORTED", "tutorial_aborted"),
            Message(150_940_633, "TUTORIAL_BROKE_1", "tutorial_broke_1"),
            Message(152_071_864, "TUTORIAL_BROKE_2", "tutorial_broke_2"),
            Message(153_203_095, "TUTORIAL_BROKE_3", "tutorial_broke_3"),
            Message(-1_455_850_811, "TUTORIAL_HELP_PLAYER", "tutorial_help_player"),
            Message(4_405_227, "TUTORIAL_10", "tutorial_10"),
            Message(-185_551_049, "TUTORIAL_TECHNICIAN_02", "tutorial_technician_02"),
            Message(-113_134_649, "TUTORIAL_TECHNICIAN_03", "tutorial_technician_03"),
            Message(361_225_970, "TUTORIAL_MOVEMENT", "tutorial_movement"),
            Message(88_347_039, "TUTORIAL_WEAPON", "tutorial_weapon"),
            Message(346_044_574, "TUTORIAL_OVERHEAT", "tutorial_overheat"),
            Message(22_391_142, "TUTORIAL_AMMO", "tutorial_ammo"),
            Message(44_677_289, "TUTORIAL_WATER", "tutorial_water"),
        });

    public static IReadOnlyList<Level100MessageAudioSpec> CharacterMessages =>
        s_characterMessages;

    public static Level100MusicRecipe TutorialMusic { get; } = new(
        "res://Assets/Level100/Music/tutorial-track-03.ogg",
        "MUS_TUTORIAL",
        3,
        "data/Music/BEA_04(Master).ogg");

    // MUS_FRONTEND resolves to track index 8, verified 2026-07-27 in all three
    // steps against pristine BEA.exe (sha256 74154bfa..., file
    // local-lab/safe-copy-bea-pristine/BEA.exe.original.backup):
    //
    // 1. INDEX 8. CMusic::PlaySelection (0x004bb8c0) case 0 computes
    //    `(-(uint)(DAT_0083d448 != 0) & 0xfffffff9) + 8`, i.e. Music.cpp:466-472's
    //    `PLAYABLE_DEMO ? 1 : 8`. DAT_0083d448 sits past .data's raw-backed extent
    //    (raw covers VA 0x00622000-0x00661000) so it loads zero, and its only
    //    writer in the image is CLIParams::ParseCommandLine (0x00423bc0) on the
    //    "-playabledemo" argument. A normal launch therefore selects 8.
    // 2. ZERO-BASED. The GetSong walk inlined at 0x004bb8c0 starts at mFirstSong
    //    (this+0xc) and advances `index` times through mNext (song+0x104), so
    //    index 0 is the head. Matches Music.cpp:476-490.
    // 3. ALPHABETICAL. PCPlatform::InitMusicPlaylist (0x00515320) calls
    //    LoadPlaylistFromDir("data\music") with the extension token at
    //    0x00630a04, which is the asciiz string "ogg". CMusic::AddToPlayList
    //    (Music.cpp:306-362) inserts before the first stricmp-greater filename.
    //    data/Music holds exactly BEA_01..BEA_10(Master).ogg and nothing else, and
    //    stricmp order equals numeric order there, so index 8 is BEA_09.
    //
    // The same rule at index 3 yields TutorialMusic's BEA_04, which is already
    // materialized and hash-verified, so it is corroborated at a second point.
    public static Level100MusicRecipe FrontendMusic { get; } = new(
        "res://Assets/Frontend/Music/frontend-track-08.ogg",
        "MUS_FRONTEND",
        8,
        "data/Music/BEA_09(Master).ogg");

    public static Level100MessageAudioSpec GetCharacterMessage(int messageId)
    {
        foreach (Level100MessageAudioSpec message in s_characterMessages)
        {
            if (message.MessageId == messageId)
            {
                return message;
            }
        }

        throw new ArgumentOutOfRangeException(
            nameof(messageId),
            messageId,
            "The mission requested a character message outside the accepted Level 100 set.");
    }

    public static Level100AudioCueRecipe GetFrontend(string cueName) => cueName switch
    {
        "Back" => Cue(
            "res://Assets/Frontend/SoundEffects/back.wav",
            43,
            "Front End\\N_FE_back",
            RetailDefaultEffectVolume * 0.52f),
        "Move" => Cue(
            "res://Assets/Frontend/SoundEffects/move.wav",
            44,
            "Front End\\N_FE_move",
            RetailDefaultEffectVolume * 0.49f),
        "Select" => Cue(
            "res://Assets/Frontend/SoundEffects/select.wav",
            45,
            "Front End\\N_FE_select",
            RetailDefaultEffectVolume * 0.52f),
        _ => throw new ArgumentOutOfRangeException(nameof(cueName), cueName, null),
    };

    public static Level100AudioCueRecipe GetEffect(Level100EffectCue cue) => cue switch
    {
        Level100EffectCue.AquilaStrafe => Cue(
            "res://Assets/Aquila/SoundEffects/strafe.wav",
            21,
            "Battle Engine\\N_BE_dash",
            0.80f,
            pitch: 10),
        Level100EffectCue.AquilaHydraulics => Cue(
            "res://Assets/Aquila/SoundEffects/hydraulics.wav",
            32,
            "Battle Engine\\N_BE_hydraulics_02",
            RetailHudMessageVolume * 0.40f),
        Level100EffectCue.AquilaIncomingMissile => Cue(
            "res://Assets/Aquila/SoundEffects/incoming-missile.wav",
            33,
            "Battle Engine\\N_BE_incoming_missile",
            RetailHudMessageVolume * 0.80f,
            pitch: 5),
        Level100EffectCue.AquilaTargetLocked => Cue(
            "res://Assets/Aquila/SoundEffects/target-locked.wav",
            30,
            "Battle Engine\\N_BE_homing_missile_lock",
            RetailHudMessageVolume * 0.80f),
        Level100EffectCue.AquilaTargetAcquired => Cue(
            "res://Assets/Aquila/SoundEffects/target-acquired.wav",
            31,
            "Battle Engine\\N_BE_homing_missile_target",
            RetailHudMessageVolume * 0.80f),
        Level100EffectCue.PulseCannonFire => Cue(
            "res://Assets/Level100/SoundEffects/pulse-cannon-fire.wav",
            37,
            "Battle Engine\\N_BE_pulse_cannon_fire",
            RetailDefaultEffectVolume * 0.65f,
            pitch: 5),
        Level100EffectCue.VulcanCannonFire => Cue(
            "res://Assets/Aquila/SoundEffects/vulcan-cannon-fire.wav",
            42,
            "Battle Engine\\N_BE_vulcan_cannon_fire",
            RetailDefaultEffectVolume * 0.75f,
            pitch: 7),
        Level100EffectCue.MicroMissileFire => Cue(
            "res://Assets/Aquila/SoundEffects/micro-missile-fire.wav",
            34,
            "Battle Engine\\N_BE_micro_missiles_fire",
            RetailDefaultEffectVolume * 0.80f,
            pitch: 15),
        // sounds.sfx holds three "Blaster" records; 155 ("Blaster 2") is the one
        // whose volume 60 and pitch variance 10 this recipe carries. Record 156
        // ("Blaster 1") names the same sample at volume 80 / variance 0. Which of
        // the two the Level 100 Target Drone selects is NOT yet established.
        Level100EffectCue.DroneVulcanFire => Cue(
            "res://Assets/Level100/SoundEffects/drone-vulcan-fire.wav",
            155,
            "Weapons\\N_WP_blaster_02",
            RetailDefaultEffectVolume * 0.60f,
            pitch: 10),
        Level100EffectCue.PulseImpact or Level100EffectCue.DroneDestroyed => Cue(
            "res://Assets/Level100/SoundEffects/explosion-small.wav",
            108,
            "Impact\\N_I_explosion_small_debris",
            RetailDefaultEffectVolume * 0.70f,
            pitch: 20),
        Level100EffectCue.MissileImpact or
        Level100EffectCue.TargetOrTrainerDestroyed => Cue(
            "res://Assets/Level100/SoundEffects/target-tank-explosion-medium.wav",
            104,
            "Impact\\N_I_explosion_medium",
            RetailDefaultEffectVolume * 0.70f,
            pitch: 30),
        Level100EffectCue.FacilityDestroyed => Cue(
            "res://Assets/Level100/SoundEffects/facility-explosion-medium.wav",
            105,
            "Impact\\N_I_explosion_medium_ricochet",
            RetailDefaultEffectVolume * 0.70f,
            pitch: 30),
        Level100EffectCue.AquilaDestroyed => Cue(
            "res://Assets/Level100/SoundEffects/aquila-explosion-huge.wav",
            109,
            "Impact\\N_I_explosion_vbig",
            RetailDefaultEffectVolume * 0.70f,
            pitch: 30),
        Level100EffectCue.TransportDestroyed => Cue(
            "res://Assets/Level100/SoundEffects/transport-explosion-large.wav",
            96,
            "Impact\\N_I_explosion_big",
            RetailDefaultEffectVolume * 0.70f,
            pitch: 30),
        Level100EffectCue.ComponentDebrisDestroyed => Cue(
            "res://Assets/Level100/SoundEffects/component-explosion.wav",
            95,
            "Impact\\N_I_explosion2",
            RetailDefaultEffectVolume * 0.70f,
            pitch: 30),
        Level100EffectCue.LargeDebrisDestroyed => Cue(
            "res://Assets/Level100/SoundEffects/explosion-large-debris.wav",
            97,
            "Impact\\N_I_explosion_big_debris",
            RetailDefaultEffectVolume * 0.70f,
            pitch: 30),
        Level100EffectCue.HugeGroundDebrisDestroyed => Cue(
            "res://Assets/Level100/SoundEffects/explosion-huge-ground-debris.wav",
            110,
            "Impact\\N_I_explosion_vbig_debris",
            RetailDefaultEffectVolume * 0.70f,
            pitch: 30),
        Level100EffectCue.RepairCharging => Cue(
            "res://Assets/Level100/SoundEffects/repair-charging.wav",
            7,
            "Atmospheres\\N_A_health_pod_charging",
            RetailDefaultEffectVolume * 0.80f),
        Level100EffectCue.RepairFull => Cue(
            "res://Assets/Level100/SoundEffects/repair-full.wav",
            8,
            "Atmospheres\\N_A_health_pod_full",
            RetailDefaultEffectVolume * 0.80f),
        _ => throw new ArgumentOutOfRangeException(nameof(cue)),
    };

    public static Level100AudioCueRecipe GetTerminal(Level100TerminalCue cue) => cue switch
    {
        Level100TerminalCue.AmmunitionDepleted => Terminal(
            "ammunition-depleted", 46, "HUD\\N_HUD_Ammunition_Depleted"),
        Level100TerminalCue.ArmourLow => Terminal(
            "armour-low", 48, "HUD\\N_HUD_Armour_Low"),
        Level100TerminalCue.EnergyLow => Terminal(
            "energy-low", 53, "HUD\\N_HUD_Energy_Low"),
        Level100TerminalCue.HostileEnvironment => Terminal(
            "hostile-environment", 57, "HUD\\N_HUD_Hostile_Environment"),
        Level100TerminalCue.IncomingMissile => Terminal(
            "incoming-missile", 58, "HUD\\N_HUD_Incoming_Missile"),
        Level100TerminalCue.IncomingWarhead => Terminal(
            "incoming-warhead", 59, "HUD\\N_HUD_Incoming_Warhead"),
        Level100TerminalCue.MicroMissilesSelected => Terminal(
            "micro-missiles-selected", 60, "HUD\\N_HUD_Micro_Missiles"),
        Level100TerminalCue.PulseCannonSelected => Terminal(
            "pulse-cannon-selected", 62, "HUD\\N_HUD_Pulse_Cannon"),
        Level100TerminalCue.VulcanCannonSelected => Terminal(
            "vulcan-cannon-selected", 72, "HUD\\N_HUD_Vulcan_Cannon"),
        Level100TerminalCue.WeaponOverheating => Terminal(
            "weapon-overheating", 75, "HUD\\N_HUD_Weapon_Overheating"),
        _ => throw new ArgumentOutOfRangeException(nameof(cue)),
    };

    public static Level100AudioCueRecipe GetAquilaTransition(AquilaTransitionCue cue) =>
        cue switch
        {
            AquilaTransitionCue.Takeoff => Cue(
                "res://Assets/Aquila/SoundEffects/engine-takeoff.wav",
                26,
                "Battle Engine\\N_BE_engine_takeoff",
                0.40f),
            AquilaTransitionCue.InFlight => Cue(
                "res://Assets/Aquila/SoundEffects/engine-inflight.wav",
                24,
                "Battle Engine\\N_BE_engine_inflight",
                0.50f,
                looping: true),
            AquilaTransitionCue.Landing => Cue(
                "res://Assets/Aquila/SoundEffects/engine-land.wav",
                25,
                "Battle Engine\\N_BE_engine_land",
                0.40f),
            _ => throw new ArgumentOutOfRangeException(nameof(cue)),
        };

    public static Level100AudioCueRecipe GetAquilaWarning(AquilaWarningAudioState state) =>
        state switch
        {
            AquilaWarningAudioState.EnergyLow => Cue(
                "res://Assets/Aquila/SoundEffects/energy-low.wav",
                23,
                "Battle Engine\\N_BE_energy_low",
                0.70f,
                looping: true),
            AquilaWarningAudioState.HullCritical => Cue(
                "res://Assets/Aquila/SoundEffects/energy-critical.wav",
                22,
                "Battle Engine\\N_BE_energy_critical",
                0.70f,
                looping: true),
            _ => throw new ArgumentOutOfRangeException(nameof(state)),
        };

    public static Level100AudioCueRecipe GetActorLoop(Level100ActorLoopCue cue) => cue switch
    {
        Level100ActorLoopCue.AirTrainer => Cue(
            "res://Assets/Level100/SoundEffects/trainer-flyby.wav",
            121,
            "Vehicles\\N_V_F_fighter_flyby",
            RetailDefaultEffectVolume * 0.45f,
            pitch: 15,
            looping: true),
        Level100ActorLoopCue.Transport => Cue(
            "res://Assets/Level100/SoundEffects/transport-flyby.wav",
            129,
            "Vehicles\\N_V_bomber_flyby",
            RetailDefaultEffectVolume * 0.40f,
            pitch: 15,
            looping: true),
        Level100ActorLoopCue.RepairPadIdle => Cue(
            "res://Assets/Level100/SoundEffects/repair-idle.wav",
            9,
            "Atmospheres\\N_A_health_pod_on",
            RetailDefaultEffectVolume * 0.50f,
            looping: true),
        _ => throw new ArgumentOutOfRangeException(nameof(cue)),
    };

    public static float ToRetailOptionMix(float optionValue)
    {
        if (!float.IsFinite(optionValue) || optionValue is < 0f or > 1f)
        {
            throw new ArgumentOutOfRangeException(
                nameof(optionValue),
                optionValue,
                "Audio option values must be finite and between zero and one.");
        }

        const float curve = 1.38f;
        float mix = 1f -
            (MathF.Tan((1f - optionValue) * curve) / MathF.Tan(curve));
        return Math.Clamp(mix, 0f, 1f);
    }

    private static Level100MessageAudioSpec Message(
        int messageId,
        string symbol,
        string audioStem) => new(
            messageId,
            symbol,
            audioStem,
            $"res://Assets/Level100/TutorialAudio/{audioStem}.ogg");

    private static Level100AudioCueRecipe Terminal(
        string localName,
        int record,
        string effectName) => Cue(
            $"res://Assets/Level100/SoundEffects/terminal-{localName}.wav",
            record,
            effectName,
            RetailHudMessageVolume);

    private static Level100AudioCueRecipe Cue(
        string resourcePath,
        int record,
        string effectName,
        float linearVolume,
        int pitch = 0,
        bool looping = false) => new(
            resourcePath,
            record,
            effectName,
            linearVolume,
            pitch,
            looping);
}

internal sealed class Level100CharacterMessageQueue
{
    private readonly Queue<Level100QueuedCharacterMessage> _messages = [];

    public int Count => _messages.Count;

    public void Enqueue(int speakerId, int messageId) =>
        _messages.Enqueue(new Level100QueuedCharacterMessage(
            speakerId,
            Level100AudioCatalog.GetCharacterMessage(messageId)));

    public bool TryDequeue(out Level100QueuedCharacterMessage message) =>
        _messages.TryDequeue(out message);

    public void Clear() => _messages.Clear();
}

internal readonly record struct Level100QueuedCharacterMessage(
    int SpeakerId,
    Level100MessageAudioSpec Audio);
