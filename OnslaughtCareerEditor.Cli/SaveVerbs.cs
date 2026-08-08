using System;
using System.Buffers.Binary;
using System.Collections.Generic;
using System.IO;
using System.Linq;

using OnslaughtCareerEditor.AppCore;

namespace OnslaughtCareerEditor.Cli
{
    /// <summary>
    /// The read/write operations over saves, options files, and app configuration.
    ///
    /// Every function here is the single implementation behind both the new verb and, where one exists,
    /// the legacy flag that used to do the same job. They cannot drift, because there is only one of
    /// each.
    /// </summary>
    public static class SaveVerbs
    {
        // ---------------------------------------------------------------- config

        public static int ConfigShow(CliContext ctx)
        {
            const string command = "config.show";
            AppConfig config = AppConfig.Load();
            string? gameDir = config.GetGameDir();
            string? detected = AppConfig.DetectGameDirectory();

            if (ctx.Json)
            {
                return ctx.Ok(command, new
                {
                    configPath = AppConfig.GetConfigPath(),
                    gameDirectory = gameDir,
                    autoDetected = detected,
                    patchedOutputDir = AppConfig.GetPatchedOutputDir(),
                    gameProfilesDir = AppConfig.GetGameProfilesDir(),
                    maxRecentFiles = config.MaxRecentFiles,
                    windowWidth = config.WindowWidth,
                    windowHeight = config.WindowHeight,
                    lastTab = config.LastTab,
                    appTheme = config.AppTheme,
                    recentFiles = config.RecentFiles
                        .Select(file => new { path = file, exists = File.Exists(file) })
                        .ToArray(),
                });
            }

            ctx.Line("Onslaught Career Editor - Configuration");
            ctx.Line("=======================================");
            ctx.Line($"Config file: {AppConfig.GetConfigPath()}");
            ctx.Line();
            ctx.Line($"Game directory:     {gameDir ?? "(not set)"}");
            ctx.Line($"Auto-detected:      {detected ?? "(not found)"}");
            ctx.Line($"Safe copy root:     {AppConfig.GetGameProfilesDir()}");
            ctx.Line($"Patched output dir: {AppConfig.GetPatchedOutputDir()}");
            ctx.Line($"Max recent files:   {config.MaxRecentFiles}");
            ctx.Line($"Window size:        {config.WindowWidth}x{config.WindowHeight}");
            ctx.Line($"Last tab:           {config.LastTab}");

            if (config.RecentFiles.Count > 0)
            {
                ctx.Line();
                ctx.Line($"Recent files ({config.RecentFiles.Count}):");
                foreach (string file in config.RecentFiles)
                    ctx.Line($"  {(File.Exists(file) ? "[OK]" : "[X]")} {file}");
            }

            return CliExit.Success;
        }

        public static int ConfigSetGameDir(CliContext ctx, string? path)
        {
            const string command = "config.set-game-dir";
            if (string.IsNullOrWhiteSpace(path))
                return ctx.Usage(command, "A game directory path is required.");

            if (!Directory.Exists(path))
                return ctx.Usage(command, $"Directory not found: {path}");

            AppConfig config = AppConfig.Load();
            if (!config.SetGameDir(path))
                return ctx.Usage(command, $"Failed to persist game directory: {path}");

            return ctx.Ok(
                command,
                new { gameDirectory = config.GetGameDir() ?? path },
                $"Game directory set to: {path}");
        }

        /// <summary>
        /// Auto-detection is the clearest case for exit 2: the tool ran exactly as asked, and the answer
        /// is that no install could be found. That is a result, not a failure to operate.
        /// </summary>
        public static int ConfigDetect(CliContext ctx)
        {
            const string command = "config.detect";
            string? detected = AppConfig.DetectGameDirectory();
            GameDirectoryInspection inspection = AppConfig.InspectGameDirectory(detected);

            object payload = new
            {
                detected,
                status = inspection.Status.ToString(),
                fullPath = inspection.FullPath,
                hasExecutable = inspection.HasExecutable,
                hasData = inspection.HasData,
                hasMusic = inspection.HasMusic,
                hasVideo = inspection.HasVideo,
            };

            if (detected is null)
            {
                if (!ctx.Json)
                {
                    ctx.Line("No Battle Engine Aquila installation was detected.");
                    ctx.Line("Set one explicitly with: config set-game-dir <path>");
                }

                return ctx.Verdict(command, "No Battle Engine Aquila installation was detected.", payload);
            }

            if (!ctx.Json)
            {
                ctx.Line($"Detected: {detected}");
                ctx.Line($"  Status:     {inspection.Status}");
                ctx.Line($"  Executable: {(inspection.HasExecutable ? "yes" : "no")}");
                ctx.Line($"  Data:       {(inspection.HasData ? "yes" : "no")}");
                ctx.Line($"  Music:      {(inspection.HasMusic ? "yes" : "no")}");
                ctx.Line($"  Video:      {(inspection.HasVideo ? "yes" : "no")}");
            }

            return ctx.Ok(command, payload);
        }

