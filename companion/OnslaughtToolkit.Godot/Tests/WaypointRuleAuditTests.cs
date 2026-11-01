// SPDX-License-Identifier: GPL-3.0-only
using OnslaughtToolkit.Companion.Levels;
using OnslaughtToolkit.Companion.Missions;
namespace OnslaughtToolkit.Companion.Tests;

internal static class WaypointRuleAuditTests
{
    internal static WorldBody World(string pathName = "Route")
    {
        WorldBody body = new() { Version = 43, BaseLevel = -1, MapNumber = 2 };
        body.Things.Add(new PlacedObject { ObjectId = 18, Init = new ObjectInit { Name = "First authored waypoint" } });
        body.Things.Add(new PlacedObject { ObjectId = 18, Init = new ObjectInit { Name = "Second authored waypoint" } });
        body.WaypointPaths.Add(new WaypointPath { Name = pathName, Slots = { 0, 1 } });
        return body;
    }

    internal static void Run(Checks check)
    {
        check.Suite("waypoint rule audit");
        WorldBody world = World();
        byte[] before = world.Write();
        string source = "// FollowWaypoint(\"missing\", 0);\ninit()\n{\nFollowWaypoint(\"ROUTE\", 0);\nFollowWaypointWait(\n\"Route\", 0, 5);\n}\n";
        WaypointRuleReport report = WaypointRuleAudit.Check(source, world);
        check.That(report.Available && report.Calls == 2 && report.Resolved == 2 && report.Unresolved == 0 && report.Findings[0].Line == 3 && report.Findings[1].Line == 5,
                   "direct calls across lines resolve using the existing path matching and retain literal source lines");
        check.That(world.Write().AsSpan().SequenceEqual(before) && source.StartsWith("// FollowWaypoint", StringComparison.Ordinal), "the audit changes neither selected world nor source");
        world.WaypointPaths.Add(new WaypointPath { Name = "Empty" });
        report = WaypointRuleAudit.Check("FollowWaypoint(\"Absent\", 0); FollowWaypointWait(\"Empty\", 0, 5); FollowWaypoint(route,0); FollowWaypoint(\"Route\" + suffix,0); FollowWaypoint((\"Route\"),0);", world);
        check.That(report.Calls == 5 && report.Unresolved == 2 && report.Unchecked == 3 && report.Findings[0].Kind == WaypointRuleKind.MissingPath && report.Findings[1].Kind == WaypointRuleKind.EmptyPath,
                   "missing and empty declared paths are distinct from expressions the limited check cannot resolve");
        report = WaypointRuleAudit.Check("Print(\"FollowWaypoint\"); XFollowWaypoint(\"Absent\",0); unit.FollowWaypoint(\"Absent\",0); followwaypoint(\"Absent\",0);", world);
        check.That(report.Available && report.Calls == 0 && report.Findings.Count == 0, "strings, member expressions, prefixes and differently cased names are not mistaken for the supported calls");
        WorldBody baseWorld = World("Route");
        baseWorld.WaypointPaths[0].Slots.Clear();
        report = WaypointRuleAudit.Check("FollowWaypoint(\"route\",0);", world, baseWorld);
        check.That(report.Unresolved == 1 && report.Findings[0].Kind == WaypointRuleKind.EmptyPath && report.Findings[0].Message.Contains("base world", StringComparison.Ordinal),
                   "the selected base-world path retains precedence even when the level's matching path has points");
        world.WaypointPaths[0].Name = "é-route";
        report = WaypointRuleAudit.Check("FollowWaypoint(\"É-route\",0);", world);
        check.That(report.Findings.Single().Kind == WaypointRuleKind.MissingPath, "non-ASCII case is not silently folded by a different comparison");
        world.WaypointPaths[0].Name = "Route";
        world.Things.Add(new PlacedObject { ObjectId = ObjectKinds.Unit, Init = new ObjectInit { Name = "Not a waypoint" } });
        world.WaypointPaths.Add(new WaypointPath { Name = "Invalid slots", Slots = { -1, short.MaxValue, 2 } });
        world.WaypointPaths.Add(new WaypointPath { Name = "Repeated slots", Slots = { 0, -1, 0, 2 } });
        report = WaypointRuleAudit.Check("FollowWaypoint(\"Invalid slots\",0); FollowWaypoint(\"Repeated slots\",0);", world);
        check.That(report.Findings[0].Kind == WaypointRuleKind.EmptyPath && report.Findings[1].Kind == WaypointRuleKind.Resolved && report.Findings[1].Message.Contains("2 waypoint rows", StringComparison.Ordinal),
                   "invalid and non-waypoint slots are excluded while repeated waypoint rows retain their selected-data order");
        world.WaypointPaths[0].Name = "Route\0uncompared suffix";
        report = WaypointRuleAudit.Check("FollowWaypoint(\"ROUTE\",0);", world);
        check.That(report.Resolved == 1, "the audit shares the existing path-name prefix rule without rewriting stored names");
        world.WaypointPaths[0].Name = "Route";
        report = WaypointRuleAudit.Check("#include authored-missing-header\n#define TARGET \"Route\"\nFollowWaypoint(TARGET,0);\nFollowWaypoint(\"Route\",0);", world);
        check.That(report.Available && report.SkippedDirectives == 2 && report.Calls == 2 && report.Resolved == 1 && report.Unchecked == 1 && report.Findings[1].Line == 3,
                   "directives are counted without reading files or expanding macros, while line numbers and unchecked expressions stay honest");
        report = WaypointRuleAudit.Check("init() {\nPrint(\"unfinished\n", world);
        check.That(!report.Available && report.Findings.Single().Kind == WaypointRuleKind.Unavailable && report.Findings[0].Line == 1,
                   "unreadable tokens produce an unavailable result rather than a successful check");
        report = WaypointRuleAudit.Check(string.Concat(Enumerable.Repeat("FollowWaypoint(\"Route\",0);\n", WaypointRuleAudit.MaxFindings + 3)), world);
        check.That(report.Calls == WaypointRuleAudit.MaxFindings + 3 && report.Findings.Count == WaypointRuleAudit.MaxFindings && report.UnshownCalls == 3,
                   "large reports explicitly count calls omitted from the bounded findings");
        check.That(!WaypointRuleAudit.Check(new string('x', ScriptCompiler.MaxSource + 1), world).Available,
                   "oversized source refuses before tokenization");
        world.WaypointPaths[0].Slots.AddRange(Enumerable.Repeat((short)0, WaypointRuleAudit.MaxPathSlots));
        check.That(!WaypointRuleAudit.Check("FollowWaypoint(\"Route\",0);", world).Available, "oversized selected path data refuses without an unbounded scan");
        check.That(!new LevelEditorModel([]).CheckWaypointRules("FollowWaypoint(\"Route\",0);").Available,
                   "a model without an open world cannot report validation success");
        check.That(WaypointRuleReport.Scope.Contains("runtime behavior are unchecked", StringComparison.Ordinal), "the report never presents static matching as runtime validation");
    }
}
