using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using NUnit.Framework;
using Onslaught___Career_Editor;

namespace OnslaughtCareerEditor.UiTests;

/// <summary>
/// The tripwire half of the silent-drop class closure.
///
/// Three defects of one class shipped, each fixed for the instance in front of it. The structural
/// answer is that no career-section payload may exist without a registered owning section. These
/// tests fail the moment someone adds a fourth payload — to the request DTO, to the snapshot the
/// contract reads, or to the patcher — without registering it.
///
/// This is a census, not a proof of behaviour. The behavioural half lives in
/// <c>SavePatchKeepSemanticsTests</c>, which drives the same table through real patches against the
/// tracked retail fixture and asserts the bytes.
/// </summary>
public class SavePatchIntentCoverageTests
{
    [Test]
    public void EverySavePatchRequestProperty_IsRoutingOrASectionSwitchOrARegisteredIntent()
    {
        string[] classified = SavePatchIntentContract.RoutingPropertyNames
            .Concat(SavePatchIntentContract.SectionSwitchPropertyNames)
            .Concat(SavePatchIntentContract.Intents.Select(intent => intent.PropertyName))
            .ToArray();

        string[] unclassified = PayloadCandidateProperties(typeof(SavePatchRequest))
            .Where(name => !classified.Contains(name, StringComparer.Ordinal))
            .ToArray();

        Assert.That(
            unclassified,
            Is.Empty,
            $"SavePatchRequest carries {string.Join(", ", unclassified)}, which no entry in " +
            "SavePatchIntentContract claims. An unclassified payload is a payload that can be " +
            "configured and silently dropped, which is exactly the defect class this table exists to " +
            "close. Register it in SavePatchIntentContract.Intents (with the section pass that " +
            "consumes it) or in RoutingPropertyNames.");
    }

    [Test]
    public void EverySnapshotProperty_IsASectionSwitchOrARegisteredIntent()
    {
        // The snapshot is the shape the contract actually reads, and it is what BesFilePatcher — the
        // type the CLI constructs directly — projects into. Censusing the DTO alone would leave the
        // CLI's real write path uncovered.
        string[] classified = SavePatchIntentContract.SectionSwitchPropertyNames
            .Concat(SavePatchIntentContract.Intents.Select(intent => intent.PropertyName))
            .ToArray();

        string[] unclassified = PayloadCandidateProperties(typeof(SavePatchIntentSnapshot))
            .Where(name => !classified.Contains(name, StringComparer.Ordinal))
            .ToArray();

        Assert.That(unclassified, Is.Empty,
            $"SavePatchIntentSnapshot carries unclassified payload(s): {string.Join(", ", unclassified)}.");
    }

    [Test]
    public void EverySectionSwitch_EitherRequiresAPayloadOrRecordsWhyItDoesNot()
    {
        foreach (string section in SavePatchIntentContract.SectionSwitchPropertyNames)
        {
            bool hasPayloadRule = SavePatchIntentContract.SectionPayloadRules
                .Any(rule => rule.SectionSwitchPropertyName == section);
            bool hasRecordedExemption = SavePatchIntentContract.SectionsWithoutPayloadRequirement
                .ContainsKey(section);

            Assert.That(
                hasPayloadRule ^ hasRecordedExemption,
                Is.True,
                $"Section '{section}' must appear in exactly one of SectionPayloadRules (it fails when " +
                $"switched on with nothing to write) or SectionsWithoutPayloadRequirement (with the " +
                $"reason it is allowed to run empty). It currently appears in " +
                $"{(hasPayloadRule ? "both" : "neither")}.");
        }
    }

    [Test]
    public void EveryIntent_NamesASectionSwitchThatExists()
    {
        foreach (SavePatchIntent intent in SavePatchIntentContract.Intents)
        {
            Assert.That(
                SavePatchIntentContract.SectionSwitchPropertyNames,
                Does.Contain(intent.SectionSwitchPropertyName),
                $"Intent '{intent.PropertyName}' claims to be owned by '{intent.SectionSwitchPropertyName}', " +
                $"which is not one of the four section switches.");
        }
    }

    [Test]
    public void EveryIntent_ActuallyReadsTheSnapshotPropertyItNames()
    {
        // Guards against an intent whose predicate looks at the wrong field: the name and the predicate
        // must agree, or the census would pass while the guard watched nothing.
        foreach (SavePatchIntent intent in SavePatchIntentContract.Intents)
        {
            SavePatchIntentSnapshot empty = new();
            Assert.That(intent.IsConfigured(empty), Is.False,
                $"Intent '{intent.PropertyName}' reports configured on a snapshot where nothing is set.");

            SavePatchIntentSnapshot configured = WithConfigured(intent.PropertyName);
            Assert.That(intent.IsConfigured(configured), Is.True,
                $"Intent '{intent.PropertyName}' does not report configured when " +
                $"SavePatchIntentSnapshot.{intent.PropertyName} is set. Its predicate reads the wrong field.");

            foreach (SavePatchIntent other in SavePatchIntentContract.Intents.Where(i => i != intent))
            {
                Assert.That(other.IsConfigured(configured), Is.False,
                    $"Setting only {intent.PropertyName} made intent '{other.PropertyName}' report " +
                    $"configured. Two intents are reading the same field.");
            }
        }
    }

