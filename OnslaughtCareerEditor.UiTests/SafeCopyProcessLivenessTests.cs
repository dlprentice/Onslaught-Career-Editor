using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using NUnit.Framework;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The "Windowed &amp; Mods" page polls these queries to notice that a copied game ended on
/// its own, instead of staying wedged until someone presses Stop on a process that no
/// longer exists. These live in the default gate because the guard they encode - a process
/// id alone is never proof of identity, because Windows recycles process ids - is the part
/// that must never quietly regress.
/// </summary>
[TestFixture]
public sealed class SafeCopyProcessLivenessTests
{
    [Test]
    public void ALeaseWhoseProcessIdIsGoneIsDead()
    {
        GameProfileManagedProcess record = BuildRecord();

        Assert.That(
            GameProfileRuntimeService.IsManagedProcessLive(record, NoProcessProbe()),
            Is.False,
            "No process holds that id, so the record cannot be live.");
    }

    [Test]
    public void ALeaseWhoseProcessIdWasRecycledIsDeadBecauseTheStartTimeDiffers()
    {
        GameProfileManagedProcess record = BuildRecord();

        // The dangerous case: the id is in use again and the path on disk still matches,
        // because the app-owned safe copy folder is right where it always was. Only the
        // start time separates "our copied game" from "somebody else's process".
        var recycled = new StubLivenessProbe(record.StartedAt.AddSeconds(30), record.ExecutablePath);

        Assert.That(
            GameProfileRuntimeService.IsManagedProcessLive(record, recycled),
            Is.False,
            "A recycled process id must not be mistaken for the managed process.");

        Assert.Multiple(() =>
        {
            // Tick-level, in both directions, and however small the gap.
            Assert.That(GameProfileRuntimeService.IsManagedProcessLive(record, new StubLivenessProbe(record.StartedAt.AddTicks(1), record.ExecutablePath)), Is.False);
            Assert.That(GameProfileRuntimeService.IsManagedProcessLive(record, new StubLivenessProbe(record.StartedAt.AddTicks(-1), record.ExecutablePath)), Is.False);
            Assert.That(GameProfileRuntimeService.IsManagedProcessLive(record, new StubLivenessProbe(record.StartedAt.AddHours(-4), record.ExecutablePath)), Is.False);
        });
    }

    [Test]
    public void ALeaseRunningADifferentExecutableIsDeadEvenWhenTheStartTimeMatches()
    {
        GameProfileManagedProcess record = BuildRecord();

        Assert.Multiple(() =>
        {
            Assert.That(
                GameProfileRuntimeService.IsManagedProcessLive(
                    record,
                    new StubLivenessProbe(record.StartedAt, Path.Combine(Path.GetTempPath(), "somewhere-else", "BEA.exe"))),
                Is.False);
            Assert.That(
                GameProfileRuntimeService.IsManagedProcessLive(record, new StubLivenessProbe(record.StartedAt, null)),
                Is.False,
                "An unreadable module path is not proof of identity.");
        });
    }

    [Test]
    public void AGenuinelyLiveLeaseIsAlive()
    {
        GameProfileManagedProcess record = BuildRecord();

        Assert.Multiple(() =>
        {
            Assert.That(
                GameProfileRuntimeService.IsManagedProcessLive(
                    record,
                    new StubLivenessProbe(record.StartedAt, record.ExecutablePath)),
                Is.True);

            // The same executable reached by a different but equivalent spelling of the
            // path is still the same executable.
            Assert.That(
                GameProfileRuntimeService.IsManagedProcessLive(
                    record,
                    new StubLivenessProbe(record.StartedAt, record.ExecutablePath.ToUpperInvariant())),
                Is.True);
            Assert.That(
                GameProfileRuntimeService.IsManagedProcessLive(
                    record,
                    new StubLivenessProbe(record.StartedAt.ToOffset(TimeSpan.Zero), record.ExecutablePath)),
                Is.True,
                "The same instant expressed in another offset is the same start time.");
        });
    }

