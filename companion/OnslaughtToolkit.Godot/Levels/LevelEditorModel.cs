// SPDX-License-Identifier: GPL-3.0-only
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
using OnslaughtToolkit.Companion.Missions;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>One row of the object table: a stored thing record, where it stands now and where the level has it.</summary>
public sealed record ObjectRow(int Index, string Kind, string Name, string Definition, Vector3 Position, Vector3 Stock, float Radius = 0f)
{
    /// <summary>The name the player sees: the record's own name, else the definition it names (a Target Tank), else its kind.</summary>
    public string Label => Name.Length > 0 ? Name : Definition.Length > 0 ? Definition : Kind;

    /// <summary>Whether the position differs from the level's own, bit for bit (a zero that became a negative zero is a change).</summary>
    public bool Changed => BitConverter.SingleToUInt32Bits(Position.X) != BitConverter.SingleToUInt32Bits(Stock.X) ||
                           BitConverter.SingleToUInt32Bits(Position.Y) != BitConverter.SingleToUInt32Bits(Stock.Y) ||
                           BitConverter.SingleToUInt32Bits(Position.Z) != BitConverter.SingleToUInt32Bits(Stock.Z);
}

/// <summary>A compiled script of the open level: its summary, and where its source is looked for (a base world's scripts are in the base level's folder).</summary>
public sealed record ScriptEntry(ScriptSummary Summary, int SourceLevel, bool FromBaseWorld);

/// <summary>What typing coordinates for an object (or putting it back) did.</summary>
public enum MoveResult
{
    /// <summary>The object was moved.</summary>
    Moved,

    /// <summary>Nothing needed to change: the object already stands there.</summary>
    Unchanged,

    /// <summary>A coordinate was not accepted, or the move cannot be made; nothing changed.</summary>
    Refused,
}

/// <param name="Result">What happened.</param>
/// <param name="Message">A sentence for the player: what was done, what was stored if it differs from what was typed, or what to fix.</param>
public sealed record MoveOutcome(MoveResult Result, string Message);

/// <summary>What saving the edit as a mod did.</summary>
/// <param name="Staged">The mod that was written, or null.</param>
/// <param name="Message">A sentence for the player: where the mod is, or why it was not saved.</param>
public sealed record SaveOutcome(StagedMod? Staged, string Message)
{
    public bool Ok => Staged is not null;
}

/// <summary>What compiling a script's source came to: the compiled script, or why there is none, and what the compiler noticed on the way.</summary>
/// <param name="Script">The compiled script (named as the one it would replace), or null.</param>
/// <param name="Message">A sentence for the player: what was made, or the compiler's message (which starts "line N: " when it is about a line).</param>
/// <param name="Line">The 0-based line the refusal is about, or null.</param>
/// <param name="Notes">What the compiler noticed (how a mixed chain of operators was grouped, a handler the game never calls, a variable declared twice).</param>
public sealed record ScriptCompileOutcome(MissionScript? Script, string Message, int? Line, IReadOnlyList<CompileNote> Notes)
{
    public bool Ok => Script is not null;

    /// <summary>What the edit makes the script do that is known to be dangerous in the game as it is (see <see cref="ScriptHazards"/>); empty when nothing is.</summary>
    public IReadOnlyList<string> Warnings { get; init; } = [];
}

/// <summary>What replacing a script from its source (or putting the shipped one back) did.</summary>
public enum ScriptEditResult
{
    /// <summary>The script was replaced; the edit can be taken back.</summary>
    Replaced,

    /// <summary>Nothing needed to change: the script is already what the source compiles to.</summary>
    Unchanged,

    /// <summary>The source did not compile, or the replacement cannot be made; nothing changed.</summary>
    Refused,
}

/// <param name="Result">What happened.</param>
/// <param name="Message">A sentence for the player.</param>
/// <param name="Line">The 0-based line a refusal is about, or null.</param>
/// <param name="Notes">What the compiler noticed (empty when the source was not compiled).</param>
public sealed record ScriptEditOutcome(ScriptEditResult Result, string Message, int? Line, IReadOnlyList<CompileNote> Notes)
{
    /// <summary>What the edit makes the script do that is known to be dangerous in the game as it is (empty when nothing is, or the source was not compiled).</summary>
    public IReadOnlyList<string> Warnings { get; init; } = [];
}

