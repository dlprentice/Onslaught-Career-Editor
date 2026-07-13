//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressRangeIterator;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Parameter;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;

public class ExportFunctionAuditSnapshot extends GhidraScript {

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

    private static String bodyRanges(Function fn) {
        StringBuilder result = new StringBuilder();
        AddressSetView body = fn.getBody();
        AddressRangeIterator ranges = body.getAddressRanges();
        while (ranges.hasNext()) {
            AddressRange range = ranges.next();
            if (result.length() > 0) {
                result.append(';');
            }
            result.append(range.getMinAddress().toString());
            result.append('-');
            result.append(range.getMaxAddress().toString());
        }
        return result.toString();
    }

    private static String prototypeKey(Function fn) {
        StringBuilder result = new StringBuilder();
        result.append("cc=").append(fn.getCallingConventionName());
        result.append("|custom=").append(fn.hasCustomVariableStorage());
        result.append("|varargs=").append(fn.hasVarArgs());
        result.append("|noreturn=").append(fn.hasNoReturn());
        result.append("|return=").append(fn.getReturn().getDataType().getPathName());
        result.append('@').append(fn.getReturn().getVariableStorage().toString());
        result.append("|params=");
        Parameter[] parameters = fn.getParameters();
        for (int i = 0; i < parameters.length; i++) {
            Parameter parameter = parameters[i];
            if (i > 0) {
                result.append(';');
            }
            result.append(parameter.getOrdinal()).append(':');
            result.append(parameter.getDataType().getPathName());
            result.append('@').append(parameter.getVariableStorage().toString());
        }
        result.append("|purge=").append(fn.getStackPurgeSize());
        return result.toString();
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        String outPath;
        if (args != null && args.length > 0 && args[0] != null && !args[0].trim().isEmpty()) {
            outPath = args[0].trim();
        } else {
            File outFile = askFile("Select function audit TSV", "Write");
            outPath = outFile.getAbsolutePath();
        }

        int total = 0;
        try (BufferedWriter writer = new BufferedWriter(
                new OutputStreamWriter(new FileOutputStream(outPath), StandardCharsets.UTF_8))) {
            writer.write(
                "address\tname\tsignature\tcomment\tstatus\tbody_ranges\tbody_address_count\t" +
                "prototype_key\tcalling_convention\tvar_args\tcustom_variable_storage\tno_return\t" +
                "inline\tthunk\tthunk_target\n"
            );
            FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
            while (functions.hasNext()) {
                monitor.checkCancelled();
                Function fn = functions.next();
                Function thunked = fn.getThunkedFunction(false);
                writer.write("0x" + fn.getEntryPoint().toString());
                writer.write("\t" + escape(fn.getName()));
                writer.write("\t" + escape(fn.getSignature().toString()));
                writer.write("\t" + escape(fn.getComment()));
                writer.write("\tOK");
                writer.write("\t" + bodyRanges(fn));
                writer.write("\t" + fn.getBody().getNumAddresses());
                writer.write("\t" + escape(prototypeKey(fn)));
                writer.write("\t" + escape(fn.getCallingConventionName()));
                writer.write("\t" + fn.hasVarArgs());
                writer.write("\t" + fn.hasCustomVariableStorage());
                writer.write("\t" + fn.hasNoReturn());
                writer.write("\t" + fn.isInline());
                writer.write("\t" + fn.isThunk());
                writer.write("\t" + (thunked == null ? "" : "0x" + thunked.getEntryPoint().toString()));
                writer.write("\n");
                total++;
            }
        }
        println("Export function audit snapshot complete: " + outPath);
        println("total_functions=" + total);
    }
}
