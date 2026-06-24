//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.ByteDataType;
import ghidra.program.model.data.CharDataType;
import ghidra.program.model.data.DataType;
import ghidra.program.model.data.FloatDataType;
import ghidra.program.model.data.IntegerDataType;
import ghidra.program.model.data.PointerDataType;
import ghidra.program.model.data.UnsignedIntegerDataType;
import ghidra.program.model.data.VoidDataType;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Function.FunctionUpdateType;
import ghidra.program.model.listing.FunctionTag;
import ghidra.program.model.listing.Parameter;
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyCDXFrontEndVideoHeadWave597 extends GhidraScript {
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
            "cdxfrontendvideo-head-wave597",
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
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;
        DataType uintType = UnsignedIntegerDataType.dataType;
        DataType floatType = FloatDataType.dataType;
        DataType byteType = ByteDataType.dataType;
        DataType charType = CharDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00541200",
                "CDXFrontEndVideo__CDXFrontEndVideo",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave597 CDXFrontEndVideo head hardening: CFEPMultiplayerStart__ctor and CDXFMV__ctor_base construct this object, and the body installs vtable 0x005e5084 before clearing the Bink handle, texture slots, frame flags, and fade alpha fields. Static retail evidence only; exact CDXFrontEndVideo layout, constructor source identity, runtime media initialization behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFrontEndVideo__CDXFrontEndVideo"},
                tags("cdxfrontendvideo", "constructor", "vtable-005e5084", "cdxfmv-embedded-object")
            ),
            new Spec(
                "0x00541220",
                "CDXFrontEndVideo__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("delete_flags", byteType)
                },
                "Wave597 CDXFrontEndVideo head hardening: vtable 0x005e5084 slot 0 points to this scalar-deleting destructor wrapper. RET 0x4 proves one stack parameter after this; the body calls DeviceObject__ctor_like_00512d50, frees this through CDXMemoryManager__Free only when delete_flags bit 0 is set, and returns this. Static retail evidence only; exact base destructor identity, allocator ownership, runtime media teardown behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFrontEndVideo__dtor", "CDXFrontEndVideo__scalar_deleting_dtor"},
                tags("cdxfrontendvideo", "scalar-deleting-dtor", "vtable-slot-0", "ret-0x4", "name-corrected")
            ),
            new Spec(
                "0x00541240",
                "CDXFrontEndVideo__SetDefaultSize",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave597 CDXFrontEndVideo head hardening: this small helper stores the default fallback video dimensions 0x200 by 0x200 at this+0x20 and this+0x24, then returns 1. Static retail evidence only; exact member names, runtime fallback sizing behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFrontEndVideo__SetDefaultSize"},
                tags("cdxfrontendvideo", "default-size", "fallback-dimensions", "returns-one")
            ),
            new Spec(
                "0x00541260",
                "CDXFrontEndVideo__Close",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave597 CDXFrontEndVideo head hardening: raw frontend and CDXFMV close paths call this wrapper, which forwards to CDXFrontEndVideo__CloseVideo and clears the Bink handle at this+0x08. Static retail evidence only; exact object ownership, runtime close ordering, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFrontEndVideo__Close"},
                tags("cdxfrontendvideo", "close", "bink-handle", "closevideo-wrapper")
            ),
            new Spec(
                "0x005412e0",
                "CDXFrontEndVideo__Open",
                "__thiscall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("video_path", charPtr),
                    param("fallback_width", intType),
                    param("fallback_height", intType),
                    param("open_flags", intType),
                    param("async_open", intType),
                    param("callback_cookie", intType)
                },
                "Wave597 CDXFrontEndVideo head hardening: CFEPCommon init/start-video paths, CDXFrontEndVideo__Render pending-open handling, and CDXFMV call sites reach this opener. RET 0x18 proves six stack parameters after this; the body configures RAD memory hooks, stores fallback dimensions, queues pending async opens through DAT_008a97d0 when needed, copies the filename into the Bink-open buffers, runs or starts CBinkOpenThread, and calls CDXFrontEndVideo__InitVideo for synchronous opens. Static retail evidence only; exact parameter semantics, runtime Bink/thread scheduling behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFrontEndVideo__Open"},
                tags("cdxfrontendvideo", "open", "bink-open", "async-open", "ret-0x18", "pending-open-buffer")
            ),
            new Spec(
                "0x00541430",
                "CDXFrontEndVideo__InitVideo",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave597 CDXFrontEndVideo head hardening: CDXFrontEndVideo__Open, __Render, and __CloseVideo call this Bink-init helper after the open thread publishes a handle. The body locks CBinkOpenThread, consumes DAT_008a9830, prepares the first Bink frame, allocates/configures two CUMTexture slots, computes power-of-two texture dimensions against device caps, and clears the fade/pending-open state. Static retail evidence only; exact texture layout, runtime GPU upload behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFrontEndVideo__InitVideo"},
                tags("cdxfrontendvideo", "init-video", "bink-frame", "cumtexture", "double-buffer")
            ),
            new Spec(
                "0x00541650",
                "CDXFrontEndVideo__CloseVideo",
                "__fastcall",
                voidType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave597 CDXFrontEndVideo head hardening: CFEPCommon shutdown/stop-video paths, CDXFrontEndVideo__Close, __Open, and CDXFMV close paths call this resource-release helper. It waits for an active open thread, initializes a deferred handle if needed, releases two CUMTexture slots, logs Bink summary counters, closes the Bink handle, clears this+0x08, and unlocks the thread. Static retail evidence only; exact resource lifetime, runtime Bink close behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFrontEndVideo__CloseVideo"},
                tags("cdxfrontendvideo", "close-video", "resource-release", "bink-summary", "cumtexture-release")
            ),
            new Spec(
                "0x00541770",
                "CDXFrontEndVideo__GetWidth",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave597 CDXFrontEndVideo head hardening: CDXFMV width call sites reach this accessor. ECX carries this; the body returns the cached fallback width at this+0x20 when no Bink handle is loaded, otherwise it returns the Bink width dword at handle+0x00. Static retail evidence only; exact Bink struct layout beyond observed fields, runtime media dimensions, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFrontEndVideo__GetWidth"},
                tags("cdxfrontendvideo", "get-width", "cached-fallback", "bink-dimensions")
            ),
            new Spec(
                "0x00541780",
                "CDXFrontEndVideo__GetHeight",
                "__fastcall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr)
                },
                "Wave597 CDXFrontEndVideo head hardening: CDXFMV height call sites reach this accessor. ECX carries this; the body returns the cached fallback height at this+0x24 when no Bink handle is loaded, otherwise it returns the Bink height dword at handle+0x04. Static retail evidence only; exact Bink struct layout beyond observed fields, runtime media dimensions, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFrontEndVideo__GetHeight"},
                tags("cdxfrontendvideo", "get-height", "cached-fallback", "bink-dimensions")
            ),
            new Spec(
                "0x00541790",
                "CDXFrontEndVideo__Render",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("x", floatType),
                    param("y", floatType),
                    param("z", floatType),
                    param("scale_x", floatType),
                    param("scale_y", floatType),
                    param("packed_argb", uintType),
                    param("centered", intType)
                },
                "Wave597 CDXFrontEndVideo head hardening: CFrontEnd__RenderVideoQuadScaledToWindow and CDXFMV render call sites reach this textured-quad renderer. RET 0x1c proves seven stack parameters after this; the body services pending async opens, decodes/copies Bink frames into double-buffered CUMTexture surfaces, modulates packed_argb by fade alpha, falls back to meshtex_default.tga when no video frame is ready, builds a six-vertex quad from x/y/z scale values, and submits it through the Direct3D device. Static retail evidence only; exact render contract, runtime GPU/media behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFrontEndVideo__Render"},
                tags("cdxfrontendvideo", "render", "bink-copy-to-buffer", "double-buffer", "ret-0x1c", "packed-argb")
            ),
            new Spec(
                "0x00541d30",
                "CDXFrontEndVideo__Update",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("wait_for_frame", charType)
                },
                "Wave597 CDXFrontEndVideo head hardening: CFrontEnd__Process and CDXFMV update call sites reach this playback updater. RET 0x4 proves one stack parameter after this; the body returns 0 when no Bink handle exists, uses BinkWait to gate frame advancement, returns -1 when wait_for_frame requests a wait and the frame is not ready, advances frames through BinkDoFrame/BinkNextFrame, and returns 1 when the observed current-frame and total-frame fields match. Static retail evidence only; exact wait flag semantics, runtime playback timing behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CDXFrontEndVideo__Update"},
                tags("cdxfrontendvideo", "update", "bink-wait", "ret-0x4", "completion-check")
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
            throw new RuntimeException("Wave597 apply failed: missing=" + stats.missing + " bad=" + stats.bad);
        }
    }
}
