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
    public async Task<PublicationReceipt> PublishAsync(string destination, byte[] prepared)
    {
        if (Busy || Session is not SaveSession session) return new PublicationReceipt(false, "Open a career first.");
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

    /// <summary>Blocks until a running transaction finishes; used only while the application closes.</summary>
    public void WaitForCompletion() => worker.WaitForCompletion();

    private void SetBusy(bool busy)
    {
        Busy = busy;
        Changed?.Invoke();
    }
}
