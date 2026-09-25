// SPDX-License-Identifier: GPL-3.0-or-later

using OnslaughtRebuild.Core;
using OnslaughtRebuild.GodotClient;

namespace OnslaughtRebuild.Client.Tests;

/// <summary>
/// Source wiring guards for selected-world display text. Executed native
/// wrapping and live-host equivalence belong to the Level Select and Briefing
/// scene harnesses;
/// these assertions alone establish neither rendered nor retail parity.
///
/// <para>1. the SELECT LEVEL name band draws the SELECTED node's row
/// (<c>session.get_selected_level_name()</c>), not an unconditional
/// <c>_level100Text</c>; and</para>
///
/// <para>2. MISSION BRIEFING draws the SELECTED world's own authored body
/// (<c>session.get_selected_briefing_body()</c>) through the measured 286px wrap
/// ceiling. The executable renderer retains its world-100 fallback for an
/// empty body; the native comparison tests that behavior explicitly.</para>
/// </summary>
public sealed class RetailFrontendSelectedWorldTextWiringTests
{
    [Fact]
    public void NameBandAndBriefingDrawTheSelectedWorldsRows()
    {
        string flow = File.ReadAllText(
            Path.Combine(AppContext.BaseDirectory, "godot-pause-source", "RetailFrontendFlow.cs"));
        string bridge = NativeFrontendSource.PageFunction("_update_briefing");
        string body = BriefingSource("briefing_body.gd");

        // Gap 1: the selector band follows the selection.
        string levelBridge = NativeLevelSelectSource.Bridge;
        Assert.Contains("\"level_name\": Text.units(session.get_selected_level_name()).value", levelBridge);
        Assert.Contains("_level.set_frame({", levelBridge);
        Assert.Contains("get_node(\"LevelName\").bind(name.value)", NativeLevelSelectSource.Function("set_frame"));
        Assert.DoesNotContain("DrawLevelSelect", flow);
        // Gap 2: the briefing page composes the selected world's own copy.
        Assert.Contains("session.get_selected_level_name()", bridge);
        Assert.Contains("session.get_selected_briefing_body()", bridge);
        Assert.Contains("Text.units(paragraph).value", bridge);
        Assert.Contains("_briefing.set_frame({", bridge);
        // ...wrapped at the measured ink ceiling, not drawn raw.
        Assert.Contains("wrap_lines()", body);
        Assert.Matches(@"wrap_ceiling:\s*float\s*=\s*286(?:\.0)?\s*:", body);
        Assert.DoesNotContain("DrawMissionBriefing", flow);
    }

    [Fact]
    public void SessionExposesTheSelectionThroughTheReleasedStrings()
    {
        var frontend = new RetailFrontendSession();

        // Cold career selects the root; both pages must read its rows.
        Assert.Equal(100, frontend.SelectedWorldNumber);
        Assert.Equal("1.00 - Training Level", frontend.SelectedLevelName);
        Assert.Equal(
            OnslaughtRebuild.Core.RetailFrontendWorldStrings.Briefing(100),
            frontend.SelectedBriefingBody);
    }

    /// <summary>
    /// The selected world-100 table pair retains its transcribed bytes. This
    /// checks the input table, not the renderer's separately wrapped fallback.
    /// </summary>
    [Fact]
    public void TranscribedReceipt_MatchesTheReleasedTablePair()
    {
        IReadOnlyList<string> released =
            RetailFrontendWorldStrings.Briefing(100);

        Assert.Equal(2, released.Count);
        Assert.Equal(
            "Tatiana will take you through the basics of piloting Battle " +
            "Engine Aquila. This will cover everything from basic movement " +
            "in both Walker and Jet modes as well as Weapons use.",
            released[0]);
        Assert.Equal(
            "Listen to her advice and try to keep Colonel Kramer happy.",
            released[1]);
    }

    private static string BriefingSource(string name) => File.ReadAllText(
        Path.Combine(AppContext.BaseDirectory, "godot-briefing-source", name));
}
