//@category Analysis
//
// Read-only dump of every analysis option and its CURRENT value for this
// program.  Run with -readOnly -noanalysis.  This is the evidence for what
// "standard analysis was run conservatively" actually means on this database:
// the saved per-program option state, not a guess about Ghidra defaults.
//
// Usage: -postScript ListAnalysisOptions.java <out_tsv>

import ghidra.app.script.GhidraScript;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.util.Map;
import java.util.TreeMap;

public class ListAnalysisOptions extends GhidraScript {

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        Map<String, String> options = new TreeMap<>(getCurrentAnalysisOptionsAndValues(currentProgram));
        if (args != null && args.length >= 1) {
            try (BufferedWriter bw = new BufferedWriter(new FileWriter(new File(args[0])))) {
                bw.write("option\tvalue\n");
                for (Map.Entry<String, String> entry : options.entrySet()) {
                    bw.write(entry.getKey() + "\t" + entry.getValue() + "\n");
                }
            }
        }
        for (Map.Entry<String, String> entry : options.entrySet()) {
            println("ANALYSIS_OPTION\t" + entry.getKey() + "\t" + entry.getValue());
        }
        println("ANALYSIS_OPTION_COUNT " + options.size());
    }
}
