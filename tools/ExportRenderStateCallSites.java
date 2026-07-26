//@category Analysis
// Read-only. Recovers Direct3D SetRenderState call sites and their literal
// (state, value) immediate pairs.
//
// Usage:
//   ExportRenderStateCallSites.java <setter_addresses_file> <out_tsv> [lookback]
//
// <setter_addresses_file> lists one 0x-prefixed address per line naming a
// render-state setter whose signature is (state, value) — either __stdcall
// (both pushed, value first) or __thiscall/__fastcall.
//
// For every CALL reference to each setter the script walks backwards up to
// <lookback> instructions inside the calling function and records every
// PUSH <imm> and MOV <reg>, <imm> it sees, so the literal state id and value
// can be read directly off the instruction bytes.
//
// The script performs no writes of any kind against the program database.

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.lang.Register;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryAccessException;
import ghidra.program.model.scalar.Scalar;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

public class ExportRenderStateCallSites extends GhidraScript {

    private static String hexBytes(Instruction instr) {
        try {
            byte[] b = instr.getBytes();
            StringBuilder sb = new StringBuilder();
            for (byte x : b) {
                if (sb.length() > 0) {
                    sb.append(' ');
                }
                sb.append(String.format("%02X", x & 0xff));
            }
            return sb.toString();
        } catch (MemoryAccessException ex) {
            return "";
        }
    }

    private static String clean(String s) {
        if (s == null) {
            return "";
        }
        return s.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ');
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 2) {
            println("Usage: ExportRenderStateCallSites.java <setter_addresses_file> <out_tsv> [lookback]");
            return;
        }

        File inFile = new File(args[0].trim());
        File outFile = new File(args[1].trim());
        int lookback = 20;
        if (args.length > 2 && args[2] != null && !args[2].trim().isEmpty()) {
            lookback = Integer.parseInt(args[2].trim());
        }

        List<Address> setters = new ArrayList<>();
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
                if (a != null) {
                    setters.add(a);
                }
            }
        }

        Listing listing = currentProgram.getListing();
        int rows = 0;

        try (PrintWriter pw = new PrintWriter(outFile, "UTF-8")) {
            pw.println("callee_addr\tcallee_name\tcall_site\tcaller_func\tcaller_addr\tseq\tinstr_addr\tbytes\tinstruction");

            for (Address setter : setters) {
                Function callee = getFunctionAt(setter);
                String calleeName = callee == null ? "<none>" : callee.getName();

                List<Address> callSites = new ArrayList<>();
                ReferenceIterator it = currentProgram.getReferenceManager()
                        .getReferencesTo(setter);
                while (it.hasNext()) {
                    Reference r = it.next();
                    RefType t = r.getReferenceType();
                    if (t.isCall() || t.isJump()) {
                        callSites.add(r.getFromAddress());
                    }
                }

                for (Address site : callSites) {
                    Function caller = getFunctionContaining(site);
                    String callerName = caller == null ? "<none>" : caller.getName();
                    String callerAddr = caller == null ? "" : caller.getEntryPoint().toString();

                    // Collect the lookback window, then emit oldest-first.
                    List<Instruction> window = new ArrayList<>();
                    Instruction cur = listing.getInstructionAt(site);
                    if (cur == null) {
                        continue;
                    }
                    window.add(cur);
                    Instruction prev = cur;
                    for (int i = 0; i < lookback; i++) {
                        prev = prev.getPrevious();
                        if (prev == null) {
                            break;
                        }
                        if (caller != null && !caller.getBody().contains(prev.getAddress())) {
                            break;
                        }
                        window.add(0, prev);
                    }

                    int seq = -(window.size() - 1);
                    for (Instruction ins : window) {
                        pw.println(setter + "\t" + clean(calleeName) + "\t" + site + "\t"
                                + clean(callerName) + "\t" + callerAddr + "\t" + seq + "\t"
                                + ins.getAddress() + "\t" + hexBytes(ins) + "\t"
                                + clean(ins.toString()));
                        seq++;
                        rows++;
                    }
                }
            }
        }

        println("ExportRenderStateCallSites: setters=" + setters.size() + " rows=" + rows
                + " out=" + outFile.getAbsolutePath());
    }
}
