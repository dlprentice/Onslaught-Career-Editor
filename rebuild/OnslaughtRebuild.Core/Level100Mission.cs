// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

/// <summary>
/// Deterministic owner for the exact released Level 100 LevelScript object.
/// It implements only the opcodes and native calls reached by that payload;
/// mechanics and presentation consume commands or report explicit facts.
/// </summary>
public sealed class Level100Mission
{
    private readonly Level100MissionProgram _program;
    private readonly Level100ActorRegistry _actors;
    private readonly Level100ActorId _playerActorId;
    private readonly Level100ScriptValue[] _locals;
    private readonly Queue<QueuedEvent> _eventQueue = new();
    private readonly List<Continuation> _continuations = [];
    private readonly List<Level100MissionEvent> _events = [];
    private readonly ObjectiveState[] _primaryObjectives =
    [
        new(1, 0, Level100PrimaryObjectiveStatus.Uninitialized),
        new(2, 0, Level100PrimaryObjectiveStatus.Uninitialized),
        new(3, 0, Level100PrimaryObjectiveStatus.Uninitialized),
        new(4, 0, Level100PrimaryObjectiveStatus.Uninitialized),
    ];

    private Execution? _activeExecution;
    private long _nextSequence = 1;
    private int _tick;
    private bool _initializerRan;
    private Level100MissionOutcome _outcome = Level100MissionOutcome.Running;
    private Level100MissionTerminalState _terminalState;
    private Level100MissionFailureReason _failureReason;
    private int _failureTextId;
    private int _terminalTicksRemaining;
    private readonly int _initialPlayerHealth;
    private int _latestPlayerHealth;
    private int _observedPlayerHealth;
    private bool _playerActive = true;
    private bool _flightModeEnabled = true;
    private Level100MissionWeaponAvailability _pulseCannonAvailability;
    private Level100MissionWeaponAvailability _twinVulcanAvailability;
    private Level100MissionWeaponAvailability _mechVulcanAvailability;
    private Level100MissionWeaponAvailability _missilePodAvailability;
    private string? _navigationObjective;
    private bool _tutorialIntroduction;
    private bool _tutorialPulseCannon;
    private bool _tutorialVulcanCannon;
    private bool _tutorialStatusBars;
    private int _scoreDelta;
    public Level100Mission(
        Level100ActorRegistry actors,
        Level100ActorId playerActorId,
        Level100TutorialProgress tutorialProgress = default,
        int initialPlayerHealth = SimulationConstants.MaximumHull)
    {
        if (initialPlayerHealth <= 0)
        {
            throw new ArgumentOutOfRangeException(nameof(initialPlayerHealth));
        }

        _program = Level100MissionProgram.LoadEmbedded();
        _actors = actors ?? throw new ArgumentNullException(nameof(actors));
        _playerActorId = playerActorId;
        if (_actors.GetThingTypeMask(_playerActorId) !=
            Level100ReleasedThingTypeMasks.BattleEngine)
        {
            throw new ArgumentException(
                "The canonical Level 100 player must carry the released Battle Engine type bit.",
                nameof(playerActorId));
        }
        _locals = _program.Symbols.Select(symbol => symbol.InitialValue).ToArray();
        _initialPlayerHealth = initialPlayerHealth;
        _latestPlayerHealth = initialPlayerHealth;
        _observedPlayerHealth = initialPlayerHealth;
        _tutorialIntroduction = tutorialProgress.Introduction;
        _tutorialPulseCannon = tutorialProgress.PulseCannon;
        _tutorialVulcanCannon = tutorialProgress.VulcanCannon;
        _tutorialStatusBars = tutorialProgress.StatusBars;

        RunNewExecution("<global initializer>", 0);
        _initializerRan = true;
        RunNewExecution("init", _program.BuiltInEventInstructionPointers[0]);
    }

