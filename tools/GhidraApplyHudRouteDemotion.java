//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.framework.model.TransactionInfo;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;
import ghidra.program.model.symbol.SourceType;

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
import java.util.List;
import java.util.Locale;
import java.util.UUID;

/**
 * Apply the four HUD route descriptive-name demotions (2026-08-14).
 *
 * Targets (route indices from local-lab/pc-hud-static-join-20260812-v1):
 *   0x00483530 CHud__RenderControllerSlotStatusPanel              -> CHud__RoutePanel_T0_00483530 (refuted)
 *   0x004858d0 CHud__RenderObjectiveProgressGaugeAndHeadingNeedle -> CHud__RoutePanel_T3_004858d0 (half refuted)
 *   0x00485d50 CHud__RenderObjectiveStatusPanel                   -> CHud__RoutePanel_T4_00485d50 (suspect)
 *   0x00486940 CHud__RenderObjectiveSlotFillPanel                 -> CHud__RoutePanel_T5_00486940 (refuted)
 *
 * This is deliberately not a generic rename tool.  It accepts only the exact
 * sealed PRE inspection and the static-join evidence note.  It changes four
 * names, the corresponding displayed signatures, four comments, and their
 * exact tag sets.  It never changes boundaries, bytes, instructions, data, or
 * references.
 *
 * Modes:
 *   dry              validate exact PRE and publish no mutation;
 *   probe-after-one  mutate one function, then force transaction rollback;
 *   probe-post-inner mutate all four, restore exact captured PRE metadata in
 *                    a compensating transaction, then force failure;
 *   apply            mutate all four in one nested transaction;
 *   readback         require exact loaded POST without mutation.
 */
public class GhidraApplyHudRouteDemotion extends GhidraScript {
    private static final String SCHEMA = "bea.ghidra.hud-route-demotion.v1";
    private static final String PROGRAM_NAME = "BEA.exe";
    private static final String PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55";
    private static final String PROGRAM_SHA256 =
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
    private static final String IMAGE_BASE = "00400000";
    private static final String LANGUAGE = "x86:LE:32:default";
    private static final String COMPILER_SPEC = "windows";
    private static final String MEMORY_SHA256 =
        "5398f750f1ffb59873a6ec7e1750b51d11b5b844a8fda8d4e43649b5b9e5089d";
    private static final long FUNCTION_COUNT = 8329;
    private static final long INSTRUCTION_COUNT = 551143;

    private static final String INSPECTION_RELATIVE =
        "local-lab/ghidra-hud-route-demotion-20260814-v1/inspection/target.tsv";
    private static final long INSPECTION_BYTES = 3402;
    private static final String INSPECTION_SHA256 =
        "aafe0ad29bc3a6d38e8c36a57e9aaaed6d0f1e7f7cf09fe13ce04aeb1314b814";

    private static final String EVIDENCE_RELATIVE =
        "local-lab/pc-hud-static-join-20260812-v1/NOTE.md";
    private static final long EVIDENCE_BYTES = 23973;
    private static final String EVIDENCE_SHA256 =
        "3eb9f53adf44f291444a037a903f3ef04245c1e06a78f86179c49591e6fdc9bc";

    private static final String DEMOTION_T0 =
        "Descriptive-name demotion 2026-08-14: the previous name " +
        "CHud__RenderControllerSlotStatusPanel is refuted - no controller or input callee exists " +
        "anywhere in this body. Measured: 20 calls to CWorld__GetWorldTextSlotTimerValue (the " +
        "mission script variable store; its only other caller is the GetVariable script " +
        "command), formats %d (%d), %d%, mm:ss and mm:ss.hh clock strings via sprintf and " +
        "CPlatform__Font, CDXFont__GetTextExtent / DrawTextDynamic, and two " +
        "CHud__RenderSegmentedMeterBar calls. Sole inbound call from " +
        "CHud__RenderOverlayForViewpoint. Renders a mission-variable readout with numeric, " +
        "percentage and clock formatting plus meter bars; exact on-screen role unproven. " +
        "Neutral Tier-3 label pending measured naming; evidence " +
        "local-lab/pc-hud-static-join-20260812-v1/NOTE.md.";

    private static final String DEMOTION_T3 =
        "Descriptive-name demotion 2026-08-14: the previous name " +
        "CHud__RenderObjectiveProgressGaugeAndHeadingNeedle is half refuted - the gauge value " +
        "this body reads is CBattleEngine__GetWeaponCharge (weapon charge), not objective " +
        "progress; the heading-needle half is supported by GetInterpolatedEulerOrientation. " +
        "Sole inbound call from CHud__RenderOverlayForViewpoint. Exact on-screen role " +
        "unproven. Neutral Tier-3 label pending measured naming; evidence " +
        "local-lab/pc-hud-static-join-20260812-v1/NOTE.md.";

