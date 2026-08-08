using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.Cli
{
    /// <summary>
    /// The two write verbs that go through the same contracted services the GUI uses:
    /// <see cref="SaveEditorService"/> for career saves and <see cref="ConfigurationEditorService"/> for
    /// options files.
    ///
    /// The old CLI reached past both of these straight into <see cref="BesFilePatcher"/>. That was not
    /// merely inelegant - it meant the headless path and the GUI path could enforce different rules over
    /// the same bytes, and the headless one was the weaker of the two.
    /// </summary>
    public static class WriteVerbs
    {
        /// <summary>
        /// Patch career sections through <see cref="SaveEditorService.PatchSave"/>.
        ///
        /// Note this verb is deliberately narrower than the legacy invocation: <c>SavePatchRequest</c>
        /// carries career payloads only, and <c>SaveEditorService</c> requires .bes on both sides, so
        /// there is no way to reach an options file from here even with a flag. Career writes into a
        /// .bea remain possible only through the legacy form, which still demands
        /// <c>--allow-career-sections-on-options-file</c>.
        /// </summary>
        public static int SavesPatch(
            CliContext ctx,
            FileInfo? input,
            FileInfo? output,
            CareerPatchOptions options)
        {
            const string command = "saves.patch";
            if (input is null || output is null)
                return ctx.Usage(command, "Both an input and an output .bes file are required.");

            if (!input.Exists)
                return ctx.Usage(command, $"Input file not found: {input.FullName}");

            if (!SaveVerbs.TryRejectInPlaceWrite(ctx, command, input.FullName, output.FullName, out int refusal))
                return refusal;

            if (CareerPatchPlan.IsOptionsLikePath(input.FullName) || CareerPatchPlan.IsOptionsLikePath(output.FullName))
            {
                return ctx.Usage(
                    command,
                    "'saves patch' writes career sections and refuses .bea/defaultoptions files.",
                    "Use 'options edit' for options files, or the legacy form with --allow-career-sections-on-options-file.");
            }

            if (!CareerPatchPlan.TryResolve(options, out ResolvedCareerPatch plan, out string error, out IReadOnlyList<string> details))
                return ctx.Usage(command, error, details.ToArray());

            var request = new SavePatchRequest
            {
                InputPath = input.FullName,
                OutputPath = output.FullName,
                Rank = plan.Rank,
                UseNewGoodiesInstead = plan.UseNewGoodiesInstead,
                GlobalKillCount = plan.GlobalKillCount,
                PatchNodes = plan.PatchNodes,
                PatchLinks = plan.PatchLinks,
                PatchGoodies = plan.PatchGoodies,
                PatchKills = plan.PatchKills,
                LevelRanks = plan.LevelRanks,
                PerCategoryKills = plan.PerCategoryKills,
            };

            // Ask the shared contract first so the refusal message names the payload and the section that
            // would drop it, rather than surfacing as a generic patch failure.
            if (SavePatchIntentContract.DescribeDiscardedIntents(request.ToIntentSnapshot()) is { } discarded)
                return ctx.Usage(command, discarded);

            if (SavePatchIntentContract.DescribeEmptySectionPass(request.ToIntentSnapshot()) is { } emptyPass)
                return ctx.Usage(command, emptyPass);

            PatchResult result;
            try
            {
                result = SaveEditorService.PatchSave(request);
            }
            catch (Exception ex) when (SaveVerbs.IsFileAccessFailure(ex))
            {
                return ctx.Usage(command, SaveVerbs.DescribeFileFailure(ex));
            }

            object payload = new
            {
                input = input.FullName,
                output = output.FullName,
                route = "SaveEditorService.PatchSave",
                message = result.Message,
                pendingSummary = SaveEditorService.BuildPendingChangesSummary(request),
                plan = CareerPatchPlan.Project(plan),
            };

            if (!ctx.Json)
            {
                ctx.Line(result.Message);
                if (result.Success)
                    ctx.Line(SaveEditorService.BuildPendingChangesSummary(request));
            }

            return result.Success ? ctx.Ok(command, payload) : ctx.Verdict(command, result.Message, payload);
        }

        public sealed class OptionsEditRequest
        {
            public double? SoundVolume { get; init; }
            public double? MusicVolume { get; init; }
            public string? InvertWalkerP1 { get; init; }
            public string? InvertWalkerP2 { get; init; }
            public string? InvertFlightP1 { get; init; }
            public string? InvertFlightP2 { get; init; }
            public string? VibrationP1 { get; init; }
            public string? VibrationP2 { get; init; }
            public uint? ControllerConfigP1 { get; init; }
            public uint? ControllerConfigP2 { get; init; }
            public double? MouseSensitivity { get; init; }
            public uint? ScreenShape { get; init; }
            public FileInfo? CopyOptionsFrom { get; init; }
            public bool NoCopyOptionsEntries { get; init; }
            public bool NoCopyOptionsTail { get; init; }
            public IReadOnlyDictionary<string, string[]> Bindings { get; init; } =
                new Dictionary<string, string[]>();
        }

        /// <summary>
        /// Edit an options file.
        ///
        /// A .bea target goes through <see cref="ConfigurationEditorService.PatchConfiguration"/>, which
        /// is exactly what the GUI's Game Options page calls, keybind validation included. A .bes target
        /// cannot: that service requires .bea on both sides. Since the legacy invocation has always been
        /// able to write the CCareer settings block inside a career save, that capability is kept here
        /// on the direct patcher rather than quietly dropped - and the route taken is reported.
        /// </summary>
        public static int OptionsEdit(
            CliContext ctx,
            FileInfo? input,
            FileInfo? output,
            OptionsEditRequest request)
        {
            const string command = "options.edit";
            if (input is null || output is null)
                return ctx.Usage(command, "Both an input and an output file are required.");

            if (!input.Exists)
                return ctx.Usage(command, $"Input file not found: {input.FullName}");

            if (!SaveVerbs.TryRejectInPlaceWrite(ctx, command, input.FullName, output.FullName, out int refusal))
                return refusal;

            bool? invertWalkerP1, invertWalkerP2, invertFlightP1, invertFlightP2, vibrationP1, vibrationP2;
            try
            {
                invertWalkerP1 = KeybindTokens.ParseTriBool(request.InvertWalkerP1, "--invert-walker-p1");
                invertWalkerP2 = KeybindTokens.ParseTriBool(request.InvertWalkerP2, "--invert-walker-p2");
                invertFlightP1 = KeybindTokens.ParseTriBool(request.InvertFlightP1, "--invert-flight-p1");
                invertFlightP2 = KeybindTokens.ParseTriBool(request.InvertFlightP2, "--invert-flight-p2");
                vibrationP1 = KeybindTokens.ParseTriBool(request.VibrationP1, "--vibration-p1");
                vibrationP2 = KeybindTokens.ParseTriBool(request.VibrationP2, "--vibration-p2");
            }
            catch (ArgumentException ex)
            {
                return ctx.Usage(command, ex.Message);
            }

            if (request.CopyOptionsFrom is not null)
            {
                if (!request.CopyOptionsFrom.Exists)
                    return ctx.Usage(command, $"--copy-options-from file not found: {request.CopyOptionsFrom.FullName}");

                if (request.NoCopyOptionsEntries && request.NoCopyOptionsTail)
                {
                    return ctx.Usage(
                        command,
                        "--copy-options-from was provided, but both --no-copy-options-entries and --no-copy-options-tail were set (nothing to copy).");
                }
            }

            bool optionsFileTarget = CareerPatchPlan.IsOptionsLikePath(input.FullName) &&
                                     CareerPatchPlan.IsOptionsLikePath(output.FullName);

            PatchResult result;
            string route;

            if (optionsFileTarget)
            {
                route = "ConfigurationEditorService.PatchConfiguration";

                IReadOnlyList<ConfigurationKeybindRow> rows;
                try
                {
                    rows = ConfigurationEditorService.LoadKeybindRowsFromFile(input.FullName)
                        .Select(row => row.CloneForEditing())
                        .ToArray();
                }
                catch (InvalidDataException ex)
                {
                    return ctx.Verdict(command, ex.Message, new { file = input.FullName });
                }
                catch (Exception ex) when (SaveVerbs.IsFileAccessFailure(ex))
                {
                    return ctx.Usage(command, SaveVerbs.DescribeFileFailure(ex));
                }

                if (!KeybindTokens.TryApplyBindings(rows, request.Bindings, out string bindError))
                    return ctx.Usage(command, bindError);

                var patchRequest = new ConfigurationPatchRequest
                {
                    InputPath = input.FullName,
                    OutputPath = output.FullName,
                    SoundVolumeOverride = request.SoundVolume is { } sound ? (float)sound : null,
                    MusicVolumeOverride = request.MusicVolume is { } music ? (float)music : null,
                    InvertWalkerP1Override = invertWalkerP1,
                    InvertWalkerP2Override = invertWalkerP2,
                    InvertFlightP1Override = invertFlightP1,
                    InvertFlightP2Override = invertFlightP2,
                    VibrationP1Override = vibrationP1,
                    VibrationP2Override = vibrationP2,
                    ControllerConfigP1Override = request.ControllerConfigP1,
                    ControllerConfigP2Override = request.ControllerConfigP2,
                    MouseSensitivityOverride = request.MouseSensitivity is { } sens ? (float)sens : null,
                    ScreenShapeOverride = request.ScreenShape,
                    CopyOptionsFromPath = request.CopyOptionsFrom?.FullName,
                    CopyOptionsEntries = request.CopyOptionsFrom is not null && !request.NoCopyOptionsEntries,
                    CopyOptionsTail = request.CopyOptionsFrom is not null && !request.NoCopyOptionsTail,
                    KeybindRows = rows,
                };

                IReadOnlyList<string> keybindErrors = ConfigurationEditorService.ValidateKeybindRows(rows);
                if (keybindErrors.Count > 0)
                    return ctx.Usage(command, "Invalid keybind overrides.", keybindErrors.ToArray());

                result = ConfigurationEditorService.PatchConfiguration(patchRequest);
            }
            else
            {
                // A career save carrying a settings block. ConfigurationEditorService will not touch a
                // .bes, so this stays on the direct patcher with every career section switched off - the
                // settings-only mode the legacy CLI has always had.
                route = "BesFilePatcher (settings-only, .bes target)";

                Dictionary<int, BesFilePatcher.OptionsEntryOverride>? keybindOverrides;
                try
                {
                    keybindOverrides = KeybindTokens.ParseEntryOverrides(request.Bindings);
                }
                catch (ArgumentException ex)
                {
                    return ctx.Usage(command, ex.Message);
                }

                var patcher = new BesFilePatcher
                {
                    PatchNodes = false,
                    PatchLinks = false,
                    PatchGoodies = false,
                    PatchKills = false,
                    SoundVolumeOverride = request.SoundVolume is { } sound ? (float)sound : null,
                    MusicVolumeOverride = request.MusicVolume is { } music ? (float)music : null,
                    InvertYAxisP1Override = invertWalkerP1,
                    InvertYAxisP2Override = invertWalkerP2,
                    InvertFlightP1Override = invertFlightP1,
                    InvertFlightP2Override = invertFlightP2,
                    VibrationP1Override = vibrationP1,
                    VibrationP2Override = vibrationP2,
                    ControllerConfigP1Override = request.ControllerConfigP1,
                    ControllerConfigP2Override = request.ControllerConfigP2,
                    OptionsMouseSensitivityOverride = request.MouseSensitivity is { } sens ? (float)sens : null,
                    OptionsScreenShapeOverride = request.ScreenShape,
                    OptionsEntryOverrides = keybindOverrides,
                };

                if (request.CopyOptionsFrom is not null)
                {
                    patcher.CopyOptionsFromPath = request.CopyOptionsFrom.FullName;
                    patcher.CopyOptionsEntries = !request.NoCopyOptionsEntries;
                    patcher.CopyOptionsTail = !request.NoCopyOptionsTail;
                }

                try
                {
                    result = patcher.PatchFile(input.FullName, output.FullName);
                }
                catch (Exception ex) when (SaveVerbs.IsFileAccessFailure(ex))
                {
                    return ctx.Usage(command, SaveVerbs.DescribeFileFailure(ex));
                }
            }

            object payload = new
            {
                input = input.FullName,
                output = output.FullName,
                route,
                message = result.Message,
            };

            if (!ctx.Json)
                ctx.Line(result.Message);

            return result.Success ? ctx.Ok(command, payload) : ctx.Verdict(command, result.Message, payload);
        }
    }
}
