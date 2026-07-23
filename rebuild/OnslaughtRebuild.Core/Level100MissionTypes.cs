// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Core;

public enum Level100MissionOutcome
{
    Running = 0,
    Won = 1,
    Lost = 2,
}

public enum Level100MissionTerminalState
{
    None = 0,
    SuccessCountdown = 1,
    FrontEndHandoffReady = 2,
    FailureCountdown = 3,
    FailureMenuReady = 4,
    FailureCountdownElapsed = 5,
}

public enum Level100MissionFailureReason
{
    None = 0,
    TutorialBroken = 1,
    PlayerDeath = 2,
    WaterLoss = 3,
}

public enum Level100MissionJetModeState
{
    NotInJetMode = 0,
    InJetMode = 1,
}

public enum Level100MissionTrigger
{
    TargetZone1 = 1,
    FiringRange = 2,
    TargetZone2 = 3,
    TargetZone3 = 4,
    TargetZone4 = 5,
}

public enum Level100MissionTargetGroup
{
    None = 0,
    StaticTargets = 1,
    TargetTrucks = 2,
    MovingTargets = 3,
    AirborneTargets1 = 4,
    AirborneTargets2 = 5,
    AirTrainer = 6,
}

public enum Level100MissionWeapon
{
    PulseCannonPod = 1,
    MechTwinVulcanCannon = 2,
    MechVulcanCannon = 3,
    MissilePod = 4,
}

public enum Level100MissionWeaponAvailability
{
    Unchanged = 0,
    Disabled = 1,
    Enabled = 2,
}

public enum Level100ScriptValueType
{
    Unset = 0,
    Integer = 1,
    Float = 2,
    String = 3,
    Boolean = 4,
    Thing = 5,
    Position = 6,
}

public enum Level100ScriptWaitKind
{
    None = 0,
    Pause = 1,
    CharacterMessage = 2,
}

public enum Level100PrimaryObjectiveStatus
{
    Uninitialized = 0,
    Failed = 1,
    Complete = 2,
}

public enum Level100ActorCommand
{
    Activate = 1,
    Deactivate = 2,
    SetObjective = 3,
    UnsetObjective = 4,
}

public enum Level100MissionInput
{
    BrokeTutorial = 1,
    HitFriendlyBuilding = 2,
    FriendlyBuildingDestroyed = 3,
    DestroyedFriendlyBuilding = 4,
    FlashThings = 5,
    HelpPlayer = 6,
    AbortAirborneDrones = 7,
    EvadeFailed = 8,
}

public readonly record struct Level100TutorialProgress(
    bool Introduction,
    bool PulseCannon,
    bool VulcanCannon,
    bool StatusBars);

public readonly record struct Level100ScriptValueSnapshot(
    Level100ScriptValueType Type,
    int Scalar,
    int ComponentY,
    int ComponentZ,
    string? Text);

public sealed record Level100ScriptLocalSnapshot(
    int Ordinal,
    string Name,
    Level100ScriptValueSnapshot Value);

public sealed record Level100QueuedEventSnapshot(
    long Sequence,
    string EventName);

public sealed record Level100ScriptExecutionSnapshot(
    string? EventName,
    int InstructionPointer,
    int Flags,
    int SavedStackSize,
    bool Abort,
    Level100ScriptValueSnapshot? CallContext,
    IReadOnlyList<Level100ScriptValueSnapshot> Stack,
    IReadOnlyList<int> CallFrames);

public sealed record Level100ScriptContinuationSnapshot(
    long Sequence,
    int DueTick,
    Level100ScriptWaitKind WaitKind,
    int WaitArgument,
    Level100ScriptExecutionSnapshot Execution);

public readonly record struct Level100PrimaryObjectiveSnapshot(
    int Objective,
    int TextId,
    Level100PrimaryObjectiveStatus Status);

