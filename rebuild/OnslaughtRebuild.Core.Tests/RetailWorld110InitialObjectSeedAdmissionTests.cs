// SPDX-License-Identifier: GPL-3.0-or-later

using System.Text;
using System.Text.Json;
using System.Text.Json.Nodes;
using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Core.Tests;

public sealed class RetailWorld110InitialObjectSeedAdmissionTests
{
    private const string ResourceName =
        "OnslaughtRebuild.Core.Assets.Level110.level110-initial-object-seeds.json";

    private static readonly string[] s_exactRows =
    [
        "wres:rlwd:0000|0|15719|62|a7c02a47e04e83bf83a83a014cb3ab9fee6d6a592739ab4f578c6543c3608cb2|27|41b00000,43fc0000,80000000|00000000,00000000,00000000|0|2|-1|LevelScript|||1|0|script",
        "wres:rlwd:0001|1|15781|59|850de203b32b967064f3a9bacca24bebd783af68760a8b4c056ea242a2b47dfc|15|43846000,43816800,80000000|bf04fd8b,00000000,00000000|0|0|-1||||1|0|start:0:1",
        "wres:rlwd:0002|2|15840|56|fffdc92e439f1aacff87c0595ee7b6315d1e41b706f87e84784729ae8e7c4c73|27|42240000,43fa0000,80000000|00000000,00000000,00000000|0|2|-1|Setup|||1|0|script",
        "wres:rlwd:0003|3|15896|51|81568a58f1321947dad8294b8641376711bed0a2f1df7bb7dadafbbae07dcba4|18|43b28000,42700000,c2200000|00000000,00000000,00000000|0|2|4||||1|0|waypoint",
        "wres:rlwd:0004|4|15947|51|fe3d861b0e6f51dadadb607db8674ee2f2e06db673edbb41048c8bd0bc27420c|18|43950000,43400000,c2200000|00000000,00000000,00000000|0|2|-1||||1|0|waypoint",
        "wres:rlwd:0005|5|15998|122|6e32ff6dd64c95a7f8639f307794af21338921f81a631dd0a9705327dbaf22f2|19|43fc0000,43820000,c2200000|3fc90fdb,00000000,00000000|0|1|-1||Fighter Second Wave|MuspellFighter2|0|0|spawner:3:40a00000:40a00000:00000000:1:Muspell Fighter:",
        "wres:rlwd:0006|6|16120|51|5d6e4f483d7e77a7df0160e02d1c0e03c04102009987deb6c49855322c3c16fc|18|43e20000,43830000,c2200000|00000000,00000000,00000000|0|2|7||||1|0|waypoint",
        "wres:rlwd:0007|7|16171|51|a98c474f399b682a44b6de131d9ceb10f2bb87047e90631867996f2a659c5c91|18|43c48000,43838000,c2200000|00000000,00000000,00000000|0|2|-1||||1|0|waypoint",
        "wres:rlwd:0008|8|16222|89|285c2e94279c737eab5849b345de5da141ae1131282c137508e2682522fbdc6b|8|43570000,43d30000,c1a00000|40490fdb,00000000,00000000|0|1|-1|Lander|||1|0|unit:Muspell Light Landing Craft:-1",
        "wres:rlwd:0009|9|16311|55|8316b95228c3aa83a32d100a73fa08a7807c59d3e9beadd556b38f5ea9d9f58c|36|436b0000,43f10000,00000000|00000000,00000000,00000000|0|2|-1||||1|0|volume:42480000",
        "wres:rlwd:0010|10|16366|51|67cf0c11c00934a2170b3ff1ce70899d486291b270322573b231e6179f587114|18|43580000,43ca0000,80000000|00000000,00000000,00000000|0|2|11||||1|0|waypoint",
        "wres:rlwd:0011|11|16417|51|18b6606f3980e8f91af41eeefa83e532d1f0ffbff6d490bb75adb601e8d0e283|18|4381c000,43ae4000,80000000|00000000,00000000,00000000|0|2|15||||1|0|waypoint",
        "wres:rlwd:0012|12|16468|90|fb20ac78a4c0bddbf2c61db1bf2aff4d0967b6bd2550acbee7256fb6d9e2df12|8|434d2000,43a39000,c1c80000|40782696,00000000,00000000|0|1|-1|Lander2|||1|0|unit:Muspell Light Landing Craft:-1",
        "wres:rlwd:0013|13|16558|90|ce411e2692aa0e2799881df060cd8883ceaf94672aafb5497669c93f5e369b6a|8|436d8000,43aa0000,c1f00000|00000000,00000000,00000000|0|1|-1|Lander3|||1|0|unit:Muspell Light Landing Empty:-1",
        "wres:rlwd:0014|14|16648|78|e9b31876f9d090743dbb1091d5f5fad3de54e4ef9901c2b2ad598d640e71147f|28|435a4000,439be000,80000000|40490fdb,00000000,00000000|0|1|-1||||1|0|squad:5:0:Light Gun Tank:-1",
        "wres:rlwd:0015|15|16726|51|3ba55f440677567ff5fb4796b78624a9437ded718374c0ff1c2fe06b76a3362b|18|43794000,43aaa000,80000000|00000000,00000000,00000000|0|2|-1||||1|0|waypoint",
        "wres:rlwd:0016|16|16777|78|95d2ba7fbb929681dbdb17983d13f80fb96bb832a8c28d64aadd7d89fedbed94|28|43744000,43a65000,80000000|40761cb1,00000000,00000000|0|1|-1||||1|0|squad:5:0:Light Gun Tank:-1",
        "wres:rlwd:0017|17|16855|87|648efa03cccef7fb74f1036e8182e8beb608cb1b9240638aebe7636e03000632|28|4381f800,4385d800,80000000|3f7cee73,00000000,00000000|0|0|-1||||1|0|squad:3:0:AV-14B Sabre Pulse Tank:-1",
        "wres:rlwd:0018|18|16942|78|7d175bc58dc38e6adbf5b05e1420bb2da10f6277dd8fcb330550472cb07d390e|28|43660000,43a2e000,80000000|00000000,00000000,00000000|0|1|-1||||1|0|squad:5:0:Light Gun Tank:-1",
        "wres:rlwd:0019|19|17020|92|aea74b9bf9b6719aa006291781ef48aa59b3be46b80e020ede4387a2dbd3bf18|28|43618000,43904000,80000000|00000000,00000000,00000000|0|0|-1|Scout|||1|0|squad:4:0:AV-14B Sabre Pulse Tank:-1",
        "wres:rlwd:0020|20|17112|89|1186a7c688a026be14c17549462f61e069e0c19b3276f44087e3ba15d6a85594|8|432a0000,43fc8000,c1c80000|40490fdb,00000000,00000000|0|1|-1|Lander|||1|0|unit:Muspell Light Landing Craft:-1",
        "wres:rlwd:0021|21|17201|51|3a0612146dc8ce230f1491586e5f9c9af8fe3295c3a91423e5bee38e2322c173|18|432a0000,43f80000,00000000|00000000,00000000,00000000|0|2|22||||1|0|waypoint",
        "wres:rlwd:0022|22|17252|51|7388c129146b37615605496357ccb71f8258f38a5e746ed25b13fee2b69198a8|18|43234000,438a8000,80000000|00000000,00000000,00000000|0|2|24||||1|0|waypoint",
        "wres:rlwd:0023|23|17303|51|254c5de2f8becbcf8cc1bed1dd88c42cfc43d39d5cee1ec0893cfdefc34ce1a9|18|431b8000,43800000,00000000|00000000,00000000,00000000|0|2|-1||||1|0|waypoint",
        "wres:rlwd:0024|24|17354|51|712e76396f15108568993026ea09742d339ecdea51324ea261031c3374785be2|18|432dc000,438be000,80000000|00000000,00000000,00000000|0|2|-1||||1|0|waypoint",
        "wres:rlwd:0025|25|17405|71|39f3ade63d3a15e62ef060c1d176376bc97326dc186cf18da512b59bbce20d00|8|435ac000,43ad4000,c1700000|40490fdb,00000000,00000000|0|1|-1||||1|0|unit:Muspell Fighter:-1",
        "wres:rlwd:0026|26|17476|51|88afea7be398ae842adf082a9d8fda9b043648f65ffe2904edd5fde5a8822d07|18|43840000,43b52000,80000000|00000000,00000000,00000000|0|2|29||||1|0|waypoint",
        "wres:rlwd:0027|27|17527|51|e979b5207742067aa696105d4172640b0905ba8dc82f7b9aa744bdd36b24b14a|18|43884000,43b6c000,80000000|00000000,00000000,00000000|0|2|30||||1|0|waypoint",
        "wres:rlwd:0028|28|17578|51|49ee71759d098a747d6167811678017b6202c0bcfa1d45ec99b97fd7c6dc0344|18|435b0000,43aac000,80000000|00000000,00000000,00000000|0|2|31||||1|0|waypoint",
        "wres:rlwd:0029|29|17629|51|a1c673b07424bb31e411d198ad9fc62f1eb5149afdfd65d63fda2d01daf5aa9b|18|43840000,438f8000,80000000|00000000,00000000,00000000|0|2|-1||||1|0|waypoint",
        "wres:rlwd:0030|30|17680|51|34be8997cd90c07d301da985d09417fed4c14b4d943186a903f841aac68327a0|18|4387c000,43930000,80000000|00000000,00000000,00000000|0|2|33||||1|0|waypoint",
        "wres:rlwd:0031|31|17731|51|65c9c357120c46d6f1291c4e66ce7b83a903d78102ed6649dac95f6e35522747|18|435d4000,43942000,80000000|00000000,00000000,00000000|0|2|32||||1|0|waypoint",
        "wres:rlwd:0032|32|17782|51|926fe33c6d5d8ca48276d094d5dab7effc1e56ebfe0692ca83eb5a8734cae74a|18|436fc000,438ca000,80000000|00000000,00000000,00000000|0|2|-1||||1|0|waypoint",
        "wres:rlwd:0033|33|17833|51|be8ea03d8cee3e573e119986a40e931a2b0a62eadd2ea9c0db82dc21b953cc46|18|438e4000,438d8000,00000000|00000000,00000000,00000000|0|2|-1||||1|0|waypoint",
        "wres:rlwd:0034|34|17884|77|bb546088a13ac94b4d28f4408da4512f7aeb339da4d18dba5b4a55a50c366255|8|43720000,43b68000,c1a00000|40490fdb,00000000,00000000|0|1|-1||||1|0|unit:Muspell Light Fighter:-1",
        "wres:rlwd:0035|35|17961|77|c7239e4309e841b1198340aa530fdc67a97fe0087ca44b3a21f7d121b5f97a58|8|43800000,43ba8000,c1a00000|40490fdb,00000000,00000000|0|1|-1||||1|0|unit:Muspell Light Fighter:-1",
        "wres:rlwd:0036|36|18038|77|b5bbaf825e345737535e9dac5050b6a550689592b3b50c04c40cd65c925bb98b|8|431f0000,43918000,c1700000|bfc90fdb,00000000,00000000|0|1|-1||||1|0|unit:Muspell Light Fighter:-1",
        "wres:rlwd:0037|37|18115|77|1c1d03609877d5dcbd847bb04115deea2563576241cb5e99cf3197a54f468d13|8|43260000,439c0000,c1700000|bfc90fdb,00000000,00000000|0|1|-1||||1|0|unit:Muspell Light Fighter:-1",
        "wres:rlwd:0038|38|18192|77|246332854077012a1838ff5a0b4fb8e1df324bb2c4cdf849acef4920b140690e|8|432e0000,43a50000,c1700000|bfc90fdb,00000000,00000000|0|1|-1||||1|0|unit:Muspell Light Fighter:-1",
        "wres:rlwd:0039|39|18269|58|5b5c8ff7b06f7eb69ba6694948fb40e158cc4b0295e2817e6b1f871a0ab21744|27|42840000,43f78000,80000000|00000000,00000000,00000000|0|2|-1|Weather|||1|0|script",
    ];

