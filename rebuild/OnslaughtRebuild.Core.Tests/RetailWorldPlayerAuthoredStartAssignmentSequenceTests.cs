// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Core.Tests;

public sealed class RetailWorldPlayerAuthoredStartAssignmentSequenceTests
{
    private const int Player = 1001;
    private const int OtherPlayer = 1002;
    private const int OldEngine = 1999;
    private const int EngineFirst = 2001;
    private const int EngineFinal = 2002;
    private const int PlayerEngineCell = 3001;
    private const int EngineFirstPlayerCell = 4001;
    private const int EngineFinalPlayerCell = 4002;

    [Fact]
    public void EveryMatchingStartAssignsInOrderAndFinalEngineRemainsPlayerTarget()
    {
        RetailWorldPlayerStartRecord first = Start("synthetic:start:first");
        RetailWorldPlayerStartRecord final = Start("synthetic:start:final");
        RetailWorldPlayerStartResolution resolution = Resolution(first, final);
        var bindings = new[]
        {
            Binding(first, EngineFirst, EngineFirstPlayerCell),
            Binding(final, EngineFinal, EngineFinalPlayerCell),
        };
        RetailActiveReaderGraph graph = GraphWithBothEngineCells();

        RetailWorldPlayerAuthoredStartAssignmentSequenceResult result =
            RetailWorldPlayerAuthoredStartAssignmentSequence.Assign(
                graph,
                resolution,
                Player,
                PlayerEngineCell,
                playerGodWord: 0,
                bindings);

        Assert.Collection(
            result.Assignments,
            step =>
            {
                Assert.Same(first, step.AuthoredStart);
                Assert.Equal(bindings[0], step.Binding);
                Assert.Equal(2, step.Assignment.Calls.Count);
            },
            step =>
            {
                Assert.Same(final, step.AuthoredStart);
                Assert.Equal(bindings[1], step.Binding);
                Assert.Equal(2, step.Assignment.Calls.Count);
            });
        Assert.Equal(EngineFinal, graph.TargetOf(PlayerEngineCell));
        Assert.Equal(Player, graph.TargetOf(EngineFirstPlayerCell));
        Assert.Equal(Player, graph.TargetOf(EngineFinalPlayerCell));
        Assert.Equal(
            [EngineFinalPlayerCell, EngineFirstPlayerCell],
            graph.ReadersNewestFirst(Player));
    }

    [Fact]
    public void LateMissingReaderCellRejectsBeforeFirstAssignmentMutation()
    {
        RetailWorldPlayerStartRecord first = Start("synthetic:start:first");
        RetailWorldPlayerStartRecord final = Start("synthetic:start:final");
        RetailWorldPlayerStartResolution resolution = Resolution(first, final);
        var graph = new RetailActiveReaderGraph();
        graph.CreateReaderCell(PlayerEngineCell, OldEngine);
        graph.CreateReaderCell(EngineFirstPlayerCell, OtherPlayer);
        int[] oldEngineReadersBefore = graph.ReadersNewestFirst(OldEngine);
        int[] otherPlayerReadersBefore = graph.ReadersNewestFirst(OtherPlayer);

        Assert.Throws<ArgumentException>(() =>
            RetailWorldPlayerAuthoredStartAssignmentSequence.Assign(
                graph,
                resolution,
                Player,
                PlayerEngineCell,
                playerGodWord: 0,
                [
                    Binding(first, EngineFirst, EngineFirstPlayerCell),
                    Binding(final, EngineFinal, EngineFinalPlayerCell),
                ]));

        Assert.Equal(OldEngine, graph.TargetOf(PlayerEngineCell));
        Assert.Equal(OtherPlayer, graph.TargetOf(EngineFirstPlayerCell));
        Assert.Equal(oldEngineReadersBefore, graph.ReadersNewestFirst(OldEngine));
        Assert.Equal(
            otherPlayerReadersBefore,
            graph.ReadersNewestFirst(OtherPlayer));
    }

    [Fact]
    public void MisorderedBindingRejectsBeforeFirstAssignmentMutation()
    {
        RetailWorldPlayerStartRecord first = Start("synthetic:start:first");
        RetailWorldPlayerStartRecord final = Start("synthetic:start:final");
        RetailWorldPlayerStartResolution resolution = Resolution(first, final);
        RetailActiveReaderGraph graph = GraphWithBothEngineCells();

        Assert.Throws<ArgumentException>(() =>
            RetailWorldPlayerAuthoredStartAssignmentSequence.Assign(
                graph,
                resolution,
                Player,
                PlayerEngineCell,
                playerGodWord: 0,
                [
                    Binding(final, EngineFinal, EngineFinalPlayerCell),
                    Binding(first, EngineFirst, EngineFirstPlayerCell),
                ]));

        Assert.Equal(OldEngine, graph.TargetOf(PlayerEngineCell));
        Assert.Null(graph.TargetOf(EngineFirstPlayerCell));
        Assert.Null(graph.TargetOf(EngineFinalPlayerCell));
    }

