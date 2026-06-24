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

public class ApplyDxFontFrontendHeadWave596 extends GhidraScript {
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
            "dxfont-frontend-head-wave596",
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
        DataType byteType = ByteDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00540840",
                "CDXBitmapFont__Deserialize",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("chunk_reader", voidPtr)
                },
                "Wave596 name/signature/comment hardening: PCPlatform__DeserializeFontsAndAssets calls this four times for CDXBitmapFont slots. RET 0x4 proves one stack parameter after this; the body reads serialized texture/font tables from chunk_reader, caches the texture at this+0x170, fills font metadata/glyph data, clears the GDI-font flag, and initializes the CVBufTexture vertex/index formats. Static retail evidence only; exact CDXBitmapFont layout, source identity, runtime font loading behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"PCPlatform__ReadHeaderPairAndResetByteCount", "CDXBitmapFont__Deserialize"},
                tags("cdxbitmapfont", "font-deserialize", "ret-0x4", "owner-corrected", "phantom-param-removed")
            ),
            new Spec(
                "0x00540970",
                "CDXBitmapFont__HasAnimatedTexture",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave596 name/signature/comment hardening: CConsole__RenderLoadingScreen calls this predicate before loading-screen text/render work. ECX carries this; the body checks the cached texture at this+0x170 and returns 1 only when CDXTexture__GetAnimatedFrame returns a non-null frame. Static retail evidence only; exact CDXBitmapFont/CDXTexture ownership, runtime loading-screen behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXEngine__HasValidAnimatedTexture", "CDXBitmapFont__HasAnimatedTexture"},
                tags("cdxbitmapfont", "animated-texture", "loading-screen", "owner-corrected")
            ),
            new Spec(
                "0x00540b60",
                "CDXFrontEnd__DestructorBody",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave596 name/signature/comment hardening: CDXFrontEnd__scalar_deleting_dtor calls this non-freeing destructor body before optional heap release. ECX carries this; the SEH-framed body unwinds waiting-thread/SPtrSet/device-object style members, installs the fallback vtable at this+8, and calls CMonitor__Shutdown(this). Static retail evidence only; exact inheritance chain, member layouts, runtime frontend teardown behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CCamera__ctor_like_00540b60", "CDXFrontEnd__DestructorBody"},
                tags("cdxfrontend", "destructor-body", "seh-wrapped", "owner-corrected")
            ),
            new Spec(
                "0x00540bf0",
                "CDXFrontEnd__Constructor",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave596 name/signature/comment hardening: raw startup/init code calls this CDXFrontEnd constructor. ECX carries this; the body runs CFEPMultiplayerStart__ctor, installs the CDXFrontEnd vtable at 0x005e5054, and returns this. Static retail evidence only; exact class hierarchy, page ownership, runtime frontend initialization behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFrontEnd__ctor_like_00540bf0", "CDXFrontEnd__Constructor"},
                tags("cdxfrontend", "constructor", "vtable-005e5054", "owner-corrected")
            ),
            new Spec(
                "0x00540c10",
                "CDXFrontEnd__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", byteType)
                },
                "Wave596 name/signature/comment hardening: vtable 0x005e5054 slot 1 is the CDXFrontEnd scalar-deleting destructor. RET 0x4 proves one stack parameter after this; the body calls CDXFrontEnd__DestructorBody(this), frees through CDXMemoryManager only when delete_flags bit 0 is set, and returns this. Static retail evidence only; exact allocation ownership, full vtable layout, runtime teardown behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFrontEnd__VFunc_01_00540c10", "CDXFrontEnd__scalar_deleting_dtor"},
                tags("cdxfrontend", "scalar-deleting-dtor", "vtable-slot-1", "ret-0x4", "phantom-param-removed")
            ),
            new Spec(
                "0x00540f70",
                "CDXFrontEnd__RenderStart",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave596 name/signature/comment hardening: CFrontEnd__Render and CDXFrontEnd vtable 0x005e5054 slot 6 reach this source-bridged RenderStart wrapper. ECX carries this; the body resets world render state, initializes transform caches, clears the screen, enables render state 0x1b, and forwards this into CFrontEnd__RenderStart. Static retail evidence only; exact CDXFrontEnd/CFrontEnd layout, full vtable layout, runtime rendering behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFrontEnd__VFunc_06_00540f70", "CDXFrontEnd__RenderStart"},
                tags("cdxfrontend", "render-start", "vtable-slot-6", "source-bridge", "owner-corrected")
            ),
            new Spec(
                "0x00540fb0",
                "CDXFrontEnd__VFunc_07_00540fb0",
                "__stdcall",
                voidType,
                new ParameterImpl[] {
                    param("render_particles", intType)
                },
                "Wave596 signature/comment hardening: CFrontEnd__Render and CDXFrontEnd vtable 0x005e5054 slot 7 reach this render-tail helper. RET 0x4 proves one stack parameter; when render_particles is nonzero the body calls CDXFrontEnd__SetupRenderMatricesAndProjection before forwarding the flag into CFrontEnd__RenderCursorEndSceneAndAsyncSave. Static retail evidence only; exact call ownership, particle/projection semantics, runtime rendering behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFrontEnd__VFunc_07_00540fb0"},
                tags("cdxfrontend", "render-tail", "vtable-slot-7", "ret-0x4", "param-renamed")
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
            throw new RuntimeException("Wave596 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
