// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;
using Xunit.Abstractions;

namespace OnslaughtRebuild.Core.Tests;

/// <summary>
/// How far the released progression chain gets under a `SimInput`-only
/// autopilot that posts no mission event.
///
/// <para>This is a <b>measurement</b>, not a success claim. `Won` is not
/// reached, and the assertions below record exactly where the run stops so
/// that a later change is measured against a number rather than against a
/// recollection. See
/// <c>local-lab/ACTOR-WEAPONS-AND-FULL-CHAIN-2026-07-26.md</c> §5.</para>
/// </summary>
public sealed class Level100FullChainTests
{
    private readonly ITestOutputHelper _output;

    public Level100FullChainTests(ITestOutputHelper output) => _output = output;

    /// <summary>
    /// The walker-only autopilot, run for 900 released seconds.
    ///
    /// <para>Measured outcome: the first three beat-3 static targets are
    /// destroyed, and the run then stops on the fourth, <c>Target Tank
    /// #23</c>. It is <b>not</b> stopped by a missing mechanism: with the
    /// released <c>Target Tank Path 1</c> now in the fixture the tank drives
    /// its authored route and parks at its final node, the autopilot walks to
    /// within its 18 m stand-off, aims, and fires - and every round lands on
    /// terrain. The autopilot chooses a firing position on high ground above
    /// the parked tank and never repositions. That is an autopilot-quality
    /// limit, not a Core limit, and it is the single thing standing between
    /// this run and beats 4 and 5.</para>
    ///
    /// <para>Beats 6, 8 and 10 are separately demonstrated by
    /// <c>Level100FlightLegTests</c>, and beats 7 and 9 now have a working
    /// player weapon for the first time (the jet Mech Vulcan Cannon launched
    /// no projectile at all before this change), but no single autopilot
    /// drives the whole chain.</para>
    /// </summary>
    [Fact]
    public void WalkerAutopilot_StopsOnTheFourthStaticTarget()
    {
        var driver = Level100PlayerDriver.Create();
        driver.Run(30 * 900);
        foreach (string line in driver.Report)
        {
            _output.WriteLine(line);
        }

        WorldSnapshot final = driver.Snapshot;
        Level100ActorSnapshot tank = final.Level100Actors.Actors
            .Single(actor => actor.Name == "Target Tank #23");
        Level100ActorCommandIntentSnapshot? intent =
            final.Level100ActorMechanics.Actors
                .FirstOrDefault(actor => actor.ActorId == tank.ActorId);
        _output.WriteLine(
            $"tank pose={tank.Pose.PositionMillimeters} intent={intent?.Intent} " +
            $"player={final.PlayerPosition} y={final.PlayerElevationMillimeters}");
        _output.WriteLine(
            $"FINAL outcome={final.Level100Mission.Outcome} " +
            $"nav={final.Level100Mission.NavigationObjective} " +
            $"mode={final.Mode} hull={final.Hull}");

        // Beat 3, three of four.
        foreach (string name in
                 new[] { "Target Tank 2", "Target Tank 3", "Target Warehouse" })
        {
            Assert.Equal(
                Level100ActorLifecycle.Destroyed,
                final.Level100Actors.Actors
                    .Single(actor => actor.Name == name).Lifecycle);
        }

        // The released path is now followed to its end, which the synthetic
        // fixture path could never do.
        Assert.Equal(Level100ActorCommandIntent.Stopped, intent?.Intent);
        Assert.True(tank.Pose.PositionMillimeters.Z > 60_000);

        // And the honest negative: `Won` is not reached.
        Assert.Equal(
            Level100MissionOutcome.Running,
            final.Level100Mission.Outcome);
    }
}
