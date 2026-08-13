//@category Symbol
// SPDX-License-Identifier: GPL-3.0-or-later

import ghidra.app.script.GhidraScript;
import ghidra.framework.model.TransactionInfo;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.FunctionTagManager;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;
import ghidra.program.model.symbol.Symbol;

import java.io.File;
import java.io.InputStream;
import java.nio.channels.FileChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.nio.file.StandardOpenOption;
import java.security.MessageDigest;
import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.UUID;

/**
 * Target-specific metadata mutator for the 34 newly admitted MissionScript
 * handlers. Registry names are Tier-2 script-facing vocabulary, never asserted
 * original C++ symbols, ABI, runtime behavior, or reconstruction parity.
 *
 * <p>Exactly three function metadata surfaces may move: primary name, bounded
 * function comment, and function tag associations. Function boundaries,
 * instructions, bytes, ABI/signature source/storage, repeatable comments, and
 * every non-target function are validation invariants.</p>
 *
 * <p>The after-one probe relies on the still-open nested transaction rollback.
 * The post-inner probe deliberately ends the POST transaction, reconstructs
 * exact PRE metadata and the PRE function-tag catalog in a second transaction,
 * verifies that restoration, and only then forces failure.</p>
 *
 * <p>Usage: {@code <repository_root> <out.tsv> <out.ready.json>
 * <dry|probe-after-one|probe-post-inner|apply|readback>}</p>
 */
public class GhidraApplyMissionRegistryNewFunctionVocabulary extends GhidraScript {
    private static final String SCHEMA =
        "bea.ghidra.mission-registry-new-function-vocabulary.v1";
    private static final String PROGRAM_NAME = "BEA.exe";
    private static final String PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55";
    private static final String PROGRAM_SHA256 =
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
    private static final String IMAGE_BASE = "00400000";
    private static final String LANGUAGE = "x86:LE:32:default";
    private static final String COMPILER_SPEC = "windows";
    private static final long FUNCTION_COUNT = 8170;
    private static final long INSTRUCTION_COUNT = 549872;
    private static final String MEMORY_SHA256 =
        "5398f750f1ffb59873a6ec7e1750b51d11b5b844a8fda8d4e43649b5b9e5089d";
    private static final String INSTRUCTION_LAYOUT_SHA256 =
        "ba8b9d6380c2acb63f625b95d6a08d3ae4df209a9da0fa41ae4c13c86e3f4ba2";
    private static final int TARGET_COUNT = 34;
    private static final String REGISTRY_TAG = "script-command-registry";
    private static final String TIER2_TAG = "tier2-script-facing-name";
    private static final String EMPTY_TAGS_SENTINEL = "<EMPTY>";
    private static final int PRE_TAG_CATALOG_COUNT = 6854;
    private static final String PRE_TAG_CATALOG_SHA256 =
        "074dd7480aebfe46aabe5a48c1429348a814c9b51b0d71d985cbdac6e764603f";
    private static final String PRE_TAG_USAGE_SHA256 =
        "0ac85baaf38153328266bf4c54178f44ad871f273dabba03dfd13aaf4ded1a97";
    private static final int POST_TAG_CATALOG_COUNT = 6854;
    private static final String POST_TAG_CATALOG_SHA256 =
        "074dd7480aebfe46aabe5a48c1429348a814c9b51b0d71d985cbdac6e764603f";
    private static final String POST_TAG_USAGE_SHA256 =
        "0cbec4d3c190f2df8be5a3bd67ceeeaa419d3d5d9b20602b7ff9e400ade12971";
    private static final String MANIFEST_RELATIVE =
        "reverse-engineering/binary-analysis/" +
        "mission-script-registry-new-function-vocabulary-normalization-2026-08-13.tsv";
    private static final long MANIFEST_BYTES = 3417;
    private static final String MANIFEST_SHA256 =
        "6154fb4bd4ae398b02d783fb50cd18381c1d224e2ac4c6f9dc1d26abb4d1ddc1";
    private static final String META_RELATIVE =
        "reverse-engineering/binary-analysis/" +
        "mission-script-registry-new-function-vocabulary-normalization-pre-metadata-2026-08-13.tsv";
    private static final long META_BYTES = 8060;
    private static final String META_SHA256 =
        "cd4f6b4d4614870c12356ebce8702760d9e885e60eaf230ecd4316b06e61164f";
    private static final String OWNER_RELATIVE =
        "reverse-engineering/binary-analysis/" +
        "mission-script-registry-new-function-vocabulary-normalization-2026-08-13.md";
    private static final long OWNER_BYTES = 7412;
    private static final String OWNER_SHA256 =
        "b9f03fd35b57cbc054b35851ec5d442bd5c30a2b403047bd99d36e1771c621f1";
    private static final String STATIC_RELATIVE =
        "reverse-engineering/binary-analysis/" +
        "mission-script-registry-new-function-static-contracts-2026-08-13.tsv";
    private static final long STATIC_BYTES = 21608;
    private static final String STATIC_SHA256 =
        "86c0c4a0e0d5fe0078cb21f271b4985cb1c4fe89aa035b66215076dfbe784a31";
    private static final String CANONICAL_PROJECTION_SHA256 =
        "cc769cb0b83aec0105d365e77f0702adcc1024914453b0f5615c8d7d1b333ce9";
    private static final String EMPTY_SHA256 =
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";

    private static final String MANIFEST_HEADER =
        "index\tcommand\thandlerVa\tregistryRecordVa\tcohort\texpectedPreName\t" +
        "proposedName\texpectedNameSource";
    private static final String META_HEADER =
        "handlerVa\tpreCommentPresent\tpreCommentLen\tpreCommentSha256\t" +
        "preRepeatableCommentPresent\tpreRepeatableCommentLen\t" +
        "preRepeatableCommentSha256\tpreTagCount\tpreTagsSha256\tpreTags";
    private static final String STATIC_HEADER =
        "registryIndex\tcommand\tentry\tlabelRelation\tsourceCoordinatePlates\t" +
        "crossBuildCoordinate\tstaticContract\tvisibleFailureOrNoOp\t" +
        "remainingUnknown\tcheapestFalsifier\tgrade\tevidenceClass";

