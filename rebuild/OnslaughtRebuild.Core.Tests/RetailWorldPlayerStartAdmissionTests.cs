// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Core.Tests;

public sealed class RetailWorldPlayerStartAdmissionTests
{
    [Fact]
    public void Admit_ExactWorld110StartPreservesRawBitsAndDeterministicIdentity()
    {
        RetailWorldPlayerStartProjection projection = AdmitExactProjection();
        RetailWorldPlayerStartProjection repeat = AdmitExactProjection();
        RetailWorldPlayerStartRecord start = Assert.Single(projection.Starts);

        Assert.Equal(110, projection.WorldNumber);
        Assert.Equal(RetailWorld110LevelActors.ArchiveIdentity, projection.ArchiveIdentity);
        Assert.Equal("wres:rlwd:0001", start.ObjectIdentity);
        Assert.Equal(15, start.ThingType);
        Assert.Equal(59, start.SerializedByteLength);
        Assert.Equal(
            "850de203b32b967064f3a9bacca24bebd783af68760a8b4c056ea242a2b47dfc",
            start.SerializedSha256);
        Assert.Equal(0x43846000, start.PositionXBits);
        Assert.Equal(0x43816800, start.PositionYBits);
        Assert.Equal(unchecked((int)0x80000000), start.PositionZBits);
        Assert.Equal(unchecked((int)0xbf04fd8b), start.OrientationXBits);
        Assert.Equal(0, start.OrientationYBits);
        Assert.Equal(0, start.OrientationZBits);
        Assert.Equal(0, start.PlaneMode);
        Assert.Equal(1, start.PlayerNumber);
        Assert.Equal(264.75f, BitConverter.Int32BitsToSingle(start.PositionXBits));
        Assert.Equal(258.8125f, BitConverter.Int32BitsToSingle(start.PositionYBits));
        Assert.Equal(
            "848bf12558581573e0056f1650d25aef09c7a7aff8520f80ece1e7228b8f3cc9",
            projection.IdentitySha256);
        Assert.Equal(projection.IdentitySha256, repeat.IdentitySha256);
    }

    [Fact]
    public void Admit_NormalizesAcceptedDigestCaseToThePinnedProjection()
    {
        RetailWorldArchiveIdentity archive =
            RetailWorld110LevelActors.ArchiveIdentity with
            {
                Sha256 = RetailWorld110LevelActors.SourceArchiveSha256.ToUpperInvariant(),
            };
        RetailWorldPlayerStartRecord start = ExactStart() with
        {
            SerializedSha256 =
                RetailWorld110LevelActors.PlayerStartSerializedSha256.ToUpperInvariant(),
        };

        RetailWorldPlayerStartProjection projection =
            RetailWorldPlayerStartAdmission.Admit(110, archive, [start]);

        Assert.Equal(
            RetailWorld110LevelActors.SourceArchiveSha256,
            projection.ArchiveIdentity.Sha256);
        Assert.Equal(
            RetailWorld110LevelActors.PlayerStartSerializedSha256,
            Assert.Single(projection.Starts).SerializedSha256);
        Assert.Equal(
            "848bf12558581573e0056f1650d25aef09c7a7aff8520f80ece1e7228b8f3cc9",
            projection.IdentitySha256);
    }

    [Fact]
    public void Admit_RejectsWorldWithoutAPlayerStartProjection()
    {
        ArgumentOutOfRangeException error = Assert.Throws<ArgumentOutOfRangeException>(() =>
            RetailWorldPlayerStartAdmission.Admit(
                200,
                RetailWorld110LevelActors.ArchiveIdentity,
                RetailWorld110LevelActors.AuthoredPlayerStarts));

        Assert.Equal("worldNumber", error.ParamName);
    }

    [Theory]
    [InlineData("path")]
    [InlineData("hash")]
    public void Admit_RejectsChangedArchiveIdentity(string field)
    {
        RetailWorldArchiveIdentity archive = field switch
        {
            "path" => RetailWorld110LevelActors.ArchiveIdentity with
            {
                RelativePath = "data/resources/100_res_PC.aya",
            },
            "hash" => RetailWorld110LevelActors.ArchiveIdentity with
            {
                Sha256 = new string('0', 64),
            },
            _ => throw new ArgumentOutOfRangeException(nameof(field)),
        };

        ArgumentException error = Assert.Throws<ArgumentException>(() =>
            RetailWorldPlayerStartAdmission.Admit(
                110,
                archive,
                RetailWorld110LevelActors.AuthoredPlayerStarts));

        Assert.Equal("archiveIdentity", error.ParamName);
    }

