//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyMathMat34VectorWave973 extends GhidraScript {
    private static class ParamSpec {
        final String name;
        final DataType type;

        ParamSpec(String name, DataType type) {
            this.name = name;
            this.type = type;
        }
    }

    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final String comment;
        final ParamSpec[] params;

        Spec(String address, String name, String callingConvention, DataType returnType, String comment, ParamSpec... params) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.comment = comment;
            this.params = params;
        }
    }

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

    private ParameterImpl param(ParamSpec spec) throws Exception {
        return new ParameterImpl(spec.name, spec.type, currentProgram);
    }

    private ParameterImpl[] params(Spec spec) throws Exception {
        ParameterImpl[] result = new ParameterImpl[spec.params.length];
        for (int i = 0; i < spec.params.length; i++) {
            result[i] = param(spec.params[i]);
        }
        return result;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
        for (int i = 0; i < spec.params.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.params[i].type.getDisplayName()).append(" ").append(spec.params[i].name);
        }
        sb.append(")");
        return sb.toString();
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        return fn.getSignature().toString().equals(expectedSignature(spec));
    }

    private void applySignature(Function fn, Spec spec) throws Exception {
        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, params(spec));
    }

    private boolean hasAllTags(Function fn, String[] expectedTags) {
        Set<String> actual = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            actual.add(tag.getName());
        }
        for (String tag : expectedTags) {
            if (!actual.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private static DataType voidPtr() {
        return new PointerDataType(VoidDataType.dataType);
    }

    private static ParamSpec p(String name, DataType type) {
        return new ParamSpec(name, type);
    }

    private Spec[] specs() {
        return new Spec[] {
            new Spec(
                "0x0040c990",
                "CBattleEngine__GetLaunchPosition",
                "__thiscall",
                VoidDataType.dataType,
                "Wave973 math/Mat34 vector review boundary recovery: recovered the missing Ghidra function object for CBattleEngine::GetLaunchPosition. Static evidence: SEH prologue at 0x0040c990, terminal RET 0x14 at 0x0040d0ed immediately before 0x0040d0f0 CWeaponStatement__UsesBallisticArcNoLocks, five stack arguments after ECX, cockpit Gun emitter fallback, weapon primary position/orientation fallback, gravity and adjust-aim branches, camera view point/orientation reads, Vec3__ElevationOrZero and Mat34__SetFromEulerAngles calls, and source parity with references/Onslaught/BattleEngine.cpp lines 3000-3069. Static retail Ghidra/source evidence only; exact retail class layout, exact out-vector/out-matrix ABI, runtime launch-position behavior, BEA patching, and rebuild parity remain separate proof.",
                p("this", voidPtr()),
                p("inWeapon", voidPtr()),
                p("inIndex", IntegerDataType.dataType),
                p("outPos", voidPtr()),
                p("outOrientation", voidPtr()),
                p("inNeedOrientation", IntegerDataType.dataType)
            )
        };
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        Stats stats = new Stats();
        String[] tags = new String[] {
            "static-reaudit",
            "math-mat34-vector-review-wave973",
            "wave973-readback-verified",
            "retail-binary-evidence",
            "function-boundary-recovered",
            "battleengine",
            "launch-position",
            "mat34",
            "vector-math",
            "source-backed",
            "comment-hardened",
            "signature-hardened"
        };

        for (Spec spec : specs()) {
            Address address = addr(spec.address);
            Function fn = functionAtEntry(address);
            if (fn == null) {
                if (dryRun) {
                    println("WOULD_CREATE: " + spec.address + " " + spec.name);
                    stats.wouldCreate++;
                    continue;
                }
                boolean disassembled = disassemble(address);
                fn = createFunction(address, spec.name);
                if (fn == null) {
                    println("BAD: could not create function at " + spec.address + " disassembled=" + disassembled);
                    stats.bad++;
                    continue;
                }
                stats.created++;
            }

            boolean changed = false;
            if (!fn.getName().equals(spec.name)) {
                if (dryRun) {
                    println("WOULD_RENAME: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                    stats.wouldRename++;
                    changed = true;
                } else {
                    fn.setName(spec.name, SourceType.USER_DEFINED);
                    stats.renamed++;
                    changed = true;
                }
            }

            if (!signatureMatches(fn, spec)) {
                if (dryRun) {
                    println("WOULD_SIGNATURE: " + spec.address + " " + expectedSignature(spec));
                    stats.signatureUpdated++;
                    changed = true;
                } else {
                    applySignature(fn, spec);
                    stats.signatureUpdated++;
                    changed = true;
                }
            }

            if (fn.getComment() == null || !fn.getComment().equals(spec.comment)) {
                if (dryRun) {
                    println("WOULD_COMMENT: " + spec.address);
                    stats.commentOnlyUpdated++;
                    changed = true;
                } else {
                    fn.setComment(spec.comment);
                    stats.commentOnlyUpdated++;
                    changed = true;
                }
            }

            if (!hasAllTags(fn, tags)) {
                if (dryRun) {
                    println("WOULD_TAGS: " + spec.address);
                    stats.commentOnlyUpdated++;
                    changed = true;
                } else {
                    for (String tag : tags) {
                        fn.addTag(tag);
                    }
                    stats.commentOnlyUpdated++;
                    changed = true;
                }
            }

            if (changed) {
                stats.updated++;
            } else {
                stats.skipped++;
            }
        }

        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " created=" + stats.created +
            " would_create=" + stats.wouldCreate +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " signature_updated=" + stats.signatureUpdated +
            " comment_only_updated=" + stats.commentOnlyUpdated +
            " missing=0" +
            " bad=" + stats.bad
        );

        if (stats.bad != 0) {
            throw new IllegalStateException("Wave973 math/Mat34 vector review encountered bad rows");
        }
    }
}
