// SPDX-License-Identifier: GPL-3.0-only
namespace OnslaughtToolkit.Companion.Levels;

public sealed partial class LevelEditorModel
{
    internal WaypointRuleReport CheckWaypointRules(string source) => WaypointRuleAudit.Check(source, Session?.Body, BaseWorld);
}
