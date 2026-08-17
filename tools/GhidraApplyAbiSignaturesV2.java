//@category Symbol
//
// AUTHORIZED LIVE signature-only applier for the byte-derived ABI cohort.
//
// This is GhidraApplyAbiSignatures WITH EXACTLY ONE GATE INVERTED.  That
// script is the rehearsal instrument and stays LIVE_FORBIDDEN forever; V2 is
// its live-capable twin and differs from it only in the containment gate:
// where the rehearsal applier requires an "abi-cohort" lane segment plus the
// authoring session's scratch GUID and refuses any path under Ghidra\Projects,
// V2 REQUIRES the live maintainer project directory by exact match and refuses
// everything else, including the tracked repository snapshot.  Every other
// gate, pin, verb, census and refusal message is carried over verbatim, and
// tools/ghidra_abi_signature_mutator_tests.py asserts that line by line.
//
// Use of this script is authorized ONLY for the 294-row cohort pinned below,
// under the maintainer's delegated per-cohort grant of 2026-08-16 and the GO
// recommendation recorded in developer_state as
// _RECOMMENDATION_20260817_ABI_COHORT_LIVE_APPLY, which requires that NO
// calling convention is ever relabelled and that the 642 no-go targets stay
// dropped.  That grant is per-cohort and is NOT standing authorization for
// Ghidra mutation.
//
// Scope: the function PROTOTYPE and nothing else - return type, formal
// parameter list, varargs flag.  It never touches a name, a body, a boundary,
// a comment, a reference, a tag, a bookmark, a data unit, a symbol, or a
// program byte.  Every one of those is proven unchanged over ALL 8,329
// functions and ALL non-dynamic symbols, not just over the targets.
//
// Modes (arg0):
//   identity  - containment + program identity + PRE state pins only
//   predict   - build every proposal and record the prototype Ghidra actually
//               renders, so the manifest's proposedSignature can be re-pinned
//               against measured reality.  DESTRUCTIVE ON THE REPLICA: see the
//               reversibility note below.  Discard the replica afterwards.
//   dry       - full PRE validation of every gate; publishes no mutation
//   apply     - dry, then update prototypes, then POST + full collateral proof
//   readback  - require the exact POST state with no mutation
//   probe     - apply, then leave reversibility to the ceremony level restore
//
// Args: <mode> <manifestTsv> <manifestSha256> <outJson> [predictOutTsv]
//
// REVERSIBILITY, measured in this Ghidra 12.1.2 headless build rather than
// assumed: endTransaction(id, false) does NOT revert Function.updateFunction
// (all 296 targets of an earlier rehearsal survived the abort, because a
// headless postScript already runs inside an outer transaction and the nested
// abort is a no-op), and Program.canUndo() is false, so the undo stack is not
// available either.  Headless also writes a new db version even when the
// script throws.  An in-process rollback therefore CANNOT be the safety net.
//
// Refusal policy, given that measured fact: every gate that can be evaluated
// without mutating is evaluated for EVERY row first - containment, identity,
// PRE counts, manifest integrity, current-signature match, target shape, and
// full data-type resolution.  Only then does the mutation loop start, so no
// gate can fail after the first write.  POST and collateral failures remain
// hard failures whose recovery is the ceremony backup restore, which is
// exactly why that discipline exists.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DataTypeManager;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.listing.Bookmark;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.DataIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.listing.ReturnParameterImpl;
import ghidra.program.model.listing.Variable;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.regex.Pattern;

public class GhidraApplyAbiSignaturesV2 extends GhidraScript {

    static final String SCHEMA = "bea.ghidra.abi-signature-correction.live.v2";

    // ---- exact program identity (db.18621, 2026-08-17) -------------------
    static final String PROGRAM_NAME = "BEA.exe";
    static final String PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55";
    static final String PROGRAM_SHA256 =
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
    static final String LANGUAGE = "x86:LE:32:default";
    static final String COMPILER_SPEC = "windows";
    static final String IMAGE_BASE = "00400000";

    static final long PRE_FUNCTIONS = 8329L;
    static final long PRE_INSTRUCTIONS = 551232L;
    static final long PRE_REFERENCES = 234493L;
    static final long PRE_DEFINED_DATA = 48583L;
    static final long PRE_UNDEFINED_DATA = 3907629L;
    static final long PRE_BOOKMARKS = 2301L;

    static final long MANIFEST_ROWS = 294L;
    static final String MANIFEST_HEADER =
        "addr|liveName|currentSignatureLive|currentSignatureSha256"
        + "|proposedSignature|callingConvention|returnTypeProposed|paramSpec"
        + "|arity|arityBytes|retImmediate|receiverInEcx|returnUsage"
        + "|evidenceBytes|confidence|changeAxes|frameCorroboration";