    public Level100MissionSnapshot Snapshot => new(
        _tick,
        Level100MissionProgram.ExpectedSha256,
        _initializerRan,
        _outcome == Level100MissionOutcome.Running,
        _nextSequence,
        SnapshotExecution(_activeExecution),
        _program.Symbols
            .Select((symbol, ordinal) => new Level100ScriptLocalSnapshot(
                ordinal,
                symbol.Name,
                _locals[ordinal].Snapshot))
            .ToArray(),
        _eventQueue.Select(item => new Level100QueuedEventSnapshot(
            item.Sequence,
            item.EventName)).ToArray(),
        _continuations
            .OrderBy(item => item.DueTick)
            .ThenBy(item => item.Sequence)
            .Select(item => new Level100ScriptContinuationSnapshot(
                item.Sequence,
                item.DueTick,
                item.WaitKind,
                item.WaitArgument,
                SnapshotExecution(item.Execution)))
            .ToArray(),
        _outcome,
        _terminalState,
        _failureReason,
        _failureTextId,
        _terminalTicksRemaining,
        _initialPlayerHealth,
        _latestPlayerHealth,
        _observedPlayerHealth,
        _playerActive,
        _flightModeEnabled,
        _pulseCannonAvailability,
        _twinVulcanAvailability,
        _mechVulcanAvailability,
        _missilePodAvailability,
        _navigationObjective,
        LocalBoolean(10),
        LocalBoolean(8),
        LocalInteger(4),
        _scoreDelta,
        new Level100TutorialProgress(
            _tutorialIntroduction,
            _tutorialPulseCannon,
            _tutorialVulcanCannon,
            _tutorialStatusBars),
        _primaryObjectives.Select(item => new Level100PrimaryObjectiveSnapshot(
            item.Objective,
            item.TextId,
            item.Status)).ToArray(),
        _events.ToArray());

    public Level100MissionOutcome Outcome => _outcome;

    public IReadOnlyList<Level100MissionEvent> DrainEvents()
    {
        Level100MissionEvent[] result = _events.ToArray();
        _events.Clear();
        return result;
    }

    public void AdvanceTick(int latestPlayerHealth)
    {
        if (latestPlayerHealth < 0)
        {
            throw new ArgumentOutOfRangeException(nameof(latestPlayerHealth));
        }

        _tick = checked(_tick + 1);
        _latestPlayerHealth = latestPlayerHealth;

        if (_outcome != Level100MissionOutcome.Running)
        {
            AdvanceTerminalCountdown();
            return;
        }

        while (_outcome == Level100MissionOutcome.Running)
        {
            Continuation? next = _continuations
                .Where(item => item.DueTick <= _tick)
                .OrderBy(item => item.DueTick)
                .ThenBy(item => item.Sequence)
                .FirstOrDefault();
            if (next is null)
            {
                break;
            }

            _continuations.Remove(next);
            RunExecution(next.Execution);
        }

        PumpEventQueue();
    }

    public bool SubmitInput(Level100MissionInput input) => input switch
    {
        Level100MissionInput.BrokeTutorial => QueueNamedEvent("Broke Tutorial"),
        Level100MissionInput.HitFriendlyBuilding =>
            QueueNamedEvent("Hit Friendly Building"),
        Level100MissionInput.FriendlyBuildingDestroyed =>
            QueueNamedEvent("Friendly Building Destroyed"),
        // This is the released mismatch: Facilities/Turret emit this spelling,
        // while LevelScript has no matching listener.
        Level100MissionInput.DestroyedFriendlyBuilding => false,
        Level100MissionInput.FlashThings => QueueNamedEvent("Flash things"),
        Level100MissionInput.HelpPlayer => QueueNamedEvent("Help Player"),
        Level100MissionInput.AbortAirborneDrones =>
            QueueNamedEvent("Abort Airborne Drones"),
        Level100MissionInput.EvadeFailed => QueueNamedEvent("Evade Failed"),
        _ => false,
    };

    public bool ReportPlayerHitDuringEvasion() => SubmitInput(Level100MissionInput.EvadeFailed);

    public bool ReportFriendlyBuildingHit() =>
        SubmitInput(Level100MissionInput.HitFriendlyBuilding);

    public bool ReportFriendlyBuildingDestroyed() =>
        SubmitInput(Level100MissionInput.FriendlyBuildingDestroyed);

    public bool ReportDestroyedFriendlyBuilding() =>
        SubmitInput(Level100MissionInput.DestroyedFriendlyBuilding);

    public bool ReportHelpPlayer() => SubmitInput(Level100MissionInput.HelpPlayer);

    public bool ReportAbortAirborneDrones() =>
        SubmitInput(Level100MissionInput.AbortAirborneDrones);

    public bool QueueExternalEvent(string eventName)
    {
        ArgumentException.ThrowIfNullOrEmpty(eventName);
        return QueueNamedEvent(eventName);
    }

    public bool ReportPlayerDeath() => DeclareExternalLoss(Level100MissionFailureReason.PlayerDeath);

    public bool ReportWaterLoss() => DeclareExternalLoss(Level100MissionFailureReason.WaterLoss);

