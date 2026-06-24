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

public class ApplyDXCompassHudHeadWave591 extends GhidraScript {
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
            "dxcompass-hud-head-wave591",
            "retail-binary-evidence",
            "dxcompass",
            "hud-render",
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

        Spec[] specs = new Spec[] {
            new Spec(
                "0x0053bb50",
                "CDXEngine__RenderOptionalFullscreenEffectPass",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave591 signature/comment hardening: CDXEngine__Render calls this ECX-only render tail from the optional fullscreen/effect path. The body gates on this+0x12c, temporarily clears/restores _DAT_0089ce54 bit 4, enables render state 0x8f, dispatches the optional effect object at this+0x8c with flag 0x40 when the this+0x110 virtual +0x16c value exceeds the threshold, writes DAT_0063012c for that pass, then resets it to 0xff. Static retail evidence only; exact CDXEngine layout, runtime effect behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {},
                tags("cdxengine", "fullscreen-effect", "render-state", "ecx-only")
            ),
            new Spec(
                "0x0053bd60",
                "CDXCompass__InitFields",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave591 owner/signature correction: CHud__Init allocates the large compass field block, calls this ECX-only return-this initializer, stores the result at CHud+0x60, and then calls CDXCompass__InitMarkerArrays. The body calls CDXCompass__Reset, clears the two ring texture pairs at this+0x3c00/+0x3c04 and this+0x3f04/+0x3f08, and clears this+0x3f0c, this+0x3c08, and this+0x3f10. Static retail evidence only; exact constructor/source identity, concrete layout, runtime HUD behavior, and rebuild parity remain unproven.",
                new String[] {"CHud__ResetCompassAndHudCounters"},
                tags("owner-corrected", "init-fields", "ring-texture", "ecx-only", "renamed")
            ),
            new Spec(
                "0x0053bda0",
                "CDXCompass__ReleaseDynamicResources",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave591 owner/signature correction: CHud__ShutDown calls CDXCompass__DestroyTextures, then this ECX-only compass field-block cleanup before freeing CHud+0x60. The body releases the two ring texture pairs at this+0x3c00/+0x3c04 and this+0x3f04/+0x3f08 via CHud__DecrementCounter9C(texture+8), destroys the objects at this+0x3f0c and this+0x3f10 through their deleting destructors, frees the CByteSprite at this+0x3c08, and clears each slot. Static retail evidence only; full resource ownership, runtime teardown behavior, and rebuild parity remain unproven.",
                new String[] {"CHud__FreeObjectIfPresent"},
                tags("owner-corrected", "resource-release", "ring-texture", "byte-sprite", "ecx-only", "renamed")
            ),
            new Spec(
                "0x0053c2e0",
                "CDXCompass__BuildByteSpriteOverlayTexture",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("battleEngineContext", voidPtr) },
                "Wave591 owner/signature correction: CDXCompass__RenderWorldSpaceOverlay calls this with the compass field block in ECX and one battle-engine context stack argument; RET 0x4 and the callsite disprove the older extra-parameter shape. The body clears the compass working buffer, fills the byte-sprite staging area at this+0x1a00, draws CByteSprite frames through this+0x3c08, iterates the battle-engine context+0x2b8 list, locks the active texture from this+0x3c00 + this+0x3c10*4, copies scaled sprite bytes into the texture rows, and unlocks. Static retail evidence only; exact list/layout semantics, runtime texture behavior, and rebuild parity remain unproven.",
                new String[] {"CDXBattleLine__BuildByteSpriteOverlayTexture"},
                tags("owner-corrected", "byte-sprite", "overlay-texture", "ring-texture", "ret-0x4", "renamed")
            ),
            new Spec(
                "0x0053c510",
                "CDXCompass__UpdateDynamicOverlayTexture",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("battleEngineContext", voidPtr) },
                "Wave591 owner/signature correction: CDXCompass__RenderWorldSpaceOverlay calls this with the compass field block in ECX and one battle-engine context stack argument; RET 0x4 and the callsite disprove the older CVBufTexture owner and extra-parameter shape. The body reads battle-engine health/tracked-position helpers, locks the active texture from this+0x3f04 + this+0x3c10*4, updates threshold caches at this+0x3c14/+0x3c1c, consults CHud__ResolveOverlaySlotRenderMode for slots 0 and 1, writes dynamic row bands, and unlocks. Static retail evidence only; exact health/slot semantics, runtime texture behavior, and rebuild parity remain unproven.",
                new String[] {"CVBufTexture__UpdateDynamicOverlayTexture"},
                tags("owner-corrected", "dynamic-overlay", "overlay-texture", "ring-texture", "ret-0x4", "renamed")
            ),
            new Spec(
                "0x0053cd30",
                "CDXCompass__RenderWorldSpaceOverlay",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("battleEngineContext", voidPtr) },
                "Wave591 owner/signature correction: CHud__RenderTargetMarkers3D calls this with CHud+0x60 compass field block in ECX and CHud+0x50 battle-engine context as the sole stack argument; RET 0x4 disproves the older extra-parameter shape. The body sets render state, calls the compass byte-sprite and dynamic texture builders, binds textures/buffers from this+0x3c00/+0x3f04/+0x3f0c/+0x3f10, orients the world-space overlay with CBattleEngine__GetInterpolatedEulerOrientation, consults CHud__ResolveOverlaySlotRenderMode slot 2, restores matrices/state, calls CDXCompass__Render, and advances this+0x3c10 outside multiplayer. Static retail evidence only; exact register-local provenance, runtime HUD behavior, and rebuild parity remain unproven.",
                new String[] {"CDXBattleLine__RenderWorldSpaceOverlay"},
                tags("owner-corrected", "world-space-overlay", "target-overlay", "compass-render", "ret-0x4", "renamed")
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
