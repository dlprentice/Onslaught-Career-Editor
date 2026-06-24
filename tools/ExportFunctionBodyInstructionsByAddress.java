//@category Analysis

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryAccessException;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;

public class ExportFunctionBodyInstructionsByAddress extends GhidraScript {

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

    private void writeInstruction(PrintWriter pw, Target target, Function fn, Instruction instr, int ordinal) {
        String flow = instr.getFlowType() != null ? instr.getFlowType().toString() : "";
        pw.println(
            target.raw + "\t" +
            "0x" + target.addr.toString() + "\t" +
            ordinal + "\t" +
            "0x" + fn.getEntryPoint().toString() + "\t" +
            clean(fn.getName()) + "\t" +
            "0x" + instr.getAddress().toString() + "\t" +
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
            popup("Usage: ExportFunctionBodyInstructionsByAddress.java <addresses_file> <out_tsv>");
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
                Address addr = toAddr(tok);
                if (addr == null) {
                    println("BADADDR: " + line);
                    continue;
                }
                targets.add(new Target(tok, addr));
            }
        }

        Listing listing = currentProgram.getListing();
        int rows = 0;
        int missing = 0;

        try (PrintWriter pw = new PrintWriter(outFile, "UTF-8")) {
            pw.println("target_raw\ttarget_addr\tordinal\tfunction_entry\tfunction_name\tinstruction_addr\tmnemonic\toperands\tbytes\tflow_type");
            for (Target target : targets) {
                Function fn = getFunctionAt(target.addr);
                if (fn == null) {
                    Function containing = getFunctionContaining(target.addr);
                    if (containing != null && containing.getEntryPoint().equals(target.addr)) {
                        fn = containing;
                    }
                }
                if (fn == null) {
                    pw.println(target.raw + "\t0x" + target.addr.toString() + "\t0\t<none>\t<no_function>\t<none>\t\t\t\tMISSING");
                    missing++;
                    rows++;
                    continue;
                }

                int ordinal = 0;
                InstructionIterator instructions = listing.getInstructions(fn.getBody(), true);
                while (instructions.hasNext()) {
                    writeInstruction(pw, target, fn, instructions.next(), ordinal++);
                    rows++;
                }
            }
        }

        println("Wrote " + rows + " function-body instruction rows to: " + outFile.getAbsolutePath());
        println("targets=" + targets.size() + " missing=" + missing);
    }
}
