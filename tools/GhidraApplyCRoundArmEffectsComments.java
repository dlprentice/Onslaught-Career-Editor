//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.framework.model.TransactionInfo;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressRange;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.address.AddressSetView;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.FunctionIterator;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.listing.InstructionIterator;
import ghidra.program.model.mem.Memory;
import ghidra.program.model.mem.MemoryBlock;

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
import java.util.Comparator;
import java.util.List;
import java.util.Locale;
import java.util.UUID;

/**
 * Append the Generation 23 bounded CRound arm-effects evidence to exactly the
 * twelve retail functions that were witnessed in the selected invocations.
 *
 * This is intentionally not a generic comment importer. It is bound to the
 * pristine retail program, exact current Ghidra envelopes and metadata
 * preimages, and the reviewed proof/refutation/adjudication/campaign lineage.
 * It never changes a name, signature, boundary, instruction, datum, reference,
 * tag, or repeatable comment.
 *
 * Modes:
 *   dry              validate the exact PRE state without mutation;
 *   probe-after-one  append one comment and force outer rollback;
 *   probe-post-inner append all comments, restore exact PRE comments, fail;
 *   apply            append all comments atomically;
 *   readback         require the exact loaded POST state without mutation.
 */
public class GhidraApplyCRoundArmEffectsComments extends GhidraScript {
    private static final String SCHEMA =
        "bea.ghidra.cround-arm-effects-comments.v1";
    private static final String PROGRAM_NAME = "BEA.exe";
    private static final String PROGRAM_MD5 = "3b456964020070efe696d2cc09464a55";
    private static final String PROGRAM_SHA256 =
        "74154bfae14ddc8ecb87a0766f5bc381c7b7f1ab334ed7a753040eda1e1e7750";
    private static final String IMAGE_BASE = "00400000";
    private static final String LANGUAGE = "x86:LE:32:default";
    private static final String COMPILER_SPEC = "windows";
    private static final String MEMORY_SHA256 =
        "5398f750f1ffb59873a6ec7e1750b51d11b5b844a8fda8d4e43649b5b9e5089d";
    private static final long FUNCTION_COUNT = 8136;
    private static final long INSTRUCTION_COUNT = 549872;

    private static final String PROOF_RELATIVE =
        "local-lab/cround-handle-event-arm-effects-20260812-v1/" +
        "proof-v1/proof.ready.json";
    private static final long PROOF_BYTES = 90443;
    private static final String PROOF_SHA256 =
        "974cbb86f8857d44369aef03e72b61656960147b7161466c4823e8d0c6ee867d";
    private static final String OVERLAY_RELATIVE =
        "local-lab/cround-handle-event-arm-effects-20260812-v1/" +
        "runtime-overlay-v1/runtime-contracts.ready.json";
    private static final long OVERLAY_BYTES = 11552;
    private static final String OVERLAY_SHA256 =
        "341834e47349dc8e2c7097f40f9bc6d390e216d61a32b6d3a36df2d0c2983307";
    private static final String REFUTER_FINDING_RELATIVE =
        "local-lab/cround-handle-event-arm-effects-20260812-v1/" +
        "refuter-finding-v1.json";
    private static final long REFUTER_FINDING_BYTES = 10355;
    private static final String REFUTER_FINDING_SHA256 =
        "28682d68afb0c3ddc8bcc17523657650b2e0800e2f87c6880127530f4795953a";
    private static final String REFUTER_RESULT_RELATIVE =
        "local-lab/cround-handle-event-arm-effects-20260812-v1/" +
        "refuter-result-v1.json";
    private static final long REFUTER_RESULT_BYTES = 5305;
    private static final String REFUTER_RESULT_SHA256 =
        "222898ab36605d5a2c3ec5642e8572197dd74cacd8af995e69d37c6379a90e67";
    private static final String ADJUDICATION_RELATIVE =
        "local-lab/cround-handle-event-arm-effects-20260812-v1/" +
        "adjudication-v1.json";
    private static final long ADJUDICATION_BYTES = 3019;
    private static final String ADJUDICATION_SHA256 =
        "f1778fde37cdb61df8179b4a8de020909c54c4901ac7e01b5a98fe785413e17d";
    private static final String CAMPAIGN_RELATIVE =
        "local-lab/re-campaign-incident-recovery-20260808-v1/" +
        "generation-23-cround-handle-event-arm-effects-v1/campaign.ready.json";
    private static final long CAMPAIGN_BYTES = 20860;
    private static final String CAMPAIGN_SHA256 =
        "4471fdfe105340ad06c2ad28d945eb05e9bc94f002110888b164581ccf1a93fc";
    private static final String AUTHORITY_RELATIVE =
        "local-lab/re-campaign-incident-recovery-20260808-v1/" +
        "generation-23-cround-handle-event-arm-effects-authority.ready.json";
    private static final long AUTHORITY_BYTES = 10522;
    private static final String AUTHORITY_SHA256 =
        "12509207913b0116a94c923da7fe163c47de226b7733538baea54eb31df73ba8";

