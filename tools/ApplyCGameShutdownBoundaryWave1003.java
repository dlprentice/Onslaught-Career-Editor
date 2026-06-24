//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCGameShutdownBoundaryWave1003 extends GhidraScript {
    private static final String ADDRESS = "0x0046c990";
    private static final String NAME = "CGame__Shutdown";
    private static final String CALLING_CONVENTION = "__fastcall";
    private static final String COMMENT =
        "Wave1003 CGame shutdown boundary recovery: recovered a missing Ghidra function object for " +
        "source-aligned CGame::Shutdown at 0x0046c990. Static evidence: DATA vtable refs 0x005dbbbc " +
        "and 0x005e50a4 point at this entry; the body stops music when CLIPARAMS.mMusic is non-zero, " +
        "calls CHud__ShutDown, GAMEINTERFACE shutdown/reset paths, particle/static-shadow/imposter/" +
        "engine/map/mesh/texture cleanup, memory-manager merge/cleanup, outro FMV handling, and console " +
        "status/command cleanup before terminal 0x0046ca6b RET. Source parity: references/Onslaught/" +
        "game.cpp:CGame::Shutdown. Static retail Ghidra evidence only; exact source-body identity, " +
        "concrete CGame/HUD/engine layouts, runtime shutdown behavior, BEA patching, and rebuild parity " +
        "remain separate proof.";
    private static final String[] TAGS = new String[] {
        "static-reaudit",
        "hud-head-render-state-review-wave1003",
        "wave1003-readback-verified",
        "retail-binary-evidence",
        "function-boundary-recovered",
        "source-parity",
        "game-lifecycle",
        "shutdown",
        "comment-hardened",
        "signature-hardened"
    };

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int created = 0;
        int wouldCreate = 0;
        int renamed = 0;
        int wouldRename = 0;
        int signatureUpdated = 0;
        int commentOnlyUpdated = 0;
        int bad = 0;
    }

    private boolean isDryRun(String mode) {
        if (mode == null || mode.trim().isEmpty()) {
            return true;
        }
        String normalized = mode.trim().toLowerCase();
        if (normalized.equals("dry") || normalized.equals("dry-run") || normalized.equals("true") || normalized.equals("1")) {
            return true;
        }
        if (normalized.equals("apply") || normalized.equals("no-dry") || normalized.equals("false") || normalized.equals("0")) {
            return false;
        }
        throw new IllegalArgumentException("Unrecognized mode: " + mode + " (use dry/apply)");
    }

    private Address addr(String addressText) {
        if (!addressText.startsWith("0x") && !addressText.startsWith("0X")) {
            addressText = "0x" + addressText;
        }
        Address result = toAddr(addressText);
        if (result == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return result;
    }

    private Function functionAtEntry(Address address) {
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private DataType voidPtr() {
        return new PointerDataType(VoidDataType.dataType);
    }

    private ParameterImpl[] params() throws Exception {
        return new ParameterImpl[] {
            new ParameterImpl("this", voidPtr(), currentProgram)
        };
    }

    private String expectedSignature() {
        return "void " + CALLING_CONVENTION + " " + NAME + "(void * this)";
    }

    private boolean signatureMatches(Function fn) {
        return fn.getSignature().toString().equals(expectedSignature());
    }

    private void applySignature(Function fn) throws Exception {
        fn.setCallingConvention(CALLING_CONVENTION);
        fn.setReturnType(VoidDataType.dataType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, params());
    }

    private boolean hasAllTags(Function fn) {
        Set<String> actual = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            actual.add(tag.getName());
        }
        for (String tag : TAGS) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private void verifyReadback(Address address) throws Exception {
        Function readBack = functionAtEntry(address);
        if (readBack == null) {
            throw new IllegalStateException("read-back missing function at " + ADDRESS);
        }
        if (!readBack.getName().equals(NAME)) {
            throw new IllegalStateException("read-back name mismatch: " + readBack.getName());
        }
        if (!signatureMatches(readBack)) {
            throw new IllegalStateException("read-back signature mismatch: " + readBack.getSignature());
        }
        if (readBack.getComment() == null || !readBack.getComment().equals(COMMENT)) {
            throw new IllegalStateException("read-back comment mismatch");
        }
        if (!hasAllTags(readBack)) {
            throw new IllegalStateException("read-back tag mismatch");
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        Stats stats = new Stats();
        Address address = addr(ADDRESS);
        Function fn = functionAtEntry(address);

        if (fn == null) {
            if (dryRun) {
                println("WOULD_CREATE: " + ADDRESS + " " + NAME);
                stats.wouldCreate++;
                println("WOULD_SIGNATURE: " + ADDRESS + " " + expectedSignature());
                stats.signatureUpdated++;
                println("WOULD_COMMENT: " + ADDRESS);
                stats.commentOnlyUpdated++;
                println("WOULD_TAGS: " + ADDRESS);
                stats.commentOnlyUpdated++;
                stats.updated++;
                println(summary(stats));
                return;
            }
            boolean disassembled = disassemble(address);
            fn = createFunction(address, NAME);
            if (fn == null) {
                stats.bad++;
                println("BAD: could not create function at " + ADDRESS + " disassembled=" + disassembled);
                println(summary(stats));
                throw new IllegalStateException("Wave1003 CGame shutdown boundary recovery could not create function");
            }
            stats.created++;
        }

        boolean changed = false;
        if (!fn.getName().equals(NAME)) {
            if (dryRun) {
                println("WOULD_RENAME: " + ADDRESS + " " + fn.getName() + " -> " + NAME);
                stats.wouldRename++;
            } else {
                fn.setName(NAME, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            changed = true;
        }
        if (!signatureMatches(fn)) {
            if (dryRun) {
                println("WOULD_SIGNATURE: " + ADDRESS + " " + expectedSignature());
            } else {
                applySignature(fn);
            }
            stats.signatureUpdated++;
            changed = true;
        }
        if (fn.getComment() == null || !fn.getComment().equals(COMMENT)) {
            if (dryRun) {
                println("WOULD_COMMENT: " + ADDRESS);
            } else {
                fn.setComment(COMMENT);
            }
            stats.commentOnlyUpdated++;
            changed = true;
        }
        if (!hasAllTags(fn)) {
            if (dryRun) {
                println("WOULD_TAGS: " + ADDRESS);
            } else {
                for (String tag : TAGS) {
                    fn.addTag(tag);
                }
            }
            stats.commentOnlyUpdated++;
            changed = true;
        }

        if (changed) {
            stats.updated++;
        } else {
            stats.skipped++;
        }

        if (!dryRun) {
            verifyReadback(address);
        }
        println(summary(stats));
        if (stats.bad != 0) {
            throw new IllegalStateException("Wave1003 CGame shutdown boundary recovery encountered bad rows");
        }
    }

    private String summary(Stats stats) {
        return "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " signature_updated=" + stats.signatureUpdated +
            " comment_only_updated=" + stats.commentOnlyUpdated +
            " missing=0" +
            " bad=" + stats.bad;
    }
}
