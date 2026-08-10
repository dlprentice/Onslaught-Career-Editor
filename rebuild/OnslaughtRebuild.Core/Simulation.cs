// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

public sealed class Simulation
{
    private sealed class MutableProjectile
    {
        // Rounds are deterministic ammunition state, not script actors. They
        // enter the actor runtime only as the released external Ammunition
        // type mask carried by a hit fact.
        public required int Id { get; init; }
        public SimVector2 Position { get; set; }
        public required SimVector2 Velocity { get; init; }
        public int ElevationMillimeters { get; set; }
        public required int VerticalVelocityMillimetersPerTick { get; init; }
        public int RemainingTicks { get; set; }
        // Per-round contact and damage. The pulse and the Twin Vulcan's Mech
        // Bullet are different released rounds, so a projectile carries its
        // own narrowphase radius and damage rather than assuming the pulse.
        public required int ContactRadiusMillimeters { get; init; }
        public required uint DamageBits { get; init; }
    }

    private sealed class MutableWalkerFoot
    {
        public required int Id { get; init; }
        public required SimVector2 StanceOffset { get; init; }
        public SimVector2 Position { get; set; }
        public int GroundElevationMillimeters { get; set; }
        public int PhaseThirds { get; set; }
        public int LiftMillimeters { get; set; }
    }

    private readonly uint _seed;
    private readonly List<MutableProjectile> _projectiles = [];
    private readonly List<MutableWalkerFoot> _walkerFeet = [];
    private readonly List<Level100MissionEvent> _level100MissionEvents = [];
    private readonly List<Level100ActorScriptCommand> _level100ActorScriptCommands = [];
    private readonly Level100TutorialProgress _level100TutorialProgress;
    private readonly Level100ActorDefinitionSet _level100ActorDefinitions;
    private Level100Mission _level100Mission = null!;
    private Level100ActorRegistry _level100Actors = null!;
    private Level100ActorScriptRuntime _level100ActorScripts = null!;
    private Level100ActorMechanics _level100ActorMechanics = null!;
    private Level100DestructionRuntime _level100Destruction = null!;
    private Level100ActorId _level100PlayerActorId;
    private int _tick;
    private int _nextProjectileId;
    private VehicleMode _mode;
    private VehicleTransition _transition;
    private int _playerGroundElevationMillimeters;
    private int _playerGroundDeltaMillimeters;
    private bool _playerOnGround;
    private bool _playerInWater;
    private bool _playerWaterFailure;
    private bool _playerOnSteepSlope;
    private bool _landingJetsActive;
    private int _groundImpactSpeedMillimetersPerTick;
    private readonly List<AquilaFlightEvent> _flightEvents = [];
    private readonly List<Level100WeaponFireEvent> _weaponFireEvents = [];
    private readonly List<Level100PlayerDamageEvent> _playerDamageEvents = [];
    private sbyte _facingX;
    private sbyte _facingZ;
    // Continuous body yaw (0 = +Z) and its retail-observed inertial step.
    private int _facingYawMicroRad;
    private int _walkerYawVelocityMicroRadPerTick;
    private int _facingPitchMicroRad;
    private int _walkerPitchVelocityMicroRadPerTick;
    private int _bodyRollMicroRad;
    private int _rollVelocityMicroRadPerTick;
    private int _walkerLastMoveXPermille;
    private int _walkerLastMoveZPermille;
    private int _walkerLastHardLeftTick;
    private int _walkerLastHardRightTick;
    private int _walkerLastHardForwardTick;
    private int _walkerLastHardBackwardTick;
    private int _walkerDashTicksRemaining;
    private int _zoomPermille;
    private int _desiredZoomPermille;
    private int _energy;
    private int _shield;
    private int _augmentCharge;
    private bool _augmentActive;
    private int _transformTicksRemaining;
    private int _fireCooldownTicksRemaining;
    private int _twinVulcanReloadTicksRemaining;
    private int _level100OpeningTicksRemaining;
    private bool _level100FlightEnabled;
    private readonly Level100PlayerWeaponRuntime _level100PlayerWeapons = new();
    private int _level100HudEmphasisMask;
    private bool _walkerToJetUsesTakeoffLift;
    private bool _walkerToJetLiftApplied;
    private int _ticksSinceGroundContact;
    private int _jetTicksSinceTransform;
    private int _jetStrafeTicksRemaining;
    private int _jetStrafeAccelerationRemainder;
    private int _jetEnergyDrainRemainderMicro;
    private int _jetThrusterPermille;
    private int _jetGroundedSlowTicks;
    private int _jetStallTicks;
    private int _jetEnergyDrainThisTick;
    private bool _jetMovedThisTick;

    public Simulation(
        uint seed,
        Level100ActorDefinitionSet level100ActorDefinitions,
        Level100TutorialProgress tutorialProgress = default)
    {
        if (seed == 0)
        {
            throw new ArgumentOutOfRangeException(nameof(seed), "Seed must be nonzero.");
        }

        _seed = seed;
        _level100ActorDefinitions = level100ActorDefinitions ??
            throw new ArgumentNullException(nameof(level100ActorDefinitions));
        _level100TutorialProgress = tutorialProgress;
        ResetDynamicState();
    }

    public WorldSnapshot Snapshot => CreateSnapshot();

    /// <summary>
    /// Measurement seam. Applies exactly the two <em>capability grants</em> the
    /// released LevelScript performs at the head of beat 6 —
    /// <c>player.EnableFlightMode()</c> and, for one Target Zone,
    /// <c>target.SetObjective(); target.Activate();</c> — so that the three
    /// "fly there and land" legs can be measured while beats 3–5 are still
    /// mechanically blocked by causes outside this lane (Target Truck and
    /// Target Drone have no contact geometry yet).
    /// </summary>
    /// <remarks>
    /// This posts <b>no</b> named mission event and advances no beat. The
    /// "Reached Target Zone N" event still has to be produced by the world:
    /// the player must actually fly into the volume and be out of jet mode
    /// there, exactly as <c>TargetZoneN.msl</c> <c>hit()</c> requires. Nothing
    /// in the shipped game path calls this; it exists only so a test can pay
    /// for the parts of the tutorial that are blocked elsewhere.
    /// </remarks>
    internal void GrantFlightLegForMeasurement(Level100MissionTrigger trigger)
    {
        _level100FlightEnabled = true;
        Level100ActorSnapshot zone = _level100Actors.Snapshot.Actors.Single(
            actor => actor.Trigger == trigger);
        _level100Actors.SetObjective(zone.ActorId, true);
        _level100Actors.Activate(zone.ActorId);
    }

    public WorldSnapshot Step(
        SimInput input,
        IReadOnlyList<Level100SimulationFact>? level100Facts = null)
    {
        input.Validate();
        _level100Destruction.ValidateExternalFacts(level100Facts);
        ValidateLevel100PlayerDamageFacts(level100Facts);

        _tick++;
        _flightEvents.Clear();
        _weaponFireEvents.Clear();
        _playerDamageEvents.Clear();

        if (input.HasAction(SimActions.Reset))
        {
            ResetDynamicState();
            return CreateSnapshot();
        }

        _level100MissionEvents.Clear();
        _level100ActorScriptCommands.Clear();
        _level100Destruction.BeginTick();

        // Read the pan state BEFORE AdvanceOpeningCamera consumes it. On the
        // tick the player skips, that call sets _level100OpeningTicksRemaining
        // to 0, so the gate below cannot see the pan it is supposed to be
        // gating on. See AdvanceOpeningCamera's remarks for the released
        // dispatch order this reproduces.
        bool skippedThePanThisTick = _level100OpeningTicksRemaining > 0 &&
            input.HasAction(SimActions.SkipPanning);

        // Scripted loss pauses immediately. Player-death/water loss keeps the
        // world live through the nominal 15-second terminal clock, but the
        // update that consumes its final tick is already the PAUSE_GAME update
        // and must not advance actor scripts or world mechanics.
        bool gameplayPausesThisTick = _level100Mission.GameplayPausesOnNextTick;
        if (!gameplayPausesThisTick)
        {
            AdvanceOpeningCamera(input);
            SyncLevel100PlayerState();
            _level100ActorScripts.AdvanceTick();
        }
        PumpLevel100EventBus();
        _level100Mission.AdvanceTick(PlayerHull);
        PumpLevel100EventBus();
        ApplyLevel100Facts(level100Facts);
        if (_level100Mission.GameplayPaused)
        {
            return CreateSnapshot();
        }

        AdvanceLevel100ActorMechanics();
        bool playerPartMoveStarted =
            _level100Actors.GetLifecycle(_level100PlayerActorId) ==
                Level100ActorLifecycle.Alive;

        // Three independent released gates, not one restated three ways.
        //
        //   Outcome == Running        - the level is still being played.
        //   Level100PlayerActive      - the SCRIPT's player.Deactivate() /
        //                               player.Activate() pair, retail Battle
        //                               Engine power at +0x580.
        //   OpeningTicksRemaining     - GAME.GetGameState() < GAME_STATE_PLAYING
        //   / skippedThePanThisTick     at Player.cpp:319.
        //
        // The last two are NOT redundant, even though the cold career's windows
        // overlap. On a COLD first career the shipped init() runs
        // player.Deactivate() (LevelScript.msl:51-52) and does not Activate
        // until TUTORIAL_TECHNICIAN_01 clears at ~t996, so the player is
        // inactive for the whole 180-tick pan and the activation gate alone
        // would look sufficient. On a RETURNING career -
        // GetSlot(SLOT_TUTORIAL_1) == TRUE, Level100TutorialProgress.
        // Introduction - init() takes the other branch, never Deactivates, and
        // the player is ACTIVE from tick 0. There the pan gate is the only
        // thing holding the player still through the released fly-in.
        // Level100SkipPanningTests asserts exactly that separation.
        SimInput playerInput = _level100Mission.Outcome == Level100MissionOutcome.Running &&
            Level100PlayerActive &&
            _level100OpeningTicksRemaining == 0 &&
            !skippedThePanThisTick
            ? input
            : SimInput.Idle;

        AdvanceTransition();
        UpdateAugmentState();

        if (_fireCooldownTicksRemaining > 0)
        {
            _fireCooldownTicksRemaining--;
        }

        if (_twinVulcanReloadTicksRemaining > 0)
        {
            _twinVulcanReloadTicksRemaining--;
        }

        TryToggleMode(playerInput);
        UpdateZoom(playerInput);
        UpdateMovement(playerInput);
        UpdateWalkerFeet();
        UpdateLevel100TriggerActors();
        UpdateResources(playerPartMoveStarted);
        TryFire(playerInput);
        UpdateProjectiles();
        SyncLevel100PlayerState();

        return CreateSnapshot();
    }

    /// <summary>
    /// The opening pan, and the released law that lets the player end it early.
    /// </summary>
    /// <remarks>
    /// <para>
    /// <c>CPlayer::ReceiveButtonAction</c>
    /// (<c>references/Onslaught/Player.cpp:311-315</c>, retail
    /// <c>0x004D3110</c> lines 39-47) handles the skip action ABOVE the
    /// movement gate:
    /// </para>
    /// <code>
    ///   if (button == BUTTON_SKIP_PANNING &amp;&amp; mCurrentViewMode == PLAYER_PAN_VIEW
    ///       &amp;&amp; GAME.GetGameState() == GAME_STATE_PANNING)
    ///   {
    ///       GotoControlView() ;
    ///       GAME.StartPlayingState() ;
    ///   }
    ///   // if game is pre running or panning don't allow control of movement
    ///   if (GAME.GetGameState() &lt; GAME_STATE_PLAYING) return ;   // Player.cpp:319
    /// </code>
    /// <para>
    /// That placement is the whole mechanism, and it encodes three separate
    /// facts:
    /// </para>
    /// <list type="number">
    ///   <item>the skip is accepted <em>only</em> while panning — the retail
    ///   condition is <c>DAT_008a9ac0 == 2</c>, <c>GAME_STATE_PANNING</c>
    ///   (<c>references/Onslaught/game.h:46</c>);</item>
    ///   <item>no movement or weapon input does anything during the pan,
    ///   because every other button falls through to the <c>:319</c>
    ///   gate;</item>
    ///   <item>after <c>StartPlayingState</c> the skip does nothing —
    ///   <c>CGame::StartPlayingState</c> itself early-returns when the state is
    ///   already <c>GAME_STATE_PLAYING</c> (<c>game.cpp:3027</c>).</item>
    /// </list>
    /// <para>
    /// <b>The skip tick is still a panning tick for every other input.</b>
    /// Retail's <c>CController::DoMappings</c> walks the shipped table in
    /// order, and every player-action row (indices 0-15, the
    /// <c>active=1</c> block) comes BEFORE the four
    /// <c>BUTTON_SKIP_PANNING</c> rows (22-25). So on the frame the pan is
    /// skipped, movement, morph, fire and the rest have already been dispatched
    /// and rejected by the <c>:319</c> gate; they take effect from the next
    /// frame.
    /// </para>
    /// <para>
    /// <b>CORRECTED 2026-07-27.</b> This paragraph used to end "Core reproduces
    /// that by leaving this tick's <c>playerInput</c> gated in
    /// <see cref="Step"/>", and it also claimed the law test asserted all three
    /// facts above. Both were false, and an adversarial review caught it by
    /// deleting the <c>_level100OpeningTicksRemaining == 0</c> clause outright
    /// and watching the whole suite stay green. This method zeroes
    /// <c>_level100OpeningTicksRemaining</c>, and the gate then read that same
    /// field and found it already zero — so on the skip tick the pan clause
    /// gated nothing. What was actually suppressing input was
    /// <c>Level100PlayerActive</c>, which is a different released gate that
    /// merely happens to be closed at the same time <em>on a cold career</em>.
    /// On a returning career it is open from tick 0 and the divergence was
    /// live. <see cref="Step"/> now reads the pan state before this call runs.
    /// </para>
    /// <para>
    /// <b>Still open, and deliberately not claimed:</b> the tick on which the
    /// pan ends NATURALLY. There <c>StartPlayingState</c> is reached from
    /// <c>FINISHED_PANNING</c> (<c>game.cpp:3051-3055</c>), which is the game's
    /// own update rather than the controller dispatch, and the drop does not
    /// establish whether that update runs before or after
    /// <c>CController::DoMappings</c> within a frame. Core therefore leaves
    /// that tick accepting input, exactly as it did before, rather than
    /// extending the skip-tick rule to it on an argument. Only the skip tick is
    /// proven, because there the state change happens <em>inside</em>
    /// <c>ReceiveButtonAction</c>, below rows 0-15.
    /// </para>
    /// <para>
    /// <c>GotoControlView()</c> (<c>Player.cpp:72-83</c>) is the camera half
    /// and belongs to the client; Core owns only
    /// <c>GAME.StartPlayingState()</c>.
    /// </para>
    /// </remarks>
    private void AdvanceOpeningCamera(SimInput input)
    {
        bool wasPanning = _level100OpeningTicksRemaining > 0;
        if (!wasPanning)
        {
            return;
        }

        _level100OpeningTicksRemaining--;

        if (input.HasAction(SimActions.SkipPanning))
        {
            _level100OpeningTicksRemaining = 0;
        }

        if (_level100OpeningTicksRemaining == 0)
        {
            // CGame::StartPlayingState (game.cpp:3025-3031). Reached exactly
            // once per run, either from FINISHED_PANNING at the end of the
            // six-second pan (game.cpp:3051-3055) or from the skip above.
            // The mission keeps its own clock - SimActions.Reset gives it a
            // fresh one while _tick keeps running - so it derives the gate
            // itself rather than being handed a simulation tick.
            _level100Mission.NotifyPlayingStateStarted();
        }
    }

    private Level100ActorPoseSnapshot PlayerPose =>
        _level100Actors.GetPose(_level100PlayerActorId);

    private SimVector2 PlayerPosition
    {
        get
        {
            Level100ActorPoseSnapshot pose = PlayerPose;
            return new SimVector2(
                pose.PositionMillimeters.X,
                pose.PositionMillimeters.Z);
        }
    }

    private SimVector2 PlayerVelocity
    {
        get
        {
            Level100ActorPoseSnapshot pose = PlayerPose;
            return new SimVector2(
                pose.LinearVelocityMillimetersPerTick.X,
                pose.LinearVelocityMillimetersPerTick.Z);
        }
    }

    private int PlayerGroundElevationMillimeters => _playerGroundElevationMillimeters;

    private int PlayerGroundDeltaMillimeters => _playerGroundDeltaMillimeters;

    private int PlayerElevationMillimeters => PlayerPose.PositionMillimeters.Y;

