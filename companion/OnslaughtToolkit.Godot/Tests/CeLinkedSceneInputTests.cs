// SPDX-License-Identifier: GPL-3.0-only
using System.Runtime.InteropServices;
using OnslaughtToolkit.Companion.Assets;
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Missions;

namespace OnslaughtToolkit.Companion.Tests;

/// <summary>What the linked preview admits from a chosen game folder, on authored bytes only: a file's kind and size decide before any read.</summary>
internal static class CeLinkedSceneInputTests
{
    private static readonly TimeSpan Wait = TimeSpan.FromSeconds(10);

    [DllImport("libc", EntryPoint = "mkfifo", SetLastError = true)]
    private static extern int MakeFifo([MarshalAs(UnmanagedType.LPUTF8Str)] string path, uint mode);

    internal static bool MakePipe(string path) => MakeFifo(path, 0x180) == 0; // 0600

    /// <summary>A reader stuck in the open of a pipe needs a writer to go on; this one lets it return so the run can end and report the failure.</summary>
    internal static void ReleaseReader(string pipe)
    {
        using (File.OpenHandle(pipe, FileMode.Open, FileAccess.Write)) { }
    }

    internal static void Run(string root, Checks check)
    {
        if (!OperatingSystem.IsLinux()) return;
        check.Suite("linked-map selected files");
        string game = Path.Combine(root, "selected-files"), resources = Path.Combine(game, "data", "resources"),
            meshes = Path.Combine(resources, "meshes"), worlds = Path.Combine(game, "data", "worlds"),
            archive = Path.Combine(resources, "777_res_pc.aya"), model = Path.Combine(meshes, "m_authored.msh.aya"),
            world = Path.Combine(worlds, "world777.wrd"), outside = Path.Combine(root, "selected-files-outside.bin");
        Directory.CreateDirectory(meshes); Directory.CreateDirectory(worlds);
        CeMissionProject project = CeLinkedSceneTests.Project(new(12, 13, -4));
        byte[] body = CeLinkedSceneTests.AnchorBody().Write(), modelBytes = AssetTests.Member(AssetTests.TwoPartMesh());
        byte[] ownWorld = CeLinkedSceneTests.Archive(body), looseWorld = CeLinkedSceneTests.Archive(null);
        File.WriteAllBytes(outside, ownWorld);
        File.WriteAllBytes(archive, ownWorld);
        File.WriteAllBytes(model, modelBytes);

        Input("the level archive", archive, ownWorld, LevelArchive.MaxFileBytes);
        Input("a referenced model", model, modelBytes, CeLinkedSceneLoader.MaxMeshBytes);
        File.WriteAllBytes(archive, looseWorld);
        File.WriteAllBytes(world, body);
        Input("a loose level world", world, body, CeLinkedSceneLoader.MaxWorldBytes);

        void Input(string label, string path, byte[] bytes, int limit)
        {
            check.That(Outcome(game, project) is null, label + ": the complete folder loads, so each refusal below comes from this one file");

            File.Delete(path);
            check.That(MakePipe(path), label + ": a named pipe could be made for the test");
            Task<Exception?> reading = Task.Run(() => Outcome(game, project));
            bool returned = reading.Wait(Wait);
            if (!returned) { ReleaseReader(path); reading.Wait(Wait); }
            check.That(returned && Refused(reading.Result, "must be a regular file"), label + ": a named pipe is refused without waiting for a writer");
            File.Delete(path);

            if (!Environment.IsPrivilegedProcess)
            {
                File.WriteAllBytes(path, bytes);
                File.SetUnixFileMode(path, UnixFileMode.None);
                check.That(Outcome(game, project) is IOException or UnauthorizedAccessException, label + ": an unreadable file is a reported refusal");
                File.Delete(path);
            }

            using (FileStream sparse = new(path, FileMode.CreateNew, FileAccess.Write)) sparse.SetLength(limit + 1L);
            check.That(Refused(Outcome(game, project), "exceeds its byte limit"), label + ": one byte over its limit is refused before any of it is read");
            File.Delete(path);

            File.WriteAllBytes(path, []);
            check.That(Refused(Outcome(game, project), "exceeds its byte limit"), label + ": an empty file is refused");
            File.Delete(path);

            File.CreateSymbolicLink(path, outside);
            check.That(Refused(Outcome(game, project), "may not be a link"), label + ": a link is refused even when its target is a regular file");
            File.Delete(path);

            File.WriteAllBytes(path, bytes);
            check.That(Outcome(game, project) is null && File.ReadAllBytes(path).AsSpan().SequenceEqual(bytes),
                label + ": the same path loads again as a regular file and is left unchanged");
        }
    }

    private static bool Refused(Exception? error, string reason) => error is InvalidDataException && error.Message.Contains(reason, StringComparison.Ordinal);

    private static Exception? Outcome(string game, CeMissionProject project)
    {
        try { _ = CeLinkedSceneLoader.Load(game, project); return null; }
        catch (Exception error) { return error; }
    }
}
