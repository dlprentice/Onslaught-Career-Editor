// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.GodotClient;

namespace OnslaughtRebuild.Client.Tests;

public sealed class Level100AudioCatalogTests
{
    [Fact]
    public void CharacterMessages_AreTheExactAcceptedLevel100Set()
    {
        (int MessageId, string AudioStem)[] expected =
        [
            (292_562, "hud_01"),
            (293_386, "hud_02"),
            (296_682, "hud_06"),
            (-1_575_499_396, "tutorial_message_log"),
            (-257_967_449, "tutorial_technician_01"),
            (82_987_417, "tutorial_13_mod"),
            (4_422_830, "tutorial_01"),
            (175_347_826, "tutorial_scanner"),
            (4_458_134, "tutorial_02"),
            (4_493_438, "tutorial_03"),
            (295_858, "hud_05"),
            (1_339_691_000, "tutorial_pulse_cannon"),
            (669_198_996, "tutorial_open_fire"),
            (-1_715_818_922, "tutorial_pulse_cannon_2"),
            (-1_616_775_312, "tutorial_vulcan_cannon"),
            (-1_860_407_443, "tutorial_open_fire_2"),
            (864_965_454, "tutorial_vulcan_cannon_2"),
            (294_210, "hud_03"),
            (295_034, "hud_04"),
            (297_506, "hud_07"),
            (298_330, "hud_08"),
            (4_564_046, "tutorial_05"),
            (22_775_962, "tutorial_zoom"),
            (667_656_903, "tutorial_dodge_mod"),
            (150_647_733, "tutorial_dodge_2"),
            (151_778_876, "tutorial_dodge_3"),
            (1_326_027_769, "tutorial_dodge_good"),
            (623_538_785, "tutorial_dodge_bad"),
            (4_528_742, "tutorial_04"),
            (165_861_931, "tutorial_landing"),
            (4_599_350, "tutorial_06"),
            (1_062_059_777, "tutorial_throttle_mod"),
            (4_475_837, "tutorial_12"),
            (4_705_262, "tutorial_09"),
            (4_634_654, "tutorial_07"),
            (80_260_569, "tutorial_strafe"),
            (4_669_958, "tutorial_08"),
            (4_440_532, "tutorial_11"),
            (162_342_028, "tutorial_aborted"),
            (150_940_633, "tutorial_broke_1"),
            (152_071_864, "tutorial_broke_2"),
            (153_203_095, "tutorial_broke_3"),
            (-1_455_850_811, "tutorial_help_player"),
            (4_405_227, "tutorial_10"),
            (-185_551_049, "tutorial_technician_02"),
            (-113_134_649, "tutorial_technician_03"),
            (361_225_970, "tutorial_movement"),
            (88_347_039, "tutorial_weapon"),
            (346_044_574, "tutorial_overheat"),
            (22_391_142, "tutorial_ammo"),
            (44_677_289, "tutorial_water"),
        ];

        (int MessageId, string AudioStem)[] actual = Level100AudioCatalog
            .CharacterMessages
            .Select(message => (message.MessageId, message.AudioStem))
            .ToArray();

        Assert.Equal(expected, actual);
        Assert.Equal(51, actual.Select(item => item.MessageId).Distinct().Count());
        Assert.All(
            Level100AudioCatalog.CharacterMessages,
            message => Assert.Equal(
                $"res://Assets/Level100/TutorialAudio/{message.AudioStem}.ogg",
                message.ResourcePath));
    }

    [Fact]
    public void CharacterMessageQueue_PreservesDuplicateOrderedEvents()
    {
        var queue = new Level100CharacterMessageQueue();
        queue.Enqueue(1_508_464, 292_562);
        queue.Enqueue(1_508_464, 292_562);
        queue.Enqueue(99, 44_677_289);

        Assert.True(queue.TryDequeue(out Level100QueuedCharacterMessage first));
        Assert.True(queue.TryDequeue(out Level100QueuedCharacterMessage second));
        Assert.True(queue.TryDequeue(out Level100QueuedCharacterMessage third));
        Assert.Equal(1_508_464, first.SpeakerId);
        Assert.Equal(292_562, first.Audio.MessageId);
        Assert.Equal(1_508_464, second.SpeakerId);
        Assert.Equal(292_562, second.Audio.MessageId);
        Assert.Equal(99, third.SpeakerId);
        Assert.Equal(44_677_289, third.Audio.MessageId);
        Assert.False(queue.TryDequeue(out _));
    }

