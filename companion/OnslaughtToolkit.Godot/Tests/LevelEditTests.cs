// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;
using System.Security.Cryptography;
using OnslaughtToolkit.Companion.Levels;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>
/// The mod stager against the Toolkit's Python stager (tools/world_mod_stage.py) on the inputs tools/level_editor_vectors.py
/// ran it on: the same <c>mod.json</c> bytes, the same files, the same refusals; its refusals to write where it must not and
/// to leave anything behind; and the edit session (move, undo, redo, what changed, what is wrong) on the edits the reference
/// writes. Authored data only; nothing here touches Godot.
/// </summary>
internal static class LevelEditTests
{
    internal static void Run(string outputDirectory, Checks check)
    {
        check.Suite("level edits");
        Stage(check, "the stage vectors", () => StageVectors(Path.Combine(outputDirectory, "level-stage"), check));
        Stage(check, "the refused stage vectors", () => RefusedStageVectors(Path.Combine(outputDirectory, "level-stage-refused"), check));
        Stage(check, "the destination rules", () => DestinationRules(Path.Combine(outputDirectory, "level-stage-rules"), check));
        Stage(check, "the failure rules", () => FailureRules(Path.Combine(outputDirectory, "level-stage-failures"), check));
        Stage(check, "the session", () => SessionBasics(check));
        Stage(check, "the move vectors", () => MoveVectors(check));
        Stage(check, "the session refusals", () => SessionRefusals(check));
        Stage(check, "the validation", () => Validation(check));
        Stage(check, "an edit staged as a mod", () => EditToMod(Path.Combine(outputDirectory, "level-stage-edit"), check));
    }

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

    private static ModInfo Info(LevelVectors.StageVector v) => new(v.Id, v.ModName, v.Version, v.Author, v.Description, v.CeMin, v.CeMax);

    private static ModInfo Info(LevelVectors.RefusedStage v) => new(v.Id, v.ModName, v.Version, v.Author, v.Description, v.CeMin, v.CeMax);

    private static Dictionary<int, byte[]> Worlds(LevelVectors.StageWorld[] worlds)
    {
        Dictionary<int, byte[]> bodies = [];
        foreach (LevelVectors.StageWorld world in worlds)
        {
            bodies[world.Level] = world.From.Length > 0 ? LevelTests.Body(world.From)
                : world.Edit.Length > 0 ? LevelTests.Unpack(LevelVectors.Edits.First(e => e.Name == world.Edit).Body)
                : Enumerable.Repeat((byte)world.Repeat, world.Size).ToArray();
        }
        return bodies;
    }

    private static string Sha256(byte[] data) => Convert.ToHexStringLower(SHA256.HashData(data));

    private static string Difference(byte[] expected, byte[] actual)
    {
        int at = 0;
        while (at < expected.Length && at < actual.Length && expected[at] == actual[at]) at++;
        return $"(first at byte {at} of {expected.Length} and {actual.Length})";
    }

    private static void Refuses<TException>(Checks check, string what, Action action) where TException : Exception
    {
        try
        {
            action();
            check.Fail($"{what}: accepted");
        }
        catch (TException)
        {
            check.That(true, what);
        }
        catch (Exception error)
        {
            check.Fail($"{what}: refused with {error.GetType().Name} instead of {typeof(TException).Name}: {error.Message}");
        }
    }

    /// <summary>Every file under a folder, as '/'-separated paths from it.</summary>
    private static string[] Listing(string root) => [.. Directory.EnumerateFiles(root, "*", SearchOption.AllDirectories)
        .Select(path => Path.GetRelativePath(root, path).Replace(Path.DirectorySeparatorChar, '/')).Order(StringComparer.Ordinal)];

