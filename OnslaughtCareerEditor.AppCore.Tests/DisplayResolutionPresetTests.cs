using System.Collections.Generic;
using System.Linq;
using OnslaughtCareerEditor.AppCore;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// The safe copy shipped one hardcoded resolution. The widescreen
    /// correction derives its aspect from the live screen width, so other sizes
    /// are offerable - but only one has ever been played, and these tests exist
    /// mainly to keep that distinction from eroding.
    /// </summary>
    public class DisplayResolutionPresetTests
    {
        [Fact]
        public void ExactlyOneOfferedPresetIsMeasured()
        {
            IReadOnlyList<DisplayResolutionPreset> measured =
                DisplayResolutionPreset.Offered.Where(preset => preset.IsMeasured).ToList();

            DisplayResolutionPreset only = Assert.Single(measured);
            Assert.Equal(1600, only.Width);
            Assert.Equal(900, only.Height);
            Assert.Same(DisplayResolutionPreset.Measured, only);
        }

        [Fact]
        public void TheMeasuredPresetIsOfferedFirst()
        {
            Assert.True(DisplayResolutionPreset.Offered[0].IsMeasured);
        }

        [Fact]
        public void OnlyTheMeasuredPresetClaimsToHaveBeenPlayed()
        {
            foreach (DisplayResolutionPreset preset in DisplayResolutionPreset.Offered)
            {
                string described = preset.Describe();
                if (preset.IsMeasured)
                {
                    Assert.Contains("played and measured", described);
                }
                else
                {
                    Assert.Contains("nobody has played at this size yet", described);
                    Assert.DoesNotContain("measured at", described);
                }
            }
        }

        [Fact]
        public void ASizeMatchingTheMeasuredOneIsNotSilentlyDowngraded()
        {
            Assert.True(DisplayResolutionPreset.FromSize(1600, 900).IsMeasured);
            Assert.False(DisplayResolutionPreset.FromSize(1920, 1080).IsMeasured);
        }

        [Theory]
        [InlineData("1920x1080", 1920, 1080)]
        [InlineData("1280X720", 1280, 720)]
        [InlineData("  2560 x 1440  ", 2560, 1440)]
        public void ReadableSizesParse(string value, int width, int height)
        {
            Assert.True(DisplayResolutionPreset.TryParse(value, out DisplayResolutionPreset preset, out string? problem));
            Assert.Null(problem);
            Assert.Equal(width, preset.Width);
            Assert.Equal(height, preset.Height);
        }

        [Theory]
        [InlineData(null)]
        [InlineData("")]
        [InlineData("huge")]
        [InlineData("1920")]
        [InlineData("1920x1080x60")]
        [InlineData("639x480")]      // below the launch validator's floor
        [InlineData("1920x479")]
        [InlineData("16385x1080")]   // above its ceiling
        public void UnusableSizesAreRefusedWithSomethingToRead(string? value)
        {
            Assert.False(DisplayResolutionPreset.TryParse(value, out _, out string? problem));
            Assert.False(string.IsNullOrWhiteSpace(problem));
        }

        [Fact]
        public void TheRefusedRangeMatchesTheCopiedGamesOwnLaunchValidator()
        {
            // GameProfilePreflightService rejects -res outside these bounds; if
            // the two ever disagree the app would offer a size the launch path
            // then refuses.
            Assert.Equal(640, DisplayResolutionPreset.MinimumWidth);
            Assert.Equal(480, DisplayResolutionPreset.MinimumHeight);
            Assert.Equal(16384, DisplayResolutionPreset.MaximumExtent);
            Assert.True(DisplayResolutionPreset.IsSupported(640, 480));
            Assert.True(DisplayResolutionPreset.IsSupported(16384, 16384));
            Assert.False(DisplayResolutionPreset.IsSupported(639, 480));
        }

        [Fact]
        public void ChoosingASizeReplacesTheProfilesResolutionRatherThanAddingASecond()
        {
            // The compatibility profile always contributes -res 1600 900. Two
            // triples would leave the copied game reading whichever its parser
            // reached last, which is exactly the kind of bug nobody notices.
            string[] profileArguments = { "-res", "1600", "900", "-skipfmv" };

            IReadOnlyList<string> applied = DisplayResolutionPreset
                .FromSize(1920, 1080)
                .ApplyTo(profileArguments);

            Assert.Equal(new[] { "-res", "1920", "1080", "-skipfmv" }, applied);
            Assert.Single(applied, token => token == "-res");
        }

        [Fact]
        public void OtherLaunchArgumentsKeepTheirOrder()
        {
            string[] profileArguments = { "-nomusic", "-res", "1600", "900", "-nosound" };

            IReadOnlyList<string> applied = DisplayResolutionPreset
                .FromSize(2560, 1440)
                .ApplyTo(profileArguments);

            Assert.Equal(new[] { "-nomusic", "-res", "2560", "1440", "-nosound" }, applied);
        }

        [Fact]
        public void AResolutionIsAddedWhenTheProfileCarriedNone()
        {
            IReadOnlyList<string> applied = DisplayResolutionPreset
                .FromSize(1280, 720)
                .ApplyTo(new[] { "-skipfmv" });

            Assert.Equal(new[] { "-skipfmv", "-res", "1280", "720" }, applied);
        }

        [Fact]
        public void ATruncatedResolutionTripleDoesNotCorruptTheRest()
        {
            // Defensive: a malformed stored argument list should still produce
            // one well-formed -res rather than leaving a stray operand behind.
            IReadOnlyList<string> applied = DisplayResolutionPreset
                .FromSize(1920, 1080)
                .ApplyTo(new[] { "-res", "1600" });

            Assert.Equal(new[] { "-res", "1920", "1080" }, applied);
        }
    }
}