    private int PlayerVerticalVelocityMillimetersPerTick =>
        PlayerPose.LinearVelocityMillimetersPerTick.Y;

    private int PlayerHull => _level100Actors.GetHealth(_level100PlayerActorId);

    private bool Level100PlayerActive => _level100Actors.IsActive(_level100PlayerActorId);

    private void CommitLevel100PlayerPose(
        SimVector2 position,
        int elevationMillimeters,
        SimVector2 velocity,
        int verticalVelocityMillimetersPerTick)
    {
        FixedBodyBasis body = GetBodyBasis();
        long upX = ((long)body.ForwardY * body.RightZ) -
            ((long)body.ForwardZ * body.RightY);
        long upY = ((long)body.ForwardZ * body.RightX) -
            ((long)body.ForwardX * body.RightZ);
        long upZ = ((long)body.ForwardX * body.RightY) -
            ((long)body.ForwardY * body.RightX);
        float rightX = (float)body.RightX / FixedTrigScale;
        float rightY = (float)body.RightY / FixedTrigScale;
        float rightZ = (float)body.RightZ / FixedTrigScale;
        float upComponentX =
            (float)DivideRoundNearest(upX, FixedTrigScale) / FixedTrigScale;
        float upComponentY =
            (float)DivideRoundNearest(upY, FixedTrigScale) / FixedTrigScale;
        float upComponentZ =
            (float)DivideRoundNearest(upZ, FixedTrigScale) / FixedTrigScale;
        float forwardX = (float)body.ForwardX / FixedTrigScale;
        float forwardY = (float)body.ForwardY / FixedTrigScale;
        float forwardZ = (float)body.ForwardZ / FixedTrigScale;
        static int Bits(float value) => BitConverter.SingleToInt32Bits(value);

        var basis = new Level100FloatBasis3Bits(
            Bits(rightX), Bits(upComponentX), Bits(forwardX),
            Bits(rightY), Bits(upComponentY), Bits(forwardY),
            Bits(rightZ), Bits(upComponentZ), Bits(forwardZ));
        _level100Actors.SetPose(
            _level100PlayerActorId,
            new Level100ActorPoseSnapshot(
                new SimVector3(
                    position.X,
                    elevationMillimeters,
                    position.Z),
                basis,
                new SimVector3(
                    velocity.X,
                    verticalVelocityMillimetersPerTick,
                    velocity.Z),
                new SimVector3(
                    _walkerPitchVelocityMicroRadPerTick,
                    _walkerYawVelocityMicroRadPerTick,
                    _rollVelocityMicroRadPerTick)));
    }

    private void SyncLevel100PlayerState()
    {
        Level100ActorPoseSnapshot pose = PlayerPose;
        CommitLevel100PlayerPose(
            new SimVector2(
                pose.PositionMillimeters.X,
                pose.PositionMillimeters.Z),
            pose.PositionMillimeters.Y,
            new SimVector2(
                pose.LinearVelocityMillimetersPerTick.X,
                pose.LinearVelocityMillimetersPerTick.Z),
            pose.LinearVelocityMillimetersPerTick.Y);
        _level100ActorScripts.SetPlayerInJetMode(_mode == VehicleMode.Jet);
    }

    private void DestroyLevel100PlayerActor()
    {
        if (_level100Actors.GetLifecycle(_level100PlayerActorId) ==
            Level100ActorLifecycle.Destroyed)
        {
            return;
        }

        _level100Destruction.ReportExternalStartedDying(_level100PlayerActorId);
        _level100Destruction.ReportExternalDied(_level100PlayerActorId);
        DrainAndDispatchLevel100ActorFacts();
    }

    private void ApplyLevel100Facts(IReadOnlyList<Level100SimulationFact>? facts)
    {
        if (facts is null)
        {
            return;
        }

        foreach (Level100SimulationFact fact in facts)
        {
            ArgumentNullException.ThrowIfNull(fact);
            switch (fact)
            {
                case Level100ActorHitFact hit:
                    _level100Actors.ReportHit(
                        hit.ActorId,
                        hit.OtherActorId,
                        hit.OtherThingTypeMask);
                    DrainAndDispatchLevel100ActorFacts();
                    break;
                case Level100ActorStartedDyingFact startedDying:
                    _level100Destruction.ReportExternalStartedDying(
                        startedDying.ActorId);
                    DrainAndDispatchLevel100ActorFacts();
                    break;
                case Level100ActorDiedFact died:
                    _level100Destruction.ReportExternalDied(died.ActorId);
                    DrainAndDispatchLevel100ActorFacts();
                    break;
                case Level100ActorPoseFact pose:
                    if (pose.ActorId == _level100PlayerActorId)
                    {
                        throw new InvalidOperationException(
                            "Player pose is owned by the deterministic vehicle simulation.");
                    }
                    _level100Actors.SetPose(pose.ActorId, pose.Pose);
                    break;
                case Level100ActorActivationFact activation:
                    if (activation.Active)
                    {
                        _level100Actors.Activate(activation.ActorId);
                    }
                    else
                    {
                        _level100Actors.Deactivate(activation.ActorId);
                    }
                    break;
                case Level100ActorObjectiveFact objective:
                    _level100Actors.SetObjective(objective.ActorId, objective.IsObjective);
                    break;
                case Level100ActorHealthFact health:
                    _level100Destruction.SetExternalHealth(
                        health.ActorId,
                        health.Health);
                    break;
                case Level100SpawnThingFact spawn:
                    IReadOnlyList<Level100ActorId> spawned = _level100Actors.SpawnThing(
                        spawn.OwnerActorId,
                        spawn.DefinitionName,
                        spawn.SpawnerName,
                        spawn.Count,
                        spawn.ScriptName);
                    foreach (Level100ActorId actorId in spawned)
                    {
                        _level100Destruction.RegisterActor(actorId);
                        _level100ActorScripts.AttachAndInitializeSpawnedActor(
                            actorId,
                            spawn.ScriptName);
                    }
                    break;
                case Level100MissionInputFact missionInput:
                    _level100Mission.SubmitInput(missionInput.Input);
                    break;
                case Level100PlayerDamageFact damage:
                    if (damage.IncomingDamageMilliLife <= 0)
                    {
                        throw new ArgumentOutOfRangeException(
                            nameof(facts),
                            "Player damage must be positive.");
                    }

                    if (ApplyLevel100PlayerDamage(
                        damage.IncomingDamageMilliLife,
                        damageShields: true,
                        Level100PlayerDamageSource.ExternalFact,
                        out bool factRequestsDeath))
                    {
                        _level100Mission.ReportPlayerHitDuringEvasion();
                        CompleteLevel100PlayerDamageDeath(factRequestsDeath);
                    }
                    break;
                case Level100PlayerDeathFact:
                    DestroyLevel100PlayerActor();
                    _level100Mission.ReportPlayerDeath();
                    break;
                case Level100WaterLossFact:
                    _level100Mission.ReportWaterLoss();
                    break;
                default:
                    throw new ArgumentOutOfRangeException(
                        nameof(facts),
                        $"Unknown Level 100 fact type {fact.GetType().Name}.");
            }

            PumpLevel100EventBus();
        }
    }

    private static void ValidateLevel100PlayerDamageFacts(
        IReadOnlyList<Level100SimulationFact>? facts)
    {
        if (facts is null)
        {
            return;
        }

        foreach (Level100SimulationFact fact in facts)
        {
            if (fact is not Level100PlayerDamageFact damage)
            {
                continue;
            }
            if (damage.IncomingDamageMilliLife <= 0)
            {
                throw new ArgumentOutOfRangeException(
                    nameof(facts),
                    "Player damage must be positive.");
            }
            // The public fact is a shielded Damage call. Constrain it to the
            // exact whole-milli subset before the tick mutates; internal actor
            // rounds already use 200/2500, and water bypasses shields.
            if (damage.IncomingDamageMilliLife <=
                    SimulationConstants.MaximumShield &&
                damage.IncomingDamageMilliLife % 50 != 0)
            {
                throw new InvalidOperationException(
                    "A player-damage fact that can reach the sufficient-shield " +
                    "branch must be divisible by 50 until fractional retail " +
                    "state is represented canonically.");
            }
        }
    }

    private void ApplyWeaponAvailability(Level100WeaponAvailabilityChanged weapon)
    {
        _level100PlayerWeapons.SetActive(weapon.Weapon, weapon.Enabled);
    }

    private void ApplyHudEmphasis(Level100HudEmphasisChanged emphasis)
    {
        if (emphasis.PartId is < 0 or > 30)
        {
            throw new InvalidOperationException(
                $"Released Level 100 requested unsupported HUD part {emphasis.PartId}.");
        }

        int bit = 1 << emphasis.PartId;
        _level100HudEmphasisMask = emphasis.Emphasized
            ? _level100HudEmphasisMask | bit
            : _level100HudEmphasisMask & ~bit;
    }

    private void ApplyLevel100ActorCommand(Level100ActorCommandRequested command)
    {
        switch (command.Command)
        {
            case Level100ActorCommand.Activate:
                _level100Actors.Activate(command.ActorId);
                break;
            case Level100ActorCommand.Deactivate:
                _level100Actors.Deactivate(command.ActorId);
                break;
            case Level100ActorCommand.SetObjective:
                _level100Actors.SetObjective(command.ActorId, true);
                break;
            case Level100ActorCommand.UnsetObjective:
                _level100Actors.SetObjective(command.ActorId, false);
                break;
            default:
                throw new ArgumentOutOfRangeException(nameof(command));
        }
    }

    private void ApplyLevel100SpawnRequest(Level100SpawnThingRequested spawn)
    {
        IReadOnlyList<Level100ActorId> spawned = _level100Actors.SpawnThing(
            spawn.OwnerActorId,
            spawn.DefinitionName,
            spawn.SpawnerName,
            spawn.Count,
            spawn.ScriptName);
        foreach (Level100ActorId actorId in spawned)
        {
            _level100Destruction.RegisterActor(actorId);
            _level100ActorScripts.AttachAndInitializeSpawnedActor(
                actorId,
                spawn.ScriptName);
        }
    }

    private void DrainAndDispatchLevel100ActorFacts()
    {
        foreach (Level100ActorFactSnapshot fact in _level100Actors.DrainFacts())
        {
            _level100ActorScripts.DispatchFact(fact);
            PumpLevel100EventBus();
        }
    }

    private void PumpLevel100EventBus()
    {
        for (int pass = 0; pass < 1_000; pass++)
        {
            IReadOnlyList<Level100MissionEvent> missionEvents = _level100Mission.DrainEvents();
            foreach (Level100MissionEvent missionEvent in missionEvents)
            {
                _level100MissionEvents.Add(missionEvent);
                ApplyLevel100MissionEvent(missionEvent);
            }

            IReadOnlyList<Level100ActorScriptEventPosted> actorEvents =
                _level100ActorScripts.DrainPostedEvents();
            IReadOnlyList<Level100ActorScriptCommand> actorCommands =
                _level100ActorScripts.DrainCommands();
            _level100ActorScriptCommands.AddRange(actorCommands);
            _level100ActorMechanics.ConsumeCommands(actorCommands);
            foreach (Level100ActorScriptEventPosted actorEvent in actorEvents)
            {
                if (actorEvent.ActorId is { } actorId)
                {
                    Level100ActorSnapshot actor = _level100Actors.GetActor(actorId);
                    if (actor.Trigger.HasValue &&
                        actor.TriggerEntered &&
                        !actor.TriggerEventDispatched)
                    {
                        _level100Actors.MarkTriggerEventDispatched(actorId);
                    }
                }

                _level100Mission.QueueExternalEvent(actorEvent.EventName);
            }

            if (missionEvents.Count == 0 && actorEvents.Count == 0 && actorCommands.Count == 0)
            {
                return;
            }
        }

        throw new InvalidOperationException("Level 100 script event bus did not settle.");
    }

    private void AdvanceLevel100ActorMechanics()
    {
        IReadOnlyList<Level100ActorMechanicsWaitCompletion> completions =
            _level100ActorMechanics.AdvanceTick();
        foreach (Level100ActorMechanicsWaitCompletion completion in completions)
        {
            if (!_level100ActorScripts.CompleteMechanicsWait(
                    completion.ActorId,
                    completion.WaitKind,
                    completion.Argument))
            {
                throw new InvalidOperationException(
                    $"Actor {completion.ActorId} completed an unowned mechanics wait.");
            }
        }

        if (completions.Count > 0)
        {
            PumpLevel100EventBus();
        }

        ApplyLevel100ActorRoundImpacts();
    }

    /// <summary>
    /// Routes released actor-owned rounds that reached their designated target.
    /// The Level 100 scripts only ever issue <c>Attack(player)</c>, so the
    /// player is the only supported target today; a round aimed at anything
    /// else is spent without effect rather than routed through an unevidenced
    /// path.
    /// </summary>
    private void ApplyLevel100ActorRoundImpacts()
    {
        IReadOnlyList<Level100ActorRoundImpact> impacts =
            _level100ActorMechanics.DrainActorRoundImpacts();
        foreach (Level100ActorRoundImpact impact in impacts)
        {
            if (impact.TargetActorId != _level100PlayerActorId ||
                impact.IncomingDamageMilliLife <= 0)
            {
                continue;
            }

            if (_level100Actors.GetLifecycle(_level100PlayerActorId) ==
                Level100ActorLifecycle.Destroyed)
            {
                continue;
            }

            // Released THING_TYPE_AMMUNITION contact on the player. This is the
            // hit BattleEngine.msl's `hit()` observes during the beat-5 dodge.
            // The script-level hit callback runs before Damage; the explicit
            // evasion report below runs after the Damage boundary succeeds.
            _level100Actors.ReportHit(
                _level100PlayerActorId,
                otherThingTypeMask: Level100ReleasedThingTypeMasks.Ammunition);
            DrainAndDispatchLevel100ActorFacts();

            if (ApplyLevel100PlayerDamage(
                impact.IncomingDamageMilliLife,
                damageShields: true,
                Level100PlayerDamageSource.ActorRound,
                out bool impactRequestsDeath))
            {
                _level100Mission.ReportPlayerHitDuringEvasion();
                CompleteLevel100PlayerDamageDeath(impactRequestsDeath);
            }

            PumpLevel100EventBus();
        }
    }

    private void ApplyLevel100MissionEvent(Level100MissionEvent missionEvent)
    {
        switch (missionEvent)
        {
            case Level100PlayerActivationChanged activation:
                if (activation.Active)
                {
                    _level100Actors.Activate(_level100PlayerActorId);
                }
                else
                {
                    _level100Actors.Deactivate(_level100PlayerActorId);
                }
                break;
            case Level100FlightModeAvailabilityChanged flight:
                _level100FlightEnabled = flight.Enabled;
                if (!flight.Enabled &&
                    _mode == VehicleMode.Jet &&
                    _transition == VehicleTransition.None)
                {
                    BeginJetToWalkerTransition();
                }
                break;
            case Level100WeaponAvailabilityChanged weapon:
                ApplyWeaponAvailability(weapon);
                break;
            case Level100HudEmphasisChanged emphasis:
                ApplyHudEmphasis(emphasis);
                break;
            case Level100ActorCommandRequested actorCommand:
                ApplyLevel100ActorCommand(actorCommand);
                break;
            case Level100SpawnThingRequested spawn:
                ApplyLevel100SpawnRequest(spawn);
                break;
            case Level100MissionEventPosted posted:
                _level100ActorScripts.PublishEvent(posted.EventName);
                break;
        }
    }

    private void EmitFlightEvent(
        AquilaFlightEvents kind,
        AquilaJetWeapon weapon = AquilaJetWeapon.None)
    {
        ushort value = (ushort)kind;
        if (value == 0 || (value & (value - 1)) != 0)
        {
            throw new ArgumentOutOfRangeException(
                nameof(kind),
                "A flight event must contain exactly one event kind.");
        }

        _flightEvents.Add(new AquilaFlightEvent(
            _tick,
            kind,
            _mode,
            _transition,
            weapon));
    }

    /// <summary>
    /// Records one player weapon RELEASE. Called once per launch instant,
    /// outside the volley loop, because that is where the released
    /// <c>ProjectileBurst__SpawnFromCurrentPreset</c> (0x005069f0) issues its
    /// single <c>CSoundManager::PlayEffect</c> - see
    /// <see cref="Level100WeaponFireEvent"/> for the disassembly.
    /// </summary>
    private void EmitWeaponFireEvent(Level100PlayerWeapon weapon, int roundCount)
    {
        if (weapon == Level100PlayerWeapon.None)
        {
            throw new ArgumentOutOfRangeException(
                nameof(weapon),
                "A weapon fire event must name the released weapon that fired.");
        }

        if (roundCount < 1)
        {
            throw new ArgumentOutOfRangeException(
                nameof(roundCount),
                "A weapon release launches at least one round.");
        }

        _weaponFireEvents.Add(new Level100WeaponFireEvent(
            _tick,
            weapon,
            roundCount));
    }

