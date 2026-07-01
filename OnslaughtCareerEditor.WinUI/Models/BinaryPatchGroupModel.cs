using System.Collections.Generic;

namespace OnslaughtCareerEditor.WinUI.Models
{
    public sealed class BinaryPatchGroupModel
    {
        public BinaryPatchGroupModel(string title, string description, string scanSummary, IReadOnlyList<BinaryPatchItemModel> items)
        {
            Title = title;
            Description = description;
            ScanSummary = scanSummary;
            Items = items;
        }

        public string Title { get; }

        public string Description { get; }

        public string ScanSummary { get; }

        public IReadOnlyList<BinaryPatchItemModel> Items { get; }
    }
}
