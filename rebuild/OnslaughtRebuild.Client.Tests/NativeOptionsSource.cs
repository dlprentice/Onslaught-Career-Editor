// SPDX-License-Identifier: GPL-3.0-or-later

namespace OnslaughtRebuild.Client.Tests;

/// <summary>Source routing for the existing focused Options consumer guards.</summary>
internal static class NativeOptionsSource
{
    public static string Read(string name) => File.ReadAllText(Path.Combine(
        AppContext.BaseDirectory, "godot-options-source", name));

    public static string Function(string name, string function)
    {
        string source = Read(name);
        string signature = $"func {function}(";
        int start = source.IndexOf(signature, StringComparison.Ordinal);
        Assert.True(start >= 0, $"{name}: {signature}");
        int next = source.IndexOf("\nfunc ", start, StringComparison.Ordinal);
        int nextStatic = source.IndexOf("\nstatic func ", start, StringComparison.Ordinal);
        if (next < 0 || nextStatic >= 0 && nextStatic < next) next = nextStatic;
        return next < 0 ? source[start..] : source[start..next];
    }
}