    [Fact]
    public void World110_AdmitsTheExactEnvelopeAndCompleteFortyRowOracle()
    {
        RetailWorldInitialObjectSeedProjection projection =
            RetailWorldInitialObjectSeedAdmission.World110;
        RetailWorldInitialObjectSeedProjection repeat =
            RetailWorldInitialObjectSeedAdmission.World110;

        Assert.Same(projection, repeat);
        Assert.Equal("onslaught.world110-initial-object-seeds.v1", projection.Schema);
        Assert.Equal(110, projection.WorldNumber);
        Assert.Equal(RetailWorld110LevelActors.ArchiveIdentity, projection.ArchiveIdentity);
        Assert.Equal(76_600, projection.RlwdByteLength);
        Assert.Equal(
            "fb56249deac8faf0033f4d4b67688ff72e12d922291c880d75b10599fc739837",
            projection.RlwdSha256);
        Assert.Equal(15_709, projection.RlwdInitialObjectHeaderOffset);
        Assert.Equal(2, projection.HeaderA);
        Assert.Equal(0, projection.HeaderB);
        Assert.Equal(40, projection.InitialObjectCount);
        Assert.Equal(18_327, projection.TreeGroupHeaderOffset);
        Assert.Equal(
            "51e51f5e1d3f7bce52ce99297711b1f299494271af3129828959e726aed04e5a",
            projection.MaterializedAssetSha256);
        Assert.Equal(s_exactRows, projection.Rows.Select(Describe).ToArray());
    }

