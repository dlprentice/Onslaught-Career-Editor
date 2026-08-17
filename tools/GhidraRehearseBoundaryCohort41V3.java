//@category Symbol
//
// SCRATCH-REPLICA REHEARSAL ONLY for a 41-row function-boundary cohort.
//
// This script is LIVE_FORBIDDEN by construction: it refuses to run unless the
// open project's directory sits under a path segment named
// "boundary-rehearsal", and it refuses outright if the path looks like the
// maintainer project or the tracked repository snapshot.  It has no live mode
// and no flag that can give it one.
//
// ---------------------------------------------------------------------------
// WHY V3 EXISTS
//
// V1/V2 authorized exactly one verb, Function.setBody().  Measured on a replica
// that leaves 274 bytes across 34 of the 41 rows admitted into a function body
// while still UNDEFINED - neither instruction nor defined data.  No completed
// ceremony in this project has ever left admitted bytes undefined.
//
// V3 therefore enforces a different, stronger invariant:
//
//     EVERY ADMITTED BYTE MUST END FULLY CLASSIFIED
//     - an instruction, or defined data -
//     rather than merely "fully instruction-covered".
//
// "Instruction-covered" is the wrong invariant here: 3 of the 41 rows admit a
// jump/SEH table that is ALREADY defined data and must never be disassembled,
// and 6 rows admit only the operand tail of an instruction that starts outside
// the added range, where there is nothing to do at all.
//
// ---------------------------------------------------------------------------
// THE AUTHORIZED MUTATIONS  (four verbs, in this order)
//
//   1. Disassembler.disassemble(seeds, restricted, true)
//        restricted set = the row's ADDED ranges, so an instruction can never
//        be created on a byte the manifest did not admit.  Seeds = the minimum
//        address of each still-undefined run.  Iterated to a fixpoint.
//
//   2. Listing.clearCodeUnits(...)  - bounded clear-to-resynchronise
//        Only for a run phase 1 could not decode, and only the single code unit
//        that immediately FOLLOWS that run, and only if that unit lies wholly
//        inside the same row's ADDED ranges.  Six rows need this: their
//        existing decode is desynchronised 2-3 bytes from the true instruction
//        stream because Ghidra's data-reference analyzer read string bytes as
//        addresses and seeded disassembly at them.  The derived clear set must
//        equal the pinned CLEAR_PLAN exactly.
//
//   3. BookmarkManager.removeBookmark(...) - bounded hygiene
//        Only Error/"Bad Instruction" bookmarks inside the admitted ranges that
//        the post-classification listing refutes, and only the pinned set.
//
//   4. Function.setBody() on the 41 preregistered entries, growing each body to
//        its preregistered proposed range set.
//
// No function is created or destroyed; no name, signature, comment, tag,
// symbol, byte, or reference is written directly; nothing outside the admitted
// ranges is ever cleared, disassembled, or bookmarked.
//
// ---------------------------------------------------------------------------
// NEW GATES OVER V1/V2
//
//   G_UNCLASSIFIED      every admitted byte is classified at the end
//   G_REGRESSION        no row's classified-byte count may DECREASE
//                       (0x00450010 proves this necessary: the precedent
//                        clear-then-disassemble shape turns 58 defined
//                        instruction bytes there into 65 undefined ones)
//   G_INSTR_ESCAPE      program-wide instruction delta == admitted-scoped delta
//                       and every new instruction lies inside its own row body
//   G_REF_ESCAPE        program-wide reference delta == admitted-sourced delta
//   G_CLEAR_PLAN        the derived clear set equals the pinned CLEAR_PLAN
//   G_CLEAR_CONTAINMENT every cleared unit lies wholly inside that row's added
//                       ranges
//   G_TABLE_PRESERVED   INCLUDE_JUMP_OR_SEH_TABLE rows keep every defined-data
//                       byte and are never cleared
//   G_PRECONDITION      rows that were already fully classified are not touched
//   G_BOOKMARKS         no bookmark change outside the admitted ranges; the
//                       removed set equals the pinned stale set
//   G_END_MID_INSTR_POST the proposal still does not end mid code unit AFTER
//                       classification
//   G_POST_CENSUS       pinned POST_INSTRUCTIONS / POST_REFERENCES /
//                       POST_BOOKMARKS / POST_FUNCTIONS
//
// Every mutating mode runs inside its own sub-transaction which is ABORTED
// unless all gates pass.  MEASURED on a scratch replica: the abort rolls the
// LOGICAL state back completely (instructions 551143, references 234478,
// bookmarks 2303, all 41 currentRanges intact after an aborted run), but
// Ghidra still writes a NEW DATABASE VERSION, so the project's files are no
// longer byte-identical to their pre state.  Byte-level recovery is therefore
// still restore-from-the-verified-PRE-backup, exactly as V2 declared.  Do not
// use a file-tree digest as the oracle for "nothing changed" after a writable
// session: use a logical readback.
//
// Usage:
//   -postScript GhidraRehearseBoundaryCohort41V3.java
//       <manifest.tsv> <out.tsv> <out.ready.json> <mode>
//
//   dry          all gates, no mutation whatsoever (run the JVM with -readOnly)
//   plan         full classification, full measurement, then ALWAYS abort.
//                Safe to run writable: nothing it does can ever persist.
//   apply        all gates + pinned census, classify, then setBody
//   readback     read bodies and classification back and compare (-readOnly)
//   probe-after-one  mid-batch halt: every gate of `apply`, then setBody on the
//                FIRST row only, so partial state can be proved recoverable
//   probe-apply  adverse testing: identical gates EXCEPT the pinned manifest
//                digest, the row count and the pinned POST census, so a
//                deliberately corrupted manifest can prove the geometry and
//                classification gates refuse.  Prints a PROBE_MODE banner.
//   probe-fault-escape          adverse fault injection: additionally seeds
//                disassembly OUTSIDE every admitted range so G_INSTR_ESCAPE and
//                G_REF_ESCAPE can be provoked.
//   probe-fault-extraclear      adverse fault injection: clears one extra unit
//                inside an admitted range so G_CLEAR_PLAN can be provoked.
//   probe-fault-clearescape     adverse fault injection: clears one unit
//                OUTSIDE the admitted ranges so G_CLEAR_CONTAINMENT can be
//                provoked.
//   probe-fault-strandbytes     adverse fault injection: strands admitted bytes
//                by clearing an instruction in an already-fully-classified row
//                without reclassifying, so G_UNCLASSIFIED and G_REGRESSION can
//                be provoked.
//   probe-fault-precedentclear  adverse fault injection: a FAITHFUL port of the
//                DESTRUCTIVE precedent shape - clear every instruction wholly
//                inside the added ranges up front, seed data-blind, and never
//                resynchronise - so G_REGRESSION can be provoked on the row
//                that proves it necessary (0x00450010, 58 defined instruction
//                bytes -> 65 undefined).
//
// Every probe-fault-* mode is refusal testing only.  Each one deliberately
// breaks the applier's own confinement so that the detector can be shown to
// fire; none of them can commit, because the gate they provoke aborts the
// sub-transaction.

