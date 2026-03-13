using System;
using System.IO;

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
}
