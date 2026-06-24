//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.IntegerDataType;
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

public class ApplyCDXMeshVBHeadWave609 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;

        Spec(
                String address,
                String name,
                String callingConvention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] allowedExistingNames,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.allowedExistingNames = allowedExistingNames;
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
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

    private boolean allowedName(Spec spec, String actual) {
        if (actual.equals(spec.name)) {
            return true;
        }
        for (String allowed : spec.allowedExistingNames) {
            if (actual.equals(allowed)) {
                return true;
            }
        }
        return false;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName())
            .append(" ")
            .append(spec.callingConvention)
            .append(" ")
            .append(spec.name)
            .append("(");
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "cdxmeshvb-head-wave609",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private Set<String> tagNames(Function fn) {
        Set<String> names = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            names.add(tag.getName());
        }
        return names;
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
        Set<String> existing = tagNames(fn);
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
        if (!fn.getName().equals(spec.name)) {
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
        if (!readBack.getName().equals(spec.name)) {
            throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
        }
        if (!signatureMatches(readBack, spec)) {
            throw new IllegalStateException("Read-back signature mismatch at " + spec.address + ": " + readBack.getSignature());
        }
        String readComment = readBack.getComment();
        if (readComment == null || !readComment.equals(spec.comment)) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("MISSING: " + spec.address + " " + spec.name);
                return;
            }
            if (!allowedName(spec, fn.getName())) {
                stats.bad++;
                println("BADNAME: " + spec.address + " actual=" + fn.getName() + " expected=" + spec.name);
                return;
            }
            boolean needsRename = !fn.getName().equals(spec.name);
            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " " + expectedSignature(spec));
                return;
            }
            if (dryRun) {
                stats.skipped++;
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + fn.getSignature() + " -> " + expectedSignature(spec));
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(
                FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                true,
                SourceType.USER_DEFINED,
                spec.parameters
            );
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            stats.updated++;
            println("OK: " + spec.address + " " + expectedSignature(spec));
        } catch (Exception ex) {
            stats.bad++;
            println("BAD: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = args == null || args.length == 0 || isDryRun(args[0]);

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0054bf80",
                "CDXMeshVB__ctor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave609 CDXMeshVB lifecycle hardening: constructor installs vtable 0x005e50fc, clears source/group/shader/name fields at +0x108/+0x10c/+0x110/+0x120/+0x124, zeroes the 64 group-pointer slots from +0x8, and passes this into the shader/render-object init path. Static retail decompile/instruction/vtable evidence only; exact class layout, source identity, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] { "CDXMeshVB__ctor_like_0054bf80" },
                tags("cdxmeshvb", "constructor", "vtable-005e50fc", "ret-c3")
            ),
            new Spec(
                "0x0054bff0",
                "CDXMeshVB__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                },
                "Wave609 CDXMeshVB lifecycle correction: vtable slot 0 is the scalar-deleting destructor wrapper, not a generic vfunc. RET 0x4 and vtable xref 0x005e50fc prove one stack flags byte; the body calls CDXMeshVB__dtor_base, frees this through CDXMemoryManager__Free when flags&1, and returns this. Static retail decompile/instruction/vtable evidence only; allocator ownership, runtime lifetime behavior, exact layout, BEA patching, and rebuild parity remain unproven.",
                new String[] { "CDXMeshVB__VFunc_00_0054bff0" },
                tags("cdxmeshvb", "scalar-deleting-dtor", "vtable-slot-0", "ret-0x4")
            ),
            new Spec(
                "0x0054c010",
                "CDXMeshVB__dtor_base",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave609 CDXMeshVB lifecycle correction: this is the destructor body called by the scalar-deleting wrapper. It reinstalls the CDXMeshVB vtable, calls CDXMeshVB__ReleaseResources, runs the retail post-release cleanup check for the first group slot, unlinks from shader/render-object lists, frees the name pointer at +0x124, and calls the base device-object teardown. Static retail decompile/instruction evidence only; destructor side-effect completeness, exact layout, runtime lifetime behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] { "CDXMeshVB__scalar_deleting_dtor_0054c010" },
                tags("cdxmeshvb", "destructor-base", "resource-release", "ret-c3")
            ),
            new Spec(
                "0x0054c0a0",
                "CDXMeshVB__BuildStaticVB",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave609 CDXMeshVB static-build hardening: ECX-only builder reads the source mesh at +0x10c, groups faces by six material/texture references into the +0x8 group table, allocates 0x24-byte static vertices plus index staging, creates a D3D vertex buffer with FVF 0x152 and per-group index buffers, then stores stride/FVF/primitive fields +0x114/+0x118/+0x11c as 0x24/0x152/4. Returns S_OK or 0x80004005-style failure. Static retail decompile/instruction evidence only; exact mesh/group layouts, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxmeshvb", "build-static-vb", "vertex-stride-0x24", "fvf-0x152", "hresult-style")
            ),
            new Spec(
                "0x0054c920",
                "CDXMeshVB__BuildSkeletalVB",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave609 CDXMeshVB skeletal-build hardening: ECX-only builder emits the Building skeletal VB status, queries vertex-shader support, builds 0x30-byte skeletal vertices with weight-derived blend fields, groups material references, creates vertex/index buffers through the DAT_00854e6c hardware-support gate, and stores stride/FVF/primitive fields +0x114/+0x118/+0x11c as 0x30/0/4. Returns S_OK or 0x80004005-style failure. Static retail decompile/instruction evidence only; exact bone/weight layouts, runtime animation rendering, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxmeshvb", "build-skeletal-vb", "vertex-stride-0x30", "vertex-shader-gate", "hresult-style")
            ),
            new Spec(
                "0x0054d3f0",
                "CDXMeshVB__ReleaseResources",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave609 CDXMeshVB resource-release hardening: vtable slot 4 and destructor xref identify this ECX-only release helper. It releases the shared first-group vertex buffer when present, walks active group records to release/clear per-group index buffers and frees group records, resets group count +0x108, clears/decrements the vertex-shader reference at +0x110, and returns 0. Static retail decompile/instruction/vtable evidence only; exact ownership model, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] { "CDXMeshVB__VFunc_04_0054d3f0" },
                tags("cdxmeshvb", "resource-release", "vtable-slot-4", "ret-c3")
            ),
            new Spec(
                "0x0054e160",
                "CDXMeshVB__Load",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("reader", voidPtr),
                    param("use_hardware_shader", intType)
                },
                "Wave609 CDXMeshVB load hardening: RET 0x8 and CMeshPart__LoadFromStream xref show two stack args, a chunk reader and hardware-shader flag. The body snapshots existing VB/source/name state, frees old group records, reads the 0x128-byte serialized header, restores selected state, allocates/copies the source mesh name, reads each group record, creates index/vertex buffers, and gates hardware-shader VB creation on DAT_00854e6c && use_hardware_shader. Static retail decompile/instruction/xref evidence only; exact serialized layout, runtime asset loading, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxmeshvb", "load", "ret-0x8", "chunk-reader", "vertex-shader-gate")
            )
        };

        Stats stats = new Stats();
        println("MODE: " + (dryRun ? "dry" : "apply"));
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println(
            "SUMMARY: updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
        if (!dryRun) {
            if (stats.bad != 0 || stats.missing != 0) {
                throw new IllegalStateException("Apply completed with bad=" + stats.bad + " missing=" + stats.missing);
            }
        }
    }
}
