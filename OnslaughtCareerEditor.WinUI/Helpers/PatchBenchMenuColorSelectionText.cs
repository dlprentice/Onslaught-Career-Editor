using OnslaughtCareerEditor.WinUI.Models;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    internal static class PatchBenchMenuColorSelectionText
    {
        public static string BuildStatus(PatchBenchMenuColorSelectionKind selection)
        {
            return selection switch
            {
                PatchBenchMenuColorSelectionKind.Red => "Selected frontend margins: red.",
                PatchBenchMenuColorSelectionKind.Green => "Selected frontend margins: green.",
                PatchBenchMenuColorSelectionKind.Black => "Selected frontend margins: black.",
                _ => "Selected frontend margins: none."
            };
        }
    }
}
