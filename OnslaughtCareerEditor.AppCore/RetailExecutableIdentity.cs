namespace OnslaughtCareerEditor.AppCore
{
    /// <summary>
    /// Whether a BEA.exe on disk is the known Steam retail file.
    ///
    /// A folder that contains BEA.exe and a data directory is only a layout check.
    /// This is the separate identity check Settings and Home need before they call
    /// that folder finished. It never writes, and it never treats an unreadable file
    /// as "already changed" - that would be a lie while the game is running.
    /// </summary>
    public enum RetailExecutableIdentity
    {
        Missing,
        Unreadable,
        KnownCleanRetail,
        DifferentFromKnownRetail,
    }
}
