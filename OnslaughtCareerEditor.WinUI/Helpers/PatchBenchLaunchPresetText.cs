using OnslaughtCareerEditor.WinUI.Models;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    internal static class PatchBenchLaunchPresetText
    {
        public static PatchBenchSelectedChoiceState BuildQuietCaptureChoiceState(bool isSelected)
        {
            return BuildChoiceState(
                "Set quiet capture launch options for safe copy",
                "Selected: quiet capture launch preset",
                isSelected);
        }

        public static PatchBenchSelectedChoiceState BuildControlBaselineChoiceState(bool isSelected)
        {
            return BuildChoiceState(
                "Set control diagnostics baseline config 1",
                "Selected: control diagnostics baseline config 1",
                isSelected);
        }

        public static PatchBenchSelectedChoiceState BuildControlSharpenedChoiceState(bool isSelected)
        {
            return BuildChoiceState(
                "Set control diagnostics sensitivity test config 1",
                "Selected: control diagnostics sensitivity test config 1",
                isSelected);
        }

        public static PatchBenchSelectedChoiceState BuildControlConfig2ChoiceState(bool isSelected)
        {
            return BuildChoiceState(
                "Set control diagnostics swapped sticks config 2",
                "Selected: control diagnostics swapped config 2",
                isSelected);
        }

        public static PatchBenchSelectedChoiceState BuildControlConfig3ChoiceState(bool isSelected)
        {
            return BuildChoiceState(
                "Set control diagnostics alternate morph jets config 3",
                "Selected: control diagnostics alternate morph jets config 3",
                isSelected);
        }

        public static PatchBenchSelectedChoiceState BuildControlConfig4ChoiceState(bool isSelected)
        {
            return BuildChoiceState(
                "Set control diagnostics swapped alternate config 4",
                "Selected: control diagnostics swapped alternate config 4",
                isSelected);
        }

        public static string BuildAdminLevelPresetTrainingWorld100StatusMessage()
        {
            return "admin level preset campaign training world 100 selected";
        }

        public static string BuildAdminLevelPresetFinalWorld800StatusMessage()
        {
            return "admin level preset final campaign world 800 selected";
        }

        public static string BuildAdminLevelPresetLocalMultiplayerWorld850StatusMessage()
        {
            return "admin level preset local multiplayer world 850 selected";
        }

        public static string BuildAdminLevelPresetLocalMultiplayerWorld851StatusMessage()
        {
            return "admin level preset local multiplayer world 851 selected";
        }

        public static string BuildLocalMultiplayerProbeStatusMessage()
        {
            return "local multiplayer level 850 launch probe selected";
        }

        public static string BuildQuietCaptureStatusMessage()
        {
            return "quiet capture launch preset selected";
        }

        public static string BuildControlBaselineStatusMessage()
        {
            return "control diagnostics baseline config 1 selected";
        }

        public static string BuildControlSharpenedStatusMessage()
        {
            return "control diagnostics sensitivity test config 1 selected";
        }

        public static string BuildControlConfig2StatusMessage()
        {
            return "control diagnostics swapped config 2 selected";
        }

        public static string BuildControlConfig3StatusMessage()
        {
            return "control diagnostics alternate config 3 selected";
        }

        public static string BuildControlConfig4StatusMessage()
        {
            return "control diagnostics swapped alternate config 4 selected";
        }

        public static string BuildClearLaunchOptionsStatusMessage()
        {
            return "launch options cleared";
        }

        private static PatchBenchSelectedChoiceState BuildChoiceState(
            string normalAutomationName,
            string selectedAutomationName,
            bool isSelected)
        {
            return new PatchBenchSelectedChoiceState(
                normalAutomationName,
                selectedAutomationName,
                isSelected);
        }
    }
}
