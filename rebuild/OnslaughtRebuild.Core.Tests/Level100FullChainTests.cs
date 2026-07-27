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
/// <c>Won</c>. <see cref="NaiveWalkerAutopilot_BreaksTheTutorialAndLoses"/>
/// loses, and the difference between them is entirely firing discipline.</para>
///
/// <para><b>What `Won` here does and does not mean.</b> Ten of the eleven named
/// progression events are produced in full by the world. The eleventh,
/// <c>Airborne Target 2 Destroyed</c> x6, is produced <b>twice</b> before
/// the LevelScript's own sub-40 % hull poll posts <c>Abort Airborne Drones</c>,
/// which sets Target Zone 4 and leads to the same shipped <c>LevelWon()</c>.
/// That is a released path with its own dialogue and its own
/// <c>AddScore(-50)</c>, and it is <b>still</b> not the same thing as clearing
/// the tutorial's combat curriculum: <c>PrimaryObjectiveComplete(4, ...)</c>
/// lives only on the full clear and does not fire. See
/// <c>local-lab/AUTOPILOT-TO-WON-2026-07-26.md</c> and
/// <c>local-lab/BEAT-9-DOGFIGHT-2026-07-27.md</c>.</para>
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
        Outcome = Driver.Run(30 * 1_200);
    }
}