    private void TryToggleMode(SimInput input)
    {
        if (!input.HasAction(SimActions.ToggleMode) ||
            _transition != VehicleTransition.None)
        {
            if (input.HasAction(SimActions.ToggleMode))
            {
                EmitFlightEvent(AquilaFlightEvents.TransformRejected);
            }
            return;
        }

        if (_mode == VehicleMode.Walker)
        {
            if (!_level100FlightEnabled ||
                _energy < SimulationConstants.TransformEnergyThreshold ||
                _walkerDashTicksRemaining > 0)
            {
                EmitFlightEvent(AquilaFlightEvents.TransformRejected);
                return;
            }

            _walkerToJetUsesTakeoffLift =
                _playerOnGround ||
                _ticksSinceGroundContact < SimulationConstants.RecentGroundContactTicks;
            _walkerToJetLiftApplied = false;
            _desiredZoomPermille = SimulationConstants.ZoomOutPermille;
            _transition = VehicleTransition.WalkerToJet;
            _transformTicksRemaining = _walkerToJetUsesTakeoffLift
                ? SimulationConstants.WalkerToJetTransitionTicks
                : SimulationConstants.WalkerToJetAirborneTransitionTicks;
            EmitFlightEvent(AquilaFlightEvents.WalkerToJetStarted);
            return;
        }

        BeginJetToWalkerTransition();
    }

    private void BeginJetToWalkerTransition()
    {
        if (_transition != VehicleTransition.None || _mode != VehicleMode.Jet)
        {
            return;
        }

        _transition = VehicleTransition.JetToWalker;
        _desiredZoomPermille = SimulationConstants.ZoomOutPermille;
        _transformTicksRemaining = SimulationConstants.JetToWalkerTransitionTicks;
        _jetGroundedSlowTicks = 0;
        _jetStallTicks = 0;
        EmitFlightEvent(AquilaFlightEvents.JetToWalkerStarted);
    }

    private void UpdateZoom(SimInput input)
    {
        // The pristine default physics.dat (175,603 bytes, sha256
        // e1fb3dedbeb29b4b4151da2c8cbbdc940b716b1a2321e1d6a9ba1542c74ada14)
        // gives both selectable Level-100 walker weapons zoom mode 1 at +0x08.
        // Jet weapons omit it, so wheel actions are ignored outside a settled
        // walker state. Charge zoom mode 2 remains deliberately open.
        if (_mode == VehicleMode.Walker && _transition == VehicleTransition.None)
        {
            if (input.HasAction(SimActions.ZoomIn))
            {
                _desiredZoomPermille = SimulationConstants.ZoomInPermille;
            }
            else if (input.HasAction(SimActions.ZoomOut))
            {
                _desiredZoomPermille = SimulationConstants.ZoomOutPermille;
            }
        }

        if (_zoomPermille < _desiredZoomPermille)
        {
            _zoomPermille = Math.Min(
                _zoomPermille + SimulationConstants.ZoomStepPermillePerTick,
                _desiredZoomPermille);
        }
        else if (_zoomPermille > _desiredZoomPermille)
        {
            _zoomPermille = Math.Max(
                _zoomPermille - SimulationConstants.ZoomStepPermillePerTick,
                _desiredZoomPermille);
        }
    }

    private void AdvanceTransition()
    {
        if (_transformTicksRemaining == 0)
        {
            return;
        }

        _transformTicksRemaining--;
        if (_transformTicksRemaining != 0)
        {
            return;
        }

        if (_transition == VehicleTransition.WalkerToJet)
        {
            _mode = VehicleMode.Jet;
            _shield = 0;
            _jetTicksSinceTransform = 0;
            _jetStrafeTicksRemaining = 0;
            _jetGroundedSlowTicks = 0;
            _jetStallTicks = 0;
        }
        else if (_transition == VehicleTransition.JetToWalker)
        {
            _mode = VehicleMode.Walker;
        }

        EmitFlightEvent(AquilaFlightEvents.TransformCompleted);
        _transition = VehicleTransition.None;
    }

    private void UpdateMovement(SimInput input)
    {
        _playerGroundDeltaMillimeters = 0;
        _playerOnSteepSlope = false;
        _landingJetsActive = false;
        _groundImpactSpeedMillimetersPerTick = 0;
        _jetMovedThisTick = false;
        _jetEnergyDrainThisTick = 0;
        if (_transition != VehicleTransition.None)
        {
            UpdateTransitionMovement();
            return;
        }

        if (_mode == VehicleMode.Walker)
        {
            UpdateWalkerYaw(input.LookX, input.LookXAnalogPermille);
            UpdateWalkerPitch(input.LookY, input.LookYAnalogPermille);
            UpdateNonJetRoll();
            ApplyWalkerLandingJets(input);
            if (_playerOnGround)
            {
                UpdateWalkerMovement(input);
            }
            else
            {
                UpdateAirborneWalkerMovement();
            }
            return;
        }

        UpdateJetMovement(input);
    }

    private void ApplyWalkerLandingJets(SimInput input)
    {
        if (!input.HasAction(SimActions.LandingJets))
        {
            return;
        }

        _landingJetsActive = true;
        SimVector2 playerVelocity = PlayerVelocity;
        var retainedVelocity = new SimVector2(
            Retain(
                playerVelocity.X,
                SimulationConstants.WalkerLandingJetHorizontalRetentionNumerator,
                SimulationConstants.WalkerLandingJetRetentionDenominator),
            Retain(
                playerVelocity.Z,
                SimulationConstants.WalkerLandingJetHorizontalRetentionNumerator,
                SimulationConstants.WalkerLandingJetRetentionDenominator));
        int verticalVelocity = PlayerVerticalVelocityMillimetersPerTick;
        if (verticalVelocity <
            -SimulationConstants.WalkerLandingJetMinimumDescentPerTick)
        {
            verticalVelocity = Retain(
                verticalVelocity,
                SimulationConstants.WalkerLandingJetVerticalRetentionNumerator,
                SimulationConstants.WalkerLandingJetRetentionDenominator);
        }

        CommitLevel100PlayerPose(
            PlayerPosition,
            PlayerElevationMillimeters,
            retainedVelocity,
            verticalVelocity);
    }

    private void UpdateTransitionMovement()
    {
        _walkerYawVelocityMicroRadPerTick = RetainAngularVelocity(
            _walkerYawVelocityMicroRadPerTick);
        _facingYawMicroRad = NormalizeMicroRad(
            _facingYawMicroRad + _walkerYawVelocityMicroRadPerTick);
        QuantizeFacingFromYaw();

        _walkerPitchVelocityMicroRadPerTick = RetainAngularVelocity(
            _walkerPitchVelocityMicroRadPerTick);
        if (_transition == VehicleTransition.WalkerToJet &&
            _facingPitchMicroRad > -30_000)
        {
            _walkerPitchVelocityMicroRadPerTick -=
                SimulationConstants.WalkerToJetPitchInputMicroRadPerTick;
        }
        ApplyJetPitchSoftLimit();
        _facingPitchMicroRad = NormalizeMicroRad(
            _facingPitchMicroRad + _walkerPitchVelocityMicroRadPerTick);

        _rollVelocityMicroRadPerTick = RetainAngularVelocity(
            _rollVelocityMicroRadPerTick);
        _bodyRollMicroRad = NormalizeMicroRad(
            _bodyRollMicroRad + _rollVelocityMicroRadPerTick);
        RetainNonJetRollAngle();

        SimVector2 playerVelocity = PlayerVelocity;
        int velocityX = playerVelocity.X;
        int velocityZ = playerVelocity.Z;
        int verticalVelocity = PlayerVerticalVelocityMillimetersPerTick;
        if (_transition == VehicleTransition.WalkerToJet)
        {
            if (_walkerToJetUsesTakeoffLift)
            {
                if (!_walkerToJetLiftApplied)
                {
                    verticalVelocity +=
                        SimulationConstants.WalkerToJetLiftImpulsePerTick;
                    if (_playerOnGround)
                    {
                        velocityX = RetainWalkerVelocity(velocityX);
                        velocityZ = RetainWalkerVelocity(velocityZ);
                        verticalVelocity = RetainWalkerVerticalVelocity(verticalVelocity);
                    }
                    _walkerToJetLiftApplied = true;
                }
            }

            verticalVelocity -= SimulationConstants.WalkerGravityPerTick;
        }
        else
        {
            if (_playerOnGround)
            {
                velocityX = RetainWalkerVelocity(velocityX);
                velocityZ = RetainWalkerVelocity(velocityZ);
            }
            verticalVelocity -= SimulationConstants.MorphIntoWalkerGravityPerTick;
        }

        ApplyLevel100FlightLimits(ref velocityX, ref velocityZ, ref verticalVelocity);
        CommitFlightMovement(velocityX, velocityZ, verticalVelocity);
    }

    private void UpdateAirborneWalkerMovement()
    {
        SimVector2 playerVelocity = PlayerVelocity;
        int velocityX = playerVelocity.X;
        int velocityZ = playerVelocity.Z;
        int verticalVelocity = PlayerVerticalVelocityMillimetersPerTick;
        if (_walkerDashTicksRemaining > 0)
        {
            // CBattleEngineWalkerPart::Move retains the complete velocity while
            // a dash is live even after ground contact is lost. Its speed cap
            // returns only for the final four updates.
            velocityX = RetainWalkerVelocity(velocityX);
            velocityZ = RetainWalkerVelocity(velocityZ);
            verticalVelocity = RetainWalkerVelocity(verticalVelocity);
            if (_walkerDashTicksRemaining <
                SimulationConstants.WalkerDashFrictionThresholdTicks)
            {
                SimVector2 horizontal = ClampMagnitude(
                    new SimVector2(velocityX, velocityZ),
                    SimulationConstants.WalkerMaximumSpeedPerTick);
                velocityX = horizontal.X;
                velocityZ = horizontal.Z;
            }
            _walkerDashTicksRemaining--;
        }
        verticalVelocity -= SimulationConstants.WalkerGravityPerTick;
        ApplyLevel100FlightLimits(ref velocityX, ref velocityZ, ref verticalVelocity);
        CommitFlightMovement(velocityX, velocityZ, verticalVelocity);
    }

    private void UpdateJetMovement(SimInput input)
    {
        _jetMovedThisTick = true;
        if (_energy > 0)
        {
            // CBattleEngineJetPart::Thrust stores 0.5-vy/2 while energy is
            // available. Core's forward input is the opposite sign of vy.
            _jetThrusterPermille = 500 + (input.MoveZ * 500);
        }
        int throttlePermille = _jetThrusterPermille;
        _jetEnergyDrainThisTick = _energy > 0
            ? TakeJetEnergyDrain(throttlePermille)
            : 0;

        SimVector2 playerVelocity = PlayerVelocity;
        int velocityX = playerVelocity.X;
        int velocityY = PlayerVerticalVelocityMillimetersPerTick;
        int velocityZ = playerVelocity.Z;
        FixedBodyBasis basis = GetBodyBasis();

        if (input.MoveX != 0 && _energy > 0)
        {
            int strafeAcceleration = TakeJetStrafeAcceleration(input.MoveX);
            AddDirection(
                ref velocityX,
                ref velocityY,
                ref velocityZ,
                basis.RightX,
                basis.RightY,
                basis.RightZ,
                strafeAcceleration);
            _jetStrafeTicksRemaining = SimulationConstants.JetStrafeAlignmentTicks;
        }

        bool poweredFlight = _energy > 0 && !_playerOnGround;
        if (poweredFlight)
        {
            ApplyJetGroundEffect(
                ref velocityX,
                ref velocityY,
                ref velocityZ,
                basis);

            int magnitude = Magnitude3D(velocityX, velocityY, velocityZ);
            int targetSpeed =
                SimulationConstants.JetMinimumSpeedPerTick +
                ((SimulationConstants.JetMaximumSpeedPerTick -
                  SimulationConstants.JetMinimumSpeedPerTick) *
                 throttlePermille / 1_000);
            int speedCorrection = DivideRoundNearest(
                (long)(targetSpeed - magnitude) *
                    SimulationConstants.JetTargetCorrectionNumerator,
                SimulationConstants.JetTargetCorrectionDenominator);
            AddDirection(
                ref velocityX,
                ref velocityY,
                ref velocityZ,
                basis.ForwardX,
                basis.ForwardY,
                basis.ForwardZ,
                speedCorrection);

            magnitude = Magnitude3D(velocityX, velocityY, velocityZ);
            int alignmentPermille = JetAlignmentPermille();
            AlignVelocityToForward(
                ref velocityX,
                ref velocityY,
                ref velocityZ,
                basis,
                magnitude,
                alignmentPermille);

            int surfaceAltitude = PlayerAltitudeAboveSupportMillimeters();
            int friction = JetFrictionNumerator(
                surfaceAltitude,
                Magnitude3D(velocityX, velocityY, velocityZ));
            RetainMagnitude(
                ref velocityX,
                ref velocityY,
                ref velocityZ,
                friction,
                SimulationConstants.JetFrictionDenominator);
            _jetGroundedSlowTicks = 0;
        }
        else
        {
            velocityX = Retain(
                velocityX,
                SimulationConstants.JetGroundedRetentionNumerator,
                SimulationConstants.JetGroundedResponseDenominator);
            velocityY = Retain(
                velocityY,
                SimulationConstants.JetGroundedRetentionNumerator,
                SimulationConstants.JetGroundedResponseDenominator);
            velocityZ = Retain(
                velocityZ,
                SimulationConstants.JetGroundedRetentionNumerator,
                SimulationConstants.JetGroundedResponseDenominator);
            int retainedMagnitude = Magnitude3D(velocityX, velocityY, velocityZ);
            int coupling = DivideRoundNearest(
                (long)retainedMagnitude *
                    SimulationConstants.JetGroundedForwardCouplingNumerator,
                SimulationConstants.JetGroundedResponseDenominator);
            AddDirection(
                ref velocityX,
                ref velocityY,
                ref velocityZ,
                basis.ForwardX,
                basis.ForwardY,
                basis.ForwardZ,
                coupling);
        }

        if (_energy == 0)
        {
            velocityY -= SimulationConstants.JetGravityPerTick;
        }

        ApplyJetWaterSkim(ref velocityX, ref velocityY, ref velocityZ);
        ApplyLevel100FlightLimits(ref velocityX, ref velocityZ, ref velocityY);
        CommitFlightMovement(velocityX, velocityZ, velocityY);
        UpdateJetOrientation(input);
        UpdateAutomaticJetLanding();

        _jetTicksSinceTransform++;
        if (_jetStrafeTicksRemaining > 0)
        {
            _jetStrafeTicksRemaining--;
        }
    }

    // CBattleEngineJetPart::Move's
    //   cost = (maxCost - minCost) * mThrusterValue + minCost
    // per retail tick, converted to Core ticks through the one shared ratio and
    // carried in micro-retail energy so no fraction is discarded.
    private const int JetEnergyDrainDenominator =
        SimulationConstants.MicroRetailEnergyPerCoreEnergyUnit *
        SimulationConstants.RetailTicksPerCoreTickDenominator;

    private int TakeJetEnergyDrain(int throttlePermille)
    {
        int costMicroPerRetailTick =
            SimulationConstants.JetMinimumEnergyDrainMicroPerRetailTick +
            ((SimulationConstants.JetMaximumEnergyDrainMicroPerRetailTick -
              SimulationConstants.JetMinimumEnergyDrainMicroPerRetailTick) *
             throttlePermille / 1_000);
        int accumulated = _jetEnergyDrainRemainderMicro +
            (costMicroPerRetailTick *
             SimulationConstants.RetailTicksPerCoreTickNumerator);
        int drain = accumulated / JetEnergyDrainDenominator;
        _jetEnergyDrainRemainderMicro = accumulated % JetEnergyDrainDenominator;
        return drain;
    }

    private int TakeJetStrafeAcceleration(sbyte input)
    {
        int accumulated = _jetStrafeAccelerationRemainder +
            (input * SimulationConstants.JetStrafeAccelerationNumerator);
        int acceleration = accumulated /
            SimulationConstants.JetStrafeAccelerationDenominator;
        _jetStrafeAccelerationRemainder = accumulated %
            SimulationConstants.JetStrafeAccelerationDenominator;
        return acceleration;
    }

