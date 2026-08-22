// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;
using Xunit.Abstractions;

namespace OnslaughtRebuild.Core.Tests;

/// <summary>
/// How far the released progression chain gets under a <c>SimInput</c>-only
/// autopilot that posts no mission event. Two drivers, same world, same
/// weapons.
///
/// <para><see cref="ChainAutopilot_ReachesWonByInputAlone"/> reaches
/// <c>Won</c>.
/// <see cref="NaiveWalkerAutopilot_ClearsTheFiringRangeAndStillNeverFinishes"/>
/// never finishes, and the difference between them is entirely firing
/// discipline.</para>
///
/// <para><b>What `Won` here means, and this changed.</b> All eleven named
/// progression events are now produced in full by the world, including
/// <c>Airborne Target 2 Destroyed</c> six times, so the LevelScript's own
/// <c>numTargets</c> countdown reaches zero and
/// <c>PrimaryObjectiveComplete(4, ...)</c> fires. Until this change the run
/// finished through the released sub-40 % hull poll instead - a shipped path
/// with its own dialogue and its own <c>AddScore(-50)</c>, but not the same
/// thing as completing the tutorial's combat curriculum. That branch is still
/// exercised, by <see cref="Level100AbortControlRunFixture"/>, because two of
/// the measurements here are about it. See
/// <c>local-lab/AUTOPILOT-TO-WON-2026-07-26.md</c> and
/// <c>local-lab/BEAT-9-DOGFIGHT-2026-07-27.md</c>, both of which predate the
/// change and describe the abort run.</para>
/// </summary>
/// <summary>
/// One chain run, shared by every test that reads it. The run is deterministic
/// and takes the better part of a minute, so it is paid for once rather than
/// once per assertion.
/// </summary>
public sealed class Level100ChainRunFixture
{
    internal Level100ChainAutopilot Driver { get; }

    internal Level100MissionOutcome Outcome { get; }

    public Level100ChainRunFixture()
    {
        Driver = Level100ChainAutopilot.Create();
        Outcome = Driver.Run(1_200 * SimulationConstants.TicksPerSecond);
    }
}

/// <summary>
/// The same chain flown by the same controller with the trigger held shut for
/// the whole of beat 9.
///
/// <para>It exists because the main run CLEARED wave 2 when it was written,
/// and two of the measurements in this file are about what happens to a player
/// who does not: the released sub-40 % <c>Abort Airborne Drones</c> poll, and
/// Blasters launched at a player whose crossing speed is below what the
/// <c>18 / slant</c> law needs. See
/// <c>Level100ChainAutopilot.CreateWithWaveTwoTriggerHeldShut</c>. No
/// assertion in either test was altered to accommodate the new run; they were
/// pointed at a run that still reaches the state they were written about.</para>
///
/// <para><b>The main run stopped clearing wave 2 on 2026-08-01</b>, by the
/// vertical-datum and look-table changes recorded on
/// <see cref="Level100FullChainTests.ChainAutopilot_ReachesWonByInputAlone"/>.
/// This fixture is KEPT anyway: it holds the wave-2 trigger shut on purpose, so
/// it isolates the abort branch by construction rather than by happening to
/// land on it, and that isolation is exactly what the two measurements need.
/// If the main run drifts back onto clearing the wave, nothing here changes.</para>
/// </summary>
public sealed class Level100AbortControlRunFixture
{
    internal Level100ChainAutopilot Driver { get; }

    internal Level100MissionOutcome Outcome { get; }

    public Level100AbortControlRunFixture()
    {
        Driver = Level100ChainAutopilot.CreateWithWaveTwoTriggerHeldShut();
        Outcome = Driver.Run(1_200 * SimulationConstants.TicksPerSecond);
    }
}

/// <summary>
/// The same control with the beat-9 evasive crab also held at zero.
///
/// <para>It exists because the 20 Hz migration's re-derivation of
/// <c>Level100ChainAutopilot.ErrorPole</c> made the crabbing control
/// <b>un-hittable</b>: measured, 243 Blasters and zero impacts, with the lowest
/// <c>v_perp * R / 18</c> the wave ever achieved being 1.21. That leaves
/// <see cref="Level100FullChainTests.BlasterMissLaw_SeparatesTheRunsOwnHitsFromItsMisses"/>
/// with only the miss side of a separatrix. This run supplies the hit side, and
/// the variable it removes - <c>MoveX</c> - is precisely the one the law is
/// about. See <c>Level100ChainAutopilot.CreateWithWaveTwoTriggerAndCrabHeldShut</c>.
/// </para>
/// </summary>
public sealed class Level100AbortNoCrabRunFixture
{
    internal Level100ChainAutopilot Driver { get; }

    internal Level100MissionOutcome Outcome { get; }

    public Level100AbortNoCrabRunFixture()
    {
        Driver = Level100ChainAutopilot.CreateWithWaveTwoTriggerAndCrabHeldShut();
        Outcome = Driver.Run(1_200 * SimulationConstants.TicksPerSecond);
    }
}

