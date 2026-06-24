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
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCDXEngineKempyCubeWave600 extends GhidraScript {
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
            "cdxengine-kempy-cube-wave600",
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
        if (!spec.comment.equals(readBack.getComment())) {
            throw new IllegalStateException("Read-back comment mismatch at " + spec.address);
        }
        Set<String> readBackTags = tagNames(readBack);
        for (String tag : spec.tags) {
            if (!readBackTags.contains(tag)) {
                throw new IllegalStateException("Read-back missing tag " + tag + " at " + spec.address);
            }
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                stats.missing++;
                println("FAIL: " + spec.address + " " + spec.name + " Function not found");
                return;
            }
            if (!allowedName(spec, fn.getName())) {
                throw new IllegalStateException("Unexpected function name: " + fn.getName());
            }

            if (!needsUpdate(fn, spec)) {
                stats.skipped++;
                println("SKIP: " + spec.address + " already " + expectedSignature(spec));
                return;
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                stats.skipped++;
                println("DRY: " + spec.address + " " + fn.getName() + " -> " + expectedSignature(spec));
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
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        VoidDataType voidType = VoidDataType.dataType;
        PointerDataType voidPtr = new PointerDataType(voidType);
        IntegerDataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00544040",
                "CDXEngine__ClearKempyCubeTextureSlots",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] { param("kempy_cube_resources", voidPtr) },
                "Wave600 CDXEngine Kempy cube hardening: CEngine__Init allocates a 0xa14 block at engine+0x498 and calls this ECX-only helper; the body returns the same resource block in EAX after zeroing five 4-byte texture slots at +0x00..+0x10. This corrects the older HudTextureSlots label to Kempy cube resource evidence. Static retail evidence only; exact resource-block layout, runtime texture behavior, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__ClearHudTextureSlots"},
                tags("cdxengine", "kempy-cube", "texture-slots", "returns-input", "label-corrected")
            ),
            new Spec(
                "0x00544060",
                "CDXEngine__ReleaseKempyCubeTexturesAndVertexBuffer",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("kempy_cube_resources", voidPtr) },
                "Wave600 CDXEngine Kempy cube hardening: CEngine__Shutdown calls this ECX-only cleanup helper for the engine+0x498 resource block. The body walks five texture pointers, decrements each texture ref/lifetime counter through CHud__DecrementCounter9C(texture+8), clears each slot, then releases global CVBuffer pointer 0x008aa908 through its vtable delete path and clears the global. Static retail evidence only; exact texture/CVBuffer ownership, runtime shutdown behavior, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__ReleaseHudTextureSlots"},
                tags("cdxengine", "kempy-cube", "texture-slots", "cvbuffer", "label-corrected")
            ),
            new Spec(
                "0x005440a0",
                "CDXEngine__InitKempyCubeTexturesAndVertexBuffer",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("cube_index", intType)
                },
                "Wave600 CDXEngine Kempy cube hardening: CEngine__SetKempyCube forwards engine+0x498 and one cube_index stack argument through CDXEngine__InitKempyCubeResources, and RET 0x4 confirms this helper consumes one stack argument after ECX. The body formats five cube texture filenames via CDXEngine__FormatCubeTextureFilename, loads them through CTexture__FindTexture, stores five texture pointers in the resource block, releases/recreates global CVBuffer 0x008aa908 from DXKempyCube.cpp line 0x52, creates a 20-vertex/20-byte/FVF 0x102 buffer, locks it, copies 100 dwords from static data 0x006508f0, and unlocks. Static retail evidence only; exact cube texture contract, vertex layout, runtime render behavior, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__InitKempyCubeTexturesAndVertexBuffer"},
                tags("cdxengine", "kempy-cube", "texture-load", "cvbuffer", "ret-0x4")
            ),
            new Spec(
                "0x005441a0",
                "CDXEngine__InitKempyCubeResources",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("cube_index", intType)
                },
                "Wave600 CDXEngine Kempy cube hardening: CEngine__SetKempyCube calls this wrapper with engine+0x498 in ECX and one cube_index stack argument. The wrapper pushes cube_index, calls CDXEngine__InitKempyCubeTexturesAndVertexBuffer, and returns with RET 0x4. Static retail evidence only; exact resource selection semantics, runtime texture behavior, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__InitKempyCubeResources"},
                tags("cdxengine", "kempy-cube", "set-kempy-cube", "wrapper", "ret-0x4")
            ),
            new Spec(
                "0x005441b0",
                "CDXEngine__RenderKempyCubeFaces",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("kempy_cube_resources", voidPtr) },
                "Wave600 CDXEngine Kempy cube hardening: CDXEngine__Render calls this ECX-only helper with engine+0x498 after projection setup. The body disables selected render states, prepares sampler/state-cache values, copies view/world-matrix data from 0x008aa8d8 into the active matrix block, binds global CVBuffer 0x008aa908, then loops five texture slots, resolves each animated texture frame through CDXTexture__GetAnimatedFrame, sets cached render state, issues the D3D draw call, and restores render/sampler state. Static retail evidence only; exact render-state semantics, vertex layout, runtime cube rendering, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__RenderKempyCubeFaces"},
                tags("cdxengine", "kempy-cube", "render", "texture-slots", "cvbuffer")
            )
        };

        println("MODE: " + (dryRun ? "dry" : "apply"));
        Stats stats = new Stats();
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
            if (stats.bad == 0 && stats.missing == 0) {
                println("REPORT: Save succeeded");
            } else {
                println("REPORT: Save blocked by bad/missing rows");
            }
        } else {
            println("REPORT: Save succeeded");
        }
    }
}