    private static class PreMeta {
        String entry;
        boolean commentPresent;
        int commentLength;
        String commentSha256;
        boolean repeatablePresent;
        int repeatableLength;
        String repeatableSha256;
        int tagCount;
        String tagsSha256;
        List<String> tags;
    }

    private static class Target {
        int index;
        String command;
        String entry;
        Address address;
        String record;
        String cohort;
        String preName;
        String postName;
        SourceType preNameSource;
        PreMeta meta;
        String labelRelation;
        String staticContract;
        String visibleFailure;
        String remainingUnknown;
        String cheapestFalsifier;
        String grade;
        String evidenceClass;
    }

    private static class StaticMeta {
        int index;
        String command;
        String entry;
        String labelRelation;
        String staticContract;
        String visibleFailure;
        String remainingUnknown;
        String cheapestFalsifier;
        String grade;
        String evidenceClass;
    }

    private static class PreState {
        String name;
        SourceType nameSource;
        boolean commentPresent;
        String comment;
        List<String> tags;
        String invariant;
        String abi;
    }

    private static void require(boolean value, String message) {
        if (!value) throw new IllegalStateException(message);
    }

    private static void equal(String owner, String field, Object expected, Object actual) {
        if (expected == null ? actual != null : !expected.equals(actual)) {
            throw new IllegalStateException(owner + " " + field + " expected=" + expected +
                " actual=" + actual);
        }
    }

    private static String hex(byte[] bytes) {
        StringBuilder result = new StringBuilder(bytes.length * 2);
        for (byte value : bytes) result.append(String.format("%02x", value & 0xff));
        return result.toString();
    }

    private static String sha256(byte[] bytes) throws Exception {
        return hex(MessageDigest.getInstance("SHA-256").digest(bytes));
    }

    private static String sha256(String value) throws Exception {
        return sha256(value.getBytes(StandardCharsets.UTF_8));
    }

    private static String nullable(String value) {
        return value == null ? "" : value;
    }

    private static String clean(String value) {
        return nullable(value).replace("\\", "\\\\").replace("\r", "\\r")
            .replace("\n", "\\n").replace("\t", "\\t");
    }

    private static String json(String value) {
        return clean(value).replace("\"", "\\\"");
    }

    private static File requirePinned(File root, String relative, long bytes,
            String digest) throws Exception {
        File file = new File(root, relative).getCanonicalFile();
        require(file.isFile(), "pinned input absent: " + file);
        byte[] value = Files.readAllBytes(file.toPath());
        equal(relative, "bytes", bytes, (long) value.length);
        equal(relative, "SHA-256", digest, sha256(value));
        require(value.length > 0 && value[value.length - 1] == '\n',
            relative + " must end in LF");
        for (byte b : value) require(b != '\r', relative + " contains CR");
        return file;
    }

    private static List<String[]> readTsv(File file, String header) throws Exception {
        List<String> lines = Files.readAllLines(file.toPath(), StandardCharsets.UTF_8);
        require(!lines.isEmpty(), "empty TSV: " + file);
        equal(file.getName(), "header", header, lines.get(0));
        List<String[]> result = new ArrayList<>();
        for (int i = 1; i < lines.size(); i++) {
            require(!lines.get(i).isEmpty(), "blank TSV row " + (i + 1));
            result.add(lines.get(i).split("\\t", -1));
        }
        return result;
    }

    private static int integer(String value, String label) {
        try { return Integer.parseInt(value); }
        catch (NumberFormatException error) { throw new IllegalStateException("bad " + label); }
    }

    private static boolean bool(String value, String label) {
        require(value.equals("true") || value.equals("false"), "bad " + label);
        return Boolean.parseBoolean(value);
    }

    private Address address(String text) {
        Address result = toAddr(text);
        require(result != null, "invalid address: " + text);
        return result;
    }

