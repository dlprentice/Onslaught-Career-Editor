using System.Security.Cryptography;

namespace OnslaughtCareerEditor.AppCore;

/// <summary>A validated input snapshot. Its bytes are never exposed for mutation.</summary>
public sealed class SaveLabSession
{
    private readonly byte[] _bytes;
    internal SaveLabSession(string inputPath, byte[] bytes, string identity)
    {
        InputPath = inputPath;
        _bytes = bytes.ToArray();
        Identity = identity;
        InputSha256 = Convert.ToHexString(SHA256.HashData(_bytes));
    }

    public string InputPath { get; }
    public string InputSha256 { get; }
    public int FileSize => _bytes.Length;
    // The existing analysis DTO is mutable; return a fresh analysis so UI changes cannot alter the plan.
    public SaveAnalysis Analysis => BesFilePatcher.AnalyzeBytes(_bytes, InputPath);
    internal string Identity { get; }
    internal ReadOnlySpan<byte> Bytes => _bytes;
}

public sealed record SaveLabOpenResult(bool Success, string Message, SaveLabSession? Session);

public sealed record SaveLabWriteResult(
    bool Success,
    string Message,
    string? OutputPath = null,
    string? OutputSha256 = null,
    SaveAnalysis? Analysis = null,
    int ChangedBytes = 0,
    bool OriginalVerified = false,
    bool UntargetedBytesVerified = false);

/// <summary>The first companion workflow: one explicit kill-count change to a new, verified copy.</summary>
public static class SaveLabService
{
    public const int MaximumKillCount = 0x00FFFFFF;

    public static SaveLabOpenResult Open(string inputPath)
    {
        try
        {
            string path = NormalizeCareerPath(inputPath);
            using SaveLabSource source = SaveLabSource.Open(path);
            byte[] bytes = source.ReadBytes();
            SaveAnalysis analysis = BesFilePatcher.AnalyzeBytes(bytes, path);
            if (!analysis.IsValid)
                return new(false, analysis.ErrorMessage ?? "That career save is not supported.", null);
            source.Verify(bytes, source.Identity);
            return new(true, "Career save opened. Choose one kill count to change in a separate copy.",
                new SaveLabSession(path, bytes, source.Identity));
        }
        catch (Exception error) when (IsExpectedFailure(error))
        {
            return new(false, DescribeFailure(error), null);
        }
    }

    public static SaveLabWriteResult WriteKillCountCopy(
        SaveLabSession session, string outputPath, int category, int kills)
        => WriteKillCountCopy(session, outputPath, category, kills, beforePublish: null);

    internal static SaveLabWriteResult WriteKillCountCopy(
        SaveLabSession session, string outputPath, int category, int kills, Action? beforePublish, Action? afterPublish = null)
    {
        string? publishedOutput = null;
        try
        {
            ArgumentNullException.ThrowIfNull(session);
            if (category is < BesFilePatcher.KILL_AIRCRAFT or > BesFilePatcher.KILL_MECHS)
                throw new InvalidOperationException("Choose one of the five kill categories.");
            if (kills is < 0 or > MaximumKillCount)
                throw new InvalidOperationException($"Kill counts must be from 0 to {MaximumKillCount:N0}.");
            string output = NormalizeCareerPath(outputPath);
            if (FileMutationSafety.AreLexicallySamePath(session.InputPath, output))
                throw new InvalidOperationException("Choose a new output file different from the original.");
            if (session.Analysis.KillCounts[category] == kills)
                throw new InvalidOperationException("Choose a different kill count before writing a copy.");

            // Both the retained patch API and this workflow execute PatchBuffer's existing byte passes.
            BesFilePatcher patcher = new()
            {
                PatchNodes = false,
                PatchLinks = false,
                PatchGoodies = false,
                PatchKills = true,
                GlobalKillCount = null,
                PerCategoryKills = new Dictionary<int, int> { [category] = kills }
            };
            byte[] expected = patcher.CreatePatchedBytes(session.Bytes);
            int changed = VerifySelectedChange(session.Bytes, expected, category, kills);

            using SaveLabSource source = SaveLabSource.Open(session.InputPath);
            source.Verify(session.Bytes, session.Identity);
            byte[] reopened = SaveLabFileTransaction.PublishNew(output, source, expected, session.Bytes,
                session.Identity, beforePublish);
            publishedOutput = output;
            afterPublish?.Invoke();
            source.Verify(session.Bytes, session.Identity);
            if (!reopened.AsSpan().SequenceEqual(expected))
                throw new IOException("The new copy did not match the prepared save bytes.");
            VerifySelectedChange(session.Bytes, reopened, category, kills);
            SaveAnalysis analysis = BesFilePatcher.AnalyzeBytes(reopened, output);
            return new(true,
                "Copy reopened and verified. The original, other categories, packed byte and all remaining bytes match the opened save.",
                output, Convert.ToHexString(SHA256.HashData(reopened)), analysis, changed,
                OriginalVerified: true, UntargetedBytesVerified: true);
        }
        catch (Exception error) when (IsExpectedFailure(error))
        {
            if (error is SaveLabPublicationException publication)
                return new(false, publication.Message, publication.OutputPath);
            if (publishedOutput is not null)
                return new(false, "A new copy exists, but final verification failed. Inspect it before using it. "
                    + DescribeFailure(error), publishedOutput);
            return new(false, DescribeFailure(error));
        }
    }

    private static int VerifySelectedChange(ReadOnlySpan<byte> original, byte[] output, int category, int kills)
    {
        SaveAnalysis analysis = BesFilePatcher.AnalyzeBytes(output);
        if (!analysis.IsValid || output.Length != original.Length || analysis.KillCounts[category] != kills)
            throw new IOException("The prepared copy failed career-save verification.");
        // The count is only the low 24 bits; the packed high byte is outside the allowed change.
        int start = BesFilePatcher.KillCountFileOffset(category);
        int changed = 0;
        for (int offset = 0; offset < original.Length; offset++)
        {
            if (original[offset] == output[offset])
                continue;
            if (offset < start || offset >= start + 3)
                throw new IOException("The copy changed bytes outside the selected kill count.");
            changed++;
        }
        if (changed == 0)
            throw new InvalidOperationException("Choose a different kill count before writing a copy.");
        return changed;
    }

    private static string NormalizeCareerPath(string path)
    {
        if (!SaveEditorService.IsCareerSaveFilePath(path))
            throw new InvalidOperationException("Choose a .bes career save file.");
        return FileMutationSafety.NormalizeLocalPath(path, "Career save");
    }

    private static bool IsExpectedFailure(Exception error) => error is IOException or UnauthorizedAccessException
        or ArgumentException or InvalidOperationException or NotSupportedException or System.Security.SecurityException
        or System.ComponentModel.Win32Exception or EntryPointNotFoundException or DllNotFoundException;

    private static string DescribeFailure(Exception error) => error switch
    {
        FileNotFoundException => "That career save could not be found. Open the save again.",
        DirectoryNotFoundException => "Choose an existing folder for the new copy.",
        UnauthorizedAccessException => "The selected file or folder could not be accessed.",
        EntryPointNotFoundException or DllNotFoundException => "This system lacks the file protections required to write a verified copy.",
        _ => error.Message
    };
}
