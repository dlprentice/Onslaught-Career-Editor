//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
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

public class ApplyAtmosphericsProfileWave874 extends GhidraScript {
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
            "atmospherics-profile-wave874",
            "wave874-readback-verified",
            "retail-binary-evidence",
            "comment-hardened",
            "signature-corrected",
            "important-weather-renderer-infrastructure",
            "high-importance-low-local-evidence-density",
            "atmospherics",
            "dxsnow"
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
        PointerDataType charPtr = new PointerDataType(CharDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00554e80",
                "DXSnow__StaticInitPrimaryTransformGlobals",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave874 static read-back: created from pointer-table DATA xref 0x00622ab8. The body writes 1.0/0 transform-basis values into globals 0x009c7f88 through 0x009c7fb4; decompile shows fourth-slot stack-temporary copies, so exact matrix/padding shape remains unproven. Adjacent table entries and the DXSnow snow bodies tie this to high-importance weather-renderer setup, not low-importance filler. Static retail evidence only; runtime snow/weather visuals, exact source identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("function-boundary-created", "pointer-table-00622ab8", "static-initializer", "transform-globals")
            ),
            new Spec(
                "0x00554f50",
                "DXSnow__StaticInitDisableSnowConfig",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave874 static read-back: created from pointer-table DATA xref 0x00622abc. The body calls CVar__Init for global 0x009c7f78 with string 0x00652444 \"DISABLE_SNOW\" and initial value 0, then registers cleanup callback 0x00554f70 through CRT__RegisterOnexitFunction. This identifies a static snow config initializer; it does not prove runtime console/config behavior. Static retail evidence only; exact source identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("function-boundary-created", "pointer-table-00622ab8", "static-initializer", "disable-snow-config")
            ),
            new Spec(
                "0x00554f70",
                "DXSnow__StaticDestroyDisableSnowConfig",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave874 static read-back: created from callback immediate DATA xref 0x00554f61 inside DXSnow__StaticInitDisableSnowConfig. The body sets ECX to 0x009c7f78 and jumps to CTweak__dtor_base_thunk_004530a0, so this is the static cleanup callback for the DISABLE_SNOW CVar object. Static retail evidence only; exact CTweak/CVar lifetime behavior, runtime snow disabling behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("function-boundary-created", "static-cleanup", "disable-snow-config")
            ),
            new Spec(
                "0x00554f80",
                "CAtmosphericsProfile__ctor",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave874 static read-back: CAtmosphericsProfile constructor/list-entry setup at the raw queue head. Atmospherics__Init calls this at 0x00404a98 after allocating a 0x3a4-byte profile object from Atmospherics.cpp debug path 0x00622ec4; the body calls the base atmospheric/link setup, installs vtable 0x005e5974, zeroes profile fields, sets 1.0 defaults at +0x18/+0x2c/+0x40/+0x54, initializes snow-related defaults +0x388=9.0, +0x38c=2.0, +0x3a0=10.0, and gates byte +0x14 from 0x009c7f84. Static retail evidence only; concrete CAtmosphericsProfile/CDXSnow layout, runtime weather behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("raw-commentless-head", "constructor", "vtable-005e5974")
            ),
            new Spec(
                "0x00555010",
                "CAtmosphericsProfile__VFunc00_GetNameString",
                "__fastcall",
                charPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave874 static read-back: created from CAtmosphericsProfile vtable 0x005e5974 slot +0x00. The tiny body returns constant string pointer 0x0065246c, dumped as \"Snow\"; it ignores the this pointer. Static retail evidence only; exact source virtual name, ListAtmospherics/debug UI behavior, runtime weather behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("function-boundary-created", "vtable-slot", "vtable-005e5974", "snow-name")
            ),
            new Spec(
                "0x00555410",
                "CAtmosphericsProfile__ReleaseResources",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave874 static read-back: CAtmosphericsProfile resource release helper, reached by vtable 0x005e5974 slot +0x10 at slot address 0x005e5984 and by Atmospherics__Shutdown dispatch. The body decrements the texture-like resource at this+0x0c via CTexture__DecrementRefCountFromNameField((this+0x0c)+8), destroys/frees the CVBufTexture-like object at this+0x08 through CVBufTexture__dtor and CDXMemoryManager__Free, releases the vertex-shader-like resource at this+0x10 through CVertexShader__DecrementLiveReferenceCount, and clears each slot. Static retail evidence only; exact resource ownership, runtime cleanup behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("vtable-slot", "resource-release", "vtable-005e5974")
            ),
            new Spec(
                "0x00555460",
                "CAtmosphericsProfile__RenderOverlay",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave874 static read-back: CAtmosphericsProfile snow/weather overlay renderer helper, called from the vtable slot +0x08 body at 0x00555a09. The body copies matrix blocks from globals 0x009c6914/0x009c6954/0x009c6994, uses device vtable slot +0x178 through 0x00888a50, samples active viewpoint/camera globals 0x0089ce4c/0x0089c9a4, subtracts profile offsets +0x390/+0x394/+0x398, clamps snow density 0x0066018c to 0..1000, and renders through the CVBufTexture-like object at this+0x08. Static retail evidence only; exact visual output, runtime weather behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("overlay-renderer", "snow-density", "matrix-copy")
            ),
            new Spec(
                "0x00555600",
                "CAtmosphericsProfile__VFunc08_UpdateSnowAndRenderOverlay",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave874 static read-back: created from CAtmosphericsProfile vtable 0x005e5974 slot +0x08, which Atmospherics__UpdateAll dispatches for each atmospheric list entry. The body gates on DAT_0089d680, profile enable byte this+0x14, shader support DAT_0063c108, atm_snowdensity 0x0066018c, and resource this+0x10; configures render/state cache helpers including RenderState_Set, D3DStateCache__SetStateCached, and D3DStateCache__SetStateRaw; copies wind/vector globals 0x00660198..0x006601a4 into this+0x58; pushes device constants through 0x00888a50 vtable slot +0x178; iterates 50 entries from this+0x68; calls CDXTexture__GetAnimatedFrame and CAtmosphericsProfile__RenderOverlay at 0x00555a09; then restores shader/render toggles. Static retail evidence only; exact source virtual name, concrete field layout, runtime snow/weather visuals, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("function-boundary-created", "vtable-slot", "vtable-005e5974", "snow-update", "overlay-renderer")
            ),
            new Spec(
                "0x00555af0",
                "DXSnow__StaticZeroOverlayVectorGlobals",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave874 static read-back: created from pointer-table DATA xref 0x00622ac0. The body clears globals 0x009c8000, 0x009c8004, and 0x009c8008, adjacent to the overlay transform initializer at 0x00555b10 and the CAtmosphericsProfile slot +0x08 body. Static retail evidence only; exact vector/global semantics, runtime weather behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("function-boundary-created", "pointer-table-00622ab8", "static-initializer", "overlay-vector-globals")
            ),
            new Spec(
                "0x00555b10",
                "DXSnow__StaticInitOverlayTransformGlobals",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave874 static read-back: created from pointer-table DATA xref 0x00622ac4. The body writes 1.0/0 transform-basis values into globals 0x009c7fd0 through 0x009c7ffc; decompile shows fourth-slot stack-temporary copies, so exact matrix/padding shape remains unproven. This is important renderer setup evidence adjacent to the CAtmosphericsProfile snow update/render body, not low-importance filler. Static retail evidence only; runtime weather visuals, exact source identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("function-boundary-created", "pointer-table-00622ab8", "static-initializer", "overlay-transform-globals")
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
