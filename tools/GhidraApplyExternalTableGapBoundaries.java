//@category Symbol
//
// Admit only the 79 reviewed external-table PC .text gap boundaries to an exact
// 8,201-function PRE copy with their preregistered address sets.
// Bounded disassembly is authorized only inside those body sets: existing
// instructions may be cleared only when their complete
// ranges are contained by one target body, and exact target coverage is then rebuilt.
// The normal disassembler is tried first; when it rejects a valid orphan instruction
// start, a one-instruction pseudo-decode may be materialized only when its complete
// byte range is still undefined and inside the same target body.
// No disassembly outside the bodies and no name, signature, comment, data, byte, or
// explicit reference mutation is authorized.  Operand references derived by Ghidra
// while creating an instruction are admitted only when their source is in a body.
//
// Usage:
//   -postScript GhidraApplyExternalTableGapBoundaries.java
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

public class GhidraApplyExternalTableGapBoundaries extends GhidraScript {

    private static final String SCHEMA =
        "bea.ghidra.external-table-gap-boundaries.v2";
    private static final String PROGRAM_NAME = "BEA.exe";
    private static final String PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55";
    private static final String PROGRAM_SHA256 =
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
    private static final String IMAGE_BASE = "00400000";
    private static final String LANGUAGE = "x86:LE:32:default";
    private static final String COMPILER_SPEC = "windows";
    private static final String TEXT_BLOCK = ".text";
    private static final long PRE_FUNCTIONS = 8201;
    private static final long POST_FUNCTIONS = 8280;
    private static final long PRE_INSTRUCTIONS = 550982;
    private static final long POST_INSTRUCTIONS = 550991;
    private static final long PRE_REFERENCES = 234537;
    private static final long POST_REFERENCES = 234495;
    private static final boolean POST_COUNTS_PINNED = true;
    private static final long EXTERNAL_INSTRUCTIONS = 3319;
    private static final long GHIDRA_BODY_INSTRUCTIONS = 3318;
    private static final int TARGET_COUNT = 79;
    private static final String MANIFEST_RELATIVE =
        "reverse-engineering/binary-analysis/" +
        "external-table-gap-function-boundaries-2026-08-13.tsv";
    private static final long MANIFEST_BYTES = 30020;
    private static final String MANIFEST_SHA256 =
        "4293ebb936639299301985f128728b127ca60014693871a981d2324d47f2044f";
    private static final String VEC4_RECEIPT_RELATIVE =
        "reverse-engineering/binary-analysis/" +
        "d3dx-vec4cross-crossbuild-boundary-2026-08-13.md";
    private static final long VEC4_RECEIPT_BYTES = 4862;
    private static final String VEC4_RECEIPT_SHA256 =
        "1a7e705984830fee60f3d0710c0b017bd663ef27a805f1aa14beb0625863d306";
    private static final String MANIFEST_HEADER =
        "rank\tretail_va\tidentity_status\tsafe_name_candidate\tcohort" +
        "\tsource\tprovider_identity_candidate\tdirect_defined_data_ref" +
        "\treference_rows\tgap_start\tgap_end_exclusive\tbody_ranges" +
        "\tbody_bytes\tinstruction_count\tbody_sha256\tnormalized_sha256" +
        "\tterminal_kinds\texternal_transfers\tdemo_va\tdemo_candidates" +
        "\tdemo_basis\tdemo_normalized_equal\tdemo_raw_equal" +
        "\talready_prepared_receipt";

    private static class Target {
        final String id;
        final String rank;
        final String identityStatus;
        final String safeNameCandidate;
        final String cohort;
        final String entryText;
        final Address entry;
        final String rangesText;
        final AddressSet body;
        final long bodyBytes;
        final long externalInstructionCount;
        final String bodyBytesSha256;
        final String demoEntry;
        final long demoCandidates;
        final String demoBasis;
        final boolean demoRawEqual;
        final boolean alreadyPreparedReceipt;

