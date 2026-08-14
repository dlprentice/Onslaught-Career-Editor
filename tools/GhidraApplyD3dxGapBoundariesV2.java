//@category Symbol
//
// Admit only the two reviewed PC/Xbox D3DX gap boundaries to an exact current
// 8,327-function/db.18617 disposable copy.  Bounded disassembly is authorized
// only inside those two single-range bodies; no disassembly outside them and no
// name, signature, comment, data, byte, or explicit-reference mutation is
// authorized.  The already admitted 0x00576B4D body is outside this campaign.
//
// Usage:
//   -postScript GhidraApplyD3dxGapBoundariesV2.java
//       <repository-root> <out.tsv> <out.ready.json>
//       <dry|probe-after-one|probe-post-inner|apply|readback>

import ghidra.app.script.GhidraScript;
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
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

public class GhidraApplyD3dxGapBoundariesV2 extends GhidraScript {

    private static final String SCHEMA = "bea.ghidra.d3dx-gap-two-boundaries.v2";
    private static final String PROGRAM_NAME = "BEA.exe";
    private static final String PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55";
    private static final String PROGRAM_SHA256 =
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
    private static final String IMAGE_BASE = "00400000";
    private static final String LANGUAGE = "x86:LE:32:default";
    private static final String COMPILER_SPEC = "windows";
    private static final String TEXT_BLOCK = ".text";
    private static final long PRE_FUNCTIONS = 8327;
    private static final long POST_FUNCTIONS = 8329;
    private static final long PRE_INSTRUCTIONS = 551143;
    private static final long POST_INSTRUCTIONS = 551143;
    private static final long PRE_REFERENCES = 234478;
    private static final long POST_REFERENCES = 234478;
    private static final int TARGET_COUNT = 2;
    private static final String MANIFEST_RELATIVE =
        "reverse-engineering/binary-analysis/" +
        "d3dx-gap-two-function-current-manifest-2026-08-14.tsv";
    private static final long MANIFEST_BYTES = 622;
    private static final String MANIFEST_SHA256 =
        "48da3f9e6c6606a5a7c14443e6fe5f3191a24fb35dfc40ec67f886f27d0351e7";
    private static final String MANIFEST_HEADER =
        "entry\texpectedRanges\texpectedBodyBytes\texpectedRangeDigest" +
        "\texpectedBodyBytesSha256\texpectedInstructionCount\tcurrentState" +
        "\tpromotionLane";

    private static class Target {
        final String id;
        final String cohort;
        final String entryText;
        final Address entry;
        final String rangesText;
        final AddressSet body;
        final long bodyBytes;
        final long externalInstructionCount;
        final String bodyRangeSha256;
        final String bodyBytesSha256;

        Target(String id, String cohort, String entryText, Address entry,
                String rangesText, AddressSet body, long bodyBytes,
                long externalInstructionCount, String bodyRangeSha256,
                String bodyBytesSha256) {
            this.id = id;
            this.cohort = cohort;
            this.entryText = entryText;
            this.entry = entry;
            this.rangesText = rangesText;
            this.body = body;
            this.bodyBytes = bodyBytes;
            this.externalInstructionCount = externalInstructionCount;
            this.bodyRangeSha256 = bodyRangeSha256;
            this.bodyBytesSha256 = bodyBytesSha256;
        }
    }

    private static class Observation {
        final Target target;
        final String status;
        final String name;
        final String nameSource;
        final String actualRanges;
        final long actualBodyBytes;
        final String actualRangeSha256;
        final String actualBodyBytesSha256;
        final long actualGhidraInstructionCount;