    // ---- the stager against the reference ------------------------------------------------------------------------------------
    private static void StageVectors(string folder, Checks check)
    {
        check.That(LevelVectors.Stages.Length >= 14, "the vector file holds the staged mods");
        foreach (LevelVectors.StageVector vector in LevelVectors.Stages)
        {
            ModInfo info = Info(vector);
            Dictionary<int, byte[]> worlds = Worlds(vector.Worlds);
            byte[] expected = LevelTests.Unpack(vector.Manifest);
            byte[] manifest = ModStager.BuildManifest(info, worlds.ToDictionary(w => ModStager.WorldPath(w.Key), w => w.Value));
            check.That(manifest.AsSpan().SequenceEqual(expected), $"{vector.Name}: mod.json is not the reference's {Difference(expected, manifest)}");
            check.That(Sha256(manifest) == vector.ManifestSha256, $"{vector.Name}: the manifest hash is the reference's");

            string parent = Path.Combine(folder, vector.Name);
            StagedMod staged = ModStager.Stage(parent, info, worlds, []);
            string root = Path.Combine(parent, vector.Id);
            check.That(staged.Root == root && staged.ManifestSha256 == vector.ManifestSha256, $"{vector.Name}: the receipt names the folder and the manifest");
            check.That(File.ReadAllBytes(Path.Combine(root, "mod.json")).AsSpan().SequenceEqual(expected), $"{vector.Name}: the mod.json written is the reference's");
            string[] listing = Listing(root), wanted = ["mod.json", .. vector.Files.Select(f => f.Path)];
            check.That(listing.SequenceEqual(wanted.Order(StringComparer.Ordinal)), $"{vector.Name}: the folder holds [{string.Join(", ", listing)}], the reference wrote [{string.Join(", ", wanted)}]");
            foreach (LevelVectors.StageFile file in vector.Files)
            {
                byte[] written = File.ReadAllBytes(Path.Combine(root, file.Path.Replace('/', Path.DirectorySeparatorChar)));
                check.That(written.Length == file.Size && Sha256(written) == file.Sha256, $"{vector.Name}: {file.Path} is the reference's");
            }
            check.That(staged.Files.Select(f => (f.Path, f.Size, f.Sha256)).SequenceEqual(vector.Files.Select(f => (f.Path, f.Size, f.Sha256))), $"{vector.Name}: the receipt lists the files as written");
            // A mod is never staged over itself: the folder now holds files.
            Refuses<ModStageException>(check, $"{vector.Name}: staging into the folder it just made", () => ModStager.Stage(parent, info, worlds, []));
        }
    }

    private static void RefusedStageVectors(string folder, Checks check)
    {
        check.That(LevelVectors.RefusedStages.Length >= 45, "the vector file holds the refused stagings");
        Directory.CreateDirectory(folder);
        foreach (LevelVectors.RefusedStage vector in LevelVectors.RefusedStages)
        {
            string parent = Path.Combine(folder, vector.Name);
            Refuses<ModStageException>(check, $"{vector.Name} ({vector.Why})", () => ModStager.Stage(parent, Info(vector), Worlds(vector.Worlds), []));
            check.That(!Directory.Exists(parent), $"{vector.Name}: a refused mod leaves nothing behind");
        }
        // Problem() names the first thing wrong with what a mod says about itself.
        check.That(ModStager.Problem(new ModInfo("ok-1", "Name")) is null && ModStager.Problem(new ModInfo("Bad", "Name")) is { } && ModStager.Problem(new ModInfo("ok", "")) is { } &&
                   ModStager.Problem(new ModInfo("ok", "Name", CeMin: "1.2.3.4.5")) is { }, "Problem names what is wrong with a mod's own words");
        // Versions are ordered as the loader orders them, and a range of one version is fine.
        foreach ((string low, string high, bool refused) in new[]
                 {
                     ("1.2", "1.1", true), ("1.10", "1.9", true), ("0.1.11", "0.1.10", true), ("2", "1.99999", true), ("1.2.0.1", "1.2", true),
                     ("1.2", "1.2", false), ("1.2.0", "1.2", false), ("1.2", "1.2.0.0", false), ("1.9", "1.10", false), ("0.1.11", "0.1.12", false),
                 })
            check.That((ModStager.Problem(new ModInfo("ok", "Name", CeMin: low, CeMax: high)) is not null) == refused, $"ce_min {low} and ce_max {high} are {(refused ? "refused" : "accepted")}");
        check.That(ModStager.Problem(new ModInfo("ok", "Name", CeMin: "99999")) is null && ModStager.Problem(new ModInfo("ok", "Name", CeMax: "0")) is null, "one bound alone is never compared");
        Refuses<ModStageException>(check, "a file that is not a world file", () => ModStager.BuildManifest(new ModInfo("ok", "Name"), new Dictionary<string, byte[]> { ["data/other.bin"] = [1] }));
        Refuses<ModStageException>(check, "a world path with four digits", () => ModStager.BuildManifest(new ModInfo("ok", "Name"), new Dictionary<string, byte[]> { ["data/worlds/world1000.wrd"] = [1] }));
        Refuses<ModStageException>(check, "more files than a mod may list", () => ModStager.BuildManifest(new ModInfo("ok", "Name"),
            Enumerable.Range(0, ModStager.MaxFilesPerMod + 1).ToDictionary(i => $"data/worlds/world{i:D3}.wrd", _ => new byte[] { 1 })));
    }