        // ---------------------------------------------------------------- saves list

        public static int SavesList(CliContext ctx)
        {
            const string command = "saves.list";
            AppConfig config = AppConfig.Load();
            string? effectiveDir = config.GetGameDir() ?? AppConfig.DetectGameDirectory();

            if (effectiveDir is null)
            {
                return ctx.Usage(
                    command,
                    "Game directory not configured and could not be auto-detected.",
                    "Use 'config set-game-dir <path>' to specify the game installation folder.");
            }

            List<SaveFileInfo> saves = AppConfig.FindSaveFiles(effectiveDir);

            if (ctx.Json)
            {
                return ctx.Ok(command, new
                {
                    searchedDirectory = effectiveDir,
                    count = saves.Count,
                    expectedFileSize = BesFilePatcher.EXPECTED_FILE_SIZE,
                    expectedVersionWord = BesFilePatcher.VERSION_WORD,
                    saves = saves.Select(save => new
                    {
                        name = save.Name,
                        path = save.Path,
                        size = save.Size,
                        modified = save.Modified,
                        isValid = save.IsValid,
                    }).ToArray(),
                });
            }

            ctx.Line("Onslaught Career Editor - Save Files");
            ctx.Line("====================================");
            ctx.Line($"Searching in: {effectiveDir}");
            ctx.Line();

            if (saves.Count == 0)
            {
                ctx.Line("No .bes/.bea save/options files found.");
                return CliExit.Success;
            }

            ctx.Line($"Found {saves.Count} save file(s):");
            ctx.Line();
            ctx.Line($"{"Name",-30} {"Size",-12} {"Modified",-20} {"Valid"}");
            ctx.Line(new string('-', 70));

            foreach (SaveFileInfo save in saves)
            {
                string sizeStr = save.Size == BesFilePatcher.EXPECTED_FILE_SIZE
                    ? $"{BesFilePatcher.EXPECTED_FILE_SIZE:N0} B"
                    : $"{save.Size:N0} B";
                ctx.Line($"{save.Name,-30} {sizeStr,-12} {save.Modified:yyyy-MM-dd HH:mm,-20} {(save.IsValid ? "Yes" : "No*")}");
            }

            ctx.Line();
            ctx.Line("Paths:");
            foreach (SaveFileInfo save in saves)
                ctx.Line($"  {save.Path}");

            ctx.Line();
            ctx.Line($"* Invalid format: expected {BesFilePatcher.EXPECTED_FILE_SIZE:N0} bytes and version word 0x{BesFilePatcher.VERSION_WORD:X4}");
            return CliExit.Success;
        }

        // ---------------------------------------------------------------- saves analyze / compare

        /// <summary>
        /// Analysis reads the structured document AppCore already builds, rather than only the rendered
        /// string. The string is still emitted for humans and still carried in the JSON payload, but a
        /// caller no longer has to scrape it: the metrics, the summary tree, and the per-slot Goodie
        /// states come through as data.
        /// </summary>
        public static int SavesAnalyze(CliContext ctx, FileInfo? input, bool verbose, bool dumpMystery)
        {
            const string command = "saves.analyze";
            if (input is null)
                return ctx.Usage(command, "An input .bes/.bea file is required.");

            if (!input.Exists)
                return ctx.Usage(command, $"Input file not found: {input.FullName}");

            SaveAnalysis analysis;
            SaveAnalyzerDocument document;
            try
            {
                analysis = BesFilePatcher.AnalyzeSave(input.FullName);
                document = SaveAnalyzerService.BuildAnalysisDocument(analysis, verbose, dumpMystery);
            }
            catch (Exception ex) when (IsFileAccessFailure(ex))
            {
                return ctx.Usage(command, DescribeFileFailure(ex));
            }

            object payload = new
            {
                file = input.FullName,
                isValid = analysis.IsValid,
                errorMessage = analysis.ErrorMessage,
                document = ProjectDocument(document),
                analysis = ProjectAnalysis(analysis),
            };

            if (!ctx.Json)
                ctx.Line(document.ReportText);

            // The file parsed, so the tool did its job; "this save is not valid" is the answer, not a
            // failure of the run. That is the whole reason exit 2 exists.
            return analysis.IsValid
                ? ctx.Ok(command, payload)
                : ctx.Verdict(command, analysis.ErrorMessage ?? "The file is not a valid BEA save.", payload);
        }

