using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using OnslaughtCareerEditor.AppCore;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// Steam root discovery used to be a hardcoded C:/D:/E: guess list, so an
    /// install on any other drive was undiscoverable. These tests pin the two
    /// properties that matter and are true on any machine: the registry lookup
    /// is total (it never throws and never emits junk), and the test-only
    /// environment override still short-circuits it so the rest of the suite
    /// stays hermetic.
    /// </summary>
    public class SteamRootDiscoveryTests
    {
        private const string SteamRootCandidatesEnvironmentVariable = "ONSLAUGHT_STEAM_ROOT_CANDIDATES";
        private const string GameDirectoryCandidatesEnvironmentVariable = "ONSLAUGHT_GAME_DIR_CANDIDATES";

        [Fact]
        public void RegistryLookupIsTotal_AndNeverYieldsMalformedPaths()
        {
            // Machine-independent: the registry may hold nothing, but whatever
            // it does hold must be usable as a path without further cleanup.
            List<string> roots = AppConfig.GetRegistrySteamRoots().ToList();

            Assert.All(roots, root =>
            {
                Assert.False(string.IsNullOrWhiteSpace(root));
                Assert.Equal(root.Trim(), root);
                // Steam stores "c:/program files (x86)/steam"; callers combine
                // these with Path.Combine, so the separator must be normalized.
                Assert.DoesNotContain('/', root);
            });
        }

        [Fact]
        public void RegistryLookupIsRepeatable()
        {
            Assert.Equal(
                AppConfig.GetRegistrySteamRoots().ToList(),
                AppConfig.GetRegistrySteamRoots().ToList());
        }

        [Fact]
        public void TheEnvironmentOverridesStillWin_SoTestsStayHermetic()
        {
            // Detection has two independent override points: a direct list of
            // game-directory candidates, and the Steam roots whose
            // libraryfolders.vdf is scanned. Both must short-circuit their
            // built-in guesses - including the registry lookup - or a developer
            // machine with Steam installed silently resolves a real install
            // inside tests that are supposed to see only fixtures.
            string? originalGameDirs = Environment.GetEnvironmentVariable(GameDirectoryCandidatesEnvironmentVariable);
            string? originalSteamRoots = Environment.GetEnvironmentVariable(SteamRootCandidatesEnvironmentVariable);
            string emptyRoot = Path.Combine(Path.GetTempPath(), $"onslaught-steam-root-probe-{Guid.NewGuid():N}");

            try
            {
                // Empty (not unset) means "no direct candidates", which leaves
                // only the Steam-library path - pointed at a folder that does
                // not exist, so nothing can be discovered.
                Environment.SetEnvironmentVariable(GameDirectoryCandidatesEnvironmentVariable, string.Empty);
                Environment.SetEnvironmentVariable(SteamRootCandidatesEnvironmentVariable, emptyRoot);

                Assert.Null(AppConfig.DetectGameDirectory());
            }
            finally
            {
                Environment.SetEnvironmentVariable(GameDirectoryCandidatesEnvironmentVariable, originalGameDirs);
                Environment.SetEnvironmentVariable(SteamRootCandidatesEnvironmentVariable, originalSteamRoots);
            }
        }
    }
}