    private static final String EVIDENCE_SUFFIX =
        "Gen23 READY 4471fdfe1053; proof 974cbb86f885; " +
        "refuter SURVIVED 222898ab3660. C2_BOUNDED_RUNTIME; PARTIAL_CONTRACT.";

    private static class Target {
        final String address;
        final String expectedName;
        final String expectedSignature;
        final long bodyBytes;
        final String bodyDigest;
        final long instructionCount;
        final long preCommentBytes;
        final String preCommentSha256;
        final String annotation;

        Target(
                String address, String expectedName, String expectedSignature,
                long bodyBytes, String bodyDigest, long instructionCount,
                long preCommentBytes, String preCommentSha256, String annotation) {
            this.address = address;
            this.expectedName = expectedName;
            this.expectedSignature = expectedSignature;
            this.bodyBytes = bodyBytes;
            this.bodyDigest = bodyDigest;
            this.instructionCount = instructionCount;
            this.preCommentBytes = preCommentBytes;
            this.preCommentSha256 = preCommentSha256;
            this.annotation = annotation + " " + EVIDENCE_SUFFIX;
        }

        String suffix() {
            return "\n\n" + annotation;
        }
    }

    private static final List<Target> TARGETS = Arrays.asList(
        new Target(
            "0x004d9910", "VFuncSlot_00_004d9910",
            "void __thiscall VFuncSlot_00_004d9910(void * this, void * event_record)",
            1078, "5b0e5818d0c66e68b43e7c3a1ca900b63e18323899045b044641df99af629864", 296,
            962, "770cdfe4a114e23dada105b130607b34fb12c55c556fbee2bca5cdaf3ee93b55",
            "Generation 23 bounded runtime addendum: 2,555 strict-CRound slot-0 " +
            "call/entry pairs across two sealed pristine-retail TTD sessions " +
            "resolved one fixed switch arm per observed invocation. Five selected " +
            "invocations establish exact receiver-write pairs for default/3000 " +
            "(43, gap-free), event 4003 (4, gap-free), event 4001 (9, witnessed " +
            "with 19 nontrivial gaps and 9 continuity breaks), event 4000 Level " +
            "521 (12, witnessed with 100 gaps and 8 breaks), and event 4000 Level " +
            "512 (16, witnessed with 30 gaps and 17 breaks). The two event-4000 " +
            "samples share eleven receiver offsets but differ in writers, values, " +
            "and order; no universal event-4000 sequence is claimed. External " +
            "writes/effects, events 2000/4002, CMissile placement, field meanings, " +
            "source spelling, broader populations, and direct rebuild parity remain open."),
        new Target(
            "0x004015e0", "CActor__Move",
            "void __fastcall CActor__Move(void * this)",
            794, "458d403f7a2baf5539b670e8aa8c4c23daf90d3fe0a737b063c9d4ae600f5696", 242,
            190, "6c9359f2a748e6692f210b405f24ec11447c0a778fdf516451a695ae096ba866",
            "Generation 23 bounded runtime addendum: the selected strict-CRound " +
            "default/3000 invocation was gap-free and attributes exact receiver " +
            "writes/readbacks in this body as part of 43 pairs shared with " +
            "CActor__HandleEvent and slot 66. This proves only that invocation and " +
            "its observed order, not universal CActor movement behavior."),
        new Target(
            "0x004019e0", "CActor__HandleEvent",
            "void __thiscall CActor__HandleEvent(void * this, void * event)",
            367, "34f37e9a08814d664dc06b4d6c44bf75165363e6727b3845c58bf3ecd01a0b40", 117,
            183, "3ad95dcaba96141d1baa65f520d91052c7a6ec9d8100a17a8280650af2141fb7",
            "Generation 23 bounded runtime addendum: in the selected gap-free " +
            "strict-CRound default/3000 path, writer PCs 0x00401B04 and 0x00401B22 " +
            "produced two exact receiver-write pairs at offset +0xDC. This is a " +
            "single selected invocation, not a universal scheduler or event claim."),
        new Target(
            "0x004d8e40", "VFuncSlot_66_004d8e40",
            "void __fastcall VFuncSlot_66_004d8e40(void * this)",
            2757, "360d3874fca5325fe7f880bd2afd7d2f914adf67fd9088fdf0bfc9e8e4617d39", 826,
            919, "a838bb1033aadbc427f9bbfc7c3f5b362400d71b58fee4a240351c7e7567a441",
            "Generation 23 bounded runtime addendum: the selected strict-CRound " +
            "default/3000 invocation was gap-free and attributes exact receiver " +
            "writes/readbacks in this body as part of 43 pairs shared with " +
            "CActor__Move and CActor__HandleEvent. This does not establish complete " +
            "slot-66 effects, CMissile behavior, or a universal write sequence."),
        new Target(
            "0x004dac90", "CRound__SelectBestTargetReaderAndSyncAimState",
            "void __thiscall CRound__SelectBestTargetReaderAndSyncAimState(void * this, void * eventPayload, void * unusedContext)",
            852, "794c414b6fb601554307cbf1e598e3dba129e11e7f64d3aa8d1c02a7f150933e", 256,
            593, "e1206ac1eba7a826a04156e8012cbb0c3655a3f3a132dc79de5a9eed995a34b7",
            "Generation 23 bounded runtime addendum: the selected strict-CRound " +
            "event-4003 invocation was gap-free and writer PCs 0x004DAF3C, " +
            "0x004DAF41, 0x004DAF47, and 0x004DAF85 produced four exact receiver " +
            "writes at offsets +0x108, +0x10C, +0x110, and +0x114. Values, field " +
            "meanings, external effects, and other invocations remain unproven."),
        new Target(
            "0x004d9f30", "CRound__UpdateEffectTransformByMode_004d9f30",
            "void __thiscall CRound__UpdateEffectTransformByMode_004d9f30(void * this, int effectMode, void * context, void * targetOrOwner)",
            1779, "4ab7ef0fb859c0ce67cedb763d88c40c45e263cac979b79965a33359572f333f", 502,
            644, "d326047ff5c7fbb271048a9ebf3e087079224ba18fbab7667ae6f7fbc73ae81a",
            "Generation 23 bounded runtime addendum: selected event-4000 and " +
            "event-4001 invocations attribute exact receiver writes/readbacks in " +
            "this body at offsets +0x7C, +0x80, +0x84, +0x88, and +0xE4. All three " +
            "lanes cross fully ledgered continuity barriers; external particle, " +
            "allocation, container, event-manager, and transitive effects were not watched."),
        new Target(
            "0x004f43d0", "CComplexThing__AddShutdownEvent",
            "void __fastcall CComplexThing__AddShutdownEvent(void * this)",
            95, "af1598763ba18f9ac46166e331ef7d81e28cd4405161fdcbfbe0aac21c589457", 34,
            507, "e1b36692ea6ecf7714dafefad16e34fe652f525a1002c635b3de80722aaea20c",
            "Generation 23 bounded runtime addendum: in the selected strict-CRound " +
            "event-4001 invocation, writer PC 0x004F441B changed the receiver word " +
            "at +0x2C from 6 to 7 after CComplexThing__StartDieProcess changed it " +
            "from 2 to 6. The lane has 19 nontrivial gaps and 9 continuity breaks; " +
            "event-2000 and external event-manager effects are not claimed."),
        new Target(
            "0x004f4430", "CComplexThing__StartDieProcess",
            "int __fastcall CComplexThing__StartDieProcess(void * this)",
            45, "9387bae09431eb4f5f5ec7607d8fb684e810af4a6285d2bd1cf0a5d1df274bcf", 19,
            434, "e853bacccd04b13356582410349644c0a3f94f6c94fb28c7263817724dc00605",
            "Generation 23 bounded runtime addendum: in the selected strict-CRound " +
            "event-4001 invocation, writer PC 0x004F443D changed the receiver word " +
            "at +0x2C from 2 to 6 before CComplexThing__AddShutdownEvent changed it " +
            "from 6 to 7. The lane has 19 nontrivial gaps and 9 continuity breaks; " +
            "unwatched script and transitive effects remain open."),
        new Target(
            "0x004cb3d0", "CParticleManager__CreateEffect",
            "void __stdcall CParticleManager__CreateEffect(void * manager, void * out_handle_slot, float spawn_x, float spawn_y, float spawn_z, float spawn_w, int looping_flag, int force_allocate)",
            485, "e5ee99ebcc608bf6482968445a5bb1dedea1cf6296a0d9cadd3b6396b1772b5f", 132,
            719, "b5b1892c746636aac6f0b5e5d5cf552c08b1d780adc6ccaf4b955f982a6f8ad6",
            "Generation 23 bounded runtime addendum: writer PC 0x004CB525 " +
            "produced an exact receiver write at +0xE4 in each selected event-4000 " +
            "invocation. Both lanes cross ledgered continuity barriers; this proves " +
            "the bounded receiver-slot write only, not allocation, particle lifetime, " +
            "external memory effects, or general CreateEffect behavior."),
        new Target(
            "0x004f3cb0", "CThing__MoveTo",
            "void __thiscall CThing__MoveTo(void * this, void * pos)",
            46, "4c01dda981fd26ad50e075b12e74e4c84d52a0df8d8e898fd3eeed17e056e3f0", 17,
            402, "b072a1a11ac191e18f13c6740020dba66fbd18d77db962dc517d66058a39ff10",
            "Generation 23 bounded runtime addendum: in the selected Level-512 " +
            "strict-CRound event-4000 invocation, writer PCs 0x004F3CBD, " +
            "0x004F3CC2, 0x004F3CC8, and 0x004F3CD1 produced four exact receiver " +
            "writes at +0x1C, +0x20, +0x24, and +0x28. The invocation has 30 " +
            "nontrivial gaps and 17 continuity breaks; broader MoveTo behavior remains open."),
        new Target(
            "0x00404150", "CAnimal__SetVector7CFromInput",
            "void __thiscall CAnimal__SetVector7CFromInput(void * this, void * inVector)",
            32, "6eb2b5954cdd64c481c16057b73117b25a67cffc370d0ca112b577cf2a2620b5", 11,
            430, "e15e67f78abf56c3c3d1380103eaf12d7e32acbc401aac14cf44fa50c31b8c92",
            "Generation 23 bounded runtime addendum: in the selected Level-512 " +
            "strict-CRound event-4000 invocation, writer PCs 0x00404159, " +
            "0x0040415E, 0x00404164, and 0x0040416A produced four exact receiver " +
            "writes at +0x7C, +0x80, +0x84, and +0x88. The invocation has 30 " +
            "nontrivial gaps and 17 continuity breaks; vector meaning and broader behavior remain open."),
        new Target(
            "0x004d8ae0", "VFuncSlot_39_004d8ae0",
            "void __thiscall VFuncSlot_39_004d8ae0(void * this, void * other_thing, void * collision_report)",
            734, "7ceb410d8ad4bbc1df16f1f5e02320ea3512e621ede4dd325ce45a85f65586f1", 228,
            925, "81b4640377e5ebc3bfbd70faf4009e496c93b5f25c282a58d6325465a0befc76",
            "Generation 23 bounded runtime addendum: in the selected Level-512 " +
            "strict-CRound event-4000 invocation, writer PC 0x004D8D58 changed " +
            "one receiver byte at +0x2C. The invocation has 30 nontrivial gaps and " +
            "17 continuity breaks; exact hit/collision semantics, CMissile placement, " +
            "and other paths remain unproven."));

