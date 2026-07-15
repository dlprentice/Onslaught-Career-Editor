namespace OnslaughtCareerEditor.UiTests;

internal static class HomeSessionResourceCleanup
{
    internal static void Run(Action disposeAutomation, Action cleanupApp)
    {
        NativeWinUiSessionResourceCleanup.Run(disposeAutomation, cleanupApp);
    }
}