    private static final String DEMOTION_T4 =
        "Descriptive-name demotion 2026-08-14: the previous name " +
        "CHud__RenderObjectiveStatusPanel is suspect, not refuted - this body counts units " +
        "via CountFlag9CBySelectionMode and formats x%d with heavy text drawing, reading as a " +
        "unit or squad count; a status panel could legitimately show counts, so the " +
        "refutation is not decisive. Sole inbound call from CHud__RenderOverlayForViewpoint. " +
        "Exact on-screen role unproven. Neutral Tier-3 label pending measured naming; " +
        "evidence local-lab/pc-hud-static-join-20260812-v1/NOTE.md.";

    private static final String DEMOTION_T5 =
        "Descriptive-name demotion 2026-08-14: the previous name " +
        "CHud__RenderObjectiveSlotFillPanel is refuted - the only two state reads are " +
        "CBattleEngine__IsEnergyWeapon and CBattleEngine__GetWeaponAmmoPercentage, a weapon " +
        "ammo/energy fill gauge with nothing objective-related. Sole inbound call from " +
        "CHud__RenderOverlayForViewpoint. Exact on-screen role unproven. Neutral Tier-3 " +
        "label pending measured naming; evidence local-lab/pc-hud-static-join-20260812-v1/" +
        "NOTE.md.";

    private static final List<String> POST_TAGS_BASE = Arrays.asList(
        "comment-hardened", "hud", "hud-overlay-helpers-wave411", "name-demoted-20260814",
        "overlay", "owner-corrected", "retail-binary-evidence", "route-panel",
        "signature-hardened", "static-reaudit");
    private static final List<String> POST_TAGS_WEAPON = Arrays.asList(
        "comment-hardened", "hud", "hud-overlay-helpers-wave411", "name-demoted-20260814",
        "overlay", "owner-corrected", "retail-binary-evidence", "route-panel",
        "signature-hardened", "static-reaudit", "weapon-status");

    private static class Target {
        final String address;
        final String preName;
        final String postName;
        final String preSignature;
        final String postSignature;
        final long bodyBytes;
        final String bodyDigest;
        final String bodyBytesSha256;
        final long instructionCount;
        final long preCommentBytes;
        final String preCommentSha256;
        final List<String> preTags;
        final String postComment;
        final List<String> postTags;

        Target(
                String address, String preName, String postName,
                long bodyBytes, String bodyDigest, String bodyBytesSha256,
                long instructionCount, long preCommentBytes, String preCommentSha256,
                List<String> preTags, String postComment, List<String> postTags) {
            this.address = address;
            this.preName = preName;
            this.postName = postName;
            this.preSignature = "void __thiscall " + preName + "(void * this)";
            this.postSignature = "void __thiscall " + postName + "(void * this)";
            this.bodyBytes = bodyBytes;
            this.bodyDigest = bodyDigest;
            this.bodyBytesSha256 = bodyBytesSha256;
            this.instructionCount = instructionCount;
            this.preCommentBytes = preCommentBytes;
            this.preCommentSha256 = preCommentSha256;
            this.preTags = sorted(preTags);
            this.postComment = postComment;
            this.postTags = sorted(postTags);
        }
    }

    private static class PreState {
        final String comment;
        final List<String> tags;

        PreState(String comment, List<String> tags) {
            this.comment = comment;
            this.tags = new ArrayList<>(tags);
        }
    }

