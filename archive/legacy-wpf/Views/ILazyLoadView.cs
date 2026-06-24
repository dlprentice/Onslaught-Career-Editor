namespace Onslaught___Career_Editor.Views
{
    /// <summary>
    /// Implement for views that should defer heavy loading until first activation.
    /// </summary>
    public interface ILazyLoadView
    {
        void EnsureLoaded();
    }
}
