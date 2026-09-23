// SPDX-License-Identifier: GPL-3.0-or-later

using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// Pins the recovered laws of the shipped <c>data/ParticleSets/*.par</c> format
/// and the two effects the Level 100 path needs from it.
///
/// <para>These are not round-trip-a-property tests. The first one is the whole
/// reason the decoder can be trusted: it re-emits the 685,194-byte shipped
/// <c>MainSet.par</c> and asserts the bytes are identical. A parser that merely
/// accepted the input would pass nothing here. The rest each assert a law
/// measured over the corpus, computed from the file at test time rather than
/// copied into a constant, so a wrong reading of the format fails the test
/// rather than agreeing with it.</para>
/// </summary>
public sealed class ParticleSetTests
{
    private const string ParticleSetDirectory =
        "rebuild/OnslaughtRebuild.Godot/Assets/Level100/ParticleSets";

    private const string MainSetRelativePath = $"{ParticleSetDirectory}/MainSet.par";

    /// <summary>
    /// The exact shipped file, from <c>rebuild/PROVENANCE.md</c> and from
    /// <c>materialize_retail_assets.py</c>, which retains it verbatim.
    /// </summary>
    private const string MainSetSha256 =
        "A51FE4419B55E1AF132E31C6B3CD8133C937745D8F4AB691EB5A0D81017DED06";

    /// <summary>
    /// The whole shipped corpus: file name, byte length, sha256 and the count
    /// its own header declares. All three are retained verbatim by
    /// <c>materialize_retail_assets.py</c>.
    /// </summary>
    private static readonly (string Name, int Length, string Sha256, int Descriptors)[]
        ShippedCorpus =
        [
            ("MainSet.par", 685_194, MainSetSha256, 1_405),
            ("Frontend.par", 28_702,
                "01A4C73D7CFC666B4A367736FABD1D91BF3459ED1C538B6CA77F70C069CF8BC6", 65),
            ("ModelViewer.par", 3_465,
                "32D85D1F0400F46A45078D49C695967CDE60ED572053059FD6246227162115A9", 9),
        ];

