// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;

namespace OnslaughtRebuild.Core.Tests;

/// <summary>
/// Parity tests for world-110 admission: the second career node's compiled
/// script objects and heightfield, measured from the pinned
/// <c>data/resources/110_res_PC.aya</c> (SHA-256
/// <c>4e041c75…3c2b</c>) on 2026-08-22 and embedded under the Level110
/// resource prefix. Nothing here reuses a Level 100 payload; every hash pin
/// is world 110's own.
/// </summary>
public sealed class RetailWorld110AdmissionTests
{
    private const int World110 = 110;

    [Fact]
    public void AllThirteenScriptObjects_AdmitWithTheirPinnedIdentities()
    {
        string[] expectedNames =
        [
            "beacon", "Lander", "Lander2", "Lander3", "LevelScript",
            "MuspellFighter", "MuspellFighter1", "MuspellFighter2",
            "Scout", "Setup", "Victory", "VitalBuilding", "Weather",
        ];

        Assert.Equal(13, expectedNames.Length);
        Assert.Equal(
            expectedNames.OrderBy(name => name, StringComparer.Ordinal).ToArray(),
            Level100MissionProgram.ProgramNamesFor(World110)
                .OrderBy(name => name, StringComparer.Ordinal).ToArray());
        foreach (string name in expectedNames)
        {
            Level100MissionProgram program = Level100MissionProgram.LoadEmbedded(World110, name);

            Assert.Equal(name, program.Name);
            Assert.NotEmpty(program.Instructions);
        }
    }

    [Fact]
    public void LevelScript_StructureMatchesTheMeasuredWorld110Pin()
    {
        Level100MissionProgram levelScript =
            Level100MissionProgram.LoadEmbedded(World110, "LevelScript");

        // Measured on 2026-08-22 from the pinned payload.
        Assert.Equal(181, levelScript.Instructions.Count);
        Assert.Equal(92, levelScript.Symbols.Count);
        Assert.Equal(11, levelScript.BuiltInEventInstructionPointers[0]);
        Assert.True(levelScript.BuiltInEventInstructionPointers
            .Skip(1).All(pointer => pointer == -1));
        Assert.True(levelScript.RunInitializer);
        Assert.Equal(5, levelScript.NamedEventInstructionPointers.Count);

        // The five released named events and their instruction pointers.
        Assert.Equal(100, levelScript.NamedEventInstructionPointers["Enemy Engaged"]);
        Assert.Equal(134, levelScript.NamedEventInstructionPointers["Vital Building Destroyed"]);
        Assert.Equal(145, levelScript.NamedEventInstructionPointers["Lander Escaped"]);
        Assert.Equal(159, levelScript.NamedEventInstructionPointers["Lander Destroyed"]);
        Assert.Equal(170, levelScript.NamedEventInstructionPointers["Lander Withdraws"]);
    }

    /// <summary>
    /// World 100 admission still works through the unchanged single-argument
    /// overloads — the L100 runtime call sites are untouched by the
    /// generalization.
    /// </summary>
    [Fact]
    public void Level100CallSites_StillLoadThroughSingleArgumentOverloads()
    {
        foreach (string name in Level100MissionProgram.ProgramNames)
        {
            Assert.Equal(name, Level100MissionProgram.LoadEmbedded(name).Name);
        }

        Assert.Same(
            Level100Terrain.Instance,
            Level100Terrain.Instance);
        Assert.NotSame(Level100Terrain.Instance, Level100Terrain.World110);
    }

    [Fact]
    public void World110Heightfield_IsItsOwnHashPinnedEnvelope()
    {
        // The measured HFLD envelope pin from the materializer table.
        Assert.Equal("fd4d076a2926fbc473b7d364703bdbc0c8a0f7a638b0ab71b6f319374da033c2",
            Convert.ToHexString(
                System.Security.Cryptography.SHA256.HashData(World110Payload()))
                .ToLowerInvariant());
    }

    [Fact]
    public void World110AndLevel100Terrains_AreDistinctMeasuredWorlds()
    {
        // Both statics load lazily at first touch; both must admit without
        // throwing. Each records the exact envelope it was loaded from, and
        // the two recorded payloads are the two distinct measured worlds:
        // the released HFLD envelopes share the format law (same declared
        // size, same 137x148 CHFD grid, same scales) but differ in height
        // data from the first sample word — world 110 is its own world, not
        // a re-pinned Level 100 envelope.
        Assert.NotNull(Level100Terrain.World110);
        Assert.NotNull(Level100Terrain.Instance);
        Assert.NotSame(Level100Terrain.Instance, Level100Terrain.World110);
        Assert.Equal(
            Level100Terrain.World110SourceSha256,
            Level100Terrain.World110.PayloadSha256);
        Assert.Equal(
            Level100Terrain.SourceSha256,
            Level100Terrain.Instance.PayloadSha256);
        Assert.NotEqual(
            Level100Terrain.SourceSha256,
            Level100Terrain.World110SourceSha256);
    }

    [Fact]
    public void UnknownWorlds_AndUnknownScriptsAreRejected()
    {
        // World 200 was admitted by the generalization slice; the next
        // unmeasured world stays rejected.
        Assert.Throws<ArgumentOutOfRangeException>(
            () => Level100MissionProgram.LoadEmbedded(210, "LevelScript"));
        Assert.Throws<ArgumentOutOfRangeException>(
            () => Level100MissionProgram.LoadEmbedded(110, "Nonexistent"));
    }

    /// <summary>
    /// Reads the embedded world-110 HFLD envelope back out of the test
    /// assembly's Core dependency so the pin is checked against the exact
    /// bytes the simulation would consume.
    /// </summary>
    private static byte[] World110Payload()
    {
        System.Reflection.Assembly assembly = typeof(Level100Terrain).Assembly;
        using System.IO.Stream stream = assembly.GetManifestResourceStream(
            "OnslaughtRebuild.Core.Assets.Level110.level110-heightfield.hfld.bin")
            ?? throw new InvalidOperationException(
                "The world-110 heightfield resource is missing.");
        using var memory = new MemoryStream();
        stream.CopyTo(memory);
        return memory.ToArray();
    }
}
