//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;

public class GhidraBatchRename extends GhidraScript {

    private static class RenameSpec {
        String addrText;
        String newName;

        RenameSpec(String addrText, String newName) {
            this.addrText = addrText;
            this.newName = newName;
        }
    }

    private RenameSpec parseLine(String raw) {
        if (raw == null) {
            return null;
        }

        String line = raw.trim();
        if (line.isEmpty() || line.startsWith("#")) {
            return null;
        }

        int ws = line.indexOf(' ');
        if (ws < 0) {
            ws = line.indexOf('\t');
        }
        if (ws < 0) {
            return null;
        }

        String addr = line.substring(0, ws).trim();
        String name = line.substring(ws).trim();
        if (addr.isEmpty() || name.isEmpty()) {
            return null;
        }

        if (!addr.startsWith("0x") && !addr.startsWith("0X")) {
            addr = "0x" + addr;
        }

        return new RenameSpec(addr, name);
    }

    private boolean parseDryMode(String mode) {
        if (mode == null) {
            return true;
        }
        String m = mode.trim().toLowerCase();
        if (m.isEmpty()) {
            return true;
        }
        if (m.equals("apply") || m.equals("no-dry") || m.equals("false") || m.equals("0")) {
            return false;
        }
        if (m.equals("dry") || m.equals("dry-run") || m.equals("true") || m.equals("1")) {
            return true;
        }
        throw new IllegalArgumentException("Unrecognized mode: " + mode + " (use dry/apply)");
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        File renameFile;
        boolean dryRun;

        if (args != null && args.length > 0 && args[0] != null && !args[0].trim().isEmpty()) {
            renameFile = new File(args[0].trim());
            if (!renameFile.exists()) {
                throw new IllegalArgumentException("Rename map not found: " + renameFile.getAbsolutePath());
            }
            dryRun = parseDryMode(args.length > 1 ? args[1] : "dry");
            println("Mode: args (" + (dryRun ? "dry" : "apply") + ")");
            println("Map: " + renameFile.getAbsolutePath());
        } else {
            renameFile = askFile("Select rename map", "Apply");
            dryRun = askYesNo("Batch Rename", "Dry run only?");
            println("Mode: interactive (" + (dryRun ? "dry" : "apply") + ")");
            println("Map: " + renameFile.getAbsolutePath());
        }

        int applied = 0;
        int skipped = 0;
        int missing = 0;
        int bad = 0;

        try (BufferedReader br = new BufferedReader(new FileReader(renameFile))) {
            String raw;
            while ((raw = br.readLine()) != null) {
                RenameSpec spec = parseLine(raw);
                if (spec == null) {
                    continue;
                }

                Address addr = toAddr(spec.addrText);
                if (addr == null) {
                    println("BADADDR: " + spec.addrText);
                    bad++;
                    continue;
                }

                Function fn = getFunctionAt(addr);
                if (fn == null) {
                    Function containing = getFunctionContaining(addr);
                    if (containing == null || !containing.getEntryPoint().equals(addr)) {
                        println("MISSING: " + spec.addrText + " -> " + spec.newName);
                        missing++;
                        continue;
                    }
                    fn = containing;
                }

                String oldName = fn.getName();
                if (oldName.equals(spec.newName)) {
                    println("SKIP: " + spec.addrText + " already " + spec.newName);
                    skipped++;
                    continue;
                }

                if (dryRun) {
                    println("DRY: " + spec.addrText + " " + oldName + " -> " + spec.newName);
                    skipped++;
                    continue;
                }

                try {
                    fn.setName(spec.newName, SourceType.USER_DEFINED);
                    println("OK: " + spec.addrText + " " + oldName + " -> " + spec.newName);
                    applied++;
                } catch (Exception ex) {
                    println("FAIL: " + spec.addrText + " " + oldName + " -> " + spec.newName + " (" + ex.getMessage() + ")");
                    bad++;
                }
            }
        }

        println("--- SUMMARY ---");
        println("applied=" + applied + " skipped=" + skipped + " missing=" + missing + " bad=" + bad);
    }
}
