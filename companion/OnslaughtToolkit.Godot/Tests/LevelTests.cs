// SPDX-License-Identifier: GPL-3.0-only
using System.IO.Compression;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// The level data layer against the Toolkit's Python reference on authored data (no game bytes): every vector
/// tools/level_editor_vectors.py writes into <c>LevelVectors.g.cs</c>. A body must read into the same fields the reference
/// reads (the reference dump, line for line), write back to the same bytes, refuse what the reference refuses, and write
/// the bytes the reference writes after the same edit; an archive must give the level numbers and bodies the reference
/// finds in it. Nothing here touches Godot.
/// </summary>
internal static class LevelTests
{
    private static readonly Dictionary<string, byte[]> Bodies = LevelVectors.Valid.ToDictionary(v => v.Name, v => Unpack(v.Body));

    /// <summary>The bytes of a valid vector by name.</summary>
    internal static byte[] Body(string name) => Bodies[name];

    internal static void Run(string outputDirectory, Checks check)
    {
        check.Suite("levels");
        Stage(check, "the valid vectors", () => Valid(check));
        Stage(check, "the refused vectors", () => Refused(check));
        Stage(check, "the truncations", () => Truncations(check));
        Stage(check, "the edits", () => Edits(check));
        Stage(check, "the write refusals", () => WriteRefusals(check));
        Stage(check, "the object kinds", () => Kinds(check));
        Stage(check, "the archive vectors", () => Archives(check));
        Stage(check, "the archive folder", () => ArchiveFolder(Path.Combine(outputDirectory, "level-archives"), check));
    }

    /// <summary>One stage failing unexpectedly is a failed check, not the end of the others.</summary>
    private static void Stage(Checks check, string name, Action stage)
    {
        try
        {
            stage();
        }
        catch (Exception error)
        {
            check.Fail($"{name} stopped with {error.GetType().Name}: {error.Message}");
        }
    }

    /// <summary>The bytes of a vector: base64 (any whitespace), then one zlib stream; empty text is no bytes.</summary>
    internal static byte[] Unpack(string packed)
    {
        string text = string.Concat(packed.Where(c => !char.IsWhiteSpace(c)));
        if (text.Length == 0) return [];
        using MemoryStream compressed = new(Convert.FromBase64String(text));
        using ZLibStream zlib = new(compressed, CompressionMode.Decompress);
        using MemoryStream output = new();
        zlib.CopyTo(output);
        return output.ToArray();
    }

    private static string Sha256(byte[] data) => Convert.ToHexStringLower(SHA256.HashData(data));

    private static void Valid(Checks check)
    {
        check.That(LevelVectors.Valid.Length >= 25, "the vector file holds the authored bodies");
        foreach (LevelVectors.WorldVector vector in LevelVectors.Valid)
        {
            byte[] body = Bodies[vector.Name];
            WorldBody model;
            try
            {
                model = WorldBody.Read(body);
            }
            catch (Exception error)
            {
                check.Fail($"{vector.Name}: the reader refused a body the reference reads: {error.Message}");
                continue;
            }
            List<string> lines = WorldDump.Lines(model);
            check.That(lines.Count == vector.Lines, $"{vector.Name}: {lines.Count} fields read, the reference reads {vector.Lines}");
            check.That(WorldDump.Hash(lines) == vector.DumpSha256, $"{vector.Name}: the dump of the fields read is not the reference's");
            if (vector.Dump.Length > 0)
            {
                string[] expected = Encoding.ASCII.GetString(Unpack(vector.Dump)).Split('\n');
                HashSet<string> wanted = [.. expected], got = [.. lines];
                string missing = string.Join(" | ", wanted.Except(got).Take(3)), extra = string.Join(" | ", got.Except(wanted).Take(3));
                check.That(missing.Length == 0 && extra.Length == 0, $"{vector.Name}: the reference reads [{missing}] and the reader reads [{extra}]");
            }
            byte[] again = model.Write();
            check.That(again.AsSpan().SequenceEqual(body), $"{vector.Name}: written again it differs {Difference(body, again)}");
            try
            {
                byte[] second = WorldBody.Read(again).Write();
                check.That(second.AsSpan().SequenceEqual(body), $"{vector.Name}: a second round trip differs");
            }
            catch (Exception error)
            {
                check.Fail($"{vector.Name}: the bytes written could not be read again: {error.Message}");
            }
        }
    }

    private static string Difference(byte[] expected, byte[] actual)
    {
        int at = 0;
        while (at < expected.Length && at < actual.Length && expected[at] == actual[at]) at++;
        return $"(first at byte {at} of {expected.Length} and {actual.Length})";
    }

