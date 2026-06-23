namespace OnslaughtCareerEditor.WinUI
{
    internal sealed record MediaHandoffRequest(string SearchText, string DisplayLabel);

    internal static class MediaHandoffService
    {
        private static MediaHandoffRequest? _pendingVideoRequest;

        public static void RequestVideo(string searchText, string displayLabel)
        {
            _pendingVideoRequest = new MediaHandoffRequest(searchText, displayLabel);
        }

        public static MediaHandoffRequest? ConsumeVideoRequest()
        {
            MediaHandoffRequest? request = _pendingVideoRequest;
            _pendingVideoRequest = null;
            return request;
        }
    }
}
