using System;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.WinUI
{
    internal static class AppConfigChangedService
    {
        public static event Action<AppConfig>? ConfigChanged;

        public static void NotifyChanged(AppConfig config)
        {
            ConfigChanged?.Invoke(config);
        }
    }
}
