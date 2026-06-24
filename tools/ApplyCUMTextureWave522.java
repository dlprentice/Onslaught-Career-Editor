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

public class ApplyCUMTextureWave522 extends GhidraScript {
    private static class Spec {
        final String address;
        final String name;
        final String callingConvention;
        final DataType returnType;
        final ParameterImpl[] parameters;
        final String comment;
        final String[] tags;
        final boolean renameAllowed;

        Spec(String address, String name, String callingConvention, DataType returnType,
                ParameterImpl[] parameters, String comment, String[] tags, boolean renameAllowed) {
            this.address = address;
            this.name = name;
            this.callingConvention = callingConvention;
            this.returnType = returnType;
            this.parameters = parameters;
            this.comment = comment;
            this.tags = tags;
            this.renameAllowed = renameAllowed;
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

    private String[] tags(String... extras) {
        String[] common = new String[] {
            "static-reaudit",
            "cumtexture-wave522",
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) throws Exception {
        Function fn = functionAtEntry(spec.address);
        if (fn == null) {
            println("MISSING: " + spec.address);
            stats.missing++;
            return;
        }
        if (!fn.getName().equals(spec.name)) {
            if (!spec.renameAllowed) {
                println("BADNAME: " + spec.address + " " + fn.getName() + " expected " + spec.name);
                stats.bad++;
                return;
            }
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
                "0x004f79d0",
                "CUMTexture__ctor_base",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave522 CUMTexture signature/comment hardening: ECX carries the CUMTexture object, the body installs vtable 0x005df908, clears the owned texture pointer at this+0x08, calls the shader/device-object base initializer, and returns this. Xrefs include CLandscapeTexture__ConstructorMip, CDXShadows__Init, and CDXFrontEndVideo__InitVideo allocation paths. Static retail evidence only; exact source constructor name, complete CUMTexture layout, runtime GPU behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cumtexture", "texture-resource", "lifecycle", "constructor", "vtable"),
                true
            ),
            new Spec(
                "0x004f7a20",
                "CUMTexture__scalar_deleting_dtor",
                "__thiscall",
                voidPtr,
                new ParameterImpl[] {param("this", voidPtr), param("delete_flags", byteType)},
                "Wave522 CUMTexture signature/comment hardening: CUMTexture vtable 0x005df908 slot 0 points here, RET 0x4 proves one explicit delete_flags stack argument after ECX, and the body calls CUMTexture__dtor_base before freeing this through CDXMemoryManager__Free when delete_flags&1 is set. Static retail evidence only; exact source destructor spelling, complete layout, runtime texture lifetime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cumtexture", "texture-resource", "lifecycle", "destructor", "vtable", "owner-corrected"),
                true
            ),
            new Spec(
                "0x004f7a40",
                "CUMTexture__dtor_base",
                "__fastcall",
                voidType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave522 CUMTexture signature/comment hardening: ECX carries the CUMTexture object. The destructor body restores vtable 0x005df908, unlinks the object from render/resource lists, releases the owned texture pointer at this+0x08 through its virtual release slot when present, clears the pointer, and delegates to the base cleanup label at 0x00512d50. Xrefs include the scalar deleting destructor, CLandscapeTexture__Destructor, and unwind cleanup. Static retail evidence only; exact source destructor name, base type identity, runtime texture lifetime behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cumtexture", "texture-resource", "lifecycle", "destructor", "cleanup"),
                true
            ),
            new Spec(
                "0x004f7ab0",
                "CUMTexture__ConfigureByMode",
                "__thiscall",
                intType,
                new ParameterImpl[] {
                    param("this", voidPtr),
                    param("texture_size", voidPtr),
                    param("mode", intType),
                    param("texture_count_or_depth", intType)
                },
                "Wave522 CUMTexture signature/comment hardening: RET 0x0c proves three explicit stack arguments after ECX. Callers in CLandscapeTexture__Init, CDXShadows__Init, and CDXFrontEndVideo__InitVideo pass a texture size/pointer-sized value, a mode selector, and a count/depth value. The body stores this+0x14/0x18, maps observed modes 0,1,3,4,5 into format/mipmap/shared fields at this+0x0c/+0x10/+0x1c, dispatches vtable slot +0x08, and preserves that result in EAX for callers that check failure. Static retail evidence only; exact mode enum names, full layout, runtime GPU behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cumtexture", "texture-resource", "configuration", "mode-selector", "signature-corrected"),
                true
            ),
            new Spec(
                "0x004f7b60",
                "CUMTexture__RecreateTextureResource",
                "__fastcall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave522 CUMTexture signature/comment hardening: CUMTexture vtable 0x005df908 slot 2 points here and CLandscapeTexture__Reset also calls it directly. The ECX-only body resolves the requested texture format from this+0x0c into this+0x24, releases any existing owned texture pointer at this+0x08, then calls CEngine__CreateTextureUnchecked with size/count/mipmap/format/shared fields from this+0x14/+0x18/+0x10/+0x24/+0x1c and output pointer this+0x08. Static retail evidence only; exact return-code contract, GPU allocation behavior, full layout, BEA patching, and rebuild parity remain unproven.",
                tags("cumtexture", "texture-resource", "resource-create", "vtable", "signature-corrected"),
                true
            ),
            new Spec(
                "0x004f7bd0",
                "CUMTexture__VFunc_03_ReleaseTextureResource",
                "__fastcall",
                intType,
                new ParameterImpl[] {param("this", voidPtr)},
                "Wave522 CUMTexture signature/comment hardening: CUMTexture vtable 0x005df908 slot 3 and CLandscapeTexture secondary vtable 0x005dc1f0 slot 3 both point here. The ECX-only body releases the owned texture pointer at this+0x08 through its virtual release slot when present, clears the pointer, and returns 0. Static retail evidence only; exact virtual name, owner sharing contract, runtime GPU behavior, BEA patching, and rebuild parity remain unproven.",
                tags("cumtexture", "texture-resource", "resource-release", "vtable", "owner-corrected"),
                true
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
