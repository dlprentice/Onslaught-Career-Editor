//@category Symbol
//
// READ-ONLY inspector for the CTentacle factory-name chain ceremony.
//
// It writes no database state of any kind: no transaction is ever opened, and
// the only files it produces are the census and receipt paths passed as
// arguments.  It is therefore safe to point at the live maintainer project with
// -readOnly, at a restored replica, or at the tracked snapshot.
//
// What it measures, so a later lane can recheck the promotion without trusting
// any prose:
//
//   1. program identity and the program-scope symbol population;
//   2. the COMPLETE symbol census - every SymbolType, every namespace, dynamic
//      symbols included - as a sorted TSV plus its digest, which is what makes
//      "this name is held by nobody" a measurement rather than an assertion;
//   3. NAME FREEDOM for each name named on the command line: the exact list of
//      holders, with type, namespace and source, so a Label in a foreign
//      namespace or an ANALYSIS-source label cannot hide;
//   4. the RTTI anchor chain read out of the program's own bytes -
//      factory -> installed vtable -> [vtable-4] Complete Object Locator ->
//      TypeDescriptor -> mangled class name - which is the evidence the name
//      rests on, cross-checkable against the pristine specimen;
//   5. the live function row for each anchor address.
//
// Usage:
//   -postScript GhidraInspectTentacleChain.java <symbolCensusTsv> <outJson>
//                                               <name> [<name> ...]
//
// Ghidra's headless launcher splits script arguments on commas, so the names may
// be given either as separate arguments or as one comma-joined argument.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

public class GhidraInspectTentacleChain extends GhidraScript {

    static final String SCHEMA = "bea.ghidra.tentacle-chain.inspect.v1";

    /** The three consecutive CTentacle vtable slots this chain concerns. */
    static final long[] FACTORIES = {0x004F0760L, 0x004F07E0L, 0x004F0860L};

    static String hex(byte[] b) {
        StringBuilder sb = new StringBuilder();
        for (byte x : b) sb.append(String.format("%02x", x & 0xff));
        return sb.toString();
    }

    static String sha256(String s) throws Exception {
        return hex(MessageDigest.getInstance("SHA-256")
            .digest(s.getBytes(StandardCharsets.UTF_8)));
    }

    static String esc(String s) {
        if (s == null) return "";
        return s.replace('\t', ' ').replace('\n', ' ').replace('\r', ' ');
    }

    static String json(String v) {
        if (v == null) return "null";
        StringBuilder sb = new StringBuilder("\"");
        for (char c : v.toCharArray()) {
            if (c == '"' || c == '\\') sb.append('\\').append(c);
            else if (c == '\n') sb.append("\\n");
            else if (c == '\t') sb.append("\\t");
            else if (c < 0x20) sb.append(String.format("\\u%04x", (int) c));
            else sb.append(c);
        }
        return sb.append('"').toString();
    }

    private int rd32(long va) throws Exception {
        byte[] b = new byte[4];
        int n = currentProgram.getMemory().getBytes(toAddr(va), b);
        if (n != 4) throw new IllegalStateException("short read at " + va);
        return ((b[3] & 0xff) << 24) | ((b[2] & 0xff) << 16)
             | ((b[1] & 0xff) << 8) | (b[0] & 0xff);
    }

