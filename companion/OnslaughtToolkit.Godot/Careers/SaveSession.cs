// SPDX-License-Identifier: MIT
using System.Security.Cryptography;
using OnslaughtToolkit.Companion.Files;

namespace OnslaughtToolkit.Companion.Careers;

/// <summary>
/// An immutable owned snapshot of one opened career. Content hash and OS file identity are
/// separate checks; callers only ever receive copies of the bytes.
/// </summary>
public sealed class SaveSession
{
    private readonly byte[] _bytes;

    private SaveSession(string path, string identity, byte[] bytes)
        => (Path, Identity, _bytes, Sha256) = (path, identity, bytes, Digest(bytes));

    public string Path { get; }
    public string Identity { get; }
    public string Sha256 { get; }
    public CareerInspection Analysis => CareerSave.Inspect(_bytes).Value!;

    public static string Digest(ReadOnlySpan<byte> bytes) => Convert.ToHexString(SHA256.HashData(bytes)).ToLowerInvariant();

    public static Outcome<SaveSession> FromRead(ProtectedRead read)
    {
        if (!read.Ok) return Outcome<SaveSession>.Refusal(read.Message);
        if (read.Bytes is not byte[] bytes) return Outcome<SaveSession>.Refusal("The protected read did not return save bytes.");
        Outcome<CareerInspection> analysis = CareerSave.Inspect(bytes);
        if (!analysis.Ok) return Outcome<SaveSession>.Refusal(analysis.Message);
        if (bytes.Length != read.Size || Digest(bytes) != read.Sha256.ToLowerInvariant() || read.Identity.Length == 0)
            return Outcome<SaveSession>.Refusal("The protected read did not provide a matching content hash and file identity.");
        return Outcome<SaveSession>.Success(new SaveSession(read.Input, read.Identity, bytes.ToArray()),
            "Career opened and protected snapshot verified.");
    }

    public byte[] CopyBytes() => _bytes.ToArray();

    public bool Matches(ReadOnlySpan<byte> bytes) => bytes.SequenceEqual(_bytes);

    public Outcome<EditPlan> Prepare(IReadOnlyDictionary<int, int> selections) => CareerSave.Preview(_bytes, selections);

    public Outcome<EditPlan> Prepare(EditRequest request) => CareerSave.Preview(_bytes, request);

    public ByteComparison CompareWith(SaveSession other) => CareerSave.Compare(_bytes, other._bytes);

    /// <summary>
    /// Independently checks a publication receipt against the prepared bytes. An inconsistent
    /// receipt never becomes success; it keeps the uncertainty that a copy may exist.
    /// </summary>
    public PublicationReceipt VerifyPublication(PublicationReceipt receipt, ReadOnlySpan<byte> prepared)
    {
        if (!receipt.Ok) return receipt;
        if (receipt.Bytes is not byte[] actual)
            return PublicationReceipt.Uncertain(receipt.Output,
                "A copy may exist, but its verified bytes were not returned. Inspect it before use.");
        if (!actual.AsSpan().SequenceEqual(prepared) || actual.Length != _bytes.Length || actual.Length != receipt.Size ||
            Digest(actual) != receipt.Sha256.ToLowerInvariant() || !receipt.OriginalVerified || !receipt.Verified)
            return PublicationReceipt.Uncertain(receipt.Output,
                "A copy may exist, but its bytes or original-file verification did not match. Inspect it before use.");
        return receipt;
    }
}