public sealed class Level100FullChainTests
    : IClassFixture<Level100ChainRunFixture>
{
    private readonly ITestOutputHelper _output;
    private readonly Level100ChainRunFixture _chain;

    public Level100FullChainTests(
        ITestOutputHelper output,
        Level100ChainRunFixture chain)
    {
        _output = output;
        _chain = chain;
    }

    /// <summary>
    /// The naive walker autopilot - fixed 18 m stand-off, fire whenever the
    /// reticle is on the objective, never check what is in between.
    ///
    /// <para>It used to stall harmlessly on beat 3's fourth target, putting
    /// 3,578 consecutive rounds into a ridge. It no longer stalls: it
    /// <b>loses</b>. With the released Target Truck routes in the fixture the
    /// three beat-4 trucks drive their authored paths across the firing range
    /// instead of off the map, and the naive driver's undirected fire destroys
    /// one at t2545 while <c>activated</c> is still FALSE. That is the
    /// <c>case FALSE</c> arm of <c>TargetTruck1.msl</c>'s <c>died()</c>:
    /// <c>PostEvent("Broke Tutorial")</c>, which LevelScript answers with
    /// <c>LevelLostString(LOSE_TUTORIAL_BROKE)</c>.</para>
    ///
    /// <para>This is kept, and kept failing-forward rather than deleted,
    /// because it is the control for
    /// <see cref="ChainAutopilot_ReachesWonByInputAlone"/>: the same world and
    /// the same weapons, and the entire difference is that the competent driver
    /// checks the ground and the surrounding structures before it pulls the
    /// trigger. Shooting without looking is not merely inefficient in this
    /// level - it is a losing move, and the released scripts say so.</para>
    /// </summary>
    [Fact]
    public void NaiveWalkerAutopilot_BreaksTheTutorialAndLoses()
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

        // The honest negative, and it is now worse than "did not finish": the
        // level is lost, through the released tutorial-broken path.
        Assert.Equal(
            Level100MissionOutcome.Lost,
            final.Level100Mission.Outcome);
        Assert.Equal(
            Level100MissionFailureReason.TutorialBroken,
            final.Level100Mission.FailureReason);

        // A beat-4 truck was destroyed before "Activate Static Targets 2"
        // armed it, which is the only way this level posts "Broke Tutorial"
        // here: the trucks are the only unactivated destructible actors in
        // range while beat 3 is being fought.
        Assert.Contains(
            final.Level100Actors.Actors,
            actor => actor.TargetGroup == Level100MissionTargetGroup.TargetTrucks &&
                actor.Lifecycle == Level100ActorLifecycle.Destroyed);
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
    /// <para>What this test does <b>not</b> claim: that beat 9 is completed by
    /// kills. <b>Two of the six wave-2 drones are destroyed</b>, and the other
    /// four are still alive when the LevelScript's own health poll posts
    /// <c>Abort Airborne Drones</c> below 40 % hull, which sets Target Zone 4
    /// as the objective and leads to the same <c>LevelWon()</c>. That is a
    /// shipped path with its own dialogue (<c>TUTORIAL_ABORTED</c>) and its own
    /// <c>AddScore(-50)</c>, not a shortcut, but it is a worse run than a good
    /// player's and <c>PrimaryObjectiveComplete(4, ...)</c> never fires.</para>
    ///
    /// <para><b>This count went down, and the cause is a correction rather than
    /// a regression.</b> The previous run destroyed four, but it was flown
    /// against <c>WalkerEnergyRegenerationPerTick = 4</c> - a placeholder that
    /// is eight times slower than the shipped
    /// <c>mGroundEnergyIncrease</c> 0.05. With the byte-faithful 33 the store
    /// refills in about eight released seconds instead of about fifty-eight, so
    /// the driver no longer has to charge on the ground before it launches: it
    /// takes off the moment the wave arms and transits 107 m into the spawn
    /// cluster, merging with all six drones at once instead of meeting them as
    /// they trickle in. The old ground recharge, named as the blocker in
    /// <c>local-lab/BEAT-9-DOGFIGHT-2026-07-27.md</c> §3, is gone - the jet
    /// never runs its store dry in this run at all - and a different blocker is
    /// in its place.</para>
    ///
    /// <para><b>The measured beat-9 trace.</b> Wave armed t9418 at 17,500 hull;
    /// kills at t10416 and later, hull 7,400 at the abort at t11896, and
    /// <c>Won</c> at t12394. The losses are two <c>Forseti Missile</c> hits and
    /// three <c>Blaster</c> streams, and every stream happens at a nearest-drone
    /// slant of 4-8 m.</para>
    ///
    /// <para><b>The blocker, stated precisely: the driver cannot both track and
    /// dodge, and that is a property of the released airframe.</b> A clean
    /// Blaster miss needs a perpendicular speed of <c>18 / slant</c> m/s - 0.45
    /// m/s at 40 m, 3.6 m/s at 5 m. With <c>JetAlignmentPermille</c> 0 the only
    /// thing feeding the crab is the released speed correction, which drives
    /// the magnitude towards <c>JetMinimumSpeedPerTick</c> at <c>MoveZ</c> -1:
    /// measured over t9925-t10005, the airframe held 75 mm per tick, i.e. 2.2
    /// m/s, at exactly the 4-8 m range where 2.2-4.5 m/s was required. But
    /// <c>MoveZ</c> -1 is also what collapses the turn radius enough to hold a
    /// drone on the reticle. The two throttles were measured against each
    /// other: <c>MoveZ</c> +1 throughout kept the hull above the abort
    /// threshold for 2,850 ticks longer (abort t14746 rather than t11896) and
    /// scored <b>zero</b> kills; <c>MoveZ</c> -1 scores kills and is shredded.
    /// Nine intermediate throttle policies, including a firing-solution-gated
    /// blend, were measured and none beat two.</para>
    ///
    /// <para><b>And the result is chaotic, so do not treat two as a tuning
    /// target.</b> Roughly thirty single- and two-parameter variations of this
    /// driver were measured against the corrected constant - yaw gain, crab
    /// segment, missile-break range, fire tolerance, altitude band, launch
    /// energy, stand-off ramps, loiter, and nearest-target hysteresis - and the
    /// kill count swings between 0 and 3 with no gradient, with two variations
    /// losing the level outright. One 3-kill point exists but its immediate
    /// neighbours in the same parameter score 0 and 2, so it is a spike and is
    /// deliberately not shipped. The honest reading is unchanged from
    /// <c>local-lab/BEAT-9-DOGFIGHT-2026-07-27.md</c> §3.1: this driver sits on
    /// a cliff, and the previous four was a point on the same cliff.</para>
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

        // And the qualification, asserted rather than only written down, so
        // that a later run cannot quietly turn this into a full-clear claim or
        // regress away from one without the gate saying so.
        //
        // `Aborted` is the released LevelScript's own `aborted` local, set by
        // `event("Abort Airborne Drones")`, which its beat-9 health poll posts
        // below 40 % hull. This run still wins through that branch: it destroys
        // TWO of the six wave-2 drones and objective 4 is never completed,
        // because `PrimaryObjectiveComplete(4, ...)` lives only on the full
        // clear.
        Assert.True(
            final.Level100Mission.Aborted,
            "This run is expected to win through the released abort branch. " +
            "If it now wins by clearing wave 2, that is better - update this " +
            "assertion and local-lab/AUTOPILOT-TO-WON-2026-07-26.md together.");

        // Both ends are meant here, and neither is a target. The floor catches
        // a driver that has stopped fighting; the ceiling catches a driver that
        // has quietly started clearing the wave, at which point the abort
        // qualification above and this whole doc comment are wrong and have to
        // be rewritten rather than re-baselined. The count is chaotic in this
        // driver's parameters - see the class remarks - so a change either side
        // is evidence about the run, not a number to chase.
        Assert.InRange(
            CountDestroyed(final, Level100MissionTargetGroup.AirborneTargets2),
            2,
            3);
        Assert.Equal(
            Level100PrimaryObjectiveStatus.Failed,
            final.Level100Mission.PrimaryObjectives
                .Single(objective => objective.Objective == 4).Status);
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
        Level100ChainAutopilot driver = _chain.Driver;
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

    private static int CountDestroyed(
        WorldSnapshot state,
        Level100MissionTargetGroup group) =>
        state.Level100Actors.Actors.Count(actor =>
            actor.TargetGroup == group &&
            actor.Lifecycle == Level100ActorLifecycle.Destroyed);
}
