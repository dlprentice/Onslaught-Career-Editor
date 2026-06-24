//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.List;

public class GhidraApplyFunctionCommentsFromTsv extends GhidraScript {

    private static class Target {
        final String address;
        final String expectedName;
        final String comment;

        Target(String address, String expectedName, String comment) {
            this.address = address;
            this.expectedName = expectedName;
            this.comment = comment;
        }
    }

    private static boolean isDryRun(String mode) {
        if (mode == null || mode.trim().isEmpty()) {
            return true;
        }
        String normalized = mode.trim().toLowerCase();
        if (normalized.equals("dry") || normalized.equals("dry-run") || normalized.equals("true") || normalized.equals("1")) {
            return true;
        }
        if (normalized.equals("apply") || normalized.equals("no-dry") || normalized.equals("false") || normalized.equals("0")) {
            return false;
        }
        throw new IllegalArgumentException("Unrecognized mode: " + mode + " (use dry/apply)");
    }

    private static String unescape(String value) {
        if (value == null) {
            return "";
        }
        return value
            .replace("\\t", "\t")
            .replace("\\n", "\n")
            .replace("\\r", "\r")
            .replace("\\\\", "\\");
    }

    private List<Target> readTargets(File inFile) throws Exception {
        List<Target> targets = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(inFile))) {
            String line;
            int lineNumber = 0;
            while ((line = br.readLine()) != null) {
                lineNumber++;
                if (line.trim().isEmpty() || line.startsWith("#")) {
                    continue;
                }
                if (lineNumber == 1 && line.startsWith("address\t")) {
                    continue;
                }
                String[] parts = line.split("\t", 3);
                if (parts.length != 3) {
                    println("BADROW: line " + lineNumber + " expected 3 tab-separated columns");
                    targets.add(new Target("BADROW:" + lineNumber, "", ""));
                    continue;
                }
                String address = parts[0].trim();
                if (!address.startsWith("0x") && !address.startsWith("0X")) {
                    address = "0x" + address;
                }
                targets.add(new Target(address, parts[1].trim(), unescape(parts[2])));
            }
        }
        return targets;
    }

    private Function getFunctionOrThrow(String addrText) throws Exception {
        Address addr = toAddr(addrText);
        if (addr == null) {
            throw new IllegalArgumentException("Bad address: " + addrText);
        }
        Function fn = getFunctionAt(addr);
        if (fn == null) {
            Function containing = getFunctionContaining(addr);
            if (containing != null && containing.getEntryPoint().equals(addr)) {
                fn = containing;
            }
        }
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + addrText);
        }
        return fn;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 1) {
            popup("Usage: GhidraApplyFunctionCommentsFromTsv.java <comments_tsv> [dry|apply]");
            return;
        }

        File inFile = new File(args[0]);
        if (!inFile.exists()) {
            throw new IllegalArgumentException("Input TSV not found: " + inFile.getAbsolutePath());
        }
        boolean dryRun = isDryRun(args.length > 1 ? args[1] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        int applied = 0;
        int skipped = 0;
        int missing = 0;
        int bad = 0;

        for (Target target : readTargets(inFile)) {
            if (target.address.startsWith("BADROW:")) {
                bad++;
                continue;
            }

            Function fn;
            try {
                fn = getFunctionOrThrow(target.address);
            } catch (Exception ex) {
                println("MISSING: " + target.address + " " + ex.getMessage());
                missing++;
                continue;
            }

            String actualName = fn.getName();
            if (!target.expectedName.equals(actualName)) {
                println("BADNAME: " + target.address + " expected " + target.expectedName + " actual " + actualName);
                bad++;
                continue;
            }

            if (dryRun) {
                println("DRY: " + target.address + " " + actualName);
                skipped++;
                continue;
            }

            fn.setComment(target.comment);
            println("OK: " + target.address + " " + actualName);
            applied++;
        }

        println("--- SUMMARY ---");
        println("applied=" + applied + " skipped=" + skipped + " missing=" + missing + " bad=" + bad);
    }
}
