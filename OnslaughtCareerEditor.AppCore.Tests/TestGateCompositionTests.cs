using System.Text.RegularExpressions;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// Guards the composition of the npm test gates themselves. The root
    /// package.json selects tests by FullyQualifiedName substring, so renaming a
    /// test class silently shrinks the gate without failing anything; this suite
    /// makes that failure loud, and pins the two gate properties the UX campaign
    /// depends on (the static UI sweep stays in the default gate, and the
    /// runtime sweep stays reachable by script).
    /// </summary>
    public class TestGateCompositionTests
    {
        private static readonly string[] TestSourceRoots =
        {
            "OnslaughtCareerEditor.AppCore.Tests",
            "OnslaughtCareerEditor.UiTests",
            Path.Combine("rebuild", "OnslaughtRebuild.Core.Tests"),
            Path.Combine("rebuild", "OnslaughtRebuild.Client.Tests"),
        };

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
        public void TheDefaultGateKeepsTheStaticUiSweepAndTheRuntimeSweepStaysScripted()
        {
            string packageJson = File.ReadAllText(Path.Combine(FindRepoRoot(), "package.json"));

            Assert.Contains("TestCategory!=WinUIRuntime", packageJson);
            Assert.Contains("\"test:ui-runtime\"", packageJson);
            Assert.Contains("TestCategory=WinUIRuntime", packageJson);

            // The default gate must not regress to a single-class UI filter: the
            // UiTests invocation inside "test" has to be the category exclusion,
            // not a FullyQualifiedName pick.
            Match uiInvocation = Regex.Match(
                packageJson,
                "OnslaughtCareerEditor\\.UiTests\\.csproj[^&]*--filter \\\\\"([^\\\\]+)\\\\\"");
            Assert.True(uiInvocation.Success, "The default gate should run OnslaughtCareerEditor.UiTests with an explicit --filter.");
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
