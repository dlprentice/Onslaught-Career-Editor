using System.Windows;
using System.Windows.Controls;

namespace Onslaught___Career_Editor.Views
{
    /// <summary>
    /// Configuration-focused wrapper for SaveEditorView.
    /// Forces .bea-oriented workflow and hides career progress patch sections.
    /// </summary>
    public partial class ConfigurationEditorView : UserControl
    {
        public ConfigurationEditorView()
        {
            InitializeComponent();
            Loaded += ConfigurationEditorView_Loaded;
        }

        private void ConfigurationEditorView_Loaded(object sender, RoutedEventArgs e)
        {
            SaveEditorControl.EditorMode = SaveEditorMode.Configuration;
        }

        public bool TryLoadConfigurationFile(string filePath, out string error)
        {
            SaveEditorControl.EditorMode = SaveEditorMode.Configuration;
            return SaveEditorControl.TryLoadInputFile(filePath, out error);
        }
    }
}
