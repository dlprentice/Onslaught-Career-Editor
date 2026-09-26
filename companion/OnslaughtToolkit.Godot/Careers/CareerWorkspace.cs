// SPDX-License-Identifier: MIT
using OnslaughtToolkit.Companion.Files;

namespace OnslaughtToolkit.Companion.Careers;

/// <summary>A read-only comparison of the open original with another supported career.</summary>
public sealed record CareerComparison(SaveSession Other, ByteComparison Bytes);

/// <summary>
/// Owns the open career and its file workflows: protected open, verified separate-copy
/// publication with an independent reopen, and read-only comparison. Pages render its state and
/// forward user choices; they never touch files themselves. One workflow runs at a time.
/// </summary>
public sealed class CareerWorkspace(SaveFileWorker worker)
{
    public SaveSession? Session { get; private set; }

    /// <summary>The last copy that was published, reopened and verified; empty after any later attempt.</summary>
    public string LastVerifiedOutput { get; private set; } = "";

    public bool Busy { get; private set; }
    public bool IsAvailable => worker.IsAvailable;

    /// <summary>Raised on the main thread whenever the session, busy state or verified result changes.</summary>
    public event Action? Changed;

    /// <summary>Raised after a different career becomes the open original.</summary>
    public event Action? SessionOpened;

    public async Task<Outcome<SaveSession>> OpenAsync(string path)
    {
        if (Busy) return Outcome<SaveSession>.Refusal("A file operation is already running.");
        SetBusy(true);
        try
        {
            Outcome<SaveSession> opened = SaveSession.FromRead(await worker.OpenCareerAsync(path));
            if (opened.Value is SaveSession session)
            {
                Session = session;
                LastVerifiedOutput = "";
                SessionOpened?.Invoke();
            }
            return opened;
        }
        finally
        {
            SetBusy(false);
        }
    }

    /// <summary>
    /// Publishes prepared bytes to a new file, checks the receipt independently, then reads the
    /// result again through the protected route. The original stays the open source.
    /// </summary>
    public Task<PublicationReceipt> PublishAsync(string destination, byte[] prepared) =>
        Session is SaveSession session ? PublishFromAsync(session, destination, prepared)
            : Task.FromResult(new PublicationReceipt(false, "Open a career first."));

    /// <summary>Opens a file as a read-only snapshot without changing the open career (the options page's source).</summary>
    public async Task<Outcome<SaveSession>> ReadSnapshotAsync(string path)
    {
        if (Busy) return Outcome<SaveSession>.Refusal("A file operation is already running.");
        SetBusy(true);
        try
        {
            return SaveSession.FromRead(await worker.OpenCareerAsync(path));
        }
        finally
        {
            SetBusy(false);
        }
    }

    /// <summary>Publishes prepared bytes as a new file whose protected source is the given snapshot, then reopens it.</summary>
    public async Task<PublicationReceipt> PublishFromAsync(SaveSession session, string destination, byte[] prepared)
    {
        if (Busy) return new PublicationReceipt(false, "A file operation is already running.");
        SetBusy(true);
        LastVerifiedOutput = "";
        try
        {
            PublicationReceipt receipt = session.VerifyPublication(
                await worker.PublishCopyAsync(session.Path, session.Identity, session.Sha256, destination, prepared), prepared);
            if (!receipt.Ok || receipt.Output is not string output) return receipt;
            Outcome<SaveSession> reopened = SaveSession.FromRead(await worker.OpenCareerAsync(output));
            if (reopened.Value is not SaveSession copy || !copy.Matches(prepared))
                return PublicationReceipt.Uncertain(output,
                    "The copy was published but its additional reopen check failed. Inspect it before use.");
            LastVerifiedOutput = output;
            return receipt;
        }
        finally
        {
            SetBusy(false);
        }
    }

    public async Task<Outcome<CareerComparison>> CompareAsync(string path)
    {
        if (Busy || Session is not SaveSession session) return Outcome<CareerComparison>.Refusal("Open an original first.");
        SetBusy(true);
        try
        {
            Outcome<SaveSession> opened = SaveSession.FromRead(await worker.OpenCareerAsync(path));
            if (opened.Value is not SaveSession other) return Outcome<CareerComparison>.Refusal(opened.Message);
            return Outcome<CareerComparison>.Success(new CareerComparison(other, session.CompareWith(other)),
                "Comparison complete. Both files were opened read-only.");
        }
        finally
        {
            SetBusy(false);
        }
    }

    /// <summary>Makes a verified backup set of every career and the options file.</summary>
    public async Task<BackupReceipt> BackUpAsync(Game.GameFolder game, string backupRoot)
    {
        if (Busy) return new BackupReceipt(false, "A file operation is already running.");
        SetBusy(true);
        try
        {
            return await worker.RunExclusiveAsync(files => Backups.Create(files, game, backupRoot, DateTime.Now),
                message => new BackupReceipt(false, message));
        }
        finally
        {
            SetBusy(false);
        }
    }

    /// <summary>
    /// Writes a verified career or options file into the game folder after a verified backup. The
    /// source is read through the protected route and must be a supported career of the same kind.
    /// </summary>
    public async Task<InstallReceipt> InstallAsync(Game.GameFolder game, string sourcePath, string targetName, string backupRoot,
        Func<bool> gameRunning)
    {
        if (Busy) return new InstallReceipt(false, "A file operation is already running.", targetName);
        bool options = string.Equals(targetName, GameInstaller.OptionsName, StringComparison.OrdinalIgnoreCase);
        if (!string.Equals(System.IO.Path.GetExtension(sourcePath), options ? ".bea" : ".bes", StringComparison.OrdinalIgnoreCase))
            return new InstallReceipt(false, options ? "Only a .bea options file can become defaultoptions.bea."
                : "Only a .bes career can go into savegames.", targetName);
        SetBusy(true);
        try
        {
            return await worker.RunExclusiveAsync(files =>
            {
                ProtectedRead read = files.OpenCareer(sourcePath);
                if (!read.Ok || read.Bytes is not byte[] bytes)
                    return new InstallReceipt(false, "The file to install could not be read: " + read.Message, targetName);
                return GameInstaller.Install(files, game, targetName, bytes, backupRoot, gameRunning, DateTime.Now);
            }, message => new InstallReceipt(false, message, targetName));
        }
        finally
        {
            SetBusy(false);
        }
    }

    /// <summary>Blocks until a running transaction finishes; used only while the application closes.</summary>
    public void WaitForCompletion() => worker.WaitForCompletion();

    private void SetBusy(bool busy)
    {
        Busy = busy;
        Changed?.Invoke();
    }
}
