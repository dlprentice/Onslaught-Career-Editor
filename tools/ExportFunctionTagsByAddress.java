//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class ExportFunctionTagsByAddress extends GhidraScript {
    private Address parseTargetAddress(String raw) {
        String value = raw.trim();
        if (!value.startsWith("0x") && !value.startsWith("0X")) {
            value = "0x" + value;
        }
        return toAddr(value);
    }

    private Function functionAtOrContaining(Address addr) {
        Function fn = getFunctionAt(addr);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(addr);
        if (containing != null && containing.getEntryPoint().equals(addr)) {
            return containing;
        }
        return null;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 2) {
            popup("Usage: ExportFunctionTagsByAddress.java <addresses_file> <out_tsv>");
            return;
        }

        File inFile = new File(args[0]);
        File outFile = new File(args[1]);
        if (!inFile.exists()) {
            throw new IllegalArgumentException("Input file not found: " + inFile.getAbsolutePath());
        }

        int rows = 0;
        int missing = 0;
        try (BufferedReader br = new BufferedReader(new FileReader(inFile));
             PrintWriter pw = new PrintWriter(outFile)) {
            pw.println("address\tname\ttags\tstatus");
            String line;
            while ((line = br.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty() || line.startsWith("#")) {
                    continue;
                }
                String token = line.split("\\s+")[0];
                Address addr = parseTargetAddress(token);
                if (addr == null) {
                    pw.println(token + "\t\t\tBADADDR");
                    missing++;
                    continue;
                }
                Function fn = functionAtOrContaining(addr);
                if (fn == null) {
                    pw.println(addr.toString() + "\t\t\tMISSING");
                    missing++;
                    continue;
                }
                List<String> names = new ArrayList<>();
                for (FunctionTag tag : fn.getTags()) {
                    names.add(tag.getName());
                }
                Collections.sort(names);
                pw.println(addr.toString() + "\t" + fn.getName() + "\t" + String.join(";", names) + "\tOK");
                rows++;
            }
        }

        println("ExportFunctionTagsByAddress complete: rows=" + rows + " missing=" + missing + " out=" + outFile.getAbsolutePath());
    }
}
