// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Core.Tests;

/// <summary>
/// The check that did not exist, and whose absence let a corrected retail table
/// and a stale test fixture disagree silently.
/// </summary>
/// <remarks>
/// <para>
/// <c>rebuild/TestSupport/Level100TestActorDefinitions.cs</c> transcribes the
/// released waypoint routes by hand so that Core-only tests need no engine and
/// no asset load. Nothing compared that transcription to the manifest the
/// product actually consumes, so it drifted twice:
/// </para>
/// <list type="number">
///   <item><c>Target Tank Path 1</c> was a synthetic triple 610 m out at
///   exactly 45 degrees until 2026-07-26, which made tutorial beat 3
///   unreachable in Core;</item>
///   <item>every route carried the 121-entry navigation graph's coordinates
///   instead of the 30 RLWD thingType-18 marker records' until
///   <c>58d9ce57</c> corrected the materializer — 30 nodes aliased onto 11
///   positions — and the fixture kept the aliased values for a further
///   commit, with a test asserting one of the aliases as retail truth.</item>
/// </list>
/// <para>
/// Both were found by reading, not by a gate. This is the gate. It is
/// deliberately an exact comparison of every field the manifest carries,
/// including <c>NodeIndex</c> and <c>RetailComponentsFloatBits</c>, because
/// both are part of the hashed definition identity even though nothing in the
/// movement path reads them yet.
/// </para>
/// </remarks>
public sealed class Level100WaypointFixtureTests
{
    private static Level100ActorDefinitionSet Manifest()
    {
        string path = Path.Combine(
            AppContext.BaseDirectory,
            "Assets",
            "Level100",
            "StaticWorld",
            "level100-static-world.json");
        Assert.True(
            File.Exists(path),
            $"The materialized Level 100 manifest is missing at '{path}'. " +
            "Run `npm run prepare:rebuild-assets`.");
        return Level100ActorDefinitionManifest.Decode(File.ReadAllBytes(path));
    }

    [Fact]
    public void TestFixtureWaypointPaths_AreTheManifestsWaypointPaths()
    {
        Level100ActorDefinitionSet manifest = Manifest();
        Level100ActorDefinitionSet fixture = Level100TestActorDefinitions.Create();

        Assert.Equal(
            manifest.WaypointPaths.Select(path => path.Name),
            fixture.WaypointPaths.Select(path => path.Name));

        foreach (Level100WaypointPathDefinition expected in manifest.WaypointPaths)
        {
            Level100WaypointPathDefinition actual =
                fixture.GetWaypointPath(expected.Name);

            // Point-by-point rather than record equality: the record holds an
            // IReadOnlyList, so its generated Equals is reference equality on
            // the collection and would pass for any two paths at all.
            Assert.Equal(expected.Points.Count, actual.Points.Count);
            for (int index = 0; index < expected.Points.Count; index++)
            {
                Assert.Equal(expected.Points[index], actual.Points[index]);
            }

            // The traversal chain and the loop flag decide MOTION, so a fixture
            // that drifted on them would send every Core-only follower down a
            // different route from the product's while every coordinate above
            // still matched.
            Assert.Equal(
                expected.TargetChainNodeIndices,
                actual.TargetChainNodeIndices);
            Assert.Equal(expected.IsClosed, actual.IsClosed);
        }
    }

    /// <summary>
    /// The shipped fact that #146 turned on: on six of the eight paths the
    /// serialized node order is NOT the order retail walks.
    /// </summary>
    /// <remarks>
    /// <para>
    /// Asserted on the manifest, so it is a statement about retail rather than
    /// about the fixture. If a future materializer change quietly made
    /// <c>points</c> chain-ordered, every consumer would keep working and this
    /// test would fail - which is the point. It is the guard that keeps the two
    /// orders visibly distinct instead of letting them silently converge.
    /// </para>
    /// <para>
    /// <c>Target Truck Path 1</c> and <c>Drone Path 1</c> are the two that
    /// genuinely agree; they are named rather than counted so that "six" cannot
    /// be satisfied by the wrong six.
    /// </para>
    /// </remarks>
    [Fact]
    public void ManifestWaypointPaths_SerializedOrderIsNotTheTraversalOrder()
    {
        Level100ActorDefinitionSet manifest = Manifest();

        string[] agreeing = manifest.WaypointPaths
            .Where(path => path.Points
                .Select(point => point.NodeIndex)
                .SequenceEqual(path.TargetChainNodeIndices))
            .Select(path => path.Name)
            .ToArray();
        Assert.Equal(["Target Truck Path 1", "Drone Path 1"], agreeing);

        // The one this task exists for.
        Level100WaypointPathDefinition flyby = manifest.GetWaypointPath("Flyby Path");
        Assert.Equal([43, 42, 41], flyby.Points.Select(point => point.NodeIndex));
        Assert.Equal([41, 42, 43], flyby.TargetChainNodeIndices);

        // Exactly the two closed chains, named for the same reason.
        Assert.Equal(
            ["Target Tank Path 2", "Drone Path 1"],
            manifest.WaypointPaths
                .Where(path => path.IsClosed)
                .Select(path => path.Name));
    }

