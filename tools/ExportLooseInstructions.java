//@category Analysis
//
// Export every instruction that is NOT inside any function body.
//
// This is where an aggressive disassembler does its damage without moving the
// function count: it converts data into loose instructions that are never
// adopted into a function, permanently occupying those bytes and blocking
// later, correct interpretation.  A pass can therefore look harmless in a
// function-level diff and still have mis-read kilobytes of data as code.
//
// Usage: -postScript ExportLooseInstructions.java <out_tsv>

import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;

public class ExportLooseInstructions extends GhidraScript {

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 1) {
            println("LOOSE_FAIL reason=usage <out_tsv>");
            return;
        }
        Listing listing = currentProgram.getListing();
        long total = 0;
        long loose = 0;
        try (BufferedWriter bw = new BufferedWriter(new FileWriter(new File(args[0])))) {
            bw.write("address\tlength\tmnemonic\tbytes\n");
            InstructionIterator it = listing.getInstructions(true);
            while (it.hasNext() && !monitor.isCancelled()) {
                Instruction insn = it.next();
                total++;
                if (getFunctionContaining(insn.getAddress()) != null) {
                    continue;
                }
                loose++;
                StringBuilder hex = new StringBuilder();
                for (byte b : insn.getBytes()) {
                    hex.append(String.format("%02x", b));
                }
                bw.write("0x" + insn.getAddress().toString()
                    + "\t" + insn.getLength()
                    + "\t" + insn.getMnemonicString().replace('\t', ' ')
                    + "\t" + hex
                    + "\n");
            }
        }
        println("LOOSE_OK totalInstructions=" + total + " looseInstructions=" + loose);
    }
}
