using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.UI.Xaml;
using Windows.Storage.Pickers;
using WinRT.Interop;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    internal static class PickerInterop
    {
        public static async Task<string?> PickFileAsync(Window window, IEnumerable<string> fileTypes)
        {
            var picker = new FileOpenPicker
            {
                SuggestedStartLocation = PickerLocationId.ComputerFolder
            };

            foreach (string fileType in fileTypes)
            {
                picker.FileTypeFilter.Add(fileType);
            }

            InitializeWithWindow.Initialize(picker, WindowNative.GetWindowHandle(window));
            var file = await picker.PickSingleFileAsync();
            return file?.Path;
        }

        public static async Task<string?> PickFolderAsync(Window window)
        {
            var picker = new FolderPicker
            {
                SuggestedStartLocation = PickerLocationId.ComputerFolder
            };
            picker.FileTypeFilter.Add("*");
            InitializeWithWindow.Initialize(picker, WindowNative.GetWindowHandle(window));
            var folder = await picker.PickSingleFolderAsync();
            return folder?.Path;
        }
    }
}
