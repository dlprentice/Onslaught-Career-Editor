using System.Collections.Generic;

namespace OnslaughtCareerEditor.WinUI.Models
{
    internal sealed record PatchBenchSafeCopyReceiptTextState(
        string Headline,
        IReadOnlyList<PatchBenchReceiptLineTextState> Lines,
        IReadOnlyList<string> IncludedChanges,
        IReadOnlyList<string> StillNotIncluded);

    internal sealed record PatchBenchReceiptLineTextState(string Label, string Value);
}