    [Fact]
    public void TypedViewsPreserveSourceOrderIdentityAndSquadSpawnerSemantics()
    {
        RetailWorldInitialObjectSeedProjection projection =
            RetailWorldInitialObjectSeedAdmission.World110;

        Assert.Equal(10, projection.UnitSeeds.Count);
        Assert.Single(projection.StartSeeds);
        Assert.Equal(19, projection.WaypointSeeds.Count);
        Assert.Single(projection.SpawnerSeeds);
        Assert.Equal(3, projection.ScriptSeeds.Count);
        Assert.Equal(5, projection.SquadSeeds.Count);
        Assert.Single(projection.VolumeSeeds);
        foreach (IReadOnlyList<RetailWorldInitialObjectSeed> view in new[]
        {
            projection.UnitSeeds,
            projection.StartSeeds,
            projection.WaypointSeeds,
            projection.SpawnerSeeds,
            projection.ScriptSeeds,
            projection.SquadSeeds,
            projection.VolumeSeeds,
        })
        {
            Assert.Equal(view.OrderBy(row => row.Ordinal), view);
            Assert.All(view, row => Assert.Same(projection.Rows[row.Ordinal], row));
        }

        Assert.Equal([14, 16, 17, 18, 19], projection.SquadSeeds.Select(row => row.Ordinal));
        RetailWorldSquadSeedTail[] squads = projection.SquadSeeds
            .Select(row => Assert.IsType<RetailWorldSquadSeedTail>(row.Tail))
            .ToArray();
        Assert.Equal([5, 5, 3, 5, 4], squads.Select(tail => tail.Amount));
        Assert.All(squads, tail => Assert.Equal(0, tail.Mode));
        Assert.Equal(22, squads.Sum(tail => tail.Amount));
        Assert.DoesNotContain(
            projection.SquadSeeds,
            squad => projection.UnitSeeds.Contains(squad));

        RetailWorldInitialObjectSeed spawnerRow = Assert.Single(projection.SpawnerSeeds);
        RetailWorldSpawnerSeedTail spawner =
            Assert.IsType<RetailWorldSpawnerSeedTail>(spawnerRow.Tail);
        Assert.Equal(5, spawnerRow.Ordinal);
        Assert.Equal(0, spawnerRow.ActiveWord);
        Assert.Equal("MuspellFighter2", spawnerRow.SpawnScript);
        Assert.Equal(3, spawner.Amount);
        Assert.Equal(0x40a00000, spawner.DelayBits);
        Assert.Equal(0x40a00000, spawner.SquadDelayBits);
        Assert.Equal(0, spawner.InitialDelayBits);
        Assert.Equal(1, spawner.SquadSize);
        Assert.Equal("Muspell Fighter", spawner.SpawnUnit);
        Assert.Equal(string.Empty, spawner.SpawnerSpawnScript);

        RetailWorldVolumeSeedTail volume = Assert.IsType<RetailWorldVolumeSeedTail>(
            Assert.Single(projection.VolumeSeeds).Tail);
        Assert.Equal(0x42480000, volume.RadiusBits);
    }

