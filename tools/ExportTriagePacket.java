//@category Battle Engine Aquila
//
// Read-only per-function triage-packet export. ONE invocation over an
// explicit address list emits one JSON packet per requested VA plus a
// run manifest and a READY receipt published last as the commit marker.
//
// Per packet (stable field names, schema bea.re.triage-packet.v1):
//   identity      entry point, tracked name, namespace/source types, tags,
//                 calling convention, signature, body ranges/digest
//   decompile     one fresh DecompInterface slice, produced read-only
//                 in memory (the program database is never modified)
//   xrefs         callers (inbound call references whose from-address sits
//                 in a function) and callees (outbound STATIC_DIRECT
//                 instruction flows)
//   strings       defined-string data referenced from inside the body,
//                 with every function that refers to each string
//   rtti/vtable   observed evidence only: slot-0 dword, executable-target
//                 test, functions holding a data reference to the entry
//                 point, slot-4 dword. Strict hierarchy proof stays with
//                 tools/re_rtti_vtables.py.
//   grade         campaign closure row joined by exact entry VA when the
//                 closure TSV is supplied (optional fourth argument)
//
// A requested VA without a function yields a status=NOT_FUNCTION packet;
// requested-but-absent evidence is recorded, never silently skipped.
//
// Usage:
//   -postScript ExportTriagePacket.java <addresses.txt> <output_dir>
//       <ready.json> [<closure.tsv>]
//
// Run analyzeHeadless with -readOnly and -noanalysis. This script makes no
// program/database changes: it refuses existing outputs, writes CREATE_NEW
// sibling temporaries, and publishes with no-clobber hard links. The READY
// receipt is published last; consumers reject a directory until it exists.

import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileOptions;
import ghidra.app.decompiler.DecompileResults;
import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.data.StringDataInstance;
import ghidra.program.model.listing.Data;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.RefType;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;
import ghidra.program.model.symbol.Symbol;

import java.io.BufferedWriter;
import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.UUID;

public class ExportTriagePacket extends GhidraScript {

    private static final String PACKET_SCHEMA = "bea.re.triage-packet.v1";
    private static final String MANIFEST_SCHEMA = "bea.re.triage-run-manifest.v1";
    private static final String READY_SCHEMA = "bea.re.triage-ready.v1";

    // gradeRow layout: gradeAfter, gradeBefore, closureClass, confidence,
    // source label, receiptSha256.
    private static final int GRADE_AFTER = 0;
    private static final int GRADE_BEFORE = 1;
    private static final int GRADE_CLASS = 2;
    private static final int GRADE_CONFIDENCE = 3;
    private static final int GRADE_SOURCE = 4;
    private static final int GRADE_RECEIPT = 5;

    private static String clean(String value) {
        if (value == null) {
            return "";
        }
        return value
            .replace("\\", "\\\\")
            .replace("\r", "\\r")
            .replace("\n", "\\n")
            .replace("\t", " ");
    }

    private static String json(String value) {
        StringBuilder result = new StringBuilder((value == null ? 0 : value.length()) + 16);
        result.append('"');
        for (int index = 0; index < value.length(); index++) {
            char item = value.charAt(index);
            switch (item) {
                case '"': result.append("\\\""); break;
                case '\\': result.append("\\\\"); break;
                case '\b': result.append("\\b"); break;
                case '\f': result.append("\\f"); break;
                case '\n': result.append("\\n"); break;
                case '\r': result.append("\\r"); break;
                case '\t': result.append("\\t"); break;
                default:
                    if (item < 0x20) {
                        result.append(String.format(Locale.ROOT, "\\u%04x", (int) item));
                    } else {
                        result.append(item);
                    }
            }
        }
        result.append('"');
        return result.toString();
    }

    private static String hex(Address address) {
        return "0x" + address.toString();
    }

    private static String hex(byte[] value) {
        StringBuilder result = new StringBuilder(value.length * 2);
        for (byte item : value) {
            result.append(String.format(Locale.ROOT, "%02x", item & 0xff));
        }
        return result.toString();
    }

    private static String sha256(byte[] raw) throws Exception {
        return hex(MessageDigest.getInstance("SHA-256").digest(raw));
    }