    private bool QueueNamedEvent(string eventName)
    {
        if (_outcome != Level100MissionOutcome.Running ||
            !_program.NamedEventInstructionPointers.ContainsKey(eventName))
        {
            return false;
        }

        _eventQueue.Enqueue(new QueuedEvent(NextSequence(), eventName));
        PumpEventQueue();
        return true;
    }

    private void PumpEventQueue()
    {
        while (_outcome == Level100MissionOutcome.Running &&
               _activeExecution is null &&
               _eventQueue.TryDequeue(out QueuedEvent item))
        {
            RunNewExecution(
                item.EventName,
                _program.NamedEventInstructionPointers[item.EventName],
                seedNamedEventGuard: true);
        }
    }

    private void RunNewExecution(
        string eventName,
        int instructionPointer,
        bool seedNamedEventGuard = false)
    {
        if (_outcome != Level100MissionOutcome.Running)
        {
            return;
        }

        var execution = new Execution(eventName, instructionPointer);
        if (seedNamedEventGuard)
        {
            // Every released named-event record declares one dispatch
            // parameter. Level 100's event body consumes that true dispatch
            // predicate in its leading JMPFALSE instruction.
            execution.Stack.Add(Level100ScriptValue.Boolean(true));
        }

        RunExecution(execution);
    }

    private void RunExecution(Execution execution)
    {
        if (_activeExecution is not null)
        {
            throw new InvalidOperationException("LevelScript execution re-entered synchronously.");
        }

        _activeExecution = execution;
        int instructionBudget = 10_000;
        while (!execution.Stopped && _outcome == Level100MissionOutcome.Running)
        {
            if (instructionBudget-- == 0)
            {
                throw new InvalidOperationException("The released LevelScript exceeded its instruction budget.");
            }

            if ((uint)execution.InstructionPointer >= _program.Instructions.Count)
            {
                throw new InvalidOperationException(
                    $"LevelScript instruction pointer {execution.InstructionPointer} is invalid.");
            }

            Level100Instruction instruction = _program.Instructions[execution.InstructionPointer++];
            WaitRequest wait = ExecuteInstruction(execution, instruction);
            if (wait.Kind != Level100ScriptWaitKind.None)
            {
                execution.SavedStackSize = execution.Stack.Count;
                execution.Abort = false;
                _continuations.Add(new Continuation(
                    NextSequence(),
                    checked(_tick + wait.Ticks),
                    wait.Kind,
                    wait.Argument,
                    execution.Clone()));
                _activeExecution = null;
                return;
            }
        }

        _activeExecution = null;
        if (_outcome != Level100MissionOutcome.Running)
        {
            _eventQueue.Clear();
            _continuations.Clear();
        }
    }

    private WaitRequest ExecuteInstruction(Execution execution, Level100Instruction instruction)
    {
        switch (instruction.Opcode)
        {
            case 1:
                PushBinaryNumeric(execution, static (left, right) => left + right,
                    static (left, right) => unchecked(left + right));
                break;
            case 2:
                PushBinaryNumeric(execution, static (left, right) => left - right,
                    static (left, right) => unchecked(left - right));
                break;
            case 3:
                PushBinaryNumeric(execution, static (left, right) => left * right,
                    static (left, right) => unchecked(left * right));
                break;
            case 5:
                execution.Stack.Add(Local(instruction.Attribute));
                break;
            case 6:
                SetLocal(instruction.Attribute, Pop(execution));
                break;
            case 9:
                PushNumericComparison(execution, static (left, right) => left > right);
                break;
            case 10:
                PushNumericComparison(execution, static (left, right) => left < right);
                break;
            case 13:
                break;
            case 14:
                _ = Pop(execution);
                break;
            case 16:
            {
                Level100ScriptValue right = Pop(execution);
                Level100ScriptValue left = Pop(execution);
                execution.Stack.Add(Level100ScriptValue.Boolean(ValuesEqual(left, right)));
                break;
            }
            case 19:
                if (!Pop(execution).AsBoolean())
                {
                    execution.InstructionPointer = instruction.Attribute;
                }
                break;
            case 20:
                execution.InstructionPointer = instruction.Attribute;
                break;
            case 21:
                SetLocalAssigned(instruction.Attribute, Peek(execution));
                break;
            case 22:
            {
                Level100ScriptValue context = Pop(execution);
                if (context.Type != Level100ScriptValueType.Thing)
                {
                    throw new InvalidOperationException("LevelScript call context is not a thing.");
                }

                execution.CallContext = context;
                break;
            }
            case 23:
                if (execution.CallFrames.Count == 0)
                {
                    execution.Stopped = true;
                }
                else
                {
                    int last = execution.CallFrames.Count - 1;
                    execution.InstructionPointer = execution.CallFrames[last];
                    execution.CallFrames.RemoveAt(last);
                }
                break;
            case 24:
                return ExecuteNativeCall(execution, instruction.Attribute);
            default:
                throw new InvalidOperationException(
                    $"Opcode {instruction.Opcode} is outside the released Level 100 runtime slice.");
        }

        return WaitRequest.None;
    }

