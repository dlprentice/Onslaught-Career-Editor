// SPDX-License-Identifier: GPL-3.0-or-later

using Godot;
using OnslaughtRebuild.Core;
using System.Reflection;
using System.Security.Cryptography;
using D = Godot.Collections.Dictionary;
using A = Godot.Collections.Array;

namespace OnslaughtRebuild.GodotClient;

/// <summary>
/// Temporary test-only oracle. Calls the retained catalog and lookup methods;
/// never reads a replacement manifest, bypasses its SHA pin, or writes assets.
/// The caller may save the object-free result only to an explicit owned fixture.
/// </summary>
public sealed partial class HudCatalogReference : RefCounted
{
    public D LoadReference()
    {
        try
        {
            Level100HudAssetCatalog catalog = Level100HudAssetCatalog.Load();
            var messages = new D();
            var help = new D();
            var specs = new A();
            var messageLookups = new A();
            var helpLookups = new A();
            var failureLookups = new A();
            foreach (Level100MessageAudioSpec row in Level100AudioCatalog.CharacterMessages)
            {
                messages[row.MessageId] = Message(catalog.GetRequired(row.MessageId));
                specs.Add(new D { ["message_id"] = row.MessageId, ["symbol"] = Units(row.Symbol),
                    ["audio_stem"] = Units(row.AudioStem), ["resource_path"] = Units(row.ResourcePath) });
            }
            foreach (Level100HudHelpPrompt prompt in Enum.GetValues<Level100HudHelpPrompt>())
                help[(int)prompt] = Help(catalog.GetRequired(prompt));
            foreach (int identity in Level100AudioCatalog.CharacterMessages.Select(row => row.MessageId)
                .Concat([int.MinValue, -1, 0, 1, int.MaxValue]).Distinct())
            {
                bool found = catalog.TryGet(identity, out Level100HudMessageDefinition? definition);
                messageLookups.Add(new D { ["id"] = identity,
                    ["try_result"] = new D { ["ok"] = true, ["found"] = found,
                        ["value"] = definition is null ? default(Variant) : (Variant)Message(definition) },
                    ["required_result"] = Capture(() => Message(catalog.GetRequired(identity))) });
            }
            foreach (int identity in Enum.GetValues<Level100HudHelpPrompt>().Select(prompt => (int)prompt)
                .Concat([int.MinValue, -1, 0, 1, int.MaxValue]).Distinct())
                helpLookups.Add(new D { ["id"] = identity,
                    ["result"] = Capture(() => Help(catalog.GetRequired((Level100HudHelpPrompt)identity))) });
            foreach (int identity in new[] { int.MinValue, -1, 0, 1, 2, 3, 4, int.MaxValue })
                failureLookups.Add(new D { ["id"] = identity,
                    ["result"] = Capture(() => Units(catalog.TerminalStrings.GetFailureReason((Level100MissionFailureReason)identity))) });

            Level100HudTerminalStrings text = catalog.TerminalStrings;
            var terminal = new D { ["victory"] = Units(text.Victory), ["defeat"] = Units(text.Defeat),
                ["mission_complete"] = Units(text.MissionComplete), ["retry"] = Units(text.Retry),
                ["back"] = Units(text.Back), ["tutorial_broken"] = Units(text.TutorialBroken),
                ["player_death"] = Units(text.PlayerDeath), ["water"] = Units(text.Water) };
            var messageText = new D();
            var helpText = new D();
            foreach (Level100MessageAudioSpec row in Level100AudioCatalog.CharacterMessages)
                messageText[row.MessageId] = Units(catalog.GetRequired(row.MessageId).Text);
            foreach (Level100HudHelpPrompt prompt in Enum.GetValues<Level100HudHelpPrompt>())
                helpText[(int)prompt] = Units(catalog.GetRequired(prompt).Text);
            var batch = new D { ["schema"] = "onslaught-hud-verified-catalog.v1", ["messages"] = messageText,
                ["help"] = helpText, ["terminal"] = new D { ["victory"] = Units(text.Victory),
                    ["defeat"] = Units(text.Defeat), ["tutorial_broken"] = Units(text.TutorialBroken),
                    ["player_death"] = Units(text.PlayerDeath), ["water"] = Units(text.Water) } };
            var pins = new D();
            foreach (string name in new[] { "ResourcePath", "ExpectedSha256", "ExpectedSchema",
                "ExpectedLevelScriptSha256", "ExpectedEnglishSourceSha256", "ExpectedTextStfSha256", "ExpectedEnglishDatSha256" })
                pins[name] = Constant(name);
            byte[] data = Godot.FileAccess.GetFileAsBytes(Constant("ResourcePath"));
            byte[] whitespace = [.. data, (byte)'\n'];
            byte[] changed = (byte[])data.Clone();
            changed[0] ^= 1;
            // These hashes compare the reachable pre-parse rejection boundary.
            // No modified bytes are ever supplied to an unpinned C# catalog.
            var rejectedHashes = new D { ["empty_object"] = Hash("{}"u8.ToArray()),
                ["null"] = Hash("null"u8.ToArray()), ["malformed"] = Hash("{\"schemaVersion\":"u8.ToArray()),
                ["whitespace_only_change"] = Hash(whitespace), ["one_byte_corruption"] = Hash(changed) };
            return new D { ["ok"] = true, ["value"] = new D { ["schema"] = 1,
                ["pins"] = pins, ["manifest_sha256"] = Hash(data), ["messages"] = messages, ["help"] = help,
                ["terminal"] = terminal, ["character_specs"] = specs, ["batch"] = batch,
                ["message_lookups"] = messageLookups, ["help_lookups"] = helpLookups,
                ["failure_lookups"] = failureLookups, ["rejected_hashes"] = rejectedHashes } };
        }
        catch (Exception error)
        {
            return Failure(error);
        }
    }

    private static D Message(Level100HudMessageDefinition value) => new()
    {
        ["message_id"] = value.MessageId, ["symbol"] = Units(value.Symbol),
        ["audio_file"] = Units(value.AudioFile), ["text"] = Units(value.Text),
    };

    private static D Help(Level100HudHelpDefinition value) => new()
    {
        ["prompt"] = (int)value.Prompt, ["symbol"] = Units(value.Symbol), ["text"] = Units(value.Text),
    };

    private static D Capture(Func<Variant> action)
    {
        try { return new D { ["ok"] = true, ["value"] = action() }; }
        catch (Exception error) { return Failure(error); }
    }

    private static D Failure(Exception error) => new()
    {
        ["ok"] = false, ["error_type"] = error.GetType().Name, ["error"] = error.Message,
    };

    private static int[] Units(string value) => value.Select(unit => (int)unit).ToArray();
    private static string Hash(byte[] value) => Convert.ToHexString(SHA256.HashData(value)).ToLowerInvariant();
    private static string Constant(string name) =>
        (string)(typeof(Level100HudAssetCatalog).GetField(name, BindingFlags.Static | BindingFlags.NonPublic)
            ?.GetRawConstantValue() ?? throw new InvalidOperationException($"Catalog constant {name} disappeared."));
}
