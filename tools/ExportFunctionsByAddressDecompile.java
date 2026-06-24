//@category Analysis

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.util.ArrayList;
import java.util.List;

public class ExportFunctionsByAddressDecompile extends GhidraScript {

    private static class Target {
        final String raw;
        final Address addr;

        Target(String raw, Address addr) {
            this.raw = raw;
            this.addr = addr;
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 2) {
            popup("Usage: ExportFunctionsByAddressDecompile.java <addresses_file> <out_dir> [timeout_sec]");
            return;
        }

        File inFile = new File(args[0]);
        File outDir = new File(args[1]);
        int timeoutSec = 60;
        if (args.length > 2 && args[2] != null && !args[2].trim().isEmpty()) {
            timeoutSec = Integer.parseInt(args[2].trim());
        }

        if (!inFile.exists()) {
            println("Input file not found: " + inFile.getAbsolutePath());
            return;
        }
        if (!outDir.exists() && !outDir.mkdirs()) {
            throw new RuntimeException("Failed to create output dir: " + outDir.getAbsolutePath());
        }

        List<Target> targets = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(inFile))) {
            String line;
            while ((line = br.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty() || line.startsWith("#")) {
                    continue;
                }
                String tok = line.split("\\s+")[0];
                if (!tok.startsWith("0x") && !tok.startsWith("0X")) {
                    tok = "0x" + tok;
                }
                Address a = toAddr(tok);
                if (a == null) {
                    println("BADADDR: " + line);
                    continue;
                }
                targets.add(new Target(tok, a));
            }
        }

        DecompInterface ifc = new DecompInterface();
        ifc.toggleCCode(true);
        ifc.toggleSyntaxTree(false);
        ifc.setSimplificationStyle("decompile");
        if (!ifc.openProgram(currentProgram)) {
            throw new RuntimeException("Failed to open program in decompiler interface");
        }

        int dumped = 0;
        int missing = 0;
        int failed = 0;

        File indexFile = new File(outDir, "index.tsv");
        try (BufferedWriter idx = new BufferedWriter(new FileWriter(indexFile))) {
            idx.write("address\tname\tsignature\tstatus\n");

            for (Target t : targets) {
                if (monitor.isCancelled()) {
                    break;
                }

                Function fn = getFunctionAt(t.addr);
                if (fn == null) {
                    Function cf = getFunctionContaining(t.addr);
                    if (cf != null && cf.getEntryPoint().equals(t.addr)) {
                        fn = cf;
                    }
                }

                if (fn == null) {
                    idx.write("0x" + t.addr.toString() + "\t<none>\t<none>\tMISSING\n");
                    missing++;
                    continue;
                }

                String name = fn.getName();
                String sig = fn.getSignature().toString().replace('\t', ' ').replace('\n', ' ');
                String base = fn.getEntryPoint().toString() + "_" + name.replaceAll("[^A-Za-z0-9_]+", "_");
                File outFile = new File(outDir, base + ".c");

                try (BufferedWriter bw = new BufferedWriter(new FileWriter(outFile))) {
                    DecompileResults dr = ifc.decompileFunction(fn, timeoutSec, monitor);
                    if (!dr.decompileCompleted() || dr.getDecompiledFunction() == null) {
                        bw.write("/* DECOMPILE_FAILED */\n");
                        bw.write("/* message: " + dr.getErrorMessage() + " */\n");
                        bw.write("/* signature: " + sig + " */\n");
                        idx.write("0x" + fn.getEntryPoint().toString() + "\t" + name + "\t" + sig + "\tFAILED\n");
                        failed++;
                    } else {
                        bw.write("/* address: 0x" + fn.getEntryPoint().toString() + " */\n");
                        bw.write("/* name: " + name + " */\n");
                        bw.write("/* signature: " + sig + " */\n\n");
                        bw.write(dr.getDecompiledFunction().getC());
                        idx.write("0x" + fn.getEntryPoint().toString() + "\t" + name + "\t" + sig + "\tOK\n");
                        dumped++;
                    }
                }
            }
        } finally {
            ifc.dispose();
        }

        println("Export complete: dir=" + outDir.getAbsolutePath());
        println("targets=" + targets.size() + " dumped=" + dumped + " missing=" + missing + " failed=" + failed);
    }
}