    private void ApplyJetGroundEffect(
        ref int velocityX,
        ref int velocityY,
        ref int velocityZ,
        FixedBodyBasis basis)
    {
        // Half a SECOND of travel ahead, per BattleEngineJetPart.cpp:548. This
        // read `velocity / 2` - half a Core tick - and was 30x too near; see
        // SimulationConstants.JetGroundEffectLookaheadTicks for the derivation.
        var samplePosition = new SimVector2(
            PlayerPosition.X + (velocityX * SimulationConstants.JetGroundEffectLookaheadTicks),
            PlayerPosition.Z + (velocityZ * SimulationConstants.JetGroundEffectLookaheadTicks));
        int ground = Level100Terrain.Instance.SampleGroundElevationMillimeters(samplePosition);
        bool overWater = Level100Terrain.WaterElevationMillimeters > ground;
        int support = overWater
            ? Level100Terrain.WaterElevationMillimeters
            : ground;
        int altitude = Math.Max(0, PlayerElevationMillimeters - support);
        if (altitude >= SimulationConstants.JetGroundEffectHeightMillimeters)
        {
            return;
        }

        // BattleEngineJetPart.cpp:565
        //   FVector acceleration = mOrientation*FVector(0,(5-altitude)/400,0);
        //   mMainPart->AddVelocity(acceleration);
        // per retail update, with altitude in retail units. Core's altitude is
        // in millimetres and 5 units is JetGroundEffectHeightMillimeters, so
        // the divisor is the shipped 400 verbatim. It read 900 at 30 Hz -
        // 400 x 9/4, the free-acceleration rate factor - and that factor is
        // now 1.
        int forwardAcceleration = DivideRoundNearest(
            SimulationConstants.JetGroundEffectHeightMillimeters - altitude,
            SimulationConstants.JetGroundEffectAccelerationDivisor);
        AddDirection(
            ref velocityX,
            ref velocityY,
            ref velocityZ,
            basis.ForwardX,
            basis.ForwardY,
            basis.ForwardZ,
            forwardAcceleration);

        if (velocityY < 0)
        {
            velocityY = Retain(
                velocityY,
                SimulationConstants.JetDescendingGroundEffectRetentionNumerator,
                SimulationConstants.JetDescendingGroundEffectRetentionDenominator);
        }

        int targetPitch = overWater
            ? 0
            : SampleTerrainPitchMicroRad(samplePosition, _facingYawMicroRad);
        int targetRoll = overWater
            ? 0
            : SampleTerrainRollMicroRad(samplePosition, _facingYawMicroRad);
        int heightFactor =
            SimulationConstants.JetGroundEffectHeightMillimeters - altitude;
        long responseNumerator =
            (long)SimulationConstants.JetGroundFollowNumerator * heightFactor;
        long responseDenominator =
            (long)SimulationConstants.JetGroundFollowDenominator *
            SimulationConstants.JetGroundEffectHeightMillimeters;
        _walkerPitchVelocityMicroRadPerTick += DivideRoundNearest(
            (long)(targetPitch - _facingPitchMicroRad) * responseNumerator,
            responseDenominator);
        _rollVelocityMicroRadPerTick += DivideRoundNearest(
            (long)(targetRoll - _bodyRollMicroRad) * responseNumerator,
            responseDenominator);
    }

    private void ApplyJetWaterSkim(
        ref int velocityX,
        ref int velocityY,
        ref int velocityZ)
    {
        if (Level100Terrain.WaterElevationMillimeters <=
            _playerGroundElevationMillimeters)
        {
            return;
        }

        int altitude =
            PlayerElevationMillimeters - Level100Terrain.WaterElevationMillimeters;
        int horizontalMagnitude = Magnitude2D(velocityX, velocityZ);
        if (altitude >= SimulationConstants.JetSkimHeightMillimeters ||
            horizontalMagnitude <= SimulationConstants.JetSkimMinimumHorizontalSpeedPerTick)
        {
            return;
        }

        // BattleEngineJetPart.cpp:532-534, per retail update:
        //   mVelocity.Z -= magnitudeXY*0.3f;      (retail Z down, Core Y up)
        //   mPitchvel   -= 0.01f*magnitudeXY;
        // The 0.3 is a ratio between two velocities and carries no rate factor
        // at all. The pitch kick is 0.01 rad per RETAIL UNIT of horizontal
        // speed, so at 20 Hz it is 10_000 micro-rad per 1_000 mm. It read
        // 4_608/667 at 30 Hz - 10_000 divided by the R3 damped-input factor
        // 2.170337, over the old 667 mm retail-unit speed scale.
        velocityY += DivideRoundNearest((long)horizontalMagnitude * 3, 10);
        _walkerPitchVelocityMicroRadPerTick -= DivideRoundNearest(
            (long)horizontalMagnitude *
                SimulationConstants.JetWaterSkimPitchKickMicroRadPerRetailUnit,
            SimulationConstants.MillimetersPerRetailUnit);
        velocityX = Retain(
            velocityX,
            SimulationConstants.JetSkimRetentionNumerator,
            SimulationConstants.JetSkimRetentionDenominator);
        velocityY = Retain(
            velocityY,
            SimulationConstants.JetSkimRetentionNumerator,
            SimulationConstants.JetSkimRetentionDenominator);
        velocityZ = Retain(
            velocityZ,
            SimulationConstants.JetSkimRetentionNumerator,
            SimulationConstants.JetSkimRetentionDenominator);

        // BattleEngineJetPart.cpp:536-538
        //     float damage=(0.5f-altitude)*20.0f;
        //     mMainPart->Damage(damage,NULL,FALSE);
        //     mMainPart->HostileEnvironment();
        //
        // Skimming water HURTS, and this reconstruction simply did not apply it -
        // measured 2026-07-27 by flying four skim passes at ~500 mm over water at
        // 400+ mm/tick with the hull sitting at full throughout.
        //
        // Units, and THE TWO THOUSANDS CANCEL - which is worth spelling out
        // because getting it wrong once produced damage 1,000x too small and the
        // law test below caught it:
        //     depth in millimetres -> released units   is  / 1,000
        //     released life        -> registry milli-life is  x 1,000
        // so the conversion is just depth_mm * 20. Core now runs at retail's
        // own 20 Hz rate, so the retained ratio is 1/1. At zero altitude that is
        // 10,000 milli-life per update against a 20,000 hull.
        //
        // That is brutal, and it is meant to be: retail's own numbers are 10.0
        // damage per update against mLife 20.0. Damage starts death only below
        // zero, so two updates leave exact-zero life alive and the third kills:
        // 0.15 seconds. This was NOT softened to taste, and it could not have
        // been written at all before
        // MaximumHull was corrected from 1.0 to 20.0 released life - against the
        // old unit the same law would have killed the player in a sixth of a
        // tick and read as a bug in this code rather than in the constant.
        //
        // HostileEnvironment() (BattleEngine.cpp:3269) is NOT here: it plays
        // "hud_hostile_environment" on a 5 s cooldown, which is presentation.
        // The WaterSkim event below is what a client gates that sample on.
        int skimDamage = checked((int)DivideRoundNearest(
            (long)(SimulationConstants.JetSkimHeightMillimeters - altitude) *
                SimulationConstants.JetWaterSkimDamagePerReleasedUnit *
                SimulationConstants.RetailTicksPerCoreTickNumerator,
            SimulationConstants.RetailTicksPerCoreTickDenominator));
        if (skimDamage > 0)
        {
            if (ApplyLevel100PlayerDamage(
                skimDamage,
                damageShields: false,
                Level100PlayerDamageSource.WaterSkim,
                out bool skimRequestsDeath))
            {
                CompleteLevel100PlayerDamageDeath(skimRequestsDeath);
            }
        }

        EmitFlightEvent(AquilaFlightEvents.WaterSkim);
    }

    private void UpdateJetOrientation(SimInput input)
    {
        SimVector2 playerVelocity = PlayerVelocity;
        int speed = Magnitude3D(
            playerVelocity.X,
            PlayerVerticalVelocityMillimetersPerTick,
            playerVelocity.Z);
        int ratePermille = speed > 7 ? 1_000 : 0;
        if (_playerOnGround && speed < SimulationConstants.JetMaximumSpeedPerTick)
        {
            ratePermille = speed < SimulationConstants.JetGroundedSlowSpeedPerTick
                ? 0
                : Math.Min(1_000, speed * 1_000 / SimulationConstants.JetMaximumSpeedPerTick);
        }
        ratePermille = ratePermille *
            Math.Min(_jetTicksSinceTransform, SimulationConstants.JetInputRampTicks) /
            SimulationConstants.JetInputRampTicks;

        int lookXPermille = ResolveLookInputPermille(input.LookX, input.LookXAnalogPermille);
        int lookYPermille = ResolveLookInputPermille(input.LookY, input.LookYAnalogPermille);
        _walkerYawVelocityMicroRadPerTick =
            RetainAngularVelocity(_walkerYawVelocityMicroRadPerTick) +
            ScaleZoomedLookInput(
                SimulationConstants.JetYawInputMicroRadPerTick,
                lookXPermille * ratePermille / 1_000);
        _walkerPitchVelocityMicroRadPerTick =
            RetainAngularVelocity(_walkerPitchVelocityMicroRadPerTick) +
            ScaleZoomedLookInput(
                SimulationConstants.JetPitchInputMicroRadPerTick,
                lookYPermille * ratePermille / 1_000);
        _rollVelocityMicroRadPerTick =
            RetainAngularVelocity(_rollVelocityMicroRadPerTick) +
            ScaleZoomedLookInput(
                SimulationConstants.JetRollInputMicroRadPerTick,
                lookXPermille * ratePermille / 1_000);

        ApplyJetPitchSoftLimit();
        _facingYawMicroRad = NormalizeMicroRad(
            _facingYawMicroRad + _walkerYawVelocityMicroRadPerTick);
        _facingPitchMicroRad = NormalizeMicroRad(
            _facingPitchMicroRad + _walkerPitchVelocityMicroRadPerTick);
        _bodyRollMicroRad = NormalizeMicroRad(
            _bodyRollMicroRad + _rollVelocityMicroRadPerTick);
        if (!(_playerOnGround && speed < SimulationConstants.JetGroundedSlowSpeedPerTick))
        {
            _bodyRollMicroRad = Retain(
                _bodyRollMicroRad,
                SimulationConstants.JetRollAutoLevelNumerator,
                SimulationConstants.JetRollAutoLevelDenominator);
        }
        QuantizeFacingFromYaw();
    }

    private void ApplyJetPitchSoftLimit()
    {
        int excess = Math.Abs(_facingPitchMicroRad) -
            SimulationConstants.JetPitchSoftLimitMicroRad;
        if (excess <= 0 ||
            Math.Sign(_walkerPitchVelocityMicroRadPerTick) !=
            Math.Sign(_facingPitchMicroRad))
        {
            return;
        }

        int multiplier = Math.Max(0, 1_000_000 - ((excess * 3) / 2));
        _walkerPitchVelocityMicroRadPerTick = Retain(
            _walkerPitchVelocityMicroRadPerTick,
            multiplier,
            1_000_000);
    }

    private void UpdateAutomaticJetLanding()
    {
        SimVector2 playerVelocity = PlayerVelocity;
        int speed = Magnitude3D(
            playerVelocity.X,
            PlayerVerticalVelocityMillimetersPerTick,
            playerVelocity.Z);
        if (_playerOnGround && speed < SimulationConstants.JetGroundedSlowSpeedPerTick)
        {
            _jetGroundedSlowTicks++;
        }
        else if (!_playerOnGround && _energy > 0)
        {
            _jetGroundedSlowTicks = 0;
        }

        if (!_playerOnGround &&
            _jetTicksSinceTransform >= SimulationConstants.JetTransformAlignmentTicks &&
            speed < SimulationConstants.JetStallSpeedPerTick)
        {
            if (_jetStallTicks == 0)
            {
                EmitFlightEvent(AquilaFlightEvents.StallStarted);
            }
            _jetStallTicks++;
        }
        else
        {
            _jetStallTicks = 0;
        }

        if (_jetTicksSinceTransform < SimulationConstants.JetAutoLandEligibilityTicks)
        {
            return;
        }

        if (_jetGroundedSlowTicks >= SimulationConstants.JetAutoLandDelayTicks ||
            speed < SimulationConstants.JetAutoLandSpeedPerTick ||
            _jetStallTicks >= SimulationConstants.JetStallDelayTicks)
        {
            BeginJetToWalkerTransition();
        }
    }

    private int JetAlignmentPermille()
    {
        if (_jetTicksSinceTransform < SimulationConstants.JetTransformAlignmentTicks)
        {
            return _jetTicksSinceTransform * 1_000 /
                SimulationConstants.JetTransformAlignmentTicks;
        }
        if (_jetStrafeTicksRemaining > 0)
        {
            return (SimulationConstants.JetStrafeAlignmentTicks -
                _jetStrafeTicksRemaining) * 1_000 /
                SimulationConstants.JetStrafeAlignmentTicks;
        }

        return 1_000;
    }

    private static int JetFrictionNumerator(int altitude, int speed)
    {
        if (altitude < 1_000)
        {
            return SimulationConstants.JetNearSurfaceFrictionNumerator;
        }
        if (altitude < 3_000)
        {
            if (speed >= 1_000)
            {
                return SimulationConstants.JetNearSurfaceFrictionNumerator;
            }

            if (altitude < 2_000)
            {
                return Interpolate(
                    SimulationConstants.JetNearSurfaceFrictionNumerator,
                    SimulationConstants.JetCruiseFrictionNumerator,
                    altitude - 1_000,
                    1_000);
            }

            return Interpolate(
                SimulationConstants.JetCruiseFrictionNumerator,
                SimulationConstants.JetLowAltitudeFrictionNumerator,
                altitude - 2_000,
                1_000);
        }

        return SimulationConstants.JetCruiseFrictionNumerator;
    }

    private static int Interpolate(int from, int to, int elapsed, int duration) =>
        from + DivideRoundNearest((long)(to - from) * elapsed, duration);

    private void UpdateWalkerYaw(sbyte lookX, short analogPermille)
    {
        int inputPermille = ResolveLookInputPermille(lookX, analogPermille);
        _walkerYawVelocityMicroRadPerTick =
            (int)((long)_walkerYawVelocityMicroRadPerTick *
                SimulationConstants.WalkerYawRetentionNumerator /
                SimulationConstants.WalkerYawRetentionDenominator) +
            ScaleZoomedLookInput(
                SimulationConstants.WalkerYawInputMicroRadPerTick,
                inputPermille);
        _facingYawMicroRad = NormalizeMicroRad(
            _facingYawMicroRad + _walkerYawVelocityMicroRadPerTick);
        QuantizeFacingFromYaw();
    }

    private void UpdateWalkerPitch(sbyte lookY, short analogPermille)
    {
        int inputPermille = ResolveLookInputPermille(lookY, analogPermille);
        _walkerPitchVelocityMicroRadPerTick =
            RetainAngularVelocity(_walkerPitchVelocityMicroRadPerTick) +
            ScaleZoomedLookInput(
                SimulationConstants.WalkerPitchInputMicroRadPerTick,
                inputPermille);
        ApplyWalkerTerrainPitchLimit();
        _facingPitchMicroRad = NormalizeMicroRad(
            _facingPitchMicroRad + _walkerPitchVelocityMicroRadPerTick);
    }

    private void ApplyWalkerTerrainPitchLimit()
    {
        if (!_playerOnGround)
        {
            ApplyJetPitchSoftLimit();
            return;
        }

        int groundPitch = SampleTerrainPitchMicroRad(
            PlayerPosition,
            _facingYawMicroRad);
        int delta = _facingPitchMicroRad - groundPitch;
        if (delta > 700_000)
        {
            _walkerPitchVelocityMicroRadPerTick -= DivideRoundNearest(
                (long)(delta - 700_000) *
                    SimulationConstants.WalkerTerrainPitchCorrectionNumerator,
                SimulationConstants.WalkerTerrainPitchCorrectionDenominator);
        }
        else if (delta > 500_000 && _walkerPitchVelocityMicroRadPerTick > 0)
        {
            int multiplier = Math.Max(0, 1_000_000 - ((delta - 500_000) * 6));
            _walkerPitchVelocityMicroRadPerTick = Retain(
                _walkerPitchVelocityMicroRadPerTick,
                multiplier,
                1_000_000);
        }
        else if (delta < -1_000_000)
        {
            _walkerPitchVelocityMicroRadPerTick -= DivideRoundNearest(
                (long)(delta + 1_000_000) *
                    SimulationConstants.WalkerTerrainPitchCorrectionNumerator,
                SimulationConstants.WalkerTerrainPitchCorrectionDenominator);
        }
        else if (delta < -800_000 && _walkerPitchVelocityMicroRadPerTick < 0)
        {
            int multiplier = Math.Max(0, 1_000_000 - (Math.Abs(delta + 800_000) * 6));
            _walkerPitchVelocityMicroRadPerTick = Retain(
                _walkerPitchVelocityMicroRadPerTick,
                multiplier,
                1_000_000);
        }
    }

