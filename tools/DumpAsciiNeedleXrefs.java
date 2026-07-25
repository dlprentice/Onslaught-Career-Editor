//@category Analysis
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.listing.Function;
import ghidra.program.model.symbol.Reference;
import java.io.File;
import java.io.PrintWriter;
import java.nio.charset.StandardCharsets;
public class DumpAsciiNeedleXrefs extends GhidraScript {
  @Override
  protected void run() throws Exception {
    String[] args = getScriptArgs();
    File out = new File(args[0]);
    try (PrintWriter pw = new PrintWriter(out)) {
      pw.println("needle\tstring_addr\txref_from\tfrom_fn");
      for (int i = 1; i < args.length; i++) {
        String needle = args[i];
        byte[] bytes = needle.getBytes(StandardCharsets.US_ASCII);
        Address found = currentProgram.getMemory().findBytes(currentProgram.getMinAddress(), bytes, null, true, monitor);
        int hits = 0;
        while (found != null && hits < 20) {
          boolean any = false;
          for (Reference ref : getReferencesTo(found)) {
            any = true;
            Function fn = getFunctionContaining(ref.getFromAddress());
            pw.printf("%s\t0x%s\t0x%s\t%s%n", needle, found, ref.getFromAddress(), fn == null ? "<none>" : fn.getName());
          }
          if (!any) {
            pw.printf("%s\t0x%s\t\t%n", needle, found);
          }
          hits++;
          found = currentProgram.getMemory().findBytes(found.add(1), bytes, null, true, monitor);
        }
      }
    }
    println("Wrote " + out.getAbsolutePath());
  }
}
