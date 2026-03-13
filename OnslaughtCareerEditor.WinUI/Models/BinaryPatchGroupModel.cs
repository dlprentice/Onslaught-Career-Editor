using System.Collections.Generic;

namespace OnslaughtCareerEditor.WinUI.Models
{
    public sealed class BinaryPatchGroupModel
    {
        public BinaryPatchGroupModel(string title, string description, IReadOnlyList<BinaryPatchItemModel> items)
        {
            Title = title;
            Description = description;
            Items = items;
        }

        public string Title { get; }

        public string Description { get; }

        public IReadOnlyList<BinaryPatchItemModel> Items { get; }
    }
}
