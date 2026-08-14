//@category Symbol
//
// Admit only the 23 corrected CRT/runtime P0 boundaries from the frozen CRT22
// run-c cohort to an exact current 8,304-function/db.18615 disposable copy.
// Disassembly is rebuilt only inside the 24 preregistered body ranges.  No name,
// signature, comment, tag, data, byte, or explicit-reference mutation is
// authorized.  The dormant 0x005B8500 canary and the separate 0x005D0A9F body
// repair are outside this campaign.
//
// Usage:
//   -postScript GhidraApplyCrtP0BoundariesV4.java
//       <repository-root> <out.tsv> <out.ready.json>
//       <dry|probe-after-one|probe-post-inner|apply|readback>

import ghidra.app.script.GhidraScript;
import ghidra.app.util.PseudoDisassembler;
import ghidra.app.util.PseudoInstruction;
import ghidra.program.disassemble.Disassembler;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressIterator;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Listing;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;
import ghidra.program.model.symbol.Reference;
import ghidra.program.model.symbol.ReferenceIterator;

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
import java.util.Arrays;
import java.util.Collections;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

public class GhidraApplyCrtP0BoundariesV4 extends GhidraScript {

    private static final String SCHEMA =
        "bea.ghidra.crt-p0-boundaries.v4";
    private static final String PROGRAM_NAME = "BEA.exe";
    private static final String PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55";
    private static final String PROGRAM_SHA256 =
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
    private static final String IMAGE_BASE = "00400000";
    private static final String LANGUAGE = "x86:LE:32:default";
    private static final String COMPILER_SPEC = "windows";
    private static final String TEXT_BLOCK = ".text";
    private static final long PRE_FUNCTIONS = 8304;
    private static final long POST_FUNCTIONS = 8327;
    private static final long PRE_INSTRUCTIONS = 551055;
    private static final long POST_INSTRUCTIONS = 551133;
    private static final long PRE_REFERENCES = 234467;
    private static final long POST_REFERENCES = 234478;
    private static final boolean POST_COUNTS_PINNED = true;
    private static final long EXTERNAL_INSTRUCTIONS = 312;
    private static final long GHIDRA_BODY_INSTRUCTIONS = 312;
    private static final int TARGET_COUNT = 23;
    private static final long BODY_BYTES = 1131;
    private static final long BODY_RANGES = 24;
    private static final long PRE_RANGES = 8434;
    private static final long POST_RANGES = 8458;
    private static final String MANIFEST_RELATIVE =
        "reverse-engineering/binary-analysis/" +
        "crt-runtime-p0-function-boundaries-2026-08-14.tsv";
    private static final long MANIFEST_BYTES = 6176;
    private static final String MANIFEST_SHA256 =
        "c60359ecfd58e7c97c45a45e1b83d034e6cc104c222781f6f611e158b459d7df";
    private static final String RUN_C_COHORT_SHA256 =
        "bc16df601740afec41bdba306d7e02996171da1cc10d3491da38d6d022bdbf5a";
    private static final String MANIFEST_HEADER =
        "entry\texpectedRanges\texpectedBodyBytes\texpectedRangeDigest" +
        "\texpectedBodyBytesSha256\texpectedInstructionCount\texpectedIsThunk" +
        "\texpectedThunkTarget\tforbiddenEntries\tresidualEntityKeys" +
        "\tquestionIds\tcontractIds\tpromotionLane";
    private static class Target {
        final String id;
        final String cohort;
        final String entryText;
        final Address entry;
        final String rangesText;
        final AddressSet body;
        final long bodyBytes;
        final long externalInstructionCount;
        final String bodyBytesSha256;
        final boolean expectedThunk;
        final String expectedThunkTarget;
        final String forbiddenEntries;
        final String residualEntityKey;
        final String contractId;
        final String promotionLane;

        Target(String id, String cohort, String entryText, Address entry,
                String rangesText, AddressSet body, long bodyBytes,
                long externalInstructionCount, String bodyBytesSha256,
                boolean expectedThunk, String expectedThunkTarget,
                String forbiddenEntries, String residualEntityKey,
                String contractId, String promotionLane) {
            this.id = id;
            this.cohort = cohort;
            this.entryText = entryText;
            this.entry = entry;
            this.rangesText = rangesText;
            this.body = body;
            this.bodyBytes = bodyBytes;
            this.externalInstructionCount = externalInstructionCount;
            this.bodyBytesSha256 = bodyBytesSha256;
            this.expectedThunk = expectedThunk;
            this.expectedThunkTarget = expectedThunkTarget;
            this.forbiddenEntries = forbiddenEntries;
            this.residualEntityKey = residualEntityKey;
            this.contractId = contractId;
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
        final String actualBodyBytesSha256;
        final long actualGhidraInstructionCount;
        final String actualIsThunk;
        final String actualThunkTarget;

        Observation(Target target, String status, String name, String nameSource,
                String actualRanges, long actualBodyBytes,
                String actualBodyBytesSha256, long actualGhidraInstructionCount,
                String actualIsThunk, String actualThunkTarget) {
            this.target = target;
            this.status = status;
            this.name = name;
            this.nameSource = nameSource;
            this.actualRanges = actualRanges;
            this.actualBodyBytes = actualBodyBytes;
            this.actualBodyBytesSha256 = actualBodyBytesSha256;
            this.actualGhidraInstructionCount = actualGhidraInstructionCount;
            this.actualIsThunk = actualIsThunk;
            this.actualThunkTarget = actualThunkTarget;
        }
    }

    private static class IntentionalProbeException extends RuntimeException {
        IntentionalProbeException(String message) {
            super(message);
        }
    }

    private static void require(boolean value, String message) {
        if (!value) {
            throw new IllegalStateException(message);
        }
    }

    private static void equal(String label, Object expected, Object actual) {
        if (expected == null ? actual != null : !expected.equals(actual)) {
            throw new IllegalStateException(
                label + " mismatch expected=" + expected + " actual=" + actual);
        }
    }