public sealed record Level100MissionSnapshot(
    int Tick,
    string ProgramSha256,
    bool InitializerRan,
    bool IsRunning,
    long NextSequence,
    Level100ScriptExecutionSnapshot ActiveExecution,
    IReadOnlyList<Level100ScriptLocalSnapshot> Locals,
    IReadOnlyList<Level100QueuedEventSnapshot> EventQueue,
    IReadOnlyList<Level100ScriptContinuationSnapshot> Continuations,
    Level100MissionOutcome Outcome,
    Level100MissionTerminalState TerminalState,
    Level100MissionFailureReason FailureReason,
    int FailureTextId,
    int TerminalTicksRemaining,
    int InitialPlayerHealth,
    int LatestPlayerHealth,
    int ObservedPlayerHealth,
    bool PlayerActive,
    bool FlightModeEnabled,
    Level100MissionWeaponAvailability PulseCannonAvailability,
    Level100MissionWeaponAvailability TwinVulcanAvailability,
    Level100MissionWeaponAvailability MechVulcanAvailability,
    Level100MissionWeaponAvailability MissilePodAvailability,
    string? NavigationObjective,
    bool Evaded,
    bool Aborted,
    int FriendlyBuildingHits,
    int ScoreDelta,
    Level100TutorialProgress TutorialProgress,
    IReadOnlyList<Level100PrimaryObjectiveSnapshot> PrimaryObjectives,
    IReadOnlyList<Level100MissionEvent> PendingEvents);

public abstract record Level100MissionEvent(int Tick);

public sealed record Level100MessageRequested(
    int Tick,
    int SpeakerId,
    int MessageId,
    bool ScriptWaitsForDuration,
    int ExpectedPlaybackTicks)
    : Level100MissionEvent(Tick);

public sealed record Level100HudEmphasisChanged(int Tick, int PartId, bool Emphasized)
    : Level100MissionEvent(Tick);

public sealed record Level100PlayerActivationChanged(int Tick, bool Active)
    : Level100MissionEvent(Tick);

public sealed record Level100FlightModeAvailabilityChanged(int Tick, bool Enabled)
    : Level100MissionEvent(Tick);

public sealed record Level100WeaponAvailabilityChanged(
    int Tick,
    Level100MissionWeapon Weapon,
    bool Enabled)
    : Level100MissionEvent(Tick);

public sealed record Level100NavigationObjectiveChanged(int Tick, string? ThingName)
    : Level100MissionEvent(Tick);

public sealed record Level100ActorCommandRequested(
    int Tick,
    Level100ActorId ActorId,
    Level100ActorCommand Command)
    : Level100MissionEvent(Tick);

public sealed record Level100SpawnThingRequested(
    int Tick,
    Level100ActorId OwnerActorId,
    string DefinitionName,
    string SpawnerName,
    int Count,
    string ScriptName)
    : Level100MissionEvent(Tick);

public sealed record Level100MissionEventPosted(int Tick, string EventName)
    : Level100MissionEvent(Tick);

public sealed record Level100HelpRequested(int Tick, int HelpMessageId)
    : Level100MissionEvent(Tick);

public sealed record Level100ScoreChanged(int Tick, int Delta, int TotalDelta)
    : Level100MissionEvent(Tick);

public sealed record Level100TutorialSlotSaved(int Tick, int Slot)
    : Level100MissionEvent(Tick);

public sealed record Level100PrimaryObjectiveChanged(
    int Tick,
    int Objective,
    int TextId,
    Level100PrimaryObjectiveStatus Status)
    : Level100MissionEvent(Tick);

public sealed record Level100MissionOutcomeDeclared(
    int Tick,
    Level100MissionOutcome Outcome,
    Level100MissionFailureReason FailureReason,
    int FailureTextId)
    : Level100MissionEvent(Tick);

public sealed record Level100TerminalStateChanged(
    int Tick,
    Level100MissionTerminalState State)
    : Level100MissionEvent(Tick);