    [Theory]
    [InlineData("objectIdentity")]
    [InlineData("thingType")]
    [InlineData("serializedByteLength")]
    [InlineData("serializedSha256")]
    [InlineData("positionXBits")]
    [InlineData("positionYBits")]
    [InlineData("positionZBits")]
    [InlineData("orientationXBits")]
    [InlineData("orientationYBits")]
    [InlineData("orientationZBits")]
    [InlineData("planeMode")]
    [InlineData("playerNumber")]
    public void Admit_RejectsEveryChangedStartField(string field)
    {
        RetailWorldPlayerStartRecord start = ExactStart();
        RetailWorldPlayerStartRecord changed = field switch
        {
            "objectIdentity" => start with { ObjectIdentity = "wres:rlwd:0002" },
            "thingType" => start with { ThingType = 8 },
            "serializedByteLength" => start with { SerializedByteLength = 60 },
            "serializedSha256" => start with { SerializedSha256 = new string('0', 64) },
            "positionXBits" => start with { PositionXBits = start.PositionXBits ^ 1 },
            "positionYBits" => start with { PositionYBits = start.PositionYBits ^ 1 },
            "positionZBits" => start with { PositionZBits = 0 },
            "orientationXBits" => start with
            {
                OrientationXBits = start.OrientationXBits ^ 1,
            },
            "orientationYBits" => start with { OrientationYBits = 1 },
            "orientationZBits" => start with { OrientationZBits = 1 },
            "planeMode" => start with { PlaneMode = 1 },
            "playerNumber" => start with { PlayerNumber = 2 },
            _ => throw new ArgumentOutOfRangeException(nameof(field)),
        };

        ArgumentException error = Assert.Throws<ArgumentException>(() =>
            RetailWorldPlayerStartAdmission.Admit(
                110,
                RetailWorld110LevelActors.ArchiveIdentity,
                [changed]));

        Assert.Equal("starts", error.ParamName);
        Assert.Contains("changed", error.Message, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public void Admit_RejectsMissingExtraAndNullStartRecords()
    {
        ArgumentException missing = Assert.Throws<ArgumentException>(() =>
            RetailWorldPlayerStartAdmission.Admit(
                110,
                RetailWorld110LevelActors.ArchiveIdentity,
                []));
        ArgumentException extra = Assert.Throws<ArgumentException>(() =>
            RetailWorldPlayerStartAdmission.Admit(
                110,
                RetailWorld110LevelActors.ArchiveIdentity,
                [ExactStart(), ExactStart()]));
        ArgumentException nullRecord = Assert.Throws<ArgumentException>(() =>
            RetailWorldPlayerStartAdmission.Admit(
                110,
                RetailWorld110LevelActors.ArchiveIdentity,
                [null!]));

        Assert.Equal("starts", missing.ParamName);
        Assert.Equal("starts", extra.ParamName);
        Assert.Equal("starts", nullRecord.ParamName);
    }

    [Fact]
    public void Admit_RejectsNullArchiveAndCollection()
    {
        Assert.Throws<ArgumentNullException>(() =>
            RetailWorldPlayerStartAdmission.Admit(
                110,
                null!,
                RetailWorld110LevelActors.AuthoredPlayerStarts));
        Assert.Throws<ArgumentNullException>(() =>
            RetailWorldPlayerStartAdmission.Admit(
                110,
                RetailWorld110LevelActors.ArchiveIdentity,
                null!));
    }

    [Fact]
    public void Admit_NormalizesToAnImmutableCopyOfThePinnedStartList()
    {
        RetailWorldPlayerStartRecord[] supplied = [ExactStart()];
        RetailWorldPlayerStartProjection projection =
            RetailWorldPlayerStartAdmission.Admit(
                110,
                RetailWorld110LevelActors.ArchiveIdentity,
                supplied);

        supplied[0] = supplied[0] with { PlayerNumber = 2 };

        RetailWorldPlayerStartRecord admitted = Assert.Single(projection.Starts);
        Assert.Equal(1, admitted.PlayerNumber);
        Assert.Throws<NotSupportedException>(() =>
            ((IList<RetailWorldPlayerStartRecord>)projection.Starts).Add(ExactStart()));
    }

    [Fact]
    public void ResolveForPlayerOne_ReturnsTheExactAuthoredStart()
    {
        RetailWorldPlayerStartProjection projection = AdmitExactProjection();

        RetailWorldPlayerStartResolution resolution = projection.ResolveForPlayer(1);

        Assert.True(resolution.IsAuthored);
        Assert.False(resolution.UsesRetailDefault);
        Assert.Same(Assert.Single(projection.Starts), resolution.AuthoredStart);
        Assert.Equal(1, resolution.PlayerNumber);
        Assert.Equal(15, resolution.ThingType);
        Assert.Equal(0x43846000, resolution.PositionXBits);
        Assert.Equal(0x43816800, resolution.PositionYBits);
        Assert.Equal(unchecked((int)0x80000000), resolution.PositionZBits);
        Assert.Equal(0, resolution.PlaneMode);
    }

    [Fact]
    public void ResolveForUnmatchedPlayer_ReturnsOnlyTheRetailDefaultPlan()
    {
        RetailWorldPlayerStartProjection projection = AdmitExactProjection();

        RetailWorldPlayerStartResolution resolution = projection.ResolveForPlayer(2);

        Assert.False(resolution.IsAuthored);
        Assert.True(resolution.UsesRetailDefault);
        Assert.Null(resolution.AuthoredStart);
        Assert.Equal(2, resolution.PlayerNumber);
        Assert.Equal(15, resolution.ThingType);
        Assert.Equal(0x43800000, resolution.PositionXBits);
        Assert.Equal(0x43800000, resolution.PositionYBits);
        Assert.Equal(0, resolution.PositionZBits);
        Assert.Equal(0, resolution.PlaneMode);
    }

    [Theory]
    [InlineData(0)]
    [InlineData(-1)]
    [InlineData(3)]
    public void ResolveForPlayer_RejectsUnsupportedPlayerNumbers(int playerNumber)
    {
        ArgumentOutOfRangeException error = Assert.Throws<ArgumentOutOfRangeException>(() =>
            AdmitExactProjection().ResolveForPlayer(playerNumber));

        Assert.Equal("playerNumber", error.ParamName);
    }

    [Fact]
    public void RejectedAdmission_DoesNotMutateAdjacentWorld110SessionState()
    {
        // Admission is deliberately detached today. Keep this forward guard so
        // a later constructor integration cannot turn rejection into a partial
        // session mutation.
        Level100ActorDefinitionSet definitions =
            RetailWorld110AdmissionTests.CreateWorld110Definitions();
        var simulation = new Simulation(
            1,
            definitions,
            worldNumber: Level100MissionProgram.WorldNumber110);
        WorldSnapshot before = simulation.Snapshot;
        RetailWorldPlayerStartRecord changed = ExactStart() with
        {
            PositionZBits = 0,
        };

        Assert.Throws<ArgumentException>(() =>
            RetailWorldPlayerStartAdmission.Admit(
                110,
                RetailWorld110LevelActors.ArchiveIdentity,
                [changed]));

        WorldSnapshot after = simulation.Snapshot;
        Assert.Equal(StateHasher.ComputeHex(before), StateHasher.ComputeHex(after));
        Assert.Equal(
            "f5c157ba2c6a9acbee78d895a25be82252951b93bdfdd8886a79ecd7bfe222aa",
            after.Level100Mission.ProgramSha256);
        Assert.Equal(
            35,
            Assert.Single(after.Level100Mission.Continuations).Execution.InstructionPointer);
    }

    private static RetailWorldPlayerStartRecord ExactStart() =>
        Assert.Single(RetailWorld110LevelActors.AuthoredPlayerStarts);

    private static RetailWorldPlayerStartProjection AdmitExactProjection() =>
        RetailWorldPlayerStartAdmission.Admit(
            RetailWorld110LevelActors.WorldNumber,
            RetailWorld110LevelActors.ArchiveIdentity,
            RetailWorld110LevelActors.AuthoredPlayerStarts);
}
