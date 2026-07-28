// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Client;
using OnslaughtRebuild.Core;
using OnslaughtRebuild.GodotClient;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// Task #114. Retail's Level 100 world is not still: it constructs and scripts
/// two ambient aircraft at level load, spawns six moving ground targets, one
/// dodge-exercise Air Trainer and nine airborne Target Drones during the
/// mission. These tests hold the client half of that against the hash-pinned
/// materialized manifest.
/// </summary>
public sealed class Level100AmbientLifeTests
{
    /// <summary>
    /// The renderer throws rather than silently skipping an actor it has no
    /// mesh for (<c>FirstFlightWorldView.AddLevel100Target</c>), so the set of
    /// canonical bindings the client registers must be EXACTLY the set of
    /// (definition, mesh) pairs a world actor can carry into the target
    /// projection - no fewer, or the client dies on the first frame that admits
    /// one; no more, or a dead registration outlives the thing it drew.
    ///
    /// <para>The eligible set is derived here from the manifest rather than
    /// restated, so it tracks the authored world. Two exclusions are
    /// deliberate and are the reason a "render everything with a mesh binding"
    /// rule does not work: the 33 base-world structures are static and carry
    /// static-world mesh keys (<c>fb_control_tower</c>, <c>iceberg2</c>, ...)
    /// drawn by the static-world asset, and the player carries
    /// <c>m_f_be1.msh.aya</c> but is drawn by the Aquila walker/jet asset.</para>
    /// </summary>
    [Fact]
    public void EveryRenderableWorldActorHasARegisteredVisualBinding()
    {
        Level100ActorDefinitionSet definitions = LoadActorDefinitions();

        var eligible = new HashSet<Level100TargetVisualBinding>();
        foreach (Level100ActorDefinition actor in definitions.Actors)
        {
            if (actor.MeshBinding is null ||
                actor.DefinitionName is null ||
                !IsRenderedWorldActor(actor))
            {
                continue;
            }

            eligible.Add(new Level100TargetVisualBinding(
                actor.DefinitionName,
                actor.MeshBinding));
        }

        foreach (Level100SpawnDefinition spawn in definitions.Spawns)
        {
            // Every spawn definition produces a live, non-static mission actor
            // in a real target group, so all of them are renderable.
            Assert.NotEqual(Level100MissionTargetGroup.None, spawn.TargetGroup);
            Assert.NotNull(spawn.MeshBinding);
            eligible.Add(new Level100TargetVisualBinding(
                spawn.DefinitionName,
                spawn.MeshBinding!));
        }

        Assert.Equal(
            Level100TargetPresentation.RenderedBindings.OrderBy(
                binding => binding.DefinitionName,
                StringComparer.Ordinal),
            eligible.OrderBy(
                binding => binding.DefinitionName,
                StringComparer.Ordinal));
    }

    /// <summary>
    /// The player is the one non-static actor with a mesh binding that must NOT
    /// reach the target projection. It is called out on its own because the
    /// obvious widening - admit anything carrying a mesh binding - admits it,
    /// and the failure would be a second Aquila drawn at the walker's feet
    /// rather than an exception.
    /// </summary>
    [Fact]
    public void ThePlayerIsNotARenderableTarget()
    {
        Level100ActorDefinition player = LoadActorDefinitions().Actors.Single(
            actor => StringComparer.Ordinal.Equals(actor.Name, "Player 1"));

        Assert.Equal("BattleEngine", player.DefinitionName);
        Assert.Equal("m_f_be1.msh.aya", player.MeshBinding);
        Assert.False(player.IsStatic);
        Assert.Equal(Level100MissionTargetGroup.None, player.TargetGroup);
        Assert.DoesNotContain(
            new Level100TargetVisualBinding("BattleEngine", "m_f_be1.msh.aya"),
            Level100TargetPresentation.RenderedBindings);
    }

