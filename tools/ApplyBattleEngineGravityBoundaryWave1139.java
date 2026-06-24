//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyBattleEngineGravityBoundaryWave1139 extends GhidraScript {
    private static final String ADDRESS = "0x004074d0";
    private static final String NAME = "CBattleEngine__Gravity";
    private static final String CALLING_CONVENTION = "__thiscall";
    private static final String COMMENT =
        "Wave1139 source-backed boundary recovery: recovered CBattleEngine::Gravity from the no-function gap "
        + "before CGame__UpdateMouseLookAngles. Static evidence: source parity with references/Onslaught/"
        + "BattleEngine.cpp lines 1064-1088, IsDying/state switch at this+0x2c and this+0x260, superclass-style "
        + "gravity constants, two jet-state tail jumps through this+0x57c into CBattleEngineJetPart__Gravity, "
        + "and default zero-gravity fallback. Static retail Ghidra/source evidence only; exact CBattleEngine/"
        + "JetPart layout, exact state enum names, runtime flight physics, BEA patching, gameplay outcomes, "
        + "and rebuild parity remain separate proof.";
    private static final String[] TAGS = {
        "static-reaudit",
        "wave1139-battleengine-jetpart-current-risk-review",
        "wave1139-readback-verified",
        "retail-binary-evidence",
        "function-boundary-recovered",
        "source-backed",
        "battleengine",
        "jet-control",
        "gravity",
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
        int missing = 0;
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

    private ParameterImpl thisParam() throws Exception {
        return new ParameterImpl("this", new PointerDataType(VoidDataType.dataType), currentProgram);
    }

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private String expectedSignature() {
        return "float " + CALLING_CONVENTION + " " + NAME + "(void * this)";
    }

    private boolean signatureMatches(Function fn) throws Exception {
        if (!CALLING_CONVENTION.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), FloatDataType.dataType)) {
            return false;
        }
        if (fn.getParameterCount() != 1) {
            return false;
        }
        Parameter actual = fn.getParameter(0);
        return "this".equals(actual.getName())
            && sameDataType(actual.getDataType(), new PointerDataType(VoidDataType.dataType));
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
    }

    private boolean hasAllTags(Function fn) {
        Set<String> actual = tagNames(fn);
        for (String tag : TAGS) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private void applySignature(Function fn) throws Exception {
        fn.setCallingConvention(CALLING_CONVENTION);
        fn.setReturnType(FloatDataType.dataType, SourceType.USER_DEFINED);
        fn.replaceParameters(
            FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
            true,
            SourceType.USER_DEFINED,
            thisParam()
        );
    }

    private void verifyReadBack() throws Exception {
        Function fn = functionAtEntry(addr(ADDRESS));
        if (fn == null) {
            throw new IllegalStateException("Read-back missing at " + ADDRESS);
        }
        if (!NAME.equals(fn.getName())) {
            throw new IllegalStateException("Read-back name mismatch: " + fn.getName());
        }
        if (!signatureMatches(fn)) {
            throw new IllegalStateException("Read-back signature mismatch: " + fn.getSignature());
        }
        if (fn.getComment() == null || !COMMENT.equals(fn.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch");
        }
        if (!hasAllTags(fn)) {
            throw new IllegalStateException("Read-back tag mismatch");
        }
    }

    @Override
    protected void run() throws Exception {
        boolean dryRun = isDryRun(getScriptArgs().length > 0 ? getScriptArgs()[0] : "dry");
        println("ApplyBattleEngineGravityBoundaryWave1139 mode=" + (dryRun ? "dry" : "apply"));

        Stats stats = new Stats();
        Address address = addr(ADDRESS);
        Function fn = functionAtEntry(address);
        boolean changed = false;

        if (fn == null) {
            if (dryRun) {
                println("WOULD_CREATE: " + ADDRESS + " " + NAME);
                stats.wouldCreate++;
                changed = true;
            } else {
                boolean disassembled = disassemble(address);
                fn = createFunction(address, NAME);
                if (fn == null) {
                    println("BAD: could not create function at " + ADDRESS + " disassembled=" + disassembled);
                    stats.bad++;
                } else {
                    println("CREATED: " + ADDRESS + " " + NAME + " disassembled=" + disassembled);
                    stats.created++;
                    changed = true;
                }
            }
        }

        if (fn != null) {
            if (!NAME.equals(fn.getName())) {
                if (dryRun) {
                    println("WOULD_RENAME: " + ADDRESS + " " + fn.getName() + " -> " + NAME);
                    stats.wouldRename++;
                    changed = true;
                } else {
                    fn.setName(NAME, SourceType.USER_DEFINED);
                    stats.renamed++;
                    changed = true;
                }
            }

            if (!signatureMatches(fn)) {
                if (dryRun) {
                    println("WOULD_SIGNATURE: " + ADDRESS + " " + expectedSignature());
                    stats.signatureUpdated++;
                    changed = true;
                } else {
                    applySignature(fn);
                    stats.signatureUpdated++;
                    changed = true;
                }
            }

            if (fn.getComment() == null || !COMMENT.equals(fn.getComment())) {
                if (dryRun) {
                    println("WOULD_COMMENT: " + ADDRESS);
                    stats.commentOnlyUpdated++;
                    changed = true;
                } else {
                    fn.setComment(COMMENT);
                    stats.commentOnlyUpdated++;
                    changed = true;
                }
            }

            if (!hasAllTags(fn)) {
                if (dryRun) {
                    println("WOULD_TAGS: " + ADDRESS);
                    stats.commentOnlyUpdated++;
                    changed = true;
                } else {
                    for (String tag : TAGS) {
                        fn.addTag(tag);
                    }
                    stats.commentOnlyUpdated++;
                    changed = true;
                }
            }

            if (!dryRun) {
                verifyReadBack();
            }
        }

        if (changed) {
            stats.updated++;
        } else {
            stats.skipped++;
        }

        println(
            "SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " created=" + stats.created
            + " would_create=" + stats.wouldCreate
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave1139 apply encountered missing/bad rows");
        }
        if (!dryRun) {
            println("REPORT: Save succeeded");
        }
    }
}
