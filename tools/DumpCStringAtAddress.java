//@category Data

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.mem.MemoryAccessException;

import java.io.File;
import java.io.PrintWriter;

public class DumpCStringAtAddress extends GhidraScript {

    private String readCString(Address addr, int maxLen) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < maxLen; i++) {
            try {
                byte b = getByte(addr.add(i));
                if (b == 0) {
                    break;
                }
                int ub = b & 0xff;
                if (ub < 0x20 || ub > 0x7e) {
                    sb.append(String.format("\\x%02x", ub));
                } else {
                    sb.append((char) ub);
                }
            } catch (MemoryAccessException ex) {
                break;
            }
        }
        return sb.toString();
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 2) {
            popup("Usage: DumpCStringAtAddress.java <address_or_ptr_address> <out_tsv> [max_len] [mode=direct|ptr]");
            return;
        }

        String addrArg = args[0];
        String mode = (args.length >= 4 && args[3] != null && !args[3].trim().isEmpty()) ? args[3].trim() : "direct";
        int maxLen = 256;
        if (args.length >= 3 && args[2] != null && !args[2].trim().isEmpty()) {
            maxLen = Integer.parseInt(args[2].trim());
        }
        if (!addrArg.startsWith("0x") && !addrArg.startsWith("0X")) {
            addrArg = "0x" + addrArg;
        }

        Address input = toAddr(addrArg);
        if (input == null) {
            throw new IllegalArgumentException("Bad address: " + addrArg);
        }

        Address target = input;
        String ptrRaw = "";
        if ("ptr".equalsIgnoreCase(mode)) {
            int raw = getInt(input);
            ptrRaw = String.format("0x%08x", raw);
            target = toAddr(Integer.toUnsignedLong(raw));
            if (target == null) {
                throw new IllegalStateException("Pointer did not resolve from " + input + ": " + ptrRaw);
            }
        }

        String text = readCString(target, maxLen);
        File out = new File(args[1]);
        try (PrintWriter pw = new PrintWriter(out)) {
            pw.println("input_addr\tmode\tptr_raw\ttarget_addr\tcstring");
            pw.println(
                input.toString() + "\t" +
                mode + "\t" +
                ptrRaw + "\t" +
                target.toString() + "\t" +
                text.replace('\t', ' ').replace('\n', ' ')
            );
        }

        println("DumpCStringAtAddress complete: input=" + input + " target=" + target + " text=" + text);
    }
}

