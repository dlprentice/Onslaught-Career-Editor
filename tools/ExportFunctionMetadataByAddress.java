//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;

public class ExportFunctionMetadataByAddress extends GhidraScript {

    private static class Target {
        final String raw;
        final Address addr;

        Target(String raw, Address addr) {
            this.raw = raw;
            this.addr = addr;
        }
    }

    private static String escape(String value) {
        if (value == null) {
            return "";
        }
        return value
            .replace("\\", "\\\\")
            .replace("\r", "\\r")
            .replace("\n", "\\n")
            .replace("\t", "\\t");
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 2) {
            popup("Usage: ExportFunctionMetadataByAddress.java <addresses_file> <out_tsv>");
            return;
        }

        File inFile = new File(args[0]);
        File outFile = new File(args[1]);
        if (!inFile.exists()) {
            println("Input file not found: " + inFile.getAbsolutePath());
            return;
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
                Address addr = toAddr(tok);
                if (addr == null) {
                    println("BADADDR: " + line);
                    continue;
                }
                targets.add(new Target(tok, addr));
            }
        }

        int found = 0;
        int missing = 0;
        try (PrintWriter pw = new PrintWriter(outFile, "UTF-8")) {
            pw.println("address\tname\tsignature\tcomment\tstatus");
            for (Target target : targets) {
                Function fn = getFunctionAt(target.addr);
                if (fn == null) {
                    Function containing = getFunctionContaining(target.addr);
                    if (containing != null && containing.getEntryPoint().equals(target.addr)) {
                        fn = containing;
                    }
                }
                if (fn == null) {
                    pw.println("0x" + target.addr.toString() + "\t<none>\t<none>\t\tMISSING");
                    missing++;
                    continue;
                }

                String address = "0x" + fn.getEntryPoint().toString();
                String name = escape(fn.getName());
                String signature = escape(fn.getSignature().toString());
                String comment = escape(fn.getComment());
                pw.println(address + "\t" + name + "\t" + signature + "\t" + comment + "\tOK");
                found++;
            }
        }

        println("Export metadata complete: " + outFile.getAbsolutePath());
        println("targets=" + targets.size() + " found=" + found + " missing=" + missing);
    }
}