    [Test]
    public void RequestAndSnapshot_AgreeOnEveryIntentValue()
    {
        // SavePatchRequest.ToIntentSnapshot is a hand-written projection, so a new property could be
        // added to the DTO, registered in the table, and then forgotten in the projection — leaving the
        // guard reading a permanent null. Round-trip each intent through the projection to catch that.
        foreach (SavePatchIntent intent in SavePatchIntentContract.Intents)
        {
            SavePatchRequest request = WithConfiguredRequest(intent.PropertyName);
            Assert.That(
                intent.IsConfigured(request.ToIntentSnapshot()),
                Is.True,
                $"SavePatchRequest.{intent.PropertyName} was set, but ToIntentSnapshot did not carry it " +
                $"through, so the guard for that payload can never fire.");
        }
    }

    [Test]
    public void RequestAndSnapshot_AgreeOnEverySectionSwitch()
    {
        // The section switches are all bool, so a copy-paste in ToIntentSnapshot that projects
        // PatchNodes into PatchLinks compiles cleanly and would silently point every guard at the
        // wrong switch. Flip one at a time and check exactly that one moved.
        foreach (string section in SavePatchIntentContract.SectionSwitchPropertyNames)
        {
            SavePatchRequest request = section switch
            {
                nameof(SavePatchRequest.PatchNodes) => new SavePatchRequest { PatchNodes = false },
                nameof(SavePatchRequest.PatchLinks) => new SavePatchRequest { PatchLinks = false },
                nameof(SavePatchRequest.PatchGoodies) => new SavePatchRequest { PatchGoodies = false },
                nameof(SavePatchRequest.PatchKills) => new SavePatchRequest { PatchKills = false },
                _ => throw new AssertionException($"Unknown section switch '{section}'.")
            };

            SavePatchIntentSnapshot snapshot = request.ToIntentSnapshot();
            foreach (string other in SavePatchIntentContract.SectionSwitchPropertyNames)
            {
                bool value = other switch
                {
                    nameof(SavePatchIntentSnapshot.PatchNodes) => snapshot.PatchNodes,
                    nameof(SavePatchIntentSnapshot.PatchLinks) => snapshot.PatchLinks,
                    nameof(SavePatchIntentSnapshot.PatchGoodies) => snapshot.PatchGoodies,
                    nameof(SavePatchIntentSnapshot.PatchKills) => snapshot.PatchKills,
                    _ => throw new AssertionException($"Unknown section switch '{other}'.")
                };

                Assert.That(
                    value,
                    Is.EqualTo(other != section),
                    $"Disabling {section} on the request produced the wrong snapshot: {other} is {value}. " +
                    $"ToIntentSnapshot is projecting a section switch into the wrong field.");
            }
        }
    }

    private static IEnumerable<string> PayloadCandidateProperties(Type type) =>
        type.GetProperties(BindingFlags.Public | BindingFlags.Instance)
            .Where(property => property.CanRead && property.GetIndexParameters().Length == 0)
            // Computed projections are not payloads in their own right.
            .Where(property => property.Name != nameof(SavePatchRequest.ToIntentSnapshot))
            .Select(property => property.Name);

    private static SavePatchIntentSnapshot WithConfigured(string propertyName) => propertyName switch
    {
        nameof(SavePatchIntentSnapshot.Rank) => new SavePatchIntentSnapshot { Rank = "A" },
        nameof(SavePatchIntentSnapshot.LevelRanks) =>
            new SavePatchIntentSnapshot { LevelRanks = new Dictionary<int, string> { [0] = "A" } },
        nameof(SavePatchIntentSnapshot.UseNewGoodiesInstead) =>
            new SavePatchIntentSnapshot { UseNewGoodiesInstead = true },
        nameof(SavePatchIntentSnapshot.GlobalKillCount) => new SavePatchIntentSnapshot { GlobalKillCount = 7 },
        nameof(SavePatchIntentSnapshot.PerCategoryKills) =>
            new SavePatchIntentSnapshot { PerCategoryKills = new Dictionary<int, int> { [0] = 7 } },
        _ => throw new AssertionException(
            $"SavePatchIntentContract registers '{propertyName}' but this test does not know how to set " +
            $"it on a snapshot. Add the case.")
    };

    private static SavePatchRequest WithConfiguredRequest(string propertyName) => propertyName switch
    {
        nameof(SavePatchRequest.Rank) => new SavePatchRequest { Rank = "A" },
        nameof(SavePatchRequest.LevelRanks) =>
            new SavePatchRequest { LevelRanks = new Dictionary<int, string> { [0] = "A" } },
        nameof(SavePatchRequest.UseNewGoodiesInstead) => new SavePatchRequest { UseNewGoodiesInstead = true },
        nameof(SavePatchRequest.GlobalKillCount) => new SavePatchRequest { GlobalKillCount = 7 },
        nameof(SavePatchRequest.PerCategoryKills) =>
            new SavePatchRequest { PerCategoryKills = new Dictionary<int, int> { [0] = 7 } },
        _ => throw new AssertionException(
            $"SavePatchIntentContract registers '{propertyName}' but this test does not know how to set " +
            $"it on a SavePatchRequest. Add the case.")
    };
}