    [Fact]
    public void StartSeedLosslesslyCrossChecksTheExistingStartAdmission()
    {
        RetailWorldInitialObjectSeed startSeed = Assert.Single(
            RetailWorldInitialObjectSeedAdmission.World110.StartSeeds);
        RetailWorldPlayerStartRecord converted = startSeed.ToPlayerStartRecord();
        RetailWorldPlayerStartRecord expected = Assert.Single(
            RetailWorld110LevelActors.AuthoredPlayerStarts);

        Assert.Equal(expected, converted);
        RetailWorldPlayerStartProjection admitted = RetailWorldPlayerStartAdmission.Admit(
            110,
            RetailWorld110LevelActors.ArchiveIdentity,
            [converted]);
        Assert.Equal(expected, Assert.Single(admitted.Starts));
        Assert.Equal(unchecked((int)0x80000000), converted.PositionZBits);
        Assert.Throws<InvalidOperationException>(() =>
            RetailWorldInitialObjectSeedAdmission.World110.Rows[0].ToPlayerStartRecord());
    }

    [Fact]
    public void DefinitionBearingRlwdSeedsJoinExactlyWithoutImportingBswdRows()
    {
        var actual = RetailWorldInitialObjectSeedAdmission.World110.Rows
            .Select(row => (Row: row, Definition: DefinitionName(row)))
            .Where(item => item.Definition is not null)
            .Select(item => (
                item.Row.ObjectIdentity,
                item.Row.ThingType,
                DefinitionName: item.Definition!))
            .ToArray();
        RetailWorldAuthoredDefinitionIdentity[] expectedDefinitions =
            RetailWorld110LevelActors.AuthoredDefinitions
                .Where(definition => definition.ObjectIdentity.StartsWith(
                    "wres:rlwd:",
                    StringComparison.Ordinal))
                .ToArray();
        var expected = expectedDefinitions.Select(definition => (
            definition.ObjectIdentity,
            definition.ThingType,
            definition.DefinitionName)).ToArray();

        Assert.Equal(16, actual.Length);
        Assert.Equal(expected, actual);
        Assert.Equal(
            33,
            RetailWorld110LevelActors.AuthoredDefinitions.Count(definition =>
                definition.ObjectIdentity.StartsWith("wres:bswd:", StringComparison.Ordinal)));
        Assert.DoesNotContain(
            RetailWorldInitialObjectSeedAdmission.World110.Rows,
            row => row.ObjectIdentity.StartsWith("wres:bswd:", StringComparison.Ordinal));
    }

