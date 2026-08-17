//@category Symbol
//
// AUTHORIZED LIVE name-only applier for the re-pinned 160-row name cohort.
//
// This is GhidraApplyNameCohort160 WITH EXACTLY ONE GATE INVERTED.  That
// script is the rehearsal instrument and stays LIVE_FORBIDDEN forever; V2 is
// its live-capable twin and differs from it only in the containment gate:
// where the rehearsal applier requires a "name-cohort" lane segment plus the
// authoring session's scratch GUID and refuses any path under Ghidra\Projects,
// V2 REQUIRES the live maintainer project directory by exact match and refuses
// everything else, including the tracked repository snapshot.  Every other
// gate, pin, verb, census and refusal message is carried over verbatim, and
// tools/ghidra_name_cohort160_mutator_tests.py asserts that line by line.
//
// Use of this script is authorized ONLY for the 160-row cohort pinned below,
// under the maintainer's delegated per-cohort grant of 2026-08-16 and the GO
// recommendation recorded in developer_state as
// _RECOMMENDATION_20260817_NAME_COHORT_LIVE_APPLY, which requires the five
// refuted rows to stay dropped.  That grant is per-cohort and is NOT standing
// authorization for Ghidra mutation.
//
// Scope: setName, and nothing else.  It never touches a function body, a
// boundary, a signature, a calling convention, a reference, a comment, a tag,
// a data unit, a bookmark, or a program byte.  Every one of those is proven
// unchanged over ALL functions and ALL non-dynamic symbols, not just targets.
//
// Modes (arg0):
//   identity  - program identity + PRE state pins only, no manifest needed
//   dry       - full PRE validation of every gate; publishes no mutation
//   apply     - dry, then rename, then full POST validation + collateral proof
//   readback  - require the exact POST state with no mutation
//   probe     - apply then force a rollback, proving the transaction is atomic
//
// Args: <mode> <manifestTsv> <manifestSha256> <outJson> [censusOutTsv]
//
// Refusal policy: any failed gate throws before any write is published.  In
// 'apply' the whole cohort runs inside one transaction; a late gate failure
// aborts it, so the database is never left half-renamed.
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressIterator;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Bookmark;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.DataIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;
import ghidra.program.model.symbol.SymbolTable;

import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.util.ArrayList;
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

public class GhidraApplyNameCohort160V2 extends GhidraScript {

    static final String SCHEMA = "bea.ghidra.name-cohort-repin.live.v2";

    // ---- exact program identity (db.18620, 2026-08-17) -------------------
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

    // digests of the read-only inventory this manifest was pinned against
    static final String PRE_FUNCTION_NAME_DIGEST =
        "1ea6683b48d7086ed4a214bbb74357d7ff964ebdc2c995f8a9d414626822b9c1";
    static final String PRE_FUNCTION_BODY_DIGEST =
        "c066b5d6093342c507b816f9823680cbef032f74ae12ec95697ccbca789a187f";

    static final long MANIFEST_ROWS = 160L;

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

    // deliberately narrow: no ':', '.', '@' or whitespace, so a name can never
    // be parsed as a namespace path or a mangled token
    static final Pattern LEGAL_NAME =
        Pattern.compile("^[A-Za-z_][A-Za-z0-9_]{0,190}$");

    // ======================================================================

    static class Row {
        String addrText;
        long addr;
        String provenance;
        String liveKind;      // FUNCTION | SYMBOL:Label
        String currentName;
        String proposedName;
        String tier;
    }

    /** Everything about one function that this applier must NOT change. */
    static class FnShape {
        String rangeSpec;
        long bodyBytes;
        int nRanges;
        String signatureShape;   // prototype with the own-name token masked
        String callingConvention;
        boolean thunk;
        String namespace;

        String key() {
            return rangeSpec + "|" + bodyBytes + "|" + nRanges + "|"
                + signatureShape + "|" + callingConvention + "|" + thunk
                + "|" + namespace;
        }
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

    // ---- containment gate -------------------------------------------------
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
        println("NAMECOHORT_LIVE_TARGET"
            + " banner=AUTHORIZED-LIVE-MAINTAINER-PROJECT cohort=160"
            + " path=" + raw);
        println("NAMECOHORT_GATE containment=ok path=" + raw);
    }

    // ---- program identity + PRE counts ------------------------------------
    private long functionCount() {
        long n = 0;
        FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
        while (it.hasNext()) { it.next(); n++; }
        return n;
    }

