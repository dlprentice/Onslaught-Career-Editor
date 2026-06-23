using System;
using System.IO;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

internal static class TestFixturePaths
{
    internal static string RepoRoot => Path.GetFullPath(
        Path.Combine(AppContext.BaseDirectory, "..", "..", "..", ".."));

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
                "Private maintainer trees include tests_shared/fixtures/gold_career_save.bin; " +
                "public candidates exclude save-shaped binary payloads."
            );
        }

        return GoldSavePath;
    }
}
