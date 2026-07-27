//@category Symbol
//
// Full function inventory for before/after analysis-pass diffing.
//
// Enumerates EVERY function in the program and emits one row per function with
// enough state to detect the four failure modes an aggressive analyser can
// cause: functions created, functions destroyed, function BOUNDS moved, and
// names/signatures overwritten.  The last two are the dangerous class - a
// graded name whose symbol SourceType is USER_DEFINED must survive an analysis
// pass untouched, and a name that survives on a function whose BODY changed is
// arguably worse than one that was deleted, because it silently re-points a
// reviewed label at different bytes.
//
// Usage: -postScript ExportFullFunctionInventory.java <out_functions_tsv> <out_program_tsv>

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.DataIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.security.MessageDigest;

public class ExportFullFunctionInventory extends GhidraScript {

    private static String clean(String value) {
        if (value == null) {
            return "";
        }
        return value.replace("\\", "\\\\").replace("\r", "\\r").replace("\n", "\\n").replace("\t", " ");
    }

    private static String hex(byte[] raw) {
        StringBuilder sb = new StringBuilder();
        for (byte b : raw) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

    // A stable digest of the exact address ranges owned by the function body.
    // Two functions with the same entry point but different bodies differ here.
    private String bodyDigest(AddressSetView body) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        for (ghidra.program.model.address.AddressRange range : body) {
            md.update(range.getMinAddress().toString().getBytes("UTF-8"));
            md.update((byte) ':');
            md.update(range.getMaxAddress().toString().getBytes("UTF-8"));
            md.update((byte) ';');
        }
        return hex(md.digest()).substring(0, 16);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 2) {
            println("INVENTORY_FAIL reason=usage <out_functions_tsv> <out_program_tsv>");
            return;
        }

        Listing listing = currentProgram.getListing();
        int total = 0;

        try (BufferedWriter bw = new BufferedWriter(new FileWriter(new File(args[0])))) {
            bw.write("address\tname\tfqname\tnameSource\tsigSource\tbodyBytes\tbodyMin\tbodyMax"
                + "\tbodyRanges\tbodyDigest\tinstrCount\tparamCount\tcallingConv\treturnType\tvarArgs"
                + "\tisThunk\tthunkTarget\tisExternal\tcustomStorage\tinline\tnoReturn\tframeSize"
                + "\tlocalSize\tparamSize\tsignature\tcommentLen\ttags\n");

            FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
            while (it.hasNext() && !monitor.isCancelled()) {
                Function fn = it.next();
                total++;

                AddressSetView body = fn.getBody();
                int instrCount = 0;
                InstructionIterator ii = listing.getInstructions(body, true);
                while (ii.hasNext()) {
                    ii.next();
                    instrCount++;
                }

                Symbol sym = fn.getSymbol();
                String nameSource = sym == null ? "NO_SYMBOL" : sym.getSource().toString();
                Function thunked = fn.isThunk() ? fn.getThunkedFunction(false) : null;
                String comment = fn.getComment();

                StringBuilder tags = new StringBuilder();
                for (ghidra.program.model.listing.FunctionTag tag : fn.getTags()) {
                    if (tags.length() > 0) {
                        tags.append(',');
                    }
                    tags.append(tag.getName());
                }

                bw.write("0x" + fn.getEntryPoint().toString()
                    + "\t" + clean(fn.getName())
                    + "\t" + clean(fn.getName(true))
                    + "\t" + nameSource
                    + "\t" + fn.getSignatureSource().toString()
                    + "\t" + body.getNumAddresses()
                    + "\t0x" + (body.getMinAddress() == null ? "" : body.getMinAddress().toString())
                    + "\t0x" + (body.getMaxAddress() == null ? "" : body.getMaxAddress().toString())
                    + "\t" + body.getNumAddressRanges()
                    + "\t" + bodyDigest(body)
                    + "\t" + instrCount
                    + "\t" + fn.getParameterCount()
                    + "\t" + clean(fn.getCallingConventionName())
                    + "\t" + clean(fn.getReturn().getDataType().getDisplayName())
                    + "\t" + fn.hasVarArgs()
                    + "\t" + fn.isThunk()
                    + "\t" + (thunked == null ? "" : "0x" + thunked.getEntryPoint().toString())
                    + "\t" + fn.isExternal()
                    + "\t" + fn.hasCustomVariableStorage()
                    + "\t" + fn.isInline()
                    + "\t" + fn.hasNoReturn()
                    + "\t" + fn.getStackFrame().getFrameSize()
                    + "\t" + fn.getStackFrame().getLocalSize()
                    + "\t" + fn.getStackFrame().getParameterSize()
                    + "\t" + clean(fn.getSignature().getPrototypeString(true))
                    + "\t" + (comment == null ? 0 : comment.length())
                    + "\t" + tags
                    + "\n");
            }
        }

        // Program-level counters.  These catch effects that never surface as a
        // function row: bytes newly disassembled, data newly defined, symbols
        // created outside function scope.
        long instrTotal = 0;
        InstructionIterator all = listing.getInstructions(true);
        while (all.hasNext() && !monitor.isCancelled()) {
            all.next();
            instrTotal++;
        }
        long dataDefined = 0;
        DataIterator dit = listing.getDefinedData(true);
        while (dit.hasNext() && !monitor.isCancelled()) {
            dit.next();
            dataDefined++;
        }
        long undefinedData = 0;
        DataIterator udit = listing.getData(true);
        while (udit.hasNext() && !monitor.isCancelled()) {
            Data d = udit.next();
            if (!d.isDefined()) {
                undefinedData++;
            }
        }

        long userSymbols = 0;
        long analysisSymbols = 0;
        long importedSymbols = 0;
        long defaultSymbols = 0;
        for (Symbol s : currentProgram.getSymbolTable().getAllSymbols(true)) {
            SourceType st = s.getSource();
            if (st == SourceType.USER_DEFINED) {
                userSymbols++;
            } else if (st == SourceType.ANALYSIS) {
                analysisSymbols++;
            } else if (st == SourceType.IMPORTED) {
                importedSymbols++;
            } else {
                defaultSymbols++;
            }
        }

        try (BufferedWriter bw = new BufferedWriter(new FileWriter(new File(args[1])))) {
            bw.write("metric\tvalue\n");
            bw.write("functions\t" + total + "\n");
            bw.write("instructions\t" + instrTotal + "\n");
            bw.write("definedData\t" + dataDefined + "\n");
            bw.write("undefinedData\t" + undefinedData + "\n");
            bw.write("symbolsUserDefined\t" + userSymbols + "\n");
            bw.write("symbolsAnalysis\t" + analysisSymbols + "\n");
            bw.write("symbolsImported\t" + importedSymbols + "\n");
            bw.write("symbolsDefaultOther\t" + defaultSymbols + "\n");
            bw.write("relocations\t" + currentProgram.getRelocationTable().getSize() + "\n");
            for (MemoryBlock block : currentProgram.getMemory().getBlocks()) {
                bw.write("block:" + block.getName() + "\t0x" + block.getStart() + "-0x"
                    + block.getEnd() + " size=" + block.getSize() + " x=" + block.isExecute() + "\n");
            }
        }

        println("INVENTORY_OK functions=" + total + " instructions=" + instrTotal
            + " definedData=" + dataDefined + " undefinedData=" + undefinedData
            + " userSymbols=" + userSymbols);
    }
}
