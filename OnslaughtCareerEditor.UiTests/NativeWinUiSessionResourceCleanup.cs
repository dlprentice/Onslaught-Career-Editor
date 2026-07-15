namespace OnslaughtCareerEditor.UiTests;

internal static class NativeWinUiSessionResourceCleanup
{
    internal static void Run(Action disposeAutomation, Action cleanupApp)
    {
        try
        {
            disposeAutomation();
        }
        finally
        {
            cleanupApp();
        }
    }
}
