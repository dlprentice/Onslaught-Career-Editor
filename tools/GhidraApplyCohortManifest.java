//@category Symbol
//
// COHORT MANIFEST FRAMEWORK - the single reusable Ghidra promotion applier.
//
// This script replaces three near-duplicate one-shot appliers
// (GhidraApplyBoundaryCohort41V4, GhidraApplyNameCohort160V2,
// GhidraApplyAbiSignaturesV2).  A cohort is now a MANIFEST plus a SPEC, not a
// new program: the spec declares the program identity, the PRE/POST metric
// pins, the manifest integrity pins, the manifest->verb column binding, and the
// opt-in verb set.  Everything else - every gate the three appliers carried -
// lives here once.
//
// POLICY.  This file is LIVE_FORBIDDEN by construction.  Its containment gate
// requires a "cohort-rehearsal" path segment and refuses any project path under
// Ghidra\Projects or under the tracked repository snapshot.  There is no mode,
// spec key, or argument that can give it a live mode.  The live-capable twin is
// GhidraApplyCohortManifestLive.java, produced from this file by the reviewed
// allowlisted derivation in tools/ghidra_cohort_framework_tests.py - the same
// one-gate-inverted pattern already audited for V4 / V2 - and it additionally
// refuses any cohort id that is not in its compiled authorization allowlist.
//
// ---------------------------------------------------------------------------
// VERBS ARE OPT-IN.  A verb the spec does not declare is structurally
// unreachable: the mutation phase only walks declared verbs, and
// G_VERB_NOT_DECLARED refuses a manifest that binds columns a declared verb
// does not own.  A name cohort therefore cannot touch a body, and a signature
// cohort cannot touch a name, because the code path does not exist for it.
//
//   SET_NAME               Function.setName / Symbol.setName
//   SET_PROTOTYPE          Function.updateFunction (DYNAMIC_STORAGE_FORMAL_PARAMS)
//                          plus Function.setVarArgs, MANIFEST-DRIVEN (see below)
//   SET_BODY               Function.setBody
//   DISASSEMBLE_BOUNDED    Disassembler.disassemble(seeds, admitted, true)
//   CLEAR_BOUNDED          Listing.clearCodeUnits inside the admitted ranges
//   REMOVE_STALE_BOOKMARK  BookmarkManager.removeBookmark for a pinned set
//
// ---------------------------------------------------------------------------
// VARARGS IS A MANIFEST FIELD OF SET_PROTOTYPE, AND ITS DEFAULT IS PRESERVE.
// The three superseded appliers all carried
//     if (f.hasVarArgs()) { f.setVarArgs(false); }
// and then asserted POST/readback varargs == false.  That is two defects in one:
// a variadic function's prototype could never be expressed, and a target that
// already had varargs=true would be silently STRIPPED with the POST gate
// certifying the stripped state as correct.  Measured 2026-08-17 on db.18622:
// 10 of the 8,329 functions carry varargs=true, so the exposure was one manifest
// row away, not hypothetical.
//
// Here the value comes from the manifest column bound by `col.varArgs`:
//     true     set varargs on
//     false    set varargs off
//     empty    PRESERVE - end POST state must equal the PRE state
//     column absent entirely: PRESERVE for every row, and `varArgs` additionally
//              stays a FROZEN collateral column, so a move on ANY function -
//              target rows included - is a refusal.  A spec can therefore never
//              strip varargs by omission, which is the whole point.
// POST and readback compare against that manifest value, never against a
// literal.  A spec cannot widen FROZEN_COLUMNS; binding col.varArgs only unlocks
// the one column for the cohort's own target rows.
//
// ---------------------------------------------------------------------------
// REVERSIBILITY, measured in this Ghidra 12.1.2 headless build rather than
// assumed:
//
//   * endTransaction(id, false) does NOT revert Function.updateFunction - a
//     headless postScript already runs inside an outer transaction, so the
//     nested abort is a no-op for that verb;
//   * Program.canUndo() is false, so the undo stack is not available either;
//   * headless writes a NEW DATABASE VERSION even when the script throws.
//
// An in-process rollback therefore CANNOT be the safety net, and this framework
// never claims one.  No receipt this file writes contains the words
// "rolled-back", "atomic", or "transaction aborted"; every receipt carries
//     reversibility = CEREMONY_LEVEL_RESTORE_FROM_VERIFIED_PRE_BACKUP
//     inProcessRollback = NOT_AVAILABLE_MEASURED_2026_08_17
// Reversibility is a ceremony-level property: restore the replica or the live
// project from its verified PRE backup and compare logical readbacks.  Do not
// use a file-tree digest as the oracle for "nothing changed" after a writable
// session - the db version advances regardless.
//
// GATE ORDER, forced by that measured fact.  EVERY gate that can be evaluated
// without mutating is evaluated for EVERY row before the first write:
// containment, policy, identity, PRE metrics, manifest integrity, per-row
// current-state staleness, collision, verb preconditions, and full data-type
// resolution.  Only then does the mutation phase start, so no gate can fail
// mid-cohort.  A phase's own POST gates (classification, POST census,
// collateral) necessarily run after that phase's writes; they are hard failures
// whose recovery is the ceremony backup restore, and the receipt says so.
//
// ---------------------------------------------------------------------------
// MODES
//   census     read-only.  Measure and print every metric the spec can pin, so
//              a new cohort's spec is written from measurement.  Gates identity
//              and containment only.  Run with -readOnly.
//   identity   containment + policy + program identity + PRE metric pins.
//              No manifest needed.  Run with -readOnly.
//   dry        every non-mutating gate for every row; publishes no mutation.
//              (alias: predict)  Run with -readOnly.
//   apply      dry, then the declared verbs, then POST + full collateral.
//   readback   assert the exact POST state with no mutation, in a separate
//              process.  Run with -readOnly.
//   collateral read-only full frozen-column census dump for external diffing.
//              Run with -readOnly.
//   plan       everything apply does except the final commit.  Safe to run
//              writable in the sense that nothing is committed - but the db
//              version still advances, so treat the replica as spent.
//   probe-fault-escape | probe-fault-extraclear | probe-fault-clearescape
//   probe-fault-strandbytes | probe-fault-precedentclear
//   probe-fault-varargsflip
//              adverse fault injection.  Each deliberately breaks the
//              framework's own confinement so the detector can be shown to
//              fire.  None can ever commit: commit is hard-wired false in
//              every fault mode.  varargsflip writes the OPPOSITE of the
//              resolved varargs decision - including the preserved PRE value
//              when the manifest asks for nothing - so the POST/readback
//              varargs gates can be provoked in both directions.
//   probe-relax-manifest
//              adverse refusal testing with the manifest digest, row-count and
//              POST-census pins DISABLED, so a deliberately corrupted manifest
//              can prove the geometry and classification gates refuse on their
//              own.  Prints a PROBE banner.  Cannot commit.
//
// Usage:
//   -postScript GhidraApplyCohortManifest.java
//       <spec.tsv> <specSha256> <manifest.tsv> <mode> <out.json> [<out.tsv>]
//
// The spec's own SHA-256 is pinned on the command line and the spec pins the
// manifest, so neither can be edited silently between rehearsal and apply.
//
// PROVENANCE.  Every run measures and echoes THIS SCRIPT'S OWN source digest
// (COHORT_APPLIER, and the "applier" object in the receipt).  Without it, the
// only way to establish which applier version produced a receipt was file mtimes
// plus re-deriving the twin - inference, not measurement, and not a chain of
// custody.  A spec may additionally pin `applierSha256`, repeated if it wants to
// admit both the instrument and its live twin; a pin that matches nothing is
// APPLIER SHA PIN and refuses before any write.

import ghidra.app.script.GhidraScript;
import ghidra.program.disassemble.Disassembler;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressIterator;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DataTypeManager;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.listing.Bookmark;
import ghidra.program.model.listing.BookmarkManager;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.DataIterator;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.listing.ReturnParameterImpl;
import ghidra.program.model.listing.Variable;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceManager;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.SymbolIterator;

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.regex.Pattern;

public class GhidraApplyCohortManifest extends GhidraScript {

    // ---------------------------------------------------------------- policy
    static final String FRAMEWORK = "bea.ghidra.cohort-framework.v1";
    static final String POLICY = "LIVE_FORBIDDEN";
    static final String CONTAINMENT_SEGMENT = "cohort-rehearsal";
    static final String[] FORBIDDEN_PATH_MARKERS = {
        "ghidra\\projects", "ghidra/projects",
        "onslaught-career-editor\\reverse-engineering",
        "onslaught-career-editor/reverse-engineering",
    };

    // Reversibility strings.  These are the ONLY reversibility claims any
    // receipt from this framework may carry.
    static final String REVERSIBILITY =
        "CEREMONY_LEVEL_RESTORE_FROM_VERIFIED_PRE_BACKUP";
    static final String IN_PROCESS_ROLLBACK =
        "NOT_AVAILABLE_MEASURED_2026_08_17";

    // ----------------------------------------------------------------- verbs
    static final String V_SET_NAME = "SET_NAME";
    static final String V_SET_PROTOTYPE = "SET_PROTOTYPE";
    static final String V_SET_BODY = "SET_BODY";
    static final String V_SET_DATA_POINTER = "SET_DATA_POINTER";
    static final String V_DISASSEMBLE = "DISASSEMBLE_BOUNDED";
    static final String V_CLEAR = "CLEAR_BOUNDED";
    static final String V_BOOKMARK = "REMOVE_STALE_BOOKMARK";
    static final List<String> KNOWN_VERBS = Arrays.asList(
        V_DISASSEMBLE, V_CLEAR, V_BOOKMARK, V_SET_BODY, V_SET_NAME,
        V_SET_PROTOTYPE, V_SET_DATA_POINTER);

    /** The frozen per-function collateral column list.  Compiled in, never
     *  spec-supplied: a spec cannot widen it, and every column not claimed by a
     *  declared verb must be byte-identical PRE vs POST for EVERY function -
     *  target rows included. */
    static final String[] FROZEN_COLUMNS = {
        "name", "rangeSpec", "bodyBytes", "bodyRangeCount", "signatureShape",
        "callingConvention", "varArgs", "signatureSource", "symbolSource",
        "thunk", "thunkedEntry", "external", "noReturn", "customStorage",
        "stackParamBytes", "stackParamCount", "commentSha",
        "repeatableCommentSha", "tags", "namespace",
    };

    /** Which frozen columns each verb is allowed to move, and only on its own
     *  target rows.  Compiled in for the same reason.
     *
     *  varArgsDeclared is the ONE spec-dependent input: it says the spec bound
     *  col.varArgs, i.e. the cohort declared varargs as an axis it is changing.
     *  It can only ever UNLOCK the single `varArgs` column for target rows; a
     *  spec cannot add a column to FROZEN_COLUMNS or unlock any other one. */
    static Set<String> mutableColumnsFor(Set<String> verbs, boolean varArgsDeclared) {
        Set<String> out = new LinkedHashSet<>();
        if (verbs.contains(V_SET_NAME)) {
            out.add("name");
            // MEASURED, not assumed: setName(..., USER_DEFINED) necessarily
            // promotes the function symbol's source, and on the 2026-08-17
            // 160-row replay exactly 5 of the 158 function targets moved
            // symbolSource DEFAULT -> USER_DEFINED.  The 2026-08-17 name applier
            // did not carry symbolSource in its shape census at all, so
            // unlocking it for SET_NAME targets loses no gate; the ABI applier
            // DID freeze it, and that freeze survives because a signature
            // cohort never declares SET_NAME.  Non-target functions can still
            // never move it under any verb.
            out.add("symbolSource");
        }
        if (verbs.contains(V_SET_BODY)) {
            out.add("rangeSpec");
            out.add("bodyBytes");
            out.add("bodyRangeCount");
        }
        if (verbs.contains(V_SET_PROTOTYPE)) {
            out.add("signatureShape");
            out.add("signatureSource");
            out.add("stackParamBytes");
            out.add("stackParamCount");
            // varArgs is unlocked ONLY for a cohort that binds col.varArgs.  A
            // prototype cohort that says nothing about varargs leaves it FROZEN,
            // so the collateral census refuses a move on a target row too - that
            // is what makes "absent column means do not touch" a gate rather
            // than an intention.
            if (varArgsDeclared) {
                out.add("varArgs");
            }
        }
        return out;
    }

    static final Pattern LEGAL_NAME =
        Pattern.compile("^[A-Za-z_][A-Za-z0-9_]{0,190}$");
    static final Pattern LEGAL_TYPE =
        Pattern.compile("^[A-Za-z_][A-Za-z0-9_ ]{0,80}( \\*)*$");
    static final Pattern LEGAL_PNAME =
        Pattern.compile("^[A-Za-z_][A-Za-z0-9_]{0,120}$");
    static final int MAX_RESYNC = 16;

    private final List<String> failures = new ArrayList<>();
    private final List<String> notes = new ArrayList<>();
    private String cohortId = "<unset>";
    /** Set true the moment the mutation phase is entered.  committed=false does
     *  NOT mean nothing was written - this build has no working in-process
     *  rollback - so every receipt reports both. */
    private boolean writesAttempted = false;
    /** probe-fault-varargsflip only: write the OPPOSITE of the resolved varargs
     *  decision so the POST/readback varargs gates can be provoked by execution.
     *  A fault mode can never commit. */
    private boolean faultVarArgsFlip = false;

    private void fail(String message) {
        failures.add(message);
    }

    private void fail(Row row, String message) {
        if (row == null) {
            failures.add(message);
        } else {
            row.gateFailures.add(message);
            failures.add(row.addrText + ": " + message);
        }
    }

    // ============================================================== spec ===

    /** A cohort spec: TSV, key<TAB>value, '#' comments, repeated keys append. */
    static class Spec {
        final Map<String, List<String>> raw = new LinkedHashMap<>();
        String path;
        String sha256;
        long bytes;

        List<String> all(String key) {
            List<String> v = raw.get(key);
            return v == null ? new ArrayList<String>() : v;
        }

        String opt(String key, String dflt) {
            List<String> v = raw.get(key);
            return (v == null || v.isEmpty()) ? dflt : v.get(0);
        }

        boolean has(String key) {
            List<String> v = raw.get(key);
            return v != null && !v.isEmpty();
        }

        long num(String key, long dflt) {
            String v = opt(key, null);
            if (v == null) {
                return dflt;
            }
            try {
                return Long.parseLong(v.trim());
            } catch (NumberFormatException exc) {
                return Long.MIN_VALUE;
            }
        }
    }

    /** Every key this framework understands.  An unknown key is a REFUSAL, so a
     *  spec cannot smuggle intent past the framework by inventing a field. */
    static final Set<String> KNOWN_SPEC_KEYS = new LinkedHashSet<>(Arrays.asList(
        "cohortId", "cohortTitle", "verb",
        "programName", "programMd5", "programSha256", "imageBase", "language",
        "compilerSpec", "textBlock", "textStart", "textEnd",
        "preFunctions", "preInstructions", "preReferences", "preDefinedData",
        "preUndefinedData", "preBookmarks",
        "preFunctionNameDigest", "preFunctionBodyDigest", "preFrozenDigest",
        "postFunctions", "postInstructions", "postReferences",
        "postDefinedData", "postUndefinedData", "postBookmarks",
        "postFunctionNameDigest", "postFunctionBodyDigest", "postFrozenDigest",
        "manifestSha256", "manifestBytes", "manifestRows", "manifestColumns",
        "manifestHeaderPipe", "applierSha256",
        "col.addr", "col.currentName", "col.proposedName", "col.liveKind",
        "col.currentRanges", "col.proposedRanges", "col.subtype",
        "col.terminatorVa", "col.terminatorBytes", "col.deltaBytes",
        "col.byteProof",
        "col.liveName", "col.currentSignature", "col.currentSignatureSha256",
        "col.proposedSignature", "col.callingConvention", "col.returnType",
        "col.paramSpec", "col.arity", "col.arityBytes", "col.varArgs",
        "col.colName", "col.dwordValue", "col.confidence", "col.colAddr",
        "col.proposedLabel",
        "unique", "constant", "enum", "enumPrefix", "forbidToken", "noCycle",
        "expectedTargetsChanged", "expectedSymbolsAdded",
        "expectedSymbolsRemoved", "expectedFunctionsUntouched",
        "admittedBytes", "admittedUndefinedBytes", "clearedUnits",
        "clearedBytes", "clearPlan", "staleBookmark", "bookmarkType",
        "bookmarkCategory", "tableSubtype", "legalCallingConvention"));

    /** This script's own source bytes, digested.  A receipt that cannot say
     *  which applier produced it cannot support a chain of custody: before this,
     *  the only way to establish which instrument version ran was file mtimes
     *  plus re-deriving the twin, which is inference rather than measurement.
     *  The instrument and its live twin necessarily differ here, so a spec that
     *  pins `applierSha256` may list both. */
    private String applierSha = "<unmeasured>";
    private String applierPath = "<unknown>";
    private long applierBytes = -1;

    private void measureApplier() {
        try {
            byte[] raw;
            try (java.io.InputStream in = getSourceFile().getInputStream()) {
                raw = in.readAllBytes();
            }
            applierBytes = raw.length;
            applierSha = sha256(raw);
            applierPath = getSourceFile().getName();
        } catch (Exception exc) {
            applierSha = "<unreadable:" + exc.getClass().getSimpleName() + ">";
        }
    }

