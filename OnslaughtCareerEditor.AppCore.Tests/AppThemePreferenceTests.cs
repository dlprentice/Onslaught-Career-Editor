using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// The appearance setting is a plain stored string, so the only contract
    /// that matters is that it can never stop the app from starting: anything
    /// unrecognized resolves to the shipped default.
    /// </summary>
    public class AppThemePreferenceTests
    {
        [Theory]
        [InlineData("system")]
        [InlineData("light")]
        [InlineData("dark")]
        public void RecognizedChoicesRoundTrip(string value)
        {
            Assert.Equal(value, AppThemePreference.Normalize(value));
        }

        [Theory]
        [InlineData("Light")]
        [InlineData("  DARK  ")]
        [InlineData("System")]
        public void ChoicesAreCaseAndWhitespaceInsensitive(string value)
        {
            Assert.Contains(AppThemePreference.Normalize(value), AppThemePreference.All);
        }

        [Theory]
        [InlineData(null)]
        [InlineData("")]
        [InlineData("   ")]
        [InlineData("solarized")]
        [InlineData("{}")]
        public void UnrecognizedOrMissingValuesFallBackToTheDefault(string? value)
        {
            Assert.Equal(AppThemePreference.Default, AppThemePreference.Normalize(value));
        }

        [Fact]
        public void TheDefaultFollowsWindows()
        {
            // The app previously pinned Light in App.xaml and shipped a full
            // dark palette that no user could ever select.
            Assert.Equal(AppThemePreference.System, AppThemePreference.Default);
        }

        [Fact]
        public void EveryChoiceHasAHumanLabel()
        {
            Assert.Equal("Match Windows", AppThemePreference.DescribeChoice(AppThemePreference.System));
            Assert.Equal("Light", AppThemePreference.DescribeChoice(AppThemePreference.Light));
            Assert.Equal("Dark", AppThemePreference.DescribeChoice(AppThemePreference.Dark));
            Assert.Equal("Match Windows", AppThemePreference.DescribeChoice("nonsense"));
        }

        [Fact]
        public void AFreshConfigStartsOnTheDefault()
        {
            Assert.Equal(AppThemePreference.Default, new AppConfig().AppTheme);
        }
    }
}
