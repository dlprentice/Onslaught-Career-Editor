// SPDX-License-Identifier: GPL-3.0-only
namespace OnslaughtToolkit.Companion.Missions;

/// <summary>Why a source cannot be compiled. <see cref="Line"/> is the 0-based line it was found on, when it has one; the message then starts "line N: " (counting from 1).</summary>
public class CompileError : Exception
{
    public CompileError(string message, int? line = null) : base(line is null ? message : $"line {line + 1}: {message}") => Line = line;

    public int? Line { get; }
}

/// <summary>An <c>#include</c> names a file the game folder does not hold (a few shipped scripts name files only the developers had).</summary>
public sealed class MissingInclude : CompileError
{
    public MissingInclude(string path) : base($"the included file {path} is not in the game folder") => Path = path;

    public string Path { get; }
}