    private String cstr(long va) throws Exception {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < 512; i++) {
            byte[] b = new byte[1];
            currentProgram.getMemory().getBytes(toAddr(va + i), b);
            if (b[0] == 0) break;
            sb.append((char) (b[0] & 0xff));
        }
        return sb.toString();
    }

    private String bytesAt(long va, int n) throws Exception {
        byte[] b = new byte[n];
        currentProgram.getMemory().getBytes(toAddr(va), b);
        return hex(b);
    }

    /** Scan [lo,hi) for `mov dword ptr [r/m], imm32` whose immediate looks
     *  like an MSVC vtable: [imm-4] is a Complete Object Locator with
     *  signature 0 and a readable TypeDescriptor. */
    private List<String> anchorChain(long lo, long hi) {
        List<String> out = new ArrayList<>();
        long i = lo;
        while (i < hi - 6) {
            try {
                byte[] b = new byte[2];
                currentProgram.getMemory().getBytes(toAddr(i), b);
                if ((b[0] & 0xff) == 0xC7) {
                    int modrm = b[1] & 0xff;
                    int mod = modrm >> 6, rm = modrm & 7;
                    long j = i + 2;
                    if (rm == 4) j += 1;
                    if (mod == 1) j += 1;
                    else if (mod == 2) j += 4;
                    else if (mod == 0 && rm == 5) j += 4;
                    if (mod != 3 && j + 4 <= hi) {
                        long imm = rd32(j) & 0xffffffffL;
                        long col = rd32(imm - 4) & 0xffffffffL;
                        int sig = rd32(col);
                        int offset = rd32(col + 4);
                        long td = rd32(col + 12) & 0xffffffffL;
                        long chd = rd32(col + 16) & 0xffffffffL;
                        long slot0 = rd32(imm) & 0xffffffffL;
                        if (sig == 0 && slot0 != 0) {
                            String nm = cstr(td + 8);
                            if (nm.startsWith(".?AV")) {
                                out.add(String.format(
                                    "store@%08x enc=%s vtable=%08x col=%08x "
                                    + "colOffset=%d td=%08x nameVa=%08x "
                                    + "name=%s chd=%08x slot0=%08x",
                                    i, bytesAt(i, (int) (j + 4 - i)), imm, col,
                                    offset, td, td + 8, nm, chd, slot0));
                            }
                        }
                        i = j + 4;
                        continue;
                    }
                }
            } catch (Exception ignore) {
                // unreadable or non-pointer immediate: not an anchor
            }
            i++;
        }
        return out;
    }

    @Override
    protected void run() throws Exception {
        String[] a = getScriptArgs();
        if (a == null || a.length < 3) {
            throw new IllegalArgumentException(
                "usage: <symbolCensusTsv> <outJson> <name>[,<name>...]");
        }
        String projectDir = state.getProject().getProjectLocator()
            .getProjectDir().getAbsolutePath();
        println("TENTACLE_INSPECT project=" + projectDir);
        println("TENTACLE_INSPECT identity program=" + currentProgram.getName()
            + " md5=" + currentProgram.getExecutableMD5()
            + " sha256=" + (currentProgram.getExecutableSHA256() == null ? ""
                : currentProgram.getExecutableSHA256().toLowerCase(Locale.ROOT))
            + " language=" + currentProgram.getLanguageID().getIdAsString()
            + " compilerSpec="
            + currentProgram.getCompilerSpec().getCompilerSpecID().getIdAsString()
            + " imageBase=" + currentProgram.getImageBase());

        // ---- complete symbol census ---------------------------------------
        StringBuilder sb = new StringBuilder(
            "address\tname\tfullName\tsymbolType\tnamespace\tsource"
            + "\tisPrimary\tisGlobal\tisDynamic\n");
        List<String> rows = new ArrayList<>();
        long nSym = 0, nNonDyn = 0;
        Map<String, List<String>> holders = new LinkedHashMap<>();
        SymbolIterator it = currentProgram.getSymbolTable().getAllSymbols(true);
        while (it.hasNext()) {
            Symbol s = it.next();
            nSym++;
            boolean dyn = s.isDynamic();
            if (!dyn) nNonDyn++;
            Address ad = s.getAddress();
            String addrText = ad == null ? "-"
                : String.format("%08x", ad.getOffset());
            String row = addrText
                + "\t" + esc(s.getName())
                + "\t" + esc(s.getName(true))
                + "\t" + s.getSymbolType()
                + "\t" + esc(s.getParentNamespace() == null ? ""
                    : s.getParentNamespace().getName(true))
                + "\t" + s.getSource()
                + "\t" + s.isPrimary()
                + "\t" + s.isGlobal()
                + "\t" + dyn;
            rows.add(row);
            holders.computeIfAbsent(s.getName(), k -> new ArrayList<>()).add(row);
        }
        Collections.sort(rows);
        for (String r : rows) sb.append(r).append('\n');
        Files.write(Paths.get(a[0]), sb.toString().getBytes(StandardCharsets.UTF_8));
        String censusSha = sha256(sb.toString());
        println("TENTACLE_INSPECT symbols=" + nSym + " nonDynamic=" + nNonDyn
            + " censusSha256=" + censusSha);

        // ---- name freedom --------------------------------------------------
        // Ghidra's headless launcher splits a script argument on commas, so the
        // name list is accepted as every argument from index 2 onward and each
        // one is comma-split again.  Both spellings therefore work.
        List<String> wanted = new ArrayList<>();
        for (int k = 2; k < a.length; k++) {
            for (String tok : a[k].split(",")) {
                if (!tok.isEmpty() && !wanted.contains(tok)) wanted.add(tok);
            }
        }
        StringBuilder jNames = new StringBuilder();
        for (String want : wanted) {
            List<String> hs = holders.get(want);
            int n = hs == null ? 0 : hs.size();
            println("TENTACLE_NAME name=" + want + " holders=" + n);
            if (hs != null) {
                for (String h : hs) println("TENTACLE_NAME_HOLDER " + want
                    + " || " + h);
            }
            if (jNames.length() > 0) jNames.append(",\n");
            jNames.append("    ").append(json(want)).append(": ").append(n);
        }

        // ---- RTTI anchor chain, from the program's own bytes --------------
        StringBuilder jAnchors = new StringBuilder();
        for (int k = 0; k < FACTORIES.length; k++) {
            long va = FACTORIES[k];
            Function f = currentProgram.getFunctionManager()
                .getFunctionAt(toAddr(va));
            String nm = f == null ? "<no function>" : f.getName();
            String fq = f == null ? "" : f.getName(true);
            String src = (f == null || f.getSymbol() == null) ? ""
                : f.getSymbol().getSource().toString();
            long lo = va, hi = va;
            StringBuilder spec = new StringBuilder();
            long bodyBytes = 0;
            if (f != null) {
                AddressSetView body = f.getBody();
                int nr = 0;
                for (AddressRange r : body) {
                    if (nr > 0) spec.append(';');
                    spec.append(String.format("%08x-%08x",
                        r.getMinAddress().getOffset(),
                        r.getMaxAddress().getOffset()));
                    bodyBytes += r.getLength();
                    nr++;
                }
                lo = body.getMinAddress().getOffset();
                hi = body.getMaxAddress().getOffset() + 1;
            }
            println(String.format(
                "TENTACLE_FN %08x name=%s fqname=%s nameSource=%s "
                + "bodyBytes=%d ranges=%s sig=%s conv=%s thunk=%s",
                va, nm, fq, src, bodyBytes, spec,
                f == null ? "" : esc(f.getSignature().getPrototypeString()),
                f == null ? "" : f.getCallingConventionName(),
                f == null ? "" : Boolean.toString(f.isThunk())));
            List<String> chain = f == null ? new ArrayList<String>()
                : anchorChain(lo, hi);
            for (String c : chain) {
                println(String.format("TENTACLE_ANCHOR %08x %s", va, c));
            }
            if (chain.isEmpty()) {
                println(String.format(
                    "TENTACLE_ANCHOR %08x NONE-IN-OWN-BODY", va));
            }
            if (jAnchors.length() > 0) jAnchors.append(",\n");
            jAnchors.append("    ").append(json(String.format("%08x", va)))
                .append(": {\"name\": ").append(json(nm))
                .append(", \"bodyBytes\": ").append(bodyBytes)
                .append(", \"ranges\": ").append(json(spec.toString()))
                .append(", \"anchors\": [");
            for (int q = 0; q < chain.size(); q++) {
                if (q > 0) jAnchors.append(", ");
                jAnchors.append(json(chain.get(q)));
            }
            jAnchors.append("]}");
        }

        // ---- refutation corroboration: the CWarspiteAI class exists --------
        println("TENTACLE_REFUTE warspiteNameVa=0063d118 str="
            + cstr(0x0063D118L)
            + " tdVa=0063d110 tdVfptr="
            + String.format("%08x", rd32(0x0063D110L))
            + " guideNameVa=00632cf8 str=" + cstr(0x00632CF8L)
            + " aiNameVa=00632d18 str=" + cstr(0x00632D18L));

        StringBuilder j = new StringBuilder();
        j.append("{\n  \"schema\": ").append(json(SCHEMA));
        j.append(",\n  \"projectDir\": ").append(json(projectDir));
        j.append(",\n  \"programName\": ").append(json(currentProgram.getName()));
        j.append(",\n  \"executableMd5\": ")
         .append(json(currentProgram.getExecutableMD5()));
        j.append(",\n  \"executableSha256\": ")
         .append(json(currentProgram.getExecutableSHA256() == null ? null
            : currentProgram.getExecutableSHA256().toLowerCase(Locale.ROOT)));
        j.append(",\n  \"symbols\": ").append(nSym);
        j.append(",\n  \"nonDynamicSymbols\": ").append(nNonDyn);
        j.append(",\n  \"symbolCensusSha256\": ").append(json(censusSha));
        j.append(",\n  \"nameHolders\": {\n").append(jNames).append("\n  }");
        j.append(",\n  \"factories\": {\n").append(jAnchors).append("\n  }");
        j.append("\n}\n");
        Files.write(Paths.get(a[1]), j.toString().getBytes(StandardCharsets.UTF_8));
        println("TENTACLE_INSPECT_OK census=" + a[0] + " json=" + a[1]);
    }
}