    private long referenceCount() {
        long n = 0;
        AddressIterator it = currentProgram.getReferenceManager()
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

    private void gateIdentity() throws Exception {
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
        println("NAMECOHORT_GATE identity=ok sha256=" + PROGRAM_SHA256);
    }

    private void gatePreCounts() {
        requireEqual("state", "functions", PRE_FUNCTIONS, functionCount());
        requireEqual("state", "instructions", PRE_INSTRUCTIONS,
            currentProgram.getListing().getNumInstructions());
        requireEqual("state", "references", PRE_REFERENCES, referenceCount());
        requireEqual("state", "definedData", PRE_DEFINED_DATA,
            currentProgram.getListing().getNumDefinedData());
        requireEqual("state", "undefinedData", PRE_UNDEFINED_DATA, undefinedDataCount());
        requireEqual("state", "bookmarks", PRE_BOOKMARKS, bookmarkCount());
        println("NAMECOHORT_GATE preCounts=ok functions=" + PRE_FUNCTIONS
            + " instructions=" + PRE_INSTRUCTIONS);
    }

    // ---- manifest ---------------------------------------------------------
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
        String[] head = rows.get(0).split("\t", -1);
        requireEqual("manifest", "header",
            "addr|provenance|liveKind|currentNameLive|proposedName|tier|"
            + "anchorKind|anchorEvidence|reason", String.join("|", head));
        requireEqual("manifest", "rowCount", MANIFEST_ROWS, (long) (rows.size() - 1));

        List<Row> out = new ArrayList<>();
        Set<String> seenAddr = new HashSet<>();
        Set<String> seenProposed = new HashSet<>();
        Set<String> seenCurrent = new HashSet<>();
        for (int i = 1; i < rows.size(); i++) {
            String[] c = rows.get(i).split("\t", -1);
            requireEqual("manifest row " + i, "columns", 9, c.length);
            Row r = new Row();
            r.addrText = c[0];
            require(r.addrText.startsWith("0x"), "row " + i + " addr must be 0x-prefixed");
            r.addr = Long.parseLong(r.addrText.substring(2), 16);
            r.provenance = c[1];
            require(r.provenance.equals("PROMOTE") || r.provenance.equals("DEMOTE")
                || r.provenance.equals("SLOTFIX"),
                "row " + i + " bad provenance " + r.provenance);
            r.liveKind = c[2];
            require(r.liveKind.equals("FUNCTION") || r.liveKind.equals("SYMBOL:Label"),
                "row " + i + " bad liveKind " + r.liveKind);
            r.currentName = c[3];
            r.proposedName = c[4];
            r.tier = c[5];
            require(LEGAL_NAME.matcher(r.proposedName).matches(),
                "row " + i + " illegal proposed name: " + r.proposedName);
            require(!r.proposedName.equals(r.currentName),
                "row " + i + " is a no-op rename: " + r.proposedName);
            require(seenAddr.add(r.addrText), "duplicate manifest address " + r.addrText);
            require(seenProposed.add(r.proposedName),
                "duplicate proposed name " + r.proposedName);
            require(seenCurrent.add(r.currentName),
                "duplicate current name " + r.currentName);
            out.add(r);
        }
        // no rename cycles: a proposal may not be another row's current name
        for (Row r : out) {
            require(!seenCurrent.contains(r.proposedName),
                "rename cycle: '" + r.proposedName + "' is another row's current "
                + "name; this applier refuses order-dependent swaps");
        }
        println("NAMECOHORT_GATE manifest=ok rows=" + out.size() + " sha256=" + got);
        return out;
    }

    // ---- census -----------------------------------------------------------
    private String signatureShape(Function f) {
        String proto = f.getSignature().getPrototypeString(true);
        String nm = f.getName();
        return nm.isEmpty() ? proto : proto.replace(nm, "NAME");
    }

    private FnShape shapeOf(Function f) {
        FnShape s = new FnShape();
        AddressSetView body = f.getBody();
        StringBuilder spec = new StringBuilder();
        int n = 0;
        long total = 0;
        for (AddressRange r : body) {
            if (n > 0) spec.append(';');
            spec.append(String.format("%08x-%08x", r.getMinAddress().getOffset(),
                r.getMaxAddress().getOffset()));
            total += r.getLength();
            n++;
        }
        s.rangeSpec = spec.toString();
        s.bodyBytes = total;
        s.nRanges = n;
        s.signatureShape = signatureShape(f);
        s.callingConvention = f.getCallingConventionName();
        s.thunk = f.isThunk();
        s.namespace = f.getParentNamespace() == null ? ""
            : f.getParentNamespace().getName(true);
        return s;
    }