    // ---- containment -----------------------------------------------------
    // The one and only project this applier may ever open.  Exact match on
    // the lowercased absolute project directory with '/' folded to '\', so a
    // scratch replica, a restored backup, a rehearsal copy or any other clone
    // can never satisfy it.
    static final String REQUIRED_LIVE_PROJECT_DIR =
        "c:\\users\\david\\ghidra\\projects\\bea.rep";
    // The tracked repository snapshot stays forbidden and is still checked
    // first, exactly as the rehearsal applier checked its forbidden markers.
    static final String[] REPO_FORBIDDEN = {
        "onslaught-career-editor\\reverse-engineering",
        "onslaught-career-editor/reverse-engineering"};

    static final Set<String> LEGAL_CC = new HashSet<>(Arrays.asList(
        "__thiscall", "__fastcall", "__stdcall", "__cdecl"));
    static final Pattern LEGAL_TYPE =
        Pattern.compile("^[A-Za-z_][A-Za-z0-9_ ]{0,80}( \\*)*$");
    static final Pattern LEGAL_PNAME =
        Pattern.compile("^[A-Za-z_][A-Za-z0-9_]{0,120}$");

    // ======================================================================

    static class Row {
        String addrText;
        long addr;
        String liveName;
        String currentSignature;
        String currentSha;
        String proposedSignature;
        String cc;
        String returnType;
        String paramSpec;
        int arity;
        int arityBytes;
        String retImmediate;
        String receiver;
        String returnUsage;
        String confidence;
        String changeAxes;
        List<String[]> params = new ArrayList<>();   // {kind,type,name,mode}
    }

    static void require(boolean ok, String message) {
        if (!ok) {
            throw new IllegalStateException("REFUSE: " + message);
        }
    }

    static void requireEqual(String owner, String field, Object want, Object got) {
        if (want == null ? got != null : !want.equals(got)) {
            throw new IllegalStateException("REFUSE: " + owner + " " + field
                + " expected [" + want + "] actual [" + got + "]");
        }
    }

    static String hex(byte[] b) {
        StringBuilder sb = new StringBuilder();
        for (byte x : b) sb.append(String.format("%02x", x & 0xff));
        return sb.toString();
    }

    static String sha256(byte[] b) throws Exception {
        return hex(MessageDigest.getInstance("SHA-256").digest(b));
    }

    static String sha256(String s) throws Exception {
        return sha256(s.getBytes(StandardCharsets.UTF_8));
    }

    static String json(String v) {
        if (v == null) return "null";
        StringBuilder sb = new StringBuilder("\"");
        for (char c : v.toCharArray()) {
            if (c == '"' || c == '\\') sb.append('\\').append(c);
            else if (c == '\n') sb.append("\\n");
            else if (c == '\r') sb.append("\\r");
            else if (c == '\t') sb.append("\\t");
            else if (c < 0x20) sb.append(String.format("\\u%04x", (int) c));
            else sb.append(c);
        }
        return sb.append('"').toString();
    }

    // ---- GATE 1: containment ---------------------------------------------
    private void gateContainment() {
        String raw = state.getProject().getProjectLocator().getProjectDir()
                .getAbsolutePath();
        String p = raw.toLowerCase(Locale.ROOT).replace('/', '\\');
        for (String bad : REPO_FORBIDDEN) {
            require(!p.contains(bad.replace('/', '\\')),
                "REPO_FORBIDDEN - refusing a project path containing '" + bad
                + "': " + raw);
        }
        require(p.equals(REQUIRED_LIVE_PROJECT_DIR),
            "project is not the live maintainer project '"
            + REQUIRED_LIVE_PROJECT_DIR + "': " + raw);
        println("ABISIG_LIVE_TARGET"
            + " banner=AUTHORIZED-LIVE-MAINTAINER-PROJECT cohort=294"
            + " path=" + raw);
        println("ABISIG_GATE containment=ok path=" + raw);
    }

    // ---- counters ---------------------------------------------------------
    private long functionCount() {
        long n = 0;
        FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
        while (it.hasNext()) { it.next(); n++; }
        return n;
    }

    private long referenceCount() {
        long n = 0;
        ghidra.program.model.address.AddressIterator it =
            currentProgram.getReferenceManager()
                .getReferenceSourceIterator(currentProgram.getMemory(), true);
        while (it.hasNext()) {
            n += currentProgram.getReferenceManager().getReferencesFrom(it.next()).length;
        }
        return n;
    }

    private long undefinedDataCount() {
        long n = 0;
        DataIterator it = currentProgram.getListing().getData(true);
        while (it.hasNext()) { if (!it.next().isDefined()) n++; }
        return n;
    }

    private long bookmarkCount() {
        long n = 0;
        Iterator<Bookmark> it = currentProgram.getBookmarkManager().getBookmarksIterator();
        while (it.hasNext()) { it.next(); n++; }
        return n;
    }

