// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Core.Tests;

public sealed class RetailWorld110LevelActorsTests
{
    [Fact]
    public void Census_AddsToTheMeasuredForty()
    {
        Assert.Equal(40, RetailWorld110LevelActors.InitialActorCount);
        Assert.Equal(2, RetailWorld110LevelActors.ActorHeaderA);
        Assert.Equal(0, RetailWorld110LevelActors.ActorHeaderB);
        Assert.Equal(40, RetailWorld110LevelActors.SumOfTypedRows);
        Assert.Equal(54669, RetailWorld110LevelActors.SharedBaseWorldBytes);
        Assert.Equal(
            "04C5A3838548A2C50819F46DC1F1746F7C20EC4AA34678BD23C8BCD2186010F4",
            RetailWorld110LevelActors.SharedBaseWorldSha256);
    }

    [Fact]
    public void Admit_ExactWorld110ProjectionPreservesAuthoredDefinitionShape()
    {
        RetailWorldActorDefinitionProjection projection = AdmitExactProjection();
        RetailWorldActorDefinitionProjection repeat = AdmitExactProjection();

        Assert.Equal(110, projection.WorldNumber);
        Assert.Equal(
            new RetailWorldArchiveIdentity(
                "data/resources/110_res_PC.aya",
                "4e041c758b9d41ba18311b1fadeacb95fc31af51320861480b97033bc24e3c2b"),
            projection.ArchiveIdentity);
        Assert.Equal(49, projection.Definitions.Count);
        Assert.Equal(48, projection.ActorDefinitionCount);
        Assert.Equal(1, projection.SpawnerDefinitionCount);
        Assert.Equal(
            new RetailWorldAuthoredDefinitionIdentity(
                "wres:bswd:0000",
                8,
                "Control Tower",
                RetailWorldAuthoredDefinitionKind.Actor),
            projection.Definitions[0]);
        Assert.Contains(
            new RetailWorldAuthoredDefinitionIdentity(
                "wres:rlwd:0005",
                19,
                "Muspell Fighter",
                RetailWorldAuthoredDefinitionKind.Spawner),
            projection.Definitions);
        Assert.Contains(
            new RetailWorldAuthoredDefinitionIdentity(
                "wres:rlwd:0019",
                28,
                "AV-14B Sabre Pulse Tank",
                RetailWorldAuthoredDefinitionKind.Actor),
            projection.Definitions);
        Assert.Equal(projection.IdentitySha256, repeat.IdentitySha256);
    }

    [Fact]
    public void Admit_RejectsWorldWithoutAnAuthoredProjection()
    {
        ArgumentOutOfRangeException error = Assert.Throws<ArgumentOutOfRangeException>(() =>
            RetailWorldActorDefinitionAdmission.Admit(
                200,
                RetailWorld110LevelActors.ArchiveIdentity,
                RetailWorld110LevelActors.AuthoredDefinitions));

        Assert.Equal("worldNumber", error.ParamName);
    }

