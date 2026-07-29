// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.GodotClient;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// The recovered laws of retail's FMV presentation, and the state routing that
/// puts Level 100's intro cutscene where retail puts it.
///
/// <para>These assert LAWS read out of a measurement, not our own arithmetic.
/// The presentation numbers come from a passive D3D9 capture of the released
/// build (<c>G:\bea-d3d9-capture\d3d9-20260728-111552.log</c>, 900 frames /
/// 896 draws, refusals 0, warnings 0, specimen verified unchanged afterwards),
/// written up in <c>local-lab/FMV-PRESENTATION-2026-07-28.md</c>. The routing
/// comes from the pinned source and from the campaign FMV table read out of the
/// pristine specimen.</para>
///
/// <para>They exist because no visual gate can cover this path: every retail
/// reference frame this project compares against was captured with
/// <c>-skipfmv</c>, and the capture rig suppresses the movie for the same
/// reason. A silently broken FMV would otherwise be invisible.</para>
/// </summary>
public sealed class RetailLevel100CutsceneTests
{
    /// <summary>
    /// <c>data/video/cutscenes/01.vid</c>, from its Bink header via ffprobe on
    /// <c>local-lab/safe-copy-bea-pristine</c>: 480x300, 25 fps, 123.80 s.
    /// </summary>
    private static readonly RetailStartupClip Level100Intro = new(3095, 25, 1, 480, 300);

    [Fact]
    public void TheQuadIsTheMeasuredLetterboxedRectangle()
    {
        // The four logged xyzrhw positions: (0,40) (640,40) (640,440) (0,440).
        Assert.Equal(0f, RetailFmvPresentation.QuadLeft);
        Assert.Equal(40f, RetailFmvPresentation.QuadTop);
        Assert.Equal(640f, RetailFmvPresentation.QuadRight);
        Assert.Equal(440f, RetailFmvPresentation.QuadBottom);

        // Letterboxed, not full-screen: equal bars top and bottom of a 640x480
        // viewport, and 640x400 of it drawn.
        Assert.Equal(640f, RetailFmvPresentation.QuadWidth);
        Assert.Equal(400f, RetailFmvPresentation.QuadHeight);
        Assert.Equal(
            RetailFmvPresentation.QuadTop,
            RetailFmvPresentation.StageHeight - RetailFmvPresentation.QuadBottom);
    }

    [Fact]
    public void TheUvPairFixesTheDecodeSizeAtFourEightyByThreeHundred()
    {
        // t0 max was logged as (0.9375, 0.5859) against a 512x512 texture.
        Assert.Equal(0.9375f, RetailFmvPresentation.MaxU, 6);
        Assert.Equal(0.5859f, RetailFmvPresentation.MaxV, 4);

        Assert.Equal(512, RetailFmvPresentation.TextureSize);
        Assert.Equal(
            480f, RetailFmvPresentation.MaxU * RetailFmvPresentation.TextureSize, 4);
        Assert.Equal(
            300f, RetailFmvPresentation.MaxV * RetailFmvPresentation.TextureSize, 4);

        // 0.5859 is the log's four-decimal rendering of 300/512 = 0.5859375,
        // not a separate number. Pinning both directions stops a future edit
        // from "tidying" the literal into something that no longer divides.
        Assert.Equal(0.5859375f, RetailFmvPresentation.MaxV, 7);
    }

    [Fact]
    public void NothingIsStretched()
    {
        // 480x300 and 640x400 are both exactly 1.6, so the upscale is uniform
        // 1.3333x and the letterbox is a consequence of the source aspect
        // rather than a separate authored border.
        float source =
            RetailFmvPresentation.SourceWidth / (float)RetailFmvPresentation.SourceHeight;
        float drawn = RetailFmvPresentation.QuadWidth / RetailFmvPresentation.QuadHeight;

        Assert.Equal(1.6f, source, 6);
        Assert.Equal(source, drawn, 6);
        Assert.Equal(
            RetailFmvPresentation.QuadWidth / RetailFmvPresentation.SourceWidth,
            RetailFmvPresentation.QuadHeight / RetailFmvPresentation.SourceHeight,
            6);
    }

    [Fact]
    public void EveryDecodedClipMatchesTheSourceSizeTheUvsImply()
    {
        // If a decode is ever retargeted, the UVs above stop describing it.
        Assert.Equal(RetailFmvPresentation.SourceWidth, Level100Intro.Width);
        Assert.Equal(RetailFmvPresentation.SourceHeight, Level100Intro.Height);
    }

