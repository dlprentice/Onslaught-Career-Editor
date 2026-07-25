//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.FunctionTagManager;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;

/**
 * Apply tag add/remove ops from a TSV.
 * Columns: address, expected_name, remove_tags, add_tags
 * remove_tags/add_tags are comma-separated (may be empty).
 * Mode: dry|apply (default dry). Fail-closed on name mismatch.
 */
public class GhidraApplyTagOpsFromTsv extends GhidraScript {

    private static class Target {
        final String address;
        final String expectedName;
        final List<String> removeTags;
        final List<String> addTags;

        Target(String address, String expectedName, List<String> removeTags, List<String> addTags) {
            this.address = address;
            this.expectedName = expectedName;
            this.removeTags = removeTags;
            this.addTags = addTags;
        }
    }

    private static boolean isDryRun(String mode) {
        if (mode == null || mode.trim().isEmpty()) {
            return true;
        }
        String normalized = mode.trim().toLowerCase(Locale.ROOT);
        if (normalized.equals("dry") || normalized.equals("dry-run")) {
            return true;
        }
        if (normalized.equals("apply")) {
            return false;
        }
        throw new IllegalArgumentException("Unrecognized mode: " + mode + " (use dry/apply)");
    }

    private static List<String> splitTags(String value) {
        List<String> out = new ArrayList<>();
        if (value == null || value.trim().isEmpty()) {
            return out;
        }
        for (String part : value.split(",")) {
            String t = part.trim();
            if (!t.isEmpty()) {
                out.add(t);
            }
        }
        return out;
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
                String[] parts = line.split("\t", -1);
                if (parts.length < 4) {
                    println("BADROW: line " + lineNumber);
                    continue;
                }
                String address = parts[0].trim().toLowerCase(Locale.ROOT);
                if (!address.startsWith("0x")) {
                    address = "0x" + address;
                }
                targets.add(new Target(
                    address,
                    parts[1].trim(),
                    splitTags(parts[2]),
                    splitTags(parts[3])
                ));
            }
        }
        return targets;
    }

    private Function getFunctionOrThrow(String addrText) throws Exception {
        Address addr = toAddr(addrText);
        Function fn = getFunctionAt(addr);
        if (fn == null) {
            throw new IllegalStateException("Function not found at " + addrText);
        }
        return fn;
    }

    private static Set<String> currentTagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 1) {
            popup("Usage: GhidraApplyTagOpsFromTsv.java <tags_tsv> [dry|apply]");
            return;
        }
        File inFile = new File(args[0]);
        if (!inFile.exists()) {
            throw new IllegalArgumentException("Input TSV not found: " + inFile.getAbsolutePath());
        }
        boolean dryRun = isDryRun(args.length > 1 ? args[1] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        FunctionTagManager tagManager = currentProgram.getFunctionManager().getFunctionTagManager();
        int applied = 0;
        int skipped = 0;
        int bad = 0;
        int missing = 0;

        for (Target target : readTargets(inFile)) {
            Function fn;
            try {
                fn = getFunctionOrThrow(target.address);
            } catch (Exception ex) {
                println("MISSING: " + target.address + " " + ex.getMessage());
                missing++;
                continue;
            }
            if (!target.expectedName.equals(fn.getName())) {
                println("BADNAME: " + target.address + " expected " + target.expectedName +
                    " actual " + fn.getName());
                bad++;
                continue;
            }

            Set<String> have = currentTagNames(fn);
            if (dryRun) {
                println("DRY: " + target.address + " remove=" + target.removeTags +
                    " add=" + target.addTags + " have=" + have);
                skipped++;
                continue;
            }

            int tx = currentProgram.startTransaction("tag-ops " + target.address);
            boolean ok = false;
            try {
                for (String name : target.removeTags) {
                    FunctionTag tag = tagManager.getFunctionTag(name);
                    if (tag != null && have.contains(name)) {
                        fn.removeTag(name);
                    }
                }
                for (String name : target.addTags) {
                    FunctionTag tag = tagManager.getFunctionTag(name);
                    if (tag == null) {
                        tag = tagManager.createFunctionTag(name, "");
                    }
                    fn.addTag(name);
                }
                ok = true;
                println("OK: " + target.address + " " + fn.getName());
                applied++;
            } finally {
                currentProgram.endTransaction(tx, ok);
            }
        }

        println("--- SUMMARY ---");
        println("applied=" + applied + " skipped=" + skipped + " missing=" + missing + " bad=" + bad);
    }
}