/// <summary>
/// The state behind the Level editor page, with no interface in it: the levels a game has, the open level's own world as an
/// <see cref="EditSession"/>, the object table, the coordinates typed for one object, and saving the edit as a Onslaught CE mod. The
/// level's own world is the only one edited; a base world the archive carries is left as it is.
/// </summary>
public sealed class LevelEditorModel(IReadOnlyList<LevelArchiveFile> levels)
{
    /// <summary>The model for the level archives of a game folder.</summary>
    public static LevelEditorModel ForGame(string gameRoot) => new(LevelArchive.List(gameRoot));

    public IReadOnlyList<LevelArchiveFile> Levels { get; private set; } = levels;

    /// <summary>
    /// Lists the game's level archives again (a quick listing of one folder), keeping the level that is open and its edit. Returns whether the
    /// list differs from the one the model had.
    /// </summary>
    public bool Rescan(string gameRoot)
    {
        IReadOnlyList<LevelArchiveFile> now = LevelArchive.List(gameRoot);
        bool differs = !now.SequenceEqual(Levels);
        Levels = now;
        return differs;
    }

    /// <summary>The level asked for last, whether or not it could be opened.</summary>
    public int? Level { get; private set; }

    private string? _savedSignature;

    /// <summary>The moved objects and where each stands, bit for bit, and the replaced scripts and their stored bytes' SHA-256, as one text: two edits that leave everything the same have the same one.</summary>
    private static string Signature(EditSession session) => string.Join(';', session.Changes().Select(change =>
        $"{change.Index}:{BitConverter.SingleToUInt32Bits(change.To.X):x8}:{BitConverter.SingleToUInt32Bits(change.To.Y):x8}:{BitConverter.SingleToUInt32Bits(change.To.Z):x8}")
        .Concat(session.ScriptChanges().Select(change => $"script {change.Index}:{Convert.ToHexStringLower(SHA256.HashData(WorldBodyWriter.ScriptBytes(session.Body.Scripts[change.Index])))}")));

    /// <summary>
    /// How many objects stand somewhere their level does not have them and how many scripts differ from the level's, when no Save as mod has written that yet
    /// (0 when there is nothing to lose): what leaving the level, the game or the companion would drop. An edit that was saved and then undone, or saved and
    /// left as it is, holds nothing unsaved.
    /// </summary>
    public int UnsavedChangeCount
    {
        get
        {
            if (Session is not { } session) return 0;
            int changed = session.Changes().Count + session.ScriptChanges().Count;
            return changed > 0 && Signature(session) != _savedSignature ? changed : 0;
        }
    }

    public bool HasUnsavedChanges => UnsavedChangeCount > 0;

    /// <summary>What the open level's archive holds.</summary>
    public LevelWorlds? Worlds { get; private set; }

    /// <summary>The edit of the open level's own world, or null when none is open.</summary>
    public EditSession? Session { get; private set; }

    /// <summary>Why the level asked for last cannot be edited, or null.</summary>
    public string? Problem { get; private set; }

    /// <summary>The open level's terrain (its archive's ERES chunk), or null when it has none or it cannot be read (see <see cref="TerrainProblem"/>). Editing does not need it.</summary>
    public Heightfield? Terrain { get; private set; }

    /// <summary>Why the terrain could not be read, or null.</summary>
    public string? TerrainProblem { get; private set; }

    /// <summary>
    /// The compiled scripts of the open level: its own world's, then its base world's (which the game loads with it). A base world's scripts name
    /// objects of the base world, which this editor does not list, so they carry no rows. Empty when no level is open.
    /// </summary>
    public IReadOnlyList<ScriptEntry> Scripts { get; private set; } = [];

    /// <summary>The base world's body, which is shown and not edited: null when the open level has none or it does not read. Its objects are not listed.</summary>
    public WorldBody? BaseWorld { get; private set; }

    /// <summary>The level whose world the archive also carries as a base world, or null. It is shown, not edited.</summary>
    public int? BaseLevel => Worlds is { BaseBody: not null } worlds && worlds.BaseLevel >= 0 ? worlds.BaseLevel : null;

    /// <summary>Raised after a level is opened or refused and after every edit, undo and redo.</summary>
    public event Action? Changed;

