//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.ReferenceManager;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.List;

public class ExportXrefsForAddresses extends GhidraScript {

    private static class Target {
        final String raw;
        final Address addr;
        final Function fn;

        Target(String raw, Address addr, Function fn) {
            this.raw = raw;
            this.addr = addr;
            this.fn = fn;
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 2) {
            popup("Usage: ExportXrefsForAddresses.java <addresses_file> <out_tsv>");
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
                Address a = toAddr(tok);
                if (a == null) {
                    println("BADADDR: " + line);
                    continue;
                }
                Function fn = getFunctionAt(a);
                if (fn == null) {
                    Function cf = getFunctionContaining(a);
                    if (cf != null && cf.getEntryPoint().equals(a)) {
                        fn = cf;
                    }
                }
                targets.add(new Target(tok, a, fn));
            }
        }

        ReferenceManager rm = currentProgram.getReferenceManager();
        int rows = 0;
        try (PrintWriter pw = new PrintWriter(outFile)) {
            pw.println("target_addr\ttarget_name\tfrom_addr\tfrom_function_addr\tfrom_function\tref_type");
            for (Target t : targets) {
                String targetName = t.fn != null ? t.fn.getName() : "<no_function>";
                ReferenceIterator it = rm.getReferencesTo(t.addr);
                boolean wroteAny = false;
                while (it.hasNext()) {
                    Reference r = it.next();
                    Address from = r.getFromAddress();
                    Function fromFn = getFunctionContaining(from);
                    String fromFnName = fromFn != null ? fromFn.getName() : "<no_function>";
                    RefType rt = r.getReferenceType();
                    String fromFnAddr = fromFn != null ? fromFn.getEntryPoint().toString() : "<none>";
                    pw.println(
                        t.addr.toString() + "\t" +
                        targetName + "\t" +
                        from.toString() + "\t" +
                        fromFnAddr + "\t" +
                        fromFnName + "\t" +
                        (rt != null ? rt.toString() : "<null>")
                    );
                    rows++;
                    wroteAny = true;
                }
                if (!wroteAny) {
                    pw.println(
                        t.addr.toString() + "\t" +
                        targetName + "\t" +
                        "<none>\t<none>\t<none>\t<none>"
                    );
                    rows++;
                }
            }
        }

        println("Wrote " + rows + " rows to: " + outFile.getAbsolutePath());
    }
}