        public static int SavesCompare(CliContext ctx, FileInfo? left, FileInfo? right)
        {
            const string command = "saves.compare";
            if (left is null || right is null)
                return ctx.Usage(command, "Two files are required to compare.");

            if (!left.Exists)
                return ctx.Usage(command, $"Input file not found: {left.FullName}");

            if (!right.Exists)
                return ctx.Usage(command, $"Compare file not found: {right.FullName}");

            BesFilePatcher.CompareResult result;
            SaveAnalyzerDocument document;
            try
            {
                result = BesFilePatcher.CompareFiles(left.FullName, right.FullName);
                document = SaveAnalyzerService.BuildCompareDocument(left.FullName, right.FullName, result);
            }
            catch (Exception ex) when (IsFileAccessFailure(ex))
            {
                return ctx.Usage(command, DescribeFileFailure(ex));
            }

            if (!ctx.Json)
                ctx.Line(document.ReportText);

            // Finding differences is a successful comparison, not a negative verdict: the caller asked
            // what differs and got a complete answer. The verdict lives in `identical`.
            return ctx.Ok(command, new
            {
                left = left.FullName,
                right = right.FullName,
                identical = result.DifferingBytes == 0 && result.SameSize,
                sameSize = result.SameSize,
                leftSize = result.File1Size,
                rightSize = result.File2Size,
                differingBytes = result.DifferingBytes,
                errorMessage = result.ErrorMessage,
                regionCounts = result.RegionCounts
                    .OrderByDescending(row => row.Value)
                    .Select(row => new { region = row.Key, bytes = row.Value })
                    .ToArray(),
                diffRanges = result.DiffRanges
                    .Select(range => new { start = range.Start, end = range.End })
                    .ToArray(),
                document = ProjectDocument(document),
            });
        }

        // ---------------------------------------------------------------- goodies

