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
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.UUID;

/**
 * Apply the five proof-bound collision-component identity corrections.
 *
 * This is deliberately not a generic rename tool.  It accepts only the exact
 * sealed collision identity proof and the exact current 8,136-function PRE or
 * POST metadata.  It changes five names, their displayed signatures, five
 * comments, and their exact tag sets.  It never changes boundaries, bytes,
 * instructions, data, or references.
 *
 * Modes:
 *   dry              validate exact PRE and publish no mutation;
 *   probe-after-one  mutate one function, then force transaction rollback;
 *   probe-post-inner mutate all five, restore exact captured PRE metadata in
 *                    a compensating transaction, then force failure;
 *   apply            mutate all five in one nested transaction;
 *   readback         require exact loaded POST without mutation.
 */
public class GhidraApplyCollisionComponentIdentity extends GhidraScript {
    private static final String SCHEMA = "bea.ghidra.collision-component-identity.v1";
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
        "local-lab/collision-component-identity-reproof-20260812-v1/proof.ready.json";
    private static final long PROOF_BYTES = 20927;
    private static final String PROOF_SHA256 =
        "63b88d3179edde082c915ac269b98ea26fd6fe3e2ab8e1315e11a0adad2e1ddb";

    private static final String DTOR_COMMENT =
        "Identity correction (2026-08-12): the retail body writes strict RTTI " +
        "CCollisionSeekingThing vtable 0x005D9608, deletes helper pointers at +0x14 " +
        "and +0x18, then shuts down the inherited monitor. Incoming destructor paths " +
        "include CCSPersistentThing, CCollisionSeekingInfantryBloke, " +
        "CCollisionSeekingRound, and CCSRay, so the prior Round-only owner was false. " +
        "The dtor_base spelling follows this database's base-destructor convention. " +
        "High-confidence static implementation identity only; exact original source " +
        "spelling, folded derived aliases, full layout, runtime teardown, and rebuild " +
        "parity remain open. Collision identity proof 63b88d3179ed.";

    private static final String RESPONSE_COMMENT =
        "Identity correction (2026-08-12): strict RTTI places this body in " +
        "CCollisionSeekingThing vtable slot 6 and reuses it through " +
        "CCSPersistentThing, CCollisionSeekingRound, " +
        "CCollisionSeekingInfantryBloke, and CCSRay. The retail body gates readiness, " +
        "applies mutual collision filters, resolves a contact, and dispatches " +
        "owner-side collision callbacks; therefore ResolveRoundCollisionResponse was " +
        "too narrow. High-confidence static base-implementation and descriptive-role " +
        "identity only; the legacy otherRound parameter label, exact source spelling, " +
        "folded aliases, every branch/field, runtime geometry, and rebuild parity " +
        "remain open. Collision identity proof 63b88d3179ed.";

    private static final String INIT_COMMENT =
        "Identity correction (2026-08-12): strict RTTI places this body in " +
        "CCSPersistentThing slot 3. Supplied CThing source allocates " +
        "CCSPersistentThing and calls virtual Init(init). The retail body calls " +
        "CCollisionSeekingThing__Init, optionally clears readiness and schedules event " +
        "3000 from mStartCollideOnNextFrame/mTimeBeforeStart, then performs the initial " +
        "neighbor scan; it performs no sound operation. High-confidence static " +
        "implementation and source-method identity only; the legacy roundConfig " +
        "parameter label, exact retail source body, runtime cadence, complete layout, " +
        "and rebuild parity remain open. Collision identity proof 63b88d3179ed.";

    private static final String SWEEP_COMMENT =
        "Identity correction (2026-08-12): strict RTTI places this body directly in " +
        "CCSPersistentThing slot 5 and reuses it in round and infantry vtables. The " +
        "seven-instruction body forwards its two arguments through the embedded " +
        "detector at this+0x24 to CHLCollisionDetector__ProcessMapWhoCollisionSweep. " +
        "CCSPersistentThing is therefore the safe base implementation owner. " +
        "High-confidence static implementation and descriptive-role identity only; " +
        "folded derived overrides at this identical address are not excluded, legacy " +
        "parameter labels are not source names, and runtime sweep behavior, complete " +
        "layout, and rebuild parity remain open. Collision identity proof 63b88d3179ed.";

