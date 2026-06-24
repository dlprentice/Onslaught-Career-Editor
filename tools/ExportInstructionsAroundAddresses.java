//@category Analysis

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryAccessException;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class ExportInstructionsAroundAddresses extends GhidraScript {

    private static class Target {
        final String raw;
        final Address addr;

        Target(String raw, Address addr) {
            this.raw = raw;
            this.addr = addr;
        }
    }

    private static String clean(String value) {
        if (value == null) {
            return "";
        }
        return value.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ');
    }

    private static String bytesToHex(byte[] bytes) {
        if (bytes == null || bytes.length == 0) {
            return "";
        }
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            if (sb.length() > 0) {
                sb.append(' ');
            }
            sb.append(String.format("%02x", b & 0xff));
        }
        return sb.toString();
    }

    private static String instructionBytes(Instruction instr) {
        try {
            return bytesToHex(instr.getBytes());
        } catch (MemoryAccessException ex) {
            return "<memory-access-error>";
        }
    }

    private String operandText(Instruction instr) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < instr.getNumOperands(); i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(instr.getDefaultOperandRepresentation(i));
        }
        return clean(sb.toString());
    }

    private void writeInstruction(PrintWriter pw, Target target, Instruction instr, String role, int ordinal) {
        Function fn = getFunctionContaining(instr.getAddress());
        String fnEntry = fn != null ? "0x" + fn.getEntryPoint().toString() : "<none>";
        String fnName = fn != null ? fn.getName() : "<no_function>";
        String flow = instr.getFlowType() != null ? instr.getFlowType().toString() : "";
        pw.println(
            target.raw + "\t" +
            "0x" + target.addr.toString() + "\t" +
            role + "\t" +
            ordinal + "\t" +
            "0x" + instr.getAddress().toString() + "\t" +
            fnEntry + "\t" +
            clean(fnName) + "\t" +
            clean(instr.getMnemonicString()) + "\t" +
            operandText(instr) + "\t" +
            instructionBytes(instr) + "\t" +
            clean(flow)
        );
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 2) {
            popup("Usage: ExportInstructionsAroundAddresses.java <addresses_file> <out_tsv> [before_count] [after_count]");
            return;
        }

        File inFile = new File(args[0]);
        File outFile = new File(args[1]);
        int beforeCount = 12;
        int afterCount = 24;
        if (args.length > 2 && args[2] != null && !args[2].trim().isEmpty()) {
            beforeCount = Integer.parseInt(args[2].trim());
        }
        if (args.length > 3 && args[3] != null && !args[3].trim().isEmpty()) {
            afterCount = Integer.parseInt(args[3].trim());
        }

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

        Listing listing = currentProgram.getListing();
        int rows = 0;
        int missing = 0;

        try (PrintWriter pw = new PrintWriter(outFile)) {
            pw.println("target_raw\ttarget_addr\trole\tordinal\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type");
            for (Target target : targets) {
                Instruction center = listing.getInstructionContaining(target.addr);
                if (center == null) {
                    pw.println(target.raw + "\t0x" + target.addr.toString() + "\tMISSING\t0\t<none>\t<none>\t<no_instruction>\t\t\t\t");
                    missing++;
                    rows++;
                    continue;
                }

                List<Instruction> before = new ArrayList<>();
                Instruction cursor = center;
                for (int i = 0; i < beforeCount; i++) {
                    cursor = cursor.getPrevious();
                    if (cursor == null) {
                        break;
                    }
                    before.add(cursor);
                }
                Collections.reverse(before);
                int ordinal = -before.size();
                for (Instruction instr : before) {
                    writeInstruction(pw, target, instr, "BEFORE", ordinal++);
                    rows++;
                }

                writeInstruction(pw, target, center, "TARGET", 0);
                rows++;

                cursor = center;
                for (int i = 1; i <= afterCount; i++) {
                    cursor = cursor.getNext();
                    if (cursor == null) {
                        break;
                    }
                    writeInstruction(pw, target, cursor, "AFTER", i);
                    rows++;
                }
            }
        }

        println("Wrote " + rows + " instruction rows to: " + outFile.getAbsolutePath());
        println("targets=" + targets.size() + " missing=" + missing);
    }
}
