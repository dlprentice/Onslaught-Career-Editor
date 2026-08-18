using System.IO;
using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    /// <summary>
    /// The sentence Save Lab shows about where the opened career lives. Kept out of the
    /// page so the wording can be tested, and so a full path cannot drift back onto the card.
    /// </summary>
    internal static class CareerSaveLocationText
    {
        public static string Describe(CareerSaveLocationKind kind, string? fileName)
        {
            string name = string.IsNullOrWhiteSpace(fileName)
                ? "This save"
                : Path.GetFileName(fileName.Trim());

            return kind switch
            {
                CareerSaveLocationKind.InstalledGame =>
                    $"{name} is inside your installed game folder. The app will not write back there. Changes go into a new file.",
                CareerSaveLocationKind.SafeCopy =>
                    $"{name} is inside a playable copy this app made. Changes still go into a new file; they do not overwrite this one.",
                CareerSaveLocationKind.ChosenFolder =>
                    $"{name} is in a folder you chose. Changes go into a new file, not this one.",
                _ => string.Empty,
            };
        }
    }
}
