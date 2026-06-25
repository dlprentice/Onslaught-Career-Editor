using OnslaughtCareerEditor.WinUI.Models;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    internal static class PatchBenchMenuColorSelectionText
    {
        public static string BuildStatus(PatchBenchMenuColorSelectionKind selection)
        {
            return selection switch
            {
                PatchBenchMenuColorSelectionKind.Red => "Selected menu background: red.",
                PatchBenchMenuColorSelectionKind.Green => "Selected menu background: green.",
                PatchBenchMenuColorSelectionKind.Black => "Selected menu background: black.",
                _ => "Selected menu background: none."
            };
        }
    }
}