    /// <summary>
    /// The distinction Home got wrong: what was written down, versus what is running.
    ///
    /// Leases are persisted, so one outlives the game being quit from its own menu, the game
    /// crashing, and the whole app being restarted. Home asked Snapshot() whether a copy was
    /// running and therefore said yes indefinitely - and offered a Stop button that stopped
    /// nothing, because there was nothing to stop.
    /// </summary>
    [Test]
    public void SnapshotLiveReportsWhatIsRunningWhileSnapshotReportsWhatWasWrittenDown()
    {
        string profilesRoot = CreateTempProfilesRoot();

        try
        {
            string leasePath = Path.Combine(profilesRoot, GameProfileManagedProcessRegistry.LeaseFileName);
            GameProfileManagedProcess record = SeedSafeCopy(profilesRoot, "safe-game-copy-live", processId: 5150);

            var registry = new GameProfileManagedProcessRegistry(leasePath);
            registry.Register(record, profilesRoot);

            var running = new StubLivenessProbe(record.StartedAt, record.ExecutablePath);
            Assert.Multiple(() =>
            {
                Assert.That(registry.Snapshot().Count, Is.EqualTo(1));
                Assert.That(registry.SnapshotLive(running).Count, Is.EqualTo(1), "A running copy is live.");
            });

            // The game has gone, and nothing has pruned the lease yet - the state Home was in.
            Assert.Multiple(() =>
            {
                Assert.That(registry.Snapshot().Count, Is.EqualTo(1), "The lease is still on record.");
                Assert.That(registry.SnapshotLive(NoProcessProbe()), Is.Empty, "But nothing is running.");
            });

            // Read-only, like TryResolveLiveManagedProcess: asking must not prune.
            Assert.That(registry.Snapshot().Count, Is.EqualTo(1), "SnapshotLive must not delete leases.");
            Assert.That(File.Exists(record.ExecutablePath), Is.True, "...nor touch the copy.");
        }
        finally
        {
            DeleteTempRoot(profilesRoot);
        }
    }

    /// <summary>
    /// A recycled process id must not read as the game coming back to life.
    /// </summary>
    [Test]
    public void SnapshotLiveRejectsARecycledProcessId()
    {
        string profilesRoot = CreateTempProfilesRoot();

        try
        {
            string leasePath = Path.Combine(profilesRoot, GameProfileManagedProcessRegistry.LeaseFileName);
            GameProfileManagedProcess record = SeedSafeCopy(profilesRoot, "safe-game-copy-recycled", processId: 6060);

            var registry = new GameProfileManagedProcessRegistry(leasePath);
            registry.Register(record, profilesRoot);

            var recycled = new StubLivenessProbe(record.StartedAt.AddSeconds(30), record.ExecutablePath);

            Assert.That(registry.SnapshotLive(recycled), Is.Empty);
        }
        finally
        {
            DeleteTempRoot(profilesRoot);
        }
    }

    [Test]
    public void PruningDropsOnlyDeadLeasesAndNeverStopsOrDeletesAnything()
    {
        string profilesRoot = CreateTempProfilesRoot();

        try
        {
            string leasePath = Path.Combine(profilesRoot, GameProfileManagedProcessRegistry.LeaseFileName);
            GameProfileManagedProcess record = SeedSafeCopy(profilesRoot, "safe-game-copy-live", processId: 4242);

            var registry = new GameProfileManagedProcessRegistry(leasePath);
            registry.Register(record, profilesRoot);

            var stillRunning = new StubLivenessProbe(record.StartedAt, record.ExecutablePath);
            Assert.Multiple(() =>
            {
                Assert.That(registry.PruneDeadLeases(stillRunning), Is.Empty);
                Assert.That(registry.Snapshot().Count, Is.EqualTo(1));
                Assert.That(registry.TryResolveLiveManagedProcess(out _, stillRunning), Is.True);
            });

            IReadOnlyList<GameProfileRegisteredProcess> pruned = registry.PruneDeadLeases(NoProcessProbe());

            Assert.Multiple(() =>
            {
                Assert.That(pruned.Select(row => row.Process.ProcessId), Is.EqualTo(new[] { record.ProcessId }));
                Assert.That(registry.Snapshot(), Is.Empty);
                Assert.That(registry.TryResolveLiveManagedProcess(out _, NoProcessProbe()), Is.False);

                // A new session must not resurrect the dead lease from disk...
                Assert.That(new GameProfileManagedProcessRegistry(leasePath).Snapshot(), Is.Empty);

                // ...and the safe copy itself is never touched by a liveness sweep.
                Assert.That(File.Exists(record.ExecutablePath), Is.True);
                Assert.That(File.Exists(record.ManifestPath), Is.True);
            });
        }
        finally
        {
            DeleteTempRoot(profilesRoot);
        }
    }