    private static String hex(byte[] bytes) {
        StringBuilder result = new StringBuilder(bytes.length * 2);
        for (byte value : bytes) {
            result.append(String.format(Locale.ROOT, "%02x", value & 0xff));
        }
        return result.toString();
    }

    private static String sha256(byte[] bytes) throws Exception {
        return hex(MessageDigest.getInstance("SHA-256").digest(bytes));
    }

    private static String clean(String value) {
        if (value == null) {
            return "";
        }
        return value.replace("\\", "\\\\").replace("\r", "\\r")
            .replace("\n", "\\n").replace("\t", " ");
    }

    private static String json(String value) {
        return clean(value).replace("\"", "\\\"");
    }

    private static String canonical(Address address) {
        return "0x" + address.toString().toLowerCase(Locale.ROOT);
    }

    private static long nonnegativeLong(String value, String label) {
        try {
            long result = Long.parseLong(value);
            require(result >= 0, label + " must be nonnegative");
            return result;
        } catch (NumberFormatException ex) {
            throw new IllegalArgumentException(label + " must be decimal", ex);
        }
    }

    private static long positiveLong(String value, String label) {
        long result = nonnegativeLong(value, label);
        require(result > 0, label + " must be positive");
        return result;
    }

    private static String requireHash(String value, String label) {
        require(value != null && value.matches("[0-9a-f]{64}"),
            label + " must be lowercase SHA-256");
        return value;
    }

    private Address parseAddress(String value, String label) {
        require(value != null && value.matches("0x[0-9a-fA-F]{8}"),
            label + " must be one 32-bit address");
        Address address = toAddr(value);
        require(address != null, label + " does not resolve");
        return address;
    }

    private AddressSet parseRanges(String value, String id) {
        require(value != null && !value.isEmpty(), "empty body ranges at " + id);
        AddressSet body = new AddressSet();
        Address priorEnd = null;
        for (String piece : value.split(";", -1)) {
            require(piece.matches("0x[0-9a-fA-F]{8}-0x[0-9a-fA-F]{8}"),
                "malformed range at " + id + ": " + piece);
            String[] bounds = piece.split("-", -1);
            Address start = parseAddress(bounds[0], "range start");
            Address endExclusive = parseAddress(bounds[1], "range end");
            require(start.compareTo(endExclusive) < 0, "empty range at " + id);
            if (priorEnd != null) {
                require(priorEnd.compareTo(start) < 0,
                    "body ranges overlap or touch at " + id);
            }
            body.addRange(start, endExclusive.subtract(1));
            priorEnd = endExclusive;
        }
        return body;
    }

    private static String canonicalRanges(AddressSetView body) {
        StringBuilder result = new StringBuilder();
        for (AddressRange range : body) {
            if (result.length() > 0) {
                result.append(';');
            }
            result.append(canonical(range.getMinAddress())).append('-')
                .append(canonical(range.getMaxAddress().add(1)));
        }
        return result.toString();
    }