    // ---- where it writes -----------------------------------------------------------------------------------------------------
    private static void DestinationRules(string folder, Checks check)
    {
        ModInfo info = new("rules", "Rules");
        Dictionary<int, byte[]> worlds = new() { [100] = LevelTests.Body("authored-v50") };

        string parent = Path.Combine(folder, "parent");
        // A parent that does not exist yet is made, with the folders under it.
        StagedMod made = ModStager.Stage(Path.Combine(parent, "a", "b"), info, worlds, []);
        check.That(File.Exists(Path.Combine(made.Root, "mod.json")) && File.Exists(Path.Combine(made.Root, "data", "worlds", "world100.wrd")), "a parent that does not exist is made");

        // An existing empty folder is used; one that holds anything is not.
        string empty = Path.Combine(folder, "empty");
        Directory.CreateDirectory(Path.Combine(empty, "rules"));
        ModStager.Stage(empty, info, worlds, []);
        check.That(File.Exists(Path.Combine(empty, "rules", "mod.json")), "an existing empty folder is used");
        string holds = Path.Combine(folder, "holds");
        Directory.CreateDirectory(Path.Combine(holds, "rules"));
        File.WriteAllText(Path.Combine(holds, "rules", "keep.txt"), "mine");
        Refuses<ModStageException>(check, "a folder that already holds a file", () => ModStager.Stage(holds, info, worlds, []));
        check.That(File.ReadAllText(Path.Combine(holds, "rules", "keep.txt")) == "mine" && Listing(Path.Combine(holds, "rules")).Length == 1, "a folder that holds a file is left as it was");
        string aFile = Path.Combine(folder, "isfile");
        Directory.CreateDirectory(aFile);
        File.WriteAllText(Path.Combine(aFile, "rules"), "a file where the folder goes");
        Refuses<ModStageException>(check, "a file where the mod folder goes", () => ModStager.Stage(aFile, info, worlds, []));

        Refuses<ModStageException>(check, "a parent that is not a full path", () => ModStager.Stage("relative/folder", info, worlds, []));

        // Never into a protected folder (the game folder, the companion's backups), compared after resolving links.
        string game = Path.Combine(folder, "game");
        Directory.CreateDirectory(Path.Combine(game, "data"));
        Refuses<ModStageException>(check, "a mod folder inside a protected folder", () => ModStager.Stage(Path.Combine(game, "mods"), info, worlds, [game]));
        Refuses<ModStageException>(check, "a mod folder that is the protected folder itself", () => ModStager.Stage(Path.GetDirectoryName(game)!, new ModInfo("game", "Game"), worlds, [game]));
        check.That(!Directory.Exists(Path.Combine(game, "mods")), "nothing is made inside a protected folder");
        check.That(ModStager.Stage(Path.Combine(folder, "beside-game"), info, worlds, [game, null, "", Path.Combine(folder, "missing")]).Files.Count == 1, "a mod folder beside a protected folder is fine, and empty or missing guards are ignored");

        // Never inside an install: a folder with BEA.exe and data above it.
        string install = Path.Combine(folder, "install");
        Directory.CreateDirectory(Path.Combine(install, "data"));
        File.WriteAllBytes(Path.Combine(install, "BEA.exe"), [1]);
        Refuses<ModStageException>(check, "a mod folder inside an install, though none is listed as protected", () => ModStager.Stage(Path.Combine(install, "mods"), info, worlds, []));
        check.That(!Directory.Exists(Path.Combine(install, "mods")), "nothing is made inside an install");

        // Never through a link.
        string real = Path.Combine(folder, "real");
        Directory.CreateDirectory(real);
        string link = Path.Combine(folder, "link");
        string linkToGame = Path.Combine(folder, "link-to-game");
        string linkedRoot = Path.Combine(folder, "linked-root");
        Directory.CreateDirectory(linkedRoot);
        try
        {
            Directory.CreateSymbolicLink(link, real);
            Directory.CreateSymbolicLink(linkToGame, game);
            Directory.CreateSymbolicLink(Path.Combine(linkedRoot, "rules"), real);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or PlatformNotSupportedException)
        {
            return;
        }
        Refuses<ModStageException>(check, "a parent that is a link", () => ModStager.Stage(link, info, worlds, []));
        Refuses<ModStageException>(check, "a parent below a link", () => ModStager.Stage(Path.Combine(link, "deeper"), info, worlds, []));
        Refuses<ModStageException>(check, "a mod folder that is a link", () => ModStager.Stage(linkedRoot, info, worlds, []));
        Refuses<ModStageException>(check, "a link that leads into a protected folder", () => ModStager.Stage(Path.Combine(linkToGame, "mods"), info, worlds, [game]));
        check.That(Listing(real).Length == 0 && !Directory.Exists(Path.Combine(game, "mods")), "nothing is written through a link");
    }