    private static void require(boolean condition, String message) {
        if (!condition) {
            throw new IllegalStateException(message);
        }
    }

    private static void requireEqual(
            String label, String field, Object expected, Object actual) {
        if (expected == null ? actual != null : !expected.equals(actual)) {
            throw new IllegalStateException(label + " " + field +
                " differs expected=" + expected + " actual=" + actual);
        }
    }

    private static String nullable(String value) {
        return value == null ? "" : value;
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

    private Function validateCommon(Target target) throws Exception {
        Address entry = toAddr(target.address);
        Function function = getFunctionAt(entry);
        require(function != null && function.getEntryPoint().equals(entry),
            "exact function is absent at " + target.address);
        requireEqual(target.address, "name", target.expectedName, function.getName());
        requireEqual(target.address, "signature", target.expectedSignature,
            function.getSignature().getPrototypeString(true));
        requireEqual(target.address, "body bytes", target.bodyBytes,
            function.getBody().getNumAddresses());
        requireEqual(target.address, "body digest", target.bodyDigest,
            bodyDigest(function.getBody()));
        requireEqual(target.address, "instruction count", target.instructionCount,
            exactInstructionCount(function.getBody(), target.address));
        return function;
    }

    private String requirePreComment(Target target, String comment) throws Exception {
        byte[] bytes = nullable(comment).getBytes(StandardCharsets.UTF_8);
        requireEqual(target.address, "PRE comment bytes", target.preCommentBytes,
            (long) bytes.length);
        requireEqual(target.address, "PRE comment SHA-256", target.preCommentSha256,
            sha256(bytes));
        require(!nullable(comment).endsWith(target.suffix()),
            target.address + " already contains the Generation 23 suffix");
        return nullable(comment);
    }

    private String requirePostComment(Target target, String comment) throws Exception {
        String value = nullable(comment);
        require(value.endsWith(target.suffix()),
            target.address + " POST comment suffix differs");
        String prefix = value.substring(0, value.length() - target.suffix().length());
        requirePreComment(target, prefix);
        return prefix;
    }

    private void validatePre() throws Exception {
        validateProgram();
        for (Target target : TARGETS) {
            requirePreComment(target, validateCommon(target).getComment());
        }
    }

    private void validatePost() throws Exception {
        validateProgram();
        for (Target target : TARGETS) {
            requirePostComment(target, validateCommon(target).getComment());
        }
    }

    private void applyPost() throws Exception {
        for (Target target : TARGETS) {
            Function function = validateCommon(target);
            String pre = requirePreComment(target, function.getComment());
            function.setComment(pre + target.suffix());
            requirePostComment(target, function.getComment());
        }
        validatePost();
    }

    private void restorePre() throws Exception {
        for (Target target : TARGETS) {
            Function function = validateCommon(target);
            String pre = requirePostComment(target, function.getComment());
            function.setComment(pre);
            requirePreComment(target, function.getComment());
        }
        validatePre();
    }

    private static File requireEvidence(
            File repositoryRoot, String relative, File supplied,
            long expectedBytes, String expectedSha256) throws Exception {
        File expected = new File(repositoryRoot, relative).getCanonicalFile();
        File actual = supplied.getCanonicalFile();
        requireEqual(relative, "canonical path", expected, actual);
        require(actual.isFile(), "evidence is absent: " + actual);
        byte[] bytes = Files.readAllBytes(actual.toPath());
        requireEqual(relative, "bytes", expectedBytes, (long) bytes.length);
        requireEqual(relative, "SHA-256", expectedSha256, sha256(bytes));
        return actual;
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
            if (stagedOutput != null) Files.deleteIfExists(stagedOutput.toPath());
            if (stagedReady != null) Files.deleteIfExists(stagedReady.toPath());
        }
    }