    private WaitRequest ExecuteNativeCall(Execution execution, int attribute)
    {
        int command = attribute & 0xff;
        int argumentCount = (attribute >> 8) & 0xff;
        int returnCount = (attribute >> 16) & 0xff;
        if ((attribute & unchecked((int)0xff000000)) != 0 || returnCount > 1)
        {
            throw new InvalidOperationException($"Invalid released native-call attribute 0x{attribute:x8}.");
        }

        var arguments = new Level100ScriptValue[argumentCount];
        for (int index = argumentCount - 1; index >= 0; index--)
        {
            arguments[index] = Pop(execution);
        }

        NativeResult result = InvokeNative(execution, command, arguments);
        execution.CallContext = null;
        execution.Stack.Add(result.Value);
        return result.Wait;
    }

    private NativeResult InvokeNative(
        Execution execution,
        int command,
        IReadOnlyList<Level100ScriptValue> arguments)
    {
        switch (command)
        {
            case 3: // SpawnThing
                RequireArguments(command, arguments, 4);
                _events.Add(new Level100SpawnThingRequested(
                    _tick,
                    RequireContext(execution),
                    arguments[0].AsString(),
                    arguments[1].AsString(),
                    arguments[2].AsInteger(),
                    arguments[3].AsString()));
                return NativeResult.Void;
            case 4: // Pause
                RequireArguments(command, arguments, 1);
                return NativeResult.Waiting(
                    Level100ScriptWaitKind.Pause,
                    Level100MissionTiming.PauseTicks(arguments[0].AsFloat()),
                    arguments[0].Scalar);
            case 5: // PostEvent
                RequireArguments(command, arguments, 1);
                PostEvent(arguments[0].AsString());
                return NativeResult.Void;
            case 9: // LevelWon
                RequireArguments(command, arguments, 0);
                DeclareWon();
                return NativeResult.Void;
            case 14: // GetThingRef
                RequireArguments(command, arguments, 1);
                string thingName = arguments[0].AsString();
                Level100ActorId? thing = _actors.GetThingRef(thingName);
                return new NativeResult(
                    thing.HasValue
                        ? Level100ScriptValue.Thing(
                            thing.Value,
                            _actors.GetThingTypeMask(thing.Value))
                        : Level100ScriptValue.NullThing,
                    WaitRequest.None);
            case 15: // Activate
                RequireArguments(command, arguments, 0);
                SetActorActivation(RequireContext(execution), true);
                return NativeResult.Void;
            case 18: // GetHealth
                RequireArguments(command, arguments, 0);
                _ = RequireContext(execution);
                _observedPlayerHealth = _latestPlayerHealth;
                return new NativeResult(
                    Level100ScriptValue.Float(_observedPlayerHealth),
                    WaitRequest.None);
            case 21: // GetPlayer
                RequireArguments(command, arguments, 1);
                return new NativeResult(
                    Level100ScriptValue.Thing(
                        _playerActorId,
                        _actors.GetThingTypeMask(_playerActorId)),
                    WaitRequest.None);
            case 23: // SetObjective
                RequireArguments(command, arguments, 0);
                SetNavigationObjective(RequireContext(execution));
                return NativeResult.Void;
            case 28: // PlayCharMessage
                RequireArguments(command, arguments, 3);
                RequestMessage(arguments, waits: false);
                return NativeResult.Void;
            case 29: // Deactivate
                RequireArguments(command, arguments, 0);
                SetActorActivation(RequireContext(execution), false);
                return NativeResult.Void;
            case 30: // UnsetObjective
                RequireArguments(command, arguments, 0);
                UnsetNavigationObjective(RequireContext(execution));
                return NativeResult.Void;
            case 34: // HighlightHudPart
                RequireArguments(command, arguments, 1);
                _events.Add(new Level100HudEmphasisChanged(
                    _tick,
                    arguments[0].AsInteger(),
                    true));
                return NativeResult.Void;
            case 35: // UnHighlightHudPart
                RequireArguments(command, arguments, 1);
                _events.Add(new Level100HudEmphasisChanged(
                    _tick,
                    arguments[0].AsInteger(),
                    false));
                return NativeResult.Void;
            case 36: // PlayCharMessageWait
                RequireArguments(command, arguments, 3);
                int messageTicks = RequestMessage(arguments, waits: true);
                return NativeResult.Waiting(
                    Level100ScriptWaitKind.CharacterMessage,
                    messageTicks,
                    arguments[1].AsInteger());
            case 83: // PrimaryObjectiveComplete
                RequireArguments(command, arguments, 2);
                SetPrimaryObjective(arguments, Level100PrimaryObjectiveStatus.Complete);
                return NativeResult.Void;
            case 85: // AddScore
                RequireArguments(command, arguments, 1);
                int delta = arguments[0].AsInteger();
                _scoreDelta = unchecked(_scoreDelta + delta);
                _events.Add(new Level100ScoreChanged(_tick, delta, _scoreDelta));
                return NativeResult.Void;
            case 87: // PrimaryObjectiveFailed
                RequireArguments(command, arguments, 2);
                SetPrimaryObjective(arguments, Level100PrimaryObjectiveStatus.Failed);
                return NativeResult.Void;
            case 98: // EnableWeapon
                RequireArguments(command, arguments, 1);
                SetWeapon(arguments[0].AsString(), true);
                return NativeResult.Void;
            case 99: // DisableWeapon
                RequireArguments(command, arguments, 1);
                SetWeapon(arguments[0].AsString(), false);
                return NativeResult.Void;
            case 100: // EnableFlightMode
                RequireArguments(command, arguments, 0);
                SetFlightMode(true);
                return NativeResult.Void;
            case 101: // DisableFlightMode
                RequireArguments(command, arguments, 0);
                SetFlightMode(false);
                return NativeResult.Void;
            case 106: // LevelLostString
                RequireArguments(command, arguments, 1);
                DeclareLost(
                    Level100MissionFailureReason.TutorialBroken,
                    arguments[0].AsInteger());
                return NativeResult.Void;
            case 118: // AddHelpMessage
                RequireArguments(command, arguments, 1);
                _events.Add(new Level100HelpRequested(_tick, arguments[0].AsInteger()));
                return NativeResult.Void;
            case 124: // GetSlot
                RequireArguments(command, arguments, 1);
                return new NativeResult(
                    Level100ScriptValue.Boolean(GetTutorialSlot(arguments[0].AsInteger())),
                    WaitRequest.None);
            case 133: // SetSlotSave
                RequireArguments(command, arguments, 2);
                SetTutorialSlot(arguments[0].AsInteger(), arguments[1].AsBoolean());
                return NativeResult.Void;
            default:
                throw new InvalidOperationException(
                    $"Native call {command} is outside the released Level 100 runtime slice.");
        }
    }