        Observation(Target target, String status, String name, String nameSource,
                String actualRanges, long actualBodyBytes, String actualRangeSha256,
                String actualBodyBytesSha256, long actualGhidraInstructionCount) {
            this.target = target;
            this.status = status;
            this.name = name;
            this.nameSource = nameSource;
            this.actualRanges = actualRanges;
            this.actualBodyBytes = actualBodyBytes;
            this.actualRangeSha256 = actualRangeSha256;
            this.actualBodyBytesSha256 = actualBodyBytesSha256;
            this.actualGhidraInstructionCount = actualGhidraInstructionCount;
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
        Address priorEntry = null;
        AddressSet allBodies = new AddressSet();
        for (int index = 1; index <= TARGET_COUNT; index++) {
            String[] fields = lines[index].split("\\t", -1);
            require(fields.length == 8,
                "manifest field count mismatch at row " + index);
            String expectedId = String.format(
                Locale.ROOT, "D3DX-GAP-%03d", index + 1);
            Address entry = parseAddress(fields[0], "retail entry");
            require(entries.add(canonical(entry)),
                "duplicate target entry: " + canonical(entry));
            if (priorEntry != null) {
                require(priorEntry.compareTo(entry) < 0,
                    "target entries are not strictly sorted");
            }
            priorEntry = entry;
            AddressSet body = parseRanges(fields[1], expectedId);
            require(body.getMinAddress().equals(entry),
                "entry is not body minimum at " + expectedId);
            long bodyBytes = positiveLong(fields[2], "body bytes");
            require(bodyBytes == body.getNumAddresses(),
                "body byte count mismatch at " + expectedId);
            String rangeSha = requireHash(fields[3], "range sha256");
            String bodySha = requireHash(fields[4], "body sha256");
            long externalInstructions = positiveLong(fields[5],
                "external instruction count");
            equal("range digest at " + expectedId,
                rangeSha, bodyRangeSha256(body));
            equal("current state at " + expectedId,
                "ABSENT_FROM_CURRENT_8327_FUNCTION_CENSUS", fields[6]);
            equal("promotion lane at " + expectedId,
                "D3DX_GAP_TWO_CURRENT_PREPARATION", fields[7]);
            require(!allBodies.intersects(body),
                "candidate bodies overlap at " + expectedId);
            allBodies.add(body);
            targets.add(new Target(expectedId, "D3DX_GAP_TWO", canonical(entry), entry,
                canonicalRanges(body), body, bodyBytes, externalInstructions,
                rangeSha, bodySha));
        }
        require(entries.equals(Set.of("0x00595fc9", "0x00596028")),
            "exact D3DX entry set drifted");
        return targets;
    }

    private void validateTargetBytesAndPlacement(Target target) throws Exception {
        equal("body range sha256 at " + target.id,
            target.bodyRangeSha256, bodyRangeSha256(target.body));
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
        String actualRangeSha = bodyRangeSha256(body);
        String actualBodySha = bodyBytesSha256(body);
        require(actualRanges.equals(target.rangesText)
                && actualBytes == target.bodyBytes
                && actualRangeSha.equals(target.bodyRangeSha256)
                && actualBodySha.equals(target.bodyBytesSha256),
            "BODY_ENVELOPE_MISMATCH entry=" + target.entryText
            + " expected=" + target.rangesText + " actual=" + actualRanges);
        require(!function.isThunk(),
            "explicit D3DX gap boundary unexpectedly became a thunk at " + target.entryText);
        require(instructionCoverage(target.body).hasSameAddresses(target.body),
            "admitted function body is not fully disassembled at " + target.entryText);
        Symbol symbol = function.getSymbol();
        require(symbol != null && symbol.getSource() == SourceType.DEFAULT,
            "created boundary does not retain a default symbol at " + target.entryText);
        require(function.getName().equals("FUN_" + target.entry.toString()),
            "created boundary does not retain the default FUN name at " + target.entryText);
        return new Observation(target, status, clean(function.getName()),
            symbol.getSource().toString(), actualRanges, actualBytes,
            actualRangeSha, actualBodySha, instructionCount(body));
    }

    private Observation observeAbsent(Target target, String status) {
        validateAbsent(target);
        return new Observation(target, status, "", "", "", 0, "", "", 0);
    }

    private Function createExact(Target target) throws Exception {
        ensureDisassembled(target);
        FunctionManager manager = currentProgram.getFunctionManager();
        Function function = manager.createFunction(
            null, target.entry, target.body, SourceType.DEFAULT);
        require(function != null && function.getEntryPoint().equals(target.entry),
            "explicit function creation failed at " + target.entryText);
        observePresent(target, "created");
        return function;
    }

