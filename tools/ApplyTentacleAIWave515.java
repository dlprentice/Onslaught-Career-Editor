//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.DoubleDataType;
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

public class ApplyTentacleAIWave515 extends GhidraScript {
    private static class Spec {
        final String address;
        final String oldName;
        final String newName;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String oldName, String newName, String callingConvention,
                DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.oldName = oldName;
            this.newName = newName;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
        int renamed = 0;
        int wouldRename = 0;
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

    private Function functionAtEntry(String addressText) {
        Address address = addr(addressText);
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private ParameterImpl param(String name, DataType dataType) throws Exception {
        return new ParameterImpl(name, dataType, currentProgram);
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "tentacle-ai-wave515",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.newName).append("(");
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName())
                .append(" ")
                .append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private boolean sameDataType(DataType actual, DataType expected) {
        if (actual == null || expected == null) {
            return actual == expected;
        }
        return actual.isEquivalent(expected) || actual.getDisplayName().equals(expected.getDisplayName());
    }

    private boolean signatureMatches(Function fn, Spec spec) {
        if (!spec.callingConvention.equals(fn.getCallingConventionName())) {
            return false;
        }
        if (!sameDataType(fn.getReturnType(), spec.returnType)) {
            return false;
        }
        if (fn.getParameterCount() != spec.parameters.length) {
            return false;
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            Parameter actual = fn.getParameter(i);
            ParameterImpl expected = spec.parameters[i];
            if (!actual.getName().equals(expected.getName())) {
                return false;
            }
            if (!sameDataType(actual.getDataType(), expected.getDataType())) {
                return false;
            }
        }
        return true;
    }