    private int RequestMessage(IReadOnlyList<Level100ScriptValue> arguments, bool waits)
    {
        int speakerId = arguments[0].AsInteger();
        int messageId = arguments[1].AsInteger();
        _ = arguments[2].AsFloat();
        int ticks = Level100MissionTiming.MessagePlaybackTicks(messageId);
        _events.Add(new Level100MessageRequested(
            _tick,
            speakerId,
            messageId,
            waits,
            ticks));
        return ticks;
    }

    private void PostEvent(string eventName)
    {
        _events.Add(new Level100MissionEventPosted(_tick, eventName));
        // Retail PostEvent publishes to the event bus. If this same compiled
        // object has a matching listener, that listener is queued as well as
        // the external event fact; execution remains non-reentrant.
        if (_program.NamedEventInstructionPointers.ContainsKey(eventName))
        {
            _eventQueue.Enqueue(new QueuedEvent(NextSequence(), eventName));
        }
    }

    private void SetActorActivation(Level100ActorId actorId, bool active)
    {
        if (actorId == _playerActorId)
        {
            _playerActive = active;
            _events.Add(new Level100PlayerActivationChanged(_tick, active));
        }

        _events.Add(new Level100ActorCommandRequested(
            _tick,
            actorId,
            active ? Level100ActorCommand.Activate : Level100ActorCommand.Deactivate));
    }

    private void SetNavigationObjective(Level100ActorId actorId)
    {
        string thingName = _actors.GetActor(actorId).Name;
        _navigationObjective = thingName;
        _events.Add(new Level100NavigationObjectiveChanged(_tick, thingName));
        _events.Add(new Level100ActorCommandRequested(
            _tick,
            actorId,
            Level100ActorCommand.SetObjective));
    }