    [Fact]
    public void FullBrightnessIsTheMeasuredDiffuseAndIsNotWhite()
    {
        // Every vertex carried diff=0xFFFEFEFE. With stage 0 MODULATE that is
        // what full brightness multiplies by; rounding it to 0xFF would discard
        // the only direct evidence of retail's fade mechanism.
        Assert.Equal(0xFE, RetailFmvPresentation.FullBrightnessChannel);
        Assert.NotEqual(0xFF, RetailFmvPresentation.FullBrightnessChannel);
    }

    [Fact]
    public void TheDecoderIsDoubleBufferedAndAlternatesStrictly()
    {
        // frame 2 -> 0x0F220EE0, frame 3 -> 0x0F2214C0, frame 4 -> 0x0F220EE0 …
        // with no exception across 896 draws.
        Assert.Equal(2, RetailFmvPresentation.BufferCount);

        var seen = new HashSet<int>();
        int previous = RetailFmvPresentation.BufferIndexForFrame(0);
        seen.Add(previous);
        for (int frame = 1; frame < 3095; frame++)
        {
            int buffer = RetailFmvPresentation.BufferIndexForFrame(frame);
            Assert.NotEqual(previous, buffer);
            seen.Add(buffer);
            previous = buffer;
        }

        // Alternation over exactly two buffers, and never a third.
        Assert.Equal(RetailFmvPresentation.BufferCount, seen.Count);
        Assert.All(seen, buffer => Assert.InRange(buffer, 0, RetailFmvPresentation.BufferCount - 1));
    }

    [Fact]
    public void TheCutsceneScheduleIsOneClipWithNothingAroundIt()
    {
        RetailStartupSchedule schedule = RetailStartupSchedule.ForSingleClip(
            RetailStartupCue.Level100IntroCutscene,
            new Dictionary<RetailStartupCue, RetailStartupClip>
            {
                [RetailStartupCue.Level100IntroCutscene] = Level100Intro,
            });

        // ffprobe on cutscenes/01.vid reports exactly this duration.
        Assert.Equal(123.80, schedule.TotalSeconds, 2);
        Assert.Equal(123.80, Level100Intro.DurationSeconds, 2);
        Assert.Empty(schedule.MissingCues);

        // No splash, no inter-clip black, no other cue.
        Assert.Equal(RetailStartupCue.Level100IntroCutscene, schedule.Sample(0.0).Cue);
        Assert.Equal(RetailStartupFrameKind.Video, schedule.Sample(0.0).Kind);
        Assert.Equal(RetailStartupFrameKind.Video, schedule.Sample(123.0).Kind);
        Assert.Equal(RetailStartupFrameKind.Finished, schedule.Sample(123.80).Kind);
        Assert.Equal(3094, schedule.Sample(Level100Intro.DurationSeconds - 1e-6).FrameIndex);
    }

    [Fact]
    public void AnUndecodedCutsceneIsAbsentRatherThanPadded()
    {
        RetailStartupSchedule schedule = RetailStartupSchedule.ForSingleClip(
            RetailStartupCue.Level100IntroCutscene,
            new Dictionary<RetailStartupCue, RetailStartupClip>());

        Assert.True(schedule.IsEmpty);
        Assert.Equal(0d, schedule.TotalSeconds);
        Assert.Equal([RetailStartupCue.Level100IntroCutscene], schedule.MissingCues);
    }

    [Fact]
    public void TheCutsceneIsNotPartOfTheColdStartChain()
    {
        // RunIntroFMV is called from CGame::RestartLoopRunLevel, not from the
        // startup sequencer at 0x004efce3-0x004efee9. Handing the cue to the
        // cold-start schedule must therefore contribute nothing.
        var schedule = new RetailStartupSchedule(
            new Dictionary<RetailStartupCue, RetailStartupClip>
            {
                [RetailStartupCue.Level100IntroCutscene] = Level100Intro,
            },
            splashPresent: false);

        Assert.True(schedule.IsEmpty);
        Assert.Equal(0d, schedule.TotalSeconds);
    }

    [Fact]
    public void RetailsSkipFmvFlagSuppressesTheLevelCutsceneToo()
    {
        // CGame::GetIntroFMV returns -1 when CLIPARAMS.mSkipFMV is set
        // (references/Onslaught/game.cpp:1108-1109), so one flag suppresses
        // both the cold-start chain and the level cutscene.
        Assert.True(RetailStartupSchedule.IsSuppressedByArguments(["--skipfmv"]));
        Assert.False(RetailStartupSchedule.IsSuppressedByArguments([]));

        // --intro is ours and overrides every suppression, so a human or a
        // future rig can always force the movie on.
        Assert.False(RetailStartupSchedule.IsSuppressedByArguments(["--skipfmv", "--intro"]));

        // The frame-counted harnesses must never sit through 123.8 s of video.
        Assert.True(RetailStartupSchedule.IsSuppressedByArguments(["--smoke"]));
        Assert.True(RetailStartupSchedule.IsSuppressedByArguments(["--capture-dir=x"]));
        Assert.True(RetailStartupSchedule.IsSuppressedByArguments(["--capture-plan=x"]));
    }

