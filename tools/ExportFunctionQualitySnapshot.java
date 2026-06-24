//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;

public class ExportFunctionQualitySnapshot extends GhidraScript {

    private static String escape(String value) {
        if (value == null) {
            return "";
        }
        return value
            .replace("\\", "\\\\")
            .replace("\r", "\\r")
            .replace("\n", "\\n")
            .replace("\t", "\\t");
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        String outPath;

        if (args != null && args.length > 0 && args[0] != null && !args[0].trim().isEmpty()) {
            outPath = args[0].trim();
        } else {
            File outFile = askFile("Select output TSV", "Write");
            outPath = outFile.getAbsolutePath();
        }

        int total = 0;
        int commented = 0;

        try (BufferedWriter bw = new BufferedWriter(new FileWriter(outPath))) {
            bw.write("address\tname\tsignature\tcomment\tstatus\n");

            FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
            while (it.hasNext() && !monitor.isCancelled()) {
                Function fn = it.next();
                total++;

                String comment = fn.getComment();
                if (comment != null && !comment.trim().isEmpty()) {
                    commented++;
                }

                bw.write("0x" + fn.getEntryPoint().toString());
                bw.write("\t");
                bw.write(escape(fn.getName()));
                bw.write("\t");
                bw.write(escape(fn.getSignature().toString()));
                bw.write("\t");
                bw.write(escape(comment));
                bw.write("\tOK\n");
            }
        }

        println("Export function quality snapshot complete: " + outPath);
        println("total_functions=" + total + " commented_functions=" + commented);
    }
}
