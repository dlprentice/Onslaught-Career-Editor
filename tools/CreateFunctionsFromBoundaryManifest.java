//@category Symbol
//
// Create or verify specimen-bound function entries only when Ghidra's natural
// body inference reproduces an exact preregistered address-set envelope.
//
// Usage:
//   -postScript CreateFunctionsFromBoundaryManifest.java \
//       <manifest.tsv> <expected_sha256> <expected_count> \
//       <out.tsv> <out.ready.json> <probe|apply|readback>

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressIterator;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;

import java.io.File;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

public class CreateFunctionsFromBoundaryManifest extends GhidraScript {

    private static final String SCHEMA = "bea-ghidra-function-body-envelope.v3";
    private static final String EXPECTED_PROGRAM_NAME = "BEA.exe";
    private static final String EXPECTED_PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55";
    private static final String EXPECTED_PROGRAM_SHA256 =
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
    private static final String EXPECTED_IMAGE_BASE = "00400000";
    private static final String EXPECTED_LANGUAGE = "x86:LE:32:default";
    private static final String EXPECTED_COMPILER_SPEC = "windows";
    private static final String EXPECTED_BLOCK = ".text";
    private static final String HEADER =
        "entry\texpectedRanges\texpectedBodyBytes\texpectedRangeDigest"
        + "\texpectedBodyBytesSha256\texpectedInstructionCount\texpectedIsThunk"
        + "\texpectedThunkTarget\tforbiddenEntries"
        + "\tresidualEntityKeys\tquestionIds\tcontractIds\tpromotionLane";

    private static class Target {
        final String entryText;
        final Address entry;
        final String expectedRanges;
        final AddressSet expectedBody;
        final long expectedBodyBytes;
        final String expectedRangeDigest;
        final String expectedBodyBytesSha256;
        final long expectedInstructionCount;
        final boolean expectedIsThunk;
        final Address expectedThunkTarget;
        final String expectedThunkTargetText;
        final List<Address> forbiddenEntries;
        final String forbiddenText;
        final String residualEntityKeys;
        final String questionIds;
        final String contractIds;
        final String promotionLane;

        Target(
                String entryText,
                Address entry,
                String expectedRanges,
                AddressSet expectedBody,
                long expectedBodyBytes,
                String expectedRangeDigest,
                String expectedBodyBytesSha256,
                long expectedInstructionCount,
                boolean expectedIsThunk,
                Address expectedThunkTarget,
                String expectedThunkTargetText,
                List<Address> forbiddenEntries,
                String forbiddenText,
                String residualEntityKeys,
                String questionIds,
                String contractIds,
                String promotionLane) {
            this.entryText = entryText;
            this.entry = entry;
            this.expectedRanges = expectedRanges;
            this.expectedBody = expectedBody;
            this.expectedBodyBytes = expectedBodyBytes;
            this.expectedRangeDigest = expectedRangeDigest;
            this.expectedBodyBytesSha256 = expectedBodyBytesSha256;
            this.expectedInstructionCount = expectedInstructionCount;
            this.expectedIsThunk = expectedIsThunk;
            this.expectedThunkTarget = expectedThunkTarget;
            this.expectedThunkTargetText = expectedThunkTargetText;
            this.forbiddenEntries = forbiddenEntries;
            this.forbiddenText = forbiddenText;
            this.residualEntityKeys = residualEntityKeys;
            this.questionIds = questionIds;
            this.contractIds = contractIds;
            this.promotionLane = promotionLane;
        }
    }

    private static class Observation {
        final Target target;
        final String status;
        final String name;
        final String nameSource;
        final String actualRanges;
        final long actualBodyBytes;
        final String actualRangeDigest;
        final String actualBodyBytesSha256;
        final long actualInstructionCount;
        final boolean actualIsThunk;
        final String actualThunkTarget;
        final String note;

        Observation(
                Target target,
                String status,
                String name,
                String nameSource,
                String actualRanges,
                long actualBodyBytes,
                String actualRangeDigest,
                String actualBodyBytesSha256,
                long actualInstructionCount,
                boolean actualIsThunk,
                String actualThunkTarget,
                String note) {
            this.target = target;
            this.status = status;
            this.name = name;
            this.nameSource = nameSource;
            this.actualRanges = actualRanges;
            this.actualBodyBytes = actualBodyBytes;
            this.actualRangeDigest = actualRangeDigest;
            this.actualBodyBytesSha256 = actualBodyBytesSha256;
            this.actualInstructionCount = actualInstructionCount;
            this.actualIsThunk = actualIsThunk;
            this.actualThunkTarget = actualThunkTarget;
            this.note = note;
        }
    }

    private static String hex(byte[] bytes) {
        StringBuilder out = new StringBuilder(bytes.length * 2);
        for (byte value : bytes) {
            out.append(String.format(Locale.ROOT, "%02x", value & 0xff));
        }
        return out.toString();
    }

    private static String sha256(byte[] bytes) throws Exception {
        return hex(MessageDigest.getInstance("SHA-256").digest(bytes));
    }