    private static void Refused(Checks check)
    {
        check.That(LevelVectors.Refused.Length >= 19, "the vector file holds the refused bodies");
        foreach (LevelVectors.RefusedVector vector in LevelVectors.Refused)
            Refuses(check, vector.Name + " (" + vector.Why + ")", () => WorldBody.Read(Unpack(vector.Body)));
    }

    /// <summary>The call must fail with <see cref="InvalidDataException"/>, not another exception and not a result.</summary>
    private static void Refuses(Checks check, string what, Action action)
    {
        try
        {
            action();
            check.Fail($"{what}: accepted");
        }
        catch (InvalidDataException)
        {
            check.That(true, what);
        }
        catch (Exception error)
        {
            check.Fail($"{what}: refused with {error.GetType().Name} instead of InvalidDataException: {error.Message}");
        }
    }

    /// <summary>A proper prefix of a body is never a body: every one must be refused.</summary>
    private static void Truncations(Checks check)
    {
        foreach ((string name, int step) in new[] { ("authored-v50", 1), ("authored-v43", 1), ("kinds-v46", 1), ("kinds-v43", 1), ("scripts-rich", 53), ("authored-v47", 61) })
        {
            byte[] body = Bodies[name];
            int accepted = 0, otherExceptions = 0;
            for (int length = 0; length < body.Length; length += length < 400 || length > body.Length - 400 ? 1 : step)
            {
                try
                {
                    WorldBody.Read(body.AsSpan(0, length));
                    accepted++;
                }
                catch (InvalidDataException)
                {
                }
                catch (Exception)
                {
                    otherExceptions++;
                }
            }
            check.That(accepted == 0 && otherExceptions == 0, $"{name}: prefixes of the body are refused ({accepted} accepted, {otherExceptions} refused with another exception)");
        }
    }

    private static void Edits(Checks check)
    {
        check.That(LevelVectors.Edits.Length >= 8, "the vector file holds the edits");
        foreach (LevelVectors.EditVector edit in LevelVectors.Edits)
        {
            WorldBody model = WorldBody.Read(Bodies[edit.From]);
            foreach (LevelVectors.EditStep step in edit.Steps)
            {
                ObjectInit init = model.Things[step.Thing].Init;
                switch (step.Op)
                {
                    case "move": init.Position = new Vector3(step.X, step.Y, step.Z); break;
                    case "rotate": init.Orientation = new Vector3(step.X, step.Y, step.Z); break;
                    case "rename": init.Name = step.Text; break;
                    default: check.Fail($"{edit.Name}: unknown step {step.Op}"); break;
                }
            }
            byte[] expected = Unpack(edit.Body), written = model.Write();
            check.That(written.AsSpan().SequenceEqual(expected), $"{edit.Name}: the edited body is not the reference's {Difference(expected, written)}");
        }
        // A move changes the twelve bytes of the position and nothing else.
        WorldBody moved = WorldBody.Read(Bodies["authored-v50"]);
        moved.Things[0].Init.Position = new Vector3(12.5f, -40f, 3f);
        byte[] before = Bodies["authored-v50"], after = moved.Write();
        int[] changed = [.. Enumerable.Range(0, before.Length).Where(i => before[i] != after[i])];
        check.That(after.Length == before.Length && changed.Length > 0 && changed.Max() - changed.Min() < 12, "a move changes only the thing's position bytes");
    }

    private static WorldBody Authored() => WorldBody.Read(Bodies["authored-v50"]);

