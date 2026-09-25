// SPDX-License-Identifier: GPL-3.0-or-later
using OnslaughtRebuild.Client;
using OnslaughtRebuild.GodotClient;

namespace OnslaughtRebuild.TestSupport;

/// <summary>
/// Executes the existing pure C# audio catalog, queue and music policy. Focused
/// source tests supply the sequences; represented numeric/string edge cases
/// test migration semantics and do not establish new retail input behavior.
/// No assets, device APIs, filesystem discovery or playback are invoked.
/// </summary>
public static class GdscriptAudioPolicyOracle
{
    public static object BuildFixtures()
    {
        var recipes = new List<object>();
        void Recipe(string method, int identity, Func<Level100AudioCueRecipe> get) =>
            recipes.Add(new { method, identity, cue_units = (int[]?)null, expected = Capture(() => Cue(get())) });
        foreach (Level100EffectCue cue in Enum.GetValues<Level100EffectCue>())
            Recipe("effect", (int)cue, () => Level100AudioCatalog.GetEffect(cue));
        foreach (Level100TerminalCue cue in Enum.GetValues<Level100TerminalCue>())
            Recipe("terminal", (int)cue, () => Level100AudioCatalog.GetTerminal(cue));
        foreach (AquilaTransitionCue cue in Enum.GetValues<AquilaTransitionCue>())
            Recipe("transition", (int)cue, () => Level100AudioCatalog.GetAquilaTransition(cue));
        foreach (AquilaWarningAudioState state in Enum.GetValues<AquilaWarningAudioState>())
            Recipe("warning", (int)state, () => Level100AudioCatalog.GetAquilaWarning(state));
        foreach (Level100ActorLoopCue cue in Enum.GetValues<Level100ActorLoopCue>())
            Recipe("loop", (int)cue, () => Level100AudioCatalog.GetActorLoop(cue));
        foreach (int identity in new[] { int.MinValue, -1, 21, 100, int.MaxValue })
        {
            Recipe("effect", identity, () => Level100AudioCatalog.GetEffect((Level100EffectCue)identity));
            Recipe("terminal", identity, () => Level100AudioCatalog.GetTerminal((Level100TerminalCue)identity));
            Recipe("transition", identity, () => Level100AudioCatalog.GetAquilaTransition((AquilaTransitionCue)identity));
            Recipe("warning", identity, () => Level100AudioCatalog.GetAquilaWarning((AquilaWarningAudioState)identity));
            Recipe("loop", identity, () => Level100AudioCatalog.GetActorLoop((Level100ActorLoopCue)identity));
        }
        foreach (string? name in new[] { "Back", "Move", "Select", "back", "", "fallback", null, "Back\0", "\ufeffBack", "\ud800" })
            recipes.Add(new { method = "frontend", identity = 0, cue_units = Units(name),
                expected = Capture(() => Cue(Level100AudioCatalog.GetFrontend(name!))) });