import ghidra.app.script.GhidraScript;
import ghidra.program.disassemble.Disassembler;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressIterator;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Bookmark;
import ghidra.program.model.listing.BookmarkManager;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceManager;

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
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.TreeSet;

public class GhidraRehearseBoundaryCohort41V3 extends GhidraScript {

    private static final String SCHEMA = "bea.ghidra.boundary-cohort-41.rehearsal.v3";
    private static final String POLICY = "LIVE_FORBIDDEN";

    private static final String PROGRAM_NAME = "BEA.exe";
    private static final String PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55";
    private static final String PROGRAM_SHA256 =
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
    private static final String IMAGE_BASE = "00400000";
    private static final String LANGUAGE = "x86:LE:32:default";
    private static final String COMPILER_SPEC = "windows";
    private static final String TEXT_BLOCK = ".text";
    private static final long TEXT_START = 0x00401000L;
    private static final long TEXT_END = 0x005d7fffL;

    private static final long PRE_FUNCTIONS = 8329L;
    private static final long PRE_INSTRUCTIONS = 551143L;
    private static final long PRE_REFERENCES = 234478L;
    private static final long PRE_BOOKMARKS = 2303L;

    // Pinned from this lane's own re-measurement of the minimal shape on a
    // replica built from the off-volume PRE backup.  See the rehearsal report.
    private static final long POST_FUNCTIONS = 8329L;
    private static final long POST_INSTRUCTIONS = 551232L;   // +89
    private static final long POST_REFERENCES = 234493L;     // +15
    private static final long POST_BOOKMARKS = 2301L;        // -2
    private static final long ADMITTED_BYTES = 3293L;
    private static final long ADMITTED_UNDEFINED_BYTES = 274L;
    private static final long CLEARED_UNITS = 25L;
    private static final long CLEARED_BYTES = 63L;

    private static final int TARGET_COUNT = 41;
    private static final long MANIFEST_BYTES = 6217L;
    private static final String MANIFEST_SHA256 =
        "9abc5aedb1c7ff3c959670a714e457480e83ed6075b76a23cee5195e20399ed3";
    private static final String MANIFEST_HEADER =
        "addr\tcurrentRanges\tproposedRanges\tsubtype\tterminatorVa"
        + "\tterminatorBytes\tdeltaBytes\tbyteProof\tagreesWithNote";

    // The ONLY spans this applier may ever clear.  Every span lies wholly
    // inside the admitted (added) ranges of its own row, so the manifest's
    // byteProof gate already pins the exact bytes each span contains.
    private static final String[] CLEAR_PLAN = {
        "0x00417190\t00417349-00417350",
        "0x00437490\t00437a3e-00437a5b",
        "0x00450010\t0045004d-00450050;00450052-00450059",
        "0x0045ffa0\t00460020-00460026",
        "0x0046ff10\t00470050-00470053",
        "0x004c4100\t004c4148-004c4149",
    };

    // Error/"Bad Instruction" bookmarks the post-classification listing refutes.
    private static final String[] STALE_BOOKMARKS = {
        "00417347", "00437a3a", "00437a41", "00437a47", "00437a4d", "00437a54",
        "0045004b", "00450051", "00450054", "0046001d", "0047004a", "00472e2c",
        "0047e190", "0048ac5c", "004c4145",
    };
    private static final String BOOKMARK_TYPE = "Error";
    private static final String BOOKMARK_CATEGORY = "Bad Instruction";

    private static final int MAX_RESYNC = 16;

    private static final String CONTAINMENT_SEGMENT = "boundary-rehearsal";
    private static final String[] FORBIDDEN_PATH_MARKERS = {
        "ghidra\\projects", "ghidra/projects",
        "onslaught-career-editor\\reverse-engineering",
        "onslaught-career-editor/reverse-engineering",
    };

    private final List<String> failures = new ArrayList<>();
    private final List<String> notes = new ArrayList<>();

    private static class Row {
        String addr;
        String currentRangesText;
        String proposedRangesText;
        String subtype;
        String terminatorVaText;
        String terminatorBytesText;
        long deltaBytes;
        String byteProof;
        String agreesWithNote;
        Address entry;
        AddressSet current;
        AddressSet proposed;
        AddressSet added;
        // measured
        String functionName = "";
        String preRanges = "";
        long preBytes = -1;
        String postRanges = "";
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
        String verdict = "PENDING";
        final List<String> gateFailures = new ArrayList<>();

        long preClassified() { return preInstrBytes + preDataBytes; }
        long postClassified() { return postInstrBytes + postDataBytes; }
    }

    private void fail(Row row, String message) {
        if (row == null) {
            failures.add(message);
        } else {
            row.gateFailures.add(message);
            failures.add(row.addr + ": " + message);
        }
    }

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

    private static String rangesText(AddressSetView set) {
        StringBuilder sb = new StringBuilder();
        for (AddressRange range : set) {
            if (sb.length() > 0) {
                sb.append(';');
            }
            sb.append(range.getMinAddress().toString())
              .append('-')
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
            Address lo = toAddr(Long.parseLong(halves[0].trim(), 16));
            Address hi = toAddr(Long.parseLong(halves[1].trim(), 16));
            if (lo.compareTo(hi) > 0) {
                return null;
            }
            set.addRange(lo, hi);
        }
        return set.isEmpty() ? null : set;
    }

    private static String jsonEscape(String value) {
        if (value == null) {
            return "";
        }
        return value.replace("\\", "\\\\").replace("\"", "\\\"")
                    .replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t");
    }

    // ---------------------------------------------------------------- census

    /** Bytes inside `set` that are neither an instruction nor defined data. */
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

    /**
     * Code-unit-accurate byte split of `set` into instruction / defined data /
     * undefined.  A byte owned by an instruction that STARTS OUTSIDE `set` is
     * an instruction byte - six rows admit exactly that (five RET_IMM_SPLIT
     * operand tails plus 0x004ac4a0), and counting them as data would misreport
     * what is already classified.
     */
    private long[] byteSplit(AddressSetView set) {
        Listing listing = currentProgram.getListing();
        long instr = 0, data = 0, undef = 0;
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
        long[] split = byteSplit(row.added);
        long instr = split[0], data = split[1], undef = split[2];
        if (pre) {
            row.preInstrBytes = instr;
            row.preDataBytes = data;
            row.preUndefBytes = undef;
            row.preInstrCount = countInstructionsIn(row.added);
        } else {
            row.postInstrBytes = instr;
            row.postDataBytes = data;
            row.postUndefBytes = undef;
            row.postInstrCount = countInstructionsIn(row.added);
        }
    }

