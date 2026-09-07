using System.Text.RegularExpressions;
using System.Text.Json;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// Guards name-filter reachability and the retained Windows UI gate.
    /// The default Linux gate is the Godot companion's supported Save Lab slice.
    /// </summary>
    public class TestGateCompositionTests
    {
        private static readonly string[] TestSourceRoots =
        {
            "OnslaughtCareerEditor.AppCore.Tests",
            "OnslaughtCareerEditor.UiTests",
            "OnslaughtCareerEditor.Cli.Tests",
            Path.Combine("rebuild", "OnslaughtRebuild.Core.Tests"),
            Path.Combine("rebuild", "OnslaughtRebuild.Client.Tests"),
        };

        /// <summary>
        /// Keep the selected AppCore fixtures reachable through the scripted gates.
        /// </summary>
        [Fact]
        public void EveryAppCoreTestClassIsSelectedByAScriptedGate()
        {
            string root = FindRepoRoot();
            string packageJson = File.ReadAllText(Path.Combine(root, "package.json"));
            HashSet<string> tokens = Regex.Matches(packageJson, "FullyQualifiedName~([A-Za-z0-9_.]+)")
                .Select(match => match.Groups[1].Value)
                .ToHashSet(StringComparer.Ordinal);

            var unreachable = new List<string>();
            string directory = Path.Combine(root, "OnslaughtCareerEditor.AppCore.Tests");
            foreach (string file in Directory.GetFiles(directory, "*Tests.cs", SearchOption.AllDirectories))
            {
                if (file.Contains($"{Path.DirectorySeparatorChar}bin{Path.DirectorySeparatorChar}") ||
                    file.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}"))
                {
                    continue;
                }

                string text = File.ReadAllText(file);
                foreach (Match match in Regex.Matches(text, @"public\s+(?:sealed\s+)?class\s+([A-Za-z0-9_]+Tests)\b"))
                {
                    string name = match.Groups[1].Value;

                    // A [Fact] or [Theory] somewhere in the file, or it declares no tests to run.
                    if (!text.Contains("[Fact]", StringComparison.Ordinal) &&
                        !text.Contains("[Theory]", StringComparison.Ordinal))
                    {
                        continue;
                    }

                    if (!tokens.Any(token => name.Contains(token, StringComparison.Ordinal)))
                    {
                        unreachable.Add(name);
                    }
                }
            }

            Assert.True(
                unreachable.Count == 0,
                $"These AppCore test classes are not selected by any npm test filter, so they never "
                    + $"run in a filtered gate: {string.Join(", ", unreachable.Distinct())}. Add a "
                    + "FullyQualifiedName~ token to package.json, or delete the suite.");
        }

        [Fact]
        public void EveryNameFilterTokenInPackageJsonMatchesADeclaredTestClass()
        {
            string root = FindRepoRoot();
            string packageJson = File.ReadAllText(Path.Combine(root, "package.json"));
            List<string> tokens = Regex.Matches(packageJson, "FullyQualifiedName~([A-Za-z0-9_.]+)")
                .Select(match => match.Groups[1].Value)
                .Distinct(StringComparer.Ordinal)
                .ToList();
            Assert.NotEmpty(tokens);

            HashSet<string> declaredClasses = new(StringComparer.Ordinal);
            foreach (string projectRoot in TestSourceRoots)
            {
                string directory = Path.Combine(root, projectRoot);
                if (!Directory.Exists(directory))
                {
                    continue;
                }

                foreach (string file in Directory.GetFiles(directory, "*.cs", SearchOption.AllDirectories))
                {
                    if (file.Contains($"{Path.DirectorySeparatorChar}bin{Path.DirectorySeparatorChar}") ||
                        file.Contains($"{Path.DirectorySeparatorChar}obj{Path.DirectorySeparatorChar}"))
                    {
                        continue;
                    }

                    foreach (Match match in Regex.Matches(File.ReadAllText(file), @"\bclass\s+([A-Za-z0-9_]+)"))
                    {
                        declaredClasses.Add(match.Groups[1].Value);
                    }
                }
            }

            List<string> unmatched = tokens
                .Where(token => !declaredClasses.Any(name => name.Contains(token, StringComparison.Ordinal)))
                .ToList();

            Assert.True(
                unmatched.Count == 0,
                $"package.json test filters reference names no test project declares: {string.Join(", ", unmatched)}. " +
                "A rename silently shrinks the gate; update package.json in the same change.");
        }

        [Fact]
        public void TheRetainedWindowsGateKeepsTheStaticUiSweepAndRuntimeRemainsReachable()
        {
            using JsonDocument package = JsonDocument.Parse(
                File.ReadAllText(Path.Combine(FindRepoRoot(), "package.json")));
            JsonElement scripts = package.RootElement.GetProperty("scripts");
            string windowsGate = scripts.GetProperty("test:winui").GetString()!;
            Assert.Contains("TestCategory=WinUIRuntime", scripts.GetProperty("test:ui-runtime").GetString());

            // Read this command explicitly: JSON property order must not decide
            // whether the static or runtime UI invocation is checked.
            Match uiInvocation = Regex.Match(
                windowsGate,
                "OnslaughtCareerEditor\\.UiTests\\.csproj[^&]*--filter \"([^\"]+)\"");
            Assert.True(uiInvocation.Success, "The retained Windows gate should run OnslaughtCareerEditor.UiTests with an explicit --filter.");
            Assert.Contains("TestCategory!=WinUIRuntime", uiInvocation.Groups[1].Value);
        }

        private static string FindRepoRoot()
        {
            DirectoryInfo? current = new(AppContext.BaseDirectory);
            while (current is not null)
            {
                if (File.Exists(Path.Combine(current.FullName, "package.json")) &&
                    File.Exists(Path.Combine(current.FullName, "OnslaughtCareerEditor.WinUI.slnx")))
                {
                    return current.FullName;
                }

                current = current.Parent;
            }

            throw new DirectoryNotFoundException("Could not locate the repository root for the gate composition tests.");
        }
    }
}
