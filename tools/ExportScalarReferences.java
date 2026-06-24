//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.scalar.Scalar;

import java.io.File;
import java.io.PrintWriter;
import java.util.HashSet;
import java.util.Set;

public class ExportScalarReferences extends GhidraScript {

    private static String clean(String value) {
        if (value == null) {
            return "";
        }
        return value.replace('\t', ' ').replace('\r', ' ').replace('\n', ' ').trim();
    }

    private static Long parseScalarToken(String token) {
        try {
            if (token.startsWith("0x") || token.startsWith("0X")) {
                return Long.parseUnsignedLong(token.substring(2), 16);
            }
            return Long.parseLong(token);
        } catch (NumberFormatException ex) {
            return null;
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 2) {
            popup("Usage: ExportScalarReferences.java <out_tsv> <value> [value...]");
            return;
        }

        File outFile = new File(args[0]);
        Set<Long> targets = new HashSet<>();
        for (int i = 1; i < args.length; i++) {
            Long parsed = parseScalarToken(args[i].trim());
            if (parsed == null) {
                println("BADVALUE: " + args[i]);
                continue;
            }
            targets.add(parsed);
        }
        if (targets.isEmpty()) {
            println("No valid scalar values supplied.");
            return;
        }

        int rows = 0;
        try (PrintWriter pw = new PrintWriter(outFile)) {
            pw.println("value_decimal\tvalue_hex\tinstruction_addr\tfunction_addr\tfunction\tblock\tmnemonic\toperand_index\toperand");
            for (Instruction instruction : currentProgram.getListing().getInstructions(true)) {
                Address address = instruction.getAddress();
                Function function = getFunctionContaining(address);
                String functionName = function != null ? function.getName() : "<no_function>";
                String functionAddress = function != null ? function.getEntryPoint().toString() : "<none>";
                MemoryBlock block = currentProgram.getMemory().getBlock(address);
                String blockName = block != null ? block.getName() : "<no_block>";

                for (int operandIndex = 0; operandIndex < instruction.getNumOperands(); operandIndex++) {
                    Object[] objects = instruction.getOpObjects(operandIndex);
                    for (Object object : objects) {
                        if (!(object instanceof Scalar)) {
                            continue;
                        }
                        Scalar scalar = (Scalar) object;
                        long unsignedValue = scalar.getUnsignedValue();
                        if (!targets.contains(unsignedValue)) {
                            continue;
                        }
                        String operand = clean(instruction.getDefaultOperandRepresentation(operandIndex));
                        pw.println(
                            unsignedValue + "\t" +
                            "0x" + Long.toHexString(unsignedValue) + "\t" +
                            address.toString() + "\t" +
                            functionAddress + "\t" +
                            clean(functionName) + "\t" +
                            clean(blockName) + "\t" +
                            clean(instruction.getMnemonicString()) + "\t" +
                            operandIndex + "\t" +
                            operand
                        );
                        rows++;
                    }
                }
            }
        }

        println("Wrote " + rows + " scalar rows to: " + outFile.getAbsolutePath());
    }
}
