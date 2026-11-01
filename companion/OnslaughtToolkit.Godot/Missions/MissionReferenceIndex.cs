using System;
using System.Collections.Generic;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>
/// A bounded, read-only view of scripts and the object assignments found in one
/// world. A missing name here may be supplied by another world. This does not
/// describe references inside script instructions or prove a mission will run.
/// </summary>
public sealed class MissionReferenceIndex
{
    public sealed class Script
    {
        internal Script(int index, ScriptSummary summary)
        {
            Index = index;
            Name = summary.Name;
            Events = Copy(summary.Events);
            Calls = Copy(summary.Calls);
            Uses = Copy(summary.Uses);
        }

        public int Index { get; }
        public string Name { get; }
        public IReadOnlyList<string> Events { get; }
        public IReadOnlyList<NativeCall> Calls { get; }
        public IReadOnlyList<ScriptUse> Uses { get; }
    }

    public readonly record struct ObjectReference(int Row, string Role, string Name, bool Resolved);

    private MissionReferenceIndex(Script[] scripts, ObjectReference[] references, ObjectReference[] unresolved)
    {
        Scripts = Array.AsReadOnly(scripts);
        References = Array.AsReadOnly(references);
        Unresolved = Array.AsReadOnly(unresolved);
    }

    public IReadOnlyList<Script> Scripts { get; }
    /// <summary>Script assignments on every object in this world, in object order.</summary>
    public IReadOnlyList<ObjectReference> References { get; }
    /// <summary>Assignments whose exact-case name was not found in this world.</summary>
    public IReadOnlyList<ObjectReference> Unresolved { get; }

    /// <summary>Rebuild the snapshot after editing, undoing, reloading or switching levels.</summary>
    public static MissionReferenceIndex Capture(WorldBody body, int maxScripts, int maxReferences)
    {
        if (body == null) throw new ArgumentNullException(nameof(body));
        if (maxScripts < 0) throw new ArgumentOutOfRangeException(nameof(maxScripts));
        if (maxReferences < 0) throw new ArgumentOutOfRangeException(nameof(maxReferences));
        if (body.Scripts.Count > maxScripts) throw new InvalidOperationException("Too many scripts for the mission view.");
        HashSet<string> names = new(StringComparer.Ordinal);
        foreach (var script in body.Scripts) names.Add(script.Name);
        var references = CollectReferences(body.Things.Count, row => ScriptCatalog.ReferencesOf(body, row, names), maxReferences);
        return Assemble(ScriptCatalog.Of(body), references);
    }

    internal static MissionReferenceIndex FromSummaries(
        IReadOnlyList<ScriptSummary> summaries,
        int objectCount,
        Func<int, IReadOnlyList<ScriptReference>> referencesAt,
        int maxScripts,
        int maxReferences)
    {
        if (summaries == null) throw new ArgumentNullException(nameof(summaries));
        if (referencesAt == null) throw new ArgumentNullException(nameof(referencesAt));
        if (objectCount < 0) throw new ArgumentOutOfRangeException(nameof(objectCount));
        if (maxScripts < 0) throw new ArgumentOutOfRangeException(nameof(maxScripts));
        if (maxReferences < 0) throw new ArgumentOutOfRangeException(nameof(maxReferences));
        if (summaries.Count > maxScripts) throw new InvalidOperationException("Too many scripts for the mission view.");

        return Assemble(summaries, CollectReferences(objectCount, referencesAt, maxReferences));
    }

    private static List<ObjectReference> CollectReferences(int objectCount,
        Func<int, IReadOnlyList<ScriptReference>> referencesAt, int maxReferences)
    {
        var references = new List<ObjectReference>();
        for (int row = 0; row < objectCount; row++)
        {
            var assignments = referencesAt(row) ?? throw new InvalidOperationException("Object assignments are unavailable.");
            if (assignments.Count > maxReferences - references.Count)
                throw new InvalidOperationException("Too many object assignments for the mission view.");
            foreach (var assignment in assignments)
            {
                var reference = new ObjectReference(row, assignment.Role, assignment.Name, assignment.Resolved);
                references.Add(reference);
            }
        }
        return references;
    }

    private static MissionReferenceIndex Assemble(IReadOnlyList<ScriptSummary> summaries, List<ObjectReference> references)
    {
        var unresolved = new List<ObjectReference>();
        foreach (var reference in references)
            if (!reference.Resolved) unresolved.Add(reference);
        var scripts = new Script[summaries.Count];
        for (int i = 0; i < scripts.Length; i++) scripts[i] = new Script(i, summaries[i]);
        return new MissionReferenceIndex(scripts, references.ToArray(), unresolved.ToArray());
    }

    private static IReadOnlyList<T> Copy<T>(IReadOnlyList<T> items)
    {
        if (items == null) throw new InvalidOperationException("Script details are unavailable.");
        var copy = new T[items.Count];
        for (int i = 0; i < copy.Length; i++) copy[i] = items[i];
        return Array.AsReadOnly(copy);
    }
}