        public static int GoodiesList(CliContext ctx, FileInfo? input, bool showReserved)
        {
            const string command = "goodies.list";
            if (input is null)
                return ctx.Usage(command, "An input .bes/.bea file is required.");

            if (!input.Exists)
                return ctx.Usage(command, $"Input file not found: {input.FullName}");

            const int careerBase = 0x0002;
            const int ccareerGoodieBase = 0x1F44;
            const int goodieBase = careerBase + ccareerGoodieBase; // 0x1F46 in file space
            const int goodieCount = 300;
            const int displayableCount = 233;

            byte[] buf;
            try
            {
                buf = File.ReadAllBytes(input.FullName);
            }
            catch (Exception ex) when (IsFileAccessFailure(ex))
            {
                return ctx.Usage(command, DescribeFileFailure(ex));
            }

            // A wrong-sized or wrong-version file is a verdict about the data, not a broken invocation.
            if (buf.Length != BesFilePatcher.EXPECTED_FILE_SIZE)
            {
                return ctx.Verdict(
                    command,
                    $"Invalid file size {buf.Length:N0} bytes (expected {BesFilePatcher.EXPECTED_FILE_SIZE:N0}).",
                    new { file = input.FullName, fileSize = buf.Length });
            }

            ushort versionWord = BinaryPrimitives.ReadUInt16LittleEndian(buf.AsSpan(0, 2));
            if (versionWord != BesFilePatcher.VERSION_WORD)
            {
                return ctx.Verdict(
                    command,
                    $"Invalid version word 0x{versionWord:X4} (expected 0x{BesFilePatcher.VERSION_WORD:X4}).",
                    new { file = input.FullName, versionWord });
            }

            var slots = new List<object>(goodieCount);
            int countNew = 0, countOld = 0, countLocked = 0, countInstructions = 0, countOther = 0, countReserved = 0;

            if (!ctx.Json)
            {
                ctx.Line("Onslaught Career Editor - Goodie List");
                ctx.Line("=====================================");
                ctx.Line($"File: {input.FullName}");
                ctx.Line($"Version: 0x{versionWord:X4}");
                ctx.Line($"Display mode: {(showReserved ? "all 300 slots" : "displayable slots (0-232)")}");
                ctx.Line();
                ctx.Line($"{"Idx",4} {"Offset",8} {"State",-13} {"Raw",-10} {"Scope",-11}");
                ctx.Line(new string('-', 52));
            }

            for (int i = 0; i < goodieCount; i++)
            {
                int off = goodieBase + i * 4;
                uint raw = BinaryPrimitives.ReadUInt32LittleEndian(buf.AsSpan(off, 4));
                bool reserved = i >= displayableCount;
                string state = ClassifyGoodie(i, raw, displayableCount);
                string scope = reserved ? "Reserved" : "Displayable";

                switch (state)
                {
                    case "NEW": countNew++; break;
                    case "OLD": countOld++; break;
                    case "LOCKED": countLocked++; break;
                    case "INSTRUCTIONS": countInstructions++; break;
                    case "OTHER": countOther++; break;
                    case "RESERVED": countReserved++; break;
                }

                if (!showReserved && reserved)
                    continue;

                if (ctx.Json)
                {
                    slots.Add(new { index = i, offset = off, state, raw, scope });
                }
                else
                {
                    ctx.Line($"{i,4} 0x{off:X4} {state,-13} 0x{raw:X8} {scope,-11}");
                }
            }

            int unlocked = countNew + countOld;

            if (ctx.Json)
            {
                return ctx.Ok(command, new
                {
                    file = input.FullName,
                    versionWord,
                    showReserved,
                    displayableCount,
                    summary = new
                    {
                        unlocked,
                        @new = countNew,
                        old = countOld,
                        locked = countLocked,
                        lockedWithHint = countInstructions,
                        other = countOther,
                        reserved = countReserved,
                    },
                    slots = slots.ToArray(),
                });
            }

            ctx.Line();
            ctx.Line("Summary (displayable slots 0-232):");
            ctx.Line($"  Unlocked: {unlocked}/{displayableCount} (NEW {countNew}, OLD {countOld})");
            ctx.Line($"  Locked: {countLocked}");
            ctx.Line($"  Locked with hint: {countInstructions}");
            if (countOther > 0)
                ctx.Line($"  Other: {countOther}");
            ctx.Line($"  Reserved slots: {countReserved}");
            if (!showReserved)
                ctx.Line("  Note: Reserved rows hidden; use --show-reserved to include them.");

            return CliExit.Success;
        }

        /// <summary>
        /// Write targeted Goodie states.
        ///
        /// A single slot goes through <see cref="SaveEditorService.PatchFocusedGoodieState"/> - the exact
        /// call the GUI's focused write makes, which brings the app-owned safe-copy savegames
        /// authorization with it. Multiple slots have no single-call twin in AppCore (the focused API
        /// takes one id), so they fall back to the bulk codec the legacy flag has always used. The route
        /// taken is reported rather than hidden, because the two do not carry the same guarantees.
        /// </summary>
        public static int GoodiesSet(
            CliContext ctx,
            FileInfo? input,
            FileInfo? output,
            IReadOnlyList<string>? entries)
        {
            const string command = "goodies.set";
            if (input is null || output is null)
                return ctx.Usage(command, "Both an input and an output .bes file are required.");

            if (!input.Exists)
                return ctx.Usage(command, $"Input file not found: {input.FullName}");

            if (entries is null || entries.Count == 0)
                return ctx.Usage(command, "Choose at least one --goodie INDEX:STATE override.");

            if (!TryParseGoodieStateOverrides(entries, out Dictionary<int, uint> overrides, out string parseError))
                return ctx.Usage(command, parseError);

            if (!TryRejectInPlaceWrite(ctx, command, input.FullName, output.FullName, out int refusal))
                return refusal;

            PatchResult result;
            string route;
            if (overrides.Count == 1)
            {
                KeyValuePair<int, uint> only = overrides.First();
                route = "focused";
                result = SaveEditorService.PatchFocusedGoodieState(new FocusedGoodieStatePatchRequest
                {
                    InputPath = input.FullName,
                    OutputPath = output.FullName,
                    GoodieId = only.Key,
                    State = (MissionScriptGoodieState)only.Value,
                });
            }
            else
            {
                route = "bulk";
                try
                {
                    result = BesFilePatcher.PatchGoodieStates(input.FullName, output.FullName, overrides);
                }
                catch (Exception ex) when (IsFileAccessFailure(ex))
                {
                    return ctx.Usage(command, DescribeFileFailure(ex));
                }
            }

            object payload = new
            {
                input = input.FullName,
                output = output.FullName,
                route,
                message = result.Message,
                overrides = overrides
                    .OrderBy(pair => pair.Key)
                    .Select(pair => new { index = pair.Key, state = pair.Value, stateName = GoodieStateName(pair.Value) })
                    .ToArray(),
            };

            if (!ctx.Json)
            {
                ctx.Line(result.Message);
                if (result.Success)
                    ctx.Line("Targeted Goodie state setup used true-view offsets and wrote only requested Goodie slots.");
            }

            return result.Success
                ? ctx.Ok(command, payload)
                : ctx.Verdict(command, result.Message, payload);
        }

