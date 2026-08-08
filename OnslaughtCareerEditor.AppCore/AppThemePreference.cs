namespace OnslaughtCareerEditor.AppCore
{
    /// <summary>
    /// The app's appearance choices, kept in AppCore so the setting is a plain
    /// value that carries no presentation dependency. The WinUI shell maps
    /// these onto ElementTheme; nothing here knows what a theme looks like.
    /// </summary>
    public static class AppThemePreference
    {
        public const string System = "system";
        public const string Light = "light";
        public const string Dark = "dark";

        /// <summary>
        /// Follow Windows by default. The app previously hard-pinned Light and
        /// shipped a complete dark palette that no user could ever reach.
        /// </summary>
        public const string Default = System;

        public static IReadOnlyList<string> All { get; } = new[] { System, Light, Dark };

        /// <summary>
        /// Accepts anything and returns a value from <see cref="All"/>. A
        /// missing, blank, or hand-edited config value resolves to the default
        /// instead of failing.
        /// </summary>
        public static string Normalize(string? value)
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                return Default;
            }

            string trimmed = value.Trim();
            foreach (string candidate in All)
            {
                if (string.Equals(candidate, trimmed, StringComparison.OrdinalIgnoreCase))
                {
                    return candidate;
                }
            }

            return Default;
        }

        /// <summary>
        /// The label shown in Settings for a stored value.
        /// </summary>
        public static string DescribeChoice(string? value) => Normalize(value) switch
        {
            Light => "Light",
            Dark => "Dark",
            _ => "Match Windows",
        };
    }
}