    [Fact]
    public void SharedCueRecipes_UseCanonicalRetailRecordsAndAssets()
    {
        Level100AudioCueRecipe pulseImpact =
            Level100AudioCatalog.GetEffect(Level100EffectCue.PulseImpact);
        Level100AudioCueRecipe droneDestroyed =
            Level100AudioCatalog.GetEffect(Level100EffectCue.DroneDestroyed);
        Assert.Equal(108, pulseImpact.RetailSoundRecord);
        Assert.Equal(pulseImpact, droneDestroyed);

        Level100AudioCueRecipe vulcan =
            Level100AudioCatalog.GetEffect(Level100EffectCue.VulcanCannonFire);
        Assert.Equal(42, vulcan.RetailSoundRecord);
        Assert.Equal(
            "res://Assets/Aquila/SoundEffects/vulcan-cannon-fire.wav",
            vulcan.ResourcePath);

        Level100AudioCueRecipe warehouse =
            Level100AudioCatalog.GetEffect(Level100EffectCue.FacilityDestroyed);
        Assert.Equal(105, warehouse.RetailSoundRecord);

        Level100AudioCueRecipe landing =
            Level100AudioCatalog.GetAquilaTransition(AquilaTransitionCue.Landing);
        Assert.Equal(25, landing.RetailSoundRecord);
        Assert.Equal(
            "res://Assets/Aquila/SoundEffects/engine-land.wav",
            landing.ResourcePath);

        Assert.Equal(43, Level100AudioCatalog.GetFrontend("Back").RetailSoundRecord);
        Assert.Equal(44, Level100AudioCatalog.GetFrontend("Move").RetailSoundRecord);
        Assert.Equal(45, Level100AudioCatalog.GetFrontend("Select").RetailSoundRecord);
    }