    private void UnsetNavigationObjective(Level100ActorId actorId)
    {
        string thingName = _actors.GetActor(actorId).Name;
        if (string.Equals(_navigationObjective, thingName, StringComparison.Ordinal))
        {
            _navigationObjective = null;
            _events.Add(new Level100NavigationObjectiveChanged(_tick, null));
        }

        _events.Add(new Level100ActorCommandRequested(
            _tick,
            actorId,
            Level100ActorCommand.UnsetObjective));
    }

    private void SetPrimaryObjective(
        IReadOnlyList<Level100ScriptValue> arguments,
        Level100PrimaryObjectiveStatus status)
    {
        int objective = arguments[0].AsInteger();
        int textId = arguments[1].AsInteger();
        if (objective < 1 || objective > _primaryObjectives.Length)
        {
            throw new InvalidOperationException($"Released objective {objective} is invalid.");
        }

        _primaryObjectives[objective - 1] = new ObjectiveState(objective, textId, status);
        _events.Add(new Level100PrimaryObjectiveChanged(
            _tick,
            objective,
            textId,
            status));
    }

    private void SetWeapon(string weaponName, bool enabled)
    {
        Level100MissionWeapon weapon = weaponName switch
        {
            "Pulse Cannon Pod" => Level100MissionWeapon.PulseCannonPod,
            "Mech Twin Vulcan Cannon" => Level100MissionWeapon.MechTwinVulcanCannon,
            "Mech Vulcan Cannon" => Level100MissionWeapon.MechVulcanCannon,
            "Missile Pod" => Level100MissionWeapon.MissilePod,
            _ => throw new InvalidOperationException(
                $"Released Level 100 requested unknown weapon '{weaponName}'."),
        };
        Level100MissionWeaponAvailability availability = enabled
            ? Level100MissionWeaponAvailability.Enabled
            : Level100MissionWeaponAvailability.Disabled;
        switch (weapon)
        {
            case Level100MissionWeapon.PulseCannonPod:
                _pulseCannonAvailability = availability;
                break;
            case Level100MissionWeapon.MechTwinVulcanCannon:
                _twinVulcanAvailability = availability;
                break;
            case Level100MissionWeapon.MechVulcanCannon:
                _mechVulcanAvailability = availability;
                break;
            case Level100MissionWeapon.MissilePod:
                _missilePodAvailability = availability;
                break;
            default:
                throw new ArgumentOutOfRangeException(nameof(weapon));
        }

        _events.Add(new Level100WeaponAvailabilityChanged(_tick, weapon, enabled));
    }

    private void SetFlightMode(bool enabled)
    {
        _flightModeEnabled = enabled;
        _events.Add(new Level100FlightModeAvailabilityChanged(_tick, enabled));
    }

    private bool GetTutorialSlot(int slot) => slot switch
    {
        63 => _tutorialIntroduction,
        64 => _tutorialPulseCannon,
        65 => _tutorialVulcanCannon,
        66 => _tutorialStatusBars,
        _ => throw new InvalidOperationException($"Released Level 100 requested unknown slot {slot}."),
    };

    private void SetTutorialSlot(int slot, bool value)
    {
        switch (slot)
        {
            case 63:
                _tutorialIntroduction = value;
                break;
            case 64:
                _tutorialPulseCannon = value;
                break;
            case 65:
                _tutorialVulcanCannon = value;
                break;
            case 66:
                _tutorialStatusBars = value;
                break;
            default:
                throw new InvalidOperationException(
                    $"Released Level 100 requested unknown saved slot {slot}.");
        }

        _events.Add(new Level100TutorialSlotSaved(_tick, slot));
    }

    private void DeclareWon()
    {
        if (_outcome != Level100MissionOutcome.Running)
        {
            return;
        }

        _outcome = Level100MissionOutcome.Won;
        _terminalState = Level100MissionTerminalState.SuccessCountdown;
        _terminalTicksRemaining = Level100MissionTiming.SuccessCountdownTicks;
        _events.Add(new Level100MissionOutcomeDeclared(
            _tick,
            _outcome,
            Level100MissionFailureReason.None,
            0));
        _events.Add(new Level100TerminalStateChanged(_tick, _terminalState));
    }

