using System;
using System.Collections.Generic;

namespace OnslaughtToolkit.Companion.Levels;

/// <summary>
/// A bounded, read-only view of the script references the existing catalogue
/// can identify. Resolution is the catalogue's observation, not proof that a
/// mission will run or that every runtime reference is known.
/// </summary>
public sealed class MissionReferenceIndex
{
    public sealed class Script
    {
        internal Script(int index, ScriptSummary summary, IReadOnlyList<ScriptReference> references)
        {
            Index = index;
            Name = summary.Name;
            Events = Copy(summary.Events);
            Calls = Copy(summary.Calls);
            Uses = Copy(summary.Uses);
            References = Copy(references);
        }

        public int Index { get; }
        public string Name { get; }
        public IReadOnlyList<string> Events { get; }
        public IReadOnlyList<NativeCall> Calls { get; }
        public IReadOnlyList<ScriptUse> Uses { get; }
        public IReadOnlyList<ScriptReference> References { get; }
    }

    public readonly record struct UnresolvedReference(int ScriptIndex, string ScriptName, string Role, string Name);

    private MissionReferenceIndex(Script[] scripts, UnresolvedReference[] unresolved)
    {
        Scripts = Array.AsReadOnly(scripts);
        Unresolved = Array.AsReadOnly(unresolved);
    }

    public IReadOnlyList<Script> Scripts { get; }
    public IReadOnlyList<UnresolvedReference> Unresolved { get; }

    /// <summary>Rebuild the snapshot after editing, undoing, reloading or switching levels.</summary>
    public static MissionReferenceIndex Capture(WorldBody body, int maxScripts, int maxReferences)
    {
        if (body == null) throw new ArgumentNullException(nameof(body));
        if (maxScripts < 0) throw new ArgumentOutOfRangeException(nameof(maxScripts));
        if (maxReferences < 0) throw new ArgumentOutOfRangeException(nameof(maxReferences));
        if (body.Scripts.Count > maxScripts) throw new InvalidOperationException("The mission has too many scripts to inspect.");
        return FromSummaries(ScriptCatalog.Of(body), index => ScriptCatalog.ReferencesOf(body, index), maxScripts, maxReferences);
    }

    internal static MissionReferenceIndex FromSummaries(
        IReadOnlyList<ScriptSummary> summaries,
        Func<int, IReadOnlyList<ScriptReference>> referencesAt,
        int maxScripts,
        int maxReferences)
    {
        if (summaries == null) throw new ArgumentNullException(nameof(summaries));
        if (referencesAt == null) throw new ArgumentNullException(nameof(referencesAt));
        if (maxScripts < 0) throw new ArgumentOutOfRangeException(nameof(maxScripts));
        if (maxReferences < 0) throw new ArgumentOutOfRangeException(nameof(maxReferences));
        if (summaries.Count > maxScripts) throw new InvalidOperationException("The mission has too many scripts to inspect.");

        var scripts = new Script[summaries.Count];
        var unresolved = new List<UnresolvedReference>();
        int referenceCount = 0;
        for (int i = 0; i < scripts.Length; i++)
        {
            var references = referencesAt(i) ?? throw new InvalidOperationException("Script references are unavailable.");
            if (references.Count > maxReferences - referenceCount)
                throw new InvalidOperationException("The mission has too many script references to inspect.");
            referenceCount += references.Count;
            var summary = summaries[i];
            scripts[i] = new Script(i, summary, references);
            foreach (var reference in scripts[i].References)
                if (!reference.Resolved)
                    unresolved.Add(new UnresolvedReference(i, summary.Name, reference.Role, reference.Name));
        }
        return new MissionReferenceIndex(scripts, unresolved.ToArray());
    }

    private static IReadOnlyList<T> Copy<T>(IReadOnlyList<T> items)
    {
        if (items == null) throw new InvalidOperationException("Script details are unavailable.");
        var copy = new T[items.Count];
        for (int i = 0; i < copy.Length; i++) copy[i] = items[i];
        return Array.AsReadOnly(copy);
    }
}