    private static String sha256(Path path) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        byte[] buffer = new byte[64 * 1024];
        try (java.io.InputStream input = Files.newInputStream(path)) {
            int read;
            while ((read = input.read(buffer)) >= 0) {
                if (read > 0) {
                    digest.update(buffer, 0, read);
                }
            }
        }
        return hex(digest.digest());
    }

    private static List<String> readAddressList(Path path) throws Exception {
        List<String> entries = new ArrayList<>();
        try (java.io.BufferedReader reader = Files.newBufferedReader(path, StandardCharsets.UTF_8)) {
            int ordinal = 0;
            String line;
            while ((line = reader.readLine()) != null) {
                ordinal++;
                String trimmed = line.trim();
                if (trimmed.isEmpty() || trimmed.startsWith("#")) {
                    continue;
                }
                String token = trimmed;
                int hash = token.indexOf('#');
                if (hash >= 0) {
                    token = token.substring(0, hash).trim();
                }
                if (!token.matches("(?i)0x[0-9a-f]{1,16}")) {
                    throw new IllegalArgumentException(
                        "address line " + ordinal + " is not a 0x-hex VA: " + trimmed);
                }
                String canonical = "0x" + token.substring(2).toLowerCase(Locale.ROOT);
                if (!entries.contains(canonical)) {
                    entries.add(canonical);
                }
            }
        }
        if (entries.isEmpty()) {
            throw new IllegalArgumentException("address list names no VA: " + path);
        }
        return entries;
    }

    private static Path checkedFinalPath(String value) throws Exception {
        return new File(value).getCanonicalFile().toPath();
    }

    private static Path siblingTemporary(Path destination, String token) {
        return destination.resolveSibling(
            "." + destination.getFileName().toString() + "." + token + ".tmp");
    }

    private static void deleteIfPresent(Path path) {
        if (path == null) {
            return;
        }
        try {
            Files.deleteIfExists(path);
        }
        catch (Exception ignored) {
            // An unlinked sibling temporary is never a READY result.
        }
    }

    private static void writeAndPublish(byte[] bytes, Path temporary, Path destination)
            throws Exception {
        try (java.io.OutputStream stream = Files.newOutputStream(temporary,
             StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE)) {
            stream.write(bytes);
        }
        Files.createLink(destination, temporary);
    }

    private static final class Edge {
        final String peer;
        final String peerName;
        final int sites;
        final boolean viaInstructionFlow;

        Edge(String peer, String peerName, int sites, boolean viaInstructionFlow) {
            this.peer = peer;
            this.peerName = peerName;
            this.sites = sites;
            this.viaInstructionFlow = viaInstructionFlow;
        }
    }

    // ------------------------------------------------------------------
    // Per-function evidence collection
    // ------------------------------------------------------------------

    private String bodyDigest(AddressSetView body) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        Memory memory = currentProgram.getMemory();
        for (AddressRange range : body) {
            digest.update(range.getMinAddress().toString().getBytes("UTF-8"));
            digest.update((byte) ':');
            digest.update(range.getMaxAddress().toString().getBytes("UTF-8"));
            digest.update((byte) ';');
        }
        byte[] buffer = new byte[64 * 1024];
        for (AddressRange range : body) {
            Address cursor = range.getMinAddress();
            Address end = range.getMaxAddress();
            while (cursor.compareTo(end) <= 0) {
                monitor.checkCancelled();
                long remaining = end.subtract(cursor) + 1;
                int requested = (int) Math.min((long) buffer.length, remaining);
                int read = memory.getBytes(cursor, buffer, 0, requested);
                if (read != requested) {
                    throw new IllegalStateException(
                        "short memory read at " + cursor + ": " + read + "/" + requested);
                }
                digest.update(buffer, 0, read);
                cursor = cursor.add(read);
            }
        }
        return hex(digest.digest());
    }

    private String decompile(Function function) {
        DecompInterface decompiler = new DecompInterface();
        decompiler.setOptions(new DecompileOptions());
        try {
            DecompileResults results =
                decompiler.decompileFunction(function, 120, monitor);
            if (results == null || !results.decompileCompleted()) {
                println("TRIAGE_PACKET_DECOMPILE_FAILED at " + hex(function.getEntryPoint())
                    + ": " + (results == null ? "no result" : results.getErrorMessage()));
                return null;
            }
            return results.getDecompiledFunction().getC();
        }
        catch (Exception exception) {
            println("TRIAGE_PACKET_DECOMPILE_FAILED at " + hex(function.getEntryPoint())
                + ": " + exception);
            return null;
        }
        finally {
            decompiler.dispose();
        }
    }

    /** Inbound call references to this entry point, grouped by caller. */
    private List<Edge> callerEdges(Function function) throws Exception {
        Map<String, Integer> sites = new LinkedHashMap<>();
        Map<String, String> names = new LinkedHashMap<>();
        ReferenceIterator references = currentProgram.getReferenceManager()
            .getReferencesTo(function.getEntryPoint());
        while (references.hasNext()) {
            Reference reference = references.next();
            if (!reference.getReferenceType().isCall()) {
                continue;
            }
            Function caller = currentProgram.getFunctionManager()
                .getFunctionContaining(reference.getFromAddress());
            if (caller == null) {
                continue;
            }
            String key = hex(caller.getEntryPoint());
            sites.put(key, sites.getOrDefault(key, 0) + 1);
            names.putIfAbsent(key, clean(caller.getName(true)));
        }

        // Attribution pass: a caller edge is "via instruction flow" when at
        // least one of the caller's call instructions flows straight here
        // (STATIC_DIRECT); edges that only appear through reference records
        // alone stay flagged false.
        Listing listing = currentProgram.getListing();
        List<Edge> edges = new ArrayList<>();
        for (Map.Entry<String, Integer> entry : sites.entrySet()) {
            boolean viaFlow = false;
            Function caller = currentProgram.getFunctionManager()
                .getFunctionAt(currentProgram.getAddressFactory().getAddress(entry.getKey()));
            if (caller != null) {
                InstructionIterator instructions =
                    listing.getInstructions(caller.getBody(), true);
                while (instructions.hasNext()) {
                    monitor.checkCancelled();
                    Instruction instruction = instructions.next();
                    if (!instruction.getFlowType().isCall()) {
                        continue;
                    }
                    for (Address destination : instruction.getFlows()) {
                        if (destination.equals(function.getEntryPoint())) {
                            viaFlow = true;
                            break;
                        }
                    }
                    if (viaFlow) {
                        break;
                    }
                }
            }
            edges.add(new Edge(entry.getKey(), names.get(entry.getKey()), entry.getValue(), viaFlow));
        }
        edges.sort((left, right) -> left.peer.compareTo(right.peer));
        return edges;
    }

    /** Outbound STATIC_DIRECT call edges resolved to internal functions. */
    private List<Edge> calleeEdges(Function function) throws Exception {
        Map<String, Integer> sites = new LinkedHashMap<>();
        Map<String, String> names = new LinkedHashMap<>();
        Listing listing = currentProgram.getListing();
        InstructionIterator instructions =
            listing.getInstructions(function.getBody(), true);
        while (instructions.hasNext()) {
            monitor.checkCancelled();
            Instruction instruction = instructions.next();
            if (!instruction.getFlowType().isCall()) {
                continue;
            }
            for (Address destination : instruction.getFlows()) {
                Function callee =
                    currentProgram.getFunctionManager().getFunctionAt(destination);
                if (callee == null || callee.isExternal()) {
                    continue;
                }
                String key = hex(callee.getEntryPoint());
                sites.put(key, sites.getOrDefault(key, 0) + 1);
                names.putIfAbsent(key, clean(callee.getName(true)));
            }
        }
        List<Edge> edges = new ArrayList<>();
        for (Map.Entry<String, Integer> entry : sites.entrySet()) {
            edges.add(new Edge(entry.getKey(), names.get(entry.getKey()), entry.getValue(), true));
        }
        edges.sort((left, right) -> left.peer.compareTo(right.peer));
        return edges;
    }

    /** Defined strings referenced from inside the body, sorted by address. */
    private TreeMap<String, String[]> stringRows(Function function) throws Exception {
        TreeMap<String, String[]> rows = new TreeMap<>();
        TreeSet<String> seen = new TreeSet<>();
        Listing listing = currentProgram.getListing();
        InstructionIterator instructions =
            listing.getInstructions(function.getBody(), true);
        while (instructions.hasNext()) {
            monitor.checkCancelled();
            Instruction instruction = instructions.next();
            for (Reference reference : instruction.getReferencesFrom()) {
                Data data = listing.getDataAt(reference.getToAddress());
                if (data == null || !data.isDefined()) {
                    continue;
                }
                StringDataInstance instance =
                    StringDataInstance.getStringDataInstance(data);
                if (instance == null) {
                    continue;
                }
                String value = instance.getStringValue();
                if (value == null) {
                    continue;
                }
                Address dataAddress = data.getAddress();
                if (!seen.add(hex(dataAddress))) {
                    continue;
                }
                TreeSet<String> referrers = new TreeSet<>();
                ReferenceIterator backRefs = currentProgram.getReferenceManager()
                    .getReferencesTo(dataAddress);
                while (backRefs.hasNext()) {
                    Function container = currentProgram.getFunctionManager()
                        .getFunctionContaining(backRefs.next().getFromAddress());
                    if (container != null) {
                        referrers.add(hex(container.getEntryPoint()));
                    }
                }
                StringBuilder referrerArray = new StringBuilder("[");
                int index = 0;
                for (String referrer : referrers) {
                    if (index++ > 0) {
                        referrerArray.append(", ");
                    }
                    referrerArray.append('"').append(referrer).append('"');
                }
                referrerArray.append(']');
                rows.put(hex(dataAddress), new String[] {
                    dataAddress.getOffset() >= 0 ? hex(dataAddress) : "",
                    Integer.toString(data.getLength()),
                    sha256(value.getBytes(StandardCharsets.UTF_8)),
                    json(clean(value)),
                    referrerArray.toString()});
            }
        }
        return rows;
    }

    /** Quoted, comma-joined function entries holding any non-call reference to target. */
    private String dataReferrers(Address target) {
        TreeSet<String> functions = new TreeSet<>();
        ReferenceIterator references =
            currentProgram.getReferenceManager().getReferencesTo(target);
        while (references.hasNext()) {
            Reference reference = references.next();
            RefType refType = reference.getReferenceType();
            if (refType.isCall() || refType.isJump()) {
                continue;
            }
            Function container = currentProgram.getFunctionManager()
                .getFunctionContaining(reference.getFromAddress());
            if (container != null) {
                functions.add(hex(container.getEntryPoint()));
            }
        }
        StringBuilder into = new StringBuilder();
        int index = 0;
        for (String entry : functions) {
            if (index++ > 0) {
                into.append(", ");
            }
            into.append('"').append(entry).append('"');
        }
        return into.toString();
    }

    /** Observed vtable-pointer evidence around the entry point (no hierarchy claims). */
    private String vtableJson(Function function) throws Exception {
        Memory memory = currentProgram.getMemory();
        Address entry = function.getEntryPoint();
        byte[] firstFour = new byte[4];
        int read;
        try {
            read = memory.getBytes(entry, firstFour);
        }
        catch (Exception exception) {
            return "null";
        }
        if (read != 4) {
            return "null";
        }
        long firstWord = 0;
        for (int index = 3; index >= 0; index--) {
            firstWord = (firstWord << 8) | (firstFour[index] & 0xffL);
        }
        Address pointerTarget =
            currentProgram.getAddressFactory().getAddress(String.format(Locale.ROOT, "%08x", firstWord));
        MemoryBlock block;
        try {
            block = memory.getBlock(pointerTarget);
        }
        catch (Exception exception) {
            block = null;
        }
        boolean pointsIntoExecutable = block != null && block.isExecute();

        StringBuilder into = new StringBuilder();
        String referrers = dataReferrers(entry);
        into.append("{\n");
        into.append("      \"slotZeroDword\": \"").append(hex(firstFour)).append("\",\n");
        into.append("      \"pointsToExecutable\": ").append(pointsIntoExecutable).append(",\n");
        into.append("      \"referencingFunctions\": [").append(referrers).append("],\n");
        if (pointsIntoExecutable) {
            Function firstSlot = currentProgram.getFunctionManager().getFunctionAt(pointerTarget);
            into.append("      \"vtableFirstSlot\": \"").append(hex(pointerTarget)).append("\",\n");
            into.append("      \"vtableFirstSlotFunction\": ");
            if (firstSlot == null) {
                into.append("null,\n");
            } else {
                into.append('"').append(hex(firstSlot.getEntryPoint())).append("\",\n");
            }
            into.append("      \"slotMinusFourDword\": ");
            try {
                byte[] locatorBytes = new byte[4];
                int locatorRead = memory.getBytes(pointerTarget.subtract(4), locatorBytes);
                if (locatorRead == 4) {
                    into.append('"').append(hex(locatorBytes)).append('"');
                } else {
                    into.append("null");
                }
            }
            catch (Exception exception) {
                into.append("null");
            }
            into.append("\n");
        }
        else {
            into.append("      \"vtableFirstSlot\": null,\n");
            into.append("      \"vtableFirstSlotFunction\": null,\n");
            into.append("      \"slotMinusFourDword\": null\n");
        }
        into.append("    }");
        return into.toString();
    }

    private String campaignGradeJson(Map<String, String[]> grades, String entryVa) {
        String[] row = grades.get(entryVa.toLowerCase(Locale.ROOT));
        StringBuilder into = new StringBuilder("{\n");
        if (row == null) {
            into.append("      \"present\": false,\n");
            into.append("      \"gradeBefore\": null,\n");
            into.append("      \"gradeAfter\": null,\n");
            into.append("      \"closureClass\": null,\n");
            into.append("      \"confidence\": null,\n");
            into.append("      \"source\": null,\n");
            into.append("      \"receiptSha256\": null\n");
        }
        else {
            into.append("      \"present\": true,\n");
            into.append("      \"gradeBefore\": ").append(json(clean(row[GRADE_BEFORE]))).append(",\n");
            into.append("      \"gradeAfter\": ").append(json(clean(row[GRADE_AFTER]))).append(",\n");
            into.append("      \"closureClass\": ").append(json(clean(row[GRADE_CLASS]))).append(",\n");
            into.append("      \"confidence\": ").append(json(clean(row[GRADE_CONFIDENCE]))).append(",\n");
            into.append("      \"source\": ").append(json(clean(row[GRADE_SOURCE]))).append(",\n");
            into.append("      \"receiptSha256\": ").append(json(clean(row[GRADE_RECEIPT]))).append("\n");
        }
        into.append("    }");
        return into.toString();
    }

    /**
     * Loads the optional closure TSV once per run: entryVa -> grade columns.
     * Absence of the file is recorded per packet as present=false, not fatal.
     */
    private Map<String, String[]> loadGrades(Path closureTsv) throws Exception {
        Map<String, String[]> grades = new LinkedHashMap<>();
        if (closureTsv == null || !Files.isRegularFile(closureTsv)) {
            return grades;
        }
        try (java.io.BufferedReader reader =
                 Files.newBufferedReader(closureTsv, StandardCharsets.UTF_8)) {
            String header = reader.readLine();
            if (header == null) {
                throw new IllegalStateException("closure TSV is empty: " + closureTsv);
            }
            String[] columns = header.split("\t", -1);
            Map<String, Integer> columnIndex = new LinkedHashMap<>();
            for (int index = 0; index < columns.length; index++) {
                columnIndex.put(columns[index].trim(), index);
            }
            for (String needed : new String[] {
                "entryVa", "gradeBefore", "gradeAfter", "closureClass",
                "confidence", "receiptSha256"}) {
                if (!columnIndex.containsKey(needed)) {
                    throw new IllegalStateException(
                        "closure TSV lacks column " + needed + ": " + closureTsv);
                }
            }
            String line;
            while ((line = reader.readLine()) != null) {
                if (line.trim().isEmpty()) {
                    continue;
                }
                String[] fields = line.split("\t", -1);
                String va = fields[columnIndex.get("entryVa")].trim().toLowerCase(Locale.ROOT);
                grades.put(va, new String[] {
                    fields[columnIndex.get("gradeAfter")],
                    fields[columnIndex.get("gradeBefore")],
                    fields[columnIndex.get("closureClass")],
                    fields[columnIndex.get("confidence")],
                    closureTsv.getFileName().toString(),
                    fields[columnIndex.get("receiptSha256")]});
            }
        }
        return grades;
    }

    // ------------------------------------------------------------------

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length < 3 || args.length > 4) {
            throw new IllegalArgumentException(
                "usage: ExportTriagePacket.java <addresses.txt> <output_dir> <ready.json>"
                    + " [<closure.tsv>]");
        }

        Path addressesFinal = checkedFinalPath(args[0]);
        Path outputRoot = checkedFinalPath(args[1]);
        Path readyFinal = checkedFinalPath(args[2]);
        Path closureTsv = args.length == 4 ? checkedFinalPath(args[3]) : null;
        if (!Files.isRegularFile(addressesFinal)) {
            throw new IllegalArgumentException("address list is missing: " + addressesFinal);
        }
        if (!Files.isDirectory(outputRoot)) {
            throw new IllegalArgumentException(
                "output directory must already exist: " + outputRoot);
        }
        if (!outputRoot.equals(readyFinal.getParent())) {
            throw new IllegalArgumentException(
                "READY receipt must sit directly inside the output directory");
        }
        List<String> entries = readAddressList(addressesFinal);

        Path manifestFinal = outputRoot.resolve("run-manifest.json");

        // Incremental ownership belongs to the driver: every packet named by a
        // fresh run must be absent here, or the driver ran --force and removed
        // them first. A stale packet must never silently shadow a fresh run.
        for (String entry : entries) {
            Path packet = outputRoot.resolve("packet-" + entry + ".json");
            if (Files.exists(packet)) {
                throw new IllegalStateException(
                    "packet already exists (driver incremental/--force contract violated): "
                        + packet);
            }
        }
        if (Files.exists(manifestFinal) || Files.exists(readyFinal)) {
            throw new IllegalStateException(
                "run-manifest.json / triage-ready.json already exist in " + outputRoot);
        }

        Map<String, String[]> grades = loadGrades(closureTsv);
        String gradesSha256 = closureTsv != null && Files.isRegularFile(closureTsv)
            ? sha256(closureTsv) : "";
        String gradesLabel = closureTsv != null && Files.isRegularFile(closureTsv)
            ? closureTsv.getFileName().toString() : "";

        int packetsWritten = 0;
        List<String> packetNames = new ArrayList<>();
        String executableSha256 =
            currentProgram.getExecutableSHA256().toLowerCase(Locale.ROOT);
        String executableMd5 =
            currentProgram.getExecutableMD5().toLowerCase(Locale.ROOT);

        String token = UUID.randomUUID().toString();
        List<Path> temporaryPaths = new ArrayList<>();
        try {
            for (String entry : entries) {
                monitor.checkCancelled();
                Address address = toAddress(entry);
                Function function =
                    currentProgram.getFunctionManager().getFunctionAt(address);
                Path packetFinal = outputRoot.resolve("packet-" + entry + ".json");
                Path packetTemporary = siblingTemporary(packetFinal, token);
                temporaryPaths.add(packetTemporary);

                String packetText;
                if (function == null) {
                    MemoryBlock requestBlock;
                    try {
                        requestBlock = currentProgram.getMemory().getBlock(address);
                    }
                    catch (Exception exception) {
                        requestBlock = null;
                    }
                    StringBuilder into = new StringBuilder();
                    into.append("{\n");
                    into.append("  \"schema\": \"").append(PACKET_SCHEMA).append("\",\n");
                    into.append("  \"status\": \"NOT_FUNCTION\",\n");
                    into.append("  \"requestedVa\": \"").append(entry).append("\",\n");
                    into.append("  \"executableSha256\": \"").append(executableSha256).append("\",\n");
                    into.append("  \"imageBase\": \"").append(hex(currentProgram.getImageBase())).append("\",\n");
                    into.append("  \"section\": ")
                        .append(requestBlock == null
                            ? "null"
                            : json(clean(requestBlock.getName())))
                        .append("\n");
                    into.append("}\n");
                    packetText = into.toString();
                    println("TRIAGE_PACKET_NOT_FUNCTION va=" + entry);
                }
                else {
                    Symbol symbol = function.getSymbol();
                    String signature =
                        clean(function.getSignature().getPrototypeString(true));
                    List<String> tagNames = new ArrayList<>();
                    for (FunctionTag tag : function.getTags()) {
                        tagNames.add(tag.getName());
                    }
                    Collections.sort(tagNames);
                    AddressSetView body = function.getBody();

                    StringBuilder into = new StringBuilder(64 * 1024);
                    into.append("{\n");
                    into.append("  \"schema\": \"").append(PACKET_SCHEMA).append("\",\n");
                    into.append("  \"status\": \"READY\",\n");
                    into.append("  \"requestedVa\": \"").append(entry).append("\",\n");
                    into.append("  \"entryVa\": \"").append(hex(function.getEntryPoint())).append("\",\n");
                    into.append("  \"name\": ").append(json(clean(function.getName()))).append(",\n");
                    into.append("  \"namespace\": ")
                        .append(json(clean(function.getParentNamespace().getName()))).append(",\n");
                    into.append("  \"nameSource\": \"")
                        .append(symbol == null ? "" : symbol.getSource().toString()).append("\",\n");
                    into.append("  \"signatureSource\": \"")
                        .append(function.getSignatureSource().toString()).append("\",\n");
                    into.append("  \"isThunk\": ").append(function.isThunk()).append(",\n");
                    into.append("  \"callingConvention\": ")
                        .append(json(clean(function.getCallingConventionName()))).append(",\n");
                    into.append("  \"signature\": ").append(json(signature)).append(",\n");
                    into.append("  \"tags\": [");
                    for (int index = 0; index < tagNames.size(); index++) {
                        if (index > 0) {
                            into.append(", ");
                        }
                        into.append(json(tagNames.get(index)));
                    }
                    into.append("],\n");
                    into.append("  \"bodyBytes\": ").append(body.getNumAddresses()).append(",\n");
                    into.append("  \"bodyMin\": \"")
                        .append(body.getMinAddress() == null ? "" : hex(body.getMinAddress()))
                        .append("\",\n");
                    into.append("  \"bodyMax\": \"")
                        .append(body.getMaxAddress() == null ? "" : hex(body.getMaxAddress()))
                        .append("\",\n");
                    into.append("  \"bodyRangeCount\": ")
                        .append(body.getNumAddressRanges()).append(",\n");
                    into.append("  \"bodyDigest\": \"").append(bodyDigest(body)).append("\",\n");
                    into.append("  \"executableSha256\": \"").append(executableSha256).append("\",\n");
                    into.append("  \"programMd5\": \"").append(executableMd5).append("\",\n");
                    into.append("  \"imageBase\": \"")
                        .append(hex(currentProgram.getImageBase())).append("\",\n");

                    String code = decompile(function);
                    into.append("  \"decompiled\": ").append(code != null).append(",\n");
                    into.append("  \"decompile\": ");
                    if (code == null) {
                        into.append("null,\n");
                    }
                    else {
                        into.append(json(code)).append(",\n");
                    }

                    List<Edge> callers = callerEdges(function);
                    List<Edge> callees = calleeEdges(function);
                    into.append("  \"callers\": [");
                    for (int index = 0; index < callers.size(); index++) {
                        Edge edge = callers.get(index);
                        if (index > 0) {
                            into.append(", ");
                        }
                        into.append("{\"caller\": \"").append(edge.peer)
                            .append("\", \"name\": ").append(json(edge.peerName))
                            .append(", \"sites\": ").append(edge.sites)
                            .append(", \"viaInstructionFlow\": ")
                            .append(edge.viaInstructionFlow)
                            .append("}");
                    }
                    into.append("],\n");
                    into.append("  \"callees\": [");
                    for (int index = 0; index < callees.size(); index++) {
                        Edge edge = callees.get(index);
                        if (index > 0) {
                            into.append(", ");
                        }
                        into.append("{\"callee\": \"").append(edge.peer)
                            .append("\", \"name\": ").append(json(edge.peerName))
                            .append(", \"sites\": ").append(edge.sites)
                            .append(", \"kind\": \"STATIC_DIRECT\"}");
                    }
                    into.append("],\n");

                    into.append("  \"stringRefs\": [");
                    boolean firstRow = true;
                    for (Map.Entry<String, String[]> row : stringRows(function).entrySet()) {
                        if (!firstRow) {
                            into.append(", ");
                        }
                        firstRow = false;
                        String[] fields = row.getValue();
                        into.append("{\"address\": \"").append(fields[0])
                            .append("\", \"length\": ").append(fields[1])
                            .append(", \"valueUtf8Sha256\": \"").append(fields[2])
                            .append("\", \"value\": ").append(fields[3])
                            .append(", \"referringFunctions\": ").append(fields[4])
                            .append("}");
                    }
                    into.append("],\n");

                    into.append("  \"vtable\": ").append(vtableJson(function)).append(",\n");
                    into.append("  \"campaignGrade\": ")
                        .append(campaignGradeJson(grades, entry)).append("\n");
                    into.append("}\n");
                    packetText = into.toString();
                    println("TRIAGE_PACKET_OK va=" + entry
                        + " name=" + clean(function.getName())
                        + " bytes=" + body.getNumAddresses());
                }

                writeAndPublish(packetText.getBytes(StandardCharsets.UTF_8),
                    packetTemporary, packetFinal);
                packetNames.add(packetFinal.getFileName().toString());
                packetsWritten++;
            }

            // --- run manifest ---
            Path manifestTemporary = siblingTemporary(manifestFinal, token);
            temporaryPaths.add(manifestTemporary);
            StringBuilder manifest = new StringBuilder();
            manifest.append("{\n");
            manifest.append("  \"schema\": \"").append(MANIFEST_SCHEMA).append("\",\n");
            manifest.append("  \"programName\": ")
                .append(json(clean(currentProgram.getName()))).append(",\n");
            manifest.append("  \"executableSha256\": \"").append(executableSha256).append("\",\n");
            manifest.append("  \"programMd5\": \"").append(executableMd5).append("\",\n");
            manifest.append("  \"imageBase\": \"")
                .append(hex(currentProgram.getImageBase())).append("\",\n");
            manifest.append("  \"language\": ")
                .append(json(clean(currentProgram.getLanguageID().toString()))).append(",\n");
            manifest.append("  \"addressList\": ")
                .append(json(addressesFinal.getFileName().toString())).append(",\n");
            manifest.append("  \"packetsWritten\": ").append(packetsWritten).append(",\n");
            manifest.append("  \"campaignGradesSource\": ")
                .append(gradesLabel.isEmpty() ? "null" : json(gradesLabel)).append(",\n");
            manifest.append("  \"campaignGradesSha256\": ")
                .append(gradesSha256.isEmpty() ? "null" : "\"" + gradesSha256 + "\"")
                .append(",\n");
            manifest.append("  \"packets\": {\n");
            int manifestIndex = 0;
            for (String name : packetNames) {
                Path packetPath = outputRoot.resolve(name);
                manifest.append("    \"").append(name).append("\": {\"sha256\": \"")
                    .append(sha256(packetPath)).append("\"}");
                manifest.append(++manifestIndex < packetNames.size() ? ",\n" : "\n");
            }
            manifest.append("  }\n}\n");
            writeAndPublish(manifest.toString().getBytes(StandardCharsets.UTF_8),
                manifestTemporary, manifestFinal);

            // --- READY receipt, published last as the commit marker ---
            Path readyTemporary = siblingTemporary(readyFinal, token);
            temporaryPaths.add(readyTemporary);
            StringBuilder ready = new StringBuilder();
            ready.append("{\n");
            ready.append("  \"schema\": \"").append(READY_SCHEMA).append("\",\n");
            ready.append("  \"status\": \"READY\",\n");
            ready.append("  \"programName\": ")
                .append(json(clean(currentProgram.getName()))).append(",\n");
            ready.append("  \"executableSha256\": \"").append(executableSha256).append("\",\n");
            ready.append("  \"packetsWritten\": ").append(packetsWritten).append(",\n");
            ready.append("  \"manifest\": {\"sha256\": \"")
                .append(sha256(manifestFinal)).append("\"},\n");
            ready.append("  \"outputDirName\": ")
                .append(json(outputRoot.getFileName().toString())).append("\n");
            ready.append("}\n");
            writeAndPublish(ready.toString().getBytes(StandardCharsets.UTF_8),
                readyTemporary, readyFinal);

            println("TRIAGE_PACKETS_READY count=" + packetsWritten
                + " exe=" + executableSha256);
        }
        catch (Exception exception) {
            // Partial publication without READY is a failed run: consumers
            // reject the directory until triage-ready.json exists.
            println("TRIAGE_PACKETS_FAILED; partial outputs carry no READY and stay untrusted");
            throw exception;
        }
        finally {
            for (Path temporary : temporaryPaths) {
                deleteIfPresent(temporary);
            }
        }
    }

    private Address toAddress(String textual) {
        return currentProgram.getAddressFactory().getAddress(textual);
    }
}