    private void DeclareLost(Level100MissionFailureReason reason, int failureTextId = 0)
    {
        if (_outcome != Level100MissionOutcome.Running ||
            reason == Level100MissionFailureReason.None)
        {
            return;
        }

        _outcome = Level100MissionOutcome.Lost;
        _failureReason = reason;
        _failureTextId = failureTextId;
        _terminalState = Level100MissionTerminalState.FailureCountdown;
        _terminalTicksRemaining = Level100MissionTiming.FailureCountdownTicks;
        _events.Add(new Level100MissionOutcomeDeclared(
            _tick,
            _outcome,
            reason,
            failureTextId));
        _events.Add(new Level100TerminalStateChanged(_tick, _terminalState));
    }

    private bool DeclareExternalLoss(Level100MissionFailureReason reason)
    {
        if (_outcome != Level100MissionOutcome.Running)
        {
            return false;
        }

        DeclareLost(reason);
        _activeExecution = null;
        _eventQueue.Clear();
        _continuations.Clear();
        return true;
    }

    private void AdvanceTerminalCountdown()
    {
        if (_terminalTicksRemaining == 0)
        {
            return;
        }

        _terminalTicksRemaining--;
        if (_outcome == Level100MissionOutcome.Won && _terminalTicksRemaining == 0)
        {
            _terminalState = Level100MissionTerminalState.FrontEndHandoffReady;
            _events.Add(new Level100TerminalStateChanged(_tick, _terminalState));
        }
        else if (_outcome == Level100MissionOutcome.Lost &&
                 _terminalTicksRemaining ==
                 Level100MissionTiming.FailureCountdownTicks -
                 Level100MissionTiming.FailureMenuDelayTicks)
        {
            _terminalState = Level100MissionTerminalState.FailureMenuReady;
            _events.Add(new Level100TerminalStateChanged(_tick, _terminalState));
        }
        else if (_outcome == Level100MissionOutcome.Lost && _terminalTicksRemaining == 0)
        {
            _terminalState = Level100MissionTerminalState.FailureCountdownElapsed;
            _events.Add(new Level100TerminalStateChanged(_tick, _terminalState));
        }
    }

    private long NextSequence()
    {
        long result = _nextSequence;
        _nextSequence = checked(_nextSequence + 1);
        return result;
    }

    private Level100ScriptValue Local(int ordinal)
    {
        if ((uint)ordinal >= _locals.Length)
        {
            throw new InvalidOperationException($"Released symbol ordinal {ordinal} is invalid.");
        }

        return _locals[ordinal];
    }

    private int LocalInteger(int ordinal)
    {
        Level100ScriptValue value = Local(ordinal);
        return value.Type == Level100ScriptValueType.Unset ? 0 : value.AsInteger();
    }

    private bool LocalBoolean(int ordinal)
    {
        Level100ScriptValue value = Local(ordinal);
        return value.Type != Level100ScriptValueType.Unset && value.AsBoolean();
    }

    private void SetLocal(int ordinal, Level100ScriptValue value)
    {
        _ = Local(ordinal);
        _locals[ordinal] = value;
    }

    private void SetLocalAssigned(int ordinal, Level100ScriptValue value)
    {
        Level100ScriptValue existing = Local(ordinal);
        if (existing.Type == Level100ScriptValueType.Unset || existing.Type == value.Type)
        {
            _locals[ordinal] = value;
            return;
        }

        if (existing.Type == Level100ScriptValueType.Float &&
            value.Type == Level100ScriptValueType.Integer)
        {
            _locals[ordinal] = Level100ScriptValue.Float(value.Scalar);
            return;
        }

        throw new InvalidOperationException(
            $"Released assignment cannot assign {value.Type} to {existing.Type} symbol {ordinal}.");
    }

    private static Level100ScriptValue Pop(Execution execution)
    {
        if (execution.Stack.Count == 0)
        {
            throw new InvalidOperationException("Released LevelScript stack underflow.");
        }

        int last = execution.Stack.Count - 1;
        Level100ScriptValue value = execution.Stack[last];
        execution.Stack.RemoveAt(last);
        return value;
    }

    private static Level100ScriptValue Peek(Execution execution)
    {
        if (execution.Stack.Count == 0)
        {
            throw new InvalidOperationException("Released LevelScript stack underflow.");
        }

        return execution.Stack[^1];
    }

    private static void PushBinaryNumeric(
        Execution execution,
        Func<float, float, float> floatOperation,
        Func<int, int, int> integerOperation)
    {
        Level100ScriptValue right = Pop(execution);
        Level100ScriptValue left = Pop(execution);
        if (left.Type == Level100ScriptValueType.Float ||
            right.Type == Level100ScriptValueType.Float)
        {
            execution.Stack.Add(Level100ScriptValue.Float(
                floatOperation(left.AsFloat(), right.AsFloat())));
        }
        else
        {
            execution.Stack.Add(Level100ScriptValue.Integer(
                integerOperation(left.AsInteger(), right.AsInteger())));
        }
    }