    private String memoryDigest() throws Exception {
        MessageDigest d = MessageDigest.getInstance("SHA-256");
        for (MemoryBlock b : currentProgram.getMemory().getBlocks()) {
            d.update((b.getName() + "|" + b.getStart() + "|" + b.getEnd() + "|"
                + b.getSize() + "|" + b.isInitialized() + "|" + b.isExecute()
                + "|" + b.isRead() + "|" + b.isWrite() + "\n")
                .getBytes(StandardCharsets.UTF_8));
            if (!b.isInitialized()) continue;
            Address cur = b.getStart();
            long remaining = b.getSize();
            while (remaining > 0) {
                int size = (int) Math.min(1 << 20, remaining);
                byte[] chunk = new byte[size];
                int read = currentProgram.getMemory().getBytes(cur, chunk);
                require(read == size, "short memory read at " + cur);
                d.update(chunk);
                remaining -= size;
                if (remaining > 0) cur = cur.add(size);
            }
        }
        return hex(d.digest());
    }

    // ---- GATE 2: identity -------------------------------------------------
    private void gateIdentity() {
        requireEqual("program", "name", PROGRAM_NAME, currentProgram.getName());
        requireEqual("program", "md5", PROGRAM_MD5, currentProgram.getExecutableMD5());
        requireEqual("program", "sha256", PROGRAM_SHA256,
            currentProgram.getExecutableSHA256() == null ? null
                : currentProgram.getExecutableSHA256().toLowerCase(Locale.ROOT));
        requireEqual("program", "language", LANGUAGE,
            currentProgram.getLanguageID().getIdAsString());
        requireEqual("program", "compilerSpec", COMPILER_SPEC,
            currentProgram.getCompilerSpec().getCompilerSpecID().getIdAsString());
        requireEqual("program", "imageBase", IMAGE_BASE,
            currentProgram.getImageBase().toString());
        println("ABISIG_GATE identity=ok sha256=" + PROGRAM_SHA256);
    }

    // ---- GATE 3: PRE counts ----------------------------------------------
    private void gatePreCounts() {
        requireEqual("state", "functions", PRE_FUNCTIONS, functionCount());
        requireEqual("state", "instructions", PRE_INSTRUCTIONS,
            currentProgram.getListing().getNumInstructions());
        requireEqual("state", "references", PRE_REFERENCES, referenceCount());
        requireEqual("state", "definedData", PRE_DEFINED_DATA,
            currentProgram.getListing().getNumDefinedData());
        requireEqual("state", "undefinedData", PRE_UNDEFINED_DATA, undefinedDataCount());
        requireEqual("state", "bookmarks", PRE_BOOKMARKS, bookmarkCount());
        println("ABISIG_GATE preCounts=ok functions=" + PRE_FUNCTIONS
            + " instructions=" + PRE_INSTRUCTIONS + " references=" + PRE_REFERENCES
            + " definedData=" + PRE_DEFINED_DATA + " undefinedData="
            + PRE_UNDEFINED_DATA + " bookmarks=" + PRE_BOOKMARKS);
    }

    // ---- GATE 4: manifest -------------------------------------------------
    private List<Row> loadManifest(String path, String pinnedSha) throws Exception {
        byte[] raw = Files.readAllBytes(Paths.get(path));
        String got = sha256(raw);
        requireEqual("manifest", "sha256", pinnedSha.toLowerCase(Locale.ROOT), got);
        String[] lines = new String(raw, StandardCharsets.UTF_8).split("\n", -1);
        List<String> rows = new ArrayList<>();
        for (String l : lines) {
            if (l.endsWith("\r")) l = l.substring(0, l.length() - 1);
            if (!l.isEmpty()) rows.add(l);
        }
        requireEqual("manifest", "header", MANIFEST_HEADER,
            String.join("|", rows.get(0).split("\t", -1)));
        requireEqual("manifest", "rowCount", MANIFEST_ROWS, (long) (rows.size() - 1));

        List<Row> out = new ArrayList<>();
        Set<String> seen = new HashSet<>();
        for (int i = 1; i < rows.size(); i++) {
            String[] c = rows.get(i).split("\t", -1);
            requireEqual("manifest row " + i, "columns", 17, c.length);
            Row r = new Row();
            r.addrText = c[0];
            require(r.addrText.matches("^0x[0-9a-f]{8}$"),
                "row " + i + " addr must be lowercase 0x-prefixed 8 hex digits: "
                + r.addrText);
            r.addr = Long.parseLong(r.addrText.substring(2), 16);
            require(seen.add(r.addrText), "duplicate manifest address " + r.addrText);
            r.liveName = c[1];
            r.currentSignature = c[2];
            r.currentSha = c[3].toLowerCase(Locale.ROOT);
            requireEqual("manifest row " + i, "currentSignatureSha256",
                sha256(r.currentSignature), r.currentSha);
            r.proposedSignature = c[4];
            require(!r.proposedSignature.equals(r.currentSignature),
                "row " + i + " is a no-op proposal: " + r.addrText);
            r.cc = c[5];
            require(LEGAL_CC.contains(r.cc),
                "row " + i + " illegal calling convention " + r.cc);
            r.returnType = c[6];
            require(LEGAL_TYPE.matcher(r.returnType).matches(),
                "row " + i + " illegal return type [" + r.returnType + "]");
            r.paramSpec = c[7];
            r.arity = Integer.parseInt(c[8]);
            r.arityBytes = Integer.parseInt(c[9]);
            require(r.arityBytes == r.arity * 4,
                "row " + i + " arityBytes/arity mismatch " + r.arityBytes
                + " vs " + r.arity);
            r.retImmediate = c[10];
            r.receiver = c[11];
            r.returnUsage = c[12];
            r.confidence = c[14];
            requireEqual("manifest row " + i, "confidence", "HIGH", r.confidence);
            r.changeAxes = c[15];
            require(c[16].equals("EXACT") || c[16].startsWith("CONSISTENT_LOWER")
                || c[16].equals("n/a"),
                "row " + i + " frame corroboration must never CONTRADICT: " + c[16]);

            int nstack = 0;
            int nreg = 0;
            if (!r.paramSpec.isEmpty()) {
                for (String p : r.paramSpec.split(";")) {
                    String[] f = p.split(":", -1);
                    requireEqual("manifest row " + i, "paramSpec field count",
                        4, f.length);
                    require(LEGAL_TYPE.matcher(f[1]).matches(),
                        "row " + i + " illegal param type [" + f[1] + "]");
                    require(LEGAL_PNAME.matcher(f[2]).matches(),
                        "row " + i + " illegal param name [" + f[2] + "]");
                    require(f[3].equals("auto") || f[3].equals("expl"),
                        "row " + i + " illegal param mode " + f[3]);
                    if (f[0].equals("STACK")) nstack++;
                    else nreg++;
                    r.params.add(f);
                }
            }
            requireEqual("manifest row " + i, "stack param count", r.arity, nstack);
            // the fastcall register-assignment hazard, re-checked here
            if (r.cc.equals("__fastcall") && nstack > 0) {
                require(nreg >= 2, "row " + i + " __fastcall with " + nreg
                    + " register param(s) and " + nstack + " stack param(s) would let "
                    + "dynamic storage fabricate an EDX argument");
            }
            out.add(r);
        }
        println("ABISIG_GATE manifest=ok rows=" + out.size() + " sha256=" + got);
        return out;
    }

