// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
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
        string audio = ReadAudioSource("level100_audio.gd");
        Assert.Contains("CHARACTER_VOICE_LEAD_SECONDS: float = 0.2", audio, StringComparison.Ordinal);
        Assert.Contains("CHARACTER_HANDOFF_SECONDS: float = 0.3", audio, StringComparison.Ordinal);
        string advance = GdMethodBody(audio, "advance");
        AssertOccursInOrder(advance,
            "_advance_music(delta)", "if not result.ok or _paused:",
            "if _voice_lead > 0.0:", "_voice_lead -= delta", "if _voice_lead <= 0.0:",
            "_voice_lead = 0.0", "return _start_next_message()");
        Assert.Equal(1, CountOccurrences(advance, "_start_next_message()"));
        AssertOccursInOrder(advance,
            "_handoff -= delta", "if _handoff <= 0.0:", "_handoff = 0.0",
            "_voice_lead = CHARACTER_VOICE_LEAD_SECONDS");
        string queue = GdMethodBody(audio, "queue_character_message");
        AssertOccursInOrder(queue,
            "_queue.enqueue(speaker_id, message_id)",
            "not _voice.playing and _handoff <= 0.0 and _voice_lead <= 0.0",
            "_voice_lead = CHARACTER_VOICE_LEAD_SECONDS");
        Assert.DoesNotContain("_start_next_message()", queue, StringComparison.Ordinal);
        Assert.Contains("_voice_lead = 0.0", GdMethodBody(audio, "stop_character_messages"), StringComparison.Ordinal);
        AssertOccursInOrder(GdMethodBody(audio, "_start_next_message"),
            "_voice_lead = 0.0", "_queue.try_dequeue()", "_voice.play()", "_observer.call(_voice)");
        AssertOccursInOrder(GdMethodBody(audio, "_begin_handoff"),
            "_active_message = null", "_queue.count() > 0", "_handoff = CHARACTER_HANDOFF_SECONDS");
    }

    [Fact]
    public void AquilaWarningLoopsFollowTheReleasedHullFirstThresholdLaw()
    {
        // Core facts cross once; the native scene owns the active loop and fade.
        string bridge = ReadGodotSource("Level100Audio.cs");
        string facts = MethodBody(bridge, "private static D FrameFacts(FrameAdvanceResult frame)");
        Assert.Contains(
            $"snapshot.Hull < 7_000 ? {(int)AquilaWarningAudioState.HullCritical} : " +
            $"snapshot.Energy < 2_000 ? {(int)AquilaWarningAudioState.EnergyLow} : {(int)AquilaWarningAudioState.Normal}",
            facts, StringComparison.Ordinal);
        Assert.DoesNotContain("Hull <= 7_000", bridge, StringComparison.Ordinal);
        Assert.DoesNotContain("Energy <= 2_000", bridge, StringComparison.Ordinal);
        Assert.True(Level100AudioCatalog.GetAquilaWarning(AquilaWarningAudioState.EnergyLow).Looping);
        Assert.True(Level100AudioCatalog.GetAquilaWarning(AquilaWarningAudioState.HullCritical).Looping);

        string audio = ReadAudioSource("level100_audio.gd");
        string consume = GdMethodBody(audio, "consume_frame");
        AssertOccursInOrder(consume,
            "update_aquila_pose(facts.actors)", "set_aquila_warning_state(facts.warning_state)");
        Assert.Equal(1, CountOccurrences(consume, "set_aquila_warning_state("));
        string warning = GdMethodBody(audio, "set_aquila_warning_state");
        AssertOccursInOrder(warning,
            "if state == 0:", "_fades.warning.target = 0.0",
            "_fades.warning.step = -F32.read_word(Catalog.RETAIL_FLIGHT_LOOP_FADE_STEP_WORD)",
            "if _loop_playing(\"warning\") and _warning_loop_state == state:",
            "return _ok()", "_stop_warning_loop()", "_set_loop(\"warning\"", "_warning_loop_state = state");
        Assert.Equal(1, CountOccurrences(warning, "_stop_warning_loop()"));
        Assert.Contains("_warning_loop_state = 0", GdMethodBody(audio, "_stop_warning_loop"), StringComparison.Ordinal);
        string fade = GdMethodBody(audio, "_advance_fade");
        AssertOccursInOrder(fade,
            "fade.accumulator >= SOUND_UPDATE_SECONDS",
            "Catalog.advance_retail_flight_loop_sub_volume(fade.sub, fade.target, fade.step)",
            "if result.crossed_target:", "if fade.target == 0.0:", "_stop_warning_loop()");
        Assert.Contains("for key: String in [\"flight\", \"warning\"]", GdMethodBody(audio, "advance"), StringComparison.Ordinal);
        Assert.Contains("_live_loops.get(\"warning\") == player", GdMethodBody(audio, "_update_spatial_attenuation"), StringComparison.Ordinal);
    }

    [Fact]
    public void WalkerMovementEventsUseTheReleasedAquilaCues()
    {
        Level100AudioCueRecipe hydraulics = Level100AudioCatalog.GetEffect(
            Level100EffectCue.AquilaHydraulics);
        Assert.Equal(
            "res://Assets/Aquila/SoundEffects/hydraulics.wav",
            hydraulics.ResourcePath);
        Assert.False(hydraulics.Looping);
        Level100AudioCueRecipe dash = Level100AudioCatalog.GetEffect(
            Level100EffectCue.AquilaStrafe);
        Assert.Equal("res://Assets/Aquila/SoundEffects/strafe.wav", dash.ResourcePath);
        Assert.False(dash.Looping);

        string consume = GdMethodBody(ReadAudioSource("level100_audio.gd"), "consume_aquila_flight_events");
        Assert.Contains($"{(int)AquilaFlightEvents.WalkerHydraulicsRequested}: result = play_on_aquila(Catalog.EffectCue.AQUILA_HYDRAULICS)", consume, StringComparison.Ordinal);
        Assert.Contains($"{(int)AquilaFlightEvents.WalkerDashRequested}: result = play_on_aquila(Catalog.EffectCue.AQUILA_STRAFE)", consume, StringComparison.Ordinal);
    }

    [Fact]
    public void WaterSkimUsesTheReleasedStrictHostileEnvironmentQuietGap()
    {
        Assert.Equal(100, Level100AudioCatalog.RetailHostileEnvironmentQuietTicks);

        int firstContact = 0;
        Assert.False(Level100AudioCatalog.ObserveHostileEnvironmentContact(
            100,
            ref firstContact));
        Assert.Equal(100, firstContact);

        firstContact = 0;
        Assert.True(Level100AudioCatalog.ObserveHostileEnvironmentContact(
            101,
            ref firstContact));
        Assert.Equal(101, firstContact);

        // Every contact restamps the gate. A continuous contact suppresses,
        // an exactly-five-second gap still suppresses and restamps, and only
        // the following 101-tick quiet gap clears.
        Assert.False(Level100AudioCatalog.ObserveHostileEnvironmentContact(
            102,
            ref firstContact));
        Assert.False(Level100AudioCatalog.ObserveHostileEnvironmentContact(
            202,
            ref firstContact));
        Assert.Equal(202, firstContact);
        Assert.True(Level100AudioCatalog.ObserveHostileEnvironmentContact(
            303,
            ref firstContact));

        Level100AudioCueRecipe cue = Level100AudioCatalog.GetTerminal(
            Level100TerminalCue.HostileEnvironment);
        Assert.Equal(57, cue.RetailSoundRecord);
        Assert.Equal(
            "res://Assets/Level100/SoundEffects/terminal-hostile-environment.wav",
            cue.ResourcePath);
        Assert.False(cue.Looping);

        string audio = ReadAudioSource("level100_audio.gd");
        string consume = GdMethodBody(audio, "consume_aquila_flight_events");
        AssertOccursInOrder(consume,
            "var start: int = simulation_tick - mission_tick", "_last_hostile_contact = start",
            $"{(int)AquilaFlightEvents.WaterSkim}:", "Catalog.observe_hostile_environment_contact(event.tick, _last_hostile_contact)",
            "_last_hostile_contact = result.previous_contact_tick", "if result.value:",
            "play_terminal_cue(Catalog.TerminalCue.HOSTILE_ENVIRONMENT)");
        AssertOccursInOrder(GdMethodBody(audio, "stop_gameplay_samples"),
            "_mission_start_tick = null", "_last_hostile_contact = 0");
        Assert.Contains("consume_aquila_flight_events(facts.flight_events, facts.simulation_tick, facts.mission_tick)",
            GdMethodBody(audio, "consume_frame"), StringComparison.Ordinal);
        string facts = MethodBody(ReadGodotSource("Level100Audio.cs"), "private static D FrameFacts(FrameAdvanceResult frame)");
        Assert.Contains("[\"simulation_tick\"] = snapshot.Tick", facts, StringComparison.Ordinal);
        Assert.Contains("[\"mission_tick\"] = mission.Tick", facts, StringComparison.Ordinal);
    }

    [Fact]
    public void DeathTerminalFeedsTheRecoveredMixBeforeTheNominalPause()
    {
        string audio = ReadAudioSource("level100_audio.gd");
        string consume = GdMethodBody(audio, "consume_frame");
        AssertOccursInOrder(consume,
            "consume_destruction_events(facts.destruction_events)",
            "set_gameplay_mix(facts.gameplay_mix)", "set_gameplay_paused(facts.gameplay_paused)");
        Assert.Equal(1, CountOccurrences(consume, "set_gameplay_mix("));
        Assert.Equal(1, CountOccurrences(consume, "set_gameplay_paused("));
        string bridge = ReadGodotSource("Level100Audio.cs");
        Assert.Contains("Level100MissionTiming.GameplayMix(", bridge, StringComparison.Ordinal);
        Assert.Contains("Level100MissionTiming.GameplayPaused(", bridge, StringComparison.Ordinal);
        string game = ReadGodotSource("FirstFlightGame.cs");
        Assert.DoesNotContain("OpenAuthenticPauseMenu", MethodBody(game, "private void ConsumeFrameEvents(FrameAdvanceResult result)"), StringComparison.Ordinal);
        string resume = MethodBody(game, "private void ResumeFromAuthenticPause()");
        AssertOccursInOrder(resume,
            "_session.SetAuthenticMenuPaused(false);",
            "Level100MissionSnapshot mission = _session.CurrentSnapshot.Level100Mission;",
            "_audio.SetGameplayPaused(Level100MissionTiming.GameplayPaused(",
            "mission.Outcome,", "mission.FailureReason,", "mission.TerminalTicksRemaining));");
        Assert.DoesNotContain("_audio.SetGameplayPaused(false)", resume, StringComparison.Ordinal);
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
        string destructionConsumer = GdMethodBody(ReadAudioSource("level100_audio.gd"), "consume_destruction_events");
        Assert.Contains($"{(int)Level100DestructionEffectKind.DroneDestroyed}: cue = Catalog.EffectCue.DRONE_DESTROYED", destructionConsumer, StringComparison.Ordinal);
        AssertOccursInOrder(destructionConsumer, "Catalog.get_effect(cue)", "retail_world(event.position)");

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
        Assert.Equal(
            RetailMusicPolicy.TrackIndex(RetailMusicSelection.Tutorial),
            music.RetailTrackIndex);
        Assert.Equal("data/Music/BEA_04(Master).ogg", music.RetailSourceName);
        Assert.Equal(
            "res://Assets/Level100/Music/tutorial-track-03.ogg",
            music.ResourcePath);
    }

    // The recovered MUS_FRONTEND law, in one place: which track, that selection
    // end replays it through shared policy, and that level entry stops it before
    // the tutorial track starts.
    // Evidence for each clause is cited in Level100AudioCatalog.FrontendMusic.
    [Fact]
    public void FrontendMusic_IsTrackEightReplayedAndStoppedOnLevelEntry()
    {
        Level100MusicRecipe music = Level100AudioCatalog.FrontendMusic;

        Assert.Equal("MUS_FRONTEND", music.RetailSelection);
        Assert.Equal(8, music.RetailTrackIndex);
        Assert.Equal(
            RetailMusicPolicy.TrackIndex(RetailMusicSelection.Frontend),
            music.RetailTrackIndex);
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

        // The exact retail source must be materialized. Selection replay belongs
        // to RetailMusicPolicy, not the decoder stream, and level entry stops the
        // frontend selection before the tutorial selection starts.
        string audio = ReadAudioSource("level100_audio.gd");
        string scene = ReadAudioSource("Level100Audio.tscn");
        string game = ReadGodotSource("FirstFlightGame.cs");
        string frontend = ReadGodotSource("RetailFrontendFlow.cs");
        string materializer = ReadGodotSource("materialize_retail_assets.py");
        Assert.Contains(music.RetailSourceName, materializer, StringComparison.Ordinal);
        Assert.Contains("var _music_policy := MusicPolicy.new()", audio, StringComparison.Ordinal);
        Assert.Contains("_music.finished.connect(_music_finished)", GdMethodBody(audio, "_ready"), StringComparison.Ordinal);
        Assert.Contains("_apply_music(_music_policy.handle_track_finished())", GdMethodBody(audio, "_music_finished"), StringComparison.Ordinal);
        string authoredFrontend = SceneResourceBody(scene, "FrontendMusic");
        Assert.Contains("source_path = \"res://Assets/Frontend/Music/frontend-track-08.ogg\"", authoredFrontend, StringComparison.Ordinal);
        Assert.DoesNotContain("looping = true", authoredFrontend, StringComparison.Ordinal);
        Assert.Contains("looping: bool = false", ReadAudioSource("retail_audio_stream.gd"), StringComparison.Ordinal);
        string ready = MethodBody(game, "public override void _Ready()");
        string startupComplete = MethodBody(
            game,
            "private void StartFrontendMusicAfterStartupMedia()");
        string stopForLevel = MethodBody(
            game,
            "private void StopFrontendMusicForLevelEntry()");
        string navigation = NativeFrontendSource.RootFunction("_handle_navigation_signal");
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
        Assert.Contains("case \"level_loading_started\": Level100LoadingStarted?.Invoke();", frontend, StringComparison.Ordinal);
        AssertOccursInOrder(navigation,
            "_load_request_raised = false", "_level100_ready = false",
            "_gameplay_activation_raised = false", "_loading_frames = 0",
            "_dispatch_host({\"kind\": \"level_loading_started\"})",
            "_cursor_mode(Frontend.CursorMode.HIDDEN)");
        Assert.Contains("_audio.StopFrontendMusic();", stopForLevel, StringComparison.Ordinal);
        AssertOccursInOrder(
            activateGameplay,
            "_audio.StartTutorialMusic();",
            "_gameplayActive = true;");
    }

    private static string ReadGodotSource(string fileName) =>
        File.ReadAllText(
            Path.Combine(AppContext.BaseDirectory, "godot-pause-source", fileName));

    private static string ReadAudioSource(string fileName) =>
        File.ReadAllText(
            Path.Combine(AppContext.BaseDirectory, "godot-audio-layout-source", fileName));

    private static string GdMethodBody(string source, string name)
    {
        int start = source.IndexOf("func " + name + "(", StringComparison.Ordinal);
        Assert.True(start >= 0, $"Expected native audio method '{name}'.");
        int next = source.Length;
        foreach (string boundary in new[] { "\nfunc ", "\nstatic func " })
        {
            int found = source.IndexOf(boundary, start, StringComparison.Ordinal);
            if (found >= 0) next = Math.Min(next, found);
        }
        return source[start..next];
    }

    private static string SceneResourceBody(string source, string resourceId)
    {
        string declaration = $"[sub_resource type=\"Resource\" id=\"{resourceId}\"]";
        int start = source.IndexOf(declaration, StringComparison.Ordinal);
        Assert.True(start >= 0, $"Expected authored audio resource '{resourceId}'.");
        int next = source.IndexOf("\n[", start + declaration.Length, StringComparison.Ordinal);
        return next < 0 ? source[start..] : source[start..next];
    }

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
        int next = source.Length;
        foreach (string boundary in new[] { "\n    private ", "\n    public ", "\n    protected ", "\n    internal " })
        {
            int found = source.IndexOf(boundary, start + declaration.Length, StringComparison.Ordinal);
            if (found >= 0) next = Math.Min(next, found);
        }
        return source[start..next];
    }

    [Fact]
    public void SoundMasterOption_UsesTheReleasedDirectFloatAndRejectsInvalidValues()
    {
        Assert.Equal(0f, Level100AudioCatalog.ToRetailSoundMasterVolume(0f));
        Assert.Equal(0.8f, Level100AudioCatalog.ToRetailSoundMasterVolume(0.8f));
        Assert.Equal(1f, Level100AudioCatalog.ToRetailSoundMasterVolume(1f));
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            Level100AudioCatalog.ToRetailSoundMasterVolume(float.NaN));
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            Level100AudioCatalog.ToRetailSoundMasterVolume(-0.01f));
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            Level100AudioCatalog.ToRetailSoundMasterVolume(1.01f));
    }

    [Fact]
    public void ColdStartOptionState_UsesTheDistinctReleasedSoundAndMusicLaws()
    {
        const float retailSoundOption = 0.8f;
        const float retailMusicOption = 0.9f;
        string audio = ReadAudioSource("level100_audio.gd");
        string music = ReadAudioSource("music_policy.gd");
        Assert.Contains($"SOUND_OPTION_WORD: int = 0x{BitConverter.SingleToUInt32Bits(retailSoundOption):x8}", audio, StringComparison.Ordinal);
        Assert.Contains("_sound_master: float = F32.read_word(SOUND_OPTION_WORD)", audio, StringComparison.Ordinal);
        Assert.Contains($"AUTHORED_DEFAULT_VOLUME_WORD: int = 0x{BitConverter.SingleToUInt32Bits(retailMusicOption):x8}", music, StringComparison.Ordinal);
        AssertOccursInOrder(GdMethodBody(music, "_init"),
            "_configured_volume = F32.read_word(AUTHORED_DEFAULT_VOLUME_WORD)",
            "_set_volume = Audio.round_volume(_configured_volume)");
        Assert.Equal(retailSoundOption, Level100AudioCatalog.ToRetailSoundMasterVolume(retailSoundOption));
        Assert.Equal(114, Level100AudioCatalog.ToRetailMusicSetVolume(retailMusicOption));
        var policy = new RetailMusicPolicy();
        Assert.Equal(retailMusicOption, policy.ConfiguredVolume);
        Assert.Equal(114, policy.SetVolume);
    }

    [Fact]
    public void SoundOptionChange_StoresTheDirectMasterAndReappliesTheMix()
    {
        string setter = GdMethodBody(ReadAudioSource("level100_audio.gd"), "set_master_sound_option");
        AssertOccursInOrder(setter,
            "Catalog.to_retail_sound_master_volume(value)", "if not admitted.ok:", "return admitted",
            "_sound_master = admitted.value", "_apply_mix()");
    }

    [Fact]
    public void MusicOptionChange_HandsTheRawFloatToTheSharedPolicy()
    {
        string setter = GdMethodBody(ReadAudioSource("level100_audio.gd"), "set_music_option");
        Assert.Contains("_music_policy.set_configured_volume(value)", setter, StringComparison.Ordinal);
        Assert.DoesNotContain("round_volume", setter, StringComparison.Ordinal);
        Assert.DoesNotContain("127", setter, StringComparison.Ordinal);
    }

    [Fact]
    public void MusicOptionChange_PreservesTheRawCareerFloatWhileChangingRoundedState()
    {
        var menu = new RetailOptionsMenu();
        menu.Enter(RetailOptionsPage.Sound);
        Assert.True(menu.MoveSelection(1));
        Assert.Equal("Music Volume", menu.SelectedRow.Label);

        int originalSetVolume = Level100AudioCatalog.ToRetailMusicSetVolume(
            menu.Settings.MusicVolume);
        Assert.True(menu.Adjust(-1));

        const float expectedRawCareerValue = 0.8f;
        Assert.Equal(expectedRawCareerValue, menu.Settings.MusicVolume);
        int changedSetVolume = Level100AudioCatalog.ToRetailMusicSetVolume(
            menu.Settings.MusicVolume);
        Assert.Equal(114, originalSetVolume);
        Assert.Equal(102, changedSetVolume);
        Assert.NotEqual(originalSetVolume, changedSetVolume);
        Assert.NotEqual(changedSetVolume / 127f, menu.Settings.MusicVolume);
        Assert.Equal(expectedRawCareerValue, menu.Settings.MusicVolume);

        string applyOptions = MethodBody(
            ReadGodotSource("FirstFlightGame.cs"),
            "private void ApplyOptionsSettings(RetailOptionsSettings settings)");
        Assert.Contains(
            "_audio.SetMusicOption(settings.MusicVolume);",
            applyOptions,
            StringComparison.Ordinal);
        Assert.DoesNotContain(
            "ToRetailMusicSetVolume",
            applyOptions,
            StringComparison.Ordinal);
    }

    [Fact]
    public void FirstFlightOptionsBoundaryDoesNotRepeatTheRetainedTangentClaim()
    {
        string game = ReadGodotSource("FirstFlightGame.cs");

        Assert.DoesNotContain("tan(x*1.38)", game, StringComparison.Ordinal);
        Assert.Contains("sound stores that float", game, StringComparison.Ordinal);
        Assert.Contains("music stores round(volume * 127)", game, StringComparison.Ordinal);
        Assert.Contains(
            "Downstream device math and audible parity are still",
            game,
            StringComparison.Ordinal);
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

    [Theory]
    [InlineData(0f, 0)]
    [InlineData(0.1f, 13)]
    [InlineData(2.5f / 127f, 2)] // ToEven = 2; AwayFromZero = 3.
    [InlineData(0.5f, 64)]
    [InlineData(0.8f, 102)]
    [InlineData(0.9f, 114)]
    [InlineData(1f, 127)]
    public void MusicOption_UsesTheReleasedRoundedSetVolumeDeterministically(
        float optionValue,
        int expectedSetVolume)
    {
        Assert.Equal(
            expectedSetVolume,
            Level100AudioCatalog.ToRetailMusicSetVolume(optionValue));
        Assert.Equal(
            expectedSetVolume,
            Level100AudioCatalog.ToRetailMusicSetVolume(optionValue));
    }

    [Fact]
    public void MusicOption_RejectsValuesOutsideTheReleasedOptionBounds()
    {
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            Level100AudioCatalog.ToRetailMusicSetVolume(float.NaN));
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            Level100AudioCatalog.ToRetailMusicSetVolume(-0.01f));
        Assert.Throws<ArgumentOutOfRangeException>(() =>
            Level100AudioCatalog.ToRetailMusicSetVolume(1.01f));
    }

    // ==================================================================
    // The three released audio laws recovered on 2026-07-27.
    // See local-lab/AUDIO-PARITY-LAWS-2026-07-27.md.
    // ==================================================================

    /// <summary>Retail's directly stored cold-start sound master volume.</summary>
    private const float ColdStartSoundMasterVolume = 0.8f;

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
    // things in Level 100's flight segment. Retail puts the jet engine 14 dB
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
            ColdStartSoundMasterVolume,
            1f);
        float weaponDb = Level100AudioCatalog.RetailVolumeDb(
            Level100AudioCatalog.RetailListenerSourceVolume,
            weapon,
            Level100AudioCatalog.RetailUnfadedSubVolume,
            ColdStartSoundMasterVolume,
            1f);

        Assert.Equal(-10.0f, engineDb, 3);
        Assert.Equal(-24.0f, weaponDb, 3);
        Assert.Equal(14.0f, engineDb - weaponDb, 3);
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

        string audio = ReadAudioSource("level100_audio.gd");
        AssertOccursInOrder(GdMethodBody(audio, "advance"),
            "for key: String in [\"flight\", \"warning\"]", "_advance_fade(key, delta)");
        AssertOccursInOrder(GdMethodBody(audio, "_fade_in_flight"),
            "_set_loop(\"flight\", _aquila, \"RetailAquilaInFlightLoop\", spec, true, 0.0)",
            "_fades.flight.sub = 0.0", "_fades.flight.target = 1.0",
            "_fades.flight.step = F32.read_word(Catalog.RETAIL_FLIGHT_LOOP_FADE_STEP_WORD)");
        Assert.Contains("_fade_out_flight()", GdMethodBody(audio, "consume_aquila_flight_events"), StringComparison.Ordinal);
        Assert.Contains("_fade_out_flight()", GdMethodBody(audio, "play_aquila_transition"), StringComparison.Ordinal);
        Assert.Contains("_live_loops.get(\"flight\") == player", GdMethodBody(audio, "_update_spatial_attenuation"), StringComparison.Ordinal);
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
    // the jet's 1 + thruster*0.25 (BattleEngine.cpp:1542). Retail PC therefore
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

    // These guards follow production wiring. Actual audio state and values are
    // compared in the native scene harness; the retained C# catalog above
    // continues to pin the independent numerical expectations during migration.
    [Fact]
    public void Level100Audio_AppliesTheThreeReleasedLawsAndNotTheInventedOnes()
    {
        string audio = ReadAudioSource("level100_audio.gd");
        // Law 1: sample gain uses the released catalog law. Only music crosses
        // Godot's native linear setter, which preserves the float logarithm.
        foreach (string method in new[] { "_mixed_db", "_spatial_db" })
        {
            string volume = GdMethodBody(audio, method);
            Assert.Contains("Catalog.retail_volume_db(", volume, StringComparison.Ordinal);
            Assert.Contains("_sound_master", volume, StringComparison.Ordinal);
            Assert.DoesNotContain("linear_to_db(", volume, StringComparison.Ordinal);
            Assert.DoesNotContain("volume_linear", volume, StringComparison.Ordinal);
        }
        Assert.Contains("_music.volume_linear = _f32(float(volume) / 127.0)", GdMethodBody(audio, "_set_music_volume"), StringComparison.Ordinal);
        Assert.DoesNotContain("ToRetailOptionMix", audio, StringComparison.Ordinal);

        // Law 2: the authored player disables Godot attenuation; the owner
        // applies retail's early refusal and updates tracked player gains.
        string spatialScene = ReadAudioSource("SpatialVoice.tscn");
        Assert.Contains("attenuation_model = 3", spatialScene, StringComparison.Ordinal);
        Assert.Contains("max_distance = 0.0", spatialScene, StringComparison.Ordinal);
        string spatial = GdMethodBody(audio, "_play_spatial");
        AssertOccursInOrder(spatial,
            "player.pitch_scale = _pitch_for(spec)",
            "Catalog.retail_refuses_non_looping_start(distance)",
            "player.volume_db = _spatial_db(spec.linear_volume, distance)", "player.play()");
        Assert.Contains("_update_spatial_attenuation()", GdMethodBody(audio, "advance"), StringComparison.Ordinal);
        Assert.Contains("Catalog.retail_source_volume_for_distance(distance)", GdMethodBody(audio, "_spatial_db"), StringComparison.Ordinal);

        // Law 3: both pitch producers pass through the same PC clamp, including
        // the variance draw consumed before a distant one-shot is refused.
        Assert.Contains("Catalog.retail_pc_pitch_multiplier(desired)", GdMethodBody(audio, "_pitch_for"), StringComparison.Ordinal);
        Assert.Contains("Catalog.retail_pc_pitch_multiplier(_f32(1.0 + _f32(admitted.value * 0.25)))",
            GdMethodBody(audio, "set_aquila_flight_pitch"), StringComparison.Ordinal);
        Assert.Contains("player.pitch_scale = _pitch_for(spec)", GdMethodBody(audio, "_set_loop"), StringComparison.Ordinal);
    }

    [Fact]
    public void NativeAudioSceneOwnsPlayersAndStartsOnlyAfterRuntimeConfiguration()
    {
        string bridge = ReadGodotSource("Level100Audio.cs");
        AssertOccursInOrder(MethodBody(bridge, "public override void _Ready()"),
            "SetProcess(false)", "if (Engine.IsEditorHint()) return;",
            "GD.Load<PackedScene>(\"res://Scenes/Audio/Level100Audio.tscn\")",
            "AddChild(_native)", "Invoke(\"configure\", Callable.From<Node>(ObservePlayback))");
        foreach (string competingOwner in new[] { "new AudioStreamPlayer", "new RetailMusicPolicy", "new Level100CharacterMessageQueue", "LegacyLevel100AudioReference" })
            Assert.DoesNotContain(competingOwner, bridge, StringComparison.Ordinal);
        Assert.Contains("PlaybackRetirement.Observe(flat)", bridge, StringComparison.Ordinal);
        Assert.Contains("PlaybackRetirement.Observe(spatial)", bridge, StringComparison.Ordinal);

        string scene = ReadAudioSource("Level100Audio.tscn");
        Assert.Contains("path=\"res://Scenes/Audio/level100_audio.gd\"", scene, StringComparison.Ordinal);
        foreach (string role in new[] { "Music", "CharacterVoice", "FlightLoop", "WarningLoop", "AirTrainer", "Transport", "RepairPad" })
            Assert.Contains($"[node name=\"{role}\"", scene, StringComparison.Ordinal);
        foreach (string player in new[] { "OneShot2D.tscn", "SpatialVoice.tscn" })
            Assert.Contains("autoplay = false", ReadAudioSource(player), StringComparison.Ordinal);
        string audio = ReadAudioSource("level100_audio.gd");
        AssertOccursInOrder(GdMethodBody(audio, "_ready"),
            "set_process(false)", "if Engine.is_editor_hint():", "return", "_voice.finished.connect");
        AssertOccursInOrder(GdMethodBody(audio, "configure"),
            "Engine.is_editor_hint() or not is_node_ready() or _initialized",
            "if not playback_started.is_valid():", "_validate_authored_recipes()",
            "_observer = playback_started", "_initialized = true", "set_process(true)");
        AssertOccursInOrder(GdMethodBody(ReadAudioSource("retail_audio_stream.gd"), "load_stream"),
            "if Engine.is_editor_hint():", "return _failure(", "FileAccess.get_file_as_bytes(source_path)");
    }

    [Fact]
    public void AudioFrameBatchRetainsTheExistingHudAndWorldInterleavings()
    {
        string nativeFrame = GdMethodBody(ReadAudioSource("level100_audio.gd"), "consume_frame");
        AssertOccursInOrder(nativeFrame,
            "update_aquila_pose(facts.actors)", "set_aquila_warning_state(facts.warning_state)",
            "_interleave(interleave, 0)", "queue_character_message(message.speaker_id, message.message_id)",
            "consume_aquila_flight_events(facts.flight_events, facts.simulation_tick, facts.mission_tick)",
            "consume_weapon_fire_events(facts.weapon_events)", "_interleave(interleave, 1)",
            "set_aquila_flight_pitch(facts.thruster_fraction)", "_interleave(interleave, 2)",
            "consume_destruction_events(facts.destruction_events)",
            "set_gameplay_mix(facts.gameplay_mix)", "set_gameplay_paused(facts.gameplay_paused)");
        Assert.Equal(3, CountOccurrences(nativeFrame, "_interleave(interleave,"));
        for (int phase = 0; phase < 3; phase++)
        {
            string call = $"_interleave(interleave, {phase})";
            int start = nativeFrame.IndexOf(call, StringComparison.Ordinal);
            int next = nativeFrame.IndexOf("\n\tresult =", start + call.Length, StringComparison.Ordinal);
            string phaseTail = next < 0 ? nativeFrame[start..] : nativeFrame[start..next];
            AssertOccursInOrder(phaseTail, "if not result.ok:", "return result");
        }

        string bridge = ReadGodotSource("Level100Audio.cs");
        string consume = MethodBody(bridge, "public void ConsumeFrame(FrameAdvanceResult frame, Action<int> interleave)");
        Assert.Equal(1, CountOccurrences(consume, "Native.Call(\"consume_frame\", FrameFacts(frame), callback)"));
        AssertOccursInOrder(consume, "interleave(phase)", "hostFailure = error", "Native.Call(\"consume_frame\"",
            "ExceptionDispatchInfo.Capture(hostFailure).Throw()", "Check(result)");
        string facts = MethodBody(bridge, "private static D FrameFacts(FrameAdvanceResult frame)");
        Assert.Contains("foreach (Level100MissionEvent value in frame.Level100MissionEvents)", facts, StringComparison.Ordinal);
        Assert.Contains("foreach (AquilaFlightEvent value in frame.AquilaFlightEvents)", facts, StringComparison.Ordinal);
        Assert.Contains("foreach (Level100WeaponFireEvent value in frame.Level100WeaponFireEvents)", facts, StringComparison.Ordinal);
        Assert.Contains("foreach (Level100DestructionEvent value in frame.Level100DestructionEvents)", facts, StringComparison.Ordinal);
        Assert.DoesNotContain("OrderBy", facts, StringComparison.Ordinal);
        Assert.DoesNotContain("Distinct", facts, StringComparison.Ordinal);

        string game = ReadGodotSource("FirstFlightGame.cs");
        string frame = MethodBody(game, "private void ConsumeFrameEvents(FrameAdvanceResult result)");
        Assert.Equal(1, CountOccurrences(frame, "_audio.ConsumeFrame(result,"));
        AssertOccursInOrder(frame,
            "case 0:", "ConsumeLevel100MissionEvents(result.Level100MissionEvents)",
            "case 1:", "_world.ConsumeLevel100WeaponFireEvents(result.Level100WeaponFireEvents)",
            "case 2:", "_world.ConsumeLevel100DestructionEvents(");
        string messages = MethodBody(game, "private void ConsumeLevel100MissionEvents(");
        AssertOccursInOrder(messages, "_hud.ConsumeMissionEvents(events)", "_smokeAudioQueuedSpeakerIds.Add(message.SpeakerId)",
            "_smokeAudioQueuedMessageIds.Add(message.MessageId)");
        Assert.DoesNotContain("_audio.QueueCharacterMessage", messages, StringComparison.Ordinal);
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
