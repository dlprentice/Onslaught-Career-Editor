using System.IO;
using NUnit.Framework;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// Advanced copy used to say a source or destination path is required.
/// Name the file, not a path.
/// </summary>
public class PreflightRequiredFileHonestyTests
{
    [Test]
    public void ABlankSourceNamesTheExecutableNotAPath()
    {
        InvalidOperationException ex = Assert.Throws<InvalidOperationException>(
            () => GameProfilePreflightService.ValidateExecutableSourceForWorkspaceCopy("  "));

        Assert.That(ex.Message, Is.EqualTo("A source executable is required."));
        Assert.That(ex.Message.ToLowerInvariant(), Does.Not.Contain("path"));
    }

    [Test]
    public void ABlankDestinationNamesTheFileNotAPath()
    {
        InvalidOperationException ex = Assert.Throws<InvalidOperationException>(
            () => GameProfilePreflightService.ValidateAppOwnedWorkspaceFileDestination("  ", "root", "BEA.exe"));

        Assert.That(ex.Message, Is.EqualTo("A destination file is required."));
        Assert.That(ex.Message.ToLowerInvariant(), Does.Not.Contain("path"));
    }

    [Test]
    public void TheSourceDoesNotKeepTheOldPathSentences()
    {
        string source = File.ReadAllText(Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.AppCore",
            "GameProfilePreflightService.cs"));

