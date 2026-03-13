//@category Analysis

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;

public class ExportFunctionsByPrefixDecompile extends GhidraScript {

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        String outDirPath;
        String prefix;
        int timeoutSec = 45;

        if (args == null || args.length < 2) {
            popup("Usage: ExportFunctionsByPrefixDecompile.java <out_dir> <name_prefix> [timeout_sec]");
            return;
        }

        outDirPath = args[0].trim();
        prefix = args[1].trim();
        if (args.length > 2 && args[2] != null && !args[2].trim().isEmpty()) {
            timeoutSec = Integer.parseInt(args[2].trim());
        }

        File outDir = new File(outDirPath);
        if (!outDir.exists() && !outDir.mkdirs()) {
            throw new RuntimeException("Failed to create output dir: " + outDir.getAbsolutePath());
        }

        DecompInterface ifc = new DecompInterface();
        ifc.toggleCCode(true);
        ifc.toggleSyntaxTree(false);
        ifc.setSimplificationStyle("decompile");

        if (!ifc.openProgram(currentProgram)) {
            throw new RuntimeException("Failed to open program in decompiler interface");
        }

        int matched = 0;
        int dumped = 0;
        int failed = 0;

        File indexFile = new File(outDir, "index.tsv");
        try (BufferedWriter idx = new BufferedWriter(new FileWriter(indexFile))) {
            idx.write("address\tname\tsignature\tstatus\n");

            FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
            while (it.hasNext() && !monitor.isCancelled()) {
                Function fn = it.next();
                String name = fn.getName();
                if (!name.startsWith(prefix)) {
                    continue;
                }
                matched++;

                String addr = fn.getEntryPoint().toString();
                String sig = fn.getSignature().toString().replace('\t', ' ').replace('\n', ' ');
                String base = addr + "_" + name.replaceAll("[^A-Za-z0-9_]+", "_");
                File outFile = new File(outDir, base + ".c");

                try (BufferedWriter bw = new BufferedWriter(new FileWriter(outFile))) {
                    DecompileResults dr = ifc.decompileFunction(fn, timeoutSec, monitor);
                    if (!dr.decompileCompleted() || dr.getDecompiledFunction() == null) {
                        bw.write("/* DECOMPILE_FAILED */\n");
                        bw.write("/* message: " + dr.getErrorMessage() + " */\n");
                        bw.write("/* signature: " + sig + " */\n");
                        idx.write("0x" + addr + "\t" + name + "\t" + sig + "\tFAILED\n");
                        failed++;
                    } else {
                        bw.write("/* address: 0x" + addr + " */\n");
                        bw.write("/* name: " + name + " */\n");
                        bw.write("/* signature: " + sig + " */\n\n");
                        bw.write(dr.getDecompiledFunction().getC());
                        idx.write("0x" + addr + "\t" + name + "\t" + sig + "\tOK\n");
                        dumped++;
                    }
                }
            }
        } finally {
            ifc.dispose();
        }

        println("Export complete: dir=" + outDir.getAbsolutePath());
        println("prefix=" + prefix + " matched=" + matched + " dumped=" + dumped + " failed=" + failed);
    }
}