    private long countAllReferences() {
        long n = 0;
        ReferenceManager rm = currentProgram.getReferenceManager();
        AddressIterator it = rm.getReferenceSourceIterator(currentProgram.getMemory(), true);
        while (it.hasNext()) {
            n += rm.getReferencesFrom(it.next()).length;
        }
        return n;
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

    private List<String> bookmarkList() {
        List<String> out = new ArrayList<>();
        java.util.Iterator<Bookmark> it =
                currentProgram.getBookmarkManager().getBookmarksIterator();
        while (it.hasNext()) {
            Bookmark b = it.next();
            out.add(b.getAddress() + "|" + b.getTypeString() + "|" + b.getCategory()
                    + "|" + b.getComment());
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

    private long countInternalFunctions(FunctionManager fm) {
        long total = 0;
        FunctionIterator it = fm.getFunctions(true);
        while (it.hasNext()) {
            it.next();
            total++;
        }
        return total;
    }

    // -------------------------------------------------------- classification

    /**
     * Phase 1: iterate bounded disassembly to a fixpoint.  Seeds are the first
     * address of each still-undefined run; the restricted set is the row's own
     * admitted bytes, so nothing can be created anywhere else.
     */
    private void phase1(Row row, AddressSetView restricted, boolean dataBlind) {
        Listing listing = currentProgram.getListing();
        while (true) {
            AddressSet undef;
            if (dataBlind) {
                // ADVERSE ONLY: the precedent shape seeds at every byte not
                // covered by an INSTRUCTION, ignoring defined data entirely.
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

    /**
     * Phase 2: clear-to-resynchronise.  For each run phase 1 could not decode,
     * clear the single code unit immediately following it - and only if that
     * unit lies wholly inside the same row's admitted bytes.
     */
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
                // G_CLEAR_CONTAINMENT: never clear across the admitted edge.
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

    private void classify(Row row, AddressSetView restricted, boolean noResync,
            boolean dataBlind) {
        for (int round = 0; round <= MAX_RESYNC; round++) {
            phase1(row, restricted, dataBlind);
            if (undefinedIn(row.added).isEmpty()) {
                return;
            }
            if (noResync || round == MAX_RESYNC || !phase2(row)) {
                return;
            }
            row.resyncRounds++;
        }
    }

    /**
     * ADVERSE FAULT INJECTION ONLY.  Reproduces the destructive precedent shape
     * (clear every instruction wholly inside the added ranges up front) so that
     * G_REGRESSION can be provoked on the row that proves it necessary.
     */
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

    // ------------------------------------------------------------------ main

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length != 4) {
            println("COHORT41_FAIL reason=usage");
            return;
        }
        Path manifestPath = Paths.get(args[0]);
        Path outTsv = Paths.get(args[1]);
        Path outJson = Paths.get(args[2]);
        String mode = args[3];

        // `probeMode` DISABLES the pins that a doctored manifest would trip
        // spuriously (manifest digest, row count, PRE/POST census).  The
        // probe-fault-* modes use the REAL manifest and therefore keep every
        // pin ENFORCED - the whole point is to watch them fire.
        boolean probeMode = "probe-apply".equals(mode);
        boolean faultEscape = "probe-fault-escape".equals(mode);
        boolean faultExtraClear = "probe-fault-extraclear".equals(mode);
        boolean faultPrecedent = "probe-fault-precedentclear".equals(mode);
        boolean faultClearEscape = "probe-fault-clearescape".equals(mode);
        boolean faultStrand = "probe-fault-strandbytes".equals(mode);
        boolean faultMode = faultEscape || faultExtraClear || faultPrecedent
                || faultClearEscape || faultStrand;
        boolean afterOne = "probe-after-one".equals(mode);
        boolean planOnly = "plan".equals(mode);
        boolean readback = "readback".equals(mode);
        boolean classifying = "apply".equals(mode) || planOnly || afterOne
                || probeMode || faultMode;
        boolean settingBodies = "apply".equals(mode) || afterOne || probeMode
                || faultMode;
        if (!("dry".equals(mode) || "apply".equals(mode) || readback || planOnly
                || probeMode || faultMode || afterOne)) {
            println("COHORT41_FAIL reason=bad_mode value=" + mode);
            return;
        }
        if (planOnly) {
            println("COHORT41_PLAN_MODE banner=always-aborts"
                + " commit=IMPOSSIBLE allGates=ENFORCED"
                + " note=logical_state_rolls_back_but_the_db_file_version_advances");
        }
        if (afterOne) {
            println("COHORT41_PROBE_AFTER_ONE banner=mid-batch-halt"
                + " rowsToApply=1 allGates=ENFORCED cohortDigestPin=ENFORCED");
        }
        if (probeMode) {
            println("COHORT41_PROBE_MODE banner=adverse-refusal-testing"
                + " cohortDigestPin=DISABLED postCensusPin=DISABLED"
                + " geometryGates=ENFORCED classificationGates=ENFORCED");
        }
        if (faultMode) {
            println("COHORT41_FAULT_MODE banner=deliberate-self-sabotage"
                + " allPins=ENFORCED allGates=ENFORCED commit=EXPECTED_IMPOSSIBLE"
                + " fault=" + (faultEscape ? "ESCAPE"
                    : faultExtraClear ? "EXTRA_CLEAR_INSIDE_A_TABLE_ROW"
                    : faultClearEscape ? "CLEAR_OUTSIDE_THE_ADMITTED_RANGE"
                    : faultStrand ? "STRAND_ADMITTED_BYTES"
                    : "VERBATIM_PRECEDENT_CLEAR_NO_RESYNC_DATA_BLIND"));
        }

        // ---- Gate 1: containment.  Never the live project, never the repo. ----
        String projectPath;
        try {
            File dir = state.getProject().getProjectLocator().getProjectDir();
            projectPath = dir.getAbsolutePath();
        } catch (Exception exc) {
            println("COHORT41_FAIL reason=no_project_locator");
            return;
        }
        String lower = projectPath.toLowerCase(Locale.ROOT);
        for (String marker : FORBIDDEN_PATH_MARKERS) {
            if (lower.contains(marker)) {
                println("COHORT41_REFUSE reason=forbidden_project_path marker=" + marker
                    + " path=" + projectPath);
                return;
            }
        }
        if (!lower.contains(CONTAINMENT_SEGMENT)) {
            println("COHORT41_REFUSE reason=project_not_in_rehearsal_scratch path="
                + projectPath);
            return;
        }

        // ---- Gate 2: program identity and PRE census. ----
        if (currentProgram == null) {
            println("COHORT41_FAIL reason=no_current_program");
            return;
        }
        String md5 = String.valueOf(currentProgram.getExecutableMD5()).toLowerCase(Locale.ROOT);
        String sha = String.valueOf(currentProgram.getExecutableSHA256()).toLowerCase(Locale.ROOT);
        if (!PROGRAM_NAME.equals(currentProgram.getName())) {
            fail(null, "program name " + currentProgram.getName());
        }
        if (!PROGRAM_MD5.equals(md5)) {
            fail(null, "program md5 " + md5);
        }
        if (!PROGRAM_SHA256.equals(sha)) {
            fail(null, "program sha256 " + sha);
        }
        if (!IMAGE_BASE.equals(currentProgram.getImageBase().toString())) {
            fail(null, "image base " + currentProgram.getImageBase());
        }
        if (!LANGUAGE.equals(currentProgram.getLanguageID().getIdAsString())) {
            fail(null, "language " + currentProgram.getLanguageID());
        }
        if (!COMPILER_SPEC.equals(
                currentProgram.getCompilerSpec().getCompilerSpecID().getIdAsString())) {
            fail(null, "compiler spec");
        }
        MemoryBlock text = currentProgram.getMemory().getBlock(TEXT_BLOCK);
        if (text == null || text.getStart().getOffset() != TEXT_START
                || text.getEnd().getOffset() != TEXT_END || !text.isExecute()) {
            fail(null, "text block geometry");
        }
        Listing listing = currentProgram.getListing();
        FunctionManager fm = currentProgram.getFunctionManager();
        BookmarkManager bm = currentProgram.getBookmarkManager();
        long preFunctions = countInternalFunctions(fm);
        long preInstructions = listing.getNumInstructions();
        long preReferences = countAllReferences();
        List<String> preBookmarkList = bookmarkList();
        long preBookmarks = preBookmarkList.size();
        if (!readback) {
            if (preFunctions != PRE_FUNCTIONS) {
                fail(null, "PRE function count " + preFunctions + " != " + PRE_FUNCTIONS);
            }
            if (preInstructions != PRE_INSTRUCTIONS) {
                fail(null, "PRE instruction count " + preInstructions
                    + " != " + PRE_INSTRUCTIONS);
            }
            if (!probeMode && preReferences != PRE_REFERENCES) {
                fail(null, "PRE reference count " + preReferences
                    + " != " + PRE_REFERENCES);
            }
            if (!probeMode && preBookmarks != PRE_BOOKMARKS) {
                fail(null, "PRE bookmark count " + preBookmarks
                    + " != " + PRE_BOOKMARKS);
            }
        }

        // ---- Gate 3: manifest identity. ----
        byte[] manifestRaw = Files.readAllBytes(manifestPath);
        String manifestSha = sha256(manifestRaw);
        boolean manifestIsPinned = MANIFEST_SHA256.equals(manifestSha)
                && manifestRaw.length == MANIFEST_BYTES;
        if (!probeMode) {
            if (manifestRaw.length != MANIFEST_BYTES) {
                fail(null, "manifest bytes " + manifestRaw.length);
            }
            if (!MANIFEST_SHA256.equals(manifestSha)) {
                fail(null, "manifest sha256 " + manifestSha);
            }
        }
        List<String> lines = new ArrayList<>();
        for (String line : new String(manifestRaw, StandardCharsets.UTF_8).split("\n", -1)) {
            String trimmed = line.endsWith("\r") ? line.substring(0, line.length() - 1) : line;
            if (!trimmed.isEmpty()) {
                lines.add(trimmed);
            }
        }
        if (lines.isEmpty() || !MANIFEST_HEADER.equals(lines.get(0))) {
            fail(null, "manifest header drift");
            emit(outTsv, outJson, new ArrayList<Row>(), mode, projectPath, manifestPath,
                 manifestSha, manifestRaw.length, preFunctions, preInstructions,
                 preReferences, preBookmarks, preFunctions, preInstructions,
                 preReferences, preBookmarks);
            println("COHORT41_FAIL reason=manifest_header");
            return;
        }
        List<Row> rows = new ArrayList<>();
        Map<String, Row> byAddr = new LinkedHashMap<>();
        for (int i = 1; i < lines.size(); i++) {
            String[] cells = lines.get(i).split("\t", -1);
            if (cells.length != 9) {
                fail(null, "row " + i + " column count " + cells.length);
                continue;
            }
            Row row = new Row();
            row.addr = cells[0].trim().toLowerCase(Locale.ROOT);
            row.currentRangesText = cells[1].trim();
            row.proposedRangesText = cells[2].trim();
            row.subtype = cells[3].trim();
            row.terminatorVaText = cells[4].trim();
            row.terminatorBytesText = cells[5].trim();
            try {
                row.deltaBytes = Long.parseLong(cells[6].trim());
            } catch (NumberFormatException exc) {
                row.deltaBytes = Long.MIN_VALUE;
                fail(row, "deltaBytes not numeric");
            }
            row.byteProof = cells[7].trim();
            row.agreesWithNote = cells[8].trim();
            if (byAddr.containsKey(row.addr)) {
                fail(row, "duplicate address in manifest");
            }
            byAddr.put(row.addr, row);
            rows.add(row);
        }
        if (!probeMode && rows.size() != TARGET_COUNT) {
            fail(null, "row count " + rows.size() + " != " + TARGET_COUNT);
        }

        AddressSet textSet = new AddressSet(toAddr(TEXT_START), toAddr(TEXT_END));
        AddressSet allProposed = new AddressSet();
        AddressSet admitted = new AddressSet();

        for (Row row : rows) {
            if (!row.addr.startsWith("0x")) {
                fail(row, "address not 0x-prefixed");
                continue;
            }
            row.entry = toAddr(Long.parseLong(row.addr.substring(2), 16));
            row.current = parseRanges(row.currentRangesText);
            row.proposed = parseRanges(row.proposedRangesText);
            if (row.current == null || row.proposed == null) {
                fail(row, "unparseable range text");
                continue;
            }
            if (!row.proposed.getMinAddress().equals(row.entry)) {
                fail(row, "proposed body does not start at the entry point");
            }
            if (!textSet.contains(row.proposed)) {
                fail(row, "proposed body leaves .text");
            }
            // Gate: growth only.
            AddressSet dropped = new AddressSet(row.current);
            dropped.delete(row.proposed);
            if (!dropped.isEmpty()) {
                fail(row, "proposal DROPS currently owned bytes: " + rangesText(dropped));
            }
            row.added = new AddressSet(row.proposed);
            row.added.delete(row.current);
            long delta = row.proposed.getNumAddresses() - row.current.getNumAddresses();
            if (delta != row.deltaBytes) {
                fail(row, "deltaBytes " + row.deltaBytes + " != measured " + delta);
            }
            if (row.added.isEmpty()) {
                fail(row, "proposal adds nothing");
            }
            // Gate: targets must not collide with each other.
            AddressSet clash = new AddressSet(allProposed);
            clash = clash.intersect(row.proposed);
            if (!clash.isEmpty()) {
                fail(row, "target/target overlap at " + rangesText(clash));
            }
            allProposed.add(row.proposed);
            admitted.add(row.added);

            // Gate: the function must exist at the exact entry.
            Function fn = fm.getFunctionAt(row.entry);
            if (fn == null) {
                fail(row, "NO FUNCTION AT ENTRY");
                continue;
            }
            row.functionName = fn.getName();
            AddressSetView body = fn.getBody();
            row.preRanges = rangesText(body);
            row.preBytes = body.getNumAddresses();

            // Gate: the fresh read must match the state this mode expects.
            AddressSet expectedNow = readback ? row.proposed : row.current;
            String expectedNowText = readback ? row.proposedRangesText
                                              : row.currentRangesText;
            if (!bodyDigest(body).equals(bodyDigest(expectedNow))) {
                fail(row, (readback ? "READBACK STATE DRIFT: " : "CURRENT STATE DRIFT: ")
                    + "replica=" + row.preRanges + " manifest=" + expectedNowText);
            }

            // Gate: terminator bytes must reproduce and sit inside the proposal.
            byte[] want = new byte[row.terminatorBytesText.length() / 2];
            for (int i = 0; i < want.length; i++) {
                want[i] = (byte) Integer.parseInt(
                    row.terminatorBytesText.substring(i * 2, i * 2 + 2), 16);
            }
            Address tva = toAddr(Long.parseLong(row.terminatorVaText, 16));
            byte[] got = new byte[want.length];
            try {
                currentProgram.getMemory().getBytes(tva, got);
            } catch (Exception exc) {
                Arrays.fill(got, (byte) 0);
                fail(row, "terminator unreadable at " + tva);
            }
            if (!Arrays.equals(want, got)) {
                fail(row, "terminator bytes differ: want=" + row.terminatorBytesText
                    + " got=" + hex(got));
            }
            AddressSet termSet = new AddressSet(tva, tva.add(want.length - 1L));
            if (!row.proposed.contains(termSet)) {
                fail(row, "terminator not inside the proposed body");
            }

            // Gate: byteProof ranges must equal the added ranges and reproduce.
            AddressSet proofSet = new AddressSet();
            for (String segment : row.byteProof.split(" \\+ ")) {
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

            // Gate: the proposal must not end mid code unit.
            Address max = row.proposed.getMaxAddress();
            CodeUnit unit = listing.getCodeUnitContaining(max);
            if (unit != null && !unit.getMaxAddress().equals(max)) {
                fail(row, "proposal ENDS MID-INSTRUCTION inside "
                    + unit.getMinAddress() + "-" + unit.getMaxAddress());
            }

            // Gate: no overlap with any other function body.
            java.util.Iterator<Function> overlapping = fm.getFunctionsOverlapping(row.proposed);
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

        long preAdmittedUndefined = 0;
        for (Row row : rows) {
            preAdmittedUndefined += row.preUndefBytes;
        }
        if (!probeMode && !readback) {
            if (admitted.getNumAddresses() != ADMITTED_BYTES) {
                fail(null, "admitted byte count " + admitted.getNumAddresses()
                    + " != " + ADMITTED_BYTES);
            }
            if (preAdmittedUndefined != ADMITTED_UNDEFINED_BYTES) {
                fail(null, "PRE admitted-undefined byte count " + preAdmittedUndefined
                    + " != " + ADMITTED_UNDEFINED_BYTES);
            }
        }

        boolean gatesPassed = failures.isEmpty();

        // ------------------------------------------------------- readback ---
        if (readback) {
            for (Row row : rows) {
                Function fn = row.entry == null ? null : fm.getFunctionAt(row.entry);
                if (fn == null) {
                    row.verdict = "FAIL_NO_FUNCTION";
                    continue;
                }
                AddressSetView body = fn.getBody();
                row.postRanges = rangesText(body);
                row.postBytes = body.getNumAddresses();
                censusRow(row, false);
                row.stillUndefined = rangesText(undefinedIn(row.added));
                boolean geometry = bodyDigest(body).equals(bodyDigest(row.proposed));
                boolean classified = row.postUndefBytes == 0;
                row.verdict = !geometry ? "FAIL_RANGE_MISMATCH"
                        : !classified ? "FAIL_UNCLASSIFIED_BYTES" : "PASS";
                if (!"PASS".equals(row.verdict)) {
                    fail(row, "readback " + row.verdict);
                }
            }
            if (preInstructions != POST_INSTRUCTIONS) {
                fail(null, "readback instruction count " + preInstructions
                    + " != " + POST_INSTRUCTIONS);
            }
            if (preReferences != POST_REFERENCES) {
                fail(null, "readback reference count " + preReferences
                    + " != " + POST_REFERENCES);
            }
            if (preBookmarks != POST_BOOKMARKS) {
                fail(null, "readback bookmark count " + preBookmarks
                    + " != " + POST_BOOKMARKS);
            }
            emit(outTsv, outJson, rows, mode, projectPath, manifestPath, manifestSha,
                 manifestRaw.length, preFunctions, preInstructions, preReferences,
                 preBookmarks, preFunctions, preInstructions, preReferences,
                 preBookmarks);
            report(mode, rows, preFunctions, preInstructions, preReferences,
                   preBookmarks, preFunctions, preInstructions, preReferences,
                   preBookmarks);
            return;
        }

        // ------------------------------------------------------------ dry ---
        if ("dry".equals(mode)) {
            for (Row row : rows) {
                row.verdict = row.gateFailures.isEmpty() ? "WOULD_APPLY" : "WOULD_REFUSE";
                row.stillUndefined = rangesText(undefinedIn(row.added));
            }
            emit(outTsv, outJson, rows, mode, projectPath, manifestPath, manifestSha,
                 manifestRaw.length, preFunctions, preInstructions, preReferences,
                 preBookmarks, preFunctions, preInstructions, preReferences,
                 preBookmarks);
            report(mode, rows, preFunctions, preInstructions, preReferences,
                   preBookmarks, preFunctions, preInstructions, preReferences,
                   preBookmarks);
            return;
        }

        // ------------------------------------------- mutating: refuse early --
        if (!gatesPassed) {
            println("COHORT41_REFUSE reason=gate_failure count=" + failures.size());
            for (String message : failures) {
                println("COHORT41_GATE_FAIL " + message);
            }
            for (Row row : rows) {
                row.verdict = row.gateFailures.isEmpty() ? "NOT_APPLIED_BATCH_REFUSED"
                                                         : "REFUSED";
            }
            emit(outTsv, outJson, rows, mode, projectPath, manifestPath, manifestSha,
                 manifestRaw.length, preFunctions, preInstructions, preReferences,
                 preBookmarks, countInternalFunctions(fm), listing.getNumInstructions(),
                 countAllReferences(), bookmarkList().size());
            println("COHORT41_NO_MUTATION_PERFORMED");
            return;
        }

        // --------------------------------------- everything below mutates ----
        List<String> preRefsInAdmitted = referencesFromWithin(admitted);
        List<String> preInstrStarts = instructionStartsIn(admitted);

        int tx = currentProgram.startTransaction("cohort41-v3-" + mode);
        boolean commit = false;
        try {
            if (classifying) {
                for (Row row : rows) {
                    if (faultPrecedent) {
                        precedentClearFault(row);
                    }
                    // The precedent port is faithful: clear up front, no
                    // resynchronising clear, and seed data-blind.  That is the
                    // exact shape that turns 0x00450010's 58 defined
                    // instruction bytes into 65 undefined ones.
                    classify(row, row.added, faultPrecedent, faultPrecedent);
                    censusRow(row, false);
                    row.stillUndefined = rangesText(undefinedIn(row.added));
                }
                if (faultExtraClear) {
                    // Deliberately clear one extra unit INSIDE the admitted range
                    // of a jump/SEH table row, so G_CLEAR_PLAN and
                    // G_TABLE_PRESERVED both have to fire.
                    for (Row row : rows) {
                        if (!"INCLUDE_JUMP_OR_SEH_TABLE".equals(row.subtype)) {
                            continue;
                        }
                        InstructionIterator it =
                                listing.getInstructions(row.added, true);
                        if (it.hasNext()) {
                            Instruction ins = it.next();
                            if (row.added.contains(ins.getMinAddress(),
                                                   ins.getMaxAddress())) {
                                row.clearedKinds.add(ins.getMinAddress() + "-"
                                        + ins.getMaxAddress() + "=INJECTED_FAULT");
                                row.cleared.addRange(ins.getMinAddress(),
                                                     ins.getMaxAddress());
                                listing.clearCodeUnits(ins.getMinAddress(),
                                                       ins.getMaxAddress(), false);
                                censusRow(row, false);
                                println("COHORT41_FAULT_INJECTED extraClearAt="
                                        + ins.getMinAddress() + " row=" + row.addr);
                                break;
                            }
                        }
                    }
                }
                if (faultClearEscape) {
                    // Deliberately record+perform a clear OUTSIDE the admitted
                    // range, so G_CLEAR_CONTAINMENT has to fire.
                    for (Row row : rows) {
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
                        listing.clearCodeUnits(unit.getMinAddress(),
                                               unit.getMaxAddress(), false);
                        censusRow(row, false);
                        println("COHORT41_FAULT_INJECTED clearOutsideAdmittedAt="
                                + unit.getMinAddress() + " row=" + row.addr);
                        break;
                    }
                }
                if (faultStrand) {
                    // Deliberately strand admitted bytes: clear one instruction
                    // inside a row that arrived 100% classified, and do NOT
                    // reclassify.  G_UNCLASSIFIED and G_REGRESSION must both fire.
                    for (Row row : rows) {
                        if (row.preUndefBytes != 0 || row.preInstrCount < 2) {
                            continue;
                        }
                        InstructionIterator it = listing.getInstructions(row.added, true);
                        while (it.hasNext()) {
                            Instruction ins = it.next();
                            if (!row.added.contains(ins.getMinAddress(),
                                                    ins.getMaxAddress())) {
                                continue;
                            }
                            row.clearedKinds.add(ins.getMinAddress() + "-"
                                    + ins.getMaxAddress() + "=STRANDED_FAULT");
                            row.cleared.addRange(ins.getMinAddress(), ins.getMaxAddress());
                            listing.clearCodeUnits(ins.getMinAddress(),
                                                   ins.getMaxAddress(), false);
                            censusRow(row, false);
                            row.stillUndefined = rangesText(undefinedIn(row.added));
                            println("COHORT41_FAULT_INJECTED strandedAt="
                                    + ins.getMinAddress() + " row=" + row.addr
                                    + " classified=" + row.preClassified() + "->"
                                    + row.postClassified());
                            break;
                        }
                        break;
                    }
                }
                if (faultEscape) {
                    // Deliberately seed disassembly OUTSIDE every admitted range.
                    // Prefer runs that start with a rel32 CALL/JMP so the fault
                    // is guaranteed to create references as well as instructions.
                    AddressSet outside = new AddressSet(textSet);
                    outside.delete(admitted);
                    AddressSet undefOutside = undefinedIn(outside);
                    if (!undefOutside.isEmpty()) {
                        AddressSet seeds = new AddressSet();
                        int n = 0, branchSeeds = 0;
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
                        Disassembler d =
                                Disassembler.getDisassembler(currentProgram, monitor, null);
                        d.disassemble(seeds, undefOutside, true);
                        println("COHORT41_FAULT_INJECTED escapeSeeds=" + n
                                + " rel32BranchSeeds=" + branchSeeds);
                    }
                }

                // ---- G_UNCLASSIFIED / G_REGRESSION / G_TABLE / G_PRECONDITION
                long postAdmittedUndefined = 0;
                long clearedUnits = 0;
                long clearedBytes = 0;
                for (Row row : rows) {
                    postAdmittedUndefined += row.postUndefBytes;
                    clearedUnits += row.clearedKinds.size();
                    clearedBytes += row.cleared.getNumAddresses();
                    if (row.postUndefBytes != 0) {
                        fail(row, "UNCLASSIFIED BYTES REMAIN in the admitted body: "
                            + row.stillUndefined);
                    }
                    if (row.postClassified() < row.preClassified()) {
                        fail(row, "CLASSIFIED-BYTE REGRESSION " + row.preClassified()
                            + " -> " + row.postClassified()
                            + " (instr " + row.preInstrBytes + "->" + row.postInstrBytes
                            + ", data " + row.preDataBytes + "->" + row.postDataBytes
                            + ")");
                    }
                    if (!row.cleared.isEmpty()
                            && !row.added.contains(row.cleared)) {
                        AddressSet outside = new AddressSet(row.cleared);
                        outside.delete(row.added);
                        fail(row, "CLEAR ESCAPED the admitted range at "
                            + rangesText(outside));
                    }
                    if ("INCLUDE_JUMP_OR_SEH_TABLE".equals(row.subtype)) {
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
                    // post-classification end-of-body re-check
                    Address max = row.proposed.getMaxAddress();
                    CodeUnit unit = listing.getCodeUnitContaining(max);
                    if (unit != null && !unit.getMaxAddress().equals(max)) {
                        fail(row, "POST-CLASSIFICATION the proposal ENDS MID-INSTRUCTION"
                            + " inside " + unit.getMinAddress() + "-"
                            + unit.getMaxAddress());
                    }
                    // every instruction inside the added set must stay inside
                    // the row's own proposed body
                    AddressSet cover = instructionCoverage(row.added);
                    AddressSet escape = new AddressSet(cover);
                    escape.delete(row.proposed);
                    if (!escape.isEmpty()) {
                        row.escaped = rangesText(escape);
                        fail(row, "INSTRUCTION ESCAPED the proposed body at "
                            + row.escaped);
                    }
                }
                if (!probeMode) {
                    if (postAdmittedUndefined != 0) {
                        fail(null, "admitted bytes still undefined: "
                            + postAdmittedUndefined);
                    }
                    if (clearedUnits != CLEARED_UNITS) {
                        fail(null, "cleared unit count " + clearedUnits
                            + " != " + CLEARED_UNITS);
                    }
                    if (clearedBytes != CLEARED_BYTES) {
                        fail(null, "cleared byte count " + clearedBytes
                            + " != " + CLEARED_BYTES);
                    }
                }

                // ---- G_CLEAR_PLAN: the derived clear set must equal the pin --
                if (manifestIsPinned) {
                    List<String> derived = new ArrayList<>();
                    for (Row row : rows) {
                        if (!row.cleared.isEmpty()) {
                            derived.add(row.addr + "\t" + rangesText(row.cleared));
                        }
                    }
                    List<String> pinned = Arrays.asList(CLEAR_PLAN);
                    if (!derived.equals(pinned)) {
                        fail(null, "CLEAR PLAN MISMATCH derived=" + derived
                            + " pinned=" + pinned);
                    }
                }

                // ---- G_INSTR_ESCAPE / G_REF_ESCAPE --------------------------
                long midInstructions = listing.getNumInstructions();
                long midReferences = countAllReferences();
                List<String> postInstrStarts = instructionStartsIn(admitted);
                List<String> postRefsInAdmitted = referencesFromWithin(admitted);
                long admittedInstrDelta = postInstrStarts.size() - preInstrStarts.size();
                long admittedRefDelta =
                        postRefsInAdmitted.size() - preRefsInAdmitted.size();
                if (midInstructions - preInstructions != admittedInstrDelta) {
                    fail(null, "INSTRUCTION ESCAPE: program delta "
                        + (midInstructions - preInstructions)
                        + " != admitted delta " + admittedInstrDelta);
                }
                if (midReferences - preReferences != admittedRefDelta) {
                    fail(null, "REFERENCE ESCAPE: program delta "
                        + (midReferences - preReferences)
                        + " != admitted-sourced delta " + admittedRefDelta);
                }

                // ---- G_BOOKMARKS: bounded hygiene ---------------------------
                TreeSet<String> stale = new TreeSet<>(Arrays.asList(STALE_BOOKMARKS));
                List<String> removed = new ArrayList<>();
                for (String key : stale) {
                    Address at = toAddr(Long.parseLong(key, 16));
                    if (!admitted.contains(at)) {
                        fail(null, "STALE BOOKMARK OUTSIDE the admitted ranges at " + at);
                        continue;
                    }
                    if (!undefinedIn(new AddressSet(at, at)).isEmpty()) {
                        fail(null, "STALE BOOKMARK at an unclassified byte " + at);
                        continue;
                    }
                    Bookmark mark = bm.getBookmark(at, BOOKMARK_TYPE, BOOKMARK_CATEGORY);
                    if (mark == null) {
                        if (!probeMode) {
                            fail(null, "PINNED STALE BOOKMARK ABSENT at " + at);
                        }
                        continue;
                    }
                    bm.removeBookmark(mark);
                    removed.add(at.toString());
                }
                List<String> postBookmarkList = bookmarkList();
                List<String> bmGained = new ArrayList<>(postBookmarkList);
                bmGained.removeAll(preBookmarkList);
                List<String> bmLost = new ArrayList<>(preBookmarkList);
                bmLost.removeAll(postBookmarkList);
                for (String s : bmGained) {
                    Address at = toAddr(Long.parseLong(s.substring(0, s.indexOf('|')), 16));
                    if (!admitted.contains(at)) {
                        fail(null, "BOOKMARK CREATED OUTSIDE the admitted ranges at " + at);
                    }
                }
                for (String s : bmLost) {
                    Address at = toAddr(Long.parseLong(s.substring(0, s.indexOf('|')), 16));
                    if (!admitted.contains(at)) {
                        fail(null, "BOOKMARK REMOVED OUTSIDE the admitted ranges at " + at);
                    }
                }
                if (!probeMode && !bmGained.isEmpty()) {
                    fail(null, "BOOKMARKS SURVIVED hygiene: " + bmGained);
                }
                notes.add("bookmarksRemoved=" + removed.size() + " " + removed);

                // ---- G_POST_CENSUS ------------------------------------------
                long postFunctionsMid = countInternalFunctions(fm);
                if (postFunctionsMid != preFunctions) {
                    fail(null, "function census moved during classification "
                        + preFunctions + " -> " + postFunctionsMid);
                }
                if (!probeMode) {
                    if (listing.getNumInstructions() != POST_INSTRUCTIONS) {
                        fail(null, "POST instruction count "
                            + listing.getNumInstructions() + " != " + POST_INSTRUCTIONS);
                    }
                    if (countAllReferences() != POST_REFERENCES) {
                        fail(null, "POST reference count " + countAllReferences()
                            + " != " + POST_REFERENCES);
                    }
                    if (postBookmarkList.size() != POST_BOOKMARKS) {
                        fail(null, "POST bookmark count " + postBookmarkList.size()
                            + " != " + POST_BOOKMARKS);
                    }
                }
            }

            // ------------------------------------------------- setBody -------
            if (settingBodies && failures.isEmpty()) {
                int appliedRows = 0;
                for (Row row : rows) {
                    if (afterOne && appliedRows >= 1) {
                        row.verdict = "HALTED_BEFORE_APPLY";
                        continue;
                    }
                    appliedRows++;
                    Function fn = fm.getFunctionAt(row.entry);
                    try {
                        fn.setBody(row.proposed);
                    } catch (Exception exc) {
                        row.verdict = "APPLY_THREW:" + exc.getClass().getSimpleName();
                        fail(row, "setBody threw " + exc);
                        continue;
                    }
                    AddressSetView body = fn.getBody();
                    row.postRanges = rangesText(body);
                    row.postBytes = body.getNumAddresses();
                    row.verdict = bodyDigest(body).equals(bodyDigest(row.proposed))
                        ? "APPLIED" : "APPLY_MISMATCH";
                    if (!"APPLIED".equals(row.verdict)) {
                        fail(row, "in-process verify failed");
                    }
                }
            } else if (settingBodies) {
                for (Row row : rows) {
                    row.verdict = "NOT_APPLIED_CLASSIFICATION_REFUSED";
                }
            } else if (planOnly) {
                for (Row row : rows) {
                    row.verdict = failures.isEmpty() ? "PLAN_WOULD_APPLY" : "PLAN_REFUSED";
                }
            }

            if (afterOne) {
                long halted = 0;
                for (Row row : rows) {
                    if ("HALTED_BEFORE_APPLY".equals(row.verdict)) {
                        halted++;
                    }
                }
                println("COHORT41_PARTIAL_STATE rowsApplied=" + (rows.size() - halted)
                    + " rowsPending=" + halted
                    + " outer_rollback_required=true"
                    + " recovery=RESTORE_VERIFIED_PRE_BACKUP");
            }

            long postFunctions = countInternalFunctions(fm);
            if (postFunctions != preFunctions) {
                fail(null, "function census moved " + preFunctions
                    + " -> " + postFunctions);
            }
            if (!probeMode && !planOnly && postFunctions != POST_FUNCTIONS) {
                fail(null, "POST function count " + postFunctions
                    + " != " + POST_FUNCTIONS);
            }

            // A deliberate self-sabotage run must never be able to commit, even
            // if some future edit made every gate miss it.
            commit = failures.isEmpty() && !planOnly && !faultMode;
            if (faultMode && failures.isEmpty()) {
                println("COHORT41_FAULT_UNDETECTED banner=NO-GATE-FIRED"
                    + " this_is_a_test_failure=true");
            }
            if (planOnly) {
                println("COHORT41_PLAN_ABORT banner=no-logical-change-persists"
                    + " failures=" + failures.size()
                    + " measurementsBelowWereTakenBeforeTheAbort=true");
            }
        } finally {
            currentProgram.endTransaction(tx, commit);
            if (!commit) {
                println("COHORT41_TRANSACTION_ABORTED"
                    + " everything_since_the_gate_sweep_rolled_back=true");
            }
        }

        long postFunctions = countInternalFunctions(fm);
        long postInstructions = listing.getNumInstructions();
        long postReferences = countAllReferences();
        long postBookmarks = bookmarkList().size();

        emit(outTsv, outJson, rows, mode, projectPath, manifestPath, manifestSha,
             manifestRaw.length, preFunctions, preInstructions, preReferences,
             preBookmarks, postFunctions, postInstructions, postReferences,
             postBookmarks);
        report(mode, rows, preFunctions, preInstructions, preReferences, preBookmarks,
               postFunctions, postInstructions, postReferences, postBookmarks);
        if (!failures.isEmpty()) {
            println("COHORT41_NO_MUTATION_PERFORMED");
        }
    }

    private void report(String mode, List<Row> rows, long preFunctions,
            long preInstructions, long preReferences, long preBookmarks,
            long postFunctions, long postInstructions, long postReferences,
            long postBookmarks) {
        long undefinedLeft = 0;
        long cleared = 0;
        for (Row row : rows) {
            undefinedLeft += row.postUndefBytes;
            cleared += row.clearedKinds.size();
        }
        if (failures.isEmpty()) {
            println("COHORT41_OK mode=" + mode + " rows=" + rows.size()
                + " preFunctions=" + preFunctions + " postFunctions=" + postFunctions
                + " preInstructions=" + preInstructions
                + " postInstructions=" + postInstructions
                + " preReferences=" + preReferences
                + " postReferences=" + postReferences
                + " preBookmarks=" + preBookmarks
                + " postBookmarks=" + postBookmarks
                + " clearedUnits=" + cleared
                + " admittedBytesStillUndefined=" + undefinedLeft);
        } else {
            println("COHORT41_FAIL mode=" + mode + " failures=" + failures.size());
            for (String message : failures) {
                println("COHORT41_GATE_FAIL " + message);
            }
        }
    }

    private void emit(Path outTsv, Path outJson, List<Row> rows, String mode,
            String projectPath, Path manifestPath, String manifestSha, long manifestBytes,
            long preFunctions, long preInstructions, long preReferences,
            long preBookmarks, long postFunctions, long postInstructions,
            long postReferences, long postBookmarks) throws Exception {
        StringBuilder tsv = new StringBuilder();
        tsv.append("addr\tname\tsubtype\tpreRanges\tpreBytes\tproposedRanges"
            + "\tproposedBytes\tdeltaBytes\taddedRanges\tpostRanges\tpostBytes"
            + "\tproposedDigest\tpostDigest\tpreInstrBytes\tpreDataBytes"
            + "\tpreUndefBytes\tpostInstrBytes\tpostDataBytes\tpostUndefBytes"
            + "\tclassifiedDelta\tphase1Passes\tresyncRounds\tclearedRanges"
            + "\tclearedKinds\tpreInstrCount\tpostInstrCount\tstillUndefined"
            + "\tescaped\tverdict\tgateFailures\n");
        for (Row row : rows) {
            tsv.append(row.addr).append('\t')
               .append(row.functionName).append('\t')
               .append(row.subtype).append('\t')
               .append(row.preRanges).append('\t')
               .append(row.preBytes).append('\t')
               .append(row.proposedRangesText).append('\t')
               .append(row.proposed == null ? -1 : row.proposed.getNumAddresses()).append('\t')
               .append(row.deltaBytes).append('\t')
               .append(row.added == null ? "" : rangesText(row.added)).append('\t')
               .append(row.postRanges).append('\t')
               .append(row.postBytes).append('\t')
               .append(row.proposed == null ? "" : bodyDigest(row.proposed)).append('\t')
               .append(row.postRanges.isEmpty() ? "" : bodyDigest(parseRanges(row.postRanges)))
               .append('\t')
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
               .append(row.verdict).append('\t')
               .append(String.join(" | ", row.gateFailures)).append('\n');
        }
        Files.write(outTsv, tsv.toString().getBytes(StandardCharsets.UTF_8));

        StringBuilder json = new StringBuilder();
        json.append("{\n  \"schema\": \"").append(SCHEMA).append("\",\n");
        json.append("  \"policy\": \"").append(POLICY).append("\",\n");
        json.append("  \"mode\": \"").append(jsonEscape(mode)).append("\",\n");
        json.append("  \"generatedAtUtc\": \"").append(Instant.now()).append("\",\n");
        json.append("  \"projectDir\": \"").append(jsonEscape(projectPath)).append("\",\n");
        json.append("  \"manifest\": {\"path\": \"")
            .append(jsonEscape(manifestPath.toString()))
            .append("\", \"bytes\": ").append(manifestBytes)
            .append(", \"sha256\": \"").append(manifestSha).append("\"},\n");
        json.append("  \"program\": {\"name\": \"").append(PROGRAM_NAME)
            .append("\", \"md5\": \"").append(PROGRAM_MD5)
            .append("\", \"sha256\": \"").append(PROGRAM_SHA256).append("\"},\n");
        json.append("  \"counts\": {\"rows\": ").append(rows.size())
            .append(", \"preFunctions\": ").append(preFunctions)
            .append(", \"postFunctions\": ").append(postFunctions)
            .append(", \"preInstructions\": ").append(preInstructions)
            .append(", \"postInstructions\": ").append(postInstructions)
            .append(", \"preReferences\": ").append(preReferences)
            .append(", \"postReferences\": ").append(postReferences)
            .append(", \"preBookmarks\": ").append(preBookmarks)
            .append(", \"postBookmarks\": ").append(postBookmarks).append("},\n");
        json.append("  \"failures\": [");
        for (int i = 0; i < failures.size(); i++) {
            json.append(i == 0 ? "" : ", ").append('"')
                .append(jsonEscape(failures.get(i))).append('"');
        }
        json.append("],\n");
        json.append("  \"notes\": [");
        for (int i = 0; i < notes.size(); i++) {
            json.append(i == 0 ? "" : ", ").append('"')
                .append(jsonEscape(notes.get(i))).append('"');
        }
        json.append("],\n");
        json.append("  \"verdict\": \"").append(failures.isEmpty() ? "PASS" : "FAIL")
            .append("\"\n}\n");
        Files.write(outJson, json.toString().getBytes(StandardCharsets.UTF_8));
    }
}