    private void UpdateNonJetRoll()
    {
        _rollVelocityMicroRadPerTick = RetainAngularVelocity(
            _rollVelocityMicroRadPerTick);
        _bodyRollMicroRad = NormalizeMicroRad(
            _bodyRollMicroRad + _rollVelocityMicroRadPerTick);
        RetainNonJetRollAngle();
    }

    private void RetainNonJetRollAngle()
    {
        _bodyRollMicroRad = Retain(
            _bodyRollMicroRad,
            SimulationConstants.WalkerYawRetentionNumerator,
            SimulationConstants.WalkerYawRetentionDenominator);
    }

    private static int RetainAngularVelocity(int velocity) =>
        (int)((long)velocity * SimulationConstants.WalkerYawRetentionNumerator /
            SimulationConstants.WalkerYawRetentionDenominator);

    private static int RetainWalkerVerticalVelocity(int velocity) => Retain(
        velocity,
        SimulationConstants.WalkerVerticalRetentionNumerator,
        SimulationConstants.WalkerVerticalRetentionDenominator);

    // Player.cpp:334-355 curves the look axis before it reaches the battle
    // engine, so the curve belongs at the single point where Core resolves a
    // look input rather than at each of the four consumers.
    private static int ResolveLookInputPermille(sbyte digital, short analog) =>
        LookAxisResponse.Apply(
            Math.Clamp((digital * 1_000) + analog, -1_000, 1_000));

    private int ScaleZoomedLookInput(int fullScale, int inputPermille) =>
        DivideRoundNearest(
            (long)fullScale * inputPermille * _zoomPermille,
            (long)SimulationConstants.ZoomScale * 1_000);

    private void UpdateWalkerMovement(SimInput input)
    {
        SimVector2 acceleration = ResolveWalkerAcceleration(input);
        var velocity = new SimVector2(
            RetainWalkerVelocity(PlayerVelocity.X) + acceleration.X,
            RetainWalkerVelocity(PlayerVelocity.Z) + acceleration.Z);
        if (_walkerDashTicksRemaining <
            SimulationConstants.WalkerDashFrictionThresholdTicks)
        {
            velocity = ClampMagnitude(
                velocity,
                SimulationConstants.WalkerMaximumSpeedPerTick);
        }
        MoveWalker(velocity);
        if (_walkerDashTicksRemaining > 0)
        {
            _walkerDashTicksRemaining--;
        }
    }

    private SimVector2 ResolveWalkerAcceleration(SimInput input)
    {
        if (_walkerDashTicksRemaining > 0)
        {
            return SimVector2.Zero;
        }

        int moveXPermille = input.MoveX * 1_000;
        int moveZPermille = input.MoveZ * 1_000;
        bool dashForwardOrBackward = ObserveWalkerForwardGesture(moveZPermille);
        int localX = input.MoveX * SimulationConstants.WalkerAccelerationPerTick;
        int localZ = input.MoveZ * SimulationConstants.WalkerAccelerationPerTick;
        bool dashLeftOrRight = false;

        // Retail receives the longitudinal button callbacks before the lateral
        // callbacks. Once a longitudinal dash starts, the lateral callback
        // returns at its mDoingDashCount gate and does not alter its history.
        if (dashForwardOrBackward)
        {
            localX = 0;
            localZ *= SimulationConstants.WalkerDashAccelerationMultiplier;
        }
        else
        {
            dashLeftOrRight = ObserveWalkerStrafeGesture(moveXPermille);
            if (dashLeftOrRight)
            {
                localX *= SimulationConstants.WalkerDashAccelerationMultiplier;
            }
        }

        if (!dashForwardOrBackward && !dashLeftOrRight &&
            input.MoveX != 0 && input.MoveZ != 0)
        {
            localX = localX * 181 / 256;
            localZ = localZ * 181 / 256;
        }

        (int sin, int cos) = FixedSinCos(_facingYawMicroRad);
        return new SimVector2(
            DivideRoundNearest(((long)localX * cos) - ((long)localZ * sin), FixedTrigScale),
            DivideRoundNearest(((long)localX * sin) + ((long)localZ * cos), FixedTrigScale));
    }

    private bool ObserveWalkerForwardGesture(int movePermille)
    {
        bool hardForward =
            _walkerLastMoveZPermille < SimulationConstants.WalkerDashStartPermille &&
            movePermille > SimulationConstants.WalkerDashStartPermille;
        bool forwardEdge =
            _walkerLastMoveZPermille < SimulationConstants.WalkerDashEndPermille &&
            movePermille > SimulationConstants.WalkerDashEndPermille;
        bool hardBackward =
            _walkerLastMoveZPermille > -SimulationConstants.WalkerDashStartPermille &&
            movePermille < -SimulationConstants.WalkerDashStartPermille;
        bool backwardEdge =
            _walkerLastMoveZPermille > -SimulationConstants.WalkerDashEndPermille &&
            movePermille < -SimulationConstants.WalkerDashEndPermille;

        if (hardForward)
        {
            _walkerLastHardForwardTick = _tick;
        }
        if (hardBackward)
        {
            _walkerLastHardBackwardTick = _tick;
        }

        bool dash =
            (forwardEdge && WalkerDashWindowContains(_walkerLastHardBackwardTick)) ||
            (backwardEdge && WalkerDashWindowContains(_walkerLastHardForwardTick));
        _walkerLastMoveZPermille = movePermille;
        if (dash)
        {
            _walkerDashTicksRemaining = SimulationConstants.WalkerDashLengthTicks;
        }
        return dash;
    }

    private bool ObserveWalkerStrafeGesture(int movePermille)
    {
        bool hardRight =
            _walkerLastMoveXPermille < SimulationConstants.WalkerDashStartPermille &&
            movePermille > SimulationConstants.WalkerDashStartPermille;
        bool rightEdge =
            _walkerLastMoveXPermille < SimulationConstants.WalkerDashEndPermille &&
            movePermille > SimulationConstants.WalkerDashEndPermille;
        bool hardLeft =
            _walkerLastMoveXPermille > -SimulationConstants.WalkerDashStartPermille &&
            movePermille < -SimulationConstants.WalkerDashStartPermille;
        bool leftEdge =
            _walkerLastMoveXPermille > -SimulationConstants.WalkerDashEndPermille &&
            movePermille < -SimulationConstants.WalkerDashEndPermille;

        if (hardRight)
        {
            _walkerLastHardRightTick = _tick;
        }
        if (hardLeft)
        {
            _walkerLastHardLeftTick = _tick;
        }

        bool dashRight = rightEdge && WalkerDashWindowContains(_walkerLastHardLeftTick);
        bool dashLeft = leftEdge && WalkerDashWindowContains(_walkerLastHardRightTick);
        _walkerLastMoveXPermille = movePermille;
        if (dashRight || dashLeft)
        {
            _walkerDashTicksRemaining = SimulationConstants.WalkerDashLengthTicks;
            if (dashLeft)
            {
                _rollVelocityMicroRadPerTick =
                    SimulationConstants.WalkerDashRollVelocityMicroRadPerTick;
            }
            else
            {
                // Retail's lateral pair is intentionally asymmetric: left
                // assigns +0.08, while right subtracts 0.08 from residual roll.
                _rollVelocityMicroRadPerTick -=
                    SimulationConstants.WalkerDashRollVelocityMicroRadPerTick;
            }
            return true;
        }
        return false;
    }

    private bool WalkerDashWindowContains(int hardMoveTick) =>
        hardMoveTick > _tick - SimulationConstants.WalkerDashWindowTicks;

    private static int RetainWalkerVelocity(int velocity) =>
        (int)((long)velocity * SimulationConstants.WalkerVelocityRetentionNumerator /
            SimulationConstants.WalkerVelocityRetentionDenominator);

    private const int FixedTrigScale = 1 << 30;
    private const int HalfPiMicroRad = 1_570_796;
    private const int PiMicroRad = 3_141_593;
    private const int CordicGainQ30 = 652_032_874;

    // Integer CORDIC keeps the local-to-world rotation deterministic without
    // introducing platform floating-point math into Core state updates.
    private static ReadOnlySpan<int> CordicAnglesMicroRad =>
    [
        785_398, 463_648, 244_979, 124_355, 62_419, 31_240, 15_624,
        7_812, 3_906, 1_953, 977, 488, 244, 122, 61, 31, 15, 8, 4, 2, 1,
    ];

    private static (int Sin, int Cos) FixedSinCos(int angleMicroRad)
    {
        int angle = NormalizeMicroRad(angleMicroRad);
        int resultSign = 1;
        if (angle > HalfPiMicroRad)
        {
            angle -= PiMicroRad;
            resultSign = -1;
        }
        else if (angle < -HalfPiMicroRad)
        {
            angle += PiMicroRad;
            resultSign = -1;
        }

        long x = CordicGainQ30;
        long y = 0;
        int remainder = angle;
        ReadOnlySpan<int> angles = CordicAnglesMicroRad;
        for (int index = 0; index < angles.Length; index++)
        {
            long previousX = x;
            if (remainder >= 0)
            {
                x -= y >> index;
                y += previousX >> index;
                remainder -= angles[index];
            }
            else
            {
                x += y >> index;
                y -= previousX >> index;
                remainder += angles[index];
            }
        }

        return ((int)y * resultSign, (int)x * resultSign);
    }

    private readonly record struct FixedBodyBasis(
        int ForwardX,
        int ForwardY,
        int ForwardZ,
        int RightX,
        int RightY,
        int RightZ);

    private FixedBodyBasis GetBodyBasis()
    {
        (int yawSin, int yawCos) = FixedSinCos(_facingYawMicroRad);
        (int pitchSin, int pitchCos) = FixedSinCos(_facingPitchMicroRad);
        (int rollSin, int rollCos) = FixedSinCos(_bodyRollMicroRad);

        int forwardX = -MultiplyFixed(yawSin, pitchCos);
        int forwardY = -pitchSin;
        int forwardZ = MultiplyFixed(yawCos, pitchCos);
        int baseRightX = yawCos;
        int baseRightZ = yawSin;
        int baseUpX = -MultiplyFixed(pitchSin, yawSin);
        int baseUpY = pitchCos;
        int baseUpZ = MultiplyFixed(pitchSin, yawCos);
        int rightX = MultiplyFixed(baseRightX, rollCos) +
            MultiplyFixed(baseUpX, rollSin);
        int rightY = MultiplyFixed(baseUpY, rollSin);
        int rightZ = MultiplyFixed(baseRightZ, rollCos) +
            MultiplyFixed(baseUpZ, rollSin);
        return new FixedBodyBasis(
            forwardX,
            forwardY,
            forwardZ,
            rightX,
            rightY,
            rightZ);
    }

    private static int MultiplyFixed(int left, int right) =>
        DivideRoundNearest((long)left * right, FixedTrigScale);

    private static void AddDirection(
        ref int velocityX,
        ref int velocityY,
        ref int velocityZ,
        int directionX,
        int directionY,
        int directionZ,
        int magnitude)
    {
        velocityX += DivideRoundNearest((long)directionX * magnitude, FixedTrigScale);
        velocityY += DivideRoundNearest((long)directionY * magnitude, FixedTrigScale);
        velocityZ += DivideRoundNearest((long)directionZ * magnitude, FixedTrigScale);
    }

    private static void AlignVelocityToForward(
        ref int velocityX,
        ref int velocityY,
        ref int velocityZ,
        FixedBodyBasis basis,
        int magnitude,
        int mixPermille)
    {
        int targetX = DivideRoundNearest(
            (long)basis.ForwardX * magnitude,
            FixedTrigScale);
        int targetY = DivideRoundNearest(
            (long)basis.ForwardY * magnitude,
            FixedTrigScale);
        int targetZ = DivideRoundNearest(
            (long)basis.ForwardZ * magnitude,
            FixedTrigScale);
        velocityX = Interpolate(velocityX, targetX, mixPermille, 1_000);
        velocityY = Interpolate(velocityY, targetY, mixPermille, 1_000);
        velocityZ = Interpolate(velocityZ, targetZ, mixPermille, 1_000);
        if (mixPermille == 1_000)
        {
            SetMagnitude(ref velocityX, ref velocityY, ref velocityZ, magnitude);
        }
    }

    private int PlayerAltitudeAboveSupportMillimeters() =>
        PlayerElevationMillimeters - Math.Max(
            _playerGroundElevationMillimeters,
            Level100Terrain.WaterElevationMillimeters);

    private static int Magnitude2D(int x, int z) =>
        IntegerSquareRoot(((long)x * x) + ((long)z * z));

    private static int Magnitude3D(int x, int y, int z) =>
        IntegerSquareRoot(
            ((long)x * x) +
            ((long)y * y) +
            ((long)z * z));

    internal static int SampleTerrainPitchMicroRad(
        SimVector2 position,
        int yawMicroRad)
    {
        SimVector2 gradient =
            Level100Terrain.Instance.SampleGroundGradientPermille(position);
        (int sin, int cos) = FixedSinCos(yawMicroRad);
        int forwardSlopePermille = DivideRoundNearest(
            (-(long)gradient.X * sin) + ((long)gradient.Z * cos),
            FixedTrigScale);
        int tangentLengthPermille = IntegerSquareRoot(
            1_000_000L + ((long)forwardSlopePermille * forwardSlopePermille));
        return -DivideRoundNearest(
            (long)forwardSlopePermille * 1_000_000,
            tangentLengthPermille);
    }

    internal static int SampleTerrainRollMicroRad(
        SimVector2 position,
        int yawMicroRad)
    {
        SimVector2 gradient =
            Level100Terrain.Instance.SampleGroundGradientPermille(position);
        (int sin, int cos) = FixedSinCos(yawMicroRad);
        int rightSlopePermille = DivideRoundNearest(
            ((long)gradient.X * cos) + ((long)gradient.Z * sin),
            FixedTrigScale);
        int tangentLengthPermille = IntegerSquareRoot(
            1_000_000L + ((long)rightSlopePermille * rightSlopePermille));
        return DivideRoundNearest(
            (long)rightSlopePermille * 500_000,
            tangentLengthPermille);
    }

    private static int Retain(int value, int numerator, int denominator) =>
        DivideRoundNearest((long)value * numerator, denominator);

    private static void RetainMagnitude(
        ref int x,
        ref int y,
        ref int z,
        int numerator,
        int denominator)
    {
        int magnitude = Magnitude3D(x, y, z);
        if (magnitude == 0)
        {
            return;
        }

        int retainedMagnitude = Retain(magnitude, numerator, denominator);
        SetMagnitude(ref x, ref y, ref z, retainedMagnitude);
    }

    private static void SetMagnitude(ref int x, ref int y, ref int z, int magnitude)
    {
        if (magnitude < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(magnitude));
        }
        if (magnitude == 0)
        {
            x = 0;
            y = 0;
            z = 0;
            return;
        }

        int currentMagnitude = Magnitude3D(x, y, z);
        if (currentMagnitude == 0 || currentMagnitude == magnitude)
        {
            return;
        }

        int dominantAxis;
        int dominantSign;
        if (Math.Abs(x) >= Math.Abs(y) && Math.Abs(x) >= Math.Abs(z))
        {
            dominantAxis = 0;
            dominantSign = Math.Sign(x);
        }
        else if (Math.Abs(y) >= Math.Abs(z))
        {
            dominantAxis = 1;
            dominantSign = Math.Sign(y);
        }
        else
        {
            dominantAxis = 2;
            dominantSign = Math.Sign(z);
        }

        x = DivideRoundNearest((long)x * magnitude, currentMagnitude);
        y = DivideRoundNearest((long)y * magnitude, currentMagnitude);
        z = DivideRoundNearest((long)z * magnitude, currentMagnitude);

        // Fixed-point component rounding can leave the vector one scalar unit
        // either side of the source float operation. Correct the dominant axis
        // within a fixed bound so malformed future inputs cannot hang Core.
        const int maximumCorrectionSteps = 4;
        for (int step = 0; step < maximumCorrectionSteps; step++)
        {
            int correctedMagnitude = Magnitude3D(x, y, z);
            if (correctedMagnitude == magnitude)
            {
                return;
            }

            int correction = dominantSign *
                (correctedMagnitude < magnitude ? 1 : -1);
            switch (dominantAxis)
            {
                case 0:
                    x += correction;
                    break;
                case 1:
                    y += correction;
                    break;
                default:
                    z += correction;
                    break;
            }
        }