    private static String clean(String value) {
        if (value == null) {
            return "";
        }
        return value.replace("\\", "\\\\")
            .replace("\r", "\\r")
            .replace("\n", "\\n")
            .replace("\t", " ");
    }

    private static String json(String value) {
        if (value == null) {
            return "";
        }
        return value.replace("\\", "\\\\")
            .replace("\"", "\\\"")
            .replace("\r", "\\r")
            .replace("\n", "\\n")
            .replace("\t", "\\t");
    }

    private static String canonical(Address address) {
        return "0x" + address.toString().toLowerCase(Locale.ROOT);
    }

    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new IllegalStateException(message);
        }
    }

    private static void requireEqual(String label, String expected, String actual) {
        if (!expected.equals(actual)) {
            throw new IllegalStateException(
                label + " mismatch expected=" + expected + " actual=" + actual);
        }
    }

    private static long positiveLong(String value, String label) {
        try {
            long parsed = Long.parseLong(value);
            if (parsed <= 0) {
                throw new IllegalArgumentException(label + " must be positive");
            }
            return parsed;
        } catch (NumberFormatException ex) {
            throw new IllegalArgumentException(label + " must be a positive decimal integer", ex);
        }
    }

    private static String requireHash(String value, String label) {
        String normalized = value == null ? "" : value.trim();
        if (!normalized.matches("[0-9a-f]{64}")) {
            throw new IllegalArgumentException(label + " must be 64 lowercase hexadecimal characters");
        }
        return normalized;
    }

    private static String requireMode(String value) {
        String mode = value == null ? "" : value.trim().toLowerCase(Locale.ROOT);
        if (!mode.equals("probe") && !mode.equals("apply") && !mode.equals("readback")) {
            throw new IllegalArgumentException("mode must be exactly probe, apply, or readback");
        }
        return mode;
    }

    private static boolean requireBoolean(String value, String label) {
        if ("true".equals(value)) {
            return true;
        }
        if ("false".equals(value)) {
            return false;
        }
        throw new IllegalArgumentException(label + " must be exactly true or false");
    }

    private static File requireNewOutput(String value, String label) throws Exception {
        File file = new File(value).getCanonicalFile();
        if (file.exists()) {
            throw new IllegalArgumentException(label + " already exists: " + file);
        }
        File parent = file.getParentFile();
        if (parent == null || !parent.isDirectory()) {
            throw new IllegalArgumentException(label + " parent is not an existing directory: " + file);
        }
        return file;
    }

    private static File stageAtomic(File target, byte[] content) throws Exception {
        File parent = target.getParentFile();
        File partial = new File(parent, "." + target.getName() + ".partial-" + UUID.randomUUID());
        try (FileChannel channel = FileChannel.open(
                partial.toPath(), StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE)) {
            ByteBuffer buffer = ByteBuffer.wrap(content);
            while (buffer.hasRemaining()) {
                channel.write(buffer);
            }
            channel.force(true);
        }
        return partial;
    }

    private static void publishStaged(File partial, File target) throws Exception {
        if (!partial.getParentFile().equals(target.getParentFile())) {
            throw new IllegalStateException("staged and final receipts must share one directory");
        }
        Files.createLink(target.toPath(), partial.toPath());
        Files.delete(partial.toPath());
    }

    private static void discardStaged(File partial) throws Exception {
        if (partial != null) {
            Files.deleteIfExists(partial.toPath());
        }
    }

    private static void preflightAtomicWrite(File target, String label) throws Exception {
        File parent = target.getParentFile();
        File source = new File(parent, "." + target.getName() + ".write-probe-" + UUID.randomUUID());
        File linked = new File(parent, "." + target.getName() + ".link-probe-" + UUID.randomUUID());
        try {
            Files.write(
                source.toPath(), new byte[] { 0 },
                StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE);
            Files.createLink(linked.toPath(), source.toPath());
        } catch (Exception ex) {
            throw new IllegalStateException(
                label + " parent cannot publish a create-new receipt: " + parent, ex);
        } finally {
            Files.deleteIfExists(source.toPath());
            Files.deleteIfExists(linked.toPath());
        }
    }

    private byte[] readToolSource() throws Exception {
        try (InputStream stream = getSourceFile().getInputStream()) {
            return stream.readAllBytes();
        }
    }

    private Address parseAddress(String value, String label) {
        if (value == null || !value.matches("0x[0-9a-f]{8}")) {
            throw new IllegalArgumentException(label + " must be one canonical lowercase address: " + value);
        }
        Address address = toAddr(value);
        if (address == null || !canonical(address).equals(value)) {
            throw new IllegalArgumentException(label + " does not resolve canonically: " + value);
        }
        return address;
    }

    private AddressSet parseRanges(String value, String entryText) {
        if (value == null || value.isEmpty()) {
            throw new IllegalArgumentException("expectedRanges is empty at " + entryText);
        }
        AddressSet body = new AddressSet();
        Address priorEnd = null;
        String[] pieces = value.split(";", -1);
        for (String piece : pieces) {
            if (!piece.matches("0x[0-9a-f]{8}-0x[0-9a-f]{8}")) {
                throw new IllegalArgumentException("malformed expected range at " + entryText + ": " + piece);
            }
            String[] bounds = piece.split("-", -1);
            Address start = parseAddress(bounds[0], "range start");
            Address endExclusive = parseAddress(bounds[1], "range endExclusive");
            require(start.compareTo(endExclusive) < 0, "empty/reversed expected range at " + entryText);
            if (priorEnd != null) {
                require(priorEnd.compareTo(start) < 0, "expected ranges overlap or touch at " + entryText);
            }
            body.addRange(start, endExclusive.subtract(1));
            priorEnd = endExclusive;
        }
        require(canonicalRanges(body).equals(value), "expectedRanges is not canonical at " + entryText);
        return body;
    }

    private List<Address> parseAddressList(String value, String label) {
        List<Address> addresses = new ArrayList<>();
        if (value == null || value.isEmpty()) {
            return addresses;
        }
        Set<String> seen = new HashSet<>();
        for (String piece : value.split(";", -1)) {
            Address address = parseAddress(piece, label);
            require(seen.add(piece), "duplicate " + label + ": " + piece);
            addresses.add(address);
        }
        return addresses;
    }

    private List<Target> loadTargets(byte[] inputBytes, int expectedCount) throws Exception {
        require(inputBytes.length > 0, "manifest is empty");
        require(inputBytes[0] != (byte) 0xef, "manifest must be UTF-8 without a BOM");
        String text = new String(inputBytes, StandardCharsets.UTF_8);
        require(text.indexOf('\r') < 0, "manifest must use LF line endings");
        require(text.endsWith("\n"), "manifest must end with exactly one LF");
        require(!text.endsWith("\n\n"), "manifest has a trailing blank row");
        String[] lines = text.split("\n", -1);
        require(lines.length >= 3 && lines[lines.length - 1].isEmpty(), "manifest row structure is invalid");
        requireEqual("manifest header", HEADER, lines[0]);

        List<Target> targets = new ArrayList<>();
        Set<String> entries = new HashSet<>();
        Address priorEntry = null;
        for (int lineNumber = 2; lineNumber < lines.length; lineNumber++) {
            String line = lines[lineNumber - 1];
            if (line.isEmpty()) {
                throw new IllegalArgumentException("manifest contains a blank row at line " + lineNumber);
            }
            String[] fields = line.split("\\t", -1);
            if (fields.length != 13) {
                throw new IllegalArgumentException(
                    "manifest line " + lineNumber + " has " + fields.length + " fields, expected 13");
            }
            Address entry = parseAddress(fields[0], "entry line " + lineNumber);
            require(entries.add(fields[0]), "duplicate manifest entry: " + fields[0]);
            if (priorEntry != null) {
                require(priorEntry.compareTo(entry) < 0, "manifest entries are not strictly sorted");
            }
            priorEntry = entry;
            AddressSet expectedBody = parseRanges(fields[1], fields[0]);
            require(expectedBody.getMinAddress().equals(entry), "function entry is not body minimum: " + fields[0]);
            long bodyBytes = positiveLong(fields[2], "expectedBodyBytes");
            require(bodyBytes == expectedBody.getNumAddresses(), "expectedBodyBytes disagrees with ranges at " + fields[0]);
            String rangeDigest = requireHash(fields[3], "expectedRangeDigest");
            String bodySha = requireHash(fields[4], "expectedBodyBytesSha256");
            long instructionCount = positiveLong(fields[5], "expectedInstructionCount");
            boolean expectedIsThunk = requireBoolean(fields[6], "expectedIsThunk");
            Address expectedThunkTarget = fields[7].isEmpty()
                ? null
                : parseAddress(fields[7], "expectedThunkTarget");
            require(expectedIsThunk == (expectedThunkTarget != null),
                "expectedThunkTarget must be present exactly when expectedIsThunk is true at "
                + fields[0]);
            require(expectedThunkTarget == null || !expectedThunkTarget.equals(entry),
                "thunk target cannot equal entry at " + fields[0]);
            List<Address> forbidden = parseAddressList(fields[8], "forbidden entry");
            for (Address address : forbidden) {
                require(!address.equals(entry), "entry cannot forbid itself: " + fields[0]);
            }
            require(!fields[9].isEmpty(), "residualEntityKeys is empty at " + fields[0]);
            require(!fields[10].isEmpty(), "questionIds is empty at " + fields[0]);
            require(!fields[11].isEmpty(), "contractIds is empty at " + fields[0]);
            require(fields[12].matches("[A-Z0-9_]+"), "promotionLane is not canonical at " + fields[0]);
            targets.add(new Target(
                fields[0], entry, fields[1], expectedBody, bodyBytes, rangeDigest, bodySha,
                instructionCount, expectedIsThunk, expectedThunkTarget, fields[7],
                forbidden, fields[8], fields[9], fields[10], fields[11], fields[12]));
        }
        require(targets.size() == expectedCount,
            "manifest count mismatch expected=" + expectedCount + " actual=" + targets.size());
        validateTargetSetConflicts(targets);
        return targets;
    }

    private void validateTargetSetConflicts(List<Target> targets) {
        Set<String> ownedAddresses = new HashSet<>();
        Set<String> entries = new HashSet<>();
        for (Target target : targets) {
            entries.add(target.entryText);
            AddressIterator addresses = target.expectedBody.getAddresses(true);
            while (addresses.hasNext()) {
                String address = canonical(addresses.next());
                require(ownedAddresses.add(address),
                    "expected function bodies overlap at " + address);
            }
        }
        for (Target target : targets) {
            for (Address forbidden : target.forbiddenEntries) {
                String address = canonical(forbidden);
                require(!entries.contains(address),
                    "forbidden entry is another manifest target: " + address);
                for (Target other : targets) {
                    if (other != target) {
                        require(!other.expectedBody.contains(forbidden),
                            "forbidden entry lies inside another expected body: " + address);
                    }
                }
            }
        }
    }

    private static String canonicalRanges(AddressSetView body) {
        StringBuilder ranges = new StringBuilder();
        for (AddressRange range : body) {
            if (ranges.length() > 0) {
                ranges.append(';');
            }
            ranges.append(canonical(range.getMinAddress()));
            ranges.append('-');
            ranges.append(canonical(range.getMaxAddress().add(1)));
        }
        return ranges.toString();
    }

    private static String bodyRangeDigest(AddressSetView body) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        for (AddressRange range : body) {
            digest.update(range.getMinAddress().toString().getBytes(StandardCharsets.UTF_8));
            digest.update((byte) ':');
            digest.update(range.getMaxAddress().toString().getBytes(StandardCharsets.UTF_8));
            digest.update((byte) ';');
        }
        return hex(digest.digest());
    }

    private String bodyBytesSha256(AddressSetView body) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        AddressIterator addresses = body.getAddresses(true);
        while (addresses.hasNext()) {
            digest.update(currentProgram.getMemory().getByte(addresses.next()));
        }
        return hex(digest.digest());
    }

    private long instructionCount(AddressSetView body) {
        long count = 0;
        InstructionIterator instructions = currentProgram.getListing().getInstructions(body, true);
        while (instructions.hasNext()) {
            instructions.next();
            count++;
        }
        return count;
    }

    private long validatedInstructionCount(AddressSetView body, String label) {
        AddressSet covered = new AddressSet();
        long count = 0;
        InstructionIterator instructions = currentProgram.getListing().getInstructions(body, true);
        while (instructions.hasNext()) {
            Instruction instruction = instructions.next();
            Address start = instruction.getMinAddress();
            Address end = instruction.getMaxAddress();
            require(body.contains(start, end),
                "INSTRUCTION_COVERAGE_MISMATCH: instruction crosses expected body at " + label
                + " instruction=" + canonical(start) + "-" + canonical(end.add(1)));
            covered.addRange(start, end);
            count++;
        }
        require(covered.hasSameAddresses(body),
            "INSTRUCTION_COVERAGE_MISMATCH at " + label
            + " body=" + canonicalRanges(body)
            + " covered=" + canonicalRanges(covered));
        return count;
    }

    private long programInstructionCount() {
        long count = 0;
        InstructionIterator instructions = currentProgram.getListing().getInstructions(true);
        while (instructions.hasNext()) {
            instructions.next();
            count++;
        }
        return count;
    }

    private Map<String, String> functionBodySnapshot() throws Exception {
        Map<String, String> snapshot = new LinkedHashMap<>();
        FunctionIterator functions = currentProgram.getFunctionManager().getFunctions(true);
        while (functions.hasNext()) {
            Function function = functions.next();
            AddressSetView body = function.getBody();
            String entry = canonical(function.getEntryPoint());
            String envelope = canonicalRanges(body)
                + "|" + body.getNumAddresses()
                + "|" + bodyRangeDigest(body)
                + "|" + instructionCount(body);
            require(snapshot.put(entry, envelope) == null,
                "duplicate function entry while snapshotting: " + entry);
        }
        return snapshot;
    }

    private void validateCreatedSetAndPreexistingBodies(
            Map<String, String> before,
            List<Target> targets) throws Exception {
        Map<String, String> after = functionBodySnapshot();
        Set<String> expectedCreated = new HashSet<>();
        for (Target target : targets) {
            expectedCreated.add(target.entryText);
        }
        Set<String> actualCreated = new HashSet<>(after.keySet());
        actualCreated.removeAll(before.keySet());
        require(actualCreated.equals(expectedCreated),
            "created function entry set differs from manifest targets");
        require(after.size() == before.size() + targets.size(),
            "function inventory count did not advance by target count");
        for (Map.Entry<String, String> row : before.entrySet()) {
            require(row.getValue().equals(after.get(row.getKey())),
                "PREEXISTING_FUNCTION_BODY_CHANGED entry=" + row.getKey());
        }
    }

    private Function exactFunction(Address entry) {
        Function function = getFunctionAt(entry);
        if (function != null && function.getEntryPoint().equals(entry)) {
            return function;
        }
        Function containing = getFunctionContaining(entry);
        if (containing != null && containing.getEntryPoint().equals(entry)) {
            return containing;
        }
        return null;
    }

    private void validateProgramIdentity() {
        require(currentProgram != null, "no current Ghidra program");
        requireEqual("program name", EXPECTED_PROGRAM_NAME, currentProgram.getName());
        String md5 = currentProgram.getExecutableMD5();
        String sha = currentProgram.getExecutableSHA256();
        requireEqual("imported executable md5", EXPECTED_PROGRAM_MD5,
            md5 == null ? "" : md5.toLowerCase(Locale.ROOT));
        requireEqual("imported executable sha256", EXPECTED_PROGRAM_SHA256,
            sha == null ? "" : sha.toLowerCase(Locale.ROOT));
        requireEqual("image base", EXPECTED_IMAGE_BASE,
            currentProgram.getImageBase().toString().toLowerCase(Locale.ROOT));
        requireEqual("language", EXPECTED_LANGUAGE, currentProgram.getLanguageID().toString());
        requireEqual("compiler spec", EXPECTED_COMPILER_SPEC,
            currentProgram.getCompilerSpec().getCompilerSpecID().toString());
        println("FUNCTION_ENVELOPE_PROGRAM_OK name=" + EXPECTED_PROGRAM_NAME
            + " sha256=" + EXPECTED_PROGRAM_SHA256 + " imageBase=0x" + EXPECTED_IMAGE_BASE);
    }

    private void validateManifestEnvelope(Target target) throws Exception {
        for (AddressRange range : target.expectedBody) {
            MemoryBlock startBlock = currentProgram.getMemory().getBlock(range.getMinAddress());
            MemoryBlock endBlock = currentProgram.getMemory().getBlock(range.getMaxAddress());
            require(startBlock != null && startBlock == endBlock,
                "expected range crosses memory blocks at " + target.entryText);
            require(EXPECTED_BLOCK.equals(startBlock.getName())
                    && startBlock.isExecute() && startBlock.isInitialized(),
                "expected body is not initialized executable .text at " + target.entryText);
        }
        requireEqual("expectedRangeDigest at " + target.entryText,
            target.expectedRangeDigest, bodyRangeDigest(target.expectedBody));
        requireEqual("expectedBodyBytesSha256 at " + target.entryText,
            target.expectedBodyBytesSha256, bodyBytesSha256(target.expectedBody));
        require(target.expectedInstructionCount == instructionCount(target.expectedBody),
            "expectedInstructionCount disagrees with listing at " + target.entryText);
        require(target.expectedInstructionCount == validatedInstructionCount(
                target.expectedBody, target.entryText),
            "expectedInstructionCount disagrees with exact instruction coverage at "
            + target.entryText);
        require(currentProgram.getListing().getInstructionAt(target.entry) != null,
            "target has no defined instruction; envelope promotion never disassembles: " + target.entryText);
    }

    private void validateInitialState(Target target, String mode) {
        Function exact = exactFunction(target.entry);
        if (mode.equals("readback")) {
            require(exact != null, "readback target has no exact function: " + target.entryText);
            return;
        }
        require(exact == null, "probe/apply requires a missing target: " + target.entryText);
        Symbol primary = currentProgram.getSymbolTable().getPrimarySymbol(target.entry);
        require(primary == null || primary.getSource() == SourceType.DEFAULT,
            "target has a non-default primary symbol that function creation could consume: "
            + target.entryText + " symbol=" + (primary == null ? "" : clean(primary.getName()))
            + " source=" + (primary == null ? "" : primary.getSource().toString()));
        AddressIterator addresses = target.expectedBody.getAddresses(true);
        while (addresses.hasNext()) {
            Address address = addresses.next();
            Function containing = getFunctionContaining(address);
            if (containing != null) {
                throw new IllegalStateException(
                    "expected body intersects existing function at " + canonical(address)
                    + " containing=" + canonical(containing.getEntryPoint()));
            }
        }
        for (Address forbidden : target.forbiddenEntries) {
            require(getFunctionAt(forbidden) == null,
                "forbidden entry already exists before mutation: " + canonical(forbidden));
        }
    }

    private Observation observe(Target target, Function function, String status, String note) throws Exception {
        require(function != null && function.getEntryPoint().equals(target.entry),
            "exact function is absent at " + target.entryText);
        AddressSetView body = function.getBody();
        String ranges = canonicalRanges(body);
        long bytes = body.getNumAddresses();
        String rangeDigest = bodyRangeDigest(body);
        String bodySha = bodyBytesSha256(body);
        long instructions = validatedInstructionCount(body, target.entryText);
        boolean isThunk = function.isThunk();
        Function thunked = isThunk ? function.getThunkedFunction(false) : null;
        String thunkTarget = thunked == null ? "" : canonical(thunked.getEntryPoint());
        require(isThunk == target.expectedIsThunk,
            "THUNK_KIND_MISMATCH entry=" + target.entryText
            + " expected=" + target.expectedIsThunk + " actual=" + isThunk
            + " actualTarget=" + thunkTarget);
        require(!isThunk || (thunked != null
                && thunked.getEntryPoint().equals(target.expectedThunkTarget)),
            "THUNK_TARGET_MISMATCH entry=" + target.entryText
            + " expected=" + target.expectedThunkTargetText
            + " actual=" + thunkTarget);
        if (!ranges.equals(target.expectedRanges)
                || bytes != target.expectedBodyBytes
                || !rangeDigest.equals(target.expectedRangeDigest)
                || !bodySha.equals(target.expectedBodyBytesSha256)
                || instructions != target.expectedInstructionCount) {
            throw new IllegalStateException(
                "BODY_ENVELOPE_MISMATCH entry=" + target.entryText
                + " expectedRanges=" + target.expectedRanges
                + " actualRanges=" + ranges
                + " expectedBytes=" + target.expectedBodyBytes
                + " actualBytes=" + bytes
                + " expectedRangeDigest=" + target.expectedRangeDigest
                + " actualRangeDigest=" + rangeDigest
                + " expectedBodySha256=" + target.expectedBodyBytesSha256
                + " actualBodySha256=" + bodySha
                + " expectedInstructions=" + target.expectedInstructionCount
                + " actualInstructions=" + instructions);
        }
        for (Address forbidden : target.forbiddenEntries) {
            require(getFunctionAt(forbidden) == null,
                "forbidden separate function exists: " + canonical(forbidden));
            if (target.expectedBody.contains(forbidden)) {
                Function containing = getFunctionContaining(forbidden);
                require(containing != null && containing.getEntryPoint().equals(target.entry),
                    "expected tail is not contained by " + target.entryText + ": " + canonical(forbidden));
            }
        }
        return new Observation(
            target, status, clean(function.getName()),
            function.getSymbol() == null ? "" : function.getSymbol().getSource().toString(),
            ranges, bytes, rangeDigest, bodySha, instructions, isThunk, thunkTarget, note);
    }

    private byte[] buildTsv(List<Observation> rows) {
        StringBuilder out = new StringBuilder();
        out.append("entry\tstatus\tname\tnameSource\texpectedRanges\tactualRanges"
            + "\texpectedBodyBytes\tactualBodyBytes\texpectedRangeDigest\tactualRangeDigest"
            + "\texpectedBodyBytesSha256\tactualBodyBytesSha256"
            + "\texpectedInstructionCount\tactualInstructionCount\texpectedIsThunk"
            + "\tactualIsThunk\texpectedThunkTarget\tactualThunkTarget\tforbiddenEntries"
            + "\tresidualEntityKeys\tquestionIds\tcontractIds\tpromotionLane\tnote\n");
        for (Observation row : rows) {
            Target target = row.target;
            out.append(target.entryText).append('\t').append(row.status).append('\t');
            out.append(row.name).append('\t').append(row.nameSource).append('\t');
            out.append(target.expectedRanges).append('\t').append(row.actualRanges).append('\t');
            out.append(target.expectedBodyBytes).append('\t').append(row.actualBodyBytes).append('\t');
            out.append(target.expectedRangeDigest).append('\t').append(row.actualRangeDigest).append('\t');
            out.append(target.expectedBodyBytesSha256).append('\t').append(row.actualBodyBytesSha256).append('\t');
            out.append(target.expectedInstructionCount).append('\t').append(row.actualInstructionCount).append('\t');
            out.append(target.expectedIsThunk).append('\t').append(row.actualIsThunk).append('\t');
            out.append(target.expectedThunkTargetText).append('\t').append(row.actualThunkTarget).append('\t');
            out.append(target.forbiddenText).append('\t').append(target.residualEntityKeys).append('\t');
            out.append(target.questionIds).append('\t').append(target.contractIds).append('\t');
            out.append(target.promotionLane).append('\t').append(clean(row.note)).append('\n');
        }
        return out.toString().getBytes(StandardCharsets.UTF_8);
    }

    private byte[] buildReady(
            String mode,
            String toolPath,
            byte[] toolBytes,
            File manifest,
            byte[] manifestBytes,
            int expectedCount,
            File output,
            byte[] outputBytes,
            long functionsBefore,
            long functionsTransient,
            long functionsAfter,
            long instructionsBefore,
            long instructionsAfter,
            boolean commitRequested,
            boolean rollbackRequested,
            boolean transactionEndReturnedCommitted) throws Exception {
        StringBuilder ready = new StringBuilder();
        ready.append("{\n");
        ready.append("  \"schemaVersion\": \"").append(SCHEMA).append("\",\n");
        ready.append("  \"completedAtUtc\": \"").append(json(Instant.now().toString())).append("\",\n");
        ready.append("  \"mode\": \"").append(mode).append("\",\n");
        ready.append("  \"tool\": {\"path\": \"").append(json(toolPath))
            .append("\", \"bytes\": ").append(toolBytes.length)
            .append(", \"sha256\": \"").append(sha256(toolBytes)).append("\"},\n");
        ready.append("  \"program\": {\"name\": \"").append(EXPECTED_PROGRAM_NAME)
            .append("\", \"executableMd5\": \"").append(EXPECTED_PROGRAM_MD5)
            .append("\", \"executableSha256\": \"").append(EXPECTED_PROGRAM_SHA256)
            .append("\", \"imageBase\": \"0x").append(EXPECTED_IMAGE_BASE)
            .append("\", \"language\": \"").append(EXPECTED_LANGUAGE)
            .append("\", \"compilerSpec\": \"").append(EXPECTED_COMPILER_SPEC).append("\"},\n");
        ready.append("  \"manifest\": {\"path\": \"").append(json(manifest.getCanonicalPath()))
            .append("\", \"bytes\": ").append(manifestBytes.length)
            .append(", \"sha256\": \"").append(sha256(manifestBytes))
            .append("\", \"expectedCount\": ").append(expectedCount).append("},\n");
        ready.append("  \"output\": {\"path\": \"").append(json(output.getCanonicalPath()))
            .append("\", \"bytes\": ").append(outputBytes.length)
            .append(", \"sha256\": \"").append(sha256(outputBytes)).append("\"},\n");
        ready.append("  \"counts\": {\"targets\": ").append(expectedCount)
            .append(", \"functionsBefore\": ").append(functionsBefore)
            .append(", \"functionsTransient\": ").append(functionsTransient)
            .append(", \"functionManagerViewAfterNestedTransaction\": ").append(functionsAfter)
            .append(", \"instructionsBefore\": ").append(instructionsBefore)
            .append(", \"instructionsAfter\": ").append(instructionsAfter).append("},\n");
        ready.append("  \"namesAuthorized\": false,\n");
        ready.append("  \"functionKindsBoundByManifest\": true,\n");
        ready.append("  \"loadedOrTransientEnvelopesVerified\": true,\n");
        ready.append("  \"commitRequested\": ").append(commitRequested).append(",\n");
        ready.append("  \"rollbackRequested\": ").append(rollbackRequested).append(",\n");
        ready.append("  \"transactionEndReturnedCommitted\": ")
            .append(transactionEndReturnedCommitted).append(",\n");
        ready.append("  \"loadedStateVerified\": ").append(mode.equals("readback")).append(",\n");
        ready.append("  \"reopenVerificationRequired\": ")
            .append(!mode.equals("readback")).append("\n");
        ready.append("}\n");
        return ready.toString().getBytes(StandardCharsets.UTF_8);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length != 6) {
            throw new IllegalArgumentException(
                "usage: <manifest.tsv> <expected_sha256> <expected_count> "
                + "<out.tsv> <out.ready.json> <probe|apply|readback>");
        }
        File manifest = new File(args[0]).getCanonicalFile();
        require(manifest.isFile(), "manifest is not a file: " + manifest);
        String expectedSha = requireHash(args[1], "expected_sha256");
        int expectedCount;
        try {
            expectedCount = Integer.parseInt(args[2]);
        } catch (NumberFormatException ex) {
            throw new IllegalArgumentException("expected_count must be a positive integer", ex);
        }
        require(expectedCount > 0, "expected_count must be positive");
        File output = requireNewOutput(args[3], "output TSV");
        File readyFile = requireNewOutput(args[4], "READY receipt");
        require(!output.equals(readyFile), "output TSV and READY receipt must differ");
        preflightAtomicWrite(output, "output TSV");
        preflightAtomicWrite(readyFile, "READY receipt");
        String mode = requireMode(args[5]);

        byte[] toolBytes = readToolSource();
        String toolPath = getSourceFile().getCanonicalPath();
        println("FUNCTION_ENVELOPE_TOOL_OK path=" + toolPath
            + " bytes=" + toolBytes.length + " sha256=" + sha256(toolBytes));
        byte[] manifestBytes = Files.readAllBytes(manifest.toPath());
        requireEqual("manifest sha256", expectedSha, sha256(manifestBytes));
        validateProgramIdentity();
        List<Target> targets = loadTargets(manifestBytes, expectedCount);
        for (Target target : targets) {
            monitor.checkCancelled();
            validateManifestEnvelope(target);
            validateInitialState(target, mode);
        }
        println("FUNCTION_ENVELOPE_PREFLIGHT_OK mode=" + mode + " targets=" + targets.size()
            + " manifestSha256=" + expectedSha);

        Map<String, String> preexistingBodies = functionBodySnapshot();
        long functionsBefore = preexistingBodies.size();
        long functionsTransient = functionsBefore;
        long functionsAfter = functionsBefore;
        long instructionsBefore = programInstructionCount();
        long instructionsAfter = instructionsBefore;
        boolean applyMode = mode.equals("apply");
        boolean commitRequested = false;
        boolean rollbackRequested = mode.equals("probe");
        boolean transactionEndReturnedCommitted = false;
        List<Observation> rows = new ArrayList<>();
        File stagedOutput = null;
        File stagedReady = null;
        int mutationTransactionId = -1;
        boolean explicitMutationEndCompleted = false;

        try {
            if (mode.equals("readback")) {
                for (Target target : targets) {
                    rows.add(observe(
                        target, exactFunction(target.entry), "verified", "exact envelope readback"));
                }
            } else {
                mutationTransactionId = currentProgram.startTransaction(
                    (mode.equals("probe") ? "Probe " : "Apply ")
                    + targets.size() + " exact function body envelopes");
                try {
                    for (Target target : targets) {
                        monitor.checkCancelled();
                        Function function = createFunction(target.entry, null);
                        require(function != null && function.getEntryPoint().equals(target.entry),
                            "function creation failed: " + target.entryText);
                    }
                    validateCreatedSetAndPreexistingBodies(preexistingBodies, targets);
                    for (Target target : targets) {
                        rows.add(observe(
                            target, exactFunction(target.entry),
                            mode.equals("probe")
                                ? "probed_rollback_requested"
                                : "created_commit_requested",
                            "natural Ghidra body inference matched; outer GhidraScript finalization is pending"));
                    }
                    functionsTransient = functionBodySnapshot().size();
                    require(functionsTransient - functionsBefore == targets.size(),
                        "transient function count did not advance by target count");
                    require(programInstructionCount() == instructionsBefore,
                        "function creation changed program instruction count");
                    if (applyMode) {
                        functionsAfter = functionsTransient;
                        instructionsAfter = instructionsBefore;
                        byte[] outputBytes = buildTsv(rows);
                        byte[] readyBytes = buildReady(
                            mode, toolPath, toolBytes, manifest, manifestBytes, expectedCount,
                            output, outputBytes, functionsBefore, functionsTransient,
                            functionsAfter, instructionsBefore, instructionsAfter,
                            true, false, false);
                        stagedOutput = stageAtomic(output, outputBytes);
                        stagedReady = stageAtomic(readyFile, readyBytes);
                        commitRequested = true;
                    }
                } finally {
                    try {
                        transactionEndReturnedCommitted = currentProgram.endTransaction(
                            mutationTransactionId, commitRequested);
                        explicitMutationEndCompleted = true;
                    } finally {
                        if (!commitRequested) {
                            discardStaged(stagedOutput);
                            discardStaged(stagedReady);
                            stagedOutput = null;
                            stagedReady = null;
                        }
                    }
                }
                require(!transactionEndReturnedCommitted,
                    "explicit transaction unexpectedly finalized outside GhidraScript's outer transaction");
            }

            functionsAfter = functionBodySnapshot().size();
            instructionsAfter = programInstructionCount();
            long expectedViewAfter = mode.equals("readback")
                ? functionsBefore
                : functionsBefore + targets.size();
            require(functionsAfter == expectedViewAfter,
                "post-nested-transaction FunctionManager view mismatch expected="
                + expectedViewAfter + " actual=" + functionsAfter);
            require(instructionsAfter == instructionsBefore,
                "final instruction count changed before=" + instructionsBefore
                + " after=" + instructionsAfter);

            if (stagedOutput == null && stagedReady == null) {
                byte[] outputBytes = buildTsv(rows);
                byte[] readyBytes = buildReady(
                    mode, toolPath, toolBytes, manifest, manifestBytes, expectedCount,
                    output, outputBytes, functionsBefore, functionsTransient,
                    functionsAfter, instructionsBefore, instructionsAfter,
                    commitRequested, rollbackRequested, transactionEndReturnedCommitted);
                stagedOutput = stageAtomic(output, outputBytes);
                stagedReady = stageAtomic(readyFile, readyBytes);
            }

            publishStaged(stagedOutput, output);
            stagedOutput = null;
            publishStaged(stagedReady, readyFile);
            stagedReady = null;
        } catch (Exception ex) {
            if (mutationTransactionId >= 0) {
                boolean outerRollbackRequestedDueToReceiptFailure = false;
                if (!explicitMutationEndCompleted && mutationTransactionId >= 0) {
                    try {
                        boolean retryReturnedCommitted = currentProgram.endTransaction(
                            mutationTransactionId, false);
                        require(!retryReturnedCommitted,
                            "failed-end rollback unexpectedly finalized outer transaction");
                        outerRollbackRequestedDueToReceiptFailure = true;
                    } catch (Exception retryEx) {
                        ex.addSuppressed(retryEx);
                    }
                }
                try {
                    int abortTransaction = currentProgram.startTransaction(
                        "Abort function envelope apply after finalization or receipt failure");
                    boolean abortReturnedCommitted = currentProgram.endTransaction(
                        abortTransaction, false);
                    require(!abortReturnedCommitted,
                        "receipt-failure abort transaction unexpectedly finalized outer transaction");
                    outerRollbackRequestedDueToReceiptFailure = true;
                } catch (Exception abortEx) {
                    ex.addSuppressed(abortEx);
                }
                println("FUNCTION_ENVELOPE_MUTATION_TAINTED mode=" + mode
                    + " targets=" + targets.size()
                    + " commit_requested=" + commitRequested
                    + " outer_rollback_requested_due_to_receipt_failure="
                    + outerRollbackRequestedDueToReceiptFailure
                    + " clone_tainted=true recovery=RESTORE_VERIFIED_SCRATCH_BASE error="
                    + clean(ex.toString()));
            }
            throw ex;
        } finally {
            discardStaged(stagedOutput);
            discardStaged(stagedReady);
        }

        println("FUNCTION_ENVELOPE_OK mode=" + mode + " targets=" + targets.size()
            + " functions_before=" + functionsBefore
            + " functions_transient=" + functionsTransient
            + " functions_after=" + functionsAfter
            + " commit_requested=" + commitRequested
            + " rollback_requested=" + rollbackRequested
            + " transaction_end_returned_committed=" + transactionEndReturnedCommitted
            + " loaded_state_verified=" + mode.equals("readback"));
    }
}
