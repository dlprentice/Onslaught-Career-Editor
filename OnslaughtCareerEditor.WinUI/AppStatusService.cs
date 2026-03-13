using System;

namespace OnslaughtCareerEditor.WinUI
{
    internal static class AppStatusService
    {
        private static string s_currentStatus = "WinUI shell ready";

        public static event Action<string>? StatusChanged;

        public static string CurrentStatus => s_currentStatus;

        public static void SetStatus(string status)
        {
            s_currentStatus = string.IsNullOrWhiteSpace(status) ? "Ready" : status.Trim();
            StatusChanged?.Invoke(s_currentStatus);
        }
    }
}