    /// <summary>Opens a level's own world for editing. Returns false, with <see cref="Problem"/> set, if it cannot be.</summary>
    public bool Open(int level)
    {
        Level = level;
        Worlds = null;
        Session = null;
        _savedSignature = null;
        Problem = null;
        Terrain = null;
        TerrainProblem = null;
        Scripts = [];
        _listedScripts = [];
        BaseWorld = null;
        LevelArchiveFile? file = Levels.FirstOrDefault(archive => archive.Level == level);
        if (file is null) return Refuse($"This game has no archive for level {level}.");
        try
        {
            LevelWorlds worlds = LevelArchive.ReadFile(file.Path);
            Worlds = worlds;
            if (worlds.RealBody is null) return Refuse($"Level {level}'s archive holds no world of its own, so there is nothing to move.");
            if (worlds.RealLevel != level)
                return Refuse($"Level {level}'s archive names level {worlds.RealLevel} as its world's level, so a mod for it would not be read as level {level}'s world. This editor does not change it.");
            EditSession session = new(worlds.RealBody);
            session.Changed += () =>
            {
                RefreshScripts();
                Changed?.Invoke();
            };
            Session = session;
            Scripts = ListScripts(session.Body, worlds);
            _listedScripts = [.. session.Body.Scripts];
            BaseWorld = ReadBaseWorld(worlds);
            if (worlds.Terrain is null)
            {
                TerrainProblem = "This level's archive holds no terrain.";
            }
            else
            {
                try
                {
                    Terrain = Heightfield.Read(worlds.Terrain);
                }
                catch (InvalidDataException error)
                {
                    TerrainProblem = $"The terrain could not be read: {error.Message}";
                }
            }
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException or InvalidDataException)
        {
            return Refuse($"Level {level} could not be read: {error.Message}");
        }
        Changed?.Invoke();
        return true;
    }

    private MissionScript[] _listedScripts = [];

    /// <summary>Lists the scripts again when the world's list holds other script objects than the ones last listed (a replacement, or taking one back).</summary>
    private void RefreshScripts()
    {
        if (Session is not { } session || Worlds is not { } worlds) return;
        MissionScript[] now = [.. session.Body.Scripts];
        if (now.AsSpan().SequenceEqual(_listedScripts)) return;
        _listedScripts = now;
        Scripts = ListScripts(session.Body, worlds);
    }

    /// <summary>The scripts of a level's own world and of its base world, as <see cref="Scripts"/> lists them (the retail gate calls this too).</summary>
    internal static IReadOnlyList<ScriptEntry> ListScripts(WorldBody own, LevelWorlds worlds)
    {
        List<ScriptEntry> entries = [.. ScriptCatalog.Of(own).Select(summary => new ScriptEntry(summary, worlds.RealLevel, FromBaseWorld: false))];
        if (ReadBaseWorld(worlds) is { } baseWorld)
            entries.AddRange(ScriptCatalog.Of(baseWorld).Select(summary => new ScriptEntry(summary with { Uses = [] }, worlds.BaseLevel, FromBaseWorld: true)));
        return entries;
    }

    /// <summary>A level archive's base world, or null when it has none or its body does not read: the base world is only shown, so the level's own world is still listed without it.</summary>
    internal static WorldBody? ReadBaseWorld(LevelWorlds worlds)
    {
        if (worlds.BaseBody is not { } baseBytes || worlds.BaseLevel < 0) return null;
        try
        {
            return WorldBody.Read(baseBytes);
        }
        catch (InvalidDataException)
        {
            return null;
        }
    }

    private bool Refuse(string problem)
    {
        Problem = problem;
        Changed?.Invoke();
        return false;
    }

    /// <summary>The objects of the open world in row order; a search keeps those whose row number, name, definition, kind or script holds it.</summary>
    public IReadOnlyList<ObjectRow> Rows(string search = "")
    {
        if (Session is null) return [];
        Dictionary<int, Vector3> stock = Session.Changes().ToDictionary(change => change.Index, change => change.From);
        string needle = search.Trim();
        List<ObjectRow> rows = [];
        for (int i = 0; i < Session.Body.Things.Count; i++)
        {
            PlacedObject thing = Session.Body.Things[i];
            ObjectRow row = new(i, thing.Kind, thing.Init.Name, thing.Definition ?? "", thing.Init.Position, stock.TryGetValue(i, out Vector3 from) ? from : thing.Init.Position,
                thing.Init.SphereTrigger?.Radius ?? 0f);
            if (needle.Length == 0 || Matches(row, thing.Init.Script, needle)) rows.Add(row);
        }
        return rows;
    }