    [Fact]
    public void SourceBufferAndEveryPublishedCollectionAreImmutableSnapshots()
    {
        byte[] source = EmbeddedBytes();
        RetailWorldInitialObjectSeedProjection projection =
            RetailWorldInitialObjectSeedAdmission.DecodeWorld110ForTests(source);
        string first = Describe(projection.Rows[0]);
        Array.Fill(source, (byte)0);

        Assert.Equal(first, Describe(projection.Rows[0]));
        Assert.Throws<NotSupportedException>(() =>
            ((IList<RetailWorldInitialObjectSeed>)projection.Rows).Add(projection.Rows[0]));
        Assert.Throws<NotSupportedException>(() =>
            ((IList<RetailWorldInitialObjectSeed>)projection.Rows)[0] = projection.Rows[1]);
        foreach (IReadOnlyList<RetailWorldInitialObjectSeed> view in new[]
        {
            projection.UnitSeeds,
            projection.StartSeeds,
            projection.WaypointSeeds,
            projection.SpawnerSeeds,
            projection.ScriptSeeds,
            projection.SquadSeeds,
            projection.VolumeSeeds,
        })
        {
            Assert.Throws<NotSupportedException>(() =>
                ((IList<RetailWorldInitialObjectSeed>)view).Add(view[0]));
        }

        RetailWorldInitialObjectSeedProjection repeat =
            RetailWorldInitialObjectSeedAdmission.DecodeWorld110ForTests(EmbeddedBytes());
        Assert.NotSame(projection, repeat);
        Assert.Equal(
            projection.Rows.Select(Describe),
            repeat.Rows.Select(Describe));
    }