    private static void WriteRefusals(Checks check)
    {
        void Case(string what, Action<WorldBody> change, string vector = "authored-v50")
        {
            WorldBody model = WorldBody.Read(Bodies[vector]);
            change(model);
            Refuses(check, "writing " + what, () => model.Write());
        }

        Case("a version below 43", m => m.Version = 42);
        Case("a version above 50", m => m.Version = 51);
        Case("more than 1000 things", m => { while (m.Things.Count < 1001) m.Things.Add(m.Things[0]); });
        Case("a defined thing without its definition", m => m.Things[0].Definition = null);
        Case("an object id the loader does not read", m => m.Things[0].ObjectId = 99);
        Case("a definition longer than a signed length byte holds", m => m.Things[0].Definition = new string('d', 128));
        Case("a named mesh longer than an unsigned length byte holds", m => m.NamedMeshes.Add(new string('m', 256)));
        Case("a thing name over 255 characters", m => m.Things[0].Init.Name = new string('n', 256));
        Case("a thing name holding a NUL", m => m.Things[0].Init.Name = "a\0b");
        Case("a character outside Latin-1", m => m.Things[0].Init.Name = "Ā");
        Case("a configuration name outside Latin-1", m => m.Header.BattleEngineConfigurations.Add("€"));
        Case("event entry points of the wrong number", m => m.Scripts[0].Code.EventPcs = new int[12]);
        Case("a script trailer of the wrong size", m => m.Scripts[0].Trailer = new byte[9]);
        Case("a script symbol holding the wrong kind of value", m => m.Scripts[0].Code.Symbols[0].Value = new ScriptInt(1));
        Case("a script symbol with an unknown data type", m => { m.Scripts[0].Code.Symbols[0].DataType = 9; m.Scripts[0].Code.Symbols[0].Value = new ScriptInt(1); });
        Case("a script symbol of a kind with no value", m => m.Scripts[0].Code.Symbols[0].Value = null);
        Case("two occupancy grids", m => m.OccupancyGrids!.RemoveAt(2));
        Case("an occupancy grid of the wrong size", m => m.OccupancyGrids![0] = new OccupancyGrid { Version = 1, Data = new byte[10] });
        Case("missing occupancy grids", m => m.OccupancyGrids = null);
        Case("an influence map whose nodes do not match its bytes", m => m.InfluenceMap.Nodes = 1);
        Case("an influence map whose links do not match its bytes", m => m.InfluenceMap.Links = 1);
        Case("an influence map of a version the loader refuses", m => m.InfluenceMap.Version = 2);
        Case("a missing level start time", m => m.LevelStartTime = null);
        Case("missing header words", m => m.Header.V2Words = null);
        Case("header words of the wrong number", m => m.Header.V2Words = [1, 2]);
        Case("a missing attach-scripts word", m => m.Things[0].Init.AttachScriptsToUnits = null);
        Case("more tree groups than a signed 16-bit count holds", m => { while (m.TreeGroups.Count <= short.MaxValue) m.TreeGroups.Add(new TreeGroup()); });
        Case("missing legacy timings", m => m.LegacyTimings = null, "authored-v46");
        Case("missing legacy grid words", m => m.LegacyGridWords = null, "authored-v48");
        Case("a spawner without its fields", m => m.Things.First(t => t.ObjectId == 19).Init.Spawner = null, "kinds-v50");
        Case("a spawner without its spawn script", m => m.Things.First(t => t.ObjectId == 19).Init.Spawner!.SpawnerSpawnScript = null, "kinds-v50");
        Case("a squad without its fields", m => m.Things.First(t => t.ObjectId == ObjectKinds.Squad).Init.Squad = null, "kinds-v50");
        Case("a cutscene without its fields", m => m.Things.First(t => t.ObjectId == 26).Init.Cutscene = null, "kinds-v50");
        Case("a start without its fields", m => m.Things.First(t => t.ObjectId == 15).Init.Start = null, "kinds-v50");
        Case("a tree without its fields", m => m.Things.First(t => t.ObjectId == 7).Init.Tree = null, "kinds-v50");
        Case("a sphere trigger without its fields", m => m.Things.First(t => t.ObjectId == 36).Init.SphereTrigger = null, "kinds-v50");

        // What the format can hold at its limits is written and read back.
        WorldBody limits = Authored();
        limits.Things[0].Definition = new string('d', 127);
        limits.Things[0].Init.Script = new string('s', 255);
        limits.NamedMeshes.Add(new string('m', 255));
        limits.Header.BattleEngineConfigurations.Add("");
        byte[] written = limits.Write();
        WorldBody read = WorldBody.Read(written);
        check.That(read.Write().AsSpan().SequenceEqual(written) && read.Things[0].Definition!.Length == 127 && read.Things[0].Init.Script.Length == 255,
            "the longest strings the length fields hold are written and read back");
    }

