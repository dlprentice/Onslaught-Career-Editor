//@category Symbol

import ghidra.app.script.GhidraScript;
import ghidra.program.model.address.Address;
import ghidra.program.model.data.CharDataType;
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

public class ApplyVBufTextureResourceTailWave532 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
        }
    }

    private static class Stats {
        int updated = 0;
        int skipped = 0;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "vbuftexture-resource-wave532",
            "retail-binary-evidence",
            "signature-corrected",
            "comment-hardened"
        };
        String[] result = new String[common.length + extras.length];
        System.arraycopy(common, 0, result, 0, common.length);
        System.arraycopy(extras, 0, result, common.length, extras.length);
        return result;
    }

    private String expectedSignature(Spec spec) {
        StringBuilder sb = new StringBuilder();
        sb.append(spec.returnType.getDisplayName()).append(" ")
            .append(spec.callingConvention).append(" ")
            .append(spec.name).append("(");
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
        Set<String> existing = new HashSet<>();
        for (FunctionTag tag : fn.getTags()) {
            existing.add(tag.getName());
        }
        for (String tag : tags) {
            if (!existing.contains(tag)) {
                return false;
            }
        }
        return true;
    }

    private boolean needsUpdate(Function fn, Spec spec) {
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }
        if (!fn.getName().equals(spec.name)) {
            println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
            stats.bad++;
            return;
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
    }

    @Override
    protected void run() throws Exception {
        String[] args = getScriptArgs();
        boolean dryRun = isDryRun(args != null && args.length > 0 ? args[0] : "dry");
        println("Mode: " + (dryRun ? "dry" : "apply"));

        DataType intType = IntegerDataType.dataType;
        DataType voidType = VoidDataType.dataType;
        DataType voidPtr = new PointerDataType(voidType);
        DataType charPtr = new PointerDataType(CharDataType.dataType);

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00501310",
                "CDXEngine__DecrementResourceRefCount",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("resource", voidPtr)},
                "Wave532 vbuftexture/resource-tail signature/comment hardening: ECX-only helper decrements field +0x60 on a CVBufTexture/resource object. It is called after temporary render/debug/texture resources are rendered or released, matching CVBufTexture__GetOrCreate increment evidence at +0x60. Static retail evidence only; exact owner type, release ownership contract, underflow behavior, runtime lifetime behavior, and rebuild parity remain unproven.",
                tags("resource-lifetime", "refcount", "cvbuftexture")
            ),
            new Spec(
                "0x00501320",
                "CScreenFx__FindTexture",
                "__cdecl",
                voidType,
                new ParameterImpl[] {param("texture_name", charPtr), param("texture_find_arg", intType)},
                "Wave532 vbuftexture/resource-tail signature/comment hardening: caller-cleaned RET C3 plus CScreenFx callsites prove texture_name and texture_find_arg stack arguments. The helper forwards texture_name to CTexture__FindTexture with fixed zero/one arguments, decrements the found texture-side counter at +0x8 through CHud__DecrementCounter9C, then ensures a CVBufTexture wrapper through CVBufTexture__GetOrCreate(texture,0). Static retail evidence only; exact CTexture lookup semantics, texture_find_arg meaning, runtime screen-effect behavior, and rebuild parity remain unproven.",
                tags("screenfx", "texture-reference", "cvbuftexture", "resource-lifetime")
            ),
            new Spec(
                "0x00501360",
                "CWaypoint__CleanupEndLevelVBufTextures",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave532 vbuftexture/resource-tail signature/comment hardening: global no-argument RET C3 helper reached from frontend/end-level cleanup paths. The body walks CVBufTexture global list head 0x00854e00, frees entries whose refcount field +0x60 is zero, then emits end-of-level VBufTexture resource leak or no-leak DebugTrace text for remaining list entries. Static retail evidence only; exact leak policy, list layout, waypoint ownership semantics, runtime cleanup behavior, and rebuild parity remain unproven.",
                tags("waypoint", "cvbuftexture", "resource-lifetime", "leak-report")
            ),
            new Spec(
                "0x00501450",
                "CVBufTexture__ClearOut",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave532 vbuftexture/resource-tail signature/comment hardening: global no-argument RET C3 helper called during CLTShell shutdown after CVertexShader__ClearOut. It walks CVBufTexture global list head 0x00854e00, frees zero-refcount entries, then emits shutdown resource leak or no-leak DebugTrace text for any remaining entries. Static retail evidence only; exact shutdown ownership policy, list layout, runtime leak behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "resource-lifetime", "leak-report", "shutdown")
            ),
            new Spec(
                "0x00501540",
                "CDXEngine__ResizeLargestIdleVertexBuffer",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave532 vbuftexture/resource-tail signature/comment hardening: global no-argument RET C3 helper called from CDXEngine__PostRender. When guard byte 0x00633d2c is clear, it scans non-persistent CVBufTexture entries, computes the power-of-two capacity needed for each current/last vertex byte count, selects the entry with the largest shrink opportunity, and calls CVBufTexture__ResizeVertexBuffer on that single entry. Static retail evidence only; exact guard-byte meaning, frame cadence, runtime device behavior, and rebuild parity remain unproven.",
                tags("cvbuftexture", "resource-pool", "buffer-trim", "post-render")
            ),
            new Spec(
                "0x005015c0",
                "CEngine__TrimVbIbPoolCapacitiesPow2",
                "__cdecl",
                voidType,
                new ParameterImpl[] {},
                "Wave532 vbuftexture/resource-tail signature/comment hardening: global no-argument RET C3 helper called from CGame restart, CDXEngine post-render, and CEngine shutdown paths. It walks CVBufTexture global list head 0x00854e00, rounds current vertex and index byte cursors up to 0x400-based powers of two, and shrinks oversized vertex/index buffers through CVBufTexture__ResizeVertexBuffer and CVBufTexture__ResizeIndexBuffer. Static retail evidence only; exact pool policy, device-loss behavior, runtime performance impact, and rebuild parity remain unproven.",
                tags("cvbuftexture", "resource-pool", "buffer-trim", "engine-shutdown")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }
        println("SUMMARY updated=" + stats.updated + " skipped=" + stats.skipped + " missing=" + stats.missing + " bad=" + stats.bad);
    }
}
