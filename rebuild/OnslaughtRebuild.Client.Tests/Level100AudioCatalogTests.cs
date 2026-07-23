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
        Assert.Equal(106, pulseImpact.RetailSoundRecord);
        Assert.Equal(pulseImpact, droneDestroyed);

        Level100AudioCueRecipe vulcan =
            Level100AudioCatalog.GetEffect(Level100EffectCue.VulcanCannonFire);
        Assert.Equal(40, vulcan.RetailSoundRecord);
        Assert.Equal(
            "res://Assets/Aquila/SoundEffects/vulcan-cannon-fire.wav",
            vulcan.ResourcePath);

        Level100AudioCueRecipe warehouse =
            Level100AudioCatalog.GetEffect(Level100EffectCue.FacilityDestroyed);
        Assert.Equal(103, warehouse.RetailSoundRecord);

        Level100AudioCueRecipe landing =
            Level100AudioCatalog.GetAquilaTransition(AquilaTransitionCue.Landing);
        Assert.Equal(24, landing.RetailSoundRecord);
        Assert.Equal(
            "res://Assets/Aquila/SoundEffects/engine-land.wav",
            landing.ResourcePath);

        Assert.Equal(41, Level100AudioCatalog.GetFrontend("Back").RetailSoundRecord);
        Assert.Equal(42, Level100AudioCatalog.GetFrontend("Move").RetailSoundRecord);
        Assert.Equal(43, Level100AudioCatalog.GetFrontend("Select").RetailSoundRecord);
    }

    [Fact]
    public void CueCatalog_CoversTheExactBoundedLevel100Categories()
    {
        Assert.Equal(
            [20, 31, 32, 29, 30, 35, 40, 33, 150, 106, 102, 102, 106,
                103, 107, 94, 93, 95, 108, 7, 8],
            Enum.GetValues<Level100EffectCue>()
                .Select(cue => Level100AudioCatalog.GetEffect(cue).RetailSoundRecord)
                .ToArray());
        Assert.Equal(
            [44, 46, 51, 55, 56, 57, 58, 60, 70, 73],
            Enum.GetValues<Level100TerminalCue>()
                .Select(cue => Level100AudioCatalog.GetTerminal(cue).RetailSoundRecord)
                .ToArray());
        Assert.Equal(
            [25, 23, 24],
            Enum.GetValues<AquilaTransitionCue>()
                .Select(cue => Level100AudioCatalog
                    .GetAquilaTransition(cue)
                    .RetailSoundRecord)
                .ToArray());
        Assert.Equal(
            [22, 21],
            new[]
            {
                AquilaWarningAudioState.EnergyLow,
                AquilaWarningAudioState.HullCritical,
            }.Select(state => Level100AudioCatalog
                .GetAquilaWarning(state)
                .RetailSoundRecord)
                .ToArray());
        Assert.Equal(
            [119, 126, 9],
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
}
