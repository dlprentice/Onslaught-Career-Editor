//@category Analysis

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Instruction;

import java.io.File;
import java.io.PrintWriter;

public class DumpDisassemblyRange extends GhidraScript {

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 3) {
            popup("Usage: DumpDisassemblyRange.java <start_addr> <end_addr> <out_file>");
            return;
        }

        String startText = args[0].startsWith("0x") || args[0].startsWith("0X") ? args[0] : "0x" + args[0];
        String endText = args[1].startsWith("0x") || args[1].startsWith("0X") ? args[1] : "0x" + args[1];
        Address start = toAddr(startText);
        Address end = toAddr(endText);
        if (start == null || end == null) {
            throw new IllegalArgumentException("Bad address range: " + startText + " .. " + endText);
        }
        if (start.compareTo(end) > 0) {
            Address t = start;
            start = end;
            end = t;
        }

        File out = new File(args[2]);
        int count = 0;
        try (PrintWriter pw = new PrintWriter(out)) {
            pw.println("address\tbytes\tmnemonic\toperands");
            Instruction ins = getInstructionAt(start);
            if (ins == null) {
                ins = getInstructionAfter(start);
            }
            while (ins != null && ins.getAddress().compareTo(end) <= 0 && !monitor.isCancelled()) {
                String bytes = getBytes(ins.getAddress(), ins.getLength()) != null
                    ? bytesToHex(getBytes(ins.getAddress(), ins.getLength()))
                    : "";
                pw.println(
                    ins.getAddress().toString() + "\t" +
                    bytes + "\t" +
                    ins.getMnemonicString() + "\t" +
                    renderOperands(ins)
                );
                count++;
                ins = getInstructionAfter(ins);
            }
        }

        println("DumpDisassemblyRange: wrote " + count + " instruction rows to " + out.getAbsolutePath());
    }

    private static String bytesToHex(byte[] b) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < b.length; i++) {
            if (i != 0) sb.append(' ');
            sb.append(String.format("%02X", b[i] & 0xFF));
        }
        return sb.toString();
    }

    private static String renderOperands(Instruction ins) {
        int n = ins.getNumOperands();
        if (n <= 0) {
            return "";
        }
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i != 0) {
                sb.append(", ");
            }
            sb.append(ins.getDefaultOperandRepresentation(i));
        }
        return sb.toString();
    }
}