    private static final List<Target> TARGETS = Arrays.asList(
        new Target(
            "0x00483530", "CHud__RenderControllerSlotStatusPanel",
            "CHud__RoutePanel_T0_00483530",
            3570, "e752a8b626dad180ca786236d8bf50aa3d769bf9a1eb88494216c959a5f7edf9",
            "b8424e351fd91fa1c7c65bbdaed766c9441a1c39c23cb7e8a7f942a39ef2ffd7", 966,
            414, "5f11063663018a80984641329b767f68e8613c364dee6b786302461ff581cf07",
            Arrays.asList("comment-hardened", "controller-status", "hud",
                "hud-overlay-helpers-wave411", "overlay", "owner-corrected",
                "retail-binary-evidence", "signature-hardened", "static-reaudit"),
            DEMOTION_T0, POST_TAGS_BASE),
        new Target(
            "0x004858d0", "CHud__RenderObjectiveProgressGaugeAndHeadingNeedle",
            "CHud__RoutePanel_T3_004858d0",
            1140, "26114fd54c806f8db45c71a8d85406f7329821480e72eedc7022d24fa8fd08a0",
            "dc0c495864c8c626cd3d7a3aa0f1f46886548c6615189315a0acbe8ba25e754a", 306,
            477, "28f021c0d2fb7cbb323301d2c97e779342debc4f97184185a7816768e5357dfe",
            Arrays.asList("comment-hardened", "hud", "hud-overlay-helpers-wave411",
                "objective", "overlay", "owner-corrected", "retail-binary-evidence",
                "signature-hardened", "static-reaudit"),
            DEMOTION_T3, POST_TAGS_BASE),
        new Target(
            "0x00485d50", "CHud__RenderObjectiveStatusPanel",
            "CHud__RoutePanel_T4_00485d50",
            3042, "349f97a22db7f35ea92691c94d74396613e394e35f2b61e2e1192d2d91911ef0",
            "675f10a28c99749384dfa2dd27ed9ddfa9ac661687ad63174293553215d372e8", 793,
            524, "16f16f8c6efe2c96323a6cab39d297d78ee0e5f6ae730674f97badda275cbd12",
            Arrays.asList("comment-hardened", "hud", "hud-overlay-helpers-wave411",
                "objective", "overlay", "owner-corrected", "retail-binary-evidence",
                "signature-hardened", "static-reaudit", "weapon-status"),
            DEMOTION_T4, POST_TAGS_WEAPON),
        new Target(
            "0x00486940", "CHud__RenderObjectiveSlotFillPanel",
            "CHud__RoutePanel_T5_00486940",
            1212, "32988a4a31ddbfea2c536e5b3f1f31e3c36d077e753c0d4b947ae8d140312c9c",
            "07b961255d5935ff48e9a6f73aff3491f05c890bade4eb0c36176186e72ddf6c", 319,
            484, "986530e20b30c940b34bec068b86b3af9e31bbb354cf0b1a027b4cbe2b022aac",
            Arrays.asList("comment-hardened", "hud", "hud-overlay-helpers-wave411",
                "objective", "overlay", "owner-corrected", "retail-binary-evidence",
                "signature-hardened", "static-reaudit", "weapon-status"),
            DEMOTION_T5, POST_TAGS_WEAPON));

    private static List<String> sorted(List<String> values) {
        List<String> result = new ArrayList<>(values);
        Collections.sort(result);
        return result;
    }

    private static void require(boolean value, String message) {
        if (!value) {
            throw new IllegalStateException(message);
        }
    }

    private static void requireEqual(String owner, String field, Object expected, Object actual) {
        if (expected == null ? actual != null : !expected.equals(actual)) {
            throw new IllegalStateException(owner + " " + field + " differs: expected=" +
                expected + " actual=" + actual);
        }
    }

    private static String nullable(String value) {
        return value == null ? "" : value;
    }

    private static String hex(byte[] bytes) {
        StringBuilder result = new StringBuilder();
        for (byte value : bytes) {
            result.append(String.format(Locale.ROOT, "%02x", value & 0xff));
        }
        return result.toString();
    }

    private static String sha256(byte[] bytes) throws Exception {
        return hex(MessageDigest.getInstance("SHA-256").digest(bytes));
    }

    private static String sha256(String value) throws Exception {
        return sha256(value.getBytes(StandardCharsets.UTF_8));
    }

    private static String json(String value) {
        return nullable(value).replace("\\", "\\\\").replace("\"", "\\\"")
            .replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t");
    }

    private long functionCount() {
        long count = 0;
        FunctionIterator iterator = currentProgram.getFunctionManager().getFunctions(true);
        while (iterator.hasNext()) {
            iterator.next();
            count++;
        }
        return count;
    }

    private long instructionCount() {
        long count = 0;
        InstructionIterator iterator = currentProgram.getListing().getInstructions(true);
        while (iterator.hasNext()) {
            iterator.next();
            count++;
        }
        return count;
    }

    private static void digestString(MessageDigest digest, String value) {
        byte[] bytes = value.getBytes(StandardCharsets.UTF_8);
        digest.update((byte) ((bytes.length >>> 24) & 0xff));
        digest.update((byte) ((bytes.length >>> 16) & 0xff));
        digest.update((byte) ((bytes.length >>> 8) & 0xff));
        digest.update((byte) (bytes.length & 0xff));
        digest.update(bytes);
    }

