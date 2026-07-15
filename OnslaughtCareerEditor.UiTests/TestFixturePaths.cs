using System;
using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

internal static class TestFixturePaths
{
    internal static string RepoRoot => ResolveRepoRoot(AppContext.BaseDirectory);

    internal static string ResolveRepoRoot(string startDirectory)
    {
        DirectoryInfo? candidate = new(Path.GetFullPath(startDirectory));
        for (int depth = 0; candidate is not null && depth < 12; depth++, candidate = candidate.Parent)
        {
            if (File.Exists(Path.Combine(candidate.FullName, "package.json")) &&
                Directory.Exists(Path.Combine(candidate.FullName, "OnslaughtCareerEditor.WinUI")) &&
                Directory.Exists(Path.Combine(candidate.FullName, "OnslaughtCareerEditor.UiTests")))
            {
                return candidate.FullName;
            }
        }

        throw new DirectoryNotFoundException(
            $"Could not resolve repository root from: {startDirectory}");
    }

    internal static string GoldSavePath => Path.Combine(
        RepoRoot,
        "tests_shared",
        "fixtures",
        "gold_career_save.bin"
    );

    internal static string RequireGoldSavePath()
    {
        if (!File.Exists(GoldSavePath))
        {
            Assert.Ignore(
                "Real-save regression fixture is absent in this checkout. " +
                "Expected tests_shared/fixtures/gold_career_save.bin from the public-primary fixture set."
            );
        }

        return GoldSavePath;
    }
}
