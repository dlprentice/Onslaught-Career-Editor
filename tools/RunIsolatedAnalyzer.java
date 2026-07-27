//@category Analysis
//
// Run ONE analyser (or one tight group) over the whole program, with every
// other analyser switched off, so the resulting database delta is attributable.
//
// Running `analyzeAll` with the program's saved options would re-run ~30
// analysers at once and the diff would be uninterpretable.  This turns every
// boolean analysis option OFF, turns the named ones ON, applies any explicit
// sub-option overrides, and then re-analyses the whole address space.  The
// delta is therefore the marginal effect of the named analyser on THIS
// database in its current state.
//
// MUTATES the program.  Only ever point it at a disposable canary copy.
//
// Usage: -postScript RunIsolatedAnalyzer.java "<AnalyzerName>[;<AnalyzerName>...]" \
//                    "<Opt=Value>[;<Opt=Value>...]"   (second arg may be "-")

import ghidra.app.script.GhidraScript;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class RunIsolatedAnalyzer extends GhidraScript {

    private static boolean isBooleanValue(String value) {
        return "true".equals(value) || "false".equals(value);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 1 || args[0].trim().isEmpty()) {
            println("ISOLATED_ANALYZER_FAIL reason=usage");
            return;
        }

        List<String> enable = new ArrayList<>();
        for (String token : args[0].split(";")) {
            if (!token.trim().isEmpty()) {
                enable.add(token.trim());
            }
        }

        Map<String, String> before = new TreeMap<>(getCurrentAnalysisOptionsAndValues(currentProgram));

        // Every analyser off.  Only top-level analyser toggles are boolean-valued
        // options with no '.' in the name; sub-options are left alone unless the
        // caller overrides them explicitly.
        // "KEEP" leaves the program's saved analyser set intact and merely adds
        // the named analysers.  This is what makes a CONTROL run possible: re-
        // running the existing set with nothing added measures how much of any
        // subsequent diff is caused by re-analysis itself rather than by the
        // analyser under test.  Without that control, ordinary churn gets
        // attributed to the new analyser.
        boolean keepExisting = enable.remove("KEEP");

        int disabled = 0;
        for (Map.Entry<String, String> entry : keepExisting
                ? new TreeMap<String, String>().entrySet()
                : before.entrySet()) {
            String key = entry.getKey();
            if (key.indexOf('.') >= 0) {
                continue;
            }
            if (!isBooleanValue(entry.getValue())) {
                continue;
            }
            if ("false".equals(entry.getValue())) {
                continue;
            }
            setAnalysisOption(currentProgram, key, "false");
            disabled++;
        }

        for (String name : enable) {
            if (!before.containsKey(name)) {
                println("ISOLATED_ANALYZER_FAIL reason=unknown_analyzer name=" + name);
                return;
            }
            setAnalysisOption(currentProgram, name, "true");
            println("ISOLATED_ANALYZER_ENABLE " + name);
        }

        if (args.length >= 2 && !"-".equals(args[1].trim()) && !args[1].trim().isEmpty()) {
            for (String pair : args[1].split(";")) {
                if (pair.trim().isEmpty()) {
                    continue;
                }
                int eq = pair.indexOf('=');
                if (eq < 0) {
                    println("ISOLATED_ANALYZER_FAIL reason=bad_option_override value=" + pair);
                    return;
                }
                String key = pair.substring(0, eq).trim();
                String value = pair.substring(eq + 1).trim();
                if (!before.containsKey(key)) {
                    println("ISOLATED_ANALYZER_FAIL reason=unknown_option name=" + key);
                    return;
                }
                setAnalysisOption(currentProgram, key, value);
                println("ISOLATED_ANALYZER_OVERRIDE " + key + "=" + value);
            }
        }

        // Prove the option state that will actually run, rather than the state
        // that was requested.
        Map<String, String> effective = new TreeMap<>(getCurrentAnalysisOptionsAndValues(currentProgram));
        for (Map.Entry<String, String> entry : effective.entrySet()) {
            if (entry.getKey().indexOf('.') < 0 && "true".equals(entry.getValue())) {
                println("ISOLATED_ANALYZER_ACTIVE " + entry.getKey());
            }
        }
        println("ISOLATED_ANALYZER_DISABLED_COUNT " + disabled);

        long start = System.currentTimeMillis();
        analyzeAll(currentProgram);
        long elapsed = System.currentTimeMillis() - start;

        println("ISOLATED_ANALYZER_OK enabled=" + String.join(",", enable)
            + " elapsedMs=" + elapsed
            + " functions=" + currentProgram.getFunctionManager().getFunctionCount());
    }
}