    private static bool Matches(ObjectRow row, string script, string needle) =>
        row.Index.ToString(System.Globalization.CultureInfo.InvariantCulture) == needle ||
        row.Name.Contains(needle, StringComparison.OrdinalIgnoreCase) || row.Definition.Contains(needle, StringComparison.OrdinalIgnoreCase) ||
        row.Kind.Contains(needle, StringComparison.OrdinalIgnoreCase) || script.Contains(needle, StringComparison.OrdinalIgnoreCase);

    /// <summary>One object's row, or null if there is no such row.</summary>
    public ObjectRow? Row(int index) => Rows().ElementAtOrDefault(index) is { } row && row.Index == index ? row : null;

    /// <summary>The texts the three fields of a row show: each coordinate as the shortest text that reads back as the stored float32.</summary>
    public static (string X, string Y, string Z) Shown(Vector3 position) =>
        (CoordinateInput.Format(position.X), CoordinateInput.Format(position.Y), CoordinateInput.Format(position.Z));

    /// <summary>
    /// Moves a row to the coordinates typed for it. A field whose text is still what <see cref="Shown"/> gives for the row is not read
    /// again, so its stored bits stay exactly as they are (a stored -0 stays -0); every other field is read as the Toolkit's move
    /// tool reads a coordinate. If any field is refused, nothing changes.
    /// </summary>
    public MoveOutcome Move(int row, string x, string y, string z)
    {
        if (Session is null) return new MoveOutcome(MoveResult.Refused, "Open a level first.");
        if (row < 0 || row >= Session.Body.Things.Count) return new MoveOutcome(MoveResult.Refused, $"There is no row {row} in this world.");
        Vector3 current = Session.Body.Things[row].Init.Position;
        (string, string, string) shown = Shown(current);
        float[] values = [current.X, current.Y, current.Z];
        string[] typed = [x, y, z], showing = [shown.Item1, shown.Item2, shown.Item3], labels = ["X", "Y", "Z"];
        List<string> rounded = [];
        for (int axis = 0; axis < 3; axis++)
        {
            if (typed[axis] == showing[axis]) continue;
            CoordinateParse parsed = CoordinateInput.Parse(typed[axis]);
            if (!parsed.Ok) return new MoveOutcome(MoveResult.Refused, $"{labels[axis]}: {parsed.Problem}");
            values[axis] = parsed.Value;
            if (parsed.Rounded) rounded.Add($"{labels[axis]} {CoordinateInput.Exact(parsed.Value)}");
        }
        Vector3 target = new(values[0], values[1], values[2]);
        if (SameBits(target, current)) return new MoveOutcome(MoveResult.Unchanged, "That is where it already stands.");
        string note = rounded.Count == 0 ? "" : $" Stored as {string.Join(", ", rounded)} (the nearest {(rounded.Count == 1 ? "value" : "values")} the game can hold).";
        return Apply(new MoveObject(row, target), $"{Session.Body.Things[row].Label} (row {row}) now stands at {Describe(target)}.{note}");
    }

    /// <summary>Moves a row to X and Y (a drag on the map), keeping its stored Z bit for bit. A move that refuses changes nothing.</summary>
    public MoveOutcome MoveTo(int row, float x, float y)
    {
        if (Session is null) return new MoveOutcome(MoveResult.Refused, "Open a level first.");
        if (row < 0 || row >= Session.Body.Things.Count) return new MoveOutcome(MoveResult.Refused, $"There is no row {row} in this world.");
        if (!float.IsFinite(x) || !float.IsFinite(y)) return new MoveOutcome(MoveResult.Refused, "A position must be finite numbers.");
        Vector3 current = Session.Body.Things[row].Init.Position;
        Vector3 target = new(x, y, current.Z);
        if (SameBits(target, current)) return new MoveOutcome(MoveResult.Unchanged, "That is where it already stands.");
        return Apply(new MoveObject(row, target), $"{Session.Body.Things[row].Label} (row {row}) now stands at {Describe(target)}.");
    }

    /// <summary>Puts a row back where the level has it (an edit that can be undone).</summary>
    public MoveOutcome Reset(int row)
    {
        if (Session is null) return new MoveOutcome(MoveResult.Refused, "Open a level first.");
        ObjectRow? current = Row(row);
        if (current is null) return new MoveOutcome(MoveResult.Refused, $"There is no row {row} in this world.");
        if (!current.Changed) return new MoveOutcome(MoveResult.Unchanged, "That object has not been moved.");
        return Apply(new MoveObject(row, current.Stock), $"{current.Label} (row {row}) is back where the level has it, at {Describe(current.Stock)}.");
    }

