// SPDX-License-Identifier: GPL-3.0-only
using System.Text.RegularExpressions;
using System.Text.Json;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// Guards the AppCore gate and name-filter reachability in package.json.
    /// </summary>
    public class TestGateCompositionTests
    {
        private static readonly string[] TestSourceRoots =
        {
            "OnslaughtCareerEditor.AppCore.Tests",
            Path.Combine("rebuild", "OnslaughtRebuild.Core.Tests"),
            Path.Combine("rebuild", "OnslaughtRebuild.Client.Tests"),
        };

        /// <summary>
        /// test:appcore runs the whole AppCore test project, so no suite can fall outside it.
        /// </summary>
        [Fact]
        public void TheAppCoreGateRunsEveryAppCoreTest()
        {
            using JsonDocument package = JsonDocument.Parse(
                File.ReadAllText(Path.Combine(FindRepoRoot(), "package.json")));
            string gate = package.RootElement.GetProperty("scripts").GetProperty("test:appcore").GetString()!;
            Assert.Contains("OnslaughtCareerEditor.AppCore.Tests.csproj", gate);
            Assert.DoesNotContain("--filter", gate);
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

        private static string FindRepoRoot()
        {
            DirectoryInfo? current = new(AppContext.BaseDirectory);
            while (current is not null)
            {
                if (File.Exists(Path.Combine(current.FullName, "package.json")) &&
                    File.Exists(Path.Combine(current.FullName, "OnslaughtCareerEditor.AppCore", "OnslaughtCareerEditor.AppCore.csproj")))
                {
                    return current.FullName;
                }

                current = current.Parent;
            }

            throw new DirectoryNotFoundException("Could not locate the repository root for the gate composition tests.");
        }
    }
}