    /** entry -> name, over every function. */
    private TreeMap<String, String> nameCensus() {
        TreeMap<String, String> m = new TreeMap<>();
        FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
        while (it.hasNext()) {
            Function f = it.next();
            m.put(String.format("%08x", f.getEntryPoint().getOffset()), f.getName());
        }
        return m;
    }

    /** entry -> everything-but-the-name, over every function. */
    private TreeMap<String, String> shapeCensus() {
        TreeMap<String, String> m = new TreeMap<>();
        FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
        while (it.hasNext()) {
            Function f = it.next();
            m.put(String.format("%08x", f.getEntryPoint().getOffset()),
                shapeOf(f).key());
        }
        return m;
    }

    /** entry -> comment + repeatable comment + tag set, over every function.
     *  This applier changes none of them, and proves it. */
    private TreeMap<String, String> metaCensus() throws Exception {
        TreeMap<String, String> m = new TreeMap<>();
        FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
        while (it.hasNext()) {
            Function f = it.next();
            List<String> tg = new ArrayList<>();
            for (ghidra.program.model.listing.FunctionTag t : f.getTags()) {
                tg.add(t.getName());
            }
            Collections.sort(tg);
            String c = f.getComment() == null ? "<none>" : f.getComment();
            String rc = f.getRepeatableComment() == null ? "<none>"
                                                         : f.getRepeatableComment();
            m.put(String.format("%08x", f.getEntryPoint().getOffset()),
                sha256(c) + "|" + sha256(rc) + "|" + tg);
        }
        return m;
    }

