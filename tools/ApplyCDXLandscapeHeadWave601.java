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

public class ApplyCDXLandscapeHeadWave601 extends GhidraScript {
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
            "cdxlandscape-head-wave601",
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
        ByteDataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00544770",
                "CDXLandscape__ReleaseOwnedResources",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("resource_record", voidPtr) },
                "Wave601 CDXLandscape head hardening: shutdown and reset paths pass a resource_record whose +0 slot is released through its vtable with argument 3, whose +0x08 vector is destroyed with 0xc-byte entries through CDXLandscape__FreeObjectCallback and then freed from the 4-byte count header, and whose +0x04 scratch buffer is freed and cleared. Static retail evidence only; exact resource-record layout, runtime landscape behavior, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXLandscape__ReleaseOwnedResources"},
                tags("cdxlandscape", "resource-array", "texture-mip-records", "callback-release", "param-renamed")
            ),
            new Spec(
                "0x005447d0",
                "CDXLandscape__FreeObjectCallback",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("object_record", voidPtr) },
                "Wave601 CDXLandscape head hardening: this 0xc-entry vector destructor callback frees the pointer stored at object_record+0 through CDXMemoryManager__Free(&DAT_009c3df0, ...). It is used by CDXLandscape__ReleaseOwnedResources and by the mip-level allocation cleanup path. Static retail evidence only; exact vector entry ownership, runtime landscape behavior, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXLandscape__FreeObjectCallback"},
                tags("cdxlandscape", "resource-array", "free-callback", "param-renamed")
            ),
            new Spec(
                "0x005447e0",
                "CDXLandscape__CreateMipLevels",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("mip_level_count", intType)
                },
                "Wave601 CDXLandscape head hardening: RET 0x4 confirms one stack argument after ECX. The body stores mip_level_count at +0x0c, allocates mip_level_count-1 CLandscapeTexture records from DXLandscape.cpp line 0x5f, allocates mip update records from line 0x6d, allocates per-level 2-byte buffers from DXLandscape.h line 0xaa, allocates the 0x14000 scratch buffer from line 0x73, and initializes non-root mip buffers to 0xff. Static retail evidence only; exact mip texture contract, runtime cache behavior, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXLandscape__CreateMipLevels"},
                tags("cdxlandscape", "mip-levels", "landscape-texture", "resource-array", "ret-0x4")
            ),
            new Spec(
                "0x00544a00",
                "CDXLandscape__Constructor",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave601 CDXLandscape head hardening: CEngine__Init allocates a 0x40-byte object, calls this ECX-only constructor, installs vtable 0x005e50d0, clears the pending HUD marker handle at +0x08, zeros resource fields at +0x24/+0x28/+0x2c/+0x30/+0x38, clears byte +0x3c, and returns this. Static retail evidence only; exact object layout, runtime landscape behavior, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXLandscape__Constructor"},
                tags("cdxlandscape", "constructor", "vtable", "hud-marker")
            ),
            new Spec(
                "0x00544a40",
                "CDXLandscape__ScalarDeletingDestructor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("flags", byteType)
                },
                "Wave601 CDXLandscape head hardening: vtable slot 0 at 0x005e50d0 points here. The stub calls CDXLandscape__Destructor on ECX, tests flags bit 0 from the single RET 0x4 stack argument, frees this through CDXMemoryManager__Free when that bit is set, and returns this. Static retail evidence only; exact deletion policy, runtime destructor ownership, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXLandscape__ScalarDeletingDestructor"},
                tags("cdxlandscape", "scalar-deleting-dtor", "vtable", "flags", "ret-0x4")
            ),
            new Spec(
                "0x00544a60",
                "CDXLandscape__Destructor",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave601 CDXLandscape head hardening: this ECX-only destructor reinstalls vtable 0x005e50d0, unlinks the object from CShaderBase render-object lists, decrements and clears the vertex shader pointer at +0x18, releases the interface pointer at +0x1c via IUnknown__ReleaseAndNull, runs the device-object cleanup helper, and releases the pending HUD marker handle. Static retail evidence only; exact base-class relationship, runtime shader ownership, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXLandscape__Destructor"},
                tags("cdxlandscape", "destructor", "shader-list", "hud-marker")
            ),
            new Spec(
                "0x00544af0",
                "CDXLandscape__Init",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("init_context", voidPtr)
                },
                "Wave601 CDXLandscape head hardening: CEngine__Init calls this with the constructed CDXLandscape object in ECX and pushes engine+0x49c as one stack argument; RET 0x4 confirms the callee consumes that argument, which is stored at +0x20. The body resets the landscape-texture update queue, registers BuildLandscapeCache and xx_coastcalc, allocates and initializes the root CLandscapeTexture, creates CVBuffer and CIBuffer resources, initializes shader-base state, invokes vtable slot 4 ReleaseBuffers, and creates LandscapeShader only when required pointers are ready. Static retail evidence only; exact init_context semantics, runtime resource availability, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXLandscape__Init"},
                tags("cdxlandscape", "init", "landscape-texture", "vertex-index-buffer", "ret-0x4")
            ),
            new Spec(
                "0x00544eb0",
                "CDXLandscape__ReleaseBuffers",
                "__fastcall",
                intType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave601 CDXLandscape head hardening: vtable slot 4 at 0x005e50e0 points here. The body releases and clears device-resource pointers at +0x08, +0x10, +0x0c, and +0x14 through each resource vtable slot +8, releases the interface pointer at +0x1c with IUnknown__ReleaseAndNull, and returns 0. Static retail evidence only; exact device-resource ownership, runtime lost-device behavior, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXLandscape__ReleaseBuffers"},
                tags("cdxlandscape", "release-buffers", "vtable-slot-4", "device-resources")
            ),
            new Spec(
                "0x00544f10",
                "CDXLandscape__Shutdown",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave601 CDXLandscape head hardening: CEngine__Shutdown calls this for engine+0x10. The body invokes vtable slot +0x10, unlinks shader-base lists, resets the CLandscapeTexture update queue, destroys the +0x24 array of 0x34-byte resource records through CDXLandscape__ReleaseOwnedResources, releases object pointers at +0x28/+0x2c/+0x30 through their scalar delete paths, destroys CDXSurf state, and decrements/clears the texture or HUD-linked pointer at +0x38. Static retail evidence only; exact shutdown ordering, runtime surface ownership, source-body identity, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXLandscape__Shutdown"},
                tags("cdxlandscape", "shutdown", "resource-array", "surface-texture")
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
