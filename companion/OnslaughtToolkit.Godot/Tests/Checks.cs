// SPDX-License-Identifier: MIT
namespace OnslaughtToolkit.Companion.Tests;

/// <summary>Collects failed expectations so one run reports every broken contract.</summary>
internal sealed class Checks
{
    private readonly List<string> _failures = [];
    private string _suite = "";

    internal IReadOnlyList<string> Failures => _failures;
    internal int Count { get; private set; }

    internal void Suite(string name) => _suite = name;

    internal void That(bool condition, string message)
    {
        Count++;
        if (!condition) _failures.Add($"[{_suite}] {message}");
    }

    internal void Fail(string message) => That(false, message);
}