    [Fact]
    public void LateMismatchedBindingRejectsBeforeFirstAssignmentMutation()
    {
        RetailWorldPlayerStartRecord first = Start("synthetic:start:first");
        RetailWorldPlayerStartRecord final = Start("synthetic:start:final");
        RetailWorldPlayerStartResolution resolution = Resolution(first, final);
        RetailActiveReaderGraph graph = GraphWithBothEngineCells();
        int[] oldEngineReadersBefore = graph.ReadersNewestFirst(OldEngine);

        Assert.Throws<ArgumentException>(() =>
            RetailWorldPlayerAuthoredStartAssignmentSequence.Assign(
                graph,
                resolution,
                Player,
                PlayerEngineCell,
                playerGodWord: 0,
                [
                    Binding(first, EngineFirst, EngineFirstPlayerCell),
                    new(
                        "synthetic:start:not-final",
                        EngineFinal,
                        EngineFinalPlayerCell),
                ]));

        Assert.Equal(OldEngine, graph.TargetOf(PlayerEngineCell));
        Assert.Null(graph.TargetOf(EngineFirstPlayerCell));
        Assert.Null(graph.TargetOf(EngineFinalPlayerCell));
        Assert.Equal(oldEngineReadersBefore, graph.ReadersNewestFirst(OldEngine));
    }

    [Fact]
    public void LatePlayerReaderCellAliasRejectsBeforeFirstAssignmentMutation()
    {
        RetailWorldPlayerStartRecord first = Start("synthetic:start:first");
        RetailWorldPlayerStartRecord final = Start("synthetic:start:final");
        RetailWorldPlayerStartResolution resolution = Resolution(first, final);
        RetailActiveReaderGraph graph = GraphWithBothEngineCells();
        int[] oldEngineReadersBefore = graph.ReadersNewestFirst(OldEngine);

        Assert.Throws<ArgumentException>(() =>
            RetailWorldPlayerAuthoredStartAssignmentSequence.Assign(
                graph,
                resolution,
                Player,
                PlayerEngineCell,
                playerGodWord: 0,
                [
                    Binding(first, EngineFirst, EngineFirstPlayerCell),
                    Binding(final, EngineFinal, PlayerEngineCell),
                ]));

        Assert.Equal(OldEngine, graph.TargetOf(PlayerEngineCell));
        Assert.Null(graph.TargetOf(EngineFirstPlayerCell));
        Assert.Null(graph.TargetOf(EngineFinalPlayerCell));
        Assert.Equal(oldEngineReadersBefore, graph.ReadersNewestFirst(OldEngine));
    }

    [Fact]
    public void SameEngineWithDifferentReaderCellsRejectsBeforeMutation()
    {
        RetailWorldPlayerStartRecord first = Start("synthetic:start:first");
        RetailWorldPlayerStartRecord final = Start("synthetic:start:final");
        RetailWorldPlayerStartResolution resolution = Resolution(first, final);
        RetailActiveReaderGraph graph = GraphWithBothEngineCells();

        Assert.Throws<ArgumentException>(() =>
            RetailWorldPlayerAuthoredStartAssignmentSequence.Assign(
                graph,
                resolution,
                Player,
                PlayerEngineCell,
                playerGodWord: 0,
                [
                    Binding(first, EngineFirst, EngineFirstPlayerCell),
                    Binding(final, EngineFirst, EngineFinalPlayerCell),
                ]));

        Assert.Equal(OldEngine, graph.TargetOf(PlayerEngineCell));
        Assert.Null(graph.TargetOf(EngineFirstPlayerCell));
        Assert.Null(graph.TargetOf(EngineFinalPlayerCell));
    }

    [Fact]
    public void SameReaderCellWithDifferentEnginesRejectsBeforeMutation()
    {
        RetailWorldPlayerStartRecord first = Start("synthetic:start:first");
        RetailWorldPlayerStartRecord final = Start("synthetic:start:final");
        RetailWorldPlayerStartResolution resolution = Resolution(first, final);
        RetailActiveReaderGraph graph = GraphWithBothEngineCells();

        Assert.Throws<ArgumentException>(() =>
            RetailWorldPlayerAuthoredStartAssignmentSequence.Assign(
                graph,
                resolution,
                Player,
                PlayerEngineCell,
                playerGodWord: 0,
                [
                    Binding(first, EngineFirst, EngineFirstPlayerCell),
                    Binding(final, EngineFinal, EngineFirstPlayerCell),
                ]));

        Assert.Equal(OldEngine, graph.TargetOf(PlayerEngineCell));
        Assert.Null(graph.TargetOf(EngineFirstPlayerCell));
        Assert.Null(graph.TargetOf(EngineFinalPlayerCell));
    }