    private static String bodyRangeSha256(AddressSetView body) throws Exception {
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

    private String memoryBytesSha256(Address start, int length) throws Exception {
        byte[] bytes = new byte[length];
        int read = currentProgram.getMemory().getBytes(start, bytes);
        equal("memory byte count at " + canonical(start), length, read);
        return sha256(bytes);
    }

    private long instructionCount(AddressSetView body) {
        long count = 0;
        InstructionIterator instructions =
            currentProgram.getListing().getInstructions(body, true);
        while (instructions.hasNext()) {
            instructions.next();
            count++;
        }
        return count;
    }

    private AddressSet instructionCoverage(AddressSetView body) {
        AddressSet covered = new AddressSet();
        InstructionIterator instructions =
            currentProgram.getListing().getInstructions(body, true);
        while (instructions.hasNext()) {
            Instruction instruction = instructions.next();
            require(body.contains(instruction.getMinAddress(), instruction.getMaxAddress()),
                "instruction crosses an admitted body boundary at "
                + canonical(instruction.getMinAddress()));
            covered.addRange(instruction.getMinAddress(), instruction.getMaxAddress());
        }
        return covered;
    }

    private Map<String, String> instructionSnapshot() throws Exception {
        Map<String, String> rows = new LinkedHashMap<>();
        InstructionIterator instructions =
            currentProgram.getListing().getInstructions(true);
        while (instructions.hasNext()) {
            Instruction instruction = instructions.next();
            String address = canonical(instruction.getAddress());
            String value = instruction.getLength() + "|"
                + hex(instruction.getBytes()) + "|"
                + clean(instruction.getMnemonicString()) + "|"
                + instruction.getFlowType() + "|"
                + String.valueOf(instruction.getFallThrough()) + "|"
                + Arrays.toString(instruction.getFlows()) + "|"
                + instruction.getFlowOverride() + "|"
                + instruction.isLengthOverridden();
            require(rows.put(address, value) == null,
                "duplicate instruction in snapshot: " + address);
        }
        return rows;
    }

    private Set<String> referenceSnapshot() {
        Set<String> rows = new HashSet<>();
        ReferenceIterator references = currentProgram.getReferenceManager()
            .getReferenceIterator(currentProgram.getMinAddress());
        while (references.hasNext()) {
            Reference reference = references.next();
            String row = canonical(reference.getFromAddress()) + "|"
                + canonical(reference.getToAddress()) + "|"
                + reference.getOperandIndex() + "|"
                + reference.getReferenceType() + "|"
                + reference.getSource() + "|"
                + reference.isPrimary() + "|"
                + reference.getSymbolID() + "|"
                + reference.isMnemonicReference() + "|"
                + reference.isOperandReference() + "|"
                + reference.isStackReference() + "|"
                + reference.isExternalReference() + "|"
                + reference.isEntryPointReference() + "|"
                + reference.isMemoryReference() + "|"
                + reference.isRegisterReference();
            require(rows.add(row), "duplicate reference snapshot row: " + row);
        }
        return rows;
    }

    private long referenceCount() {
        long count = 0;
        ReferenceIterator references = currentProgram.getReferenceManager()
            .getReferenceIterator(currentProgram.getMinAddress());
        while (references.hasNext()) {
            references.next();
            count++;
        }
        return count;
    }

    private long programInstructionCount() {
        long count = 0;
        InstructionIterator instructions =
            currentProgram.getListing().getInstructions(true);
        while (instructions.hasNext()) {
            instructions.next();
            count++;
        }
        return count;
    }

    private long internalFunctionCount() {
        long count = 0;
        FunctionIterator functions =
            currentProgram.getFunctionManager().getFunctions(true);
        while (functions.hasNext()) {
            functions.next();
            count++;
        }
        return count;
    }

    private long internalFunctionRangeCount() {
        long count = 0;
        FunctionIterator functions =
            currentProgram.getFunctionManager().getFunctions(true);
        while (functions.hasNext()) {
            count += functions.next().getBody().getNumAddressRanges();
        }
        return count;
    }

    private Map<String, String> functionSnapshot() throws Exception {
        Map<String, String> rows = new LinkedHashMap<>();
        FunctionIterator functions =
            currentProgram.getFunctionManager().getFunctions(true);
        while (functions.hasNext()) {
            Function function = functions.next();
            AddressSetView body = function.getBody();
            Symbol symbol = function.getSymbol();
            String entry = canonical(function.getEntryPoint());
            String value = clean(function.getName()) + "|"
                + (symbol == null ? "" : symbol.getSource().toString()) + "|"
                + canonicalRanges(body) + "|" + body.getNumAddresses() + "|"
                + bodyRangeSha256(body) + "|" + instructionCount(body) + "|"
                + function.isThunk() + "|" + function.hasNoReturn() + "|"
                + clean(function.getSignature().getPrototypeString());
            require(rows.put(entry, value) == null,
                "duplicate function entry in snapshot: " + entry);
        }
        return rows;
    }

    private void validateProgramIdentity() {
        require(currentProgram != null, "no current program");
        equal("program name", PROGRAM_NAME, currentProgram.getName());
        equal("executable md5", PROGRAM_MD5,
            currentProgram.getExecutableMD5().toLowerCase(Locale.ROOT));
        equal("executable sha256", PROGRAM_SHA256,
            currentProgram.getExecutableSHA256().toLowerCase(Locale.ROOT));
        equal("image base", IMAGE_BASE,
            currentProgram.getImageBase().toString().toLowerCase(Locale.ROOT));
        equal("language", LANGUAGE, currentProgram.getLanguageID().toString());
        equal("compiler spec", COMPILER_SPEC,
            currentProgram.getCompilerSpec().getCompilerSpecID().toString());
    }

    private List<Target> loadTargets(File manifest) throws Exception {
        byte[] bytes = Files.readAllBytes(manifest.toPath());
        equal("manifest bytes", MANIFEST_BYTES, (long) bytes.length);
        equal("manifest sha256", MANIFEST_SHA256, sha256(bytes));
        require(bytes.length > 0 && bytes[0] != (byte) 0xef,
            "manifest must be UTF-8 without BOM");
        String text = new String(bytes, StandardCharsets.UTF_8);
        require(text.indexOf('\r') < 0 && text.endsWith("\n")
                && !text.endsWith("\n\n"),
            "manifest line endings are not canonical");
        String[] lines = text.split("\n", -1);
        equal("manifest header", MANIFEST_HEADER, lines[0]);
        require(lines.length == TARGET_COUNT + 2,
            "manifest row count mismatch");

        List<Target> targets = new ArrayList<>();
        Set<String> entries = new HashSet<>();
        Set<String> forbidden = new HashSet<>();
        Address priorEntry = null;
        AddressSet allBodies = new AddressSet();
        long totalBodyBytes = 0;
        long totalInstructions = 0;
        long totalRanges = 0;
        int thunkCount = 0;
        for (int index = 1; index <= TARGET_COUNT; index++) {
            String[] fields = lines[index].split("\\t", -1);
            require(fields.length == 13,
                "manifest field count mismatch at row " + index);
            String expectedId = String.format(Locale.ROOT, "CRT-P0-%03d", index);
            Address entry = parseAddress(fields[0], "entry");
            String entryText = canonical(entry);
            equal("canonical entry at " + expectedId, entryText, fields[0]);
            require(entries.add(entryText), "duplicate target entry: " + entryText);
            if (priorEntry != null) {
                require(priorEntry.compareTo(entry) < 0,
                    "target entries are not strictly sorted");
            }
            priorEntry = entry;
            AddressSet body = parseRanges(fields[1], expectedId);
            equal("canonical ranges at " + expectedId,
                canonicalRanges(body), fields[1]);
            require(body.getMinAddress().equals(entry),
                "entry is not body minimum at " + expectedId);
            long bodyBytes = positiveLong(fields[2], "body bytes");
            equal("body byte count at " + expectedId,
                bodyBytes, body.getNumAddresses());
            String rangeDigest = requireHash(fields[3], "range digest");
            equal("range digest at " + expectedId,
                rangeDigest, bodyRangeSha256(body));
            String bodySha = requireHash(fields[4], "body sha256");
            long externalInstructions =
                positiveLong(fields[5], "instruction count");
            require(fields[6].equals("true") || fields[6].equals("false"),
                "thunk flag is not boolean at " + expectedId);
            boolean expectedThunk = fields[6].equals("true");
            String expectedThunkTarget = fields[7];
            if (expectedThunk) {
                thunkCount++;
                equal("sole thunk entry", "0x0045ac20", entryText);
                equal("sole thunk target", "0x0045ac30", expectedThunkTarget);
            } else {
                equal("unexpected thunk target at " + expectedId,
                    "", expectedThunkTarget);
            }
            if (!fields[8].isEmpty()) {
                for (String item : fields[8].split(";", -1)) {
                    Address protectedEntry = parseAddress(item, "forbidden entry");
                    require(forbidden.add(canonical(protectedEntry)),
                        "duplicate forbidden entry");
                }
            }
            require(fields[9].equals("CRT22_P0_" +
                    entryText.substring(2).toUpperCase(Locale.ROOT)),
                "residual key drift at " + expectedId);
            require(fields[10].equals("Q_CRT23_BOUNDARY_" +
                    entryText.substring(2).toUpperCase(Locale.ROOT)),
                "question id drift at " + expectedId);
            equal("contract at " + expectedId, "BOUNDARY_ONLY", fields[11]);
            equal("promotion lane at " + expectedId,
                "CRT22_P0_SCRATCH_ONLY", fields[12]);
            require(!allBodies.intersects(body),
                "candidate bodies overlap at " + expectedId);
            allBodies.add(body);
            totalBodyBytes += bodyBytes;
            totalInstructions += externalInstructions;
            totalRanges += body.getNumAddressRanges();
            targets.add(new Target(expectedId, "CRT22_P0", entryText, entry,
                canonicalRanges(body), body, bodyBytes, externalInstructions,
                bodySha, expectedThunk, expectedThunkTarget, fields[8],
                fields[9], fields[11], fields[12]));
        }
        equal("body byte total", BODY_BYTES, totalBodyBytes);
        equal("body range total", BODY_RANGES, totalRanges);
        equal("external instruction total", EXTERNAL_INSTRUCTIONS,
            totalInstructions);
        equal("thunk count", 1, thunkCount);
        require(forbidden.equals(Set.of(
                "0x00542720", "0x005d0ad6", "0x005d0aea")),
            "forbidden-entry set drifted");
        require(entries.contains("0x0045ac20")
                && entries.contains("0x00542710")
                && !entries.contains("0x00542720")
                && !entries.contains("0x005b8500")
                && !entries.contains("0x005d0ad6")
                && !entries.contains("0x005d0aea"),
            "required include/exclude set drifted");
        Target tailOwner = targets.stream()
            .filter(target -> target.entryText.equals("0x00542710"))
            .findFirst().orElseThrow();
        equal("tail-owner ranges",
            "0x00542710-0x0054271a;0x00542720-0x00542736",
            tailOwner.rangesText);
        return targets;
    }

    private void validateTargetBytesAndPlacement(Target target) throws Exception {
        equal("body bytes sha256 at " + target.id,
            target.bodyBytesSha256, bodyBytesSha256(target.body));
        require(target.bodyBytes == target.body.getNumAddresses(),
            "body bytes mismatch at " + target.id);
        for (AddressRange range : target.body) {
            MemoryBlock first = currentProgram.getMemory().getBlock(range.getMinAddress());
            MemoryBlock last = currentProgram.getMemory().getBlock(range.getMaxAddress());
            require(first != null && first == last && TEXT_BLOCK.equals(first.getName())
                    && first.isExecute() && first.isInitialized(),
                "target body is not initialized executable .text at " + target.id);
        }
    }

    private Function exactFunction(Target target) {
        Function function =
            currentProgram.getFunctionManager().getFunctionAt(target.entry);
        return function != null && function.getEntryPoint().equals(target.entry)
            ? function : null;
    }

    private void validateAbsent(Target target) {
        require(exactFunction(target) == null,
            "target function already exists at " + target.entryText);
        AddressIterator addresses = target.body.getAddresses(true);
        while (addresses.hasNext()) {
            Address address = addresses.next();
            Function containing =
                currentProgram.getFunctionManager().getFunctionContaining(address);
            if (containing != null) {
                throw new IllegalStateException(
                    "target body overlaps function "
                    + canonical(containing.getEntryPoint())
                    + " at " + canonical(address));
            }
        }
        Symbol primary = currentProgram.getSymbolTable().getPrimarySymbol(target.entry);
        require(primary == null || primary.getSource() == SourceType.DEFAULT,
            "target has non-default primary symbol at " + target.entryText);
    }

    private Observation observePresent(Target target, String status) throws Exception {
        Function function = exactFunction(target);
        require(function != null, "target function is absent at " + target.entryText);
        AddressSetView body = function.getBody();
        String actualRanges = canonicalRanges(body);
        long actualBytes = body.getNumAddresses();
        String actualBodySha = bodyBytesSha256(body);
        require(actualRanges.equals(target.rangesText)
                && actualBytes == target.bodyBytes
                && actualBodySha.equals(target.bodyBytesSha256),
            "BODY_ENVELOPE_MISMATCH entry=" + target.entryText
            + " expected=" + target.rangesText + " actual=" + actualRanges);
        boolean expectedThunk = target.entryText.equals("0x0045ac20");
        equal("thunk kind at " + target.entryText,
            expectedThunk, function.isThunk());
        if (expectedThunk) {
            Function thunked = function.getThunkedFunction(false);
            require(thunked != null
                    && canonical(thunked.getEntryPoint()).equals("0x0045ac30"),
                "0x0045AC20 is not a thunk to 0x0045AC30");
        }
        require(instructionCoverage(target.body).hasSameAddresses(target.body),
            "admitted function body is not fully disassembled at " + target.entryText);
        long actualInstructionCount = instructionCount(body);
        equal("Ghidra/external instruction count at " + target.entryText,
            target.externalInstructionCount, actualInstructionCount);
        Symbol symbol = function.getSymbol();
        require(symbol != null && symbol.getSource() == SourceType.DEFAULT,
            "created boundary does not retain a default symbol at " + target.entryText);
        if (expectedThunk) {
            Function thunked = function.getThunkedFunction(false);
            require(thunked != null && function.getName().equals(thunked.getName()),
                "default thunk name does not mirror its exact target at "
                + target.entryText + " actual=" + clean(function.getName()));
        } else {
            require(function.getName().equals("FUN_" + target.entry.toString()),
                "created boundary does not retain the default FUN name at "
                + target.entryText + " actual=" + clean(function.getName()));
        }
        Function thunked = function.isThunk()
            ? function.getThunkedFunction(false) : null;
        return new Observation(target, status, clean(function.getName()),
            symbol.getSource().toString(), actualRanges, actualBytes,
            actualBodySha, actualInstructionCount,
            String.valueOf(function.isThunk()),
            thunked == null ? "" : canonical(thunked.getEntryPoint()));
    }

    private Observation observeAbsent(Target target, String status) {
        validateAbsent(target);
        return new Observation(target, status, "", "", "", 0, "", 0,
            "", "");
    }
    private void validateProtectedState(boolean admitted) throws Exception {
        Address tail = parseAddress("0x00542720", "local tail");
        Address filter = parseAddress("0x005d0ad6", "parent filter");
        Address handler = parseAddress("0x005d0aea", "parent handler");
        Address excluded = parseAddress("0x005b8500", "excluded canary");
        for (Address entry : List.of(tail, filter, handler, excluded)) {
            require(currentProgram.getFunctionManager().getFunctionAt(entry) == null,
                "protected address became a function entry at " + canonical(entry));
        }
        if (admitted) {
            Function tailOwner =
                currentProgram.getFunctionManager().getFunctionContaining(tail);
            require(tailOwner != null
                    && canonical(tailOwner.getEntryPoint()).equals("0x00542710"),
                "0x00542720 is not retained as the 0x00542710 local tail");
        } else {
            require(currentProgram.getFunctionManager().getFunctionContaining(tail) == null,
                "PRE unexpectedly owns the 0x00542720 local tail");
        }
        require(currentProgram.getFunctionManager().getFunctionContaining(filter) == null
                && currentProgram.getFunctionManager().getFunctionContaining(handler) == null,
            "separate 0x005D0A9F body repair leaked into the P0 campaign");
        require(currentProgram.getFunctionManager().getFunctionContaining(excluded) == null,
            "excluded 0x005B8500 canary is unexpectedly owned");
    }

    private Function createExact(Target target) throws Exception {
        clearContainedInstructions(target);
        ensureDisassembled(target);
        Function function;
        if (target.entryText.equals("0x0045ac20")) {
            function = createFunction(target.entry, null);
        } else {
            FunctionManager manager = currentProgram.getFunctionManager();
            function = manager.createFunction(
                null, target.entry, target.body, SourceType.DEFAULT);
        }
        require(function != null && function.getEntryPoint().equals(target.entry),
            "explicit function creation failed at " + target.entryText);
        observePresent(target, "created");
        return function;
    }

    private void clearContainedInstructions(Target target) {
        Listing listing = currentProgram.getListing();
        Set<Address> starts = new LinkedHashSet<>();
        AddressIterator addresses = target.body.getAddresses(true);
        while (addresses.hasNext()) {
            Address address = addresses.next();
            require(listing.getDefinedDataContaining(address) == null,
                "defined data intersects admitted body at " + canonical(address));
            Instruction instruction = listing.getInstructionContaining(address);
            if (instruction == null) {
                continue;
            }
            require(target.body.contains(
                    instruction.getMinAddress(), instruction.getMaxAddress()),
                "pre-existing instruction crosses admitted body at "
                + canonical(instruction.getMinAddress()));
            starts.add(instruction.getMinAddress());
        }
        List<Address> descending = new ArrayList<>(starts);
        Collections.reverse(descending);
        for (Address start : descending) {
            Instruction instruction = listing.getInstructionAt(start);
            require(instruction != null,
                "pre-existing instruction disappeared before bounded replacement");
            listing.clearCodeUnits(
                instruction.getMinAddress(), instruction.getMaxAddress(), false);
        }
        require(instructionCoverage(target.body).isEmpty(),
            "admitted body retained an instruction after bounded clearing at "
            + target.entryText);
    }

    private void ensureDisassembled(Target target) throws Exception {
        AddressSet covered = instructionCoverage(target.body);
        AddressSet remaining = new AddressSet(target.body);
        remaining.delete(covered);
        Disassembler disassembler = Disassembler.getDisassembler(
            currentProgram, monitor, message -> println(
                "CRT_P0_DISASSEMBLER message=" + clean(message)));
        int passes = 0;
        while (!remaining.isEmpty()) {
            monitor.checkCancelled();
            require(++passes <= target.bodyBytes,
                "disassembly made no bounded progress at " + target.id);
            Address seed = remaining.getMinAddress();
            AddressSet seeds = new AddressSet(seed, seed);
            disassembler.disassemble(seeds, target.body, true);
            AddressSet nextCovered = instructionCoverage(target.body);
            AddressSet nextRemaining = new AddressSet(target.body);
            nextRemaining.delete(nextCovered);
            if (nextRemaining.getNumAddresses() >= remaining.getNumAddresses()) {
                PseudoInstruction pseudo =
                    new PseudoDisassembler(currentProgram).disassemble(seed);
                require(pseudo != null && pseudo.getMinAddress().equals(seed),
                    "pseudo-disassembly failed at " + target.id
                    + " seed=" + canonical(seed));
                require(remaining.contains(pseudo.getMinAddress(), pseudo.getMaxAddress()),
                    "pseudo-disassembly escaped undefined target bytes at " + target.id
                    + " seed=" + canonical(seed));
                Instruction created = currentProgram.getListing().createInstruction(
                    seed, pseudo.getPrototype(), pseudo.getMemBuffer(),
                    pseudo.getProcessorContext(), pseudo.getLength());
                require(created != null
                        && created.getMinAddress().equals(seed)
                        && created.getMaxAddress().equals(pseudo.getMaxAddress()),
                    "pseudo-disassembly materialization failed at " + target.id
                    + " seed=" + canonical(seed));
                nextCovered = instructionCoverage(target.body);
                nextRemaining = new AddressSet(target.body);
                nextRemaining.delete(nextCovered);
            }
            require(nextRemaining.getNumAddresses() < remaining.getNumAddresses(),
                "bounded disassembly made no progress at " + target.id
                + " seed=" + canonical(seed));
            remaining = nextRemaining;
        }
        require(instructionCoverage(target.body).hasSameAddresses(target.body),
            "disassembly did not cover the exact body at " + target.id);
    }

    private void validatePostSnapshot(Map<String, String> before,
            List<Target> targets) throws Exception {
        Map<String, String> after = functionSnapshot();
        require(after.size() == before.size() + targets.size(),
            "POST function count did not advance by target count");
        Set<String> expected = new HashSet<>();
        for (Target target : targets) {
            expected.add(target.entryText);
        }
        Set<String> created = new HashSet<>(after.keySet());
        created.removeAll(before.keySet());
        require(created.equals(expected),
            "created function entry set differs from target manifest");
        for (Map.Entry<String, String> row : before.entrySet()) {
            equal("non-target function changed at " + row.getKey(),
                row.getValue(), after.get(row.getKey()));
        }
    }

    private void validateInstructionDelta(Map<String, String> before,
            AddressSetView authorizedBodies) throws Exception {
        Map<String, String> after = instructionSnapshot();
        for (Map.Entry<String, String> row : before.entrySet()) {
            Address start = parseAddress(row.getKey(), "PRE instruction");
            if (!authorizedBodies.contains(start)) {
                equal("instruction outside admitted bodies changed at " + row.getKey(),
                    row.getValue(), after.get(row.getKey()));
            }
        }
        for (Map.Entry<String, String> row : after.entrySet()) {
            if (row.getValue().equals(before.get(row.getKey()))) {
                continue;
            }
            Address start = parseAddress(row.getKey(), "new instruction");
            Instruction instruction = currentProgram.getListing().getInstructionAt(start);
            require(instruction != null
                    && authorizedBodies.contains(
                        instruction.getMinAddress(), instruction.getMaxAddress()),
                "new instruction escaped admitted bodies at " + row.getKey());
        }
    }

    private void validateReferenceDelta(Set<String> before,
            AddressSetView authorizedBodies) {
        Set<String> after = referenceSnapshot();
        for (String row : before) {
            String from = row.substring(0, row.indexOf('|'));
            if (!authorizedBodies.contains(parseAddress(from, "PRE reference source"))) {
                require(after.contains(row),
                    "reference outside admitted bodies changed: " + row);
            }
        }
        for (String row : after) {
            if (before.contains(row)) {
                continue;
            }
            String from = row.substring(0, row.indexOf('|'));
            require(authorizedBodies.contains(parseAddress(from, "new reference source")),
                "new reference escaped admitted bodies: " + row);
        }
    }

    private byte[] buildTsv(List<Observation> rows) {
        StringBuilder out = new StringBuilder();
        out.append("candidateId\tcohort\tentry\tstatus\tname\tnameSource")
            .append("\texpectedRanges\tactualRanges")
            .append("\texpectedBodyBytes\tactualBodyBytes\texpectedBodySha256")
            .append("\tactualBodySha256\texternalInstructionCount")
            .append("\tactualGhidraInstructionCount\texpectedIsThunk\tactualIsThunk")
            .append("\texpectedThunkTarget\tactualThunkTarget\tforbiddenEntries")
            .append("\tresidualEntityKey\tcontractId\tpromotionLane\n");
        for (Observation row : rows) {
            Target target = row.target;
            out.append(target.id).append('\t').append(target.cohort).append('\t')
                .append(target.entryText).append('\t')
                .append(row.status).append('\t')
                .append(row.name).append('\t').append(row.nameSource).append('\t')
                .append(target.rangesText).append('\t').append(row.actualRanges).append('\t')
                .append(target.bodyBytes).append('\t').append(row.actualBodyBytes).append('\t')
                .append(target.bodyBytesSha256).append('\t').append(row.actualBodyBytesSha256).append('\t')
                .append(target.externalInstructionCount).append('\t')
                .append(row.actualGhidraInstructionCount).append('\t')
                .append(target.expectedThunk).append('\t').append(row.actualIsThunk).append('\t')
                .append(target.expectedThunkTarget).append('\t').append(row.actualThunkTarget).append('\t')
                .append(target.forbiddenEntries).append('\t')
                .append(target.residualEntityKey).append('\t')
                .append(target.contractId).append('\t')
                .append(target.promotionLane).append('\n');
        }
        return out.toString().getBytes(StandardCharsets.UTF_8);
    }

    private static String relativePosix(File repository, File artifact)
            throws Exception {
        File canonical = artifact.getCanonicalFile();
        require(canonical.toPath().startsWith(repository.toPath()),
            "receipt artifact escapes repository root: " + canonical);
        return repository.toPath().relativize(canonical.toPath()).toString()
            .replace(File.separatorChar, '/');
    }

    private byte[] buildReady(String mode, File repository, File manifest,
            byte[] manifestBytes,
            File tool, byte[] toolBytes, File output, byte[] outputBytes,
            long functionsBefore, long functionsAfter,
            long instructionsBefore, long instructionsAfter) throws Exception {
        StringBuilder out = new StringBuilder();
        out.append("{\n");
        out.append("  \"schemaVersion\": \"").append(SCHEMA).append("\",\n");
        out.append("  \"completedAtUtc\": \"").append(Instant.now()).append("\",\n");
        out.append("  \"mode\": \"").append(mode).append("\",\n");
        out.append("  \"tool\": {\"path\": \"")
            .append(json(relativePosix(repository, tool)))
            .append("\", \"bytes\": ").append(toolBytes.length)
            .append(", \"sha256\": \"").append(sha256(toolBytes)).append("\"},\n");
        out.append("  \"manifest\": {\"path\": \"")
            .append(json(relativePosix(repository, manifest)))
            .append("\", \"bytes\": ").append(manifestBytes.length)
            .append(", \"sha256\": \"").append(sha256(manifestBytes)).append("\"},\n");
        out.append("  \"output\": {\"path\": \"")
            .append(json(relativePosix(repository, output)))
            .append("\", \"bytes\": ").append(outputBytes.length)
            .append(", \"sha256\": \"").append(sha256(outputBytes)).append("\"},\n");
        out.append("  \"program\": {\"name\": \"").append(PROGRAM_NAME)
            .append("\", \"md5\": \"").append(PROGRAM_MD5)
            .append("\", \"sha256\": \"").append(PROGRAM_SHA256).append("\"},\n");
        out.append("  \"counts\": {\"targets\": ").append(TARGET_COUNT)
            .append(", \"externalInstructions\": ").append(EXTERNAL_INSTRUCTIONS)
            .append(", \"ghidraBodyInstructions\": ").append(GHIDRA_BODY_INSTRUCTIONS)
            .append(", \"functionsBefore\": ").append(functionsBefore)
            .append(", \"functionsAfter\": ").append(functionsAfter)
            .append(", \"instructionsBefore\": ").append(instructionsBefore)
            .append(", \"instructionsAfter\": ").append(instructionsAfter).append("},\n");
        out.append("  \"explicitBodySetsAuthorized\": true,\n");
        out.append("  \"sourceCohortSha256\": \"").append(RUN_C_COHORT_SHA256)
            .append("\",\n");
        out.append("  \"bodyBytes\": ").append(BODY_BYTES).append(",\n");
        out.append("  \"bodyRanges\": ").append(BODY_RANGES).append(",\n");
        out.append("  \"preFunctionRanges\": ").append(PRE_RANGES).append(",\n");
        out.append("  \"postFunctionRanges\": ").append(POST_RANGES).append(",\n");
        out.append("  \"protectedEntries\": [\"0x00542720\", \"0x005d0ad6\", \"0x005d0aea\"],\n");
        out.append("  \"excludedCanary\": \"0x005b8500\",\n");
        out.append("  \"postCountsPinned\": ").append(POST_COUNTS_PINNED)
            .append(",\n");
        out.append("  \"namesAuthorized\": false,\n");
        out.append("  \"metadataAuthorized\": false,\n");
        out.append("  \"separateReadbackRequired\": ")
            .append(!mode.equals("readback")).append("\n");
        out.append("}\n");
        return out.toString().getBytes(StandardCharsets.UTF_8);
    }

    private static File requireNewOutput(String value, String label) throws Exception {
        File output = new File(value).getCanonicalFile();
        require(!output.exists(), label + " already exists: " + output);
        File parent = output.getParentFile();
        require(parent != null && parent.isDirectory(),
            label + " parent is not an existing directory");
        return output;
    }

    private static File stage(File output, byte[] bytes) throws Exception {
        File partial = new File(output.getParentFile(),
            "." + output.getName() + ".partial-" + UUID.randomUUID());
        try (FileChannel channel = FileChannel.open(partial.toPath(),
                StandardOpenOption.CREATE_NEW, StandardOpenOption.WRITE)) {
            ByteBuffer buffer = ByteBuffer.wrap(bytes);
            while (buffer.hasRemaining()) {
                channel.write(buffer);
            }
            channel.force(true);
        }
        return partial;
    }

    private static void publish(File partial, File output) throws Exception {
        Files.createLink(output.toPath(), partial.toPath());
        Files.delete(partial.toPath());
    }

    private byte[] readToolSource() throws Exception {
        try (InputStream stream = getSourceFile().getInputStream()) {
            return stream.readAllBytes();
        }
    }

    private void publishReceipts(String mode, File repository, File manifest,
            byte[] manifestBytes,
            File output, File ready,
            List<Observation> rows, long functionsBefore, long functionsAfter,
            long instructionsBefore, long instructionsAfter) throws Exception {
        byte[] outputBytes = buildTsv(rows);
        byte[] toolBytes = readToolSource();
        File tool = new File(getSourceFile().getCanonicalPath()).getCanonicalFile();
        byte[] readyBytes = buildReady(mode, repository, manifest, manifestBytes,
            tool, toolBytes, output, outputBytes,
            functionsBefore, functionsAfter, instructionsBefore, instructionsAfter);
        File stagedOutput = null;
        File stagedReady = null;
        try {
            stagedOutput = stage(output, outputBytes);
            stagedReady = stage(ready, readyBytes);
            publish(stagedOutput, output);
            stagedOutput = null;
            publish(stagedReady, ready);
            stagedReady = null;
        } finally {
            if (stagedOutput != null) {
                Files.deleteIfExists(stagedOutput.toPath());
            }
            if (stagedReady != null) {
                Files.deleteIfExists(stagedReady.toPath());
            }
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        require(args != null && args.length == 4,
            "usage: <repository-root> <out.tsv> <out.ready.json> " +
            "<dry|probe-after-one|probe-post-inner|apply|readback>");
        File repository = new File(args[0]).getCanonicalFile();
        File manifest = new File(repository, MANIFEST_RELATIVE).getCanonicalFile();
        require(manifest.isFile(), "tracked manifest is missing");
        require(manifest.toPath().startsWith(repository.toPath()),
            "tracked manifest escapes repository root");
        File output = requireNewOutput(args[1], "output TSV");
        File ready = requireNewOutput(args[2], "READY receipt");
        require(!output.equals(ready), "output paths must differ");
        File labRoot = new File(repository, "local-lab").getCanonicalFile();
        require(output.toPath().startsWith(labRoot.toPath())
                && ready.toPath().startsWith(labRoot.toPath()),
            "receipts must stay inside this repository's local-lab tree");
        require(output.getParentFile().equals(ready.getParentFile()),
            "output TSV and READY receipt must share one run directory");
        String mode = args[3];
        require(Arrays.asList("dry", "probe-after-one", "probe-post-inner",
                "apply", "readback").contains(mode),
            "unsupported mode: " + mode);
        require(POST_COUNTS_PINNED || !mode.equals("readback"),
            "exploratory tool cannot authorize a saved readback");

        validateProgramIdentity();
        List<Target> targets = loadTargets(manifest);
        for (Target target : targets) {
            monitor.checkCancelled();
            validateTargetBytesAndPlacement(target);
        }

        long expectedInitialFunctions = mode.equals("readback")
            ? POST_FUNCTIONS : PRE_FUNCTIONS;
        equal("initial function count", expectedInitialFunctions,
            internalFunctionCount());
        long expectedInitialInstructions = mode.equals("readback")
            ? POST_INSTRUCTIONS : PRE_INSTRUCTIONS;
        equal("initial instruction count", expectedInitialInstructions,
            programInstructionCount());
        long expectedInitialReferences = mode.equals("readback")
            ? POST_REFERENCES : PRE_REFERENCES;
        equal("initial reference count", expectedInitialReferences,
            referenceCount());
        validateProtectedState(mode.equals("readback"));
        long expectedInitialRanges = mode.equals("readback")
            ? POST_RANGES : PRE_RANGES;
        equal("initial function range count", expectedInitialRanges,
            internalFunctionRangeCount());
        Map<String, String> before = functionSnapshot();
        Map<String, String> instructionsBeforeSnapshot = instructionSnapshot();
        Set<String> referencesBeforeSnapshot = referenceSnapshot();
        AddressSet authorizedBodies = new AddressSet();
        for (Target target : targets) {
            authorizedBodies.add(target.body);
        }
        List<Observation> rows = new ArrayList<>();
        long functionsBefore = before.size();
        long instructionsBefore = programInstructionCount();

        if (mode.equals("dry")) {
            for (Target target : targets) {
                rows.add(observeAbsent(target, "ready_absent"));
            }
            publishReceipts(mode, repository, manifest,
                Files.readAllBytes(manifest.toPath()),
                output, ready, rows, functionsBefore, functionsBefore,
                instructionsBefore, instructionsBefore);
            println("CRT_P0_BOUNDARIES_OK mode=dry targets=" + TARGET_COUNT
                + " functions=" + functionsBefore);
            return;
        }

        if (mode.equals("readback")) {
            for (Target target : targets) {
                rows.add(observePresent(target, "verified"));
            }
            equal("readback Ghidra body instruction count",
                GHIDRA_BODY_INSTRUCTIONS, instructionCount(authorizedBodies));
            validateProtectedState(true);
            equal("readback function count", POST_FUNCTIONS,
                internalFunctionCount());
            equal("readback function range count", POST_RANGES,
                internalFunctionRangeCount());
            equal("readback instruction count", POST_INSTRUCTIONS,
                programInstructionCount());
            equal("readback reference count", POST_REFERENCES,
                referenceCount());
            publishReceipts(mode, repository, manifest,
                Files.readAllBytes(manifest.toPath()),
                output, ready, rows, functionsBefore, functionsBefore,
                instructionsBefore, instructionsBefore);
            println("CRT_P0_BOUNDARIES_OK mode=readback targets=" + TARGET_COUNT
                + " functions=" + functionsBefore);
            return;
        }

        for (Target target : targets) {
            validateAbsent(target);
        }

        int transaction = -1;
        boolean ended = false;
        try {
            if (mode.equals("probe-after-one")) {
                transaction = currentProgram.startTransaction(
                    "CRT P0 forced failure after one explicit function");
                createExact(targets.get(0));
                println("CRT_P0_BOUNDARIES_FORCED_AFTER_ONE_FAILURE entry="
                    + targets.get(0).entryText + " rollback_requested=true");
                throw new IntentionalProbeException(
                    "forced failure after one CRT P0 function");
            }

            transaction = currentProgram.startTransaction(
                "Create 23 exact CRT P0 function boundaries");
            for (Target target : targets) {
                createExact(target);
            }
            validateProtectedState(true);
            equal("transient Ghidra body instruction count",
                GHIDRA_BODY_INSTRUCTIONS, instructionCount(authorizedBodies));
            validatePostSnapshot(before, targets);
            validateInstructionDelta(instructionsBeforeSnapshot, authorizedBodies);
            validateReferenceDelta(referencesBeforeSnapshot, authorizedBodies);
            equal("transient function count", POST_FUNCTIONS,
                internalFunctionCount());
            equal("transient function range count", POST_RANGES,
                internalFunctionRangeCount());
            if (POST_COUNTS_PINNED) {
                equal("transient instruction count", POST_INSTRUCTIONS,
                    programInstructionCount());
                equal("transient reference count", POST_REFERENCES,
                    referenceCount());
            } else {
                println("CRT_P0_EXPLORATORY_COUNTS instructions="
                    + programInstructionCount() + " references=" + referenceCount());
            }
            boolean commit = !mode.equals("probe-post-inner");
            boolean commitReturned = currentProgram.endTransaction(transaction, commit);
            ended = true;
            require(!commitReturned,
                "nested transaction unexpectedly finalized the outer script transaction");

            if (mode.equals("probe-post-inner")) {
                println("CRT_P0_BOUNDARIES_POST_INNER_ROLLBACK_REQUESTED "
                    + "targets=" + TARGET_COUNT
                    + " transaction_state_visible_until_outer_close=true"
                    + " separate_readback_required=true");
                println("CRT_P0_BOUNDARIES_FORCED_POST_INNER_FAILURE "
                    + "inner_rollback_requested=true outer_rollback_required=true");
                throw new IntentionalProbeException(
                    "forced failure after full nested admission rollback");
            }

            require(mode.equals("apply"), "unexpected mutating mode");
            for (Target target : targets) {
                rows.add(observePresent(target, "created"));
            }
            long functionsAfter = internalFunctionCount();
            long instructionsAfter = programInstructionCount();
            publishReceipts(mode, repository, manifest,
                Files.readAllBytes(manifest.toPath()),
                output, ready, rows, functionsBefore, functionsAfter,
                instructionsBefore, instructionsAfter);
            println("CRT_P0_BOUNDARIES_OK mode=apply targets=" + TARGET_COUNT
                + " functions_before=" + functionsBefore
                + " functions_after=" + functionsAfter);
        } catch (IntentionalProbeException ex) {
            if (transaction >= 0 && !ended) {
                boolean rollbackReturned =
                    currentProgram.endTransaction(transaction, false);
                ended = true;
                require(!rollbackReturned,
                    "probe rollback unexpectedly finalized outer transaction");
            }
            println("CRT_P0_BOUNDARIES_MUTATION_TAINTED mode=" + mode
                + " recovery=OUTER_ROLLBACK_AND_SEPARATE_READBACK_REQUIRED");
            throw ex;
        } catch (Exception ex) {
            if (transaction >= 0 && !ended) {
                try {
                    currentProgram.endTransaction(transaction, false);
                    ended = true;
                } catch (Exception rollbackError) {
                    ex.addSuppressed(rollbackError);
                }
            }
            println("CRT_P0_BOUNDARIES_MUTATION_TAINTED mode=" + mode
                + " recovery=RESTORE_VERIFIED_SCRATCH_BASE error=" + clean(ex.toString()));
            throw ex;
        }
    }
}