        var laws = new List<object>();
        void Law(string operation, int[] integers, float[] values, Func<object?> invoke) =>
            laws.Add(new { name = operation + "_" + laws.Count, operation, integers,
                words = values.Select(Word).ToArray(), expected = Capture(invoke) });
        void Option(float value)
        {
            Law("sound_option", [], [value], () => Word(Level100AudioCatalog.ToRetailSoundMasterVolume(value)));
            Law("music_option", [], [value], () => Level100AudioCatalog.ToRetailMusicSetVolume(value));
        }
        foreach (float value in new[] { 0f, -0f, .1f, .5f, .8f, .9f, 1f, -.01f, 1.01f,
            float.Epsilon, -float.Epsilon, float.MaxValue, -float.MaxValue,
            float.NaN, float.PositiveInfinity, float.NegativeInfinity }) Option(value);
        for (int step = 0; step < 127; step++)
        {
            float tie = (step + .5f) / 127f;
            Option(MathF.BitDecrement(tie)); Option(tie); Option(MathF.BitIncrement(tie));
        }
        void Distance(float value)
        {
            Law("distance", [], [value], () => Level100AudioCatalog.RetailSourceVolumeForDistance(value));
            Law("nonloop_start", [], [value], () => Level100AudioCatalog.RetailRefusesNonLoopingStart(value));
        }
        foreach (float value in new[] { -1f, -0f, 0f, 4f, 8f, 20f, 25f, 45f, 49.99f, 50f, 80f,
            MathF.BitDecrement(50f), MathF.BitIncrement(50f), float.NaN, float.PositiveInfinity,
            float.NegativeInfinity, float.MaxValue, -float.MaxValue }) Distance(value);
        foreach (int value in new[] { int.MinValue, int.MinValue + 1, -10001, -10000, -5000, -4600,
            -4100, -4001, -4000, -3900, -1, 0, 1, int.MaxValue })
            Law("pc_shape", [value], [], () => Level100AudioCatalog.RetailPcShapedMillibels(value));
        void Mix(int source, float effect, float sub, float master, float type)
        {
            Law("fade", [source], [effect, sub, master, type], () =>
                Level100AudioCatalog.RetailFadeMillibels(source, effect, sub, master, type));
            Law("volume_db", [source], [effect, sub, master, type], () =>
                Word(Level100AudioCatalog.RetailVolumeDb(source, effect, sub, master, type)));
        }
        foreach (int source in new[] { 0, 100, 127 })
            foreach (float volume in new[] { 0f, .39f, .394f, .489f, .499f, .5f, .6f, .75f, 1f })
                Mix(source, volume, 1f, 1f, 1f);
        Mix(100, Level100AudioCatalog.GetAquilaTransition(AquilaTransitionCue.InFlight).LinearVolume, 1f, .8f, 1f);
        Mix(100, Level100AudioCatalog.GetEffect(Level100EffectCue.PulseCannonFire).LinearVolume, 1f, .8f, 1f);
        foreach (float distance in new[] { 20f, 45f })
            Mix(Level100AudioCatalog.RetailSourceVolumeForDistance(distance),
                Level100AudioCatalog.GetEffect(Level100EffectCue.PulseImpact).LinearVolume, 1f, 1f, 1f);
        foreach (int source in new[] { int.MinValue, -16777217, -1, 16777217, int.MaxValue })
            foreach (float value in new[] { -1f, 0f, .5f, 1f, float.MaxValue,
                float.NaN, float.NegativeInfinity, float.PositiveInfinity }) Mix(source, value, 1f, 1f, 1f);
        uint seed = 0x41554449;
        uint Next() => seed = unchecked(seed * 1664525u + 1013904223u);
        for (int index = 0; index < 256; index++)
        {
            int source = index % 2 == 0 ? (int)(Next() % 128) : unchecked((int)Next());
            float effect = (int)(Next() % 2001) / 1000f;
            float sub = (int)(Next() % 1001) / 1000f;
            float master = (int)(Next() % 1001) / 1000f;
            float type = (int)(Next() % 1001) / 1000f;
            Mix(source, effect, sub, master, type);
            Distance(((int)(Next() % 100001) - 25000) / 1000f);
        }
        foreach (uint word in new uint[] { 0, 0x80000000, 1, 0x80000001, 0x3f000000, 0x3f800000,
            0x3f800001, 0x3fa00000, 0x7f800000, 0xff800000, 0x7fc00000, 0xffc12345, 0x7f800001, 0xff800123 })
        {
            float pitch = BitConverter.UInt32BitsToSingle(word);
            Law("pitch_word", [], [pitch], () => Word(Level100AudioCatalog.RetailPcPitchMultiplier(pitch)));
        }
        var contacts = new List<object>();
        foreach ((int current, int previous) in new (int, int)[]
        {
            (100,0), (101,0), (102,101), (202,102), (303,202), (1,2), (0,0),
            (int.MaxValue,int.MinValue), (int.MinValue,int.MaxValue), (int.MinValue,int.MinValue),
        })
        {
            int stored = previous;
            Dictionary<string, object?> result = Capture(() => Level100AudioCatalog.ObserveHostileEnvironmentContact(current, ref stored));
            result["previous_contact_tick"] = stored;
            contacts.Add(new { current, previous, expected = result });
        }
        var flight = new List<object>();
        void Flight(float current, float target, float step)
        {
            bool crossed = false;
            Dictionary<string, object?> result = Capture(() => Word(Level100AudioCatalog.AdvanceRetailFlightLoopSubVolume(current, target, step, out crossed)));
            if ((bool)result["ok"]!) result["crossed_target"] = crossed;
            flight.Add(new { words = new[] { Word(current), Word(target), Word(step) }, expected = result });
        }
        foreach (bool fadeIn in new[] { true, false })
        {
            float value = fadeIn ? 0f : 1f;
            float goal = fadeIn ? 1f : 0f;
            float step = (fadeIn ? 1 : -1) * Level100AudioCatalog.RetailFlightLoopFadeStep;
            for (int index = 0; index < 52; index++)
            {
                Flight(value, goal, step);
                value = Level100AudioCatalog.AdvanceRetailFlightLoopSubVolume(value, goal, step, out _);
            }
        }
        float reversed = 0f;
        for (int index = 0; index < 21; index++)
        {
            float step = (index < 10 ? 1 : -1) * Level100AudioCatalog.RetailFlightLoopFadeStep;
            float goal = index < 10 ? 1f : 0f;
            Flight(reversed, goal, step);
            reversed = Level100AudioCatalog.AdvanceRetailFlightLoopSubVolume(reversed, goal, step, out _);
        }
        foreach (float value in new[] { -.01f, 1.01f, float.NaN, float.PositiveInfinity, float.NegativeInfinity })
        {
            Flight(value, 1f, .02f); Flight(0f, value, .02f); Flight(0f, 1f, value);
        }
        foreach (float value in new[] { 0f, -0f, .01f, MathF.BitDecrement(.02f), MathF.BitIncrement(.02f), -.02f })
            Flight(0f, 1f, value);
        var character = new List<object>();
        foreach (int identity in Level100AudioCatalog.CharacterMessages.Select(row => row.MessageId)
            .Concat([int.MinValue, -1, 0, 1, int.MaxValue]))
            character.Add(new { identity, expected = Capture(() => Message(Level100AudioCatalog.GetCharacterMessage(identity))) });
        return new { schema = 1, recipes, laws, contacts, flight, character,
            character_specs = Level100AudioCatalog.CharacterMessages.Select(Message).ToArray(),
            tutorial_music = Music(Level100AudioCatalog.TutorialMusic), frontend_music = Music(Level100AudioCatalog.FrontendMusic),
            constants = Constants(), track_indices = new[] { int.MinValue, -1, 0, 1, 2, 3, int.MaxValue }
                .Select(value => new { selection = value, expected = Capture(() => RetailMusicPolicy.TrackIndex((RetailMusicSelection)value)) }).ToArray(),
            music_scenarios = MusicScenarios(), queue = QueueScenario() };
    }

