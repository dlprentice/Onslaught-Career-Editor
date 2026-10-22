// SPDX-License-Identifier: GPL-3.0-only
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    [CollectionDefinition(Name, DisableParallelization = true)]
    public sealed class AppConfigEnvironmentCollection
    {
        public const string Name = "AppConfig environment";
    }
}