        throw new InvalidOperationException(
            $"Fixed magnitude correction did not converge to {magnitude}.");
    }

    private static int DivideRoundNearest(long numerator, long denominator)
    {
        long half = denominator / 2L;
        return (int)(numerator >= 0
            ? (numerator + half) / denominator
            : (numerator - half) / denominator);
    }

    private void MoveWalker(SimVector2 velocity)
    {
        SimVector2 currentPosition = PlayerPosition;
        if (GoingIntoLevel100Water(velocity))
        {
            velocity = SimVector2.Zero;
        }
        else
        {
            velocity = ResolveLevel100SteepSlope(velocity);
        }
        SimVector2 nextPosition = new(
            currentPosition.X + velocity.X,
            currentPosition.Z + velocity.Z);
        nextPosition = ResolveLevel100WalkerContact(
            currentPosition,
            nextPosition,
            SimulationConstants.Level100ControlTowerPosition,
            SimulationConstants.Level100ControlTowerContactRadius);
        nextPosition = ResolveLevel100WalkerContact(
            currentPosition,
            nextPosition,
            SimulationConstants.Level100TankFactoryPosition,
            SimulationConstants.Level100TankFactoryContactRadius);
        CommitPlayerPosition(nextPosition);
    }

    private bool GoingIntoLevel100Water(SimVector2 velocity)
    {
        if (!_playerOnGround)
        {
            return false;
        }

        int currentGround = _playerGroundElevationMillimeters;
        int futureGround = Level100Terrain.Instance.SampleGroundElevationMillimeters(
            new SimVector2(
                PlayerPosition.X + velocity.X,
                PlayerPosition.Z + velocity.Z));
        int water = Level100Terrain.WaterElevationMillimeters;
        if (water - currentGround > 300)
        {
            return futureGround < currentGround;
        }

        return water - futureGround > 300;
    }

    private SimVector2 ResolveLevel100SteepSlope(SimVector2 velocity)
    {
        for (int iteration = 0; iteration < 6; iteration++)
        {
            var future = new SimVector2(
                PlayerPosition.X + velocity.X,
                PlayerPosition.Z + velocity.Z);
            SimVector2 gradient =
                Level100Terrain.Instance.SampleGroundGradientPermille(future);
            long gradientSquared =
                ((long)gradient.X * gradient.X) +
                ((long)gradient.Z * gradient.Z);
            if (gradientSquared <=
                SimulationConstants.Level100SteepSlopeGradientSquaredThreshold)
            {
                return velocity;
            }

            _playerOnSteepSlope = true;
            long uphill =
                ((long)velocity.X * gradient.X) +
                ((long)velocity.Z * gradient.Z);
            if (uphill <= 0)
            {
                return velocity;
            }

            velocity = new SimVector2(
                velocity.X - DivideRoundNearest(uphill * gradient.X, gradientSquared),
                velocity.Z - DivideRoundNearest(uphill * gradient.Z, gradientSquared));
        }

        return velocity;
    }

    private static SimVector2 ResolveLevel100WalkerContact(
        SimVector2 currentPosition,
        SimVector2 nextPosition,
        SimVector2 facilityPosition,
        int contactRadius)
    {
        long offsetX = (long)nextPosition.X - facilityPosition.X;
        long offsetZ = (long)nextPosition.Z - facilityPosition.Z;
        long radiusSquared = (long)contactRadius * contactRadius;
        long distanceSquared = (offsetX * offsetX) + (offsetZ * offsetZ);
        if (distanceSquared >= radiusSquared)
        {
            return nextPosition;
        }

        if (distanceSquared == 0)
        {
            offsetX = (long)currentPosition.X - facilityPosition.X;
            offsetZ = (long)currentPosition.Z - facilityPosition.Z;
            distanceSquared = (offsetX * offsetX) + (offsetZ * offsetZ);
            if (distanceSquared == 0)
            {
                return new SimVector2(facilityPosition.X + contactRadius, facilityPosition.Z);
            }
        }

        int distance = IntegerSquareRoot(distanceSquared);
        int resolvedX =
            facilityPosition.X + DivideRoundNearest(offsetX * contactRadius, distance);
        int resolvedZ =
            facilityPosition.Z + DivideRoundNearest(offsetZ * contactRadius, distance);
        while (true)
        {
            long resolvedOffsetX = (long)resolvedX - facilityPosition.X;
            long resolvedOffsetZ = (long)resolvedZ - facilityPosition.Z;
            if ((resolvedOffsetX * resolvedOffsetX) + (resolvedOffsetZ * resolvedOffsetZ) >=
                radiusSquared)
            {
                return new SimVector2(resolvedX, resolvedZ);
            }

            if (Math.Abs(offsetX) >= Math.Abs(offsetZ))
            {
                resolvedX += Math.Sign(offsetX);
            }
            else
            {
                resolvedZ += Math.Sign(offsetZ);
            }
        }
    }

    private void CommitPlayerPosition(SimVector2 nextPosition)
    {
        SimVector2 previousPosition = PlayerPosition;
        int previousGroundElevation = _playerGroundElevationMillimeters;
        SimVector2 velocity = new(
            nextPosition.X - previousPosition.X,
            nextPosition.Z - previousPosition.Z);
        _playerGroundElevationMillimeters =
            Level100Terrain.Instance.SampleGroundElevationMillimeters(nextPosition);
        _playerGroundDeltaMillimeters =
            _playerGroundElevationMillimeters - previousGroundElevation;
        int elevation =
            _playerGroundElevationMillimeters +
            Level100Terrain.WalkerCenterOfGravityMillimeters;
        bool wasInWater = _playerInWater;
        _playerOnGround = true;
        _playerInWater =
            elevation <=
            Level100Terrain.WaterElevationMillimeters +
                Level100Terrain.WalkerCenterOfGravityMillimeters;
        if (!wasInWater && _playerInWater)
        {
            EmitFlightEvent(AquilaFlightEvents.EnteredWater);
        }
        UpdateWaterFailureState(elevation);
        _ticksSinceGroundContact = 0;
        CommitLevel100PlayerPose(
            nextPosition,
            elevation,
            velocity,
            0);
    }

    private void CommitFlightMovement(
        int velocityX,
        int velocityZ,
        int verticalVelocity)
    {
        bool wasOnGround = _playerOnGround;
        bool wasInWater = _playerInWater;
        int previousGroundElevation = _playerGroundElevationMillimeters;
        SimVector2 playerPosition = PlayerPosition;
        var nextPosition = new SimVector2(
            playerPosition.X + velocityX,
            playerPosition.Z + velocityZ);
        int nextGround =
            Level100Terrain.Instance.SampleGroundElevationMillimeters(nextPosition);
        int nextElevation = PlayerElevationMillimeters + verticalVelocity;
        int minimumElevation =
            nextGround + Level100Terrain.WalkerCenterOfGravityMillimeters;
        bool onGround = nextElevation <= minimumElevation;
        if (onGround)
        {
            if (!wasOnGround)
            {
                _groundImpactSpeedMillimetersPerTick = Magnitude3D(
                    velocityX,
                    verticalVelocity,
                    velocityZ);
                int damagingThreshold =
                    _mode == VehicleMode.Walker &&
                    _transition == VehicleTransition.None
                        ? SimulationConstants.WalkerGroundImpactThresholdPerTick
                        : SimulationConstants.JetGroundImpactThresholdPerTick;
                if (_groundImpactSpeedMillimetersPerTick > damagingThreshold)
                {
                    // The released threshold and contact speed are known, but
                    // the float damage-to-current-hull translation is not.
                    EmitFlightEvent(
                        AquilaFlightEvents.GroundImpactDamageThresholdCrossed);
                }
            }

            nextElevation = minimumElevation;
            if (verticalVelocity < -37)
            {
                verticalVelocity = Math.Max(1, -verticalVelocity / 100);
            }
            else
            {
                verticalVelocity = 0;
            }
        }

        _playerGroundElevationMillimeters = nextGround;
        _playerGroundDeltaMillimeters = nextGround - previousGroundElevation;
        _playerOnGround = onGround;
        _playerInWater =
            nextElevation <=
            Level100Terrain.WaterElevationMillimeters +
                Level100Terrain.WalkerCenterOfGravityMillimeters;
        if (!wasOnGround && onGround)
        {
            EmitFlightEvent(AquilaFlightEvents.Touchdown);
        }
        if (!wasInWater && _playerInWater)
        {
            EmitFlightEvent(AquilaFlightEvents.EnteredWater);
        }
        UpdateWaterFailureState(nextElevation);
        _ticksSinceGroundContact = onGround
            ? 0
            : Math.Min(int.MaxValue, _ticksSinceGroundContact + 1);
        CommitLevel100PlayerPose(
            nextPosition,
            nextElevation,
            new SimVector2(velocityX, velocityZ),
            verticalVelocity);
    }

    /// <summary>
    /// Retail's water kill test, as a predicate on the committed player
    /// elevation.
    ///
    /// <para><c>references/Onslaught/BattleEngine.cpp:1249-1266</c>:</para>
    /// <code>
    /// float altitude = mPos.Z - MAP.GetWaterLevel();
    /// if ((altitude > -0.2f) &amp;&amp; ((mVulnerable) || (!CLIPARAMS.mDeveloperMode)))
    ///     StartDieProcess();
    /// </code>
    /// <para>Retail's Z axis points DOWN - proven inside the same family, at
    /// <c>actor.cpp:120-125</c>, where the ground clamp fires on
    /// <c>alt &lt;= mPos.Z</c> and then assigns <c>mPos.Z = alt</c> - so
    /// <c>altitude &gt; -0.2f</c> in retail's frame is
    /// <c>A &lt; waterAltitude + 0.2 m</c> in this one. The 0.2 m is
    /// <see cref="SimulationConstants.WaterFailureClearanceMillimeters"/> = 200.
    /// <c>mVulnerable || !developerMode</c> is unconditionally true in a retail
    /// build and is therefore not a divergence.</para>
    ///
    /// <para>Extracted only so it can be named and pinned; the call site below
    /// is unchanged. See <c>Level100FerryLandingTests</c> Gate C - loosening
    /// this is how every previous attempt at the Target Zone 4 ferry went
    /// wrong, and it is the one change that would fake every other gate in that
    /// file.</para>
    /// </summary>
    internal static bool WaterFailureAtElevation(int playerElevationMillimeters) =>
        playerElevationMillimeters <=
            Level100Terrain.WaterElevationMillimeters +
                SimulationConstants.WaterFailureClearanceMillimeters;

    private void UpdateWaterFailureState(int playerElevationMillimeters)
    {
        if (_playerWaterFailure ||
            !WaterFailureAtElevation(playerElevationMillimeters))
        {
            return;
        }

        _playerWaterFailure = true;
        EmitFlightEvent(AquilaFlightEvents.WaterFailureStarted);
        if (_level100Mission.ReportWaterLoss())
        {
            PumpLevel100EventBus();
        }
    }

    private void ApplyLevel100FlightLimits(
        ref int velocityX,
        ref int velocityZ,
        ref int verticalVelocity)
    {
        SimVector2 playerPosition = PlayerPosition;
        velocityX = ApplyMapEdgeVelocityLimit(
            playerPosition.X,
            velocityX,
            Level100Terrain.MinimumRelativeXMillimeters,
            Level100Terrain.MaximumRelativeXMillimeters);
        velocityZ = ApplyMapEdgeVelocityLimit(
            playerPosition.Z,
            velocityZ,
            Level100Terrain.MinimumRelativeZMillimeters,
            Level100Terrain.MaximumRelativeZMillimeters);
        if (PlayerElevationMillimeters >
            SimulationConstants.Level100MaximumElevationMillimeters &&
            verticalVelocity > 0)
        {
            verticalVelocity = 0;
        }
    }

    private static int ApplyMapEdgeVelocityLimit(
        int position,
        int velocity,
        int minimum,
        int maximum)
    {
        int outside = position < minimum
            ? minimum - position
            : position > maximum
                ? position - maximum
                : 0;
        bool movingOut =
            (position < minimum && velocity < 0) ||
            (position > maximum && velocity > 0);
        if (!movingOut)
        {
            return velocity;
        }

        int remaining = Math.Max(
            0,
            SimulationConstants.Level100MapEdgeSlowdownMillimeters - outside);
        return Retain(
            velocity,
            remaining,
            SimulationConstants.Level100MapEdgeSlowdownMillimeters);
    }

    private void UpdateWalkerFeet()
    {
        if (_mode != VehicleMode.Walker || _transition != VehicleTransition.None)
        {
            AlignWalkerFeetToNaturalTargets();
            return;
        }

        long playerDisplacementSquared =
            ((long)PlayerVelocity.X * PlayerVelocity.X) +
            ((long)PlayerVelocity.Z * PlayerVelocity.Z) +
            ((long)PlayerGroundDeltaMillimeters * PlayerGroundDeltaMillimeters);
        bool ownerMoved = playerDisplacementSquared > 10L * 10L;
        int threshold = ownerMoved
            ? SimulationConstants.WalkerFootMovingThresholdMillimeters
            : SimulationConstants.WalkerFootStationaryThresholdMillimeters;

        for (int footIndex = 0; footIndex < _walkerFeet.Count; footIndex++)
        {
            MutableWalkerFoot foot = _walkerFeet[footIndex];
            SimVector2 targetPosition = NaturalWalkerFootPosition(foot.StanceOffset);
            int targetGround =
                Level100Terrain.Instance.SampleGroundElevationMillimeters(targetPosition);
            int deltaX = targetPosition.X - foot.Position.X;
            int deltaZ = targetPosition.Z - foot.Position.Z;
            int deltaGround = targetGround - foot.GroundElevationMillimeters;

            if (foot.PhaseThirds == 0)
            {
                long distanceSquared =
                    ((long)deltaX * deltaX) +
                    ((long)deltaZ * deltaZ) +
                    ((long)deltaGround * deltaGround);
                if (distanceSquared > (long)threshold * threshold &&
                    CanBeginWalkerFootSwing(footIndex, distanceSquared, threshold))
                {
                    // Released CMCMech enters phase one without moving or
                    // lifting the planted point until its next update.
                    foot.PhaseThirds = 3;
                }
                continue;
            }

            foot.PhaseThirds +=
                SimulationConstants.WalkerFootPhaseUnitsPerSecond * 3 /
                SimulationConstants.TicksPerSecond;
            if (foot.PhaseThirds >=
                (SimulationConstants.WalkerFootPhaseEnd + 1) * 3)
            {
                foot.PhaseThirds = 0;
                foot.LiftMillimeters = 0;
                continue;
            }

            int phaseDenominator = SimulationConstants.WalkerFootPhaseEnd * 3;
            foot.Position = new SimVector2(
                foot.Position.X + DivideRoundNearest(
                    (long)deltaX * foot.PhaseThirds,
                    phaseDenominator),
                foot.Position.Z + DivideRoundNearest(
                    (long)deltaZ * foot.PhaseThirds,
                    phaseDenominator));
            foot.GroundElevationMillimeters =
                Level100Terrain.Instance.SampleGroundElevationMillimeters(foot.Position);
            int phaseAngleMicroRad = DivideRoundNearest(
                (long)foot.PhaseThirds * PiMicroRad,
                phaseDenominator);
            (int phaseSin, _) = FixedSinCos(phaseAngleMicroRad);
            foot.LiftMillimeters = Math.Max(
                0,
                DivideRoundNearest(
                    (long)phaseSin * SimulationConstants.WalkerFootLiftMillimeters,
                    FixedTrigScale));
        }
    }

    private bool CanBeginWalkerFootSwing(
        int footIndex,
        long distanceSquared,
        int threshold)
    {
        long forcedThreshold = threshold * 2L;
        if (distanceSquared > forcedThreshold * forcedThreshold)
        {
            return true;
        }

        int earlySwings = _walkerFeet.Count(foot =>
            foot.PhaseThirds > 0 &&
            foot.PhaseThirds <= (SimulationConstants.WalkerFootPhaseEnd / 2) * 3);
        if (earlySwings >= SimulationConstants.WalkerFootMaximumEarlySwings)
        {
            return false;
        }

        bool sameParityReady = false;
        bool predecessorClear = true;
        for (int otherIndex = 0; otherIndex < _walkerFeet.Count; otherIndex++)
        {
            int otherPhase = _walkerFeet[otherIndex].PhaseThirds;
            bool otherReady = otherPhase == 0 ||
                otherPhase > (SimulationConstants.WalkerFootPhaseEnd / 2) * 3;
            if (otherReady && otherIndex != footIndex)
            {
                if ((otherIndex & 1) == (footIndex & 1))
                {
                    sameParityReady = true;
                }
            }
            else if (otherIndex == footIndex - 1)
            {
                predecessorClear = false;
            }
        }

        return sameParityReady && predecessorClear;
    }

    private void BuildWalkerFeet()
    {
        _walkerFeet.Clear();
        for (int index = 0;
             index < SimulationConstants.WalkerFootStanceOffsetsMillimeters.Count;
             index++)
        {
            SimVector2 stance = SimulationConstants.WalkerFootStanceOffsetsMillimeters[index];
            SimVector2 position = NaturalWalkerFootPosition(stance);
            _walkerFeet.Add(new MutableWalkerFoot
            {
                Id = index,
                StanceOffset = stance,
                Position = position,
                GroundElevationMillimeters =
                    Level100Terrain.Instance.SampleGroundElevationMillimeters(position),
            });
        }
    }

    private void AlignWalkerFeetToNaturalTargets()
    {
        foreach (MutableWalkerFoot foot in _walkerFeet)
        {
            foot.Position = NaturalWalkerFootPosition(foot.StanceOffset);
            foot.GroundElevationMillimeters =
                Level100Terrain.Instance.SampleGroundElevationMillimeters(foot.Position);
            foot.PhaseThirds = 0;
            foot.LiftMillimeters = 0;
        }
    }

    private SimVector2 NaturalWalkerFootPosition(SimVector2 stanceOffset)
    {
        SimVector2 playerPosition = PlayerPosition;
        (int sin, int cos) = FixedSinCos(_facingYawMicroRad);
        return new SimVector2(
            playerPosition.X + DivideRoundNearest(
                ((long)stanceOffset.X * cos) - ((long)stanceOffset.Z * sin),
                FixedTrigScale),
            playerPosition.Z + DivideRoundNearest(
                ((long)stanceOffset.X * sin) + ((long)stanceOffset.Z * cos),
                FixedTrigScale));
    }

    private void UpdateLevel100TriggerActors()
    {
        DrainAndDispatchLevel100ActorFacts();

        foreach (Level100ActorSnapshot trigger in _level100Actors.Snapshot.Actors
            .Where(actor => actor.Trigger.HasValue && actor.Pose is not null)
            .OrderBy(actor => actor.ActorId.Value))
        {
            if (trigger.TriggerEventDispatched || trigger.TriggerEntered)
            {
                continue;
            }

            Level100MissionJetModeState jetModeState =
                Level100MissionTiming.JetModeState(
                    _mode,
                    _transition,
                    _ticksSinceGroundContact);
            if (trigger.Active &&
                (!Level100MissionTiming.RequiresNotInJetMode(trigger.Trigger!.Value) ||
                 jetModeState ==
                    Level100MissionJetModeState.NotInJetMode) &&
                IsWithinLevel100Trigger(
                    PlayerPosition,
                    PlayerElevationMillimeters,
                    trigger.Pose!.PositionMillimeters))
            {
                // The side actor owns its factual overlap and released pause;
                // LevelScript sees only the resulting named event.
                _level100Actors.BeginTriggerDispatch(
                    trigger.ActorId,
                    jetModeState);
                DrainAndDispatchLevel100ActorFacts();
            }
        }
    }

    // Level100ObjectiveTriggerRadius is a centre-to-centre *sphere* overlap
    // threshold (authored 5.0 plus the single-player CBattleEngine 0.4 that
    // CBattleEngine::GetRadius returns), and the released engine carries one
    // isotropic radius per thing -- CThing builds its own extent as
    // FVector(r, r, r) (references/Onslaught/thing.cpp:231-236, 519-520).
    // Testing it in the horizontal plane alone let a jet satisfy
    // "Reached Target Zone N" by passing 12 m overhead, which would make the
    // released landing lesson (HELP_RETRO) decorative: measured, all three of
    // beats 6, 8 and 10 completed at 11-13 m up in level flight, never landing.
    //
    // All five Level 100 trigger volumes are authored at retail Z = 0, and
    // released CThing::Init (0x004F34A0) raises an authored thing to the height
    // field sample -- see local-lab/STATIC-OBJECT-SEATING-2026-07-26.md.
    // Without that the test would be stricter than retail by the terrain height
    // under each volume: 898 mm at Target Zone 2, which costs 434 mm of
    // horizontal tolerance.
    //
    // Level100ActorRegistry.SeatOnGround now owns that seating for EVERY actor
    // class rather than for ground vehicles alone, so a volume arrives here
    // already seated and this line is idempotent on it -- the registry's seat
    // is max(authored, ground, water), and max(that, ground) is that. It is
    // kept because a pose can also arrive from a restored snapshot or from
    // SetPose, neither of which re-runs Init, and the containment test must not
    // depend on which of those produced the pose.
    private bool IsWithinLevel100Trigger(
        SimVector2 position,
        int elevationMillimeters,
        SimVector3 trigger)
    {
        var triggerHorizontal = new SimVector2(trigger.X, trigger.Z);
        int seatedTriggerY = Math.Max(
            trigger.Y,
            Level100Terrain.Instance.SampleGroundElevationMillimeters(
                triggerHorizontal));
        long deltaX = (long)position.X - trigger.X;
        long deltaY = (long)elevationMillimeters - seatedTriggerY;
        long deltaZ = (long)position.Z - trigger.Z;
        long radius = SimulationConstants.Level100ObjectiveTriggerRadius;
        return (deltaX * deltaX) + (deltaY * deltaY) + (deltaZ * deltaZ) <=
            radius * radius;
    }

    private static SimVector2 ClampMagnitude(SimVector2 value, int maximum)
    {
        long magnitudeSquared = ((long)value.X * value.X) + ((long)value.Z * value.Z);
        long maximumSquared = (long)maximum * maximum;
        if (magnitudeSquared <= maximumSquared)
        {
            return value;
        }

        int magnitude = IntegerSquareRoot(magnitudeSquared);
        if ((long)magnitude * magnitude < magnitudeSquared)
        {
            magnitude++;
        }

        return new SimVector2(
            value.X * maximum / magnitude,
            value.Z * maximum / magnitude);
    }

    private static int IntegerSquareRoot(long value)
    {
        long low = 0;
        long high = Math.Min(value, int.MaxValue);
        long result = 0;
        while (low <= high)
        {
            long middle = low + ((high - low) / 2);
            long square = (long)middle * middle;
            if (square <= value)
            {
                result = middle;
                low = middle + 1;
            }
            else
            {
                high = middle - 1;
            }
        }

        return checked((int)result);
    }

    /// <summary>
    /// Full turn rounded to integer micro-radians. Keeps yaw in (−half, half].
    /// </summary>
    private const int TwoPiMicroRad = 6_283_185;

    private static int NormalizeMicroRad(int microRad)
    {
        int wrapped = microRad % TwoPiMicroRad;
        if (wrapped > TwoPiMicroRad / 2)
        {
            wrapped -= TwoPiMicroRad;
        }
        else if (wrapped <= -(TwoPiMicroRad / 2))
        {
            wrapped += TwoPiMicroRad;
        }

        return wrapped;
    }

    private void QuantizeFacingFromYaw()
    {
        // Eight-way snap from continuous yaw for FacingX/Z and fire aim.
        int yaw = NormalizeMicroRad(_facingYawMicroRad);
        int sector = (int)((long)((yaw + TwoPiMicroRad) % TwoPiMicroRad) * 8 / TwoPiMicroRad);
        (_facingX, _facingZ) = sector switch
        {
            0 => ((sbyte)0, (sbyte)1),
            1 => ((sbyte)1, (sbyte)1),
            2 => ((sbyte)1, (sbyte)0),
            3 => ((sbyte)1, (sbyte)-1),
            4 => ((sbyte)0, (sbyte)-1),
            5 => ((sbyte)-1, (sbyte)-1),
            6 => ((sbyte)-1, (sbyte)0),
            _ => ((sbyte)-1, (sbyte)1),
        };
    }

    private void UpdateResources(bool playerPartMoveStarted)
    {
        // The released outer CBattleEngine::Move does not call WalkerPart::Move
        // or JetPart::Move once IsDying() is true. Resource regeneration/drain
        // belongs to those part moves, so a pre-Move lethal hit skips it. A
        // lethal water skim occurs near the END of JetPart::Move, after its
        // energy work; preserve that already-started part update even though
        // the lifecycle has changed by the time this method commits it.
        if (!playerPartMoveStarted)
        {
            return;
        }

        if (!_jetMovedThisTick)
        {
            if (CanRechargeWalkerEnergy(_ticksSinceGroundContact))
            {
                _energy = Math.Min(
                    SimulationConstants.MaximumEnergy,
                    _energy + SimulationConstants.WalkerEnergyRegenerationPerTick);
            }
            if (_energy == SimulationConstants.MaximumEnergy)
            {
                _jetEnergyDrainRemainderMicro = 0;
            }
            _shield = _energy;
            return;
        }

        int previousEnergy = _energy;
        _energy = Math.Max(0, _energy - _jetEnergyDrainThisTick);
        if (previousEnergy > 0 && _energy == 0)
        {
            _jetEnergyDrainRemainderMicro = 0;
        }
        _shield = 0;
    }

    /// <summary>
    /// Released WalkerPart recharge gate. The pristine body compares elapsed
    /// time since ground contact strictly below 0.3 seconds.
    /// </summary>
    internal static bool CanRechargeWalkerEnergy(int ticksSinceGroundContact)
    {
        if (ticksSinceGroundContact < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(ticksSinceGroundContact));
        }

        return ticksSinceGroundContact <
            SimulationConstants.WalkerRechargeGroundContactTicks;
    }

    private void UpdateAugmentState()
    {
        if (_level100Actors.GetLifecycle(_level100PlayerActorId) !=
            Level100ActorLifecycle.Alive)
        {
            return;
        }

        // CBattleEngine::Move handles this after Damage has accumulated charge.
        // Aquila Prototype's primary Pulse Cannon Pod uses an available store,
        // so its AugmentWeapon gate succeeds when the released 10.0 threshold
        // is reached. Damage itself never flips the active flag.
        Level100PlayerDamageState advanced = Level100PlayerDamage.AdvanceAugment(
            new Level100PlayerDamageState(
                PlayerHull,
                _energy,
                _shield,
                _augmentCharge,
                _augmentActive));
        _augmentCharge = advanced.AugmentChargeMilli;
        _augmentActive = advanced.AugmentActive;
    }

    private bool ApplyLevel100PlayerDamage(
        int incomingDamageMilliLife,
        bool damageShields,
        Level100PlayerDamageSource source,
        out bool requestsDeath)
    {
        requestsDeath = false;
        if (_level100Actors.GetLifecycle(_level100PlayerActorId) !=
            Level100ActorLifecycle.Alive)
        {
            return false;
        }

        Level100PlayerDamageResult result = Level100PlayerDamage.Apply(
            new Level100PlayerDamageState(
                PlayerHull,
                _energy,
                _shield,
                _augmentCharge,
                _augmentActive),
            incomingDamageMilliLife,
            damageShields,
            isWalker: _mode == VehicleMode.Walker &&
                _transition == VehicleTransition.None);

        _energy = result.State.EnergyMilli;
        _shield = result.State.ShieldMilli;
        _augmentCharge = result.State.AugmentChargeMilli;
        _augmentActive = result.State.AugmentActive;
        _level100Destruction.SetExternalHealth(
            _level100PlayerActorId,
            Math.Max(0, result.State.LifeMilli));
        _playerDamageEvents.Add(new Level100PlayerDamageEvent(
            _tick,
            source,
            incomingDamageMilliLife,
            result.ShieldAbsorbedMilliLife,
            result.LifeDamageMilliLife,
            result.RequestsDeath));
        requestsDeath = result.RequestsDeath;
        return true;
    }

    private void CompleteLevel100PlayerDamageDeath(bool requestsDeath)
    {
        if (!requestsDeath)
        {
            return;
        }

        DestroyLevel100PlayerActor();
        _level100Mission.ReportPlayerDeath();
    }

    private void TryFire(SimInput input)
    {
        if (!input.HasAction(SimActions.Fire) ||
            _transformTicksRemaining != 0)
        {
            return;
        }

        if (_mode == VehicleMode.Jet)
        {
            Level100MissionWeapon selected =
                _level100PlayerWeapons.GetCurrentWeapon(VehicleMode.Jet);
            if (!_level100PlayerWeapons.IsActive(selected))
            {
                return;
            }

            // Missile Pod selection is now represented exactly, but its
            // released launch/round law is not. Do not synthesize a shot.
            if (selected == Level100MissionWeapon.MissilePod)
            {
                return;
            }
            if (selected != Level100MissionWeapon.MechVulcanCannon)
            {
                throw new InvalidOperationException(
                    $"Unsupported Level 100 jet weapon {selected}.");
            }

            // Aquila Prototype's JetPart owns Mech Vulcan Cannon followed by Missile
            // Pod. ResetConfiguration selects slot zero and jet fire never
            // routes through the walker-only primary Pulse Cannon.
            if (_fireCooldownTicksRemaining != 0)
            {
                return;
            }

            EmitFlightEvent(
                AquilaFlightEvents.JetWeaponFireRequested,
                AquilaJetWeapon.MechVulcanCannon);
            EmitWeaponFireEvent(
                Level100PlayerWeapon.MechVulcanCannon,
                SimulationConstants.MechVulcanVolleySize);
            _fireCooldownTicksRemaining = SimulationConstants.MechVulcanReloadTicks;

            // The jet weapon now actually launches. Until this change the jet
            // branch emitted a presentation event and nothing else, so the
            // player had no working weapon at all during beats 7 and 9 - the
            // LevelScript disables both walker weapons there, which is what
            // TUTORIAL_THROTTLE_MOD is teaching. `Mech Vulcan Cannon` fires
            // CWeaponVolleySize 2 `Mech Air Bullet` rounds; see
            // SimulationConstants for the shipped record and for the two
            // CWeaponLaunchSequence muzzle offsets that are read but not
            // modelled. Energy is not spent here because the jet weapon's
            // consumption field has no decoded value-id, and inventing one
            // would be an unproven behaviour claim.
            for (int round = 0;
                 round < SimulationConstants.MechVulcanVolleySize;
                 round++)
            {
                LaunchWalkerRound(
                    SimulationConstants.MechAirBulletSpeedPerTick,
                    SimulationConstants.MechAirBulletLifetimeTicks,
                    Level100ContactMechanics.PulseRadiusMillimeters,
                    SimulationConstants.MechAirBulletDamageBits);
            }
            return;
        }

        Level100MissionWeapon walkerSelected =
            _level100PlayerWeapons.GetCurrentWeapon(VehicleMode.Walker);
        if (!_level100PlayerWeapons.IsActive(walkerSelected))
        {
            return;
        }

        if (walkerSelected == Level100MissionWeapon.PulseCannonPod)
        {
            if (_fireCooldownTicksRemaining != 0 ||
                _energy < SimulationConstants.FireEnergyCost)
            {
                return;
            }

            _energy -= SimulationConstants.FireEnergyCost;
            _fireCooldownTicksRemaining = SimulationConstants.PulseCannonReloadTicks;
            // `Mech Pulse Cannon Charged` carries no CWeaponVolleySize node, so
            // it takes the shipped default of 1 and one release is one round.
            EmitWeaponFireEvent(Level100PlayerWeapon.PulseCannonPod, 1);
            LaunchWalkerRound(
                SimulationConstants.ProjectileSpeedPerTick,
                SimulationConstants.ProjectileLifetimeTicks,
                Level100ContactMechanics.PulseRadiusMillimeters,
                Level100DestructionState.PulseDamageBits);
            return;
        }

        // The released script disables the Pulse Cannon Pod and enables the
        // Mech Twin Vulcan Cannon at the end of the first firing-range
        // exercise, so from that point the walker's only weapon is the Twin
        // Vulcan. Its weapon mode fires CWeaponVolleySize 4 Mech Bullet rounds
        // per CWeaponReloadTime 0.05 s. CWeaponInaccuracy 0.006981317 rad and
        // the four CWeaponLaunchSequence muzzle entries are read but not
        // modelled: neither a released scatter sequence nor released muzzle
        // offsets are established, and inventing either would be an unproven
        // behaviour claim. The volley therefore leaves the one evidenced
        // BattleEngine emitter along the aim ray.
        if (walkerSelected != Level100MissionWeapon.MechTwinVulcanCannon)
        {
            throw new InvalidOperationException(
                $"Unsupported Level 100 walker weapon {walkerSelected}.");
        }
        if (_twinVulcanReloadTicksRemaining > 0 ||
            _energy < SimulationConstants.TwinVulcanFireEnergyCost)
        {
            return;
        }

        _energy -= SimulationConstants.TwinVulcanFireEnergyCost;
        _twinVulcanReloadTicksRemaining +=
            SimulationConstants.TwinVulcanReloadTicks;
        EmitWeaponFireEvent(
            Level100PlayerWeapon.MechTwinVulcanCannon,
            SimulationConstants.TwinVulcanVolleySize);
        for (int round = 0; round < SimulationConstants.TwinVulcanVolleySize; round++)
        {
            LaunchWalkerRound(
                SimulationConstants.MechBulletSpeedPerTick,
                SimulationConstants.MechBulletLifetimeTicks,
                Level100ContactMechanics.PulseRadiusMillimeters,
                Level100DestructionState.MechBulletDamageBits);
        }
    }

    /// <summary>
    /// Emits one round from the evidenced cockpit emitter along the current
    /// aim. Speed, lifetime, contact radius and damage are the round's, not
    /// the pulse's.
    /// </summary>
    private void LaunchWalkerRound(
        int speedPerTick,
        int lifetimeTicks,
        int contactRadiusMillimeters,
        uint damageBits)
    {
        (int sin, int cos) = FixedSinCos(_facingYawMicroRad);
        (int pitchSin, int pitchCos) = FixedSinCos(_facingPitchMicroRad);
        int horizontalSpeed = DivideRoundNearest(
            (long)pitchCos * speedPerTick,
            FixedTrigScale);
        int velocityX = DivideRoundNearest(
            -(long)sin * horizontalSpeed,
            FixedTrigScale);
        int velocityZ = DivideRoundNearest(
            (long)cos * horizontalSpeed,
            FixedTrigScale);
        int verticalVelocity = DivideRoundNearest(
            -(long)pitchSin * speedPerTick,
            FixedTrigScale);
        int emitterForwardPlane = DivideRoundNearest(
            ((long)SimulationConstants.PulseCannonEmitterForwardMillimeters * pitchCos) +
            ((long)SimulationConstants.PulseCannonEmitterUpMillimeters * pitchSin),
            FixedTrigScale);
        int emitterVerticalOffset = DivideRoundNearest(
            (-(long)SimulationConstants.PulseCannonEmitterForwardMillimeters * pitchSin) +
            ((long)SimulationConstants.PulseCannonEmitterUpMillimeters * pitchCos),
            FixedTrigScale);
        int emitterOffsetX = DivideRoundNearest(
            ((long)SimulationConstants.PulseCannonEmitterRightMillimeters * cos) -
            ((long)emitterForwardPlane * sin),
            FixedTrigScale);
        int emitterOffsetZ = DivideRoundNearest(
            ((long)SimulationConstants.PulseCannonEmitterRightMillimeters * sin) +
            ((long)emitterForwardPlane * cos),
            FixedTrigScale);

        SimVector2 playerPosition = PlayerPosition;
        _projectiles.Add(new MutableProjectile
        {
            Id = _nextProjectileId++,
            Position = new SimVector2(
                playerPosition.X + emitterOffsetX,
                playerPosition.Z + emitterOffsetZ),
            Velocity = new SimVector2(velocityX, velocityZ),
            ElevationMillimeters =
                PlayerElevationMillimeters + emitterVerticalOffset,
            VerticalVelocityMillimetersPerTick = verticalVelocity,
            RemainingTicks = lifetimeTicks,
            ContactRadiusMillimeters = contactRadiusMillimeters,
            DamageBits = damageBits,
        });
    }

    private void UpdateProjectiles()
    {
        for (int projectileIndex = _projectiles.Count - 1; projectileIndex >= 0; projectileIndex--)
        {
            MutableProjectile projectile = _projectiles[projectileIndex];
            var start = new SimVector3(
                projectile.Position.X,
                projectile.ElevationMillimeters,
                projectile.Position.Z);
            var end = new SimVector3(
                checked(projectile.Position.X + projectile.Velocity.X),
                checked(projectile.ElevationMillimeters +
                    projectile.VerticalVelocityMillimetersPerTick),
                checked(projectile.Position.Z + projectile.Velocity.Z));
            projectile.Position = new SimVector2(end.X, end.Z);
            projectile.ElevationMillimeters = end.Y;
            projectile.RemainingTicks--;

            bool hit = _level100Destruction.TryApplyRoundSweep(
                start,
                end,
                projectile.ContactRadiusMillimeters,
                projectile.DamageBits,
                out _);
            if (hit)
            {
                DrainAndDispatchLevel100ActorFacts();
            }

            if (hit || projectile.RemainingTicks <= 0)
            {
                _projectiles.RemoveAt(projectileIndex);
            }
        }
    }

    private void ResetDynamicState()
    {
        _nextProjectileId = 1;
        _mode = VehicleMode.Walker;
        _transition = VehicleTransition.None;
        SimVector2 initialPosition = SimVector2.Zero;
        _playerGroundElevationMillimeters =
            Level100Terrain.Instance.SampleGroundElevationMillimeters(initialPosition);
        _playerGroundDeltaMillimeters = 0;
        _playerOnGround = true;
        _playerInWater =
            _playerGroundElevationMillimeters <= Level100Terrain.WaterElevationMillimeters;
        _playerWaterFailure = false;
        _playerOnSteepSlope = false;
        _landingJetsActive = false;
        _groundImpactSpeedMillimetersPerTick = 0;
        _flightEvents.Clear();
        _weaponFireEvents.Clear();
        _playerDamageEvents.Clear();
        _facingYawMicroRad = SimulationConstants.Level100PlayerStartYawMicroRad;
        QuantizeFacingFromYaw();
        _walkerYawVelocityMicroRadPerTick = 0;
        _facingPitchMicroRad = 0;
        _walkerPitchVelocityMicroRadPerTick = 0;
        _bodyRollMicroRad = 0;
        _rollVelocityMicroRadPerTick = 0;
        _walkerLastMoveXPermille = 0;
        _walkerLastMoveZPermille = 0;
        int initialHardMoveTick =
            _tick - SimulationConstants.WalkerDashInitialHistoryTicks;
        _walkerLastHardLeftTick = initialHardMoveTick;
        _walkerLastHardRightTick = initialHardMoveTick;
        _walkerLastHardForwardTick = initialHardMoveTick;
        _walkerLastHardBackwardTick = initialHardMoveTick;
        _walkerDashTicksRemaining = 0;
        _zoomPermille = SimulationConstants.ZoomOutPermille;
        _desiredZoomPermille = SimulationConstants.ZoomOutPermille;
        _energy = SimulationConstants.MaximumEnergy;
        _shield = SimulationConstants.MaximumShield;
        _augmentCharge = 0;
        _augmentActive = false;
        _transformTicksRemaining = 0;
        _fireCooldownTicksRemaining = 0;
        _twinVulcanReloadTicksRemaining = 0;
        _level100OpeningTicksRemaining = SimulationConstants.Level100OpeningPanTicks;
        // A configured weapon starts ACTIVE.
        //
        // CORRECTION, recorded here because a commit message cannot be edited:
        // 424483da argued this from the BINARY and said +0x9c "is exactly what
        // the Enable (0x004fe2b0) and Disable (0x004fe310) list-walkers write".
        // That call path is WRONG and was refuted on 2026-07-26. Those two are
        // shared Unit-family virtuals over this+0x17C and are not the player's
        // path at all; Battle Engine script calls route through 0x0040DC30 /
        // 0x0040DC60 to the part-specific writers at 0x004127A0 / 0x00412830
        // (jet) and 0x00414970 / 0x00414A40 (walker). So there are at least SIX
        // direct writers, not two, plus configuration reset as a further
        // semantic path. Do not cite that commit's addresses.
        //
        // The CONCLUSION survives untouched, because it rests on the source and
        // the shipped scripts below rather than on that call path. But it is
        // supported STATICALLY, not behaviourally: no copied-retail watchpoint
        // on +0x9c from construction through beat 7 exists, and no capture shows
        // a Mech Vulcan round fired with no prior script enable. Until one does,
        // do not restate this as observed retail behaviour.
        //
        // `CBattleEngineJetPart::
        // ResetConfiguration` and `CBattleEngineWalkerPart::ResetConfiguration`
        // spawn one CWeapon per name in the configuration's weapon list, call
        // `weapon->Init(init)` and append it; neither ever calls
        // `SetActive(FALSE)`, and `EnableWeapon`/`DisableWeapon` only flip that
        // flag on a weapon that is already owned
        // (references/Onslaught/BattleEngineJetPart.cpp:976-1044,
        // BattleEngineWalkerPart.cpp:1030-1065).
        //
        // The shipped Level 100 object proves the same thing on its own, and
        // more sharply. Across all 25 hash-pinned compiled scripts,
        // `Mech Vulcan Cannon` and `Missile Pod` are named exactly once each -
        // in `DisableWeapon` inside `event("Abort Airborne Drones")` - and are
        // never enabled anywhere; and `init()` opens by *disabling*
        // `Mech Twin Vulcan Cannon` and `Pulse Cannon Pod`. Under a
        // start-disabled model every one of those four instructions is dead
        // code and beat 7 is unwinnable, because the script disables both
        // walker weapons at the end of beat 5 and the jet's Mech Vulcan Cannon
        // is the only weapon the player has for the first drone wave. Under
        // start-enabled every one of them is necessary. Aquila Prototype ships
        // walker `["Mech Twin Vulcan Cannon"]`, mPrimaryWeapon
        // `"Pulse Cannon Pod"` and jet `["Mech Vulcan Cannon", "Missile Pod"]`
        // (battle engine configurations.dat @0x2d2), so all four are owned.
        //
        // Measured before this change: a `SimInput`-only autopilot that reached
        // beat 7 held Fire in jet mode with `Level100MechVulcanCannonEnabled`
        // false for 570 released seconds and launched no round, because
        // `TryFire` returns on that flag. Flight mode gets the same treatment
        // for the same reason; the released `init()` disables it explicitly on
        // the first tick, so the observable start state is unchanged there.
        _level100FlightEnabled = true;
        _level100PlayerWeapons.ResetConfiguration();
        _level100HudEmphasisMask = 0;
        _walkerToJetUsesTakeoffLift = false;
        _walkerToJetLiftApplied = false;
        _ticksSinceGroundContact = 0;
        _jetTicksSinceTransform = 0;
        _jetStrafeTicksRemaining = 0;
        _jetStrafeAccelerationRemainder = 0;
        _jetEnergyDrainRemainderMicro = 0;
        _jetThrusterPermille = 500;
        _jetGroundedSlowTicks = 0;
        _jetStallTicks = 0;
        _jetEnergyDrainThisTick = 0;
        _jetMovedThisTick = false;
        _projectiles.Clear();
        _level100Actors = new Level100ActorRegistry(_level100ActorDefinitions);
        _level100ActorMechanics = new Level100ActorMechanics(
            _level100Actors,
            _level100ActorDefinitions);
        _level100Destruction = new Level100DestructionRuntime(_level100Actors);
        _level100PlayerActorId = _level100Actors.GetThingRef("Player 1") ??
            throw new InvalidOperationException("Level 100 Player is missing.");
        _level100Actors.SetHealth(_level100PlayerActorId, SimulationConstants.MaximumHull);
        _level100Actors.Activate(_level100PlayerActorId);
        CommitLevel100PlayerPose(
            initialPosition,
            _playerGroundElevationMillimeters +
                Level100Terrain.WalkerCenterOfGravityMillimeters,
            SimVector2.Zero,
            0);
        BuildWalkerFeet();
        _level100ActorScripts = new Level100ActorScriptRuntime(
            _level100Actors,
            _level100PlayerActorId);
        _level100ActorScripts.InitializeReleasedScripts();
        _level100MissionEvents.Clear();
        _level100ActorScriptCommands.Clear();
        _level100Mission = new Level100Mission(
            _level100Actors,
            _level100PlayerActorId,
            _level100TutorialProgress,
            PlayerHull);
        SyncLevel100PlayerState();
        PumpLevel100EventBus();
    }

    private WorldSnapshot CreateSnapshot()
    {
        Level100ActorSnapshot player = _level100Actors.GetActor(_level100PlayerActorId);
        SimVector2 playerPosition = new(
            player.Pose.PositionMillimeters.X,
            player.Pose.PositionMillimeters.Z);
        SimVector2 playerVelocity = new(
            player.Pose.LinearVelocityMillimetersPerTick.X,
            player.Pose.LinearVelocityMillimetersPerTick.Z);
        ProjectileSnapshot[] projectiles = _projectiles
            .OrderBy(projectile => projectile.Id)
            .Select(projectile => new ProjectileSnapshot(
                projectile.Id,
                projectile.Position,
                projectile.Velocity,
                projectile.ElevationMillimeters,
                projectile.VerticalVelocityMillimetersPerTick,
                projectile.RemainingTicks))
            .ToArray();
        WalkerFootContactSnapshot[] walkerFeet = _walkerFeet
            .OrderBy(foot => foot.Id)
            .Select(foot => new WalkerFootContactSnapshot(
                foot.Id,
                foot.Position,
                foot.GroundElevationMillimeters,
                foot.PhaseThirds,
                foot.LiftMillimeters))
            .ToArray();
        return new WorldSnapshot(
            _tick,
            _seed,
            _level100TutorialProgress,
            _mode,
            _transition,
            playerPosition,
            playerVelocity,
            _playerGroundElevationMillimeters,
            _playerGroundDeltaMillimeters,
            player.Pose.PositionMillimeters.Y,
            player.Pose.LinearVelocityMillimetersPerTick.Y,
            _playerOnGround,
            _playerInWater,
            _playerWaterFailure,
            _playerOnSteepSlope,
            _landingJetsActive,
            _groundImpactSpeedMillimetersPerTick,
            Array.AsReadOnly(_flightEvents.ToArray()),
            _facingX,
            _facingZ,
            _facingYawMicroRad,
            _walkerYawVelocityMicroRadPerTick,
            _facingPitchMicroRad,
            _walkerPitchVelocityMicroRadPerTick,
            _bodyRollMicroRad,
            _rollVelocityMicroRadPerTick,
            _walkerLastMoveXPermille,
            _walkerLastMoveZPermille,
            _walkerLastHardLeftTick,
            _walkerLastHardRightTick,
            _walkerLastHardForwardTick,
            _walkerLastHardBackwardTick,
            _walkerDashTicksRemaining,
            _energy,
            _shield,
            player.Health,
            _augmentCharge,
            _augmentActive,
            Array.AsReadOnly(_playerDamageEvents.ToArray()),
            _transformTicksRemaining,
            _walkerToJetUsesTakeoffLift,
            _walkerToJetLiftApplied,
            _ticksSinceGroundContact,
            _jetTicksSinceTransform,
            _jetStrafeTicksRemaining,
            _jetStrafeAccelerationRemainder,
            _jetEnergyDrainRemainderMicro,
            _jetThrusterPermille,
            _jetGroundedSlowTicks,
            _jetStallTicks,
            _fireCooldownTicksRemaining,
            _twinVulcanReloadTicksRemaining,
            _level100OpeningTicksRemaining,
            player.Active,
            _level100FlightEnabled,
            _level100PlayerWeapons.IsActive(Level100MissionWeapon.PulseCannonPod),
            _level100PlayerWeapons.IsActive(Level100MissionWeapon.MechTwinVulcanCannon),
            _level100PlayerWeapons.IsActive(Level100MissionWeapon.MechVulcanCannon),
            _level100PlayerWeapons.IsActive(Level100MissionWeapon.MissilePod),
            _level100PlayerWeapons.WalkerSelectedWeapon,
            _level100PlayerWeapons.JetSelectedWeapon,
            _zoomPermille,
            _desiredZoomPermille,
            _level100HudEmphasisMask,
            _level100Mission.Snapshot,
            Array.AsReadOnly(_level100MissionEvents.ToArray()),
            _level100Actors.Snapshot,
            _level100Destruction.Snapshot,
            _level100Destruction.Events,
            Array.AsReadOnly(_weaponFireEvents.ToArray()),
            _level100ActorScripts.Snapshot,
            Array.AsReadOnly(_level100ActorScriptCommands.ToArray()),
            _level100ActorMechanics.Snapshot,
            _nextProjectileId,
            Array.AsReadOnly(projectiles),
            Array.AsReadOnly(walkerFeet));
    }

}
