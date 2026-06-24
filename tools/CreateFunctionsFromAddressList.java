//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.SourceType;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;

public class CreateFunctionsFromAddressList extends GhidraScript {

    private static class Target {
        final String raw;
        final Address addr;
        final String desiredName;

        Target(String raw, Address addr, String desiredName) {
            this.raw = raw;
            this.addr = addr;
            this.desiredName = desiredName;
        }
    }

    private static boolean isDryRun(String mode) {
        if (mode == null || mode.trim().isEmpty()) {
            return false;
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

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 2) {
            popup("Usage: CreateFunctionsFromAddressList.java <addresses_file> <out_tsv> [mode=dry|apply]");
            return;
        }

        File inFile = new File(args[0]);
        File outFile = new File(args[1]);
        boolean dryRun = isDryRun(args.length >= 3 ? args[2] : "apply");
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

                String[] parts = line.split("\\s+");
                String tok = parts[0];
                String desiredName = parts.length >= 2 ? parts[1].trim() : "";
                if (!tok.startsWith("0x") && !tok.startsWith("0X")) {
                    tok = "0x" + tok;
                }

                Address a = toAddr(tok);
                if (a == null) {
                    println("BADADDR: " + line);
                    continue;
                }
                targets.add(new Target(tok, a, desiredName));
            }
        }

        int created = 0;
        int already = 0;
        int failed = 0;
        int wouldCreate = 0;
        int renamed = 0;
        int wouldRename = 0;

        try (PrintWriter pw = new PrintWriter(outFile)) {
            pw.println("address\tstatus\tname\tsignature\tnote");

            for (Target t : targets) {
                if (monitor.isCancelled()) {
                    break;
                }

                String status = "failed";
                String name = "";
                String sig = "";
                String note = "";

                try {
                    Function fn = getFunctionAt(t.addr);
                    if (fn == null) {
                        Function cf = getFunctionContaining(t.addr);
                        if (cf != null && cf.getEntryPoint().equals(t.addr)) {
                            fn = cf;
                        }
                    }

                    if (fn != null) {
                        status = "already_exists";
                        already++;
                        name = fn.getName();
                        sig = fn.getSignature().toString().replace('\t', ' ').replace('\n', ' ');
                        if (!t.desiredName.isEmpty() && !name.equals(t.desiredName)) {
                            if (dryRun) {
                                status = "would_rename";
                                wouldRename++;
                                note = "function present; dry-run would rename to " + t.desiredName;
                            } else {
                                fn.setName(t.desiredName, SourceType.USER_DEFINED);
                                renamed++;
                                name = fn.getName();
                                sig = fn.getSignature().toString().replace('\t', ' ').replace('\n', ' ');
                                status = "renamed_existing";
                                note = "function present before create attempt; renamed";
                            }
                        } else {
                            note = "function present before create attempt";
                        }
                    } else {
                        if (dryRun) {
                            status = "would_create";
                            wouldCreate++;
                            note = t.desiredName.isEmpty()
                                ? "dry-run would disassemble+create"
                                : "dry-run would disassemble+create and name " + t.desiredName;
                            pw.println(
                                t.addr.toString() + "\t" +
                                status + "\t" +
                                name + "\t" +
                                sig + "\t" +
                                note
                            );
                            continue;
                        }

                        boolean disasmOk = disassemble(t.addr);
                        Function createdFn = createFunction(t.addr, null);
                        if (createdFn != null) {
                            status = "created";
                            created++;
                            if (!t.desiredName.isEmpty()) {
                                createdFn.setName(t.desiredName, SourceType.USER_DEFINED);
                                renamed++;
                            }
                            name = createdFn.getName();
                            sig = createdFn.getSignature().toString().replace('\t', ' ').replace('\n', ' ');
                            note = disasmOk ? "disassemble+create succeeded" : "create succeeded (disassemble returned false)";
                            if (!t.desiredName.isEmpty()) {
                                note += "; renamed";
                            }
                        } else {
                            failed++;
                            status = "failed";
                            note = disasmOk ? "createFunction returned null after disassemble" : "disassemble and create failed";
                        }
                    }
                } catch (Exception ex) {
                    failed++;
                    status = "failed";
                    note = ex.getClass().getSimpleName() + ": " + ex.getMessage();
                }

                pw.println(
                    t.addr.toString() + "\t" +
                    status + "\t" +
                    name + "\t" +
                    sig + "\t" +
                    note
                );
            }
        }

        println("CreateFunctionsFromAddressList complete: mode=" + (dryRun ? "dry" : "apply") +
            " targets=" + targets.size() +
            " created=" + created +
            " would_create=" + wouldCreate +
            " already_exists=" + already +
            " renamed=" + renamed +
            " would_rename=" + wouldRename +
            " failed=" + failed);
        println("Output TSV: " + outFile.getAbsolutePath());
    }
}