    /** address\tname\ttype\tnamespace\tsource for every non-dynamic symbol. */
    private List<String> symbolCensus() {
        List<String> out = new ArrayList<>();
        SymbolIterator it = currentProgram.getSymbolTable().getAllSymbols(true);
        while (it.hasNext()) {
            Symbol s = it.next();
            if (s.isDynamic()) continue;
            Address a = s.getAddress();
            out.add((a == null ? "-" : String.format("%08x", a.getOffset()))
                + "\t" + s.getName() + "\t" + s.getSymbolType()
                + "\t" + (s.getParentNamespace() == null ? ""
                    : s.getParentNamespace().getName(true))
                + "\t" + s.getSource() + "\t" + s.isPrimary());
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

    // ---- target resolution + collision ------------------------------------
    private Function functionAt(Row r) {
        Address a = toAddr(r.addr);
        Function f = currentProgram.getFunctionManager().getFunctionAt(a);
        require(f != null, "no function entry at " + r.addrText);
        requireEqual(r.addrText, "function entry", a, f.getEntryPoint());
        return f;
    }

    private Symbol labelAt(Row r) {
        Address a = toAddr(r.addr);
        require(currentProgram.getFunctionManager().getFunctionAt(a) == null,
            r.addrText + " is a function, but the manifest says SYMBOL:Label");
        Symbol s = currentProgram.getSymbolTable().getPrimarySymbol(a);
        require(s != null, "no primary symbol at " + r.addrText);
        require(!s.isDynamic(), r.addrText + " primary symbol is dynamic");
        requireEqual(r.addrText, "symbolType", "Label", s.getSymbolType().toString());
        return s;
    }

    private String currentNameOf(Row r) {
        return r.liveKind.equals("FUNCTION") ? functionAt(r).getName()
                                             : labelAt(r).getName();
    }

    /** every non-dynamic symbol name in the database -> its addresses. */
    private Map<String, List<String>> nameIndex() {
        Map<String, List<String>> idx = new HashMap<>();
        SymbolIterator it = currentProgram.getSymbolTable().getAllSymbols(true);
        while (it.hasNext()) {
            Symbol s = it.next();
            if (s.isDynamic()) continue;
            Address a = s.getAddress();
            idx.computeIfAbsent(s.getName(), k -> new ArrayList<>())
               .add(a == null ? "-" : String.format("%08x", a.getOffset()));
        }
        return idx;
    }

    /** PRE holders of each row's current name, minus the target itself.  This
     *  database legitimately carries duplicate names, so the POST assertion is
     *  "the target no longer holds it and every OTHER holder is untouched",
     *  not "the name vanished". */
    private Map<String, List<String>> preOtherHolders = new HashMap<>();

    private void gatePre(List<Row> rows) {
        Map<String, List<String>> idx = nameIndex();
        preOtherHolders.clear();
        int ambiguous = 0;
        for (Row r : rows) {
            String self = r.addrText.substring(2);
            String live = currentNameOf(r);
            // the decisive staleness gate
            requireEqual(r.addrText, "CURRENT name", r.currentName, live);

            List<String> holders = idx.get(r.currentName);
            require(holders != null && holders.contains(self),
                "PRE census: '" + r.currentName + "' is not held at "
                + r.addrText + " (holders " + holders + ")");
            List<String> others = new ArrayList<>(holders);
            others.remove(self);
            Collections.sort(others);
            if (!others.isEmpty()) ambiguous++;
            preOtherHolders.put(r.addrText, others);

            // collision: the proposed name may not exist anywhere else
            List<String> hits = idx.get(r.proposedName);
            if (hits != null) {
                for (String h : hits) {
                    require(h.equals(self),
                        "collision: proposed name '" + r.proposedName
                        + "' for " + r.addrText + " already exists at 0x" + h);
                }
            }
        }
        println("NAMECOHORT_GATE preRows=ok rows=" + rows.size()
            + " (current-name match + collision-free) rowsWhoseCurrentNameIs"
            + "AlsoHeldElsewhere=" + ambiguous);
    }

    private void gatePost(List<Row> rows) {
        Map<String, List<String>> idx = nameIndex();
        for (Row r : rows) {
            String self = r.addrText.substring(2);
            requireEqual(r.addrText, "POST name", r.proposedName, currentNameOf(r));

            List<String> hits = idx.get(r.proposedName);
            require(hits != null && hits.size() == 1 && hits.get(0).equals(self),
                "POST census for '" + r.proposedName + "' is not exactly one "
                + "symbol at " + r.addrText + " (got " + hits + ")");

            List<String> old = idx.get(r.currentName);
            List<String> stillThere = old == null ? new ArrayList<>()
                                                  : new ArrayList<>(old);
            Collections.sort(stillThere);
            require(!stillThere.contains(self),
                "POST: the PRE name '" + r.currentName + "' is still held at "
                + r.addrText);
            List<String> expected = preOtherHolders.get(r.addrText);
            require(expected != null && expected.equals(stillThere),
                "POST: other holders of the PRE name '" + r.currentName
                + "' changed: expected " + expected + " actual " + stillThere);
        }
        println("NAMECOHORT_GATE postRows=ok rows=" + rows.size());
    }

    // ---- collateral proof --------------------------------------------------
    private String collateralProof(List<Row> rows,
                                   TreeMap<String, String> preNames,
                                   TreeMap<String, String> preShapes,
                                   TreeMap<String, String> preMeta,
                                   List<String> preSyms,
                                   String preMemory) throws Exception {
        TreeMap<String, String> postNames = nameCensus();
        TreeMap<String, String> postShapes = shapeCensus();
        TreeMap<String, String> postMeta = metaCensus();
        List<String> postSyms = symbolCensus();

        require(preNames.keySet().equals(postNames.keySet()),
            "the set of function entry points changed");

        Map<String, String> want = new HashMap<>();
        Set<String> targetEntries = new HashSet<>();
        for (Row r : rows) {
            if (r.liveKind.equals("FUNCTION")) {
                String k = String.format("%08x", r.addr);
                want.put(k, r.proposedName);
                targetEntries.add(k);
            }
        }

        List<String> drift = new ArrayList<>();
        int changed = 0;
        for (String k : preNames.keySet()) {
            String a = preNames.get(k), b = postNames.get(k);
            boolean isTarget = targetEntries.contains(k);
            if (!a.equals(b)) {
                changed++;
                if (!isTarget) {
                    drift.add("NON-TARGET NAME CHANGED " + k + " '" + a + "' -> '" + b + "'");
                } else if (!b.equals(want.get(k))) {
                    drift.add("TARGET NAME WRONG " + k + " '" + b + "' want '"
                        + want.get(k) + "'");
                }
            } else if (isTarget) {
                drift.add("TARGET NAME DID NOT CHANGE " + k + " '" + a + "'");
            }
            // the shape must be identical for EVERY function, target or not
            if (!preShapes.get(k).equals(postShapes.get(k))) {
                drift.add("SHAPE CHANGED " + k + " '" + preShapes.get(k)
                    + "' -> '" + postShapes.get(k) + "'");
            }
            // comment / repeatable comment / tag set must be untouched for
            // EVERY function, target rows included
            if (!preMeta.get(k).equals(postMeta.get(k))) {
                drift.add("COMMENT-OR-TAG CHANGED " + k + " '" + preMeta.get(k)
                    + "' -> '" + postMeta.get(k) + "'");
            }
        }
        requireEqual("collateral", "changed function names",
            (long) targetEntries.size(), (long) changed);

        // symbol-table delta must be exactly the renames
        Set<String> preSet = new HashSet<>(preSyms);
        Set<String> postSet = new HashSet<>(postSyms);
        Set<String> added = new HashSet<>(postSet);
        added.removeAll(preSet);
        Set<String> removed = new HashSet<>(preSet);
        removed.removeAll(postSet);
        requireEqual("collateral", "symbols added", (long) rows.size(), (long) added.size());
        requireEqual("collateral", "symbols removed", (long) rows.size(), (long) removed.size());
        requireEqual("collateral", "non-dynamic symbol count",
            (long) preSyms.size(), (long) postSyms.size());
        for (String s : added) {
            String[] c = s.split("\t", -1);
            boolean matched = false;
            for (Row r : rows) {
                if (c[0].equals(String.format("%08x", r.addr))
                        && c[1].equals(r.proposedName)) { matched = true; break; }
            }
            if (!matched) drift.add("UNEXPECTED ADDED SYMBOL " + s);
        }
        for (String s : removed) {
            String[] c = s.split("\t", -1);
            boolean matched = false;
            for (Row r : rows) {
                if (c[0].equals(String.format("%08x", r.addr))
                        && c[1].equals(r.currentName)) { matched = true; break; }
            }
            if (!matched) drift.add("UNEXPECTED REMOVED SYMBOL " + s);
        }

        // structural counts and raw bytes
        requireEqual("collateral", "functions", PRE_FUNCTIONS, functionCount());
        requireEqual("collateral", "instructions", PRE_INSTRUCTIONS,
            currentProgram.getListing().getNumInstructions());
        requireEqual("collateral", "references", PRE_REFERENCES, referenceCount());
        requireEqual("collateral", "definedData", PRE_DEFINED_DATA,
            currentProgram.getListing().getNumDefinedData());
        requireEqual("collateral", "undefinedData", PRE_UNDEFINED_DATA,
            undefinedDataCount());
        requireEqual("collateral", "bookmarks", PRE_BOOKMARKS, bookmarkCount());
        requireEqual("collateral", "memory digest", preMemory, memoryDigest());
        requireEqual("collateral", "function shape digest",
            digestOf(preShapes), digestOf(postShapes));
        requireEqual("collateral", "function comment/tag digest",
            digestOf(preMeta), digestOf(postMeta));

        require(drift.isEmpty(), "collateral drift: " + drift);

        StringBuilder sb = new StringBuilder();
        sb.append("functionsExamined=").append(preNames.size())
          .append(" namesChanged=").append(changed)
          .append(" targetsExpected=").append(targetEntries.size())
          .append(" shapeDigestPre=").append(digestOf(preShapes))
          .append(" shapeDigestPost=").append(digestOf(postShapes))
          .append(" metaDigestPre=").append(digestOf(preMeta))
          .append(" metaDigestPost=").append(digestOf(postMeta))
          .append(" symbolsPre=").append(preSyms.size())
          .append(" symbolsPost=").append(postSyms.size())
          .append(" symbolsAdded=").append(added.size())
          .append(" symbolsRemoved=").append(removed.size())
          .append(" memoryDigest=").append(preMemory)
          .append(" nameDigestPre=").append(digestOf(preNames))
          .append(" nameDigestPost=").append(digestOf(postNames));
        return sb.toString();
    }

    // ======================================================================
    @Override
    protected void run() throws Exception {
        String[] a = getScriptArgs();
        require(a.length >= 1, "usage: <mode> <manifest> <manifestSha256> <outJson>");
        String mode = a[0];

        gateContainment();
        gateIdentity();
        gatePreCounts();

        if (mode.equals("identity")) {
            println("NAMECOHORT_VERDICT mode=identity result=PASS");
            if (a.length >= 4) writeJson(a[3], mode, "PASS", null, null, null);
            return;
        }

        require(a.length >= 4, "usage: <mode> <manifest> <manifestSha256> <outJson>");
        List<Row> rows = loadManifest(a[1], a[2]);

        // ---- readback is a POST-state assertion and must NOT run the PRE
        //      gates; it verifies the applied database in a fresh process.
        if (mode.equals("readback")) {
            Map<String, List<String>> idx = nameIndex();
            for (Row r : rows) {
                String self = r.addrText.substring(2);
                requireEqual(r.addrText, "POST name", r.proposedName,
                    currentNameOf(r));
                List<String> hits = idx.get(r.proposedName);
                require(hits != null && hits.size() == 1
                        && hits.get(0).equals(self),
                    "POST census for '" + r.proposedName + "' is not exactly "
                    + "one symbol at " + r.addrText + " (got " + hits + ")");
                List<String> old = idx.get(r.currentName);
                require(old == null || !old.contains(self),
                    "POST: the PRE name '" + r.currentName + "' is still held "
                    + "at " + r.addrText);
            }
            println("NAMECOHORT_GATE readbackRows=ok rows=" + rows.size());
            println("NAMECOHORT_VERDICT mode=readback result=PASS rows="
                + rows.size());
            writeJson(a[3], mode, "PASS", rows, "POST verified without mutation",
                null);
            return;
        }

        TreeMap<String, String> preNames = nameCensus();
        TreeMap<String, String> preShapes = shapeCensus();
        TreeMap<String, String> preMeta = metaCensus();
        List<String> preSyms = symbolCensus();
        String preMemory = memoryDigest();
        // any name drift ANYWHERE in the database - target or not - refuses
        requireEqual("state", "function NAME digest", PRE_FUNCTION_NAME_DIGEST,
            digestOf(nameDigestForm(preNames)));

        gatePre(rows);

        if (a.length >= 5) {
            StringBuilder sb = new StringBuilder("entry\tpreName\n");
            for (Map.Entry<String, String> e : preNames.entrySet()) {
                sb.append(e.getKey()).append('\t').append(e.getValue())
                  .append('\n');
            }
            Files.write(Paths.get(a[4]), sb.toString().getBytes(StandardCharsets.UTF_8));
        }

        if (mode.equals("dry")) {
            println("NAMECOHORT_VERDICT mode=dry result=PASS rows=" + rows.size());
            writeJson(a[3], mode, "PASS", rows, "no mutation published", null);
            return;
        }

        require(mode.equals("apply") || mode.equals("probe"),
            "unknown mode " + mode);

        int tx = currentProgram.startTransaction(SCHEMA + ":" + mode);
        boolean commit = false;
        String proof;
        try {
            for (Row r : rows) {
                if (r.liveKind.equals("FUNCTION")) {
                    Function f = functionAt(r);
                    requireEqual(r.addrText, "apply-time current name",
                        r.currentName, f.getName());
                    f.setName(r.proposedName, SourceType.USER_DEFINED);
                } else {
                    Symbol s = labelAt(r);
                    requireEqual(r.addrText, "apply-time current name",
                        r.currentName, s.getName());
                    s.setName(r.proposedName, SourceType.USER_DEFINED);
                }
            }
            gatePost(rows);
            proof = collateralProof(rows, preNames, preShapes, preMeta,
                                    preSyms, preMemory);
            commit = mode.equals("apply");
        } finally {
            currentProgram.endTransaction(tx, commit);
        }
        println("NAMECOHORT_COLLATERAL " + proof);
        println("NAMECOHORT_VERDICT mode=" + mode + " result=PASS committed="
            + commit + " rows=" + rows.size());
        writeJson(a[3], mode, "PASS", rows, proof, commit ? "committed" : "rolled-back");
    }

    /** the inventory's name digest is entry\tfullName; rebuild that exact form. */
    private TreeMap<String, String> nameDigestForm(TreeMap<String, String> ignored) {
        TreeMap<String, String> m = new TreeMap<>();
        FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
        while (it.hasNext()) {
            Function f = it.next();
            m.put(String.format("%08x", f.getEntryPoint().getOffset()), f.getName(true));
        }
        return m;
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
        j.append(",\n  \"functionNameDigest\": ")
         .append(json(digestOf(nameDigestForm(null))));
        j.append(",\n  \"functionShapeDigest\": ").append(json(digestOf(shapeCensus())));
        j.append(",\n  \"functionMetaDigest\": ").append(json(digestOf(metaCensus())));
        j.append(",\n  \"symbolCensusDigest\": ").append(json(digestOf(symbolCensus())));
        j.append(",\n  \"rows\": ").append(rows == null ? 0 : rows.size());
        j.append(",\n  \"transaction\": ").append(json(txState));
        j.append(",\n  \"collateral\": ").append(json(proof));
        j.append("\n}\n");
        Files.write(Paths.get(path), j.toString().getBytes(StandardCharsets.UTF_8));
    }
}