    [Fact]
    public void TheCutsceneSitsBetweenLoadingAndGameplay()
    {
        RetailFrontendSession frontend = LoadedLevel100();

        Assert.Equal(RetailFrontendScreen.Loading, frontend.Screen);
        Assert.True(frontend.Level100IntroCutscenePending);

        frontend.BeginLevel100IntroCutscene();
        Assert.Equal(RetailFrontendScreen.IntroCutscene, frontend.Screen);

        frontend.CompleteLevel100IntroCutscene();
        Assert.Equal(RetailFrontendScreen.Gameplay, frontend.Screen);
    }

    [Fact]
    public void SuppressingTheCutsceneStillConsumesTheFirstRound()
    {
        RetailFrontendSession frontend = LoadedLevel100();

        frontend.CompleteLevel100Load();

        Assert.Equal(RetailFrontendScreen.Gameplay, frontend.Screen);
        Assert.False(frontend.Level100IntroCutscenePending);

        frontend.RestartLevel100();
        Assert.True(frontend.ConsumeLevel100LaunchRequest());
        Assert.Throws<InvalidOperationException>(frontend.BeginLevel100IntroCutscene);
    }

    [Fact]
    public void ARetryDoesNotReplayTheCutsceneButLeavingAndReenteringDoes()
    {
        // mFirstTimeRound: set TRUE when the level is entered
        // (references/Onslaught/game.cpp:1607) and FALSE at the bottom of each
        // restart-loop iteration (game.cpp:1691).
        RetailFrontendSession frontend = LoadedLevel100();
        frontend.BeginLevel100IntroCutscene();
        frontend.CompleteLevel100IntroCutscene();

        frontend.RestartLevel100();
        Assert.False(frontend.Level100IntroCutscenePending);
        Assert.True(frontend.ConsumeLevel100LaunchRequest());
        Assert.Throws<InvalidOperationException>(frontend.BeginLevel100IntroCutscene);

        // The Retry still reaches gameplay; it simply does so without a movie.
        frontend.CompleteLevel100Load();
        Assert.Equal(RetailFrontendScreen.Gameplay, frontend.Screen);

        // Leaving to the frontend ends the restart loop, so the next entry is a
        // first time round again.
        frontend.LeaveLevel100ForMainMenu();
        Assert.True(frontend.Level100IntroCutscenePending);
    }

    [Fact]
    public void TheCutsceneCannotStartBeforeTheLevelHasLoaded()
    {
        var frontend = new RetailFrontendSession();
        Assert.Throws<InvalidOperationException>(frontend.BeginLevel100IntroCutscene);
        Assert.Throws<InvalidOperationException>(frontend.CompleteLevel100IntroCutscene);

        // Reaching Loading is not enough: the launch request has to be consumed
        // first, which is what says the world is actually being built.
        for (int page = 0; page < PagesFromClickToStartToLoading; page++)
        {
            frontend.Confirm();
        }

        Assert.Equal(RetailFrontendScreen.Loading, frontend.Screen);
        Assert.Throws<InvalidOperationException>(frontend.BeginLevel100IntroCutscene);
    }

    /// <summary>
    /// Click-to-start, FEP_MAIN (New Game), CHOOSE GAME NAME, SELECT LEVEL,
    /// MISSION BRIEFING, SELECT CONFIGURATION — six confirmations reach LOADING.
    /// </summary>
    private const int PagesFromClickToStartToLoading = 6;

    /// <summary>
    /// Drives the released page chain to the point retail runs the intro FMV:
    /// click-to-start, main menu, CHOOSE GAME NAME, SELECT LEVEL, MISSION
    /// BRIEFING, SELECT CONFIGURATION, LOADING, world built.
    /// </summary>
    private static RetailFrontendSession LoadedLevel100()
    {
        var frontend = new RetailFrontendSession();
        for (int page = 0; page < PagesFromClickToStartToLoading; page++)
        {
            frontend.Confirm();
        }

        Assert.Equal(RetailFrontendScreen.Loading, frontend.Screen);
        Assert.True(frontend.ConsumeLevel100LaunchRequest());
        return frontend;
    }
}