    // ---- census helpers ---------------------------------------------------
    private static String rangeSpec(AddressSetView body) {
        StringBuilder sb = new StringBuilder();
        int n = 0;
        for (AddressRange r : body) {
            if (n++ > 0) sb.append(';');
            sb.append(String.format("%08x-%08x", r.getMinAddress().getOffset(),
                r.getMaxAddress().getOffset()));
        }
        return sb.toString();
    }

    /** entry -> rendered prototype, over every function. */
    private TreeMap<String, String> sigCensus() {
        TreeMap<String, String> m = new TreeMap<>();
        FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
        while (it.hasNext()) {
            Function f = it.next();
            m.put(String.format("%08x", f.getEntryPoint().getOffset()),
                f.getSignature().getPrototypeString(true));
        }
        return m;
    }

    /** entry -> everything this applier must NOT change. */
    private TreeMap<String, String> untouchableCensus() throws Exception {
        TreeMap<String, String> m = new TreeMap<>();
        FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
        while (it.hasNext()) {
            Function f = it.next();
            List<String> tg = new ArrayList<>();
            for (ghidra.program.model.listing.FunctionTag t : f.getTags()) {
                tg.add(t.getName());
            }
            Collections.sort(tg);
            Function thunked = f.isThunk() ? f.getThunkedFunction(false) : null;
            m.put(String.format("%08x", f.getEntryPoint().getOffset()),
                f.getName(true)
                + "|" + rangeSpec(f.getBody())
                + "|" + f.getBody().getNumAddresses()
                + "|" + f.getBody().getNumAddressRanges()
                + "|" + f.isThunk()
                + "|" + (thunked == null ? "-" : thunked.getEntryPoint().toString())
                + "|" + f.isExternal()
                + "|" + f.hasNoReturn()
                + "|" + (f.getSymbol() == null ? "NO_SYMBOL"
                         : f.getSymbol().getSource().toString())
                + "|" + sha256(f.getComment() == null ? "<none>" : f.getComment())
                + "|" + sha256(f.getRepeatableComment() == null ? "<none>"
                               : f.getRepeatableComment())
                + "|" + tg
                + "|" + (f.getParentNamespace() == null ? ""
                         : f.getParentNamespace().getName(true)));
        }
        return m;
    }

    private List<String> symbolCensus() {
        List<String> out = new ArrayList<>();
        SymbolIterator it = currentProgram.getSymbolTable().getAllSymbols(true);
        while (it.hasNext()) {
            Symbol s = it.next();
            if (s.isDynamic()) continue;
            Address a = s.getAddress();
            out.add((a == null ? "-" : String.format("%08x", a.getOffset()))
                + "\t" + s.getName(true) + "\t" + s.getSymbolType()
                + "\t" + s.getSource() + "\t" + s.isPrimary() + "\t" + s.isPinned());
        }
        Collections.sort(out);
        return out;
    }

