// SPDX-License-Identifier: GPL-3.0-only
using System.Collections.ObjectModel;
using System.Numerics;
using System.Text;

namespace OnslaughtToolkit.Companion.Missions;

/// <summary>An authored placement, identified independently of its position in a list. Definition names are references, not bundled assets.</summary>
public sealed record CeMissionPlacement(string Id, string Name, string Definition, Vector3 Position, string? ScriptId = null);

/// <summary>Preserved source text. This document does not compile it or assert that CE can execute it.</summary>
public sealed record CeMissionSource(string Id, string Name, string Text);

/// <summary>
/// An immutable candidate CE authoring document, independent of retail world bytes and editor scenes.
/// X and Y are horizontal; positive Z points down. Positions use game units, with no physical-unit conversion implied.
/// This is an authoring contract; CE runtime loading and source compilation are separate consumers.
/// </summary>
public sealed class CeMissionProject
{
    public const string Kind = "onslaught.ce.mission-project", CoordinateFrame = "aquila-xyz-z-down", SourceLanguage = "bea-msl";
    public const int Version = 1, MaxPlacements = 4096, MaxScripts = 128, MaxSourceBytes = 1 << 20,
        MaxTotalSourceBytes = 4 << 20, MaxDocumentBytes = 8 << 20;
    private static readonly UTF8Encoding Utf8 = new(false, true);

    public string Id { get; }
    public string Name { get; }
    public string? EntryScriptId { get; }
    public ReadOnlyCollection<CeMissionPlacement> Placements { get; }
    public ReadOnlyCollection<CeMissionSource> Scripts { get; }

    public CeMissionProject(string id, string name, IEnumerable<CeMissionPlacement> placements,
        IEnumerable<CeMissionSource> scripts, string? entryScriptId = null)
    {
        CheckId(id, "Project ID");
        CheckText(name, "Project name", 256, allowEmpty: false, multiline: false);
        ArgumentNullException.ThrowIfNull(placements);
        ArgumentNullException.ThrowIfNull(scripts);
        CeMissionPlacement[] objects = placements.Take(MaxPlacements + 1).ToArray();
        CeMissionSource[] sources = scripts.Take(MaxScripts + 1).ToArray();
        if (objects.Length > MaxPlacements || sources.Length > MaxScripts)
            throw new ArgumentException("The project exceeds the editor's placement or script limit.");
        HashSet<string> objectIds = new(StringComparer.Ordinal), sourceIds = new(StringComparer.Ordinal);
        int sourceBytes = 0;
        foreach (CeMissionSource source in sources)
        {
            ArgumentNullException.ThrowIfNull(source);
            CheckId(source.Id, "Script ID");
            if (!sourceIds.Add(source.Id)) throw new ArgumentException("Script IDs must be unique.");
            CheckText(source.Name, "Script name", 256, allowEmpty: false, multiline: false);
            sourceBytes += CheckText(source.Text, "Script source", MaxSourceBytes, allowEmpty: true, multiline: true);
            if (sourceBytes > MaxTotalSourceBytes) throw new ArgumentException("The project's combined script source is too large.");
        }
        foreach (CeMissionPlacement placement in objects)
        {
            ArgumentNullException.ThrowIfNull(placement);
            CheckId(placement.Id, "Placement ID");
            if (!objectIds.Add(placement.Id)) throw new ArgumentException("Placement IDs must be unique.");
            CheckText(placement.Name, "Placement name", 256, allowEmpty: false, multiline: false);
            CheckText(placement.Definition, "Definition reference", 256, allowEmpty: false, multiline: false);
            Vector3 position = placement.Position;
            if (!float.IsFinite(position.X) || !float.IsFinite(position.Y) || !float.IsFinite(position.Z))
                throw new ArgumentException("A placement needs three finite coordinates.");
            CheckScriptReference(placement.ScriptId, sourceIds);
        }
        CheckScriptReference(entryScriptId, sourceIds);
        Id = id;
        Name = name;
        EntryScriptId = entryScriptId;
        Placements = Array.AsReadOnly(objects.OrderBy(item => item.Id, StringComparer.Ordinal).ToArray());
        Scripts = Array.AsReadOnly(sources.OrderBy(item => item.Id, StringComparer.Ordinal).ToArray());
    }

    public static CeMissionProject Empty(string id, string name) => new(id, name, [], []);

    public CeMissionPlacement Placement(string id) => Placements.FirstOrDefault(item => item.Id == id)
        ?? throw new ArgumentException("That placement is not in this project.");

    public CeMissionSource Script(string id) => Scripts.FirstOrDefault(item => item.Id == id)
        ?? throw new ArgumentException("That script is not in this project.");

    internal CeMissionProject WithPlacements(IEnumerable<CeMissionPlacement> placements) => new(Id, Name, placements, Scripts, EntryScriptId);
    internal CeMissionProject WithScripts(IEnumerable<CeMissionSource> scripts) => new(Id, Name, Placements, scripts, EntryScriptId);
    internal CeMissionProject WithEntry(string? scriptId) => new(Id, Name, Placements, Scripts, scriptId);
    internal CeMissionProject WithName(string name) => new(Id, name, Placements, Scripts, EntryScriptId);

    private static void CheckScriptReference(string? id, HashSet<string> scripts)
    {
        if (id is null) return;
        CheckId(id, "Script reference");
        if (!scripts.Contains(id)) throw new ArgumentException("A script reference names no source in this project.");
    }

    private static void CheckId(string value, string label)
    {
        if (value is null || value.Length is < 1 or > 96 || !AsciiStart(value[0]) ||
            value.Any(character => !AsciiStart(character) && !(character is >= '0' and <= '9' or '-' or '.')))
            throw new ArgumentException($"{label} must be an ASCII identifier of at most 96 characters.");
    }

    private static bool AsciiStart(char value) => value is >= 'a' and <= 'z' or >= 'A' and <= 'Z' or '_';

    private static int CheckText(string value, string label, int maxBytes, bool allowEmpty, bool multiline)
    {
        if (value is null || (!allowEmpty && string.IsNullOrWhiteSpace(value)) ||
            value.Any(character => char.IsControl(character) && !(multiline && character is '\r' or '\n' or '\t')))
            throw new ArgumentException($"{label} is empty or contains unsupported control characters.");
        try
        {
            int bytes = Utf8.GetByteCount(value);
            if (bytes > maxBytes) throw new ArgumentException($"{label} exceeds the editor's text limit.");
            return bytes;
        }
        catch (EncoderFallbackException error) { throw new ArgumentException($"{label} is not valid Unicode.", error); }
    }
}
