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
/// </summary>
public sealed class Level100MessageScheduleTests
{
    private const uint Seed = 0x4F4E534Cu;
    private const long OneCoreStepTicks = 333_334;

    /// <summary>
    /// <paramref name="ticks"/> is the wanted ON-SCREEN length. Core's event
    /// carries a SCRIPT WAIT duration, which is the voice length plus an
    /// 18-tick post-roll, so the fixture adds the post-roll back on and the
    /// schedule subtracts it again.
    /// </summary>
    private static Level100HudMessageDeliverySnapshot Delivery(
        int tick,
        int messageId,
        int ticks) =>
        new(
            tick,
            Level100HudSpeaker.Tatiana,
            messageId,
            ScriptWaitsForDuration: false,
            ticks + Level100MessageSchedule.VoiceWaitPostRollTicks);

    [Fact]
    public void AMessageRequestedWithNothingPlayingStartsOnItsRequestTick()
    {
        Level100HudMessageDeliverySnapshot[] deliveries =
            [Delivery(tick: 40, messageId: 1, ticks: 60)];

        Assert.Null(Level100MessageSchedule.ActiveAt(deliveries, 39));
        Level100MessageScheduleEntry? first =
            Level100MessageSchedule.ActiveAt(deliveries, 40);
        Assert.NotNull(first);
        Assert.Equal(40, first!.Value.StartTick);
        Assert.Equal(0, first.Value.ElapsedTicksAt(40));
        Assert.Equal(59, first.Value.ElapsedTicksAt(99));

        // Half-open window: the last tick of the message is 99, and 100 is a gap.
        Assert.NotNull(Level100MessageSchedule.ActiveAt(deliveries, 99));
        Assert.Null(Level100MessageSchedule.ActiveAt(deliveries, 100));
    }

    [Fact]
    public void AMessageRequestedWhileAnotherIsSpeakingWaitsOutTheHandoff()
    {
        // The second is requested at tick 50, ten ticks into the first. The
        // audio adapter queues it and only starts it 0.3 s after the first
        // voice's Finished signal, so the schedule must do the same.
        Level100HudMessageDeliverySnapshot[] deliveries =
        [
            Delivery(tick: 40, messageId: 1, ticks: 60),
            Delivery(tick: 50, messageId: 2, ticks: 30),
        ];

        Assert.Equal(
            1,
            Level100MessageSchedule.ActiveAt(deliveries, 99)!.Value.Delivery.MessageId);

        // Ticks 100..108 are the handoff gap; nothing is on screen.
        for (int tick = 100; tick < 100 + Level100MessageSchedule.HandoffTicks; tick++)
        {
            Assert.Null(Level100MessageSchedule.ActiveAt(deliveries, tick));
        }

        Level100MessageScheduleEntry? second =
            Level100MessageSchedule.ActiveAt(deliveries, 109);
        Assert.NotNull(second);
        Assert.Equal(2, second!.Value.Delivery.MessageId);
        Assert.Equal(100 + Level100MessageSchedule.HandoffTicks, second.Value.StartTick);
        Assert.Null(Level100MessageSchedule.ActiveAt(deliveries, 139));
    }

    [Fact]
    public void AMessageRequestedInsideTheHandoffGapStillWaitsForIt()
    {
        // Requested at 104, i.e. after the first ended (100) but during the
        // handoff the Finished handler armed. The adapter's
        // QueueCharacterMessage refuses to start while
        // _characterMessageHandoffSecondsRemaining > 0, so the third message
        // here must not jump the gap either. Deliveries 1 and 2 set the gap up;
        // 3 is the one under test.
        Level100HudMessageDeliverySnapshot[] deliveries =
        [
            Delivery(tick: 40, messageId: 1, ticks: 60),
            Delivery(tick: 50, messageId: 2, ticks: 30),
            Delivery(tick: 104, messageId: 3, ticks: 20),
        ];

        // #2 runs 109..138 inclusive and ends at 139, so #3 starts one handoff
        // after that - it does NOT jump into the gap it was requested during.
        Assert.Null(Level100MessageSchedule.ActiveAt(deliveries, 139));
        Level100MessageScheduleEntry? third = Level100MessageSchedule.ActiveAt(
            deliveries,
            139 + Level100MessageSchedule.HandoffTicks);
        Assert.NotNull(third);
        Assert.Equal(3, third!.Value.Delivery.MessageId);
        Assert.Equal(139 + Level100MessageSchedule.HandoffTicks, third.Value.StartTick);
    }

    [Fact]
    public void AMessageRequestedAfterEverythingEndedStartsImmediately()
    {
        // A genuine gap: nothing was queued when the first ended, so the
        // Finished handler armed no handoff and the second starts on its own
        // request tick with no delay.
        Level100HudMessageDeliverySnapshot[] deliveries =
        [
            Delivery(tick: 40, messageId: 1, ticks: 60),
            Delivery(tick: 400, messageId: 2, ticks: 30),
        ];

        Assert.Null(Level100MessageSchedule.ActiveAt(deliveries, 399));
        Assert.Equal(
            400,
            Level100MessageSchedule.ActiveAt(deliveries, 400)!.Value.StartTick);
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

    [Fact]
    public void TheDisplayWindowIsTheVoiceLengthAndNotTheScriptWait()
    {
        // Measured off the shipped Ogg granules, all 43 catalogued messages
        // that have a Level100MissionTiming.MessagePlaybackTicks entry:
        //   ExpectedPlaybackTicks - 30 * oggSeconds = 18.03
        //   (min 17.55, max 18.42; every one rounds to 18)
        // e.g. HUD_01 169 ticks / 5.029 s, HUD_02 210 / 6.399 s.
        // The table is a SCRIPT WAIT duration. The panel and the portrait were
        // previously on screen exactly while AudioStreamPlayer.Playing was
        // true - the voice length - so the schedule must subtract the post-roll
        // or it silently extends every message by 0.6 s and delays every queued
        // successor by the same.
        Assert.Equal(18, Level100MessageSchedule.VoiceWaitPostRollTicks);

        var delivery = new Level100HudMessageDeliverySnapshot(
            Tick: 0,
            Level100HudSpeaker.Tatiana,
            MessageId: 292_562,
            ScriptWaitsForDuration: true,
            ExpectedPlaybackTicks: 169);
        Assert.Equal(151, Level100MessageSchedule.DisplayTicks(delivery));

        // Degenerate entries clamp rather than going negative or zero-length.
        Assert.Equal(
            1,
            Level100MessageSchedule.DisplayTicks(delivery with { ExpectedPlaybackTicks = 3 }));
    }

    [Fact]
    public void TheHandoffIsThreeTenthsOfASecondInCoreTicks()
    {
        // Level100Audio.RetailCharacterMessageHandoffSeconds = 0.3, from
        // CMessageBox__AdvanceRevealAndScheduleNextTick (0x004b8020) scheduling
        // event 0xbba with the immediate 0x3e99999a = 0.30f. Written in seconds
        // so a Core tick-rate change keeps its meaning.
        Assert.Equal(
            (3 * SimulationConstants.TicksPerSecond) / 10,
            Level100MessageSchedule.HandoffTicks);
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
        for (int step = 0; step < 600; step++)
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