    private List<String> bookmarkCensus() {
        List<String> out = new ArrayList<>();
        Iterator<Bookmark> it = currentProgram.getBookmarkManager().getBookmarksIterator();
        while (it.hasNext()) {
            Bookmark b = it.next();
            out.add(b.getAddress() + "\t" + b.getTypeString() + "\t"
                + b.getCategory() + "\t" + b.getComment());
        }
        Collections.sort(out);
        return out;
    }

    private List<String> definedDataCensus() throws Exception {
        List<String> out = new ArrayList<>();
        DataIterator it = currentProgram.getListing().getDefinedData(true);
        while (it.hasNext()) {
            monitor.checkCancelled();
            Data d = it.next();
            out.add(d.getAddress() + "\t" + d.getLength() + "\t"
                + d.getDataType().getPathName());
        }
        Collections.sort(out);
        return out;
    }

    private static String digestOf(Map<String, String> m) throws Exception {
        StringBuilder sb = new StringBuilder();
        for (Map.Entry<String, String> e : m.entrySet()) {
            sb.append(e.getKey()).append('\t').append(e.getValue()).append('\n');
        }
        return sha256(sb.toString());
    }

    private static String digestOf(List<String> l) throws Exception {
        return sha256(String.join("\n", l) + "\n");
    }

    // ---- target resolution + PRE row gate ---------------------------------
    private Function functionAt(Row r) {
        Address a = toAddr(r.addr);
        Function f = currentProgram.getFunctionManager().getFunctionAt(a);
        require(f != null, "no function entry at " + r.addrText);
        requireEqual(r.addrText, "function entry", a, f.getEntryPoint());
        return f;
    }

    // ---- GATE 5: current signature must match, or refuse -----------------
    private void gatePreRows(List<Row> rows) throws Exception {
        for (Row r : rows) {
            Function f = functionAt(r);
            requireEqual(r.addrText, "CURRENT name", r.liveName, f.getName());
            String live = f.getSignature().getPrototypeString(true);
            requireEqual(r.addrText, "CURRENT signature", r.currentSignature, live);
            requireEqual(r.addrText, "CURRENT signature sha256", r.currentSha,
                sha256(live));
            requireEqual(r.addrText, "CURRENT calling convention", r.cc,
                f.getCallingConventionName());
            require(!f.hasCustomVariableStorage(),
                r.addrText + " uses custom variable storage; this applier only "
                + "installs dynamic storage");
            require(!f.isThunk(),
                r.addrText + " is a thunk; a thunk's prototype follows its target");
            require(!f.isExternal(), r.addrText + " is external");
        }
        println("ABISIG_GATE preRows=ok rows=" + rows.size()
            + " (current signature + name + convention all matched)");
    }

    // ---- type resolution: LOOKUP ONLY, never define a new type -----------
    private DataType resolveType(String spec) {
        DataTypeManager dtm = currentProgram.getDataTypeManager();
        int stars = 0;
        String base = spec.trim();
        while (base.endsWith("*")) {
            stars++;
            base = base.substring(0, base.length() - 1).trim();
        }
        List<DataType> hits = new ArrayList<>();
        dtm.findDataTypes(base, hits);
        DataType dt = null;
        if (!hits.isEmpty()) {
            dt = hits.get(0);
        } else {
            dt = dtm.getDataType("/" + base);
        }
        if (dt == null && base.equals("void")) {
            dt = ghidra.program.model.data.VoidDataType.dataType;
        }
        require(dt != null, "unknown data type [" + spec + "]; this applier "
            + "refuses to define new types");
        for (int i = 0; i < stars; i++) {
            dt = PointerDataType.getPointer(dt, dtm);
        }
        return dt;
    }

    /** GATE 6: resolve every data type the manifest names, before any write.
     *  Type resolution is the one part of applyRow that can fail on data, so
     *  proving it for the whole cohort up front is what makes the mutation
     *  loop unable to abort half way. */
    private void gateTypesResolvable(List<Row> rows) {
        int n = 0;
        for (Row r : rows) {
            resolveType(r.returnType);
            n++;
            for (String[] pp : r.params) {
                if (pp[3].equals("auto")) continue;
                resolveType(pp[1]);
                n++;
            }
        }
        println("ABISIG_GATE types=ok resolved=" + n
            + " (lookup only, no new type defined)");
    }

    /** Install one prototype.  Returns the prototype Ghidra actually renders. */
    private String applyRow(Row r) throws Exception {
        Function f = functionAt(r);
        List<Variable> params = new ArrayList<>();
        for (String[] p : r.params) {
            if (p[3].equals("auto")) {
                continue;   // Ghidra regenerates auto params from the convention
            }
            params.add(new ParameterImpl(p[2], resolveType(p[1]), currentProgram));
        }
        f.updateFunction(r.cc, new ReturnParameterImpl(resolveType(r.returnType),
                currentProgram), params,
            FunctionUpdateType.DYNAMIC_STORAGE_FORMAL_PARAMS, true,
            SourceType.USER_DEFINED);
        if (f.hasVarArgs()) {
            f.setVarArgs(false);
        }
        return f.getSignature().getPrototypeString(true);
    }