    private static object MusicScenarios()
    {
        var scenarios = new List<object>();
        MusicTape Begin(string name) { var tape = new MusicTape(name); scenarios.Add(tape.Fixture); return tape; }
        var initial = Begin("initial_and_option_admission");
        initial.Fade(); initial.Finish(); initial.Kill();
        foreach (float value in new[] { -0f, 0f, 2.5f / 127f, 3.5f / 127f, .5f, .8f, .9f, 1f,
            -.01f, 1.01f, float.NaN, float.PositiveInfinity, float.NegativeInfinity }) initial.Volume(value);
        initial.Reset();
        var replacement = Begin("immediate_and_faded_selection");
        replacement.Select(0, "frontend-track-08.ogg"); replacement.Select(2, "tutorial-track-03.ogg");
        replacement.Finish(); replacement.Select(0, "frontend-track-08.ogg", true);
        replacement.Fade(22); replacement.Finish(); replacement.Kill(); replacement.Reset();
        var replay = Begin("existing_pinned_replay_tape");
        replay.Select(0, "frontend-track-08.ogg"); replay.Select(2, "tutorial-track-03.ogg", true);
        replay.Fade(22); replay.Volume(.8f); replay.Fade(); replay.Finish();
        var same = Begin("same_track_keeps_existing_queue_and_selection");
        same.Select(0, "A"); same.Select(2, "B", true); same.Select(2, "A", true);
        same.Fade(22); same.Finish(); same.Volume(.8f); same.Fade(4);
        var random = Begin("direct_list_assignment_and_retained_selection");
        random.List("named", null, false); random.Finish(); random.List(null, "random", false);
        random.Finish(); random.Select(int.MaxValue, "selection"); random.List("named-again", null, false);
        random.Finish(); random.Kill();
        var nullQueue = Begin("null_faded_request_has_no_replacement");
        nullQueue.Select(0, "A"); nullQueue.List(null, null); nullQueue.Fade(26); nullQueue.Finish();
        var nullFailure = Begin("null_direct_failure_mutates_metadata_before_error");
        nullFailure.List(null, null, false); nullFailure.Select(0, "A"); nullFailure.Select(2, "B", true);
        nullFailure.List(null, null, false); nullFailure.Fade(22); nullFailure.Finish();
        var nullSelection = Begin("represented_null_and_unknown_selection");
        nullSelection.Select(2, null); nullSelection.Finish(); nullSelection.Select(int.MinValue, "");
        nullSelection.Finish(); nullSelection.Select(-1, null, true); nullSelection.Fade(23); nullSelection.Reset();
        var text = Begin("ordinal_raw_utf16_identity");
        foreach (string value in new[] { "", "A\0B", "A\0C", "\ufeff", "\ud800", "\udfff", "\ud83d\ude80", "é", "e\u0301" })
        {
            text.Select(0, value); text.Select(2, value, true); text.Finish();
            text.List(value + "x", value, true); text.Fade(22);
        }
        return scenarios;
    }

