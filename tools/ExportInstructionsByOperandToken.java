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
import java.util.Locale;

public class ExportInstructionsByOperandToken extends GhidraScript {

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

    private static List<String> readTokens(File tokenFile) throws Exception {
        List<String> tokens = new ArrayList<>();
        try (BufferedReader br = new BufferedReader(new FileReader(tokenFile))) {
            String line;
            while ((line = br.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty() || line.startsWith("#")) {
                    continue;
                }
                tokens.add(line);
            }
        }
        return tokens;
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 2) {
            popup("Usage: ExportInstructionsByOperandToken.java <tokens_file> <out_tsv>");
            return;
        }

        File tokenFile = new File(args[0]);
        File outFile = new File(args[1]);
        if (!tokenFile.exists()) {
            println("Token file not found: " + tokenFile.getAbsolutePath());
            return;
        }

        List<String> tokens = readTokens(tokenFile);
        if (tokens.isEmpty()) {
            println("No tokens in: " + tokenFile.getAbsolutePath());
            return;
        }

        Listing listing = currentProgram.getListing();
        InstructionIterator it = listing.getInstructions(true);
        int rows = 0;
        int instructions = 0;

        try (PrintWriter pw = new PrintWriter(outFile)) {
            pw.println("token\tinstruction_addr\tfunction_entry\tfunction_name\tmnemonic\toperands\tbytes\tflow_type");
            while (it.hasNext() && !monitor.isCancelled()) {
                Instruction instr = it.next();
                instructions++;
                String operands = operandText(instr);
                String haystack = operands.toLowerCase(Locale.ROOT);
                for (String token : tokens) {
                    if (!haystack.contains(token.toLowerCase(Locale.ROOT))) {
                        continue;
                    }
                    Address addr = instr.getAddress();
                    Function fn = getFunctionContaining(addr);
                    String fnEntry = fn != null ? "0x" + fn.getEntryPoint().toString() : "<none>";
                    String fnName = fn != null ? fn.getName() : "<no_function>";
                    String flow = instr.getFlowType() != null ? instr.getFlowType().toString() : "";
                    pw.println(
                        clean(token) + "\t" +
                        "0x" + addr.toString() + "\t" +
                        fnEntry + "\t" +
                        clean(fnName) + "\t" +
                        clean(instr.getMnemonicString()) + "\t" +
                        operands + "\t" +
                        instructionBytes(instr) + "\t" +
                        clean(flow)
                    );
                    rows++;
                }
            }
        }

        println("Wrote " + rows + " matching instruction rows to: " + outFile.getAbsolutePath());
        println("tokens=" + tokens.size() + " instructions_scanned=" + instructions);
    }
}