    private String memoryDigest() throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        Memory memory = currentProgram.getMemory();
        List<MemoryBlock> blocks = new ArrayList<>(Arrays.asList(memory.getBlocks()));
        blocks.sort(Comparator.comparing(MemoryBlock::getStart)
            .thenComparing(MemoryBlock::getEnd).thenComparing(MemoryBlock::getName));
        for (MemoryBlock block : blocks) {
            String name = block.getName();
            String source = block.getSourceName();
            String comment = block.getComment();
            digestString(digest,
                name.length() + ":" + sha256(name) +
                "\t" + (source == null ? -1 : source.length()) + ":" + sha256(nullable(source)) +
                "\t" + (comment == null ? -1 : comment.length()) + ":" + sha256(nullable(comment)) +
                "\t" + block.getStart() + "\t" + block.getEnd() + "\t" + block.getSize() +
                "\t" + block.isInitialized() + "\t" + block.isRead() + "\t" + block.isWrite() +
                "\t" + block.isExecute() + "\t" + block.isVolatile() +
                "\t" + block.isArtificial() + "\t" + block.isMapped() +
                "\t" + block.isOverlay() + "\t" + block.isLoaded() + "\t" + block.getType());
            if (!block.isInitialized()) {
                continue;
            }
            Address cursor = block.getStart();
            long remaining = block.getSize();
            while (remaining > 0) {
                monitor.checkCancelled();
                int size = (int) Math.min(1024 * 1024L, remaining);
                byte[] chunk = new byte[size];
                int read = memory.getBytes(cursor, chunk);
                requireEqual("program", "memory read", size, read);
                digest.update(chunk);
                cursor = cursor.add(size);
                remaining -= size;
            }
        }
        return hex(digest.digest());
    }

    private void validateProgram() throws Exception {
        requireEqual("program", "name", PROGRAM_NAME, currentProgram.getName());
        requireEqual("program", "MD5", PROGRAM_MD5,
            currentProgram.getExecutableMD5().toLowerCase(Locale.ROOT));
        requireEqual("program", "SHA-256", PROGRAM_SHA256,
            currentProgram.getExecutableSHA256().toLowerCase(Locale.ROOT));
        requireEqual("program", "image base", IMAGE_BASE,
            currentProgram.getImageBase().toString().toLowerCase(Locale.ROOT));
        requireEqual("program", "language", LANGUAGE,
            currentProgram.getLanguageID().toString());
        requireEqual("program", "compiler", COMPILER_SPEC,
            currentProgram.getCompilerSpec().getCompilerSpecID().toString());
        requireEqual("program", "memory", MEMORY_SHA256, memoryDigest());
        requireEqual("program", "functions", FUNCTION_COUNT, functionCount());
        requireEqual("program", "instructions", INSTRUCTION_COUNT, instructionCount());
    }

    private String bodyDigest(AddressSetView body) throws Exception {
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
        for (AddressRange range : body) {
            Address cursor = range.getMinAddress();
            long remaining = range.getLength();
            while (remaining > 0) {
                int size = (int) Math.min(1024 * 1024L, remaining);
                byte[] chunk = new byte[size];
                int read = currentProgram.getMemory().getBytes(cursor, chunk);
                requireEqual("body", "memory read", size, read);
                digest.update(chunk);
                cursor = cursor.add(size);
                remaining -= size;
            }
        }
        return hex(digest.digest());
    }

    private long exactInstructionCount(AddressSetView body, String label) {
        AddressSet covered = new AddressSet();
        long count = 0;
        InstructionIterator iterator = currentProgram.getListing().getInstructions(body, true);
        while (iterator.hasNext()) {
            Instruction instruction = iterator.next();
            require(body.contains(instruction.getMinAddress(), instruction.getMaxAddress()),
                "instruction crosses body at " + label + ": " + instruction.getAddress());
            covered.addRange(instruction.getMinAddress(), instruction.getMaxAddress());
            count++;
        }
        require(covered.hasSameAddresses(body), "instruction coverage differs at " + label);
        return count;
    }

    private List<String> tags(Function function) {
        List<String> result = new ArrayList<>();
        for (FunctionTag tag : function.getTags()) {
            result.add(tag.getName());
        }
        Collections.sort(result);
        return result;
    }

    private void setTags(Function function, List<String> expected) {
        for (String existing : tags(function)) {
            function.removeTag(existing);
        }
        for (String name : expected) {
            require(function.addTag(name), "could not add tag " + name + " at " + function.getEntryPoint());
        }
        requireEqual(function.getEntryPoint().toString(), "tag set", expected, tags(function));
    }

    private Function exactFunction(Target target) {
        Address entry = toAddr(target.address);
        Function function = getFunctionAt(entry);
        require(function != null && function.getEntryPoint().equals(entry),
            "exact function is absent at " + target.address);
        return function;
    }

    private void validateCommon(Target target, Function function) throws Exception {
        requireEqual(target.address, "name source", SourceType.USER_DEFINED,
            function.getSymbol().getSource());
        requireEqual(target.address, "signature source", SourceType.USER_DEFINED,
            function.getSignatureSource());
        requireEqual(target.address, "body bytes", target.bodyBytes,
            function.getBody().getNumAddresses());
        requireEqual(target.address, "body digest", target.bodyDigest,
            bodyDigest(function.getBody()));
        requireEqual(target.address, "body bytes SHA-256", target.bodyBytesSha256,
            bodyBytesSha256(function.getBody()));
        requireEqual(target.address, "instruction count", target.instructionCount,
            exactInstructionCount(function.getBody(), target.address));
    }

    private void validateNameCensus(String name, String expectedAddress) {
        int count = 0;
        String address = "";
        FunctionIterator iterator = currentProgram.getFunctionManager().getFunctions(true);
        while (iterator.hasNext()) {
            Function function = iterator.next();
            if (function.getName().equals(name)) {
                count++;
                address = "0x" + function.getEntryPoint().toString();
            }
        }
        requireEqual(name, "function-name census", 1, count);
        requireEqual(name, "function-name owner", expectedAddress, address);
    }

    private void validateNameAbsent(String name) {
        FunctionIterator iterator = currentProgram.getFunctionManager().getFunctions(true);
        while (iterator.hasNext()) {
            require(!iterator.next().getName().equals(name), "unexpected existing function name: " + name);
        }
    }

    private void validatePreTarget(Target target) throws Exception {
        Function function = exactFunction(target);
        validateCommon(target, function);
        requireEqual(target.address, "PRE name", target.preName, function.getName());
        requireEqual(target.address, "PRE signature", target.preSignature,
            function.getSignature().getPrototypeString(true));
        byte[] comment = nullable(function.getComment()).getBytes(StandardCharsets.UTF_8);
        requireEqual(target.address, "PRE comment bytes", target.preCommentBytes, (long) comment.length);
        requireEqual(target.address, "PRE comment SHA-256", target.preCommentSha256, sha256(comment));
        requireEqual(target.address, "PRE tags", target.preTags, tags(function));
    }

    private void validatePostTarget(Target target) throws Exception {
        Function function = exactFunction(target);
        validateCommon(target, function);
        requireEqual(target.address, "POST name", target.postName, function.getName());
        requireEqual(target.address, "POST signature", target.postSignature,
            function.getSignature().getPrototypeString(true));
        requireEqual(target.address, "POST comment", target.postComment, function.getComment());
        requireEqual(target.address, "POST tags", target.postTags, tags(function));
    }

    private void validatePre() throws Exception {
        validateProgram();
        for (Target target : TARGETS) {
            validatePreTarget(target);
            validateNameCensus(target.preName, target.address);
        }
        for (Target target : TARGETS) {
            validateNameAbsent(target.postName);
        }
    }

    private void validatePost() throws Exception {
        validateProgram();
        for (Target target : TARGETS) {
            validatePostTarget(target);
            validateNameCensus(target.postName, target.address);
        }
        for (Target target : TARGETS) {
            validateNameAbsent(target.preName);
        }
    }

    private PreState capturePre(Target target) throws Exception {
        validatePreTarget(target);
        Function function = exactFunction(target);
        return new PreState(function.getComment(), tags(function));
    }

    private void applyPost(Target target) throws Exception {
        Function function = exactFunction(target);
        validateCommon(target, function);
        requireEqual(target.address, "apply PRE name", target.preName, function.getName());
        function.setName(target.postName, SourceType.USER_DEFINED);
        function.setComment(target.postComment);
        setTags(function, target.postTags);
        validatePostTarget(target);
    }

    private void restorePre(Target target, PreState state) throws Exception {
        Function function = exactFunction(target);
        validateCommon(target, function);
        requireEqual(target.address, "restore POST name", target.postName, function.getName());
        function.setName(target.preName, SourceType.USER_DEFINED);
        function.setComment(state.comment);
        setTags(function, state.tags);
        validatePreTarget(target);
    }

    private static File requireEvidence(
            File repositoryRoot, String relative, File supplied,
            long expectedBytes, String expectedSha256) throws Exception {
        File canonical = supplied.getCanonicalFile();
        File expected = new File(repositoryRoot, relative).getCanonicalFile();
        requireEqual(relative, "canonical evidence path", expected, canonical);
        require(canonical.isFile(), "evidence is absent: " + canonical);
        byte[] bytes = Files.readAllBytes(canonical.toPath());
        requireEqual(relative, "evidence bytes", expectedBytes, (long) bytes.length);
        requireEqual(relative, "evidence SHA-256", expectedSha256, sha256(bytes));
        return canonical;
    }

    private static File requireNewOutput(String value, String label) throws Exception {
        File output = new File(value).getCanonicalFile();
        require(!output.exists(), label + " already exists: " + output);
        require(output.getParentFile() != null && output.getParentFile().isDirectory(),
            label + " parent is absent: " + output);
        return output;
    }

    private static void force(File file) throws Exception {
        try (FileChannel channel = FileChannel.open(file.toPath(), StandardOpenOption.WRITE)) {
            channel.force(true);
        }
    }

    private static File stage(File output, byte[] bytes) throws Exception {
        File partial = new File(output.getParentFile(),
            "." + output.getName() + ".partial-" + UUID.randomUUID());
        Files.write(partial.toPath(), bytes, StandardOpenOption.CREATE_NEW,
            StandardOpenOption.WRITE);
        force(partial);
        return partial;
    }

    private static void publishPair(
            File output, byte[] outputBytes, File ready, byte[] readyBytes) throws Exception {
        File stagedOutput = null;
        File stagedReady = null;
        boolean outputPublished = false;
        try {
            stagedOutput = stage(output, outputBytes);
            stagedReady = stage(ready, readyBytes);
            Files.move(stagedOutput.toPath(), output.toPath(), StandardCopyOption.ATOMIC_MOVE);
            stagedOutput = null;
            outputPublished = true;
            Files.move(stagedReady.toPath(), ready.toPath(), StandardCopyOption.ATOMIC_MOVE);
            stagedReady = null;
        }
        catch (Exception error) {
            if (outputPublished && output.isFile() &&
                    sha256(Files.readAllBytes(output.toPath())).equals(sha256(outputBytes))) {
                Files.delete(output.toPath());
            }
            throw error;
        }
        finally {
            if (stagedOutput != null) {
                Files.deleteIfExists(stagedOutput.toPath());
            }
            if (stagedReady != null) {
                Files.deleteIfExists(stagedReady.toPath());
            }
        }
    }

    private byte[] buildOutput(String mode, String state) throws Exception {
        StringBuilder output = new StringBuilder();
        output.append("address\tmode\tstate\tname\tnameSource\tsigSource\tsignature\t")
            .append("bodyBytes\tbodySha256\tinstructionCount\tcommentBytes\tcommentSha256\t")
            .append("tags\ttagsSha256\n");
        for (Target target : TARGETS) {
            Function function = exactFunction(target);
            String comment = nullable(function.getComment());
            String tagText = String.join(",", tags(function));
            output.append(target.address).append('\t').append(mode).append('\t')
                .append(state).append('\t').append(function.getName()).append('\t')
                .append(function.getSymbol().getSource()).append('\t')
                .append(function.getSignatureSource()).append('\t')
                .append(function.getSignature().getPrototypeString(true)).append('\t')
                .append(function.getBody().getNumAddresses()).append('\t')
                .append(bodyBytesSha256(function.getBody())).append('\t')
                .append(exactInstructionCount(function.getBody(), target.address)).append('\t')
                .append(comment.getBytes(StandardCharsets.UTF_8).length).append('\t')
                .append(sha256(comment)).append('\t').append(tagText).append('\t')
                .append(sha256(tagText)).append('\n');
        }
        return output.toString().getBytes(StandardCharsets.UTF_8);
    }

    private byte[] buildReady(
            String mode, String state, File tool, byte[] toolBytes,
            File inspection, File evidence,
            File output, byte[] outputBytes, boolean commitRequested,
            boolean nestedEndReturnedCommitted) throws Exception {
        StringBuilder ready = new StringBuilder();
        ready.append("{\n");
        ready.append("  \"schema\": \"").append(SCHEMA).append("\",\n");
        ready.append("  \"completedAtUtc\": \"").append(json(Instant.now().toString()))
            .append("\",\n");
        ready.append("  \"mode\": \"").append(mode).append("\",\n");
        ready.append("  \"state\": \"").append(state).append("\",\n");
        ready.append("  \"tool\": {\"path\": \"").append(json(tool.getCanonicalPath()))
            .append("\", \"bytes\": ").append(toolBytes.length)
            .append(", \"sha256\": \"").append(sha256(toolBytes)).append("\"},\n");
        ready.append("  \"inspection\": {\"path\": \"").append(json(inspection.getCanonicalPath()))
            .append("\", \"bytes\": ").append(INSPECTION_BYTES)
            .append(", \"sha256\": \"").append(INSPECTION_SHA256).append("\"},\n");
        ready.append("  \"evidence\": {\"path\": \"").append(json(evidence.getCanonicalPath()))
            .append("\", \"bytes\": ").append(EVIDENCE_BYTES)
            .append(", \"sha256\": \"").append(EVIDENCE_SHA256).append("\"},\n");
        ready.append("  \"program\": {\"name\": \"").append(PROGRAM_NAME)
            .append("\", \"md5\": \"").append(PROGRAM_MD5)
            .append("\", \"sha256\": \"").append(PROGRAM_SHA256)
            .append("\", \"functions\": ").append(FUNCTION_COUNT)
            .append(", \"instructions\": ").append(INSTRUCTION_COUNT).append("},\n");
        ready.append("  \"targets\": 4,\n");
        ready.append("  \"output\": {\"path\": \"").append(json(output.getCanonicalPath()))
            .append("\", \"bytes\": ").append(outputBytes.length)
            .append(", \"sha256\": \"").append(sha256(outputBytes)).append("\"},\n");
        ready.append("  \"mutation\": {\"namesChanged\": 4, \"displayedSignaturesChanged\": 4, ")
            .append("\"commentsChanged\": 4, \"tagSetsChanged\": 4, ")
            .append("\"boundariesChanged\": 0, \"bytesChanged\": 0, ")
            .append("\"instructionsChanged\": 0, \"dataUnitsChanged\": 0, ")
            .append("\"referencesChanged\": 0},\n");
        ready.append("  \"commitRequested\": ").append(commitRequested).append(",\n");
        ready.append("  \"nestedEndReturnedCommitted\": ")
            .append(nestedEndReturnedCommitted).append(",\n");
        ready.append("  \"loadedStateVerified\": ").append(mode.equals("readback")).append(",\n");
        ready.append("  \"descriptiveNamesDemoted\": true,\n");
        ready.append("  \"originalSymbolsRecovered\": false,\n");
        ready.append("  \"runtimeSemanticsAuthorized\": false,\n");
        ready.append("  \"rebuildReadyAuthorized\": false,\n");
        ready.append("  \"liveMutationAuthorized\": false,\n");
        ready.append("  \"authorityBoundary\": ")
            .append("\"requires_external_two_replica_and_separate_live_readback\"\n");
        ready.append("}\n");
        return ready.toString().getBytes(StandardCharsets.UTF_8);
    }

    private void validateOuter(long expectedId, String phase) {
        TransactionInfo info = currentProgram.getCurrentTransactionInfo();
        require(info != null, phase + " outer transaction is absent");
        requireEqual("transaction", phase + " id", expectedId, info.getID());
        requireEqual("transaction", phase + " status",
            TransactionInfo.Status.NOT_DONE, info.getStatus());
        requireEqual("transaction", phase + " terminated", false,
            currentProgram.hasTerminatedTransaction());
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        if (args == null || args.length != 5) {
            throw new IllegalArgumentException(
                "usage: <inspection-target.tsv> <evidence-NOTE.md> <out.tsv> <out.ready.json> " +
                "<dry|probe-after-one|probe-post-inner|apply|readback>");
        }
        String mode = args[4].toLowerCase(Locale.ROOT);
        require(Arrays.asList("dry", "probe-after-one", "probe-post-inner", "apply", "readback")
            .contains(mode), "unsupported mode: " + mode);

        byte[] toolBytes;
        try (InputStream stream = getSourceFile().getInputStream()) {
            toolBytes = stream.readAllBytes();
        }
        File tool = new File(getSourceFile().getCanonicalPath()).getCanonicalFile();
        requireEqual("tool", "directory", "tools", tool.getParentFile().getName());
        File repositoryRoot = tool.getParentFile().getParentFile().getCanonicalFile();
        File inspection = requireEvidence(repositoryRoot, INSPECTION_RELATIVE, new File(args[0]),
            INSPECTION_BYTES, INSPECTION_SHA256);
        File evidence = requireEvidence(repositoryRoot, EVIDENCE_RELATIVE, new File(args[1]),
            EVIDENCE_BYTES, EVIDENCE_SHA256);
        File output = requireNewOutput(args[2], "output TSV");
        File ready = requireNewOutput(args[3], "READY receipt");
        requireEqual("output", "distinct paths", false, output.equals(ready));
        requireEqual("output", "shared parent", output.getParentFile(), ready.getParentFile());

        if (mode.equals("readback")) {
            validatePost();
            byte[] outputBytes = buildOutput(mode, "POST");
            byte[] readyBytes = buildReady(mode, "POST", tool, toolBytes, inspection, evidence,
                output, outputBytes, false, false);
            publishPair(output, outputBytes, ready, readyBytes);
            println("HUD_ROUTE_DEMOTION_READBACK_COMPLETE targets=4 loaded_state_verified=true");
            return;
        }

        validatePre();
        println("HUD_ROUTE_DEMOTION_PREFLIGHT_OK targets=4 functions=" + FUNCTION_COUNT +
            " instructions=" + INSTRUCTION_COUNT + " tool_sha256=" + sha256(toolBytes));
        if (mode.equals("dry")) {
            byte[] outputBytes = buildOutput(mode, "PRE");
            byte[] readyBytes = buildReady(mode, "PRE", tool, toolBytes, inspection, evidence,
                output, outputBytes, false, false);
            publishPair(output, outputBytes, ready, readyBytes);
            println("HUD_ROUTE_DEMOTION_DRY_COMPLETE targets=4 mutations=0");
            return;
        }

        List<PreState> preStates = new ArrayList<>();
        for (Target target : TARGETS) {
            preStates.add(capturePre(target));
        }
        TransactionInfo outer = currentProgram.getCurrentTransactionInfo();
        require(outer != null && !currentProgram.hasTerminatedTransaction(),
            "mutation requires a healthy outer Ghidra transaction");
        long outerId = outer.getID();
        validateOuter(outerId, "before mutation");
        int transaction = currentProgram.startTransaction("Demote four HUD route descriptive names");
        boolean transactionEnded = false;
        boolean commitRequested = false;
        boolean nestedCommitted = false;
        try {
            for (int index = 0; index < TARGETS.size(); index++) {
                monitor.checkCancelled();
                applyPost(TARGETS.get(index));
                if (mode.equals("probe-after-one") && index == 0) {
                    println("HUD_ROUTE_DEMOTION_FORCED_AFTER_ONE_FAILURE rollback_required=true");
                    throw new IllegalStateException(
                        "intentional HUD route-demotion after-one rollback probe");
                }
            }
            commitRequested = mode.equals("apply") || mode.equals("probe-post-inner");
            nestedCommitted = currentProgram.endTransaction(transaction, commitRequested);
            transactionEnded = true;
            requireEqual("transaction", "nested end committed", false, nestedCommitted);
            validateOuter(outerId, "after nested end");

            if (mode.equals("probe-post-inner")) {
                int restore = currentProgram.startTransaction(
                    "Restore HUD route PRE metadata after post-inner probe");
                boolean restoreEnded = false;
                try {
                    for (int index = TARGETS.size() - 1; index >= 0; index--) {
                        restorePre(TARGETS.get(index), preStates.get(index));
                    }
                    boolean restoreCommitted = currentProgram.endTransaction(restore, true);
                    restoreEnded = true;
                    requireEqual("transaction", "restore nested end committed", false, restoreCommitted);
                }
                finally {
                    if (!restoreEnded) {
                        currentProgram.endTransaction(restore, false);
                    }
                }
                validatePre();
                validateOuter(outerId, "after compensating PRE restore");
                println("HUD_ROUTE_DEMOTION_COMPENSATING_PRE_RESTORE_COMPLETE targets=4");
                println("HUD_ROUTE_DEMOTION_FORCED_POST_INNER_FAILURE pre_restored=true");
                throw new IllegalStateException(
                    "intentional HUD route-demotion post-inner rollback probe");
            }

            require(mode.equals("apply"), "unexpected successful mutation mode: " + mode);
            validatePost();
            byte[] outputBytes = buildOutput(mode, "POST");
            byte[] readyBytes = buildReady(mode, "POST", tool, toolBytes, inspection, evidence,
                output, outputBytes, true, nestedCommitted);
            publishPair(output, outputBytes, ready, readyBytes);
            println("HUD_ROUTE_DEMOTION_APPLY_COMPLETE targets=4 reopen_verification_required=true");
        }
        catch (Exception error) {
            if (!transactionEnded) {
                try {
                    nestedCommitted = currentProgram.endTransaction(transaction, false);
                    transactionEnded = true;
                }
                catch (Exception rollbackError) {
                    error.addSuppressed(rollbackError);
                }
            }
            println("HUD_ROUTE_DEMOTION_MUTATION_TAINTED mode=" + mode +
                " commit_requested=" + commitRequested +
                " nested_end_returned_committed=" + nestedCommitted);
            throw error;
        }
        finally {
            if (!transactionEnded) {
                currentProgram.endTransaction(transaction, false);
            }
        }
    }
}