    // ---- when something fails ------------------------------------------------------------------------------------------------
    private static void FailureRules(string folder, Checks check)
    {
        ModInfo info = new("fails", "Fails");
        Dictionary<int, byte[]> worlds = new() { [100] = LevelTests.Body("authored-v50"), [7] = LevelTests.Body("authored-v43") };

        // The world files are written first, in path order, and mod.json last.
        List<string> order = [];
        string parent = Path.Combine(folder, "order");
        ModStager.Stage(parent, info, worlds, [], beforeWrite: path => order.Add(Path.GetRelativePath(Path.Combine(parent, "fails"), path).Replace(Path.DirectorySeparatorChar, '/')));
        check.That(order.SequenceEqual(["data/worlds/world007.wrd", "data/worlds/world100.wrd", "mod.json"]), "the world files are written first, in path order, and mod.json last: " + string.Join(", ", order));

        // A failure at any write leaves nothing: not the files, not the folders this call made.
        for (int failAt = 0; failAt < 3; failAt++)
        {
            string where = Path.Combine(folder, $"fail-{failAt}");
            Directory.CreateDirectory(where);
            int writes = 0, at = failAt;
            Refuses<ModStageException>(check, $"a failure at write {failAt}", () => ModStager.Stage(Path.Combine(where, "made", "twice"), info, worlds, [],
                beforeWrite: _ => { if (writes++ == at) throw new IOException("the disk said no"); }));
            check.That(Listing(where).Length == 0 && Directory.GetDirectories(where).Length == 0, $"a failure at write {failAt} leaves nothing behind");
        }

        // A mod folder that existed (empty) stays, empty; one the call made goes.
        string kept = Path.Combine(folder, "kept");
        Directory.CreateDirectory(Path.Combine(kept, "fails"));
        Refuses<ModStageException>(check, "a failure into an existing empty folder", () => ModStager.Stage(kept, info, worlds, [], beforeWrite: path => { if (path.EndsWith("mod.json", StringComparison.Ordinal)) throw new IOException("no"); }));
        check.That(Directory.Exists(Path.Combine(kept, "fails")) && Directory.GetFileSystemEntries(Path.Combine(kept, "fails")).Length == 0, "an existing empty folder is left empty after a failure");
    }