        // ---------------------------------------------------------------- options

        public static int OptionsShow(CliContext ctx, FileInfo? input)
        {
            const string command = "options.show";
            if (input is null)
                return ctx.Usage(command, "An input .bea options file is required.");

            if (!input.Exists)
                return ctx.Usage(command, $"Input file not found: {input.FullName}");

            ConfigurationSnapshot snapshot;
            try
            {
                snapshot = ConfigurationEditorService.LoadConfigurationSnapshot(input.FullName);
            }
            catch (InvalidDataException ex)
            {
                // The file was read and rejected on its contents: a data verdict.
                return ctx.Verdict(command, ex.Message, new { file = input.FullName });
            }
            catch (Exception ex) when (IsFileAccessFailure(ex))
            {
                return ctx.Usage(command, DescribeFileFailure(ex));
            }

            object payload = new
            {
                file = snapshot.FilePath,
                fileName = snapshot.FileName,
                soundVolume = snapshot.SoundVolume,
                musicVolume = snapshot.MusicVolume,
                invertWalkerP1 = snapshot.InvertWalkerP1,
                invertWalkerP2 = snapshot.InvertWalkerP2,
                invertFlightP1 = snapshot.InvertFlightP1,
                invertFlightP2 = snapshot.InvertFlightP2,
                vibrationP1 = snapshot.VibrationP1,
                vibrationP2 = snapshot.VibrationP2,
                controllerConfigP1 = snapshot.ControllerConfigP1,
                controllerConfigP2 = snapshot.ControllerConfigP2,
                optionsEntryCount = snapshot.OptionsEntryCount,
                mouseSensitivity = snapshot.MouseSensitivity,
                controlSchemeIndex = snapshot.ControlSchemeIndex,
                languageIndex = snapshot.LanguageIndex,
                screenShape = snapshot.ScreenShape,
                d3dDeviceIndex = snapshot.D3DDeviceIndex,
                keybinds = snapshot.KeybindRows.Select(row => new
                {
                    group = row.GroupLabel,
                    action = row.ActionLabel,
                    entryId = row.EntryId,
                    player1 = row.CurrentPlayer1Token,
                    player2 = row.CurrentPlayer2Token,
                }).ToArray(),
            };

            if (!ctx.Json)
            {
                ctx.Line($"Game Options: {snapshot.FileName}");
                ctx.Line(new string('=', 40));
                ctx.Line($"  Sound volume:   {snapshot.SoundVolume:0.###}");
                ctx.Line($"  Music volume:   {snapshot.MusicVolume:0.###}");
                ctx.Line($"  Invert Y (Walker): P1={(snapshot.InvertWalkerP1 ? "On" : "Off")} P2={(snapshot.InvertWalkerP2 ? "On" : "Off")}");
                ctx.Line($"  Invert Y (Flight): P1={(snapshot.InvertFlightP1 ? "On" : "Off")} P2={(snapshot.InvertFlightP2 ? "On" : "Off")}");
                ctx.Line($"  Vibration:      P1={(snapshot.VibrationP1 ? "On" : "Off")} P2={(snapshot.VibrationP2 ? "On" : "Off")}");
                ctx.Line($"  Ctrl config:    P1={snapshot.ControllerConfigP1} P2={snapshot.ControllerConfigP2}");
                ctx.Line($"  Mouse sens:     {snapshot.MouseSensitivity:0.###}");
                ctx.Line($"  Control scheme: {snapshot.ControlSchemeIndex}");
                ctx.Line($"  Screen shape:   {snapshot.ScreenShape} (0=4:3, 1=16:9, 2=1:1)");
                ctx.Line($"  Options entries:{snapshot.OptionsEntryCount}");
                ctx.Line();
                ctx.Line($"{"Group",-10} {"Action",-18} {"P1",-14} {"P2",-14}");
                ctx.Line(new string('-', 60));
                foreach (ConfigurationKeybindRow row in snapshot.KeybindRows)
                    ctx.Line($"{row.GroupLabel,-10} {row.ActionLabel,-18} {row.CurrentPlayer1Token,-14} {row.CurrentPlayer2Token,-14}");
            }

            return ctx.Ok(command, payload);
        }

