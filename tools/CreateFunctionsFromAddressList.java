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

public class CreateFunctionsFromAddressList extends GhidraScript {

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
            popup("Usage: CreateFunctionsFromAddressList.java <addresses_file> <out_tsv>");
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

                Address a = toAddr(tok);
                if (a == null) {
                    println("BADADDR: " + line);
                    continue;
                }
                targets.add(new Target(tok, a));
            }
        }

        int created = 0;
        int already = 0;
        int failed = 0;

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
                        note = "function present before create attempt";
                    } else {
                        boolean disasmOk = disassemble(t.addr);
                        Function createdFn = createFunction(t.addr, null);
                        if (createdFn != null) {
                            status = "created";
                            created++;
                            name = createdFn.getName();
                            sig = createdFn.getSignature().toString().replace('\t', ' ').replace('\n', ' ');
                            note = disasmOk ? "disassemble+create succeeded" : "create succeeded (disassemble returned false)";
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

        println("CreateFunctionsFromAddressList complete: targets=" + targets.size() +
            " created=" + created + " already_exists=" + already + " failed=" + failed);
        println("Output TSV: " + outFile.getAbsolutePath());
    }
}