    private byte[] buildOutput(String mode, String state) throws Exception {
        StringBuilder output = new StringBuilder();
        output.append("address\tmode\tstate\tname\tsignature\tbodyBytes\tbodyDigest\t")
            .append("instructionCount\tcommentBytes\tcommentSha256\tannotationSha256\n");
        for (Target target : TARGETS) {
            Function function = validateCommon(target);
            String comment = nullable(function.getComment());
            output.append(target.address).append('\t').append(mode).append('\t')
                .append(state).append('\t').append(function.getName()).append('\t')
                .append(function.getSignature().getPrototypeString(true)).append('\t')
                .append(target.bodyBytes).append('\t').append(target.bodyDigest).append('\t')
                .append(target.instructionCount).append('\t')
                .append(comment.getBytes(StandardCharsets.UTF_8).length).append('\t')
                .append(sha256(comment)).append('\t').append(sha256(target.annotation)).append('\n');
        }
        return output.toString().getBytes(StandardCharsets.UTF_8);
    }

    private static void appendStamp(
            StringBuilder ready, String label, File file,
            String expectedSha, boolean comma) throws Exception {
        byte[] bytes = Files.readAllBytes(file.toPath());
        requireEqual(label, "receipt SHA-256", expectedSha, sha256(bytes));
        ready.append("    \"").append(label).append("\": {\"path\": \"")
            .append(json(file.getCanonicalPath())).append("\", \"bytes\": ")
            .append(bytes.length).append(", \"sha256\": \"").append(expectedSha)
            .append("\"}").append(comma ? "," : "").append("\n");
    }

