//@category Symbol
//
// SCRATCH-REPLICA REHEARSAL ONLY for a 41-row function-boundary cohort.
//
// This script is LIVE_FORBIDDEN by construction: it refuses to run unless the
// open project's directory sits under a path segment named
// "boundary-rehearsal", and it refuses outright if the path looks like the
// maintainer project or the tracked repository snapshot.
//
// The only authorized mutation is Function.setBody() on the 41 preregistered
// entries, growing each body to its preregistered proposed range set.  No
// function is created or destroyed; no name, signature, comment, tag, symbol,
// data unit, byte, reference, or disassembly change is authorized, and the
// script asserts the program-scope instruction and function counts are
// unchanged after the mutation.
//
// Usage:
//   -postScript GhidraRehearseBoundaryCohort41.java
//       <manifest.tsv> <out.tsv> <out.ready.json>
//       <dry|apply|readback|probe-apply>
//
//   dry          all gates, no mutation (run the JVM with -readOnly)
//   apply        all gates + pinned cohort digest, then setBody
//   readback     read bodies back and compare to proposedRanges (-readOnly)
//   probe-apply  adverse testing: identical gates EXCEPT the pinned cohort
//                digest, so a deliberately corrupted manifest can prove the
//                geometry gates refuse.  Prints a PROBE_MODE banner.

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.CodeUnit;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryBlock;

import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

public class GhidraRehearseBoundaryCohort41 extends GhidraScript {

    private static final String SCHEMA = "bea.ghidra.boundary-cohort-41.rehearsal.v1";
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

    private static final int TARGET_COUNT = 41;
    private static final long MANIFEST_BYTES = 6217L;
    private static final String MANIFEST_SHA256 =
        "9abc5aedb1c7ff3c959670a714e457480e83ed6075b76a23cee5195e20399ed3";
    private static final String MANIFEST_HEADER =
        "addr\tcurrentRanges\tproposedRanges\tsubtype\tterminatorVa"
        + "\tterminatorBytes\tdeltaBytes\tbyteProof\tagreesWithNote";

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
        String verdict = "PENDING";
        final List<String> gateFailures = new ArrayList<>();
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
        boolean probeMode = "probe-apply".equals(mode);
        boolean mutating = "apply".equals(mode) || probeMode;
        boolean readback = "readback".equals(mode);
        if (!("dry".equals(mode) || "apply".equals(mode) || readback || probeMode)) {
            println("COHORT41_FAIL reason=bad_mode value=" + mode);
            return;
        }
        if (probeMode) {
            println("COHORT41_PROBE_MODE banner=adverse-refusal-testing"
                + " cohortDigestPin=DISABLED geometryGates=ENFORCED");
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
            println("COHORT41_REFUSE reason=project_not_in_rehearsal_scratch path=" + projectPath);
            return;
        }

        // ---- Gate 2: program identity. ----
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
        long preFunctions = countInternalFunctions(fm);
        long preInstructions = listing.getNumInstructions();
        if (preFunctions != PRE_FUNCTIONS) {
            fail(null, "PRE function count " + preFunctions + " != " + PRE_FUNCTIONS);
        }
        if (preInstructions != PRE_INSTRUCTIONS) {
            fail(null, "PRE instruction count " + preInstructions + " != " + PRE_INSTRUCTIONS);
        }

        // ---- Gate 3: manifest identity. ----
        byte[] manifestRaw = Files.readAllBytes(manifestPath);
        String manifestSha = sha256(manifestRaw);
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
                 preFunctions, preInstructions);
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
            // Before a mutation that is currentRanges; after one it is
            // proposedRanges.  Either way the check is against a fresh read of
            // the replica, never against the drop's ledger or shard rows.
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
        }

        boolean gatesPassed = failures.isEmpty();

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
                row.verdict = bodyDigest(body).equals(bodyDigest(row.proposed))
                    ? "PASS" : "FAIL_RANGE_MISMATCH";
            }
        } else if (mutating) {
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
                     manifestRaw.length, preFunctions, preInstructions,
                     countInternalFunctions(fm), listing.getNumInstructions());
                println("COHORT41_NO_MUTATION_PERFORMED");
                return;
            }
            for (Row row : rows) {
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
        } else {
            for (Row row : rows) {
                row.verdict = row.gateFailures.isEmpty() ? "WOULD_APPLY" : "WOULD_REFUSE";
            }
        }

        long postFunctions = countInternalFunctions(fm);
        long postInstructions = listing.getNumInstructions();
        if (mutating) {
            if (postFunctions != preFunctions) {
                fail(null, "function census moved " + preFunctions + " -> " + postFunctions);
            }
            if (postInstructions != preInstructions) {
                fail(null, "instruction count moved " + preInstructions
                    + " -> " + postInstructions);
            }
        }

        emit(outTsv, outJson, rows, mode, projectPath, manifestPath, manifestSha,
             manifestRaw.length, preFunctions, preInstructions, postFunctions,
             postInstructions);

        if (failures.isEmpty()) {
            println("COHORT41_OK mode=" + mode + " rows=" + rows.size()
                + " preFunctions=" + preFunctions + " postFunctions=" + postFunctions
                + " preInstructions=" + preInstructions
                + " postInstructions=" + postInstructions);
        } else {
            println("COHORT41_FAIL mode=" + mode + " failures=" + failures.size());
            for (String message : failures) {
                println("COHORT41_GATE_FAIL " + message);
            }
        }
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

    private void emit(Path outTsv, Path outJson, List<Row> rows, String mode,
            String projectPath, Path manifestPath, String manifestSha, long manifestBytes,
            long preFunctions, long preInstructions, long postFunctions,
            long postInstructions) throws Exception {
        StringBuilder tsv = new StringBuilder();
        tsv.append("addr\tname\tsubtype\tpreRanges\tpreBytes\tproposedRanges"
            + "\tproposedBytes\tdeltaBytes\taddedRanges\tpostRanges\tpostBytes"
            + "\tproposedDigest\tpostDigest\tverdict\tgateFailures\n");
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
            .append(", \"postInstructions\": ").append(postInstructions).append("},\n");
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
