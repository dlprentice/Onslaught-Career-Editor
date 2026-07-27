// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.GodotClient;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// The message schedule is the HUD's clock. It exists because the previous
/// clock - <c>AudioStreamPlayer.GetPlaybackPosition()</c>, reached through
/// <c>Level100MessagePlaybackState.PositionSeconds</c> - is the audio mixer's
/// WALL clock, while every capture this project scores against is keyed on Core
/// ticks. Measured cost of that mismatch, two captures of the same commit:
/// message panel 21.28 % material / meanD 16.5 and portrait/compass 25.15 % /
/// 5.0, against 0.00 % on five other regions and retail's own 0.02 % floor.
/// After the change the same pair is byte-identical on all 92 frames.
///
/// <para><b>Who owns the schedule changed, and these tests changed with it.</b>
/// This type used to reconstruct the message-box queue on the client, from
/// request ticks, with a 0.3 s handoff and an 18-tick post-roll subtracted off
/// every duration. Core now owns the released message box outright
/// (<c>Level100MissionTiming.MessageBoxAllowedTick</c> and
/// <c>MessageAdvanceDelayTicks</c>) and holds each event back to the tick the
/// message actually becomes active, so the delivery tick IS the start tick and
/// the duration IS the shipped table entry. The tests that asserted the client
/// side of the old reconstruction are gone because the behaviour they pinned is
/// refuted, not because they were inconvenient.</para>
/// </summary>
public sealed class Level100MessageScheduleTests
{
    private const uint Seed = 0x4F4E534Cu;
    private const long OneCoreStepTicks = 333_334;

    private static Level100HudMessageDeliverySnapshot Delivery(
        int tick,
        int messageId,
        int ticks) =>
        new(
            tick,
            Level100HudSpeaker.Tatiana,
            messageId,
            ScriptWaitsForDuration: false,
            ticks);

    [Fact]
    public void ADeliveryIsOnScreenFromItsOwnTickForItsOwnDuration()
    {
        Level100HudMessageDeliverySnapshot[] deliveries =
            [Delivery(tick: 40, messageId: 1, ticks: 60)];

        Assert.Null(Level100MessageSchedule.ActiveAt(deliveries, 39));
        Level100MessageScheduleEntry? first =
            Level100MessageSchedule.ActiveAt(deliveries, 40);
        Assert.NotNull(first);
        Assert.Equal(40, first!.Value.StartTick);
        Assert.Equal(60, first.Value.DurationTicks);
        Assert.Equal(0, first.Value.ElapsedTicksAt(40));
        Assert.Equal(59, first.Value.ElapsedTicksAt(99));

        // Half-open window: the last tick of the message is 99, and 100 is a gap.
        Assert.NotNull(Level100MessageSchedule.ActiveAt(deliveries, 99));
        Assert.Null(Level100MessageSchedule.ActiveAt(deliveries, 100));
    }

    [Fact]
    public void ConsecutiveDeliveriesShowTheGapCoreScheduledAndNothingElse()
    {
        // Core has already applied MessageAdvanceDelayTicks; the HUD does not
        // reapply it, and it must not invent one of its own either.
        Level100HudMessageDeliverySnapshot[] deliveries =
        [
            Delivery(tick: 40, messageId: 1, ticks: 60),
            Delivery(
                tick: 100 + Level100MissionTiming.MessageAdvanceDelayTicks,
                messageId: 2,
                ticks: 30),
        ];

        Assert.Equal(
            1,
            Level100MessageSchedule.ActiveAt(deliveries, 99)!.Value.Delivery.MessageId);
        for (int tick = 100;
             tick < 100 + Level100MissionTiming.MessageAdvanceDelayTicks;
             tick++)
        {
            Assert.Null(Level100MessageSchedule.ActiveAt(deliveries, tick));
        }

        Level100MessageScheduleEntry? second = Level100MessageSchedule.ActiveAt(
            deliveries,
            100 + Level100MissionTiming.MessageAdvanceDelayTicks);
        Assert.NotNull(second);
        Assert.Equal(2, second!.Value.Delivery.MessageId);
    }

    [Fact]
    public void ElapsedSecondsIsTicksOverTheCoreRateAndIsClamped()
    {
        Level100HudMessageDeliverySnapshot[] deliveries =
            [Delivery(tick: 0, messageId: 1, ticks: SimulationConstants.TicksPerSecond)];
        Level100MessageScheduleEntry entry =
            Level100MessageSchedule.ActiveAt(deliveries, 0)!.Value;

        Assert.Equal(1d, entry.DurationSeconds);
        Assert.Equal(0d, entry.ElapsedSecondsAt(0));
        Assert.Equal(
            0.5d,
            entry.ElapsedSecondsAt(SimulationConstants.TicksPerSecond / 2),
            6);
        // Never negative, never past the end, whatever tick it is asked about.
        Assert.Equal(0d, entry.ElapsedSecondsAt(-100));
        Assert.Equal(1d, entry.ElapsedSecondsAt(10_000));
    }

