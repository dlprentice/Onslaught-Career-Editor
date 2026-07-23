// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using OnslaughtRebuild.GodotClient;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Client.Tests;

public sealed class Level100HudPresentationTests
{
    private const long OneCoreStepTicks = 333_334;
    private const uint Seed = 0x4F4E534Cu;

    [Fact]
    public void ProductMissionPathProjectsOrderedMessagesAndCanonicalObjectives()
    {
        var session = new InteractiveSession(
            Seed,
            Level100TestActorDefinitions.Create());
        var presentation = new Level100HudPresentationState();
        var requestedMessages = new List<Level100MessageRequested>();

        Consume(session.AdvanceFrameTicks(0));
        for (int tick = 0;
             tick < 1_100 &&
             !string.Equals(
                 session.CurrentSnapshot.Level100Mission.NavigationObjective,
                 "Target Zone 1",
                 StringComparison.Ordinal);
             tick++)
        {
            Consume(session.AdvanceFrameTicks(OneCoreStepTicks));
        }

        Assert.Equal(
            "Target Zone 1",
            session.CurrentSnapshot.Level100Mission.NavigationObjective);
        Level100MessageRequested playing = requestedMessages[^1];
        Level100HudSnapshot hud = presentation.Project(
            session.CurrentSnapshot,
            new Level100MessagePlaybackState(
                playing.SpeakerId,
                playing.MessageId,
                PositionSeconds: 0.25d,
                LengthSeconds: 1d,
                Playing: true,
                Paused: false));

        Assert.Equal(
            requestedMessages.Select(message =>
                (message.Tick, message.SpeakerId, message.MessageId)),
            hud.DeliveredMessages.Select(message =>
                (message.Tick, (int)message.Speaker, message.MessageId)));
        Assert.Equal(playing.MessageId, hud.ActiveMessage?.MessageId);
        Assert.Equal(playing.SpeakerId, (int?)hud.ActiveMessage?.Speaker);

        Level100ActorSnapshot[] canonicalObjectives =
            session.CurrentSnapshot.Level100Actors.Actors
                .Where(actor =>
                    actor.Active &&
                    actor.IsObjective &&
                    actor.Lifecycle != Level100ActorLifecycle.Destroyed)
                .ToArray();
        Assert.NotEmpty(canonicalObjectives);
        Assert.Equal(
            canonicalObjectives.Select(actor => actor.ActorId),
            hud.Objectives.Select(objective => objective.ActorId));
        Assert.Equal(
            canonicalObjectives.Select(actor => actor.Pose.PositionMillimeters),
            hud.Objectives.Select(objective => objective.PositionMillimeters));
        Assert.Equal(
            canonicalObjectives.Select(actor => actor.Name),
            hud.Objectives.Select(objective => objective.ThingName));

        Assert.Empty(hud.Contacts);
        Assert.Empty(hud.Threats);
        Assert.Empty(hud.DamageFlashes);
        Assert.Null(hud.Target);
        Assert.Null(hud.Weapon.SelectedWeapon);
        Assert.Null(hud.Weapon.PulseHeatPermille);
        Assert.Null(hud.Weapon.VulcanAmmo);
        Assert.False(hud.BattleLine.HasInfluenceValues);

        Level100ActorId removedObjective = canonicalObjectives[0].ActorId;
        FrameAdvanceResult destruction = session.AdvanceFrameTicks(
            OneCoreStepTicks,
            [new Level100ActorDiedFact(removedObjective)]);
        Consume(destruction);
        Level100HudSnapshot afterDestruction = presentation.Project(
            destruction.CurrentSnapshot,
            default);
        Assert.DoesNotContain(
            afterDestruction.Objectives,
            objective => objective.ActorId == removedObjective);

        void Consume(FrameAdvanceResult frame)
        {
            presentation.Consume(frame.Level100MissionEvents);
            requestedMessages.AddRange(
                frame.Level100MissionEvents.OfType<Level100MessageRequested>());
        }
    }

    [Fact]
    public void ProjectionPreservesRepeatedHelpAndRequiresPlaybackSpeakerIdentity()
    {
        var session = new InteractiveSession(
            Seed,
            Level100TestActorDefinitions.Create());
        var presentation = new Level100HudPresentationState();
        FrameAdvanceResult initial = session.AdvanceFrameTicks(0);
        Level100MessageRequested message = Assert.Single(
            initial.Level100MissionEvents.OfType<Level100MessageRequested>());
        presentation.Consume(initial.Level100MissionEvents);
        presentation.Consume(
        [
            new Level100HelpRequested(
                initial.CurrentSnapshot.Tick,
                (int)Level100HudHelpPrompt.Fire),
            new Level100HelpRequested(
                initial.CurrentSnapshot.Tick,
                (int)Level100HudHelpPrompt.Transform),
            new Level100HelpRequested(
                initial.CurrentSnapshot.Tick,
                (int)Level100HudHelpPrompt.Fire),
        ]);

        Level100HudSnapshot hud = presentation.Project(
            initial.CurrentSnapshot,
            new Level100MessagePlaybackState(
                ActiveSpeakerId: (int)Level100HudSpeaker.Kramer,
                ActiveMessageId: message.MessageId,
                PositionSeconds: 0d,
                LengthSeconds: 1d,
                Playing: true,
                Paused: false));

        Assert.Equal(
            [
                Level100HudHelpPrompt.Fire,
                Level100HudHelpPrompt.Transform,
                Level100HudHelpPrompt.Fire,
            ],
            hud.DeliveredHelp);
        Assert.Null(hud.ActiveMessage);
    }
}