    private MoveOutcome Apply(IEditCommand command, string done)
    {
        try
        {
            Session!.Apply(command);
        }
        catch (InvalidOperationException error)
        {
            return new MoveOutcome(MoveResult.Refused, error.Message);
        }
        return new MoveOutcome(MoveResult.Moved, done);
    }

    private static string Describe(Vector3 position) => $"{CoordinateInput.Format(position.X)}, {CoordinateInput.Format(position.Y)}, {CoordinateInput.Format(position.Z)}";

    private static bool SameBits(Vector3 a, Vector3 b) =>
        BitConverter.SingleToUInt32Bits(a.X) == BitConverter.SingleToUInt32Bits(b.X) &&
        BitConverter.SingleToUInt32Bits(a.Y) == BitConverter.SingleToUInt32Bits(b.Y) &&
        BitConverter.SingleToUInt32Bits(a.Z) == BitConverter.SingleToUInt32Bits(b.Z);

    /// <summary>A sentence about the changes made, or null when there are none: "1 object moved: Target Tank (row 12), 62.1 units." and "1 script replaced: alpha (1 symbol differs)."</summary>
    public string? ChangeSummary()
    {
        IReadOnlyList<ObjectChange> changes = Session?.Changes() ?? [];
        IReadOnlyList<ScriptChange> scripts = Session?.ScriptChanges() ?? [];
        List<string> sentences = [];
        if (changes.Count > 0)
        {
            string list = string.Join("; ", changes.Take(3).Select(change => $"{change.Name} (row {change.Index}), {change.Distance:0.0} units"));
            sentences.Add($"{(changes.Count == 1 ? "1 object moved" : $"{changes.Count} objects moved")}: {list}{(changes.Count > 3 ? $" and {changes.Count - 3} more" : "")}.");
        }
        if (scripts.Count > 0)
        {
            string list = string.Join("; ", scripts.Take(3).Select(change => $"{change.Name} ({change.Describe()})"));
            sentences.Add($"{(scripts.Count == 1 ? "1 script replaced" : $"{scripts.Count} scripts replaced")}: {list}{(scripts.Count > 3 ? $" and {scripts.Count - 3} more" : "")}.");
        }
        return sentences.Count == 0 ? null : string.Join(" ", sentences);
    }

    /// <summary>The place of a script entry in the open level's own world, or null for an entry of the base world (which is shown, not edited) or one this model does not list.</summary>
    public int? OwnScriptIndex(ScriptEntry entry)
    {
        if (entry.FromBaseWorld) return null;
        for (int i = 0; i < Scripts.Count; i++)
            if (ReferenceEquals(Scripts[i], entry)) return i;
        return null;
    }

    /// <summary>
    /// Compiles source text as the replacement for one of the open level's own scripts: headers come from the game folder, and the compile session's two
    /// counters start where the shipped script's do, so that what the edit did not touch keeps its names and the result differs from the shipped script
    /// where the source does. Nothing is replaced; see <see cref="ReplaceScriptFromSource"/>.
    /// </summary>
    public ScriptCompileOutcome CompileScript(int scriptIndex, string source, string gameRoot)
    {
        if (Session is null) return new ScriptCompileOutcome(null, "Open a level first.", null, []);
        if (scriptIndex < 0 || scriptIndex >= Session.Body.Scripts.Count) return new ScriptCompileOutcome(null, $"There is no script {scriptIndex} in this world.", null, []);
        MissionScript shipped = Session.ShippedScript(scriptIndex);
        List<CompileNote> notes = [];
        try
        {
            MissionScript script = ScriptCompiler.Compile(shipped.Name, source, ScriptCompiler.IncludesFrom(gameRoot), ScriptCompiler.ConstStartOf(shipped), ScriptCompiler.DoOnceStartOf(shipped), null, notes);
            return new ScriptCompileOutcome(script, $"Compiled {script.Name}: {script.Code.Instructions.Count} instructions.", null, notes) { Warnings = ScriptHazards.Warnings(shipped, script) };
        }
        catch (MissingInclude error)
        {
            return new ScriptCompileOutcome(null, $"{error.Message}, so this script cannot be compiled here.", null, notes);
        }
        catch (CompileError error)
        {
            return new ScriptCompileOutcome(null, error.Message, error.Line, notes);
        }
        catch (Exception error) when (error is IOException or UnauthorizedAccessException)
        {
            return new ScriptCompileOutcome(null, $"A file the script includes could not be read: {error.Message}", null, notes);
        }
    }