    private boolean hasAllTags(Function fn, String[] tags) {
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.newName)) {
            return true;
        }
        if (!signatureMatches(fn, spec)) {
            return true;
        }
        String existingComment = fn.getComment();
        if (existingComment == null || !existingComment.equals(spec.comment)) {
            return true;
        }
        return !hasAllTags(fn, spec.tags);
    }

    private void verifyReadBack(Spec spec) throws Exception {
        Function readBack = functionAtEntry(spec.address);
        if (readBack == null) {
            throw new IllegalStateException("Read-back missing at " + spec.address);
        }
        if (!readBack.getName().equals(spec.newName)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        if (!signatureMatches(readBack, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
        }
        if (!spec.comment.equals(readBack.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }

        String currentName = fn.getName();
        if (!currentName.equals(spec.oldName) && !currentName.equals(spec.newName)) {
            println("BADNAME: " + spec.address + " " + currentName + " expected " + spec.oldName + " or " + spec.newName);
            stats.bad++;
            return;
        }

        boolean renameNeeded = !currentName.equals(spec.newName);
        boolean updateNeeded = needsUpdate(fn, spec);
        if (!updateNeeded) {
            println("SKIP: " + spec.address + " " + spec.newName);
            stats.skipped++;
            return;
        }

        if (dryRun) {
            println("DRY: " + spec.address + " " + currentName + " -> " + spec.newName + " :: " + expectedSignature(spec));
            stats.skipped++;
            if (renameNeeded) {
                stats.wouldRename++;
            }
            return;
        }

        if (renameNeeded) {
            fn.setName(spec.newName, SourceType.USER_DEFINED);
            stats.renamed++;
        }
        fn.setCallingConvention(spec.callingConvention);
        fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
        fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
        fn.setComment(spec.comment);
        for (String tag : spec.tags) {
            fn.addTag(tag);
        }
        verifyReadBack(spec);
        println("OK: " + spec.address + " " + spec.newName + " :: " + expectedSignature(spec));
        stats.updated++;
        Thread.sleep(50);
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType byteType = ByteDataType.dataType;
        DataType doubleType = DoubleDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x004f0760",
                "CTentacle__CreateTentacleGuide",
                "CTentacle__CreateTentacleGuide",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave515 signature/comment hardening: CTentacle guide factory. Factory-table data at 0x005e4170 references this entry; the body allocates a 0xec-byte object from pool 0x1b with Tentacle.cpp line 0x2f evidence, calls CMCTentacle__Constructor with owner context this+0x08 when available, and stores the component pointer or NULL at this+0x70. Static retail evidence only; exact source method name, concrete CTentacle/guide layouts, runtime tentacle behavior, BEA patching, and rebuild parity remain unproven.",
                tags("tentacle", "factory", "motion-controller", "guide")
            ),
            new Spec(
                "0x004f07e0",
                "CTentacle__CreateTentacleAI",
                "CTentacle__CreateTentacleAI",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave515 signature/comment hardening: CTentacle AI factory. Factory-table data at 0x005e4174 references this entry; the body allocates a 0x20-byte object from pool 0x17 with Tentacle.cpp line 0x35 evidence, calls CGuide__ctor_base with the owner pointer, installs vtable 0x005df46c, and stores the AI pointer or NULL at this+0x208. Static retail evidence only; exact CTentacleAI layout, runtime AI behavior, BEA patching, and rebuild parity remain unproven.",
                tags("tentacle", "factory", "ai", "guide")
            ),
            new Spec(
                "0x004f0860",
                "CTentacle__CreateWarspiteAI",
                "CTentacle__CreateWarspiteAI",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("init_context", voidPtr)},
                "Wave515 signature/comment hardening: CTentacle Warspite-style AI factory. Factory-table data at 0x005e4178 references this entry; RET 0x4 plus ECX/stack use show this plus one init_context argument. The body allocates a 0x60-byte pool-0x17 object with Tentacle.cpp line 0x3c evidence, calls CWarspite__Init with owner/init_context, installs vtable 0x005df498, and stores the pointer or NULL at this+0x13c. Static retail evidence only; exact Warspite helper identity, concrete layouts, runtime tentacle boss behavior, BEA patching, and rebuild parity remain unproven.",
                tags("tentacle", "factory", "warspite", "ai")
            ),
            new Spec(
                "0x004f08f0",
                "CTentacleAI__VFunc_01_004f08f0",
                "CTentacleAI__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("delete_flags", byteType)},
                "Wave515 rename/signature/comment hardening: CTentacleAI scalar deleting destructor. Vtable data at 0x005df49c points here; the body calls the adjacent destructor-base helper, frees this through CDXMemoryManager__Free only when delete_flags bit 0 is set, returns this, and ends with RET 0x4. Static retail evidence only; allocator ownership, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("tentacle", "ai", "destructor", "vtable-slot-1")
            ),
            new Spec(
                "0x004f0910",
                "CUnitAI__ctor_like_004f0910",
                "CTentacleAI__dtor_base",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave515 rename/signature/comment hardening: CTentacleAI destructor-base body reached only from CTentacleAI__scalar_deleting_dtor in current xrefs. The body restores the CUnitAI-style base vtable 0x005d8d1c, removes linked reader cells at +0x28, +0x24, and +0x0c when present, then calls CMonitor__Shutdown. It is structurally identical to the saved CUnitAI__dtor_base pattern but emitted in the adjacent Tentacle.cpp cluster. Static retail evidence only; exact C++ emission identity, concrete linked-set layout, runtime destruction behavior, and rebuild parity remain unproven.",
                tags("tentacle", "ai", "destructor", "base-cleanup")
            ),
            new Spec(
                "0x004f0c50",
                "CMCTentacle__BuildOrientationMatrixFromEuler",
                "CMCTentacle__BuildOrientationMatrixFromEuler",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("out_matrix", voidPtr)},
                "Wave515 signature/comment hardening: CMCTentacle orientation-matrix builder reached from CMCTentacle__UpdateSpline at 0x0049dd79. RET 0x4 confirms one explicit out_matrix argument after ECX; the body builds yaw/pitch-derived basis values from global angle constants, combines them with CSquadNormal__BuildOrientationMatrixFromEuler and two Mat34__MultiplyBasisToOut calls, then copies 12 dwords to out_matrix. Static retail evidence only; exact math names, concrete CMCTentacle layout, runtime spline motion behavior, BEA patching, and rebuild parity remain unproven.",
                tags("tentacle", "motion-controller", "matrix", "spline")
            ),
            new Spec(
                "0x004f1220",
                "CUnit__GetSpeedScaleByFlag30C",
                "CUnit__GetSpeedScaleByFlag30C",
                "__fastcall",
                doubleType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave515 signature/comment hardening: compact CUnit speed-scale selector. Current xrefs are two nearby branch/call sites; the body returns global float constant 0x005dbe34 when this+0x30c is nonzero, otherwise returns global float constant 0x005df464. Static retail evidence only; exact flag meaning, source identity, runtime movement behavior, and rebuild parity remain unproven.",
                tags("unit", "movement", "speed-scale", "flag")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad
        );
        if (stats.missing != 0 || stats.bad != 0) {
            throw new IllegalStateException("Wave515 Tentacle AI apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