    private List<Target> loadTargets(File root) throws Exception {
        File manifest = requirePinned(root, MANIFEST_RELATIVE, MANIFEST_BYTES, MANIFEST_SHA256);
        File metadata = requirePinned(root, META_RELATIVE, META_BYTES, META_SHA256);
        File staticRows = requirePinned(root, STATIC_RELATIVE, STATIC_BYTES, STATIC_SHA256);
        requirePinned(root, OWNER_RELATIVE, OWNER_BYTES, OWNER_SHA256);
        Map<String, StaticMeta> contracts = new LinkedHashMap<>();
        for (String[] row : readTsv(staticRows, STATIC_HEADER)) {
            equal("static contracts", "columns", 12, row.length);
            StaticMeta contract = new StaticMeta();
            contract.index = integer(row[0], "static registry index");
            contract.command = row[1];
            contract.entry = row[2];
            contract.labelRelation = row[3];
            contract.staticContract = row[6];
            contract.visibleFailure = row[7];
            contract.remainingUnknown = row[8];
            contract.cheapestFalsifier = row[9];
            contract.grade = row[10];
            contract.evidenceClass = row[11];
            require(contract.labelRelation.equals("CONSISTENT") ||
                contract.labelRelation.equals("BROADER"),
                "unreviewed label relation: " + contract.entry);
            equal(contract.entry, "static grade", "C1_CANDIDATE_PARTIAL", contract.grade);
            equal(contract.entry, "static evidence class", "STATIC_HYPOTHESIS_ONLY",
                contract.evidenceClass);
            require(contracts.put(contract.entry.toLowerCase(Locale.ROOT), contract) == null,
                "duplicate static contract: " + contract.entry);
        }
        Map<String, PreMeta> metas = new LinkedHashMap<>();
        for (String[] row : readTsv(metadata, META_HEADER)) {
            equal("PRE metadata", "columns", 10, row.length);
            PreMeta meta = new PreMeta();
            meta.entry = row[0];
            meta.commentPresent = bool(row[1], "comment presence");
            meta.commentLength = integer(row[2], "comment length");
            meta.commentSha256 = row[3];
            meta.repeatablePresent = bool(row[4], "repeatable presence");
            meta.repeatableLength = integer(row[5], "repeatable length");
            meta.repeatableSha256 = row[6];
            meta.tagCount = integer(row[7], "tag count");
            meta.tagsSha256 = row[8];
            require(!row[9].isEmpty(),
                "PRE tag field must use explicit empty sentinel: " + meta.entry);
            meta.tags = row[9].equals(EMPTY_TAGS_SENTINEL) ? new ArrayList<>() :
                new ArrayList<>(Arrays.asList(row[9].split(",", -1)));
            require(!meta.tags.contains(EMPTY_TAGS_SENTINEL),
                "PRE tag sentinel cannot be a tag name: " + meta.entry);
            equal(meta.entry, "empty-tag sentinel",
                meta.tagCount == 0, row[9].equals(EMPTY_TAGS_SENTINEL));
            List<String> sorted = new ArrayList<>(meta.tags);
            Collections.sort(sorted);
            equal(meta.entry, "sorted PRE tags", sorted, meta.tags);
            equal(meta.entry, "tag count", meta.tagCount, meta.tags.size());
            equal(meta.entry, "tag digest", meta.tagsSha256, sortedDigest(meta.tags));
            if (!meta.commentPresent) {
                equal(meta.entry, "absent comment length", 0, meta.commentLength);
                equal(meta.entry, "absent comment digest", EMPTY_SHA256, meta.commentSha256);
            }
            require(metas.put(meta.entry.toLowerCase(Locale.ROOT), meta) == null,
                "duplicate PRE metadata: " + meta.entry);
        }

        List<Target> targets = new ArrayList<>();
        Set<Integer> indices = new HashSet<>();
        Set<String> entries = new HashSet<>();
        Set<String> postNames = new HashSet<>();
        StringBuilder canonical = new StringBuilder();
        int priorIndex = -1;
        for (String[] row : readTsv(manifest, MANIFEST_HEADER)) {
            equal("manifest", "columns", 8, row.length);
            Target target = new Target();
            target.index = integer(row[0], "registry index");
            target.command = row[1];
            target.entry = row[2];
            target.address = address(target.entry);
            target.record = row[3];
            target.cohort = row[4];
            target.preName = row[5];
            target.postName = row[6];
            target.preNameSource = SourceType.valueOf(row[7]);
            require(target.index > priorIndex, "manifest is not index-sorted");
            priorIndex = target.index;
            require(indices.add(target.index), "duplicate index " + target.index);
            require(entries.add(target.entry.toLowerCase(Locale.ROOT)),
                "duplicate handler " + target.entry);
            require(postNames.add(target.postName), "duplicate proposed name " + target.postName);
            equal(target.entry, "proposed name", "IScript__" + target.command, target.postName);
            equal(target.entry, "registry record",
                String.format("0x%08x", 0x0064CE20L + 0x40L * target.index), target.record);
            equal(target.entry, "cohort", "NEW34_STATIC_C1", target.cohort);
            require(target.preName.matches("FUN_[0-9a-f]{8}"),
                "new function must start from FUN_*: " + target.entry);
            equal(target.entry, "default name source", SourceType.DEFAULT, target.preNameSource);
            target.meta = metas.get(target.entry.toLowerCase(Locale.ROOT));
            require(target.meta != null, "missing PRE metadata: " + target.entry);
            StaticMeta contract = contracts.get(target.entry.toLowerCase(Locale.ROOT));
            require(contract != null, "missing static contract: " + target.entry);
            equal(target.entry, "contract index", target.index, contract.index);
            equal(target.entry, "contract command", target.command, contract.command);
            target.labelRelation = contract.labelRelation;
            target.staticContract = contract.staticContract;
            target.visibleFailure = contract.visibleFailure;
            target.remainingUnknown = contract.remainingUnknown;
            target.cheapestFalsifier = contract.cheapestFalsifier;
            target.grade = contract.grade;
            target.evidenceClass = contract.evidenceClass;
            canonical.append(target.index).append('\t').append(target.entry).append('\t')
                .append(target.preName).append('\t').append(target.postName).append('\n');
            targets.add(target);
        }
        equal("manifest", "targets", TARGET_COUNT, targets.size());
        equal("PRE metadata", "targets", TARGET_COUNT, metas.size());
        equal("static contracts", "targets", TARGET_COUNT, contracts.size());
        equal("manifest", "canonical projection", CANONICAL_PROJECTION_SHA256,
            sha256(canonical.toString()));
        return targets;
    }

    private void validateProgram() throws Exception {
        equal("program", "name", PROGRAM_NAME, currentProgram.getName());
        equal("program", "MD5", PROGRAM_MD5,
            currentProgram.getExecutableMD5().toLowerCase(Locale.ROOT));
        equal("program", "SHA-256", PROGRAM_SHA256,
            currentProgram.getExecutableSHA256().toLowerCase(Locale.ROOT));
        equal("program", "image base", IMAGE_BASE, currentProgram.getImageBase().toString());
        equal("program", "language", LANGUAGE, currentProgram.getLanguageID().toString());
        equal("program", "compiler", COMPILER_SPEC,
            currentProgram.getCompilerSpec().getCompilerSpecID().toString());
        long functions = 0;
        FunctionIterator functionIterator =
            currentProgram.getFunctionManager().getFunctions(true);
        while (functionIterator.hasNext()) { functionIterator.next(); functions++; }
        equal("program", "internal functions", FUNCTION_COUNT, functions);
        long instructions = 0;
        InstructionIterator instructionIterator = currentProgram.getListing().getInstructions(true);
        while (instructionIterator.hasNext()) { instructionIterator.next(); instructions++; }
        equal("program", "instructions", INSTRUCTION_COUNT, instructions);
        equal("program", "memory SHA-256", MEMORY_SHA256, memorySha256());
        equal("program", "instruction layout SHA-256", INSTRUCTION_LAYOUT_SHA256,
            instructionLayoutSha256());
    }

