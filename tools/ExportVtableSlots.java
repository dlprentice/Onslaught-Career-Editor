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

public class ExportVtableSlots extends GhidraScript {

    private static class Target {
        final String raw;
        final Address vtable;

        Target(String raw, Address vtable) {
            this.raw = raw;
            this.vtable = vtable;
        }
    }

    private String normalizeAddr(Address addr) {
        return addr == null ? "<none>" : addr.toString();
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 2) {
            popup("Usage: ExportVtableSlots.java <vtable_addresses_file> <out_tsv> [slot_count]");
            return;
        }

        File inFile = new File(args[0]);
        File outFile = new File(args[1]);
        int slotCount = args.length >= 3 ? Integer.parseInt(args[2]) : 4;
        if (!inFile.exists()) {
            println("Input file not found: " + inFile.getAbsolutePath());
            return;
        }
        if (slotCount <= 0 || slotCount > 256) {
            throw new IllegalArgumentException("slot_count must be in 1..256");
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

        int rows = 0;
        try (PrintWriter pw = new PrintWriter(outFile)) {
            pw.println("vtable\tslot_index\tslot_addr\tpointer_raw\tpointer_addr\tfunction_entry\tfunction_name\tcontaining_entry\tcontaining_name\tstatus");

            for (Target t : targets) {
                if (monitor.isCancelled()) {
                    break;
                }
                for (int i = 0; i < slotCount; i++) {
                    Address slotAddr = t.vtable.add((long) i * 4L);
                    String pointerRaw = "<read_error>";
                    String pointerAddrText = "<read_error>";
                    String functionEntry = "<none>";
                    String functionName = "<no_function>";
                    String containingEntry = "<none>";
                    String containingName = "<no_function>";
                    String status = "OK";

                    try {
                        int raw = getInt(slotAddr);
                        pointerRaw = String.format("0x%08x", raw);
                        Address pointerAddr = toAddr(Integer.toUnsignedLong(raw));
                        pointerAddrText = normalizeAddr(pointerAddr);

                        if (pointerAddr != null) {
                            Function fn = getFunctionAt(pointerAddr);
                            if (fn != null) {
                                functionEntry = normalizeAddr(fn.getEntryPoint());
                                functionName = fn.getName();
                            } else {
                                status = "NO_FUNCTION_AT_POINTER";
                            }

                            Function containing = getFunctionContaining(pointerAddr);
                            if (containing != null) {
                                containingEntry = normalizeAddr(containing.getEntryPoint());
                                containingName = containing.getName();
                                if (fn == null) {
                                    status = "POINTER_INSIDE_FUNCTION";
                                }
                            }
                        }
                    } catch (Exception ex) {
                        status = "READ_ERROR";
                    }

                    pw.println(
                        t.vtable.toString() + "\t" +
                        i + "\t" +
                        slotAddr.toString() + "\t" +
                        pointerRaw + "\t" +
                        pointerAddrText + "\t" +
                        functionEntry + "\t" +
                        functionName + "\t" +
                        containingEntry + "\t" +
                        containingName + "\t" +
                        status
                    );
                    rows++;
                }
            }
        }

        println("ExportVtableSlots complete: targets=" + targets.size() + " rows=" + rows + " out=" + outFile.getAbsolutePath());
    }
}