    /// <summary>
    /// The display window is the whole shipped table entry, and the 18-tick
    /// offset in that table is NOT subtracted.
    /// </summary>
    /// <remarks>
    /// The arithmetic behind the old subtraction is not in dispute: measured
    /// off the shipped Ogg granules, all 43 catalogued messages give
    /// <c>ExpectedPlaybackTicks - 30 * oggSeconds = 18.03</c> (min 17.55, max
    /// 18.42). The INTERPRETATION was wrong. Retail activates the message
    /// before the voice starts (<c>CMessageBox__TryAdvanceQueuedMessage</c>
    /// <c>0x004b7b80</c>, 0.2 s) and retains it through the completion hold
    /// (<c>CMessageBox__AdvanceRevealAndScheduleNextTick</c> <c>0x004b8020</c>,
    /// 0.3 s), so subtracting the 18 reproduced the old
    /// <c>AudioStreamPlayer.Playing</c> window - voice only - rather than
    /// retail's. The eight retail boundaries measured in
    /// <c>rebuild/PROVENANCE.md</c> span exactly the table entries to within
    /// the 50 ms sampler.
    /// </remarks>
    [Fact]
    public void TheDisplayWindowIsTheWholeShippedTableEntry()
    {
        var delivery = new Level100HudMessageDeliverySnapshot(
            Tick: 0,
            Level100HudSpeaker.Tatiana,
            MessageId: 292_562,
            ScriptWaitsForDuration: true,
            ExpectedPlaybackTicks: 169);
        Assert.Equal(169, Level100MessageSchedule.DisplayTicks(delivery));

        // Degenerate entries clamp rather than going negative or zero-length.
        Assert.Equal(
            1,
            Level100MessageSchedule.DisplayTicks(delivery with { ExpectedPlaybackTicks = 0 }));
    }

    [Fact]
    public void TheGreetingIsOnScreenAfterTheOpeningPanAndNotBehindIt()
    {
        // The reported defect: "no greeting". HUD_01 was delivered on Core tick
        // 0 and was over before the HUD appeared, because CPanCamera's
        // GetShowHUD is false for the whole six-second pan.
        var session = new InteractiveSession(
            Seed,
            Level100TestActorDefinitions.Create());
        var presentation = new Level100HudPresentationState();

        FrameAdvanceResult frame = session.AdvanceFrameTicks(0);
        presentation.Consume(frame.Level100MissionEvents);
        var greetingTicks = new List<int>();
        for (int step = 0; step < 600; step++)
        {
            frame = session.AdvanceFrameTicks(OneCoreStepTicks);
            presentation.Consume(frame.Level100MissionEvents);
            Level100HudSnapshot hud = presentation.Project(frame.CurrentSnapshot, default);
            if (hud.ActiveMessage?.MessageId == 292_562)
            {
                greetingTicks.Add(frame.CurrentSnapshot.Level100Mission.Tick);
            }
        }

        Assert.NotEmpty(greetingTicks);
        Assert.Equal(Level100MissionTiming.MessageBoxAllowedTick, greetingTicks[0]);
        Assert.True(
            greetingTicks[0] >= SimulationConstants.Level100OpeningPanTicks,
            "the greeting must not be spent behind the opening pan");
        Assert.Equal(169, greetingTicks.Count);
    }

    [Fact]
    public void TheActiveMessageIsAFunctionOfTheCoreTickAloneOnTheProductPath()
    {
        // The property that makes the capture instrument trustworthy: replay
        // the real mission and, at every tick, confirm the projection's active
        // message is exactly what the tick schedule says - and that it does not
        // move when the mixer state handed in is varied.
        var session = new InteractiveSession(
            Seed,
            Level100TestActorDefinitions.Create());
        var presentation = new Level100HudPresentationState();

        FrameAdvanceResult frame = session.AdvanceFrameTicks(0);
        presentation.Consume(frame.Level100MissionEvents);
        int observedActive = 0;
        for (int step = 0; step < 900; step++)
        {
            frame = session.AdvanceFrameTicks(OneCoreStepTicks);
            presentation.Consume(frame.Level100MissionEvents);

            Level100HudSnapshot silent = presentation.Project(
                frame.CurrentSnapshot,
                default);
            Level100HudSnapshot noisy = presentation.Project(
                frame.CurrentSnapshot,
                new Level100MessagePlaybackState(
                    ActiveSpeakerId: (int)Level100HudSpeaker.Kramer,
                    ActiveMessageId: 292562,
                    PositionSeconds: 3.5d,
                    LengthSeconds: 4d,
                    Playing: true,
                    Paused: false));

            Assert.Equal(
                silent.ActiveMessage?.MessageId,
                noisy.ActiveMessage?.MessageId);
            Assert.Equal(
                Level100MessageSchedule
                    .ActiveAt(
                        silent.DeliveredMessages,
                        frame.CurrentSnapshot.Level100Mission.Tick)
                    ?.Delivery.MessageId,
                silent.ActiveMessage?.MessageId);
            if (silent.ActiveMessage is not null)
            {
                observedActive++;
            }
        }

        // The replay has to actually exercise the path, or the assertions above
        // are vacuous.
        Assert.True(observedActive > 100, $"only {observedActive} active ticks");
    }
}