    [Fact]
    public void ExactRepeatedEngineTupleStillProducesOneStepPerMatchingStart()
    {
        RetailWorldPlayerStartRecord first = Start("synthetic:start:first");
        RetailWorldPlayerStartRecord final = Start("synthetic:start:final");
        RetailWorldPlayerStartResolution resolution = Resolution(first, final);
        var graph = new RetailActiveReaderGraph();
        graph.CreateReaderCell(PlayerEngineCell);
        graph.CreateReaderCell(EngineFirstPlayerCell);

        RetailWorldPlayerAuthoredStartAssignmentSequenceResult result =
            RetailWorldPlayerAuthoredStartAssignmentSequence.Assign(
                graph,
                resolution,
                Player,
                PlayerEngineCell,
                playerGodWord: 0,
                [
                    Binding(first, EngineFirst, EngineFirstPlayerCell),
                    Binding(final, EngineFirst, EngineFirstPlayerCell),
                ]);

        Assert.Collection(
            result.Assignments,
            firstStep =>
            {
                Assert.Same(first, firstStep.AuthoredStart);
                Assert.All(
                    firstStep.Assignment.Calls,
                    call => Assert.NotEmpty(call.ReaderActions));
            },
            finalStep =>
            {
                Assert.Same(final, finalStep.AuthoredStart);
                Assert.All(
                    finalStep.Assignment.Calls,
                    call => Assert.Empty(call.ReaderActions));
            });
        Assert.Equal(EngineFirst, graph.TargetOf(PlayerEngineCell));
        Assert.Equal(Player, graph.TargetOf(EngineFirstPlayerCell));
    }

    [Fact]
    public void NonzeroGodWordEmitsBothPolicyIntentsForEveryMatchedStart()
    {
        RetailWorldPlayerStartRecord first = Start("synthetic:start:first");
        RetailWorldPlayerStartRecord final = Start("synthetic:start:final");
        RetailWorldPlayerStartResolution resolution = Resolution(first, final);
        RetailActiveReaderGraph graph = GraphWithBothEngineCells();

        RetailWorldPlayerAuthoredStartAssignmentSequenceResult result =
            RetailWorldPlayerAuthoredStartAssignmentSequence.Assign(
                graph,
                resolution,
                Player,
                PlayerEngineCell,
                playerGodWord: 1,
                [
                    Binding(first, EngineFirst, EngineFirstPlayerCell),
                    Binding(final, EngineFinal, EngineFinalPlayerCell),
                ]);

        Assert.Collection(
            result.Assignments,
            firstStep => AssertGodCalls(firstStep, EngineFirst),
            finalStep => AssertGodCalls(finalStep, EngineFinal));
    }

    [Fact]
    public void ExactWorld110PlayerOneAssignsTheWresRlwd0001Binding()
    {
        RetailWorldPlayerStartProjection projection =
            RetailWorldPlayerStartAdmission.Admit(
                RetailWorld110LevelActors.WorldNumber,
                RetailWorld110LevelActors.ArchiveIdentity,
                RetailWorld110LevelActors.AuthoredPlayerStarts);
        RetailWorldPlayerStartResolution resolution = projection.ResolveForPlayer(1);
        RetailWorldPlayerStartRecord exactStart = Assert.Single(projection.Starts);
        var graph = new RetailActiveReaderGraph();
        graph.CreateReaderCell(PlayerEngineCell);
        graph.CreateReaderCell(EngineFirstPlayerCell);

        RetailWorldPlayerAuthoredStartAssignmentSequenceResult result =
            RetailWorldPlayerAuthoredStartAssignmentSequence.Assign(
                graph,
                resolution,
                Player,
                PlayerEngineCell,
                playerGodWord: 0,
                [Binding(exactStart, EngineFirst, EngineFirstPlayerCell)]);

        RetailWorldPlayerAuthoredStartAssignmentStep step =
            Assert.Single(result.Assignments);
        Assert.Same(exactStart, step.AuthoredStart);
        Assert.Equal("wres:rlwd:0001", step.Binding.StartObjectIdentity);
        Assert.Equal(EngineFirst, graph.TargetOf(PlayerEngineCell));
        Assert.Equal(Player, graph.TargetOf(EngineFirstPlayerCell));
    }