    // ---- the edit session ----------------------------------------------------------------------------------------------------
    private static void SessionBasics(Checks check)
    {
        byte[] baseline = LevelTests.Body("authored-v50");
        EditSession session = new(baseline);
        int changed = 0;
        session.Changed += () => changed++;
        check.That(!session.CanUndo && !session.CanRedo && session.Changes().Count == 0 && session.ToBytes().AsSpan().SequenceEqual(baseline), "a new session holds the baseline and nothing to undo");
        check.That(session.Validate() is { CanSave: false } report && report.Errors.Single().Code == "no-change", "an unchanged world has nothing to save");

        LevelVectors.EditVector edit = LevelVectors.Edits.First(e => e.Name == "move-v50");
        byte[] expected = LevelTests.Unpack(edit.Body);
        session.Apply(new MoveObject(0, new Vector3(12.5f, -40f, 3f)));
        check.That(session.ToBytes().AsSpan().SequenceEqual(expected), "a move writes the bytes the reference writes for it");
        check.That(session.CanUndo && !session.CanRedo && session.UndoDescription == "Move Tank 1 (row 0)", "a move can be undone and says what it did: " + session.UndoDescription);
        ObjectChange change = session.Changes().Single();
        check.That(change.Index == 0 && change.Kind == "unit" && change.Name == "Tank 1" && change.From == new Vector3(10f, 20f, 0f) && change.To == new Vector3(12.5f, -40f, 3f) && Math.Abs(change.Distance - 60.13f) < 0.01f, "the change names the thing, where it was and where it is");
        check.That(session.Undo() && session.ToBytes().AsSpan().SequenceEqual(baseline) && session.Changes().Count == 0 && !session.CanUndo && session.CanRedo, "undo gives the baseline bytes back");
        check.That(!session.Undo(), "undo with nothing to undo does nothing");
        check.That(session.Redo() && session.ToBytes().AsSpan().SequenceEqual(expected) && session.CanUndo && !session.CanRedo && session.RedoDescription is null, "redo makes the move again, to the same bytes");
        check.That(!session.Redo(), "redo with nothing to redo does nothing");
        session.Undo();
        session.Apply(new MoveObject(2, new Vector3(1f, 2f, 3f)));
        check.That(!session.CanRedo, "a new edit clears what could be redone");
        check.That(session.UndoDescription == "Move waypoint (row 2)" && session.Changes().Single().Name == "waypoint", "a thing with no name is called by its kind: " + session.UndoDescription);
        check.That(changed == 5, $"every edit, undo and redo that happens raises Changed ({changed} of 5)");

        // Moving the same thing twice, then undoing both.
        EditSession twice = new(baseline);
        twice.Apply(new MoveObject(0, new Vector3(1f, 1f, 1f)));
        twice.Apply(new MoveObject(0, new Vector3(2f, 2f, 2f)));
        check.That(twice.Changes().Single().To == new Vector3(2f, 2f, 2f) && twice.Changes().Single().From == new Vector3(10f, 20f, 0f), "two moves of one thing are one change from the baseline");
        twice.Undo();
        check.That(twice.Body.Things[0].Init.Position == new Vector3(1f, 1f, 1f), "undo puts back the position before the last move, not the baseline's");
        twice.UndoAll();
        check.That(twice.ToBytes().AsSpan().SequenceEqual(baseline) && !twice.CanUndo, "UndoAll gives the baseline");
        twice.Apply(new MoveObject(0, new Vector3(10f, 20f, 0f)));
        check.That(twice.Changes().Count == 0 && twice.Validate().Errors.Single().Code == "no-change", "a move back to where the thing was is no change");

        // A change of the height alone, and of a zero's sign alone, is a change (compared bit for bit).
        EditSession height = new(baseline);
        height.Apply(new MoveObject(0, new Vector3(10f, 20f, 5f)));
        check.That(height.Changes().Count == 1 && height.Validate().CanSave, "a move that changes only the height is a change");
        EditSession sign = new(baseline);
        sign.Apply(new MoveObject(0, new Vector3(10f, 20f, -0f)));
        check.That(sign.Changes().Count == 1 && sign.Validate().CanSave && !sign.ToBytes().AsSpan().SequenceEqual(baseline), "a move from zero to negative zero is a change");

        // The baseline is copied: changing the array given to the session does not change the session.
        byte[] mine = baseline.ToArray();
        EditSession copied = new(mine);
        mine[10] ^= 0xFF;
        check.That(copied.Baseline.AsSpan().SequenceEqual(baseline) && copied.ToBytes().AsSpan().SequenceEqual(baseline), "the session keeps its own copy of the baseline");
    }

