// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.TestSupport;

namespace OnslaughtRebuild.Core.Tests;

public sealed class RetailWorld110LevelActorsTests
{
    [Fact]
    public void Census_AddsToTheMeasuredForty()
    {
        Assert.Equal(40, RetailWorld110LevelActors.InitialActorCount);
        Assert.Equal(2, RetailWorld110LevelActors.ActorHeaderA);
        Assert.Equal(0, RetailWorld110LevelActors.ActorHeaderB);
        Assert.Equal(40, RetailWorld110LevelActors.SumOfTypedRows);
        Assert.Equal(54669, RetailWorld110LevelActors.SharedBaseWorldBytes);
        Assert.Equal(
            "04C5A3838548A2C50819F46DC1F1746F7C20EC4AA34678BD23C8BCD2186010F4",
            RetailWorld110LevelActors.SharedBaseWorldSha256);
    }

    [Fact]
    public void DefinitionSet_CarriesTheWorldNumber_AndRejectsUnknownWorlds()
    {
        Level100ActorDefinitionSet root = Level100TestActorDefinitions.Create();
        Assert.Equal(RetailWorldCatalog.RootWorldNumber, root.WorldNumber);

        Assert.Throws<ArgumentOutOfRangeException>(
            () => new Level100ActorDefinitionSet(
                root.Actors,
                root.Spawns,
                root.WaypointPaths,
                root.MotionDefinitions,
                worldNumber: 999));
    }
}
