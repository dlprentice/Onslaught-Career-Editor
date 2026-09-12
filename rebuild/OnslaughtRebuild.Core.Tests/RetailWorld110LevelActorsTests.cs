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
    public void Type15Start_RemainsSeparateFromDefinitionBearingActors()
    {
        RetailWorldPlayerStartRecord start =
            Assert.Single(RetailWorld110LevelActors.AuthoredPlayerStarts);

        Assert.Equal("wres:rlwd:0001", start.ObjectIdentity);
        Assert.Equal(15, start.ThingType);
        Assert.Equal(1, start.PlayerNumber);
        Assert.DoesNotContain(
            RetailWorld110LevelActors.AuthoredDefinitions,
            definition => definition.ThingType == 15);
        Assert.DoesNotContain(
            RetailWorld110LevelActors.AuthoredDefinitions,
            definition => StringComparer.Ordinal.Equals(
                definition.ObjectIdentity,
                start.ObjectIdentity));
        Assert.DoesNotContain(
            RetailWorld110LevelActors.AuthoredDefinitions,
            definition => StringComparer.Ordinal.Equals(
                definition.DefinitionName,
                "Player 1"));
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
    public void RejectedAdmission_DoesNotMutateActualWorld110ConstructionState()
    {
        var world = RetailWorld110InitialConstruction.Create();
        Level100ActorRegistrySnapshot before = world.Actors.Snapshot;
        RetailWorldAuthoredDefinitionIdentity[] changed =
            RetailWorld110LevelActors.AuthoredDefinitions.ToArray();
        changed[0] = changed[0] with { DefinitionName = "Wrong definition" };

        Assert.Throws<ArgumentException>(() =>
            RetailWorldActorDefinitionAdmission.Admit(
                RetailWorld110LevelActors.WorldNumber,
                RetailWorld110LevelActors.ArchiveIdentity,
                changed));

        Level100ActorRegistrySnapshot after = world.Actors.Snapshot;
        Assert.Equal(before.Actors, after.Actors);
        Assert.Equal(before.BaseStates, after.BaseStates);
        Assert.Equal(before.DefinitionSetIdentitySha256, after.DefinitionSetIdentitySha256);
        Assert.Equal(43, after.Actors.Count);
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

        // Creation-owned raw Plane motion/guide/events select schema 47.
        Assert.Equal(
            "f121a4698b3eb150282ee8dd66c297922f9d54d0a56bb18dece072c04b4f55b8",
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
