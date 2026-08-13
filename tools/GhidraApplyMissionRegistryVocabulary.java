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
 * Target-specific metadata mutator for the reviewed 75-row MissionScript
 * registry vocabulary-normalization cohort. Registry names are Tier-2
 * script-facing vocabulary, never asserted original C++ symbols or behavior.
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
public class GhidraApplyMissionRegistryVocabulary extends GhidraScript {
    private static final String SCHEMA = "bea.ghidra.mission-registry-vocabulary.v1";
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
    private static final int TARGET_COUNT = 75;
    private static final int DEFAULT_COUNT = 54;
    private static final int MSG_COUNT = 5;
    private static final int CLASS3_COUNT = 16;
    private static final String REGISTRY_TAG = "script-command-registry";
    private static final String TIER2_TAG = "tier2-script-facing-name";
    private static final String EMPTY_TAGS_SENTINEL = "<EMPTY>";
    private static final int PRE_TAG_CATALOG_COUNT = 6853;
    private static final String PRE_TAG_CATALOG_SHA256 =
        "351e7234d66db90af13a4f4ecfd3df9e1ed7f6db6b9828f97f0758f8cdeef811";
    private static final String PRE_TAG_USAGE_SHA256 =
        "bc7a8ba82155bb7a8f33fbb4ec2ebc15684dffa11b75b212338baf3eca06efd9";
    private static final int POST_TAG_CATALOG_COUNT = 6854;
    private static final String POST_TAG_CATALOG_SHA256 =
        "074dd7480aebfe46aabe5a48c1429348a814c9b51b0d71d985cbdac6e764603f";
    private static final String POST_TAG_USAGE_SHA256 =
        "a23aa97dca8f2f36646abc90a12363581a4d87610cc897b4c5558a8044bbcd78";
    private static final String MANIFEST_RELATIVE =
        "reverse-engineering/binary-analysis/" +
        "mission-script-registry-vocabulary-normalization-2026-08-13.tsv";
    private static final long MANIFEST_BYTES = 7299;
    private static final String MANIFEST_SHA256 =
        "a30897bbb1c842fa046af62f3dc1f91b7888af162963d01422074f083c513145";
    private static final String META_RELATIVE =
        "reverse-engineering/binary-analysis/" +
        "mission-script-registry-vocabulary-normalization-pre-metadata-2026-08-13.tsv";
    private static final long META_BYTES = 22628;
    private static final String META_SHA256 =
        "cc7cc62d64bcd62f6024f2b4ccc66c369426853c638ba90a773d537fd269470b";
    private static final String OWNER_RELATIVE =
        "reverse-engineering/binary-analysis/" +
        "mission-script-registry-vocabulary-normalization-2026-08-13.md";
    private static final long OWNER_BYTES = 11148;
    private static final String OWNER_SHA256 =
        "ac26beab94426fff3d30a04490200ce41e125787d5f5ad0784ee37dfd0114e01";
    private static final String CANONICAL_PROJECTION_SHA256 =
        "39a9f2f01eb82c9f1924f716cb621dd9d9f680f7c584315e770f7731a0da9992";
    private static final String EMPTY_SHA256 =
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855";