public sealed class Level100FullChainTests
    : IClassFixture<Level100ChainRunFixture>,
      IClassFixture<Level100AbortControlRunFixture>,
      IClassFixture<Level100AbortNoCrabRunFixture>
{
    private readonly ITestOutputHelper _output;
    private readonly Level100ChainRunFixture _chain;
    private readonly Level100AbortControlRunFixture _abortControl;
    private readonly Level100AbortNoCrabRunFixture _abortNoCrab;

    public Level100FullChainTests(
        ITestOutputHelper output,
        Level100ChainRunFixture chain,
        Level100AbortControlRunFixture abortControl,
        Level100AbortNoCrabRunFixture abortNoCrab)
    {
        _output = output;
        _chain = chain;
        _abortControl = abortControl;
        _abortNoCrab = abortNoCrab;
    }

    /// <summary>
    /// The naive walker autopilot - fixed 18 m stand-off, fire whenever the
    /// reticle is on the objective, never check what is in between.
    ///
    /// <para>It clears the firing range but never wins, with more rounds in the
    /// terrain than in every target combined.</para>
    ///
    /// <para><b>It used to stall a beat earlier, and #146 is why.</b> Beat 3's
    /// fourth target, <c>Target Tank #23</c>, follows <c>Target Tank Path 1</c>.
    /// Walked in the level file's SERIALIZED order that route opens at node 18,
    /// (-68688, 80000), which took the tank away from the firing range and out
    /// of this driver's fixed 18 m stand-off forever. Walked in the order the
    /// markers' own <c>target</c> pointers chain them - [6, 7, 18] - it opens at
    /// node 6, (-25438, 20500), which brings it into range on its first leg. The
    /// tank now dies and beat 3 completes. The exact later navigation objective
    /// and terminal branch remain timing-sensitive measurements, not properties
    /// of this deliberately incompetent driver.</para>
    ///
    /// <para><b>The terminal details are reported but not asserted.</b> They have
    /// changed more than once as retail-correct timing was restored. On the
    /// 2026-08-13 branch the run reaches <c>Lost/TutorialBroken</c> at t13010
    /// with <c>Firing Range</c> still selected. Earlier branches stayed
    /// <c>Running</c> at <c>Target Zone 2</c>. Neither exact branch is the
    /// contract: clearing all four firing-range statics, following the authored
    /// route, wasting most rounds on terrain, and still not winning are.</para>
    ///
    /// <para>This is kept, and kept failing-forward rather than deleted,
    /// because it is the control for
    /// <see cref="ChainAutopilot_ReachesWonByInputAlone"/>: the same world and
    /// the same weapons, and the entire difference is that the competent driver
    /// checks the ground and the surrounding structures before it pulls the
    /// trigger. Shooting without looking does not merely cost rounds in this
    /// level - it does not finish it at all.</para>
    /// </summary>
    [Fact]
    public void NaiveWalkerAutopilot_ClearsTheFiringRangeAndStillNeverFinishes()
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
            $"reason={final.Level100Mission.FailureReason} " +
            $"textId={final.Level100Mission.FailureTextId} " +
            $"nav={final.Level100Mission.NavigationObjective} " +
            $"mode={final.Mode} hull={final.Hull} " +
            $"destroyed={string.Join(",", final.Level100Actors.Actors
                .Where(actor => actor.Lifecycle == Level100ActorLifecycle.Destroyed)
                .Select(actor => actor.Name))}");

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
        //
        // Asserted against the route DATA rather than against a coordinate.
        // This used to be `Z > 60_000`, a number lifted from where the tank
        // happened to stop under the pre-`58d9ce57` waypoint table - which
        // resolved node indices against the wrong RLWD structure, so the route
        // it described was not the released one at all. A magic number cannot
        // tell "followed the route to its end" from "the route moved", and when
        // the route was corrected this assertion failed while the behaviour it
        // was written to check was still exactly right.
        Assert.Equal(Level100ActorCommandIntent.Stopped, intent?.Intent);
        Level100ActorDefinitionSet definitions = Level100TestActorDefinitions.Create();
        // The last node of the AUTHORED TRAVERSAL, not of the serialized list.
        // `Target Tank Path 1` serializes [18, 6, 7] and is walked [6, 7, 18],
        // so its final node is 18 and its serialized last entry, 7, is the
        // route's middle. Reading `Points[^1]` here would assert the tank
        // stopped at a node it drives straight past.
        Level100WaypointPathDefinition tankPath =
            definitions.GetWaypointPath("Target Tank Path 1");
        Level100WaypointPointDefinition lastNode =
            tankPath.ChainPoint(tankPath.TargetChainNodeIndices.Count - 1);
        long arrivalRadius = definitions
            .GetMotionDefinition("Target Tank").ArrivalRadiusMillimeters;
        long deltaX = tank.Pose.PositionMillimeters.X - (long)lastNode.PositionMillimeters.X;
        long deltaZ = tank.Pose.PositionMillimeters.Z - (long)lastNode.PositionMillimeters.Z;
        Assert.True(
            (deltaX * deltaX) + (deltaZ * deltaZ) < arrivalRadius * arrivalRadius,
            $"Target Tank #23 stopped at {tank.Pose.PositionMillimeters}, which is not " +
            $"inside the {arrivalRadius} mm arrival radius of its route's final node " +
            $"{lastNode.PositionMillimeters}.");

        // THE HONEST NEGATIVE: shooting without looking does not finish this
        // level. Exact failure time, reason, and selected navigation objective
        // have moved as retail-correct timing changed, so none is the invariant.
        //
        // Everything around it moved under #146, and the move is real rather
        // than cosmetic, so the old assertions are re-derived from the driver's
        // own report rather than nudged. This test used to be called
        // `…StallsOnBeatThreeAndNeverFinishes` and asserted that Target Tank #23
        // was still ALIVE and the objective still "Firing Range". Both were
        // consequences of walking `Target Tank Path 1` in SERIALIZED order
        // [18, 6, 7]: node 18 is at (-68688, 80000), so the tank's first move
        // was away from the firing range and out of the naive driver's reach.
        // The authored `target` chain is [6, 7, 18] and node 6 is at
        // (-25438, 20500) - toward the player - so the tank now drives into
        // range on its first leg and dies there.
        //
        // Measured on this tree (driver report above): 10 actors destroyed and
        // Lost/TutorialBroken at t13010 with "Firing Range" selected. Those are
        // retained as a dated observation, not promoted into a brittle branch
        // assertion.
        Assert.NotEqual(Level100MissionOutcome.Won, final.Level100Mission.Outcome);
        Assert.Equal(Level100ActorLifecycle.Destroyed, tank.Lifecycle);

        // The waste is still the point, restated as what is now measurable.
        // 2,396 rounds went into the terrain against 422 into every target
        // combined, so more than half of everything fired still hits nothing -
        // which is the same claim the old `> 1_000` bound was making before the
        // corrected routes let the driver connect at all.
        Assert.True(
            driver.ImpactsByActor.TryGetValue(0, out int terrainImpacts),
            "the naive driver must still be recording terrain impacts");
        int targetImpacts = driver.ImpactsByActor
            .Where(pair => pair.Key != 0)
            .Sum(pair => pair.Value);
        Assert.True(
            terrainImpacts > targetImpacts,
            $"the naive driver put {terrainImpacts} rounds into terrain against " +
            $"{targetImpacts} into all targets combined; its failure mode is " +
            "supposed to be that most rounds hit nothing.");
    }

    /// <summary>
    /// The whole released chain, played end to end by one autopilot that drives
    /// <see cref="SimInput"/> and nothing else.
    ///
    /// <para><b>No mission event is posted by this test or by the driver.</b>
    /// Every one of the eleven named progression events comes out of the world:
    /// the two volumes are entered on foot, the four beat-3 statics and the
    /// three beat-4 trucks and the six beat-5 moving spawns are shot with the
    /// weapons the script hands over in the order it hands them over, the three
    /// flight legs are flown and landed so that <c>TargetZoneN.msl</c>'s
    /// <c>InJetMode() == FALSE</c> is satisfied, and the beat-7 drones are shot
    /// down in jet mode because the script has disabled both walker weapons by
    /// then. <c>LevelWon()</c> is called by the released
    /// <c>event("Reached Target Zone 4")</c> and by nothing else.</para>
    ///
    /// <para><b>Current measured branch, re-pinned 2026-08-21 with a bisect
    /// receipt.</b> The 2026-08-14 branch (pinned at 383d5b3e "Model player
    /// weapon scatter") reached <c>Won</c> at t8404 with 8,428 milli-life.
    /// Across 4a978c5b..988f2db0 the evidenced InJetMode contract cluster
    /// left that route unreachable — the chain exhausted its budget stuck at
    /// Target Zone 2 in walker mode — and e633b511 ("Pin Level 100
    /// TargetZone hit() InJetMode and Pause wait-stop") restored winning by
    /// a different, contract-correct route: the modern trajectory (Won at
    /// t6572, hull 18,244) first exists at e633b511 and is stable through
    /// HEAD. Established by a tick-pin-only bisect (predicate greps the
    /// 8404 assertion itself; commits where the chain cannot win are skips,
    /// because they have no tick to drift): e633b511 BAD with Expected 8404
    /// / Actual 6572 at this file's tick pin, hull 18244; last GOOD
    /// ancestor b56cd36a; all nine commits between are skips. Re-pinning is
    /// justified by that measured attribution — these are evidenced retail
    /// contract changes, not a silent regression. The OPEN parity question
    /// (whether training now plays easier than retail, hull 18,244 vs the
    /// route's old 8,428) is unchanged and belongs to the Level 100 lane
    /// with retail-side evidence. The prior abort-path trajectories remain
    /// dated evidence in the local-lab reports, not the active expectation
    /// of this test.</para>
    /// </summary>
    [Fact]
    public void ChainAutopilot_ReachesWonByInputAlone()
    {
        Level100ChainAutopilot driver = _chain.Driver;
        Level100MissionOutcome outcome = _chain.Outcome;
        foreach (string line in driver.Report)
        {
            _output.WriteLine(line);
        }

        WorldSnapshot final = driver.Snapshot;
        Assert.Equal(Level100MissionOutcome.Won, outcome);
        Assert.Equal(Level100MissionOutcome.Won, final.Level100Mission.Outcome);

        // Beats 1-5: every authored and spawned ground target the script
        // activates is destroyed by the player's rounds.
        foreach (string name in new[]
        {
            "Target Tank 2", "Target Tank 3", "Target Warehouse", "Target Tank #23",
        })
        {
            Assert.Equal(
                Level100ActorLifecycle.Destroyed,
                final.Level100Actors.Actors
                    .Single(actor => actor.Name == name).Lifecycle);
        }

        Assert.Equal(
            3,
            CountDestroyed(final, Level100MissionTargetGroup.TargetTrucks));
        Assert.Equal(
            6,
            CountDestroyed(final, Level100MissionTargetGroup.MovingTargets));

        // Beat 7: the first drone wave, which only the jet's Mech Vulcan Cannon
        // can touch.
        Assert.Equal(
            3,
            CountDestroyed(final, Level100MissionTargetGroup.AirborneTargets1));

        // Beats 6, 8 and 10: all three volumes were entered, and each one only
        // dispatches out of jet mode.
        foreach (Level100MissionTrigger trigger in new[]
        {
            Level100MissionTrigger.TargetZone1,
            Level100MissionTrigger.FiringRange,
            Level100MissionTrigger.TargetZone2,
            Level100MissionTrigger.TargetZone3,
            Level100MissionTrigger.TargetZone4,
        })
        {
            Assert.True(
                final.Level100Actors.Actors
                    .Single(actor => actor.Trigger == trigger).TriggerEventDispatched,
                $"{trigger} never dispatched.");
        }

        // Beat 9's numbers are REPORTED BEFORE they are asserted, deliberately.
        // They used to be written out below the first beat-9 assertion, so a
        // run that tripped that assertion printed nothing about why - which is
        // exactly the shape that cost a re-run during the 2026-08-01
        // re-derivation.
        _output.WriteLine(
            $"beat 9: kills=" +
            $"{CountDestroyed(final, Level100MissionTargetGroup.AirborneTargets2)} " +
            $"damage={driver.WaveTwoDamageDealt} " +
            $"spawnsDamaged={driver.WaveTwoSpawnsDamaged} " +
            $"aborted={final.Level100Mission.Aborted} " +
            $"objective4=" +
            $"{final.Level100Mission.PrimaryObjectives.Single(objective => objective.Objective == 4).Status}");

        // Exact re-derivation after the player-damage/resource correction.
        // These are three readings of the same released branch: six world
        // deaths count numTargets to zero, PrimaryObjectiveComplete(4, ...)
        // marks the objective, and the low-hull abort never fires.
        Assert.False(final.Level100Mission.Aborted);
        int waveTwoKills =
            CountDestroyed(final, Level100MissionTargetGroup.AirborneTargets2);
        Assert.Equal(6, waveTwoKills);
        Assert.Equal(6, driver.WaveTwoSpawnsDamaged);
        Assert.Equal(6_000, driver.WaveTwoDamageDealt);
        Assert.Equal(
            Level100PrimaryObjectiveStatus.Complete,
            final.Level100Mission.PrimaryObjectives
                .Single(objective => objective.Objective == 4).Status);
        Assert.Equal(6_572, final.Tick);
        Assert.Equal(18_244, final.Hull);
    }

    /// <summary>
    /// The <c>18 / slant</c> Blaster miss law, tested against the run's own
    /// hits and misses instead of being asserted from the weapon record.
    ///
    /// <para><b>The derivation.</b> <c>Drone Vulcan Cannon</c> carries no
    /// <c>CWeaponTrack</c> and no lead law, so <c>LaunchActorRound</c> points
    /// every <c>Blaster</c> at the player's pose on the tick it is fired and
    /// the round then flies a fixed heading at <c>CRoundVelocity</c> 45.0.
    /// <c>TryReportActorRoundImpact</c> sweeps that segment against the target's
    /// <c>CBattleEngine::GetRadius</c> 0.4 m sphere. A round launched from
    /// <c>R</c> metres therefore arrives after <c>R / 45</c> seconds and needs
    /// the player to have crossed 0.4 m by then, which is a perpendicular speed
    /// of <c>0.4 * 45 / R = 18 / R</c> m/s.
    /// </para>
    ///
    /// <para><b>The measurement.</b> <see cref="Level100ChainAutopilot"/>
    /// records every player-directed Blaster: its launch slant range, the
    /// player's perpendicular speed on the launch tick, and the closest
    /// approach of the round's swept segment across its whole life. The
    /// dimensionless ratio <c>v_perp * R / 18</c> then separates hits from
    /// misses sharply. Measured over the run's 262 player-directed Blasters:
    /// </para>
    ///
    /// <list type="table">
    ///   <item><description>ratio &lt; 0.50: <b>20 of 20</b> hit</description></item>
    ///   <item><description>ratio 0.50-1.00: 20 of 28 hit</description></item>
    ///   <item><description>ratio 1.00-2.50: 4 of 41 hit</description></item>
    ///   <item><description>ratio &gt; 2.50: <b>0 of 173</b> hit</description></item>
    /// </list>
    ///
    /// <para>The soft shoulder either side of 1.0 is the shipped
    /// <c>CWeaponInaccuracy</c> 0.01745329 rad - one degree, which is 0.09 m of
    /// lateral scatter at 5 m and 0.63 m at 36 m - plus the player accelerating
    /// during the round's flight. The law is a separatrix, not a threshold, and
    /// this test asserts it as one.</para>
    ///
    /// <para><b>What follows from it, and it is the reason the measurement was
    /// taken.</b> The required crossing speed falls as range grows, so the
    /// Blaster is a knife-range weapon: the measured hit rate by launch band is
    /// 70 % inside 5 m, 65 % from 5-10 m, and 5 % or less at every band beyond
    /// 10 m. This run's Blaster impacts all occur inside 10 m; their 200-unit
    /// inputs are routed through the player Damage contract rather than treated
    /// as direct hull subtraction.
    /// <b>Standing off does not follow from that, and was measured.</b> See the
    /// class remarks on <c>Level100ChainAutopilot.EngageWaveTwo</c>: the
    /// <c>Forseti Drone Missile Launcher</c>'s <c>CWeaponMinRange</c> 20.0 means
    /// the range band that defeats the Blaster is also the band that switches
    /// on a weapon carrying 2,500 aggregate incoming damage rather than 200.
    /// The resulting hull cost depends on shield state and on whether the
    /// missile's round and explosion are separate Damage calls.</para>
    /// </summary>
    [Fact]
    public void BlasterMissLaw_SeparatesTheRunsOwnHitsFromItsMisses()
    {
        // TWO CONTROLS, AND THE SECOND ONE IS NEW BECAUSE THE DRIVER GOT BETTER.
        // The 20 Hz migration's re-derivation of the beat-9 control poles
        // (`Level100ChainAutopilot.ErrorPole`) made the crabbing control
        // un-hittable: 243 Blasters, ZERO impacts, lowest ratio 1.21. It is
        // still the whole miss side of the separatrix and is kept. The hit side
        // now comes from the same sortie flown with `MoveX` held at zero, which
        // is the variable this law is about. Measured over the union, 551
        // rounds: ratio < 0.5 -> 15 of 17 hit; 0.5-1.0 -> 26 of 44; 1.0-2.5 ->
        // 4 of 76; > 2.5 -> 0 of 388.
        IReadOnlyList<Level100ChainAutopilot.ObservedBlaster> blasters =
        [
            .. _abortControl.Driver.Blasters,
            .. _abortNoCrab.Driver.Blasters,
        ];

        // The impact envelope is the same 0.4 m the runtime tests against.
        const double EnvelopeMillimeters =
            SimulationConstants.Level100PlayerContactRadiusMillimeters;

        // THE RANGE BEYOND WHICH THIS LAW IS NOT THE DECIDING TERM, derived
        // from two shipped numbers rather than chosen. `Drone Vulcan Cannon`
        // carries CWeaponInaccuracy 0.01745329 rad - one degree - so a round
        // launched from R metres can be thrown R * 0.01745329 metres wide of
        // the aim point by the scatter ALONE. At R = 0.4 / 0.01745329 = 22.92 m
        // that equals the whole envelope, and past it a shot can miss a
        // stationary player without the crossing-speed law having anything to
        // do with it. Both populations below are confined to that band, on both
        // sides of the separatrix, so this is a statement of the law's domain
        // and not a filter applied to one arm.
        //
        // Stated plainly because it is exactly the kind of bound that gets
        // abused: it removes ONE shot from the inside population - a 30.88 m
        // launch that missed by 613 mm - taking it from 15 of 17 to 15 of 16.
        // The other inside miss, at 15.81 m, is inside the band and is counted
        // against the law. On the outside population it removes 284 of 388 and
        // changes the rate not at all, because that rate is zero.
        const double InaccuracyRadians = 0.017_453_29;
        const double ConeLimitedRangeMeters =
            EnvelopeMillimeters / 1_000d / InaccuracyRadians;

        static double Ratio(Level100ChainAutopilot.ObservedBlaster shot) =>
            shot.PerpendicularSpeedMetersPerSecond * shot.LaunchSlantMeters / 18.0;

        var comfortablyInside = blasters
            .Where(shot =>
                Ratio(shot) < 0.5 &&
                shot.LaunchSlantMeters < ConeLimitedRangeMeters)
            .ToList();
        var comfortablyOutside = blasters
            .Where(shot =>
                Ratio(shot) > 2.5 &&
                shot.LaunchSlantMeters < ConeLimitedRangeMeters)
            .ToList();

        // Both populations have to be large enough for a rate to mean anything.
        Assert.True(
            comfortablyInside.Count >= 10,
            $"Only {comfortablyInside.Count} Blasters were launched against a " +
            "crossing speed below half the law's requirement; the law is not " +
            "being exercised on that side.");
        Assert.True(
            comfortablyOutside.Count >= 50,
            $"Only {comfortablyOutside.Count} Blasters were launched against a " +
            "crossing speed above 2.5x the law's requirement.");

        double insideHitRate = comfortablyInside
            .Count(shot => shot.ClosestApproachMillimeters < EnvelopeMillimeters) /
            (double)comfortablyInside.Count;
        double outsideHitRate = comfortablyOutside
            .Count(shot => shot.ClosestApproachMillimeters < EnvelopeMillimeters) /
            (double)comfortablyOutside.Count;

        _output.WriteLine(
            $"inside n={comfortablyInside.Count} rate={insideHitRate:F3}; " +
            $"outside n={comfortablyOutside.Count} rate={outsideHitRate:F3}");
        foreach (Level100ChainAutopilot.ObservedBlaster shot in comfortablyOutside
                     .Where(shot => shot.ClosestApproachMillimeters < EnvelopeMillimeters))
        {
            _output.WriteLine(
                $"  outside HIT ratio={Ratio(shot):F2} " +
                $"slant={shot.LaunchSlantMeters:F2} " +
                $"crossing={shot.PerpendicularSpeedMetersPerSecond:F2} " +
                $"closest={shot.ClosestApproachMillimeters}");
        }

        // A player moving at less than half the required crossing speed is hit.
        Assert.True(
            insideHitRate >= 0.9,
            $"Blasters fired at a stationary-enough player hit only " +
            $"{insideHitRate:P0} of the time; the 18/slant law does not hold.");

        // A player moving at more than 2.5x it is not.
        Assert.True(
            outsideHitRate <= 0.02,
            $"Blasters fired at a player crossing well above the law's " +
            $"requirement still hit {outsideHitRate:P0} of the time.");

        // And the closest-approach observable has to agree with the explicit
        // damage boundary, which is what makes it evidence rather than a second
        // geometry engine. Each Blaster carries 200 incoming milli-life; its
        // actual hull share depends on the released shield law. The observable
        // over-counts slightly because it evaluates a swept segment on every
        // Core tick while the runtime advances rounds only on the 20 Hz retail
        // base tick. It can also under-count at the envelope: the observable
        // re-derives the base-tick segment end from yaw/pitch doubles and
        // truncates it, where the runtime integrates the same step in
        // integers, so the two disagree by sub-millimetre amounts at the
        // 400 mm boundary. Measured across this suite's 302 Blasters, exactly
        // two rounds land in the 2 mm band outside the envelope (400.30 mm
        // and 400.81 mm), and the 400.81 mm round IS a runtime hit — the
        // single event behind the old 153-vs-154 under-count. Rounds inside
        // the band are indeterminate for the observable, so the agreement
        // clause credits them and separately pins that the band stays small;
        // the per-event identity diff above names any future disagreement
        // instead of leaving a bare count to be re-fitted.
        const double ReconstructionBandMillimeters = 2d;
        int strictHits = blasters
            .Count(shot => shot.ClosestApproachMillimeters < EnvelopeMillimeters);
        int bandRounds = blasters.Count(shot =>
            shot.ClosestApproachMillimeters >= EnvelopeMillimeters &&
            shot.ClosestApproachMillimeters < EnvelopeMillimeters + ReconstructionBandMillimeters);
        Assert.True(
            bandRounds <= 4,
            $"{bandRounds} Blasters landed in the +-2 mm reconstruction band; the " +
            "observable's geometry has degraded beyond its measured precision.");
        int damageBlasterHits =
            _abortControl.Driver.PlayerDamageEvents.Count(damage =>
                damage.Source == Level100PlayerDamageSource.ActorRound &&
                damage.IncomingDamageMilliLife == 200) +
            _abortNoCrab.Driver.PlayerDamageEvents.Count(damage =>
                damage.Source == Level100PlayerDamageSource.ActorRound &&
                damage.IncomingDamageMilliLife == 200);

        // PER-EVENT IDENTITY DIFF (instrument). The InRange assertion below
        // can only say "153 vs 154"; this diff names the exact damage event
        // with no counted observable (or the reverse) so the wrong contract
        // can be identified instead of fitted. Damage events carry Tick; each
        // counted observable carries ClosestTick; a ±1 window absorbs the
        // removal step, because a round that impacts is deleted inside the
        // killing step so its closest segment is observed at most one tick
        // before the damage event lands.
        static void ReportIdentityDiff(
            string tag,
            Level100ChainAutopilot driver,
            double envelope,
            ITestOutputHelper output)
        {
            List<int> damageTicks =
            [
                .. driver.PlayerDamageEvents
                    .Where(damage =>
                        damage.Source == Level100PlayerDamageSource.ActorRound &&
                        damage.IncomingDamageMilliLife == 200)
                    .Select(damage => damage.Tick)
                    .OrderBy(tick => tick),
            ];
            var counted = driver.Blasters
                .Where(shot => shot.ClosestApproachMillimeters < envelope)
                .Select(shot => (
                    shot.LaunchTick,
                    shot.ClosestTick,
                    shot.ClosestApproachMillimeters,
                    shot.LifeTicks,
                    shot.FinalRemainingBaseTicks))
                .OrderBy(shot => shot.ClosestTick)
                .ToList();
            bool[] used = new bool[counted.Count];
            var unmatchedDamage = new List<int>();
            foreach (int tick in damageTicks)
            {
                int match = -1;
                for (int i = 0; i < counted.Count; i++)
                {
                    if (!used[i] && Math.Abs(counted[i].ClosestTick - tick) <= 1)
                    {
                        match = i;
                        break;
                    }
                }

                if (match < 0)
                {
                    unmatchedDamage.Add(tick);
                }
                else
                {
                    used[match] = true;
                }
            }

            output.WriteLine(
                $"{tag}: damage events={damageTicks.Count} " +
                $"counted observables={counted.Count} " +
                $"unmatched damage={unmatchedDamage.Count} " +
                $"unmatched observables={used.Count(flag => !flag)}");
            foreach (int tick in unmatchedDamage)
            {
                IEnumerable<string> near = counted
                    .Where(shot => Math.Abs(shot.ClosestTick - tick) <= 5)
                    .Select(shot =>
                        $"closest@{shot.ClosestTick}({shot.ClosestApproachMillimeters:F0}mm," +
                        $"launch {shot.LaunchTick},life {shot.LifeTicks}," +
                        $"rem {shot.FinalRemainingBaseTicks})");
                // All observables near the orphan, counted or not, plus any
                // whose terminal tick (launch + life + the removal step) is
                // near it — this separates "tracked but measured >= 400mm"
                // from "never present in any snapshot".
                IEnumerable<string> nearAny = driver.Blasters
                    .Where(shot =>
                        Math.Abs(shot.ClosestTick - tick) <= 3 ||
                        Math.Abs((shot.LaunchTick + shot.LifeTicks + 1) - tick) <= 2)
                    .Select(shot =>
                        $"launch {shot.LaunchTick} life {shot.LifeTicks} " +
                        $"closest {shot.ClosestApproachMillimeters:F1}mm@{shot.ClosestTick} " +
                        $"rem {shot.FinalRemainingBaseTicks}");
                output.WriteLine(
                    $"  {tag} damage@{tick} has NO counted observable within +-{1}; " +
                    $"counted context: {string.Join("; ", near.DefaultIfEmpty("none within +-5"))}");
                output.WriteLine(
                    $"    all nearby observables: " +
                    $"{string.Join(" | ", nearAny.DefaultIfEmpty("NONE - no blaster was near this tick at all"))}");
            }

            for (int i = 0; i < counted.Count; i++)
            {
                if (!used[i])
                {
                    output.WriteLine(
                        $"  {tag} counted observable " +
                        $"closest@{counted[i].ClosestTick}" +
                        $"({counted[i].ClosestApproachMillimeters:F0}mm," +
                        $"launch {counted[i].LaunchTick}) matches NO damage event");
                }
            }
        }

        ReportIdentityDiff("abortControl", _abortControl.Driver, EnvelopeMillimeters, _output);
        ReportIdentityDiff("abortNoCrab", _abortNoCrab.Driver, EnvelopeMillimeters, _output);
        foreach (string note in _abortControl.Driver.BoundaryBandNotes)
        {
            _output.WriteLine($"  boundary-band control: {note}");
        }

        foreach (string note in _abortNoCrab.Driver.BoundaryBandNotes)
        {
            _output.WriteLine($"  boundary-band noCrab: {note}");
        }

        Assert.InRange(
            strictHits + bandRounds,
            damageBlasterHits,
            damageBlasterHits + 8);
    }

    /// <summary>
    /// <c>SetAIState(AI_OFF)</c> silences a unit's weapons.
    ///
    /// <para><b>Why this test exists, and the trap it closes.</b> The AI_OFF
    /// gate in <c>Level100ActorWeaponRuntime.AdvanceActorWeapons</c> was once
    /// believed inert, because adding it left the chain trace byte-identical:
    /// hull 17500 / 16300 / 11200 / 7500 and <c>Won</c> at t10504, unchanged.
    /// It was not inert. <b>The chain's last hull checkpoint is t10028 and the
    /// abort lands at t10030</b>, so a real, load-bearing behaviour change was
    /// invisible to every number anyone was looking at. Nothing in this suite
    /// observed anything after the abort. This test is that observable, and it
    /// is deliberately the only assertion here that lives past t10030.</para>
    ///
    /// <para><b>The law, not a number.</b> The assertion is "an actor whose
    /// <c>AiState</c> is <c>AI_OFF</c> launches no further rounds", not a
    /// pinned hull figure. Hull values move whenever any damage constant moves,
    /// and a test pinned to 6700-versus-6500 gets deleted rather than fixed.
    /// Rounds already in flight at the abort are unaffected and are expected to
    /// keep arriving - the released gate stops the weapon, not the
    /// ammunition.</para>
    ///
    /// <para>The mechanism is <c>AirborneDrone2.msl</c>: <c>init()</c> issues
    /// <c>Attack(player)</c> at line 26, and
    /// <c>event("Abort Airborne Drones")</c> at lines 40-43 answers with
    /// <c>SetAIState(AI_OFF)</c>. LevelScript's beat-9 health poll posts that
    /// event below 40 % hull.</para>
    /// </summary>
    [Fact]
    public void AbortAirborneDrones_SilencesTheDronesThatWereAttacking()
    {
        Level100ChainAutopilot driver = _abortControl.Driver;
        int abortTick = Assert.IsType<int>(driver.AbortTick);

        // The test is only meaningful if the abort actually put a *firing*
        // actor into AI_OFF. Without this, a run that never reached beat 9
        // would pass vacuously.
        Level100ActorCommandIntentSnapshot[] silenced =
            driver.MechanicsAtAbort
                .Where(actor =>
                    actor.AiState == SimulationConstants.ReleasedAiStateOff &&
                    actor.Intent == Level100ActorCommandIntent.Attacking)
                .ToArray();
        _output.WriteLine(
            $"abort at t{abortTick}; AI_OFF and attacking: " +
            string.Join(", ", silenced.Select(actor => actor.ActorId.Value)));
        Assert.NotEmpty(silenced);

        // Every round that was ever launched by an AI_OFF owner after the
        // abort. The released gate makes this set empty.
        Level100ChainAutopilot.ObservedRoundLaunch[] violations =
            driver.RoundLaunches
                .Where(launch =>
                    launch.Tick > abortTick &&
                    launch.OwnerAiState == SimulationConstants.ReleasedAiStateOff)
                .ToArray();
        foreach (Level100ChainAutopilot.ObservedRoundLaunch launch in violations)
        {
            _output.WriteLine(
                $"  t{launch.Tick} round {launch.RoundId} launched by actor " +
                $"{launch.OwnerActorId} while AiState=AI_OFF");
        }

        Assert.True(
            violations.Length == 0,
            $"{violations.Length} round(s) were launched after t{abortTick} by " +
            "actors the released script had already put into AI_OFF. " +
            "SetAIState(AI_OFF) must silence a unit's weapons - see " +
            "Level100ActorWeaponRuntime.AdvanceActorWeapons.");

        // And the control: the same drones did fire before the abort, so the
        // gate is what emptied the set above rather than the run never having
        // armed them.
        Assert.Contains(
            driver.RoundLaunches,
            launch => launch.Tick <= abortTick &&
                silenced.Any(actor => actor.ActorId.Value == launch.OwnerActorId));
    }

    /// <summary>
    /// The weapon-fire cue is emitted once per weapon RELEASE, never once per
    /// ROUND.
    ///
    /// <para><b>Why this is the assertion.</b> Retail issues exactly one
    /// <c>CSoundManager::PlayEffect</c> per launch instant and then spawns the
    /// whole volley. Byte-verified in the pristine specimen
    /// (<c>local-lab/safe-copy-bea-pristine/BEA.exe.original.backup</c>, sha256
    /// <c>74154bfa…</c> - not the installed executable, which is patched):
    /// <c>ProjectileBurst__SpawnFromCurrentPreset</c> at <c>0x005069f0</c>
    /// calls <c>0x004e1940</c> at <c>0x00506a96</c>, loads
    /// <c>[weaponMode+0x48]</c> (CWeaponVolleySize) at <c>0x00506a9b</c>, and
    /// only then enters the spawn loop whose head is <c>0x00506aaa</c> - the
    /// target of the back edge <c>JL</c> at <c>0x0050788b</c>. The call is
    /// outside the loop.</para>
    ///
    /// <para><b>Why it needs the full chain.</b> The Pulse Cannon's volley size
    /// is 1, so the firing range cannot tell the two laws apart. The Twin
    /// Vulcan's is 4 and the jet Mech Vulcan's is 2, and only a run that
    /// reaches beats 4 and 7 fires them. The discriminating case is asserted to
    /// have actually occurred rather than assumed, so this cannot pass
    /// vacuously on a run that only ever tapped the Pulse Cannon.</para>
    /// </summary>
    [Fact]
    public void PlayerWeaponFire_IsOneEventPerReleaseAndNotOnePerRound()
    {
        Level100ChainAutopilot.ObservedPlayerWeaponRelease[] releases =
            _chain.Driver.PlayerWeaponReleases.ToArray();
        Assert.NotEmpty(releases);

        foreach (Level100ChainAutopilot.ObservedPlayerWeaponRelease release in releases)
        {
            // TryFire admits at most one weapon per tick, so a tick that
            // carries two events is a producer emitting per round.
            Level100WeaponFireEvent fired = Assert.Single(release.Events);
            Assert.Equal(release.Tick, fired.Tick);
            Assert.NotEqual(Level100PlayerWeapon.None, fired.Weapon);

            // The one event accounts for the whole volley: RoundCount is what
            // the release created, and the projectile-id watermark agrees.
            if (release.RoundsCreated >= 0)
            {
                Assert.Equal(fired.RoundCount, release.RoundsCreated);
            }
        }

        // The volley weapons the law is about were actually fired. Without
        // this, a run that never left the Pulse Cannon would pass on a
        // per-round producer too.
        Level100WeaponFireEvent[] fireEvents = releases
            .SelectMany(release => release.Events)
            .ToArray();
        _output.WriteLine(
            "releases by weapon: " +
            string.Join(
                ", ",
                fireEvents
                    .GroupBy(item => item.Weapon)
                    .OrderBy(group => group.Key)
                    .Select(group =>
                        $"{group.Key}x{group.Count()} " +
                        $"volley={string.Join("/", group.Select(item => item.RoundCount).Distinct().Order())}")));

        Assert.Contains(
            fireEvents,
            item => item.Weapon == Level100PlayerWeapon.MechTwinVulcanCannon &&
                item.RoundCount == SimulationConstants.TwinVulcanVolleySize);
        Assert.Contains(
            fireEvents,
            item => item.Weapon == Level100PlayerWeapon.MechVulcanCannon &&
                item.RoundCount == SimulationConstants.MechVulcanVolleySize);
        Assert.Contains(
            fireEvents,
            item => item.Weapon == Level100PlayerWeapon.PulseCannonPod &&
                item.RoundCount == 1);
    }

    private static int CountDestroyed(
        WorldSnapshot state,
        Level100MissionTargetGroup group) =>
        state.Level100Actors.Actors.Count(actor =>
            actor.TargetGroup == group &&
            actor.Lifecycle == Level100ActorLifecycle.Destroyed);
}