        Target(String id, String rank, String identityStatus,
                String safeNameCandidate, String cohort, String entryText, Address entry,
                String rangesText, AddressSet body, long bodyBytes,
                long externalInstructionCount, String bodyBytesSha256,
                String demoEntry, long demoCandidates, String demoBasis,
                boolean demoRawEqual, boolean alreadyPreparedReceipt) {
            this.id = id;
            this.rank = rank;
            this.identityStatus = identityStatus;
            this.safeNameCandidate = safeNameCandidate;
            this.cohort = cohort;
            this.entryText = entryText;
            this.entry = entry;
            this.rangesText = rangesText;
            this.body = body;
            this.bodyBytes = bodyBytes;
            this.externalInstructionCount = externalInstructionCount;
            this.bodyBytesSha256 = bodyBytesSha256;
            this.demoEntry = demoEntry;
            this.demoCandidates = demoCandidates;
            this.demoBasis = demoBasis;
            this.demoRawEqual = demoRawEqual;
            this.alreadyPreparedReceipt = alreadyPreparedReceipt;
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

        Observation(Target target, String status, String name, String nameSource,
                String actualRanges, long actualBodyBytes,
                String actualBodyBytesSha256, long actualGhidraInstructionCount) {
            this.target = target;
            this.status = status;
            this.name = name;
            this.nameSource = nameSource;
            this.actualRanges = actualRanges;
            this.actualBodyBytes = actualBodyBytes;
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
        Map<String, Integer> rankCounts = new LinkedHashMap<>();
        Map<String, Integer> demoBasisCounts = new LinkedHashMap<>();
        long totalBodyBytes = 0;
        long totalInstructions = 0;
        int rawEqualCount = 0;
        int directReferenceCount = 0;
        int preparedReceiptCount = 0;
        for (int index = 1; index <= TARGET_COUNT; index++) {
            String[] fields = lines[index].split("\\t", -1);
            require(fields.length == 24,
                "manifest field count mismatch at row " + index);
            String expectedId = String.format(Locale.ROOT, "ETG-%03d", index);
            String rank = fields[0];
            require(rank.matches("P[012]"), "invalid preparation rank at " + expectedId);
            rankCounts.put(rank, rankCounts.getOrDefault(rank, 0) + 1);
            Address entry = parseAddress(fields[1], "retail entry");
            require(entries.add(canonical(entry)),
                "duplicate target entry: " + canonical(entry));
            if (priorEntry != null) {
                require(priorEntry.compareTo(entry) < 0,
                    "target entries are not strictly sorted");
            }
            priorEntry = entry;
            String identityStatus = fields[2];
            require(identityStatus.matches("[A-Z0-9_]+"),
                "identity status is not canonical at " + expectedId);
            String safeNameCandidate = fields[3];
            if (rank.equals("P2")) {
                require(safeNameCandidate.isEmpty(),
                    "P2 row unexpectedly carries a semantic name at " + expectedId);
            } else {
                require(safeNameCandidate.matches("[A-Za-z0-9_]+"),
                    "P0/P1 safe name is not canonical at " + expectedId);
            }
            String cohort = fields[4];
            require(cohort.matches("[A-Z0-9_]+"),
                "cohort is not canonical at " + expectedId);
            require(!fields[5].isEmpty(), "source is empty at " + expectedId);
            require(fields[7].equals("true") || fields[7].equals("false"),
                "direct-reference flag is not boolean at " + expectedId);
            if (fields[7].equals("true")) {
                directReferenceCount++;
            }
            positiveLong(fields[8], "reference rows");
            Address gapStart = parseAddress(fields[9], "gap start");
            Address gapEnd = parseAddress(fields[10], "gap end");
            require(gapStart.compareTo(gapEnd) < 0,
                "empty gap envelope at " + expectedId);
            AddressSet body = parseRanges(fields[11], expectedId);
            require(body.getMinAddress().equals(entry),
                "entry is not body minimum at " + expectedId);
            require(gapStart.compareTo(entry) <= 0
                    && body.getMaxAddress().add(1).compareTo(gapEnd) <= 0,
                "body escapes its prepared gap envelope at " + expectedId);
            long bodyBytes = positiveLong(fields[12], "body bytes");
            require(bodyBytes == body.getNumAddresses(),
                "body byte count mismatch at " + expectedId);
            long externalInstructions = positiveLong(fields[13],
                "external instruction count");
            String bodySha = requireHash(fields[14], "body sha256");
            requireHash(fields[15], "normalized body sha256");
            require(!fields[16].isEmpty(), "terminal kind is empty at " + expectedId);
            Address demoEntry = parseAddress(fields[18], "demo entry");
            long demoCandidates = positiveLong(fields[19], "demo candidates");
            String demoBasis = fields[20];
            require(Set.of(
                    "UNIQUE_FULL_MASKED_BODY",
                    "EQUAL_DELTA_BRACKET_FULL_NORMALIZED_BODY",
                    "CROSS_BUILD_INIT_TABLE_SLOT_FULL_NORMALIZED_BODY"
                ).contains(demoBasis),
                "unsupported demo basis at " + expectedId);
            demoBasisCounts.put(
                demoBasis, demoBasisCounts.getOrDefault(demoBasis, 0) + 1);
            require(fields[21].equals("true"),
                "demo normalized equality is not true at " + expectedId);
            require(fields[22].equals("true") || fields[22].equals("false"),
                "demo raw equality is not boolean at " + expectedId);
            boolean demoRawEqual = fields[22].equals("true");
            if (demoRawEqual) {
                rawEqualCount++;
            }
            require(fields[23].equals("true") || fields[23].equals("false"),
                "prepared-receipt flag is not boolean at " + expectedId);
            boolean alreadyPrepared = fields[23].equals("true");
            if (alreadyPrepared) {
                preparedReceiptCount++;
            }
            require(!allBodies.intersects(body),
                "candidate bodies overlap at " + expectedId);
            allBodies.add(body);
            totalBodyBytes += bodyBytes;
            totalInstructions += externalInstructions;
            targets.add(new Target(expectedId, rank, identityStatus,
                safeNameCandidate, cohort, canonical(entry), entry,
                canonicalRanges(body), body, bodyBytes, externalInstructions,
                bodySha, canonical(demoEntry), demoCandidates, demoBasis,
                demoRawEqual, alreadyPrepared));
        }
        equal("P0 row count", 12, rankCounts.getOrDefault("P0", 0));
        equal("P1 row count", 20, rankCounts.getOrDefault("P1", 0));
        equal("P2 row count", 47, rankCounts.getOrDefault("P2", 0));
        equal("body byte total", 9234L, totalBodyBytes);
        equal("external instruction total", EXTERNAL_INSTRUCTIONS,
            totalInstructions);
        equal("direct-reference row count", 72, directReferenceCount);
        equal("raw-equal demo row count", 26, rawEqualCount);
        equal("unique demo basis count", 45,
            demoBasisCounts.getOrDefault("UNIQUE_FULL_MASKED_BODY", 0));
        equal("equal-delta demo basis count", 33,
            demoBasisCounts.getOrDefault(
                "EQUAL_DELTA_BRACKET_FULL_NORMALIZED_BODY", 0));
        equal("initializer-slot demo basis count", 1,
            demoBasisCounts.getOrDefault(
                "CROSS_BUILD_INIT_TABLE_SLOT_FULL_NORMALIZED_BODY", 0));
        equal("already-prepared receipt count", 1, preparedReceiptCount);

        Target vec4 = targets.stream()
            .filter(target -> target.entryText.equals("0x005762dd"))
            .findFirst().orElseThrow();
        equal("Vec4Cross rank", "P0", vec4.rank);
        equal("Vec4Cross identity", "EXACT_D3DX_PDB_PUBLIC_POST_HOTPATCH",
            vec4.identityStatus);
        equal("Vec4Cross safe name", "D3DX_COMPAT__c_D3DXVec4Cross",
            vec4.safeNameCandidate);
        require(vec4.alreadyPreparedReceipt,
            "Vec4Cross row does not consume its existing receipt");

        Target yuv = targets.stream()
            .filter(target -> target.entryText.equals("0x0058862e"))
            .findFirst().orElseThrow();
        equal("YUV-family rank", "P1", yuv.rank);
        equal("YUV-family identity", "D3DX_SHARED_YUV_CODEC_DTOR_LINEAGE",
            yuv.identityStatus);
        equal("YUV-family safe name",
            "D3DX_COMPAT__CCodecYUVFamily__SharedScalarDeletingDtor",
            yuv.safeNameCandidate);
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
        require(!function.isThunk(),
            "explicit external-table gap boundary unexpectedly became a thunk at "
            + target.entryText);
        require(instructionCoverage(target.body).hasSameAddresses(target.body),
            "admitted function body is not fully disassembled at " + target.entryText);
        long actualInstructionCount = instructionCount(body);
        if (target.entryText.equals("0x0055e3f4")) {
            equal("Ghidra x87 prefix-folded instruction count",
                12L, actualInstructionCount);
            equal("external x87 instruction count",
                13L, target.externalInstructionCount);
        } else {
            equal("Ghidra/external instruction count at " + target.entryText,
                target.externalInstructionCount, actualInstructionCount);
        }
        Symbol symbol = function.getSymbol();
        require(symbol != null && symbol.getSource() == SourceType.DEFAULT,
            "created boundary does not retain a default symbol at " + target.entryText);
        require(function.getName().equals("FUN_" + target.entry.toString()),
            "created boundary does not retain the default FUN name at " + target.entryText);
        return new Observation(target, status, clean(function.getName()),
            symbol.getSource().toString(), actualRanges, actualBytes,
            actualBodySha, actualInstructionCount);
    }

    private Observation observeAbsent(Target target, String status) {
        validateAbsent(target);
        return new Observation(target, status, "", "", "", 0, "", 0);
    }

    private Function createExact(Target target) throws Exception {
        clearContainedInstructions(target);
        ensureDisassembled(target);
        FunctionManager manager = currentProgram.getFunctionManager();
        Function function = manager.createFunction(
            null, target.entry, target.body, SourceType.DEFAULT);
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
                "EXTERNAL_TABLE_GAP_DISASSEMBLER message=" + clean(message)));
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
        out.append("candidateId\trank\tidentityStatus\tsafeNameCandidate\tcohort")
            .append("\tentry\tstatus\tname\tnameSource\texpectedRanges\tactualRanges")
            .append("\texpectedBodyBytes\tactualBodyBytes\texpectedBodySha256")
            .append("\tactualBodySha256\texternalInstructionCount")
            .append("\tactualGhidraInstructionCount\tdemoEntry\tdemoCandidates")
            .append("\tdemoBasis\tdemoRawEqual\talreadyPreparedReceipt\n");
        for (Observation row : rows) {
            Target target = row.target;
            out.append(target.id).append('\t').append(target.rank).append('\t')
                .append(target.identityStatus).append('\t')
                .append(target.safeNameCandidate).append('\t')
                .append(target.cohort).append('\t').append(target.entryText).append('\t')
                .append(row.status).append('\t')
                .append(row.name).append('\t').append(row.nameSource).append('\t')
                .append(target.rangesText).append('\t').append(row.actualRanges).append('\t')
                .append(target.bodyBytes).append('\t').append(row.actualBodyBytes).append('\t')
                .append(target.bodyBytesSha256).append('\t').append(row.actualBodyBytesSha256).append('\t')
                .append(target.externalInstructionCount).append('\t')
                .append(row.actualGhidraInstructionCount).append('\t')
                .append(target.demoEntry).append('\t').append(target.demoCandidates).append('\t')
                .append(target.demoBasis).append('\t').append(target.demoRawEqual).append('\t')
                .append(target.alreadyPreparedReceipt).append('\n');
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
            byte[] manifestBytes, File consumedProof, byte[] consumedProofBytes,
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
        out.append("  \"consumedProof\": {\"path\": \"")
            .append(json(relativePosix(repository, consumedProof)))
            .append("\", \"bytes\": ").append(consumedProofBytes.length)
            .append(", \"sha256\": \"").append(sha256(consumedProofBytes))
            .append("\"},\n");
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
            byte[] manifestBytes, File consumedProof, byte[] consumedProofBytes,
            File output, File ready,
            List<Observation> rows, long functionsBefore, long functionsAfter,
            long instructionsBefore, long instructionsAfter) throws Exception {
        byte[] outputBytes = buildTsv(rows);
        byte[] toolBytes = readToolSource();
        File tool = new File(getSourceFile().getCanonicalPath()).getCanonicalFile();
        byte[] readyBytes = buildReady(mode, repository, manifest, manifestBytes,
            consumedProof, consumedProofBytes, tool, toolBytes, output, outputBytes,
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
        File consumedProof =
            new File(repository, VEC4_RECEIPT_RELATIVE).getCanonicalFile();
        require(consumedProof.isFile()
                && consumedProof.toPath().startsWith(repository.toPath()),
            "Vec4Cross consumed proof is missing or escapes repository root");
        byte[] consumedProofBytes = Files.readAllBytes(consumedProof.toPath());
        equal("Vec4Cross proof bytes", VEC4_RECEIPT_BYTES,
            (long) consumedProofBytes.length);
        equal("Vec4Cross proof sha256", VEC4_RECEIPT_SHA256,
            sha256(consumedProofBytes));
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
                Files.readAllBytes(manifest.toPath()), consumedProof,
                consumedProofBytes,
                output, ready, rows, functionsBefore, functionsBefore,
                instructionsBefore, instructionsBefore);
            println("EXTERNAL_TABLE_GAP_BOUNDARIES_OK mode=dry targets=" + TARGET_COUNT
                + " functions=" + functionsBefore);
            return;
        }

