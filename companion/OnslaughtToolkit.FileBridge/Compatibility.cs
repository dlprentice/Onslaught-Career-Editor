namespace OnslaughtCareerEditor.AppCore;

// Compile-time adapters for the two linked safety files, not a save codec.
// GDScript owns the format. The native boundary only bounds the supported payload.
internal static class BesFilePatcher
{
    internal const int EXPECTED_FILE_SIZE = 10004;
}

// The file bridge cannot create profile or default-output directories. A caller
// must select an existing directory; the unrelated AppCore lanes fail closed.
internal static class AppConfig
{
    internal static string GetGameProfilesDir() =>
        throw new NotSupportedException("The file bridge does not manage game profiles.");

    internal static string GetPatchedOutputDir() =>
        throw new NotSupportedException("Choose an existing folder for the new copy.");
}