    /// <summary>
    /// The two ambient aircraft, as retail authors them. Every value here is
    /// read from the shipped world data through the hash-pinned manifest; the
    /// classes, the script bindings and the fact that both are built before the
    /// player has control are separately MEASURED at runtime in the 2026-07-28
    /// TTD trace (<c>CreateThingByType</c> creations 28 and 29 from
    /// <c>CWorld__LoadWorld</c>, then <c>CComplexThing__SetScript</c> rows T3f
    /// and T41).
    ///
    /// <para>Both carry target group <c>None</c>: they are pure atmosphere with
    /// no mission role, which is exactly why the old two-group render whitelist
    /// dropped them.</para>
    /// </summary>
    [Fact]
    public void BothAmbientAircraftAreAuthoredIntoTheLevelWorldWithTheirScripts()
    {
        Level100ActorDefinitionSet definitions = LoadActorDefinitions();

        Level100ActorDefinition transporter = definitions.Actors.Single(
            actor => StringComparer.Ordinal.Equals(
                actor.DefinitionIdentity,
                "wres:rlwd:0021"));
        Assert.Equal("U-17 Highside Transporter", transporter.DefinitionName);
        Assert.Equal("Transporter", transporter.ScriptName);
        Assert.Equal(
            Level100TargetPresentation.TransporterBinding,
            new Level100TargetVisualBinding(
                transporter.DefinitionName!,
                transporter.MeshBinding!));
        Assert.False(transporter.IsStatic);
        Assert.True(transporter.Active);
        Assert.Equal(Level100MissionTargetGroup.None, transporter.TargetGroup);
        // Retail (218.5, 297.5, -15.0) on the 0-512 map, in Core millimetres.
        Assert.Equal(
            new SimVector3(-70_188, -15_000, 54_250),
            transporter.InitialPose.PositionMillimeters);

        Level100ActorDefinition airTrainer = definitions.Actors.Single(
            actor => StringComparer.Ordinal.Equals(
                actor.DefinitionIdentity,
                "wres:rlwd:0040"));
        Assert.Equal("Air Trainer", airTrainer.DefinitionName);
        Assert.Equal("Flyby", airTrainer.ScriptName);
        Assert.Equal(
            Level100TargetPresentation.AirTrainerBinding,
            new Level100TargetVisualBinding(
                airTrainer.DefinitionName!,
                airTrainer.MeshBinding!));
        Assert.False(airTrainer.IsStatic);
        Assert.True(airTrainer.Active);
        Assert.Equal(Level100MissionTargetGroup.None, airTrainer.TargetGroup);
        // Retail (265.5, 392.5, -15.0).
        Assert.Equal(
            new SimVector3(-23_188, -15_000, 149_250),
            airTrainer.InitialPose.PositionMillimeters);
    }

    /// <summary>
    /// The two ambient scripts each issue one <c>FollowWaypointWait</c>, so the
    /// route decides whether either aircraft ever leaves its authored spot. Both
    /// routes are authored ABOVE the ground - the only two of the eight named
    /// paths that are - and that altitude is the third independent leg of the
    /// waypoint-index correction: under the superseded decode every node in
    /// every path sat at a uniform +10 m.
    /// </summary>
    [Fact]
    public void TheTwoAmbientRoutesAreTheOnlyAirbornePathsAndCarryTheirAuthoredAltitude()
    {
        Level100ActorDefinitionSet definitions = LoadActorDefinitions();

        Assert.Equal(8, definitions.WaypointPaths.Count);
        Assert.Equal(
            ["Flyby Path", "Transporter Path"],
            definitions.WaypointPaths
                .Where(path => path.Points.Any(
                    point => point.PositionMillimeters.Y != 0))
                .Select(path => path.Name)
                .OrderBy(name => name, StringComparer.Ordinal));

        Level100WaypointPathDefinition flyby = Path(definitions, "Flyby Path");
        Assert.Equal(
            [-15_000, -15_000, 0],
            flyby.Points.Select(point => point.PositionMillimeters.Y).Order());

        Level100WaypointPathDefinition transporter =
            Path(definitions, "Transporter Path");
        Assert.Equal(
            [-20_000, -20_000, 0],
            transporter.Points.Select(point => point.PositionMillimeters.Y).Order());
    }

    /// <summary>
    /// The engine loop is a property of the shipped unit definition, so the
    /// dodge-exercise Air Trainer sounds like the ambient one, and the Target
    /// Drone - which shares the Air Trainer's mesh but carries no
    /// <c>CUnitNoise</c> record at all - stays silent rather than borrowing it.
    /// </summary>
    [Fact]
    public void OnlyTheTwoAmbientAircraftDefinitionsCarryAnEngineLoop()
    {
        Assert.Equal(
            Level100ActorLoopCue.AirTrainer,
            Level100AudioCatalog.GetActorEngineLoop("Air Trainer"));
        Assert.Equal(
            Level100ActorLoopCue.Transport,
            Level100AudioCatalog.GetActorEngineLoop("U-17 Highside Transporter"));

        foreach (Level100TargetVisualBinding binding in
            Level100TargetPresentation.RenderedBindings)
        {
            bool expected =
                binding == Level100TargetPresentation.AirTrainerBinding ||
                binding == Level100TargetPresentation.TransporterBinding;
            Assert.Equal(
                expected,
                Level100AudioCatalog.GetActorEngineLoop(
                    binding.DefinitionName) is not null);
        }
    }

    /// <summary>
    /// The same predicate the target projection applies to an authored actor:
    /// a mission target group always renders, and the only group-less actors
    /// that render are the non-static, non-player ones - the two ambient
    /// aircraft.
    /// </summary>
    private static bool IsRenderedWorldActor(Level100ActorDefinition actor) =>
        actor.TargetGroup != Level100MissionTargetGroup.None ||
        (!actor.IsStatic &&
            !StringComparer.Ordinal.Equals(actor.Name, "Player 1"));

    private static Level100WaypointPathDefinition Path(
        Level100ActorDefinitionSet definitions,
        string name) =>
        definitions.WaypointPaths.Single(
            path => StringComparer.Ordinal.Equals(path.Name, name));

    private static string ManifestPath => System.IO.Path.Combine(
        AppContext.BaseDirectory,
        "Assets",
        "Level100",
        "StaticWorld",
        "level100-static-world.json");

    private static Level100ActorDefinitionSet LoadActorDefinitions() =>
        Level100ActorDefinitionManifest.Decode(File.ReadAllBytes(ManifestPath));
}
