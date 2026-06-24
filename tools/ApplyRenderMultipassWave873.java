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

public class ApplyRenderMultipassWave873 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String convention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] allowedExistingNames;
        final String[] tags;

        Spec(
                String address,
                String name,
                String convention,
                DataType returnType,
                ParameterImpl[] parameters,
                String comment,
                String[] allowedExistingNames,
                String[] tags) {
            this.address = address;
            this.name = name;
            this.convention = convention;
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
        Address address = toAddr(addressText);
        if (address == null) {
            throw new IllegalArgumentException("Bad address: " + addressText);
        }
        return address;
    }

    private Function functionAtEntry(String addressText) {
        Address address = addr(addressText);
        Function fn = getFunctionAt(address);
        if (fn != null) {
            return fn;
        }
        Function containing = getFunctionContaining(address);
        if (containing != null && containing.getEntryPoint().equals(address)) {
            return containing;
        }
        return null;
    }

    private ParameterImpl param(String name, DataType type) throws Exception {
        return new ParameterImpl(name, type, currentProgram);
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "render-multipass-wave873",
            "wave873-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-reviewed",
            "owner-corrected",
            "important-renderer-infrastructure",
            "high-importance-low-local-evidence-density",
            "render-queue",
            "multipass-render"
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
        if (!spec.convention.equals(fn.getCallingConventionName())) {
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

    private boolean alreadyApplied(Function fn, Spec spec) {
        return fn.getName().equals(spec.name)
            && signatureMatches(fn, spec)
            && spec.comment.equals(fn.getComment())
            && hasAllTags(fn, spec.tags);
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ").append(spec.convention).append(" ").append(spec.name).append("(");
        if (spec.parameters.length == 0) {
            sb.append("void");
        }
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName()).append(" ").append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                println("MISSING: " + spec.address + " " + spec.name);
                stats.missing++;
                stats.bad++;
                return;
            }
            if (!allowedName(spec, fn.getName())) {
                println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
                stats.bad++;
                return;
            }

            boolean needsRename = !fn.getName().equals(spec.name);
            boolean needsSignature = !signatureMatches(fn, spec);
            boolean needsComment = !spec.comment.equals(fn.getComment());
            boolean needsTags = !hasAllTags(fn, spec.tags);

            if (!needsRename && !needsSignature && !needsComment && !needsTags) {
                println("SKIP_OK: " + spec.address + " " + spec.name + " already current");
                stats.skipped++;
                return;
            }

            if (dryRun) {
                println("DRY_UPDATE: " + spec.address + " " + fn.getName()
                    + " -> " + expectedSignature(spec)
                    + " needsRename=" + needsRename
                    + " needsSignature=" + needsSignature
                    + " needsComment=" + needsComment
                    + " needsTags=" + needsTags);
                stats.skipped++;
                if (needsRename) {
                    stats.wouldRename++;
                }
                if (needsSignature) {
                    stats.signatureUpdated++;
                } else if (needsComment || needsTags || needsRename) {
                    stats.commentOnlyUpdated++;
                }
                return;
            }

            if (needsRename) {
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            if (needsSignature) {
                fn.setCallingConvention(spec.convention);
                fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
                fn.replaceParameters(
                    FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS,
                    true,
                    SourceType.USER_DEFINED,
                    spec.parameters
                );
                stats.signatureUpdated++;
            } else if (needsComment || needsTags || needsRename) {
                stats.commentOnlyUpdated++;
            }
            if (needsComment) {
                fn.setComment(spec.comment);
            }
            for (String tag : spec.tags) {
                if (!tagNames(fn).contains(tag)) {
                    fn.addTag(tag);
                }
            }

            Function readback = functionAtEntry(spec.address);
            if (readback == null || !alreadyApplied(readback, spec)) {
                println("READBACK_BAD: " + spec.address);
                if (readback != null) {
                    println("READBACK_GOT: " + readback.getName() + " " + readback.getSignature() + " convention=" + readback.getCallingConventionName());
                }
                stats.bad++;
                return;
            }
            println("READBACK_OK: " + spec.address + " " + spec.name + " " + readback.getSignature() + " convention=" + readback.getCallingConventionName());
            stats.updated++;
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
                "0x00553960",
                "CRenderQueue__RenderMultipassLayerA",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave873 render multipass static read-back: CDXEngine__Render callsite 0x0053e692 loads ECX=0x009c7550, the documented global CRenderQueue, before this call, so this corrects the stale CDXEngine owner prefix to CRenderQueue. The body exits under DAT_0089d680 or disabled this+0x704, checks render queue key/state via CDXEngine__GetRenderQueueSortKeyAt0C(&DAT_009c7c58), clears this+0x704/sets this+0x706 and resets global tint 0xe7 on empty state, configures D3D/state-cache texture stages, copies the DAT_009c7c90 matrix block through CDXEngine__SetWorldMatrixElements(&DAT_009c65c0,...), then walks entries at this+0x10c with count this+0x5bc and material/table pointers around this+0x640 to drive CDXLandscape__RenderTileRange and restore render state. This is high-importance, low local-evidence-density renderer infrastructure, not low-importance filler. Static retail Ghidra evidence only; exact CRenderQueue entry/material layout, exact D3D enum names, runtime multipass render behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__RenderMultipassLayerA"},
                tags("layer-a", "owner-corrected-from-cdxengine", "landscape-tile-range", "state-restore", "global-tint")
            ),
            new Spec(
                "0x00554170",
                "CRenderQueue__RenderMultipassLayerB",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave873 render multipass static read-back: CDXEngine__Render callsite 0x0053e6af loads ECX=0x009c7550, the documented global CRenderQueue, before this call, so this corrects the stale CDXEngine owner prefix to CRenderQueue. The body requires DAT_0089d680 clear, this+0x704 enabled, and this+0x5b0 set; configures multi-stage texture states, writes the DAT_00628258 immediate quad/light block through D3D device slot +0xb0, marks global matrix/state blocks DAT_009c6914/DAT_009c6954 dirty, walks this+0x5bc entries and material pointers at this+0x640, calls CEngine__SetRenderStateCached for stages 0..3, applies pending CDXEngine render state, issues the D3D device draw slot +0x14c with primitive type/count-like arguments, then restores texture stage/global dirty bytes. This is high-importance, low local-evidence-density renderer infrastructure, not low-importance filler. Static retail Ghidra evidence only; exact CRenderQueue entry/material layout, exact D3D enum names, runtime multipass render behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__RenderMultipassLayerB"},
                tags("layer-b", "owner-corrected-from-cdxengine", "d3d-draw-slot-14c", "state-restore", "global-matrix-state")
            ),
            new Spec(
                "0x005545d0",
                "CRenderQueue__BuildProjectedSprites",
                "__thiscall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr), param("unit", voidPtr)},
                "Wave873 render multipass static read-back: both CVBufTexture__RenderDynamicUnitPass callsites 0x004773ab and 0x004779b3 push the active unit pointer and load ECX=0x009c7550 before calling this helper, so this corrects the stale CDXEngine owner prefix to CRenderQueue. The body samples the unit/source world position through vfuncs, calls CStaticShadows__SampleShadowHeightBilinear(&DAT_006fadc8,...), derives a scale/alpha term from the unit vfunc +0x40, height delta, flag 0x02000000, camera distance, and constants around 0x005d85c0/0x005d85ec/0x005d8c70, skips duplicate active entries already present at this+0x10c when this+0x704 is set, then forwards sprite data to CRenderQueue__EmitBillboardStrip. This is high-importance projected-sprite/shadow connector infrastructure, not low-importance filler. Static retail Ghidra evidence only; exact unit/source class, exact sprite payload layout, runtime shadow/sprite behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__BuildProjectedSprites"},
                tags("projected-sprites", "owner-corrected-from-cdxengine", "dynamic-unit-render", "static-shadow", "duplicate-queue-skip")
            ),
            new Spec(
                "0x00554750",
                "CRenderQueue__EmitBillboardStrip",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("x", floatType),
                    param("y", floatType),
                    param("z_bits", intType),
                    param("w_bits", intType),
                    param("scale", floatType),
                    param("count", intType)
                },
                "Wave873 render multipass static read-back: CRenderQueue__BuildProjectedSprites calls this helper at 0x0055473a with the same 0x009c7550 CRenderQueue receiver. The body exits under DAT_0089d680, clamps large scale to 2.0, blends global shadow/tint colors DAT_006fbe54 and DAT_006fbe44 using count-derived alpha, computes projected x/y bounds from CRenderQueue view-vector fields this+0x594/this+0x598, then loops the projected footprint. Each quad samples CStaticShadows__SampleShadowHeightBilinear four times, computes UV-like offsets, writes four vertices through CVBufTexture__AddVertices(*(this+0x5b8), ..., 4), and writes six indices through CVBufTexture__AddIndices(*(this+0x5b8), ..., 6). z_bits and w_bits are preserved as stack-cleaned but currently unused/static-bit payload arguments from the caller. Static retail Ghidra evidence only; exact vertex format, exact tint packing, exact sprite payload layout, runtime projected-billboard behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__EmitBillboardStrip"},
                tags("projected-sprites", "owner-corrected-from-cdxengine", "billboard-strip", "static-shadow", "vbuftexture-write")
            ),
            new Spec(
                "0x00554df0",
                "CRenderQueue__RenderVBufTextureWithStateToggle",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave873 render multipass static read-back: CDXEngine__Render callsite 0x0053e846 loads ECX=0x009c7550 before this call, and the target saves ECX in ESI before loading CVBufTexture pointer *(this+0x5b8). This corrects the stale CVBufTexture owner/signature to a CRenderQueue receiver wrapper. The body switches D3D texture-stage states 0/1/2 to mode 3, disables render state 0xe, calls CVBufTexture__Render(*(this+0x5b8), reset_after_render=1), then restores stage states 1/2 and render state 0xe to enabled. This is high-importance render-queue/CVBufTexture handoff infrastructure, not low-importance filler. Static retail Ghidra evidence only; exact this+0x5b8 field identity, exact D3D enum names, runtime render output, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CVBufTexture__RenderWithStateToggle"},
                tags("owner-corrected-from-cvbuftexture", "vbuftexture-render", "state-toggle", "field-5b8")
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
            + " signature_updated=" + stats.signatureUpdated
            + " comment_only_updated=" + stats.commentOnlyUpdated
            + " missing=" + stats.missing
            + " bad=" + stats.bad);

        if (stats.missing != 0 || stats.bad != 0) {
            throw new RuntimeException("Wave873 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