    [Fact]
    public void CallerBindingCollectionAndReturnedStepsAreDeeplyImmutable()
    {
        RetailWorldPlayerStartRecord start = Start("synthetic:start:only");
        RetailWorldPlayerStartResolution resolution = Resolution(start);
        RetailWorldPlayerAuthoredStartEngineBinding original =
            Binding(start, EngineFirst, EngineFirstPlayerCell);
        var callerBindings = new List<RetailWorldPlayerAuthoredStartEngineBinding>
        {
            original,
        };
        var graph = new RetailActiveReaderGraph();
        graph.CreateReaderCell(PlayerEngineCell);
        graph.CreateReaderCell(EngineFirstPlayerCell);

        RetailWorldPlayerAuthoredStartAssignmentSequenceResult result =
            RetailWorldPlayerAuthoredStartAssignmentSequence.Assign(
                graph,
                resolution,
                Player,
                PlayerEngineCell,
                playerGodWord: 0,
                callerBindings);

        callerBindings[0] = Binding(start, EngineFinal, EngineFinalPlayerCell);
        callerBindings.Clear();

        RetailWorldPlayerAuthoredStartAssignmentStep step =
            Assert.Single(result.Assignments);
        Assert.Equal(original, step.Binding);
        Assert.Same(start, step.AuthoredStart);

        IList<RetailWorldPlayerAuthoredStartAssignmentStep> assignments =
            (IList<RetailWorldPlayerAuthoredStartAssignmentStep>)result.Assignments;
        Assert.True(assignments.IsReadOnly);
        Assert.Throws<NotSupportedException>(() => assignments.Clear());

        IList<RetailPlayerBattleEngineAssignmentCall> nestedCalls =
            (IList<RetailPlayerBattleEngineAssignmentCall>)step.Assignment.Calls;
        Assert.True(nestedCalls.IsReadOnly);
        Assert.Throws<NotSupportedException>(() => nestedCalls.Clear());
    }

    private static RetailActiveReaderGraph GraphWithBothEngineCells()
    {
        var graph = new RetailActiveReaderGraph();
        graph.CreateReaderCell(PlayerEngineCell, OldEngine);
        graph.CreateReaderCell(EngineFirstPlayerCell);
        graph.CreateReaderCell(EngineFinalPlayerCell);
        return graph;
    }

    private static void AssertGodCalls(
        RetailWorldPlayerAuthoredStartAssignmentStep step,
        int expectedEngineIdentity)
    {
        Assert.Collection(
            step.Assignment.Calls,
            call => Assert.Equal(
                RetailPlayerBattleEngineAssignmentCallKind.SetPlayerBattleEngineReader,
                call.Kind),
            call => Assert.Equal(
                RetailPlayerBattleEngineAssignmentCallKind.SetBattleEnginePlayerReader,
                call.Kind),
            call =>
            {
                Assert.Equal(
                    RetailPlayerBattleEngineAssignmentCallKind.SetVulnerable,
                    call.Kind);
                Assert.Equal(expectedEngineIdentity, call.ReceiverIdentity);
                Assert.Equal(0, call.RawBooleanArgument);
            },
            call =>
            {
                Assert.Equal(
                    RetailPlayerBattleEngineAssignmentCallKind.SetInfiniteEnergy,
                    call.Kind);
                Assert.Equal(expectedEngineIdentity, call.ReceiverIdentity);
                Assert.Equal(1, call.RawBooleanArgument);
            });
    }

    private static RetailWorldPlayerAuthoredStartEngineBinding Binding(
        RetailWorldPlayerStartRecord start,
        int engineIdentity,
        int enginePlayerReaderCellIdentity) =>
        new(
            start.ObjectIdentity,
            engineIdentity,
            enginePlayerReaderCellIdentity);

    private static RetailWorldPlayerStartResolution Resolution(
        params RetailWorldPlayerStartRecord[] starts) =>
        RetailWorldPlayerStartResolution.FromOrderedMatches(starts);

    private static RetailWorldPlayerStartRecord Start(string objectIdentity) =>
        new(
            objectIdentity,
            ThingType: 15,
            SerializedByteLength: 59,
            SerializedSha256:
                "850de203b32b967064f3a9bacca24bebd783af68760a8b4c056ea242a2b47dfc",
            PositionXBits: 0x43846000,
            PositionYBits: 0x43816800,
            PositionZBits: unchecked((int)0x80000000),
            OrientationXBits: unchecked((int)0xbf04fd8b),
            OrientationYBits: 0,
            OrientationZBits: 0,
            PlaneMode: 0,
            PlayerNumber: 1);
}