    [Fact]
    public void ShippedMainSetIsTheExactRetailFile()
    {
        byte[] bytes = ReadMainSet();
        Assert.Equal(685_194, bytes.Length);
        Assert.Equal(
            MainSetSha256,
            Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(bytes)));
    }

    /// <summary>
    /// The decoder's falsifiability check. Parse then re-emit; the bytes must
    /// be identical, including the CRLF line endings, the 65-star record
    /// separators, the trailing CRLF, and every authored value verbatim.
    /// </summary>
    [Fact]
    public void ShippedMainSetRoundTripsByteIdentically()
    {
        byte[] bytes = ReadMainSet();
        ParticleSetFile set = ParticleSetFile.Parse(bytes);
        Assert.Equal(bytes, set.ToBytes());
    }

    /// <summary>
    /// The census. <c>Num_Particle_Descriptors</c> is exact, and the type
    /// histogram is the one measured across the shipped file.
    /// </summary>
    [Fact]
    public void ShippedMainSetCensusIsExact()
    {
        ParticleSetFile set = ParticleSetFile.Parse(ReadMainSet());
        Assert.Equal(1_405, set.DeclaredCount);
        Assert.Equal(set.DeclaredCount, set.Descriptors.Count);
        Assert.StartsWith(
            "ParticleSystemEd_File_(C)2000_Lost_Toys_Ltd",
            set.Header,
            StringComparison.Ordinal);

        Dictionary<int, int> byType = [];
        foreach (ParticleDescriptor descriptor in set.Descriptors)
        {
            byType[descriptor.TypeId] = byType.GetValueOrDefault(descriptor.TypeId) + 1;
        }

        Assert.Equal(
            new Dictionary<int, int>
            {
                [1] = 378,
                [2] = 327,
                [4] = 34,
                [5] = 92,
                [6] = 253,
                [7] = 73,
                [8] = 99,
                [9] = 8,
                [10] = 42,
                [11] = 12,
                [12] = 20,
                [13] = 67,
            },
            byType);
    }

    /// <summary>
    /// <b>The corpus census, over every shipped <c>.par</c> file rather than the
    /// one the sun happens to need.</b> A decoder proven on one file is a decoder
    /// proven on one file; this parses all three, re-emits each byte-identically,
    /// and recomputes the whole 1,479-descriptor type histogram from the files.
    ///
    /// <para>Every number below is derived at test time. Nothing is read from a
    /// constant the decoder also writes, so a wrong reading of the record
    /// framing - a missed separator, a swallowed blank line, a mis-split
    /// key/value - moves a count here and fails, rather than agreeing with
    /// itself.</para>
    /// </summary>
    [Fact]
    public void TheWholeShippedCorpusDecodesReEmitsAndCensusesExactly()
    {
        Dictionary<int, int> corpusByType = [];
        int corpusDescriptors = 0;

        foreach ((string name, int length, string sha256, int declared) in ShippedCorpus)
        {
            byte[] bytes = File.ReadAllBytes(Locate($"{ParticleSetDirectory}/{name}"));
            Assert.Equal(length, bytes.Length);
            Assert.Equal(
                sha256,
                Convert.ToHexString(System.Security.Cryptography.SHA256.HashData(bytes)));

            ParticleSetFile set = ParticleSetFile.Parse(bytes);

            // The falsifiability check, per file.
            Assert.Equal(bytes, set.ToBytes());

            // The header count and the records actually framed out agree.
            Assert.Equal(declared, set.DeclaredCount);
            Assert.Equal(declared, set.Descriptors.Count);
            Assert.StartsWith(
                "ParticleSystemEd_File_(C)2000_Lost_Toys_Ltd",
                set.Header,
                StringComparison.Ordinal);
            Assert.Equal("File_Version 1.000000", set.VersionLine);

            corpusDescriptors += set.Descriptors.Count;
            foreach (ParticleDescriptor descriptor in set.Descriptors)
            {
                corpusByType[descriptor.TypeId] =
                    corpusByType.GetValueOrDefault(descriptor.TypeId) + 1;

                // Every descriptor is named and typed; no record is a fragment.
                Assert.NotEmpty(descriptor.Name);
                Assert.True(
                    Enum.IsDefined(descriptor.Type),
                    $"'{descriptor.Name}' in {name} carries unshipped type " +
                    $"{descriptor.TypeId}.");
            }
        }

        Assert.Equal(1_479, corpusDescriptors);
        Assert.Equal(corpusDescriptors, corpusByType.Values.Sum());

        // Twelve record types are authored. Retail's type 3 CPDModifier is now
        // statically proven, but no shipped descriptor instantiates it.
        Assert.Equal(
            new Dictionary<int, int>
            {
                [1] = 405,
                [2] = 338,
                [4] = 40,
                [5] = 97,
                [6] = 258,
                [7] = 77,
                [8] = 100,
                [9] = 14,
                [10] = 46,
                [11] = 13,
                [12] = 24,
                [13] = 67,
            },
            corpusByType);
        Assert.DoesNotContain(3, corpusByType.Keys);
        Assert.True(Enum.IsDefined(ParticleDescriptorType.Modifier));
    }

    /// <summary>
    /// The pristine executable contains 124 case-sensitive token names and one
    /// 125-byte parse-kind table. This recomputes the distinct shipped keys
    /// from all three files and requires every one to land in that exact retail
    /// partition. Unknown mod fields remain losslessly parseable, but they are
    /// not silently described as retail-recognized tokens.
    /// </summary>
    [Fact]
    public void RetailTokenTableCoversEveryShippedKeyExactly()
    {
        HashSet<string> tokenNames = new(StringComparer.Ordinal)
        {
            "ParticleSystemEd_File_(C)2000_Lost_Toys_Ltd",
            "File_Version",
            "Num_Particle_Descriptors",
            "Particle_Descriptor_Type",
            "Particle_Descriptor_Name",
            ParticleSetFile.RecordSeparator,
        };

        foreach ((string name, _, _, _) in ShippedCorpus)
        {
            ParticleSetFile set = ParticleSetFile.Parse(
                File.ReadAllBytes(Locate($"{ParticleSetDirectory}/{name}")));
            foreach (ParticleDescriptor descriptor in set.Descriptors)
            {
                foreach (ParticleField field in descriptor.Fields)
                {
                    tokenNames.Add(field.Key);
                }
            }
        }

        Dictionary<RetailParticleTokenParseKind, int> byKind = [];
        foreach (string tokenName in tokenNames)
        {
            Assert.True(
                RetailParticleTokenContract.TryGetParseKind(tokenName, out var kind),
                $"Shipped token '{tokenName}' is absent from the retail registry.");
            byKind[kind] = byKind.GetValueOrDefault(kind) + 1;
        }

        Assert.Equal(124, tokenNames.Count);
        Assert.Equal(
            new Dictionary<RetailParticleTokenParseKind, int>
            {
                [RetailParticleTokenParseKind.MarkerNoValue] = 2,
                [RetailParticleTokenParseKind.DirectFloat] = 19,
                [RetailParticleTokenParseKind.DirectInt] = 47,
                [RetailParticleTokenParseKind.RawRemainderString] = 3,
                [RetailParticleTokenParseKind.FloatWithOptionalReference] = 37,
                [RetailParticleTokenParseKind.ReferenceName] = 16,
            },
            byKind);
        StringBuilder exactMapping = new();
        foreach (string tokenName in tokenNames.Order(StringComparer.Ordinal))
        {
            Assert.True(RetailParticleTokenContract.TryGetParseKind(tokenName, out var kind));
            exactMapping
                .Append(tokenName)
                .Append('\t')
                .Append((int)kind)
                .Append('\n');
        }
        Assert.Equal(
            "b99eb664bfbfb7f215ca3fbbbfa253a5f24267bcb2a0567a4ca0a0ea45d22d2c",
            Convert.ToHexString(SHA256.HashData(
                Encoding.UTF8.GetBytes(exactMapping.ToString()))).ToLowerInvariant());
        Assert.False(RetailParticleTokenContract.TryGetParseKind(
            "Future_Modded_Field", out var unknown));
        Assert.Equal(RetailParticleTokenParseKind.Unrecognized, unknown);
    }

    /// <summary>Factory type ids bind to exact retail RTTI loaders.</summary>
    [Fact]
    public void RetailDescriptorFactoryCoversAllThirteenTypes()
    {
        (string ClassName, uint Loader)[] expected =
        [
            ("CPDSimpleSprite", 0x004C05C0),
            ("CPDEmitter", 0x004C1810),
            ("CPDModifier", 0x004C20C0),
            ("CPDSelector", 0x004C2130),
            ("CPDColourRange", 0x004C2300),
            ("CPDTimeline", 0x004C24C0),
            ("CPDShape", 0x004C2B70),
            ("CPDTrail", 0x004C3120),
            ("CPDMover", 0x004C4420),
            ("CPDFunction", 0x004C4840),
            ("CPDMesh", 0x004C4B00),
            ("CPDFoR", 0x004C5330),
            ("CPDPMesh", 0x004C5730),
        ];

        for (int typeId = 1; typeId <= expected.Length; typeId++)
        {
            Assert.Equal(
                expected[typeId - 1].ClassName,
                RetailParticleTokenContract.DescriptorClassName(typeId));
            Assert.Equal(
                expected[typeId - 1].Loader,
                RetailParticleTokenContract.DescriptorLoaderAddress(typeId));
            Assert.True(Enum.IsDefined((ParticleDescriptorType)typeId));
        }
    }

    /// <summary>
    /// Retail's writer treats Velocity_Randomness as float-plus-reference, but
    /// its reader's token table classifies it as a direct float. Every shipped
    /// emitter masks the defect by placing it immediately after
    /// Initial_Velocity_Z with the same NONE-or-missing suffix.
    /// </summary>
    [Fact]
    public void VelocityRandomnessPinsTheMaskedRetailReaderDefect()
    {
        Assert.True(RetailParticleTokenContract.TryGetParseKind(
            "Initial_Velocity_Z", out var priorKind));
        Assert.True(RetailParticleTokenContract.TryGetParseKind(
            "Velocity_Randomness", out var velocityKind));
        Assert.Equal(RetailParticleTokenParseKind.FloatWithOptionalReference, priorKind);
        Assert.Equal(RetailParticleTokenParseKind.DirectFloat, velocityKind);

        int emitters = 0;
        int noneSuffixes = 0;
        int missingSuffixes = 0;
        foreach ((string name, _, _, _) in ShippedCorpus)
        {
            ParticleSetFile set = ParticleSetFile.Parse(
                File.ReadAllBytes(Locate($"{ParticleSetDirectory}/{name}")));
            foreach (ParticleDescriptor emitter in set.Descriptors.Where(
                descriptor => descriptor.Type == ParticleDescriptorType.Emitter))
            {
                int velocityIndex = -1;
                for (int index = 0; index < emitter.Fields.Count; index++)
                {
                    if (emitter.Fields[index].Key == "Velocity_Randomness")
                    {
                        velocityIndex = index;
                        break;
                    }
                }

                Assert.True(velocityIndex > 0);
                ParticleField prior = emitter.Fields[velocityIndex - 1];
                ParticleField velocity = emitter.Fields[velocityIndex];
                Assert.Equal("Initial_Velocity_Z", prior.Key);
                Assert.NotNull(prior.Value);
                Assert.NotNull(velocity.Value);

                string priorSuffix = Suffix(prior.Value!);
                string velocitySuffix = Suffix(velocity.Value!);
                Assert.Equal(priorSuffix, velocitySuffix);
                Assert.True(priorSuffix is "NONE" or "");
                Assert.Equal(
                    emitter.FloatWithModifier("Velocity_Randomness").Value,
                    emitter.RetailDirectFloat("Velocity_Randomness"));

                emitters++;
                if (velocitySuffix == "NONE")
                {
                    noneSuffixes++;
                }
                else
                {
                    missingSuffixes++;
                }
            }
        }

        Assert.Equal(338, emitters);
        Assert.Equal(336, noneSuffixes);
        Assert.Equal(2, missingSuffixes);
    }

    /// <summary>
    /// <b>The animation law.</b> For every <c>Anim_Type 1</c> sprite the file
    /// authors, <c>Life * Anim_Speed</c> equals <c>End_Frame - Texture_Number</c>
    /// exactly. That identity is what proves the sprite starts at
    /// <c>Texture_Number</c> rather than at cell 0: the eleven records that
    /// author a non-zero <c>Texture_Number</c> only satisfy it under this
    /// reading, and under the "start at 0" reading three of them are off by more
    /// than a factor of two.
    /// </summary>
    [Fact]
    public void PlayOnceSpritesLandOnTheirLastAtlasCellExactly()
    {
        ParticleSetFile set = ParticleSetFile.Parse(ReadMainSet());
        int checkedSprites = 0;
        int withExplicitStartCell = 0;
        foreach (ParticleDescriptor sprite in set.Descriptors)
        {
            if (sprite.TypeId != 1 || sprite.Int("Anim_Type") != 1)
            {
                continue;
            }

            int life = sprite.Int("Life");
            int startCell = sprite.Int("Texture_Number");
            int endCell = sprite.Int("End_Frame");
            int span = endCell - Math.Max(startCell, 0);
            if (life < 0 || span <= 0)
            {
                continue;
            }

            checkedSprites++;
            if (startCell > 0)
            {
                withExplicitStartCell++;
            }

            double travelled = life * sprite.Float("Anim_Speed");
            Assert.True(
                Math.Abs(travelled - span) <= 0.02 * span,
                $"'{sprite.Name}' travels {travelled:F4} cells over its life but its " +
                $"authored span {startCell}..{endCell} is {span}.");
        }

        Assert.Equal(56, checkedSprites);
        Assert.Equal(11, withExplicitStartCell);
    }

    /// <summary>
    /// <b>The atlas law.</b> <c>Texture_Size</c> selects the grid the sprite
    /// indexes: 2 is 4x4, 3 is 2x2, 4 is the whole texture. Every sprite that
    /// actually indexes the grid stays inside it.
    ///
    /// <para>The four shipped records that would violate this all author
    /// <c>Anim_Type 0</c>, where <c>End_Frame</c> is inert, so the check is
    /// restricted to the sprites that read the field.</para>
    /// </summary>
    [Fact]
    public void AtlasCellsNeverEscapeTheGridTheirTextureSizeSelects()
    {
        ParticleSetFile set = ParticleSetFile.Parse(ReadMainSet());
        int animating = 0;
        int staticWithCell = 0;
        foreach (ParticleDescriptor sprite in set.Descriptors)
        {
            if (sprite.TypeId != 1)
            {
                continue;
            }

            int side = ParticleEffectResolver.AtlasGridSide(sprite.Int("Texture_Size"));
            int cells = side * side;
            int startCell = sprite.Int("Texture_Number");
            int endCell = sprite.Int("End_Frame");
            bool animates = sprite.Int("Anim_Type") != 0;

            if (animates)
            {
                animating++;
                Assert.True(
                    startCell >= -1 && startCell < cells && endCell < cells,
                    $"'{sprite.Name}' animates cells {startCell}..{endCell} in a " +
                    $"{side}x{side} grid.");
                continue;
            }

            if (startCell < 0)
            {
                continue;
            }

            staticWithCell++;
            Assert.True(
                startCell < cells,
                $"'{sprite.Name}' selects cell {startCell} in a {side}x{side} grid.");
        }

        Assert.Equal(161, animating);
        Assert.Equal(91, staticWithCell);
    }

    /// <summary>
    /// Hole 1. The Warehouse is a Level 100 objective and its destruction drew
    /// nothing at all. <c>default physics.dat</c> names
    /// <c>Muspell Building Explosion Effect</c> for it, and Core already
    /// carries that string in
    /// <c>Level100ContactMap.DestructionParticleDescriptor</c>.
    /// </summary>
    [Fact]
    public void WarehouseDestructionResolvesItsAuthoredFourEntryTimeline()
    {
        ParticleSetFile set = ParticleSetFile.Parse(ReadMainSet());
        ParticleDescriptor timeline = set.Require("Muspell Building Explosion Effect");
        Assert.Equal(ParticleDescriptorType.Timeline, timeline.Type);
        Assert.Equal(4, timeline.Int("Num_Entries"));
        Assert.Equal(
            new[]
            {
                "Debris Emitter Medium",
                "Flash Building",
                "Building Smoke Emitter",
                "Muspell Building Explosion Emitter",
            },
            timeline.RawAll("Particle_Descriptor"));

        // All four entries fire at Time 0. The tank's seven-entry timeline is
        // the one with 0/0/0/0/0/5/10 offsets; this one is simultaneous.
        Assert.Equal(new[] { "0", "0", "0", "0" }, timeline.RawAll("Time"));

        ParticleEffectPlan plan = ParticleEffectResolver.Resolve(
            set, "Muspell Building Explosion Effect");

        // The building flash is a single unanimated sun2 sprite, radius 3 for
        // 6 turns - 0.3 s at the released 20 Hz.
        ParticleSpriteLayer flash = Single(plan, "Flash Building");
        Assert.Equal("sun2.tga", flash.TextureName);
        Assert.Equal(1, flash.AtlasColumns);
        Assert.Equal(ParticleAnimationMode.Static, flash.AnimationMode);
        Assert.Equal(3f, flash.StartRadius);
        Assert.Equal(6, flash.LifeTurns);
        Assert.Equal(1, flash.InstanceCount);

        // The smoke column is one alpha-blended alparticle4 sprite on a
        // radius-1.5 sphere, looping cells 0..14 for 300 turns (15 s). One,
        // because `Building Smoke Emitter` authors Emit_Per_Turn 1.0 with
        // Life 0 - a single-turn burst of one - and its Shape supplies the
        // position, not the count.
        ParticleSpriteLayer smoke = Single(plan, "Smoke Sprite Anim Large Building");
        Assert.Equal("alparticle4.tga", smoke.TextureName);
        Assert.Equal(1, smoke.BlendMode);
        Assert.Equal(ParticleAnimationMode.Loop, smoke.AnimationMode);
        Assert.Equal(0, smoke.StartCell);
        Assert.Equal(14, smoke.EndCell);
        Assert.Equal(300, smoke.LifeTurns);
        Assert.True(smoke.RandomStartCell);
        Assert.Equal(1, smoke.InstanceCount);
        Assert.NotNull(smoke.Shape);
        Assert.Equal(1.5f, smoke.Shape!.Value.Radius);
        Assert.Equal("Faint grey to black", smoke.ColourRange!.Value.Name);

        // The fireball body is the additive fireball sheet, cells 0..11.
        ParticleSpriteLayer fire = Single(plan, "Fire Sprite Damped Long");
        Assert.Equal("fireball.tga", fire.TextureName);
        Assert.Equal(0, fire.BlendMode);
        Assert.Equal(11, fire.EndCell);
        Assert.Equal(60, fire.LifeTurns);

        // The authored tree also contains mesh shrapnel, and the resolver says
        // so rather than quietly dropping it.
        Assert.Contains(
            plan.Unimplemented,
            entry => entry.Contains("Shrapnel 4", StringComparison.Ordinal) &&
                entry.Contains("type 11 (Mesh) is authored but not drawn", StringComparison.Ordinal));
        Assert.Contains(
            plan.Unimplemented,
            entry => entry.Contains("Emit_Per_Turn modifier 'Decrease'", StringComparison.Ordinal));

        // 7 debris + 1 flash + 1 smoke + 32 fireball. Every one of those counts
        // comes out of an authored Emit_Per_Turn and Life; none is chosen.
        Assert.Equal(4, plan.Layers.Count);
        Assert.Equal(41, plan.TotalInstances);
        Assert.Equal(7, Single(plan, "Debris Sprite").InstanceCount);
        Assert.Equal(32, fire.InstanceCount);
    }

    [Fact]
    public void TargetTankExplosionUsesAuthoredSpriteTimingAndAtlasLaws()
    {
        ParticleSetFile set = ParticleSetFile.Parse(ReadMainSet());
        ParticleDescriptor timeline = set.Require("Tank Explosion Medium");
        Assert.Equal(ParticleDescriptorType.Timeline, timeline.Type);
        IReadOnlyList<string> entries = timeline.RawAll("Particle_Descriptor");
        IReadOnlyList<string> times = timeline.RawAll("Time");
        int flashIndex = entries.ToList().IndexOf("Flash");
        Assert.True(flashIndex >= 0);
        Assert.Equal("0", times[flashIndex]);
        int directSpriteIndex = entries.ToList().IndexOf("Explosion Anim Sprite Medium");
        Assert.True(directSpriteIndex >= 0);
        Assert.Equal("5", times[directSpriteIndex]);

        ParticleEffectPlan plan = ParticleEffectResolver.Resolve(
            set,
            "Tank Explosion Medium");
        ParticleSpriteLayer flash = Single(plan, "Flash");
        Assert.Equal(new[] { 0 }, flash.StartTurns);
        Assert.Equal("sun2.tga", flash.TextureName);
        Assert.Equal(5, flash.LifeTurns);
        Assert.Equal(5f, flash.StartRadius);
        Assert.Equal(0f, flash.FinalRadius);
        Assert.Equal(1, flash.AtlasColumns);

        ParticleSpriteLayer direct = Single(plan, "Explosion Anim Sprite Medium");
        Assert.Equal(new[] { 5 }, direct.StartTurns);
        Assert.Equal(ParticleAnimationMode.PlayOnce, direct.AnimationMode);
        Assert.Equal(0, direct.StartCell);
        Assert.Equal(7, direct.EndCell);
        Assert.Equal(0.7f, direct.AnimationCellsPerTurn);
        Assert.Equal(10, direct.LifeTurns);
        Assert.Equal(1.5f, direct.StartRadius);
        Assert.Equal(1.3f, direct.FinalRadius);

        ParticleSpriteLayer fireball = Single(plan, "Fire Sprite Damped 2");
        Assert.Equal(ParticleAnimationMode.Loop, fireball.AnimationMode);
        Assert.True(fireball.RandomStartCell);
        Assert.Equal(0, fireball.StartCell);
        Assert.Equal(11, fireball.EndCell);
        Assert.Equal(0.5f, fireball.AnimationCellsPerTurn);
        Assert.Equal(30, fireball.LifeTurns);
        Assert.Equal(1f, fireball.StartRadius);
        Assert.Equal(0.5f, fireball.FinalRadius);

        string worldSource = File.ReadAllText(Locate(
            "rebuild/OnslaughtRebuild.Godot/FirstFlightWorldView.cs"));
        string spawn = RequireSection(
            worldSource,
            "private void SpawnTargetTankDestruction(",
            "private void SpawnTargetDroneDestruction(");
        Assert.Contains(
            "SpawnDestructionScene(TargetTankDestructionScenePath, $\"TargetTankDestruction{targetId}\", position)",
            spawn, StringComparison.Ordinal);
        string spawnScene = RequireSection(worldSource, "private void SpawnDestructionScene(", "private void UpdateRetailPixelCentreOffset(");
        AssertSourceOrder(spawnScene,
            "GD.Load<PackedScene>(path)",
            "scene.Instantiate<Node3D>()",
            "root.Name = name;",
            "root.Position = position;",
            "AddChild(root);",
            "root.Call(\"start\")",
            "WorldPresentationResult(returned)");
        Assert.DoesNotContain("AnimateTargetTankDelayedExplosion", worldSource, StringComparison.Ordinal);
        Assert.DoesNotContain("AnimateLoopingFireball", worldSource, StringComparison.Ordinal);
        Assert.DoesNotContain("AnimateFacilitySmoke", worldSource, StringComparison.Ordinal);

        // These are the actual production profiles and controller, not a
        // retained renderer. Their named mesh radii are checked separately in
        // ParticleQuadSizeConventionTests. Actual callback and material-state
        // parity belongs to the dedicated scene checks, beyond this source guard.
        foreach ((string name, string profile, string lifetime) in new[]
        {
            ("TargetTankDestruction", "tank", "1.5"),
            ("TargetDroneDestruction", "drone", "1.5"),
            ("FacilityDestruction", "facility", "15.0"),
        })
        {
            string scene = File.ReadAllText(Locate($"rebuild/OnslaughtRebuild.Godot/Scenes/World/{name}.tscn"));
            Assert.Contains($"{name}ScenePath = \"res://Scenes/World/{name}.tscn\"", worldSource, StringComparison.Ordinal);
            Assert.Contains("res://Scenes/World/destruction_effect.gd", scene, StringComparison.Ordinal);
            Assert.Contains($"profile = \"{profile}\"", scene, StringComparison.Ordinal);
            string timer = RequireSection(scene, "[node name=\"Lifetime\" type=\"Timer\" parent=\".\"]", "[node ");
            Assert.Contains($"wait_time = {lifetime}\n", timer, StringComparison.Ordinal);
            Assert.Contains("one_shot = true", timer, StringComparison.Ordinal);
            Assert.DoesNotContain("autostart = true", timer, StringComparison.Ordinal);
        }

        string animation = File.ReadAllText(Locate("rebuild/OnslaughtRebuild.Godot/Scenes/World/destruction_effect.gd"));
        Assert.Contains("TICKS_PER_SECOND: int = 20", animation, StringComparison.Ordinal);
        Assert.Contains("COLUMNS: int = 4", animation, StringComparison.Ordinal);
        Assert.Contains("ROWS: int = 4", animation, StringComparison.Ordinal);
        Assert.DoesNotContain("func _ready(", animation, StringComparison.Ordinal);
        Assert.DoesNotContain("func _process(", animation, StringComparison.Ordinal);
        string start = RequireSection(animation, "func start()", "func _start_tank()");
        AssertSourceOrder(start,
            "if Engine.is_editor_hint():",
            "if _started or not is_inside_tree():",
            "_started = true",
            "lifetime.timeout.connect(queue_free)",
            "lifetime.start()",
            "\"tank\": _start_tank()",
            "\"drone\": _start_drone()",
            "\"facility\": _start_facility()");

        string tank = RequireSection(animation, "func _start_tank()", "func _start_drone()");
        AssertSourceOrder(tank,
            "_layer(\"TargetTankFlash\")",
            "_animate_scale(flash, 1.0, 0.0, 0.25)",
            "_layer(\"ExplosionAnimatedSprite\")",
            "_animate_tank_delayed(explosion)",
            "_layer(\"ExplosionFireball\")",
            "_animate_looping_fireball(fireball, 30)",
            "_animate_scale(fireball, 1.0, 0.5, 1.5)");
        string drone = RequireSection(animation, "func _start_drone()", "func _start_facility()");
        AssertSourceOrder(drone,
            "_layer(\"DroneFlash\")",
            "_animate_scale(flash, 1.0, 0.0, 0.25)",
            "_layer(\"DroneFireball\")",
            "_animate_looping_fireball(fireball, 30)",
            "_animate_scale(fireball, 1.0, 0.5, 1.5)");
        string facility = RequireSection(animation, "func _start_facility()", "func _layer(");
        AssertSourceOrder(facility,
            "_layer(\"FacilityFlash\")",
            "_animate_scale(flash, 1.0, 0.0, 0.3)",
            "_layer(\"FacilityFireball\")",
            "_animate_looping_fireball(fireball, 60)",
            "_animate_scale(fireball, 1.0, 4.0, 3.0)",
            "_layer(\"FacilitySmoke\")",
            "_animate_facility_smoke(smoke)",
            "_animate_scale(smoke, 1.0, F.value(2.0 / 3.0), 15.0)");
        string facilityScene = File.ReadAllText(Locate("rebuild/OnslaughtRebuild.Godot/Scenes/World/FacilityDestruction.tscn"));
        string smokeMaterial = RequireSection(facilityScene, "[sub_resource type=\"StandardMaterial3D\" id=\"SmokeMaterial\"]", "[sub_resource ");
        Assert.Contains("blend_mode = 0", smokeMaterial, StringComparison.Ordinal);
        Assert.Matches(
            @"(?s)\[node name=""FacilitySmoke"" type=""MeshInstance3D""[^\]]*\][^\[]*" +
            @"material_override = SubResource\(""SmokeMaterial""\)",
            facilityScene);

        string layer = RequireSection(animation, "func _layer(", "func _animate_tank_delayed(");
        Assert.Contains("sprite.material_override = sprite.material_override.duplicate(false)", layer, StringComparison.Ordinal);
        string delayed = RequireSection(animation, "func _animate_tank_delayed(", "func _animate_looping_fireball(");
        Assert.Contains("START_CELL: int = 0", delayed, StringComparison.Ordinal);
        Assert.Contains("END_CELL: int = 7", delayed, StringComparison.Ordinal);
        Assert.Contains("CELLS_PER_TURN: float = 0.7", delayed, StringComparison.Ordinal);
        Assert.Contains("LIFE_SECONDS: float = 0.5", delayed, StringComparison.Ordinal);
        Assert.Contains("5.0 / TICKS_PER_SECOND", delayed, StringComparison.Ordinal);
        Assert.Contains("1.0 / (CELLS_PER_TURN * TICKS_PER_SECOND)", delayed, StringComparison.Ordinal);
        AssertSourceOrder(delayed,
            "_set_cell(material, START_CELL)",
            "sprite.visible = false",
            "sprite.scale = Vector3.ONE",
            "var atlas: Tween = create_tween()",
            "atlas.tween_interval(start_delay)",
            "atlas.tween_callback(_set_visible.bind(sprite, true))",
            "range(START_CELL + 1, END_CELL + 1)",
            "atlas.tween_interval(interval)",
            "atlas.tween_callback(_set_cell.bind(material, cell))",
            "var scaling: Tween = create_tween()",
            "scaling.tween_interval(start_delay)",
            "F.value(F.value(1.3) / F.value(1.5))",
            "scaling.tween_property(sprite, \"scale\", Vector3.ONE * final_scale, LIFE_SECONDS)",
            "scaling.tween_callback(_set_visible.bind(sprite, false))");

        string looping = RequireSection(animation, "func _animate_looping_fireball(", "func _animate_facility_smoke(");
        string smoke = RequireSection(animation, "func _animate_facility_smoke(", "func _animate_scale(");
        foreach ((string source, int endCell, string lifeTurns) in new[]
        {
            (looping, 11, "life_turns"),
            (smoke, 14, "LIFE_TURNS"),
        })
        {
            Assert.Contains("START_CELL: int = 0", source, StringComparison.Ordinal);
            Assert.Contains($"END_CELL: int = {endCell}", source, StringComparison.Ordinal);
            Assert.Contains("CELLS_PER_TURN: float = 0.5", source, StringComparison.Ordinal);
            Assert.Contains("cell_count: int = END_CELL - START_CELL + 1", source, StringComparison.Ordinal);
            AssertSourceOrder(source,
                "initial_cell: int = START_CELL + (randi() % cell_count)",
                "1.0 / (CELLS_PER_TURN * TICKS_PER_SECOND)",
                $"int({lifeTurns} * CELLS_PER_TURN)",
                "_set_cell(material, initial_cell)",
                "var atlas: Tween = create_tween()",
                "range(1, advances + 1)",
                "START_CELL + ((initial_cell - START_CELL + step) % cell_count)",
                "atlas.tween_interval(interval)",
                "atlas.tween_callback(_set_cell.bind(material, cell))");
        }

        Assert.Contains("atlas.tween_callback(_set_visible.bind(sprite, false))", looping, StringComparison.Ordinal);
        Assert.Contains("LIFE_TURNS: int = 300", smoke, StringComparison.Ordinal);
        Assert.DoesNotContain("_set_visible", smoke, StringComparison.Ordinal);
        string scaling = RequireSection(animation, "func _animate_scale(", "func _set_cell(");
        Assert.Contains("sprite.scale = Vector3.ONE * F.value(start_scale)", scaling, StringComparison.Ordinal);
        Assert.Contains("sprite.create_tween().tween_property(sprite, \"scale\", Vector3.ONE * F.value(end_scale), duration)", scaling, StringComparison.Ordinal);
    }

    [Fact]
    public void VulcanRoundImpactUsesAuthoredDirectSpark()
    {
        ParticleSetFile set = ParticleSetFile.Parse(ReadMainSet());
        ParticleDescriptor timeline = set.Require("Mech Bullet Hit Unit Effect");
        Assert.Equal(ParticleDescriptorType.Timeline, timeline.Type);
        IReadOnlyList<string> entries = timeline.RawAll("Particle_Descriptor");
        IReadOnlyList<string> times = timeline.RawAll("Time");
        int sparkIndex = entries.ToList().IndexOf("Spark Anim Sprite");
        Assert.True(sparkIndex >= 0);
        Assert.Equal("0", times[sparkIndex]);

        ParticleEffectPlan plan = ParticleEffectResolver.Resolve(
            set,
            "Mech Bullet Hit Unit Effect");
        ParticleSpriteLayer spark = Single(plan, "Spark Anim Sprite");
        Assert.Equal(new[] { 0 }, spark.StartTurns);
        Assert.Equal("alparticle2.tga", spark.TextureName);
        Assert.Equal(0, spark.BlendMode);
        Assert.Equal(0.3f, spark.StartRadius);
        Assert.Equal(1f, spark.FinalRadius);
        Assert.Equal(5, spark.LifeTurns);
        Assert.Equal(4, spark.AtlasColumns);
        Assert.Equal(ParticleAnimationMode.PlayOnce, spark.AnimationMode);
        Assert.Equal(11, spark.StartCell);
        Assert.Equal(15, spark.EndCell);
        Assert.Equal(0.8f, spark.AnimationCellsPerTurn);
        ParticleEffectPlan groundPlan = ParticleEffectResolver.Resolve(
            set,
            "Bullet Ground Hit Effect");
        ParticleSpriteLayer groundSpark = Single(groundPlan, "Spark Anim Sprite");
        Assert.Equal(new[] { 0 }, groundSpark.StartTurns);
        Assert.Equal(spark.TextureName, groundSpark.TextureName);
        Assert.Equal(spark.StartCell, groundSpark.StartCell);
        Assert.Equal(spark.EndCell, groundSpark.EndCell);

        string simulationSource = File.ReadAllText(Locate(
            "rebuild/OnslaughtRebuild.Core/Simulation.cs"));
        string projectileUpdate = RequireSection(
            simulationSource,
            "private void UpdateProjectiles()",
            "private void ResetDynamicState()");
        Assert.Contains("projectile.Kind switch", projectileUpdate, StringComparison.Ordinal);
        Assert.Contains(
            "Level100ProjectileKind.MechPulseBoltMedium =>",
            projectileUpdate,
            StringComparison.Ordinal);
        Assert.Contains(
            "Level100ProjectileKind.MechBullet or",
            projectileUpdate,
            StringComparison.Ordinal);
        Assert.Contains(
            "Level100ProjectileKind.MechAirBullet =>",
            projectileUpdate,
            StringComparison.Ordinal);
        Assert.Contains(
            "Level100DestructionEffectKind.VulcanImpact",
            projectileUpdate,
            StringComparison.Ordinal);

        string worldSource = File.ReadAllText(Locate(
            "rebuild/OnslaughtRebuild.Godot/FirstFlightWorldView.cs"));
        string eventSwitch = RequireSection(
            worldSource,
            "public void ConsumeLevel100DestructionEvents(",
            "public void ConsumeLevel100WeaponFireEvents(");
        Assert.Contains(
            "case Level100DestructionEffectKind.VulcanImpact:",
            eventSwitch,
            StringComparison.Ordinal);
        Assert.Contains(
            "SpawnVulcanImpact(position, item.ActorId, tick);",
            eventSwitch,
            StringComparison.Ordinal);

        string spawn = RequireSection(
            worldSource,
            "private void SpawnVulcanImpact(",
            "private void SpawnTargetTankDestruction(");
        Assert.Contains("GD.Load<PackedScene>(VulcanImpactScenePath)", spawn, StringComparison.Ordinal);
        Assert.Contains("Node3D root = scene.Instantiate<Node3D>();", spawn, StringComparison.Ordinal);
        Assert.Contains("root.Name = $\"VulcanImpact{targetId}-{tick}\";", spawn, StringComparison.Ordinal);
        Assert.Contains("root.Position = position;", spawn, StringComparison.Ordinal);
        Assert.Contains("AddChild(root);", spawn, StringComparison.Ordinal);
        Assert.Contains("root.Call(\"start\")", spawn, StringComparison.Ordinal);
        Assert.DoesNotContain("AnimateVulcanImpactSpark", worldSource, StringComparison.Ordinal);
        Assert.DoesNotContain("_vulcanImpactSparkTexture", worldSource, StringComparison.Ordinal);

        string presentation = RequireSection(worldSource, "private void BuildPulseCannonPresentation(", "private void SpawnPulseImpact(");
        // Keep all six admission slots. PulseImpact and the destruction
        // scenes share the same blob/flash recipe objects.
        int priorAdmission = -1;
        foreach (string marker in new[]
        {
            "AdmitDestructionArtwork(\"animated_blob\")",
            "pulse.Call(\"admit_artwork\")",
            "effect.Call(\"admit_artwork\")",
            "AdmitDestructionArtwork(\"flash_medium\")",
            "AdmitDestructionArtwork(\"explosion_animated\")",
            "AdmitDestructionArtwork(\"fireball\")",
        })
        {
            int admission = presentation.IndexOf(marker, StringComparison.Ordinal);
            Assert.True(admission > priorAdmission, $"Texture admission '{marker}' moved before its original slot.");
            Assert.Equal(admission, presentation.LastIndexOf(marker, StringComparison.Ordinal));
            priorAdmission = admission;
        }
        AssertSourceOrder(presentation,
            "GD.Load<GDScript>(PulseImpactScriptPath)",
            "pulse.Call(\"admit_artwork\")",
            "WorldPresentationResult(returned)",
            "GD.Load<GDScript>(VulcanImpactScriptPath)",
            "effect.Call(\"admit_artwork\")",
            "WorldPresentationResult(returned)");

        string scene = File.ReadAllText(Locate("rebuild/OnslaughtRebuild.Godot/Scenes/World/VulcanImpact.tscn"));
        Assert.Contains("res://Scenes/World/vulcan_impact.gd", scene, StringComparison.Ordinal);
        Assert.Contains("res://Scenes/World/VulcanImpactTexture.tres", scene, StringComparison.Ordinal);
        Assert.Contains("wait_time = 0.25", scene, StringComparison.Ordinal);
        Assert.Contains("one_shot = true", scene, StringComparison.Ordinal);
        Assert.Contains("size = Vector2(0.6, 0.6)", scene, StringComparison.Ordinal);
        Assert.Contains("albedo_color = Color(1, 1, 1, 1)", scene, StringComparison.Ordinal);
        Assert.Contains("blend_mode = 1", scene, StringComparison.Ordinal);
        Assert.Contains("uv1_scale = Vector3(0.25, 0.25, 1)", scene, StringComparison.Ordinal);
        Assert.Contains("uv1_offset = Vector3(0.75, 0.5, 0)", scene, StringComparison.Ordinal);
        string recipe = File.ReadAllText(Locate("rebuild/OnslaughtRebuild.Godot/Scenes/World/VulcanImpactTexture.tres"));
        Assert.Contains("res://Assets/Level100/Textures/vulcan-impact-spark.texture.aya", recipe, StringComparison.Ordinal);
        Assert.Contains("dimensions = Vector2i(256, 256)", recipe, StringComparison.Ordinal);
        Assert.Contains("compression = 0", recipe, StringComparison.Ordinal);
        string animation = File.ReadAllText(Locate("rebuild/OnslaughtRebuild.Godot/Scenes/World/vulcan_impact.gd"));
        Assert.Contains("ARTWORK = preload(\"res://Scenes/World/VulcanImpactTexture.tres\")", animation, StringComparison.Ordinal);
        Assert.Contains("ARTWORK.ensure_loaded()", animation, StringComparison.Ordinal);
        Assert.Contains("START_CELL: int = 11", animation, StringComparison.Ordinal);
        Assert.Contains("END_CELL: int = 15", animation, StringComparison.Ordinal);
        Assert.Contains("CELLS_PER_TURN: float = 0.8", animation, StringComparison.Ordinal);
        Assert.Contains("TICKS_PER_SECOND: int = 20", animation, StringComparison.Ordinal);
        Assert.Contains("1.0 / (CELLS_PER_TURN * TICKS_PER_SECOND)", animation, StringComparison.Ordinal);
        Assert.Contains("range(START_CELL + 1, END_CELL + 1)", animation, StringComparison.Ordinal);
        Assert.Contains("atlas.tween_interval(interval)", animation, StringComparison.Ordinal);
        Assert.Contains("atlas.tween_callback(_set_cell.bind(material, cell))", animation, StringComparison.Ordinal);
        Assert.Contains("Vector3.ONE * F.value(10.0 / 3.0), 0.25", animation, StringComparison.Ordinal);
        Assert.Contains("spark.create_tween().tween_property", animation, StringComparison.Ordinal);
        Assert.Contains("lifetime.timeout.connect(queue_free)", animation, StringComparison.Ordinal);
        Assert.DoesNotContain("func _ready(", animation, StringComparison.Ordinal);
        Assert.DoesNotContain("randi(", animation, StringComparison.Ordinal);

        string materializer = File.ReadAllText(Locate(
            "rebuild/tools/materialize_retail_assets.py"));
        Assert.Contains(
            "Particle%alparticle2.tga(0)R5G6B5.aya\", \"95c15d4269ffea56e7be13ac7fb64a71a999cce2b9417cb73ce9c7313cef4389\"",
            materializer,
            StringComparison.Ordinal);

        string audioSource = File.ReadAllText(Path.Combine(
            AppContext.BaseDirectory, "godot-audio-layout-source", "level100_audio.gd"));
        int audioStart = audioSource.IndexOf("func consume_destruction_events(", StringComparison.Ordinal);
        Assert.True(audioStart >= 0);
        int audioEnd = audioSource.IndexOf("\nfunc ", audioStart + 1, StringComparison.Ordinal);
        Assert.True(audioEnd > audioStart);
        Assert.Contains(
            $"0, {(int)Level100DestructionEffectKind.VulcanImpact}: continue",
            audioSource[audioStart..audioEnd],
            StringComparison.Ordinal);
    }

    [Fact]
    public void PulseImpactUsesRetainedNativePresentation()
    {
        // Source-wiring checks for the retained b8c1a220 presentation, with
        // actual tween/float-word comparisons owned by the scene checks.
        // This does not promote its representative layers to a complete
        // retail particle emitter or change the retained 1.07 blob scale.
        string worldSource = File.ReadAllText(Locate("rebuild/OnslaughtRebuild.Godot/FirstFlightWorldView.cs"));
        string spawn = RequireSection(worldSource, "private void SpawnPulseImpact(", "private void SpawnVulcanImpact(");
        AssertSourceOrder(spawn,
            "GD.Load<PackedScene>(PulseImpactScenePath)",
            "scene.Instantiate<Node3D>()",
            "root.Name = $\"PulseImpact{targetId}-{tick}\";",
            "root.Position = position;",
            "AddChild(root);",
            "root.Call(\"start\", _particlePresentationSeconds)",
            "WorldPresentationResult(returned)");
        foreach (string retired in new[]
        {
            "CreateTimedEffect(", "CreateEffectSprite(", "CreateEffectMaterial(",
            "CreatePulseBlastSphere(", "AnimatePulseBlast(", "AnimatePulseImpactBlob(", "AnimateScale(",
            "_pulseImpactAnimatedTexture", "_pulseImpactShockwaveTexture", "_effectFlashMediumTexture",
        })
        {
            Assert.DoesNotContain(retired, worldSource, StringComparison.Ordinal);
        }

        string scene = File.ReadAllText(Locate("rebuild/OnslaughtRebuild.Godot/Scenes/World/PulseImpact.tscn"));
        Assert.Contains("res://Scenes/World/pulse_impact.gd", scene, StringComparison.Ordinal);
        Assert.Contains("res://Scenes/World/EffectAnimatedBlobTexture.tres", scene, StringComparison.Ordinal);
        Assert.Contains("res://Scenes/World/EffectFlashMediumTexture.tres", scene, StringComparison.Ordinal);
        Assert.Contains("res://Scenes/World/PulseShockwaveTexture.tres", scene, StringComparison.Ordinal);
        string timer = RequireSection(scene, "[node name=\"Lifetime\" type=\"Timer\" parent=\".\"]", "[node ");
        Assert.Contains("wait_time = 1.05\n", timer, StringComparison.Ordinal);
        Assert.Contains("one_shot = true", timer, StringComparison.Ordinal);
        Assert.DoesNotContain("autostart = true", timer, StringComparison.Ordinal);
        string sphere = RequireSection(scene, "[sub_resource type=\"SphereMesh\" id=\"BlastSphere\"]", "[node ");
        Assert.Contains("radius = 0.5\n", sphere, StringComparison.Ordinal);
        Assert.Contains("height = 1.0\n", sphere, StringComparison.Ordinal);
        Assert.Contains("radial_segments = 10\n", sphere, StringComparison.Ordinal);
        Assert.Contains("rings = 10\n", sphere, StringComparison.Ordinal);
        Assert.Matches(
            @"(?s)\[node name=""PulseBlastSphere"" type=""MeshInstance3D""[^\]]*\][^\[]*" +
            @"mesh = SubResource\(""BlastSphere""\)", scene);
        string recipe = File.ReadAllText(Locate("rebuild/OnslaughtRebuild.Godot/Scenes/World/PulseShockwaveTexture.tres"));
        Assert.Contains("res://Assets/Level100/Textures/pulse-impact-shockwave.texture.aya", recipe, StringComparison.Ordinal);
        Assert.Contains("dimensions = Vector2i(128, 128)", recipe, StringComparison.Ordinal);
        Assert.Contains("compression = 0", recipe, StringComparison.Ordinal);

        string animation = File.ReadAllText(Locate("rebuild/OnslaughtRebuild.Godot/Scenes/World/pulse_impact.gd"));
        Assert.Contains("ARTWORK = preload(\"res://Scenes/World/PulseShockwaveTexture.tres\")", animation, StringComparison.Ordinal);
        Assert.Contains("ARTWORK.ensure_loaded()", animation, StringComparison.Ordinal);
        Assert.Contains("FRAME_ADVANCES: int = 14", animation, StringComparison.Ordinal);
        Assert.Contains("ATLAS_CELLS: int = 15", animation, StringComparison.Ordinal);
        Assert.DoesNotContain("func _ready(", animation, StringComparison.Ordinal);
        Assert.DoesNotContain("func _process(", animation, StringComparison.Ordinal);
        string start = RequireSection(animation, "func start(", "func _layer(");
        AssertSourceOrder(start,
            "if Engine.is_editor_hint():",
            "if _started or not is_inside_tree():",
            "F.value(global_seconds)",
            "lifetime.timeout.connect(queue_free)",
            "lifetime.start()",
            "_layer(\"BlueAnimatedBlob\")",
            "_animate_blob(blob)",
            "_animate_scale(blob, 1.0, F.value(1.07), 1.0)",
            "_layer(\"FlashMedium\")",
            "_animate_scale(flash, 1.0, 0.0, 0.3)",
            "_layer(\"PulseBlastSphere\")",
            "_animate_blast(sphere, seconds)");
        string layer = RequireSection(animation, "func _layer(", "func _animate_blob(");
        Assert.Contains("sprite.material_override = sprite.material_override.duplicate(false)", layer, StringComparison.Ordinal);
        string blob = RequireSection(animation, "func _animate_blob(", "func _animate_scale(");
        AssertSourceOrder(blob,
            "randi() % ATLAS_CELLS",
            "var atlas: Tween = create_tween()",
            "1.0 / FRAME_ADVANCES",
            "range(FRAME_ADVANCES + 1)",
            "(start_frame + step) % ATLAS_CELLS",
            "atlas.tween_callback(_set_cell.bind(material, frame))",
            "if step < FRAME_ADVANCES:",
            "atlas.tween_interval(interval)");
        // The first random cell remains a deferred callback; one global draw
        // occurs when starting the blob, and no second draw occurs at a tick.
        Assert.DoesNotContain("_set_cell(", blob, StringComparison.Ordinal);
        Assert.Equal(animation.IndexOf("randi()", StringComparison.Ordinal), animation.LastIndexOf("randi()", StringComparison.Ordinal));
        string blast = RequireSection(animation, "func _animate_blast(", "static func initial_scroll(");
        AssertSourceOrder(blast,
            "initial_scroll(global_seconds)",
            "_apply_blast(0.0, sphere, material, initial_v)",
            "create_tween().tween_method(_apply_blast.bind(sphere, material, initial_v), 0.0, 1.0, 0.5)");
        string scroll = RequireSection(animation, "static func initial_scroll(", "static func blast_values(");
        AssertSourceOrder(scroll,
            "F.value(-2.0 * F.value(global_seconds))",
            "F.value(fmod(value, 1.0))",
            "F.value(remainder + 1.0) if remainder < 0.0 else remainder");
        string values = RequireSection(animation, "static func blast_values(", "func _apply_blast(");
        AssertSourceOrder(values,
            "var age: float = F.value(normalized_age)",
            "Vector2.from_angle(age).y",
            "F.value(F.value(F.value(0.6) * sine) + F.value(0.4))",
            "F.value(radius / 0.5)",
            "F.value(F.value(initial_v) - age)",
            "F.value(1.0 + F.value(F.value(0.0 - 1.0) * age))",
            "F.value(1.0 + F.value(F.value(1.0 - 1.0) * age))");
        string apply = RequireSection(animation, "func _apply_blast(", "func _set_cell(");
        AssertSourceOrder(apply,
            "blast_values(initial_v, normalized_age)",
            "sphere.scale = values.scale",
            "material.uv1_offset = values.uv_offset",
            "material.albedo_color = values.color");
    }

    [Fact]
    public void PulseBoltMaterialsUseAuthoredBirthColours()
    {
        ParticleSetFile set = ParticleSetFile.Parse(ReadMainSet());

        AssertBirthColour("Pulse Bolt Trail", "Mid Grey To Black", 0.5f);
        AssertBirthColour(
            "Mech Pulse Bolt Sprite Medium 2",
            "Feint Grey To Black Delayed",
            0.25f);
        AssertBirthColour("Mech Pulse Trail Medium", "Faint grey to black", 0.3f);
        Assert.Null(set.Require("Mech Pulse Bolt Sprite Medium").Reference("Colour_Range"));

        string scene = File.ReadAllText(Locate(
            "rebuild/OnslaughtRebuild.Godot/Scenes/World/PulseBolt.tscn"));
        AssertMaterial("Spark", "1, 1, 1, 1", billboard: true);
        AssertMaterial("Trail", "0.5, 0.5, 0.5, 1", billboard: false);
        AssertMaterial("Halo", "0.25, 0.25, 0.25, 1", billboard: true);
        AssertMaterial("Energy", "0.3, 0.3, 0.3, 1", billboard: false);
        string owner = File.ReadAllText(Locate(
            "rebuild/OnslaughtRebuild.Godot/Scenes/World/world_entities.gd"));
        Assert.Contains("material.albedo_texture = textures[key]", owner, StringComparison.Ordinal);
        Assert.Contains("material.emission_texture = textures[key]", owner, StringComparison.Ordinal);

        void AssertMaterial(string id, string rgba, bool billboard)
        {
            string material = RequireSection(scene,
                $"[sub_resource type=\"StandardMaterial3D\" id=\"{id}\"]", "\n[");
            Assert.Contains("albedo_color = Color(" + rgba + ")", material, StringComparison.Ordinal);
            Assert.Contains("emission = Color(" + rgba + ")", material, StringComparison.Ordinal);
            foreach (string property in new[] { "transparency = 1", "blend_mode = 1", "shading_mode = 0", "cull_mode = 2", "emission_enabled = true" })
                Assert.Contains(property, material, StringComparison.Ordinal);
            Assert.Equal(billboard, material.Contains("billboard_mode = 1", StringComparison.Ordinal));
        }

        void AssertBirthColour(string descriptorName, string rangeName, float value)
        {
            ParticleDescriptor descriptor = set.Require(descriptorName);
            Assert.Equal(rangeName, descriptor.Reference("Colour_Range"));
            ParticleDescriptor range = set.Require(rangeName);
            Assert.Equal(value, range.FloatWithModifier("Start_Red").Value);
            Assert.Equal(value, range.FloatWithModifier("Start_Green").Value);
            Assert.Equal(value, range.FloatWithModifier("Start_Blue").Value);
        }
    }

    [Fact]
    public void PlayerProjectileTrailsUseAuthoredSimulationSamples()
    {
        ParticleSetFile set = ParticleSetFile.Parse(ReadMainSet());
        ParticleDescriptor pulse = set.Require("Pulse Bolt Trail");
        Assert.Equal(ParticleDescriptorType.Trail, pulse.Type);
        Assert.Equal(5, pulse.Int("Num_Points"));
        Assert.Equal(0.08f, pulse.Float("Start_Width"));
        Assert.Equal(0, pulse.Int("Blend_Mode"));
        Assert.Equal(-2, pulse.Int("Life"));

        ParticleDescriptor vulcan = set.Require("Mech Bullet");
        Assert.Equal(ParticleDescriptorType.Trail, vulcan.Type);
        Assert.True(
            vulcan.Raw("Texture")?.EndsWith(
                @"Particle\Bullet.tga",
                StringComparison.OrdinalIgnoreCase) == true);
        Assert.Equal(0, vulcan.Int("Blend_Mode"));
        Assert.Equal(0.02f, vulcan.Float("Width"));
        Assert.Equal(0.02f, vulcan.Float("Start_Width"));
        Assert.Equal(3, vulcan.Int("Num_Points"));
        Assert.Equal(-2, vulcan.Int("Life"));

        Assert.True(Level100ProjectileTrailHistory.UsesAuthoredTrail(
            Level100ProjectileKind.MechPulseBoltMedium));
        Assert.True(Level100ProjectileTrailHistory.UsesAuthoredTrail(
            Level100ProjectileKind.MechBullet));
        Assert.True(Level100ProjectileTrailHistory.UsesAuthoredTrail(
            Level100ProjectileKind.MechAirBullet));
        Assert.False(Level100ProjectileTrailHistory.UsesAuthoredTrail(
            Level100ProjectileKind.None));
        Assert.Equal(5, Level100ProjectileTrailHistory.AuthoredPointCount(
            Level100ProjectileKind.MechPulseBoltMedium));
        Assert.Equal(3, Level100ProjectileTrailHistory.AuthoredPointCount(
            Level100ProjectileKind.MechBullet));
        Assert.Equal(3, Level100ProjectileTrailHistory.AuthoredPointCount(
            Level100ProjectileKind.MechAirBullet));
        Assert.Equal(
            SimulationConstants.ProjectileLifetimeTicks,
            Level100ProjectileTrailHistory.AuthoredLifetimeTicks(
                Level100ProjectileKind.MechPulseBoltMedium));
        Assert.Equal(
            SimulationConstants.MechBulletLifetimeTicks,
            Level100ProjectileTrailHistory.AuthoredLifetimeTicks(
                Level100ProjectileKind.MechBullet));
        Assert.Equal(
            SimulationConstants.MechAirBulletLifetimeTicks,
            Level100ProjectileTrailHistory.AuthoredLifetimeTicks(
                Level100ProjectileKind.MechAirBullet));

        var history = new Level100ProjectileTrailHistory(
            pulse.Int("Num_Points"),
            SimulationConstants.ProjectileLifetimeTicks);
        var velocity = new Level100RenderVector3(1f, 0f, 0f);
        history.Advance(
            new Level100RenderVector3(1f, 0f, 0f),
            velocity,
            SimulationConstants.ProjectileLifetimeTicks - 1);
        // Skip four renderer-visible snapshots. The history must recover their
        // fixed-step positions instead of stretching one frame-dependent span.
        history.Advance(
            new Level100RenderVector3(6f, 0f, 0f),
            velocity,
            SimulationConstants.ProjectileLifetimeTicks - 6);

        Assert.Equal(
            [2f, 3f, 4f, 5f, 6f],
            history.Points.Select(point => point.X).ToArray());
        Level100RenderVector3[] rendered = history.WithRenderedHead(
            new Level100RenderVector3(5.5f, 0f, 0f));
        Assert.Equal(5, rendered.Length);
        Assert.Equal(5.5f, rendered[^1].X);
        Assert.Equal(6f, history.Points[^1].X);

        var vulcanHistory = new Level100ProjectileTrailHistory(
            vulcan.Int("Num_Points"),
            SimulationConstants.MechBulletLifetimeTicks);
        vulcanHistory.Advance(
            new Level100RenderVector3(1f, 0f, 0f),
            velocity,
            SimulationConstants.MechBulletLifetimeTicks - 1);
        vulcanHistory.Advance(
            new Level100RenderVector3(4f, 0f, 0f),
            velocity,
            SimulationConstants.MechBulletLifetimeTicks - 4);
        Assert.Equal(
            [2f, 3f, 4f],
            vulcanHistory.Points.Select(point => point.X).ToArray());

        string owner = File.ReadAllText(Locate(
            "rebuild/OnslaughtRebuild.Godot/Scenes/World/world_entities.gd"));
        Assert.Contains("PULSE_TRAIL_WIDTH_BITS: int = 0x3da3d70a", owner, StringComparison.Ordinal);
        Assert.Contains("VULCAN_TRAIL_WIDTH_BITS: int = 0x3ca3d70a", owner, StringComparison.Ordinal);
        Assert.Equal(0.08f, BitConverter.UInt32BitsToSingle(0x3da3d70a));
        Assert.Equal(0.02f, BitConverter.UInt32BitsToSingle(0x3ca3d70a));
        string update = RequireSection(owner, "func _update_projectiles(", "func _spawn_muzzle(");
        Assert.Contains("history.advance(position, _trail_velocity(item), item.remaining_ticks)", update, StringComparison.Ordinal);
        Assert.Contains("Interpolation.uses_authored_trail(item.kind)", update, StringComparison.Ordinal);
        Assert.Contains("Interpolation.authored_point_count(item.kind)", update, StringComparison.Ordinal);
        Assert.Contains("Interpolation.authored_lifetime_ticks(item.kind)", update, StringComparison.Ordinal);
        Assert.Contains("history.with_rendered_head(rendered.value.position)", update, StringComparison.Ordinal);
        Assert.Contains("_trails.erase(id)", update, StringComparison.Ordinal);
        Assert.Contains("_projectiles.erase(id)", update, StringComparison.Ordinal);
        Assert.DoesNotContain("item.remaining_ticks >", update, StringComparison.Ordinal);
        string pulseScene = File.ReadAllText(Locate("rebuild/OnslaughtRebuild.Godot/Scenes/World/PulseBolt.tscn"));
        string vulcanScene = File.ReadAllText(Locate("rebuild/OnslaughtRebuild.Godot/Scenes/World/VulcanBullet.tscn"));
        foreach (string layer in new[] { "PulseBoltSprite", "PulseBoltHalo", "PulseBoltEnergyTrail" })
        {
            Assert.Contains(layer, pulseScene, StringComparison.Ordinal);
            Assert.DoesNotContain(layer, vulcanScene, StringComparison.Ordinal);
        }
        Assert.Contains("ProjectileTrail", pulseScene, StringComparison.Ordinal);
        Assert.Contains("ProjectileTrail", vulcanScene, StringComparison.Ordinal);
        string trailUpdater = RequireSection(owner, "func _update_trail(", "func _result()");
        Assert.Contains("Mesh.PRIMITIVE_TRIANGLE_STRIP", trailUpdater, StringComparison.Ordinal);
        Assert.Contains("width * 0.5", trailUpdater, StringComparison.Ordinal);
        Assert.Contains("surface.add_vertex", trailUpdater, StringComparison.Ordinal);
        string world = File.ReadAllText(Locate("rebuild/OnslaughtRebuild.Godot/FirstFlightWorldView.cs"));
        string controller = File.ReadAllText(Locate("rebuild/OnslaughtRebuild.Godot/Scenes/World/world_presentation.gd"));
        Assert.Contains("WorldFrameFacts(previous, current, interpolationAlpha, frameDelta, failures)", world, StringComparison.Ordinal);
        Assert.Contains("_worldPresentation.Call(\"render_frame\", batch)", world, StringComparison.Ordinal);
        Assert.Contains("_aquila_stage.bind(previous, current, player_yaw, frame_delta, batch.alpha_bits, stage)", controller, StringComparison.Ordinal);
        Assert.Contains("_call_checked(_entities, \"render_frame\", [entity_batch.value, callback], \"entity presentation\")", controller, StringComparison.Ordinal);
        Assert.DoesNotContain("Level100ProjectileTrailHistory", world, StringComparison.Ordinal);
        Assert.DoesNotContain("Level100RenderInterpolation.Interpolate", world, StringComparison.Ordinal);

        string materializer = File.ReadAllText(Locate(
            "rebuild/tools/materialize_retail_assets.py"));
        Assert.Contains(
            "Level100/Textures/vulcan-bullet-trail.texture.aya",
            materializer,
            StringComparison.Ordinal);
        Assert.Contains(
            "Particle%Bullet.tga(0)R5G6B5.aya",
            materializer,
            StringComparison.Ordinal);
        Assert.Contains(
            "42da4484967f48958e71c9529435306c284fbbc36fc1f7a6ca2befc1eac2f01c",
            materializer,
            StringComparison.Ordinal);
    }

    /// <summary>
    /// Hole 2. Every shot the player fires has an authored muzzle flash.
    /// <c>default physics.dat</c> binds it at the weapon mode
    /// <c>Mech Pulse Cannon Charged</c> (record at file offset <c>0x0134EB</c>,
    /// round <c>Mech Pulse Bolt Medium</c> at <c>0x01352D</c>, particle name
    /// <c>Pulse Cannon Muzzle Flash</c> at <c>0x013550</c>, launch sound
    /// <c>BE Pulse Cannon Fire</c> at <c>0x013576</c>) - and that is the mode
    /// the Level 100 <c>Pulse Cannon Pod</c> weapon at <c>0x01746B</c> selects.
    ///
    /// <para>Note that it names the type-1 SPRITE, not the type-6 timeline
    /// <c>Pulse Cannon Muzzle Flash Effect</c>. The other pulse cannons in the
    /// same file (IS2, IS3, Carrier, Naval) name the timeline; the Battle
    /// Engine's does not.</para>
    /// </summary>
    [Fact]
    public void PulseCannonMuzzleFlashResolvesToOneAuthoredSprite()
    {
        ParticleSetFile set = ParticleSetFile.Parse(ReadMainSet());
        ParticleEffectPlan plan = ParticleEffectResolver.Resolve(
            set, "Pulse Cannon Muzzle Flash");

        Assert.Equal(ParticleDescriptorType.Sprite, plan.RootType);
        ParticleSpriteLayer flash = Assert.Single(plan.Layers);
        Assert.Empty(plan.Unimplemented);

        Assert.Equal("alparticle5.tga", flash.TextureName);
        Assert.Equal(0, flash.BlendMode);
        Assert.Equal(4, flash.AtlasColumns);
        Assert.Equal(4, flash.AtlasRows);
        Assert.Equal(1, flash.StartCell);
        Assert.Equal(15, flash.EndCell);
        Assert.Equal(ParticleAnimationMode.PlayOnce, flash.AnimationMode);
        Assert.Equal(1.4f, flash.AnimationCellsPerTurn);
        Assert.Equal(10, flash.LifeTurns);
        Assert.Equal(0.3f, flash.StartRadius);
        Assert.Equal(1.5f, flash.FinalRadius);
        Assert.True(flash.FadeColour);
        Assert.False(flash.RandomStartCell);
        Assert.Equal(1, flash.InstanceCount);

        ParticleColourRange cyan = flash.ColourRange!.Value;
        Assert.Equal("Cyan", cyan.Name);
        Assert.Equal((0.5f, 1f, 1f), cyan.Start);
        Assert.Equal((0.5f, 1f, 1f), cyan.End);
        Assert.False(cyan.UseTransition);

        string gameSource = File.ReadAllText(Locate(
            "rebuild/OnslaughtRebuild.Godot/FirstFlightGame.cs"));
        string frameEvents = RequireSection(
            gameSource,
            "private void ConsumeFrameEvents(FrameAdvanceResult result)",
            "private void RunFocusLossHandlerSmokeProbe()");
        Assert.Contains(
            "_world.ConsumeLevel100WeaponFireEvents(result.Level100WeaponFireEvents);",
            frameEvents,
            StringComparison.Ordinal);

        string worldSource = File.ReadAllText(Locate(
            "rebuild/OnslaughtRebuild.Godot/FirstFlightWorldView.cs"));
        string fireEvents = RequireSection(
            worldSource,
            "public void ConsumeLevel100WeaponFireEvents(",
            "private void BuildEnvironment()");
        Assert.Contains(
            "weapons.Add(item is null ? default(Variant) : (int)item.Weapon);",
            fireEvents,
            StringComparison.Ordinal);
        Assert.Contains(
            "_worldPresentation.Call(\"queue_weapon_events\", batch)",
            fireEvents,
            StringComparison.Ordinal);
        string controller = File.ReadAllText(Locate("rebuild/OnslaughtRebuild.Godot/Scenes/World/world_presentation.gd"));
        string queueEvents = RequireSection(controller, "func queue_weapon_events(", "func host_snapshot()");
        Assert.Equal(1, (int)Level100PlayerWeapon.PulseCannonPod);
        Assert.Contains("PULSE_CANNON_POD: int = 1", controller, StringComparison.Ordinal);
        Assert.Contains("if weapon == PULSE_CANNON_POD:", queueEvents, StringComparison.Ordinal);
        Assert.Contains("_pending_muzzles = _wrap_i32(_pending_muzzles + 1)", queueEvents, StringComparison.Ordinal);
        Assert.Contains("\"pending_muzzles\": _pending_muzzles", controller, StringComparison.Ordinal);
        Assert.Contains("_pending_muzzles = rendered.pending_muzzles", controller, StringComparison.Ordinal);
        Assert.DoesNotContain(
            "MechTwinVulcanCannon",
            fireEvents,
            StringComparison.Ordinal);
        Assert.DoesNotContain(
            "MechVulcanCannon",
            fireEvents,
            StringComparison.Ordinal);

        string owner = File.ReadAllText(Locate("rebuild/OnslaughtRebuild.Godot/Scenes/World/world_entities.gd"));
        string projectileUpdate = RequireSection(owner, "func _update_projectiles(", "func _spawn_muzzle(");
        int newProjectileBranch = projectileUpdate.IndexOf("if not _projectiles.has(item.id):", StringComparison.Ordinal);
        int muzzleFlashSpawn = projectileUpdate.IndexOf("_spawn_muzzle(_launch_position(item), item.id)", StringComparison.Ordinal);
        int priorStateJoin = projectileUpdate.IndexOf("Interpolation.interpolate_projectile(previous.get(item.id)", StringComparison.Ordinal);
        Assert.True(newProjectileBranch >= 0);
        Assert.InRange(muzzleFlashSpawn, newProjectileBranch + 1, priorStateJoin - 1);
        Assert.Contains("if item.kind == 1 and _pending_muzzles > 0:", projectileUpdate, StringComparison.Ordinal);
        Assert.Contains("_pending_muzzles = _i32(_pending_muzzles - 1)", projectileUpdate, StringComparison.Ordinal);
        Assert.Contains("_pending_muzzles = 0", projectileUpdate, StringComparison.Ordinal);
        string presentation = RequireSection(worldSource, "private void BuildPulseCannonPresentation(", "private void SpawnPulseImpact(");
        string scene = File.ReadAllText(Locate("rebuild/OnslaughtRebuild.Godot/Scenes/World/PulseMuzzleFlash.tscn"));
        Assert.DoesNotContain("particle-alparticle5-additive.texture.aya", presentation, StringComparison.Ordinal);
        Assert.Contains("particle-alparticle5-additive.texture.aya", scene, StringComparison.Ordinal);
        Assert.Contains("retail_texture_page.gd", scene, StringComparison.Ordinal);
        Assert.Contains("_admit_texture_pages()", owner, StringComparison.Ordinal);
        Assert.Contains("wait_time = 0.5", scene, StringComparison.Ordinal);
        Assert.Contains("one_shot = true", scene, StringComparison.Ordinal);
        Assert.Contains("size = Vector2(0.6, 0.6)", scene, StringComparison.Ordinal);
        Assert.Contains("albedo_color = Color(0.5, 1, 1, 1)", scene, StringComparison.Ordinal);
        Assert.Contains("uv1_scale = Vector3(0.25, 0.25, 1)", scene, StringComparison.Ordinal);
        string animation = File.ReadAllText(Locate("rebuild/OnslaughtRebuild.Godot/Scenes/World/pulse_muzzle_flash.gd"));
        Assert.Contains("START_CELL: int = 1", animation, StringComparison.Ordinal);
        Assert.Contains("END_CELL: int = 15", animation, StringComparison.Ordinal);
        Assert.Contains("CELLS_PER_TURN: float = 1.4", animation, StringComparison.Ordinal);
        Assert.Contains("TICKS_PER_SECOND: int = 20", animation, StringComparison.Ordinal);
        Assert.Contains("1.0 / (CELLS_PER_TURN * TICKS_PER_SECOND)", animation, StringComparison.Ordinal);
        Assert.Contains("Vector3.ONE * 5.0, 0.5", animation, StringComparison.Ordinal);
        Assert.Contains("Engine.is_editor_hint()", animation, StringComparison.Ordinal);
        string launchPosition = RequireSection(owner, "static func _launch_position(", "static func _trail_velocity(");
        Assert.Contains("PULSE_LIFETIME - item.remaining_ticks", launchPosition, StringComparison.Ordinal);
        Assert.Contains("item.velocity_x * elapsed", launchPosition, StringComparison.Ordinal);
        Assert.Contains("item.vertical_velocity * elapsed", launchPosition, StringComparison.Ordinal);
        Assert.Contains("item.velocity_z * elapsed", launchPosition, StringComparison.Ordinal);

        string materializer = File.ReadAllText(Locate(
            "rebuild/tools/materialize_retail_assets.py"));
        Assert.Contains(
            "Particle%alparticle5.tga(0)R5G6B5.aya\", \"5004b8c6a688b82605f870e60d4ed32a32203b4371f1aec72155fef1619a5fa0\"",
            materializer,
            StringComparison.Ordinal);
    }

    /// <summary>
    /// <b>A measured retail defect, pinned so nobody "fixes" it by inventing a
    /// number.</b> <c>Pulse Cannon Muzzle Flash</c> authors cells 1..15 of
    /// <c>alparticle5.tga</c>, but only cells 0..8 of that 128x128 sheet are
    /// inked: cells 9-15 measure mean luminance exactly 0.000. Five of the six
    /// other sprites that use the sheet author <c>End_Frame 8</c>, which is its
    /// real last inked cell.
    ///
    /// <para>So the released flash shows art for cells 1..8 - 7 cells at 1.4
    /// cells per turn, i.e. 5 of its 10 turns, 0.25 s - and then draws nothing
    /// for the rest of its life. That is what retail does. This test asserts
    /// the arithmetic so the reconstruction reproduces the released duration
    /// instead of stretching the animation to fill the sprite's life.</para>
    /// </summary>
    [Fact]
    public void PulseCannonMuzzleFlashRunsOffTheInkedEndOfItsOwnAtlas()
    {
        ParticleSetFile set = ParticleSetFile.Parse(ReadMainSet());
        ParticleSpriteLayer flash = Assert.Single(
            ParticleEffectResolver.Resolve(set, "Pulse Cannon Muzzle Flash").Layers);

        const int lastInkedCell = 8;
        float turnsToLastInkedCell =
            (lastInkedCell - flash.StartCell) / flash.AnimationCellsPerTurn;
        Assert.Equal(5f, turnsToLastInkedCell, 4);
        Assert.Equal(
            0.25f,
            turnsToLastInkedCell / ParticleEffectResolver.GameTurnsPerSecond,
            4);
        Assert.True(flash.EndCell > lastInkedCell);

        // The five other alparticle5 sprites that stop at the real last inked
        // cell, which is why 8 is a measurement of the sheet and not a guess.
        int stopAtEight = 0;
        foreach (ParticleDescriptor sprite in set.Descriptors)
        {
            if (sprite.TypeId == 1 &&
                sprite.Raw("Texture")?.EndsWith("alparticle5.tga", StringComparison.OrdinalIgnoreCase) == true &&
                sprite.Int("End_Frame") == lastInkedCell)
            {
                stopAtEight++;
            }
        }

        Assert.Equal(5, stopAtEight);
    }

    /// <summary>
    /// The three additive textures the materializer newly retains are exactly
    /// the <c>Blend_Mode 0</c> textures the two closed holes ask for, and no
    /// more. If a later change makes an effect reach for a fourth, this fails
    /// rather than the renderer throwing at runtime.
    /// </summary>
    [Fact]
    public void ClosedHolesAskForOnlyTheRetainedTextures()
    {
        ParticleSetFile set = ParticleSetFile.Parse(ReadMainSet());
        SortedSet<string> wanted = new(StringComparer.Ordinal);
        foreach (string effect in
            (string[])["Muspell Building Explosion Effect", "Pulse Cannon Muzzle Flash"])
        {
            foreach (ParticleSpriteLayer layer in
                ParticleEffectResolver.Resolve(set, effect).Layers)
            {
                wanted.Add(
                    layer.TextureName + "#" +
                    layer.BlendMode.ToString(CultureInfo.InvariantCulture));
            }
        }

        Assert.Equal(
            new[]
            {
                "alparticle4.tga#1",
                "alparticle5.tga#0",
                "fireball.tga#0",
                "sun2.tga#0",
            },
            wanted);
    }

    private static ParticleSpriteLayer Single(ParticleEffectPlan plan, string descriptorName)
    {
        ParticleSpriteLayer? found = null;
        foreach (ParticleSpriteLayer layer in plan.Layers)
        {
            if (!string.Equals(layer.DescriptorName, descriptorName, StringComparison.Ordinal))
            {
                continue;
            }

            Assert.Null(found);
            found = layer;
        }

        Assert.NotNull(found);
        return found!;
    }

    private static byte[] ReadMainSet() => File.ReadAllBytes(Locate(MainSetRelativePath));

    private static string Suffix(string value)
    {
        int space = value.IndexOf(' ');
        return space < 0 ? "" : value[(space + 1)..];
    }

    private static string RequireSection(string source, string start, string end)
    {
        int startIndex = source.IndexOf(start, StringComparison.Ordinal);
        Assert.True(startIndex >= 0, $"Source section start '{start}' is missing.");
        int endIndex = source.IndexOf(end, startIndex + start.Length, StringComparison.Ordinal);
        Assert.True(endIndex > startIndex, $"Source section end '{end}' is missing.");
        return source[startIndex..endIndex];
    }

    private static void AssertSourceOrder(string source, params string[] statements)
    {
        int offset = 0;
        foreach (string statement in statements)
        {
            int index = source.IndexOf(statement, offset, StringComparison.Ordinal);
            Assert.True(index >= 0, $"Source operation '{statement}' is missing or out of order.");
            offset = index + statement.Length;
        }
    }

    private static string Locate(string repositoryRelativePath)
    {
        DirectoryInfo? directory = new(AppContext.BaseDirectory);
        while (directory is not null)
        {
            string candidate = Path.Combine(
                directory.FullName, repositoryRelativePath.Replace('/', Path.DirectorySeparatorChar));
            if (File.Exists(candidate))
            {
                return candidate;
            }

            directory = directory.Parent;
        }

        throw new FileNotFoundException(
            $"Could not locate '{repositoryRelativePath}'. Run 'npm run prepare:rebuild-assets'.");
    }
}