    [Fact]
    public void Admit_RejectsWrongArchiveIdentity()
    {
        RetailWorldArchiveIdentity wrongArchive =
            RetailWorld110LevelActors.ArchiveIdentity with
            {
                Sha256 = new string('0', 64),
            };

        ArgumentException error = Assert.Throws<ArgumentException>(() =>
            RetailWorldActorDefinitionAdmission.Admit(
                RetailWorld110LevelActors.WorldNumber,
                wrongArchive,
                RetailWorld110LevelActors.AuthoredDefinitions));

        Assert.Equal("archiveIdentity", error.ParamName);
        Assert.Contains("archive identity", error.Message, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void Admit_RejectsWrongObjectIdentity()
    {
        RetailWorldAuthoredDefinitionIdentity[] changed =
            RetailWorld110LevelActors.AuthoredDefinitions.ToArray();
        changed[0] = changed[0] with { ObjectIdentity = "wres:bswd:0034" };

        ArgumentException error = Assert.Throws<ArgumentException>(() =>
            RetailWorldActorDefinitionAdmission.Admit(
                RetailWorld110LevelActors.WorldNumber,
                RetailWorld110LevelActors.ArchiveIdentity,
                changed));

        Assert.Equal("definitions", error.ParamName);
        Assert.Contains("object identity", error.Message, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void Admit_RejectsWrongDefinitionIdentity()
    {
        RetailWorldAuthoredDefinitionIdentity[] changed =
            RetailWorld110LevelActors.AuthoredDefinitions.ToArray();
        changed[0] = changed[0] with { DefinitionName = "Forseti Pulse Tank Factory" };

        ArgumentException error = Assert.Throws<ArgumentException>(() =>
            RetailWorldActorDefinitionAdmission.Admit(
                RetailWorld110LevelActors.WorldNumber,
                RetailWorld110LevelActors.ArchiveIdentity,
                changed));

        Assert.Equal("definitions", error.ParamName);
        Assert.Contains("definition identity", error.Message, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void Admit_RejectsWrongDefinitionShape()
    {
        RetailWorldAuthoredDefinitionIdentity[] changed =
            RetailWorld110LevelActors.AuthoredDefinitions.ToArray();
        changed[0] = changed[0] with
        {
            Kind = RetailWorldAuthoredDefinitionKind.Spawner,
        };

        ArgumentException error = Assert.Throws<ArgumentException>(() =>
            RetailWorldActorDefinitionAdmission.Admit(
                RetailWorld110LevelActors.WorldNumber,
                RetailWorld110LevelActors.ArchiveIdentity,
                changed));

        Assert.Equal("definitions", error.ParamName);
        Assert.Contains("definition shape", error.Message, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void Admit_RejectsOmittedRequiredDefinition()
    {
        ArgumentException error = Assert.Throws<ArgumentException>(() =>
            RetailWorldActorDefinitionAdmission.Admit(
                RetailWorld110LevelActors.WorldNumber,
                RetailWorld110LevelActors.ArchiveIdentity,
                RetailWorld110LevelActors.AuthoredDefinitions.Skip(1)));

        Assert.Equal("definitions", error.ParamName);
        Assert.Contains("49", error.Message, StringComparison.Ordinal);
    }

    [Fact]
    public void RejectedAdmission_DoesNotMutateAdjacentWorld110SessionState()
    {
        Level100ActorDefinitionSet definitions =
            RetailWorld110AdmissionTests.CreateWorld110Definitions();
        var simulation = new Simulation(
            1,
            definitions,
            worldNumber: Level100MissionProgram.WorldNumber110);
        WorldSnapshot before = simulation.Snapshot;
        RetailWorldAuthoredDefinitionIdentity[] changed =
            RetailWorld110LevelActors.AuthoredDefinitions.ToArray();
        changed[0] = changed[0] with { DefinitionName = "Wrong definition" };

        Assert.Throws<ArgumentException>(() =>
            RetailWorldActorDefinitionAdmission.Admit(
                RetailWorld110LevelActors.WorldNumber,
                RetailWorld110LevelActors.ArchiveIdentity,
                changed));

        WorldSnapshot after = simulation.Snapshot;
        Assert.Equal(StateHasher.ComputeHex(before), StateHasher.ComputeHex(after));
        Assert.Equal(
            "f5c157ba2c6a9acbee78d895a25be82252951b93bdfdd8886a79ecd7bfe222aa",
            after.Level100Mission.ProgramSha256);
        Assert.Equal(
            Level100Terrain.World110SourceSha256,
            Level100Terrain.World110.PayloadSha256);
        Assert.Equal(
            RetailSecondaryObjectiveStatus.Failed,
            after.Level100Mission.SecondaryObjectives[1].Status);
        Assert.Equal(
            35,
            Assert.Single(after.Level100Mission.Continuations).Execution.InstructionPointer);
    }

    [Fact]
    public void Admission_DoesNotChangeTheWorld100FortyStepCanonicalHash()
    {
        _ = AdmitExactProjection();
        var root = new Simulation(
            1,
            Level100TestActorDefinitions.Create(),
            new Level100TutorialProgress(
                Introduction: true,
                PulseCannon: true,
                VulcanCannon: true,
                StatusBars: true));
        WorldSnapshot state = root.Snapshot;
        for (int tick = 0; tick < 40; tick++)
        {
            state = root.Step(new SimInput(0, 1));
        }

        Assert.Equal(
            "b8a1c8bc9150dfd02d83c7866f619b9601fcbd34615b1b59d014d49193a11216",
            StateHasher.ComputeHex(state));
    }

    [Fact]
    public void DefinitionSet_CarriesTheWorldNumber_AndRejectsUnknownWorlds()
    {
        Level100ActorDefinitionSet root = Level100TestActorDefinitions.Create();
        Assert.Equal(RetailWorldCatalog.RootWorldNumber, root.WorldNumber);

        Assert.Throws<ArgumentOutOfRangeException>(
            () => new Level100ActorDefinitionSet(
                root.Actors,
                root.Spawns,
                root.WaypointPaths,
                root.MotionDefinitions,
                worldNumber: 999));
    }

    private static RetailWorldActorDefinitionProjection AdmitExactProjection() =>
        RetailWorldActorDefinitionAdmission.Admit(
            RetailWorld110LevelActors.WorldNumber,
            RetailWorld110LevelActors.ArchiveIdentity,
            RetailWorld110LevelActors.AuthoredDefinitions);
}