    /// <summary>The loader's object-id table: the names, the classes and the ids it refuses.</summary>
    private static void Kinds(Checks check)
    {
        check.That(ObjectKinds.NameOf(8) == "unit" && ObjectKinds.NameOf(18) == "waypoint" && ObjectKinds.NameOf(36) == "sphere-trigger", "object ids have the reference's kind names");
        check.That(ObjectKinds.NameOf(99) == "oid-99" && ObjectKinds.NameOf(33) == "wall", "an unnamed id is oid-N and the wall is named though it is not read");
        check.That(ObjectKinds.IsDefined(8) && ObjectKinds.IsDefined(28) && ObjectKinds.IsDefined(39) && !ObjectKinds.IsDefined(18) && !ObjectKinds.IsDefined(15), "the defined kinds are unit, building, squad, feature and hazard");
        check.That(ObjectKinds.ClassOf(19) == ObjectClass.Spawner && ObjectKinds.ClassOf(28) == ObjectClass.Squad && ObjectKinds.ClassOf(15) == ObjectClass.Start &&
                   ObjectKinds.ClassOf(41) == ObjectClass.Start && ObjectKinds.ClassOf(8) == ObjectClass.Base && ObjectKinds.ClassOf(18) == ObjectClass.Base, "object ids have the reference's record layouts");
        foreach (int id in new[] { 0, 1, 2, 33, 99, -1 })
            Refuses(check, $"object id {id} has no record layout", () => ObjectKinds.ClassOf(id));
    }

    private static void Archives(Checks check)
    {
        check.That(LevelVectors.Archives.Length >= 10 && LevelVectors.RefusedArchives.Length >= 22, "the vector file holds the archives");
        foreach (LevelVectors.ArchiveVector vector in LevelVectors.Archives)
        {
            try
            {
                LevelWorlds worlds = LevelArchive.Read(Unpack(vector.File));
                check.That(worlds.BaseLevel == vector.BaseLevel && worlds.RealLevel == vector.RealLevel, $"{vector.Name}: levels {worlds.BaseLevel} and {worlds.RealLevel}, the reference finds {vector.BaseLevel} and {vector.RealLevel}");
                check.That((worlds.BaseBody is null ? null : Sha256(worlds.BaseBody)) == vector.BaseSha256, $"{vector.Name}: the base world is not the reference's");
                check.That((worlds.RealBody is null ? null : Sha256(worlds.RealBody)) == vector.RealSha256, $"{vector.Name}: the level's own world is not the reference's");
                if (worlds.RealBody is not null) check.That(WorldBody.Read(worlds.RealBody).Write().AsSpan().SequenceEqual(worlds.RealBody), $"{vector.Name}: the level's own world round-trips");
            }
            catch (Exception error)
            {
                check.Fail($"{vector.Name}: the reader refused an archive the reference reads: {error.Message}");
            }
        }
        foreach (LevelVectors.RefusedArchive vector in LevelVectors.RefusedArchives)
            Refuses(check, vector.Name + " (" + vector.Why + ")", () => LevelArchive.Read(Unpack(vector.File)));
        // Each of these is a valid archive but for its one member, so it is refused for that member and for nothing the chunks hold.
        foreach ((string name, string reason) in new[]
                 {
                     ("member-trailing-data", "data after it"), ("member-adler-repeated", "data after it"), ("member-adler-after-gap", "data after it"),
                     ("member-adler-after-junk", "data after it"), ("member-cut-short-before-adler", "truncated zlib stream"),
                     ("member-truncated", "truncated zlib stream"), ("member-over-1mib", "limit"), ("member-1mib-plus-one", "limit"), ("member-pack-buffer-plus-one", "implausible"), ("member-needs-dictionary", "invalid zlib data"),
                 })
        {
            LevelVectors.RefusedArchive vector = LevelVectors.RefusedArchives.First(v => v.Name == name);
            try
            {
                LevelArchive.Read(Unpack(vector.File));
                check.Fail($"{name}: accepted");
            }
            catch (InvalidDataException error)
            {
                check.That(error.Message.Contains(reason, StringComparison.Ordinal), $"{name}: refused for \"{error.Message}\", not for \"{reason}\"");
            }
        }
        // A stream that asks for a preset dictionary is refused with what the stream's reader said and the exception behind it (ZLibException is internal to the BCL).
        try
        {
            LevelArchive.Read(Unpack(LevelVectors.RefusedArchives.First(v => v.Name == "member-needs-dictionary").File));
            check.Fail("member-needs-dictionary: accepted");
        }
        catch (InvalidDataException error)
        {
            check.That(error.InnerException?.GetType().Name == "ZLibException" && error.Message.Contains("unexpected error code", StringComparison.Ordinal),
                $"member-needs-dictionary: refused with the zlib reader's own exception and message kept: {error.InnerException?.GetType().Name}, \"{error.Message}\"");
        }
        check.That(LevelWorlds.WorldFileName(7) == "data/worlds/world007.wrd" && LevelWorlds.WorldFileName(100) == "data/worlds/world100.wrd", "a level's loose world file is world%03d.wrd");
        ArchiveLimits(check);
    }

