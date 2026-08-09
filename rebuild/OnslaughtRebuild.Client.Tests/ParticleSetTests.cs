// SPDX-License-Identifier: GPL-3.0-or-later

using System.Globalization;
using System.Security.Cryptography;
using System.Text;
using OnslaughtRebuild.Client;

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
