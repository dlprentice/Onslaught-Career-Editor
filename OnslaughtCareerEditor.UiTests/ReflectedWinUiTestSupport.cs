using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using NUnit.Framework;

namespace OnslaughtCareerEditor.UiTests;

internal static class ReflectedWinUiTestSupport
{
    private const string WinUiAssemblyPathEnvironmentVariable = "ONSLAUGHT_WINUI_TEST_ASSEMBLY_PATH";
    private static readonly object s_resolverLock = new();
    private static string? s_assemblyDirectory;
    private static bool s_resolverRegistered;

    internal static Type GetRequiredType(string fullName, params string[] reflectedWinUiSourceRelativePaths)
    {
        Assembly assembly = LoadWinUiAssembly(reflectedWinUiSourceRelativePaths);
        return assembly.GetType(fullName, throwOnError: true)!;
    }

    internal static object InvokeRequiredStaticMethod(Type type, string methodName, params object?[] arguments)
    {
        MethodInfo method = type.GetMethod(methodName, BindingFlags.Static | BindingFlags.Public)
            ?? throw new InvalidOperationException($"Missing public static method {type.FullName}.{methodName}.");
        return method.Invoke(null, arguments)
            ?? throw new InvalidOperationException($"{type.FullName}.{methodName} returned null.");
    }

    internal static string GetStringProperty(object instance, string propertyName)
    {
        PropertyInfo property = instance.GetType().GetProperty(propertyName, BindingFlags.Instance | BindingFlags.Public)
            ?? throw new InvalidOperationException($"Missing text-state property {propertyName}.");
        return (string)(property.GetValue(instance) ?? throw new InvalidOperationException($"Text-state property {propertyName} was null."));
    }

    private static Assembly LoadWinUiAssembly(IReadOnlyCollection<string> reflectedWinUiSourceRelativePaths)
    {
        string assemblyPath = ResolveWinUiAssemblyPath();
        Assert.That(
            File.Exists(assemblyPath),
            Is.True,
            $"WinUI build output not found at {assemblyPath}. Run dotnet build .\\OnslaughtCareerEditor.WinUI\\OnslaughtCareerEditor.WinUI.csproj --nologo before reflected WinUI helper-output tests.");
        AssertWinUiAssemblyIsFresh(assemblyPath, reflectedWinUiSourceRelativePaths);

        string assemblyDirectory = Path.GetDirectoryName(assemblyPath)
            ?? throw new InvalidOperationException("WinUI assembly path did not include a directory.");
        RegisterAssemblyResolver(assemblyDirectory);
        return Assembly.LoadFrom(assemblyPath);
    }

    private static void AssertWinUiAssemblyIsFresh(
        string assemblyPath,
        IReadOnlyCollection<string> reflectedWinUiSourceRelativePaths)
    {
        DateTime assemblyWriteTime = File.GetLastWriteTimeUtc(assemblyPath);
        var missingSources = new List<string>();
        var staleSources = new List<string>();

        foreach (string sourcePath in reflectedWinUiSourceRelativePaths.Select(ResolveRepoPath))
        {
            if (!File.Exists(sourcePath))
            {
                missingSources.Add(sourcePath);
                continue;
            }

            if (File.GetLastWriteTimeUtc(sourcePath) > assemblyWriteTime)
            {
                staleSources.Add(sourcePath);
            }
        }

        Assert.That(
            missingSources,
            Is.Empty,
            $"WinUI source file(s) needed by this reflection test are missing: {string.Join(", ", missingSources)}");
        Assert.That(
            staleSources,
            Is.Empty,
            $"WinUI build output at {assemblyPath} is older than reflected WinUI source file(s): {string.Join(", ", staleSources)}. Run dotnet build .\\OnslaughtCareerEditor.WinUI\\OnslaughtCareerEditor.WinUI.csproj --nologo before reflected WinUI helper-output tests.");
    }

    private static string ResolveWinUiAssemblyPath()
    {
        string? explicitPath = Environment.GetEnvironmentVariable(WinUiAssemblyPathEnvironmentVariable);
        if (!string.IsNullOrWhiteSpace(explicitPath))
        {
            return explicitPath;
        }

        return Path.Combine(
            TestFixturePaths.RepoRoot,
            "OnslaughtCareerEditor.WinUI",
            "bin",
            "Debug",
            "net10.0-windows10.0.19041.0",
            "win-x64",
            "OnslaughtCareerEditor.WinUI.dll");
    }

    private static string ResolveRepoPath(string relativePath)
    {
        string[] parts = relativePath.Split(['/', '\\'], StringSplitOptions.RemoveEmptyEntries);
        return Path.Combine(parts.Prepend(TestFixturePaths.RepoRoot).ToArray());
    }

    private static void RegisterAssemblyResolver(string assemblyDirectory)
    {
        lock (s_resolverLock)
        {
            s_assemblyDirectory = assemblyDirectory;
            if (s_resolverRegistered)
            {
                return;
            }

            AppDomain.CurrentDomain.AssemblyResolve += ResolveAssemblyFromWinUiOutput;
            s_resolverRegistered = true;
        }
    }

    private static Assembly? ResolveAssemblyFromWinUiOutput(object? sender, ResolveEventArgs args)
    {
        string? assemblyDirectory;
        lock (s_resolverLock)
        {
            assemblyDirectory = s_assemblyDirectory;
        }

        if (string.IsNullOrWhiteSpace(assemblyDirectory))
        {
            return null;
        }

        string dependencyPath = Path.Combine(assemblyDirectory, $"{new AssemblyName(args.Name).Name}.dll");
        return File.Exists(dependencyPath) ? Assembly.LoadFrom(dependencyPath) : null;
    }
}