    private static void PushNumericComparison(
        Execution execution,
        Func<float, float, bool> comparison)
    {
        Level100ScriptValue right = Pop(execution);
        Level100ScriptValue left = Pop(execution);
        execution.Stack.Add(Level100ScriptValue.Boolean(
            comparison(left.AsFloat(), right.AsFloat())));
    }

    private static bool ValuesEqual(Level100ScriptValue left, Level100ScriptValue right)
    {
        if (left.Type == Level100ScriptValueType.Float ||
            right.Type == Level100ScriptValueType.Float)
        {
            return left.AsFloat() == right.AsFloat();
        }

        if (left.Type is Level100ScriptValueType.Integer or Level100ScriptValueType.Boolean &&
            right.Type is Level100ScriptValueType.Integer or Level100ScriptValueType.Boolean)
        {
            return left.Scalar == right.Scalar;
        }

        return left.Type == right.Type &&
               left.Scalar == right.Scalar &&
               left.ComponentY == right.ComponentY &&
               left.ComponentZ == right.ComponentZ &&
               string.Equals(left.Text, right.Text, StringComparison.Ordinal);
    }

    private static void RequireArguments(
        int command,
        IReadOnlyCollection<Level100ScriptValue> arguments,
        int expected)
    {
        if (arguments.Count != expected)
        {
            throw new InvalidOperationException(
                $"Released native call {command} expected {expected} arguments, got {arguments.Count}.");
        }
    }

    private static Level100ActorId RequireContext(Execution execution) =>
        execution.CallContext?.AsActorId() ?? throw new InvalidOperationException(
            "Released LevelScript native method has no resolved actor context.");

    private static Level100ScriptExecutionSnapshot SnapshotExecution(Execution? execution) =>
        execution is null
            ? new Level100ScriptExecutionSnapshot(
                null,
                -1,
                0,
                0,
                false,
                null,
                Array.Empty<Level100ScriptValueSnapshot>(),
                Array.Empty<int>())
            : new Level100ScriptExecutionSnapshot(
                execution.EventName,
                execution.InstructionPointer,
                execution.Flags,
                execution.SavedStackSize,
                execution.Abort,
                execution.CallContext?.Snapshot,
                execution.Stack.Select(item => item.Snapshot).ToArray(),
                execution.CallFrames.ToArray());

    private sealed class Execution
    {
        internal Execution(string? eventName, int instructionPointer)
        {
            EventName = eventName;
            InstructionPointer = instructionPointer;
        }

        internal string? EventName { get; }
        internal int InstructionPointer { get; set; }
        internal int Flags { get; set; }
        internal int SavedStackSize { get; set; }
        internal bool Abort { get; set; }
        internal Level100ScriptValue? CallContext { get; set; }
        internal List<Level100ScriptValue> Stack { get; } = [];
        internal List<int> CallFrames { get; } = [];
        internal bool Stopped { get; set; }

        internal Execution Clone()
        {
            var result = new Execution(EventName, InstructionPointer)
            {
                Flags = Flags,
                SavedStackSize = SavedStackSize,
                Abort = Abort,
                CallContext = CallContext,
                Stopped = Stopped,
            };
            result.Stack.AddRange(Stack);
            result.CallFrames.AddRange(CallFrames);
            return result;
        }
    }

    private sealed record Continuation(
        long Sequence,
        int DueTick,
        Level100ScriptWaitKind WaitKind,
        int WaitArgument,
        Execution Execution);

    private readonly record struct QueuedEvent(long Sequence, string EventName);

    private readonly record struct ObjectiveState(
        int Objective,
        int TextId,
        Level100PrimaryObjectiveStatus Status);

    private readonly record struct WaitRequest(
        Level100ScriptWaitKind Kind,
        int Ticks,
        int Argument)
    {
        internal static WaitRequest None => new(Level100ScriptWaitKind.None, 0, 0);
    }

    private readonly record struct NativeResult(Level100ScriptValue Value, WaitRequest Wait)
    {
        internal static NativeResult Void => new(Level100ScriptValue.Integer(0), WaitRequest.None);

        internal static NativeResult Waiting(
            Level100ScriptWaitKind kind,
            int ticks,
            int argument) => new(
                Level100ScriptValue.Integer(0),
                new WaitRequest(kind, ticks, argument));
    }
}