    private void gateApplierPin(Spec spec) {
        List<String> pinned = spec.all("applierSha256");
        if (pinned.isEmpty()) {
            return;
        }
        for (String want : pinned) {
            if (want.equalsIgnoreCase(applierSha)) {
                return;
            }
        }
        fail("APPLIER SHA PIN: applier sha256 " + applierSha + " is not among the "
            + pinned.size() + " pinned by the spec " + pinned);
    }

    private Spec loadSpec(Path specPath, String pinnedSha) throws Exception {
        Spec spec = new Spec();
        byte[] rawBytes = Files.readAllBytes(specPath);
        spec.path = specPath.toString();
        spec.bytes = rawBytes.length;
        spec.sha256 = sha256(rawBytes);
        if (!spec.sha256.equalsIgnoreCase(pinnedSha)) {
            fail("SPEC SHA PIN: spec sha256 " + spec.sha256 + " != pinned "
                + pinnedSha.toLowerCase(Locale.ROOT));
        }
        for (String line : new String(rawBytes, StandardCharsets.UTF_8).split("\n", -1)) {
            if (line.endsWith("\r")) {
                line = line.substring(0, line.length() - 1);
            }
            String trimmed = line.trim();
            if (trimmed.isEmpty() || trimmed.startsWith("#")) {
                continue;
            }
            int tab = line.indexOf('\t');
            if (tab < 0) {
                fail("SPEC SYNTAX: line is not key<TAB>value: " + line);
                continue;
            }
            String key = line.substring(0, tab).trim();
            String value = line.substring(tab + 1).trim();
            if (!KNOWN_SPEC_KEYS.contains(key)) {
                fail("SPEC UNKNOWN KEY: " + key);
                continue;
            }
            List<String> bucket = spec.raw.get(key);
            if (bucket == null) {
                bucket = new ArrayList<>();
                spec.raw.put(key, bucket);
            }
            bucket.add(value);
        }
        return spec;
    }

    // ================================================================ row ===

    static class Row {
        String addrText;
        long addr;
        Address entry;
        final Map<String, String> cells = new LinkedHashMap<>();
        String liveKind = "FUNCTION";

        // geometry
        AddressSet current;
        AddressSet proposed;
        AddressSet added;
        long deltaBytes = Long.MIN_VALUE;
        String subtype = "";

        // prototype
        final List<String[]> params = new ArrayList<>();
        int arity;
        int arityBytes;
        /** The function's varargs state as measured BEFORE any write.  It is the
         *  expectation for a PRESERVE row, so a preserved row is proven against
         *  a measurement rather than against a literal. */
        boolean preVarArgs;
        /** The manifest's varargs decision: TRUE, FALSE, or null for PRESERVE
         *  (empty cell, or no bound column at all). */
        Boolean varArgsWanted;
        String varArgsPost = "";

        // measurement
        String targetName = "";
        String preRanges = "";
        String postRanges = "";
        long preBytes = -1;
        long postBytes = -1;
        long preInstrBytes;
        long preDataBytes;
        long preUndefBytes;
        long postInstrBytes;
        long postDataBytes;
        long postUndefBytes;
        long preInstrCount;
        long postInstrCount;
        int phase1Passes;
        int resyncRounds;
        AddressSet cleared = new AddressSet();
        final List<String> clearedKinds = new ArrayList<>();
        String stillUndefined = "";
        String escaped = "";
        String rendered = "";
        String verdict = "PENDING";
        final List<String> gateFailures = new ArrayList<>();

        String get(String logical) {
            String v = cells.get(logical);
            return v == null ? "" : v;
        }

        long preClassified() { return preInstrBytes + preDataBytes; }
        long postClassified() { return postInstrBytes + postDataBytes; }
    }

    // ============================================================ helpers ===

    private static String hex(byte[] raw) {
        StringBuilder sb = new StringBuilder();
        for (byte b : raw) {
            sb.append(String.format(Locale.ROOT, "%02x", b & 0xff));
        }
        return sb.toString();
    }

    private static String sha256(byte[] raw) throws Exception {
        return hex(MessageDigest.getInstance("SHA-256").digest(raw));
    }

    private static String sha256(String s) throws Exception {
        return sha256(s.getBytes(StandardCharsets.UTF_8));
    }

    private static String jsonEscape(String value) {
        if (value == null) {
            return "";
        }
        StringBuilder sb = new StringBuilder();
        for (char c : value.toCharArray()) {
            if (c == '"' || c == '\\') {
                sb.append('\\').append(c);
            } else if (c == '\n') {
                sb.append("\\n");
            } else if (c == '\r') {
                sb.append("\\r");
            } else if (c == '\t') {
                sb.append("\\t");
            } else if (c < 0x20) {
                sb.append(String.format(Locale.ROOT, "\\u%04x", (int) c));
            } else {
                sb.append(c);
            }
        }
        return sb.toString();
    }

    private static String rangesText(AddressSetView set) {
        StringBuilder sb = new StringBuilder();
        for (AddressRange range : set) {
            if (sb.length() > 0) {
                sb.append(';');
            }
            sb.append(range.getMinAddress().toString()).append('-')
              .append(range.getMaxAddress().toString());
        }
        return sb.toString();
    }

    private static String bodyDigest(AddressSetView set) throws Exception {
        MessageDigest md = MessageDigest.getInstance("SHA-256");
        for (AddressRange range : set) {
            md.update(range.getMinAddress().toString().getBytes(StandardCharsets.UTF_8));
            md.update((byte) ':');
            md.update(range.getMaxAddress().toString().getBytes(StandardCharsets.UTF_8));
            md.update((byte) ';');
        }
        return hex(md.digest());
    }

    private static String rangeSpec(AddressSetView body) {
        StringBuilder sb = new StringBuilder();
        int n = 0;
        for (AddressRange r : body) {
            if (n++ > 0) {
                sb.append(';');
            }
            sb.append(String.format(Locale.ROOT, "%08x-%08x",
                r.getMinAddress().getOffset(), r.getMaxAddress().getOffset()));
        }
        return sb.toString();
    }

    private AddressSet parseRanges(String text) {
        AddressSet set = new AddressSet();
        for (String part : text.trim().split(";")) {
            part = part.trim();
            if (part.isEmpty()) {
                continue;
            }
            String[] halves = part.split("-");
            if (halves.length != 2) {
                return null;
            }
            try {
                Address lo = toAddr(Long.parseLong(halves[0].trim(), 16));
                Address hi = toAddr(Long.parseLong(halves[1].trim(), 16));
                if (lo.compareTo(hi) > 0) {
                    return null;
                }
                set.addRange(lo, hi);
            } catch (Exception exc) {
                return null;
            }
        }
        return set.isEmpty() ? null : set;
    }

    private static String digestOfMap(Map<String, String> m) throws Exception {
        StringBuilder sb = new StringBuilder();
        for (Map.Entry<String, String> e : m.entrySet()) {
            sb.append(e.getKey()).append('\t').append(e.getValue()).append('\n');
        }
        return sha256(sb.toString());
    }

    private static String digestOfList(List<String> l) throws Exception {
        return sha256(String.join("\n", l) + "\n");
    }

    // ============================================================= census ===

    private long functionCount() {
        long n = 0;
        FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
        while (it.hasNext()) {
            it.next();
            n++;
        }
        return n;
    }

    private long referenceCount() {
        long n = 0;
        ReferenceManager rm = currentProgram.getReferenceManager();
        AddressIterator it = rm.getReferenceSourceIterator(currentProgram.getMemory(), true);
        while (it.hasNext()) {
            n += rm.getReferencesFrom(it.next()).length;
        }
        return n;
    }

    private long undefinedDataCount() {
        long n = 0;
        DataIterator it = currentProgram.getListing().getData(true);
        while (it.hasNext()) {
            if (!it.next().isDefined()) {
                n++;
            }
        }
        return n;
    }

    private long bookmarkCount() {
        long n = 0;
        Iterator<Bookmark> it = currentProgram.getBookmarkManager().getBookmarksIterator();
        while (it.hasNext()) {
            it.next();
            n++;
        }
        return n;
    }

    private String memoryDigest() throws Exception {
        MessageDigest d = MessageDigest.getInstance("SHA-256");
        for (MemoryBlock b : currentProgram.getMemory().getBlocks()) {
            d.update((b.getName() + "|" + b.getStart() + "|" + b.getEnd() + "|"
                + b.getSize() + "|" + b.isInitialized() + "|" + b.isExecute()
                + "|" + b.isRead() + "|" + b.isWrite() + "\n")
                .getBytes(StandardCharsets.UTF_8));
            if (!b.isInitialized()) {
                continue;
            }
            Address cur = b.getStart();
            long remaining = b.getSize();
            while (remaining > 0) {
                int size = (int) Math.min(1 << 20, remaining);
                byte[] chunk = new byte[size];
                int read = currentProgram.getMemory().getBytes(cur, chunk);
                if (read != size) {
                    fail("SHORT MEMORY READ at " + cur);
                    break;
                }
                d.update(chunk);
                remaining -= size;
                if (remaining > 0) {
                    cur = cur.add(size);
                }
            }
        }
        return hex(d.digest());
    }

    private long readInt(Address address) throws Exception {
        byte[] got = new byte[4];
        if (currentProgram.getMemory().getBytes(address, got) != 4) {
            throw new IllegalStateException("cannot read 4 bytes at " + address);
        }
        return ((long) (got[0] & 0xff))
            | ((long) (got[1] & 0xff) << 8)
            | ((long) (got[2] & 0xff) << 16)
            | ((long) (got[3] & 0xff) << 24);
    }

    private String readCString(Address address) throws Exception {
        byte[] chunk = new byte[128];
        int read = currentProgram.getMemory().getBytes(address, chunk);
        int end = 0;
        while (end < read && chunk[end] != 0) {
            end++;
        }
        return new String(chunk, 0, end, StandardCharsets.US_ASCII);
    }

    private static String signatureShape(Function f) {
        String proto = f.getSignature().getPrototypeString(true);
        String nm = f.getName();
        return nm.isEmpty() ? proto : proto.replace(nm, "NAME");
    }

    /** entry -> the FROZEN_COLUMNS row, tab separated, for every function. */
    private TreeMap<String, String> frozenCensus() throws Exception {
        TreeMap<String, String> m = new TreeMap<>();
        FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
        while (it.hasNext()) {
            monitor.checkCancelled();
            Function f = it.next();
            m.put(String.format(Locale.ROOT, "%08x", f.getEntryPoint().getOffset()),
                  String.join("\t", frozenRow(f)));
        }
        return m;
    }

    private List<String> frozenRow(Function f) throws Exception {
        List<String> tg = new ArrayList<>();
        for (FunctionTag t : f.getTags()) {
            tg.add(t.getName());
        }
        Collections.sort(tg);
        Function thunked = f.isThunk() ? f.getThunkedFunction(false) : null;
        int stackParams = 0;
        for (Parameter p : f.getParameters()) {
            if (p.isStackVariable()) {
                stackParams++;
            }
        }
        AddressSetView body = f.getBody();
        List<String> out = new ArrayList<>();
        out.add(f.getName(true));
        out.add(rangeSpec(body));
        out.add(String.valueOf(body.getNumAddresses()));
        out.add(String.valueOf(body.getNumAddressRanges()));
        out.add(signatureShape(f));
        out.add(String.valueOf(f.getCallingConventionName()));
        out.add(String.valueOf(f.hasVarArgs()));
        out.add(String.valueOf(f.getSignatureSource()));
        out.add(f.getSymbol() == null ? "NO_SYMBOL"
                                     : f.getSymbol().getSource().toString());
        out.add(String.valueOf(f.isThunk()));
        out.add(thunked == null ? "-" : thunked.getEntryPoint().toString());
        out.add(String.valueOf(f.isExternal()));
        out.add(String.valueOf(f.hasNoReturn()));
        out.add(String.valueOf(f.hasCustomVariableStorage()));
        out.add(String.valueOf(f.getStackFrame().getParameterSize()));
        out.add(String.valueOf(stackParams));
        out.add(sha256(f.getComment() == null ? "<none>" : f.getComment()));
        out.add(sha256(f.getRepeatableComment() == null ? "<none>"
                                                       : f.getRepeatableComment()));
        out.add(tg.toString());
        out.add(f.getParentNamespace() == null ? ""
                : f.getParentNamespace().getName(true));
        return out;
    }