        if (mode.equals("readback")) {
            for (Target target : targets) {
                rows.add(observePresent(target, "verified"));
            }
            equal("readback Ghidra body instruction count",
                GHIDRA_BODY_INSTRUCTIONS, instructionCount(authorizedBodies));
            equal("readback function count", POST_FUNCTIONS,
                internalFunctionCount());
            equal("readback instruction count", POST_INSTRUCTIONS,
                programInstructionCount());
            equal("readback reference count", POST_REFERENCES,
                referenceCount());
            publishReceipts(mode, repository, manifest,
                Files.readAllBytes(manifest.toPath()), consumedProof,
                consumedProofBytes,
                output, ready, rows, functionsBefore, functionsBefore,
                instructionsBefore, instructionsBefore);
            println("EXTERNAL_TABLE_GAP_BOUNDARIES_OK mode=readback targets=" + TARGET_COUNT
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
                    "External-table gap forced failure after one explicit function");
                createExact(targets.get(0));
                println("EXTERNAL_TABLE_GAP_BOUNDARIES_FORCED_AFTER_ONE_FAILURE entry="
                    + targets.get(0).entryText + " rollback_requested=true");
                throw new IntentionalProbeException(
                    "forced failure after one external-table gap function");
            }

            transaction = currentProgram.startTransaction(
                "Create 79 exact external-table gap function boundaries");
            for (Target target : targets) {
                createExact(target);
            }
            equal("transient Ghidra body instruction count",
                GHIDRA_BODY_INSTRUCTIONS, instructionCount(authorizedBodies));
            validatePostSnapshot(before, targets);
            validateInstructionDelta(instructionsBeforeSnapshot, authorizedBodies);
            validateReferenceDelta(referencesBeforeSnapshot, authorizedBodies);
            equal("transient function count", POST_FUNCTIONS,
                internalFunctionCount());
            if (POST_COUNTS_PINNED) {
                equal("transient instruction count", POST_INSTRUCTIONS,
                    programInstructionCount());
                equal("transient reference count", POST_REFERENCES,
                    referenceCount());
            } else {
                println("EXTERNAL_TABLE_GAP_EXPLORATORY_COUNTS instructions="
                    + programInstructionCount() + " references=" + referenceCount());
            }
            boolean commit = !mode.equals("probe-post-inner");
            boolean commitReturned = currentProgram.endTransaction(transaction, commit);
            ended = true;
            require(!commitReturned,
                "nested transaction unexpectedly finalized the outer script transaction");

            if (mode.equals("probe-post-inner")) {
                println("EXTERNAL_TABLE_GAP_BOUNDARIES_POST_INNER_ROLLBACK_REQUESTED "
                    + "targets=" + TARGET_COUNT
                    + " transaction_state_visible_until_outer_close=true"
                    + " separate_readback_required=true");
                println("EXTERNAL_TABLE_GAP_BOUNDARIES_FORCED_POST_INNER_FAILURE "
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
                Files.readAllBytes(manifest.toPath()), consumedProof,
                consumedProofBytes,
                output, ready, rows, functionsBefore, functionsAfter,
                instructionsBefore, instructionsAfter);
            println("EXTERNAL_TABLE_GAP_BOUNDARIES_OK mode=apply targets=" + TARGET_COUNT
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
            println("EXTERNAL_TABLE_GAP_BOUNDARIES_MUTATION_TAINTED mode=" + mode
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
            println("EXTERNAL_TABLE_GAP_BOUNDARIES_MUTATION_TAINTED mode=" + mode
                + " recovery=RESTORE_VERIFIED_SCRATCH_BASE error=" + clean(ex.toString()));
            throw ex;
        }
    }
}
