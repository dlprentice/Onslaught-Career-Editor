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
    public void CharacterMessageVoiceStartsAfterTheReleasedActivationLead()
    {
        string audio = ReadGodotSource("Level100Audio.cs");
        Assert.Contains(
            "RetailCharacterMessageVoiceLeadSeconds = 0.2d;",
            audio,
            StringComparison.Ordinal);
        Assert.Contains(
            "RetailCharacterMessageHandoffSeconds = 0.3d;",
            audio,
            StringComparison.Ordinal);

        int processStart = audio.IndexOf(
            "public override void _Process(double delta)",
            StringComparison.Ordinal);
        int processEnd = audio.IndexOf(
            "public void StartTutorialMusic()",
            processStart,
            StringComparison.Ordinal);
        string process = audio[processStart..processEnd];
        AssertOccursInOrder(
            process,
            "if (_gameplayPaused)",
            "_characterMessageVoiceLeadSecondsRemaining -= delta;",
            "if (_characterMessageVoiceLeadSecondsRemaining <= 0d)",
            "_characterMessageVoiceLeadSecondsRemaining = 0d;",
            "StartNextCharacterMessage();");
        Assert.Equal(1, CountOccurrences(process, "StartNextCharacterMessage();"));
        AssertOccursInOrder(
            process,
            "_characterMessageHandoffSecondsRemaining -= delta;",
            "if (_characterMessageHandoffSecondsRemaining <= 0d)",
            "_characterMessageHandoffSecondsRemaining = 0d;",
            "_characterMessageVoiceLeadSecondsRemaining =",
            "RetailCharacterMessageVoiceLeadSeconds;");

        int queueStart = audio.IndexOf(
            "public void QueueCharacterMessage(int speakerId, int messageId)",
            StringComparison.Ordinal);
        int queueEnd = audio.IndexOf(
            "public void StopCharacterMessages()",
            queueStart,
            StringComparison.Ordinal);
        string queue = audio[queueStart..queueEnd];
        AssertOccursInOrder(
            queue,
            "_characterMessageVoiceLeadSecondsRemaining =",
            "RetailCharacterMessageVoiceLeadSeconds;");
        Assert.DoesNotContain("StartNextCharacterMessage();", queue, StringComparison.Ordinal);

        string stop = audio[queueEnd..audio.IndexOf(
            "public void SetMasterSoundOption(float optionValue)",
            queueEnd,
            StringComparison.Ordinal)];
        Assert.Contains(
            "_characterMessageVoiceLeadSecondsRemaining = 0d;",
            stop,
            StringComparison.Ordinal);
        Assert.Contains(
            "_characterMessageVoiceLeadSecondsRemaining = 0d;",
            MethodBody(audio, "private void StartNextCharacterMessage()"),
            StringComparison.Ordinal);
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
        string frontend = ReadGodotSource("RetailFrontendFlow.cs");
        string materializer = ReadGodotSource("materialize_retail_assets.py");

        Assert.Contains(music.RetailSourceName, materializer, StringComparison.Ordinal);
        Assert.Contains(
            "LoadOgg(recipe.ResourcePath, looping: true)",
            audio,
            StringComparison.Ordinal);
        string ready = MethodBody(game, "public override void _Ready()");
        string startupComplete = MethodBody(
            game,
            "private void StartFrontendMusicAfterStartupMedia()");
        string stopForLevel = MethodBody(
            game,
            "private void StopFrontendMusicForLevelEntry()");
        string navigation = MethodBody(
            frontend,
            "private void HandleNavigationSignal(RetailFrontendSignal signal)");
        string activateGameplay = MethodBody(
            game,
            "private void ActivateFrontendGameplay()");

        Assert.DoesNotContain("_audio.StartFrontendMusic();", ready, StringComparison.Ordinal);
        Assert.Contains(
            "_audio.StartFrontendMusic();",
            startupComplete,
            StringComparison.Ordinal);
        Assert.Contains(
            "_frontend.Level100LoadingStarted += StopFrontendMusicForLevelEntry;",
            ready,
            StringComparison.Ordinal);
        Assert.Contains(
            "Level100LoadingStarted?.Invoke();",
            navigation,
            StringComparison.Ordinal);
        Assert.Contains("_audio.StopFrontendMusic();", stopForLevel, StringComparison.Ordinal);
        AssertOccursInOrder(
            activateGameplay,
            "_audio.StartTutorialMusic();",
            "_gameplayActive = true;");
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

    private static string MethodBody(string source, string declaration)
    {
        int start = source.IndexOf(declaration, StringComparison.Ordinal);
        Assert.True(start >= 0, $"Expected method declaration '{declaration}'.");
        int next = source.IndexOf("\n    private ", start + declaration.Length, StringComparison.Ordinal);
        if (next < 0)
        {
            next = source.IndexOf("\n    public ", start + declaration.Length, StringComparison.Ordinal);
        }
        return next < 0 ? source[start..] : source[start..next];
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

    // ==================================================================
    // The three released audio laws recovered on 2026-07-27.
    // See local-lab/AUDIO-PARITY-LAWS-2026-07-27.md.
    // ==================================================================

    /// <summary>ToRetailOptionMix(0.8f), retail's cold-start sound option.</summary>
    private const float ColdStartSoundMix = 0.945312f;

    // LAW 1. CSoundManager::Fade, references/Onslaught/SoundManager.cpp:760-793.
    //
    //   tv = SINT(float(v) * mMasterVolume * mSubVolume * MASTER * GAME);
    //   tv = tv * 200;  if (tv > 10000) tv = 10000;
    //   tv = ((tv - 10000)/2);  if (tv < -10000) tv = -10000;
    //
    // The three properties Mathf.LinearToDb did not have, each pinned below:
    // a saturation PLATEAU at the top, a map that is linear IN DECIBELS below
    // the knee, and a floor that is not silence.
    [Fact]
    public void ReleasedFadeLaw_SaturatesAtTheKneeAndFloorsAtMinusFiftyDecibels()
    {
        // (a) The plateau. A tracked event's source volume is 100, so any
        // combined multiplier at or above 0.5 gives tv >= 50, tv*200 >= 10000,
        // and the cap makes the millibel result exactly zero.
        foreach (float multiplier in new[] { 0.5f, 0.6f, 0.75f, 1f })
        {
            Assert.Equal(
                0,
                Level100AudioCatalog.RetailFadeMillibels(100, multiplier, 1f, 1f, 1f));
        }

        // The step immediately below the knee is one integer of tv, i.e. one
        // whole decibel. That quantisation is the source's own SINT truncation.
        Assert.Equal(
            -100,
            Level100AudioCatalog.RetailFadeMillibels(100, 0.499f, 1f, 1f, 1f));
        Assert.Equal(
            -200,
            Level100AudioCatalog.RetailFadeMillibels(100, 0.489f, 1f, 1f, 1f));

        // (b) An untracked event's source volume is 127
        // (SoundManager.cpp:526), so its knee is at 50/127 = 0.3937, not 0.5.
        Assert.Equal(
            0,
            Level100AudioCatalog.RetailFadeMillibels(127, 0.394f, 1f, 1f, 1f));
        Assert.NotEqual(
            0,
            Level100AudioCatalog.RetailFadeMillibels(127, 0.39f, 1f, 1f, 1f));

        // (c) The floor is -5000 mB, and the tv < -10000 clamp in the source is
        // unreachable for any v <= 127.
        Assert.Equal(
            -5_000,
            Level100AudioCatalog.RetailFadeMillibels(0, 1f, 1f, 1f, 1f));
        Assert.Equal(
            -5_000,
            Level100AudioCatalog.RetailFadeMillibels(100, 0f, 1f, 1f, 1f));
    }

    // The PC-only second stage, references/Onslaught/pcsoundmanager.cpp:405-410,
    // under the developer's comment "Ensure we actually fall off to silence".
    // It does not reach silence: Fade's -5000 floor shapes to -70 dB.
    [Theory]
    [InlineData(0, 0)]
    [InlineData(-3_900, -3_900)]
    [InlineData(-4_000, -4_000)]
    [InlineData(-4_100, -4_300)]
    [InlineData(-4_600, -5_800)]
    [InlineData(-5_000, -7_000)]
    public void ReleasedPcShaping_TriplesTheSlopeBelowMinusFortyDecibels(
        int fadeMillibels,
        int expectedShaped)
    {
        Assert.Equal(
            expectedShaped,
            Level100AudioCatalog.RetailPcShapedMillibels(fadeMillibels));
    }

    // The player-visible half of law 1: the RELATIVE balance of the two loudest
    // things in Level 100's flight segment. Retail puts the jet engine 17 dB
    // above the Pulse Cannon report. Mathf.LinearToDb put them 3.7 dB apart
    // (-6.51 vs -10.25), so the weapon dominated a mix retail has the engine
    // dominate. Both cues sit on the listener, so both take source volume 100.
    [Fact]
    public void ReleasedFadeLaw_KeepsTheJetEngineAboveTheWeaponReport()
    {
        float engine = Level100AudioCatalog
            .GetAquilaTransition(AquilaTransitionCue.InFlight).LinearVolume;
        float weapon = Level100AudioCatalog
            .GetEffect(Level100EffectCue.PulseCannonFire).LinearVolume;

        float engineDb = Level100AudioCatalog.RetailVolumeDb(
            Level100AudioCatalog.RetailListenerSourceVolume,
            engine,
            Level100AudioCatalog.RetailUnfadedSubVolume,
            ColdStartSoundMix,
            1f);
        float weaponDb = Level100AudioCatalog.RetailVolumeDb(
            Level100AudioCatalog.RetailListenerSourceVolume,
            weapon,
            Level100AudioCatalog.RetailUnfadedSubVolume,
            ColdStartSoundMix,
            1f);

        Assert.Equal(-3.0f, engineDb, 3);
        Assert.Equal(-20.0f, weaponDb, 3);
        Assert.Equal(17.0f, engineDb - weaponDb, 3);
    }

    [Fact]
    public void AquilaFlightLoopFade_UsesTheReleasedSignedStepAndAdapterPath()
    {
        float fadeIn = 0f;
        float fadeOut = 1f;
        bool fadeInComplete = false;
        bool fadeOutComplete = false;
        for (int update = 0; update < 50; update++)
        {
            fadeIn = Level100AudioCatalog.AdvanceRetailFlightLoopSubVolume(
                fadeIn,
                1f,
                Level100AudioCatalog.RetailFlightLoopFadeStep,
                out fadeInComplete);
            fadeOut = Level100AudioCatalog.AdvanceRetailFlightLoopSubVolume(
                fadeOut,
                0f,
                -Level100AudioCatalog.RetailFlightLoopFadeStep,
                out fadeOutComplete);
            Assert.False(fadeInComplete);
            Assert.False(fadeOutComplete);
        }

        Assert.True(fadeIn < 1f);
        Assert.True(fadeOut > 0f);
        fadeIn = Level100AudioCatalog.AdvanceRetailFlightLoopSubVolume(
            fadeIn,
            1f,
            Level100AudioCatalog.RetailFlightLoopFadeStep,
            out fadeInComplete);
        fadeOut = Level100AudioCatalog.AdvanceRetailFlightLoopSubVolume(
            fadeOut,
            0f,
            -Level100AudioCatalog.RetailFlightLoopFadeStep,
            out fadeOutComplete);
        Assert.True(fadeInComplete);
        Assert.True(fadeOutComplete);
        Assert.Equal(1f, fadeIn);
        Assert.Equal(0f, fadeOut);

        float reversed = 0f;
        for (int update = 0; update < 10; update++)
        {
            reversed = Level100AudioCatalog.AdvanceRetailFlightLoopSubVolume(
                reversed,
                1f,
                Level100AudioCatalog.RetailFlightLoopFadeStep,
                out bool crossed);
            Assert.False(crossed);
        }
        for (int update = 0; update < 10; update++)
        {
            reversed = Level100AudioCatalog.AdvanceRetailFlightLoopSubVolume(
                reversed,
                0f,
                -Level100AudioCatalog.RetailFlightLoopFadeStep,
                out bool crossed);
            Assert.False(crossed);
        }
        Assert.Equal(0f, reversed);
        reversed = Level100AudioCatalog.AdvanceRetailFlightLoopSubVolume(
            reversed,
            0f,
            -Level100AudioCatalog.RetailFlightLoopFadeStep,
            out bool reversalComplete);
        Assert.True(reversalComplete);
        Assert.Equal(0f, reversed);

        string audio = ReadGodotSource("Level100Audio.cs");
        Assert.Contains(
            "AdvanceAquilaFlightLoopFade(delta);",
            audio,
            StringComparison.Ordinal);
        Assert.Contains("initialSubVolume: 0f", audio, StringComparison.Ordinal);
        Assert.Equal(2, CountOccurrences(audio, "FadeOutAquilaFlightLoop();"));
        Assert.Contains(
            "ReferenceEquals(player, _aquilaFlightLoop)",
            audio,
            StringComparison.Ordinal);
    }

    // LAW 2. CSoundManager::GetVolumeForPos,
    // references/Onslaught/SoundManager.cpp:437-442, with FAR_SOUND 50 from
    // references/Onslaught/SoundManager.h:21. Linear from 100 at the listener
    // to 0 at 50 units, and flat at 0 beyond. This replaces an invented Godot
    // inverse-distance model with MaxDistance 80 / UnitSize 8, neither of which
    // appears anywhere in the source.
    [Theory]
    [InlineData(0f, 100)]
    [InlineData(4f, 92)]
    [InlineData(8f, 84)]
    [InlineData(20f, 60)]
    [InlineData(25f, 50)]
    [InlineData(45f, 10)]
    [InlineData(50f, 0)]
    [InlineData(80f, 0)]
    public void ReleasedSpatialAttenuation_IsLinearToZeroAtFiftyUnits(
        float distanceUnits,
        int expectedSourceVolume)
    {
        Assert.Equal(50f, Level100AudioCatalog.RetailFarSoundUnits);
        Assert.Equal(
            expectedSourceVolume,
            Level100AudioCatalog.RetailSourceVolumeForDistance(distanceUnits));
    }

    // The "SRG early out", references/Onslaught/SoundManager.cpp:519-524. A
    // NON-LOOPING event at or beyond FAR_SOUND is deleted and never plays;
    // looping events are exempt by the `!event->mLooping` test at :520.
    [Fact]
    public void ReleasedSpatialAttenuation_RefusesANonLoopingStartBeyondFarSound()
    {
        Assert.False(Level100AudioCatalog.RetailRefusesNonLoopingStart(49.99f));
        Assert.True(Level100AudioCatalog.RetailRefusesNonLoopingStart(50f));
        Assert.True(Level100AudioCatalog.RetailRefusesNonLoopingStart(80f));
    }

    // The player-visible half of law 2, using the same Pulse impact cue the
    // divergence audit worked through (LinearVolume 0.49 = 0.7 caller x record
    // 70/100) at unity mix so the numbers are directly comparable. The old
    // inverse-distance model gave roughly -14 dB at 20 units and -21 dB at 45;
    // it was 37 dB too loud at the far end and kept playing out to 80 units.
    [Theory]
    [InlineData(20f, -21.0f)]
    [InlineData(45f, -58.0f)]
    public void ReleasedSpatialAttenuation_PutsTheImpactCueAtTheReleasedLevel(
        float distanceUnits,
        float expectedDb)
    {
        float impact = Level100AudioCatalog
            .GetEffect(Level100EffectCue.PulseImpact).LinearVolume;
        Assert.Equal(0.49f, impact, 5);

        Assert.Equal(
            expectedDb,
            Level100AudioCatalog.RetailVolumeDb(
                Level100AudioCatalog.RetailSourceVolumeForDistance(distanceUnits),
                impact,
                Level100AudioCatalog.RetailUnfadedSubVolume,
                1f,
                1f),
            3);
    }

    // LAW 3. references/Onslaught/pcsoundmanager.cpp:398-401. The clamp runs
    // immediately before the single SetFrequency call, on PlaySound and on every
    // later update, and BOTH producers only ever emit values at or above 1.0 -
    // PlayEffect's 1 + (rand() % variance)/100 (SoundManager.cpp:1188-1196) and
    // the jet's 1 + thruster*0.25 (BattleEngine.cpp:1541). Retail PC therefore
    // plays every sample at a constant 44000 Hz.
    [Fact]
    public void ReleasedPcPitchClamp_MakesEveryLevel100CueConstantPitch()
    {
        // The jet at full throttle, which used to raise the engine loop by a
        // musical third.
        Assert.Equal(1f, Level100AudioCatalog.RetailPcPitchMultiplier(1.25f));

        // Every pitch variance the Level 100 catalog actually carries, at its
        // loudest possible random draw.
        foreach (Level100AudioCueRecipe recipe in AllCatalogRecipes())
        {
            float worstCaseProducer = recipe.PitchVariancePercent == 0
                ? 1f
                : 1f + ((recipe.PitchVariancePercent - 1) / 100f);
            Assert.Equal(
                1f,
                Level100AudioCatalog.RetailPcPitchMultiplier(worstCaseProducer));
        }

        // The clamp is one-sided: it is a ceiling, not a pin. Nothing in the
        // Level 100 catalog reaches this branch, but the source's `>` is the
        // whole condition and a two-sided clamp would be a different law.
        Assert.Equal(0.5f, Level100AudioCatalog.RetailPcPitchMultiplier(0.5f));
    }

    // The adapter half of all three laws. Level100Audio.cs is Godot-typed and
    // cannot be compiled into this project, so it is asserted as source text -
    // the same technique ColdStartOptionMixes_PushRetailOptionValuesThroughTheCurve
    // already uses on the same file.
    [Fact]
    public void Level100Audio_AppliesTheThreeReleasedLawsAndNotTheInventedOnes()
    {
        string audio = ReadGodotSource("Level100Audio.cs");

        // Law 1: the linear->dB conversion is gone from the SOUND path. The one
        // surviving use is music, which is CMusic and never passes through
        // CSoundManager::Fade at all.
        Assert.Equal(1, CountOccurrences(audio, "Mathf.LinearToDb("));
        Assert.Contains(
            "Mathf.LinearToDb(_musicOptionMix)",
            audio,
            StringComparison.Ordinal);
        Assert.Contains(
            "Level100AudioCatalog.RetailVolumeDb(",
            audio,
            StringComparison.Ordinal);

        // Law 2: the invented distances are gone, Godot's model is off, and the
        // released early-out and per-update tracking are present.
        Assert.DoesNotContain("MaxDistance = 80f", audio, StringComparison.Ordinal);
        Assert.DoesNotContain("UnitSize = 8f", audio, StringComparison.Ordinal);
        Assert.Contains(
            "AttenuationModel = AudioStreamPlayer3D.AttenuationModelEnum.Disabled",
            audio,
            StringComparison.Ordinal);
        Assert.Contains(
            "Level100AudioCatalog.RetailRefusesNonLoopingStart(distanceUnits)",
            audio,
            StringComparison.Ordinal);
        Assert.Contains(
            "UpdateSpatialAttenuation();",
            audio,
            StringComparison.Ordinal);

        // Law 3: both producers reach the buffer through the PC clamp, and
        // neither assigns a raw PitchScale any more.
        Assert.DoesNotContain(
            "PitchScale = 1f + (thrusterFraction * 0.25f)",
            audio,
            StringComparison.Ordinal);
        Assert.Equal(
            2,
            CountOccurrences(audio, "Level100AudioCatalog.RetailPcPitchMultiplier("));
    }

    private static int CountOccurrences(string source, string value)
    {
        int count = 0;
        int cursor = 0;
        while (true)
        {
            int found = source.IndexOf(value, cursor, StringComparison.Ordinal);
            if (found < 0)
            {
                return count;
            }
            count++;
            cursor = found + value.Length;
        }
    }

    private static IEnumerable<Level100AudioCueRecipe> AllCatalogRecipes()
    {
        foreach (Level100EffectCue cue in Enum.GetValues<Level100EffectCue>())
        {
            yield return Level100AudioCatalog.GetEffect(cue);
        }
        foreach (Level100TerminalCue cue in Enum.GetValues<Level100TerminalCue>())
        {
            yield return Level100AudioCatalog.GetTerminal(cue);
        }
        foreach (Level100ActorLoopCue cue in Enum.GetValues<Level100ActorLoopCue>())
        {
            yield return Level100AudioCatalog.GetActorLoop(cue);
        }
        foreach (AquilaTransitionCue cue in Enum.GetValues<AquilaTransitionCue>())
        {
            yield return Level100AudioCatalog.GetAquilaTransition(cue);
        }
        yield return Level100AudioCatalog.GetAquilaWarning(
            AquilaWarningAudioState.EnergyLow);
        yield return Level100AudioCatalog.GetAquilaWarning(
            AquilaWarningAudioState.HullCritical);
        foreach (string cueName in new[] { "Back", "Move", "Select" })
        {
            yield return Level100AudioCatalog.GetFrontend(cueName);
        }
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