    private String memorySha256() throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        Memory memory = currentProgram.getMemory();
        List<MemoryBlock> blocks = new ArrayList<>(Arrays.asList(memory.getBlocks()));
        blocks.sort(Comparator.comparing(MemoryBlock::getStart)
            .thenComparing(MemoryBlock::getEnd).thenComparing(MemoryBlock::getName));
        for (MemoryBlock block : blocks) {
            String source = block.getSourceName();
            String comment = block.getComment();
            digestString(digest, block.getName().length() + ":" + sha256(block.getName()) +
                "\t" + (source == null ? -1 : source.length()) + ":" +
                sha256(nullable(source)) + "\t" +
                (comment == null ? -1 : comment.length()) + ":" +
                sha256(nullable(comment)) + "\t" + block.getStart() + "\t" +
                block.getEnd() + "\t" + block.getSize() + "\t" +
                block.isInitialized() + "\t" + block.isRead() + "\t" +
                block.isWrite() + "\t" + block.isExecute() + "\t" +
                block.isVolatile() + "\t" + block.isArtificial() + "\t" +
                block.isMapped() + "\t" + block.isOverlay() + "\t" +
                block.isLoaded() + "\t" + block.getType());
            if (!block.isInitialized()) continue;
            Address cursor = block.getStart();
            long remaining = block.getSize();
            while (remaining > 0) {
                int amount = (int) Math.min(1024 * 1024L, remaining);
                byte[] buffer = new byte[amount];
                int read = memory.getBytes(cursor, buffer);
                equal(block.getName(), "memory read", amount, read);
                digest.update(buffer);
                cursor = cursor.add(read);
                remaining -= read;
            }
        }
        return hex(digest.digest());
    }

    private static void digestString(MessageDigest digest, String value) {
        byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
        digest.update((byte) ((bytes.length >>> 24) & 0xff));
        digest.update((byte) ((bytes.length >>> 16) & 0xff));
        digest.update((byte) ((bytes.length >>> 8) & 0xff));
        digest.update((byte) (bytes.length & 0xff));
        digest.update(bytes);
    }

    private static String sortedDigest(List<String> rows) throws Exception {
        List<String> sorted = new ArrayList<>(rows);
        Collections.sort(sorted);
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        for (String row : sorted) digestString(digest, row);
        return hex(digest.digest());
    }

    private String instructionLayoutSha256() throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        InstructionIterator iterator = currentProgram.getListing().getInstructions(true);
        while (iterator.hasNext()) {
            monitor.checkCancelled();
            Instruction instruction = iterator.next();
            digestString(digest, instruction.getAddress().toString());
            digestString(digest, Integer.toString(instruction.getLength()));
            digest.update(instruction.getBytes());
            digestString(digest, instruction.getMnemonicString());
            digestString(digest, instruction.getFlowType().toString());
            digestString(digest, String.valueOf(instruction.getFallThrough()));
            digestString(digest, Arrays.toString(instruction.getFlows()));
            digestString(digest, instruction.getFlowOverride().toString());
            digestString(digest, Boolean.toString(instruction.isLengthOverridden()));
        }
        return hex(digest.digest());
    }

    private Function exact(Target target) {
        Function result = currentProgram.getFunctionManager().getFunctionAt(target.address);
        require(result != null && result.getEntryPoint().equals(target.address),
            "missing exact function: " + target.entry);
        return result;
    }

    private List<String> tags(Function function) {
        List<String> result = new ArrayList<>();
        for (FunctionTag tag : function.getTags()) result.add(tag.getName());
        Collections.sort(result);
        return result;
    }

    private List<String> tagDefinitions() {
        FunctionTagManager manager =
            currentProgram.getFunctionManager().getFunctionTagManager();
        List<String> result = new ArrayList<>();
        for (FunctionTag tag : manager.getAllFunctionTags()) {
            String comment = tag.getComment();
            result.add(tag.getName() + "\u0000" + (comment != null) + "\u0000" +
                nullable(comment));
        }
        Collections.sort(result);
        return result;
    }

    private List<String> tagUsage() {
        FunctionTagManager manager =
            currentProgram.getFunctionManager().getFunctionTagManager();
        List<String> result = new ArrayList<>();
        for (FunctionTag tag : manager.getAllFunctionTags()) {
            result.add(tag.getName() + "\u0000" + manager.getUseCount(tag));
        }
        Collections.sort(result);
        return result;
    }

    private void validateTagCatalog(boolean post) throws Exception {
        FunctionTagManager manager =
            currentProgram.getFunctionManager().getFunctionTagManager();
        List<String> definitions = tagDefinitions();
        List<String> usage = tagUsage();
        equal("tag catalog", "count", post ? POST_TAG_CATALOG_COUNT :
            PRE_TAG_CATALOG_COUNT, definitions.size());
        equal("tag catalog", "definitions SHA-256", post ? POST_TAG_CATALOG_SHA256 :
            PRE_TAG_CATALOG_SHA256, sortedDigest(definitions));
        equal("tag catalog", "usage SHA-256", post ? POST_TAG_USAGE_SHA256 :
            PRE_TAG_USAGE_SHA256, sortedDigest(usage));
        FunctionTag registry = manager.getFunctionTag(REGISTRY_TAG);
        require(registry != null, "registry tag definition is absent");
        equal("tag catalog", "registry definition comment", "",
            nullable(registry.getComment()));
        FunctionTag tier2 = manager.getFunctionTag(TIER2_TAG);
        require(tier2 != null, "Tier-2 tag definition is absent");
        equal("tag catalog", "Tier-2 definition comment", "",
            nullable(tier2.getComment()));
        equal("tag catalog", "registry use count", post ? 128 : 94,
            manager.getUseCount(registry));
        equal("tag catalog", "Tier-2 use count", post ? 109 : 75,
            manager.getUseCount(tier2));
    }

    private List<String> postTags(Target target) {
        Set<String> result = new HashSet<>(target.meta.tags);
        result.add(REGISTRY_TAG);
        result.add(TIER2_TAG);
        List<String> sorted = new ArrayList<>(result);
        Collections.sort(sorted);
        return sorted;
    }

    private String postComment(Target target) {
        return "Mission registry vocabulary: slot " + target.index + " (record " +
            target.record + ") registers this handler as `" + target.command +
            "`. The promoted `" + target.postName + "` name is Tier 2 script-facing " +
            "vocabulary under the project naming convention, not a recovered C++ symbol or " +
            "evidence of this handler's ABI, runtime behavior, or complete semantics.\n\n" +
            "Static envelope (`" + target.grade + "` / `" + target.evidenceClass + "`; " +
            "registry-label relation `" + target.labelRelation + "`): " +
            target.staticContract + "\n\nVisible failure/no-op boundary: " +
            target.visibleFailure + "\n\nRemaining unknowns: " + target.remainingUnknown +
            "\n\nCheapest falsifier: " + target.cheapestFalsifier +
            " No runtime reachability, causal behavior, source equivalence, or " +
            "reconstruction parity is admitted by this metadata promotion.";
    }

    private String abiKey(Function function) {
        StringBuilder result = new StringBuilder();
        result.append("sigSource=").append(function.getSignatureSource());
        result.append("|cc=").append(function.getCallingConventionName());
        result.append("|custom=").append(function.hasCustomVariableStorage());
        result.append("|varargs=").append(function.hasVarArgs());
        result.append("|noreturn=").append(function.hasNoReturn());
        result.append("|return=").append(function.getReturn().getDataType().getPathName());
        result.append('@').append(function.getReturn().getVariableStorage());
        result.append("|params=");
        Parameter[] parameters = function.getParameters();
        for (int i = 0; i < parameters.length; i++) {
            if (i > 0) result.append(';');
            Parameter parameter = parameters[i];
            result.append(parameter.getOrdinal()).append(':').append(parameter.getName())
                .append(':').append(parameter.getDataType().getPathName()).append('@')
                .append(parameter.getVariableStorage()).append(':').append(parameter.getSource());
        }
        result.append("|purge=").append(function.getStackPurgeSize());
        result.append("|frame=").append(function.getStackFrame().getFrameSize());
        result.append("|local=").append(function.getStackFrame().getLocalSize());
        result.append("|param=").append(function.getStackFrame().getParameterSize());
        return result.toString();
    }

    private String invariantKey(Function function) throws Exception {
        AddressSetView body = function.getBody();
        StringBuilder ranges = new StringBuilder();
        MessageDigest bytes = MessageDigest.getInstance("SHA-256");
        long instructions = 0;
        for (AddressRange range : body) {
            if (ranges.length() > 0) ranges.append(',');
            ranges.append(range.getMinAddress()).append('-').append(range.getMaxAddress());
            Address cursor = range.getMinAddress();
            long remaining = range.getLength();
            while (remaining > 0) {
                int amount = (int) Math.min(1024 * 1024L, remaining);
                byte[] chunk = new byte[amount];
                int read = currentProgram.getMemory().getBytes(cursor, chunk);
                equal(function.getName(), "body read", amount, read);
                bytes.update(chunk);
                cursor = cursor.add(read);
                remaining -= read;
            }
        }
        InstructionIterator iterator = currentProgram.getListing().getInstructions(body, true);
        while (iterator.hasNext()) { iterator.next(); instructions++; }
        return body.getNumAddresses() + "|" + ranges + "|" + hex(bytes.digest()) + "|" +
            instructions + "|thunk=" + function.isThunk() + "|target=" +
            (function.getThunkedFunction(false) == null ? "" :
                function.getThunkedFunction(false).getEntryPoint()) + "|external=" +
            function.isExternal() + "|inline=" + function.isInline();
    }

    private void validateMeta(Target target, Function function) throws Exception {
        String comment = nullable(function.getComment());
        equal(target.entry, "PRE comment present", target.meta.commentPresent,
            function.getComment() != null);
        equal(target.entry, "PRE comment length", target.meta.commentLength, comment.length());
        equal(target.entry, "PRE comment SHA-256", target.meta.commentSha256, sha256(comment));
        String repeatable = nullable(function.getRepeatableComment());
        equal(target.entry, "repeatable present", target.meta.repeatablePresent,
            function.getRepeatableComment() != null);
        equal(target.entry, "repeatable length", target.meta.repeatableLength,
            repeatable.length());
        equal(target.entry, "repeatable SHA-256", target.meta.repeatableSha256,
            sha256(repeatable));
        equal(target.entry, "PRE tags", target.meta.tags, tags(function));
    }

    private void validateNoCollision(Target target) {
        for (Symbol symbol : currentProgram.getSymbolTable().getAllSymbols(true)) {
            require(!symbol.getName().equals(target.postName),
                "proposed-name collision: " + target.postName + " at " + symbol.getAddress());
        }
    }

    private PreState validatePre(Target target) throws Exception {
        Function function = exact(target);
        require(!function.isThunk(), "target is thunk: " + target.entry);
        equal(target.entry, "PRE name", target.preName, function.getName());
        equal(target.entry, "PRE name source", target.preNameSource,
            function.getSymbol().getSource());
        validateMeta(target, function);
        validateNoCollision(target);
        PreState result = new PreState();
        result.name = function.getName();
        result.nameSource = function.getSymbol().getSource();
        result.commentPresent = function.getComment() != null;
        result.comment = nullable(function.getComment());
        result.tags = tags(function);
        result.invariant = invariantKey(function);
        result.abi = abiKey(function);
        return result;
    }

    private void validatePost(Target target) throws Exception {
        Function function = exact(target);
        require(!function.isThunk(), "POST target is thunk: " + target.entry);
        equal(target.entry, "POST name", target.postName, function.getName());
        equal(target.entry, "POST name source", SourceType.USER_DEFINED,
            function.getSymbol().getSource());
        equal(target.entry, "POST comment", postComment(target),
            nullable(function.getComment()));
        equal(target.entry, "POST tags", postTags(target), tags(function));
        String repeatable = nullable(function.getRepeatableComment());
        equal(target.entry, "POST repeatable present", target.meta.repeatablePresent,
            function.getRepeatableComment() != null);
        equal(target.entry, "POST repeatable length", target.meta.repeatableLength,
            repeatable.length());
        equal(target.entry, "POST repeatable SHA-256", target.meta.repeatableSha256,
            sha256(repeatable));
    }

    private void mutate(Target target, PreState pre) throws Exception {
        Function function = exact(target);
        function.setName(target.postName, SourceType.USER_DEFINED);
        function.setComment(postComment(target));
        List<String> expectedTags = postTags(target);
        for (String tag : tags(function)) {
            if (!expectedTags.contains(tag)) function.removeTag(tag);
        }
        for (String tag : expectedTags) {
            if (!tags(function).contains(tag)) require(function.addTag(tag),
                "failed to add tag " + tag + " at " + target.entry);
        }
        validatePost(target);
        equal(target.entry, "body/instruction invariant", pre.invariant, invariantKey(function));
        equal(target.entry, "ABI/storage invariant", pre.abi, abiKey(function));
    }

    private void setTags(Function function, List<String> expected) {
        for (String existing : tags(function)) function.removeTag(existing);
        for (String name : expected) require(function.addTag(name),
            "failed to restore tag " + name + " at " + function.getEntryPoint());
        equal(function.getEntryPoint().toString(), "restored tags", expected, tags(function));
    }

    private void restorePre(Target target, PreState pre) throws Exception {
        Function function = exact(target);
        equal(target.entry, "restore POST name", target.postName, function.getName());
        function.setName(pre.name, pre.nameSource);
        function.setComment(pre.commentPresent ? pre.comment : null);
        setTags(function, pre.tags);
        PreState restored = validatePre(target);
        equal(target.entry, "restored body/instruction invariant", pre.invariant,
            restored.invariant);
        equal(target.entry, "restored ABI/storage invariant", pre.abi, restored.abi);
    }

    private static File newOutput(String value, String label) throws Exception {
        File file = new File(value).getCanonicalFile();
        require(!file.exists(), label + " already exists: " + file);
        require(file.getParentFile() != null && file.getParentFile().isDirectory(),
            label + " parent absent: " + file);
        return file;
    }

    private static String repositoryRelative(File repositoryRoot, File file)
            throws Exception {
        java.nio.file.Path root = repositoryRoot.getCanonicalFile().toPath();
        java.nio.file.Path target = file.getCanonicalFile().toPath();
        require(target.startsWith(root), "path is outside supplied repository root: " + target);
        return root.relativize(target).toString().replace(File.separatorChar, '/');
    }

    private static File stage(File output, byte[] bytes) throws Exception {
        File partial = new File(output.getParentFile(), "." + output.getName() +
            ".partial-" + UUID.randomUUID());
        Files.write(partial.toPath(), bytes, StandardOpenOption.CREATE_NEW,
            StandardOpenOption.WRITE);
        try (FileChannel channel = FileChannel.open(partial.toPath(), StandardOpenOption.WRITE)) {
            channel.force(true);
        }
        return partial;
    }

    private static void publishPair(File output, byte[] outputBytes, File ready,
            byte[] readyBytes) throws Exception {
        File a = stage(output, outputBytes), b = stage(ready, readyBytes);
        try {
            Files.move(a.toPath(), output.toPath(), StandardCopyOption.ATOMIC_MOVE);
            a = null;
            Files.move(b.toPath(), ready.toPath(), StandardCopyOption.ATOMIC_MOVE);
            b = null;
        } finally {
            if (a != null) Files.deleteIfExists(a.toPath());
            if (b != null) Files.deleteIfExists(b.toPath());
        }
    }

    private byte[] output(String mode, String state, List<Target> targets) throws Exception {
        StringBuilder result = new StringBuilder();
        result.append("index\thandlerVa\tcohort\tmode\tstate\tname\tnameSource\t")
            .append("invariantSha256\tabiSha256\tcommentLen\tcommentSha256\t")
            .append("repeatableCommentSha256\ttagCount\ttagsSha256\ttags\n");
        for (Target target : targets) {
            Function function = exact(target);
            String comment = nullable(function.getComment());
            List<String> tagNames = tags(function);
            result.append(target.index).append('\t').append(target.entry).append('\t')
                .append(target.cohort).append('\t').append(mode).append('\t').append(state)
                .append('\t').append(function.getName()).append('\t')
                .append(function.getSymbol().getSource()).append('\t')
                .append(sha256(invariantKey(function))).append('\t')
                .append(sha256(abiKey(function))).append('\t').append(comment.length())
                .append('\t').append(sha256(comment)).append('\t')
                .append(sha256(nullable(function.getRepeatableComment()))).append('\t')
                .append(tagNames.size()).append('\t')
                .append(sha256(String.join(",", tagNames))).append('\t')
                .append(String.join(",", tagNames)).append('\n');
        }
        return result.toString().getBytes(StandardCharsets.UTF_8);
    }

    private byte[] ready(String mode, String state, String toolRelative, byte[] toolBytes,
            String outputRelative, byte[] outputBytes,
            boolean commitRequested, boolean nestedCommitted) throws Exception {
        String value = "{\n" +
            "  \"schema\": \"" + SCHEMA + "\",\n" +
            "  \"completedAtUtc\": \"" + Instant.now() + "\",\n" +
            "  \"mode\": \"" + mode + "\",\n" +
            "  \"state\": \"" + state + "\",\n" +
            "  \"tool\": {\"path\": \"" + json(toolRelative) +
                "\", \"bytes\": " + toolBytes.length + ", \"sha256\": \"" +
                sha256(toolBytes) + "\"},\n" +
            "  \"manifest\": {\"path\": \"" + MANIFEST_RELATIVE +
                "\", \"bytes\": " + MANIFEST_BYTES + ", \"sha256\": \"" +
                MANIFEST_SHA256 + "\"},\n" +
            "  \"preMetadata\": {\"path\": \"" + META_RELATIVE +
                "\", \"bytes\": " + META_BYTES + ", \"sha256\": \"" +
                META_SHA256 + "\"},\n" +
            "  \"staticContracts\": {\"path\": \"" + STATIC_RELATIVE +
                "\", \"bytes\": " + STATIC_BYTES + ", \"sha256\": \"" +
                STATIC_SHA256 + "\"},\n" +
            "  \"owner\": {\"path\": \"" + OWNER_RELATIVE +
                "\", \"bytes\": " + OWNER_BYTES + ", \"sha256\": \"" +
                OWNER_SHA256 + "\"},\n" +
            "  \"program\": {\"name\": \"" + PROGRAM_NAME +
                "\", \"md5\": \"" + PROGRAM_MD5 + "\", \"sha256\": \"" +
                PROGRAM_SHA256 + "\", \"functions\": " + FUNCTION_COUNT +
                ", \"instructions\": " + INSTRUCTION_COUNT + "},\n" +
            "  \"targets\": {\"total\": 34, \"NEW34_STATIC_C1\": 34},\n" +
            "  \"tagCatalog\": {\"count\": " +
                (state.equals("POST") ? POST_TAG_CATALOG_COUNT : PRE_TAG_CATALOG_COUNT) +
                ", \"definitionsSha256\": \"" +
                (state.equals("POST") ? POST_TAG_CATALOG_SHA256 : PRE_TAG_CATALOG_SHA256) +
                "\", \"usageSha256\": \"" +
                (state.equals("POST") ? POST_TAG_USAGE_SHA256 : PRE_TAG_USAGE_SHA256) +
                "\"},\n" +
            "  \"mutation\": {\"namesChanged\": 34, \"commentsChanged\": 34, " +
                "\"newFunctionComments\": 34, \"tagAssociationsAdded\": 68, " +
                "\"tagAssociationsRemoved\": 0, \"tagDefinitionsAdded\": 0, " +
                "\"boundariesChanged\": 0, \"abiChanged\": 0, \"bytesChanged\": 0, " +
                "\"instructionsChanged\": 0, \"referencesChanged\": 0},\n" +
            "  \"output\": {\"path\": \"" + json(outputRelative) +
                "\", \"bytes\": " + outputBytes.length + ", \"sha256\": \"" +
                sha256(outputBytes) + "\"},\n" +
            "  \"commitRequested\": " + commitRequested + ",\n" +
            "  \"nestedEndReturnedCommitted\": " + nestedCommitted + ",\n" +
            "  \"loadedStateVerified\": " + mode.equals("readback") + ",\n" +
            "  \"registryNamesAreOriginalCppSymbols\": false,\n" +
            "  \"runtimeBehaviorAuthorized\": false,\n" +
            "  \"reconstructionParityAuthorized\": false,\n" +
            "  \"liveMutationAuthorized\": false\n" +
            "}\n";
        return value.getBytes(StandardCharsets.UTF_8);
    }

    private void validateOuter(long expectedId, String phase) {
        TransactionInfo info = currentProgram.getCurrentTransactionInfo();
        require(info != null, phase + " outer transaction is absent");
        equal("transaction", phase + " id", expectedId, info.getID());
        equal("transaction", phase + " status", TransactionInfo.Status.NOT_DONE,
            info.getStatus());
        equal("transaction", phase + " terminated", false,
            currentProgram.hasTerminatedTransaction());
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        require(args != null && args.length == 4,
            "usage: <repository_root> <out.tsv> <out.ready.json> " +
            "<dry|probe-after-one|probe-post-inner|apply|readback>");
        String mode = args[3].toLowerCase(Locale.ROOT);
        require(Arrays.asList("dry", "probe-after-one", "probe-post-inner", "apply", "readback")
            .contains(mode), "invalid mode: " + mode);
        File root = new File(args[0]).getCanonicalFile();
        require(root.isDirectory(), "repository root absent: " + root);
        File tool = new File(getSourceFile().getCanonicalPath()).getCanonicalFile();
        require(tool.getParentFile().equals(new File(root, "tools").getCanonicalFile()),
            "tool is not under supplied repository root");
        File out = newOutput(args[1], "TSV output");
        File receipt = newOutput(args[2], "READY output");
        String toolRelative = repositoryRelative(root, tool);
        String outputRelative = repositoryRelative(root, out);
        String readyRelative = repositoryRelative(root, receipt);
        equal("tool", "repository-relative path",
            "tools/GhidraApplyMissionRegistryNewFunctionVocabulary.java", toolRelative);
        require(!out.equals(receipt) && out.getParentFile().equals(receipt.getParentFile()),
            "output paths must be distinct siblings");
        require(!outputRelative.equals(readyRelative),
            "repository-relative output paths must differ");
        File manifest = new File(root, MANIFEST_RELATIVE).getCanonicalFile();
        File metadata = new File(root, META_RELATIVE).getCanonicalFile();
        File owner = new File(root, OWNER_RELATIVE).getCanonicalFile();
        List<Target> targets = loadTargets(root);
        validateProgram();
        byte[] toolBytes;
        try (InputStream stream = getSourceFile().getInputStream()) {
            toolBytes = stream.readAllBytes();
        }

        if (mode.equals("readback")) {
            for (Target target : targets) validatePost(target);
            validateTagCatalog(true);
            byte[] output = output(mode, "POST", targets);
            publishPair(out, output, receipt, ready(mode, "POST", toolRelative, toolBytes,
                outputRelative, output, false, false));
            println("MISSION_REGISTRY_NEW_FUNCTION_VOCABULARY_READBACK_COMPLETE targets=34 " +
                "loaded_state_verified=true");
            return;
        }

        List<PreState> pre = new ArrayList<>();
        for (Target target : targets) pre.add(validatePre(target));
        validateTagCatalog(false);
        println("MISSION_REGISTRY_NEW_FUNCTION_VOCABULARY_PREFLIGHT_OK targets=34 " +
            "functions=8170 " +
            "canonical_projection=" + CANONICAL_PROJECTION_SHA256);
        if (mode.equals("dry")) {
            byte[] output = output(mode, "PRE", targets);
            publishPair(out, output, receipt, ready(mode, "PRE", toolRelative, toolBytes,
                outputRelative, output, false, false));
            println("MISSION_REGISTRY_NEW_FUNCTION_VOCABULARY_DRY_COMPLETE " +
                "targets=34 mutations=0");
            return;
        }

        TransactionInfo outer = currentProgram.getCurrentTransactionInfo();
        require(outer != null && !currentProgram.hasTerminatedTransaction(),
            "mutation requires healthy outer transaction");
        long outerId = outer.getID();
        validateOuter(outerId, "before mutation");
        int transaction = currentProgram.startTransaction(
            "Normalize 34 new MissionScript registry-facing names");
        boolean ended = false, requested = false, nestedCommitted = false;
        boolean compensatingPreRestored = false;
        try {
            int limit = mode.equals("probe-after-one") ? 1 : targets.size();
            for (int i = 0; i < limit; i++) {
                monitor.checkCancelled();
                mutate(targets.get(i), pre.get(i));
            }
            if (mode.equals("probe-after-one")) {
                println("MISSION_REGISTRY_NEW_FUNCTION_VOCABULARY_FORCED_AFTER_ONE_FAILURE " +
                    "outer_rollback_required=true");
                throw new IllegalStateException("intentional after-one rollback probe");
            }
            validateTagCatalog(true);
            requested = true;
            nestedCommitted = currentProgram.endTransaction(transaction, true);
            ended = true;
            require(!nestedCommitted, "nested transaction unexpectedly committed outer");
            validateOuter(outerId, "after nested end");
            for (int i = 0; i < targets.size(); i++) {
                validatePost(targets.get(i));
                equal(targets.get(i).entry, "body/instruction invariant", pre.get(i).invariant,
                    invariantKey(exact(targets.get(i))));
                equal(targets.get(i).entry, "ABI/storage invariant", pre.get(i).abi,
                    abiKey(exact(targets.get(i))));
            }
            validateTagCatalog(true);
            if (mode.equals("probe-post-inner")) {
                int restore = currentProgram.startTransaction(
                    "Restore MissionScript registry vocabulary PRE metadata");
                boolean restoreEnded = false;
                try {
                    for (int i = targets.size() - 1; i >= 0; i--) {
                        restorePre(targets.get(i), pre.get(i));
                    }
                    validateTagCatalog(false);
                    boolean restoreCommitted = currentProgram.endTransaction(restore, true);
                    restoreEnded = true;
                    require(!restoreCommitted,
                        "restore nested transaction unexpectedly committed outer");
                } finally {
                    if (!restoreEnded) currentProgram.endTransaction(restore, false);
                }
                for (Target target : targets) validatePre(target);
                validateTagCatalog(false);
                validateOuter(outerId, "after compensating PRE restore");
                compensatingPreRestored = true;
                println("MISSION_REGISTRY_NEW_FUNCTION_VOCABULARY_" +
                    "COMPENSATING_PRE_RESTORE_COMPLETE targets=34 " +
                    "tag_catalog_restored=true");
                println("MISSION_REGISTRY_NEW_FUNCTION_VOCABULARY_" +
                    "FORCED_POST_INNER_FAILURE " +
                    "nested_commit_requested=true pre_restored=true");
                throw new IllegalStateException("intentional post-inner rollback probe");
            }
            require(mode.equals("apply"), "unexpected successful mutation mode: " + mode);
            byte[] output = output(mode, "POST", targets);
            publishPair(out, output, receipt, ready(mode, "POST", toolRelative, toolBytes,
                outputRelative, output, true, nestedCommitted));
            println("MISSION_REGISTRY_NEW_FUNCTION_VOCABULARY_APPLY_COMPLETE targets=34 " +
                "reopen_verification_required=true");
        } catch (Exception error) {
            if (!ended) {
                try {
                    nestedCommitted = currentProgram.endTransaction(transaction, false);
                    ended = true;
                } catch (Exception rollbackError) { error.addSuppressed(rollbackError); }
            }
            println("MISSION_REGISTRY_NEW_FUNCTION_VOCABULARY_MUTATION_TAINTED mode=" + mode +
                " commit_requested=" + requested + " nested_committed=" + nestedCommitted +
                " outer_rollback_required=" + !compensatingPreRestored +
                " recovery=" + (compensatingPreRestored ?
                    "COMPENSATING_PRE_RESTORE_VERIFIED" :
                    "SEPARATE_EXACT_PRE_READBACK_REQUIRED"));
            throw error;
        } finally {
            if (!ended) currentProgram.endTransaction(transaction, false);
        }
    }
}