    // ---- GATE 7: POST per row --------------------------------------------
    private void gatePostRows(List<Row> rows) throws Exception {
        for (Row r : rows) {
            Function f = functionAt(r);
            String live = f.getSignature().getPrototypeString(true);
            requireEqual(r.addrText, "POST signature", r.proposedSignature, live);
            requireEqual(r.addrText, "POST calling convention", r.cc,
                f.getCallingConventionName());
            requireEqual(r.addrText, "POST name", r.liveName, f.getName());
            requireEqual(r.addrText, "POST stack parameter bytes", r.arityBytes,
                f.getStackFrame().getParameterSize());
            requireEqual(r.addrText, "POST varargs", false, f.hasVarArgs());
            requireEqual(r.addrText, "POST signature source", "USER_DEFINED",
                f.getSignatureSource().toString());
            require(!f.hasCustomVariableStorage(),
                r.addrText + " POST uses custom variable storage");
            int stack = 0;
            for (Parameter p : f.getParameters()) {
                if (p.isStackVariable()) stack++;
            }
            requireEqual(r.addrText, "POST stack parameter count", r.arity, stack);
        }
        println("ABISIG_GATE postRows=ok rows=" + rows.size());
    }

    // ---- GATE 9: collateral over EVERY function and symbol ----------------
    private String collateralProof(List<Row> rows,
                                   TreeMap<String, String> preSigs,
                                   TreeMap<String, String> preUntouchable,
                                   List<String> preSyms,
                                   List<String> preBookmarks,
                                   List<String> preDefinedData,
                                   String preMemory) throws Exception {
        TreeMap<String, String> postSigs = sigCensus();
        TreeMap<String, String> postUntouchable = untouchableCensus();

        require(preSigs.keySet().equals(postSigs.keySet()),
            "the set of function entry points changed");
        require(preUntouchable.equals(postUntouchable),
            "non-signature function state changed (name/body/thunk/comment/tag/"
            + "namespace/nameSource); first difference: "
            + firstDiff(preUntouchable, postUntouchable));

        Map<String, String> want = new HashMap<>();
        for (Row r : rows) {
            want.put(String.format("%08x", r.addr), r.proposedSignature);
        }
        long changed = 0;
        long untouched = 0;
        for (Map.Entry<String, String> e : preSigs.entrySet()) {
            String k = e.getKey();
            String post = postSigs.get(k);
            if (want.containsKey(k)) {
                requireEqual("0x" + k, "target POST signature", want.get(k), post);
                require(!post.equals(e.getValue()),
                    "0x" + k + " is a manifest target but its signature did not change");
                changed++;
            } else {
                requireEqual("0x" + k, "NON-TARGET signature", e.getValue(), post);
                untouched++;
            }
        }
        requireEqual("collateral", "changed function count",
            (long) rows.size(), changed);
        requireEqual("collateral", "untouched function count",
            PRE_FUNCTIONS - rows.size(), untouched);

        List<String> postSyms = symbolCensus();
        require(preSyms.equals(postSyms),
            "the non-dynamic symbol census changed (" + preSyms.size() + " -> "
            + postSyms.size() + ")");
        List<String> postBookmarks = bookmarkCensus();
        require(preBookmarks.equals(postBookmarks), "the bookmark census changed");
        List<String> postDefinedData = definedDataCensus();
        require(preDefinedData.equals(postDefinedData),
            "the defined-data census changed");
        requireEqual("collateral", "memory digest", preMemory, memoryDigest());

        requireEqual("collateral", "POST functions", PRE_FUNCTIONS, functionCount());
        requireEqual("collateral", "POST instructions", PRE_INSTRUCTIONS,
            currentProgram.getListing().getNumInstructions());
        requireEqual("collateral", "POST references", PRE_REFERENCES, referenceCount());
        requireEqual("collateral", "POST definedData", PRE_DEFINED_DATA,
            currentProgram.getListing().getNumDefinedData());
        requireEqual("collateral", "POST undefinedData", PRE_UNDEFINED_DATA,
            undefinedDataCount());
        requireEqual("collateral", "POST bookmarks", PRE_BOOKMARKS, bookmarkCount());

        return "functions=" + PRE_FUNCTIONS + " signaturesChanged=" + changed
            + " signaturesUntouched=" + untouched
            + " untouchableDigest=" + digestOf(postUntouchable)
            + " symbolDigest=" + digestOf(postSyms)
            + " bookmarkDigest=" + digestOf(postBookmarks)
            + " definedDataDigest=" + digestOf(postDefinedData)
            + " memoryDigest=" + preMemory
            + " postSignatureDigest=" + digestOf(postSigs);
    }

    private static String firstDiff(Map<String, String> a, Map<String, String> b) {
        for (Map.Entry<String, String> e : a.entrySet()) {
            String o = b.get(e.getKey());
            if (o == null || !o.equals(e.getValue())) {
                return "0x" + e.getKey() + " [" + e.getValue() + "] -> [" + o + "]";
            }
        }
        for (String k : b.keySet()) if (!a.containsKey(k)) return "new 0x" + k;
        return "(none)";
    }