    /** Non-dynamic symbols only.  Dynamic (auto-generated, never stored) labels
     *  legitimately move when bounded disassembly corrects a desynchronised
     *  decode; a STORED symbol may not. */
    private List<String> symbolCensus() {
        List<String> out = new ArrayList<>();
        SymbolIterator it = currentProgram.getSymbolTable().getAllSymbols(true);
        while (it.hasNext()) {
            Symbol s = it.next();
            if (s.isDynamic()) {
                continue;
            }
            Address a = s.getAddress();
            out.add((a == null ? "-" : String.format(Locale.ROOT, "%08x", a.getOffset()))
                + "\t" + s.getName() + "\t" + s.getName(true)
                + "\t" + s.getSymbolType()
                + "\t" + (s.getParentNamespace() == null ? ""
                          : s.getParentNamespace().getName(true))
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

    private TreeMap<String, String> nameDigestForm() {
        TreeMap<String, String> m = new TreeMap<>();
        FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
        while (it.hasNext()) {
            Function f = it.next();
            m.put(String.format(Locale.ROOT, "%08x", f.getEntryPoint().getOffset()),
                  f.getName(true));
        }
        return m;
    }

    private TreeMap<String, String> bodyDigestForm() {
        TreeMap<String, String> m = new TreeMap<>();
        FunctionIterator it = currentProgram.getFunctionManager().getFunctions(true);
        while (it.hasNext()) {
            Function f = it.next();
            m.put(String.format(Locale.ROOT, "%08x", f.getEntryPoint().getOffset()),
                  rangeSpec(f.getBody()));
        }
        return m;
    }

    /** Every non-dynamic symbol name -> its addresses. */
    private Map<String, List<String>> nameIndex() {
        Map<String, List<String>> idx = new HashMap<>();
        SymbolIterator it = currentProgram.getSymbolTable().getAllSymbols(true);
        while (it.hasNext()) {
            Symbol s = it.next();
            if (s.isDynamic()) {
                continue;
            }
            Address a = s.getAddress();
            String key = s.getName();
            List<String> bucket = idx.get(key);
            if (bucket == null) {
                bucket = new ArrayList<>();
                idx.put(key, bucket);
            }
            bucket.add(a == null ? "-" : String.format(Locale.ROOT, "%08x", a.getOffset()));
        }
        return idx;
    }

    // ----------------------------------------------------- geometry census --

    private AddressSet undefinedIn(AddressSetView set) {
        Listing listing = currentProgram.getListing();
        AddressSet out = new AddressSet();
        for (AddressRange range : set) {
            Address p = range.getMinAddress();
            while (p != null && p.compareTo(range.getMaxAddress()) <= 0) {
                CodeUnit unit = listing.getCodeUnitContaining(p);
                boolean defined = (unit instanceof Instruction)
                        || (unit instanceof Data && ((Data) unit).isDefined());
                Address stop = (unit == null) ? p : unit.getMaxAddress();
                if (stop.compareTo(range.getMaxAddress()) > 0) {
                    stop = range.getMaxAddress();
                }
                if (!defined) {
                    out.addRange(p, stop);
                }
                if (stop.equals(range.getMaxAddress())) {
                    break;
                }
                p = stop.add(1);
            }
        }
        return out;
    }

    private AddressSet instructionCoverage(AddressSetView set) {
        AddressSet cover = new AddressSet();
        InstructionIterator it = currentProgram.getListing().getInstructions(set, true);
        while (it.hasNext()) {
            Instruction ins = it.next();
            cover.addRange(ins.getMinAddress(), ins.getMaxAddress());
        }
        return cover;
    }

    /** Code-unit-accurate byte split into instruction / defined data /
     *  undefined.  A byte owned by an instruction that STARTS OUTSIDE `set` is
     *  an instruction byte: several rows admit exactly that (operand tails), and
     *  counting them as data would misreport what is already classified. */
    private long[] byteSplit(AddressSetView set) {
        Listing listing = currentProgram.getListing();
        long instr = 0;
        long data = 0;
        long undef = 0;
        for (AddressRange range : set) {
            Address p = range.getMinAddress();
            while (p != null && p.compareTo(range.getMaxAddress()) <= 0) {
                CodeUnit unit = listing.getCodeUnitContaining(p);
                Address stop = (unit == null) ? p : unit.getMaxAddress();
                if (stop.compareTo(range.getMaxAddress()) > 0) {
                    stop = range.getMaxAddress();
                }
                long n = stop.getOffset() - p.getOffset() + 1;
                if (unit instanceof Instruction) {
                    instr += n;
                } else if (unit instanceof Data && ((Data) unit).isDefined()) {
                    data += n;
                } else {
                    undef += n;
                }
                if (stop.equals(range.getMaxAddress())) {
                    break;
                }
                p = stop.add(1);
            }
        }
        return new long[] {instr, data, undef};
    }

    private long countInstructionsIn(AddressSetView set) {
        long n = 0;
        InstructionIterator it = currentProgram.getListing().getInstructions(set, true);
        while (it.hasNext()) {
            it.next();
            n++;
        }
        return n;
    }

    private void censusRow(Row row, boolean pre) {
        if (row.added == null) {
            return;
        }
        long[] split = byteSplit(row.added);
        if (pre) {
            row.preInstrBytes = split[0];
            row.preDataBytes = split[1];
            row.preUndefBytes = split[2];
            row.preInstrCount = countInstructionsIn(row.added);
        } else {
            row.postInstrBytes = split[0];
            row.postDataBytes = split[1];
            row.postUndefBytes = split[2];
            row.postInstrCount = countInstructionsIn(row.added);
        }
    }

    private List<String> referencesFromWithin(AddressSetView set) {
        List<String> out = new ArrayList<>();
        ReferenceManager rm = currentProgram.getReferenceManager();
        AddressIterator it = rm.getReferenceSourceIterator(set, true);
        while (it.hasNext()) {
            Address a = it.next();
            for (Reference r : rm.getReferencesFrom(a)) {
                out.add(r.getFromAddress() + "->" + r.getToAddress() + ":"
                        + r.getReferenceType() + ":" + r.getOperandIndex());
            }
        }
        Collections.sort(out);
        return out;
    }

    private List<String> instructionStartsIn(AddressSetView set) {
        List<String> out = new ArrayList<>();
        InstructionIterator it = currentProgram.getListing().getInstructions(set, true);
        while (it.hasNext()) {
            out.add(it.next().getMinAddress().toString());
        }
        Collections.sort(out);
        return out;
    }

    // ===================================================== classification ===

    private void phase1(Row row, AddressSetView restricted, boolean dataBlind) {
        Listing listing = currentProgram.getListing();
        while (true) {
            AddressSet undef;
            if (dataBlind) {
                undef = new AddressSet(row.added);
                undef.delete(instructionCoverage(row.added));
            } else {
                undef = undefinedIn(row.added);
            }
            if (undef.isEmpty()) {
                return;
            }
            AddressSet seeds = new AddressSet();
            for (AddressRange r : undef) {
                seeds.add(r.getMinAddress());
            }
            long before = listing.getNumInstructions();
            Disassembler disassembler =
                    Disassembler.getDisassembler(currentProgram, monitor, null);
            disassembler.disassemble(seeds, restricted, true);
            row.phase1Passes++;
            if (listing.getNumInstructions() == before) {
                return;
            }
        }
    }

    private boolean phase2(Row row) {
        Listing listing = currentProgram.getListing();
        boolean progressed = false;
        for (AddressRange r : undefinedIn(row.added)) {
            Address after = r.getMaxAddress();
            Address probe;
            try {
                probe = after.add(1);
            } catch (Exception exc) {
                continue;
            }
            if (!row.added.contains(probe)) {
                continue;
            }
            CodeUnit unit = listing.getCodeUnitContaining(probe);
            if (unit == null) {
                continue;
            }
            boolean defined = (unit instanceof Instruction)
                    || (unit instanceof Data && ((Data) unit).isDefined());
            if (!defined) {
                continue;
            }
            if (!row.added.contains(unit.getMinAddress(), unit.getMaxAddress())) {
                // never clear across the admitted edge
                continue;
            }
            String kind = (unit instanceof Instruction) ? "INSTR"
                    : "DATA:" + ((Data) unit).getDataType().getName();
            row.clearedKinds.add(unit.getMinAddress() + "-" + unit.getMaxAddress()
                    + "=" + kind);
            row.cleared.addRange(unit.getMinAddress(), unit.getMaxAddress());
            listing.clearCodeUnits(unit.getMinAddress(), unit.getMaxAddress(), false);
            progressed = true;
        }
        return progressed;
    }

    private void classify(Row row, boolean allowResync, boolean noResync,
            boolean dataBlind) {
        for (int round = 0; round <= MAX_RESYNC; round++) {
            phase1(row, row.added, dataBlind);
            if (undefinedIn(row.added).isEmpty()) {
                return;
            }
            if (!allowResync || noResync || round == MAX_RESYNC || !phase2(row)) {
                return;
            }
            row.resyncRounds++;
        }
    }

    /** ADVERSE FAULT INJECTION ONLY: the destructive precedent shape. */
    private void precedentClearFault(Row row) {
        Listing listing = currentProgram.getListing();
        List<Instruction> doomed = new ArrayList<>();
        InstructionIterator it = listing.getInstructions(row.added, true);
        while (it.hasNext()) {
            Instruction ins = it.next();
            if (row.added.contains(ins.getMinAddress(), ins.getMaxAddress())) {
                doomed.add(ins);
            }
        }
        for (Instruction ins : doomed) {
            row.clearedKinds.add(ins.getMinAddress() + "-" + ins.getMaxAddress()
                    + "=PRECEDENT_FAULT");
            row.cleared.addRange(ins.getMinAddress(), ins.getMaxAddress());
            listing.clearCodeUnits(ins.getMinAddress(), ins.getMaxAddress(), false);
        }
    }

    // ================================================= type resolution =====

    private DataType resolveType(String spec, Row row) {
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
        if (dt == null) {
            fail(row, "unknown data type [" + spec + "]; this framework refuses "
                + "to define new types");
            return null;
        }
        for (int i = 0; i < stars; i++) {
            dt = PointerDataType.getPointer(dt, dtm);
        }
        return dt;
    }

    // =============================================================== main ===

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 5 || args.length > 6) {
            println("COHORT_FAIL reason=usage expected="
                + "<spec.tsv> <specSha256> <manifest.tsv> <mode> <out.json> [<out.tsv>]"
                + " got=" + (args == null ? 0 : args.length));
            return;
        }
        Path specPath = Paths.get(args[0]);
        String specSha = args[1];
        Path manifestPath = Paths.get(args[2]);
        String mode = args[3];
        Path outJson = Paths.get(args[4]);
        Path outTsv = args.length == 6 ? Paths.get(args[5]) : null;

        boolean census = "census".equals(mode);
        boolean identity = "identity".equals(mode);
        boolean dry = "dry".equals(mode) || "predict".equals(mode);
        boolean apply = "apply".equals(mode);
        boolean readback = "readback".equals(mode);
        boolean collateralOnly = "collateral".equals(mode);
        boolean planOnly = "plan".equals(mode);
        boolean relax = "probe-relax-manifest".equals(mode);
        boolean faultEscape = "probe-fault-escape".equals(mode);
        boolean faultExtraClear = "probe-fault-extraclear".equals(mode);
        boolean faultClearEscape = "probe-fault-clearescape".equals(mode);
        boolean faultStrand = "probe-fault-strandbytes".equals(mode);
        boolean faultPrecedent = "probe-fault-precedentclear".equals(mode);
        faultVarArgsFlip = "probe-fault-varargsflip".equals(mode);
        boolean faultMode = faultEscape || faultExtraClear || faultClearEscape
                || faultStrand || faultPrecedent || faultVarArgsFlip;
        boolean mutating = apply || planOnly || relax || faultMode;
        if (!(census || identity || dry || apply || readback || collateralOnly
                || planOnly || relax || faultMode)) {
            println("COHORT_FAIL reason=bad_mode value=" + mode);
            return;
        }

        // ---- GATE 1: containment.  Never live, never the tracked repo. ------
        String projectPath;
        try {
            File dir = state.getProject().getProjectLocator().getProjectDir();
            projectPath = dir.getAbsolutePath();
        } catch (Exception exc) {
            println("COHORT_FAIL reason=no_project_locator");
            return;
        }
        String lower = projectPath.toLowerCase(Locale.ROOT).replace('/', '\\');
        for (String marker : FORBIDDEN_PATH_MARKERS) {
            if (lower.contains(marker.replace('/', '\\'))) {
                println("COHORT_REFUSE reason=forbidden_project_path marker=" + marker
                    + " path=" + projectPath);
                return;
            }
        }
        if (!lower.contains(CONTAINMENT_SEGMENT)) {
            println("COHORT_REFUSE reason=project_not_in_rehearsal_scratch path="
                + projectPath);
            return;
        }
        println("COHORT_GATE containment=ok policy=" + POLICY + " path=" + projectPath);
        measureApplier();
        println("COHORT_APPLIER script=" + applierPath + " bytes=" + applierBytes
            + " sha256=" + applierSha + " framework=" + FRAMEWORK);

        if (currentProgram == null) {
            println("COHORT_FAIL reason=no_current_program");
            return;
        }

        // ---- spec ----------------------------------------------------------
        Spec spec = loadSpec(specPath, specSha);
        cohortId = spec.opt("cohortId", "<missing>");
        gateApplierPin(spec);
        Set<String> verbs = new LinkedHashSet<>();
        for (String v : spec.all("verb")) {
            if (!KNOWN_VERBS.contains(v)) {
                fail("SPEC UNKNOWN VERB: " + v);
            } else {
                verbs.add(v);
            }
        }
        if (verbs.isEmpty() && !(census || identity || collateralOnly)) {
            fail("SPEC declares no verb");
        }
        // Verb-declaration gate: a column binding only a non-declared verb owns
        // is a refusal, so a name cohort is structurally unable to touch a body.
        checkVerbColumnBinding(spec, verbs);
        boolean varArgsDeclared = spec.has("col.varArgs");
        Set<String> mutableColumns = mutableColumnsFor(verbs, varArgsDeclared);
        println("COHORT_GATE spec=ok cohort=" + cohortId + " sha256=" + spec.sha256
            + " verbs=" + verbs + " mutableColumns=" + mutableColumns);
        println("COHORT_GATE varargsPolicy=MANIFEST_DRIVEN_DEFAULT_PRESERVE"
            + " varargsColumnBound=" + varArgsDeclared
            + " varArgsFrozenForTargets=" + !varArgsDeclared);

        // ---- GATE 2: program identity --------------------------------------
        gateIdentity(spec);

        Listing listing = currentProgram.getListing();
        FunctionManager fm = currentProgram.getFunctionManager();
        BookmarkManager bm = currentProgram.getBookmarkManager();

        long nowFunctions = functionCount();
        long nowInstructions = listing.getNumInstructions();
        long nowReferences = referenceCount();
        long nowDefinedData = listing.getNumDefinedData();
        long nowUndefinedData = undefinedDataCount();
        List<String> preBookmarkList = bookmarkCensus();
        long nowBookmarks = preBookmarkList.size();

        if (census) {
            println("COHORT_CENSUS functions=" + nowFunctions
                + " instructions=" + nowInstructions
                + " references=" + nowReferences
                + " definedData=" + nowDefinedData
                + " undefinedData=" + nowUndefinedData
                + " bookmarks=" + nowBookmarks);
            println("COHORT_CENSUS functionNameDigest="
                + digestOfMap(nameDigestForm())
                + " functionBodyDigest=" + digestOfMap(bodyDigestForm())
                + " frozenCensusDigest=" + digestOfMap(frozenCensus())
                + " symbolDigest=" + digestOfList(symbolCensus())
                + " symbolCount=" + symbolCensus().size()
                + " bookmarkDigest=" + digestOfList(preBookmarkList)
                + " definedDataDigest=" + digestOfList(definedDataCensus())
                + " memoryDigest=" + memoryDigest());
            MemoryBlock text = currentProgram.getMemory().getBlock(
                spec.opt("textBlock", ".text"));
            if (text != null) {
                println("COHORT_CENSUS textBlock=" + text.getName()
                    + " start=" + text.getStart() + " end=" + text.getEnd()
                    + " execute=" + text.isExecute());
            }
            emitJson(outJson, mode, projectPath, spec, manifestPath, "n/a", 0,
                new ArrayList<Row>(), verbs, mutableColumns,
                nowFunctions, nowInstructions, nowReferences, nowDefinedData,
                nowUndefinedData, nowBookmarks,
                nowFunctions, nowInstructions, nowReferences, nowDefinedData,
                nowUndefinedData, nowBookmarks, null, false);
            report(mode, 0);
            return;
        }

        // ---- GATE 3: PRE metric pins ---------------------------------------
        // readback compares against POST, everything else against PRE.
        if (!readback && !collateralOnly) {
            gateMetrics(spec, "PRE", "pre", nowFunctions, nowInstructions,
                nowReferences, nowDefinedData, nowUndefinedData, nowBookmarks,
                relax);
            if (spec.has("preFunctionNameDigest")) {
                String got = digestOfMap(nameDigestForm());
                if (!spec.opt("preFunctionNameDigest", "").equals(got)) {
                    fail("PRE function NAME digest " + got + " != pinned "
                        + spec.opt("preFunctionNameDigest", ""));
                }
            }
            if (spec.has("preFunctionBodyDigest")) {
                String got = digestOfMap(bodyDigestForm());
                if (!spec.opt("preFunctionBodyDigest", "").equals(got)) {
                    fail("PRE function BODY digest " + got + " != pinned "
                        + spec.opt("preFunctionBodyDigest", ""));
                }
            }
            if (spec.has("preFrozenDigest")) {
                String got = digestOfMap(frozenCensus());
                if (!spec.opt("preFrozenDigest", "").equals(got)) {
                    fail("PRE frozen-census digest " + got + " != pinned "
                        + spec.opt("preFrozenDigest", ""));
                }
            }
        } else {
            gateMetrics(spec, "POST", "post", nowFunctions, nowInstructions,
                nowReferences, nowDefinedData, nowUndefinedData, nowBookmarks,
                relax || collateralOnly);
            if (!collateralOnly) {
                gatePostDigests(spec);
            }
        }

        if (identity) {
            println("COHORT_VERDICT mode=identity cohort=" + cohortId
                + " result=" + (failures.isEmpty() ? "PASS" : "FAIL"));
            emitJson(outJson, mode, projectPath, spec, manifestPath, "n/a", 0,
                new ArrayList<Row>(), verbs, mutableColumns,
                nowFunctions, nowInstructions, nowReferences, nowDefinedData,
                nowUndefinedData, nowBookmarks,
                nowFunctions, nowInstructions, nowReferences, nowDefinedData,
                nowUndefinedData, nowBookmarks, null, false);
            report(mode, 0);
            return;
        }

        // ---- GATE 4: manifest integrity ------------------------------------
        int failuresBeforeManifest = failures.size();
        byte[] manifestRaw = Files.readAllBytes(manifestPath);
        String manifestSha = sha256(manifestRaw);
        boolean manifestIsPinned =
            spec.opt("manifestSha256", "").equalsIgnoreCase(manifestSha)
            && manifestRaw.length == spec.num("manifestBytes", -1);
        if (!relax) {
            if (!spec.opt("manifestSha256", "").equalsIgnoreCase(manifestSha)) {
                fail("manifest sha256 " + manifestSha + " != pinned "
                    + spec.opt("manifestSha256", ""));
            }
            if (spec.has("manifestBytes")
                    && manifestRaw.length != spec.num("manifestBytes", -1)) {
                fail("manifest bytes " + manifestRaw.length + " != pinned "
                    + spec.num("manifestBytes", -1));
            }
        }
        for (String token : spec.all("forbidToken")) {
            if (new String(manifestRaw, StandardCharsets.UTF_8).contains(token)) {
                fail("FORBIDDEN MANIFEST TOKEN present: " + token);
            }
        }
        List<String> lines = new ArrayList<>();
        for (String line : new String(manifestRaw, StandardCharsets.UTF_8).split("\n", -1)) {
            String t = line.endsWith("\r") ? line.substring(0, line.length() - 1) : line;
            if (!t.isEmpty()) {
                lines.add(t);
            }
        }
        if (lines.isEmpty()) {
            fail("manifest is empty");
            println("COHORT_FAIL reason=manifest_empty");
            emitJson(outJson, mode, projectPath, spec, manifestPath, manifestSha,
                manifestRaw.length, new ArrayList<Row>(), verbs, mutableColumns,
                nowFunctions, nowInstructions, nowReferences, nowDefinedData,
                nowUndefinedData, nowBookmarks, nowFunctions, nowInstructions,
                nowReferences, nowDefinedData, nowUndefinedData, nowBookmarks,
                null, false);
            return;
        }
        String[] headerCells = lines.get(0).split("\t", -1);
        String headerPipe = String.join("|", headerCells);
        if (!spec.opt("manifestHeaderPipe", "").equals(headerPipe)) {
            fail("manifest header drift: [" + headerPipe + "] != pinned ["
                + spec.opt("manifestHeaderPipe", "") + "]");
            println("COHORT_FAIL reason=manifest_header");
            emitJson(outJson, mode, projectPath, spec, manifestPath, manifestSha,
                manifestRaw.length, new ArrayList<Row>(), verbs, mutableColumns,
                nowFunctions, nowInstructions, nowReferences, nowDefinedData,
                nowUndefinedData, nowBookmarks, nowFunctions, nowInstructions,
                nowReferences, nowDefinedData, nowUndefinedData, nowBookmarks,
                null, false);
            return;
        }
        long declaredColumns = spec.num("manifestColumns", headerCells.length);
        if (headerCells.length != declaredColumns) {
            fail("manifest header column count " + headerCells.length
                + " != pinned " + declaredColumns);
        }
        if (!relax && spec.has("manifestRows")
                && (lines.size() - 1) != spec.num("manifestRows", -1)) {
            fail("row count " + (lines.size() - 1) + " != "
                + spec.num("manifestRows", -1));
        }

        Map<String, Integer> binding = columnBinding(spec, headerCells);
        List<Row> rows = new ArrayList<>();
        Map<String, Row> byAddr = new LinkedHashMap<>();
        Map<String, Set<String>> uniqueSeen = new LinkedHashMap<>();
        for (String u : spec.all("unique")) {
            uniqueSeen.put(u, new HashSet<String>());
        }
        for (int i = 1; i < lines.size(); i++) {
            String[] cells = lines.get(i).split("\t", -1);
            if (cells.length != declaredColumns) {
                fail("row " + i + " column count " + cells.length + " != "
                    + declaredColumns);
                continue;
            }
            Row row = new Row();
            for (Map.Entry<String, Integer> e : binding.entrySet()) {
                row.cells.put(e.getKey(), cells[e.getValue()].trim());
            }
            row.addrText = row.get("addr").toLowerCase(Locale.ROOT);
            if (!row.addrText.startsWith("0x")) {
                fail(row, "address not 0x-prefixed");
                rows.add(row);
                continue;
            }
            try {
                row.addr = Long.parseLong(row.addrText.substring(2), 16);
                row.entry = toAddr(row.addr);
            } catch (Exception exc) {
                fail(row, "address not parseable: " + row.addrText);
                rows.add(row);
                continue;
            }
            if (byAddr.containsKey(row.addrText)) {
                fail(row, "duplicate address in manifest");
            }
            byAddr.put(row.addrText, row);
            // generic value legality
            for (String constant : spec.all("constant")) {
                String[] kv = constant.split("=", 2);
                if (kv.length == 2 && row.cells.containsKey(kv[0])
                        && !row.get(kv[0]).equals(kv[1])) {
                    fail(row, "column " + kv[0] + " must equal [" + kv[1]
                        + "] but is [" + row.get(kv[0]) + "]");
                }
            }
            for (String enumSpec : spec.all("enum")) {
                String[] kv = enumSpec.split("=", 2);
                if (kv.length != 2 || !row.cells.containsKey(kv[0])) {
                    continue;
                }
                List<String> allowed = Arrays.asList(kv[1].split(","));
                if (!allowed.contains(row.get(kv[0]))) {
                    fail(row, "illegal value in " + kv[0] + ": ["
                        + row.get(kv[0]) + "] not in " + allowed);
                }
            }
            for (String enumSpec : spec.all("enumPrefix")) {
                String[] kv = enumSpec.split("=", 2);
                if (kv.length != 2 || !row.cells.containsKey(kv[0])) {
                    continue;
                }
                boolean ok = false;
                for (String p : kv[1].split(",")) {
                    if (row.get(kv[0]).startsWith(p)) {
                        ok = true;
                        break;
                    }
                }
                if (!ok) {
                    fail(row, "illegal value in " + kv[0] + ": ["
                        + row.get(kv[0]) + "] matches no allowed prefix of "
                        + kv[1]);
                }
            }
            for (Map.Entry<String, Set<String>> e : uniqueSeen.entrySet()) {
                if (!row.cells.containsKey(e.getKey())) {
                    continue;
                }
                if (!e.getValue().add(row.get(e.getKey()))) {
                    fail(row, "duplicate " + e.getKey() + " "
                        + row.get(e.getKey()));
                }
            }
            rows.add(row);
        }

        // no-op rows, per verb
        for (Row row : rows) {
            if (verbs.contains(V_SET_NAME) && row.cells.containsKey("proposedName")
                    && row.get("proposedName").equals(row.get("currentName"))) {
                fail(row, "is a no-op rename: " + row.get("proposedName"));
            }
            if (verbs.contains(V_SET_PROTOTYPE)
                    && row.cells.containsKey("proposedSignature")
                    && row.get("proposedSignature").equals(row.get("currentSignature"))) {
                fail(row, "is a no-op proposal");
            }
        }

        // rename cycles: a proposal may not be another row's current name
        for (String cycleSpec : spec.all("noCycle")) {
            String[] pc = cycleSpec.split(":", 2);
            if (pc.length != 2) {
                fail("SPEC noCycle must be proposedCol:currentCol");
                continue;
            }
            Set<String> currents = new HashSet<>();
            for (Row row : rows) {
                currents.add(row.get(pc[1]));
            }
            for (Row row : rows) {
                if (currents.contains(row.get(pc[0]))) {
                    fail(row, "rename cycle: '" + row.get(pc[0]) + "' is another "
                        + "row's current name; this framework refuses "
                        + "order-dependent swaps");
                }
            }
        }
        // Report honestly: "ok" only if no manifest-scope gate actually failed.
        if (failures.size() == failuresBeforeManifest) {
            println("COHORT_GATE manifest=ok rows=" + rows.size()
                + " sha256=" + manifestSha);
        } else {
            println("COHORT_GATE manifest=FAILED gatesFailed="
                + (failures.size() - failuresBeforeManifest) + " rows="
                + rows.size() + " sha256=" + manifestSha);
        }

        // ---- GATE 5: per-row resolution, staleness and verb preconditions ---
        AddressSet textSet = null;
        if (spec.has("textStart") && spec.has("textEnd")) {
            textSet = new AddressSet(toAddr(Long.parseLong(spec.opt("textStart", "0"), 16)),
                                     toAddr(Long.parseLong(spec.opt("textEnd", "0"), 16)));
        }
        AddressSet allProposed = new AddressSet();
        AddressSet admitted = new AddressSet();
        Map<String, List<String>> preOtherHolders = new HashMap<>();
        Map<String, List<String>> idx = nameIndex();

        for (Row row : rows) {
            if (row.entry == null) {
                continue;
            }
            Function fn = fm.getFunctionAt(row.entry);
            row.liveKind = row.cells.containsKey("liveKind")
                    ? row.get("liveKind") : "FUNCTION";

            if ("SYMBOL:Label".equals(row.liveKind)) {
                if (fn != null) {
                    fail(row, "is a function, but the manifest says SYMBOL:Label");
                    continue;
                }
                Symbol s = currentProgram.getSymbolTable().getPrimarySymbol(row.entry);
                if (s == null) {
                    fail(row, "no primary symbol at " + row.addrText);
                    continue;
                }
                if (s.isDynamic()) {
                    fail(row, "primary symbol is dynamic");
                    continue;
                }
                if (!"Label".equals(s.getSymbolType().toString())) {
                    fail(row, "symbolType expected [Label] actual ["
                        + s.getSymbolType() + "]");
                    continue;
                }
                row.targetName = s.getName();
            } else if ("DATA:POINTER".equals(row.liveKind)) {
                try {
                    if (!verbs.contains(V_SET_DATA_POINTER)) {
                        fail(row, "DATA:POINTER row without the SET_DATA_POINTER verb");
                        continue;
                    }
                    if (fn != null) {
                        fail(row, "is a function, but the manifest says DATA:POINTER");
                        continue;
                    }
                    if (readback) {
                        if (listing.getDefinedDataAt(row.entry) == null) {
                            fail(row, "READBACK slot has no defined data");
                            continue;
                        }
                        Symbol label = currentProgram.getSymbolTable()
                                .getPrimarySymbol(row.entry);
                        if (label == null
                                || !row.get("proposedLabel").equals(label.getName())) {
                            fail(row, "READBACK label expected ["
                                + row.get("proposedLabel") + "] actual ["
                                + (label == null ? "<none>" : label.getName()) + "]");
                            continue;
                        }
                    } else {
                        Data directData = listing.getDefinedDataAt(row.entry);
                        Data containingData = listing.getDataContaining(row.entry);
                        boolean undefinedNow = directData == null
                            && (containingData == null
                                || !containingData.isDefined());
                        if (!undefinedNow) {
                            fail(row, "slot is already inside defined data");
                            continue;
                        }
                    }
                    long want = Long.parseLong(row.get("dwordValue"), 16);
                    long got = readInt(row.entry);
                    if (got != want) {
                        fail(row, "slot dword expected [" + row.get("dwordValue")
                            + "] actual [" + String.format("%08x", got) + "]");
                        continue;
                    }
                    Address target = row.entry.getNewAddress(got);
                    if (fm.getFunctionAt(target) == null) {
                        fail(row, "slot dword target is not a function entry: "
                            + String.format("%08x", got));
                        continue;
                    }
                    Address colAddr = toAddr(
                        Long.parseLong(row.get("colAddr").replaceFirst("^0x", ""), 16));
                    long colStruct = readInt(colAddr);
                    long td = readInt(toAddr(colStruct + 0x0c));
                    String mangled = readCString(toAddr(td + 0x08));
                    if (mangled.isEmpty()
                            || !mangled.equalsIgnoreCase(row.get("colName"))) {
                        fail(row, "COL identity expected [" + row.get("colName")
                            + "] actual [" + mangled + "]");
                        continue;
                    }
                    if (!readback) {
                        List<String> hits = idx.get(row.get("proposedLabel"));
                        if (hits != null) {
                            for (String h : hits) {
                                if (!h.equals(row.addrText.substring(2))) {
                                    fail(row, "collision: proposed label '"
                                        + row.get("proposedLabel")
                                        + "' already exists at 0x" + h);
                                }
                            }
                        }
                    }
                    row.targetName = row.get("proposedLabel");
                } catch (Exception exc) {
                    fail(row, "data slot gate threw " + exc);
                }
            } else {
                if (fn == null) {
                    fail(row, "NO FUNCTION AT ENTRY");
                    continue;
                }
                if (!fn.getEntryPoint().equals(row.entry)) {
                    fail(row, "function entry expected [" + row.entry
                        + "] actual [" + fn.getEntryPoint() + "]");
                    continue;
                }
                row.targetName = fn.getName();
                row.preRanges = rangesText(fn.getBody());
                row.preBytes = fn.getBody().getNumAddresses();
            }

            // -- staleness: the recorded CURRENT state must still be true -----
            if (verbs.contains(V_SET_NAME) && row.cells.containsKey("currentName")) {
                if (!readback && !row.get("currentName").equals(row.targetName)) {
                    fail(row, "CURRENT name expected [" + row.get("currentName")
                        + "] actual [" + row.targetName + "]");
                }
                if (readback && !row.get("proposedName").equals(row.targetName)) {
                    fail(row, "READBACK name expected [" + row.get("proposedName")
                        + "] actual [" + row.targetName + "]");
                }
            }
            if (verbs.contains(V_SET_PROTOTYPE) && fn != null) {
                gatePrototypeRow(row, fn, readback);
            }
            if (verbs.contains(V_SET_BODY) && fn != null) {
                gateGeometryRow(row, fn, spec, textSet, allProposed, admitted,
                    readback, fm, listing);
            }

            // -- collision + PRE holder bookkeeping for SET_NAME -------------
            if (verbs.contains(V_SET_NAME) && !readback) {
                String self = row.addrText.substring(2);
                List<String> holders = idx.get(row.get("currentName"));
                if (holders == null || !holders.contains(self)) {
                    fail(row, "PRE census: '" + row.get("currentName")
                        + "' is not held at " + row.addrText + " (holders "
                        + holders + ")");
                }
                List<String> others = holders == null ? new ArrayList<String>()
                        : new ArrayList<>(holders);
                others.remove(self);
                Collections.sort(others);
                preOtherHolders.put(row.addrText, others);
                if (!LEGAL_NAME.matcher(row.get("proposedName")).matches()) {
                    fail(row, "illegal proposed name: " + row.get("proposedName"));
                }
                List<String> hits = idx.get(row.get("proposedName"));
                if (hits != null) {
                    for (String h : hits) {
                        if (!h.equals(self)) {
                            fail(row, "collision: proposed name '"
                                + row.get("proposedName") + "' for "
                                + row.addrText + " already exists at 0x" + h);
                        }
                    }
                }
            }
        }

        // ---- GATE 6: full data-type resolution before any write -------------
        if (verbs.contains(V_SET_PROTOTYPE) && !readback) {
            int resolved = 0;
            for (Row row : rows) {
                if (resolveType(row.get("returnType"), row) != null) {
                    resolved++;
                }
                for (String[] pp : row.params) {
                    if (pp[3].equals("auto")) {
                        continue;
                    }
                    if (resolveType(pp[1], row) != null) {
                        resolved++;
                    }
                }
            }
            println("COHORT_GATE types=ok resolved=" + resolved
                + " (lookup only, no new type defined)");
            int vaOn = 0;
            int vaOff = 0;
            int vaPreserve = 0;
            int vaPreserveTrue = 0;
            for (Row row : rows) {
                if (row.varArgsWanted == null) {
                    vaPreserve++;
                    if (row.preVarArgs) {
                        vaPreserveTrue++;
                    }
                } else if (row.varArgsWanted.booleanValue()) {
                    vaOn++;
                } else {
                    vaOff++;
                }
            }
            println("COHORT_GATE varargs=ok setTrue=" + vaOn + " setFalse=" + vaOff
                + " preserve=" + vaPreserve + " preservedTrue=" + vaPreserveTrue
                + " (preserve compares POST against the measured PRE value)");
        }

        // ---- boundary aggregate pins ---------------------------------------
        long preAdmittedUndefined = 0;
        for (Row row : rows) {
            preAdmittedUndefined += row.preUndefBytes;
        }
        if (verbs.contains(V_SET_BODY) && !relax && !readback) {
            if (spec.has("admittedBytes")
                    && admitted.getNumAddresses() != spec.num("admittedBytes", -1)) {
                fail("admitted byte count " + admitted.getNumAddresses() + " != "
                    + spec.num("admittedBytes", -1));
            }
            if (spec.has("admittedUndefinedBytes")
                    && preAdmittedUndefined != spec.num("admittedUndefinedBytes", -1)) {
                fail("PRE admitted-undefined byte count " + preAdmittedUndefined
                    + " != " + spec.num("admittedUndefinedBytes", -1));
            }
        }

        // ---- PRE census snapshot -------------------------------------------
        TreeMap<String, String> preFrozen = frozenCensus();
        List<String> preSyms = symbolCensus();
        List<String> preDefinedData = definedDataCensus();
        String preMemory = memoryDigest();
        List<String> preRefsInAdmitted = referencesFromWithin(admitted);
        List<String> preInstrStarts = instructionStartsIn(admitted);
        println("COHORT_PRE frozenDigest=" + digestOfMap(preFrozen)
            + " symbolDigest=" + digestOfList(preSyms)
            + " bookmarkDigest=" + digestOfList(preBookmarkList)
            + " definedDataDigest=" + digestOfList(preDefinedData)
            + " memoryDigest=" + preMemory);

        // ---- readback ------------------------------------------------------
        if (readback) {
            gateReadback(rows, spec, verbs, fm, idx);
            for (Row row : rows) {
                row.verdict = row.gateFailures.isEmpty() ? "PASS" : "FAIL";
            }
            emit(outTsv, rows);
            emitJson(outJson, mode, projectPath, spec, manifestPath, manifestSha,
                manifestRaw.length, rows, verbs, mutableColumns,
                nowFunctions, nowInstructions, nowReferences, nowDefinedData,
                nowUndefinedData, nowBookmarks, nowFunctions, nowInstructions,
                nowReferences, nowDefinedData, nowUndefinedData, nowBookmarks,
                null, false);
            report(mode, rows.size());
            return;
        }

        // ---- collateral (read-only dump) -----------------------------------
        if (collateralOnly) {
            StringBuilder sb = new StringBuilder("entry\t"
                + String.join("\t", FROZEN_COLUMNS) + "\n");
            for (Map.Entry<String, String> e : preFrozen.entrySet()) {
                sb.append(e.getKey()).append('\t').append(e.getValue()).append('\n');
            }
            if (outTsv != null) {
                Files.write(outTsv, sb.toString().getBytes(StandardCharsets.UTF_8));
            }
            emitJson(outJson, mode, projectPath, spec, manifestPath, manifestSha,
                manifestRaw.length, rows, verbs, mutableColumns,
                nowFunctions, nowInstructions, nowReferences, nowDefinedData,
                nowUndefinedData, nowBookmarks, nowFunctions, nowInstructions,
                nowReferences, nowDefinedData, nowUndefinedData, nowBookmarks,
                null, false);
            report(mode, rows.size());
            return;
        }

        // ---- dry -----------------------------------------------------------
        if (dry) {
            for (Row row : rows) {
                row.verdict = row.gateFailures.isEmpty() ? "WOULD_APPLY"
                                                         : "WOULD_REFUSE";
                if (row.added != null) {
                    row.stillUndefined = rangesText(undefinedIn(row.added));
                }
            }
            emit(outTsv, rows);
            emitJson(outJson, mode, projectPath, spec, manifestPath, manifestSha,
                manifestRaw.length, rows, verbs, mutableColumns,
                nowFunctions, nowInstructions, nowReferences, nowDefinedData,
                nowUndefinedData, nowBookmarks, nowFunctions, nowInstructions,
                nowReferences, nowDefinedData, nowUndefinedData, nowBookmarks,
                null, false);
            report(mode, rows.size());
            return;
        }

        // ---- mutating: refuse before the first write ------------------------
        if (!failures.isEmpty()) {
            println("COHORT_REFUSE reason=gate_failure count=" + failures.size());
            for (String message : failures) {
                println("COHORT_GATE_FAIL " + message);
            }
            for (Row row : rows) {
                row.verdict = row.gateFailures.isEmpty() ? "NOT_APPLIED_BATCH_REFUSED"
                                                         : "REFUSED";
            }
            emit(outTsv, rows);
            emitJson(outJson, mode, projectPath, spec, manifestPath, manifestSha,
                manifestRaw.length, rows, verbs, mutableColumns,
                nowFunctions, nowInstructions, nowReferences, nowDefinedData,
                nowUndefinedData, nowBookmarks, functionCount(),
                listing.getNumInstructions(), referenceCount(),
                listing.getNumDefinedData(), undefinedDataCount(),
                bookmarkCount(), null, false);
            println("COHORT_NO_MUTATION_PERFORMED");
            return;
        }
        println("COHORT_GATE allNonMutatingGatesPassed=true rows=" + rows.size()
            + " firstWriteMayNowProceed=true");
        if (planOnly) {
            println("COHORT_PLAN_MODE banner=never-commits commit=IMPOSSIBLE"
                + " allGates=ENFORCED note=db_file_version_still_advances");
        }
        if (relax) {
            println("COHORT_PROBE_MODE banner=adverse-refusal-testing"
                + " manifestDigestPin=DISABLED rowCountPin=DISABLED"
                + " postCensusPin=DISABLED otherGates=ENFORCED commit=IMPOSSIBLE");
        }
        if (faultMode) {
            println("COHORT_FAULT_MODE banner=deliberate-self-sabotage"
                + " allPins=ENFORCED allGates=ENFORCED commit=IMPOSSIBLE fault="
                + mode);
        }

        // =============================== MUTATION PHASES ====================
        String collateral = null;
        writesAttempted = true;
        int tx = currentProgram.startTransaction(FRAMEWORK + ":" + cohortId + ":" + mode);
        boolean commit = false;
        try {
            // -- PHASE A: bounded classification (disassemble + clear) -------
            if (verbs.contains(V_DISASSEMBLE) || verbs.contains(V_CLEAR)) {
                for (Row row : rows) {
                    if (row.added == null) {
                        continue;
                    }
                    if (faultPrecedent) {
                        precedentClearFault(row);
                    }
                    classify(row, verbs.contains(V_CLEAR), faultPrecedent,
                             faultPrecedent);
                    censusRow(row, false);
                    row.stillUndefined = rangesText(undefinedIn(row.added));
                }
                injectFaults(rows, spec, listing, textSet, admitted, faultExtraClear,
                    faultClearEscape, faultStrand, faultEscape);
                gateClassification(rows, spec, admitted, preInstrStarts,
                    preRefsInAdmitted, nowInstructions, nowReferences,
                    manifestIsPinned, relax, listing);
            }

            // -- PHASE B: bounded bookmark hygiene ---------------------------
            List<String> removedBookmarks = new ArrayList<>();
            if (verbs.contains(V_BOOKMARK)) {
                gateBookmarks(spec, admitted, bm, preBookmarkList, removedBookmarks,
                    relax);
            }

            // -- PHASE C: setBody --------------------------------------------
            if (verbs.contains(V_SET_BODY) && failures.isEmpty()) {
                for (Row row : rows) {
                    if (row.proposed == null) {
                        continue;
                    }
                    Function fn = fm.getFunctionAt(row.entry);
                    try {
                        fn.setBody(row.proposed);
                        row.postRanges = rangesText(fn.getBody());
                        row.postBytes = fn.getBody().getNumAddresses();
                        row.verdict = bodyDigest(fn.getBody())
                                .equals(bodyDigest(row.proposed))
                            ? "APPLIED" : "APPLY_MISMATCH";
                    } catch (Exception exc) {
                        row.verdict = "APPLY_THREW:" + exc.getClass().getSimpleName();
                        fail(row, "setBody threw " + exc);
                    }
                    if (!"APPLIED".equals(row.verdict)) {
                        fail(row, "in-process verify failed: " + row.verdict);
                    }
                }
            }

            // -- PHASE D: setName --------------------------------------------
            if (verbs.contains(V_SET_NAME) && failures.isEmpty()) {
                for (Row row : rows) {
                    try {
                        if ("SYMBOL:Label".equals(row.liveKind)) {
                            Symbol s = currentProgram.getSymbolTable()
                                    .getPrimarySymbol(row.entry);
                            s.setName(row.get("proposedName"), SourceType.USER_DEFINED);
                        } else {
                            Function f = fm.getFunctionAt(row.entry);
                            f.setName(row.get("proposedName"), SourceType.USER_DEFINED);
                        }
                        row.verdict = "APPLIED";
                    } catch (Exception exc) {
                        row.verdict = "APPLY_THREW:" + exc.getClass().getSimpleName();
                        fail(row, "setName threw " + exc);
                    }
                }
            }

            // -- PHASE E: setPrototype ---------------------------------------
            if (verbs.contains(V_SET_PROTOTYPE) && failures.isEmpty()) {
                for (Row row : rows) {
                    try {
                        row.rendered = applyPrototype(row);
                        row.verdict = row.rendered.equals(row.get("proposedSignature"))
                            ? "APPLIED" : "APPLY_MISMATCH";
                    } catch (Exception exc) {
                        row.verdict = "APPLY_THREW:" + exc.getClass().getSimpleName();
                        fail(row, "updateFunction threw " + exc);
                    }
                    if (!"APPLIED".equals(row.verdict)) {
                        fail(row, "rendered prototype expected ["
                            + row.get("proposedSignature") + "] actual ["
                            + row.rendered + "]");
                    }
                }
            }

            // -- PHASE F: setDataPointer ------------------------------------
            if (verbs.contains(V_SET_DATA_POINTER) && failures.isEmpty()) {
                for (Row row : rows) {
                    if (!"DATA:POINTER".equals(row.liveKind)) {
                        continue;
                    }
                    try {
                        listing.createData(row.entry,
                            new PointerDataType(
                                ghidra.program.model.data.VoidDataType.dataType));
                        currentProgram.getSymbolTable().createLabel(
                            row.entry, row.get("proposedLabel"),
                            SourceType.USER_DEFINED);
                        row.verdict = "APPLIED";
                    } catch (Exception exc) {
                        row.verdict = "APPLY_THREW:" + exc.getClass().getSimpleName();
                        fail(row, "setDataPointer threw " + exc);
                    }
                }
            }

            // -- POST gates --------------------------------------------------
            gatePostRows(rows, spec, verbs, fm, readback);
            if (verbs.contains(V_SET_NAME)) {
                gateNamePost(rows, preOtherHolders);
            }
            collateral = collateralProof(rows, spec, verbs, mutableColumns,
                preFrozen, preSyms, preBookmarkList, preDefinedData, preMemory,
                admitted, removedBookmarks, relax);
            gateMetrics(spec, "POST", "post", functionCount(),
                listing.getNumInstructions(), referenceCount(),
                listing.getNumDefinedData(), undefinedDataCount(),
                bookmarkCount(), relax);
            if (!relax) {
                gatePostDigests(spec);
            }

            // A plan run and every fault run must be structurally unable to
            // commit even if some future edit made every gate miss them.
            commit = failures.isEmpty() && !planOnly && !faultMode;
            if (faultMode && failures.isEmpty()) {
                println("COHORT_FAULT_UNDETECTED banner=NO-GATE-FIRED"
                    + " this_is_a_test_failure=true");
            }
        } finally {
            currentProgram.endTransaction(tx, commit);
        }
        println("COHORT_REVERSIBILITY inProcessRollback=" + IN_PROCESS_ROLLBACK
            + " recovery=" + REVERSIBILITY
            + " note=this_framework_never_claims_transaction_level_atomicity");
        if (collateral != null) {
            println("COHORT_COLLATERAL " + collateral);
        }
        emit(outTsv, rows);
        emitJson(outJson, mode, projectPath, spec, manifestPath, manifestSha,
            manifestRaw.length, rows, verbs, mutableColumns,
            nowFunctions, nowInstructions, nowReferences, nowDefinedData,
            nowUndefinedData, nowBookmarks, functionCount(),
            listing.getNumInstructions(), referenceCount(),
            listing.getNumDefinedData(), undefinedDataCount(), bookmarkCount(),
            collateral, commit);
        report(mode, rows.size());
        if (!failures.isEmpty()) {
            println("COHORT_NO_COMMIT_PERFORMED recovery=" + REVERSIBILITY);
        }
    }

    // ======================================================= gate bodies ===

    private void checkVerbColumnBinding(Spec spec, Set<String> verbs) {
        // Each optional column belongs to exactly one verb.  Binding a column a
        // non-declared verb owns is a refusal: it is the only way a cohort
        // could ask for a mutation it did not declare.
        Map<String, String> owner = new LinkedHashMap<>();
        owner.put("col.currentName", V_SET_NAME);
        owner.put("col.proposedName", V_SET_NAME);
        owner.put("col.currentRanges", V_SET_BODY);
        owner.put("col.proposedRanges", V_SET_BODY);
        owner.put("col.terminatorVa", V_SET_BODY);
        owner.put("col.terminatorBytes", V_SET_BODY);
        owner.put("col.deltaBytes", V_SET_BODY);
        owner.put("col.byteProof", V_SET_BODY);
        owner.put("col.currentSignature", V_SET_PROTOTYPE);
        owner.put("col.currentSignatureSha256", V_SET_PROTOTYPE);
        owner.put("col.proposedSignature", V_SET_PROTOTYPE);
        owner.put("col.returnType", V_SET_PROTOTYPE);
        owner.put("col.paramSpec", V_SET_PROTOTYPE);
        owner.put("col.arity", V_SET_PROTOTYPE);
        owner.put("col.arityBytes", V_SET_PROTOTYPE);
        owner.put("col.varArgs", V_SET_PROTOTYPE);
        owner.put("col.colName", V_SET_DATA_POINTER);
        owner.put("col.dwordValue", V_SET_DATA_POINTER);
        owner.put("col.confidence", V_SET_DATA_POINTER);
        owner.put("col.colAddr", V_SET_DATA_POINTER);
        owner.put("col.proposedLabel", V_SET_DATA_POINTER);
        for (Map.Entry<String, String> e : owner.entrySet()) {
            if (spec.has(e.getKey()) && !verbs.contains(e.getValue())) {
                fail("VERB NOT DECLARED: the spec binds " + e.getKey()
                    + " but never declares verb " + e.getValue()
                    + "; this framework refuses an undeclared mutation");
            }
        }
        // required bindings for each declared verb
        if (verbs.contains(V_SET_NAME)) {
            requireBinding(spec, "col.currentName", V_SET_NAME);
            requireBinding(spec, "col.proposedName", V_SET_NAME);
        }
        if (verbs.contains(V_SET_BODY)) {
            requireBinding(spec, "col.currentRanges", V_SET_BODY);
            requireBinding(spec, "col.proposedRanges", V_SET_BODY);
        }
        if (verbs.contains(V_SET_PROTOTYPE)) {
            requireBinding(spec, "col.currentSignature", V_SET_PROTOTYPE);
            requireBinding(spec, "col.proposedSignature", V_SET_PROTOTYPE);
            requireBinding(spec, "col.returnType", V_SET_PROTOTYPE);
            requireBinding(spec, "col.paramSpec", V_SET_PROTOTYPE);
            requireBinding(spec, "col.callingConvention", V_SET_PROTOTYPE);
            // col.varArgs is DELIBERATELY NOT REQUIRED.  An absent binding is the
            // PRESERVE default, and it additionally keeps varArgs frozen for
            // every row.  Requiring it would force every future prototype cohort
            // to restate a value it has no evidence about.
        }
        if (verbs.contains(V_SET_DATA_POINTER)) {
            requireBinding(spec, "col.colName", V_SET_DATA_POINTER);
            requireBinding(spec, "col.dwordValue", V_SET_DATA_POINTER);
            requireBinding(spec, "col.proposedLabel", V_SET_DATA_POINTER);
        }
        if (verbs.contains(V_CLEAR) && !verbs.contains(V_DISASSEMBLE)) {
            fail("VERB DEPENDENCY: CLEAR_BOUNDED without DISASSEMBLE_BOUNDED "
                + "would strand admitted bytes");
        }
    }

    private void requireBinding(Spec spec, String key, String verb) {
        if (!spec.has(key)) {
            fail("SPEC declares verb " + verb + " but does not bind " + key);
        }
    }

    private Map<String, Integer> columnBinding(Spec spec, String[] headerCells) {
        Map<String, Integer> binding = new LinkedHashMap<>();
        for (String key : KNOWN_SPEC_KEYS) {
            if (!key.startsWith("col.") || !spec.has(key)) {
                continue;
            }
            String logical = key.substring(4);
            String want = spec.opt(key, "");
            int at = -1;
            for (int i = 0; i < headerCells.length; i++) {
                if (headerCells[i].equals(want)) {
                    at = i;
                    break;
                }
            }
            if (at < 0) {
                fail("SPEC binds " + key + " to manifest column [" + want
                    + "] which the header does not contain");
                continue;
            }
            binding.put(logical, at);
        }
        if (!binding.containsKey("addr")) {
            fail("SPEC must bind col.addr");
        }
        return binding;
    }

    private void gateIdentity(Spec spec) {
        String md5 = String.valueOf(currentProgram.getExecutableMD5())
                .toLowerCase(Locale.ROOT);
        String sha = String.valueOf(currentProgram.getExecutableSHA256())
                .toLowerCase(Locale.ROOT);
        if (!spec.opt("programName", "").equals(currentProgram.getName())) {
            fail("program name expected [" + spec.opt("programName", "")
                + "] actual [" + currentProgram.getName() + "]");
        }
        if (!spec.opt("programMd5", "").equalsIgnoreCase(md5)) {
            fail("program md5 expected [" + spec.opt("programMd5", "")
                + "] actual [" + md5 + "]");
        }
        if (!spec.opt("programSha256", "").equalsIgnoreCase(sha)) {
            fail("program sha256 expected [" + spec.opt("programSha256", "")
                + "] actual [" + sha + "]");
        }
        if (!spec.opt("imageBase", "").equals(currentProgram.getImageBase().toString())) {
            fail("program imageBase expected [" + spec.opt("imageBase", "")
                + "] actual [" + currentProgram.getImageBase() + "]");
        }
        if (!spec.opt("language", "").equals(
                currentProgram.getLanguageID().getIdAsString())) {
            fail("program language expected [" + spec.opt("language", "")
                + "] actual [" + currentProgram.getLanguageID() + "]");
        }
        if (!spec.opt("compilerSpec", "").equals(
                currentProgram.getCompilerSpec().getCompilerSpecID().getIdAsString())) {
            fail("program compilerSpec expected [" + spec.opt("compilerSpec", "")
                + "] actual ["
                + currentProgram.getCompilerSpec().getCompilerSpecID() + "]");
        }
        if (spec.has("textBlock")) {
            MemoryBlock text = currentProgram.getMemory()
                    .getBlock(spec.opt("textBlock", ".text"));
            long wantStart = Long.parseLong(spec.opt("textStart", "0"), 16);
            long wantEnd = Long.parseLong(spec.opt("textEnd", "0"), 16);
            if (text == null || text.getStart().getOffset() != wantStart
                    || text.getEnd().getOffset() != wantEnd || !text.isExecute()) {
                fail("text block geometry");
            }
        }
        println("COHORT_GATE identity=ok sha256=" + sha);
    }

    private void gateMetrics(Spec spec, String label, String prefix,
            long functions, long instructions, long references, long definedData,
            long undefinedData, long bookmarks, boolean relaxed) {
        if (relaxed) {
            return;
        }
        // The refusal texts are written out in full rather than composed, so
        // that a grep for any one of them finds the gate that emits it.  The
        // gate inventory in tools/ghidra_cohort_framework_tests.py matches
        // these exact strings.
        if ("PRE".equals(label)) {
            checkMetric(spec, "preFunctions", "PRE function count", functions);
            checkMetric(spec, "preInstructions", "PRE instruction count",
                instructions);
            checkMetric(spec, "preReferences", "PRE reference count", references);
            checkMetric(spec, "preDefinedData", "PRE definedData count",
                definedData);
            checkMetric(spec, "preUndefinedData", "PRE undefinedData count",
                undefinedData);
            checkMetric(spec, "preBookmarks", "PRE bookmark count", bookmarks);
        } else {
            checkMetric(spec, "postFunctions", "POST function count", functions);
            checkMetric(spec, "postInstructions", "POST instruction count",
                instructions);
            checkMetric(spec, "postReferences", "POST reference count",
                references);
            checkMetric(spec, "postDefinedData", "POST definedData count",
                definedData);
            checkMetric(spec, "postUndefinedData", "POST undefinedData count",
                undefinedData);
            checkMetric(spec, "postBookmarks", "POST bookmark count", bookmarks);
        }
        if (!"PRE".equals(label) && !"POST".equals(label)) {
            fail("metric label must be PRE or POST, not " + label);
        }
    }

    private void gatePostDigests(Spec spec) throws Exception {
        if (spec.has("postFunctionNameDigest")) {
            String got = digestOfMap(nameDigestForm());
            if (!spec.opt("postFunctionNameDigest", "").equals(got)) {
                fail("POST function NAME digest " + got + " != pinned "
                    + spec.opt("postFunctionNameDigest", ""));
            }
        }
        if (spec.has("postFunctionBodyDigest")) {
            String got = digestOfMap(bodyDigestForm());
            if (!spec.opt("postFunctionBodyDigest", "").equals(got)) {
                fail("POST function BODY digest " + got + " != pinned "
                    + spec.opt("postFunctionBodyDigest", ""));
            }
        }
        if (spec.has("postFrozenDigest")) {
            String got = digestOfMap(frozenCensus());
            if (!spec.opt("postFrozenDigest", "").equals(got)) {
                fail("POST frozen-census digest " + got + " != pinned "
                    + spec.opt("postFrozenDigest", ""));
            }
        }
    }

    private void checkMetric(Spec spec, String key, String label, long actual) {
        if (!spec.has(key)) {
            return;
        }
        long want = spec.num(key, Long.MIN_VALUE);
        if (want != actual) {
            fail(label + " " + actual + " != " + want);
        }
    }

    private void gatePrototypeRow(Row row, Function f, boolean readback)
            throws Exception {
        String live = f.getSignature().getPrototypeString(true);
        if (row.cells.containsKey("liveName")
                && !row.get("liveName").equals(f.getName())) {
            fail(row, "CURRENT name expected [" + row.get("liveName")
                + "] actual [" + f.getName() + "]");
        }
        String wantSig = readback ? row.get("proposedSignature")
                                  : row.get("currentSignature");
        if (!wantSig.equals(live)) {
            if (readback) {
                fail(row, "READBACK signature expected [" + wantSig
                    + "] actual [" + live + "]");
            } else {
                fail(row, "CURRENT signature expected [" + wantSig
                    + "] actual [" + live + "]");
            }
        }
        if (!readback && row.cells.containsKey("currentSignatureSha256")) {
            String got = sha256(live);
            if (!row.get("currentSignatureSha256").equalsIgnoreCase(got)) {
                fail(row, "CURRENT signature sha256 expected ["
                    + row.get("currentSignatureSha256") + "] actual [" + got + "]");
            }
        }
        if (row.cells.containsKey("callingConvention")
                && !row.get("callingConvention").equals(f.getCallingConventionName())) {
            fail(row, "CURRENT calling convention expected ["
                + row.get("callingConvention") + "] actual ["
                + f.getCallingConventionName() + "]");
        }
        if (f.hasCustomVariableStorage()) {
            fail(row, "uses custom variable storage; this framework only "
                + "installs dynamic storage");
        }
        if (f.isThunk()) {
            fail(row, "is a thunk; a thunk's prototype follows its target");
        }
        if (f.isExternal()) {
            fail(row, "is external");
        }
        // -- varargs: manifest-driven, PRESERVE by default --------------------
        // The PRE value is measured here, before any write, so a PRESERVE row is
        // graded against the state that actually existed rather than a literal.
        row.preVarArgs = f.hasVarArgs();
        row.varArgsWanted = null;
        String varArgsCell = row.get("varArgs").trim();
        if (row.cells.containsKey("varArgs") && !varArgsCell.isEmpty()) {
            if ("true".equals(varArgsCell)) {
                row.varArgsWanted = Boolean.TRUE;
            } else if ("false".equals(varArgsCell)) {
                row.varArgsWanted = Boolean.FALSE;
            } else {
                fail(row, "illegal varargs value [" + varArgsCell + "]; the "
                    + "varargs column is true, false, or EMPTY for preserve");
            }
        }
        // The proposed prototype string and the varargs decision must agree, so a
        // row cannot ask for varargs while pinning a non-variadic rendering (or
        // the reverse) and then fail confusingly at the rendered-prototype gate.
        // Ghidra renders a variadic prototype with a ", ...)" tail - measured on
        // db.18622, where all 10 varargs=true functions render that way.
        if (!readback) {
            boolean resolved = row.varArgsWanted == null
                ? row.preVarArgs : row.varArgsWanted.booleanValue();
            boolean proposedIsVariadic =
                row.get("proposedSignature").endsWith(", ...)");
            if (resolved != proposedIsVariadic) {
                fail(row, "varargs/proposedSignature disagree: the varargs "
                    + "decision resolves to [" + resolved + "] but the proposed "
                    + "signature " + (proposedIsVariadic
                        ? "ends with a ', ...)' tail" : "has no ', ...)' tail"));
            }
        }
        // paramSpec / arity structure
        row.params.clear();
        int nstack = 0;
        int nreg = 0;
        try {
            row.arity = Integer.parseInt(row.get("arity"));
            row.arityBytes = Integer.parseInt(row.get("arityBytes"));
        } catch (NumberFormatException exc) {
            fail(row, "arity/arityBytes not numeric");
            return;
        }
        if (row.arityBytes != row.arity * 4) {
            fail(row, "arityBytes/arity mismatch " + row.arityBytes + " vs "
                + row.arity);
        }
        if (!LEGAL_TYPE.matcher(row.get("returnType")).matches()) {
            fail(row, "illegal return type [" + row.get("returnType") + "]");
        }
        String paramSpec = row.get("paramSpec");
        if (!paramSpec.isEmpty()) {
            for (String p : paramSpec.split(";")) {
                String[] fields = p.split(":", -1);
                if (fields.length != 4) {
                    fail(row, "paramSpec field count expected [4] actual ["
                        + fields.length + "]");
                    continue;
                }
                if (!LEGAL_TYPE.matcher(fields[1]).matches()) {
                    fail(row, "illegal param type [" + fields[1] + "]");
                }
                if (!LEGAL_PNAME.matcher(fields[2]).matches()) {
                    fail(row, "illegal param name [" + fields[2] + "]");
                }
                if (!fields[3].equals("auto") && !fields[3].equals("expl")) {
                    fail(row, "illegal param mode " + fields[3]);
                }
                if (fields[0].equals("STACK")) {
                    nstack++;
                } else {
                    nreg++;
                }
                row.params.add(fields);
            }
        }
        if (nstack != row.arity) {
            fail(row, "stack param count expected [" + row.arity + "] actual ["
                + nstack + "]");
        }
        if ("__fastcall".equals(row.get("callingConvention")) && nstack > 0
                && nreg < 2) {
            fail(row, "__fastcall with " + nreg + " register param(s) and "
                + nstack + " stack param(s) would let dynamic storage"
                + " fabricate an EDX argument");
        }
    }

    private void gateGeometryRow(Row row, Function fn, Spec spec,
            AddressSet textSet, AddressSet allProposed, AddressSet admitted,
            boolean readback, FunctionManager fm, Listing listing)
            throws Exception {
        row.subtype = row.get("subtype");
        row.current = parseRanges(row.get("currentRanges"));
        row.proposed = parseRanges(row.get("proposedRanges"));
        if (row.current == null || row.proposed == null) {
            fail(row, "unparseable range text");
            return;
        }
        if (!row.proposed.getMinAddress().equals(row.entry)) {
            fail(row, "proposed body does not start at the entry point");
        }
        if (textSet != null && !textSet.contains(row.proposed)) {
            fail(row, "proposed body leaves .text");
        }
        AddressSet dropped = new AddressSet(row.current);
        dropped.delete(row.proposed);
        if (!dropped.isEmpty()) {
            fail(row, "proposal DROPS currently owned bytes: " + rangesText(dropped));
        }
        row.added = new AddressSet(row.proposed);
        row.added.delete(row.current);
        if (row.cells.containsKey("deltaBytes")) {
            try {
                row.deltaBytes = Long.parseLong(row.get("deltaBytes"));
            } catch (NumberFormatException exc) {
                fail(row, "deltaBytes not numeric");
            }
            long delta = row.proposed.getNumAddresses() - row.current.getNumAddresses();
            if (row.deltaBytes != Long.MIN_VALUE && delta != row.deltaBytes) {
                fail(row, "deltaBytes " + row.deltaBytes + " != measured " + delta);
            }
        }
        if (row.added.isEmpty()) {
            fail(row, "proposal adds nothing");
        }
        AddressSet clash = new AddressSet(allProposed).intersect(row.proposed);
        if (!clash.isEmpty()) {
            fail(row, "target/target overlap at " + rangesText(clash));
        }
        allProposed.add(row.proposed);
        admitted.add(row.added);

        AddressSetView body = fn.getBody();
        AddressSet expectedNow = readback ? row.proposed : row.current;
        String expectedNowText = readback ? row.get("proposedRanges")
                                          : row.get("currentRanges");
        if (!bodyDigest(body).equals(bodyDigest(expectedNow))) {
            fail(row, (readback ? "READBACK STATE DRIFT: " : "CURRENT STATE DRIFT: ")
                + "replica=" + rangesText(body) + " manifest=" + expectedNowText);
        }

        if (row.cells.containsKey("terminatorBytes")
                && row.cells.containsKey("terminatorVa")) {
            String tbytes = row.get("terminatorBytes");
            byte[] want = new byte[tbytes.length() / 2];
            for (int i = 0; i < want.length; i++) {
                want[i] = (byte) Integer.parseInt(tbytes.substring(i * 2, i * 2 + 2), 16);
            }
            Address tva = toAddr(Long.parseLong(row.get("terminatorVa"), 16));
            byte[] got = new byte[want.length];
            try {
                currentProgram.getMemory().getBytes(tva, got);
            } catch (Exception exc) {
                Arrays.fill(got, (byte) 0);
                fail(row, "terminator unreadable at " + tva);
            }
            if (!Arrays.equals(want, got)) {
                fail(row, "terminator bytes differ: want=" + tbytes + " got=" + hex(got));
            }
            AddressSet termSet = new AddressSet(tva, tva.add(want.length - 1L));
            if (!row.proposed.contains(termSet)) {
                fail(row, "terminator not inside the proposed body");
            }
        }

        if (row.cells.containsKey("byteProof")) {
            AddressSet proofSet = new AddressSet();
            for (String segment : row.get("byteProof").split(" \\+ ")) {
                int eq = segment.indexOf('=');
                if (eq < 0) {
                    fail(row, "malformed byteProof segment");
                    continue;
                }
                String[] halves = segment.substring(0, eq).trim().split("-");
                Address lo = toAddr(Long.parseLong(halves[0].trim(), 16));
                Address hi = toAddr(Long.parseLong(halves[1].trim(), 16));
                proofSet.addRange(lo, hi);
                String hexPart = segment.substring(eq + 1).trim();
                int span = (int) (hi.getOffset() - lo.getOffset() + 1);
                byte[] actual = new byte[span];
                try {
                    currentProgram.getMemory().getBytes(lo, actual);
                } catch (Exception exc) {
                    fail(row, "byteProof range unreadable at " + lo);
                    continue;
                }
                String actualHex = hex(actual);
                int dots = hexPart.indexOf("..");
                boolean ok;
                if (dots >= 0) {
                    ok = actualHex.startsWith(hexPart.substring(0, dots))
                        && actualHex.endsWith(hexPart.substring(dots + 2));
                } else {
                    ok = actualHex.startsWith(hexPart);
                }
                if (!ok) {
                    fail(row, "byteProof does not reproduce at " + lo);
                }
            }
            if (!bodyDigest(proofSet).equals(bodyDigest(row.added))) {
                fail(row, "byteProof ranges " + rangesText(proofSet)
                    + " != added ranges " + rangesText(row.added));
            }
        }

        Address max = row.proposed.getMaxAddress();
        CodeUnit unit = listing.getCodeUnitContaining(max);
        if (unit != null && !unit.getMaxAddress().equals(max)) {
            fail(row, "proposal ENDS MID-INSTRUCTION inside " + unit.getMinAddress()
                + "-" + unit.getMaxAddress());
        }

        Iterator<Function> overlapping = fm.getFunctionsOverlapping(row.proposed);
        while (overlapping.hasNext()) {
            Function other = overlapping.next();
            if (!other.getEntryPoint().equals(row.entry)) {
                AddressSet hit = new AddressSet(other.getBody()).intersect(row.proposed);
                fail(row, "OVERLAPS existing function " + other.getName() + " @"
                    + other.getEntryPoint() + " at " + rangesText(hit));
            }
        }
        censusRow(row, true);
    }

    private void injectFaults(List<Row> rows, Spec spec, Listing listing,
            AddressSet textSet, AddressSet admitted, boolean faultExtraClear,
            boolean faultClearEscape, boolean faultStrand, boolean faultEscape) {
        String tableSubtype = spec.opt("tableSubtype", "INCLUDE_JUMP_OR_SEH_TABLE");
        if (faultExtraClear) {
            for (Row row : rows) {
                if (row.added == null || !tableSubtype.equals(row.subtype)) {
                    continue;
                }
                InstructionIterator it = listing.getInstructions(row.added, true);
                if (it.hasNext()) {
                    Instruction ins = it.next();
                    if (row.added.contains(ins.getMinAddress(), ins.getMaxAddress())) {
                        row.clearedKinds.add(ins.getMinAddress() + "-"
                            + ins.getMaxAddress() + "=INJECTED_FAULT");
                        row.cleared.addRange(ins.getMinAddress(), ins.getMaxAddress());
                        listing.clearCodeUnits(ins.getMinAddress(),
                            ins.getMaxAddress(), false);
                        censusRow(row, false);
                        println("COHORT_FAULT_INJECTED extraClearAt="
                            + ins.getMinAddress() + " row=" + row.addrText);
                        break;
                    }
                }
            }
        }
        if (faultClearEscape) {
            for (Row row : rows) {
                if (row.added == null) {
                    continue;
                }
                Address before;
                try {
                    before = row.added.getMinAddress().subtract(1);
                } catch (Exception exc) {
                    continue;
                }
                CodeUnit unit = listing.getCodeUnitContaining(before);
                if (unit == null || row.added.contains(unit.getMinAddress())) {
                    continue;
                }
                row.clearedKinds.add(unit.getMinAddress() + "-"
                    + unit.getMaxAddress() + "=INJECTED_FAULT_OUTSIDE");
                row.cleared.addRange(unit.getMinAddress(), unit.getMaxAddress());
                listing.clearCodeUnits(unit.getMinAddress(), unit.getMaxAddress(),
                    false);
                censusRow(row, false);
                println("COHORT_FAULT_INJECTED clearOutsideAdmittedAt="
                    + unit.getMinAddress() + " row=" + row.addrText);
                break;
            }
        }
        if (faultStrand) {
            for (Row row : rows) {
                if (row.added == null || row.preUndefBytes != 0
                        || row.preInstrCount < 2) {
                    continue;
                }
                InstructionIterator it = listing.getInstructions(row.added, true);
                while (it.hasNext()) {
                    Instruction ins = it.next();
                    if (!row.added.contains(ins.getMinAddress(), ins.getMaxAddress())) {
                        continue;
                    }
                    row.clearedKinds.add(ins.getMinAddress() + "-"
                        + ins.getMaxAddress() + "=STRANDED_FAULT");
                    row.cleared.addRange(ins.getMinAddress(), ins.getMaxAddress());
                    listing.clearCodeUnits(ins.getMinAddress(), ins.getMaxAddress(),
                        false);
                    censusRow(row, false);
                    row.stillUndefined = rangesText(undefinedIn(row.added));
                    println("COHORT_FAULT_INJECTED strandedAt=" + ins.getMinAddress()
                        + " row=" + row.addrText + " classified="
                        + row.preClassified() + "->" + row.postClassified());
                    break;
                }
                break;
            }
        }
        if (faultEscape && textSet != null) {
            AddressSet outside = new AddressSet(textSet);
            outside.delete(admitted);
            AddressSet undefOutside = undefinedIn(outside);
            if (!undefOutside.isEmpty()) {
                AddressSet seeds = new AddressSet();
                int n = 0;
                int branchSeeds = 0;
                for (AddressRange r : undefOutside) {
                    if (r.getLength() < 5) {
                        continue;
                    }
                    byte[] head = new byte[1];
                    try {
                        currentProgram.getMemory().getBytes(r.getMinAddress(), head);
                    } catch (Exception exc) {
                        continue;
                    }
                    int op = head[0] & 0xff;
                    if (op != 0xe8 && op != 0xe9) {
                        continue;
                    }
                    seeds.add(r.getMinAddress());
                    branchSeeds++;
                    if (++n >= 8) {
                        break;
                    }
                }
                for (AddressRange r : undefOutside) {
                    if (n >= 8) {
                        break;
                    }
                    seeds.add(r.getMinAddress());
                    n++;
                }
                Disassembler d = Disassembler.getDisassembler(currentProgram, monitor, null);
                d.disassemble(seeds, undefOutside, true);
                println("COHORT_FAULT_INJECTED escapeSeeds=" + n
                    + " rel32BranchSeeds=" + branchSeeds);
            }
        }
    }

    private void gateClassification(List<Row> rows, Spec spec, AddressSet admitted,
            List<String> preInstrStarts, List<String> preRefsInAdmitted,
            long preInstructions, long preReferences, boolean manifestIsPinned,
            boolean relaxed, Listing listing) throws Exception {
        String tableSubtype = spec.opt("tableSubtype", "INCLUDE_JUMP_OR_SEH_TABLE");
        long postAdmittedUndefined = 0;
        long clearedUnits = 0;
        long clearedBytes = 0;
        for (Row row : rows) {
            if (row.added == null) {
                continue;
            }
            postAdmittedUndefined += row.postUndefBytes;
            clearedUnits += row.clearedKinds.size();
            clearedBytes += row.cleared.getNumAddresses();
            if (row.postUndefBytes != 0) {
                fail(row, "UNCLASSIFIED BYTES REMAIN in the admitted body: "
                    + row.stillUndefined);
            }
            if (row.postClassified() < row.preClassified()) {
                fail(row, "CLASSIFIED-BYTE REGRESSION " + row.preClassified()
                    + " -> " + row.postClassified() + " (instr " + row.preInstrBytes
                    + "->" + row.postInstrBytes + ", data " + row.preDataBytes
                    + "->" + row.postDataBytes + ")");
            }
            if (!row.cleared.isEmpty() && !row.added.contains(row.cleared)) {
                AddressSet outside = new AddressSet(row.cleared);
                outside.delete(row.added);
                fail(row, "CLEAR ESCAPED the admitted range at " + rangesText(outside));
            }
            if (tableSubtype.equals(row.subtype)) {
                if (!row.cleared.isEmpty()) {
                    fail(row, "JUMP/SEH TABLE ROW WAS CLEARED: "
                        + rangesText(row.cleared));
                }
                if (row.postDataBytes != row.preDataBytes) {
                    fail(row, "JUMP/SEH TABLE DATA CHANGED " + row.preDataBytes
                        + " -> " + row.postDataBytes);
                }
            }
            if (row.preUndefBytes == 0) {
                if (!row.cleared.isEmpty()
                        || row.postInstrCount != row.preInstrCount
                        || row.postClassified() != row.preClassified()) {
                    fail(row, "PRECONDITION ROW WAS MUTATED: cleared="
                        + rangesText(row.cleared) + " instrCount "
                        + row.preInstrCount + "->" + row.postInstrCount);
                }
            }
            Address max = row.proposed.getMaxAddress();
            CodeUnit unit = listing.getCodeUnitContaining(max);
            if (unit != null && !unit.getMaxAddress().equals(max)) {
                fail(row, "POST-CLASSIFICATION the proposal ENDS MID-INSTRUCTION "
                    + "inside " + unit.getMinAddress() + "-" + unit.getMaxAddress());
            }
            AddressSet cover = instructionCoverage(row.added);
            AddressSet escape = new AddressSet(cover);
            escape.delete(row.proposed);
            if (!escape.isEmpty()) {
                row.escaped = rangesText(escape);
                fail(row, "INSTRUCTION ESCAPED the proposed body at " + row.escaped);
            }
        }
        if (!relaxed) {
            if (postAdmittedUndefined != 0) {
                fail("admitted bytes still undefined: " + postAdmittedUndefined);
            }
            if (spec.has("clearedUnits")
                    && clearedUnits != spec.num("clearedUnits", -1)) {
                fail("cleared unit count " + clearedUnits + " != "
                    + spec.num("clearedUnits", -1));
            }
            if (spec.has("clearedBytes")
                    && clearedBytes != spec.num("clearedBytes", -1)) {
                fail("cleared byte count " + clearedBytes + " != "
                    + spec.num("clearedBytes", -1));
            }
        }
        // the derived clear set must equal the pinned plan exactly
        if (manifestIsPinned && spec.has("clearPlan")) {
            List<String> derived = new ArrayList<>();
            for (Row row : rows) {
                if (!row.cleared.isEmpty()) {
                    derived.add(row.addrText + "\t" + rangesText(row.cleared));
                }
            }
            List<String> pinned = new ArrayList<>();
            for (String p : spec.all("clearPlan")) {
                pinned.add(p.replace('|', '\t'));
            }
            if (!derived.equals(pinned)) {
                fail("CLEAR PLAN MISMATCH derived=" + derived + " pinned=" + pinned);
            }
        }
        long midInstructions = listing.getNumInstructions();
        long midReferences = referenceCount();
        List<String> postInstrStarts = instructionStartsIn(admitted);
        List<String> postRefsInAdmitted = referencesFromWithin(admitted);
        long admittedInstrDelta = postInstrStarts.size() - preInstrStarts.size();
        long admittedRefDelta = postRefsInAdmitted.size() - preRefsInAdmitted.size();
        if (midInstructions - preInstructions != admittedInstrDelta) {
            fail("INSTRUCTION ESCAPE: program delta "
                + (midInstructions - preInstructions) + " != admitted delta "
                + admittedInstrDelta);
        }
        if (midReferences - preReferences != admittedRefDelta) {
            fail("REFERENCE ESCAPE: program delta "
                + (midReferences - preReferences) + " != admitted-sourced delta "
                + admittedRefDelta);
        }
    }

    private void gateBookmarks(Spec spec, AddressSet admitted, BookmarkManager bm,
            List<String> preBookmarkList, List<String> removed, boolean relaxed) {
        String type = spec.opt("bookmarkType", "Error");
        String category = spec.opt("bookmarkCategory", "Bad Instruction");
        TreeSet<String> stale = new TreeSet<>(spec.all("staleBookmark"));
        for (String key : stale) {
            Address at = toAddr(Long.parseLong(key, 16));
            if (!admitted.contains(at)) {
                fail("STALE BOOKMARK OUTSIDE the admitted ranges at " + at);
                continue;
            }
            if (!undefinedIn(new AddressSet(at, at)).isEmpty()) {
                fail("STALE BOOKMARK at an unclassified byte " + at);
                continue;
            }
            Bookmark mark = bm.getBookmark(at, type, category);
            if (mark == null) {
                if (!relaxed) {
                    fail("PINNED STALE BOOKMARK ABSENT at " + at);
                }
                continue;
            }
            bm.removeBookmark(mark);
            removed.add(at.toString());
        }
        List<String> postBookmarkList = bookmarkCensus();
        List<String> gained = new ArrayList<>(postBookmarkList);
        gained.removeAll(preBookmarkList);
        List<String> lost = new ArrayList<>(preBookmarkList);
        lost.removeAll(postBookmarkList);
        for (String s : gained) {
            Address at = toAddr(Long.parseLong(s.substring(0, s.indexOf('\t')), 16));
            if (!admitted.contains(at)) {
                fail("BOOKMARK CREATED OUTSIDE the admitted ranges at " + at);
            }
        }
        for (String s : lost) {
            Address at = toAddr(Long.parseLong(s.substring(0, s.indexOf('\t')), 16));
            if (!admitted.contains(at)) {
                fail("BOOKMARK REMOVED OUTSIDE the admitted ranges at " + at);
            }
        }
        if (!relaxed && !gained.isEmpty()) {
            fail("BOOKMARKS SURVIVED hygiene: " + gained);
        }
        notes.add("bookmarksRemoved=" + removed.size() + " " + removed);
    }

    private void gatePostRows(List<Row> rows, Spec spec, Set<String> verbs,
            FunctionManager fm, boolean readback) throws Exception {
        for (Row row : rows) {
            if (row.entry == null) {
                continue;
            }
            if (verbs.contains(V_SET_NAME)) {
                String live = "SYMBOL:Label".equals(row.liveKind)
                    ? currentProgram.getSymbolTable().getPrimarySymbol(row.entry).getName()
                    : fm.getFunctionAt(row.entry).getName();
                if (!row.get("proposedName").equals(live)) {
                    fail(row, "POST name expected [" + row.get("proposedName")
                        + "] actual [" + live + "]");
                }
            }
            Function f = fm.getFunctionAt(row.entry);
            if (f == null) {
                continue;
            }
            if (verbs.contains(V_SET_BODY) && row.proposed != null) {
                if (!bodyDigest(f.getBody()).equals(bodyDigest(row.proposed))) {
                    fail(row, "POST body expected [" + row.get("proposedRanges")
                        + "] actual [" + rangesText(f.getBody()) + "]");
                }
                if (!undefinedIn(row.added).isEmpty()) {
                    fail(row, "POST admitted bytes still undefined: "
                        + rangesText(undefinedIn(row.added)));
                }
            }
            if (verbs.contains(V_SET_PROTOTYPE)) {
                String live = f.getSignature().getPrototypeString(true);
                if (!row.get("proposedSignature").equals(live)) {
                    fail(row, "POST signature expected ["
                        + row.get("proposedSignature") + "] actual [" + live + "]");
                }
                if (!row.get("callingConvention").equals(f.getCallingConventionName())) {
                    fail(row, "POST calling convention expected ["
                        + row.get("callingConvention") + "] actual ["
                        + f.getCallingConventionName() + "]");
                }
                if (row.cells.containsKey("liveName")
                        && !row.get("liveName").equals(f.getName())) {
                    fail(row, "POST name expected [" + row.get("liveName")
                        + "] actual [" + f.getName() + "]");
                }
                if (row.arityBytes != f.getStackFrame().getParameterSize()) {
                    fail(row, "POST stack parameter bytes expected ["
                        + row.arityBytes + "] actual ["
                        + f.getStackFrame().getParameterSize() + "]");
                }
                // Compared against the MANIFEST decision, never a literal.  For a
                // PRESERVE row the expectation is the PRE value measured before
                // the write, so an accidental strip is a hard failure here even
                // though the manifest said nothing.
                boolean wantVarArgs = row.varArgsWanted == null
                    ? row.preVarArgs : row.varArgsWanted.booleanValue();
                row.varArgsPost = String.valueOf(f.hasVarArgs());
                if (f.hasVarArgs() != wantVarArgs) {
                    fail(row, "POST varargs expected [" + wantVarArgs
                        + "] actual [" + f.hasVarArgs() + "]"
                        + (row.varArgsWanted == null
                            ? " (PRESERVE: the PRE value)" : ""));
                }
                if (!"USER_DEFINED".equals(f.getSignatureSource().toString())) {
                    fail(row, "POST signature source expected [USER_DEFINED] "
                        + "actual [" + f.getSignatureSource() + "]");
                }
                if (f.hasCustomVariableStorage()) {
                    fail(row, "POST uses custom variable storage");
                }
                int stack = 0;
                for (Parameter p : f.getParameters()) {
                    if (p.isStackVariable()) {
                        stack++;
                    }
                }
                if (stack != row.arity) {
                    fail(row, "POST stack parameter count expected [" + row.arity
                        + "] actual [" + stack + "]");
                }
            }
        }
    }

    private void gateNamePost(List<Row> rows,
            Map<String, List<String>> preOtherHolders) {
        Map<String, List<String>> idx = nameIndex();
        for (Row row : rows) {
            if (row.entry == null) {
                continue;
            }
            String self = row.addrText.substring(2);
            List<String> hits = idx.get(row.get("proposedName"));
            if (hits == null || hits.size() != 1 || !hits.get(0).equals(self)) {
                fail(row, "POST census for '" + row.get("proposedName")
                    + "' is not exactly one symbol at " + row.addrText + " (got "
                    + hits + ")");
            }
            List<String> old = idx.get(row.get("currentName"));
            List<String> stillThere = old == null ? new ArrayList<String>()
                                                  : new ArrayList<>(old);
            Collections.sort(stillThere);
            if (stillThere.contains(self)) {
                fail(row, "POST: the PRE name '" + row.get("currentName")
                    + "' is still held at " + row.addrText);
            }
            List<String> expected = preOtherHolders.get(row.addrText);
            if (expected == null || !expected.equals(stillThere)) {
                fail(row, "POST: other holders of the PRE name '"
                    + row.get("currentName") + "' changed: expected " + expected
                    + " actual " + stillThere);
            }
        }
    }

    private void gateReadback(List<Row> rows, Spec spec, Set<String> verbs,
            FunctionManager fm, Map<String, List<String>> idx) throws Exception {
        for (Row row : rows) {
            if (row.entry == null) {
                continue;
            }
            if (verbs.contains(V_SET_NAME)) {
                String self = row.addrText.substring(2);
                List<String> hits = idx.get(row.get("proposedName"));
                if (hits == null || hits.size() != 1 || !hits.get(0).equals(self)) {
                    fail(row, "READBACK census for '" + row.get("proposedName")
                        + "' is not exactly one symbol at " + row.addrText
                        + " (got " + hits + ")");
                }
                List<String> old = idx.get(row.get("currentName"));
                if (old != null && old.contains(self)) {
                    fail(row, "READBACK: the PRE name '" + row.get("currentName")
                        + "' is still held at " + row.addrText);
                }
            }
            Function f = fm.getFunctionAt(row.entry);
            if (f == null) {
                continue;
            }
            if (verbs.contains(V_SET_BODY) && row.proposed != null) {
                row.postRanges = rangesText(f.getBody());
                row.postBytes = f.getBody().getNumAddresses();
                censusRow(row, false);
                row.stillUndefined = rangesText(undefinedIn(row.added));
                if (!bodyDigest(f.getBody()).equals(bodyDigest(row.proposed))) {
                    fail(row, "READBACK RANGE MISMATCH");
                }
                if (row.postUndefBytes != 0) {
                    fail(row, "READBACK UNCLASSIFIED BYTES: " + row.stillUndefined);
                }
            }
            if (verbs.contains(V_SET_PROTOTYPE)) {
                if (row.arityBytes != f.getStackFrame().getParameterSize()) {
                    fail(row, "READBACK stack parameter bytes expected ["
                        + row.arityBytes + "] actual ["
                        + f.getStackFrame().getParameterSize() + "]");
                }
                // A separate readback process cannot know the PRE state, so an
                // explicit manifest value is asserted directly and a PRESERVE row
                // is proven by the full prototype-string equality gate above:
                // Ghidra renders varargs as the ", ...)" tail, so a stripped
                // varargs cannot satisfy READBACK signature expected [...].
                row.varArgsPost = String.valueOf(f.hasVarArgs());
                if (row.varArgsWanted != null
                        && f.hasVarArgs() != row.varArgsWanted.booleanValue()) {
                    fail(row, "READBACK varargs expected [" + row.varArgsWanted
                        + "] actual [" + f.hasVarArgs() + "]");
                }
                if (!"USER_DEFINED".equals(f.getSignatureSource().toString())) {
                    fail(row, "READBACK signature source expected [USER_DEFINED] "
                        + "actual [" + f.getSignatureSource() + "]");
                }
                if (f.hasCustomVariableStorage()) {
                    fail(row, "READBACK uses custom variable storage");
                }
            }
        }
        println("COHORT_GATE readbackRows=ok rows=" + rows.size());
    }

    private String applyPrototype(Row row) throws Exception {
        Function f = currentProgram.getFunctionManager().getFunctionAt(row.entry);
        List<Variable> params = new ArrayList<>();
        for (String[] p : row.params) {
            if (p[3].equals("auto")) {
                continue;   // Ghidra regenerates auto params from the convention
            }
            params.add(new ParameterImpl(p[2], resolveType(p[1], row), currentProgram));
        }
        f.updateFunction(row.get("callingConvention"),
            new ReturnParameterImpl(resolveType(row.get("returnType"), row),
                currentProgram),
            params, FunctionUpdateType.DYNAMIC_STORAGE_FORMAL_PARAMS, true,
            SourceType.USER_DEFINED);
        // The varargs decision comes from the manifest; a row that asked for
        // nothing is restored to the value measured before this write, so
        // updateFunction cannot silently drop it either.  This is the only
        // setVarArgs call in the framework.
        boolean want = row.varArgsWanted == null
            ? row.preVarArgs : row.varArgsWanted.booleanValue();
        if (faultVarArgsFlip) {
            want = !want;    // probe-fault-varargsflip; can never commit
        }
        if (f.hasVarArgs() != want) {
            f.setVarArgs(want);
        }
        return f.getSignature().getPrototypeString(true);
    }

    // ======================================================== collateral ===

    private String collateralProof(List<Row> rows, Spec spec, Set<String> verbs,
            Set<String> mutableColumns, TreeMap<String, String> preFrozen,
            List<String> preSyms, List<String> preBookmarks,
            List<String> preDefinedData, String preMemory, AddressSet admitted,
            List<String> removedBookmarks, boolean relaxed) throws Exception {
        TreeMap<String, String> postFrozen = frozenCensus();
        if (!preFrozen.keySet().equals(postFrozen.keySet())) {
            Set<String> created = new LinkedHashSet<>(postFrozen.keySet());
            created.removeAll(preFrozen.keySet());
            Set<String> destroyed = new LinkedHashSet<>(preFrozen.keySet());
            destroyed.removeAll(postFrozen.keySet());
            fail("the set of function entry points changed: created=" + created
                + " destroyed=" + destroyed);
        }
        Set<String> targets = new HashSet<>();
        for (Row row : rows) {
            if (row.entry != null) {
                targets.add(String.format(Locale.ROOT, "%08x", row.addr));
            }
        }
        List<String> drift = new ArrayList<>();
        Map<String, Integer> columnMoves = new LinkedHashMap<>();
        int rowsChanged = 0;
        for (String key : preFrozen.keySet()) {
            String[] before = preFrozen.get(key).split("\t", -1);
            String post = postFrozen.get(key);
            if (post == null) {
                continue;
            }
            String[] after = post.split("\t", -1);
            boolean isTarget = targets.contains(key);
            boolean moved = false;
            for (int c = 0; c < FROZEN_COLUMNS.length; c++) {
                String bv = c < before.length ? before[c] : "";
                String av = c < after.length ? after[c] : "";
                if (bv.equals(av)) {
                    continue;
                }
                moved = true;
                String column = FROZEN_COLUMNS[c];
                Integer n = columnMoves.get(column);
                columnMoves.put(column, n == null ? 1 : n + 1);
                if (!isTarget) {
                    drift.add("NON-TARGET 0x" + key + " column " + column
                        + " changed [" + bv + "] -> [" + av + "]");
                } else if (!mutableColumns.contains(column)) {
                    drift.add("TARGET 0x" + key + " moved FROZEN column " + column
                        + " [" + bv + "] -> [" + av + "]");
                }
            }
            if (moved) {
                rowsChanged++;
            } else if (isTarget && !mutableColumns.isEmpty()) {
                drift.add("TARGET 0x" + key + " did not change at all");
            }
        }
        if (spec.has("expectedTargetsChanged") && !relaxed) {
            long want = spec.num("expectedTargetsChanged", -1);
            if (rowsChanged != want) {
                fail("changed function count " + rowsChanged + " != " + want);
            }
        }
        if (spec.has("expectedFunctionsUntouched") && !relaxed) {
            long untouched = preFrozen.size() - rowsChanged;
            if (untouched != spec.num("expectedFunctionsUntouched", -1)) {
                fail("untouched function count " + untouched + " != "
                    + spec.num("expectedFunctionsUntouched", -1));
            }
        }

        // -- symbols ------------------------------------------------------
        List<String> postSyms = symbolCensus();
        Set<String> addedSyms = new LinkedHashSet<>(postSyms);
        addedSyms.removeAll(preSyms);
        Set<String> removedSyms = new LinkedHashSet<>(preSyms);
        removedSyms.removeAll(postSyms);
        if (verbs.contains(V_SET_DATA_POINTER)) {
            if (!removedSyms.isEmpty()) {
                fail("SET_DATA_POINTER removed non-dynamic symbols: "
                    + removedSyms);
            }
            if (!relaxed && spec.has("expectedSymbolsAdded")
                    && addedSyms.size() != spec.num("expectedSymbolsAdded", -1)) {
                fail("symbols added " + addedSyms.size() + " != "
                    + spec.num("expectedSymbolsAdded", -1));
            }
            for (String s : addedSyms) {
                String[] c = s.split("\t", -1);
                boolean matched = false;
                for (Row row : rows) {
                    if (c[0].equals(String.format(Locale.ROOT, "%08x", row.addr))
                            && c[1].equals(row.get("proposedLabel"))) {
                        matched = true;
                        break;
                    }
                }
                if (!matched) {
                    drift.add("UNEXPECTED ADDED SYMBOL " + s);
                }
            }
        } else if (!verbs.contains(V_SET_NAME)) {
            if (!addedSyms.isEmpty() || !removedSyms.isEmpty()) {
                fail("the non-dynamic symbol census changed but no rename verb "
                    + "was declared: added=" + addedSyms.size() + " removed="
                    + removedSyms.size() + " first="
                    + (addedSyms.isEmpty() ? removedSyms.iterator().next()
                                           : addedSyms.iterator().next()));
            }
        } else {
            if (!relaxed && spec.has("expectedSymbolsAdded")
                    && addedSyms.size() != spec.num("expectedSymbolsAdded", -1)) {
                fail("symbols added " + addedSyms.size() + " != "
                    + spec.num("expectedSymbolsAdded", -1));
            }
            if (!relaxed && spec.has("expectedSymbolsRemoved")
                    && removedSyms.size() != spec.num("expectedSymbolsRemoved", -1)) {
                fail("symbols removed " + removedSyms.size() + " != "
                    + spec.num("expectedSymbolsRemoved", -1));
            }
            if (preSyms.size() != postSyms.size()) {
                fail("non-dynamic symbol count " + preSyms.size() + " -> "
                    + postSyms.size());
            }
            for (String s : addedSyms) {
                String[] c = s.split("\t", -1);
                boolean matched = false;
                for (Row row : rows) {
                    if (c[0].equals(String.format(Locale.ROOT, "%08x", row.addr))
                            && c[1].equals(row.get("proposedName"))) {
                        matched = true;
                        break;
                    }
                }
                if (!matched) {
                    drift.add("UNEXPECTED ADDED SYMBOL " + s);
                }
            }
            for (String s : removedSyms) {
                String[] c = s.split("\t", -1);
                boolean matched = false;
                for (Row row : rows) {
                    if (c[0].equals(String.format(Locale.ROOT, "%08x", row.addr))
                            && c[1].equals(row.get("currentName"))) {
                        matched = true;
                        break;
                    }
                }
                if (!matched) {
                    drift.add("UNEXPECTED REMOVED SYMBOL " + s);
                }
            }
        }

        // -- bookmarks ----------------------------------------------------
        List<String> postBookmarks = bookmarkCensus();
        if (!verbs.contains(V_BOOKMARK)) {
            if (!preBookmarks.equals(postBookmarks)) {
                fail("the bookmark census changed but REMOVE_STALE_BOOKMARK was "
                    + "not declared");
            }
        } else {
            List<String> lost = new ArrayList<>(preBookmarks);
            lost.removeAll(postBookmarks);
            List<String> gained = new ArrayList<>(postBookmarks);
            gained.removeAll(preBookmarks);
            if (!gained.isEmpty()) {
                fail("bookmarks GAINED: " + gained);
            }
            Set<String> lostAt = new TreeSet<>();
            for (String s : lost) {
                lostAt.add(s.substring(0, s.indexOf('\t')));
            }
            Set<String> wantAt = new TreeSet<>(removedBookmarks);
            // MEASURED, not assumed: on the 2026-08-17 41-row replay all 15
            // pinned Error/"Bad Instruction" bookmarks were present and removed,
            // but only 2 tuples actually disappear from the census.  The other
            // 13 are re-created byte-identically by the surrounding bounded
            // classification, which is why the completed ceremony's net is
            // 2303 -> 2301 rather than 2303 -> 2288.  The true invariant is
            // therefore "nothing outside the pinned set was removed", not
            // equality.  A removal the pin did not authorise still refuses.
            Set<String> unpinned = new TreeSet<>(lostAt);
            unpinned.removeAll(wantAt);
            if (!unpinned.isEmpty()) {
                fail("bookmark removal set " + lostAt + " contains addresses "
                    + unpinned + " that are not in the pinned removed set "
                    + wantAt);
            }
            notes.add("bookmarkTuplesLost=" + lostAt.size()
                + " pinnedRemovals=" + wantAt.size()
                + " recreatedIdenticallyByClassification="
                + (wantAt.size() - lostAt.size()));
        }

        // -- defined data -------------------------------------------------
        List<String> postDefinedData = definedDataCensus();
        boolean dataMayMove = verbs.contains(V_CLEAR)
            || verbs.contains(V_DISASSEMBLE)
            || verbs.contains(V_SET_DATA_POINTER);
        if (!dataMayMove) {
            if (!preDefinedData.equals(postDefinedData)) {
                fail("the defined-data census changed but no geometry verb was "
                    + "declared");
            }
        } else {
            Set<Address> dataTargets = new HashSet<>();
            for (Row row : rows) {
                if ("DATA:POINTER".equals(row.liveKind) && row.entry != null) {
                    dataTargets.add(row.entry);
                }
            }
            Set<String> preSet = new LinkedHashSet<>(preDefinedData);
            Set<String> postSet = new LinkedHashSet<>(postDefinedData);
            Set<String> changed = new LinkedHashSet<>(preSet);
            changed.removeAll(postSet);
            Set<String> gained = new LinkedHashSet<>(postSet);
            gained.removeAll(preSet);
            changed.addAll(gained);
            for (String s : changed) {
                Address at = toAddr(Long.parseLong(s.substring(0, s.indexOf('\t')), 16));
                boolean allowed = verbs.contains(V_SET_DATA_POINTER)
                    ? dataTargets.contains(at) : admitted.contains(at);
                if (!allowed) {
                    fail("DEFINED DATA CHANGED OUTSIDE the admitted ranges at "
                        + at + " (" + s + ")");
                }
            }
        }

        // -- raw bytes ----------------------------------------------------
        String postMemory = memoryDigest();
        if (!preMemory.equals(postMemory)) {
            fail("collateral memory digest expected [" + preMemory + "] actual ["
                + postMemory + "]");
        }

        if (!drift.isEmpty()) {
            fail("collateral drift (" + drift.size() + "): " + drift.subList(0,
                Math.min(12, drift.size())));
        }

        return "functionsExamined=" + preFrozen.size()
            + " rowsDeclared=" + rows.size()
            + " functionsChanged=" + rowsChanged
            + " functionsUntouched=" + (preFrozen.size() - rowsChanged)
            + " columnsMoved=" + columnMoves
            + " mutableColumns=" + mutableColumns
            + " frozenDigestPre=" + digestOfMap(preFrozen)
            + " frozenDigestPost=" + digestOfMap(postFrozen)
            + " symbolsPre=" + preSyms.size() + " symbolsPost=" + postSyms.size()
            + " symbolsAdded=" + addedSyms.size()
            + " symbolsRemoved=" + removedSyms.size()
            + " symbolDigestPost=" + digestOfList(postSyms)
            + " bookmarkDigestPost=" + digestOfList(postBookmarks)
            + " definedDataDigestPost=" + digestOfList(postDefinedData)
            + " memoryDigest=" + postMemory;
    }

    // ============================================================ output ===

    private void report(String mode, int rowCount) {
        if (failures.isEmpty()) {
            println("COHORT_OK cohort=" + cohortId + " mode=" + mode + " rows="
                + rowCount + " policy=" + POLICY);
        } else {
            println("COHORT_FAIL cohort=" + cohortId + " mode=" + mode
                + " failures=" + failures.size());
            for (String message : failures) {
                println("COHORT_GATE_FAIL " + message);
            }
        }
        println("COHORT_VERDICT mode=" + mode + " cohort=" + cohortId + " result="
            + (failures.isEmpty() ? "PASS" : "FAIL"));
    }

    private void emit(Path outTsv, List<Row> rows) throws Exception {
        if (outTsv == null) {
            return;
        }
        StringBuilder tsv = new StringBuilder();
        tsv.append("addr\ttargetName\tliveKind\tsubtype\tpreRanges\tpreBytes"
            + "\tproposedRanges\tproposedBytes\tdeltaBytes\taddedRanges"
            + "\tpostRanges\tpostBytes\tproposedDigest\tpostDigest"
            + "\tpreInstrBytes\tpreDataBytes\tpreUndefBytes\tpostInstrBytes"
            + "\tpostDataBytes\tpostUndefBytes\tclassifiedDelta\tphase1Passes"
            + "\tresyncRounds\tclearedRanges\tclearedKinds\tpreInstrCount"
            + "\tpostInstrCount\tstillUndefined\tescaped"
            + "\tvarArgsPre\tvarArgsWanted\tvarArgsPost\trendered\tverdict"
            + "\tgateFailures\n");
        for (Row row : rows) {
            tsv.append(row.addrText).append('\t')
               .append(row.targetName).append('\t')
               .append(row.liveKind).append('\t')
               .append(row.subtype).append('\t')
               .append(row.preRanges).append('\t')
               .append(row.preBytes).append('\t')
               .append(row.get("proposedRanges")).append('\t')
               .append(row.proposed == null ? -1 : row.proposed.getNumAddresses())
               .append('\t')
               .append(row.deltaBytes == Long.MIN_VALUE ? "" : row.deltaBytes)
               .append('\t')
               .append(row.added == null ? "" : rangesText(row.added)).append('\t')
               .append(row.postRanges).append('\t')
               .append(row.postBytes).append('\t')
               .append(row.proposed == null ? "" : bodyDigest(row.proposed))
               .append('\t')
               .append(row.postRanges.isEmpty() ? ""
                       : bodyDigest(parseRanges(row.postRanges))).append('\t')
               .append(row.preInstrBytes).append('\t')
               .append(row.preDataBytes).append('\t')
               .append(row.preUndefBytes).append('\t')
               .append(row.postInstrBytes).append('\t')
               .append(row.postDataBytes).append('\t')
               .append(row.postUndefBytes).append('\t')
               .append(row.postClassified() - row.preClassified()).append('\t')
               .append(row.phase1Passes).append('\t')
               .append(row.resyncRounds).append('\t')
               .append(rangesText(row.cleared)).append('\t')
               .append(String.join(",", row.clearedKinds)).append('\t')
               .append(row.preInstrCount).append('\t')
               .append(row.postInstrCount).append('\t')
               .append(row.stillUndefined).append('\t')
               .append(row.escaped).append('\t')
               .append(row.preVarArgs).append('\t')
               .append(row.varArgsWanted == null ? "PRESERVE"
                       : String.valueOf(row.varArgsWanted)).append('\t')
               .append(row.varArgsPost).append('\t')
               .append(row.rendered).append('\t')
               .append(row.verdict).append('\t')
               .append(String.join(" | ", row.gateFailures)).append('\n');
        }
        Files.write(outTsv, tsv.toString().getBytes(StandardCharsets.UTF_8));
    }

    private void emitJson(Path outJson, String mode, String projectPath, Spec spec,
            Path manifestPath, String manifestSha, long manifestBytes,
            List<Row> rows, Set<String> verbs, Set<String> mutableColumns,
            long preFunctions, long preInstructions, long preReferences,
            long preDefinedData, long preUndefinedData, long preBookmarks,
            long postFunctions, long postInstructions, long postReferences,
            long postDefinedData, long postUndefinedData, long postBookmarks,
            String collateral, boolean committed) throws Exception {
        StringBuilder j = new StringBuilder();
        j.append("{\n  \"framework\": \"").append(FRAMEWORK).append("\",\n");
        j.append("  \"policy\": \"").append(POLICY).append("\",\n");
        j.append("  \"cohortId\": \"").append(jsonEscape(cohortId)).append("\",\n");
        j.append("  \"mode\": \"").append(jsonEscape(mode)).append("\",\n");
        j.append("  \"generatedAtUtc\": \"").append(Instant.now()).append("\",\n");
        j.append("  \"projectDir\": \"").append(jsonEscape(projectPath)).append("\",\n");
        j.append("  \"reversibility\": \"").append(REVERSIBILITY).append("\",\n");
        j.append("  \"inProcessRollback\": \"").append(IN_PROCESS_ROLLBACK)
         .append("\",\n");
        j.append("  \"gateOrder\": \"ALL_NON_MUTATING_GATES_FOR_ALL_ROWS_BEFORE_")
         .append("FIRST_WRITE\",\n");
        j.append("  \"varargsPolicy\": \"MANIFEST_DRIVEN_DEFAULT_PRESERVE\",\n");
        j.append("  \"varargsColumnBound\": ").append(spec.has("col.varArgs"))
         .append(",\n");
        j.append("  \"applier\": {\"script\": \"").append(jsonEscape(applierPath))
         .append("\", \"bytes\": ").append(applierBytes)
         .append(", \"sha256\": \"").append(jsonEscape(applierSha))
         .append("\", \"pinnedBySpec\": ")
         .append(!spec.all("applierSha256").isEmpty()).append("},\n");
        j.append("  \"spec\": {\"path\": \"").append(jsonEscape(spec.path))
         .append("\", \"bytes\": ").append(spec.bytes)
         .append(", \"sha256\": \"").append(spec.sha256).append("\"},\n");
        j.append("  \"manifest\": {\"path\": \"")
         .append(jsonEscape(manifestPath.toString()))
         .append("\", \"bytes\": ").append(manifestBytes)
         .append(", \"sha256\": \"").append(jsonEscape(manifestSha)).append("\"},\n");
        j.append("  \"verbs\": [");
        int i = 0;
        for (String v : verbs) {
            j.append(i++ == 0 ? "" : ", ").append('"').append(v).append('"');
        }
        j.append("],\n");
        j.append("  \"mutableColumns\": [");
        i = 0;
        for (String c : mutableColumns) {
            j.append(i++ == 0 ? "" : ", ").append('"').append(c).append('"');
        }
        j.append("],\n");
        j.append("  \"frozenColumns\": [");
        for (int k = 0; k < FROZEN_COLUMNS.length; k++) {
            j.append(k == 0 ? "" : ", ").append('"').append(FROZEN_COLUMNS[k])
             .append('"');
        }
        j.append("],\n");
        j.append("  \"program\": {\"name\": \"")
         .append(jsonEscape(spec.opt("programName", "")))
         .append("\", \"md5\": \"").append(jsonEscape(spec.opt("programMd5", "")))
         .append("\", \"sha256\": \"")
         .append(jsonEscape(spec.opt("programSha256", ""))).append("\"},\n");
        j.append("  \"counts\": {\"rows\": ").append(rows.size())
         .append(", \"preFunctions\": ").append(preFunctions)
         .append(", \"postFunctions\": ").append(postFunctions)
         .append(", \"preInstructions\": ").append(preInstructions)
         .append(", \"postInstructions\": ").append(postInstructions)
         .append(", \"preReferences\": ").append(preReferences)
         .append(", \"postReferences\": ").append(postReferences)
         .append(", \"preDefinedData\": ").append(preDefinedData)
         .append(", \"postDefinedData\": ").append(postDefinedData)
         .append(", \"preUndefinedData\": ").append(preUndefinedData)
         .append(", \"postUndefinedData\": ").append(postUndefinedData)
         .append(", \"preBookmarks\": ").append(preBookmarks)
         .append(", \"postBookmarks\": ").append(postBookmarks).append("},\n");
        j.append("  \"committed\": ").append(committed).append(",\n");
        // committed=false does NOT mean nothing was written: this build has no
        // working in-process rollback, so a refused mutating mode still leaves
        // the database changed.  writesAttempted is the honest field.
        j.append("  \"writesAttempted\": ").append(writesAttempted).append(",\n");
        j.append("  \"collateral\": ")
         .append(collateral == null ? "null"
                 : "\"" + jsonEscape(collateral) + "\"").append(",\n");
        j.append("  \"failures\": [");
        for (int k = 0; k < failures.size(); k++) {
            j.append(k == 0 ? "" : ", ").append('"')
             .append(jsonEscape(failures.get(k))).append('"');
        }
        j.append("],\n");
        j.append("  \"notes\": [");
        for (int k = 0; k < notes.size(); k++) {
            j.append(k == 0 ? "" : ", ").append('"')
             .append(jsonEscape(notes.get(k))).append('"');
        }
        j.append("],\n");
        j.append("  \"result\": \"").append(failures.isEmpty() ? "PASS" : "FAIL")
         .append("\"\n}\n");
        Files.write(outJson, j.toString().getBytes(StandardCharsets.UTF_8));
    }
}
