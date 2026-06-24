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
import ghidra.program.model.listing.ParameterImpl;
import ghidra.program.model.symbol.SourceType;

import java.util.HashSet;
import java.util.Set;

public class ApplyMissionScriptObjectCodeWave588 extends GhidraScript {
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

    private Function functionAtEntry(Address address) {
        Function fn = getFunctionAt(address);
        if (fn == null) {
            Function containing = getFunctionContaining(address);
            if (containing != null && containing.getEntryPoint().equals(address)) {
                fn = containing;
            }
        }
        return fn;
    }

    private Function getFunctionOrReport(Spec spec, Stats stats) {
        Function fn = functionAtEntry(addr(spec.address));
        if (fn == null) {
            stats.missing++;
            println("FAIL: " + spec.address + " " + spec.name + " Function not found");
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
            "mission-script-object-code-wave588",
            "retail-binary-evidence",
            "mission-script",
            "mission-script-object-code",
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

    private void applySpec(Spec spec, boolean dryRun, Stats stats) {
        try {
            Function fn = getFunctionOrReport(spec, stats);
            if (fn == null) {
                stats.skipped++;
                return;
            }

            String currentName = fn.getName();
            if (!allowedName(spec, currentName)) {
                throw new IllegalStateException("Unexpected function name at " + spec.address + ": " + currentName);
            }

            boolean needsRename = !currentName.equals(spec.name);
            if (dryRun) {
                if (needsRename) {
                    stats.wouldRename++;
                }
                println("DRY: " + spec.address + " " + currentName + " -> " + expectedSignature(spec));
                stats.skipped++;
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

            Function readBack = functionAtEntry(addr(spec.address));
            if (readBack == null) {
                throw new IllegalStateException("Read-back missing at " + spec.address);
            }
            if (!readBack.getName().equals(spec.name)) {
                throw new IllegalStateException("Read-back name mismatch at " + spec.address + ": " + readBack.getName());
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

            println("OK: " + spec.address + " " + readBack.getSignature());
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
        DataType charPtr = new PointerDataType(CharDataType.dataType);
        DataType intType = IntegerDataType.dataType;

        Spec[] specs = new Spec[] {
            new Spec(
                "0x00539c80",
                "CMissionScriptObjectCode__CMissionScriptObjectCode",
                "__fastcall",
                voidPtr,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave588 signature/comment hardening: ECX-only constructor reached from CFEPMultiplayerStart__ctor. The body calls CWaitingThread__ctor_base, installs the observed vtable pointer 0x005e4f5c, clears the byte at this+0x20, and returns this. Only slot 0x005e4f5c[0] -> CMissionScriptObjectCode__LoadAsync is proven; the full vtable boundary remains unproven. Static retail evidence only; exact CMissionScriptObjectCode layout, source identity, runtime mission-script loading behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CMissionScriptObjectCode__CMissionScriptObjectCode"},
                tags("constructor", "waiting-thread-base", "ecx-only")
            ),
            new Spec(
                "0x00539ca0",
                "CMissionScriptObjectCode__LoadAsync",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr) },
                "Wave588 signature/comment hardening: virtual async-load method from vtable slot 0x005e4f5c[0]. The body closes any prior CDXMemBuffer at this+0x1c, allocates a 0x134-byte CDXMemBuffer from XBOXAsyncCache, applies buffer size this+0x124, calls CDXMemBuffer__InitFromFile on the path at this+0x20, emits DebugTrace file-not-found diagnostics on failure, releases the buffer on failure, and clears the first path byte before return. Only slot 0x005e4f5c[0] is proven; the full vtable boundary remains unproven. Static retail evidence only; exact async/cache ownership, source identity, runtime file-load behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CMissionScriptObjectCode__LoadAsync"},
                tags("async-load", "vtable-slot", "cdx-mem-buffer", "thiscall")
            ),
            new Spec(
                "0x00539dc0",
                "CMissionScriptObjectCode__StartLoadAsync",
                "__thiscall",
                voidType,
                new ParameterImpl[] { param("this", voidPtr), param("filename", charPtr), param("buffer_size", intType) },
                "Wave588 signature/comment hardening: async-start helper reached from CFEPGoodies__StartLoadingGoody. RET 0x8 proves filename and buffer_size stack arguments after ECX; the body waits for the current thread, copies filename into this+0x20, stores buffer_size at this+0x124, and starts the background worker through CBinkOpenThread__StartAsync. Static retail evidence only; exact file path ownership, source identity, runtime Goodie/script loading behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CMissionScriptObjectCode__StartLoadAsync"},
                tags("async-start", "ret-8", "bink-open-thread", "filename-copy")
            ),
            new Spec(
                "0x00539f00",
                "CMissionScriptObjectCode__InitFields",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("field_block", voidPtr) },
                "Wave588 signature/comment hardening: ECX-only HUD script-field-block initializer reached from CHud__Init. The body zeroes the object-code pointer at +0x00, reference-counted slots at +0x04/+0x08/+0x0c/+0x10/+0x14, allocation slot +0x18, and virtual-owned slots at +0x70/+0x74/+0x78. Static retail evidence only; this does not prove a full CMissionScriptObjectCode instance layout, source identity, runtime HUD/script behavior, BEA patching, or rebuild parity.",
                new String[] {"CMissionScriptObjectCode__InitFields"},
                tags("field-block", "hud-init", "ecx-only")
            ),
            new Spec(
                "0x00539f30",
                "CMissionScriptObjectCode__ClearFields_Thunk",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("field_block", voidPtr) },
                "Wave588 name/signature/comment hardening: one-instruction JMP thunk reached from CHud__ShutDown that forwards the supplied ECX field_block to CMissionScriptObjectCode__ClearFields at 0x00539f40. Static retail evidence only; exact thunk purpose, source identity, runtime HUD/script teardown behavior, BEA patching, and rebuild parity remain unproven.",
                new String[] {"CMissionScriptObjectCode__ClearFields", "CMissionScriptObjectCode__ClearFields_Thunk"},
                tags("field-block", "hud-shutdown", "clear-fields-thunk", "jmp-thunk", "renamed")
            ),
            new Spec(
                "0x00539f40",
                "CMissionScriptObjectCode__ClearFields",
                "__fastcall",
                voidType,
                new ParameterImpl[] { param("field_block", voidPtr) },
                "Wave588 signature/comment hardening: ECX-only HUD script-field-block teardown body reached from CHud__ShutDown and the 0x00539f30 thunk. The body frees the object-code record through CMissionScriptObjectCode__FreeObjectIfPresent and CDXMemoryManager__Free, releases reference-counted slots through CHud__DecrementCounter9C, calls virtual deleting destructors for slots +0x70/+0x74/+0x78, frees allocation slot +0x18, and clears each slot as it is released. Static retail evidence only; this does not prove a full CMissionScriptObjectCode instance layout, source identity, runtime HUD/script teardown behavior, BEA patching, or rebuild parity.",
                new String[] {"CMissionScriptObjectCode__ClearFields"},
                tags("field-block", "hud-shutdown", "free-object-if-present", "ecx-only")
            )
        };

        Stats stats = new Stats();
        for (Spec spec : specs) {
            applySpec(spec, dryRun, stats);
        }

        println("SUMMARY updated=" + stats.updated
            + " skipped=" + stats.skipped
            + " renamed=" + stats.renamed
            + " would_rename=" + stats.wouldRename
            + " missing=" + stats.missing
            + " bad=" + stats.bad);
    }
}