    private sealed class MusicTape
    {
        private readonly RetailMusicPolicy _policy = new();
        private readonly List<object> _steps = [];
        public object Fixture { get; }
        public MusicTape(string name) => Fixture = new { name, initial = Snapshot(_policy.Snapshot()), steps = _steps };
        private void Add(string operation, object input, Func<object?> action) =>
            _steps.Add(new { operation, input, result = Capture(action), snapshot = Snapshot(_policy.Snapshot()) });
        public void Select(int selection, string? track, bool fade = false) => Add("selection",
            new { selection, track_units = Units(track), fade }, () => Actions(_policy.PlaySelection((RetailMusicSelection)selection, track!, fade)));
        public void List(string? requested, string? random, bool fade = true) => Add("list",
            new { requested_units = Units(requested), random_units = Units(random), fade },
            () => Actions(_policy.PlayFromList(requested, random, fade)));
        public void Volume(float value) => Add("volume", new { word = Word(value) }, () => { _policy.SetConfiguredVolume(value); return null; });
        public void Fade(int count = 1) { for (int index = 0; index < count; index++) Add("fade", new { }, () => Actions(_policy.AdvanceFadeStep())); }
        public void Finish() => Add("finished", new { }, () => Actions(_policy.HandleTrackFinished()));
        public void Kill() => Add("kill", new { }, () => Actions(_policy.Kill()));
        public void Reset() => Add("reset", new { }, () => Actions(_policy.Reset()));
    }

    private static object QueueScenario()
    {
        var queue = new Level100CharacterMessageQueue();
        var steps = new List<object>();
        void Enqueue(int speaker, int message) => steps.Add(new { operation = "enqueue", speaker, message,
            result = Capture(() => { queue.Enqueue(speaker, message); return null; }), count = queue.Count });
        void Dequeue()
        {
            bool found = queue.TryDequeue(out Level100QueuedCharacterMessage message);
            steps.Add(new { operation = "dequeue", speaker = 0, message = 0,
                result = new { ok = true, found, value = new { speaker_id = message.SpeakerId, audio = Message(message.Audio) } }, count = queue.Count });
        }
        void Clear() { queue.Clear(); steps.Add(new { operation = "clear", speaker = 0, message = 0, result = new { ok = true, value = (object?)null }, count = queue.Count }); }
        Dequeue(); Enqueue(1508464, 292562); Enqueue(1508464, 292562); Enqueue(99, 44677289);
        Enqueue(int.MinValue, int.MaxValue); Dequeue(); Dequeue(); Dequeue(); Dequeue();
        foreach (Level100MessageAudioSpec row in Level100AudioCatalog.CharacterMessages) Enqueue(row.MessageId, row.MessageId);
        foreach (Level100MessageAudioSpec _ in Level100AudioCatalog.CharacterMessages) Dequeue();
        Enqueue(int.MaxValue, 292562); Enqueue(int.MinValue, 292562); Clear(); Dequeue(); Clear();
        return steps;
    }