    [Test]
    public void ResolvingALiveProcessSkipsARecycledIdAndReturnsTheOneStillRunning()
    {
        string profilesRoot = CreateTempProfilesRoot();

        try
        {
            string leasePath = Path.Combine(profilesRoot, GameProfileManagedProcessRegistry.LeaseFileName);
            GameProfileManagedProcess older = SeedSafeCopy(
                profilesRoot,
                "safe-game-copy-older",
                processId: 111,
                startedAt: DateTimeOffset.UtcNow.AddMinutes(-30));
            GameProfileManagedProcess newer = SeedSafeCopy(
                profilesRoot,
                "safe-game-copy-newer",
                processId: 222,
                startedAt: DateTimeOffset.UtcNow.AddMinutes(-5));

            var registry = new GameProfileManagedProcessRegistry(leasePath);
            registry.Register(older, profilesRoot);
            registry.Register(newer, profilesRoot);

            // The newest lease is the one whose id got recycled; the older one is the game
            // still on screen. Ordering by "newest first" alone would answer wrongly here.
            var probe = new PerProcessLivenessProbe(new Dictionary<int, GameProfileProcessLivenessProbeResult>
            {
                [older.ProcessId] = new(true, older.StartedAt, older.ExecutablePath),
                [newer.ProcessId] = new(true, newer.StartedAt.AddSeconds(90), newer.ExecutablePath),
            });

            Assert.That(registry.TryResolveLiveManagedProcess(out GameProfileRegisteredProcess live, probe), Is.True);
            Assert.That(live.Process.ProcessId, Is.EqualTo(older.ProcessId));

            IReadOnlyList<GameProfileRegisteredProcess> pruned = registry.PruneDeadLeases(probe);

            Assert.Multiple(() =>
            {
                Assert.That(pruned.Select(row => row.Process.ProcessId), Is.EqualTo(new[] { newer.ProcessId }));
                Assert.That(registry.Snapshot().Select(row => row.Process.ProcessId), Is.EqualTo(new[] { older.ProcessId }));
            });
        }
        finally
        {
            DeleteTempRoot(profilesRoot);
        }
    }

    private static IGameProfileProcessLivenessProbe NoProcessProbe() => new StubLivenessProbe();

    private static GameProfileManagedProcess BuildRecord()
    {
        string safeCopyRoot = Path.Combine(Path.GetTempPath(), "onslaught-liveness", "safe-game-copy");
        return new GameProfileManagedProcess(
            ProcessId: 4242,
            ExecutablePath: Path.Combine(safeCopyRoot, "BEA.exe"),
            WorkingDirectory: safeCopyRoot,
            Arguments: Array.Empty<string>(),
            StartedAt: DateTimeOffset.UtcNow,
            ManifestPath: Path.Combine(safeCopyRoot, "onslaught-profile-manifest.json"));
    }

    private static string CreateTempProfilesRoot()
    {
        string profilesRoot = Path.Combine(Path.GetTempPath(), $"onslaught-liveness-{Guid.NewGuid():N}", "profiles");
        Directory.CreateDirectory(profilesRoot);
        return profilesRoot;
    }

    private static GameProfileManagedProcess SeedSafeCopy(
        string profilesRoot,
        string profileName,
        int processId,
        DateTimeOffset? startedAt = null)
    {
        string safeCopyRoot = Path.Combine(profilesRoot, profileName);
        Directory.CreateDirectory(safeCopyRoot);

        string executablePath = Path.Combine(safeCopyRoot, "BEA.exe");
        string manifestPath = Path.Combine(safeCopyRoot, "onslaught-profile-manifest.json");
        File.WriteAllBytes(executablePath, new byte[] { 0x4D, 0x5A });
        File.WriteAllText(manifestPath, "{}");

        return new GameProfileManagedProcess(
            ProcessId: processId,
            ExecutablePath: executablePath,
            WorkingDirectory: safeCopyRoot,
            Arguments: Array.Empty<string>(),
            StartedAt: startedAt ?? DateTimeOffset.UtcNow,
            ManifestPath: manifestPath);
    }

    private static void DeleteTempRoot(string profilesRoot)
    {
        string? parent = Path.GetDirectoryName(profilesRoot);
        if (!string.IsNullOrWhiteSpace(parent) && Directory.Exists(parent))
        {
            Directory.Delete(parent, recursive: true);
        }
    }

    private sealed class StubLivenessProbe : IGameProfileProcessLivenessProbe
    {
        private readonly GameProfileProcessLivenessProbeResult _result;

        public StubLivenessProbe()
        {
            _result = new GameProfileProcessLivenessProbeResult(false, null, null);
        }

        public StubLivenessProbe(DateTimeOffset startedAt, string? mainModulePath)
        {
            _result = new GameProfileProcessLivenessProbeResult(true, startedAt, mainModulePath);
        }

        public GameProfileProcessLivenessProbeResult Probe(GameProfileManagedProcess process) => _result;
    }

    private sealed class PerProcessLivenessProbe : IGameProfileProcessLivenessProbe
    {
        private readonly IReadOnlyDictionary<int, GameProfileProcessLivenessProbeResult> _resultsByProcessId;

        public PerProcessLivenessProbe(IReadOnlyDictionary<int, GameProfileProcessLivenessProbeResult> resultsByProcessId)
        {
            _resultsByProcessId = resultsByProcessId;
        }

        public GameProfileProcessLivenessProbeResult Probe(GameProfileManagedProcess process)
        {
            return _resultsByProcessId.TryGetValue(process.ProcessId, out GameProfileProcessLivenessProbeResult? result)
                ? result
                : new GameProfileProcessLivenessProbeResult(false, null, null);
        }
    }
}