    /// <summary>Compiles source text and, when it compiles, replaces the script with the result as one edit that can be taken back. A source that does not compile changes nothing.</summary>
    public ScriptEditOutcome ReplaceScriptFromSource(int scriptIndex, string source, string gameRoot)
    {
        ScriptCompileOutcome compiled = CompileScript(scriptIndex, source, gameRoot);
        if (compiled.Script is not { } script) return new ScriptEditOutcome(ScriptEditResult.Refused, compiled.Message, compiled.Line, compiled.Notes);
        if (Same(Session!.Body.Scripts[scriptIndex], script)) return new ScriptEditOutcome(ScriptEditResult.Unchanged, $"{script.Name} is already what this source compiles to.", null, compiled.Notes) { Warnings = compiled.Warnings };
        return ApplyScript(new ReplaceScript(scriptIndex, script), $"Replaced {script.Name}.", compiled.Notes) with { Warnings = compiled.Warnings };
    }

    /// <summary>Puts a script back as the level has it (an edit that can be undone).</summary>
    public ScriptEditOutcome ResetScript(int scriptIndex)
    {
        if (Session is null) return new ScriptEditOutcome(ScriptEditResult.Refused, "Open a level first.", null, []);
        if (scriptIndex < 0 || scriptIndex >= Session.Body.Scripts.Count) return new ScriptEditOutcome(ScriptEditResult.Refused, $"There is no script {scriptIndex} in this world.", null, []);
        MissionScript shipped = Session.ShippedScript(scriptIndex);
        if (Same(Session.Body.Scripts[scriptIndex], shipped)) return new ScriptEditOutcome(ScriptEditResult.Unchanged, $"{shipped.Name} has not been replaced.", null, []);
        return ApplyScript(new ReplaceScript(scriptIndex, shipped), $"{shipped.Name} is back as the level has it.", []);
    }

    private ScriptEditOutcome ApplyScript(ReplaceScript command, string done, IReadOnlyList<CompileNote> notes)
    {
        try
        {
            Session!.Apply(command);
        }
        catch (InvalidOperationException error)
        {
            return new ScriptEditOutcome(ScriptEditResult.Refused, error.Message, null, notes);
        }
        return new ScriptEditOutcome(ScriptEditResult.Replaced, done, null, notes);
    }

    private static bool Same(MissionScript a, MissionScript b) => WorldBodyWriter.ScriptBytes(a).AsSpan().SequenceEqual(WorldBodyWriter.ScriptBytes(b));

    /// <summary>"Level 100 edit".</summary>
    public static string DefaultModName(int level) => $"Level {level} edit";

    /// <summary>A mod id (lowercase letters, digits, '-' and '_', at most 48) made from a name; "level-edit" if nothing is left of it.</summary>
    public static string ModIdFromName(string name)
    {
        StringBuilder id = new();
        foreach (char c in name.ToLowerInvariant())
        {
            char next = c is (>= 'a' and <= 'z') or (>= '0' and <= '9') or '_' ? c : '-';
            if (next == '-' && (id.Length == 0 || id[^1] == '-')) continue;
            id.Append(next);
        }
        string text = id.ToString().TrimEnd('-');
        if (text.Length > 48) text = text[..48].TrimEnd('-');
        return text.Length == 0 ? "level-edit" : text;
    }

    /// <summary>Writes the open edit as a CE mod folder <c>PARENT/ID</c>, or says why not (nothing changed, a folder that is not new, a game folder).</summary>
    public SaveOutcome SaveAsMod(string parent, ModInfo info, IEnumerable<string?> protectedFolders)
    {
        if (Session is null || Level is not int level) return new SaveOutcome(null, "Open a level first.");
        ValidationReport report = Session.Validate();
        if (!report.CanSave) return new SaveOutcome(null, report.Errors[0].Message);
        try
        {
            StagedMod staged = ModStager.Stage(parent, info, new Dictionary<int, byte[]> { [level] = Session.ToBytes() }, protectedFolders);
            _savedSignature = Signature(Session);
            return new SaveOutcome(staged, $"Saved the mod to {staged.Root}.");
        }
        catch (Exception error) when (error is ModStageException or InvalidDataException)
        {
            return new SaveOutcome(null, error.Message);
        }
    }
}