    private void ensureDisassembled(Target target) throws Exception {
        AddressSet covered = instructionCoverage(target.body);
        AddressSet remaining = new AddressSet(target.body);
        remaining.delete(covered);
        Disassembler disassembler = Disassembler.getDisassembler(
            currentProgram, monitor, message -> println(
                "D3DX_GAP_DISASSEMBLER message=" + clean(message)));
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
            require(nextRemaining.getNumAddresses() < remaining.getNumAddresses(),
                "disassembly made no progress at " + target.id
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
            equal("pre-existing instruction changed at " + row.getKey(),
                row.getValue(), after.get(row.getKey()));
        }
        for (Map.Entry<String, String> row : after.entrySet()) {
            if (before.containsKey(row.getKey())) {
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
        require(after.containsAll(before),
            "one or more PRE references disappeared during admission");
        for (String row : after) {
            if (before.contains(row)) {
                continue;
            }
            String from = row.substring(0, row.indexOf('|'));
            require(authorizedBodies.contains(parseAddress(from, "new reference source")),
                "new reference escaped admitted bodies: " + row);
        }
    }

    private void clearNewInstructions(Map<String, String> before) {
        Listing listing = currentProgram.getListing();
        List<Address> added = new ArrayList<>();
        InstructionIterator instructions = listing.getInstructions(true);
        while (instructions.hasNext()) {
            Instruction instruction = instructions.next();
            if (!before.containsKey(canonical(instruction.getAddress()))) {
                added.add(instruction.getAddress());
            }
        }
        for (int index = added.size() - 1; index >= 0; index--) {
            Instruction instruction = listing.getInstructionAt(added.get(index));
            require(instruction != null,
                "new instruction disappeared before compensation");
            listing.clearCodeUnits(
                instruction.getMinAddress(), instruction.getMaxAddress(), false);
        }
    }

    private byte[] buildTsv(List<Observation> rows) {
        StringBuilder out = new StringBuilder();
        out.append("candidateId\tcohort\tentry\tstatus\tname\tnameSource")
            .append("\texpectedRanges\tactualRanges\texpectedBodyBytes")
            .append("\tactualBodyBytes\texpectedRangeSha256\tactualRangeSha256")
            .append("\texpectedBodyBytesSha256\tactualBodyBytesSha256")
            .append("\texternalInstructionCount\tactualGhidraInstructionCount\n");
        for (Observation row : rows) {
            Target target = row.target;
            out.append(target.id).append('\t').append(target.cohort).append('\t')
                .append(target.entryText).append('\t').append(row.status).append('\t')
                .append(row.name).append('\t').append(row.nameSource).append('\t')
                .append(target.rangesText).append('\t').append(row.actualRanges).append('\t')
                .append(target.bodyBytes).append('\t').append(row.actualBodyBytes).append('\t')
                .append(target.bodyRangeSha256).append('\t').append(row.actualRangeSha256).append('\t')
                .append(target.bodyBytesSha256).append('\t').append(row.actualBodyBytesSha256).append('\t')
                .append(target.externalInstructionCount).append('\t')
                .append(row.actualGhidraInstructionCount).append('\n');
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
            byte[] manifestBytes, File tool, byte[] toolBytes, File output,
            byte[] outputBytes,
            long functionsBefore, long functionsAfter,
            long instructionsBefore, long instructionsAfter,
            long referencesBefore, long referencesAfter) throws Exception {
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
            .append(", \"functionsBefore\": ").append(functionsBefore)
            .append(", \"functionsAfter\": ").append(functionsAfter)
            .append(", \"instructionsBefore\": ").append(instructionsBefore)
            .append(", \"instructionsAfter\": ").append(instructionsAfter)
            .append(", \"referencesBefore\": ").append(referencesBefore)
            .append(", \"referencesAfter\": ").append(referencesAfter).append("},\n");
        out.append("  \"explicitBodySetsAuthorized\": true,\n");
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
            byte[] manifestBytes, File output, File ready,
            List<Observation> rows, long functionsBefore, long functionsAfter,
            long instructionsBefore, long instructionsAfter,
            long referencesBefore, long referencesAfter) throws Exception {
        byte[] outputBytes = buildTsv(rows);
        byte[] toolBytes = readToolSource();
        File tool = new File(getSourceFile().getCanonicalPath()).getCanonicalFile();
        byte[] readyBytes = buildReady(mode, repository, manifest, manifestBytes,
            tool, toolBytes, output, outputBytes,
            functionsBefore, functionsAfter, instructionsBefore, instructionsAfter,
            referencesBefore, referencesAfter);
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
        long referencesBefore = referenceCount();

        if (mode.equals("dry")) {
            for (Target target : targets) {
                rows.add(observeAbsent(target, "ready_absent"));
            }
            publishReceipts(mode, repository, manifest,
                Files.readAllBytes(manifest.toPath()),
                output, ready, rows, functionsBefore, functionsBefore,
                instructionsBefore, instructionsBefore,
                referencesBefore, referencesBefore);
            println("D3DX_GAP_BOUNDARIES_OK mode=dry targets=" + TARGET_COUNT
                + " functions=" + functionsBefore);
            return;
        }

        if (mode.equals("readback")) {
            for (Target target : targets) {
                rows.add(observePresent(target, "verified"));
            }
            equal("readback function count", POST_FUNCTIONS,
                internalFunctionCount());
            equal("readback instruction count", POST_INSTRUCTIONS,
                programInstructionCount());
            equal("readback reference count", POST_REFERENCES,
                referenceCount());
            publishReceipts(mode, repository, manifest,
                Files.readAllBytes(manifest.toPath()),
                output, ready, rows, functionsBefore, functionsBefore,
                instructionsBefore, instructionsBefore,
                referencesBefore, referencesBefore);
            println("D3DX_GAP_BOUNDARIES_OK mode=readback targets=" + TARGET_COUNT
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
                    "D3DX gap forced failure after one explicit function");
                createExact(targets.get(0));
                println("D3DX_GAP_BOUNDARIES_FORCED_AFTER_ONE_FAILURE entry="
                    + targets.get(0).entryText + " rollback_requested=true");
                throw new IntentionalProbeException(
                    "forced failure after one D3DX gap function");
            }

            transaction = currentProgram.startTransaction(
                "Create two exact D3DX gap function boundaries");
            for (Target target : targets) {
                createExact(target);
            }
            validatePostSnapshot(before, targets);
            validateInstructionDelta(instructionsBeforeSnapshot, authorizedBodies);
            validateReferenceDelta(referencesBeforeSnapshot, authorizedBodies);
            equal("transient function count", POST_FUNCTIONS,
                internalFunctionCount());
            equal("transient instruction count", POST_INSTRUCTIONS,
                programInstructionCount());
            equal("transient reference count", POST_REFERENCES,
                referenceCount());
            boolean commitReturned = currentProgram.endTransaction(transaction, true);
            ended = true;
            require(!commitReturned,
                "nested commit unexpectedly finalized the outer script transaction");

            if (mode.equals("probe-post-inner")) {
                int compensation = currentProgram.startTransaction(
                    "Compensate two D3DX gap function boundaries");
                FunctionManager manager = currentProgram.getFunctionManager();
                for (int index = targets.size() - 1; index >= 0; index--) {
                    Target target = targets.get(index);
                    require(manager.removeFunction(target.entry),
                        "compensation could not remove " + target.entryText);
                }
                clearNewInstructions(instructionsBeforeSnapshot);
                boolean compensationReturned =
                    currentProgram.endTransaction(compensation, true);
                require(!compensationReturned,
                    "compensation unexpectedly finalized the outer transaction");
                equal("compensated function snapshot", before, functionSnapshot());
                equal("compensated instruction snapshot",
                    instructionsBeforeSnapshot, instructionSnapshot());
                equal("compensated instruction count", PRE_INSTRUCTIONS,
                    programInstructionCount());
                equal("compensated reference snapshot",
                    referencesBeforeSnapshot, referenceSnapshot());
                equal("compensated reference count", PRE_REFERENCES,
                    referenceCount());
                println("D3DX_GAP_BOUNDARIES_COMPENSATING_PRE_RESTORE_COMPLETE "
                    + "targets=" + TARGET_COUNT + " functions=" + internalFunctionCount());
                println("D3DX_GAP_BOUNDARIES_FORCED_POST_INNER_FAILURE "
                    + "outer_rollback_required=true");
                throw new IntentionalProbeException(
                    "forced failure after post-inner compensation");
            }

            require(mode.equals("apply"), "unexpected mutating mode");
            for (Target target : targets) {
                rows.add(observePresent(target, "created"));
            }
            long functionsAfter = internalFunctionCount();
            long instructionsAfter = programInstructionCount();
            long referencesAfter = referenceCount();
            publishReceipts(mode, repository, manifest,
                Files.readAllBytes(manifest.toPath()),
                output, ready, rows, functionsBefore, functionsAfter,
                instructionsBefore, instructionsAfter,
                referencesBefore, referencesAfter);
            println("D3DX_GAP_BOUNDARIES_OK mode=apply targets=" + TARGET_COUNT
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
            println("D3DX_GAP_BOUNDARIES_MUTATION_TAINTED mode=" + mode
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
            println("D3DX_GAP_BOUNDARIES_MUTATION_TAINTED mode=" + mode
                + " recovery=RESTORE_VERIFIED_SCRATCH_BASE error=" + clean(ex.toString()));
            throw ex;
        }
    }
}