    private static final String MANIFEST_HEADER =
        "index\tcommand\thandlerVa\tregistryRecordVa\tcohort\texpectedPreName\t" +
        "proposedName\texpectedNameSource";
    private static final String META_HEADER =
        "handlerVa\tpreCommentPresent\tpreCommentLen\tpreCommentSha256\t" +
        "preRepeatableCommentPresent\tpreRepeatableCommentLen\t" +
        "preRepeatableCommentSha256\tpreTagCount\tpreTagsSha256\tpreTags";

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
        requirePinned(root, OWNER_RELATIVE, OWNER_BYTES, OWNER_SHA256);
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
        int defaults = 0, messages = 0, class3 = 0;
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
                String.format("0x%08X", 0x0064CE20L + 0x40L * target.index), target.record);
            if (target.cohort.equals("DEFAULT54")) {
                defaults++;
                require(target.preName.matches("FUN_[0-9a-f]{8}"),
                    "DEFAULT54 must start from FUN_*: " + target.entry);
                equal(target.entry, "default name source", SourceType.DEFAULT, target.preNameSource);
            } else if (target.cohort.equals("MSG5")) {
                messages++;
            } else if (target.cohort.equals("CLASS3_16")) {
                class3++;
            } else throw new IllegalStateException("unknown cohort: " + target.cohort);
            target.meta = metas.get(target.entry.toLowerCase(Locale.ROOT));
            require(target.meta != null, "missing PRE metadata: " + target.entry);
            canonical.append(target.index).append('\t').append(target.entry).append('\t')
                .append(target.preName).append('\t').append(target.postName).append('\n');
            targets.add(target);
        }
        equal("manifest", "targets", TARGET_COUNT, targets.size());
        equal("PRE metadata", "targets", TARGET_COUNT, metas.size());
        equal("manifest", "DEFAULT54", DEFAULT_COUNT, defaults);
        equal("manifest", "MSG5", MSG_COUNT, messages);
        equal("manifest", "CLASS3_16", CLASS3_COUNT, class3);
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
        if (post) {
            require(tier2 != null, "Tier-2 tag definition is absent");
            equal("tag catalog", "Tier-2 definition comment", "",
                nullable(tier2.getComment()));
            equal("tag catalog", "Tier-2 use count", TARGET_COUNT,
                manager.getUseCount(tier2));
        } else {
            equal("tag catalog", "Tier-2 definition absent", null, tier2);
        }
    }

    private List<String> postTags(Target target) {
        Set<String> result = new HashSet<>(target.meta.tags);
        if (target.index == 28) result.remove("callback-message");
        if (target.index == 36 || target.index == 91) result.remove("fade-event");
        result.add(REGISTRY_TAG);
        result.add(TIER2_TAG);
        List<String> sorted = new ArrayList<>(result);
        Collections.sort(sorted);
        return sorted;
    }

    private String commonComment(Target target) {
        return "Mission registry vocabulary: slot " + target.index + " (record " +
            target.record + ") registers this handler as `" + target.command + "`. The promoted `" +
            target.postName + "` name is Tier 2 script-facing vocabulary under the project " +
            "naming convention, not a recovered C++ symbol and not evidence of this handler's " +
            "signature, arguments, side effects, failure behavior, or complete semantics.";
    }

    private String suffix(Target target) {
        String extra;
        if (target.cohort.equals("DEFAULT54")) {
            extra = "This function had only a default `FUN_*` label before this metadata " +
                "promotion; no behavior claim is added.";
        } else if (target.cohort.equals("CLASS3_16")) {
            extra = "The prior label `" + target.preName + "` was a Tier 3 mechanism-facing " +
                "description. Its bounded body/callee observations remain in the pre-existing " +
                "comment and tags where present; this vocabulary rename neither refutes those " +
                "observations nor upgrades them into a behavior contract.";
        } else {
            require(false, "suffix append is forbidden for MSG5: " + target.entry);
            return "";
        }
        return commonComment(target) + "\n\n" + extra;
    }

    private String messageComment(Target target) {
        require(target.cohort.equals("MSG5"),
            "message comment requested outside MSG5: " + target.entry);
        String measured = "Measured row-specific facts: this native obtains localized text, " +
            "constructs a seven-argument `CMessage__ctor_base`, and submits the message through " +
            "`CMessageBox__InsertQueuedMessageSortedAndMaybeAdvance`; queued advancement can " +
            "reach `CMessageBox__StartVoiceOrFallbackTextReveal`. ";
        String row;
        switch (target.index) {
            case 17:
                row = "Constructor argument 1 is fixed global `0x0089C328`; argument 5 is a " +
                    "register in the optional-audio-reader slot; argument 6 is a register; " +
                    "argument 7 is literal `0xA`. Argument 1 is the measured `AddMessage` " +
                    "distinction from the four `*CharMessage*` forms.";
                break;
            case 28:
                row = "Constructor argument 5 is a register in the optional-audio-reader slot; " +
                    "argument 6 is literal `0`; argument 7 is literal `0xA`. The measured " +
                    "body/call layer registers no callback, so the prior callback claim and tag " +
                    "are withdrawn.";
                break;
            case 36:
                row = "Constructor argument 5 is a register in the optional-audio-reader slot; " +
                    "argument 6 is a register; argument 7 is literal `0xA`. This body also calls " +
                    "`CEventManager__GetNextFreeEvent` and `CScheduledEvent__Set`, which " +
                    "establishes the `Wait` scheduling axis at this layer, not fade; the prior " +
                    "fade claim and tag are withdrawn.";
                break;
            case 90:
                row = "Constructor argument 5 is a register in the optional-audio-reader slot; " +
                    "argument 6 is literal `0`; argument 7 is caller-varied. Argument 7 is the " +
                    "measured `P` axis; priority remains a plausible mechanism reading, not a " +
                    "recovered field meaning, so `priority-message` is retained only at that " +
                    "bounded confidence.";
                break;
            case 91:
                row = "Constructor arguments 5, 6, and 7 are registers. This body also calls " +
                    "`CEventManager__GetNextFreeEvent` and `CScheduledEvent__Set`. Argument 6 " +
                    "plus scheduling establishes the `Wait` axis, while argument 7 is the " +
                    "measured `P` axis; the fade claim and tag are withdrawn, while " +
                    "`priority-message` and `scheduled-event-7d1` remain at their bounded " +
                    "structural confidence.";
                break;
            default:
                throw new IllegalStateException("unreviewed MSG5 index: " + target.index);
        }
        return commonComment(target) + "\n\n" + measured + row + " Complete behavior, " +
            "unresolved constructor slots and field meanings, failure paths, and original C++ " +
            "identity remain open.";
    }

    private String postComment(Target target, String pre) {
        if (target.cohort.equals("MSG5")) return messageComment(target);
        return pre.isEmpty() ? suffix(target) : pre + "\n\n" + suffix(target);
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
        String expectedComment = target.cohort.equals("MSG5") ? messageComment(target) :
            postComment(target, commentPrefix(target, function));
        equal(target.entry, "POST comment", expectedComment, nullable(function.getComment()));
        equal(target.entry, "POST tags", postTags(target), tags(function));
        String repeatable = nullable(function.getRepeatableComment());
        equal(target.entry, "POST repeatable present", target.meta.repeatablePresent,
            function.getRepeatableComment() != null);
        equal(target.entry, "POST repeatable length", target.meta.repeatableLength,
            repeatable.length());
        equal(target.entry, "POST repeatable SHA-256", target.meta.repeatableSha256,
            sha256(repeatable));
    }

    private String commentPrefix(Target target, Function function) throws Exception {
        require(!target.cohort.equals("MSG5"),
            "MSG5 comments replace PRE and have no retained prefix: " + target.entry);
        String post = nullable(function.getComment());
        String suffix = suffix(target);
        String prefix;
        if (post.equals(suffix)) prefix = "";
        else {
            String delimiter = "\n\n" + suffix;
            require(post.endsWith(delimiter), "POST comment suffix mismatch: " + target.entry);
            prefix = post.substring(0, post.length() - delimiter.length());
        }
        equal(target.entry, "retained PRE comment length", target.meta.commentLength,
            prefix.length());
        equal(target.entry, "retained PRE comment SHA-256", target.meta.commentSha256,
            sha256(prefix));
        return prefix;
    }

    private void mutate(Target target, PreState pre) throws Exception {
        Function function = exact(target);
        function.setName(target.postName, SourceType.USER_DEFINED);
        function.setComment(postComment(target, pre.comment));
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

    private void removeCreatedTier2TagDefinition() {
        FunctionTagManager manager =
            currentProgram.getFunctionManager().getFunctionTagManager();
        FunctionTag tag = manager.getFunctionTag(TIER2_TAG);
        require(tag != null, "created Tier-2 tag definition is absent during PRE restore");
        equal("tag catalog", "Tier-2 use count before definition removal", 0,
            manager.getUseCount(tag));
        tag.delete();
        equal("tag catalog", "Tier-2 definition removed", null,
            manager.getFunctionTag(TIER2_TAG));
    }

    private static File newOutput(String value, String label) throws Exception {
        File file = new File(value).getCanonicalFile();
        require(!file.exists(), label + " already exists: " + file);
        require(file.getParentFile() != null && file.getParentFile().isDirectory(),
            label + " parent absent: " + file);
        return file;
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

    private byte[] ready(String mode, String state, File tool, byte[] toolBytes,
            File manifest, File metadata, File owner, File output, byte[] outputBytes,
            boolean commitRequested, boolean nestedCommitted) throws Exception {
        String value = "{\n" +
            "  \"schema\": \"" + SCHEMA + "\",\n" +
            "  \"completedAtUtc\": \"" + Instant.now() + "\",\n" +
            "  \"mode\": \"" + mode + "\",\n" +
            "  \"state\": \"" + state + "\",\n" +
            "  \"tool\": {\"path\": \"" + json(tool.getCanonicalPath()) +
                "\", \"bytes\": " + toolBytes.length + ", \"sha256\": \"" +
                sha256(toolBytes) + "\"},\n" +
            "  \"manifest\": {\"path\": \"" + json(manifest.getCanonicalPath()) +
                "\", \"bytes\": " + MANIFEST_BYTES + ", \"sha256\": \"" +
                MANIFEST_SHA256 + "\"},\n" +
            "  \"preMetadata\": {\"path\": \"" + json(metadata.getCanonicalPath()) +
                "\", \"bytes\": " + META_BYTES + ", \"sha256\": \"" +
                META_SHA256 + "\"},\n" +
            "  \"owner\": {\"path\": \"" + json(owner.getCanonicalPath()) +
                "\", \"bytes\": " + OWNER_BYTES + ", \"sha256\": \"" +
                OWNER_SHA256 + "\"},\n" +
            "  \"program\": {\"name\": \"" + PROGRAM_NAME +
                "\", \"md5\": \"" + PROGRAM_MD5 + "\", \"sha256\": \"" +
                PROGRAM_SHA256 + "\", \"functions\": " + FUNCTION_COUNT +
                ", \"instructions\": " + INSTRUCTION_COUNT + "},\n" +
            "  \"targets\": {\"total\": 75, \"DEFAULT54\": 54, \"MSG5\": 5, " +
                "\"CLASS3_16\": 16},\n" +
            "  \"tagCatalog\": {\"count\": " +
                (state.equals("POST") ? POST_TAG_CATALOG_COUNT : PRE_TAG_CATALOG_COUNT) +
                ", \"definitionsSha256\": \"" +
                (state.equals("POST") ? POST_TAG_CATALOG_SHA256 : PRE_TAG_CATALOG_SHA256) +
                "\", \"usageSha256\": \"" +
                (state.equals("POST") ? POST_TAG_USAGE_SHA256 : PRE_TAG_USAGE_SHA256) +
                "\"},\n" +
            "  \"mutation\": {\"namesChanged\": 75, \"commentsChanged\": 75, " +
                "\"newFunctionComments\": 54, \"tagAssociationsAdded\": 130, " +
                "\"tagAssociationsRemoved\": 3, \"tagDefinitionsAdded\": 1, " +
                "\"boundariesChanged\": 0, \"abiChanged\": 0, \"bytesChanged\": 0, " +
                "\"instructionsChanged\": 0, \"referencesChanged\": 0},\n" +
            "  \"output\": {\"path\": \"" + json(output.getCanonicalPath()) +
                "\", \"bytes\": " + outputBytes.length + ", \"sha256\": \"" +
                sha256(outputBytes) + "\"},\n" +
            "  \"commitRequested\": " + commitRequested + ",\n" +
            "  \"nestedEndReturnedCommitted\": " + nestedCommitted + ",\n" +
            "  \"loadedStateVerified\": " + mode.equals("readback") + ",\n" +
            "  \"registryNamesAreOriginalCppSymbols\": false,\n" +
            "  \"behaviorContractsAuthorized\": false,\n" +
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
        File out = newOutput(args[1], "TSV output");
        File receipt = newOutput(args[2], "READY output");
        require(!out.equals(receipt), "output paths must differ");
        File manifest = new File(root, MANIFEST_RELATIVE).getCanonicalFile();
        File metadata = new File(root, META_RELATIVE).getCanonicalFile();
        File owner = new File(root, OWNER_RELATIVE).getCanonicalFile();
        List<Target> targets = loadTargets(root);
        validateProgram();
        byte[] toolBytes;
        try (InputStream stream = getSourceFile().getInputStream()) {
            toolBytes = stream.readAllBytes();
        }
        File tool = new File(getSourceFile().getCanonicalPath()).getCanonicalFile();

        if (mode.equals("readback")) {
            for (Target target : targets) validatePost(target);
            validateTagCatalog(true);
            byte[] output = output(mode, "POST", targets);
            publishPair(out, output, receipt, ready(mode, "POST", tool, toolBytes,
                manifest, metadata, owner, out, output, false, false));
            println("MISSION_REGISTRY_VOCABULARY_READBACK_COMPLETE targets=75 " +
                "loaded_state_verified=true");
            return;
        }

        List<PreState> pre = new ArrayList<>();
        for (Target target : targets) pre.add(validatePre(target));
        validateTagCatalog(false);
        println("MISSION_REGISTRY_VOCABULARY_PREFLIGHT_OK targets=75 functions=8170 " +
            "canonical_projection=" + CANONICAL_PROJECTION_SHA256);
        if (mode.equals("dry")) {
            byte[] output = output(mode, "PRE", targets);
            publishPair(out, output, receipt, ready(mode, "PRE", tool, toolBytes,
                manifest, metadata, owner, out, output, false, false));
            println("MISSION_REGISTRY_VOCABULARY_DRY_COMPLETE targets=75 mutations=0");
            return;
        }

        TransactionInfo outer = currentProgram.getCurrentTransactionInfo();
        require(outer != null && !currentProgram.hasTerminatedTransaction(),
            "mutation requires healthy outer transaction");
        long outerId = outer.getID();
        validateOuter(outerId, "before mutation");
        int transaction = currentProgram.startTransaction(
            "Normalize 75 MissionScript registry-facing names");
        boolean ended = false, requested = false, nestedCommitted = false;
        boolean compensatingPreRestored = false;
        try {
            int limit = mode.equals("probe-after-one") ? 1 : targets.size();
            for (int i = 0; i < limit; i++) {
                monitor.checkCancelled();
                mutate(targets.get(i), pre.get(i));
            }
            if (mode.equals("probe-after-one")) {
                println("MISSION_REGISTRY_VOCABULARY_FORCED_AFTER_ONE_FAILURE " +
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
                    removeCreatedTier2TagDefinition();
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
                println("MISSION_REGISTRY_VOCABULARY_COMPENSATING_PRE_RESTORE_COMPLETE " +
                    "targets=75 tag_catalog_restored=true");
                println("MISSION_REGISTRY_VOCABULARY_FORCED_POST_INNER_FAILURE " +
                    "nested_commit_requested=true pre_restored=true");
                throw new IllegalStateException("intentional post-inner rollback probe");
            }
            require(mode.equals("apply"), "unexpected successful mutation mode: " + mode);
            byte[] output = output(mode, "POST", targets);
            publishPair(out, output, receipt, ready(mode, "POST", tool, toolBytes,
                manifest, metadata, owner, out, output, true, nestedCommitted));
            println("MISSION_REGISTRY_VOCABULARY_APPLY_COMPLETE targets=75 " +
                "reopen_verification_required=true");
        } catch (Exception error) {
            if (!ended) {
                try {
                    nestedCommitted = currentProgram.endTransaction(transaction, false);
                    ended = true;
                } catch (Exception rollbackError) { error.addSuppressed(rollbackError); }
            }
            println("MISSION_REGISTRY_VOCABULARY_MUTATION_TAINTED mode=" + mode +
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
