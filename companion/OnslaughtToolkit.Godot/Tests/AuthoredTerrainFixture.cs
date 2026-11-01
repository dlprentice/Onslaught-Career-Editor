// SPDX-License-Identifier: GPL-3.0-only
using System.IO.Compression;
using System.Text;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Adds only authored terrain data to an authored level archive.</summary>
internal static class AuthoredTerrainFixture
{
    internal static void AddDraftSources(string gameRoot)
    {
        string folder = Path.Combine(gameRoot, "data", "MissionScripts", "level100");
        Directory.CreateDirectory(folder);
        foreach (MissionScript script in WorldBody.Read(LevelTests.Body("authored-v50")).Scripts)
            File.WriteAllText(Path.Combine(folder, script.Name + ".msl"), "// Authored source-draft fixture.\n");
    }

    internal static byte[] WithAuthoredTerrain(byte[] archive)
    {
        byte[] terrain = LevelTests.Unpack(LevelVectors.Terrain.Eres);
        using MemoryStream chunk = new();
        using (BinaryWriter writer = new(chunk, Encoding.ASCII, leaveOpen: true))
        {
            writer.Write(Encoding.ASCII.GetBytes("ERES"));
            writer.Write((uint)terrain.Length);
            writer.Write(terrain);
        }
        byte[] input = chunk.ToArray();
        using MemoryStream joined = new();
        using (BinaryWriter writer = new(joined, Encoding.ASCII, leaveOpen: true))
        {
            int part = Math.Min(LevelArchive.PackBufferBytes / 2, LevelArchive.MaxMemberInflatedBytes / 2);
            for (int at = 0; at < input.Length; at += part)
            {
                using MemoryStream compressed = new();
                using (ZLibStream zlib = new(compressed, CompressionLevel.Optimal, leaveOpen: true))
                    zlib.Write(input, at, Math.Min(part, input.Length - at));
                byte[] member = compressed.ToArray();
                if (member.Length > LevelArchive.PackBufferBytes) throw new InvalidDataException("The authored terrain fixture exceeds the member limit.");
                writer.Write((uint)member.Length);
                writer.Write(member);
            }
            writer.Write(archive);
        }
        return joined.ToArray();
    }
}
