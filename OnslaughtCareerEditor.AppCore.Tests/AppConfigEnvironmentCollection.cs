using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    [CollectionDefinition(Name, DisableParallelization = true)]
    public sealed class AppConfigEnvironmentCollection
    {
        public const string Name = "AppConfig environment";
    }
}