    /// <summary>Every edit vector made only of moves, made through a session: the reference's bytes, and undo to the baseline.</summary>
    private static void MoveVectors(Checks check)
    {
        int made = 0;
        foreach (LevelVectors.EditVector edit in LevelVectors.Edits)
        {
            if (edit.Steps.Any(step => step.Op != "move")) continue;
            made++;
            byte[] baseline = LevelTests.Body(edit.From);
            EditSession session = new(baseline);
            foreach (LevelVectors.EditStep step in edit.Steps) session.Apply(new MoveObject(step.Thing, new Vector3(step.X, step.Y, step.Z)));
            byte[] expected = LevelTests.Unpack(edit.Body);
            check.That(session.ToBytes().AsSpan().SequenceEqual(expected), $"{edit.Name}: the session writes the reference's bytes");
            session.UndoAll();
            check.That(session.ToBytes().AsSpan().SequenceEqual(baseline), $"{edit.Name}: undoing every move gives the baseline");
            while (session.Redo())
            {
            }
            check.That(session.ToBytes().AsSpan().SequenceEqual(expected), $"{edit.Name}: redoing every move gives the edit again");
        }
        check.That(made >= 5, $"the move vectors were run ({made})");
    }

    private static void SessionRefusals(Checks check)
    {
        byte[] baseline = LevelTests.Body("authored-v50");
        EditSession session = new(baseline);
        foreach (int index in new[] { -1, 5, 999 })
            Refuses<InvalidOperationException>(check, $"moving row {index} of five", () => session.Apply(new MoveObject(index, new Vector3(1f, 1f, 1f))));
        foreach (Vector3 bad in new[] { new Vector3(float.NaN, 1f, 1f), new Vector3(1f, float.PositiveInfinity, 1f), new Vector3(1f, 1f, float.NegativeInfinity) })
            Refuses<InvalidOperationException>(check, $"moving to {bad}", () => session.Apply(new MoveObject(0, bad)));
        check.That(!session.CanUndo && session.ToBytes().AsSpan().SequenceEqual(baseline), "a refused move changes nothing and is not an undo step");

        EditSession special = new(LevelTests.Body("special-floats"));
        Refuses<InvalidOperationException>(check, "moving a thing whose stored position is not finite", () => special.Apply(new MoveObject(0, new Vector3(1f, 1f, 1f))));
        special.Apply(new MoveObject(2, new Vector3(1f, 2f, 3f)));
        check.That(special.Changes().Count == 1, "another thing of that world can be moved");
        Refuses<InvalidDataException>(check, "a session on bytes that are not a world body", () => _ = new EditSession([1, 2, 3]));
        Refuses<InvalidDataException>(check, "a session on a body with a byte left over", () => _ = new EditSession([.. baseline, 0]));
        Refuses<InvalidDataException>(check, "a session on no bytes", () => _ = new EditSession([]));
        Refuses<InvalidOperationException>(check, "a move of a body with fewer rows than it names", () => new MoveObject(0, Vector3.One).Do(WorldBody.Read(LevelTests.Body("empty-v50"))));
    }

