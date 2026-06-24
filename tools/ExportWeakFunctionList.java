//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;

public class ExportWeakFunctionList extends GhidraScript {

    private boolean isWeakName(String n) {
        return n.startsWith("FUN_") || n.startsWith("Auto_") || n.contains("__Unk_");
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        String outPath;
        String mode = "weak";

        if (args != null && args.length > 0 && args[0] != null && !args[0].trim().isEmpty()) {
            outPath = args[0].trim();
            if (args.length > 1 && args[1] != null && !args[1].trim().isEmpty()) {
                mode = args[1].trim().toLowerCase();
            }
        } else {
            File outFile = askFile("Select output file", "Write");
            outPath = outFile.getAbsolutePath();
        }

        boolean onlyWeak = !"all".equals(mode);

        int total = 0;
        int weak = 0;

        try (BufferedWriter bw = new BufferedWriter(new FileWriter(outPath))) {
            bw.write("address\tname\tsignature\n");

            FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
            while (it.hasNext() && !monitor.isCancelled()) {
                Function fn = it.next();
                total++;

                String name = fn.getName();
                boolean weakName = isWeakName(name);
                if (weakName) {
                    weak++;
                }

                if (onlyWeak && !weakName) {
                    continue;
                }

                String addr = "0x" + fn.getEntryPoint().toString();
                String sig = fn.getSignature().toString().replace('\t', ' ').replace('\n', ' ');
                bw.write(addr + "\t" + name + "\t" + sig + "\n");
            }
        }

        println("Export complete: " + outPath);
        println("mode=" + mode + " total_functions=" + total + " weak_functions=" + weak);
    }
}
