//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.BooleanDataType;
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

public class ApplyCDXLandscapeTargetShadowWave604 extends GhidraScript {
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
            "cdxlandscape-target-shadow-wave604",
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
        DataType boolType = BooleanDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00546220",
                "CDXLandscape__SetRenderTarget",
                "__thiscall",
                boolType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("target_surface", voidPtr)
                },
                "Wave604 CDXLandscape target/shadow hardening: RET 0x4 confirms one stack argument after ECX. CGame__Render and CDXLandscape__RenderShadowMap both pass the implicit this/ECX value as a stack/local two-surface save pair and push target_surface from CGame view state or CDXLandscape this+0x08. The body captures the current D3D target/depth surfaces into the save pair, queries an auxiliary surface/pointer from target_surface through vtable slot 0x48, updates device target/depth state through slots 0x94/0x9c, logs Failed SRT/Failed SDSS paths, disables DAT_009c6480 on failures, releases the auxiliary surface on success, and returns AL as the success flag. Static retail evidence only; exact D3D interface semantics, surface ownership lifetime, runtime shadow-map rendering, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXLandscape__SetRenderTarget"},
                tags("cdxlandscape", "render-target", "ret-0x4", "surface-pair", "d3d-target")
            ),
            new Spec(
                "0x005463f0",
                "CDXLandscape__ReleaseRenderTarget",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave604 CDXLandscape target/shadow hardening: plain RET confirms no stack arguments after ECX. CGame__Render calls this with implicit this/ECX=&local_surface_pair when the temporary target path was armed. The body restores device target/depth state from this[0]/[1] through D3D vtable slots 0x94/0x9c with a fallback restore order, then releases and nulls both saved surfaces. Static retail evidence only; exact D3D interface semantics, COM lifetime ownership, runtime render-target behavior, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXLandscape__ReleaseRenderTarget"},
                tags("cdxlandscape", "render-target-release", "ret-c3", "surface-pair", "d3d-restore")
            ),
            new Spec(
                "0x00546460",
                "CDXLandscape__ReleaseSurfaces",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave604 CDXLandscape target/shadow hardening: plain RET confirms no stack arguments after ECX. CGame__Render final/unwind paths call this with implicit this/ECX=&local_surface_pair when render-target restore is not needed. The body releases this[0] and this[1] if non-null, writes both slots back to null, and does not issue the D3D restore calls used by CDXLandscape__ReleaseRenderTarget. Static retail evidence only; exact COM lifetime ownership, unwind-path coverage, runtime render-target behavior, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXLandscape__ReleaseSurfaces"},
                tags("cdxlandscape", "surface-release", "ret-c3", "surface-pair", "unwind-cleanup")
            ),
            new Spec(
                "0x00546490",
                "CDXLandscape__RenderShadowMap",
                "__thiscall",
                boolType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("record_index", intType)
                },
                "Wave604 CDXLandscape target/shadow hardening: RET 0x4 confirms one stack argument after ECX. CDXLandscape__RenderTerrain pushes 0 with ECX=this, and the body computes this+0x24 + record_index*0x34 after guarding DAT_009c648c, non-multiplayer state, and required this+0x08/0x0c/0x18/0x1c resources. It configures D3DStateCache/render states, binds this+0x28 and this+0x2c buffers plus this+0x18/0x1c shader/texture resources, switches to the target surface at this+0x08 through CDXLandscape__SetRenderTarget, draws the base terrain and resource-record tile subranges, calls CWaterRenderSystem__RenderShadowPass(DAT_0089c9b4), restores target/depth surfaces and render states, and returns AL as the success flag. Static retail evidence only; exact resource-record layout, D3D state semantics, runtime shadow-map rendering, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXLandscape__RenderShadowMap"},
                tags("cdxlandscape", "shadow-map", "ret-0x4", "resource-record", "d3d-state")
            ),
            new Spec(
                "0x00546900",
                "CDXLandscape__RenderTileRange",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("x_min", intType),
                    param("x_max", intType),
                    param("z_min", intType),
                    param("z_max", intType)
                },
                "Wave604 CDXLandscape target/shadow hardening: RET 0x10 plus CDXEngine__RenderMultipassLayerA callsite pushes prove four coordinate bounds after ECX=DAT_0089c9b0. The body averages x_min/x_max and z_min/z_max with the 0.5 scalar, samples CStaticShadows__SampleShadowHeightBilinear, subtracts the resource-origin vector returned from the this+0x24 resource object, shifts and clamps coordinate bounds into 0..0x3f tile indices, iterates 64x64 tile records, binds the tile CVBuffer at +0x0c, chooses the DAT_009c64dc material record from tile bytes +0x10/+0x11, applies pending render state and validation through DAT_009c7c58, and draws indexed primitives for accepted tiles. Static retail evidence only; exact tile/resource structure semantics, shadow-height runtime behavior, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXLandscape__RenderTileRange"},
                tags("cdxlandscape", "tile-range", "ret-0x10", "static-shadows", "tile-records")
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