    private static void ArchiveLimits(Checks check)
    {
        check.That(LevelArchive.MaxFileBytes == LevelVectors.ReferenceLimits.MaxFileBytes && LevelArchive.MaxInflatedBytes == LevelVectors.ReferenceLimits.MaxInflatedBytes &&
                   LevelArchive.MaxMembers == LevelVectors.ReferenceLimits.MaxMembers && LevelArchive.PackBufferBytes == LevelVectors.ReferenceLimits.PackBufferBytes &&
                   LevelArchive.MaxMemberInflatedBytes == LevelVectors.ReferenceLimits.MaxMemberInflatedBytes, "the archive limits are the reference's");

        // The members of an archive inflate to at most the archive total together: each may take what the earlier ones left.
        byte[] Member(int inflated)
        {
            using MemoryStream packed = new();
            using (ZLibStream zlib = new(packed, CompressionLevel.Optimal, leaveOpen: true)) zlib.Write(new byte[inflated]);
            byte[] member = packed.ToArray();
            return [.. BitConverter.GetBytes((uint)member.Length), .. member];
        }
        byte[] three = [.. Member(1000), .. Member(1000), .. Member(1000)];
        check.That(LevelArchive.Inflate(three, 3000).Length == 3000, "members that inflate to exactly the archive total are read");
        Refuses(check, "members that inflate to one byte more than the archive total", () => LevelArchive.Inflate(three, 2999));
        Refuses(check, "a member that has nothing left of the archive total", () => LevelArchive.Inflate(three, 2000));
        Refuses(check, "a first member over the archive total", () => LevelArchive.Inflate(three, 999));
    }

    private static void ArchiveFolder(string folder, Checks check)
    {
        string resources = Path.Combine(folder, "data", "Resources");
        Directory.CreateDirectory(resources);
        LevelVectors.ArchiveVector one = LevelVectors.Archives.First(v => v.Name == "real-only"), two = LevelVectors.Archives.First(v => v.Name == "base-and-real");
        string a = Path.Combine(resources, "100_res_PC.aya"), b = Path.Combine(resources, "007_res_pc.aya");
        File.WriteAllBytes(a, Unpack(one.File));
        File.WriteAllBytes(b, Unpack(two.File));
        foreach (string other in new[] { "100_res_PC.aya.bak", "res_PC.aya", "1000_res_PC.aya", "10_res_PC.aya", "goodie_03_res_PC.aya", "100_res_PC.AYA.txt" })
            File.WriteAllBytes(Path.Combine(resources, other), [1]);
        bool linked = true;
        try
        {
            File.CreateSymbolicLink(Path.Combine(resources, "101_res_PC.aya"), a);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or PlatformNotSupportedException)
        {
            linked = false;
        }

        IReadOnlyList<LevelArchiveFile> files = LevelArchive.List(folder);
        check.That(files.Select(f => f.Level).SequenceEqual([7, 100]), "the level archives are the three-digit NNN_res_PC.aya files, by number, links left out: " + string.Join(",", files.Select(f => f.Level)));
        check.That(files.Count == 2 && files[0].Path == b && files[1].Path == a, "each level archive names its file");
        check.That(LevelArchive.List(Path.Combine(folder, "missing")).Count == 0 && LevelArchive.List(resources).Count == 0, "a folder with no data/resources lists nothing");
        // Two files of one level number: the later name wins, as in the reference (only where names differ by case).
        string twins = Path.Combine(folder, "twins", "data", "resources");
        Directory.CreateDirectory(twins);
        File.WriteAllBytes(Path.Combine(twins, "100_res_PC.aya"), Unpack(one.File));
        File.WriteAllBytes(Path.Combine(twins, "100_res_pc.aya"), Unpack(two.File));
        if (Directory.GetFiles(twins).Length == 2)
        {
            IReadOnlyList<LevelArchiveFile> twin = LevelArchive.List(Path.Combine(folder, "twins"));
            check.That(twin.Count == 1 && twin[0].Path == Path.Combine(twins, "100_res_pc.aya"), "two level archives of one number list the later name");
        }
        LevelWorlds worlds = LevelArchive.ReadFile(a);
        check.That(worlds.RealLevel == one.RealLevel && worlds.BaseBody is null && worlds.RealBody is not null, "an archive file is read");
        if (linked) Refuses(check, "reading a level archive that is a link", () => LevelArchive.ReadFile(Path.Combine(resources, "101_res_PC.aya")));
        Refuses(check, "reading an empty level archive file", () =>
        {
            string empty = Path.Combine(resources, "empty.aya");
            File.WriteAllBytes(empty, []);
            LevelArchive.ReadFile(empty);
        });
    }
}
