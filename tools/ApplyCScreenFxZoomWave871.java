//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.DataType;
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

public class ApplyCScreenFxZoomWave871 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String convention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String convention, DataType returnType, ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.convention = convention;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "cscreenfx-zoom-wave871",
            "wave871-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-reviewed",
            "important-renderer-infrastructure",
            "screenfx",
            "zoom-effect",
            "renderer-connective-code"
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
            if (!fn.getName().equals(spec.name)) {
                println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
                stats.bad++;
                return;
            }

            boolean needsSignature = !signatureMatches(fn, spec);
            boolean needsComment = !spec.comment.equals(fn.getComment());
            boolean needsTags = !hasAllTags(fn, spec.tags);

            if (!needsSignature && !needsComment && !needsTags) {
                println("SKIP_OK: " + spec.address + " " + spec.name + " already current");
                stats.skipped++;
                return;
            }

            if (dryRun) {
                println("DRY_UPDATE: " + spec.address + " " + spec.name
                    + " -> " + expectedSignature(spec)
                    + " needsSignature=" + needsSignature
                    + " needsComment=" + needsComment
                    + " needsTags=" + needsTags);
                stats.skipped++;
                if (needsSignature) {
                    stats.signatureUpdated++;
                } else if (needsComment || needsTags) {
                    stats.commentOnlyUpdated++;
                }
                return;
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
            } else if (needsComment || needsTags) {
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

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00551c90",
                "CScreenFx__InitZoomEffectCvar",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("state", voidPtr)},
                "Wave871 CScreenFx zoom static read-back: clears the zoomline and reticle CVBufTexture slots at state+0/state+4, sets the enable byte at state+0x10 to 1, and registers console variable cg_zoomeffectenabled with description \"Is the visual effect for zooming enabled?\" through CConsole__RegisterVariable(&DAT_00663498, ..., type 3, state+0x10, 0, 0). The only code xref is CEngine__Init at 0x00449cfb. This is important screen-effect renderer infrastructure, not low-importance filler. Static retail Ghidra evidence only; exact CScreenFx layout, runtime zoom-effect behavior, BEA patching, and rebuild parity remain unproven.",
                tags("console-variable", "zoom-effect-cvar", "engine-init")
            ),
            new Spec(
                "0x00551cc0",
                "CScreenFx__LoadZoomTextures",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("state", voidPtr)},
                "Wave871 CScreenFx zoom static read-back: CEngine__InitResources calls this loader to resolve screenfx\\zoomlines.tga and screenfx\\reticle.tga through CScreenFx__FindTexture(texture_name, 1), store the returned CVBufTexture pointers at state+0/state+4, and configure each with CVBufTexture__SetVBFormat(FVF 0x144, usage 0x208, stride 0x1c, primitive 4, pool 0) plus CVBufTexture__SetIBFormat(index format 0x65, usage 0x208, reserved 2, pool 0). Static retail Ghidra evidence only; exact texture ownership, exact D3D enum meanings, runtime zoom-line/reticle rendering, BEA patching, and rebuild parity remain unproven.",
                tags("texture-load", "zoomlines-texture", "reticle-texture", "vbuftexture-format", "engine-initresources")
            ),
            new Spec(
                "0x00551d40",
                "CScreenFx__ReleaseZoomTextures",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("state", voidPtr)},
                "Wave871 CScreenFx zoom static read-back: CEngine__Shutdown calls this release helper; it checks state+0 and state+4, calls CDXEngine__DecrementResourceRefCount for each non-null zoomline/reticle CVBufTexture pointer, then clears the corresponding slot. This closes the static lifecycle paired with CScreenFx__LoadZoomTextures. Static retail Ghidra evidence only; exact release ownership contract, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                tags("texture-release", "resource-refcount", "engine-shutdown", "zoom-effect-lifecycle")
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
            throw new RuntimeException("Wave871 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
