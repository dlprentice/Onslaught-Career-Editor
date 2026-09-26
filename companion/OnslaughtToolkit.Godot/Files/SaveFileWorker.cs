// SPDX-License-Identifier: MIT
namespace OnslaughtToolkit.Companion.Files;

/// <summary>
/// Runs protected file operations one at a time on a worker thread, so the interface stays
/// responsive. Awaiting callers resume on Godot's main thread. A wait never cancels a running
/// transaction; <see cref="WaitForCompletion"/> lets shutdown finish it rather than abandon it.
/// </summary>
public sealed class SaveFileWorker(IProtectedSaveFiles? files)
{
    public const string UnavailableMessage =
        "Protected save access is unavailable, so nothing can be opened or written. Restore the complete application.";

    private Task? _active;

    public bool IsAvailable => files is not null;
    public bool IsBusy => _active is { IsCompleted: false };

    public Task<ProtectedRead> OpenCareerAsync(string path) => files is null
        ? Task.FromResult(new ProtectedRead(false, UnavailableMessage))
        : Run(() => files.OpenCareer(path),
            () => new ProtectedRead(false, "A protected file operation is already running."),
            () => new ProtectedRead(false, "The protected read did not return a valid result."));

    public Task<PublicationReceipt> PublishCopyAsync(string input, string identity, string sha256, string output, byte[] prepared)
    {
        if (files is null) return Task.FromResult(new PublicationReceipt(false, UnavailableMessage));
        // A private array crosses to the worker; later edits by the caller cannot reach it.
        byte[] owned = prepared.ToArray();
        return Run(() => files.PublishCopy(input, identity, sha256, output, owned),
            () => new PublicationReceipt(false, "A protected file operation is already running."),
            () => PublicationReceipt.Uncertain(output,
                "The protected operation did not return a valid result. A copy may exist; inspect it before use."));
    }

    /// <summary>Runs another protected file workflow (backups, game-folder writes) through the same single-flight worker.</summary>
    public Task<T> RunExclusiveAsync<T>(Func<IProtectedSaveFiles, T> operation, Func<string, T> refusal) where T : class =>
        files is null
            ? Task.FromResult(refusal(UnavailableMessage))
            : Run(() => operation(files), () => refusal("A protected file operation is already running."),
                () => refusal("The file operation stopped without a result. Inspect the game folder and the backup folder before continuing."));

    public void WaitForCompletion()
    {
        try { _active?.Wait(); }
        catch (AggregateException) { }
    }

    private async Task<T> Run<T>(Func<T> operation, Func<T> busy, Func<T> invalid) where T : class
    {
        if (IsBusy) return busy();
        Task<T> task = Task.Run(operation);
        _active = task;
        try
        {
            return await task ?? invalid();
        }
        catch (Exception)
        {
            return invalid();
        }
    }
}