        // ---------------------------------------------------------------- shared helpers

        /// <summary>
        /// The in-place write block. Preserved verbatim from the original CLI: patching a save onto
        /// itself is refused outright rather than being allowed to half-succeed and destroy the only
        /// copy of the input.
        /// </summary>
        public static bool TryRejectInPlaceWrite(
            CliContext ctx,
            string command,
            string inputPath,
            string outputPath,
            out int exitCode)
        {
            exitCode = CliExit.Success;
            try
            {
                if (string.Equals(
                        Path.GetFullPath(inputPath),
                        Path.GetFullPath(outputPath),
                        StringComparison.OrdinalIgnoreCase))
                {
                    exitCode = ctx.Usage(
                        command,
                        "Output file must be different from input file. In-place patching is blocked.");
                    return false;
                }
            }
            catch (Exception ex) when (ex is ArgumentException or IOException or NotSupportedException or System.Security.SecurityException)
            {
                exitCode = ctx.Usage(command, $"Unable to canonicalize input/output paths: {ex.Message}");
                return false;
            }

            return true;
        }

        public static bool TryParseGoodieStateOverrides(
            IReadOnlyList<string>? entries,
            out Dictionary<int, uint> overrides,
            out string error)
        {
            overrides = new Dictionary<int, uint>();
            error = string.Empty;

            if (entries is null || entries.Count == 0)
            {
                error = "Choose at least one Goodie INDEX:STATE override.";
                return false;
            }

            foreach (string rawEntry in entries)
            {
                string entry = rawEntry.Trim();
                string[] parts = entry.Split(':', 2, StringSplitOptions.TrimEntries);
                if (parts.Length != 2 ||
                    !int.TryParse(parts[0], System.Globalization.NumberStyles.Integer, System.Globalization.CultureInfo.InvariantCulture, out int index))
                {
                    error = $"Invalid Goodie entry '{entry}'. Expected INDEX:STATE, for example 71:new.";
                    return false;
                }

                if (!TryParseGoodieState(parts[1], out uint state))
                {
                    error = $"Invalid Goodie state '{parts[1]}' for index {index}. Use 0, 1, 2, 3, locked, instructions, new, or old.";
                    return false;
                }

                overrides[index] = state;
            }

            return true;
        }

        public static bool TryParseGoodieState(string rawState, out uint state)
        {
            switch (rawState.Trim().ToLowerInvariant())
            {
                case "0":
                case "locked":
                case "none":
                    state = 0;
                    return true;
                case "1":
                case "instructions":
                case "instruction":
                    state = 1;
                    return true;
                case "2":
                case "new":
                    state = 2;
                    return true;
                case "3":
                case "old":
                case "viewed":
                    state = 3;
                    return true;
                default:
                    state = 0;
                    return false;
            }
        }

        public static string GoodieStateName(uint state) => state switch
        {
            0 => "LOCKED",
            1 => "INSTRUCTIONS",
            2 => "NEW",
            3 => "OLD",
            _ => "OTHER",
        };

        private static string ClassifyGoodie(int index, uint raw, int displayableCount)
        {
            if (index >= displayableCount) return "RESERVED";
            return raw switch
            {
                2 => "NEW",
                3 => "OLD",
                0 => "LOCKED",
                1 => "INSTRUCTIONS",
                _ => "OTHER",
            };
        }

