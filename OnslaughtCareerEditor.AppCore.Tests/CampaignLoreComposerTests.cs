using System;
using System.Collections.Generic;
using Onslaught___Career_Editor;
using Xunit;

namespace OnslaughtCareerEditor.AppCore.Tests
{
    /// <summary>
    /// The campaign lore page shows the game's own mission names, and must never ship them.
    ///
    /// That is the point of this class, and it is a rights boundary rather than a technical one:
    /// reading a file the player already owns is a different act from putting the game's text
    /// inside a package anyone can download. The shipped document carries a marker; the names are
    /// read off the player's disk when the page opens.
    /// </summary>
    public class CampaignLoreComposerTests
    {
        private static IReadOnlyList<GameLevelName> TwoLevels() =>
        [
            new GameLevelName("1.00", "Training Level", "1.00 - Training Level", false),
            new GameLevelName("2.11", "The Long Retreat", "2.11 - The Long Retreat", true),
        ];

        [Fact]
        public void ADocumentWithoutTheMarkerIsReturnedUntouched()
        {
            // This runs on every document the reader opens, so doing nothing has to be exact.
            const string markdown = "# Something else\n\nNo marker here.\n";

            Assert.Equal(markdown, CampaignLoreComposer.Compose(markdown, TwoLevels()));
            Assert.False(CampaignLoreComposer.WantsMissionList(markdown));
        }

        [Fact]
        public void TheMarkerBecomesATableOfTheGamesOwnNames()
        {
            string document = "# The Campaign\n\n" + CampaignLoreComposer.MissionListMarker + "\n";

            string composed = CampaignLoreComposer.Compose(document, TwoLevels());

            Assert.Contains("1.00", composed);
            Assert.Contains("Training Level", composed);
            Assert.Contains("2.11", composed);
            Assert.Contains("The Long Retreat", composed);
            Assert.DoesNotContain(CampaignLoreComposer.MissionListMarker, composed);
            Assert.Contains("There are 2 of them in your copy.", composed);
        }

        [Fact]
        public void ARepeatedMapIsMarkedAsTheHarderVersionRatherThanLookingLikeADuplicate()
        {
            string composed = CampaignLoreComposer.Compose(
                CampaignLoreComposer.MissionListMarker,
                TwoLevels());

            // Without this a reader sees the same code twice and assumes the app is broken.
            Assert.Contains("harder version of the same map", composed);
        }

        [Fact]
        public void NoGameConfiguredSaysSoAndSaysWhatToDo()
        {
            // A page that silently loses its middle reads as a bug. It must never be empty.
            IReadOnlyList<GameLevelName>?[] nothingAtAll =
            [
                null,
                Array.Empty<GameLevelName>(),
            ];

            foreach (IReadOnlyList<GameLevelName>? nothing in nothingAtAll)
            {
                string composed = CampaignLoreComposer.Compose(
                    CampaignLoreComposer.MissionListMarker,
                    nothing);

                Assert.NotEmpty(composed.Trim());
                Assert.Contains("cannot see your game", composed);
                Assert.Contains("Settings", composed);
                Assert.DoesNotContain(CampaignLoreComposer.MissionListMarker, composed);
            }
        }

        [Fact]
        public void APipeInATitleCannotShearTheTable()
        {
            // Nothing in the retail English file contains one, which is exactly why this is worth
            // handling: the other languages have not been read, and a sheared table is silent.
            IReadOnlyList<GameLevelName> awkward =
            [
                new GameLevelName("3.01", "Hold | The Line", "3.01 - Hold | The Line", false),
            ];

            string composed = CampaignLoreComposer.Compose(
                CampaignLoreComposer.MissionListMarker,
                awkward);

            Assert.Contains(@"Hold \| The Line", composed);
        }

        [Fact]
        public void ComposeSurvivesANullDocument()
        {
            Assert.Equal(string.Empty, CampaignLoreComposer.Compose(null, TwoLevels()));
            Assert.False(CampaignLoreComposer.WantsMissionList(null));
        }
    }
}