        Assert.That(source, Does.Not.Contain("Executable source path is required."));
        Assert.That(source, Does.Not.Contain("Workspace destination path is required."));
        Assert.That(source, Does.Not.Contain("BEA.exe was not found under the copied game profile."));
        Assert.That(source, Does.Contain("CopiedBeaMissing"));
        Assert.That(source, Does.Not.Contain("FileNotFoundException(CopiedBeaMissing,"));
        Assert.That(source, Does.Not.Contain("Executable source was not found."));
        Assert.That(source, Does.Contain("SourceExecutableMissing"));
        Assert.That(source, Does.Not.Contain("FileNotFoundException(SourceExecutableMissing,"));
        Assert.That(source, Does.Not.Contain("BEA.exe source was not found."));
        Assert.That(source, Does.Not.Contain("Required game entry is missing: BEA.exe"));
        Assert.That(source, Does.Not.Contain("Executable override is missing."));
        Assert.That(source, Does.Not.Contain("FileNotFoundException($\"Required game file is missing: {entry}\", path)"));
        Assert.That(source, Does.Not.Contain("Required game file is missing:"));
        Assert.That(source, Does.Contain("RequiredGameFileMissing"));
        Assert.That(source, Does.Not.Contain("required game file '{entry}'"));
        Assert.That(source, Does.Not.Contain("Game entry '{entry}'"));
        Assert.That(GameProfilePreflightService.RequiredGameFileMissing,
            Is.EqualTo("A required game file is missing."));
        Assert.That(GameProfilePreflightService.RequiredGameFileMissing.ToLowerInvariant(),
            Does.Not.Contain("path"));
        Assert.That(source, Does.Not.Contain("Level 100 text target is missing."));
        Assert.That(source, Does.Not.Contain("Level 100 text backup is missing."));
        Assert.That(source, Does.Not.Contain("Level 100 early-flight target is missing."));
        Assert.That(source, Does.Not.Contain("Level 100 early-flight backup is missing."));
        Assert.That(source, Does.Not.Contain("music replacement target is missing."));
        Assert.That(source, Does.Not.Contain("music replacement backup is missing."));
        Assert.That(source, Does.Not.Contain("control-options target is missing."));
        Assert.That(source, Does.Not.Contain("control-options backup is missing."));
        Assert.That(source, Does.Not.Contain("data\\\\language\\\\english.dat."));
        Assert.That(source, Does.Not.Contain("data\\\\resources\\\\100_res_PC.aya."));
        Assert.That(source, Does.Contain("Level100EnglishDatMissing"));
        Assert.That(source, Does.Contain("Level100EnglishDatBackupMissing"));
        Assert.That(source, Does.Contain("Level100ResourceMissing"));
        Assert.That(source, Does.Contain("Level100ResourceBackupMissing"));
        Assert.That(source, Does.Not.Contain("FileNotFoundException(Level100EnglishDatMissing,"));
        Assert.That(source, Does.Not.Contain("FileNotFoundException(Level100ResourceMissing,"));
        Assert.That(source, Does.Not.Contain("FileNotFoundException(Level100ResourceBackupMissing,"));
        Assert.That(source, Does.Contain("TargetMusicFileMissing"));
        Assert.That(source, Does.Contain("MusicBackupMissing"));
        Assert.That(source, Does.Not.Contain("FileNotFoundException(GameProfileMusicReplacementService.TargetMusicFileMissing,"));
        Assert.That(source, Does.Not.Contain("FileNotFoundException(GameProfileMusicReplacementService.MusicBackupMissing,"));
        Assert.That(source, Does.Contain("OptionsFileMissing"));
        Assert.That(source, Does.Contain("OptionsBackupMissing"));
        Assert.That(source, Does.Not.Contain("FileNotFoundException(GameProfileControlOptionsService.OptionsFileMissing,"));
        Assert.That(source, Does.Not.Contain("FileNotFoundException(GameProfileControlOptionsService.OptionsBackupMissing,"));
        Assert.That(source, Does.Not.Contain("path must be package-relative."));
        Assert.That(source, Does.Not.Contain("path escapes the generated profile."));
        Assert.That(source, Does.Not.Contain("manifest executable path does not match the launch root."));
        Assert.That(source, Does.Contain("FileMustStayInsideCopy"));
        Assert.That(source, Does.Contain("CopiedBeaMismatch"));
        Assert.That(GameProfilePreflightService.FileMustStayInsideCopy,
            Is.EqualTo("That file must stay inside the copy."));
        Assert.That(GameProfilePreflightService.CopiedBeaMismatch,
            Is.EqualTo("That copy's BEA.exe does not match this copy."));
        Assert.That(GameProfilePreflightService.FileMustStayInsideCopy.ToLowerInvariant(),
            Does.Not.Contain("path"));
        Assert.That(GameProfilePreflightService.CopiedBeaMismatch.ToLowerInvariant(),
            Does.Not.Contain("path"));
        Assert.That(source, Does.Not.Contain("launch requires the copied executable backup snapshot"));
        Assert.That(source, Does.Not.Contain("backup snapshot hash does not match its sidecar."));
        Assert.That(source, Does.Not.Contain("backup snapshot is not a trusted clean Steam retail specimen."));
        Assert.That(source, Does.Not.Contain("not a clean base for selected patches"));
        Assert.That(source, Does.Not.Contain("preparation refuses reparse points"));
        Assert.That(source, Does.Contain("CopyCannotUseLink"));
        Assert.That(source, Does.Contain("FileCannotShareData"));
        Assert.That(source, Does.Not.Contain("is hardlinked to another file"));
        Assert.That(GameProfilePreflightService.FileCannotShareData,
            Is.EqualTo("That file cannot share its data with another file."));
        Assert.That(GameProfilePreflightService.FileCannotShareData.ToLowerInvariant(),
            Does.Not.Contain("hardlink"));
        Assert.That(GameProfilePreflightService.FileCannotShareData.ToLowerInvariant(),
            Does.Not.Contain("identity"));
        Assert.That(source, Does.Not.Contain("Could not inspect hardlink count"));
        Assert.That(source, Does.Not.Contain("Win32 error:"));
        Assert.That(source, Does.Contain("FileCouldNotBeInspected"));
        Assert.That(source, Does.Not.Contain("manifest patch state:"));
        Assert.That(source, Does.Not.Contain("patch apply failed:"));
        Assert.That(source, Does.Not.Contain("patch verification failed:"));
        Assert.That(source, Does.Contain("CopiedBeaPatchesMismatch"));
        Assert.That(source, Does.Contain("CopiedBeaPatchApplyFailed"));
        Assert.That(source, Does.Not.Contain("Required patch catalog row is missing:"));
        Assert.That(source, Does.Contain("RequiredPatchRowMissing"));
        Assert.That(GameProfilePreflightService.RequiredPatchRowMissing,
            Is.EqualTo("A required patch row is missing."));
        Assert.That(GameProfilePreflightService.RequiredPatchRowMissing.ToLowerInvariant(),
            Does.Not.Contain("catalog"));
        Assert.That(GameProfilePreflightService.RequiredPatchRowMissing.ToLowerInvariant(),
            Does.Not.Contain("key"));
        Assert.That(source, Does.Contain("ProfileNeedsItsPatchRows"));
        Assert.That(source, Does.Contain("ProfilePresetNotReady"));
        Assert.That(source, Does.Not.Contain("cannot be used to prepare a safe game copy."));
        Assert.That(source, Does.Not.Contain("exact proof-bounded patch row set"));
        Assert.That(source, Does.Not.Contain("{preset.DisplayName}"));
        Assert.That(GameProfilePreflightService.ProfileNeedsItsPatchRows,
            Is.EqualTo("That copy profile needs its exact patch rows."));
        Assert.That(GameProfilePreflightService.ProfileNeedsItsPatchRows.ToLowerInvariant(),
            Does.Not.Contain("proof"));
        Assert.That(source, Does.Contain("UnsupportedLaunchArgument"));
        Assert.That(source, Does.Contain("UnexpectedLaunchArgumentValue"));
        Assert.That(source, Does.Contain("LaunchArgumentNeedsANumber"));
        Assert.That(source, Does.Not.Contain("Unsupported launch argument '"));
        Assert.That(source, Does.Not.Contain("Unexpected launch argument value '"));
        Assert.That(source, Does.Not.Contain("requires a numeric value."));
        Assert.That(GameProfilePreflightService.UnsupportedLaunchArgument,
            Is.EqualTo("That launch argument is not supported."));
        Assert.That(GameProfilePreflightService.UnsupportedLaunchArgument.ToLowerInvariant(),
            Does.Not.Contain("path"));
        Assert.That(source, Does.Contain("CopyDetailsIncomplete"));
        Assert.That(source, Does.Not.Contain("Playable copied game folder {label} is missing"));
        Assert.That(source, Does.Not.Contain("Playable copied game folder {label} has an empty"));
        Assert.That(GameProfilePreflightService.CopyDetailsIncomplete,
            Is.EqualTo("That copy's details are incomplete."));
        Assert.That(GameProfilePreflightService.CopyDetailsIncomplete.ToLowerInvariant(),
            Does.Not.Contain("path"));
        Assert.That(source, Does.Contain("CopyLaunchFolderMissing"));
        Assert.That(source, Does.Contain("CopyLaunchFolderMismatch"));
        Assert.That(source, Does.Not.Contain("manifest is missing its target root marker"));
        Assert.That(source, Does.Not.Contain("manifest does not match the launch root"));
        Assert.That(GameProfilePreflightService.CopyLaunchFolderMissing,
            Is.EqualTo("That copy is missing its launch folder."));
        Assert.That(GameProfilePreflightService.CopyLaunchFolderMismatch,
            Is.EqualTo("That copy does not match this launch folder."));
        Assert.That(GameProfilePreflightService.CopyLaunchFolderMissing.ToLowerInvariant(),
            Does.Not.Contain("playable"));
        Assert.That(GameProfilePreflightService.CopyLaunchFolderMismatch.ToLowerInvariant(),
            Does.Not.Contain("root"));
        Assert.That(source, Does.Contain("CopyManifestMissing"));
        Assert.That(source, Does.Contain("CopyManifestOutOfDate"));
        Assert.That(source, Does.Not.Contain("Launch plan requires a generated playable copied game folder manifest."));
        Assert.That(source, Does.Not.Contain("Launch plan requires a current playable copied game folder manifest."));
        Assert.That(GameProfilePreflightService.CopyManifestMissing,
            Is.EqualTo("That copy is missing onslaught-profile-manifest.json."));
        Assert.That(GameProfilePreflightService.CopyManifestMissing.ToLowerInvariant(),
            Does.Not.Contain("playable"));
        Assert.That(GameProfilePreflightService.CopyManifestOutOfDate.ToLowerInvariant(),
            Does.Not.Contain("playable"));
        Assert.That(source, Does.Not.Contain("Refusing to delete a folder that is not an app-generated playable copied game folder:"));
        Assert.That(source, Does.Contain("CopiedBackupMissing"));
        Assert.That(source, Does.Contain("CopiedBackupHashMissing"));
        Assert.That(source, Does.Contain("CopiedBackupHashMismatch"));
        Assert.That(source, Does.Contain("CopiedBackupNotRetail"));
        Assert.That(GameProfilePreflightService.CopiedBackupMissing,
            Is.EqualTo("That copy is missing BEA.exe.original.backup."));
        Assert.That(GameProfilePreflightService.CopiedBackupNotRetail.ToLowerInvariant(),
            Does.Not.Contain("path"));
        Assert.That(GameProfilePreflightService.CopiedBackupNotRetail.ToLowerInvariant(),
            Does.Not.Contain("specimen"));
        Assert.That(source, Does.Contain("Level100TextDetailsInvalid"));
        Assert.That(source, Does.Contain("Level100TextDetailsUnsupported"));
        Assert.That(source, Does.Contain("Level100TextDetailsWrongTarget"));
        Assert.That(source, Does.Contain("Level100TextBackupMismatch"));
        Assert.That(source, Does.Contain("Level100TextFileMismatch"));
        Assert.That(source, Does.Contain("Level100TextSizeMismatch"));
        Assert.That(source, Does.Contain("Level100TextWrongId"));
        Assert.That(source, Does.Contain("Level100TextRangeMissing"));
        Assert.That(source, Does.Contain("Level100TextRangeInvalid"));
        Assert.That(source, Does.Contain("Level100TextBytesMismatch"));
        Assert.That(source, Does.Not.Contain("Playable copied game folder Level 100 text"));
        Assert.That(GameProfilePreflightService.Level100TextDetailsInvalid,
            Is.EqualTo("That copy's Level 100 text details are invalid."));
        Assert.That(GameProfilePreflightService.Level100TextDetailsUnsupported,
            Is.EqualTo("That copy's Level 100 text details are out of date."));
        Assert.That(GameProfilePreflightService.Level100TextDetailsWrongTarget,
            Is.EqualTo("That copy's Level 100 text details do not target english.dat."));
        Assert.That(GameProfilePreflightService.Level100TextBackupMismatch,
            Is.EqualTo("That copy's english.dat.original.backup no longer matches."));
        Assert.That(GameProfilePreflightService.Level100TextFileMismatch,
            Is.EqualTo("That copy's english.dat no longer matches."));
        Assert.That(GameProfilePreflightService.Level100TextSizeMismatch,
            Is.EqualTo("That copy's Level 100 text file sizes do not match."));
        Assert.That(GameProfilePreflightService.Level100TextWrongId,
            Is.EqualTo("That copy's Level 100 text details name the wrong text."));
        Assert.That(GameProfilePreflightService.Level100TextRangeMissing,
            Is.EqualTo("That copy's Level 100 text details are missing their changed range."));
        Assert.That(GameProfilePreflightService.Level100TextRangeInvalid,
            Is.EqualTo("That copy's Level 100 text details have an invalid changed range."));
        Assert.That(GameProfilePreflightService.Level100TextBytesMismatch,
            Is.EqualTo("That copy's Level 100 text no longer matches."));
        Assert.That(GameProfilePreflightService.Level100TextDetailsInvalid.ToLowerInvariant(),
            Does.Not.Contain("playable"));
        Assert.That(GameProfilePreflightService.Level100TextDetailsUnsupported.ToLowerInvariant(),
            Does.Not.Contain("schema"));
        Assert.That(GameProfilePreflightService.Level100TextFileMismatch.ToLowerInvariant(),
            Does.Not.Contain("manifest"));
        Assert.That(GameProfilePreflightService.Level100TextBytesMismatch.ToLowerInvariant(),
            Does.Not.Contain("replacement"));
        Assert.That(source, Does.Contain("Level100EarlyFlightDetailsInvalid"));
        Assert.That(source, Does.Contain("Level100EarlyFlightDetailsUnsupported"));
        Assert.That(source, Does.Contain("Level100EarlyFlightDetailsWrongTarget"));
        Assert.That(source, Does.Contain("Level100EarlyFlightBackupMismatch"));
        Assert.That(source, Does.Contain("Level100EarlyFlightFileMismatch"));
        Assert.That(source, Does.Contain("Level100EarlyFlightSizeMismatch"));
        Assert.That(source, Does.Contain("Level100EarlyFlightWrongCommand"));
        Assert.That(source, Does.Contain("Level100EarlyFlightPayloadMismatch"));
        Assert.That(source, Does.Not.Contain("Playable copied game folder Level 100 early-flight"));
        Assert.That(GameProfilePreflightService.Level100EarlyFlightDetailsInvalid,
            Is.EqualTo("That copy's Level 100 early-flight details are invalid."));
        Assert.That(GameProfilePreflightService.Level100EarlyFlightDetailsUnsupported,
            Is.EqualTo("That copy's Level 100 early-flight details are out of date."));
        Assert.That(GameProfilePreflightService.Level100EarlyFlightDetailsWrongTarget,
            Is.EqualTo("That copy's Level 100 early-flight details do not target 100_res_PC.aya."));
        Assert.That(GameProfilePreflightService.Level100EarlyFlightBackupMismatch,
            Is.EqualTo("That copy's 100_res_PC.aya.original.backup no longer matches."));
        Assert.That(GameProfilePreflightService.Level100EarlyFlightFileMismatch,
            Is.EqualTo("That copy's 100_res_PC.aya no longer matches."));
        Assert.That(GameProfilePreflightService.Level100EarlyFlightSizeMismatch,
            Is.EqualTo("That copy's Level 100 early-flight archive sizes do not match."));
        Assert.That(GameProfilePreflightService.Level100EarlyFlightWrongCommand,
            Is.EqualTo("That copy's Level 100 early-flight details have the wrong command."));
        Assert.That(GameProfilePreflightService.Level100EarlyFlightPayloadMismatch,
            Is.EqualTo("That copy's Level 100 early-flight payload no longer matches."));
        Assert.That(GameProfilePreflightService.Level100EarlyFlightDetailsInvalid.ToLowerInvariant(),
            Does.Not.Contain("playable"));
        Assert.That(GameProfilePreflightService.Level100EarlyFlightDetailsUnsupported.ToLowerInvariant(),
            Does.Not.Contain("schema"));
        Assert.That(GameProfilePreflightService.Level100EarlyFlightFileMismatch.ToLowerInvariant(),
            Does.Not.Contain("manifest"));
        Assert.That(GameProfilePreflightService.Level100EarlyFlightWrongCommand.ToLowerInvariant(),
            Does.Not.Contain("substitution"));
    }

    [Test]
    public void AMissingSourceExecutableDoesNotAttachTheFilePath()
    {
        string missing = Path.Combine(Path.GetTempPath(), $"gone-bea-{Guid.NewGuid():N}", "BEA.exe");
        FileNotFoundException error = Assert.Throws<FileNotFoundException>(
            () => GameProfilePreflightService.ValidateExecutableSourceForWorkspaceCopy(missing));

        Assert.That(error.Message, Is.EqualTo(GameProfilePreflightService.SourceExecutableMissing));
        Assert.That(error.Message, Is.EqualTo("That source executable could not be found."));
        Assert.That(error.FileName, Is.Null.Or.Empty);
        Assert.That(error.Message, Does.Not.Contain(missing));
        Assert.That(error.Message.ToLowerInvariant(), Does.Not.Contain("path"));
    }
}
