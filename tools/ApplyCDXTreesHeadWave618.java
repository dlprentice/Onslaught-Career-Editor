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

public class ApplyCDXTreesHeadWave618 extends GhidraScript {
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
            "cdxtrees-wave618",
            "retail-binary-evidence",
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
                "0x0055a350",
                "CDXTrees__CDXTrees",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave618 CDXTrees head hardening: ECX-only constructor called for the global tree renderer object at 0x009cc148 from the nearby static-init thunk at 0x0055a325. Body returns this in EAX and installs CDXTrees vtable 0x005e59d8. Static retail decompile/instruction/vtable evidence only; exact CDXTrees object layout, runtime vegetation behavior, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtrees", "constructor", "vtable-005e59d8", "ret-c3", "signature-corrected")
            ),
            new Spec(
                "0x0055a360",
                "CDXTrees__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", byteType)
                },
                "Wave618 CDXTrees head hardening: vtable 0x005e59d8 slot 0 points here, and RET 0x4 confirms one explicit delete_flags stack argument. Body calls CDXTrees__dtor, frees this through CDXMemoryManager__Free when delete_flags bit 0 is set, and returns this. Static retail decompile/instruction/vtable evidence only; exact allocator ownership, runtime tree-renderer lifetime, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtrees", "scalar-deleting-dtor", "vtable-slot-0", "ret-0x4", "signature-corrected", "vtable-verified")
            ),
            new Spec(
                "0x0055a380",
                "CDXTrees__dtor",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave618 CDXTrees head hardening: destructor body reached from the scalar-deleting wrapper and nearby static-dtor thunk. Body reinstalls CDXTrees vtable 0x005e59d8, then tail-jumps to the device/base cleanup helper at 0x00512d50. Static retail decompile/instruction evidence only; exact base-class destructor identity, runtime cleanup ordering, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtrees", "destructor", "device-object-tail", "vtable-005e59d8", "signature-corrected")
            ),
            new Spec(
                "0x0055a390",
                "CDXTrees__Init",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave618 CDXTrees head hardening: CEngine__Init callsite 0x00449d0f passes global object 0x009cc148 in ECX. Body initializes shader/render-object base state through CShaderBase__Init(&DAT_00855bb0), clears the two CVBufTexture pointers at this+0x08 and this+0x0c, and returns with RET. Static retail decompile/xref/instruction evidence only; exact inherited layout, runtime init behavior, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtrees", "init", "shader-base", "buffer-fields", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055a3b0",
                "CDXTrees__ReleaseBuffers",
                "__thiscall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave618 CDXTrees head hardening: vtable 0x005e59d8 slot 4 points here. Body releases CVBufTexture objects at this+0x08 and this+0x0c through CVBufTexture__dtor plus CDXMemoryManager__Free, clears both fields, and returns 0. Static retail decompile/instruction/vtable evidence only; exact buffer ownership, lost-device behavior, runtime vegetation rendering, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtrees", "release-buffers", "cvbuftexture", "vtable-slot-4", "signature-corrected", "vtable-verified")
            ),
            new Spec(
                "0x0055a400",
                "CDXTrees__Reset",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave618 CDXTrees head hardening: CGame__ShutdownRestartLoop and CEngine__Shutdown callsites pass the global tree renderer in ECX. Body invokes vtable slot +0x10, which resolves to CDXTrees__ReleaseBuffers for this vtable, then unlinks this object from CShaderBase render-object lists. Static retail decompile/xref/instruction evidence only; exact reset/lost-device semantics, runtime render-list behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtrees", "reset", "release-buffers", "render-list-unlink", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055a420",
                "CDXTrees__BuildTreeGeometry",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave618 CDXTrees head hardening: CGame__LoadLevel and CDXTrees__Render callsites pass the tree renderer in ECX. Body releases old buffers, allocates two 0x68-byte CVBufTexture objects from debug path DXTrees.cpp lines 0x5e and 0x6a, configures VB format 0x152 with stride 0x24 and IB format 0x65, walks the CMapWho quadtree through DAT_00704290, filters owners with flag 0x02000000, emits 4 vertices and 6 indices per tree, stores each tree vertex index, and increments this+0x10. Static retail decompile/xref/instruction evidence only; exact tree/imposter layouts, runtime billboard output, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtrees", "build-tree-geometry", "quadtree", "cvbuftexture", "tree-flag-02000000", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055aa10",
                "CDXTrees__Render",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave618 CDXTrees head hardening: CDXEngine__Render callsite 0x0053e7c1 passes the global tree renderer in ECX. Body lazily calls CDXTrees__BuildTreeGeometry when this+0x08 is empty, copies world matrix state, binds the animated tree texture, applies alpha/render-state setup, renders the primary buffer with CVBufTexture__RenderIndexedNoValidate, optionally renders the secondary buffer when the sampled shadow-height delta exceeds the observed threshold, then restores render states. Static retail decompile/xref/instruction evidence only; exact render-state meanings, runtime vegetation/shadow output, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtrees", "render", "billboard-render", "render-state", "secondary-buffer", "signature-corrected", "callsite-verified")
            ),
            new Spec(
                "0x0055ae40",
                "CDXTrees__HideTree",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("tree_object", voidPtr)
                },
                "Wave618 CDXTrees head hardening: CRTTree__Destructor callsite 0x004de001 pushes the tree object and passes global tree renderer 0x009cc148 in ECX; RET 0x4 confirms one explicit stack argument. Body reads the tree vertex index at tree_object+0x30, requires both tree buffers to exist, locks 0x90 bytes at vertex_index*0x24 in each backing CVBuffer, zeros the four vertex position triples, then unlocks. Static retail decompile/xref/instruction evidence only; exact CRTTree/layout semantics, runtime tree destruction visibility, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxtrees", "hide-tree", "lock-range", "vertex-stride-0x24", "ret-0x4", "signature-corrected", "callsite-verified")
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