    private byte[] buildReady(
            String mode, String state, File tool, byte[] toolBytes,
            List<File> evidence, File output, byte[] outputBytes,
            boolean commitRequested, boolean nestedEndReturnedCommitted) throws Exception {
        StringBuilder ready = new StringBuilder();
        ready.append("{\n");
        ready.append("  \"schema\": \"").append(SCHEMA).append("\",\n");
        ready.append("  \"completedAtUtc\": \"").append(Instant.now()).append("\",\n");
        ready.append("  \"mode\": \"").append(mode).append("\",\n");
        ready.append("  \"state\": \"").append(state).append("\",\n");
        ready.append("  \"tool\": {\"path\": \"").append(json(tool.getCanonicalPath()))
            .append("\", \"bytes\": ").append(toolBytes.length)
            .append(", \"sha256\": \"").append(sha256(toolBytes)).append("\"},\n");
        ready.append("  \"program\": {\"name\": \"").append(PROGRAM_NAME)
            .append("\", \"executableSha256\": \"").append(PROGRAM_SHA256)
            .append("\", \"memorySha256\": \"").append(MEMORY_SHA256)
            .append("\", \"functions\": ").append(FUNCTION_COUNT)
            .append(", \"instructions\": ").append(INSTRUCTION_COUNT).append("},\n");
        ready.append("  \"evidence\": {\n");
        appendStamp(ready, "proof", evidence.get(0), PROOF_SHA256, true);
        appendStamp(ready, "runtimeOverlay", evidence.get(1), OVERLAY_SHA256, true);
        appendStamp(ready, "refuterFinding", evidence.get(2), REFUTER_FINDING_SHA256, true);
        appendStamp(ready, "refuterResult", evidence.get(3), REFUTER_RESULT_SHA256, true);
        appendStamp(ready, "adjudication", evidence.get(4), ADJUDICATION_SHA256, true);
        appendStamp(ready, "generation23", evidence.get(5), CAMPAIGN_SHA256, true);
        appendStamp(ready, "generation23Authority", evidence.get(6), AUTHORITY_SHA256, false);
        ready.append("  },\n");
        ready.append("  \"output\": {\"path\": \"").append(json(output.getCanonicalPath()))
            .append("\", \"bytes\": ").append(outputBytes.length)
            .append(", \"sha256\": \"").append(sha256(outputBytes)).append("\"},\n");
        ready.append("  \"mutation\": {\"targetComments\": ").append(TARGETS.size())
            .append(", \"namesChanged\": 0, \"signaturesChanged\": 0, ")
            .append("\"boundariesChanged\": 0, \"bytesChanged\": 0, ")
            .append("\"instructionsChanged\": 0, \"dataUnitsChanged\": 0, ")
            .append("\"referencesChanged\": 0},\n");
        ready.append("  \"commitRequested\": ").append(commitRequested).append(",\n");
        ready.append("  \"nestedEndReturnedCommitted\": ")
            .append(nestedEndReturnedCommitted).append(",\n");
        ready.append("  \"loadedStateVerified\": ").append(mode.equals("readback"))
            .append(",\n");
        ready.append("  \"authorityBoundary\": ")
            .append("\"requires_two_independent_scratch_replicas_and_separate_live_readback\",\n");
        ready.append("  \"limitations\": [\n")
            .append("    \"Only five selected invocations in two sealed sessions are described.\",\n")
            .append("    \"Only default/3000 and event 4003 are gap-free.\",\n")
            .append("    \"External writes/effects, event 2000, event 4002, CMissile placement, field meanings, source spelling, and direct rebuild parity remain open.\",\n")
            .append("    \"The apply receipt precedes outer Ghidra save and is not live authority without fresh-process readback.\"\n")
            .append("  ]\n");
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
        if (args == null || args.length != 10) {
            throw new IllegalArgumentException(
                "usage: <proof.ready.json> <overlay.ready.json> <refuter-finding.json> " +
                "<refuter-result.json> <adjudication.json> <campaign.ready.json> " +
                "<authority.ready.json> <out.tsv> <out.ready.json> " +
                "<dry|probe-after-one|probe-post-inner|apply|readback>");
        }
        String mode = args[9].toLowerCase(Locale.ROOT);
        require(Arrays.asList("dry", "probe-after-one", "probe-post-inner", "apply", "readback")
            .contains(mode), "unsupported mode: " + mode);

        byte[] toolBytes;
        try (InputStream stream = getSourceFile().getInputStream()) {
            toolBytes = stream.readAllBytes();
        }
        File tool = new File(getSourceFile().getCanonicalPath()).getCanonicalFile();
        requireEqual("tool", "directory", "tools", tool.getParentFile().getName());
        File repositoryRoot = tool.getParentFile().getParentFile().getCanonicalFile();
        List<File> evidence = Arrays.asList(
            requireEvidence(repositoryRoot, PROOF_RELATIVE, new File(args[0]),
                PROOF_BYTES, PROOF_SHA256),
            requireEvidence(repositoryRoot, OVERLAY_RELATIVE, new File(args[1]),
                OVERLAY_BYTES, OVERLAY_SHA256),
            requireEvidence(repositoryRoot, REFUTER_FINDING_RELATIVE, new File(args[2]),
                REFUTER_FINDING_BYTES, REFUTER_FINDING_SHA256),
            requireEvidence(repositoryRoot, REFUTER_RESULT_RELATIVE, new File(args[3]),
                REFUTER_RESULT_BYTES, REFUTER_RESULT_SHA256),
            requireEvidence(repositoryRoot, ADJUDICATION_RELATIVE, new File(args[4]),
                ADJUDICATION_BYTES, ADJUDICATION_SHA256),
            requireEvidence(repositoryRoot, CAMPAIGN_RELATIVE, new File(args[5]),
                CAMPAIGN_BYTES, CAMPAIGN_SHA256),
            requireEvidence(repositoryRoot, AUTHORITY_RELATIVE, new File(args[6]),
                AUTHORITY_BYTES, AUTHORITY_SHA256));
        File output = requireNewOutput(args[7], "output TSV");
        File ready = requireNewOutput(args[8], "READY receipt");
        requireEqual("output", "distinct paths", false, output.equals(ready));
        requireEqual("output", "shared parent", output.getParentFile(), ready.getParentFile());

        if (mode.equals("readback")) {
            validatePost();
            byte[] outputBytes = buildOutput(mode, "POST");
            byte[] readyBytes = buildReady(mode, "POST", tool, toolBytes,
                evidence, output, outputBytes, false, false);
            publishPair(output, outputBytes, ready, readyBytes);
            println("CROUND_ARM_COMMENTS_READBACK_COMPLETE targets=" + TARGETS.size() +
                " loaded_state_verified=true");
            return;
        }

        validatePre();
        println("CROUND_ARM_COMMENTS_PREFLIGHT_OK targets=" + TARGETS.size() +
            " functions=" + FUNCTION_COUNT + " instructions=" + INSTRUCTION_COUNT +
            " tool_sha256=" + sha256(toolBytes));
        if (mode.equals("dry")) {
            byte[] outputBytes = buildOutput(mode, "PRE");
            byte[] readyBytes = buildReady(mode, "PRE", tool, toolBytes,
                evidence, output, outputBytes, false, false);
            publishPair(output, outputBytes, ready, readyBytes);
            println("CROUND_ARM_COMMENTS_DRY_COMPLETE targets=" + TARGETS.size() +
                " mutations=0");
            return;
        }

        TransactionInfo outer = currentProgram.getCurrentTransactionInfo();
        require(outer != null && !currentProgram.hasTerminatedTransaction(),
            "mutation requires a healthy outer Ghidra transaction");
        long outerId = outer.getID();
        validateOuter(outerId, "before mutation");
        int transaction = currentProgram.startTransaction(
            "Append Generation 23 CRound arm-effects comments");
        boolean transactionEnded = false;
        boolean commitRequested = false;
        boolean nestedCommitted = false;
        try {
            if (mode.equals("probe-after-one")) {
                Target target = TARGETS.get(0);
                Function function = validateCommon(target);
                function.setComment(requirePreComment(target, function.getComment()) + target.suffix());
                requirePostComment(target, function.getComment());
                println("CROUND_ARM_COMMENTS_FORCED_AFTER_ONE_FAILURE rollback_required=true");
                throw new IllegalStateException(
                    "intentional CRound arm-comments after-one rollback probe");
            }

            applyPost();
            commitRequested = mode.equals("apply") || mode.equals("probe-post-inner");
            nestedCommitted = currentProgram.endTransaction(transaction, commitRequested);
            transactionEnded = true;
            requireEqual("transaction", "nested end committed", false, nestedCommitted);
            validateOuter(outerId, "after nested end");

            if (mode.equals("probe-post-inner")) {
                int restore = currentProgram.startTransaction(
                    "Restore CRound arm-effects PRE comments after probe");
                boolean restoreEnded = false;
                try {
                    restorePre();
                    boolean restoreCommitted = currentProgram.endTransaction(restore, true);
                    restoreEnded = true;
                    requireEqual("transaction", "restore nested end committed",
                        false, restoreCommitted);
                }
                finally {
                    if (!restoreEnded) {
                        currentProgram.endTransaction(restore, false);
                    }
                }
                validatePre();
                validateOuter(outerId, "after compensating PRE restore");
                println("CROUND_ARM_COMMENTS_COMPENSATING_PRE_RESTORE_COMPLETE targets=" +
                    TARGETS.size());
                println("CROUND_ARM_COMMENTS_FORCED_POST_INNER_FAILURE pre_restored=true");
                throw new IllegalStateException(
                    "intentional CRound arm-comments post-inner rollback probe");
            }

            require(mode.equals("apply"), "unexpected successful mutation mode: " + mode);
            validatePost();
            byte[] outputBytes = buildOutput(mode, "POST");
            byte[] readyBytes = buildReady(mode, "POST", tool, toolBytes,
                evidence, output, outputBytes, true, nestedCommitted);
            publishPair(output, outputBytes, ready, readyBytes);
            println("CROUND_ARM_COMMENTS_APPLY_COMPLETE targets=" + TARGETS.size() +
                " reopen_verification_required=true");
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
            println("CROUND_ARM_COMMENTS_MUTATION_TAINTED mode=" + mode +
                " nested_committed=" + nestedCommitted +
                " outer_rollback_required=" + !mode.equals("probe-post-inner") +
                " recovery=" + (mode.equals("probe-post-inner") ?
                    "COMPENSATING_PRE_RESTORE_VERIFIED" : "RESTORE_VERIFIED_SCRATCH_BASE"));
            throw error;
        }
    }
}