    private static object Constants() => new
    {
        hostile_quiet_ticks = Level100AudioCatalog.RetailHostileEnvironmentQuietTicks,
        radio_volume_word = Word(Level100AudioCatalog.RetailRadioMessageVolume), hud_volume_word = Word(Level100AudioCatalog.RetailHudMessageVolume),
        default_effect_volume_word = Word(Level100AudioCatalog.RetailDefaultEffectVolume), weapon_launch_volume_word = Word(Level100AudioCatalog.RetailWeaponLaunchVolume),
        far_sound_word = Word(Level100AudioCatalog.RetailFarSoundUnits), untracked_source_volume = Level100AudioCatalog.RetailUntrackedSourceVolume,
        listener_source_volume = Level100AudioCatalog.RetailListenerSourceVolume, unfaded_sub_volume_word = Word(Level100AudioCatalog.RetailUnfadedSubVolume),
        flight_fade_step_word = Word(Level100AudioCatalog.RetailFlightLoopFadeStep), authored_music_volume_word = Word(RetailMusicPolicy.AuthoredDefaultVolume),
        music_full_volume = RetailMusicPolicy.FullVolume, music_fade_step = RetailMusicPolicy.FadeStep, playlist_extension = RetailMusicPolicy.PlaylistExtension,
    };
    private static object Cue(Level100AudioCueRecipe value) => new { resource_path = value.ResourcePath,
        retail_sound_record = value.RetailSoundRecord, retail_effect_name = value.RetailEffectName,
        linear_volume_word = Word(value.LinearVolume), pitch_variance_percent = value.PitchVariancePercent, looping = value.Looping };
    private static object Music(Level100MusicRecipe value) => new { resource_path = value.ResourcePath,
        retail_selection = value.RetailSelection, retail_track_index = value.RetailTrackIndex, retail_source_name = value.RetailSourceName };
    private static object Message(Level100MessageAudioSpec value) => new { message_id = value.MessageId,
        symbol = Units(value.Symbol), audio_stem = Units(value.AudioStem), resource_path = Units(value.ResourcePath) };
    private static object Snapshot(RetailMusicPolicySnapshot value) => new { configured_volume_word = Word(value.ConfiguredVolume),
        set_volume = value.SetVolume, current_volume = value.CurrentVolume, target_volume = value.TargetVolume,
        is_playing = value.IsPlaying, play_type = (int)value.PlayType, current_track_identity = Units(value.CurrentTrackIdentity),
        queued_track_identity = Units(value.QueuedTrackIdentity), selection = (int?)value.Selection,
        selection_track_identity = Units(value.SelectionTrackIdentity) };
    private static object Actions(IReadOnlyList<RetailMusicAction> actions) => actions.Select(value => new {
        kind = (int)value.Kind, track_identity = Units(value.TrackIdentity), volume = value.Volume }).ToArray();
    private static Dictionary<string, object?> Capture(Func<object?> action)
    {
        try { return new() { ["ok"] = true, ["value"] = action() }; }
        catch (Exception error) { return new() { ["ok"] = false, ["error_type"] = error.GetType().Name,
            ["parameter"] = (error as ArgumentException)?.ParamName ?? string.Empty }; }
    }
    private static uint Word(float value) => BitConverter.SingleToUInt32Bits(value);
    private static int[]? Units(string? value) => value?.Select(unit => (int)unit).ToArray();
}
