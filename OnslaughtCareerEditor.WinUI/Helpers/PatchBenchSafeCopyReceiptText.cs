using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using OnslaughtCareerEditor.WinUI.Models;

namespace OnslaughtCareerEditor.WinUI.Helpers
{
    internal static class PatchBenchSafeCopyReceiptText
    {
        public static string Build(PatchBenchSafeCopyReceiptTextState state)
        {
            ArgumentNullException.ThrowIfNull(state);

            string headline = NormalizeDisplayText(state.Headline);
            PatchBenchReceiptLineTextState[] lines = (state.Lines ?? Array.Empty<PatchBenchReceiptLineTextState>())
                .Select(line => new PatchBenchReceiptLineTextState(
                    NormalizeDisplayText(line.Label),
                    NormalizeDisplayText(line.Value)))
                .ToArray();
            string[] includedChanges = NormalizeList(state.IncludedChanges);
            string[] stillNotIncluded = NormalizeList(state.StillNotIncluded);

            var builder = new StringBuilder();
            builder.AppendLine(headline);
            foreach (PatchBenchReceiptLineTextState line in lines)
            {
                string lineText = $"{line.Label}: {line.Value}";
                ThrowIfUnsafeDisplayValue(lineText, nameof(state));
                builder.AppendLine(lineText);
            }

            builder.AppendLine();
            builder.AppendLine("Included changes");
            foreach (string change in includedChanges)
            {
                builder.AppendLine($"- {change}");
            }

            builder.AppendLine();
            builder.AppendLine("Still not included");
            foreach (string limit in stillNotIncluded)
            {
                builder.AppendLine($"- {limit}");
            }

            string output = builder.ToString().TrimEnd();
            ThrowIfUnsafeDisplayValue(output, nameof(state));
            return output;
        }

        private static string[] NormalizeList(IReadOnlyList<string>? values)
        {
            return (values ?? Array.Empty<string>())
                .Select(NormalizeDisplayText)
                .Where(value => !string.IsNullOrWhiteSpace(value))
                .ToArray();
        }

        private static string NormalizeDisplayText(string? value)
        {
            string text = value ?? string.Empty;
            var builder = new StringBuilder(text.Length);
            bool pendingSpace = false;

            foreach (char current in text.Trim())
            {
                if (char.IsWhiteSpace(current))
                {
                    pendingSpace = true;
                    continue;
                }

                if (pendingSpace && builder.Length > 0)
                {
                    builder.Append(' ');
                }

                builder.Append(current);
                pendingSpace = false;
            }

            string normalized = builder.ToString();
            ThrowIfUnsafeDisplayValue(normalized, nameof(value));
            return normalized;
        }

        private static void ThrowIfUnsafeDisplayValue(string value, string? parameterName)
        {
            if (ContainsUnsafeDisplayValue(value))
            {
                throw new ArgumentException("Receipt text contains unsafe display value.", parameterName);
            }
        }

        private static bool ContainsUnsafeDisplayValue(string value)
        {
            if (string.IsNullOrWhiteSpace(value))
            {
                return false;
            }

            string lower = value.ToLowerInvariant();
            string compact = BuildCompactDisplayToken(lower);
            return ContainsDriveRoot(value) ||
                ContainsRepeatedSeparator(value) ||
                ContainsSeparated(lower, "users") ||
                ContainsSeparated(lower, "appdata") ||
                lower.Contains("/home/", StringComparison.Ordinal) ||
                lower.Contains("/mnt/", StringComparison.Ordinal) ||
                lower.Contains("program files", StringComparison.Ordinal) ||
                lower.Contains("steamapps", StringComparison.Ordinal) ||
                UnsafeFragments.Any(fragment => lower.Contains(fragment, StringComparison.Ordinal)) ||
                UnsafeCompactFragments.Any(fragment => compact.Contains(fragment, StringComparison.Ordinal));
        }

        private static bool ContainsDriveRoot(string value)
        {
            for (int i = 0; i + 2 < value.Length; i++)
            {
                if (char.IsAsciiLetter(value[i]) &&
                    value[i + 1] == ':' &&
                    IsDirectorySeparator(value[i + 2]))
                {
                    return true;
                }
            }

            return false;
        }

        private static bool ContainsRepeatedSeparator(string value)
        {
            for (int i = 0; i + 1 < value.Length; i++)
            {
                if (IsDirectorySeparator(value[i]) && IsDirectorySeparator(value[i + 1]))
                {
                    return true;
                }
            }

            return false;
        }

        private static string BuildCompactDisplayToken(string value)
        {
            var builder = new StringBuilder(value.Length);
            foreach (char current in value)
            {
                if (char.IsLetterOrDigit(current))
                {
                    builder.Append(current);
                }
            }

            return builder.ToString();
        }

        private static bool ContainsSeparated(string value, string token)
        {
            return value.Contains(Join("\\", token, "\\"), StringComparison.Ordinal) ||
                value.Contains(Join("/", token, "/"), StringComparison.Ordinal);
        }

        private static bool IsDirectorySeparator(char value)
        {
            return value == '\\' || value == '/';
        }

        private static string Join(params string[] parts)
        {
            return string.Concat(parts);
        }

        private static readonly string[] UnsafeFragments =
        [
            Join("proof", "-id"),
            Join("proof", "_id"),
            Join("proof", "-root"),
            Join("proof", "_root"),
            Join("runtime", "-proof-"),
            Join("start", "-process"),
            Join("command", "preview"),
            Join("source", "path"),
            Join("manifest", "path"),
            Join("proof", "id"),
            Join("target", "gameroot"),
            Join("target", "executable", "path"),
            Join("online", "-ready"),
            Join("online", " session"),
            Join("enable ", "host"),
            Join("enable ", "join"),
            Join("public", " matchmaking"),
            Join("net", "play"),
            Join("host/join ", "available"),
            Join("host/join ", "enabled"),
        ];

        private static readonly string[] UnsafeCompactFragments =
        [
            Join("proof", "id"),
            Join("proof", "root"),
            Join("runtime", "proof"),
            Join("start", "process"),
            Join("command", "preview"),
            Join("source", "path"),
            Join("manifest", "path"),
            Join("target", "game", "root"),
            Join("target", "executable", "path"),
            Join("online", "ready"),
            Join("online", "session"),
            Join("online", "play", "ready"),
            Join("online", "play", "available"),
            Join("online", "multiplayer", "ready"),
            Join("online", "multiplayer", "available"),
            Join("online", "multiplayer", "enabled"),
            Join("online", "multiplayer", "supported"),
            Join("online", "multiplayer", "unlocked"),
            Join("multiplayer", "ready"),
            Join("public", "matchmaking"),
            Join("net", "play"),
            Join("lan", "play", "available"),
            Join("enable", "host"),
            Join("enable", "join"),
            Join("host", "game", "available"),
            Join("join", "game", "available"),
            Join("host", "join", "available"),
            Join("host", "join", "enabled"),
            Join("host", "join", "ready"),
            Join("host", "join", "supported"),
            Join("host", "join", "unlocked"),
            Join("host", "and", "join", "available"),
            Join("host", "and", "join", "enabled"),
            Join("host", "and", "join", "ready"),
            Join("host", "and", "join", "supported"),
            Join("host", "and", "join", "unlocked"),
            Join("onslaught", "profile", "manifest", "json"),
        ];
    }
}