        public static bool IsFileAccessFailure(Exception ex) =>
            ex is IOException or UnauthorizedAccessException or NotSupportedException
                or ArgumentException or System.Security.SecurityException;

        public static string DescribeFileFailure(Exception ex) => ex switch
        {
            UnauthorizedAccessException => $"Access denied: {ex.Message}",
            IOException => $"Failed to access file: {ex.Message}",
            _ => ex.Message,
        };

        private static object ProjectDocument(SaveAnalyzerDocument document) => new
        {
            isComparisonMode = document.IsComparisonMode,
            title = document.Title,
            modeText = document.ModeText,
            statusText = document.StatusText,
            summaryTitle = document.SummaryTitle,
            reportText = document.ReportText,
            metrics = document.Metrics
                .Select(metric => new { label = metric.Label, value = metric.Value, detail = metric.Detail })
                .ToArray(),
            summaryNodes = document.SummaryNodes.Select(ProjectNode).ToArray(),
            goodieStates = document.GoodieStates.Select(state => new
            {
                index = state.Index,
                fileOffset = state.FileOffset,
                rawState = state.RawState,
                stateLabel = state.StateLabel,
                isDisplayable = state.IsDisplayable,
                isUnlocked = state.IsUnlocked,
            }).ToArray(),
        };

        private static object ProjectNode(SaveAnalyzerTreeNode node) => new
        {
            label = node.Label,
            children = node.Children.Select(ProjectNode).ToArray(),
        };

        private static object ProjectAnalysis(SaveAnalysis analysis) => new
        {
            filePath = analysis.FilePath,
            isOptionsFile = analysis.IsOptionsFile,
            fileSize = analysis.FileSize,
            versionWord = analysis.VersionWord,
            versionValid = analysis.VersionValid,
            versionStamp = analysis.VersionStamp,
            newGoodieCountRaw = analysis.NewGoodieCountRaw,
            godModeEnabled = analysis.GodModeEnabledOn,
            careerInProgress = analysis.CareerInProgressOn,
            soundVolume = analysis.SoundVolume,
            musicVolume = analysis.MusicVolume,
            invertWalker = analysis.InvertYAxisRaw.Select(value => value != 0).ToArray(),
            invertFlight = analysis.InvertFlightRaw.Select(value => value != 0).ToArray(),
            vibration = analysis.VibrationRaw.Select(value => value != 0).ToArray(),
            controllerConfig = analysis.ControllerConfigNum,
            optionsEntryCount = analysis.OptionsEntryCount,
            optionsTailStart = analysis.OptionsTailStart,
            optionsMouseSensitivity = analysis.OptionsMouseSensitivity,
            optionsControlSchemeIndex = analysis.OptionsControlSchemeIndex,
            optionsLanguageIndex = analysis.OptionsLanguageIndex,
            optionsScreenShape = analysis.OptionsScreenShape,
            optionsD3DDeviceIndex = analysis.OptionsD3DDeviceIndex,
            completedNodes = analysis.CompletedNodes,
            partialNodes = analysis.PartialNodes,
            emptyNodes = analysis.EmptyNodes,
            rankDistribution = analysis.RankDistribution,
            completedNodeDetails = analysis.CompletedNodeDetails
                .Select(detail => new
                {
                    index = detail.Index,
                    world = detail.World,
                    rank = detail.Rank,
                    rankBits = detail.RankBits,
                })
                .ToArray(),
            completedLinks = analysis.CompletedLinks,
            totalLinks = analysis.TotalLinks,
            goodies = new
            {
                @new = analysis.GoodiesNew,
                old = analysis.GoodiesOld,
                locked = analysis.GoodiesLocked,
                lockedWithHint = analysis.GoodiesInstructions,
                other = analysis.GoodiesOther,
                reserved = analysis.GoodiesReserved,
            },
            killCounts = analysis.KillCounts,
            nextUnlockThresholds = analysis.NextUnlockThresholds,
            activeTechSlots = analysis.ActiveTechSlots,
            totalTechSlots = analysis.TotalTechSlots,
            mysteryRegions = analysis.MysteryRegions.Select(region => new
            {
                name = region.Name,
                description = region.Description,
                startOffset = region.StartOffset,
                endOffset = region.EndOffset,
                size = region.Size,
                nonZeroCount = region.NonZeroCount,
                allZeros = region.AllZeros,
                allFF = region.AllFF,
            }).ToArray(),
        };
    }
}