    [Fact]
    public void DecoderRejectsEveryMalformedEnvelopeRowAndTailShape()
    {
        var mutations = new (string Name, Action<JsonObject> Mutate)[]
        {
            ("schema", root => root["schema"] = "onslaught.world110-initial-object-seeds.v2"),
            ("world", root => root["worldNumber"] = 100),
            ("archive path", root => root["archive"]!["relativePath"] = "data/resources/100_res_PC.aya"),
            ("archive hash", root => root["archive"]!["sha256"] = new string('0', 64)),
            ("RLWD length", root => root["rlwdByteLength"] = 76_599),
            ("RLWD hash", root => root["rlwdSha256"] = new string('0', 64)),
            ("header offset", root => root["rlwdInitialObjectHeaderOffset"] = 15_710),
            ("header A", root => root["headerA"] = 1),
            ("header B", root => root["headerB"] = 1),
            ("row count", root => root["initialObjectCount"] = 39),
            ("tree offset", root => root["treeGroupHeaderOffset"] = 18_326),
            ("tree A", root => root["treeGroupHeaderA"] = 1),
            ("tree B", root => root["treeGroupHeaderB"] = 1),
            ("census", root => root["census"]![0]!["count"] = 9),
            ("missing row", root => Rows(root).RemoveAt(39)),
            ("extra row", root => Rows(root).Add(Rows(root)[0]!.DeepClone())),
            ("null row", root => Rows(root)[0] = null),
            ("same-type reorder", SwapSameTypeRows),
            ("duplicate rewritten identity", DuplicateRowWithRewrittenIdentity),
            ("wrong object identity", root => Rows(root)[0]!["objectIdentity"] = "wres:rlwd:0001"),
            ("offset regression", root => Rows(root)[1]!["recordOffset"] = 15_780),
            ("invalid length", root => Rows(root)[0]!["serializedByteLength"] = 0),
            ("invalid row digest", root => Rows(root)[0]!["serializedSha256"] = "bad"),
            ("unsupported thing type", root => Rows(root)[0]!["thingType"] = 99),
            ("non-finite pose", root => Rows(root)[3]!["positionXBits"] = 0x7fc00000),
            ("non-boolean active", root => Rows(root)[0]!["activeWord"] = 2),
            ("non-boolean attach", root => Rows(root)[0]!["attachScriptsToUnitsWord"] = -1),
            ("wrong tail kind", root => Rows(root)[14]!["tail"] = new JsonObject { ["kind"] = "waypoint" }),
            ("missing tail member", root => Rows(root)[14]!["tail"]!.AsObject().Remove("amount")),
            ("changed unit trailer", root => Rows(root)[8]!["tail"]!["trailer"] = 0),
            ("invalid squad amount", root => Rows(root)[14]!["tail"]!["amount"] = 0),
            ("invalid squad mode", root => Rows(root)[14]!["tail"]!["mode"] = -1),
            ("non-finite delay", root => Rows(root)[5]!["tail"]!["delayBits"] = 0x7f800000),
            ("non-finite radius", root => Rows(root)[9]!["tail"]!["radiusBits"] = 0x7f800000),
            ("unknown document member", root => root["unexpected"] = 1),
            ("unknown row member", root => Rows(root)[0]!["unexpected"] = 1),
            ("unknown tail member", root => Rows(root)[0]!["tail"]!["unexpected"] = 1),
        };

        foreach ((string name, Action<JsonObject> mutate) in mutations)
        {
            JsonObject candidate = ExactJson();
            mutate(candidate);
            InvalidDataException error = Assert.Throws<InvalidDataException>(() =>
                DecodeCandidate(candidate));
            Assert.NotEmpty(error.Message);
        }
    }

    [Fact]
    public void DecoderVerifiesHashBeforeJsonAndNormalizesSyntaxFailures()
    {
        byte[] exact = EmbeddedBytes();
        byte[] changed = exact.Concat([(byte)' ']).ToArray();

        Assert.Throws<InvalidDataException>(() =>
            RetailWorldInitialObjectSeedAdmission.DecodeWorld110ForTests(
                changed,
                RetailWorldInitialObjectSeedAdmission.World110MaterializedAssetSha256));
        Assert.Throws<InvalidDataException>(() =>
            RetailWorldInitialObjectSeedAdmission.DecodeWorld110ForTests(
                exact,
                new string('0', 64)));
        Assert.Throws<InvalidDataException>(() =>
            RetailWorldInitialObjectSeedAdmission.DecodeWorld110ForTests(
                Encoding.UTF8.GetBytes("{")));
        Assert.Throws<ArgumentNullException>(() =>
            RetailWorldInitialObjectSeedAdmission.DecodeWorld110ForTests(null!));
    }

