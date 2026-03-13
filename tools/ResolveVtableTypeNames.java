//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.MemoryAccessException;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;

public class ResolveVtableTypeNames extends GhidraScript {

    private static class Target {
        final String raw;
        final Address vtable;

        Target(String raw, Address vtable) {
            this.raw = raw;
            this.vtable = vtable;
        }
    }

    private String readCString(Address addr, int maxLen) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < maxLen; i++) {
            try {
                byte b = getByte(addr.add(i));
                if (b == 0) {
                    break;
                }
                sb.append((char) (b & 0xff));
            } catch (MemoryAccessException ex) {
                break;
            }
        }
        return sb.toString();
    }

    private String demangleTypeName(String raw) {
        if (raw == null) {
            return "";
        }
        // Common MSVC RTTI type descriptor name shape: .?AVClassName@@
        if (raw.startsWith(".?AV") && raw.endsWith("@@") && raw.length() > 6) {
            return raw.substring(4, raw.length() - 2);
        }
        if (raw.startsWith(".?AU") && raw.endsWith("@@") && raw.length() > 6) {
            return raw.substring(4, raw.length() - 2);
        }
        return raw;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 2) {
            popup("Usage: ResolveVtableTypeNames.java <vtable_addresses_file> <out_tsv>");
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

        int rows = 0;
        try (PrintWriter pw = new PrintWriter(outFile)) {
            pw.println("vtable\tcol_ptr_slot\tcol_addr\tsignature\toffset\tcd_offset\ttype_desc\tclass_desc\traw_type_name\tdemangled_type_name");

            for (Target t : targets) {
                if (monitor.isCancelled()) {
                    break;
                }

                Address colPtrSlot = t.vtable.subtract(4);
                String colAddrText = "<read_error>";
                String sigText = "<read_error>";
                String offText = "<read_error>";
                String cdOffText = "<read_error>";
                String typeDescText = "<read_error>";
                String classDescText = "<read_error>";
                String rawTypeName = "";
                String demangled = "";

                try {
                    int colRaw = getInt(colPtrSlot);
                    long colUnsigned = Integer.toUnsignedLong(colRaw);
                    Address colAddr = toAddr(colUnsigned);
                    colAddrText = colAddr != null ? colAddr.toString() : String.format("0x%08x", colRaw);

                    if (colAddr != null) {
                        int sig = getInt(colAddr);
                        int off = getInt(colAddr.add(4));
                        int cdOff = getInt(colAddr.add(8));
                        int typeRaw = getInt(colAddr.add(12));
                        int classRaw = getInt(colAddr.add(16));

                        sigText = String.format("0x%08x", sig);
                        offText = Integer.toString(off);
                        cdOffText = Integer.toString(cdOff);
                        typeDescText = String.format("0x%08x", typeRaw);
                        classDescText = String.format("0x%08x", classRaw);

                        Address typeDescAddr = toAddr(Integer.toUnsignedLong(typeRaw));
                        if (typeDescAddr != null) {
                            // TypeDescriptor layout (x86): pVFTable, spare, char name[]
                            Address nameAddr = typeDescAddr.add(8);
                            rawTypeName = readCString(nameAddr, 256);
                            demangled = demangleTypeName(rawTypeName);
                        }
                    }
                } catch (Exception ex) {
                    // Keep row with read_error markers.
                }

                pw.println(
                    t.vtable.toString() + "\t" +
                    colPtrSlot.toString() + "\t" +
                    colAddrText + "\t" +
                    sigText + "\t" +
                    offText + "\t" +
                    cdOffText + "\t" +
                    typeDescText + "\t" +
                    classDescText + "\t" +
                    rawTypeName.replace('\t', ' ').replace('\n', ' ') + "\t" +
                    demangled.replace('\t', ' ').replace('\n', ' ')
                );
                rows++;
            }
        }

        println("ResolveVtableTypeNames complete: rows=" + rows + " out=" + outFile.getAbsolutePath());
    }
}