    private static void Validation(Checks check)
    {
        byte[] baseline = LevelTests.Body("authored-v50");

        EditSession inside = new(baseline);
        inside.Apply(new MoveObject(0, new Vector3(100f, 200f, -5f)));
        ValidationReport fine = inside.Validate();
        check.That(fine.CanSave && fine.Warnings.Count == 0, "a move inside the terrain square has no findings");

        EditSession outside = new(baseline);
        outside.Apply(new MoveObject(0, new Vector3(512f, 10f, 0f)));
        outside.Apply(new MoveObject(1, new Vector3(10f, -0.5f, 0f)));
        outside.Apply(new MoveObject(2, new Vector3(0f, 511.5f, 0f)));
        outside.Apply(new MoveObject(3, new Vector3(511.5f, 0f, 0f)));
        outside.Apply(new MoveObject(4, new Vector3(10f, 512f, 0f)));
        ValidationReport warned = outside.Validate();
        check.That(warned.CanSave && warned.Warnings.Select(w => w.Index).Order().SequenceEqual([0, 1, 4]) && warned.Warnings.All(w => w.Code == "outside-terrain"), "moves to or past the edge of the square warn, and moves to its corners inside do not");

        EditSession baseWorld = new(baseline, isBaseWorld: true);
        check.That(baseWorld.IsBaseWorld && baseWorld.Validate().Warnings.Count == 0, "an untouched base world has no warnings (it has an error: nothing to save)");
        baseWorld.Apply(new MoveObject(0, new Vector3(100f, 200f, 0f)));
        check.That(baseWorld.Validate().Warnings.Select(w => w.Code).SequenceEqual(["base-world"]), "a change to a base world warns about careers");

        // Edits made around the commands are found.
        EditSession rogue = new(baseline);
        rogue.Apply(new MoveObject(0, new Vector3(100f, 200f, 0f)));
        rogue.Body.Things[1].Init.Name = "renamed";
        check.That(rogue.Validate().Errors.Select(e => e.Code).SequenceEqual(["other-change"]) && !rogue.Validate().CanSave, "a change that is not a move is an error");
        EditSession removed = new(baseline);
        removed.Body.Things.RemoveAt(4);
        check.That(removed.Validate().Errors.Select(e => e.Code).SequenceEqual(["rows-changed"]), "removing a row is an error");
        EditSession reordered = new(baseline);
        (reordered.Body.Things[1], reordered.Body.Things[2]) = (reordered.Body.Things[2], reordered.Body.Things[1]);
        check.That(reordered.Validate().Errors.Select(e => e.Code).SequenceEqual(["rows-changed"]), "swapping a unit and a waypoint is an error");
        EditSession notFinite = new(baseline);
        notFinite.Body.Things[0].Init.Position = new Vector3(float.NaN, 0f, 0f);
        check.That(notFinite.Validate().Errors.Any(e => e.Code == "not-finite" && e.Index == 0), "a position that is not finite is an error");
        EditSession unwritable = new(baseline);
        unwritable.Body.Things[0].Init.Name = new string('n', 300);
        check.That(unwritable.Validate().Errors.Select(e => e.Code).SequenceEqual(["cannot-write"]), "a body the format cannot hold is an error");
        EditSession tooMany = new(baseline);
        while (tooMany.Body.Things.Count < 1001) tooMany.Body.Things.Add(tooMany.Body.Things[0]);
        check.That(tooMany.Validate().Errors.Select(e => e.Code).SequenceEqual(["cannot-write"]), "more than 1000 rows is an error");
    }

    /// <summary>The whole flow: a move made in a session, staged as a mod, is the folder the reference stages for that edit.</summary>
    private static void EditToMod(string folder, Checks check)
    {
        LevelVectors.StageVector vector = LevelVectors.Stages.First(v => v.Name == "full-metadata");
        EditSession session = new(LevelTests.Body("authored-v50"));
        session.Apply(new MoveObject(0, new Vector3(12.5f, -40f, 3f)));
        Dictionary<int, byte[]> worlds = new() { [100] = session.ToBytes(), [1] = LevelTests.Body("authored-v43") };
        check.That(session.Validate().CanSave, "the edit can be saved");
        StagedMod staged = ModStager.Stage(folder, Info(vector), worlds, []);
        check.That(staged.ManifestSha256 == vector.ManifestSha256 && staged.Files.Select(f => (f.Path, f.Size, f.Sha256)).SequenceEqual(vector.Files.Select(f => (f.Path, f.Size, f.Sha256))), "a move made in a session stages as the mod the reference stages for that edit");
        check.That(File.ReadAllBytes(Path.Combine(staged.Root, "mod.json")).AsSpan().SequenceEqual(LevelTests.Unpack(vector.Manifest)), "its mod.json is the reference's, byte for byte");
        EditSession reread = new(File.ReadAllBytes(Path.Combine(staged.Root, "data", "worlds", "world100.wrd")));
        check.That(reread.Body.Things[0].Init.Position == new Vector3(12.5f, -40f, 3f), "the staged world file reads back with the moved position");
    }
}
