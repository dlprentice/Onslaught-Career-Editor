// SPDX-License-Identifier: GPL-3.0-only
using System.Text.Json;

namespace OnslaughtToolkit.Companion.Levels;

internal sealed record EditorProjectState(EditorProjectIdentity Basis, string World, string Terrain);

internal sealed class PreparedEditorProject(LevelEditorModel owner, EditSession expectedSession, long revision,
    TerrainDraft? expectedTerrain, EditorProjectState expectedState, RestoredEditorProject restored, string restoredHash,
    IReadOnlyList<ScriptEntry> entries)
{
    internal LevelEditorModel Owner { get; } = owner;
    internal EditSession ExpectedSession { get; } = expectedSession;
    internal long Revision { get; } = revision;
    internal TerrainDraft? ExpectedTerrain { get; } = expectedTerrain;
    internal EditorProjectState ExpectedState { get; } = expectedState;
    internal RestoredEditorProject Restored { get; } = restored;
    internal string RestoredHash { get; } = restoredHash;
    internal IReadOnlyList<ScriptEntry> Entries { get; } = entries;
}

public sealed partial class LevelEditorModel
{
    private long _revision;

    private void AnnounceChange()
    {
        _revision++;
        Changed?.Invoke();
    }

    private EditorProjectBase? ProjectBase() => Session is { } session && Worlds is { RealBody: { } anchor } worlds && Level is int level
        ? new EditorProjectBase(level, false, worlds.BaseLevel, session.IsBaseWorld, session.Baseline, anchor, worlds.BaseBody, worlds.Terrain) : null;

    internal byte[] CaptureProject(IReadOnlyList<EditorProjectScript> scripts) => ProjectBase() is { } basis && Session is { } session
        ? EditorProject.Capture(basis, session, _terrainDraft, scripts) : throw new InvalidDataException("Choose the project's base level first.");

    internal EditorProjectState ProjectState()
    {
        if (ProjectBase() is not { } basis || Session is not { } session) throw new InvalidDataException("Choose a level first.");
        return new(EditorProject.Identity(basis), EditorProject.Hash(session.ToBytes()),
            JsonSerializer.Serialize(_terrainDraft is { } terrain ? new { terrain.Baseline.Divisions, Points = terrain.Offsets() } : null));
    }

    internal bool TryPrepareProject(ReadOnlyMemory<byte> bytes, out PreparedEditorProject? prepared, out string message)
    {
        prepared = null;
        if (ProjectBase() is not { } basis || Session is not { } session || Worlds is not { } worlds)
        {
            message = "Choose the project's base level first.";
            return false;
        }
        try
        {
            RestoredEditorProject restored = EditorProject.Restore(bytes, basis);
            IReadOnlyList<ScriptEntry> entries = ListScripts(restored.Session.Body, worlds);
            string hash = EditorProject.Hash(EditorProject.Capture(basis, restored.Session, restored.Terrain, restored.Scripts));
            prepared = new(this, session, _revision, _terrainDraft, ProjectState(), restored, hash, entries);
            message = "The editor project matches the selected base level. Opening starts a fresh undo history.";
            return true;
        }
        catch (Exception error) when (ProjectFailure(error))
        {
            message = error is InvalidDataException ? error.Message : "The editor project could not be checked safely. The current edit was kept.";
            return false;
        }
    }

    internal bool CanCommitProject(PreparedEditorProject prepared)
    {
        if (!ReferenceEquals(prepared.Owner, this) || !ReferenceEquals(Session, prepared.ExpectedSession) || prepared.Revision != _revision ||
            !ReferenceEquals(_terrainDraft, prepared.ExpectedTerrain) || prepared.Restored.Session.CanUndo || prepared.Restored.Session.CanRedo) return false;
        try
        {
            return ProjectBase() is { } basis && prepared.ExpectedState == ProjectState() &&
                EditorProject.Hash(EditorProject.Capture(basis, prepared.Restored.Session, prepared.Restored.Terrain, prepared.Restored.Scripts)) == prepared.RestoredHash;
        }
        catch (Exception error) when (ProjectFailure(error)) { return false; }
    }

    /// <summary>The page suppresses notifications until its prepared script state has also been installed.</summary>
    internal bool CommitProject(PreparedEditorProject prepared, bool notify = true)
    {
        if (!CanCommitProject(prepared) || Worlds is not { } worlds) return false;
        EditSession replacement = prepared.Restored.Session;
        // The panel prepared these same entry objects; its selection must remain an owned model entry.
        IReadOnlyList<ScriptEntry> entries = prepared.Entries;
        replacement.Changed += () =>
        {
            if (!ReferenceEquals(Session, replacement)) return;
            RefreshScripts();
            AnnounceChange();
        };
        Session = replacement;
        Scripts = entries;
        _terrainDraft = prepared.Restored.Terrain;
        _savedSignature = null;
        Problem = null;
        _revision++;
        if (notify) Changed?.Invoke();
        return true;
    }

    internal void AnnounceProjectOpened() => Changed?.Invoke();
    private static bool ProjectFailure(Exception error) => error is IOException or UnauthorizedAccessException or ArgumentException or NotSupportedException || EditSession.IsUnstorable(error);
}
