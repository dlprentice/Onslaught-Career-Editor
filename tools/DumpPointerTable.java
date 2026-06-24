//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.mem.MemoryAccessException;

import java.io.File;
import java.io.PrintWriter;

public class DumpPointerTable extends GhidraScript {

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 3) {
            popup("Usage: DumpPointerTable.java <table_addr> <entry_count> <out_tsv>");
            return;
        }

        String tableArg = args[0];
        if (!tableArg.startsWith("0x") && !tableArg.startsWith("0X")) {
            tableArg = "0x" + tableArg;
        }
        Address table = toAddr(tableArg);
        if (table == null) {
            println("Bad table address: " + args[0]);
            return;
        }

        int count = Integer.parseInt(args[1]);
        File outFile = new File(args[2]);

        int rows = 0;
        try (PrintWriter pw = new PrintWriter(outFile)) {
            pw.println("slot\tentry_addr\tptr\tptr_name\tptr_signature");
            for (int i = 0; i < count; i++) {
                if (monitor.isCancelled()) {
                    break;
                }
                Address entryAddr = table.add(i * 4L);
                String ptrText = "<read_error>";
                String name = "<none>";
                String sig = "<none>";

                try {
                    int raw = getInt(entryAddr);
                    long unsigned = Integer.toUnsignedLong(raw);
                    Address ptr = toAddr(unsigned);
                    ptrText = ptr != null ? ptr.toString() : String.format("0x%08x", raw);

                    if (ptr != null) {
                        Function fn = getFunctionAt(ptr);
                        if (fn == null) {
                            Function cf = getFunctionContaining(ptr);
                            if (cf != null && cf.getEntryPoint().equals(ptr)) {
                                fn = cf;
                            }
                        }
                        if (fn != null) {
                            name = fn.getName();
                            sig = fn.getSignature().toString().replace('\t', ' ').replace('\n', ' ');
                        }
                    }
                } catch (MemoryAccessException ex) {
                    ptrText = "<memory_access_exception>";
                    name = "<memory_access_exception>";
                    sig = ex.getMessage();
                }

                pw.println(
                    i + "\t" +
                    entryAddr.toString() + "\t" +
                    ptrText + "\t" +
                    name + "\t" +
                    sig
                );
                rows++;
            }
        }

        println("DumpPointerTable complete: rows=" + rows + " out=" + outFile.getAbsolutePath());
    }
}
