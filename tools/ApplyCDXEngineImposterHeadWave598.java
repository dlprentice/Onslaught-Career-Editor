//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
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

public class ApplyCDXEngineImposterHeadWave598 extends GhidraScript {
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
            "cdxengine-imposter-head-wave598",
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
            println("OK: " + spec.address + " " + functionAtEntry(spec.address).getSignature());
            Thread.sleep(50);
        } catch (Exception ex) {
            stats.bad++;
            println("FAIL: " + spec.address + " " + spec.name + " " + ex.getClass().getSimpleName() + ": " + ex.getMessage());
        }
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType intType = IntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00542740",
                "CDXEngine__InitLandscapeTextureTables",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] {
                    param("texture_table_owner", voidPtr)
                },
                "Wave598 CDXEngine/imposter head hardening: static-init code loads ECX with 0x008aa4e8 before calling this small helper, which forwards that owner pointer to the currently labeled 0x00481400 constructor/base-init helper and returns the same pointer. Static retail evidence only; exact owner type, landscape texture table layout, constructor identity, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__InitLandscapeTextureTables"},
                tags("cdxengine", "landscape-texture-table", "static-init", "returns-input")
            ),
            new Spec(
                "0x005428d0",
                "CDXImposter__InitGlobals",
                "__cdecl",
                intType,
                new ParameterImpl[] {},
                "Wave598 CDXEngine/imposter head hardening: CGame__Init calls this imposter global initializer, which clears matrix/sample globals around 0x00650848/0x00650888, resets imposter list/count/texture-buffer globals, seeds identity-matrix lanes with 1.0f, conditionally clears 0x008aa8c8, and returns 1. Static retail evidence only; exact global layout, runtime imposter startup behavior, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXImposter__InitGlobals"},
                tags("cdximposter", "global-init", "cgame-init", "returns-one")
            ),
            new Spec(
                "0x00542990",
                "CDXImposter__ShutdownAll",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave598 CDXEngine/imposter head hardening: the shutdown path walks global imposter list 0x0067a678, frees each frame-data allocation and imposter object, decrements 0x008aa8bc per entry, releases the secondary/primary CVBufTexture globals, releases the texture atlas handle, and clears the stored width/height globals. Static retail evidence only; exact object layout, resource ownership, runtime teardown behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXImposter__ShutdownAll"},
                tags("cdximposter", "global-shutdown", "resource-release", "linked-list")
            ),
            new Spec(
                "0x00542a30",
                "CDXImposter__InitEntry",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] {
                    param("imposter", voidPtr)
                },
                "Wave598 CDXEngine/imposter head hardening: CImposter__FindOrCreate and CDXImposter__Create use this entry initializer after allocating a 0x4c imposter object. ECX carries the object pointer; the body clears fields +0x30/+0x38/+0x3c, increments global count 0x008aa8bc, and returns the same pointer in EAX. Static retail evidence only; exact field names, source-body identity, runtime imposter behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXImposter__InitEntry"},
                tags("cdximposter", "entry-init", "cimposter", "returns-input")
            ),
            new Spec(
                "0x00542a50",
                "CDXEngine__BuildDirectionalSampleRing",
                "__cdecl",
                voidType,
                new ParameterImpl[] {
                    param("view_yaw_radians", floatType)
                },
                "Wave598 CDXEngine/imposter head hardening: CDXEngine__Render computes camera/view yaw with fpatan and calls this one-float helper. The body records yaw at 0x0067a680, builds static basis/sample-ring matrices in 0x00650888 and 0x008aa790..0x008aa86c, derives a normalized view direction at 0x008aa780, calls CDXEngine__BuildZRotationMatrix inside a four-slot loop, packs sort keys through CDXEngine__PackVec3AndDepthToSortKey, and marks 0x008aa8b0 dirty. Static retail evidence only; exact matrix/vector layouts, runtime render behavior, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__BuildDirectionalSampleRing"},
                tags("cdxengine", "imposter", "sample-ring", "render-prep", "one-float-arg")
            ),
            new Spec(
                "0x00542ee0",
                "CDXEngine__BuildZRotationMatrix",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("angle_radians", floatType)
                },
                "Wave598 CDXEngine/imposter head hardening: CDXEngine__BuildDirectionalSampleRing passes ECX as a local 3x4 matrix buffer and pushes one angle float; RET 0x4 confirms exactly one stack parameter after the ECX output pointer. The body writes a Z-rotation basis with cos/sin lanes and an identity Z row. Static retail evidence only; exact matrix type, source-body identity, runtime render behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__BuildZRotationMatrix"},
                tags("cdxengine", "imposter", "z-rotation", "ret-0x4", "matrix-helper")
            ),
            new Spec(
                "0x00543300",
                "CDXEngine__RenderImposterBillboardSet",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("view_context", voidPtr),
                    param("alpha", intType),
                    param("frame_index", intType)
                },
                "Wave598 CDXEngine/imposter head hardening: CRTTree and nearby mesh/tree callsites pass ECX as an imposter object plus three stack arguments, and RET 0xc confirms the view-context, alpha, and frame-index stack shape. The body gates on the global imposter initialization flag and imposter+0x38, samples view matrices through the first two view-context vfuncs, uses imposter fields +0x24/+0x3c/+0x40 to pick frame data, calls CDXImposter__BuildQuadGeometry for six billboard faces, and advances the basis for the first four faces. Static retail evidence only; exact owner/source identity, frame-data layout, runtime tree/imposter rendering behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__RenderImposterBillboardSet"},
                tags("cdxengine", "cdximposter", "billboard-render", "ret-0xc", "tree-imposter")
            ),
            new Spec(
                "0x005438c0",
                "CDXImposter__RenderAll",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave598 CDXEngine/imposter head hardening: CDXEngine__Render calls this global imposter render pass after world draw state setup. The body gates on imposter initialization/list globals, optionally draws the texture atlas debug sprite, sets cached D3D/render states, binds the imposter texture atlas through CDXTexture__GetAnimatedFrame, renders the primary and secondary CVBufTexture batches, and restores sampler/state-cache values. Static retail evidence only; exact render-state semantics, runtime visual behavior, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXImposter__RenderAll"},
                tags("cdximposter", "render-all", "render-state", "cvbuftexture")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY: updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave598 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