    [Fact]
    public void StandaloneAdmissionDoesNotChangeTheWorld100CanonicalHash()
    {
        _ = RetailWorldInitialObjectSeedAdmission.World110;
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

    private static string Describe(RetailWorldInitialObjectSeed row) =>
        string.Join(
            '|',
            row.ObjectIdentity,
            row.Ordinal,
            row.RecordOffset,
            row.SerializedByteLength,
            row.SerializedSha256,
            row.ThingType,
            $"{Hex(row.PositionXBits)},{Hex(row.PositionYBits)},{Hex(row.PositionZBits)}",
            $"{Hex(row.OrientationXBits)},{Hex(row.OrientationYBits)},{Hex(row.OrientationZBits)}",
            row.MeshNumber,
            row.Allegiance,
            row.Target,
            row.Script,
            row.Name,
            row.SpawnScript,
            row.ActiveWord,
            row.AttachScriptsToUnitsWord,
            DescribeTail(row.Tail));

    private static string DescribeTail(RetailWorldInitialObjectSeedTail tail) =>
        tail switch
        {
            RetailWorldUnitSeedTail unit =>
                $"unit:{unit.DefinitionName}:{unit.Trailer}",
            RetailWorldStartSeedTail start =>
                $"start:{start.PlaneModeWord}:{start.PlayerNumber}",
            RetailWorldWaypointSeedTail => "waypoint",
            RetailWorldSpawnerSeedTail spawner =>
                $"spawner:{spawner.Amount}:{Hex(spawner.DelayBits)}:" +
                $"{Hex(spawner.SquadDelayBits)}:{Hex(spawner.InitialDelayBits)}:" +
                $"{spawner.SquadSize}:{spawner.SpawnUnit}:{spawner.SpawnerSpawnScript}",
            RetailWorldScriptSeedTail => "script",
            RetailWorldSquadSeedTail squad =>
                $"squad:{squad.Amount}:{squad.Mode}:{squad.DefinitionName}:{squad.Trailer}",
            RetailWorldVolumeSeedTail volume => $"volume:{Hex(volume.RadiusBits)}",
            _ => throw new ArgumentOutOfRangeException(nameof(tail)),
        };

    private static string? DefinitionName(RetailWorldInitialObjectSeed row) =>
        row.Tail switch
        {
            RetailWorldUnitSeedTail unit => unit.DefinitionName,
            RetailWorldSpawnerSeedTail spawner => spawner.SpawnUnit,
            RetailWorldSquadSeedTail squad => squad.DefinitionName,
            _ => null,
        };

    private static string Hex(int bits) => unchecked((uint)bits).ToString("x8");

    private static JsonObject ExactJson() =>
        JsonNode.Parse(EmbeddedBytes())!.AsObject();

    private static JsonArray Rows(JsonObject root) => root["rows"]!.AsArray();

    private static void DecodeCandidate(JsonObject candidate)
    {
        byte[] bytes = Encoding.UTF8.GetBytes(candidate.ToJsonString(
            new JsonSerializerOptions { WriteIndented = false }));
        _ = RetailWorldInitialObjectSeedAdmission.DecodeWorld110ForTests(bytes);
    }

    private static void SwapSameTypeRows(JsonObject root)
    {
        JsonArray rows = Rows(root);
        JsonNode first = rows[3]!.DeepClone();
        rows[3] = rows[4]!.DeepClone();
        rows[4] = first;
    }

    private static void DuplicateRowWithRewrittenIdentity(JsonObject root)
    {
        JsonArray rows = Rows(root);
        JsonObject replacement = rows[4]!.DeepClone().AsObject();
        replacement["ordinal"] = 3;
        replacement["objectIdentity"] = "wres:rlwd:0003";
        rows[3] = replacement;
    }

    private static byte[] EmbeddedBytes()
    {
        using Stream stream = typeof(RetailWorldInitialObjectSeedAdmission).Assembly
            .GetManifestResourceStream(ResourceName) ??
            throw new InvalidOperationException("The test seed resource is missing.");
        var bytes = new byte[checked((int)stream.Length)];
        stream.ReadExactly(bytes);
        return bytes;
    }
}