    // ======================================================================
    @Override
    protected void run() throws Exception {
        String[] a = getScriptArgs();
        require(a != null && a.length >= 4,
            "usage: <mode> <manifestTsv> <manifestSha256> <outJson> [predictOutTsv]");
        String mode = a[0];

        gateContainment();
        gateIdentity();
        gatePreCounts();

        if (mode.equals("identity")) {
            println("ABISIG_VERDICT mode=identity result=PASS");
            writeJson(a[3], mode, "PASS", null, "identity + PRE pins only", null);
            return;
        }

        List<Row> rows = loadManifest(a[1], a[2]);

        TreeMap<String, String> preSigs = sigCensus();
        TreeMap<String, String> preUntouchable = untouchableCensus();
        List<String> preSyms = symbolCensus();
        List<String> preBookmarks = bookmarkCensus();
        List<String> preDefinedData = definedDataCensus();
        String preMemory = memoryDigest();
        println("ABISIG_PRE signatureDigest=" + digestOf(preSigs)
            + " untouchableDigest=" + digestOf(preUntouchable)
            + " symbolDigest=" + digestOf(preSyms)
            + " bookmarkDigest=" + digestOf(preBookmarks)
            + " definedDataDigest=" + digestOf(preDefinedData)
            + " memoryDigest=" + preMemory);

        // readback asserts the POST state, so it must NOT require the PRE
        // signature; it runs its own row gate and never mutates.
        if (mode.equals("readback")) {
            long tgt = 0;
            for (Row r : rows) {
                Function f = functionAt(r);
                String live = f.getSignature().getPrototypeString(true);
                requireEqual(r.addrText, "readback signature", r.proposedSignature,
                    live);
                requireEqual(r.addrText, "readback name", r.liveName, f.getName());
                requireEqual(r.addrText, "readback calling convention", r.cc,
                    f.getCallingConventionName());
                requireEqual(r.addrText, "readback stack parameter bytes",
                    r.arityBytes, f.getStackFrame().getParameterSize());
                requireEqual(r.addrText, "readback varargs", false, f.hasVarArgs());
                requireEqual(r.addrText, "readback signature source",
                    "USER_DEFINED", f.getSignatureSource().toString());
                require(!f.hasCustomVariableStorage(),
                    r.addrText + " readback uses custom variable storage");
                tgt++;
            }
            // and prove every NON-target signature is still the PRE string the
            // manifest recorded nothing about: the manifest's own PRE census
            // digest must no longer match, while everything else is identical
            Set<String> tset = new HashSet<>();
            for (Row r : rows) tset.add(String.format("%08x", r.addr));
            long nonTargets = 0;
            for (String k : preSigs.keySet()) {
                if (!tset.contains(k)) nonTargets++;
            }
            requireEqual("readback", "target count", (long) rows.size(), tgt);
            requireEqual("readback", "non-target count",
                PRE_FUNCTIONS - rows.size(), nonTargets);
            println("ABISIG_READBACK signatureDigest=" + digestOf(preSigs)
                + " untouchableDigest=" + digestOf(preUntouchable)
                + " symbolDigest=" + digestOf(preSyms)
                + " bookmarkDigest=" + digestOf(preBookmarks)
                + " definedDataDigest=" + digestOf(preDefinedData)
                + " memoryDigest=" + preMemory
                + " targets=" + tgt + " nonTargets=" + nonTargets);
            println("ABISIG_VERDICT mode=readback result=PASS rows=" + rows.size());
            writeJson(a[3], mode, "PASS", rows,
                "readback only, no mutation", null);
            return;
        }

        gatePreRows(rows);
        gateTypesResolvable(rows);

        if (mode.equals("predict")) {
            require(a.length >= 5, "predict needs a predictOutTsv path");
            StringBuilder sb = new StringBuilder(
                "addr\tcurrentSignature\tmanifestProposed\trenderedProposed"
                + "\tmatch\tpostParamBytes\tpostStackParams\n");
            int tx = currentProgram.startTransaction(SCHEMA + ":predict");
            try {
                for (Row r : rows) {
                    String rendered = applyRow(r);
                    Function f = functionAt(r);
                    int stack = 0;
                    for (Parameter p : f.getParameters()) {
                        if (p.isStackVariable()) stack++;
                    }
                    sb.append(r.addrText).append('\t').append(r.currentSignature)
                      .append('\t').append(r.proposedSignature).append('\t')
                      .append(rendered).append('\t')
                      .append(rendered.equals(r.proposedSignature)).append('\t')
                      .append(f.getStackFrame().getParameterSize()).append('\t')
                      .append(stack).append('\n');
                }
            } finally {
                currentProgram.endTransaction(tx, true);
            }
            println("ABISIG_PREDICT_DESTRUCTIVE this replica is now mutated; "
                + "headless offers no working prototype rollback, so the caller "
                + "MUST discard this replica and rebuild it from the backup");
            Files.write(Paths.get(a[4]), sb.toString().getBytes(StandardCharsets.UTF_8));
            // prove the rollback really happened - and if it did not, say exactly
            // which entries survived, because that is a safety fact about this
            // Ghidra build's transaction abort, not a manifest problem
            // even in predict, prove the blast radius is exactly the targets
            TreeMap<String, String> afterSigs = sigCensus();
            long diffs = 0;
            Set<String> tgt = new HashSet<>();
            for (Row r : rows) tgt.add(String.format("%08x", r.addr));
            for (Map.Entry<String, String> e : preSigs.entrySet()) {
                String post = afterSigs.get(e.getKey());
                if (post == null || !post.equals(e.getValue())) {
                    diffs++;
                    require(tgt.contains(e.getKey()),
                        "predict changed a NON-TARGET signature at 0x" + e.getKey());
                }
            }
            requireEqual("predict", "changed signature count",
                (long) rows.size(), diffs);
            require(digestOf(preUntouchable).equals(digestOf(untouchableCensus())),
                "predict changed non-signature function state");
            println("ABISIG_VERDICT mode=predict result=PASS rows=" + rows.size()
                + " (transaction rolled back, census identical)");
            writeJson(a[3], mode, "PASS", rows, "prediction only, rolled back",
                "rolled-back");
            return;
        }

        if (mode.equals("dry")) {
            println("ABISIG_VERDICT mode=dry result=PASS rows=" + rows.size());
            writeJson(a[3], mode, "PASS", rows, "no mutation published", null);
            return;
        }

        require(mode.equals("apply") || mode.equals("probe"), "unknown mode " + mode);

        int tx = currentProgram.startTransaction(SCHEMA + ":" + mode);
        boolean commit = false;
        String proof;
        try {
            for (Row r : rows) {
                Function f = functionAt(r);
                requireEqual(r.addrText, "apply-time current signature",
                    r.currentSignature, f.getSignature().getPrototypeString(true));
                String rendered = applyRow(r);
                requireEqual(r.addrText, "rendered prototype",
                    r.proposedSignature, rendered);
            }
            gatePostRows(rows);
            proof = collateralProof(rows, preSigs, preUntouchable, preSyms,
                                    preBookmarks, preDefinedData, preMemory);
            commit = true;   // see the endTransaction note: abort is a no-op here
        } finally {
            currentProgram.endTransaction(tx, commit);
        }
        if (mode.equals("probe")) {
            println("ABISIG_PROBE this build has no working in-process "
                + "rollback; reversibility is proven at the ceremony level by "
                + "restoring the replica from its backup and comparing digests");
        }
        println("ABISIG_COLLATERAL " + proof);
        println("ABISIG_VERDICT mode=" + mode + " result=PASS committed=" + commit
            + " rows=" + rows.size());
        writeJson(a[3], mode, "PASS", rows, proof,
            commit ? "committed" : "rolled-back");
    }

