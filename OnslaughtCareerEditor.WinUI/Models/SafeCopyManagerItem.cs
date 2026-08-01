using System;
using System.Globalization;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.WinUI.Models
{
    /// <summary>
    /// One safe copy as the manager list shows it.
    ///
    /// Everything a row needs is computed here rather than in the template, because the numbers are
    /// the point of the list: somebody opens it because several gigabytes went missing, and the
    /// answer has to be readable at a glance rather than assembled by a converter.
    ///
    /// The per-row automation ids are derived from the folder name so a test can address one row
    /// among several. Folder names are already constrained to letters, digits, dot, underscore and
    /// dash by the create path, but this sanitizes anyway - an id that silently contains a space
    /// would break addressing rather than fail loudly.
    /// </summary>
    public sealed class SafeCopyManagerItem
    {
        public SafeCopyManagerItem(SafeCopyOverview overview)
        {
            ArgumentNullException.ThrowIfNull(overview);

            DisplayName = overview.DisplayName;
            ProfileRoot = overview.ProfileRoot;
            SizeText = SafeCopyCatalogService.DescribeSize(overview.SizeBytes);
            CareerSaveCount = overview.CareerSaveCount;
            CanLaunch = overview.Playable;

            string id = Sanitize(overview.DisplayName);
            SafeCopyRowAutomationId = $"SafeCopyRow_{id}";
            LaunchAutomationId = $"SafeCopyRowLaunch_{id}";
            OpenFolderAutomationId = $"SafeCopyRowOpenFolder_{id}";
            DeleteAutomationId = $"SafeCopyRowDelete_{id}";

            DetailText = BuildDetail(overview);
        }

        public string DisplayName { get; }

        public string ProfileRoot { get; }

        public string SizeText { get; }

        public string DetailText { get; }

        public int CareerSaveCount { get; }

        public bool CanLaunch { get; }

        public string SafeCopyRowAutomationId { get; }

        public string LaunchAutomationId { get; }

        public string OpenFolderAutomationId { get; }

        public string DeleteAutomationId { get; }

        /// <summary>The accessible name for this row's delete button, naming which copy it deletes.</summary>
        public string DeleteAccessibleName => $"Delete {DisplayName}";

        public string LaunchAccessibleName => $"Launch {DisplayName}";

        public string OpenFolderAccessibleName => $"Open the folder for {DisplayName}";

        private static string BuildDetail(SafeCopyOverview overview)
        {
            string careers = overview.CareerSaveCount switch
            {
                0 => "no careers inside",
                1 => "1 career inside",
                _ => $"{overview.CareerSaveCount} careers inside",
            };

            string made = overview.CreatedUtc == DateTime.MinValue
                ? "date unknown"
                : $"made {overview.CreatedUtc.ToLocalTime().ToString("d MMM yyyy", CultureInfo.CurrentCulture)}";

            return overview.Playable
                ? $"{careers}, {made}"
                : $"{careers}, {made} - this one has no BEA.exe, so it cannot be launched";
        }

        private static string Sanitize(string name)
        {
            char[] characters = name.ToCharArray();
            for (int index = 0; index < characters.Length; index++)
            {
                if (!char.IsLetterOrDigit(characters[index]))
                    characters[index] = '_';
            }

            return new string(characters);
        }
    }
}
