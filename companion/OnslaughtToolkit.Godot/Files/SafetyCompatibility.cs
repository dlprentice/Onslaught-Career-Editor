// SPDX-License-Identifier: MIT
namespace OnslaughtCareerEditor.AppCore;

// Compile-time adapters for the two linked safety files, not another save codec.
// The companion's career codec validates the format; this constant bounds the protected I/O payload.
internal static class BesFilePatcher
{
    internal const int EXPECTED_FILE_SIZE = 10004;
}

// The protected adapter never enters the legacy profile/default-output creation lanes.
// A user must choose an existing folder for every separately published copy.
internal static class AppConfig
{
    internal static string GetGameProfilesDir() =>
        throw new NotSupportedException("The protected save adapter does not manage game profiles.");

    internal static string GetPatchedOutputDir() =>
        throw new NotSupportedException("Choose an existing folder for the new copy.");
}