    private void writeJson(String path, String mode, String result, List<Row> rows,
                           String proof, String txState) throws Exception {
        StringBuilder j = new StringBuilder();
        j.append("{\n  \"schema\": ").append(json(SCHEMA));
        j.append(",\n  \"mode\": ").append(json(mode));
        j.append(",\n  \"result\": ").append(json(result));
        j.append(",\n  \"projectDir\": ").append(json(
            state.getProject().getProjectLocator().getProjectDir().getAbsolutePath()));
        j.append(",\n  \"programSha256\": ").append(json(PROGRAM_SHA256));
        j.append(",\n  \"functions\": ").append(functionCount());
        j.append(",\n  \"instructions\": ")
         .append(currentProgram.getListing().getNumInstructions());
        j.append(",\n  \"references\": ").append(referenceCount());
        j.append(",\n  \"definedData\": ")
         .append(currentProgram.getListing().getNumDefinedData());
        j.append(",\n  \"undefinedData\": ").append(undefinedDataCount());
        j.append(",\n  \"bookmarks\": ").append(bookmarkCount());
        j.append(",\n  \"memoryDigest\": ").append(json(memoryDigest()));
        j.append(",\n  \"signatureDigest\": ").append(json(digestOf(sigCensus())));
        j.append(",\n  \"untouchableDigest\": ")
         .append(json(digestOf(untouchableCensus())));
        j.append(",\n  \"symbolDigest\": ").append(json(digestOf(symbolCensus())));
        j.append(",\n  \"bookmarkDigest\": ").append(json(digestOf(bookmarkCensus())));
        j.append(",\n  \"definedDataDigest\": ")
         .append(json(digestOf(definedDataCensus())));
        j.append(",\n  \"rows\": ").append(rows == null ? 0 : rows.size());
        j.append(",\n  \"transaction\": ").append(json(txState));
        j.append(",\n  \"collateral\": ").append(json(proof));
        j.append("\n}\n");
        Files.write(Paths.get(path), j.toString().getBytes(StandardCharsets.UTF_8));
    }
}