    private static final String EVENT_COMMENT =
        "Identity correction (2026-08-12): strict RTTI places this body directly in " +
        "CCSPersistentThing slot 0 and reuses it in round and infantry vtables. The " +
        "event-manager source dispatches slot 0 as IListener::HandleEvent; this body " +
        "accepts event 3000 and restores readiness bit 0x400, matching the delayed-start " +
        "event armed by CCSPersistentThing__Init. High-confidence static implementation " +
        "and virtual-role identity only; folded derived overrides at this identical " +
        "address are not excluded, exact retail source body, runtime scheduling, " +
        "complete layout, and rebuild parity remain open. Collision identity proof " +
        "63b88d3179ed.";

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
                String preSignature, String postSignature,
                long bodyBytes, String bodyDigest, String bodyBytesSha256,
                long instructionCount, long preCommentBytes, String preCommentSha256,
                List<String> preTags, String postComment, List<String> postTags) {
            this.address = address;
            this.preName = preName;
            this.postName = postName;
            this.preSignature = preSignature;
            this.postSignature = postSignature;
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
            "0x004263f0", "CCollisionSeekingRound__Destructor",
            "CCollisionSeekingThing__dtor_base",
            "void __fastcall CCollisionSeekingRound__Destructor(void * this)",
            "void __fastcall CCollisionSeekingThing__dtor_base(void * this)",
            100, "21005db99300ad4864944885e7e132f47092c311bf918441f9a3710af8d666f4",
            "b3763d249257fab412f20d423661ca1ad401f0c45d20203393dc62edcded7f4b", 31,
            558, "0c5340eb07914ecc053cff3b9c5ea86a1c1355c335ad50005f999ad5c4e872ef",
            Arrays.asList("collision-seeking-round",
                "collision-seeking-round-tail-review-wave1059", "comment-hardened",
                "destructor", "monitor-shutdown", "retail-binary-evidence",
                "static-reaudit", "tag-normalized", "wave1059-readback-verified"),
            DTOR_COMMENT,
            Arrays.asList("collision-seeking", "collision-seeking-thing",
                "collision-seeking-round-tail-review-wave1059", "comment-hardened",
                "destructor", "identity-corrected", "monitor-shutdown", "owner-corrected",
                "retail-binary-evidence", "static-reaudit", "tag-normalized",
                "wave1059-readback-verified")),
        new Target(
            "0x004264a0", "CCollisionSeekingThing__ResolveRoundCollisionResponse",
            "CCollisionSeekingThing__ResolveCollisionResponse",
            "void __thiscall CCollisionSeekingThing__ResolveRoundCollisionResponse" +
                "(void * this, void * otherRound)",
            "void __thiscall CCollisionSeekingThing__ResolveCollisionResponse" +
                "(void * this, void * otherRound)",
            1105, "bb2981e7511f01d47d9c41e1f8b671f8cede7108b5a28ec8c42042331b9ccef0",
            "4aa1dd31761d87e3ed4bd32a5f722d496484c783e7cc01c410fdb116ccd28f6c", 330,
            423, "90cb46900ab8c29b049f519e72014162bab5765d65f407f154c3aabdce3672bd",
            Arrays.asList("collision-response", "collision-seeking-round",
                "collision-seeking-round-tail-review-wave1059", "comment-hardened",
                "delayed-ready-flag", "peer-collision", "retail-binary-evidence",
                "static-reaudit", "tag-normalized", "wave1059-readback-verified"),
            RESPONSE_COMMENT,
            Arrays.asList("collision-response", "collision-seeking-thing",
                "collision-seeking-round-tail-review-wave1059", "comment-hardened",
                "delayed-ready-flag", "identity-corrected", "owner-corrected",
                "peer-collision", "retail-binary-evidence", "static-reaudit",
                "tag-normalized", "wave1059-readback-verified")),
        new Target(
            "0x004269b0", "CCSPersistentThing__InitWithSound", "CCSPersistentThing__Init",
            "void __thiscall CCSPersistentThing__InitWithSound" +
                "(void * this, void * roundConfig)",
            "void __thiscall CCSPersistentThing__Init" +
                "(void * this, void * roundConfig)",
            70, "566ba611eacde225e7bbc21672b0b5537de8d3013edfa56dead81680fe2adac8",
            "bd4cf3f803c5d5a661b2d81ef96d1c2753a6ba4be722a4d1c6673ea96dedddd4", 27,
            380, "374ad3ee3c4f18ab55ccaf5a0eacac511259200582a1859bc9fa48f97c7f554a",
            Collections.emptyList(),
            INIT_COMMENT,
            Arrays.asList("collision-seeking", "comment-hardened",
                "delayed-ready-flag", "event-scheduling", "identity-corrected",
                "initial-collision-scan", "owner-corrected", "persistent-collision",
                "persistent-slot", "retail-binary-evidence", "static-reaudit")),
        new Target(
            "0x00426a00", "CCollisionSeekingRound__ProcessMapWhoCollisionSweep",
            "CCSPersistentThing__ProcessMapWhoCollisionSweep",
            "void __thiscall CCollisionSeekingRound__ProcessMapWhoCollisionSweep" +
                "(void * this, void * startOrContext, void * endOrContext)",
            "void __thiscall CCSPersistentThing__ProcessMapWhoCollisionSweep" +
                "(void * this, void * startOrContext, void * endOrContext)",
            21, "01f8d02a6e32b1785f396eae0cfa6c2a2dc60e1239edfdb0aa09d542caca8ca6",
            "3bbee0a1544633b9f917ddd44b5a4bc4864499a9042a0d21cd8038251d709424", 7,
            302, "813256d29226faf2c561fe9d9538edb9a40c68efa88ebacc31576982e344c6db",
            Arrays.asList("collision-seeking-round",
                "collision-seeking-round-tail-review-wave1059", "comment-hardened",
                "hlcollisiondetector-bridge", "mapwho-sweep", "retail-binary-evidence",
                "static-reaudit", "tag-normalized", "wave1059-readback-verified"),
            SWEEP_COMMENT,
            Arrays.asList("collision-seeking-round-tail-review-wave1059",
                "comment-hardened", "hlcollisiondetector-bridge", "identity-corrected",
                "mapwho-sweep", "owner-corrected", "persistent-collision",
                "persistent-slot", "retail-binary-evidence", "static-reaudit",
                "tag-normalized", "wave1059-readback-verified")),
        new Target(
            "0x00426a20", "CCollisionSeekingRound__MarkDelayedCollisionReady",
            "CCSPersistentThing__HandleEvent",
            "void __thiscall CCollisionSeekingRound__MarkDelayedCollisionReady" +
                "(void * this, void * event)",
            "void __thiscall CCSPersistentThing__HandleEvent" +
                "(void * this, void * event)",
            24, "34e6532e3dc7757596029d98cf76f202d843a415b4dbbff9153d8df92cd861b0",
            "0cf29c9c31fba213a38f5dfb2e4dbb21d7526f4d19fdbbcd5a64dca9ab82ea9b", 7,
            346, "07462366f96214cce6a7354813e6460f84657c3c52a9593821c8a23bf91939ae",
            Arrays.asList("collision-seeking-round",
                "collision-seeking-round-tail-review-wave1059", "comment-hardened",
                "delayed-ready-flag", "event-callback", "retail-binary-evidence",
                "static-reaudit", "tag-normalized", "wave1059-readback-verified"),
            EVENT_COMMENT,
            Arrays.asList("collision-seeking-round-tail-review-wave1059",
                "comment-hardened", "delayed-ready-flag", "event-callback",
                "event-handler", "identity-corrected", "owner-corrected",
                "persistent-collision", "persistent-slot", "retail-binary-evidence",
                "static-reaudit", "tag-normalized", "wave1059-readback-verified"))
    );

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
            String mode, String state, File tool, byte[] toolBytes, File proof,
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
        ready.append("  \"proof\": {\"path\": \"").append(json(proof.getCanonicalPath()))
            .append("\", \"bytes\": ").append(PROOF_BYTES)
            .append(", \"sha256\": \"").append(PROOF_SHA256).append("\"},\n");
        ready.append("  \"program\": {\"name\": \"").append(PROGRAM_NAME)
            .append("\", \"md5\": \"").append(PROGRAM_MD5)
            .append("\", \"sha256\": \"").append(PROGRAM_SHA256)
            .append("\", \"functions\": ").append(FUNCTION_COUNT)
            .append(", \"instructions\": ").append(INSTRUCTION_COUNT).append("},\n");
        ready.append("  \"targets\": 5,\n");
        ready.append("  \"output\": {\"path\": \"").append(json(output.getCanonicalPath()))
            .append("\", \"bytes\": ").append(outputBytes.length)
            .append(", \"sha256\": \"").append(sha256(outputBytes)).append("\"},\n");
        ready.append("  \"mutation\": {\"namesChanged\": 5, \"displayedSignaturesChanged\": 5, ")
            .append("\"commentsChanged\": 5, \"tagSetsChanged\": 5, ")
            .append("\"boundariesChanged\": 0, \"bytesChanged\": 0, ")
            .append("\"instructionsChanged\": 0, \"dataUnitsChanged\": 0, ")
            .append("\"referencesChanged\": 0},\n");
        ready.append("  \"commitRequested\": ").append(commitRequested).append(",\n");
        ready.append("  \"nestedEndReturnedCommitted\": ")
            .append(nestedEndReturnedCommitted).append(",\n");
        ready.append("  \"loadedStateVerified\": ").append(mode.equals("readback")).append(",\n");
        ready.append("  \"implementationIdentityNamesAuthorized\": true,\n");
        ready.append("  \"runtimeSemanticsAuthorized\": false,\n");
        ready.append("  \"rebuildReadyAuthorized\": false,\n");
        ready.append("  \"authorityBoundary\": ")
            .append("\"requires_verified_pre_backup_two_replicas_rollback_probes_and_separate_live_readback\"\n");
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
        if (args == null || args.length != 4) {
            throw new IllegalArgumentException(
                "usage: <proof.ready.json> <out.tsv> <out.ready.json> " +
                "<dry|probe-after-one|probe-post-inner|apply|readback>");
        }
        String mode = args[3].toLowerCase(Locale.ROOT);
        require(Arrays.asList("dry", "probe-after-one", "probe-post-inner", "apply", "readback")
            .contains(mode), "unsupported mode: " + mode);

        byte[] toolBytes;
        try (InputStream stream = getSourceFile().getInputStream()) {
            toolBytes = stream.readAllBytes();
        }
        File tool = new File(getSourceFile().getCanonicalPath()).getCanonicalFile();
        requireEqual("tool", "directory", "tools", tool.getParentFile().getName());
        File repositoryRoot = tool.getParentFile().getParentFile().getCanonicalFile();
        File proof = requireEvidence(repositoryRoot, PROOF_RELATIVE, new File(args[0]),
            PROOF_BYTES, PROOF_SHA256);
        File output = requireNewOutput(args[1], "output TSV");
        File ready = requireNewOutput(args[2], "READY receipt");
        requireEqual("output", "distinct paths", false, output.equals(ready));
        requireEqual("output", "shared parent", output.getParentFile(), ready.getParentFile());

        if (mode.equals("readback")) {
            validatePost();
            byte[] outputBytes = buildOutput(mode, "POST");
            byte[] readyBytes = buildReady(mode, "POST", tool, toolBytes, proof,
                output, outputBytes, false, false);
            publishPair(output, outputBytes, ready, readyBytes);
            println("COLLISION_COMPONENT_IDENTITY_READBACK_COMPLETE targets=5 loaded_state_verified=true");
            return;
        }

        validatePre();
        println("COLLISION_COMPONENT_IDENTITY_PREFLIGHT_OK targets=5 functions=" + FUNCTION_COUNT +
            " instructions=" + INSTRUCTION_COUNT + " tool_sha256=" + sha256(toolBytes));
        if (mode.equals("dry")) {
            byte[] outputBytes = buildOutput(mode, "PRE");
            byte[] readyBytes = buildReady(mode, "PRE", tool, toolBytes, proof,
                output, outputBytes, false, false);
            publishPair(output, outputBytes, ready, readyBytes);
            println("COLLISION_COMPONENT_IDENTITY_DRY_COMPLETE targets=5 mutations=0");
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
        int transaction = currentProgram.startTransaction("Correct five collision-component identities");
        boolean transactionEnded = false;
        boolean commitRequested = false;
        boolean nestedCommitted = false;
        try {
            for (int index = 0; index < TARGETS.size(); index++) {
                monitor.checkCancelled();
                applyPost(TARGETS.get(index));
                if (mode.equals("probe-after-one") && index == 0) {
                    println("COLLISION_COMPONENT_IDENTITY_FORCED_AFTER_ONE_FAILURE rollback_required=true");
                    throw new IllegalStateException(
                        "intentional collision-component identity after-one rollback probe");
                }
            }
            commitRequested = mode.equals("apply") || mode.equals("probe-post-inner");
            nestedCommitted = currentProgram.endTransaction(transaction, commitRequested);
            transactionEnded = true;
            requireEqual("transaction", "nested end committed", false, nestedCommitted);
            validateOuter(outerId, "after nested end");

            if (mode.equals("probe-post-inner")) {
                int restore = currentProgram.startTransaction(
                    "Restore collision-component PRE metadata after post-inner probe");
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
                println("COLLISION_COMPONENT_IDENTITY_COMPENSATING_PRE_RESTORE_COMPLETE targets=5");
                println("COLLISION_COMPONENT_IDENTITY_FORCED_POST_INNER_FAILURE pre_restored=true");
                throw new IllegalStateException(
                    "intentional collision-component identity post-inner rollback probe");
            }

            require(mode.equals("apply"), "unexpected successful mutation mode: " + mode);
            validatePost();
            byte[] outputBytes = buildOutput(mode, "POST");
            byte[] readyBytes = buildReady(mode, "POST", tool, toolBytes, proof,
                output, outputBytes, true, nestedCommitted);
            publishPair(output, outputBytes, ready, readyBytes);
            println("COLLISION_COMPONENT_IDENTITY_APPLY_COMPLETE targets=5 reopen_verification_required=true");
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
            println("COLLISION_COMPONENT_IDENTITY_MUTATION_TAINTED mode=" + mode +
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

