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

public class ApplyDXEngineResourceTailWave592 extends GhidraScript {
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
        sb.append(spec.returnType.getDisplayName());
        sb.append(" ");
        sb.append(spec.callingConvention);
        sb.append(" ");
        sb.append(spec.name);
        sb.append("(");
        for (int i = 0; i < spec.parameters.length; i++) {
            if (i > 0) {
                sb.append(", ");
            }
            sb.append(spec.parameters[i].getDataType().getDisplayName());
            sb.append(" ");
            sb.append(spec.parameters[i].getName());
        }
        sb.append(")");
        return sb.toString();
    }

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "dxengine-resource-tail-wave592",
            "retail-binary-evidence",
            "cdxengine",
            "resource-lifecycle",
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
        if (!hasAllTags(readBack, spec.tags)) {
            throw new IllegalStateException("Read-back tag mismatch at " + spec.address);
        }
    }

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = functionAtEntry(spec.address);
            if (fn == null) {
                println("MISSING: " + spec.address);
                stats.missing++;
                return;
            }
            if (!allowedName(spec, fn.getName())) {
                println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
                stats.bad++;
                return;
            }
            if (!fn.getName().equals(spec.name)) {
                if (dryRun) {
                    println("DRYRENAME: " + spec.address + " " + fn.getName() + " -> " + spec.name);
                    stats.wouldRename++;
                    stats.skipped++;
                    return;
                }
                fn.setName(spec.name, SourceType.USER_DEFINED);
                stats.renamed++;
            }
            if (!needsUpdate(fn, spec)) {
                println("SKIP: " + spec.address + " " + spec.name);
                stats.skipped++;
                return;
            }
            if (dryRun) {
                println("DRY: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
                stats.skipped++;
                return;
            }

            fn.setCallingConvention(spec.callingConvention);
            fn.setReturnType(spec.returnType, SourceType.USER_DEFINED);
            fn.replaceParameters(FunctionUpdateType.DYNAMIC_STORAGE_ALL_PARAMS, true, SourceType.USER_DEFINED, spec.parameters);
            fn.setComment(spec.comment);
            for (String tag : spec.tags) {
                fn.addTag(tag);
            }
            verifyReadBack(spec);
            println("OK: " + spec.address + " " + spec.name + " :: " + expectedSignature(spec));
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
                "0x0053d3a0",
                "CDXEngine__ReleaseDefaultTextureAndMeshRefs",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave592 owner/signature correction: CLTShell shutdown passes the global CDXEngine object at 0x89c9a0 in ECX before this helper releases the default texture handle at this+0x4e4 through CHud__DecrementCounter9C(texture+8), decrements the default mesh usage counter at this+0x28 + 0x170, and clears both slots. Static retail evidence only; exact CDXEngine layout, runtime shutdown behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CLTShell__ReleaseHudRefAndTargetHandle"},
                tags("owner-corrected", "resource-release", "default-texture", "default-mesh", "ecx-only", "renamed")
            ),
            new Spec(
                "0x0053d3e0",
                "CDXEngine__Shutdown",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave592 vtable-slot correction: CDXEngine vtable slot 2 at 0x005e4fd0 calls CEngine__Shutdown, releases the same default texture/mesh pair as CDXEngine__ReleaseDefaultTextureAndMeshRefs, releases texture handles at this+0x4c0, this+0x4e8, and this+0x4ec, destroys the CDXPatchManager, and clears this+0xc80. Static retail evidence only; exact virtual contract, concrete member names, runtime teardown behavior, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__VFunc_03_0053d3e0"},
                tags("vtable-slot-2", "resource-release", "texture-release", "patch-manager", "ecx-only", "renamed")
            ),
            new Spec(
                "0x0053d4c0",
                "CDXEngine__UploadScaledRgbLookupTable",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("gammaScale", floatType) },
                "Wave592 signature/comment hardening: the SetGammaBias command stub parses one float, loads ECX with the global CDXEngine object at 0x89c9a0, pushes that float, and calls this RET 0x4 helper. The body scales three 256-entry RGB lookup-table lanes rooted around this+0x6f4, clamps against the retail float constants at 0x005d8568/0x005d856c, expands bytes to 16-bit ramp entries, and dispatches the active device vfunc at +0x54 with the local ramp. Static retail evidence only; exact display-device contract, gamma semantics, runtime video behavior, and rebuild parity remain unproven.",
                new String[] {},
                tags("gamma-ramp", "rgb-lookup-table", "setgammabias", "ret-0x4")
            ),
            new Spec(
                "0x0053d5f0",
                "CDXEngine__Init",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave592 vtable-slot correction: CGame__Init passes the global CDXEngine object at 0x89c9a0 to vtable slot 0 at 0x005e4fc8 immediately after CHeightField startup. The body calls CEngine__Init, initializes CDXEngine render/resource fields, obtains the device RGB lookup table through the active device vfunc at +0x58, registers SetGammaBias/cg_renderreflections/cg_texturereflections controls, initializes CDXPatchManager with 800/300/0x5a, and returns TRUE/FALSE. Static retail evidence only; exact field layout, runtime device behavior, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__VFunc_01_0053d5f0"},
                tags("vtable-slot-0", "init", "console-command", "console-variable", "patch-manager", "ecx-only", "renamed")
            ),
            new Spec(
                "0x0053d6d0",
                "CDXEngine__InitResources",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave592 vtable-slot correction: CGame__RunLevel passes the global CDXEngine object at 0x89c9a0 to vtable slot 1 at 0x005e4fcc after level resource loading and before GameInterface/HUD texture loading. The body calls CEngine__InitResources, loads meshtex/default.tga, meshtex/outline.tga, and meshtex/EdArrow.tga into this+0x4e4/+0x4e8/+0x4ec, acquires default.msh into this+0x28 with a usage increment, and caches the Sun_Sprite physics node at this+0xc80. Static retail evidence only; exact resource ownership, runtime level-load behavior, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__VFunc_02_0053d6d0"},
                tags("vtable-slot-1", "resource-load", "default-texture", "default-mesh", "sun-sprite", "ecx-only", "renamed")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated +
            " skipped=" + stats.skipped +
            " renamed=" + stats.renamed +
            " would_rename=" + stats.wouldRename +
            " missing=" + stats.missing +
            " bad=" + stats.bad);
    }
}