    /// <summary>
    /// The authored Air Trainer pose that
    /// <see cref="Level100AirTrainerFlybyTests"/> flies from, checked against
    /// the manifest it was copied out of.
    /// </summary>
    /// <remarks>
    /// The Core fixture parks every non-static actor at the origin, so that
    /// test states the pose itself. A stated constant is a stale constant
    /// waiting to happen, and this is the check that makes it not one.
    /// </remarks>
    [Fact]
    public void ManifestAirTrainer_IsAuthoredWhereTheseTestsPutIt()
    {
        Level100ActorDefinition trainer = Assert.Single(
            Manifest().Actors,
            actor => actor.Name == "Air Trainer");

        Assert.Equal("Flyby", trainer.ScriptName);
        Assert.Equal(
            Level100AirTrainerFlybyTests.AuthoredAirTrainerPosition,
            trainer.InitialPose.PositionMillimeters);
        Assert.Equal(
            Level100AirTrainerFlybyTests.AuthoredAirTrainerBasis,
            trainer.InitialPose.BasisFloatBits);
    }

    [Fact]
    public void TestFixtureMotionDefinitions_AreTheManifestsMotionDefinitions()
    {
        Level100ActorDefinitionSet manifest = Manifest();
        Level100ActorDefinitionSet fixture = Level100TestActorDefinitions.Create();

        // Every field is a scalar, so the generated record equality is the
        // whole comparison here.
        Assert.Equal(manifest.MotionDefinitions, fixture.MotionDefinitions);
    }

    /// <summary>
    /// The property the aliasing broke, asserted on the manifest itself so it
    /// cannot come back through the materializer without a failure.
    /// </summary>
    /// <remarks>
    /// Before <c>58d9ce57</c> the 30 waypoint nodes held only 11 distinct
    /// positions, with 19 aliased pairs; afterwards all 30 are distinct. That
    /// count is what makes this a real check rather than a restatement — a
    /// coordinate lookup against the wrong table is exactly the failure that
    /// produces repeated positions.
    /// </remarks>
    [Fact]
    public void ManifestWaypointNodes_AreDistinctPositionsWithNoAliasing()
    {
        Level100ActorDefinitionSet manifest = Manifest();
        Level100WaypointPointDefinition[] points = manifest.WaypointPaths
            .SelectMany(path => path.Points)
            .ToArray();

        Assert.Equal(30, points.Length);
        Assert.Equal(30, points.Select(point => point.NodeIndex).Distinct().Count());
        Assert.Equal(30, points.Select(point => point.PositionMillimeters).Distinct().Count());

        // The independent corroboration from the correction: exactly four nodes
        // sit off the ground, and they are the two ambient AIRCRAFT routes -
        // -15000 on Flyby Path, the Air Trainer's own spawn altitude, and
        // -20000 on Transporter Path. Nothing in the decode knows which path
        // belongs to which aircraft.
        Assert.Equal(
            new Dictionary<int, int> { [0] = 26, [-15_000] = 2, [-20_000] = 2 },
            points
                .GroupBy(point => point.PositionMillimeters.Y)
                .ToDictionary(group => group.Key, group => group.Count()));
        Assert.All(
            manifest.GetWaypointPath("Flyby Path").Points.Skip(1),
            point => Assert.Equal(-15_000, point.PositionMillimeters.Y));
        Assert.All(
            manifest.GetWaypointPath("Transporter Path").Points.Skip(1),
            point => Assert.Equal(-20_000, point.PositionMillimeters.Y));
    }
}
