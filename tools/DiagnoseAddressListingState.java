//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.mem.MemoryBlock;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;

public class DiagnoseAddressListingState extends GhidraScript {
    private Address parseTargetAddress(String text) {
        if (!text.startsWith("0x") && !text.startsWith("0X")) {
            text = "0x" + text;
        }
        Address addr = toAddr(text);
        if (addr == null) {
            throw new IllegalArgumentException("Bad address: " + text);
        }
        return addr;
    }

    private String text(Object value) {
        return value == null ? "<none>" : value.toString();
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 2) {
            popup("Usage: DiagnoseAddressListingState.java <addresses_file> <out_tsv>");
            return;
        }

        File inFile = new File(args[0]);
        File outFile = new File(args[1]);
        int rows = 0;

        try (BufferedReader br = new BufferedReader(new FileReader(inFile));
             PrintWriter pw = new PrintWriter(outFile)) {
            pw.println("input\taddress\tmemory_block\tbyte0\tinstruction_at\tinstruction_containing\tdata_at\tdata_containing\tfunction_at\tfunction_containing\tstatus");
            String line;
            while ((line = br.readLine()) != null) {
                line = line.trim();
                if (line.isEmpty() || line.startsWith("#")) {
                    continue;
                }
                Address address = parseTargetAddress(line.split("\\s+")[0]);
                MemoryBlock block = currentProgram.getMemory().getBlock(address);
                String byte0 = "<read_error>";
                try {
                    byte0 = String.format("0x%02x", getByte(address) & 0xff);
                } catch (Exception ignored) {
                }

                Instruction insAt = getInstructionAt(address);
                Instruction insContaining = currentProgram.getListing().getInstructionContaining(address);
                Data dataAt = getDataAt(address);
                Data dataContaining = currentProgram.getListing().getDefinedDataContaining(address);
                Function fnAt = getFunctionAt(address);
                Function fnContaining = getFunctionContaining(address);
                String status = "OK";
                if (block == null) {
                    status = "NO_MEMORY_BLOCK";
                } else if (insAt == null && dataAt == null && dataContaining == null) {
                    status = "UNDEFINED";
                } else if (insAt == null && (dataAt != null || dataContaining != null)) {
                    status = "DEFINED_DATA";
                } else if (insAt == null && insContaining != null) {
                    status = "INSIDE_INSTRUCTION";
                } else if (insAt != null && fnAt == null) {
                    status = "INSTRUCTION_NO_FUNCTION";
                }

                pw.println(
                    line + "\t" +
                    address + "\t" +
                    text(block == null ? null : block.getName()) + "\t" +
                    byte0 + "\t" +
                    text(insAt) + "\t" +
                    text(insContaining) + "\t" +
                    text(dataAt) + "\t" +
                    text(dataContaining) + "\t" +
                    text(fnAt) + "\t" +
                    text(fnContaining) + "\t" +
                    status
                );
                rows++;
            }
        }

        println("DiagnoseAddressListingState complete: rows=" + rows + " out=" + outFile.getAbsolutePath());
    }
}