    [Fact]
    public void CueCatalog_CoversTheExactBoundedLevel100Categories()
    {
        Assert.Equal(
            [21, 32, 33, 30, 31, 37, 42, 34, 155, 108, 104, 104, 108,
                105, 109, 96, 95, 97, 110, 7, 8],
            Enum.GetValues<Level100EffectCue>()
                .Select(cue => Level100AudioCatalog.GetEffect(cue).RetailSoundRecord)
                .ToArray());
        Assert.Equal(
            [46, 48, 53, 57, 58, 59, 60, 62, 72, 75],
            Enum.GetValues<Level100TerminalCue>()
                .Select(cue => Level100AudioCatalog.GetTerminal(cue).RetailSoundRecord)
                .ToArray());
        Assert.Equal(
            [26, 24, 25],
            Enum.GetValues<AquilaTransitionCue>()
                .Select(cue => Level100AudioCatalog
                    .GetAquilaTransition(cue)
                    .RetailSoundRecord)
                .ToArray());
        Assert.Equal(
            [23, 22],
            new[]
            {
                AquilaWarningAudioState.EnergyLow,
                AquilaWarningAudioState.HullCritical,
            }.Select(state => Level100AudioCatalog
                .GetAquilaWarning(state)
                .RetailSoundRecord)
                .ToArray());
        Assert.Equal(
            [121, 129, 9],
            Enum.GetValues<Level100ActorLoopCue>()
                .Select(cue => Level100AudioCatalog.GetActorLoop(cue).RetailSoundRecord)
                .ToArray());

        Assert.Throws<ArgumentOutOfRangeException>(() =>
            Level100AudioCatalog.GetFrontend("fallback"));
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            Level100AudioCatalog.GetCharacterMessage(int.MaxValue));
    }

    [Fact]
    public void TutorialMusic_UsesReleasedTutorialSelectionTrackThree()
    {
        Level100MusicRecipe music = Level100AudioCatalog.TutorialMusic;

        Assert.Equal("MUS_TUTORIAL", music.RetailSelection);
        Assert.Equal(3, music.RetailTrackIndex);
        Assert.Equal("data/Music/BEA_04(Master).ogg", music.RetailSourceName);
        Assert.Equal(
            "res://Assets/Level100/Music/tutorial-track-03.ogg",
            music.ResourcePath);
    }

    // The recovered MUS_FRONTEND law, in one place: which track, that it loops,
    // and that level entry stops it before the tutorial track starts.
    // Evidence for each clause is cited in Level100AudioCatalog.FrontendMusic.
    [Fact]
    public void FrontendMusic_IsTrackEightLoopedAndStoppedOnLevelEntry()
    {
        Level100MusicRecipe music = Level100AudioCatalog.FrontendMusic;

        Assert.Equal("MUS_FRONTEND", music.RetailSelection);
        Assert.Equal(8, music.RetailTrackIndex);
        Assert.Equal("data/Music/BEA_09(Master).ogg", music.RetailSourceName);
        Assert.Equal(
            "res://Assets/Frontend/Music/frontend-track-08.ogg",
            music.ResourcePath);

        // Track 8 is the ninth entry of the alphabetical data\music playlist, and
        // track 3 is the fourth. Both must agree with the same zero-based rule.
        string[] playlist =
        [
            "BEA_01(Master).ogg", "BEA_02(Master).ogg", "BEA_03(Master).ogg",
            "BEA_04(Master).ogg", "BEA_05(Master).ogg", "BEA_06(Master).ogg",
            "BEA_07(Master).ogg", "BEA_08(Master).ogg", "BEA_09(Master).ogg",
            "BEA_10(Master).ogg",
        ];
        Assert.Equal(
            playlist,
            playlist.OrderBy(name => name, StringComparer.OrdinalIgnoreCase));
        Assert.Equal(
            music.RetailSourceName,
            "data/Music/" + playlist[music.RetailTrackIndex]);
        Assert.Equal(
            Level100AudioCatalog.TutorialMusic.RetailSourceName,
            "data/Music/" +
                playlist[Level100AudioCatalog.TutorialMusic.RetailTrackIndex]);

        // The exact retail source must be materialized, and the frontend track
        // must load looping and stop at level entry before the tutorial track.
        string audio = ReadGodotSource("Level100Audio.cs");
        string game = ReadGodotSource("FirstFlightGame.cs");
        string materializer = ReadGodotSource("materialize_retail_assets.py");

        Assert.Contains(music.RetailSourceName, materializer, StringComparison.Ordinal);
        Assert.Contains(
            "LoadOgg(recipe.ResourcePath, looping: true)",
            audio,
            StringComparison.Ordinal);
        AssertOccursInOrder(
            game,
            "_audio.StartFrontendMusic();",
            "_audio.StopFrontendMusic();",
            "_audio.StartTutorialMusic();");
    }

    private static string ReadGodotSource(string fileName) =>
        File.ReadAllText(
            Path.Combine(AppContext.BaseDirectory, "godot-pause-source", fileName));

    private static void AssertOccursInOrder(string source, params string[] values)
    {
        int cursor = 0;
        foreach (string value in values)
        {
            int found = source.IndexOf(value, cursor, StringComparison.Ordinal);
            Assert.True(found >= 0, $"Expected '{value}' after offset {cursor}.");
            cursor = found + value.Length;
        }
    }

    [Fact]
    public void AudioOptionCurve_MatchesReleasedEndpointsAndRejectsInvalidValues()
    {
        Assert.Equal(0f, Level100AudioCatalog.ToRetailOptionMix(0f));
        Assert.Equal(1f, Level100AudioCatalog.ToRetailOptionMix(1f));
        Assert.InRange(Level100AudioCatalog.ToRetailOptionMix(0.5f), 0f, 1f);
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            Level100AudioCatalog.ToRetailOptionMix(float.NaN));
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            Level100AudioCatalog.ToRetailOptionMix(1.01f));
    }

    // Regression fence for a unit error that shipped on 2026-07-27 and was
    // caught in review rather than by a test.
    //
    // Retail's authored cold-start values are OPTION VALUES -
    // CCareer::CCareer (references/Onslaught/Career.cpp:173-174,
    // mSoundVolume=0.8f / mMusicVolume=0.9f), corroborated by the pristine
    // specimen's own initialisers in CCareer::StaticInitDefaults 0x0041B6A0
    // (mov [0x00662AAC], 0.8f at 0x0041B70D; mov [0x00662AB0], 0.9f at
    // 0x0041B717).
    //
    // Level100Audio's _soundOptionMix/_musicOptionMix fields hold the
    // POST-CURVE mix. Assigning 0.8f/0.9f into them directly is therefore a
    // unit error, and a quiet one - it under-drives the game by 1.45 dB and
    // 0.68 dB, which no existing assertion noticed because the endpoint test
    // above only pins ToRetailOptionMix(0) and (1).
    //
    // This test fails on the raw-literal form and on any drift in the curve.
    [Fact]
    public void ColdStartOptionMixes_PushRetailOptionValuesThroughTheCurve()
    {
        const float retailSoundOption = 0.8f;
        const float retailMusicOption = 0.9f;

        string audio = ReadGodotSource("Level100Audio.cs");

        // The option values must still be the sourced retail quantities.
        Assert.Contains(
            $"RetailSoundOptionValue = {retailSoundOption:0.0}f",
            audio,
            StringComparison.Ordinal);
        Assert.Contains(
            $"RetailMusicOptionValue = {retailMusicOption:0.0}f",
            audio,
            StringComparison.Ordinal);

        // ...and they must reach the fields THROUGH the curve, not raw.
        Assert.Contains(
            "_soundOptionMix =\r\n        Level100AudioCatalog.ToRetailOptionMix(RetailSoundOptionValue)"
                .Replace("\r\n", "\n", StringComparison.Ordinal),
            audio.Replace("\r\n", "\n", StringComparison.Ordinal),
            StringComparison.Ordinal);
        Assert.Contains(
            "_musicOptionMix =\r\n        Level100AudioCatalog.ToRetailOptionMix(RetailMusicOptionValue)"
                .Replace("\r\n", "\n", StringComparison.Ordinal),
            audio.Replace("\r\n", "\n", StringComparison.Ordinal),
            StringComparison.Ordinal);

        // The exact defect that shipped: the option value written straight in.
        Assert.DoesNotContain(
            "_soundOptionMix = 0.8f", audio, StringComparison.Ordinal);
        Assert.DoesNotContain(
            "_musicOptionMix = 0.9f", audio, StringComparison.Ordinal);

        // And the curve must actually attenuate less than the raw value would,
        // by the measured amount. This is the half that cannot be satisfied by
        // renaming things.
        float soundMix = Level100AudioCatalog.ToRetailOptionMix(retailSoundOption);
        float musicMix = Level100AudioCatalog.ToRetailOptionMix(retailMusicOption);

        Assert.Equal(0.9453f, soundMix, 4);
        Assert.Equal(0.9732f, musicMix, 4);

        double soundDecibelsQuieterIfRaw =
            20d * Math.Log10(soundMix / retailSoundOption);
        double musicDecibelsQuieterIfRaw =
            20d * Math.Log10(musicMix / retailMusicOption);

        Assert.Equal(1.45d, soundDecibelsQuieterIfRaw, 2);
        Assert.Equal(0.68d, musicDecibelsQuieterIfRaw, 2);
    }

    // Every Level 100 mix level is reproduced from two released facts rather
    // than chosen: the integer volume/pitch fields of the matching
    // data/sounds/sounds.sfx record (version 103, 170 records), and
    // CSoundManager::PlayEffect's `volume = (volume * effect->mVolume) / 100`
    // with the call site's caller volume. Caller volumes are the released
    // constants DEFAULT_SOUND_VOLUME 0.7f, mHUDMessageVolume 0.45f, and
    // ENGINE_VOLUME 1.0f as passed by the Battle Engine call sites.
    //
    // This is the regression fence for the standing rule that no mix level may
    // be guessed. Any recipe volume that stops being caller x record/100, or
    // any pitch variance that stops being the record's own field, fails here.
    private const float CallerDefault = 0.70f;
    private const float CallerHudMessage = 0.45f;
    private const float CallerEngine = 1.00f;
    // NOT a released named constant: the literal 0x3f000000 pushed into
    // PlayEffect's volume slot by the weapon-launch body
    // ProjectileBurst__SpawnFromCurrentPreset (0x005069f0) in the pristine
    // specimen. See Level100AudioCatalog.RetailWeaponLaunchVolume for the
    // disassembly. The two player weapon-fire cues below carried CallerDefault
    // until 2026-07-27; that was an assumption, and the bytes refute it.
    private const float CallerWeaponLaunch = 0.50f;

    public static TheoryData<Level100AudioCueRecipe, int, int, int, float>
        RetailSfxRecords => new()
    {
        { Level100AudioCatalog.GetFrontend("Back"), 43, 52, 0, CallerDefault },
        { Level100AudioCatalog.GetFrontend("Move"), 44, 49, 0, CallerDefault },
        { Level100AudioCatalog.GetFrontend("Select"), 45, 52, 0, CallerDefault },
        { Effect(Level100EffectCue.AquilaStrafe), 21, 80, 10, CallerEngine },
        { Effect(Level100EffectCue.AquilaHydraulics), 32, 40, 0, CallerHudMessage },
        { Effect(Level100EffectCue.AquilaIncomingMissile), 33, 80, 5, CallerHudMessage },
        { Effect(Level100EffectCue.AquilaTargetLocked), 30, 80, 0, CallerHudMessage },
        { Effect(Level100EffectCue.AquilaTargetAcquired), 31, 80, 0, CallerHudMessage },
        { Effect(Level100EffectCue.PulseCannonFire), 37, 65, 5, CallerWeaponLaunch },
        { Effect(Level100EffectCue.VulcanCannonFire), 42, 75, 7, CallerWeaponLaunch },
        // NOT corrected to CallerWeaponLaunch, and that is a deliberate stop
        // rather than an oversight. Both are silent - neither has a producer -
        // and neither has been shown to reach 0x005069f0. Micro Missiles are a
        // separate player weapon whose launcher path was not traced, and the
        // Drone Vulcan is an actor weapon with its own evidence item. If either
        // is later shown to launch through that body, its caller is 0.5f too.
        { Effect(Level100EffectCue.MicroMissileFire), 34, 80, 15, CallerDefault },
        { Effect(Level100EffectCue.DroneVulcanFire), 155, 60, 10, CallerDefault },
        { Effect(Level100EffectCue.PulseImpact), 108, 70, 20, CallerDefault },
        { Effect(Level100EffectCue.MissileImpact), 104, 70, 30, CallerDefault },
        { Effect(Level100EffectCue.FacilityDestroyed), 105, 70, 30, CallerDefault },
        { Effect(Level100EffectCue.AquilaDestroyed), 109, 70, 30, CallerDefault },
        { Effect(Level100EffectCue.TransportDestroyed), 96, 70, 30, CallerDefault },
        { Effect(Level100EffectCue.ComponentDebrisDestroyed), 95, 70, 30, CallerDefault },
        { Effect(Level100EffectCue.LargeDebrisDestroyed), 97, 70, 30, CallerDefault },
        { Effect(Level100EffectCue.HugeGroundDebrisDestroyed), 110, 70, 30, CallerDefault },
        { Effect(Level100EffectCue.RepairCharging), 7, 80, 0, CallerDefault },
        { Effect(Level100EffectCue.RepairFull), 8, 80, 0, CallerDefault },
        { Loop(Level100ActorLoopCue.RepairPadIdle), 9, 50, 0, CallerDefault },
        { Loop(Level100ActorLoopCue.AirTrainer), 121, 45, 15, CallerDefault },
        { Loop(Level100ActorLoopCue.Transport), 129, 40, 15, CallerDefault },
        { Transition(AquilaTransitionCue.Takeoff), 26, 40, 0, CallerEngine },
        { Transition(AquilaTransitionCue.InFlight), 24, 50, 0, CallerEngine },
        { Transition(AquilaTransitionCue.Landing), 25, 40, 0, CallerEngine },
        { Warning(AquilaWarningAudioState.EnergyLow), 23, 70, 0, CallerEngine },
        { Warning(AquilaWarningAudioState.HullCritical), 22, 70, 0, CallerEngine },
        { Terminal(Level100TerminalCue.AmmunitionDepleted), 46, 100, 0, CallerHudMessage },
        { Terminal(Level100TerminalCue.ArmourLow), 48, 100, 0, CallerHudMessage },
        { Terminal(Level100TerminalCue.EnergyLow), 53, 100, 0, CallerHudMessage },
        { Terminal(Level100TerminalCue.HostileEnvironment), 57, 100, 0, CallerHudMessage },
        { Terminal(Level100TerminalCue.IncomingMissile), 58, 100, 0, CallerHudMessage },
        { Terminal(Level100TerminalCue.IncomingWarhead), 59, 100, 0, CallerHudMessage },
        { Terminal(Level100TerminalCue.MicroMissilesSelected), 60, 100, 0, CallerHudMessage },
        { Terminal(Level100TerminalCue.PulseCannonSelected), 62, 100, 0, CallerHudMessage },
        { Terminal(Level100TerminalCue.VulcanCannonSelected), 72, 100, 0, CallerHudMessage },
        { Terminal(Level100TerminalCue.WeaponOverheating), 75, 100, 0, CallerHudMessage },
    };

    [Theory]
    [MemberData(nameof(RetailSfxRecords))]
    public void EveryMixLevelIsTheReleasedPlayEffectProductOfItsSfxRecord(
        Level100AudioCueRecipe recipe,
        int expectedRecord,
        int recordVolume,
        int recordPitchVariance,
        float callerVolume)
    {
        Assert.Equal(expectedRecord, recipe.RetailSoundRecord);
        Assert.Equal(recordPitchVariance, recipe.PitchVariancePercent);
        Assert.Equal(
            callerVolume * recordVolume / 100f,
            recipe.LinearVolume,
            5);
    }

    // mRadioMessageVolume is 0.42f on the PC branch of CSoundManager::Init and
    // 0.70f only on PS2; mHUDMessageVolume is 0.45f on both.
    [Fact]
    public void MessageVolumeConstantsAreTheReleasedPcBranchValues()
    {
        Assert.Equal(0.42f, Level100AudioCatalog.RetailRadioMessageVolume);
        Assert.Equal(0.45f, Level100AudioCatalog.RetailHudMessageVolume);
        Assert.Equal(0.70f, Level100AudioCatalog.RetailDefaultEffectVolume);
    }

    // CSoundManager::SetMasterVolume's non-PS2 branch is
    // mMasterVolume = 1 - tan((1 - val) * 1.38f) / tan(1.38f).
    [Theory]
    [InlineData(0.25f)]
    [InlineData(0.5f)]
    [InlineData(0.75f)]
    public void AudioOptionCurveMatchesTheReleasedTangentLaw(float optionValue)
    {
        float expected = 1f -
            (MathF.Tan((1f - optionValue) * 1.38f) / MathF.Tan(1.38f));

        Assert.Equal(
            expected,
            Level100AudioCatalog.ToRetailOptionMix(optionValue),
            5);
    }

    private static Level100AudioCueRecipe Effect(Level100EffectCue cue) =>
        Level100AudioCatalog.GetEffect(cue);

    private static Level100AudioCueRecipe Loop(Level100ActorLoopCue cue) =>
        Level100AudioCatalog.GetActorLoop(cue);

    private static Level100AudioCueRecipe Terminal(Level100TerminalCue cue) =>
        Level100AudioCatalog.GetTerminal(cue);

    private static Level100AudioCueRecipe Transition(AquilaTransitionCue cue) =>
        Level100AudioCatalog.GetAquilaTransition(cue);

    private static Level100AudioCueRecipe Warning(AquilaWarningAudioState state) =>
        Level100AudioCatalog.GetAquilaWarning(state);
}
